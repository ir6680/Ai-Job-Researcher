"""
Tintash Official Careers Source.
Connects to Tintash's careers portal.
"""

from typing import List
import httpx
from backend.app.services.job_discovery.base_source import BaseJobSource, RawDiscoveredJob
from backend.app.utils.logger import get_logger

logger = get_logger(__name__)


class TintashJobSource(BaseJobSource):
    source_id = "tintash"
    source_name = "Tintash Careers"
    source_type = "company_careers"
    base_url = "https://tintash.com/careers"
    description = "Official career portal of Tintash Studios (Lahore)."

    async def discover_jobs(
        self,
        keywords: List[str],
        target_city: str = "Lahore",
        limit: int = 20
    ) -> List[RawDiscoveredJob]:
        logger.info(f"[{self.source_id}] Querying live Tintash portal...")
        results: List[RawDiscoveredJob] = []

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
        }

        try:
            async with httpx.AsyncClient(headers=headers, follow_redirects=True, timeout=12.0) as client:
                resp = await client.get(self.base_url)
                if resp.status_code == 404:
                    logger.warning(
                        f"[{self.source_id}] Tintash careers URL returned HTTP 404 Not Found. "
                        "The company has restructured its career links or moved hiring to unindexed subpages."
                    )
                    return results

                logger.info(f"[{self.source_id}] Response status: {resp.status_code}")
        except Exception as e:
            logger.error(f"[{self.source_id}] Query failed: {e}")

        return results
