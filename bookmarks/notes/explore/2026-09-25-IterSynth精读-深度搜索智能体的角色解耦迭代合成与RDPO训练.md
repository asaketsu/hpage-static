# IterSynth精读-深度搜索智能体的角色解耦迭代合成与RDPO训练

> **来源**：arXiv (Tencent)
> **原文链接**：https://arxiv.org/abs/2609.29444
> **代码**：https://github.com/Tencent/IterSynth
> **作者**：Xingyu Wu, Yuchen Yan, Yongliang Shen 等（浙江大学 + 腾讯）
> **记录日期**：2026-09-25

**标签**：#论文精读 #LLM智能体 #强化学习 #GRPO #深度搜索 #角色解耦

---

## 一、内容整理

### 1.1 核心问题：ReAct 单策略深搜的两大顽疾

深度搜索（Deep Search）要求 LLM 智能体分解复杂查询、检索证据、合成有据答案。现有 ReAct 式开源智能体（SFT + outcome RL 流水线）存在两个结构性缺陷：

- **角色耦合（Role Coupling）**：单一策略要同时承担规划、查询 formulate、证据过滤、缺口识别、冲突消解、最终合成六种异构能力。一个未分化的策略全包，导致过早终止、冗余搜索、浅层证据使用
- **上下文累积（Context Accumulation）**：长程搜索不断堆叠检索段落、中间思考、部分结论，有用证据被淹没，早期错误传播到后续决策。实测（Appendix H）：即使 64K 上下文，BrowseComp 上 ReAct 轨迹 **59% 以上在上下文耗尽前无法终止**

现有解法的不足：
- **多智能体方案**（不同子任务分给不同模型）：降低单模型认知负担，但推理成本↑、部署复杂度↑、协调开销↑
- **摘要式方案**（IterResearch 每 step 重建工作区、AgentFold 主动折叠上下文、ReSum 周期性 summarize-and-reset）：部分缓解上下文累积，但探索与整合仍耦合同一决策流

### 1.2 IterSynth 双角色迭代工作流

核心设计：**同一策略参数 + 角色专属 prompt + 动作约束**，交替执行 Planner 与 Synthesizer 两个子步。

**Planner（规划者）— 控制搜索轨迹**
- 观测：原始问题 q + 当前全局摘要 M_t（**不观测完整历史**，只看紧凑状态）
- 动作空间：`search(q_t)` 发新查询 / `answer(â)` 终止并给最终答案
- 职责：识别缺失信息、formulate 可搜索子问题、决定终止时机

**Synthesizer（合成者）— 维护持久记忆**
- 触发：Planner 选择 search 后，环境返回检索结果 TR_t
- 观测：当前状态 + Planner 决策 + 检索证据
- 动作：产出推理轨迹 + 更新后的全局摘要 M_{t+1}
- 约束：**只能做记忆更新**，不能发查询也不能给最终答案

状态转移：`s_{t+1} = (q, M_{t+1})` — 检索历史被摘要替换，上下文始终紧凑。这是「summary as persistent state」的关键：搜索历史不进上下文，进摘要。

### 1.3 两阶段训练配方

**阶段一：冷启动 SFT（结构初始化）**
- 用 Qwen3.5-397B-A17B 在真实搜索环境中 rollout 双角色循环，合成多轮轨迹
- 过滤管线：修复无效工具调用、剔除幻觉推理步、只保留可验证正确答案的轨迹
- 产出 ~10K 高质量轨迹，展开为 per-turn 样本（每个 Planner/Synthesizer 响应都是独立监督目标）
- Qwen3-8B 全参 SFT

**阶段二：RDPO（Role-Decoupled Policy Optimization）**

三个关键机制：

1. **多轮轨迹展开**：每个查询 G 个 rollout，每条轨迹 T_i 轮迭代，产生 Σ T_i 个交互轮（而非仅 G 个轨迹级样本）
2. **复合奖励**：`r_{i,t}^ρ = r_acc,i + α · r_rubric,i,t^ρ`
   - 终端精度奖励 r_acc ∈ {0,1}，均匀广播到轨迹所有轮
   - LLM judge 对每个中间行为按 **五维 rubric** 打分，Planner 和 Synthesizer 各一套
