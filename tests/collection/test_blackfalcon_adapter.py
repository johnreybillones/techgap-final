import json
import tempfile
import unittest
from pathlib import Path

from scripts.jobs.blackfalcon_adapter import normalize_item, import_items
from scripts.jobs.release import freeze_raw_release, validate_release


class BlackFalconAdapterTests(unittest.TestCase):
    def payload(self, **changes):
        row = {
            "jobId": "seek-job-hash-abc",
            "seekJobId": 12345678,
            "title": "Data Engineer",
            "canonicalUrl": "https://ph.jobstreet.com/job/12345678",
            "description": "Build ETL pipelines with Python and SQL. Required: AWS experience.",
            "descriptionHtml": "<p>Build ETL pipelines with Python and SQL. Required: AWS experience.</p>",
            "employmentType": "Full time",
            "location": "Makati City, Metro Manila",
            "postedDate": "2026-10-20T00:00:00Z",
            "searchUrl": "https://ph.jobstreet.com/jobs?keywords=data%20engineer&page=2",
        }
        row.update(changes)
        return row

    def provenance(self):
        return {"actor": "blackfalcondata/jobstreet-scraper", "actor_id": "owner~actor",
                "build_id": "build-id", "build_number": "1.2.3", "run_id": "run1",
                "dataset_id": "dataset1", "query_id": "data-engineer", "query": "data engineer",
                "captured_at": "2026-10-23T00:00:00Z"}

    def test_id_must_match_canonical_job_url_not_actor_job_id(self):
        normalized = normalize_item(self.payload(), self.provenance())
        self.assertEqual(normalized["posting_key"], "jobstreet:ph:12345678")
        self.assertNotIn("seek-job-hash-abc", normalized["posting_key"])
        bad = normalize_item(self.payload(canonicalUrl="https://ph.jobstreet.com/job/87654321"), self.provenance())
        self.assertFalse(bad["valid"])
        self.assertIn("seek_id_url_mismatch", bad["reasons"])

    def test_missing_identity_is_invalid_but_payload_remains_linked(self):
        result = normalize_item(self.payload(seekJobId=None), self.provenance())
        self.assertFalse(result["valid"])
        self.assertIn("missing_seek_job_id", result["reasons"])

    def test_description_and_supported_page_provenance_are_retained(self):
        result = normalize_item(self.payload(), self.provenance())
        self.assertEqual(result["derived"]["description_text"], self.payload()["description"])
        self.assertEqual(result["page_number"], 2)
        self.assertEqual(result["raw_payload"], self.payload())
        unknown = normalize_item(self.payload(searchUrl="https://ph.jobstreet.com/jobs?keywords=data%20engineer"), self.provenance())
        self.assertIsNone(unknown["page_number"])

    def test_import_deduplicates_ids_and_preserves_changed_description_versions_and_release_links(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            items = [self.payload(), self.payload(), self.payload(description="Changed: Python, SQL, dbt, Snowflake."),
                     self.payload(canonicalUrl="https://ph.jobstreet.com/job/999")]
            report = import_items(root, items, provenance=self.provenance())
            self.assertEqual(report["returned_rows"], 4)
            self.assertEqual(report["distinct_source_ids"], 1)
            self.assertEqual(report["invalid_rows"], 1)
            self.assertEqual(report["versions"], 2)
            raw_records = [json.loads(line) for line in (root / "raw" / "run1" / "items.jsonl").read_text().splitlines()]
            self.assertEqual(raw_records[0]["payload"], self.payload())
            self.assertEqual(raw_records[0]["provenance"], self.provenance())
            manifest = freeze_raw_release(root, release_id="test", phase="test", requested_target=1,
                window_start="2026-10-01T00:00:00Z", window_end="2026-10-23T00:00:00Z",
                reported_charge_usd="0.00")
            self.assertEqual(manifest["release_status"], "raw_ready")
            self.assertTrue(validate_release(root)["valid"])


if __name__ == "__main__":
    unittest.main()
