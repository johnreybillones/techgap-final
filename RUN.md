# Model pipeline: GPU run, then the remaining stages

## A. GPU run: GLiNER2 fine-tuning (plan step 2)

Unzip into an empty folder (or over a clone of `dev`); run all commands from that folder.

1. Install (Python 3.10+; torch with CUDA from the host, Colab/Kaggle already have it):

       pip install "gliner2[local]==2.1.0" matplotlib

2. Base model: copy `models/gliner2-base-v1/` here, or use the hub id `fastino/gliner2-base-v1` for `--model`
   (needs internet; pinned revision f9634218e53580c56edf0de97ca1a7d3f1c2354e).
3. Check one configuration first (shows epoch time and memory):

       python scripts/pipeline/train_extract.py train --release data/pre_model/saved-pre-model-20261031-v4 --model fastino/gliner2-base-v1 --run-id ft-v1 --max-configs 1 --epochs 2

   If it works, delete the previous `data/evaluation/ft-v1/` and `data/training/ft-v1/`, then run the full search by dropping
   `--max-configs 1 --epochs 2`. Never reads the test file. Lower `--batch-size` (default 8) if memory runs out.
4. Only after step 3 finishes, test once (refuses to run twice for one run id):

       python scripts/pipeline/train_extract.py evaluate --run-id ft-v1 --compare-run extraction-frozen-v1

5. Keep `data/evaluation/ft-v1/` (small). Weights stay in `data/training/ft-v1/` (git-ignored; keep `cfg*/best`).
   Look at `plots/training_curves.png` and `tuning_results.jsonl` before reporting. If the fine-tuned model is not better
   on validation and test, say so and keep the frozen model as the candidate (plan section 3).

## B. Branch and PR

    git clone https://github.com/johnreybillones/techgap-final.git && cd techgap-final
    git checkout dev && git checkout -b feature/model-training
    # put data/evaluation/ft-v1/ in place, then
    git add data/evaluation/ft-v1 && git commit -m "feat: fine-tuned extractor run ft-v1" && git push -u origin feature/model-training
    # open a PR to dev

Do not commit `data/pre_model/*/*.jsonl`, `data/training/`, `models/` or `dist/` (raw-derived data and weights; ignored by git).
Syllabus JSON is already in the repo under `data/syllabi/`; the full v4 release (second zip) goes into `data/pre_model/`.

## C. Read before the next stages (all in `docs/`)

Order: `plan/PLANNED_DATA_FLOW.md` (what data goes in and out; owns every formula) ->
`plan/MODEL_PIPELINE_PLAN_2026-10-31.md` (this work: sections 5-11) ->
`research/COMPUTATIONAL_SCIENCE_AND_ML2_PIPELINE_CHANGES_2026-10-22.md` (requirements TC-01 to TC-12) ->
`plan/MODEL_EVALUATION_SOURCE_NOTES.md` (metric definitions) ->
`plan/PREMODEL_DATA_PREPARATION_PLAN_2026-10-24.md` (only for how the release files were made: sections 1, 5, 6).
`scripts/legacy_pipeline/contracts.py` holds the pinned retriever and support-model ids (read ids/revisions only).

## D. After the GPU run: the rest of the model (plan section 10, steps 3 to 5)

Go in order; do not start a step before the previous stop point is met. Put each new result in `data/evaluation/<run_id>/`
with the layout in plan section 4. Write what was built and decided into `MODEL_PIPELINE_PLAN_2026-10-31.md` only
(model detail lives there). Do not edit `PLANNED_DATA_FLOW.md` or the pre-model plan without a decision from the project owner.

1. **Close step 2.** Three-variant table (dictionary, frozen GLiNER2, fine-tuned) with intervals, curves, and train/validation/test
   side by side. Stop point: the table exists.
2. **Step 3, support and retrieval reference set (section 5).** Needs the full release (`documents.jsonl`, `passages.jsonl`,
   `annotations.jsonl`, `job_decisions.jsonl`). About 150 required-job-span queries from validation and test sources only,
   pooled candidates (exact/alias, TF-IDF, SBERT, depth 20), AI-agent labels plus a checker. Stop point: counts per track and class.
   **Ask the project owner before spending agent tokens** (estimate first).
3. **Step 4, retrieval and support (sections 6, 7).** Add `sentence-transformers` and `scikit-learn` to
   `scripts/requirements-pipeline.txt` when needed. Feature records, Recall@k for k in {5,10,20,40}, support rule vs. NLI
   (TC-09 paired comparison). Tune only on validation; both models stay frozen.
4. **Step 5, robustness and reproducibility (sections 8, 9).** About 20 AI-written controlled cases, subgroup cuts by track and
   source type, `scripts/pipeline/run_experiment.py`, README with commands and artifact schema.

Rules that apply throughout:
- Test files are read once per final run. Nothing is tuned or selected on test.
- Labels are AI-agent silver labels: call results "agreement with AI-checked reference labels", never accuracy or verified F1.
- Zero denominators are `undefined`; groups below the minimum are `insufficient_groups`; BSCS Game test is too small to report.
- Metrics never enter a coverage score, count or recommendation (data flow section 6).
- Keep the checks in `tests/pipeline/` passing: `pytest` and `ruff check . --select E9,F` must pass before a PR (CI runs both).
- Open decisions are in plan section 11 (epoch cap, minimum groups, number of queries and token budget); ask the owner.