3. **角色解耦组优势**：奖励按角色分成两个池，各自独立归一化
   - `A_{i,t}^ρ = (r_{i,t}^ρ - μ_q^ρ) / σ_q^ρ`
   - 解耦优势直接插入标准 GRPO 目标，无其他算法修改

**Rubric 构造（Appendix C，三阶段蒸馏）**：
- Stage 1：SFT 策略在 held-out 查询上 rollout，收集 20 对正负对比轨迹（同查询，一对一错）
- Stage 2：Claude-4.6-Sonnet 独立分析每个对比对，分别给 Planner/Synthesizer 生成区分好坏行为的评价标准（规划侧：子查询精度、终止时机；合成侧：证据忠实度、离题信息抑制）
- Stage 3：合并语义重复项，每角色收敛为 **恰好 5 条 rubric**，冻结后用于整个 RL 阶段
- 训练时 judge 用 Gemini-2.5-flash-lite（成本与质量平衡），每轮调用两次（各评一个角色）

### 1.4 关键实验结果

**主实验（Table 1，五个基准：BrowseComp / BrowseComp-ZH / GAIA / xBench-DS-2505 / 2510）**

- IterSynth-8B 平均分 **50.7**，≤8B 组第一，超最强小智能体 MiroThinker-v1.0-8B **+4.2 分**
- BrowseComp-ZH 提升最大：55.4 分，超小智能体基线 **+15.2 分**（探索密集型任务收益最高）
- **跨级别竞争力**：8B 参数 surpass ReSum-30B、AgentFold-30B、OpenSeeker-30B-SFT，接近 IterResearch-30B 与 WebSailor-V2-30B（不到 1/3 参数预算）
- 与基础模型+工具组对比：仍低于 GPT-5 High（69.8）等前沿闭源，但 GLM-4.7（64.1）以下的开源基础模型被全面超越

**训练方法消融（Table 2）**

- IterSynth-SFT：44.1 → +outcome-only GRPO：48.9 → +RDPO：**50.7**
- 关键对照 **w/o RD**（同复合奖励但混合角色归一化）：**47.2，甚至低于纯 GRPO**
- 结论：仅加 turn-level rubric 奖励不够，密集的 Synthesizer 侧奖励与稀疏的 Planner 侧奖励**共享单一基线会纠缠信用信号**——解耦归一化才是增益来源

**角色互换消融（Table 3，单角色替换回未训练 Qwen3-8B）**

- Synthesizer 替换：平均 **-17.4**（58.9 → 41.5）
- Planner 替换：平均 **-41.1**（58.9 → 17.8）
- 解读：**规划是更高需求的角色**——弱 Planner 产出坏子查询污染全程证据收集，Synthesizer 无力回天；而弱 Synthesizer 场景下，训练过的 Planner 能通过针对性追查部分补偿

**免训练 prompting 范式（Table 5.1）**

- IterSynth 作为纯 prompt 工作流直接用于前沿闭源模型：
  - Claude-4.5-Opus：ReAct 60.6 → IterSynth **66.1**（+5.5）
  - DeepSeek-V3.1：ReAct 43.4 → IterSynth **47.9**（+4.5）
- 超过同样做迭代上下文重建的 IterResearch，证明「分离搜索控制与证据整合」是通用结构先验，不依赖特定模型行为

**补充**：Appendix J 显示轻量 not-attempted 重采样策略可将额外推理算力稳定转化为精度增益。

## 二、查询拓展

### 2.1 GRPO 与组相对优势

Group Relative Policy Optimization：同一 query 的 G 个 rollout 组内归一化优势（减组均值除组标准差），免 critic。IterSynth 的 RDPO 本质是**把组维度从"轨迹"细化到"角色×轮次"**——同一条轨迹里 Planner 子步和 Synthesizer 子步进入不同归一化池。这与此前精读的 GRPO 优势估计缺陷谱系（Spurious Advantage、Sign Balance）同属一个谱系：归一化基准选错，信用信号就被污染。

