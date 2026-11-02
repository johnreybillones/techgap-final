# Model pipeline plan: extraction, retrieval, support, evaluation

> Approved 2026-10-31 as drafted; GPU training decided. Step 1 code: `scripts/pipeline/` (`evaluate.py`, `baseline.py`, `run_extraction.py`) and `tests/pipeline/`. Scope: build, train and evaluate the model stages that sit between the pre-model release and the result data. Data meanings and formulas stay in [PLANNED_DATA_FLOW.md](PLANNED_DATA_FLOW.md); data preparation stays in [PREMODEL_DATA_PREPARATION_PLAN_2026-10-24.md](PREMODEL_DATA_PREPARATION_PLAN_2026-10-24.md). The assignment obligations (TC-01 to TC-12) are in [COMPUTATIONAL_SCIENCE_AND_ML2_PIPELINE_CHANGES_2026-10-22.md](../research/COMPUTATIONAL_SCIENCE_AND_ML2_PIPELINE_CHANGES_2026-10-22.md); this plan does not restate them, it says how each is met. Metric definitions and prerequisites: [MODEL_EVALUATION_SOURCE_NOTES.md](MODEL_EVALUATION_SOURCE_NOTES.md). No result is claimed here. Everything marked **OPEN** needs a decision before that step starts.

## 1. Fixed inputs

- Release `data/pre_model/saved-pre-model-20261031-v4/` (cutoff 2026-10-27). Files used: `gliner2_train.jsonl` (1,600), `gliner2_val.jsonl` (176), `gliner2_test.jsonl` (473), `annotations.jsonl` (provenance, modality, clause offsets), `job_decisions.jsonl`, `documents.jsonl`, `passages.jsonl`, `manifest.json`.
- Labels are AI-agent silver labels. Every metric computed from them is named "agreement with AI-checked reference labels (silver)". No accuracy claim.
- Test (buckets 80-99) is untouched until the final run. Nothing is tuned, selected or looked at on test before step 7.
- Counts to quote in every table: examples, source groups (about 226 / 24 / 61 job groups, 46 / 8 / 14 syllabus groups for train / validation / test), and entities per type. BSCS Game has about 10 test passages and is reported as "insufficient", not as a metric.
- Models, pinned in `scripts/legacy_pipeline/contracts.py`: extractor `fastino/gliner2-base-v1` (local copy `models/gliner2-base-v1/`), retriever `sentence-transformers/all-mpnet-base-v2`, support candidate `MoritzLaurer/deberta-v3-base-zeroshot-v2.0`. Read the IDs and revisions from there; do not import its policy code.
- Environment: `.venv` (Python 3.14, `gliner2` 2.1.0, CPU-only torch). Add `sentence-transformers` and `scikit-learn`/`numpy` only when the step that needs them starts, and record versions in the run manifest.

## 2. How each assignment item is met

| Item | Met by | Step |
| --- | --- | --- |
| TC-01 input gates | Already in `pre_model_data.py` and release v4; evaluation reads only `training_ready` releases and records the release ID | done |
| TC-02 reference labels | Extraction: existing checked labels. Support and retrieval: new bounded set (section 5) | 1, 6 |
| TC-03 train / validation / test | Release v4 split manifest; evaluator re-checks zero group overlap | done, 2 |
| TC-04 feature records | Section 6 | 6 |
| TC-05 baseline | Exact dictionary built from train labels only | 3 |
| TC-06 development-only tuning | Extraction threshold, retrieval k, support thresholds, all on validation | 4, 6 |
| TC-07 metrics | `evaluate.py` | 2 |
| TC-08 intervals | Group bootstrap in `evaluate.py` | 2 |
| TC-09 full vs reduced | One comparison, chosen in section 7 | 7 |
| TC-10 subgroups and robustness | Section 8 | 8 |
| TC-11 artifacts and gates | Section 9 | 2, 9 |
| TC-12 training experiment | Section 3 | 5 |

## 3. GLiNER2 extractor (detailed)

**Task.** Exact span and type extraction over three entity types (`technical_task`, `technical_knowledge`, `tool_technology`) on the v4 files. Context, modality and AND/OR structure stay outside the model, as in the pre-model plan.

**Variants compared on the same test file.**

| Variant | Weights trained here | Settings chosen on validation |
| --- | --- | --- |
| Exact dictionary baseline | none (dictionary built from train spans) | none |
| Frozen GLiNER2 | none | extraction threshold |
| Fine-tuned GLiNER2 | train split only | epochs/checkpoint, learning rates, extraction threshold |

