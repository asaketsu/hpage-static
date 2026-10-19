# MANTA: 多 Agent 网络拓扑自适应 — 推理时自进化的协作架构

> **来源**：arXiv (cs.AI)
> **原文链接**：https://arxiv.org/abs/2607.28527
> **作者**：Mao-Xun Huang, Jerry Wang, Yi-Cheng Lai, Zhengxin Zhang, Claire Cardie, Hen-Hsen Huang
> **记录日期**：2026-08-01

**标签**：#多Agent #拓扑自适应 #自进化 #推理时优化 #协作架构 #Agent框架

---

## 一、内容详细整理

### 1.1 核心问题

多 Agent 系统（MAS）在复杂问题求解中展现了优势——任务分解、Agent 专业化、信息交换、中间验证。但现有系统将**通信拓扑视为固定设计或离线优化目标**，从未在执行过程中动态调整。

MANTA 提出一个核心问题：**多 Agent 系统能否在解决每个任务的同时，自改进其通信拓扑？**

这不同于以往依赖训练、离线搜索或预执行优化的方法。它需要三个能力：
- **实例条件化规划**（instance-conditioned planning）
- **测试时拓扑变异**（test-time topology mutation from traces）
- **跨运行经验迁移**（cross-run transfer without weight updates）

### 1.2 七层自我改进层次（关键理论框架）

论文提出了一个 Agent 系统自我改进的层次分类法（Figure 1），将现有工作按"被改进的对象"分层：

- **L0 输出层**：Self-Refine — 改进 Agent 生成的内容
- **L1 提示词层**：APO, APE, DSPy, MIPRO, PromptBreeder, TextGrad, GEPA — 改进指令文本
- **L2 推理轨迹层**：CoT, Self-Consistency, ToT, GoT — 改进中间推理结构
- **L3 技能/工具层**：ReAct, Toolformer, Voyager — 改进 Agent 的行动能力
- **L4 记忆层**：Reflexion, DC, Generative Agents, A-MEM, AWM, ACE — 改进跨交互的经验存储
- **L5 角色层**：CAMEL, ChatDev, MetaGPT, Debate, EoT, MALLM — 改进单个 Agent 的角色定义
- **L6 拓扑层**：MASS, AFlow, ADAS, AgentSquare, **MANTA** — 改进多 Agent 之间的组织方式
- **L7 权重层**：RLHF, SELF — 改进模型参数

> **MANTA 的定位**：L0-L5 改进的是 Agent **产出什么、观察什么、记住什么、执行什么**，MANTA 改进的是 Agent **如何被组织**。

### 1.3 系统架构

MANTA 包含两层嵌套结构：

**目标系统层**（target MAS）：通过推理、工具调用、消息交换来解决任务。
**编排层**（orchestration）：选择 Agent、通信链路、信息可见性——但不直接解决任务。

编排层由三个 LLM 组件 + 确定性代码组成：

- **Topology Planner（拓扑规划器）**：分析任务需求，产出紧凑计划——交互模式、Agent 数量、可选验证器或嵌套组。确定性代码将其展开为完整拓扑。
- **Trace Auditor（轨迹审计器）**：扫描结构化工件、工具记录、relay packets、置信度、未解决问题、证据可见性。报告**过程风险**（process risks），而非答案正确性。
- **Skill Reflector（技能反思器）**：每 N 次运行后更新长期 playbook 中的经验教训。

确定性代码负责：验证拓扑、运行 Agent、路由消息、控制修复、决定何时停止。

### 1.4 拓扑表示

拓扑规范定义了一个版本化且经验证的 MAS。关键概念：

- **结构角色（structural role）**：coordinator / worker / verifier / debater / voter — 决定图中的位置
- **阶段角色（stage role）**：worker（产出有证据支撑的贡献） / critic（检查并修订可见声明）
- **模式组（pattern groups）**：预定义交互结构，可嵌套——允许 Agent 将工作委托给子组
- **上下文策略（context policy）**：控制消息、发送者、共享证据的可见性、消息传播距离、是否接收完整或摘要报告

> **重要约束**：单 Agent 和六种固定工作流是拓扑表示的特例，支持嵌套组合。

### 1.5 编排循环（Orchestration Loop）

