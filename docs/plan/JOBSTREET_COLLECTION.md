# Plan 1 — Job Data Collection Execution Plan

Updated: 2026-10-22 (Asia/Manila). Companion: [Plan 2 — processing after collection](DATA_FLOW_ACTUAL.md). Decisions: [DECISIONS.md](DECISIONS.md). Change record: [DATA_FLOW_CHANGES.md](DATA_FLOW_CHANGES.md).

**Goal:** Build a reusable, source-backed collection of computing-related Philippine entry/junior advertisements relevant to the four academic tracks, starting with 1,000 accepted postings and expanding toward 4,000 without recollecting or recounting the initial set.

**Boundary:** This plan specifies acquisition, preservation, identity/version handling, admission, collection checks and the handoff. Plan 2 specifies detailed competency extraction, academic matching and analytical computations. These are future execution instructions, not a claim the collector already exists. Writing this plan starts no paid run or schedule.

## 1. Confirmed scope and interpretation

| Item | Instruction or evidence |
| --- | --- |
| Initial target | 1,000 distinct eligible postings: 25% of the 4,000 goal. Size alone does not establish representativeness or model accuracy. |
| Expansion | 4,000 in total, including reusable initial records. An intact eligible 1,000 leaves 3,000 additional postings. |
| Track allocation | The four-track count motivates the 4,000 total. This is not yet an instruction to enforce 1,000 postings per track; show achieved counts by track and retain cross-track advertisements once. |
| Tracks | BSCS Intelligent Systems and Game Development; BSIT Network Technology and Web Development; relevant common/core computing roles. |
| Population | Same entry/junior population for Academic and Student analysis. Exclude internships; unclear/conflicting seniority stays outside analysis until resolved. |
| Geography | Philippine jobs; remote is acceptable when Philippine applicants are eligible. Search country alone is insufficient evidence. |
| Period | Recent first; extend backward only for insufficient supply; never beyond 12 calendar months. |
| Inactive | Include usable captured/recoverable historical descriptions within the chosen period. Closure does not prove hiring. |
| Raw data | Preserve all returned fields, particularly salary and full descriptions. Missing salary never excludes a posting. |
| Money | Approximately USD 5 Free-plan usage is believed available for the whole goal. Verify actual remaining allowance; do not assume additional months or funds. |
| Operation | Automatic ordinary imports; one-time human development checking allowed. No recurring project-team approval queue. |

**Confirmed** identifies a user decision; **observed** identifies saved/measured evidence; **planning default** identifies a concrete engineering proposal; **execution gate** identifies evidence/settings required before a dependent action. Defaults are not measured performance or separately approved spending.

## 2. Existing pilot and reuse

Keep the original [field-discovery sample](../../data/collection_samples/jobstreet/README.md) unchanged. Its input was `web developer`, country `ph`, `posted_date: "30d"`, `results_wanted: 10`, no city restriction, a USD 0.10 run cap and 300-second timeout.

Evidence: [input](../../data/collection_samples/jobstreet/jobstreet-input.json), [actor contract](../../data/collection_samples/jobstreet/actor-contract.json), [run](../../data/collection_samples/jobstreet/run.json), [raw postings](../../data/collection_samples/jobstreet/raw-jobs.json), [inventory](../../data/collection_samples/jobstreet/field-inventory.csv), [checks](../../data/collection_samples/jobstreet/sample-checks.json).

Observed run `5Ie8oVyO2W9EQ8aWI`, dataset `IA9jjL6ESB2SOQnWg`, build `0.0.36` returned ten records, 32 keys and a reported USD 0.0104. All ten had nonempty text/HTML; three source comparisons were recorded without observed missing description sections. Salary appeared in five. Intermediate/experience-conflicting examples mean the ten are not automatically ten eligible junior jobs.

Migration:

1. Hash/import original payloads with their original run/time provenance; never edit the source sample.
2. Apply the current admission/date/quality policy.
3. Credit accepted records toward 1,000; retain excluded/unresolved records and reasons.
4. Reconcile whether the pilot's charge already reduced the verified account balance; do not subtract it twice.
5. Reuse saved descriptions when parsers/models change. A renamed field or changed score formula does not require a new scrape.

## 3. Exact search registry

Use one request per literal string. Query family is a discovery hint; actual duties determine final role/track links. Do not concatenate the list into undocumented Boolean syntax.

