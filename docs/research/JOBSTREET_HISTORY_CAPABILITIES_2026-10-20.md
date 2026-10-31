# JobStreet collection and historical availability — 20 October 2026

**Decision update, 2026-10-22:** The user selected recent-first acquisition, expanding only if needed up to twelve months, rather than requiring a complete retrospective six-month archive. [Plan 1](../plan/JOBSTREET_COLLECTION.md) supersedes the six/twelve-month recommendations below. Availability limits remain; cadence and actual remaining allowance require execution evidence.

Status: read-only primary-source capability research. No actor was run, no job collection was started, no budget was spent and no account, schedule or source permission was changed. These findings inform the collection plan; they do not reopen the deferred scoring/ranking choices.

## 1. Findings that determine the feasible history plan

**Neither inspected actor documents a complete retrospective six- or twelve-month archive of Philippine JobStreet postings.** Both search the obtainable source listings. An older date condition can select an old record that is still obtainable, but cannot reconstruct an ad already removed from the source. `anytime`, date post-filters and an `isExpired` field must not be described as historical-archive access.

This limit is material: SEEK's current Philippine product terms state that ads normally remain posted for 30 days and may be removed earlier. The advertising terms allow extension and early expiration. Consequently, an ad's disappearance is not proof the role was filled; an ad can age out or be withdrawn. [Philippine product terms, Common Terms §2(c)](https://ph.employer.seek.com/support/productterms), [advertising terms §53(c)](https://ph.employer.seek.com/support/termsconditions).

The Philippine JobStreet website terms also explicitly acknowledge that a vacancy can have been filled before its ad is removed. Therefore even a still-displayed ad does not establish an unfilled vacancy. Retain **advertisement availability** separately from **hiring outcome**, with the latter unknown unless independently supported. [Website terms §10(m)](https://ph.jobstreet.com/terms).

The defensible distinction is:

- **Retrospective request:** collect all relevant postings published during a past six/twelve-month interval, including ads no longer obtainable. No usable archive supplying that population was established by this research.
- **Current recoverable snapshot:** collect discoverable postings now, preserve their actual source dates/statuses, and describe the dates and limitations actually obtained. Some older or expired detail content might remain obtainable; this was not tested and cannot be promised.
- **Prospective observation archive:** retain postings as they are observed, including their complete descriptions and raw context. Later observations/status changes can mark them unavailable while preserving the earlier evidence. Once observations span six/twelve months, that retained collection can support the corresponding observed window, subject to its known capture gaps.

## 2. Pilot actor: shahidirfan/JobStreet-Scraper

The current Apify metadata/input/output/pricing lookup was performed on 20 October 2026. Actor ID `f7ggUvGaOrrUuPkZQ`; metadata reports modification on 7 October 2026. This live lookup independently confirms the contract saved during the earlier pilot; the local [actor contract](../../data/collection_samples/jobstreet/actor-contract.json) is a historical artifact, not the authority for current pricing/capabilities.

| Capability | Current verified documentation | Consequence |
| --- | --- | --- |
| Dates | `posted_date`: `anytime`, `24h`, `7d`, `30d`; default `24h`. | Longest explicit rolling recency option is 30 days. `anytime` removes that recency restriction; no documented archive follows. |
| Country | Keyword/location mode accepts `country: "ph"`. | Use the Philippine site; source/site selection alone does not establish remote-work residency eligibility. |
| URLs | `startUrl` is for a search-results page and overrides keyword/location mode. | The README explicitly excludes individual `/job/<id>` detail URLs as this input. Dates must be encoded in the search URL when this mode is used. |
| Result cap | `results_wanted` is the requested maximum. | It is not a promise of that many relevant, unique or complete records. |
| Paging/sort controls | No explicit `maxPages`, start-page or sort field appears in the current input schema. | Do not invent accepted input keys or an exhaustive-pagination guarantee. Search-URL behavior beyond documented settings requires verification. |
| Status/detail evidence | Output includes `detail_status`, `isExpired`, descriptions, IDs/URLs, posting/collection times and salary when published. | These are record fields; no expired-only or historical-discovery switch is documented. |

Sources: [current input documentation](https://apify.com/shahidirfan/jobstreet-scraper/input-schema), [actor README, especially URL instructions and output fields](https://apify.com/shahidirfan/jobstreet-scraper). The Apify metadata tool supplied the current schema and inferred output types; inferred types do not guarantee field completeness in every posting.

The existing pilot proves ten records were saved with build `0.0.36`; it does not prove a production query can obtain a requested larger quantity, exhaust its results or recover expired listings. No current actor execution was performed here.

## 3. Alternative: blackfalcondata/jobstreet-scraper

A current read-only Apify metadata/input/output/pricing lookup was also performed on 20 October 2026. Actor ID `7kznL2vbJaceNOPHS`; metadata reports modification on 19 October 2026. Its additional controls make it a **candidate for a separately approved bounded capability test**, not an adopted replacement or a validated archive.

| Control | Current documented behavior | Important limit |
| --- | --- | --- |
| `dateRange` | Source recency codes `1`, `3`, `7`, `14`, `31` days. | No six/twelve-month code. The current MCP schema makes this field optional; omit it for an unrestricted recency search rather than assuming an empty string is accepted. |
| `fromDate`, `toDate`, `maxAgeMinutes` | Conditions applied after collection; ISO dates/datetimes accepted for the first two. | They select retrieved records. They do not recover records absent from search/detail availability. |
| `startUrls` | Accepts search/category pages and individual `/job/<id>` URLs. Detail URLs skip search pages; supplied sources are added to any query search. | A known URL is needed for direct detail retrieval. The documentation does not guarantee removed/expired content remains retrievable. Do not accidentally add the default query when intending a URL-only test. |
| `maxResults` | Default 100; `0` removes this actor result cap; applied after post-filters. | Unlimited actor output is not unlimited source availability and is unsuitable as an unbounded cost setting. |
| `maxPages` | Default 5 per search source; schema describes roughly 22–32 listings per page. | The page window can bind before the requested result count; the source's hard result/pagination maximum was not established. |
| `sortMode` | `relevance` or `date`; default relevance. | Relevance order is not a random sample or chronological coverage guarantee. |
| Details | `includeDetails: true`; source descriptions and raw salary text can be retained. | Use untruncated text/HTML for competency extraction; compact or truncated output can remove needed evidence. |
| Incremental tracking | `incrementalMode`, `stateKey`, `emitUnchanged`, `emitExpired`; default emissions are new/updated/reappeared records. | Tracking begins with a baseline; it does not recover listings that vanished before that baseline. |

Sources: [current input documentation](https://apify.com/blackfalcondata/jobstreet-scraper/input-schema), [OpenAPI/input contract](https://apify.com/blackfalcondata/jobstreet-scraper/api/openapi). The README separately identifies date filters as a post-collection pipeline and describes direct-URL and incremental behavior. [Actor README](https://apify.com/blackfalcondata/jobstreet-scraper).

The important status distinction is in the schema: `emitExpired` emits records **no longer found in search results**. This is disappearance from the actor's tracked search universe, not confirmed source expiration or hiring. A changed keyword/filter, date-limited search aging a record out, a short page window, retrieval failure or changing search position can also affect discoverability. Keep the underlying observation separately from a source `isExpired`/`listingStatus` value. The schema itself warns that jobs beyond `maxPages` are outside tracked state. [Current input schema](https://apify.com/blackfalcondata/jobstreet-scraper/input-schema).

The actor offers `firstSeenAt`, `lastSeenAt`, `changeType`, status and content-hash-related output fields, but those are provider-produced records whose accuracy remains untested for TechGap. Its repost detection must not silently merge or discard source IDs before its rules have been evaluated. No applicant counts, proprietary job score, contact discovery or notification feature is needed to establish the requested historical competency collection.

## 4. Recommended six/twelve-month design, pending user choice

**Recommend a six-month rolling observed-posting archive as the initial analytical target, retaining a separately identified twelve-month comparison/expansion option.** This is a recency/scope proposal, not a claim that six months is statistically sufficient. Actual accepted counts by role/track and date must be measured before claiming usable coverage; twelve months can add observations while changing the age of the evidence.

For a run on 20 October 2026, a six-month retrospective target begins 20 April 2026 and a twelve-month target begins 20 October 2025. Exact timestamp boundaries/timezone must be recorded when a collection is authorized. Neither interval can currently be labeled completely recoverable through the two actors.

Proposed bootstrap:

1. Define the role/query matrix and a total paid ceiling in the collection plan. Keep country, seniority, remote eligibility, timeframe and inclusion rules consistent across tracks; do not assume a query title proves eligibility.
2. Use the pilot actor's `anytime` mode, or a separately tested alternative with no recency restriction, to acquire the presently recoverable baseline within the approved cap. Preserve source dates rather than invent six months of coverage.
3. Measure minimum/maximum publication date, per-week or per-month counts, missing-date counts, complete-description counts, duplicate IDs, role/track relevance, entry/junior eligibility and raw salary presence. Distinguish returned events from final accepted unique postings.
4. If an authorized, identified collection of older source URLs already exists, a bounded alternative-actor test could check whether those specific expired pages still provide full evidence. Do not enumerate unknown IDs or treat the URL interface as historical discovery. No such older-URL collection has been established here.
5. If immediate retrospective six/twelve-month completeness is essential, identify and assess an actual archive/export/licensed source with dates, full descriptions, salary/raw context, permitted use and source IDs. Until it exists, mark that requirement unavailable and ask the user to choose how to proceed; do not silently replace it with a current snapshot.

Proposed continuing collection:

1. Capture source evidence prospectively on a schedule more frequent than ad availability. Daily collection is a candidate to reduce misses; it does not guarantee capture of an ad withdrawn between observations. A six-month analysis window is different from a six-month scraping interval.
2. Use overlapping discovery windows and preserve IDs and content versions. If incremental actor state is used, keep the search universe stable and sufficiently paginated; do not interpret disappearance from a moving seven/thirty-one-day search as confirmed vacancy closure.
3. Keep complete source descriptions/HTML, salary as published or missing, source posting time, first/last observation time, query provenance, source availability/status and collection failures. Preserve an earlier full record when a later fetch returns only an unavailable shell.
4. Include a qualifying posting in the historical window even if its ad subsequently expires. Historical advertised competency demand is about what was advertised during the defined interval; it need not be limited to ads active on the analysis day. Count a source posting once in that window under the eventual dedup/version policy.
5. Keep `hiring_outcome: unknown` unless a genuine authoritative outcome source is established. Neither absence, expiry, `validThrough`, an application count nor elapsed time is proof a person was hired.
6. Report the actual observation start, collection gaps, capped/incomplete searches and obtainable date coverage. Before a full six/twelve months has accumulated, call the result an observed partial window. A retained archive still reflects the query/observation method rather than every Philippine vacancy.

## 5. Quantity and pagination audit required before promising counts

Neither actor contract establishes a guaranteed quantity for any of the four tracks. Requested maxima, search totals, returned records and accepted unique relevant postings are different counts. No current production volume was measured in this research.

Recommended collection-manifest fields are technical design proposals, not pre-existing actor fields:

| Record group | Proposed audit contents |
| --- | --- |
| Identity/configuration | Actor ID, immutable build/version when available, full input, run ID, dataset ID, query/source ID, collection start/end, country/site, sort and date settings, requested result/page/charge/time limits. |
| Source availability | Source-reported total if actually returned, pages requested/completed, last successful page, observed earliest/latest posting time, source exhaustion evidence, warnings/retries/errors, stopping reason. Unknown facts remain null/unknown. |
| Quantity reconciliation | Emitted records; unique source IDs; duplicates across queries; incomplete/missing descriptions; invalid/missing dates; eligibility/relevance exclusions; unresolved cases; final accepted distinct posting count. |
| Query/track provenance | Every query that found a posting and each validated role/track association. A shared posting is one underlying posting, not four records merely because it supports four track views. |
| Status/history | Original source status, each observation's retrieval outcome, previous full-content reference, first missing observation and later reappearance; hiring outcome separately unknown. |
| Cost | Charged event counts, actor-start events, reported charge and observed cost per accepted unique posting; proposed estimates remain separate. |

Reaching the cap means the collected set may be truncated. Finishing below the cap is not proof of source exhaustion: failures, post-filters or the alternative's default five-page bound can also explain it. Do not publish an exhaustive count without source/page completion evidence. Apify's run/build and dataset facilities supply execution/output provenance, not proof that a source universe was exhaustively crawled. [Official run/build documentation](https://docs.apify.com/actors/running/runs-and-builds), [official dataset documentation](https://docs.apify.com/storage/dataset).

Use date sorting for a chronological acquisition strategy only after verifying its accepted inputs and completion behavior. Preserve query caps and stopping causes so later sampling decisions can distinguish availability from budget limits. An actor's generous numeric cap cannot manufacture rarer entry-level roles or cure an unsupported retrospective window.

## 6. Current actor-event prices and illustrative arithmetic

Verified through current Apify metadata and the public pricing pages on 20 October 2026:

| Actor | Result event | Start event | Source |
| --- | --- | --- | --- |
| shahidirfan | Free-tier USD 0.00099/result; lower per-result rates on other tiers. | USD 0.0005/start event. | [Public pricing](https://apify.com/shahidirfan/jobstreet-scraper/pricing) |
| blackfalcondata | USD 0.002/result. | USD 0.01/start event. | [Public pricing](https://apify.com/blackfalcondata/jobstreet-scraper/pricing) |

Both pricing pages mark platform usage included. Metadata states a start-event count depends on actor memory, with one event per GB and a minimum of one. At one GB, for `E` emitted record events and `R` starts, illustrative actor-event totals are `0.00099E + 0.0005R` and `0.002E + 0.01R` respectively.

For example, **4,000 emitted result events across four one-GB starts**, not an approved or demonstrated collection quantity, calculate to USD 3.962 versus USD 8.04. This does not imply 4,000 accepted unique relevant postings. Cross-query duplicates, later-ineligible postings, repeat emissions, status/change emissions and additional runs change the total. Budget forecasts must use billed events and measured acceptance yield; they cannot assume every emitted row survives eligibility/deduplication. Recheck prices and apply an explicit total-charge ceiling before any authorized run. No new spending is authorized by this note.

## 7. Source-access and verification limits

The Philippine website terms explicitly address copying content including expired postings and require prior written consent for automated gathering. Apify actor availability alone does not establish TechGap's source-access or archive-retention permission. Record the applicable permission before production collection; this note neither obtains it nor provides a legal determination. [JobStreet website terms §7(b)(ii), §7(d)](https://ph.jobstreet.com/terms).

The JobStreet help centre's article index was discoverable, but the specific filled-vacancy article body was not returned by the web reader; the stronger status conclusion above relies on the directly readable Philippine terms instead. Public actor descriptions and inferred output schemas describe capabilities, not verified TechGap runtime success. Direct retrieval of an expired URL, provider incremental expiration accuracy, source hard pagination limits and production query yields remain untested. No undocumented API endpoint, paid test or hidden historical dataset was used.

The collection-plan questions to settle now concern the desired retrospective versus prospective window, fallback when history is unavailable, next collection budget and whether to test the alternative's needed capabilities. Deferred scoring/ranking decisions remain deferred.
