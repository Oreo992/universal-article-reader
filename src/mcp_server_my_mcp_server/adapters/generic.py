"""Generic (fallback) adapter — works with any URL."""

import re
import html as htmlmod
from typing import Any, Dict
from urllib.parse import urlparse, parse_qs, urlunparse

from .base import SiteAdapter, SiteConfig


class GenericAdapter(SiteAdapter):
    """Fallback adapter that tries to extract content from any web page.

    It looks for ``<article>``, then ``<main>``, then ``<body>`` as the
    content container.
    """

    def match(self, url: str) -> bool:
        try:
            scheme = urlparse(url).scheme
            return scheme in ("http", "https")
        except Exception:
            return False

    def site_config(self) -> SiteConfig:
        return SiteConfig(
            ua=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0 Safari/537.36"
            ),
            referer="",
            accept_language="zh-CN,zh;q=0.9,en;q=0.8",
            needs_browser=False,
        )

    def clean_url(self, url: str) -> str:
        try:
            u = urlparse(url)
            q = parse_qs(u.query, keep_blank_values=True)
            for k in list(q):
                if k.startswith("utm_"):
                    q.pop(k)
            query = "&".join(f"{k}={','.join(v)}" for k, v in q.items())
            return urlunparse((u.scheme, u.netloc, u.path, u.params, query, u.fragment))
        except Exception:
            return url

    def parse(self, html: str) -> Dict[str, Any]:
        title = _extract_title(html)
        author = _extract_author(html)
        pub_time = _extract_pub_time(html)
        content_html = _extract_content(html)
        images = _extract_images(content_html)
        links = _extract_links(content_html)

        return {
            "title": title,
            "author": author,
            "pub_time": pub_time,
            "content_html": content_html,
            "images": images,
            "links": links,
        }


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def _extract_title(html: str) -> str:
    # og:title
    m = re.search(r"property=\"og:title\"[^>]*content=\"(.*?)\"", html, re.I)
    if m:
        return htmlmod.unescape(m.group(1)).strip()
    # <title>
    m = re.search(r"<title[^>]*>(.*?)</title>", html, re.S | re.I)
    if m:
        return htmlmod.unescape(re.sub(r"<[^>]+>", "", m.group(1))).strip()
    # first <h1>
    m = re.search(r"<h1[^>]*>(.*?)</h1>", html, re.S | re.I)
    if m:
        return re.sub(r"<[^>]+>", "", m.group(1)).strip()
    return ""


def _extract_author(html: str) -> str:
    m = re.search(r"name=\"author\"[^>]*content=\"(.*?)\"", html, re.I)
    if m:
        return htmlmod.unescape(m.group(1)).strip()
    m = re.search(r"\"author\"\s*:\s*(?:\{[^}]*\"name\"\s*:\s*)?\"(.*?)\"", html)
    if m:
        return m.group(1).strip()
    return ""


def _extract_pub_time(html: str) -> str:
    for prop in ("article:published_time", "datePublished", "og:updated_time"):
        m = re.search(rf"(?:property|name)=\"{prop}\"[^>]*content=\"(.*?)\"", html, re.I)
        if m:
            return m.group(1).strip()
    m = re.search(r"\"datePublished\"\s*:\s*\"(.*?)\"", html)
    if m:
        return m.group(1).strip()
    return ""


def _extract_content(html: str) -> str:
    # Try <article>
    m = re.search(r"<article[^>]*>(.*?)</article>", html, re.S | re.I)
    if m:
        return m.group(1)
    # Try <main>
    m = re.search(r"<main[^>]*>(.*?)</main>", html, re.S | re.I)
    if m:
        return m.group(1)
    # Fallback to <body>
    m = re.search(r"<body[^>]*>(.*?)</body>", html, re.S | re.I)
    if m:
        return m.group(1)
    return html


def _extract_images(html: str) -> list:
    seen: set = set()
    imgs: list = []
    for im in re.findall(r"<img[^>]*src=\"(.*?)\"", html, re.I):
        v = htmlmod.unescape(im)
        if v and v not in seen:
            seen.add(v)
            imgs.append(v)
    return imgs


def _extract_links(html: str) -> list:
    return list(dict.fromkeys(
        htmlmod.unescape(a) for a in re.findall(r"<a[^>]*href=\"(.*?)\"", html, re.I)
    ))
