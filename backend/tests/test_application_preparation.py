"""
Comprehensive Unit & Integration Test Suite for Phase 5:
Application Preparation & Human Approval Engine.

Covers:
1. Application package creation
2. Missing information detection
3. Cover letter evidence validation
4. Application field traceability
5. User edits stored separately
6. Master CV immutability guaranteed
7. Approval workflow and status transitions (DRAFT -> READY_FOR_SUBMISSION)
8. Safety boundary: rejection of SUBMITTED status transition
9. Unsupported claim rejection / Hallucination guard in cover letter
10. Readiness validation criteria
11. Eligibility gate & manual override
12. End-to-end API endpoints via FastAPI TestClient
"""

import os
import pytest
from datetime import datetime
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.app.database import Base
from backend.app.main import app
from backend.app.models import (
    User, MasterCV, Skill, Experience, Project, Education, Job, TailoredCV,
    Application, ApplicationPackage, ApplicationAnswer, ApplicationReview
)
from backend.app.services.application_service.application_engine import ApplicationEngine
from backend.app.services.application_service.cover_letter_generator import CoverLetterGenerator
from backend.app.services.tailoring.tailoring_engine import CVTailoringEngine


@pytest.fixture
def app_db():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    TestingSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = TestingSession()

    # Seed User & Master CV
    user = User(email="irfanbinrajpoot@gmail.com", full_name="Irfan Rajpoot")
    db.add(user)
    db.flush()

    cv = MasterCV(
        user_id=user.id,
        full_name="Irfan Rajpoot",
        email="irfanbinrajpoot@gmail.com",
        phone="+92 300 1234567",
        location="Lahore, Pakistan",
        summary="AI and Backend Software Engineer based in Lahore with experience developing Python REST APIs and machine learning pipelines.",
        github_url="https://github.com/irfanrajpoot",
        linkedin_url="https://linkedin.com/in/irfan-rajpoot",
        portfolio_url="https://irfanrajpoot.dev",
        is_primary=True,
        version=1
    )
    db.add(cv)
    db.flush()

    # Skills
    skills = [
        ("Python", "Languages", "Expert"),
        ("REST APIs", "Frameworks", "Expert"),
        ("AI/ML", "Technical", "Intermediate"),
        ("Git", "Tools/DevOps", "Expert"),
        ("FastAPI", "Frameworks", "Intermediate"),
        ("SQL", "Databases", "Intermediate"),
        ("PostgreSQL", "Databases", "Intermediate"),
        ("RAG", "Technical", "Beginner"),
        ("Agentic Systems", "Technical", "Beginner"),
    ]
    for name, cat, prof in skills:
        db.add(Skill(master_cv_id=cv.id, name=name, category=cat, proficiency=prof))

    # Experience: Munshi.AI
    db.add(Experience(
        master_cv_id=cv.id,
        company_name="Munshi.AI",
        role_title="AI/ML Engineer",
        description="Built agentic workflows and FastAPI backend microservices.",
        highlights=[
            "Built resilient agentic pipelines using Python and FastAPI.",
            "Designed and consumed high-throughput REST APIs.",
            "Collaborated on experimental LLM retrieval mechanisms."
        ],
        technologies_used=["Python", "FastAPI", "AI/ML", "Git"]
    ))

    # Projects
    db.add(Project(
        master_cv_id=cv.id,
        title="AI/ML FYP",
        description="Autonomous AI agent simulation and evaluation benchmark.",
        technologies=["Python", "PyTorch", "FastAPI", "Machine Learning"],
        highlights=[
            "Implemented baseline agentic models and evaluation benchmarks.",
            "Engineered REST API endpoints for model inference and tracking."
        ]
    ))
    db.add(Project(
        master_cv_id=cv.id,
        title="Inventory Tracker",
        description="Database management project built during university.",
        technologies=["Python", "SQL", "Flask"],
        highlights=["Built basic CRUD tables for inventory records."]
    ))

    # Education
    db.add(Education(
        master_cv_id=cv.id,
        institution="University in Lahore",
        degree="BS in Computer Science",
        location="Lahore, Pakistan"
    ))

    # Target Job 1: Eligible Whizzbridge AI Role (Match >= 70)
    job_ai = Job(
        company="Whizzbridge",
        job_title="AI Application Engineer (Agentic Systems)",
        location="Lahore, Pakistan",
        source="Whizzbridge Careers",
        source_url="https://www.whizzbridge.com/career/ai-application-engineer-agentic-systems",
        description="Seeking an AI Application Engineer to build agentic systems, Python services, and RAG pipelines.",
        required_skills=["Python", "REST APIs", "AI/ML", "Git", "RAG", "Agentic Systems", "Docker", "AWS"],
        dedup_hash="whizzbridge_agentic_ai_app_hash_1"
    )
    db.add(job_ai)

    # Target Job 2: Low-scoring job (Match < 70)
    job_low = Job(
        company="Legacy Mobile Ltd",
        job_title="Senior iOS Architect",
        location="Karachi, Pakistan",
        source="External",
        source_url="https://example.com/jobs/ios-arch",
        description="Requires 10+ years Swift, Objective-C, and mobile architecture experience.",
        required_skills=["Swift", "Objective-C", "iOS Architecture", "CoreData", "Metal"],
        dedup_hash="senior_ios_architect_app_hash_2"
    )
    db.add(job_low)

    db.commit()
    return db


