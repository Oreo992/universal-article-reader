from typing import Dict, Any
import re
import html as htmlmod
from datetime import datetime, timezone


def _extract_between(html: str, start: str, end: str) -> str:
    try:
        i = html.index(start)
        j = html.index(end, i + len(start))
        return html[i + len(start): j]
    except Exception:
        return ""


def naive_parse_wechat_html(html: str) -> Dict[str, Any]:
    """
    Naive parser that attempts to extract title, author, published time, and
    main content region (#js_content). For production use, replace with
    BeautifulSoup-based robust parsing.
    """
    # title
    title = ""
    m = re.search(r"<h2[^>]*id=\"activity-name\"[^>]*>(.*?)</h2>", html, re.S | re.I)
    if m:
        title = re.sub(r"<[^>]+>", "", m.group(1)).strip()
    if not title:
        m = re.search(r"property=\"og:title\"[^>]*content=\"(.*?)\"", html, re.I)
        if m:
            title = m.group(1).strip()

    # author (public account name)
    author = ""
    m = re.search(r"id=\"js_name\"[^>]*>(.*?)</", html, re.S | re.I)
    if m:
        author = re.sub(r"<[^>]+>", "", m.group(1)).strip()
    if not author:
        m = re.search(r"name=\"author\"[^>]*content=\"(.*?)\"", html, re.I)
        if m:
            author = m.group(1).strip()

    # published time meta
    pub_time = ""
    m = re.search(r"property=\"article:published_time\"[^>]*content=\"(.*?)\"", html, re.I)
    if m:
        pub_time = m.group(1).strip()
    if not pub_time:
        m = re.search(r"property=\"og:updated_time\"[^>]*content=\"(.*?)\"", html, re.I)
        if m:
            pub_time = m.group(1).strip()
    # fallback: parse ct (unix timestamp) from inline script: var ct = "1699999999";
    if not pub_time:
        m = re.search(r"var\s+ct\s*=\s*\"?(\d{10})\"?\s*;", html)
        if m:
            try:
                ts = int(m.group(1))
                pub_time = datetime.fromtimestamp(ts, tz=timezone.utc).isoformat()
            except Exception:
                pass

    # main content (#js_content)
    content_html = ""
    m = re.search(r"<div[^>]*id=\"js_content\"[^>]*>(.*?)</div>", html, re.S | re.I)
    if m:
        content_html = m.group(1)
        # Normalize common WeChat lazy-load attributes onto src for downstream Markdown conversion
        # - data-src, data-original, data-backup-src
        content_html = re.sub(r"<img([^>]*?)data-src=\"(.*?)\"", r"<img\\1src=\"\\2\"", content_html)
        content_html = re.sub(r"<img([^>]*?)data-original=\"(.*?)\"", r"<img\\1src=\"\\2\"", content_html)
        content_html = re.sub(r"<img([^>]*?)data-backup-src=\"(.*?)\"", r"<img\\1src=\"\\2\"", content_html)

    # Collect image URLs using multiple strategies commonly seen in WeChat articles
    images = []
    # 1) img src="..."
    for im in re.findall(r"<img[^>]*src=\"(.*?)\"", content_html, re.I):
        images.append(htmlmod.unescape(im))
    # 2) img data-src="..." (lazy loaded)
    for im in re.findall(r"<img[^>]*data-src=\"(.*?)\"", content_html, re.I):
        images.append(htmlmod.unescape(im))
    # 3) img data-original / data-backup-src variants
    for im in re.findall(r"<img[^>]*data-original=\"(.*?)\"", content_html, re.I):
        images.append(htmlmod.unescape(im))
    for im in re.findall(r"<img[^>]*data-backup-src=\"(.*?)\"", content_html, re.I):
        images.append(htmlmod.unescape(im))
    # 4) Inline style background-image: url("...") on figure/section/span
    for im in re.findall(r"background-image\s*:\s*url\(['\"]?(.*?)['\"]?\)", content_html, re.I):
        images.append(htmlmod.unescape(im))
    # Deduplicate while preserving order
    seen = set()
    dedup_images = []
    for im in images:
        if im and im not in seen:
            seen.add(im)
            dedup_images.append(im)

    # collect links
    links = []
    for a in re.findall(r"<a[^>]*href=\"(.*?)\"", content_html, re.I):
        links.append(htmlmod.unescape(a))

    return {
        "title": title,
        "author": author,
        "pub_time": pub_time,
        "content_html": content_html,
        "images": dedup_images,
        "links": list(dict.fromkeys(links)),
    }