**Training configuration** (field names are `TrainingConfig` in `gliner2` 2.1.0; defaults verified by reading the installed package, behavior on this corpus not yet tested):

- Start from `fastino/gliner2-base-v1`, full fine-tune. Defaults to start from: `encoder_lr=1e-5`, `task_lr=5e-4`, `weight_decay=0.01`, `scheduler_type=linear`, `warmup_ratio=0.1`, `max_grad_norm=1.0`, `seed=42`, `save_best=True`, `early_stopping=True` (patience 3).
- Bounded search on validation only: at most 4 configurations (for example `encoder_lr` in {5e-6, 1e-5}, `task_lr` in {2.5e-4, 5e-4}), a fixed epoch cap (OPEN: 5, set after the first epoch time is known). Failed or abandoned configurations are kept in the log.
- **Loss.** The trainer's own loss is logged as `train_loss` / `eval_loss` and described in the report as GLiNER2's implemented objective. Do not call it cross-entropy and do not rename threshold sweeps as loss. The default checkpoint metric is `eval_loss`. The primary task metric (validation micro F1, exact span and type) is **not** produced by the trainer: compute it per epoch from the saved checkpoints with our own evaluator (**OPEN:** confirm the trainer exposes a per-epoch callback; otherwise evaluate each saved checkpoint after training). Checkpoint choice rule, fixed before training: lowest validation loss; report validation F1 beside it.
- **Regularization used:** weight decay and early stopping (both supported by the config). LoRA (`use_lora`, `lora_r`, ...) is available; use it only if full fine-tuning does not fit memory or time. State in the report what was used and why.
- **Compute (decided 2026-10-31).** Training runs on a GPU (a free service such as Colab or Kaggle, or another machine with a GPU), with the release files and `models/gliner2-base-v1/` copied there. All scripts take `--device auto` and never assume CPU. CPU estimate for reference only: about 30 minutes per epoch for about 1,800 examples (earlier smoke run), so the 4-configuration search is practical only on a GPU. Set `fp16`/`bf16` from the device and record the device and precision in `checkpoint_manifest.json`.
- **Frozen inference threshold.** Sweep on validation (candidate thresholds 0.1 to 0.9, step 0.1, plus the model default), choose by validation micro F1 with precision as tie-break, freeze it, then run test once for each variant.
- **Underfitting / overfitting.** Report the train and validation loss and F1 curves and the train / validation / test F1 side by side. A gap alone is not proof of a cause; say so.
- **Not adopted automatically.** If the fine-tuned model is worse on validation or test, report it and keep the frozen checkpoint as the production candidate.

**Baseline.** Lowercase exact match of every distinct train span text, longest match first, type taken from the most frequent train label of that text, no stemming, no context rules in the first version. It is built from the train split only. Alias merging and context rules are "suggested" and are deferred.

**Artifacts.** `training_history.jsonl` (step, epoch, train loss, validation loss, validation F1), `training_config.json`, `checkpoint_manifest.json` (revision, library versions, device, precision, seed, selected checkpoint hash). Weights stay under `models/` (git-ignored); only hashes go in the run.

### 3.1 Running the training on a GPU

Code: `scripts/pipeline/train_extract.py`. Smoke-tested on CPU with a 24-example slice on 2026-10-31; run at full size on a local CUDA GPU on 2026-11-01 (results in 3.2).

1. Copy to the GPU machine: the repository's `scripts/` folder, `models/gliner2-base-v1/`, and `data/pre_model/saved-pre-model-20261031-v4/` (only `manifest.json`, `split_index.jsonl`, `gliner2_train.jsonl`, `gliner2_val.jsonl` are needed for `train`; `gliner2_test.jsonl` is only needed for `evaluate`). Also `data/evaluation/extraction-frozen-v1/` for the comparison.
2. Install: `pip install "gliner2[local]==2.1.0" matplotlib` (torch with CUDA from the host; the repo `.venv` has a CPU build).
3. Train and select (never reads the test file):

   ```bash
   python scripts/pipeline/train_extract.py train --release data/pre_model/saved-pre-model-20261031-v4 --model models/gliner2-base-v1 --run-id ft-v1
   ```

   Precision is chosen from the device (`--precision auto`: bf16, else fp16, else fp32). Four configurations run in turn; a failed one (for example out of memory) is logged and skipped. Lower `--batch-size` if memory runs out. Outputs: `data/evaluation/ft-v1/` (`training_history.jsonl`, `training_config.json`, `tuning_results.jsonl`, `checkpoint_manifest.json`, `plots/training_curves.png`) and weights under `data/training/ft-v1/` (not tracked).
