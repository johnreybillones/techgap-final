"""Resolve and repair syllabus JSON files flagged as 'needs_review'.

This script operates as a dedicated post-processor for edge cases, keeping
the primary extract_syllabi.py clean and focused on standard layouts.

Repairs Handled:
1. 3-Column Tables: Merges split TLO columns [CLO, TLO ID, TLO Text] into standard CLO/TLO structures.
2. Orphaned Table Headers: Reconnects header-only tables at the bottom of a page to their body on the next page.
3. Missing Header Fallbacks: Recovers course title from the PDF filename and defaults omitted prerequisites/corequisites to "None".
4. Duplicate Outcome IDs: Renumbers accidentally duplicated CLO/TLO identifiers sequentially.
5. Thesis / Capstone Courses: Handles research/capstone syllabi that naturally omit standard 2-column lecture plan tables.

Usage:
    python scripts/resolve_review_syllabi.py [--dry-run]
"""

import argparse
import json
from pathlib import Path
import re
import pdfplumber

EXTRACTOR_VERSION = "dlsud-cics-v2-repaired"
PERIOD_HEADING = re.compile(
    r"(?:Learning\s+(?:Outcomes|Plan)\s+for\s+(?:the\s+)?|(?:LEARNING\s+PLAN\s+FOR\s+)?)(Midterm|Final)\s+Period\s*:?",
    re.IGNORECASE,
)


def clean(text):
    return re.sub(r"\s+", " ", text or "").strip()


def outcomes(text, prefix):
    pat_str = r"(?:CL[O0]|CL\s*[O0])" if prefix == "CLO" else r"(?:TL[O0]|TL\s*[O0])"
    pattern = re.compile(rf"^\s*[•●\u2022\uf0b7\-\*]?\s*({pat_str}\s*\d+)\s*[.:)\-]\s*", re.IGNORECASE | re.MULTILINE)
    matches = list(pattern.finditer(text))
    return [
        {"id": re.sub(r"\s+", "", match.group(1)).upper().replace("CL0", "CLO").replace("TL0", "TLO"),
         "text": clean(text[match.end():matches[index + 1].start() if index + 1 < len(matches) else len(text)])}
        for index, match in enumerate(matches)
    ]


def parse_learning_plan_extended(pdf):
    """Parse learning plan supporting 2-column, 3-column split, and orphaned header continuations."""
    periods = []
    pending = None

    for page in pdf.pages:
        headings = page.search(PERIOD_HEADING) or []
        previous, pending = pending, None
        tables = sorted(page.find_tables(), key=lambda t: t.bbox[1])

        for table in tables:
            rows = table.extract()
            if not rows:
                continue

            # Case A: Matching next-page continuation of a previous table
            if previous is not None:
                prior_period, prior_bbox = previous
                # Check if first row contains outcome identifiers
                first_cell_joined = " ".join(clean(c) for c in rows[0] if c)
                if re.search(r"\b(?:CL[O0]|TL[O0])\s*\d+", first_cell_joined, re.I):
                    period = prior_period
                    body = rows
                    previous = None
                else:
                    body = []
            else:
                body = []

            # Case B: Standard or 3-column Overview Header
            if not body:
                header = [clean(c).casefold() for c in rows[0] if c]
                is_overview = (
                    len(header) >= 2
                    and "course learning outcome" in header[0]
                    and "topic learning outcome" in header[1]
                )
                if not is_overview:
                    continue

                above = [h for h in headings if h["bottom"] <= table.bbox[1]]
                if not above and not headings:
                    continue
                heading = max(above, key=lambda h: h["bottom"]) if above else headings[0]
                period_name = clean(heading["groups"][0]).capitalize()

                period = {
                    "period": period_name,
                    "course_learning_outcomes": [],
                    "topic_learning_outcomes": [],
                    "additional_text": [],
                    "source_pages": [],
                }
                periods.append(period)
                body = rows[1:]

            if not body:
                # If table only had the header row, it continues on the next page
                pending = period, table.bbox
                continue

            # Process body rows (2-column or 3-column)
            left_cells = []
            right_cells = []
            for row in body:
                left_cells.append(row[0] or "")
                if len(row) == 2:
                    right_cells.append(row[1] or "")
                elif len(row) >= 3:
                    # Merge TLO number in col 1 and description in col 2
                    tlo_id = clean(row[1])
                    tlo_desc = clean(row[2])
                    if tlo_id and tlo_desc:
                        right_cells.append(f"{tlo_id}. {tlo_desc}")
                    elif tlo_desc:
                        right_cells.append(tlo_desc)
                    elif tlo_id:
                        right_cells.append(tlo_id)

            left_text = "\n".join(left_cells)
            right_text = "\n".join(right_cells)
            period["course_learning_outcomes"].extend(outcomes(left_text, "CLO"))
            period["topic_learning_outcomes"].extend(outcomes(right_text, "TLO"))

            # Capture additional outcome text
            right_parts = re.split(r"(?m)^\s*[•●\u2022\uf0b7]\s*", right_text)
            for part in right_parts[1:]:
                cleaned_part = clean(part)
                if cleaned_part and not re.match(r"^(?:TL[O0]|CL[O0])\s*\d+", cleaned_part, re.I):
                    period["additional_text"].append(cleaned_part)

            if page.page_number not in period["source_pages"]:
                period["source_pages"].append(page.page_number)

            # Check if this table was near the bottom and continues
            if page.height - table.bbox[3] < 90:
                pending = period, table.bbox

    return periods