@pytest.fixture
def client(app_db):
    from backend.app.database import get_db
    app.dependency_overrides[get_db] = lambda: app_db
    test_client = TestClient(app)
    yield test_client
    app.dependency_overrides.clear()


def test_application_package_creation(app_db):
    """1. Verify application package is created with all required components."""
    job = app_db.query(Job).filter(Job.company == "Whizzbridge").first()
    app_record = ApplicationEngine.prepare_application_package(app_db, job.id)

    assert app_record is not None
    assert app_record.job_id == job.id
    assert app_record.tailored_cv_id is not None
    assert app_record.cover_letter is not None
    assert "Whizzbridge" in app_record.cover_letter
    assert "Munshi.AI" in app_record.cover_letter
    assert app_record.candidate_profile["full_name"] == "Irfan Rajpoot"
    assert app_record.candidate_profile["email"] == "irfanbinrajpoot@gmail.com"
    assert len(app_record.application_answers) == 8
    assert app_record.status in ("DRAFT", "REVIEW_REQUIRED")


def test_missing_information_detection(app_db):
    """2. Verify missing candidate info (like expected salary) is detected as REQUIRES_USER_INPUT."""
    job = app_db.query(Job).filter(Job.company == "Whizzbridge").first()
    app_record = ApplicationEngine.prepare_application_package(app_db, job.id)

    answers = {a["question_key"]: a for a in app_record.application_answers}
    assert answers["expected_salary"]["status"] == "REQUIRES_USER_INPUT"
    assert answers["expected_salary"]["answer_text"] is None

    # Should be flagged in validation errors
    assert any("expected_salary" in err for err in app_record.validation_errors)
    assert app_record.readiness_status == "REVIEW_REQUIRED"


def test_cover_letter_evidence_validation(app_db):
    """3. Verify cover letter uses only verified candidate facts with evidence metadata."""
    job = app_db.query(Job).filter(Job.company == "Whizzbridge").first()
    app_record = ApplicationEngine.prepare_application_package(app_db, job.id)

    # Check evidence traceability map
    evidence = app_record.evidence_map
    assert len(evidence) >= 3
    for ev in evidence:
        assert ev["status"] == "SUPPORTED"
        assert ev["source"] == "Master CV"
        assert "Munshi.AI" in ev["source_item"] or "University" in ev["source_item"] or "Skills" in ev["source_item"] or "Summary" in ev["source_item"]


def test_application_field_traceability(app_db):
    """4. Verify structured application profile fields trace directly to Master CV."""
    job = app_db.query(Job).filter(Job.company == "Whizzbridge").first()
    app_record = ApplicationEngine.prepare_application_package(app_db, job.id)

    fields = app_record.application_fields
    assert fields["full_name"]["value"] == "Irfan Rajpoot"
    assert fields["full_name"]["status"] == "SUPPORTED"
    assert fields["email"]["value"] == "irfanbinrajpoot@gmail.com"
    assert fields["github"]["value"] == "https://github.com/irfanrajpoot"
    assert fields["linkedin"]["value"] == "https://linkedin.com/in/irfan-rajpoot"


