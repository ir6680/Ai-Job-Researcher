# Lahore AI Job Application Agent

> **Goal:** End-to-end autonomous agent targeting entry-level software/IT engineering jobs in Lahore, Pakistan.

---

## 📌 Phase 1 & Phase 2 Architecture Overview

### Phase 1: Foundation (Master CV, Relational Schema & REST APIs)
- **Master CV Module:** Deterministic, non-hallucinatory parsing from `PDF`, `DOCX`, and `TXT` files. Factual extraction of contact links, education, skills catalog, experience, and projects.
- **PostgreSQL Database:** Relational models for `users`, `master_cv`, `skills`, `education`, `experience`, `projects`, `certifications`, `jobs`, `applications`, and `tailored_cvs`.
- **FastAPI Backend:** Clean modular REST endpoints with Pydantic v2 schemas.

### Phase 2: Job Discovery & Collection (New in Phase 2)
- **Automated Multi-Source Discovery:**
  - Official company career pages for Lahore software powerhouses:
    - **Systems Limited** (DHA Phase 8 & Central campuses)
    - **Arbisoft** (Canal Road, Thokar Niaz Baig campus - Fresh Grad batch)
    - **Devsinc** (Johar Town & Gulberg campuses)
    - **Tintash** (Cantt / DHA campus)
    - **10Pearls** (Gulberg III campus)
    - **Netsol Technologies** (NetSol Avenue, Ring Road campus - Graduate Trainee Engineer)
    - **Confiz** (Gulberg campus)
  - Legitimate job boards:
    - **Rozee.pk IT Board** (TkXel, VentureDive, Afiniti, etc.)
  - Search engine aggregated discovery feeds.
- **Modular Source Architecture:** Every source implements `BaseJobSource` with individual timeout protection and graceful degradation (failure in one source never crashes the run).
- **Data Cleaning & Normalization:**
  - Company names normalized to canonical representations (e.g. `Systems Ltd` → `Systems Limited`).
  - Job titles stripped of bracketed urgency or location noise (e.g. `[Urgent]`, `(Immediate)`).
  - Preservation of full original text in `raw_description`.
  - Structured extraction of `responsibilities` bullet points.
- **Location Filtering:** Strictly accepts `Lahore, Pakistan` and `Remote (Pakistan)`. Rejects jobs explicitly designated for other regions (Karachi, Islamabad, Dubai, UK) unless remote.
- **Entry-Level Filtering:** Matches entry-level keywords (`0-1 years`, `Fresh`, `Trainee`, `Intern`, `Associate`, `Junior`). Strictly rejects Senior, Principal, Lead, Architect, and 4+ years roles.
- **Deduplication Engine:**
  - Multi-tier matching: Exact URL match, SHA-256 content fingerprint (`dedup_hash`), and company + normalized title similarity.
  - Prevents redundant entries and marks canonical references.
- **Audit & Metrics Tracking:** Every discovery run is logged in `job_discovery_runs` table with metrics (total raw collected, new added, duplicates skipped, non-Lahore rejected, non-entry rejected).

---

## 🗄️ Database Schema Updates (Phase 2 Migration)

To migrate an existing Phase 1 database to Phase 2, execute the following SQL statements:

```sql
-- Add Phase 2 columns to jobs table
ALTER TABLE jobs ADD COLUMN IF NOT EXISTS source_url VARCHAR(1000);
ALTER TABLE jobs ADD COLUMN IF NOT EXISTS raw_description TEXT;
ALTER TABLE jobs ADD COLUMN IF NOT EXISTS responsibilities JSONB DEFAULT '[]';
ALTER TABLE jobs ADD COLUMN IF NOT EXISTS discovered_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP;
ALTER TABLE jobs ADD COLUMN IF NOT EXISTS posting_date VARCHAR(50);
ALTER TABLE jobs ADD COLUMN IF NOT EXISTS deadline VARCHAR(50);
ALTER TABLE jobs ADD COLUMN IF NOT EXISTS job_status VARCHAR(50) DEFAULT 'discovered';
ALTER TABLE jobs ADD COLUMN IF NOT EXISTS duplicate_status VARCHAR(50) DEFAULT 'unique';
ALTER TABLE jobs ADD COLUMN IF NOT EXISTS canonical_job_id VARCHAR(36);
ALTER TABLE jobs ADD COLUMN IF NOT EXISTS dedup_hash VARCHAR(64);

-- Create indexes for high-speed deduplication lookups
CREATE INDEX IF NOT EXISTS idx_jobs_dedup_hash ON jobs(dedup_hash);
CREATE INDEX IF NOT EXISTS idx_jobs_duplicate_status ON jobs(duplicate_status);
CREATE INDEX IF NOT EXISTS idx_jobs_discovered_at ON jobs(discovered_at);

-- Create job_discovery_runs audit table
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
```

