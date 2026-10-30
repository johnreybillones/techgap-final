# Suggested pipeline changes for Computational Science and Machine Learning 2

Date: 2026-10-22 (Asia/Manila).

Baseline: [DATA_FLOW_ACTUAL.md](../plan/DATA_FLOW_ACTUAL.md), including P0–P10 and E1–E4.

Assessment sources:

- Computational Science: `C:/Users/Alfierey/Downloads/FINAL_PROJECT_-_Computational_Science(2).docx`.
- Machine Learning 2 (ML2): `C:/Users/Alfierey/Downloads/Machine_Learning_2-FINAL_PROJECT(3).pdf`, particularly pp. 2–3 (data preparation, training, optimization and generalization), p. 4 (technical methodology/results), and p. 6 (task-appropriate evaluation and leakage prevention).

Scope: technical changes to data, models, training, evaluation and reproducible pipeline execution. Paper preparation, literature-review deliverables, recording, submission and other non-pipeline work are excluded.

## 1. Scope and architectural decision

Retain the proposed processing chain:

```text
Validated job/syllabus releases
  -> text units
  -> GLiNER2 extraction
  -> concepts and requirement expressions
  -> SBERT retrieval
  -> rules and evaluated NLI support assessment
  -> Boolean coverage and aggregation
  -> priorities, recommendations and roadmaps
```

The main additions are reference labels, experimental baselines, evaluation code, statistical confidence intervals, controlled feature experiments, robustness checks and a bounded training/fine-tuning experiment for ML2. These extend development/evaluation around the pipeline; they do not require another production model or a major change to P0–P10.

The NLI checkpoint is already a candidate in the baseline plan. Its role must be evaluated independently. Neither assignment requires introducing an unrelated model family such as logistic regression, CNN, LSTM, Random Forest or XGBoost. Computational Science's evaluation changes do not alone require fine-tuning; ML2 additionally asks for actual model training, loss/optimization and training-versus-validation analysis. The proposed response is to fine-tune the existing GLiNER2 component rather than add a production stage. SBERT can initially remain pretrained; its similarity remains a retrieval signal rather than proof of directional support. The ML2 PDF does not explicitly require retraining every pretrained component.

All changes below are proposals for implementation. No model results, statistical intervals or performance improvements are claimed. Scope is limited to data processing, models, experiments and machine-readable results.

## 2. Change summary

| ID | Area | Suggested change | Technical impact | Status |
| --- | --- | --- | --- | --- |
| TC-01 | P0 input validation | Enforce usable-source and completeness gates; freeze the evaluated releases | Strengthen existing validation | **REQUIRED** (minimum) |
| TC-02 | E1 reference labels | Create independent source-linked labels for extraction, structure, retrieval and support | Annotation data and validation | **REQUIRED** (extraction + support minimum) |
| TC-03 | E2 partitions | Make development/training/validation/test roles explicit and prevent source leakage | Split manifest and checks | **REQUIRED** |
| TC-04 | P1–P5 features | Materialize reproducible features and validate tokenization, encoding and normalization | Existing stage outputs and checks | **REQUIRED** (minimum) |
| TC-05 | Experimental baselines | Implement simple task-matched baselines | Evaluation-only adapters | **REQUIRED** (at least one) |
| TC-06 | E3 tuning | Execute development-only setting selection and freeze the chosen configuration | Tuning runner | **REQUIRED** (thresholds only) |
| TC-07 | E4 metrics | Compute task-specific and end-to-end metrics against reference labels | Evaluation harness | **REQUIRED** (core metrics) |
| TC-08 | E4 uncertainty | Compute statistical confidence intervals and paired comparison intervals | Statistical evaluation | **REQUIRED** |
| TC-09 | Feature contribution | Run controlled full-versus-reduced experiments | Experimental configuration switches | **REQUIRED** (at least one) |
| TC-10 | Bias/robustness | Evaluate meaningful subgroups, difficult cases and controlled transformations | Evaluation suites | **REQUIRED** (minimum) |
| TC-11 | P10 reproducibility | Save predictions, metrics, splits, configurations and dependency checks | Evaluation artifacts and release gates | **REQUIRED** (minimum) |
| TC-12 | ML2 training experiment | Compare frozen and domain-adapted GLiNER2; log loss, optimization, regularization and generalization | Offline training workflow; same P2 interface | **REQUIRED** |

