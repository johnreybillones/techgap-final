# JobStreet collection plan

Updated: 2026-10-23 (Asia/Manila). Status: revised planning strategy; no new paid campaign is authorized or running. The [planned data flow](PLANNED_DATA_FLOW.md) owns the meaning of downstream student and faculty results. This plan owns acquisition, query and route selection, spending controls, source preservation, deduplication, collection counts, and the raw handoff. The [brainstorm handoff](JOBSTREET_BRAINSTORM_HANDOFF.md) records why the older junior-only and ESCO-based collection policy was reconsidered.

## 1. Scope and count units

Collect Philippine computing employment postings relevant to BSCS Intelligent Systems, BSCS Game Development, BSIT Network Technology, BSIT Web Development, and common computing work. Include all employment seniority levels. Retain remote jobs when Philippine applicants are eligible. Collect actual internship/OJT vacancies as a separate cohort; they never increase the employment count. Malaysia, Singapore and Indonesia postings form a separate international pool (decided 2026-10-27; see [planned data flow](PLANNED_DATA_FLOW.md) §1) and never increase the Philippine counts. International collection needs its own plan, source-access basis and spending authorization; none exists yet. A search term discovers candidates. It does not prove relevance, track membership, or membership in the curated student-facing career list. Keep an employer's original title even if no curated career match is justified. ESCO occupations are not track or career labels.

The 1,000 distinct-employment figure is a stretch target pursued only while useful incremental yield supports collection, not a hard minimum. The 4,000 figure is a longer-term aspiration subject to the same yield gate, not a minimum, automatic batch, or claim of attainable supply. Do not impose equal track quotas: a posting may support more than one track, but counts once in the employment total. The actual query-limited observation window and track/role sparsity must accompany every result. A single snapshot cannot establish a national market rate or demand trend.

Report these stages separately, for employment and internships where applicable:

| Stage | Meaning |
| --- | --- |
| Returned rows | All provider observations saved, including repeat appearances and invalid items. |
| Billed rows and settled charge | Provider-charged results and reconciled USD; do not infer either from the returned-row count. |
| Distinct source IDs | Stable JobStreet IDs after reuse of the saved registry; multiple queries or versions do not create new IDs. |
| New distinct IDs | IDs absent from the saved registry before the batch. A new ID alone is not a useful job. |
| Likely relevant jobs | Source-backed title/duties screen for computing work and Philippine eligibility, clearly marked provisional until checked. |
| Technically assessable jobs | Relevant postings with enough source duties/qualifications to identify required technical capability groups. A nonempty teaser or title alone is insufficient; preferred-only or unclear requirements do not create a required-skill score. |

The pilot's primary marginal yield is **new distinct, relevant, technically assessable employment postings per billed row and per reconciled USD**. Show every funnel count, the same measures by track/common work, missing-description reasons, and separate internship counts. If billing is unreconciled, the per-dollar measure is unavailable. A small human-checked sample of relevance and technical-text decisions exposes screening errors; it does not turn every provisional decision into reviewed truth or establish population-wide accuracy. Routine collection does not require a person to approve every posting. Do not use older admission decisions or the recent unreliable model run as ground truth.

## 2. Saved evidence and reuse

Keep the original [10-posting field-discovery sample](../../data/collection_samples/jobstreet/README.md) unchanged. The [completed campaign](../../data/job_collections/jobstreet-2026-10-live-preflight) and linked [recovery package](../../data/job_collections/jobstreet-2026-10-live-preflight-dataset-recovery-v1/recovery_manifest.json) preserve already-paid output. The [reconciliation campaign](../../data/job_collections/jobstreet-2026-10-recovered-reconciliation-v1/README.md) has **850 returned observations, 438 distinct JobStreet IDs, and 443 semantic versions across 34 runs**. Those are collection facts, not reviewed relevance or assessability counts. The legacy 46 accepted IDs use a superseded rule and must not be treated as the new employment baseline.

The frozen local ledger lists USD 0.60605. An authenticated read-only check of all 34 saved provider runs on 2026-10-23 found 850 charged result events and USD 0.85850 total run usage; 11 local settlements understate their provider runs. The USD 0.25245 difference is therefore a stale/incomplete local-ledger total, preserved as history rather than silently edited. See the [run-level reconciliation](../../data/job_collections/jobstreet-2026-10-recovered-reconciliation-raw-v2-yield-audit-v1/billing_reconciliation_2026-10-23.json) and earlier [route and billing review](../research/JOBSTREET_ROUTE_COMPARISON_2026-10-23.md). Use reconciled provider run usage for historical cost claims; recheck current account usage and settle every new run before another paid start. Recover an existing paid dataset by resuming that dataset, never by starting a replacement actor run. Preserve original hashes and provenance when creating a separate recovery or reprocessed release.

