-- backend/migrations/004_deduplication_entity_resolution.sql
-- Extends core tables so cleaned staging data can be resolved into core entities.

ALTER TABLE core.candidates
    ADD COLUMN IF NOT EXISTS original_email VARCHAR(255);

ALTER TABLE core.ingestion_batches
    ADD COLUMN IF NOT EXISTS duplicate_rows INT DEFAULT 0;

ALTER TABLE core.jobs
    ADD COLUMN IF NOT EXISTS location VARCHAR(150),
    ADD COLUMN IF NOT EXISTS employment_type VARCHAR(50),
    ADD COLUMN IF NOT EXISTS opening_date DATE,
    ADD COLUMN IF NOT EXISTS closing_date DATE,
    ADD COLUMN IF NOT EXISTS job_status VARCHAR(50),
    ADD COLUMN IF NOT EXISTS ingestion_batch_id UUID REFERENCES core.ingestion_batches(id);

ALTER TABLE core.applications
    ADD COLUMN IF NOT EXISTS source VARCHAR(100),
    ADD COLUMN IF NOT EXISTS ingestion_batch_id UUID REFERENCES core.ingestion_batches(id);

ALTER TABLE core.stage_events
    ADD COLUMN IF NOT EXISTS feedback TEXT,
    ADD COLUMN IF NOT EXISTS ingestion_batch_id UUID REFERENCES core.ingestion_batches(id),
    ADD COLUMN IF NOT EXISTS source_row_number INTEGER;

CREATE TABLE IF NOT EXISTS core.possible_duplicates (
    id BIGSERIAL PRIMARY KEY,
    ingestion_batch_id UUID REFERENCES core.ingestion_batches(id) ON DELETE CASCADE,
    entity_type VARCHAR(50) NOT NULL,
    matched_on VARCHAR(100) NOT NULL,
    primary_record_id BIGINT,
    secondary_record_id BIGINT,
    reason TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_possible_duplicates_batch
    ON core.possible_duplicates(ingestion_batch_id);
