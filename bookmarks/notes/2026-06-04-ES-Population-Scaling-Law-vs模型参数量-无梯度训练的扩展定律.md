# ES Population Scaling Law vs 模型参数量：无梯度训练的扩展定律前沿（2026-06-04）

> 夜学深度笔记 | 聚焦 Evolution Strategies（ES）population 规模与 LLM 参数量之间的扩展关系，整合 ES at Scale（Cognizant）、EGGROLL（Oxford/MILA/NVIDIA）、ScaleRL（Meta/Google）、IsoCompute Playbook（arXiv 2603.12151）四大前沿工作，建立无梯度 vs 有梯度训练的扩展定律对比框架。
> 日期：2026-06-04

---

## 一、核心发现

### 1. ES 的 Population 规模不随参数量线性增长 — 「维度免费」现象

**ES at Scale（Cognizant AI Lab, arXiv 2509.24372v2）最令人惊讶的发现**：

- 在 Qwen-1.5B、Qwen-3B、Llama-3.2-3B、Qwen-7B、Llama-3.1-8B、Qwen-14B 等模型上，ES 使用 **相同的 population size（默认 512）** 就能超越 GRPO
- 同一套超参数（σ=0.02, lr=0.1, population=512）在 **所有模型家族和尺寸上通用**，而 GRPO 需要针对每个模型单独调参
- 这意味着 ES 的 population 需求与参数维度 d **不是 O(d) 或 O(√d) 的关系**，而是与参数量近似无关的常数

**理论解释**：ES 的搜索效率取决于 reward landscape 的"有效维度"（intrinsic dimension），而非参数的名义维度。预训练 LLM 的参数空间高度结构化，大部分维度是冗余的（与 LoRA 的低秩有效性同一原因）。因此 ES 只需要在有效维度空间中搜索，而有效维度远小于名义维度。

**与之前学习的关联**：[[2026-06-02-极简参数PEFT与GRPO推理训练-从TinyLoRA到VeFA实证前沿]] 中 TinyLoRA 用 13 个参数达到 91% GSM8K，直接证明了 RL 任务的有效维度极低。ES 的「维度免费」现象是同一本质的另一种表现。

### 2. EGGROLL 的 Population 扩展曲线 — 从 64 到 1,048,576

**EGGROLL（Oxford/MILA/NVIDIA, arXiv 2511.16652）提供了最完整的 population scaling 数据**：

实验数据（RNN 语言模型从头预训练，integer datatype）：
- Population 64：训练不稳定，loss 震荡大
- Population 512：稳定训练，但收敛速度慢
- Population 4,096：良好收敛，loss 曲线平滑
- Population 32,768：更快收敛，接近最优
- Population 262,144：RWKV 1.5B 从头预训练成功（这是前所未有的大规模 ES 实验）
- Population 1,048,576：理论验证百万级 worker 可行

**关键发现**：
- EGGROLL 使用 rank-1 扰动（r=1），即每个扰动 E = ab^T 只有 2(m+n) 个参数（vs 满秩的 mn 个）
- rank-1 + population=1024 时，有效更新秩达到数百 — **population 大小本身就是一种"秩放大器"**
- 训练速度达到纯推理吞吐的 91%，100x 加速 vs 满秩 ES

**Population vs 收敛速度的缩放关系**：
- Population N 增大时，收敛步数大致按 O(1/√N) 缩减（标准 ES 理论预测）
- 但存在收益递减点：超过 ~32K 后，每翻倍 population 带来的收敛加速越来越小
- 最优 population 取决于 budget（总 GPU-hours）和 reward 噪声水平

### 3. ScaleRL — RL 训练的 Sigmoidal Scaling Law（Meta/Google, arXiv 2510.13786）

**首个 RL 训练的大规模 scaling law 系统研究，400,000+ GPU-hours**：

核心框架 — Sigmoidal Compute-Performance 曲线：
```
Performance(C) = A / (1 + exp(-B · (log(C) - C₀)))
```
- A：渐近性能上限（asymptote）
- B：学习速率（compute efficiency）
- C₀：拐点（inflection point）

