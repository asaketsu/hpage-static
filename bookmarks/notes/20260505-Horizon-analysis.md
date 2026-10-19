　　Horizon 是一个 AI 驱动的个人新闻雷达系统，由 Thysrael 于 2026 年 2 月创建，截至分析日已获得 1606 Stars、248 Forks。项目以 MIT 协议开源，使用 Python 编写，核心代码约 7270 行，测试代码 2142 行。项目定位为「构建你专属的 AI 新闻雷达」，从 Hacker News、Reddit、RSS、Telegram、Twitter、GitHub 六大来源抓取内容，经去重、AI 评分、背景丰富化后生成双语（中英文）日报，推送到 GitHub Pages、邮件、Webhook（飞书/钉钉/Slack/Discord）和 MCP 服务。

## 项目画像

| 维度 | 详情 |
|------|------|
| 仓库 | github.com/Thysrael/Horizon |
| Stars | 1606（增长极快，3个月） |
| 语言 | Python 99.5% |
| 许可 | MIT |
| 创建 | 2026-02-20 |
| 维护者 | Thysrael（个人开发者） |
| 依赖 | httpx, anthropic, openai, google-genai, pydantic, tenacity, ddgs, mcp, rich |
| 官网 | horizon1123.top |

## 核心架构

Horizon 采用清晰的异步流水线架构，核心编排器 `HorizonOrchestrator.run()` 按以下顺序执行：

**Fetch（抓取）**：六个独立的异步 Scraper（RSS/HN/Reddit/Telegram/Twitter/GitHub）并发拉取内容，统一为 `ContentItem` Pydantic 模型。每个 Scraper 继承自 `BaseScraper` 抽象基类，接收共享的 `httpx.AsyncClient`。

**Dedup（去重）**：先做基于 URL 的跨源去重（`merge_cross_source_duplicates`），再做基于 AI 的语义主题去重（`merge_topic_duplicates`），用 LLM 判断多条新闻是否报道同一事件。

**Score & Filter（评分过滤）**：AI 对每条内容评分（0-10），基于技术深度、新颖性、影响力、社区参与度等因素。低于阈值（默认 6.0）的过滤掉。评分提示词精心设计，区分 Groundbreaking/High Value/Interesting/Low Priority/Noise 五档。

**Enrich（丰富化）**：对高分内容进行第二遍 AI 处理。先用 DuckDuckGo 搜索相关背景，再让 AI 提取关键概念并生成背景知识，添加社区讨论摘要。

**Summarize（摘要）**：生成结构化的 Markdown 日报，包含概述、每条新闻的详细摘要、背景分析和讨论。支持中英双语，中文输出经过 pangu.py 自动添加盘古之白（中英文间空格）。

**Deliver（推送）**：支持 GitHub Pages（Jekyll）、邮件（SMTP/IMAP 自动订阅退订）、Webhook（飞书卡片/钉钉/Slack/Discord/通用 JSON）和 MCP 服务四种推送渠道。

## 技术栈评价

**优点**：全面异步（httpx + asyncio），Pydantic v2 强类型配置验证，tenacity 重试策略，rich 美化终端输出，DuckDuckGo 免费搜索，MCP 协议集成。代码结构清晰，模块职责分明。

**不足**：Twitter 依赖 Apify 付费服务（🟡 中度），GitHub Actions 的 daily-summary.yml 直接用 yml 执行完整流水线导致 Action 日志超长（🟡 轻度），单维护者风险（🔴 严重），无缓存层每次全量抓取（🟡 中度）。

## 亮点与不足

**亮点**：

一、多遍 AI 处理管线。不是简单调用一次 AI 摘要，而是分三遍（评分→去重→丰富化），每遍有不同的系统提示词和目标。这种分阶段设计让 AI 的每次调用都有明确的单一职责，输出质量更可控。

二、语义去重机制。URL 去重只解决完全相同的链接，Horizon 还用 LLM 判断多条不同来源的新闻是否在报道同一事件（如「Gemma 4 发布」在 HN 和 Reddit 同时出现），这在实际使用中非常有价值。

三、MCP 服务集成。将整个管线暴露为 MCP 工具（hz_fetch_items, hz_score_items, hz_filter_items 等），其他 Agent 可以像调用函数一样调用 Horizon 的各阶段。这是面向 AI Agent 生态的正确姿势。

