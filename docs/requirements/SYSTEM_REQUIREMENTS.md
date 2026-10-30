# TechGap System Requirements Specification

Status: Requirements baseline derived from the supplied sources and the user's scope clarifications. It defines expected system behavior, not an implementation design or a claim that the system has already been built or evaluated.

## 1. Purpose and authority

TechGap is a web-based decision-support system for the College of Information and Computer Studies (CICS) at De La Salle University–Dasmariñas (DLSU-D). It compares competencies represented in official computing courses with skills required by computing-related Philippine job postings. It supports academic curriculum review and students' preparation for selected career roles. [CH1 §§1.1–1.3, 1.5–1.7]

The required outputs and user-observable quality expectations come primarily from the faculty and student questionnaires. Chapter 1 establishes the project purpose, advisory role, academic constraints, and broader capabilities. The user's clarifications resolve delivery scope, course inclusion, access, persistence, and questionnaire administration.

| Reference | Meaning |
| --- | --- |
| CH1 | [Techgap Chapter 1.pdf](../paper/Techgap%20Chapter%201.pdf). References identify chapter sections and physical PDF pages where needed. |
| FQ | [Faculty questionnaire](../paper/TechGap%20Questionnaire%20for%20Faculty.pdf). Item codes are prefixed with `FQ-`. |
| SQ | [Student questionnaire](../paper/TechGap%20Questionnaire%20for%20Students.pdf). Item codes are prefixed with `SQ-`. |
| U1 | User confirmation: full Chapter 1 scope, including simulation and continuous job-market updates. |
| U2 | User confirmation: also include official common/core computing courses. |
| U3 | User confirmation: choose a role without sign-in and retain selections between visits. |
| U4 | User confirmation: questionnaires are completed outside TechGap. |
| U5 | User direction: base quality expectations on the questionnaires; do not add numerical operational targets. |
| U6 | User direction: combine faculty members/professors, department chairs, associate dean, and dean into one Faculty/Academic Administrator user group. |

Requirements use `shall` to identify required behavior. Acceptance checks describe observable evidence of that behavior. Questionnaire ratings assess users' experience of the system; they are not proof of universal analytical accuracy or full standards compliance.

## 2. Users and system boundaries

### 2.1 Users

| User | Expected activity |
| --- | --- |
| CICS BSCS/BSIT student | Select academic context and completed courses, compare career options, assess coursework-to-career alignment, identify gaps and future coverage, and follow learning guidance. |
| Faculty/Academic Administrator — faculty member/professor, department chair, associate dean, or dean | Review track-level curriculum alignment, gaps, low-demand topics, recommendations, and academic reports; examine proposed enhancements and their projected effects; exercise academic judgment through the same shared experience. |

There are two system user groups: Student and Faculty/Academic Administrator. Faculty and administrative titles are members of the same system group, not separate system roles. Academic authority over formal adoption remains an institutional matter; grouping the users does not change that authority. The sources do not require separate signed-in accounts or distinct permission levels. Industry partners, employers, the university, and other researchers are beneficiaries described in Chapter 1, without separately specified system experiences. [FQ p. 2; SQ p. 2; CH1 §1.6; U3, U6]

### 2.2 Included scope

The system shall support BS Computer Science and BS Information Technology within CICS at DLSU-D, including the following tracks:

| Program | Specialization tracks |
| --- | --- |
| BS Computer Science | Intelligent Systems; Game Development |
| BS Information Technology | Network Technology; Web Development |

The analyzed academic content shall include official specialization-track subjects and official common/core computing courses applicable to the selected program and track. The inclusion of common/core courses is the user's explicit expansion of the narrower specialization-subject wording in Chapter 1 §1.7. [FQ p. 2; SQ p. 2; CH1 §1.7; U2]

The full required scope includes curriculum and job-skill analysis, academic dashboards and reports, additive curriculum recommendations, simulation of proposed curriculum enhancements, continuing job-market acquisition and updates, and student career guidance. A controlled processed dataset remains appropriate for the research evaluation described in Chapter 1; it does not limit the full system to a permanently fixed dataset. [CH1 §§1.2, 1.5, 1.7; U1]

### 2.3 Exclusions and limits

