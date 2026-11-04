"""Build excel/conservation_review_2025.xlsx: the review model as a formula-driven Excel workbook.

Inputs (blue) are the transcribed filing data; every result (black) is an Excel formula, so changing
an assumption or a filed number recalculates the whole model. scripts/verify_excel.py recalculates
the workbook in LibreOffice and checks its results against the Python analysis.
"""
import csv
import sys
from pathlib import Path

from openpyxl import Workbook
from openpyxl.comments import Comment
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
import eccr  # noqa: E402

OUT = ROOT / "excel" / "conservation_review_2025.xlsx"
FONT = "Arial"
BLUE, BLACK, GREEN = "0000FF", "000000", "008000"
HEAD_FILL = PatternFill("solid", fgColor="DCE6F1")
KEY_FILL = PatternFill("solid", fgColor="FFFF00")
THIN = Border(bottom=Side(style="thin", color="BFBFBF"))
USD = '$#,##0;($#,##0);"-"'
USD2 = '$#,##0.00;($#,##0.00);"-"'
NUM = '#,##0;(#,##0);"-"'
PCT = '0.0%;(0.0%);"-"'

wb = Workbook()


def sheet(title, first=False):
    ws = wb.active if first else wb.create_sheet()
    ws.title = title
    return ws


def style(c, color=BLACK, bold=False, fmt=None, fill=None, wrap=False, italic=False):
    c.font = Font(name=FONT, size=10, color=color, bold=bold, italic=italic)
    if fmt:
        c.number_format = fmt
    if fill:
        c.fill = fill
    if wrap:
        c.alignment = Alignment(wrap_text=True, vertical="top")
    return c


def header(ws, row, names, widths=None):
    for j, n in enumerate(names, 1):
        c = ws.cell(row=row, column=j, value=n)
        style(c, bold=True, fill=HEAD_FILL, wrap=True)
        c.border = THIN
    if widths:
        for j, w in enumerate(widths, 1):
            ws.column_dimensions[get_column_letter(j)].width = w
    ws.freeze_panes = ws.cell(row=row + 1, column=1)


def title(ws, text, sub=None):
    style(ws.cell(row=1, column=1, value=text), bold=True).font = Font(name=FONT, size=13, bold=True)
    if sub:
        style(ws.cell(row=2, column=1, value=sub), italic=True, color="595959")


# ------------------------------------------------------------------ README
ws = sheet("README", first=True)
ws.column_dimensions["A"].width = 110
lines = [
    ("2025 Conservation Program Review: Florida investor-owned electric utilities", True),
    ("Independent analysis of public filings. Not a Florida Public Service Commission document.", False),
    ("", False),
    ("What this workbook does", True),
    ("Reproduces the review in docs/recommendation.md with live Excel formulas: goal achievement, savings reconciliation, "
     "DSM-report vs. ECCR true-up cost reconciliation, cost per kWh saved, simple payback, participation sensitivity and screening groups.", False),
    ("", False),
    ("Sheets", True),
    ("Assumptions - every threshold and scenario value used by the formulas. Change them here.", False),
    ("Programs - one row per program from the 2025 DSM annual reports (inputs) plus cost per kWh, payback, tier, screening group and participation scenarios (formulas).", False),
    ("Goals - reported 2025 achievement vs. approved goals, % of goal and met/not met.", False),
    ("Savings check - sum of program pages vs. each utility's reported total.", False),
    ("ECCR costs - program cost lines from each utility's 2025 ECCR final true-up exhibit, and the filed totals they must add to.", False),
    ("Mapping - which DSM-report program corresponds to which ECCR line.", False),
    ("Reconciliation - DSM-report cost vs. ECCR cost for every ECCR line, within the DSM report's rounding.", False),
    ("Summary - headline results, all formulas.", False),
    ("", False),
    ("Colour key", True),
    ("Blue text = input transcribed from a filing or an assumption. Black text = formula. Green text = formula that links to another sheet. "
     "Yellow fill = key assumption.", False),
    ("", False),
    ("Sources", True),
    ("2025 DSM annual reports: floridapsc.com/pscfiles/website-files/PDF/Utilities/Electricgas/ARDemandSide/2025/ (one PDF per utility).", False),
    ("ECCR 2025 final true-up, Docket 20260002-EG (filed May 5, 2026): FPL Exhibit LSN-1 (Doc. 02616-2026, p.27), "
     "Duke Exhibit KR-1T (Doc. 02608-2026, Schedule CT-2 p.2), Tampa Electric Exhibit RGJ-1 (Doc. 02603-2026, Schedule CT-2 p.2).", False),
    ("Each Programs row names its source file and line. FPUC's report gives direct costs only, so FPUC is excluded from the cost-per-kWh screen.", False),
]
for i, (t, b) in enumerate(lines, 1):
    style(ws.cell(row=i, column=1, value=t), bold=b, wrap=True)

