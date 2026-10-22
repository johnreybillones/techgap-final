"""Offline campaign preparation and saved-run import CLI."""
import argparse
import json
from pathlib import Path

try:  # Support both `python -m scripts.jobs.collect` and direct script execution.
    from .registry import Registry
    from .apify_adapter import verify_execution_gate
    from .admission import evaluate
    from .contracts import canonical_hash, validate_item, validate_config
    from .release import freeze_release, validate_release
except ImportError:  # pragma: no cover - exercised by the direct CLI entry point
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from jobs.registry import Registry
    from jobs.apify_adapter import verify_execution_gate
    from jobs.admission import evaluate
    from jobs.contracts import canonical_hash, validate_item, validate_config
    from jobs.release import freeze_release, validate_release


def prepare(root, campaign_id, window_end, target=1000, window_start=None):
    root = Path(root) / campaign_id
    root.mkdir(parents=True, exist_ok=False)
    if window_start is None:
        from datetime import datetime, timedelta
        end = datetime.fromisoformat(window_end.replace("Z", "+00:00"))
        window_start = (end - timedelta(days=30)).isoformat()
    config = {"schema_version": "job-collection-v1", "campaign_id": campaign_id,
        "requested_target": target, "window_start": window_start, "window_end": window_end, "report_timezone": "Asia/Manila",
        "admission_policy_version": "explicit-entry-junior-v1", "queries": query_registry(), "live_collection_enabled": False}
    (root / "collection_config.json").write_text(json.dumps(config, indent=2) + "\n", encoding="utf-8")
    Registry(root)
    return root


