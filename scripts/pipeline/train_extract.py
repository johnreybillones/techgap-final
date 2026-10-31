"""Step 2 of MODEL_PIPELINE_PLAN: fine-tune GLiNER2 on the train split, select on validation, test once.

Two stages, so the test file is never read while training or selecting:

    python scripts/pipeline/train_extract.py train --release RELEASE --model models/gliner2-base-v1 --run-id ft-v1
    python scripts/pipeline/train_extract.py evaluate --run-id ft-v1 --compare-run extraction-frozen-v1

`train` needs a GPU for a practical run (it also works on CPU for a smoke test with --max-train/--max-val).
It writes everything under data/evaluation/<run-id>/; weights go to data/training/<run-id>/ (not tracked).
"""
import argparse
import itertools
import json
import platform
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from scripts.pipeline import evaluate  # noqa: E402
from scripts.pipeline.run_extraction import (LABELS, THRESHOLDS, SEED, check_isolation, load_split, rows, run_model,  # noqa: E402
                                             score, sha, spans_from, write_jsonl)

# Bounded search from the plan: 2 encoder rates x 2 task-head rates.
GRID = list(itertools.product([5e-6, 1e-5], [2.5e-4, 5e-4]))


def precision_flags(choice):
    import torch
    if choice == "auto":
        choice = "bf16" if torch.cuda.is_available() and torch.cuda.is_bf16_supported() else "fp16" if torch.cuda.is_available() else "fp32"
    return choice, {"fp16": choice == "fp16", "bf16": choice == "bf16"}


def curve_metric(val, batch_size):
    """Per-epoch validation F1 at the model's default threshold (0.5); the trainer only reports loss."""
    def compute(model, _dataset):
        import torch
        model.eval()
        with torch.no_grad():
            raw = run_model(model, val["inputs"], 0.5, batch_size)
        m = evaluate.micro(score(val, [spans_from(r) for r in raw])[1])
        return {"val_micro_f1": m["f1"] or 0.0, "val_precision": m["precision"] or 0.0, "val_recall": m["recall"] or 0.0}
    return compute


def sweep(model, val, batch_size):
    raw = run_model(model, val["inputs"], min(THRESHOLDS), batch_size)
    results = [{"split": "val", "threshold": t, **evaluate.micro(score(val, [spans_from(r, t) for r in raw])[1])} for t in THRESHOLDS]
    best = max(results, key=lambda x: (x["f1"] or 0, x["precision"] or 0))
    return results, best["threshold"]


def plot_curves(history, path):
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        return False
    fig, axes = plt.subplots(1, 2, figsize=(10, 4))
    for cfg in sorted({h["config"] for h in history}):
        h = [x for x in history if x["config"] == cfg]
        tr = [x for x in h if x["kind"] == "train" and x.get("loss") is not None]
        ev = [x for x in h if x["kind"] == "eval"]
        axes[0].plot([x["step"] for x in tr], [x["loss"] for x in tr], alpha=0.4, label="train cfg%d" % cfg)
        axes[0].plot([x["step"] for x in ev], [x["eval_loss"] for x in ev], marker="o", label="val cfg%d" % cfg)
        axes[1].plot([x["epoch"] for x in ev], [x["val_micro_f1"] for x in ev], marker="o", label="cfg%d" % cfg)
    axes[0].set(title="Loss", xlabel="step"); axes[1].set(title="Validation micro F1 (threshold 0.5)", xlabel="epoch")
    axes[0].legend(fontsize=6); axes[1].legend(fontsize=6)
    fig.tight_layout(); fig.savefig(path, dpi=120); plt.close(fig)
    return True


