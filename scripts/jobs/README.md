# JobStreet collection utilities

The current implementation supports local campaign preparation, importing saved JSON dataset exports, conservative rule-based admission, and hash-checked release manifests. Import and validation paths do not make network calls.

```powershell
python -B scripts/jobs/collect.py prepare dev-2026-10 --window-end 2026-10-22T00:00:00+08:00
python -B scripts/jobs/collect.py import data/job_collections/dev-2026-10 saved-items.json --run-id saved-run-id --query-id WD01
```

Preparation freezes a 30-day window by default and records the 34 literal discovery routes from the plan. Pass `--window-start` to freeze another supported window. Import expects a saved JSON array and a matching campaign config. It preserves every item as raw JSON, appends identities, semantic versions, observations and admission evidence, and adds each source ID at most once to `eligible_frame.jsonl`.

`collect` requires exactly one of `--dry-run`, `--preflight` or `--execute`; a bare command cannot start an actor. Dry-run is offline. Preflight performs read-only actor/build checks. Execute requires the campaign's explicit `live_collection_enabled: true` and recorded actor/build, source-access, current allowance, collection authorization and budget evidence in `live_adapter`; it reserves the cap before issuing one POST. The adapter never repeats a start automatically. `resume` attaches only to the saved run or an operator-reconciled run ID and never starts a replacement.

An unknown start may be resolved with a Console-verified run ID, or with `resume --no-run-evidence <file>` after saved evidence confirms that Apify created no run. The latter releases only that request's reservation. See [the adapter plan](../../docs/plan/JOBSTREET_LIVE_ADAPTER_PLAN.md#31-campaign-and-request-validation) for required evidence fields and scope matching.

Example local preview:

```powershell
python -B scripts/jobs/collect.py collect data/job_collections/dev-2026-10 --query-id WD01 --results-wanted 25 --charge-cap-usd 0.05 --dry-run
```

The `live_adapter` evidence fields are intentionally not populated by `prepare`; it never enables live collection or fabricates an authorization/account balance. Keep `APIFY_API_TOKEN` in an ignored repository `.env` or the process environment. `python-dotenv==1.0.1` is pinned for this repository's Python 3.8 runtime. The provider's generic identity response is not treated as an allowance; stale/missing local allowance evidence blocks execution.

Live collection has not been executed or preflighted against an account. Offline tests exercise an injected transport only. Account-level allowance, source access, build-contract compatibility, actual billing fields and returned-description quality remain to be verified before the separate bounded pilot.

Admission is a conservative deterministic first pass; its evidence and unresolved states require review as policy or parsing changes. It is not a validated classifier. Repost identity resolution, adaptive date-window widening, automatic operational stop decisions, sampling and source-page development checks remain manual or unimplemented. A released evidence package should not be treated as complete population coverage or a validated analytical dataset.