# ------------------------------------------------------------------ Assumptions
ws = sheet("Assumptions")
title(ws, "Assumptions", "Blue cells are inputs; yellow marks the analyst's screening choices. None comes from a filing.")
header(ws, 3, ["Assumption", "Value", "Used for"], [46, 14, 80])
A = {}
rows = [
    ("low_tier", "Lower-cost tier: max $ per first-year kWh", 0.15, USD2, "Tier = lower when $/kWh <= this"),
    ("high_tier", "Higher-cost tier: above $ per first-year kWh", 0.60, USD2, "Tier = higher when $/kWh > this"),
    ("fixed_share", "Fixed share of program cost", 0.30, PCT, "Participation sensitivity: this share of cost does not scale with participation"),
    ("value_1", "Value of saved energy, scenario 1 ($/kWh)", 0.03, USD2, "Simple payback (about the current fuel clause on residential tariffs)"),
    ("value_2", "Value of saved energy, scenario 2 ($/kWh)", 0.06, USD2, "Simple payback"),
    ("value_3", "Value of saved energy, scenario 3 ($/kWh)", 0.10, USD2, "Simple payback"),
    ("materiality", "Materiality floor for screening ($)", 100000, USD, "Programs below this cost are listed but not screened"),
    ("part_lo", "Participation scenario: low", 0.8, PCT, "Share of actual 2025 participation"),
    ("part_mid", "Participation scenario: actual", 1.0, PCT, "Share of actual 2025 participation"),
    ("part_hi", "Participation scenario: high", 1.2, PCT, "Share of actual 2025 participation"),
    ("tol_k", "Rounding tolerance per program, $000-rounded reports ($)", 500, USD, "FPL and Duke DSM reports state costs in $000"),
    ("tol_teco", "Rounding tolerance per program, Tampa Electric ($)", 50, USD, "Tampa Electric's DSM report states costs to $0.1k"),
]
for i, (key, label, val, fmt, use) in enumerate(rows, 4):
    style(ws.cell(row=i, column=1, value=label))
    c = style(ws.cell(row=i, column=2, value=val), color=BLUE, fmt=fmt,
              fill=KEY_FILL if key in ("low_tier", "high_tier", "fixed_share") else None)
    style(ws.cell(row=i, column=3, value=use))
    A[key] = f"Assumptions!$B${i}"

# ------------------------------------------------------------------ Programs
progs = eccr.load_programs()
ws = sheet("Programs")
title(ws, "Programs (2025 DSM annual reports)", "Columns A-I are inputs from the reports; J-T are formulas.")
cols = ["Utility", "Program", "Cost basis", "2025 program cost ($)", "First-year kWh saved (meter)", "kWh saved (generator)",
        "Utility-reported net benefits ($)", "Demand-response program?", "Source (file, line)",
        "Screenable (fully loaded cost, kWh credited)", "Cost per first-year kWh ($)",
        "Payback (yrs) at value 1", "Payback (yrs) at value 2", "Payback (yrs) at value 3", "Cost tier",
        "Screened (screenable and >= materiality)", "Screening group",
        "$/kWh at low participation", "$/kWh at actual participation", "$/kWh at high participation"]
