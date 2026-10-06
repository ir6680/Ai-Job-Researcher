"""
Job Cleaning, Normalization, Filtering, and Deduplication Service.
Ensures zero bad data enters the database:
- Normalizes company names and titles
- Strictly filters for Lahore location
- Strictly filters for entry-level / junior scope (rejecting senior/lead roles)
- Removes duplicates via URL and content similarity fingerprinting
"""

import re
import hashlib
from typing import Optional, Tuple, List
from sqlalchemy.orm import Session
from backend.app.services.job_discovery.base_source import RawDiscoveredJob
from backend.app.models import Job
from backend.app.utils.logger import get_logger

logger = get_logger(__name__)

# Known Company Normalization Mapping for Lahore Software Houses
COMPANY_NORMALIZATION_MAP = {
    "systems": "Systems Limited",
    "systems ltd": "Systems Limited",
    "systems limited pakistan": "Systems Limited",
    "arbisoft": "Arbisoft",
    "arbisoft llc": "Arbisoft",
    "arbisoft pvt ltd": "Arbisoft",
    "devsinc": "Devsinc",
    "devsinc inc": "Devsinc",
    "devsinc pvt ltd": "Devsinc",
    "tintash": "Tintash",
    "tintash studios": "Tintash",
    "10pearls": "10Pearls",
    "ten pearls": "10Pearls",
    "netsol": "Netsol Technologies",
    "netsol tech": "Netsol Technologies",
    "netsol technologies limited": "Netsol Technologies",
    "confiz": "Confiz",
    "confiz solutions": "Confiz",
    "tkxel": "TkXel",
    "venturedive": "VentureDive",
    "afiniti": "Afiniti",
    "educative": "Educative",
    "whizzbridge": "Whizzbridge",
}

# Known Non-Entry Keywords to immediately reject
SENIOR_KEYWORDS = [
    r"\bsenior\b", r"\bsr\.\b", r"\blead\b", r"\bprincipal\b", r"\bstaff\b",
    r"\barchitect\b", r"\bdirector\b", r"\bhead of\b", r"\bmanager\b",
    r"\bvp\b", r"\bvice president\b", r"\bteam lead\b", r"\btech lead\b",
    r"\b5\+\s*years\b", r"\b6\+\s*years\b", r"\b7\+\s*years\b", r"\b8\+\s*years\b",
    r"\b10\+\s*years\b"
]

# Explicit Other Cities to reject if not Remote
OTHER_CITIES_REJECT = [
    r"\bkarachi\b", r"\bislamabad\b", r"\brawalpindi\b", r"\bfaisalabad\b",
    r"\bpeshawar\b", r"\bmultan\b", r"\bquetta\b", r"\bdubai\b", r"\blondon\b",
    r"\bnew york\b", r"\bberlin\b", r"\bsingapore\b"
]


