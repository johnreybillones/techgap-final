# TechGap Core Implementation Plan

Prepared: 2026-10-18. Current execution-plan split and decisions: 2026-10-22.

**Goal:** Build the actual Student and Faculty/Academic Administrator journeys using official curriculum content and collected Philippine JobStreet evidence.

**Status:** Working implementation plan requested by the user. Answered choices are recorded separately from recommendations and unresolved choices. The plan is written now; it does not depend on completing another interview. Application implementation has not started in this checkout.

**Current execution plans, 2026-10-22:** [Plan 1 — job collection](JOBSTREET_COLLECTION.md) owns exact searches, 1,000-to-4,000 reuse, recent-first acquisition up to twelve months, budget, identities/admission and the frozen raw handoff. [Plan 2 — processing after collection](DATA_FLOW_ACTUAL.md) owns detailed algorithms, model candidates, requirements, matching, calculations, guidance, evaluation and reruns. [Data-flow changes](DATA_FLOW_CHANGES.md) is the change/limitation record. These two plans and the latest [decisions](DECISIONS.md) take precedence over older pipeline settings below. [DATA_FLOW.md](DATA_FLOW.md) remains the historical mixed plan; neither plan claims implemented or evaluated analytics.

**Architecture recommendation:** One web frontend, one Python API and processing package, and Supabase for shared data and analysis results. Run ingestion and extraction as repeatable batch commands rather than starting them on every dashboard request.

**Candidate stack:** Next.js/TypeScript, Python/FastAPI, Supabase/Postgres, and Apify. This continues the existing architectural proposal; full-system stack approval, dependency versions, deployment, and model artifacts are not established decisions.

**For implementation:** Work through the tasks below. Resolve only the decisions required for the task being started. Do not interpret this planning document as authorization for paid collection, deletion of stored evidence, or deployment.

Read [Decision register](DECISIONS.md) for answered items and questions with their deadlines. Read [Changes from the handoffs](CHANGES_FROM_HANDOFF.md) for the history of scope and planning changes. The behavioral baseline remains [SYSTEM_REQUIREMENTS.md](../requirements/SYSTEM_REQUIREMENTS.md).

Collection update, 2026-10-19: the focused [syllabus plan](SYLLABUS_COLLECTION.md) includes a Python script verified on the supplied PDF; the [JobStreet plan](JOBSTREET_COLLECTION.md) includes a completed 10-posting Apify sample and actual field inventory. These are collection pilots; the analytical system remains unimplemented.

User answers, 2026-10-20: use syllabus JSON only as academic competency content, require extraction fixes before calling analysis complete, and permit supporting references conditionally when reliable, evidence-backed and serving a distinct purpose. The user clarified that CSV `Track` / `Course Code` pairs already supply applicability: a separate JSON lookup is proposed, with no redundant CSV description/outcome text sent to the model. [Data flow](DATA_FLOW.md) records the actual schema, mapping recommendation and feature dependencies; [A19–A22](DECISIONS.md) record these answers. Code-to-syllabus linkage, placement and constraints remain unresolved.

For the current detailed source-to-result procedure, read the two execution plans above. The remainder of this index retains broader application delivery context; it does not add frontend/backend work to the two data/algorithm plans. [Processing after collection](DATA_FLOW_ACTUAL.md) specifies contextual extraction, semantic retrieval, evidence support, profiles, calculations and guidance. Academic analysis uses all applicable selected-track syllabi; Student current analysis uses completed courses only. Read [Data-flow changes](DATA_FLOW_CHANGES.md) for specific data-dependent reductions and deferrals. Neither document specifies frontend/backend design or claims full baseline completion.

## 1. Delivery scope

| Experience | Required working journey |
| --- | --- |
| Student | Choose program, track and year; select eligible completed courses; inspect ranked careers and their requirements; compare and select a suggested or alternative role; inspect alignment, supporting course evidence, gaps and future coverage; follow an ordered roadmap with openable resources. |
| Faculty/Academic Administrator | Select track; inspect whole-curriculum alignment, industry requirements and course evidence; review demand-related gap priorities and low-demand topics; inspect additive recommendations alongside findings; generate, print and download an academic review report. |
| Shared operation | Choose role without sign-in; retain each experience's selections across views and visits; update dependent results when selections change; show source/version context; recover from failed operations. |
| Evidence lifecycle | Import official curriculum, collect and process JobStreet evidence, preserve a controlled evaluation dataset, accept subsequent curriculum updates, refresh job evidence and remove outdated data under an agreed policy. |

