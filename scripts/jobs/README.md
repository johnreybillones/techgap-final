# JobStreet collection utilities

The current implementation supports local campaign preparation, importing saved JSON dataset exports, conservative rule-based admission, and hash-checked release manifests. Import and validation paths do not make network calls.

```powershell
python -B scripts/jobs/collect.py prepare dev-2026-10 --window-end 2026-10-22T00:00:00+08:00
python -B scripts/jobs/collect.py import data/job_collections/dev-2026-10 saved-items.json --run-id saved-run-id --query-id WD01
```

Preparation freezes a 30-day window by default and records the 34 literal discovery routes from the plan. Pass `--window-start` to freeze another supported window. Import expects a saved JSON array and a matching campaign config. It preserves every item as raw JSON, appends identities, semantic versions, observations and admission evidence, and adds each source ID at most once to `eligible_frame.jsonl`.

`collect` intentionally raises an execution-gate error. Live adapter execution is not implemented. Before any provider adapter is enabled, verify actual account allowance, source-access basis, run-level charge caps, actor contract/build, pagination and full-description behavior. Do not place credentials in run logs or config files.

Admission is a conservative deterministic first pass; its evidence and unresolved states require review as policy or parsing changes. It is not a validated classifier. Repost identity resolution, adaptive date-window widening, automatic operational stop decisions, sampling and source-page development checks remain manual or unimplemented. A released evidence package should not be treated as complete population coverage or a validated analytical dataset.