1. **查询条件化规划**：Planner 接收任务 + 经验记忆（无法访问 benchmark 标签或预定义拓扑），分析任务需求和潜在过程风险，产出交互模式、Agent 数量、可选验证器
2. **确定性代码展开**：将计划展开为完整拓扑，分配角色和上下文策略，验证所有结构约束
3. **回合执行**：按组结构递归执行拓扑。Agent 通过**结构化 relay packets** 通信（非原始转录本）——包含答案、证据、置信度、未解决问题。共享上下文控制器强制执行每个 Agent 的可见性策略
4. **工具去重 + 证据账本**：相同工具调用自动去重，append-only 证据账本保留跨分支的声明和支撑证据
5. **轨迹审计**：每回合后，Auditor 扫描结构化工件。可添加 trace-grounded 过程标志，但**不能查看 benchmark 答案**
6. **修复或最终化**：如果审计建议修复（至少一个中/高严重性标志可修复），Controller 批准**一次有界修复**（最多三个操作）；否则最终化答案
7. **修复后的最终回合**：在修订后的拓扑上运行最后一回合

### 1.6 两时间尺度 Playbook 记忆

- **短期 playbook**（this run）：记录本运行中每回合的拓扑、发现和决策
- **长期 playbook**（cross-run）：存储跨运行的持久原则——如何选择拓扑、经验教训。由 Skill Reflector 每 N 次运行批量更新

> **关键设计**：长期 playbook 只使用**过程信号**（process signals），从不接收 benchmark 判定。这确保了系统不会作弊。

### 1.7 拓扑变异操作符

修复时，Planner 产出最多三个变异操作：
- **添加或扩展 Agent**：如扩展过载 worker 为子组 hub
- **更改组模式**：如星形 → 两级树
- **编辑通信边**：如添加直接链接形成完全连接辩论
- **更改信息可见性**：如提升/降低可见性级别

确定性代码将操作应用到拓扑副本上，验证所有角色、引用、成员资格、嵌套和 Agent 限制。无效提案使用保守的修复编译器或被跳过。

### 1.8 实验设置

- **模型**：Gemma 4（Google DeepMind 2026）
- **评估方式**：每 benchmark 30 题，每实验 3 次独立运行取均值
- **五个 benchmark**：
  - BrowseComp — 多步信息检索与证据综合
  - StableToolBench — 可靠外部工具选择与执行
  - PlanCraft — 长程规划与依赖感知动作排序
  - WorkBench — 现实多步工作流
  - MATH — 结构化推理

### 1.9 关键实验结果

**总性能（Table 1 核心数据）**：

- MANTA 平均得分 **74.0**，超出最强基线 **5.8 个百分点**
- 在 PlanCraft 上取得最佳结果
- 在每个 benchmark 上都优于 Single Agent
- **MANTA 使用了所有 MAS 中最少的 token**——元操作仅占推理预算的约 **12%**

**基线对比**（部分代表性数据）：
- Voting 平均 64.7 | Group Chat Debate 65.5 | Fully Linked Debate 65.1
- Orchestrator w/o Discussion ~65 | AFlow / ADAS / AgentSquare / MASS 在 64-68 区间
- Single Agent 59.3 | Self-Refine 55.6 | CoT 50.0

**消融实验（Table 2）**：

- 完整 MANTA：成功率 71.7%，平均每运行 100,315 tokens
- 无初始 Topology Planner（用固定 coordinator-worker）：57.5%（**下降 14.2**）
- 无拓扑变异：60.8%（下降 10.9）
- 无长期 playbook 更新：67.5%（下降 4.2）
- 无长期 playbook：66.7%（下降 5.0）

> **核心发现**：初始拓扑规划是最大贡献者，执行时修复提供额外提升，跨运行学习提供增量收益。

**变异预算效果（Figure 4）**：
- 所有 4 个 benchmark 随预算增加而改善
- **第一次变异带来最大增益**，后续变异增益递减
- 预算 3 时覆盖最多困难任务

**长期 playbook 迁移性**：
- 同 benchmark 迁移：正面提升
- 跨 benchmark 迁移：唯一产生正面平均增益的方法
- 证明 playbook 学到了**可复用的结构知识**，而非 benchmark 专属工作流

### 1.10 拓扑演化案例（三典型案例）

**案例 1 — 扩展过载分支**：
- 初始：三星拓扑（coordinator + 2 workers）
- 问题：一个 worker 负责多个 facet 并遇到工具失败
- 修复：将该 worker 扩展为子组 hub（含子 Agent），拓扑从星形变为两级树
- 结果：仅增加受影响分支的分解和专业化

**案例 2 — 更改验证和执行顺序**：
- 问题 A：单 Agent 产出低置信度输出无验证 → 添加验证器形成两 Agent 链
- 问题 B：并行 Agent 尝试同一状态变更操作 → 星形改为链式串行化执行，防止重复应用

