# TechGap Questionnaire and Source Traceability

This document maps every rated statement in the two questionnaires to [System requirements](SYSTEM_REQUIREMENTS.md). It contains 50 faculty/administrator items and 40 student items. Source prefixes distinguish repeated printed codes: `FQ-CA1` and `SQ-CA1` are different items.

The expected behaviors below are paraphrases for system review, not replacements for the survey wording. Quality and usefulness ratings remain external, qualitative evaluations. No passing rating or numerical response-time target is added.

Page references are physical PDF page numbers.

## 1. Faculty and academic administrators

Source: [Faculty questionnaire](../paper/TechGap%20Questionnaire%20for%20Faculty.pdf).

### 1.1 Curriculum alignment analysis — page 3

| Item | Expected system behavior | Requirements |
| --- | --- | --- |
| FQ-CA1 | Present the relationship between the selected curriculum track and skill requirements in the analyzed JobStreet dataset. | FR-A01, FR-A03, FR-D04 |
| FQ-CA2 | Connect curriculum coverage classifications to curriculum content for that track. | FR-A02 |
| FQ-CA3 | Present industry skill requirements associated with the selected track. | FR-A03 |
| FQ-CA4 | Identify the track to which each alignment result applies. | FR-A01 |
| FQ-CA5 | Allow coverage and industry requirements for the same track to be viewed together. | FR-A02, FR-A03 |

### 1.2 Gap and obsolescence reports — page 4

| Item | Expected system behavior | Requirements |
| --- | --- | --- |
| FQ-GO1 | Distinguish covered competencies from possible gaps. | FR-A04, FR-D03 |
| FQ-GO2 | Present gap priorities in relation to demand in the analyzed dataset. | FR-A05, BR-07 |
| FQ-GO3 | Identify curriculum topics with low analyzed demand for academic review. | FR-A06, BR-08 |
| FQ-GO4 | Explain why a competency or topic is identified as a possible gap or low-demand topic. | FR-A04, FR-A06, NFR-AC05 |
| FQ-GO5 | Keep gap and low-demand findings associated with the selected track. | FR-A01, FR-A06, NFR-AC01 |

The questionnaire's section title uses “obsolescence,” while its items describe low demand warranting further review. BR-08 preserves that more limited interpretation.

### 1.3 Curriculum recommendations — page 5

| Item | Expected system behavior | Requirements |
| --- | --- | --- |
| FQ-CR1 | Identify course-related areas for additional technical competencies. | FR-A07 |
| FQ-CR2 | Explain how a proposed enhancement addresses an identified gap. | FR-A07, NFR-AC05 |
| FQ-CR3 | Present recommendations as additions or enhancements to the existing curriculum. | FR-A07, BR-09 |
| FQ-CR4 | Identify the course or curriculum area associated with each enhancement. | FR-A07 |
| FQ-CR5 | Permit gaps and proposed enhancements to be reviewed together. | FR-A08 |

### 1.4 Generated reports for academic review — page 6

| Item | Expected system behavior | Requirements |
| --- | --- | --- |
| FQ-GR1 | Consolidate alignment findings, gaps, and recommendations in a generated report. | FR-A09 |
| FQ-GR2 | Include summarized findings suitable for academic examination. | FR-A09 |
| FQ-GR3 | Present a printable report suitable for curriculum-review discussions. | FR-A10, NFR-US04 |
| FQ-GR4 | Include the selected curriculum track in the report. | FR-A01, FR-A09 |
| FQ-GR5 | Allow findings to be retained or shared for further academic review. | FR-A10 |

### 1.5 Functional accuracy — page 7

| Item | Expected system behavior | Requirements |
| --- | --- | --- |
| FQ-FA1 | Display findings that correspond to the selected track. | NFR-AC01 |
| FQ-FA2 | Keep coverage and possible gap classifications consistent. | NFR-AC02 |
| FQ-FA3 | Keep the alignment score consistent with track coverage information. | NFR-AC03 |
| FQ-FA4 | Update displayed results after the selected track changes. | FR-SH03, NFR-AC04, BR-12 |
| FQ-FA5 | Ensure explanations correspond to the displayed findings. | NFR-AC05 |

### 1.6 Performance efficiency — page 8

