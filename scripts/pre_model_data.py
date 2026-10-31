#!/usr/bin/env python3
"""Prepare immutable saved JobStreet and syllabus evidence for GLiNER2 labeling.

This module intentionally does not import the legacy admission pipeline.  Its
outputs preserve source identity and require independently checked annotations
before any model-native export is produced.
"""
from __future__ import annotations

import argparse
import difflib
import hashlib
import html
from html.parser import HTMLParser
import json
import os
from pathlib import Path
import platform
import re
import shutil
import sys
import tempfile
import unicodedata
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
JOB_ROOTS = (
    "data/job_collections/jobstreet-2026-10-recovered-reconciliation-raw-v2",
    "data/job_collections/jobstreet-2026-10-six-query-pilot-20261023",
    "data/job_collections/blackfalcon-data-engineer-paginated-20261023",
    "data/job_collections/jobstreet-2026-10-game-four-query-proposal",
)
TEXT_VERSION = "pre-model-text-v1"
LABELS = ("technical_task", "technical_knowledge", "tool_technology")
TRACKS = ("bscs_is", "bscs_game", "bsit_network", "bsit_web")
SEED = "techgap-pre-model-v1"
RULES_VERSION = "premodel-preparation-v4"
MIN_LINK_CHARS = 40
MODEL_REVISION = "f9634218e53580c56edf0de97ca1a7d3f1c2354e"  # same pin as scripts/legacy_pipeline/contracts.py
CHECKPOINT = ROOT / "models" / "gliner2-base-v1" / "model.safetensors"


def checkpoint_sha():
    return file_sha(CHECKPOINT) if CHECKPOINT.is_file() else None



def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha_bytes(value):
    return hashlib.sha256(value).hexdigest()


def sha_obj(value):
    return sha_bytes(canonical(value).encode("utf-8"))


def file_sha(path):
    return sha_bytes(Path(path).read_bytes())


def write_jsonl(path, rows):
    data = "".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in rows)
    atomic_text(path, data)


