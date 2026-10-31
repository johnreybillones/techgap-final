# Job acquisition research — 17 October 2026

Status: documentary research for the actual system plan. No Actor was run, no dataset was collected, and no credentials or billing account were accessed. Publisher documentation establishes a claimed contract; collection reliability, missingness, description completeness, relevance, and deduplication quality remain unverified.

Authority: [SYSTEM_REQUIREMENTS.md](../requirements/SYSTEM_REQUIREMENTS.md), especially §3.1, BR-07 and FR-D02–D04, requires computing-related Philippine JobStreet evidence and explained findings grounded in the analyzed dataset. Additional sources, collection windows, and operational limits require decisions. This note does not choose an Actor or alter requirements.

## Documented output mapping

The following are documented fields relevant to TechGap, not a claim that every collected listing will contain usable values. [Shahidirfan README](https://apify.com/shahidirfan/jobstreet-scraper), [Black Falcon Data README](https://apify.com/blackfalcondata/jobstreet-scraper).

| Purpose | shahidirfan/jobstreet-scraper | blackfalcondata/jobstreet-scraper |
| --- | --- | --- |
| Posting identity | `id` | `seekJobId`; separate `jobId` |
| Evidence link | `url`, `list_url` | `canonicalUrl`, `sourceUrl`, `searchUrl` |
| Role/relevance context | `title`, `classification`, `subClassification` | `title`, `category`, `subCategory`, `roleId` |
| Employer | `company`, optional advertiser identifiers | `company`, `advertiserId` |
| Geography | `location` | `location`, `locationCountry`, `locationState`, `locationSuburb`, `locationPostcode` |
| Skill evidence | `description_text`, `description_html`, `teaser`, `bulletPoints` | `description`, `descriptionHtml`, `descriptionMarkdown`, `teaser`, `bulletPoints` |
| Dates | `postedAt_iso`, `postedAt_display`, `scrapedAt` | `postedDate`, `validThrough`, `scrapedAt`, `fetchedAt` |
| Status | `detail_status`, `isExpired` | `detailFetched`, `isExpired`, `listingStatus` |
| Employment | `workType`, `workArrangements` | `employmentType`, `workArrangement` |
| Salary (optional for current outputs) | `salary` | `salaryText`, `salaryMin`, `salaryMax`, `salaryCurrency`, `salaryType` |

Shahidirfan says unpublished fields may be omitted. Black Falcon says standard output retains unavailable values as null; compact output omits descriptions. Its documented incremental output includes change/repost metadata. Neither publisher establishes a validated TechGap skill column, career taxonomy, demand score, curriculum match, or alignment score. Those require later pipeline stages. [Shahidirfan README](https://apify.com/shahidirfan/jobstreet-scraper), [Black Falcon Data README](https://apify.com/blackfalcondata/jobstreet-scraper).

## Inputs and limits

Shahidirfan supports `keyword`, typed `location`, `country` (`ph` for Philippines), `posted_date` (`anytime`, `24h`, `7d`, `30d`), `results_wanted` (minimum 1, default 20), optional proxy configuration, and `startUrl`. A search URL overrides keyword/location; its host determines the market. No cross-run deduplication behavior or upper result bound was established from the inspected input contract. [Shahidirfan input](https://apify.com/shahidirfan/jobstreet-scraper/input-schema).

Black Falcon supports `country: "PH"`, location, query batches encoded as a string, and `startUrls` added to other searches. Batches deduplicate by job ID. `maxResults` defaults to 100, accepts up to 1000, and zero means unlimited; `maxPages` defaults to 5, accepts 1–50 per source. Date filters include `dateRange`, `fromDate`, `toDate`, `maxAgeMinutes`. Full text requires `includeDetails`; preserve it using `compact: false`, `descriptionMaxLength: 0`, and a suitable `descriptionFormat`. Incremental mode tracks changes within a configured search universe; an expired emission can mean no longer found in that search. It does not prove the posting expired globally. [Black Falcon input](https://apify.com/blackfalcondata/jobstreet-scraper/input-schema).

## Scheduling and spending

Apify supports recurring schedules, timezone selection, and annual schedules. Its documentation requires an initial Actor run before scheduling. Six-month or yearly scheduling is technically feasible; no schedule was created. The actual dates and interval remain undecided. [Apify scheduling](https://docs.apify.com/actors/running/schedules).

At research time, Shahidirfan's Free-tier price table lists $0.99/1000 results plus an Actor-start event of $0.0005; platform usage is included. Black Falcon lists $2/1000 plus $0.01/start, with platform usage included. Discounts and prices may change; these are not approved spending limits. [Shahidirfan pricing](https://apify.com/shahidirfan/jobstreet-scraper/pricing), [Black Falcon pricing](https://apify.com/blackfalcondata/jobstreet-scraper/pricing).

The run API supports `maxTotalChargeUsd` across pricing models, plus timeout and build selection. `maxItems` is a charged-item bound specifically for pay-per-result Actors; it does not guarantee returned row count and should not replace Actor inputs or the total-cost cap. Retries need their own total budget because a per-run limit does not set a whole-refresh limit. [Apify Run Actor API](https://docs.apify.com/api/v2/actors-runs-post).

## Proposed adapter responsibilities — decisions still needed

This is a proposed information contract derived from the required outputs, not an approved schema or model choice.

| Responsibility | Proposed required information | Missing-value consequence to decide |
| --- | --- | --- |
| Traceability and deduplication | source name/market, source posting ID, canonical evidence URL, collection time, actor/build/run/dataset IDs, query/filter configuration, snapshot ID | Report rejected/duplicate counts; never invent IDs or source evidence. An adapter may generate internal identifiers with explicitly recorded provenance. |
| Competency extraction | complete usable description text, title, evidence spans linked to the source text | A title/teaser alone cannot be silently substituted for full job requirements. Decide whether a failed detail record is retried, excluded, or stored as incomplete. |
| Philippine computing relevance | actual location/country evidence, role/title, description, available classification | Define Philippine/remote eligibility and computing-role inclusion. A market-domain flag alone needs an explicit policy for ambiguous geography. |
| Recency and repeated refresh | collected-at, available posting date, run status, search window and bounds | Distinguish source posting time from collection time; decide how missing dates affect eligibility. |
| Demand summaries | normalized posting identity, approved career association, extracted competency evidence, dataset window and denominator, deduplication decisions | Frequency and demand belong to analyzed records; applicant counts and scraped ranking scores are not substitutes. |

Salary, company profiles, logos, recruiter contacts, screening questions, and applicant counts are not necessary to the present required alignment outputs. Proposed storage policy should retain fields with a defined analytical/evidence purpose; optional fields should not become compulsory eligibility filters without a requirement. Store parser/extractor versions and provenance as TechGap metadata rather than pretending the actor supplies them. [Requirements baseline](../requirements/SYSTEM_REQUIREMENTS.md).

## Boundaries to resolve in the interview

1. **Sampling meaning:** a snapshot of available postings every 6/12 months, or continuous observation summarized every 6/12 months? Live search/date filters do not establish an archive of all vacancies posted during a preceding six-month/year period. That historical completeness remains unverified.
2. **Population:** Philippine computing roles are required; decide domestic locations, Philippines-eligible remote roles, seniority, employment types, and any exclusions. Broad career sampling and a graduate-focused subset answer different questions.
3. **Source scope:** the requirements currently identify JobStreet. Comparing other sources is research; adding one to ingestion requires explicit scope agreement.
4. **Volume and query strategy:** choose target roles/searches, result/page bounds, and total refresh budget after a limited actual-data evaluation. Search overlap needs deduplication; identical postings with new IDs need a separate repost policy.
5. **Automated quality behavior:** agree required fields, incomplete-record handling, retries, clear failure reporting, and minimum evidence for showing a result. These checks do not introduce human review.
6. **Retention:** decide what counts as outdated, whether to retain any historical snapshots, and how long source text and derived evidence must remain available to reproduce saved reports. Proposed sequence: collect replacement, validate it automatically, activate it, then prune according to the agreed policy. Capacity and indexes need measurement before assigning retention numbers. Supabase-specific limits and deletion design were not investigated in this note.

The next verification step is a bounded real sample after the collection plan and spending authorization are agreed, checking the documented fields against actual saved output. This research supplies no invented rows or measured quality claims.
