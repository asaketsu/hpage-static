# Active Data Selection：LLM 训练动态数据选择前沿技术

> 夜学日期：2026-05-20 ｜ 深度：L3 ｜ 主题：训练中动态选择最有价值数据的方法论全景
> 标签：#ActiveDataSelection #动态数据选择 #GRPO #LLM训练 #课程学习 #数据工程 #DataCentricAI

---

## 一、核心发现

### 1. OPUS：优化器感知的数据选择——8x 预训练效率突破

**论文**：OPUS: Towards Efficient and Principled Data Selection in LLM Pre-training (arxiv 2602.05400, Qwen Team/阿里 + 上交 EPIC Lab)

核心创新：在**优化器诱导的更新空间**（optimizer-induced update space）中定义数据效用，而非原始梯度空间。

- 传统方法在 raw gradient space 打分，但 LLM 用 AdamW/Muon 训练时，预条件矩阵会重塑有效更新方向——产生根本性错配
- OPUS 评分 = 样本 optimizer-shaped 有效更新 与 稳定代理目标下降方向 的对齐度
- 使用 **Boltzmann 采样** 平衡 proxy alignment 和冗余控制
- **实验**：GPT-2 Large/XL on FineWeb-Edu，30B token OPUS 选数据 > 全量 200B token 训练效果
- 来源：Qwen 团队，工业级验证

### 2. PDS：最优控制视角的数据选择（ICLR 2025）

**论文**：Data Selection via Optimal Control for Language Models (Microsoft Research + 清华 CoAI)

将数据选择建模为**广义最优控制问题**，用 Pontryagin 最大值原理（PMP）求解。

- PMP 给出一组必要条件，刻画最优数据选择与 LM 训练动力学的**精确关系**
- 引入"目标向量" λ*_t 捕获**长程训练动态**——不同于静态质量过滤
- 三步流程：训练数据评分器 → 大规模推理选数据 → 用选中语料预训练
- PDS 选出的 CommonCrawl 数据：跨模型尺寸一致提升下游任务性能
- 与启发式过滤（dedup/pattern matching）根本不同：**训练过程感知**

### 3. GREATS：Taylor 展开近似的高效在线选数据（NeurIPS 2024）

**论文**：GREATS: Online Selection of High-Quality Data for LLM Training in Every Iteration (Stanford + Princeton)

每次训练迭代动态选 batch——**不需要参考模型**。

- 贪心算法优化数据 batch 质量，用 Taylor 展开近似边际增益
- 一阶近似：个体梯度 ∙ 虚拟模型（已用选中 batch 更新一步后）的验证损失梯度
- 开发了一系列规模化技术（Hessian 近似、批内并行）
- 显著提升收敛速度和泛化性能

### 4. DOTS + Rollout Replay：GRPO 微调数据效率 25-65% 提升（NeurIPS 2025）

**论文**：Improving Data Efficiency for LLM RL Fine-tuning Through Difficulty-targeted Online Data Selection and Rollout Replay

针对 RL 微调（特别是 GRPO）的数据效率问题。

- **自适应难度**概念：优先选择**中等难度**问题——最有信息量的学习信号
- Attention-based 框架：只需对**小规模参考集**做 rollout，其余问题通过相似度估计难度
- **Rollout Replay**：复用历史 rollout 减少生成成本
- 跨 6 个 LLM-数据集组合，RL 微调时间减少 **23-62%**
- 有开源实现（ASTRAL-Group/data-efficient-llm-rl）

### 5. CPPO/DPPO：GRPO 加速的 Completion 剪枝（NeurIPS 2025 + arxiv 2026）

**CPPO**（NeurIPS 2025）：Completion Pruning Policy Optimization
- 关键发现：不是所有 completion 对策略训练贡献相同，贡献取决于**相对 advantage**
- 剪枝低绝对 advantage 的 completion → GSM8K **8x 加速**，Math **3.5x 加速**
- 动态 completion 分配：剪枝后空出 GPU 算力分配给更多问题

