# VLM 强化学习训练：视觉编码器与 LoRA 配置前沿

> 夜学深度笔记 | 覆盖 VLM-R1/Vision-G1/CLGRPO/Vision-SR1/VoRA/LVR/Praxis-VLM/DeepVideo-R1 八大前沿方法 + 视觉编码器冻结/解冻决策 + LoRA 工程配置
> 日期：2026-05-24

---

## 核心发现

### 1. VLM 的 RL 训练存在「模态不对称」问题，视觉编码器需要特殊处理

VLM 在 RL 训练中面临纯 LLM 不存在的独特挑战：

- **视觉编码器的梯度信号密度远低于语言模型**：ViT 的参数只通过图像 token 接收梯度，而语言模型的参数通过所有 token 接收梯度。GRPO 的 group-centered advantage 在视觉模态上的信号效率更低
- **Reward Hacking 在视觉任务中更严重**：VLM-R1（arxiv 2504.07615）首次系统揭示 VLM 的 RL 训练中 reward hacking 的独特表现——目标检测任务中模型学会「作弊」通过生成高频 bbox 而非真正理解视觉内容
- **语言捷径（Language Shortcut）**：Vision-SR1（ICLR 2026）发现 VLM 在 RL 中倾向于绕过视觉理解、仅依赖文本先验（text prior），因为在纯文本推理上更容易获得高 reward
- **信息论推导**：Schulman 的 r=1 LoRA 信息论在 VLM 上需要修正——RL 的 O(1) bits/episode 论证假设所有参数都接收到相同的 advantage 信号，但 VLM 的视觉编码器接收的信号被视觉 token 占比稀释（通常 <10%）

### 2. 视觉编码器的冻结策略：主流做法是冻结 + LoRA

当前 VLM RL 训练的工程实践呈现清晰的模式：

| 方法 | 视觉编码器策略 | LoRA 配置 | 效果 |
|------|--------------|-----------|------|
| VLM-R1 | 冻结 ViT，仅训练 LLM LoRA | Qwen2-VL backbone, PEFT | SOTA on REC/OVD |
| Vision-G1 (AAAI) | 冻结 ViT，多轮 RL | Qwen2.5-VL-7B, influence-based 数据选择 | 46 数据集 13 维度泛化 |
| CLGRPO | 三阶段渐进式：SFT→CoT SFT→GRPO | Small VLM (Qwen2-VL-2B) | 增量训练策略 |
| Vision-SR1 (ICLR 2026) | 冻结 ViT，分解视觉/语言 reward | Qwen2-VL backbone | 自 reward，无外部视觉监督 |
| Praxis-VLM (NeurIPS 2025) | 纯文本 GRPO 训练 → 视觉迁移 | 文本驱动的 reasoning 迁移 | 跨模态泛化 |
| DeepVideo-R1 (NeurIPS 2025) | 冻结视觉编码器 | Reg-GRPO + 难度感知 | 视频 RL |
| VoRA | 无外部编码器，LoRA 即视觉 | rank-1024, 双向注意力, block-wise 蒸馏 | 消除 ViT 依赖 |
| FlexAI Blueprint | 冻结视觉层 | q_proj, v_proj LoRA | Qwen2.5-VL-3B |

**关键发现**：
- **几乎所有主流工作都冻结视觉编码器**，只在 LLM 部分应用 LoRA
- FlexAI 的 VLM GRPO 配置明确 `--lora_target_modules "q_proj" "v_proj"`，仅针对语言模型的注意力层
- Unsloth 的 VLM RL 支持可选训练视觉层（使用 transformers 推理时），但使用 vLLM 推理时视觉层不参与训练
- VoRA 是唯一例外：完全消除外部 ViT，用 LoRA rank-1024 直接在 LLM 内部编码视觉

### 3. Vision-SR1：视觉-语言推理分解（ICLR 2026 亮点）

Vision-SR1（arxiv 2508.19652）提出了解决 VLM RL 训练核心问题的优雅方案：

- **推理分解**：将 VLM 推理分为「视觉感知推理」和「语言推理」两个阶段
  - 模型先生成自包含的视觉描述（不回头看图像即可回答问题）
  - 然后联合优化视觉和语言推理
- **多 Reward 目标**：
  - 视觉描述的准确性 reward（是否充分描述了图像中的关键信息）
  - 最终答案的正确性 reward
  - 两个 reward 通过 multi-reward loss 联合优化
- **效果**：在不依赖外部视觉监督的情况下，显著减少视觉幻觉（hallucination）和语言捷径
- **与我们的知识关联**：这是 GDPO（多目标 GRPO）在 VLM 领域的直接应用，分维度 reward 标准化在视觉/语言模态间平衡

### 4. Praxis-VLM：文本驱动 RL 迁移到视觉（NeurIPS 2025）

Praxis-VLM（arxiv 2503.16965）揭示了一个反直觉的发现：

- VLM 将视觉场景替换为文本描述时，决策性能几乎没有下降
- **文本 GRPO 训练的 reasoning 能力可以零样本迁移到视觉推理**
- 这意味着可以先用纯文本场景做廉价的 RL 训练，再迁移到多模态推理
- **工程意义**：视觉编码器不需要参与 RL 训练——语言模型部分获得的 reasoning 策略足以迁移

