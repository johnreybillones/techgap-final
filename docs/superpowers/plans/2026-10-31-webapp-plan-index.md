# TechGap web app — plan index (2026-10-31)

The spec ([2026-10-31-techgap-frontend-backend-design.md](../specs/2026-10-31-techgap-frontend-backend-design.md)) covers four independently buildable parts. Each gets its own plan, so each produces working, testable software on its own. Only Plan A is written; B–D are scoped here and written when their inputs exist.

| Plan | Delivers | Needs first | Status |
| --- | --- | --- | --- |
| **A. Core API** — [2026-10-31-webapp-core-api.md](2026-10-31-webapp-core-api.md) | Release format v0, mock release, loader, active-release pointer, public read API, developer CLI | Nothing | Written |
| **B. Frontend** | Role chooser; student and faculty screens against the mock release; shared display-rule components; print report page; browser-stored selections | Plan A (mock release served locally) | Not written |
| **C. Upload, auth, jobs, storage** | Academic Administrator sign-in (Supabase Auth, invite-only); single-course PDF upload, extraction and accept/reject; buckets (raw PDFs, raw jobs, syllabus sets, release archive); `syllabus_records`, `syllabus_versions` and `jobs` tables; a new syllabus version per upload (previous version with that course replaced or added); queued uploads and one follow-up recompute; failure handling with developer re-dispatch; workflow dispatch and result import; the yearly workflow gated by `YEARLY_REFRESH_ENABLED`; release retention (active plus 4 recent); learning-resource import file | Plan A; D6 and D7 from the data-flow session applied; Supabase project; GitHub dispatch token | Not written |
| **D. Student scoring and student endpoints** | Pure scoring module for the contract's section 3 (status for a course set, bounds, scored / qualified / not scored, unweighted mean); ranking, role analysis, roadmap, "possible later" endpoints | Plan A | Unblocked as a rule set (contract decisions P1–P5, P7, P8 of 2026-10-31); not written |

## Decided in the contract (2026-10-31)

P1 group status for a course set, P2 bounds, P3 combined alignment, P4 ranking, P5 roadmap gaps and "possible later", P7 Review list, P8 public display of jobs. Still open: P6 (capability registry; only affects learning-resource keys, Plan C) and P9 (release-format review).

Plan B (frontend) is preceded by an HTML/CSS/JS prototype, to agree the screens and interactions before the React build.

## Order

A first. Then B and C can proceed in parallel (separate files). D starts when P1–P6 are answered and A is done.
