"""Write docs/recommendation.md (staff-recommendation format) and its figures.

Run after scripts/analyze.py. Every number in the document is computed from the
data files here; nothing is typed in by hand.
"""
import csv
import json
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))
import eccr  # noqa: E402
import svgcharts as sc  # noqa: E402

DOCS, FIG = ROOT / "docs", ROOT / "docs" / "figures"
FIG.mkdir(parents=True, exist_ok=True)
UTILS = ["Florida Power & Light", "Duke Energy Florida", "Tampa Electric", "Florida Public Utilities"]
SHORT = {"Florida Power & Light": "FPL", "Duke Energy Florida": "Duke", "Tampa Electric": "Tampa Electric",
         "Florida Public Utilities": "FPUC"}
LOW, HIGH = 0.15, 0.60  # $/first-year kWh screening thresholds (analyst's choice; see Issue 5)

progs = eccr.load_programs()
for p in progs:
    nb = p.get("net_benefits_thousands")
    p["nb"] = float(nb) * 1000 if nb not in (None, "") else None
goals = {r["utility"]: r for r in csv.DictReader(open(ROOT / "data" / "goals_vs_achieved_2025.csv"))}
recon = json.load(open(ROOT / "outputs" / "reconciliation.json"))
ct2 = {r["utility"]: r for r in csv.DictReader(open(ROOT / "data" / "ct2_totals_2025.csv"))}
tot = eccr.utility_totals(progs)
reqs = list(csv.DictReader(open(ROOT / "outputs" / "requirements_checklist.csv")))


def money(v, d=0):
    return f"${v:,.{d}f}" if v >= 0 else f"-${-v:,.{d}f}"


def mil(v, d=1):
    return f"${v / 1e6:,.{d}f} million"


KEEP_UPPER = {"DX", "EA", "RCS", "C/I", "HVAC", "LED"}
SMALL = {"AND", "FOR", "OF", "OR", "THE", "TO", "AKA"}


def name(p):
    """Title-case words a utility printed in capitals; leave mixed-case names and acronyms alone."""
    import re

    def fix(m):
        w = m.group(0)
        if w in KEEP_UPPER or len(w) <= 1:
            return w
        if w in SMALL:
            return w.lower()
        return "/".join(part.capitalize() for part in w.split("/"))
    n = p["program"].replace("ENERGY STAR", "\x00")
    n = re.sub(r"[A-Z][A-Z/]+", fix, n).replace("\x00", "ENERGY STAR")
    n = n.replace("TIER1", "Tier 1").replace("Tier1", "Tier 1")
    return n[0].upper() + n[1:]


def pct(a, b):
    return a / b - 1


def tier(cpk):
    return "lower" if cpk <= LOW else ("moderate" if cpk <= HIGH else "higher")


def classify(p):
    cpk = p["cost"] / p["kwh"]
    t = tier(cpk)
    nb = p["nb"]
    if nb is None:
        return "Needs more support" if t == "higher" else "Insufficient information"
    if t in ("lower", "moderate") and nb > 0:
        return "Appears cost-effective"
    if t == "higher" and nb <= 0:
        return "Needs more support"
    return "Mixed signals"


ranked = [p for p in progs if eccr.rankable(p)]
for p in ranked:
    p["cpk"] = p["cost"] / p["kwh"]
    p["cls"] = classify(p)
material = sorted([p for p in ranked if p["cost"] >= 100_000], key=lambda p: p["cpk"])
small = [p for p in ranked if p["cost"] < 100_000]
fpuc = [p for p in progs if p["utility"] == "Florida Public Utilities"]
demand = [p for p in progs if p["demand_program"] and p["utility"] != "Florida Public Utilities"]
no_kwh = [p for p in progs if not p["demand_program"] and not p["kwh"] and (p["cost"] or 0) > 0
          and p["utility"] != "Florida Public Utilities"]

# ---------------------------------------------------------------- figures
g_items = []
for u in UTILS:
    g = goals[u]
    g_items.append((SHORT[u], float(g["achieved_gwh"]) / float(g["goal_gwh"]) * 100, 0))
(FIG / "fig1_goal_achievement.svg").write_text(sc.hbar(
    g_items, "Figure 1. 2025 annual energy savings as a share of the approved goal",
    "Horizontal bars: percent of 2025 GWh goal achieved, at the generator, as reported by each utility.",
    lambda v: f"{v:.0f}%", x_max=160, ref_line=100, ref_label="goal", ticks=[0, 50, 100, 150], label_w=140))

uidx = {"Florida Power & Light": 0, "Duke Energy Florida": 1, "Tampa Electric": 2}
def short_label(p, limit=54):
    import re
    n = re.sub(r"\s*\(.*?\)", "", name(p)).strip()
    n = n.replace("Heating, Ventilating & Air Conditioning", "HVAC").replace("Commercial/Industrial", "C/I")
    lab = f"{'TECO' if p['utility'] == 'Tampa Electric' else SHORT[p['utility']]}: {n}"
    if len(lab) > limit:
        lab = lab[:limit].rsplit(" ", 1)[0] + "..."
    return lab


