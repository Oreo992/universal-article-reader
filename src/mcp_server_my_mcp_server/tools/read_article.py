"""
Universal article reader — works with any supported site.

Uses the adapter registry to detect the site and select the right parser.
"""

from dataclasses import dataclass, asdict
from typing import Any, Dict, Optional

from ..adapters.base import AdapterRegistry, SiteConfig
from ..adapters.wechat import WechatAdapter
from ..adapters.zhihu import ZhihuAdapter
from ..adapters.csdn import CSDNAdapter
from ..adapters.jianshu import JianshuAdapter
from ..adapters.juejin import JuejinAdapter
from ..adapters.cnblogs import CnblogsAdapter
from ..adapters.medium import MediumAdapter
from ..adapters.generic import GenericAdapter

from ..utils.config import ReaderConfig
from ..utils.rate_limit import TokenBucket
from ..utils.http_fetch import fetch_html
from ..utils.browser_fetch import fetch_html_via_browser
from ..utils.markdown import html_to_markdown_minimal
from ..utils.cache import TTLCache
from ..utils.observability import FetchLog


ERROR_INVALID_URL = "invalid_url"
ERROR_UNSUPPORTED = "unsupported_site"
ERROR_BLOCKED_403 = "blocked_403"
ERROR_TIMEOUT = "timeout"
ERROR_NO_CONTENT = "no_content"


def _build_default_registry() -> AdapterRegistry:
    """Build a registry with all built-in adapters (GenericAdapter last)."""
    return AdapterRegistry([
        WechatAdapter(),
        ZhihuAdapter(),
        CSDNAdapter(),
        JianshuAdapter(),
        JuejinAdapter(),
        CnblogsAdapter(),
        MediumAdapter(),
        GenericAdapter(),  # fallback — must be last
    ])


