# Memo: Screening of 2025 Conservation Program Cost-Effectiveness (Florida investor-owned electric utilities)

*Independent portfolio analysis built from public filings; not an official Commission staff product. Method and limits: docs/METHODOLOGY.md.*

## Purpose
Screen the energy-saving programs Florida's four investor-owned electric utilities reported for 2025, check the reported costs against each utility's Energy Conservation Cost Recovery (ECCR) final true-up filing, and identify which programs warrant a closer look.

## Scope of what was analyzed
- 67 programs from 4 utilities' 2025 DSM annual reports. 35 energy-efficiency programs from FPL, Duke and Tampa Electric have both cost and credited kWh and are ranked below. Demand-response/load-control programs (credited in kW) and programs with no kWh credited can't be ranked on cost per kWh.
- FPL, Duke and Tampa Electric program costs were cross-checked line by line against their 2025 ECCR true-up exhibits (Docket 20260002-EG).
- The 35 ranked programs cost $58.1 million and credit 193.1 GWh of first-year savings at the meter, an average of $0.301 per kWh.
- Florida Public Utilities reports direct costs only, so its programs are shown separately rather than ranked with the others.

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

## Florida Public Utilities (direct costs only; not comparable to the tables above)
| Program | 2025 direct cost | kWh saved (meter) | $ per kWh |
|---|---|---|---|
| Residential Energy Survey | $60,002 | 16,716 | $3.59 |
| Residential Heating and Cooling Upgrade | $5,660 | 102,690 | $0.06 |
| Residential Low Income Program | $5,731 | 7,020 | $0.82 |
| Residential Small Appliance Program | $108 | 924 | $0.12 |

FPUC's three commercial programs had no participants in 2025.

## Goals comparison (2025, as reported by each utility)
- Florida Power & Light: 102.57 GWh achieved vs. 100.08 GWh goal (at generator).
- Duke Energy Florida: 65 GWh achieved vs. 56 GWh goal (at generator (report rounds to whole MW/GWh)).
- Tampa Electric: 65.8 GWh achieved vs. 47.0 GWh goal (at generator (combined residential + C/I)).
- Florida Public Utilities: 0.127 GWh achieved vs. 0.517 GWh goal (at generator (as printed in Table 2-3; program pages sum to 0.131 GWh - see checks)).

## Cost cross-check against ECCR filings
- **Florida Power & Light**: 14 of 14 DSM-to-ECCR cost comparisons agree within rounding; $49.2 million (29% of the filed total) is in ECCR lines with no DSM program page (largest: Commercial/Industrial Load Control, $36.5 million).
- **Duke Energy Florida**: 12 of 12 DSM-to-ECCR cost comparisons agree within rounding; $3.7 million (3% of the filed total) is in ECCR lines with no DSM program page (largest: Conservation Program Admin, $2.7 million).
- **Tampa Electric**: 29 of 31 DSM-to-ECCR cost comparisons agree within rounding; $2.4 million (5% of the filed total) is in ECCR lines with no DSM program page (largest: Common Expenses, $1.2 million).

## Observations for follow-up
1. **Ranking is sensitive to what a program's cost includes.** Audit and education programs carry cost but credit little direct savings, so their $/kWh looks poor by construction. They should be judged on what they feed into other programs, which these filings do not show.
2. **Program costs reconcile closely; savings totals do not always.** 55 of 57 DSM-report program costs match the ECCR exhibits within the report's rounding. The exceptions are small: Energy Planner (DSM report $130 below the ECCR exhibit); Residential Prime Time Plus (DSM report $62 below the ECCR exhibit), both Tampa Electric programs with large capital-investment (depreciation and return) amounts in the true-up. On savings, Tampa Electric's program pages sum to 63.6 GWh at the generator against 65.8 GWh in its summary (a gap of 2.2 GWh), and FPUC's summary appears to swap its meter and generator energy totals (0.127 vs. 0.131 GWh). FPL's reconcile exactly and Duke's within rounding. See outputs/checks.md.
3. **Costs recovered outside the reported programs.** Each utility's ECCR true-up includes material costs in lines with no program page in its DSM report: a program closed to new participants (FPL's Commercial/Industrial Load Control, the largest single item), common and administrative expenses, research and development, cogeneration and qualifying-facility administration, pilots and a regulatory asset (amounts above). Because these costs don't appear in the program-level reporting, a reviewer should confirm each is supported and properly recoverable through the clause.
4. **Participation sensitivity.** Under the stated assumption that 30% of each program's cost is fixed, 80% participation raises $/kWh by 7.5% and 120% changes it by -5.0% (outputs/participation_sensitivity.csv). Fixed-cost shares were not available in the filings, so this is illustrative.

## Recommendation
Treat this as a screening list, not a finding. Request measure lives and cost detail for the highest-$/kWh programs above; ask Tampa Electric to reconcile its summary savings to its program pages and FPUC to correct its Table 2-3/2-6 labels; and request support for the ECCR lines that have no corresponding DSM program page.
