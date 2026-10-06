"""
Whizzbridge Official Careers Source.
Live web scraping for official Whizzbridge career portal (Lahore).
"""

from typing import List
import httpx
from bs4 import BeautifulSoup
from backend.app.services.job_discovery.base_source import BaseJobSource, RawDiscoveredJob
from backend.app.utils.logger import get_logger

logger = get_logger(__name__)


class WhizzbridgeJobSource(BaseJobSource):
    source_id = "whizzbridge"
    source_name = "Whizzbridge Careers"
    source_type = "company_careers"
    base_url = "https://www.whizzbridge.com/careers"
    description = "Official career portal of Whizzbridge Lahore."

    async def discover_jobs(
        self,
        keywords: List[str],
        target_city: str = "Lahore",
        limit: int = 20
    ) -> List[RawDiscoveredJob]:
        logger.info(f"[{self.source_id}] Querying live Whizzbridge careers...")
        results: List[RawDiscoveredJob] = []

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
        }

        try:
            async with httpx.AsyncClient(headers=headers, follow_redirects=True, timeout=12.0) as client:
                resp = await client.get(self.base_url)
                if resp.status_code != 200:
                    logger.warning(f"[{self.source_id}] Whizzbridge returned HTTP {resp.status_code}")
                    return results

                soup = BeautifulSoup(resp.text, "html.parser")
                
                # Whizzbridge lists links like /career/ai-application-engineer-agentic-systems
                job_links = []
                for a in soup.find_all("a", href=True):
                    href = a["href"]
                    if href.startswith("/career/") and href != "/career/" and href not in job_links:
                        job_links.append(href)

                logger.info(f"[{self.source_id}] Found {len(job_links)} openings on Whizzbridge.")

                for path in job_links:
                    full_url = f"https://www.whizzbridge.com{path}" if path.startswith("/") else path
                    try:
                        det_resp = await client.get(full_url)
                        if det_resp.status_code != 200:
                            continue

                        det_soup = BeautifulSoup(det_resp.text, "html.parser")
                        h1 = det_soup.find("h1")
                        title = h1.get_text(strip=True) if h1 else path.replace("/career/", "").replace("-", " ").title()

                        # Keyword check
                        if keywords:
                            matches = any(
                                kw.lower() in title.lower() or any(term in title.lower() for term in ["engineer", "developer", "ai", "ml", "python", "software"])
                                for kw in keywords
                            )
                            if not matches:
                                continue

                        desc_paragraphs = [p.get_text(strip=True) for p in det_soup.find_all("p") if len(p.get_text(strip=True)) > 30]
                        full_desc = "\n\n".join(desc_paragraphs[:8]) or f"{title} at Whizzbridge, Lahore."

                        responsibilities: List[str] = []
                        req_skills: List[str] = []

                        for ul in det_soup.find_all("ul"):
                            items = [li.get_text(strip=True) for li in ul.find_all("li") if len(li.get_text(strip=True)) > 10]
                            for it in items:
                                if any(k in it.lower() for k in ["python", "machine learning", "rag", "git", "api", "experience", "degree"]):
                                    req_skills.append(it[:80])
                                else:
                                    responsibilities.append(it[:100])

                        results.append(
                            RawDiscoveredJob(
                                company="Whizzbridge",
                                job_title=title,
                                location=f"{target_city}, Pakistan",
                                description=full_desc,
                                raw_description=full_desc,
                                responsibilities=responsibilities[:8],
                                required_skills=req_skills[:8] or ["Python", "AI/ML Basics", "REST APIs", "Git"],
                                preferred_skills=["FastAPI", "Docker", "RAG", "LLMs"],
                                experience_requirement="0-2 years (Entry to Junior)",
                                education_requirement="BS Computer Science / Software Engineering",
                                job_type="Full-time",
                                source="Whizzbridge Careers",
                                source_url=full_url,
                                job_url=full_url
                            )
                        )

                        if len(results) >= limit:
                            break

                    except Exception as e:
                        logger.debug(f"Failed to fetch detail for {path}: {e}")

        except Exception as e:
            logger.error(f"[{self.source_id}] Live query failed: {e}")

        logger.info(f"[{self.source_id}] Extracted {len(results)} valid live jobs.")
        return results