| Item | Expected system behavior | Requirements |
| --- | --- | --- |
| FQ-PE1 | Respond to track selection within an acceptable time. | NFR-PE01 |
| FQ-PE2 | Display the alignment dashboard within an acceptable time. | NFR-PE02 |
| FQ-PE3 | Display gap findings within an acceptable time. | NFR-PE03 |
| FQ-PE4 | Generate the curriculum report within an acceptable time. | NFR-PE04 |
| FQ-PE5 | Permit completion of evaluation activities without excessive delays. | NFR-PE05 |

### 1.7 Reliability — page 9

| Item | Expected system behavior | Requirements |
| --- | --- | --- |
| FQ-RE1 | Remain operational throughout academic evaluation activities. | NFR-RE01 |
| FQ-RE2 | Complete repeated analysis using the same track and dataset without failure. | NFR-RE02 |
| FQ-RE3 | Retain the selected track between related views. | FR-SH02, NFR-RE03 |
| FQ-RE4 | Complete report generation without crashes or unexpected interruption. | NFR-RE04 |
| FQ-RE5 | Allow retry after an operation fails and permit continued use. | NFR-RE05 |

### 1.8 Usability — page 10

| Item | Expected system behavior | Requirements |
| --- | --- | --- |
| FQ-US1 | Provide clear instructions for academic activities. | NFR-US01 |
| FQ-US2 | Make academic features easy to locate. | NFR-US02 |
| FQ-US3 | Use understandable terminology. | NFR-US03 |
| FQ-US4 | Present findings in a visually interpretable form. | NFR-US04 |
| FQ-US5 | Support navigation between related academic results without confusion. | NFR-US05 |

### 1.9 Perceived usefulness — page 11

| Item | Expected basis for the user's evaluation | Requirements/outcomes |
| --- | --- | --- |
| FQ-PU1 | Consolidated findings help curriculum review. | FR-A09, OUT-A01 |
| FQ-PU2 | Findings help identify topics requiring further examination. | FR-A04, FR-A06, OUT-A02 |
| FQ-PU3 | Gap information helps recognize requirements needing added curriculum coverage. | FR-A04, FR-A07, OUT-A03 |
| FQ-PU4 | Alignment outputs can be presented in curriculum discussions. | FR-A03, FR-A10, OUT-A04 |
| FQ-PU5 | Reports help prepare academic-review documentation. | FR-A09, FR-A10, OUT-A05 |

### 1.10 Decision-making support — page 12

| Item | Expected basis for the user's evaluation | Requirements/outcomes |
| --- | --- | --- |
| FQ-DS1 | Alignment findings support consideration of whether revisions are needed. | FR-A03, OUT-D01 |
| FQ-DS2 | Gap priorities support selection of areas for further review. | FR-A05, OUT-D02 |
| FQ-DS3 | Recommendations support consideration of possible enhancements. | FR-A07, OUT-D03 |
| FQ-DS4 | Explanations connect proposed enhancements with the findings. | FR-A07, FR-A08, NFR-AC05, OUT-D04 |
| FQ-DS5 | Advisory outputs support, and preserve, stakeholders' final judgment. | BR-01, OUT-D05 |

## 2. Students

Source: [Student questionnaire](../paper/TechGap%20Questionnaire%20for%20Students.pdf).

### 2.1 Curriculum-to-career alignment — page 3

| Item | Expected system behavior | Requirements |
| --- | --- | --- |
| SQ-CA1 | Show how selected completed courses relate to requirements of the chosen role. | FR-T05 |
| SQ-CA2 | Distinguish competencies represented by selected coursework from gaps. | FR-T06 |
| SQ-CA3 | Identify role requirements associated with official courses not yet completed as Future Curriculum Coverage. | FR-T06, BR-05 |
| SQ-CA4 | Allow completed courses to be selected for analysis. | FR-T01 |
| SQ-CA5 | Display an alignment score for the selected career role. | FR-T05 |

### 2.2 Career pathway recommendations — page 4

| Item | Expected system behavior | Requirements |
| --- | --- | --- |
| SQ-CP1 | Suggest roles relevant to learning represented by selected courses. | FR-T02 |
| SQ-CP2 | Display role skill requirements that support career-option comparison. | FR-T03 |
| SQ-CP3 | Allow another available role to be selected for a preferred pathway analysis. | FR-T04 |
| SQ-CP4 | Present suggested roles in ranked order. | FR-T02 |
| SQ-CP5 | Identify the target role used for the detailed analysis. | FR-T04 |

