# Ranking, low-demand review and roadmap options — 20 October 2026

**Decision update, 2026-10-22:** The user accepted R8: distinct-ad demand priorities, equal-posting career coverage, descriptive topic review and demand/resource-scoped roadmap order. Original unapproved-policy wording below is historical. [Plan 2](../plan/DATA_FLOW_ACTUAL.md) and [A31](../plan/DECISIONS.md) now govern; model evaluation, broader reverse relevance and categorical cutoffs remain explicit gates.

Status: research and recommendations for D09/D10, **not approved scoring or ranking policy**. No collection, model, ranking, benchmark or production pipeline was run. This note investigates the consequential choices requested by the user before the execution plan is rewritten.

## 1. Established scope and available evidence

The latest user answers define one population for Academic and Student analysis: entry/junior computing postings, including remote work eligible for people in the Philippines. No experience-year cutoff has been approved; “junior” must not silently become “at most two years.” Experience evidence can help determine population eligibility, but is not a competency-score criterion. Salary, education, experience, soft skills, benefits and offered training remain retained source context, outside technical competency scoring. Technical work responsibilities can supply competency evidence when the source supports that interpretation.

Inspected local evidence: [actual flow](../plan/DATA_FLOW_ACTUAL.md), [change record](../plan/DATA_FLOW_CHANGES.md), [decision register](../plan/DECISIONS.md), [requirements](../requirements/SYSTEM_REQUIREMENTS.md), and [saved posting field inventory](../../data/collection_samples/jobstreet/field-inventory.csv). These distinguish provisional TOPSIS, unapproved ranking rules and actual source fields. They provide posting IDs, descriptions/HTML, dates and role context. They do not establish valid employer-wide prevalence, teaching effort, course capacity, proficiency, gap severity, a complete prerequisite graph or an expert relevance-ranking label set.