**DPPO**（arxiv 2026）：Dynamic Pruning Policy Optimization
- 层级重要性采样 + 数学推导的重缩放因子 → **无偏梯度**
- 不改变原始 GRPO 优化目标，理论上严格等价

### 6. CurES：RL 推理课程学习（ICLR 2026）

**论文**：CurES: From Gradient Analysis to Efficient Curriculum Learning for Reasoning LLMs (人大 + Wang Jun)

从 RL 梯度优化角度系统分析课程学习。

- **两个关键因素**：① 训练 prompt 采样分布 → 决定梯度下降收敛速率；② rollout 数量分配 → 影响梯度一致性/稳定性
- 理论推导 prompt 采样分布与收敛速率的关系
- 与 DOTS 互补：CurES 关注"选哪些 prompt"，DOTS 关注"用多少 rollout"

---

## 二、技术原理解析

### 2.1 三代数据选择范式演进

```
第一代（静态过滤）：
  启发式规则 → 去重/模式匹配/质量分类器 → 训练前一次性筛选
  代表：FineWeb、The Pile 过滤管线
  局限：与训练过程无关，不知道模型当前最需要什么数据

第二代（模型驱动评分）：
  小代理模型打分 → perplexity/loss 过滤 → DSIR/RDS
  代表：MATES (NeurIPS 2024)
  改进：模型感知，但仍是训练前离线完成

第三代（在线动态选择）：★ 本次重点
  训练中每步动态评分 → 梯度/优化器/损失感知 → 适应性选择
  代表：OPUS/PDS/GREATS/DOTS/CPPO
  优势：数据选择随模型状态进化
```

### 2.2 在线数据选择的理论基础

**核心问题**：给定候选 batch B_t = {z_1, ..., z_N}，选 K < N 个样本用于训练。

**方差最小化视角**（Omission/重要性采样）：
- 有放回采样时，最优采样权重 ∝ 梯度范数 ‖∇ℓ(θ, z_i)‖
- 无放回时，最优加权 Bernoulli 采样 → Omission 用历史 EMA 替代额外前向传播

**验证损失最小化视角**（GREATS）：
- 选 batch 使验证损失下降最大：max_{S⊂B, |S|=K} L_val(w_{t+1}(S)) - L_val(w_t)
- Taylor 展开：U(zi|Ŝ) ≈ ⟨g(zi), ∇_w L_val(ŵ_{t+1}(Ŝ))⟩
- 贪心选最大边际增益

**优化器感知视角**（OPUS）：
- AdamW 更新：θ_{t+1} = θ_t - η · m_t / (√v_t + ε)
- 有效更新方向 ≠ 原始梯度方向
- OPUS 在 H^{-1}g 空间打分（H = AdamW 二阶矩的近似）
- 评分：s(z) = ⟨H^{-1}∇ℓ(z), d_proxy⟩ 其中 d_proxy 是代理模型的下降方向

**最优控制视角**（PDS）：
- 状态方程：θ_{t+1} = θ_t - η∇ℓ(θ_t, γ_t ⊙ B_t)
- 目标：min J(γ) = L_val(θ_T) s.t. γ_t ∈ {0,1}^N
- PMP 必要条件 → 协态变量 λ*_t 编码长程训练动态
- λ*_t · ∇ℓ(θ_t, z_i) → 数据 z_i 在第 t 步的"长期价值"

### 2.3 RL 微调中的数据效率

**GRPO 原始公式的问题**：
- 每个问题采样 G 个 completion → O(G) 生成成本
- 所有问题使用相同 rollout 数量 → 不区分信息量
- 没有考虑问题难度的动态变化

**DOTS 解法**：
1. 预计算：对小参考集做完整 rollout，记录 reward → 得到"自适应难度"
2. 训练时：用 attention 模型预测剩余问题的难度（基于 embedding 相似度）
3. 选择中等难度问题（信息量最大）
4. Rollout Replay：缓存历史 rollout，按一定概率复用

