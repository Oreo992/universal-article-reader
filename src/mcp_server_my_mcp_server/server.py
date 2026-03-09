"""
Server registration stub.

Depending on your MCP runtime, import and register tools here.
This module demonstrates exposing read_wechat_article and read_article as callables.
"""

from typing import Dict, Any

from .tools.read_wechat_article import read_wechat_article
from .tools.read_article import read_article


def list_tools() -> Dict[str, Any]:
    """Return tool metadata map that an MCP runtime can use to register."""
    return {
        "read_wechat_article": {
            "func": read_wechat_article,
            "description": "读取公开的微信公众号文章，返回Markdown与结构化元数据。",
            "inputs": {
                "url": {"type": "string", "required": True},
                "include_images": {"type": "boolean", "required": False, "default": True},
                "force_browser": {"type": "boolean", "required": False, "default": False},
            },
        },
        "read_article": {
            "func": read_article,
            "description": "读取任意支持站点的文章（微信、知乎、CSDN、简书、掘金、博客园、Medium及通用网页），返回Markdown与结构化元数据。",
            "inputs": {
                "url": {"type": "string", "required": True},
                "include_images": {"type": "boolean", "required": False, "default": True},
                "force_browser": {"type": "boolean", "required": False, "default": False},
            },
        },
    }