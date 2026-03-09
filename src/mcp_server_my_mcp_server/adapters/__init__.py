"""
Site adapters package.

Each adapter handles fetching configuration and HTML parsing for a specific
website (or class of websites).
"""

from .base import SiteConfig, SiteAdapter, AdapterRegistry

__all__ = ["SiteConfig", "SiteAdapter", "AdapterRegistry"]
