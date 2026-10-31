"""Versioned P2A policy gates and source/count-unit reconciliation."""
from collections import Counter, defaultdict


POLICY_VERSION = "entry-junior-internship-v3-auto"


def decide_admission(case, *, policy_version=POLICY_VERSION):
    """Apply only explicit P2A gates to source/model evidence.

    ``case`` is produced by the classifier stage. This function does not infer
    missing facts and never turns a technical model failure into a rejection.
    """
    if case.get("technical_failure"):
        raise RuntimeError("p2a_technical_failure:" + str(case["technical_failure"]))

    reasons = []
    for field, reason in (
        ("identity_ok", "identity_not_established"),
        ("date_ok", "date_outside_or_not_established"),
        ("geography_ok", "philippine_eligibility_not_established"),
        ("usable_text", "usable_source_text_not_established"),
        ("computing_relevance_supported", "computing_relevance_not_supported"),
    ):
        if case.get(field) is not True:
            reasons.append(reason)
    if not case.get("occupation"):
        reasons.append("no_supported_occupation")
    if case.get("explicit_senior_applicant_role"):
        reasons.append("explicit_senior_applicant_role")
    minimum = case.get("mandatory_experience_min_years")
    if minimum is not None and float(minimum) > 2:
        reasons.append("mandatory_experience_above_two_years")
    cohort = case.get("cohort")
    if cohort not in {"employment", "internship"}:
        reasons.append("cohort_not_established")

    decision = "reject" if reasons else "accept"
    return {
        "schema_version": "job-admission-decision-v1",
        "policy_version": policy_version,
        "posting_key": case["posting_key"],
        "count_unit_id": case.get("count_unit_id") or case["posting_key"],
        "selected_version_id": case["selected_version_id"],
        "selected_raw_hash": case["selected_raw_hash"],
        "decision": decision,
        "accepted_cohort": cohort if decision == "accept" else None,
        "occupation": case.get("occupation"),
        "track_links": case.get("tracks", []),
        "seniority_basis": case.get("seniority_basis"),
        "evidence": case.get("evidence", {}),
        "reason_codes": sorted(set(reasons)),
        "attempt_history": case.get("attempt_history", []),
        "model_versions": case.get("model_versions", {}),
        "taxonomy_version": case.get("taxonomy_version"),
    }


def reconcile_decisions(decisions):
    decisions = list(decisions)
    keys = [row["posting_key"] for row in decisions]
    if len(keys) != len(set(keys)):
        raise ValueError("duplicate_source_decision")
    counts = Counter()
    accepted_by_unit = defaultdict(list)
    for row in decisions:
        if row.get("decision") == "accept":
            cohort = row.get("accepted_cohort")
            if cohort not in {"employment", "internship"}:
                raise ValueError("accepted_decision_missing_cohort")
            counts["accepted_" + cohort] += 1
            accepted_by_unit[row["count_unit_id"]].append(row)
        elif row.get("decision") == "reject":
            counts["rejected"] += 1
        else:
            raise ValueError("nonterminal_admission_decision")

    units = []
    for unit_id, members in sorted(accepted_by_unit.items()):
        cohorts = {row["accepted_cohort"] for row in members}
        if len(cohorts) != 1:
            raise ValueError("count_unit_mixed_cohort:" + unit_id)
        selected = sorted(members, key=lambda row: row["posting_key"])[0]
        units.append({
            "count_unit_id": unit_id,
            "cohort": selected["accepted_cohort"],
            "representative_posting_key": selected["posting_key"],
            "representative_version_id": selected["selected_version_id"],
            "source_posting_keys": sorted(row["posting_key"] for row in members),
        })
    total = len(decisions)
    summary = {
        "input_postings": total,
        "accepted_employment": counts["accepted_employment"],
        "accepted_internship": counts["accepted_internship"],
        "rejected": counts["rejected"],
        "accepted_count_units": len(units),
    }
    summary["equation_reconciles"] = total == (
        summary["accepted_employment"] + summary["accepted_internship"] + summary["rejected"]
    )
    return summary, units

