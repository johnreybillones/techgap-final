import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path

from scripts.jobs.collect import main
from tests.collection.test_apify_adapter import AdapterPreviewTests


class LiveCliTests(unittest.TestCase):
    def campaign(self, root):
        config = AdapterPreviewTests().config(root)
        config["campaign_id"] = "c1"
        (root / "collection_config.json").write_text(json.dumps(config), encoding="utf-8")
        return root

    def test_bare_collect_requires_explicit_execution_mode(self):
        with self.assertRaises(SystemExit) as error:
            main(["collect", "somewhere"])
        self.assertEqual(error.exception.code, 2)

    def test_dry_run_prints_preview_without_token_or_request(self):
        with tempfile.TemporaryDirectory() as temp:
            root = self.campaign(Path(temp))
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                result = main(["collect", str(root), "--query-id", "WD01", "--results-wanted", "25",
                               "--charge-cap-usd", "0.05", "--dry-run"])
            self.assertEqual(result, 0)
            preview = json.loads(output.getvalue())
            self.assertEqual(preview["input"]["keyword"], "web developer")
            self.assertFalse((root / "requests").exists())

    def test_resume_parser_rejects_query_and_cost_replacement(self):
        with self.assertRaises(SystemExit) as error:
            main(["resume", "somewhere", "--request-id", "r", "--query-id", "WD01"])
        self.assertEqual(error.exception.code, 2)


if __name__ == "__main__": unittest.main()
