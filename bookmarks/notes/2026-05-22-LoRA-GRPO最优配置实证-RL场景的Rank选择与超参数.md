# LoRA + GRPO 最优配置实证 — RL 场景的 Rank 选择与超参数体系

> 夜学深度笔记 | 覆盖 Schulman "LoRA Without Regret" RL 实验全貌 + 首篇 GRPO 场景自适应 Rank 分配失败实证（arXiv 2605.07366）+ veRL/Unsloth/Rank-GRPO 工程实践
> 日期：2026-05-22

---

## 核心发现

### 1. Schulman 证实：RL 场景下 r=1 LoRA 即可匹配 FullFT

John Schulman（OpenAI 联创，现 Thinking Machines 首席科学家）在 "LoRA Without Regret" 中通过大量实验证明：

- **rank-1 LoRA 在 GRPO/RLHF 等策略梯度算法中完全匹配 FullFT**，因为每轮训练仅需 O(1) 比特信息（scalar advantage function）
- Llama-3.1-8B 的 rank-1 LoRA 有 3M 参数，而 MATH 数据集 10K 问题 × 32 样本 = 320K 比特信息需求，容量绰绰有余
- DeepSeek-R1-Zero 训练 5.3M episodes，信息量 < rank-1 LoRA 参数量，理论上可用 LoRA 复现
- **LoRA 有更宽的最优学习率范围**（LR vs reward 曲线更平坦），RL 场景下对 LR 选择更宽容
- 在 Qwen3-8b-base + DeepMath 数据集上验证：rank 1/4/16/64/256 和 FullFT 学习曲线几乎完全重合

### 2. 自适应 Rank 分配在 GRPO 下彻底失败（arXiv 2605.07366）

Yash Sawant（2026.05，提交 CoLoRAI@ICML 2026）首次实证了 SFT 时代有效的自适应 Rank 策略（AdaLoRA/GoRA/IGU-LoRA）在 GRPO 下不仅无效，反而有害：

- **Proportional 分配比 Uniform 低 4.5 个点**（70.0% vs 74.5% GSM8K）
- GRPO 梯度景观极平坦：最大/最小层梯度比仅 2.17×（SFT 文献报告 >10×）
- 前 30% 层仅承载 36% 梯度信号（SFT 下 >80%），所有层都在工作
- **梯度放大效应**：非均匀分配将 2.17× 差距扩大到 3.00×，形成正反馈循环
- **关键洞察**：Rank 决定梯度重要性（相关性 0.972），而非反过来。移动 rank → 梯度重要性跟着移动
- **结论**：GRPO 下统一分配是最优且最便宜的策略

### 3. 最优学习率是 FullFT 的 10 倍

Schulman 在 14 个 Llama/Qwen 模型上验证：

- **LoRA 最优 LR ≈ 10 × FullFT 最优 LR**（拟合乘数 9.8）
- 短训练（<100 步）：乘数上升到 ~15×
- 这个比例在 SFT 和 RL 场景下均成立
- 标准参数化下（α=32, A 高斯初始化 1/√d_in, B=0），最优 LR 与 rank 近似无关
- 公式拟合：LR = M_LoRA × (2000/hidden_size)^(model_pow)

### 4. 目标层选择：MLP + Attention 缺一不可

- MLP-only LoRA ≈ MLP+Attention LoRA（两者差距微小）
- **Attention-only LoRA 严重落后**，即使参数量匹配（attn rank=256 < mlp rank=128）
- MLP/MoE 层是 LoRA 的主要贡献者，Attention 层叠加效果微弱
- 结论：覆盖所有主要线性层（q/k/v/o/gate/up/down）是最优策略

### 5. LoRA 对大 Batch 更敏感

- LoRA 在大 batch 下性能退化比 FullFT 更严重
- 这种退化与 rank 无关，是 BA 矩阵乘积参数化的固有性质
- 两者都在较小 batch 下取得最佳 loss，实际影响有限

---

## 技术原理解析

### 为什么 RL 只需 r=1？信息论论证

Schulman 给出了精妙的信息论解释：

1. **SFT 信息量**：每个 token 提供 O(1) 比特，训练 10 亿 token = 10 亿比特
2. **RL 信息量**：每个 episode 仅提供 O(1) 比特（一个 scalar advantage 值），即使生成数千 token
3. **信息密度差距**：RL 每个训练 token 吸收的信息量是 SFT 的 ~1/1000
4. **容量计算**：rank-1 LoRA 的 3M 参数 >> MATH 320K 比特需求，容量富裕 10×

这意味着在 RL 训练中，LoRA 的容量瓶颈几乎不可能被触及。

### 为什么自适应 Rank 在 GRPO 下失败？两个机制

**机制一：梯度景观平坦**

SFT 下不同层梯度幅度差异巨大（>10×），某些层确实"空闲"。但 GRPO 的 group-centered advantage 机制使梯度均匀分布到所有层——每层都在参与策略优化，没有可以安全裁剪的"冗余"层。

**机制二：Rank-Gradient 正反馈循环**

