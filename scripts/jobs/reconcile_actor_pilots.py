"""Reconcile the saved Shahidirfan and Blackfalcon JobStreet pilot evidence.

This command is offline and read-only with respect to its input pilot directories.
It writes a case sheet, machine report, Markdown report, and hash manifest to a
new output directory supplied by the caller.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import html
import json
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import parse_qs, urlparse

RULE_VERSION = "actor-pilot-reconciliation-v1"
FROZEN_REGISTRY_SHA256 = "ca2430a13307abe27cfdb58ecdeb948775d8c095b649fe2908cb6e40c65b9107"

# Case adjudications are ID keyed so input ordering cannot change a result.
# Evidence passages are extracted from the saved description at runtime.
ASSESSMENTS = {
    "95083491": ("yes", "yes", "required Databricks, Azure, SQL, Python and PySpark experience is specified."),
    "95060375": ("yes", "yes", "Python proficiency, SQL/noSQL and ETL experience are specified in job specifications."),
    "95082168": ("yes", "unavailable", "The saved item has no description or technical requirements."),
    "95244013": ("yes", "yes", "The description requires SQL and Python or a comparable programming language."),
    "95455079": ("yes", "yes", "The Data Scientist duties and qualifications specify machine learning, statistical modeling and programming capabilities."),
    "95460042": ("yes", "yes", "Required proficiencies include Microsoft Word, Excel and Power BI; the role also describes KPI debugging and time-series analysis duties."),
    "94964870": ("yes", "yes", "The role requires proficiency in Python, Java, Scala or SQL and database/data-warehouse capabilities."),
    "95114710": ("yes", "yes", "Qualifications require Azure DevOps, Git, CI/CD, SQL and a cloud data platform."),
    "95370509": ("yes", "yes", "The section is explicitly headed Required Technical Skills and lists Fabric, SQL, Python and PySpark."),
    "95449518": ("yes", "yes", "The qualification section specifies familiarity with SQL/databases and data visualization tools; Python or R is preferred and is not used as the sole basis."),
    "95280900": ("yes", "yes", "The role requires strong SQL, data modeling and hands-on dbt/SQLMesh or similar transformation framework experience."),
    "95078464": ("yes", "yes", "Qualifications require hands-on Snowflake/database and transformation experience plus SQL and a data programming language."),
    "94940619": ("yes", "yes", "Qualifications require SQL, a programming language and ETL/ELT, data modeling and warehousing experience."),
    "95225559": ("yes", "yes", "The role requires Azure Databricks, Spark, Python/PySpark, SQL and Microsoft Purview capabilities."),
    "95461396": ("yes", "yes", "Required qualifications specify hands-on LLM and AI/agent orchestration framework experience."),
    "95372988": ("yes", "yes", "The description requires Databricks, Apache Spark, Python, SQL and data-pipeline/ETL experience."),
}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def read_jsonl(path: Path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def canonical_hash(value) -> str:
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()


def validate_blackfalcon(bf: Path):
    validation = read_json(bf / "raw_handoff_validation.json")
    mismatches = []
    for relative, expected in validation["hashes"].items():
        path = bf / Path(relative)
        actual = sha256(path) if path.is_file() else None
        if actual != expected:
            mismatches.append({"file": relative, "expected": expected, "actual": actual})
    if mismatches:
        raise ValueError("Blackfalcon input hash mismatch: " + json.dumps(mismatches, ensure_ascii=False))
    return validation


def registry_id(row):
    sid = str(row.get("source_id") or row.get("seekJobId") or "")
    if not re.fullmatch(r"\d+", sid):
        raise ValueError("comparison registry has invalid source ID: " + repr(sid))
    return sid


def registry_ids(rows):
    ids = [registry_id(row) for row in rows]
    if len(ids) != len(set(ids)):
        raise ValueError("comparison registry contains duplicate source IDs")
    return set(ids)


def source_id_from_item(item):
    sid = str(item.get("seekJobId", "")); url = urlparse(item.get("canonicalUrl", ""))
    tail = url.path.rstrip("/").split("/")[-1]
    if not re.fullmatch(r"\d+", sid) or tail != sid or url.hostname != "ph.jobstreet.com":
        raise ValueError("numeric seekJobId does not match canonical URL: " + repr(sid))
    return sid


def classify_cohort(item, description):
    employment_type = str(item.get("employmentType") or "").strip()
    vacancy_fields = str(item.get("title") or "") + " " + employment_type
    explicit_internship = re.search(r"intern(ship)?|\bOJT\b", vacancy_fields, re.I)
    explicit_internship_in_description = re.search(r"\b(internship|OJT)\s+(position|role|program|vacancy)\b", description, re.I)
    if explicit_internship or explicit_internship_in_description:
        return "internship", "separate_cohort"
    if employment_type.casefold() in {"full time", "part time", "contract/temp"}:
        return "employment", "yes"
    return "unresolved", "unresolved"


def page_from_search_url(search_url: str, request: dict):
    """Return explicit page only when host/query/date context match the request."""
    if not search_url:
        return None
    parsed = urlparse(search_url)
    params = parse_qs(parsed.query)
    request_input = request.get("input", request)
    request_query = str(request_input.get("query", request_input.get("searchStringsArray", [""])[0])).strip().casefold()
    keyword = params.get("keywords", [""])[0].replace("+", " ").casefold()
    date_range = params.get("daterange", [""])[0]
    expected_range = str(request_input.get("dateRange", ""))
    if parsed.hostname != "ph.jobstreet.com" or keyword != request_query or not expected_range or date_range != expected_range:
        return None
    raw_page = params.get("page", [None])[0]
    return int(raw_page) if raw_page and raw_page.isdigit() else None


def clean_description(item):
    raw = item.get("description") or item.get("descriptionMarkdown") or item.get("descriptionHtml") or ""
    text = html.unescape(re.sub(r"<[^>]+>", " ", str(raw)))
    return re.sub(r"\s+", " ", text).strip()


def source_passage(description: str, assessment_id: str):
    if not description:
        return ""
    # Keep the matching source phrase compact and verbatim.
    patterns = {
        "95083491": r"Strong experience with[^.]+\.", "95060375": r"Proficiency in Python\.[^.]+\.",
        "95244013": r"Proficiency in SQL and Python[^.]+\.", "95455079": r"Programming: Expert proficiency in Python \(Numpy, Pandas, Scikit-learn, TensorFlow/Keras/PyTorch\) and/or R\.",
        "95460042": r"Strong working knowledge of Microsoft Word[^.]+\.", "94964870": r"Proficiency in at least one[^.]+\.",
        "95114710": r"Hands-on experience with Azure DevOps[^.]+\.", "95370509": r"Fabric pipelines and notebooks.{0,70}Solid SQL proficiency\.",
        "95449518": r"Familiarity with SQL[^.]+\.", "95280900": r"Strong SQL skills[^.]+\.",
        "95078464": r"Hands-on experience with Snowflake.{0,110}?(?=Proficiency in SQL)", "94940619": r"Strong proficiency in SQL and at least one programming language \(e\.g\., Python, Scala, or Java\)\.",
        "95225559": r"strong hands-on experience with Azure Databricks[^.]+\.", "95461396": r"Hands-on experience with Large Language Models[^.]+\.",
        "95372988": r"strong expertise in Databricks[^.]+\.",
    }
    match = re.search(patterns.get(assessment_id, r"(?!)"), description, re.IGNORECASE)
    if match:
        return match.group(0)[:420]
    if assessment_id == "95244013":
        match = re.search(r"Proficiency in SQL and Python[^.]*\.", description, re.I)
        return match.group(0) if match else description[:350]
    return description[:350]


def build(bf: Path, sh: Path, output: Path, request_path: Path, generated_at=None):
    bf = bf.resolve(); sh = sh.resolve(); output = output.resolve()
    if output == bf or bf in output.parents or output == sh or sh in output.parents:
        raise ValueError("output directory must be outside both original pilot directories")
    validation = validate_blackfalcon(bf)
    sh_manifest = read_json(sh / "manifest.json")
    sh_recon = read_json(sh / "final_reconciliation_2026-10-23.json")
    with (sh / "new_id_yield_audit_2026-10-23.csv").open(encoding="utf-8-sig", newline="") as stream:
        sh_audit = list(csv.DictReader(stream))
    sh_manifest_mismatches = []
    for relative, expected in sh_manifest.get("artifact_hashes", {}).items():
        path = sh / Path(relative)
        actual = sha256(path) if path.is_file() else None
        if actual != expected:
            sh_manifest_mismatches.append({"file": relative, "expected": expected, "actual": actual})
    unexpected_manifest_mismatches = [entry for entry in sh_manifest_mismatches if entry["file"] != "README.md"]
    if unexpected_manifest_mismatches:
        raise ValueError("six-query frozen manifest artifact hash mismatch: " + json.dumps(unexpected_manifest_mismatches, ensure_ascii=False))
    sh_registry_path = sh / "comparison_registry_2026-10-23.jsonl"
    sh_registry = read_jsonl(sh_registry_path)
    expected_registry_hash = FROZEN_REGISTRY_SHA256
    if sha256(sh_registry_path) != expected_registry_hash or sh_manifest.get("artifact_hashes", {}).get("comparison_registry_2026-10-23.jsonl") != expected_registry_hash:
        raise ValueError("six-query comparison registry hash does not match frozen 467-ID frame")
    saved_set = registry_ids(sh_registry)
    if len(saved_set) != 467:
        raise ValueError("frozen comparison registry must contain 467 unique numeric IDs")
    raw_items = read_json(bf / "raw_items.json")
    observations = read_jsonl(bf / "observations.jsonl")
    versions = read_jsonl(bf / "versions.jsonl")
    audits = {str(row["seekJobId"]): row for row in read_json(bf / "source_audit.json")}
    request_path = request_path.resolve()
    request = read_json(request_path)
    request_input = request.get("input", {})
    run_final = read_json(bf / "run_final.json")
    old_yield = read_json(bf / "yield_report.json")
    if request.get("actor_id") != run_final.get("actId") or request.get("build_id") != run_final.get("buildId"):
        raise ValueError("saved exact request actor/build does not match completed run metadata")
    if request_input.get("maxPages") != 2 or request_input.get("maxResults") != 50 or request_input.get("country") != "PH":
        raise ValueError("saved exact request does not match the bounded two-page, 50-result PH contract")
    if request.get("request_body_sha256") is None:
        raise ValueError("saved exact request is missing its body hash")
    run_window = old_yield.get("window", {})
    if request_input.get("fromDate") != run_window.get("fromDate") or request_input.get("toDate") != run_window.get("toDate"):
        raise ValueError("saved exact request UTC window does not match the saved yield-report window")
    started = datetime.fromisoformat(run_final["startedAt"].replace("Z", "+00:00"))
    window_start = datetime.fromisoformat(request_input["fromDate"].replace("Z", "+00:00"))
    window_end = datetime.fromisoformat(request_input["toDate"].replace("Z", "+00:00"))
    launch_lag_seconds = (started - window_end).total_seconds()
    if started < window_start or launch_lag_seconds > 300:
        raise ValueError("completed run start is outside the saved window or more than five minutes after its frozen end")
    actual_options = run_final.get("options", {})
    requested_options = request.get("run_options", {})
    run_option_matches = {
        "build": actual_options.get("build") == requested_options.get("build"),
        "maxTotalChargeUsd": actual_options.get("maxTotalChargeUsd") == requested_options.get("maxTotalChargeUsd"),
        "restartOnError": actual_options.get("restartOnError") == requested_options.get("restartOnError"),
        "timeout": actual_options.get("timeoutSecs") == requested_options.get("timeout"),
        "memory": actual_options.get("memoryMbytes") == requested_options.get("memory"),
    }
    if len(raw_items) != 50 or len(observations) != 50 or len(versions) != 50:
        raise ValueError("expected 50 raw items, observations, and versions")
    ids = []
    raw_by_id = {}
    for item in raw_items:
        sid = source_id_from_item(item)
        ids.append(sid); raw_by_id[sid] = item
    if len(ids) != 50 or len(set(ids)) != 50:
        raise ValueError("expected 50 unique numeric seekJobId values")
    new_ids = sorted(set(ids) - saved_set)
    if len(set(ids) & saved_set) != 34 or len(new_ids) != 16:
        raise ValueError("Blackfalcon must join to exactly 34 saved and 16 new IDs")
    if len(saved_set | set(ids)) != 483:
        raise ValueError("combined registry union must contain 483 unique IDs")
    if set(new_ids) != set(ASSESSMENTS):
        raise ValueError("assessment map does not cover exact new ID set")

    cases = []
    for sid in new_ids:
        item = raw_by_id[sid]; audit = audits.get(sid, {}); desc = clean_description(item)
        raw_payload_hash = canonical_hash(item)
        url = item.get("canonicalUrl", "")
        loc_country = str(item.get("locationCountry") or "").upper()
        desc_lower = desc.casefold()
        remote_ph = bool(re.search(r"remote.{0,35}(?:open to|eligible|applicants in) (?:the )?philippines|(?:open to|eligible for) (?:applicants in )?the philippines.{0,35}remote", desc_lower))
        phil = "eligible" if loc_country == "PH" or remote_ph else "unresolved"
        employment_type = str(item.get("employmentType") or "").strip()
        cohort, employment = classify_cohort(item, desc)
        relevant, technical, reason = ASSESSMENTS[sid]
        page = page_from_search_url(item.get("searchUrl", ""), request)
        text_excerpt = source_passage(desc, sid) if technical == "yes" else ""
        if sid == "95460042":
            relevance_reason = "The title names data analytics; duties specify KPI validation, debugging, time-series analysis and Power BI reporting, resolving the support-title ambiguity."
        elif sid in {"95455079", "95461396"}:
            relevance_reason = "The title and duties identify data science/AI development work in computing; a curated-role link is not required and query membership was not used as evidence."
        else:
            relevance_reason = "The advertised title '%s' clearly identifies data, analytics, engineering, or AI computing work; query membership was not used as a role assignment." % item.get("title", "")
        case = {
            "source_id": sid, "posting_key": "jobstreet:ph:" + sid,
            "raw_pointer": "raw_items.json#/" + str(ids.index(sid)), "raw_item_sha256": raw_payload_hash,
            "canonicalUrl": url, "title": item.get("title", ""), "company": item.get("company", ""),
            "location": item.get("location", ""), "locationCountry": item.get("locationCountry"),
            "philippine_scope": phil, "employmentType": employment_type, "cohort": cohort,
            "employment": employment, "postedDate": item.get("postedDate"), "capturedAt": item.get("scrapedAt"),
            "description_chars": int(item.get("descriptionLength") or len(desc)), "description_quality": "missing" if not desc else item.get("contentQuality", "available"),
            "duty_requirement_passage": text_excerpt, "searchUrl": item.get("searchUrl", ""), "page": page,
            "relevant_computing_employment": relevant,
            "technical_assessability": technical,
            "adjudication_reason": reason,
            "decision_reasons": {
                "philippine_scope": "locationCountry=PH in the saved raw item." if loc_country == "PH" else ("Description explicitly supports remote eligibility for Philippine applicants." if remote_ph else "No locationCountry=PH or explicit Philippine remote eligibility evidence."),
                "employment_cohort": ("Advertised title/work type explicitly identifies an internship or OJT vacancy." if cohort == "internship" else ("Saved employmentType is %s; no internship/OJT vacancy is advertised." % employment_type if employment == "yes" else "Saved work type does not establish employment.")),
                "computing_relevance": relevance_reason,
                "technical_assessability": reason,
            },
            "prior_source_audit": {k: audit.get(k) for k in ("philippine_eligibility", "employment_status", "technical_assessability", "role_link", "description_quality")},
            "prior_yield_report": None,
            "observation_pointer": "observations.jsonl#jobstreet:ph:" + sid,
            "version_pointer": "versions.jsonl#jobstreet:ph:" + sid,
        }
        cases.append(case)
    # Attach prior conflicting yield flags keyed by ID.
    for old in old_yield.get("new_rows", []):
        case = next((c for c in cases if c["source_id"] == str(old.get("seekJobId"))), None)
        if case is not None:
            case["prior_yield_report"] = {k: old.get(k) for k in ("philippine_eligibility", "employment_status", "technical_assessability", "source_audited_usable")}

    counts = Counter({name: 0 for name in ("philippine_scope_employment", "relevant_employment",
                                          "technically_assessable_relevant_employment", "internships",
                                          "unresolved_cases", "missing_description_cases")})
    for c in cases:
        if c["philippine_scope"] == "eligible" and c["employment"] == "yes": counts["philippine_scope_employment"] += 1
        if c["philippine_scope"] == "eligible" and c["employment"] == "yes" and c["relevant_computing_employment"] == "yes": counts["relevant_employment"] += 1
        if c["philippine_scope"] == "eligible" and c["employment"] == "yes" and c["relevant_computing_employment"] == "yes" and c["technical_assessability"] == "yes": counts["technically_assessable_relevant_employment"] += 1
        if c["cohort"] == "internship": counts["internships"] += 1
        if any(v == "unresolved" for v in (c["philippine_scope"], c["employment"], c["relevant_computing_employment"], c["technical_assessability"])): counts["unresolved_cases"] += 1
        if not c["description_chars"]: counts["missing_description_cases"] += 1
    all_items_by_id = raw_by_id
    page_groups = {}
    for page in (2, 3, None):
        group = [item for item in all_items_by_id.values() if page_from_search_url(item.get("searchUrl", ""), request) == page]
        new_group = [c for c in cases if c["page"] == page]
        page_groups[str(page) if page is not None else "unproven"] = {
            "rows": len(group), "new_ids": len(new_group),
            "corrected_provisional_assessable_new_employment_ids": sum(c["philippine_scope"] == "eligible" and c["employment"] == "yes" and c["relevant_computing_employment"] == "yes" and c["technical_assessability"] == "yes" for c in new_group),
        }
    corrected_usable = counts["technically_assessable_relevant_employment"]
    report = {
        "schema": "actor-pilot-reconciliation-v2", "rule_version": RULE_VERSION,
        "window_utc": {"fromDate": request_input.get("fromDate"), "toDate": request_input.get("toDate")},
        "inputs": {"blackfalcon_run_id": validation["run_id"], "blackfalcon_dataset_id": validation["dataset_id"], "frozen_registry_ids": len(saved_set), "frozen_registry_sha256": expected_registry_hash, "blackfalcon_raw_sha256": validation["hashes"]["raw_items.json"]},
        "identity_and_registry": {"blackfalcon_observations": len(observations), "distinct_numeric_ids": len(set(ids)), "saved_ids": len(set(ids) & saved_set), "new_ids": len(new_ids), "combined_union_ids": len(saved_set | set(ids))},
        "input_integrity": {"blackfalcon_validation_hashes_checked": len(validation["hashes"]), "six_query_manifest_entries_checked": len(sh_manifest.get("artifact_hashes", {})), "six_query_manifest_mismatches": sh_manifest_mismatches, "readme_mismatch_explanation": "README.md was updated as explicitly required to correct its candidate-run status. The frozen pilot manifest and its original hash record were preserved; the other manifest-listed inputs match." if sh_manifest_mismatches else None},
        "blackfalcon_corrected": {**dict(counts), "new_ids": len(cases), "description_availability": {"full": old_yield.get("full_descriptions"), "missing_or_empty": old_yield.get("missing_or_empty_descriptions"), "new_ids_with_description": sum(bool(c["description_chars"]) for c in cases)}, "page_groups": page_groups, "billed_rows": 50, "settled_usd": 0.11, "assessable_per_billed_row": corrected_usable / 50, "assessable_per_settled_usd": corrected_usable / 0.11, "prior_yield_report_claimed_usable_new_ids": old_yield.get("source_audited_usable_new_ids"), "prior_source_audit_claimed_assessable_new_employment_ids": sum(bool(c["prior_source_audit"].get("employment_status")) and bool(c["prior_source_audit"].get("technical_assessability")) for c in cases), "corrected_cases_that_disagree_with_yield_flag": sum((c.get("prior_yield_report") or {}).get("source_audited_usable") != (c["philippine_scope"] == "eligible" and c["employment"] == "yes" and c["relevant_computing_employment"] == "yes" and c["technical_assessability"] == "yes") for c in cases)},
        "shahidirfan_baseline": {"queries": [q.get("keyword") for q in read_json(sh / "collection_config.json").get("queries", [])], "prior_registry_ids": 438, "returned_rows": 150, "distinct_ids": 148, "new_ids": 29, "provisional_assessable_employment_ids": 29, "description_availability_new_ids": dict(Counter(row.get("description_quality", "unknown") for row in sh_audit)), "settled_usd": 0.1515, "per_billed_row": 29/150, "per_settled_usd": 29/0.1515, "window_start_utc": sh_recon.get("window_start"), "window_end_utc": sh_recon.get("window_end"), "provisional_status": True, "source_audit_rows": len(sh_audit)},
        "pagination": {"status": "pagination_unverified", "request": request, "run_metadata": {"actual_run_options": actual_options, "requested_vs_actual_run_option_matches": run_option_matches, "started_at": run_final.get("startedAt"), "finished_at": run_final.get("finishedAt")}, "saved_request_window_matches_yield_report": True, "run_started_within_five_minutes_of_frozen_window_end": True, "launch_lag_after_frozen_window_seconds": launch_lag_seconds, "request_payload_submitted_not_independently_confirmed": not bool(request.get("request_sent")), "input_evidence_limitation": "The saved exact-request artifact records request_sent=false. The completed run metadata confirms build and run-level charge/retry options but does not expose the actor input body, so submission of every actor input field is not independently proven.", "reason": "22 of 50 saved observations have no qualifying explicit page parameter; six rows have page=3 although maxPages=2. The saved evidence does not explain either discrepancy."},
        "route_decision": "Keep shahidirfan/jobstreet-scraper as the bounded recent first-page default. Retain Blackfalcon output as candidate-depth evidence; pagination remains unverified and blocks routine adoption. No further run is authorized by this reconciliation.",
        "cases": cases,
    }
    output.mkdir(parents=True, exist_ok=False)
    (output / "cases.json").write_text(json.dumps(cases, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (output / "report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    fields = list(cases[0].keys())
    with (output / "cases.csv").open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields); writer.writeheader()
        for row in cases:
            writer.writerow({k: json.dumps(v, ensure_ascii=False) if isinstance(v, (dict, list)) else v for k, v in row.items()})
    bf_page_summary = ", ".join("page %s: %s rows / %s new / %s assessable new" % (page, value["rows"], value["new_ids"], value["corrected_provisional_assessable_new_employment_ids"]) for page, value in page_groups.items())
    sh_baseline = report["shahidirfan_baseline"]
    integrity_line = "The six-query manifest still records the original README hash; the README was updated as required, and all other manifest-listed pilot files validate." if sh_manifest_mismatches else "All manifest-listed six-query pilot files validate."
    md = ["# Blackfalcon pilot reconciliation v2", "", f"Rule version: `{RULE_VERSION}`. Labels are source-text provisional assessments, not independently reviewed admissions.", "", "## Reconciled result", "", f"- 50 rows; 50 unique IDs; 34 saved; 16 new; combined registry: 483 IDs.", f"- Corrected assessable relevant Philippine employment IDs: **{corrected_usable} / 16** (prior yield report claimed {old_yield.get('source_audited_usable_new_ids')}).", f"- Missing descriptions among new IDs: {counts['missing_description_cases']}; unresolved: {counts['unresolved_cases']}; internships: {counts['internships']}. The full run has {old_yield.get('full_descriptions')} descriptions and {old_yield.get('missing_or_empty_descriptions')} missing/empty descriptions.", f"- Blackfalcon yield: {corrected_usable}/50 billed rows; {corrected_usable}/USD 0.11 settled.", f"- Saved URL page breakdown ({bf_page_summary}).", "- Page evidence remains `pagination_unverified`: 22 rows lack qualifying page URLs and 6 show page 3 despite `maxPages=2`.", "- The saved request artifact says `request_sent=false`; run metadata confirms build and run-level options, but not every submitted actor input value.", f"- Input integrity: all 67 Blackfalcon listed hashes and 206 of 207 six-query manifest artifact hashes validate. {integrity_line}", "", "## Comparison", "", f"Shahidirfan queried: {', '.join(sh_baseline['queries'])}; prior registry 438 IDs; window {sh_baseline['window_start_utc']} to {sh_baseline['window_end_utc']}; 29 provisional assessable new employment IDs / 150 billed rows / USD 0.15150 settled; new-ID description quality: {sh_baseline['description_availability_new_ids']}.", f"Blackfalcon queried `data engineer`; prior registry 467 IDs; window {request_input.get('fromDate')} to {request_input.get('toDate')}; 15 full descriptions among 16 new IDs (48 full / 2 missing across all returned rows); 50 billed rows / USD 0.11 settled.", "", "These cohorts use different query sets, prior frames, and UTC windows. Their dated marginal-yield observations are not a controlled A/B test or a market-demand estimate.", "", "## Route decision", "", report["route_decision"], "", "Query diversification and reuse of saved data remain the next planning levers. No further collection is scheduled or authorized.", "", "## Case details", "", "See `cases.csv` and `cases.json` for ID-keyed source pointers, hashes, cited passages, page evidence, per-decision reasons, and old flags side by side.", ""]
    (output / "report.md").write_text("\n".join(md), encoding="utf-8")
    manifest = {"schema": "actor-pilot-reconciliation-manifest-v1", "rule_version": RULE_VERSION, "generated_at_utc": generated_at or datetime.now(timezone.utc).isoformat(), "inputs": {"blackfalcon_raw_handoff_validation_sha256": sha256(bf / "raw_handoff_validation.json"), "blackfalcon_validated_file_hashes": validation["hashes"], "blackfalcon_raw_items_sha256": sha256(bf / "raw_items.json"), "blackfalcon_exact_request_sha256": sha256(request_path), "six_query_manifest_sha256": sha256(sh / "manifest.json"), "six_query_readme_current_sha256": sha256(sh / "README.md") if (sh / "README.md").is_file() else None, "six_query_readme_recorded_sha256": sh_manifest.get("artifact_hashes", {}).get("README.md"), "six_query_manifest_mismatches": sh_manifest_mismatches, "frozen_registry_sha256": sha256(sh_registry_path)}, "outputs": {name: sha256(output / name) for name in ("cases.json", "cases.csv", "report.json", "report.md")}}
    (output / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--blackfalcon", type=Path, required=True)
    parser.add_argument("--shahidirfan", type=Path, required=True)
    parser.add_argument("--request", type=Path, required=True, help="saved exact request JSON for the Blackfalcon run")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    report = build(args.blackfalcon, args.shahidirfan, args.output, args.request)
    print(json.dumps({"output": str(args.output.resolve()), "identity_and_registry": report["identity_and_registry"], "blackfalcon_corrected": {k:v for k,v in report["blackfalcon_corrected"].items() if k != "page_groups"}}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
