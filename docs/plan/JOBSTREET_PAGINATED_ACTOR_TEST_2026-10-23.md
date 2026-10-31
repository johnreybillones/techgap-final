# JobStreet paginated-actor test plan

Updated: 2026-10-23 (Asia/Manila). **Status: bounded test completed; no further paid start is authorized by this document.** The saved result was reconciled offline in [`Blackfalcon reconciliation v2`](../../data/job_collections/blackfalcon-data-engineer-paginated-20261023-reconciliation-v2/report.md). The proposal below is retained as historical test contract; the run produced 16 new IDs and 15 provisional assessable relevant employment IDs, but pagination remains `pagination_unverified`. Shahidirfan remains the bounded first-page default. This result does not authorize a larger collection, recurring schedule, or actor switch. [JobStreet collection policy](JOBSTREET_COLLECTION.md) remains authoritative for count units, source preservation, and spending controls.

## Completed test result

The saved exact request used one `data engineer` query, `maxPages=2`, `maxResults=50`, and a USD 0.11 cap. The completed run returned and billed 50 rows at USD 0.11. ID-keyed reconciliation confirms 50 unique IDs, 34 already in the frozen 467-ID registry, 16 new IDs, and a 483-ID combined union. Fifteen of the 16 new IDs have source text supporting technical assessment; one has no description. These remain provisional source-text judgments, not human-reviewed admissions. The run exposed 22 rows without explicit page evidence and six rows marked page 3 despite the two-page cap. The saved request artifact records `request_sent=false`, and run metadata does not expose the submitted actor input body, so the actual input fields cannot all be independently confirmed. The route decision therefore retains `pagination_unverified`.

No follow-up run or actor switch is scheduled or authorized. Reuse saved data and diversify queries during later planning.

## Decision to answer

Does one capped, two-page `data engineer` search produce **new, relevant, technically assessable Philippine employment postings** beyond the saved JobStreet registry at an acceptable settled cost? The first test prioritizes proof of later-page yield using a query that previously returned clear technical work. A separate test would be needed to judge Game Development or SOC coverage.

The completed six-query pilot returned 150 rows, 148 distinct IDs, and 29 IDs absent from the prior 438-ID registry. The source-linked audit found 29 likely relevant and technically assessable employment IDs in the new set; these are source-audited provisional outcomes, not human-reviewed jobs. The generic screen passed 27 and failed two: one short but skill-explicit description, and one reporting role whose required Microsoft Office capability and optional BI tools did not match the screen vocabulary. The `data engineer` query contributed 9 new IDs, 8 of which passed that generic screen. The proposed comparison registry has **467 distinct IDs** (438 prior plus 29 pilot), and its membership and selected-version hash are recorded before any candidate run. [Pilot reconciliation](../../data/job_collections/jobstreet-2026-10-six-query-pilot-20261023/final_reconciliation_2026-10-23.json); [source-linked audit](../../data/job_collections/jobstreet-2026-10-six-query-pilot-20261023/new_id_yield_audit_2026-10-23.csv).

## Why one 50-result run

