-- database/seed.sql
-- Seed script for initial HR user and BATCH-001 demo data

-- 1. Insert Default HR User
INSERT INTO core.users (id, email, hashed_password, full_name, role)
VALUES (1, 'hr@recruitflow.com', '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeg6Lruj3vjPGga31lW', 'HR Admin', 'hr_user')
ON CONFLICT (email) DO NOTHING;

-- 2. Insert Default Ingestion Batch BATCH-001
INSERT INTO core.ingestion_batches (id, user_id, batch_name, status, total_records, accepted_records, rejected_records)
VALUES ('00000000-0000-0000-0000-000000000001', 1, 'BATCH-001 (Default Seed Batch)', 'active', 10, 10, 0)
ON CONFLICT (id) DO NOTHING;

-- 3. Insert Seed Candidates
INSERT INTO core.candidates (candidate_id, department, role, application_date, source, experience_years, location, ingestion_batch_id)
VALUES 
('C1001', 'IT', 'Backend Developer', '2026-01-05', 'LinkedIn', 2, 'Delhi', '00000000-0000-0000-0000-000000000001'),
('C1002', 'IT', 'Frontend Developer', '2026-01-07', 'Referral', 3, 'Bangalore', '00000000-0000-0000-0000-000000000001'),
('C1003', 'Finance', 'Financial Analyst', '2026-01-08', 'Indeed', 1, 'Mumbai', '00000000-0000-0000-0000-000000000001'),
('C1004', 'IT', 'Data Engineer', '2026-01-10', 'LinkedIn', 4, 'Pune', '00000000-0000-0000-0000-000000000001'),
('C1005', 'HR', 'HR Executive', '2026-01-11', 'Referral', 2, 'Delhi', '00000000-0000-0000-0000-000000000001'),
('C1006', 'Sales', 'Sales Executive', '2026-01-12', 'Company Website', 1, 'Chandigarh', '00000000-0000-0000-0000-000000000001'),
('C1007', 'IT', 'Backend Developer', '2026-01-14', 'LinkedIn', 5, 'Hyderabad', '00000000-0000-0000-0000-000000000001'),
('C1008', 'Finance', 'Accountant', '2026-01-15', 'Indeed', 2, 'Mumbai', '00000000-0000-0000-0000-000000000001'),
('C1009', 'IT', 'QA Engineer', '2026-01-17', 'Referral', 2, 'Bangalore', '00000000-0000-0000-0000-000000000001'),
('C1010', 'Sales', 'Sales Manager', '2026-01-18', 'LinkedIn', 6, 'Delhi', '00000000-0000-0000-0000-000000000001')
ON CONFLICT DO NOTHING;
