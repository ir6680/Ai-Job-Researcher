"""
Comprehensive Unit & Integration Test Suite for Phase 4:
Evidence-Grounded Job-Specific CV Tailoring Engine.

Covers:
1. Master CV immutability
2. Strong skills prioritized
3. Missing skills not inserted
4. Relevant projects reordered
5. Unsupported experience rejected
6. Summary contains only supported facts
7. ATS keyword classification works
8. Evidence traceability works
9. Integrity guard catches hallucinations
10. Versioning works
11. Caching works
12. DOCX generation works
13. PDF generation works
14. Application threshold eligibility gate
15. API endpoints work
"""

import os
import pytest
from datetime import datetime
from docx import Document
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.app.database import Base
from backend.app.main import app
from backend.app.models import User, MasterCV, Skill, Experience, Project, Education, Job, TailoredCV
from backend.app.services.tailoring.tailoring_engine import CVTailoringEngine
from backend.app.services.tailoring.document_generator import generate_docx_cv, generate_pdf_cv
from backend.app.services.matching_service import JobMatchingService


@pytest.fixture
def tailoring_db():
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
        summary="AI and Backend Software Engineer based in Lahore with expertise in Python, FastAPI, and machine learning architectures.",
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
            "Designed and consumed high-throughput FastAPI endpoints.",
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

    # Target Job 1: AI Application Engineer at Whizzbridge (Match >= 70)
    job_ai = Job(
        company="Whizzbridge",
        job_title="AI Application Engineer (Agentic Systems)",
        location="Lahore, Pakistan",
        source="Whizzbridge Careers",
        source_url="https://www.whizzbridge.com/career/ai-application-engineer-agentic-systems",
        description="Seeking an AI Application Engineer to build agentic systems, Python services, and RAG pipelines.",
        required_skills=["Python", "REST APIs", "AI/ML", "Git", "RAG", "Agentic Systems", "Docker", "AWS"],
        dedup_hash="whizzbridge_agentic_ai_hash_1"
    )
    db.add(job_ai)

    # Target Job 2: Senior iOS Architect (Match < 70)
    job_senior = Job(
        company="Legacy Mobile Ltd",
        job_title="Senior iOS Architect",
        location="Karachi, Pakistan",
        source="External",
        description="Requires 10+ years Swift, Objective-C, and mobile architecture experience.",
        required_skills=["Swift", "Objective-C", "iOS Architecture", "CoreData", "Metal"],
        dedup_hash="senior_ios_architect_hash_2"
    )
    db.add(job_senior)

    db.commit()
    yield db
    db.close()


def test_master_cv_immutability(tailoring_db):
    """1. Verify Master CV is completely unchanged after tailoring."""
    cv_before = tailoring_db.query(MasterCV).first()
    summary_before = cv_before.summary
    version_before = cv_before.version
    skills_count_before = len(cv_before.skills)

    job = tailoring_db.query(Job).filter(Job.company == "Whizzbridge").first()
    CVTailoringEngine.tailor_cv_for_job(tailoring_db, job.id)

    cv_after = tailoring_db.query(MasterCV).first()
    assert cv_after.summary == summary_before
    assert cv_after.version == version_before
    assert len(cv_after.skills) == skills_count_before


def test_strong_skills_prioritized(tailoring_db):
    """2. Verify required match skills (Python, REST APIs, Git, AI/ML) appear first."""
    job = tailoring_db.query(Job).filter(Job.company == "Whizzbridge").first()
    tailored = CVTailoringEngine.tailor_cv_for_job(tailoring_db, job.id)

    prioritized = tailored.structured_content["prioritized_skills"]
    assert "Python" in prioritized[:4]
    assert "REST APIs" in prioritized[:4]
    assert "AI/ML" in prioritized[:4]


def test_missing_skills_not_inserted(tailoring_db):
    """3. Verify missing JD skills (e.g. AWS, Docker) are NOT inserted into the tailored CV."""
    job = tailoring_db.query(Job).filter(Job.company == "Whizzbridge").first()
    tailored = CVTailoringEngine.tailor_cv_for_job(tailoring_db, job.id)

    prioritized = tailored.structured_content["prioritized_skills"]
    # Neither AWS nor Docker was in candidate Master CV skills
    assert "AWS" not in prioritized
    assert "Docker" not in prioritized


