# Proposed amendments to SYSTEM_REQUIREMENTS.md (2026-10-31)

**Status:** Proposal only. Nothing here is applied to `SYSTEM_REQUIREMENTS.md`. Each item records a decision the user gave in the frontend/backend brainstorm and the text it would change. The user approves, edits or rejects each item before any edit is made. IDs refer to the current requirements file.

**Already applied in the file (no action):** academic-constraint reference (CMO 25 minimums, §3.1), printable report shared by URL (FR-A09, FR-A10), additive-only recommendations with CMO knowledge area and no removals (BR-09), low-demand review list marked CHED-mandated (FR-A06).

## A1. Split the user groups and add a signed-in Academic Administrator role (user decisions: Q1 A, 2026-10-31 role clarification)

- **U6 is reversed.** The single Faculty/Academic Administrator group is split. Add a user-confirmation row (U7): *Faculty* (faculty member/professor) and *Academic Administrator* (department chair, associate dean, dean) are separate roles; each title belongs to one role.
- **§2.1:** three roles.

  | Role | Sign-in | Features |
  | --- | --- | --- |
  | Student | No | Student features |
  | Faculty | No | Faculty features |
  | Academic Administrator | Yes, invite-only; accounts created by a developer | All Faculty features, plus syllabus upload |

  Rename "Faculty/Academic Administrator" to "Faculty" wherever it names the no-sign-in group (§1, §2.1, §3.2, §5.3, §9). The external questionnaires keep their respondent definitions; they are not system roles.
- **§2.3:** change "Sign-in, account registration, and verified academic identity are not part of the confirmed access model" to: Student and Faculty use the system without sign-in. Academic Administrators sign in; there is no self-registration and no in-app user management.
- **FR-SH01:** the user chooses Student or Faculty without sign-in. An Academic Administrator signs in.
- **BR-11:** add "Academic Administrator access is authenticated; the Student and Faculty role selections are not."
- **New FR-AD01:** Academic Administrators shall sign in to use syllabus upload; other users shall not need to.
- **New FR-AD02:** Academic Administrators shall be able to upload a single-course syllabus PDF. The system shall extract it, publish it as a new syllabus version, show the status of the resulting recalculation, and carry extraction warnings visibly (see A7).
- **FR-D05:** replace "This does not require a user-facing syllabus upload activity" with a reference to FR-AD02.
- **Not requirements (user scope):** release rollback in the interface, learning-resource editing in the interface, and any general system-administration console. A developer reverts a release and imports learning resources.

## A2. Remove curriculum simulation (user decision: Q2 A)

- **Remove:** FR-M01–FR-M04, FR-A11, BR-10, the "Curriculum revision guidance" and "Curriculum simulation" rows in §3.2, AC-06.
- **Reword:** the simulation sentence in §2.2 and U1; "simulated" in BR-09 and §8.1; the simulation sentence in §10.
- **Follow-up:** Chapter 1 §1.2 lists simulation, so `PAPER_CHANGE_NOTES.md` needs an entry. `QUESTIONNAIRE_TRACEABILITY.md` and `REQUIREMENTS_VERIFICATION.md` were not read for this proposal and may need matching edits.

## A3. Add the international pool (user decision: Q3 B)

- **FR-D02 and §3.1 job-market reference:** "Philippine JobStreet postings" becomes the local pool (Philippine jobs and remote jobs open to Philippine applicants) plus a separate international pool (Malaysia, Singapore, Indonesia), per `PLANNED_DATA_FLOW.md` §1.
- **New FR-D06:** The system shall let the user select the pool, shall never combine pools in one count or score, and shall state "no data yet" when a pool has no result set.
- The international pool has no collected data today; FR-D06 is satisfied by the "no data yet" state until it does.

## A4. Roadmap order wording (user decision: Q5 A)

- **FR-T07:** replace "a clear learning order" with "steps ordered by observed demand, labeled as a demand order and not a prerequisite order".

## A5. Job-market updates (user decision: Q7 B)

- **FR-D02:** state that job data is re-collected yearly and starts automatically within a standing authorization (cost ceiling, frozen queries, recorded source-access basis), per `JOBSTREET_COLLECTION.md` §8. No automatic run happens until that authorization is recorded.

## A6. Retention, evaluation dataset, hosting (user decisions: Q10 A, Q9 A, evaluation-label A)

- **FR-SH02:** state that selections are retained in the user's own browser on that device; the server stores no student selections and there is no cross-device retention.
- **FR-D04:** state that a result release whose manifest `purpose` is `controlled_evaluation` is always labeled and never combined with other releases. This is an application convention; the data-flow contract does not define the flag (decision D3).
- **§6:** add a known-limitation note: the free-tier hosting can cause a slow first load after idle periods. No numeric target is added (U5).

## A7. Upload rules (user decisions: N1 A, N2 A, N4 A, D6a)

- Accepted upload: a single-course, text-native CICS syllabus PDF. Other files are rejected with a clear message.
- Publish is automatic. The file is accepted when its text is extractable and course code and track can be extracted; title is metadata and not required (data-flow decision D6a). It is rejected otherwise. `needs_review` and `issues` are carried as visible warnings.
- A course with no CMO knowledge-area mapping is shown as "unmapped" and is not marked CHED-mandated until mapped.
