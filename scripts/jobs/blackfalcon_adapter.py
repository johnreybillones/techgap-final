"""Offline import and normalization for blackfalcondata's JobStreet Actor."""
import hashlib
import json
import re
from datetime import datetime
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from .contracts import canonical_hash, canonical_json
from .registry import Registry

ACTOR_NAME = "blackfalcondata/jobstreet-scraper"
DERIVED_SCHEMA = "blackfalcon-jobstreet-derived-v1"


def _source_id_from_url(value):
    parsed = urlparse(str(value or ""))
    if parsed.scheme != "https" or not parsed.hostname or not parsed.hostname.lower().endswith("jobstreet.com"):
        return None
    match = re.fullmatch(r"/job/(\d+)/?", parsed.path)
    return match.group(1) if match else None


def _page_number(search_url, expected_query):
    parsed = urlparse(str(search_url or ""))
    if parsed.scheme != "https" or not parsed.hostname or not parsed.hostname.lower().endswith("jobstreet.com"):
        return None
    query_values = parse_qs(parsed.query)
    page = query_values.get("page", [None])[-1]
    keywords = query_values.get("keywords", [None])[-1]
    if not page or not page.isdigit() or int(page) < 1 or not keywords:
        return None
    if " ".join(keywords.casefold().split()) != " ".join(str(expected_query or "").casefold().split()):
        return None
    return int(page)


def normalize_item(payload, provenance):
    """Return validation, a derived legacy-compatible view, and raw provenance."""
    if not isinstance(payload, dict):
        return {"valid": False, "reasons": ["item_not_object"], "raw_payload": payload,
                "provenance": provenance, "posting_key": None, "derived": None, "page_number": None}
    reasons = []
    seek_id = payload.get("seekJobId")
    if seek_id is None or not re.fullmatch(r"\d+", str(seek_id)):
        reasons.append("missing_seek_job_id")
    url_id = _source_id_from_url(payload.get("canonicalUrl"))
    if url_id is None:
        reasons.append("missing_or_invalid_canonical_url")
    if seek_id is not None and url_id is not None and str(seek_id) != url_id:
        reasons.append("seek_id_url_mismatch")
    source_id = str(seek_id) if seek_id is not None and re.fullmatch(r"\d+", str(seek_id)) else None
    posting_key = "jobstreet:ph:" + source_id if source_id and url_id == source_id else None
    description = payload.get("descriptionMarkdown") or payload.get("description") or payload.get("descriptionHtml") or ""
    derived = {
        "schema_version": DERIVED_SCHEMA,
        "id": source_id,
        "url": payload.get("canonicalUrl"),
        "title": payload.get("title"),
        "company": payload.get("company"),
        "location": payload.get("location"),
        "workType": payload.get("employmentType"),
        "workArrangement": payload.get("workArrangement"),
        "postedAt_iso": payload.get("postedDate"),
        "description_text": description,
        "description_html": payload.get("descriptionHtml"),
        "detail_status": "full_details_requested" if payload.get("description") or payload.get("descriptionHtml") or payload.get("descriptionMarkdown") else "description_missing",
        "actor_job_id": payload.get("jobId"),
        "seek_job_id": source_id,
        "canonical_url": payload.get("canonicalUrl"),
        "search_url": payload.get("searchUrl"),
        "page_number": _page_number(payload.get("searchUrl"), (provenance or {}).get("query")),
    }
    return {"valid": not reasons, "reasons": reasons, "posting_key": posting_key,
            "source_id": source_id, "raw_payload": payload, "provenance": provenance,
            "raw_hash": hashlib.sha256(canonical_json(payload).encode("utf-8")).hexdigest(),
            "derived": derived, "page_number": derived["page_number"]}


