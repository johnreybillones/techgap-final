"""Append-only local registry; imports never perform network requests."""
import json
import os
import re
import uuid
import unicodedata
from pathlib import Path

from .contracts import canonical_hash, validate_item


def _jsonl(path):
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def _description_hash(item):
    value = item.get("description_text") or item.get("description_html") or ""
    value = unicodedata.normalize("NFC", value.replace("\r\n", "\n").replace("\r", "\n"))
    return canonical_hash(re.sub(r"\s+", " ", value).strip())


class Registry:
    def __init__(self, root):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)
        (self.root / "raw").mkdir(exist_ok=True)

    def read_jsonl(self, name):
        return _jsonl(self.root / name)

    def _append(self, name, row):
        with (self.root / name).open("a", encoding="utf-8", newline="\n") as stream:
            stream.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")

    def _append_once(self, name, key, value, row):
        if any(existing.get(key) == value for existing in self.read_jsonl(name)):
            return
        self._append(name, row)

    def import_item(self, item, *, run_id, dataset_item_id, query_id):
        check = validate_item(item)
        if not check["valid"]:
            raise ValueError(",".join(check["reasons"]))
        raw_hash = canonical_hash(item)
        observation_id = canonical_hash([run_id, str(dataset_item_id), raw_hash])
        observations = self.read_jsonl("observations.jsonl")
        observation_exists = any(row["observation_id"] == observation_id for row in observations)
        source_id = str(item["id"])
        posting_key = "jobstreet:ph:" + source_id
        raw_path = Path("raw") / run_id / (raw_hash + ".json")
        absolute = self.root / raw_path
        absolute.parent.mkdir(parents=True, exist_ok=True)
        if not absolute.exists():
            temp = absolute.with_name(absolute.name + ".tmp-" + uuid.uuid4().hex)
            temp.write_text(json.dumps(item, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            os.replace(str(temp), str(absolute))
        self._append_once(str(Path("raw") / run_id / "items.jsonl"), "observation_id", observation_id,
            {"observation_id": observation_id, "dataset_item_id": str(dataset_item_id), "raw_hash": raw_hash, "item": item})
        description_hash = _description_hash(item)
        semantic_fields = {key: item.get(key, {"__missing__": True}) for key in (
            "description_text", "description_html", "title", "company", "location", "salary",
            "workType", "postedAt_iso", "postedAt_display", "detail_status", "isExpired")}
        version_id = canonical_hash([posting_key, semantic_fields])
        postings = self.read_jsonl("postings.jsonl")
        if not any(row["posting_key"] == posting_key for row in postings):
            self._append("postings.jsonl", {"posting_key": posting_key, "source_id": source_id, "source_url": item["url"]})
        versions = self.read_jsonl("versions.jsonl")
        if not any(row["version_id"] == version_id for row in versions):
            self._append("versions.jsonl", {"version_id": version_id, "posting_key": posting_key,
                "raw_hash": raw_hash, "raw_file": raw_path.as_posix(), "description_hash": description_hash,
                "fields": item, "full_description": bool(item.get("description_text") or item.get("description_html"))})
        if not observation_exists:
            self._append("observations.jsonl", {"observation_id": observation_id, "posting_key": posting_key,
                "version_id": version_id, "run_id": run_id, "dataset_item_id": str(dataset_item_id),
                "query_id": query_id, "raw_hash": raw_hash, "raw_file": raw_path.as_posix()})
        return not observation_exists
