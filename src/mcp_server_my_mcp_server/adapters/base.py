"""
Base classes for site adapters.

SiteConfig  — per-site HTTP / browser configuration
SiteAdapter — abstract adapter that every site must implement
AdapterRegistry — URL → adapter router
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse


@dataclass
class SiteConfig:
    """Per-site fetch configuration."""

    ua: str = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0 Safari/537.36"
    )
    referer: str = ""
    accept_language: str = "zh-CN,zh;q=0.9,en;q=0.8"
    extra_headers: Dict[str, str] = field(default_factory=dict)
    timeout_seconds: int = 15
    browser_wait_selector: Optional[str] = None
    needs_browser: bool = False


class SiteAdapter(ABC):
    """Abstract base class for all site adapters."""

    @abstractmethod
    def match(self, url: str) -> bool:
        """Return True if this adapter can handle *url*."""

    @abstractmethod
    def site_config(self) -> SiteConfig:
        """Return fetch configuration for this site."""

    @abstractmethod
    def parse(self, html: str) -> Dict[str, Any]:
        """
        Parse raw HTML and return a dict with at least:
          title, author, pub_time, content_html, images, links
        """

    def clean_url(self, url: str) -> str:
        """Optional: strip tracking / normalise URL. Default: identity."""
        return url

    def validate_url(self, url: str) -> bool:
        """Optional: extra validation beyond match(). Default: True."""
        return True


class AdapterRegistry:
    """Registry that routes a URL to the first matching adapter."""

    def __init__(self, adapters: Optional[List[SiteAdapter]] = None):
        self._adapters: List[SiteAdapter] = list(adapters or [])

    def register(self, adapter: SiteAdapter) -> None:
        self._adapters.append(adapter)

    def find(self, url: str) -> Optional[SiteAdapter]:
        for adapter in self._adapters:
            if adapter.match(url):
                return adapter
        return None