- Other colleges, institutions, and degree programs are outside the defined academic scope.
- General Education courses are excluded from skill matching.
- Internships, seminars, on-the-job training, external certifications, extracurricular activities, and other informal learning do not contribute to the student's alignment score.
- The system does not test actual student mastery or retained knowledge, or guarantee employment or professional readiness.
- Recommendations and simulated scenarios do not modify institutional records or enact curriculum changes.
- Sign-in, account registration, and verified academic identity are not part of the confirmed access model.
- Questionnaire completion, consent collection for the survey, respondent demographics, survey responses, and research-response analysis are outside TechGap.

[CH1 §1.7; SQ p. 2; FQ/SQ p. 1; U3–U4]

## 3. Required information and outputs

### 3.1 Information used by the system

| Information | Required content and boundary |
| --- | --- |
| Official academic reference | Applicable program and track; course identity and title; documented learning outcomes and technical topics/competencies, derived from official syllabi and pre-validated before analysis. Common/core courses are included where applicable. |
| Academic constraint reference | CHED CMO No. 25, s. 2015 minimums for the selected program: program outcomes, minimum units, common courses and required knowledge areas. A fixed reference; institutional constraints are not stored. |
| Job-market reference | Computing-related Philippine JobStreet postings, associated career roles, technical skill requirements, and the demand information used in the analysis. Chapter 1's approximately 5,000 postings describes its study dataset, not an exact contractual minimum or maximum. |
| Student selections | Program, applicable specialization track, year level, completed official courses selected for inclusion, and target career role. No name or student number is required for this experience. |
| Academic-user selections | Selected curriculum track; proposed additions or enhancements when using simulation. |
| Learning-resource reference | Resources associated with the skills in the student's roadmap, with links the student can open. |

[CH1 §§1.2, 1.5, 1.7; FQ-CA1–CA5, CR1–CR5; SQ-CA1–CA5, CP1–CP5, UG1–UG5; U2–U3]

Research-demographic questions do not automatically become system input requirements. For example, teaching experience, survey eligibility responses, and optional comments belong to the external questionnaires. The four supported tracks remain the system boundary even though the student survey provides an `Other` demographic response. [FQ/SQ p. 2; U4]

### 3.2 Required outputs

| Output | Minimum expected content |
| --- | --- |
| Academic alignment dashboard | Selected track; alignment summary and score; curriculum coverage and skill classifications connected to course content; industry skill requirements for the same track. |
| Gap and low-demand topic report | Covered skills and possible gaps; demand-related gap priorities; low-demand curriculum topics; selected-track context; explanations for the findings. |
| Curriculum recommendations | Proposed additions or enhancements; identified gap; related course or curriculum area; explanation connecting the proposal to the finding; preservation of academic constraints. |
| Curriculum revision guidance | Prioritized enhancements and course-level changes; their projected effects on alignment; explanations and academic constraints; clear separation of current findings from projected improvements. This guidance may be included in the academic review report. |
| Academic review report | Selected track; consolidated alignment findings, gap findings and priorities, and curriculum recommendations; summarized explanations suitable for academic discussion; printable, shareable by URL. |
| Curriculum simulation | Existing curriculum baseline; proposed enhancements; projected effects on alignment; a clear distinction between current findings and projected outcomes. |
| Career-role suggestions | Ranked roles related to selected coursework; role skill requirements that support comparison; another available role as an alternative analysis target; identification of the selected role. |
| Personal alignment results | Selected academic context and completed-course basis; selected career role; alignment score; covered skills and gaps; future curriculum coverage; explanations consistent with those results. |
| Upskilling roadmap | Gaps for the selected career role; an ordered series of learning steps; the skill to study at each step; relevant linked learning resources that can be opened. |

[FQ Part I; SQ Part I; CH1 §1.2]

No requirement is made for a particular number of career suggestions, named dashboard scoring formulas, exact skill-classification thresholds, fixed resource counts, or a specific report-file format. These are not established by the supplied questionnaires.

## 4. Business and interpretation rules