def atomic_text(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(path.name + ".tmp-" + next(tempfile._get_candidate_names()))
    with temp.open("w", encoding="utf-8", newline="\n") as stream:
        stream.write(data)
    os.replace(temp, path)


def read_jsonl(path, issues, stage, *, required=True):
    path = Path(path)
    if not path.exists():
        if required:
            issues.append(issue(stage, "missing_file", str(path)))
        return []
    rows = []
    with path.open(encoding="utf-8") as stream:
        for line_number, line in enumerate(stream, 1):
            if not line.strip():
                continue
            try:
                value = json.loads(line)
                if not isinstance(value, dict):
                    raise ValueError("line_not_object")
                rows.append((line_number, value))
            except (json.JSONDecodeError, ValueError) as exc:
                issues.append(issue(stage, "malformed_jsonl", str(path), line_number=line_number, evidence=str(exc)))
    return rows


def issue(stage, reason, source_path=None, **extra):
    result = {"stage": stage, "reason_code": reason, "retry_eligible": False}
    if source_path is not None:
        result["source_path"] = str(source_path)
    result.update(extra)
    return result


def parse_time(value):
    if not isinstance(value, str) or not value.strip():
        return None
    try:
        dt = datetime.fromisoformat(value.strip().replace("Z", "+00:00"))
        if dt.tzinfo is None:
            return None
        return dt.astimezone(timezone.utc)
    except ValueError:
        return None


def norm_field(value):
    if value is None:
        return None
    return re.sub(r"\s+", " ", str(value).strip()).upper()


class VisibleHTML(HTMLParser):
    BLOCKS = {"h1", "h2", "h3", "h4", "h5", "h6", "p", "div", "br", "li", "tr", "td"}
    HIDDEN = {"hidden", "aria-hidden"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts = []
        self.ignored = 0

    VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track", "wbr"}

    def handle_starttag(self, tag, attrs):
        if tag in self.VOID:  # void tags never send an end tag, so they must not touch the ignore counter
            if not self.ignored and tag in self.BLOCKS:
                self.parts.append("\n")
            return
        attrs = dict(attrs)
        if tag in ("script", "style", "nav") or self.ignored:
            self.ignored += 1
            return
        style = (attrs.get("style") or "").replace(" ", "").lower()
        if "hidden" in attrs or attrs.get("aria-hidden", "").lower() == "true" or "display:none" in style or "visibility:hidden" in style:
            self.ignored += 1
            return
        if tag in self.BLOCKS:
            self.parts.append("\n")

    def handle_startendtag(self, tag, attrs):
        if tag in self.VOID:
            self.handle_starttag(tag, attrs)
        # other self-closing tags carry no content and open no region

    def handle_endtag(self, tag):
        if tag in self.VOID:
            return
        if self.ignored:
            self.ignored -= 1
        elif tag in self.BLOCKS:
            self.parts.append("\n")

    def handle_data(self, data):
        if not self.ignored:
            self.parts.append(data)

    def text(self):
        raw = "".join(self.parts)
        lines = []
        for line in raw.splitlines():
            line = re.sub(r"[\t\r\f\v ]+", " ", html.unescape(line)).strip()
            if line and (not lines or line != lines[-1]):
                lines.append(line)
        return "\n".join(lines)


def visible_html(value):
    parser = VisibleHTML()
    try:
        parser.feed(value or "")
        parser.close()
    except Exception:
        return ""
    return parser.text()


def token_sequence(value):
    return re.findall(r"[a-z0-9]+", re.sub(r"\s+", " ", value or "").lower())


def clean_text(value):
    value = unicodedata.normalize("NFC", value or "").replace("\r\n", "\n").replace("\r", "\n")
    lines = [re.sub(r"[\t\f\v ]+", " ", x).strip() for x in value.split("\n")]
    out = []
    for line in lines:
        if line and (not out or line != out[-1]):
            out.append(line)
    return "\n".join(out)


def job_id_from_url(value):
    if not isinstance(value, str):
        return None
    match = re.fullmatch(r"https?://(?:www\.)?ph\.jobstreet\.com/job/(\d+)/?", value.strip(), re.I)
    return match.group(1) if match else None


def _manifest_hashes(root, manifest):
    data = manifest or {}
    hashes = data.get("artifact_hashes") or {}
    hashes.update(data.get("inputs", {}).get("blackfalcon_validated_file_hashes", {}))
    hashes.update(data.get("blackfalcon_validated_file_hashes", {}))
    return {str(k).replace("\\", "/"): v for k, v in hashes.items() if isinstance(v, str)}


def load_job_roots(repo_root, cutoff, issues):
    postings_by_id = {}
    release_stats = {}
    inputs = {}
    for relative in JOB_ROOTS:
        root = repo_root / relative
        if not root.is_dir():
            issues.append(issue("jobs", "missing_release_root", relative))
            continue
        manifest_path = root / "manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8")) if manifest_path.exists() else {}
        hashes = _manifest_hashes(root, manifest)
        source_blocked = False
        for name in ("observations.jsonl", "versions.jsonl", "postings.jsonl", "source_frame.jsonl"):
            path = root / name
            if path.exists():
                inputs[path.relative_to(repo_root).as_posix()] = file_sha(path)
                if name in ("observations.jsonl", "versions.jsonl", "postings.jsonl", "source_frame.jsonl"):
                    declared = hashes.get(name)
                    if declared and declared != file_sha(path):
                        # Blackfalcon's reconciliation manifest validates original
                        # inputs; recognize that it may intentionally differ from
                        # subsequently generated joined indexes.
                        issues.append(issue("jobs", "manifest_index_hash_mismatch", relative + "/" + name,
                                            declared=declared, actual=file_sha(path)))
                        if name != "source_frame.jsonl" or manifest.get("schema") == "actor-pilot-reconciliation-manifest-v1":
                            source_blocked = True
            elif name != "source_frame.jsonl":
                issues.append(issue("jobs", "missing_index", relative + "/" + name))
                source_blocked = True
        if source_blocked:  # a source with failed integrity checks never enters a release
            release_stats[relative] = {"observations_in_index": 0, "observations_in_cutoff": 0, "versions_in_index": 0,
                "postings_in_index": 0, "blocked_from_training": True, "source_frame_count": 0}
            continue
        observation_rows = read_jsonl(root / "observations.jsonl", issues, "jobs")
        version_rows = read_jsonl(root / "versions.jsonl", issues, "jobs")
        posting_rows = read_jsonl(root / "postings.jsonl", issues, "jobs")
        versions = {row.get("version_id"): row for _, row in version_rows}
        index_postings = {row.get("posting_key"): row for _, row in posting_rows}
        run_path = root / "runs.jsonl"
        run_lookup = {r.get("run_id"): r for _, r in read_jsonl(run_path, issues, "jobs", required=False)} if run_path.exists() else {}
        raw_methods = ((manifest.get("integrity") or {}).get("raw_hash_method") or
                       (manifest.get("raw_hash") or {}).get("method") or
                       manifest.get("raw_hash_method"))
        included_observations = 0
        for line_number, obs in observation_rows:
            version = versions.get(obs.get("version_id"))
            posting = index_postings.get(obs.get("posting_key"))
            if not version or not posting or version.get("posting_key") != obs.get("posting_key"):
                issues.append(issue("jobs", "observation_link_mismatch", relative + "/observations.jsonl",
                                    line_number=line_number, observation_id=obs.get("observation_id")))
                continue
            raw_rel = obs.get("raw_file") or version.get("raw_file")
            raw_path = (root / str(raw_rel)).resolve() if raw_rel else None
            if not raw_path or not raw_path.is_file():
                issues.append(issue("jobs", "raw_file_missing", relative + "/observations.jsonl",
                                    line_number=line_number, raw_file=raw_rel))
                source_blocked = True
                continue
            actual = file_sha(raw_path)
            declared = hashes.get(str(raw_rel).replace("\\", "/"))
            if declared and declared != actual:
                issues.append(issue("jobs", "raw_byte_hash_mismatch", relative + "/" + str(raw_rel),
                                    expected=declared, actual=actual))
                source_blocked = True
                continue
            if obs.get("raw_hash") and raw_methods in ("sha256_bytes", "raw_bytes", "bytes") and obs["raw_hash"] != actual:
                issues.append(issue("jobs", "raw_hash_mismatch", relative + "/" + str(raw_rel),
                                    method=raw_methods, expected=obs["raw_hash"], actual=actual))
                source_blocked = True
                continue
            fields = version.get("fields") if isinstance(version.get("fields"), dict) else {}
            source_id = str(posting.get("source_id") or "")
            key = str(obs.get("posting_key") or "")
            key_match = re.fullmatch(r"jobstreet:ph:(\d+)", key)
            url = fields.get("canonical_url") or fields.get("url") or posting.get("source_url")
            url_id = job_id_from_url(url)
            blackfalcon = "blackfalcon" in str(obs.get("actor") or version.get("actor") or relative).lower()
            seek_id = fields.get("seek_job_id") if blackfalcon else None
            candidates = {key_match.group(1) if key_match else None, url_id,
                         str(seek_id) if seek_id not in (None, "") else None,
                         source_id if source_id.isdigit() else None}
            candidates.discard(None)
            if not key_match or not url_id or len(candidates) != 1:
                reason = "invalid_posting_key" if not key_match else "canonical_url_id_mismatch"
                if blackfalcon and seek_id not in (None, "") and str(seek_id) != url_id:
                    reason = "blackfalcon_seek_job_id_url_mismatch"
                issues.append(issue("jobs", reason, relative + "/observations.jsonl", line_number=line_number,
                                    posting_key=key, source_id=source_id, url=url,
                                    seek_job_id=seek_id, actor_job_id=fields.get("actor_job_id") if blackfalcon else None))
                continue
            actor = obs.get("actor") or version.get("actor") or obs.get("actor_id") or version.get("actor_id")
            version.setdefault("_source_root", relative)
            version.setdefault("_source_hash", actual)
            version.setdefault("_raw_file", str(raw_rel))
            version.setdefault("_fields", fields)
            raw_data = json.loads(raw_path.read_text(encoding="utf-8"))
            version.setdefault("_provider_raw", raw_data)
            when_raw = obs.get("captured_at") or fields.get("scrapedAt")
            if not when_raw and obs.get("run_id"):
                run_row = run_lookup.get(obs.get("run_id"), {})
                when_raw = next((run_row.get(k) for k in ("captured_at", "finished_at", "started_at", "run_at") if run_row.get(k)), None)
            when = parse_time(when_raw)
            if when is None:
                issues.append(issue("jobs", "capture_time_unknown", relative + "/observations.jsonl",
                                    line_number=line_number, observation_id=obs.get("observation_id")))
                continue  # no proven observation time, so it cannot be shown to precede the cutoff
            if when > cutoff:
                continue
            included_observations += 1
            key_id = key_match.group(1)
            entry = postings_by_id.setdefault(key_id, {"id": key_id, "observations": [], "versions": {}, "posting_records": [], "roots": set()})
            entry["observations"].append({"release_root": relative, "line_number": line_number,
                "observation_id": obs.get("observation_id"), "posting_key": key, "version_id": obs.get("version_id"),
                "observed_at": when.isoformat().replace("+00:00", "Z") if when else None,
                "observed_at_source": "captured_at" if obs.get("captured_at") else "scrapedAt_or_run" if when_raw else "unknown",
                "actor": actor, "actor_id": obs.get("actor_id") or version.get("actor_id"), "run_id": obs.get("run_id"),
                "dataset_id": obs.get("dataset_id") or version.get("dataset_id"), "query_id": obs.get("query_id"),
                "page_number": obs.get("page_number", fields.get("page_number")), "raw_file": str(raw_rel), "raw_hash": obs.get("raw_hash")})
            entry["versions"][version["version_id"]] = version
            entry["posting_records"].append({"release_root": relative, **posting})
            entry["roots"].add(relative)
        release_stats[relative] = {"observations_in_index": len(observation_rows), "observations_in_cutoff": included_observations,
            "versions_in_index": len(version_rows), "postings_in_index": len(posting_rows), "blocked_from_training": source_blocked,
            "source_frame_count": len(read_jsonl(root / "source_frame.jsonl", issues, "jobs", required=False))}
    return postings_by_id, release_stats, inputs


