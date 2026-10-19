"""Extract selected fields from text-native DLSU-D CICS syllabus PDFs.

Usage: python scripts/extract_syllabi.py INPUT_PDF_OR_FOLDER --output OUTPUT_FOLDER
The initial template is verified only against the supplied Web Development Lab PDF.
"""

import argparse
import hashlib
import json
from pathlib import Path
import re

import pdfplumber


EXTRACTOR_VERSION = "dlsud-cics-v1"
LABELS = {
    "course_code": r"COURSE\s+CODE",
    "course_title": r"COURSE\s+TITLE",
    "course_type": r"COURSE\s+TYPE",
    "course_credit": r"COURSE\s+CREDIT",
    "prerequisites": r"PRE[-\s]*REQUISITES?",
    "corequisites": r"CO[-\s]*REQUISITES?",
}
PERIOD_HEADING = re.compile(r"Learning Outcomes for\s+(.+?)\s+Period", re.IGNORECASE)


def clean(text):
    """Join layout whitespace; retain source wording, punctuation and spelling."""
    return re.sub(r"\s+", " ", text or "").strip()


def section(text, start, end):
    match = re.search(
        rf"^\s*{start}\s*:\s*(.*?)(?=^\s*{end}\s*:)",
        text, re.IGNORECASE | re.MULTILINE | re.DOTALL,
    )
    return match.group(1) if match else ""


def outcomes(text, prefix):
    """Parse numbered outcomes without treating the next column as continuation."""
    pattern = re.compile(rf"^\s*({prefix}\s*\d+)\s*[.:)\-]\s*", re.IGNORECASE | re.MULTILINE)
    matches = list(pattern.finditer(text))
    return [
        {"id": re.sub(r"\s+", "", match.group(1)).upper(),
         "text": clean(text[match.end():matches[index + 1].start() if index + 1 < len(matches) else len(text)])}
        for index, match in enumerate(matches)
    ]


def learning_plan(pdf):
    """Read only two-column overview tables and matching next-page continuations."""
    periods = []
    pending = None
    for page in pdf.pages:
        headings = page.search(PERIOD_HEADING) or []
        previous, pending = pending, None
        if not headings and previous is None:
            continue
        for table in sorted(page.find_tables(), key=lambda item: item.bbox[1]):
            rows = table.extract()
            if not rows or any(len(row) != 2 for row in rows):
                continue
            header = [clean(cell).casefold() for cell in rows[0]]
            if header == ["course learning outcomes", "topic learning outcomes"]:
                above = [heading for heading in headings if heading["bottom"] <= table.bbox[1]]
                if not above:
                    continue
                heading = max(above, key=lambda item: item["bottom"])
                period = {
                    "period": clean(heading["groups"][0]),
                    "course_learning_outcomes": [], "topic_learning_outcomes": [],
                    "additional_text": [], "source_pages": [],
                }
                periods.append(period)
                body = rows[1:]
            elif previous is not None:
                prior_period, prior_bbox = previous
                # Same table width and an outcome at the top of the next page.
                if (table.bbox[1] > 120
                        or abs(table.bbox[0] - prior_bbox[0]) > 5
                        or abs(table.bbox[2] - prior_bbox[2]) > 5
                        or not any(re.match(r"\s*(CLO|TLO)\s*\d+\s*[.:)]", cell or "", re.I)
                                   for cell in rows[0])):
                    continue
                period, body = prior_period, rows
                previous = None
            else:
                continue

            left = "\n".join(row[0] or "" for row in body)
            right = "\n".join(row[1] or "" for row in body)
            right_parts = re.split(r"(?m)^\s*[•●]\s*", right)
            period["course_learning_outcomes"].extend(outcomes(left, "CLO"))
            period["topic_learning_outcomes"].extend(outcomes(right_parts[0], "TLO"))
            period["additional_text"].extend(clean(part) for part in right_parts[1:] if clean(part))
            period["source_pages"].append(page.page_number)
            if page.height - table.bbox[3] < 40:
                pending = period, table.bbox
    return periods


