"""Test universal article reader."""

from mcp_server_my_mcp_server.tools.read_article import read_article


def test_read_article_invalid_url():
    result = read_article("not-a-url")
    assert "error" in result


def test_read_article_unsupported_scheme():
    result = read_article("ftp://example.com/file")
    assert "error" in result or result.get("adapter") == "GenericAdapter"


def test_read_article_wechat_invalid():
    # This URL doesn't start with /s, so WeChat adapter won't match it
    # GenericAdapter will match and try to fetch, which will fail
    result = read_article("https://mp.weixin.qq.com/invalid")
    assert "error" in result
    # The URL is technically valid HTTP, so it will be tried and fail with no_content
    assert result["error"] in ("invalid_url", "unsupported_site", "no_content")
