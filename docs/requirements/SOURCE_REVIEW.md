# TechGap Requirements: Source Review

Status: Source evidence and decision record supporting the [System requirements](SYSTEM_REQUIREMENTS.md). The five scope questions have been answered by the user, who also requests one combined Faculty/Academic Administrator user group. Statements about what the papers specify are distinguished from those user-confirmed additions. Manual paper-edit notes are recorded separately in [Paper change notes](PAPER_CHANGE_NOTES.md).

## 1. Source documents

References use physical PDF page numbers, counted from the first page of each file.

| Reference | Document | Relevant contents |
| --- | --- | --- |
| CH1 | [Techgap Chapter 1.pdf](../paper/Techgap%20Chapter%201.pdf) | Project purpose, stakeholders, objectives, standards, scope, and limitations. Sections 1.2–1.7 appear on PDF pages 13–25. |
| FQ | [TechGap Questionnaire for Faculty.pdf](../paper/TechGap%20Questionnaire%20for%20Faculty.pdf) | Faculty/administrator evaluation: participation conditions, respondent information, 20 functionality statements, 30 general evaluation statements, and optional feedback. |
| SQ | [TechGap Questionnaire for Students.pdf](../paper/TechGap%20Questionnaire%20for%20Students.pdf) | Student evaluation: participation conditions, eligibility and respondent information, 15 functionality statements, 25 general evaluation statements, and optional feedback. |

Questionnaire codes are qualified by source. For example, `FQ-CA1` and `SQ-CA1` are different statements even though their printed codes are identical.

Existing PRDs and use-case documents are not used to fill gaps in these sources. The requirements baseline is derived from the supplied papers and the user's clarifications, rather than from implementation choices in older planning documents.

## 2. Established purpose and users

TechGap is a web-based advisory system for examining curriculum–industry alignment and supporting student career preparation within CICS at DLSU-D. Its academic programs are BS Computer Science and BS Information Technology. Final curriculum decisions remain with academic stakeholders. The system does not automatically change institutional records or enforce curriculum revisions. [CH1 §§1.2, 1.5, 1.7; PDF pp. 13–15, 19–20, 24–25]

The questionnaires identify four specialization tracks: Computer Science–Intelligent Systems, Computer Science–Game Development, Information Technology–Network Technology, and Information Technology–Web Development. Faculty, department chairs, the associate dean, and the dean are academic users. The student questionnaire limits evaluation eligibility to currently enrolled BSCS/BSIT students in CICS at DLSU-D. Evaluation eligibility does not, by itself, define a sign-in or identity-verification requirement. [FQ p. 2; SQ p. 2]

## 3. Established academic-user capabilities

| Capability supported by the source | Evidence |
| --- | --- |
| Select and identify the curriculum track being analyzed; display curriculum coverage and JobStreet skill requirements for that same track. | FQ-CA1–CA5, p. 3 |
| Distinguish covered skills from possible gaps; prioritize gaps using demand represented in the analyzed dataset. | FQ-GO1–GO2, p. 4 |
| Identify low-demand curriculum topics for further academic review and explain the gap or low-demand finding. | FQ-GO3–GO5, p. 4 |
| Present additions or enhancements connected to identified gaps and identify the related course or curriculum area. | FQ-CR1–CR5, p. 5 |
| Generate a consolidated, printable report containing alignment findings, gaps, recommendations, and selected-track information; permit retention or sharing for academic review. | FQ-GR1–GR5, p. 6 |
| Support consideration of curriculum changes, priorities, and enhancements while preserving the final judgment of academic stakeholders. | FQ-DS1–DS5, p. 12 |

Low demand in the analyzed dataset is a reason for review. It is not evidence that a topic is universally obsolete or safe to remove. Chapter 1 and the faculty questionnaire describe additive recommendations and protection of mandated competencies. [CH1 §1.7, p. 24; FQ-GO3–GO4, p. 4; FQ-CR3, p. 5]

## 4. Established student capabilities

