# Ecdysis：高效Runtime Harness自进化训练框架

> **来源**：arXiv
> **原文链接**：https://arxiv.org/abs/2609.11677
> **作者**：Yue Ruiqing, Cui Yu, Sun Zhuoyu, Pan Sicheng, Xue Xianhong, Li Tingyu, Li Ting, Zhu Wenzhuo, Chen Yi, Liu Yifei, Huang Baohan, Cui Zhe, Zhang Haibin, Zuo Cong
> **记录日期**：2026-09-12

**标签**：#harness自进化 #失败归因 #跨任务聚合 #LLMAgent #模型特异性vs系统性修复

---

## 一、内容整理

### 1.1 核心问题：Harness 进化的失败归因困境

LLM Agent 的 runtime harness（运行时操控层）对性能至关重要——去掉所有 harness 层后六种 Qwen3 模型组合平均准确率仅 29.72%，人工配置的固定 harness 可达 50.28%，而用编码 Agent 逐失败串行修改 harness 只有 43.33%，仍低于人工配置。

现有 harness 自进化方法的核心瓶颈不在收集失败信号，而在**可靠地解释失败**。一个观测到的失败可能来自两种根因：

- **模型特异性缺陷（model-specific deficiency）**：当前 LLM 自身能力的不足
- **系统性 harness 缺陷（systematic harness deficiency）**：harness 交互机制本身的设计问题

直接对单个失败做修改，会导致不必要的模型特异性适配——harness 被改去"绕过"模型弱点而非修复通用机制缺陷，最终过拟合训练任务和当前模型，泛化性下降。

### 1.2 形式化分解：ΔH = t·ΔH_model + (1-t)·ΔH_harness

论文提出一个简洁的概念分解。将一轮进化中编码 Agent 产生的总 harness 更新 ΔH 分解为：

- ΔH_model：模型特异性适配分量
- ΔH_harness：系统性 harness 修复分量
- t ∈ [0,1]：模型适配决策占比

公式：**ΔH = t·ΔH_model + (1-t)·ΔH_harness, t ∈ [0,1]**

t 越大，当前观测失败可能被快速"解决"，但 harness 会过拟合当前模型和训练任务。核心假设是：**跨任务实例反复出现的失败模式**比孤立失败提供更强的系统性缺陷证据，可以将适配从不必要的模型特异性偏移中拉开。

### 1.3 Ecdysis 框架：三层架构

**第一层 — 批量跨实例失败聚合（Cross-Instance Aggregation）**：
不再将每个失败作为独立修改信号，而是将一轮进化中多个任务实例的失败证据联合分析，识别跨任务反复出现的失败模式，优先处理这些提供更强系统性缺陷证据的模式。

**第二层 — 失败驱动协同精炼（Failure-Driven Collaborative Refinement, FDCR）**：
三个角色迭代分析聚合后的失败证据：
- **Analyst**：诊断失败原因
- **Critic**：审查诊断的可靠性
- **Engineer**：提出具体的 harness 修改规格
- **Moderator**：综合三方分析，产出结构化修改规格（modification specification）

经 K 轮迭代精炼后，Moderator 输出最终修改计划，由编码 Agent 实现。多角色互补视角减少失败解释的歧义。

**第三层 — 训练数据感知策展（Failure-Aware Data Curation）**：
训练任务不是等价的——有些暴露新的执行路径或未覆盖的 harness 缺陷，有些只产生已知失败模式的冗余表现。论文提出优先选择能暴露新颖交互结构和失败机制的任务，减少冗余执行成本。实验证明仅用 1/4 训练数据（5 个失败样本）即可达到与全量训练相当的性能。

### 1.4 算法流程