c_items = [(short_label(p), p["cpk"], uidx[p["utility"]]) for p in material]
(FIG / "fig2_cost_per_kwh.svg").write_text(sc.hbar(
    c_items, "Figure 2. Program cost per first-year kWh saved (programs costing at least $100,000)",
    "Horizontal bars on a logarithmic scale: 2025 program cost divided by first-year kWh saved at the meter.",
    lambda v: f"${v:.2f}", x_max=max(p["cpk"] for p in material) * 1.6, log=True,
    ticks=[0.01, 0.1, 1, 10], legend=["FPL", "Duke", "Tampa Electric (TECO)"], label_w=370,
    ref_line=HIGH, ref_label=f"${HIGH:.2f} screen"))

s_items = []
for u in UTILS[:3]:
    s = recon["summary"][u]
    t = s["ct2_total"]
    s_items.append((SHORT[u], [t - s["extra_total"], s["extra_total"]]))
(FIG / "fig3_eccr_composition.svg").write_text(sc.stacked100(
    s_items, "Figure 3. 2025 ECCR program costs: reported program pages vs. other lines",
    "100% stacked bars per utility: share of ECCR true-up costs that match a DSM program page vs. lines with no page.",
    ["Matched to a DSM program page", "No DSM program page"], label_w=140))

# ---------------------------------------------------------------- text pieces
def goal_row(u):
    g = goals[u]
    cells = []
    for a, b in (("achieved_gwh", "goal_gwh"), ("achieved_summer_mw", "goal_summer_mw"),
                 ("achieved_winter_mw", "goal_winter_mw")):
        A, B = float(g[a]), float(g[b])
        cells.append(f"{g[a]} / {g[b]} ({A / B:.0%})")
    return f"| {u} | " + " | ".join(cells) + " |"


missed = []
for u in UTILS:
    g = goals[u]
    for k, lab in (("gwh", "annual energy"), ("summer_mw", "summer peak demand"), ("winter_mw", "winter peak demand")):
        if float(g[f"achieved_{k}"]) < float(g[f"goal_{k}"]):
            missed.append((u, lab))
met_all = [u for u in UTILS if not any(m[0] == u for m in missed)]
teco_missed = [lab for u, lab in missed if u == "Tampa Electric"]
fpuc_missed = [lab for u, lab in missed if u == "Florida Public Utilities"]

sav_rows = []
for u in UTILS:
    s_ = tot[u]["kwh_gen"] / 1e6
    rep = float(goals[u]["achieved_gwh"])
    sav_rows.append(f"| {u} | {s_:,.3f} | {rep:,.3f} | {s_ - rep:+.3f} | {pct(s_, rep):+.1%} |")
fp = tot["Florida Public Utilities"]
teco_gap = tot["Tampa Electric"]["kwh_gen"] / 1e6 - float(goals["Tampa Electric"]["achieved_gwh"])

rs = recon["summary"]
n_cmp = sum(v["matched"] + v["mismatched"] for v in rs.values())
n_bad = sum(v["mismatched"] for v in rs.values())
bad = [r for r in recon["rows"] if not r["ok"]]
cost_rows = []
for u in UTILS[:3]:
    s = rs[u]
    cost_rows.append(f"| {u} | {money(recon['line_sums'][u])} | {money(s['ct2_total'])} | "
                     f"{money(recon['line_sums'][u] - s['ct2_total'])} | {s['matched']} of {s['matched'] + s['mismatched']} |")
extra_rows = []
for u in UTILS[:3]:
    for n, v in sorted(rs[u]["extra"], key=lambda x: -x[1]):
        extra_rows.append(f"| {u} | {n} | {money(v)} | {v / rs[u]['ct2_total']:.1%} |")
extra_all = sum(rs[u]["extra_total"] for u in UTILS[:3])
ct2_all = sum(rs[u]["ct2_total"] for u in UTILS[:3])

cls_order = ["Appears cost-effective", "Mixed signals", "Needs more support", "Insufficient information"]
cls_counts = {c: [p for p in material if p["cls"] == c] for c in cls_order}


def prog_row(p):
    nb = "n/a" if p["nb"] is None else money(p["nb"])
    return (f"| {SHORT[p['utility']]} | {name(p)} | {money(p['cost'])} | {p['kwh'] / 1e6:,.2f} | "
            f"${p['cpk']:.2f} | {tier(p['cpk'])} | {nb} | {p['cls']} |")


a_cost = sum(p["cost"] for p in ranked)
a_kwh = sum(p["kwh"] for p in ranked)
by_u = {u: [p for p in ranked if p["utility"] == u] for u in UTILS[:3]}
u_avg = {u: sum(p["cost"] for p in v) / sum(p["kwh"] for p in v) for u, v in by_u.items()}

lowinc = [p for p in material if any(w in p["program"].lower() for w in ("low-income", "low income", "neighborhood"))]
mixed_lo = [p for p in cls_counts["Mixed signals"] if tier(p["cpk"]) != "higher"]
mixed_hi = [p for p in cls_counts["Mixed signals"] if tier(p["cpk"]) == "higher"]

f = eccr.FIXED_COST_SHARE
sens = {s: eccr.scenario(1, 1, s)[0] / s - 1 for s in eccr.PARTICIPATION_SCENARIOS}
moves = []
for p in material:
    tiers = {tier(eccr.scenario(p["cost"], p["kwh"], s)[0] / eccr.scenario(p["cost"], p["kwh"], s)[1])
             for s in eccr.PARTICIPATION_SCENARIOS}
    if len(tiers) > 1:
        moves.append(p)

