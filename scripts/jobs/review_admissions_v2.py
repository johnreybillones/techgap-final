"""Prepare and reconcile human-reviewed v2 JobStreet admission decisions.

This tool is offline. It reads the immutable screening CSV and writes a separate
review artifact; it never changes v1 admissions, observations, or raw payloads.
"""
import argparse
import csv
import hashlib
import json
import os
import tempfile
from collections import Counter
from datetime import datetime
from pathlib import Path


POLICY_VERSION = "entry-junior-internship-v2-reviewed"
REVIEW_COLUMNS = (
    "review_decision", "reviewer_id", "reviewed_at", "review_reason",
    "review_evidence_json", "verified_gates_json", "cohort", "canonical_role",
    "track_memberships_json",
)
GATES = ("identity", "publication_date", "philippine_eligibility", "description",
         "computing_duties", "cohort", "seniority")
COHORTS = {"employment", "internship"}
TRACKS = {"Intelligent Systems", "Game Development", "Network Technology",
          "Web Development", "Shared/core"}
DECISIONS = {"accepted", "excluded", "unresolved"}


def _digest(path):
    value = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()


def _write_new(path, writer):
    """Atomically create an artifact without replacing existing review evidence."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=str(path.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="") as stream:
            writer(stream)
            stream.flush()
            os.fsync(stream.fileno())
        # Hard-link creation is atomic and fails if another artifact already exists.
        os.link(temporary, str(path))
    except FileExistsError:
        raise FileExistsError("Refusing to replace existing review artifact: {}".format(path))
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def prepare_template(screen_csv, output_csv):
    """Copy screen evidence to a new editable template with empty review fields."""
    with Path(screen_csv).open(encoding="utf-8-sig", newline="") as source:
        reader = csv.DictReader(source)
        if not reader.fieldnames or not {"posting_key", "source_id", "source_url", "selected_version_id",
                                        "source_raw_sha256"}.issubset(reader.fieldnames):
            raise ValueError("Screen CSV is missing required source identity fields")
        if set(REVIEW_COLUMNS).intersection(reader.fieldnames):
            raise ValueError("Input already contains review columns; use a screen-only CSV")
        fields = list(reader.fieldnames) + list(REVIEW_COLUMNS)
        rows = list(reader)
    keys = [row["posting_key"] for row in rows]
    if len(keys) != len(set(keys)):
        raise ValueError("Screen CSV contains duplicate posting_key values")

    def write(stream):
        writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            row.update({name: "" for name in REVIEW_COLUMNS})
            writer.writerow(row)
    _write_new(output_csv, write)
    return {"template": str(output_csv), "rows": len(rows), "screen_sha256": _digest(screen_csv)}


def _json_cell(row, name, expected, posting_key):
    try:
        result = json.loads(row.get(name) or "")
    except (TypeError, ValueError) as exc:
        raise ValueError("{} has invalid {} JSON".format(posting_key, name)) from exc
    if not isinstance(result, expected):
        raise ValueError("{} {} must be a JSON {}".format(posting_key, name, expected.__name__))
    return result


def _decision(row):
    key = row.get("posting_key", "")
    decision = (row.get("review_decision") or "").strip().lower()
    reviewer = (row.get("reviewer_id") or "").strip()
    reviewed_at = (row.get("reviewed_at") or "").strip()
    reason = (row.get("review_reason") or "").strip()
    if decision not in DECISIONS:
        raise ValueError("{} review_decision must be accepted, excluded, or unresolved".format(key))
    if not reviewer or not reviewed_at or not reason:
        raise ValueError("{} needs reviewer_id, reviewed_at, and review_reason".format(key))
    try:
        timestamp = datetime.fromisoformat(reviewed_at.replace("Z", "+00:00"))
        if timestamp.tzinfo is None:
            raise ValueError
    except ValueError as exc:
        raise ValueError("{} reviewed_at must be an ISO-8601 timestamp with timezone".format(key)) from exc
    evidence = _json_cell(row, "review_evidence_json", list, key) if (row.get("review_evidence_json") or "").strip() else []
    verified = _json_cell(row, "verified_gates_json", dict, key) if (row.get("verified_gates_json") or "").strip() else {}
    tracks = _json_cell(row, "track_memberships_json", list, key) if (row.get("track_memberships_json") or "").strip() else []
    if not evidence or any(not isinstance(item, dict) or item.get("gate") not in GATES or
                           not isinstance(item.get("excerpt"), str) or not item["excerpt"].strip()
                           for item in evidence):
        raise ValueError("{} needs source evidence passages with a valid gate and nonempty excerpt".format(key))
    if decision == "accepted":
        if row.get("cohort") not in COHORTS:
            raise ValueError("{} accepted decision needs cohort employment or internship".format(key))
        if not (row.get("canonical_role") or "").strip():
            raise ValueError("{} accepted decision needs a reviewed canonical_role".format(key))
        if not tracks or any(track not in TRACKS for track in tracks) or len(tracks) != len(set(tracks)):
            raise ValueError("{} accepted decision needs unique validated track memberships".format(key))
        if set(verified) != set(GATES) or any(verified.get(gate) is not True for gate in GATES):
            raise ValueError("{} accepted decision must set every verified gate to true".format(key))
        cited = {item.get("gate") for item in evidence if isinstance(item, dict) and
                 item.get("gate") in GATES and isinstance(item.get("excerpt"), str) and item["excerpt"].strip()}
        if cited != set(GATES):
            raise ValueError("{} accepted decision needs a source excerpt for every gate".format(key))
    return {
        "posting_key": key,
        "source_id": str(row.get("source_id") or ""),
        "source_url": row.get("source_url") or "",
        "source_version_id": row.get("selected_version_id") or "",
        "source_raw_sha256": row.get("source_raw_sha256") or "",
        "policy_version": POLICY_VERSION,
        "decision": decision,
        "cohort": row.get("cohort") if decision == "accepted" else None,
        "canonical_role": (row.get("canonical_role") or "").strip() if decision == "accepted" else None,
        "track_memberships": sorted(tracks) if decision == "accepted" else [],
        "reviewer_id": reviewer,
        "reviewed_at": reviewed_at,
        "reason": reason,
        "verified_gates": verified,
        "evidence": evidence,
    }


def reconcile(screen_csv, reviewed_csv, output_dir):
    """Validate reviewed rows and create append-only v2 decisions plus counts."""
    with Path(screen_csv).open(encoding="utf-8-sig", newline="") as source:
        screen_reader = csv.DictReader(source)
        screen_columns = set(screen_reader.fieldnames or ())
        screen_rows = list(screen_reader)
    with Path(reviewed_csv).open(encoding="utf-8-sig", newline="") as source:
        review_reader = csv.DictReader(source)
        if not review_reader.fieldnames or not set(REVIEW_COLUMNS).issubset(review_reader.fieldnames):
            raise ValueError("Reviewed CSV is missing required review columns")
        if not screen_columns.issubset(review_reader.fieldnames):
            raise ValueError("Reviewed CSV is missing source screening columns")
        review_rows = list(review_reader)

    screen = {row["posting_key"]: row for row in screen_rows}
    if len(screen) != len(screen_rows):
        raise ValueError("Screen CSV contains duplicate posting keys")
    reviewed_keys = [row.get("posting_key") for row in review_rows]
    if len(reviewed_keys) != len(set(reviewed_keys)):
        raise ValueError("Reviewed CSV contains duplicate posting keys")
    unknown = set(reviewed_keys) - set(screen)
    if unknown:
        raise ValueError("Reviewed CSV contains unknown posting keys: " + ", ".join(sorted(unknown)[:5]))
    decisions = []
    for row in review_rows:
        key = row["posting_key"]
        source = screen[key]
        for field in screen_columns:
            if row.get(field) != source.get(field):
                raise ValueError("{} source screening/evidence field changed: {}".format(key, field))
        if not any((row.get(field) or "").strip() for field in REVIEW_COLUMNS):
            continue
        decisions.append(_decision(row))

    counts = Counter(d["decision"] for d in decisions)
    accepted = [d for d in decisions if d["decision"] == "accepted"]
    by_cohort = Counter(d["cohort"] for d in accepted)
    track_counts = Counter(track for d in accepted for track in d["track_memberships"])
    cohort_tracks = {cohort: dict(sorted(Counter(
        track for decision in accepted if decision["cohort"] == cohort
        for track in decision["track_memberships"]).items())) for cohort in sorted(COHORTS)}
    role_counts = {cohort: dict(sorted(Counter(
        decision["canonical_role"] for decision in accepted if decision["cohort"] == cohort).items()))
        for cohort in sorted(COHORTS)}
    total = len(screen)
    pending = total - len(decisions)
    complete = pending == 0 and counts["unresolved"] == 0
    summary = {
        "schema_version": "jobstreet-admission-review-summary-v2",
        "policy_version": POLICY_VERSION,
        "screen_sha256": _digest(screen_csv),
        "reviewed_csv_sha256": _digest(reviewed_csv),
        "source_posting_count": total,
        "reviewed_posting_count": len(decisions),
        "pending_review_count": pending,
        "accepted_employment_distinct_ids": by_cohort["employment"],
        "accepted_internship_distinct_ids": by_cohort["internship"],
        "excluded_distinct_ids": counts["excluded"],
        "unresolved_distinct_ids": counts["unresolved"] + pending,
        "exclusion_reason_counts": dict(sorted(Counter(
            d["reason"] for d in decisions if d["decision"] == "excluded").items())),
        "unresolved_reason_counts": dict(sorted(Counter(
            d["reason"] for d in decisions if d["decision"] == "unresolved").items())),
        "accepted_roles_by_cohort": role_counts,
        "accepted_track_memberships_by_cohort_overlapping": cohort_tracks,
        "accepted_track_memberships_overlapping": dict(sorted(track_counts.items())),
        "baseline_status": "reviewed" if complete else "review_required",
        "counts_are_distinct_by": "posting_key (one source ID counted once per cohort)",
        "limitations": [
            "Screen-only categories and keyword candidates are not accepted decisions.",
            "No cross-source or repost identity merges are inferred.",
            "A reviewed baseline does not establish representative market coverage or model adequacy.",
        ],
    }
    if complete:
        summary["accepted_employment_remaining_to_1000"] = max(0, 1000 - by_cohort["employment"])
        summary["accepted_employment_remaining_to_4000"] = max(0, 4000 - by_cohort["employment"])
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    decisions_path, summary_path = out / "admissions-v2.jsonl", out / "summary-v2.json"
    if decisions_path.exists() or summary_path.exists():
        raise FileExistsError("Refusing to replace existing review artifacts in {}".format(out))
    _write_new(decisions_path, lambda stream: stream.writelines(
        json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in decisions))
    _write_new(summary_path, lambda stream: stream.write(json.dumps(summary, ensure_ascii=False, indent=2) + "\n"))
    return summary


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    template = commands.add_parser("prepare-template", help="copy screen evidence into a new review template")
    template.add_argument("screen_csv", type=Path)
    template.add_argument("output_csv", type=Path)
    run = commands.add_parser("reconcile", help="validate reviewed decisions and write a distinct v2 artifact")
    run.add_argument("screen_csv", type=Path)
    run.add_argument("reviewed_csv", type=Path)
    run.add_argument("output_dir", type=Path)
    args = parser.parse_args(argv)
    try:
        result = (prepare_template(args.screen_csv, args.output_csv) if args.command == "prepare-template"
                  else reconcile(args.screen_csv, args.reviewed_csv, args.output_dir))
    except (OSError, ValueError) as exc:
        parser.exit(2, "error: {}\n".format(exc))
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
