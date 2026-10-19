# Claude Code 之父 Boris Cherny：编程已死，数千 Agent 夜间打工

> **来源**：Sequoia Capital AI Ascent 2026 · Business Insider · Lenny's Podcast · HN #48050402 · 2026-05-04
> **原文**：https://www.youtube.com/watch?v=SlGRN8jh2RI
> **笔记ID**：sniff-20260525-boris-cherny-coding-solved
> **格式**：双格式(MD + HTML) · 含借鉴进化点 · RAG/wiki联动
> **关联**：[AI编码工具战争](2026-05-24-AI编码工具战争-CodexClaudeCodeCursor收敛为分层架构.md) [Superset YC P26](2026-05-23-Superset-YC-P26-AI-Agent-IDE.md) [10万行Rust AI开发实战](2026-05-21-10万行Rust-AI开发实战-Code-Contracts与性能优化.md)

## 摘要

Boris Cherny 是 Anthropic Claude Code 的创建者和负责人。在 Sequoia Capital AI Ascent 2026 上，他分享了一个震撼性观点：编程已"解决"（solved）。他自己 2026 年没有写过一行代码，每天从手机上提交数十个 PR，夜间有"几千个" AI 子 Agent 在为他工作。Claude Code 已占据 GitHub 公开提交的 4%，日活用户上月翻倍。这不是炫技，而是对软件开发范式根本性转变的宣言。

## 核心内容

### 1. "编程已解决"的核心论点

Cherny 的定义：对他个人编写的代码类型来说，AI 编程已经完全解决。关键不是 AI 能写所有代码，而是：
  日常开发中的 CRUD、API 集成、测试编写、重构等"确定性"工作已完全自动化
  人类的价值从"写代码"转移到"定义问题"和"审核方案"
  编程从手工劳动变为"管理"劳动——管理 AI Agent 的输出

### 2. 千级 Agent 夜间工作流

Cherny 的工作流：
  Claude App 左侧有 Code Tab，他维护多个并行会话
  每个会话是一个独立的编码任务
  夜间有"几千个" AI 子 Agent 执行更深层的任务
  早上醒来检查结果，快速审核合并

这揭示了 AI 编程从"单个 Agent 辅助"到"Agent 集群协作"的范式跃迁。

### 3. Claude Code 的增长数据

  占 GitHub 公开提交的 4%
  日活用户（DAU）上月翻倍
  从一个"简单的终端原型"一年内演变为改变软件工程角色的工具
  Claude Code + Cowork 组合正在扩展到编程之外的所有专业工作

### 4. 产品哲学的反直觉原则

Cherny 分享了驱动 Claude Code 成功的产品原则：
  不要过度设计——让用户自己发现用法（vibe coding 的反面）
  终端是程序员的自然栖息地，不要强行迁移到 GUI
  信任用户：给他们强大但危险的工具，而非安全但无用的工具

## 关键概念

**Vibe Coding → Agentic Engineering**：从"凭感觉写提示词让 AI 生成代码"到"系统性地管理和编排 AI Agent 完成工程任务"的演变。

**Agent 集群（Agent Swarm）**：大量 AI Agent 并行工作，每个负责一个子任务，由人类做最终审核和合并。

**PR-per-day 工作流**：从传统的一天写几个 PR 到一天审核合并数十个 PR，工作性质根本改变。

## 能力边界

  "编程已解决"仅适用于 Cherny 的代码类型——大型系统的日常维护和迭代
  不适用于：全新算法设计、性能关键路径优化、安全敏感代码
  千级 Agent 工作流需要极强的系统设计能力和审核能力
  Claude Code 占 GitHub 4% 意味着 96% 仍然是人类，但增速惊人

## 最佳实践

  采用"夜间 Agent 打工 + 早上审核"模式，最大化时间利用率
  学习 Agent 编排：如何拆分任务、如何设置质量门禁
  保留对核心架构和安全关键代码的人工控制

## 🔍 借鉴学习进化点（必填）

