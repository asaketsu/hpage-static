# 极简参数 PEFT + GRPO 推理训练前沿：从 TinyLoRA(13参数) 到 VeFA 实证全景（2026-06-02）

> 夜学深度笔记 | 深入分析"RL 训练到底需要多少参数"这一核心问题。覆盖 TinyLoRA（Meta FAIR, arXiv 2602.04118, 13参数91%GSM8K）、VeFA 特征空间适配、Evolution Strategies（ES, arXiv 2509.24372）、Hybrid-LoRA（arXiv 2605.18822）的实证数据，以及 GTPO/CEPO/TEPO/DGPO 四种最新的 token 级 credit assignment GRPO 变体。建立"极简参数 RL"的方法谱系与 VeFA 定位分析。
> 日期：2026-06-02

---

## 一、核心发现

### 1. TinyLoRA：13 个参数足以推理（Meta FAIR, arXiv 2602.04118, Feb 2026）

**这是 2026 年以来对"RL 训练参数需求"最有颠覆性的发现**：

核心机制：
- TinyLoRA 基于 LoRA-XS，将可训练低秩矩阵 R 替换为固定随机投影矩阵的加权和：R = Σᵢ vᵢ Pᵢ
- v ∈ R^u 是极小的可训练向量（u 可低至 1），Pᵢ 是固定的随机矩阵
- 关键创新：**全权重绑定（full weight tying）** — 所有模块、所有层共享同一组 v
- 整个模型的更新量压缩到 u 个参数（u=13 时仅 26 bytes）

关键实验数据（Qwen2.5-7B-Instruct, GRPO）：
- **13 个参数 → GSM8K 91%**（基线 76%，+15 个百分点）
- 在 AIME/AMC/MATH500 上恢复 90% 的性能提升，仅用 **1000x 更少参数**
- **RL 远比 SFT 高效**：相同参数预算下，SFT 需要 100-1000x 更多参数才能匹配 RL
- **规模趋势**：模型越大，达到 FullFT 95% 性能所需的参数越少 → 万亿模型可能只需几个参数

**与 VeFA 的关系**：TinyLoRA 的 v 向量在概念上与 VeFA 的 diag(v) 缩放向量极其相似——都是极小参数集通过固定结构扩展到完整权重更新。但 TinyLoRA 通过随机投影 Pᵢ 引入新的方向信息（超越 W₀ 列空间），而 VeFA 严格限制在 W₀ 的列空间内。这直接回答了我们之前的问题：**RL 确实只需要极少的参数维度，但方向多样性（而非仅幅度调整）仍然重要**。

### 2. Evolution Strategies：无梯度 RL 超越 GRPO（arXiv 2509.24372, Updated 2026）

**ES 在 LLM 后训练中的首次成功规模化**，提出了一种全新的 backpropagation-free 范式：

核心机制：
- ES 直接对所有模型参数添加高斯噪声，保留性能更好的版本
- 不需要策略梯度、不需要价值函数、不需要 KL 惩罚
- 完全免反传（backpropagation-free）

关键发现：
- **Countdown 推理任务**：ES 在所有测试模型（Qwen/Llama 3B）上大幅超越 GRPO/PPO
- **15x 更低的结果方差**：跨 run 稳定性远超 GRPO
- **同一超参数跨模型适用**：GRPO 需要为每个模型单独调参，ES 不需要
- **更好的 reward-KL tradeoff**：简洁响应任务上 ES 无需 KL 惩罚系数即超越 GRPO
- **对长 horizon reward 更鲁棒**
- **更不容易 reward hacking**

**与 VeFA 的关系**：ES 的成功暗示 RL 训练中参数空间的搜索可能比精确的梯度方向更重要。VeFA 限制了搜索空间（仅幅度调整），而 ES 在全参数空间搜索但用极其简单的信号（标量 reward + 噪声）。两者都指向同一结论：**RL 需要的信息量远比我们想象的少**。