def import_items(root, items, *, provenance):
    """Import a saved candidate dataset without network access or paid execution."""
    root = Path(root)
    registry = Registry(root)
    run_id = provenance.get("run_id")
    query_id = provenance.get("query_id")
    if not run_id or not query_id:
        raise ValueError("provenance_requires_run_and_query_ids")
    raw_dir = root / "raw" / run_id
    raw_dir.mkdir(parents=True, exist_ok=True)
    versions_before = len(registry.read_jsonl("versions.jsonl"))
    distinct_before = {row.get("posting_key") for row in registry.read_jsonl("postings.jsonl")}
    valid_count = invalid_count = 0
    for index, payload in enumerate(items):
        result = normalize_item(payload, provenance)
        raw_hash = result.get("raw_hash") or canonical_hash(payload)
        raw_file = Path("raw") / run_id / (raw_hash + ".json")
        envelope = {"payload": payload, "provenance": provenance,
                    "raw_payload_sha256": raw_hash, "candidate_actor": ACTOR_NAME}
        absolute = root / raw_file
        if not absolute.exists():
            absolute.write_text(json.dumps(envelope, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        raw_items = raw_dir / "items.jsonl"
        if not any(row.get("run_id") == run_id and row.get("dataset_item_id") == str(index)
                   for row in registry.read_jsonl(raw_items.relative_to(root).as_posix())):
            registry._append(raw_items.relative_to(root).as_posix(), {
                "run_id": run_id, "dataset_item_id": str(index), "raw_hash": raw_hash,
                "raw_file": raw_file.as_posix(), "payload": payload, "provenance": provenance,
                "identity_valid": result["valid"]})
        if not result["valid"]:
            invalid_count += 1
            invalid_rows = registry.read_jsonl("invalid_items.jsonl")
            if not any(row.get("run_id") == run_id and row.get("dataset_item_id") == str(index)
                       for row in invalid_rows):
                registry._append("invalid_items.jsonl", {"run_id": run_id, "query_id": query_id,
                    "dataset_item_id": str(index), "raw_hash": raw_hash, "raw_file": raw_file.as_posix(),
                    "reasons": result["reasons"], "actor": ACTOR_NAME,
                    "actor_id": provenance.get("actor_id"), "build_id": provenance.get("build_id"),
                    "dataset_id": provenance.get("dataset_id")})
            continue
        valid_count += 1
        key = result["posting_key"]
        derived = result["derived"]
        postings = registry.read_jsonl("postings.jsonl")
        if not any(row.get("posting_key") == key for row in postings):
            registry._append("postings.jsonl", {"posting_key": key, "source_id": result["source_id"],
                "source_url": derived["url"]})
        version_id = canonical_hash([key, derived])
        versions = registry.read_jsonl("versions.jsonl")
        if not any(row.get("version_id") == version_id for row in versions):
            registry._append("versions.jsonl", {"version_id": version_id, "posting_key": key,
                "raw_hash": raw_hash, "raw_file": raw_file.as_posix(),
                "description_hash": canonical_hash(derived.get("description_text") or ""),
                "fields": derived, "full_description": bool(derived.get("description_text")),
                "actor": ACTOR_NAME, "actor_id": provenance.get("actor_id"),
                "build_id": provenance.get("build_id"), "dataset_id": provenance.get("dataset_id")})
        observation_id = canonical_hash([run_id, str(index), raw_hash])
        if not any(row.get("observation_id") == observation_id for row in registry.read_jsonl("observations.jsonl")):
            registry._append("observations.jsonl", {"observation_id": observation_id,
                "posting_key": key, "version_id": version_id, "run_id": run_id,
                "dataset_id": provenance.get("dataset_id"), "dataset_item_id": str(index),
                "query_id": query_id, "raw_hash": raw_hash, "raw_file": raw_file.as_posix(),
                "actor": ACTOR_NAME, "actor_id": provenance.get("actor_id"),
                "build_id": provenance.get("build_id"), "build_number": provenance.get("build_number"),
                "search_url": derived.get("search_url"), "page_number": derived.get("page_number"),
                "captured_at": provenance.get("captured_at")})
    if not any(row.get("run_id") == run_id for row in registry.read_jsonl("runs.jsonl")):
        run = {key: provenance.get(key) for key in ("run_id", "dataset_id", "query_id", "actor_id", "actor",
                "build_id", "build_number", "started_at", "finished_at", "status", "provider_charge_usd",
                "charged_event_counts", "actual_run_options", "requested_run_options")}
        run.update({"actor": ACTOR_NAME, "returned_items": len(items), "import_status": "imported",
                    "imported_at": datetime.utcnow().isoformat() + "Z"})
        registry._append("runs.jsonl", run)
        registry._append("source_runs.jsonl", dict(run, billing_status="reconciled" if provenance.get("provider_charge_usd") is not None else "unknown"))
    new_keys = {row["posting_key"] for row in registry.read_jsonl("postings.jsonl")} - distinct_before
    return {"returned_rows": len(items), "valid_rows": valid_count, "invalid_rows": invalid_count,
            "distinct_source_ids": len(new_keys), "total_distinct_source_ids": len(registry.read_jsonl("postings.jsonl")),
            "versions": len(registry.read_jsonl("versions.jsonl")) - versions_before}
