-- 03 ECCR transcription check: do each exhibit's program lines add up to its filed total?
SELECT t.utility,
       COUNT(l.line_no)              AS lines,
       SUM(l.cost_usd)               AS sum_of_lines_usd,
       t.total_usd                   AS filed_total_usd,
       SUM(l.cost_usd) - t.total_usd AS difference_usd,
       t.what
FROM eccr_filed_totals t
JOIN eccr_lines l ON l.utility = t.utility
GROUP BY t.utility, t.total_usd, t.what;
