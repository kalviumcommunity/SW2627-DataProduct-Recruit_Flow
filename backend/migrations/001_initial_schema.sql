-- backend/migrations/001_initial_schema.sql

-- 1. Create the 3 logical schemas
CREATE SCHEMA IF NOT EXISTS raw;
CREATE SCHEMA IF NOT EXISTS staging;
CREATE SCHEMA IF NOT EXISTS core;

-- 2. Core Audit & Reference
CREATE TABLE core.ingestion_batches (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    filename VARCHAR(255) NOT NULL,
    file_hash VARCHAR(128) NOT NULL,
    status VARCHAR(50) DEFAULT 'pending',
    total_rows INT DEFAULT 0,
    accepted_rows INT DEFAULT 0,
    rejected_rows INT DEFAULT 0,
    uploaded_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE core.departments (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL
);

CREATE TABLE core.stages (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(80) UNIQUE NOT NULL,
    order_index INT UNIQUE NOT NULL,
    is_terminal BOOLEAN DEFAULT FALSE
);

-- 3. Insert Reference Data (Departments & Stages)
INSERT INTO core.departments (name) VALUES 
('Engineering'), ('Sales'), ('Marketing'), ('IT'), ('HR'), ('Finance')
ON CONFLICT (name) DO NOTHING;

INSERT INTO core.stages (name, order_index) VALUES 
('Applied', 1),
('Screening', 2),
('Recruiter Screen', 3),
('Hiring Manager Review', 4),
('Technical Interview', 5),
('Final Interview', 6),
('Offer', 7),
('Offer Accepted', 8),
('Joined', 9)
ON CONFLICT (name) DO NOTHING;

-- 4. Core Business Tables (The Foundation)
CREATE TABLE core.candidates (
    id BIGSERIAL PRIMARY KEY,
    candidate_id VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(255) NULL, -- Notice: NOT UNIQUE
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    phone VARCHAR(50),
    ingestion_batch_id UUID REFERENCES core.ingestion_batches(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE core.jobs (
    id BIGSERIAL PRIMARY KEY,
    job_id VARCHAR(100) UNIQUE NOT NULL,
    job_title VARCHAR(150) NOT NULL,
    department_id BIGINT NOT NULL REFERENCES core.departments(id)
);

CREATE TABLE core.applications (
    id BIGSERIAL PRIMARY KEY,
    application_id VARCHAR(100) UNIQUE NOT NULL,
    candidate_id BIGINT NOT NULL REFERENCES core.candidates(id),
    job_id BIGINT NOT NULL REFERENCES core.jobs(id),
    application_date DATE NOT NULL
    -- Intentionally no UNIQUE(candidate_id, job_id) here
);

CREATE TABLE core.stage_events (
    id BIGSERIAL PRIMARY KEY,
    stage_event_id VARCHAR(100) UNIQUE NOT NULL,
    application_id BIGINT NOT NULL REFERENCES core.applications(id) ON DELETE CASCADE,
    stage_id BIGINT NOT NULL REFERENCES core.stages(id),
    entered_at TIMESTAMP WITH TIME ZONE NOT NULL,
    exited_at TIMESTAMP WITH TIME ZONE,
    dropoff_flag BOOLEAN DEFAULT FALSE,
    dropoff_reason VARCHAR(100),
    CONSTRAINT chk_dropoff CHECK (dropoff_flag = FALSE OR dropoff_reason IS NOT NULL)
);
