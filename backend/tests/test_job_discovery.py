"""
Tests for Phase 2: Job Discovery & Collection.
Covers:
- Job parsing & cleaning
- Location filtering (strictly Lahore or Remote)
- Entry-level filtering (rejecting Senior, Lead, 5+ yrs)
- Deduplication detection (URL & content fingerprinting)
- Database insertion and schema integrity
"""

import pytest
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.app.database import Base
from backend.app.models import Job, JobDiscoveryRun
from backend.app.services.job_discovery.base_source import RawDiscoveredJob
from backend.app.services.job_discovery.job_cleaner_service import JobCleanerService
from backend.app.services.job_discovery.sources.registry import get_all_sources, list_source_infos


@pytest.fixture
def test_db():
    """In-memory SQLite database for isolated test execution."""
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = TestingSessionLocal()
    yield db
    db.close()


def test_job_cleaning_and_normalization():
    raw = RawDiscoveredJob(
        company="systems ltd [lahore]",
        job_title="Junior Python Developer [Urgent] - Lahore",
        location="DHA Phase 8, Lahore",
        description="Systems is looking for a junior python engineer.\n\nKey Responsibilities:\n- Build REST APIs with FastAPI\n- Write unit tests\n- Maintain PostgreSQL tables.",
        responsibilities=[],
        required_skills=["Python", "FastAPI"],
        source="Systems Careers",
        source_url="https://systemsltd.com/careers/jr-py"
    )

    cleaned = JobCleanerService.clean_and_normalize(raw)

    # Verifies normalization
    assert cleaned.company == "Systems Limited"
    assert "Urgent" not in cleaned.job_title
    assert cleaned.job_title == "Junior Python Developer"
    assert len(cleaned.responsibilities) >= 2
    assert "Build REST APIs with FastAPI" in cleaned.responsibilities[0]
    assert cleaned.raw_description == raw.description


def test_location_filtering():
    # Valid Lahore locations
    assert JobCleanerService.is_lahore_location("Lahore, Pakistan", "")[0] is True
    assert JobCleanerService.is_lahore_location("DHA Phase 6, Lahore", "")[0] is True
    assert JobCleanerService.is_lahore_location("Remote (Pakistan)", "")[0] is True

    # Invalid non-Lahore locations
    assert JobCleanerService.is_lahore_location("Karachi, Sindh", "")[0] is False
    assert JobCleanerService.is_lahore_location("Islamabad, Federal", "")[0] is False
    assert JobCleanerService.is_lahore_location("London, UK", "")[0] is False


def test_entry_level_filtering():
    # Valid entry-level roles
    assert JobCleanerService.is_entry_level("Junior Software Engineer", "Work with senior engineers", "0-1 years")[0] is True
    assert JobCleanerService.is_entry_level("Associate Python Developer", "Fresh graduates welcome", "0 years")[0] is True
    assert JobCleanerService.is_entry_level("Software Engineering Intern", "3-month internship", "Student")[0] is True
    assert JobCleanerService.is_entry_level("Trainee Engineer", "Comprehensive training", "Fresh")[0] is True

    # Senior roles that MUST be rejected
    is_valid, reason = JobCleanerService.is_entry_level("Senior Python Architect", "Lead backend", "7+ years")
    assert is_valid is False
    assert "senior" in reason.lower()

    is_valid_lead, reason_lead = JobCleanerService.is_entry_level("Principal Software Engineer", "10+ years experience", "10+ years")
    assert is_valid_lead is False

    is_valid_exp, reason_exp = JobCleanerService.is_entry_level("Backend Developer", "Must have 6+ years of experience in distributed systems", "5+ years")
    assert is_valid_exp is False


def test_duplicate_detection(test_db):
    job1 = Job(
        company="Arbisoft",
        job_title="Junior Software Engineer",
        location="Lahore, Pakistan",
        source_url="https://arbisoft.com/careers/jse-1",
        job_url="https://arbisoft.com/careers/jse-1",
        description="Backend engineering with Python and Django.",
        source="Arbisoft Careers",
        dedup_hash=JobCleanerService.compute_dedup_hash("Arbisoft", "Junior Software Engineer", "Lahore, Pakistan", "https://arbisoft.com/careers/jse-1", "Backend engineering with Python and Django.")
    )
    test_db.add(job1)
    test_db.commit()

    # Exact URL duplicate
    duplicate_raw = RawDiscoveredJob(
        company="Arbisoft",
        job_title="Junior Software Engineer",
        location="Lahore, Pakistan",
        description="Backend engineering with Python and Django.",
        source="Arbisoft Careers",
        source_url="https://arbisoft.com/careers/jse-1"
    )
    is_dup, canonical_id = JobCleanerService.detect_duplicate(duplicate_raw, test_db)
    assert is_dup is True
    assert canonical_id == job1.id

    # New unique job
    unique_raw = RawDiscoveredJob(
        company="Devsinc",
        job_title="Associate QA Engineer",
        location="Lahore, Pakistan",
        description="Quality assurance testing.",
        source="Devsinc Careers",
        source_url="https://devsinc.com/careers/qa-1"
    )
    is_dup_unique, _ = JobCleanerService.detect_duplicate(unique_raw, test_db)
    assert is_dup_unique is False


def test_modular_source_registry():
    sources = get_all_sources()
    assert "systems_limited" in sources
    assert "arbisoft" in sources
    assert "devsinc" in sources
    assert "rozee_pk" in sources

    infos = list_source_infos()
    assert len(infos) >= 6
    assert any(info.id == "systems_limited" for info in infos)


def test_database_discovery_run_record(test_db):
    run = JobDiscoveryRun(
        status="completed",
        sources_checked=["systems_limited", "arbisoft"],
        keywords_used=["Python Developer", "Software Engineer"],
        total_discovered=5,
        new_jobs_added=3,
        duplicates_skipped=1,
        rejected_non_lahore=1,
        rejected_non_entry=0
    )
    test_db.add(run)
    test_db.commit()
    test_db.refresh(run)

    assert run.id is not None
    assert run.new_jobs_added == 3
    assert run.duplicates_skipped == 1
    assert run.status == "completed"
