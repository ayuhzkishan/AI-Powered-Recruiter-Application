-- Run with: psql $DATABASE_URL -f app/db/schema.sql

CREATE EXTENSION IF NOT EXISTS "pgcrypto";   -- For gen_random_uuid()

CREATE TABLE IF NOT EXISTS users (
    id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email            VARCHAR(255) UNIQUE NOT NULL,
    hashed_password  VARCHAR(255) NOT NULL,
    full_name        VARCHAR(100),
    role             VARCHAR(20) DEFAULT 'recruiter',
    created_at       TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS candidates (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    first_name          VARCHAR(100) NOT NULL,
    last_name           VARCHAR(100) NOT NULL,
    email               VARCHAR(255) UNIQUE NOT NULL,
    phone               VARCHAR(20),
    raw_resume_text     TEXT,
    resume_file_path    VARCHAR(500),
    processing_status   VARCHAR(20) DEFAULT 'pending',
    created_by          UUID REFERENCES users(id) ON DELETE SET NULL,
    created_at          TIMESTAMPTZ DEFAULT NOW(),
    updated_at          TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS job_descriptions (
    id                       UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title                    VARCHAR(200) NOT NULL,
    department               VARCHAR(100),
    status                   VARCHAR(20) DEFAULT 'draft',
    raw_description          TEXT NOT NULL,
    minimum_experience_years INTEGER DEFAULT 0,
    created_by               UUID REFERENCES users(id) ON DELETE SET NULL,
    created_at               TIMESTAMPTZ DEFAULT NOW(),
    updated_at               TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS ai_analysis (
    id                          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    candidate_id                UUID REFERENCES candidates(id) ON DELETE CASCADE,
    summary                     TEXT,
    extracted_skills            JSONB,
    extracted_education         JSONB,
    extracted_experience        JSONB,
    calculated_years_experience NUMERIC(4,1),
    extracted_projects          JSONB,
    extracted_certifications    JSONB,
    created_at                  TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS match_records (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    candidate_id    UUID REFERENCES candidates(id) ON DELETE CASCADE,
    job_id          UUID REFERENCES job_descriptions(id) ON DELETE CASCADE,
    match_score     NUMERIC(5,2),
    fit_analysis    JSONB,
    skill_mapping   JSONB,
    review_status   VARCHAR(20) DEFAULT 'pending',
    matched_at      TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(candidate_id, job_id)
);
