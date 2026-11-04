# Florida Conservation Program Cost Review (2025 reporting year)

A reviewer-style screen of the energy-conservation programs reported by Florida's four investor-owned electric utilities. It reads the utilities' public filings with the Florida Public Service Commission, reconciles program costs in their annual DSM reports against their Energy Conservation Cost Recovery (ECCR) true-up filings, checks savings totals, computes cost per kWh saved and a simple payback measure, tests sensitivity to participation, and writes a short staff-style memo.

**Read first:** [docs/memo.md](docs/memo.md) (findings) and [docs/METHODOLOGY.md](docs/METHODOLOGY.md) (assumptions and limits). Reconciliation results: [outputs/checks.md](outputs/checks.md).

## Scope
- **All 4 investor-owned utilities**: 67 programs parsed from the 2025 DSM annual reports of Florida Power & Light, Duke Energy Florida, Tampa Electric and Florida Public Utilities.
- **Cost cross-check** for FPL, Duke and Tampa Electric: every DSM-report program cost is matched to its line in the utility's 2025 ECCR final true-up exhibit (Docket 20260002-EG). 55 of 57 comparisons agree within the report's rounding; the two exceptions are $130 and $62. ECCR lines with no DSM program page are listed with their share of the filed total.
- **Savings check** for all four: program pages vs. each utility's reported total. FPL reconciles exactly and Duke within rounding; Tampa Electric is 2.2 GWh short of its summary; FPUC's summary appears to swap its meter and generator energy totals.
- 35 FPL, Duke and Tampa Electric efficiency programs are ranked on $/kWh. FPUC reports direct costs only, so its programs are shown separately.
- FPUC's ECCR true-up was not located, so its costs are not cross-checked.
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
- `data/fpuc_programs_2025_manual.csv` - FPUC programs (different report layout; two tables are images), transcribed by hand
- `data/eccr_2025_costs.csv` - ECCR true-up costs by line for FPL, Duke and Tampa Electric; `data/ct2_totals_2025.csv` - filed totals
- `data/dsm_to_eccr_map.csv` - which DSM program page corresponds to which ECCR line
- `data/goals_vs_achieved_2025.csv` - utility-reported achieved vs. goal GWh
- `src/eccr.py` - metrics; `scripts/` - fetch, extract, analyze; `tests/`; `outputs/`; `docs/`

## Sources
Utility annual DSM reports: `floridapsc.com/pscfiles/website-files/PDF/Utilities/Electricgas/ARDemandSide/2025/` (one PDF per utility). ECCR true-up exhibits (Docket 20260002-EG): FPL `floridapsc.com/library/filings/2026/02616-2026/02616-2026.pdf`, Duke `.../02608-2026/02608-2026.pdf`, Tampa Electric `.../02603-2026/02603-2026.pdf`. Goals: Orders PSC-2024-0505-FOF-EG (FPL), PSC-2024-0429-FOF-EG (Duke), PSC-2024-0430-FOF-EG (Tampa Electric), PSC-2024-0431-FOF-EG (FPUC).