def fix_duplicate_ids(outcome_list, prefix):
    """Renumber accidentally duplicated outcome identifiers sequentially."""
    ids = [item["id"] for item in outcome_list]
    if len(ids) == len(set(ids)):
        return outcome_list, False

    fixed = []
    for idx, item in enumerate(outcome_list):
        expected_id = f"{prefix}{idx + 1}"
        fixed.append({"id": expected_id, "text": item["text"]})
    return fixed, True


def deduce_title_from_filename(filename):
    """Extract clean title from standard DLSU-D CICS syllabus filenames."""
    name = Path(filename).stem
    # Match patterns like: S-ITWB311 Web Development Lec
    match = re.search(r"^(?:[A-Z0-9_\-]+)\s+(.+?)(?:\s+(?:Lec|Lab|Lecture|Laboratory|\(2\)))?$", name, re.I)
    return match.group(1).strip() if match else name


def validate_record(record, pdf_text):
    """Validate repaired record against standard rules."""
    labels = ["course_code", "course_title", "course_type", "course_credit", "prerequisites", "corequisites"]
    issues = []

    # Check basic fields
    for field in [*labels, "course_description", "course_learning_outcomes"]:
        if not record.get(field):
            issues.append(f"Missing or unrecognized: {field}")

    # Check learning plan
    is_thesis_or_capstone = any(
        kw in (record.get("course_title") or "").upper() or kw in (record.get("course_code") or "").upper()
        for kw in ("THESIS", "CAPSTONE", "PRACTICUM", "OJT")
    )

    if not record.get("learning_plan"):
        if is_thesis_or_capstone:
            record["notes"] = "Exempted from periodic lecture table requirement (Research/Capstone/Practicum course)."
        else:
            issues.append("Missing or unrecognized: learning_plan")
    else:
        known_clos = {outcome["id"] for outcome in record["course_learning_outcomes"]}
        for period in record["learning_plan"]:
            for field in ["course_learning_outcomes", "topic_learning_outcomes"]:
                name = f"{period['period']}.{field}"
                if not period[field]:
                    issues.append(f"Missing or unrecognized: {name}")
            if any(outcome["id"] not in known_clos for outcome in period["course_learning_outcomes"]):
                issues.append(f"{period['period']}: learning-plan CLO not found in main CLO list")

    return issues


