# TechGap: Conversation Decisions and Manual Paper-Edit Notes

Purpose: Keep a separate record of decisions made in this conversation that change, extend, or clarify the supplied papers. The PDFs have not been edited. Suggested wording below is for the authors to review and insert manually where appropriate.

Sources: [Chapter 1](../paper/Techgap%20Chapter%201.pdf), [Faculty questionnaire](../paper/TechGap%20Questionnaire%20for%20Faculty.pdf), and [Student questionnaire](../paper/TechGap%20Questionnaire%20for%20Students.pdf). Page numbers are physical PDF page numbers.

## 1. Changes or additions to record in the paper

| ID | Conversation decision | Relationship to the current papers | Manual-edit locations |
| --- | --- | --- | --- |
| PC-01 | Include official common/core computing courses as well as specialization-track subjects. [U2] | **Explicit scope expansion:** Chapter 1 §1.7, p. 24 describes specialization-track syllabus subjects. The questionnaires refer more generally to CICS coursework and do not explicitly exclude common/core computing subjects. | Revise Chapter 1 §1.7's academic reference and any other descriptions of the analyzed course set. Clarify coursework scope in the questionnaires' evaluation instructions if needed. |
| PC-02 | Users choose Student or Faculty/Academic Administrator without sign-in. [U3] | **Additional access requirement:** Neither Chapter 1 nor the questionnaires specifies this entry behavior or an authentication requirement. | State the two role-based experiences and access boundary in Chapter 1 §1.2 and/or §1.7. Distinguish intended CICS users from verified identity. |
| PC-03 | Retain users' selections between visits. [U3] | **Extended retention requirement:** FQ-RE3, p. 9 and SQ-RE3, p. 8 require retention while navigating related views. They do not assess returning on a later visit. | Add the between-visit behavior to Chapter 1's system description/scope. Consider adding a separate reliability item if the study should evaluate it. Keep survey-response retention separate from application-selection retention. |

### PC-01: Academic content expansion

Suggested Chapter 1 scope wording:

> The academic reference includes official syllabi for CICS specialization-track subjects and applicable common/core computing courses in the BS Computer Science and BS Information Technology programs. General Education courses remain excluded from skill matching. Student alignment uses competencies represented by the official courses selected as completed.

This changes the eligible course set, not the four specialization tracks, institution, program scope, informal-learning exclusions, or coursework-only scoring rule.

The current questionnaires' generic references to curriculum content and selected CICS courses can accommodate this expansion. A new functionality category is not necessary solely because common/core courses are included. If the scope is stated in respondent instructions, ensure those instructions describe the expanded eligible course set.

### PC-02: Role selection without sign-in

Suggested system-description wording:

> TechGap provides Student and Faculty/Academic Administrator experiences. Users select an experience without signing in. Role selection determines the activities presented and does not verify identity or confer institutional authority.

The questionnaires' eligibility statements still define the research respondents. They do not become an application identity-verification procedure. Faculty/administrator titles can remain separate demographic answers even though the users share one system experience.

### PC-03: Retaining selections between visits

Suggested system-description wording:

> TechGap retains the selected role and relevant academic and career selections while users navigate related results and when they return on a later visit.

If this extended behavior is to be rated, suggested additional external questionnaire wording is:

| Instrument | Suggested new statement |
| --- | --- |
| Faculty/administrator | When I return to TechGap on a later visit, my previously selected curriculum track remains available. |
| Student | When I return to TechGap on a later visit, my previous academic and career selections remain available. |

These are proposed additions, not items currently in the questionnaires. If added, the authors must update instrument numbering, coverage tables, and the required evaluation activities. The current instruments still contain 50 faculty items and 40 student items.

## 2. Clarifications that do not contradict the papers

These decisions are included so that every conversation clarification is accounted for. They should not be mislabeled as new capabilities missing from Chapter 1.