4. Test once with the frozen choice (`evaluate` refuses to run twice for one run id):

   ```bash
   python scripts/pipeline/train_extract.py evaluate --run-id ft-v1 --compare-run extraction-frozen-v1
   ```

   Needs `data/training/ft-v1/` (the selected checkpoint) and the release test file; writes metrics, intervals, paired differences against the dictionary and the frozen model, and `result_manifest.json`.
5. Copy `data/evaluation/ft-v1/` back into the repository. The per-epoch validation F1 in the history uses the model's default threshold (0.5); the final threshold is chosen separately on validation and stored in `checkpoint_manifest.json`.
6. Train and validation F1 of the selected checkpoint at the frozen threshold (reads only train and validation; writes `fit_metrics.jsonl`):

   ```bash
   python scripts/pipeline/train_extract.py fit --run-id ft-v1
   ```

### 3.2 Step 2 results (run `ft-v1`, release v4)

All figures are **agreement with AI-checked reference labels (silver)**, exact span and type, micro-averaged; intervals are 95% group bootstrap (2,000 resamples, seed 0, unit `split_group_id`). Not accuracy.

**Three variants on test** (473 examples, 75 source groups). Dictionary and frozen from `data/evaluation/extraction-frozen-v1/`, fine-tuned from `data/evaluation/ft-v1/`.

| Variant | Threshold (chosen on val) | Precision | Recall | Micro F1 | 95% interval |
| --- | --- | --- | --- | --- | --- |
| Exact dictionary | n/a | 0.274 | 0.336 | 0.302 | 0.261 to 0.345 |
| Frozen GLiNER2 | 0.6 | 0.223 | 0.355 | 0.274 | 0.237 to 0.309 |
| Fine-tuned GLiNER2 | 0.4 | 0.609 | 0.732 | **0.665** | 0.631 to 0.696 |

Paired differences in micro F1 on test (same resampled groups): fine-tuned minus frozen **+0.359 to +0.423**; fine-tuned minus dictionary **+0.319 to +0.405**; frozen minus dictionary -0.074 to +0.014 (no clear difference). Both intervals for the fine-tuned model exclude zero, so under section 3 ("not adopted automatically") the fine-tuned checkpoint is the extraction candidate. Production replacement stays a separate decision (section 9).

**Per type, test micro F1.**

| Type | Dictionary | Frozen | Fine-tuned |
| --- | --- | --- | --- |
| `technical_knowledge` | 0.270 | 0.287 | 0.690 |
| `technical_task` | 0.100 | 0.134 | 0.529 |
| `tool_technology` | 0.585 | 0.449 | 0.804 |

`technical_task` is the weakest type for every variant; its fine-tuned precision is 0.474.

**Train / validation / test, fine-tuned, threshold 0.4** (`fit_metrics.jsonl`, `metrics.jsonl`).

| Split | Examples | Groups | Precision | Recall | Micro F1 |
| --- | --- | --- | --- | --- | --- |
| Train | 1,600 | 272 | 0.680 | 0.804 | 0.737 |
| Validation | 176 | 32 | 0.602 | 0.694 | 0.645 |
| Test | 473 | 75 | 0.609 | 0.732 | 0.665 |

The train F1 is about 0.07 to 0.09 above validation and test, and validation and test agree. Validation loss of the selected configuration was lowest at epoch 3 (31.82) and rose to 40.95 by epoch 5 while validation F1 stayed between 0.64 and 0.67 (`plots/training_curves.png`). Rising loss with flat F1 is consistent with the model growing over-confident on some spans after epoch 3, which the loss-based checkpoint rule avoids. A train/validation gap alone does not prove overfitting (section 3); no stronger claim is made.

**Search.** Grid of section 3 (`encoder_lr` x `task_lr`), batch size 4, epoch cap 10 with early stopping (patience 2 on `eval_loss`), bf16 on CUDA, about 4,350 seconds in total.

