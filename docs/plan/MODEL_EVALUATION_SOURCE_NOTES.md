# Model evaluation source notes

Verified against publisher documentation on 2026-10-22 (Asia/Manila). These notes establish technical feasibility, not measured TechGap performance. They do not establish which metrics the course assignment mandates; use the attached assignment for that determination.

## What GLiNER2 and SBERT actually return

- The selected `fastino/gliner2-base-v1` supports entity extraction, classification, and structured extraction; the publisher documents local fine-tuning. [Publisher model card](https://huggingface.co/fastino/gliner2-base-v1).
- GLiNER2's API can return extracted text, character offsets and confidence scores with `include_spans=True` and `include_confidence=True`. Its repository also documents full training and LoRA adapters. These are predictions/scores, not an automatic accuracy report. [Official repository](https://github.com/fastino-ai/GLiNER2).
- SBERT/Sentence Transformers encodes texts into embeddings and calculates pairwise similarities, including cosine. A cosine value measures geometric similarity; it is not a probability that a course teaches a competency. [Official similarity documentation](https://www.sbert.net/docs/sentence_transformer/usage/semantic_textual_similarity.html).

**Implication:** Both chosen models can supply predictions for evaluation, but neither supplies trustworthy project accuracy without an independently labeled evaluation dataset. Publisher examples and benchmark numbers cannot substitute for TechGap test results.

## Metrics that can be calculated and their prerequisites

| Task | Applicable metrics | Required evidence and implementation |
| --- | --- | --- |
| GLiNER2 technical-span extraction | Entity precision, recall, F1; per-type and micro/macro results; support counts | Human-labeled spans/types and held-out predictions; define exact span/type matching. Count unmatched predictions as false positives and missed gold spans as false negatives. This is a proposed evaluation protocol. |
| GLiNER2 context/modality classification | Accuracy, per-class precision/recall/F1, macro F1, confusion matrix | Human labels for the same units/classes; predictions at a fixed decision policy. For mixed/multilabel contexts use a documented multilabel protocol. |
| SBERT candidate retrieval | Recall@k, Precision@k, MRR@k, MAP@k and nDCG@k | Queries, evidence corpus, independently judged relevant evidence and a specified k. Evaluate whether valid evidence reaches the shortlist. |
| SBERT pair decision | Accuracy, precision, recall, F1, confusion matrix | Human-labeled matched/unmatched pairs plus a threshold chosen on development data and frozen for final test evaluation. This evaluates that binary decision, not directional educational support. |
| SBERT graded similarity | Pearson and Spearman correlations | Independent human similarity ratings for text pairs. Similarity ratings alone do not establish curriculum coverage. |

Sentence Transformers supplies `BinaryClassificationEvaluator` for labeled similar/dissimilar pairs, `EmbeddingSimilarityEvaluator` for human similarity scores, and `InformationRetrievalEvaluator` for query/corpus relevance judgments. Its binary evaluator exposes accuracy, precision, recall, F1 and average precision. Its similarity evaluator exposes Pearson/Spearman correlations. Its retrieval evaluator supports the listed ranking metrics. [Official evaluator reference](https://www.sbert.net/docs/package_reference/sentence_transformer/evaluation.html).

A confusion matrix requires actual and predicted labels; it counts classification outcomes. A cosine similarity matrix is a different artifact. [scikit-learn confusion matrix API](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.confusion_matrix.html).

## Conditional metrics and plots

- **ROC curve / ROC-AUC:** Feasible for a defined binary decision with positive/negative gold labels and continuous scores. Binary ROC-AUC accepts unthresholded decision scores, so calibrated probabilities are not mandatory. Retain scores for all evaluation cases; accepted extractions alone omit rejected/negative cases. AUC evaluates discrimination and does not prove calibration. [scikit-learn ROC-AUC API](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.roc_auc_score.html).
- **Training and validation loss curves:** Feasible if the team actually trains/fine-tunes a model and logs the selected loss over training steps/epochs and held-out validation data. Sentence Transformers documents training/evaluation datasets, loss functions, logging steps and TensorBoard/W&B callbacks. Frozen pretrained inference generates no project training history. Threshold tuning is not weight training. [Official training overview](https://www.sbert.net/docs/sentence_transformer/training_overview.html).
- **Clustering metrics:** If an explicit clustering experiment is added to embeddings, silhouette, Davies-Bouldin and Calinski-Harabasz assess cluster geometry; labeled cluster comparisons can use ARI/NMI. These assess clustering, not extraction or curriculum support. A descriptive topic review without clusters cannot report a meaningful silhouette score. [scikit-learn clustering evaluation](https://scikit-learn.org/stable/modules/clustering.html#clustering-performance-evaluation).
- **Regression errors:** MAE/MSE/RMSE/R-squared require a defined numerical prediction target and independent numerical truth. Similarity or alignment percentages do not automatically turn the pipeline into regression. The plan's arithmetic coverage/demand outputs are system indicators, not model accuracy metrics. [scikit-learn task-based metric guidance](https://scikit-learn.org/stable/modules/model_evaluation.html).

## Limits relevant to the plan

`DATA_FLOW_ACTUAL.md` also selects `cross-encoder/nli-deberta-v3-base` for P6, alongside rules. Its directional-support decisions need separate validation. GLiNER2 extraction and SBERT retrieval metrics cannot certify that stage or the final combined coverage decisions.

The plan explicitly treats checkpoint choices as candidates and reports no measured performance. All metrics above are technically attainable with appropriate tasks, labels and evaluation code; this is not evidence that the plan has already produced them. Preserve an untouched test set, tune thresholds on development data, and report fixed-threshold test results rather than presenting best test-set thresholds as unbiased final performance. These are evaluation recommendations, not claims of additional assignment requirements.
