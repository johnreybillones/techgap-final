"""Source-text normalization and evidence-span integrity helpers."""
import re
import unicodedata


def normalize_text(value):
    value = unicodedata.normalize("NFC", str(value or "").replace("\r\n", "\n").replace("\r", "\n"))
    return re.sub(r"[ \t]+", " ", value).strip()


def checked_span(source, start, end, label):
    if not isinstance(start, int) or not isinstance(end, int) or start < 0 or end <= start or end > len(source):
        raise ValueError("invalid_source_span")
    return {"label": label, "start": start, "end": end, "text": source[start:end]}


def verify_spans(source, spans):
    return [checked_span(source, span["start"], span["end"], span["label"]) for span in spans]

