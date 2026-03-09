"""
Headless browser fallback (Playwright/Puppeteer).

To enable, install Playwright for Python:
    pip install playwright
    playwright install chromium

Then implement fetch_html_via_browser to open the page, wait for #js_content,
and return rendered HTML.

This scaffold provides an optional implementation placeholder to avoid hard deps
at this stage.
"""

from typing import Optional, Any

try:
    from playwright.sync_api import sync_playwright  # type: ignore
    HAS_PLAYWRIGHT = True
except Exception:
    HAS_PLAYWRIGHT = False

from .observability import Timer


def fetch_html_via_browser(
    url: str,
    config: Any,
    wait_selector: Optional[str] = None,
) -> tuple[Optional[str], int | None, int]:
    """Fetch *url* with a headless Chromium browser.

    *config* is duck-typed (needs .browser_enabled, .ua, .referer,
    .timeout_seconds).  *wait_selector* overrides the default selector to
    wait for after navigation (e.g. ``#js_content`` for WeChat).
    """
    timer = Timer()
    if not getattr(config, "browser_enabled", True) or not HAS_PLAYWRIGHT:
        return None, None, timer.elapsed_ms()

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            ctx = browser.new_context(user_agent=config.ua, locale="zh-CN")
            page = ctx.new_page()
            page.set_extra_http_headers({"Referer": config.referer})
            page.goto(url, wait_until="domcontentloaded", timeout=config.timeout_seconds * 1000)
            # wait for a content selector if provided
            selector = wait_selector
            if selector:
                try:
                    page.wait_for_selector(selector, timeout=8000)
                except Exception:
                    pass
            try:
                page.wait_for_load_state("networkidle", timeout=5000)
            except Exception:
                pass
            html = page.content()
            browser.close()
            # no status code via Playwright API; return None
            return html, None, timer.elapsed_ms()
    except Exception:
        return None, None, timer.elapsed_ms()