### 2.3 Upskilling guidance — page 5

| Item | Expected system behavior | Requirements |
| --- | --- | --- |
| SQ-UG1 | Address the chosen role's identified gaps through the roadmap. | FR-T07 |
| SQ-UG2 | Provide a clear order for learning the recommended skills. | FR-T07 |
| SQ-UG3 | Link resources relevant to the roadmap competencies. | FR-T08 |
| SQ-UG4 | Identify the individual skill to study at each learning step. | FR-T07 |
| SQ-UG5 | Allow linked roadmap resources to be opened. | FR-T08 |

### 2.4 Functional accuracy — page 6

| Item | Expected system behavior | Requirements |
| --- | --- | --- |
| SQ-FA1 | Reflect the selected program, year level, and completed courses in the results. | FR-T01, NFR-AC01 |
| SQ-FA2 | Keep displayed coverage and gap classifications consistent. | NFR-AC02 |
| SQ-FA3 | Keep the personal alignment score consistent with displayed coverage. | NFR-AC03 |
| SQ-FA4 | Update results after program or course selections change. | FR-SH03, NFR-AC04, BR-12 |
| SQ-FA5 | Keep explanations consistent with the displayed results. | NFR-AC05 |

### 2.5 Performance efficiency — page 7

| Item | Expected system behavior | Requirements |
| --- | --- | --- |
| SQ-PE1 | Respond to student input selections within an acceptable time. | NFR-PE01 |
| SQ-PE2 | Display career suggestions within an acceptable time after course submission. | NFR-PE02 |
| SQ-PE3 | Display alignment results within an acceptable time after role selection. | NFR-PE03 |
| SQ-PE4 | Make the roadmap available within an acceptable time. | NFR-PE04 |
| SQ-PE5 | Permit completion of evaluation activities without excessive delays. | NFR-PE05 |

### 2.6 Reliability — page 8

| Item | Expected system behavior | Requirements |
| --- | --- | --- |
| SQ-RE1 | Remain operational throughout student evaluation activities. | NFR-RE01 |
| SQ-RE2 | Complete repeated analysis for the same selected courses and role without failure. | NFR-RE02 |
| SQ-RE3 | Retain selected information between related views. | FR-SH02, NFR-RE03 |
| SQ-RE4 | Load the roadmap without crashes or unexpected interruption. | NFR-RE04 |
| SQ-RE5 | Allow retry after failure and permit continued use. | NFR-RE05 |

### 2.7 Usability — page 9

| Item | Expected system behavior | Requirements |
| --- | --- | --- |
| SQ-US1 | Provide clear instructions for student activities. | NFR-US01 |
| SQ-US2 | Make student features easy to locate. | NFR-US02 |
| SQ-US3 | Use understandable terminology. | NFR-US03 |
| SQ-US4 | Present results in a visually interpretable form. | NFR-US04 |
| SQ-US5 | Support navigation between related student results without confusion. | NFR-US05 |

### 2.8 Perceived usefulness — page 10

| Item | Expected basis for the user's evaluation | Requirements/outcomes |
| --- | --- | --- |
| SQ-PU1 | Role requirements help the student understand needed technical competencies. | FR-T03, FR-T05, OUT-T01 |
| SQ-PU2 | Coverage and gaps clarify the limits of completed-course evidence. | FR-T06, BR-04, OUT-T02 |
| SQ-PU3 | Gaps and roadmap steps identify independent-learning needs. | FR-T06, FR-T07, OUT-T03 |
| SQ-PU4 | Roadmap links help identify relevant learning resources. | FR-T08, OUT-T04 |
| SQ-PU5 | Role analysis and roadmap support further preparation for a preferred pathway. | FR-T04, FR-T07, OUT-T05 |

## 3. Chapter 1 capabilities and boundaries

These requirements remain in scope even where no rated questionnaire item directly covers them.

