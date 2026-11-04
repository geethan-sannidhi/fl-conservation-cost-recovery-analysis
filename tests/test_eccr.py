import csv, sys, unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
import eccr  # noqa: E402


class Metrics(unittest.TestCase):
    def test_cost_per_kwh(self):
        self.assertAlmostEqual(eccr.cost_per_kwh(570_000, 17_853_658), 0.031926, places=5)

    def test_payback(self):
        # $1,000 cost, 5,000 kWh/yr at $0.10 = $500/yr -> 2.0 years
        self.assertAlmostEqual(eccr.payback_years(1000, 5000, 0.10), 2.0)

    def test_no_savings_gives_none(self):
        self.assertIsNone(eccr.cost_per_kwh(100, 0))
        self.assertIsNone(eccr.payback_years(100, None, 0.1))

    def test_scenario_full_participation_is_identity(self):
        self.assertEqual(eccr.scenario(1000, 500, 1.0), (1000, 500))

    def test_scenario_scales_variable_cost_only(self):
        c, k = eccr.scenario(1000, 500, 0.5, fixed=0.3)  # 300 + 700*0.5
        self.assertAlmostEqual(c, 650)
        self.assertAlmostEqual(k, 250)


class Data(unittest.TestCase):
    def test_fpl_ct3_sums_to_ct2_total_within_rounding(self):
        rows = list(csv.DictReader(open(ROOT / "data" / "fpl_eccr_2025_ct3_costs.csv")))
        self.assertLessEqual(abs(sum(int(r["total_cost_2025_usd"]) for r in rows) - 168_697_310), 2)

    def test_fpl_program_savings_reconcile_to_reported_gwh(self):
        t = eccr.utility_totals(eccr.load_programs())["Florida Power & Light"]
        self.assertAlmostEqual(t["kwh_gen"] / 1e6, 102.57, places=2)

    def test_demand_programs_excluded_from_screen(self):
        ps = eccr.load_programs()
        self.assertTrue(all(not eccr.analyzable(p) for p in ps if p["demand_program"]))
        self.assertTrue(any(eccr.analyzable(p) for p in ps))


if __name__ == "__main__":
    unittest.main()
