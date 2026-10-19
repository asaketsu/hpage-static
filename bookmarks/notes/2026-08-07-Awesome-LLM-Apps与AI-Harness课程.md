# Awesome LLM Apps + AI Harness 课程 — 100+ Agent 模板库 & 全栈 Agent 工程教程

> **来源 1**：[github.com/Shubhamsaboo/awesome-llm-apps](https://github.com/Shubhamsaboo/awesome-llm-apps) — 131K⭐ Apache-2.0
> **来源 2**：[xueai.app/slides](https://xueai.app/slides/home.en.html) — Luo Xiaoshan (罗小山) AI Harness 课程

---

## 第一部分：Awesome LLM Apps — 100+ 开源 AI Agent 模板库

### 基本信息

| 项目 | 详情 |
|------|------|
| **Stars** | 131,108 (GitHub Top 级别) |
| **Forks** | 19,330 |
| **License** | Apache-2.0（Fork it, ship it, sell it） |
| **语言** | Python |
| **定位** | 100+ AI Agents, Agent Skills 和 RAG Apps，免费开源 |
| **兼容模型** | Claude / Gemini / GPT / DeepSeek / Llama / Qwen |
| **附属** | [Unwind AI](https://www.theunwindai.com) 教程站 |

### 模板分类矩阵

#### 🧩 Agent Skills — 给编码 Agent 新能力

一条命令安装，自然语言使用。支持 Claude Code / Codex / Cursor。

| Skill | 功能 |
|-------|------|
| **Project Graveyard** | 找出你放弃的副业项目，分析死因，推荐值得回归的 |
| **Scope Creep Detector** | 检查 diff 是否超出原始意图 |
| **Commit Archaeologist** | 从引入提交重建代码区域的意图 |
| **Dependency Doctor** | 检查依赖清单（过时/重复/安全） |
| **Advisor Orchestrator Worker** | Meta Loop：Claude Fable 5 顾问→GPT-5.6 编排→Gemini 3.5 Flash 执行 |
| **Self-Improving Agent Skills** | 用 Gemini + ADK 自动优化 Agent 技能（与 SkillOpt 同类） |

#### 🌱 Starter AI Agents — 单文件入门级

| Agent | 场景 |
|-------|------|
| Blog to Podcast | 博客 URL → 播客 |
| Breakup Recovery | 分手恢复 Agent 团队 |
| Data Analysis | CSV/Excel 自然语言问答 |
| Medical Imaging | X 光诊断 (Gemini) |
| Meme Generator | 驱动真实浏览器做表情包 |
| Music Generator | Prompt → MP3 |
| Travel Agent | 个性化行程 |
| Multimodal Agent | 视频+搜索 |
| Mixture of Agents | 多 LLM 回答+聚合 |
| xAI Finance | Grok 驱动实时股票 |
| OpenAI Research | 多 Agent 主题研究 |

#### 🚀 Advanced AI Agents — 生产级

| Agent | 特色 |
|-------|------|
| Home Renovation | 空间照片→装修计划+渲染图 |
| DevPulse AI | 多 Agent 信号情报聚合 |
| Deep Research | OpenAI SDK + Firecrawl |
| VC Due Diligence | 多 Agent 投资分析 |
| System Architect | DeepSeek R1 架构评审 + Claude |
| Self-Evolving Agent | EvoAgentX 重写自己的工作流 |
| Fraud Investigation | 公开记录交叉验证 |
| Trust-Gated Agent Team | 每个 Agent 被验证，每个操作有 hash 链审计 |

#### 🛰️ Always-on Agents — 后台值守

| Agent | 功能 |
|-------|------|
| HN Briefing | 定时读 Hacker News，排名后发 Slack/邮件 |
| Release Radar | 监控依赖发布，推送破坏性变更 |

#### 🗣️ Voice AI Agents

| Agent | 功能 |
|-------|------|
| Customer Support Voice | 基于自有文档的语音客服 |
| Insurance Claim Live | Gemini Live 实时语音理赔 |
| Voice RAG | PDF 问答→语音回答 |

#### ♾️ MCP AI Agents

| Agent | 连接 |
|-------|------|
| Browser MCP | 自然语言驱动浏览器 |
| GitHub MCP | 英文分析任意仓库 |
| Notion MCP | 终端操作 Notion 页面 |
| Travel Planner MCP | Airbnb + Google Maps 实时数据 |

#### 🖼️ Generative UI Agents

| Agent | 功能 |
|-------|------|
| Dashboard Canvas | 描述仪表盘→实时图表组装 |
| MCP App Builder | 描述 MCP 应用→沙箱实例 |
| Shadcn Component Generator | 聊天生成 shadcn 组件 |

#### 📚 RAG Tutorials（精选）

| 教程 | 特色 |
|------|------|
| Hybrid Search RAG | 关键词+向量搜索→Claude |
| Local Hybrid RAG | 全本地运行 |
| Knowledge Graph RAG | 多跳推理+可验证来源 |
| RAG Failure Diagnostics | 系统化诊断 RAG 管线错误 |
| Vision RAG | 图片+PDF 页面问答 |

#### 🧑‍🏫 Agent Framework Crash Courses

| 课程 | 内容 |
|------|------|
| Google ADK | Starter agent → 结构化输出 → 工具 → 记忆 → 多 Agent |
| OpenAI Agents SDK | Function calling → 结构化输出 → Handoffs → Swarm 编排 |

### 安装方式

```bash
# Agent Skill 一键安装
npx skills add https://github.com/Shubhamsaboo/awesome-llm-apps/tree/main/agent_skills/project-graveyard

# Clone 运行任意 Agent
cd awesome-llm-apps/starter_ai_agents/ai_blog_to_podcast_agent
```

---

## 第二部分：AI Harness 课程 — 从第一性原理到生产级 Agent

### 基本信息

| 项目 | 详情 |
|------|------|
| **名称** | AI Harness · From Fundamentals to Production-Grade Agents |
| **作者** | Luo Xiaoshan (罗小山) |
| **平台** | xueai.app (Miyang 账号体系) |
| **费用** | 免费（前两节开放，登录解锁全部） |
| **规模** | 186 个互动知识点 |

### 课程定位

> From "calling an API" to "reading production Coding Agent code"

从"调用 API"到"读生产级 Coding Agent 源码"。

### 目标受众

| 受众 | 价值 |
|------|------|
| **AI 产品经理** | 超越"调 Prompt"——理解底层原理，与工程师有效协作 |
| **转行者** | 产品/商业背景 → 系统化 AI 知识库（不会过时的心智模型） |
| **创始人和独立开发者** | 上线真实 AI 功能——关注成本、质量、工程权衡 |

### 课程结构：54 主题 · 7 章 + 甜点

| 章节 | 方向 |
|------|------|
| Ch1-2 | LLM 基础原理 |
| Ch3 | Prompt Engineering |
| Ch4 | Agent 实操 |
| Ch5 | 生产级 Harness 设计模式 |
| Ch6 | Grok Build 的 Rust 源码 |
| Ch7 | Vibe Coding 协作 |
| 甜点 | 雷军创业课——产品与商业 |

> 每个主题独立自足，可按需学习，随时回看。

---

## 查询拓展

- Awesome LLM Apps 的 Self-Improving Agent Skills（Gemini+ADK）与 SkillOpt 有什么异同？
- Trust-Gated Agent Team 的 hash 链审计怎么实现？
- Always-on Agents 的调度机制——GitHub Actions 还是自建调度器？
- AI Harness 课程的"Grok Build Rust 源码"章节具体讲什么？
- Advisor Orchestrator Worker 的三模型 Meta Loop 架构适合什么场景？

---

## 归纳总结

这两个资源代表了 AI Agent 工程化的两个面：

**Awesome LLM Apps（131K⭐）** 是当前最大的开源 Agent 模板库，覆盖从单文件入门到生产级多 Agent 团队的完整光谱。100+ 模板横跨 Agent Skills / Starter / Advanced / Always-on / Voice / MCP / Generative UI / RAG / Game-Playing / Memory / Fine-tuning 等 10+ 类别。最大价值是**可直接 Fork→修改→上线→售卖**（Apache-2.0 允许商用）。

**AI Harness 课程** 是系统化的知识层，从 LLM 第一性原理到生产级 Coding Agent 源码分析，186 个知识点覆盖全栈。定位明确——不是"教你调 API"，而是"给你一套不会过时的心智框架"。

两者组合 = **模板（怎么做）+ 原理（为什么这样做）** 的完整学习路径。

---

## 趋势判断

- **Agent 模板库成为基础设施**：131K Stars 说明市场对"现成 Agent 模板"的需求巨大。类似 Docker Hub 之于容器——模板库成为 Agent 时代的"镜像仓库"
- **Agent Skills 一键安装成为标准**：`npx skills add` 模式正在成为跨 Agent（Claude Code/Codex/Cursor）的通用技能安装协议
- **Always-on Agent 是下一波**：后台值守型 Agent（HN Briefing / Release Radar）代表了从"被动响应"到"主动值守"的转变
- **Self-Improving Agent Skills 出现在模板库中**：说明技能自优化（SkillOpt 类）已经从学术走向工程实践
- **中文 AI 教育内容质量提升**：罗小山的 AI Harness 课程覆盖 Harness 设计模式和 Rust 源码分析，说明中文 AI 工程教育内容正在追上英文水平

---

## 关联分析

- **与 Hermes Agent 的直接关联**：Awesome LLM Apps 的多个 Agent 模板可以直接适配到 Hermes——如 Always-on HN Briefing Agent（与用户的 `blogwatcher` Skill 同类）、Voice RAG Agent（与 `voice-assistant-service-stack` Skill 互补）、MCP Agents（与 `mcp-integration` Skill 对接）
- **与 Self-Improving Agent Skills 的关联**：这个模板与 SkillOpt 是同类——自动优化 Agent 技能。可以用它来优化 Hermes 的 180+ Skill
- **与 Agent Harness 执行栈的关联**：AI Harness 课程第 5 章"生产级 Harness 设计模式"与用户已有的 `harness-architecture`（六层 Harness）和 `harness-checkpoint`（检查点机制）Skill 直接对应
- **与 FDE 商业模式的关联**：Awesome LLM Apps 的 100+ 模板就是 FDE 的"武器库"——帮企业快速搭建 AI Agent 时的现成起点，Apache-2.0 允许商用
- **与 Vibe Coding 的关联**：课程第 7 章 Vibe Coding 协作与用户之前保存的 Vibe Coding 视觉词典笔记直接关联

---

## 📎 关键链接

- 📦 Awesome LLM Apps：[github.com/Shubhamsaboo/awesome-llm-apps](https://github.com/Shubhamsaboo/awesome-llm-apps)
- 📰 Unwind AI 教程：[theunwindai.com](https://www.theunwindai.com)
- 📖 AI Harness 课程：[xueai.app/slides](https://xueai.app/slides/home.en.html)

---

*笔记创建：2026-08-07 · 来源：awesome-llm-apps + AI Harness 课程*

## 相关笔记

- [Coding-Agent-Harness解剖学-Mastra深度架构](2026-08-07-Coding-Agent-Harness解剖学-Mastra深度架构.md)
- [DeepSeek-Agent-Harness执行栈全景图](2026-08-06-DeepSeek-Agent-Harness执行栈全景图.md)
- [Awesome-Journal-Skills-4152个期刊投稿AI工作流](2026-08-08-Awesome-Journal-Skills-4152个期刊投稿AI工作流.md)

---
