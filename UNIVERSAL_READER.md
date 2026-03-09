# Universal Article Reader — 通用文章阅读器

从多个站点读取文章，返回结构化 Markdown 内容和元数据。

## 支持的站点

| 站点 | 域名 | 适配器 | 需要浏览器 |
|------|------|--------|-----------|
| 微信公众号 | mp.weixin.qq.com | WechatAdapter | 可选（回退） |
| 知乎 | zhihu.com / zhuanlan.zhihu.com | ZhihuAdapter | 是 |
| CSDN | blog.csdn.net | CSDNAdapter | 否 |
| 简书 | jianshu.com | JianshuAdapter | 否 |
| 掘金 | juejin.cn | JuejinAdapter | 是 (SPA) |
| 博客园 | cnblogs.com | CnblogsAdapter | 否 |
| Medium | medium.com | MediumAdapter | 可选 |
| 通用网页 | 任意 HTTP/HTTPS | GenericAdapter | 否 |

## 快速开始

### 安装

```bash
cd C:\Users\Administrator\Desktop\wechat-article-reader-main
pip install -e .           # 基础安装
pip install -e .[browser]  # 含浏览器支持（推荐）
pip install -e .[mcp]      # 含 MCP 服务器
```

### CLI 使用

```bash
# 通用阅读器（自动识别站点）
read-article-cli https://zhuanlan.zhihu.com/p/123456
read-article-cli https://blog.csdn.net/xxx/article/details/123
read-article-cli https://mp.weixin.qq.com/s/xxx

# 仅微信（向后兼容）
read-wechat-cli https://mp.weixin.qq.com/s/xxx --include-images
```

### Python API

```python
from mcp_server_my_mcp_server.tools.read_article import read_article

result = read_article("https://blog.csdn.net/xxx/article/details/123")
print(result["title"])
print(result["content_md"])
print(result["adapter"])  # "CSDNAdapter"
```

### MCP Tool

启动 MCP 服务器：

```bash
wechat-mcp-http
```

调用 `read_article` tool：

```json
{
  "url": "https://zhuanlan.zhihu.com/p/123456",
  "include_images": true,
  "force_browser": false
}
```

## 返回格式

```json
{
  "title": "文章标题",
  "author": "作者",
  "pub_time": "发布时间",
  "content_md": "Markdown 正文",
  "images": ["图片URL列表"],
  "links": ["链接列表"],
  "source_url": "清理后的源URL",
  "adapter": "WechatAdapter",
  "strategy": "http",
  "logs": {}
}
```

## 架构

### 站点适配器模式

```
SiteAdapter (ABC)
├── WechatAdapter        # mp.weixin.qq.com
├── ZhihuAdapter         # zhihu.com
├── CSDNAdapter          # csdn.net
├── JianshuAdapter       # jianshu.com
├── JuejinAdapter        # juejin.cn
├── CnblogsAdapter       # cnblogs.com
├── MediumAdapter        # medium.com
└── GenericAdapter       # 兜底通用提取
```

`AdapterRegistry` 按注册顺序逐个调用 `match(url)`，返回第一个匹配的适配器。

### 关键模块

- `adapters/` — 站点适配器
- `tools/read_article.py` — 通用阅读器
- `tools/read_wechat_article.py` — 微信专用（向后兼容）
- `utils/` — HTTP/浏览器获取、解析、缓存、限流

## 测试

```bash
# 运行所有测试
python -m pytest tests/ -v

# 运行特定测试
python -m pytest tests/test_adapters/test_registry.py -v
python -m pytest tests/test_adapters/test_wechat_adapter.py -v
```

## Claude Code Skill

已创建 Skill：`universal-article-reader`

位置：`C:\Users\Administrator\.claude\skills\universal-article-reader\`

使用：在 Claude Code 中直接调用该 Skill 来读取任意支持站点的文章。

## 向后兼容

- 原有 `read-wechat-cli` 命令完全保留
- 原有 `read_wechat_article` MCP tool 完全保留
- 原有 Python API 完全保留
- 所有现有测试通过

## License

MIT