def test_user_edits_stored_separately(app_db):
    """5. Verify user manual modifications are stored in user_edits without altering Master CV."""
    job = app_db.query(Job).filter(Job.company == "Whizzbridge").first()
    app_record = ApplicationEngine.prepare_application_package(app_db, job.id)

    custom_cl = "Customized opening statement written by candidate."
    custom_salary = "150,000 PKR"
    custom_notice = "2 weeks notice"

    updated = ApplicationEngine.update_user_edits(
        db=app_db,
        application_id=app_record.id,
        cover_letter=custom_cl,
        custom_answers={
            "expected_salary": custom_salary,
            "notice_period": custom_notice
        },
        notes="Candidate custom note."
    )

    assert updated.user_edits["cover_letter"] == custom_cl
    assert updated.user_edits["custom_answers"]["expected_salary"] == custom_salary
    assert updated.cover_letter == custom_cl

    answers = {a["question_key"]: a for a in updated.application_answers}
    assert answers["expected_salary"]["answer_text"] == custom_salary
    assert answers["expected_salary"]["status"] == "USER_EDITED"


def test_master_cv_immutability(app_db):
    """6. Verify Master CV remains strictly immutable across application preparation and edits."""
    cv_before = app_db.query(MasterCV).first()
    summary_before = cv_before.summary
    email_before = cv_before.email
    skills_count_before = len(cv_before.skills)

    job = app_db.query(Job).filter(Job.company == "Whizzbridge").first()
    app_record = ApplicationEngine.prepare_application_package(app_db, job.id)

    # Edit application
    ApplicationEngine.update_user_edits(
        db=app_db,
        application_id=app_record.id,
        cover_letter="Modified cover letter.",
        custom_answers={"expected_salary": "200,000 PKR"}
    )

    # Approve application
    ApplicationEngine.approve_application(app_db, app_record.id)

    cv_after = app_db.query(MasterCV).first()
    assert cv_after.summary == summary_before
    assert cv_after.email == email_before
    assert len(cv_after.skills) == skills_count_before


def test_approval_workflow_and_status_transitions(app_db):
    """7. Verify explicit approval transitions status to READY_FOR_SUBMISSION."""
    job = app_db.query(Job).filter(Job.company == "Whizzbridge").first()
    app_record = ApplicationEngine.prepare_application_package(app_db, job.id)

    assert app_record.status in ("DRAFT", "REVIEW_REQUIRED")
    assert app_record.approval_timestamp is None

    # Approve
    approved = ApplicationEngine.approve_application(
        db=app_db,
        application_id=app_record.id,
        reviewer_name="Irfan Rajpoot",
        notes="Approved for submission."
    )

    assert approved.status == "READY_FOR_SUBMISSION"
    assert approved.approval_timestamp is not None
    assert approved.review_timestamp is not None

    # Verify review record created
    reviews = app_db.query(ApplicationReview).filter(ApplicationReview.application_id == app_record.id).all()
    assert len(reviews) == 1
    assert reviews[0].decision == "APPROVED"


def test_safety_boundary_rejection_of_submitted_status():
    """8. Verify setting status to SUBMITTED directly is rejected in Phase 5."""
    from backend.app.database import SessionLocal
    db = SessionLocal()
    from backend.app.services.master_cv_service import MasterCVService
    MasterCVService.seed_candidate_profile_if_empty(db)
    job = db.query(Job).filter(Job.company == "Whizzbridge").first()
    if not job:
        job = db.query(Job).first()

    app_record = ApplicationEngine.prepare_application_package(db, job.id, force=True)

    client = TestClient(app)
    # Attempt to PATCH status directly to SUBMITTED
    resp = client.patch(
        f"/api/v1/applications/{app_record.id}",
        json={"status": "SUBMITTED"}
    )
    assert resp.status_code == 400
    assert "Cannot transition to SUBMITTED in Phase 5" in resp.json()["detail"]
    db.close()


def test_unsupported_claim_rejection_in_cover_letter(app_db):
    """9. Verify Hallucination Guard rejects unsupported seniority and certifications."""
    job = app_db.query(Job).filter(Job.company == "Whizzbridge").first()
    cv = app_db.query(MasterCV).first()
    tailored = CVTailoringEngine.tailor_cv_for_job(app_db, job.id)
    match_eval = type("MatchEval", (), {"required_skills": ["Python"], "relevant_experience": ["Munshi.AI"], "partial": [], "match_score": 85})()

    text, integrity, evidence, rejected = CoverLetterGenerator.generate_cover_letter(job, cv, tailored, match_eval)
    assert integrity == "PASS"
    assert len(rejected) == 0

    # Test rejection mechanism with fake text
    fake_cl = "I have 10+ years experience as director of engineering with AWS Certified Solutions Architect Professional."
    rejected_test = [f for f in CoverLetterGenerator.FORBIDDEN_SENIORITY_CLAIMS if f in fake_cl.lower()]
    assert len(rejected_test) >= 2


