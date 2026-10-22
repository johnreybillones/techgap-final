"""Freeze and verify immutable raw-evidence release manifests."""
import hashlib
import json
from pathlib import Path

from .registry import _jsonl


def _sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


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
    audit = {"raw_unique_source_keys": len(latest), "terminal_counts": terminal_counts,
        "eligible_count_units": len(rows), "equation_reconciles": len(latest) == sum(terminal_counts.values()),
        "run_count": len(_jsonl(root / "runs.jsonl")), "observation_count": len(_jsonl(root / "observations.jsonl")),
        "version_count": len(versions), "invalid_item_count": len(_jsonl(root / "invalid_items.jsonl")),
        "query_ids": sorted({row.get("query_id") for row in _jsonl(root / "observations.jsonl")}),
        "limitations": ["No live collection was executed.", "Coverage and representativeness are not established."]}
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
        "reported_charge_usd": reported_charge_usd,
        "release_status": "complete_target" if len(rows) >= requested_target else "development_only_shortfall",
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
    frame = root / manifest.get("membership_file", "")
    if not frame.is_file() or _sha(frame) != manifest.get("membership_sha256"):
        errors.append("membership_hash_mismatch")
    return {"valid": not errors, "errors": errors}
