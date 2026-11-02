"""Step 1 of MODEL_PIPELINE_PLAN: dictionary baseline and frozen GLiNER2 on validation and test.

    python scripts/pipeline/run_extraction.py --release data/pre_model/saved-pre-model-20261031-v4 \
        --model models/gliner2-base-v1 --run-id extraction-frozen-v1

Order is fixed: build baseline from train, sweep the threshold on validation, write the choice to
tuning_results.jsonl, only then read the test file and predict. Works on CPU or CUDA (--device auto).
"""
import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from scripts.pipeline import baseline, evaluate  # noqa: E402

LABELS = ["technical_task", "technical_knowledge", "tool_technology"]
THRESHOLDS = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]  # 0.5 is the model default
SEED = 0


def rows(path):
    return [json.loads(x) for x in Path(path).read_text(encoding="utf-8").splitlines() if x.strip()]


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write_jsonl(path, items):
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.writelines(json.dumps(x, ensure_ascii=False, sort_keys=True) + "\n" for x in items)


def load_split(release, name):
    data = rows(release / ("gliner2_%s.jsonl" % name))
    groups = {r["row"]: r["split_group_id"] for r in rows(release / "split_index.jsonl") if r["split"] == name}
    gold = [{(t, e["start"], e["end"]) for t, v in r["output"]["entities"].items() for e in v} for r in data]
    return {"inputs": [r["input"] for r in data], "gold": gold, "groups": [groups[i] for i in range(len(data))], "rows": data}


def check_isolation(release):
    """Gate: no source group appears in more than one split."""
    seen = {}
    for r in rows(release / "split_index.jsonl"):
        if seen.setdefault(r["split_group_id"], r["split"]) != r["split"]:
            raise SystemExit("group %s appears in %s and %s" % (r["split_group_id"], seen[r["split_group_id"]], r["split"]))


def spans_from(result, min_conf=0.0):
    return {(t, e["start"], e["end"]) for t, items in result["entities"].items() for e in items if e["confidence"] >= min_conf}


def run_model(model, inputs, threshold, batch_size):
    out = model.batch_extract_entities(inputs, LABELS, batch_size=batch_size, threshold=threshold,
                                       include_confidence=True, include_spans=True)
    return out