@dataclass
class ArticleReadResult:
    title: str
    author: str
    pub_time: str
    content_md: str
    images: list
    links: list
    source_url: str
    adapter: str
    strategy: str
    logs: dict

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class ArticleReader:
    """Universal article reader with caching and rate-limiting."""

    def __init__(
        self,
        config: Optional[ReaderConfig] = None,
        registry: Optional[AdapterRegistry] = None,
    ):
        self.config = config or ReaderConfig()
        self.registry = registry or _build_default_registry()
        self.bucket = TokenBucket(
            capacity=self.config.burst,
            refill_rate_per_sec=self.config.rate_limit_per_min / 60.0,
        )
        self.cache = TTLCache(ttl_seconds=self.config.cache_ttl_seconds)

    def read(
        self,
        url: str,
        include_images: bool = True,
        force_browser: bool = False,
    ) -> Dict[str, Any]:
        # 1. find adapter
        adapter = self.registry.find(url)
        if adapter is None:
            return {
                "error": ERROR_UNSUPPORTED,
                "message": "No adapter found for this URL.",
                "source_url": url,
            }

        # 2. validate
        if not adapter.validate_url(url):
            return {
                "error": ERROR_INVALID_URL,
                "message": "URL validation failed.",
                "source_url": url,
            }

        # 3. clean url
        clean_url = adapter.clean_url(url)

        # 4. cache
        cached = self.cache.get(clean_url)
        if cached:
            return cached

        # 5. rate limit
        self.bucket.acquire()

        # 6. build fetch config by merging adapter site_config with reader config
        site_cfg = adapter.site_config()
        fetch_cfg = _FetchConfig(site_cfg, self.config)

        # 7. fetch
        use_browser = force_browser or site_cfg.needs_browser
        html, status, dur, strategy, logs = self._fetch(
            clean_url, fetch_cfg, site_cfg, use_browser
        )

        if not html:
            err = ERROR_NO_CONTENT
            if status == 403:
                err = ERROR_BLOCKED_403
            elif status is None:
                err = ERROR_TIMEOUT
            return {
                "error": err,
                "message": "Failed to fetch article.",
                "source_url": clean_url,
                "logs": logs,
            }

        # 8. parse
        parsed = adapter.parse(html)
        content_html = parsed.get("content_html", "")
        content_md = html_to_markdown_minimal(content_html)

        result = ArticleReadResult(
            title=parsed.get("title", ""),
            author=parsed.get("author", ""),
            pub_time=parsed.get("pub_time", ""),
            content_md=content_md,
            images=parsed.get("images", []) if include_images else [],
            links=parsed.get("links", []),
            source_url=clean_url,
            adapter=type(adapter).__name__,
            strategy=strategy,
            logs=logs,
        ).to_dict()

        self.cache.set(clean_url, result)
        return result

    # ------------------------------------------------------------------
    def _fetch(self, url, fetch_cfg, site_cfg, use_browser):
        """Try HTTP first; fall back / force browser as needed."""
        logs: Dict[str, Any] = {}

        if not use_browser:
            html, status, dur = fetch_html(url, fetch_cfg)
            log_http = FetchLog(
                url=url, strategy="http", status_code=status,
                success=bool(html), error_code=None, retries=0,
                duration_ms=dur, ua=fetch_cfg.ua, referer=fetch_cfg.referer,
            )
            logs["http"] = log_http.to_dict()

            if html and (status is None or status < 400):
                return html, status, dur, "http", logs

            # fallback to browser
            if self.config.browser_enabled:
                html2, status2, dur2 = fetch_html_via_browser(
                    url, fetch_cfg,
                    wait_selector=site_cfg.browser_wait_selector,
                )
                log_br = FetchLog(
                    url=url, strategy="browser", status_code=status2,
                    success=bool(html2), error_code=None, retries=0,
                    duration_ms=dur2, ua=fetch_cfg.ua, referer=fetch_cfg.referer,
                )
                logs["browser"] = log_br.to_dict()
                if html2:
                    return html2, status2, dur2, "browser_fallback", logs
            return None, status, dur, "http_failed", logs

        # browser-first path
        html, status, dur = fetch_html_via_browser(
            url, fetch_cfg,
            wait_selector=site_cfg.browser_wait_selector,
        )
        log_br = FetchLog(
            url=url, strategy="browser", status_code=status,
            success=bool(html), error_code=None, retries=0,
            duration_ms=dur, ua=fetch_cfg.ua, referer=fetch_cfg.referer,
        )
        logs["browser"] = log_br.to_dict()

        if html:
            return html, status, dur, "browser", logs

        # fallback to HTTP even when browser was preferred
        html2, status2, dur2 = fetch_html(url, fetch_cfg)
        log_http = FetchLog(
            url=url, strategy="http", status_code=status2,
            success=bool(html2), error_code=None, retries=0,
            duration_ms=dur2, ua=fetch_cfg.ua, referer=fetch_cfg.referer,
        )
        logs["http"] = log_http.to_dict()
        if html2 and (status2 is None or status2 < 400):
            return html2, status2, dur2, "http_fallback", logs
        return None, status2, dur2, "browser_failed", logs


class _FetchConfig:
    """Adapter between SiteConfig + ReaderConfig and the duck-typed fetch API."""

    def __init__(self, site: SiteConfig, reader: ReaderConfig):
        self.ua = site.ua
        self.referer = site.referer
        self.accept_language = site.accept_language
        self.extra_headers = site.extra_headers
        self.timeout_seconds = reader.timeout_seconds
        self.browser_enabled = reader.browser_enabled


# -----------------------------------------------------------------------
# Module-level convenience function (MCP tool entry point)
# -----------------------------------------------------------------------

def read_article(
    url: str,
    include_images: bool = True,
    force_browser: bool = False,
    config: Optional[ReaderConfig] = None,
) -> Dict[str, Any]:
    """Read an article from any supported site and return structured output."""
    reader = ArticleReader(config=config)
    return reader.read(url, include_images=include_images, force_browser=force_browser)
