import json
import hashlib
import os
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, patch
from urllib.parse import parse_qs, urlparse

from scripts.jobs.apify_adapter import (AdapterError, ApifyTransport, ExecutionGateError, build_request,
    download_dataset, load_token, poll_run, start_run, verify_execution_gate)
from scripts.jobs.apify_adapter import preflight
from scripts.jobs.acquisition_state import AcquisitionState


class AdapterPreviewTests(unittest.TestCase):
    def test_transport_encodes_boolean_query_values_as_lowercase(self):
        response = MagicMock()
        response.__enter__.return_value = response
        response.read.return_value = b'{"data":{}}'
        response.headers.items.return_value = []
        opener = MagicMock()
        opener.open.return_value = response
        with patch("scripts.jobs.apify_adapter.build_opener", return_value=opener):
            ApifyTransport("sentinel").request("POST", "/v2/actors/actor/runs",
                query={"restartOnError": False, "otherFlag": True}, body={})
        url = opener.open.call_args.args[0].full_url
        self.assertEqual(parse_qs(urlparse(url).query)["restartOnError"], ["false"])
        self.assertEqual(parse_qs(urlparse(url).query)["otherFlag"], ["true"])

    def config(self, root):
        now = datetime.now(timezone.utc)
        end = now.isoformat()
        contract = root / "contract.json"
        contract_snapshot = json.loads((Path(__file__).resolve().parents[2] / "data/collection_samples/jobstreet/actor-contract.json").read_text(encoding="utf-8"))
        contract.write_text(json.dumps(contract_snapshot), encoding="utf-8")
        allowance = root / "allowance.json"
        allowance.write_text("verified allowance", encoding="utf-8")
        access = root / "access.md"
        access.write_text("source basis", encoding="utf-8")
        auth = root / "authorization.md"
        auth.write_text("scope approval", encoding="utf-8")
        from scripts.jobs.collect import query_registry
        return {"schema_version": "job-collection-v1", "campaign_id": "c1", "window_start": (now - timedelta(days=30)).isoformat(),
                "window_end": end, "live_collection_enabled": True, "queries": query_registry(),
                "live_adapter": {"actor_id": "f7ggUvGaOrrUuPkZQ", "actor_name": "shahidirfan/jobstreet-scraper",
                    "build_number": "0.0.36", "build_id": "wcMB0BeF4w9asSke8",
                    "actor_contract_sha256": hashlib.sha256(contract.read_bytes()).hexdigest(), "actor_contract_verified_at": (now - timedelta(days=1)).isoformat(),
                    "actor_contract_evidence": str(contract), "source_access_basis": {"basis": "public postings", "evidence": str(access)},
                    "allowance_verified_at": (now - timedelta(hours=1)).isoformat(), "allowance_evidence": str(allowance),
                    "allowance_snapshot_basis": "pilot cost already reflected; baseline is zero",
                    "allowance_reconciliation_evidence": str(allowance),
                    "verified_available_usd": "5.00", "campaign_ceiling_usd": "0.30", "baseline_spend_usd": "0",
                    "per_run_cap_usd": "0.05",
                    "authorized_collection_scope": {"reference": "approval-1", "evidence": str(auth), "campaign_id": "c1",
                        "query_ids": ["WD01"], "window_start": (now - timedelta(days=30)).isoformat(),
                        "window_end": end, "max_charge_usd": "0.05"},
                    "timeout_secs": 300, "memory_mbytes": 1024, "max_results_per_run": 25},
                "pilot_core_query_ids": ["IS04", "GD01", "NT01", "WD01", "SH01", "SH05"],
                "pilot_optional_query_ids": [], "conditional_start_evidence": {}}

    def test_builds_exact_registered_preview_and_filter(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            config = self.config(root)
            request = build_request(config, query_id="WD01", results_wanted=25, charge_cap_usd="0.05",
                                    campaign_root=root, now=config["window_end"])
            self.assertEqual(request["input"]["keyword"], "web developer")
            self.assertEqual(request["input"]["posted_date"], "30d")
            self.assertEqual(request["input"]["results_wanted"], 25)
            self.assertEqual(request["run_options"]["build"], "0.0.36")

    def test_four_game_core_queries_are_supported_and_must_stay_game_only(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            config = self.config(root)
            config["queries"] = [
                {"query_id": "GD07", "keyword": "Unreal developer", "family": "Game Development", "status": "enabled"},
                {"query_id": "GD08", "keyword": "gameplay programmer", "family": "Game Development", "status": "enabled"},
                {"query_id": "GD03", "keyword": "game designer", "family": "Game Development", "status": "enabled"},
                {"query_id": "GD09", "keyword": "game QA tester", "family": "Game Development", "status": "enabled"},
            ]
            config["pilot_core_query_ids"] = ["GD07", "GD08", "GD03", "GD09"]
            config["pilot_optional_query_ids"] = []
            scope = config["live_adapter"]["authorized_collection_scope"]
            scope.update({"query_ids": config["pilot_core_query_ids"], "max_charge_usd": "0.101"})
            config["live_adapter"].update({"per_run_cap_usd": "0.02525", "campaign_ceiling_usd": "0.101"})
            request = build_request(config, query_id="GD08", results_wanted=25,
                                    charge_cap_usd="0.02525", campaign_root=root,
                                    now=config["window_end"])
            self.assertEqual(request["input"]["keyword"], "gameplay programmer")
            self.assertEqual(request["input"], {"keyword": "gameplay programmer", "location": "", "country": "ph",
                              "posted_date": "30d", "results_wanted": 25,
                              "proxyConfiguration": {"useApifyProxy": False}})
            self.assertEqual(request["run_options"], {"build": "0.0.36", "timeout": 300,
                              "memory": 1024, "maxTotalChargeUsd": 0.02525, "restartOnError": False})
            self.assertEqual(request["pilot_stage"], "core")

            config["queries"][1]["family"] = "Network Technology"
            with self.assertRaisesRegex(ExecutionGateError, "pilot_four_core_queries_must_be_game_development_only"):
                build_request(config, query_id="GD08", results_wanted=25,
                              charge_cap_usd="0.02525", campaign_root=root,
                              now=config["window_end"])

    def test_legacy_six_core_preview_remains_supported(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            config = self.config(root)
            request = build_request(config, query_id="WD01", results_wanted=25,
                                    charge_cap_usd="0.05", campaign_root=root,
                                    now=config["window_end"])
            self.assertEqual(request["pilot_stage"], "core")

    def test_30_day_filter_does_not_change_to_anytime_after_a_short_delay(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            config = self.config(root)
            end = datetime.fromisoformat(config["window_end"])
            request = build_request(config, query_id="WD01", results_wanted=25,
                                    charge_cap_usd="0.05", campaign_root=root,
                                    now=(end + timedelta(minutes=5)).isoformat())
            self.assertEqual(request["input"]["posted_date"], "30d")
            with self.assertRaisesRegex(ExecutionGateError, "stale_window_end"):
                build_request(config, query_id="WD01", results_wanted=25,
                              charge_cap_usd="0.05", campaign_root=root,
                              now=(end + timedelta(hours=2)).isoformat())

    def test_disabled_execution_and_unknown_query_are_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            config = self.config(root)
            config["live_collection_enabled"] = False
            with self.assertRaises(ExecutionGateError):
                verify_execution_gate(config, query_id="WD01", results_wanted=5, charge_cap_usd="0.01", campaign_root=root)
            config["live_collection_enabled"] = True
            with self.assertRaises(ExecutionGateError):
                build_request(config, query_id="not-registered", results_wanted=5, charge_cap_usd="0.01", campaign_root=root)

    def test_nonfinite_cap_missing_scope_and_excessive_cap_are_rejected_offline(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            config = self.config(root)
            for cap in ("NaN", "Infinity", "0", "0.06"):
                with self.assertRaises(ExecutionGateError):
                    build_request(config, query_id="WD01", results_wanted=1, charge_cap_usd=cap,
                                  campaign_root=root, now=config["window_end"])
            config["live_adapter"]["campaign_ceiling_usd"] = "0.31"
            with self.assertRaisesRegex(ExecutionGateError, "campaign_ceiling_exceeds_pilot_limit"):
                build_request(config, query_id="WD01", results_wanted=1, charge_cap_usd="0.05",
                              campaign_root=root, now=config["window_end"])
            config["live_adapter"].pop("authorized_collection_scope")
            with self.assertRaises(ExecutionGateError):
                build_request(config, query_id="WD01", results_wanted=1, charge_cap_usd="0.01",
                              campaign_root=root, now=config["window_end"])

    def test_configured_per_run_cap_is_enforced_below_global_ceiling(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            config = self.config(root)
            config["live_adapter"]["per_run_cap_usd"] = "0.02525"
            with self.assertRaisesRegex(ExecutionGateError, "charge_cap_exceeds_configured_per_run_cap"):
                build_request(config, query_id="WD01", results_wanted=25,
                              charge_cap_usd="0.05", campaign_root=root,
                              now=config["window_end"])
            request = build_request(config, query_id="WD01", results_wanted=25,
                                    charge_cap_usd="0.02525", campaign_root=root,
                                    now=config["window_end"])
            self.assertEqual(request["run_options"]["maxTotalChargeUsd"], 0.02525)

    def test_token_loader_prefers_environment_and_redacts_nested_values(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            with patch.dict(os.environ, {"APIFY_API_TOKEN": "sentinel-token"}):
                self.assertEqual(load_token(root), "sentinel-token")
            from scripts.jobs.apify_adapter import sanitize
            self.assertNotIn("sentinel-token", json.dumps(sanitize({"error": {"details": "sentinel-token"}}, "sentinel-token")))

    def test_token_loader_reads_explicit_repository_dotenv_path_and_rejects_blank(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / ".env").write_text("APIFY_API_TOKEN=from-file\n", encoding="utf-8")
            calls = []
            def fake_load(*, dotenv_path, override):
                calls.append((Path(dotenv_path), override))
                os.environ["APIFY_API_TOKEN"] = "from-file"
            with patch.dict(os.environ, {}, clear=True), patch.dict(sys.modules, {"dotenv": SimpleNamespace(load_dotenv=fake_load)}):
                self.assertEqual(load_token(root), "from-file")
                self.assertEqual(calls, [(root / ".env", False)])
                os.environ["APIFY_API_TOKEN"] = " "
                with self.assertRaises(ExecutionGateError): load_token(root)

    def test_start_is_single_post_even_when_followup_poll_fails(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            request = build_request(self.config(root), query_id="WD01", results_wanted=2,
                                    charge_cap_usd="0.05", campaign_root=root)
            calls = []
            def fake(method, path, query, body, timeout, headers):
                calls.append((method, path))
                if method == "POST":
                    return {"data": {"id": "r1", "actId": request["actor_id"], "buildId": request["expected_build_id"],
                                     "defaultDatasetId": "d1", "status": "READY",
                                     "options": {"build": request["expected_build_number"], "timeoutSecs": 300,
                                         "memoryMbytes": request["run_options"]["memory"], "maxTotalChargeUsd": 0.05, "restartOnError": False}}}, {}
                raise AdapterError("http_503", "temporary")
            state = AcquisitionState(root)
            transport = ApifyTransport("sentinel", fake)
            run = start_run(request, transport, state)
            with self.assertRaises(AdapterError):
                poll_run("r1", transport, state, request["request_id"], timeout_secs=1,
                         clock=lambda: 0, sleep=lambda _: None)
            self.assertEqual(sum(method == "POST" for method, _ in calls), 1)
            self.assertEqual(run["id"], "r1")

    def test_failed_start_preserves_redacted_provider_error_without_retry(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            request = build_request(self.config(root), query_id="WD01", results_wanted=2,
                                    charge_cap_usd="0.05", campaign_root=root)
            calls = []
            def fake(method, path, query, body, timeout, headers):
                calls.append(method)
                raise AdapterError("http_400", "invalid input; token sentinel-token")
            state = AcquisitionState(root)
            with self.assertRaisesRegex(AdapterError, "start_outcome_unknown"):
                start_run(request, ApifyTransport("sentinel-token", fake), state)
            record = state.get(request["request_id"])
            self.assertEqual(calls, ["POST"])
            self.assertEqual(record["status"], "start_outcome_unknown")
            self.assertEqual(record["billing_status"], "reserved")
            self.assertEqual(record["last_error_category"], "http_400")
            self.assertIn("invalid input", record["last_error_message"])
            self.assertNotIn("sentinel-token", json.dumps(record))
            evidence = root / "no-run.json"
            evidence.write_text('{"result":"no run"}', encoding="utf-8")
            state.reconcile_no_run(request["request_id"], evidence)
            record = state.get(request["request_id"])
            self.assertEqual(record["status"], "failed")
            self.assertEqual(record["start_error_category"], "http_400")
            self.assertIn("invalid input", record["start_error_message"])
            self.assertNotIn("sentinel-token", json.dumps(record))

    def test_download_preserves_complete_multi_page_items_and_checkpoints(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            state = AcquisitionState(root)
            request = {"request_id": "req", "campaign_root": str(root), "reserved_usd": "0.05", "input": {}, "config_sha256": "x"}
            state.reserve(request)
            state.update("req", "running", run_id="r1")
            source = [{"id": 1, "nested": {"v": "你好"}}, {"salary": None}, {"html": "<b>x</b>"}]
            def fake(method, path, query, body, timeout, headers):
                if path == "/v2/datasets/d1": return {"data": {"itemCount": 3}}, {}
                offset = query["offset"]
                page = source[offset:offset + query["limit"]]
                return page, {"x-apify-pagination-total": "3", "x-apify-pagination-offset": str(offset)}
            result = download_dataset({"id": "r1", "defaultDatasetId": "d1", "status": "SUCCEEDED"},
                ApifyTransport("sentinel", fake), state, "req", page_size=2, sleep=lambda _: None)
            self.assertEqual(json.loads(result.read_text(encoding="utf-8")), source)
            self.assertTrue((root / "raw" / "r1" / "pages" / "0.json").is_file())
            self.assertTrue((root / "raw" / "r1" / "pages" / "2.json").is_file())

    def test_preflight_checks_saved_contract_against_pinned_build_without_post(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            config = self.config(root)
            request = build_request(config, query_id="WD01", results_wanted=2, charge_cap_usd="0.05",
                                    campaign_root=root, now=config["window_end"])
            snapshot = json.loads(Path(request["actor_contract_evidence"]).read_text(encoding="utf-8"))
            calls = []
            def fake(method, path, query, body, timeout, headers):
                calls.append(method)
                if "/builds/" in path:
                    live_schema = json.loads(json.dumps(snapshot["input_schema"]))
                    for name, field in live_schema["properties"].items():
                        field["editor"] = "select" if name in {"country", "posted_date"} else "textfield"
                    live_schema["properties"]["results_wanted"]["minimum"] = 1
                    return {"data": {"id": request["expected_build_id"], "buildNumber": request["expected_build_number"],
                                     "actorDefinition": {"input": live_schema}}}, {}
                actual_events = {}
                for index, event in enumerate(snapshot["pricing"]["events"]):
                    if "tieredPricing" in event:
                        actual_events[str(index)] = {"eventTitle": event["title"], "eventTieredPricingUsd": {
                            tier["tier"]: {"tieredEventPriceUsd": tier["priceUsd"]} for tier in event["tieredPricing"]}}
                    else:
                        actual_events[str(index)] = {"eventTitle": event["title"], "eventPriceUsd": event["priceUsd"]}
                return {"data": {"id": request["actor_id"], "pricingInfos": [{"startedAt": "2026-10-01T00:00:00Z",
                    "pricingModel": snapshot["pricing"]["model"], "pricingPerEvent": {"actorChargeEvents": actual_events}}]}}, {}
            result = preflight(config, request, ApifyTransport("sentinel", fake))
            self.assertEqual(result["build_id"], request["expected_build_id"])
            self.assertEqual(calls, ["GET", "GET"])

    def test_download_recovers_page_saved_before_checkpoint_without_refetching_it(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            state = AcquisitionState(root)
            state.reserve({"request_id": "req", "campaign_root": str(root), "reserved_usd": "0.05", "input": {}, "config_sha256": "x"})
            page_dir = root / "raw" / "r1" / "pages"
            page_dir.mkdir(parents=True)
            (page_dir / "0.json").write_text('[{"value":"saved"}]', encoding="utf-8")
            def fake(method, path, query, body, timeout, headers):
                if path == "/v2/datasets/d1": return {"data": {"itemCount": 1}}, {}
                raise AssertionError("saved source page must not be fetched or replaced")
            result = download_dataset({"id": "r1", "defaultDatasetId": "d1"}, ApifyTransport("s", fake), state,
                                      "req", page_size=10, sleep=lambda _: None)
            self.assertEqual(json.loads(result.read_text(encoding="utf-8")), [{"value": "saved"}])
            self.assertTrue(json.loads((page_dir / "0.metadata.json").read_text(encoding="utf-8"))["recovered_checkpoint"])


if __name__ == "__main__":
    unittest.main()