def select_job(entry):
    ranked = []
    obs_by_version = {}
    for obs in entry["observations"]:
        obs_by_version.setdefault(obs["version_id"], []).append(obs)
    for version_id, version in entry["versions"].items():
        fields = version.get("_fields", {})
        raw = version.get("_provider_raw", {})
        html_value = fields.get("description_html")
        text_value = fields.get("description_text")
        text = visible_html(html_value) if isinstance(html_value, str) else ""
        source_field = "description_html" if text else "description_text" if isinstance(text_value, str) and text_value else None
        if not text and source_field == "description_text":
            text = clean_text(text_value)
        detail = str(fields.get("detail_status") or "").lower()
        flags = []
        if re.search(r"partial|teaser|truncat", detail) or raw.get("full_description") is False or version.get("full_description") is False:
            flags.append("explicit_partial_or_teaser")
        if re.search(r"(?:\.\.\.|…|read more|show more)\s*$", text, re.I):
            flags.append("ending_truncation_marker")
        timestamps = [parse_time(x.get("observed_at")) for x in obs_by_version.get(version_id, [])]
        timestamps = [x for x in timestamps if x]
        latest = max(timestamps) if timestamps else None
        ranked.append({"version_id": version_id, "version": version, "fields": fields, "text": text,
                       "source_field": source_field, "flags": flags, "latest": latest,
                       "nonempty": bool(text.strip()), "observations": obs_by_version.get(version_id, [])})
    clean = [r for r in ranked if r["nonempty"] and not r["flags"]]
    if clean:
        selected = max(clean, key=lambda r: (r["latest"] or datetime.min.replace(tzinfo=timezone.utc), r["version_id"]))
        text_status, reason = "apparently_usable", "most_recent_nonempty_unflagged_version"
    else:
        nonempty = [r for r in ranked if r["nonempty"]]
        if nonempty:
            selected = max(nonempty, key=lambda r: (len(r["text"]), r["latest"] or datetime.min.replace(tzinfo=timezone.utc), r["version_id"]))
            text_status, reason = "partial_or_uncertain", "longest_nonempty_fallback"
        else:
            selected = max(ranked, key=lambda r: (r["latest"] or datetime.min.replace(tzinfo=timezone.utc), r["version_id"]))
            text_status, reason = "absent", "no_nonempty_version"
    return selected, ranked, text_status, reason


def split_job_passages(doc_id, text, heading=None):
    passages = []
    for match in re.finditer(r"[^\n]+", text):
        value = match.group().strip()
        if not value:
            continue
        start = match.start() + len(match.group()) - len(match.group().lstrip())
        end = start + len(value)
        if re.fullmatch(r"[^.!?]{1,100}", value) and value.isupper() and len(value.split()) <= 10:
            heading = value
            continue
        passage_id = sha_obj({"document_id": doc_id, "field": "description", "field_item_id": str(start),
                              "document_start": start, "document_end": end, "text_transform_version": TEXT_VERSION})
        passages.append({"passage_id": passage_id, "document_id": doc_id, "source_type": "job",
            "field": "description", "field_item_id": str(start), "text": value,
            "document_start": start, "document_end": end,
            "source_references": [{"document_id": doc_id, "field": "description", "start": start, "end": end}],
            "quality_flags": [], "source_aliases": [], "heading_context": heading, "split_group_id": None})
    return passages


def syllabus_track(track, course_code, title):
    value = (track or "").strip()
    title_norm = re.sub(r"\s+", " ", (title or "")).strip().lower()
    table = {
        "Common (IT & CS)": list(TRACKS),
        "CS Core & Electives": ["bscs_is", "bscs_game"],
        "IT Core & Electives": ["bsit_network", "bsit_web"],
        "CS - Intelligent Systems": ["bscs_is"],
        "CS - Game Development": ["bscs_game"],
        "IT - Network Technology": ["bsit_network"],
        "IT - Web Development": ["bsit_web"],
    }
    if value in table:
        return table[value], "resolved"
    if value == "General & Foundational":
        if "number theory" in title_norm:
            return ["bscs_is", "bscs_game"], "resolved"
        if title_norm in {"living in the it era", "it application tools in business"}:
            return ["bsit_network", "bsit_web"], "resolved"
    return [], "applicability_unresolved"


def build_syllabi(repo_root, issues, input_hashes):
    documents, passages, warnings = [], [], []
    paths = sorted(p for p in (repo_root / "data/syllabi").rglob("*.pdf.json") if p.name != "summary.json")
    records = []
    for path in paths:
        rel = path.relative_to(repo_root).as_posix()
        raw_bytes = path.read_bytes()
        input_hashes[rel] = sha_bytes(raw_bytes)
        try:
            obj = json.loads(raw_bytes.decode("utf-8"))
            if not isinstance(obj, dict):
                raise ValueError("root_not_object")
        except Exception as exc:
            issues.append(issue("syllabus", "malformed_json", rel, evidence=str(exc)))
            continue
        source = obj.get("source") if isinstance(obj.get("source"), dict) else {}
        type_warnings = []
        for key in ("course_code", "track", "course_description", "status"):
            if key in obj and obj[key] is not None and not isinstance(obj[key], str):
                type_warnings.append("invalid_type:" + key)
        if not isinstance(obj.get("course_learning_outcomes"), list):
            type_warnings.append("invalid_type:course_learning_outcomes")
        if not isinstance(obj.get("learning_plan"), list):
            type_warnings.append("invalid_type:learning_plan")
        if not isinstance(obj.get("issues"), (list, dict, type(None))):
            type_warnings.append("invalid_type:issues")
        code, track = obj.get("course_code"), obj.get("track")
        title = obj.get("course_title")
        applied_tracks, applicability = syllabus_track(track, code, title)
        family_code = re.sub(r"(?:LA|LC)$", "", norm_field(code) or "")
        family = sha_obj({"course_code": family_code, "applicable_tracks": applied_tracks or ["unresolved"]})
        doc_id = "syllabus:" + sha_bytes(rel.encode("utf-8"))
        statements = []
        desc = obj.get("course_description")
        if isinstance(desc, str) and desc.strip():
            statements.append({"field": "course_description", "item_id": "course_description", "text": desc.strip(),
                               "order": 0, "period": None, "source_pages": (source.get("field_pages") or {}).get("course_description", [])})
        seen_outcome_ids = set()
        clo_end = 0
        for i, outcome in enumerate(obj.get("course_learning_outcomes") or []):
            if not isinstance(outcome, dict):
                type_warnings.append("invalid_clo_item")
                continue
            item_id = outcome.get("id") or str(i)
            if item_id in seen_outcome_ids:
                type_warnings.append("duplicate_outcome_id:" + str(item_id))
            seen_outcome_ids.add(item_id)
            if isinstance(outcome.get("text"), str) and outcome["text"].strip():
                statements.append({"field": "course_learning_outcomes", "item_id": str(item_id), "text": outcome["text"].strip(),
                    "order": len(statements), "period": None, "source_pages": outcome.get("source_pages") or (source.get("field_pages") or {}).get("course_learning_outcomes", [])})
        clo_end = len(statements)
        plan = obj.get("learning_plan") or []
        if not plan:
            type_warnings.append("missing_learning_plan")
        for pi, period in enumerate(plan):
            if not isinstance(period, dict):
                type_warnings.append("invalid_learning_plan_item")
                continue
            period_name = period.get("period") or period.get("title") or str(pi)
            for key in ("topic_learning_outcomes", "additional_text"):
                values = period.get(key) or []
                if not isinstance(values, list):
                    type_warnings.append("invalid_learning_plan_field:" + key)
                    continue
                for i, item in enumerate(values):
                    if isinstance(item, str):
                        text, item_id, pages = item, str(i), period.get("source_pages", [])
                    elif isinstance(item, dict):
                        text, item_id, pages = item.get("text"), str(item.get("id") or i), item.get("source_pages") or period.get("source_pages", [])
                    else:
                        type_warnings.append("invalid_learning_plan_statement")
                        continue
                    if isinstance(text, str) and text.strip():
                        statements.append({"field": key, "item_id": item_id, "text": text.strip(),
                                           "order": len(statements), "period": period_name, "source_pages": pages})
        # A learning-plan copy of a CLO is one example. Keep the CLO's earlier
        # canonical position and attach each exact copy as an additional alias.
        canonical_by_text = {}
        for statement in statements[:clo_end]:
            exact = re.sub(r"\s+", " ", unicodedata.normalize("NFC", statement["text"])).strip()
            canonical_by_text.setdefault(exact, statement)
        filtered = statements[:clo_end]
        for statement in statements[clo_end:]:
            exact = re.sub(r"\s+", " ", unicodedata.normalize("NFC", statement["text"])).strip()
            canonical = canonical_by_text.get(exact)
            if canonical is not None:
                canonical.setdefault("inline_aliases", []).append(statement)
            else:
                canonical_by_text[exact] = statement
                filtered.append(statement)
        statements = filtered
        full_parts, positions = [], []
        cursor = 0
        for statement in statements:
            if full_parts:
                full_parts.append("\n\n")
                cursor += 2
            text = statement["text"]
            start, end = cursor, cursor + len(text)
            positions.append({**statement, "start": start, "end": end})
            full_parts.append(text)
            cursor = end
        full_text = "".join(full_parts)
        document = {"document_id": doc_id, "source_type": "syllabus", "source_path": rel,
            "source_sha256": sha_bytes(raw_bytes), "source_pdf": source.get("filename"), "source_pdf_sha256": source.get("sha256"),
            "extractor_version": source.get("extractor_version"), "field_pages": source.get("field_pages", {}),
            "course_code": code, "course_code_normalized": norm_field(code), "course_title": title,
            "track": track, "track_normalized": norm_field(track), "applicable_tracks": applied_tracks,
            "applicability_state": applicability, "course_family_key": family_code,
            "course_family_group": family, "status": obj.get("status"), "issues": obj.get("issues"),
            "field_type_warnings": type_warnings, "completeness": {"description": bool(desc),
                "clo_count": len(obj.get("course_learning_outcomes") or []), "learning_plan_count": len(plan)},
            "full_text": full_text, "text_transform_version": TEXT_VERSION,
            "placements": {"year_level": obj.get("year_level"), "semester": obj.get("semester")}, "split_group_id": family}
        documents.append(document)
        if applicability != "resolved":
            warnings.append({"document_id": doc_id, "reason": "applicability_unresolved"})
        for placement in positions:
            norm_text = re.sub(r"\s+", " ", unicodedata.normalize("NFC", placement["text"])).strip()
            pid = sha_obj({"document_id": doc_id, "field": placement["field"], "field_item_id": placement["item_id"],
                "document_start": placement["start"], "document_end": placement["end"], "text_transform_version": TEXT_VERSION})
            passages.append({"passage_id": pid, "document_id": doc_id, "source_type": "syllabus",
                "field": placement["field"], "field_item_id": placement["item_id"], "text": placement["text"],
                "document_start": placement["start"], "document_end": placement["end"],
                "source_references": [{"source_path": rel, "source_sha256": document["source_sha256"],
                    "field": placement["field"], "field_item_id": placement["item_id"],
                    "start": placement["start"], "end": placement["end"], "period": placement["period"],
                    "order": placement["order"], "source_pages": placement["source_pages"]}],
                "quality_flags": sorted(set(type_warnings)),
                "source_aliases": [{"source_path": rel, "source_sha256": document["source_sha256"],
                    "field": alias["field"], "field_item_id": alias["item_id"], "start": placement["start"],
                    "end": placement["end"], "period": alias["period"], "order": alias["order"],
                    "source_pages": alias["source_pages"]} for alias in placement.get("inline_aliases", [])],
                "split_group_id": family, "normalized_text_key": norm_text})
        records.append({"document": document, "passages": passages[-len(positions):] if positions else []})
    # Connect globally identical training text before splitting.
    by_text = {}
    docs_by_id = {d["document_id"]: d for d in documents}
    for passage in passages:
        key = re.sub(r"\s+", " ", unicodedata.normalize("NFC", passage["text"])).strip()
        by_text.setdefault(key, []).append(passage)
    for same in by_text.values():
        if len(same) < 2:
            continue
        ids = sorted({p["document_id"] for p in same})
        combined_group = sha_bytes("\n".join(ids).encode("utf-8"))
        for p in same:
            p["split_group_id"] = combined_group
            docs_by_id[p["document_id"]]["split_group_id"] = combined_group
        # Keep all exact-source pointers under a canonical primary passage.
        same.sort(key=lambda p: (p["document_id"], p["field"], p["field_item_id"], p["document_start"]))
        primary = same[0]
        for alias in same[1:]:
            primary["source_aliases"].extend(alias["source_references"])
            alias["_deduplicated_into"] = primary["passage_id"]
    passages = [p for p in passages if not p.get("_deduplicated_into")]
    return documents, passages, warnings, len(paths)