| ID | Required rule | Basis |
| --- | --- | --- |
| BR-01 | TechGap's outputs shall remain advisory. Final curriculum judgments and adoption decisions belong to academic stakeholders. | CH1 §§1.1, 1.7; FQ-DS5 |
| BR-02 | Academic analysis shall use official, pre-validated syllabus-derived content for eligible specialization and common/core computing courses. | CH1 §1.7; U2 |
| BR-03 | General Education and the excluded informal-learning experiences shall not contribute to skill matching or personal alignment scoring. | CH1 §1.7; SQ p. 2 |
| BR-04 | A selected completed/passed course represents its documented competencies for the analysis, under Chapter 1's stated full-mastery modeling assumption. The system shall explain that this is coursework-based evidence, not a proficiency test. | CH1 §1.7; SQ p. 2 |
| BR-05 | Future Curriculum Coverage shall identify relevant competencies in applicable official courses not yet completed. It shall remain distinguishable from competencies represented by selected completed courses and shall not be counted as coverage supplied by those completed courses. | SQ-CA3; CH1 §1.7; BR-04 |
| BR-06 | Logically covered skills shall be recognized through justified relationships to represented competencies rather than reported automatically as missing because of different wording. Their treatment shall have an explanation connected to the academic evidence. | CH1 §§1.3, 1.5; FQ-GO1, GO4 |
| BR-07 | Gap priorities and low-demand findings shall be grounded in the analyzed job dataset. Findings shall not be represented as an exhaustive account of the whole job market. | FQ-GO2–GO4; CH1 §1.7 |
| BR-08 | Low demand is a reason for academic review. It shall not automatically establish that a topic is obsolete, authorize its removal, or override mandated coverage. | FQ-GO3–GO4; CH1 §1.7 |
| BR-09 | Curriculum recommendations and simulated enhancements shall be additive and preserve mandated competencies, core-course obligations, and applicable minimum academic requirements. Each recommendation shall name the CMO 25 knowledge area it falls under. Removal of coursework shall not be recommended. | FQ-CR3; CH1 §§1.2, 1.7 |
| BR-10 | Simulated improvements shall be presented as projected outcomes, distinct from current curriculum findings and from adopted institutional changes. | CH1 §§1.2, 1.6–1.7 |
| BR-11 | Role selection shall determine the experience shown; it shall not be described as authenticated identity or verified academic authority. | U3 |
| BR-12 | Relevant changes in selections shall be reflected in all related results. Previously selected context shall not be presented as if it belongs to the new analysis. | FQ-FA1, FA4; SQ-FA1, FA4; FQ/SQ-FA5 |
| BR-13 | Recommendations shall follow defined rules and academic constraints. When evidence, selections, proposed changes, and those rules remain unchanged, the recommendations shall be consistent across repeated evaluations. | CH1 §1.2, pp. 13–14 |

## 5. Functional requirements

### 5.1 Shared access and selections

| ID | Requirement | Basis |
| --- | --- | --- |
| FR-SH01 | The system shall allow the user to choose Student or Faculty/Academic Administrator and enter the corresponding experience without sign-in. | U3 |
| FR-SH02 | The system shall retain the user's selections between related views and between visits, and make those retained selections available when the user returns. This includes the selected role and the academic or career selections relevant to that experience. | U3; FQ/SQ-RE3 |
| FR-SH03 | The system shall allow relevant selections to be changed and display results that correspond to the changed analysis context. | FQ-FA4; SQ-FA4 |

Retention is a requirement on selections. It does not introduce verified identities, cross-device accounts, or tracking of learning completion.

### 5.2 Academic and industry evidence

| ID | Requirement | Basis |
| --- | --- | --- |
| FR-D01 | The system shall use official, pre-validated syllabus-derived learning outcomes and technical topics to identify the competencies represented by eligible courses. | CH1 §§1.1, 1.5, 1.7; U2 |
| FR-D02 | The system shall acquire and continue updating computing-related Philippine JobStreet data, identify role skill requirements and demand information, and use updated evidence in subsequent analysis. | CH1 §§1.2, 1.5, 1.7; U1 |
| FR-D03 | The system shall compare curriculum competencies with relevant industry requirements and distinguish direct coverage, justified logical coverage, and possible gaps. | CH1 §§1.3, 1.5 |
| FR-D04 | The system shall support analysis against the controlled processed dataset used for research evaluation, with findings interpreted in relation to the dataset used. Ongoing collection shall not make controlled evaluation findings appear to describe an unspecified live market. | CH1 §1.7; FQ-CA1, GO2–GO3; U1 |
| FR-D05 | The system shall support subsequent analysis using revised official curriculum references when updated, pre-validated syllabus-derived content is supplied. This does not require a user-facing syllabus upload activity. | CH1 §1.2, p. 13; §1.7, pp. 24–25 |

