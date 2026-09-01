-- Stage-to-Stage Transition Drop-off and Loss Quantification
SELECT 
    stage_name,
    candidates_entered,
    candidates_passed,
    candidates_dropped,
    ROUND((candidates_dropped::numeric / NULLIF(candidates_entered, 0)) * 100, 2) AS dropoff_rate
FROM stage_metrics
ORDER BY stage_order ASC;
