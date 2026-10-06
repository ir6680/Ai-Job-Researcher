"""
Unit tests for CV Parser Service.
Ensures zero invention of data and accurate extraction of factual fields.
"""

import pytest
from backend.app.services.cv_parser_service import CVParserService


def test_cv_parser_never_invents_missing_data():
    sample_text = """
    Ahmad Khan
    ahmad.khan@example.com
    +92 300 1234567
    
    Education:
    FAST NUCES Lahore
    BS Computer Science (2020 - 2024)
    CGPA: 3.45

    Technical Skills:
    Python, FastAPI, PostgreSQL, Docker, Git, React
    """

    parsed = CVParserService.parse(sample_text, "ahmad_cv.pdf")

    # Verified facts
    assert parsed.full_name == "Ahmad Khan"
    assert parsed.email == "ahmad.khan@example.com"
    assert parsed.phone == "+92 300 1234567"
    assert "Lahore" in parsed.location

    # No certifications were mentioned in text, so certifications list MUST be empty
    assert len(parsed.certifications) == 0

    # No github link was provided in text, so github_url MUST be None
    assert parsed.github_url is None

    # Extracted skills must include the genuine mentions
    skill_names = [s.name.lower() for s in parsed.skills]
    assert "python" in skill_names
    assert "fastapi" in skill_names
    assert "postgresql" in skill_names
    assert "docker" in skill_names


def test_pakistani_phone_extraction():
    text1 = "Contact me at +92-321-7654321 for queries."
    text2 = "Call 03001234567 anytime."
    
    assert CVParserService.extract_phone(text1) is not None
    assert CVParserService.extract_phone(text2) is not None


def test_github_and_linkedin_links():
    text = """
    LinkedIn: https://linkedin.com/in/irfan-rajpoot
    GitHub: https://github.com/irfanrajpoot
    Portfolio: https://irfanrajpoot.dev
    """
    links = CVParserService.extract_links(text)
    assert links["linkedin_url"] == "https://linkedin.com/in/irfan-rajpoot"
    assert links["github_url"] == "https://github.com/irfanrajpoot"
    assert links["portfolio_url"] == "https://irfanrajpoot.dev"
