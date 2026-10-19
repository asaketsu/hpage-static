# The Agency — 200+ AI 专家 Agent 人格库（12 部门全覆盖）

> GitHub: https://github.com/msitarzewski/agency-agents
> License: MIT
> App: https://agencyagents.app (macOS/Linux/Windows 原生应用)
> 评分: ⭐⭐⭐⭐⭐ (5/5) — 目前最大规模的 AI Agent 人格模板开源库，12 部门 200+ 专业角色

## 一句话定位

**一个完整的"AI 代理公司"人格模板库——200+ 个精心设计的专业 AI Agent，覆盖工程/设计/营销/销售/安全/测试等 12 个部门，每个 Agent 有独特人格、工作流程和交付物定义。支持 Claude Code、Cursor、Codex、Gemini CLI、OpenCode、Hermes 等 15+ 工具一键安装。**

## 核心架构

### 设计理念

每个 Agent 不是简单的 prompt template，而是包含：
- **身份与人格特质**（Identity & Personality）
- **核心使命与工作流**（Mission & Workflows）
- **技术交付物 + 代码示例**（Deliverables）
- **成功指标 + 沟通风格**（Success Metrics）

> 定位语：*"Assembling your dream team, except they're AI specialists who never sleep, never complain, and always deliver."*

### 多工具兼容（15+ 平台）

| 工具 | 安装命令 |
|------|----------|
| Claude Code | `./scripts/install.sh --tool claude-code` |
| Cursor | `--tool cursor` |
| Codex | `--tool codex` |
| Gemini CLI | `--tool gemini-cli` |
| OpenCode | `--tool opencode` |
| GitHub Copilot | `--tool copilot` |
| **Hermes** | `--tool hermes` |
| Antigravity | `--tool antigravity` |
| OpenClaw | `--tool openclaw` |
| Aider | `--tool aider` |
| Windsurf | `--tool windsurf` |
| Kimi Code | `--tool kimi` |
| Osaurus | `--tool osaurus` |
| Mistral Vibe | `--tool vibe` |

支持按部门/单个 Agent 精细安装：
```bash
./scripts/install.sh --tool hermes --division engineering,security
./scripts/install.sh --tool cursor --agent frontend-developer,ui-designer
```

## 12 个部门全景

### 💻 Engineering Division（工程部，~50 个 Agent）

最大部门，覆盖全栈工程：

| Agent | 专长 |
|-------|------|
| Frontend Developer | React/Vue/Angular, UI 实现 |
| Backend Architect | API 设计, 数据库架构, 微服务 |
| Mobile App Builder | iOS/Android, React Native, Flutter |
| AI Engineer | ML 模型, 部署, AI 集成 |
| DevOps Automator | CI/CD, 基础设施自动化 |
| **Embedded Firmware Engineer** | 裸机/RTOS, ESP32/STM32/Nordic |
| **Multi-Agent Systems Architect** | 多 Agent 管线设计与治理 |
| **RAG Pipeline Engineer** | 生产级 RAG 管线 |
| **LLM Post-Training Engineer** | SFT/DPO/GRPO/RLVR 后训练 |
| **Prompt Engineer** | LLM prompt 设计与优化 |
| **Feishu Integration Developer** | 飞书/Lark 生态集成 |
| **Voice AI Integration Engineer** | STT 管线, Whisper, ASR |
| Code Reviewer / SRE / Database Optimizer / Software Architect / ... | |

### 🎨 Design Division（设计部，10 个）

UI Designer, UX Researcher, UX Architect, Brand Guardian, Visual Storyteller, Whimsy Injector（趣味注入者）, Image Prompt Engineer, Inclusive Visuals Specialist, Persona Walkthrough, UI Finish-Gate Reviewer

### 💰 Paid Media Division（付费媒体部，7 个）

PPC Campaign Strategist, Search Query Analyst, Paid Media Auditor, Tracking & Measurement, Ad Creative Strategist, Programmatic & Display Buyer, Paid Social Strategist

### 💼 Sales Division（销售部，10 个）