def train_stage(args):
    import torch
    from gliner2 import GLiNER2
    from gliner2.training.trainer import ExtractorTrainer, TrainingConfig

    release, run = Path(args.release), Path(args.eval_root) / args.run_id
    manifest = json.loads((release / "manifest.json").read_text(encoding="utf-8"))
    if not manifest.get("training_ready"):
        raise SystemExit("release is not training_ready")
    check_isolation(release)
    run.mkdir(parents=True, exist_ok=False)
    weights = Path(args.weights_root) / args.run_id

    train_rows = rows(release / "gliner2_train.jsonl")[: args.max_train or None]
    val = load_split(release, "val")
    if args.max_val:
        val = {k: v[: args.max_val] for k, v in val.items()}
    # trainer reads files, so write the (possibly truncated) slices next to the weights
    weights.mkdir(parents=True, exist_ok=True)
    train_file, val_file = weights / "train.jsonl", weights / "val.jsonl"
    write_jsonl(train_file, train_rows)
    write_jsonl(val_file, val["rows"])

    precision, flags = precision_flags(args.precision)
    history, outcomes, configs = [], [], []
    for i, (enc_lr, task_lr) in enumerate(GRID[: args.max_configs]):
        cfg = TrainingConfig(output_dir=str(weights / ("cfg%d" % i)), experiment_name="cfg%d" % i, num_epochs=args.epochs,
                             batch_size=args.batch_size, eval_batch_size=2 * args.batch_size, encoder_lr=enc_lr, task_lr=task_lr,
                             weight_decay=0.01, eval_strategy="epoch", save_best=True, metric_for_best="eval_loss",
                             greater_is_better=False, early_stopping=True, early_stopping_patience=2, save_total_limit=args.epochs,
                             seed=SEED + 42, num_workers=0, report_to_wandb=False, **flags)
        configs.append({"config": i, "encoder_lr": enc_lr, "task_lr": task_lr, "precision": precision, **{
            k: getattr(cfg, k) for k in ("num_epochs", "batch_size", "weight_decay", "scheduler_type", "warmup_ratio",
                                         "max_grad_norm", "early_stopping_patience", "seed")}})
        try:
            model = GLiNER2.from_pretrained(args.model)
            trainer = ExtractorTrainer(model, cfg, compute_metrics=curve_metric(val, 2 * args.batch_size))
            summary = trainer.train(train_data=str(train_file), eval_data=str(val_file))
        except Exception as exc:  # failed or out-of-memory configurations are kept in the log
            outcomes.append({"config": i, "status": "failed", "error": repr(exc)[:500]})
            continue
        for h in summary["train_metrics_history"]:
            history.append({"config": i, "kind": "train", **{k: h.get(k) for k in ("step", "epoch", "loss", "learning_rate")}})
        for h in summary["eval_metrics_history"]:
            history.append({"config": i, "kind": "eval", **{k: h.get(k) for k in ("step", "eval_loss", "val_micro_f1", "val_precision", "val_recall")},
                            "epoch": (h.get("epoch") or 0) + 1})  # trainer counts epochs from 0
        outcomes.append({"config": i, "status": "ok", "best_eval_loss": summary["best_metric"], "epochs_run": summary["total_epochs"],
                         "seconds": summary["total_time_seconds"]})
        del trainer, model
        torch.cuda.empty_cache()

    ok = [o for o in outcomes if o["status"] == "ok"]
    if not ok:
        raise SystemExit("every configuration failed; see training_outcomes in the run folder")
    pick = min(ok, key=lambda o: o["best_eval_loss"])  # rule fixed in the plan: lowest validation loss
    best_dir = weights / ("cfg%d" % pick["config"]) / "best"

    model = GLiNER2.from_pretrained(str(best_dir))
    tuning, chosen = sweep(model, val, 2 * args.batch_size)  # threshold chosen on validation only
    write_jsonl(run / "training_history.jsonl", history)
    write_jsonl(run / "tuning_results.jsonl", tuning + [{"system": "finetuned_gliner2", "selected_threshold": chosen, "config": pick["config"],
                                                         "rule": "max val micro F1, precision tie-break"}])
    (run / "training_config.json").write_text(json.dumps({"grid": configs, "outcomes": outcomes, "selected": pick,
        "selection_rule": "lowest validation eval_loss over all configurations"}, indent=2, sort_keys=True), encoding="utf-8")
    weights_file = next(iter(sorted(best_dir.glob("*.safetensors"))), None)
    (run / "checkpoint_manifest.json").write_text(json.dumps({
        "base_model": args.model, "base_revision": manifest.get("model_revision"), "selected_checkpoint": str(best_dir),
        "weights_sha256": sha(weights_file) if weights_file else None, "selected_threshold": chosen, "config": pick["config"],
        "release_id": manifest["release_id"], "train_examples": len(train_rows), "val_examples": len(val["inputs"]),
        "python": platform.python_version(), "torch": torch.__version__, "device": "cuda" if torch.cuda.is_available() else "cpu",
        "precision": precision, "created_utc": datetime.now(timezone.utc).isoformat(),
        "lora": False, "regularization": ["weight_decay=0.01", "early_stopping(patience=2, on eval_loss)"]}, indent=2, sort_keys=True), encoding="utf-8")
    (run / "plots").mkdir(exist_ok=True)
    plotted = plot_curves(history, run / "plots" / "training_curves.png")
    print(json.dumps({"run": str(run), "selected_config": pick["config"], "best_eval_loss": pick["best_eval_loss"],
                      "selected_threshold": chosen, "plot": plotted}, sort_keys=True))


def group_table(split, spans_per_example):
    return score(split, spans_per_example)[2]