实验揭示了一个反直觉的因果关系：
- 分配高 rank → 层获得更多梯度信号（变得"更重要"）
- 分配低 rank → 层梯度信号被抑制（变得"更不重要"）
- 相关性 0.972（随机分配也达 0.946）

这意味着 profile → allocate 范式在 RL 下是自我实现的预言：你测量到的"重要性"只是你分配的 rank 的反映，而非层的内在属性。

### 4→2 超参数简化

LoRA 有 4 个潜在超参数：α（缩放因子）、LR_A（A 矩阵学习率）、LR_B（B 矩阵学习率）、init_A（A 初始化幅度）。Schulman 证明在 Adam 优化下存在二维不变性：

**不变变换**（p, q > 0）：
- α → α/(pq)
- init_A → p·init_A
- LR_A → p·LR_A
- LR_B → q·LR_B

4 维空间坍缩为 2 维，只需关注：
1. **α·init_A·LR_B**：初始更新幅度（学习曲线初始斜率）
2. **init_A/LR_A**：A 矩阵偏离初始状态的步数（时间尺度参数）

这意味着：
- LoRA+（不同 A/B 学习率）等价于调整时间尺度参数
- Unsloth 建议 α=2r 等价于增大 init_A/LR_A
- 标准 PEFT 默认值（α=32, 统一 LR, 高斯 init）已经接近最优

---

## 工程实践配置参考

### veRL 框架 GRPO + LoRA 配置

```
actor_rollout_ref.model.lora_rank = 32       # 统一分配
actor_rollout_ref.model.lora_alpha = 32       # 标准值
actor_rollout_ref.model.target_modules = "all-linear"  # 所有线性层
actor_rollout_ref.rollout.load_format = "safetensors"   # 必须设置
actor_rollout_ref.model.use_shm = True         # 70B+ 模型推荐
actor_rollout_ref.rollout.layered_summon = True # 70B+ 或显存紧张时
```

### Unsloth GRPO 推荐

- **LR**：RL 场景用比 SFT 更低的学习率（SFT 推荐 2e-4，RL 推荐 1e-5 ~ 5e-5）
- **Rank**：16 或 32 起步（RL 下 rank-1 理论可行但实践中 16/32 更稳定）
- **Alpha**：= rank 或 2× rank
- **Target**：所有 7 个线性层
- **rsLoRA**：可用 alpha/sqrt(rank) 缩放提升高 rank 稳定性

### Rank-GRPO（Netflix, ICLR 2026）实战配置

```
lr = 1e-6                    # GRPO 用极低学习率
kl_beta = 1e-3               # KL 惩罚系数
adam_beta1 = 0.9
adam_beta2 = 0.99
per_device_batch = 16
gradient_accumulation = 6     # 有效 batch = 96
num_generations = 8           # K=8 per prompt
max_prompt_length = 2048
max_completion_length = 1024
reward_func = exp_inf         # 推荐系统专用 reward
vllm_gpu_memory = 0.5
vllm_tensor_parallel = 4
```

---

## 知识关联

- [[2026-05-17-LoRA高效微调前沿技术全景]] → 本次从 RL 场景补充了 Schulman 的 r=1 RL 理论、4→2 超参数简化、最优 LR 10× 比例。原笔记记录了 SFT 下的 17 种变体，本次聚焦 RL 场景下的特异性
- [[2026-05-04-LLM对齐训练范式RLHF-DPO-GRPO-DAPO]] → 原笔记提到"Gradient Checkpointing + LoRA 做 GRPO"的工程建议，本次用 Schulman 理论论证了为什么 LoRA 在 RL 下有效（信息论），以及为什么 rank 选择与 SFT 不同
- [[2026-05-18-MoE模型LoRA微调最佳实践]] → Schulman 明确提到 MoE 模型的 LoRA 实验（Qwen3-30B-A3B），MoE 层与 Dense 层遵循相同结论。GoAT 的 SVD 分段初始化在 RL 场景下可能不需要（r=1 足够）
- [[2026-05-19-蒸馏量化RL三联流水线-后训练范式统一]] → 三联流水线的 RL 阶段可用极低 rank LoRA（r=1 理论可行），大幅降低 Teacher RL → Dense Bridge 的训练成本
- [[2026-05-14-多目标GRPO-GDPO-ShapE-GRPO]] → 多目标 GRPO 的 reward 冲突消解与 LoRA rank 选择独立。GDPO 在 LoRA 上无特殊要求
- [[2026-05-08-LLM推理优化前沿技术2026]] → LoRA 适配器的小体积特性使得 RL 训练后的部署更高效（multi-tenant serving via vLLM/SGLang）
- obs_notes: RLHF/DPO/PEFT 基础概念 → 本次补充了 RL 场景下 PEFT 的理论论证和实证数据

---

## Actionable Insights