| Chapter evidence | Required behavior or boundary | Requirements/sections |
| --- | --- | --- |
| §1.1, pp. 11–12; §1.7, pp. 24–25 | Advisory curriculum decision support within CICS at DLSU-D. | BR-01; §2 |
| §1.2, pp. 13–14; §1.5, p. 19 | Ongoing acquisition and integration of industry skill evidence. | FR-D02 |
| §1.2, p. 13; §1.7, pp. 24–25 | Use updated, pre-validated official curriculum references when supplied. | FR-D05 |
| §1.2, pp. 13–14 | Produce structured, explainable recommendations under defined rules and academic constraints, consistently for unchanged conditions. | FR-A07; BR-13; NFR-AC05 |
| §1.2, p. 14 | Provide prioritized curriculum revision guidance, course-related enhancements, and projected alignment effects. | FR-A11 |
| §1.2, pp. 13–14; §1.6, p. 22 | Represent proposed enhancements, project their effects, compare with the baseline, and refine scenarios. | FR-M01–M04; BR-10 |
| §1.2, p. 14; §1.7, p. 24 | Preserve academic constraints and mandated competencies through additive proposals. | FR-A07; FR-M03; BR-09; §8.1 |
| §1.3, p. 16; §1.5, p. 19 | Identify direct/logical coverage and genuine possible gaps. | FR-D03; BR-06 |
| §1.5, pp. 19–20 | Curriculum analysis and student roadmapping support the project's objectives. | FR-A01–A11; FR-T01–T08 |
| §1.7, pp. 24–25 | Use official syllabus-derived, pre-validated academic data. | FR-D01; BR-02 |
| §1.7, pp. 24–25 | Exclude General Education and informal-learning experiences from matching/scoring. | BR-03; §2.3 |
| §1.7, p. 25 | Treat selected completed coursework as competency evidence under the stated mastery assumption; do not test actual retention. | BR-04; FR-T05; §10 |
| §1.7, p. 25 | Allow controlled evaluation data while retaining the full system's ongoing collection scope. | FR-D04; §2.2 |
| §1.7, p. 25 | Do not automatically modify institutional records or enforce curriculum changes. | BR-01; FR-M04 |

## 4. User-confirmed decisions

| Decision | Effect on the specification | Requirements/sections |
| --- | --- | --- |
| U1 — Full Chapter 1 scope | Simulation and continuing industry evidence updates are required capabilities rather than deferred exclusions. The controlled study dataset remains an evaluation boundary. | FR-D02–D04; FR-M01–M04; §2.2 |
| U2 — Include official common/core computing courses | Expand eligible academic content beyond specialization subjects while keeping General Education excluded. | FR-D01; FR-T01; BR-02–BR-03; §2.2 |
| U3 — Role selection without sign-in; retain selections between visits | Provide both experiences without accounts and make previous selections available on return. | FR-SH01–SH02; BR-11 |
| U4 — External questionnaires | Do not add survey completion, survey-response collection, or research demographics to the application requirements. | §2.3; §3.1; §8.3 |
| U5 — Questionnaire-based expectations | Use qualitative quality criteria as written; do not add numerical timing, device/browser, capacity, or passing-rating requirements. | §6; §8.2–8.3 |
| U6 — Combine faculty and administrators | Treat faculty members/professors, department chairs, associate dean, and dean as members of the same Faculty/Academic Administrator system group. | §2.1; FR-SH01 |

## 5. Non-rated questionnaire content

| Source content | Treatment |
| --- | --- |
| FQ/SQ p. 1: privacy, voluntary participation, consent, research contacts, retention, and separate informed consent | External research-administration conditions, described in requirements §8.3. They do not establish an in-app survey feature. |
| FQ p. 2: academic role, reviewed track, and years of experience | Stakeholder and reviewed-track evidence. Teaching/administration experience remains a survey demographic. |
| SQ p. 2: eligibility, program, track, year level, and scoring disclaimer | Eligibility limits research respondents; program/track/year support student context; the coursework-only disclaimer supports BR-03–BR-04. Survey `Other` responses do not expand supported programs/tracks. |
| FQ p. 13 and SQ p. 11: optional feedback and validation signatures | External study feedback and instrument-validation material, not system functionality. |
| FQ/SQ response instructions: 5–1 agreement, `N/A`, and permission to leave items unanswered | External evaluation rules; no numerical passing threshold or in-app scoring workflow is specified. |

The mapping covers all 90 rated statements. It does not claim that all features have been implemented, that every respondent will rate them favorably, or that the study establishes full ISO compliance.

The broader source audit is recorded in [Requirements verification](REQUIREMENTS_VERIFICATION.md). Conversation changes and suggested locations for manual paper edits are recorded separately in [Paper change notes](PAPER_CHANGE_NOTES.md).
