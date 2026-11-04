# Memo: Screening of 2025 Conservation Program Cost-Effectiveness (FPL, Duke Energy Florida, Tampa Electric)

*Independent portfolio analysis built from public filings; not an official Commission staff product. Method and limits: docs/METHODOLOGY.md.*

## Purpose
Screen the energy-saving programs three of Florida's four investor-owned electric utilities reported for 2025, using their filed annual DSM reports and FPL's ECCR final true-up exhibit, and identify which programs warrant a closer look.

## Scope of what was analyzed
- 60 programs reported by three utilities; 35 are energy-efficiency programs with both cost and credited kWh and are screened below. The rest are demand-response/load-control programs (credited in kW, not kWh) or programs with no savings credited (e.g., FPL Home Energy Survey), which cannot be ranked on cost per kWh.
- The 35 screened programs cost $58.1 million and credit 193.1 GWh of first-year savings at the meter, an average of $0.301 per kWh.
- Florida Public Utilities is excluded from the program screen (its report is formatted differently); it appears only in the goals comparison.

## Lowest cost per kWh saved (programs costing at least $100,000)
| Utility | Program | 2025 cost | GWh saved (meter, first-year) | $ per kWh | Years at $0.10/kWh |
|---|---|---|---|---|---|
| Florida Power & Light | Business Lighting | $570,000 | 17.85 | $0.03 | 0.3 |
| Tampa Electric | Residential Customer Assisted Audits | $420,500 | 9.58 | $0.04 | 0.4 |
| Tampa Electric | Residential Heating And Cooling Tier1 | $151,200 | 3.07 | $0.05 | 0.5 |
| Florida Power & Light | Residential New Construction (BuildSmart®) | $724,000 | 7.72 | $0.09 | 0.9 |
| Tampa Electric | Residential Heating And Cooling Tier 2 | $297,200 | 3.03 | $0.10 | 1.0 |
| Florida Power & Light | Residential Ceiling Insulation | $1,709,000 | 16.42 | $0.10 | 1.0 |

## Highest cost per kWh saved (programs costing at least $100,000)
| Utility | Program | 2025 cost | GWh saved (meter, first-year) | $ per kWh | Years at $0.10/kWh |
|---|---|---|---|---|---|
| Tampa Electric | Energy Planner | $2,132,700 | 0.21 | $10.18 | 101.8 |
| Duke Energy Florida | Business Energy Check | $344,000 | 0.09 | $3.75 | 37.5 |
| Tampa Electric | RESIDENTIAL ALTERNATE AUDIT (aka Walk-Thru Audit or EA Free) | $2,216,300 | 1.02 | $2.16 | 21.6 |
| Tampa Electric | Residential Ceiling Insulation | $414,100 | 0.29 | $1.41 | 14.1 |
| Tampa Electric | Free Commercial/Industrial Audit | $587,500 | 0.45 | $1.31 | 13.1 |
| Duke Energy Florida | Multi-Family New Builder Construction | $114,000 | 0.10 | $1.15 | 11.5 |

## Goals comparison (2025, as reported by each utility)
- Florida Power & Light: 102.57 GWh achieved vs. 100.08 GWh goal (at generator).
- Duke Energy Florida: 65 GWh achieved vs. 56 GWh goal (at generator (rounded to whole GWh in report)).
- Tampa Electric: 65.8 GWh achieved vs. 47.0 GWh goal (at generator (combined residential + C/I)).
- Florida Public Utilities: 0.131 GWh achieved vs. 0.465 GWh goal (at meter).

## Observations for follow-up
1. **Ranking is sensitive to what a program's cost includes.** Audit and education programs carry cost but credit little direct savings, so their $/kWh looks poor by construction. They should be judged on what they feed into other programs, which these filings do not show.
2. **Data that does not line up.** Tampa Electric's program pages sum to 63.6 GWh at the generator against 65.8 GWh in its summary (a gap of 2.2 GWh); the report prints combined and per-plan rows, and the summary basis is not stated. Duke's program pages sum to 65.44 GWh vs. 65 reported (rounding). FPL's reconcile exactly. See outputs/checks.md.
3. **FPL costs recovered beyond the listed programs.** About $49.2 million (29% of FPL's 2025 ECCR program costs) sits in lines such as C/I Load Control, Common Expenses and Energy Select that have no matching program page in the DSM report. The DSM report still reconciles to the ECCR exhibit program by program for the 14 programs it covers.
4. **Participation sensitivity.** Under the stated assumption that 30% of each program's cost is fixed, 80% participation raises $/kWh by 7.5% and 120% changes it by -5.0% (outputs/participation_sensitivity.csv). Fixed-cost shares were not available in the filings, so this is illustrative.

## Recommendation
Treat this as a screening list, not a finding: request program-level cost detail and measure lives for the highest-$/kWh programs above, and ask Tampa Electric to reconcile its summary to its program pages before relying on either number.
