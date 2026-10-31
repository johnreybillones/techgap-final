"""Offline, provisional query-yield audit for an immutable raw-v2 release."""
import argparse
import csv
import json
import re
from collections import defaultdict
from pathlib import Path

TECH = re.compile(r"\b(software|program|developer|engineer|computing|computer|data|network|system|cyber|security|web|game|database|cloud|qa|tester|it support|machine learning|artificial intelligence|technical support)\b", re.I)
TASK = re.compile(r"\b(develop|design|build|maintain|deploy|configure|analy[sz]e|test|troubleshoot|implement|manage|monitor|program|code|support)\w*\b", re.I)
TECH_DETAIL = re.compile(r"\b(python|java|javascript|sql|cloud|linux|network|database|api|software|programming|coding|server|security|framework|system|application|testing|technical)\b", re.I)
INTERN = re.compile(r"\b(intern(ship)?|ojt|on.the.job training)\b", re.I)
FAMILY_TERMS = {
    "Intelligent Systems": re.compile(r"\b(machine learning|artificial intelligence|ai|data scientist|data engineer|data analyst|data analysis|analytics|computer vision|nlp)\b", re.I),
    "Game Development": re.compile(r"\b(game|gaming|unity|unreal|gameplay|level designer)\b", re.I),
    "Network Technology": re.compile(r"\b(network|noc|system administrator|cybersecurity|cyber security|soc analyst|infrastructure|linux administrator)\b", re.I),
    "Web Development": re.compile(r"\b(web|website|frontend|front[ -]?end|backend|back[ -]?end|full[ -]?stack|react|angular|vue)\b", re.I),
    "Shared/core": re.compile(r"\b(software engineer|software developer|application developer|programmer|qa engineer|software tester|quality assurance)\b", re.I),
}