Outbound Strategist, Discovery Coach, Deal Strategist, Sales Engineer, Proposal Strategist, Pipeline Analyst, Account Strategist, Sales Coach, Sales Outreach, Offer & Lead Gen Strategist

### 📢 Marketing Division（营销部，~35 个）

**中国平台专家最密集的部门**：

| Agent | 平台 |
|-------|------|
| Xiaohongshu Specialist | 小红书 |
| WeChat Official Account Manager | 微信公众号 |
| Zhihu Strategist | 知乎 |
| Baidu SEO Specialist | 百度 SEO |
| Bilibili Content Strategist | B 站 |
| Douyin Strategist | 抖音 |
| Kuaishou Strategist | 快手 |
| Weibo Strategist | 微博 |
| China E-Commerce Operator | 淘宝/天猫/拼多多 |
| Cross-Border E-Commerce | 亚马逊/Shopee/Lazada |
| Private Domain Operator | 企业微信私域 |
| Livestream Commerce Coach | 直播带货 |
| Multi-Platform Publisher | 一键多平台分发 |
| **AI Citation Strategist** | AEO/GEO, AI 推荐可见性 |
| **Agentic Search Optimizer** | WebMCP & Agent 任务完成 |
| Global Podcast Strategist / LinkedIn / Twitter / TikTok / Instagram / Reddit / SEO / Email / PR | |

### 📊 Product Division（产品部，5 个）

Sprint Prioritizer, Trend Researcher, Feedback Synthesizer, Behavioral Nudge Engine, Product Manager

### 🎬 Project Management Division（项目管理部，7 个）

Studio Producer, Project Shepherd, Studio Operations, Experiment Tracker, Senior PM, Jira Workflow Steward, Meeting Notes Specialist

### 🧪 Testing Division（测试部，9 个）

Evidence Collector, Reality Checker, Test Results Analyzer, Performance Benchmarker, API Tester, Tool Evaluator, Workflow Optimizer, Accessibility Auditor, Test Automation Engineer

### 🔒 Security Division（安全部，12 个）

Security Architect, AppSec Engineer, Penetration Tester, Cloud Security Architect, Incident Responder, Threat Intelligence Analyst, Threat Detection Engineer, SecOps Engineer, Compliance Auditor, Blockchain Security Auditor, **AI-Generated Code Security Auditor**, Secrets & Credential Hygiene Engineer

### 🛟 Support Division（支持部，6 个）

Support Responder, Analytics Reporter, Finance Tracker, Infrastructure Maintainer, Legal Compliance Checker, Executive Summary Generator

### 🥽 Spatial Computing Division（空间计算部，6 个）

XR Interface Architect, macOS Spatial/Metal Engineer, XR Immersive Developer, XR Cockpit Interaction, visionOS Spatial Engineer, Terminal Integration Specialist

### 🎯 Specialized Division（特别事业部，~30 个）

Agents Orchestrator, LSP/Index Engineer, MCP Builder, ZK Steward（知识管理/Zettelkasten）, Automation Governance Architect, Cultural Intelligence Strategist, Developer Advocate, Model QA Specialist, Document Generator, Civil Engineer, Business Strategist, Change Management Consultant, 各种行业专家（法律/医疗/房产/零售/招聘/留学）

## 关键设计亮点

### 1. 人格驱动而非模板驱动

每个 Agent 有独特的声音、沟通风格和工作方式，不是泛化的提示模板。例如：
- **Whimsy Injector**（趣味注入者）：专门负责给产品添加人格魅力、微交互、彩蛋
- **Reality Checker**（现实检查者）：基于证据的认证和质量门禁
- **Minimal Change Engineer**（最小变更工程师）：只修被要求的问题，零范围蔓延

### 2. 中国本土化深度

营销部门有 **15+ 个中国平台专属 Agent**（小红书/抖音/B站/知乎/微博/快手/公众号/私域/直播带货/跨境电商），覆盖中国数字营销全生态。

### 3. 安装粒度精细

```bash
# 交互式选择工具+部门
./scripts/install.sh

# 只要工程和安全部门
./scripts/install.sh --tool hermes --division engineering,security

# 只要特定 Agent
./scripts/install.sh --tool cursor --agent frontend-developer,ui-designer

# 查看所有团队
./scripts/install.sh --list teams

# 干跑预览
./scripts/install.sh --tool opencode --division engineering --dry-run
```