Before paying again, reprocess the saved descriptions under the current scope. Measure source-ID overlap by query, full-description availability, provisional relevance and assessability, and track/common-work coverage. Check a small sample of those decisions against the original text. Reuse the saved source-ID registry in every later pilot comparison. A changed parser, model, role list, or scoring rule should first rerun saved evidence, not trigger recollection.

## 3. Small query and route pilot

### Query choice

The first paid comparison, if its execution gates are met, uses **six core query starts**: one search string for each of the four tracks, one for common computing work, and one complementary string selected from the saved overlap and text-quality check. Prefer strings that add plausible distinct supply and technical descriptions. Freeze the exact six literal strings and their rationale before seeking campaign authorization; they are not selected merely because a search family has many IDs. Search shared work once. Do not add junior/graduate prefixes by default, since employment at every seniority is in scope. Keep internship discovery strings and results separately visible.

For this bounded pilot, the user selected `data engineer`, `gameplay engineer`, `NOC engineer`, `full stack developer`, `application developer`, and `SOC analyst` in that order. The [disabled pilot configuration](../../data/job_collections/jobstreet-2026-10-recovered-reconciliation-raw-v2-yield-audit-v1/proposed-pilot/collection_config.json) records their IDs and saved-sample comparison. Replacing `front end developer` with `full stack developer` raised the six-query saved-prefix union from 144 to 147 distinct IDs and from 137 to 141 provisionally assessable employment IDs. Those historical capped prefixes do not predict fresh yield or certify relevance. For this small pilot, the user selected an [analyst source-text review](../../data/job_collections/jobstreet-2026-10-recovered-reconciliation-raw-v2-yield-audit-v1/analyst_review_2026-10-23.csv) with provisional labels in place of the planned independent check. This lets the bounded query-yield experiment proceed after its payment gates, but does not satisfy the data flow's independent human-labeled evaluation before trusting downstream rankings.

The historical 34 strings in the appendix are a candidate inventory, not an instruction to rerun all 34. An old query's exclusive IDs show discovery difference, not technical relevance. If a current first-page query repeats the saved prefix or yields no new assessable employment jobs, do not pay to repeat it. Complete the cross-track core comparison within the caps when safe; one weak query does not prove another track or route has no supply.

After the six core starts, at most **two additional starts** may test documented alternatives for a weak track or common-work group. Record the observed gap, the alternative's expected complement, and the comparison rule first. These starts are conditional, not automatic. Do not use them merely to reach eight starts or to repeat a zero-yield prefix. The completed 2026-10-23 paginated-actor test was a separately scoped candidate run; any future paginated route or internship collection still requires its own route/cohort scope and caps, and is not silently included in these eight employment-query starts.

### Route choice

Use the existing `shahidirfan/jobstreet-scraper` first-page route only while bounded comparisons yield new assessable postings with full text. Its documented input lacks a page/offset/sort continuation control, so increasing `results_wanted` does not establish deeper supply. If depth is needed, evaluate `blackfalcondata/jobstreet-scraper` separately: verify its current contract, output fields, complete descriptions, price, source-access basis and page-position evidence, then make a capped page-1/page-2 comparison. Switch only if later pages add distinct relevant assessable jobs at an acceptable settled cost. Local deduplication prevents double-counting, not charges for returned duplicates. The [dated route comparison](../research/JOBSTREET_ROUTE_COMPARISON_2026-10-23.md) is a starting point to reverify, not proof of later-page yield.

### Planning caps and stop rule

| Control | First pilot limit |
| --- | --- |
| Core paid starts | Six, one per frozen core string. |
| Conditional paid starts | At most two after the core funnel is reviewed. |
| Campaign paid starts | At most eight total for this existing-route pilot. |
| Requested results / billed-item control | At most 25 in actor input. The proposed Free-tier execution cap is USD 0.02525, equivalent to one USD 0.0005 start and 25 USD 0.00099 result events under the verified pricing; recheck this arithmetic and provider behavior before use. `maxItems` is not effective for this pay-per-event actor. |
| Per-run charge | USD 0.05 planning ceiling; USD 0.02525 proposed execution cap at the verified Free-tier prices. |
| Campaign charge | USD 0.30 maximum, including all starts and results. |
| Run time | 300 seconds maximum per run. |

