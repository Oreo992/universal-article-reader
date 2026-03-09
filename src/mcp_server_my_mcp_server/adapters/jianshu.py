"""Jianshu (jianshu.com) adapter."""

import re
import html as htmlmod
from typing import Any, Dict
from urllib.parse import urlparse

from .base import SiteAdapter, SiteConfig


class JianshuAdapter(SiteAdapter):
    """Adapter for Jianshu articles."""

    def match(self, url: str) -> bool:
        try:
            host = urlparse(url).hostname or ""
            return host in ("jianshu.com", "www.jianshu.com")
        except Exception:
            return False

    def site_config(self) -> SiteConfig:
        return SiteConfig(
            ua=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0 Safari/537.36"
            ),
            referer="https://www.jianshu.com/",
            accept_language="zh-CN,zh;q=0.9",
            browser_wait_selector="article, .show-content",
            needs_browser=False,
        )

    def parse(self, html: str) -> Dict[str, Any]:
        title = ""
        m = re.search(r"<h1[^>]*class=\"[^\"]*title[^\"]*\"[^>]*>(.*?)</h1>", html, re.S | re.I)
        if m:
            title = re.sub(r"<[^>]+>", "", m.group(1)).strip()
        if not title:
            m = re.search(r"property=\"og:title\"[^>]*content=\"(.*?)\"", html, re.I)
            if m:
                title = htmlmod.unescape(m.group(1)).strip()

        author = ""
        m = re.search(r"class=\"[^\"]*name[^\"]*\"[^>]*><a[^>]*>(.*?)</a>", html, re.S | re.I)
        if m:
            author = re.sub(r"<[^>]+>", "", m.group(1)).strip()

        pub_time = ""
        m = re.search(r"class=\"[^\"]*publish-time[^\"]*\"[^>]*>(.*?)</", html, re.S | re.I)
        if m:
            pub_time = re.sub(r"<[^>]+>", "", m.group(1)).strip()
        if not pub_time:
            m = re.search(r"property=\"article:published_time\"[^>]*content=\"(.*?)\"", html, re.I)
            if m:
                pub_time = m.group(1).strip()

        content_html = ""
        m = re.search(r"<article[^>]*>(.*?)</article>", html, re.S | re.I)
        if m:
            content_html = m.group(1)
        if not content_html:
            m = re.search(r"<div[^>]*class=\"[^\"]*show-content[^\"]*\"[^>]*>(.*?)</div>", html, re.S | re.I)
            if m:
                content_html = m.group(1)

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


def _extract_images(html: str) -> list:
    seen: set = set()
    imgs: list = []
    for attr in ("src", "data-original-src"):
        for im in re.findall(rf"<img[^>]*{attr}=\"(.*?)\"", html, re.I):
            v = htmlmod.unescape(im)
            if v and v not in seen:
                seen.add(v)
                imgs.append(v)
    return imgs


def _extract_links(html: str) -> list:
    return list(dict.fromkeys(
        htmlmod.unescape(a) for a in re.findall(r"<a[^>]*href=\"(.*?)\"", html, re.I)
    ))
