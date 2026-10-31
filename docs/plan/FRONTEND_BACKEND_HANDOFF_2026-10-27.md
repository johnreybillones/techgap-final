# TechGap frontend and backend — brainstorm handoff

**Purpose:** Context for a separate session that brainstorms and builds the TechGap frontend and backend. Updated 2026-10-27. The model pipeline is still being built in parallel, so build against the output meanings below with **mock data**. Model accuracy does not block this work; only the output shapes matter.

**Authority:** [PLANNED_DATA_FLOW.md](PLANNED_DATA_FLOW.md) owns what every result means and how it is calculated. This file only carries the parts the system needs. Screen layout, chart types, API design, storage and auth are for the frontend/backend session to decide. If this file and the contract disagree, the contract wins.

## 1. What the system does

TechGap compares the technical requirements in saved JobStreet postings (Philippine local pool; a separate international pool is planned) with what a school's syllabi actually teach. It serves two users:

- **Faculty:** see how well all courses in a track cover observed job requirements, and where the gaps are.
- **Students:** pick a track and the courses they have completed, then see which careers their completed coursework best matches and what to learn next.

Four tracks only: **BSCS Intelligent Systems, BSCS Game Development, BSIT Network Technology, BSIT Web Development.** General Education and informal learning never create coverage.

## 2. Data the system can use now

**Syllabi** — 119 JSON files in `data/syllabi/` (all `status: ok` as of 2026-10-24). Fields used by the system: `course_code`, `course_title`, `course_type` (Lecture/Lab), `course_credit`, `prerequisites`, `corequisites`, `track`, `year_level`, `semester`, `course_description`, `course_learning_outcomes`, `learning_plan`, `status`, `issues`. Lecture and lab sections are separate files (code suffix `LA`/`LC`).

Course-to-track applicability, from the JSON `track` value:

| JSON `track` | Applies to |
| --- | --- |
| `Common (IT & CS)` | all four tracks |
| `CS Core & Electives` | both BSCS tracks |
| `IT Core & Electives` | both BSIT tracks |
| `CS - Intelligent Systems`, `CS - Game Development`, `IT - Network Technology`, `IT - Web Development` | that track only |
| `General & Foundational` | Number Theory → both BSCS; Living in the IT Era and IT Application Tools in Business → both BSIT; any other → unresolved, never broadcast |

**Career roles** — a draft list of 19 broad roles is awaiting approval: [CURATED_ROLE_LIST_DRAFT_2026-10-27.md](CURATED_ROLE_LIST_DRAFT_2026-10-27.md). Treat role names as placeholders until approved. Students choose from this list only; raw employer titles are never shown as a different career name.

**Job postings** — about 497 saved postings, with provisional labels only. Real requirement and coverage results do not exist yet; use mock data.

## 3. Shared vocabulary in every result

- **Cohort:** `employment` or `internship`. Always kept separate; never mixed in one count or score.
- **Pool:** `local` (Philippine jobs and remote jobs open to Philippine applicants) or `international` (Malaysia, Singapore, Indonesia). Separate like cohorts; never mixed in one count or score. Only local data exists today.
- **Requirement modality:** `required`, `preferred`, `allowed_alternative`, `unclear`. Only required requirements count toward scores; preferred ones are shown separately.
- **Requirement group:** one independently assessable required capability. Explicit alternatives form one OR group; jointly required parts form an AND group.
- **Coverage status of a group:** `covered`, `partial`, `missing`, `unresolved`. Unresolved means not enough evidence; it is **not** missing.
- **Capability categories:** technical task, technical knowledge, tool/technology.
- **Every result carries:** pool, cohort, track or role, observation window, distinct-posting counts (assessable and total), syllabus version, rule version, and source references (job posting IDs/URLs and syllabus passages with course code).

## 4. Formulas the backend will display, not recompute differently

