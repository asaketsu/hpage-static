# radixArk 的 Miles 与 SGLang：大规模 RL 后训练的双引擎

> **类型**: 原创技术研究笔记
> **日期**: 2026-07-31
> **标签**: `radixArk` `Miles` `SGLang` `RL` `后训练` `MoE` `FP8` `Rollout` `RLHF`

---

## 核心结论

radixArk 是一家聚焦大规模 RL 后训练基础设施的公司。其核心产品 **Miles** 是企业级强化学习框架（fork 自清华 slime），与 **SGLang**（LMSYS 的高性能推理引擎）深度耦合，共同解决大规模 RL 训练的三大难题：**训练-推理不一致（Mismatch）、MoE 模型训练崩溃、Rollout 吞吐瓶颈**。Miles 主攻训练稳定性与低精度优化，SGLang 主攻高吞吐推理。两者共同构成了"**SGLang 推理生成 → Miles 训练更新**"的 RL 闭环。

---

## 一、radixArk 与 Miles 是什么？

| 维度 | 说明 |
|------|------|
| **radixArk** | AI 基础设施公司，聚焦大规模 RL 后训练 |
| **Miles** | 企业级 RL 框架，fork 自清华 [slime](https://github.com/THUDM/slime) |
| **定位** | "Enterprise-Grade RL for Large-Scale Model Post-Training" |
| **GitHub** | [radixark/miles](https://github.com/radixark/miles) ⭐1836 |
| **发起方** | InfiXAI + 蚂蚁集团 + SGLang RL Team + Miles 社区 |
| **首发** | 2025-11 |
| **技术栈** | Miles（训练）+ SGLang（推理/Rollout）+ Megatron-LM（大模型训练组件） |

> Miles 官方名言：*"A journey of a thousand miles begins with a single rollout."*

---

## 二、SGLang 与 Miles 的关系：RL 闭环的双引擎

```
大规模 RL 后训练的完整闭环:

┌─────────────────────────────────────────────────────┐
│                    RL 训练循环                        │
│                                                     │
│  ┌──────────────────────────────────────────────┐   │
│  │  SGLang (Rollout 引擎)                        │   │
│  │  • 高吞吐推理生成                              │   │
│  │  • RadixAttention 前缀缓存                    │   │
│  │  • FP8 推理量化                               │   │
│  │  • 推测解码 (Speculative Decoding)            │   │
│  │  • 路由决策记录 (R3)                          │   │
│  │  ↓                                           │   │
│  │  生成轨迹 (trajectories) + log prob           │   │
│  └──────────────────────┬───────────────────────┘   │
│                         │                           │
│                    权重同步 (Zero-Copy)              │
│                         │                           │
│  ┌──────────────────────┴───────────────────────┐   │
│  │  Miles (训练引擎)                             │   │
│  │  • GRPO / PPO 等 RL 算法                      │   │
│  │  • Megatron-LM / FSDP 训练后端                 │   │
│  │  • FP8 训练量化                               │   │
│  │  • 路由决策回放 (R3)                          │   │
│  │  • 重要性采样修正 (TIS/MIS)                   │   │
│  │  ↓                                           │   │
│  │  更新后的模型权重                             │   │
│  └──────────────────────┬───────────────────────┘   │
│                         │                           │
│                    权重重载到 SGLang                  │
│                         │                           │
│  ──────────────────────┴────────────────────────    │
│                       下一个 Epoch                   │
└─────────────────────────────────────────────────────┘

核心协同:
  SGLang 负责"快"——高吞吐 Rollout
  Miles 负责"稳"——稳定的大规模训练
```

### 分工矩阵

| 能力 | SGLang | Miles |
|------|--------|-------|
| 推理生成 (Rollout) | ✅ **核心** | — |
| RL 算法 (GRPO/PPO) | — | ✅ **核心** |
| 梯度更新/训练 | — | ✅ **核心** (Megatron/FSDP) |
| 高吞吐 KV 缓存 | ✅ RadixAttention | — |
| FP8 推理 | ✅ | — |
| FP8 训练 | — | ✅ **Unified FP8** |
| MoE 专家路由 | ✅ 记录路由 (R3) | ✅ 回放路由 (R3) |
| 推测解码 | ✅ | ✅ Online SFT Draft |
| 权重同步 | ✅ 零拷贝映射 | ✅ CUDA IPC |

---

## 三、Miles 的核心技术贡献

### 3.1 消除训练-推理不一致（Train-Inference Mismatch）

这是大规模 MoE RL 的**头号难题**：训练用 BF16/FP32，推理用 FP8/INT4 量化，精度差异导致 log prob 不一致，RL 训练发散甚至崩溃。

| 解法 | 说明 |
|------|------|
| **Unified FP8** (2025-11) | 业界首个端到端 FP8 采样+训练统一管线——训练和推理用完全相同的 FP8 量化逻辑，消除量化误差导致的 RL 崩溃 |
| **R3: Rollout Routing Replay** (2025-12) | 记录 SGLang 推理时的专家路由决策，训练时回放——消除 MoE 模型的"训练-推理路由不一致"，防止 Qwen3/DeepSeek-V3 等 MoE 训练崩溃 |
| **Bit-wise Identical Log Probs** | 内核级优化（FlashAttention-3, DeepGEMM）实现确定性的前向/反向传播 |
| **TIS/MIS 算法修正** | 当不一致不可避免时，用截断重要性采样 (TIS) 和掩码重要性采样 (MIS) 缓解 off-policy 偏差 |

### +SGLang 协同：R3 是 SGLang 联合发布

> R3（Rollout Routing Replay）由 **Miles 与 SGLang 联合开发**——SGLang 记录路由，Miles 回放路由，两端协同解决 MoE RL 不稳定问题。

### 3.2 极致性能优化

| 技术 | 效果 |
|------|------|
| **Speculative RL Training** | 用 Online SFT Draft Model 做推测解码，Rollout 加速 **25%+**（与传统冻结 draft 不同，Miles 在线更新 draft 策略防漂移） |
| **Zero-Copy Weight Sync** | CUDA IPC 零拷贝映射 + 异步张量聚合 + 桶式展平，权重同步时间减少 **50%** |
| **Partial Rollout & Over-Sampling** | 多轮 RL 的"长尾效应"——过度采样请求并回收半成品轨迹，最大化 GPU 利用率 |

### 3.3 INT4 QAT：1TB 模型单机训练

| 维度 | 说明 |
|------|------|
| **动机** | 1TB+ 级别模型（如 DeepSeek-V3 671B）跨节点训练通信开销巨大 |
| **方案** | INT4 W4A16 量化感知训练，受 Kimi K2-Thinking 报告启发 |
| **效果** | 1TB 模型可装入单机（如 H200），消除跨节点瓶颈，**Rollout 效率翻倍**，精度保持 BF16 水平 |

---

## 四、模型与场景支持

### 4.1 支持的模型

| 家族 | 支持型号 |
|------|---------|
| **DeepSeek** | R1, V3, V3.2 |
| **Qwen** | Qwen 2, 2.5, 3 |
| **Llama** | Llama 3, 3.1, 3.3, 4 |
| **GLM** | GLM-4.5, 4.6, 4.7 |
| **Gemma** | Gemma 2, 3, 3N |
| **MiniMax** | M2, M2.1 |
| **其他** | Mistral, Mixtral, Phi, gpt-oss 等 SGLang/Megatron 支持的任意模型 |

### 4.2 训练场景

| 场景 | 说明 |
|------|------|
| **Multi-Turn Interaction** | 多轮对话和工具使用 |
| **VLM & LLM** | 视觉-语言模型 + 纯文本模型统一框架 |
| **Reasoning & Coding** | 数学/逻辑推理 + 编码 Agent 专项优化 |
| **Multi-Agent RL** | MrlX 协同进化框架——多 Agent 共同训练（如医患模拟、DeepResearch 流水线） |

---

## 五、radixArk 的完整技术栈

| 仓库 | Star | 说明 |
|------|------|------|
| **[miles](https://github.com/radixark/miles)** | ⭐1836 | 核心 RL 框架 |
| **[sgl-router-for-miles](https://github.com/radixark/sgl-router-for-miles)** | ⭐6 | SGLang 路由器（专门为 Miles 优化的 SGLang 分支/封装） |
| **[Megatron-Bridge](https://github.com/radixark/Megatron-Bridge)** | ⭐4 | Megatron 训练库 + HF 双向转换 |
| **[Megatron-LM](https://github.com/radixark/Megatron-LM)** | ⭐10 | Megatron fork（定制优化） |
| **[miles_diffusion](https://github.com/radixark/miles_diffusion)** | ⭐23 | [实验] 扩散模型 RL 后训练框架 |
| **[gorilla](https://github.com/radixark/gorilla)** | ⭐0 | 函数调用/工具调用训练评估 |
| **[docs](https://github.com/radixark/docs)** | ⭐0 | 文档 |

---

## 六、Miles 与其他 RL 框架对比

| 维度 | Miles | verl | slime | AReaL |
|------|-------|------|-------|-------|
| **起源** | radixArk (fork slime) | 字节火山 | 清华 THUDM | 蚂蚁 inclusionAI |
| **推理引擎** | **SGLang** (深度协同) | SGLang | SGLang | SGLang |
| **训练后端** | Megatron + FSDP | FSDP | FSDP | Megatron |
| **FP8 训练** | ✅ **Unified FP8** | ✅ | 部分 | ✅ |
| **MoE 路由一致性** | ✅ **R3** | — | — | — |
| **INT4 QAT** | ✅ | — | — | — |
| **推测 RL** | ✅ Online SFT Draft | — | ✅ | — |
| **多 Agent RL** | ✅ MrlX | — | — | — |
| **企业级** | ✅ 核心定位 | ✅ | 研究 | ✅ |
| **VLM 多轮** | ✅ | ✅ | ✅ | — |

> Miles 与 SGLang 的关系最紧密——R3 和 Unified FP8 都是两者联合开发的。SGLang README 也将 Miles 列为 RL 后训练的核心采用方之一。

---

## 七、SGLang RL 生态全景

SGLang 是多个 RL 框架的推理后端：

| RL 框架 | 团队 | 与 SGLang 关系 |
|---------|------|---------------|
| **Miles** | radixArk + 蚂蚁 | **最深度协同**——联合开发 R3/FP8 |
| **verl** | 字节火山 | 采用 SGLang 做 rollout |
| **slime** | 清华 THUDM | Miles 的上游 |
| **AReaL** | 蚂蚁 inclusionAI | 采用 SGLang |
| **Tunix** | Google | 采用 SGLang |

---

## 八、快速启动参考（文档记录）

```bash
# Docker
docker pull radixark/miles:latest

# FP8 GRPO 训练 Qwen3 示例
python train.py \
    --advantage-estimator grpo \
    --model-name qwen3-30b-a3b \
    --hf-checkpoint /path/to/qwen3-30b-a3b-hf \
    --rollout-batch-size 512 \
    --n-samples-per-prompt 8
```

---

## 九、技术演进时间线

| 时间 | 里程碑 |
|------|--------|
| 2025-11 | Miles 项目启动（InfiXAI + 蚂蚁 + SGLang RL Team） |
| 2025-11 | Unified FP8 发布（首个端到端 FP8 RL） |
| 2025-11 | 推测解码 RL 集成 |
| 2025-12 | **R3: Rollout Routing Replay**（与 SGLang 联合，解决 MoE RL 崩溃） |
| 2026-01 | INT4 QAT（1TB 模型单机训练） |
| 2026-01 | VLM 多轮训练 + MrlX 多 Agent 共进化 |
| 2026-02 | 详细 CLI 参数文档 |

---

## 十、关键术语速查

| 术语 | 说明 |
|------|------|
| **Miles** | radixArk 企业级 RL 框架，fork 自 slime |
| **SGLang** | LMSYS 高性能推理引擎，Miles 的 rollout 后端 |
| **Rollout** | RL 中的推理生成阶段——用当前策略生成轨迹 |
| **Train-Inference Mismatch** | 训练（高精度）与推理（量化）的 log prob 不一致，导致 RL 发散 |
| **Unified FP8** | 训练和推理统一 FP8 量化，消除精度不一致 |
| **R3 (Rollout Routing Replay)** | 记录推理路由→训练回放，解决 MoE 路由不一致 |
| **TIS** | Truncated Importance Sampling，截断重要性采样 |
| **MIS** | Masked Importance Sampling，掩码重要性采样 |
| **QAT** | Quantization-Aware Training，量化感知训练 |
| **Zero-Copy Weight Sync** | CUDA IPC 零拷贝权重同步 |
| **Speculative RL** | 推测解码加速 RL Rollout |
| **slime** | 清华 THUDM RL 框架，Miles 的上游 |
| **Megatron-LM** | NVIDIA 大规模训练框架 |

---

## 十一、与现有笔记的关联

| 关联笔记 | 关系 |
|---------|------|
| **SGLang vs vLLM** | 本笔记是 SGLang 在 RL 训练领域的深度展开——SGLang 不只是推理引擎，更是 Miles/verl/slime 等 RL 框架的 rollout 后端 |
| **PyTorch** | Miles/SGLang/Megatron 全部基于 PyTorch 构建 |
| **飞机结构设计 AI** | 研究策划中的"专家模型训练"阶段需要 RL 后训练（GRPO），Miles 是候选框架 |
| **Gemini Robotics 2** | VLA 模型的 RL 后训练可参考 Miles 的 VLM 多轮 RL 范式 |
| **具身智能产业链** | 算法类企业（星海图/深谋/达闼）的模型训练基础设施 |
| **VLA Action Head** | Action Head 模型的 RL 微调可参考 Miles 的 VLM 多轮训练 |


## 相关笔记

- [LLM 后训练 RL 框架 2026 全景 slime verl vime](./2026-08-02-LLM后训练RL框架2026全景-slime-Miles-verl-vime生态.md) — 本文续篇，四大引擎生态扩展
- [LLM 推理模型 RL 训练前沿 GRPO 到 DAPO](./2026-07-18-LLM推理模型RL训练前沿-从GRPO到DAPO与异步系统.md) — RL 算法演进路径
- [推理时计算扩展 Best-of-N 到 Compute-Optimal](./2026-07-28-推理时计算扩展-从Best-of-N到Compute-Optimal自适应分配.md) — 训练后推理优化配合
- [ES-GRPO 混合训练 Pipeline](./2026-06-05-ES-GRPO混合训练Pipeline-无梯度与有梯度RL的最优切换.md) — 混合 RL 训练策略
