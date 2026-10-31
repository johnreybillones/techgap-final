# JobStreet actor evidence reconciliation plan

**Status:** Implementation handoff, 2026-10-23 (Asia/Manila). Execute this plan in the next conversation. The user chose **offline work only**. This replaces the completed six-query checklist previously in `PLAN.md`. It authorizes no actor start, paid retrieval, wider campaign, recurring collection, or switch of the routine route.

**Goal:** Produce a reproducible, source-linked comparison of the completed Shahidirfan and Blackfalcon pilots; correct the conflicting Blackfalcon yield analysis; and record a route decision aligned with [PLANNED_DATA_FLOW.md](docs/plan/PLANNED_DATA_FLOW.md) and [JOBSTREET_COLLECTION.md](docs/plan/JOBSTREET_COLLECTION.md).

**Route decision:** Keep `shahidirfan/jobstreet-scraper` as the default for bounded, recent first-page discovery. Preserve `blackfalcondata/jobstreet-scraper` output as candidate depth evidence; do not adopt it as the routine route from this run. Keep `pagination_unverified` unless saved run evidence resolves both missing page evidence and six page-3 rows under `maxPages=2`. The next conversation is to execute this decision, not choose another actor.

**Preservation rule:** Do not modify either pilot's original raw items, observations, versions, reports, requests, run metadata, hashes, or billing files. Write corrected derived artifacts to a new sibling directory. Use numeric JobStreet IDs validated against canonical URLs for cross-actor identity; the Blackfalcon hashed `jobId` is provenance only. Older admission/model decisions and query labels are not ground truth.

## Fixed evidence

| Frame | Saved result | Evidence location |
| --- | --- | --- |
| Historical registry | 438 distinct IDs | `data/job_collections/jobstreet-2026-10-recovered-reconciliation-raw-v2-yield-audit-v1/` |
| Shahidirfan six-query pilot | 150 returned/billed rows, 148 distinct IDs, 29 new against 438, USD 0.15150 settled; 29 provisionally source-audited assessable employment IDs | `data/job_collections/jobstreet-2026-10-six-query-pilot-20261023/` |
| Blackfalcon comparison registry | 467 IDs; SHA-256 `ca2430a13307abe27cfdb58ecdeb948775d8c095b649fe2908cb6e40c65b9107` | Six-query `comparison_registry_2026-10-23.jsonl` |
| Blackfalcon run | `PV3wSBkgCSJlLcGUM`, dataset `g5lOHihZXdtgMGXzw`, build `0.4.47` / `BCrNkaKb8HsInZ2vV`; 50 returned/billed, 50 distinct valid IDs, 34 saved, 16 new, 48 nonempty descriptions, USD 0.11000 settled | `data/job_collections/blackfalcon-data-engineer-paginated-20261023/` |
| Analysis conflict | `yield_report.json` says 3 usable new IDs; `source_audit.json` marks all 16 new IDs Philippine eligible and 9 as employment with assessable technical text. ID-level flags disagree. Both files match the recorded hashes. | Blackfalcon `raw_handoff_validation.json` |
| Page conflict | 22 qualifying page-2 rows, 6 page-3 rows despite `maxPages=2`, and 22 without qualifying page evidence | Blackfalcon request and yield report |

The runs have different query sets, prior registries, and UTC windows. Their ratios are dated marginal-yield observations, **not** a controlled A/B test or a market-demand estimate. The expected combined registry count is 483; verify it from the actual 467-ID frame and 16 new IDs before publishing it.

## Implementation files

- Create `scripts/jobs/reconcile_actor_pilots.py`: offline read-only input validation, ID-keyed joins, registry union, case-sheet/report generation, and page-evidence analysis. Accept explicit input/output paths; refuse an output path inside either original pilot directory.
- Create `tests/collection/test_reconcile_actor_pilots.py`: focused fixtures for ID-keyed joins, conflicting flags, missing text, internship separation, page evidence, hash/registry validation, and deterministic output.
- Create `data/job_collections/blackfalcon-data-engineer-paginated-20261023-reconciliation-v2/`: 16-case source-linked sheet, machine-readable corrected report, compact Markdown comparison/decision report, and manifest with input/output hashes and rule version.
- Update `data/job_collections/jobstreet-2026-10-six-query-pilot-20261023/README.md`: remove its stale statement that no candidate run has started; keep its original counts and provisional-label status.
- Update `docs/plan/JOBSTREET_PAGINATED_ACTOR_TEST_2026-10-23.md`: mark the one authorized test completed, link its reconciled result, and retain the proposed test contract as history.
- Update `docs/plan/JOBSTREET_COLLECTION.md` only where it still describes this completed candidate test as future work. Preserve its count definitions and spending gates. Do not change the meanings in `PLANNED_DATA_FLOW.md`.

## Task 1 — Validate the saved inputs

