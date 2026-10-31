"""Freeze and verify immutable raw-evidence release manifests."""
import hashlib
import json
import os
import re
import shutil
import uuid
from pathlib import Path

from .registry import _jsonl


def _sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _atomic_json(path, value):
    path = Path(path)
    temp = path.with_name(path.name + ".tmp-" + uuid.uuid4().hex)
    temp.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(str(temp), str(path))


def _atomic_jsonl(path, rows):
    path = Path(path)
    temp = path.with_name(path.name + ".tmp-" + uuid.uuid4().hex)
    temp.write_text("".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in rows), encoding="utf-8")
    os.replace(str(temp), str(path))


def _source_frame(root):
    postings = {row["posting_key"]: row for row in _jsonl(root / "postings.jsonl")}
    versions = {}
    for row in _jsonl(root / "versions.jsonl"):
        versions[row["version_id"]] = row
    observations = _jsonl(root / "observations.jsonl")
    run_metadata = {}
    for name in ("runs.jsonl", "source_runs.jsonl"):
        path = root / name
        for row in _jsonl(path) if path.is_file() else []:
            if row.get("run_id"):
                run_metadata.setdefault(row["run_id"], {}).update({key: value for key, value in row.items()
                                                                    if value not in (None, "")})
    by_posting = {}
    for row in observations:
        by_posting.setdefault(row["posting_key"], []).append(row)
    frame = []
    for posting_key, posting in sorted(postings.items()):
        linked = by_posting.get(posting_key, [])
        available = [versions[row["version_id"]] for row in linked if row.get("version_id") in versions]
        if not available:
            raise ValueError("posting_without_available_version:" + posting_key)
        selected = max(available, key=lambda row: (row.get("full_description") is True,
            len(str((row.get("fields") or {}).get("description_text") or
                    (row.get("fields") or {}).get("description_html") or ""))))
        fields = selected.get("fields") or {}
        text = str(fields.get("description_text") or fields.get("description_html") or "")
        plain_length = len(re.sub(r"<[^>]*>", " ", text).strip())
        detail = str(fields.get("detail_status") or "").lower()
        if not text.strip():
            completeness = "absent"
        elif selected.get("full_description") is False or any(flag in detail for flag in ("teaser", "partial", "truncated")) or re.search(r"(?:\.\.\.|…|read more|show more)\s*$", text, re.I):
            completeness = "suspected_truncation"
        elif plain_length < 300:
            completeness = "short"
        else:
            completeness = "uncertain_completeness"
        raw_file = root / selected["raw_file"]
        if not raw_file.is_file():
            raise ValueError("selected_raw_file_missing:" + posting_key)
        raw_hash = selected.get("raw_hash")
        # Older registries use a canonical JSON hash rather than a byte hash;
        # existence plus registry linkage is retained and both IDs are explicit.
        frame.append({
            "posting_key": posting_key,
            "source_id": posting["source_id"],
            "source_url": posting["source_url"],
            "count_unit_id": posting.get("count_unit_id", posting_key),
            "group_members": posting.get("group_members", [posting_key]),
            "selected_version_id": selected["version_id"],
            "selected_raw_hash": raw_hash,
            "selected_raw_file": selected["raw_file"],
            "original_title": fields.get("title"),
            "employer": fields.get("company"),
            "publication_date": fields.get("postedAt_iso"),
            "location": fields.get("location"),
            "work_type": fields.get("workType"),
            "work_arrangements": fields.get("workArrangements"),
            "capture_date": fields.get("scrapedAt"),
            "full_description_available": bool(fields.get("description_text") or fields.get("description_html")),
            "description_characters": plain_length,
            "description_completeness": completeness,
            "source_field_flags": {name: fields.get(name) not in (None, "", []) for name in
                ("title", "company", "url", "description_text", "description_html", "postedAt_iso",
                 "scrapedAt", "location", "workType", "workArrangements", "salary")},
            "run_observations": [{"observation_id": row["observation_id"], "query_id": row.get("query_id"),
                "run_id": row.get("run_id"), "dataset_id": run_metadata.get(row.get("run_id"), {}).get("dataset_id"),
                "actor_id": run_metadata.get(row.get("run_id"), {}).get("actor_id"),
                "actor": run_metadata.get(row.get("run_id"), {}).get("actor"),
                "build_id": run_metadata.get(row.get("run_id"), {}).get("build_id"),
                "build": run_metadata.get(row.get("run_id"), {}).get("build")}
                for row in linked],
            "alternate_version_ids": sorted({row["version_id"] for row in available if row["version_id"] != selected["version_id"]}),
            "observation_ids": sorted(row["observation_id"] for row in linked),
            "run_ids": sorted({row["run_id"] for row in linked}),
            "query_ids": sorted({row["query_id"] for row in linked}),
            "diagnostics": {"provider_full_description_flag": selected.get("full_description"),
                            "detail_status": fields.get("detail_status"), "detail_source": fields.get("detail_source"),
                            "version_count": len({row["version_id"] for row in available})},
        })
    return frame


