-- 06 Program screen: cost per first-year kWh, simple payback, cost tier and screening group.
-- Screenable = not a demand program, kWh credited, fully loaded cost. Screened = screenable and cost >= materiality.
-- Recommendation Issue 5.
WITH a AS (
    SELECT MAX(CASE WHEN name = 'low_tier'    THEN value END) AS low_tier,
           MAX(CASE WHEN name = 'high_tier'   THEN value END) AS high_tier,
           MAX(CASE WHEN name = 'value_1'     THEN value END) AS value_1,
           MAX(CASE WHEN name = 'value_2'     THEN value END) AS value_2,
           MAX(CASE WHEN name = 'value_3'     THEN value END) AS value_3,
           MAX(CASE WHEN name = 'materiality' THEN value END) AS materiality
    FROM assumptions
),
base AS (
    SELECT p.*, a.*,
           CASE WHEN NOT p.is_demand_program AND p.kwh_meter > 0 AND p.program_cost_usd IS NOT NULL
                THEN p.program_cost_usd / p.kwh_meter END AS cost_per_kwh
    FROM programs_flagged p CROSS JOIN a
),
tiered AS (
    SELECT *,
           CASE WHEN cost_per_kwh IS NULL THEN NULL
                WHEN cost_per_kwh <= low_tier  THEN 'lower'
                WHEN cost_per_kwh <= high_tier THEN 'moderate'
                ELSE 'higher' END AS cost_tier,
           (cost_per_kwh IS NOT NULL AND cost_basis = 'total program cost') AS screenable
    FROM base
)
SELECT utility, short_name, program, cost_basis, program_cost_usd, kwh_meter, net_benefits_usd,
       is_demand_program, screenable,
       ROUND(cost_per_kwh, 6)                                    AS cost_per_kwh,
       ROUND(program_cost_usd / (kwh_meter * value_1), 2)        AS payback_years_value_1,
       ROUND(program_cost_usd / (kwh_meter * value_2), 2)        AS payback_years_value_2,
       ROUND(program_cost_usd / (kwh_meter * value_3), 2)        AS payback_years_value_3,
       cost_tier,
       (screenable AND program_cost_usd >= materiality)          AS screened,
       CASE WHEN NOT (screenable AND program_cost_usd >= materiality) THEN NULL
            WHEN net_benefits_usd IS NULL THEN
                 CASE WHEN cost_tier = 'higher' THEN 'Needs more support' ELSE 'Insufficient information' END
            WHEN cost_tier <> 'higher' AND net_benefits_usd > 0 THEN 'Appears cost-effective'
            WHEN cost_tier =  'higher' AND net_benefits_usd <= 0 THEN 'Needs more support'
            ELSE 'Mixed signals' END                             AS screening_group
FROM tiered
ORDER BY screened DESC, cost_per_kwh;
