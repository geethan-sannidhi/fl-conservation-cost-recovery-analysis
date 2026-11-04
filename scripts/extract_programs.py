"""Extract program-level cost and savings from utilities' 2025 DSM annual reports
(text produced by `pdftotext -layout`). Output: data/programs_2025.csv

Each report block starts with 'Program Name:' and contains
  - 'Annual kWh Reduction' / 'kWh Savings' rows (last two numbers = program total @meter, @generator)
  - 'Total [Utility] Program Cost ... ($000)'
The LAST kWh row in a block is the program total (TECO prints per-plan rows, then a combined row).
"""
import csv, re, sys
from pathlib import Path

TEXT_DIR = Path(sys.argv[1])
OUT = Path(sys.argv[2])

REPORTS = {
    "FPL":  ("dsm_2025_FloridaPowerandLightCompany.txt", "Florida Power & Light"),
    "DEF":  ("dsm_2025_DukeEnergyFlorida.txt", "Duke Energy Florida"),
    "TECO": ("dsm_2025_TampaElectricCompany.txt", "Tampa Electric"),
}
NUM = re.compile(r"\(?-?\$?[\d,]+(?:\.\d+)?\)?")

def nums(line):
    out = []
    for m in NUM.findall(line):
        s = m.strip("()$").replace(",", "").replace("$", "")
        if s in ("", "-"):
            continue
        try:
            v = float(s)
        except ValueError:
            continue
        out.append(-v if m.startswith("(") else v)
    return out

rows = []
for key, (fname, utility) in REPORTS.items():
    lines = (TEXT_DIR / fname).read_text().splitlines()
    starts = [i for i, l in enumerate(lines) if re.match(r"\s*Program Name:", l)]
    for n, s in enumerate(starts):
        e = starts[n + 1] if n + 1 < len(starts) else len(lines)
        block = lines[s:e]
        name = re.sub(r"\s+", " ", block[0].split("Program Name:")[1]).strip()
        kwh_rows = [l for l in block if re.search(r"(Annual kWh Reduction|^\s*kWh Savings)", l)]
        cost_rows = [l for l in block if re.search(r"Total (Utility )?Program Cost", l)]
        nb_rows = [l for l in block if "Net Benefits" in l]
        net_benefits = ""
        if nb_rows:
            tail = nb_rows[0].split(":")[-1] if ":" in nb_rows[0] else nb_rows[0].split("($000)")[-1]
            tail = tail.strip()
            if tail and not tail.upper().startswith("N/A"):
                m = re.match(r"^(-)?\(?-?\$?\s*([\d,]+(?:\.\d+)?)\)?", tail)
                if m:
                    v = float(m.group(2).replace(",", ""))
                    net_benefits = -v if (m.group(1) or tail.startswith("(") or tail.startswith("-")) else v
        kwh_meter = kwh_gen = cost = None
        kwh_note = ""
        # TECO reports some programs under two DSM plans (2020-2029 and 2025-2034) and prints a
        # combined row flagged "Note 1: ... not included in achievements". Goals for 2025 come from
        # the 2025-2034 plan, so where that plan row exists it is used instead of the combined row.
        if True:
            for i, l in enumerate(block):
                if "2025-2034 DSM Plan" in l:
                    kk = [x for x in block[i:i + 8] if "Annual kWh Reduction" in x]
                    if kk:
                        v = nums(kk[0].split("Reduction")[-1])
                        if len(v) >= 2:
                            kwh_meter, kwh_gen = v[-2], v[-1]
                            kwh_note = "2025-2034 plan row used (TECO reports two plans)"
        if kwh_rows and kwh_meter is None:
            v = nums(kwh_rows[-1].split("Reduction")[-1] if "Reduction" in kwh_rows[-1] else kwh_rows[-1].split("Savings")[-1])
            if len(v) >= 2:
                kwh_meter, kwh_gen = v[-2], v[-1]
        if cost_rows:
            v = nums(cost_rows[0].split(":")[-1] if ":" in cost_rows[0] else cost_rows[0].split(")")[-1])
            if v:
                cost = v[-1]
        rows.append(dict(utility=utility, program=name, annual_kwh_at_meter=kwh_meter,
                         annual_kwh_at_generator=kwh_gen, program_cost_thousands=cost, net_benefits_thousands=net_benefits, kwh_note=kwh_note,
                         source_file=fname, source_line=s + 1))

# FPUC's report uses a different layout (and two of its tables are images), so its programs are
# transcribed by hand in data/fpuc_programs_2025_manual.csv and appended here.
manual = Path(__file__).resolve().parents[1] / "data" / "fpuc_programs_2025_manual.csv"
for r in csv.DictReader(open(manual)):
    rows.append({k: r.get(k, "") for k in rows[0]})

OUT.parent.mkdir(parents=True, exist_ok=True)
with open(OUT, "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
print(len(rows), "programs written to", OUT)
