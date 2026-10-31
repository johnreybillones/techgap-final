import csv
import json
import tempfile
import unittest
from pathlib import Path

from scripts.legacy_pipeline.convert_esco import convert_occupations_csv


class EscoConversionTests(unittest.TestCase):
    def test_converts_occupation_fields_and_uses_description_for_definition(self):
        with tempfile.TemporaryDirectory() as temp:
            source = Path(temp) / "occupations_en.csv"
            output = Path(temp) / "occupations.jsonl"
            with source.open("w", encoding="utf-8", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=[
                    "conceptType", "conceptUri", "preferredLabel", "altLabels",
                    "definition", "description",
                ])
                writer.writeheader()
                writer.writerow({
                    "conceptType": "Occupation",
                    "conceptUri": "http://data.europa.eu/esco/occupation/1",
                    "preferredLabel": "Software developer",
                    "altLabels": "Programmer\nSoftware engineer",
                    "definition": "",
                    "description": "Develops software applications.",
                })

            count = convert_occupations_csv(source, output)
            row = json.loads(output.read_text(encoding="utf-8").strip())

            self.assertEqual(count, 1)
            self.assertEqual(row["uri"], "http://data.europa.eu/esco/occupation/1")
            self.assertEqual(row["label"], "Software developer")
            self.assertEqual(row["aliases"], ["Programmer", "Software engineer"])
            self.assertEqual(row["definition"], "Develops software applications.")


if __name__ == "__main__":
    unittest.main()
