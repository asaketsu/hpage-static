# Agent Harness Engineering：知识体系总纲与索引

> **类型**: 原创知识体系总纲（索引笔记）
> **日期**: 2026-07-31
> **标签**: `Agent-Harness` `Agentic-Engineering` `Loop` `Harness` `FDE` `知识索引`

---

## 核心结论

Agent Harness Engineering 是 AI Agent 从"玩具"走向"生产系统"的核心方法论。它不是一个单一技术，而是由 **Loop（循环执行）→ Harness（控制框架）→ FDE（现场部署）** 三层构成的完整工程体系。本笔记是知识总纲，串联已积累的 40+ 篇相关笔记。

---

## 一、三层体系：Loop → Harness → FDE

```
┌──────────────────────────────────────────────────────┐
│              Agentic Engineering 三层体系              │
├──────────────────────────────────────────────────────┤
│                                                      │
│  第三层: FDE (Forward Deployed Engineer)              │
│  把 Agent 从实验室带到现场, 解决最后一公里落地         │
│  ▲                                                   │
│  │  现场需求挖掘 → 快速 POC → 集成 → 调试 → 反馈     │
│  │                                                   │
│  ──────────────────────────────────────────────      │
│                                                      │
│  第二层: Harness (控制框架)                           │
│  定义 Agent "怎么工作"的工程化约束和保障机制           │
│  ▲                                                   │
│  │  上下文管理 / 工具权限 / 质量门禁 / 安全沙箱       │
│  │  状态持久化 / Checkpoint / 可观测性 / 评估闭环     │
│  │                                                   │
│  ──────────────────────────────────────────────      │
│                                                      │
│  第一层: Loop (执行循环)                              │
│  Agent 的基本执行单元 — 感知→推理→行动→观察→再推理    │
│  ▲                                                   │
│  │  ReAct Loop / 多轮对话 / 工具调用 / 自我修正       │
│  │                                                   │
│  ──────────────────────────────────────────────      │
│                                                      │
│  底座: LLM (大语言模型)                              │
│  提供推理与生成能力                                   │
└──────────────────────────────────────────────────────┘
```

| 层 | 核心问题 | 关键技术 |
|----|---------|---------|
| **Loop** | Agent 怎么一步步执行？ | ReAct / ReWOO / 多轮工具调用 / 自我修正 |
| **Harness** | 怎么保证执行可控、可信、稳定？ | 上下文分层 / 质量门禁 / 安全沙箱 / 评估闭环 / 可观测性 |
| **FDE** | 怎么把 Agent 真正落到客户现场？ | 现场需求挖掘 / 快速 POC / 系统集成 / 反馈迭代 |

---

## 二、Harness Engineering 的核心原则（来自 AGENTS.md）

你的 Hermes AGENTS.md 已定义了 5 条 Harness Engineering 准则：

| 原则 | 说明 | 对应笔记 |
|------|------|---------|
| **上下文分层加载** | L1 常驻（AGENTS.md，<40% 填充率）/ L2 阶段触发（Skill 按需）/ L3 按需查询（Wiki） | 上下文管理类笔记 |
| **执行/评判分离** | 做事的 Agent 和审查的 Agent 必须分开 | Multi-Agent Harness 设计 |
| **质量门禁机械化** | "检查通过"不算通过，"exit_code=0 && tests>0"才算 | 评估闭环类笔记 |
| **Dry Run 先行** | 新 Skill/新流程上线前必须空跑验证 | 实践类笔记 |
| **规范即活文档** | 每发现一个错误，就工程化消除其再发可能 | 全部笔记的写作动机 |

---

## 三、知识图谱：40+ 篇笔记分类索引

### A. 理论基础与范式定义（7 篇）

| 笔记 | 核心内容 |
|------|---------|
| **2026-04-30 Harness-Engineering即控制论** | Harness = 控制论在 AI 中的应用 |
| **2026-05-25 Agent-Harness-Engineering-从Prompt到Harness的范式跃迁** | 从 Prompt 工程到 Harness 工程的范式转变 |
| **2026-05-26 Agent架构关键变化-Harness成为新后端** | Harness 正在取代传统后端 |
| **2026-05-31 agent两条路线-harness-vs-protocol** | Harness 路线 vs Protocol 路线 |
| **2026-06-14 LoopEngineering-vs-Harness-AI编程新范式** | Loop 工程 vs Harness 工程 |
| **2026-06-15 Agentic-Engineering三层体系-Loop-Harness-FDE** | 三层体系的完整定义（本笔记的源头） |
| **Loop工程已死-Graph工程永生** | 从 Loop 到 Graph 的演进 |

### B. Loop 执行循环（6 篇）