"Required" means the assignment obligation is not met without it (the *minimum* noted). Everything beyond that minimum is classed as **suggested** in §2.1. Where a later section (§3–§14) describes more than the minimum, §2.1 governs.

### 2.1 Required changes vs. suggested improvements

**Required now (minimum to satisfy the assignments):**

| ID | Required minimum |
| --- | --- |
| TC-01 | Fixed source versions; incomplete/failed extraction is withheld, never zero demand or 100% alignment. |
| TC-02 | Independent human-checked labels for technical-span extraction and support decisions (the tasks actually scored). No model-self-labels. |
| TC-03 | Explicit development/train/validation/test roles; group-aware split with zero source overlap; learned preprocessing fit on non-test data only; split manifest with seed and overlap check. |
| TC-04 | Stored feature records that reproduce source spans; embedding dimension/finiteness/norm checks; unsafe truncation flagged. |
| TC-05 | At least one simple baseline (exact/alias dictionary for extraction) on the same held-out data as the main approach. |
| TC-06 | Development-only threshold selection for GLiNER2 and NLI support; settings frozen before final test; no test-based tuning. |
| TC-07 | Extraction micro P/R/F1 (exact match), per-type P/R/F1, support P/R/F1 with abstentions counted, Recall@k for retrieval, with explicit denominators and sample counts; baseline-vs-improved table, curves and confusion-matrix plots for ML2. |
| TC-08 | 95% group-level bootstrap CIs (seeded) for the final summary metrics and for the baseline-vs-main difference; explicit "insufficient groups" state instead of a fake interval. |
| TC-09 | Controlled full-vs-reduced comparison for at least one claimed engineered feature (e.g., NLI-assisted support vs. strict rules, or SBERT vs. lexical retrieval), with paired CI. |
| TC-10 | Metrics split by at least track/role family, with counts; a small set of human-labeled perturbation cases (repeated statements, negation/offered training, future-only course, incomplete syllabus). |
| TC-11 | Saved splits, configs, predictions, metrics, intervals and a result manifest; automated checks for split isolation, no final-test tuning, and abstention/zero-denominator handling. |
| TC-12 | One real training run of GLiNER2 (bounded span/type extraction) on training groups; train/validation loss and primary metric curves; validation-selected checkpoint; frozen vs. fine-tuned vs. baseline comparison on locked test sources; comparison reported even if fine-tuning is worse. |

**Suggested only (not required now; defer):**

- TC-01: repairing every uncertain syllabus field beyond what is needed for the evaluated cases.
- TC-02: labels for requirement structure (AND/OR), concept normalization, full retrieval relevance sets, and end-to-end human-derived alignment/gap references.
- TC-03: fixed 70/30 ratio; class/family/layout stratification beyond reporting actual counts.
- TC-04: full persisted records for every stage (offsets, concept links, expression trees, exact/alias route ranks).
- TC-05: TF-IDF retrieval comparator; a support-decision procedure for retrieval-only baselines.
- TC-06: retrieval shortlist sweep `k = 5, 10, 20, 40`; margin tuning; tie-break analysis.
- TC-07: relaxed span matching, context/modality macro-F1, structure match rate, normalization correctness, gap-detection P/R/F1, alignment MAE, Pearson/Spearman, ROC-AUC/AP.
- TC-08: 2,000-resample count (configurable default); multiway/block resampling for dependent support pairs beyond declaring the limitation.
- TC-09: the remaining variant rows (heading context, action/object/tool qualifiers, alias normalization, AND/OR flattening).
- TC-10: subgroup cuts by language, layout, tool familiarity; remaining perturbation cases (paraphrase, heading loss, nested alternatives, broad-vs-specific, overlong passages).
- TC-11: the full `data/evaluation/<run_id>/` file tree and `errors.jsonl`; per-metric hash fields beyond config/split/prediction hashes.
- TC-12: LoRA, SBERT fine-tuning, multiple regularizers, wide hyperparameter search, downstream end-to-end effect analysis, baseline §1.1 and `analysis_config.json` edits, notebook packaging.