```
输入：固定任务模型 θ, 运行环境 E, 训练任务集 D_train, 初始 harness H_base
      失败阈值 λ, 进化轮数 R, 精炼轮数 K
输出：冻结的最终 harness H_F

1. H_0 ← H_base
2. for i = 1 to R:
3.   T_i ← Collect(θ, H_{i-1}, E, D_train)          # 收集执行轨迹
4.   f_λ(τ) ← I[S(τ) < λ]                            # 标记失败轨迹
5.   B_i ← Aggregate({τ ∈ T_i : f_λ(τ)=1})           # 结构化失败证据
6.   if B_i = ∅: H_i ← H_{i-1}; continue
7.   G_i ← Group(B_i)                                 # 失败模式分组
8.   A ← {Analyst, Critic, Engineer}                  # 三角色
9.   M_i ← ∅                                          # 共享角色转录
10.  for k = 1 to K:
11.    foreach A ∈ A:
12.      m_i^{k,A} ← A(G_i, M_i)                       # 角色分析
13.      M_i ← M_i ∘ m_i^{k,A}                         # 追加到转录
14.  q_i ← Moderator(G_i, M_i)                        # 结构化修改规格
15.  H_i^c ← Edit(H_{i-1}, q_i)                       # 编码 Agent 实现
16.  if J_train(H_i^c) > J_train(H_{i-1}):            # 严格改进才接受
17.    H_i ← H_i^c
18.  else: H_i ← H_{i-1}
19. H_F ← H_R
20. return H_F
```

### 1.5 关键实验结果

**总体性能（τ²-Bench 两数据集平均，5 模型）**：
- Direct（无 harness）：38.17% 准确率
- Human-Aug.（人工优化）：51.67%
- Self-Evolution (SE)（逐失败串行修改）：46.67%
- Ecdysis (w/o FDCR)：54.67%
- Ecdysis (w/ FDCR)：59.33%

Ecdysis (w/ FDCR) 相对 SE 提升 27.1%，相对 Human-Aug. 提升 14.8%。Pass³（三次独立试验全部通过率）提升 55.2%。

**训练效率**：
- τ²-Retail：Ecdysis (w/o FDCR) 1,292.4s vs SE，加速 1.42×
- τ²-Airline：Ecdysis (w/o FDCR) 2,510.8s，加速 3.23×；Ecdysis (w/ FDCR) 4,403.0s，加速 1.84×

**API 成本**：
- SE：$8.484 (Retail) / $6.382 (Airline)
- Ecdysis (w/o FDCR)：$2.485 / $2.136（降低 70.71% / 66.53%）
- Ecdysis (w/ FDCR)：$5.763 / $2.609（降低 32.07% / 59.12%）

**消融分析**：
- 失败聚合单独贡献：准确率 +8.00%（SE→Ecdysis w/o FDCR）
- FDCR 额外贡献：准确率 +4.67%（Ecdysis w/o FDCR→w/ FDCR）
- 结论：失败聚合提供主要效率增益，FDCR 是精度导向的精炼模块

**模型特异性适配量化（t 值）**：
- SE 的 t = 60.0%（60% 修改决策是模型适配）
- Ecdysis 的 t = 45.5%（降低 14.5 个百分点）
- 证明跨任务失败分析有效减少了不必要的模型特异性适配

**跨模型泛化**：
- Qwen3-32B 在 τ²-Airline 上从 SE 的 51.67% 提升到 Ecdysis 的 68.33%
- 该模型未参与训练，harness 是用 Qwen3-8B 训练的
- 证明 Ecdysis 训练的 harness 可零样本迁移到其他 LLM

**1/4 训练数据实验**：
- 仅用 5 个训练失败样本（原 20 个的 1/4）
- 性能与全量训练相当，训练成本大幅降低
- 随机选 5 个样本则性能下降
- 证明失败感知的任务选择优于随机采样

## 二、查询拓展

### 2.1 Runtime Harness 与 Inference-Time Compute Scaling

Runtime harness 是介于 LLM 参数和任务之间的一层"软基础设施"——包括任务规划、工具交互、上下文管理、错误恢复等机制。它与 inference-time compute scaling（推理时计算扩展）的关系是：harness 决定了额外的推理计算如何被组织和使用。Ecdysis 的贡献在于展示了 harness 本身也可以作为优化目标，且优化方法的质量（失败归因可靠性）比优化次数更重要。

### 2.2 Model-Specific Accommodation 与 Overfitting

