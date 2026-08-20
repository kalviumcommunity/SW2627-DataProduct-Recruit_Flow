-- database/schema.sql
-- Fixed PostgreSQL Schema for RecruitFlow HR Recruitment Intelligence Platform

-- 1. Create Logical Schemas
CREATE SCHEMA IF NOT EXISTS raw;
CREATE SCHEMA IF NOT EXISTS staging;
CREATE SCHEMA IF NOT EXISTS core;

-- Enable UUID extension if available
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 2. User Credentials Table (HR Authentication)
CREATE TABLE IF NOT EXISTS core.users (
    id BIGSERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(150),
    role VARCHAR(50) DEFAULT 'hr_user',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 3. Ingestion Batches Lineage Table
CREATE TABLE IF NOT EXISTS core.ingestion_batches (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id BIGINT REFERENCES core.users(id) ON DELETE SET NULL,
    batch_name VARCHAR(150) NOT NULL,
    status VARCHAR(50) DEFAULT 'active', -- active, processing, cleared, failed
    total_records INT DEFAULT 0,
    accepted_records INT DEFAULT 0,
    rejected_records INT DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 4. Core Candidates Table
CREATE TABLE IF NOT EXISTS core.candidates (
    id BIGSERIAL PRIMARY KEY,
    candidate_id VARCHAR(100) NOT NULL,
    department VARCHAR(100),
    role VARCHAR(150),
    application_date DATE,
    source VARCHAR(100),
    experience_years INT,
    location VARCHAR(100),
    ingestion_batch_id UUID REFERENCES core.ingestion_batches(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 5. Core Recruitment Stage Events Table
CREATE TABLE IF NOT EXISTS core.recruitment_stages (
    id BIGSERIAL PRIMARY KEY,
    candidate_id VARCHAR(100) NOT NULL,
    stage VARCHAR(100) NOT NULL,
    stage_entry_date DATE,
    stage_exit_date DATE,
    status VARCHAR(50),
    rejection_reason VARCHAR(255),
    ingestion_batch_id UUID REFERENCES core.ingestion_batches(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 6. Core Interviews Ratings Table
CREATE TABLE IF NOT EXISTS core.interviews (
    id BIGSERIAL PRIMARY KEY,
    interview_id VARCHAR(100) NOT NULL,
    candidate_id VARCHAR(100) NOT NULL,
    stage VARCHAR(100),
    interview_date DATE,
    interviewer VARCHAR(150),
    technical_score INT,
    communication_score INT,
    overall_score FLOAT,
    recommendation VARCHAR(100),
    feedback TEXT,
    ingestion_batch_id UUID REFERENCES core.ingestion_batches(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 7. Core Onboarding Outcomes Table
CREATE TABLE IF NOT EXISTS core.onboarding (
    id BIGSERIAL PRIMARY KEY,
    candidate_id VARCHAR(100) NOT NULL,
    offer_date DATE,
    offer_status VARCHAR(50),
    expected_joining_date DATE,
    actual_joining_date DATE,
    joining_status VARCHAR(50),
    onboarding_status VARCHAR(50),
    ingestion_batch_id UUID REFERENCES core.ingestion_batches(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 8. Validation Errors Audit Log Table
CREATE TABLE IF NOT EXISTS core.validation_errors (
    id BIGSERIAL PRIMARY KEY,
    ingestion_batch_id UUID REFERENCES core.ingestion_batches(id) ON DELETE CASCADE,
    entity_type VARCHAR(50) NOT NULL,
    row_number INT,
    error_message TEXT NOT NULL,
    raw_payload TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexing for Query Velocity
CREATE INDEX IF NOT EXISTS idx_candidates_batch ON core.candidates(ingestion_batch_id);
CREATE INDEX IF NOT EXISTS idx_candidates_cid ON core.candidates(candidate_id);
CREATE INDEX IF NOT EXISTS idx_stages_batch ON core.recruitment_stages(ingestion_batch_id);
CREATE INDEX IF NOT EXISTS idx_stages_cid ON core.recruitment_stages(candidate_id);
CREATE INDEX IF NOT EXISTS idx_interviews_batch ON core.interviews(ingestion_batch_id);
CREATE INDEX IF NOT EXISTS idx_interviews_cid ON core.interviews(candidate_id);
CREATE INDEX IF NOT EXISTS idx_onboarding_batch ON core.onboarding(ingestion_batch_id);
CREATE INDEX IF NOT EXISTS idx_onboarding_cid ON core.onboarding(candidate_id);
