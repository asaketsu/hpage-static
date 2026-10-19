---
title: Scrapling 竞品分析
date: 20260501
tags: [scraping, python, web-crawler, anti-bot, mcp, adaptive]
related: [[]]
---

# Scrapling — 自适应 Web Scraping 框架

## 项目画像

| 维度 | 信息 |
|------|------|
| 仓库 | github.com/D4Vinci/Scrapling |
| Stars | 39,376 ⭐ |
| Forks | 3,521 |
| 语言 | Python (100%) |
| 创建 | 2024-10-13 |
| 最近更新 | 2026-04-30 |
| 版本 | 0.4.7 |
| 许可证 | BSD-3-Clause |
| 作者 | Karim Shoair |
| 定位 | **一站式自适应爬虫框架** — 从单请求到全规模爬取，零妥协 |
| 一句话 | 解析器能学习网站变化自动重定位元素，Fetcher 绕过 Cloudflare，Spider 支持暂停/恢复/并发 |

## 核心架构

Scrapling 分三层架构：

### 1. Parser 层（自适应解析）
- 基于 lxml + cssselect，兼容 Scrapy/Parsel 的 `::text`/`::attr()` 伪元素语法
- **Adaptive 引擎**：核心创新点。首次抓取时 `auto_save=True` 保存元素特征签名（标签名、属性、文本、兄弟关系、父级路径），网站改版后 `adaptive=True` 用相似度算法自动重定位元素
- 性能：文本提取比 BS4 快 ~780x，与 Parsel/Scrapy 基本持平（2.02ms vs 2.04ms）
- 支持 CSS/XPath/BS4-style/find_by_text/regex 等多种选择器

### 2. Fetcher 层（三级抓取器）
| Fetcher | 场景 | 技术 |
|---------|------|------|
| Fetcher | 快速HTTP | curl_cffi TLS指纹伪装，HTTP/3 |
| DynamicFetcher | JS渲染 | Playwright Chromium/Chrome |
| StealthyFetcher | 反爬绕过 | patchright + 指纹欺骗，自动绕 Cloudflare Turnstile |

- 每个 Fetcher 都有 Session 版本（cookie/状态持久化）
- 全部支持 async（AsyncFetcherSession/AsyncStealthySession/AsyncDynamicSession）
- 内建 ProxyRotator（轮换策略可自定义）
- DNS-over-HTTPS 防泄漏，广告域名屏蔽（~3500个）

### 3. Spider 层（爬虫框架）
- Scrapy 风格 API：`start_urls` + `async parse()` + `yield`
- 并发控制（per-domain 限速）
- **多 Session**：一个 Spider 内同时用 HTTP + Stealthy 浏览器，按 URL 路由
- **暂停/恢复**：`crawldir` 检查点持久化，Ctrl+C 优雅停止
- **流式输出**：`async for item in spider.stream()` 实时消费
- robots.txt 合规、开发模式（磁盘缓存重放）
- 内建 JSON/JSONL 导出

### 4. AI 集成层
- **MCP Server**：10 个工具（get/bulk_get/fetch/bulk_fetch/stealthy_fetch/bulk_stealthy_fetch/screenshot/convert_html_to_markdown/extract_structured_data_from_html/extract_structured_data_from_url）
- 支持 bulk 并行抓取、结构化数据提取
- **Agent Skill**：OpenClaw 生态正式发布，含完整 examples + references
- CLI `--ai-targeted` 参数防止 prompt injection

### 5. 开发者体验
- 交互式 IPython Shell（`scrapling shell`）
- CLI 直接抓取无需写代码（`scrapling extract`）
- curl 转 Scrapling 请求
- 92% 测试覆盖率 + PyRight/MyPy 全量类型检查
- Docker 镜像（自动构建）
- ReadTheDocs 完整文档

## 亮点与不足

### ✅ 亮点
1. **Adaptive 解析** — 业界唯一的"学习型"解析器，网站改版自动适应，这是杀手级特性
2. **三级 Fetcher 统一接口** — HTTP/动态/隐身一套 API 切换，不需要学三套库
3. **Cloudflare 绕过零配置** — 不依赖第三方 solver，自动化绕过 Turnstile
4. **Spider 暂停/恢复** — 长任务不怕中断，生产级可靠性
5. **MCP + Agent Skill 双生态** — 同时支持 Claude/Cursor MCP 和 OpenClaw，AI Agent 直接用
6. **极致性能** — 解析速度与 Parsel 持平，远超 BS4（~780x）
7. **Lazy Import** — `__getattr__` 惰性加载，按需安装依赖

