"""Check each utility's 2025 filings against the Commission's reporting requirements.

Two kinds of evidence:
- automated: every program page in the FPL, Duke and Tampa Electric DSM reports is searched for the items
  Rule 25-17.0021(6)(a)-(n) requires (run with --sources DIR to refresh data/requirements_auto_review.csv);
- reviewed: items that need reading or cross-referencing (deadlines, variance justifications, goals vs.
  the 2024 orders, FPUC's table-based report, ECCR true-up items) are recorded with evidence in
  data/requirements_manual_review.csv.
Writes outputs/requirements_checklist.csv and docs/REQUIREMENTS.md.
"""
import argparse
import csv
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AUTO = ROOT / "data" / "requirements_auto_review.csv"
UTILS = ["Florida Power & Light", "Duke Energy Florida", "Tampa Electric", "Florida Public Utilities"]
SHORT = {"Florida Power & Light": "FPL", "Duke Energy Florida": "Duke", "Tampa Electric": "Tampa Electric",
         "Florida Public Utilities": "FPUC"}
REPORTS = {"Florida Power & Light": "dsm_2025_FloridaPowerandLightCompany.txt",
           "Duke Energy Florida": "dsm_2025_DukeEnergyFlorida.txt",
           "Tampa Electric": "dsm_2025_TampaElectricCompany.txt"}
# Item -> regex patterns that must all appear on a program page (the Program Name block plus the 4 lines above it).
PAGE_CHECKS = {
    "R6-a": [r"Utility:"],
    "R6-b": [r"Program Name:", r"Program Start Date"],
    "R6-c": [r"Reporting Period"],
    "R6-d": [r"Customers"],
    "R6-e": [r"Eligible"],
    "R6-f": [r"Projected"],
    "R6-g": [r"Penetration"],
    "R6-h": [r"Actual"],
    "R6-i": [r"Penetration", r"Actual"],
    "R6-j": [r"Over \(Under\)|\(h-e\)|\(g-d\)|Participation Over"],
    "R6-l": [r"kWh (Savings|Reduction)", r"Winter kW", r"Summer kW", r"@ ?Meter", r"@ ?Generator", r"Per Installation", r"Program Total"],
    "R6-m": [r"Cost per Installation", r"Total (Utility )?Program Cost"],
    "R6-n": [r"Net Benefits"],
}
NO_SAVINGS = re.compile(r"No kW or kWh savings attributed", re.I)


def auto_review(sources):
    rows = []
    for u, fname in REPORTS.items():
        lines = (Path(sources) / fname).read_text().splitlines()
        starts = [i for i, l in enumerate(lines) if re.match(r"\s*Program Name:", l)]
        blocks = []
        for n, s in enumerate(starts):
            e = starts[n + 1] if n + 1 < len(starts) else len(lines)
            blocks.append((lines[s].split(":", 1)[1].strip(), "\n".join(lines[max(0, s - 4):e])))
        for item, pats in PAGE_CHECKS.items():
            missing = [name for name, b in blocks if not all(re.search(p, b, re.I) for p in pats)]
            exempt = [name for name, b in blocks if name in missing and NO_SAVINGS.search(b)]
            if not missing:
                status, ev = "Met", f"All {len(blocks)} program pages include it."
            elif set(missing) == set(exempt):
                status = "Met"
                ev = (f"{len(blocks) - len(missing)} of {len(blocks)} program pages include it; the other "
                      f"{len(missing)} ({'; '.join(missing)}) state that no kW or kWh savings are attributed to the program.")
            else:
                status, ev = "Partly met", f"Missing on {len(missing)} of {len(blocks)} program pages: {'; '.join(missing)}."
            if item == "R6-n" and status == "Met":
                ev += " The report does not show whether the figure is annualized as the rule's formula requires."
            rows.append({"id": item, "utility": u, "status": status, "evidence": ev})
    with open(AUTO, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["id", "utility", "status", "evidence"])
        w.writeheader()
        w.writerows(rows)
    return rows


