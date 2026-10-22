"""Conservative deterministic eligibility checks with evidence passages."""
import re
from datetime import datetime, timezone


def _date(value):
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        return parsed.replace(tzinfo=timezone.utc) if parsed.tzinfo is None else parsed.astimezone(timezone.utc)
    except (AttributeError, ValueError):
        return None


def evaluate(item, *, window_start, window_end):
    checks = {}
    title = str(item.get("title") or "")
    desc = str(item.get("description_text") or "")
    text = title + "\n" + desc
    def evidence(pattern):
        match = re.search(pattern, text, re.I)
        return match.group(0) if match else None
    start, end = _date(window_start), _date(window_end)
    posted = _date(item.get("postedAt_iso"))
    checks["identity"] = {"state": "pass" if item.get("id") and item.get("url") else "unknown", "evidence": item.get("id")}
    checks["date"] = {"state": "pass" if posted and start and end and start <= posted < end else ("fail" if posted and start and end and (posted < start or posted >= end) else "unknown"), "evidence": item.get("postedAt_iso")}
    geo = (str(item.get("location") or "") + " " + desc).lower()
    geo_ok = any(term in geo for term in ("philippines", "manila", "cebu", "davao", "makati", "quezon city", "philippine applicants"))
    geo_no = bool(re.search(r"(only|must be based in)\s+(the )?(us|united states|india|singapore|australia|uk)\b", geo))
    checks["geography"] = {"state": "fail" if geo_no else ("pass" if geo_ok else "unknown"), "evidence": item.get("location") if geo_ok or geo_no else None}
    internship = evidence(r"\b(internship|intern|OJT|student placement|apprenticeship)\b")
    checks["internship"] = {"state": "fail" if internship else "pass", "evidence": internship or item.get("workType")}
    junior = evidence(r"\b(junior|jr\.?|entry[- ]level|graduate|fresh graduates? welcome|no experience required)\b")
    senior = evidence(r"\b(senior|lead|manager|intermediate|minimum\s+[3-9]\s+years?|at least\s+[3-9]\s+years?)\b")
    checks["seniority"] = {"state": "fail" if senior else ("pass" if junior else "unknown"), "evidence": senior or junior}
    duties = evidence(r"\b(develop|program|software|network|database|cybersecurity|machine learning|data engineer|gameplay|web application|system administrator|QA engineer)\w*\b")
    checks["relevance"] = {"state": "pass" if duties else "unknown", "evidence": duties}
    full = bool(item.get("description_text", "").strip() or item.get("description_html", "").strip())
    checks["description"] = {"state": "pass" if full and not item.get("isExpired") else "unknown", "evidence": "full_description" if full else None}
    states = [x["state"] for x in checks.values()]
    terminal = "excluded" if "fail" in states else ("eligible" if all(s == "pass" for s in states) else "unresolved")
    reasons = [name for name, value in checks.items() if value["state"] != "pass"]
    return {"policy_version": "explicit-entry-junior-v1", "state": terminal, "checks": checks, "reasons": reasons}