def freeze_raw_release(root, *, release_id, phase, requested_target, window_start, window_end,
                       reported_charge_usd):
    """Create the Plan 1 raw-v2 handoff without consulting legacy admission."""
    root = Path(root)
    frame = _source_frame(root)
    frame_path = root / "source_frame.jsonl"
    _atomic_jsonl(frame_path, frame)
    observations = _jsonl(root / "observations.jsonl")
    invalid = _jsonl(root / "invalid_items.jsonl")
    source_runs = _jsonl(root / "source_runs.jsonl")
    has_live = bool(source_runs)
    unknown_billing = has_live and any(row.get("provider_charge_usd") is None or row.get("billing_status") == "unknown"
                                       for row in source_runs)
    limitations = ["Coverage and representativeness are not established."]
    if unknown_billing:
        limitations.append("Provider billing is not reconciled; dependent paid execution and final economics are blocked.")
    audit = {
        "schema_version": "job-collection-audit-v2",
        "raw_observation_count": len(observations),
        "distinct_source_id_count": len(frame),
        "invalid_item_count": len(invalid),
        "source_frame_unique": len({row["posting_key"] for row in frame}) == len(frame),
        "all_observations_accounted_for": all(row.get("posting_key") in {item["posting_key"] for item in frame}
                                                for row in observations),
        "all_invalid_items_have_raw_link": all(row.get("run_id") and row.get("query_id") and row.get("raw_hash")
            and row.get("raw_file") and (root / row["raw_file"]).is_file() for row in invalid),
        "billing_status": "not_reconciled" if unknown_billing else "reconciled" if has_live else "not_applicable",
        "limitations": limitations,
    }
    _atomic_json(root / "collection_audit.json", audit)
    artifacts = {}
    for path in sorted(p for p in root.rglob("*") if p.is_file() and p.name != "manifest.json"):
        artifacts[path.relative_to(root).as_posix()] = _sha(path)
    manifest = {
        "schema_version": "job-collection-raw-v2",
        "release_id": release_id,
        "phase": phase,
        "requested_target": requested_target,
        "raw_observation_count": len(observations),
        "distinct_source_id_count": len(frame),
        "invalid_item_count": len(invalid),
        "window_start": window_start,
        "window_end": window_end,
        "report_timezone": "Asia/Manila",
        "count_unit_policy_version": "source-id-with-evidenced-repost-groups-v1",
        "source_membership_file": "source_frame.jsonl",
        "source_membership_sha256": _sha(frame_path),
        "artifact_hashes": artifacts,
        "admission_status": "not_classified",
        "admission_feedback": None,
        "reported_charge_usd": reported_charge_usd,
        "billing_status": audit["billing_status"],
        "release_status": "raw_ready" if audit["source_frame_unique"] and audit["all_observations_accounted_for"]
            and audit["all_invalid_items_have_raw_link"] else "invalid_handoff",
        "limitations": limitations,
    }
    _atomic_json(root / "manifest.json", manifest)
    return manifest


def migrate_raw_release(source_root, destination_root, **release_options):
    """Copy immutable collection evidence into a new raw-v2 release directory."""
    source = Path(source_root)
    destination = Path(destination_root)
    if destination.exists():
        raise FileExistsError(str(destination))
    destination.mkdir(parents=True)
    try:
        for name in ("collection_config.json", "query_registry.json", "runs.jsonl", "source_runs.jsonl",
                     "postings.jsonl", "versions.jsonl", "observations.jsonl", "invalid_items.jsonl",
                     "collection_checks.jsonl", "repost_candidates.jsonl"):
            path = source / name
            if path.is_file():
                shutil.copy2(str(path), str(destination / name))
        if (source / "raw").is_dir():
            shutil.copytree(str(source / "raw"), str(destination / "raw"))
        else:
            raise ValueError("missing_raw_evidence_directory")
        return freeze_raw_release(destination, **release_options)
    except Exception:
        shutil.rmtree(str(destination), ignore_errors=True)
        raise


def attach_admission_feedback(root, feedback):
    """Validate and link immutable P2A feedback into an existing raw-v2 release."""
    root = Path(root)
    manifest = json.loads((root / "manifest.json").read_text(encoding="utf-8"))
    if manifest.get("schema_version") != "job-collection-raw-v2":
        raise ValueError("feedback_requires_raw_v2_release")
    if feedback.get("raw_input_sha256") != manifest.get("source_membership_sha256"):
        raise ValueError("raw_input_hash_mismatch")
    total = sum(int(feedback.get(name, 0)) for name in ("accepted_employment", "accepted_internship", "rejected"))
    if total != int(feedback.get("input_postings", -1)) or total != manifest.get("distinct_source_id_count"):
        raise ValueError("source_decision_equation_mismatch")
    required = ("release_id", "release_path", "release_sha256", "policy_version", "model_versions",
                "taxonomy_version", "count_unit_membership_sha256")
    missing = [name for name in required if not feedback.get(name)]
    if missing:
        raise ValueError("missing_feedback_fields:" + ",".join(missing))
    _atomic_json(root / "admission_feedback.json", feedback)
    manifest["artifact_hashes"]["admission_feedback.json"] = _sha(root / "admission_feedback.json")
    manifest["admission_status"] = "classified"
    manifest["admission_feedback"] = {
        "release_id": feedback["release_id"], "release_path": feedback["release_path"],
        "release_sha256": feedback["release_sha256"], "policy_version": feedback["policy_version"],
    }
    _atomic_json(root / "manifest.json", manifest)
    return manifest


