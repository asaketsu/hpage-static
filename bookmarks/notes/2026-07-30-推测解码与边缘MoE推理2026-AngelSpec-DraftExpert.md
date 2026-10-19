# 推测解码与边缘 MoE 推理 2026 — AngelSpec 与 DraftExpert

> **出处**: arXiv 2607.25852 (AngelSpec) + arXiv 2607.24434 (DraftExpert) + arXiv 2607.23099 (MoE Skew)
> **日期**: 2026-07-30
> **标签**: #LLM推理 #推测解码 #MoE #边缘部署 #Jetson #speculative-decoding #模型压缩
> **学习方式**: 夜间自学习 cron (Tavily 432 降级 → curl arXiv API)

---

## 📌 内容整理

### 核心问题：推测解码的"没有一刀切"困境

推测解码（Speculative Decoding）是 2024-2026 年 LLM 推理优化最重要的技术之一——用一个小的 draft 模型快速生成候选 token，再用大 target 模型并行验证，在不改变输出分布的前提下加速推理。

但 2026 年的研究揭示了一个关键事实：**没有单一的 draft 架构能在所有真实负载下最优**。不同任务类型（闲聊、代码、数学）需要不同的 draft 策略：

- **自回归多 token 预测（MTP）**：轻量、稳定，适合高熵的开放式闲聊
- **块并行扩散（Block-Parallel Diffusion）**：在长序列上分摊 draft 延迟，适合代码和数学的更长可预测续写
- 选哪个？**取决于输出分布**——而这又因请求而异

### 发现 1：AngelSpec — 统一训练框架 + 自适应验证

**arXiv: 2607.25852** | 2026-07-28

AngelSpec 的核心是在三个层面同时解决"异构性"问题：

**训练层 — 共特化（Co-Specialization）**：
- 不把一个万能 draft 模型拟合到均匀数据混合上
- MTP draft 训练在多样化对话数据上（适合高熵闲聊）
- Block-diffusion draft 训练在代码和数学数据上（适合长可预测续写）
- 两个 draft 各有所长，训练时就已经领域特化

**架构层 — DFly 框架**：
- 混合目标条件骨干（hybrid target-conditioning backbone）
- 前驱条件自回归头（predecessor-conditioned autoregressive head）
- 改善目标特征利用率和块内依赖建模，同时保持生成并行性

**推理层 — 共享批级验证资源**：
- 验证成本和接受长度随领域、请求、在线负载、硬件而变化
- DFly 将验证视为**批级共享资源**：跨请求将算力重新分配给高置信度前缀
- 用预期效用 + profiled 成本模型**在线自适应验证深度**

**关键性能数据**：
- 在 Hy3-A21B 上，平均接受长度提升约 **30%**
- 在 4-64 并发度范围内，始终保持最高平均吞吐量
- 相比自回归解码：**1.98-2.40x 加速**
- 相比 DFlash：**10.5-11.8% 吞吐提升**

**为什么验证是"批级共享资源"？** 因为在多请求并发场景下，不同请求的 draft 质量不同——有些请求的 draft 置信度高（多验证几个 token），有些低（少验证或跳过）。把验证算力从"每请求固定"改为"跨请求动态分配"，整体吞吐最大化。

### 发现 2：DraftExpert — 面向端侧 MoE 的自推测解码

**arXiv: 2607.24434** | 2026-07-27

DraftExpert 解决的是 MoE 模型在端侧设备（Jetson/手机 NPU）上的推理加速——这是一个全新且独特的挑战。

**端侧 MoE 的新瓶颈**：
- MoE 模型每次只激活少量 expert，但路由的 expert 权重经常超过加速器内存
- 延迟关键的单用户场景：expert 需要从 CPU 内存按需加载到 GPU，或从 Flash 加载到移动 NPU
- 自推测解码面临新困境：增加 draft expert 集能提升准确性，但触发额外的 expert 加载；而便宜的小 draft 接受率低

**DraftExpert 的解决方案**：

1. **每层一个轻量级加速器驻留 draft expert**：
   - 通过自蒸馏（self-distillation）从冻结的 target MoE 中学习
   - 蒸馏信号：residual（残差）、logit/token、router-agreement（路由器一致性）
   - 这个 draft expert 常驻加速器，不需要按需加载

2. **固定 footprint 的 draft 组合**：
   - shared expert + top-1 target expert + draft expert
   - 置信度-扩展截断（confidence-expansion truncation）：高置信度时多生成，低置信度时截断
   - target-expert 预取（prefetching）：预测接下来可能需要的 target expert，提前加载

