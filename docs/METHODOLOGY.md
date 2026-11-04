# Methodology and limits

## Data
- **Cost**: "Total Program Cost of the Utility ($000)" from each program page of the utility's 2025 DSM annual report. Reported in thousands (TECO to $0.1k), so small programs carry rounding error. For FPL, all 14 program costs agree with Exhibit LSN-1 p.27 within $500 (see outputs/checks.md).
- **Savings**: "Annual kWh Reduction" / "kWh Savings", program total **at the meter**, first year. These are the savings credited for 2025 installations/participants.
- **TECO**: some programs show two DSM plans (2020-2029 and 2025-2034) plus a combined row flagged "not included in achievements". The 2025-2034 plan row is used where present because 2025 goals come from that plan. This is a judgment; with it, TECO's program pages sum to 63.6 GWh vs. 65.8 reported.
- **FPUC**: its report has a different layout and Tables 3-1/3-2 are images, so its seven programs are transcribed by hand (`data/fpuc_programs_2025_manual.csv`) from the rendered pages. Its Table 4-1 costs are direct sub-ledger costs only, so FPUC is excluded from the cross-utility ranking.
- **ECCR cross-check**: program cost lines from each utility's 2025 final true-up (FPL Exhibit LSN-1 p.27; Duke Exhibit KR-1T Schedule CT-2 p.2; Tampa Electric Exhibit RGJ-1 Schedule CT-2 p.2) are mapped to DSM program pages in `data/dsm_to_eccr_map.csv`. Where one ECCR line covers several DSM pages (Duke Load Management; Tampa Electric Heating and Cooling Tiers 1 and 2), the DSM costs are summed. Tolerance is the DSM report's rounding: $500 per program for FPL and Duke ($000 reported), $50 for Tampa Electric ($0.1k reported).
- **Excluded from $/kWh**: programs whose names indicate demand response/load control (credited in kW) and programs with no kWh credited. The name filter is a keyword list in `src/eccr.py`; check it if adding programs.

## Metrics
- **Cost per kWh saved** = program cost / first-year kWh at meter. It ignores measure life (a 15-year insulation measure and a 1-year behavioral program are treated alike) and includes program overhead (audits, education, administration), so it overstates cost for programs whose benefits show up in other programs.
- **Payback (years)** = program cost / (first-year kWh x value per kWh). This is "years of first-year savings needed to equal cost" and is a ranking aid, not a customer payback. Value per kWh is an **assumption**, shown at $0.03, $0.06 and $0.10; none is taken from a filing. (For reference, fuel clauses on current residential tariffs are around $0.03-0.04/kWh.)
- **Participation sensitivity**: participation at 80%, 100%, 120% of actual. kWh scales fully; cost scales only on its variable part, with **30% assumed fixed**. The fixed share is not in the filings; change `FIXED_COST_SHARE` to test it.

## What was not done
- No Commission cost-effectiveness tests, no avoided-cost modeling, no measure-life or net-to-gross adjustments.
- FPUC costs were not cross-checked to an ECCR filing (not located).
- Savings and costs come straight from utility reports; they were checked for internal consistency, not audited.
