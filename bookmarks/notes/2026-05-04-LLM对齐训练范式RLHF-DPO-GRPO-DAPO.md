# LLM 对齐训练范式全景：从 RLHF 到 GRPO/DAPO/RLVR

> 📅 2026-05-04 | 夜间自学习 | 深度 L3
> 🏷️ #RLHF #DPO #GRPO #DAPO #RLVR #对齐训练 #后训练 #DeepSeek #强化学习

---

## 一、核心发现

### 发现1：后训练范式已从「4模型RLHF」进化到「1模型GRPO」

从 2022 年 RLHF 需要同时维护 4 个神经网络（Actor/Critic/Reference/Reward Model），到 2026 年 GRPO 只需 1 个 policy model + 规则验证器，训练成本降低约 60%，效果反而提升了 20 个百分点。

**架构演进路线**：
- **RLHF/PPO**（2022）：Actor + Critic + Reference + Reward Model = 4 模型
- **DPO**（2023）：Policy + Reference = 2 模型，消除 Reward Model 和 Critic
- **GRPO**（2024，DeepSeekMath）：Policy + Reference = 2 模型，用组内统计替代 Critic
- **RLVR**（2025，DeepSeek-R1）：Policy + 规则验证器 = 1 模型（无 Reference 也无 Reward Model）

**关键洞察**：GRPO 的核心创新在于用「组内相对优势」替代「Critic 预测价值」，这是一个 Z-score 标准化过程——对同一个 question 采样 G 个输出，计算每个输出的 reward，然后用 `(r_i - mean(r)) / std(r)` 得到 advantage。不需要训练额外的 value network。

### 发现2：GRPO 的数学本质——组相对策略优化

**GRPO 目标函数**：

```
J_GRPO(θ) = E_{q,{o_i}}[1/G * Σ_{i=1}^{G} 1/|o_i| * Σ_{t=1}^{|o_i|} (
    min(r_{i,t}(θ) * A_i, clip(r_{i,t}(θ), 1-ε, 1+ε) * A_i)
    - β * D_KL(π_θ || π_ref)
)]
```

其中：
- `r_{i,t}(θ) = π_θ(o_{i,t}|q,o_{i,<t}) / π_{θ_old}(o_{i,t}|q,o_{i,<t})` 是重要性采样比率
- `A_i = (r_i - mean(r_1,...,r_G)) / std(r_1,...,r_G)` 是组内标准化优势（Z-score）
- `β * D_KL` 是 KL 散度惩罚，防止偏离参考策略太远
- `ε` 是 PPO 风格的裁剪范围

**与 PPO 的关键区别**：
1. **无 Critic**：PPO 用 Value Network 预测 baseline，GRPO 用组内均值
2. **组内标准化**：A_i 不是绝对优势，而是相对同组的优势
3. **Token 级求和**：对每个 token 的概率比进行裁剪更新

### 发现3：DAPO 在 GRPO 基础上的关键改进

**DAPO（Decoupled Clip and Dynamic sAmpling Policy Optimization）** 针对 GRPO 的三个问题：

1. **非对称裁剪**：GRPO 用 `(1-ε, 1+ε)` 对称裁剪，DAPO 改为 `(1-ε_low, 1+ε_high)` 非对称裁剪，对负优势样本允许更大的更新幅度
2. **动态采样**：GRPO 保留所有 G 个样本（包括 reward 全相同的无效组），DAPO 过滤掉全正确/全错误的组，只保留有信息量的样本
3. **序列级归一化**：GRPO 按 `1/|o_i|` 加权每个 token，DAPO 改为 `1/Σ|o_i|` 全局归一化，减少长度偏差

**DAPO 目标函数**：

```
J_DAPO(θ) = E_{q,{o_i}}[1/Σ|o_i| * Σ_i Σ_t min(
    r_{i,t}(θ) * A_i,
    clip(r_{i,t}(θ), 1-ε_low, 1+ε_high) * A_i
)]
```

注意 DAPO 去掉了 KL 惩罚项，进一步简化。

### 发现4：GRPO 与 DPO 的隐含等价关系——"Your GRPO Is Secretly DPO"

