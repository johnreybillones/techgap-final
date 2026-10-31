"""Deterministic writer for a hash-linked, admission-only release."""
import hashlib
import json
import os
import sys
import uuid
from pathlib import Path

from .admission import POLICY_VERSION, decide_admission, reconcile_decisions
from .classify_jobs import classify_posting


def _sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _write(path, content):
    path = Path(path)
    temp = path.with_name(path.name + ".tmp-" + uuid.uuid4().hex)
    with temp.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(content)
    os.replace(str(temp), str(path))


def _jsonl(path):
    return [json.loads(line) for line in Path(path).read_text(encoding="utf-8").splitlines() if line.strip()]


def _canonical_hash(value):
    encoded = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def _validated_sources(source_frame, raw_release_id):
    source_frame = Path(source_frame)
    raw_root = source_frame.parent
    raw_manifest = json.loads((raw_root / "manifest.json").read_text(encoding="utf-8"))
    if raw_manifest.get("release_id") != raw_release_id:
        raise ValueError("raw_release_id_mismatch")
    if raw_manifest.get("source_membership_sha256") != _sha(source_frame):
        raise ValueError("raw_source_frame_hash_mismatch")
    rows = _jsonl(source_frame)
    if raw_manifest.get("distinct_source_id_count") != len(rows):
        raise ValueError("raw_source_count_mismatch")
    keys = [row.get("posting_key") for row in rows]
    if not rows or any(not key for key in keys) or len(keys) != len(set(keys)):
        raise ValueError("raw_source_frame_identity_invalid")
    for row in rows:
        relative = Path(row.get("selected_raw_file", ""))
        raw_path = (raw_root / relative).resolve()
        if raw_root.resolve() not in raw_path.parents or not raw_path.is_file():
            raise ValueError("selected_raw_file_missing_or_outside_release:" + row["posting_key"])
        fields = json.loads(raw_path.read_text(encoding="utf-8"))
        if _canonical_hash(fields) != row.get("selected_raw_hash"):
            raise ValueError("selected_raw_hash_mismatch:" + row["posting_key"])
        if not row.get("selected_version_id") or not row.get("count_unit_id"):
            raise ValueError("source_version_or_count_unit_missing:" + row["posting_key"])
    return rows, raw_manifest


def _complete_partial_rows(path):
    path = Path(path)
    if not path.is_file():
        return []
    raw = path.read_bytes()
    lines = raw.splitlines(keepends=True)
    complete = []
    valid_bytes = bytearray()
    for line in lines:
        if not line.endswith(b"\n"):
            break
        complete.append(json.loads(line.decode("utf-8")))
        valid_bytes.extend(line)
    if len(valid_bytes) != len(raw):
        temp = path.with_name(path.name + ".tmp-" + uuid.uuid4().hex)
        temp.write_bytes(valid_bytes)
        os.replace(str(temp), str(path))
    return complete


