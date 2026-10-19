# 多目标 GRPO：Reward 融合、冲突消解与前沿方法全景（GDPO/ShapE-GRPO/AW-GRPO/RACO/OSPO/ARPO）

> 📅 2026-05-14 | 夜间自学习 | 深度 L3
> 🏷️ #GRPO #GDPO #多目标优化 #Reward融合 #对齐训练 #强化学习 #DeepSeek #NVIDIA #Shapley值

---

## 一、核心发现

### 发现1：GRPO 在多 Reward 场景存在「Reward Collapse」致命缺陷

NVIDIA 2026年1月论文 GDPO（arXiv:2601.05242）揭示了一个被忽视的关键问题：当 GRPO 直接应用于多 reward 场景时，不同 reward 组合经过组内标准化后会坍缩为相同的 advantage 值。

**数学证明**：假设有 3 个 reward（正确性 r₁、格式 r₂、长度 r₃），对于同一个 prompt 采样 G 个响应。GRPO 的做法是：

```
# GRPO 的错误做法：先求和再标准化
total_reward = w₁*r₁ + w₂*r₂ + w₃*r₃
advantage = (total_reward - mean(total_rewards)) / std(total_rewards)
```

问题在于：当不同的 reward 维度呈现不同的分布特性（例如 r₁ 是二值的 0/1，r₂ 是连续的 [0,1] 浮点），求和后再标准化，低方差维度的信号被高方差维度淹没。极端情况下，两个完全不同的 reward 组合（如 [1, 0.5, 0.8] vs [0, 0.9, 0.7]）可能得到相同的 advantage 值，导致模型无法区分哪些行为真正需要改进。

**实证**：在 Tool Calling、Math Reasoning、Code Reasoning 三个任务上，朴素多 reward GRPO 的约束满足率（format/length）比单 reward GRPO 更差，甚至出现训练早期崩溃。

### 发现2：GDPO 的解法——先标准化再聚合（Decoupled Normalization）

GDPO 的核心思想极其简洁：**对每个 reward 维度独立进行组内标准化，然后再加权聚合**。

```
# GDPO 的正确做法：先分维度标准化再聚合
for i in [1,2,3]:
    adv_i = (r_i - mean(r_i_group)) / (std(r_i_group) + ε)
final_advantage = w₁*adv_1 + w₂*adv_2 + w₃*adv_3
```

**关键差异**：
- GRPO：Σ reward → 标准化 → advantage（一个总 reward，一次标准化）
- GDPO：标准化 reward₁ → 标准化 reward₂ → 标准化 reward₃ → 加权求和（每个维度独立标准化）

这样做保留了每个 reward 维度的相对信息，避免了维度间的信号淹没。GDPO 在 NVlabs/GDPO 开源实现中基于 verl、TRL 和 nemo-RL 框架。

**实验结果**（NVIDIA 报告）：
- Tool Calling：格式准确率从 GRPO 的 72% 提升到 GDPO 的 94%
- Math Reasoning：准确率 +3.2%，长度约束满足率 +18%
- Code Reasoning：bug 率下降 40%，格式合规率 +22%
- 训练稳定性：GRPO 在 30% 的多 reward 配置下出现训练崩溃，GDPO 为 0

### 发现3：AW-GRPO（CyberAgent/EMNLP Industry 2025）——自适应权重平衡

AW-GRPO（Auto-Weighted GRPO）解决了另一个问题：**多 reward 的权重如何设定？**

传统做法是手动设定 w₁, w₂, w₃ 权重，但 AW-GRPO 让模型在训练过程中自动调整权重。其核心思想是：根据每个 reward 维度的训练进度（loss 下降率）动态调整权重——训练较慢的维度获得更大权重。

**算法**：
1. 初始化各 reward 维度权重 w_i = 1/K
2. 每个 training step 计算各维度的 advantage
3. 根据各维度的「违反率」（constraint violation rate）动态调整权重
4. 违反率高的维度权重增大，反之减小

**应用**：CyberAgent 在广告文本生成任务（WMT 2024 En-Ja 翻译）上验证，AW-GRPO 在 Readability 和 BLEURT 两个指标上同时取得最优，且约束违反率降低 60%。

### 发现4：ShapE-GRPO 和 OSPO——用博弈论分解 Reward

两篇独立论文将 Shapley 值引入 GRPO 框架，但解决不同层次的问题：

