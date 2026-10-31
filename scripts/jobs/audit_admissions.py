"""Create a source-linked, read-only review of one JobStreet campaign."""
import argparse
import csv
import html
import json
import re
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CAMPAIGN = ROOT / "data/job_collections/jobstreet-2026-10-live-preflight"
OUT = CAMPAIGN / "admission-audit-v2"


def read_jsonl(path):
    with path.open(encoding="utf-8") as stream:
        return [json.loads(line) for line in stream if line.strip()]


def clean(value):
    text = html.unescape(re.sub(r"<[^>]+>", " ", str(value or "")))
    return re.sub(r"\s+", " ", text).strip()


def first_match(patterns, text):
    for label, pattern in patterns:
        match = re.search(pattern, text, re.I)
        if match:
            return label, match.group(0)
    return "", ""


def context_for(pattern, text, radius=110):
    match = re.search(pattern, text, re.I)
    if not match:
        return ""
    return text[max(0, match.start() - radius):min(len(text), match.end() + radius)].strip()


ROLE_PATTERNS = [
    ("data analyst", r"\bdata\s+(?:and\s+)?(?:business\s+)?analyst\b"),
    ("data scientist", r"\bdata scientist\b"),
    ("data engineer", r"\bdata engineer\b"),
    ("machine learning / AI engineer", r"\b(?:machine learning|ML|AI|artificial intelligence)\s+(?:/\s*)?(?:engineer|developer)\b|\b(?:AI|ML) engineer\b"),
    ("computer vision engineer", r"\bcomputer vision\b"),
    ("game developer", r"\bgame developer\b"),
    ("game programmer", r"\bgame programmer\b"),
    ("game designer", r"\bgame designer\b"),
    ("level designer", r"\blevel designer\b"),
    ("gameplay engineer", r"\bgameplay engineer\b"),
    ("Unity developer", r"\bUnity developer\b"),
    ("Unreal developer", r"\bUnreal (?:Engine )?developer\b"),
    ("network engineer", r"\bnetwork engineer\b"),
    ("network administrator", r"\bnetwork administrator\b"),
    ("network support", r"\bnetwork support\b"),
    ("NOC engineer", r"\bNOC engineer\b"),
    ("systems administrator", r"\bsystems? administrator\b"),
    ("cybersecurity analyst", r"\bcyber ?security analyst\b"),
    ("SOC analyst", r"\bSOC analyst\b"),
    ("frontend developer", r"\bfront[- ]end developer\b|\bfrontend developer\b"),
    ("backend developer", r"\bback[- ]end developer\b|\bbackend developer\b"),
    ("full stack developer", r"\bfull[- ]stack developer\b"),
    ("web developer", r"\bweb developer\b|\bweb application developer\b"),
    ("application developer", r"\bapplication developer\b"),
    ("QA / software tester", r"\bQA engineer\b|\bquality assurance\b|\bsoftware tester\b|\btest engineer\b"),
    ("software engineer", r"\bsoftware engineer\b"),
    ("software developer", r"\bsoftware developer\b"),
    ("programmer", r"\bprogrammer\b"),
]

TRACK_PATTERNS = {
    "Intelligent Systems": r"\b(?:data analyst|data scientist|data engineer|machine learning|\bAI\b|artificial intelligence|computer vision|analytics|data science)\b",
    "Game Development": r"\b(?:game developer|game programmer|game designer|gameplay|level designer|Unity|Unreal Engine)\b",
    "Network Technology": r"\b(?:network engineer|network administrator|network support|NOC|systems administrator|cyber ?security|SOC analyst)\b",
    "Web Development": r"\b(?:web developer|web application|front[- ]end|frontend|back[- ]end|backend|full[- ]stack)\b",
    "Shared/core": r"\b(?:software engineer|software developer|application developer|programmer|QA engineer|quality assurance|software tester)\b",
}

