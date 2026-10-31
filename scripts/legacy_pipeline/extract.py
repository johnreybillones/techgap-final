"""GLiNER2 adapter contract with mandatory source-span reproduction."""
import re

from .text import verify_spans


class Gliner2Extractor:
    def __init__(self, model, *, version, schema):
        self.model = model
        self.version = version
        self.schema = schema

    def extract(self, text):
        try:
            result = self.model.extract(text, self.schema, include_spans=True)
        except Exception as exc:
            raise RuntimeError("gliner2_inference_failed") from exc
        if not isinstance(result, dict):
            raise RuntimeError("gliner2_invalid_result")
        entities = result.get("entities", {})
        if not isinstance(entities, dict):
            raise RuntimeError("gliner2_invalid_entities")

        normalized = {}
        for category, spans in entities.items():
            if not isinstance(spans, list):
                raise RuntimeError("gliner2_invalid_entity_list:" + str(category))
            normalized[category] = verify_spans(
                text,
                [{**span, "label": category} for span in spans],
            )

        mandatory = normalized.get("mandatory_experience", [])
        seniority = normalized.get("seniority_requirement", [])
        normalized["experience"] = mandatory + normalized.get("preferred_experience", [])
        normalized["seniority"] = seniority
        normalized["duties"] = normalized.get("duties", [])
        normalized["location"] = normalized.get("work_location", [])
        normalized["seniority_basis"] = (
            "explicit_source_statement" if seniority else "inferred"
        )
        normalized["explicit_senior_applicant_role"] = any(
            re.search(r"\b(senior|lead|principal)\b", span["text"], re.I)
            for span in seniority
        )
        normalized["mandatory_experience_min_years"] = _minimum_years(mandatory)
        return normalized


def _minimum_years(spans):
    minima = []
    for span in spans:
        value = span["text"].casefold()
        patterns = (
            r"(?:at least|minimum(?: of)?|no less than)\s+(\d+(?:\.\d+)?)\s*(?:years?|yrs?)",
            r"(\d+(?:\.\d+)?)\s*\+\s*(?:years?|yrs?)",
            r"(\d+(?:\.\d+)?)\s*(?:-|to)\s*\d+(?:\.\d+)?\s*(?:years?|yrs?)",
            r"(\d+(?:\.\d+)?)\s*(?:years?|yrs?)",
        )
        for pattern in patterns:
            match = re.search(pattern, value)
            if match:
                minima.append(float(match.group(1)))
                break
    return min(minima) if minima else None

