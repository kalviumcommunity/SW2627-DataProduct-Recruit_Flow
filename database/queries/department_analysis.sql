-- database/queries/department_analysis.sql
-- Calculate department-wise drop-off rates and compare them against company averages

WITH candidate_outcomes AS (
    SELECT 
        c.candidate_id,
        c.department,
        -- A candidate is joined (hired) if they have a stage = 'Joined' with status 'Completed' or 'Passed'
        -- Or if onboarding table says joining_status = 'Joined'
        CASE 
            WHEN EXISTS (
                SELECT 1 FROM core.recruitment_stages rs 
                WHERE rs.candidate_id = c.candidate_id 
                  AND rs.stage = 'Joined' 
                  AND rs.status IN ('Completed', 'Passed', 'Joined')
            ) OR EXISTS (
                SELECT 1 FROM core.onboarding o
                WHERE o.candidate_id = c.candidate_id
                  AND o.joining_status = 'Joined'
            ) THEN 0 -- Not dropped (hired & joined)
            ELSE 1 -- Dropped
        END as is_dropped
    FROM core.candidates c
),
company_avg AS (
    SELECT 
        COUNT(*)::float as company_total,
        SUM(is_dropped)::float as company_dropped,
        (SUM(is_dropped)::float / COUNT(*)::float) * 100.0 as company_dropoff_rate
    FROM candidate_outcomes
),
dept_metrics AS (
    SELECT 
        co.department,
        COUNT(*) as total_candidates,
        SUM(co.is_dropped) as dropped_candidates,
        COUNT(*) - SUM(co.is_dropped) as joined_candidates,
        ROUND(((SUM(co.is_dropped)::float / COUNT(*)::float) * 100.0)::numeric, 2) as department_dropoff_rate
    FROM candidate_outcomes co
    GROUP BY co.department
)
SELECT 
    dm.department,
    dm.total_candidates,
    dm.dropped_candidates,
    dm.joined_candidates,
    dm.department_dropoff_rate,
    ROUND(ca.company_dropoff_rate::numeric, 2) as company_average_dropoff_rate,
    ROUND((dm.department_dropoff_rate - ca.company_dropoff_rate)::numeric, 2) as delta_from_company_average
FROM dept_metrics dm
CROSS JOIN company_avg ca
ORDER BY dm.department;
