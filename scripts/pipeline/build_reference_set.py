"""Step 3 of MODEL_PIPELINE_PLAN (section 5): support and retrieval reference set.

    python scripts/pipeline/build_reference_set.py sample --release RELEASE --out data/reference/support-v1
    python scripts/pipeline/build_reference_set.py pool --release RELEASE --out data/reference/support-v1
    python scripts/pipeline/build_reference_set.py batches                                  # first pass
    python scripts/pipeline/build_reference_set.py batches --name batches-b --pairs-per-batch 150   # blind second pass
    python scripts/pipeline/build_reference_set.py compare   # agreement; writes adjudicate/ batches for disagreements
    python scripts/pipeline/build_reference_set.py merge     # judgments.jsonl and the stop-point counts

Queries are required job spans from checked validation and test annotations only, so train stays free of them.
Candidates are pooled from exact-term, TF-IDF and SBERT rankings (union, depth 20 each). Two AI agents label each
pooled pair blind to each other; an adjudicator settles disagreements. Passages outside the pool are "not judged",
so Recall@k is recall against pooled judgments.
Files holding job text are git-ignored like the release they come from; only manifests and counts are tracked.
"""
import argparse
import ast
import hashlib
import json
import random
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from scripts.legacy_pipeline.contracts import RETRIEVER_MODEL  # noqa: E402
from scripts.pipeline.run_extraction import rows, sha, write_jsonl  # noqa: E402

TRACKS = ("bscs_game", "bscs_is", "bsit_network", "bsit_web")
STRATA = TRACKS + ("general",)
SPLITS = {"val": 50, "test": 100}  # about 150 queries (plan section 5, open decision 4)
PER_POSTING = 6  # spreads queries over job groups for the group bootstrap
DEPTH = 20
SEED = 20261102
STOP = set("a an and are as at be by for from in into is it of on or the to with using use its their your our".split())
LABELS = ("supports", "does_not_support", "unresolved")
MIN_DISTINCT_REASONS = 0.5  # every first-pass file had at least 0.58; the stamped checks had at most 0.03


def tokens(text):
    return [t for t in re.findall(r"[a-z0-9][a-z0-9+#.]*", text.lower()) if t not in STOP]


def tracks_of(value):
    return ast.literal_eval(value) if isinstance(value, str) else list(value or [])


def load(release):
    release = Path(release)
    ann = rows(release / "annotations.jsonl")
    split_of = {r["split_group_id"]: r["split"] for r in rows(release / "split_index.jsonl")}
    jobs = {a["document_id"]: a["decision"] for a in ann if a["kind"] == "job" and a["disposition"] in ("accepted", "corrected")}
    docs = {d["document_id"]: d for d in rows(release / "documents.jsonl")}
    passages = {p["passage_id"]: p for p in rows(release / "passages.jsonl")}
    manifest = json.loads((release / "manifest.json").read_text(encoding="utf-8"))
    return ann, split_of, jobs, docs, passages, manifest


def candidates(ann, split_of, jobs, passages):
    """One candidate per distinct (posting, required requirement text) in validation and test."""
    out, seen = [], set()
    for a in sorted(ann, key=lambda x: (x["document_id"], x["passage_id"] or "")):  # job-level rows have no passage
        if a["kind"] != "span" or a["source_type"] != "job" or a["disposition"] not in ("accepted", "corrected"):
            continue
        split, job = split_of.get(a["split_group_id"]), jobs.get(a["document_id"])
        if split not in SPLITS or not job or job["relevance"] != "relevant":
            continue
        text = passages[a["passage_id"]]["text"]
        for sp in sorted(a["decision"]["spans"], key=lambda s: (s["start"], s["end"])):
            key = (a["document_id"], sp["text"].lower().strip())
            if sp["modality"] != "required" or key in seen:
                continue
            seen.add(key)
            tracks = sorted(job["tracks"])
            # a multi-track posting is stratified by its rarest track (game first) so thin tracks keep every query
            stratum = next((t for t in TRACKS if t in tracks), "general")
            qid = hashlib.sha256(("%s|%s|%d|%d" % (a["passage_id"], sp["type"], sp["start"], sp["end"])).encode("utf-8"))
            out.append({"query_id": qid.hexdigest()[:16],
                        "split": split, "stratum": stratum, "tracks": tracks, "document_id": a["document_id"],
                        "split_group_id": a["split_group_id"], "passage_id": a["passage_id"], "type": sp["type"],
                        "text": sp["text"], "clause": text[sp["clause_start"]:sp["clause_end"]], "start": sp["start"], "end": sp["end"]})
    return out