### 2.2 深搜智能体的上下文管理路线

- **IterResearch**：每步从演化报告重建聚焦工作区
- **AgentFold**：主动折叠（proactive folding）维持紧凑工作记忆
- **ReSum**：周期性 summarize-and-reset
- **IterSynth 的差异**：不是"事后压缩"而是"结构性前置"——摘要不是上下文的压缩产物，而是**唯一的持久状态**，检索原文根本不进入后续轮次
- 与 MemDecay（区域感知 KV 驱逐）、ODA（按需注意力读取）正交：那些在 token/KV 层做，IterSynth 在工作流层做

### 2.3 角色 prompt 分离 vs 多智能体

IterSynth 强调「同一参数、不同 prompt」——角色特化通过 prompt + 信息访问 + 动作约束实现，不需要两个模型。这与 MeowBot 团队的四猫架构（共享一个模型，角色由 system prompt 定义）完全同构。论文的价值在于用 Role-swap 消融证明了这种 prompt 级角色分工经过 RL 后确实产生了**功能性的角色能力**（不是结构摆设）。

## 三、归纳总结

### 3.1 核心框架：双角色迭代合成

```
        ┌─────────────────────────────────────────┐
        │            原始问题 q（固定）              │
        └──────────────────┬──────────────────────┘
                           │
        ┌──────────────────▼──────────────────────┐
        │  Planner（每轮）                          │
        │  输入: q + 全局摘要 M_t                    │
        │  输出: search(q_t) 或 answer(â)           │
        └───────┬─────────────────────────────────┘
                │ search(q_t)
                ▼
        ┌─────────────────────────────────────────┐
        │  环境 E → 返回检索结果 TR_t                │
        └───────┬─────────────────────────────────┘
                │ TR_t
                ▼
        ┌─────────────────────────────────────────┐
        │  Synthesizer（每轮）                      │
        │  输入: s_t + Planner决策 + TR_t           │
        │  输出: 更新后摘要 M_{t+1}（仅记忆更新）      │
        └───────┬─────────────────────────────────┘
                │
                ▼  s_{t+1} = (q, M_{t+1}) —— 历史被摘要替换
```

### 3.2 RDPO 信用分配链

```
终端 r_acc（0/1，广播全轨迹）
         │
         ├── Planner 池: {r_acc + α·rubric^P} → 组内归一化 → A^P
         │                                    （跨 rollout × 轮次聚合）
         └── Synthesizer 池: {r_acc + α·rubric^S} → 组内归一化 → A^S
                                              │
                                              ▼
                              标准 GRPO 策略更新（零算法改动）
```

### 3.3 三层递进的增益来源

- 工作流层（SFT 44.1）：结构先验 = 角色分离 + 摘要状态
- RL 层（GRPO 48.9）：outcome 信号优化搜索行为
- 信用层（RDPO 50.7）：角色池归一化解耦信用 —— 单独贡献 +1.8，且 w/o RD 反跌至 47.2 证明混合归一化是**负贡献**

## 四、趋势判断

### 趋势1：深搜智能体的竞争焦点从"训练算法"转向"工作流×训练协同设计"

依据：论文结论原话「jointly designing agent workflows and role-aware optimization methods」。纯 outcome RL（GRPO）在同 workflow 下只加 4.8 分，而 workflow 换成 IterSynth 后免训练就+4.5~5.5。工作流是放大器，训练算法是精修器。

### 趋势2：单模型 + prompt 角色分工将挤压小规模多智能体系统

依据：多智能体的成本/协调开销 vs 同参数角色切换的零额外部署。IterSynth 8B 打 30B 多智能体方案（ReSum-30B 仅 33.3）。当 RL 能真正优化 prompt 定义的角色能力时（Table 3 证明），独立小模型分工的性价比下降。

### 趋势3：过程奖励（rubric）的正确用法是"角色隔离"而非"直接混合"

