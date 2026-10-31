import csv
import json
import tempfile
import unittest
from pathlib import Path

from scripts.jobs.audit_saved_campaign import audit, write_review_sheet
from scripts.jobs.collect import query_registry


def write_jsonl(path, rows):
    path.write_text("".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8")


class SavedCampaignAuditTests(unittest.TestCase):
    def test_recovery_funnel_uses_linked_runs_and_keeps_cohorts_and_reasons(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp) / "base"
            root = Path(temp) / "raw"
            base.mkdir(); root.mkdir()
            (root / "collection_config.json").write_text(json.dumps({"queries": query_registry()}), encoding="utf-8")
            write_jsonl(base / "postings.jsonl", [{"source_id": "old"}])
            posts = [
                {"posting_key": "jobstreet:ph:old", "source_id": "old"},
                {"posting_key": "jobstreet:ph:new-missing", "source_id": "new-missing"},
                {"posting_key": "jobstreet:ph:new-intern", "source_id": "new-intern"},
            ]
            write_jsonl(root / "postings.jsonl", posts)
            internship_text = "Intern software developer will build Python applications and maintain database systems. " + ("Technical duties and requirements. " * 10)
            write_jsonl(root / "versions.jsonl", [
                {"posting_key": posts[0]["posting_key"], "version_id": "v-old", "raw_file": "raw/old.json", "fields": {"title": "Software Engineer", "description_text": internship_text}},
                {"posting_key": posts[1]["posting_key"], "version_id": "v-missing", "raw_file": "raw/missing.json", "fields": {"title": "Software Developer"}},
                {"posting_key": posts[2]["posting_key"], "version_id": "v-intern", "raw_file": "raw/intern.json", "fields": {"title": "Software Developer Internship", "description_text": internship_text}},
            ])
            obs = [
                {"posting_key": posts[0]["posting_key"], "query_id": "SH01", "run_id": "recovered"},
                {"posting_key": posts[0]["posting_key"], "query_id": "SH01", "run_id": "recovered"},
                {"posting_key": posts[1]["posting_key"], "query_id": "SH01", "run_id": "recovered"},
                {"posting_key": posts[1]["posting_key"], "query_id": "SH01", "run_id": "recovered"},
                {"posting_key": posts[2]["posting_key"], "query_id": "SH01", "run_id": "recovered"},
                {"posting_key": posts[0]["posting_key"], "query_id": "SH01", "run_id": "outside"},
            ]
            write_jsonl(root / "observations.jsonl", obs)
            write_jsonl(root / "invalid_items.jsonl", [{"run_id": "recovered", "query_id": "SH01"}])
            recovery = Path(temp) / "recovery.json"
            recovery.write_text(json.dumps({"recovered_datasets": [{"run_id": "recovered"}]}), encoding="utf-8")
            report = audit(root, base, recovery)
            funnel = report["summary"]["incremental_funnel"]
            self.assertEqual(funnel["combined"], {"returned_rows": 6, "new_distinct_ids": 2,
                "provisional_relevant": 2, "provisional_technically_assessable": 1})
            self.assertEqual(funnel["employment"]["returned_rows"], 2)
            self.assertEqual(funnel["internship"]["new_distinct_ids"], 1)
            quality = {row["source_id"]: row for row in report["description_quality_by_source_id"]}
            self.assertEqual(quality["new-missing"]["description_quality"], "absent")
            self.assertEqual(quality["new-missing"]["unassessable_reason"], "description_absent")
            self.assertEqual(report["summary"]["returned_observations"], 6)

    def test_audit_uses_source_text_and_reports_overlap_and_baseline_delta(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "raw"
            base = Path(temp) / "base"
            root.mkdir()
            base.mkdir()
            (root / "collection_config.json").write_text(json.dumps({"queries": query_registry()}), encoding="utf-8")
            (base / "postings.jsonl").write_text('{"source_id":"old"}\n', encoding="utf-8")
            posts = [{"posting_key": "jobstreet:ph:old", "source_id": "old"},
                     {"posting_key": "jobstreet:ph:new", "source_id": "new"}]
            write_jsonl(root / "postings.jsonl", posts)
            long_text = "Develop and maintain Python software systems. " + ("Technical duties and requirements. " * 10)
            versions = [{"posting_key": row["posting_key"], "version_id": "v" + str(i), "fields": {
                "title": "Data Engineer" if i == 0 else "Software Intern", "description_text": long_text}}
                for i, row in enumerate(posts)]
            write_jsonl(root / "versions.jsonl", versions)
            write_jsonl(root / "observations.jsonl", [
                {"posting_key": "jobstreet:ph:old", "query_id": "IS03"},
                {"posting_key": "jobstreet:ph:old", "query_id": "SH01"},
                {"posting_key": "jobstreet:ph:new", "query_id": "GD01"}])
            report = audit(root, base)
            summary = report["summary"]
            self.assertEqual(summary["distinct_source_ids"], 2)
            self.assertEqual(summary["new_distinct_ids_vs_baseline"], 1)
            self.assertEqual(summary["new_provisional_assessable_ids"], 1)
            is_query = next(q for q in report["query_results"] if q["query_id"] == "IS03")
            self.assertEqual(is_query["overlapping_ids"], 1)
            self.assertEqual(len(report["proposed_queries"]), 6)
            self.assertEqual(report["proposed_queries"][0]["query"], "data engineer")
            review = write_review_sheet(root, report, Path(temp) / "review.csv")
            with review.open(encoding="utf-8-sig") as stream:
                sheet = list(csv.DictReader(stream))
            self.assertTrue(sheet)
            self.assertTrue(all(row["reviewer_decision"] == "pending" for row in sheet))


if __name__ == "__main__":
    unittest.main()
