"""
Basic tests (placeholders). In a real environment, provide a public WeChat
article URL and assert structured output. Here we only verify function returns
dict and error handling on invalid URLs.
"""

from mcp_server_my_mcp_server.tools.read_wechat_article import read_wechat_article


def test_invalid_url():
    res = read_wechat_article("https://example.com/abc")
    assert isinstance(res, dict)
    assert res.get("error") == "invalid_url"