header(ws, 3, cols, [16, 44, 16, 15, 15, 15, 15, 11, 30, 13, 12, 11, 11, 11, 10, 13, 22, 12, 12, 12])
r0 = 4
for i, p in enumerate(progs):
    r = r0 + i
    nb = p.get("net_benefits_thousands")
    vals = [p["utility"], p["program"], eccr.cost_basis(p["utility"]),
            None if p["cost"] is None else round(p["cost"], 2),
            p["kwh"], float(p["annual_kwh_at_generator"]) if p["annual_kwh_at_generator"] not in (None, "") else None,
            float(nb) * 1000 if nb not in (None, "") else None, bool(p["demand_program"]),
            f"{p['source_file']}, {p['source_line']}"]
    fmts = [None, None, None, USD, NUM, NUM, USD, None, None]
    for j, (v, f) in enumerate(zip(vals, fmts), 1):
        style(ws.cell(row=r, column=j, value=v), color=BLUE, fmt=f)
    R = str(r)
    f = {
        "J": f'=AND(NOT(H{R}),ISNUMBER(E{R}),E{R}>0,ISNUMBER(D{R}),C{R}="total program cost")',
        "K": f'=IF(AND(NOT(H{R}),ISNUMBER(E{R}),ISNUMBER(D{R})),IF(E{R}>0,D{R}/E{R},""),"")',
        "L": f'=IF(K{R}="","",D{R}/(E{R}*{A["value_1"]}))',
        "M": f'=IF(K{R}="","",D{R}/(E{R}*{A["value_2"]}))',
        "N": f'=IF(K{R}="","",D{R}/(E{R}*{A["value_3"]}))',
        "O": f'=IF(K{R}="","",IF(K{R}<={A["low_tier"]},"lower",IF(K{R}<={A["high_tier"]},"moderate","higher")))',
        "P": f'=AND(J{R},D{R}>={A["materiality"]})',
        "Q": (f'=IF(NOT(P{R}),"",IF(NOT(ISNUMBER(G{R})),IF(O{R}="higher","Needs more support","Insufficient information"),'
              f'IF(AND(O{R}<>"higher",G{R}>0),"Appears cost-effective",IF(AND(O{R}="higher",G{R}<=0),"Needs more support","Mixed signals"))))'),
    }
    for col, part in (("R", "part_lo"), ("S", "part_mid"), ("T", "part_hi")):
        f[col] = (f'=IF(K{R}="","",D{R}*({A["fixed_share"]}+(1-{A["fixed_share"]})*{A[part]})/(E{R}*{A[part]}))')
    for col, formula in f.items():
        c = style(ws[f"{col}{R}"], color=GREEN if "Assumptions!" in formula else BLACK,
                  fmt={"K": USD2, "L": "0.0", "M": "0.0", "N": "0.0", "R": USD2, "S": USD2, "T": USD2}.get(col))
        c.value = formula
PR = (r0, r0 + len(progs) - 1)
ws.auto_filter.ref = f"A3:T{PR[1]}"
ws["H3"].comment = Comment("Identified from the program name (load management, interruptible, curtailable, standby, demand "
                           "response, etc.). These programs are credited in kW, so cost per kWh is not meaningful.", "analyst")
ws["Q3"].comment = Comment("Appears cost-effective: lower/moderate tier and positive net benefits. Needs more support: higher tier "
                           "and zero, negative or no net benefits. Mixed signals: the two disagree. Insufficient information: no "
                           "net benefits reported and tier not higher.", "analyst")


def prog_rng(col):
    return f"Programs!${col}${PR[0]}:${col}${PR[1]}"


# ------------------------------------------------------------------ Goals
goals = list(csv.DictReader(open(ROOT / "data" / "goals_vs_achieved_2025.csv")))
ws = sheet("Goals")
title(ws, "2025 achievement vs. approved goals (at the generator)", "Achieved and goal values are inputs from each DSM report.")
header(ws, 3, ["Utility", "Achieved GWh", "Goal GWh", "% of energy goal", "Energy goal met?",
               "Achieved summer MW", "Goal summer MW", "% of summer goal", "Summer goal met?",
               "Achieved winter MW", "Goal winter MW", "% of winter goal", "Winter goal met?",
               "All three met?", "Basis", "Goals order", "Source"],
       [24, 11, 10, 11, 10, 11, 10, 11, 10, 11, 10, 11, 10, 10, 40, 20, 40])