def test_relevant_projects_reordered(tailoring_db):
    """4. Verify AI project (AI/ML FYP) is prioritized over unrelated projects."""
    job = tailoring_db.query(Job).filter(Job.company == "Whizzbridge").first()
    tailored = CVTailoringEngine.tailor_cv_for_job(tailoring_db, job.id)

    projects = tailored.structured_content["projects"]
    assert len(projects) >= 2
    # AI/ML FYP has highest relevance to AI Application Engineer
    assert projects[0]["title"] == "AI/ML FYP"


def test_unsupported_experience_rejected(tailoring_db):
    """5. Verify unsupported experience or seniority claims are caught by integrity guard."""
    cv = tailoring_db.query(MasterCV).first()
    fake_content = {
        "summary": "10+ years experience as director of engineering with AWS Certified Solutions Architect Professional"
    }
    status, rejected = CVTailoringEngine.run_hallucination_guard(cv, fake_content)
    assert status == "REVIEW_REQUIRED"
    assert len(rejected) >= 2


def test_summary_contains_only_supported_facts(tailoring_db):
    """6. Verify summary contains only verified facts from Master CV."""
    job = tailoring_db.query(Job).filter(Job.company == "Whizzbridge").first()
    tailored = CVTailoringEngine.tailor_cv_for_job(tailoring_db, job.id)

    summary = tailored.structured_content["summary"]
    assert "Munshi.AI" in summary
    assert "Whizzbridge" in summary
    assert "Expert" not in summary
    assert "10+" not in summary


def test_ats_keyword_classification(tailoring_db):
    """7. Verify ATS keyword classification (SUPPORTED, PARTIALLY_SUPPORTED, UNSUPPORTED)."""
    cv = tailoring_db.query(MasterCV).first()
    job = tailoring_db.query(Job).filter(Job.company == "Whizzbridge").first()
    keywords = ["Python", "RAG", "Kubernetes"]

    classified, before, after = CVTailoringEngine.classify_ats_keywords(keywords, cv)
    status_map = {c["keyword"]: c["status"] for c in classified}

    assert status_map["Python"] == "SUPPORTED"
    assert status_map["RAG"] == "SUPPORTED" or status_map["RAG"] == "PARTIALLY_SUPPORTED"
    assert status_map["Kubernetes"] == "UNSUPPORTED"
    assert after >= before


def test_evidence_traceability_works(tailoring_db):
    """8. Verify every tailored statement links to Master CV source and reason."""
    job = tailoring_db.query(Job).filter(Job.company == "Whizzbridge").first()
    tailored = CVTailoringEngine.tailor_cv_for_job(tailoring_db, job.id)

    evidence = tailored.evidence_map
    assert len(evidence) >= 3
    for item in evidence:
        assert "generated_text" in item
        assert "source_section" in item
        assert "source_item" in item
        assert "source_text" in item
        assert "reason" in item


def test_integrity_guard_catches_hallucinations(tailoring_db):
    """9. Verify integrity guard marks status PASS for grounded content."""
    job = tailoring_db.query(Job).filter(Job.company == "Whizzbridge").first()
    tailored = CVTailoringEngine.tailor_cv_for_job(tailoring_db, job.id)
    assert tailored.integrity_status == "PASS"
    assert len(tailored.rejected_claims) == 0


def test_versioning_increments_per_job(tailoring_db):
    """10. Verify versioning increments on fresh generation (v1 -> v2)."""
    job = tailoring_db.query(Job).filter(Job.company == "Whizzbridge").first()
    v1 = CVTailoringEngine.tailor_cv_for_job(tailoring_db, job.id, force_regenerate=True)
    v2 = CVTailoringEngine.tailor_cv_for_job(tailoring_db, job.id, force_regenerate=True)

    assert v1.version == 1
    assert v2.version == 2
    assert v2.id != v1.id


def test_caching_returns_existing_without_regeneration(tailoring_db):
    """11. Verify caching returns existing record when fingerprint is identical."""
    job = tailoring_db.query(Job).filter(Job.company == "Whizzbridge").first()
    t1 = CVTailoringEngine.tailor_cv_for_job(tailoring_db, job.id, force_regenerate=False)
    t2 = CVTailoringEngine.tailor_cv_for_job(tailoring_db, job.id, force_regenerate=False)

    assert t1.id == t2.id
    assert t1.version == t2.version