3. **精确验证**：
   - 最终 token 仍由 target 模型精确验证（exactly verified）
   - draft 只是"猜测"，target 保证输出正确性

**关键性能数据**（DeepSeek-V2-Lite 和 Moonlight-16B-A3B）：
- 解码吞吐量平均提升 **1.45x**
- draft 接受率 **84-87%**
- 预取命中率 **86-88%**

**对 Jetson Orin 的直接启示**：
- Jetson Orin Nano Super 有 8GB 统一内存 + 128GB NVMe SSD
- MoE 模型（如 DeepSeek-V2-Lite）的 expert 可以放在 NVMe 上，按需加载到 GPU
- DraftExpert 的 prefetching 机制直接适用于这种"Flash→NPU/GPU" offload 场景

### 发现 3：MoE 推理的分布偏斜问题

**arXiv: 2607.23099** | 2026-07-25

虽然未提取完整摘要，但从标题可见一个重要的工程问题：

MoE 推理由稀疏 expert GEMM 组成，其形状随运行时路由分布而变化。现有服务系统通常用**静态 token-count 桶**选择 fused-MoE kernel，忽略了决定 tile padding 和内存访问模式的 per-expert 路由分布。

这导致的问题：实际路由分布偏斜时（某些 expert 被频繁激活，另一些很少），静态分桶的 kernel 选择不再最优，产生不必要的 padding 和内存浪费。

---

## 🔍 查询拓展

### 推测解码技术谱系（2024-2026）

| 方法 | Draft 来源 | 适用场景 | 局限性 |
|---|---|---|---|
| **经典 SpecDec** (2024) | 独立小模型 | 通用加速 | draft 与 target 不匹配 |
| **Self-SpecDec** (2025) | target 模型自身（跳层） | 无需额外模型 | 加速比有限 |
| **MTP** (2025-2026) | 多 token 预测头 | 高熵开放文本 | 代码/数学表现差 |
| **Block-Diffusion** (2026) | 扩散模型并行生成 | 长可预测序列 | 训练复杂 |
| **AngelSpec** (2026) | MTP + Block-Diffusion 双路 | 全负载自适应 | 需要训练两个 draft |
| **DraftExpert** (2026) | 端侧 MoE draft expert | 端侧 MoE offload | 需要 self-distillation 训练 |

### 对 Hermes Jetson 部署的实际价值

当前 Hermes 在 Jetson Orin 上跑 Ollama（本地推理），存在以下可优化点：

1. **推测解码集成**：
   - Ollama 已支持 draft 模型（`--draft-model` 参数）
   - 可以用小模型（如 Qwen3-0.5B）作为 draft，加速主模型推理
   - AngelSpec 的"按领域选择 draft 策略"可以指导选择

2. **MoE 模型端侧部署**：
   - DeepSeek-V2-Lite（16B 总参数，3B 激活）非常适合 Jetson
   - DraftExpert 的 expert offload 策略可以解决"权重超过内存"问题
   - shared+top-1+draft 组合在 Jetson 上可实现接近 1.5x 加速

3. **验证算力分配**：
   - AngelSpec 的"验证作为批级共享资源"概念
   - 在 Hermes 多请求并发时（cron job + 用户交互），可以动态分配验证深度

---

## 📊 归纳总结

### 三大技术趋势

1. **从单一 draft 到多策略自适应**：AngelSpec 证明，不同负载需要不同 draft 策略。未来的推理引擎需要**运行时自适应切换** draft 机制，而非一劳永逸地选择一种。

2. **从云端到端侧的 MoE 部署**：DraftExpert 打开了 MoE 模型在端侧设备上的部署路径——通过 expert offload + draft expert + prefetching，让超出内存的大 MoE 模型在 Jetson/手机上可运行。

3. **从静态到动态的 kernel 选择**：MoE 推理的分布偏斜问题推动了从静态桶到动态自适应 kernel 选择，这对 Triton/cutlass 层面的优化有直接影响。

### 核心设计原则提炼

- **"按领域特化训练，按负载自适应推理"**（AngelSpec）：训练阶段让不同 draft 擅长不同领域，推理阶段根据当前请求选择最优 draft
- **"draft 常驻，target 按需"**（DraftExpert）：draft expert 小到可以常驻加速器，target expert 大到需要从外部存储按需加载
- **"验证是可调度资源"**（AngelSpec）：验证深度不是固定的，而是根据置信度和系统负载动态调整

### 反直觉发现

