-- database/queries/stage_duration.sql
-- Calculate stage duration metrics (Average, Median, Min, Max) and identify hiring bottlenecks

-- 1. Stage-level duration statistics & Bottleneck Analysis
WITH stage_intervals AS (
    SELECT 
        rs.candidate_id,
        rs.stage,
        COALESCE(rs.stage_exit_date, rs.stage_entry_date) - rs.stage_entry_date AS duration_days
    FROM core.recruitment_stages rs
    WHERE rs.stage_entry_date IS NOT NULL
),
stage_stats AS (
    SELECT 
        stage,
        COUNT(DISTINCT candidate_id) as candidates_count,
        ROUND(AVG(duration_days)::numeric, 2) as avg_duration_days,
        PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY duration_days) as median_duration_days,
        MIN(duration_days) as min_duration_days,
        MAX(duration_days) as max_duration_days,
        ROUND(COALESCE(STDDEV(duration_days), 0)::numeric, 2) as std_duration_days
    FROM stage_intervals
    GROUP BY stage
),
overall_avg AS (
    SELECT AVG(avg_duration_days) as benchmark_avg_days
    FROM stage_stats
)
SELECT 
    ss.stage,
    ss.candidates_count,
    ss.avg_duration_days,
    ss.median_duration_days,
    ss.min_duration_days,
    ss.max_duration_days,
    ss.std_duration_days,
    CASE 
        WHEN ss.avg_duration_days > oa.benchmark_avg_days * 1.5 THEN 'High Bottleneck'
        WHEN ss.avg_duration_days >= oa.benchmark_avg_days THEN 'Medium Bottleneck'
        ELSE 'Normal'
    END as bottleneck_severity
FROM stage_stats ss
CROSS JOIN overall_avg oa
ORDER BY ss.avg_duration_days DESC;

-- 2. Department-wise Hiring Velocity Breakdown
WITH candidate_journey_duration AS (
    SELECT 
        c.candidate_id,
        c.department,
        MIN(rs.stage_entry_date) as start_date,
        MAX(COALESCE(rs.stage_exit_date, rs.stage_entry_date)) as end_date,
        MAX(COALESCE(rs.stage_exit_date, rs.stage_entry_date)) - MIN(rs.stage_entry_date) as total_duration_days,
        CASE 
            WHEN EXISTS (
                SELECT 1 FROM core.recruitment_stages r_sub 
                WHERE r_sub.candidate_id = c.candidate_id 
                  AND r_sub.stage = 'Joined' 
                  AND r_sub.status IN ('Completed', 'Passed', 'Joined')
            ) THEN 1 
            ELSE 0 
        END as is_hired
    FROM core.candidates c
    JOIN core.recruitment_stages rs ON c.candidate_id = rs.candidate_id
    GROUP BY c.candidate_id, c.department
)
SELECT 
    department,
    COUNT(*) as total_candidates,
    ROUND(AVG(total_duration_days)::numeric, 2) as avg_total_duration_days,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY total_duration_days) as median_total_duration_days,
    ROUND(AVG(CASE WHEN is_hired = 1 THEN total_duration_days END)::numeric, 2) as avg_time_to_hire_days,
    ROUND(AVG(CASE WHEN is_hired = 0 THEN total_duration_days END)::numeric, 2) as avg_time_to_drop_days
FROM candidate_journey_duration
GROUP BY department
ORDER BY avg_total_duration_days DESC;