1. **GRPO 训练直接用 Uniform rank=16，别折腾自适应分配** — SFT 的 AdaLoRA/GoRA 在 GRPO 下会掉 4.5 点。省钱省力效果更好
2. **LoRA LR 设为 FullFT LR 的 10 倍** — 14 个模型验证的比例，短训练用 15 倍
3. **覆盖所有线性层** — Attention-only LoRA 严重不足，必须包含 MLP/MoE 层
4. **RL 训练不需要高 rank** — 理论上 r=1 足够，实践中 r=16~32 给予足够余量
5. **对 Hermes 的启示**：如果要给 Hermes Agent 加 RL 自进化能力（ARPO 工具调用训练），用 LoRA r=16 + GRPO 即可在单卡上完成
6. **veRL 是最成熟的 GRPO+LoRA 框架** — 支持 FSDP/FSDP2 + vLLM/SGLang，可直接用于我们的训练实验

---

## 待深入问题

1. GRPO + DoRA 方向-幅度分解在 RL 下是否有优势？Schulman 未测试
2. LoRA + GRPO 在非推理任务（开放式生成、代码、多语言）上的 rank 需求是否仍然极低？
3. 自适应 Rank 的在线版本（AdaLoRA 式动态调整）能否避免静态分配的放大效应？
4. GRPO + LoRA + 量化（QLoRA）在 RL 训练中的精度影响——SFT 下 QLoRA ≈ LoRA，RL 下是否成立？
5. LoRA 合并（merge）后的 RL 训练是否可以迭代进行？即 LoRA RL → merge → LoRA RL → merge
6. GRPO 的大 batch 退化与 sequence parallel 的交互——长序列训练下 LoRA 的 batch 敏感性
7. 多模态模型（VLM）的 RL 训练中 LoRA 配置是否遵循相同的 r=1 足够论断？

---

## 参考来源

1. **John Schulman**, "LoRA Without Regret", Thinking Machines Lab, 2025 — https://thinkingmachines.ai/blog/lora/
2. **Yash Sawant**, "Gradient-Based LoRA Rank Allocation Under GRPO: An Empirical Study", arXiv:2605.07366, 2026.05 — https://arxiv.org/abs/2605.07366
3. **Yash Sawant**, Blog: "Gradient-Based LoRA Rank Allocation Fails in GRPO" — https://yashsawant22.github.io/2026/05/08/lora-grpo-rank-allocation.html
4. **Yaochen Zhu et al.**, "Rank-GRPO: Training LLM-based Conversational Recommender Systems with RL", ICLR 2026, Netflix — https://github.com/yaochenzhu/Rank-GRPO
5. **veRL Documentation**, "RL(HF) algorithms with LoRA Support" — https://verl.readthedocs.io/en/latest/advance/ppo_lora.html
6. **Unsloth**, "LoRA fine-tuning Hyperparameters Guide" — https://unsloth.ai/docs/get-started/fine-tuning-llms-guide/lora-hyperparameters-guide
7. **ARENA**, "Chapter 2: Reinforcement Learning - GRPO LoRA" — https://learn.arena.education/chapter2_rl/04_rlhf/3-grpo-lora/

## 相关笔记
- [蒸馏量化RL三联流水线-后训练范式统一](2026-05-19-蒸馏量化RL三联流水线-后训练范式统一.md)
- [Active-Data-Selection-LLM训练动态数据选择前沿](2026-05-20-Active-Data-Selection-LLM训练动态数据选择前沿.md)
- [MLA多头潜在注意力-DeepSeek-KV缓存压缩与推理优化](2026-05-21-MLA多头潜在注意力-DeepSeek-KV缓存压缩与推理优化.md)
- [llm-finetune-dataflow-dataflex-pipeline](2026-05-21-llm-finetune-dataflow-dataflex-pipeline.md)
- [react-agent-llm-agentic-training-research](2026-05-21-react-agent-llm-agentic-training-research.md)
- [llm-inference-opt-incremental2](explore/2026-05-18-llm-inference-opt-incremental2.md)
- [llm-inference-opt-update](explore/2026-05-18-llm-inference-opt-update.md)
- [llm-self-prompt-optimization](explore/2026-05-18-llm-self-prompt-optimization.md)
- [MoE-稀疏激活微调工程实践](explore/2026-05-19-MoE-稀疏激活微调工程实践.md)
- [SGLang-vs-vLLM-推理引擎对比](explore/2026-05-19-SGLang-vs-vLLM-推理引擎对比.md)
- [llm_wiki分析与Skill进化](explore/2026-05-20-llm_wiki分析与Skill进化.md)
- [边缘AI推理优化-Jetson平台深度研究](explore/2026-05-21-边缘AI推理优化-Jetson平台深度研究.md)
- [llama-cpp预编译二进制与本地LLM推理](explore/2026-05-22-llama-cpp预编译二进制与本地LLM推理.md)
- [llm-inference-opt-2026-05-17](explore/llm-inference-opt-2026-05-17.md)
- [llm-inference-opt-deep-dive](explore/llm-inference-opt-deep-dive.md)
- [llm-inference-opt-incremental-20260517](explore/llm-inference-opt-incremental-20260517.md)

→ 相关：2026-10-19-五种LLM微调技术图解-LoRA家族PEFT变体谱系.md