**CPPO/DPPO 解法**：
1. 生成 G 个 completion 后，计算绝对 advantage |Â_i|
2. 剪枝 advantage 低的 completion（CPPO 直接丢弃，DPPO 用重要性采样保持无偏）
3. 空出计算 → 可以处理更多问题

### 2.4 方法对比矩阵

| 方法 | 阶段 | 信号 | 计算开销 | 适用场景 | 顶会 |
|------|------|------|----------|----------|------|
| OPUS | 预训练 | 优化器感知梯度+代理目标 | 中（代理模型+投影） | 大规模预训练 | arxiv 2026 |
| PDS | 预训练 | PMP 协态变量（长程动态） | 中（评分器训练） | 预训练数据筛选 | ICLR 2025 |
| GREATS | 预训练/微调 | Taylor 展开验证损失 | 低（一阶近似） | 在线 batch 选择 | NeurIPS 2024 |
| DOTS | RL微调 | 自适应难度+attention | 低（参考集小） | GRPO 推理训练 | NeurIPS 2025 |
| CPPO | RL微调 | Advantage 剪枝 | 极低（无额外开销） | GRPO 加速 | NeurIPS 2025 |
| DPPO | RL微调 | 层级重要性采样 | 极低（重缩放因子） | GRPO 无偏加速 | arxiv 2026 |
| CurES | RL微调 | 梯度方差+收敛分析 | 中（梯度统计） | 课程学习推理 | ICLR 2026 |
| DWM | 预训练 | 双层优化权重模型 | 中（权重模型训练） | 数据混合优化 | ICML 2025 |
| Omission | 预训练 | 历史 EMA 梯度范数 | 极低（增量更新） | 数据剪枝 | arxiv |
| NICE | 指令微调 | 策略梯度影响估计 | 中（非可微指标） | 任务特定微调 | ICML 2025 |

---

## 三、知识关联

- [[2026-05-05-大模型数据工程-合成数据-数据质量-课程学习]] → 本次深入了数据工程的"动态选择"维度，补充了 05-05 笔记中仅涉及静态课程学习的内容。课程学习的梯度方差分析（Pythia 实验）与 CurES 的 RL 梯度分析形成互补
- [[2026-05-04-GRPO-RLHF-DPO-训练范式对比与实战]] → DOTS/CPPO/DPPO 直接作用于 GRPO，是 GRPO 工程实践的关键加速技术。与 05-04 笔记中 GRPO 推导链完美衔接
- [[2026-05-14-多目标 GRPO GDPO ShapE-GRPO]] → CurES 的 prompt 采样分布理论可推广到多目标场景，与 GDPO 的分维度标准化互补
- [[2026-05-19-蒸馏量化RL三联流水线]] → 三联流水线中的 RL 阶段可用 DOTS/CPPO 加速，DenseGRPO 的 step-wise reward 与 DOTS 的自适应难度有交叉
- [[2026-05-10-蒸馏量化联合策略-QAD-LBLLM-CapacityGap]] → NICE 的非可微指标数据选择可应用于量化后模型的数据策展
- obs_notes: [[LLM的不确定性]] → OPUS/GREATS 本质上是在量化数据对模型更新的不确定性/信息量
- obs_notes: [[大模型核心术语]] → 补充 Active Data Selection 作为新术语

---

## 四、Actionable Insights

