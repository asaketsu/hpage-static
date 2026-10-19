# 生产级 Multi-Agent Harness 设计全拆解

- 📅 2026-06-14
- ⭐ 5/5 — 极高质量的工程架构文章，从 Demo 到生产全链路拆解，方法论可直接对标自评
- 🏷️ #Multi-Agent #Harness #Agent架构 #工程实践 #MCP
- 📰 腾讯云开发者 · 李伟山
- 🔗 https://mp.weixin.qq.com/s/JPhcyDc4JwRmnMQ-76A-FQ

## 摘要

文章系统拆解了生产级 Multi-Agent Harness（多智能体执行框架）的八大模块：架构编排、工具治理、状态与记忆、评估体系、成本控制、MCP 接入、可观测性、落地路线。核心论点：**Demo 与生产之间的鸿沟由 Harness 决定**——Prompt 是台词，Agent 是演员，工具是道具，模型是大脑，Harness 是舞台的导演、调度系统、安全规章和票务系统。

---

## 一、Harness 是什么

> **Harness ≠ Prompt ≠ Orchestrator ≠ Agent Framework**

| 概念 | 解决什么 | 局限 |
|------|---------|------|
| Prompt | 让模型理解任务 | 不解决可靠性 |
| Orchestrator | 解决顺序 | 不解决资源/记忆/成本/安全 |
| Agent Framework（LangGraph 等） | 提供积木 | 不是生产建筑方案 |
| **Harness** | **统一收束能力、工具、状态、通信、编排、监控** | **完整工程方案** |

> Framework 是积木，Harness 是把积木拼成生产建筑的工程方案。

---

## 二、架构编排：Agent 出主意，Harness 拿决定

### 核心原则

> **Agent 负责局部智能，Harness 负责全局控制。**

大模型不是可靠的调度器——缺乏成本意识、并发意识、权限意识、全局一致性意识。

### Orchestrator 独占的五项决策权

1. **任务生命周期**：创建→规划→执行→审查→完成/失败
2. **执行计划裁决**：计划可来自 Planner，但执行控制权归 Orchestrator
3. **Agent 路由**：结合任务类型、能力、权限、历史质量评分
4. **失败处理**：重试/降级/跳过/终止——不能让出错 Agent 自己决定
5. **硬终止条件**：`max_steps`、`max_tokens`、`max_duration`、`max_tool_calls`

### 声明式 vs 命令式

```
声明式：{step: 1, intent: "research", agent: "researcher", input: "..."}
命令式：直接 await researcher.run("...")
```

> **别让 Agent 开车，让 Agent 当导航。** 声明式允许 Harness 介入：重排顺序、并行优化、拒绝步骤、安全审查。

---

## 三、工具治理：Tool Registry 是安全边界

> **工具不是函数调用，而是生产资源的对外授权点。**

### Tool Registry 九项必须元信息

| # | 元信息 | # | 元信息 |
|---|--------|---|--------|
| 1 | 工具名称 | 6 | 风险等级（低/中/高） |
| 2 | 工具描述 | 7 | 是否需要人工确认 |
| 3 | 输入参数 JSON Schema | 8 | 输出结果结构 |
| 4 | 允许调用的 Agent 列表（RBAC） | 9 | 审计日志策略 |
| 5 | 调用超时与速率限制 | | |

> **哪怕只有 3 个工具，也从第一天起强制走 Tool Registry。先有规矩，后扩规模。**

---

## 四、状态与记忆：记住该记的，忘掉该忘的

### 记忆的四种失败

| 失败方式 | 后果 |
|---------|------|
| 记得太少 | 无法复用经验 |
| 记得太多 | 上下文膨胀，成本爆炸 |
| 不分层 | 临时数据与长期知识混杂 |
| 不遗忘 | 过期信息污染决策 |

### State 三层架构

| 层级 | 生命周期 | 存储 | 用途 |
|------|---------|------|------|
| Working State | 当前步骤 | 内存 | 任务结束即丢 |
| Session State | 一次会话 | Redis + TTL | 多 Agent 共享 |
| Execution Log | 不可变 | 持久化 | 审计、回放、评估 |

### 记忆两类 + 遗忘机制

- **Episodic（事件记忆）**：踩坑、用户偏好、处理经验
- **Semantic（语义记忆）**：领域概念、业务规则、工具约束
- **遗忘评分**：基于访问频次 × 创建时间 × 重要性 × 最近使用 → 低分删除 / 中分压缩摘要 / 高分保留

> **记忆不是仓库，而是花园。需要定期修剪。**

---

## 五、评估体系：不只看答案，要看轨迹

### 只看最终答案会漏掉的信号

- 最终报告对了，但用了未授权数据源
- 最终代码能跑，但调了十几次无意义工具
- 某次成功只是因为重试撞上了正确答案

### 四层 Eval Pipeline

| 层级 | 评估内容 |
|------|---------|
| Component Eval | 单 Agent 是否选对工具、参数合规 |
| **Trajectory Eval** ⭐ | 步骤是否必要、顺序合理、是否循环（**Multi-Agent 最大创新点**） |
| Task Completion Eval | 是否满足目标、无事实错误 |
| End-to-End Eval | 用户采纳率、人工返工率、单位任务成本 |

