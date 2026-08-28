-- Role-Wise Candidate Volume & Drop-off Breakdown within Departments
SELECT 
    c.department,
    c.job_role,
    COUNT(DISTINCT c.candidate_id) AS total_applied,
    COUNT(DISTINCT CASE WHEN s.stage = 'Joined' THEN c.candidate_id END) AS total_joined,
    ROUND((1.0 - (COUNT(DISTINCT CASE WHEN s.stage = 'Joined' THEN c.candidate_id END)::numeric / NULLIF(COUNT(DISTINCT c.candidate_id), 0))) * 100, 2) AS dropoff_rate
FROM candidates c
LEFT JOIN stage_events s ON c.candidate_id = s.candidate_id
GROUP BY c.department, c.job_role
ORDER BY c.department, dropoff_rate DESC;
