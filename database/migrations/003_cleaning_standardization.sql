-- backend/migrations/003_cleaning_standardization.sql
-- Adds cleaning-state and standardization metadata to staging tables.

ALTER TABLE staging.candidates
    ADD COLUMN IF NOT EXISTS cleaned_status VARCHAR(20) DEFAULT 'pending',
    ADD COLUMN IF NOT EXISTS cleaned_at TIMESTAMP WITH TIME ZONE,
    ADD COLUMN IF NOT EXISTS _email_standardized BOOLEAN DEFAULT FALSE;

ALTER TABLE staging.jobs
    ADD COLUMN IF NOT EXISTS cleaned_status VARCHAR(20) DEFAULT 'pending',
    ADD COLUMN IF NOT EXISTS cleaned_at TIMESTAMP WITH TIME ZONE,
    ADD COLUMN IF NOT EXISTS _department_standardized BOOLEAN DEFAULT FALSE;

ALTER TABLE staging.applications
    ADD COLUMN IF NOT EXISTS cleaned_status VARCHAR(20) DEFAULT 'pending',
    ADD COLUMN IF NOT EXISTS cleaned_at TIMESTAMP WITH TIME ZONE,
    ADD COLUMN IF NOT EXISTS _date_parsed BOOLEAN DEFAULT FALSE;

ALTER TABLE staging.stage_events
    ADD COLUMN IF NOT EXISTS cleaned_status VARCHAR(20) DEFAULT 'pending',
    ADD COLUMN IF NOT EXISTS cleaned_at TIMESTAMP WITH TIME ZONE,
    ADD COLUMN IF NOT EXISTS _stage_standardized BOOLEAN DEFAULT FALSE,
    ADD COLUMN IF NOT EXISTS _entered_parsed BOOLEAN DEFAULT FALSE,
    ADD COLUMN IF NOT EXISTS _exited_parsed BOOLEAN DEFAULT FALSE,
    ADD COLUMN IF NOT EXISTS _dropoff_flag_standardized BOOLEAN DEFAULT FALSE,
    ADD COLUMN IF NOT EXISTS _reason_standardized BOOLEAN DEFAULT FALSE;

CREATE INDEX IF NOT EXISTS idx_staging_candidates_cleaned_status
    ON staging.candidates(cleaned_status);

CREATE INDEX IF NOT EXISTS idx_staging_jobs_cleaned_status
    ON staging.jobs(cleaned_status);

CREATE INDEX IF NOT EXISTS idx_staging_applications_cleaned_status
    ON staging.applications(cleaned_status);

CREATE INDEX IF NOT EXISTS idx_staging_stage_events_cleaned_status
    ON staging.stage_events(cleaned_status);