TC-01–TC-11 retain the Computational Science changes and supply much of ML2's data/evaluation work. TC-12 addresses ML2's additional training obligation; TC-03, TC-05–TC-07 and TC-11 below also specify the corresponding training partitions, comparisons, plots and artifacts. The statistical-CI and feature-contribution requirements originate in the Computational Science assessment; ML2 calls for suitable metrics and comparisons without prescribing those same statistical methods.

## 3. TC-01 — Enforce input-quality gates

Extend P0 so that every evaluation case resolves to a fixed job/syllabus source version and an explicit usability state.

- Verify hashes, selected posting versions, duplicate groups, component identities and track applicability.
- Repair defective syllabus records against source PDFs; retain uncertain page boundaries and fields as unresolved until verified.
- Preserve missing applicable academic components in completeness counts. Do not remove them to make a track appear complete.
- Separate usable positive evidence from eligibility for complete alignment or confirmed whole-scope gap calculations.
- Ensure empty/failed extraction cannot become zero demand, zero requirements or 100% alignment.

**Acceptance check:** incomplete inputs produce explicit withheld/qualified outputs. They cannot silently enter complete-score denominators or negative reference labels.

## 4. TC-02 — Build independent reference labels

Extend E1 with validated annotation records containing source/version IDs, exact evidence text/spans, task labels, annotator identity, adjudication state and label-schema version.

Required evaluation targets:

| Task | Reference labels |
| --- | --- |
| Extraction | Exact technical span boundaries and types |
| Context/modality | Technical versus incidental/prerequisite/offered-training context; required/preferred/unspecified and other applicable classes |
| Requirement structure | Independently assessable groups, action/object/tool/qualifiers, AND/OR relations and ambiguous structures |
| Normalization | Supported concept/alias links; distinct concepts that must remain separate |
| Retrieval | Relevant academic evidence passages for each requirement query within a defined corpus |
| Support | Supported, unsupported or unresolved comparison, with source/scope basis |
| End-to-end outputs | Human-derived requirement credit, alignment and confirmed-gap references for selected complete cases |

Model predictions may assist annotation, but must not serve as their own correctness labels. Review disputed cases and retain unresolved references separately. Include no-match cases and difficult negatives, not only obvious positive matches.

Retrieval relevance sets need sufficiently complete judgments for the declared corpus; an incomplete list of known positives must not be presented as exhaustive passage recall. Gold-unresolved support cases are not automatically unsupported cases.

**Acceptance check:** each scored prediction has an independently checked reference and a reproducible source link. Actual labeled counts and uncovered categories are available to the evaluator.

## 5. TC-03 — Implement explicit, leakage-resistant partitions

Retain the proposed 70% development / 30% held-out starting split where feasible, subject to actual source-group and class counts.

1. Group duplicate/near-duplicate advertisements and revisions before splitting. Keep revisions of an academic component together.
2. Partition job groups and academic components before constructing support pairs. Neither held-out source set may enter setting selection.
3. For frozen pretrained models, use development data for extraction thresholds, retrieval shortlist and support settings; treat final held-out data as test data.
4. For the ML2 training experiment (TC-12), partition the development portion into training/validation groups or use group-aware internal validation. Make this split explicit before training. Keep final test sources untouched. Do not invent a mandatory inner ratio; choose one based on available independent groups and labels, and preserve it in the split manifest.
5. Fit learned preprocessing, such as TF-IDF vocabulary/IDF, on the designated fitting partition. Do not fit on final-test documents. Freeze dictionaries/rules before final testing as well.
6. Preserve class/family/layout coverage where group constraints permit. Validate actual counts rather than assuming group splitting guarantees stratification.
7. Store source memberships, seeds, task-specific counts and overlap-check results. Insufficient or missing strata must remain explicit.

