-- backend/migrations/006_candidate_journey_reconstruction.sql
-- Adds journey reconstruction support and exposes analytical views for Part B.

ALTER TABLE core.stage_events
    ADD COLUMN IF NOT EXISTS stage_outcome VARCHAR(50),
    ADD COLUMN IF NOT EXISTS is_derived BOOLEAN DEFAULT FALSE,
    ADD COLUMN IF NOT EXISTS derivation_reason TEXT;

UPDATE core.stage_events
SET is_derived = COALESCE(is_derived, FALSE);

CREATE OR REPLACE VIEW core.v_application_journey AS
WITH stage_timeline AS (
    SELECT
        a.id AS application_internal_id,
        a.application_id,
        a.candidate_id,
        c.candidate_id AS candidate_external_id,
        c.email,
        c.first_name,
        c.last_name,
        j.job_id,
        j.job_title,
        d.name AS department,
        s.id AS stage_internal_id,
        s.name AS stage_name,
        s.order_index AS stage_order,
        se.entered_at,
        se.exited_at,
        se.stage_outcome,
        COALESCE(se.dropoff_flag, FALSE) AS dropoff_flag,
        se.dropoff_reason,
        se.feedback,
        COALESCE(se.is_derived, FALSE) AS is_derived,
        se.derivation_reason,
        EXTRACT(EPOCH FROM (se.exited_at - se.entered_at)) / 86400 AS duration_days,
        ROW_NUMBER() OVER (PARTITION BY a.id ORDER BY se.entered_at, se.id) AS stage_sequence,
        COUNT(se.id) OVER (PARTITION BY a.id) AS total_stages
    FROM core.applications a
    JOIN core.candidates c ON a.candidate_id = c.id
    JOIN core.jobs j ON a.job_id = j.id
    JOIN core.departments d ON j.department_id = d.id
    LEFT JOIN core.stage_events se ON a.id = se.application_id
    LEFT JOIN core.stages s ON se.stage_id = s.id
)
SELECT
    application_internal_id,
    application_id,
    candidate_external_id,
    email,
    first_name,
    last_name,
    job_id,
    job_title,
    department,
    stage_internal_id,
    stage_name,
    stage_order,
    entered_at,
    exited_at,
    stage_outcome,
    dropoff_flag,
    dropoff_reason,
    feedback,
    is_derived,
    derivation_reason,
    duration_days,
    stage_sequence,
    total_stages,
    CASE WHEN exited_at IS NULL THEN TRUE ELSE FALSE END AS is_current_stage,
    CASE WHEN dropoff_flag = TRUE THEN TRUE ELSE FALSE END AS is_dropoff_stage
FROM stage_timeline
ORDER BY application_id, stage_sequence;

CREATE OR REPLACE VIEW core.v_application_summary AS
WITH journey_summary AS (
    SELECT
        a.id AS application_internal_id,
        a.application_id,
        a.candidate_id,
        c.candidate_id AS candidate_external_id,
        c.email,
        j.job_id,
        j.job_title,
        d.name AS department,
        a.application_date,
        a.source,
        MIN(se.entered_at) AS first_entered_at,
        MAX(COALESCE(se.exited_at, se.entered_at)) AS last_event_at,
        COUNT(se.id) AS total_stages_entered,
        COALESCE(BOOL_OR(se.dropoff_flag), FALSE) AS has_dropoff,
        (
            SELECT s.name
            FROM core.stage_events se2
            JOIN core.stages s ON se2.stage_id = s.id
            WHERE se2.application_id = a.id
              AND se2.dropoff_flag = TRUE
            ORDER BY se2.entered_at DESC, se2.id DESC
            LIMIT 1
        ) AS dropoff_stage,
        (
            SELECT se2.dropoff_reason
            FROM core.stage_events se2
            WHERE se2.application_id = a.id
              AND se2.dropoff_flag = TRUE
            ORDER BY se2.entered_at DESC, se2.id DESC
            LIMIT 1
        ) AS dropoff_reason,
        (
            SELECT se2.stage_outcome
            FROM core.stage_events se2
            WHERE se2.application_id = a.id
            ORDER BY se2.entered_at DESC, se2.id DESC
            LIMIT 1
        ) AS final_outcome,
        (
            SELECT s.name
            FROM core.stage_events se2
            JOIN core.stages s ON se2.stage_id = s.id
            WHERE se2.application_id = a.id
            ORDER BY se2.entered_at DESC, se2.id DESC
            LIMIT 1
        ) AS final_stage,
        COALESCE(BOOL_OR(se.stage_outcome = 'Joined'), FALSE) AS is_hired,
        EXISTS (
            SELECT 1
            FROM core.stage_events se2
            JOIN core.stages s ON se2.stage_id = s.id
            WHERE se2.application_id = a.id
              AND s.name IN ('Offer', 'Offer Accepted')
        ) AS reached_offer_stage,
        EXTRACT(EPOCH FROM (MAX(COALESCE(se.exited_at, se.entered_at)) - a.application_date::timestamp)) / 86400 AS total_days_in_process
    FROM core.applications a
    JOIN core.candidates c ON a.candidate_id = c.id
    JOIN core.jobs j ON a.job_id = j.id
    JOIN core.departments d ON j.department_id = d.id
    LEFT JOIN core.stage_events se ON a.id = se.application_id
    GROUP BY a.id, c.id, j.id, d.id, a.application_date, a.source
)
SELECT
    application_internal_id,
    application_id,
    candidate_external_id,
    email,
    job_id,
    job_title,
    department,
    application_date,
    source,
    first_entered_at,
    last_event_at,
    total_stages_entered,
    has_dropoff,
    dropoff_stage,
    dropoff_reason,
    final_outcome,
    final_stage,
    is_hired,
    reached_offer_stage,
    total_days_in_process,
    CASE
        WHEN is_hired THEN 'Hired'
        WHEN has_dropoff AND dropoff_stage = 'Offer' THEN 'Offer Declined'
        WHEN has_dropoff THEN 'Dropped Out'
        WHEN total_stages_entered > 0 AND last_event_at IS NOT NULL AND last_event_at > first_entered_at THEN 'In Progress'
        ELSE 'Unknown'
    END AS application_status
FROM journey_summary;