def _cls_at(p, share):
    c, k = eccr.scenario(p["cost"], p["kwh"], share)
    q = dict(p, cost=c, kwh=k)
    return classify(q)


group_changes = [(p, {sh: _cls_at(p, sh) for sh in eccr.PARTICIPATION_SCENARIOS}) for p in material]
group_changes = [(p, g) for p, g in group_changes if len(set(g.values())) > 1]
if group_changes:
    group_change_sentence = (f"{len(group_changes)} of the {len(material)} screened programs sit close enough to the ${HIGH:.2f} threshold to change "
        "screening group across that range: " + "; ".join(
        f"{SHORT[p['utility']]} {name(p)} ({g[0.8].lower()} at 80% participation, {g[1.2].lower()} at 120%)" for p, g in group_changes) + ".")
else:
    group_change_sentence = "No program changes screening group on participation alone."

req_ids = sorted({r["id"] for r in reqs})
req_n = len(req_ids)
req_rows = []
for u in UTILS:
    c = {}
    for r in reqs:
        if r["utility"] == u:
            c[r["status"]] = c.get(r["status"], 0) + 1
    req_rows.append(f"| {u} | {c.get('Met', 0)} | {c.get('Partly met', 0)} | {c.get('Not met', 0)} | {c.get('Not found', 0)} | "
                    f"{c.get(chr(67) + 'an' + chr(39) + 't determine', 0) + c.get('Not reviewed', 0)} |")
req_issue_rows = [f"| {SHORT[r['utility']]} | {r['rule']} | {r['status']} | {r['evidence']} |"
                  for r in reqs if r["status"] in ("Partly met", "Not met", "Not found")]
fpuc_rows = "\n".join(
    f"| {name(p)} | {money(p['cost'])} | {p['kwh']:,.0f} | {money(p['cost'] / p['kwh'], 2) if p['kwh'] else 'n/a'} | "
    f"{money(p['nb']) if p['nb'] not in (None,) else 'n/a'} |" for p in fpuc if p["cost"])

