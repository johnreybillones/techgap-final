# TechGap planned data flow

**Status:** Agreed planning contract, 2026-10-23. This describes the intended data processing and result data; it does not claim that the pipeline has been implemented or validated. It records the decisions reverified in the current discussion. Where older plans conflict, use this contract for the revised design. Keep the older documents as history until their separate revisions are agreed.

**Boundary:** Job acquisition, query tuning, duplicate avoidance, cost and collection targets belong to the collection plan. Backend storage/APIs and frontend layout/interactions may have separate implementation documents later. This file owns the rules that turn saved jobs and syllabus evidence into student and faculty results. Changing an output's meaning requires updating this contract even if its screen or API changes elsewhere.

## 1. Inputs and populations

| Input | Use and limit |
| --- | --- |
| Saved JobStreet postings | Preserve the original title, description, source ID, URL, collection/publication dates, query, and available raw fields. Reuse previously saved IDs when collection or processing is revised. A query identifies candidates; its results are not automatically relevant or members of its originating track. |
| Syllabus JSON in `data/syllabi/` | Use course code, track, description, learning outcomes and available learning-plan text as academic evidence. Include applicable courses even when extraction status is `needs_review`; carry source and completeness warnings. Do not fill missing competency text from a title, CSV, or outside reference. Updated year/semester metadata will be used when supplied. |
| Curated career-role list | Defines the career names students may select and compare. The four academic tracks define track scope; ESCO occupations and search-query labels do not define track or student-facing career labels. |
| Verified learning resources | Used only to link a confirmed gap to a real, suitable learning destination. An absent resource does not erase the gap. |

The four supported tracks are **BSCS Intelligent Systems, BSCS Game Development, BSIT Network Technology, and BSIT Web Development**. Relevant common/core computing work and coursework can contribute to the applicable tracks; General Education and informal learning do not create academic coverage.

Include relevant employment postings at **all seniority levels**. Keep actual internship/OJT vacancies in a separate cohort so their counts and results are not mixed with employment. Seniority may be retained as descriptive context, but it neither excludes a relevant job nor changes its technical coverage score. Philippine jobs and remote jobs open to Philippine applicants are in scope. The collection period is recent first, with a maximum lookback of twelve months; actual coverage depends on the postings obtained.

## 2. Processing sequence

1. **Preserve and deduplicate.** Keep raw observations and versions; identify distinct postings for analysis. Report returned rows, distinct postings, relevant postings, and assessable postings separately. Never use an older model decision as a gold label.
2. **Decide relevance and links.** Use a clear technical title to link a posting to one or more of the four tracks or a curated career role. For a generic, unfamiliar or conflicting title, inspect the actual duties and requirements. Keep relevant general computing postings even if no specific track or curated role can be supported; they can inform overall computing demand, but not a fabricated track/role profile. Retain the employer title and reason for each link. Do not infer relevance solely from the search query or force an unmatched title into a different career name.
3. **Extract job requirements.** Find source-backed technical capabilities in stated duties and required qualifications. Keep the exact passage, posting ID and whether it is required, preferred, an allowed alternative, or unclear. Preserve task/tool qualifiers and explicit AND/OR wording. Salary, years of experience, education, benefits, soft skills and offered training remain available as context but do not count as technical skills.
4. **Prepare academic evidence.** Read applicable syllabus descriptions, outcomes and learning-plan statements with their course code, track, source field and extraction status. A short syllabus phrase is evidence only for what it actually says. Course title or broad topic alone does not prove a specific job capability. Flag missing or uncertain course evidence instead of dropping the course.
5. **Match the same capability.** Retrieve possible syllabus passages by exact terms/aliases and semantic search, then decide whether those passages support the *same* task, knowledge or tool requirement at the stated scope. Similarity is a search aid, not proof of coverage. For a multi-part requirement, record which parts are supported; preserve allowed alternatives. Use simple parsing first, and compare any proposed extraction or matching model with human-checked examples before adopting it.
6. **Calculate and publish results.** Derive demand, coverage, gaps, career comparisons, recommendations and roadmaps from the linked evidence. Every result keeps its cohort, track/role, observation window, distinct-posting counts, syllabus version, rule version, and source references. A new model or rule can rerun on saved postings without another paid collection.

An extraction failure leaves a relevant raw posting available for repair but out of demand and coverage calculations that require its missing technical text. It must not count as a posting with zero demand or zero coverage.

## 3. Calculation rules

