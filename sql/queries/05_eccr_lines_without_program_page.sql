-- 05 ECCR costs with no DSM program page: recovered through the clause but absent from program reporting.
-- Recommendation Issue 4.
SELECT l.utility, l.eccr_program, l.cost_usd,
       ROUND(1.0 * l.cost_usd / t.total_usd, 4)                                         AS share_of_filed_total,
       SUM(l.cost_usd) OVER (PARTITION BY l.utility)                                    AS utility_total_without_page_usd,
       ROUND(1.0 * SUM(l.cost_usd) OVER (PARTITION BY l.utility) / t.total_usd, 4)      AS utility_share_without_page
FROM eccr_lines l
JOIN eccr_filed_totals t ON t.utility = l.utility
WHERE NOT EXISTS (SELECT 1 FROM dsm_eccr_map m WHERE m.utility = l.utility AND m.eccr_program = l.eccr_program)
ORDER BY l.utility, l.cost_usd DESC;
