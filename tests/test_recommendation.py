import subprocess, sys, unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class Recommendation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        for s in ("analyze.py", "write_recommendation.py"):
            subprocess.run([sys.executable, str(ROOT / "scripts" / s)], check=True, capture_output=True)
        cls.doc = (ROOT / "docs" / "recommendation.md").read_text()
        sys.path.insert(0, str(ROOT / "scripts"))

    def test_has_all_issues_and_disclaimer(self):
        for i in range(1, 8):
            self.assertIn(f"### Issue {i}:", self.doc)
        self.assertIn("not a Florida Public Service Commission document", self.doc)

    def test_figures_written_and_referenced(self):
        for f in ("fig1_goal_achievement", "fig2_cost_per_kwh", "fig3_eccr_composition"):
            self.assertTrue((ROOT / "docs" / "figures" / f"{f}.svg").exists())
            self.assertIn(f"figures/{f}.svg", self.doc)

    def test_no_unformatted_values(self):
        for bad in ("{", "}", "nan", "$-"):
            self.assertNotIn(bad, self.doc.replace("{len", ""), bad)

    def test_classification_rules(self):
        import write_recommendation as w
        mk = lambda cost, kwh, nb: {"cost": cost, "kwh": kwh, "nb": nb}
        self.assertEqual(w.classify(mk(100, 1000, 5)), "Appears cost-effective")      # $0.10, positive
        self.assertEqual(w.classify(mk(100, 1000, -5)), "Mixed signals")              # $0.10, negative
        self.assertEqual(w.classify(mk(1000, 1000, -5)), "Needs more support")        # $1.00, negative
        self.assertEqual(w.classify(mk(1000, 1000, 5)), "Mixed signals")              # $1.00, positive
        self.assertEqual(w.classify(mk(1000, 1000, None)), "Needs more support")
        self.assertEqual(w.classify(mk(100, 1000, None)), "Insufficient information")


if __name__ == "__main__":
    unittest.main()