依据：w/o RD 消融——同样的 rubric 奖励混合归一化后 47.2 < 纯 GRPO 48.9。过程奖励的密度差异（Planner 稀疏/Synthesizer 密集）使共享基线成为毒药。预示后续工作会把"归一化分组粒度"当作一等公民超参。

### 趋势4：小模型 + 结构先验逼近大模型的路径确立

依据：8B 达到 30B 级性能（50.7 vs 56.8-58.3）。与 LFM2.5-2.6B 端侧 Agent（此前精读）同一趋势：结构红利 > 参数红利。

## 五、关联分析

### 5.1 与 PACT（2026-09-23 精读）的关联

PACT 解决 LLM RL 信用分配的唯一表示与评论家对齐；RDPO 是同一问题的另一解法——不建 critic，而是**按角色分组归一化**实现信用隔离。两者对照：PACT 在值函数层做对齐，RDPO 在优势归一化层做隔离。

### 5.2 与 GRPO优势估计缺陷谱系（2026-09-06）的关联

该笔记记录 Spurious Advantage 与 Sign Balance 修正。RDPO 的 w/o RD 消融（47.2 < 48.9）是又一个"归一化基准污染信用"的实证案例，可加入缺陷谱系：**角色异质性奖励混合归一化**是第六类缺陷。

### 5.3 与 ContextPilot（2026-08-31）及 MemDecay（2026-07-15）的关联

三者都在治"上下文累积"病：ContextPilot 用细粒度 RL 决定信息进出上下文；MemDecay 在 KV 层做区域感知驱逐；IterSynth 在工作流层让摘要成为唯一状态。三个正交层次可叠加——Hermes 的 context-compressor（渐进式压缩，工具输出落盘只留摘要）本质就是 IterSynth 的摘要状态思想在 Agent 工具层的应用。

### 5.4 与 MeowBot 四猫架构的关联

Planner/Synthesizer 共享参数、prompt 分角色、动作空间隔离 —— 与四猫（Dev/OPM/Content/Data）"同一模型不同 system prompt"完全同构。Table 3 的角色互换消融给四猫架构提供了实证支持：角色分工需要"训练/沉淀"才能产生真实能力差异，仅靠 prompt 摆结构不够。

### 5.5 与 Ecdysis（2026-09-12）四角色拆解的关联

Ecdysis 的 FDCR 四角色（失败聚合与修复）与 IterSynth 双角色都属"harness 级结构修复优于模型特异迁就"流派。

## 六、金句摘录

> 「even with a 64K context, ReAct trajectories on BrowseComp fail to terminate before context exhaustion in over 59% of cases」— 上下文长度治标不治本的量化证据

> 「dense Synthesizer-side rewards and sparser Planner-side rewards should not share a single baseline, as doing so entangles their credit signals」— RDPO 的核心洞察，一句话讲清消融结果

> 「IterSynth provides the structural foundation, while RDPO converts this prior into stable long-horizon behavior」— 工作流与训练的关系定位

## 七、行动启示

- **对 Hermes 深搜类 skill**：analysis-pipeline / deep-analysis / arxiv-deep-research 可借鉴 Planner-Synthesizer 交替模式——每轮检索后立即让"合成者视角"产出/更新结构化摘要，后续检索决策只基于摘要而非累积原文，控制上下文膨胀
- **对多角色 Agent 评估**：Table 3 的 role-swap 消融是低成本可复用的评估法——把某角色 prompt 换成空白基线，测性能跌幅即可量化每个角色的真实贡献
- **对 RL 训练实践**：任何多角色/多阶段轨迹的 GRPO 训练，优势归一化必须按角色分组，混合归一化可能比不加过程奖励还差

## 八、拓展应用推荐

### 8.1 Hermes Gateway 的角色感知上下文管理（P0 潜力）

IterSynth 的「摘要为唯一持久状态」可直接落地：长会话中工具输出（terminal/search 结果）已有 context-compressor 落盘机制，可升级为**角色交替式摘要更新**——每轮工具调用后由合成视角产出增量摘要替换原始输出，Planner 视角的下一步决策只读摘要。预计显著降低长 cron 任务（如 watchdog、集群巡检）的上下文占用。

