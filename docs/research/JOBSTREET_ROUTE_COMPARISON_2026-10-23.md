# JobStreet route and billing review

Checked 2026-10-23 (Asia/Manila). Provider and account values below are read-only snapshots taken 2026-10-22 16:20–16:22 UTC. No actor run was started for this review.

**Later reconciliation, 2026-10-23:** An authenticated read-only check of all 34 saved run IDs found 850 billed result events and USD 0.85850 in total provider run usage. The older USD 0.60605 local ledger understated 11 run settlements by USD 0.25245 in total. Keep the older figures below as the dated snapshot; use the [run-level reconciliation](../../data/job_collections/jobstreet-2026-10-recovered-reconciliation-raw-v2-yield-audit-v1/billing_reconciliation_2026-10-23.json) for historical campaign cost. The user also confirmed that previously handled source permission covers the accepted six-query 30-day pilot; see its [scope record](../../data/job_collections/jobstreet-2026-10-recovered-reconciliation-raw-v2-yield-audit-v1/proposed-pilot/source_access_scope_2026-10-23.json). No consent document was inspected in this review, and no new actor run was started.

## Route comparison

| Evidence area | `shahidirfan/jobstreet-scraper` (pinned route) | `blackfalcondata/jobstreet-scraper` (candidate route) |
| --- | --- | --- |
| Current controls | Input accepts `results_wanted` and posted-date values including anytime, 24h, 7d, and 30d. The published schema does not expose a page, offset, or sort control. | Input documents `maxResults` (up to 1,000), `maxPages` (up to 50), `sortMode`, date ranges, and `includeDetails`. `startUrls` supplements the query rather than replacing it. |
| Current output fields | Output documentation includes `description_text` and `description_html`, plus `postedAt_iso` and display date fields. | Output uses a different shape, including `jobId`, `canonicalUrl`, `postedDate`, and `description`/`descriptionHtml`; it needs a separate adapter and provenance mapping. |
| Price shown | $0.99 per 1,000 dataset results plus $0.0005 per actor-start event. Current Free plan advertises up to 5,050 monthly results and $5 of usage. | $2 per 1,000 results plus $0.01 per actor start on the current pricing page. |
| What the public evidence establishes | It does not show how to continue beyond the first 25 results. Accepting a larger result count is not evidence of deeper retrieval. | It offers pagination controls suitable for a bounded continuation experiment. Its schema and price do not establish exhaustive history, source permission, or results beyond a repeated prefix. |
| Pilot status | Do not raise the local cap on contract evidence alone. | Candidate for a separate adapter evaluation only after a source-access basis and new campaign scope are recorded. |

Sources: [pinned actor input schema](https://apify.com/shahidirfan/jobstreet-scraper/input-schema), [pinned actor output documentation](https://apify.com/shahidirfan/jobstreet-scraper), [pinned actor pricing](https://apify.com/shahidirfan/jobstreet-scraper/pricing), [candidate actor input schema](https://apify.com/blackfalcondata/jobstreet-scraper/input-schema), and [candidate actor pricing](https://apify.com/blackfalcondata/jobstreet-scraper/pricing). Published listings may change; recheck contract and price before a future run.

## Source-access gate

The local source-access record only describes the previously handled permission basis for the pinned actor/build and the completed campaign's exact queries and date window. It does not include a written JobStreet/SEEK consent artifact for a new actor, query set, date window, or campaign. The current [JobStreet Philippines Terms](https://ph.jobstreet.com/terms) prohibit automated data gathering/extraction/screen scraping except with prior written consent and separately address automated processes that use a specific technical interface/API. This comparison is a source-access gate, not a legal determination. Record an applicable written consent or other source-authorized basis before a new collection campaign.

## Account and saved-ledger reconciliation

The authenticated read-only account snapshot reported a Free plan, a $5 monthly usage allowance for the Oct 5–Nov 4 cycle, and total usage of $0.8709589205642893 as of 2026-10-22 16:22:04 UTC. The arithmetic remainder at that time was about $4.129041. This is a snapshot, not a new campaign budget or spending authorization.

The provider run list showed 34 campaign starts and 850 result events. At the event prices shown for the pinned actor, these events imply $0.8585 for the campaign: 34 × $0.0005 starts plus 850 × $0.00099 results. The local campaign ledger records 700 imported rows and $0.60605. The $0.25245 difference is unresolved by the frozen local ledger.

Six local dataset files contain empty arrays, while current provider dataset metadata reports 25 items for each (150 rows total). Five additional 25-item run settlements also understate the result-event amount. The separate recovery package fetched and hash-recorded these six existing datasets; it did not start runs or rewrite the original campaign. A separate reconciliation campaign now imports all 850 provider rows and has 438 distinct IDs across 443 versions. Its v1 replay yields 46 distinct legacy eligible IDs; that is a historical-rule count and does not mean 46 cases passed v2 human review.

The account snapshot, current provider run counters, and local ledger differ in scope and timing. Use the original local charge only as its saved ledger figure. Preserve the discrepancy and reconcile it against provider invoice/usage evidence before treating any campaign cost-per-eligible estimate as final.

## Decision for remaining plan steps

- Step 2 route comparison is documented. The pinned route has no documented continuation control. The alternative is only a candidate route, not a verified yield route.
- Current source-access evidence does not establish permission for either route under a new campaign scope, so continuation status is `continuation_unavailable` pending applicable written authorization.
- The current account allowance snapshot is not a campaign budget. Set a new campaign ceiling and per-run cap only after source scope is established and billing is reconciled.
- Steps 3 and 4 require a newly authorized bounded pilot, actual page/position evidence, and human-reviewed v2 yield. No new actor run has been made.
- Step 5 release remains gated on case review, billing reconciliation, and complete source provenance.

