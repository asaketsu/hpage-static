---
title: Obscura 竞品分析
date: 2026-05-01
tags: [headless-browser, rust, web-scraping, anti-detection, 竞品分析]
status: active
---

# Obscura — 开源轻量级无头浏览器（Rust）

## 一、项目画像

| 维度 | 信息 |
|------|------|
| 仓库 | h4ckf0r0day/obscura |
| Stars | **8,770 ⭐** / 549 Forks |
| 语言 | Rust |
| 创建 | 2026-04-13（18 天前） |
| 最新版 | v0.1.1 (2026-04-25) |
| 许可 | Apache 2.0 |
| 定位 | 面向 AI Agent 和爬虫的开源无头浏览器引擎 |

**一句话：** Rust 写的轻量级无头浏览器，替代 headless Chrome，内存 30MB vs Chrome 200MB+，内置反指纹和 tracker 屏蔽。

## 二、核心卖点

### 对比 headless Chrome

| 指标 | Obscura | Headless Chrome |
|------|---------|----------------|
| 内存 | **30 MB** | 200+ MB |
| 二进制大小 | **70 MB** | 300+ MB |
| 反检测 | **内置** | 无 |
| 页面加载 | **85 ms** | ~500 ms |
| 启动 | **即时** | ~2s |
| Puppeteer | ✅ | ✅ |
| Playwright | ✅ | ✅ |

**关键：** 通过 CDP（Chrome DevTools Protocol）兼容 Puppeteer/Playwright，迁移成本接近零。

## 三、技术架构

### 3.1 能力矩阵

| 能力 | 实现方式 |
|------|---------|
| JS 执行 | 内嵌 V8 引擎 |
| 浏览器协议 | CDP 完整实现 |
| 反指纹 | per-session 随机化（GPU/screen/canvas/audio/battery） |
| Tracker 屏蔽 | 3,520 域名黑名单，含分析/广告/遥测/指纹 |
| 并发爬取 | 多 worker 进程 + 可配置并发数 |
| 代理 | HTTP/SOCKS5 |
| 输出格式 | HTML / text / links / JSON / Markdown |

### 3.2 CDP 支持范围

| 域 | 方法 |
|----|------|
| Target | create/close/attach/createContext |
| Page | navigate/frameTree/lifecycleEvents |
| Runtime | evaluate/callFunctionOn/getProperties |
| DOM | getDocument/querySelector/getOuterHTML |
| Network | cookies/headers/userAgent |
| Fetch | enable/continue/fulfill/fail（实时拦截） |
| Input | mouse/key dispatch |
| LP | **getMarkdown**（DOM→Markdown 转换）← 独特 |

### 3.3 CLI 命令

```bash
obscura serve --port 9222 --stealth     # CDP 服务器
obscura fetch <URL> --eval "..."        # 单页抓取+JS执行
obscura scrape url1 url2 --concurrency 25 --format json  # 批量并行
```

## 四、深度分析

### 4.1 为什么能这么快？

- Rust 零成本抽象 + 无 GC 暂停
- 不渲染 GUI（纯 headless，不需要 compositor）
- V8 编译后缓存（首次 ~5min，后续秒级）
- 精简渲染管线：不做布局/绘制，只执行 JS + 提取 DOM

### 4.2 反检测体系（Stealth Mode）

这是 Obscura 最有竞争力的部分：

- `navigator.webdriver = undefined`（Chrome 默认 true）
- GPU/WebGL 指纹随机化
- Canvas 指纹随机化
- AudioContext 指纹随机化
- `Function.prototype.toString()` 返回 `[native code]`
- `event.isTrusted = true`
- 隐藏内部属性（`Object.keys(window)` 安全）
- 3,520 tracker 域名直接屏蔽（不加载）

### 4.3 独特的 LP Domain

CDP 里有一个 `LP.getMarkdown` 方法——直接把 DOM 转成 Markdown。这个对 AI Agent 场景特别有价值：抓完网页直接拿 Markdown 喂 LLM，不需要额外的 html-to-markdown 转换步骤。

## 五、与我方的关联（三档分析）

### 第一档：有利进化 → 立刻落实

**无。** Obscura 是一个独立的浏览器引擎，不在我们的技术栈路径上。我们的 browser 工具已经由 Hermes 内置。

### 第二档：有价值 → 记录备用

1. **反检测思路** — 如果未来需要绕过网站反爬（如竞品监控、数据采集），Obscura 的反指纹策略清单（7 层）是很好的参考。记入 memory。
2. **CDP.getMarkdown** — DOM 直接转 Markdown 的思路，如果需要优化 web_extract 的输出质量，值得关注。
3. **并行爬取模式** — `--concurrency 25` + worker 进程的模式，批量抓取场景可参考。

### 第三档：知识库内容

- Rust + V8 的无头浏览器架构
- CDP 协议兼容设计
- Tracker 黑名单维护
- 性能优化手法

## 六、竞品格局

Obscura 处于一个快速升温的赛道：

| 竞品 | 定位 | Obscura 的差异 |
|------|------|---------------|
| Headless Chrome | 通用浏览器 | Obscura 专攻自动化，轻 7x |
| Playwright | 测试框架 | Obscura 是底层引擎 |
| Puppeteer | Chrome 自动化 | Obscura 兼容其协议 |
| Crawl4AI | AI 爬虫框架 | Obscura 更底层 |
| Firecrawl | 网页转 API | Obscura 是引擎不是服务 |

**8,770 星 / 18 天** = 增长速度惊人，说明 AI Agent + 网页交互的需求爆发。

## 七、预判

1. **短期：** 会成为 AI Agent 生态的标准浏览器引擎之一（类似 Crawl4AI 之于爬虫）
2. **中期：** 会被 AI Agent 框架（LangChain、CrewAI 等）集成
3. **长期：** 可能出现云托管版（类似 Browserbase），Obscura 做底层引擎

## 八、关联笔记

- [[DeepSeek Agent 生态]] — Agent 工具链中的浏览器层
- [垂域模型](垂域模型.md) — 反指纹技术是安全领域的垂域能力


## 相关笔记
- [Scrapling — 自适应 Web Scraping 框架](20260501-scrapling-analysis.md)