**Acceptance check:** zero prohibited source overlap, no test-dependent configuration selection, and an explicit role for every partition. The ratio alone is not evidence of sufficient evaluation data.

## 6. TC-04 — Materialize and validate features

Use the existing P1–P5 contracts to save actual feature records:

- Source-faithful text units, heading/parent context, language and exact offsets.
- GLiNER2 spans, context/modality labels and confidence scores.
- Canonical concept links and capability action/object/tool/qualifiers.
- Requirement expression trees and their source spans.
- Tokenizer identity, token counts, chunk boundaries and overlength state.
- MPNet embeddings, exact/alias candidate routes, cosine scores and ranks.

Keep the existing L2 normalization for nonzero embeddings. Validate vector dimension, finiteness and norm. Enforce model-specific input limits and flag unsafe truncation. Preserve technical punctuation and relation/negation context.

Do not apply continuous scaling to arbitrary category IDs. No additional standardization or min-max stage is necessary unless a newly evaluated component requires it. Confidence and cosine values must not be converted directly into curriculum coverage credit.

**Acceptance check:** stored features reproduce their source spans and declared encoding; identical input/configuration hashes reproduce equivalent features within a declared numerical tolerance.

## 7. TC-05 — Implement simple experimental baselines

Use baselines on the same tasks and source partitions as the main components.

| Task | Suggested baseline | Main comparison |
| --- | --- | --- |
| Extraction | Exact dictionary/alias matching with explicit context rules | GLiNER2 extraction |
| Extraction training (ML2) | Frozen GLiNER2 with validation-selected inference settings | Fine-tuned GLiNER2 on the same labeled tasks and locked test sources |
| Retrieval | Exact/alias lexical ranking; optionally TF-IDF cosine if a richer lexical comparator is needed | Pure SBERT and the deployed exact/alias-plus-SBERT union |
| Support | Strict same-capability and instruction-context rules | Rules plus the evaluated NLI candidate |

Start with the existing exact/alias/rule mechanisms. Add TF-IDF only if needed for a meaningful retrieval comparison. Baselines are experiment adapters, not mandatory new stages in the production pipeline.

For an end-to-end comparison, retain the same source populations, group logic and aggregation rules while replacing the component under study. A baseline that only performs retrieval cannot be compared directly with full-pipeline support F1 without specifying its support-decision procedure.

**Acceptance check:** at least one implemented simple baseline and the main approach produce comparable predictions on a common held-out task. Stage-specific baselines should isolate the components whose benefit is being evaluated.

## 8. TC-06 — Execute development-only tuning

Implement E3's setting search:

- GLiNER2 extraction/classification thresholds selected from development score boundaries.
- Retrieval shortlist candidates `k = 5, 10, 20, 40`, where the corpus permits, with exact/alias union and expansion behavior fixed.
- NLI support-score thresholds and margins, subject to the existing source/scope guards.
- Existing tie-breaking rules for selection, including their precision tradeoff.

Store candidate settings, development metrics, selected setting and resulting configuration hash. Freeze everything before final-test inference. If insufficient positive/negative examples prevent meaningful tuning, retain an unvalidated state instead of inventing a threshold.

For inference-only Computational Science comparisons, fine-tuning is not a prerequisite. For the combined ML2 scope, execute TC-12 as a separate training experiment; select its loss and hyperparameters on training/validation data. Threshold and shortlist tuning remain inference-parameter selection and must not be presented as weight training. Production adoption of a fine-tuned checkpoint depends on the measured comparison; checkpoint replacement is not automatic.

