# SQL

The review's analysis written as SQL against a SQLite database built from the repository's data files.

```bash
python3 scripts/run_queries.py      # builds data/conservation_2025.sqlite, runs every query, writes outputs/sql/*.csv
python3 -m unittest tests.test_sql  # checks every query against the Python analysis
```

To explore interactively, open `data/conservation_2025.sqlite` in any SQLite client (for example DB Browser for SQLite, or `sqlite3` in a terminal) and run the files below. Run `06_program_screen.sql` as a view named `program_screen` first if you want to run 07 or 08 by hand: `CREATE VIEW program_screen AS <contents of 06>`.

| File | Question | Recommendation issue |
|---|---|---|
| `schema.sql` | Tables, keys and the `programs_flagged` view (demand-program flag from a keyword table) | - |
| `queries/01_goal_achievement.sql` | Did each utility meet its 2025 energy, summer and winter goals? | 1 |
| `queries/02_savings_reconciliation.sql` | Do program pages add up to each reported total? | 2 |
| `queries/03_eccr_line_totals.sql` | Do the transcribed ECCR lines add up to each filed total? | 3 |
| `queries/04_cost_reconciliation.sql` | Does each DSM-report program cost match its ECCR line within rounding? | 3 |
| `queries/05_eccr_lines_without_program_page.sql` | Which ECCR costs have no DSM program page, and what share of the total are they? | 4 |
| `queries/06_program_screen.sql` | Cost per kWh, payback, tier and screening group for every program | 5 |
| `queries/07_screening_summary.sql` | Programs per screening group; portfolio and utility cost per kWh | 5 |
| `queries/08_participation_sensitivity.sql` | Cost per kWh at 80% / 100% / 120% participation; which programs change tier | 6 |

Thresholds and scenario values live in the `assumptions` table (same defaults as the Excel model's Assumptions sheet), so changing a row there changes every query that uses it.
