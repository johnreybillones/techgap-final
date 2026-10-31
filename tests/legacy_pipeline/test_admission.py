import unittest

from scripts.legacy_pipeline.admission import decide_admission, reconcile_decisions


class AdmissionPolicyTests(unittest.TestCase):
    def base_case(self):
        return {
            "posting_key": "jobstreet:ph:1",
            "count_unit_id": "jobstreet:ph:1",
            "selected_version_id": "v1",
            "selected_raw_hash": "h1",
            "identity_ok": True,
            "date_ok": True,
            "geography_ok": True,
            "usable_text": True,
            "computing_relevance_supported": True,
            "occupation": {"uri": "esco:1", "label": "software developer", "version": "v1"},
            "tracks": [{"id": "shared-core", "basis": "source-supported duties"}],
            "cohort": "employment",
            "seniority_basis": "inferred",
            "mandatory_experience_min_years": None,
            "explicit_senior_applicant_role": False,
            "evidence": {},
            "attempt_history": [{"attempt": 1}],
        }

    def test_inferred_junior_without_years_can_pass(self):
        decision = decide_admission(self.base_case())
        self.assertEqual(decision["decision"], "accept")
        self.assertEqual(decision["accepted_cohort"], "employment")
        self.assertEqual(decision["seniority_basis"], "inferred")

    def test_exact_or_at_least_two_years_can_pass_but_more_than_two_rejects(self):
        case = self.base_case()
        case["mandatory_experience_min_years"] = 2
        self.assertEqual(decide_admission(case)["decision"], "accept")
        case["mandatory_experience_min_years"] = 3
        result = decide_admission(case)
        self.assertEqual(result["decision"], "reject")
        self.assertIn("mandatory_experience_above_two_years", result["reason_codes"])

    def test_missing_occupation_rejects_with_specific_reason(self):
        case = self.base_case()
        case["occupation"] = None
        result = decide_admission(case)
        self.assertEqual(result["decision"], "reject")
        self.assertIn("no_supported_occupation", result["reason_codes"])

    def test_reconciliation_is_at_source_and_count_unit_levels(self):
        accepted = decide_admission(self.base_case())
        rejected_case = self.base_case()
        rejected_case.update(posting_key="jobstreet:ph:2", selected_version_id="v2",
                             selected_raw_hash="h2", count_unit_id="group:1",
                             explicit_senior_applicant_role=True)
        rejected = decide_admission(rejected_case)
        summary, units = reconcile_decisions([accepted, rejected])
        self.assertEqual(summary["input_postings"], 2)
        self.assertEqual(summary["accepted_employment"], 1)
        self.assertEqual(summary["accepted_internship"], 0)
        self.assertEqual(summary["rejected"], 1)
        self.assertTrue(summary["equation_reconciles"])
        self.assertEqual(len(units), 1)


if __name__ == "__main__":
    unittest.main()
