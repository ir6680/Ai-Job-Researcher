"""
Database connection, session management, and Base model definition.
Supports PostgreSQL (production/docker) and SQLite (quick local tests).
"""

from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from backend.app.config import settings
from backend.app.utils.logger import get_logger

logger = get_logger(__name__)

# Normalize sqlite URL if relative
db_url = settings.DATABASE_URL
connect_args = {}
if db_url.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

try:
    engine = create_engine(
        db_url,
        connect_args=connect_args,
        pool_pre_ping=True,
        echo=False
    )
    # Validate connection immediately
    with engine.connect() as conn:
        pass
    logger.info(f"Connected to database successfully using: {db_url}")
except Exception as e:
    logger.warning(f"Failed to connect with {db_url}: {e}. Falling back to SQLite.")
    engine = create_engine(
        "sqlite:///./job_agent.db",
        connect_args={"check_same_thread": False},
        echo=False
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency to yield database session per request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def run_migrations():
    """Migrate database schema for Phase 4 fields if missing."""
    from sqlalchemy import inspect, text
    try:
        inspector = inspect(engine)
        if "tailored_cvs" in inspector.get_table_names():
            columns = [c["name"] for c in inspector.get_columns("tailored_cvs")]
            new_cols = [
                ("match_result_id", "VARCHAR(100)"),
                ("target_company", "VARCHAR(255)"),
                ("target_role", "VARCHAR(255)"),
                ("ats_keyword_coverage", "FLOAT"),
                ("integrity_status", "VARCHAR(50) DEFAULT 'PASS'"),
                ("human_reviewed", "BOOLEAN DEFAULT 0"),
                ("structured_content", "JSON"),
                ("tailoring_changes", "JSON"),
                ("evidence_map", "JSON"),
                ("rejected_claims", "JSON"),
                ("matched_keywords", "JSON"),
                ("missing_keywords", "JSON"),
                ("docx_path", "VARCHAR(500)"),
                ("pdf_path", "VARCHAR(500)"),
                ("cache_hash", "VARCHAR(64)"),
                ("generated_at", "DATETIME"),
            ]
            with engine.begin() as conn:
                for col_name, col_type in new_cols:
                    if col_name not in columns:
                        try:
                            conn.execute(text(f"ALTER TABLE tailored_cvs ADD COLUMN {col_name} {col_type}"))
                            logger.info(f"Migrated column {col_name} into tailored_cvs.")
                        except Exception as e:
                            logger.debug(f"Column {col_name} migration error or already added: {e}")

        # Phase 5: Applications table schema migration
        if "applications" in inspector.get_table_names():
            app_columns = [c["name"] for c in inspector.get_columns("applications")]
            app_new_cols = [
                ("match_result_id", "VARCHAR(100)"),
                ("readiness_status", "VARCHAR(50) DEFAULT 'REVIEW_REQUIRED'"),
                ("cover_letter", "TEXT"),
                ("candidate_profile", "JSON"),
                ("application_fields", "JSON"),
                ("application_answers", "JSON"),
                ("application_package", "JSON"),
                ("user_edits", "JSON"),
                ("validation_errors", "JSON"),
                ("evidence_map", "JSON"),
                ("review_timestamp", "DATETIME"),
                ("approval_timestamp", "DATETIME"),
                # Phase 6 Browser Agent columns
                ("browser_state", "JSON"),
                ("submission_lock", "BOOLEAN DEFAULT 0"),
                ("submission_token", "VARCHAR(100)"),
                ("submission_attempt_id", "VARCHAR(100)"),
                ("confirmation_message", "TEXT"),
                ("confirmation_reference", "VARCHAR(255)"),
                ("submission_url", "VARCHAR(500)"),
            ]
            with engine.begin() as conn:
                for col_name, col_type in app_new_cols:
                    if col_name not in app_columns:
                        try:
                            conn.execute(text(f"ALTER TABLE applications ADD COLUMN {col_name} {col_type}"))
                            logger.info(f"Migrated column {col_name} into applications.")
                        except Exception as e:
                            logger.debug(f"Column {col_name} migration error: {e}")

        # Ensure all tables (including submission_audit_logs) are created
        Base.metadata.create_all(bind=engine)
    except Exception as e:
        logger.warning(f"Error during run_migrations: {e}")


def init_db():
    """Create all tables in the database and run schema migrations."""
    try:
        Base.metadata.create_all(bind=engine)
        run_migrations()
        logger.info("Database tables and migrations verified successfully.")
    except Exception as e:
        logger.error(f"Error initializing database tables: {e}")
        raise e
