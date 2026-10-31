import unittest

from scripts.pipeline import baseline, evaluate


class MetricTests(unittest.TestCase):
    def test_exact_match_counts_and_undefined_denominators(self):
        gold = {("tool_technology", 0, 3), ("technical_task", 5, 10)}
        pred = {("tool_technology", 0, 3), ("technical_task", 5, 9)}  # second span has wrong end
        counts = evaluate.example_counts(gold, pred)
        self.assertEqual(counts["tool_technology"], [1, 0, 0])
        self.assertEqual(counts["technical_task"], [0, 1, 1])
        m = evaluate.micro(counts)
        self.assertEqual((m["tp"], m["fp"], m["fn"]), (1, 1, 1))
        self.assertAlmostEqual(m["f1"], 0.5)
        empty = evaluate.prf(0, 0, 0)
        self.assertIsNone(empty["precision"])
        self.assertIsNone(empty["f1"])

    def test_wrong_type_is_both_fp_and_fn(self):
        counts = evaluate.example_counts({("technical_task", 0, 4)}, {("tool_technology", 0, 4)})
        self.assertEqual(evaluate.micro(counts)["f1"], 0.0)


class IntervalTests(unittest.TestCase):
    def table(self, n, tp=1):
        return {"g%d" % i: {"technical_task": [tp, 1, 1]} for i in range(n)}

    def test_too_few_groups_is_explicit(self):
        out = evaluate.interval(self.table(3), min_groups=10)
        self.assertEqual(out["status"], "insufficient_groups")

    def test_interval_is_seeded_and_contains_the_estimate(self):
        t = self.table(30)
        a = evaluate.interval(t, n=200, seed=1)
        self.assertEqual(a, evaluate.interval(t, n=200, seed=1))
        self.assertLessEqual(a["lower"], 0.5)
        self.assertGreaterEqual(a["upper"], 0.5)

    def test_paired_difference_uses_same_groups(self):
        better = self.table(30, tp=3)
        out = evaluate.interval(self.table(30), extra=better, n=200, seed=1)
        self.assertGreater(out["lower"], 0)


class BaselineTests(unittest.TestCase):
    def test_dictionary_matches_whole_words_after_source_line(self):
        rows = [{"output": {"entities": {"tool_technology": [{"text": "SQL", "start": 0, "end": 3}], "technical_task": []}}}]
        d = baseline.build(rows)
        text = "Source: job posting\nUse sql and MySQL"
        self.assertEqual(baseline.predict(d, text), {("tool_technology", 24, 27)})


if __name__ == "__main__":
    unittest.main()
