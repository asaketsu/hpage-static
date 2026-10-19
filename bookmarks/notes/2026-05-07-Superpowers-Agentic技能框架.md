# Superpowers — Agentic 技能框架与软件开发方法论

- 📅 2026-05-07
- ⭐ 4.5/5 — 目前最成熟的 AI Coding Agent 技能编排框架，18 万 Star 证明了其方法论普适性
- 🏷️ #AI-Agent #Skill框架 #TDD #SubAgent #Claude-Code #开源分析
- 📰 GitHub: obra/superpowers
- 🔗 https://github.com/obra/superpowers

## 摘要

Superpowers 是一个面向 AI Coding Agent 的完整软件开发方法论框架。作者 Jesse Vincent（obra）构建了一套基于可组合 Skill 的开发工作流：从需求 brainstorming → 设计 → 计划编写 → 子 Agent 并行执行 → 代码审查 → 验证收尾，覆盖了软件开发的完整生命周期。它不是工具，而是方法论——通过精心编排的 prompt 模板和流程约束，让 Claude Code/Codex/Gemini CLI 等 Agent 自动遵循高质量工程实践。18 万 Star、MIT 协议、v5.1.0，支持 8 个主流 Agent 平台。

## 核心内容

### 项目画像

| 维度 | 数据 |
|------|------|
| Stars | 181,589 |
| Forks | 16,128 |
| 语言 | Shell（主要是 Skill 文档 + Hook 脚本） |
| 协议 | MIT |
| 版本 | v5.1.0（2026-04-30） |
| 创建时间 | 2025-10-09 |
| 作者 | Jesse Vincent（obra） |
| 定位 | Agentic Skills Framework + 软件开发方法论 |

### 架构：13 个 Skill 组成的开发流水线

```
brainstorming → using-git-worktrees → writing-plans
     ↓                                    ↓
     ↓                        subagent-driven-development（主线）
     ↓                        executing-plans（备线，无 subagent 时）
     ↓                                    ↓
     ↓                        test-driven-development（TDD 红绿灯）
     ↓                        systematic-debugging（根因分析）
     ↓                        dispatching-parallel-agents（并行）
     ↓                        requesting-code-review（审查）
     ↓                        verification-before-completion（验证）
     ↓                        finishing-a-development-branch（收尾）
     ↓
using-superpowers（入口路由）
writing-skills（创建新 Skill 的 Skill）
```

### 核心理念

1. **Subagent-Driven Development（SDD）** — 每个 Task 派独立 subagent 执行，隔离上下文。Agent 不继承会话历史，只接收精确构造的指令。完成后经过两轮审查：spec compliance review → code quality review
2. **硬门控（Hard Gate）** — 每个 Skill 都有不可跳过的强制检查点。如 brainstorming 不完成不能写代码，TDD 没看测试失败不能写实现，验证不通过不能声称完成
3. **铁律文化** — "违反规则的字面意思就是违反规则的精神"。规则不是建议，是约束
4. **上下文精确注入** — subagent 只拿到任务描述 + 必要上下文，不拿会话历史。这避免了上下文污染和 token 浪费

### 技术实现亮点

**Hook 系统**：Claude Code 的 SessionStart hook 自动触发 `using-superpowers` Skill，实现零配置激活。

**Skill 元数据格式**：
```yaml
---
name: skill-name
description: 触发条件描述（Agent 用这个判断是否激活 Skill）
---
```

**审查分离**：spec reviewer 和 code quality reviewer 是两个独立角色。spec reviewer 检查"做没做对"，code reviewer 检查"做得好不好"。reviewer prompt 里明确写"Do Not Trust the Report"——不信任实现者的自我报告。

**TDD 三阶段**：RED（写测试看失败）→ GREEN（写最少代码通过）→ REFACTOR（重构）。testing-anti-patterns.md 列举了 12 种常见反模式。

**Skill 测试方法**：用 subagent 做"压力测试"——不带 Skill 跑一遍看 agent 怎么失败（RED），加载 Skill 再跑看是否合规（GREEN），然后关闭漏洞（REFACTOR）。本质是把 TDD 应用到了流程文档上。

### 多平台支持