### 5.3 Faculty and academic administrators

| ID | Requirement | Basis |
| --- | --- | --- |
| FR-A01 | The system shall allow selection of a supported curriculum track and clearly identify that track throughout its related analysis and reports. | FQ-CA4; FQ-GO5; FQ-GR4 |
| FR-A02 | The system shall display curriculum coverage connected to the selected track's course content and skill classifications. | FQ-CA2 |
| FR-A03 | The system shall present an alignment summary and score alongside the industry skill requirements associated with the same selected track. | FQ-CA1, CA3, CA5; FQ-FA3 |
| FR-A04 | The system shall present covered skills and possible missing competencies and explain the evidence supporting their classification. | FQ-GO1, GO4; CH1 §1.3 |
| FR-A05 | The system shall present identified gaps in a priority order related to demand in the analyzed dataset. | FQ-GO2 |
| FR-A06 | The system shall identify low-demand curriculum topics for the selected track, relate them to curriculum content, and explain why they warrant further review. They shall be listed for review, and marked CHED-mandated where they fall in a required knowledge area. | FQ-GO3–GO5 |
| FR-A07 | The system shall recommend additions or enhancements that address identified gaps, identify the related course or curriculum area, explain the relationship to the finding, and apply BR-09 and BR-13. | FQ-CR1–CR4; CH1 §§1.2, 1.7 |
| FR-A08 | The system shall allow identified gaps and their proposed enhancements to be reviewed together. | FQ-CR5 |
| FR-A09 | The system shall generate a consolidated academic report containing the selected track, alignment findings, gaps and priorities, curriculum recommendations, and summarized findings suitable for academic review. The report shall state that recommendations are additive and checked against CMO 25, and that institutional constraints remain for faculty to verify. | FQ-GR1, GR2, GR4 |
| FR-A10 | The system shall provide the academic report as a printable page that can be shared by URL and reproduces the same content for the same data release. | FQ-GR3, GR5 |
| FR-A11 | The system shall provide curriculum revision guidance that prioritizes proposed enhancements, identifies their target courses or curriculum areas, and presents their projected alignment effects separately from current findings. This guidance may be included in the consolidated academic report. | CH1 §1.2, p. 14 |

### 5.4 Curriculum-change simulation

These capabilities are required by Chapter 1 and U1 even though neither questionnaire contains a dedicated simulation rating section.

| ID | Requirement | Basis |
| --- | --- | --- |
| FR-M01 | The system shall allow academic users to represent proposed curriculum additions or enhancements for a selected track before formal adoption. | CH1 §1.2, pp. 13–14; U1 |
| FR-M02 | The system shall project the effect of the proposed enhancements on curriculum–industry alignment and permit comparison with the current curriculum baseline. | CH1 §1.2, pp. 13–14; §1.6, p. 22 |
| FR-M03 | The system shall support revising a proposed scenario and examining its projected effects again, while applying the academic constraints in BR-09. | CH1 §1.2, pp. 13–14 |
| FR-M04 | The system shall identify simulated results as projections and keep scenario evaluation distinct from adoption or modification of official institutional records. | CH1 §§1.2, 1.7; BR-01, BR-10 |

### 5.5 Students

