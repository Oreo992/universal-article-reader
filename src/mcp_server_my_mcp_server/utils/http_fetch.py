from typing import Optional, Any
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError
import ssl

from .observability import Timer


def fetch_html(url: str, config: Any) -> tuple[Optional[str], int | None, int]:
    """
    Fetch HTML via standard library (urllib) to avoid external deps.
    Returns: (html, status_code, duration_ms)

    *config* is duck-typed — any object with .ua, .referer, .accept_language,
    .timeout_seconds attributes (WechatReaderConfig or SiteConfig both work).
    """
    timer = Timer()

    headers = {
        "User-Agent": config.ua,
        "Referer": config.referer,
        "Accept-Language": config.accept_language,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Cache-Control": "no-cache",
    }
    # Merge extra_headers if the config provides them (SiteConfig does)
    extra = getattr(config, "extra_headers", None)
    if extra:
        headers.update(extra)

    req = Request(url, headers=headers, method="GET")

    # Use default SSL context (certificate verification ON).
    # If your environment requires disabling verification (not recommended),
    # replace with: ctx = ssl._create_unverified_context()
    ctx = ssl.create_default_context()
    try:
        with urlopen(req, timeout=config.timeout_seconds, context=ctx) as resp:
            status = getattr(resp, "status", None)
            html = resp.read().decode("utf-8", errors="ignore")
            return html, status, timer.elapsed_ms()
    except HTTPError as e:
        return None, e.code, timer.elapsed_ms()
    except URLError:
        return None, None, timer.elapsed_ms()
    except Exception:
        return None, None, timer.elapsed_ms()