from typing import Dict, Any
import os

try:
    from fastmcp import FastMCP
except Exception as e:  # pragma: no cover
    FastMCP = None  # type: ignore

from .tools.read_wechat_article import read_wechat_article
from .tools.read_article import read_article


def build_server() -> "FastMCP":
    if FastMCP is None:
        raise RuntimeError("fastmcp is not installed. Please install with: uv pip install -e ./your-mcp-project[mcp]")
    # Use a consistent MCP server identifier to match README examples
    mcp = FastMCP("wechat-article-reader")

    @mcp.tool
    def read_wechat_article_tool(url: str, include_images: bool = True, force_browser: bool = False) -> Dict[str, Any]:
        """Read a public WeChat article and return structured Markdown JSON"""
        return read_wechat_article(url=url, include_images=include_images, force_browser=force_browser)

    @mcp.tool
    def read_article_tool(url: str, include_images: bool = True, force_browser: bool = False) -> Dict[str, Any]:
        """Read an article from any supported site (WeChat, Zhihu, CSDN, Jianshu, Juejin, Cnblogs, Medium, or generic) and return structured Markdown JSON"""
        return read_article(url=url, include_images=include_images, force_browser=force_browser)

    return mcp


def main() -> None:
    mcp = build_server()
    # Expose HTTP transport at /mcp/ (default path by FastMCP)
    # You can adjust host/port via environment variables or here directly.
    host = os.getenv("MCP_HTTP_HOST", "127.0.0.1")
    try:
        port = int(os.getenv("MCP_HTTP_PORT", "8000"))
    except Exception:
        port = 8000
    mcp.run(transport="http", host=host, port=port)


if __name__ == "__main__":
    main()