**ShapE-GRPO**（arXiv:2603.29871, MIT/2026）：解决「集合级 reward 如何分配到单个候选」的问题。在推荐、头脑风暴等场景中，LLM 生成一组候选 {y₁, y₂, ..., yₖ}，reward 评估的是整个集合的效用（如多样性+覆盖率），而非单个候选。朴素 GRPO 给所有候选分配同一个集合级 reward，ShapE-GRPO 用 Shapley 值将集合 reward 分解为每个候选的边际贡献。

**OSPO**（Amazon, arXiv:2601.08403）：解决「序列级 reward 如何分配到 token/片段」的问题。标准 GRPO 给整个响应分配一个标量 advantage，OSPO 用 Owen-Shapley 分解将 advantage 分配到响应的各个片段（segment），实现细粒度的信用分配（credit assignment）。

### 发现5：RACO——免 Reward Model 的多目标对齐

RACO（Reward-free Alignment for Conflicting Objectives, arXiv:2602.02495）提出了一个更激进的方案：完全不需要 reward model。

**核心思想**：用 Conflict-Averse Gradient Descent（CAGrad）直接在偏好数据上优化多个目标，避免学习显式的 reward model。当 helpfulness 和 safety 的梯度方向冲突时，CAGrad 找到一个「最不坏」的更新方向。

**改进 CAGrad-Clip**：原始 CAGrad 在高度冲突的偏好批次上会过度保护低优先级目标，CAGrad-Clip 通过权重预算约束（π_i ≤ w_i）防止过度修正，同时保留 Pareto 收敛保证。

---

## 二、技术原理解析

### 2.1 多 Reward 融合的三大流派

| 流派 | 代表方法 | 核心思路 | 优势 | 局限 |
|------|----------|----------|------|------|
| **标准化后聚合** | GDPO | 每个 reward 独立标准化再加权 | 保留维度信息 | 需要预设权重 |
| **自适应权重** | AW-GRPO | 动态调整各 reward 权重 | 免手动调权 | 训练不稳定风险 |
| **博弈论分解** | ShapE-GRPO/OSPO | 用 Shapley 值分配 credit | 理论最优 | 计算开销 O(2^n) |
| **梯度冲突消解** | RACO | CAGrad 直接在偏好数据优化 | 无需 reward model | 偏好数据需求大 |

### 2.2 GDPO 的数学推导

**Step 1: GRPO 的 Reward Collapse 问题形式化**

设有 K 个 reward 函数 {r₁, r₂, ..., r_K}，对 prompt q 采样 G 个响应 {o₁, ..., o_G}。GRPO 的 advantage 为：

```
A_i = (Σ_k w_k * r_k(o_i, q) - μ) / σ
```

其中 μ = (1/G)Σ_i Σ_k w_k * r_k(o_i, q)，σ = std(Σ_k w_k * r_k(o_i, q))

**Collapse 证明**：考虑两个响应 o_a 和 o_b，其中 r₁(o_a) > r₁(o_b) 但 r₂(o_a) < r₂(o_b)，且 Σ_k w_k * r_k(o_a) = Σ_k w_k * r_k(o_b)。则 A_a = A_b，模型无法区分——即使 o_a 在维度1上更好。

**Step 2: GDPO 的解法**

```
GDPO advantage:
A_i^GDPO = Σ_k w_k * (r_k(o_i, q) - μ_k) / (σ_k + ε)
```

其中 μ_k = (1/G)Σ_i r_k(o_i, q)，σ_k = std({r_k(o_i, q)}_i=1..G)

每个维度独立标准化后加权，不会出现维度间的信号淹没。

### 2.3 ShapE-GRPO 的 Shapley 分解

对于集合级 reward U(S)，其中 S = {y₁, ..., yₖ}，候选 y_j 的 Shapley 值为：

```
φ_j = (1/K!) Σ_{π∈Perm(K)} [U(S_{π,≤j}) - U(S_{π,<j})]
```

其中 S_{π,≤j} = {y_{π(1)}, ..., y_{π(j)}} 是排列 π 中前 j 个元素组成的子集。

**近似计算**：精确 Shapley 值需要 O(K!) 次评估，实践中用蒙特卡洛采样 M 个随机排列近似，复杂度降为 O(M·K·C_eval)。

**与 GRPO 的整合**：将 Shapley 值 φ_j 作为候选 y_j 的 advantage 信号替代原来的统一 set-level reward。

### 2.4 ARPO——Agent 专用的多轮 RL