def make_chunks(passage):
    words = list(re.finditer(r"\S+", passage["text"]))
    if len(words) <= 384:
        return [{"chunk_id": passage["passage_id"], "text": passage["text"], "chunk_start": 0,
                 "chunk_end": len(passage["text"]), "token_range": [0, len(words)]}]
    output = []
    start = 0
    while start < len(words):
        last = min(start + 384, len(words))
        a, b = words[start].start(), words[last - 1].end()
        output.append({"chunk_id": sha_obj({"passage_id": passage["passage_id"], "chunk_start": a,
                                             "chunk_end": b, "text_transform_version": TEXT_VERSION}),
                       "text": passage["text"][a:b], "chunk_start": a, "chunk_end": b,
                       "token_range": [start, last]})
        if last == len(words):
            break
        start = last - 64
    return output


def _syllabus_issue_warning(obj):
    return "needs_review" if obj.get("status") == "needs_review" else None


def split_for_group(group_id):
    bucket = int.from_bytes(hashlib.sha256((SEED + ":" + group_id).encode("utf-8")).digest()[:8], "big") % 100
    return "train" if bucket < 70 else "val" if bucket < 80 else "test"


def add_connectivity_edges(passages, documents, links):
    """Union source groups for exact shared text while retaining separate records."""
    parent = {d["document_id"]: d["document_id"] for d in documents}
    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x
    def union(a, b):
        a, b = find(a), find(b)
        if a != b:
            parent[max(a, b)] = min(a, b)
    for a, members in links.items():
        for b in members:
            union(a, b)
    by_course_family = {}
    for doc in documents:
        if doc["source_type"] == "syllabus":
            key = doc.get("course_family_key"), tuple(doc.get("applicable_tracks", []))
            by_course_family.setdefault(key, []).append(doc["document_id"])
    for members in by_course_family.values():
        for other in members[1:]:
            union(members[0], other)
    text_docs = {}
    for passage in passages:
        key = re.sub(r"\s+", " ", unicodedata.normalize("NFC", passage["text"])).strip()
        text_docs.setdefault(key, set()).add(passage["document_id"])
    for members in text_docs.values():
        members = sorted(members)
        for other in members[1:]:
            union(members[0], other)
    components = {}
    for doc_id in parent:
        components.setdefault(find(doc_id), []).append(doc_id)
    group_ids = {doc_id: sha_bytes("\n".join(sorted(members)).encode("utf-8"))
                 for members in components.values() for doc_id in members}
    for doc in documents:
        doc["split_group_id"] = group_ids[doc["document_id"]]
    for passage in passages:
        passage["split_group_id"] = group_ids[passage["document_id"]]
    return group_ids