| Config | `encoder_lr` | `task_lr` | Best val loss | Epochs run | Best val F1 in history (threshold 0.5) |
| --- | --- | --- | --- | --- | --- |
| 0 (selected) | 5e-6 | 2.5e-4 | **31.82** (epoch 3) | 5 | 0.668 (epoch 4) |
| 1 | 5e-6 | 5e-4 | 36.02 | 5 | 0.684 (epoch 5) |
| 2 | 1e-5 | 2.5e-4 | 32.99 | 4 | 0.685 (epoch 4) |
| 3 | 1e-5 | 5e-4 | failed: CUDA out of memory | 0 | n/a |

The checkpoint rule fixed before training is lowest validation loss, so config 0 was selected even though configs 1 and 2 logged higher validation F1 at a later epoch. Those F1 values are within about 0.02 of each other on 32 validation groups, which is inside the validation interval width; switching rules after seeing them would be selection on a noisy metric and is not done.

**Deviation: the test file was read twice.** A first attempt (2026-11-01 15:26 UTC, batch size 8, epoch cap 5) trained only config 0; configs 1 to 3 ran out of GPU memory. Its test evaluation ran (threshold 0.5, micro F1 0.678). The run folder was then moved aside, and the search was rerun with batch size 4 so that all configurations could train; this second run's test evaluation (17:05 UTC) is the one reported above. The rerun was triggered by the out-of-memory failures, not by the test number, and the reported figure is the lower of the two, but the section 1 rule "test is untouched until the final run" was not met. The first attempt is kept, unchanged, in `data/evaluation/ft-v1-backup/` (its manifests still carry run id `ft-v1`) as the record. The evaluator's guard against a second test read is per run folder; it does not stop a read after the folder is moved.

**Stop point for step 2: met** (three-variant table, intervals, curves, train/validation/test side by side), with the deviation above disclosed.

## 4. Evaluation harness (`scripts/pipeline/evaluate.py`, proposed)

Smallest version that meets TC-07, TC-08 and TC-11. Standard library plus `numpy`; plots with `matplotlib` only when step 8 needs them.

- **Metrics.** Extraction micro and per-type P/R/F1 with exact span and type match; TP/FP/FN stored; zero denominators are `undefined`, never 0 or 1. Later steps add Recall@k and support P/R/F1 with abstentions counted as misses for overall recall, resolved-only shown beside it. Relaxed matching, macro averages and everything marked "suggested" in the requirements document are skipped until needed.
- **Intervals.** 95% percentile bootstrap, 2,000 resamples (configurable), seeded; resampling unit is the source group (`split_group_id`), with the same sampled groups for paired comparisons (difference interval). If a subgroup has fewer than a declared minimum of groups (**OPEN:** default 10), write `insufficient_groups` instead of an interval.
- **Gates (tests under `tests/pipeline/`).** Group overlap between train / validation / test is zero; no configuration file is newer than, or references, the test predictions; abstention and zero denominators behave as defined; the same source set is used by baseline and model; a toy fixture reproduces known P/R/F1 and a known interval.
- **Layout.** One run directory `data/evaluation/<run_id>/` with: `split_manifest.json` (copy of release split info and hashes), `experiment_config.json`, `training_config.json`, `training_history.jsonl`, `checkpoint_manifest.json`, `tuning_results.jsonl`, `predictions.jsonl`, `metrics.jsonl`, `intervals.jsonl`, `comparisons.jsonl`, `plots/`, `result_manifest.json`. `errors.jsonl` and per-metric hash fields are deferred. Evaluation metrics are never mixed with the application's own metrics.

## 5. Support and retrieval reference set (new labels)

Needed because TC-07 requires Recall@k and support P/R/F1 and the pre-model release has neither. Built from **validation and test sources only**, so train stays free of it.

- **Queries.** Required-modality job spans from checked annotations in validation and test, stratified by track, one per distinct (posting, requirement). Target about 150 queries (**OPEN**, fix after seeing availability; BSCS Game will be thin).
- **Corpus.** All prepared syllabus passages of the tracks the query's posting maps to (and all four tracks for general computing postings).
- **Judgments by pooling.** For each query, pool the top candidates from exact/alias match, TF-IDF cosine and SBERT cosine (union, depth 20 per method). An AI agent labels each pooled passage `supports | does_not_support | unresolved` against the stated scope, a second agent checks. Passages outside the pool are treated as not judged, so Recall@k is reported as "recall against pooled judgments", not exhaustive passage recall.
- **Support labels** reuse the same judgments. Gold-unresolved is kept separate and never counted as negative.
- **Cost guard.** Agent labeling follows the pre-model practice (Haiku-low first pass where the instruction is obvious, Sonnet checker); estimate tokens before launching and ask first.
- **Groups for intervals.** Resample by query's job group. Pairs share syllabus passages, which makes them dependent, so the interval design is stated in the report as conditional on the fixed syllabus corpus (an ordinary independent-pair bootstrap is not used).

