"""
Job Discovery Sources Registry.
Enables plug-and-play addition of new career portals and job boards.
"""

from typing import Dict, List, Optional
from backend.app.services.job_discovery.base_source import BaseJobSource
from backend.app.services.job_discovery.sources.devsinc_source import DevsincJobSource
from backend.app.services.job_discovery.sources.educative_source import EducativeJobSource
from backend.app.services.job_discovery.sources.netsol_source import NetsolJobSource, ConfizJobSource
from backend.app.services.job_discovery.sources.whizzbridge_source import WhizzbridgeJobSource
from backend.app.services.job_discovery.sources.venturedive_source import VentureDiveJobSource
from backend.app.services.job_discovery.sources.systems_limited_source import SystemsLimitedJobSource
from backend.app.services.job_discovery.sources.arbisoft_source import ArbisoftJobSource
from backend.app.services.job_discovery.sources.rozee_source import RozeeJobSource, SearchEngineJobSource
from backend.app.services.job_discovery.sources.tintash_source import TintashJobSource
from backend.app.services.job_discovery.sources.ten_pearls_source import TenPearlsJobSource
from backend.app.schemas import JobDiscoverySourceInfo
from backend.app.utils.logger import get_logger

logger = get_logger(__name__)

# Register all modular sources
_ALL_SOURCES: Dict[str, BaseJobSource] = {
    "devsinc": DevsincJobSource(),
    "educative": EducativeJobSource(),
    "netsol": NetsolJobSource(),
    "whizzbridge": WhizzbridgeJobSource(),
    "venturedive": VentureDiveJobSource(),
    "confiz": ConfizJobSource(),
    "systems_limited": SystemsLimitedJobSource(),
    "arbisoft": ArbisoftJobSource(),
    "rozee_pk": RozeeJobSource(),
    "search_engine": SearchEngineJobSource(),
    "tintash": TintashJobSource(),
    "ten_pearls": TenPearlsJobSource(),
}

# Alias mapping for environment variable configurations
SOURCE_ALIASES = {
    "rozee": "rozee_pk",
    "rozee_pk": "rozee_pk",
    "official_careers": ["devsinc", "educative", "netsol", "whizzbridge", "venturedive", "systems_limited", "arbisoft"],
    "company_careers": ["devsinc", "educative", "netsol", "whizzbridge", "venturedive", "systems_limited", "arbisoft"],
    "linkedin": "search_engine",
    "indeed": "search_engine",
    "job_board": ["rozee_pk", "search_engine"],
}


def resolve_source_ids(source_keys: List[str]) -> List[str]:
    """Resolve aliases like 'official_careers' into specific modular source IDs."""
    resolved: List[str] = []
    for key in source_keys:
        k = key.strip().lower()
        if k in SOURCE_ALIASES:
            alias = SOURCE_ALIASES[k]
            if isinstance(alias, list):
                resolved.extend(alias)
            else:
                resolved.append(alias)
        elif k in _ALL_SOURCES:
            resolved.append(k)
        else:
            resolved.append(k)
    return list(dict.fromkeys(resolved))


def get_all_sources() -> Dict[str, BaseJobSource]:
    """Return all registered job discovery sources."""
    return _ALL_SOURCES


def get_source_by_id(source_id: str) -> Optional[BaseJobSource]:
    """Retrieve specific source instance by ID with alias support."""
    k = source_id.strip().lower()
    if k in _ALL_SOURCES:
        return _ALL_SOURCES[k]
    if k in SOURCE_ALIASES and isinstance(SOURCE_ALIASES[k], str):
        return _ALL_SOURCES.get(SOURCE_ALIASES[k])
    return None


def list_source_infos() -> List[JobDiscoverySourceInfo]:
    """Return serializable information for all registered sources."""
    return [
        JobDiscoverySourceInfo(
            id=s.source_id,
            name=s.source_name,
            type=s.source_type,
            is_active=s.is_active,
            base_url=s.base_url,
            description=s.description
        )
        for s in _ALL_SOURCES.values()
    ]