### 5. VoRA：视觉即 LoRA，消除编码器依赖

VoRA（arxiv 2503.20680）是架构范式的根本性改变：

- **核心思想**：不使用外部 ViT 编码器，而是用 LoRA 层直接在 LLM 内部编码视觉能力
- **关键配置**：rank=1024（比标准 LoRA 大 16-64 倍），双向注意力掩码，block-wise 蒸馏
- **训练流程**：先用预训练 ViT 作为教师进行 block-wise 知识蒸馏到 LoRA 层
- **效果**：数据效率显著提升，在足够数据时匹配传统编码器架构
- **与 RL 的关联**：这种架构下 RL 训练的梯度可以直接流过 LoRA 视觉层，没有冻结编码器的梯度截断问题

---

## 技术原理解析

### VLM 架构下的 RL 信息流分析

标准 VLM（如 Qwen2-VL、LLaVA）架构包含三个组件：视觉编码器（ViT）→ 连接器（Projector/Adapter）→ 语言模型（LLM）。

在 GRPO RL 训练中，信息流如下：

1. **Forward Pass**：图像 → ViT（冻结）→ 视觉 token → LLM → 文本生成
2. **Reward 计算**：基于生成的文本（ bbox 坐标、答案文本等）
3. **Advantage 计算**：group 内归一化 reward
4. **梯度反传**：从 LLM 的文本输出端 → 反传到 LLM 参数 → 通过 LoRA 更新

**关键问题**：梯度在到达 ViT 时已经被截断（冻结），这意味着视觉编码器的表征能力在 RL 阶段不会改善。如果初始的视觉表征不够好，RL 无法修正这个问题。

### 冻结 vs 解冻视觉编码器的 Trade-off

**冻结的优势**：
- 训练稳定性好（视觉表征不被破坏）
- 显存需求低（不需要存储 ViT 的梯度）
- 与 vLLM 推理兼容性好
- 符合 Schulman 的信息论论证——RL 只需 O(1) bits/episode，视觉编码器的参数容量远超需求

**解冻的潜在好处**（实验验证尚少）：
- 视觉任务特化：在医疗/工业视觉等垂直领域，通用 ViT 的表征可能不够
- 视觉幻觉修正：RL 的 reward 信号可能帮助视觉编码器学会避免幻觉
- 与 QLoRA 的潜力：ViT 4-bit 量化 + LoRA 可以在低显存下解冻训练

### Latent Visual Reasoning（LVR）：突破文本推理的局限

LVR（arxiv 2509.24251，UC Davis）提出了全新范式：

1. 视觉编码器将图像投射到与语言模型共享的语义空间
2. 语言模型被训练生成 latent states 来重建关键视觉 token
3. 通过在视觉 embedding 空间做自回归推理（而非文本），实现「用视觉思考」
4. 适配 GRPO 到 latent reasoning：在 latent 空间做 RL，平衡视觉推理和文本生成

**核心洞察**：当前 VLM 的 CoT 推理本质上是语言推理（用文本描述视觉内容），LVR 使模型直接在视觉空间推理。这对 RL 训练的意义在于——reward 信号可以直接评估视觉推理质量，而非仅评估最终的文本答案。

---

## 工程实践配置

### Unsloth VLM RL 配置（推荐起步）

```
模型：Qwen3-VL-8B 或 Gemma-3-4B
LoRA rank：16-32（语言模型部分）
视觉编码器：默认冻结，Unsloth 推理模式下可选训练
LR：1e-5 ~ 5e-5
Target modules：q_proj, k_proj, v_proj, o_proj, gate_proj, up_proj, down_proj
Batch size：per_device = 4-8, gradient_accumulation = 4-8
vLLM 推理：fast_inference=True（1.5-2x 加速，90% VRAM 节省）
```

### veRL VLM LoRA 配置

```
actor_rollout_ref.model.lora.type = "vlm_lora"  # veRL 内置 VLM LoRA 类型
actor_rollout_ref.model.lora.merge = True  # 推理前 merge LoRA
actor_rollout_ref.rollout.layered_summon = True  # 70B+ 模型推荐
```

### FlexAI GRPO VLM 配置

```
模型：Qwen2.5-VL-3B-Instruct
LR：1e-5
LoRA targets：q_proj, v_proj（仅注意力层，保守配置）
Dtype：bfloat16
Max prompt：2048, Max completion：1024
DeepSpeed：ZeRO-3
vLLM：colocate 模式
```

### 关键工程发现

1. **Qwen2.5-VL RL 的 Quirk**：RL 训练中可能生成空图像占位符（需要用 vLLM 模式或 Unsloth 推理解决）
2. **vLLM 视觉层限制**：使用 vLLM 推理时视觉编码器不可训练，必须切换到 transformers 推理才能训练视觉层
3. **LoRA merge 时精度问题**：veRL 支持 merge LoRA 后传输到 vLLM（更快但有精度损失）或加载独立 adapter

---

## 知识关联

