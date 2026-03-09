---
name: universal-article-reader
description: 通用文章阅读器 — 从任意支持站点抓取文章并返回结构化 Markdown
version: 1.0.0
tags: [article, reader, markdown, scraper, mcp]
---

# Universal Article Reader

从多个站点读取文章，返回结构化 Markdown 内容和元数据。

## 支持的站点

| 站点 | 域名 | 需要浏览器 |
|------|------|-----------|
| 微信公众号 | mp.weixin.qq.com | 可选（回退） |
| 知乎 | zhihu.com / zhuanlan.zhihu.com | 是 |
| CSDN | blog.csdn.net | 否 |
| 简书 | jianshu.com | 否 |
| 掘金 | juejin.cn | 是 (SPA) |
| 博客园 | cnblogs.com | 否 |
| Medium | medium.com | 可选 |
| 通用网页 | 任意 HTTP/HTTPS | 否 |

## 使用方式

### CLI

```bash
# 通用阅读器（自动识别站点）
read-article-cli <URL> [--no-browser] [--force-browser] [--no-images]

# 仅微信（向后兼容）
read-wechat-cli <URL> [--no-browser] [--force-browser] [--include-images]
```

### MCP Tool

通过 MCP 服务器调用 `read_article` tool：

```json
{
  "url": "https://zhuanlan.zhihu.com/p/123456",
  "include_images": true,
  "force_browser": false
}
```

### Python API

```python
from mcp_server_my_mcp_server.tools.read_article import read_article

result = read_article("https://blog.csdn.net/xxx/article/details/123")
print(result["title"])
print(result["content_md"])
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

## 项目路径

`C:\Users\Administrator\Desktop\wechat-article-reader-main`

## 安装

```bash
cd C:\Users\Administrator\Desktop\wechat-article-reader-main
pip install -e .           # 基础安装
pip install -e .[browser]  # 含浏览器支持
pip install -e .[mcp]      # 含 MCP 服务器
```