- **"增加 draft expert 集不总是更好"**（DraftExpert）：直觉上多加 draft expert 能提升准确性，但在端侧场景下会触发更多 expert 加载，反而拖慢速度。置信度截断比盲目扩展更有效。
- **"块并行扩散在代码/数学上比 MTP 强"**（AngelSpec）：直觉上更复杂的 draft 机制应该全面更优，但实际上 block-diffusion 在代码/数学（长可预测序列）上的优势来自"在长序列上分摊 draft 延迟"这一特性，而非 draft 本身更聪明。

---

## 📈 趋势判断

### 短期趋势（3-6个月）

- **推测解码成为推理引擎标配**：vLLM、TensorRT-LLM、Ollama 等引擎将原生支持多 draft 策略切换
- **端侧 MoE 部署工具链成熟**：类似 DraftExpert 的 expert offload 框架将开源，Jetson/手机 NPU 部署 MoE 模型变得可行

### 中期趋势（6-12个月）

- **推理优化从"一刀切"到"千人千面"**：不同用户、不同任务、不同硬件配置下的最优推理配置将自动生成
- **Draft 模型的自动训练**：类似 DraftExpert 的 self-distillation pipeline 将被工具化，给定 target 模型自动生成最优 draft

### 对边缘 AI 部署的影响

Jetson Orin Nano Super（8GB RAM, 67 TOPS）部署 LLM 的路线图：
- **Phase 1（当前）**：7B 模型 + INT4 量化 + 标准 KV cache → 可运行但速度有限
- **Phase 2（近期）**：7B 模型 + 推测解码（小 draft 模型）→ 1.5-2x 加速
- **Phase 3（中期）**：MoE 模型（DeepSeek-V2-Lite）+ DraftExpert 式 expert offload → 更大模型可部署
- **Phase 4（远期）**：AngelSpec 式多策略自适应 + 硬件感知 kernel 调度 → 理论最优推理

---

## 🔗 关联分析

### 与已有笔记/知识的关联

- **本地模型部署-消费级GPU推理** (2026-07-29)：ZSE 引擎的冷启动优化与推测解码的推理加速是互补的——前者解决"启动慢"，后者解决"运行慢"
- **LLM推理优化技术** Skill：现有 Skill 涵盖 PagedAttention/量化/推测解码/连续批处理，本次笔记补充了推测解码的最新进展（AngelSpec 的多策略 + DraftExpert 的端侧 MoE）
- **edge-llm-quantization** Skill：GGUF 量化 + Jetson 部署的现有工作流，可以增加 DraftExpert 式 MoE expert offload 作为新部署策略
- **Jetson Orin 平台** Skill：CUDA 编译、传感器集成的现有体系，可以集成推测解码推理优化

### 对 Hermes 系统的具体改进建议

1. **Ollama 推测解码配置**：在 Jetson 上的 Ollama 配置中，增加 `--draft-model` 参数，用小模型加速主模型推理
2. **MoE 模型部署实验**：尝试在 Jetson 上部署 DeepSeek-V2-Lite（16B/3B），用 DraftExpert 式 expert offload 策略
3. **llm-inference-optimization Skill 更新**：补充 AngelSpec 的多策略自适应和 DraftExpert 的端侧 MoE 章节

---

## 📚 参考论文

1. **AngelSpec**: Towards Real-World High Performance Inference with Speculative Decoding — arXiv:2607.25852
2. **DraftExpert**: Expansion-Aware Self-Speculative Decoding for End-Device MoE Inference — arXiv:2607.24434
3. **Decoding the Skew**: Distribution-Aware MoE Inference with Adaptive Kernel Dispatch — arXiv:2607.23099
4. **MoE²-LoRA**: When MoE Models Meet MoE-style Low-Rank Adaptation — arXiv:2607.21978
5. **Beyond Independent Optimization**: Compression, MoE Routing, and Quantization Interactions in Multimodal Edge Intelligence — arXiv:2607.20981


## 相关笔记

- [LLM推理加速2026-MTP与推测解码实战全景](./2026-07-02-LLM推理加速2026-MTP与推测解码实战全景.md) — 推测解码全景综述
- [LLM推理优化2026突破-SMoE端侧部署-SpecSA](./2026-07-08-LLM推理优化2026突破-SMoE端侧部署-SpecSA稀疏推测解码.md) — 稀疏推测解码
- [LLM推理优化2026全景-三层栈-NSA稀疏注意力](./2026-07-11-LLM推理优化2026全景-三层栈-NSA稀疏注意力-引擎横评.md) — 推理优化三层栈
