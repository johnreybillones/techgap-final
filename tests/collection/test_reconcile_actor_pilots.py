import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.jobs import reconcile_actor_pilots as reconcile


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False), encoding="utf-8")


def write_jsonl(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows), encoding="utf-8")


def make_inputs(root):
    bf = root / "blackfalcon"
    sh = root / "shahidirfan"
    ids = list(reconcile.ASSESSMENTS)
    saved = [str(80000000 + n) for n in range(34)]
    all_ids = saved + ids
    raw_items = []
    for index, sid in enumerate(all_ids):
        description = "Required SQL and Python capabilities for data pipelines." if sid != "95082168" else ""
        page = 2 if index < 22 else (3 if index < 28 else None)
        query = "https://ph.jobstreet.com/jobs?keywords=data+engineer&daterange=31"
        if page is not None:
            query = query.replace("&daterange", "&page=%s&daterange" % page)
        raw_items.append({"seekJobId": sid, "canonicalUrl": "https://ph.jobstreet.com/job/" + sid,
                          "title": "Data Engineer", "company": "Example", "location": "Makati",
                          "locationCountry": "PH", "employmentType": "Full time", "workArrangement": "onsite",
                          "postedDate": "2026-10-20T00:00:00Z", "scrapedAt": "2026-10-23T00:00:00Z",
                          "description": description, "contentQuality": "full", "searchUrl": query})
    write_json(bf / "raw_items.json", raw_items)
    keys = ["jobstreet:ph:" + sid for sid in all_ids]
    write_jsonl(bf / "observations.jsonl", [{"posting_key": k} for k in keys])
    write_jsonl(bf / "versions.jsonl", [{"posting_key": k} for k in keys])
    old_flags = [{"seekJobId": sid, "philippine_eligibility": False, "employment_status": False,
                  "technical_assessability": False, "role_link": False, "description_quality": "missing"}
                 for sid in all_ids]
    write_json(bf / "source_audit.json", old_flags)
    write_json(bf / "yield_report.json", {"window": {"fromDate": "2026-09-23T00:00:00Z", "toDate": "2026-10-23T00:00:00Z"},
                "full_descriptions": 48, "missing_or_empty_descriptions": 2, "source_audited_usable_new_ids": 3,
                "new_rows": [{"seekJobId": sid, "philippine_eligibility": False,
                "employment_status": False, "technical_assessability": False, "source_audited_usable": False} for sid in ids]})
    write_json(bf / "run_final.json", {"startedAt": "2026-10-23T00:00:00Z", "finishedAt": "2026-10-23T00:01:00Z",
                                        "actId": "actor", "buildId": "build", "options": {"build": "0.4.47",
                                        "maxTotalChargeUsd": 0.11, "restartOnError": False, "timeoutSecs": 300,
                                        "memoryMbytes": 1024}})
    (bf / "requests").mkdir(parents=True)
    write_json(bf / "requests" / "request.json", {"actor_id": "actor", "build_id": "build", "request_body_sha256": "synthetic",
        "run_options": {"build": "0.4.47", "maxTotalChargeUsd": 0.11, "restartOnError": False, "timeout": 300, "memory": 1024}, "input": {
        "query": "data engineer", "country": "PH", "maxPages": 2, "maxResults": 50, "dateRange": "31",
        "fromDate": "2026-09-23T00:00:00Z", "toDate": "2026-10-23T00:00:00Z"}})
    raw_hash = hashlib.sha256((bf / "raw_items.json").read_bytes()).hexdigest()
    write_json(bf / "raw_handoff_validation.json", {"run_id": "run", "dataset_id": "dataset", "hashes": {"raw_items.json": raw_hash}})

    registry_path = sh / "comparison_registry_2026-10-23.jsonl"
    write_jsonl(registry_path, [{"source_id": sid} for sid in saved + [str(81000000 + n) for n in range(433)]])
    registry_hash = hashlib.sha256(registry_path.read_bytes()).hexdigest()
    write_json(sh / "manifest.json", {"artifact_hashes": {"comparison_registry_2026-10-23.jsonl": registry_hash}})
    write_json(sh / "collection_config.json", {"queries": [{"keyword": q} for q in ["data engineer", "gameplay engineer", "NOC engineer", "full stack developer", "application developer", "SOC analyst"]]})
    write_json(sh / "final_reconciliation_2026-10-23.json", {"window_start": "2026-09-23T00:00:00Z", "window_end": "2026-10-23T00:00:00Z"})
    (sh / "new_id_yield_audit_2026-10-23.csv").write_text("source_id\n12345678\n", encoding="utf-8-sig")
    return bf, sh, registry_hash


class ReconcileActorPilotsTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)

    def tearDown(self):
        patch.stopall()
        self.temp.cleanup()

    def test_source_id_join_and_registry_duplicates(self):
        self.assertEqual(reconcile.source_id_from_item({"seekJobId": "123", "canonicalUrl": "https://ph.jobstreet.com/job/123"}), "123")
        with self.assertRaisesRegex(ValueError, "does not match"):
            reconcile.source_id_from_item({"seekJobId": "123", "canonicalUrl": "https://ph.jobstreet.com/job/124"})
        with self.assertRaisesRegex(ValueError, "duplicate"):
            reconcile.registry_ids([{"source_id": "123"}, {"source_id": "123"}])

    def test_internship_rule_and_missing_description(self):
        self.assertEqual(reconcile.classify_cohort({"title": "Analytics Engineer", "employmentType": "Contract/Temp"}, "Prior experience or internship is an advantage."), ("employment", "yes"))
        self.assertEqual(reconcile.classify_cohort({"title": "Data Intern", "employmentType": "Full time"}, "SQL required"), ("internship", "separate_cohort"))
        self.assertEqual(reconcile.classify_cohort({"title": "Data Engineer", "employmentType": "Full time"}, ""), ("employment", "yes"))

    def test_page_evidence_requires_matching_host_query_and_date_context(self):
        request = {"query": "data engineer", "dateRange": "31"}
        self.assertEqual(reconcile.page_from_search_url("https://ph.jobstreet.com/jobs?keywords=data+engineer&page=2&daterange=31", request), 2)
        self.assertIsNone(reconcile.page_from_search_url("https://ph.jobstreet.com/jobs?keywords=data+engineer&daterange=31", request))
        self.assertIsNone(reconcile.page_from_search_url("https://example.com/jobs?keywords=data+engineer&page=2&daterange=31", request))
        self.assertIsNone(reconcile.page_from_search_url("https://ph.jobstreet.com/jobs?keywords=analyst&page=2&daterange=31", request))

    def test_blackfalcon_hash_validation_fails_on_tampered_input(self):
        bf = self.root / "bf"
        (bf / "raw_items.json").parent.mkdir(parents=True)
        (bf / "raw_items.json").write_text("[]", encoding="utf-8")
        write_json(bf / "raw_handoff_validation.json", {"hashes": {"raw_items.json": "bad"}})
        with self.assertRaisesRegex(ValueError, "hash mismatch"):
            reconcile.validate_blackfalcon(bf)

    def test_determinism_id_keyed_flag_conflict_and_missing_text(self):
        bf, sh, registry_hash = make_inputs(self.root)
        patch.object(reconcile, "FROZEN_REGISTRY_SHA256", registry_hash).start()
        out_a, out_b = self.root / "out-a", self.root / "out-b"
        request = bf / "requests" / "request.json"
        report_a = reconcile.build(bf, sh, out_a, request, generated_at="2026-10-23T00:00:00+00:00")
        report_b = reconcile.build(bf, sh, out_b, request, generated_at="2026-10-23T00:00:00+00:00")
        self.assertEqual(report_a, report_b)
        self.assertEqual(report_a["identity_and_registry"], {"blackfalcon_observations": 50, "distinct_numeric_ids": 50,
                                                              "saved_ids": 34, "new_ids": 16, "combined_union_ids": 483})
        self.assertTrue(all(report_a["pagination"]["run_metadata"]["requested_vs_actual_run_option_matches"].values()))
        self.assertEqual(report_a["blackfalcon_corrected"]["page_groups"], {
            "2": {"rows": 22, "new_ids": 0, "corrected_provisional_assessable_new_employment_ids": 0},
            "3": {"rows": 6, "new_ids": 0, "corrected_provisional_assessable_new_employment_ids": 0},
            "unproven": {"rows": 22, "new_ids": 16, "corrected_provisional_assessable_new_employment_ids": 15},
        })
        rows_a = json.loads((out_a / "cases.json").read_text(encoding="utf-8"))
        rows_b = json.loads((out_b / "cases.json").read_text(encoding="utf-8"))
        self.assertEqual(rows_a, rows_b)
        case = next(row for row in rows_a if row["source_id"] == "95060375")
        self.assertFalse(case["prior_source_audit"]["technical_assessability"])
        self.assertEqual(case["technical_assessability"], "yes")
        missing = next(row for row in rows_a if row["source_id"] == "95082168")
        self.assertEqual(missing["description_chars"], 0)
        self.assertEqual(missing["technical_assessability"], "unavailable")
        self.assertEqual(report_a["blackfalcon_corrected"]["internships"], 0)
        for filename in ("cases.csv", "cases.json", "report.json", "report.md", "manifest.json"):
            self.assertEqual((out_a / filename).read_bytes(), (out_b / filename).read_bytes())

    def test_frozen_registry_hash_is_enforced(self):
        bf, sh, registry_hash = make_inputs(self.root)
        patch.object(reconcile, "FROZEN_REGISTRY_SHA256", "wrong").start()
        with self.assertRaisesRegex(ValueError, "registry hash"):
            reconcile.build(bf, sh, self.root / "out", bf / "requests" / "request.json",
                            generated_at="2026-10-23T00:00:00+00:00")


if __name__ == "__main__":
    unittest.main()