for i, g in enumerate(goals, 4):
    R = str(i)
    style(ws.cell(row=i, column=1, value=g["utility"]), color=BLUE)
    for col, key in (("B", "achieved_gwh"), ("C", "goal_gwh"), ("F", "achieved_summer_mw"), ("G", "goal_summer_mw"),
                     ("J", "achieved_winter_mw"), ("K", "goal_winter_mw")):
        style(ws[f"{col}{R}"], color=BLUE, fmt="#,##0.000").value = float(g[key])
    for a, b, pc, met in (("B", "C", "D", "E"), ("F", "G", "H", "I"), ("J", "K", "L", "M")):
        style(ws[f"{pc}{R}"], fmt=PCT).value = f"=IF({b}{R}>0,{a}{R}/{b}{R},\"\")"
        style(ws[f"{met}{R}"]).value = f'=IF({a}{R}>={b}{R},"Yes","No")'
    style(ws[f"N{R}"]).value = f'=IF(AND(E{R}="Yes",I{R}="Yes",M{R}="Yes"),"Yes","No")'
    for col, key in (("O", "basis"), ("P", "goals_order"), ("Q", "source")):
        style(ws[f"{col}{R}"], color=BLUE).value = g[key]
GR = (4, 3 + len(goals))

# ------------------------------------------------------------------ Savings check
ws = sheet("Savings check")
title(ws, "Do program pages add up to each utility's reported total?", "GWh at the generator. Reported totals link to the Goals sheet.")
header(ws, 3, ["Utility", "Sum of program pages (GWh)", "Reported total (GWh)", "Difference (GWh)", "Difference (%)", "Note"],
       [24, 16, 14, 14, 12, 90])
notes = {
    "Duke Energy Florida": "Report rounds totals to whole GWh.",
    "Tampa Electric": "Program pages use the 2025-2034 plan rows; the summary basis is not shown in the report.",
    "Florida Public Utilities": "Program pages: 0.127 GWh at meter, 0.131 at generator; the report's Tables 2-3/2-6 appear to swap the labels.",
}
for i, g in enumerate(goals, 4):
    R = str(i)
    style(ws[f"A{R}"]).value = f"=Goals!A{R}"
    ws[f"A{R}"].font = Font(name=FONT, size=10, color=GREEN)
    style(ws[f"B{R}"], color=GREEN, fmt="#,##0.000").value = f"=SUMIFS({prog_rng('F')},{prog_rng('A')},A{R})/1000000"
    style(ws[f"C{R}"], color=GREEN, fmt="#,##0.000").value = f"=Goals!B{R}"
    style(ws[f"D{R}"], fmt="+#,##0.000;-#,##0.000;0.000").value = f"=B{R}-C{R}"
    style(ws[f"E{R}"], fmt="+0.0%;-0.0%;0.0%").value = f"=IF(C{R}<>0,D{R}/C{R},\"\")"
    style(ws[f"F{R}"], wrap=True).value = notes.get(g["utility"], "")

# ------------------------------------------------------------------ ECCR costs
lines_ = list(csv.DictReader(open(ROOT / "data" / "eccr_2025_costs.csv")))
ct2 = list(csv.DictReader(open(ROOT / "data" / "ct2_totals_2025.csv")))
ws = sheet("ECCR costs")
title(ws, "ECCR 2025 final true-up: program cost lines", "Inputs transcribed from Schedule CT-2/CT-3 of each exhibit (Docket 20260002-EG).")
header(ws, 3, ["Utility", "Line", "ECCR line", "2025 actual cost ($)", "Source"], [24, 6, 52, 16, 60])
for i, l in enumerate(lines_, 4):
    for j, (v, fmt) in enumerate(((l["utility"], None), (int(l["line_no"]), None), (l["eccr_program"], None),
                                  (int(l["total_cost_usd"]), USD), (l["source"], None)), 1):
        style(ws.cell(row=i, column=j, value=v), color=BLUE, fmt=fmt)
ER = (4, 3 + len(lines_))
t0 = ER[1] + 3
style(ws.cell(row=t0 - 1, column=1, value="Do the lines add up to the filed total?"), bold=True)
header_row = t0
for j, n in enumerate(["Utility", "", "Filed total", "Sum of lines ($)", "Filed total ($)", "Difference ($)"], 1):
    style(ws.cell(row=header_row, column=j, value=n or None), bold=True, fill=HEAD_FILL)
