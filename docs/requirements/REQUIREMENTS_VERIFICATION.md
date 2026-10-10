# TechGap Requirements Verification

## 1. Result and scope of the check

The requirements have been rechecked against Chapter 1's substantive text on physical PDF pages 8–25 and every page of both questionnaires. All stated system capabilities, required outputs, business boundaries, and questionnaire quality expectations within the agreed non-technical requirements scope are covered after the corrections recorded below.

The [Questionnaire traceability table](QUESTIONNAIRE_TRACEABILITY.md) maps all 50 faculty/administrator rated statements and all 40 student rated statements. Non-rated questionnaire material is accounted for as academic context or external research administration, rather than silently converted into application features.

This is a document-coverage check. It does not verify a built application, empirical analytical accuracy, legal/regulatory compliance, or a favorable research result. Technical and methodological implementation details remain deferred under the user's instruction. They are not counted as missing user-facing features.

Conversation decisions that extend or differ from the papers are identified separately in [Paper change notes](PAPER_CHANGE_NOTES.md). In particular, the common/core-course expansion is a user-authorized departure from Chapter 1's narrower course wording, not an undiscovered requirement in the original PDF.

## 2. Findings addressed during the recheck

| Finding | Resolution | Source |
| --- | --- | --- |
| The user table listed faculty and administrators on separate rows despite their shared experience. | Replace those rows with one Faculty/Academic Administrator user group, including all named academic titles. Record U6. | User instruction; Chapter 1 §1.6, pp. 21–22; FQ p. 2 |
| Support for revised official academic content was implicit in the academic-reference requirements. | Add FR-D05 to make subsequent analysis of updated, pre-validated official curriculum references explicit. | Chapter 1 §1.2, p. 13; §1.7, pp. 24–25 |
| Explainability and academic constraints were explicit, but consistent recommendations under defined rules were only implicit. | Add BR-13 and reference it from FR-A07. | Chapter 1 §1.2, pp. 13–14 |
| Prioritized gaps and simulation were covered, but projected improvements in the curriculum revision guidance were not explicit. | Add FR-A11 and the corresponding required-output content; extend AC-06 to inspect that guidance. | Chapter 1 §1.2, p. 14 |

No rated questionnaire statement was missing from the previous mapping. These corrections strengthen coverage of Chapter 1 and the user's requested user-group presentation.

## 3. Chapter 1 coverage

| Source | Stated expectation or boundary | Coverage |
| --- | --- | --- |
| §1.1, pp. 8–12; §1.5, p. 19 | A web-based CICS curriculum–industry decision-support system for DLSU-D. | Requirements §§1–2; BR-01 |
| §1.1, pp. 11–12; §1.7, pp. 24–25 | Use official academic content, extract represented competencies, and organize evidence for analysis. | FR-D01; BR-02; requirements §3.1 |
| §1.2, p. 13 | Integrate updated curriculum and industry evidence to keep evaluation responsive to changing requirements. | FR-D02, FR-D05 |
| §1.3, p. 16; §1.5, p. 19 | Identify in-demand technical competencies from Philippine job-market evidence. | FR-D02; FR-A03, FR-A05 |
| §1.3, p. 16; §1.5, p. 19 | Compare represented curriculum competencies with industry requirements. | FR-D03; FR-A02–A04 |
| §1.3, p. 16; §1.5, p. 19 | Recognize logically covered skills and possible missing competencies. | FR-D03; FR-A04; BR-06 |
| §1.3, p. 16; §1.5, p. 19 | Prioritize gaps in relation to demand and changing industry evidence. | FR-A05; FR-D02; BR-07 |
| §1.3, p. 16 | Identify low-demand topics for curriculum review. | FR-A06; BR-08 |
| §1.2, pp. 13–14 | Produce structured, explainable, rules-based recommendations under academic constraints. | FR-A07–A08; BR-09, BR-13; NFR-AC05 |
| §1.2, p. 14 | Preserve mandated core competencies and applicable minimum academic requirements. | FR-A07; FR-M03; BR-09; requirements §8.1 |
| §1.2, p. 14; §1.3, p. 16 | Provide prioritized course-related revision guidance and summary reports, including projected alignment effects. | FR-A09–A11; requirements §3.2 |
| §1.2, pp. 13–14; §1.6, p. 22 | Simulate proposed enhancements before adoption; compare projected effects and refine proposals. | FR-M01–M04; BR-10 |
| §1.3, pp. 16–17; §1.7, p. 24 | Relate completed coursework to a chosen career role and display personal alignment and skill gaps. | FR-T01–T06 |
| §1.2, p. 14; §1.6, p. 21 | Provide career-aligned skill roadmaps and learning-resource guidance for independent learning. | FR-T07–T08; OUT-T01–T05 |
| §1.3, p. 17; §1.5, pp. 19–20 | Evaluate functionality, usability, accuracy, efficiency, and reliability using the stated quality instruments. | Functional requirements §5; non-functional requirements §6; evaluation boundary §8 |
| §1.4, p. 18 | Evaluate perceived usefulness, decision support, career alignment clarity, and curriculum alignment results. | OUT-A01–A05; OUT-T01–T05; OUT-D01–D05; FR-A03; FR-T05; requirements §8.3 |
| §1.6, pp. 21–23 | Serve students and academic stakeholders; benefit industry, university, and researchers. | Requirements §2.1; user outcomes §7. Beneficiaries do not create unspecified additional application roles. |
| §1.7, p. 24 | Limit the original academic reference to specialization subjects and exclude General Education. | General Education exclusion preserved in BR-03. The user explicitly expands eligible courses through U2; see PC-01. |
| §1.7, p. 24 | Use computing-related JobStreet postings, with approximately 5,000 postings in the described study dataset. | FR-D02, FR-D04; requirements §3.1. The approximate study quantity is not turned into an invented exact system limit. |
| §1.7, pp. 24–25 | Confine scope to CICS BSCS/BSIT at DLSU-D; use pre-validated official syllabus-derived data. | Requirements §2; FR-D01; BR-02 |
| §1.7, p. 25 | Exclude informal learning, internships, seminars, OJT, external certifications, and extracurricular activities from the score. | BR-03; FR-T05; requirements §§2.3, 10 |
| §1.7, p. 25 | Treat passing/completed coursework as full competency representation without testing actual retained knowledge. | BR-04; FR-T05; requirements §10 |
| §1.7, p. 25 | Use a controlled processed dataset for research evaluation; expanded acquisition is described for Thesis 2. | FR-D04; requirements §2.2. U1 selects full system capabilities without changing the study schedule. |
| §1.7, p. 25 | Keep outputs advisory and do not automatically alter institutional records or enforce changes. | BR-01; FR-M04 |