These are **planning ceilings**, not spending authorization. The campaign and per-run limits both apply; the pilot stops when either prevents the next start, even if fewer than eight starts occurred. The verified Free-tier event prices imply about USD 0.1515 for six and USD 0.202 for eight 25-result runs, provided every requested result is charged at the checked price. This is a cost estimate, not a yield forecast or a promise of 25 returned rows. Recheck the actor build, account tier, event prices, allowance and cap behavior immediately before execution. [Actor pricing](https://apify.com/shahidirfan/jobstreet-scraper/pricing); [Apify run limits](https://docs.apify.com/api/v2/actors-runs-post).

Execute serially and reconcile each run before another paid start. Stop immediately for an access/contract change, unknown paid-start outcome, unreconciled billing, exceeded or unenforceable cap, incomplete dataset, systematic missing/truncated descriptions, or a repeated prefix with no credible new supply. Save a failed or partial run and its reason; do not silently substitute teasers, start an automatic paid retry, or call a capped request proof of source exhaustion. Review the six-core funnel before either optional start. A large batch is not the automatic next step after this pilot.

## 4. Observation window

Use the most recent **30 days** first. If one or more track/common-work groups remain sparse, test an older window only where the route can demonstrably retrieve older postings, under a separately scoped cap. Consider 90, then 180, then at most 365 days; widen again only when the prior step adds distinct relevant, technically assessable jobs at acceptable cost. Keep the actual publication-date window and cohort on every count. Apply the same stated cutoff when comparing groups, and disclose differences if a later release cannot do so.

The existing actor documents `24h`, `7d`, `30d`, and `anytime`, not exclusive 90/180/365-day retrieval. An `anytime` request plus local filtering does not guarantee older jobs or an archive. Preserve publication, collection, first-observed and last-observed times separately. Do not replace an uncertain publication date with collection time. Retain a usable saved description when a later page becomes an expired shell; closure does not prove a hiring outcome.

## 5. Source access, billing and execution gates

Before any new paid campaign, record an applicable source-authorized basis covering the chosen actor, query strings, date scope and intended use. The [current JobStreet terms](https://ph.jobstreet.com/terms) state a prior-written-consent condition for automated extraction. For this bounded pilot, the user confirmed that their previously handled permission covers the [six accepted searches, pinned actor, fresh 30-day window and same project use](../../data/job_collections/jobstreet-2026-10-recovered-reconciliation-raw-v2-yield-audit-v1/proposed-pilot/source_access_scope_2026-10-23.json); no consent document was inspected. Recheck the applicable terms and preserve the authorization evidence. This plan makes no legal determination.

Also use the run-level historical billing reconciliation, verify available account funds and current pricing, pin/verify the actor build, confirm complete-description output, and record the exact campaign/per-run/result/time/start controls. The pinned actor uses pay-per-event pricing: `maxItems` does not supply a provider-side 25-result cap. At the verified Free-tier event prices, `maxTotalChargeUsd=0.02525` financially limits one start plus 25 billed result events, assuming no other billable events and the provider honoring the cap; it is not a direct item-count limit and does not guarantee 25 returned rows. Stop or recalculate before execution if the account tier, event prices or actor behavior differ. A past USD 0.10 approval, public Free-plan allowance, or the planning USD 0.30 ceiling is not a new campaign authorization. Do not run if any required limit cannot be enforced. Keep credentials in local ignored configuration and out of artifacts/logs.

For an authorized run, reserve the remaining campaign ceiling, start once, save the run ID immediately, poll/resume that run, fetch its dataset, and settle its actual charge. An unknown start outcome requires provider reconciliation before another start. Recheck initially empty datasets against provider metadata and verify downloaded item counts before finalizing zero rows. Preserve a charge discrepancy and stop dependent paid execution until resolved. `results_wanted` is actor input; provider `maxItems` limits chargeable items but does not itself guarantee how many rows the actor returns. The local campaign ledger enforces the aggregate ceiling across runs.

## 6. Raw preservation, identities and handoff

Preserve every returned raw object and field, including full text/HTML, original title, employer, source URL, dates, location, work arrangement and optional salary. Missing salary is recorded, never an exclusion. Retain invalid items with a reason rather than inventing an ID. Use the exact JobStreet source ID as the primary identity (`jobstreet:ph:<id>`). Multiple queries/runs for one ID produce one distinct posting with multiple observation links. Preserve materially changed descriptions as versions, select one coherent full version for a release, and retain the alternatives. Different IDs with similar templates are candidate duplicate links; merge count units only with evidence of the same advertisement.

The raw release must include a compact, traceable index with:

- Stable source ID and URL; original employer title and employer.
- Selected full-description version, raw pointer/hash and alternate-version links.
- Publication/capture dates with uncertainty, location/remote eligibility evidence and source work-type evidence.
- Query, actor/build, run and dataset links; source-ID/duplicate links and selection-policy version.
- Missing-field, invalid-item, completeness and truncation flags.

Retain the complete raw payload beside the index. Do not stamp collector-certified seniority, internship, track, curated career, relevance, or skill labels onto it. The [planned data flow](PLANNED_DATA_FLOW.md) resolves those from source evidence downstream. A valid raw handoff can exist before classification; report unavailable semantic counts as unavailable, not zero. Later corrections regenerate derived decisions from saved raw versions without changing the original evidence or buying the same descriptions again.

Report returned, billed, invalid, distinct, new, provisional relevant, sample-checked relevant, and technically assessable counts separately, along with internships, costs, actual windows and sparse groups. The raw release must have unique source keys, explicit links for every observation or invalid item, and verified artifact hashes. Source URL, title, description and dates must remain auditable through downstream demand and coverage results.

## 7. Sequence and expansion decision

1. **Prepare without spending:** reconcile saved datasets and billing; inspect saved overlap and full descriptions; record the small pilot's analyst review and its provisional status; select and freeze six literal queries, source/date scope, actor build, pricing and caps.
2. **Resolve execution gates:** source authorization, account funds, provider contract and enforceable run/campaign ceilings. Record a separately scoped spending authorization before any paid start.
3. **Run the six-query pilot sequentially:** save full raw output and provenance, reconcile every dataset and charge, deduplicate against saved IDs, and report the employment funnel and separate internships after each run.
4. **Review the core result:** use up to two conditional starts only for a documented coverage gap with a plausible complementary query. Otherwise stop the pilot. Do not treat a search string as a student career name.
5. **Choose the next bounded step:** the 2026-10-23 pagination comparison is complete and remains `pagination_unverified`; Shahidirfan stays the bounded recent first-page default, and the Blackfalcon output is retained as candidate-depth evidence. Reuse saved data and diversify queries during later planning. Any future pagination run or older date-window test needs separate scope and authorization. No further run is scheduled or authorized by this completed test. If measured new assessable yield is adequate across the four tracks and shared work, plan a staged larger batch and remeasure after each batch. No single pilot establishes the 1,000/4,000 targets, representativeness or model accuracy.
6. **Freeze a release:** preserve raw and index hashes, count denominators, query/run/date/cost evidence, missingness, unresolved access or billing limitations, and the provisional versus checked status of relevance estimates.

Do not broaden the campaign, adopt a recurring schedule, switch source/actor, or count internships toward the employment goal without a new scope and measured reason. If supply is unavailable within the twelve-month boundary, report the shortfall. Faculty and student outputs must carry the observation window, distinct-posting denominator and evidence limitations from this collection.

## Appendix: historical query inventory

These 34 literal strings were used as discovery routes in the saved campaign. They are candidates for offline overlap review, **not** the approved six-query list and not curated student-facing career names. Technical relevance and new yield remain unmeasured under the revised policy.

| ID | Literal string | Discovery family |
| --- | --- | --- |
| IS01 | data analyst | Intelligent Systems |
| IS02 | data scientist | Intelligent Systems |
| IS03 | data engineer | Intelligent Systems |
| IS04 | machine learning engineer | Intelligent Systems |
| IS05 | AI engineer | Intelligent Systems |
| IS06 | AI programmer | Intelligent Systems |
| IS07 | computer vision engineer | Intelligent Systems |
| GD01 | game developer | Game Development |
| GD02 | game programmer | Game Development |
| GD03 | game designer | Game Development |
| GD04 | level designer | Game Development |
| GD05 | gameplay engineer | Game Development |
| GD06 | Unity developer | Game Development |
| GD07 | Unreal developer | Game Development |
| NT01 | network engineer | Network Technology |
| NT02 | network administrator | Network Technology |
| NT03 | network support engineer | Network Technology |
| NT04 | NOC engineer | Network Technology |
| NT05 | systems administrator | Network Technology |
| NT06 | cybersecurity analyst | Network Technology |
| NT07 | SOC analyst | Network Technology |
| WD01 | web developer | Web Development |
| WD02 | frontend developer | Web Development |
| WD03 | front end developer | Web Development |
| WD04 | backend developer | Web Development |
| WD05 | back end developer | Web Development |
| WD06 | full stack developer | Web Development |
| WD07 | web application developer | Web Development |
| SH01 | software engineer | Shared/core |
| SH02 | software developer | Shared/core |
| SH03 | application developer | Shared/core |
| SH04 | programmer | Shared/core |
| SH05 | QA engineer | Shared/core |
| SH06 | software tester | Shared/core |