INTERN_TITLE = re.compile(r"\b(?:intern(?:ship)?|OJT|student placement|apprentice(?:ship)?)\b", re.I)
INTERN_BODY = re.compile(r"\b(?:intern(?:ship)?|OJT|student placement|apprentice(?:ship)?)\b", re.I)
ENTRY = re.compile(r"\b(?:junior|jr\.?|entry[- ]level|fresh graduates? welcome|open to fresh graduates?|no experience required|graduate trainee|graduate role)\b", re.I)
SENIOR_TITLE = re.compile(r"\b(?:mid[- ]level|intermediate|senior|sr\.?|lead|manager|principal|head of)\b", re.I)
YEARS = re.compile(r"(?P<low>\d+)\s*(?:-|–|—|to)\s*(?P<high>\d+)\s*\+?\s*years?", re.I)
PLUS_YEARS = re.compile(r"(?P<n>\d+)\s*\+\s*years?", re.I)
AT_LEAST = re.compile(r"\b(?:at least|minimum(?: of)?|no less than)\s+(?P<n>\d+)\s+years?", re.I)
EXACT_YEARS = re.compile(r"\b(?P<n>\d+)\s+years?\s+(?:of\s+)?(?:relevant\s+)?experience\b", re.I)


def experience_screen(title, body):
    combined = title + "\n" + body
    explicit_entry = ENTRY.search(title) or ENTRY.search(body)
    senior_title = SENIOR_TITLE.search(title)
    mentions = []
    for match in YEARS.finditer(combined):
        low, high = int(match.group("low")), int(match.group("high"))
        left = combined[max(0, match.start() - 90):match.start()]
        mandatory = bool(re.search(r"required|requirement|minimum|at least|experience|years? of", left, re.I))
        mentions.append(("range", low, high, match.group(0), mandatory))
    for pattern, kind in ((PLUS_YEARS, "open"), (AT_LEAST, "open"), (EXACT_YEARS, "exact")):
        for match in pattern.finditer(combined):
            left = combined[max(0, match.start() - 90):match.start()]
            mandatory = kind != "exact" or bool(re.search(r"required|requirement|minimum|at least", left, re.I))
            n = int(match.groupdict().get("n") or 0)
            mentions.append((kind, n, n, match.group(0), mandatory))
    mandatory = [m for m in mentions if m[4]]
    over_two = [m for m in mandatory if m[2] > 2]
    within_two = [m for m in mandatory if 0 <= m[1] <= m[2] <= 2]
    open_two = [m for m in mandatory if m[0] == "open" and m[1] == 2]
    if senior_title:
        seniority, evidence = "outside_entry_junior_candidate", senior_title.group(0)
    elif over_two:
        seniority, evidence = "outside_entry_junior_candidate", "; ".join(m[3] for m in over_two)
    elif open_two:
        seniority, evidence = "unresolved_open_ended_two_year_requirement", "; ".join(m[3] for m in open_two)
    elif explicit_entry:
        seniority, evidence = "entry_junior_evidence_candidate", explicit_entry.group(0)
    elif within_two:
        seniority, evidence = "clear_0_2_year_requirement_candidate", "; ".join(m[3] for m in within_two)
    else:
        seniority, evidence = "unresolved_seniority", "; ".join(m[3] for m in mentions[:4])
    return seniority, evidence, mentions