**Acceptance check:** selected settings can be traced to development evidence and are unchanged during final testing. No automatic numerical passing target is inferred from the coursework.

## 9. TC-07 — Compute the evaluation metrics

The Computational Science assessment requires suitable metrics with confidence intervals; it does not name a fixed metric list. ML2 requires task-appropriate evaluation and baseline/improved comparison, including plots; its classification P/R/F1/confusion-matrix and regression MAE/MSE/RMSE examples do not mandate regression. Use the following proposed task-specific set, with sample counts and 95% CIs for summary performance estimates.

| Task | Metrics to calculate | Scoring convention |
| --- | --- | --- |
| Technical extraction | Micro precision, recall and F1; per-type P/R/F1 | Exact source/span/type match; count each match once; relaxed matching is separate |
| Context/modality | Macro-F1 and per-class P/R/F1 with support counts; accuracy/confusion matrix for single-label tasks | Use multilabel scoring and per-label binary confusion matrices for overlapping context classes |
| Requirement structure | Exact group/tree match rate | Define structural equivalence before testing |
| Concept normalization | Correct concept links / assessable labeled links; unresolved rate | Distinguish wrong links from abstention |
| Retrieval | Macro Recall@k for evaluated shortlist sizes | Average per-query passage recall over queries with labeled relevant evidence; count zero-relevant queries separately |
| Support decisions | Support precision/recall/F1; false-support counts; confusion matrix for defined gold classes; decision coverage and abstention rate | Abstained gold-positive cases count as missed support for overall recall; also show resolved-only performance and abstention counts by gold class |
| End-to-end gaps | Gap-detection precision/recall/F1 | Compare confirmed gaps under the same complete evidence scope |
| End-to-end alignment | Mean absolute error in percentage points | Compare with human-derived reference scores using identical group/aggregation rules; count withheld outputs |

Core calculations:

```text
precision = TP / (TP + FP)
recall = TP / (TP + FN)
F1 = 2*TP / (2*TP + FP + FN)

Recall@k(query) = relevant retrieved passages / reference relevant passages
macro_Recall@k = mean(per-query Recall@k for defined queries)

decision_coverage = resolved decisions / all in-scope evaluation cases
abstention_rate = unresolved decisions / all in-scope evaluation cases

alignment_MAE_pp = mean(abs(predicted_percent - reference_percent))
```

For support, distinguish `FP/(TP+FP)` (false-discovery fraction) from `FP/(FP+TN)` (false-positive rate). Name the denominator, show abstained gold-negative cases separately, and do not treat gold-unresolved cases as negative truth. Persist TP/FP/FN/TN where meaningful and use an explicit undefined status for zero denominators.

Evaluate initial retrieval separately from all-evidence expansion; exhaustive retrieval must not hide poor top-k performance. Keep application alignment percentages and demand counts separate from predictive-quality metrics.

For ML2, also generate training/validation loss and task-metric curves from TC-12, relevant classification confusion-matrix plots, and a baseline-versus-improved metric table. Label each task/system/split and its sample count. Span extraction uses entity TP/FP/FN rather than fabricated true-negative counts. State per-type, micro and macro averaging explicitly, and report exact versus relaxed span matches separately.

Evaluate SBERT with Recall@k even when its weights stay frozen. Pearson/Spearman require independent graded similarity labels and are optional. ROC-AUC/AP require a defined scored binary task and are optional. No clustering metric is needed without a clustering task. The alignment MAE above compares against independent human reference calculations; it does not require introducing a regression model.

**Acceptance check:** baseline/main metrics are calculated from actual held-out predictions and references, with explicit denominators, unresolved/withheld counts and no substituted publisher benchmark scores.

## 10. TC-08 — Add statistical confidence intervals

Add a resampling evaluator for each selected summary metric and each paired baseline/main or ablation difference.