| 笔记 | 核心内容 |
|------|---------|
| **2026-04-07 agent-loop-core-scheduling** | Agent Loop 的核心调度机制 |
| **2026-04-07 OpenClaw-autonomy-harness-loop** | OpenClaw 自主权 Harness Loop |
| **2026-05-14 手撸Agent-ReAct-Loop从零实现** | ReAct Loop 从零实现 |
| **2026-06-15 Loop-Engineering-Prompt之后的下一个范式** | Prompt 之后是 Loop 工程 |
| **2026-06-01 eval-loop评估闭环消灭slop** | Eval Loop 消灭 AI 幻觉/低质量输出 |
| **AgentLoop经验自进化闭环-Agent越用越准** | Agent Loop 经验自进化 |

### C. Harness 设计与架构（8 篇）

| 笔记 | 核心内容 |
|------|---------|
| **2026-05-06 harness-engineering-落地实践** | Harness 工程落地实践 |
| **2026-05-07 Harness-Engineering-AI-Coding-90%-实战** | AI Coding 90% 实战 |
| **2026-06-11 Agent-Harness自我修复架构-四层自动闭环** | 四层自我修复自动闭环 |
| **2026-06-14 生产级Multi-Agent-Harness设计全拆解** | 生产级 Multi-Agent Harness 全拆解 |
| **2026-07-17 HarnessVLA冻结大模型变可调度接触技能的记忆引导Agent架构** | Harness VLA 记忆引导 |
| **2026-07-26 Agentic上下文管理与自进化Agent记忆架构** | 上下文管理与自进化记忆 |
| **Harness-Engineering-载具设计研究报告** | Harness 用于载具设计 |
| **langchain-harness-memory-analysis** | LangChain Harness 记忆分析 |

### D. MCP 协议与工具生态（2 篇）

| 笔记 | 核心内容 |
|------|---------|
| **2026-04-23 MCP协议与Agentic-LLM-2025趋势** | MCP 协议定义与趋势 |
| **2026-04-27 MCP协议生态与Agentic-RAG架构深度学习** | MCP 生态 + Agentic RAG |

### E. 安全、评估与可观测性（2 篇）

| 五步流程 | 涉及笔记 |
|---------|---------|
| 安全加固 | Anthropic开源AI漏洞发现框架 |
| 评估闭环 | eval-loop评估闭环消灭slop |

### F. 具身智能与机器人 Agent（5 篇）

| 笔记 | 核心内容 |
|------|---------|
| **2026-06-23 AgenticROS自然语言操控ROS2** | 自然语言操控 ROS2 |
| **2026-07-14 Agentic-RL用强化学习训练AI自主决策** | Agentic RL |
| **2026-05-24 Cloudflare-Agents-Week-2026-Agentic-Cloud全栈基础设施** | Agentic Cloud 基础设施 |
| **2026-05-25 高德OPC自主增长系统-Harness多Agent架构** | 高德 OPC 多 Agent 架构 |
| **2026-08 多个具身智能笔记** | VLA Action Head / Gemini Robotics / ABot-N1 |

### G. 应用实践与行业落地（8+ 篇）

| 笔记 | 核心内容 |
|------|--------- |
| **2026-05-07 Superpowers-Agentic技能框架** | Agentic 技能框架 |
| **2026-05-14 MATLAB-Agentic-Toolkit分析** | MATLAB Agentic 工具包 |
| **2026-05-21 react-agent-llm-agentic-training-research** | Agent 训练研究 |
| **2026-05-31 agent两条路线-harness-vs-protocol** | 两条路线之争 |
| **2026-06-08 Harness壁垒崩塌人人创建的时代来了** | Harness 壁垒崩塌 |
| **2026-06-08 Google Agentic RAG多智能体框架** | Google Agentic RAG |
| **2026-06-14 LoopEngineering-vs-Harness-AI编程新范式** | Loop vs Harness 新范式 |
| **2026-07-26 Agentic上下文管理与自进化Agent记忆架构** | 自进化记忆架构 |

### H. 最新融合：生产级 Agent（2 篇）

| 笔记 | 核心内容 |
|------|---------|
| **2026-07-31 AI-Agent从玩具走向企业级生产系统** | 核心痛点 + 五步落地流程（刚保存） |
| **2026-07-31 FDE工程师岗位解析** | FDE = 三层体系的顶层执行者（刚保存） |

---

## 四、核心概念矩阵

### Loop 的三种形态

| 形态 | 特点 | 代表 |
|------|------|------|
| **ReAct Loop** | 感知→推理→行动→观察→再推理 | 经典 Agent Loop |
| **Eval Loop** | 生成→评估→反馈→修正 | 消灭 slop（低质量输出） |
| **Self-Evolution Loop** | 使用→积累经验→自我改进→越用越准 | AgentLoop 经验自进化 |