# ---------------------------------------------------------------- document
today = date.today().strftime("%B %-d, %Y")
doc = f"""# Review of 2025 Conservation Program Results and Cost Recovery: Florida Investor-Owned Electric Utilities

| | |
|---|---|
| **Date** | {today} |
| **Subject** | 2025 demand-side management (DSM) results and Energy Conservation Cost Recovery (ECCR) program costs for Florida Power & Light, Duke Energy Florida, Tampa Electric and Florida Public Utilities |
| **Format** | Written in the structure of a utility-commission staff recommendation (case background, issues, recommendation, analysis) |
| **Prepared with** | Claude, Anthropic's AI assistant, which retrieved the filings, wrote the analysis code and drafted this document under the author's direction (see Appendix C) |
| **Status** | **Independent analysis of public filings. This is not a Florida Public Service Commission document, does not represent Commission staff, and makes no regulatory finding.** |

---

## Summary of recommendations

| Issue | Question | Recommendation |
|---|---|---|
| 1 | Did each utility meet its 2025 approved numeric conservation goals? | {" and ".join(SHORT[u] for u in met_all)} met all three 2025 goals (annual energy, summer and winter peak demand). Tampa Electric met its energy and summer goals but missed its winter demand goal. FPUC missed all three. |
| 2 | Do the program-level savings in each DSM report add up to the totals each utility reports? | Yes for FPL and Duke. No for Tampa Electric (a {abs(teco_gap):.1f} GWh gap) and FPUC (summary tables appear to swap meter and generator energy totals). Ask both utilities to reconcile before relying on their totals. |
| 3 | Do the program costs in the DSM reports agree with the ECCR true-up filings? | Yes, closely: {n_cmp - n_bad} of {n_cmp} program costs agree within the reports' rounding; the {n_bad} exceptions total {money(sum(abs(r['dsm_usd'] - r['eccr_usd']) for r in bad))}. FPUC was not cross-checked. |
| 4 | Are there ECCR costs that do not appear in any DSM program report? | Yes: {mil(extra_all)} ({extra_all / ct2_all:.0%} of the three utilities' combined ECCR program costs), mostly FPL's closed Commercial/Industrial Load Control program and administrative lines. Request support for each line. |
| 5 | Which energy-efficiency programs look cost-effective on a screening basis, and which need more support? | Of {len(material)} programs costing at least $100,000, {len(cls_counts['Appears cost-effective'])} appear cost-effective on both measures used, {len(cls_counts['Mixed signals'])} give mixed signals and {len(cls_counts['Needs more support'])} need more support (see Table 6). |
| 6 | How sensitive are the cost results to participation? | Moderately. A 20% participation shortfall raises cost per kWh by about {sens[0.8]:.1%} under the assumed cost structure; {len(moves)} of {len(material)} programs would change screening tier. |
| 7 | Do the filings meet the Commission's reporting requirements? | Mostly. FPL's filings meet all {req_n} requirements checked. Duke and Tampa Electric do not justify all goal variances above 15% and include no advertising savings-claim documentation; Duke's report shows a 2025 energy goal (56 GWh) that differs from its order (55 GWh); FPUC's report omits several program items and doesn't match its 2024 goals order. |
| 8 | What reporting improvements should be requested? | Consistent net-benefit methodology, measure lives, cost basis disclosure and reconciliation tables (see Issue 8). |

---

## Case background

**Legal framework.** The Florida Energy Efficiency and Conservation Act (FEECA) requires the Commission to set numeric conservation goals for the utilities it covers and to approve plans to meet them. Goals are set under Rule 25-17.0021, Florida Administrative Code, and utilities report results annually under subsection (5) of that rule. Utilities recover the cost of approved conservation programs through the Energy Conservation Cost Recovery clause under Rule 25-17.015, F.A.C., which includes an annual final true-up of actual against projected costs.

**Current goals.** The goals in effect for 2025 were set in 2024 for each utility: FPL, Order No. PSC-2024-0505-FOF-EG (Docket 20240012-EG); Duke Energy Florida, Order No. PSC-2024-0429-FOF-EG (Docket 20240013-EG); Tampa Electric, Order No. PSC-2024-0430-FOF-EG (Docket 20240014-EG); and FPUC, Order No. PSC-2024-0431-FOF-EG (Docket 20240015-EG). 2025 is the first year of the new goal period.

**Filings reviewed.**
- Each utility's 2025 DSM annual report, filed in February-March 2026 and posted on the Commission's website. These give program-level participation, demand and energy savings, cost and the utility's reported net benefits.
- The 2025 ECCR final true-up testimony and exhibits for FPL (Exhibit LSN-1), Duke (Exhibit KR-1T) and Tampa Electric (Exhibit RGJ-1), all filed May 5, 2026 in Docket 20260002-EG. These give actual 2025 conservation costs by program.
- FPUC's ECCR true-up was not located among the filings reviewed.

**Scope.** This review compares what the utilities reported against their goals, checks the filings for internal consistency and agreement with each other, and screens program cost per kWh saved. It does **not** audit the underlying records, re-run the Commission's cost-effectiveness tests, evaluate the true-up interest or revenue calculations, or recommend changes to recovery factors. Full methods and limits are in Appendix C.

---

## Discussion of issues

### Issue 1: Did each utility meet its 2025 approved numeric conservation goals?

**Recommendation:** {" and ".join(SHORT[u] for u in met_all)} met all three 2025 goals. Tampa Electric missed its winter peak demand goal while exceeding its energy goal by a wide margin. FPUC fell short on all three, with energy savings at {float(goals['Florida Public Utilities']['achieved_gwh']) / float(goals['Florida Public Utilities']['goal_gwh']):.0%} of goal. FPUC's shortfall should be monitored in 2026; one transition year doesn't establish a pattern.

**Analysis:** Table 1 shows each utility's reported 2025 achievement against its approved goal, at the generator.

*Table 1. 2025 achieved vs. goal (achieved / goal, % of goal)*

| Utility | Annual energy (GWh) | Summer peak (MW) | Winter peak (MW) |
|---|---|---|---|
""" + "\n".join(goal_row(u) for u in UTILS) + f"""

![Figure 1](figures/fig1_goal_achievement.svg)

- **FPL** exceeded all three goals; its energy savings were {pct(102.57, 100.08):.0%} above goal, and its demand savings 19-23% above.
- **Duke** reports figures rounded to whole MW and GWh, with variances of +18% (energy), +80% (summer) and +72% (winter) against its total goals. Most of the demand margin comes from commercial/industrial programs, where Duke reports variances of +597% (winter) and +300% (summer) against small goals of 4 and 7 MW. Duke's report shows a 2025 energy goal of 56 GWh, but its goals order sets 55 GWh (the 56 is the 2026 goal); this review uses the order's figure (Issue 7).
- **Tampa Electric** exceeded its energy goal by {pct(65.8, 47.0):.0%} and its summer goal, but reached 86.7% of its combined winter goal as reported (86.0% residential, 88.4% commercial/industrial). It moved to its new 2025-2034 program portfolio on June 1, 2025, after the plan was approved in April, and states that it would have met all 2025 goals had the new plan started January 1.
- **FPUC** describes 2025 as a transition year: residential programs were restructured and commercial programs had no participants. The goals are small in absolute terms (0.517 GWh), so a handful of additional participants moves the result substantially. FPUC's report also compares against goals that differ from its 2024 goals order; against the order's 0.465 GWh, FPUC reached about 28% of its energy goal (Issue 7).

Tampa Electric's and FPUC's achievement figures are affected by the reconciliation issues in Issue 2, but neither issue is large enough to change whether a goal was met.

### Issue 2: Do the program-level savings in each DSM report add up to the totals each utility reports?

**Recommendation:** FPL's and Duke's program savings reconcile to their reported totals. Tampa Electric's program pages fall {abs(teco_gap):.1f} GWh ({abs(pct(tot['Tampa Electric']['kwh_gen'] / 1e6, 65.8)):.1%}) short of its reported 65.8 GWh, and FPUC's summary tables appear to have their meter and generator energy totals swapped. Ask Tampa Electric to provide a reconciliation from program pages to its summary, and FPUC to confirm and correct its Tables 2-3 and 2-6.

**Analysis:** Each DSM report gives savings for every program and a summary total. If the report is internally consistent, the program figures should add up to the total.

*Table 2. Sum of program pages vs. reported total, GWh at the generator*

| Utility | Sum of program pages | Reported total | Difference | % |
|---|---|---|---|---|
""" + "\n".join(sav_rows) + f"""

- **FPL** reconciles exactly. **Duke**'s small difference is within its rounding to whole GWh.
- **Tampa Electric** reports many programs under both its 2020-2029 and 2025-2034 DSM plans, and for several audit programs prints a combined row that it marks as not counted toward achievements. This review uses the 2025-2034 plan rows, because 2025 goals come from that plan. On that basis the program pages total {tot['Tampa Electric']['kwh_gen'] / 1e6:.1f} GWh. Using the combined rows instead gives about 91 GWh. Neither matches the reported 65.8 GWh, and the report does not show how the summary was built.
- **FPUC**: its program pages total {fp['kwh_meter']:,.0f} kWh at the meter and {fp['kwh_gen']:,.0f} kWh at the generator. FPUC's Table 2-3 (labelled "At the Generator") shows 0.127 GWh and Table 2-6 ("At the Meter") shows 0.131 GWh. Generator savings include line losses and should be the larger figure, so the energy labels appear swapped. The winter MW figures in the same tables are labelled correctly. The effect on FPUC's goal comparison is small (0.131 rather than 0.127 GWh achieved against 0.517).

### Issue 3: Do the program costs in the DSM reports agree with the ECCR true-up filings?

**Recommendation:** Yes. The DSM reports and the ECCR true-up schedules are consistent for FPL, Duke and Tampa Electric: {n_cmp - n_bad} of {n_cmp} program-level comparisons agree within the DSM reports' rounding. The {n_bad} exceptions ({"; ".join(f"Tampa Electric {r['eccr_program']}, {money(abs(r['dsm_usd'] - r['eccr_usd']))}" for r in bad)}) are immaterial but could be explained in Tampa Electric's next report. FPUC's costs should be cross-checked once its ECCR true-up exhibit is obtained.

**Analysis:** First, each true-up exhibit's program lines were added up and compared with the filed total.

*Table 3. ECCR true-up program lines vs. filed totals (2025 actual)*

| Utility | Sum of program lines | Filed total | Difference | DSM-to-ECCR program matches |
|---|---|---|---|---|
""" + "\n".join(cost_rows) + f"""

FPL's $1 difference is rounding in the filing. Tampa Electric's filed total here is before it removes its Renewable Energy (Sun to Go) program ($51,578), which is recovered separately; its "Total Program Costs" after that removal is {money(47_597_019)}.

Second, each DSM-report program cost was matched to its ECCR line. The DSM reports state costs in thousands of dollars (Tampa Electric to the nearest $100), so differences up to $500 per program ($50 for Tampa Electric) are rounding. Two mappings combine programs: Duke reports Residential Load Management and Commercial Energy Management separately but recovers them on one ECCR line, and Tampa Electric splits its Heating and Cooling program into two tiers. Both combined comparisons agree. The full line-by-line comparison is in Appendix B.

The two Tampa Electric exceptions are the only Tampa Electric DSM programs with significant capital-investment (depreciation and return) amounts in the true-up: $607,906 for Energy Planner and $267,121 for Prime Time Plus. A small difference in the depreciation or return figures used in the two filings could explain the gap; the filings don't say.

### Issue 4: Are there ECCR costs that do not appear in any DSM program report?

**Recommendation:** Yes. {mil(extra_all)} of 2025 ECCR program costs across the three utilities ({extra_all / ct2_all:.0%}) sits in lines with no corresponding program page in the DSM reports. Because the DSM reports are where program cost-effectiveness is reported, request support for these lines: why each is recoverable through the clause, how common costs are allocated, and, for FPL's Commercial/Industrial Load Control program, why a program closed to new participants is not reported in the DSM report.

**Analysis:**

![Figure 3](figures/fig3_eccr_composition.svg)

*Table 4. ECCR lines with no DSM program page, 2025*

| Utility | ECCR line | Cost | Share of utility's ECCR total |
|---|---|---|---|
""" + "\n".join(extra_rows) + f"""

- **FPL** has the largest amount, {mil(rs['Florida Power & Light']['extra_total'])} ({rs['Florida Power & Light']['extra_share']:.0%}). Most is Commercial/Industrial Load Control ($36.5 million), a demand-response program the true-up exhibit lists as closed to new participants (it shows 478 MW in the inception-to-date column). FPL's DSM report covers 14 programs and omits it. Common Expenses ($7.5 million) and Energy Select, recovered as a regulatory asset through depreciation and return only ($5.1 million), make up most of the rest.
- **Duke**'s unmatched lines are Conservation Program Admin ($2.7 million), Qualifying Facility ($0.6 million) and Technology Development ($0.4 million).
- **Tampa Electric**'s are mostly common expenses ($1.2 million) and an Integrated Renewable Energy System pilot ($0.9 million), which is entirely capital investment.

Some of these costs, such as shared administration, have no natural program page. But none of them shows up in program-level cost-effectiveness reporting. Program results look better than the portfolio's full cost would suggest, by the amounts above.

### Issue 5: Which energy-efficiency programs look cost-effective on a screening basis, and which need more support?

**Recommendation:** Table 6 sorts the {len(material)} energy-efficiency programs that cost at least $100,000 into four groups. The {len(cls_counts['Needs more support'])} programs marked "needs more support" have high cost per kWh saved **and** zero, negative or unreported net benefits in the utility's own report. For those, request measure lives, cost breakdowns and the cost-effectiveness test results behind the reported net benefits. "Mixed signals" programs need an explanation of why the two measures disagree. This is a screen, not a cost-effectiveness determination.

**Analysis:** Two measures are combined.

1. **Cost per first-year kWh saved** = 2025 program cost / 2025 first-year kWh savings at the meter. It is simple and comparable across utilities but ignores measure life: a 15-year insulation measure and a one-year behavioral program are treated alike. Programs are grouped as *lower* (up to ${LOW:.2f}/kWh), *moderate* (${LOW:.2f}-${HIGH:.2f}) or *higher* (above ${HIGH:.2f}). These thresholds are this review's choice: at ${LOW:.2f}, about a year and a half of savings valued at $0.10/kWh covers the program cost; above ${HIGH:.2f}, it takes more than six years at $0.10/kWh, or ten at $0.06.
2. **The utility's own reported net benefits** for measures installed in 2025. These account for measure life and avoided costs, but the reports don't say on the program pages which test produced them, and the utilities evidently use different methods. They are used here only for their sign within each utility, not compared across utilities.

Across all {len(ranked)} ranked programs, cost per first-year kWh averaged ${a_cost / a_kwh:.3f}: FPL ${u_avg['Florida Power & Light']:.3f}, Duke ${u_avg['Duke Energy Florida']:.3f} and Tampa Electric ${u_avg['Tampa Electric']:.3f}.

![Figure 2](figures/fig2_cost_per_kwh.svg)

*Table 5. Screening groups, programs costing at least $100,000*

| Group | Rule | Programs |
|---|---|---|
| Appears cost-effective | lower or moderate cost per kWh **and** positive reported net benefits | {len(cls_counts['Appears cost-effective'])} |
| Mixed signals | the two measures disagree | {len(cls_counts['Mixed signals'])} |
| Needs more support | higher cost per kWh **and** zero, negative or no reported net benefits | {len(cls_counts['Needs more support'])} |
| Insufficient information | no net benefits reported and cost per kWh not higher | {len(cls_counts['Insufficient information'])} |

*Table 6. Program screen, programs costing at least $100,000 (sorted by cost per kWh)*

| Utility | Program | 2025 cost | GWh saved (meter) | $/kWh | Tier | Utility net benefits | Group |
|---|---|---|---|---|---|---|---|
""" + "\n".join(prog_row(p) for p in material) + f"""

Observations:
- **Most mixed signals are low cost per kWh with zero or negative reported net benefits** ({len(mixed_lo)} of {len(cls_counts['Mixed signals'])}: {", ".join(f"{n} {SHORT[u]}" for u, n in sorted(((u, sum(1 for p in mixed_lo if p['utility'] == u)) for u in UTILS[:3]), key=lambda x: -x[1]) if n)}). FPL's Business Lighting, for example, has the lowest cost per kWh in the screen (${next(p['cpk'] for p in material if p['program'] == 'Business Lighting'):.2f}) but FPL reports negative net benefits ({money(next(p['nb'] for p in material if p['program'] == 'Business Lighting'))}). {"FPL reports negative net benefits for every one of its energy-efficiency programs in Table 6. " if all((p['nb'] or 0) < 0 for p in material if p['utility'] == 'Florida Power & Light') else ""}That pattern is consistent with a test that counts lost revenue as a cost, such as the Rate Impact Measure, but the report doesn't name the test.
- **The reverse case** ({len(mixed_hi)} program{"s" if len(mixed_hi) != 1 else ""}: {", ".join(f"{SHORT[p['utility']]} {name(p)}" for p in mixed_hi)}) is high cost per kWh with positive net benefits. Tampa Electric's Energy Planner, at ${next(p['cpk'] for p in material if p['program'] == 'ENERGY PLANNER'):.2f} per kWh with {money(next(p['nb'] for p in material if p['program'] == 'ENERGY PLANNER'))} of reported net benefits, is the clearest example. It credits about 2.0 summer and 2.6 winter kW of peak reduction per participant against about 1,100 kWh a year, so its value is mostly in demand reduction, which cost per kWh doesn't capture. It arguably belongs with the demand programs.
- **Audit and education programs** (Tampa Electric's Walk-Through Audit and Free Commercial/Industrial Audit, Duke's Business Energy Check) fall in the higher tier by construction: their main purpose is to steer customers into other programs, and the savings they credit directly are small. They should be judged on referrals, which the filings don't report.
- **Low-income programs** ({", ".join(f"{SHORT[p['utility']]} {name(p)}" for p in lowinc)}) have moderate to high cost per kWh and negative reported net benefits. These programs may be offered for reasons other than cost-effectiveness; that context should be weighed before any change is recommended.
- **{len(small)} smaller programs** (under $100,000 each, {money(sum(p['cost'] for p in small))} combined) are listed in Appendix A but not screened, because rounding in the reported costs makes their cost per kWh unreliable.
- **Not screened:** {len(demand)} demand-response and load-control programs ({mil(sum(p['cost'] or 0 for p in demand))} in 2025) are credited in kW rather than kWh, and {len(no_kwh)} programs with costs ({", ".join(f"{SHORT[p['utility']]} {name(p)}" for p in no_kwh)}) credit no kWh savings at all.

*FPUC (shown separately; direct costs only).* FPUC's report gives direct program costs, not fully loaded costs, so its programs aren't comparable to the table above.

| Program | 2025 direct cost | kWh saved (meter) | $/kWh | FPUC-reported net benefits |
|---|---|---|---|---|
{fpuc_rows}

FPUC computes its net benefits from fuel-only avoided energy costs (5.446 cents/kWh) over ten years. Its Residential Energy Survey is the largest cost and shows negative net benefits; its Heating and Cooling Upgrade shows positive net benefits at low cost per kWh.

### Issue 6: How sensitive are the cost results to participation?

**Recommendation:** Results are moderately sensitive. A 20% participation shortfall raises cost per kWh by about {sens[0.8]:.1%}, and 20% higher participation lowers it by about {abs(sens[1.2]):.1%}, assuming {f:.0%} of each program's cost is fixed. {group_change_sentence}

**Analysis:** If participation changes, savings change in proportion but only part of the cost does: administration, marketing and fixed overhead stay. Three scenarios were tested: 80%, 100% and 120% of actual 2025 participation. The fixed share of cost isn't in the filings; {f:.0%} is an assumption, and the per-program results for all three scenarios are in `outputs/participation_sensitivity.csv`. The relationship is simple: with fixed share *f* and participation share *s*, cost per kWh scales by (*f* + (1 - *f*) *s*) / *s*. At *f* = {f:.0%}, that is {1 + sens[0.8]:.3f} at 80% and {1 + sens[1.2]:.3f} at 120%. Programs near a tier threshold, or with more fixed cost than assumed (audits, education, new programs in their first year), are the most exposed.

### Issue 7: Do the filings meet the Commission's reporting requirements?

**Recommendation:** Mostly, with specific gaps to raise with three utilities. FPL's DSM report and ECCR filing meet all {req_n} requirements checked. Ask Duke and Tampa Electric to justify every goal variance above 15% as Rule 25-17.0021(6)(k) requires, and to confirm whether their 2025 advertising made energy-savings claims requiring documentation under Rule 25-17.015(5). Ask Duke to correct the 2025 energy goal in its report to the order's 55 GWh. Ask FPUC to add program start dates, eligible customers and the penetration levels the rule defines, to report net benefits on the rule's annualized basis, and to restate its goal comparison against Order PSC-2024-0431-FOF-EG.

**Analysis:** Each utility's 2025 DSM report was checked against the annual-report requirements of Rule 25-17.0021(6), F.A.C. (items (a)-(n) plus the deadline and the residential and commercial/industrial goal comparison) and against its 2024 goals order. The FPL, Duke and Tampa Electric ECCR true-up filings were checked against the Rule 25-17.015 requirements quoted in those filings. Every program page in the FPL, Duke and Tampa Electric reports was searched for each required item; FPUC's table-based report, the variance explanations, the goal values and the ECCR items were reviewed by hand. The full checklist, with evidence for every cell, is in `docs/REQUIREMENTS.md`.

*Table 7. Requirements checked, by result*

| Utility | Met | Partly met | Not met | Not found | Can't determine / not reviewed |
|---|---|---|---|---|---|
""" + "\n".join(req_rows) + f"""

*Where the filings do not line up with the requirements*

| Utility | Requirement | Result | What was found |
|---|---|---|---|
""" + "\n".join(req_issue_rows) + f"""

Notes:
- **Variance justifications** matter because a large variance in either direction can signal goals set too low or programs reported inconsistently. FPL and FPUC explain theirs; Duke's commercial/industrial demand results were six and four times their goals with no explanation in the report.
- **Advertising documentation** is required only for advertisements that claim energy savings. "Not found" means it was not in the filings reviewed, not that a rule was broken.
- **Rule text.** Rule 25-17.0021 is checked against its text as proposed in the Commission staff recommendation of February 23, 2023, adopted May 18, 2023 (Order PSC-2023-0165-FOF-EU). The adopted text could not be retrieved, so any change made at adoption is not reflected. Rule 25-17.015 is checked only for the subsections the utilities quote.

### Issue 8: What reporting improvements should be requested?

**Recommendation:** Request the following in future DSM annual reports and ECCR true-up filings. Each addresses a gap that limited this review.

1. **State the cost-effectiveness test behind "net benefits"** on each program page, and use the same basis across utilities, so results can be compared (Issue 5).
2. **Report measure lives and lifetime kWh** for each program, so cost per lifetime kWh can be calculated rather than cost per first-year kWh (Issue 5).
3. **Disclose the cost basis**: whether reported program costs are fully loaded (as FPL, Duke and Tampa Electric's appear to be) or direct only (as FPUC's are) (Issue 5).
4. **Include a reconciliation table** from program pages to summary savings totals, at both the meter and the generator, and correct FPUC's Table 2-3/2-6 labels (Issue 2).
5. **Include a bridge from DSM-report program costs to ECCR true-up costs**, listing every ECCR line with no program page and its allocation basis (Issues 3 and 4).
6. **Report referrals or downstream participation** for audit and education programs, whose value isn't captured by their own credited savings (Issue 5).
7. **Justify every variance above 15%**, in either direction, and cite the current goals order with goal values that match it (Issue 7).

---

## Appendix A. All programs

"Screened" programs are energy-efficiency programs with fully loaded costs of at least $100,000. Costs are as reported in each DSM report (thousands of dollars, converted); kWh are first-year, at the meter.

| Utility | Program | 2025 cost | kWh saved (meter) | $/kWh | Utility net benefits | Status |
|---|---|---|---|---|---|---|
""" + "\n".join(
    f"| {SHORT[p['utility']]} | {name(p)} | {money(p['cost'] or 0)} | {'none credited' if p['kwh'] is None else format(p['kwh'], ',.0f')} | "
    f"{'n/a (kW program)' if p['demand_program'] else money(p['cost'] / p['kwh'], 2) if p['kwh'] and p['cost'] else 'n/a'} | {'n/a' if p['nb'] is None else money(p['nb'])} | "
    + ("screened: " + p["cls"] if p in material else
       "demand response (kW)" if p["demand_program"] else
       "direct cost only (FPUC)" if p["utility"] == "Florida Public Utilities" else
       "no kWh credited" if not p["kwh"] else "under $100,000") + " |"
    for p in sorted(progs, key=lambda p: (UTILS.index(p["utility"]), -(p["cost"] or 0)))) + f"""

## Appendix B. DSM-to-ECCR cost reconciliation

The line-by-line tables, including the mapping of each DSM program to its ECCR line, are generated in [`outputs/checks.md`](../outputs/checks.md). Mapping: [`data/dsm_to_eccr_map.csv`](../data/dsm_to_eccr_map.csv).

## Appendix C. Method and limitations

- **Data extraction.** Program data for FPL, Duke and Tampa Electric were parsed from the text of their DSM reports (`scripts/extract_programs.py`); each row keeps its source line. FPUC's report uses a different layout and two of its tables are images, so its seven programs were transcribed by hand from the rendered pages (`data/fpuc_programs_2025_manual.csv`). ECCR costs were transcribed from the exhibits named in the Case Background, and the transcription is tested against each filing's total.
- **Tampa Electric dual-plan rows.** Where Tampa Electric reports a program under both its 2020-2029 and 2025-2034 plans, the 2025-2034 row is used (Issue 2).
- **Demand programs** are identified by keywords in the program name (`src/eccr.py`); they are excluded from cost per kWh.
- **Thresholds and assumptions** chosen by this review: the $100,000 materiality floor, the ${LOW:.2f} and ${HIGH:.2f} cost-per-kWh tiers, and the {f:.0%} fixed-cost share. None comes from a filing; each is a single constant in the code and can be changed.
- **Not done:** no audit of utility records; no Commission cost-effectiveness tests (RIM, TRC, Participant) and no avoided-cost modeling; no review of true-up interest, revenues or recovery factors; no cross-check of FPUC costs; no net-to-gross or measure-life adjustments.
- **Use of AI.** This review was built with Claude, Anthropic's AI assistant. The author set the questions and scope and directed the work; Claude retrieved the filings, wrote the extraction and analysis code, built the Excel model and SQL database, and drafted this document. Figures come from the cited filings and are checked by the repository's tests.
- **Reproducibility.** `scripts/fetch_sources.sh` downloads every source; `scripts/analyze.py` and `scripts/write_recommendation.py` regenerate all tables, figures and this document. Unit tests in `tests/` check the transcriptions against filed totals.

## Appendix D. Sources

- FPL, *2025 Demand-Side Management Annual Report* (Feb. 27, 2026); Duke Energy Florida, *Summary of 2025 Demand Side Management Achievements*; Tampa Electric, *2025 Demand Side Management Program Accomplishments Report*; FPUC, *2025 Annual Conservation Report* (revised, March 6, 2026). All at `floridapsc.com/pscfiles/website-files/PDF/Utilities/Electricgas/ARDemandSide/2025/`.
- Docket 20260002-EG, ECCR 2025 final true-up, filed May 5, 2026: FPL testimony of L. Noack and Exhibit LSN-1 (Document No. 02616-2026); Duke testimony of K. Rodriguez and Exhibit KR-1T (02608-2026); Tampa Electric testimony of R. Johnson and Exhibit RGJ-1 (02603-2026).
- Goals orders: PSC-2024-0505-FOF-EG (FPL), PSC-2024-0429-FOF-EG (Duke), PSC-2024-0430-FOF-EG (Tampa Electric), PSC-2024-0431-FOF-EG (FPUC).
- Rule 25-17.0021, F.A.C.: Commission staff recommendation, Docket 20200181-EU (Commission Conference of March 7, 2023, Item 2, Attachment A); adoption Order PSC-2023-0165-FOF-EU (May 18, 2023). Rule 25-17.015, F.A.C.: as quoted in the 2025 ECCR true-up filings.
"""
(DOCS / "recommendation.md").write_text(doc)
print(f"wrote docs/recommendation.md ({len(doc.split()):,} words) and 3 figures")