def extract_syllabus(path):
    record = {"source": {
        "filename": path.name,
        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "extractor_version": EXTRACTOR_VERSION,
        "pdfplumber_version": pdfplumber.__version__,
    }}
    with pdfplumber.open(path) as pdf:
        texts = [page.extract_text() or "" for page in pdf.pages]
        text = "\n".join(texts)
        record["source"]["page_count"] = len(pdf.pages)
        for field, label in LABELS.items():
            match = re.search(rf"^\s*{label}\s*:[ \t]*([^\n]*)", text, re.I | re.M)
            record[field] = (clean(match.group(1)) or None) if match else None
        record["course_description"] = clean(section(text, r"COURSE\s+DESCRIPTION", r"COURSE\s+LEARNING\s+OUTCOMES")) or None
        clo_text = section(text, r"COURSE\s+LEARNING\s+OUTCOMES", r"LEARNING\s+PLAN")
        record["course_learning_outcomes"] = outcomes(clo_text, "CLO")
        record["learning_plan"] = learning_plan(pdf)
        # Small section-level references; original PDFs remain the evidence.
        plan_start = next((i for i, value in enumerate(texts)
                           if re.search(r"LEARNING\s+PLAN\s*:", value, re.I)), -1)
        record["source"]["field_pages"] = {
            **{field: [index + 1 for index, value in enumerate(texts)
                       if re.search(rf"^\s*{label}\s*:", value, re.I | re.M)]
               for field, label in LABELS.items()},
            "course_description": [index + 1 for index, value in enumerate(texts)
                                   if re.search(r"COURSE\s+DESCRIPTION\s*:", value, re.I)],
            "course_learning_outcomes": [index + 1 for index, value in enumerate(texts)
                                         if index <= plan_start
                                         and re.search(r"^\s*CLO\s*\d+\s*[.:)]",
                                                       re.split(r"LEARNING\s+PLAN\s*:", value, flags=re.I)[0], re.I | re.M)],
        }

    issues = []
    for field in [*LABELS, "course_description", "course_learning_outcomes", "learning_plan"]:
        if not record[field]:
            issues.append(f"Missing or unrecognized: {field}")
    lists = [("course_learning_outcomes", record["course_learning_outcomes"])]
    known_clos = {outcome["id"] for outcome in record["course_learning_outcomes"]}
    for period in record["learning_plan"]:
        for field in ["course_learning_outcomes", "topic_learning_outcomes"]:
            name = f"{period['period']}.{field}"
            if not period[field]:
                issues.append(f"Missing or unrecognized: {name}")
            lists.append((name, period[field]))
        if any(outcome["id"] not in known_clos for outcome in period["course_learning_outcomes"]):
            issues.append(f"{period['period']}: learning-plan CLO not found in main CLO list")
    for name, values in lists:
        ids = [value["id"] for value in values]
        if len(ids) != len(set(ids)):
            issues.append(f"Duplicate outcome identifiers: {name}")
        if any(not value["text"] for value in values):
            issues.append(f"Empty outcome text: {name}")
    heading_count = len(PERIOD_HEADING.findall(text))
    if heading_count != len(record["learning_plan"]):
        issues.append("Some period headings do not have a recognized learning-plan table")
    record.update(status="needs_review" if issues else "ok", issues=issues)
    return record


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="One PDF or a folder of syllabus PDFs")
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    source = args.input.resolve()
    if source.is_file() and source.suffix.lower() == ".pdf":
        files, base = [source], source.parent
    elif source.is_dir():
        files, base = sorted(p for p in source.rglob("*") if p.is_file() and p.suffix.lower() == ".pdf"), source
    else:
        parser.error("Input must be an existing PDF file or folder")
    if not files:
        parser.error("No PDF files found")
    counts = {"ok": 0, "needs_review": 0, "failed": 0}
    summary = []
    # Appending .json also keeps a source named summary.pdf away from summary.json.
    for path in files:
        relative = path.relative_to(base)
        output_relative = relative.with_suffix(relative.suffix + ".json")
        destination = args.output / output_relative
        try:
            record = extract_syllabus(path)
        except Exception as error:
            # Isolate unreadable/encrypted/unexpected files; continue the batch.
            record = {"source": {"filename": path.name}, "status": "failed",
                      "error": f"{type(error).__name__}: {error}"}
        write_json(destination, record)
        counts[record["status"]] += 1
        summary.append({"input": relative.as_posix(), "output": output_relative.as_posix(),
                        "status": record["status"]})
        print(f"{record['status']}: {relative.as_posix()}")
    write_json(args.output / "summary.json", {"counts": counts, "files": summary})
    print(json.dumps(counts))
    return 1 if counts["needs_review"] or counts["failed"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