### Harness 的五大支柱

| 支柱 | 说明 | 生产级对应 |
|------|------|-----------|
| **上下文管理** | 分层加载，<40% 填充率 | 短/中/长分层记忆 |
| **工具治理** | MCP 协议 + 权限三层模型 | 统一协议适配层 |
| **质量门禁** | exit_code=0 才算完成 | 基准测试集 + 灰度发布 |
| **安全沙箱** | 输入审查 + 权限隔离 + 输出审核 | 三层安全防护 |
| **评估闭环** | Eval Loop 持续改进 | OpenTelemetry 全链路 |

### FDE 的核心价值

> 技术突破只是上半场，现场落地才是决胜的下半场。FDE 是打下半场的人。

| FDE 能力 | Harness 对应 |
|---------|-------------|
| 现场需求挖掘 | 上下文管理（理解客户真实场景） |
| 快速 POC | Loop（快速迭代原型） |
| 系统集成 | 工具治理（MCP 协议适配） |
| 调试排障 | 评估闭环（全链路可观测性） |
| 反馈迭代 | 自进化 Loop（经验回传产品） |

---

## 五、演进脉络：从 Prompt 到生产级系统

```
时间线:

2024  Prompt Engineering (提示词工程)
  ↓   "怎么说能让 LLM 听话"
  
2025  Loop Engineering (循环工程)
  ↓   "让 Agent 一步步执行任务"
  
2025  Harness Engineering (控制框架)
  ↓   "让 Agent 可控、可信、稳定"
  
2026  Agentic Engineering (Agent 工程学)
  ↓   "Loop + Harness + FDE 三位一体"
  
2026  Production Agent (生产级系统)
      "稳定批量 + 可控可信 + 成本可控"
```

---

## 六、与 Hermes 的直接关系

Hermes 的 AGENTS.md 本身就是 Harness Engineering 的实践范例：

| AGENTS.md 条目 | Harness 层 |
|----------------|-----------|
| 上下文一次性原则 | 上下文管理 |
| 质量门禁机械化 | 质量门禁 |
| Harness Engineering 五条准则 | Harness 核心 |
| 工具权限三层模型 | 安全沙箱 |
| 龙虾法则（Hal Stack） | 规范即活文档 |
| SESSION BOOT | 状态持久化 |

---

## 七、关键术语速查

| 术语 | 说明 |
|------|------|
| **Loop** | Agent 执行循环（ReAct/Eval/Self-Evolution） |
| **Harness** | 控制框架，保证 Agent 可控可信稳定 |
| **FDE** | Forward Deployed Engineer，把 Agent 推向现场 |
| **ReAct** | Reasoning + Acting，经典 Agent Loop |
| **Eval Loop** | 生成→评估→反馈→修正闭环 |
| **MCP** | Model Context Protocol，工具标准化协议 |
| **质量门禁** | exit_code=0 && tests>0 才算通过 |
| **Slop** | AI 生成的低质量/幻觉输出 |
| **Sandbox** | 安全隔离执行环境 |
| **Checkpoint** | 断点续跑快照 |
| **OTel** | OpenTelemetry，全链路可观测性 |

---

## 八、后续建议

| 优先级 | 建议 |
|--------|------|
| **P0** | 在 Hermes 中实际验证"Eval Loop"——建立自动化评测流水线 |
| **P1** | 把飞机结构设计专家模型的训练纳入 Agentic RL 框架 |
| **P2** | 研究 HarnessVLA 在具身智能中的落地（与 Gemini Robotics 2 呼应） |
| **P3** | 关注 Miles/SGLang 在 RL 后训练中的实践 |


## 相关笔记

- [AI Agent 从玩具走向企业级生产系统](./2026-07-31-AI-Agent从玩具走向企业级生产系统.md) — 同期姊妹篇，生产化落地流程
- [AI Agent 可靠性科学从失败模式到优雅降级](./2026-07-13-AI-Agent可靠性科学-从失败模式到优雅降级.md) — 可靠性工程基础
- [Agent 并行工具调用与投机执行](./2026-07-27-Agent并行工具调用与投机执行架构.md) — Harness 内部执行优化
- [自进化 Agent 2026 三层进化矩阵](./2026-07-06-自进化Agent2026-三层进化矩阵与源码级重写.md) — Agent 进化理论框架
- [AI Agent 自进化与记忆系统 2026 最新架构](./2026-07-23-AI-Agent自进化与记忆系统-2026最新架构.md) — 记忆层与进化层结合