Programs/tracks: BSCS Intelligent Systems and Game Development; BSIT Network Technology and Web Development. Include applicable common/core computing courses. Exclude General Education and informal learning from matching and student scores.

All displayed analytical findings must come from the implemented pipeline and identified evidence. Empty or insufficient evidence produces an explanation of what cannot be assessed. Synthetic job demand, example scores and fixed demonstration outputs are not production results.

**Requirements conflict:** The user requested removal of simulation. The baseline still requires FR-M01–FR-M04 and the projected-effects portion of FR-A11. Those activities are held separately in conditional task P7 below, pending the scoped resolution in D01. The ordinary journeys and data work can proceed. The project cannot claim full baseline coverage while that conflict remains unresolved.

Faculty Microsoft sign-in is a v2 preference, outside the current implementation design. OCR is tentatively deferred to v3. Visual styling decisions and a mock-UI build are outside this plan's current work.

## 2. What is available and what must be obtained

| Available evidence | Planning consequence |
| --- | --- |
| 119 saved syllabus JSON records in `data/syllabi/`: 30 `ok`, 89 `needs_review`, none failed. | A19 selects these as the only academic-content source; A20 requires extraction fixes before complete analysis. Structural status is not independently measured source accuracy. |
| JSON has course identity/type/credit, dependencies, description, CLOs, period overviews and source metadata, with missing/unparsed values. CSV track/code pairs provide applicability metadata under A22. | Use the exact [source contract](DATA_FLOW.md). Validate code-to-component links separately; academic version, year/semester placement and constraints are not supplied by the membership pairs. |
| Original syllabus PDFs and the verified Web Development Laboratory sample remain available as extraction evidence. | Fix and check unfamiliar layouts against the source PDFs. Do not fill missing competency text from CSVs or guess placement from filenames/folders. |
| Repeated course codes occur in the saved batch, including lecture/lab records. | Preserve source identity and raw values; define component identity/versions without silently merging different components. |
| [JobStreet sample](../../data/collection_samples/jobstreet/README.md): shahidirfan build `0.0.36`, ten postings and 32 observed keys. | Pilot actor/output verified. Broader roles, queries, population, subsequent spend and refresh remain open; alternative actor contracts are only research. |
| A Python syllabus extraction pilot and a 10-posting local JobStreet sample now exist. No application implementation, database schema or model artifacts were produced by this collection work. | Build the core analytical implementation; the source samples do not establish working matching/scoring. Supabase contents were not inspected. |

Missing references/work: validated links from CSV membership to syllabus components, any further eligibility/placement and academic constraints required by claimed behavior, sufficient job evidence for all four tracks, evidence-backed career definitions, inference relationships and a validated resource collection. [Official supporting-reference candidates](../research/SUPPORTING_REFERENCES_RESEARCH_2026-10-20.md) are researched, not adopted. Obtaining/evaluating evidence is development work; consequential unapproved input choices remain explicit.

## 3. End-to-end processing

1. **Import curriculum.** Use syllabus JSON for competency text and a deduplicated CSV-derived track/code reference for applicability. Preserve source identities and actual page/JSON-path evidence; resolve code-to-component links and extraction issues before complete analysis. Do not substitute CSV competency text or infer absent placement. Identify later official revisions explicitly.
2. **Acquire jobs.** Use one selected Apify adapter first. Record the actual search population, limits, collection time and source payload. Identify duplicates and incomplete details before producing a usable snapshot.
3. **Extract competencies from both inputs.** Extract named tools, technical knowledge and useful capability phrases with exact supporting text. Compare a literal baseline with a contextual extraction candidate. Preserve unmatched terms and ambiguous extraction explicitly.
4. **Normalize and match.** Resolve supported aliases and equivalent expressions. Create coverage links only when academic evidence supports the required competency. Similarity, a shared broad category or a course prerequisite alone cannot establish coverage.
5. **Build career and track profiles.** Associate real postings with explained role definitions and relevant tracks. Aggregate distinct-posting competency requirements and demand measures. Keep the collection population and exclusions visible.
6. **Calculate alignment.** Use the whole eligible curriculum for academic results and selected completed courses for current student results. Find future coverage among applicable courses not completed; exclude it from the current score.
7. **Produce guidance.** Rank gaps with the agreed demand-related rules, attach additive recommendations to courses/curriculum areas, and build ordered skill-specific roadmaps with relevant resource links.
8. **Serve and retain results.** Supply the frontend and reports from the same analysis record and rules version. Preserve browser selections; identify evidence changes and recompute affected results.

