"""P2A extraction, ESCO retrieval, independent classification and reconsideration."""
from datetime import datetime
import re
from urllib.parse import urlparse

from .contracts import TRACKS
from .text import normalize_text


def _date(value):
    try:
        return datetime.fromisoformat(str(value or "").replace("Z", "+00:00"))
    except ValueError:
        return None


def _supported(scores, name):
    row = scores.get(name, {})
    return float(row.get("entailment", float("-inf"))) > float(row.get("not_entailment", float("inf")))


def classify_posting(source, *, extractor, retriever, classifier, taxonomy_version,
                     window_start, window_end, max_reconsiderations=1):
    fields = source.get("fields", {})
    text = normalize_text(fields.get("description_text") or fields.get("description_html"))
    title = normalize_text(fields.get("title"))
    evidence = extractor.extract(text) if text else {
        "duties": [], "experience": [], "seniority": [], "location": [],
        "seniority_basis": "inferred", "mandatory_experience_min_years": None,
        "explicit_senior_applicant_role": False,
    }
    passages = [span["text"] for key in ("duties", "mandatory_experience", "seniority", "work_location")
                for span in evidence.get(key, [])]
    if not passages and text:
        passages = [text]
    attempts = []
    selected = None
    scores = {}
    catalogue_size = len(getattr(getattr(retriever, "taxonomy", None), "occupations", ()))
    limits = list(dict.fromkeys([20, 40] + ([catalogue_size] if catalogue_size else [])))[:max_reconsiderations + 2]
    for attempt, limit in enumerate(limits, 1):
        candidates = retriever.retrieve(title, passages, limit)
        hypotheses = {
            "computing_relevance": "The applicant's principal work performs a computing function.",
            "junior_suitability": "The applicant can perform this vacancy with zero to two years of experience.",
            "internship_vacancy": "This vacancy is an internship, student placement, or on-the-job training role.",
            "employment_vacancy": "This vacancy is regular employment rather than an internship or student placement.",
        }
        for row in candidates:
            hypotheses["occupation:" + row["uri"]] = "The applicant's principal function is " + row["definition"]
        for track_id, definition in TRACKS.items():
            hypotheses["track:" + track_id] = "The applicant " + definition
        scores = classifier.score("\n".join([title] + passages), hypotheses)
        supported = [row for row in candidates if _supported(scores, "occupation:" + row["uri"])]
        attempts.append({"attempt": attempt, "candidate_limit": limit,
                         "candidate_uris": [row["uri"] for row in candidates],
                         "supported_occupation_uris": [row["uri"] for row in supported],
                         "hypotheses": hypotheses,
                         "scores": {key: value for key, value in scores.items()
                                    if not key.startswith("_")},
                         "classifier_input_chunks": getattr(classifier, "last_chunks", [])})
        if len(supported) == 1:
            selected = supported[0]
            break
        # Expand to the complete catalog only when the current candidates
        # produced no occupation support; ambiguity is already a match state.
        if supported:
            break
    posted = _date(fields.get("postedAt_iso"))
    start, end = _date(window_start), _date(window_end)
    date_ok = bool(posted and start and end and start <= posted <= end)
    internship_supported = _supported(scores, "internship_vacancy")
    employment_supported = _supported(scores, "employment_vacancy")
    cohort = ("internship" if internship_supported and not employment_supported else
              "employment" if employment_supported and not internship_supported else None)
    tracks = [{"id": track_id, "basis": "independent_source-text_hypothesis"}
              for track_id in TRACKS if _supported(scores, "track:" + track_id)]
    return {
        **{name: source[name] for name in ("posting_key", "count_unit_id", "selected_version_id", "selected_raw_hash")},
        "identity_ok": bool(source.get("posting_key") and source.get("selected_version_id") and source.get("selected_raw_hash")),
        "date_ok": date_ok,
        "geography_ok": _philippine_location(source, fields),
        "usable_text": bool(text),
        "computing_relevance_supported": _supported(scores, "computing_relevance"),
        "occupation": selected,
        "tracks": tracks,
        "cohort": cohort,
        "cohort_basis": "independent_source_text_hypothesis" if cohort else "unresolved",
        "seniority_basis": evidence.get("seniority_basis") or "inferred",
        "mandatory_experience_min_years": evidence.get("mandatory_experience_min_years"),
        "explicit_senior_applicant_role": evidence.get("explicit_senior_applicant_role") is True,
        "evidence": evidence,
        "attempt_history": attempts,
        "model_versions": {"extractor": extractor.version, "retriever": retriever.version,
                           "classifier": classifier.version},
        "taxonomy_version": taxonomy_version,
    }


