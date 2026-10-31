# JobStreet Live Adapter Implementation Plan

> **For implementation:** Follow the tasks in order, using `superpowers:executing-plans` when executing this plan. Checkboxes track future work; none indicates completed implementation.

Updated: 2026-10-22 (Asia/Manila).

**Goal:** Connect one bounded registered JobStreet query at a time to Apify, preserve its raw dataset and run provenance, and import the saved results into an existing collection campaign.

**Architecture:** Extend the existing Python collection CLI with an asynchronous start/poll/download workflow. Keep provider HTTP operations in the adapter, acquisition checkpoints and reservations in a small local state module, and admission/identity handling in the existing importer. Recovery attaches to an existing run; it never silently purchases another run.

**Tech stack:** Existing Python CLI, `argparse`, JSON/JSONL, `pathlib`, `Decimal`, `unittest`/`unittest.mock`; standard-library HTTP transport with an injectable request function; `python-dotenv` for local `.env` loading. Select and pin a compatible published dotenv release during dependency setup. No web service or database migration is needed for this adapter.

**Status (2026-10-22):** Offline adapter and CLI implementation is present and its collection tests pass. No token was read, account preflight run, or paid run started. Task 7 remains pending; current account allowance, source authorization, successful provider behavior and description quality have not been verified live.

**Implemented offline:** explicit preview/preflight/execute modes; registered query and date-window checks; pinned build and saved input/pricing-contract comparisons; token loading/redaction; atomic request checkpoints, single-writer lock, budget ledger and no-run reconciliation; one-POST start, same-run polling, raw paginated dataset export/recovery; metadata-aware and replay-safe local import; truthful release billing/provenance limitations. Verification: `python -B -m unittest discover -s tests/collection -v`, `python -B scripts/jobs/collect.py collect --help`, and `git diff --check` passed on 2026-10-22. These are offline checks only.

**Still pending:** account-specific allowance evidence, operator source-access and collection-scope evidence in a real campaign config, provider preflight against the account, one authorized paid run, actual billing reconciliation, live interruption/recovery, and source-description comparison. A failed or incomplete account preflight blocks execution; implementation does not imply a live-verified adapter.

## 1. Why this is needed and what already exists

The adapter is required for automatic collection through the repo. It is optional when the operator starts the actor in Apify Console, exports the dataset as a JSON array, and imports that saved file. Both routes use the existing third-party actor; neither changes its search capabilities.

The [collection execution plan](JOBSTREET_COLLECTION.md) remains authoritative for the population, 34 query strings, recent-first window, twelve-month limit, admission rules, 1,000-to-4,000 reuse target and spending constraints. This companion specifies the missing integration rather than a new collection policy.

| Verified local component | Present behavior | Adapter work needed |
| --- | --- | --- |
| [`collect.py`](../../scripts/jobs/collect.py) | `prepare`, JSON-array `import`, `freeze`, `validate`; `collect` calls a blocking gate. | Add explicit dry-run/live/resume arguments and call the adapter only on the live path. |
| [`apify_adapter.py`](../../scripts/jobs/apify_adapter.py) | Checks some gate fields, then always raises an unimplemented error. | Implement authenticated HTTP, exact input mapping, run polling and complete dataset retrieval. |
| [`contracts.py`](../../scripts/jobs/contracts.py) | Basic config/item/run validation; `validate_run` is not wired into import. | Validate live controls, metadata and nested credential exclusion. |
| [`registry.py`](../../scripts/jobs/registry.py) | Local append-only raw payloads, identities, versions and observations. | Preserve existing identity rules; add targeted recovery guarantees needed by live import. |
| `import_run()` in `collect.py` | Receives `run_id`/`query_id`; writes null dataset, actor, build and run times. | Accept optional saved metadata and preserve verified values. |
| [`release.py`](../../scripts/jobs/release.py) | Hash checks; charge supplied by caller; audit always says no live collection occurred. | Derive truthful acquisition limitations and reconcile known live charges. |
| [Collection tests](../../tests/collection/test_collection.py) | Saved-fixture import/admission/release cases. | Add network-free lifecycle, budget, provenance and recovery cases. |

