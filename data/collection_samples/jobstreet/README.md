# JobStreet sample test — 19 October 2026

**The bounded collection test passed.** Apify returned 10 distinct posting IDs with usable description text. This establishes that the selected actor can collect this sample; it does not establish whole-market coverage or finalize the production population/schema.

## Run and measured checks

| Item | Observed result |
| --- | --- |
| Actor/build | `shahidirfan/JobStreet-Scraper`, build `0.0.36` |
| Run | `5Ie8oVyO2W9EQ8aWI`, `SUCCEEDED`, exit code 0 |
| Dataset | `IA9jjL6ESB2SOQnWg` |
| Search | `web developer`, Philippine market, `30d`, no city/seniority/employment restriction |
| Collection started | 19 October 2026, 05:24:47 Asia/Manila (`2026-10-18T21:24:47.240Z`) |
| Reported runtime | 4.029 seconds |
| Reported run charge | **USD 0.0104**, within the approved **USD 0.10** cap; one run, no retries |
| Run options verified | `maxTotalChargeUsd: 0.1`, `timeoutSecs: 300`; actor input `results_wanted: 10` |
| Records / fields | 10 records; union of **32 top-level fields**, including two arrays and no nested object fields |
| Description availability | 10/10 plain-text and HTML descriptions, 774–7,379 characters of plain text; none equals its teaser |
| Description checks | All 10 inspected; HTML-derived text matches normalized plain text in 10/10. Three source-page descriptions compared in the browser, with no missing description sections observed. |
| Identity / status | 10 unique IDs, URLs and exact description hashes; all report `Active`, none `isExpired: true` |
| Dates | Source posting dates span 7–16 October 2026; all are within 30 days of observation |
| Employment / arrangement | 9 `Full time`, 1 `Contract/Temp`; 6 `On-site`, 3 `Remote`, 1 `Hybrid` |

The API's run metadata was read through the authenticated Apify MCP resource interface. The saved run record contains the input, limits, build, events and reported cost, without account tokens.

## Actual field availability

The [field inventory](field-inventory.csv) lists all 32 keys, observed types, examples, present/nonempty/null/empty/missing counts and proposed uses. The counts describe only these 10 records.

| Field(s) | Nonempty / 10 | Consequence |
| --- | --- | --- |
| `id`, `url`, `title`, `company`, `location` | 10 each | Available identity/context; title and company wording still need interpretation. |
| `description_text`, `description_html` | 10 each | Preserve both; use the text for later competency extraction and HTML for source structure/evidence. |
| `classification`, `subClassification` | 10 each | Source categories are context, not validated career/track assignments. |
| `postedAt_iso`, `postedAt_display`, `scrapedAt` | 10 each | Keep source posting time separate from observation time. |
| `workType`, `workArrangements`, `detail_status`, `isExpired` | 10 each | Available population/status context; description can disagree with a listing label. |
| `source`, `list_url`, `detail_source` | 10 each | Preserve collection provenance. Detail source is `graphql` in this sample. |
| `teaser` | 10 | Supplementary; do not substitute it for the description. |
| `salary` | 5 | Missing in five; keep optional. |
| `bulletPoints` | 3 | Missing in seven; keep optional. |
| `advertiserId`, `employerId` | 9, 8 | Employer identity cannot depend on either field always being present. |
| `companyProfileStructuredDataId` | 10 present | Two values are **0**; nonempty does not establish a usable identity. Preserve raw zero and treat its meaning as unresolved before employer counting. |
| `brandingLogoUrl` | 5 | Branding is unnecessary for alignment. |
| `roleId`, `isFeatured`, `displayType`, `apiSearchToken`, `apiSection`, `apiSectionRank` | 10 each | Preserve in raw output; source taxonomy/promotion/search metadata is not a TechGap score or demand measure. |

Unavailable optional fields were **omitted**, rather than returned as explicit nulls. No separate posting-country or seniority field appeared. Preserve the Philippine search market in run metadata without inventing a posting-country value.

## Source comparisons and interpretation issues

The ordinary web-fetch tool could not retrieve the three posting URLs. All three were accessible through the browser and were checked there. This check covered the visible job-description body, not employer questions/company-profile text outside it.

| Posting | Source comparison / finding |
| --- | --- |
| [Gramans — 95302417](https://ph.jobstreet.com/job/95302417) | Role introduction, eight responsibility bullets and eight qualification bullets were retained. It requires two years of professional experience. |
| [Cardinal Health — 95324832](https://ph.jobstreet.com/job/95324832) | The source itself labels the listing `Web Developer` but describes an `Application Support Engineer`, including four-plus years of experience. All visible description sections were retained. The source's visible employer/location labels are more specific than the actor's `Cardinal Health` / `Bonifacio Global City, Metro Manila` values. |
| [Lhoopa — 95118509](https://ph.jobstreet.com/job/95118509) | The source itself describes a web development internship/training opportunity while the title says `Web Developer` and the work-type label says `Full time`. The training, responsibilities, candidate and expected-outcome sections were retained. |

All ten records have an individual [review note](postings-review.csv). No record was deleted or silently classified into a final TechGap career. The sample includes web, full-stack, general programming and application-support descriptions; a search keyword is not a final role definition.

## Recommended retained information — for user verification

Keep posting ID/URL, raw title/company/location, full description, raw classification/subclassification, posting and collection timestamps, work type/arrangement, detail/expiry status, source/search provenance and run/build/dataset references. Keep available employer IDs with explicit missing/sentinel handling. Preserve HTML with the source evidence. Keep salary, teaser and bullet points optional. Keep remaining returned metadata in the raw sample, with no requirement to copy it into the later analytical table.

Skills and seniority can be derived later from descriptions with supporting evidence; they were not delivered as validated actor fields. Before collecting the full dataset, decide the intended role/search coverage, experience levels, internship eligibility, remote eligibility and next-run budget. These decisions affect the analyzed population; the sample does not answer them.

## Saved evidence and limits

- [Original returned records](raw-jobs.json): all 10 items, no field projection, fetched with `clean: false`.
- [Sanitized run record](run.json): verified options, provenance and reported charge.
- [Actor input](jobstreet-input.json) and [checked actor contract](actor-contract.json).
- [Machine-readable checks](sample-checks.json), including a SHA-256 of the saved raw JSON.
- [Collection plan](../../../docs/plan/JOBSTREET_COLLECTION.md).

No exact ID/URL/description duplicates were observed; reposts with different IDs are not comprehensively tested. Only three descriptions were independently compared with source pages. Other missing source fields, unseen layouts, future actor changes and retrieval failures remain possible. This small search sample cannot establish demand prevalence, represent all four tracks or prove that every vacancy from the preceding month was collected.
