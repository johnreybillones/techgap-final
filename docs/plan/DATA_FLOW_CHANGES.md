# Data Flow Change Record — Two Execution Plans

Updated: 2026-10-22. Current plans: [Plan 1 — job collection](JOBSTREET_COLLECTION.md) and [Plan 2 — processing after collection](DATA_FLOW_ACTUAL.md). Decisions: [DECISIONS.md](DECISIONS.md). Requirements: [SYSTEM_REQUIREMENTS.md](../requirements/SYSTEM_REQUIREMENTS.md).

This file records changes, reasons and remaining evidence limits. It is not a third execution plan. Older [DATA_FLOW.md](DATA_FLOW.md) and research notes retain historical proposals; the two plans and latest decision entries govern the current technical direction. A completed plan is not an implemented/evaluated pipeline.

## 1. Document split and handoff

| Document | Owns | Ends with |
| --- | --- | --- |
| Plan 1 | Exact query registry, acquisition/time/budget rules, raw preservation, source identities/versions, eligibility, duplicate handling, collection audit and expansion. | Frozen raw release: accepted count-unit/version membership, hashes, source/run/query evidence, admission decisions, actual quantities/dates/costs and limitations. |
| Plan 2 | Academic input validation, description division, competency extraction, logic/normalization, populations, semantic retrieval, evidence assessment, scores/demand, priorities, enhancement/resource/roadmap records and evaluation/reruns. | Versioned traceable feature/report records and analytical evaluation evidence. |
| This change record | Differences from earlier proposals, effects and unresolved claims. | Cross-references and explicit gate descriptions. |

Collection uses only the text checks needed to admit usable relevant records. Detailed competency/model processing belongs to Plan 2. Raw release limitations cannot disappear at the handoff.

## 2. User decisions incorporated

| Earlier state | Current instruction | Concrete effect |
| --- | --- | --- |
| Only a ten-record field-discovery pilot; full collection initially proposed at 5,000. | Start with 25% of the revised 4,000 goal: 1,000 accepted distinct postings. | Save an audited development release; do not mistake 1,000 returned/billed rows for 1,000 eligible jobs. |
| Sample-to-full relationship unspecified. | Avoid duplicates when expanding to the actual goal. | One persistent source-ID/version registry across phases; reuse sample IDs toward 4,000 and count only additional eligible units. |
| Fixed rolling six-month window proposed. | Recent first; older months only when supply is insufficient; maximum twelve months. | Common adaptive interval with an absolute twelve-calendar-month ceiling; do not require a full retrospective six-month archive. |
| Earlier choice excluded internships and left generic experience-only seniority unresolved. | Keep relevant internship/OJT as a separate cohort with the same roles and four-track/Shared-core classifications; admit generic employment roles only with a clear 0–2-year mandatory requirement and no conflict. | Internship totals do not satisfy employment targets. Explicit mid/senior roles stay outside employment; open-ended or contradictory experience remains unresolved. |
| No numerical budget supplied. | Approximately USD 5 Free usage believed available for the total goal. | Campaign ceiling no higher than verified available allocation/USD 5; serial capped runs and actual-charge ledger. No promise of 4,000 accepted jobs within it. |
| R5 unfamiliar-concept handling awaiting answer. | Follow recommendation. | Accept evaluated clear source-backed local concepts even without external catalog linkage. |
| R6 scoring awaiting answer. | Follow recommendation. | Equal binary independently assessable core groups, explicit AND/OR, preferred findings separate, unknown evidence visible and mean posting aggregation. |
| R7 logical coverage awaiting answer. | Follow recommendation. | Same-capability evidence and narrowly scoped evaluated directional rules; no framework/taxonomy/prerequisite shortcut. |
| R8 ranking/roadmap choices awaiting answer. | Follow recommendation. | Observed distinct-ad demand priority; career mean coverage; descriptive n/N topic review; demand/resource-scoped preparation order. TOPSIS conditional/deferred. |
| Salary could be overlooked as analytically unused. | Retain salary in extracted job data. | Full payload preservation with missing/null/empty distinctions; no score weight, inference or salary-based exclusion. |
| Processing stages described at a broad level. | Concrete technical execution required. | Both plans specify inputs, exact procedures, formulas/candidate checkpoints, output records, checks, stop/uncertainty states and rerun dependencies. |

Other preserved decisions: same entry/junior Philippine employment population for both experiences; eligible remote jobs allowed; responsibilities supply technical evidence; education, experience, soft skills, benefits and offered training remain raw/context; Academic uses whole applicable coursework and Student current coverage uses completed courses only; future courses earn no current credit; one-time human development checking allowed. The first evaluated release retains all four tracks; overlapping track memberships and Shared/core are reported separately within each cohort. Recent-first expansion may exceed one month as needed but has a twelve-calendar-month maximum.

## 3. Changes to technical treatment