*(Note: When launching freshly via Docker Compose or `init_db.sql`, all tables and columns are created automatically).*

---

## 🚀 Setup & Local Execution

### Option A: Docker Compose (PostgreSQL 16 + FastAPI)

1. Copy environment variables:
   ```bash
   cp .env.example .env
   ```
2. Start the multi-container stack:
   ```bash
   docker-compose up --build
   ```
3. Access services:
   - **Interactive API Documentation:** `http://localhost:8000/docs`
   - **Alternative ReDoc:** `http://localhost:8000/redoc`
   - **API Base:** `http://localhost:8000/api/v1`

---

### Option B: Local Python 3.12+ Setup

1. Create and activate a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate    # Windows: .\venv\Scripts\activate
   ```
2. Install requirements:
   ```bash
   pip install -r requirements.txt
   ```
3. Configure `.env`:
   ```bash
   cp .env.example .env
   ```
   *(For fast testing without a local PostgreSQL instance, `DATABASE_URL="sqlite:///./job_agent.db"` is supported).*
4. Run the Uvicorn server:
   ```bash
   uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
   ```

---

## 🧪 Automated Testing

Run the test suite with:
```bash
pytest backend/tests -v
```

### Verified Test Cases (`backend/tests/test_job_discovery.py`):
- `test_job_cleaning_and_normalization`: Validates normalization of company names (`systems ltd [lahore]` → `Systems Limited`), title noise stripping, and extraction of responsibilities.
- `test_location_filtering`: Validates acceptance of Lahore/Remote locations and rejection of Karachi, Islamabad, and overseas locations.
- `test_entry_level_filtering`: Verifies entry-level acceptance (`Junior`, `Associate`, `Intern`, `Trainee`, `0-1 yrs`) and strict rejection of Senior, Lead, Principal, and 5+ years positions.
- `test_duplicate_detection`: Verifies URL-based and SHA-256 fingerprint deduplication against existing database records.
- `test_modular_source_registry`: Verifies all modular career sources are registered and active.
- `test_database_discovery_run_record`: Verifies audit metric recording in `job_discovery_runs`.

---

## 🔌 Phase 2 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/v1/jobs/discover` | Trigger an automated job discovery run with configurable keywords & sources |
| `GET` | `/api/v1/jobs/discovery-runs` | Retrieve historical discovery run audit logs and metrics |
| `GET` | `/api/v1/jobs/discovery-sources` | List all registered modular discovery sources |
| `GET` | `/api/v1/jobs` | Query jobs with faceted filters (`keyword`, `company`, `source`, `location`, `status`, `duplicate_status`) |
| `GET` | `/api/v1/jobs/{id}` | View complete collected job details (full description, responsibilities, metadata) |
| `PATCH`| `/api/v1/jobs/{id}/status` | Update job status (`saved`, `ignored`, `applied`, `archived`) |
| `POST` | `/api/v1/jobs/{id}/refresh` | Re-clean, normalize, and extract responsibilities for an existing job |
| `POST` | `/api/v1/jobs` | Manually add a job opening |
| `DELETE`| `/api/v1/jobs/{id}` | Delete a job record |

---

## 🛡️ Anti-Bot & Rate-Limiting Policy
- All discovery connectors utilize descriptive User-Agent headers (`LahoreJobAgent/2.0`).
- No CAPTCHAs, authentication barriers, or anti-bot protections are bypassed.
- Each source is queried with bounded timeouts (15s default) and individual exception handling.

---

## 🗺️ What is Intentionally Reserved for Phase 3
Phase 2 strictly handles discovery, extraction, cleaning, and deduplication. The following are intentionally reserved for **Phase 3**:
1. **Job Description (JD) Semantic Analysis:** Extracting hard skills vs soft skills weighting from collected JDs.
2. **CV-to-Job Matching Engine:** Computing compatibility scores between the candidate's Master CV and discovered Lahore jobs.
3. **AI CV Tailoring Engine:** Selecting optimal projects, skills, and highlights tailored to specific job requirements.
4. **Tailored Application Generation:** Exporting tailored PDF/DOCX CVs and cover letters.
5. **Browser Automation:** Headless submission automation (Playwright/Selenium).