**案例 3 — 重布线和插入评审者**：
- 问题 A：PlanCraft 中三 Agent 过早达成共识（低置信度 + 问题未解决）→ 添加 worker-verifier 直接边，形成完全连接辩论。下一轮审计通过，置信度 1.0，得分 1.0
- 问题 B：Math500 中单 Agent 返回低置信度答案无人检查 → 插入一个 critic 角色的 Agent，形成辩论对。下一轮审计通过，置信度 1.0，得分 1.0

> **洞察**：添加的 Agent 不试图自己解题——它唯一的工作是检查已存在的答案。修复不总是"加更多解题者"，而是"加验证能力"。

---

## 二、查询拓展

### 2.1 relay packets 通信模式

relay packets 是 MANTA 设计的结构化通信单元，区别于传统 MAS 中常见的原始对话转录本（raw transcript）传递。每个 packet 包含四个字段：答案、证据、置信度、未解决问题。这种设计减少了 token 消耗（因为不需要传递完整的对话历史），同时保持了关键信息的可审计性。这与 ReAct 框架中的 thought-action-observation 三元组有异曲同工之处，但 MANTA 的设计更偏向跨 Agent 的信息聚合而非单 Agent 的推理链。

### 2.2 进程信号 vs 答案正确性

MANTA 的核心设计哲学之一是**审计器只看过程不看结果**。Trace Auditor 检测的是协作过程中的可观测异常——如过早共识、未验证的工具失败、低置信度输出——而非将 Agent 答案与 ground truth 对比。这一设计有两个关键含义：（1）系统在推理时无需标签数据；（2）过程信号与正确性有统计相关性但不等价（论文附录验证了这一点）。这种"不依赖标签的推理时自改进"范式与 Reflexion 的"不需要外部反馈的自我反思"一脉相承。

### 2.3 有界变异（Bounded Mutation）设计

MANTA 严格限制每次运行最多一次修复、最多三个操作。这与自动架构搜索（如 ADAS、AFlow）的"无界搜索"形成鲜明对比。有界设计的合理性在于：（1）避免无限循环的修复尝试消耗过多 token；（2）强制 Planner 每次修复都要精准——消融实验证明第一次变异贡献最大收益；（3）符合论文"inference-time" 而非"offline optimization" 的定位。这一设计与 Hermes Agent 的"单次重试后升级"原则高度一致。

### 2.4 Gemma 4 作为骨干模型

实验使用 Google DeepMind 2026 年发布的 Gemma 4 作为唯一骨干模型。这是一个值得注意的选择——MANTA 的效果不是靠大模型能力（如 GPT-5 / Claude 4.5）堆出来的，而是在中等规模开源模型上证明了拓扑自适应的价值。这意味着 MANTA 的架构创新可以移植到不同的模型基础设施上。

---

## 三、归纳总结

### 3.1 MANTA 编排循环框架

```
任务输入
  │
  ▼
┌─────────────────────────────────────┐
│  Topology Planner                    │
│  输入: 任务 + 长期 playbook           │
│  输出: 交互模式 + Agent 数 + 角色     │
│  约束: 看不到 benchmark 标签          │
└──────────────┬──────────────────────┘
               │ 确定性代码展开 + 验证
               ▼
┌─────────────────────────────────────┐
│  Turn Executor                       │
│  - 递归执行拓扑                       │
│  - relay packets 通信                 │
│  - 工具去重 + 证据账本                │
│  - 上下文可见性策略执行                │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│  Trace Auditor                       │
│  扫描: 工件/工具记录/置信度/证据       │
│  输出: 过程标志 (非答案正确性)         │
│  判定: clean → 最终化                 │
│        flagged → 触发修复             │
└──────────────┬──────────────────────┘
               │ if flagged
               ▼
┌─────────────────────────────────────┐
│  Controller + 修复                    │
│  - 最多 1 次有界变异 (≤3 操作)        │
│  - 添加/扩展 Agent                    │
│  - 更改模式/边/可见性                 │
│  - 验证后执行最终回合                  │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│  Finalizer                           │
│  投票 + 证据综合 → 最终答案           │
└─────────────────────────────────────┘
               │
    ┌──────────┴──────────┐
    ▼                     ▼
 短期 playbook        长期 playbook
 (本运行记录)     Skill Reflector 每 N 运行更新
```

### 3.2 七层自我改进层次