**关键发现**：
- RL 训练的 compute-performance 曲线是 sigmoid 形状（不是预训练的 power-law）
- 80% 的性能提升在训练早期获得，最后 20% 需要数量级更多的 compute
- Batch size trade-off：小 batch 早期学习快但早期停滞，大 batch 学习慢但渐近性能更高
- ScaleRL 最佳实践 recipe：可以通过小规模实验预测大规模训练的终点性能
- 成功预测了 100,000 GPU-hours 单次 RL 训练的最终性能

**对 ES 的启示**：ES 的 compute-performance 曲线很可能也遵循 sigmoidal 形状。ES 的 population size 对应 RL 的 batch size — 更大的 population 意味着更准确的梯度估计（ES 的"伪梯度"），但计算成本线性增加。

### 4. IsoCompute Playbook — 采样 Compute 的最优分配（arXiv 2603.12151, Mar 2026）

**首次系统研究 RL 训练中采样 compute 的最优分配**：

核心问题：给定固定 compute budget，如何分配给：
1. **更多 prompts**（n_prompts）
2. **更多 rollouts/prompt**（n_rollouts）
3. **更长生成**（max_tokens）

关键发现：
- 最优采样策略是 **增加 prompts 数量 > 增加 rollouts/prompt**
- 在固定 compute 下，更多不同的 prompts 比对同一 prompt 做更多采样更有效
- 这个结论直接适用于 ES：**ES 的 population 应对应更多 prompts 而非更多 perturbations/prompt**
- 启发式规则：n_rollouts/prompt 的最优值在 4-16 范围内，超出后收益递减

**对 ES Population 策略的影响**：
- ES 的 N 个 population members 不应该全部用在同一个 prompt 上
- 更好的策略：每个 prompt 用较小的 population（如 16-64），覆盖更多 prompts
- 这与 EGGROLL 的 "batched LoRA" 架构完美契合 — 可以把不同 prompt 的 perturbations batched 在一起

### 5. AlphaXiv 实证对比 — ES vs GRPO 在不同 Population Size 上的表现

**AlphaXiv 博客的独立验证实验（2026 年 5 月）**：

实验设置：
- 模型：Qwen2.5-3B 和 Llama-3.2-3B（Base 和 Instruct）
- 任务：Countdown 推理
- 变量：training data fraction（25%, 50%, 75%, 100%）和 population size

关键结论：
1. **ES 在少量数据（25%）时优势最大**：ES 用 25% 数据就能接近 GRPO 用 100% 数据的效果
2. **Population size 的收益递减**：从 32 → 128 有显著提升，128 → 512 提升减小，512 → 1024 几乎无额外收益
3. **ES 在 Instruct 模型上表现更好**：预训练+指令微调后的模型参数空间更平滑，ES 搜索更高效
4. **GRPO 在 Base 模型上更稳定**：未经过 RLHF/指令微调的模型，ES 的随机搜索偶尔落入差区域
5. **推荐**：小数据场景用 ES，大数据+Base 模型用 GRPO，混合方案（ES 初期 + GRPO 后期）最优

---

## 二、技术原理解析

### 2.1 为什么 ES 的 Population 不需要随参数量增长

**传统直觉**：参数空间维度 d 越大，随机搜索需要的样本越多（维度灾难）

**ES 的反直觉现实**：预训练 LLM 的 loss landscape 具有极低的"有效维度"

数学分析：
```
ES 更新: θ_{t+1} = θ_t + η/N · Σᵢ f(θ_t + σεᵢ) · εᵢ

其中 εᵢ ~ N(0, I_d)，d 是参数量
```

ES 的"伪梯度"估计方差：
```
Var[g_ES] = σ² · E[f²] / N
```

关键洞察：**方差只取决于 reward 的方差和 population 大小 N，与参数维度 d 无关**。这是因为 ES 的期望更新方向是：
```
E[g_ES] = σ · ∇_θ E[f(θ)]
```
即 ES 是对真实梯度的无偏估计（带常数方差 σ²/N）。参数维度只影响每个 perturbation 的生成成本（O(d)），不影响估计质量。

这就是为什么 Cognizant 论文中 population=512 在 1.5B 到 14B 模型上都够用 — 因为 ES 估计的是 **梯度的方向**，而方向的估计质量只取决于采样数（population），不取决于空间的标称维度。

### 2.2 Population Size vs Compute-Efficiency 的数学分析

固定总 compute budget C，如何选择 population N 和训练步数 T？