| ID | Requirement | Basis |
| --- | --- | --- |
| FR-T01 | The system shall allow the student to select program, applicable specialization track, year level, and completed official courses to include in analysis. Eligible common/core computing courses shall also be available. | SQ p. 2; SQ-CA4, FA1; U2 |
| FR-T02 | The system shall present ranked career-role suggestions related to the learning represented by the selected completed courses. | SQ-CP1, CP4 |
| FR-T03 | The system shall display the skill requirements of available career options so the student can compare them. | SQ-CP2 |
| FR-T04 | The system shall allow the student to select a suggested role or another available career role for analysis, and clearly identify the selected target. | SQ-CP3, CP5 |
| FR-T05 | The system shall display an alignment score and explain how the selected completed courses relate to the selected role's skill requirements, subject to BR-03–BR-05. | SQ-CA1, CA5; CH1 §1.7 |
| FR-T06 | The system shall distinguish skills represented by the selected completed courses from possible gaps and identify relevant future coverage in applicable official courses not yet completed. | SQ-CA2–CA3 |
| FR-T07 | The system shall provide a roadmap addressing identified gaps for the selected career role, with a clear learning order and an individual skill identified at each step. | SQ-UG1, UG2, UG4 |
| FR-T08 | The system shall associate relevant learning resources with roadmap skills and allow the student to open the linked resources. | SQ-UG3, UG5 |

## 6. Non-functional requirements

These requirements preserve the questionnaire's qualitative expectations. No numerical timing limits, availability percentages, capacity targets, device/browser matrix, or minimum survey score are added. [U5]

### 6.1 Functional accuracy

| ID | Requirement | Basis |
| --- | --- | --- |
| NFR-AC01 | Results shall reflect the selected track for academic users and the selected program, year level, and courses for students. | FQ/SQ-FA1 |
| NFR-AC02 | Coverage summaries and possible gap classifications shall be consistent with one another. | FQ/SQ-FA2 |
| NFR-AC03 | Alignment scores shall be consistent with the coverage information presented for that analysis. | FQ/SQ-FA3 |
| NFR-AC04 | Results shall update to reflect relevant selection changes. | FQ/SQ-FA4 |
| NFR-AC05 | Explanations shall correspond to the actual displayed results. | FQ/SQ-FA5 |

### 6.2 Performance efficiency

| ID | Requirement | Basis |
| --- | --- | --- |
| NFR-PE01 | Curriculum-track and student-input selections shall receive a response within a time acceptable to the evaluator. | FQ/SQ-PE1 |
| NFR-PE02 | The academic alignment dashboard and student career suggestions shall become available within an acceptable time after the relevant selections. | FQ/SQ-PE2 |
| NFR-PE03 | Academic gap results and student alignment results shall become available within an acceptable time. | FQ/SQ-PE3 |
| NFR-PE04 | Academic report generation and student roadmap availability shall complete within an acceptable time. | FQ/SQ-PE4 |
| NFR-PE05 | Users shall be able to complete the evaluation activities without excessive processing delays. | FQ/SQ-PE5 |

Acceptability is assessed through the external questionnaires using respondents' experience. This document does not convert that expectation into an invented number of seconds.

### 6.3 Reliability

| ID | Requirement | Basis |
| --- | --- | --- |
| NFR-RE01 | The system shall remain operational throughout the evaluation activities performed by users. | FQ/SQ-RE1 |
| NFR-RE02 | Repeating analysis for the same academic track and dataset, or the same student course selections and career role, shall complete without failure. | FQ/SQ-RE2 |
| NFR-RE03 | Selected information shall be retained while navigating between related views. Between-visit retention is additionally required by FR-SH02. | FQ/SQ-RE3; U3 |
| NFR-RE04 | Academic report generation and student roadmap loading shall complete without a system crash or unexpected interruption. | FQ/SQ-RE4 |
| NFR-RE05 | If an operation fails, the user shall be able to retry it and continue using the system. | FQ/SQ-RE5 |

### 6.4 Usability

| ID | Requirement | Basis |
| --- | --- | --- |
| NFR-US01 | Instructions shall clearly explain how to perform the relevant activities. | FQ/SQ-US1 |
| NFR-US02 | Interface organization shall make required features easy to locate. | FQ/SQ-US2 |
| NFR-US03 | System terminology shall be understandable to the intended users. | FQ/SQ-US3 |
| NFR-US04 | Visual presentation shall make analysis findings easy to interpret. | FQ/SQ-US4 |
| NFR-US05 | Navigation shall allow movement between related results without confusion. | FQ/SQ-US5 |

## 7. Expected usefulness and decision-support outcomes

These are study-specific user outcomes, separate from the selected ISO-informed quality criteria. The listed capabilities shall provide a basis for users to assess each outcome; a favorable rating is not assumed.

