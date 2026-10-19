# DeepSeek Agent Harness 内测招募 — Agent 执行栈全景图

> **来源**：[@Xsir01 的推文](https://x.com/Xsir01/status/2084203368894062609)
> **作者**：Xsir
> **发布日期**：2026-08-03
> **阅读量**：14.1K Views
> **核心标签**：DeepSeek、Agent Harness、执行栈、Agent 基础设施

---

## 一句话定义

> DeepSeek Agent Harness 内测招募帖的评论区变成了一次「Agent 执行栈建设者的集中亮相」——展示了模型之外的**完整执行层**：工作台、Runtime、多 Agent 协作、沙箱、评测、观测。

---

## 内容整理

### 7 大分类 + 代表项目

#### 1. Coding Agent 工作台

让 Agent 在代码、终端、浏览器和真实项目里持续工作。

| 项目 | 特色 |
|------|------|
| **Kun** | 本地优先的 Agent 工作台 |
| **Setsuna Desktop** | 跨平台编程代理桌面应用 |
| **pi-workbench** | 围绕 pi 的桌面工作台，含模型路由、Agent Teams、Kanban |
| **RxyCode** | 规划→执行→校验一体，内置评测 Harness |
| **OpenPrd** | 面向真实长周期项目，强调进度保留、设计稿与实现结果对比、持续验证 |
| CodePilot | — |

#### 2. 多 Agent 协作与任务编排

不满足于"一个 Agent 对话到底"，搭建 Agent 团队和任务流水线。

| 项目 | 核心能力 |
|------|---------|
| **Archify** | 多 Agent 编排 |
| **Squad** | 多 Agent 协作 |
| **MCO** | 多 Agent 协调 |
| **Hive** | 群体智能 |
| **Hermes Console** | Agent 控制台 |
| **Tide** | 任务流 |
| **agent-sop** | SOP 标准化流程 |

关键特性：并行/串行/分治任务、多 Agent 上下文传递、跨模型协作、任务失败恢复、Token 监控、人工审核与结构化 signoff。

#### 3. Harness Runtime 和基础设施

最接近执行内核——管理 Agent 的上下文、工具调用、状态和任务生命周期。

| 项目 | 定位 |
|------|------|
| **Lambda Agent** | 执行内核 |
| **Seele / seelex** | Runtime |
| **Taus** | 任务生命周期 |
| **orca-agent** | 执行引擎 |

> 如果你想自己开发 Agent 产品而非用现成客户端，重点关注这些。

#### 4. 安全、权限和沙箱

Agent 进入生产环境后最容易出问题的不是生成质量，而是**权限和副作用**。

| 项目 | 解决问题 |
|------|---------|
| **boxsh** | 文件和进程隔离 |
| **bash-guard** | Shell 命令安全 |
| **pass-vault-v2** | 工具权限控制 |
| **orca-agent** | 长任务失败恢复、副作用幂等、安全门禁 |

> 这一类很可能是未来 Agent 基础设施里最重要的部分之一。

#### 5. 评测、验收和可观测性

Agent 说"任务完成了"不代表真的完成了。

| 项目 | 关注点 |
|------|--------|
| **goal-conditions** | 如何判断目标是否真正完成 |
| **evidence-harness** | 如何保存执行证据 |
| **ntkit** | 评估 Agent 完整过程 |
| **ATTEST-100** | Diff / 截图对比 |
| **Pulse** | 监控运行状态、Skill、Memory 和 Token 消耗 |

> 目前最容易被忽视、但最值得关注的一层。

#### 6. 垂直场景 Agent

不是通用 Harness，而是把 Agent 放进具体场景。

| 项目 | 场景 |
|------|------|
| **DataAgent / datafoundry** | 企业数据查询、SQL 和知识引擎 |
| **AI_MIDI** | 多轮对话修改 MIDI |
| **pi-rp** | 角色扮演 Agent 基础设施 |
| **whale-cli / LifeOS** | 学习和个人工作流 |
| **ChatLuna** | 基于 Koishi 的 IM 机器人平台 |
| **OpenPencil / Open Design / Canvas Prompt / FlowGrid** | 设计和创作工作流 |
| **OpenMinis** | iOS/Android 端侧 Agent |

> OpenPencil 展示了用 DeepSeek v4-flash 生成设计稿的视频，是评论区里少数有完整演示的项目。

#### 7. 渠道和平台接入

Agent 入口正在从聊天窗口扩展到 IDE、桌面、终端、企业 IM、手机和内部系统。

| 项目 | 接入渠道 |
|------|---------|
| **feishu-codex-bridge** | 飞书 |
| **con-terminal** | 终端 |
| **agent-teams-android** | 移动端 |

---

## 查询拓展

- DeepSeek Agent Harness 的官方定义和 API 是什么？内测招募的具体要求？
- pi-workbench 的"模型路由 + Agent Teams + Kanban"设计与 Hermes 的 Kanban/Cron 体系有何异同？
- RxyCode 内置评测 Harness 的架构？与 Hermes 的 verification-gate 模式对比？
- boxsh / bash-guard 的沙箱实现——容器化还是 syscall 级？
- evidence-harness 的执行证据保存机制——是否可以集成到 Hermes 的 cron 执行追踪？
- OpenMinis 端侧 Agent 在 iOS/Android 上的技术栈？

---

## 归纳总结

这篇推文的价值不在于介绍单个项目，而在于**绘制了 AI Agent 执行栈的完整分层图**：

```
┌─────────────────────────────────────────┐
│  7. 渠道接入 (飞书/终端/移动端/IM)         │ ← Agent 入口层
├─────────────────────────────────────────┤
│  6. 垂直场景 (数据/设计/RP/端侧)           │ ← 应用层
├─────────────────────────────────────────┤
│  2. 多 Agent 协作 (编排/任务流/交接)       │ ← 编排层
├─────────────────────────────────────────┤
│  1. Coding Agent 工作台 (IDE/桌面/项目)    │ ← 交互层
├─────────────────────────────────────────┤
│  3. Harness Runtime (上下文/工具/状态)     │ ← 执行内核
├─────────────────────────────────────────┤
│  4. 安全/沙箱 (隔离/权限/幂等)             │ ← 安全层
├─────────────────────────────────────────┤
│  5. 评测/验收/可观测性 (证据/监控)         │ ← 质量保证层
└─────────────────────────────────────────┘
```

这 7 层构成了从模型到生产级 Agent 应用的完整中间件栈。DeepSeek 的内测成为了这个生态的集中亮相窗口。

---

## 趋势判断

- **Agent 执行栈成为独立赛道**：模型层（DeepSeek/GPT/Qwen）之上正在形成一个完整的"Agent 中间件"市场，7 层分层已经清晰
- **安全沙箱层被严重低估**：评论区里安全项目最少但最关键——Agent 进入生产环境后的权限/副作用/幂等控制是刚需
- **评测验收层是下一个蓝海**：goal-conditions / evidence-harness / ATTEST-100 说明"如何判断 Agent 真的完成了任务"是当前最大的空白
- **Agent 入口多元化**：从聊天窗口扩展到飞书/终端/手机/IDE，Agent 正在变成无处不在的"数字员工"
- **DeepSeek 生态效应**：内测招募帖评论区变成了项目展示会，说明围绕 DeepSeek 的 Agent 生态已经自发形成

---

## 关联分析

- **与 Hermes Agent 的直接关联**：Hermes 本身就是第 3 层（Harness Runtime）+ 第 7 层（飞书渠道接入）的实现。这 7 层分层可以作为 Hermes 能力差距分析框架——Hermes 在第 4 层（安全沙箱）和第 5 层（评测验收）有提升空间
- **与用户 Harness 架构研究的关联**：用户已有 `harness-architecture`（六层 Harness 架构）和 `agent-workflow-orchestration`（工作流编排）Skill。这 7 层是补充视角——从社区实战项目角度验证了 Harness 分层
- **与 SkillOpt 的关联**：SkillOpt 解决的是第 5 层（评测验收）的前提条件——"可靠的验证器"。有了验证器，才能用 SkillOpt 训练技能。goal-conditions 和 evidence-harness 正在做这种验证器
- **与 FDE 商业模式的关联**：FDE 落地企业 AI 时，这 7 层就是完整的技术选型清单——每一层选一个工具组合成交付方案
- **与安全治理的关联**：用户已有 `agent-security-governance`（零信任安全基线）和 `deterministic-guardrails`（确定性护栏）Skill。boxsh / bash-guard 是同类思路的开源实现

---

*笔记创建：2026-08-06 · 来源：@Xsir01 推文*


## 相关笔记

- [AWS Context Ontology Accelerator](./2026-08-06-AWS-Context-Ontology-Accelerator-语义上下文层.md) — 语义上下文层方案
- [SkillOpt 微软技能优化器](./2026-08-06-SkillOpt-微软Agent技能训练优化器.md) — Skill 训练与 Harness 协同
- [Harness vs Loop vs Graph 三层实践指南](./2026-08-01-Harness-vs-Loop-vs-Graph三层实践指南.md) — Harness 架构选型方法论
- Copilot 范式三波进化（explore 目录）— Agent 编排范式演进