def import_run(root, input_file, *, run_id, query_id):
    registry = Registry(root)
    config_path = Path(root) / "collection_config.json"
    config = json.loads(config_path.read_text(encoding="utf-8")) if config_path.exists() else {}
    config_check = validate_config(config)
    if not config_check["valid"]:
        raise ValueError("Invalid campaign config: " + ", ".join(config_check["errors"]))
    window_end, window_start = config.get("window_end"), config.get("window_start")
    if not window_end or not window_start:
        raise ValueError("Campaign window_start and window_end must be frozen before importing")
    if query_id not in {row["query_id"] for row in config.get("queries", [])}:
        raise ValueError("query_id is not in the frozen campaign registry")
    items = json.loads(Path(input_file).read_text(encoding="utf-8"))
    if not isinstance(items, list):
        raise ValueError("Saved dataset must be a JSON array")
    imported = 0
    invalid = 0
    for index, item in enumerate(items):
        check = validate_item(item)
        if not check["valid"]:
            invalid += 1
            raw_hash = canonical_hash(item)
            observation_key = (run_id, str(index), raw_hash)
            if any((row.get("run_id"), row.get("dataset_item_id"), row.get("raw_hash")) == observation_key
                   for row in registry.read_jsonl("invalid_items.jsonl")):
                continue
            raw_folder = Path(root) / "raw" / run_id
            raw_folder.mkdir(parents=True, exist_ok=True)
            raw_path = raw_folder / (raw_hash + ".json")
            if not raw_path.exists():
                raw_path.write_text(json.dumps(item, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            registry._append(str(Path("raw") / run_id / "items.jsonl"), {"dataset_item_id": str(index),
                "raw_hash": raw_hash, "item": item, "identity_valid": False})
            registry._append("invalid_items.jsonl", {"run_id": run_id, "query_id": query_id,
                "dataset_item_id": str(index), "raw_hash": raw_hash, "raw_file": raw_path.relative_to(Path(root)).as_posix(),
                "reasons": check["reasons"]})
            continue
        created = registry.import_item(item, run_id=run_id, dataset_item_id=index, query_id=query_id)
        imported += int(created)
        if created:
            admission = evaluate(item, window_start=window_start, window_end=window_end)
            registry._append("admission.jsonl", {"posting_key": "jobstreet:ph:" + str(item["id"]),
                "run_id": run_id, "query_id": query_id, **admission})
            if admission["state"] == "eligible" and not any(row.get("count_unit_id") == "jobstreet:ph:" + str(item["id"]) for row in registry.read_jsonl("eligible_frame.jsonl")):
                raw_hash = canonical_hash(item)
                version = next(row for row in registry.read_jsonl("versions.jsonl") if row["raw_hash"] == raw_hash)
                registry._append("eligible_frame.jsonl", {"count_unit_id": "jobstreet:ph:" + str(item["id"]),
                    "source_id": str(item["id"]), "selected_version": version["version_id"],
                    "window_start": window_start, "window_end": window_end, "admission": admission})
    from datetime import datetime, timezone
    run_record = {"run_id": run_id, "dataset_id": None, "query_id": query_id,
        "actor_id": None, "build": None, "started_at": None, "finished_at": None,
        "status": "saved_payload_imported", "returned_items": len(items), "new_observations": imported,
        "invalid_items": invalid, "imported_at": datetime.now(timezone.utc).isoformat(),
        "source_file": Path(input_file).name}
    prior_runs = registry.read_jsonl("runs.jsonl")
    if not any(row.get("run_id") == run_id and row.get("query_id") == query_id for row in prior_runs):
        registry._append("runs.jsonl", run_record)
    return {"returned": len(items), "new_observations": imported, "invalid_items": invalid, "window_start": window_start}


def query_registry():
    rows = [
        ("IS01", "data analyst", "Intelligent Systems"), ("IS02", "data scientist", "Intelligent Systems"),
        ("IS03", "data engineer", "Intelligent Systems"), ("IS04", "machine learning engineer", "Intelligent Systems"),
        ("IS05", "AI engineer", "Intelligent Systems"), ("IS06", "AI programmer", "Intelligent Systems"),
        ("IS07", "computer vision engineer", "Intelligent Systems"), ("GD01", "game developer", "Game Development"),
        ("GD02", "game programmer", "Game Development"), ("GD03", "game designer", "Game Development"),
        ("GD04", "level designer", "Game Development"), ("GD05", "gameplay engineer", "Game Development"),
        ("GD06", "Unity developer", "Game Development"), ("GD07", "Unreal developer", "Game Development"),
        ("NT01", "network engineer", "Network Technology"), ("NT02", "network administrator", "Network Technology"),
        ("NT03", "network support engineer", "Network Technology"), ("NT04", "NOC engineer", "Network Technology"),
        ("NT05", "systems administrator", "Network Technology"), ("NT06", "cybersecurity analyst", "Network Technology"),
        ("NT07", "SOC analyst", "Network Technology"), ("WD01", "web developer", "Web Development"),
        ("WD02", "frontend developer", "Web Development"), ("WD03", "front end developer", "Web Development"),
        ("WD04", "backend developer", "Web Development"), ("WD05", "back end developer", "Web Development"),
        ("WD06", "full stack developer", "Web Development"), ("WD07", "web application developer", "Web Development"),
        ("SH01", "software engineer", "Shared/core"), ("SH02", "software developer", "Shared/core"),
        ("SH03", "application developer", "Shared/core"), ("SH04", "programmer", "Shared/core"),
        ("SH05", "QA engineer", "Shared/core"), ("SH06", "software tester", "Shared/core"),
    ]
    return [{"query_id": query_id, "keyword": keyword, "family": family, "status": "enabled"}
            for query_id, keyword, family in rows]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("prepare"); p.add_argument("campaign_id"); p.add_argument("--root", default="data/job_collections"); p.add_argument("--window-end", required=True); p.add_argument("--window-start", help="Frozen UTC start; defaults to 30 days before window_end"); p.add_argument("--target", type=int, default=1000)
    p = sub.add_parser("import"); p.add_argument("campaign"); p.add_argument("input"); p.add_argument("--run-id", required=True); p.add_argument("--query-id", required=True)
    sub.add_parser("collect", help="Live collection is blocked pending verified execution controls")
    p = sub.add_parser("validate", help="Validate hashes in an existing release")
    p.add_argument("campaign")
    p = sub.add_parser("freeze", help="Build and hash a release from imported evidence")
    p.add_argument("campaign"); p.add_argument("--release-id", required=True); p.add_argument("--phase", default="development_only")
    p.add_argument("--target", type=int, default=1000); p.add_argument("--window-start", required=True); p.add_argument("--window-end", required=True)
    p.add_argument("--reported-charge-usd", type=float, default=0.0)
    args = parser.parse_args()
    if args.command == "prepare":
        print(prepare(args.root, args.campaign_id, args.window_end, args.target, args.window_start))
    elif args.command == "import":
        print(json.dumps(import_run(args.campaign, args.input, run_id=args.run_id, query_id=args.query_id)))
    elif args.command == "validate":
        result = validate_release(args.campaign)
        print(json.dumps(result))
        if not result["valid"]:
            raise SystemExit(1)
    elif args.command == "freeze":
        result = freeze_release(args.campaign, release_id=args.release_id, phase=args.phase,
            requested_target=args.target, window_start=args.window_start, window_end=args.window_end,
            reported_charge_usd=args.reported_charge_usd)
        print(json.dumps(result, ensure_ascii=False))
    else:
        try:
            verify_execution_gate()
        except RuntimeError as exc:
            parser.error(str(exc))


if __name__ == "__main__":
    main()
