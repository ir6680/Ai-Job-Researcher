"""
Master CV Business Logic Service.
Handles persistence, versioning, and child record management for Master CV.
"""

from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc
from backend.app.models import (
    User,
    MasterCV,
    Skill,
    Education,
    Experience,
    Project,
    Certification
)
from backend.app.schemas import (
    MasterCVCreate,
    MasterCVUpdate,
    SkillCreate,
    SkillUpdate,
    EducationCreate,
    EducationUpdate,
    ExperienceCreate,
    ExperienceUpdate,
    ProjectCreate,
    ProjectUpdate,
    CertificationCreate,
    CertificationUpdate,
    ExtractedCVData
)
from backend.app.utils.logger import get_logger

logger = get_logger(__name__)


class MasterCVService:

    @staticmethod
    def get_or_create_default_user(db: Session, email: str = "applicant@lahore-jobs.pk", name: str = "Lahore Candidate") -> User:
        """Fetch primary candidate user or create a default record."""
        user = db.query(User).filter(User.email == email).first()
        if not user:
            user = User(
                email=email,
                full_name=name,
                is_active=True,
                target_city="Lahore"
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            logger.info(f"Created default user: {user.email}")
        return user

    @classmethod
    def seed_candidate_profile_if_empty(cls, db: Session) -> Optional[MasterCV]:
        """Seed Irfan Rajpoot's master candidate profile if no Master CV exists."""
        existing = cls.get_master_cv(db)
        if existing:
            return existing

        user = cls.get_or_create_default_user(db, email="irfanbinrajpoot@gmail.com", name="Irfan Rajpoot")
        cv = MasterCV(
            user_id=user.id,
            full_name="Irfan Rajpoot",
            email="irfanbinrajpoot@gmail.com",
            phone="+92 300 1234567",
            location="Lahore, Pakistan",
            summary="Passionate Software & AI Engineer based in Lahore with experience developing agentic workflows, Python REST APIs, and machine learning pipelines.",
            github_url="https://github.com/irfanrajpoot",
            linkedin_url="https://linkedin.com/in/irfan-rajpoot",
            portfolio_url="https://irfanrajpoot.dev",
            is_primary=True,
            raw_text="Irfan Rajpoot - AI Engineer in Lahore, Pakistan. Experience at Munshi.AI. Final Year Project: AI/ML FYP.",
            version=1
        )
        db.add(cv)
        db.flush()

        # Add Core Skills
        skills_data = [
            ("Python", "Languages", "Expert", 2.0),
            ("REST APIs", "Frameworks", "Expert", 2.0),
            ("AI/ML", "Technical", "Intermediate", 1.5),
            ("Git", "Tools/DevOps", "Expert", 2.0),
            ("FastAPI", "Frameworks", "Intermediate", 1.5),
            ("SQL", "Databases", "Intermediate", 1.5),
            ("PostgreSQL", "Databases", "Intermediate", 1.5),
            ("RAG", "Technical", "Beginner", 0.5),
            ("Agentic Systems", "Technical", "Beginner", 0.5),
        ]
        for name, cat, prof, yrs in skills_data:
            db.add(Skill(master_cv_id=cv.id, name=name, category=cat, proficiency=prof, years_of_experience=yrs))

        # Add Experience: Munshi.AI
        db.add(Experience(
            master_cv_id=cv.id,
            company_name="Munshi.AI",
            role_title="AI/ML Engineer",
            employment_type="Full-time",
            location="Lahore, Pakistan",
            start_date="2025-06",
            end_date=None,
            is_current=True,
            description="Developing intelligent agent workflows, Python backend microservices, and AI integrations.",
            highlights=[
                "Built resilient agentic pipelines using Python and FastAPI.",
                "Designed and consumed high-throughput REST APIs.",
                "Collaborated on experimental LLM retrieval mechanisms."
            ],
            technologies_used=["Python", "FastAPI", "AI/ML", "Git", "REST APIs"]
        ))

        # Add Project: AI/ML FYP
        db.add(Project(
            master_cv_id=cv.id,
            title="AI/ML FYP",
            description="Final Year Project exploring autonomous AI agents and machine learning architectures for enterprise automation.",
            technologies=["Python", "PyTorch", "FastAPI", "Git", "Machine Learning"],
            highlights=[
                "Implemented baseline agentic models and evaluation benchmarks.",
                "Engineered REST APIs for model inference and tracking."
            ]
        ))

        # Add Project: Backend Inventory Management System
        db.add(Project(
            master_cv_id=cv.id,
            title="Backend Inventory Management System",
            description="Relational database management and inventory tracking service developed with Python and SQL.",
            technologies=["Python", "SQL", "PostgreSQL", "FastAPI"],
            highlights=[
                "Designed normalized relational database schemas and indexed SQL queries for inventory records.",
                "Engineered RESTful endpoints for transaction tracking and inventory updates."
            ]
        ))

        # Add Education
        db.add(Education(
            master_cv_id=cv.id,
            institution="University in Lahore",
            degree="Bachelor of Science in Computer Science",
            field_of_study="Computer Science",
            start_date="2021",
            end_date="2025",
            is_current=False,
            location="Lahore, Pakistan"
        ))

        db.commit()
        db.refresh(cv)
        logger.info(f"Seeded Irfan Rajpoot candidate profile for {cv.full_name} (Munshi.AI, AI/ML FYP).")
        return cv

    @classmethod
    def get_master_cv(cls, db: Session, cv_id: Optional[str] = None) -> Optional[MasterCV]:
        """Fetch the active or specific Master CV with all relationships."""
        if cv_id:
            return db.query(MasterCV).filter(MasterCV.id == cv_id).first()
        # Default: get latest primary Master CV
        return db.query(MasterCV).order_by(desc(MasterCV.updated_at)).first()

    @classmethod
    def create_master_cv(cls, db: Session, data: MasterCVCreate) -> MasterCV:
        """Create a new Master CV and attach child items."""
        user = cls.get_or_create_default_user(db, data.email or "applicant@lahore-jobs.pk", data.full_name)

        # Mark existing CVs as non-primary if this one is primary
        if data.is_primary:
            db.query(MasterCV).filter(MasterCV.user_id == user.id).update({"is_primary": False})

        cv = MasterCV(
            user_id=user.id,
            full_name=data.full_name,
            email=data.email,
            phone=data.phone,
            location=data.location or "Lahore, Pakistan",
            summary=data.summary,
            github_url=data.github_url,
            linkedin_url=data.linkedin_url,
            portfolio_url=data.portfolio_url,
            website_url=data.website_url,
            is_primary=data.is_primary,
            raw_text=data.raw_text,
            source_filename=data.source_filename,
            version=1
        )
        db.add(cv)
        db.flush()

        # Add initial skills
        for s in data.skills:
            skill = Skill(
                master_cv_id=cv.id,
                name=s.name,
                category=s.category,
                proficiency=s.proficiency,
                years_of_experience=s.years_of_experience
            )
            db.add(skill)

        # Add initial education
        for e in data.education:
            edu = Education(
                master_cv_id=cv.id,
                institution=e.institution,
                degree=e.degree,
                field_of_study=e.field_of_study,
                start_date=e.start_date,
                end_date=e.end_date,
                is_current=e.is_current,
                grade_or_gpa=e.grade_or_gpa,
                location=e.location,
                description=e.description
            )
            db.add(edu)

        # Add initial experience
        for exp in data.experience:
            ex = Experience(
                master_cv_id=cv.id,
                company_name=exp.company_name,
                role_title=exp.role_title,
                employment_type=exp.employment_type,
                location=exp.location,
                start_date=exp.start_date,
                end_date=exp.end_date,
                is_current=exp.is_current,
                description=exp.description,
                highlights=exp.highlights,
                technologies_used=exp.technologies_used
            )
            db.add(ex)

        # Add initial projects
        for p in data.projects:
            proj = Project(
                master_cv_id=cv.id,
                title=p.title,
                description=p.description,
                role=p.role,
                technologies=p.technologies,
                repo_url=p.repo_url,
                live_url=p.live_url,
                start_date=p.start_date,
                end_date=p.end_date,
                highlights=p.highlights
            )
            db.add(proj)

        # Add initial certifications
        for c in data.certifications:
            cert = Certification(
                master_cv_id=cv.id,
                name=c.name,
                issuing_organization=c.issuing_organization,
                issue_date=c.issue_date,
                expiration_date=c.expiration_date,
                credential_id=c.credential_id,
                credential_url=c.credential_url
            )
            db.add(cert)

        db.commit()
        db.refresh(cv)
        logger.info(f"Created Master CV ID {cv.id} for {cv.full_name}")
        return cv

    @classmethod
    def save_extracted_cv(cls, db: Session, parsed: ExtractedCVData) -> MasterCV:
        """Create or update Master CV strictly from extracted CV data without hallucination."""
        # Find if existing Master CV exists
        existing_cv = cls.get_master_cv(db)

        if existing_cv:
            # Increment version and update fields if extracted
            existing_cv.version += 1
            if parsed.full_name and parsed.full_name != "Candidate":
                existing_cv.full_name = parsed.full_name
            if parsed.email:
                existing_cv.email = parsed.email
            if parsed.phone:
                existing_cv.phone = parsed.phone
            if parsed.location:
                existing_cv.location = parsed.location
            if parsed.summary:
                existing_cv.summary = parsed.summary
            if parsed.github_url:
                existing_cv.github_url = parsed.github_url
            if parsed.linkedin_url:
                existing_cv.linkedin_url = parsed.linkedin_url
            if parsed.portfolio_url:
                existing_cv.portfolio_url = parsed.portfolio_url
            existing_cv.raw_text = parsed.raw_text
            existing_cv.source_filename = parsed.filename

            # Add skills that do not already exist
            existing_skill_names = {s.name.lower() for s in existing_cv.skills}
            for s in parsed.skills:
                if s.name.lower() not in existing_skill_names:
                    db.add(Skill(
                        master_cv_id=existing_cv.id,
                        name=s.name,
                        category=s.category,
                        proficiency=s.proficiency,
                        years_of_experience=s.years_of_experience
                    ))
                    existing_skill_names.add(s.name.lower())

            # Add education if missing
            if not existing_cv.education and parsed.education:
                for e in parsed.education:
                    db.add(Education(
                        master_cv_id=existing_cv.id,
                        institution=e.institution,
                        degree=e.degree,
                        field_of_study=e.field_of_study,
                        start_date=e.start_date,
                        end_date=e.end_date,
                        is_current=e.is_current,
                        grade_or_gpa=e.grade_or_gpa,
                        location=e.location,
                        description=e.description
                    ))

            # Add experiences if missing
            if not existing_cv.experience and parsed.experience:
                for exp in parsed.experience:
                    db.add(Experience(
                        master_cv_id=existing_cv.id,
                        company_name=exp.company_name,
                        role_title=exp.role_title,
                        employment_type=exp.employment_type,
                        location=exp.location,
                        description=exp.description
                    ))

            db.commit()
            db.refresh(existing_cv)
            return existing_cv

        # Otherwise create new Master CV
        create_payload = MasterCVCreate(
            full_name=parsed.full_name or "Applicant",
            email=parsed.email or "candidate@lahore-jobs.pk",
            phone=parsed.phone,
            location=parsed.location or "Lahore, Pakistan",
            summary=parsed.summary,
            github_url=parsed.github_url,
            linkedin_url=parsed.linkedin_url,
            portfolio_url=parsed.portfolio_url,
            website_url=parsed.website_url,
            skills=parsed.skills,
            education=parsed.education,
            experience=parsed.experience,
            projects=parsed.projects,
            certifications=parsed.certifications,
            raw_text=parsed.raw_text,
            source_filename=parsed.filename
        )
        return cls.create_master_cv(db, create_payload)

    @staticmethod
    def update_master_cv(db: Session, cv_id: str, data: MasterCVUpdate) -> Optional[MasterCV]:
        cv = db.query(MasterCV).filter(MasterCV.id == cv_id).first()
        if not cv:
            return None
        
        update_dict = data.model_dump(exclude_unset=True)
        for key, val in update_dict.items():
            setattr(cv, key, val)

        cv.version += 1
        db.commit()
        db.refresh(cv)
        return cv

    # Child item management
    @staticmethod
    def add_skill(db: Session, cv_id: str, data: SkillCreate) -> Skill:
        skill = Skill(master_cv_id=cv_id, **data.model_dump())
        db.add(skill)
        db.commit()
        db.refresh(skill)
        return skill

    @staticmethod
    def delete_skill(db: Session, skill_id: str) -> bool:
        s = db.query(Skill).filter(Skill.id == skill_id).first()
        if not s:
            return False
        db.delete(s)
        db.commit()
        return True

    @staticmethod
    def add_project(db: Session, cv_id: str, data: ProjectCreate) -> Project:
        proj = Project(master_cv_id=cv_id, **data.model_dump())
        db.add(proj)
        db.commit()
        db.refresh(proj)
        return proj

    @staticmethod
    def delete_project(db: Session, project_id: str) -> bool:
        p = db.query(Project).filter(Project.id == project_id).first()
        if not p:
            return False
        db.delete(p)
        db.commit()
        return True

    @staticmethod
    def add_experience(db: Session, cv_id: str, data: ExperienceCreate) -> Experience:
        exp = Experience(master_cv_id=cv_id, **data.model_dump())
        db.add(exp)
        db.commit()
        db.refresh(exp)
        return exp

    @staticmethod
    def delete_experience(db: Session, exp_id: str) -> bool:
        e = db.query(Experience).filter(Experience.id == exp_id).first()
        if not e:
            return False
        db.delete(e)
        db.commit()
        return True

    @staticmethod
    def add_education(db: Session, cv_id: str, data: EducationCreate) -> Education:
        edu = Education(master_cv_id=cv_id, **data.model_dump())
        db.add(edu)
        db.commit()
        db.refresh(edu)
        return edu

    @staticmethod
    def delete_education(db: Session, edu_id: str) -> bool:
        ed = db.query(Education).filter(Education.id == edu_id).first()
        if not ed:
            return False
        db.delete(ed)
        db.commit()
        return True
