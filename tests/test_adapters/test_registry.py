"""Test adapter registry and URL routing."""

from mcp_server_my_mcp_server.adapters.base import AdapterRegistry
from mcp_server_my_mcp_server.adapters.wechat import WechatAdapter
from mcp_server_my_mcp_server.adapters.zhihu import ZhihuAdapter
from mcp_server_my_mcp_server.adapters.csdn import CSDNAdapter
from mcp_server_my_mcp_server.adapters.generic import GenericAdapter


def test_registry_wechat():
    registry = AdapterRegistry([WechatAdapter(), GenericAdapter()])
    adapter = registry.find("https://mp.weixin.qq.com/s/abc123")
    assert adapter is not None
    assert isinstance(adapter, WechatAdapter)


def test_registry_zhihu():
    registry = AdapterRegistry([WechatAdapter(), ZhihuAdapter(), GenericAdapter()])
    adapter = registry.find("https://zhuanlan.zhihu.com/p/123456")
    assert adapter is not None
    assert isinstance(adapter, ZhihuAdapter)


def test_registry_csdn():
    registry = AdapterRegistry([CSDNAdapter(), GenericAdapter()])
    adapter = registry.find("https://blog.csdn.net/user/article/details/123")
    assert adapter is not None
    assert isinstance(adapter, CSDNAdapter)


def test_registry_generic_fallback():
    registry = AdapterRegistry([WechatAdapter(), GenericAdapter()])
    adapter = registry.find("https://example.com/article")
    assert adapter is not None
    assert isinstance(adapter, GenericAdapter)


def test_registry_no_match():
    registry = AdapterRegistry([WechatAdapter()])
    adapter = registry.find("https://example.com/article")
    assert adapter is None
