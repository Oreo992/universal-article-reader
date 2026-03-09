"""Zhihu (zhihu.com) adapter."""

import re
import html as htmlmod
from typing import Any, Dict
from urllib.parse import urlparse

from .base import SiteAdapter, SiteConfig


class ZhihuAdapter(SiteAdapter):
    """Adapter for Zhihu articles and answers."""

    _HOSTS = {"zhihu.com", "www.zhihu.com", "zhuanlan.zhihu.com"}

    def match(self, url: str) -> bool:
        try:
            host = urlparse(url).hostname or ""
            return host in self._HOSTS
        except Exception:
            return False

    def site_config(self) -> SiteConfig:
        return SiteConfig(
            ua=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0 Safari/537.36"
            ),
            referer="https://www.zhihu.com/",
            accept_language="zh-CN,zh;q=0.9",
            browser_wait_selector=".Post-RichTextContainer, .RichContent-inner",
            needs_browser=True,
        )

    def parse(self, html: str) -> Dict[str, Any]:
        title = ""
        m = re.search(r"<h1[^>]*class=\"[^\"]*Post-Title[^\"]*\"[^>]*>(.*?)</h1>", html, re.S | re.I)
        if m:
            title = re.sub(r"<[^>]+>", "", m.group(1)).strip()
        if not title:
            m = re.search(r"property=\"og:title\"[^>]*content=\"(.*?)\"", html, re.I)
            if m:
                title = htmlmod.unescape(m.group(1)).strip()

        author = ""
        m = re.search(r"\"name\"\s*:\s*\"(.*?)\"", html)
        if m:
            author = m.group(1).strip()
        if not author:
            m = re.search(r"class=\"[^\"]*AuthorInfo-name[^\"]*\"[^>]*>(.*?)</", html, re.S | re.I)
            if m:
                author = re.sub(r"<[^>]+>", "", m.group(1)).strip()

        pub_time = ""
        m = re.search(r"\"datePublished\"\s*:\s*\"(.*?)\"", html)
        if m:
            pub_time = m.group(1).strip()

        content_html = ""
        # Try zhuanlan article body
        m = re.search(r"<div[^>]*class=\"[^\"]*Post-RichTextContainer[^\"]*\"[^>]*>(.*?)</div>\s*</div>", html, re.S | re.I)
        if m:
            content_html = m.group(1)
        if not content_html:
            m = re.search(r"<div[^>]*class=\"[^\"]*RichContent-inner[^\"]*\"[^>]*>(.*?)</div>", html, re.S | re.I)
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
    images: list = []
    for attr in ("src", "data-original", "data-actualsrc"):
        for im in re.findall(rf"<img[^>]*{attr}=\"(.*?)\"", html, re.I):
            v = htmlmod.unescape(im)
            if v and v not in seen:
                seen.add(v)
                images.append(v)
    return images


def _extract_links(html: str) -> list:
    return list(dict.fromkeys(
        htmlmod.unescape(a) for a in re.findall(r"<a[^>]*href=\"(.*?)\"", html, re.I)
    ))