| # | 点 | 原文要点 | 对当前系统的借鉴 | 行动计划 |
|---|-----|---------|---------------|---------|
| 1 | 千级 Agent 并行工作流 | 几千个 AI 子 Agent 夜间执行深层任务 | Hermes 的 kanban-orchestrator + subagent-driven-development 可实现类似的并行 Agent 编排 | 设计"夜间批量任务"模式：睡前提交任务队列，Agent 集群自动执行 |
| 2 | PR 审核模式转变 | 从写 PR 变为审核 PR，工作量性质改变 | 将代码审查流程改为"AI 生成 + 人类审核"模式 | 在 github-code-review skill 中增加 AI-generated diff 的审核模板 |
| 3 | 终端优先哲学 | 程序员最习惯终端，不要强行 GUI 化 | Hermes 的 CLI-first 设计方向正确，继续强化 TUI 体验 | 优化 hermes TUI 的 slash commands 体验 |
| 4 | Agent 集群的质量门禁 | 千级 Agent 需要自动化质量检查 | 借鉴 verification-gate skill 建立多级自动验证 | 为 subagent 任务增加 auto-verification 层 |
| 5 | 从 vibe coding 到 agentic engineering | 系统性编排 > 随意提示 | Hermes 的 skill-pipeline 正是 agentic engineering 的实现 | 将 skill-pipeline 推广为所有复杂任务的标准工作流 |

## 🔗 RAG / Wiki 联动（必填）

### 当前状态
  已有 AI 编码工具战争笔记，含 Codex/Claude Code/Cursor 对比
  agent-health-monitoring 记录了 Agent 稳定性监控方案
  kanban-orchestrator 实现了任务分解和分配

### 改进方案
1. 在 AI 编码专题中新增"Agent 编排模式"章节，整合 Cherny 的工作流
2. 设计 Hermes 原生的"夜间任务队列"功能
3. 将 Agent 集群模式文档化为可复用的 skill

### 已执行操作
- ✅ 笔记已写入 bookmarks/notes
- ⏳ Agent 编排模式文档待下次会话创建

## 相关笔记
- [Agent Skills才是关键抽象层](2026-04-02-Agent Skills才是关键抽象层.md)
- [Claude-Code四层记忆架构](2026-04-03-Claude-Code四层记忆架构.md)
- [Claude-Code-324-prompts-analysis](2026-04-04-Claude-Code-324-prompts-analysis.md)
- [Hermes-Agent四层记忆架构深度分析](2026-05-22-Hermes-Agent四层记忆架构深度分析.md)
- [OpenClaw日常聊天黑化Agent-ULSPB安全研究](2026-05-22-OpenClaw日常聊天黑化Agent-ULSPB安全研究.md)
- [Domain-Camouflaged-Injection-Attacks-域伪装注入绕过多Agent检测](2026-05-23-Domain-Camouflaged-Injection-Attacks-域伪装注入绕过多Agent检测.md)
- [Microsoft取消ClaudeCode许可-AI编码战企业政治](2026-05-23-Microsoft取消ClaudeCode许可-AI编码战企业政治.md)
- [Superset-YC-P26-AI-Agent-IDE](2026-05-23-Superset-YC-P26-AI-Agent-IDE.md)
- [AI编码工具战争-CodexClaudeCodeCursor收敛为分层架构](2026-05-24-AI编码工具战争-CodexClaudeCodeCursor收敛为分层架构.md)
- [Cloudflare-Agents-Week-2026-Agentic-Cloud全栈基础设施](2026-05-24-Cloudflare-Agents-Week-2026-Agentic-Cloud全栈基础设施.md)
- [PiAgent深度分析](2026-05-24-PiAgent深度分析.md)
- [浅浅走入Hermes-Agent的记忆-毛毛MA](2026-05-25-浅浅走入Hermes-Agent的记忆-毛毛MA.md)
- [高德OPC自主增长系统-Harness多Agent架构](2026-05-25-高德OPC自主增长系统-Harness多Agent架构.md)
- [零信任安全2026-Agent系统新攻击面与安全基线-深度蒸馏](explore/2026-05-21-零信任安全2026-Agent系统新攻击面与安全基线-深度蒸馏.md)
- [GROW开放世界VLM-Agent强化学习框架](explore/2026-05-22-GROW开放世界VLM-Agent强化学习框架.md)
- [agent-evolution-rag](explore/2026-05-23-agent-evolution-rag.md)
- [Harness-工程-AI-编程智能体成功率从20%到100%](explore/2026-05-24-Harness-工程-AI-编程智能体成功率从20%到100%.md)
- [MOSS自主Agent源码级自进化](explore/2026-05-24-MOSS自主Agent源码级自进化.md)