论文《It Takes Two: Your GRPO Is Secretly DPO》（OpenReview 2025）揭示了重要发现：

- 当 GRPO 的组大小 G=2 时，其目标函数**数学等价于 DPO**
- GRPO 本质上是 DPO 从「一对比较」到「组内多路比较」的泛化
- 这意味着 DPO 的很多理论分析可以直接迁移到 GRPO

**实战基准对比**（来自 arXiv:2512.22631）：
- GRPO 在大模型（7B+）上表现更优，推理类任务提升显著
- DPO 在小模型（1.5B-3B）上更稳定，跨任务一致性更好
- 最佳实践：先用 DPO 做对齐，再用 GRPO 做推理强化

### 发现5：2026 年后训练前沿——RLVR、λ-GRPO、Training-Free GRPO

**RLVR（Reinforcement Learning with Verifiable Rewards）**：
- DeepSeek-R1 的核心范式：用规则验证器（代码执行、数学验算）替代 Reward Model
- 在可验证任务上（数学/编程/逻辑推理）效果惊人
- 局限：开放性生成任务（创意写作、对话）缺乏可定义的验证器

**λ-GRPO（ICLR 2026 Under Review）**：
- 解决 GRPO 的长度偏差问题：同一个 A_i 均匀分配给所有 token，导致模型偏好生成长输出
- 引入可学习参数 λ 控制Token级权重：长输出的每个token权重更低
- 在 Qwen2.5 的 1.5B/3B/7B 上，比 GRPO 分别提升 +1.9%/+1.0%/+1.7%
- 统一了 GRPO/DAPO/Dr.GRPO 等变体

**Training-Free GRPO（ICLR 2026）**：
- 不更新模型参数！用冻结的 LLM + 可变的经验上下文（experiential context）来优化
- 将优化从参数空间转移到上下文空间
- 在数学推理和 Web 搜索任务上建立了「性能-成本」新 Pareto 前沿
- 对 Agent 场景特别有意义：可以动态调整 prompt/context 来优化策略

### 发现6：生产级后训练流水线（2026 最佳实践）

来自 Zylos 等生产系统的经验，当前最佳三阶段流水线：

```
Stage 1: SFT（冷启动）
  ↓ 格式化工具调用、基础指令遵循
Stage 2: DPO/SimPO（对齐）
  ↓ 偏好学习、人类价值观对齐
Stage 3: GRPO/DAPO（推理强化）
  ↓ 可验证任务上的 RL 训练
  ↓ 输出：部署就绪的模型
```

**关键技术选择**：
- RL 框架：verl（字节）、OpenRLHF、Meituan DORA
- 同步 RL 在长序列 Agent 任务中会崩，需要异步 rollout
- Prompt Augmentation（arXiv:2602.03190）可以提升 GRPO 的 rollout 多样性

---

## 二、技术原理解析

### 2.1 从策略梯度到 GRPO 的完整推导链

**第一性原理：策略梯度定理**

```
∇_θ J(θ) = E_{τ~π_θ}[∇_θ log π_θ(τ) * R(τ)]
```

问题：方差太大。

**改进1：REINFORCE with Baseline**
```
∇_θ J(θ) = E[∇_θ log π_θ(τ) * (R(τ) - b)]
```
用 baseline b 降低方差，但需要一个准确的价值函数。

**改进2：PPO（Proximal Policy Optimization）**
```
L_PPO = E[min(ratio * A, clip(ratio, 1-ε, 1+ε) * A)]
```
裁剪防止过大更新，但需要 Critic 网络估计 A（Advantage = R - V(s)）。

**改进3：GRPO**
```
A_i = (r_i - mean(group_rewards)) / std(group_rewards)
```
用组内统计替代 Critic，本质上是用「同伴对比」来定义什么是「好」。这是一个非常优雅的设计：
- 不需要额外的价值网络训练
- 组内自动归一化，不需要全局 reward scale 调参
- 隐含了「相对排序」信息，比绝对分数更鲁棒

### 2.2 DPO 的隐式奖励机制

DPO 的核心洞察：RLHF 的最优策略可以用隐式奖励函数表示。

```
π*(y|x) ∝ π_ref(y|x) * exp(r(x,y)/β)
```