ARPO（Agentic Reinforced Policy Optimization, arXiv:2507.19849）将 GRPO 扩展到多轮工具调用场景：

**核心创新**：
1. **Entropy-based Adaptive Rollout**：在高熵（不确定性大）的工具调用轮次自动分支采样，低熵轮次直接通过
2. **Advantage Attribution**：将最终 reward 归因到每一步工具调用，而非统一分配到整个轨迹
3. **Step-level GRPO**：每步独立计算组内 advantage，类似 GDPO 的思想但作用在时间维度

**效果**：用 50% 的 tool-use 数据即超过轨迹级 RL 的表现，30B 参数模型在工具调用任务上超过 10x 大小的前沿模型。

---

## 三、知识关联

- [[2026-05-04-LLM对齐训练范式RLHF-DPO-GRPO-DAPO.md]] → 本篇直接扩展了 GRPO 的数学基础，从单 reward 推广到多 reward。原有 GRPO 公式中的 A_i 是单维度 Z-score，GDPO 将其扩展为多维独立 Z-score 的加权和
- [[2026-05-09-LLM知识蒸馏技术全景.md]] → RLAD（RL 感知蒸馏）与多 reward GRPO 有交叉：蒸馏时保留 RL 能力本质上是多 reward 平衡问题（模仿教师 + 保留 RL 信号）
- [[2026-05-10-蒸馏量化联合策略-QAD-LBLLM-CapacityGap.md]] → GoR 的 QAT+KD 损失自适应平衡与 AW-GRPO 的动态权重调整思想一致
- [[2026-05-05-大模型数据工程-合成数据-数据质量-课程学习.md]] → 多 reward 设定下的课程学习：先训练主 reward（如正确性），再逐步加入约束 reward（如格式、长度），与数据课程学习范式相通
- [[2026-05-06-MoE混合专家模型-路由策略-负载均衡-训练稳定性.md]] → Shapley 值在 MoE 专家重要性评估（Shapley-MoE）和多 reward 分配（ShapE-GRPO）中的应用一脉相承
- [[2026-05-13-MoE投机解码-稀疏激活与推理加速深度解析.md]] → ARPO 的 step-level advantage 与投机解码的 token-level 验证有类似的多粒度信号分解思想
- obs_notes: [[computer SCI]] → 已有 RL 基础概念参考

---

## 四、Actionable Insights

### 4.1 对 Hermes Agent 的直接价值

1. **Hermes Skill 训练可用 GDPO**：当 Skill 涉及多个质量维度（正确性 + 格式 + 风格）时，GDPO 的分维度标准化可避免训练信号坍缩。TRL 库已支持 GDPO。

2. **Self-Evolution 用 RACO 思路**：Hermes 的 evolver 需要同时优化多个质量指标（错误率、响应时间、用户满意度），RACO 的 CAGrad 提供了免 reward model 的多目标优化方案。

3. **Agent RL 用 ARPO**：Hermes 的工具调用训练本质上就是多轮决策，ARPO 的 entropy-based adaptive rollout 和 advantage attribution 直接适用。

### 4.2 技术落地路径

1. **短期**（1-2周）：在 TRL/vLLM 中实验 GDPO 替代 GRPO 进行多 reward 微调
2. **中期**（1月）：探索 AW-GRPO 自适应权重用于 Hermes Skill 质量优化
3. **长期**：ShapE-GRPO + OSPO 的细粒度 credit assignment 用于 Agent 工具调用训练

### 4.3 开源资源

- NVIDIA GDPO 实现：github.com/NVlabs/GDPO（基于 verl + TRL + nemo-RL）
- CyberAgent AW-GRPO：github.com/CyberAgentAILab/AW-GRPO
- Amazon OSPO：github.com/amazon-science/owen-shapley-policy-optimization
- ARPO：dongguanting/ARPO-RL-Reasoning-10K

---

## 五、方法对比矩阵

