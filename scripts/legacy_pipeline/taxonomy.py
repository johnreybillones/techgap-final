"""Validated local ESCO occupation reference and exact alias index."""
import json
from dataclasses import dataclass
from pathlib import Path

from .text import normalize_text


@dataclass(frozen=True)
class EscoTaxonomy:
    version: str
    occupations: tuple
    alias_index: dict

    @classmethod
    def load(cls, path, *, version):
        path = Path(path)
        if not path.is_file() or not version:
            raise ValueError("missing_esco_release_or_version")
        rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
        uris = set()
        index = {}
        normalized = []
        for row in rows:
            if not all(row.get(name) for name in ("uri", "label", "definition")):
                raise ValueError("invalid_esco_occupation")
            if row["uri"] in uris:
                raise ValueError("duplicate_esco_uri:" + row["uri"])
            uris.add(row["uri"])
            item = {"uri": row["uri"], "label": row["label"], "definition": row["definition"],
                    "aliases": list(row.get("aliases", []))}
            normalized.append(item)
            for label in [item["label"]] + item["aliases"]:
                index.setdefault(normalize_text(label).casefold(), []).append(item)
        if not normalized:
            raise ValueError("empty_esco_release")
        return cls(version=version, occupations=tuple(normalized), alias_index=index)

    def exact(self, value):
        return list(self.alias_index.get(normalize_text(value).casefold(), []))


class ExactAndSemanticRetriever:
    """Union exact aliases with a provided pinned local embedding index."""
    def __init__(self, taxonomy, semantic_index, *, version):
        self.taxonomy = taxonomy
        self.semantic_index = semantic_index
        self.version = version

    def retrieve(self, title, passages, limit):
        exact = self.taxonomy.exact(title)
        semantic = self.semantic_index.search("\n".join([title] + list(passages)), limit=limit)
        merged = []
        seen = set()
        for row in exact + semantic:
            if row["uri"] not in seen:
                seen.add(row["uri"])
                merged.append(row)
        return merged


class SentenceTransformerIndex:
    """In-memory MPNet occupation index over normalized local embeddings."""
    def __init__(self, model, occupations, *, embeddings=None):
        self.model = model
        self.occupations = list(occupations)
        if not self.occupations:
            raise ValueError("empty_esco_occupation_index")
        if embeddings is None:
            texts = [row["label"] + ". " + row["definition"] for row in self.occupations]
            embeddings = model.encode(
                texts, convert_to_numpy=True, normalize_embeddings=True,
                batch_size=64, show_progress_bar=False,
            )
        if len(embeddings) != len(self.occupations):
            raise ValueError("esco_embedding_count_mismatch")
        self.embeddings = embeddings

    def search(self, query, *, limit):
        query_embedding = self.model.encode([query], convert_to_numpy=True, normalize_embeddings=True)[0]
        scored = []
        for row, embedding in zip(self.occupations, self.embeddings):
            score = sum(float(a) * float(b) for a, b in zip(query_embedding, embedding))
            scored.append((score, row))
        scored.sort(key=lambda pair: (-pair[0], pair[1]["uri"]))
        return [row for _, row in scored[:max(0, int(limit))]]