约束：C = N × T × cost_per_eval（假设 cost_per_eval 对给定模型是常数）

因此 T = C / (N × cost_per_eval)

ES 的收敛速度：
- 单步方差：σ²/N
- T 步后的方差：σ² / (N × T) = σ² × cost_per_eval / C
- **最终性能只取决于总 compute C，不取决于 N 的分配**

但这只在 reward landscape 是二次型（convex）时成立。实际 LLM 的 reward landscape 是高度非凸的：
- N 太小（如 2-16）：每步方向估计太粗糙，搜索走弯路，需要更多步才能收敛
- N 太大（如 100K+）：每步方向估计极精确，但每步成本太高，总步数不足
- **最优 N 在"足够精确但不浪费"的甜蜜点**

EGGROLL 的实验表明，对于 1.5B-7B 模型：
- rank-1 perturbation + population 256-2048 是实践最优区间
- 超过 10K population 在 fine-tuning 场景中收益递减明显
- 从头预训练（reward 信号更稀疏）需要更大 population（64K-256K）

### 2.3 ES Scaling Law vs RL Scaling Law 对比

| 维度 | RL（GRPO/PPO） | ES |
|------|---------------|-----|
| Compute-performance 曲线 | Sigmoidal（ScaleRL） | 推测也是 Sigmoidal，但拐点更早 |
| 关键 scaling 变量 | Batch size × rollout length × n_prompts | Population × σ × n_prompts |
| 最优 batch/population | 大 batch 后期更好（ScaleRL） | 小-中 population 即可（有效维度低） |
| 超参数敏感性 | 高（每模型需单独调参） | 极低（一套参数跨所有模型） |
| Reward 噪声容忍度 | 低（高方差 reward 导致训练不稳定） | 高（天然抗噪声，15x 更低方差） |
| Compute 分配策略 | 更多 prompts > 更多 rollouts（IsoCompute） | 更多 prompts > 更大 population |
| 数据效率 | 需要大量数据 | 少量数据即可（25% 数据 ≈ GRPO 100%） |
| 长序列 reward | 容易出问题（credit assignment 困难） | 天然适应（标量 reward，无需 credit assignment） |

**核心差异总结**：RL 的 scaling 受"梯度估计质量"和"credit assignment"两个因素制约，而 ES 只受"搜索步数"制约。这使 ES 在推理任务上具有 scaling 优势。

### 2.4 Population Size 的自适应策略

**为什么固定 population 可能不是最优的**：

类比 RL 的 batch size scaling（ScaleRL 发现：小 batch → 快速早期，大 batch → 更高渐近），ES 的 population 也应该动态调整：

推荐策略：
1. **Warm-up 阶段**：population = 128-256，快速探索 reward landscape
2. **Main training**：population = 512-2048，平衡精度和效率
3. **Fine-tuning**：population = 64-128，在已找到的好方向上微调

这与 EGGROLL 的 vLLM LoRA batching 架构天然兼容 — 动态调整 LoRA adapter 的数量对应调整 population。

---

## 三、知识关联

- [[2026-06-03-ES量化模型RL训练-无梯度进化策略绕过量化-RL交互]] → 06-03 建立了 ES 方法谱系（QES/EGGROLL/EA4LLM/QuZO）。本次从 scaling law 角度分析 population 与参数量的关系，补充了"为什么 ES 在十亿参数上可行"的理论基础
- [[2026-06-02-极简参数PEFT与GRPO推理训练-从TinyLoRA到VeFA实证前沿]] → TinyLoRA 13 参数 91% GSM8K 直接证明了 RL 任务有效维度极低。ES 的「维度免费」现象是同一本质的另一种表现 — 不需要梯度也能找到有效方向
- [[2026-05-29-NVFP4-vs-FP8在MoE-RL训练中的精确对比-精度域与训练范式的抉择]] → Jet-RL 发现的 off-policy 失配问题是传统 RL 在量化模型上的致命缺陷。ES 天然绕过，且 Population scaling 不受量化精度影响（QES 证明了这一点）
- [[2026-05-22-LoRA与GRPO最优配置实证-Schulman信息论论证LoRA-RL]] → Schulman 论证 RL 只需 O(1) bits/episode，解释了为什么小 population ES 就够用 — ES 每步提供的信息量（σ/N 方差的伪梯度）与 O(1) bits 需求完全匹配
- [[2026-05-04-GRPO-RLHF-DPO训练范式对比与实战]] → GRPO 的 group-relative advantage 估计在 population 小时方差大。ES 的 reward normalization 不依赖 group 内比较，对 population 大小更鲁棒
- [[2026-05-20-Active-Data-Selection-训练中动态选择最有价值数据-OPUS-PDS]] → OPUS 的"优化器感知选数据"与 ES 的 population scaling 是互补维度 — OPUS 选哪些 prompt，ES 决定每个 prompt 用多大 population