| Capability supported by the source | Evidence |
| --- | --- |
| Select completed courses for analysis and display their relationship to the requirements of a selected career role. | SQ-CA1, CA4–CA5, p. 3 |
| Distinguish skills represented by selected courses from identified gaps; identify future curriculum coverage in courses not yet completed. | SQ-CA2–CA3, p. 3 |
| Display ranked career suggestions related to selected coursework, support comparison of their skill requirements, and permit selection of another available career role. | SQ-CP1–CP5, p. 4 |
| Provide a roadmap that addresses gaps for the selected role, orders the learning steps, identifies the skill at each step, and links to resources that the student can open. | SQ-UG1–UG5, p. 5 |
| Reflect the student's selected program, year level, and courses in the displayed results. | SQ-FA1, p. 6 |

The student score represents skills associated with official coursework. Chapter 1 explicitly uses the assumption that passing a course represents full mastery, while also excluding assessments of actual retained knowledge. The documentation must disclose that modeling assumption rather than describe the result as verified proficiency. Informal learning, internships, seminars, on-the-job training, external certifications, and extracurricular activities do not contribute to the score. Linked external learning resources are guidance, not additional scoring evidence. [CH1 §1.7, pp. 24–25; SQ p. 2]

## 5. Quality expectations established by the questionnaires

| Area | Observable expectation | Evidence |
| --- | --- | --- |
| Functional accuracy | Results reflect selections; scores, classifications, explanations, and summaries agree; results update after relevant selections change. | FQ-FA1–FA5, p. 7; SQ-FA1–FA5, p. 6 |
| Performance efficiency | Selection responses, suggestions, analysis results, reports, and roadmaps become available within an acceptable time without excessive delays. No numerical time limits are supplied. | FQ-PE1–PE5, p. 8; SQ-PE1–PE5, p. 7 |
| Reliability | Evaluation activities remain operational, repeated analyses complete, selections persist between related views, report/roadmap operations complete, and failed operations can be retried. The questionnaires do not specify between-visit retention; the user separately requires it. | FQ-RE1–RE5, p. 9; SQ-RE1–RE5, p. 8; U3 |
| Usability | Instructions, feature organization, terminology, visual results, and navigation are understandable. | FQ-US1–US5, p. 10; SQ-US1–US5, p. 9 |
| Perceived usefulness | Academic users can use findings for review and documentation; students can understand role requirements, recognize coursework limits, choose independent learning areas, find resources, and plan career preparation. | FQ-PU1–PU5, p. 11; SQ-PU1–PU5, p. 10 |

The questionnaires adapt selected ISO/IEC 25010 quality criteria. They explicitly do not evaluate every characteristic or establish full ISO compliance. Perceived usefulness and faculty decision-making support are additional study criteria. The sources do not specify the ISO edition or a minimum passing evaluation rating. The user directs this specification to use the questionnaire's expectations without adding numerical targets or broader operational commitments. Perceived functional accuracy ratings do not establish measured skill-extraction accuracy: respondents are not expected to verify individual job postings. [FQ pp. 1, 7; SQ pp. 1, 6; U5]

## 6. Data and evaluation boundaries established by Chapter 1

- The academic reference consists of official syllabus PDFs parsed into pre-validated structured data. General Education courses are excluded from skill matching. Section 1.7 describes specialization-track subjects; the user explicitly expands the system's eligible academic content to include official common/core computing subjects. [CH1 §1.7, pp. 24–25; U2]
- Industry requirements come from computing-related Philippine JobStreet postings. Chapter 1 describes approximately 5,000 postings, not an exact guaranteed minimum or a maximum. [CH1 §§1.5, 1.7, pp. 19, 24]
- The evaluation uses a controlled, processed dataset. Expanded collection and continuous scraping are described as subsequent work in Thesis 2. The user requests the full Chapter 1 system, so continuing acquisition and updates are required capabilities while the controlled dataset remains a study-evaluation boundary. Findings may be incomplete because of the data boundary. [CH1 §1.7, p. 25; U1]
- Chapter 1 describes curriculum-change simulation and projected improvements in its purpose and significance sections, but the questionnaires do not evaluate a simulation activity. The user's full-scope decision includes this capability in the system requirements. [CH1 §1.2, pp. 13–14; §1.6, p. 22; U1]
- Chapter 1 references CHED CMO No. 25, Series of 2015, preserving mandated competencies and minimum academic requirements. These papers do not supply enough detail to establish specific unit floors, protected course lists, or a complete compliance checklist. [CH1 §1.1, pp. 8–12; §1.2, p. 14; §1.7, p. 24]

