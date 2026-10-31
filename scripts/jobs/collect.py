"""Offline campaign preparation and saved-run import CLI."""
import argparse
import json
import sys
from pathlib import Path

try:  # Support both `python -m scripts.jobs.collect` and direct script execution.
    from .registry import Registry
    from .apify_adapter import verify_execution_gate
    from .contracts import canonical_hash, validate_item, validate_config, validate_run_metadata
    from .release import freeze_raw_release, freeze_release, validate_release
    from .acquisition_state import AcquisitionState, StateError
    from .apify_adapter import (AdapterError, ApifyTransport, build_request, download_dataset, load_token,
        poll_run, preflight, run_metadata, start_run, _atomic_json, _get_retry, sanitize, _provider_id)
except ImportError:  # pragma: no cover - exercised by the direct CLI entry point
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from jobs.registry import Registry
    from jobs.apify_adapter import verify_execution_gate
    from jobs.contracts import canonical_hash, validate_item, validate_config, validate_run_metadata
    from jobs.release import freeze_raw_release, freeze_release, validate_release
    from jobs.acquisition_state import AcquisitionState, StateError
    from jobs.apify_adapter import (AdapterError, ApifyTransport, build_request, download_dataset, load_token,
        poll_run, preflight, run_metadata, start_run, _atomic_json, _get_retry, sanitize, _provider_id)


def prepare(root, campaign_id, window_end, target=1000, window_start=None):
    root = Path(root) / campaign_id
    root.mkdir(parents=True, exist_ok=False)
    if window_start is None:
        from datetime import datetime, timedelta
        end = datetime.fromisoformat(window_end.replace("Z", "+00:00"))
        window_start = (end - timedelta(days=30)).isoformat()
    config = {"schema_version": "job-collection-v1", "campaign_id": campaign_id,
        "requested_target": target, "window_start": window_start, "window_end": window_end, "report_timezone": "Asia/Manila",
        "queries": query_registry(),
        "live_collection_enabled": False, "live_adapter": {}, "pilot_core_query_ids": [],
        "pilot_optional_query_ids": [], "conditional_start_evidence": {}}
    (root / "collection_config.json").write_text(json.dumps(config, indent=2) + "\n", encoding="utf-8")
    Registry(root)
    return root


