import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from jobs.registry import Registry
from jobs.admission import evaluate
from jobs.contracts import validate_item, validate_run_metadata
from jobs.release import freeze_release, validate_release
from jobs.collect import _terminal_charge, prepare, import_run
from unittest.mock import patch


class CollectionTests(unittest.TestCase):
    def test_terminal_charge_prefers_settled_usage_total_on_every_path(self):
        self.assertEqual(_terminal_charge({"usageTotalUsd": 1.25, "chargedUsd": 9.0}), 1.25)
        self.assertEqual(_terminal_charge({"usageTotalUsd": None, "chargedUsd": 9.0}), 9.0)

    def test_import_preserves_verified_run_metadata_and_rejects_mismatches(self):
        metadata = {"run_id": "r2", "query_id": "WD01", "dataset_id": "d1", "actor_id": "a1",
                    "actor": "actor/name", "build": "0.0.36", "build_id": "b1",
                    "started_at": "2026-10-01T00:00:00Z", "finished_at": "2026-10-01T00:01:00Z", "status": "SUCCEEDED"}
        self.assertTrue(validate_run_metadata(metadata, run_id="r2", query_id="WD01")["valid"])
        self.assertFalse(validate_run_metadata(metadata, run_id="r3", query_id="WD01")["valid"])
        self.assertFalse(validate_run_metadata({**metadata, "pricing_info": {"authorization": "secret"}},
            run_id="r2", query_id="WD01")["valid"])
        with tempfile.TemporaryDirectory() as temp:
            root = prepare(Path(temp), "campaign", "2026-10-22T00:00:00+00:00")
            source = Path(temp) / "items.json"
            source.write_text("[]", encoding="utf-8")
            import_run(root, source, run_id="r2", query_id="WD01", run_metadata=metadata)
            import_run(root, source, run_id="r2", query_id="WD01", run_metadata=metadata)
            with self.assertRaisesRegex(ValueError, "Conflicting"):
                import_run(root, source, run_id="r2", query_id="WD01", run_metadata={**metadata, "dataset_id": "other"})
            row = __import__("json").loads((root / "runs.jsonl").read_text(encoding="utf-8"))
            self.assertEqual(row["dataset_id"], "d1")
            self.assertEqual(row["provider_status"], "SUCCEEDED")
            self.assertEqual(len(Registry(root).read_jsonl("observations.jsonl")), 0)
            root2 = prepare(Path(temp), "campaign-enrichment", "2026-10-22T00:00:00+00:00")
            import_run(root2, source, run_id="r2", query_id="WD01")
            import_run(root2, source, run_id="r2", query_id="WD01", run_metadata={**metadata, "provider_charge_usd": 0.02})
            source_run = Registry(root2).read_jsonl("source_runs.jsonl")[0]
            self.assertEqual(source_run["billing_status"], "reconciled")

    def test_import_is_idempotent_and_preserves_raw_payload(self):
        with tempfile.TemporaryDirectory() as temp:
            registry = Registry(Path(temp))
            item = {"id": "123", "url": "https://ph.jobstreet.com/job/123", "title": "Junior Developer", "salary": None,
                    "postedAt_iso": "2026-10-01T00:00:00Z", "location": "Manila, Philippines",
                    "description_text": "Fresh graduates welcome. Build software applications.", "workType": "Full time"}
            self.assertTrue(registry.import_item(item, run_id="r1", dataset_item_id="i1", query_id="WD01"))
            self.assertFalse(registry.import_item(item, run_id="r1", dataset_item_id="i1", query_id="WD01"))
            self.assertEqual(len(list((Path(temp) / "raw").rglob("*.json"))), 1)
            self.assertEqual(len(registry.read_jsonl("observations.jsonl")), 1)
            self.assertIsNone(registry.read_jsonl("versions.jsonl")[0]["fields"]["salary"])

    def test_raw_import_does_not_depend_on_or_write_legacy_admission(self):
        with tempfile.TemporaryDirectory() as temp:
            root = prepare(Path(temp), "repair", "2026-10-22T00:00:00+00:00")
            source = Path(temp) / "items.json"
            item = {"id": "123", "url": "https://ph.jobstreet.com/job/123", "title": "Junior Developer",
                "postedAt_iso": "2026-10-01T00:00:00Z", "location": "Manila, Philippines",
                "description_text": "Fresh graduates welcome. Build software applications.", "workType": "Full time"}
            source.write_text(__import__("json").dumps([item]), encoding="utf-8")
            registry = Registry(root)
            result = import_run(root, source, run_id="r1", query_id="WD01")
            self.assertEqual(result["new_observations"], 1)
            self.assertEqual(result["distinct_source_ids_observed"], 1)
            self.assertEqual(registry.read_jsonl("admission.jsonl"), [])
            self.assertFalse((root / "eligible_frame.jsonl").exists())

    def test_registry_repairs_raw_item_append_after_interrupted_observation_write(self):
        with tempfile.TemporaryDirectory() as temp:
            registry = Registry(Path(temp))
            item = {"id": "x1", "url": "https://ph.jobstreet.com/job/x1", "title": "Developer"}
            original = registry._append
            def fail_observation(name, row):
                if name == "observations.jsonl": raise OSError("simulated interruption")
                return original(name, row)
            with patch.object(registry, "_append", side_effect=fail_observation):
                with self.assertRaises(OSError): registry.import_item(item, run_id="r", dataset_item_id=0, query_id="WD01")
            registry.import_item(item, run_id="r", dataset_item_id=0, query_id="WD01")
            self.assertEqual(len(registry.read_jsonl("raw/r/items.jsonl")), 1)

    def test_salary_change_is_version_but_semantic_parse_cache_can_reuse_description(self):
        a = {"id":"1","url":"https://ph.jobstreet.com/job/1","title":"Junior Developer","salary":"₱1","description_text":"Build software"}
        b = {**a, "salary":"₱2"}
        with tempfile.TemporaryDirectory() as temp:
            registry=Registry(Path(temp))
            registry.import_item(a,run_id="r",dataset_item_id="1",query_id="WD01")
            registry.import_item(b,run_id="r",dataset_item_id="2",query_id="WD02")
            self.assertEqual(len(registry.read_jsonl("versions.jsonl")),2)
            self.assertEqual(registry.read_jsonl("versions.jsonl")[0]["description_hash"], registry.read_jsonl("versions.jsonl")[1]["description_hash"])

    def test_admission_requires_explicit_entry_evidence_and_complete_description(self):
        base={"id":"1","url":"https://ph.jobstreet.com/job/1","title":"Developer","postedAt_iso":"2026-10-01T00:00:00Z","location":"Manila, Philippines","description_text":"Build software applications. Fresh graduates welcome.","workType":"Full time"}
        result=evaluate(base, window_start="2026-09-22T00:00:00Z",window_end="2026-10-22T00:00:00Z")
        self.assertEqual(result["state"],"eligible")
        result=evaluate({**base,"description_text":"Build software applications. Requires 2 years of experience."},window_start="2026-09-22T00:00:00Z",window_end="2026-10-22T00:00:00Z")
        self.assertEqual(result["state"],"unresolved")
        result=evaluate({**base,"description_text":"","teaser":"Build software"},window_start="2026-09-22T00:00:00Z",window_end="2026-10-22T00:00:00Z")
        self.assertEqual(result["state"],"unresolved")

    def test_release_hashes_and_validates_artifacts(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)
            (root/"eligible_frame.jsonl").write_text("",encoding="utf-8")
            manifest=freeze_release(root,release_id="r1",phase="development_only",requested_target=1000,
                window_start="2026-09-22T00:00:00Z",window_end="2026-10-22T00:00:00Z",reported_charge_usd=0.0)
            self.assertEqual(manifest["achieved_eligible_count"],0)
            self.assertTrue(validate_release(root)["valid"])
            (root/"eligible_frame.jsonl").write_text("tampered",encoding="utf-8")
            self.assertFalse(validate_release(root)["valid"])

    def test_release_audit_reports_live_provenance_and_unknown_billing(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "eligible_frame.jsonl").write_text("", encoding="utf-8")
            (root / "source_runs.jsonl").write_text('{"run_id":"r1","status":"SUCCEEDED","billing_status":"unknown"}\n', encoding="utf-8")
            manifest = freeze_release(root, release_id="r1", phase="development_only", requested_target=1,
                window_start="2026-09-22T00:00:00Z", window_end="2026-10-22T00:00:00Z", reported_charge_usd=0.0)
            self.assertTrue(any("billing" in item for item in manifest["limitations"]))
            audit = __import__("json").loads((root / "collection_audit.json").read_text(encoding="utf-8"))
            self.assertFalse(audit["financially_reconciled"])

    def test_contract_rejects_missing_or_inconsistent_source_identity(self):
        self.assertFalse(validate_item({"id":"1","url":"https://ph.jobstreet.com/job/2"})["valid"])
        self.assertFalse(validate_item({"title":"No ID"})["valid"])

    def test_prepare_import_and_release_stay_offline_and_record_query_registry(self):
        with tempfile.TemporaryDirectory() as temp:
            root = prepare(Path(temp), "campaign", "2026-10-22T00:00:00+00:00")
            import json
            config = json.loads((root / "collection_config.json").read_text(encoding="utf-8"))
            self.assertEqual(len(config["queries"]), 34)
            source = Path(temp) / "items.json"
            item = {"id":"123","url":"https://ph.jobstreet.com/job/123","title":"Junior Developer",
                "postedAt_iso":"2026-10-01T00:00:00Z","location":"Manila, Philippines",
                "description_text":"Fresh graduates welcome. Build software applications.","workType":"Full time"}
            source.write_text(json.dumps([item]), encoding="utf-8")
            result = import_run(root, source, run_id="r1", query_id="WD01")
            self.assertEqual(result["new_observations"], 1)
            self.assertEqual(result["distinct_source_ids_observed"], 1)
            self.assertFalse((root / "admission.jsonl").exists())
            self.assertTrue((root / "raw" / "r1" / "items.jsonl").is_file())


if __name__ == "__main__":
    unittest.main()