四、飞书卡片模板。Webhook 配置支持飞书卡片格式（schema 2.0），内置 Markdown 和可折叠两种布局，直接对接飞书 Bot 而不需要额外适配。

五、Setup Wizard。交互式配置向导，用 Rich 库做终端 UI，支持预设模板匹配（用户输入兴趣关键词自动推荐源配置），降低新用户上手门槛。

**不足**：

一、单维护者瓶颈（🔴 严重）。0 open issues 不代表健康，可能意味着 issue 处理不过来或社区参与度低。248 fork 但只有 2 个 watcher，说明大量 fork 是收藏性质的。

二、无增量缓存（🟡 中度）。每次运行都全量抓取所有源，没有历史数据的增量比对机制。对于高频更新的源（如 HN），大量内容是重复的。

三、AI 调用成本不可控（🟡 中度）。每个内容项至少调用一次 AI（评分），高分项调用两次（+丰富化），去重再调用一次。如果源配置较多，每日 AI 调用量可能很高。

## 可借鉴模式

| 模式 | 说明 | 新颖性 | 可移植性 | 优先级 |
|------|------|--------|---------|--------|
| 多遍 AI 管线 | 分阶段处理：评分→去重→丰富化，每遍单一职责 | 中（我们 news-aggregator 是单遍） | 高 | ⭐⭐⭐ |
| 语义去重 | LLM 判断多源同主题新闻，避免重复推送 | 高（我们无此能力） | 高 | ⭐⭐⭐ |
| MCP 工具暴露 | 将管线各阶段封装为 MCP tool，供 Agent 编排 | 高（我们 MCP 使用较少） | 高 | ⭐⭐ |
| Pydantic 强类型配置 | config.json 用 Pydantic 模型验证，运行前捕获配置错误 | 低（我们已有 Pydantic 惯例） | 中 | ⭐ |
| Webhook 平台模板 | 飞书/钉钉/Slack/Discord 各有专用推送模板 | 中（我们飞书推送较粗糙） | 高 | ⭐⭐ |
| 双语管线 | 同一数据源一次处理输出中英两版摘要 | 中 | 中 | ⭐ |

## 与我们的关联

**直接关联**：Horizon 的功能与我们的 news-aggregator skill 高度重叠。我们也有新闻抓取→推送的流程，但缺乏多遍 AI 处理和语义去重。Horizon 的飞书 Webhook 模板可以直接参考改进我们的推送格式。

**可借鉴**：语义去重模式可以融入 news-aggregator skill，提升推送质量。多遍 AI 管线思路可以用于我们任何需要 LLM 质量把关的场景（如笔记加工、竞品分析）。

**不应借鉴**：Apify 付费 Twitter 抓取、邮件订阅系统、GitHub Pages 部署方案。这些要么有成本，要么与我们的技术栈不符。

## 竞品定位

Horizon 定位在「个人新闻雷达」赛道，与我们 jbot 的新闻聚合功能直接竞争。但 Horizon 是独立工具，需要用户自行部署和维护；jbot 是嵌入在对话式 Agent 中的能力，用户零配置即用。

**我们的优势**：对话式交互、多模态（语音/图片）、已有 AutoCLI 55+ 站点覆盖、cron 自动化。

**Horizon 的优势**：管线设计更精细（多遍 AI、语义去重）、MCP 集成、双语输出、飞书卡片原生支持。

## 预判

**短期**（1-3月）：Horizon 会继续快速增长，中文开发者社区关注度高（HelloGitHub 推荐）。MCP 集成是差异化亮点。

**中期**（3-6月）：可能遇到单维护者瓶颈，PR 积压、功能迭代放缓。社区可能会 fork 出增强版。

**长期**（6月+）：如果维护者持续投入，有望成为个人新闻聚合领域的标准工具之一。如果停滞，其架构模式（多遍 AI 管线、语义去重）会被其他项目借鉴吸收。


## 相关笔记
- [[2026-05-02-SkillClaw-analysis]] (关键词: analysis)
- [[stock-analysis-system]] (关键词: analysis)
- [[2026-05-06-lewislulu-html-ppt-skill-analysis]] (关键词: analysis)