DPO 目标：
```
L_DPO = -E[log σ(β * log(π_θ(y_w|x)/π_ref(y_w|x)) - β * log(π_θ(y_l|x)/π_ref(y_l|x)))]
```

其中 y_w > y_l 是偏好对。本质上是让模型直接学习「好输出比坏输出的概率高多少」。

**DPO vs GRPO 的关键区别**：
| 维度 | DPO | GRPO |
|------|-----|------|
| 训练数据 | 离线偏好对 (y_w, y_l) | 在线生成 + 规则验证 |
| 奖励来源 | 人类标注 | 程序验证器 |
| 模型数量 | 2（policy + ref） | 2（policy + ref），但 ref 可去 |
| 是否需要采样 | 否（离线） | 是（在线 G 个样本） |
| 长处 | 对齐人类偏好 | 推理能力强化 |
| 短处 | 依赖标注质量 | 需要可验证的任务 |

### 2.3 GRPO 训练的工程细节

**关键超参数**：
- **组大小 G**：通常 8-16，越大 advantage 估计越准但计算成本越高
- **KL 惩罚 β**：0.01-0.1，太小模型会 drift，太大学不动
- **裁剪 ε**：0.2（标准 PPO 值）
- **学习率**：通常 1e-6 到 5e-7，比 SFT 小一个数量级

**训练流程**：
1. 对每个 question q，从 π_θ_old 采样 G 个 completion
2. 用验证器给每个 completion 打分（0/1 或连续分数）
3. 计算组内 Z-score advantage
4. 用 PPO 风格裁剪目标更新 π_θ
5. 每隔 N 步更新 π_θ_old（on-policy 的保证）

**显存管理**：
- GRPO 不需要 Critic，省约 50% 显存
- 但需要存 G 个样本的 log_probs，G=16 时开销不小
- 实战建议：用 Gradient Checkpointing + LoRA 做 GRPO

---

## 三、知识关联

- [2026-04-28-LLM推理优化前沿技术2026](2026-04-28-LLM推理优化前沿技术2026.md) → 推理优化关注的是部署后的加速，本篇关注训练阶段的优化。两者共同决定最终用户体验。量化（GPTQ/AWQ）通常在 GRPO 训练后进行。
- [2026-05-01-deepseek-agent-ecosystem](2026-05-01-deepseek-agent-ecosystem.md) → DeepSeek 生态的 Agent 工具（Deep Code、Reasonix）背后正是 GRPO 训练的模型。DeepSeek-R1 的推理能力源于 RLVR + GRPO。
- [2026-05-01-AI-Agent记忆架构前沿学习](2026-05-01-AI-Agent记忆架构前沿学习.md) → Agent 的记忆系统（长期记忆、RAG 增强）与 GRPO 的在线采样有交叉：Agent 在推理时的轨迹可以作为 GRPO 的训练数据。
- [2026-05-03-AI-Agent-Protocol-Ecosystem-2026-学习](2026-05-03-AI-Agent-Protocol-Ecosystem-2026-学习.md) → Agent 协议（A2A/MCP）定义了工具调用规范，而 GRPO 训练的 Agent 需要遵循这些协议。Tool-using Agent 的后训练流水线是 2026 年的热点。
- [2026-04-05-Google-Gemma4-open-source](2026-04-05-Google-Gemma4-open-source.md) → Gemma 等开源模型通常经过 DPO 对齐，了解 GRPO 可以帮助理解为什么某些开源模型推理能力更强。
- obs_notes: [[大模型核心术语]] → 已有 RLHF/DPO/PEFT 的基础概念定义，本篇补充了数学推导和工程细节
- obs_notes: [[大模型核心术语]] 中的「人类反馈强化学习 (RLHF)」「知识蒸馏」条目 → 本篇是这些概念的深度展开

---

## 四、Actionable Insights

