import json
import tempfile
import unittest
from pathlib import Path

from scripts.jobs.acquisition_state import AcquisitionState, StateError


class AcquisitionStateTests(unittest.TestCase):
    def request(self, root, request_id="req-1", cap="0.05"):
        return {"request_id": request_id, "campaign_root": str(root), "reserved_usd": cap,
                "config_sha256": "c", "input": {"keyword": "developer"}}

    def game_scope_config(self, query_ids=("GD07", "GD08", "GD03", "GD09")):
        keywords = {"GD07": "Unreal developer", "GD08": "gameplay programmer",
                    "GD03": "game designer", "GD09": "game QA tester"}
        return {"live_collection_enabled": True,
                "queries": [{"query_id": qid, "keyword": keywords.get(qid, "x"),
                             "family": "Game Development" if qid != "NT01" else "Network Technology",
                             "status": "enabled"} for qid in query_ids],
                "pilot_core_query_ids": list(query_ids), "pilot_optional_query_ids": [],
                "live_adapter": {"campaign_ceiling_usd": "0.101", "baseline_spend_usd": "0"}}

    def game_request(self, root, request_id, query_id):
        req = self.request(root, request_id, "0.02525")
        req.update({"query_id": query_id, "pilot_stage": "core",
                    "input": {"keyword": "game", "results_wanted": 25},
                    "run_options": {"maxTotalChargeUsd": 0.02525, "timeout": 300, "restartOnError": False}})
        return req

    def test_four_game_scope_accepts_four_then_rejects_fifth_start(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            config = self.game_scope_config()
            (root / "collection_config.json").write_text(json.dumps(config), encoding="utf-8")
            state = AcquisitionState(root)
            for index, query_id in enumerate(config["pilot_core_query_ids"], 1):
                request_id = "req-{}".format(index)
                state.reserve(self.game_request(root, request_id, query_id))
                state.settle(request_id, "run-{}".format(index), "0.02525")
                state.update(request_id, "imported", billing_status="reconciled")
            self.assertEqual(len(state._all_requests()), 4)
            with self.assertRaisesRegex(StateError, "pilot_start_limit_reached"):
                state.reserve(self.game_request(root, "req-5", "GD07"))

    def test_four_game_scope_rejects_mixed_family(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            config = self.game_scope_config(("GD07", "GD08", "GD03", "NT01"))
            (root / "collection_config.json").write_text(json.dumps(config), encoding="utf-8")
            state = AcquisitionState(root)
            with self.assertRaisesRegex(StateError, "pilot_four_core_queries_must_be_game_development_only"):
                state.reserve(self.game_request(root, "req-1", "GD07"))

    def test_legacy_six_core_scope_still_accepts_a_core_start(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            core = ["IS01", "GD01", "NT01", "WD01", "SH01", "SH02"]
            families = {"IS01": "Intelligent Systems", "GD01": "Game Development",
                        "NT01": "Network Technology", "WD01": "Web Development",
                        "SH01": "Shared/core", "SH02": "Shared/core"}
            config = {"live_collection_enabled": True,
                      "queries": [{"query_id": qid, "family": families[qid], "status": "enabled"} for qid in core],
                      "pilot_core_query_ids": core, "pilot_optional_query_ids": [],
                      "live_adapter": {"campaign_ceiling_usd": "0.30", "baseline_spend_usd": "0"}}
            (root / "collection_config.json").write_text(json.dumps(config), encoding="utf-8")
            request = self.request(root)
            request.update({"query_id": "IS01", "pilot_stage": "core",
                            "input": {"keyword": "data engineer", "results_wanted": 25},
                            "run_options": {"maxTotalChargeUsd": 0.05, "timeout": 300, "restartOnError": False}})
            self.assertEqual(AcquisitionState(root).reserve(request)["status"], "reserved")

    def test_legacy_six_core_plus_two_optionals_still_caps_at_eight_starts(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            core = ["IS01", "GD01", "NT01", "WD01", "SH01", "SH02"]
            optional = ["NT07", "SH03"]
            families = {"IS01": "Intelligent Systems", "GD01": "Game Development",
                        "NT01": "Network Technology", "WD01": "Web Development",
                        "SH01": "Shared/core", "SH02": "Shared/core",
                        "NT07": "Complement", "SH03": "Shared/core"}
            ids = core + optional
            config = {"live_collection_enabled": True,
                      "queries": [{"query_id": qid, "family": families[qid], "status": "enabled"} for qid in ids],
                      "pilot_core_query_ids": core, "pilot_optional_query_ids": optional,
                      "conditional_start_evidence": {qid: {"observed_gap": "gap", "comparison_rule": "rule"}
                                                     for qid in optional},
                      "live_adapter": {"campaign_ceiling_usd": "0.30", "baseline_spend_usd": "0"}}
            (root / "collection_config.json").write_text(json.dumps(config), encoding="utf-8")
            state = AcquisitionState(root)
            for index, query_id in enumerate(ids, 1):
                request_id = "req-{}".format(index)
                request = self.game_request(root, request_id, query_id)
                request["reserved_usd"] = "0.02525"
                request["pilot_stage"] = "core" if query_id in core else "conditional"
                state.reserve(request)
                state.settle(request_id, "run-{}".format(index), "0.02525")
                state.update(request_id, "imported", billing_status="reconciled")
            self.assertEqual(len(state._all_requests()), 8)
            with self.assertRaisesRegex(StateError, "pilot_start_limit_reached"):
                state.reserve(self.game_request(root, "req-9", "IS01"))

    def test_reservation_survives_unknown_start_and_blocks_second_start(self):
        with tempfile.TemporaryDirectory() as temp:
            state = AcquisitionState(temp)
            state.reserve(self.request(Path(temp)))
            state.update("req-1", "start_outcome_unknown")
            with self.assertRaises(StateError):
                state.reserve(self.request(Path(temp), "req-2"))
            self.assertEqual(state.get("req-1")["status"], "start_outcome_unknown")

    def test_duplicate_settlement_is_counted_once_and_trailing_ledger_is_repaired(self):
        with tempfile.TemporaryDirectory() as temp:
            state = AcquisitionState(temp)
            state.reserve(self.request(Path(temp)))
            state.settle("req-1", "run-1", "0.02", evidence={"source": "run"})
            state.settle("req-1", "run-1", "0.02", evidence={"source": "run"})
            ledger = Path(temp) / "budget_ledger.jsonl"
            with ledger.open("a", encoding="utf-8") as stream: stream.write('{"partial":')
            repaired = AcquisitionState(temp)
            rows = [json.loads(line) for line in ledger.read_text(encoding="utf-8").splitlines()]
            self.assertEqual(len([r for r in rows if r.get("event") == "settlement"]), 1)
            self.assertEqual(repaired.available("5", "0"), "4.98")
            self.assertEqual(repaired.available("5", "1"), "3.98")

    def test_exclusive_campaign_lock_rejects_a_second_writer(self):
        with tempfile.TemporaryDirectory() as temp:
            first = AcquisitionState(temp)
            second = AcquisitionState(temp)
            with first.lock():
                with self.assertRaises(StateError):
                    with second.lock(): pass

    def test_dead_writer_lock_is_recovered_but_unresolved_request_still_blocks_start(self):
        with tempfile.TemporaryDirectory() as temp:
            state = AcquisitionState(temp)
            state.reserve(self.request(Path(temp)))
            state.lock_path.mkdir()
            (state.lock_path / "owner.json").write_text('{"pid":99999999}', encoding="utf-8")
            with state.lock():
                self.assertTrue(state.lock_path.exists())
            with self.assertRaises(StateError):
                state.reserve(self.request(Path(temp), "req-2"))

    def test_verified_no_run_evidence_releases_only_that_request_reservation(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            state = AcquisitionState(root)
            state.reserve(self.request(root))
            state.update("req-1", "start_outcome_unknown")
            evidence = root / "console-check.txt"
            evidence.write_text("No run with request timestamp found", encoding="utf-8")
            state.reconcile_no_run("req-1", evidence)
            self.assertTrue(state.get("req-1")["reservation_released"])
            state.reserve(self.request(root, "req-2"))

    def test_over_cap_provider_settlement_is_recorded_and_blocks_following_starts(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            from scripts.jobs.collect import query_registry
            config = {"live_collection_enabled": True, "queries": query_registry(),
                      "pilot_core_query_ids": ["IS01", "GD01", "NT01", "WD01", "SH01", "SH02"],
                      "pilot_optional_query_ids": [],
                      "live_adapter": {"campaign_ceiling_usd": "0.30", "baseline_spend_usd": "0"}}
            (root / "collection_config.json").write_text(json.dumps(config), encoding="utf-8")
            state = AcquisitionState(root)
            request = self.request(root)
            request.update({"query_id": "IS01", "pilot_stage": "core",
                            "input": {"keyword": "data engineer", "results_wanted": 25},
                            "run_options": {"maxTotalChargeUsd": 0.05, "timeout": 300, "restartOnError": False}})
            state.reserve(request)
            state.update("req-1", "importing", run_id="run-1")
            with self.assertRaisesRegex(StateError, "provider_charge_exceeded_pilot_cap"):
                state.settle("req-1", "run-1", "0.06")
            self.assertEqual(state._ledger()[-1]["amount_usd"], "0.06")
            self.assertTrue(state.get("req-1")["cap_violation"])
            with self.assertRaisesRegex(StateError, "prior_run_exceeded_pilot_cap"):
                state.reserve(self.request(root, "req-2"))


if __name__ == "__main__": unittest.main()