def test_readiness_validation_criteria(app_db):
    """10. Verify readiness checks flag missing required elements."""
    job = app_db.query(Job).filter(Job.company == "Whizzbridge").first()
    cv = app_db.query(MasterCV).first()

    # Missing email
    bad_profile = {"full_name": "Irfan", "email": "", "phone": "123", "location": "Lahore"}
    readiness, errors = ApplicationEngine.check_application_readiness(
        job=job,
        cv=cv,
        tailored_cv=None,
        candidate_profile=bad_profile,
        application_answers=[],
        match_score=85.0
    )
    assert readiness == "REVIEW_REQUIRED"
    assert any("email" in e.lower() for e in errors)
    assert any("tailored cv" in e.lower() for e in errors)


def test_eligibility_gate_and_manual_override(app_db):
    """11. Verify low-scoring job (<70%) requires force=True to prepare application."""
    job_low = app_db.query(Job).filter(Job.company == "Legacy Mobile Ltd").first()

    with pytest.raises(ValueError) as exc:
        ApplicationEngine.prepare_application_package(app_db, job_low.id, force=False)
    assert "below the application threshold" in str(exc.value)

    # With force=True, it succeeds
    forced_app = ApplicationEngine.prepare_application_package(app_db, job_low.id, force=True)
    assert forced_app is not None
    assert forced_app.job_id == job_low.id


def test_application_api_endpoints_end_to_end():
    """12. Verify all Phase 5 API endpoints work end-to-end via FastAPI TestClient."""
    from backend.app.database import SessionLocal
    db = SessionLocal()
    from backend.app.services.master_cv_service import MasterCVService
    MasterCVService.seed_candidate_profile_if_empty(db)
    job = db.query(Job).filter(Job.company == "Whizzbridge").first()
    if not job:
        job = db.query(Job).first()

    client = TestClient(app)

    # 1. POST /api/v1/jobs/{job_id}/prepare-application
    post_resp = client.post(f"/api/v1/jobs/{job.id}/prepare-application", json={"force": True})
    assert post_resp.status_code in (200, 201)
    app_data = post_resp.json()
    app_id = app_data["id"]
    assert app_data["job_id"] == job.id
    assert app_data["cover_letter"] is not None
    assert "candidate_profile" in app_data

    # 2. GET /api/v1/jobs/{job_id}/application
    job_app_resp = client.get(f"/api/v1/jobs/{job.id}/application")
    assert job_app_resp.status_code == 200
    assert job_app_resp.json()["id"] == app_id

    # 3. GET /api/v1/applications
    list_resp = client.get("/api/v1/applications")
    assert list_resp.status_code == 200
    assert len(list_resp.json()) >= 1

    # 4. GET /api/v1/applications/{id}
    detail_resp = client.get(f"/api/v1/applications/{app_id}")
    assert detail_resp.status_code == 200
    assert detail_resp.json()["id"] == app_id

    # 5. PATCH /api/v1/applications/{id}
    patch_resp = client.patch(
        f"/api/v1/applications/{app_id}",
        json={
            "cover_letter": "Updated cover letter text from candidate.",
            "custom_answers": {"expected_salary": "180,000 PKR"},
            "notes": "Reviewed by user."
        }
    )
    assert patch_resp.status_code == 200
    assert patch_resp.json()["cover_letter"] == "Updated cover letter text from candidate."

    # 6. POST /api/v1/applications/{id}/review
    rev_resp = client.post(
        f"/api/v1/applications/{app_id}/review",
        json={"notes": "Looked over all details."}
    )
    assert rev_resp.status_code == 200

    # 7. POST /api/v1/applications/{id}/approve
    approve_resp = client.post(
        f"/api/v1/applications/{app_id}/approve",
        json={"notes": "Confirmed and ready for submission."}
    )
    assert approve_resp.status_code == 200
    assert approve_resp.json()["status"] == "READY_FOR_SUBMISSION"
    assert approve_resp.json()["approval_timestamp"] is not None

    # 8. GET /api/v1/applications/{id}/cover-letter
    cl_resp = client.get(f"/api/v1/applications/{app_id}/cover-letter")
    assert cl_resp.status_code == 200
    assert cl_resp.json()["application_id"] == app_id
    assert cl_resp.json()["integrity_status"] == "PASS"

    db.close()
