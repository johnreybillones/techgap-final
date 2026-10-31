"""Copy AI decisions and checks from one pre-model release to another.

Only rows whose source hash still matches the new release's queue are carried;
everything else stays unlabeled. finalize re-validates every carried row.
Usage: python scripts/carry_labels.py OLD_RELEASE_DIR NEW_RELEASE_DIR
"""
import json
import sys
from pathlib import Path


def rows(path):
    return [json.loads(x) for x in path.read_text(encoding="utf-8").splitlines() if x.strip()]


def carry(old, new):
    queue = rows(new / "annotation_queue.jsonl")
    jobs = {q["document_id"]: q["source_hash"] for q in queue if q["kind"] == "job"}
    spans = {q["passage_id"]: q["text_sha256"] for q in queue if q["kind"] == "span"}
    keep = {
        "job_decisions.jsonl": lambda r: jobs.get(r.get("document_id")) == r.get("source_hash"),
        "span_drafts.jsonl": lambda r: spans.get(r.get("passage_id")) == r.get("text_sha256"),
        "ai_checks.jsonl": lambda r: (jobs if r.get("kind") == "job" else spans).get(
            r.get("document_id") if r.get("kind") == "job" else r.get("passage_id")) == r.get("source_hash"),
    }
    counts = {}
    for name, ok in keep.items():
        source = rows(old / name)
        kept = [r for r in source if ok(r)]
        with open(new / name, "w", encoding="utf-8", newline="\n") as f:
            f.writelines(json.dumps(r, ensure_ascii=False) + "\n" for r in kept)
        counts[name] = (len(kept), len(source) - len(kept))
    return counts


if __name__ == "__main__":
    print(carry(Path(sys.argv[1]), Path(sys.argv[2])))