def main(sources=None):
    if sources:
        auto_review(sources)
    reqs = list(csv.DictReader(open(ROOT / "data" / "requirements.csv")))
    review = {}
    for path, kind in ((AUTO, "automated"), (ROOT / "data" / "requirements_manual_review.csv", "reviewed")):
        for r in csv.DictReader(open(path)):
            review[(r["id"], r["utility"])] = {**r, "method": kind}
    out = []
    for q in reqs:
        for u in UTILS:
            r = review.get((q["id"], u))
            if r is None:
                if q["id"].startswith("E-") and u == "Florida Public Utilities":
                    r = {"status": "Not reviewed", "evidence": "FPUC's ECCR true-up filing was not located.", "method": "-"}
                else:
                    raise SystemExit(f"no review for {q['id']} / {u}")
            out.append({"id": q["id"], "rule": q["rule"], "requirement": q["requirement"], "utility": u,
                        "status": r["status"], "method": r["method"], "evidence": r["evidence"]})
    (ROOT / "outputs").mkdir(exist_ok=True)
    with open(ROOT / "outputs" / "requirements_checklist.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(out[0]))
        w.writeheader()
        w.writerows(out)
    write_doc(reqs, out)
    return out


ICON = {"Met": "Met", "Partly met": "**Partly met**", "Not met": "**Not met**", "Not found": "**Not found**",
        "Can't determine": "Can't determine", "Not reviewed": "Not reviewed"}


def write_doc(reqs, out):
    by = {(r["id"], r["utility"]): r for r in out}
    issues = [r for r in out if r["status"] in ("Partly met", "Not met", "Not found")]
    counts = {u: {} for u in UTILS}
    for r in out:
        counts[r["utility"]][r["status"]] = counts[r["utility"]].get(r["status"], 0) + 1
    lines = [
        "# Reporting requirements check",
        "",
        "Generated by `scripts/check_requirements.py`. Each utility's 2025 DSM annual report and (for FPL, Duke and Tampa Electric) "
        "its 2025 ECCR final true-up filing, checked against what the Commission's rules and the 2024 goals orders require.",
        "",
        "**Status meanings.** *Met*: found. *Partly met*: some of what the requirement asks for is missing. *Not met*: the filing "
        "contradicts the requirement or the order. *Not found*: searched for and not found in the filing reviewed (it may exist "
        "elsewhere). *Can't determine*: the posted documents don't show it. Evidence for every cell is in "
        "`outputs/requirements_checklist.csv`.",
        "",
        "## Summary",
        "",
        "| Utility | Met | Partly met | Not met | Not found | Can't determine / not reviewed |",
        "|---|---|---|---|---|---|",
    ]
    for u in UTILS:
        c = counts[u]
        lines.append(f"| {u} | {c.get('Met', 0)} | {c.get('Partly met', 0)} | {c.get('Not met', 0)} | {c.get('Not found', 0)} | "
                     f"{c.get(chr(67) + 'an' + chr(39) + 't determine', 0) + c.get('Not reviewed', 0)} |")
    lines += ["", "## Where the filings do not line up with the requirements", ""]
    for r in issues:
        lines.append(f"- **{SHORT[r['utility']]}, {r['rule']}** ({r['status'].lower()}): {r['evidence']}")
    lines += ["", "## Full checklist", "", "| Requirement | Rule | " + " | ".join(SHORT[u] for u in UTILS) + " |",
              "|---|---|" + "---|" * len(UTILS)]
    for q in reqs:
        lines.append(f"| {q['requirement']} | {q['rule']} | " + " | ".join(ICON[by[(q['id'], u)]['status']] for u in UTILS) + " |")
    lines += [
        "",
        "## Sources and limits",
        "",
        "- **Rule 25-17.0021, F.A.C.** (goals and annual reports): text as proposed in the Commission staff recommendation of "
        "February 23, 2023 (Docket 20200181-EU, Commission Conference of March 7, 2023, Attachment A), adopted May 18, 2023 "
        "(Order PSC-2023-0165-FOF-EU). The adopted text could not be retrieved here (flrules.org is outside this environment's "
        "network access), so any change made between proposal and adoption is not reflected.",
        "- **Rule 25-17.015, F.A.C.** (ECCR): requirements as quoted in the utilities' 2025 true-up filings (FPL petition, "
        "Doc. 02614-2026; FPL testimony, Doc. 02616-2026; Duke testimony, Doc. 02608-2026). Only the subsections quoted there "
        "are checked.",
        "- **Goals orders:** PSC-2024-0505-FOF-EG (FPL, Attachment A Issue 12), PSC-2024-0429-FOF-EG (Duke, Exhibit A table of "
        "2025-2034 annual goals), PSC-2024-0430-FOF-EG (Tampa Electric, residential and C/I tables), PSC-2024-0431-FOF-EG "
        "(FPUC, Attachment B). The goal tables are scanned images and were read from the rendered pages.",
        "- **Automated checks** confirm that each required item appears on every program page; they do not verify the values. "
        "FPUC's report uses tables rather than program pages, so it was reviewed by hand.",
        "- This is an independent review of public filings, not a Commission compliance determination.",
    ]
    (ROOT / "docs" / "REQUIREMENTS.md").write_text("\n".join(lines) + "\n")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--sources", help="folder with the DSM report text files (scripts/fetch_sources.sh output)")
    a = ap.parse_args()
    rows = main(a.sources)
    print(f"wrote outputs/requirements_checklist.csv ({len(rows)} checks) and docs/REQUIREMENTS.md")