def prepare(release_id, cutoff_text, output_root, repo_root=ROOT):
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{0,99}", release_id):
        raise ValueError("invalid_release_id")
    cutoff = parse_time(cutoff_text)
    if cutoff is None:
        raise ValueError("cutoff_must_be_absolute_utc_timestamp")
    issues = []
    input_hashes = {}
    jobs, release_stats, job_input_hashes = load_job_roots(repo_root, cutoff, issues)
    input_hashes.update(job_input_hashes)
    documents, passages = [], []
    selected_counts = {"apparently_usable": 0, "partial_or_uncertain": 0, "absent": 0}
    for job_id, entry in sorted(jobs.items()):
        selected, candidates, text_status, reason = select_job(entry)
        fields, text = selected["fields"], selected["text"]
        selected_counts[text_status] += 1
        flags = []
        if selected["version"].get("full_description") is not None:
            provider_full = selected["version"].get("full_description")
        else:
            provider_full = selected["_provider_raw"].get("full_description")
        if provider_full is not None and not isinstance(provider_full, bool):
            flags.append("invalid_full_description_type")
        if selected["source_field"] is None:
            flags.append("description_missing")
            issues.append(issue("jobs", "missing_description", selected["version"].get("_raw_file"), document_id="jobstreet:ph:" + job_id))
        html_value, text_value = fields.get("description_html"), fields.get("description_text")
        if html_value and text_value:
            html_text = visible_html(html_value)
            a, b = token_sequence(html_text), token_sequence(text_value)
            ratio = difflib.SequenceMatcher(None, a, b, autojunk=False).ratio() if a or b else 1.0
            if ratio < .90:
                flags.append("html_text_disagreement")
        page_values = {x.get("page_number") for x in entry["observations"]}
        if None in page_values:
            flags.append("page_number_missing")
        if len(page_values - {None}) > 1:
            flags.append("page_number_conflict")
        observations = sorted(entry["observations"], key=lambda x: (x.get("observation_id") or "", x.get("release_root") or ""))
        if len({x.get("actor_id") or x.get("actor") for x in observations}) > 1:
            flags.append("cross_actor_overlap")
        selected_observations = selected["observations"]
        max_observed = max((x["observed_at"] for x in selected_observations if x.get("observed_at")), default=None)
        source_root = selected["version"]["_source_root"]
        source_hash = selected["version"]["_source_hash"]
        doc_id = "jobstreet:ph:" + job_id
        candidate_rows = []
        ranked_sorted = sorted(candidates, key=lambda x: (x["version_id"] != selected["version_id"], x["version_id"]))
        for rank, candidate in enumerate(ranked_sorted, 1):
            candidate_rows.append({"version_id": candidate["version_id"], "source_root": candidate["version"]["_source_root"],
                "raw_file": candidate["version"]["_raw_file"], "source_sha256": candidate["version"]["_source_hash"],
                "latest_included_observation": candidate["latest"].isoformat().replace("+00:00", "Z") if candidate["latest"] else None,
                "text_characters": len(candidate["text"]), "flags": candidate["flags"], "rank": rank,
                "selected": candidate["version_id"] == selected["version_id"],
                "selection_reason": reason if candidate["version_id"] == selected["version_id"] else None})
        doc = {"document_id": doc_id, "source_type": "job", "source_path": source_root + "/" + selected["version"]["_raw_file"],
            "source_sha256": source_hash, "source_roots": sorted(entry["roots"]), "source_id": job_id,
            "posting_key": "jobstreet:ph:" + job_id, "original_title": fields.get("title"), "company": fields.get("company"),
            "url": fields.get("canonical_url") or fields.get("url"), "location": fields.get("location"),
            "work_type": fields.get("workType"), "work_arrangement": fields.get("workArrangements", fields.get("workArrangement")),
            "salary": {"present": "salary" in fields, "value": fields.get("salary")},
            "dates": {k: {"original": fields.get(src), "parsed_utc": parse_time(fields.get(src)).isoformat().replace("+00:00", "Z") if parse_time(fields.get(src)) else None,
                "parse_status": "parsed" if parse_time(fields.get(src)) else "unparsed_or_absent"} for k, src in
                (("publication", "postedAt_iso"), ("scraped", "scrapedAt"))},
            "text_status": text_status, "requirement_set_complete": "unverified" if text_status == "apparently_usable" else False,
            "full_description_provider_flag": provider_full, "full_text": text, "text_transform_version": TEXT_VERSION,
            "selected_version_id": selected["version_id"], "selected_raw_file": selected["version"]["_raw_file"],
            "selected_source_root": source_root, "selected_source_field": selected["source_field"],
            "selected_observed_at": max_observed, "selection_reason": reason, "version_candidates": candidate_rows,
            "alternate_version_ids": sorted(v for v in entry["versions"] if v != selected["version_id"]),
            "versions": [{"version_id": v, "source_root": r["version"]["_source_root"], "raw_file": r["version"]["_raw_file"],
                          "source_sha256": r["version"]["_source_hash"]} for v, r in sorted(((r["version_id"], r) for r in candidates))],
            "observations": observations, "quality_flags": sorted(set(flags)),
            "eligibility_state": "unresolved", "relevance_state": "unresolved", "seniority_state": "unresolved",
            "track_state": "unresolved", "split_group_id": None}
        documents.append(doc)
        passages.extend(split_job_passages(doc_id, text))
    syll_docs, syll_passages, syll_warnings, syllabus_count = build_syllabi(repo_root, issues, input_hashes)
    documents.extend(syll_docs)
    passages.extend(syll_passages)
    # Job leakage groups: exact description links across IDs; near duplicates only
    # when normalized employer and title agree as specified by the plan.
    job_docs = [d for d in documents if d["source_type"] == "job"]
    links = {d["document_id"]: {d["document_id"]} for d in job_docs}
    exact_jobs = {}
    title_company_jobs = {}
    for doc in job_docs:
        body = doc["full_text"]
        if not body:
            continue
        exact_key = re.sub(r"\s+", " ", unicodedata.normalize("NFC", body)).strip()
        exact_jobs.setdefault(exact_key, []).append(doc)
        title_key = (norm_field(doc.get("company")), norm_field(doc.get("original_title")))
        if all(title_key):
            title_company_jobs.setdefault(title_key, []).append(doc)
    for same in exact_jobs.values():
        for i, a in enumerate(same):
            for b in same[i + 1:]:
                links[a["document_id"]].add(b["document_id"])
                links[b["document_id"]].add(a["document_id"])
    for same in title_company_jobs.values():
        for i, a in enumerate(same):
            for b in same[i + 1:]:
                if difflib.SequenceMatcher(None, a["full_text"], b["full_text"], autojunk=False).ratio() >= .90:
                    links[a["document_id"]].add(b["document_id"])
                    links[b["document_id"]].add(a["document_id"])
    # Connected components for both job and syllabus groups, plus identical text.
    # Union-find handles transitive near duplicate and syllabus/text aliases.
    parent = {doc["document_id"]: doc["document_id"] for doc in documents}
    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x
    def union(a, b):
        a, b = find(a), find(b)
        if a != b:
            parent[max(a, b)] = min(a, b)
    for doc in documents:
        if doc["source_type"] == "syllabus":
            fam = doc.get("course_family_group")
            for other in documents:
                if other["source_type"] == "syllabus" and other.get("course_family_group") == fam:
                    union(doc["document_id"], other["document_id"])
    for a, members in links.items():
        for b in members:
            union(a, b)
    passage_text_docs = {}
    for passage in passages:
        normalized = re.sub(r"\s+", " ", unicodedata.normalize("NFC", passage["text"])).strip()
        if len(normalized) < MIN_LINK_CHARS: continue  # headings like "About the role" must not chain unrelated postings
        passage_text_docs.setdefault(normalized, set()).add(passage["document_id"])
    for members in passage_text_docs.values():
        members = sorted(members)
        for other in members[1:]:
            union(members[0], other)
    comp = {}
    for doc_id in parent:
        comp.setdefault(find(doc_id), []).append(doc_id)
    group_id_for = {doc_id: sha_bytes("\n".join(sorted(ids)).encode("utf-8")) for ids in comp.values() for doc_id in ids}
    for doc in documents:
        doc["split_group_id"] = group_id_for[doc["document_id"]]
    for passage in passages:
        passage["split_group_id"] = group_id_for[passage["document_id"]]
    # One annotation queue row per distinct chunk. Exact content across documents
    # has already been linked into one split group; retain all lineage references.
    passages.sort(key=lambda x: x["passage_id"])
    documents.sort(key=lambda x: x["document_id"])
    queue = []
    queue_seen = {}
    document_by_id = {d["document_id"]: d for d in documents}
    for passage in passages:
        for chunk in make_chunks(passage):
            key = re.sub(r"\s+", " ", unicodedata.normalize("NFC", chunk["text"])).strip()
            queue_id = chunk["chunk_id"]
            row = {"queue_id": queue_id, "kind": "span", "passage_id": passage["passage_id"],
                "document_id": passage["document_id"], "source_type": passage["source_type"],
                "source_path": document_by_id[passage["document_id"]]["source_path"],
                "source_hash": document_by_id[passage["document_id"]]["source_sha256"],
                "text": chunk["text"], "text_sha256": sha_bytes(chunk["text"].encode("utf-8")),
                "passage_text": passage["text"], "document_start": passage["document_start"] + chunk["chunk_start"],
                "document_end": passage["document_start"] + chunk["chunk_end"], "chunk_start": chunk["chunk_start"],
                "chunk_end": chunk["chunk_end"], "heading_context": passage.get("heading_context"),
                "quality_flags": passage.get("quality_flags", []), "source_status": document_by_id[passage["document_id"]].get("status"),
                "applicability_state": document_by_id[passage["document_id"]].get("applicability_state"),
                "text_status": document_by_id[passage["document_id"]].get("text_status"),
                "source_references": passage.get("source_references", []) + passage.get("source_aliases", []),
                "permitted_labels": list(LABELS), "split_group_id": passage["split_group_id"],
                "processing_instructions": "Use exact text only; annotate technical spans and language; preserve source qualifications."}
            if key in queue_seen:
                existing = queue_seen[key]
                existing["source_references"].extend(row["source_references"])
                if row["document_id"] < existing["document_id"]:
                    lineage = existing["source_references"]
                    existing.update({k: row[k] for k in ("document_id", "source_type", "source_path", "source_hash", "passage_id", "document_start", "document_end")})
                    existing["source_references"] = lineage
            else:
                queue_seen[key] = row
    queue = sorted(queue_seen.values(), key=lambda x: x["queue_id"])
    # Job decision queue is distinct from span queue.
    for doc in [d for d in documents if d["source_type"] == "job"]:
        source_hash = doc["source_sha256"]
        queue.append({"queue_id": sha_obj({"kind": "job", "document_id": doc["document_id"], "source_hash": source_hash,
                                            "rule_version": RULES_VERSION}),
            "kind": "job", "document_id": doc["document_id"], "source_type": "job", "source_path": doc["source_path"],
            "source_hash": source_hash, "title": doc.get("original_title"), "text": doc.get("full_text", ""),
            "company": doc.get("company"), "location": doc.get("location"), "work_type": doc.get("work_type"),
            "work_arrangement": doc.get("work_arrangement"),
            "text_sha256": sha_bytes(doc.get("full_text", "").encode("utf-8")), "quality_flags": doc["quality_flags"],
            "text_status": doc["text_status"], "observations": doc["observations"], "versions": doc["versions"],
            "permitted_labels": ["relevance", "tracks", "cohort", "ph_eligibility"],
            "split_group_id": doc["split_group_id"], "processing_instructions": "Decide relevance/tracks/cohort/PH eligibility from title and description; query is provenance only."})
    queue.sort(key=lambda x: (x["kind"], x["queue_id"]))
    exclusions = [x for x in issues if x["reason_code"] in ("capture_time_unknown", "missing_description")]
    release = Path(output_root) / release_id
    if release.exists():
        existing_path = release / "manifest.json"
        if existing_path.exists():
            existing = json.loads(existing_path.read_text(encoding="utf-8"))
            if existing.get("input_hashes") != input_hashes or existing.get("rules_version") != RULES_VERSION or existing.get("cutoff_utc") != cutoff_text:
                raise FileExistsError("release_id_exists_with_different_inputs_or_rules:" + str(release))
            print(release)
            return release
        raise FileExistsError(str(release))
    release.parent.mkdir(parents=True, exist_ok=True)
    temp = Path(tempfile.mkdtemp(prefix=release_id + ".tmp-", dir=release.parent))
    try:
        write_jsonl(temp / "documents.jsonl", documents)
        write_jsonl(temp / "passages.jsonl", passages)
        write_jsonl(temp / "annotation_queue.jsonl", queue)
        write_jsonl(temp / "issues.jsonl", sorted(issues, key=lambda x: (x.get("stage", ""), x.get("reason_code", ""), x.get("source_path", ""), x.get("line_number", 0))))
        prompt_text = "Prompts and schemas are versioned in docs/plan/PREMODEL_DATA_PREPARATION_PLAN_2026-10-24.md, sections D1-D3. Agents must cite exact source offsets and keep unresolved decisions explicit."
        atomic_text(temp / "prompts.txt", prompt_text + "\n")
        outputs = {p.name: file_sha(p) for p in sorted(temp.iterdir()) if p.is_file()}
        counts = {"job_documents": len(jobs), "syllabus_documents": len(syll_docs), "syllabus_json_files": syllabus_count,
            "passages": len(passages), "queue_items": len(queue), "job_decisions_queued": sum(q["kind"] == "job" for q in queue),
            "span_decisions_queued": sum(q["kind"] == "span" for q in queue), "selected_job_text_status": selected_counts,
            "source_roots": release_stats, "applicability_warnings": len(syll_warnings), "issues": len(issues)}
        manifest = {"schema_version": "pre-model-release-v1", "release_id": release_id,
            "created_at_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "cutoff_utc": cutoff.isoformat().replace("+00:00", "Z"), "input_hashes": input_hashes,
            "rules_version": RULES_VERSION, "text_transform_version": TEXT_VERSION,
            "prompts_sha256": file_sha(temp / "prompts.txt"), "entity_labels": list(LABELS),
            "model_id": "fastino/gliner2-base-v1", "model_revision": MODEL_REVISION, "model_weights_sha256": checkpoint_sha(),
            "prepare_python_version": platform.python_version(),
            "counts": counts, "exclusions_and_warnings": exclusions + syll_warnings,
            "split_method": "connected source groups and stable SHA-256 bucket", "split_seed": SEED,
            "split_buckets": {"train": "0-69", "val": "70-79", "test": "80-99"},
            "outputs": outputs, "training_ready": False, "training_ready_reasons": ["AI decisions and independent checks are pending"]}
        atomic_text(temp / "manifest.json", json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n")
        os.replace(temp, release)
    except Exception:
        shutil.rmtree(temp, ignore_errors=True)
        raise
    print(release)
    return release


def load_release(release):
    def rows(name):
        path = release / name
        return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()] if path.exists() else []
    return rows