| ID | Literal keyword | Discovery family |
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

There are 34 distinct queries. Preserve spelling variants as discovery routes but collapse hits by identity. Search shared roles once, not once per track.

Basis: [curriculum membership CSVs](../../csv/old_curriculum/), [requirements](../requirements/SYSTEM_REQUIREMENTS.md), official [DLSU-D BSCS](https://www.dlsud.edu.ph/academics/degree/undergraduate/bachelor-of-science-in-computer-science) and [BSIT](https://www.dlsud.edu.ph/academics/degree/undergraduate/bachelor-of-science-in-information-technology). CSV titles justify discovery; CSV descriptions/outcomes do not become model competency input. Inspect actual data-engineering and technical-game-design duties instead of assuming every result matches a track.

Exclude nontechnical game-host/casino-dealer/customer-service duties; assess genuine technical software work on its duties. Do not search only technologies currently taught, which would hide novel relevant requirements.

Planning default: add literal junior/graduate-prefixed supplements only after auditing base-query yield. Version every added/removed query with its rationale. Such supplements neither replace broad discovery nor establish an exhausted market.

## 4. Period and historical recovery

### 4.1 One cutoff and adaptive expansion

Freeze `window_end` as a timezone-aware campaign cutoff, with `report_timezone = Asia/Manila`. Membership uses publication time in `[window_start, window_end)`.

Planning default ladder:

1. End minus 30 days.
2. End minus 60 days.
3. End minus 90 days.
4. End minus 180 days.
5. End minus 12 calendar months; stop here.

The increments implement recent-first collection; the 12-month maximum is the confirmed numeric boundary. Calendar-month subtraction clamps to the last valid day if necessary; store the resulting actual timestamps.

At each step union retained eligible records, globally deduplicate and recount. Expand only if accepted supply remains short, money remains and a real route can recover additional older records. Apply the same interval to all tracks; do not quietly give one track older evidence.

Example cutoff `2026-10-22T00:00:00+08:00` permits no date earlier than `2025-10-22T00:00:00+08:00`. If 30 days suffice, twelve months need not be collected. Later campaigns re-evaluate retained records against a new cutoff; frozen earlier releases retain original membership.

### 4.2 Date and inactive evidence

Preserve `postedAt_iso` and `postedAt_display`. Keep publication, collection, first-observed, last-observed and status-observed times separate. Validate ISO dates before preferring them over relative display wording.

A relative-only date retains its original wording, reference observation and inferred interval/precision. Admit it only when window membership is unambiguous. Missing/conflicting/boundary-crossing dates produce `unresolved_date`. Never substitute collection time for publication.

Retain a closed advertisement's full dated eligible description if captured/recoverable. A later expired-page shell cannot overwrite earlier complete evidence. Search disappearance means `not_found_in_search` for that query/time; it does not prove source-wide expiry or hiring. Keep `hiring_outcome = unknown` without authoritative outcome evidence.

### 4.3 Provider limits

The pilot actor documents `anytime`, `24h`, `7d` and `30d`. Apply the 60/90/180-day/twelve-month rules locally; do not invent actor date options. `anytime` does not resurrect deleted advertisements.

Its current contract does not establish an exclusive start-date filter, skip-known-ID list, chronological continuation or expired archive. Its search-results `startUrl` is not an arbitrary detail-page interface. Verify actual controls before using a continuation/history strategy. If requests only repeat the same first results, pause that route rather than repeatedly paying for a prefix.

An alternative adapter requires its own verified contract, full-description check, provenance and budget. SEEK's published terms describe typical 30-day visibility with possible early removal; configured lookback is not obtainable history. See [history research](../research/JOBSTREET_HISTORY_CAPABILITIES_2026-10-20.md), [actor inputs](https://apify.com/shahidirfan/jobstreet-scraper/input-schema), [SEEK product terms](https://ph.employer.seek.com/support/productterms). Establish source-access basis before bulk execution; a marketplace listing alone does not settle source access conditions.

## 5. Admission algorithm

Plan 1 performs only the parsing/classification necessary for eligibility and description usability. Full competency interpretation belongs to Plan 2. Every decision retains source passages.

| Check | Accept | Other result |
| --- | --- | --- |
| Identity | Stable source ID and consistent source URL. | Missing/conflicting identity: unresolved; no array-position substitute ID. |
| Date | Publication unambiguously inside common interval. | Outside: excluded. Missing/conflicting/uncertain: unresolved. |
| Geography | Philippine location or explicit Philippine applicant eligibility. | Other-country-only restriction: excluded. Remote without eligibility evidence: unresolved. |
| Seniority | Explicit junior/entry/graduate/fresh-graduate applicant evidence with no conflicting mandatory requirement. | Intermediate/senior/lead/manager: excluded. Generic title with only experience years, or contradictions: unresolved. |
| Internship | Ordinary employee role. Full/part-time/contract recorded; type alone does not prove seniority. | Internship/OJT/student-placement apprenticeship: excluded. Ambiguous type: unresolved. |
| Relevance | Actual principal technical duties match supported computing scope. | Unrelated duties: excluded; title-only evidence: unresolved. |
| Description | Usable full source description without known truncation/detail failure. | Teaser, expired shell or failed detail: unresolved unusable record, not zero-skill job. |
| Salary | Preserve published or missing/null/empty state. | Never an exclusion or zero-value imputation. |

Do not invent a 0–2-year cap. A generic developer title requiring two years stays unresolved without explicit junior evidence. "Work with senior engineers" describes colleagues. "Fresh graduates welcome" plus contradictory mandatory experience needs contextual resolution.

Use rules on title/metadata and applicant clauses first. When a model is needed, reuse the Plan 2 GLiNER2 candidate and its evaluation protocol; unvalidated model guesses cannot establish admission. Ordinary operators need not manually resolve every case: unresolved records remain outside analysis.

Keep per-check states, then assign one terminal population state:

1. `excluded` if definitive out-of-scope/out-of-window evidence exists; retain all reasons.
2. Otherwise `unresolved` if any required check is unknown/contradictory/unusable.
3. Otherwise `eligible`.

Version decisions. Reprocess saved evidence when admission rules/parsing improve without scraping again. Primary sampling family can remain uncertain even when general computing scope is established; disclose that distinction.

## 6. Persistent duplicate and version handling

### 6.1 Identities

| Name | Definition |
| --- | --- |
| `posting_key` | `jobstreet:ph:` plus exact string source ID; stable across queries, phases and runs. |
| `raw_hash` | SHA-256 of deterministic UTF-8 complete payload serialization: sorted object keys; preserved array order/string/null values. |
| `description_hash` | SHA-256 of description after versioned Unicode/newline/whitespace comparison normalization. Preserve punctuation, technology names and negation; keep original text. |
| `version_id` | SHA-256 of posting key plus semantic-content hash covering description, title/employer/location/salary/work type/publication/status; distinguish missing/null/empty. |
| `observation_id` | Run ID plus dataset item identity/index and payload hash; identifies a retrieval, not a new job. |
| `repost_group_id` | Evidenced same-ad/requisition relationship; every source ID remains traceable. |

Display-age/search-token changes can alter raw payload without changing competency content. Retain observations but reuse parsing when description hash/configuration match. Salary/status changes preserve context versions without increasing demand.

A frozen release selects one usable version per count unit as of its observation cutoff. Never count all content versions as separate jobs.

### 6.2 Import algorithm

```text
validate source ID/URL; save original payload
key = "jobstreet:ph:" + source_id
create registry entry only if key is new
append observation/query/run link only if observation_id is new
append version only if semantic-content version is new
retain earlier full content when new retrieval is blank/expired
re-evaluate admission when relevant fields or policy changed
count accepted identity once in the selected release
```

Enforce unique posting/version/observation identities with transactional writes. A local single-process registry is sufficient initially; later concurrency requires atomic upserts/unique constraints. Reimporting a saved run after a crash cannot add jobs/observations or trigger another paid request.

### 6.3 Different-ID repetition

1. Generate candidates from employer ID, normalized title, location and description hash; preserve all source IDs.
2. Group as the same advertisement only when stable requisition/source evidence supports that identity.
3. For a confirmed group use its first source publication for the twelve-month rule; retain reappearance times separately. Do not rejuvenate a confirmed old ad by changing its ID/date.
4. Similar text/template alone gives `possible_repost`, without silent merging.
5. Confirmed ad groups are count units where established; otherwise posting keys are count units. Report conversions from source-key totals separately.
6. Plan 2 uses exactly this identity in counts/denominators. Keep possible repeats together for evaluation splitting to reduce leakage.

### 6.4 Preventing repeat charges

Skip known complete IDs before detail fetch **only if the adapter supports ID discovery/targeted detail requests**. Resume supported cursors/pages/incremental state after saving outputs. Those capabilities are not established for the pilot contract.

For prefix-only search: reuse local data first; forecast the cost of the whole repeated prefix; increase limits only for a bounded, justified new-supply request within funds; pause zero-new-result routes; evaluate another verified adapter if needed. Local duplicate prevention cannot reverse charges for returned duplicates.

## 7. Artifacts and raw-field contract

Proposed root: `data/job_collections/<campaign_id>/`, with a shared registry across phases/campaigns. These artifacts are future outputs.

| Artifact | Required contents |
| --- | --- |
| `collection_config.json` | Schema/query/admission versions; targets; cutoff/window; geography; actor/build; batch/time/charge caps; verified allowance timestamp; source-access basis; stop rules. |
| `query_registry.json` | Exact queries, IDs, hints, rationale and enabled/superseded states. |
| `raw/<run_id>/items.jsonl` | Every unchanged returned object, all HTML/text/metadata/salary and null/empty states. |
| `runs.jsonl` | Sanitized input/options, actor/build/run/dataset IDs, UTC start/end/status, caps, warnings, exposed pagination and actual charges/events. |
| `postings.jsonl` | Posting key, source URLs/IDs, first/last observation, versions and count-unit links. |
| `versions.jsonl` | Semantic hash/version, source fields, raw pointer/hash, prior version and full-content availability. |
| `observations.jsonl` | Observation/posting/version/run/query IDs, retrieval time/outcome, source status and raw pointer. |
| `admission.jsonl` | Per-check evidence/states, terminal decision, reasons, policy/model and decision time. |
| `repost_candidates.jsonl` | Members, candidate basis, identity evidence, confirmed/unresolved result and counting effect. |
| `eligible_frame.jsonl` | Frozen accepted count-unit IDs, selected versions, dates and role/track evidence. |
| `collection_audit.json` | Actual quantities/dates, family/track/month composition, failures/caps, duplicate yield, missingness, spend and limitations. |
| `manifest.json` | Release/config/policy IDs, artifact hashes, target/achieved count, evidence cutoff, restrictions and previous release. |

Observed source fields include `id`, `url`, `title`, `company`, `employerId`, `advertiserId`, `location`, `salary`, `workType`, `classification`, `subClassification`, `postedAt_iso`, `postedAt_display`, `workArrangements`, `description_html` and `description_text`. Preserve the entire object even when unused. Derived field names above are not claimed actor fields.

Salary example: retain `"₱30,000 – ₱35,000 per month"` unchanged. No conversion, imputation or salary weighting is required. Missing, null, empty and zero are distinct.

Store normalized UTC timestamps plus original timezone/precision; reporting timezone is separate. Use temporary-file validation and atomic replace for artifacts. Do not put credentials/authentication headers in logs/manifests.

## 8. Cost computation and controls

Public metadata checked 2026-10-22 lists Free-tier `p = 0.00099 USD/result` and `s = 0.0005 USD/start event`. Start units depend on allocated GB, with minimum one. [Actor metadata](https://api.apify.com/v2/acts/shahidirfan~jobstreet-scraper), [pricing](https://apify.com/shahidirfan/jobstreet-scraper/pricing).

```text
event_cost = p * billable_returned_items + s * start_event_units
yield = new_accepted_count_units / billable_returned_items
expected_extra_rows = ceil(remaining_accepted_target / measured_nonzero_yield)
expected_extra_cost = p * expected_extra_rows + expected_start_cost
```

Yield is a measured forecast, not a promise; preserve query/date basis and declining marginal yield. Reconcile actual reported charges and do not double-add compute already included in actor pricing.

| Result events | Result charge alone | Boundary |
| --- | --- | --- |
| 1,000 | USD 0.9900 | Returned rows may be duplicate/ineligible. |
| 3,000 | USD 2.9700 | Not necessarily 3,000 new eligible count units. |
| 4,000 | USD 3.9600 | USD 1.04 remains from a hypothetical USD 5 before starts/other usage. |

The public [Free plan](https://apify.com/pricing) lists USD 5 monthly usage, not this account's remaining balance. Do not assume renewed allowance, promise 4,000 within USD 5, or use account rotation to bypass controls.

Execution procedure:

1. Verify actual available allocation; set campaign ceiling to `min(5.00, verified_allocation)`.
2. Reconcile prior pilot/other usage with the verified balance without double subtraction.
3. Planning default: serial requests of up to 25 results and 300-second timeout. These are engineering controls, not proven source-completeness limits.
4. Before each run, reserve an explicit run-level charge cap within account and unreserved campaign funds. Include start units/current rates/applicable other charges.
5. Release unused reservation only after actual charge reconciliation. No uncapped fallback when the interface cannot enforce the chosen ceiling.
6. No automatic paid retries. Serial execution prevents concurrent reservations spending the same balance.
7. Reforecast after each batch; pause an unaffordable target rather than spend the remainder while promising success.
8. This plan starts no new paid run; the old USD 0.10 approval was for one completed test.

`results_wanted` is actor input; `maxTotalChargeUsd` and timeout are run controls. Verify their exact interface in [Apify run API](https://docs.apify.com/api/v2/actors-runs-post)/[MCP docs](https://docs.apify.com/mcp). Returned-item limits are not total-cost caps.

### 8.1 Live adapter: purpose, current status and process

A live adapter is the local bridge between this campaign and Apify's existing JobStreet actor. It starts the actor with the registered search settings, waits for the run, saves its dataset and run evidence, then sends the saved items through the importer. It automates acquisition; it does not change how the actor searches, create historical access or guarantee eligible supply.

**Observed repository status (2026-10-22):** The repository now implements an offline-by-default, one-query Apify adapter in `scripts/jobs/apify_adapter.py`, durable request/budget state in `scripts/jobs/acquisition_state.py`, `collect --dry-run/--preflight/--execute`, `resume`, metadata-aware import, and release billing/provenance reporting. Network behavior was checked only with injected fakes; no account preflight or paid run has been performed. Current balance/access authorization, actual runtime billing visibility, successful live recovery, and description checks remain unverified. The live pilot is still pending.

The adapter now provides the automatic local collection route. Operators can also use Apify Console followed by a JSON dataset export and the `import` operation; the same budget, provenance and admission rules apply. Console execution still requires its own bounded collection authorization.

Planned live process:

1. Load `APIFY_API_TOKEN` from the environment or local `.env`, keeping it out of saved artifacts and logs; validate the campaign, registered query, frozen date window, result limit and spending controls.
2. Reserve the run cap under section 8 and start the verified actor/build with the matching input. The pilot resolved to build `0.0.36`; future calls must explicitly pin and verify the build rather than rely on `latest`.
3. Save the returned run ID immediately, poll that run to completion and resume it after interruption without starting another paid run.
4. Retrieve its default dataset with all fields preserved; checkpoint downloads and save complete raw items plus sanitized run/dataset/build/status/time/charge metadata.
5. Import the saved dataset using the original run ID and registered query ID, retain dataset provenance, reconcile charges and report returned versus new eligible records before another request.

Use the asynchronous start/poll/fetch flow documented in [Apify's run-and-retrieve guide](https://docs.apify.com/academy/api/run-actor-and-retrieve-data-via-api). The detailed file changes, recovery rules, proposed commands, implementation tasks and acceptance checks are in the separate [JobStreet live adapter implementation plan](JOBSTREET_LIVE_ADAPTER_PLAN.md). That document is a proposal: neither these instructions nor its example commands implement the adapter or authorize a new paid run.

## 9. Acquisition sequence

### C1. Prepare and resume safely

- [ ] Freeze config/query registry, cutoff and targets; create campaign/release IDs.
- [ ] Import pilot under section 2; load shared identities and actual spending ledger.
- [ ] Verify actor/build/contract, available allowance, source-access basis, full-description output and actual continuation controls.
- [ ] Create raw export/checkpoint paths before any request.

**Exit:** known budget, identifiable scope and idempotent saved-data import. A missing financial/access/control fact stops only dependent execution.

### C2. Request a bounded query round

Planning default: for indices 1–7 interleave available IS, GD, NT and WD queries; interleave SH01–SH06 one at a time. Visit each base query once before repeatedly favoring one family. Use country `ph` and no city filter.

Up to 25 returned items per query yields at most 850 first-round items. Result-event estimate: `850 * 0.00099 = 0.8415 USD`, plus starts. This distributes discovery effort, not actual market proportions.

Save input/output/run/charge evidence after every request. Reached caps, failed routes, teaser-only responses and unknown pagination produce explicit incomplete-coverage reasons.

### C3. Import and classify each batch

1. Validate item identity/type; save unchanged raw output and schema inventory.
2. Apply section 6 idempotent posting/version/observation handling.
3. Preserve all descriptions/context.
4. Apply section 5 admission with source passages.
5. Record principal family and supported multi-track links from duties, retaining ambiguous classification.
6. Reconcile billed/raw/new/reused/excluded/unresolved/accepted counts and update marginal yield.
7. Select one usable version per count unit. Multiple query/track links do not multiply total jobs.

### C4. Continue, widen or stop

If target is short, first visit unvisited routes in the common interval. Use supported continuation for more results; prefix repeats require section 6.4's cost check. When recent recoverable supply is insufficient, widen using section 4 and retain previous identities.

Stop reasons: `target_reached`, `budget_exhausted`, `unaffordable_projection`, `recoverable_source_exhausted`, `continuation_unavailable`, `max_lookback_reached`, `contract_changed` or `run_failed`. A capped request cannot prove source exhaustion. Unobtainable history is a documented shortfall, not permission to invent an archive or exceed twelve months.

### C5. Freeze a checked release

Resolve integrity failures and produce sections 10–11 artifacts. `complete_target` means achieved requested count, not actual market coverage. `development_only_shortfall` can describe an honest smaller release. Broken identities/hashes/raw evidence produce `invalid_handoff` and block dependent processing.

## 10. Allocation and reliability limits

Do not force 312/313 records per track. Tracks overlap, and equal quotas do not preserve observed role proportions. Search heading totals do not supply eligible population counts.

**Budget-conscious default:** retain eligible unique records from bounded multi-query discovery until target/stop. Describe actual role/month/employer/location composition as a query-limited development cohort. Do not pay for 4,000 descriptions simply to discard 75%. Equal query batches are not a national probability sample.

If a sufficiently defined eligible observed frame already exists without unnecessary paid detail retrieval and a subset is needed:

1. Assign each count unit one principal-role-family × posting-month stratum; mixed/unclassified gets its own stratum. Multi-track applicability remains separate.
2. For frame `N`, target `n` and stratum `N_h` compute `q_h = n * N_h / N`.
3. Allocate floors, then largest fractional remainders; break allocation ties by stratum ID.
4. Sample without replacement with saved seed/stable ID ordering.
5. Save frame hash, selected IDs, `N_h`, `n_h` and inclusion fraction `n_h/N_h`.
6. Use `n = min(target, N)`. A zero-selected tiny stratum supplies no subgroup estimate.

This conditional policy preserves that observed frame, not an unmeasured market. No such validated complete frame exists today.

Report actual family/track/month/employer/location counts, missingness, caps/failures and repeated-template concentration. Do not invent a subgroup minimum or call sparse roles reliable. Balanced difficult-case evaluation samples have separate flags and cannot silently alter demand prevalence.

References: [Cedefop job-ad representativeness](https://www.cedefop.europa.eu/it/publications/6217), [Statistics Canada sampling manual](https://www150.statcan.gc.ca/n1/pub/12-587-x/12-587-x2003001-eng.pdf). These explain methods/bias checks; neither certifies this collection.

## 11. Handoff to Plan 2

Deliver a frozen **raw-evidence release**, not a skill dataset already derived by models.

```json
{
  "schema_version": "job-collection-v1",
  "release_id": "campaign-and-release-identifier",
  "phase": "initial_1000",
  "requested_target": 1000,
  "achieved_eligible_count": 0,
  "window_start": null,
  "window_end": null,
  "report_timezone": "Asia/Manila",
  "count_unit_policy_version": "source-id-with-evidenced-repost-groups-v1",
  "admission_policy_version": "explicit-entry-junior-v1",
  "membership_file": "eligible_frame.jsonl",
  "membership_sha256": null,
  "artifact_hashes": {},
  "reported_charge_usd": 0,
  "release_status": "not_executed",
  "limitations": []
}
```

This is an unexecuted schema example, not a completed dataset. Release generation fills actual times/counts/hashes; required measured values cannot stay null in a successful handoff.

Required checks:

- One selected full usable version/raw hash/source identity per accepted count unit.
- Accepted date/geography/seniority/internship/relevance/description checks.
- Every returned raw field retained, with explicit salary missingness.
- Query/run links and selection/identity policy versions.
- Requested versus achieved counts/windows, spend and incomplete routes disclosed.
- Within reconciled unique source-key scope: `raw_unique = eligible + excluded + unresolved`. Report confirmed-ad-group conversion separately from source-key totals.
- Every artifact hash validates before model processing.

A valid manifest can still be undersized or coverage-limited; Plan 2 carries those restrictions forward.

## 12. Collector verification cases

These are future implementation acceptance cases, not tests executed by writing this plan.

| Case | Expected outcome |
| --- | --- |
| Same ID in two queries | One posting/count unit, two query links, saved observations. |
| Reimport same run | No extra postings/versions/observations or paid request. |
| Revised requirements under same ID | One posting, multiple versions; release selects intended version. |
| Salary-only change | Context version retained; unchanged competency cache reusable. |
| Complete description followed by expired shell | Full saved evidence preserved; shell recorded separately. |
| Different IDs share template | Candidate link; no unsupported automatic merge. |
| Internship or uncertain generic seniority | Excluded/unresolved rather than admitted to fill quota. |
| Unknown date/remote country | Unresolved evidence, no invented timestamp/eligibility. |
| Expand 1,000 toward 4,000 | Initial IDs reused; only new accepted count units increase total. |
| Charge/result/time cap or source failure | Correct stop/coverage state and actual spend/shortfall. |
| Changed schema/missing detail | Contract failure; raw saved; no silent teaser fallback. |

Source-check development cases across families/layouts, missing salary and ambiguous admission; compare source text with saved output. Record checked IDs, discrepancies and inaccessible pages. Choose case coverage from actual available records and disclose the checked count. The old three-source check does not certify the expanded collection.

## 13. Expansion, updates and retention

After initial development evaluation, expand the shared registry using remaining verified funds and supported routes:

```text
additional_needed = max(0, 4000 - currently_eligible_reusable_count_units)
```

It equals 3,000 only if all initial 1,000 still qualify. Re-evaluate date/policy changes; do not credit records that aged out or failed revised checks.

Freeze initial study/evaluation evidence. New records create a new release rather than rewriting held-out labels or earlier reports. Keep duplicate families grouped across evaluation partitions.

Ongoing collection remains in scope, but no paid weekly/monthly cadence is adopted under the current allowance. Acquisition and report-refresh cadence are separate future measured/funded choices. Retain closed evidence needed by the chosen cohort/reports/evaluation. Inactive does not itself mean deletable; lifecycle duration and report reproducibility must be established before deletion.

## 14. Implementation work products and order

These are proposed files, not existing commands:

| Order | File | Responsibility and exit evidence |
| --- | --- | --- |
| 1 | `scripts/jobs/contracts.py` | Raw/config/run/manifest validation; invalid items retained with reasons. |
| 2 | `scripts/jobs/registry.py` | Transactional identities/versioning; idempotent saved-run import. |
| 3 | `scripts/jobs/admission.py` | Evidence-bearing section 5 checks and terminal states. |
| 4 | `scripts/jobs/apify_adapter.py` | Verified build/input/run controls, capped serial retrieval, raw export and actual-charge ledger. |
| 5 | `scripts/jobs/collect.py` | Section 9 query/window loop, checkpoints and stop reasons; default configuration inspection before provider execution. |
| 6 | `scripts/jobs/release.py` | Frozen IDs, hashes, audit and section 11 manifest, deterministic regeneration. |
| 7 | `tests/collection/` | Fixture acceptance cases in section 12; live calls require an authorized bounded collection. |

Expose separate prepare/import/validate/collect/freeze operations; importing a module or validating saved data cannot trigger a paid request. Establish final CLI syntax during implementation rather than pretending these proposed paths already run.

First-phase completion means an audited valid handoff with actual achieved count/restrictions. It does not certify downstream models, national demand or that 4,000 accepted jobs fit USD 5.
