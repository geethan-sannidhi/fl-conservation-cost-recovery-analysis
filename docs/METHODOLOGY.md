# Methodology and limits

## Data
- **Cost**: "Total Program Cost of the Utility ($000)" from each program page of the utility's 2025 DSM annual report. Reported in thousands (TECO to $0.1k), so small programs carry rounding error. For FPL, all 14 program costs agree with Exhibit LSN-1 p.27 within $500 (see outputs/checks.md).
- **Savings**: "Annual kWh Reduction" / "kWh Savings", program total **at the meter**, first year. These are the savings credited for 2025 installations/participants.
- **TECO**: some programs show two DSM plans (2020-2029 and 2025-2034) plus a combined row flagged "not included in achievements". The 2025-2034 plan row is used where present because 2025 goals come from that plan. This is a judgment; with it, TECO's program pages sum to 63.6 GWh vs. 65.8 reported.
- **Excluded from $/kWh**: programs whose names indicate demand response/load control (credited in kW) and programs with no kWh credited. The name filter is a keyword list in `src/eccr.py`; check it if adding programs.

## Metrics
- **Cost per kWh saved** = program cost / first-year kWh at meter. It ignores measure life (a 15-year insulation measure and a 1-year behavioral program are treated alike) and includes program overhead (audits, education, administration), so it overstates cost for programs whose benefits show up in other programs.
- **Payback (years)** = program cost / (first-year kWh x value per kWh). This is "years of first-year savings needed to equal cost" and is a ranking aid, not a customer payback. Value per kWh is an **assumption**, shown at $0.03, $0.06 and $0.10; none is taken from a filing. (For reference, fuel clauses on current residential tariffs are around $0.03-0.04/kWh.)
- **Participation sensitivity**: participation at 80%, 100%, 120% of actual. kWh scales fully; cost scales only on its variable part, with **30% assumed fixed**. The fixed share is not in the filings; change `FIXED_COST_SHARE` to test it.

## What was not done
- No Commission cost-effectiveness tests, no avoided-cost modeling, no measure-life or net-to-gross adjustments.
- Duke and TECO costs were not cross-checked to their ECCR exhibits (only FPL's were retrieved).
- Florida Public Utilities programs were not parsed.
- Savings and costs come straight from utility reports; they were checked for internal consistency, not audited.
