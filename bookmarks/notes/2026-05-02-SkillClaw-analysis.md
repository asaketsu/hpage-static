---
title: SkillClaw 集体技能进化框架深度分析
date: 2026-05-02
source: https://github.com/AMAP-ML/SkillClaw
tags: [竞品分析, skill-evolution, collective-intelligence, agent, Hermes]
related: [evolver](2026-04-05-capability-evolver-self-upgrade.md), [auto-dream](Auto-Dream.md), [Hermes Agent](2026-04-13-hermes-agent-vs-openclaw.md)
---

## 项目画像

| 维度 | 内容 |
|------|------|
| 仓库 | AMAP-ML/SkillClaw |
| Stars | 1,120 |
| Forks | 105 |
| 语言 | Python |
| 创建时间 | 2026-04-10 |
| 团队 | DreamX（阿里高德相关） |
| License | MIT |
| 论文 | arXiv:2604.08377 |
| 定位 | **多用户 Agent 生态中的集体技能进化框架** |

**一句话**：SkillClaw 是一个让 AI Agent 技能从真实用户交互中自动进化、跨用户共享的中间件系统。用户正常聊天即可，技能在后台静默进化。

## 核心架构

SkillClaw 分为两大部分：

### 1. 客户端（skillclaw/）— 本地代理+技能注入

- **API Proxy**：拦截 LLM 请求（OpenAI Chat/Responses API、Anthropic Messages），在 prompt 中注入匹配的技能
- **SkillManager**：本地技能检索引擎，支持 template（关键词）和 embedding（语义）两种检索模式
- **PRMScorer**：Process Reward Model 评分器，用 LLM 对每轮回复做多轮投票（默认3轮），输出 +1/-1/0 评分
- **SkillHub**：云同步模块，支持 S3/OSS/本地存储，实现多用户技能共享
- **ValidationWorker**：客户端空闲时自动参与技能验证的分布式 worker
- **Dashboard**：Web UI 展示技能进化状态

工作流：`用户请求 → Proxy拦截 → SkillManager注入技能 → 转发LLM → PRM评分 → 记录session`

### 2. 进化服务端（evolve_server/）— 技能进化引擎

- **Summarizer**：会话轨迹结构化（无损 trajectory + LLM 分析摘要），提取引用的技能、平均PRM分数、工具错误标记
- **SessionJudge**：LLM 多维度评分（task_completion 0.55 / response_quality 0.30 / efficiency 0.05 / tool_usage 0.10）
- **Aggregation**：按引用的技能分组会话，同一会话可归入多个技能组
- **Execution**：核心进化决策 — improve_skill / optimize_description / create_skill / skip
- **SkillVerifier**：新/改技能的验证
- **SkillIDRegistry**：技能名称→ID映射，带版本追踪和变更历史
- **EvolveServer / AgentEngine**：两种进化引擎实现

工作流：`采集sessions → 轨迹结构化 → LLM评分 → 按技能聚合 → 进化决策 → 生成/修改技能 → 验证 → 上传`

### 关键设计模式

**1. 集体进化（Collective Evolution）**
不同用户使用同一技能会产生互补信号，揭示技能在什么条件下有效/失败。跨用户聚合这些信号是核心竞争力。

**2. 双循环架构（Two Loops）**
- 内循环：单用户实时 — 使用技能→收集反馈
- 外循环：跨用户批量 — 聚合反馈→进化技能→分发更新

**3. PRM 多数投票评分**
用 LLM 做 judge，3次独立评分取多数投票（+1/-1/0），降低单次评分噪声。

**4. 五类失败分类**
- SKILL_CONTENT_STALE（内容过时）
- SKILL_MISSELECT（选错技能）
- SKILL_GAP（技能缺口）
- TOOL_ERROR（工具使用错误）
- MODEL_BASELINE（模型基础能力）

**5. AgentSkills 兼容格式**
技能使用 SKILL.md + YAML frontmatter 格式，与 OpenClaw/Hermes 的技能格式兼容。

## 亮点与不足

### 亮点 ✅

1. **集体进化理念领先** — 多用户协同改进技能，跨用户知识转移，这是真正的网络效应
2. **论文+代码双输出** — 有学术论证（WildClawBench 评测），6轮进化提升88%
3. **协议兼容性好** — 支持 OpenAI Chat/Responses、Anthropic Messages，适配 Hermes/OpenClaw/Codex
4. **分布式验证** — 客户端空闲时自动参与验证，巧妙利用闲置算力
5. **会话级评分体系** — 多维度加权评分比简单 pass/fail 更精细
6. **技能版本追踪** — content_sha + version + history，支持回滚
7. **Dashboard 可视化** — Web UI 展示进化状态，增强可观测性

