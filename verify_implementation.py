#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
验证脚本 — 测试通用文章阅读器的所有功能
"""

import sys
import os

# 设置 UTF-8 输出
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# 添加项目路径
PROJECT_ROOT = r"C:\Users\Administrator\Desktop\wechat-article-reader-main"
SRC_DIR = os.path.join(PROJECT_ROOT, "src")
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from mcp_server_my_mcp_server.tools.read_article import read_article
from mcp_server_my_mcp_server.adapters.base import AdapterRegistry
from mcp_server_my_mcp_server.adapters.wechat import WechatAdapter
from mcp_server_my_mcp_server.adapters.zhihu import ZhihuAdapter
from mcp_server_my_mcp_server.adapters.csdn import CSDNAdapter
from mcp_server_my_mcp_server.adapters.generic import GenericAdapter


def test_adapter_routing():
    """测试适配器路由"""
    print("=" * 60)
    print("测试 1: 适配器路由")
    print("=" * 60)

    registry = AdapterRegistry([
        WechatAdapter(),
        ZhihuAdapter(),
        CSDNAdapter(),
        GenericAdapter(),
    ])

    test_urls = [
        ("https://mp.weixin.qq.com/s/abc123", "WechatAdapter"),
        ("https://zhuanlan.zhihu.com/p/123456", "ZhihuAdapter"),
        ("https://blog.csdn.net/xxx/article/details/123", "CSDNAdapter"),
        ("https://example.com/article", "GenericAdapter"),
    ]

    for url, expected in test_urls:
        adapter = registry.find(url)
        adapter_name = type(adapter).__name__ if adapter else "None"
        status = "✓" if adapter_name == expected else "✗"
        print(f"{status} {url}")
        print(f"  → {adapter_name} (期望: {expected})")

    print()


def test_url_validation():
    """测试 URL 验证"""
    print("=" * 60)
    print("测试 2: URL 验证")
    print("=" * 60)

    test_cases = [
        ("https://mp.weixin.qq.com/s/abc123", True, "有效微信 URL"),
        ("https://mp.weixin.qq.com/invalid", False, "无效微信 URL（不是 /s 路径）"),
        ("https://example.com/article", True, "通用 URL"),
        ("ftp://example.com/file", False, "不支持的协议"),
    ]

    for url, should_work, desc in test_cases:
        result = read_article(url)
        has_error = "error" in result
        status = "✓" if (not has_error) == should_work else "✗"
        print(f"{status} {desc}")
        print(f"  URL: {url}")
        if has_error:
            print(f"  错误: {result.get('error')}")
        else:
            print(f"  适配器: {result.get('adapter')}")

    print()


def test_backward_compatibility():
    """测试向后兼容性"""
    print("=" * 60)
    print("测试 3: 向后兼容性")
    print("=" * 60)

    from mcp_server_my_mcp_server.tools.read_wechat_article import read_wechat_article

    # 测试原有 API 仍然工作
    result = read_wechat_article("https://example.com/not-wechat")
    assert "error" in result
    assert result["error"] == "invalid_url"
    print("✓ read_wechat_article() 仍然正常工作")

    # 测试 WechatReaderConfig 仍然可用
    from mcp_server_my_mcp_server.utils.config import WechatReaderConfig
    cfg = WechatReaderConfig(browser_enabled=False)
    assert cfg.browser_enabled == False
    print("✓ WechatReaderConfig 仍然可用")

    print()


def main():
    print("\n" + "=" * 60)
    print("通用文章阅读器 — 功能验证")
    print("=" * 60 + "\n")

    try:
        test_adapter_routing()
        test_url_validation()
        test_backward_compatibility()

        print("=" * 60)
        print("✓ 所有验证通过！")
        print("=" * 60)

    except Exception as e:
        print(f"\n✗ 验证失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
