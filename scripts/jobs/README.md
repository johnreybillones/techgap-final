# JobStreet collection utilities

The current implementation supports local campaign preparation, importing saved JSON dataset exports, bounded live collection, and hash-checked raw-v2 release manifests. The older rule-based admission path remains available for historical releases. Import and validation paths do not make network calls.

```powershell
python -B scripts/jobs/collect.py prepare dev-2026-10 --window-end 2026-10-22T00:00:00+08:00
python -B scripts/jobs/collect.py import data/job_collections/dev-2026-10 saved-items.json --run-id saved-run-id --query-id WD01
```

Preparation freezes a 30-day window by default and records the historical 34 literal discovery routes from the plan. Pass `--window-start` to freeze another supported window. Import expects a saved JSON array and a matching campaign config. It preserves every returned item as raw JSON and appends source identities, semantic versions, query/run observations, and invalid-item reasons. New imports do not run legacy admission or write `eligible_frame.jsonl`; the legacy artifacts and release command remain available as historical outputs.

`collect` requires exactly one of `--dry-run`, `--preflight` or `--execute`; a bare command cannot start an actor. Dry-run is offline. Preflight performs read-only actor/build checks. Execute requires the campaign's explicit `live_collection_enabled: true` and recorded actor/build, source-access, current allowance, collection authorization and budget evidence in `live_adapter`; it reserves the cap before issuing one POST. The adapter never repeats a start automatically. `resume` attaches only to the saved run or an operator-reconciled run ID and never starts a replacement.

Live requests are additionally bounded to six frozen unique core query IDs, no more than two evidence-backed conditional starts, 25 requested rows, USD 0.05 per request, the campaign's configured lower per-run cap, USD 0.30 per campaign, and 300 seconds. The accepted pilot proposal uses USD 0.02525 per run at the verified Free-tier event prices. Requests are serial and each query can be started once. Conditional requests require all six core requests to be imported/failed with reconciled billing plus a saved gap and comparison rule. These are code ceilings, not spending authorization.

Run the read-only saved-data audit against a raw-v2 release and its earlier registry to measure full-campaign overlap and produce six provisional query proposals. `--recovery-manifest` restricts the incremental funnel to the referenced recovered run IDs; the optional review sheet remains pending until a human reviewer completes its decision fields:

```powershell
python -B scripts/jobs/audit_saved_campaign.py data/job_collections/jobstreet-2026-10-recovered-reconciliation-raw-v2 --baseline data/job_collections/jobstreet-2026-10-live-preflight --recovery-manifest data/job_collections/jobstreet-2026-10-live-preflight-dataset-recovery-v1/recovery_manifest.json --output data/job_collections/jobstreet-2026-10-recovered-reconciliation-raw-v2-yield-audit-v1/audit.json --review-sheet data/job_collections/jobstreet-2026-10-recovered-reconciliation-raw-v2-yield-audit-v1/review_sheet.csv
```

Its relevance, cohort and technical-assessability screens are provisional and do not reuse admission labels or model outputs. Description flags distinguish absent, short, suspected truncation and uncertain completeness; a provider full-description flag does not prove all sections were captured. The user selected an analyst review for this bounded pilot; see `analyst_review_2026-10-23.csv`. The original review sheet remains pending for an independent human check, which is still required before trusting downstream rankings. The accompanying `proposed-pilot/collection_config.json` contains the six user-selected strings and plan caps, but remains disabled pending fresh account/window evidence and separate spending authorization. The historical cost correction is in `billing_reconciliation_2026-10-23.json` beside the audit.

Normal `collect.py freeze` produces a raw-v2 handoff independent of legacy admission. Use `freeze-legacy` only for historical admission-based releases. Both reject an existing frozen manifest; import into a writable campaign context before freezing.

An unknown start may be resolved with a Console-verified run ID, or with `resume --no-run-evidence <file>` after saved evidence confirms that Apify created no run. The latter releases only that request's reservation. See [the adapter plan](../../docs/plan/JOBSTREET_LIVE_ADAPTER_PLAN.md#31-campaign-and-request-validation) for required evidence fields and scope matching.

Illustrative local preview after its campaign evidence is complete and live collection is explicitly enabled (the current proposal is still disabled):

```powershell
python -B scripts/jobs/collect.py collect data/job_collections/jobstreet-2026-10-recovered-reconciliation-raw-v2-yield-audit-v1/proposed-pilot --query-id WD06 --results-wanted 25 --charge-cap-usd 0.02525 --dry-run
```

The `live_adapter` evidence fields are intentionally not populated by `prepare`; it never enables live collection or fabricates an authorization/account balance. Keep `APIFY_API_TOKEN` in an ignored repository `.env` or the process environment. `python-dotenv==1.0.1` is pinned for this repository's Python 3.8 runtime. The provider's generic identity response is not treated as an allowance; stale/missing local allowance evidence blocks execution.

The earlier 34-run campaign was collected. On 2026-10-23, read-only account/run/build checks verified its 850 charged result events, USD 0.85850 provider run usage and the pinned actor's pay-per-event contract. These snapshots can age; refresh allowance and exact window evidence before the separate six-query pilot. No new pilot actor run has started.

