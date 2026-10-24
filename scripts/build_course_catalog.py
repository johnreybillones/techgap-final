"""Build clean course catalog & relationship graph (data/syllabi/course_catalog.json)
and slim down data/syllabi/summary.json to remove redundant data duplication.
"""

import json
from pathlib import Path
import re


def clean_code(raw: str) -> str:
    """Normalize raw course code into canonical format (e.g. 'S-ITCS123')."""
    if not raw:
        return ""
    code = raw.strip()
    # Normalize unicode hyphens/dashes
    code = re.sub(r"[\u2010-\u2015\u2212\ufe58\ufe63\uff0d]", "-", code)
    # Remove spaces around hyphens and within code
    code = re.sub(r"\s+", "", code)
    # Ensure S- or G- prefix format
    code = re.sub(r"^[sS][\-_]?", "S-", code)
    code = re.sub(r"^[gG][\-_]?", "G-", code)
    if not code.startswith("S-") and not code.startswith("G-"):
        code = f"S-{code}"
    # Standardize casing: prefix and dept uppercase
    parts = code.split("-", 1)
    if len(parts) == 2:
        return f"{parts[0].upper()}-{parts[1].upper()}"
    return code.upper()


def parse_requisite_codes(text: str) -> list[str]:
    """Extract individual normalized course codes from freeform requisite text."""
    if not text or text.strip().lower() in ("none", "n/a", ""):
        return []

    # Normalize dashes and replace separators with commas
    t = re.sub(r"[\u2010-\u2015\u2212\ufe58\ufe63\uff0d]", "-", text)
    t = t.replace("&", ",").replace(" and ", ",").replace(" AND ", ",")
    t = t.replace("/", ",").replace(";", ",")

    found = []
    # Match patterns like S-ITCS111, G-COMP001LA, ITCS123, CSPC212
    matches = re.findall(r"\b(?:[SG]\s*[\-_]\s*)?[A-Za-z]{2,6}\s*\d{3}[A-Za-z0-9]*\b", t)
    for m in matches:
        norm = clean_code(m)
        if norm and norm not in found:
            found.append(norm)

    return found