- A **requirement group** is one independently assessable required capability. Repeated wording in one posting counts once. Explicit alternatives form one OR group; jointly required components form an AND group. Preferred and unclear requirements appear separately and do not inflate the required-skill score.
- A group is **covered** only when the selected syllabus evidence supports every required component, or at least one allowed OR alternative. A group is **partial** when an explicit multi-part requirement has supported and unsupported components. A confirmed unsupported group is **missing**. Insufficient job or syllabus evidence is **unresolved**, not missing. Partial groups receive no full-coverage credit in the strict score.
- For a posting with a complete set of assessable required groups: `posting coverage = covered groups / distinct required groups`. No assessable required groups means **no score**, not 0% or 100%. With unresolved groups or an incomplete requirement set, qualify or withhold the score rather than silently treating unknowns as misses.
- A role or track alignment figure is the **mean of assessable distinct postings' coverage**, with one contribution per posting. Always show how many relevant postings had a usable score and how many did not. The same rule applies to faculty and student calculations; the syllabus evidence set differs.
- **Observed demand** for a requirement is `n / N`: `n` distinct assessable postings in the selected population that state it, over `N` postings whose technical requirements can be assessed. State the cohort, role/track and time window. Count a requirement once per posting; do not present query-limited sample percentages as population-wide market rates.
- Order confirmed gaps by observed distinct-posting demand. Equal demand ties. Low observed demand is descriptive only; one snapshot cannot establish a decline, obsolescence or a reason to remove a course. No untested weighting, TOPSIS rank, or trend line is needed for the first reliable result.

## 4. Faculty result data

Faculty results compare **all applicable courses in a track** with observed job requirements. They must expose the underlying jobs, course passages, counts and unresolved evidence. The following data supports the proposed views; chart type and layout belong to the frontend.

| Output | Data the pipeline can produce |
| --- | --- |
| Industry skill demand ranking | Required technical capabilities ordered by observed `n/N`, with posting counts and cohort/window. |
| Curriculum–skill map | Course-by-capability evidence links with covered, partial, missing or unresolved status; no strength claim based solely on a short phrase. |
| Demand versus curriculum coverage | Each capability's observed demand beside its supported curriculum coverage/status, with denominators and limits. |
| Coverage distribution | Counts or proportions of covered, partial, missing and unresolved requirement groups for a chosen track or curated career role. |
| Career-family comparison | Requirement frequencies and coverage across curated roles where enough assessable postings exist; sparse roles stay visibly sparse. |
| Competency category distribution | Observed requirements grouped into explainable technical categories, with category rules and counts. |
| Course-level relevance evidence | The observed job capabilities a course supports, partly supports, or does not establish, with source passages. Do not invent a course “relevance percentage.” |
| Targeted syllabus-change suggestions | For a confirmed, observed gap, suggest an **additive** capability or practice for a related course when its current subject provides a defensible link; otherwise suggest a curriculum area. Show the job evidence, observed demand, course relationship and any unknown institutional constraints. Faculty decides whether to adopt it. |

The proposed **skill demand trend** view is deferred. A single query-limited collection snapshot cannot establish how demand changed over time. Salary, hiring outcomes and curriculum effects are likewise not inferred from these records. No hypothetical curriculum simulation is part of this flow.

## 5. Student result data

The system receives a track and the **final set of completed course IDs**. For a regular student, the application may auto-select courses before the chosen year level and semester once reliable placement metadata is supplied. An irregular student may change the completed-course selection freely. This selection behavior is an application concern; the pipeline scores only the completed IDs. Future courses may be shown as possible later coverage but never count toward the current score.

| Output | Data the pipeline can produce |
| --- | --- |
| Ranked career recommendations | Curated career roles ranked by current completed-course coverage of their observed required capabilities. Show the competencies driving the ranking, assessable and total posting counts, ties, and evidence limits. This is an academic match, not a measure of personal mastery, hiring probability or eligibility by seniority. |
| Career details | Observed required skills and their covered, partial, missing or unresolved status for the student's completed courses; source job counts and relevant syllabus evidence. Preferred requirements remain separately labeled. |
| Selected career analysis | The chosen role's posting-level and combined alignment, reasons for each status, supporting completed courses, gaps, and future-course possibilities shown separately. A role with no assessable postings remains selectable but has **no numeric alignment score**. |
| Career-specific roadmap | Confirmed gaps ordered by observed demand, with verified learning resources where available. Show supported alternatives; do not invent a universal prerequisite order or a resource for every gap. |

Employment and internship evidence are identified separately throughout the student results. Raw employer titles without a defensible mapping are never silently displayed as a different curated career.

## 6. Reliability and document ownership

Before choosing extraction/matching methods or trusting rankings, check a **small, one-time human-labeled sample** covering job relevance/track links, requirement extraction, and syllabus support decisions. Compare simple rules with candidate models on the same cases, inspect recurring errors, fix the method and rerun saved postings. A model checkpoint, similarity score or plausible chart does not establish accuracy. Keep source spans, versioned decisions, incomplete counts and examples of errors so results can be audited. A small pilot may expose a defect; it cannot establish population-wide accuracy.

The next collection effort should be a **small cost-capped yield test**, using previously saved IDs to measure genuinely new distinct relevant postings before larger targets. Query and duplicate improvements belong to a separate JobStreet collection discussion; this data-flow contract does not authorize a paid campaign.

The collection document owns acquisition rules. This document owns data meanings and formulas. Future backend and frontend documents should reference these outputs rather than copy their definitions. Open inputs include the updated syllabus placement fields, the curated role list, verified learning resources, and measured model quality. Until supplied or checked, dependent results remain qualified rather than filled by assumptions.