def _jsonl(path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def _text(row):
    fields = row.get("fields") or {}
    return "\n".join(str(fields.get(k) or "") for k in ("description_text", "description_html", "title"))


def _provisional(row):
    fields = row.get("fields") or {}
    title = str(fields.get("title") or "")
    body = " ".join(str(fields.get(k) or "") for k in ("description_text", "description_html"))
    internship = bool(INTERN.search(title + " " + body))
    relevant = bool(TECH.search(title + " " + body))
    description = fields.get("description_text") or fields.get("description_html") or ""
    assessable = relevant and len(re.sub(r"<[^>]*>", " ", str(description))) >= 300 and bool(TASK.search(str(description))) and bool(TECH_DETAIL.search(str(description)))
    return ("internship" if internship else "employment"), relevant, assessable


def _description_quality(row):
    fields = row.get("fields") or {}
    raw = str(fields.get("description_text") or fields.get("description_html") or "")
    text = re.sub(r"<[^>]*>", " ", raw).strip()
    if not text:
        return "absent", 0
    detail = str(fields.get("detail_status") or "").lower()
    if row.get("full_description") is False or any(flag in detail for flag in ("teaser", "partial", "truncated")) or re.search(r"(?:\.\.\.|…|read more|show more)\s*$", text, re.I):
        return "suspected_truncation", len(text)
    if len(text) < 300:
        return "short", len(text)
    # Provider detail flags prove that text was returned, not that every posting section was captured.
    return "uncertain_completeness", len(text)


def _assessability_reason(row, relevant):
    if not relevant:
        return "not_provisionally_relevant"
    quality, length = _description_quality(row)
    if quality == "absent":
        return "description_absent"
    fields = row.get("fields") or {}
    description = str(fields.get("description_text") or fields.get("description_html") or "")
    if length < 300:
        return "description_short"
    if not TASK.search(description):
        return "no_duty_or_task_evidence"
    if not TECH_DETAIL.search(description):
        return "no_technical_detail"
    return "provisionally_assessable"


def audit(root, baseline=None, recovery_manifest=None):
    root = Path(root)
    config = json.loads((root / "collection_config.json").read_text(encoding="utf-8"))
    queries = {q["query_id"]: q for q in config["queries"]}
    postings = {r["posting_key"]: r for r in _jsonl(root / "postings.jsonl")}
    all_observations = _jsonl(root / "observations.jsonl")
    invalid_rows = _jsonl(root / "invalid_items.jsonl") if (root / "invalid_items.jsonl").exists() else []
    recovery_runs = None
    if recovery_manifest:
        recovery = json.loads(Path(recovery_manifest).read_text(encoding="utf-8"))
        recovery_runs = {row["run_id"] for row in recovery.get("recovered_datasets", [])}
    observations = all_observations
    batch_observations = [row for row in observations if recovery_runs is None or row.get("run_id") in recovery_runs]
    batch_invalid = [row for row in invalid_rows if recovery_runs is None or row.get("run_id") in recovery_runs]
    versions = defaultdict(list)
    for row in _jsonl(root / "versions.jsonl"):
        versions[row["posting_key"]].append(row)
    best = {}
    classifications = {}
    for key, choices in versions.items():
        selected = max(choices, key=lambda r: len(_text(r)))
        best[key] = selected
        classifications[key] = _provisional(selected)
    by_query = defaultdict(set)
    for row in observations:
        if row.get("query_id") in queries:
            by_query[row["query_id"]].add(row["posting_key"])
    counts = {}
    for qid in queries:
        keys = by_query.get(qid, set())
        family = queries[qid].get("family")
        family_term = FAMILY_TERMS.get(family, TECH)
        family_relevant = {k for k in keys if family_term.search(_text(best.get(k, {})))}
        family_assessable = {k for k in family_relevant if classifications.get(k, (None, False, False))[2]}
        cohorts = {name: {k for k in keys if classifications.get(k, ("employment", False, False))[0] == name}
                   for name in ("employment", "internship")}
        desc_len = {k: len(re.sub(r"<[^>]*>", " ", str(((best.get(k, {}).get("fields") or {}).get("description_text") or (best.get(k, {}).get("fields") or {}).get("description_html") or "")))) for k in keys}
        desc = {k for k in keys if desc_len[k] > 0}
        substantial = {k for k in keys if desc_len[k] >= 300}
        relevant = family_relevant
        assessable = family_assessable
        linked_queries = defaultdict(set)
        for observation in observations:
            if observation.get("posting_key") in postings:
                linked_queries[observation["posting_key"]].add(observation.get("query_id"))
        counts[qid] = {"returned_rows": sum(o.get("query_id") == qid for o in observations),
            "distinct_ids": len(keys), "description_present_ids": len(desc), "description_300plus_ids": len(substantial),
            "overlapping_ids": sum(len(linked_queries[k]) > 1 for k in keys),
            "exclusive_ids": sum(len(linked_queries[k]) == 1 for k in keys), "provisional_relevant": len(relevant),
            "provisional_assessable": len(assessable), "broad_computing_relevant": sum(classifications.get(k, (None, False, False))[1] for k in keys),
            "employment": len(cohorts["employment"]), "internship": len(cohorts["internship"]), "ids": keys,
            "assessable_ids": assessable}
    query_sets = {qid: values["ids"] for qid, values in counts.items()}
    pairwise_overlap = []
    qids = list(queries)
    for index, left in enumerate(qids):
        for right in qids[index + 1:]:
            shared = query_sets[left] & query_sets[right]
            if shared:
                pairwise_overlap.append({"query_id_a": left, "query_id_b": right, "shared_distinct_ids": len(shared)})
    ids_in_multiple_queries = {key for ids in query_sets.values() for key in ids
        if sum(key in other for other in query_sets.values()) > 1}
    # Pick each track string by plausible assessable yield with description availability as a tie-breaker.
    families = ["Intelligent Systems", "Game Development", "Network Technology", "Web Development", "Shared/core"]
    chosen = []
    for family in families:
        candidates = [qid for qid, q in queries.items() if q.get("family") == family]
        if not candidates:
            continue
        qid = max(candidates, key=lambda q: (counts.get(q, {}).get("provisional_assessable", 0),
                                               counts.get(q, {}).get("description_present_ids", 0),
                                               counts.get(q, {}).get("provisional_relevant", 0)))
        chosen.append((family, qid, queries[qid]["keyword"]))
    covered = set().union(*(counts[qid]["ids"] for _, qid, _ in chosen)) if chosen else set()
    # Complement query is the remaining string with the most additional provisional assessable IDs.
    remaining = [q for q in queries if q not in {qid for _, qid, _ in chosen}]
    complement = max(remaining, key=lambda q: (len(counts.get(q, {}).get("assessable_ids", set()) - covered),
        counts.get(q, {}).get("description_present_ids", 0), counts.get(q, {}).get("provisional_relevant", 0)))
    marginal = len(counts.get(complement, {}).get("assessable_ids", set()) - covered)
    summary = {"returned_observations": len(observations), "invalid_returned_rows": len(batch_invalid),
        "returned_rows_including_invalid": len(observations) + len(batch_invalid), "distinct_source_ids": len(postings),
        "distinct_ids_seen_under_multiple_queries": len(ids_in_multiple_queries),
        "semantic_versions": sum(map(len, versions.values())),
        "description_present_distinct_ids": sum(bool((v.get("fields") or {}).get("description_text") or (v.get("fields") or {}).get("description_html")) for v in best.values()),
        "description_under_300_or_missing_ids": sum(len(re.sub(r"<[^>]*>", " ", str((v.get("fields") or {}).get("description_text") or (v.get("fields") or {}).get("description_html") or ""))) < 300 for v in best.values()),
        "provisional_relevant_ids": sum(v[1] for v in classifications.values()),
        "provisional_assessable_ids": sum(v[2] for v in classifications.values()),
        "employment_provisional_relevant": sum(v[1] and v[0] == "employment" for v in classifications.values()),
        "employment_provisional_assessable": sum(v[2] and v[0] == "employment" for v in classifications.values()),
        "internship_provisional_relevant": sum(v[1] and v[0] == "internship" for v in classifications.values()),
        "internship_provisional_assessable": sum(v[2] and v[0] == "internship" for v in classifications.values())}
    for cohort in ("employment", "internship"):
        cohort_keys = {k for k, value in classifications.items() if value[0] == cohort}
        summary[cohort + "_distinct_ids"] = len(cohort_keys)
        summary[cohort + "_returned_observations"] = sum(o.get("posting_key") in cohort_keys for o in observations)
        summary[cohort + "_description_present_ids"] = sum(bool((best[k].get("fields") or {}).get("description_text") or (best[k].get("fields") or {}).get("description_html")) for k in cohort_keys)
    if baseline:
        prior_ids = {row["source_id"] for row in _jsonl(Path(baseline) / "postings.jsonl")}
        batch_keys = {row["posting_key"] for row in batch_observations if row.get("posting_key") in postings}
        new_keys = {key for key in batch_keys if postings[key]["source_id"] not in prior_ids}
        summary["baseline_distinct_source_ids"] = len(prior_ids)
        summary["incremental_returned_rows"] = len(batch_observations) + len(batch_invalid)
        summary["incremental_new_distinct_ids"] = len(new_keys)
        summary["new_distinct_ids_vs_baseline"] = len(new_keys)
        summary["new_provisional_relevant_ids"] = sum(classifications.get(k, (None, False, False))[1] for k in new_keys)
        summary["new_provisional_assessable_ids"] = sum(classifications.get(k, (None, False, False))[2] for k in new_keys)
        summary["new_employment_provisional_assessable_ids"] = sum(classifications.get(k, (None, False, False))[2] and classifications.get(k, (None, False, False))[0] == "employment" for k in new_keys)
        summary["new_internship_provisional_assessable_ids"] = sum(classifications.get(k, (None, False, False))[2] and classifications.get(k, (None, False, False))[0] == "internship" for k in new_keys)
        summary["new_employment_distinct_ids"] = sum(classifications.get(k, (None, False, False))[0] == "employment" for k in new_keys)
        summary["new_internship_distinct_ids"] = sum(classifications.get(k, (None, False, False))[0] == "internship" for k in new_keys)
        summary["new_employment_provisional_relevant_ids"] = sum(classifications.get(k, (None, False, False))[1] and classifications.get(k, (None, False, False))[0] == "employment" for k in new_keys)
        summary["new_internship_provisional_relevant_ids"] = sum(classifications.get(k, (None, False, False))[1] and classifications.get(k, (None, False, False))[0] == "internship" for k in new_keys)
        summary["incremental_funnel"] = {}
        for cohort in ("employment", "internship"):
            cohort_new = {key for key in new_keys if classifications.get(key, (None, False, False))[0] == cohort}
            cohort_obs = {row.get("posting_key") for row in batch_observations
                          if row.get("posting_key") in postings and classifications.get(row["posting_key"], (None, False, False))[0] == cohort}
            relevant_new = {key for key in cohort_new if classifications.get(key, (None, False, False))[1]}
            assessable_new = {key for key in cohort_new if classifications.get(key, (None, False, False))[2]}
            summary["incremental_funnel"][cohort] = {
                "returned_rows": sum(row.get("posting_key") in cohort_obs for row in batch_observations),
                "new_distinct_ids": len(cohort_new), "provisional_relevant": len(relevant_new),
                "provisional_technically_assessable": len(assessable_new)}
        summary["incremental_funnel"]["combined"] = {
            "returned_rows": len(batch_observations) + len(batch_invalid), "new_distinct_ids": len(new_keys),
            "provisional_relevant": sum(classifications.get(k, (None, False, False))[1] for k in new_keys),
            "provisional_technically_assessable": sum(classifications.get(k, (None, False, False))[2] for k in new_keys)}
    proposals = [{"family": family, "query_id": qid, "query": text,
        "saved_distinct_ids": counts[qid]["distinct_ids"], "provisional_relevant": counts[qid]["provisional_relevant"],
        "provisional_assessable": counts[qid]["provisional_assessable"],
        "description_present_ids": counts[qid]["description_present_ids"],
        "description_300plus_ids": counts[qid]["description_300plus_ids"],
        "overlapping_ids": counts[qid]["overlapping_ids"], "exclusive_ids": counts[qid]["exclusive_ids"],
        "expected_marginal_assessable_ids": len(counts[qid]["assessable_ids"] - (set().union(*(counts[p]["ids"] for _, p, _ in chosen[:i])) if i else set())),
        "expected_marginal_value": "{} provisional assessable IDs outside the earlier proposed queries; {} of this query's IDs also occur under another saved search.".format(
            len(counts[qid]["assessable_ids"] - (set().union(*(counts[p]["ids"] for _, p, _ in chosen[:i])) if i else set())), counts[qid]["overlapping_ids"]),
        "uncertainty": "Relevance and assessability are provisional text screens. All 34 historical searches returned 25 rows, so the saved prefixes were capped and the marginal count is not a forecast of new supply."}
        for i, (family, qid, text) in enumerate(chosen)]
    proposals.append({"family": "Complement", "query_id": complement, "query": queries[complement]["keyword"],
        "saved_distinct_ids": counts[complement]["distinct_ids"], "provisional_relevant": counts[complement]["provisional_relevant"],
        "provisional_assessable": counts[complement]["provisional_assessable"],
        "description_present_ids": counts[complement]["description_present_ids"],
        "description_300plus_ids": counts[complement]["description_300plus_ids"],
        "overlapping_ids": counts[complement]["overlapping_ids"], "exclusive_ids": counts[complement]["exclusive_ids"],
        "expected_marginal_assessable_ids": marginal,
        "expected_marginal_value": "{} provisional assessable IDs do not occur under the five proposed core queries, making this the measured complement in the saved sample.".format(marginal),
        "uncertainty": "Alternative saved query; its marginal count is the heuristic candidate pool excluded by the five proposed strings, not a forecast. All historical searches hit the 25-row request cap."})
    query_results = []
    for qid, values in counts.items():
        row = {k: v for k, v in values.items() if k not in {"ids", "assessable_ids"}}
        row.update({"query_id": qid, "query": queries[qid]["keyword"], "family": queries[qid]["family"]})
        query_results.append(row)
    quality_rows = []
    linked_queries_by_id = defaultdict(set)
    for observation in all_observations:
        linked_queries_by_id[observation.get("posting_key")].add(observation.get("query_id"))
    for key, version in best.items():
        quality, length = _description_quality(version)
        _, is_relevant, assessable = classifications.get(key, ("employment", False, False))
        quality_rows.append({"posting_key": key, "source_id": postings.get(key, {}).get("source_id"),
            "description_quality": quality, "description_characters": length,
            "provisional_relevance": is_relevant, "provisional_assessability": assessable,
            "unassessable_reason": None if assessable else _assessability_reason(version, is_relevant),
            "query_ids": sorted(qid for qid in linked_queries_by_id.get(key, set()) if qid),
            "provider_full_description_flag": version.get("full_description"),
            "source_detail_status": (version.get("fields") or {}).get("detail_status"),
            "source_detail_source": (version.get("fields") or {}).get("detail_source"),
            "raw_file": version.get("raw_file"), "version_id": version.get("version_id")})
    summary["description_quality_counts"] = {code: sum(row["description_quality"] == code for row in quality_rows)
        for code in ("absent", "short", "suspected_truncation", "uncertain_completeness")}
    return {"schema_version": "saved-jobstreet-yield-audit-v2", "source_release": str(root), "summary": summary,
        "query_results": query_results, "pairwise_query_overlap": pairwise_overlap,
        "proposed_queries": proposals, "description_quality_by_source_id": quality_rows,
        "recovery_run_ids": sorted(recovery_runs) if recovery_runs is not None else None,
        "method": "All relevance, cohort and assessability results are provisional text screens; location and remote eligibility still need source review. Technical assessability requires a description of at least 300 characters, a task verb, and technical detail; every unassessable source ID has an inspectable reason and raw pointer. Provider detail flags show that text was returned, not that all sections are complete. Internship terms split cohorts. No legacy admission or model outputs are used."}


def write_review_sheet(root, report, destination):
    root = Path(root)
    postings = {row["posting_key"]: row for row in _jsonl(root / "postings.jsonl")}
    versions = defaultdict(list)
    for row in _jsonl(root / "versions.jsonl"):
        versions[row["posting_key"]].append(row)
    observations = _jsonl(root / "observations.jsonl")
    by_query = defaultdict(set)
    for row in observations:
        by_query[row.get("query_id")].add(row.get("posting_key"))
    quality = {row["posting_key"]: row for row in report["description_quality_by_source_id"]}
    selected = []
    seen = set()
    for proposal in report["proposed_queries"]:
        qid = proposal["query_id"]
        candidates = sorted(by_query[qid], key=lambda key: (not quality.get(key, {}).get("provisional_assessability", False), key))
        for want_assessable in (True, False):
            match = next((key for key in candidates if key not in seen and
                          quality.get(key, {}).get("provisional_assessability", False) is want_assessable), None)
            if match:
                selected.append(match); seen.add(match)
    # Ensure the compact sample contains observed duplicates and missing/short text when available.
    for condition in (lambda row: len(row.get("query_ids", [])) > 1,
                      lambda row: row.get("description_quality") == "absent",
                      lambda row: row.get("description_quality") == "short"):
        match = next((row["posting_key"] for row in report["description_quality_by_source_id"]
                      if row["posting_key"] not in seen and condition(row)), None)
        if match and len(selected) < 24:
            selected.append(match); seen.add(match)
    fields = ("source_id", "query_ids", "original_title", "duty_qualification_passage", "proposed_relevance",
              "proposed_cohort", "proposed_track_coverage", "proposed_technical_text_assessability",
              "assessability_reason", "description_quality", "raw_file", "version_id",
              "reviewer_decision", "reviewer_reason")
    destination = Path(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        for key in selected[:24]:
            version = max(versions[key], key=lambda row: len(_text(row)))
            source = version.get("fields") or {}
            title = str(source.get("title") or "")
            body = re.sub(r"<[^>]*>", " ", str(source.get("description_text") or source.get("description_html") or ""))
            sentences = re.split(r"(?<=[.!?])\s+", body)
            passage = next((sentence.strip() for sentence in sentences if TASK.search(sentence) or TECH_DETAIL.search(sentence)), body[:500])
            _, relevant, assessable = _provisional(version)
            coverage = sorted(name for name, pattern in FAMILY_TERMS.items() if pattern.search(title + " " + body))
            linked = sorted({row.get("query_id") for row in observations if row.get("posting_key") == key})
            row = quality[key]
            writer.writerow({"source_id": postings[key]["source_id"], "query_ids": ";".join(linked),
                "original_title": title, "duty_qualification_passage": passage[:500],
                "proposed_relevance": "provisional_likely_relevant" if relevant else "provisional_not_relevant",
                "proposed_cohort": "internship" if INTERN.search(title + " " + body) else "employment",
                "proposed_track_coverage": ";".join(coverage),
                "proposed_technical_text_assessability": "provisional_assessable" if assessable else "provisional_unassessable",
                "assessability_reason": row.get("unassessable_reason") or "provisional_screen_passed",
                "description_quality": row["description_quality"], "raw_file": row["raw_file"],
                "version_id": row["version_id"], "reviewer_decision": "pending", "reviewer_reason": ""})
    return destination


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("release", help="Saved raw-v2 campaign directory")
    parser.add_argument("--baseline", help="Earlier saved raw-v2 registry to measure genuinely new distinct IDs")
    parser.add_argument("--recovery-manifest", help="Restrict the incremental batch to runs linked by this recovery manifest")
    parser.add_argument("--output", required=True, help="JSON report path; source release remains unchanged")
    parser.add_argument("--review-sheet", help="Optional compact CSV template for source-text review")
    args = parser.parse_args()
    report = audit(args.release, args.baseline, args.recovery_manifest)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if args.review_sheet:
        write_review_sheet(args.release, report, args.review_sheet)
    print(json.dumps({"output": args.output, "summary": report["summary"], "proposed_queries": report["proposed_queries"]}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