**局限性**：ES 目前在符号推理等结构化任务上验证，多目标对齐等复杂场景的适用性尚未验证。

### 3. GRPO Token 级 Credit Assignment 爆发（2026 H1 四大新方法）

标准 GRPO 的关键缺陷：同一序列中所有 token 收到相同的 reward — 推理关键步骤和语法填充词获得相同信号。2026 上半年至少四种方法独立解决这个问题：

**GTPO/GRPO-S（ICML 2026, arXiv 2508.04349）**：
- Dynamic Entropy Weighting — 用策略熵 H_{i,t} 作为"认知努力"的代理
- 高熵 token = 推理关键节点 → 获得更大 reward 权重
- 在 AIME 和 MATH500 上显著超越 DAPO 基线
- Token 级（GTPO）和序列级（GRPO-S）两个变体

**CEPO（arXiv 2605.19436）**：
- Contrastive Evidence Policy Optimization
- 对比正/负答案条件下的 token 概率比：P_T+(y_t) / P_T-(y_t)
- 正确答案支持 + 错误答案反对 → 真正的推理步骤
- 仅利用训练 batch 中已有的拒绝 rollout，无额外计算

**TEPO（arXiv 2604.12736）**：
- Token-Level Policy Optimization — 通过序列级似然将组级 reward 传播到 token 级
- 引入 token 级 KL 散度掩码约束，仅对正 advantage + 熵递减的 token 施加约束
- 解决 GRPO 的熵坍塌问题

**DGPO（arXiv 2605.03327）**：
- Distribution Guided Policy Optimization
- 用有界 Hellinger Distance 替代无界 KL 散度
- 熵门控机制重分配序列级 advantage 到 token 级
- AIME2024/2025 SOTA，计算效率与 GRPO 相当

### 4. Hybrid-LoRA 后训练实证（arXiv 2605.18822, May 2026）— 补充数据

之前笔记已覆盖核心内容，补充新发现：
- **Hybrid-Score 的梯度加权敏感度** s = (1/r) ||e ⊙ g||₁ 与 VeFA 的 diag(v) · W₀ 存在数学对偶
- Hybrid-LoRA 在 Qwen-2.5 全系列（1.5B/3B/7B）上验证，平均优于最佳基线 4.36%
- **关键数据更新**：10% FFT 模块 = 93% 参数减少，性能接近 FullFT

### 5. Hard Samples 在 GRPO 小模型上的收益递减（arXiv 2604.06298）

- GRPO + LoRA 在 SLM（0.5B-3B）上训练数学推理
- 在 GSM8K 和 MATH 上测试困难样本缩放
- **发现**：超过一定难度阈值后，增加训练数据难度对 SLM 收益递减
- 对我们的启示：小模型 GRPO 训练中数据难度需要匹配模型容量，而非一味追求困难

---

## 二、技术原理解析

### 2.1 TinyLoRA 的极简参数化数学

**LoRA → LoRA-XS → TinyLoRA 的演化路径**：

LoRA: ΔW = BA（r×d 参数）
LoRA-XS: ΔW = BRS（利用 W₀ 的 SVD 分解 U Σ V^T，R 在奇异子空间中学习）
TinyLoRA: R = Σᵢ vᵢ Pᵢ（随机投影加权和，仅 u 个参数）

**全权重绑定的关键假设**：
- 不同层/模块的最优更新方向虽不同，但可以通过共享的 v 和不同的 Pᵢ 自动适配
- 本质是一种元学习：v 学习"全局信号强度"，Pᵢ 负责"局部方向翻译"
- 这与 Schulman 的 O(1) bits/episode 信息论论证完美吻合：13 个 bf16 参数 = 208 bits，远超每轮 RL 所需

**为什么 RL 比 SFT 更适合极简参数**：
1. RL 的信号是标量 advantage → 信息量极低，13 参数足够承载
2. SFT 的信号是逐 token 梯度 → 信息量大，需要更高秩
3. RL 本质是"解锁"已有能力，而非"注入"新知识 → 幅度调整 > 方向学习

