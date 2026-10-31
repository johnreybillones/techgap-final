import json
import tempfile
import unittest
from pathlib import Path

from scripts import pre_model_data as pre


class TextPreparationTests(unittest.TestCase):
    def test_html_keeps_structure_and_ignores_hidden_content(self):
        value = '<h2>Requirements</h2><nav>noise</nav><p>Python or R</p><ul><li>SQL and C++</li></ul><div hidden>secret</div>'
        self.assertEqual(pre.visible_html(value), "Requirements\nPython or R\nSQL and C++")

    def test_job_url_requires_canonical_jobstreet_id(self):
        self.assertEqual(pre.job_id_from_url("https://ph.jobstreet.com/job/12345"), "12345")
        self.assertIsNone(pre.job_id_from_url("https://ph.jobstreet.com/jobs/12345"))

    def test_split_is_stable(self):
        self.assertEqual(pre.split_for_group("abc"), pre.split_for_group("abc"))

    def test_split_follows_bucket_ranges_70_10_20(self):
        names = [pre.split_for_group(str(i)) for i in range(2000)]
        self.assertEqual(set(names), {"train", "val", "test"})
        share = {s: names.count(s) / 2000 for s in set(names)}
        self.assertAlmostEqual(share["train"], 0.70, delta=0.04)
        self.assertAlmostEqual(share["val"], 0.10, delta=0.04)
        self.assertAlmostEqual(share["test"], 0.20, delta=0.04)

    def test_syllabus_track_mapping_does_not_broadcast_unknown_general(self):
        self.assertEqual(pre.syllabus_track("General & Foundational", "X", "Number Theory")[0], ["bscs_is", "bscs_game"])
        self.assertEqual(pre.syllabus_track("General & Foundational", "X", "Unknown")[1], "applicability_unresolved")

    def test_chunk_offsets_reproduce_exact_original(self):
        source = " ".join("word%d" % i for i in range(800))
        p = {"passage_id": "p", "text": source}
        for chunk in pre.make_chunks(p):
            self.assertEqual(source[chunk["chunk_start"]:chunk["chunk_end"]], chunk["text"])

    def test_span_validation_catches_changed_occurrence(self):
        item = {"passage_id": "p", "source_type": "syllabus", "text_sha256": pre.sha_bytes(b"Use SQL."), "text": "Use SQL."}
        decision = {"passage_id": "p", "source_type": "syllabus", "text_sha256": item["text_sha256"],
            "language": "english", "spans": [{"start": 4, "end": 7, "text": "SQL", "type": "tool_technology",
                "clause_start": 0, "clause_end": 8, "modality": "not_applicable"}],
            "passage_complete": True, "technical_content": "present", "agent": "a", "model": "m",
            "configuration": "c", "prompt_version": "technical-spans-v1"}
        self.assertIsNone(pre.validate_span(decision, item))
        decision["spans"][0]["text"] = "Sql"
        self.assertEqual(pre.validate_span(decision, item), "span_offset_mismatch")


class JobRootGateTests(unittest.TestCase):
    ROOT = "data/job_collections/x"

    def load(self, captured_at="2026-01-01T00:00:00Z", obs_extra=None, manifest=None):
        """Build one-observation job root in a temp repo and return (postings, stats, issues)."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / self.ROOT
            (root / "raw").mkdir(parents=True)
            (root / "raw" / "a.json").write_text("{}", encoding="utf-8")
            url = "https://ph.jobstreet.com/job/123"
            rows = {
                "observations.jsonl": {"observation_id": "o", "version_id": "v", "posting_key": "jobstreet:ph:123",
                                       "raw_file": "raw/a.json", "captured_at": captured_at, **(obs_extra or {})},
                "versions.jsonl": {"version_id": "v", "posting_key": "jobstreet:ph:123", "raw_file": "raw/a.json",
                                   "fields": {"canonical_url": url}},
                "postings.jsonl": {"posting_key": "jobstreet:ph:123", "source_id": "123", "source_url": url},
            }
            for name, row in rows.items():
                with open(root / name, "w", encoding="utf-8", newline="\n") as f:
                    f.write(json.dumps(row) + "\n")
            if manifest:
                (root / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
            issues = []
            old, pre.JOB_ROOTS = pre.JOB_ROOTS, (self.ROOT,)
            try:
                postings, stats, _ = pre.load_job_roots(Path(tmp), pre.parse_time("2026-10-27T00:00:00Z"), issues)
            finally:
                pre.JOB_ROOTS = old
            return postings, stats[self.ROOT], issues

    def test_known_time_observation_is_included(self):
        postings, stats, _ = self.load()
        self.assertEqual(list(postings), ["123"])
        self.assertFalse(stats["blocked_from_training"])

    def test_unknown_capture_time_is_excluded(self):
        postings, _, issues = self.load(captured_at=None)
        self.assertEqual(postings, {})
        self.assertIn("capture_time_unknown", [i["reason_code"] for i in issues])

    def test_raw_hash_mismatch_drops_observation_and_blocks_source(self):
        postings, stats, _ = self.load(obs_extra={"raw_hash": "0" * 64}, manifest={"raw_hash_method": "sha256_bytes"})
        self.assertEqual(postings, {})
        self.assertTrue(stats["blocked_from_training"])

    def test_index_hash_mismatch_skips_whole_root(self):
        postings, stats, _ = self.load(manifest={"artifact_hashes": {"observations.jsonl": "0" * 64}})
        self.assertEqual(postings, {})
        self.assertTrue(stats["blocked_from_training"])


class CheckedJobDecisionTests(unittest.TestCase):
    def test_only_checked_decisions_gate_jobs(self):
        ann = [
            {"kind": "job", "document_id": "a", "disposition": "accepted", "decision": {"relevance": "relevant"}},
            {"kind": "job", "document_id": "b", "disposition": "corrected", "decision": {"relevance": "unresolved"}},
            {"kind": "job", "document_id": "c", "disposition": "unresolved", "decision": None},
            {"kind": "span", "document_id": "d", "disposition": "accepted", "decision": {}},
        ]
        self.assertEqual(pre.final_job_decisions(ann),
                         {"a": {"relevance": "relevant"}, "b": {"relevance": "unresolved"}})


class HtmlEdgeTests(unittest.TestCase):
    def test_void_tag_inside_hidden_region_does_not_swallow_the_page(self):
        self.assertEqual(pre.visible_html("<nav>a<br>b</nav><p>keep</p>"), "keep")


if __name__ == "__main__":
    unittest.main()