Proposed starting method: 95% percentile bootstrap intervals with a stored seed and 2,000 resamples. This resample count is a configurable engineering proposal, not an assignment-prescribed value.

1. Freeze model settings and final-test predictions first.
2. Resample independent source groups rather than individual correlated spans.
3. Recalculate the metric for each resample; retain interval endpoints at the 2.5th and 97.5th percentiles.
4. Use identical sampled groups for paired system comparisons and calculate the interval of their metric difference.
5. For support pairs sharing both jobs and academic components, use a validated multiway/block resampling design or an evaluation design with independent blocks. Do not apply an ordinary independent-pair bootstrap to dependent pairs.
6. Save resampling unit, repetitions, seed, undefined-replicate count and insufficiency state. Do not manufacture intervals when independent groups are inadequate.

These intervals measure uncertainty under the declared evaluation design. They do not repair query-selection bias. P7's lower/upper unresolved-evidence bounds remain a separate quantity and cannot satisfy the statistical-CI requirement.

**Acceptance check:** every selected final performance estimate has a computed CI or an explicit technical reason it cannot yet be estimated; missing CIs remain an unmet evaluation item.

## 11. TC-09 — Measure feature/component contribution

Run selected comparisons that isolate the proposed technical contribution:

| Full-pipeline feature | Controlled experimental variant | Main outcomes |
| --- | --- | --- |
| Heading/parent context | Remove that context from the relevant extractor input | Extraction/context F1; false support |
| Action/object/tool qualifiers | Reduce to technology mentions | Support F1; alignment error |
| Supported alias normalization | Disable alias merging | Concept-link correctness; missed support |
| SBERT retrieval | Substitute the fixed lexical baseline | Recall@k; end-to-end support recall |
| AND/OR requirement structure | Use a clearly defined flattened experimental representation | Group correctness; gap F1; alignment error |
| NLI-assisted support | Apply the strict-rule baseline instead | Support precision/recall; abstention; alignment error |

Choose the variants relevant to the contribution being tested; every row is not automatically required. Keep sources and labels fixed. Define whether variants are separately tuned on development data or use fixed settings; freeze that protocol before testing. Evaluate paired differences with CIs.

Experimental weakening must not overwrite normal result artifacts. Preserve variant IDs and separate output directories.

**Acceptance check:** the claimed benefit of an engineered feature/component is supported by a controlled measured comparison, or remains explicitly unproven. Improved results alone do not establish novelty relative to all prior work.

## 12. TC-10 — Add subgroup and robustness evaluation

Calculate applicable primary metrics by track/role family, source layout, language, frequent/unfamiliar tools and input-completeness state. Preserve actual group counts and overlapping memberships. Missing or small groups remain explicit; do not claim equal performance from insufficient evidence.

Add controlled test cases:

- Repeated requirement statements: demand/coverage weight must not increase.
- Harmless paraphrases and formatting changes: expected capability meaning stays the same.
- Heading loss: expose reduced structure and measure the effect.
- Negation, offered training and prerequisite-only mentions: expected support/requirement labels must change appropriately.
- Nested alternatives and task/tool composites: verify grouping and coverage credit.
- Broad related topics versus specific required tasks: measure false coverage.
- Overlong passages and incomplete syllabi: preserve unresolved/withheld behavior.
- Future-only course support: current alignment must receive no credit.

Use human-checked expected labels for transformations. Negation is not a label-preserving perturbation. Show metric changes and error counts rather than only aggregate accuracy.

**Acceptance check:** measured subgroup/robustness outputs identify failure locations, affected counts and downstream consequences. Criticality should consider false coverage and falsely confirmed gaps, not only average F1.

## 13. TC-11 — Add reproducible evaluation artifacts and gates

Extend the proposed `scripts/pipeline/evaluate.py` and `tests/pipeline/` rather than introducing a separate production architecture. Baseline adapters and experiment orchestration can be small supporting modules.

