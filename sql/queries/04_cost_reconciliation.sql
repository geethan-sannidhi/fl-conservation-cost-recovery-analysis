-- 04 Cost reconciliation: DSM-report program cost vs. ECCR true-up cost, one row per ECCR line that has
-- at least one DSM program page. Tolerance = the DSM report's rounding x number of DSM programs on the line.
-- Recommendation Issue 3.
WITH a AS (
    SELECT MAX(CASE WHEN name = 'tol_k'    THEN value END) AS tol_k,
           MAX(CASE WHEN name = 'tol_teco' THEN value END) AS tol_teco
    FROM assumptions
),
dsm AS (
    SELECT m.utility, m.eccr_program,
           COUNT(*)                         AS dsm_programs,
           GROUP_CONCAT(m.dsm_program, '; ') AS dsm_program_names,
           SUM(p.program_cost_usd)          AS dsm_cost_usd
    FROM dsm_eccr_map m
    JOIN programs p ON p.utility = m.utility AND p.program = m.dsm_program
    WHERE m.eccr_program IS NOT NULL
    GROUP BY m.utility, m.eccr_program
)
SELECT l.utility, l.line_no, l.eccr_program,
       l.cost_usd                         AS eccr_cost_usd,
       d.dsm_programs, d.dsm_program_names,
       d.dsm_cost_usd,
       d.dsm_cost_usd - l.cost_usd        AS difference_usd,
       d.dsm_programs * CASE WHEN l.utility = 'Tampa Electric' THEN a.tol_teco ELSE a.tol_k END AS tolerance_usd,
       CASE WHEN ABS(d.dsm_cost_usd - l.cost_usd)
                 <= d.dsm_programs * CASE WHEN l.utility = 'Tampa Electric' THEN a.tol_teco ELSE a.tol_k END
            THEN 'Yes' ELSE 'No' END       AS within_rounding
FROM eccr_lines l
JOIN dsm d ON d.utility = l.utility AND d.eccr_program = l.eccr_program
CROSS JOIN a
ORDER BY l.utility, l.line_no;