def test_docx_generation_produces_valid_file(tailoring_db, tmp_path):
    """12. Verify DOCX document generator creates valid .docx readable by python-docx."""
    output_docx = str(tmp_path / "test_cv.docx")
    data = {
        "full_name": "Irfan Rajpoot",
        "location": "Lahore, Pakistan",
        "email": "irfanbinrajpoot@gmail.com",
        "summary": "AI Engineer in Lahore.",
        "skills_by_category": {"Languages": ["Python", "SQL"]},
        "projects": [{"title": "Munshi.AI", "technologies": ["Python"], "highlights": ["Built backend"]}]
    }
    path = generate_docx_cv(data, output_docx)
    assert os.path.exists(path)
    assert os.path.getsize(path) > 1000

    doc = Document(path)
    text = " ".join(p.text for p in doc.paragraphs)
    assert "IRFAN RAJPOOT" in text
    assert "Munshi.AI" in text


def test_pdf_generation_produces_valid_file(tailoring_db, tmp_path):
    """13. Verify PDF document generator creates valid .pdf file with content."""
    output_pdf = str(tmp_path / "test_cv.pdf")
    data = {
        "full_name": "Irfan Rajpoot",
        "location": "Lahore, Pakistan",
        "email": "irfanbinrajpoot@gmail.com",
        "summary": "AI Engineer in Lahore.",
        "skills_by_category": {"Languages": ["Python", "SQL"]},
        "projects": [{"title": "Munshi.AI", "technologies": ["Python"], "highlights": ["Built backend"]}]
    }
    path = generate_pdf_cv(data, output_pdf)
    assert os.path.exists(path)
    assert os.path.getsize(path) > 1000


def test_application_threshold_eligibility_gate(tailoring_db):
    """14. Verify jobs with match score < 70 fail unless force=True."""
    job_senior = tailoring_db.query(Job).filter(Job.company == "Legacy Mobile Ltd").first()

    with pytest.raises(ValueError) as exc:
        CVTailoringEngine.tailor_cv_for_job(tailoring_db, job_senior.id, force=False)
    assert "below the application threshold" in str(exc.value)

    # With force=True, it succeeds
    forced_cv = CVTailoringEngine.tailor_cv_for_job(tailoring_db, job_senior.id, force=True)
    assert forced_cv is not None
    assert forced_cv.target_company == "Legacy Mobile Ltd"


def test_tailoring_api_endpoints():
    """15. Test all tailoring API endpoints end-to-end via FastAPI TestClient."""
    from backend.app.database import SessionLocal
    db = SessionLocal()
    from backend.app.services.master_cv_service import MasterCVService
    MasterCVService.seed_candidate_profile_if_empty(db)
    job = db.query(Job).filter(Job.company == "Whizzbridge").first()
    if not job:
        job = db.query(Job).first()

    client = TestClient(app)

    # 1. POST /jobs/{id}/tailor-cv
    post_resp = client.post(f"/api/v1/jobs/{job.id}/tailor-cv", json={"force": True})
    assert post_resp.status_code in (200, 201)
    tailored_data = post_resp.json()
    cv_id = tailored_data["id"]
    assert tailored_data["match_score"] >= 70
    assert tailored_data["integrity_status"] == "PASS"

    # 2. GET /jobs/{id}/tailored-cvs
    list_resp = client.get(f"/api/v1/jobs/{job.id}/tailored-cvs")
    assert list_resp.status_code == 200
    assert len(list_resp.json()) >= 1

    # 3. GET /tailored-cvs/{id}
    get_resp = client.get(f"/api/v1/tailored-cvs/{cv_id}")
    assert get_resp.status_code == 200
    assert get_resp.json()["id"] == cv_id

    # 4. GET /tailored-cvs/{id}/evidence
    ev_resp = client.get(f"/api/v1/tailored-cvs/{cv_id}/evidence")
    assert ev_resp.status_code == 200
    assert isinstance(ev_resp.json(), list)

    # 5. POST /tailored-cvs/{id}/review
    rev_resp = client.post(f"/api/v1/tailored-cvs/{cv_id}/review")
    assert rev_resp.status_code == 200
    assert rev_resp.json()["human_reviewed"] is True

    # 6. GET /tailored-cvs/{id}/download/docx
    docx_resp = client.get(f"/api/v1/tailored-cvs/{cv_id}/download/docx")
    assert docx_resp.status_code == 200
    assert "application/vnd.openxmlformats" in docx_resp.headers["content-type"]

    # 7. GET /tailored-cvs/{id}/download/pdf
    pdf_resp = client.get(f"/api/v1/tailored-cvs/{cv_id}/download/pdf")
    assert pdf_resp.status_code == 200
    assert "application/pdf" in pdf_resp.headers["content-type"]
