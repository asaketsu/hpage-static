# Agent 两条路线：Harness vs Protocol-Native

> 来源：[@Potatoloogs (土豆本豆)](https://x.com/Potatoloogs/status/2060982941711491494) · 2026-05-31
> 标签：`#AI Agent` `#多Agent系统` `#Protocol` `#架构思考` `#Agent社会`

---

## 核心论点

Agent 发展分成两条路线，大部分讨论集中在第一条，但**第二条可能更值得关注**。

---

## 第一条路线：Harness 式多 Agent 系统

**本质**：Workflow Engine + Ontology，多个 Agent 共享上下文、共享目标、中心化调度。

**关键技术栈**：
- Prompt Engineering
- Context Management
- Task Routing
- Tool Calling
- Planning / Memory / Workflow

**本质仍属于软件工程问题**——Agent 更像可调用的函数、带人格的工具、任务节点。LLM Orchestration = 一个大模型调度多个子角色完成复杂推理。

> 所以当年擅长编程的人都重获新生。

---

## 第二条路线：Protocol-Native Agent System

**核心变化**：每个人拥有自己的 Personal Agent，甚至是**专属的无人公司**。

### 从 task-scoped 到 identity-scoped

| 维度 | 第一条路线 | 第二条路线 |
|------|-----------|-----------|
| Agent 性质 | 任务级实例 | 身份级实体 |
| 生命周期 | 任务结束即销毁 | 长期持续存在 |
| 拥有属性 | 无 | 记忆、身份、偏好、资源、权限、关系网络、利益边界 |
| 代表 | 工具 | 代表"你" |

### 为什么只能依赖协议？

当海量 Agent 独立存在时，它们之间必须解决：

1. **身份确认** — 你是谁
2. **权限边界** — 你能做什么
3. **信任机制** — 我怎么相信你
4. **委托关系** — 我把什么交给你
5. **协商机制** — 我们怎么达成一致
6. **激励机制** — 你为什么要做
7. **声誉系统** — 别人怎么评价你
8. **价值交换** — 怎么结算

> Agent 之间的交互已经不是 API Call，更像**制度性交互**。

### 核心转变

**AI 世界的核心会从 Prompt Engineering 转向 Protocol Engineering。**

---

## 协议即组织：三阶段演进

| 阶段 | 协议功能 | 代表 |
|------|---------|------|
| **传统互联网** | 数据通信 | TCP/IP、HTTP、SMTP — 发送和接收端约定说话格式 |
| **区块链** | 状态计算 | 以太坊 — 全网共同执行状态转换规则 |
| **Agent Society** | 组织协调 | 定义协调、权限、激励、身份、组织关系 — 协议承担"组织"功能 |

---

## 作者观点

> 现在读起来可能不太直观，因为第二条路线还没成为现实。但回想三年前有人说"LLM 提供基座能力、中间层提供原子能力、用户自己攒趁手的工具"。当时也觉得抽象，现在就是 vibe coding 的日常。第二条路线可能也是这样，过半年再看就能 get 到了。

---

## 思考

这篇推文精准捕捉了 Agent 演化的分水岭。第一条路线（Harness）是当前主流——我们的 Hermes + Kanban + Cron 本质上就是这条路。但第二条路线指向更深层的变革：当 Agent 成为个人数字身份的延伸时，Agent 间的协作不能靠中心化调度，只能靠**去中心化协议**。

**与我们系统的关系**：

| 我们的实践 | 对应路线 |
|-----------|---------|
| Hermes Gateway + Kanban 编排 | 第一条路线（Harness） |
| Memory Graph + 身份记忆 | 向第二条路线过渡的基础设施 |
| 三机交换池（exchange-protocol） | 第二条路线的雏形（Agent 间经验共享） |

**关键启发**：Protocol Engineering 的思维需要提前布局——身份、信任、权限、价值交换这些底层协议，值得在当前系统中就开始设计。

## 相关笔记
- [[2026-05-06-harness-engineering-落地实践|05-06-harness-engineering-落地实践]]
- [[2026-04-23-深入源码Hermes-Agent-Self-Improving|04-23-深入源码Hermes-Agent-Self-Improving]]
- [[2026-04-07-OpenClaw-autonomy-harness-loop|04-07-OpenClaw-autonomy-harness-loop]]
- [[2026-05-31-领域专长才是真正的护城河-Agent时代的价值重估|05-31-领域专长才是真正的护城河-Agent时代的价值重估]]
