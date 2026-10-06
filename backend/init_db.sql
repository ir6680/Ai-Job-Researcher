-- ==============================================================
-- Lahore AI Job Application Agent - Phase 1 PostgreSQL Schema DDL
-- Database: job_agent_db
-- ==============================================================

-- Enable UUID extension if available
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 1. Users Table
CREATE TABLE IF NOT EXISTS users (
    id VARCHAR(36) PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    target_city VARCHAR(100) DEFAULT 'Lahore',
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 2. Master CV Table
CREATE TABLE IF NOT EXISTS master_cv (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    full_name VARCHAR(255) NOT NULL,
    email VARCHAR(255),
    phone VARCHAR(50),
    location VARCHAR(255) DEFAULT 'Lahore, Pakistan',
    summary TEXT,
    github_url VARCHAR(500),
    linkedin_url VARCHAR(500),
    portfolio_url VARCHAR(500),
    website_url VARCHAR(500),
    version INTEGER DEFAULT 1,
    is_primary BOOLEAN DEFAULT TRUE,
    raw_text TEXT,
    source_filename VARCHAR(255),
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 3. Skills Table
CREATE TABLE IF NOT EXISTS skills (
    id VARCHAR(36) PRIMARY KEY,
    master_cv_id VARCHAR(36) NOT NULL REFERENCES master_cv(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    category VARCHAR(50) DEFAULT 'Technical',
    proficiency VARCHAR(50) DEFAULT 'Intermediate',
    years_of_experience REAL,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 4. Education Table
CREATE TABLE IF NOT EXISTS education (
    id VARCHAR(36) PRIMARY KEY,
    master_cv_id VARCHAR(36) NOT NULL REFERENCES master_cv(id) ON DELETE CASCADE,
    institution VARCHAR(255) NOT NULL,
    degree VARCHAR(255) NOT NULL,
    field_of_study VARCHAR(255),
    start_date VARCHAR(50),
    end_date VARCHAR(50),
    is_current BOOLEAN DEFAULT FALSE,
    grade_or_gpa VARCHAR(50),
    location VARCHAR(100) DEFAULT 'Lahore, Pakistan',
    description TEXT,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 5. Experience Table
CREATE TABLE IF NOT EXISTS experience (
    id VARCHAR(36) PRIMARY KEY,
    master_cv_id VARCHAR(36) NOT NULL REFERENCES master_cv(id) ON DELETE CASCADE,
    company_name VARCHAR(255) NOT NULL,
    role_title VARCHAR(255) NOT NULL,
    employment_type VARCHAR(50) DEFAULT 'Full-time',
    location VARCHAR(100) DEFAULT 'Lahore, Pakistan',
    start_date VARCHAR(50),
    end_date VARCHAR(50),
    is_current BOOLEAN DEFAULT FALSE,
    description TEXT,
    highlights JSONB DEFAULT '[]',
    technologies_used JSONB DEFAULT '[]',
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 6. Projects Table
CREATE TABLE IF NOT EXISTS projects (
    id VARCHAR(36) PRIMARY KEY,
    master_cv_id VARCHAR(36) NOT NULL REFERENCES master_cv(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    role VARCHAR(100),
    technologies JSONB DEFAULT '[]',
    repo_url VARCHAR(500),
    live_url VARCHAR(500),
    start_date VARCHAR(50),
    end_date VARCHAR(50),
    highlights JSONB DEFAULT '[]',
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 7. Certifications Table
CREATE TABLE IF NOT EXISTS certifications (
    id VARCHAR(36) PRIMARY KEY,
    master_cv_id VARCHAR(36) NOT NULL REFERENCES master_cv(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    issuing_organization VARCHAR(255) NOT NULL,
    issue_date VARCHAR(50),
    expiration_date VARCHAR(50),
    credential_id VARCHAR(100),
    credential_url VARCHAR(500),
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 8. Jobs Table (Phase 2 Discovery & Deduplication Extended)
CREATE TABLE IF NOT EXISTS jobs (
    id VARCHAR(36) PRIMARY KEY,
    company VARCHAR(255) NOT NULL,
    job_title VARCHAR(255) NOT NULL,
    location VARCHAR(255) DEFAULT 'Lahore, Pakistan',
    job_url VARCHAR(1000),
    source_url VARCHAR(1000),
    description TEXT NOT NULL,
    raw_description TEXT,
    responsibilities JSONB DEFAULT '[]',
    required_skills JSONB DEFAULT '[]',
    preferred_skills JSONB DEFAULT '[]',
    experience_requirement VARCHAR(100) DEFAULT 'Entry-level (0-1 years)',
    education_requirement VARCHAR(255) DEFAULT 'BS Computer Science / Software Engineering',
    job_type VARCHAR(50) DEFAULT 'Full-time',
    salary VARCHAR(100),
    source VARCHAR(100) DEFAULT 'Manual',
    status VARCHAR(50) DEFAULT 'discovered',
    job_status VARCHAR(50) DEFAULT 'discovered',
    discovered_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    posting_date VARCHAR(50),
    deadline VARCHAR(50),
    duplicate_status VARCHAR(50) DEFAULT 'unique',
    canonical_job_id VARCHAR(36),
    dedup_hash VARCHAR(64),
    notes TEXT,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 9. Job Discovery Runs Table (Phase 2 Audit & Tracking)
CREATE TABLE IF NOT EXISTS job_discovery_runs (
    id VARCHAR(36) PRIMARY KEY,
    triggered_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP WITHOUT TIME ZONE,
    status VARCHAR(50) DEFAULT 'running',
    sources_checked JSONB DEFAULT '[]',
    keywords_used JSONB DEFAULT '[]',
    total_discovered INTEGER DEFAULT 0,
    new_jobs_added INTEGER DEFAULT 0,
    duplicates_skipped INTEGER DEFAULT 0,
    rejected_non_lahore INTEGER DEFAULT 0,
    rejected_non_entry INTEGER DEFAULT 0,
    error_message TEXT,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 10. Tailored CVs Table (Prepared for Phase 3)
CREATE TABLE IF NOT EXISTS tailored_cvs (
    id VARCHAR(36) PRIMARY KEY,
    master_cv_id VARCHAR(36) NOT NULL REFERENCES master_cv(id) ON DELETE CASCADE,
    job_id VARCHAR(36) NOT NULL REFERENCES jobs(id) ON DELETE CASCADE,
    tailored_content JSONB DEFAULT '{}',
    match_score REAL,
    highlighted_skills JSONB DEFAULT '[]',
    version INTEGER DEFAULT 1,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 10. Applications Table
CREATE TABLE IF NOT EXISTS applications (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    job_id VARCHAR(36) NOT NULL REFERENCES jobs(id) ON DELETE CASCADE,
    master_cv_id VARCHAR(36) NOT NULL REFERENCES master_cv(id) ON DELETE CASCADE,
    tailored_cv_id VARCHAR(36) REFERENCES tailored_cvs(id) ON DELETE SET NULL,
    status VARCHAR(50) DEFAULT 'draft',
    applied_at TIMESTAMP WITHOUT TIME ZONE,
    interview_date TIMESTAMP WITHOUT TIME ZONE,
    notes TEXT,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for high-speed lookups
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_master_cv_user ON master_cv(user_id);
CREATE INDEX IF NOT EXISTS idx_skills_cv ON skills(master_cv_id);
CREATE INDEX IF NOT EXISTS idx_skills_name ON skills(name);
CREATE INDEX IF NOT EXISTS idx_jobs_company ON jobs(company);
CREATE INDEX IF NOT EXISTS idx_jobs_status ON jobs(status);
CREATE INDEX IF NOT EXISTS idx_applications_status ON applications(status);
CREATE INDEX IF NOT EXISTS idx_applications_job ON applications(job_id);
