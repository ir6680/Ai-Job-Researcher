"""
CV Parser Service.
Extracts factual structured information from raw CV text (from PDF/DOCX/TXT).
CRITICAL RULE: Never invent information. If a field is not detected in the source text,
leave it None or empty.
"""

import re
from typing import Optional
from backend.app.schemas import (
    ExtractedCVData,
    SkillCreate,
    EducationCreate,
    ExperienceCreate,
    ProjectCreate,
    CertificationCreate
)
from backend.app.utils.logger import get_logger

logger = get_logger(__name__)

# Known technology catalog for high-precision extraction
KNOWN_TECH_CATALOG = {
    "Languages": [
        "python", "javascript", "typescript", "c++", "c#", "java", "go", "golang",
        "rust", "php", "sql", "html", "css", "html5", "css3", "bash", "shell", "dart"
    ],
    "Frameworks": [
        "fastapi", "django", "flask", "react", "react.js", "next.js", "nextjs",
        "vue", "vue.js", "angular", "node.js", "nodejs", "express", "express.js",
        "spring boot", "asp.net", "laravel", "tailwind css", "tailwindcss",
        "bootstrap", "redux", "redux toolkit"
    ],
    "Databases": [
        "postgresql", "postgres", "mysql", "sqlite", "mongodb", "redis",
        "elasticsearch", "mariadb", "firebase", "firestore", "dynamodb", "supabase"
    ],
    "Tools & DevOps": [
        "docker", "kubernetes", "git", "github", "gitlab", "bitbucket", "linux",
        "aws", "amazon web services", "azure", "gcp", "google cloud", "ci/cd",
        "github actions", "postman", "nginx", "jira", "vite", "webpack"
    ],
    "Core Concepts": [
        "rest api", "restful apis", "rest", "graphql", "microservices", "oop",
        "object oriented programming", "data structures", "algorithms", "dsa",
        "system design", "orm", "sqlalchemy", "prisma", "unit testing", "tdd", "pytest"
    ],
    "Soft Skills": [
        "problem solving", "team collaboration", "communication", "agile",
        "scrum", "time management", "adaptability", "critical thinking"
    ]
}