| ID | Expected outcome | Basis |
| --- | --- | --- |
| OUT-A01 | Academic users can consolidate analysis findings for curriculum review. | FQ-PU1 |
| OUT-A02 | Academic users can identify topics that warrant further examination. | FQ-PU2 |
| OUT-A03 | Academic users can recognize industry requirements needing additional curriculum coverage. | FQ-PU3 |
| OUT-A04 | Academic users can present alignment findings during curriculum discussions. | FQ-PU4 |
| OUT-A05 | Academic users can prepare documentation for academic review. | FQ-PU5 |
| OUT-T01 | Students can understand the technical skills required by a selected career role. | SQ-PU1 |
| OUT-T02 | Students can recognize the limits of the skills represented by completed courses. | SQ-PU2 |
| OUT-T03 | Students can identify areas requiring independent learning. | SQ-PU3 |
| OUT-T04 | Students can identify relevant learning resources. | SQ-PU4 |
| OUT-T05 | Students can plan further preparation for a preferred career pathway. | SQ-PU5 |
| OUT-D01 | Academic users can consider whether curriculum revisions are necessary. | FQ-DS1 |
| OUT-D02 | Academic users can use gap priorities to select areas for further review. | FQ-DS2 |
| OUT-D03 | Academic users can use recommendations as a basis for possible enhancements. | FQ-DS3 |
| OUT-D04 | Academic users can consider proposed enhancements in relation to the explanations and findings. | FQ-DS4 |
| OUT-D05 | Academic users retain final judgment while receiving advisory information. | FQ-DS5 |

## 8. Standards and evaluation boundaries

### 8.1 Academic standards

Chapter 1 identifies CHED CMO No. 25, Series of 2015 as the academic standards reference for the programs. TechGap's recommendations and simulations shall preserve applicable national and institutional academic requirements, including mandated competencies, core courses, and minimum academic requirements. This is the standards obligation specified by the supplied paper. [CH1 §1.1, pp. 8–12; §1.2, p. 14; §1.7, p. 24]

### 8.2 Software quality assessment

Both questionnaires adapt selected ISO/IEC 25010 product-quality criteria. The requirements cover the questionnaire's functional accuracy, performance efficiency, reliability, and usability expectations. Perceived usefulness and academic decision-making support are additional study-specific criteria. The instruments expressly do not assess every ISO characteristic or establish full ISO compliance. This specification preserves that distinction without adding an edition requirement or broader certification claim. [FQ/SQ p. 1; CH1 §§1.5–1.7; U5]

### 8.3 External research administration

The questionnaires shall remain external evaluation instruments. Their stated participation conditions include voluntary consent, permission to skip items or stop before submission, confidential research-team handling, limited demographics, no respondent name/student number, optional feedback, and thesis-period response retention. They reference the Data Privacy Act of 2012 and a separate research protocol and informed-consent document. Those conditions govern external research administration; they do not introduce survey collection or survey-response storage into TechGap. [FQ/SQ pp. 1–2 and final feedback pages; U4]

The external response scale is 5–1 agreement with `N/A` for unexamined or unassessable features, and unanswered items are permitted. No minimum passing rating or aggregation procedure is defined here. Functional accuracy ratings concern consistency of displayed results; respondents are not expected to verify individual job postings. [FQ pp. 3–12; SQ pp. 3–10; U5]

Declining survey consent means the respondent does not proceed. Participation or stopping before submission must not affect grades, academic standing, employment, or institutional standing. The questionnaires also state that identifying details should not be included in comments, findings may be summarized by respondent group for authorized academic reviewers, and later removal of a submitted response may be impossible if it cannot be identified. These are external study conditions, not additional application features. [FQ/SQ p. 1; U4]

## 9. Acceptance scenarios

These scenarios describe the evidence to inspect in the finished system. They do not prescribe testing tools, statistical methods, or implementation choices. The complete item-level evaluation mapping is in [Questionnaire traceability](QUESTIONNAIRE_TRACEABILITY.md).