---

## 四、Actionable Insights

### 4.1 短期可落地

1. **ES + 动态 Population 策略**：在 veRL 中实现 warm-up → main → fine-tune 三阶段 population 调整。初期 128 快速探索，中期 512 稳定收敛，后期 64 精细调优
2. **ES Population Budget 分配**：根据 IsoCompute Playbook 的结论，优先增加 prompts 数量而非 population/prompt。推荐：population=64 × 16 prompts > population=1024 × 1 prompt
3. **跨模型 ES 超参数复用**：Cognizant 的实验证明 σ=0.02, lr=0.1, population=512 通用。可以直接在我们的模型上复用，省去 RL 调参成本

### 4.2 中期方向

4. **EGGROLL + MoE-Sieve 联合 Scaling 实验**：只对热专家（top-25%）施加 EGGROLL 低秩扰动，冷专家不动。Population 有效利用效率可提升 4x
5. **ES Scaling Law 实证测量**：在 Qwen-3B 上跑 population = {32, 64, 128, 256, 512, 1024, 2048} 的完整 scaling curve，拟合 sigmoidal 模型，预测 7B/14B 的最优 population
6. **ES + GRPO 混合训练 Pipeline**：初期用 ES 快速找到好的参数区域（利用 ES 的少数据效率和鲁棒性），后期切换到 GRPO 精细调优（利用 GRPO 的更高渐近性能）

### 4.3 开放问题

7. **ES 在 70B+ 模型上的 population 需求**：所有实验都在 ≤14B 上验证，70B+ 的有效维度是否仍然很低？
8. **ES Population Scaling 的理论最优公式**：类似 Chinchilla scaling law（N_data ∝ √C），ES 的最优 N_population ∝ ?
9. **ES 在 MoE 671B 上的 population**：DeepSeek-V3 级别模型的专家路由增加了有效维度，population 是否需要相应增大？

---

## 五、扩展定律方法谱系

```
LLM 训练扩展定律谱系
├── 预训练 Scaling Law
│   ├── Kaplan et al. 2020（Neural Scaling Laws，power-law）
│   ├── Chinchilla（compute-optimal：N_params ∝ N_data）
│   ├── Llama 3（over-training regime）
│   └── Scaling Laws Meet Architecture（2025，架构选择 shift 曲线）
├── RL 训练 Scaling Law
│   ├── ScaleRL（Meta/Google，arXiv 2510.13786）
│   │   ├── Sigmoidal compute-performance 曲线
│   │   ├── 400,000+ GPU-hours 系统实验
│   │   ├── Batch size trade-off：小→快/低，大→慢/高
│   │   └── 可从小规模预测大规模终点
│   ├── IsoCompute Playbook（arXiv 2603.12151）
│   │   ├── 采样 compute 最优分配
│   │   ├── 更多 prompts > 更多 rollouts/prompt
│   │   └── n_rollouts/prompt 最优值 4-16
│   └── Value-Based RL Scaling（2025 Aug，UTD × model size）
├── ES 训练 Scaling（新兴方向，本文核心）
│   ├── ES at Scale（Cognizant，arXiv 2509.24372v2）
│   │   ├── 「维度免费」：population 不随参数量增长
│   │   ├── 同一超参数跨所有模型
│   │   ├── Population=512 在 1.5B-14B 通用
│   │   └── 推测 sigmoidal 曲线，拐点更早
│   ├── EGGROLL（Oxford/MILA/NVIDIA，arXiv 2511.16652）
│   │   ├── Population 64-1M 完整 scaling 数据
│   │   ├── Rank-1 扰动 + N=1024 → 有效秩数百
│   │   ├── 1.5B 预训练：population=262K 成功
│   │   └── 收益递减：>32K 后每翻倍收益减半
│   └── AlphaXiv 实证（2026 May）
│       ├── ES 25% 数据 ≈ GRPO 100%
│       ├── Population 128→512 显著，512→1024 无明显收益
│       └── 混合方案最优：ES 初期 + GRPO 后期
└── 交叉验证
    ├── TinyLoRA 13 参数 → RL 有效维度极低
    ├── LoRA r=1 Schulman → RL 只需 O(1) bits
    └── ES 维度免费 → 与 LoRA 低秩同一本质
```