def validate_job_decision(row, document):
    required = {"document_id", "source_hash", "relevance", "relevance_basis", "tracks", "cohort", "ph_eligibility",
                "curated_role_id", "evidence", "reason", "agent", "model", "configuration", "prompt_version"}
    if not required.issubset(row): return "missing_fields"
    if row["document_id"] != document["document_id"] or row["source_hash"] != document["source_sha256"]: return "source_hash_or_id_mismatch"
    if row["relevance"] not in ("relevant", "irrelevant", "unresolved"): return "invalid_relevance"
    if row["relevance_basis"] not in ("title", "description", "both", "conflict", "insufficient"): return "invalid_relevance_basis"
    if row["cohort"] not in ("employment", "internship", "unresolved"): return "invalid_cohort"
    if row["ph_eligibility"] not in ("yes", "no", "unresolved"): return "invalid_ph_eligibility"
    if not isinstance(row["tracks"], list) or any(x not in TRACKS for x in row["tracks"]): return "invalid_tracks"
    if row["curated_role_id"] is not None: return "curated_role_not_available"
    return validate_evidence(row.get("evidence"), document.get("original_title", ""), document.get("full_text", ""), None)


def validate_evidence(items, title, text, passage=None):
    if not isinstance(items, list): return "invalid_evidence"
    for e in items:
        if not isinstance(e, dict): return "invalid_evidence_item"
        field = e.get("field")
        source = title if field == "title" else text if field in ("description", "full_text") else None
        start, end, mention = e.get("start"), e.get("end"), e.get("text")
        if source is None or not isinstance(start, int) or not isinstance(end, int) or not isinstance(mention, str): return "invalid_evidence_reference"
        if start < 0 or end < start or end > len(source) or source[start:end] != mention: return "evidence_span_mismatch"
    return None