支持 8 个 Agent 平台：Claude Code（官方插件市场）、Codex CLI/App、Factory Droid、Gemini CLI、OpenCode、Cursor、GitHub Copilot CLI。通过平台特定的 plugin 目录适配。

## 🔍 借鉴点

### ① 有利进化 — 立即落实

| 模式 | 说明 | 落实方式 |
|------|------|----------|
| **两轮审查分离** | spec compliance + code quality 分开审，互不干扰 | 我们 `delegate_task` 审查角色已按此设计，但需确保 reviewer prompt 包含"Do Not Trust"声明 |
| **Skill 测试用 subagent 压力测试** | 不带 Skill 看 agent 怎么翻车，带上再看是否修复 | 更新 `writing-skills` skill，加入 pressure test 环节 |
| **Hard Gate 不可跳过** | brainstorming 不完成不能编码，验证不通过不能声称完成 | 我们的 Skill 也需要硬门控标记（如 `<HARD-GATE>`） |
| **上下文精确注入** | subagent 不继承会话历史，只拿构造好的指令 | 已在 `subagent-driven-development` skill 中遵循 |

### ② 有价值备用

| 模式 | 说明 | 记忆 |
|------|------|------|
| **Git Worktree 隔离工作空间** | 每个 feature branch 用 worktree 隔离，避免 main 被污染 | 适合多分支并行开发场景 |
| **dispatching-parallel-agents** | 无依赖的独立任务可并行派发 | 我们 `delegate_task` 已支持，但缺少自动识别并行性的机制 |
| **Skill 版本管理** | package.json 管理版本，RELEASE-NOTES 追踪变更 | Skill 规模大到一定程度后需要 |
| **brainstorming 可视化 companion** | 本地 HTTP server + WebSocket 实时协作 | 复杂需求讨论时有价值 |

### ③ 笔记存档

- anthropic-best-practices.md（1150 行）是最全的 Skill 编写指南
- CLAUDE.md 里 94% PR 拒绝率的警示和反 slop 指南非常有价值
- defense-in-depth.md 的四层验证模型（Entry → Business → Environment → Debug）

## 🔗 关联性

- 关联已有 Skill：`subagent-driven-development` — 直接借鉴了 SDD 模式，但我们的版本更轻量
- 关联已有 Skill：`writing-plans` — 源自同一思路，superpowers 版更强调 DRY/YAGNI
- 关联已有 Skill：`systematic-debugging` — 我们的版本已有根因分析，superpowers 多了 defense-in-depth
- 关联已有 Skill：`test-driven-development` — 两边理念一致
- 关联项目：[Hermes Agent](2026-04-13-hermes-agent-vs-openclaw.md) — 我们的 Skill 系统设计思路与 superpowers 高度一致
- 关联笔记：[[2026-05-06-Hermes-Agent-skill-体系]] — skill 编排方法论

## 💡 启发

1. **Skill 是方法论不是工具** — superpowers 证明了"纯 prompt 工程可以让 AI 自觉遵循工程实践"。不需要改代码，不需要新框架，只要 Skill 写得足够好。我们的 Skill 系统走的正是这条路
2. **审查的不信任原则** — "Do Not Trust the Report" 这句话应该成为所有 reviewer prompt 的标配。AI 的自我报告天然乐观
3. **18 万 Star 背后的洞察** — 市场需要的是"方法论封装"而非"工具堆砌"。用户不想学 TDD，但想要 TDD 的效果。Skill 正好是方法论的载体
4. **Hard Gate > 软提醒** — `<HARD-GATE>` 标签比"建议你先做 X"有效 10 倍。约束必须是强制的才有效

## 🔮 预判

- **短期**（1-3 月）：superpowers 会成为 AI Coding Skill 的事实标准，更多 Agent 平台会原生支持其格式
- **中期**（3-6 月）：会出现 "Skill marketplace"——类似 VS Code 插件市场，但卖的是方法论而非工具
- **长期**（6-12 月）：Skill 会分化为"通用方法论"（如 superpowers）和"领域专用"（如 quant-trading skill）。我们的定位应在后者——垂直领域深度

## 相关笔记
- [[2026-05-06-Hermes-Agent-skill-体系]]
- [[2026-05-07-HermesClaw-iLink多路路由代理]]