def build_catalog(syllabi_dir: Path):
    summary_path = syllabi_dir / "summary.json"
    with open(summary_path, encoding="utf-8") as f:
        summary_data = json.load(f)

    courses = {}
    tracks = {}
    year_levels = {}

    for item in summary_data["files"]:
        out_path = syllabi_dir / item["output"]
        if not out_path.exists():
            continue

        with open(out_path, encoding="utf-8") as jf:
            cdata = json.load(jf)

        raw_code = cdata.get("course_code") or item.get("course_code") or ""
        code = clean_code(raw_code)
        if not code:
            continue

        raw_prereq = cdata.get("prerequisites") or item.get("prerequisites") or ""
        raw_coreq = cdata.get("corequisites") or item.get("corequisites") or ""
        track = cdata.get("track") or item.get("track") or "Unassigned"
        year = cdata.get("year_level") or item.get("year_level") or "Unassigned"
        semester = cdata.get("semester") or item.get("semester") or "Unassigned"
        title = cdata.get("course_title") or item.get("course_title") or ""
        course_type = cdata.get("course_type", "")
        credits = cdata.get("course_credit", "")
        desc = cdata.get("course_description", "")
        clos = cdata.get("course_learning_outcomes", [])

        prereq_list = parse_requisite_codes(raw_prereq)
        coreq_list = parse_requisite_codes(raw_coreq)

        # Learning plan summary
        lp = cdata.get("learning_plan", [])
        period_topics = {}
        for p in lp:
            p_name = p.get("period", "")
            tlos = [t.get("text", "") for t in p.get("topic_learning_outcomes", []) if t.get("text")]
            if p_name:
                period_topics[p_name] = tlos

        # If course already recorded (e.g. duplicate syllabus copy or pairing), aggregate
        if code not in courses:
            courses[code] = {
                "course_code": code,
                "course_title": title,
                "course_type": course_type,
                "course_credit": credits,
                "track": track,
                "year_level": year,
                "semester": semester,
                "prerequisites": {
                    "raw": raw_prereq,
                    "codes": prereq_list,
                },
                "corequisites": {
                    "raw": raw_coreq,
                    "codes": coreq_list,
                },
                "course_description": desc,
                "learning_outcomes": [c.get("text") for c in clos if c.get("text")],
                "topics": period_topics,
                "syllabus_files": [item["output"]],
            }
        else:
            # Merge files
            if item["output"] not in courses[code]["syllabus_files"]:
                courses[code]["syllabus_files"].append(item["output"])
            # Fill missing
            if not courses[code]["course_description"] and desc:
                courses[code]["course_description"] = desc
            if not courses[code]["learning_outcomes"] and clos:
                courses[code]["learning_outcomes"] = [c.get("text") for c in clos if c.get("text")]
            for p_name, t_list in period_topics.items():
                if p_name not in courses[code]["topics"] or not courses[code]["topics"][p_name]:
                    courses[code]["topics"][p_name] = t_list

        # Track aggregation
        if track not in tracks:
            tracks[track] = []
        if code not in tracks[track]:
            tracks[track].append(code)

        # Year aggregation
        if year not in year_levels:
            year_levels[year] = []
        if code not in year_levels[year]:
            year_levels[year].append(code)

    catalog = {
        "metadata": {
            "total_courses": len(courses),
            "total_syllabus_files": len(summary_data["files"]),
            "tracks": list(tracks.keys()),
            "year_levels": list(year_levels.keys()),
        },
        "tracks": tracks,
        "year_levels": year_levels,
        "courses": courses,
    }

    # Write course_catalog.json
    catalog_path = syllabi_dir / "course_catalog.json"
    with open(catalog_path, "w", encoding="utf-8") as f:
        json.dump(catalog, f, indent=2, ensure_ascii=False)
    print(f"Created {catalog_path} with {len(courses)} unique courses.")

    # Slim down summary.json:
    # 1. counts
    # 2. by_year: { Year: { total, ok, needs_review, failed, course_codes: [...] } }
    # 3. by_track: { Track: { total, ok, needs_review, failed, course_codes: [...] } }
    # 4. files: [ { input, output, course_code, status } ] (lightweight, no nested duplicated full objects!)
    slim_by_year = {}
    if "by_year" in summary_data:
        for y, ydata in summary_data["by_year"].items():
            slim_by_year[y] = {
                "total": ydata.get("total", 0),
                "ok": ydata.get("ok", 0),
                "needs_review": ydata.get("needs_review", 0),
                "failed": ydata.get("failed", 0),
                "course_codes": year_levels.get(y, []),
            }

    slim_by_track = {}
    if "by_track" in summary_data:
        for t, tdata in summary_data["by_track"].items():
            slim_by_track[t] = {
                "total": tdata.get("total", 0),
                "ok": tdata.get("ok", 0),
                "needs_review": tdata.get("needs_review", 0),
                "failed": tdata.get("failed", 0),
                "course_codes": tracks.get(t, []),
            }

    slim_files = []
    for f in summary_data["files"]:
        slim_files.append({
            "course_code": clean_code(f.get("course_code", "")),
            "course_title": f.get("course_title", ""),
            "input": f.get("input", ""),
            "output": f.get("output", ""),
            "status": f.get("status", "ok"),
        })

    slim_summary = {
        "counts": summary_data["counts"],
        "by_year": slim_by_year,
        "by_track": slim_by_track,
        "files": slim_files,
    }

    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(slim_summary, f, indent=2, ensure_ascii=False)
    print(f"Slimmed down {summary_path} from 4000+ lines to {len(slim_files) * 7 + 50} lines.")


if __name__ == "__main__":
    build_catalog(Path("data/syllabi"))