def validate_span(row, queue_item):
    required = {"passage_id", "source_type", "text_sha256", "language", "spans", "passage_complete", "technical_content",
                "agent", "model", "configuration", "prompt_version"}
    if not required.issubset(row): return "missing_fields"
    if row["passage_id"] != queue_item["passage_id"] or row["text_sha256"] != queue_item["text_sha256"]: return "source_hash_or_id_mismatch"
    if row["source_type"] != queue_item["source_type"]: return "source_type_mismatch"
    if row["language"] not in ("english", "non_english", "uncertain"): return "invalid_language"
    if row["technical_content"] not in ("present", "absent", "unclear"): return "invalid_technical_content"
    if row["prompt_version"] != "technical-spans-v1": return "prompt_version_mismatch"
    if not isinstance(row["spans"], list) or not isinstance(row["passage_complete"], bool): return "invalid_spans_or_completeness"
    if row["technical_content"] == "absent" and row["spans"]: return "absent_with_spans"
    text = queue_item["text"]
    seen = set()
    for span in row["spans"]:
        if not isinstance(span, dict): return "invalid_span"
        if not {"start", "end", "text", "type", "clause_start", "clause_end", "modality"}.issubset(span): return "missing_span_fields"
        start, end, cstart, cend = (span.get(k) for k in ("start", "end", "clause_start", "clause_end"))
        if any(not isinstance(x, int) for x in (start, end, cstart, cend)): return "invalid_offsets"
        if span.get("type") not in LABELS: return "invalid_label_type"
        allowed_modality = ("required", "preferred", "allowed_alternative", "unclear") if row["source_type"] == "job" else ("not_applicable",)
        if span.get("modality") not in allowed_modality: return "invalid_modality"
        if start < 0 or end <= start or end > len(text) or text[start:end] != span.get("text"): return "span_offset_mismatch"
        if cstart < 0 or cend < end or cend > len(text) or text[cstart:cend] != span.get("clause_text", text[cstart:cend]) or not (cstart <= start and end <= cend): return "clause_offset_mismatch"
        key = (span["type"], start, end)
        if key in seen: return "duplicate_span"
        seen.add(key)
    return None


def final_job_decisions(annotations):
    """Checked job decisions only: the first pass if accepted, the checker's replacement if corrected."""
    return {a["document_id"]: a["decision"] for a in annotations
            if a["kind"] == "job" and a["disposition"] in ("accepted", "corrected")}


