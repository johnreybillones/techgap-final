import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from jobs.registry import Registry
from jobs.admission import evaluate
from jobs.contracts import canonical_hash, validate_item
from jobs.release import freeze_release, validate_release
from jobs.collect import prepare, import_run


class CollectionTests(unittest.TestCase):
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
            self.assertEqual(len((root / "eligible_frame.jsonl").read_text(encoding="utf-8").splitlines()), 1)
            self.assertTrue((root / "raw" / "r1" / "items.jsonl").is_file())


if __name__ == "__main__":
    unittest.main()