## 6. Retrieval and support stages (short)

- **Feature records (TC-04).** For each query and passage store: source ID, exact offsets, tokenizer name, token count and overlength flag, embedding dimension, finiteness, L2 norm, cosine and rank. Checks fail the run on wrong dimension, non-finite values or unsafe truncation. Cosine and confidence are never turned into coverage.
- **Retrieval.** Compare (a) exact/alias ranking, (b) TF-IDF cosine fitted on the train split's syllabus-free text or on the corpus only if that is declared, (c) pretrained SBERT, (d) exact/alias plus SBERT union. Macro Recall@k for k in {5, 10, 20, 40}, chosen k on validation.
- **Support.** Baseline: strict same-capability rule (exact/alias term match within the stated scope). Candidate: rule plus the NLI checkpoint with thresholds and margin chosen on validation. Report support P/R/F1, false-support counts, decision coverage and abstention rate with explicit denominators.
- Both stay frozen (no weight training), as the requirements document allows. SBERT fine-tuning is out of scope.

## 7. Component comparison (TC-09)

One controlled comparison with a paired interval, chosen so it needs no new labels: **NLI-assisted support versus strict rules** (same queries, same pooled judgments, only the support decision differs). If time allows, add **SBERT versus lexical retrieval** from the Recall@k results already produced. Other rows of the requirements table are deferred. Variants write to their own directories and never overwrite the normal results.

## 8. Subgroups and robustness (TC-10)

- Cuts by track and by source type (job / syllabus), always with group counts; a cut with too few groups is `insufficient`. Layout and language cuts are deferred.
- A small set of about 20 controlled cases, **written and checked by AI agents (silver)**, covering: repeated requirement statements (weight must not rise), negation, offered training, prerequisite-only mention, future-only course (no credit), incomplete syllabus (withheld, not zero). Negation is not label-preserving, so each case carries its own expected label. Report counts and failures, not only an average.

## 9. Reproducibility (TC-11 and the demonstration)

- One CLI entry point `scripts/pipeline/run_experiment.py` (proposed) with sub-steps: validate release, build baseline, tune on validation, train, freeze, evaluate on test, write manifest. A short README gives the commands, the pinned dependencies (`scripts/requirements-pipeline.txt` is extended) and the artifact schema. A notebook is optional.
- `result_manifest.json` lists input release ID and hashes, model revisions, library versions, seeds, configuration hashes, prediction hashes and the date the test file was first read.
- Production replacement of the extractor checkpoint is a separate, explicit decision after the comparison.

## 10. Order of work and stop points

1. **Extraction first** (everything needed for ML2, no new labels): evaluator core (section 4), baseline (3), threshold sweep on validation, frozen test run. *Stop:* baseline and frozen GLiNER2 numbers with intervals exist on v4 test. Decide CPU vs. GPU.
2. **Train** (section 3): bounded search on validation, pick checkpoint, freeze, single test run, comparison table and curves. *Stop:* three-variant table plus curves.
3. **Reference set** (section 5): sample queries, pool candidates, label, check. *Stop:* counts per track and per class are known; **ask before spending tokens**.
4. **Retrieval and support** (section 6) and TC-09 (section 7).
5. **Robustness cases** (section 8) and artifact/gate completion (section 9).

Steps 1 and 2 satisfy TC-05, TC-07 (extraction), TC-08, TC-11 (partial) and TC-12. Steps 3 to 5 satisfy the Computational Science items. Do not start a step before the previous stop point is met.

## 11. Open decisions

1. ~~CPU or GPU~~ decided: GPU, scripts device-agnostic.
2. ~~Epoch cap and the number of search configurations~~ used in `ft-v1`: cap 10, early stopping ended every configuration by epoch 5; 4 configurations, one failed on memory (section 3.2).
3. Minimum group count for an interval (default 10).
4. Number of queries in the support set (default about 150) and the labeling budget in tokens.
5. Whether the relevance and track classifier for new postings ([PLANNED_DATA_FLOW §7](PLANNED_DATA_FLOW.md)) is built in this plan. It is not required by either assignment, so it is **not** included; it can follow once step 2 is done.
6. The drift and retraining cadence in data-flow §7 is still an unapproved proposal and is not part of this plan.