def finalize(release):
    rows = load_release(release)
    documents = {x["document_id"]: x for x in rows("documents.jsonl")}
    queue = rows("annotation_queue.jsonl")
    issues = rows("issues.jsonl")
    job_rows = rows("job_decisions.jsonl")
    span_rows = rows("span_drafts.jsonl")
    checks = rows("ai_checks.jsonl")
    jobs_by_doc = {r.get("document_id"): r for r in job_rows}
    spans_by_pid = {r.get("passage_id"): r for r in span_rows}
    check_by_key = {(r.get("kind"), r.get("document_id") or r.get("passage_id")): r for r in checks}
    annotations, unresolved = [], 0
    accepted_counts = {"accepted": 0, "corrected": 0, "unresolved": 0, "unchecked": 0}
    for item in queue:
        kind = item["kind"]
        key = item["document_id"] if kind == "job" else item["passage_id"]
        source = jobs_by_doc.get(key) if kind == "job" else spans_by_pid.get(key)
        checker = check_by_key.get((kind, key))
        doc = documents.get(item["document_id"])
        failure = None
        if source is None: failure = "missing_agent_decision"
        elif kind == "job": failure = validate_job_decision(source, doc or {})
        else: failure = validate_span(source, item)
        if checker is None:
            disposition, decision = "unchecked", None
        elif checker.get("source_hash") not in (item.get("source_hash"), item.get("text_sha256")):
            disposition, decision, failure = "unresolved", None, "checker_hash_mismatch"
        elif checker.get("decision") not in ("accepted", "corrected", "unresolved"):
            disposition, decision, failure = "unresolved", None, "invalid_checker_decision"
        else:
            disposition = checker["decision"]
            decision = source
            if disposition == "corrected":
                decision = checker.get("replacement")
                if not isinstance(decision, dict): failure = "corrected_missing_replacement"
                elif kind == "job": failure = validate_job_decision(decision, doc or {})
                else: failure = validate_span(decision, item)
            elif disposition == "accepted" and failure:
                disposition = "unresolved"
        if failure:
            disposition, decision = "unresolved", None
            issues.append(issue("finalize", failure, key, item_id=item["queue_id"], source_type=item["source_type"]))
        if disposition == "unresolved": unresolved += 1
        accepted_counts[disposition] = accepted_counts.get(disposition, 0) + 1
        annotations.append({"queue_id": item["queue_id"], "kind": kind, "document_id": item["document_id"],
            "passage_id": item.get("passage_id"), "source_type": item["source_type"], "source_hash": item["source_hash"],
            "text_sha256": item.get("text_sha256"), "decision": decision, "checker": checker,
            "disposition": disposition, "unresolved_reason": failure if disposition == "unresolved" else None,
            "split_group_id": item["split_group_id"], "quality_flags": item.get("quality_flags", [])})
    expected_job_ids = {q["document_id"] for q in queue if q["kind"] == "job"}
    expected_span_ids = {q["passage_id"] for q in queue if q["kind"] == "span"}
    for row in job_rows:
        if row.get("document_id") not in expected_job_ids:
            issues.append(issue("finalize", "unexpected_job_decision", row.get("document_id")))
    for row in span_rows:
        if row.get("passage_id") not in expected_span_ids:
            issues.append(issue("finalize", "unexpected_span_decision", row.get("passage_id")))
    for row in checks:
        key = row.get("document_id") if row.get("kind") == "job" else row.get("passage_id")
        valid_ids = expected_job_ids if row.get("kind") == "job" else expected_span_ids
        if key not in valid_ids:
            issues.append(issue("finalize", "unexpected_ai_check", key))
    write_jsonl(release / "annotations.jsonl", sorted(annotations, key=lambda x: x["queue_id"]))
    train, val, test = [], [], []
    count_details = {name: {"examples": 0, "source_types": {}, "entity_types": {k: 0 for k in LABELS}, "negatives": 0} for name in ("train", "val", "test")}
    checked = {x["queue_id"]: x for x in annotations}
    final_jobs = final_job_decisions(annotations)
    exact_hash_splits = {}
    for item in queue:
        if item["kind"] != "span": continue
        annotation = checked.get(item["queue_id"])
        if not annotation or annotation["disposition"] not in ("accepted", "corrected"): continue
        decision = annotation["decision"]
        job_decision = final_jobs.get(item["document_id"])
        if item["source_type"] == "job":
            if not job_decision or job_decision.get("relevance") != "relevant": continue
            completeness_ok = item.get("text_status") == "apparently_usable" and not item.get("quality_flags")
        else:
            doc = documents[item["document_id"]]
            completeness_ok = doc.get("status") == "ok" and not item.get("quality_flags") and item.get("applicability_state") == "resolved"
        if decision.get("language") != "english": continue
        spans = decision.get("spans", [])
        negative = decision.get("technical_content") == "absent" and decision.get("passage_complete") is True and completeness_ok
        if not spans and not negative: continue
        pref = "Source: job posting\n" if item["source_type"] == "job" else "Source: syllabus\n"
        context = (item.get("heading_context") + "\n") if item.get("heading_context") else ""
        final_input = pref + context + item["text"]
        offset = len(pref) + len(context)
        entities = {k: [] for k in LABELS}
        exclude = False
        for span in spans:
            start, end = offset + span["start"], offset + span["end"]
            clause_start, clause_end = span["clause_start"], span["clause_end"]
            # Exclude if the supported clause itself crossed a chunk boundary.
            if clause_start < 0 or clause_end > len(item["text"]):
                issues.append(issue("finalize", "span_clause_crosses_chunk", item.get("source_path"), item_id=item["queue_id"], span=span))
                exclude = True
                break
            if final_input[start:end] != span["text"]:
                issues.append(issue("finalize", "export_span_mismatch", item.get("source_path"), item_id=item["queue_id"], span=span))
                exclude = True
                break
            entities[span["type"]].append({"text": span["text"], "start": start, "end": end})
        if exclude: continue
        split = split_for_group(item["split_group_id"])
        text_hash = sha_bytes(unicodedata.normalize("NFC", item["text"]).encode("utf-8"))
        if text_hash in exact_hash_splits and exact_hash_splits[text_hash] != split:
            issues.append(issue("finalize", "split_leakage", item.get("source_path"), item_id=item["queue_id"]))
            continue
        exact_hash_splits[text_hash] = split
        native = {"input": final_input, "output": {"entities": entities},
                  "_provenance": {"queue_id": item["queue_id"], "document_id": item["document_id"],
                                  "passage_id": item["passage_id"], "source_type": item["source_type"],
                                  "split_group_id": item["split_group_id"]}}
        {"train": train, "val": val, "test": test}[split].append(native)
        detail = count_details[split]
        detail["examples"] += 1
        detail["source_types"][item["source_type"]] = detail["source_types"].get(item["source_type"], 0) + 1
        detail["negatives"] += int(negative)
        for label, values in entities.items(): detail["entity_types"][label] += len(values)
    # GLiNER2 schema is strict: provenance stays in the separate annotations file.
    for split_name, examples in (("train", train), ("val", val), ("test", test)):
        native_rows = [{"input": x["input"], "output": x["output"]} for x in examples]
        write_jsonl(release / ("gliner2_" + split_name + ".jsonl"), native_rows)
    # Row order of each native file -> source group, so evaluation can resample by group.
    write_jsonl(release / "split_index.jsonl", [dict(x["_provenance"], split=name, row=i)
        for name, examples in (("train", train), ("val", val), ("test", test)) for i, x in enumerate(examples)])
    write_jsonl(release / "issues.jsonl", sorted(issues, key=lambda x: (x.get("stage", ""), x.get("reason_code", ""), x.get("source_path", ""))))
    manifest = json.loads((release / "manifest.json").read_text(encoding="utf-8"))
    manifest["counts"]["annotation_dispositions"] = accepted_counts
    manifest["counts"]["export_splits"] = count_details
    manifest["training_ready"] = bool(all(count_details[s]["examples"] > 0 for s in ("train", "val", "test")) and
        all(count_details["train"]["entity_types"][k] > 0 for k in LABELS) and not accepted_counts.get("unchecked", 0) and
        not any(x["reason_code"] in ("split_leakage", "export_span_mismatch") for x in issues))
    manifest["training_ready_reasons"] = [] if manifest["training_ready"] else ["unchecked decisions, an empty split, a missing positive label type, or an integrity failure"]
    manifest["outputs"] = {p.name: file_sha(p) for p in sorted(release.iterdir()) if p.is_file() and p.name != "manifest.json"}
    atomic_text(release / "manifest.json", json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n")
    if unresolved or accepted_counts.get("unchecked", 0):
        return 1
    return 0


def verify(release):
    issues = []
    manifest = json.loads((release / "manifest.json").read_text(encoding="utf-8"))
    for name, expected in manifest.get("outputs", {}).items():
        path = release / name
        if not path.is_file() or file_sha(path) != expected:
            issues.append(issue("verify", "output_hash_mismatch", name, expected=expected, actual=file_sha(path) if path.is_file() else None))
    docs = {r["document_id"]: r for r in load_release(release)("documents.jsonl")}
    passages = load_release(release)("passages.jsonl")
    for passage in passages:
        doc = docs.get(passage.get("document_id"))
        if not doc:
            issues.append(issue("verify", "passage_document_missing", passage.get("passage_id")))
        elif doc["full_text"][passage["document_start"]:passage["document_end"]] != passage["text"]:
            issues.append(issue("verify", "passage_offset_mismatch", passage.get("passage_id")))
    annotations = load_release(release)("annotations.jsonl")
    for ann in annotations:
        d = docs.get(ann["document_id"])
        if not d or ann.get("source_hash") != d.get("source_sha256"):
            issues.append(issue("verify", "annotation_source_link_mismatch", ann.get("queue_id")))
    native_hashes = {}
    for split in ("train", "val", "test"):
        path = release / ("gliner2_" + split + ".jsonl")
        for line_number, row in enumerate(load_release(release)(path.name), 1):
            for label, items in row.get("output", {}).get("entities", {}).items():
                if label not in LABELS:
                    issues.append(issue("verify", "unknown_entity_type", path.name, line_number=line_number, label=label))
                for ent in items:
                    if row["input"][ent["start"]:ent["end"]] != ent["text"]:
                        issues.append(issue("verify", "entity_offset_mismatch", path.name, line_number=line_number))
            h = sha_bytes(unicodedata.normalize("NFC", row["input"].split("\n", 1)[-1]).encode("utf-8"))
            if h in native_hashes and native_hashes[h] != split:
                issues.append(issue("verify", "split_leakage", path.name, line_number=line_number))
            native_hashes[h] = split
    if issues:
        write_jsonl(release / "issues.jsonl", sorted(load_release(release)("issues.jsonl") + issues,
            key=lambda x: (x.get("stage", ""), x.get("reason_code", ""), x.get("source_path", ""))))
        print(release / "issues.jsonl")
        return 1
    print(json.dumps({"release": str(release), "training_ready": manifest.get("training_ready"), "issues": 0}, sort_keys=True))
    return 0


def cli(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("prepare")
    p.add_argument("--release-id", required=True)
    p.add_argument("--cutoff-utc", required=True)
    p.add_argument("--output-root", required=True)
    for name in ("finalize", "verify"):
        p = sub.add_parser(name)
        p.add_argument("--release-id", required=True)
        p.add_argument("--output-root", required=True)
    args = parser.parse_args(argv)
    try:
        release = Path(args.output_root) / args.release_id
        if args.command == "prepare":
            prepare(args.release_id, args.cutoff_utc, args.output_root)
            return 0
        if not release.is_dir():
            raise FileNotFoundError(str(release))
        if args.command == "finalize":
            result = finalize(release)
            print(release / "issues.jsonl")
            return result
        return verify(release)
    except Exception as exc:
        print("pre_model_data: " + str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(cli())
