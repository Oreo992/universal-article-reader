import argparse
import json
from typing import Any, Dict

from .tools.read_wechat_article import read_wechat_article
from .tools.read_article import read_article
from .utils.config import WechatReaderConfig, ReaderConfig


def main() -> None:
    """CLI entry point for WeChat-only reader (backward compatible)."""
    parser = argparse.ArgumentParser(
        description="Read a public WeChat article and output structured Markdown JSON"
    )
    parser.add_argument("url", help="WeChat article URL, e.g. https://mp.weixin.qq.com/s/...")
    parser.add_argument(
        "--include-images",
        action="store_true",
        help="Include image URLs in the output (default off)",
    )
    parser.add_argument(
        "--no-browser",
        action="store_true",
        help="Disable browser fallback and use HTTP-only fetching",
    )
    parser.add_argument(
        "--force-browser",
        action="store_true",
        help="Force browser rendering even if HTTP succeeds (better image extraction)",
    )
    args = parser.parse_args()

    # Respect --no-browser flag by constructing config accordingly
    cfg = WechatReaderConfig(browser_enabled=not args.no_browser)
    result: Dict[str, Any] = read_wechat_article(
        url=args.url,
        include_images=args.include_images,
        force_browser=args.force_browser,
        config=cfg,
    )

    print(json.dumps(result, ensure_ascii=False, indent=2))


def main_universal() -> None:
    """CLI entry point for the universal article reader."""
    parser = argparse.ArgumentParser(
        description="Read an article from any supported site and output structured Markdown JSON"
    )
    parser.add_argument("url", help="Article URL (WeChat, Zhihu, CSDN, Jianshu, Juejin, Cnblogs, Medium, or any web page)")
    parser.add_argument(
        "--include-images",
        action="store_true",
        default=True,
        help="Include image URLs in the output (default on)",
    )
    parser.add_argument(
        "--no-images",
        action="store_true",
        help="Exclude image URLs from the output",
    )
    parser.add_argument(
        "--no-browser",
        action="store_true",
        help="Disable browser fallback and use HTTP-only fetching",
    )
    parser.add_argument(
        "--force-browser",
        action="store_true",
        help="Force browser rendering even if HTTP succeeds",
    )
    args = parser.parse_args()

    include_images = not args.no_images
    cfg = ReaderConfig(browser_enabled=not args.no_browser)
    result: Dict[str, Any] = read_article(
        url=args.url,
        include_images=include_images,
        force_browser=args.force_browser,
        config=cfg,
    )

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()