- **Posting coverage** = covered groups / distinct required groups. No assessable required groups means **no score** (not 0% or 100%). Unresolved groups qualify or withhold the score.
- **Role or track alignment** = mean of assessable postings' coverage, one contribution per posting. Always show how many postings had a score and how many did not.
- **Observed demand** for a requirement = `n / N`: `n` distinct assessable postings stating it, out of `N` assessable postings in the selected cohort, track/role and window.
- **Gap order** = confirmed gaps ordered by observed demand; equal demand ties.

## 5. Faculty results

| View | Data the pipeline will provide |
| --- | --- |
| Industry skill demand ranking | Required capabilities ordered by `n/N`, with posting counts, cohort and window. |
| Curriculum–skill map | Course-by-capability links with covered/partial/missing/unresolved status. |
| Demand vs curriculum coverage | Each capability's demand beside its coverage status, with denominators. |
| Coverage distribution | Counts or proportions of each status for a track or role. |
| Career-family comparison | Requirement frequencies and coverage across roles that have enough assessable postings; sparse roles stay visibly sparse. |
| Competency category distribution | Requirements grouped into technical categories, with counts. |
| Course-level relevance evidence | Capabilities a course supports, partly supports or does not establish, with source passages. No course "relevance %". |
| Targeted syllabus-change suggestions | For a confirmed gap: an additive capability for a related course, or a curriculum area; shows job evidence, demand and course link. Faculty decides. |

Not included: demand trend over time, salary or hiring outcomes, curriculum simulation.

## 6. Student results

**Input:** track plus the final set of **completed course IDs**. For a regular student, the app may auto-select courses before the chosen year level and semester (the syllabus JSON has `year_level` and `semester`). An irregular student may edit the selection freely. The pipeline scores only the completed IDs; future courses can be shown as possible later coverage but never count toward the current score.

| View | Data the pipeline will provide |
| --- | --- |
| Ranked career recommendations | Roles ranked by completed-course coverage of their required capabilities; driving competencies, assessable and total posting counts, ties, evidence limits. |
| Career details | Required skills with status for the student's courses; preferred skills labeled separately; job counts and syllabus evidence. |
| Selected career analysis | Posting-level and combined alignment, reasons per status, supporting courses, gaps, and future-course possibilities shown separately. |
| Career-specific roadmap | Confirmed gaps ordered by demand, with learning resources where available. No invented prerequisite order. |

## 7. Display rules the UI must respect

- A role with no assessable postings stays selectable but shows **no numeric score**.
- Show denominators and sparse counts; never hide that a role or track has few postings.
- A recommendation is an **academic match**, not personal mastery, hiring probability or seniority eligibility.
- Employment and internship results are always labeled and kept apart.
- Demand figures describe a query-limited sample in a stated window, not the national market.
- Unresolved is shown as unresolved, never folded into missing.

## 8. Learning resources (system side)

Learning resources are a frontend/backend concern, not part of the model pipeline. The pipeline outputs confirmed gaps; the backend attaches a verified resource where one exists. A missing resource never removes the gap. Resources must be keyed by the same capability names the pipeline outputs. Those names come from requirement extraction, which is not built yet, so collect resources now and map them once the names exist.

## 9. Open items for the brainstorm session

- Tech stack, API design, storage, auth and deployment: not decided anywhere yet.
- The pipeline's output file format does not exist yet; define a mock that carries the fields in §3–6 and agree it with the pipeline later.
- Capability naming key for learning resources (see §8).
- Final career-role list (pending approval).
- How the international pool is shown to faculty and students (for example a side-by-side comparison) is a UI decision; international data is not collected yet.
- Refresh: job data is re-collected yearly and syllabi can be uploaded by users; results should refresh without a person involved. The backend likely triggers the scripted refresh and publishes new versioned results. Upload handling does not exist yet. See [PLANNED_DATA_FLOW.md](PLANNED_DATA_FLOW.md) §7.
- Out of scope here: job collection and model training.