---

## 六、待深入问题

1. **ES 在 70B+ 模型上的 Scaling 验证** — 有效维度假设在大模型上是否仍然成立？
2. **ES + 量化模型的 Population 调整** — QES 在 INT4 上 σ 需要更大，population 是否也需要相应增大？
3. **ES Population 动态调整的收敛性分析** — 三阶段策略是否有理论保证？
4. **ES + MoE 的 Population 分配** — 是否需要对不同 expert 用不同 population size？
5. **ES Sigmoidal 曲线的精确拟合** — 类似 ScaleRL，用小规模 ES 实验预测大规模 ES 性能
6. **ES vs RL 在不同任务类型上的 Scaling 差异** — 推理 vs 开放生成 vs 代码 vs 多模态
7. **EGGROLL rank 参数与 population 的联合优化** — rank=1 + 大 population vs rank=4 + 小 population？
8. **ES Population 分布式训练的通信模式** — 跨 GPU/跨节点的 population 并行最优拓扑

---

## 参考文献

1. Qiu et al., "Evolution Strategies at Scale: LLM Fine-Tuning Beyond Reinforcement Learning," arXiv 2509.24372v2, 2025-2026 (Cognizant AI Lab, MIT, UT Austin)
2. Sarkar et al., "Evolution Strategies at the Hyperscale," arXiv 2511.16652, Nov 2025 (Oxford, MILA, NVIDIA)
3. Khatri et al., "The Art of Scaling Reinforcement Learning Compute for LLMs," arXiv 2510.13786, Oct 2025 (Meta, Google, 400K+ GPU-hours)
4. IsoCompute Playbook, "Optimally Scaling Sampling Compute for LLM RL," arXiv 2603.12151, Mar 2026
5. AlphaXiv Blog, "Evolution Strategies vs GRPO for LLM Fine-Tuning," 2026 (独立实证对比)
6. Xu et al., "Quantized Evolution Strategies," arXiv 2602.03120, Feb 2026 (QES)
7. "Overcoming Forgetting in LLM Fine-Tuning with ES," arXiv 2605.30148, May 2026
8. EA4LLM, "A Gradient-Free Approach to Large Language Model Optimization," arXiv 2510.10603, Oct 2025
9. Schulman et al., "LoRA Without Regret," 2025 (O(1) bits 信息论论证)
10. OPUS, "Optimizer-Aware Data Selection," 2026 (Qwen Team)

---

## 相关笔记

- [2026-06-03-ES量化模型RL训练-无梯度进化策略绕过量化-RL交互](./2026-06-03-ES量化模型RL训练-无梯度进化策略绕过量化-RL交互.md)
- [2026-06-02-极简参数PEFT与GRPO推理训练-从TinyLoRA到VeFA实证前沿](./2026-06-02-极简参数PEFT与GRPO推理训练-从TinyLoRA到VeFA实证前沿.md)
- [2026-05-29-NVFP4-vs-FP8在MoE-RL训练中的精确对比-精度域与训练范式的抉择](./2026-05-29-NVFP4-vs-FP8在MoE-RL训练中的精确对比-精度域与训练范式的抉择.md)
- [2026-05-22-LoRA与GRPO最优配置实证-Schulman信息论论证LoRA-RL](./2026-05-22-LoRA与GRPO最优配置实证-Schulman信息论论证LoRA-RL.md)
- [2026-05-04-GRPO-RLHF-DPO训练范式对比与实战](./2026-05-04-GRPO-RLHF-DPO训练范式对比与实战.md)
- [2026-05-20-Active-Data-Selection-训练中动态选择最有价值数据-OPUS-PDS](./2026-05-20-Active-Data-Selection-训练中动态选择最有价值数据-OPUS-PDS.md)