The current utilities do not establish complete transactional imports, a shared registry across campaigns, automated multi-query/window scheduling, or validated admission accuracy. Implementing this adapter must not be reported as completing those broader collection-plan responsibilities.

## 2. Chosen approach and scope

**Recommended:** Start the actor, persist its run ID, poll status, fetch its dataset, then import locally. Apify documents this asynchronous approach for runs exceeding five minutes; saved run identity also gives this repo a recovery point. A synchronous run-and-return endpoint is simpler but ties collection to one connection. Console export remains the immediate manual alternative. [Apify workflow guide](https://docs.apify.com/academy/api/run-actor-and-retrieve-data-via-api)

The first adapter handles one query and the campaign's already frozen window per invocation. Proposed defaults are at most 25 requested results and a 300-second provider timeout, matching section 8 of the collection plan. A distinct result limit and an explicit positive USD run cap are required. No automatic query round, window widening, recurring schedule, new provider, competency model or frontend is included. Those remain separate work products in the parent plan.

Only one acquisition/import process may write the campaign at a time. A campaign lock must span reservation through final checkpoint/import, including resume. An unresolved remote run or unknown start outcome blocks another start even after the local process exits.

## 3. Input, configuration and execution contract

### 3.1 Campaign and request validation

Read `collection_config.json` and resolve the literal keyword by enabled `query_id`; reject arbitrary keyword overrides and disabled/unknown IDs. Keep the exact input, query registry hash and config hash with each request.

Validate timezone-aware `window_start < window_end`, with no start earlier than twelve calendar months before the frozen end; use calendar subtraction with end-of-month clamping. Reject a run-level window different from the campaign. Wider windows require an explicit parent-plan campaign revision and local re-evaluation, not an adapter side effect.

Keep the existing top-level `live_collection_enabled` default `false`; an operator must explicitly enable it after recording the execution evidence. Require it to be `true` for `--execute`; dry-run/preflight may explain what still blocks execution. Extend config with a `live_adapter` object containing:

| Field | Meaning and validation |
| --- | --- |
| `actor_id`, `actor_name`, `build_number`, `build_id` | Expected provider identity and verified build. Initial baseline: actor `f7ggUvGaOrrUuPkZQ`, `shahidirfan/jobstreet-scraper`, build `0.0.36`, build ID `wcMB0BeF4w9asSke8`. |
| `actor_contract_sha256`, `actor_contract_verified_at` | Snapshot hash/time plus evidence path for input, billing, description and continuation checks. A bare boolean is insufficient. |
| `source_access_basis` | Recorded basis and evidence reference required by the parent plan. |
| `allowance_verified_at`, `verified_available_usd` | Actual account allowance evidence and timestamp; not the public Free-plan amount. |
| `allowance_snapshot_basis`, `allowance_reconciliation_evidence` | Explain whether prior pilot usage is already reflected in the verified balance and point to its evidence; if it is reflected, `baseline_spend_usd` must not subtract it again. |
| `campaign_ceiling_usd`, `baseline_spend_usd` | Ceiling at most `min(5.00, verified allocation)` and spending against that ceiling not already reflected in the allowance snapshot. |
| `authorized_collection_scope` | Evidence reference plus exact `campaign_id`, `query_ids`, `window_start`, `window_end`, and `max_charge_usd`; the historical pilot approval covers only that pilot. |
| `timeout_secs`, `memory_mbytes`, `max_results_per_run` | Positive finite controls; initially 300 seconds, verified 1,024 MB allocation and maximum 25 results. |

Use decimal arithmetic for money; reject zero, negative, non-finite and excessive caps. Refuse a start if gate evidence is absent, account evidence no longer applies to the current balance/period, an earlier reservation is unresolved, or the new cap exceeds unreserved funds. Do not quietly refresh a cap upward or enable live collection while preparing a campaign.

### 3.2 Credential handling

Load credentials only for explicit live/preflight/resume operations. Prefer an existing `APIFY_API_TOKEN` environment variable; otherwise load the repository-root `.env` using `python-dotenv` with `override=False`, independent of current working directory. Reject missing/blank values. `prepare`, `import`, `freeze`, `validate`, module import and dry-run must work without a token or network.

Authenticate with a Bearer header; never place the token in a URL, CLI flag, config, checkpoint, run artifact or exception. Use a fixed HTTPS Apify API origin and reject redirects rather than forwarding credentials to another host. Save allowlisted response headers only; sanitize nested diagnostic objects and redact the actual token value before emitting errors. [Apify authentication](https://docs.apify.com/api/v2/getting-started)

### 3.3 Actor input and run controls

Use the [saved actor contract](../../data/collection_samples/jobstreet/actor-contract.json) and [pilot input](../../data/collection_samples/jobstreet/jobstreet-input.json) as the baseline, then verify compatibility before enabling a new run. For `WD01`, a 30-day request for 25 results is:

```json
{
  "keyword": "web developer",
  "location": "",
  "country": "ph",
  "posted_date": "30d",
  "results_wanted": 25,
  "proxyConfiguration": {"useApifyProxy": false}
}
```

Choose the narrowest documented filter covering the requested age span at execution: `24h`, `7d`, `30d`, otherwise `anytime`. Calculate that span from execution time to the frozen start, not just the window's duration; resuming an old campaign can require broader discovery. Enforce exact `[window_start, window_end)` membership locally. There are no invented `60d`/`90d` actor values. Record that `anytime` cannot guarantee recoverable historical supply; exclude `startUrl` overrides from this initial adapter.

Send build `0.0.36`, `timeout=300`, the verified memory allocation, `maxTotalChargeUsd=<reserved cap>` and `restartOnError=false` as run options. Keep `results_wanted` in the input body. Apify's `maxItems` is a pay-per-result billing control, so it is not a substitute for the run cost cap on this saved pay-per-event actor. [Run Actor API](https://docs.apify.com/api/v2/actors-runs-post)

The [pilot run evidence](../../data/collection_samples/jobstreet/run.json) records actual options `build: latest`, resolving to the build number/ID above. Future starts must explicitly request the number, verify that it is still available and compare the returned build ID; no fallback to `latest`. Verify the expected build using [Get Actor build](https://docs.apify.com/api/v2/actor-build-get). If it is unavailable or incompatible, stop and record `contract_changed` before proposing a replacement.

## 4. Run lifecycle, preservation and recovery

All API paths below are relative to `https://api.apify.com`. The transport accepts a method, path, query, JSON body and timeout and returns decoded content plus allowlisted headers. Inject it in tests so no unit test reaches Apify.

1. **Validate and preview.** Build the sanitized request and inspect local campaign state. Dry-run ends here without loading credentials, reserving funds or sending HTTP.
2. **Verify and reserve.** On explicit execution, verify provider/account evidence, obtain the exclusive campaign lock and atomically save a request ID, config/input hashes and reservation before POST. Budget availability is `ceiling - baseline spend - reconciled new charges - outstanding reservations`; define the baseline at the recorded allowance snapshot so spending is never subtracted twice.
3. **Start once.** `POST /v2/actors/f7ggUvGaOrrUuPkZQ/runs` with the section 3 controls. Persist returned `id`, `actId`, `buildId`, `defaultDatasetId`, status and times immediately. Compare actual identity/options with the request; mismatches halt acquisition and retain the reservation pending reconciliation. Never automatically repeat this POST. [Run Actor API](https://docs.apify.com/api/v2/actors-runs-post)
4. **Poll the same run.** `GET /v2/actor-runs/{run_id}` until terminal; keep local acquisition state separate from provider status. Treat `SUCCEEDED` as success; `FAILED`, `TIMED-OUT` and `ABORTED` as terminal failures; `READY`, `RUNNING`, `TIMING-OUT` and `ABORTING` as nonterminal. Unexpected status pauses with evidence. Use a 30-second HTTP timeout and five-second polling interval, with a local wait deadline of provider timeout plus 120 seconds; expiration checkpoints a still-remote run for resume. [Get Actor run](https://docs.apify.com/api/v2/actor-run-get)
5. **Fetch complete raw output.** On success, obtain `defaultDatasetId` from that run. Read `/v2/datasets/{dataset_id}/items` as JSON in ascending insertion order with `offset`, bounded page `limit`, `clean=false`, `skipHidden=false` and `skipEmpty=false`. Do not project, omit, flatten or unwind fields. Preserve each page body and pagination headers; compare offsets/counts/total and verify total stability against terminal dataset metadata. An empty dataset is a valid observed result; missing dataset identity or incomplete pagination is an error. [Dataset items API](https://docs.apify.com/api/v2/dataset-items-get)
6. **Finish the saved export.** Assemble a complete JSON array in absolute dataset-index order, validate its count/hash and atomically publish `dataset.json`. The importer reads JSON arrays, so do not pass its per-item JSONL archive as the input. Dataset pagination retrieves an existing dataset; it does not establish JobStreet search continuation.
7. **Import and reconcile.** Call the extended `import_run(campaign, dataset_file, run_id=..., query_id=..., run_metadata=...)`. Persist the query/config linkage and verified dataset ID. Refresh authenticated terminal run billing: retain provider-reported total, charged event counts and pricing evidence when exposed. Missing total remains unknown, never zero; hold the reservation and block another start until reconciled. Do not sum compute/events again when already included in the reported total. [Run billing fields](https://docs.apify.com/api/v2/actor-run-get)
8. **Report.** Write returned count, new observations, newly accepted count units, reused/invalid/excluded/unresolved counts, actual charges or unknown billing and coverage warnings. A successful provider status does not prove an uncapped search, complete descriptions or achievement of the eligible target.

### 4.1 Files inside `data/job_collections/<campaign_id>/`

| Artifact | Purpose |
| --- | --- |
| `requests/<request_id>.json` | Local acquisition state: sanitized request, hashes, query, reservation, run/dataset IDs, next dataset offset, page hashes, import/billing status and last error category. |
| `budget_ledger.jsonl` | Reservation/settlement evidence keyed by request/run; one charge contribution per run, regardless of polling or reimport count. |
| `raw/<run_id>/pages/<offset>.json` | Original complete JSON page body; validate before marking the offset saved. |
| `raw/<run_id>/pages/<offset>.metadata.json` | Offset/count/total, retrieval time and page hash; no authentication headers. |
| `raw/<run_id>/dataset.json` | Complete ordered array for the existing importer; published only after every page validates. |
| `raw/<run_id>/run.json` | Sanitized initial/final run evidence, effective controls, build and dataset IDs, status/times and billing. |
| Existing `runs.jsonl`, raw item files and registry artifacts | Import metadata and unchanged source objects under current identity/admission rules. |

Use temporary files and atomic replace for JSON checkpoints/exports; recover incomplete trailing ledger writes deterministically. Checkpoint updates never rewrite saved source pages. Protect acquisition state and ledger from concurrent writers. Do not mutate a previously frozen release; new acquisition uses a writable campaign/release context, preserving prior frozen artifacts.

### 4.2 Explicit failure behavior

| Failure | Required outcome |
| --- | --- |
| Invalid input, missing gate fact or token | No paid POST; actionable sanitized error. |
| Start response lost, malformed or missing run ID | Persist `start_outcome_unknown`; keep funds reserved; block starts. Operator reconciles the request with Apify Console/run evidence and attaches a verified ID, or records verified no-run evidence. Do not assume an idempotency guarantee. |
| Local crash after POST but before ID persistence | The pre-existing reservation/request forces the same unknown-start recovery; never replay the POST on restart. |
| 401/403 | Pause; fix credentials/access without retrying a paid start. |
| Poll/download 429, transient 5xx or network timeout | Retry GET only, at most three attempts, respecting `Retry-After` or bounded 1/2/4-second backoff; preserve state when exhausted. |
| Failed/timed-out/aborted run | Save terminal evidence, retrieve any available partial dataset as raw evidence, reconcile charges and report `run_failed`; no automatic admission/import or paid replacement. |
| Dataset interruption, count/hash mismatch or invalid page | Keep verified pages; resume the same dataset at the first unverified offset; no import until export is complete. |
| Import interrupted | Reuse the same export, run ID and absolute item indices; repair partial per-item writes before replay; do not claim append-only files alone are transactional. |
| Unknown charge or effective cap/build mismatch | Preserve evidence and stop further starts; do not release reserved money on an assumption. |
| Local interruption/deadline while actor runs | Checkpoint and report remote status; local exit does not imply abort. Resume only polls/downloads/imports the same run. |

## 5. Proposed CLI and operator process

These are the implemented CLI forms. Run from the repository root. Preparation remains offline:

```powershell
python -B scripts/jobs/collect.py prepare dev-2026-10 --window-end 2026-10-22T00:00:00+08:00
```

The operator then records section 3 gate evidence/settings in the campaign config and keeps the token in local `.env`. No command takes the token as an argument.

```powershell
# Local preview only, with no network or credential requirement.
python -B scripts/jobs/collect.py collect data/job_collections/dev-2026-10 --query-id WD01 --results-wanted 25 --charge-cap-usd 0.05 --dry-run

# Read-only provider/build/contract/pricing checks; no actor start.
python -B scripts/jobs/collect.py collect data/job_collections/dev-2026-10 --query-id WD01 --results-wanted 25 --charge-cap-usd 0.05 --preflight

# One explicitly authorized start, then download and local import.
python -B scripts/jobs/collect.py collect data/job_collections/dev-2026-10 --query-id WD01 --results-wanted 25 --charge-cap-usd 0.05 --execute
```

Require exactly one of `--dry-run`, `--preflight` or `--execute`; bare `collect` must never start a run. The USD 0.05 example is an illustrative cap, not new spending approval or a cost guarantee. A stale historical window can return no recoverable records.

The live command prints a local request ID before starting. Resume uses that checkpoint; an optional run ID is only for reconciling an unknown start and must pass actor/build/input/dataset checks against the stored request:

```powershell
# Reconnect to the original request; never start or resurrect an actor.
python -B scripts/jobs/collect.py resume data/job_collections/dev-2026-10 --request-id request-identifier

# Attach a verified Console-discovered run after an unknown start.
python -B scripts/jobs/collect.py resume data/job_collections/dev-2026-10 --request-id request-identifier --run-id verified-run-id

# Planned: release a reservation only after Console evidence confirms no remote run was created.
python -B scripts/jobs/collect.py resume data/job_collections/dev-2026-10 --request-id request-identifier --no-run-evidence evidence/no-run-check.txt
```

For the manual route, the existing import remains usable:

```powershell
python -B scripts/jobs/collect.py import data/job_collections/dev-2026-10 saved-items.json --run-id saved-run-id --query-id WD01
```

Manual import also accepts `--run-metadata saved-run.json` for provenance. Legacy imports without metadata remain explicitly incomplete; no fabricated actor/dataset IDs. After a batch, apply the parent plan's yield/budget/coverage decision before requesting another query. Adapter readiness does not itself automate that decision.

## 6. Implementation tasks and validation

All paths below are relative to the repository root. Implement each task with a failing focused test first, run it to confirm the intended failure, add the smallest implementation and rerun that test. Keep tests isolated with temporary directories, fake transport, fake clock/sleeper and a sentinel token. No ordinary test may perform a provider request.

### Task 1 — Configuration, credentials and request preview

**Modify:** `scripts/jobs/contracts.py`, `scripts/jobs/apify_adapter.py`, `scripts/requirements-collection.txt`, `.env.example`.
**Create tests:** `tests/collection/test_apify_adapter.py`.

- [ ] Add tests for enabled query lookup, timezone/window bounds, unknown/disabled queries, positive integer result limits, non-finite/cost limits, missing authorization/access/allowance/contract evidence, disabled live execution and caps over remaining funds. Assert zero transport calls on every rejected case.
- [ ] Extend `verify_execution_gate` to return a validated request on success instead of always raising; retain explicit error categories on failures. Implement the section 3 mapping and a sanitized preview without network or token access.
- [ ] Add tests for environment precedence, repository-root `.env` resolution from another directory, blank tokens and redaction in nested failures/artifacts. Add the pinned dotenv dependency and keep `.env` ignored; `.env.example` contains a blank key only.
- [ ] Run `python -B -m unittest discover -s tests/collection -p test_apify_adapter.py -v`; expect the new validation/secret-handling cases to pass.

### Task 2 — Durable state and budget reservation

**Create:** `scripts/jobs/acquisition_state.py`, `tests/collection/test_acquisition_state.py`.

- [ ] Define request states `prepared`, `reserved`, `start_outcome_unknown`, `running`, `downloading`, `downloaded`, `importing`, `imported` and `failed`; track billing separately as `reserved`, `unknown` or `reconciled`.
- [ ] Test exclusive writers, crash after reservation, stale lock recovery against the saved request, partial checkpoint/ledger writes, duplicate settlement and baseline/pilot accounting. Assert unknown remote state prevents a second start.
- [ ] Implement atomic checkpoint replacement, a campaign lock and a reservation/settlement ledger using decimal values serialized as strings. A repeated state event must not change the monetary balance twice.
- [ ] Run `python -B -m unittest discover -s tests/collection -p test_acquisition_state.py -v`; expect recovery and balance cases to pass without provider access.

### Task 3 — Provider preflight, start-once and polling

**Modify:** `scripts/jobs/apify_adapter.py`, `tests/collection/test_apify_adapter.py`.

- [ ] Test the exact actor/body/run options, response identity checks and a fake `READY -> RUNNING -> SUCCEEDED` sequence. Assert one POST even when later GETs fail. Add separate unknown-start, unavailable build, 401/403, 429/5xx, deadline and terminal-failure cases.
- [ ] Implement read-only preflight against current actor/build/input/pricing and authenticated account evidence, retaining sanitized relevant fields only. Account balance must be established from actual allowance/usage evidence; `/users/me` credential success alone is insufficient. If the API does not expose an authoritative remaining allocation, require recorded current Console evidence rather than infer one.
- [ ] Implement the fixed-origin transport with Bearer auth and no implicit POST retry/redirect. Persist the reservation before start and the ID immediately afterward; polling uses the injected clock and the section 4 deadline/retry rules.
- [ ] Compare effective build/cost/time/memory controls with the request. Check billing visibility while authenticated; never transform an omitted charge into zero.
- [ ] Rerun `python -B -m unittest discover -s tests/collection -p test_apify_adapter.py -v`; verify unknown starts produce one POST at most and remain blocked on resume until reconciled.

### Task 4 — Complete raw download and recovery

**Modify:** `scripts/jobs/apify_adapter.py`, `scripts/jobs/acquisition_state.py`, `tests/collection/test_apify_adapter.py`.

- [ ] Test a multi-page dataset including unknown/nested keys, null/empty salary, HTML, Unicode, hidden fields and an invalid item. Assert all decoded objects and absolute ordering equal the fixture and raw response pages are retained.
- [ ] Test an interruption between page save and checkpoint update, changed total, unexpected empty page, zero-item success, absent dataset ID and partial output after a failed run.
- [ ] Implement section 4 pagination/checkpoint/export rules. Verify page files/hashes before advancing; only publish `dataset.json` after count/total reconciliation. Recovery fetches the original dataset, never starts a new actor.
- [ ] Rerun the adapter and state test modules; expect complete page recovery, no duplicate indices and zero automatic import for failed/incomplete runs.

### Task 5 — Import provenance and truthful release evidence

**Modify:** `scripts/jobs/collect.py`, `scripts/jobs/contracts.py`, `scripts/jobs/registry.py`, `scripts/jobs/release.py`, `tests/collection/test_collection.py`.

- [ ] Add backward-compatible `run_metadata=None` to `import_run`. Validate matching run/query/dataset/actor/build/times/status, preserve verified fields in `runs.jsonl`, and distinguish provider status from local import status. Keep optional metadata absence visible for legacy offline imports.
- [ ] Test importing the same run twice, attaching metadata after a prior metadata-free import, conflicting metadata and one run observed through multiple queries. Use one verified source-run record plus query linkage so run charges are counted once; retain older evidence when recording an enrichment rather than silently dropping it under the existing run/query deduplication check.
- [ ] Test crash injection at raw/posting/version/observation/admission writes. Add targeted replay/repair so an observation written before admission cannot cause a resumed import to skip that admission forever. Publish/rebuild derived eligible membership only from complete decisions; unresolved repair blocks successful import completion.
- [ ] Replace the unconditional release claim `No live collection was executed.` with evidence-derived limitations. Known live charges reconcile by run ID with the ledger; unknown charges block a financially reconciled live handoff. Preserve explicit charges/provenance limitations for offline imports; retain coverage and admission-accuracy limitations.
- [ ] Run `python -B -m unittest discover -s tests/collection -v`; expect old offline cases and new provenance/recovery cases to pass without network access. This tests adapter integration, not all parent-plan release or shared-registry requirements.

### Task 6 — CLI integration and operating instructions

**Modify:** `scripts/jobs/collect.py`, `scripts/jobs/README.md`, `docs/plan/JOBSTREET_COLLECTION.md`, this plan.
**Create tests:** `tests/collection/test_live_cli.py`.

- [ ] Implement the exact section 5 options with mutually exclusive execution modes; `resume` accepts request/run identity only, never replacement query/window/cost options. Map local errors to concise nonzero CLI results with a recovery pointer.
- [ ] Test bare `collect`, dry-run, preflight, authorized execute, request resume and unknown-start reconciliation. Assert offline commands/dry-run make zero HTTP requests, preflight makes zero POSTs, execute starts at most once and resume makes zero paid POSTs.
- [ ] Run `python -B -m unittest discover -s tests/collection -v` and `python -B scripts/jobs/collect.py collect --help`; expect a passing collection suite and help matching section 5. Run `git diff --check` and review paths/artifacts for leaked sentinel credentials.
- [ ] Update the utility README and parent-plan status to describe only implemented behavior. Mark tested tasks here with verification evidence; leave the live pilot pending until actually authorized and measured.

### Task 7 — Bounded live verification, after implementation

**Evidence location:** a newly authorized campaign under `data/job_collections/`; keep the original discovery pilot unchanged.

- [ ] Complete all offline tests and a read-only preflight first. Record actual current allowance, source-access basis, contract/build compatibility and effective caps. Confirm the authorized request's query/window/result/cost controls; the old USD 0.10 pilot authorization does not carry forward.
- [ ] Run one bounded query under that authorization. Save actual request/run/dataset/build IDs, unchanged pages/export, terminal status, charge evidence and import report. Record whether caps or detail failures limited results.
- [ ] Resume/reimport the saved run and verify no second start, duplicate charge contribution, posting or observation; check dataset provenance reaches run records and release evidence.
- [ ] Compare selected saved full descriptions with accessible source pages across actual returned cases and report the count/discrepancies. A successful small run establishes integration for those cases, not collection-wide accuracy, eligible supply, historical completeness or affordability of 4,000 jobs.

## 7. Completion criteria

The adapter is ready when Tasks 1–6 pass their offline checks and the implemented commands preserve the complete saved dataset and provenance through interrupted acquisition/import, enforce reservations and caps, and never retry a paid start automatically. **Live verified** is a separate claim requiring Task 7 evidence. Missing funding/access/build facts block paid execution, not documentation or offline implementation work.

The resulting operator flow is: prepare campaign -> record gate evidence -> preview/preflight -> execute one bounded query -> save/checkpoint -> import -> reconcile/audit -> choose the next parent-plan action. The initial target can remain short; report the measured shortfall without changing eligibility or promising unavailable history.