Proposed evaluation outputs:

```text
data/evaluation/<evaluation_run_id>/
  annotation_manifest.json
  split_manifest.json
  experiment_config.json
  training_config.json
  training_history.jsonl
  checkpoint_manifest.json
  tuning_results.jsonl
  predictions.jsonl
  metrics.jsonl
  intervals.jsonl
  comparisons.jsonl
  errors.jsonl
  plots/
  result_manifest.json
```

Each metric record should carry task, system/variant, dataset/split/config hashes, evaluation unit, numerator/denominator where applicable, estimate, interval method/endpoints, sample/source-group counts and unresolved/undefined state. Keep evaluation metrics distinct from P7's application `metrics.jsonl`.

For TC-12, retain training/validation loss and task metrics by epoch/step; optimizer/scheduler settings; model/library versions; device/precision; seed; selected checkpoint or adapter hashes; and early-stopping state. `checkpoint_manifest.json` may reference separately stored model weights rather than duplicate them. Preserve baseline/frozen/fine-tuned prediction identities and generated comparison tables/plots. Do not generate training-history records for frozen models as if they had been trained in this project.

Automated checks must verify source references and split isolation; deterministic Boolean/aggregation fixtures; reproducible settings; baseline/main task comparability; no final-test tuning; and correct handling of abstention, missing denominators and failed extraction.

## 14. TC-12 — Train an existing component for ML2

### 14.1 Minimal change and experimental target

Add an offline training workflow for the selected `fastino/gliner2-base-v1` candidate using the TC-02 technical-span/context labels. Start with a clearly bounded task, such as exact technical-span/type extraction; add contextual classification to training only where the labels and training schema support it. A proposed question is whether domain adaptation improves this task over the frozen checkpoint and exact/alias baseline. This is an experimental target, not an assumed improvement.

