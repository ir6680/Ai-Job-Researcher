"""
Tests for Job model and schema integrity.
"""

from backend.app.schemas import JobCreate, JobResponse


def test_job_create_schema_validation():
    data = {
        "company": "Systems Limited",
        "job_title": "Associate Python Engineer",
        "location": "Lahore, Pakistan",
        "description": "Looking for entry-level python developer with strong OOP and SQL.",
        "required_skills": ["Python", "SQL", "Git"],
        "preferred_skills": ["FastAPI", "Docker"],
        "salary": "PKR 120,000 / month",
        "source": "Careers Portal"
    }

    job_in = JobCreate(**data)
    assert job_in.company == "Systems Limited"
    assert "Python" in job_in.required_skills
    assert job_in.location == "Lahore, Pakistan"