### 2.2 VeFA vs TinyLoRA 的精确对比

| 维度 | VeFA | TinyLoRA |
|------|------|----------|
| 参数化 | W_eff = diag(v) · W₀ | ΔW = B(Σᵢ vᵢ Pᵢ)S |
| 可训练参数 | d（hidden_size 量级） | u（可低至 1） |
| 方向自由度 | 0（严格限制在 W₀ 列空间） | u 个随机投影方向（可超越 W₀） |
| 权重绑定 | 每层独立 v | 全模型共享 v |
| 信息容量 | d 个自由度 | u × 随机投影数量 |
| 分布鲁棒性 | 数学保证（列空间不变） | 依赖随机投影质量 |
| RL 理论兼容性 | 完美（O(1) bits << d） | 超越理论需求（u=13 >> 1 bit/episode） |

**关键结论**：TinyLoRA 的 u=13 >> VeFA 的 d=4096 是因为 TinyLoRA 需要学习"选择哪些随机投影方向"（离散选择），而 VeFA 的 d 个参数都是连续缩放（更信息密集）。但从 RL 信号匹配角度，VeFA 的 d 个参数完全足够。

**预测**：VeFA (d=4096 自由度) 在 RL 场景中应该不逊于 TinyLoRA (u=13)，因为 RL 的标量 advantage 可以通过 VeFA 的连续缩放精确传播。VeFA 的优势在于分布鲁棒性，TinyLoRA 的优势在于极致参数效率。

### 2.3 ES 的"零信息理论"解释

ES 的成功可以用信息论重新理解：
- ES 的每次参数扰动 = 对整个参数空间的一次随机探测
- reward 信号 = 标量，O(1) bits
- 但 ES 利用了整个参数空间的**结构**：预训练已经将"好方向"编码在权重中
- 高斯噪声探索的是权重的邻域，而预训练已经确保邻域内有大量有用方向
- 这与 VeFA 的"幅度调整"和 TinyLoRA 的"随机投影"殊途同归：**预训练模型已经包含了足够的先验，RL 只需极小扰动**

### 2.4 Token 级 Credit Assignment 的统一视角

四种方法可以统一为对 GRPO advantage 的 token 级调制：

GRPO 原始: A_{k,t} = r_k（所有 token 相同）
GTPO: A_{k,t} = r_k × (H_{i,t} / ΣH)（熵加权）
CEPO: A_{k,t} = r_k × (P_T+(y_t) / P_T-(y_t))（对比证据）
TEPO: A_{k,t} = Σ_{s≤t} w_s · r_k（似然传播）
DGPO: A_{k,t} = r_k × gate(H_{i,t}) × D_H(p_t, p_ref)（Hellinger 门控）

**共同模式**：都用一个 token 级权重 w_t 调制原始 GRPO advantage，区别在于 w_t 的计算方式。这对 VeFA 有重要启示——VeFA 的逐元素缩放 v 实际上等价于一种隐式的 token 级权重调制（通过 W₀ 的列空间结构）。

---

## 三、知识关联