def evaluate_stage(args):
    from gliner2 import GLiNER2

    run = Path(args.eval_root) / args.run_id
    if (run / "result_manifest.json").exists():
        raise SystemExit("test already read for this run; start a new run id")
    ckpt = json.loads((run / "checkpoint_manifest.json").read_text(encoding="utf-8"))
    release = Path(args.release) if args.release else Path("data/pre_model") / ckpt["release_id"]
    test = load_split(release, "test")
    model = GLiNER2.from_pretrained(ckpt["selected_checkpoint"])
    thr = ckpt["selected_threshold"]
    preds = [spans_from(r, thr) for r in run_model(model, test["inputs"], thr, args.batch_size)]
    per, total, groups = score(test, preds)
    metrics = [{"system": "finetuned_gliner2", "split": "test", "scope": "micro", "examples": len(test["inputs"]), "groups": len(groups),
                "reference": "silver", **evaluate.micro(total)}]
    metrics += [{"system": "finetuned_gliner2", "split": "test", "scope": "type:" + t, **m} for t, m in evaluate.per_type(total).items()]
    intervals = [{"system": "finetuned_gliner2", "split": "test", "metric": "micro_f1",
                  **evaluate.interval(groups, n=args.resamples, seed=SEED, min_groups=args.min_groups)}]
    comparisons = []
    if args.compare_run:
        other = Path(args.eval_root) / args.compare_run
        saved = [json.loads(x) for x in (other / "predictions.jsonl").read_text(encoding="utf-8").splitlines() if x.strip()]
        for system in ("exact_dictionary", "frozen_gliner2"):
            by_row = {r["row"]: {tuple(s) for s in r["spans"]} for r in saved if r["system"] == system and r["split"] == "test"}
            other_groups = group_table(test, [by_row[i] for i in range(len(test["inputs"]))])
            comparisons.append({"split": "test", "metric": "micro_f1", "difference": "finetuned_gliner2 - " + system,
                                **evaluate.interval(other_groups, extra=groups, n=args.resamples, seed=SEED, min_groups=args.min_groups)})
    write_jsonl(run / "metrics.jsonl", metrics)
    write_jsonl(run / "intervals.jsonl", intervals)
    write_jsonl(run / "comparisons.jsonl", comparisons)
    write_jsonl(run / "predictions.jsonl", [{"system": "finetuned_gliner2", "split": "test", "row": i, "spans": sorted(p)} for i, p in enumerate(preds)])
    (run / "result_manifest.json").write_text(json.dumps({
        "run_id": args.run_id, "created_utc": datetime.now(timezone.utc).isoformat(), "release_id": ckpt["release_id"],
        "checkpoint_sha256": ckpt["weights_sha256"], "threshold": thr, "compared_with": args.compare_run,
        "tuning_sha256": sha(run / "tuning_results.jsonl"), "predictions_sha256": sha(run / "predictions.jsonl"),
        "metrics_sha256": sha(run / "metrics.jsonl"),
        "note": "labels are AI-checked silver; metrics are agreement with them, not verified accuracy"}, indent=2, sort_keys=True), encoding="utf-8")
    m = metrics[0]
    print("finetuned test P=%.3f R=%.3f F1=%.3f" % (m["precision"] or 0, m["recall"] or 0, m["f1"] or 0))
    for c in comparisons:
        print(c["difference"], {k: c.get(k) for k in ("status", "lower", "upper")})


def main(argv=None):
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="stage", required=True)
    for name in ("train", "evaluate"):
        p = sub.add_parser(name)
        p.add_argument("--run-id", required=True)
        p.add_argument("--eval-root", default="data/evaluation")
        p.add_argument("--batch-size", type=int, default=8)
    t, e = sub.choices["train"], sub.choices["evaluate"]
    t.add_argument("--release", required=True)
    t.add_argument("--model", required=True)
    t.add_argument("--weights-root", default="data/training")
    t.add_argument("--epochs", type=int, default=5)
    t.add_argument("--precision", default="auto", choices=["auto", "fp16", "bf16", "fp32"])
    t.add_argument("--max-configs", type=int, default=len(GRID))
    t.add_argument("--max-train", type=int, default=0, help="smoke test only")
    t.add_argument("--max-val", type=int, default=0, help="smoke test only")
    e.add_argument("--release", default=None)
    e.add_argument("--compare-run", default=None)
    e.add_argument("--resamples", type=int, default=2000)
    e.add_argument("--min-groups", type=int, default=10)
    args = ap.parse_args(argv)
    (train_stage if args.stage == "train" else evaluate_stage)(args)


if __name__ == "__main__":
    main()
