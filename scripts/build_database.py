"""Build data/conservation_2025.sqlite from the repository's CSVs using sql/schema.sql."""
import csv
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
import eccr  # noqa: E402

DB = ROOT / "data" / "conservation_2025.sqlite"
SHORT = {"Florida Power & Light": "FPL", "Duke Energy Florida": "Duke", "Tampa Electric": "Tampa Electric",
         "Florida Public Utilities": "FPUC"}
ASSUMPTIONS = [
    ("low_tier", 0.15, "Lower-cost tier: max $ per first-year kWh"),
    ("high_tier", 0.60, "Higher-cost tier: above $ per first-year kWh"),
    ("fixed_share", 0.30, "Fixed share of program cost (participation sensitivity)"),
    ("value_1", 0.03, "Value of saved energy, scenario 1 ($/kWh)"),
    ("value_2", 0.06, "Value of saved energy, scenario 2 ($/kWh)"),
    ("value_3", 0.10, "Value of saved energy, scenario 3 ($/kWh)"),
    ("materiality", 100000, "Materiality floor for screening ($)"),
    ("part_lo", 0.8, "Participation scenario: low"),
    ("part_hi", 1.2, "Participation scenario: high"),
    ("tol_k", 500, "Rounding tolerance per program, reports in $000"),
    ("tol_teco", 50, "Rounding tolerance per program, Tampa Electric ($0.1k)"),
]


def num(v, scale=1.0):
    return None if v in (None, "") else float(v) * scale


def build(path=DB):
    if path.exists():
        path.unlink()
    con = sqlite3.connect(path)
    con.execute("PRAGMA foreign_keys = ON")
    con.executescript((ROOT / "sql" / "schema.sql").read_text())
    con.executemany("INSERT INTO utilities VALUES (?,?,?)", [(u, s, eccr.cost_basis(u)) for u, s in SHORT.items()])
    rows = list(csv.DictReader(open(ROOT / "data" / "programs_2025.csv")))
    con.executemany(
        "INSERT INTO programs (utility, program, program_cost_usd, kwh_meter, kwh_generator, net_benefits_usd, kwh_note, source_file, source_line)"
        " VALUES (?,?,?,?,?,?,?,?,?)",
        [(r["utility"], r["program"], num(r["program_cost_thousands"], 1000), num(r["annual_kwh_at_meter"]),
          num(r["annual_kwh_at_generator"]), num(r["net_benefits_thousands"], 1000), r["kwh_note"] or None,
          r["source_file"], r["source_line"]) for r in rows])
    con.executemany("INSERT INTO demand_keywords VALUES (?)", [(k,) for k in eccr.DEMAND_WORDS])
    con.executemany("INSERT INTO goals VALUES (?,?,?,?,?,?,?,?,?,?)", [
        (g["utility"], float(g["achieved_gwh"]), float(g["goal_gwh"]), float(g["achieved_summer_mw"]), float(g["goal_summer_mw"]),
         float(g["achieved_winter_mw"]), float(g["goal_winter_mw"]), g["basis"], g["goals_order"], g["source"])
        for g in csv.DictReader(open(ROOT / "data" / "goals_vs_achieved_2025.csv"))])
    con.executemany("INSERT INTO eccr_lines VALUES (?,?,?,?,?)", [
        (l["utility"], int(l["line_no"]), l["eccr_program"], int(l["total_cost_usd"]), l["source"])
        for l in csv.DictReader(open(ROOT / "data" / "eccr_2025_costs.csv"))])
    con.executemany("INSERT INTO eccr_filed_totals VALUES (?,?,?,?)", [
        (t["utility"], int(t["ct2_total_usd"]), t["what"], t["source"]) for t in csv.DictReader(open(ROOT / "data" / "ct2_totals_2025.csv"))])
    con.executemany("INSERT INTO dsm_eccr_map VALUES (?,?,?)", [
        (m["utility"], m["dsm_program"], m["eccr_program"] or None) for m in csv.DictReader(open(ROOT / "data" / "dsm_to_eccr_map.csv"))])
    con.executemany("INSERT INTO assumptions VALUES (?,?,?)", ASSUMPTIONS)
    con.commit()
    return con


if __name__ == "__main__":
    con = build()
    counts = {t: con.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
              for t in ("utilities", "programs", "goals", "eccr_lines", "eccr_filed_totals", "dsm_eccr_map", "assumptions")}
    print(f"wrote {DB.relative_to(ROOT)}: " + ", ".join(f"{k} {v}" for k, v in counts.items()))
