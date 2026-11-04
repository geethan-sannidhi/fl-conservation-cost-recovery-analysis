-- 02 Savings reconciliation: do program pages add up to each utility's reported total (GWh at the generator)?
-- Recommendation Issue 2.
SELECT g.utility,
       ROUND(SUM(p.kwh_generator) / 1e6, 3)                          AS program_pages_gwh_generator,
       ROUND(SUM(p.kwh_meter) / 1e6, 3)                              AS program_pages_gwh_meter,
       g.achieved_gwh                                                AS reported_gwh,
       ROUND(SUM(p.kwh_generator) / 1e6 - g.achieved_gwh, 3)         AS difference_gwh,
       ROUND((SUM(p.kwh_generator) / 1e6 - g.achieved_gwh) / g.achieved_gwh, 4) AS difference_pct
FROM goals g
JOIN programs p ON p.utility = g.utility
GROUP BY g.utility, g.achieved_gwh
ORDER BY ABS(difference_pct) DESC;