for i, t in enumerate(ct2, header_row + 1):
    R = str(i)
    style(ws[f"A{R}"], color=BLUE).value = t["utility"]
    style(ws[f"C{R}"], color=BLUE, wrap=True).value = t["what"]
    style(ws[f"D{R}"], fmt=USD).value = f"=SUMIFS($D${ER[0]}:$D${ER[1]},$A${ER[0]}:$A${ER[1]},A{R})"
    style(ws[f"E{R}"], color=BLUE, fmt=USD).value = int(t["ct2_total_usd"])
    style(ws[f"F{R}"], fmt=USD).value = f"=D{R}-E{R}"
CT = (header_row + 1, header_row + len(ct2))

# ------------------------------------------------------------------ Mapping
maps = list(csv.DictReader(open(ROOT / "data" / "dsm_to_eccr_map.csv")))
ws = sheet("Mapping")
title(ws, "DSM-report program to ECCR line", "Columns A-C are the analyst's mapping (inputs); D looks up the DSM-report cost.")
header(ws, 3, ["Utility", "DSM report program", "ECCR line (blank = no ECCR line)", "DSM report cost ($)"], [24, 60, 52, 16])
for i, m in enumerate(maps, 4):
    R = str(i)
    for col, key in (("A", "utility"), ("B", "dsm_program"), ("C", "eccr_program")):
        style(ws[f"{col}{R}"], color=BLUE).value = m[key] or None
    style(ws[f"D{R}"], color=GREEN, fmt=USD).value = f"=SUMIFS({prog_rng('D')},{prog_rng('A')},A{R},{prog_rng('B')},B{R})"
MR = (4, 3 + len(maps))

# ------------------------------------------------------------------ Reconciliation
ws = sheet("Reconciliation")
title(ws, "DSM-report cost vs. ECCR true-up cost, by ECCR line",
      "Within rounding = |difference| <= tolerance per program x number of DSM programs on the line.")
header(ws, 3, ["Utility", "ECCR line", "ECCR cost ($)", "DSM programs on this line", "DSM report cost ($)", "Difference ($)",
               "Tolerance ($)", "Within rounding?", "Has a DSM program page?"], [24, 52, 15, 12, 15, 13, 12, 12, 13])
for i, l in enumerate(lines_, 4):
    R, e = str(i), i - 4 + ER[0]
    style(ws[f"A{R}"], color=GREEN).value = f"='ECCR costs'!A{e}"
    style(ws[f"B{R}"], color=GREEN).value = f"='ECCR costs'!C{e}"
    style(ws[f"C{R}"], color=GREEN, fmt=USD).value = f"='ECCR costs'!D{e}"
    style(ws[f"D{R}"], color=GREEN).value = f"=COUNTIFS(Mapping!$A${MR[0]}:$A${MR[1]},A{R},Mapping!$C${MR[0]}:$C${MR[1]},B{R})"
    style(ws[f"E{R}"], color=GREEN, fmt=USD).value = (f'=IF(D{R}=0,"",SUMIFS(Mapping!$D${MR[0]}:$D${MR[1]},'
                                                      f"Mapping!$A${MR[0]}:$A${MR[1]},A{R},Mapping!$C${MR[0]}:$C${MR[1]},B{R}))")
    style(ws[f"F{R}"], fmt=USD).value = f'=IF(D{R}=0,"",E{R}-C{R})'
    style(ws[f"G{R}"], color=GREEN, fmt=USD).value = (f'=IF(D{R}=0,"",D{R}*IF(A{R}="Tampa Electric",{A["tol_teco"]},{A["tol_k"]}))')
    style(ws[f"H{R}"]).value = f'=IF(D{R}=0,"",IF(ABS(F{R})<=G{R},"Yes","No"))'
    style(ws[f"I{R}"]).value = f'=IF(D{R}>0,"Yes","No")'
RR = (4, 3 + len(lines_))

# ------------------------------------------------------------------ Summary
ws = sheet("Summary")
title(ws, "Summary (all formulas)", "Updates when inputs or assumptions change.")
ws.column_dimensions["A"].width = 64
for c in "BCDE":
    ws.column_dimensions[c].width = 16
