"""
Job and Application Service.
Handles job storage, query filtering, seeding Lahore software house opportunities,
and application status lifecycle.
"""

from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc, or_
from backend.app.models import Job, Application, MasterCV, User
from backend.app.schemas import JobCreate, JobUpdate, ApplicationCreate, ApplicationUpdate
from backend.app.utils.logger import get_logger

logger = get_logger(__name__)


# Curated starter jobs for Lahore software houses (Entry-Level / Intern)
LAHORE_STARTER_JOBS = [
    {
        "company": "Systems Limited",
        "job_title": "Associate Software Engineer - Python / Backend",
        "location": "Lahore (DHA Phase 8 & Central)",
        "job_url": "https://www.systemsltd.com/careers",
        "description": "Looking for fresh graduates with strong foundations in Python, data structures, algorithms, and relational databases. You will work on enterprise cloud solutions, microservices, and high-performance APIs.",
        "required_skills": ["Python", "FastAPI", "SQL", "Git", "OOP", "Data Structures"],
        "preferred_skills": ["Docker", "PostgreSQL", "Redis", "Unit Testing"],
        "experience_requirement": "Fresh Graduate (0-1 years)",
        "education_requirement": "BS in Computer Science / Software Engineering",
        "job_type": "Full-time / On-site",
        "salary": "PKR 100,000 - 140,000 / month",
        "source": "Systems Careers Portal",
        "status": "saved"
    },
    {
        "company": "Arbisoft",
        "job_title": "Junior Software Engineer (Fresh Graduates Batch)",
        "location": "Lahore (Canal Road, Thokar)",
        "job_url": "https://arbisoft.com/careers",
        "description": "Join Arbisoft's renowned engineering batch. We look for passionate coders who excel in algorithmic thinking, clean code architecture, Python/Django, and web systems.",
        "required_skills": ["Python", "Django", "PostgreSQL", "REST APIs", "Git"],
        "preferred_skills": ["React", "TypeScript", "AWS", "Celery"],
        "experience_requirement": "0-1 years (Entry-Level)",
        "education_requirement": "Bachelor's in Computer Science",
        "job_type": "Full-time / Hybrid",
        "salary": "PKR 110,000 - 150,000 / month",
        "source": "Arbisoft Careers",
        "status": "saved"
    },
    {
        "company": "Devsinc",
        "job_title": "Junior Full Stack Developer",
        "location": "Lahore (Johar Town & Gulberg)",
        "job_url": "https://www.devsinc.com/careers",
        "description": "Devsinc is hiring driven junior developers passionate about modern web stacks (Python/Node backend + React frontend). Rapid learning environment with mentorship from senior architects.",
        "required_skills": ["JavaScript", "Python", "React", "PostgreSQL", "HTML/CSS"],
        "preferred_skills": ["FastAPI", "Tailwind CSS", "Docker"],
        "experience_requirement": "0-1 years",
        "education_requirement": "BS Computer Science",
        "job_type": "Full-time",
        "salary": "PKR 90,000 - 130,000 / month",
        "source": "LinkedIn",
        "status": "saved"
    },
    {
        "company": "Tintash",
        "job_title": "Software Engineer Trainee - Web & AI",
        "location": "Lahore (Cantt / DHA)",
        "job_url": "https://tintash.com/careers",
        "description": "Opportunity to work with international startups building web and AI products. Focus on clean code, test-driven development, and scalable APIs.",
        "required_skills": ["Python", "FastAPI", "PostgreSQL", "Problem Solving"],
        "preferred_skills": ["AI/ML Basics", "Docker", "Git"],
        "experience_requirement": "Fresh Graduate",
        "education_requirement": "BSCS / BSSE",
        "job_type": "Full-time",
        "salary": "PKR 95,000 - 135,000 / month",
        "source": "Tintash Portal",
        "status": "saved"
    },
    {
        "company": "10Pearls",
        "job_title": "Associate Software Engineer - Backend",
        "location": "Lahore (Gulberg III)",
        "job_url": "https://10pearls.com/careers",
        "description": "Work on scalable cloud backend services. Candidates should possess solid object-oriented concepts, database design skills, and eagerness to build modern distributed systems.",
        "required_skills": ["Python", "FastAPI", "SQL", "Git"],
        "preferred_skills": ["PostgreSQL", "Docker", "CI/CD"],
        "experience_requirement": "0-1 years",
        "education_requirement": "BS Computer Science",
        "job_type": "Full-time / Hybrid",
        "salary": "PKR 100,000 - 140,000 / month",
        "source": "10Pearls Portal",
        "status": "saved"
    },
    {
        "company": "Netsol Technologies",
        "job_title": "Graduate Trainee Engineer",
        "location": "Lahore (NetSol Avenue, Ring Road)",
        "job_url": "https://netsoltech.com/careers",
        "description": "Global enterprise fintech software leader hiring fresh talent for asset finance and leasing platforms.",
        "required_skills": ["OOP", "Data Structures", "SQL", "Python or Java"],
        "preferred_skills": ["Agile", "Linux", "Relational DBs"],
        "experience_requirement": "Entry-Level (0 years)",
        "education_requirement": "Bachelor's in Computing",
        "job_type": "Full-time",
        "salary": "PKR 85,000 - 120,000 / month",
        "source": "Netsol Careers",
        "status": "saved"
    }
]