### LLM-as-Judge 适用边界

| 适合 LLM-as-Judge | 不适合（应用确定性检查） |
|-------------------|------------------------|
| 表达完整性 | 事实正确性 |
| 推理连贯性 | 代码可运行性 |
| 总结质量 | SQL 结果、权限合规 |

> **Eval 必须进入 CI。Prompt 就是代码，工具 Schema 就是接口，执行轨迹就是日志，Eval 就是测试体系。**

---

## 六、成本控制：Token Budget 是生命线

### 三大策略

**策略一：Model Routing（模型路由）**

| 任务类型 | 模型选择 |
|---------|---------|
| 分类/摘要/格式转换 | 小模型 |
| 复杂推理/最终合成 | 强模型 |
| 高风险审查 | 强模型 + 规则校验双保险 |
| 低价值重试 | 禁止高价模型 |

**策略二：Context Compression（上下文压缩）**

保留最近几轮原文 + 更早历史压缩为结构化摘要。⚠️ 事实型任务保留原始引用；合规型任务关键证据不可压缩。

**策略三：Budget 分级降级**

```
🟢 绿区 >50%   → 正常执行
🟡 黄区 20-50% → 压缩上下文
🔴 红区 5-20%  → 切小模型 + 跳过 CoT
⛔ 熔断 <5%    → 强制收束，返回 partial result
```

### 核心运营指标

> **单位业务结果成本（每完成一个合格任务多少钱）** ← 可运营的标志

---

## 七、MCP 工具接入：标准化 ≠ 安全

> **MCP 之于 AI 工具，如同 USB-C 之于充电接口。**

### 五条最佳实践

| # | 实践 | 原因 |
|---|------|------|
| 1 | **永远不要把 MCP Server 直接暴露给 Agent** | 必须经过 Tool Registry |
| 2 | 每个 MCP Server 单独配额 | 防止流氓 Server 拖垮系统 |
| 3 | 工具做白名单而非黑名单 | 只开放真正需要的 |
| 4 | 高风险工具走 Human-in-the-Loop | 写入/删除/代码执行/支付 |
| 5 | 所有 MCP 调用打 Trace | 来源、参数、结果可追溯 |

> **MCP 让工具接入变得便宜，Harness 让工具调用变得可信。**

---

## 八、可观测性与落地路线

### 错误类型

Agent 的错误往往不是异常，而是**过程偏移**：调错工具、读错记忆、误解目标、压缩丢约束、路由用了能力不够的小模型。

### 三阶段落地

| 阶段 | 目标 | 关键组件 |
|------|------|---------|
| Phase 1 MVP | 跑通一条端到端闭环 | 最小 Orchestrator + Tool Registry + 基础 Trace + 评估数据集 |
| Phase 2 Hardening | Demo 变可控系统 | Budget + 权限 + 重试 + 压缩 + 轨迹评估 + 审计 + 回归测试 |
| Phase 3 Scale | 支撑多场景并发 | 分布式队列 + 多租户 + 动态路由 + 质量排行榜 + A/B 测试 + 成本看板 |

### 技术选型

- **小团队**：LangGraph / 轻量状态机 + FastAPI + Redis + PostgreSQL/pgvector + Langfuse/OpenTelemetry + LiteLLM 网关

### 十个灵魂问题

> 把这十个问题回答清楚，你就已经越过了大多数 Agent Demo 的边界：

1. 任务怎么进来？ 2. 谁负责拆解？ 3. 谁负责调度？
4. 工具怎么接？ 5. 状态放哪里？ 6. 记忆怎么检索？
7. 预算怎么控制？ 8. 轨迹怎么评估？ 9. 失败怎么处理？ 10. 审计怎么保留？

---

## 💡 启发

- **"别让 Agent 开车，让 Agent 当导航"** —— 声明式编排的精髓，Harness 保留全局控制权
- **记忆是花园不是仓库** —— 遗忘机制比记忆机制更难设计，但更关键
- **Trajectory Eval 是 Multi-Agent 最大创新点** —— 传统 Eval 只看答案，不看路径
- **MCP 标准化降低接入成本，但不降低安全风险** —— 接入越简单越要管权限

## 🔮 预判

- Harness 工程化能力将成为 Agent 团队的核心竞争力，而非模型选择能力
- "单位业务结果成本"会成为 Multi-Agent 系统的标准 KPI
- MCP + Tool Registry 的组合将成为工具治理标准模式

## 相关笔记
- [LoopEngineering vs Harness AI编程新范式](2026-06-14-LoopEngineering-vs-Harness-AI编程新范式.md) (关键词: Harness, AI编程)
- [Anthropic开源AI漏洞发现框架-Harness](2026-06-05-Anthropic开源AI漏洞发现框架-Defending-Code-Reference-Harness.md) (关键词: Harness)
- [RD-Agent-Quant multi-agent框架](explore/2026-05-18-RD-Agent-Quant-multi-agent-quant-framework-deep-dive.md) (关键词: Multi-Agent)
