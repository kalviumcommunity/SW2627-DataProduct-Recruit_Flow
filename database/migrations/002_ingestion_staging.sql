-- backend/migrations/002_ingestion_staging.sql
-- Adds the ingestion pipeline tables and the batch columns required by the current code.

CREATE EXTENSION IF NOT EXISTS pgcrypto;

ALTER TABLE core.ingestion_batches
    ADD COLUMN IF NOT EXISTS file_type VARCHAR(20),
    ADD COLUMN IF NOT EXISTS error_message TEXT;

CREATE TABLE IF NOT EXISTS raw.raw_records (
    id BIGSERIAL PRIMARY KEY,
    ingestion_batch_id UUID NOT NULL REFERENCES core.ingestion_batches(id) ON DELETE CASCADE,
    entity_type VARCHAR(50) NOT NULL,
    source_file_name VARCHAR(255) NOT NULL,
    source_row_number INTEGER NOT NULL,
    raw_data JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS staging.candidates (
    staging_record_id BIGSERIAL PRIMARY KEY,
    ingestion_batch_id UUID NOT NULL REFERENCES core.ingestion_batches(id) ON DELETE CASCADE,
    raw_record_id BIGINT REFERENCES raw.raw_records(id),
    source_row_number INTEGER,
    validation_status VARCHAR(20) DEFAULT 'pending',
    validation_error_count INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    candidate_id VARCHAR(100),
    email VARCHAR(255),
    original_email VARCHAR(255),
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    phone VARCHAR(50)
);

CREATE TABLE IF NOT EXISTS staging.jobs (
    staging_record_id BIGSERIAL PRIMARY KEY,
    ingestion_batch_id UUID NOT NULL REFERENCES core.ingestion_batches(id) ON DELETE CASCADE,
    raw_record_id BIGINT REFERENCES raw.raw_records(id),
    source_row_number INTEGER,
    validation_status VARCHAR(20) DEFAULT 'pending',
    validation_error_count INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    job_id VARCHAR(100),
    job_title VARCHAR(150),
    department VARCHAR(100),
    location VARCHAR(150),
    employment_type VARCHAR(50)
);

CREATE TABLE IF NOT EXISTS staging.applications (
    staging_record_id BIGSERIAL PRIMARY KEY,
    ingestion_batch_id UUID NOT NULL REFERENCES core.ingestion_batches(id) ON DELETE CASCADE,
    raw_record_id BIGINT REFERENCES raw.raw_records(id),
    source_row_number INTEGER,
    validation_status VARCHAR(20) DEFAULT 'pending',
    validation_error_count INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    application_id VARCHAR(100),
    candidate_id VARCHAR(100),
    job_id VARCHAR(100),
    application_date VARCHAR(50),
    source VARCHAR(100)
);

CREATE TABLE IF NOT EXISTS staging.stage_events (
    staging_record_id BIGSERIAL PRIMARY KEY,
    ingestion_batch_id UUID NOT NULL REFERENCES core.ingestion_batches(id) ON DELETE CASCADE,
    raw_record_id BIGINT REFERENCES raw.raw_records(id),
    source_row_number INTEGER,
    validation_status VARCHAR(20) DEFAULT 'pending',
    validation_error_count INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    stage_event_id VARCHAR(100),
    application_id VARCHAR(100),
    stage_name VARCHAR(80),
    entered_at VARCHAR(50),
    exited_at VARCHAR(50),
    stage_outcome VARCHAR(50),
    dropoff_flag VARCHAR(10),
    dropoff_reason VARCHAR(100)
);

CREATE TABLE IF NOT EXISTS core.validation_errors (
    id BIGSERIAL PRIMARY KEY,
    ingestion_batch_id UUID NOT NULL REFERENCES core.ingestion_batches(id) ON DELETE CASCADE,
    entity_type VARCHAR(50) NOT NULL,
    source_row_number INTEGER,
    error_message TEXT NOT NULL,
    raw_data JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_staging_candidates_batch ON staging.candidates(ingestion_batch_id);
CREATE INDEX IF NOT EXISTS idx_staging_jobs_batch ON staging.jobs(ingestion_batch_id);
CREATE INDEX IF NOT EXISTS idx_staging_applications_batch ON staging.applications(ingestion_batch_id);
CREATE INDEX IF NOT EXISTS idx_staging_stage_events_batch ON staging.stage_events(ingestion_batch_id);
