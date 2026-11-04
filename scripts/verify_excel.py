"""Check the Excel model's computed values against the Python analysis.

Reads the cached (recalculated) values in excel/conservation_review_2025.xlsx, so recalculate the
workbook after rebuilding it (opening and saving it in Excel does this; so does LibreOffice).
Exits non-zero on any mismatch. Also used by tests/test_excel.py.
"""
import json
import sys
from pathlib import Path

from openpyxl import load_workbook

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
import eccr  # noqa: E402

XLSX = ROOT / "excel" / "conservation_review_2025.xlsx"
LOW, HIGH = 0.15, 0.60  # must match Assumptions defaults and scripts/write_recommendation.py


def expected_group(p):
    if not (eccr.rankable(p) and p["cost"] >= 100_000):
        return None
    cpk = p["cost"] / p["kwh"]
    tier = "lower" if cpk <= LOW else "moderate" if cpk <= HIGH else "higher"
    nb = p.get("net_benefits_thousands")
    if nb in (None, ""):
        return "Needs more support" if tier == "higher" else "Insufficient information"
    nb = float(nb)
    if tier != "higher" and nb > 0:
        return "Appears cost-effective"
    if tier == "higher" and nb <= 0:
        return "Needs more support"
    return "Mixed signals"


def check():
    problems = []
    wb = load_workbook(XLSX, data_only=True)
    ws = wb["Programs"]
    if ws["K4"].value is None and ws["J4"].value is None:
        return ["workbook has no computed values: recalculate it first"]
    progs = eccr.load_programs()
    for i, p in enumerate(progs):
        r = 4 + i
        if ws[f"B{r}"].value != p["program"]:
            problems.append(f"row {r}: program order differs")
            continue
        k = ws[f"K{r}"].value
        exp = p["cost"] / p["kwh"] if eccr.analyzable(p) else None
        if (exp is None) != (k in (None, "")) or (exp is not None and abs(k - exp) > 1e-9):
            problems.append(f"{p['program']}: $/kWh {k} vs {exp}")
        g = ws[f"Q{r}"].value or None
        if g != expected_group(p):
            problems.append(f"{p['program']}: group {g!r} vs {expected_group(p)!r}")

    recon = json.load(open(ROOT / "outputs" / "reconciliation.json"))["summary"]
    s = wb["Summary"]
    found = {}
    for row in s.iter_rows(min_row=1, max_row=s.max_row):
        if row[0].value in recon:
            found[row[0].value] = [c.value for c in row[1:5]]
    for u, v in recon.items():
        got = found.get(u)
        exp = [v["matched"], v["matched"] + v["mismatched"], v["extra_total"], v["extra_share"]]
        if not got or got[0] != exp[0] or got[1] != exp[1] or abs(got[2] - exp[2]) > 0.5 or abs(got[3] - exp[3]) > 1e-9:
            problems.append(f"Summary {u}: {got} vs {exp}")

    counts = {}
    for row in s.iter_rows(min_row=1, max_row=s.max_row):
        if row[0].value in ("Appears cost-effective", "Mixed signals", "Needs more support", "Insufficient information"):
            counts[row[0].value] = row[1].value
    exp_counts = {}
    for p in progs:
        g = expected_group(p)
        if g:
            exp_counts[g] = exp_counts.get(g, 0) + 1
    for k_, v in exp_counts.items():
        if counts.get(k_) != v:
            problems.append(f"screening count {k_}: {counts.get(k_)} vs {v}")

    tot = eccr.utility_totals(progs)
    sc = wb["Savings check"]
    for r in range(4, 8):
        u, got = sc[f"A{r}"].value, sc[f"B{r}"].value
        if abs(got - tot[u]["kwh_gen"] / 1e6) > 1e-9:
            problems.append(f"Savings check {u}: {got}")

    ec = wb["ECCR costs"]
    for row in ec.iter_rows(min_row=1, max_row=ec.max_row):
        if row[0].value in recon and isinstance(row[5].value, (int, float)) and row[3].value is not None and row[2].value and "CT-2" in str(row[2].value):
            if abs(row[5].value) > 2:
                problems.append(f"ECCR lines vs filed total {row[0].value}: {row[5].value}")
    return problems


if __name__ == "__main__":
    probs = check()
    if probs:
        print("MISMATCHES:\n" + "\n".join(probs))
        sys.exit(1)
    print("Excel model matches the Python analysis: program $/kWh and screening groups, reconciliation summary, "
          "screening counts, savings totals and ECCR line totals.")
