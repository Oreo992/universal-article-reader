"""Juejin (juejin.cn) adapter."""

import re
import html as htmlmod
from typing import Any, Dict
from urllib.parse import urlparse

from .base import SiteAdapter, SiteConfig


class JuejinAdapter(SiteAdapter):
    """Adapter for Juejin (掘金) articles — SPA, needs browser."""

    def match(self, url: str) -> bool:
        try:
            host = urlparse(url).hostname or ""
            return host in ("juejin.cn", "www.juejin.cn")
        except Exception:
            return False

    def site_config(self) -> SiteConfig:
        return SiteConfig(
            ua=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0 Safari/537.36"
            ),
            referer="https://juejin.cn/",
            accept_language="zh-CN,zh;q=0.9",
            browser_wait_selector=".article-content",
            needs_browser=True,
        )

    def parse(self, html: str) -> Dict[str, Any]:
        title = ""
        m = re.search(r"<h1[^>]*class=\"[^\"]*article-title[^\"]*\"[^>]*>(.*?)</h1>", html, re.S | re.I)
        if m:
            title = re.sub(r"<[^>]+>", "", m.group(1)).strip()
        if not title:
            m = re.search(r"property=\"og:title\"[^>]*content=\"(.*?)\"", html, re.I)
            if m:
                title = htmlmod.unescape(m.group(1)).strip()

        author = ""
        m = re.search(r"class=\"[^\"]*username[^\"]*\"[^>]*>(.*?)</", html, re.S | re.I)
        if m:
            author = re.sub(r"<[^>]+>", "", m.group(1)).strip()

        pub_time = ""
        m = re.search(r"class=\"[^\"]*time[^\"]*\"[^>]*>(.*?)</", html, re.S | re.I)
        if m:
            pub_time = re.sub(r"<[^>]+>", "", m.group(1)).strip()

        content_html = ""
        m = re.search(r"<div[^>]*class=\"[^\"]*article-content[^\"]*\"[^>]*>(.*?)</div>\s*</div>", html, re.S | re.I)
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
