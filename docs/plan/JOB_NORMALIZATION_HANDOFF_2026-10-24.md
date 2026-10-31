# Job normalization — pipeline conversation handoff

**Purpose:** Start the first offline processing milestone in a separate conversation using already saved JobStreet data. The user chose **lossless normalized jobs first**. This handoff does not include a paid collection, relevance classifier, requirement extractor, syllabus matcher, alignment score, or implementation authorization for later pipeline stages. [PLANNED_DATA_FLOW.md](PLANNED_DATA_FLOW.md) is the current downstream contract; use it over conflicting historical pipeline assumptions.

## Settled boundary

Normalize the preserved raw observations into a reproducible, versioned job index without changing the originals. A source ID represents one distinct posting for analysis; multiple query/run observations and materially changed descriptions remain linked as versions. Choose one coherent source version for a derived release while retaining alternate versions and the selection reason. Report returned rows, valid distinct IDs, missing/invalid records and version counts separately. A query is provenance, never a track or curated-role label.

This milestone handles **structure and text preparation**: identity, provenance, selected and alternate descriptions, dates, location/work-type fields, and quality flags. Relevance/track/career decisions, technical requirement groups, modality, syllabus support, demand and coverage calculations belong to later derived stages. An absent or unusable description remains visible and unavailable for text-dependent calculations; it is not a posting with zero technical demand or zero coverage.

## Inputs and current evidence

- [Historical raw-v2 release](../../data/job_collections/jobstreet-2026-10-recovered-reconciliation-raw-v2/manifest.json): 850 observations and 438 distinct IDs across the earlier campaign.
- [Six-query raw-v2 release](../../data/job_collections/jobstreet-2026-10-six-query-pilot-20261023/manifest.json): 150 more observations, 29 IDs new against the 438-ID frame, and a 467-ID comparison registry. Its labels are provisional source-text assessments, not ground truth.
- [Blackfalcon raw handoff](../../data/job_collections/blackfalcon-data-engineer-paginated-20261023/raw_handoff_validation.json) and [reconciliation](../../data/job_collections/blackfalcon-data-engineer-paginated-20261023-reconciliation-v2/report.md): 50 observations, 16 IDs new against 467, reported combined union 483. The actor's hashed `jobId` is provenance; validate numeric `seekJobId` against `canonicalUrl` for the shared `jobstreet:ph:<id>` key. Blackfalcon page evidence remains unverified and is an observation-quality flag, not a reason to discard the posting.
- [Syllabus extraction summary](../../data/syllabi/summary.json): syllabus JSON is a separate later academic-evidence input, including records marked `needs_review`. Do not insert CSV text, course titles, or outside reference text as missing competency evidence during this job-only milestone.

The 483-ID count is a current reported union, not a hardcoded target for a reusable normalizer. Verify source membership and hashes from the saved releases at execution time. Preserve the updated six-query README/manifest hash discrepancy as a documented metadata mismatch; verify that raw/index artifacts themselves remain intact.

## Recommended derived record and checks

For each source ID, retain:

- Stable `jobstreet:ph:<numeric-id>` key, original actor-specific IDs, canonical/source URL, original employer title/company, and all raw item pointers/hashes.
- Selected description text and HTML where available, selected version ID/hash, alternate version links, and a deterministic selection rule. Keep original text byte-for-byte in raw storage; any cleaned plain text is a **new derived field** with transformation version. Preserve headings, list boundaries, AND/OR wording, and task/tool qualifiers rather than flattening them into a bag of terms.
- Publication time, collection time, first/last observed time, each with its own source and parse/uncertainty status. Never substitute capture time for an unknown publication time. Normalize parseable values to a stated UTC representation while retaining original strings.
- Location, `locationCountry`, work arrangement, employment type, salary and other available fields as source values plus clearly named parsed views. Preserve absent versus explicit null versus empty. Missing salary is not an exclusion.
- Query, actor/build, run, dataset, observation and page/source URL links. A missing or contradictory page number stays unknown/flagged. Similar text under different JobStreet IDs is a duplicate **candidate** link, not an automatic merged posting.
- Description missingness, suspected truncation/uncertain completeness, conflicting-field and invalid-item reasons. Do not infer PH eligibility, internship, relevance, seniority, track, curated role or technical skills solely from a query or the normalized schema.

Validate that every normalized posting links to an existing raw payload and that every valid source ID appears once in the derived distinct-posting index while retaining all observations. Verify hash references, deterministic reruns, cross-actor same-ID joins and separate version/observation counts. Use focused fixtures that include a shared ID across actors, changed description, missing date, empty text, null field, invalid ID/URL pair and contradictory page evidence.

## Why existing pipeline code needs inspection

The current `scripts/pipeline/contracts.py` still declares an `entry-junior-internship` policy and older track categories. The agreed [planned data flow](PLANNED_DATA_FLOW.md) includes all employment seniority levels and the four academic tracks, so the existing admission runner is not the normalization contract. Reuse only code whose identity/text/provenance behavior is verified against the new raw releases; avoid carrying its old policy labels into this milestone.

## Completion and next boundary

The first milestone is complete when the combined saved corpus can be regenerated offline into a hash-linked normalized index; its counts reconcile to source observations and distinct IDs; full raw payloads and alternate versions remain recoverable; and missing/uncertain fields remain explicit. No relevance or score claim is required to complete normalization.

Afterward, the separate processing discussion can design source-backed relevance/track/curated-role links, technical requirement extraction and grouping, syllabus evidence preparation, same-capability matching, and calculations in the order specified by [PLANNED_DATA_FLOW.md](PLANNED_DATA_FLOW.md). Before trusting those decisions or student/faculty rankings, use an independent small source-labeled evaluation; routine processing should still produce automatic decisions rather than depend on a human approval queue. New collection can proceed alongside normalization because each new raw release can be normalized with the same versioned rules.
