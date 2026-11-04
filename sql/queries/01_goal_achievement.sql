-- 01 Goal achievement: did each utility meet its 2025 approved goals (annual energy, summer and winter peak)?
-- Recommendation Issue 1.
SELECT utility,
       achieved_gwh, goal_gwh,
       ROUND(achieved_gwh / goal_gwh, 4)                 AS pct_energy_goal,
       ROUND(achieved_summer_mw / goal_summer_mw, 4)     AS pct_summer_goal,
       ROUND(achieved_winter_mw / goal_winter_mw, 4)     AS pct_winter_goal,
       CASE WHEN achieved_gwh >= goal_gwh
             AND achieved_summer_mw >= goal_summer_mw
             AND achieved_winter_mw >= goal_winter_mw THEN 'Yes' ELSE 'No' END AS all_goals_met,
       TRIM(CASE WHEN achieved_gwh < goal_gwh THEN 'energy ' ELSE '' END ||
            CASE WHEN achieved_summer_mw < goal_summer_mw THEN 'summer ' ELSE '' END ||
            CASE WHEN achieved_winter_mw < goal_winter_mw THEN 'winter' ELSE '' END) AS goals_missed
FROM goals
ORDER BY pct_energy_goal DESC;
