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
    def test_eccr_lines_sum_to_filed_totals(self):
        rows = list(csv.DictReader(open(ROOT / "data" / "eccr_2025_costs.csv")))
        for t in csv.DictReader(open(ROOT / "data" / "ct2_totals_2025.csv")):
            got = sum(int(r["total_cost_usd"]) for r in rows if r["utility"] == t["utility"])
            with self.subTest(utility=t["utility"]):
                self.assertLessEqual(abs(got - int(t["ct2_total_usd"])), 2)

    def test_every_dsm_program_is_mapped_and_targets_exist(self):
        progs = [p for p in eccr.load_programs() if p["utility"] != "Florida Public Utilities"]
        mapping = list(csv.DictReader(open(ROOT / "data" / "dsm_to_eccr_map.csv")))
        mapped = {(m["utility"], m["dsm_program"]) for m in mapping}
        self.assertEqual({(p["utility"], p["program"]) for p in progs} - mapped, set())
        lines = {(r["utility"], r["eccr_program"]) for r in csv.DictReader(open(ROOT / "data" / "eccr_2025_costs.csv"))}
        for m in mapping:
            if m["eccr_program"]:
                self.assertIn((m["utility"], m["eccr_program"]), lines)

    def test_duke_load_management_combines_two_dsm_programs(self):
        # DSM report: 34,874k + 677k; ECCR line: 35,550,302
        ps = {p["program"]: p["cost"] for p in eccr.load_programs() if p["utility"] == "Duke Energy Florida"}
        dsm = ps["Residential Load Management (a/k/a Residential Energy Management, Energy-Wise)"] + ps["Commercial Energy Management"]
        self.assertLessEqual(abs(dsm - 35_550_302), 1000)

    def test_fpuc_program_pages_sum(self):
        t = eccr.utility_totals(eccr.load_programs())["Florida Public Utilities"]
        self.assertEqual(t["kwh_meter"], 127_350)
        self.assertEqual(t["kwh_gen"], 131_160)

    def test_fpuc_not_ranked_with_fully_loaded_costs(self):
        ps = eccr.load_programs()
        self.assertFalse(any(eccr.rankable(p) for p in ps if p["utility"] == "Florida Public Utilities"))
        self.assertTrue(any(eccr.analyzable(p) for p in ps if p["utility"] == "Florida Public Utilities"))

    def test_fpl_program_savings_reconcile_to_reported_gwh(self):
        t = eccr.utility_totals(eccr.load_programs())["Florida Power & Light"]
        self.assertAlmostEqual(t["kwh_gen"] / 1e6, 102.57, places=2)

    def test_demand_programs_excluded_from_screen(self):
        ps = eccr.load_programs()
        self.assertTrue(all(not eccr.analyzable(p) for p in ps if p["demand_program"]))
        self.assertTrue(any(eccr.analyzable(p) for p in ps))


if __name__ == "__main__":
    unittest.main()
