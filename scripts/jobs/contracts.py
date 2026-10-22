"""Canonical serialization and source item validation."""
import hashlib
import json
from urllib.parse import urlparse


def canonical_json(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def canonical_hash(value):
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def validate_item(item):
    reasons = []
    if not isinstance(item, dict):
        return {"valid": False, "reasons": ["item_not_object"]}
    source_id = item.get("id")
    url = item.get("url")
    if source_id is None or not str(source_id).strip():
        reasons.append("missing_source_id")
    parsed = urlparse(str(url or ""))
    if (parsed.scheme != "https" or not parsed.hostname or not parsed.hostname.lower().endswith("jobstreet.com")
            or not parsed.path.rstrip("/").endswith("/" + str(source_id))):
        reasons.append("missing_or_inconsistent_source_url")
    return {"valid": not reasons, "reasons": reasons}


def validate_config(config):
    errors = []
    if not isinstance(config, dict) or config.get("schema_version") != "job-collection-v1":
        errors.append("unsupported_config_schema")
    if isinstance(config, dict):
        if not config.get("window_start") or not config.get("window_end"):
            errors.append("missing_frozen_window")
        if not isinstance(config.get("requested_target"), int) or config.get("requested_target", 0) < 1:
            errors.append("invalid_requested_target")
    return {"valid": not errors, "errors": errors}


def validate_run(run):
    required = ("run_id", "actor_id", "build", "dataset_id", "started_at", "finished_at", "status")
    errors = ["missing_" + field for field in required if not run.get(field)]
    if any(key.lower() in {"token", "authorization", "cookie", "password"} for key in run):
        errors.append("credential_field_in_run_record")
    return {"valid": not errors, "errors": errors}
