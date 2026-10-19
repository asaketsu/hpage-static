# Agents From Scratch — LangChain 官方 Agent 构建四部曲：分诊→评估→HITL→记忆

> **来源**：[langchain-ai/agents-from-scratch](https://github.com/langchain-ai/agents-from-scratch)（GitHub，2.1k Star / 405 Fork / 196 commits，MIT）
> **作者**：LangChain 官方（LangGraph 团队）
> **记录日期**：2026-08-22
> **配套**：[Ambient Agents 博客](https://blog.langchain.dev/introducing-ambient-agents/) · [Agent Inbox](https://github.com/langchain-ai/agent-inbox) · LangGraph Studio

**标签**：#LangGraph #Agent构建 #HumanInTheLoop #Agent记忆 #Agent评估 #ContextEngineering

---

### 7 模块索引（本报告内容映射）

| 模块 | 对应章节 | 说明 |
|------|---------|------|
| tag 标签 | 头部标签行 | 6 个标签 |
| 出处 | 头部出处行 | GitHub 仓库 + LangChain 生态 |
| 内容整理 | 第一~四章 | 四部曲结构/各章详解/工程细节 |
| 查询拓展 | 第五章 | Ambient Agent 范式 + triage-workflow 混合 |
| 归纳总结 | 第六章 | 四层递进图 + 与 Hermes 对照 |
| 趋势判断 | 第七章 | 3 条预测 |
| 关联分析 | 第八章 | 与 5 篇已有笔记交叉 |
| 拓展应用推荐 | 第九章 | 可落地借鉴清单 |
| 指南分析 | 第十章 | 教程质量评估 |

---

## 一句话总纲

> **Agent 构建的官方教科书路线：先 triage+agent 混合架构，再评估（LLM-as-judge + 工具调用判分），再 HITL（interrupt + Agent Inbox），最后记忆（LangGraph Store 从反馈学习）——四层递进，每层一个 notebook + 可运行代码。**

---

## 一、内容详细整理

### 1.1 仓库定位

官方"从零构建 Agent"教程，最终产物是一个 **ambient agent**（环境代理）——连接 Gmail API 管理邮件。4 个 section，每个配 notebook + `src/email_assistant/` 完整代码。

**核心特点**：不是玩具 demo——每层递进都有真实工程约束（评估数据集/HITL 界面/持久化 Store/Gmail 真实 API）。

### 1.2 第 0 章：LangGraph 101（前置）

覆盖基础概念：

- chat models / tool calling 基础
- **agents vs workflows** 的区别（自主决策 vs 固定流程）
- LangGraph nodes / edges / memory
- LangGraph Studio 可视化调试

### 1.3 第 1 章：构建 Agent（triage + agent 混合架构）

**架构**：email triage step（分类工作流）+ 响应处理 agent（自主决策）的组合。

```
收到邮件 → [triage 工作流：分类/标记/路由] → [response agent：工具调用生成回复]
```

这是 LangChain 官方教程反复强调的模式——**固定流程的部分用 workflow（可控、可测），需要自主判断的部分才用 agent（灵活但有风险）**。分类交给确定性 workflow，响应策略交给 agent。

### 1.4 第 2 章：评估（Evaluation）

三层评估对象：

| 评估层 | 方法 |
|--------|------|
| 邮件回复质量 | LLM-as-a-judge |
| 工具调用正确性 | 断言工具选择/参数 |
| Triage 决策正确性 | 分类标签比对 |

**工具链**：Pytest（CI 集成）+ LangSmith `evaluate` API（追踪/指标/版本对比）。评估数据集在 `eval/email_dataset.py`。

**关键设计**：测试结果记录到 LangSmith 项目——可视化 trace、评估指标、**不同 Agent 实现的对比**（回归检测）。

### 1.5 第 3 章：Human-in-the-Loop（HITL）

**机制**：interrupt 暂停 + 人工审查特定工具调用（发邮件/定会议这类不可逆动作）。

**界面**：[Agent Inbox](https://github.com/langchain-ai/agent-inbox)——LangChain 官方 HITL 界面，人类在收件箱式 UI 里批准/编辑/拒绝 Agent 的工具调用。

```
Agent 决定 send_email → interrupt 暂停 → Agent Inbox 推送给人类
→ 人类 批准/编辑参数/拒绝 → Agent 继续/修正
```

### 1.6 第 4 章：记忆（Memory）

**机制**：从用户反馈学习，适应偏好——用 [LangGraph Store](https://langchain-ai.github.io/langgraph/concepts/memory/#long-term-memory) 持久化。

**数据流**：

```
人类在 HITL 中 编辑了 Agent 的草稿 → 编辑差异作为反馈信号
→ 提取偏好（"用户喜欢简短回复"/"称呼用 X"）→ 写入 Store
→ 下次生成时检索相关记忆注入 context
```

这是**记忆来自 HITL 交互**的闭环设计——不是预先灌入知识，而是从人类修正中持续学习。

### 1.7 工程细节（可复用）

- **Python 3.11+**（LangGraph 兼容性要求）
- **uv** 包管理（官方推荐，快且可靠）
- **可编辑安装**：notebook 依赖 `from email_assistant import ...`，必须 editable install
- **mock-first**：notebooks 用 mock 邮件/日历工具，Gmail 真实 API 单独一章
- **部署**：LangGraph Platform 一键部署 graph
- **测试**：`run_all_tests.py` 一键跑全套 + notebook 冒烟测试

### 1.8 未来扩展

LangMem 深度集成——后台记忆集合管理 + 记忆查询工具（Hot path 冷热分离）。

---

## 二、查询拓展

### 2.1 Ambient Agent 范式

LangChain 2026 主推的概念（配套博客《Introducing Ambient Agents》）：Agent 不是被动等你提问，而是**持续监听环境事件**（邮件到达/日历变更/通知），主动分类处理，只在需要人类决策时打断你。

与本机体系的呼应：Hermes 的 cron 主动推送/传感器扫描就是 ambient 模式——Agent 不只在对话里响应，还在后台持续工作。

### 2.2 Triage-Workflow + Agent 混合：为什么不是纯 Agent

纯 Agent（所有决策都交给 LLM 自主）的问题：分类这种确定性任务也走 LLM = 不可控 + 慢 + 贵。官方教程的解法：

| 任务类型 | 架构 | 原因 |
|----------|------|------|
| 邮件分类（newsletter/紧急/普通） | **workflow**（固定 prompt 分类） | 规则明确、需要稳定、可单测 |
| 响应策略（回什么/怎么回） | **agent**（工具调用自主决策） | 情况多变、需要灵活 |

这与 Anthropic 的 "Building effective agents" 观点一致：workflow 能解决的不用 agent。

### 2.3 Agent Inbox：HITL 的产品化

Agent Inbox 是 LangChain 开源的通用 HITL 界面——把"人类审批 Agent 动作"做成收件箱交互。任何 LangGraph interrupt 的 agent 都能接入。**HITL 从代码机制（interrupt 函数）上升为产品界面**，这是 Agent 可信度建设的关键一步。

### 2.4 LangGraph Store vs 传统 Memory

- 传统 memory：对话历史（thread-level，短期）
- LangGraph Store：**跨 thread 持久化记忆**（namespace 隔离，长期）——"用户偏好简短回复"这种事实不属于任何一次对话

这解决了"每次对话重新学习偏好"的问题，是 Agent 从工具到助手的分水岭。

---

## 三、归纳总结

### 3.1 四层递进架构图

```
L0 基础：LangGraph 101
    ↓ nodes/edges/memory + agents vs workflows
L1 功能：triage(workflow) + response(agent) 混合
    ↓ 分类可控 + 响应灵活
L2 质量：评估体系
    ↓ LLM-judge(回复) + 断言(工具调用) + 分类比对(triage)
L3 可信：HITL
    ↓ interrupt + Agent Inbox 审批不可逆动作
L4 进化：记忆
    ↓ 从 HITL 反馈学习偏好 → Store 持久化 → 注入 context
    ↓
最终形态：ambient agent（Gmail 真实部署）
```

### 3.2 与 Hermes 体系对照

| 教程层 | Hermes 对应 | 状态 |
|--------|-------------|------|
| triage + agent 混合 | Hermes Gateway 的消息路由 + Agent 决策 | ✅ 同构 |
| 评估（LLM-judge） | content-judge skill | ✅ 已有 |
| 评估（工具调用断言） | skill-stress-test 对照实验 | ⚠️ 部分覆盖 |
| HITL interrupt | 用户确认机制（[ACTION REQUIRED]） | ⚠️ 有机制无产品界面 |
| Agent Inbox 式界面 | 飞书卡片审批（lark-approval skill） | ⚠️ 场景化未通用 |
| 记忆闭环（反馈→偏好） | TieredMemory L1/L2/L3 | ⚠️ 有存储缺"从修正学习"提取器 |

---

## 四、趋势判断

### 趋势 1：Ambient Agent 将取代对话式 Agent 成为默认形态

> 依据：LangChain 官方主推 + 本机 Hermes 的 cron/传感器实践已验证。被动问答的 Agent 利用率天然低，主动监听+按需打断才是"数字员工"形态。

### 趋势 2：HITL 将产品化为独立界面层

> 依据：Agent Inbox 作为独立开源项目发布。interrupt 是代码机制，但审批需要好界面——收件箱隐喻（批量处理/优先级/过滤）会被更多 Agent 产品采用。

### 趋势 3：评估驱动开发（EDD）成为 Agent 工程标配

> 依据：教程把 evaluation 放在 HITL/记忆之前（第 2 章）——先有度量再谈可信。LangSmith 的"实现对比"把回归检测带进 Agent 开发，类似 CI 之于 Web 开发。

---

## 五、关联分析

### 5.1 与 [2026-08-11-从零构建托管式AI-Agent-服务端循环会话与工具调用.md](2026-08-11-从零构建托管式AI-Agent-服务端循环会话与工具调用.md) 的关联

那篇笔记覆盖"服务端 Agent 的循环会话/工具调用"基础设施层，本仓库在其上加了**评估/HITL/记忆**三层。互补：那篇讲"怎么跑起来"，本篇讲"怎么可信+进化"。

### 5.2 与 [2026-08-13-AI-Agent记忆架构2026前沿-MemoryOS-三层存储-Mem0-vs-Letta选型.md](2026-08-13-AI-Agent记忆架构2026前沿-MemoryOS-三层存储-Mem0-vs-Letta选型.md) 的关联

那篇对比记忆框架选型（MemoryOS/Mem0/Letta），本仓库的 LangGraph Store 是第四个选项——**框架原生记忆**（不引入独立记忆系统，直接用 Agent 框架的 Store）。

**选型启示**：如果 Agent 主框架是 LangGraph，Store 原生方案集成成本最低；跨框架才需要 Mem0/Letta。

### 5.3 与 [2026-08-21-EnvHarness环境脚手架-环境与Agent共进化的Google新范式.md](2026-08-21-EnvHarness环境脚手架-环境与Agent共进化的Google新范式.md) 的关联

EnvHarness 是**训练侧**的自进化（环境针对弱点施压），本仓库第 4 章记忆是**部署侧**的自进化（从用户修正学习）。两者互补成完整进化闭环：训练期用 EnvHarness 拉能力，部署期用反馈记忆适偏好。

### 5.4 与 [2026-08-22-PMSkill2.0-产品经理工作蒸馏工厂-21个Skill三层架构.md](2026-08-22-PMSkill2.0-产品经理工作蒸馏工厂-21个Skill三层架构.md) 的关联

pm-skills 的"6 角色评审"与本仓库的"Agent Inbox 人工审批"都是**人类判断注入点**——前者在方案层（事前），后者在执行层（事中）。共同趋势：Agent 自主性越强，人类介入点越要设计得精准。

### 5.5 与 Hermes 自身架构的关联

- **评估层差距**：Hermes 有 content-judge（输出质量）但缺"工具调用正确性断言"——教程第 2 章的三层评估（回复/工具/triage）中，工具调用断言正是 skill-stress-test 补齐的方向
- **记忆提取器差距**：TieredMemory 有 L1/L2/L3 存储，但缺"从用户 HITL 修正中自动提取偏好"的机制——教程第 4 章的反馈差异分析是可借鉴实现
- **Ambient 验证**：本机 cron 主动推送体系已是 ambient 实践，教程提供了官方架构背书

---

## 六、拓展应用推荐

### 6.1 可直接借鉴的 4 个机制

1. **三层评估分层**：输出质量（LLM-judge）/ 工具调用（断言）/ 路由决策（分类比对）——补齐 skill-stress-test 的"工具调用断言"层
2. **反馈差异提取记忆**：用户编辑 Agent 输出时，diff 就是偏好信号——可给 Hermes 的语音纠错/笔记修改场景加"偏好提取器"
3. **不可逆动作 interrupt 名单**：发消息/删文件/付款类动作强制 HITL——映射到本机的 [ACTION REQUIRED] 机制，可产品化为飞书审批卡片
4. **triage-workflow 与 agent 分界原则**：确定性任务走 workflow（可控可测），判断性任务走 agent（灵活）——选型时先问"这个步骤规则明确吗"

### 6.2 学习路径建议

- 先跑 LangGraph 101 notebook（半天）理解 graph 抽象
- 重点读 evaluation.ipynb（第 2 章）——评估是四层中最容易迁移的
- hitl.ipynb + Agent Inbox 本地部署体验审批流
- memory.ipynb 的 Store API 可对照 TieredMemory 评估

### 6.3 与 LangGraph 编排技能联动

本机已有 langgraph-orchestration skill——本仓库是该 skill 的官方实战补充，四部曲 notebook 可作为 skill 的 references 素材。

---

## 七、指南分析

### 7.1 教程质量

- **递进设计好**：四层每层独立成章，前层是后层基础——可按需取用
- **代码完整**：notebook + src 完整实现 + tests，非伪代码
- **工程真实**：mock-first 但有 Gmail 真实集成 + LangGraph Platform 部署
- **生态闭环**：LangSmith（追踪）/ Agent Inbox（HITL）/ Store（记忆）——官方全家桶但各组件可单独借鉴思想

### 7.2 局限

- **深度绑定 LangChain 生态**：interrupt/Store/LangSmith 是 LangGraph 特有——思想可迁移但代码不可直接移植到其他框架
- **单场景**：email assistant 一种场景，多 Agent/长时程任务未覆盖
- **评估数据集小**：教学级规模，生产级评估体系需要更大更全的数据集
- **Python only**：无 TS/其他语言版本

---

## 八、金句摘录

> "These section build from the basics of agents, to agent evaluation, to human-in-the-loop, and finally to memory."（四层递进的官方路线）

> "Agents vs Workflows" ——LangGraph 101 的第一课：不是所有任务都该用 agent

> 记忆章节核心：从用户反馈学习，adapt to preferences over time——记忆不是灌入的，是从修正中长出来的

---

## 九、行动启示

- **评估分层补齐**：skill-stress-test 的下一步加"工具调用断言"层（借鉴教程第 2 章三层评估）
- **偏好提取器原型**：用户修正笔记/纠错时，diff 分析提取偏好写入 memory——低成本的记忆进化试点
- **interrupt 名单显式化**：把"不可逆动作需确认"从原则变成显式清单（发消息/删文件/付款/部署），配飞书审批卡片
- **ambient 架构背书**：本机 cron 主动体系与官方 ambient agent 方向一致，可继续深化（传感器→决策→打断的节奏设计）

---

> **延伸阅读**：
> - 仓库：https://github.com/langchain-ai/agents-from-scratch
> - Ambient Agents 博客：https://blog.langchain.dev/introducing-ambient-agents/
> - Agent Inbox：https://github.com/langchain-ai/agent-inbox
> - [从零构建托管式 AI Agent](2026-08-11-从零构建托管式AI-Agent-服务端循环会话与工具调用.md) — 基础设施层互补
> - [AI Agent 记忆架构 2026](2026-08-13-AI-Agent记忆架构2026前沿-MemoryOS-三层存储-Mem0-vs-Letta选型.md) — 记忆选型对照
> - [EnvHarness 环境脚手架](2026-08-21-EnvHarness环境脚手架-环境与Agent共进化的Google新范式.md) — 训练侧进化互补

## 相关笔记

- [从零构建托管式 AI Agent](2026-08-11-从零构建托管式AI-Agent-服务端循环会话与工具调用.md) — 服务端循环与工具调用
- [EnvHarness 环境脚手架](2026-08-21-EnvHarness环境脚手架-环境与Agent共进化的Google新范式.md) — 环境与代理共进化范式
- [Context Management POMDP 形式化](~/explore/2026-08-18-context-management-pomdp-formalization-deep-dive.md) — Agent 记忆与上下文的理论基座