def repair_file(json_path: Path, pdf_path: Path, dry_run: bool = False):
    with open(json_path, encoding="utf-8") as f:
        data = json.load(f)

    if data.get("status") == "ok":
        return None

    changes = []
    text_content = ""

    # Open PDF for deep extraction if needed
    if pdf_path.exists():
        with pdfplumber.open(pdf_path) as pdf:
            text_content = "\n".join(p.extract_text() or "" for p in pdf.pages)

            # Repair A: Re-parse Learning Plan with extended 3-col & orphan bridging
            if not data.get("learning_plan") or any("topic_learning_outcomes" in i for i in data.get("issues", [])):
                repaired_plan = parse_learning_plan_extended(pdf)
                if repaired_plan:
                    data["learning_plan"] = repaired_plan
                    changes.append("Repaired learning_plan tables (3-col / orphan bridge)")

    # Repair B: Header Fallbacks
    if not data.get("course_title"):
        deduced = deduce_title_from_filename(data["source"]["filename"])
        if deduced:
            data["course_title"] = deduced
            changes.append(f"Deduced course_title: '{deduced}'")

    if not data.get("prerequisites"):
        data["prerequisites"] = "None"
        changes.append("Defaulted missing prerequisites to 'None'")

    if not data.get("corequisites"):
        data["corequisites"] = "None"
        changes.append("Defaulted missing corequisites to 'None'")

    # Repair C: Fix Duplicate Outcome IDs
    if "Duplicate outcome identifiers: course_learning_outcomes" in data.get("issues", []):
        data["course_learning_outcomes"], fixed = fix_duplicate_ids(data.get("course_learning_outcomes", []), "CLO")
        if fixed:
            changes.append("Deduplicated master course_learning_outcomes IDs")

    for period in data.get("learning_plan", []):
        period["course_learning_outcomes"], f1 = fix_duplicate_ids(period.get("course_learning_outcomes", []), "CLO")
        period["topic_learning_outcomes"], f2 = fix_duplicate_ids(period.get("topic_learning_outcomes", []), "TLO")
        if f1 or f2:
            changes.append(f"Deduplicated outcome IDs in {period['period']}")

    # Repair D: Validate and update status
    new_issues = validate_record(data, text_content)
    old_status = data["status"]
    data["issues"] = new_issues
    data["status"] = "needs_review" if new_issues else "ok"

    if data["status"] != old_status:
        changes.append(f"Status changed: {old_status} -> {data['status']}")

    if not changes:
        return None

    if not dry_run:
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    return {
        "file": json_path.name,
        "old_status": old_status,
        "new_status": data["status"],
        "changes": changes,
        "remaining_issues": new_issues,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true", help="Inspect repairs without writing to disk")
    parser.add_argument("--dir", type=Path, default=Path("data/syllabi"), help="Root directory containing extracted JSONs")
    args = parser.parse_args()

    summary_path = args.dir / "summary.json"
    if not summary_path.exists():
        parser.error(f"summary.json not found in {args.dir}")

    with open(summary_path, encoding="utf-8") as f:
        summary_data = json.load(f)

    print(f"Loaded summary: {summary_data['counts']}")
    print(f"Dry run mode: {args.dry_run}\n" + "=" * 60)

    repaired_count = 0
    promoted_to_ok = 0

    for file_entry in summary_data["files"]:
        if file_entry["status"] != "needs_review":
            continue

        json_path = args.dir / file_entry["output"]
        pdf_path = Path("docs/Syllabi") / file_entry["input"]

        result = repair_file(json_path, pdf_path, dry_run=args.dry_run)
        if result:
            repaired_count += 1
            if result["new_status"] == "ok":
                promoted_to_ok += 1
                status_symbol = "OK: PROMOTED"
            else:
                status_symbol = "INFO: PARTIALLY REPAIRED"

            print(f"[{status_symbol}] {result['file']}")
            for change in result["changes"]:
                print(f"    - {change}")
            if result["remaining_issues"]:
                print(f"    Remaining issues: {result['remaining_issues']}")
            print()

    print("=" * 60)
    print(f"Repairs applied to: {repaired_count} files")
    print(f"Promoted to 'ok':   {promoted_to_ok} files")


if __name__ == "__main__":
    main()
