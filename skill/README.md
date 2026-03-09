# Universal Article Reader - Claude Code Skill

这是一个 Claude Code Skill，可以让 Claude 读取多个站点的文章并返回结构化 Markdown 内容。

## 支持的站点

- 微信公众号 (mp.weixin.qq.com)
- 知乎 (zhihu.com)
- CSDN (csdn.net)
- 简书 (jianshu.com)
- 掘金 (juejin.cn)
- 博客园 (cnblogs.com)
- Medium (medium.com)
- 任意网页（通用适配器）

## 安装方法

### Windows
```bash
xcopy /E /I skill "%USERPROFILE%\.claude\skills\universal-article-reader"
```

### macOS/Linux
```bash
cp -r skill/ ~/.claude/skills/universal-article-reader/
```

## 使用方法

安装后，在 Claude Code 中可以：

1. 直接调用 Skill：
   ```
   /universal-article-reader
   ```

2. 或者让 Claude 自动识别并使用

## 依赖

需要先安装主项目：

```bash
cd ..
pip install -e .           # 基础安装
pip install -e .[browser]  # 含浏览器支持（推荐）
```

## 项目地址

完整项目：https://github.com/Oreo992/universal-article-reader
