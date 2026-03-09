from dataclasses import dataclass, asdict
from typing import Dict, Any

from ..utils.config import WechatReaderConfig
from ..utils.rate_limit import TokenBucket
from ..utils.http_fetch import fetch_html
from ..utils.browser_fetch import fetch_html_via_browser
from ..utils.parser import naive_parse_wechat_html
from ..utils.markdown import html_to_markdown_minimal
from ..utils.cache import TTLCache, content_fingerprint
from ..utils.compliance import is_public_wechat_article, strip_tracking_params
from ..utils.observability import FetchLog


ERROR_INVALID_URL = "invalid_url"
ERROR_NEED_AUTH = "need_auth"
ERROR_BLOCKED_403 = "blocked_403"
ERROR_RATE_LIMITED_429 = "rate_limited_429"
ERROR_TIMEOUT = "timeout"
ERROR_NO_CONTENT = "no_content"


@dataclass
class ReadResult:
    title: str
    author: str
    pub_time: str
    content_md: str
    images: list[str]
    links: list[str]
    source_url: str
    strategy: str
    logs: dict

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class WechatArticleReader:
    def __init__(self, config: WechatReaderConfig):
        self.config = config
        self.bucket = TokenBucket(capacity=config.burst, refill_rate_per_sec=config.rate_limit_per_min / 60.0)
        self.cache = TTLCache(ttl_seconds=config.cache_ttl_seconds)

    def read(self, url: str, include_images: bool = True, force_browser: bool = False) -> Dict[str, Any]:
        # compliance: only public links
        if not is_public_wechat_article(url):
            return {"error": ERROR_INVALID_URL, "message": "URL not allowed (must be public mp.weixin.qq.com/s link).", "source_url": url}

        clean_url = strip_tracking_params(url)

        # cache
        cached = self.cache.get(clean_url)
        if cached:
            return cached

        # rate limit
        self.bucket.acquire()

        # attempt HTTP fetch first
        html, status, dur = fetch_html(clean_url, self.config)
        log_http = FetchLog(url=clean_url, strategy="http", status_code=status, success=bool(html), error_code=None, retries=0, duration_ms=dur, ua=self.config.ua, referer=self.config.referer)

        log_browser = None
        strategy = "http"
        logs: Dict[str, Any] = {"http": log_http.to_dict()}

        if not html or (status is not None and status >= 400):
            # fallback to browser if HTTP failed
            html2, status2, dur2 = fetch_html_via_browser(clean_url, self.config, wait_selector="#js_content")
            log_browser = FetchLog(url=clean_url, strategy="browser", status_code=status2, success=bool(html2), error_code=None, retries=0, duration_ms=dur2, ua=self.config.ua, referer=self.config.referer)
            final_html = html2 or ""
            strategy = "browser_fallback" if final_html else "http_failed"
            logs = {"http": log_http.to_dict(), "browser": log_browser.to_dict()}
            if not final_html:
                err = ERROR_NO_CONTENT if (status is None or status == 200) else (ERROR_BLOCKED_403 if status == 403 else ERROR_TIMEOUT)
                return {"error": err, "message": "Failed to fetch article.", "source_url": clean_url, "logs": logs}
            html = final_html
        elif force_browser and self.config.browser_enabled:
            # force a browser render to improve image extraction even if HTTP succeeded
            html2, status2, dur2 = fetch_html_via_browser(clean_url, self.config, wait_selector="#js_content")
            log_browser = FetchLog(url=clean_url, strategy="browser", status_code=status2, success=bool(html2), error_code=None, retries=0, duration_ms=dur2, ua=self.config.ua, referer=self.config.referer)
            if html2:
                html = html2
                strategy = "browser_forced"
            logs = {"http": log_http.to_dict(), "browser": (log_browser.to_dict() if log_browser else {})}

        parsed = naive_parse_wechat_html(html)
        content_html = parsed.get("content_html", "")
        content_md = html_to_markdown_minimal(content_html)

        result = ReadResult(
            title=parsed.get("title", ""),
            author=parsed.get("author", ""),
            pub_time=parsed.get("pub_time", ""),
            content_md=content_md,
            images=parsed.get("images", []) if include_images else [],
            links=parsed.get("links", []),
            source_url=clean_url,
            strategy=strategy,
            logs=logs,
        ).to_dict()

        # cache by source_url + fingerprint (optional, here use URL key only)
        self.cache.set(clean_url, result)

        return result


def read_wechat_article(url: str, include_images: bool = True, force_browser: bool = False, config: WechatReaderConfig | None = None) -> Dict[str, Any]:
    """
    MCP tool entry: read a public WeChat article and return structured output.
    """
    cfg = config or WechatReaderConfig()
    reader = WechatArticleReader(cfg)
    return reader.read(url, include_images=include_images, force_browser=force_browser)