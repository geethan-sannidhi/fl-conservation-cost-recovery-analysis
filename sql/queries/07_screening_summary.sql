-- 07 Screening summary: programs per group, and portfolio cost per kWh by utility (screenable programs).
-- Depends on 06 being saved as the view program_screen (scripts/run_queries.py does this).
SELECT 'group' AS kind, screening_group AS label, COUNT(*) AS programs,
       ROUND(SUM(program_cost_usd), 0) AS cost_usd, NULL AS cost_per_kwh
FROM program_screen WHERE screened
GROUP BY screening_group
UNION ALL
SELECT 'utility', utility, COUNT(*), ROUND(SUM(program_cost_usd), 0),
       ROUND(SUM(program_cost_usd) / SUM(kwh_meter), 4)
FROM program_screen WHERE screenable
GROUP BY utility
UNION ALL
SELECT 'portfolio', 'All screenable programs', COUNT(*), ROUND(SUM(program_cost_usd), 0),
       ROUND(SUM(program_cost_usd) / SUM(kwh_meter), 4)
FROM program_screen WHERE screenable
ORDER BY kind, programs DESC;
