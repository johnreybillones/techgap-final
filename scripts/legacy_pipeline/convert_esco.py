"""Convert the ESCO occupations CSV into the pipeline's JSONL taxonomy contract."""

import csv
import json
from pathlib import Path
from typing import Dict, List


def _split_labels(value: str) -> List[str]:
    labels = []
    for item in (value or "").replace("|", "\n").splitlines():
        item = item.strip()
        if item and item not in labels:
            labels.append(item)
    return labels


def convert_occupations_csv(source: Path, output: Path) -> int:
    """Convert ESCO ``occupations_en.csv`` while preserving only model-ready fields."""
    rows_by_uri: Dict[str, Dict[str, object]] = {}
    with Path(source).open("r", encoding="utf-8-sig", newline="") as handle:
        for row in csv.DictReader(handle):
            if row.get("conceptType") != "Occupation":
                continue
            uri = (row.get("conceptUri") or "").strip()
            label = (row.get("preferredLabel") or "").strip()
            definition = (row.get("description") or row.get("definition") or "").strip()
            if not uri or not label:
                raise ValueError("ESCO occupation row requires conceptUri and preferredLabel")
            converted = {
                "uri": uri,
                "label": label,
                "aliases": _split_labels(row.get("altLabels", "")),
                "definition": definition,
            }
            existing = rows_by_uri.get(uri)
            if existing is None:
                rows_by_uri[uri] = converted
            else:
                existing["aliases"] = list(dict.fromkeys(
                    list(existing["aliases"]) + list(converted["aliases"])
                ))
                if not existing["definition"] and definition:
                    existing["definition"] = definition

    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_suffix(output.suffix + ".tmp")
    with temporary.open("w", encoding="utf-8", newline="\n") as handle:
        for row in rows_by_uri.values():
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
    temporary.replace(output)
    return len(rows_by_uri)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    print(convert_occupations_csv(args.source, args.output))
