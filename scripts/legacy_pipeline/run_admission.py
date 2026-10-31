"""Run local P2A admission over a frozen raw-v2 JobStreet release."""
import argparse
import hashlib
import importlib.metadata
import json
import os
import platform
import sys
from pathlib import Path

import numpy as np

from .classify_jobs import TransformersZeroShotClassifier
from .contracts import CLASSIFIER_MODEL, EXTRACTOR_MODEL, RETRIEVER_MODEL
from .extract import Gliner2Extractor
from .runner import run_admission_release
from .taxonomy import EscoTaxonomy, ExactAndSemanticRetriever, SentenceTransformerIndex


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_RAW_RELEASE = "jobstreet-2026-10-recovered-reconciliation-raw-v2"
TAXONOMY_VERSION = "esco-v1.2.1-occupations-en"


def _sha256(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _verify_snapshot(model_dir, model):
    metadata = Path(model_dir) / ".cache" / "huggingface" / "download" / "config.json.metadata"
    if not metadata.is_file():
        raise RuntimeError("pinned_model_snapshot_metadata_missing:" + model["id"])
    actual = metadata.read_text(encoding="utf-8").splitlines()[0].strip()
    if actual != model["revision"]:
        raise RuntimeError("pinned_model_revision_mismatch:" + model["id"])
    weight = Path(model_dir) / "model.safetensors"
    tokenizer = Path(model_dir) / "tokenizer.json"
    if not weight.is_file() or not tokenizer.is_file():
        raise RuntimeError("pinned_model_artifacts_missing:" + model["id"])
    return {"id": model["id"], "revision": actual,
            "model_safetensors_sha256": _sha256(weight),
            "tokenizer_json_sha256": _sha256(tokenizer)}


def _build_extractor_schema(model):
    return model.create_schema().entities({
        "duties": "Principal tasks and responsibilities performed by the person hired for this vacancy",
        "mandatory_experience": "Minimum or required prior work experience for the applicant",
        "preferred_experience": "Preferred or advantageous prior experience, not a mandatory condition",
        "seniority_requirement": "Explicit senior, lead, principal, or other applicant seniority requirement",
        "work_location": "The stated physical work location or geographic restriction for the vacancy",
        "internship_evidence": "Text explicitly saying this vacancy is an internship, student placement, or OJT",
    }).build()


def _load_components():
    os.environ["HF_HUB_OFFLINE"] = "1"
    os.environ["TRANSFORMERS_OFFLINE"] = "1"
    from gliner2 import GLiNER2
    from sentence_transformers import SentenceTransformer
    import torch
    from transformers import pipeline

    torch.set_num_threads(max(1, min(8, os.cpu_count() or 1)))

    model_paths = {
        "extractor": ROOT / "models" / "gliner2-base-v1",
        "retriever": ROOT / "models" / "all-mpnet-base-v2",
        "classifier": ROOT / "models" / "deberta-v3-base-zeroshot-v2.0",
    }
    model_specs = {"extractor": EXTRACTOR_MODEL, "retriever": RETRIEVER_MODEL,
                   "classifier": CLASSIFIER_MODEL}
    artifact_metadata = {
        name: _verify_snapshot(model_paths[name], model_specs[name]) for name in model_paths
    }

    gliner_model = GLiNER2.from_pretrained(str(model_paths["extractor"]), local_files_only=True)
    extractor = Gliner2Extractor(
        gliner_model,
        version=EXTRACTOR_MODEL["id"] + "@" + EXTRACTOR_MODEL["revision"],
        schema=_build_extractor_schema(gliner_model),
    )

    taxonomy_path = ROOT / "data" / "references" / "esco" / "v1.2.1" / "occupations.jsonl"
    taxonomy = EscoTaxonomy.load(taxonomy_path, version=TAXONOMY_VERSION)
    embedding_model = SentenceTransformer(
        str(model_paths["retriever"]), device="cpu", local_files_only=True
    )
    cache_path = ROOT / "models" / "esco-v1.2.1-mpnet-e8c3b32.npy"
    cache_meta_path = cache_path.with_suffix(".json")
    cache_identity = {
        "taxonomy_sha256": _sha256(taxonomy_path),
        "encoder_revision": RETRIEVER_MODEL["revision"],
        "sentence_transformers_version": importlib.metadata.version("sentence-transformers"),
        "occupation_count": len(taxonomy.occupations),
        "max_seq_length": embedding_model.max_seq_length,
    }
    cached_embeddings = None
    if cache_path.is_file() and cache_meta_path.is_file():
        try:
            cache_meta = json.loads(cache_meta_path.read_text(encoding="utf-8"))
            if all(cache_meta.get(key) == value for key, value in cache_identity.items()) \
                    and cache_meta.get("embeddings_sha256") == _sha256(cache_path):
                cached_embeddings = np.load(cache_path, allow_pickle=False)
        except (OSError, ValueError, json.JSONDecodeError):
            cached_embeddings = None
    if cached_embeddings is None:
        cached_embeddings = embedding_model.encode(
            [row["label"] + ". " + row["definition"] for row in taxonomy.occupations],
            convert_to_numpy=True, normalize_embeddings=True,
            batch_size=64, show_progress_bar=True,
        )
        temp_cache = cache_path.with_name(cache_path.name + ".tmp.npy")
        with temp_cache.open("wb") as handle:
            np.save(handle, cached_embeddings, allow_pickle=False)
        os.replace(str(temp_cache), str(cache_path))
        cache_identity["embeddings_sha256"] = _sha256(cache_path)
        temp_meta = cache_meta_path.with_name(cache_meta_path.name + ".tmp")
        temp_meta.write_text(json.dumps(cache_identity, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        os.replace(str(temp_meta), str(cache_meta_path))
    semantic_index = SentenceTransformerIndex(
        embedding_model, taxonomy.occupations, embeddings=cached_embeddings
    )
    retriever = ExactAndSemanticRetriever(
        taxonomy, semantic_index,
        version=RETRIEVER_MODEL["id"] + "@" + RETRIEVER_MODEL["revision"],
    )

    zero_shot_pipeline = pipeline(
        "zero-shot-classification", model=str(model_paths["classifier"]),
        tokenizer=str(model_paths["classifier"]), device=-1, local_files_only=True,
    )
    classifier = TransformersZeroShotClassifier(
        zero_shot_pipeline,
        version=CLASSIFIER_MODEL["id"] + "@" + CLASSIFIER_MODEL["revision"],
    )
    libraries = {}
    for package in ("gliner2", "sentence-transformers", "transformers", "torch", "numpy"):
        libraries[package] = importlib.metadata.version(package)
    runtime = {
        "python": platform.python_version(), "platform": platform.platform(),
        "device": "cpu", "precision": "float32", "cpu_count": os.cpu_count(),
        "torch_num_threads": torch.get_num_threads(),
        "library_versions": libraries, "models": artifact_metadata,
        "taxonomy_sha256": _sha256(taxonomy_path),
        "taxonomy_occupation_count": len(taxonomy.occupations),
        "mpnet_max_seq_length": embedding_model.max_seq_length,
        "zero_shot_max_position_embeddings": zero_shot_pipeline.model.config.max_position_embeddings,
        "zero_shot_batch_size": classifier.batch_size,
    }
    return extractor, retriever, classifier, taxonomy, runtime


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw-release", default=DEFAULT_RAW_RELEASE)
    parser.add_argument("--output-release", default=None)
    args = parser.parse_args(argv)

    raw_root = ROOT / "data" / "job_collections" / args.raw_release
    raw_manifest = json.loads((raw_root / "manifest.json").read_text(encoding="utf-8"))
    release_id = args.output_release or (args.raw_release + "-p2a-auto-v1")
    output_root = ROOT / "data" / "job_collections" / release_id
    print("Loading pinned local models and indexing ESCO occupations on CPU...",
          file=sys.stderr, flush=True)
    extractor, retriever, classifier, taxonomy, runtime = _load_components()
    print("Models loaded; starting saved-data admission run.", file=sys.stderr, flush=True)
    manifest = run_admission_release(
        raw_root / "source_frame.jsonl", output_root,
        release_id=release_id, raw_release_id=args.raw_release,
        extractor=extractor, retriever=retriever, classifier=classifier,
        taxonomy_version=taxonomy.version,
        window_start=raw_manifest["window_start"], window_end=raw_manifest["window_end"],
        runtime_metadata=runtime,
    )

    from scripts.jobs.release import attach_admission_feedback
    feedback = {
        "release_id": release_id,
        "release_path": output_root.relative_to(ROOT).as_posix(),
        "release_sha256": manifest["release_sha256"],
        "raw_input_sha256": manifest["raw_input_sha256"],
        "policy_version": manifest["policy_version"],
        "model_versions": manifest["model_versions"],
        "taxonomy_version": manifest["taxonomy_version"],
        "count_unit_membership_sha256": manifest["count_unit_membership_sha256"],
        "input_postings": manifest["summary"]["input_postings"],
        "accepted_employment": manifest["summary"]["accepted_employment"],
        "accepted_internship": manifest["summary"]["accepted_internship"],
        "rejected": manifest["summary"]["rejected"],
    }
    attach_admission_feedback(raw_root, feedback)
    print(json.dumps({"release": str(output_root), "summary": manifest["summary"],
                      "release_sha256": manifest["release_sha256"]}, indent=2))


if __name__ == "__main__":
    main()