def run_admission_release(source_frame, output_dir, *, release_id, raw_release_id, extractor,
                          retriever, classifier, taxonomy_version, window_start, window_end,
                          runtime_metadata=None):
    source_frame = Path(source_frame)
    output = Path(output_dir)
    source_rows, raw_manifest = _validated_sources(source_frame, raw_release_id)
    raw_hash = _sha(source_frame)
    raw_manifest_hash = _sha(source_frame.parent / "manifest.json")
    model_versions = {"extractor": extractor.version, "retriever": retriever.version,
                      "classifier": classifier.version}
    run_config = {
        "release_id": release_id, "raw_release_id": raw_release_id,
        "raw_input_sha256": raw_hash,
        "policy_version": POLICY_VERSION, "taxonomy_version": taxonomy_version,
        "model_versions": model_versions, "runtime": runtime_metadata or {},
        "window_start": window_start, "window_end": window_end,
    }
    config_content = json.dumps(run_config, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    config_hash = hashlib.sha256(config_content.encode("utf-8")).hexdigest()
    config_path = output / "run_config.json"
    partial_path = output / "decisions.partial.jsonl"
    if output.exists():
        if not config_path.is_file():
            raise FileExistsError("output_release_exists_without_matching_run_config:" + str(output))
        if json.loads(config_path.read_text(encoding="utf-8")) != run_config:
            raise ValueError("existing_admission_run_config_mismatch")
        existing_manifest_path = output / "manifest.json"
        if existing_manifest_path.is_file():
            finished = json.loads(existing_manifest_path.read_text(encoding="utf-8"))
            if finished.get("run_config_sha256") != config_hash:
                raise ValueError("completed_admission_run_config_mismatch")
            for name, expected in finished.get("artifacts", {}).items():
                if _sha(output / name) != expected:
                    raise ValueError("completed_admission_artifact_hash_mismatch:" + name)
            return finished
    else:
        output.mkdir(parents=True)
        _write(config_path, config_content)

    source_by_key = {row["posting_key"]: row for row in source_rows}
    decisions_by_key = {}
    for decision in _complete_partial_rows(partial_path):
        key = decision.get("posting_key")
        source = source_by_key.get(key)
        if source is None or key in decisions_by_key:
            raise ValueError("partial_admission_source_key_invalid_or_duplicate")
        for name in ("selected_version_id", "selected_raw_hash", "count_unit_id"):
            if decision.get(name) != source.get(name):
                raise ValueError("partial_admission_source_link_mismatch:" + key)
        decisions_by_key[key] = decision

    for index, source in enumerate(source_rows, 1):
        if source["posting_key"] in decisions_by_key:
            continue
        raw_path = source_frame.parent / source["selected_raw_file"]
        fields = json.loads(raw_path.read_text(encoding="utf-8"))
        case = classify_posting({**source, "fields": fields}, extractor=extractor, retriever=retriever,
                                classifier=classifier, taxonomy_version=taxonomy_version,
                                window_start=window_start, window_end=window_end)
        decision = decide_admission(case)
        with partial_path.open("a", encoding="utf-8", newline="\n") as handle:
            handle.write(json.dumps(decision, ensure_ascii=False, sort_keys=True) + "\n")
            handle.flush()
            os.fsync(handle.fileno())
        decisions_by_key[source["posting_key"]] = decision
        print("P2A completed {}/{} source postings".format(len(decisions_by_key), len(source_rows)),
              file=sys.stderr, flush=True)

    decisions = [decisions_by_key[row["posting_key"]] for row in source_rows]
    summary, units = reconcile_decisions(decisions)
    if not summary["equation_reconciles"]:
        raise RuntimeError("admission_source_equation_did_not_reconcile")
    decisions_path = output / "decisions.jsonl"
    units_path = output / "count_units.jsonl"
    _write(decisions_path, "".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in decisions))
    _write(units_path, "".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in units))
    manifest = {
        "schema_version": "job-admission-release-v1", "release_id": release_id,
        "raw_release_id": raw_release_id, "raw_input_file": source_frame.name,
        "raw_input_sha256": raw_hash, "policy_version": POLICY_VERSION,
        "taxonomy_version": taxonomy_version,
        "raw_manifest_sha256": raw_manifest_hash,
        "run_config_sha256": config_hash,
        "raw_source_count": raw_manifest.get("distinct_source_id_count"),
        "model_versions": model_versions,
        "runtime": runtime_metadata or {},
        "summary": summary,
        "artifacts": {"decisions.jsonl": _sha(decisions_path), "count_units.jsonl": _sha(units_path),
                      "run_config.json": _sha(config_path)},
        "count_unit_membership_sha256": _sha(units_path),
        "domain_accuracy": "not_measured",
    }
    manifest_path = output / "manifest.json"
    _write(manifest_path, json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n")
    manifest["release_sha256"] = hashlib.sha256(
        "".join(manifest["artifacts"][name] for name in sorted(manifest["artifacts"])).encode("ascii")
    ).hexdigest()
    _write(manifest_path, json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n")
    partial_path.unlink(missing_ok=True)
    return manifest