| 方法 | 发表 | 解决的问题 | 核心 | 多 reward | 计算开销 | 收敛稳定性 |
|------|------|-----------|------|----------|---------|-----------|
| GRPO | 2024 | 去除 Critic | 组内 Z-score | ❌ 坍缩 | 低 | 单 reward 稳定 |
| DAPO | 2024 | GRPO 效率改进 | 非对称裁剪+动态采样 | ❌ 同 GRPO | 低 | 较好 |
| GDPO | 2026.01 | 多 Reward 坍缩 | 分维度独立标准化 | ✅ | 低 | 最好 |
| AW-GRPO | 2025.11 | 权重设定 | 自适应权重调整 | ✅ | 中 | 中 |
| ShapE-GRPO | 2026.03 | 集合级 Reward 分配 | Shapley 值分解 | ✅ | 高 | 好 |
| OSPO | 2026.01 | Token 级 Credit | Owen-Shapley 分解 | ✅ | 高 | 好 |
| RACO | 2026.02 | 免 Reward Model | CAGrad 梯度冲突消解 | ✅ | 低 | 好 |
| ARPO | 2025.07 | Agent 多轮训练 | Entropy 采样+Advantage 归因 | ✅ | 中 | 好 |

---

## 六、待深入的问题清单

1. **GDPO 的权重敏感性**：虽然解决了坍缩问题，但 w₁, w₂, w₃ 权重仍需手动设定。权重变化 10% 对最终效果的影响有多大？是否可用 AW-GRPO 的自适应权重 + GDPO 的分维度标准化？
2. **ShapE-GRPO 的计算效率**：蒙特卡洛 Shapley 的采样数 M 如何选择？M 太小近似误差大，M 太大训练慢。是否存在自适应采样策略？
3. **RACO + GDPO 的联合**：CAGrad 的梯度冲突消解 + GDPO 的分维度标准化是否互补？前者作用于梯度空间，后者作用于 advantage 空间，理论上可叠加。
4. **多 Reward 在 MoE 模型上的特殊挑战**：MoE 的专家路由不均可能导致不同 expert 对不同 reward 维度的敏感度不同，是否需要 expert-aware 的 reward 分配？
5. **OSPO 与投机解码的关联**：Owen-Shapley 的 token 级 credit assignment 是否能用于改进投机解码的 draft model 训练？
6. **ARPO 在 Hermes Agent 上的实证**：entropy-based adaptive rollout 与 Hermes 的多工具调用场景匹配度如何？是否需要针对 Agent 场景调整 advantage attribution 策略？

---

## 七、参考论文

1. Liu et al. "GDPO: Group reward-Decoupled Normalization Policy Optimization for Multi-reward RL Optimization" (NVIDIA, arXiv:2601.05242, Jan 2026)
2. Ai et al. "ShapE-GRPO: Shapley-Enhanced Reward Allocation for Multi-Candidate LLM Training" (MIT, arXiv:2603.29871, Mar 2026)
3. Ichihara & Jinnai. "Auto-Weighted Group Relative Preference Optimization for Multi-Objective Text Generation Tasks" (CyberAgent, EMNLP Industry 2025)
4. Li et al. "Optimizing Safe and Aligned Language Generation: A Multi-Objective GRPO Approach" (arXiv:2503.21819, Mar 2025)
5. Chen et al. "Reward-free Alignment for Conflicting Objectives" (arXiv:2602.02495, Feb 2026)
6. Sarkar et al. "Owen-Shapley Policy Optimization (OSPO): A Principled RL Algorithm for Generative Search LLMs" (Amazon, arXiv:2601.08403, Jan 2026)
7. Dong et al. "Agentic Reinforced Policy Optimization" (arXiv:2507.19849, 2025)
8. "Multi-Reward GRPO Fine-Tuning for De-biasing Large Language Models" (arXiv:2511.06023, Nov 2024)

## 相关笔记
- [MoE投机解码-稀疏激活与推理加速深度解析](2026-05-13-MoE投机解码-稀疏激活与推理加速深度解析.md)
- [从零训练GPT完整指南](2026-05-13-从零训练GPT完整指南.md)
- [序列并行与上下文并行-长上下文训练的第四维并行](2026-05-15-序列并行与上下文并行-长上下文训练的第四维并行.md)


## 相关笔记
- [2026-05-12-网络安全-security-automation](2026-05-12-网络安全-security-automation.md)
- [2026-05-12-数据治理-data-catalog](2026-05-12-数据治理-data-catalog.md)
- [20260513-llm-wiki-obsidian-gbrain-知识自组织与自进化](20260513-llm-wiki-obsidian-gbrain-知识自组织与自进化.md)
- [llm-wiki-gbrain-agent-evolution_33aa818c](llm-wiki-gbrain-agent-evolution_33aa818c.md)
- [2026-05-15-上下文才是Agent的命门-QClaw上下文竞争论](2026-05-15-上下文才是Agent的命门-QClaw上下文竞争论.md)