def allocate(pool, target, rng):
    """Equal share per stratum, capped by availability and PER_POSTING; leftovers go to strata that still have queries."""
    by_stratum = {}
    for s in STRATA:
        items = [q for q in pool if q["stratum"] == s]
        rng.shuffle(items)
        per_doc, kept = Counter(), []
        for q in items:
            if per_doc[q["document_id"]] < PER_POSTING:
                per_doc[q["document_id"]] += 1
                kept.append(q)
        by_stratum[s] = kept
    take = dict.fromkeys(STRATA, 0)
    left = target
    while left:
        open_ = [s for s in STRATA if take[s] < len(by_stratum[s])]
        if not open_:
            break
        for s in sorted(open_, key=lambda s: take[s]):
            if left and take[s] < len(by_stratum[s]):
                take[s] += 1
                left -= 1
    return [q for s in STRATA for q in by_stratum[s][: take[s]]]


def sample_stage(args):
    ann, split_of, jobs, _, passages, manifest = load(args.release)
    pool = candidates(ann, split_of, jobs, passages)
    rng = random.Random(SEED)
    picked = []
    for split, target in SPLITS.items():
        picked += allocate([q for q in pool if q["split"] == split], target, rng)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    write_jsonl(out / "queries.jsonl", picked)
    counts = {"available": dict(Counter("%s/%s" % (q["split"], q["stratum"]) for q in pool)),
              "selected": dict(Counter("%s/%s" % (q["split"], q["stratum"]) for q in picked)),
              "selected_by_type": dict(Counter("%s/%s" % (q["split"], q["type"]) for q in picked)),
              "selected_postings": dict(Counter("%s/%s" % (s, st) for s, st, _ in {(q["split"], q["stratum"], q["document_id"]) for q in picked})),
              "selected_groups": dict(Counter(s for s, _ in {(q["split"], q["split_group_id"]) for q in picked}))}
    write_manifest(out, {"stage": "sample", "release_id": manifest["release_id"], "seed": SEED, "targets": SPLITS,
                         "per_posting_cap": PER_POSTING, "queries_sha256": sha(out / "queries.jsonl"), "counts": counts})
    print(json.dumps(counts, indent=1, sort_keys=True))


def corpus_for(tracks, corpus):
    wanted = set(tracks) or set(TRACKS)  # general computing postings search all four tracks
    return [p for p in corpus if wanted & set(p["tracks"])]


def syllabus_corpus(docs, passages):
    out = []
    for p in sorted(passages.values(), key=lambda p: p["passage_id"]):
        if p["source_type"] != "syllabus":
            continue
        d = docs[p["document_id"]]
        out.append({"passage_id": p["passage_id"], "document_id": p["document_id"], "course_code": d.get("course_code"),
                    "course_title": d.get("course_title"), "field": p["field"], "heading": p.get("heading_context"),
                    "status": d.get("status"), "tracks": tracks_of(d.get("applicable_tracks")), "text": p["text"]})
    return out


def exact_rank(query, corpus):
    """Exact-term baseline: share of distinct query terms present in the passage, full phrase first. No aliases yet."""
    q = set(tokens(query))
    phrase = query.lower().strip()
    scored = []
    for p in corpus:
        hit = len(q & set(tokens(p["text"]))) / len(q) if q else 0
        if hit:
            scored.append((-(hit + (1 if phrase in p["text"].lower() else 0)), p["passage_id"]))
    return [pid for _, pid in sorted(scored)[:DEPTH]]


def dense_rank(qvec, corpus, matrix, index):
    import numpy as np
    ids = [p["passage_id"] for p in corpus]
    sims = matrix[[index[i] for i in ids]] @ qvec
    order = sorted(range(len(ids)), key=lambda i: (-float(sims[i]), ids[i]))[:DEPTH]
    if not np.all(np.isfinite(sims)):
        raise SystemExit("non-finite similarity")
    return [ids[i] for i in order], [float(sims[i]) for i in order]