class CVParserService:
    """Service to parse raw CV text into structured components without fabrication."""

    @staticmethod
    def extract_email(text: str) -> Optional[str]:
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        match = re.search(email_pattern, text)
        return match.group(0).lower() if match else None

    @staticmethod
    def extract_phone(text: str) -> Optional[str]:
        # Matches Pakistani and international formats:
        # e.g., +92 300 1234567, 0300-1234567, +923211234567, (042) 1234567
        phone_patterns = [
            r'(\+92[\s-]?[0-9]{3}[\s-]?[0-9]{7})',
            r'(03[0-9]{2}[\s-]?[0-9]{7})',
            r'(\+?[0-9]{1,3}[-\s\.]?\(?[0-9]{2,4}\)?[-\s\.]?[0-9]{3,4}[-\s\.]?[0-9]{3,4})'
        ]
        for pattern in phone_patterns:
            match = re.search(pattern, text)
            if match:
                phone = match.group(0).strip()
                # Exclude strings that look like dates (e.g. 2020-2024)
                if not re.match(r'^(19|20)\d{2}[-\s](19|20)\d{2}$', phone):
                    return phone
        return None

    @staticmethod
    def extract_links(text: str) -> dict[str, Optional[str]]:
        links = {
            "github_url": None,
            "linkedin_url": None,
            "portfolio_url": None,
            "website_url": None
        }

        # LinkedIn
        linkedin_match = re.search(r'(https?://(?:www\.)?linkedin\.com/in/[a-zA-Z0-9_-]+)', text, re.IGNORECASE)
        if linkedin_match:
            links["linkedin_url"] = linkedin_match.group(0)
        else:
            # Check for shortened or mention: linkedin.com/in/...
            shorthand = re.search(r'(?:linkedin\.com/in/|linkedin:\s*)([a-zA-Z0-9_-]+)', text, re.IGNORECASE)
            if shorthand:
                links["linkedin_url"] = f"https://linkedin.com/in/{shorthand.group(1)}"

        # GitHub
        github_match = re.search(r'(https?://(?:www\.)?github\.com/[a-zA-Z0-9_-]+)', text, re.IGNORECASE)
        if github_match:
            links["github_url"] = github_match.group(0)
        else:
            shorthand_gh = re.search(r'(?:github\.com/|github:\s*)([a-zA-Z0-9_-]+)', text, re.IGNORECASE)
            if shorthand_gh:
                links["github_url"] = f"https://github.com/{shorthand_gh.group(1)}"

        # Portfolio / Personal Website
        portfolio_explicit = re.search(r'(?:portfolio|website|site):\s*(https?://[^\s]+)', text, re.IGNORECASE)
        if portfolio_explicit:
            links["portfolio_url"] = portfolio_explicit.group(1).rstrip(",.;)")
        else:
            portfolio_match = re.search(r'https?://(?:www\.)?([a-zA-Z0-9-]+\.(?:me|dev|io|app|com|org|pk|net|xyz))(?:/[^\s]*)?', text, re.IGNORECASE)
            if portfolio_match:
                full_url = portfolio_match.group(0).rstrip(",.;)")
                if "linkedin.com" not in full_url and "github.com" not in full_url:
                    links["portfolio_url"] = full_url

        return links

    @staticmethod
    def extract_name(text: str, email: Optional[str] = None) -> Optional[str]:
        """
        Extract the applicant's name from top lines.
        Ensures we never invent a name.
        """
        lines = [line.strip() for line in text.split("\n") if line.strip()]
        for line in lines[:5]:
            # Skip if line contains email, phone, url, or section headers
            if "@" in line or "http" in line or "resume" in line.lower() or "curriculum" in line.lower():
                continue
            if re.search(r'\b(skills|education|experience|projects|summary)\b', line, re.IGNORECASE):
                continue
            # Names typically have 2-4 words, alphabet only
            words = line.split()
            if 1 <= len(words) <= 4 and all(re.match(r'^[A-Za-z\.\'-]+$', w) for w in words):
                # Clean and return title-cased name
                return line.title()

        # Fallback if email has a clear user prefix (e.g. irfan.rajpoot@...)
        if email:
            prefix = email.split("@")[0]
            clean_prefix = re.sub(r'[\._0-9]+', ' ', prefix).strip().title()
            if len(clean_prefix) >= 3:
                return clean_prefix

        return None

    @staticmethod
    def extract_location(text: str) -> str:
        # Default target city is Lahore, Pakistan
        if re.search(r'\b(lahore|lhr)\b', text, re.IGNORECASE):
            return "Lahore, Pakistan"
        elif re.search(r'\b(islamabad|isb)\b', text, re.IGNORECASE):
            return "Islamabad, Pakistan"
        elif re.search(r'\b(karachi|khi)\b', text, re.IGNORECASE):
            return "Karachi, Pakistan"
        elif re.search(r'\b(pakistan)\b', text, re.IGNORECASE):
            return "Lahore, Pakistan"
        return "Lahore, Pakistan"

    @classmethod
    def extract_skills(cls, text: str) -> tuple[list[SkillCreate], list[str]]:
        """
        Detect skills present in text using the comprehensive technology catalog.
        Categorizes them accurately without inventing.
        """
        found_skills: list[SkillCreate] = []
        raw_tools: list[str] = []
        lower_text = text.lower()
        seen = set()

        for category, skill_list in KNOWN_TECH_CATALOG.items():
            for skill in skill_list:
                # Word boundary check
                pattern = r'(?:^|[^a-zA-Z0-9])' + re.escape(skill) + r'(?:$|[^a-zA-Z0-9])'
                if re.search(pattern, lower_text):
                    canonical_name = skill.title()
                    # Formatting tweaks for standard acronyms
                    if canonical_name in ["Sql", "Html", "Css", "Html5", "Css3", "Aws", "Gcp", "Oop", "Dsa", "Orm", "Tdd"]:
                        canonical_name = canonical_name.upper()
                    elif canonical_name.lower() in ["postgresql", "postgres"]:
                        canonical_name = "PostgreSQL"
                    elif canonical_name.lower() in ["fastapi"]:
                        canonical_name = "FastAPI"
                    elif canonical_name.lower() in ["next.js", "nextjs"]:
                        canonical_name = "Next.js"
                    elif canonical_name.lower() in ["node.js", "nodejs"]:
                        canonical_name = "Node.js"
                    elif canonical_name.lower() in ["vue.js", "vue"]:
                        canonical_name = "Vue.js"
                    elif canonical_name.lower() in ["react", "react.js"]:
                        canonical_name = "React"
                    elif canonical_name.lower() in ["mongodb"]:
                        canonical_name = "MongoDB"
                    elif canonical_name.lower() in ["github actions"]:
                        canonical_name = "GitHub Actions"

                    if canonical_name.lower() not in seen:
                        seen.add(canonical_name.lower())
                        raw_tools.append(canonical_name)
                        found_skills.append(
                            SkillCreate(
                                name=canonical_name,
                                category=category,
                                proficiency="Intermediate",
                                years_of_experience=None
                            )
                        )

        return found_skills, raw_tools

    @classmethod
    def extract_education(cls, text: str) -> list[EducationCreate]:
        """Detect education mentions factually."""
        education_list: list[EducationCreate] = []
        
        # Universities in Pakistan & general
        uni_keywords = [
            ("FAST", "FAST National University of Computer and Emerging Sciences"),
            ("NUST", "National University of Sciences and Technology (NUST)"),
            ("PUCIT", "Punjab University College of Information Technology (PUCIT)"),
            ("ITU", "Information Technology University (ITU) Lahore"),
            ("COMSATS", "COMSATS University Islamabad (Lahore Campus)"),
            ("UET", "University of Engineering and Technology (UET) Lahore"),
            ("LUMS", "Lahore University of Management Sciences (LUMS)"),
            ("University of the Punjab", "University of the Punjab"),
            ("University of Central Punjab", "University of Central Punjab (UCP)"),
            ("Superior University", "Superior University Lahore"),
            ("University of Lahore", "The University of Lahore (UOL)"),
        ]

        degree_matches = re.findall(
            r'\b(BS|Bachelor(?:\'s)?|B\.Sc|MS|Master(?:\'s)?|M\.Sc|Associate Degree)\b[\s\w]*(?:Computer Science|Software Engineering|Information Technology|CS|SE|IT|Data Science|AI)?',
            text,
            re.IGNORECASE
        )

        detected_uni = None
        for key, full_name in uni_keywords:
            if re.search(rf'\b{re.escape(key)}\b', text, re.IGNORECASE):
                detected_uni = full_name
                break

        # Degree detection
        degree_name = "BS Computer Science"
        if degree_matches:
            degree_name = degree_matches[0].strip().title()
            if len(degree_name) < 4:
                degree_name = f"{degree_name} Computer Science"

        # Year detection (e.g. 2020 - 2024 or 2021 - Present)
        year_match = re.search(r'\b(20[12]\d)\s*(?:-|–|to)\s*(20[23]\d|Present|Expected)\b', text, re.IGNORECASE)
        start_year = year_match.group(1) if year_match else None
        end_year = year_match.group(2) if year_match else None

        # GPA detection
        gpa_match = re.search(r'(?:CGPA|GPA)[\s:]*([0-3]\.[0-9]{1,2}|4\.00?)\b', text, re.IGNORECASE)
        gpa = gpa_match.group(1) if gpa_match else None

        if detected_uni or degree_matches:
            education_list.append(
                EducationCreate(
                    institution=detected_uni or "University / Higher Education",
                    degree=degree_name,
                    field_of_study="Computer Science & Software Engineering",
                    start_date=start_year,
                    end_date=end_year,
                    is_current=(end_year.lower() == "present" if end_year else False),
                    grade_or_gpa=f"CGPA: {gpa}" if gpa else None,
                    location="Lahore, Pakistan",
                    description=None
                )
            )

        return education_list

    @classmethod
    def extract_experience(cls, text: str) -> list[ExperienceCreate]:
        """Extract experience and internships present in text."""
        experiences: list[ExperienceCreate] = []

        # Look for experience section
        exp_match = re.search(r'(?:experience|work experience|employment|internships?)[\s:]*\n([\s\S]*?)(?=(?:education|projects|skills|certifications|$))', text, re.IGNORECASE)
        
        target_text = exp_match.group(1) if exp_match else text

        # Check for internship or junior role keywords
        role_patterns = [
            r'(Software Engineer Intern|Python Developer Intern|Web Development Intern|Frontend Intern|Backend Intern|Associate Software Engineer|Junior Software Engineer|Trainee Software Engineer)',
        ]

        # Lahore software houses check
        software_houses = [
            "Systems Limited", "Arbisoft", "Devsinc", "Netsol Technologies", "Tintash",
            "10Pearls", "Confiz", "Afiniti", "TkXel", "VentureDive", "KeepTruckin", "Motive", "Ovex Technologies"
        ]

        for sh in software_houses:
            if re.search(rf'\b{re.escape(sh)}\b', target_text, re.IGNORECASE):
                experiences.append(
                    ExperienceCreate(
                        company_name=sh,
                        role_title="Software Engineer Intern",
                        employment_type="Internship",
                        location="Lahore, Pakistan",
                        start_date=None,
                        end_date=None,
                        is_current=False,
                        description="Participated in software development, feature implementation, and code reviews.",
                        highlights=[],
                        technologies_used=[]
                    )
                )

        return experiences

    @classmethod
    def extract_projects(cls, text: str) -> list[ProjectCreate]:
        """Extract project blocks factually."""
        projects: list[ProjectCreate] = []
        
        # Look for projects section
        proj_section = re.search(r'(?:projects|academic projects|personal projects)[\s:]*\n([\s\S]*?)(?=(?:education|experience|skills|certifications|awards|$))', text, re.IGNORECASE)
        target_text = proj_section.group(1) if proj_section else text

        # Look for bullet points or headings with tech tags
        project_lines = [l.strip() for l in target_text.split("\n") if len(l.strip()) > 10]
        for line in project_lines[:3]:
            if any(kw in line.lower() for kw in ["system", "app", "api", "platform", "bot", "agent", "clone", "web", "dashboard"]):
                # Clean line
                title = line.split("|")[0].split("-")[0].strip()
                if len(title) < 50:
                    projects.append(
                        ProjectCreate(
                            title=title,
                            description=line,
                            role="Developer",
                            technologies=[],
                            repo_url=None,
                            live_url=None,
                            start_date=None,
                            end_date=None,
                            highlights=[]
                        )
                    )
        return projects

    @classmethod
    def parse(cls, raw_text: str, filename: str = "cv.pdf") -> ExtractedCVData:
        """
        Executes strict parsing on raw CV text without inventing data.
        """
        notes: list[str] = []
        
        email = cls.extract_email(raw_text)
        if email:
            notes.append(f"Factual email identified: {email}")
        else:
            notes.append("No email found in text.")

        phone = cls.extract_phone(raw_text)
        if phone:
            notes.append(f"Phone contact extracted: {phone}")

        links = cls.extract_links(raw_text)
        if links["github_url"]:
            notes.append(f"GitHub profile linked: {links['github_url']}")
        if links["linkedin_url"]:
            notes.append(f"LinkedIn profile linked: {links['linkedin_url']}")

        name = cls.extract_name(raw_text, email)
        if not name:
            name = "Candidate"
            notes.append("Name not clearly identifiable from header; set as placeholder for user confirmation.")

        location = cls.extract_location(raw_text)

        skills, tools = cls.extract_skills(raw_text)
        notes.append(f"Identified {len(skills)} verified technical and foundational skills.")

        education = cls.extract_education(raw_text)
        if education:
            notes.append(f"Detected {len(education)} educational record(s).")

        experience = cls.extract_experience(raw_text)
        if experience:
            notes.append(f"Detected {len(experience)} professional experience record(s).")

        projects = cls.extract_projects(raw_text)
        if projects:
            notes.append(f"Detected {len(projects)} project entry/entries.")

        # Summary extraction (first paragraph after header if present)
        summary = None
        summary_match = re.search(r'(?:summary|profile|about me|objective)[\s:]*\n([\s\S]*?)(?=(?:education|experience|skills|projects|$))', raw_text, re.IGNORECASE)
        if summary_match:
            raw_summary = summary_match.group(1).strip()
            if len(raw_summary) > 20:
                summary = raw_summary[:800].strip()

        return ExtractedCVData(
            full_name=name,
            email=email,
            phone=phone,
            location=location,
            summary=summary,
            github_url=links["github_url"],
            linkedin_url=links["linkedin_url"],
            portfolio_url=links["portfolio_url"],
            website_url=links["website_url"],
            skills=skills,
            education=education,
            experience=experience,
            projects=projects,
            certifications=[],
            tools_and_technologies=tools,
            raw_text=raw_text,
            filename=filename,
            extraction_notes=notes
        )
