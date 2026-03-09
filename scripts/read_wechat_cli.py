import sys
import json
import os


def ensure_path():
    # add project src to sys.path
    here = os.path.dirname(os.path.abspath(__file__))
    root = os.path.dirname(here)
    src = os.path.join(root, "src")
    if src not in sys.path:
        sys.path.insert(0, src)


def main():
    ensure_path()
    from mcp_server_my_mcp_server.tools.read_wechat_article import read_wechat_article
    from mcp_server_my_mcp_server.utils.config import WechatReaderConfig

    if len(sys.argv) < 2:
        print("Usage: python read_wechat_cli.py <wechat_article_url> [--no-images] [--no-browser]", file=sys.stderr)
        sys.exit(1)

    url = sys.argv[1]
    include_images = True
    browser_enabled = True
    if "--no-images" in sys.argv[2:]:
        include_images = False
    if "--no-browser" in sys.argv[2:]:
        browser_enabled = False

    cfg = WechatReaderConfig(browser_enabled=browser_enabled)
    res = read_wechat_article(url, include_images=include_images, config=cfg)
    print(json.dumps(res, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()