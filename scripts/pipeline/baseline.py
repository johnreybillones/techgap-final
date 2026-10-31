"""Exact-match dictionary baseline for span extraction (MODEL_PIPELINE_PLAN section 3).

The dictionary is built from training spans only. Matching is case-insensitive on whole
words; every dictionary entry is searched independently, so nested spans can both match.
"""
import re
from collections import Counter, defaultdict


def build(train_rows):
    """Distinct lowercase span text -> its most frequent type (ties: alphabetical)."""
    votes = defaultdict(Counter)
    for row in train_rows:
        for label, items in row["output"]["entities"].items():
            for item in items:
                votes[item["text"].lower()][label] += 1
    return {text: sorted(c.items(), key=lambda kv: (-kv[1], kv[0]))[0][0] for text, c in votes.items()}


def predict(dictionary, text):
    """Set of (type, start, end) over `text`, ignoring the leading 'Source: ...' line."""
    body = text.index("\n") + 1 if "\n" in text else 0
    lower = text.lower()
    found = set()
    for entry, label in dictionary.items():
        if entry not in lower[body:]:
            continue
        for m in re.finditer(r"(?<!\w)" + re.escape(entry) + r"(?!\w)", lower[body:]):
            found.add((label, body + m.start(), body + m.end()))
    return found
