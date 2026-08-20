-- backend/migrations/005_core_load_errors.sql
-- Records why dedup/entity-resolution skipped a row during core loading.

CREATE TABLE IF NOT EXISTS core.load_errors (
    id BIGSERIAL PRIMARY KEY,
    ingestion_batch_id UUID NOT NULL REFERENCES core.ingestion_batches(id) ON DELETE CASCADE,
    entity_type VARCHAR(50) NOT NULL,
    source_row_number INTEGER,
    external_id VARCHAR(100),
    reason TEXT NOT NULL,
    raw_data JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_core_load_errors_batch
    ON core.load_errors(ingestion_batch_id);

CREATE INDEX IF NOT EXISTS idx_core_load_errors_entity
    ON core.load_errors(entity_type);
