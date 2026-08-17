-- backend/migrations/007_supporting_entities_schema.sql
-- Adds schema support for interviews, offers, and onboarding as supporting MVP entities.

-- ============================================================
-- STAGING TABLES
-- ============================================================

CREATE TABLE IF NOT EXISTS staging.interviews (
    staging_record_id BIGSERIAL PRIMARY KEY,
    ingestion_batch_id UUID NOT NULL REFERENCES core.ingestion_batches(id) ON DELETE CASCADE,
    raw_record_id BIGINT REFERENCES raw.raw_records(id),
    source_row_number INTEGER,
    validation_status VARCHAR(20) DEFAULT 'pending',
    validation_error_count INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    cleaned_status VARCHAR(20) DEFAULT 'pending',
    cleaned_at TIMESTAMP WITH TIME ZONE,
    interview_id VARCHAR(100),
    application_id VARCHAR(100),
    candidate_id VARCHAR(100),
    interview_type VARCHAR(80),
    scheduled_at VARCHAR(50),
    completed_at VARCHAR(50),
    interview_status VARCHAR(50),
    technical_score VARCHAR(20),
    communication_score VARCHAR(20),
    overall_score VARCHAR(20),
    recommendation VARCHAR(50),
    feedback TEXT
);

CREATE TABLE IF NOT EXISTS staging.offers (
    staging_record_id BIGSERIAL PRIMARY KEY,
    ingestion_batch_id UUID NOT NULL REFERENCES core.ingestion_batches(id) ON DELETE CASCADE,
    raw_record_id BIGINT REFERENCES raw.raw_records(id),
    source_row_number INTEGER,
    validation_status VARCHAR(20) DEFAULT 'pending',
    validation_error_count INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    cleaned_status VARCHAR(20) DEFAULT 'pending',
    cleaned_at TIMESTAMP WITH TIME ZONE,
    offer_id VARCHAR(100),
    application_id VARCHAR(100),
    candidate_id VARCHAR(100),
    offer_date VARCHAR(50),
    offered_role VARCHAR(150),
    offered_salary VARCHAR(50),
    currency VARCHAR(20),
    joining_date VARCHAR(50),
    offer_status VARCHAR(50),
    response_date VARCHAR(50),
    offer_rejection_reason TEXT
);

CREATE TABLE IF NOT EXISTS staging.onboarding (
    staging_record_id BIGSERIAL PRIMARY KEY,
    ingestion_batch_id UUID NOT NULL REFERENCES core.ingestion_batches(id) ON DELETE CASCADE,
    raw_record_id BIGINT REFERENCES raw.raw_records(id),
    source_row_number INTEGER,
    validation_status VARCHAR(20) DEFAULT 'pending',
    validation_error_count INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    cleaned_status VARCHAR(20) DEFAULT 'pending',
    cleaned_at TIMESTAMP WITH TIME ZONE,
    onboarding_id VARCHAR(100),
    offer_id VARCHAR(100),
    application_id VARCHAR(100),
    candidate_id VARCHAR(100),
    planned_joining_date VARCHAR(50),
    actual_joining_date VARCHAR(50),
    joining_status VARCHAR(50),
    no_join_reason TEXT,
    onboarding_completed VARCHAR(10)
);

-- ============================================================
-- CORE TABLES
-- ============================================================

CREATE TABLE IF NOT EXISTS core.interviews (
    id BIGSERIAL PRIMARY KEY,
    interview_id VARCHAR(100) UNIQUE NOT NULL,
    application_id BIGINT NOT NULL REFERENCES core.applications(id) ON DELETE CASCADE,
    candidate_id BIGINT NOT NULL REFERENCES core.candidates(id),
    interview_type VARCHAR(80),
    scheduled_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    interview_status VARCHAR(50),
    technical_score NUMERIC(4,1),
    communication_score NUMERIC(4,1),
    overall_score NUMERIC(4,1),
    recommendation VARCHAR(50),
    feedback TEXT,
    ingestion_batch_id UUID REFERENCES core.ingestion_batches(id),
    source_row_number INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS core.offers (
    id BIGSERIAL PRIMARY KEY,
    offer_id VARCHAR(100) UNIQUE NOT NULL,
    application_id BIGINT NOT NULL REFERENCES core.applications(id) ON DELETE CASCADE,
    candidate_id BIGINT NOT NULL REFERENCES core.candidates(id),
    offer_date DATE,
    offered_role VARCHAR(150),
    offered_salary NUMERIC(12,2),
    currency VARCHAR(20),
    joining_date DATE,
    offer_status VARCHAR(50),
    response_date DATE,
    offer_rejection_reason TEXT,
    ingestion_batch_id UUID REFERENCES core.ingestion_batches(id),
    source_row_number INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS core.onboarding (
    id BIGSERIAL PRIMARY KEY,
    onboarding_id VARCHAR(100) UNIQUE NOT NULL,
    offer_id BIGINT NOT NULL REFERENCES core.offers(id) ON DELETE CASCADE,
    application_id BIGINT NOT NULL REFERENCES core.applications(id) ON DELETE CASCADE,
    candidate_id BIGINT NOT NULL REFERENCES core.candidates(id),
    planned_joining_date DATE,
    actual_joining_date DATE,
    joining_status VARCHAR(50),
    no_join_reason TEXT,
    onboarding_completed BOOLEAN DEFAULT FALSE,
    ingestion_batch_id UUID REFERENCES core.ingestion_batches(id),
    source_row_number INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================================
-- INDEXES
-- ============================================================

CREATE INDEX IF NOT EXISTS idx_staging_interviews_batch ON staging.interviews(ingestion_batch_id);
CREATE INDEX IF NOT EXISTS idx_staging_offers_batch ON staging.offers(ingestion_batch_id);
CREATE INDEX IF NOT EXISTS idx_staging_onboarding_batch ON staging.onboarding(ingestion_batch_id);

CREATE INDEX IF NOT EXISTS idx_core_interviews_batch ON core.interviews(ingestion_batch_id);
CREATE INDEX IF NOT EXISTS idx_core_offers_batch ON core.offers(ingestion_batch_id);
CREATE INDEX IF NOT EXISTS idx_core_onboarding_batch ON core.onboarding(ingestion_batch_id);

CREATE INDEX IF NOT EXISTS idx_core_interviews_application ON core.interviews(application_id);
CREATE INDEX IF NOT EXISTS idx_core_offers_application ON core.offers(application_id);
CREATE INDEX IF NOT EXISTS idx_core_onboarding_application ON core.onboarding(application_id);

