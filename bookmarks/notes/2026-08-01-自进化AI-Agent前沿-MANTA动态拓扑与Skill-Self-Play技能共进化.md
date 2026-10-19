# 自进化 AI Agent 前沿：MANTA 动态拓扑 + Skill Self-Play 技能共进化框架

> **来源**：arXiv 2026年7月最新论文 + EvoAgentX 综述仓库
> **记录日期**：2026-08-01
> **搜索方式**：arXiv Atom API 直搜 + TinyFish + HN Algolia（Tavily 432 配额耗尽，全程降级链）

**标签**：#AI-Agent #自进化 #多智能体系统 #Skill-Self-Play #MANTA #EvoAgentX #记忆优化 #Agent记忆

---

## 一、内容详细整理

### 1.1 核心论文一览

| 论文 | arXiv ID | 核心创新 | 实验增益 |
|------|----------|---------|---------|
| **MANTA** | 2607.28527 | 多 Agent 网络拓扑推理时自进化 | 5 基准平均 74.0 分，超最强 baseline +5.8pp |
| **Skill Self-Play (Skill-SP)** | 2607.22529 | 技能共进化：proposer + solver + skill controller | 工具使用+推理任务性能上限持续提升 |
| **Causal-AgentIR** | 2607.21125 | 分层多 Agent + 自进化因果记忆图 | 图像修复知识可增/改/合/强化/遗忘 |
| **ReasoningBank** | 2509.25140 | 推理记忆规模化 Agent 自进化 | — |

### 1.2 MANTA：推理时网络拓扑自进化

**MANTA (Multi-Agent Network Topology Adaptation)** 打破了传统多 Agent 系统将通信拓扑视为固定设计参数的惯例。

**核心机制 — 三阶段自适应**：

1. **任务条件拓扑初始化**：执行前从先前的结构经验中初始化一个与任务条件相关的拓扑
2. **协作轨迹监控**：部署期间监控 Agent 协作轨迹，检测当前组织结构是否充分
3. **有界结构更新**：当组织不足时执行受限的结构调整——可修改 Agent 角色、通信链路、执行顺序、信息可见性和验证路径，但保持任务接口和 Agent 预算不变

**关键设计决策**：
- **有界更新**（bounded updates）——不是推翻重建，而是增量修改，保留任务接口不变
- **结构经验记忆**——从历史拓扑结构中学习，实现跨任务迁移
- 推理时自改进扩展到了协作架构本身

**实验结果**：
- 5 个基准（信息检索、工具使用、规划、工作流执行、数学推理）
- 平均分 74.0，超最强 baseline 5.8 个百分点
- PlanCraft 基准上取得最佳结果

### 1.3 Skill Self-Play：技能共进化突破 LLM 能力天花板

**Skill-SP** 解决了 LLM 自进化的核心矛盾——**任务多样性 vs 验证可靠性**：

- **环境绑定方法**：获得精确反馈，但学习被困在狭窄领域
- **开放式自生成**：拓宽任务空间，但缺乏可靠验证，误导性奖励污染训练循环

**Skill-SP 的中间路线**：将 **Agent 技能**作为调和此矛盾的桥梁：
- 每个技能确保在特定场景下的深度可验证执行
- 跨技能的动态路由维持开放式任务多样性

**三组件共进化架构**（RL 循环编排）：

| 组件 | 职责 | 机制 |
|------|------|------|
| **Proposer（提议者）** | 生成具有挑战性的任务 | 基于动态采样的技能条件生成 |
| **Solver（求解者）** | 探索候选解法 | 推送能力边界 |
| **Skill Controller（技能控制器）** | 收集执行反馈 | 更新和扩展技能库 |

**核心价值**：有效弥合了**结构化验证**与**开放式探索**之间的鸿沟。对初始对齐不良的模型有显著的逆转效果（striking turnarounds）。

> **开源代码**：https://github.com/Qwen-Applications/skill-self-play

### 1.4 Causal-AgentIR：自进化因果记忆图

**突破点**：将 Agent 记忆从非结构化文本摘要升级为**结构化因果记忆图**。

**记忆图结构**：
- 节点：退化模式、图像区域、修复工具、动作、质量变化、用户偏好
- 边：因果关系（特定修复操作/工具序列如何在不同退化条件下影响修复质量）

**记忆操作**（远超简单 CRUD）：
- 添加（add）、更新（update）、合并（merge）、强化（reinforce）、忽略（ignore）、丢弃（discard）
- 全部基于观察到的质量变化和反馈驱动

**六 Agent 协作系统**：规划 Agent + 退化分析 Agent + 工具专家 Agent + 因果记忆推理 Agent + 结果批判 Agent + 记忆策展 Agent

---

## 二、查询拓展

### 2.1 EvoAgentX 生态系统全景

**EvoAgentX**（GitHub 3193 stars，2026-07-31 活跃更新）是当前最完整的自进化 Agent 开源框架。

**五层模块化架构**：