Admission is a conservative deterministic first pass; its evidence and unresolved states require review as policy or parsing changes. It is not a validated classifier. Repost identity resolution, adaptive date-window widening, automatic operational stop decisions, sampling and source-page development checks remain manual or unimplemented. A released evidence package should not be treated as complete population coverage or a validated analytical dataset.

## Reviewed admission baseline v2

The saved `admission-audit-v2/posting_case_review.csv` is a screening aid, not a set of approved labels. Prepare a separate review copy with blank decision fields:

```powershell
python -B scripts/jobs/review_admissions_v2.py prepare-template `
  data/job_collections/jobstreet-2026-10-live-preflight/admission-audit-v2/posting_case_review.csv `
  data/job_collections/jobstreet-2026-10-live-preflight/admission-audit-v2-review/posting_case_review.csv
```

For each source ID, fill `review_decision` (`accepted`, `excluded`, or `unresolved`), `reviewer_id`, timezone-qualified ISO `reviewed_at`, `review_reason`, and `review_evidence_json` (a JSON array of `{ "gate": "...", "excerpt": "..." }` source passages). All decisions need at least one evidence passage. For an accepted row, also fill `cohort` (`employment` or `internship`), `canonical_role`, `track_memberships_json` (a JSON array of every supported track), and `verified_gates_json` (all seven gates set to JSON `true`); the evidence must cover `identity`, `publication_date`, `philippine_eligibility`, `description`, `computing_duties`, `cohort`, and `seniority`. Screening evidence columns must remain unchanged.

Reconcile the completed or partial review into new files, leaving the v1 campaign ledger and the screen CSV untouched:

```powershell
python -B scripts/jobs/review_admissions_v2.py reconcile `
  data/job_collections/jobstreet-2026-10-live-preflight/admission-audit-v2/posting_case_review.csv `
  data/job_collections/jobstreet-2026-10-live-preflight/admission-audit-v2-review/posting_case_review.csv `
  data/job_collections/jobstreet-2026-10-live-preflight/admission-audit-v2-review/results
```

The summary reports accepted employment and internship source IDs separately, overlapping track memberships, exclusions, unresolved and pending review. It calls the employment count a baseline only after every source ID has an explicit accepted or excluded decision and none remain unresolved. Artifact creation refuses to overwrite existing results; make a new review version/output directory for later corrections. This offline workflow does not perform live collection or establish market coverage.

After a terminal run, dataset retrieval rechecks an initially empty default dataset before accepting zero rows, because provider run completion and dataset population can become visible at different times. Settled `usageTotalUsd` is preferred over the start-time `chargedUsd` field when recording provider charges.

To recover provider datasets for existing locally saved-empty runs into a separate, hash-recorded package, use `recover_dataset_outputs.py`. It only performs authenticated GET requests, refuses to overwrite its destination, and leaves the original campaign untouched:

```powershell
python -B scripts/jobs/recover_dataset_outputs.py data/job_collections/source-campaign data/job_collections/source-campaign-dataset-recovery-v1
```

The recovery command is for already-created datasets; it does not start or resume actors. Compare recovered counts and charges against provider evidence before using them in a release.

## Raw-v2 handoff and automatic-admission integration

`scripts.jobs.release.migrate_raw_release` copies a frozen campaign into a new
derived release directory and builds `source_frame.jsonl`,
`collection_audit.json`, and a `job-collection-raw-v2` manifest. It includes
every identifiable source posting and never reads legacy `admission.jsonl` or
`eligible_frame.jsonl` to select membership. The migration refuses to overwrite
an existing destination and validates hashes with `validate_release`.

The admission-only implementation is in `scripts/pipeline/`. It validates a
local ESCO occupation release, checks every extracted span against source text,
unions exact/alias and MPNet candidates, applies independent zero-shot
hypotheses, expands the shortlist from 20 to 40 and searches the full catalog
before a no-match rejection, then writes one final decision per source ID plus
a separate count-unit frame. The writer checks source-frame and selected-raw
hashes and checkpoints completed decisions for resume. Policy-fixture tests do
not establish domain accuracy. Missing dependencies or artifacts are a run
failure, not 438 fabricated rejections.

From the repository root, run the saved-data baseline with the existing Python
3.14 environment:

```powershell
.venv\Scripts\python.exe -m scripts.pipeline.run_admission
```

The command is offline-only, loads the pinned local checkpoints, and attaches
model feedback to the raw-v2 release after all source IDs reconcile. It writes
the admission release under `data/job_collections/` and progress under
`data/job_collections/_run_logs/`. The first MPNet index build is cached under
ignored `models/`; no paid collection request is made.

After a successful admission run, pass its release summary through
`attach_admission_feedback`. The join requires a matching raw source-frame hash,
the equality `input_postings = accepted_employment + accepted_internship +
rejected`, explicit model/taxonomy/policy identities, and a count-unit
membership hash. Until that succeeds, the raw manifest correctly retains
`admission_status: not_classified` and accepted yield is unavailable.