- [ ] Record `git status --short`; the checkout has substantial uncommitted work. Do not reset or overwrite unrelated files.
- [ ] Read the six-query `manifest.json`, `final_reconciliation_2026-10-23.json`, `new_id_yield_audit_2026-10-23.csv`, and comparison registry. Read the Blackfalcon exact request, `run_final.json`, `raw_items.json`, `source_audit.json`, `yield_report.json`, and `raw_handoff_validation.json`.
- [ ] Recompute SHA-256 for the Blackfalcon files named by the validation record and for the 467-ID registry. Fail on a mismatch and report the changed file; do not silently accept it.
- [ ] Assert 50 Blackfalcon observations and 50 unique numeric `seekJobId` values, each equal to the final `/job/<id>` segment in its `canonicalUrl`. Join against the frozen 467-ID registry and assert exactly 34 saved plus 16 new. Independently compute the combined union.

**Done when:** Input hashes, identities, observation counts, and registry arithmetic are reproducible without network access.

## Task 2 — Reconcile the 16 new IDs

- [ ] Produce one case row per new numeric ID, keyed by ID rather than dataset position. Include raw pointer/hash, URL, original title, location/`locationCountry`, `employmentType`, publication/capture dates, description length, short duty/requirement source passage, `searchUrl`, supported page number, and both existing files' flags side by side.
- [ ] Apply the following rules consistently. `locationCountry=PH` or explicit remote eligibility for Philippine applicants supports Philippine scope; a conflict is `unresolved`. `Full time`, `Part time`, or `Contract/Temp` is employment unless the vacancy explicitly says internship/OJT; explicit internship/OJT forms a separate cohort; unknown work type stays unresolved. A clear technical title supports computing relevance, including general computing work without a curated-role link; generic/conflicting titles require duties evidence. Technical assessability requires an explicit **required** technical capability in duties or qualifications and a cited source passage; a nonempty description, preferred-only tools, soft skills, or a query hit is insufficient. Missing or unusably truncated technical text is unavailable, not zero demand or zero coverage. Record uncertain evidence as `unresolved`, not `false`.
- [ ] Treat `source_audit.json` labels as provisional candidates and `yield_report.json` as conflicting prior output. Check all 16 against saved raw text. Record a short source-backed reason for every changed or retained decision. A Data Scientist or AI Developer can be relevant without being mapped to the `data engineer` role; query membership does not assign track or role.
- [ ] Recompute separately: new IDs, Philippine-scope employment, relevant employment, technically assessable relevant employment, internships, unresolved cases, and missing-description cases. Explicitly reconcile the saved `3` to the corrected figure. Compute corrected provisional yield per 50 billed rows and per settled USD 0.11000; never call it independently reviewed or accepted.
- [ ] Write only to the v2 sibling directory, recording rule version, UTC window, denominators, reasons, input hashes, and unresolved cases. The 16-case source review is pilot quality assessment, not a human-review dependency for routine collection or evidence of model accuracy.

**Done when:** Every new ID has a traceable case row; the aggregate count is the sum of those rows; each difference from the old `3` has a visible reason.

## Task 3 — Assess pagination from the same run

- [ ] Compare the exact request (`maxPages=2`, `maxResults=50`, one `data engineer` query, no `startUrls`, frozen UTC bounds) with saved run metadata and any saved logs. Make no Apify or JobStreet request.
- [ ] Derive page number only from a `searchUrl` whose host, query, and search/date context match the request. Preserve `page=null` where a URL does not explicitly prove the page; do not infer page 1 from missing `page` or dataset order.
- [ ] Count rows, new IDs, and corrected provisional assessable new employment IDs separately for proven page 2, proven page 3, and unproven page. Retain page-3 rows as observations; do not relabel them as page 2.
- [ ] Keep `pagination_unverified` if existing evidence cannot explain both 22 unproven rows and six page-3 rows. Record the exact discrepancy for a possible future maintainer inquiry. Do not send that inquiry in this task.

**Done when:** Every page-specific claim is reconstructable from saved URLs and the route decision does not rely on unverified depth.

## Task 4 — Publish the comparison and close the handoff

- [ ] Recompute the Shahidirfan dated baseline from its saved files: 29 provisional new assessable employment IDs / 150 billed rows and / USD 0.15150. Recompute Blackfalcon ratios from Task 2. Show both query sets, prior registry sizes, UTC windows, description availability, settled charges, and provisional-label status. Do not claim universal actor superiority from these sequential samples.
- [ ] State the fixed route decision: Shahidirfan remains the bounded first-page default; Blackfalcon results are retained but its pagination behavior blocks routine adoption. Query diversification and reuse of saved data are the next collection-planning levers. No further run is scheduled or authorized.
- [ ] Update the stale README and two plan documents listed above with links to the v2 report. Preserve the raw originals and both governing contracts.
- [ ] Run the focused reconciliation tests, relevant Blackfalcon adapter/raw-release tests, and `git diff --check`. Run the reconciler twice into separate temporary output directories and confirm identical derived content apart from deliberately recorded generation metadata. Confirm original pilot hashes did not change. Report exact commands, outcomes, changed files, and any remaining evidence limitation.

**Done when:** The v2 manifest/report reproduces all counts from preserved inputs, explains the `3`-ID correction and pagination status, and records the route decision without leaving another actor or paid-test choice to the next conversation.

## Outside this handoff

Further paid collection, an actor switch, older date windows, internship collection, 1,000/4,000-posting targets, model selection, and student/faculty ranking validation require separate scope and evidence. The next conversation should **execute these four tasks**, not redesign the collection strategy or infer spending authorization from this plan.
