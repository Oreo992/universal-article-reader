"""Test generic adapter parsing."""

from mcp_server_my_mcp_server.adapters.generic import GenericAdapter


SAMPLE_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Generic Article Title</title>
    <meta property="og:title" content="Generic Article Title" />
    <meta name="author" content="John Doe" />
    <meta property="article:published_time" content="2024-01-01T00:00:00Z" />
</head>
<body>
    <article>
        <h1>Generic Article Title</h1>
        <p>This is the article content.</p>
        <img src="https://example.com/image.jpg" />
        <a href="https://example.com/link">Link</a>
    </article>
</body>
</html>
"""


def test_generic_adapter_match():
    adapter = GenericAdapter()
    assert adapter.match("https://example.com/article")
    assert adapter.match("http://blog.example.org/post/123")
    assert not adapter.match("ftp://example.com/file")


def test_generic_adapter_parse():
    adapter = GenericAdapter()
    result = adapter.parse(SAMPLE_HTML)

    assert result["title"] == "Generic Article Title"
    assert result["author"] == "John Doe"
    assert result["pub_time"] == "2024-01-01T00:00:00Z"
    assert "article content" in result["content_html"]
    assert len(result["images"]) >= 1
    assert len(result["links"]) >= 1


def test_generic_adapter_clean_url():
    adapter = GenericAdapter()
    dirty = "https://example.com/article?utm_source=test&utm_medium=email&id=123"
    clean = adapter.clean_url(dirty)
    assert "utm_source" not in clean
    assert "utm_medium" not in clean
    assert "id=123" in clean