def import_run(root, input_file, *, run_id, query_id, run_metadata=None):
    if (Path(root) / "manifest.json").exists():
        raise ValueError("Frozen release is immutable; import into a writable campaign context")
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
    if run_metadata is not None:
        metadata_check = validate_run_metadata(run_metadata, run_id=run_id, query_id=query_id)
        if not metadata_check["valid"]:
            raise ValueError("Invalid run metadata: " + ", ".join(metadata_check["errors"]))
        prior_run = next((row for row in registry.read_jsonl("runs.jsonl")
                          if row.get("run_id") == run_id and row.get("query_id") == query_id), None)
        prior_source = next((row for row in registry.read_jsonl("source_runs.jsonl") if row.get("run_id") == run_id), None)
        for key, value in run_metadata.items():
            run_key = "provider_status" if key == "status" else key
            if prior_run and prior_run.get(run_key) not in (None, "") and prior_run[run_key] != value:
                raise ValueError("Conflicting run metadata field: " + run_key)
            if prior_source and key not in {"query_id", "import_status"} and prior_source.get(key) not in (None, "") and prior_source[key] != value:
                raise ValueError("Conflicting source run metadata field: " + key)
    items = json.loads(Path(input_file).read_text(encoding="utf-8"))
    if not isinstance(items, list):
        raise ValueError("Saved dataset must be a JSON array")
    imported = 0
    invalid = 0
    prior_posting_keys = {row.get("posting_key") for row in registry.read_jsonl("postings.jsonl")}
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
        posting_key = "jobstreet:ph:" + str(item["id"])
    from datetime import datetime, timezone
    run_record = {"run_id": run_id, "dataset_id": None, "query_id": query_id,
        "actor_id": None, "build": None, "started_at": None, "finished_at": None,
        "status": "saved_payload_imported", "provider_status": None, "import_status": "imported",
        "returned_items": len(items), "new_observations": imported,
        "invalid_items": invalid, "imported_at": datetime.now(timezone.utc).isoformat(),
        "source_file": Path(input_file).name}
    if run_metadata:
        run_record.update(run_metadata)
        run_record["provider_status"] = run_metadata["status"]
        run_record["status"] = "provider_run_imported"
        run_record["import_status"] = "imported"
    prior_runs = registry.read_jsonl("runs.jsonl")
    existing = next((row for row in prior_runs if row.get("run_id") == run_id and row.get("query_id") == query_id), None)
    if existing:
        # Enrichment is additive; conflicting verified metadata must not overwrite prior evidence.
        for metadata_key, value in (run_metadata or {}).items():
            key = "provider_status" if metadata_key == "status" else "import_status" if metadata_key == "import_status" else metadata_key
            if metadata_key == "status":
                existing.setdefault("provider_status", value)
            if existing.get(key) not in (None, "") and value not in (None, "") and existing[key] != value:
                raise ValueError("Conflicting run metadata field: " + key)
            if existing.get(key) in (None, "") and value not in (None, ""):
                existing[key] = value
        run_path = Path(root) / "runs.jsonl"
        run_path.write_text("".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in prior_runs), encoding="utf-8")
    else:
        registry._append("runs.jsonl", run_record)
    source_runs = registry.read_jsonl("source_runs.jsonl")
    source = {k: v for k, v in (run_metadata or {}).items() if k not in {"query_id", "import_status"}}
    if run_metadata:
        source["billing_status"] = "reconciled" if run_metadata.get("provider_charge_usd") is not None else "unknown"
    if not any(row.get("run_id") == run_id for row in source_runs):
        registry._append("source_runs.jsonl", source or {"run_id": run_id, "billing_status": "unknown"})
    elif source:
        prior = next(row for row in source_runs if row.get("run_id") == run_id)
        for key, value in source.items():
            if key == "billing_status" and prior.get(key) == "unknown" and value == "reconciled":
                prior[key] = value
                continue
            if prior.get(key) not in (None, "") and value not in (None, "") and prior[key] != value:
                raise ValueError("Conflicting source run metadata field: " + key)
            if prior.get(key) in (None, "") and value not in (None, ""):
                prior[key] = value
        (Path(root) / "source_runs.jsonl").write_text("".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in source_runs), encoding="utf-8")
    imported_keys = {"jobstreet:ph:" + str(item["id"]) for item in items if validate_item(item)["valid"]}
    return {"returned": len(items), "new_observations": imported,
        "reused_items": sum(1 for item in items if validate_item(item)["valid"] and
                             "jobstreet:ph:" + str(item["id"]) in prior_posting_keys), "invalid_items": invalid,
        "distinct_source_ids_observed": len(imported_keys),
        "window_start": window_start}


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


def _read_config(campaign):
    path = Path(campaign) / "collection_config.json"
    if not path.is_file():
        raise ValueError("Campaign config not found: " + str(path))
    return json.loads(path.read_text(encoding="utf-8"))


def _terminal_charge(run):
    """Prefer the present terminal settled total; use chargedUsd only as fallback."""
    return run.get("usageTotalUsd") if run.get("usageTotalUsd") is not None else run.get("chargedUsd")