Chapter 1's contextual labor statistics, cited literature, and research hypothesis are not additional application functions. Its background reference to standards covering BSIS does not expand this system beyond the BSCS/BSIT scope expressly stated in §1.7.

## 4. Questionnaire coverage counts

| Faculty section | Source page | Rated items mapped |
| --- | --- | --- |
| Curriculum alignment analysis | 3 | 5 |
| Gap and obsolescence reports | 4 | 5 |
| Curriculum recommendations | 5 | 5 |
| Generated reports | 6 | 5 |
| Functional accuracy | 7 | 5 |
| Performance efficiency | 8 | 5 |
| Reliability | 9 | 5 |
| Usability | 10 | 5 |
| Perceived usefulness | 11 | 5 |
| Decision-making support | 12 | 5 |
| **Faculty total** | | **50** |

| Student section | Source page | Rated items mapped |
| --- | --- | --- |
| Curriculum-to-career alignment | 3 | 5 |
| Career pathway recommendations | 4 | 5 |
| Upskilling guidance | 5 | 5 |
| Functional accuracy | 6 | 5 |
| Performance efficiency | 7 | 5 |
| Reliability | 8 | 5 |
| Usability | 9 | 5 |
| Perceived usefulness | 10 | 5 |
| **Student total** | | **40** |

The mapping includes Future Curriculum Coverage, selection of another available career role, ranked role suggestions, ordered roadmap steps, openable resources, printable/shareable academic reports, selection-sensitive findings, retry after failure, and every quality/usefulness/decision-support statement.

## 5. Non-rated questionnaire content

| Content | Coverage and boundary |
| --- | --- |
| Privacy statement, research purpose, contacts, confidential handling, authorized-reviewer sharing, thesis-period retention, and separate informed consent | Requirements §8.3 and the external questionnaire references. Research response handling is not an application feature under U4. |
| Voluntary consent, declining participation, skipping items, stopping before submission, no adverse academic/employment consequences, and limits on later withdrawal of unidentified responses | Requirements §8.3. These are external participation conditions. |
| Faculty academic title, reviewed track, and years of experience | Requirements §2.1 and §3.1; faculty questionnaire remains an external demographic instrument. Combining the application user group does not remove title choices. |
| Student CICS/BSCS/BSIT eligibility, program, four tracks, year level, and coursework-only scoring notice | Requirements §§2–3; FR-T01; BR-03–BR-04. Survey eligibility does not introduce sign-in or identity verification. |
| `Other` demographic responses | Remain external survey options; they do not silently expand the specified academic scope. |
| 5–1 agreement scale, `N/A`, and unanswered-item permission | Requirements §8.3. No numerical system-performance limit or passing score is inferred. |
| Optional improvement/decision feedback and validation signatures | External study and instrument-validation material, identified in traceability §5. |

## 6. Verification boundaries

- The check covers the requirements the user asked to document: expected behavior, outputs, boundaries, standards references, and quality expectations.
- It does not turn Chapter 1's technical methodology into an implementation plan or choose technologies.
- The CHED obligation is recorded at the level stated in the supplied paper. Particular unit figures or protected identifiers are not fabricated.
- ISO-related wording is limited to the questionnaires' selected adapted criteria and does not claim full compliance.
- The PDF text is the source of the item counts. The proposed between-visit questionnaire additions in the paper-edit notes are not counted as existing items.
- The source PDFs remain unchanged. Paper changes are a separate manual task for the authors.
