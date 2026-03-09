"""Test WeChat adapter parsing."""

from mcp_server_my_mcp_server.adapters.wechat import WechatAdapter


SAMPLE_HTML = """
<!DOCTYPE html>
<html>
<head>
    <meta property="og:title" content="测试文章标题" />
    <meta name="author" content="测试公众号" />
    <meta property="article:published_time" content="2024-01-01T00:00:00Z" />
</head>
<body>
    <h2 id="activity-name">测试文章标题</h2>
    <div id="js_name">测试公众号</div>
    <div id="js_content">
        <p>这是文章内容。</p>
        <img src="https://example.com/image1.jpg" />
        <img data-src="https://example.com/image2.jpg" />
        <a href="https://example.com/link">链接</a>
    </div>
</body>
</html>
"""


def test_wechat_adapter_match():
    adapter = WechatAdapter()
    assert adapter.match("https://mp.weixin.qq.com/s/abc123")
    assert adapter.match("https://mp.weixin.qq.com/s?__biz=xxx")
    assert not adapter.match("https://example.com/article")


def test_wechat_adapter_parse():
    adapter = WechatAdapter()
    result = adapter.parse(SAMPLE_HTML)

    assert result["title"] == "测试文章标题"
    assert result["author"] == "测试公众号"
    assert result["pub_time"] == "2024-01-01T00:00:00Z"
    assert "这是文章内容" in result["content_html"]
    assert len(result["images"]) >= 1
    assert len(result["links"]) >= 1


def test_wechat_adapter_clean_url():
    adapter = WechatAdapter()
    dirty = "https://mp.weixin.qq.com/s/abc?chksm=123&scene=456&utm_source=test"
    clean = adapter.clean_url(dirty)
    assert "chksm" not in clean
    assert "scene" not in clean
    assert "utm_source" not in clean
