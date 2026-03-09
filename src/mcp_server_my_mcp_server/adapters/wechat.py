"""WeChat (mp.weixin.qq.com) adapter — wraps existing parser & compliance logic."""

from typing import Any, Dict

from .base import SiteAdapter, SiteConfig
from ..utils.parser import naive_parse_wechat_html
from ..utils.compliance import is_public_wechat_article, strip_tracking_params


class WechatAdapter(SiteAdapter):
    """Adapter for WeChat Official Account articles."""

    def match(self, url: str) -> bool:
        return is_public_wechat_article(url)

    def site_config(self) -> SiteConfig:
        return SiteConfig(
            ua=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/116.0 Safari/537.36 MicroMessenger/8.0"
            ),
            referer="https://mp.weixin.qq.com/",
            accept_language="zh-CN,zh;q=0.9",
            browser_wait_selector="#js_content",
            needs_browser=False,
        )

    def parse(self, html: str) -> Dict[str, Any]:
        return naive_parse_wechat_html(html)

    def clean_url(self, url: str) -> str:
        return strip_tracking_params(url)

    def validate_url(self, url: str) -> bool:
        return is_public_wechat_article(url)