## 7. Research-participation conditions

Both questionnaires state voluntary participation, permission to skip items or stop before submission, and confidential handling by the research team. They request limited respondent demographics, ratings, and optional comments, without names or student numbers. They state thesis-period retention and reference the Data Privacy Act of 2012 and the research protocol. Their privacy statement accompanies a separate informed-consent document. These conditions apply to research responses; they do not establish how normal system usage data must be collected or retained. [FQ pp. 1–2, 13; SQ pp. 1–2, 11]

Ratings use 5–1 agreement responses, with `N/A` for insufficient evidence or unexamined features; an item may also be unanswered. The questionnaires do not define an aggregation method or a numerical acceptance threshold. The user confirms that questionnaires are administered outside TechGap, so survey completion and response storage are outside the application requirements. [FQ pp. 3–12; SQ pp. 3–10; U4]

## 8. Resolved scope decisions

| Reference | User's decision | Requirements effect |
| --- | --- | --- |
| U1 | Full Chapter 1 scope. | Include simulation and continuing job-market acquisition and updates. Preserve the controlled-dataset research boundary without making it the full system's permanent limitation. |
| U2 | Also include official common/core computing courses. | Expand academic evidence beyond specialization subjects; General Education remains excluded. |
| U3 | Choose a role without sign-in and retain selections between visits. | Require role selection, no sign-in, and retention of relevant selections across visits. |
| U4 | Questionnaires outside TechGap. | Keep research survey administration and response collection outside the application. |
| U5 | Base expectations on the questionnaires; additional numerical operational targets are outside this specification request. | State qualitative accuracy, efficiency, reliability, usability, and usefulness expectations without inventing timing limits, capacity commitments, or passing ratings. |
| U6 | Combine faculty members/professors, department chair, associate dean, and dean as system users. | List Student and Faculty/Academic Administrator as the two user groups; retain academic titles as members of the latter group. |

## 9. Alignment notes for related documents

The following differences should be respected when reading older project plans alongside this requirements baseline:

- Chapter 1 §1.7's specialization-only academic reference must be read with U2's explicit addition of official common/core computing courses. The paper's scope wording should be aligned with this confirmed expansion when revised.
- A v1 plan that defers simulation or ongoing industry-data acquisition does not cover U1's full requested system scope. Controlled research evaluation and the complete system's capabilities are separate boundaries.
- Replacement or removal recommendations in older plans conflict with the supplied faculty questionnaire and Chapter 1's additive, mandated-competency-preserving boundary.
- Supplementary job sources, exact suggestion counts, scoring formulas, numerical cutoffs, protected-course identifiers, and numerical unit floors in older plans are not adopted as requirements merely because they appear there. The present source documents do not establish those details.
- Between-visit selection retention is a user-confirmed requirement. Survey eligibility, demographic questions, feedback, and consent do not create sign-in or in-app survey requirements.

The existing PRDs, use cases, and technical documents are unchanged. This source-based requirements set states the requested system behavior without choosing implementation technologies.

The subsequent completeness recheck made three existing Chapter 1 expectations explicit in the requirements: use of updated official curriculum references, consistent recommendations under unchanged evidence and rules, and prioritized revision guidance with projected alignment effects. These are source-coverage corrections, not new conversation changes to the paper. See [Requirements verification](REQUIREMENTS_VERIFICATION.md).
