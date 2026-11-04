# Florida Conservation Program Cost Review (2025 reporting year)

A reviewer-style screen of the energy-conservation programs reported by Florida's investor-owned electric utilities. It reads the utilities' public filings with the Florida Public Service Commission, checks that the reported numbers reconcile, computes cost per kWh saved and a simple payback measure, tests sensitivity to participation, and writes a short staff-style memo.

**Read first:** [docs/memo.md](docs/memo.md) (findings) and [docs/METHODOLOGY.md](docs/METHODOLOGY.md) (assumptions and limits). Reconciliation results: [outputs/checks.md](outputs/checks.md).

## Scope
- Program-level screen for **3 utilities**: Florida Power & Light, Duke Energy Florida, Tampa Electric (60 programs parsed, 35 screened on $/kWh). Florida Public Utilities appears only in the goals comparison.
- Costs and savings are from each utility's 2025 DSM annual report (filed Feb-Mar 2026). FPL's costs are also cross-checked to its ECCR final true-up exhibit (Docket 20260002-EG).
- This is a screening exercise, not an official staff analysis and not a cost-effectiveness test under Commission rules (no RIM/TRC/Participant tests, no measure lives).

## Run
Requires Python 3 and `pdftotext` (poppler).
```bash
scripts/fetch_sources.sh /tmp/sources            # downloads PDFs from floridapsc.com, converts to text
python3 scripts/extract_programs.py /tmp/sources data/programs_2025.csv
python3 scripts/analyze.py                       # writes outputs/*.csv, outputs/checks.md, docs/memo.md
python3 -m unittest discover -s tests -v
```

## Layout
- `data/programs_2025.csv` - extracted program costs and kWh savings (with source file and line)
- `data/fpl_eccr_2025_ct3_costs.csv` - FPL program costs transcribed from Exhibit LSN-1 p.27
- `data/goals_vs_achieved_2025.csv` - utility-reported achieved vs. goal GWh
- `src/eccr.py` - metrics; `scripts/` - fetch, extract, analyze; `tests/`; `outputs/`; `docs/`

## Sources
Utility annual DSM reports: `floridapsc.com/pscfiles/website-files/PDF/Utilities/Electricgas/ARDemandSide/2025/` (one PDF per utility). FPL ECCR exhibit: `floridapsc.com/library/filings/2026/02616-2026/02616-2026.pdf`. Goals: Orders PSC-2024-0505-FOF-EG (FPL), PSC-2024-0429-FOF-EG (Duke), PSC-2024-0430-FOF-EG (Tampa Electric), PSC-2024-0431-FOF-EG (FPUC).