def score(split, preds):
    per = [evaluate.example_counts(g, p) for g, p in zip(split["gold"], preds)]
    total = {}
    for c in per:
        evaluate.add_counts(total, c)
    return per, total, evaluate.by_group(per, split["groups"])


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--release", required=True)
    ap.add_argument("--model", required=True)
    ap.add_argument("--run-id", required=True)
    ap.add_argument("--eval-root", default="data/evaluation")
    ap.add_argument("--device", default="auto")
    ap.add_argument("--batch-size", type=int, default=16)
    ap.add_argument("--resamples", type=int, default=2000)
    ap.add_argument("--min-groups", type=int, default=10)
    args = ap.parse_args(argv)

    release, run = Path(args.release), Path(args.eval_root) / args.run_id
    manifest = json.loads((release / "manifest.json").read_text(encoding="utf-8"))
    if not manifest.get("training_ready"):
        raise SystemExit("release is not training_ready")
    check_isolation(release)
    run.mkdir(parents=True, exist_ok=False)

    import torch
    from gliner2 import GLiNER2
    device = "cuda" if args.device == "auto" and torch.cuda.is_available() else ("cpu" if args.device == "auto" else args.device)
    model = GLiNER2.from_pretrained(args.model).to(device)
    model.eval()

    train = rows(release / "gliner2_train.jsonl")
    dictionary = baseline.build(train)
    val = load_split(release, "val")

    # 1) validation: baseline and threshold sweep. Test is not read yet.
    base_val = score(val, [baseline.predict(dictionary, x) for x in val["inputs"]])
    raw_val = run_model(model, val["inputs"], min(THRESHOLDS), args.batch_size)
    tuning = []
    for t in THRESHOLDS:
        m = evaluate.micro(score(val, [spans_from(r, t) for r in raw_val])[1])
        tuning.append({"system": "frozen_gliner2", "split": "val", "threshold": t, **m})
    best = max(tuning, key=lambda x: (x["f1"] or 0, x["precision"] or 0))
    # ponytail: thresholds above the lowest one are applied by filtering confidences instead of re-running.
    tuning.append({"system": "frozen_gliner2", "selected_threshold": best["threshold"], "rule": "max val micro F1, precision tie-break"})
    write_jsonl(run / "tuning_results.jsonl", tuning)
    chosen = best["threshold"]

    # 2) frozen settings -> test, read once
    test = load_split(release, "test")
    base_test = score(test, [baseline.predict(dictionary, x) for x in test["inputs"]])
    raw_test = run_model(model, test["inputs"], chosen, args.batch_size)
    frozen_preds = [spans_from(r, chosen) for r in raw_test]
    frozen_test = score(test, frozen_preds)
    frozen_val = score(val, [spans_from(r, chosen) for r in raw_val])

    metrics, intervals, predictions = [], [], []
    for system, split_name, split, sc in (("exact_dictionary", "val", val, base_val), ("frozen_gliner2", "val", val, frozen_val),
                                          ("exact_dictionary", "test", test, base_test), ("frozen_gliner2", "test", test, frozen_test)):
        _, total, groups = sc
        metrics.append({"system": system, "split": split_name, "scope": "micro", "examples": len(split["inputs"]),
                        "groups": len(groups), "unit": "exact type+offsets", "reference": "silver", **evaluate.micro(total)})
        metrics += [{"system": system, "split": split_name, "scope": "type:" + t, **m} for t, m in evaluate.per_type(total).items()]
        intervals.append({"system": system, "split": split_name, "metric": "micro_f1",
                          **evaluate.interval(groups, n=args.resamples, seed=SEED, min_groups=args.min_groups)})
    comparison = {"split": "test", "metric": "micro_f1", "difference": "frozen_gliner2 - exact_dictionary",
                  **evaluate.interval(base_test[2], extra=frozen_test[2], n=args.resamples, seed=SEED, min_groups=args.min_groups)}
    for system, split_name, split, preds in (("exact_dictionary", "test", test, None), ("frozen_gliner2", "test", test, frozen_preds)):
        for i, text in enumerate(split["inputs"]):
            p = preds[i] if preds else baseline.predict(dictionary, text)
            predictions.append({"system": system, "split": split_name, "row": i, "spans": sorted(p)})

    write_jsonl(run / "metrics.jsonl", metrics)
    write_jsonl(run / "intervals.jsonl", intervals)
    write_jsonl(run / "comparisons.jsonl", [comparison])
    write_jsonl(run / "predictions.jsonl", predictions)
    (run / "split_manifest.json").write_text(json.dumps({
        "release_id": manifest["release_id"], "split_buckets": manifest["split_buckets"], "seed": manifest["split_seed"],
        "export_splits": manifest["counts"]["export_splits"], "group_overlap_check": "passed",
        "file_hashes": {n: sha(release / n) for n in ("gliner2_train.jsonl", "gliner2_val.jsonl", "gliner2_test.jsonl", "split_index.jsonl")}},
        indent=2, sort_keys=True), encoding="utf-8")
    config = {"model": args.model, "model_revision": manifest.get("model_revision"), "thresholds": THRESHOLDS, "selected_threshold": chosen,
              "labels": LABELS, "bootstrap": {"resamples": args.resamples, "seed": SEED, "min_groups": args.min_groups},
              "device": device, "batch_size": args.batch_size, "torch": torch.__version__}
    (run / "experiment_config.json").write_text(json.dumps(config, indent=2, sort_keys=True), encoding="utf-8")
    (run / "result_manifest.json").write_text(json.dumps({
        "run_id": args.run_id, "created_utc": datetime.now(timezone.utc).isoformat(), "release_id": manifest["release_id"],
        "config_sha256": sha(run / "experiment_config.json"), "tuning_sha256": sha(run / "tuning_results.jsonl"),
        "predictions_sha256": sha(run / "predictions.jsonl"), "metrics_sha256": sha(run / "metrics.jsonl"),
        "note": "labels are AI-checked silver; metrics are agreement with them, not verified accuracy"}, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps({"run": str(run), "selected_threshold": chosen}, sort_keys=True))
    for m in metrics:
        if m["scope"] == "micro":
            print(m["system"], m["split"], "P=%s R=%s F1=%s" % tuple(None if m[k] is None else round(m[k], 3) for k in ("precision", "recall", "f1")))


if __name__ == "__main__":
    main()