def _philippine_location(source, fields):
    location = normalize_text(fields.get("location"))
    country = normalize_text(fields.get("country")).casefold()
    host = (urlparse(str(source.get("source_url") or "")).hostname or "").casefold()
    philippine_place_terms = (
        "philippines", "metro manila", "central luzon", "central visayas", "western visayas",
        "eastern visayas", "northern mindanao", "davao region", "calabarzon", "mimaropa",
        "bicol region", "ilocos region", "cagayan valley", "caraga", "cordillera",
        "soccsksargen", "zamboanga peninsula", "bangsamoro", "cebu", "pampanga", "batangas",
        "bulacan", "laguna", "cavite", "rizal", "iloilo", "negros", "cagayan de oro",
        "davao", "makati", "manila", "pasig", "taguig", "quezon city", "pasay", "mandaluyong",
        "paranaque", "parañaque", "muntinlupa", "antipolo", "angeles city", "bacolod", "iloilo city",
    )
    local_location = any(term in location.casefold() for term in philippine_place_terms)
    local_country = country in {"philippines", "ph"}
    # Require a saved location. The endpoint is Philippine-specific, but an
    # absent location alone cannot establish geographic eligibility.
    return bool(location and (local_country or local_location or host == "ph.jobstreet.com"))


class TransformersZeroShotClassifier:
    """Thin fail-closed adapter over a locally cached Transformers pipeline."""
    def __init__(self, pipeline, *, version, batch_size=32):
        self.pipeline = pipeline
        self.version = version
        self.batch_size = batch_size
        self.last_chunks = []

    def _chunks(self, text, hypotheses):
        tokenizer = self.pipeline.tokenizer
        configured = int(getattr(self.pipeline.model.config, "max_position_embeddings", 512))
        tokenizer_limit = int(getattr(tokenizer, "model_max_length", configured))
        max_length = min(configured, tokenizer_limit)
        longest_hypothesis = max(
            len(tokenizer(value, add_special_tokens=False)["input_ids"])
            for value in hypotheses.values()
        )
        budget = max_length - longest_hypothesis - 3
        if budget < 32:
            raise RuntimeError("zero_shot_pair_token_budget_too_small")

        units = [unit.strip() for unit in re.split(r"(?<=[.!?;:])\s+|\n+", text) if unit.strip()]
        output = []
        current = []
        for unit in units:
            if len(tokenizer(unit, add_special_tokens=False)["input_ids"]) > budget:
                if current:
                    output.append(" ".join(current))
                    current = []
                words = unit.split()
                start = 0
                while start < len(words):
                    end = start
                    while end < len(words):
                        candidate = " ".join(words[start:end + 1])
                        if len(tokenizer(candidate, add_special_tokens=False)["input_ids"]) > budget:
                            break
                        end += 1
                    if end == start:
                        raise RuntimeError("zero_shot_statement_exceeds_token_budget")
                    output.append(" ".join(words[start:end]))
                    if end >= len(words):
                        break
                    start = max(start + 1, end - 12)
                continue
            candidate = " ".join(current + [unit])
            if current and len(tokenizer(candidate, add_special_tokens=False)["input_ids"]) > budget:
                output.append(" ".join(current))
                current = [unit]
            else:
                current.append(unit)
        if current:
            output.append(" ".join(current))
        self.last_chunks = [{"index": index, "text": chunk,
                             "token_count": len(tokenizer(chunk, add_special_tokens=False)["input_ids"])}
                            for index, chunk in enumerate(output)]
        return output

    def score(self, text, hypotheses):
        labels = list(hypotheses)
        descriptions = [hypotheses[label] for label in labels]
        chunks = self._chunks(text, hypotheses)
        if not chunks:
            return {}
        per_description = {description: [] for description in descriptions}
        try:
            for chunk in chunks:
                output = self.pipeline(chunk, candidate_labels=descriptions, multi_label=True,
                                       hypothesis_template="{}", batch_size=self.batch_size)
                for description, score in zip(output["labels"], output["scores"]):
                    per_description[description].append(float(score))
        except Exception as exc:
            raise RuntimeError("zero_shot_inference_failed") from exc
        result = {}
        for label, description in hypotheses.items():
            values = per_description[description]
            if not values:
                raise RuntimeError("zero_shot_missing_hypothesis_score")
            # Keep the source chunk with the strongest entailment evidence.
            score = max(values)
            result[label] = {"entailment": score, "not_entailment": 1.0 - score}
        return result

