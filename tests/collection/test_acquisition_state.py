import json
import tempfile
import unittest
from pathlib import Path

from scripts.jobs.acquisition_state import AcquisitionState, StateError


class AcquisitionStateTests(unittest.TestCase):
    def request(self, root, request_id="req-1", cap="0.05"):
        return {"request_id": request_id, "campaign_root": str(root), "reserved_usd": cap,
                "config_sha256": "c", "input": {"keyword": "developer"}}

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


if __name__ == "__main__": unittest.main()