Observed posting frequencies are evidence about the collected population. Online ads have coverage and content biases: the European Commission's JRC identifies overrepresentation of highly skilled occupations and differences between advertised skills and actual work needs. Its study does **not** estimate Philippine JobStreet bias. The applicable implication is to label TechGap's observed collection honestly, rather than claim a representative national labour-market estimate. [JRC institutional research summary](https://joint-research-centre.ec.europa.eu/jrc-news-and-updates/online-job-ads-promising-yet-biased-data-employment-and-education-policy-2024-01-24_en).

## 2. Recommendation: explicit demand ordering before a composite index

**Recommend v1 gap ordering by distinct-posting demand within the defined analysis population. Retain TOPSIS as an investigated candidate rather than forcing a second criterion into it.** This changes the provisional direction and needs the user's decision.

The proposed calculation is an auditable engineering design, not a formula established for TechGap by an external paper:

1. Freeze a collection snapshot and population-policy version. Resolve duplicate source IDs, entry/junior eligibility, Philippines eligibility, full-description availability and role membership. Keep excluded and unresolved posting counts and reasons.
2. Take only requirement units accepted under the eventual D08 policy. Deduplicate repeated mentions of the same requirement within a posting. A count measures distinct postings, not text occurrences, scraped HTML/text copies, query appearances or displayed search rank.
3. Count explicit required technical competencies and technical responsibilities classified as requirements under the agreed extraction policy. Preserve preferred, alternative-option and unspecified contexts separately. Do not silently relabel every technical mention as mandatory.
4. For each competency or explicit alternative group, retain `supporting_posting_ids`, `required_count`, `preferred_count`, `alternative_option_count`, `unspecified_count` and the applicable population denominator. These context counts may overlap and therefore must not automatically be added into one total.
5. Identify the requirements lacking established coverage in the selected academic/current-student evidence set. Keep genuinely unresolved coverage separate from assessed possible gaps.
6. Order assessed gaps by required-posting count descending. Show `n/N` and percentage beside each item. Equal counts receive equal priority rank; a stable identifier can arrange tied rows for reproducibility without claiming one is more important.
7. Show optional/preferred evidence as a separate list or field until the user approves its analytical treatment. No arbitrary “required = 1, preferred = 0.5” weights are assumed.

Within a fixed population, prevalence is `100 × n/N`; it is useful explanatory context but gives the same order as count. For track-level analysis, the population needs an explicit role-to-track association policy; search keywords or classifier proximity alone cannot establish that relationship. Unequal query caps can affect the collected role mix, so the resulting counts must not be described as uncapped whole-market demand.

**Illustrative numbers only, not extracted results:** in 100 eligible, analyzable postings, SQL is required in 50, Git in 40 and Docker in 20. If all three are assessed gaps, the proposed order is SQL, Git, Docker, with evidence `50/100`, `40/100`, `20/100`. Their corresponding prevalence values are 50%, 40% and 20%; those are the same criterion in different units.

For “React or Vue,” retain the alternative group. A posting provides evidence that either option can satisfy that requirement, not evidence that both are mandatory. A student with a supported Vue match already satisfies that group. An unmet group remains a choice to resolve in learning guidance; the system must not automatically turn it into two required gaps. Normalization of alternative groups and their inclusion in the main demand order remain coupled to D08.

Missing descriptions/extraction are not zero demand. Preserve the whole eligible count, the analyzable subset count and excluded/unresolved count. Publish the exact denominator actually used. If required text is incomplete, do not claim the analysis covers all eligible postings. A known unresolved mention cannot silently become an accepted requirement or disappear without an issue record.

## 3. What TOPSIS can and cannot add here

TOPSIS is a multiple-attribute decision method from Hwang and Yoon's work. Its method reference establishes an algorithm, not appropriate TechGap criteria, weights or accuracy. The original book is subscription content; its publisher metadata and chapter scope were verified, rather than claiming the full book was read. [Hwang and Yoon, 1981, methods chapter](https://link.springer.com/chapter/10.1007/978-3-642-48318-9_3).

An open original research article describes the positive/negative ideal framework and examines effects of normalization and weights. Its application concerns corporate sustainability, so its empirical results do not validate curriculum-gap ranking. Its methodological implication is that aggregation choices affect the answer and require disclosure. [López-García, Liern and Pérez-Gladish, published 2023](https://link.springer.com/article/10.1007/s10479-023-05543-8).

For the present source contract:

| Candidate criterion | What is available | Recommendation |
| --- | --- | --- |
| Distinct-posting count | Derivable from accepted requirements and posting IDs. | Valid observed-demand criterion within a stated population. |
| Posting prevalence | Count divided by the same population size. | Display with count; do not add it as a second supposedly new criterion. |
| Gap indicator | Every candidate in a gap-only table is already a gap. | A constant column provides no discrimination. Uncertain matches are not a severity scale. |
| Number of roles using the competency | Derivable after validated role grouping. | Potentially different “breadth” objective, but its importance is a product decision; splitting/merging role groups changes the value. Do not adopt automatically. |
| Required versus preferred frequency | Separately derivable if context is reliable. | Preserve both; combining them introduces a tradeoff requiring approval. They are not automatically independent importance measures. |
| Salary, education, experience, soft skills, benefits, offered training | Source context, with missing values. | Excluded from technical scoring by the latest user direction. |
| Employer prevalence, difficulty, teaching effort/capacity, proficiency, severity, Bloom level | No established valid measurement contract. | Do not fabricate values to populate a TOPSIS matrix. |

Statistical independence of every criterion is not a universal TOPSIS requirement. The concrete problem here is double-counting the same demand measurement and presenting an unapproved tradeoff as an objective result.

### One-criterion consequence, derived explicitly

For a single nonnegative benefit criterion `x_i`, classical vector normalization and a fixed positive weight are common positive scaling. The distance-based closeness therefore simplifies algebraically to:

`C_i = (x_i − min(x)) / (max(x) − min(x))`, when `max(x) > min(x)`.

For counts 50, 40 and 20, closeness is 1, 2/3 and 0. The order is identical to raw demand order. The last item still appears in 20 postings: a closeness of 0 does not mean no demand. If all counts are equal, the expression is undefined because ideal and worst coincide; all alternatives should be reported tied without inventing a score. Empty, single-item, zero-column and missing-input cases also require explicit handling.

Adding an alternative can change the reference extrema and therefore the values, even without changing an old skill's evidence. With multiple criteria, the original García-Cascales and Lamata study documents TOPSIS rank reversal when the alternative set changes. Its accessible abstract was verified; no paywalled numerical experiment was reproduced. [García-Cascales and Lamata, 2012, original paper](https://doi.org/10.1016/j.mcm.2011.12.022).

If TOPSIS is later selected, the execution plan must record alternatives, raw criterion values, formulas, units, direction, source coverage, normalization, weights, distance function, ideal/worst points, ties and degenerate-input behavior. Evaluate the approved weight range and candidate-set additions/removals; report rank changes and ties rather than selecting whichever configuration produces the expected answer. A TOPSIS closeness is a relative decision index, not alignment, confidence, mastery or probability of employment.

## 4. Career comparison: recommend equal posting contribution

**Recommend comparing roles by the mean of per-posting required-group coverage**, conditional on D08 approving binary requirement groups and their coverage rules. Use the same chosen aggregation in the selected-role alignment result so ranking and the displayed target result remain consistent. This is a proposed TechGap metric, not a published validated career-success model.

For role `r`, let `P_r` be its accepted eligible posting set. For posting `j`, let `m_j` be its nonempty, deduplicated required-group count and `c_j` its covered-group count. For completely assessed postings:

`posting_alignment_j = c_j / m_j`

`role_alignment_r = 100 × sum(posting_alignment_j for j in P_r) / |P_r|`

Each posting contributes equally. Each independently assessable requirement within a posting contributes equally. An OR group is covered by any accepted option; an AND statement is split only when its independently assessable parts have been established. Repeated mentions do not add weight. Required responsibilities follow the agreed extraction treatment. Preferred-only evidence is separate under the recommendation above.

This metric answers “What share of the stated required groups is supported, on average, across these collected postings for this role?” It does not mean “What percentage of employers will hire this student?” It does not grant current coverage from future courses, salary, education or years of experience.

**Illustrative example:** a student's completed courses support SQL, Git and Python, with no established React/Vue, statistics or Power BI coverage.

| Role / illustrative posting | Required groups | Covered groups | Posting alignment |
| --- | --- | --- | --- |
| Web / W1 | SQL; Git; (React OR Vue) | SQL; Git | 2/3 = 66.67% |
| Web / W2 | SQL; Git; Python | All three | 3/3 = 100% |
| Data / D1 | SQL; Python; statistics | SQL; Python | 2/3 = 66.67% |
| Data / D2 | SQL; Python; Power BI | SQL; Python | 2/3 = 66.67% |

The proposed role values are Web 83.33% and Data 66.67%, each with `N = 2` and the specific posting evidence. Two postings are transparent support, not an established sufficient evidence level.

Aggregation matters. Taking the union of Web's four distinct groups produces 3/4 = 75%, assigning Python's one-posting requirement the same role-level weight as SQL's two-posting requirement. Pooling all covered/required groups across postings instead gives verbose postings more influence. For a separate example with one 20-group posting at 1/20 coverage and one 2-group posting at 2/2, the posting mean is 52.5%, while pooled coverage is 3/22 = 13.64%. Neither is a mathematical mistake; they answer different questions. Equal posting contribution is the recommended interpretation, and needs user approval.

The OECD's original graduate-skills study found occupational and within-cluster geographic variation in its US posting sample. This supports preserving role and location context, but does not choose TechGap's aggregation formula or establish Philippine role definitions. [Brüning and Mangeol, 2020](https://www.oecd.org/en/publications/what-skills-do-employers-seek-in-graduates_bf533d35-en.html).

### Incomplete or incomparable career evidence

- `m_j = 0` supplies no technical-coverage ratio, not 0% or 100%. Distinguish no stated technical requirements from failed extraction. Record such postings and why they are outside the score denominator.
- For a fixed, complete extracted group set with `u_j` unresolved coverage assessments, `c_j/m_j` is only a demonstrated lower bound and `(c_j + u_j)/m_j` a possible upper bound. For 2 covered, 1 gap and 1 unresolved group, these are 50%–75%. They are not statistical confidence intervals and must not grant uncertain credit.
- If the requirement extraction itself is incomplete, the denominator may be unknown. The preceding bound does not cover undiscovered requirements; withhold a complete score and expose the extraction issue.
- Do not obtain a seemingly complete role score by silently dropping unresolved postings. Either show a clearly labeled assessed-subset result with both subset and whole counts, or keep complete-role ranking pending. Recommend the latter for a production “best aligned role” claim.
- A strict comparison between two bounded results is supported only when one's demonstrated lower bound exceeds the other's possible upper bound; otherwise their order can depend on the unresolved assessments. This is a proposed conservative ordering rule, not probability estimation.
- Do not mix current/future evidence, collection windows, different seniority policies or inconsistent role definitions in one comparison. Rank by alignment alone; display demand/support alongside it without silently multiplying the score by posting volume.
- No source establishes a universal minimum role-posting count or confidence band for this non-random collection. Show exact support and limits; decide any suppression/minimum rule through explicit policy and development evaluation. `N = 0` is necessarily unavailable. Do not invent “at least 30” as accepted policy.

## 5. Low-demand topics: descriptive review before a cutoff

**Recommend a review list ordered by observed posting prevalence ascending, retaining the count and denominator.** Use “not observed in this analyzed collection” for `0/N`. Reserve a categorical “low demand” threshold for an explicit user-approved policy evaluated on the eventual population. Foundational or institutionally required content must not be treated as disposable because employers do not name it in ads.

This recommendation uses the same demand records as the gap list, but starts from academic competencies: a course topic can be present in the curriculum and rarely observed in the chosen collection. Keep topic identity, source course/outcomes, matched posting evidence, observation context, snapshot/population and uncertainty. Do not compare a web-only posting sample against every computing track and then label networking or hardware topics low demand.

“Below 5% of postings” and “bottom fifth percentile of competency prevalences” are different rules. In 100 postings, the former concerns fewer than five matching postings. The latter concerns a topic's relative position among topic prevalence values and can flag some topics even when all have substantial absolute prevalence. Neither cutoff has been approved here. A snapshot supplies no historical decline claim; changing role/query mix can change observed prevalence without a change in underlying demand.

The current ten-posting pilot establishes obtainable descriptions, not adequate whole-track topic-demand evidence. The JRC's bias findings support interpreting missing/low observed counts carefully; they do not provide a numeric TechGap cutoff. [JRC source](https://joint-research-centre.ec.europa.eu/jrc-news-and-updates/online-job-ads-promising-yet-biased-data-employment-and-education-policy-2024-01-24_en).

## 6. Roadmap order: target-role demand with scoped preparation

**Recommend target-role gap demand order as the default roadmap order, adjusted only by explicitly sourced preparation needed for the chosen resource.** This is useful ordering without claiming a universal prerequisite graph or a duration-optimized learning schedule.

Proposed process:

1. Start from the selected role's assessed current gaps, using the same required-group policy. Keep preferred learning targets separate and preserve alternative choices.
2. Attach the selected role's distinct-posting counts and sort descending, with tied priorities explicit. A stable identifier can order tied rows only for reproducibility.
3. Attach applicable uncompleted-course evidence as a future-coverage annotation. It does not remove a current gap, reduce its demand count or automatically postpone it: no study deadline/course-placement policy has been supplied.
4. Attach only a verified relevant learning destination. Retain provider, exact URL, subject, suitability, checked date and any provider-stated preparation. A missing destination leaves the gap visible with resource-unavailable status.
5. When the chosen resource explicitly requires preparation not supported by completed-course evidence, include a labeled preparatory step before that resource. Preparation is for using that resource, not another observed employer requirement, and does not receive current alignment credit. Avoid indefinite inferred prerequisite expansion.
6. If several selected resources provide verified ordering constraints, represent only those constraints as directed edges and perform a topological ordering. Among currently available steps choose the highest target-role demand; ties remain equally prioritized. Detect a cycle and surface the conflicting source constraints rather than silently removing an edge. Python's official `graphlib` contract supports topological ordering and cycle detection, but supplies no skill relationships. [Python documentation](https://docs.python.org/3/library/graphlib.html).
7. Preserve a per-step explanation: gap evidence, frequency, any ordering constraint and source, resource status and future-course annotation. No unsupported estimated study hours, personal proficiency or automatic progress tracking is added.

For example, MDN's DOM scripting lesson explicitly asks for HTML, CSS fundamentals and JavaScript basics. Those statements justify preparation for that lesson only; they do not prove a universal relationship or that a student already has those skills. If the student lacks supported JavaScript basics, the plan can place an appropriate verified JavaScript preparation resource before that DOM lesson. Another independent high-demand gap can keep its demand priority. [MDN lesson](https://developer.mozilla.org/en-US/docs/Learn_web_development/Core/Scripting/DOM_scripting).

## 7. Development checks before calling the ranking usable

The user has allowed one-time human checking during development. Recommend a frozen, independently checked example set covering population eligibility, repeated/overlapping collection results, required/preferred/alternative contexts, OR/AND groups, uncommon terms, course-evidence uncertainty, role ambiguity and incomplete descriptions. Labels and disagreements must be traceable to source passages; the check does not create a routine approval queue.

Verify these substantive invariants against independently calculated examples:

- Repeating a competency within one posting or returning the same ID through two queries does not increase demand or its scoring weight.
- A supported OR option covers one group; it does not create two requirements. Offered training and preferred-only skills do not enter mandatory counts under the recommended policy.
- Additional verified current-course coverage never lowers alignment for an unchanged posting/role evidence set. Additional future-course evidence never increases current alignment.
- Reordering source files, rows, queries or tied candidates leaves values and priority ranks unchanged.
- Unknown coverage and incomplete extraction retain their issues and denominators/status. Empty evidence cannot become 100% alignment.
- The role score can be independently reconstructed from posting scores and their inclusion/exclusion reasons. Different role-profile sampling choices are compared before a cross-role ranking is promoted as meaningful.
- Run comparisons with and without disputed role assignments, uncertain-context postings and possible reposts; show material ranking changes. If TOPSIS is selected later, also test agreed weight variations, constant/correlated columns and candidate additions/removals.
- Roadmap dependencies preserve the exact resource source, respect their order and expose cycles; preparation steps do not change the current score or masquerade as employer-demand observations.

Report the evaluated collection scope and observed failures. These checks establish consistency and development evidence, not representative national demand, personal mastery or hiring prediction. Numeric model-quality targets, minimum role support and sensitivity tolerances still need an explicit validation policy.

## 8. Decisions to present to the user

1. Approve demand-only v1 gap ordering, with TOPSIS deferred until meaningful sourced additional criteria and tradeoffs exist, or require investigation of a specific additional criterion before proceeding?
2. Approve equal posting contribution for role alignment/ranking, alongside binary requirement groups, explicit OR handling and preferred evidence kept separate? Confirm the same aggregation is used for selected-role alignment.
3. Approve descriptive topic-review counts/order initially, with a categorical low-demand label held until an explicit cutoff is agreed?
4. Approve target-role demand order plus provider-stated preparation for selected resources, keeping future-course annotations separate?

Remaining discovery/policy needs: role grouping and track association, eligible population rules for ambiguous experience/remote statements, sufficient collection scope and authorized budget, recurring snapshot meaning, unknown-term/coverage policy, required-versus-unspecified extraction rules, and development evidence for support thresholds. Research has not silently settled them.