- [[2026-06-01-VeFA与RL训练交叉-特征空间适配在强化学习中的适用性]] → 本篇是其「待深入问题 #1: VeFA 在 GRPO 上的实证对比」的完整回答。通过 TinyLoRA 的 u=13 实证和 ES 的全参数搜索结果，从正反两面论证了 VeFA 在 RL 中的定位
- [[2026-05-31-LoRA侵入维度消除策略-从发现到系统性解决方案]] → VeFA 的无侵入维度保证在 ES 和 TinyLoRA 的背景下获得新意义：侵入维度可能对 RL 训练无关紧要（13 参数也能 work），但分布鲁棒性是 VeFA 的独特价值
- [[2026-05-22-LoRA-GRPO最优配置实证-RL场景的Rank选择与超参数]] → Schulman 的 r=1 信息论论证被 TinyLoRA 进一步推向极端（u=13），但 Schulman 论证的"RL 不需要新方向"被 TinyLoRA 的随机投影部分修正
- [[2026-05-25-DoRA量化RL训练-方向幅度分解在低精度强化学习中的表现]] → TinyLoRA 的随机投影方向 + VeFA 的幅度缩放 ≈ 退化的 DoRA，DoRA 的归一化不稳定问题在极简参数场景中自动消失
- [[2026-05-17-LoRA高效微调前沿技术全景]] → 补充 TinyLoRA/ES/GTPO/CEPO/TEPO/DGPO 六种新方法到谱系
- [[2026-05-14-多目标GRPO-GDPO-ShapE-GRPO-AW-GRPO-RACO-OSPO-ARPO]] → GTPO/CEPO/TEPO/DGPO 是与多目标 GRPO 正交的维度（token 级 vs 目标级），可以叠加
- [[2026-05-23-QLoRA在RL训练中的精度影响-QeRL-NVFP4量化]] → QeRL 在 7B 上 90.8% GSM8K（NVFP4+LoRA），TinyLoRA 91%（13 参数纯 bf16）— 极端效率方向一致
- [[2026-05-29-NVFP4-vs-FP8在MoE-RL训练中的精确对比]] → ES 的无梯度特性可能绕过量化-RL 交互问题，值得在量化模型上测试 ES
- [[2026-05-04-GRPO-RLHF-DPO训练范式对比与实战]] → ES 代表了 RL 训练范式的新选择（ES vs PPO vs GRPO 三足鼎立）
- obs_notes: [[大模型核心术语]] → 补充了 TinyLoRA/ES/GTPO 等新概念

---

## 四、Actionable Insights

1. **VeFA-FFN + TinyLoRA-Attention 的混合方案**：基于 Hybrid-LoRA 发现 FFN 层 LoRA 足够，而 TinyLoRA 证明极简参数在 RL 中有效。建议 FFN 层用 VeFA（分布鲁棒性 + 无侵入维度），Attention 层用 TinyLoRA（方向灵活性）。参数预算：FFN 层 d=4096 个 v 参数，Attention 层 u=32 个 v 参数。

2. **veRL + TinyLoRA 集成**：TinyLoRA 已被 HuggingFace PEFT 库原生支持（TinyLoraConfig），可以直接通过 veRL 的 PEFT 集成使用。先用 u=32 在 GSM8K 上跑 baseline，再尝试 VeFA 对比。

3. **ES 作为 VeFA 的上界参考**：在做 VeFA 实证实验时，ES 应作为另一个 baseline。如果 VeFA 接近 ES 性能 → 说明 VeFA 的参数效率足够；如果 VeFA 远低于 ES → 说明方向多样性确实重要。

4. **Token 级 Credit Assignment 与 VeFA 的天然兼容**：VeFA 的 diag(v)·W₀ 在 token 级产生隐式的 attention 权重调制。GTPO 的熵加权或 CEPO 的对比证据可以直接叠加到 VeFA 训练中，不需要修改 VeFA 的参数化。

5. **Hermes Agent RL 自进化**：如果给 Hermes 加 RL 自进化能力，TinyLoRA 的 13 参数方案意味着几乎零存储成本。每次 skill 学习可以只存储 26 bytes 的 adapter diff。

6. **Hard Samples 收益递减的实践指导**：小模型 GRPO 训练中，数据难度应匹配模型容量。我们用 Qwen-2.5-1.5B/3B 做实验时，不应盲目追求 AIME 级别的困难数据。

---

## 五、待深入问题

