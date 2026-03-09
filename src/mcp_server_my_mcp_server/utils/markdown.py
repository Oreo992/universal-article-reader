import re


def html_to_markdown_minimal(html: str) -> str:
    """
    Minimal HTML→Markdown converter for paragraphs and images.
    For production, replace with markdownify/turndown-like robust converter.
    """
    if not html:
        return ""

    # images
    html = re.sub(r"<img[^>]*src=\"(.*?)\"[^>]*>", r"![](\1)", html, flags=re.I)

    # links: keep text (strip tags)
    html = re.sub(r"<a[^>]*href=\"(.*?)\"[^>]*>(.*?)</a>", r"\2 (\1)", html, flags=re.S | re.I)

    # replace <br> with newline
    html = re.sub(r"<br\s*/?>", "\n", html, flags=re.I)

    # paragraphs
    html = re.sub(r"</p>", "\n\n", html, flags=re.I)
    html = re.sub(r"<p[^>]*>", "", html, flags=re.I)

    # strip other tags
    text = re.sub(r"<[^>]+>", "", html)
    # normalize spaces
    text = re.sub(r"\s+", " ", text).strip()
    # restore basic newlines
    text = re.sub(r" \n ", "\n", text)
    return text