GLiNER2 supports local training and LoRA adapters in the [publisher repository](https://github.com/fastino-ai/GLiNER2). LoRA is a candidate for reducing trainable parameters; hardware feasibility, compatible dependency versions and checkpoint support must still be checked. The publisher's supported capability does not establish local memory/runtime or TechGap accuracy.

Keep P2's input/output contracts: source-faithful text/schema in, spans/classifications/confidences with source/model identity out. Only its selected checkpoint/adapter changes if evaluation supports adoption. Initially keep SBERT and the NLI candidate frozen and evaluate them independently. No additional production model is needed to produce the required training evidence. Fine-tuning SBERT is an alternative if a retrieval-training question and appropriate labels are selected, not an additional mandatory experiment; its [official training overview](https://www.sbert.net/docs/sentence_transformer/training_overview.html) describes dataset/loss/evaluator-based training.

### 14.2 Training procedure and configuration

1. Inspect the pinned model's supported training implementation and data schema. Convert independently checked annotations into its training format, with source IDs and exact spans preserved. Do not derive gold labels solely from the model's own predictions.
2. Use TC-03's explicit training/validation/test groups. Train weights/adapters on training records only. Select model settings, inference thresholds and checkpoints using validation evidence only; retain the final test set for the frozen comparison.
3. Record the actual architecture and trainable/frozen parameter scope. For LoRA, include target modules, rank, scaling and dropout where used. For all variants, retain checkpoint/revision, library versions and feature/tokenization policy.
4. Select and record the training implementation's actual loss and explain its relation to the labeled outputs. Record any component losses/weights for multitask training. Do not assume a generic cross-entropy formula matches GLiNER2's implemented objective; do not rename cosine similarity or threshold sweeps as training loss.
5. Specify the actual optimizer, learning rates, epochs, batch size/effective batch size, schedule/warmup, seed, device and precision. Compare a bounded, declared validation search rather than asserting arbitrary settings are optimal. Retain failed configurations and resource failures.
6. Log training/validation loss and the primary extraction metric across epochs/steps. Use a consistent validation protocol and a fixed metric direction for checkpoint selection. Training loss is not the final quality metric.
7. Evaluate applicable regularization, such as supported weight decay, LoRA/model dropout or validation-based early stopping. Record what was used and why. ML2's examples do not require every regularizer simultaneously; unsupported settings must not be invented.
8. Freeze selected weights/adapter, inference thresholds and configuration before final-test prediction. Do not choose which result to report based on the final-test ranking of multiple configurations.

### 14.3 Required measured comparisons

| Variant | Weight training in this project | Outputs to compare |
| --- | --- | --- |
| Exact/alias/context-rule baseline | None | Exact-span/type P/R/F1 and context metrics where the baseline defines those predictions |
| Frozen GLiNER2 | None | Same task metrics under validation-selected inference settings |
| Domain-adapted GLiNER2 | Training data only; validation-selected checkpoint | Same held-out metrics; training/validation loss and task-metric curves; training configuration |

Report test source/span/class counts, per-type and micro P/R/F1, relevant context metrics/confusion matrices, and paired metric-difference CIs under TC-08's valid resampling design. Discuss observed underfitting/overfitting from curves and comparable partition metrics; a train/test gap alone does not establish its cause.

When measuring downstream effects, hold retrieval, NLI/rule policy, group logic, source population and aggregation settings fixed across extractor variants. Report support/gap errors, abstentions, withheld outputs and alignment-reference error under TC-07. This isolates the extraction change instead of attributing every pipeline difference to fine-tuning.

If the fine-tuned variant performs worse, retain and expose that result. Keep the better validated production candidate under the declared selection policy; the training experiment need not force a new deployment checkpoint. Publisher pretraining statistics cannot substitute for these project measurements.

### 14.4 Integration and acceptance checks

Add a small training entry point such as proposed `scripts/pipeline/train_extract.py`, reusing existing contracts/configuration/annotation utilities. This filename is a proposal, not an existing runnable module. Extend `evaluate.py` for checkpoint comparisons rather than creating a second scoring architecture.

Provide a reproducible notebook or CLI invocation path that runs data validation, the bounded training/evaluation experiment and a traceable extraction-to-analysis example. Pin dependencies and supply data/checkpoint locations, commands and expected artifact schemas. No frontend/backend deployment is required for this technical demonstration.

Update baseline §1.1's “custom fine-tuning is not required initially” statement to distinguish the optional production adaptation policy from this proposed ML2 training experiment. Extend E1–E4 and `analysis_config.json` with the training partition/configuration, checkpoint and evaluation references. These are proposed baseline edits; this change document does not itself modify `DATA_FLOW_ACTUAL.md`.

**Acceptance check:** an actual training run produces saved weights/adapter, genuine training/validation histories, validation-selected settings and final held-out comparisons against the frozen/baseline variants. Data leakage, missing labels, failed training or unmeasured results remain explicit blockers to claiming this technical requirement complete. Threshold tuning alone does not pass this check.

## 15. Implementation order and completion boundary

1. Freeze usable sources and create independent reference labels: TC-01–TC-02.
2. Freeze partitions and validate materialized features: TC-03–TC-04.
3. Implement baselines; train and select the ML2 experiment using training/validation data; execute validation-only inference tuning: TC-05–TC-06 and TC-12.
4. Freeze settings, run final inference, compute metrics/CIs: TC-07–TC-08.
5. Run predefined contribution and robustness experiments: TC-09–TC-10.
6. Verify artifacts and release gates: TC-11.

Technical completion requires actual baseline/main predictions, measured held-out metrics with uncertainty, empirical feature comparisons, robustness results, a reproducible analytical demonstration and ML2's training/optimization/generalization evidence. Editing the processing plan alone does not complete those experiments. Train an existing component for the proposed ML2 study; adopt changed production weights only when the evaluated selection policy supports them. Another production model or a major P0–P10 redesign is not the default remedy.