```
L7 权重层      RLHF, SELF          ← 需训练
L6 拓扑层      MANTA, MASS, AFlow   ← 本文焦点
─────────────────────────────────────
L5 角色层      CAMEL, ChatDev       ← 多 Agent 组织
L4 记忆层      Reflexion, A-MEM     ← 跨交互经验
L3 技能层      ReAct, Voyager       ← 行动能力
L2 轨迹层      CoT, ToT, GoT        ← 推理结构
L1 提示词层    DSPy, GEPA           ← 指令优化
L0 输出层      Self-Refine          ← 输出修订
```

> 越往上，改进的抽象层次越高，对模型权重和训练数据的依赖越低。

### 3.3 消融贡献分解

- 无初始规划：-14.2%（**最大贡献**，说明任务条件化拓扑选择至关重要）
- 无拓扑修复：-10.9%（第二大贡献，说明执行时变异有效）
- 无 playbook 更新：-4.2%（增量贡献，说明跨运行学习有价值）
- 无 playbook：-5.0%（基线参考）

> **启示**：初始规划 >> 执行时修复 > 跨运行学习。三层叠加但边际递减。

### 3.4 与自动 Agent 设计框架的对比

- **AFlow**：搜索预定义操作符 + 工作流级优化 — 离线搜索，执行时固定
- **ADAS**：LLM meta-agent 迭代提议改进 — 基于历史评估，执行前确定
- **AgentSquare**：模块化组合（agent/tool/memory/workflow）— 搜索空间大但执行前固定
- **MASS**：联合优化 prompt + 拓扑 — 最接近但仍是离线优化
- **MANTA**：唯一在执行过程中（inference-time）调整拓扑的系统

---

## 四、趋势判断

### 趋势1：推理时自改进从个体扩展到组织层面

MANTA 代表了一个重要趋势——推理时适应不再局限于 prompt 调整、推理链重构或记忆更新，而是扩展到了**协作架构本身**。论文的七层分类法（L0-L7）提供了一个清晰的路线图：未来研究可能继续向上探索 L7（权重层在线适应）或混合多层联动。

依据：消融实验证明拓扑层（L6）的自改进带来 5.8pp 的平均提升，不依赖任何模型权重更新。

### 趋势2：有界变异优于无界搜索

MANTA 的"最多一次修复、三个操作"设计取得了比无界搜索框架（AFlow、ADAS）更好的结果，同时使用更少 token。这暗示了在 MAS 架构优化中，**精准的局部修复可能比全局搜索更高效**。

依据：MANTA 平均 74.0 vs AFlow/ADAS/AgentSquare/MASS 64-68 区间，且 token 消耗最低。

### 趋势3：过程信号驱动的审计将成为标准

Trace Auditor 不依赖 ground truth 而是检测过程异常（过早共识、未验证失败、低置信度），这一范式可能在 Agent 系统中普及——因为实际部署中往往没有标签数据。

依据：论文附录验证了过程标志与正确性的统计相关性，且消融中去除审计+修复导致 10.9% 下降。

### 趋势4：Agent 系统将向"可重配置组织"演化

MANTA 展示了 Agent 系统从"固定流水线"到"可重配置组织"的转变。未来的 Agent 框架可能内置拓扑编辑能力作为标准功能，类似微服务架构中的动态服务发现与负载均衡。

依据：三案例（扩展分支/改验证顺序/重布线）展示了同一框架下多种重配置模式的实用性。

---

## 五、关联分析

### 5.1 与 Hermes Agent 多 Agent 编排的关联

Hermes 的四猫团队（Dev/OPM/Content/Data Meow）本质上是一种**固定拓扑**——明确的角色分工和消息路由。MANTA 的发现表明：

- 不同任务可能需要不同的拓扑（如纯分析任务可能不需要 Content Meow，但需要更多 Data Meow 并行）
- 执行中的审计可以检测到"过早共识"（如 Dev 和 OPM 都同意但证据不足）
- 一次性修复预算（MANTA 的有界变异）可以防止无限循环

**直接借鉴点**：Hermes 的 agent-orchestration-pattern skill 可以引入"任务条件化拓扑初始化"和"执行中审计触发"两个机制。

### 5.2 与 agent-primitive-architecture 三原语的关联

Hermes 的 Agent/Skill/Hook 三原语架构与 MANTA 的拓扑表示存在映射关系：

- MANTA 的"结构角色"（coordinator/worker/verifier）≈ Hermes 的 Agent 原语
- MANTA 的"长期 playbook"≈ Hermes 的 Skill 系统（可复用经验）
- MANTA 的"Auditor + Controller"≈ Hermes 的 Hook 系统（执行中拦截和修正）

### 5.3 与 Beyond-Leaderboard 六大失败模式的关联

