"""Canonical serialization and source item validation."""
import hashlib
import json
from datetime import datetime
from decimal import Decimal, InvalidOperation
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
    if not isinstance(run, dict):
        return {"valid": False, "errors": ["run_not_object"]}
    errors = ["missing_" + field for field in required if not run.get(field)]
    forbidden = {"token", "authorization", "cookie", "password", "secret", "api_token"}
    def scan(value):
        if isinstance(value, dict):
            for key, child in value.items():
                if str(key).lower() in forbidden:
                    errors.append("credential_field_in_run_record")
                scan(child)
        elif isinstance(value, list):
            for child in value: scan(child)
    scan(run)
    return {"valid": not errors, "errors": errors}


def validate_run_metadata(metadata, *, run_id, query_id):
    if not isinstance(metadata, dict):
        return {"valid": False, "errors": ["run_metadata_not_object"]}
    errors = []
    if metadata.get("run_id") != run_id: errors.append("run_id_mismatch")
    if metadata.get("query_id") != query_id: errors.append("query_id_mismatch")
    for field in ("dataset_id", "actor_id", "build", "build_id", "started_at", "finished_at", "status"):
        if not metadata.get(field): errors.append("missing_" + field)
    if metadata.get("status") not in {"SUCCEEDED", "FAILED", "TIMED-OUT", "ABORTED"}:
        errors.append("nonterminal_or_unknown_provider_status")
    try:
        started = datetime.fromisoformat(str(metadata.get("started_at", "")).replace("Z", "+00:00"))
        finished = datetime.fromisoformat(str(metadata.get("finished_at", "")).replace("Z", "+00:00"))
        if started.tzinfo is None or finished.tzinfo is None or started >= finished:
            errors.append("invalid_run_time_interval")
    except (TypeError, ValueError):
        errors.append("invalid_run_time_interval")
    if metadata.get("provider_charge_usd") is not None:
        try:
            charge = Decimal(str(metadata["provider_charge_usd"]))
            if not charge.is_finite() or charge < 0: errors.append("invalid_provider_charge")
        except (InvalidOperation, TypeError, ValueError):
            errors.append("invalid_provider_charge")
    forbidden = {"token", "authorization", "cookie", "password", "secret", "api_token"}
    def scan(value):
        if isinstance(value, dict):
            for key, child in value.items():
                if str(key).lower() in forbidden: errors.append("credential_field_in_run_metadata")
                scan(child)
        elif isinstance(value, list):
            for child in value: scan(child)
    scan(metadata)
    return {"valid": not errors, "errors": errors}