| 层级 | 名称 | 功能 |
|------|------|------|
| L1 | Basic Components | 基础组件层 |
| L2 | Agent | Agent 定义与管理 |
| L3 | Workflow | 工作流编排 |
| L4 | **Evolving** | **进化层：集成 3 种 MAS 优化算法** |
| L5 | Evaluation | 评估层 |

**进化层集成的三种优化算法**：
- **TextGrad**：通过文本梯度优化 Agent prompt
- **AFlow**：自动化 Agent 工作流生成
- **MIPRO**：多指令提示优化

**实验增益**（EvoAgentX 论文 arXiv:2507.03616）：
- HotPotQA F1 提升 7.44%
- MBPP pass@1 提升 10.00%
- MATH 解决率提升 10.00%
- GAIA 整体准确率提升最高 20.00%

### 2.2 Awesome-Self-Evolving-Agents 综述分类体系

EvoAgentX 团队维护的综述仓库（arXiv:2508.07407）将自进化 Agent 技术分为**三大方向**：

**方向一：单 Agent 优化**
- 1.1 LLM 行为优化（训练型：SFT/RL；测试时：反馈型/搜索型/推理型）
- 1.2 Prompt 优化（编辑型/进化型/生成型/文本梯度型）
- **1.3 记忆优化**（⭐ 与 Hermes 最相关）
- 1.4 工具优化（训练型/推理时/功能性）
- 1.5 统一优化

**方向二：多 Agent 优化**
- 2.1 自动多 Agent 构建
- 2.2 MAS 优化（CORAL/R&D-Agent/AFlow/ADAS/GPTSwarm 等）

**方向三：领域特定优化**
- 3.1 生物医学（STELLA/HealthFlow/MedAgentSim）
- 3.2 编程（Darwin Gödel Machine/OpenEvolve/Live-SWE-agent）
- 3.3 科学研究（PiFlow）
- 3.4 金融与法律

### 2.3 记忆优化方向关键论文（与 Hermes 高度相关）

| 论文 | 核心贡献 | 对 Hermes 的启发 |
|------|---------|-----------------|
| **A-MEM** (2502.12110) | Agentic Memory for LLM Agents | 记忆作为 Agent 可操作对象 |
| **Mem0** (2504.19413) | 生产级可扩展长期记忆 | 生产级记忆架构 |
| **Memory-R1** (2508.19828) | RL 增强 LLM Agent 记忆管理能力 | 记忆管理本身可通过 RL 优化 |
| **ReasoningBank** (2509.25140) | 推理记忆规模化自进化 | 推理过程本身就是可进化的记忆 |
| **Agent Workflow Memory** (2409.07429) | 工作流记忆 | Skill 工作流的记忆化 |
| **Memento** (2508.16153) | 无需微调 LLM 的 Agent 微调 | 通过外部记忆实现"微调"效果 |

---

## 三、归纳总结

### 3.1 自进化 Agent 技术成熟度阶梯

```
Level 0: 静态 Agent（固定 prompt + 固定工具）
  ↓
Level 1: Prompt 自优化（TextGrad/GEPA/EvoPrompt）
  ↓
Level 2: 记忆增强（A-MEM/Mem0/Agent Workflow Memory）
  ↓
Level 3: 技能自进化（Skill-SP/EvoAgent/Darwin Gödel Machine）
  ↓
Level 4: 工作流自进化（AFlow/EvoAgentX/ADAS）
  ↓
Level 5: 多 Agent 拓扑自进化（MANTA/CORAL/AgentNet）
  ↓
Level 6: 完全自主进化（Darwin Gödel Machine：开放式自我改进）
```

### 3.2 三大共性问题与解决方向

| 问题 | 传统方案 | 自进化方案 | 代表论文 |
|------|---------|-----------|---------|
| **任务多样性 vs 验证可靠性** | 二选一 | 技能作为中间桥梁 | Skill-SP |
| **拓扑固定导致协作次优** | 人工设计/离线优化 | 推理时有界结构更新 | MANTA |
| **记忆退化/遗忘/冲突** | 静态文本摘要 | 因果记忆图 + 六操作 | Causal-AgentIR |

### 3.3 对 Hermes 生态的直接价值映射

| 前沿技术 | Hermes 对应组件 | 差距/机会 |
|---------|----------------|----------|
| MANTA 拓扑自进化 | 固定四猫团队（Dev/OPM/Content/Data） | ⭐ 可实现任务条件动态团队重组 |
| Skill-SP 技能共进化 | evolver Skill + auto-skill | ⭐ 当前是单向沉淀，缺少 proposer/solver 对抗循环 |
| Causal-AgentIR 因果记忆 | MEMORY.md + session_search | ⚠️ 当前是扁平文本，缺少因果图结构 |
| EvoAgentX 进化层 | evolver + skill-review | ⚠️ 缺少 TextGrad/MIPRO 等算法集成 |
| Memory-R1 RL 记忆管理 | 记忆手动写入 | ⚠️ 记忆管理策略本身未优化 |

---

## 四、趋势判断

### 趋势1：Agent 记忆从"存储"走向"推理"——Memory-R1 范式