| Area | Revised specification | Verification boundary |
| --- | --- | --- |
| Search routes | 34 literal base queries relevant to four families plus shared computing; query origin does not prove career/track eligibility. | Actual available eligible counts and current continuation behavior are unmeasured. |
| Balance | Budgeted development cohort first; conditional proportional allocation only from a sufficiently defined observed frame. | No paid full 4,000-frame prerequisite, equal-track quota or national representativeness claim. |
| History | Retain usable inactive records, with publication/observation dates distinct. | Removed descriptions are not reconstructed; expired/not-found does not establish hired. |
| Duplicate identity | Source keys, semantic versions, idempotent observations and evidence-based repost groups. | Same text under different IDs is a candidate, not automatic same-vacancy proof. |
| Charges | Billed outputs, raw IDs and accepted ad count units reconciled separately. | Local deduplication does not prevent a provider billing repeated returned results. |
| Text division | HTML blocks/headings/list items, statements, protected technology names, JSON/page paths and token-safe chunks. | Fallback text and unavailable coordinates remain explicit. |
| Extraction | Pinned GLiNER2 starting candidate plus literal baseline and source-span/context validation. | Schema support is documented; TechGap performance is not measured. |
| Matching | Pinned MPNet/cosine retrieval followed by source/scope checks and a pinned NLI candidate. | Cosine and NLI scores are not alignment/mastery percentages or automatic coverage proof. |
| Requirements | Independent groups, linked task/tool scope, AND/OR trees, repeated-evidence deduplication. | Ambiguous grouping/modality remains unresolved; no invented fractional credit. |
| Aggregation | Score per posting/count unit, then equal-contribution mean. | Incomplete denominators cannot silently disappear; partial aggregates are labeled and complete scores withheld. |
| Priorities | Count accepted requirement groups once per ad, retain contexts and alternative options. | No unapproved composite weights, low-demand threshold or trend claim. |
| Guidance | Advisory course/area candidates and verified resource-specific preparation graph. | No invented contact hours, universal prerequisites, course placement or all-gap resource completeness. |
| Evaluation | Source-group labels/split, explicit parameter-selection proposals, held-out errors and deterministic fixtures. | Workload/split/search defaults are proposals, not approved accuracy targets or completed experiments. |
| Reprocessing | Source/config hashes and per-stage invalidation. | Parser/model/score changes reuse raw collection; updated evidence produces a new frozen release. |

## 4. Data-dependent limits and separate gates

Keep missing inputs separate from ordinary derivation and empirical work. A model or score being unevaluated does not mean the stage should be removed.

| Limit/gate | What may proceed | What cannot yet be claimed |
| --- | --- | --- |
| Actual credit/account conditions and efficient actor continuation unverified | Prepare configs, preserve pilot, implement/import/check local registry. | Another run authorized by the old pilot approval; exact campaign capacity; cheap exclusion of known IDs or complete source enumeration. |
| Older source availability incomplete | Use actually captured/recoverable dated postings and report achieved window. | Complete retrospective twelve-month history merely because it was requested. |
| Syllabus extraction issues/applicability links unresolved | Repair sources, develop algorithms, retain qualified positive evidence. | Complete whole-track/student analysis by dropping problematic applicable courses or substituting CSV competency text. |
| Candidate model/checkpoint/threshold performance unmeasured | Implement explicit experiments and score labeled development fixtures. | Validated production coverage, guaranteed accuracy or acceptable error rates from model cards. |
| No general directional rule collection | Evaluated same-capability comparisons and specific evidenced rules. | General automatic distinct-skill logical coverage or coverage inferred from taxonomy/prerequisites alone. |
| Reverse curriculum-relevance metric provisional | Academic-unit demand links and the accepted forward coverage score. | An approved second-direction percentage or automatic reversal of support implications. |
| Categorical low-demand cutoff unselected | Descriptive observed n/N and ascending review order. | A 5%/percentile/obsolete label or decline from one snapshot. |
| Mandated/core/capacity/placement references absent | Qualified additive course/area enhancement candidates. | Compliance-validated recommendations satisfying all of FR-A07/BR-09 or exact placement/hours. |
| Some gaps lack verified resources | Gap nodes, verified matches and demand order. | Complete resource coverage for every extracted gap; hidden deletion of unmatched gaps. |
| No universal prerequisite graph | Explicit scoped provider preparation and topological ordering where valid. | A universal dependency-complete learning sequence. |
| D01 simulation conflict persists | Ordinary source-backed current analysis and advisory enhancements. | Full FR-A11/FR-M01–FR-M04 completion or a silently implemented/removed simulation scope. |
| Export format and retention/deletion rules open | Shared report records and immutable releases. | A selected PDF/Word exporter or permission to delete inactive evidence. |
| Application stack outside these plans | Algorithm/data specifications and implementation module map. | Approved frontend/backend/deployment choices. |

## 5. Requirements and completion interpretation

Plan 2 section 16 maps retained processing to the actual requirement IDs. The requirements baseline is unchanged. FR-D01–FR-D05, FR-A01–FR-A10 and FR-T01–FR-T08 have specified processing responsibilities, with the source/model/constraint/resource qualifications above. Shared selection recomputation uses the same result records. Projection/simulation remains D01's separate conflict.

Writing these plans completes documentation of the intended sequence. Collector completion requires an audited real release under Plan 1; analytical completion requires evaluated transformations and traceable actual results under Plan 2. Passing document-link/arithmetic checks does not establish source accuracy, model accuracy or runtime behavior.

## 6. Next execution order

1. Prepare Plan 1 configuration/registry and reconcile existing raw pilot records.
2. Verify remaining credit, current adapter controls and source route before any additionally requested paid collection.
3. Collect/freeze an actual development release, reporting shortfalls rather than forcing its target.
4. In parallel with source availability, repair academic extraction/applicability and prepare Plan 2 labels.
5. Implement P0–P6 and E1–E4; freeze evaluated configurations before automatic production findings.
6. Implement deterministic metrics/guidance/results, preserving unresolved inputs and the explicit claim gates.
7. Expand the shared collection toward 4,000 only with verified remaining funds/retrieval controls and reused eligible IDs.

No collection, model inference, implementation deployment, scheduled task or deletion is performed by this documentation update.

Documentation verification on 2026-10-22 checked eight edited documents, 68 relative links, balanced code fences/inline formatting, table columns, the JSON manifest example, 34 distinct literal queries, worked cost/mean calculations, pinned revision identifiers and unchanged pilot input settings. A fresh-reader consistency review identified canonical requirement identity and academic-topic relevance gaps; both were resolved and re-reviewed. These are document checks, not empirical model, collection or implementation validation.
