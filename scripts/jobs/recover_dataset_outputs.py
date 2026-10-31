"""Recover saved-empty Apify datasets into a separate, immutable evidence package."""
import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

try:
    from .apify_adapter import ApifyTransport, load_token, _get_retry
except ImportError:  # pragma: no cover - direct script entry point
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from jobs.apify_adapter import ApifyTransport, load_token, _get_retry


def recover(campaign, output):
    campaign, output = Path(campaign), Path(output)
    if output.exists():
        raise FileExistsError("recovery output already exists: {}".format(output))
    source_runs = [json.loads(line) for line in (campaign / "runs.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
    empty = [row for row in source_runs if row.get("returned_items") == 0 and row.get("dataset_id") and row.get("run_id")]
    if not empty:
        raise ValueError("no zero-item saved runs with dataset IDs were found")
    token = load_token(Path(__file__).resolve().parents[2])
    transport = ApifyTransport(token)
    output.mkdir(parents=True)
    manifest_rows = []
    for run in empty:
        dataset_id = run["dataset_id"]
        metadata, _ = _get_retry(transport, "/v2/datasets/" + dataset_id, query={"limit": 0})
        metadata = metadata.get("data", metadata) if isinstance(metadata, dict) else {}
        total = metadata.get("itemCount")
        if not isinstance(total, int) or total < 1:
            continue
        items, offset = [], 0
        while offset < total:
            page, headers = _get_retry(transport, "/v2/datasets/{}/items".format(dataset_id),
                query={"offset": offset, "limit": min(1000, total - offset), "desc": False,
                       "clean": False, "skipHidden": False, "skipEmpty": False})
            if not isinstance(page, list) or not page:
                raise RuntimeError("dataset {} ended before its advertised item count".format(dataset_id))
            page_total = headers.get("x-apify-pagination-total")
            if page_total is not None and int(page_total) != total:
                raise RuntimeError("dataset {} item count changed during recovery".format(dataset_id))
            items.extend(page)
            offset += len(page)
        final, _ = _get_retry(transport, "/v2/datasets/" + dataset_id, query={"limit": 0})
        final = final.get("data", final) if isinstance(final, dict) else {}
        if final.get("itemCount") != total or len(items) != total:
            raise RuntimeError("dataset {} count did not reconcile".format(dataset_id))
        folder = output / "datasets" / run["run_id"]
        folder.mkdir(parents=True)
        raw = (json.dumps(items, ensure_ascii=False, separators=(",", ":")) + "\n").encode("utf-8")
        (folder / "dataset.json").write_bytes(raw)
        metadata_record = {"run_id": run["run_id"], "query_id": run.get("query_id"),
            "dataset_id": dataset_id, "recovered_at": datetime.now(timezone.utc).isoformat(),
            "provider_item_count": total, "recovered_item_count": len(items),
            "dataset_metadata": metadata, "source_campaign": campaign.name,
            "sha256": hashlib.sha256(raw).hexdigest()}
        (folder / "recovery.json").write_text(json.dumps(metadata_record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        manifest_rows.append(metadata_record)
    if not manifest_rows:
        output.rmdir()
        raise RuntimeError("provider reports no recoverable items for the saved-empty runs")
    manifest = {"schema_version": "apify-dataset-recovery-v1", "source_campaign": str(campaign),
        "created_at": datetime.now(timezone.utc).isoformat(), "recovered_datasets": manifest_rows}
    (output / "recovery_manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return manifest


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("campaign")
    parser.add_argument("output")
    args = parser.parse_args(argv)
    result = recover(args.campaign, args.output)
    print(json.dumps({"output": args.output, "datasets": len(result["recovered_datasets"]),
                      "items": sum(row["recovered_item_count"] for row in result["recovered_datasets"])}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