| ID | Scenario | Expected evidence | Requirements |
| --- | --- | --- | --- |
| AC-01 | Choose either experience, enter relevant selections, navigate away, and return on a later visit. | No sign-in is required; the corresponding experience is accessible; selections remain available across related views and visits. | FR-SH01–SH02; NFR-RE03 |
| AC-02 | Review one academic track, then select another. | Each view identifies its track; coverage, industry requirements, alignment score, classifications, and explanations correspond to the current selection. | FR-A01–A03; FR-SH03; NFR-AC01–AC05 |
| AC-03 | Examine a track's gap and low-demand findings. | Covered and logically covered competencies can be distinguished from possible gaps; priorities relate to analyzed demand; low-demand topics have explanations and are presented for review. | FR-D03; FR-A04–A06; BR-06–BR-08 |
| AC-04 | Review curriculum recommendations alongside the findings and repeat the review with unchanged evidence and rules. | Each enhancement identifies its gap and course/curriculum area; its explanation is consistent; recommendations are additive, preserve academic constraints, and remain consistent under unchanged conditions. | FR-A07–A08; BR-09, BR-13 |
| AC-05 | Generate and print or retain an academic review report. | The selected track, alignment findings, gaps/priorities, and recommendations are consolidated into a readable artifact suitable for further academic review and sharing. | FR-A09–A10; NFR-RE04 |
| AC-06 | Propose an enhancement, inspect its projected effect, revise it, and inspect again; review the curriculum revision guidance. | Baseline and projected alignment can be compared; projections correspond to the proposal; prioritized guidance identifies affected courses and projected effects; protected academic coverage is preserved; no institutional curriculum changes are enacted. | FR-M01–M04; FR-A11; BR-01, BR-09–BR-10 |
| AC-07 | Examine analysis using the controlled evaluation dataset and analysis after job-market evidence or the supplied official curriculum reference is updated. | Findings refer to the evidence actually used; updated, pre-validated academic and industry evidence is available to subsequent analysis; controlled study findings remain interpretable as controlled findings. | FR-D02–D05; BR-07 |
| AC-08 | Select a student's program, track, year, and completed courses, including applicable common/core courses. | Selected coursework comes from the eligible official academic reference; the result reflects those selections; informal learning and General Education are excluded from the score. | FR-T01, FR-T05; BR-02–BR-04; NFR-AC01 |
| AC-09 | Compare suggested career roles and choose another available role. | Suggestions are ranked in relation to selected coursework; requirements support comparison; the chosen role is identified in detailed results. | FR-T02–T04 |
| AC-10 | Inspect the personal alignment score and coverage report. | The score, explanations, and classifications agree; skills represented by selected completed courses, possible gaps, and future coverage are distinguishable; actual mastery is not claimed to have been tested. | FR-T05–T06; BR-04–BR-05; NFR-AC02–AC05 |
| AC-11 | Follow the roadmap for the selected role and open resources. | The roadmap addresses identified gaps, supplies an order, identifies each step's skill, and provides relevant links the student can open. | FR-T07–T08; NFR-RE04 |
| AC-12 | Complete the applicable questionnaire activities, repeat an analysis, and retry a failed operation where one occurs. | Activities complete without excessive delay or unexpected interruption; repetition completes; retry permits continued use; instructions, terminology, result presentation, and navigation can be assessed against the questionnaire. | NFR-PE01–PE05; NFR-RE01–RE05; NFR-US01–US05 |

## 10. Interpretation limits

The system describes coverage evidenced by official academic content, not verified personal proficiency. Demand findings describe the JobStreet evidence analyzed, not every employer or future vacancy. A low-demand finding invites review, while an enhancement or simulation supports judgment rather than guaranteeing a better academic or employment outcome. These limits shall be preserved when presenting findings. [CH1 §§1.1–1.2, 1.7; FQ-GO3–GO4, DS5; SQ p. 2]

The complete requirements include Chapter 1 capabilities that are absent from or less explicit in the questionnaires: continuing academic and industry evidence updates, justified logical coverage, curriculum-change simulation, projected revision guidance, consistent recommendations under defined rules, and academic-constraint preservation. Their absence from the rated survey sections does not remove them from the user-confirmed full scope.

See [Requirements verification](REQUIREMENTS_VERIFICATION.md) for the source-coverage audit and [Paper change notes](PAPER_CHANGE_NOTES.md) for conversation decisions to consider when manually editing the paper.
