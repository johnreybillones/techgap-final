# Pipeline policy research and recommendations

**Decision update, 2026-10-22:** The user accepted R5–R8. The proposal/status wording below preserves the original research-stage record; the current selected policies and explicit evaluation gates are in [Plan 2](../plan/DATA_FLOW_ACTUAL.md) and [A31](../plan/DECISIONS.md). Numerical examples remain illustrative; no model accuracy is established.

Prepared: 2026-10-20. Applies to [DATA_FLOW_ACTUAL.md](../plan/DATA_FLOW_ACTUAL.md) and [DATA_FLOW_CHANGES.md](../plan/DATA_FLOW_CHANGES.md). Ranking details: [ranking research](RANKING_OPTIONS_RESEARCH_2026-10-20.md).

**Status:** Research and proposed decisions for the user's questions 5-8. The recommendations below are not approved scoring policies, evaluated TechGap models, or implemented processing. They provide concrete choices to review before the full execution-plan rewrite. Numerical examples are illustrative, not analytical findings from the saved collection.

## 1. Confirmed answers and their consequences

| Confirmed answer | Consequence for the plan |
| --- | --- |
| Model development means the algorithms applied to extracted data to produce information for system features. | Specify parsing, extraction, normalization, evidence comparison, aggregation, scoring, ordering and output records. Custom neural-model training is not an independently established requirement. |
| One-time human checking of development evaluation examples is acceptable. | Build a source-labeled development benchmark; retain automatic ordinary ingestion without a recurring human approval queue. This does not establish who labels it, its size or an accuracy target. |
| Both experiences use the same entry/junior population; remote jobs are acceptable. | Academic and Student evidence use the same eligibility policy. Preserve Philippine eligibility and seniority evidence. A numeric experience-year cap, internship inclusion and handling of conflicting/unspecified seniority have not been selected. |
| Technical responsibilities contribute competency evidence alongside qualifications. | Parse technical duties as analytical evidence. Do not require every technical competency to appear under a Qualifications heading. Preserve duty/required/preferred/unspecified context separately. |
| Salary and education, experience, soft skills, benefits and offered training are retained without becoming technical-alignment inputs. | Preserve the original posting payload and source wording. These fields do not create technical competency score credit or priority weights. Experience/geography may be useful for eligibility; using them for that separate purpose is proposed below, not a numeric seniority rule already approved. |

The user's statement that contextual information is not part of model development does not mean it is physically absent from description text. Degree, experience and benefits can occur inside the description. The processor must recognize their context while leaving the original text intact.

### What the local pilot establishes

The saved [raw postings](../../data/collection_samples/jobstreet/raw-jobs.json) contain ten records. Salary is present in five and absent in five. The first posting's HTML contains headings, paragraphs and list items; its `description_text` flattens these into a paragraph. Posting `95306355` is titled Intermediate Web Developer; `95324832` contains a four-plus-year experience requirement. Other postings explicitly identify junior roles or welcome fresh graduates. This is evidence that population filtering is needed, not a validated count of eligible postings.

Preserve all ten raw records. A later population decision changes analytical membership, not the original collection. No new actor run or model inference was performed for this research.

## 2. How description text should become meaningful records

This is a proposed processing sequence to make the recommendations concrete. It is not a claim that GLiNER alone performs every transformation.

