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


EXTRACTOR_VERSION = "dlsud-cics-v2"
LABELS = {
    "course_code": r"COURSE\s+CODE",
    "course_title": r"COURSE\s+TITLE",
    "course_type": r"COURSE\s+TYPE",
    "course_credit": r"COURSE\s+CREDIT",
    "prerequisites": r"PRE[-\s]*REQUISITES?",
    "corequisites": r"CO[-\s]*REQUISITES?",
}
PERIOD_HEADING = re.compile(
    r"(?:Learning\s+(?:Outcomes|Plan)\s+for\s+(?:the\s+)?|(?:LEARNING\s+PLAN\s+FOR\s+)?)(Midterm|Final)\s+Period\s*:?",
    re.IGNORECASE,
)


def clean(text):
    """Join layout whitespace; retain source wording, punctuation and spelling."""
    return re.sub(r"\s+", " ", text or "").strip()


def section(text, start, end):
    match = re.search(
        rf"^\s*(?:[IVXLCDM]+\.\s*)?{start}\s*:?\s*(.*?)(?=^\s*(?:[IVXLCDM]+\.\s*)?{end}\s*:?)",
        text, re.IGNORECASE | re.MULTILINE | re.DOTALL,
    )
    return match.group(1) if match else ""


def outcomes(text, prefix):
    """Parse numbered outcomes without treating the next column as continuation."""
    pat_str = r"(?:CL[O0]|CL\s*[O0])" if prefix == "CLO" else r"(?:TL[O0]|TL\s*[O0])"
    pattern = re.compile(rf"^\s*[•●\u2022\uf0b7\-\*]?\s*({pat_str}\s*\d+)\s*[.:)\-]\s*", re.IGNORECASE | re.MULTILINE)
    matches = list(pattern.finditer(text))
    return [
        {"id": re.sub(r"\s+", "", match.group(1)).upper().replace("CL0", "CLO").replace("TL0", "TLO"),
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
            if len(header) == 2 and "course learning outcome" in header[0] and "topic learning outcome" in header[1]:
                above = [heading for heading in headings if heading["bottom"] <= table.bbox[1]]
                if not above:
                    continue
                heading = max(above, key=lambda item: item["bottom"])
                period_name = clean(heading["groups"][0]).capitalize()
                period = {
                    "period": period_name,
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
                        or not any(re.match(r"\s*[•●\u2022\uf0b7\-\*]?\s*(CL[O0]|TL[O0])\s*\d+\s*[.:)]", cell or "", re.I)
                                   for cell in rows[0])):
                    continue
                period, body = prior_period, rows
                previous = None
            else:
                continue

            left = "\n".join(row[0] or "" for row in body)
            right = "\n".join(row[1] or "" for row in body)
            right_parts = re.split(r"(?m)^\s*[•●\u2022\uf0b7]\s*", right)
            period["course_learning_outcomes"].extend(outcomes(left, "CLO"))
            period["topic_learning_outcomes"].extend(outcomes(right, "TLO"))
            for part in right_parts[1:]:
                cleaned_part = clean(part)
                if cleaned_part and not re.match(r"^(?:TL[O0]|CL[O0])\s*\d+", cleaned_part, re.I):
                    period["additional_text"].append(cleaned_part)
            period["source_pages"].append(page.page_number)
            if page.height - table.bbox[3] < 40:
                pending = period, table.bbox
    return periods


def classify_track(code: str) -> str:
    cleaned = re.sub(r"[^A-Z0-9]", "", (code or "").upper())
    if "CSGD" in cleaned:
        return "CS - Game Development"
    if "CSIS" in cleaned:
        return "CS - Intelligent Systems"
    if "ITWB" in cleaned:
        return "IT - Web Development"
    if "ITNT" in cleaned:
        return "IT - Network Technology"
    if "ITCS" in cleaned:
        return "Common (IT & CS)"
    if any(k in cleaned for k in ("CSPC", "CSSE", "CSPE", "CSTH")) or "CS" in cleaned:
        return "CS Core & Electives"
    if any(k in cleaned for k in ("ITPC", "ITPE", "ITCP")) or "IT" in cleaned:
        return "IT Core & Electives"
    if cleaned.startswith("G") or "COMP" in cleaned or "MATH" in cleaned:
        return "General & Foundational"
    return "Unassigned"


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
            match = re.search(rf"^\s*{label}\s*:[ \t]*([^\n]*(?:\n[ \t]{{2,}}[^\n]+)*)", text, re.I | re.M)
            if match:
                val = clean(match.group(1))
                if not val and field in ("prerequisites", "corequisites"):
                    val = "None"
                record[field] = val or None
            else:
                record[field] = None
        record["track"] = classify_track(record.get("course_code"))
        record["course_description"] = clean(section(text, r"COURSE\s+DESCRIPTION", r"COURSE\s+LEARNING\s+OUTCOMES")) or None
        clo_text = section(text, r"COURSE\s+LEARNING\s+OUTCOMES", r"LEARNING\s+PLAN")
        record["course_learning_outcomes"] = outcomes(clo_text, "CLO")
        record["learning_plan"] = learning_plan(pdf)
        # Small section-level references; original PDFs remain the evidence.
        plan_start = next((i for i, value in enumerate(texts)
                           if re.search(r"LEARNING\s+PLAN\s*:?", value, re.I)), -1)
        record["source"]["field_pages"] = {
            **{field: [index + 1 for index, value in enumerate(texts)
                       if re.search(rf"^\s*{label}\s*:", value, re.I | re.M)]
               for field, label in LABELS.items()},
            "course_description": [index + 1 for index, value in enumerate(texts)
                                   if re.search(r"COURSE\s+DESCRIPTION\s*:?", value, re.I)],
            "course_learning_outcomes": [index + 1 for index, value in enumerate(texts)
                                         if index <= plan_start
                                         and re.search(r"^\s*[•●\u2022\uf0b7\-\*]?\s*CL[O0]\s*\d+\s*[.:)]",
                                                       re.split(r"LEARNING\s+PLAN\s*:?", value, flags=re.I)[0], re.I | re.M)],
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
    found_periods = set(h.capitalize() for h in PERIOD_HEADING.findall(text) if h.capitalize() in ("Midterm", "Final"))
    plan_periods = set(p["period"] for p in record["learning_plan"])
    missing_periods = found_periods - plan_periods
    if missing_periods:
        issues.append(f"Missing recognized learning-plan table for period(s): {', '.join(sorted(missing_periods))}")
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
    by_track = {}
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
        track = record.get("track", "Unassigned")
        if track not in by_track:
            by_track[track] = {"total": 0, "ok": 0, "needs_review": 0, "failed": 0, "files": []}
        by_track[track]["total"] += 1
        by_track[track][record["status"]] += 1
        by_track[track]["files"].append({
            "course_code": record.get("course_code"),
            "course_title": record.get("course_title"),
            "status": record["status"],
            "output": output_relative.as_posix(),
        })
        summary.append({"input": relative.as_posix(), "output": output_relative.as_posix(),
                        "track": track, "status": record["status"]})
        print(f"{record['status']} [{track}]: {relative.as_posix()}")
    write_json(args.output / "summary.json", {"counts": counts, "by_track": by_track, "files": summary})
    print(json.dumps(counts))
    return 1 if counts["needs_review"] or counts["failed"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