def freeze_release(root, *, release_id, phase, requested_target, window_start, window_end, reported_charge_usd):
    root = Path(root)
    # Rebuild membership from the latest recorded decision per source key.
    admissions = _jsonl(root / "admission.jsonl")
    latest = {}
    for row in admissions:
        latest[row["posting_key"]] = row
    versions = _jsonl(root / "versions.jsonl")
    version_by_key = {}
    for row in versions:
        version_by_key.setdefault(row["posting_key"], []).append(row)
    membership = []
    for key, decision in sorted(latest.items()):
        if decision.get("state") != "eligible":
            continue
        candidates = version_by_key.get(key, [])
        if not candidates:
            continue
        selected = candidates[-1]
        membership.append({"count_unit_id": key, "source_id": key.rsplit(":", 1)[-1],
            "selected_version": selected["version_id"], "raw_hash": selected["raw_hash"],
            "window_start": window_start, "window_end": window_end, "admission": decision})
    frame = root / "eligible_frame.jsonl"
    frame.write_text("".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in membership), encoding="utf-8")
    rows = _jsonl(frame)
    terminal_counts = {state: sum(row.get("state") == state for row in latest.values())
                       for state in ("eligible", "excluded", "unresolved")}
    source_runs = _jsonl(root / "source_runs.jsonl")
    has_live_evidence = any(row.get("actor_id") or row.get("provider_status") or row.get("status") in
                            {"SUCCEEDED", "FAILED", "TIMED-OUT", "ABORTED"} for row in source_runs)
    unknown_billing = any(row.get("provider_charge_usd") is None or row.get("billing_status") == "unknown"
                          for row in source_runs) if has_live_evidence else False
    limitations = []
    if not has_live_evidence:
        limitations.append("No verified live acquisition evidence is present; imported payload provenance may be incomplete.")
    if unknown_billing:
        limitations.append("At least one live run has unknown billing; financial reconciliation is incomplete.")
    limitations.extend(["Coverage and representativeness are not established.",
                        "Admission rules and source descriptions have not been validated for collection-wide accuracy."])
    audit = {"raw_unique_source_keys": len(latest), "terminal_counts": terminal_counts,
        "eligible_count_units": len(rows), "equation_reconciles": len(latest) == sum(terminal_counts.values()),
        "run_count": len(_jsonl(root / "runs.jsonl")), "observation_count": len(_jsonl(root / "observations.jsonl")),
        "version_count": len(versions), "invalid_item_count": len(_jsonl(root / "invalid_items.jsonl")),
        "query_ids": sorted({row.get("query_id") for row in _jsonl(root / "observations.jsonl")}),
        "has_live_evidence": has_live_evidence, "financially_reconciled": not unknown_billing,
        "limitations": limitations}
    (root / "collection_audit.json").write_text(json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    artifacts = {}
    for path in sorted(p for p in root.rglob("*") if p.is_file() and p.name != "manifest.json"):
        artifacts[path.relative_to(root).as_posix()] = _sha(path)
    manifest = {"schema_version": "job-collection-v1", "release_id": release_id, "phase": phase,
        "requested_target": requested_target, "achieved_eligible_count": len(rows), "window_start": window_start,
        "window_end": window_end, "report_timezone": "Asia/Manila",
        "count_unit_policy_version": "source-id-with-evidenced-repost-groups-v1",
        "admission_policy_version": "explicit-entry-junior-v1", "membership_file": "eligible_frame.jsonl",
        "membership_sha256": _sha(frame), "artifact_hashes": artifacts,
        "reported_charge_usd": (sum(float(row["provider_charge_usd"]) for row in source_runs
                                     if row.get("provider_charge_usd") is not None) if has_live_evidence else reported_charge_usd),
        "financially_reconciled": audit["financially_reconciled"],
        "release_status": ("financial_reconciliation_pending" if unknown_billing else
                           "complete_target" if len(rows) >= requested_target else "development_only_shortfall"),
        "limitations": audit["limitations"]}
    (root / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return manifest


def validate_release(root):
    root = Path(root)
    manifest_path = root / "manifest.json"
    if not manifest_path.exists():
        return {"valid": False, "errors": ["missing_manifest"]}
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    errors = []
    for name, expected in manifest.get("artifact_hashes", {}).items():
        path = root / name
        if not path.is_file() or _sha(path) != expected:
            errors.append("artifact_hash_mismatch:" + name)
    membership_name = manifest.get("source_membership_file") or manifest.get("membership_file", "")
    membership_hash = manifest.get("source_membership_sha256") or manifest.get("membership_sha256")
    frame = root / membership_name
    if not frame.is_file() or _sha(frame) != membership_hash:
        errors.append("membership_hash_mismatch")
    return {"valid": not errors, "errors": errors}