| ID | Decision | Existing source position | Suggested manual treatment |
| --- | --- | --- | --- |
| PC-04 | Cover the full Chapter 1 system, including simulation and continuing job-market updates. [U1] | Chapter 1 §1.2, pp. 13–14 and §1.6, p. 22 already describe simulation and ongoing evaluation. Section 1.7, p. 25 describes a controlled evaluation dataset and expanded collection in Thesis 2. The questionnaires evaluate processed-dataset findings and do not contain a dedicated simulation section. | Clarify the distinction between full system capabilities and the controlled research evaluation. This decision does not, by itself, change the study schedule or require the existing survey to rate every broader capability. |
| PC-05 | Administer questionnaires outside TechGap. [U4] | The supplied instruments describe research participation and response handling but do not specify an in-app survey feature. | State external administration in the study procedure or system boundary if its location could otherwise be ambiguous. Do not add survey collection to the application description. |
| PC-06 | Use questionnaire-based qualitative quality expectations without adding numerical operational targets. [U5] | The questionnaires use acceptable timing, reliability, usability, consistency, and usefulness judgments. Their first pages explicitly limit ISO assertions to selected adapted criteria. They supply no numerical timing limit or minimum passing rating. | Preserve these qualitative expectations. If Chapter 1's general ISO wording is revised, clarify that the study uses selected ISO-informed criteria plus study-specific usefulness and decision-support criteria, rather than claiming full compliance. |
| PC-07 | Combine faculty members/professors, department chairs, associate dean, and dean into one Faculty/Academic Administrator system user group. [U6] | Chapter 1 §1.6, pp. 21–22 already groups CICS faculty and academic administrators. The faculty questionnaire addresses these users jointly and distinguishes titles only in its demographic question on p. 2. | Use two system user groups consistently: Student and Faculty/Academic Administrator. No change to the current questionnaire's academic-title demographic choices is required. The earlier three-row requirements user table has been corrected. |

Suggested clarification for PC-04:

> The full TechGap scope includes continuing integration of academic and job-market evidence and simulation of proposed curriculum enhancements. Research evaluation uses a controlled, processed dataset so its findings can be examined consistently. Controlled evaluation findings refer to the dataset used; later acquisition and updates remain part of the full system scope.

Suggested clarification for PC-05:

> The evaluation questionnaires are administered separately from TechGap. The application provides the activities and outputs being evaluated and does not collect questionnaire responses or research consent.

Suggested clarification for PC-06:

> Software-quality evaluation uses the selected ISO-informed criteria adapted in the questionnaires. Perceived usefulness and academic decision-making support are additional study-specific criteria. The evaluation does not establish full ISO compliance.

Suggested user-group wording for PC-07:

> TechGap serves two system user groups: CICS BSCS/BSIT students and Faculty/Academic Administrators. The latter includes faculty members/professors, department chairs, the associate dean, and the dean, who share the academic review experience. Final curriculum adoption remains subject to institutional authority and judgment.

## 3. Source-coverage corrections, not paper changes

The completeness recheck made the following existing Chapter 1 expectations explicit in the requirements. They are not new conversation additions or reasons to change the original paper:

| Existing expectation | Source | Requirements made explicit |
| --- | --- | --- |
| Updated official curriculum references can inform subsequent analysis. | Chapter 1 §1.2, p. 13; §1.7, pp. 24–25 | FR-D05 |
| Structured, explainable recommendations follow defined rules and academic constraints and are consistent under unchanged conditions. | Chapter 1 §1.2, pp. 13–14 | BR-13; FR-A07 |
| Revision guidance includes prioritized enhancements, course-level changes, and projected alignment improvements. | Chapter 1 §1.2, p. 14 | FR-A11 |

The source-based advisory rule, additive recommendations, General Education exclusion, informal-learning exclusion, passing-course mastery assumption, and distinction between current and future curriculum coverage remain unchanged. The user-group consolidation also does not transfer formal decision authority between academic titles.

## 4. Manual-edit checklist

- [ ] Update Chapter 1's specialization-only course reference to include eligible common/core computing courses. [PC-01]
- [ ] Record role selection without sign-in as the access model. [PC-02]
- [ ] Record retention of selections between visits. [PC-03]
- [ ] Decide whether the external questionnaires should explicitly rate between-visit retention; if so, update the instruments and their evaluation activities. [PC-03]
- [ ] Check that full system scope and controlled study evaluation are clearly distinguished, while preserving the stated research timeline. [PC-04]
- [ ] State external questionnaire administration wherever needed to clarify the application/research boundary. [PC-05]
- [ ] Keep ISO-related claims aligned with the questionnaires' selected-criteria limitation. [PC-06]
- [ ] Use Student and Faculty/Academic Administrator as the two system user groups, while retaining relevant academic-title demographics. [PC-07]

This checklist records author actions to consider. It does not mark the PDFs as already revised or presume that an optional new questionnaire item has been adopted.