1. **GRPO 训练加速可落地**：CPPO 已开源（github.com/lzhxmu/CPPO），8x 加速可直接用于 Hermes Agent 的工具调用训练。DOTS 有 ASTRAL-Group 开源实现。如果我们做 GRPO 微调，应该默认启用 CPPO
2. **预训练数据管线升级**：OPUS 的优化器感知选数据思路可指导我们的数据工程。当前 05-05 笔记中的启发式过滤可以升级为模型感知过滤
3. **课程学习与 RL 训练结合**：CurES 的梯度分析框架可用于设计 Agent RL 训练的数据调度策略——先用简单工具调用任务 warmup，再过渡到复杂多步规划
4. **Hermes 自训练数据策展**：如果我们用 Agent 交互数据做自进化训练，DOTS 的"中等难度优先"策略直接适用——过滤太简单和太难的交互记录
5. **对已有 Skill 的增强**：
   - `grpo-rl-training` skill 可加入 CPPO/DPPO 加速建议
   - `asa-pipeline` 的学习材料选择可参考自适应难度概念

---

## 五、待深入问题

1. **OPUS + MoE 训练**：MoE 的路由不均导致不同 expert 对不同数据的敏感度差异，OPUS 的代理目标应如何适配？
2. **在线选择的分布式实现**：FSDP/Megatron 下如何高效实现在线数据选择？评分计算如何与梯度计算 overlap？
3. **CPPO + 多目标 GRPO**：CPPO 剪枝低 advantage completion 时，如果使用 GDPO 多维度 reward，剪枝策略如何设计？
4. **PDS 协态变量的计算效率**：长程训练动态的 λ*_t 反向计算在千卡训练中的工程可行性
5. **自适应难度的在线更新**：DOTS 的参考集难度是预计算的，训练中模型能力提升后如何动态更新？
6. **OPUS + 合成数据**：合成数据的 OPUS 评分与自然数据的差异，是否可以指导合成数据配方优化
7. **CurES 的 rollout 预算分配理论**：最优 rollout 数量与 prompt 难度的定量关系

---

## 参考文献

1. Wang et al., "OPUS: Towards Efficient and Principled Data Selection in LLM Pre-training" (arxiv 2602.05400, 2026)
2. Gu et al., "Data Selection via Optimal Control for Language Models" (ICLR 2025)
3. Wang et al., "GREATS: Online Selection of High-Quality Data for LLM Training" (NeurIPS 2024)
4. ASTRAL-Group, "Improving Data Efficiency for LLM RL Fine-tuning Through Difficulty-targeted Online Data Selection and Rollout Replay" (NeurIPS 2025)
5. Zhang et al., "CPPO: Accelerating the Training of GRPO-Based Reasoning Models" (NeurIPS 2025)
6. Zhang et al., "DPPO: Unbiased Dynamic Pruning for Efficient Group-Based Policy Optimization" (arxiv 2603.04135, 2026)
7. Zeng et al., "CurES: From Gradient Analysis to Efficient Curriculum Learning for Reasoning LLMs" (ICLR 2026)
8. DWM, "LLM Data Selection and Utilization via Dynamic Bi-level Optimization" (ICML 2025)
9. NICE, "NICE Data Selection for Instruction Tuning with Non-differentiable Evaluation Metric" (ICML 2025)
10. "Learn from the Past: Dynamic Data Pruning" (Omission, OpenReview)
11. Li et al., "A Survey on Data Selection for Language Models" (arxiv 2402.16827, 2024)
12. "Hard Examples Are All You Need: Maximizing GRPO Post-Training Under Annotation Budgets" (arxiv 2508.14094, 2025)
13. Jiang et al., "DeCS: Overthinking Reduction with Decoupled Rewards and Curriculum Data Scheduling" (ICLR 2026)