class JobCleanerService:
    """Handles cleaning, normalization, validation, and deduplication of discovered jobs."""

    @staticmethod
    def normalize_company(company: str) -> str:
        """Normalize company name to canonical form."""
        cleaned = company.strip()
        lower = cleaned.lower()
        for pattern, canonical in COMPANY_NORMALIZATION_MAP.items():
            if lower == pattern or lower.startswith(pattern):
                return canonical
        # Remove trailing LLC, Pvt Ltd, Inc
        cleaned = re.sub(r'[\(\[\{]?(?:pvt|private|llc|inc|limited|ltd)[\)\]\}]?\.?', '', cleaned, flags=re.IGNORECASE).strip()
        return cleaned.title() if len(cleaned) > 2 else company.strip()

    @staticmethod
    def normalize_job_title(title: str) -> str:
        """Clean title of noise like [Urgent], (Immediate), location suffixes."""
        cleaned = title.strip()
        # Remove bracketed tags like [Urgent], (Walk-in), [Lahore]
        cleaned = re.sub(r'[\[\(].*?(?:urgent|immediate|lahore|walk-in|hiring|pk).*?[\]\)]', '', cleaned, flags=re.IGNORECASE)
        # Remove trailing dash / separator followed by Lahore / Pakistan
        cleaned = re.sub(r'[-\|\/]\s*(?:lahore|pakistan|on-site|remote).*?$', '', cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        return cleaned.title() if cleaned else title.strip()

    @staticmethod
    def is_lahore_location(location: str, description: str, target_city: str = "Lahore") -> Tuple[bool, str]:
        """
        Verify if the job is located in Lahore, Pakistan or Remote open to Pakistan.
        Rejects jobs strictly designated for other cities.
        """
        loc_lower = location.lower()
        # 1. Reject other cities immediately if not Lahore
        for city_pat in OTHER_CITIES_REJECT:
            if re.search(city_pat, loc_lower) and "lahore" not in loc_lower:
                return False, f"Job location is non-Lahore ({location})"

        comb = f"{location} {description[:300]}".lower()

        # 2. Check for remote open to Pakistan
        if "remote" in comb or "anywhere in pakistan" in comb or "work from home" in comb:
            return True, "Remote (Pakistan)"

        # 3. Check for explicit other city in description if Lahore not mentioned
        for city_pat in OTHER_CITIES_REJECT:
            if re.search(city_pat, comb) and "lahore" not in comb:
                return False, f"Job location is non-Lahore ({location})"

        # 4. Check for Lahore
        if "lahore" in comb or "lhr" in comb or "johar town" in comb or "gulberg" in comb:
            return True, "Lahore, Pakistan"

        # 5. Default fallback: if location specifies Pakistan and no other city
        if "pakistan" in comb:
            return True, "Lahore, Pakistan"

        return False, f"Location '{location}' is not in {target_city}"

    @classmethod
    def is_entry_level(
        cls,
        title: str,
        description: str,
        experience_requirement: str,
        keywords: Optional[List[str]] = None
    ) -> Tuple[bool, str]:
        """
        Validates if the position is genuine entry-level / junior / trainee / intern.
        Rejects senior, staff, lead, and manager positions.
        """
        title_lower = title.lower()
        desc_lower = description[:1000].lower()
        exp_lower = experience_requirement.lower()

        # 1. Check for Senior rejections in Title first
        for pat in SENIOR_KEYWORDS:
            if re.search(pat, title_lower):
                return False, f"Rejected: Title contains senior keyword '{pat}'"

        # 2. Check for heavy experience requirements in text
        if re.search(r'\b(4\+|5\+|6\+|7\+|8\+|10\+)\s*(?:to\s*\d+\s*)?years\b', exp_lower) or \
           re.search(r'\b(4\+|5\+|6\+|7\+|8\+|10\+)\s*(?:to\s*\d+\s*)?years\s*(?:of\s*)?experience\b', desc_lower):
            return False, "Rejected: Requires 4+ years of professional experience"

        # 3. Check for positive entry-level markers
        entry_markers = [
            r"\bentry[- ]level\b", r"\bfresh\b", r"\btrainee\b", r"\bintern\b",
            r"\binternship\b", r"\bjunior\b", r"\bjr\.\b", r"\bassociate\b",
            r"\bgraduate\b", r"\b0[- ]1\s*years?\b", r"\b0[- ]2\s*years?\b",
            r"\b1[- ]2\s*years?\b", r"\bno experience required\b"
        ]
        for marker in entry_markers:
            if re.search(marker, title_lower) or re.search(marker, exp_lower) or re.search(marker, desc_lower[:400]):
                return True, "Verified Entry-Level"

        # 4. Check if title matches configured entry keywords
        if keywords:
            for kw in keywords:
                if kw.lower() in title_lower:
                    return True, f"Matches keyword: {kw}"

        # Standard Software Engineer title with 0-2 years experience is acceptable
        if "software engineer" in title_lower or "developer" in title_lower or "programmer" in title_lower:
            return True, "Standard Software Engineer opening"

        return False, "Does not match entry-level software/IT criteria"

    @staticmethod
    def extract_responsibilities(text: str) -> List[str]:
        """Extract bullet points of key responsibilities from text."""
        responsibilities: List[str] = []
        
        # Look for responsibilities header
        resp_block = re.search(
            r'(?:responsibilities|duties|what you will do|key responsibilities|role description)[\s:]*\n([\s\S]*?)(?=(?:requirements|qualifications|skills|what we offer|benefits|$))',
            text,
            re.IGNORECASE
        )
        target = resp_block.group(1) if resp_block else text

        for line in target.split("\n"):
            clean = line.strip()
            # Look for bullet indicators: -, *, •, or numbered: 1.
            if re.match(r'^[-*•\d\.]+\s+', clean):
                item = re.sub(r'^[-*•\d\.]+\s+', '', clean).strip()
                if 15 < len(item) < 250:
                    responsibilities.append(item)

        return responsibilities[:8]

    @staticmethod
    def compute_dedup_hash(company: str, title: str, location: str, url: str, description: str) -> str:
        """
        Compute deterministic SHA-256 fingerprint for deduplication.
        Combines normalized company + title + first 150 characters of description.
        """
        norm_company = company.strip().lower()
        norm_title = re.sub(r'[^a-z0-9]', '', title.lower())
        norm_desc = re.sub(r'\s+', ' ', description[:150].lower())
        key = f"{norm_company}::{norm_title}::{norm_desc}"
        return hashlib.sha256(key.encode('utf-8')).hexdigest()

    @classmethod
    def detect_duplicate(cls, job: RawDiscoveredJob, db: Session) -> Tuple[bool, Optional[str]]:
        """
        Check if job is a duplicate in the database.
        Checks:
        1. Exact job_url / source_url match
        2. Exact dedup_hash match
        3. Same company + exact normalized title within last 30 days
        """
        # 1. URL match
        if job.source_url:
            existing = db.query(Job).filter(
                (Job.source_url == job.source_url) | (Job.job_url == job.source_url)
            ).first()
            if existing:
                return True, existing.id

        # 2. Hash match
        dedup_hash = cls.compute_dedup_hash(
            job.company, job.job_title, job.location, job.source_url, job.description
        )
        existing_hash = db.query(Job).filter(Job.dedup_hash == dedup_hash).first()
        if existing_hash:
            return True, existing_hash.id

        # 3. Soft match: Same company and normalized title
        norm_title = job.job_title.lower().strip()
        same_title = db.query(Job).filter(
            Job.company.ilike(job.company),
            Job.job_title.ilike(norm_title)
        ).first()
        if same_title:
            return True, same_title.id

        return False, None

    @classmethod
    def clean_and_normalize(cls, raw: RawDiscoveredJob) -> RawDiscoveredJob:
        """Produce fully cleaned job representation preserving original raw description."""
        cleaned_company = cls.normalize_company(raw.company)
        cleaned_title = cls.normalize_job_title(raw.job_title)
        
        # Preserve original description in raw_description if not already set
        raw_desc = raw.raw_description or raw.description
        
        # Clean description whitespace
        cleaned_desc = re.sub(r'\n{3,}', '\n\n', raw.description).strip()
        
        # Extract responsibilities if not provided
        responsibilities = raw.responsibilities
        if not responsibilities:
            responsibilities = cls.extract_responsibilities(cleaned_desc)

        return RawDiscoveredJob(
            company=cleaned_company,
            job_title=cleaned_title,
            location=raw.location or "Lahore, Pakistan",
            description=cleaned_desc,
            raw_description=raw_desc,
            responsibilities=responsibilities,
            required_skills=raw.required_skills,
            preferred_skills=raw.preferred_skills,
            experience_requirement=raw.experience_requirement or "Entry-level (0-1 years)",
            education_requirement=raw.education_requirement or "BS Computer Science / Software Engineering",
            job_type=raw.job_type or "Full-time",
            salary=raw.salary,
            source=raw.source,
            source_url=raw.source_url,
            job_url=raw.job_url or raw.source_url,
            posting_date=raw.posting_date,
            deadline=raw.deadline
        )