### 4. 原生桌面 App

[agencyagents.app](https://agencyagents.app) 提供可视化浏览和一键安装，支持 macOS/Linux/Windows，自动更新。

## 💡 对 Hermes Agent 的借鉴分析

### ✅ 我们已有的对标

| The Agency 部门 | Hermes 对标 |
|----------------|-------------|
| Engineering | Dev Meow（开发喵） |
| Product/PM | OPM Meow（运营喵） |
| Marketing | Content Meow（内容喵） |
| Testing/Analytics | Data Meow（分析喵） |
| Security | red-teaming skills（300+攻防skill） |
| Support | 系统巡检 cron + watchdog |

### 🔥 值得借鉴的设计

| 设计点 | 内容 | 对 Hermes 的启发 |
|--------|------|-----------------|
| **人格驱动 Agent** | 每个 Agent 有独特人格和沟通风格 | 我们的 team-roles skill（content-meow/dev-meow等）已有类似设计，但颗粒度可以更细 |
| **按部门/Agent 精细安装** | `--division engineering,security` | Hermes 的 skill 加载机制可以借鉴这种按"部门"分组的方式 |
| **Whimsy Injector** | 专门负责产品趣味性 | 独特的角色设计——不是所有 Agent 都要严肃 |
| **Minimal Change Engineer** | 只修被要求的，零范围蔓延 | 对标我们的 `agent-search-edit` skill，但更极端 |
| **AI Citation Strategist** | AEO/GEO，让 AI 推荐中可见 | 全新的营销赛道——不是给人看 SEO，而是给 AI 看 |
| **Agentic Search Optimizer** | 让 AI 浏览 Agent 能使用的网站 | WebMCP 标准的实践者 |
| **中国平台 15+ 专属 Agent** | 小红书/抖音/B站/知乎全覆盖 | 我们有 `xhs-content-pipeline` 等单个 skill，但缺乏系统化的中国平台 Agent 矩阵 |
| **AI-Generated Code Security Auditor** | 专门审计 AI/vibe-coded 应用的安全 | AI 代码安全审计是新兴需求 |
| **Multi-Agent Systems Architect** | 多 Agent 管线设计与治理 | 对标我们的 `agent-orchestration-pattern` skill |
| **Feishu Integration Developer** | 飞书生态集成 | 我们有 22 个飞书 skill，但可以包装成统一的"飞书集成专家"角色 |

### 📊 规模对比

| 维度 | The Agency | Hermes Agent |
|------|-----------|--------------|
| Agent/角色数 | 200+ | 4 猫 + 300+ skills |
| 组织方式 | 12 部门制 | 技能目录制（category） |
| 人格深度 | 每个 Agent 有独立 .md | team-roles 4 猫 + skill 描述 |
| 多工具支持 | 15+ AI 工具 | 仅 Hermes |
| 中国平台覆盖 | 15+ 专属 Agent | 数个独立 skill |
| 安装方式 | App + CLI | skill_view / skill_manage |

## 趋势判断

1. **Agent 人格库正在成为新赛道**：从单一 Agent → Agent 团队 → Agent 人格市场。The Agency / Claude Code agents / Hermes skills 都在这个方向
2. **中国本土化是差异化关键**：The Agency 营销部 1/3 是中国平台 Agent，说明海外对中国数字营销生态的需求
3. **AEO（AI Engine Optimization）正在取代传统 SEO**：AI Citation Strategist 和 Agentic Search Optimizer 预示着营销的新方向——不只是给搜索引擎优化，要给 AI Agent 优化
4. **"AI 公司"概念正在落地**：完整的 12 部门结构模拟真实公司组织，从工程到销售到法务全覆盖

## 关联

- → 相关：agent-orchestration-pattern（多 Agent 编排设计模式）
- → 相关：agent-primitive-architecture（Agent 三原语架构）
- → 相关：team-roles（Hermes 四猫团队角色）
- → 相关：xhs-content-pipeline（小红书内容生产）