1. **Skill 更新**：`grpo-rl-training` skill 应更新，加入 DAPO/RLVR/λ-GRPO 的最新内容
2. **量化交易模型微调**：如果用 Kronos 金融模型做推理任务，GRPO + 规则验证器（回测收益作为 reward）可能比 DPO 更有效
3. **Agent 自进化**：Hermes 的自进化机制可以借鉴 Training-Free GRPO 的思路——不修改模型参数，通过优化上下文/prompt 来改进策略
4. **开放问题**：对于 Hermes 的 Skill 自动生成/优化，可以考虑用 DPO 做偏好对齐（人类评估 Skill 质量），用 GRPO 做推理强化（可验证任务成功率）
5. **Cron Job 优化**：当前 nightly-auto-learn 的学习结果用 DPO 思路——选最好的笔记存档。可以引入 GRPO 思路——生成多个版本，组内比较选最优

---

## 五、待深入的问题清单

1. **GRPO 在非推理任务上的适用性**：创意写作、多轮对话等没有明确验证器的任务，GRPO 如何适配？
2. **多目标优化**：GDPO（Group reward-Decoupled Normalization Policy Optimization）如何处理多个冲突的 reward signal？
3. **GRPO + MoE**：MoE 架构下 GRPO 的路由策略如何优化？专家选择是否也需要 RL？
4. **分布式 GRPO 训练**：verl/OpenRLHF 框架在大规模 GRPO 训练中的工程优化细节
5. **Training-Free GRPO 的上下文优化**：具体用什么形式的 experiential context？few-shot examples？retrieved passages？
6. **ShapE-GRPO**（arXiv:2603.29871）：用 Shapley 值做奖励分配的多候选训练，如何理解？
7. **GIFT**（arXiv:2510.23868）：将 GRPO 与 DPO 隐式融合，收敛更快、泛化更好，具体机制？

---

## 六、参考来源

1. DeepSeekMath: GRPO 原始论文（Shao et al., 2024）
2. DeepSeek-R1: RLVR 范式的规模化验证（Guo et al., 2025）
3. λ-GRPO: Unifying the GRPO Frameworks with Learnable Token Preferences（arXiv:2510.06870, ICLR 2026 Under Review）
4. Training-Free GRPO（arXiv:2510.08191, ICLR 2026）
5. It Takes Two: Your GRPO Is Secretly DPO（OpenReview 2025）
6. GIFT: Group-relative Implicit Fine Tuning（arXiv:2510.23868）
7. Prompt Augmentation Scales up GRPO Training（arXiv:2602.03190）
8. Cameron Wolfe: GRPO Deep (Learning) Focus 博客
9. HuggingFace LLM Course Chapter 12: GRPO 详解
10. Stanford CS224N 2026 Lecture 8: Post-training

