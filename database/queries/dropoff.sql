-- database/queries/dropoff.sql
-- Cross-tabulate drop-off reasons by stage and department

WITH candidate_dropoffs AS (
    SELECT 
        c.candidate_id,
        c.department,
        rs.stage as dropoff_stage,
        -- Standardize rejection reasons to match REASON_MAP behavior
        COALESCE(
            CASE 
                WHEN LOWER(rs.rejection_reason) LIKE '%technical mismatch%' 
                     OR LOWER(rs.rejection_reason) LIKE '%tech mismatch%' 
                     OR LOWER(rs.rejection_reason) LIKE '%insufficient python knowledge%' 
                     OR LOWER(rs.rejection_reason) LIKE '%failed technical interview%' THEN 'Technical Mismatch'
                WHEN LOWER(rs.rejection_reason) LIKE '%salary%' 
                     OR LOWER(rs.rejection_reason) LIKE '%compensation%' THEN 'Salary Expectation'
                WHEN LOWER(rs.rejection_reason) LIKE '%candidate withdrew%' 
                     OR LOWER(rs.rejection_reason) LIKE '%application put on hold; candidate withdrew%' THEN 'Candidate Withdrew'
                WHEN LOWER(rs.rejection_reason) LIKE '%did not join after accepting offer%' 
                     OR LOWER(rs.rejection_reason) = 'no show' 
                     OR LOWER(rs.rejection_reason) = 'no-show' THEN 'No Show'
                WHEN LOWER(rs.rejection_reason) LIKE '%declined offer - better opportunity%' 
                     OR LOWER(rs.rejection_reason) LIKE '%declined offer - better opportunity elsewhere%' THEN 'Offer Declined - Better Opportunity'
                ELSE INITCAP(rs.rejection_reason)
            END,
            'Unspecified Drop-off'
        ) as rejection_reason
    FROM core.candidates c
    JOIN core.recruitment_stages rs ON c.candidate_id = rs.candidate_id
    WHERE rs.status IN ('Rejected', 'Withdrawn', 'No-show')
)
SELECT 
    department,
    dropoff_stage as stage,
    rejection_reason,
    COUNT(*) as count
FROM candidate_dropoffs
GROUP BY department, dropoff_stage, rejection_reason
ORDER BY department, dropoff_stage, count DESC;
