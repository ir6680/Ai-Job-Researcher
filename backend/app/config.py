"""
Configuration module using pydantic-settings.
Supports environment variables from .env or system environment.
"""

import os
from pathlib import Path
from typing import List, Union
from pydantic_settings import BaseSettings
from pydantic import Field, field_validator

BASE_DIR = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    APP_NAME: str = "Lahore AI Job Application Agent"
    APP_VERSION: str = "2.0.0-phase2"
    APP_ENV: str = "development"
    DEBUG: bool = True
    PORT: int = 8000
    HOST: str = "0.0.0.0"

    # Database
    DATABASE_URL: str = Field(
        default="postgresql://postgres:postgres@localhost:5432/job_agent_db",
        description="PostgreSQL connection string. Fallback to sqlite:// for quick tests."
    )

    # File uploads
    UPLOAD_DIR: str = str(BASE_DIR / "uploads")
    MAX_UPLOAD_SIZE_MB: int = 10
    ALLOWED_EXTENSIONS: list[str] = [".pdf", ".docx", ".txt"]

    # Security
    SECRET_KEY: str = "insecure-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440

    # Job target context (Phase 2 Discovery & Collection)
    TARGET_CITY: str = "Lahore"
    TARGET_COUNTRY: str = "Pakistan"
    
    # Configurable entry-level keywords for job discovery
    ENTRY_LEVEL_KEYWORDS: Union[List[str], str] = [
        "Python Developer",
        "Backend Developer",
        "Software Engineer",
        "Junior Developer",
        "AI/ML Engineer",
        "QA Engineer",
        "QA Automation Engineer",
        "Software Intern",
        "Trainee Engineer",
        "Associate Software Engineer",
        "Junior Software Engineer",
        "Full Stack Developer"
    ]

    # Enabled modular job sources
    JOB_SOURCES: Union[List[str], str] = [
        "devsinc",
        "educative",
        "netsol",
        "whizzbridge",
        "venturedive",
        "systems_limited",
        "arbisoft",
        "confiz",
        "rozee_pk",
        "search_engine",
        "tintash",
        "ten_pearls"
    ]

    MAX_JOBS_PER_RUN: int = 50
    DISCOVERY_REQUEST_TIMEOUT_SECONDS: int = 15
    DISCOVERY_USER_AGENT: str = "LahoreJobAgent/2.0 (+https://github.com/irfanrajpoot/ai-job-agent; Entry-level Research)"

    # Phase 4: CV Tailoring & Application Threshold
    APPLICATION_THRESHOLD: int = 70
    TAILORED_CV_STORAGE_DIR: str = "/app/applet/exports/tailored_cvs"

    @field_validator("ENTRY_LEVEL_KEYWORDS", "JOB_SOURCES", mode="after")
    @classmethod
    def parse_comma_separated_list(cls, value: Union[str, List[str]]) -> List[str]:
        if isinstance(value, str):
            val = value.strip()
            if val.startswith("[") and val.endswith("]"):
                try:
                    import json
                    parsed = json.loads(val)
                    if isinstance(parsed, list):
                        return [str(x).strip() for x in parsed if str(x).strip()]
                except Exception:
                    pass
            return [item.strip() for item in val.split(",") if item.strip()]
        return value

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


settings = Settings()

# Ensure uploads directory exists
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