## 相关笔记
- [Hermes-LLM-Wiki-学习笔记](2026-04-18-Hermes-LLM-Wiki-学习笔记.md)
- [MCP协议与Agentic-LLM-2025趋势](2026-04-23-MCP协议与Agentic-LLM-2025趋势.md)
- [垂域LLM指导航空结构设计](2026-04-27-垂域LLM指导航空结构设计.md)
- [LLM推理优化前沿技术2026](2026-04-28-LLM推理优化前沿技术2026.md)
- [LLM-Agent驱动量化交易系统前沿学习](2026-04-29-LLM-Agent驱动量化交易系统前沿学习.md)
- [边缘AI与On-Device-LLM前沿学习](2026-04-30-边缘AI与On-Device-LLM前沿学习.md)
- [deepseek-agent-ecosystem](2026-05-01-deepseek-agent-ecosystem.md)
- [Awesome-LLM-Apps-109K星应用模板库](2026-05-05-Awesome-LLM-Apps-109K星应用模板库.md)
- [开源AI模型2025-DeepSeek-Qwen新格局](2026-05-05-开源AI模型2025-DeepSeek-Qwen新格局.md)
- [PageIndex-无向量推理式RAG](2026-05-07-PageIndex-无向量推理式RAG.md)
- [大模型量化技术全景-GGUF-GPTQ-AWQ-FP8-BitNet](2026-05-07-大模型量化技术全景-GGUF-GPTQ-AWQ-FP8-BitNet.md)
- [ollama-vllm-llamacpp-deploy-comparison](2026-05-08-ollama-vllm-llamacpp-deploy-comparison.md)
- [推理加速深度解析-投机解码-KVCache-连续批处理](2026-05-08-推理加速深度解析-投机解码-KVCache-连续批处理.md)
- [LLM知识蒸馏技术全景](2026-05-09-LLM知识蒸馏技术全景.md)
- [DeepSeek-V4-开源模型新格局](2026-05-10-DeepSeek-V4-开源模型新格局.md)
- [蒸馏量化联合策略-QAD-LBLLM-CapacityGap](2026-05-10-蒸馏量化联合策略-QAD-LBLLM-CapacityGap.md)
- [5月AI模型大战-GPT55-DeepSeekV4](2026-05-11-5月AI模型大战-GPT55-DeepSeekV4.md)
- [AI趋势2026-推理时计算与反思Agent](2026-05-11-AI趋势2026-推理时计算与反思Agent.md)
- [LLM冲击下PINN应用变化与发展](2026-05-11-LLM冲击下PINN应用变化与发展.md)
- [MoE蒸馏与压缩-专家路由迁移-稀疏结构处理](2026-05-11-MoE蒸馏与压缩-专家路由迁移-稀疏结构处理.md)
- [MoE投机解码-稀疏激活与推理加速深度解析](2026-05-13-MoE投机解码-稀疏激活与推理加速深度解析.md)
- [从零训练GPT完整指南](2026-05-13-从零训练GPT完整指南.md)
- [JAX-NVIDIA-GPU-微调Llama3.1实战方案](2026-05-15-JAX-NVIDIA-GPU-微调Llama3.1实战方案.md)
- [序列并行与上下文并行-长上下文训练的第四维并行](2026-05-15-序列并行与上下文并行-长上下文训练的第四维并行.md)
- [LoRA高效微调前沿技术全景](2026-05-17-LoRA高效微调前沿技术全景.md)
- [[2026-05-18-Fine-Tuning理论与实践-从理论基础到2026全景]] (关键词: Fine-Tuning, 全景综述)
- [20260513-llm-wiki-obsidian-gbrain-知识自组织与自进化](20260513-llm-wiki-obsidian-gbrain-知识自组织与自进化.md)
- [AutoSearch 自主训练任务](AutoSearch 自主训练任务.md)
- [2025年5月AI大爆发-Claude4-Qwen3-DeepSeek-R1](explore/2026-05-09-2025年5月AI大爆发-Claude4-Qwen3-DeepSeek-R1.md)
- [开源AI春季爆发-模型推理Agent](explore/2026-05-09-开源AI春季爆发-模型推理Agent.md)
- [2026年5月AI模型大战-GPT5.5-Grok4.3-DeepSeekV4](explore/2026-05-13-2026年5月AI模型大战-GPT5.5-Grok4.3-DeepSeekV4.md)
- [开源AI模型新格局-DeepSeek冲击波](explore/2026-05-13-开源AI模型新格局-DeepSeek冲击波.md)
- [LLM推理优化-MoE量化加速全景](explore/2026-05-16-LLM推理优化-MoE量化加速全景.md)
- [LLM推理优化技术](explore/2026-05-16-LLM推理优化技术.md)
- [llm-pid-tuner](llm-pid-tuner.md)
- [llm-wiki-gbrain-agent-evolution_33aa818c](llm-wiki-gbrain-agent-evolution_33aa818c.md)
- [分布式训练技术全景-FSDP-DeepSpeed-Megatron](orphan/2026-05-05-分布式训练技术全景-FSDP-DeepSpeed-Megatron.md)
- [MoE混合专家模型-路由策略-负载均衡-训练稳定性](orphan/2026-05-06-MoE混合专家模型-路由策略-负载均衡-训练稳定性.md)
- [多目标GRPO-GDPO-AW-GRPO-Reward融合与冲突消解](orphan/2026-05-14-多目标GRPO-GDPO-AW-GRPO-Reward融合与冲突消解.md)
- [MegatronCore模块化重构与MoE训练前沿](orphan/2026-05-16-MegatronCore模块化重构与MoE训练前沿.md)
- [表达清晰的5个训练](orphan/2026-05-16-表达清晰的5个训练.md)
- [tinyedge-lora](tinyedge-lora.md)
- [前瞻性问题-AI垂域LLM载具设计](前瞻性问题-AI垂域LLM载具设计.md)