1. **VeFA + TinyLoRA 精确对比实验设计**：在 Qwen2.5-7B 上，VeFA(d=4096) vs TinyLoRA(u=13) vs LoRA(r=16) 三组 GRPO 实验，benchmark: GSM8K/MATH500/AIME
2. **VeFA + GTPO 熵加权联合**：VeFA 的逐元素缩放 + GTPO 的 token 级熵加权是否能叠加收益
3. **ES + VeFA 混合**：ES 在 VeFA 缩放向量 v 空间做搜索（而非全参数空间），是否兼具两者优势
4. **TinyLoRA 的 MoE 适配**：全权重绑定在 MoE 模型上是否仍然有效（不同专家可能需要不同的 v）
5. **ES 在量化模型上的 RL 训练**：无梯度 ES 是否绕过量化-RL 交互问题
6. **Token 级 Credit Assignment 对 LoRA rank 需求的影响**：更精细的 credit 是否降低 rank 需求
7. **TinyLoRA 全权重绑定的理论极限**：13 参数 vs 1 参数的性能差距有多大
8. **ES + QeRL 联合**：ES 在 NVFP4 量化模型上做 RL 训练的可行性
9. **DGPO Hellinger Distance 在 VeFA 训练中的应用**：有界距离替代 KL 是否缓解 VeFA 的梯度受限问题

---

## 六、参考文献

1. Moriss et al. (2026). "Learning to Reason in 13 Parameters." Meta FAIR/Cornell/CMU. arXiv:2602.04118.
2. Novak et al. (2026). "Evolution Strategies at Scale: LLM Fine-Tuning Beyond Reinforcement Learning." arXiv:2509.24372v2.
3. Hybrid-LoRA Team (2026). "Hybrid-LoRA: Bridging Full Fine-Tuning and Low-Rank Adaptation for Post-Training." arXiv:2605.18822.
4. Tan & Pan (2026). "GTPO and GRPO-S: Token and Sequence-Level Reward Shaping with Policy Entropy." ICML 2026. arXiv:2508.04349.
5. CEPO Team (2026). "CEPO: RLVR Self-Distillation using Contrastive Evidence Policy Optimization." arXiv:2605.19436.
6. TEPO Team (2026). "Token-Level Policy Optimization: Linking Group-Level Rewards to Token-Level Aggregation via Sequence-Level Likelihood." arXiv:2604.12736.
7. DGPO Team (2026). "DGPO: Distribution Guided Policy Optimization for Fine Grained Credit Assignment." arXiv:2605.03327.
8. Hard Samples Team (2026). "Limits of Difficulty Scaling: Hard Samples Yield Diminishing Returns in GRPO-Tuned SLMs." arXiv:2604.06298.
9. Wang, Gu, Huang (2025). "VeFA: Vector-Based Feature Space Adaptation for Robust Model Fine-Tuning." arXiv:2510.19155.
10. Schulman et al. (2025). "LoRA Without Regret." Thinking Machines Lab.
11. Shao et al. (2024). "DeepSeekMath: GRPO." (GRPO 原始论文)
12. AlphaXiv Blog. "Evolution Strategies vs GRPO for LLM Fine-Tuning." https://alphaxiv.org/blog/es-for-fine-tuning-llms

---

## 相关笔记

- [2026-06-01-VeFA与RL训练交叉](./2026-06-01-VeFA与RL训练交叉-特征空间适配在强化学习中的适用性.md)
- [2026-05-31-LoRA侵入维度消除策略](./2026-05-31-LoRA侵入维度消除策略-从发现到系统性解决方案.md)
- [2026-05-22-LoRA-GRPO最优配置实证](./2026-05-22-LoRA-GRPO最优配置实证-RL场景的Rank选择与超参数.md)
- [2026-05-25-DoRA量化RL训练](./2026-05-25-DoRA量化RL训练-方向幅度分解在低精度强化学习中的表现.md)
- [2026-05-17-LoRA高效微调前沿技术全景](./2026-05-17-LoRA高效微调前沿技术全景.md)
- [2026-05-14-多目标GRPO](./2026-05-14-多目标GRPO-GDPO与ShapE-GRPO-多reward融合与冲突消解.md)
- [2026-05-23-QLoRA在RL训练中的精度影响](./2026-05-23-QLoRA在RL训练中的精度影响.md)
- [2026-05-04-GRPO训练范式对比](./2026-05-04-GRPO-RLHF-DPO训练范式对比与实战.md)
