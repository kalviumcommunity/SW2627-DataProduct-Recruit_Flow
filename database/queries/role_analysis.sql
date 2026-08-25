-- database/queries/role_analysis.sql
-- Drill down into specific roles within departments and compare against department averages

WITH candidate_outcomes AS (
    SELECT 
        c.candidate_id,
        c.department,
        c.role,
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
            ) THEN 0
            ELSE 1
        END as is_dropped
    FROM core.candidates c
),
dept_metrics AS (
    SELECT 
        department,
        (SUM(is_dropped)::float / COUNT(*)::float) * 100.0 as department_dropoff_rate
    FROM candidate_outcomes
    GROUP BY department
),
role_metrics AS (
    SELECT 
        department,
        role,
        COUNT(*) as total_candidates,
        SUM(is_dropped) as dropped_candidates,
        COUNT(*) - SUM(is_dropped) as joined_candidates,
        ROUND(((SUM(is_dropped)::float / COUNT(*)::float) * 100.0)::numeric, 2) as role_dropoff_rate
    FROM candidate_outcomes
    GROUP BY department, role
)
SELECT 
    rm.department,
    rm.role,
    rm.total_candidates,
    rm.dropped_candidates,
    rm.joined_candidates,
    rm.role_dropoff_rate,
    ROUND(dm.department_dropoff_rate::numeric, 2) as department_average_dropoff_rate,
    ROUND((rm.role_dropoff_rate - dm.department_dropoff_rate)::numeric, 2) as delta_from_department_average
FROM role_metrics rm
JOIN dept_metrics dm ON rm.department = dm.department
ORDER BY rm.department, rm.role_dropoff_rate DESC;
