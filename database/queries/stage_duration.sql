-- Average and Median Days Spent Per Recruitment Stage
SELECT 
    stage,
    ROUND(AVG(EXTRACT(EPOCH FROM (exited_at - entered_at)) / 86400)::numeric, 1) AS avg_duration_days,
    ROUND(PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY EXTRACT(EPOCH FROM (exited_at - entered_at)) / 86400)::numeric, 1) AS median_duration_days
FROM stage_events
WHERE entered_at IS NOT NULL AND exited_at IS NOT NULL
GROUP BY stage;
