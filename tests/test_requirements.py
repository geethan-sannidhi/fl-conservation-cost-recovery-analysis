"""The requirements checklist must cover every requirement for every utility, with evidence."""
import csv
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATUSES = {"Met", "Partly met", "Not met", "Not found", "Can't determine", "Not reviewed"}


class Requirements(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.reqs = list(csv.DictReader(open(ROOT / "data" / "requirements.csv")))
        cls.rows = list(csv.DictReader(open(ROOT / "outputs" / "requirements_checklist.csv")))

    def test_complete_grid(self):
        utils = {r["utility"] for r in self.rows}
        self.assertEqual(len(utils), 4)
        self.assertEqual(len(self.rows), len(self.reqs) * 4)
        self.assertEqual({(r["id"], r["utility"]) for r in self.rows},
                         {(q["id"], u) for q in self.reqs for u in utils})

    def test_valid_status_and_evidence(self):
        for r in self.rows:
            with self.subTest(id=r["id"], utility=r["utility"]):
                self.assertIn(r["status"], STATUSES)
                self.assertGreater(len(r["evidence"]), 15)

    def test_goals_data_uses_order_values(self):
        g = {r["utility"]: r for r in csv.DictReader(open(ROOT / "data" / "goals_vs_achieved_2025.csv"))}
        self.assertEqual(float(g["Duke Energy Florida"]["goal_gwh"]), 55.0)   # Order PSC-2024-0429-FOF-EG
        self.assertEqual(float(g["Florida Power & Light"]["goal_gwh"]), 100.08)  # Order PSC-2024-0505-FOF-EG

    def test_doc_generated(self):
        doc = (ROOT / "docs" / "REQUIREMENTS.md").read_text()
        self.assertIn("Where the filings do not line up with the requirements", doc)
        self.assertIn("not a Commission compliance determination", doc)


if __name__ == "__main__":
    unittest.main()