## 相关笔记
- [数据治理-Data-Catalog](2026-05-03-数据治理-Data-Catalog.md)
- [数据治理-Data-Lineage血缘分析](2026-05-05-数据治理-Data-Lineage血缘分析.md)
- [数据治理-Data-Quality数据质量](2026-05-05-数据治理-Data-Quality数据质量.md)
- [数据治理-data-quality](2026-05-08-数据治理-data-quality.md)
- [数据治理趋势AI工程化](2026-05-10-数据治理趋势AI工程化.md)
- [数据治理框架2026趋势](2026-05-16-数据治理框架2026趋势.md)
- [数据治理-data-catalog](2026-05-18-数据治理-data-catalog.md)
- [数据治理-data-quality-v2](explore/2026-05-04-数据治理-data-quality-v2.md)
- [数据治理-lineage-v2](explore/2026-05-04-数据治理-lineage-v2.md)
- [data-catalog-数据治理](explore/2026-05-05-data-catalog-数据治理.md)
- [data-governance-framework](explore/2026-05-06-data-governance-framework.md)
- [data-governance-framework-2026](explore/2026-05-07-data-governance-framework-2026.md)
- [data-quality-governance](explore/2026-05-07-data-quality-governance.md)
- [data-catalog](explore/2026-05-08-data-catalog.md)
- [data-catalog-governance](explore/2026-05-09-data-catalog-governance.md)
- [data-lineage-governance-tools](explore/2026-05-09-data-lineage-governance-tools.md)
- [data-quality-framework](explore/2026-05-09-data-quality-framework.md)
- [数据治理-governance-framework](explore/2026-05-09-数据治理-governance-framework.md)
- [数据治理框架-2025对比](explore/2026-05-09-数据治理框架-2025对比.md)
- [data-quality-governance-2026](explore/2026-05-10-data-quality-governance-2026.md)
- [数据治理-数据血缘-lineage](explore/2026-05-10-数据治理-数据血缘-lineage.md)
- [数据治理框架-2026最佳实践](explore/2026-05-10-数据治理框架-2026最佳实践.md)
- [data-lineage-governance](explore/2026-05-11-data-lineage-governance.md)
- [data-quality-governance-framework](explore/2026-05-11-data-quality-governance-framework.md)
- [数据治理-data-catalog](explore/2026-05-19-数据治理-data-catalog.md)
- [数据治理-data-quality](explore/2026-05-19-数据治理-data-quality.md)
- [数据治理-lineage](explore/2026-05-19-数据治理-lineage.md)
- [数据治理-data-catalog](orphan/2026-05-05-数据治理-data-catalog.md)
- [data-lineage-governance](orphan/2026-05-08-data-lineage-governance.md)
- [数据治理-框架演进](orphan/2026-05-08-数据治理-框架演进.md)
- [数据血缘-lineage-工具全景](orphan/2026-05-09-数据血缘-lineage-工具全景.md)
- [skills-catalog](orphan/skills-catalog.md)
- [skills-data-science](orphan/skills-data-science.md)
- [Karpathy-LLM-Wiki-second-brain](2026-04-05-Karpathy-LLM-Wiki-second-brain.md)
- [Hermes-LLM-Wiki-学习笔记](2026-04-18-Hermes-LLM-Wiki-学习笔记.md)
- [LLM推理优化前沿技术2026](2026-04-28-LLM推理优化前沿技术2026.md)
- [LLM-Agent驱动量化交易系统前沿学习](2026-04-29-LLM-Agent驱动量化交易系统前沿学习.md)
- [边缘AI与On-Device-LLM前沿学习](2026-04-30-边缘AI与On-Device-LLM前沿学习.md)
- [deepseek-agent-ecosystem](2026-05-01-deepseek-agent-ecosystem.md)
- [LLM对齐训练范式RLHF-DPO-GRPO-DAPO](2026-05-04-LLM对齐训练范式RLHF-DPO-GRPO-DAPO.md)
- [开源AI模型2025-DeepSeek-Qwen新格局](2026-05-05-开源AI模型2025-DeepSeek-Qwen新格局.md)
- [PageIndex-无向量推理式RAG](2026-05-07-PageIndex-无向量推理式RAG.md)
- [大模型量化技术全景-GGUF-GPTQ-AWQ-FP8-BitNet](2026-05-07-大模型量化技术全景-GGUF-GPTQ-AWQ-FP8-BitNet.md)
- [推理加速深度解析-投机解码-KVCache-连续批处理](2026-05-08-推理加速深度解析-投机解码-KVCache-连续批处理.md)
- [LLM知识蒸馏技术全景](2026-05-09-LLM知识蒸馏技术全景.md)
- [DeepSeek-V4-开源模型新格局](2026-05-10-DeepSeek-V4-开源模型新格局.md)
- [蒸馏量化联合策略-QAD-LBLLM-CapacityGap](2026-05-10-蒸馏量化联合策略-QAD-LBLLM-CapacityGap.md)
- [5月AI模型大战-GPT55-DeepSeekV4](2026-05-11-5月AI模型大战-GPT55-DeepSeekV4.md)
- [AI趋势2026-推理时计算与反思Agent](2026-05-11-AI趋势2026-推理时计算与反思Agent.md)
- [LLM冲击下PINN应用变化与发展](2026-05-11-LLM冲击下PINN应用变化与发展.md)
- [MoE蒸馏与压缩-专家路由迁移-稀疏结构处理](2026-05-11-MoE蒸馏与压缩-专家路由迁移-稀疏结构处理.md)
- [JAX-NVIDIA-GPU-微调Llama3.1实战方案](2026-05-15-JAX-NVIDIA-GPU-微调Llama3.1实战方案.md)
- [LoRA高效微调前沿技术全景](2026-05-17-LoRA高效微调前沿技术全景.md)
- [SGLang高性能LLM推理框架深度分析](2026-05-17-SGLang高性能LLM推理框架深度分析.md)
- [Agent元认知-LLM不确定性感知](2026-05-18-Agent元认知-LLM不确定性感知.md)
- [MoE模型LoRA微调最佳实践](2026-05-18-MoE模型LoRA微调最佳实践.md)
- [蒸馏量化RL三联流水线-后训练范式统一](2026-05-19-蒸馏量化RL三联流水线-后训练范式统一.md)
- [AutoSearch 自主训练任务](AutoSearch 自主训练任务.md)
- [2025年5月AI大爆发-Claude4-Qwen3-DeepSeek-R1](explore/2026-05-09-2025年5月AI大爆发-Claude4-Qwen3-DeepSeek-R1.md)
- [开源AI春季爆发-模型推理Agent](explore/2026-05-09-开源AI春季爆发-模型推理Agent.md)
- [LLM推理优化-MoE量化加速全景](explore/2026-05-16-LLM推理优化-MoE量化加速全景.md)
- [LLM推理优化技术](explore/2026-05-16-LLM推理优化技术.md)
- [llm-inference-opt-incremental2](explore/2026-05-18-llm-inference-opt-incremental2.md)
- [llm-inference-opt-update](explore/2026-05-18-llm-inference-opt-update.md)
- [llm-self-prompt-optimization](explore/2026-05-18-llm-self-prompt-optimization.md)
- [MoE-稀疏激活微调工程实践](explore/2026-05-19-MoE-稀疏激活微调工程实践.md)
- [SGLang-vs-vLLM-推理引擎对比](explore/2026-05-19-SGLang-vs-vLLM-推理引擎对比.md)
- [llm_wiki分析与Skill进化](explore/2026-05-20-llm_wiki分析与Skill进化.md)
- [llm-inference-opt-2026-05-17](explore/llm-inference-opt-2026-05-17.md)
- [llm-inference-opt-incremental-20260517](explore/llm-inference-opt-incremental-20260517.md)
- [llm-pid-tuner](llm-pid-tuner.md)
- [分布式训练技术全景-FSDP-DeepSpeed-Megatron](orphan/2026-05-05-分布式训练技术全景-FSDP-DeepSpeed-Megatron.md)
- [表达清晰的5个训练](orphan/2026-05-16-表达清晰的5个训练.md)
- [tinyedge-lora](tinyedge-lora.md)
- [前瞻性问题-AI垂域LLM载具设计](前瞻性问题-AI垂域LLM载具设计.md)
