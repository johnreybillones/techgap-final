"""Source-based checks for the syllabus sample and repeatable batch command."""

import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "extract_syllabi.py"
SAMPLE = ROOT / "csv" / "old_curriculum" / "S-ITWB311LA Web Development Lab.pdf"


class SyllabusCollectionTests(unittest.TestCase):
    def run_command(self, source, output):
        self.assertTrue(SCRIPT.is_file(), "The batch extraction script is missing")
        return subprocess.run(
            [sys.executable, "-B", str(SCRIPT), str(source), "--output", str(output)],
            capture_output=True, text=True, encoding="utf-8", check=False,
        )

    def sample_result(self, output):
        run = self.run_command(SAMPLE, output)
        self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
        return json.loads((output / (SAMPLE.name + ".json")).read_text(encoding="utf-8"))

    def test_sample_preserves_fields_and_cross_page_learning_outcomes(self):
        with tempfile.TemporaryDirectory() as temp:
            record = self.sample_result(Path(temp))
        self.assertEqual(record["status"], "ok")
        self.assertEqual(record["course_code"], "S-ITWB311LA")
        self.assertEqual(record["course_title"], "Web Development")
        self.assertEqual(record["course_type"], "Laboratory")
        self.assertEqual(record["course_credit"], "One (1) Unit")
        self.assertEqual(record["prerequisites"], "None")
        self.assertEqual(record["corequisites"], "S-ITWB311")
        self.assertTrue(record["course_description"].endswith("using PHP and MySQL."))
        self.assertEqual(len(record["course_learning_outcomes"]), 6)
        self.assertEqual(record["course_learning_outcomes"][3]["text"],
                         "Evaluate design standards in planning layout, design and development of a complete website.")
        midterm, final = record["learning_plan"]
        self.assertEqual([midterm["period"], final["period"]], ["Midterm", "Final"])
        self.assertEqual([x["id"] for x in midterm["course_learning_outcomes"]],
                         ["CLO1", "CLO2", "CLO3", "CLO6"])
        self.assertEqual([x["id"] for x in final["course_learning_outcomes"]],
                         ["CLO1", "CLO2", "CLO4", "CLO5", "CLO6"])
        self.assertEqual([x["id"] for x in midterm["topic_learning_outcomes"]],
                         ["TLO1", "TLO2", "TLO3"])
        self.assertEqual([x["id"] for x in final["topic_learning_outcomes"]],
                         ["TLO4", "TLO5", "TLO6"])
        self.assertEqual(final["topic_learning_outcomes"][-1]["text"],
                         "Learn PHP Web Concepts and MySQL")
        self.assertEqual(final["source_pages"], [5, 6])
        self.assertEqual(midterm["additional_text"],
                         ["Collaboration, Skilled Communication, Knowledge Construction, Self-Regulation, Real-World Problem-Solving."])
        self.assertEqual(record["source"]["sha256"], hashlib.sha256(SAMPLE.read_bytes()).hexdigest())

    def test_weekly_tables_and_unrequested_sections_are_excluded(self):
        with tempfile.TemporaryDirectory() as temp:
            record = self.sample_result(Path(temp))
        content = json.dumps(record, ensure_ascii=False)
        for excluded in ["Week 1", "Module 0", "Schoolbook", "Enabling Assessment",
                         "Gospel Reading", "CONSULTATION", "GRADING SYSTEM", "netacad"]:
            self.assertNotIn(excluded.casefold(), content.casefold())
        self.assertNotIn("clo_tlo_pairs", content)

    def test_batch_continues_after_failure_and_preserves_same_named_files(self):
        with tempfile.TemporaryDirectory() as temp:
            source, output = Path(temp) / "input", Path(temp) / "output"
            for folder in ["a", "b"]:
                (source / folder).mkdir(parents=True)
                shutil.copy2(SAMPLE, source / folder / "course.pdf")
            (source / "broken.pdf").write_bytes(b"not a PDF")
            run = self.run_command(source, output)
            self.assertEqual(run.returncode, 1, run.stdout + run.stderr)
            summary = json.loads((output / "summary.json").read_text(encoding="utf-8"))
            self.assertEqual(summary["counts"], {"ok": 2, "needs_review": 0, "failed": 1})
            self.assertEqual(len(summary["files"]), 3)
            before = (output / "a" / "course.pdf.json").read_bytes()
            self.assertTrue((output / "b" / "course.pdf.json").is_file())
            failure = json.loads((output / "broken.pdf.json").read_text(encoding="utf-8"))
            self.assertEqual(failure["status"], "failed")
            self.assertTrue(failure["error"])
            self.run_command(source, output)
            self.assertEqual((output / "a" / "course.pdf.json").read_bytes(), before)


if __name__ == "__main__":
    unittest.main()
