"""Span-extraction scoring and group bootstrap intervals (MODEL_PIPELINE_PLAN sections 3-4).

Spans are (type, start, end) tuples; a prediction counts only on exact type and offsets.
Zero denominators are None ("undefined"), never 0 or 1.
"""
import random
from collections import defaultdict


def prf(tp, fp, fn):
    p = tp / (tp + fp) if tp + fp else None
    r = tp / (tp + fn) if tp + fn else None
    f1 = 2 * tp / (2 * tp + fp + fn) if 2 * tp + fp + fn else None
    return {"tp": tp, "fp": fp, "fn": fn, "precision": p, "recall": r, "f1": f1}


def example_counts(gold, pred):
    """{type: [tp, fp, fn]} for one example; gold and pred are sets of (type, start, end)."""
    out = defaultdict(lambda: [0, 0, 0])
    for t, *_ in gold | pred:
        out[t]
    for span in gold | pred:
        c = out[span[0]]
        c[0 if span in gold and span in pred else 1 if span in pred else 2] += 1
    return dict(out)


def add_counts(total, counts):
    for t, (tp, fp, fn) in counts.items():
        row = total.setdefault(t, [0, 0, 0])
        row[0] += tp; row[1] += fp; row[2] += fn
    return total


def micro(total):
    return prf(*(sum(v[i] for v in total.values()) for i in range(3)))


def per_type(total):
    return {t: prf(*v) for t, v in sorted(total.items())}


def by_group(per_example, groups):
    """Sum example counts into one count table per source group."""
    out = {}
    for counts, g in zip(per_example, groups):
        add_counts(out.setdefault(g, {}), counts)
    return out


def interval(group_totals, extra=None, n=2000, seed=0, min_groups=10, stat=lambda t: micro(t)["f1"]):
    """95% percentile bootstrap over source groups.

    `extra` is a second system's group table (same groups) for a paired difference (extra - first).
    """
    names = sorted(group_totals)
    if len(names) < min_groups:
        return {"status": "insufficient_groups", "groups": len(names), "min_groups": min_groups}
    rng = random.Random(seed)
    values, undefined = [], 0
    for _ in range(n):
        picked = [names[rng.randrange(len(names))] for _ in names]
        a = stat_of(group_totals, picked, stat)
        b = stat_of(extra, picked, stat) if extra is not None else None
        v = a if extra is None else (None if a is None or b is None else b - a)
        if v is None:
            undefined += 1
        else:
            values.append(v)
    if not values:
        return {"status": "undefined", "groups": len(names), "resamples": n, "undefined_replicates": undefined}
    values.sort()
    lo, hi = values[int(0.025 * len(values))], values[min(len(values) - 1, int(0.975 * len(values)))]
    return {"status": "ok", "groups": len(names), "resamples": n, "seed": seed, "unit": "split_group_id",
            "lower": lo, "upper": hi, "undefined_replicates": undefined}


def stat_of(group_totals, picked, stat):
    total = {}
    for g in picked:
        add_counts(total, group_totals.get(g, {}))
    return stat(total)