1. **Keep source evidence:** retain every original returned key, including `salary` when published, `description_html`, `description_text`, posting ID/URL, query/run identity and dates. Record missing versus null versus empty; do not infer an undisclosed salary or normalize it to zero.
2. **Recover document blocks:** parse HTML in document order. Treat each paragraph and list item as a block, associate subsequent blocks with their heading, and handle headings written as bold paragraphs as well as heading elements. Prevent a paragraph inside a list item from being emitted a second time. Python's HTML parser exposes tags and text; choosing an HTML parser does not itself solve section classification. [Python HTML parser documentation](https://docs.python.org/3/library/html.parser.html).
3. **Build an evidence representation:** create readable text with explicit paragraph/list boundaries and a mapping from each block to its DOM path and character offsets in that generated text. Keep actor text as a separate representation; generated offsets must not be represented as offsets into original HTML or PDF coordinates. If HTML is unavailable or malformed, preserve a fallback and reduced-structure status rather than inventing headings.
4. **Classify sections and statements:** use headings plus statement content to distinguish duties, qualifications, required technical skills, preferred skills, education, experience, soft skills, benefits, offered training and company background. A heading alone is insufficient: a Qualifications section can mix several kinds. A mixed statement can contain both a technical span and contextual spans.
5. **Extract technical spans:** extract named technologies, technical knowledge and capability phrases from relevant statements. A schema-driven extractor such as GLiNER2 is a candidate for entity/structured extraction and classification. Its publisher documents span output; preserve exact source spans and model/configuration identity. Extraction scores are model outputs, not calibrated correctness guarantees. [GLiNER2 paper](https://aclanthology.org/2025.emnlp-demos.10/), [publisher repository](https://github.com/fastino-ai/GLiNER2).
6. **Recover requirement logic:** retain negation, required/preferred/duty context, alternatives, conjunctions, tools and objects. List splitting is not automatically competency splitting. Punctuation in `Node.js`, `C++` or a product name must not break the technology name. An ambiguous slash or relation receives unresolved status, not an assumed AND/OR rule.
7. **Make separate outputs:** produce raw/context records and proposed technical requirement records. Preserve offered-training mentions as offered training, not as required prior knowledge. Keep relationships from a capability to its tool; do not inflate the denominator by counting every noun and its parent capability separately.
8. **Admit analytical records only after checks:** require a valid source slice, technical relevance, resolved requirement context/structure, posting eligibility and an evaluated extraction policy. An uncertain record remains visible without becoming a confident gap or coverage finding.

For each block/statement/mention/requirement record, retain its source posting, section/block identity, text representation, evidence span, context, processing version and uncertainty reason. A requirement additionally records its expression tree and its accepted concept references. Evidence coordinates must be validated against the actual saved representation.

**Local example, extraction only:** posting `95302417` contains a duty about building automation workflows using n8n to connect APIs and other tools. The proposed records retain the capability, `n8n` as a tool and the integration context. They do not turn every mentioned API/LLM/tool into an independent prerequisite. This posting's entry/junior eligibility is not established by that extraction example. Official n8n documentation describes its workflow-automation purpose; that definition explains terminology and cannot create syllabus coverage. [n8n documentation](https://docs.n8n.io/).

Span-based skill extraction and linking to a fixed inventory are distinguishable designs in the research literature. SkillSpan supplies expert annotation guidance and evaluates skill/knowledge spans; its published results do not establish performance on TechGap's Philippine postings or syllabus text. [SkillSpan paper](https://aclanthology.org/2022.naacl-main.366/).

## 3. Question 5: a competency absent from an existing catalog

### Meaning and example

A catalog is a controlled list of competency concepts and aliases. Suppose the local list currently contains PHP, MySQL, JavaScript and React. A later posting explicitly asks for n8n workflow development. The posting supplies evidence of that requirement even if the local list has no n8n entry. Missing from the catalog means unknown to that reference, not missing from the source.

| Source situation | Recommended treatment |
| --- | --- |
| Clear technical term/capability, such as n8n in a workflow-development duty | Preserve it, give an accepted source-backed local concept an identifier, and retain catalog status `unlinked`. Catalog absence alone does not exclude it. |
| Supported alternate wording of an existing concept | Link the wording while retaining the original mention and the evidence for equivalence. |
| Ambiguous abbreviation, such as a standalone `R` without sufficient context | Retain an unresolved mention. Do not automatically map it to a programming language or include it as a definite scored requirement. |
| Tool mentioned only as something the employer will teach | Preserve offered-training context; do not treat it as required prior competence. |
| A clear new job requirement with incomplete academic evidence | Keep the requirement; its coverage is unassessable until the relevant academic evidence is adequate. Do not turn a catalog miss into a curriculum gap. |

**Recommendation R5:** allow clear, source-grounded competencies without requiring a pre-existing external-catalog entry. Keep extraction acceptance, concept linking and coverage assessment as separate statuses. A local ID identifies a stored concept; it does not establish that all similar phrases refer to the same capability. Unknown concepts require the same evaluated checks as known ones.

The European Commission describes ESCO non-preferred terms as including synonyms, spelling variants and abbreviations. This supports explicit alias handling; it does not mean ESCO has already been adopted or that every abbreviation is safe to merge. [ESCO terminology explanation](https://esco.ec.europa.eu/en/about-esco/escopedia/escopedia/non-preferred-term).

**Alternative:** restrict scoring to an approved catalog. This gives a bounded vocabulary, but delays legitimate new requirements and can understate observed technologies. It conflicts with the already confirmed intent to extract beyond a fixed literal list unless new entries have an explicit lifecycle. The proposed source-backed policy handles that lifecycle without a recurring approval queue.

## 4. Question 6: what counts in the alignment percentage

### Binary support is different from partial skill proficiency

Here, a binary result answers whether the included coursework supports a defined requirement. It does not claim that a student has a measured proficiency of 0% or 100%. Partial proficiency would need additional evidence and a defined scale; it is not supplied by a similarity value.

**Illustrative posting:** Python and SQL are required; either React or Vue is acceptable; Docker is preferred. Assume adequate source evidence and coursework supporting Python and React, but not SQL.

| Independent core requirement group | Coursework finding | Credit under R6 |
| --- | --- | --- |
| Python | Supported | 1 |
| SQL | No support established in complete assessed evidence | 0 |
| React OR Vue | React supported | 1 |
| Docker, preferred | Assessed separately | Outside the core denominator |

This gives `2 / 3 × 100 = 66.7%` core requirement coverage. Counting React and Vue as two mandatory gaps would misread the posting. Docker remains available as a preferred-skill finding and optional roadmap target; it is not discarded.

**Recommendation R6:** start with equal binary credit per independently assessable core requirement group. Proposed core scope includes explicit required technical competencies and clear technical duties; explicit preferred competencies get a separate summary. Preserve unspecified modality separately until its analytical treatment is agreed. Do not guess fractional weights from adjectives such as strong or basic.

### Conjunctions and composite tasks

- A list of independent skills, `Python and SQL`, gives two assessable requirements when its context supports that interpretation.
- `React or Vue` is one alternative group: either supported option satisfies it; count it once.
- `Build REST APIs using Python` retains the task/tool relationship. Python evidence alone does not establish REST API development. Show supported components, but do not assign invented half-credit to the whole task.
- For a genuinely linked `A AND B` requirement group, all necessary supported components are needed. For `A OR B`, one supported alternative suffices. Preserve nesting rather than converting the expression to a flat bag of keywords.
- Repeating one requirement in several sections of the same posting adds evidence, not more denominator weight. Different tasks involving the same tool are not automatically duplicates; task granularity must be fixed in annotation guidance and evaluated.

### Unknown is different from unsupported

With three defined groups, if two are supported and the third cannot yet be assessed, do not report either a complete `2/2 = 100%` or an ordinary `2/3` gap score. Display two confirmed supported groups and one unresolved group. A proposed supplementary figure is a **confirmed-support fraction** `2/3`, labeled incomplete; the possible evidence-resolution range is `2/3` to `3/3`. This is a logical bound, not a statistical confidence interval. Do not produce a final complete alignment score while relevant source extraction remains defective.

If the number or structure of requirements itself is unresolved, even that bound is unavailable. A posting with no usable core requirements receives no score. Exclusion from a numerical aggregate must be visible through total/assessed/unassessable posting counts; it cannot silently improve the result.

### From postings to a role or academic population

For a fully assessable posting `j`, propose `coverage_j = supported_core_groups_j / total_core_groups_j`. For a fully assessable validated role population, propose the arithmetic mean of `coverage_j`, with each distinct eligible posting contributing once. Use the same rule for career comparison and the selected role's alignment. A verbose posting therefore has no extra population weight just because it lists more requirements. The [ranking research](RANKING_OPTIONS_RESEARCH_2026-10-20.md) compares this with pooled groups and a unique role-skill union.

For Academic analysis, the evidence supplied to those comparisons is the entire applicable selected-track coursework set; for Student analysis it is only selected completed courses. Future courses never enter the current numerator. Separate curriculum-relevance measures require their own explicit denominator; they must not be presented as interchangeable with job-requirement coverage.

These formulas are proposed TechGap policies. Research sources do not prescribe a universally correct curriculum-alignment formula. Sentence Transformers documents semantic similarity as comparison of text embeddings, and its evaluation tools measure pair decisions on labeled examples. Therefore cosine is a candidate-retrieval signal, not the proposed alignment percentage or a proficiency scale. [Semantic similarity documentation](https://www.sbert.net/docs/sentence_transformer/usage/semantic_textual_similarity.html), [evaluation documentation](https://www.sbert.net/docs/package_reference/sentence_transformer/evaluation.html).

## 5. Question 7: logical coverage in plain language

Logical coverage asks whether actual coursework supports a job requirement even when the same words do not appear. It must distinguish supported meaning from mere relatedness.

| Illustrative course evidence | Illustrative job requirement | Proposed assessment |
| --- | --- | --- |
| Create SQL queries that combine records from multiple tables using JOIN | Query relational data using SQL joins | Same concrete capability under different wording; can receive supported coverage after semantic assessment is evaluated. |
| Introduction to databases | Optimize PostgreSQL queries | Related subject, insufficient evidence for that task/tool-specific requirement. |
| Develop a web page using React | Any advanced JavaScript task | React's mention alone does not establish every JavaScript capability. |
| A Python course is a prerequisite for an AI course | Implement a neural network | The prerequisite relationship alone does not establish that the included coursework teaches this capability. |

**Recommendation R7:** implement evidence-backed same-capability matching and narrowly scoped directional rules; keep unsupported cross-skill implications unresolved. Do not enable a general rule such as any framework implies all its language's skills. The existing requirements' wording about different expressions should not be narrowed to an assumption that logical coverage always needs a universal graph.

Proposed comparison order:

1. Retrieve exact terms and supported aliases, while checking task, object and context.
2. Use SBERT/cosine to retrieve candidate academic passages for the actual requirement, retaining the full passages and versioned retrieval settings.
3. Evaluate whether those passages support the same required capability; reject a match that relies only on topic similarity, offered training, incidental mention or a narrower unsupported task.
4. For a distinct-skill implication, require a versioned rule with direction, factual source, scope, required course evidence, prohibited cases and development examples. An external definition alone never replaces course evidence. If no supported rule exists, emit unresolved relationship status.
5. Store the actual passage(s), the assessed requirement, matching basis, rule/evaluator identity and explanation. Only accepted support can receive score credit; future-course support remains separate.

The technical relationship itself is not a curriculum-coverage rule. TypeScript's documentation describes its relationship to JavaScript, but does not demonstrate what a specific syllabus teaches. [Official TypeScript explanation](https://www.typescriptlang.org/docs/handbook/typescript-in-5-minutes.html).

W3C explicitly separates informal SKOS concept organization from formal assertions about the domain. A broader/narrower/related edge is not, by itself, a prerequisite or coursework-coverage implication. [SKOS Reference, sections 1.3 and 8](https://www.w3.org/TR/skos-reference/).

Natural-language inference evaluates whether a premise supports a hypothesis, unlike symmetric similarity. A pair classifier is a possible experiment for directional evidence checking; a generic NLI model is not an adopted curriculum evaluator and requires TechGap examples. A similarity reranker cannot be relabeled as entailment without evaluating that task. [Original NLI corpus paper](https://aclanthology.org/D15-1075/), [Sentence Transformers pair-classification documentation](https://www.sbert.net/docs/cross_encoder/training_overview.html).

If an automatic evidence evaluator is used, benchmark exact matching, semantic same-capability decisions and any conditional-rule stage separately. Until it meets the agreed evaluation policy, uncertain candidates remain unresolved. This recommendation does not claim a working logical-coverage engine or full compliance today.

## 6. Question 8: ranking recommendation summary

Full source analysis, algorithms and examples are in [ranking research](RANKING_OPTIONS_RESEARCH_2026-10-20.md).

| Responsibility | Recommendation for review |
| --- | --- |
| Academic gap priority | Order assessable gaps by distinct eligible postings expressing each core requirement, within the fixed selected-track population. Preserve required/duty/preferred/alternative contexts; do not pretend each option of an OR group is individually mandatory. |
| TOPSIS | Keep as a candidate, not a v1 requirement. Introduce it only after genuinely different sourced criteria, their directions and user-approved tradeoffs exist. Count and prevalence in a fixed population are proportional and should not be duplicated as independent criteria. |
| Career ranking | Compare the mean per-posting core-group coverage under the same assessment policy, showing source counts, uncertainty and limits. Do not interpret coursework alignment as employment probability. |
| Low-demand review | Show observed `n/N` and no observed occurrence. Do not invent a high/low cutoff or call zero observations obsolete. A categorical low-demand label remains gated until a cutoff and sufficient population are agreed. |
| Roadmap | Order supported gap targets by their selected-role posting demand, with shared ranks for substantive ties. Add preparatory order only where a relevant resource explicitly supports it; do not invent a universal dependency graph. |

The proposed demand order is a recommendation, not a silent replacement of provisional TOPSIS. Sparse or unresolved results remain qualified. Salary, soft skills and years of experience are not proposed skill-priority criteria.

## 7. Eligibility and evaluation work still needed

### Entry/junior and remote admission

Propose an `eligible / ineligible / unresolved` evidence record before technical population aggregation. Record explicit role-level statements, applicant requirements, Philippine/remote eligibility and contradictions. A mention of working with senior developers must not classify the applicant's role as senior. An explicitly intermediate title is contrary evidence for the confirmed population; a generic title with two years required is not automatically junior or senior without a chosen rule. Remote alone does not establish Philippine eligibility.

The user has not selected an experience-year cutoff. Recommend preserving explicit junior/entry/fresh-graduate evidence and leaving conflicting/unspecified cases unresolved while evaluating a numeric policy only if needed. Degree, salary and technical competency coverage do not establish seniority. Whether internships enter the same population also remains a separate scope choice; do not infer inclusion from a fresh-graduate title that also mentions internships.

### Development benchmark

Use the authorized one-time human checking to label actual source passages for block boundaries, technical/context separation, skill spans, requirement modality, AND/OR grouping, eligibility, aliases, same-capability coverage and false cross-skill implications. Include unfamiliar terms, task/tool composites, negation, training offers, missing sections and incomplete syllabi. Keep jobs and academic records in each evaluation scope; external datasets cannot certify either source automatically.

Separate development examples used to tune rules/thresholds from a held-out source-level evaluation. Group duplicated/related versions of a source together so repeated text does not leak across the partitions. Group-aware splitting is an established mechanism; exact split sizes and the final error policy still depend on the available labeled collection. [scikit-learn GroupShuffleSplit documentation](https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.GroupShuffleSplit.html).

Measure extraction precision/recall and span errors, requirement-context/group errors, incorrect normalization, false supported coverage, missed support, unresolved rates and downstream score/count consistency separately. Select encoder/extractor artifacts and retrieval/acceptance settings using development evidence, then evaluate held-out sources. No numerical accuracy target, cutoff, runtime or fine-tuning requirement is established by this research.

## 8. Decisions needed before these become the execution specification

- R5: accept source-backed local competencies without requiring an existing catalog entry, subject to the evaluated acceptance policy.
- R6: accept equal binary core requirement groups, explicit AND/OR logic, separate preferred findings, visible uncertainty and the proposed per-posting population aggregation. The treatment of unspecified modality and precise task granularity still need worked-case agreement.
- R7: accept same-capability evidence matching and a bounded, tested rule approach; retain unresolved status for unsupported cross-skill implications. No general graph or NLI model is assumed supplied or validated.
- R8: accept transparent demand ordering for v1 instead of making TOPSIS compulsory; retain explicit criteria/weight approval if TOPSIS is introduced later. Low-demand cutoffs and sparse-role sufficiency are not silently supplied.

After these policy choices, the full execution plan can specify the approved artifact schemas, exact stage algorithms, example transformations, evaluation cases, dependencies, rerun rules and failure outputs. This research resolves what the options mean; it does not substitute proposed choices for user decisions.