class JobService:

    @classmethod
    def seed_starter_jobs_if_empty(cls, db: Session) -> int:
        """Seed initial entry-level Lahore jobs if none exist."""
        existing_count = db.query(Job).count()
        if existing_count > 0:
            return 0

        created = 0
        for item in LAHORE_STARTER_JOBS:
            job = Job(**item)
            db.add(job)
            created += 1

        db.commit()
        logger.info(f"Seeded {created} curated Lahore software house jobs.")
        return created

    @staticmethod
    def get_jobs(
        db: Session,
        skip: int = 0,
        limit: int = 50,
        search: Optional[str] = None,
        company: Optional[str] = None,
        status: Optional[str] = None
    ) -> list[Job]:
        query = db.query(Job)
        if search:
            query = query.filter(
                or_(
                    Job.job_title.ilike(f"%{search}%"),
                    Job.company.ilike(f"%{search}%"),
                    Job.description.ilike(f"%{search}%")
                )
            )
        if company:
            query = query.filter(Job.company.ilike(f"%{company}%"))
        if status:
            query = query.filter(Job.status == status)

        return query.order_by(desc(Job.created_at)).offset(skip).limit(limit).all()

    @staticmethod
    def get_job_by_id(db: Session, job_id: str) -> Optional[Job]:
        return db.query(Job).filter(Job.id == job_id).first()

    @staticmethod
    def create_job(db: Session, data: JobCreate) -> Job:
        job = Job(**data.model_dump())
        db.add(job)
        db.commit()
        db.refresh(job)
        return job

    @staticmethod
    def update_job(db: Session, job_id: str, data: JobUpdate) -> Optional[Job]:
        job = db.query(Job).filter(Job.id == job_id).first()
        if not job:
            return None
        for key, val in data.model_dump(exclude_unset=True).items():
            setattr(job, key, val)
        db.commit()
        db.refresh(job)
        return job

    @staticmethod
    def delete_job(db: Session, job_id: str) -> bool:
        job = db.query(Job).filter(Job.id == job_id).first()
        if not job:
            return False
        db.delete(job)
        db.commit()
        return True


class ApplicationService:

    @staticmethod
    def list_applications(db: Session, status: Optional[str] = None) -> list[Application]:
        query = db.query(Application)
        if status:
            query = query.filter(Application.status == status)
        return query.order_by(desc(Application.updated_at)).all()

    @staticmethod
    def create_application(db: Session, data: ApplicationCreate) -> Application:
        # Resolve user
        user = db.query(User).first()
        user_id = data.user_id or (user.id if user else None)
        if not user_id:
            user = User(email="applicant@lahore-jobs.pk", full_name="Candidate")
            db.add(user)
            db.flush()
            user_id = user.id

        # Resolve master cv if not provided
        master_cv_id = data.master_cv_id
        if not master_cv_id:
            mcv = db.query(MasterCV).first()
            if mcv:
                master_cv_id = mcv.id

        app = Application(
            user_id=user_id,
            job_id=data.job_id,
            master_cv_id=master_cv_id,
            tailored_cv_id=data.tailored_cv_id,
            status=data.status or "draft",
            notes=data.notes,
            applied_at=data.applied_at
        )
        db.add(app)
        db.commit()
        db.refresh(app)
        return app

    @staticmethod
    def update_application(db: Session, app_id: str, data: ApplicationUpdate) -> Optional[Application]:
        app = db.query(Application).filter(Application.id == app_id).first()
        if not app:
            return None
        for key, val in data.model_dump(exclude_unset=True).items():
            setattr(app, key, val)
        db.commit()
        db.refresh(app)
        return app