### Proposed minimum information contract

These are proposed implementation fields, not claims that all fields already exist in source files.

| Record | Minimum information and use |
| --- | --- |
| Curriculum course/outcome | Generated component identity with basis; saved code/title/type/credit/dependencies/description/outcome/period fields; source hash/parser and actual page/JSON-path references. Official applicability/placement/version/constraints remain missing. Distinguish missing from explicit `None`; derived IDs/units do not become observed source facts. |
| Job posting | Source ID and evidence URL; title, employer and available classification; usable full description; location/country evidence; available posting date; collection time; actor/run/build/query and snapshot identity. Preserve provider values alongside normalization. |
| Extracted competency | Tool/knowledge/capability type; label; source passage and offsets/reference; normalized concept or unresolved status; extractor version. Never invent a confidence percentage. |
| Coverage finding | Requirement competency; supporting course/outcome references; direct/logical/gap classification and explanation; separate future-course references; rules and evidence versions. |
| Analysis result | Selected track or student context/role; evidence versions; eligible-posting count and exclusions; coverage findings; score numerator/denominator and rules; priorities; recommendations or roadmap; report identity. |
| Resource | Skill association, real destination URL, title/provider, relevance basis and link-check status. Resource-selection policy remains D10. |

Retain all original job fields including salary, with missing/null/empty states. Salary and contextual metadata supply no technical-alignment credit or priority weight. Preserve source evidence under the eventual retention policy; measurement and report reproducibility precede deletion.

### Scoring and model decisions

A31 accepts equal binary independently assessable core requirement groups, explicit AND/OR, separate preferred findings, visible uncertainty and equal-contribution mean per-posting aggregation. Plan 2 P3/P6/P7 gives exact formulas, expression identities, support states and bounds; Academic uses all applicable coursework and Student current uses completed courses only.

Demand priorities use distinct-ad counts, careers use mean current-coursework coverage, and topic review starts with evaluated exact-capability n/N. Broader reverse curriculum relevance and categorical low-demand cutoffs remain separately gated. TOPSIS is deferred/conditional under accepted R8, superseding its earlier provisional preference. No custom training or fixed model quota is required.

Pinned GLiNER2, MPNet and NLI checkpoints are starting evaluation candidates, not measured TechGap models. Plan 2 E1–E4 specifies labels, group splits, parameter selection and error reporting. No model confidence becomes proficiency or alignment credit; incomplete sources/denominators cannot silently improve scores.

## 4. Proposed implementation boundaries

Use a small repository layout if the candidate stack is accepted under D14. These paths are intended artifacts; they are not existing application files.

| Proposed path | Responsibility |
| --- | --- |
| `frontend/app/page.tsx` | Role selection and returning-user entry. |
| `frontend/app/student/page.tsx` | Academic inputs, career comparison, selected-role findings and roadmap. Begin with one complete flow; split components as it grows. |
| `frontend/app/academic/page.tsx` | Track dashboard, evidence/findings and additive recommendations. |
| `frontend/app/academic/report/page.tsx` | Report view and print/download actions using an actual analysis record. |
| `frontend/lib/api.ts`, `frontend/lib/context.ts` | API calls/errors and versioned browser-retained selections for both experiences. |
| `backend/app/main.py`, `backend/app/contracts.py` | API entry point and common validated request/result shapes. |
| `backend/app/ingest/curriculum.py`, `backend/app/ingest/jobs.py` | Reusable import and selected-actor collection/normalization commands. |
| `backend/app/analysis/extraction.py`, `backend/app/analysis/coverage.py` | Source-linked competency extraction and coverage/scoring rules. |
| `backend/app/analysis/profiles.py`, `backend/app/analysis/guidance.py` | Career/track aggregation, demand/ranking, recommendations and roadmap generation. |
| `backend/app/storage.py`, `backend/app/reports.py` | Shared-data persistence and reproducible report output. |
| `backend/tests/`, `frontend/tests/`, `docs/operations/README.md` | Source-based analytical checks, user-journey checks and school-operation instructions. |