模型特异性适配是 harness 进化中的过拟合现象——harness 被改成"绕过"当前模型的某个弱点，而非修复通用交互机制。例如，某模型在特定场景下会错误调用工具，SE 方法可能直接在 harness 中禁止该工具调用（全局禁止），这虽然解决了当前训练任务的问题，但缩小了 harness 的有效动作空间，损害了跨模型泛化。Ecdysis 通过跨任务聚合识别系统性缺陷，只在反复出现的失败模式上做修改，避免了这种过拟合。

### 2.3 FDCR 多角色协同与 LLM-as-Judge

FDCR 的三角色（Analyst/Critic/Engineer）+ Moderator 架构与 LLM-as-Judge 的多评审模式异曲同工。区别在于 FDCR 不是评判输出质量，而是诊断失败原因——Analyst 提出假设，Critic 审查假设可靠性，Engineer 转化为具体修改规格。共享转录 M 确保角色间信息传递，避免重复分析。这与 Hermes Agent 的 Dev/Critic 角色分离设计模式一致。

## 三、归纳总结

### 3.1 Harness 进化方法对比框架

- **Direct**：无 harness，裸模型直接执行。准确率最低（38.17%），但 token 消耗也最低（8.7M）
- **Human-Aug.**：人工固定优化 harness。强基线（51.67%），但不可自动进化
- **Self-Evolution (SE)**：逐失败串行修改。准确率反而低于人工基线（46.67%），因过拟合模型特异性。每次失败独立调用编码 Agent，成本高且调用完成率低（67%）
- **Ecdysis (w/o FDCR)**：跨实例聚合 + 单次修改。准确率 54.67%，成本降低 70%。编码 Agent 调用完成率 100%
- **Ecdysis (w/ FDCR)**：聚合 + 多角色精炼。准确率最高 59.33%，但训练时间略增。精度-效率可调

### 3.2 核心洞察：失败不是等价的

论文最重要的概念贡献是"失败不是等价的可操作信号"：

```
观测失败 → 根因歧义 → 直接修改 = 赌博
         ├─ 模型特异性 → 适配 = 过拟合风险↑
         └─ 系统性缺陷 → 修复 = 泛化收益↑

跨任务反复出现 → 系统性证据更强 → 优先修复
孤立出现 → 可能是模型特异性 → 谨慎或跳过
```

这个二分法与 Hermes Agent 的错误案例库（error-case-library）设计理念一致——区分"环境/模型偶发错误"和"系统性设计缺陷"是正确归因的前提。

## 四、趋势判断

### 趋势1：Harness 自进化从"盲目搜索"转向"诊断驱动"
SE 方法本质是"试错法"——每遇到一个失败就改一次，不做根因分析。Ecdysis 代表了从"盲目搜索"到"诊断驱动"的范式转变。未来 harness 进化将越来越依赖可靠的失败归因机制，而非单纯的迭代次数。依据：t 值从 60% 降到 45.5% 直接关联泛化性提升。

### 趋势2：训练数据质量 > 数量，适用于 harness 进化领域
论文证明 1/4 训练数据可达全量性能，但随机选 1/4 不行。这与 on-policy distillation 的发现一致——少量精心选择的困难样本可替代大量数据。harness 进化的"困难样本"是能暴露新颖执行路径和失败机制的任务，而非简单数量积累。

### 趋势3：多角色协同从"评审"扩展到"诊断"
FDCR 将 LLM-as-Judge 从输出评审扩展到失败诊断。Analyst/Critic/Engineer 的分工比单一 Judge 更适合需要多视角的根因分析任务。这种模式可推广到 Agent 系统的任何需要归因的环节——不仅是 harness 进化，也包括在线错误恢复和事后分析。

## 五、关联分析

### 5.1 与 Hermes Agent harness-architecture skill 的关联

Hermes 已有 `harness-architecture` skill（六层 Harness 架构设计模式），定义了复杂 Agent 任务的系统化框架。Ecdysis 证明了 harness 层本身可以自进化，且进化方法的质量比层数更重要。关联点：
- 六层架构中的"诊断层"可以引入 Ecdysis 的跨任务失败聚合机制
- Hermes 的 evolver skill 已有错误模式分析→规则沉淀逻辑，Ecdysis 的 t 值量化（模型适配 vs 系统修复）可作为 evolver 的归因过滤器

### 5.2 与 SoL-Pi 自优化 Harness 的关联

