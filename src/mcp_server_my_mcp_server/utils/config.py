from dataclasses import dataclass
from typing import Optional


@dataclass
class ReaderConfig:
    """
    Universal article reader configuration.

    - timeout_seconds: request timeout
    - rate_limit_per_min: max requests per minute (per instance)
    - burst: burst capacity for token bucket
    - proxy: optional HTTP/HTTPS proxy
    - cache_ttl_seconds: TTL for content cache
    - browser_enabled: whether to enable headless browser
    """

    timeout_seconds: int = 15
    rate_limit_per_min: int = 30
    burst: int = 5
    proxy: Optional[str] = None
    cache_ttl_seconds: int = 24 * 3600
    browser_enabled: bool = True


@dataclass
class WechatReaderConfig:
    """
    Configuration for WeChat article reader.

    - ua: User-Agent string (should include MicroMessenger to increase success rate)
    - referer: HTTP Referer header (mp.weixin.qq.com)
    - accept_language: Accept-Language header
    - timeout_seconds: request timeout
    - rate_limit_per_min: max requests per minute (per instance)
    - burst: burst capacity for token bucket
    - proxy: optional HTTP/HTTPS proxy (e.g., http://127.0.0.1:7890)
    - cache_ttl_seconds: TTL for content cache
    - download_assets: whether to download assets (images) for stable access
    - browser_enabled: whether to enable headless browser fallback
    """

    ua: str = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/116.0 Safari/537.36 MicroMessenger/8.0"
    )
    referer: str = "https://mp.weixin.qq.com/"
    accept_language: str = "zh-CN,zh;q=0.9"
    timeout_seconds: int = 15
    rate_limit_per_min: int = 30
    burst: int = 5
    proxy: Optional[str] = None
    cache_ttl_seconds: int = 24 * 3600
    download_assets: bool = False
    browser_enabled: bool = True