The candidate actor documents `maxPages`, `maxResults`, full-description retrieval, and about 22–32 listings per page. Its example item carries a `searchUrl` with `page=2`. Fifty emitted results should be enough to encounter a second page when that query has sufficient supply, while keeping the proposed single-run charge at **USD 0.11**: USD 0.01 start plus at most 50 × USD 0.002 results. Fifty may cover only part of page 2; the test cannot establish exhaustive depth. Missing page evidence or fewer than enough results makes the page-specific conclusion inconclusive, not a reason to retry automatically. [Input schema](https://apify.com/blackfalcondata/jobstreet-scraper/input-schema), [output example](https://apify.com/blackfalcondata/jobstreet-scraper), [pricing](https://apify.com/blackfalcondata/jobstreet-scraper/pricing).

## Phase 1 — Complete the saved-data baseline without spending

1. Inspect the 29 new pilot IDs against the saved raw descriptions. Save a source-linked audit of employment/internship status, Philippine eligibility, technical relevance, usable required-capability text, track/common-work links, and the two text-screen failures. Keep automated screen labels provisional and distinguish checked examples from collection-wide counts. A search query is not a track label.
2. Reconcile the exact 438-ID prior frame, 148-ID pilot frame, 29 new IDs, and 467-ID combined registry. Record the registry membership hash and selected raw-description version for each source ID. Do not treat the old legacy admission results as current eligibility truth.
3. Correct the completed pilot's stale README, freeze its raw-v2 manifest after the audit is saved, and run release validation. Confirm observation-to-raw links, file hashes, window, counts, and USD 0.15150 provider-reconciled charge. The pilot currently has no `manifest.json`.
4. Compute the pilot's checked or clearly provisional `new relevant assessable employment IDs / billed row` and `/ settled USD` baseline. The 29-ID audit yields 29/150 = 0.1933 per billed result row and 29/USD 0.15150 = 191.42 per settled dollar; these are provisional source-text judgments, not human-reviewed counts. Keep the denominator, query set, and UTC window with every measure.

## Phase 2 — Build and preflight the candidate route without spending

The current `scripts/jobs/apify_adapter.py` is pinned to the original actor/build and the importer expects `id` plus `url`. Changing only the actor name in its config would bypass or fail those checks. Add a separate candidate adapter and focused tests before any paid start; reuse the existing transport, campaign reservation, recovery, and raw-release patterns where their contracts fit.

The adapter must:

- Preserve each candidate item unchanged, with actor/build, run, dataset, query, capture time, and raw hash.
- Verify that the numeric `seekJobId` equals the final ID in the Philippine `canonicalUrl`, then normalize to `jobstreet:ph:<id>`. The candidate's `jobId` is a different identifier in its published example and must not become the cross-actor source key. Missing or inconsistent IDs remain linked invalid observations.
- Map `description`/`descriptionHtml`, title, employer, location, employment type, and publication date into a versioned derived view while retaining the complete candidate payload. Never overwrite the original actor's raw data or silently merge different source IDs.
- Retain `searchUrl` and derive a page number only when its URL and query evidence support it. Do not infer page 2 from dataset order alone.
- Exercise fixture tests for ID/URL agreement, missing fields, full-text preservation, page evidence, duplicate IDs, a changed description, and import/release validation.

Immediately before any authorized run, check the candidate's live actor/build identity, input/output contract, active event prices, account allowance, minimum charge cap, and the effective Apify run options. The user confirmed in this conversation that their existing JobStreet permission covers this candidate actor and bounded TechGap test; record the exact actor, query, window, and use in the campaign evidence. JobStreet's published terms require prior written consent for automated extraction; this plan does not establish the contents of an unseen permission document. [JobStreet terms](https://ph.jobstreet.com/terms).

## Phase 3 — Proposed single-run contract

| Control | Proposed value |
| --- | --- |
| Actor | `blackfalcondata/jobstreet-scraper`, build pinned after live preflight |
| Search | One literal `data engineer` query; `country: "PH"`; no extra `startUrls` or query batch |
| Window | Fresh 30-day UTC interval frozen immediately before the start; actor `dateRange: "31"`, `maxAgeMinutes: 43200`, and absolute `fromDate` / `toDate` bounds equal to that frozen interval, with local verification of every publication date |
| Page/order | `maxPages: 2`, `sortMode: "relevance"` |
| Output | `maxResults: 50`, `includeDetails: true`, `compact: false`, `descriptionMaxLength: 0`, `descriptionFormat: "all"`, `includeApplicantInsights: false`, `incrementalMode: false` |
| Spend | One start; actor input limit 50; Apify `maxTotalChargeUsd: 0.11`; local campaign ceiling USD 0.11; no automatic paid retry |
| Recovery | Persist the request and run ID immediately; if the start outcome is unknown, reconcile that start rather than issuing another POST |

The actor's date filters are documented as post-collection filters. They do not prove that all jobs in the 30-day window were searched, and the new window will differ slightly from the completed pilot's frozen window. Record both windows and compare IDs against the frozen registry. Apify documents `maxTotalChargeUsd` as the run's total-cost cap; verify its effective value on the returned run before treating the request as safely bounded. [Date fields](https://apify.com/blackfalcondata/jobstreet-scraper/input-schema), [run API](https://docs.apify.com/api/v2/actors-runs-post).

**Execution gate:** obtain a separate, explicit spending authorization for this exact actor, query, frozen window, one-start rule, and USD 0.11 maximum. Selecting these values for the written plan is not that authorization. Do not start if source-scope evidence, fresh prices/funds, build pin, full-detail contract, or either cap cannot be verified.

## Phase 4 — Run, reconcile, and inspect

1. Save the exact sanitized request and current contract snapshot. Reserve USD 0.11 in a new campaign ledger, start once with `restartOnError: false`, and save the returned run ID before polling.
2. Fetch the existing run's dataset and run metadata. Recheck initially empty or partial datasets against provider item counts; resume the same run/dataset when needed. Settle actual `usageTotalUsd` and charged events against the local ledger before interpreting cost.
3. Preserve all returned raw items and invalid items. Confirm emitted rows, billed events, IDs, full-description availability/truncation, and `searchUrl` page evidence. Any error, charge discrepancy, contract mismatch, unknown start, or incomplete download stops paid execution; it does not trigger a replacement run.
4. Compare valid JobStreet IDs to the frozen 467-ID registry. Inspect new IDs' source text for Philippine employment eligibility, relevance, required technical capabilities, and track/common-work links. Keep provisional decisions and a small checked sample distinguishable.

## Report and decision rule

Report separately: returned rows; billed results and settled USD; invalid records; distinct IDs; IDs already saved; new IDs; new relevant employment IDs; new technically assessable employment IDs; missing/short descriptions; page-1 and page-2 counts where `searchUrl` proves page; and the same new/usable counts by page. Also report IDs or versions shared with the prior actor. Query membership must not establish a role or track link. The within-run page-1 versus page-2 comparison is the primary pagination evidence. The earlier `data engineer` query and six-run pilot are historical cost references, not a simultaneous actor A/B test: the registry and collection time have changed.

**Route proof:** at least one valid, previously unseen, relevant and technically assessable ID must have supported page-2 provenance and a usable full description. If page provenance cannot be established, report `pagination_unverified` even if there are new IDs.

**Budget comparison:** compare new assessable employment IDs per settled USD with the audited six-run baseline using the same label rules. At the source-audited provisional 29-ID baseline, a full 50-row USD 0.11 test would need **22** new assessable IDs to match the pilot's jobs-per-dollar rate. Page-2 supply can still justify a separately scoped follow-up for a sparse track, but it does not authorize scale by itself.

**Next decision:** recommend a wider candidate-actor pilot only if page-2 supply, full-text quality, source-ID mapping, and settled marginal cost are credible. Otherwise retain the saved data, investigate query choice or a different route offline, and stop paid testing. No 1,000/4,000-posting target or market-trend claim follows from this test.
