-- 08 Participation sensitivity: cost per kWh at low / actual / high participation, with a fixed share of cost
-- that does not scale. Flags programs whose cost tier changes across the range. Recommendation Issue 6.
WITH a AS (
    SELECT MAX(CASE WHEN name = 'fixed_share' THEN value END) AS f,
           MAX(CASE WHEN name = 'part_lo'     THEN value END) AS lo,
           MAX(CASE WHEN name = 'part_hi'     THEN value END) AS hi,
           MAX(CASE WHEN name = 'low_tier'    THEN value END) AS low_tier,
           MAX(CASE WHEN name = 'high_tier'   THEN value END) AS high_tier
    FROM assumptions
),
s AS (
    SELECT ps.utility, ps.program, ps.cost_per_kwh,
           ps.cost_per_kwh * (a.f + (1 - a.f) * a.lo) / a.lo AS cpk_low,
           ps.cost_per_kwh * (a.f + (1 - a.f) * a.hi) / a.hi AS cpk_high,
           a.low_tier, a.high_tier
    FROM program_screen ps CROSS JOIN a
    WHERE ps.screened
)
SELECT utility, program,
       ROUND(cpk_low, 4) AS cost_per_kwh_low_participation,
       ROUND(cost_per_kwh, 4) AS cost_per_kwh_actual,
       ROUND(cpk_high, 4) AS cost_per_kwh_high_participation,
       CASE WHEN (cpk_low  <= low_tier) <> (cpk_high <= low_tier)
              OR (cpk_low  <= high_tier) <> (cpk_high <= high_tier) THEN 'Yes' ELSE 'No' END AS tier_changes
FROM s
ORDER BY tier_changes DESC, cost_per_kwh;