- [[2026-05-22-LoRA-GRPO最优配置实证-RL场景的Rank选择与超参数]] → Schulman 的 r=1 信息论论证在 VLM 上需要修正：视觉 token 占比低导致视觉编码器接收的 RL 信号被稀释。LoRA 配置需区分语言层和视觉连接器
- [[2026-05-23-QLoRA在RL训练中的精度影响-量化与强化学习深度解析]] → VLM 的视觉编码器是 QLoRA 的新应用场景：4-bit ViT + LoRA 可以在低显存下解冻视觉编码器做 RL。但 QeRL「量化噪声增强探索」在视觉 token 上是否有效尚未验证
- [[2026-05-18-MoE模型LoRA微调最佳实践]] → MoE-VLM（如 LLaVA-MoD）的 RL 训练需要同时考虑专家路由不均和视觉编码器冻结的双重约束
- [[2026-05-14-Active-Data-Selection-LLM训练动态数据选择前沿]] → Vision-G1 的 influence function 数据选择是 OPUS 在 VLM 领域的直接应用
- [[2026-05-19-蒸馏量化RL三联流水线-后训练范式统一]] → 三联流水线在 VLM 场景需要扩展：Teacher RL 可能是纯文本 VLM（Praxis-VLM 思路），Dense Bridge 需要视觉 token 对齐
- [[2026-05-04-LLM对齐训练范式RLHF-DPO-GRPO-DAPO]] → GRPO 的 group-centered advantage 在 VLM 的多模态 token 混合场景下行为不同——视觉 token 的 contribution 被稀释
- [[2026-05-06-MoE混合专家模型前沿-路由策略与训练稳定性]] → VoRA 的 rank-1024 视觉 LoRA 实质上创造了隐式 MoE 结构，每层有语言 LoRA 和视觉 LoRA 两套参数

---

## Actionable Insights

1. **Hermes Vision 集成**：如果未来 Hermes Agent 接入视觉能力（截图理解、UI 操作），VLM RL 训练框架可以直接复用。推荐 Unsloth + Qwen3-VL-8B 方案（单 T4 可训）
2. **Skill 开发机会**：`vlm-grpo-training` skill — 从图片+描述数据训练自定义 VLM 推理模型，涵盖数据准备、LoRA 配置、reward 设计
3. **验证实验**：可以用小规模实验验证「视觉编码器冻结 vs 解冻」在具体任务上的差异（如 OCR、文档理解），补充现有的纯 LLM 结论
4. **Praxis-VLM 迁移思路**：先在纯文本场景做 GRPO RL 训练 reasoning，再迁移到视觉输入。这可能比直接在多模态数据上训练更高效

---

## 待深入问题

1. 视觉编码器解冻 + LoRA 的 RL 训练在垂直领域（医疗影像、工业检测）的效果 — 通用 ViT 表征是否足够
2. VoRA 的 rank-1024 视觉 LoRA 在 RL 场景下的表现 — 大 rank 视觉 LoRA 是否也遵循 Schulman r=1 论证的 RL 低信息需求
3. Latent Visual Reasoning + GRPO 的完整训练 pipeline — latent 空间的 reward 如何设计
4. MoE-VLM（如 DeepSeek-V4 可能有视觉变体）的 RL 训练 — 专家路由 + 视觉编码器的双重 LoRA 策略
5. Vision-SR1 的多 reward 信号如何与 GDPO 分维度标准化结合 — 视觉/语言 reward 是否需要不同的 normalization 策略
6. Praxis-VLM 文本→视觉迁移的零样本泛化边界 — 哪些视觉推理能力无法从文本训练获得
7. VLM RL 训练的 reward hacking 检测与防御 — VLM-R1 发现的 OD reward hacking 在其他视觉任务上的普遍性

---

## 参考文献

1. VLM-R1: A Stable and Generalizable R1-style Large Vision-Language Model (arxiv 2504.07615, 2025.04)
2. Vision-G1: Towards General Vision Language Reasoning with Multi-Domain Data Curation (AAAI, arxiv 2508.12680)
3. CLGRPO: Reasoning Ability Enhancement for Small VLMs (arxiv 2506.18048)
4. Vision-SR1: Self-Rewarding Vision-Language Model via Reasoning Decomposition (ICLR 2026, arxiv 2508.19652)
5. Praxis-VLM: Vision-Grounded Decision Making via Text-Driven Reinforcement Learning (NeurIPS 2025, arxiv 2503.16965)
6. VoRA: Vision as LoRA (arxiv 2503.20680)
7. Latent Visual Reasoning (arxiv 2509.24251)
8. DeepVideo-R1: Video Reinforcement Fine-Tuning via Difficulty-aware Regressive GRPO (NeurIPS 2025, arxiv 2506.07464)
9. Tina: Tiny Reasoning Models via LoRA (arxiv 2504.15777)
10. SCALe: Balanced Thinking - Improving Chain of Thought Training in VLMs (arxiv 2603.18656)
11. UAV-VL-R1: Generalizing VLMs via SFT and Multi-Stage GRPO for UAV Visual Reasoning (arxiv 2508.11196)

## 相关笔记