def _finish_request(campaign, state, record, transport):
    request_id = record["request_id"]
    if record.get("status") == "contract_mismatch" or record.get("last_error_category") == "effective_build_mismatch":
        raise AdapterError("contract_mismatch", "effective build/options mismatch requires manual reconciliation; saved run evidence retained")
    run_id = record.get("run_id")
    if not run_id:
        raise AdapterError("start_outcome_unknown", "request has no verified run ID; reconcile it before resuming")
    run, _ = _get_retry(transport, "/v2/actor-runs/" + run_id)
    run = run.get("data", run) if isinstance(run, dict) else run
    if run.get("status") not in {"SUCCEEDED", "FAILED", "TIMED-OUT", "ABORTED"}:
        run = poll_run(run_id, transport, state, request_id, timeout_secs=record["run_options"]["timeout"])
    run_path = Path(campaign) / "raw" / run_id / "run.json"
    _atomic_json(run_path, {"request_id": request_id, "request": record.get("sanitized_request"),
        "run": sanitize(run, transport.token), "actor_id": record.get("actor_id"), "build_id": run.get("buildId"),
        "build_number": record.get("expected_build_number"), "dataset_id": run.get("defaultDatasetId"),
        "status": run.get("status")})
    if run.get("status") != "SUCCEEDED":
        if run.get("defaultDatasetId"):
            try: download_dataset(run, transport, state, request_id)
            except AdapterError: pass
        charge = _terminal_charge(run)
        if charge is None:
            state.update(request_id, "failed", billing_status="unknown", provider_status=run.get("status"))
        else:
            state.settle(request_id, run_id, charge, evidence={"provider_status": run.get("status")})
            state.update(request_id, "failed", provider_status=run.get("status"))
        raise AdapterError("run_failed", "run ended with {}; no import was performed".format(run.get("status")))
    dataset_file = download_dataset(run, transport, state, request_id)
    refreshed, _ = _get_retry(transport, "/v2/actor-runs/" + run_id)
    refreshed = refreshed.get("data", refreshed) if isinstance(refreshed, dict) else refreshed
    if refreshed.get("status") != "SUCCEEDED":
        state.update(request_id, "running", provider_status=refreshed.get("status"),
                     last_error_category="terminal_status_changed")
        raise AdapterError("terminal_status_changed", "run status changed while fetching its dataset; resume and inspect saved evidence")
    run = refreshed
    _atomic_json(run_path, {"request_id": request_id, "request": record.get("sanitized_request"),
        "run": sanitize(run, transport.token), "actor_id": record.get("actor_id"), "build_id": run.get("buildId"),
        "build_number": record.get("expected_build_number"), "dataset_id": run.get("defaultDatasetId"),
        "status": run.get("status")})
    state.update(request_id, "importing")
    meta = run_metadata(run, record, run.get("defaultDatasetId"), imported_status="imported")
    outcome = import_run(campaign, dataset_file, run_id=run_id, query_id=record["query_id"], run_metadata=meta)
    charge = _terminal_charge(run)
    if charge is None:
        state.update(request_id, "imported", billing_status="unknown", import_report=outcome)
    else:
        state.settle(request_id, run_id, charge, evidence={"provider_status": run.get("status"),
            "charged_event_counts": run.get("chargedEventCounts"), "pricing_info": run.get("pricingInfo")})
        state.update(request_id, "imported", billing_status="reconciled", import_report=outcome)
    return outcome


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("prepare"); p.add_argument("campaign_id"); p.add_argument("--root", default="data/job_collections"); p.add_argument("--window-end", required=True); p.add_argument("--window-start", help="Frozen UTC start; defaults to 30 days before window_end"); p.add_argument("--target", type=int, default=1000)
    p = sub.add_parser("import"); p.add_argument("campaign"); p.add_argument("input"); p.add_argument("--run-id", required=True); p.add_argument("--query-id", required=True); p.add_argument("--run-metadata")
    p = sub.add_parser("collect", help="Preview, preflight or execute one registered JobStreet query")
    p.add_argument("campaign")
    mode = p.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--preflight", action="store_true")
    mode.add_argument("--execute", action="store_true")
    p.add_argument("--query-id", required=True); p.add_argument("--results-wanted", type=int, required=True)
    p.add_argument("--charge-cap-usd", required=True)
    p = sub.add_parser("resume", help="Resume or reconcile an existing acquisition; never starts a run")
    p.add_argument("campaign"); p.add_argument("--request-id", required=True)
    reconcile = p.add_mutually_exclusive_group()
    reconcile.add_argument("--run-id", help="Verified Console-discovered run ID for an unknown start")
    reconcile.add_argument("--no-run-evidence", help="Local evidence file confirming no remote run was created")
    p = sub.add_parser("validate", help="Validate hashes in an existing release")
    p.add_argument("campaign")
    p = sub.add_parser("freeze", help="Build and hash a raw-v2 release from imported evidence")
    p.add_argument("campaign"); p.add_argument("--release-id", required=True); p.add_argument("--phase", default="development_only")
    p.add_argument("--target", type=int, default=1000); p.add_argument("--window-start", required=True); p.add_argument("--window-end", required=True)
    p.add_argument("--reported-charge-usd", type=float, default=0.0)
    p = sub.add_parser("freeze-legacy", help="Build a historical admission-based release")
    p.add_argument("campaign"); p.add_argument("--release-id", required=True); p.add_argument("--phase", default="development_only")
    p.add_argument("--target", type=int, default=1000); p.add_argument("--window-start", required=True); p.add_argument("--window-end", required=True)
    p.add_argument("--reported-charge-usd", type=float, default=0.0)
    args = parser.parse_args(argv)
    if args.command == "prepare":
        print(prepare(args.root, args.campaign_id, args.window_end, args.target, args.window_start))
    elif args.command == "import":
        try:
            metadata = json.loads(Path(args.run_metadata).read_text(encoding="utf-8")) if args.run_metadata else None
            print(json.dumps(import_run(args.campaign, args.input, run_id=args.run_id, query_id=args.query_id, run_metadata=metadata)))
        except (ValueError, RuntimeError, OSError) as exc:
            print(str(exc), file=sys.stderr)
            return 1
    elif args.command == "collect":
        try:
            config = _read_config(args.campaign)
            request = build_request(config, query_id=args.query_id, results_wanted=args.results_wanted,
                                    charge_cap_usd=args.charge_cap_usd, campaign_root=args.campaign)
            if args.dry_run:
                print(json.dumps(request, ensure_ascii=False, indent=2))
                return 0
            token = load_token(Path(__file__).resolve().parents[2])
            transport = ApifyTransport(token)
            if args.preflight:
                result = preflight(config, request, transport)
                print(json.dumps(result, ensure_ascii=False))
                return 0
            if (Path(args.campaign) / "manifest.json").exists():
                raise ValueError("Frozen release is immutable; prepare a writable campaign context")
            state = AcquisitionState(args.campaign)
            with state.lock():
                preflight(config, request, transport)
                print(json.dumps({"request_id": request["request_id"], "status": "starting"}), flush=True)
                record = start_run(request, transport, state)
                state.update(request["request_id"], "running", sanitized_request=request)
                outcome = _finish_request(args.campaign, state, state.get(request["request_id"]), transport)
            print(json.dumps({"request_id": request["request_id"], "run_id": record["id"], "import": outcome}, ensure_ascii=False))
            return 0
        except (ValueError, RuntimeError, OSError) as exc:
            print(str(exc), file=sys.stderr)
            return 1
    elif args.command == "resume":
        try:
            state = AcquisitionState(args.campaign)
            with state.lock():
                record = state.get(args.request_id)
                if args.no_run_evidence:
                    state.reconcile_no_run(args.request_id, args.no_run_evidence)
                    print(json.dumps({"request_id": args.request_id, "status": "verified_no_remote_run",
                                      "reservation_released": True}, ensure_ascii=False))
                    return 0
                if args.run_id:
                    _provider_id(args.run_id, "run_id")
                    if record.get("run_id") and record["run_id"] != args.run_id:
                        raise ValueError("run_id conflicts with saved request")
                    token = load_token(Path(__file__).resolve().parents[2])
                    transport = ApifyTransport(token)
                    response, _ = transport.request("GET", "/v2/actor-runs/" + args.run_id)
                    run = response.get("data", response)
                    if run.get("actId") != record.get("actor_id") or run.get("buildId") != record.get("expected_build_id") or run.get("input") != record.get("input"):
                        raise ValueError("reconciled run does not match saved actor/build/input")
                    record = state.update(args.request_id, "running", run_id=args.run_id,
                        dataset_id=run.get("defaultDatasetId"), provider_status=run.get("status"), provider_run=run)
                elif record.get("status") == "start_outcome_unknown" and not record.get("run_id"):
                    raise ValueError("start outcome is unknown; supply a verified --run-id after Console reconciliation")
                token = load_token(Path(__file__).resolve().parents[2])
                transport = ApifyTransport(token)
                outcome = _finish_request(args.campaign, state, record, transport)
            print(json.dumps({"request_id": args.request_id, "import": outcome}, ensure_ascii=False))
            return 0
        except (ValueError, RuntimeError, OSError) as exc:
            print(str(exc), file=sys.stderr)
            return 1
    elif args.command == "validate":
        result = validate_release(args.campaign)
        print(json.dumps(result))
        if not result["valid"]:
            raise SystemExit(1)
    elif args.command in {"freeze", "freeze-legacy"}:
        try:
            if (Path(args.campaign) / "manifest.json").exists():
                raise ValueError("Frozen release is immutable; freeze a writable campaign context")
            freezer = freeze_raw_release if args.command == "freeze" else freeze_release
            result = freezer(args.campaign, release_id=args.release_id, phase=args.phase,
                requested_target=args.target, window_start=args.window_start, window_end=args.window_end,
                reported_charge_usd=args.reported_charge_usd)
            print(json.dumps(result, ensure_ascii=False))
        except (ValueError, RuntimeError, OSError) as exc:
            print(str(exc), file=sys.stderr)
            return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