API responsibilities: retrieve eligible courses and versions; list comparable careers; analyze student selections for a target role; retrieve academic track findings; generate/download a report; expose latest evidence/run status. Exact routes and payload schemas are finalized alongside the first working service, not treated as existing contracts.

One Python implementation owns extraction, coverage and score logic. The frontend presents returned findings instead of maintaining a second set of formulas. Keep privileged provider credentials on the server as basic implementation hygiene; Microsoft authentication and a broader security feature program remain outside the current scope.

## 5. Build phases and concrete tasks

Checkboxes describe future work. None is marked complete merely because this plan exists. Workload is expressed as deliverables and dependencies; no team capacity or processing benchmark supports a calendar promise yet.

### P1 — Prepare the real academic input

- [ ] Build a repeatable import-quality summary for the syllabus JSON batch, preserving hashes/parser versions, missing fields and component collisions. Use the measured inventory in DATA_FLOW.md as the baseline; CSV usage is limited to applicability metadata.
- [ ] Fix extraction defects and verify the affected source layouts before calling an analysis complete (A20); structural `ok` alone is insufficient evidence of accuracy.
- [ ] Build/review the proposed track/code applicability reference from the CSVs; validate links to syllabus components, retaining ambiguous/unmatched cases (D03). Resolve further placement/constraint sources only as needed; include eligible common/core courses and exclude GE using evidence.
- [ ] Define component IDs and raw-to-normalized mappings; preserve conflicting versions for an explicit source-resolution rule instead of fuzzy merging.
- [ ] Import available supported fields with per-record status and source references; rerunning the same input must not create duplicate components/outcomes. Missing metadata must not be invented.

**Artifacts:** curriculum input/applicability mapping, quality summary, source-verified extraction repairs and reusable importer. **Exit:** eligible component links/outcomes are traceable; required extraction issues are resolved before complete analysis; unavailable official metadata is explicit. Mapping validation and any placement/constraint-dependent claims await D03; independent diagnostics can proceed. **Decisions due:** D02–D03 and stack choice D14 before application scaffolding.

### P2 — Acquire and store actual job evidence

- [ ] Execute the preparation/checks in Plan 1 for the selected entry/junior employment cohort and separate internship/OJT cohort, 34-query registry, initial 1,000 employment goal and verified allocation no higher than USD 5. Provider fields/continuation remain contract checks, not assumed completeness.
- [ ] Build on the completed bounded shahidirfan sample and actual field inventory. Before broader collection, agree its population/spend and recheck the contract; inspect descriptions, dates, geography, IDs and failures. The pilot does not authorize another paid run or require an automatic alternative-actor test.
- [ ] Implement the selected adapter, duplicate/repost policy and incomplete-detail status. Record raw and normalized fields, errors and exclusions; never substitute a title/teaser for unavailable full requirements without labeling the evidence limit.
- [ ] Load the agreed usable collection and preserve an identifiable controlled evaluation version. Measure actual table/index/text size; do not infer Supabase capacity from CSV byte size.

**Artifacts:** saved actual output, provider-field mapping, collection summary, reusable collector and initial usable snapshot. **Exit:** every analyzed posting is traceable and eligible under the recorded rules. **Dependency:** D04 spending/population decisions before a run; curriculum work can proceed independently.

### P3 — Implement and assess competency extraction

- [ ] Implement source-linked extraction records for tools, technical knowledge and capability phrases from actual curriculum/job passages.
- [ ] Compare a literal baseline with one contextual extraction candidate and one semantic-linking candidate. Measure extraction errors, incorrect aliases/coverage and unknown-term handling separately on the agreed evaluation material.
- [ ] Choose artifacts based on extraction/linking evidence and measured runtime. Record versions and operating requirements; do not invent accuracy targets or assume pretrained inference is project-specific training.
- [ ] Implement the agreed automatic unknown/uncertainty policy and repeatable reruns. Failed or ambiguous records receive explicit statuses; no recurring human import-approval queue is introduced.