Memory-R1（2508.19828）标志着记忆管理的范式转变：不再把记忆当作被动的存储和检索，而是用 RL 优化记忆管理策略本身——什么时候存、存什么、如何压缩、何时遗忘。这与 Hermes 当前手动 memory 工具调用形成代差。

### 趋势2：技能库从"静态沉淀"走向"对抗共进化"——Skill-SP 范式

Skill-SP 的 proposer-solver 对抗循环意味着技能库不再是错误修复的单向沉淀（Hermes evolver 当前模式），而是一个持续被挑战和扩展的活系统。proposer 不断生成当前技能库无法解决的任务，倒逼技能进化。

### 趋势3：多 Agent 拓扑从"设计时"走向"推理时"——MANTA 范式

MANTA 证明了通信拓扑可以在推理时有界自进化。这对 Hermes 的四猫团队架构有直接启发——不同任务可能需要不同的团队组合和通信路径，而非固定的"所有任务都走 Dev→OPM→Content→Data"。

### 趋势4：自进化 Agent 综述已经形成完整分类学——技术成熟度标志

EvoAgentX 团队的综述（arXiv:2508.07407）覆盖了 2023-2025 三大方向上百篇论文，形成了完整的分类体系。这意味着自进化 Agent 已从"探索期"进入"工程化期"——开源框架（EvoAgentX/MASLab）开始整合多种优化算法到统一平台。

---

## 五、关联分析

### 5.1 与 evolver Skill 的关联

> evolver 当前实现了"错误模式分析→规则沉淀→经验闭环"，对应自进化 Level 2-3。Skill-SP 的共进化框架可以为 evolver 增加 proposer 循环：自动生成当前 Skill 库无法处理的任务场景，倒逼 Skill 扩展。

### 5.2 与 agent-primitive-architecture 的关联

> Agent 三原语架构（Agents/Skills/Hooks）中的 Skills 层，对应 Skill-SP 的技能库概念。MANTA 的拓扑自进化直接影响 Agents 层的动态组合方式。

### 5.3 与 Darwin Skill 2.0 分析笔记的关联

> 此前已分析的 Darwin Gödel Machine（开放式自我改进 Agent）属于 Level 6 完全自主进化。Skill-SP 是其技术前提——只有技能库可以共进化，才能支撑完全自主的 Agent 进化。

### 5.4 与 Hermes 四猫团队架构的关联

> MANTA 的推理时拓扑自适应直接挑战当前固定的四猫团队（Dev/OPM/Content/Data）路由模式。不同任务类型可能需要不同的猫组合和通信路径——例如纯数据分析任务可能只需要 Data Meow 的深度自治，而不需要 OPM 的优先级仲裁。

---

## 六、金句摘录

> 「Inference-time self-improvement can extend to the architecture of collaboration itself.」— MANTA 论文核心论断。推理时自改进不再局限于 prompt 或工具，而是扩展到协作架构本身。

> 「Each skill ensures deep, verifiable execution in a specific scenario, while dynamic routing across skills maintains open-ended task variety.」— Skill-SP 对"技能"作为多样性-可靠性桥梁的精准定义。

> 「Restoration experience can be added, updated, merged, reinforced, ignored, or discarded according to observed quality changes and feedback.」— Causal-AgentIR 对记忆六操作的完整定义，远超 CRUD。

---

## 七、行动启示

- **P0：为 evolver 增加 Skill-SP 式的 proposer 循环**——当前 evolver 是错误驱动的被动沉淀，增加一个 proposer 组件主动生成"当前 Skill 库的盲区任务"，倒逼技能扩展
- **P1：评估 EvoAgentX 框架的 TextGrad/MIPRO 集成**——EvoAgentX 已开源（3193 stars），其进化层的 TextGrad 算法可直接用于优化 Hermes Skill prompt
- **P1：研究 Memory-R1 的 RL 记忆管理**——将记忆管理从"手动写入"升级为"RL 优化的自动策略"
- **P2：实验 MANTA 式的任务条件团队路由**——替换固定的四猫分配，实现按任务类型动态选择猫组合
- **P2：将 MEMORY.md 从扁平文本升级为因果记忆图**——借鉴 Causal-AgentIR 的图结构，支持多跳因果推理

## 相关笔记

- [MANTA 多 Agent 拓扑自适应](explore/2026-08-01-MANTA多Agent拓扑自适应.md) — MANTA 框架的详细拆解笔记
- [HiSkill 分层技能图](explore/2026-07-29-HiSkill分层技能图.md) — Skill Self-Play 的技能图基础，分层技能组织
- [LLM 自进化为何崩溃](explore/2026-07-21-LLM自进化为何崩溃-自合成数据信息增益.md) — 自进化的信息增益陷阱，Skill Self-Play 需要规避的失败模式
- [Agent 蒸馏与长程规划 2026](explore/2026-07-29-Agent蒸馏与长程规划2026-MAD-OPD与Physics-of-Planning.md) — MAD-OPD 长程规划，自进化 Agent 的规划层
- [具身智能数据引擎与自进化学习](2026-08-01-具身智能数据引擎与自进化学习-ACE-Data-0与Criticality-Model.md) — Criticality Model 与自进化学习的交叉