rr = lambda col: f"Reconciliation!${col}${RR[0]}:${col}${RR[1]}"
row = 4
style(ws.cell(row=row, column=1, value="Goals"), bold=True); row += 1
style(ws.cell(row=row, column=1, value="Utilities meeting all three 2025 goals"))
style(ws.cell(row=row, column=2), color=GREEN).value = f'=COUNTIF(Goals!$N${GR[0]}:$N${GR[1]},"Yes")'
style(ws.cell(row=row, column=3), color=GREEN).value = f"=ROWS(Goals!$N${GR[0]}:$N${GR[1]})"
style(ws.cell(row=row, column=4, value="of utilities")); row += 2

style(ws.cell(row=row, column=1, value="Cost reconciliation (DSM report vs. ECCR true-up)"), bold=True)
for j, n in enumerate(["Utility", "Lines matched", "Lines checked", "No-page ECCR cost ($)", "Share of filed total"], 1):
    style(ws.cell(row=row + 1, column=j, value=n), bold=True, fill=HEAD_FILL)
row += 2
first = row
for t in ct2:
    u, R = t["utility"], str(row)
    style(ws[f"A{R}"], color=BLUE).value = u
    style(ws[f"B{R}"], color=GREEN).value = f'=COUNTIFS({rr("A")},A{R},{rr("H")},"Yes")'
    style(ws[f"C{R}"], color=GREEN).value = f'=COUNTIFS({rr("A")},A{R},{rr("I")},"Yes")'
    style(ws[f"D{R}"], color=GREEN, fmt=USD).value = f'=SUMIFS({rr("C")},{rr("A")},A{R},{rr("I")},"No")'
    total_ref = f"SUMIFS('ECCR costs'!$E${CT[0]}:$E${CT[1]},'ECCR costs'!$A${CT[0]}:$A${CT[1]},A{R})"
    style(ws[f"E{R}"], color=GREEN, fmt=PCT).value = f"=D{R}/{total_ref}"
    row += 1
R = str(row)
style(ws[f"A{R}"], bold=True).value = "Total"
for col in "BCD":
    style(ws[f"{col}{R}"], bold=True, fmt=USD if col == "D" else None).value = f"=SUM({col}{first}:{col}{row - 1})"
style(ws[f"E{R}"], color=GREEN, bold=True, fmt=PCT).value = f"=D{R}/SUM('ECCR costs'!$E${CT[0]}:$E${CT[1]})"
row += 2

style(ws.cell(row=row, column=1, value="Screening (programs costing at least the materiality floor)"), bold=True); row += 1
SCREEN_FIRST = row
for grp in ["Appears cost-effective", "Mixed signals", "Needs more support", "Insufficient information"]:
    style(ws.cell(row=row, column=1, value=grp))
    style(ws.cell(row=row, column=2), color=GREEN).value = f'=COUNTIF({prog_rng("Q")},A{row})'
    row += 1
style(ws.cell(row=row, column=1, value="Programs screened"), bold=True)
style(ws.cell(row=row, column=2), bold=True).value = f"=SUM(B{SCREEN_FIRST}:B{row - 1})"
row += 2
style(ws.cell(row=row, column=1, value="Portfolio cost per first-year kWh, all screenable programs ($)"))
style(ws.cell(row=row, column=2), color=GREEN, fmt="$0.000").value = (
    f'=SUMIFS({prog_rng("D")},{prog_rng("J")},TRUE)/SUMIFS({prog_rng("E")},{prog_rng("J")},TRUE)')
row += 1
style(ws.cell(row=row, column=1, value="Participation sensitivity: change in $/kWh at low participation"))
style(ws.cell(row=row, column=2), color=GREEN, fmt="+0.0%;-0.0%").value = (
    f'=({A["fixed_share"]}+(1-{A["fixed_share"]})*{A["part_lo"]})/{A["part_lo"]}-1')
row += 1
style(ws.cell(row=row, column=1, value="Participation sensitivity: change in $/kWh at high participation"))
style(ws.cell(row=row, column=2), color=GREEN, fmt="+0.0%;-0.0%").value = (
    f'=({A["fixed_share"]}+(1-{A["fixed_share"]})*{A["part_hi"]})/{A["part_hi"]}-1')

OUT.parent.mkdir(exist_ok=True)
wb.save(OUT)
print(f"wrote {OUT.relative_to(ROOT)} ({len(progs)} programs, {len(lines_)} ECCR lines)")