**Artifacts:** real extracted evidence, comparison findings, selected processing artifacts and reusable commands. **Exit:** supported/unsupported matches can be inspected and behavior under unfamiliar terms is defined. **Decisions due:** D07 and D11; experiments need representative inputs from P1/P2.

### P4 — Build alignment, demand and guidance

- [ ] Establish career definitions, posting associations and track relevance from actual evidence. Separate inferred role labels from publisher-supplied job titles; report sparse/uncertain role evidence honestly.
- [ ] Implement direct and justified logical coverage plus possible gaps. Evaluate completed-course coverage separately from all applicable not-yet-completed courses.
- [ ] Implement the accepted forward formulas and uncertainty rules in Plan 2 P7; evaluate grouping/support before complete results. Reverse relevance is a separate D08 gate.
- [ ] Calculate distinct-posting demand/prevalence with explicit denominators; implement the agreed priority and low-demand review rules (D09). Low observed demand does not prove obsolescence or decline.
- [ ] Generate additive, course-linked enhancements under official academic constraints. Obtain missing constraint references before claiming compliance; do not invent unit floors, protected IDs, course hours or projected gains.
- [ ] Produce skill-specific ordered roadmaps and relevant openable resources (D10). Support ordering with learning dependencies or resource sequences; a vocabulary hierarchy alone does not establish a learning order.

**Artifacts:** one analytical service producing real scores, evidence, demand summaries and guidance. **Exit:** the same inputs/evidence/rules yield consistent results; insufficient evidence is explicit. **Dependency:** P3 and D05/D08–D10. This phase supplies shared logic for both user experiences.

### P5 — Complete both working user journeys

- [ ] Implement role entry and separate browser-retained Student/Academic contexts. Recover safely from malformed, incompatible or no-longer-eligible saved selections.
- [ ] Connect Student program/track/year/course inputs to actual eligible curriculum. Show real ranked/alternative careers, requirement comparison, selected-role evidence, current gaps, future coverage and roadmap links.
- [ ] Connect Academic track selection to actual coverage, requirements, scores, gap priorities, low-demand review and anchored recommendations shown alongside findings.
- [ ] Reflect selection/version changes throughout related outputs; remove stale dependent results before replacement results appear. Exercise loading, no-evidence, failure and retry behavior.

**Artifacts:** connected Student and Academic flows. **Exit:** each journey can be completed with actual stored evidence and revisited with selections intact. **Parallel work:** the two experiences can be built independently after the shared result shapes and context handling are stable. No team size or subagent use is assumed.

### P6 — Reports, updates and school operation

- [ ] Generate a consolidated academic report from the exact analysis shown in the dashboard; include track, evidence versions/window, score basis, findings/priorities, recommendations and limits. Implement print and agreed download format (D13).
- [ ] Implement revised-curriculum imports and recurring job collection under D06. Stage replacement data, apply automatic checks, activate successful output and retain a clear failure/retry status. A failed refresh must not silently replace usable findings.
- [ ] Implement the agreed Supabase retention rule (D12), including evidence needed for the controlled evaluation and retained reports. Check source-text, derived-record and index usage; remove only records eligible under that rule.
- [ ] Document ordinary school operation: import commands, refresh schedule/configuration, failure recovery, resource maintenance and retention behavior. No developer-operated manual approval step belongs in that routine.

**Artifacts:** actual printable/downloadable reports, update/retention jobs and an operating guide. **Exit:** a later evidence version changes subsequent analysis without relabeling older controlled findings; a report remains interpretable after retention actions. **Decisions due:** D06, D12–D14. No schedule or deletion is created by this document.

### P7 — Conditional curriculum projection work

**On hold under D01.** The user's removal request conflicts with the unchanged requirements. This is not part of the active ordinary-journey build while the conflict is open.

- [ ] Resolve whether the removal concerns fake demonstrations or the real proposed-enhancement capability. If the real capability is removed, record the explicit baseline/source changes before claiming full compliance.
- [ ] Only if retained: represent additive proposed changes, apply the same evidence/scoring/constraint rules, compare baseline and projected results, permit revision/re-evaluation, and label projections separately from current findings/adopted records.
- [ ] If retained, include prioritized course-specific projected effects in revision guidance and reports. No arbitrary sample improvements or institutional adoption action are permitted.

