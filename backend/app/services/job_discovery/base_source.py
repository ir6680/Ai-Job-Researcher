"""
Job Discovery Base Source Interface and Data Structures.
Modular design allowing seamless addition of new company career portals and job boards.
"""

from abc import ABC, abstractmethod
from typing import Optional, List
from pydantic import BaseModel, Field


class RawDiscoveredJob(BaseModel):
    """Normalized payload extracted by any modular job source before validation."""
    company: str
    job_title: str
    location: str = "Lahore, Pakistan"
    description: str
    raw_description: Optional[str] = None
    responsibilities: List[str] = Field(default_factory=list)
    required_skills: List[str] = Field(default_factory=list)
    preferred_skills: List[str] = Field(default_factory=list)
    experience_requirement: str = "Entry-level (0-1 years)"
    education_requirement: str = "BS Computer Science / Software Engineering or equivalent"
    job_type: str = "Full-time"
    salary: Optional[str] = None
    source: str
    source_url: str
    job_url: Optional[str] = None
    posting_date: Optional[str] = None
    deadline: Optional[str] = None


class BaseJobSource(ABC):
    """Abstract Base Class for all modular job discovery sources."""

    source_id: str
    source_name: str
    source_type: str  # 'company_careers', 'job_board', 'search_engine'
    base_url: str
    description: str
    is_active: bool = True

    @abstractmethod
    async def discover_jobs(
        self,
        keywords: List[str],
        target_city: str = "Lahore",
        limit: int = 20
    ) -> List[RawDiscoveredJob]:
        """
        Query and extract jobs from this source.
        Must handle errors gracefully and never crash the caller.
        """
        pass