2026-09-11 精读的 SoL-Pi（英伟达开源自我优化 Harness）也关注 harness 自进化，但 SoL-Pi 侧重"机制设计"（四大机制 + RSI 流水线），Ecdysis 侧重"进化方法的质量"（失败归因 + 跨任务聚合）。两者互补：SoL-Pi 提供架构，Ecdysis 提供训练方法学。

### 5.3 与 Beyond the Leaderboard 失败模式分类的关联

2026-07-09 精读的 Beyond the Leaderboard (2607.05775) 提出了 LLM Agent 六大失败模式分类法和三定律。Ecdysis 的"模型特异性 vs 系统性缺陷"二分法可视为该分类法在 harness 进化场景的特化应用——判断一个失败属于哪类，决定了应该修模型、修 harness、还是两者都不修。

### 5.4 与 error-case-library 的关联

Hermes 的 `error-case-library` skill 记录每次排查的根因、症状、解法。Ecdysis 的跨任务失败聚合本质上是一种自动化的 error-case 分析——不再依赖人工逐条判断根因，而是通过统计跨任务复发频率自动推断系统性。未来可在 error-case-library 中引入"复发计数"字段，达到阈值自动标记为系统性缺陷。

## 六、金句摘录

> 「An observed failure may arise from the current model's behavior or from a systematic deficiency in the harness. This distinction is critical because harness evolution can either perform model-specific accommodation, adapting to idiosyncrasies of the current model, or harness-level repair, addressing systematic deficiencies in the interaction mechanism.」— 失败归因的二分法定义

> 「Cross-task recurrence is used as an inductive bias rather than as proof of causal attribution.」— 诚实地承认跨任务复发是归纳偏置而非因果证明

> 「Effective harness training should prioritize informative tasks over data quantity.」— 数据质量优先于数量的原则

## 七、行动启示

- **失败归因过滤器**：在 evolver/error-case-library 中引入跨任务复发计数，区分模型偶发 vs 系统性缺陷
- **多角色诊断**：将 Analyst/Critic/Engineer 模式引入 Hermes Agent 的错误恢复流程
- **训练数据策展**：Hermes skill 压测（skill-stress-test）应优先选择能暴露新颖失败路径的任务
- **t 值监控**：在 harness 自进化过程中量化模型适配占比，作为泛化性预警指标

## 八、拓展应用推荐

### 8.1 Hermes Skill 进化的 t 值监控

当前 Hermes 的 skill-review/evolver 机制会审查和合并 skill，但缺乏"这个修改是模型特异性适配还是通用改进"的区分。引入 t 值监控：
- 对每个 skill 修改标注"模型适配"或"通用修复"
- 跨 session 统计修改的复发模式
- t > 50% 的 skill 修改应标记为"过拟合风险"

### 8.2 FDCR 模式用于 cron job 失败诊断

Hermes cron job 失败时，当前只有 watchdog 做简单重试。可引入 FDCR 模式：
- Analyst：分析失败日志，提出根因假设
- Critic：审查假设（是否环境偶发 vs 系统设计问题）
- Engineer：提出具体修复方案
- Moderator：综合判断，决定执行修复还是上报

## 九、指南分析

### 9.1 实施路线图：从论文到 Hermes

**P0（立即可做）— error-case-library 引入复发计数**：
- 在 error-case-library 的每个案例中新增 `recurrence_count` 字段
- 跨 session 统计同一根因出现次数
- ≥3 次自动标记为"系统性缺陷"，优先修复

**P1（短期）— evolver 引入 t 值标注**：
- evolver 每次分析错误模式时，标注修改建议为"模型适配"或"通用修复"
- 产出 t 值统计报告，高 t 值提醒过拟合风险

**P2（中期）— FDCR 模式用于复杂错误诊断**：
- 在 watchdog 或手动排查复杂错误时，用 Analyst/Critic/Engineer 三角色替代单一分析
- 共享转录确保角色间信息传递

**P3（长期）— harness 自进化管线**：
- 参考 Ecdysis 的批量聚合 + 严格改进接受协议
- 在 Hermes skill 进化中引入"跨任务失败聚合"而非"逐失败修改"
- 用 1/4 精选训练数据替代全量，降低进化成本