**Exit:** either implement and verify the retained requirements, or explicitly amend their scope and associated traceability. Neither outcome is assumed.

### P8 — Verify the release and hand it over

- [ ] Walk through AC-01–AC-12 using actual evidence, recording D01's exception until resolved. Check score/count consistency, source links, changed selections, revisits, repeated runs, report output and failed-operation recovery.
- [ ] Complete the agreed analytical evaluation (D11), including false logical coverage and incomplete/new terminology. Report measured boundaries rather than claiming questionnaires prove model correctness.
- [ ] Measure processing/runtime, resource use and retained storage for the real dataset. Assess qualitative responsiveness and reliability against the questionnaires; do not invent numerical pass marks.
- [ ] Exercise operation with revised curriculum and job evidence, verify the chosen retention policy against saved reports, and complete school operating instructions.
- [ ] Synchronize affected older planning documents with resolved decisions using a documented comparison. Preserve unresolved conflicts and original source traceability; document updates do not themselves amend the thesis papers.

**Exit:** working release evidence and operating instructions exist; any remaining limitation or requirements exception is named. External questionnaires remain outside the application.

## 6. Requirement coverage and release evidence

This is a plan-to-requirement mapping, not a claim of implemented coverage. Business rules BR-01–BR-13 apply across the relevant tasks; BR-09/BR-10's projection aspects follow D01.

| Requirements | Work | Acceptance evidence |
| --- | --- | --- |
| FR-SH01, FR-SH02, FR-SH03 | P5, P8 | AC-01: both experiences without sign-in; navigation/revisit retention; correct results after changes. |
| FR-D01, FR-D02, FR-D03, FR-D04, FR-D05 | P1–P4, P6, P8 | AC-07 plus AC-03/AC-10: source-linked comparison; controlled and updated evidence distinguishable; revised curriculum works. |
| FR-T01, FR-T02, FR-T03, FR-T04, FR-T05, FR-T06, FR-T07, FR-T08 | P4–P5, P8 | AC-08, AC-09, AC-10, AC-11: valid inputs; role comparison/alternative; consistent coverage/score/future findings; ordered resources. |
| FR-A01, FR-A02, FR-A03, FR-A04, FR-A05, FR-A06, FR-A07, FR-A08 | P4–P5, P8 | AC-02, AC-03, AC-04: track context, explained coverage, demand-related priorities, additive anchored recommendations. |
| FR-A09, FR-A10 | P6, P8 | AC-05: consolidated real report that can be printed/downloaded and interpreted. |
| FR-A11, FR-M01, FR-M02, FR-M03, FR-M04 | Conditional P7, P8 | AC-06: open scope conflict D01; projected-effects and proposal behavior cannot be marked complete yet. |
| NFR-AC01–NFR-AC05 | P4–P6, P8 | Selection/track sensitivity, agreement among findings/scores/explanations and invalidation of stale outputs. |
| NFR-PE01–NFR-PE05 | P3–P6, P8 | Measured complete journeys and evaluator-assessed acceptable delay; no assumed seconds. |
| NFR-RE01–NFR-RE05 | P1–P6, P8 | AC-01/AC-12: repeatability, persistence, report/roadmap completion and retry without lost valid context. |
| NFR-US01–NFR-US05 | P5–P6, P8 | AC-12: clear instructions, terms, findings and navigation. |
| OUT-A01–OUT-A05, OUT-T01–OUT-T05, OUT-D01–OUT-D05 | P4–P8 | Required activities support the externally assessed outcomes; favorable ratings are not assumed. |

## 7. Immediate next work

Start P1's source inventory/import mapping and P2's collection contract/query proposal. These can proceed without settling every later formula, report option or retention duration. Before scaffolding, confirm D14's proposed stack; before any paid run, verify D04's actual allowance/current controls and apply the cap. The source-dependent eligibility mapping awaits D03. Discuss each remaining decision when its dependent task approaches, using the register rather than restarting the interview.

The earlier 1–2 week aspiration is not a commitment: available people, approved budget, academic references and measured model runtime have not been supplied. P1–P4 establish the real evidence and analytical foundation; P5–P6 connect complete journeys; P8 verifies the delivered behavior. P7 remains conditional.
