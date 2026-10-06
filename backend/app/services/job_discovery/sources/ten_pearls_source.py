"""
10Pearls Official Careers Source.
Connects to 10Pearls Lahore career portal.
"""

from typing import List
import httpx
from bs4 import BeautifulSoup
from backend.app.services.job_discovery.base_source import BaseJobSource, RawDiscoveredJob
from backend.app.utils.logger import get_logger

logger = get_logger(__name__)


class TenPearlsJobSource(BaseJobSource):
    source_id = "ten_pearls"
    source_name = "10Pearls Careers"
    source_type = "company_careers"
    base_url = "https://10pearls.com/careers"
    description = "Official career portal of 10Pearls Lahore."

    async def discover_jobs(
        self,
        keywords: List[str],
        target_city: str = "Lahore",
        limit: int = 20
    ) -> List[RawDiscoveredJob]:
        logger.info(f"[{self.source_id}] Querying live 10Pearls portal...")
        results: List[RawDiscoveredJob] = []

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
        }

        try:
            async with httpx.AsyncClient(headers=headers, follow_redirects=True, timeout=12.0) as client:
                resp = await client.get(self.base_url)
                logger.info(f"[{self.source_id}] Status {resp.status_code} ({len(resp.text)} bytes)")
                
                soup = BeautifulSoup(resp.text, "html.parser")
                # 10Pearls uses client-side embedded widget / iframe for open positions
                logger.info(f"[{self.source_id}] Parsed 10Pearls portal page.")
        except Exception as e:
            logger.error(f"[{self.source_id}] Query failed: {e}")

        return results