### 不足 🔴🟡

1. 🟡 **依赖云存储** — 进化服务端强依赖 S3/OSS，单用户离线场景用不上集体进化
2. 🟡 **PRM 成本高** — 每轮3次 LLM 调用做评分，大规模部署成本不低
3. 🟡 **代理拦截模式** — 作为中间代理拦截所有 API 请求，增加了延迟和故障点
4. 🔴 **技能质量保障弱** — 缺乏对进化产出的系统性质量门控，LLM 生成的技能可能引入噪声
5. 🟡 **隐私风险** — 多用户共享技能意味着交互数据可能泄露到共享层

## 与我们系统的关联

### 直接关联

SkillClaw 与我们的 evolver / auto-dream / auto-learn 系统解决同一问题：**如何让 Agent 技能从经验中自动改进**。

| 维度 | 我们的系统 | SkillClaw |
|------|-----------|-----------|
| 架构 | 内置（cron job 驱动） | 独立中间件（API Proxy） |
| 数据源 | session_search + 日志 | 拦截的 API 请求/回复 |
| 进化触发 | 定时（03:00-04:15） | 积累足够 sessions 后批量 |
| 评分 | 无量化评分 | PRM 多数投票 + Session Judge |
| 共享 | 单用户 | 多用户集体 |
| 技能格式 | SKILL.md YAML frontmatter | 完全兼容 ✅ |
| 验证 | evolver 自检 | SkillVerifier + 分布式验证 |

### 可借鉴模式

| 模式 | 说明 | 新颖性 | 可移植性 | 优先级 |
|------|------|--------|---------|--------|
| **PRM 多数投票评分** | 3轮 LLM judge 评分取多数投票 | ⭐⭐⭐ 我们没有量化评分 | 高 — 可直接加入 auto-evolver | 🔴 高 |
| **会话级多维度评分** | task_completion/response_quality/efficiency/tool_usage 加权 | ⭐⭐⭐ | 高 — 可改造 session judge cron | 🔴 高 |
| **五类失败分类** | 系统化分类技能失败原因 | ⭐⭐ 我们有错误分析但不分类 | 高 — 可加到 sensor-grid | 🟡 中 |
| **技能版本追踪** | content_sha + version + history | ⭐ 已有 Curator 但缺显式版本号 | 中 — 需要 skill 文件改格式 | 🟡 中 |
| **分布式验证** | 客户端空闲时参与验证 | ⭐ 单用户暂不需要 | 低 | 🟢 低 |
| **Skill Hub 云同步** | 多用户技能共享 | ⭐ 单用户不需要 | 低 | 🟢 低 |
| **Dashboard** | Web UI 展示进化状态 | ⭐⭐ | 中 — 可加到 Hermes Dashboard | 🟡 中 |

### 不应借鉴

1. **API Proxy 拦截模式** — 我们是内置 agent，不需要中间代理
2. **云存储依赖** — 我们是单用户，本地文件系统足够
3. **多用户集体进化** — 当前场景不需要

## 竞品定位

SkillClaw 处于 **Agent 技能管理层** 的独特位置：

- vs **MemGPT/Letta** — MemGPT 做记忆管理，SkillClaw 做技能进化，互补不竞争
- vs **LangChain/LangGraph** — LangChain 做编排，SkillClaw 做事后改进
- vs **Hermes（我们）** — Hermes 做全栈 agent，SkillClaw 做其中"技能进化"这一环

**SkillClaw 的壁垒**：集体进化机制 + 论文论证 + AgentSkills 兼容生态

**我们的壁垒**：端到端内置 + 零配置 + 多维传感器闭环

## 预判

| 时间 | 预判 |
|------|------|
| 短期（1-3月） | Stars 继续增长，Hermes 社区部分用户会装 SkillClaw 做技能进化 |
| 中期（3-6月） | 可能成为 Hermes/OpenClaw 生态的"技能进化标准"，类似 RAG 对检索增强的地位 |
| 长期 | 如果 Agent 生态成熟，集体进化会成为基础设施层，SkillClaw 需要与更多框架深度集成 |