### 8.2 借鉴点优先级评估（Hermes / Jetson / 量化）

- **P0 — 摘要状态工作流**：analysis-pipeline skill 的检索循环改造。增量价值：现有 skill 只做"分析完落盘"，不做"每轮摘要替换"。工作量：一个 cron 会话内可验证
- **P0 — Role-swap 消融评估法**：用于验证四猫架构角色贡献。现有 skill 均未覆盖角色有效性量化。工作量：设计一个对比实验（某猫 prompt 置空 vs 完整）
- **P1 — 角色分组归一化**：若未来做 Agent 轨迹 RL 训练（Agentic-RL 配方笔记方向），RDPO 的分组归一化是必选项。当前无 RL 训练管线，暂记入方法论库
- **P1 — 五维 rubric 蒸馏管线**：正负对比轨迹 → LLM 归纳 → 收敛 5 条冻结。可迁移到 content-judge skill 的评分表自动构造（对比好坏输出蒸馏评分维度，替代手工评分表）
- **P2 — Jetson 端侧**：8B 模型 + 结构先验打 30B 的结论支持端侧部署路线（nexa-local-inference），但搜索智能体场景在 Jetson 上暂无刚需
- **P3 — 量化交易**：not-attempted 重采样（Appendix J）的"推理算力换精度"思想与 Best-of-N 采样同源，quant 领域已有 inference-time-scaling 覆盖

## 九、指南分析

### 9.1 本篇可作为的操作指南

- **构建双角色工作流的规格**：角色定义三要素（职责/信息访问/动作约束）+ 状态转移方程（s_{t+1} = (q, M_{t+1})）可直接照抄为任何"探索-整合"型 Agent 的设计模板
- **Rubric 蒸馏三步法**：20 对正负轨迹 → 独立 prompt 归纳 → 合并冻结 5 条。这是可复用的奖励设计 SOP，适用于任何 LLM-as-judge 场景
- **消融实验设计范式**：训练方法消融（SFT/GRPO/RDPO/w-o RD 四格）+ 角色互换消融（换基线模型）的双消融结构，是 Agent 论文实验章节的标杆模板

### 9.2 复现路径

代码已开源（github.com/Tencent/IterSynth）。复现门槛：Qwen3-8B 全参 SFT + RL 需多卡 GPU（论文未详述卡数，10K 轨迹合成依赖 Qwen3.5-397B-A17B API）。**低成本复现替代**：免训练 prompting 范式（Table 5.1）零训练成本，任何前沿模型可直接套 Planner/Synthesizer prompt 模板获得 +4~5 分。

### 9.3 批判性审视

- BrowseComp 上 30.9 分实际低于 MiroThinker-v1.0-8B 的 31.1，主要增益来自中文基准 BrowseComp-ZH（+15.2）——角色解耦对中文长程搜索的收益是否存在基准特异性，需谨慎
- rubric 由 Claude-4.6-Sonnet 蒸馏、judge 用 Gemini-2.5-flash-lite，奖励模型与策略模型族不同，存在 judge 偏差风险（论文未讨论）
- 59% 上下文耗尽失败率出自 Appendix H 的 ReAct 基线，可能低估了带上下文管理的 ReAct 变体


## 相关笔记

- [PACT精读-LLM强化学习的信用分配唯一表示与评论家对齐](./2026-09-23-PACT精读-LLM强化学习的信用分配唯一表示与评论家对齐.md) — 同为 RL 训练方法精读：IterSynth 的 RDPO 训练 vs PACT 的信用分配
- [RL训练失败模式与RewardHacking自动检测](./2026-09-17-RL训练失败模式与RewardHacking自动检测.md) — RL 训练失败模式与迭代合成的奖励设计风险互补
- [MII协议状态](./2026-09-22-MII协议状态.md) — 智能体协议层进展，与搜索 agent 角色解耦同属 agent 架构议题
