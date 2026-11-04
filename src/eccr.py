"""Metrics for Florida IOU conservation programs (2025 reporting year)."""
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEMAND_WORDS = ("load management", "on call", "interruptible", "curtailable", "standby",
                "demand reduction", "demand response", "load control", "prime time", "cyclic",
                "extended", "energy management")  # kW programs: little or no kWh credited

AVOIDED_COST_SCENARIOS = (0.03, 0.06, 0.10)  # $/kWh, ASSUMPTIONS (see docs/METHODOLOGY.md)
PARTICIPATION_SCENARIOS = (0.8, 1.0, 1.2)    # share of actual 2025 participation
FIXED_COST_SHARE = 0.30                      # ASSUMPTION: share of program cost that does not scale


def load_programs(path=ROOT / "data" / "programs_2025.csv"):
    out = []
    for r in csv.DictReader(open(path)):
        kwh = float(r["annual_kwh_at_meter"]) if r["annual_kwh_at_meter"] else None
        cost = float(r["program_cost_thousands"]) * 1000 if r["program_cost_thousands"] else None
        name = r["program"].lower()
        out.append({**r, "kwh": kwh, "cost": cost,
                    "demand_program": any(w in name for w in DEMAND_WORDS)})
    return out


def cost_per_kwh(cost, kwh):
    return None if not kwh or cost is None else cost / kwh


def payback_years(cost, kwh, value_per_kwh):
    """Years of first-year savings, valued at value_per_kwh, needed to equal the program cost."""
    return None if not kwh or cost is None else cost / (kwh * value_per_kwh)


def scenario(cost, kwh, share, fixed=FIXED_COST_SHARE):
    """Participation share scales kWh fully and cost only on its variable part."""
    return cost * (fixed + (1 - fixed) * share), kwh * share


def analyzable(p):
    return (not p["demand_program"]) and p["kwh"] and p["cost"] is not None


def utility_totals(programs):
    t = {}
    for p in programs:
        u = t.setdefault(p["utility"], {"cost": 0.0, "kwh_meter": 0.0, "kwh_gen": 0.0})
        u["cost"] += p["cost"] or 0
        u["kwh_meter"] += p["kwh"] or 0
        u["kwh_gen"] += float(p["annual_kwh_at_generator"] or 0)
    return t