## 相关笔记
- [AutoClaw-自进化与Skill商店](2026-04-17-AutoClaw-自进化与Skill商店.md)
- [hack-skills-给AI装上黑客大脑](2026-04-17-hack-skills-给AI装上黑客大脑.md)
- [Lima轻量级虚拟机管理工具](2026-04-22-Lima轻量级虚拟机管理工具.md)
- [歸藏PPT-Skill-电子杂志风网页演示](2026-04-24-歸藏PPT-Skill-电子杂志风网页演示.md)
- [竞品吸收_OpenCLI](2026-04-28-竞品吸收_OpenCLI.md)
- [竞品吸收笔记-khazix-skills](2026-04-29-竞品吸收笔记-khazix-skills.md)
- [从零构建AI-CLI方法论-ChainlessChain](2026-05-04-从零构建AI-CLI方法论-ChainlessChain.md)
- [Claude创意连接器9大工具-Blender-MCP深度解析](2026-05-05-Claude创意连接器9大工具-Blender-MCP深度解析.md)
- [github-ai-trending-mattpocock-skills](2026-05-05-github-ai-trending-mattpocock-skills.md)
- [lewislulu-html-ppt-skill-analysis](2026-05-06-lewislulu-html-ppt-skill-analysis.md)
- [addyosmani-agent-skills生产级Agent技能包](2026-05-08-addyosmani-agent-skills生产级Agent技能包.md)
- [Claude-Code工程师放弃Markdown转HTML](2026-05-09-Claude-Code工程师放弃Markdown转HTML.md)
- [OfficeCLI-AI-Agent的Office工具](2026-05-09-OfficeCLI-AI-Agent的Office工具.md)
- [Skill盈利死结与Plugin演进](2026-05-09-Skill盈利死结与Plugin演进.md)
- [skill-building-invoice-automation](2026-05-10-skill-building-invoice-automation.md)
- [softwarecopyright-skill-analysis](2026-05-10-softwarecopyright-skill-analysis.md)
- [nTop-Automate-CLI-完整测试文档](2026-05-12-nTop-Automate-CLI-完整测试文档.md)
- [中文学术去AI味10步Skill框架](2026-05-12-中文学术去AI味10步Skill框架.md)
- [30个网络抓包调试工具速查](2026-05-14-30个网络抓包调试工具速查.md)
- [HTML-Anything-Agent驱动HTML编辑器](2026-05-14-HTML-Anything-Agent驱动HTML编辑器.md)
- [SkillFactory-测试驱动Skill生成工厂](2026-05-14-SkillFactory-测试驱动Skill生成工厂.md)
- [Supertonic-闪电般本地TTS](2026-05-14-Supertonic-闪电般本地TTS.md)
- [数据目录工具全景指南](2026-05-15-数据目录工具全景指南.md)
- [CyberVerse公众号HTML模板分析](orphan/2026-05-03-CyberVerse公众号HTML模板分析.md)
- [国自然申请书AI-Skill流水线](orphan/2026-05-04-国自然申请书AI-Skill流水线.md)
- [数据血缘-lineage-工具全景](orphan/2026-05-09-数据血缘-lineage-工具全景.md)
- [论文写作Skill工具链组合方案](orphan/2026-05-12-论文写作Skill工具链组合方案.md)
- [HTML的不合理有效性-Claude-Code-团队](orphan/2026-05-16-HTML的不合理有效性-Claude-Code-团队.md)
- [20260512-10-skill-学术去ai味框架](orphan/20260512-10-skill-学术去ai味框架.md)
- [build-ai-cli](orphan/build-ai-cli.md)
- [hermes-skill-top10-2026w18](orphan/hermes-skill-top10-2026w18.md)
- [skills-apple](orphan/skills-apple.md)
- [skills-catalog](orphan/skills-catalog.md)
- [skills-data-science](orphan/skills-data-science.md)
- [skills-dogfood](orphan/skills-dogfood.md)
- [skills-email](orphan/skills-email.md)
- [skills-github](orphan/skills-github.md)
- [skills-leisure](orphan/skills-leisure.md)
- [skills-logo-generator-skill](orphan/skills-logo-generator-skill.md)
- [skills-smart-home](orphan/skills-smart-home.md)
- [skills-social-media](orphan/skills-social-media.md)
- [skills-team-roles](orphan/skills-team-roles.md)
- [skills-autonomous-ai-agents](skills-autonomous-ai-agents.md)
- [skills-creative](skills-creative.md)
- [skills-devops](skills-devops.md)
- [skills-gaming](skills-gaming.md)
- [skills-mcp](skills-mcp.md)
- [skills-media](skills-media.md)
- [skills-mlops](skills-mlops.md)
- [skills-note-taking](skills-note-taking.md)
- [skills-openclaw-imports](skills-openclaw-imports.md)
- [skills-overview](skills-overview.md)
- [skills-productivity](skills-productivity.md)
- [skills-red-teaming](skills-red-teaming.md)
- [skills-research](skills-research.md)
- [skills-software-development](skills-software-development.md)