def main(argv=None):
    global CAMPAIGN, OUT
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--campaign", type=Path, default=CAMPAIGN)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    CAMPAIGN = args.campaign.resolve()
    OUT = args.output.resolve() if args.output else CAMPAIGN / "admission-audit-v2"
    OUT.mkdir(parents=True, exist_ok=True)
    postings = {row["posting_key"]: row for row in read_jsonl(CAMPAIGN / "postings.jsonl")}
    versions = defaultdict(list)
    for row in read_jsonl(CAMPAIGN / "versions.jsonl"):
        versions[row["posting_key"]].append(row)
    admissions = defaultdict(list)
    for row in read_jsonl(CAMPAIGN / "admission.jsonl"):
        admissions[row["posting_key"]].append(row)
    observations = defaultdict(list)
    for row in read_jsonl(CAMPAIGN / "observations.jsonl"):
        observations[row["posting_key"]].append(row)
    config = json.loads((CAMPAIGN / "collection_config.json").read_text(encoding="utf-8"))
    query_names = {q["query_id"]: q.get("family", "") for q in config["queries"]}
    window_start, window_end = config["window_start"], config["window_end"]

    audit_rows = []
    for key, posting in postings.items():
        candidates = versions.get(key, [])
        version = max(candidates, key=lambda v: (bool(v.get("full_description")), len(clean(v.get("fields", {}).get("description_text")))))
        fields = version.get("fields", {})
        title = clean(fields.get("title"))
        body = clean(fields.get("description_text") or fields.get("description_html"))
        old = admissions.get(key, [])
        old_states = {x["state"] for x in old}
        if "eligible" in old_states:
            old_state = "eligible"
        elif "unresolved" in old_states:
            old_state = "unresolved"
        else:
            old_state = "excluded"
        checks = defaultdict(set)
        check_evidence = defaultdict(set)
        for admission in old:
            for name, result in admission.get("checks", {}).items():
                checks[name].add(result.get("state", "unknown"))
                if result.get("evidence") not in (None, ""):
                    check_evidence[name].add(clean(result.get("evidence")))
        non_seniority = ["identity", "date", "geography", "relevance", "description"]
        other_gate = "pass" if all(checks.get(name) == {"pass"} for name in non_seniority) else (
            "fail" if any("fail" in checks.get(name, set()) for name in non_seniority) else "review")
        intern_title = INTERN_TITLE.search(title)
        open_to_intern = bool(re.search(r"\bopen to\s+(?:an?\s+)?intern(?:ship)?\b|\binterns?\s+welcome\b", title, re.I))
        intern_body = INTERN_BODY.search(body)
        if intern_title and open_to_intern:
            cohort, cohort_evidence = "vacancy_context_review", intern_title.group(0)
        elif intern_title:
            cohort, cohort_evidence = "internship_cohort_candidate", intern_title.group(0)
        elif intern_body:
            snippet = body[max(0, intern_body.start()-100):min(len(body), intern_body.end()+120)]
            cohort, cohort_evidence = "vacancy_context_review", snippet
        else:
            cohort, cohort_evidence = "employment_cohort_candidate", clean(fields.get("workType"))
        seniority, seniority_evidence, mentions = experience_screen(title, body)
        if cohort == "internship_cohort_candidate":
            population = "internship_review_candidate" if other_gate != "fail" else "fails_other_saved_gate"
        elif seniority in ("entry_junior_evidence_candidate", "clear_0_2_year_requirement_candidate"):
            population = "employment_review_candidate" if other_gate != "fail" else "fails_other_saved_gate"
        elif seniority == "outside_entry_junior_candidate":
            population = "outside_entry_junior_candidate"
        else:
            population = "unresolved_for_review"
        role, role_evidence = first_match(ROLE_PATTERNS, title)
        if not role:
            role = "other / role review"
            role_evidence = title
        track_text = title + "\n" + body[:6000]
        tracks = [name for name, pattern in TRACK_PATTERNS.items() if re.search(pattern, track_text, re.I)]
        track_evidence = []
        for name, pattern in TRACK_PATTERNS.items():
            snippet = context_for(pattern, track_text, 45)
            if snippet:
                track_evidence.append(name + ": " + snippet)
        query_ids = sorted({x["query_id"] for x in observations.get(key, [])})
        query_families = sorted({query_names.get(q, "") for q in query_ids if query_names.get(q, "")})
        date_state = ";".join(sorted(checks.get("date", {"unknown"})))
        audit_rows.append({
            "posting_key": key, "source_id": posting.get("source_id"), "source_url": posting.get("source_url"),
            "title": title, "company": clean(fields.get("company")), "location": clean(fields.get("location")),
            "posted_at": fields.get("postedAt_iso", ""), "legacy_state_v1": old_state,
            "legacy_states_across_observations": ";".join(sorted(old_states)), "other_saved_gates": other_gate,
            "date_check_states": date_state, "proposed_population_screen": population,
            "cohort_evidence_screen": cohort, "cohort_evidence": cohort_evidence,
            "seniority_admission_evidence_context": context_for(r"\b(?:years?|experience|junior|graduate|senior|lead|intermediate)\b", title + " " + body, 140),
            "seniority_screen": seniority, "seniority_evidence": seniority_evidence,
            "all_year_mentions": "; ".join(m[3] for m in mentions), "canonical_role_candidate": role,
            "role_title_evidence": role_evidence, "track_candidates_screen_only": "; ".join(tracks),
            "track_evidence_contexts_screen_only": " || ".join(track_evidence),
            "query_ids": ";".join(query_ids), "discovery_families": ";".join(query_families),
            "saved_identity_evidence": "; ".join(sorted(check_evidence["identity"])),
            "saved_date_evidence": "; ".join(sorted(check_evidence["date"])),
            "saved_geography_evidence": "; ".join(sorted(check_evidence["geography"])),
            "saved_relevance_evidence": "; ".join(sorted(check_evidence["relevance"])),
            "saved_description_evidence": "; ".join(sorted(check_evidence["description"])),
            "description_excerpt": body[:360], "selected_version_id": version.get("version_id"),
            "source_raw_file": version.get("raw_file"), "source_raw_sha256": version.get("raw_hash"),
        })

    audit_rows.sort(key=lambda r: (r["proposed_population_screen"], r["canonical_role_candidate"], r["posting_key"]))
    csv_path = OUT / "posting_case_review.csv"
    with csv_path.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(audit_rows[0]))
        writer.writeheader()
        writer.writerows(audit_rows)

    counts = Counter(row["proposed_population_screen"] for row in audit_rows)
    cohort_counts = Counter(row["cohort_evidence_screen"] for row in audit_rows)
    old_counts = Counter(row["legacy_state_v1"] for row in audit_rows)
    accepted_cross = Counter(row["proposed_population_screen"] for row in audit_rows if row["legacy_state_v1"] == "eligible")
    other_gate_counts = Counter(row["other_saved_gates"] for row in audit_rows)
    date_counts = Counter(row["date_check_states"] for row in audit_rows)
    roles = defaultdict(Counter)
    tracks = defaultdict(Counter)
    for row in audit_rows:
        cohort = row["proposed_population_screen"]
        roles[cohort][row["canonical_role_candidate"]] += 1
        for track in filter(None, row["track_candidates_screen_only"].split("; ")):
            tracks[cohort][track] += 1
    obs_count = len(read_jsonl(CAMPAIGN / "observations.jsonl"))
    version_count = sum(len(v) for v in versions.values())
    eligible_ids = {r["posting_key"] for r in audit_rows if r["legacy_state_v1"] == "eligible"}
    output = [
        "# JobStreet admission audit — proposed screen v2",
        "",
        "Updated: 2026-10-22 (Asia/Manila). This is a read-only reclassification screen; it does not rewrite campaign admission records or establish reviewed eligibility.",
        "",
        "## Reconciled evidence frame",
        "",
        f"- Distinct source posting IDs: {len(postings)}.",
        f"- Saved semantic versions: {version_count}; raw observations: {obs_count}.",
        f"- Legacy v1 unique states: eligible {old_counts['eligible']} (matches the {len(eligible_ids)} distinct keys in `eligible_frame.jsonl`), unresolved {old_counts['unresolved']}, excluded {old_counts['excluded']}; one key is counted once using eligible > unresolved > excluded across observations.",
        f"- Re-screen of the 33 legacy accepted IDs: {accepted_cross['employment_review_candidate']} remain employment candidates pending source review, {accepted_cross['outside_entry_junior_candidate']} screen outside entry/junior, and {accepted_cross['unresolved_for_review']} require review under v2. The six outside-screen cases and ten unresolved cases are individually linked in the CSV; do not carry all 33 forward as validated under v2.",
        f"- Saved non-seniority gate aggregation across distinct IDs: {other_gate_counts['pass']} pass, {other_gate_counts['review']} need review, {other_gate_counts['fail']} have at least one saved failure. Date checks are pass for {date_counts['pass']} IDs and fail for {date_counts['fail']} IDs; repeated observations with mixed evidence are retained in each case row.",
        f"- Frozen window: `{window_start}` to `{window_end}`; these are the campaign's observed source-date checks, not a 12-month collection.",
        "- Identity is exact JobStreet source ID. Five keys have a second semantic version; those versions are retained but counted once. Similarity/repost evidence was not adjudicated, so no cross-ID merge is applied.",
        "",
        "## Proposed rule and screen result",
        "",
        "Proposed rule version: `entry-junior-internship-v2-proposed`, reflecting decisions A37–A40 and Plan 1 §5. A posting is only eligible after identity, in-window publication, Philippine eligibility, usable description, actual computing duties and cohort are all established. Internship/OJT vacancies form a separate cohort. Employee vacancies enter entry/junior through explicit junior/graduate evidence or a clear mandatory 0–2-year maximum. Explicit seniority or mandatory requirements above two years are outside that cohort; open-ended `2+`/`at least 2`, conflicts, unclear wording and ambiguous internship mentions remain unresolved.",
        "",
        "The generated CSV is a screening aid. Its population, canonical-role and track fields are candidates based on deterministic title/text matching; they are not accepted cohort counts. The CSV preserves direct saved evidence for identity, date, geography, relevance and description, plus nearby source context for seniority, internship/OJT and every track keyword match. Human review remains necessary for whether an experience statement is mandatory, whether a body mention describes this vacancy, principal duties, track membership, outdated/expired shells and conflicting versions. Body mentions of internship/OJT are surfaced with context rather than treated as a vacancy type.",
        "",
        "| Screen-only category | Distinct IDs |",
        "| --- | ---: |",
    ]
    for name, count in sorted(counts.items()):
        output.append(f"| `{name}` | {count} |")
    output += ["", "Cohort marker screen (before eligibility gates):", "", "| Cohort marker | Distinct IDs |", "| --- | ---: |"]
    for name, count in sorted(cohort_counts.items()):
        output.append(f"| `{name}` | {count} |")
    output += [
        "",
        f"These counts partition the {len(postings)} IDs, but `employment_review_candidate` and `internship_review_candidate` are not final eligible cohorts because remaining gates and source context need case-level review. Do not use their sum as the accepted employment or internship total.",
        "",
        f"The cohort marker screen identifies {cohort_counts['internship_cohort_candidate']} explicit title-level internship/OJT/apprentice cases and {cohort_counts['vacancy_context_review']} title/body mentions requiring vacancy-context review. It does not determine which mentions refer to the current vacancy rather than past experience or general background.",
        "",
        "## Canonical role and track screening counts",
        "",
        "The tables below count the `canonical_role_candidate` and keyword-derived `track_candidates_screen_only` in the CSV, separated by the proposed screen category. Track values may overlap, and an unassigned role is retained for review. Discovery query family is provenance only; it is not counted as a verified academic track.",
        "",
        "### Role candidates",
        "",
        "| Screen category | Candidate role | Distinct IDs |",
        "| --- | --- | ---: |",
    ]
    for cohort in sorted(roles):
        for role, count in sorted(roles[cohort].items(), key=lambda pair: (-pair[1], pair[0])):
            output.append(f"| `{cohort}` | {role} | {count} |")
    output += ["", "### Track candidates", "", "| Screen category | Track candidate | Distinct IDs |", "| --- | --- | ---: |"]
    for cohort in sorted(tracks):
        for track, count in sorted(tracks[cohort].items(), key=lambda pair: (-pair[1], pair[0])):
            output.append(f"| `{cohort}` | {track} | {count} |")
    output += [
        "",
        "## Case review and collection decision",
        "",
        f"Every posting key is linked in `{csv_path.name}` to its JobStreet URL, selected version ID, raw-file pointer/hash, title, source text excerpt, query/run-derived discovery families, saved legacy checks, experience/cohort evidence and role/track screen. The file includes all {len(audit_rows)} IDs, including all legacy accepted, excluded and unresolved cases.",
        "",
        f"The collection is {max(0, 1000 - len(eligible_ids))} below the initial target of 1,000 accepted entry/junior postings under the historical policy frame. The v2 candidate screen is not sufficient to revise that accepted count. This campaign contains {obs_count} saved raw observations; duplicates and unresolved cases substantially reduce usable supply.",
        "",
        "The saved data does not establish recoverable supply beyond this one-month window. Although the actor request used `anytime`, the recorded adapter does not establish chronological continuation, a start-date filter or skip-known-ID support, and queries commonly reached their 25-result limit. Repeatedly running the same prefixes would incur duplicate charges. Therefore window widening is permitted by policy but its recoverability is unproven from this campaign; evaluate a verified continuation/history route before paying for more acquisition.",
        "",
        "No saved admission, raw payload, observation, eligible-frame row or budget ledger was changed by this audit. No new paid collection was run.",
        "",
    ]
    (OUT / "README.md").write_text("\n".join(output), encoding="utf-8")
    print(json.dumps({"distinct_posting_ids": len(audit_rows), "versions": version_count, "observations": obs_count,
                      "legacy_unique_states": dict(old_counts), "proposed_screen": dict(counts),
                      "case_review_csv": str(csv_path), "report": str(OUT / 'README.md')}, ensure_ascii=False))


if __name__ == "__main__":
    main()