def pool_stage(args):
    import numpy as np
    import sentence_transformers
    import sklearn
    from sentence_transformers import SentenceTransformer
    from sklearn.feature_extraction.text import TfidfVectorizer

    _, _, _, docs, passages, manifest = load(args.release)
    out = Path(args.out)
    queries = rows(out / "queries.jsonl")
    corpus = syllabus_corpus(docs, passages)
    index = {p["passage_id"]: i for i, p in enumerate(corpus)}
    texts = [p["text"] for p in corpus]

    tfidf = TfidfVectorizer(lowercase=True, token_pattern=r"[A-Za-z0-9][A-Za-z0-9+#.]*", sublinear_tf=True).fit(texts)  # fitted on the syllabus corpus (declared)
    t_mat = tfidf.transform(texts)
    model = SentenceTransformer(RETRIEVER_MODEL["id"], revision=RETRIEVER_MODEL["revision"], device=args.device)
    s_mat = model.encode(texts, batch_size=64, normalize_embeddings=True, convert_to_numpy=True)
    s_q = model.encode([q["text"] for q in queries], batch_size=64, normalize_embeddings=True, convert_to_numpy=True)
    if s_mat.shape[1] != model.get_sentence_embedding_dimension() or not np.all(np.isfinite(s_mat)):
        raise SystemExit("embedding check failed")
    t_q = tfidf.transform([q["text"] for q in queries])

    pooled, sizes = [], []
    for qi, q in enumerate(queries):
        sub = corpus_for(q["tracks"], corpus)
        sub_idx = [index[p["passage_id"]] for p in sub]
        t_sims = (t_mat[sub_idx] @ t_q[qi].T).toarray().ravel()
        t_order = sorted(range(len(sub)), key=lambda i: (-t_sims[i], sub[i]["passage_id"]))
        ranks = {"exact": exact_rank(q["text"], sub),
                 "tfidf": [sub[i]["passage_id"] for i in t_order[:DEPTH] if t_sims[i] > 0],
                 "sbert": dense_rank(s_q[qi], sub, s_mat, index)[0]}
        union = sorted({pid for r in ranks.values() for pid in r})
        sizes.append(len(union))
        pooled.append({"query_id": q["query_id"], "corpus_size": len(sub), "ranks": ranks, "pool": union})
    write_jsonl(out / "pool.jsonl", pooled)
    write_jsonl(out / "corpus.jsonl", corpus)
    sizes.sort()
    write_manifest(out, {"stage": "pool", "depth": DEPTH, "methods": ["exact", "tfidf", "sbert"],
                         "exact": "distinct query-term share, full phrase first; aliases not used",
                         "tfidf": "fitted on all prepared syllabus passages (declared), sublinear tf",
                         "sbert": RETRIEVER_MODEL, "sbert_dimension": int(s_mat.shape[1]), "device": args.device,
                         "versions": {"sentence_transformers": sentence_transformers.__version__, "sklearn": sklearn.__version__,
                                      "numpy": np.__version__},
                         "pairs": sum(sizes), "pool_size": {"min": sizes[0], "median": sizes[len(sizes) // 2], "max": sizes[-1]},
                         "corpus_passages": len(corpus), "pool_sha256": sha(out / "pool.jsonl"), "corpus_sha256": sha(out / "corpus.jsonl")})
    print(json.dumps({"queries": len(queries), "pairs": sum(sizes), "median_pool": sizes[len(sizes) // 2]}, sort_keys=True))


def passage_line(n, p):
    # compact for the agents: they answer with index n, which maps back through pool.jsonl order
    return "%d | %s | %s | %s" % (n, p["course_code"], p["field"], p["text"])


def batches_stage(args):
    """Labeling batches for the agents: each holds whole queries with their pooled passages.

    `--name batches` is the first pass; `--name batches-b` the blind second pass (smaller batches, same pairs)."""
    out = Path(args.out)
    queries = {q["query_id"]: q for q in rows(out / "queries.jsonl")}
    corpus = {p["passage_id"]: p for p in rows(out / "corpus.jsonl")}
    pooled = rows(out / "pool.jsonl")
    bdir = out / args.name
    bdir.mkdir(exist_ok=True)
    batch, size, n, chars = [], 0, 0, []

    def flush():
        nonlocal batch, size, n
        if batch:
            write_jsonl(bdir / ("batch-%03d.jsonl" % n), batch)
            chars.append(sum(len(json.dumps(x)) for x in batch))
            n += 1
        batch, size = [], 0

    for row in pooled:
        q = queries[row["query_id"]]
        item = {"query_id": q["query_id"], "requirement": q["text"], "type": q["type"], "clause": q["clause"],
                "passages": [passage_line(n, corpus[pid]) for n, pid in enumerate(row["pool"])]}
        if size + len(item["passages"]) > args.pairs_per_batch:
            flush()
        batch.append(item)
        size += len(item["passages"])
    flush()
    write_manifest(out, {"stage": args.name, "batches": n, "pairs_per_batch": args.pairs_per_batch, "batch_chars": chars,
                         "labels": LABELS})
    print(json.dumps({"batches": n, "total_chars": sum(chars), "max_chars": max(chars)}, sort_keys=True))


def check_rows(path, expected):
    """Validate one agent file: every expected pair exactly once, a known label, a reason. Returns {(qid, n): row}.

    Gate added after the support-check-v1 failure (checkers stamped 'accepted' by script with one generic reason):
    a file whose reasons are mostly duplicates is rejected and its batch rerun."""
    if not path.exists():
        return None, ["missing " + path.name]
    got, errors = {}, []
    for i, line in enumerate(x for x in path.read_text(encoding="utf-8").splitlines() if x.strip()):
        try:
            r = json.loads(line)
        except json.JSONDecodeError as exc:
            errors.append("%s row %d: not JSON (%s)" % (path.name, i, exc))
            continue
        key = (r.get("query_id"), r.get("n"))
        if key not in expected:
            errors.append("%s row %d: unknown pair %s" % (path.name, i, key))
        elif key in got:
            errors.append("%s row %d: duplicate pair %s" % (path.name, i, key))
        elif r.get("label") not in LABELS:
            errors.append("%s row %d: bad label %r" % (path.name, i, r.get("label")))
        elif not (r.get("reason") or "").strip():
            errors.append("%s row %d: no reason" % (path.name, i))
        else:
            got[key] = r
    errors += ["%s: no row for %s" % (path.name, k) for k in sorted(set(expected) - set(got))[:5]]
    distinct = len({r["reason"].strip().lower() for r in got.values()})
    if got and distinct < MIN_DISTINCT_REASONS * len(got):
        errors.append("%s: only %d distinct reasons for %d pairs (generic or generated)" % (path.name, distinct, len(got)))
    return got, errors


def load_pass(out, batch_dir, label_dir, suffix):
    """All labels of one pass, keyed by (query_id, n), with every file validated against its batch."""
    labels, problems = {}, []
    for batch in sorted((out / batch_dir).glob("batch-[0-9][0-9][0-9].jsonl")):  # not the *.out.jsonl beside them
        # label batches list a query's passages; adjudication batches hold one (query_id, n) pair per item
        expected = {(item["query_id"], n) for item in rows(batch)
                    for n in (range(len(item["passages"])) if "passages" in item else [item["n"]])}
        got, errors = check_rows(out / label_dir / (batch.stem + suffix), expected)
        problems += errors
        labels.update(got or {})
    return labels, problems


def kappa(pairs):
    """Cohen's kappa for two raters over the same items; None when chance agreement is 1."""
    n = len(pairs)
    observed = sum(a == b for a, b in pairs) / n
    ca, cb = Counter(a for a, _ in pairs), Counter(b for _, b in pairs)
    expected = sum(ca[k] * cb[k] for k in LABELS) / (n * n)
    return None if expected == 1 else (observed - expected) / (1 - expected)


def both_passes(out):
    first, p1 = load_pass(out, "batches", "labels", ".first.jsonl")
    second, p2 = load_pass(out, "batches-b", "labels-b", ".second.jsonl")
    if p1 + p2:
        print("\n".join((p1 + p2)[:40]))
        raise SystemExit("%d problems; rerun those batches first" % len(p1 + p2))
    if set(first) != set(second):
        raise SystemExit("the two passes cover different pairs")
    return first, second


def compare_stage(args):
    """Agreement between the blind passes; disagreements go to adjudication batches with both labels and reasons."""
    out = Path(args.out)
    first, second = both_passes(out)
    queries = {q["query_id"]: q for q in rows(out / "queries.jsonl")}
    corpus = {p["passage_id"]: p for p in rows(out / "corpus.jsonl")}
    pool = {r["query_id"]: r["pool"] for r in rows(out / "pool.jsonl")}
    keys = sorted(first)
    pairs = [(first[k]["label"], second[k]["label"]) for k in keys]
    confusion = Counter("%s|%s" % p for p in pairs)
    items = []
    for k in keys:
        if first[k]["label"] != second[k]["label"]:
            q = queries[k[0]]
            items.append({"query_id": k[0], "n": k[1], "requirement": q["text"], "type": q["type"], "clause": q["clause"],
                          "passage": passage_line(k[1], corpus[pool[k[0]][k[1]]]),
                          "label_a": first[k]["label"], "reason_a": first[k]["reason"],
                          "label_b": second[k]["label"], "reason_b": second[k]["reason"]})
    adir = out / "adjudicate"
    adir.mkdir(exist_ok=True)
    for i in range(0, len(items), args.pairs_per_batch):
        write_jsonl(adir / ("batch-%03d.jsonl" % (i // args.pairs_per_batch)), items[i:i + args.pairs_per_batch])
    stats = {"pairs": len(pairs), "agreement": sum(a == b for a, b in pairs) / len(pairs), "cohen_kappa": kappa(pairs),
             "confusion_first|second": dict(sorted(confusion.items())), "disagreements": len(items),
             "adjudication_batches": -(-len(items) // args.pairs_per_batch)}
    write_manifest(out, {"stage": "compare", **stats})
    print(json.dumps(stats, indent=1, sort_keys=True))


def merge_stage(args):
    """Final judgments: the shared label where both blind passes agree, else the adjudicator's label.
    An adjudicator 'unresolved' stays unresolved (gold-unresolved, never counted as negative)."""
    out = Path(args.out)
    first, second = both_passes(out)
    adjudicated, problems = load_pass(out, "adjudicate", "adjudicate", ".out.jsonl")
    if problems:
        print("\n".join(problems[:40]))
        raise SystemExit("%d adjudication problems" % len(problems))
    queries = {q["query_id"]: q for q in rows(out / "queries.jsonl")}
    pool = {r["query_id"]: r["pool"] for r in rows(out / "pool.jsonl")}
    judgments = []
    for k in sorted(first):
        a, b = first[k]["label"], second[k]["label"]
        if a != b and k not in adjudicated:
            raise SystemExit("no adjudication for %s" % (k,))
        q = queries[k[0]]
        judgments.append({"query_id": k[0], "passage_id": pool[k[0]][k[1]], "split": q["split"], "stratum": q["stratum"],
                          "split_group_id": q["split_group_id"], "label": a if a == b else adjudicated[k]["label"],
                          "source": "agreed" if a == b else "adjudicated", "first_label": a, "second_label": b,
                          "adjudication_reason": adjudicated[k]["reason"] if a != b else None})
    write_jsonl(out / "judgments.jsonl", judgments)
    by, supported = defaultdict(Counter), defaultdict(set)
    for j in judgments:
        cell = "%s/%s" % (j["split"], j["stratum"])
        by[cell][j["label"]] += 1
        if j["label"] == "supports":
            supported[cell].add(j["query_id"])
    counts = {"pairs_by_label": {k: dict(v) for k, v in sorted(by.items())},
              "queries_with_support": {k: len(v) for k, v in sorted(supported.items())},
              "queries": dict(Counter("%s/%s" % (q["split"], q["stratum"]) for q in queries.values())),
              "labels": dict(Counter(j["label"] for j in judgments)), "sources": dict(Counter(j["source"] for j in judgments))}
    write_manifest(out, {"stage": "merge", "pairs": len(judgments), "judgments_sha256": sha(out / "judgments.jsonl"), "counts": counts,
                         "note": "AI-agent silver labels; agreement between agents is not accuracy"})
    print(json.dumps(counts, indent=1, sort_keys=True))


def write_manifest(out, entry):
    path = out / "manifest.json"
    m = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
    m[entry.pop("stage")] = entry
    path.write_text(json.dumps(m, indent=2, sort_keys=True), encoding="utf-8")


def main(argv=None):
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="stage", required=True)
    stages = {"sample": sample_stage, "pool": pool_stage, "batches": batches_stage, "compare": compare_stage, "merge": merge_stage}
    for name in stages:
        p = sub.add_parser(name)
        p.add_argument("--release", default="data/pre_model/saved-pre-model-20261031-v4")
        p.add_argument("--out", default="data/reference/support-v1")
    sub.choices["pool"].add_argument("--device", default="cuda")
    sub.choices["batches"].add_argument("--name", default="batches", choices=["batches", "batches-b"])
    sub.choices["batches"].add_argument("--pairs-per-batch", type=int, default=200)
    sub.choices["compare"].add_argument("--pairs-per-batch", type=int, default=120)
    args = ap.parse_args(argv)
    stages[args.stage](args)


if __name__ == "__main__":
    main()
