-- Schema for the 2025 Florida conservation program review (SQLite).
-- Loaded from the repository's CSVs by scripts/build_database.py.

CREATE TABLE utilities (
    utility       TEXT PRIMARY KEY,
    short_name    TEXT NOT NULL,
    cost_basis    TEXT NOT NULL CHECK (cost_basis IN ('total program cost', 'direct costs only'))
);

-- One row per program page in each utility's 2025 DSM annual report.
CREATE TABLE programs (
    program_id        INTEGER PRIMARY KEY,
    utility           TEXT NOT NULL REFERENCES utilities(utility),
    program           TEXT NOT NULL,
    program_cost_usd  REAL,            -- "Total Program Cost of the Utility", converted from $000
    kwh_meter         REAL,            -- first-year kWh saved at the meter (NULL = none credited)
    kwh_generator     REAL,
    net_benefits_usd  REAL,            -- utility-reported net benefits (NULL = not reported)
    kwh_note          TEXT,
    source_file       TEXT NOT NULL,
    source_line       TEXT NOT NULL,
    UNIQUE (utility, program)
);

-- Keywords that mark demand-response / load-control programs (credited in kW, not kWh).
CREATE TABLE demand_keywords (keyword TEXT PRIMARY KEY);

CREATE TABLE goals (
    utility             TEXT PRIMARY KEY REFERENCES utilities(utility),
    achieved_gwh        REAL NOT NULL, goal_gwh        REAL NOT NULL,
    achieved_summer_mw  REAL NOT NULL, goal_summer_mw  REAL NOT NULL,
    achieved_winter_mw  REAL NOT NULL, goal_winter_mw  REAL NOT NULL,
    basis               TEXT, goals_order TEXT, source TEXT
);

-- Program cost lines from each utility's 2025 ECCR final true-up exhibit (Docket 20260002-EG).
CREATE TABLE eccr_lines (
    utility       TEXT NOT NULL REFERENCES utilities(utility),
    line_no       INTEGER NOT NULL,
    eccr_program  TEXT NOT NULL,
    cost_usd      INTEGER NOT NULL,
    source        TEXT NOT NULL,
    PRIMARY KEY (utility, line_no),
    UNIQUE (utility, eccr_program)
);

-- The filed total each utility's lines must add up to.
CREATE TABLE eccr_filed_totals (
    utility    TEXT PRIMARY KEY REFERENCES utilities(utility),
    total_usd  INTEGER NOT NULL,
    what       TEXT, source TEXT
);

-- Analyst's mapping from DSM-report program to ECCR line (eccr_program NULL = no ECCR line).
CREATE TABLE dsm_eccr_map (
    utility       TEXT NOT NULL,
    dsm_program   TEXT NOT NULL,
    eccr_program  TEXT,
    PRIMARY KEY (utility, dsm_program),
    FOREIGN KEY (utility, dsm_program) REFERENCES programs(utility, program)
);

-- Screening thresholds and scenario values (the same defaults as the Excel Assumptions sheet).
CREATE TABLE assumptions (name TEXT PRIMARY KEY, value REAL NOT NULL, description TEXT);

-- Programs with derived flags used by the queries.
CREATE VIEW programs_flagged AS
SELECT p.*,
       u.short_name,
       u.cost_basis,
       EXISTS (SELECT 1 FROM demand_keywords k WHERE lower(p.program) LIKE '%' || k.keyword || '%') AS is_demand_program
FROM programs p
JOIN utilities u USING (utility);