精读笔记 [2026-07-09 Beyond the Leaderboard](2026-07-09-BeyondLeaderboard.md) 分析了 LLM Agent 的六大失败模式，其中"组合性鸿沟"和"脚手架边际递减"与 MANTA 直接相关：

- MANTA 的"有界变异"正是对"脚手架边际递减"的回应——第一次修复最有效，后续递减
- MANTA 的"扩展过载分支"直接解决了"组合性鸿沟"——当一个 Agent 承担过多子任务时分解为子组

### 5.4 与 EvoSOP 自进化工具生命周期的关联

精读笔记 [2026-07-10 EvoSOP](2026-07-10-EvoSOP.md) 分析了工具的 Construct/Merge/Evaluate/Prune 生命周期。MANTA 的拓扑变异操作（添加 Agent/改边/改可见性）可以视为"组织层面的 Construct"，而其有界预算和保守修复编译器则是"组织层面的 Prune"。

### 5.5 与 quant-trading A股系统的关联

量化交易系统中的多策略组合管理（multi-strategy portfolio）与 MANTA 的多 Agent 拓扑有结构性相似：

- 策略的组合方式（并行投票/串行验证/分层委托）对应不同的拓扑模式
- 交易执行中的风控审计（如 [Binding-Drift](2026-07-23-BindingDrift.md) 的高风险动作前交叉验证）对应 MANTA 的 Trace Auditor

---

## 六、金句摘录

> "Can a multi-agent system improve its communication topology while solving each individual task?"

> "Topology as a distinct layer of self-improvement, where effective adaptation may involve rewiring communication, changing execution order, or adding validation rather than simply increasing the number of agents."

> "The added agent never attempts the task itself; its only job is to check the answer that already exists."

> "MANTA achieves the lowest overall token consumption among the evaluated multi-agent systems."

---

## 七、行动启示与借鉴点评估

### 🔨 可直接移植（P0/P1）

**P0 — Hermes Gateway 执行中审计门禁**
- MANTA 的 Trace Auditor 证明"过程信号审计"无需 ground truth 即可有效检测问题
- 实施：在 Hermes 多 Agent 委派（delegate_task）后增加审计环节，检测过早共识/低置信度/未验证失败
- 关联现有 skill：agent-reliability-engineering（Circuit Breaker）、beyond-leaderboard-case-study
- 工作量：2-3 天（审计器 LLM prompt + Hook 集成）

**P0 — Agent 编排任务条件化拓扑初始化**
- MANTA 最大消融贡献（-14.2%）来自初始拓扑规划
- 实施：agent-orchestration-pattern skill 增加"任务分析→拓扑选择"前置步骤，不同任务类型映射不同默认拓扑（分析任务→Data Meow 主导，开发任务→Dev Meow 主导，内容任务→Content Meow 主导）
- 工作量：1-2 天（拓扑选择 prompt + 角色权重调整）

**P1 — 有界变异重试机制**
- MANTA 的"最多一次修复"设计直接对应 Hermes 的 retry 策略
- 实施：多 Agent 协作失败后，不是简单重试，而是"一次有界拓扑变异"（如添加一个验证 Agent 或改为串行执行）
- 工作量：3-5 天（变异操作定义 + 验证编译器）

### ⚠️ 需工程改造（P2）

**P2 — Relay Packets 结构化通信**
- MANTA 的 relay packets（答案+证据+置信度+未解决问题）比原始转录本更高效
- Hermes delegate_task 的消息传递可引入结构化 packet 格式
- 障碍：需修改 delegate_task 的消息序列化层，影响面较大

**P2 — 长期 Playbook 跨会话经验迁移**
- MANTA 的长期 playbook 在 Skill Reflector 定期更新中持续改进
- Hermes 的 Skill 系统已有类似机制（auto-skill + skill-review），但缺少"拓扑选择经验"的专门积累
- 实施：新增 "topology-playbook" 记忆类型，记录"某类任务用什么拓扑最有效"

### ❌ 暂不适用

**完整拓扑动态变异引擎** — MANTA 的完整编排层（Planner + Auditor + Controller + Reflector）是一个重量级系统，对 Hermes 当前的单/少 Agent 场景过于复杂。当前优先落实审计门禁和条件化拓扑初始化即可获得大部分收益。


## 相关笔记

- [本地CUA推理时扩展失效模式](./2026-08-02-本地CUA推理时扩展失效模式.md) — Agent推理时扩展的失效模式分析
- Agent编排陷阱与Harness控制面（~/explore/2026-07-30） — 多Agent编排架构与陷阱
