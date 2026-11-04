"""The SQL queries must reproduce the Python analysis (and therefore the Excel model and the recommendation)."""
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))
import eccr  # noqa: E402
import run_queries  # noqa: E402
from verify_excel import expected_group  # noqa: E402


class SQLResults(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.r = run_queries.run(write=False)
        cls.progs = eccr.load_programs()
        cls.recon = json.load(open(ROOT / "outputs" / "reconciliation.json"))

    def test_goals(self):
        met = {x["utility"]: x["all_goals_met"] for x in self.r["01_goal_achievement"]}
        self.assertEqual(met, {"Florida Power & Light": "Yes", "Duke Energy Florida": "Yes",
                               "Tampa Electric": "No", "Florida Public Utilities": "No"})

    def test_savings_sums(self):
        tot = eccr.utility_totals(self.progs)
        for x in self.r["02_savings_reconciliation"]:
            self.assertAlmostEqual(x["program_pages_gwh_generator"], round(tot[x["utility"]]["kwh_gen"] / 1e6, 3))

    def test_eccr_lines_add_to_filed_totals(self):
        for x in self.r["03_eccr_line_totals"]:
            self.assertLessEqual(abs(x["difference_usd"]), 2, x["utility"])

    def test_cost_reconciliation_matches_python(self):
        rows = self.r["04_cost_reconciliation"]
        py = {(x["utility"], x["eccr_program"]): x for x in self.recon["rows"]}
        self.assertEqual(len(rows), len(py))
        for x in rows:
            p = py[(x["utility"], x["eccr_program"])]
            self.assertAlmostEqual(x["dsm_cost_usd"], p["dsm_usd"], places=2)
            self.assertEqual(x["within_rounding"] == "Yes", p["ok"])

    def test_lines_without_program_page(self):
        got = {}
        for x in self.r["05_eccr_lines_without_program_page"]:
            got[x["utility"]] = x["utility_total_without_page_usd"]
        for u, s in self.recon["summary"].items():
            self.assertEqual(got[u], s["extra_total"])

    def test_program_screen_matches_python(self):
        sql = {(x["utility"], x["program"]): x for x in self.r["06_program_screen"]}
        self.assertEqual(len(sql), len(self.progs))
        for p in self.progs:
            x = sql[(p["utility"], p["program"])]
            with self.subTest(program=p["program"]):
                self.assertEqual(bool(x["is_demand_program"]), p["demand_program"])
                if eccr.analyzable(p):
                    self.assertAlmostEqual(x["cost_per_kwh"], round(p["cost"] / p["kwh"], 6), places=6)
                else:
                    self.assertIsNone(x["cost_per_kwh"])
                self.assertEqual(x["screening_group"], expected_group(p))

    def test_portfolio_cost_per_kwh(self):
        ranked = [p for p in self.progs if eccr.rankable(p)]
        port = next(x for x in self.r["07_screening_summary"] if x["kind"] == "portfolio")
        self.assertEqual(port["programs"], len(ranked))
        self.assertAlmostEqual(port["cost_per_kwh"], round(sum(p["cost"] for p in ranked) / sum(p["kwh"] for p in ranked), 4))

    def test_participation_tier_changes(self):
        changes = [x["program"] for x in self.r["08_participation_sensitivity"] if x["tier_changes"] == "Yes"]
        self.assertEqual(sorted(changes), ["Neighborhood Energy Saver",
                                           "Residential Incentive Program (f/k/a Home Energy Improvement)"])


if __name__ == "__main__":
    unittest.main()
