"""
Unit tests for Phase 3: Candidate-Job Matching & Fit Evaluation Engine.
Verifies:
- Match Score calculation
- Required Skills matched (✓)
- Relevant Experience matched (✓)
- Partial skill/technology alignment (△)
- Missing requirements identified (✗)
- Recommendation level determination
- Deterministic formatted report output
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.app.database import Base
from backend.app.models import Job, MasterCV, Skill, Experience, Project, User
from backend.app.services.matching_service import JobMatchingService


@pytest.fixture
def match_db():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    TestingSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = TestingSession()
    yield db
    db.close()


def test_ai_application_engineer_matching(match_db):
    # 1. Setup User and Master CV
    user = User(email="irfanbinrajpoot@gmail.com", full_name="Irfan Rajpoot")
    match_db.add(user)
    match_db.flush()

    cv = MasterCV(
        user_id=user.id,
        full_name="Irfan Rajpoot",
        email="irfanbinrajpoot@gmail.com",
        location="Lahore, Pakistan",
        summary="AI & Software Engineer specialized in Python and machine learning.",
        is_primary=True
    )
    match_db.add(cv)
    match_db.flush()

    # Add Skills
    for s_name in ["Python", "REST APIs", "AI/ML", "Git", "FastAPI"]:
        match_db.add(Skill(master_cv_id=cv.id, name=s_name))

    # Add Experience: Munshi.AI
    match_db.add(Experience(
        master_cv_id=cv.id,
        company_name="Munshi.AI",
        role_title="AI/ML Engineer",
        description="Developed agentic workflows and Python REST services."
    ))

    # Add Project: AI/ML FYP
    match_db.add(Project(
        master_cv_id=cv.id,
        title="AI/ML FYP",
        description="Final Year Project on autonomous agents."
    ))

    # 2. Setup Whizzbridge Job
    job = Job(
        company="Whizzbridge",
        job_title="AI Application Engineer (Agentic Systems)",
        location="Lahore, Pakistan",
        source="Whizzbridge Careers",
        source_url="https://www.whizzbridge.com/career/ai-application-engineer-agentic-systems",
        description="Build agentic systems and RAG workflows using Python and machine learning.",
        required_skills=["Python", "AI/ML", "REST APIs", "Git", "RAG", "Agentic Systems"]
    )
    match_db.add(job)
    match_db.commit()

    # 3. Evaluate Match
    evaluation = JobMatchingService.evaluate_match(job=job, cv=cv, db=match_db)

    # 4. Assertions
    assert evaluation.match_score == 87
    assert evaluation.recommendation == "STRONG MATCH"

    # Required Skills (✓)
    assert "Python" in evaluation.required_skills
    assert "REST APIs" in evaluation.required_skills
    assert "AI/ML" in evaluation.required_skills
    assert "Git" in evaluation.required_skills

    # Relevant Experience (✓)
    assert "Munshi.AI" in evaluation.relevant_experience
    assert "AI/ML FYP" in evaluation.relevant_experience

    # Partial (△)
    assert "RAG" in evaluation.partial
    assert "Agentic Systems" in evaluation.partial

    # Missing (✗)
    assert any("rag" in m.lower() for m in evaluation.missing)

    # Formatted Report
    report = evaluation.formatted_report
    assert "Match Score: 87%" in report
    assert "✓ Python" in report
    assert "✓ Munshi.AI" in report
    assert "△ RAG" in report
    assert "Recommendation:\nSTRONG MATCH" in report
