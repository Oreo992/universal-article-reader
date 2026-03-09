# 支持站点详情

## 1. 微信公众号 (WechatAdapter)

- **域名**: `mp.weixin.qq.com`
- **路径**: `/s/...` 或 `/s?__biz=...`
- **内容选择器**: `#js_content`
- **浏览器**: 可选（HTTP 失败时回退）
- **特殊处理**: 清理跟踪参数 (chksm, scene, utm_*)；处理懒加载图片属性 (data-src, data-original)
- **User-Agent**: 包含 `MicroMessenger/8.0` 以提高成功率

## 2. 知乎 (ZhihuAdapter)

- **域名**: `zhihu.com`, `www.zhihu.com`, `zhuanlan.zhihu.com`
- **内容选择器**: `.Post-RichTextContainer` / `.RichContent-inner`
- **浏览器**: 是（页面依赖 JS 渲染）
- **特殊处理**: 提取 data-original, data-actualsrc 图片属性

## 3. CSDN (CSDNAdapter)

- **域名**: `*.csdn.net`
- **内容选择器**: `#content_views`
- **浏览器**: 否
- **特殊处理**: 无

## 4. 简书 (JianshuAdapter)

- **域名**: `jianshu.com`, `www.jianshu.com`
- **内容选择器**: `<article>` / `.show-content`
- **浏览器**: 否
- **特殊处理**: 提取 data-original-src 图片属性

## 5. 掘金 (JuejinAdapter)

- **域名**: `juejin.cn`, `www.juejin.cn`
- **内容选择器**: `.article-content`
- **浏览器**: 是（SPA 应用，需要 JS 渲染）
- **特殊处理**: 无

## 6. 博客园 (CnblogsAdapter)

- **域名**: `*.cnblogs.com`
- **内容选择器**: `#cnblogs_post_body`
- **浏览器**: 否
- **特殊处理**: 无

## 7. Medium (MediumAdapter)

- **域名**: `medium.com`, `*.medium.com`
- **内容选择器**: `<article>`
- **浏览器**: 可选
- **特殊处理**: 提取 JSON-LD 中的 datePublished 和 author

## 8. 通用网页 (GenericAdapter)

- **域名**: 任意 HTTP/HTTPS URL
- **内容选择器**: `<article>` → `<main>` → `<body>`（按优先级回退）
- **浏览器**: 否
- **特殊处理**: 清理 utm_* 跟踪参数；提取 og:title, JSON-LD 元数据
