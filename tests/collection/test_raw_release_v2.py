import json
import tempfile
import unittest
from pathlib import Path

from scripts.jobs.release import attach_admission_feedback, migrate_raw_release, freeze_raw_release, validate_release
from scripts.jobs.collect import main, prepare


def write_jsonl(path, rows):
    path.write_text("".join(json.dumps(row, sort_keys=True) + "\n" for row in rows), encoding="utf-8")


class RawReleaseV2Tests(unittest.TestCase):
    def test_cli_import_then_default_freeze_preserves_valid_and_invalid_raw_items(self):
        with tempfile.TemporaryDirectory() as temp:
            root = prepare(temp, "cli", "2026-10-23T00:00:00Z", target=25)
            payload = {"id": "77", "url": "https://ph.jobstreet.com/job/77", "title": "Data Engineer",
                       "description_text": "Build and maintain data systems", "postedAt_iso": "2026-10-20T00:00:00Z"}
            invalid = {"title": "Missing source identity", "description_text": "Preserve this payload"}
            dataset = root / "saved.json"
            dataset.write_text(json.dumps([payload, invalid]), encoding="utf-8")
            self.assertEqual(main(["import", str(root), str(dataset), "--run-id", "saved-run", "--query-id", "IS03"]), 0)
            self.assertEqual(main(["freeze", str(root), "--release-id", "raw-cli", "--phase", "saved",
                                   "--target", "25", "--window-start", "2026-09-23T00:00:00Z",
                                   "--window-end", "2026-10-23T00:00:00Z"]), 0)
            self.assertTrue(validate_release(root)["valid"])
            manifest = json.loads((root / "manifest.json").read_text(encoding="utf-8"))
            frame = [json.loads(line) for line in (root / "source_frame.jsonl").read_text(encoding="utf-8").splitlines()]
            observations = [json.loads(line) for line in (root / "observations.jsonl").read_text(encoding="utf-8").splitlines()]
            invalid_rows = [json.loads(line) for line in (root / "invalid_items.jsonl").read_text(encoding="utf-8").splitlines()]
            self.assertEqual(manifest["schema_version"], "job-collection-raw-v2")
            self.assertEqual([row["source_id"] for row in frame], ["77"])
            self.assertEqual(frame[0]["query_ids"], ["IS03"])
            self.assertEqual(frame[0]["run_ids"], ["saved-run"])
            self.assertEqual(frame[0]["observation_ids"], [observations[0]["observation_id"]])
            self.assertTrue((root / frame[0]["selected_raw_file"]).is_file())
            self.assertEqual(json.loads((root / frame[0]["selected_raw_file"]).read_text())["description_text"], payload["description_text"])
            self.assertEqual(len(invalid_rows), 1)
            self.assertEqual(invalid_rows[0]["run_id"], "saved-run")
            self.assertTrue((root / invalid_rows[0]["raw_file"]).is_file())
            self.assertEqual(json.loads((root / invalid_rows[0]["raw_file"]).read_text()), invalid)
            audit = json.loads((root / "collection_audit.json").read_text(encoding="utf-8"))
            self.assertTrue(audit["all_invalid_items_have_raw_link"])
            self.assertIn("observations.jsonl", manifest["artifact_hashes"])
            self.assertEqual(main(["freeze", str(root), "--release-id", "again", "--window-start", "2026-09-23T00:00:00Z",
                                   "--window-end", "2026-10-23T00:00:00Z"]), 1)
            self.assertEqual(validate_release(root), {"valid": True, "errors": []})

    def test_explicit_legacy_freeze_command_remains_callable(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            self.build_campaign(root)
            self.assertEqual(main(["freeze-legacy", str(root), "--release-id", "legacy", "--target", "1",
                                   "--window-start", "2026-09-01T00:00:00Z", "--window-end", "2026-10-23T00:00:00Z"]), 0)
            self.assertEqual(json.loads((root / "manifest.json").read_text())["schema_version"], "job-collection-v1")

    def build_campaign(self, root):
        raw = root / "raw" / "run-1"
        raw.mkdir(parents=True)
        payload = {"id": "1", "url": "https://ph.jobstreet.com/job/1", "title": "Developer",
                   "description_text": "Build software", "postedAt_iso": "2026-10-01T00:00:00Z",
                   "location": "Manila"}
        (raw / "h1.json").write_text(json.dumps(payload), encoding="utf-8")
        write_jsonl(root / "postings.jsonl", [{"posting_key": "jobstreet:ph:1", "source_id": "1",
                                                "source_url": payload["url"]}])
        write_jsonl(root / "versions.jsonl", [{"posting_key": "jobstreet:ph:1", "version_id": "v1",
                                                "raw_hash": "h1", "raw_file": "raw/run-1/h1.json",
                                                "full_description": True, "fields": payload}])
        write_jsonl(root / "observations.jsonl", [{"observation_id": "o1", "posting_key": "jobstreet:ph:1",
                                                    "version_id": "v1", "run_id": "run-1", "query_id": "Q1",
                                                    "raw_hash": "h1", "raw_file": "raw/run-1/h1.json"}])
        write_jsonl(root / "runs.jsonl", [])
        write_jsonl(root / "source_runs.jsonl", [])
        write_jsonl(root / "invalid_items.jsonl", [])
        (root / "collection_config.json").write_text(json.dumps({"campaign_id": "c1"}), encoding="utf-8")

    def test_raw_release_includes_every_source_without_legacy_filter(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            self.build_campaign(root)
            write_jsonl(root / "admission.jsonl", [{"posting_key": "jobstreet:ph:1", "state": "excluded"}])
            manifest = freeze_raw_release(root, release_id="raw-r1", phase="saved-baseline",
                                          requested_target=1000, window_start="2026-09-01T00:00:00Z",
                                          window_end="2026-10-23T00:00:00Z", reported_charge_usd=None)
            frame = [json.loads(line) for line in (root / "source_frame.jsonl").read_text().splitlines()]
            self.assertEqual(len(frame), 1)
            self.assertEqual(frame[0]["posting_key"], "jobstreet:ph:1")
            self.assertNotIn("admission", frame[0])
            self.assertEqual(manifest["schema_version"], "job-collection-raw-v2")
            self.assertEqual(manifest["admission_status"], "not_classified")
            self.assertIsNone(manifest["admission_feedback"])
            self.assertTrue(validate_release(root)["valid"])

    def test_feedback_join_validates_raw_hash_and_source_equation(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            self.build_campaign(root)
            manifest = freeze_raw_release(root, release_id="raw-r1", phase="saved-baseline",
                                          requested_target=1000, window_start="2026-09-01T00:00:00Z",
                                          window_end="2026-10-23T00:00:00Z", reported_charge_usd=None)
            feedback = {"schema_version": "job-admission-feedback-v1", "release_id": "a1",
                        "release_path": "admission/a1/manifest.json", "release_sha256": "abc",
                        "raw_input_sha256": manifest["source_membership_sha256"],
                        "policy_version": "entry-junior-internship-v3-auto",
                        "model_versions": {"extractor": "x", "retriever": "y", "classifier": "z"},
                        "taxonomy_version": "esco-v1", "input_postings": 1,
                        "accepted_employment": 1, "accepted_internship": 0, "rejected": 0,
                        "accepted_count_units": 1, "count_unit_membership_sha256": "units"}
            joined = attach_admission_feedback(root, feedback)
            self.assertEqual(joined["admission_status"], "classified")
            self.assertEqual(json.loads((root / "admission_feedback.json").read_text())["release_id"], "a1")

            feedback["raw_input_sha256"] = "wrong"
            with self.assertRaisesRegex(ValueError, "raw_input_hash_mismatch"):
                attach_admission_feedback(root, feedback)

    def test_source_index_selects_the_longest_saved_description(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            self.build_campaign(root)
            write_jsonl(root / "source_runs.jsonl", [{"run_id": "run-1", "dataset_id": "dataset-1",
                "actor_id": "actor-1", "actor": "example/actor", "build_id": "build-id", "build": "1.2.3"}])
            payload = {"id": "1", "url": "https://ph.jobstreet.com/job/1", "title": "Developer",
                       "description_text": "Short teaser", "postedAt_iso": "2026-10-02T00:00:00Z",
                       "location": "Cebu", "workType": "Full time"}
            (root / "raw" / "run-2").mkdir()
            (root / "raw" / "run-2" / "h2.json").write_text(json.dumps(payload), encoding="utf-8")
            versions = [json.loads(line) for line in (root / "versions.jsonl").read_text().splitlines()]
            versions.extend([
                {"posting_key": "jobstreet:ph:1", "version_id": "v2", "raw_hash": "h2",
                 "raw_file": "raw/run-2/h2.json", "full_description": True, "fields": payload}])
            write_jsonl(root / "versions.jsonl", versions)
            observations = [json.loads(line) for line in (root / "observations.jsonl").read_text().splitlines()]
            observations.append({"observation_id": "o2", "posting_key": "jobstreet:ph:1", "version_id": "v2",
                                 "run_id": "run-2", "query_id": "Q2", "raw_file": "raw/run-2/h2.json"})
            write_jsonl(root / "observations.jsonl", observations)
            freeze_raw_release(root, release_id="raw-r1", phase="saved-baseline", requested_target=1,
                               window_start="2026-09-01T00:00:00Z", window_end="2026-10-23T00:00:00Z",
                               reported_charge_usd=None)
            row = json.loads((root / "source_frame.jsonl").read_text().strip())
            self.assertEqual(row["selected_version_id"], "v1")
            self.assertEqual(row["alternate_version_ids"], ["v2"])
            self.assertEqual(row["original_title"], "Developer")
            self.assertEqual(row["employer"], None)
            self.assertEqual(row["description_completeness"], "short")
            self.assertFalse(row["source_field_flags"]["company"])
            self.assertEqual(row["run_observations"][0]["query_id"], "Q1")
            self.assertEqual(row["run_observations"][0]["run_id"], "run-1")
            self.assertEqual(row["run_observations"][0]["dataset_id"], "dataset-1")
            self.assertEqual(row["run_observations"][0]["build_id"], "build-id")

    def test_migration_creates_new_release_without_mutating_source(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            source = base / "source"
            source.mkdir()
            self.build_campaign(source)
            legacy = source / "manifest.json"
            legacy.write_text('{"schema_version":"job-collection-v1"}\n', encoding="utf-8")
            destination = base / "raw-v2"
            manifest = migrate_raw_release(source, destination, release_id="raw-r1", phase="saved-baseline",
                                           requested_target=1000, window_start="2026-09-01T00:00:00Z",
                                           window_end="2026-10-23T00:00:00Z", reported_charge_usd=None)
            self.assertEqual(json.loads(legacy.read_text())["schema_version"], "job-collection-v1")
            self.assertEqual(manifest["schema_version"], "job-collection-raw-v2")
            self.assertTrue((destination / "raw" / "run-1" / "h1.json").is_file())
            with self.assertRaises(FileExistsError):
                migrate_raw_release(source, destination, release_id="raw-r2", phase="saved-baseline",
                                    requested_target=1000, window_start="2026-09-01T00:00:00Z",
                                    window_end="2026-10-23T00:00:00Z", reported_charge_usd=None)


if __name__ == "__main__":
    unittest.main()
