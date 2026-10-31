import json
import tempfile
import unittest
from pathlib import Path

from scripts.pipeline.classify_jobs import classify_posting
from scripts.pipeline.runner import run_admission_release
from scripts.pipeline.taxonomy import EscoTaxonomy, SentenceTransformerIndex
from scripts.pipeline.text import checked_span


class FakeExtractor:
    version = "extractor-test"

    def extract(self, text):
        return {"duties": [checked_span(text, 0, len(text), "duty")],
                "mandatory_experience_min_years": None,
                "explicit_senior_applicant_role": False,
                "internship_vacancy": False}


class FakeRetriever:
    version = "retriever-test"

    def retrieve(self, title, passages, limit):
        return [{"uri": "esco:developer", "label": "software developer", "definition": "build software"}]


class FakeClassifier:
    version = "classifier-test"

    def score(self, text, hypotheses):
        return {name: {"entailment": 1.0, "not_entailment": 0.0} for name in hypotheses}


class PipelineTests(unittest.TestCase):
    def test_semantic_index_uses_normalized_embeddings_and_descending_scores(self):
        class Model:
            def __init__(self): self.calls = []
            def encode(self, texts, **kwargs):
                self.calls.append((texts, kwargs))
                return [[1.0, 0.0], [0.0, 1.0]] if len(texts) == 2 else [[0.0, 1.0]]
        model = Model()
        rows = [{"uri": "a", "label": "A", "definition": "first"},
                {"uri": "b", "label": "B", "definition": "second"}]
        index = SentenceTransformerIndex(model, rows)
        self.assertEqual(index.search("query", limit=1)[0]["uri"], "b")
        self.assertTrue(all(call[1]["normalize_embeddings"] for call in model.calls))

    def test_checked_span_must_reproduce_source(self):
        span = checked_span("Build software", 0, 5, "duty")
        self.assertEqual(span["text"], "Build")
        with self.assertRaisesRegex(ValueError, "invalid_source_span"):
            checked_span("Build software", 8, 30, "duty")

    def test_esco_taxonomy_validates_unique_uris_and_aliases(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "esco.jsonl"
            path.write_text(json.dumps({"uri": "esco:developer", "label": "software developer",
                                        "aliases": ["programmer"], "definition": "build software"}) + "\n",
                            encoding="utf-8")
            taxonomy = EscoTaxonomy.load(path, version="esco-test")
            self.assertEqual(taxonomy.exact("Programmer")[0]["uri"], "esco:developer")
            path.write_text(path.read_text() + path.read_text(), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "duplicate_esco_uri"):
                EscoTaxonomy.load(path, version="esco-test")

    def test_classifier_runs_one_bounded_reconsideration(self):
        source = {"posting_key": "jobstreet:ph:1", "count_unit_id": "jobstreet:ph:1",
                  "selected_version_id": "v1", "selected_raw_hash": "h1",
                  "fields": {"title": "Developer", "description_text": "Build software",
                             "postedAt_iso": "2026-10-01T00:00:00Z", "location": "Manila"}}
        result = classify_posting(source, extractor=FakeExtractor(), retriever=FakeRetriever(),
                                  classifier=FakeClassifier(), taxonomy_version="esco-test",
                                  window_start="2026-09-01T00:00:00Z", window_end="2026-10-23T00:00:00Z")
        self.assertEqual(result["occupation"]["uri"], "esco:developer")
        self.assertTrue(result["computing_relevance_supported"])
        self.assertEqual(len(result["attempt_history"]), 1)

    def test_runner_writes_reconciled_hash_linked_release(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            raw = root / "raw.json"
            fields = {"id": "1", "title": "Developer", "description_text": "Build software",
                      "postedAt_iso": "2026-10-01T00:00:00Z", "location": "Manila"}
            raw.write_text(json.dumps(fields), encoding="utf-8")
            frame = root / "source_frame.jsonl"
            frame.write_text(json.dumps({"posting_key": "jobstreet:ph:1", "count_unit_id": "jobstreet:ph:1",
                                         "selected_version_id": "v1", "selected_raw_hash": "h1",
                                         "selected_raw_file": "raw.json"}) + "\n", encoding="utf-8")
            output = root / "admission-release"
            manifest = run_admission_release(frame, output, release_id="a1", raw_release_id="r1",
                                             extractor=FakeExtractor(), retriever=FakeRetriever(),
                                             classifier=FakeClassifier(), taxonomy_version="esco-test",
                                             window_start="2026-09-01T00:00:00Z",
                                             window_end="2026-10-23T00:00:00Z")
            self.assertEqual(manifest["summary"]["accepted_employment"], 1)
            self.assertTrue(manifest["summary"]["equation_reconciles"])
            self.assertTrue((output / "decisions.jsonl").is_file())
            self.assertTrue((output / "count_units.jsonl").is_file())
            self.assertEqual(manifest["raw_input_sha256"], __import__("hashlib").sha256(frame.read_bytes()).hexdigest())


if __name__ == "__main__":
    unittest.main()