### 🔴 不足
1. **仅 Python** — 无 Node.js/Go 绑定，JS 生态无法直接用（🟡 非核心问题）
2. **Playwright 依赖重** — StealthyFetcher 需要 patchright + browserforge + 完整浏览器，安装体积大
3. **Adaptive 精度未公开** — 相似度算法细节未在 README 说明，复杂 DOM 变化可靠性存疑
4. **社区生态尚浅** — 虽 39k star，但 middleware/pipeline 生态远不如 Scrapy 丰富

## 可借鉴模式

| 模式 | 说明 | 新颖性 | 可移植性 | 优先级 |
|------|------|--------|---------|--------|
| Adaptive 解析 | 保存元素签名→相似度匹配→自动重定位 | ⭐⭐⭐ 极高 | 中，需实现相似度引擎 | 🔥 P1 |
| 三级 Fetcher 统一接口 | HTTP/Dynamic/Stealth 同 API | ⭐⭐ 中 | 高，可直接参考设计 | P2 |
| Lazy Import 模式 | `__getattr__` 按需加载减少依赖 | ⭐ 低 | 高 | P3 |
| Spider 暂停/恢复 | 检查点持久化 | ⭐⭐ 中 | 高，可借鉴到任务系统 | P2 |
| MCP Server 设计 | 10 工具覆盖抓取全链路 | ⭐ 低 | 高 | P3 |
| CLI 零代码抓取 | `scrapling extract` 直接出结果 | ⭐ 低 | 高 | P3 |

## 与我们关联

### 直接关联
- **web_extract/browser 工具增强**：Scrapling 的 MCP Server 是我们 web_extract 的直接竞品，它多了反爬绕过、结构化提取
- **ClawHub 生态**：Scrapling 已正式入驻 OpenClaw（clawhub.ai/D4Vinci/scrapling-official），说明 ClawHub 分发是趋势

### 可借鉴
1. **Adaptive 解析思路** — 我们 RAG 索引和文档处理可以借鉴"元素签名+相似度"模式，当文档格式变化时自动适配
2. **三级降级链** — web_extract → browser → stealthy 的降级策略与我们的 search-fallback-chain 思路一致，可参考其 Fetcher 分层设计
3. **Agent Skill 结构** — Scrapling 的 agent-skill 目录结构（SKILL.md + examples/ + references/）是很好的 Skill 组织范式

### 不应借鉴
- 不需要安装 Scrapling 本身（我们已有 web_extract + browser 工具）
- 不需要在服务器装 Playwright（体积太大，违背"不在本机运行代码"原则）

## 竞品定位

| 维度 | Scrapling | 我们的 web 工具 |
|------|-----------|----------------|
| 核心能力 | 自适应解析 + 反爬绕过 | 通用搜索/提取/浏览 |
| 反爬 | ⭐⭐⭐ Turnstile 绕过 | ⭐ 基础 browser |
| 解析 | ⭐⭐⭐ 自适应 | ⭐⭐ CSS/XPath |
| 生态 | Python 社区 | Hermes/ClawHub 生态 |
| AI 集成 | MCP Server | 内建工具 |
| 市场交叉 | AI Agent 抓取场景 | AI Agent 信息获取 |

**竞争壁垒**：Scrapling 在"专业爬虫"领域无可匹敌，但我们是"通用助手"定位，不直接竞争。它更像是一个可集成的专业工具。

## 预判

- **短期**（1-3月）：Scrapling 将成为 AI Agent 爬虫的默认选择，Star 冲 50k+
- **中期**（3-6月）：可能出现"Scrapling + LLM"的自动爬虫 Agent 产品
- **长期**（6月+）：反爬对抗升级后，Scrapling 需要持续维护指纹库，可持续性取决于社区贡献

---

*分析完成于 20260501 | 猫仔出品*


## 相关笔记
- [[2026-05-12-中文学术去AI味10步Skill框架]] (关键词: 框架)
