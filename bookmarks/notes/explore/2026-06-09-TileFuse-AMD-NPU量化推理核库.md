# TileFuse: AMD NPU 上融合混合精度量化 LLM 推理核库

> **来源**: [arXiv:2606.11357](https://arxiv.org/abs/2606.11357) | [GitHub](https://github.com/glassescrab/mlir-aie/tree/feature/update-mix-mm-int4-verification)
>
> **作者**: Wesley Pang, Gregory Hyegang Jun, Feiyang Liu, Deming Chen (UIUC)
>
> **日期**: 2026-06-09 (v1), 2026-07-01 (v2) | **领域**: cs.DC, cs.AI, cs.AR, cs.PF

---

## 一、核心问题与研究动机

### 边缘 NPU 的困境

当前客户级 SoC 普遍集成 NPU（Apple Core ML、Qualcomm QNN、Intel OpenVINO 等），但这些 NPU 软件栈多为**闭源专有**，仅提供高层部署接口，缺乏底层编程控制。更关键的是，广泛使用的开源量化格式（如 **AWQ 的 W4A16**）无法直接映射到 NPU 上——它们只能支持受限的子集（per-tensor、per-channel、对称量化），而现代边缘 LLM 普遍使用**非对称 per-group** 量化。

这意味着用户被迫**适应模型去适配 NPU**，而非让 NPU 直接运行已有的预量化模型。

### AMD XDNA2 的独特优势

AMD XDNA2 NPU（集成于 Ryzen AI 7 350 Krackan Point 和 Ryzen AI 9 HX 370 Strix Point）提供了独特的可重构空间架构 + 开源近金属软件栈 **MLIR-AIE (IRON)**，允许开发者自定义微内核和显式数据流。这使其成为研究 NPU 量化 LLM 推理的绝佳平台。

---

## 二、方法论

### 2.1 整体设计

TileFuse 是一个端到端的近金属实现，包含三个核心组件：

| 组件 | 目标 |
|------|------|
| 权重预分块 (Weight Pre-tiling) | 将量化元数据与权重打包，重组布局以支持大矩阵 |
| 混合精度微内核 (Mixed-precision Microkernels) | 融合解压、反量化和 GEMM/GEMV 计算 |
| GEMV 数据流协同设计 | 利用完整的 4×8 AIE 阵列加速 token 生成 |

### 2.2 四个设计挑战

1. **高效即时反量化**：反量化后需复用权重 tile，而非每次重新计算。TileFuse 使用计算核本地内存存储反量化后的 BF16 权重。
2. **有限流下的元数据传输**：XDNA2 流接口有限，无法同时传输权重、激活和元数据三个独立流。
3. **大 MLP 层支持**：LLM MLP 层维度常达 32K，但 DMA 步长寄存器有限，超过 8K 需拆分调用。
4. **GEMV 硬件利用率低**：token 生成阶段的 GEMV 操作基线只使用一行计算核。

### 2.3 核心技术

**权重预分块与元数据打包**：
- W4A16 格式：权重 tile 按 INT4 连续存储，后跟 BF16 缩放因子和 INT8 零点（per-group 128）。
- 128×64 权重 tile 需 64 个缩放因子 + 64 个零点（复制以对齐 128 字节 DMA 要求）。
- 额外元数据仅占 1.5% 内存。

**交错列主预分块**：
- 默认行主布局中，AIE 列 j 处理的 tile 分布在列 j, j+8, j+16...，造成大内存步长。
- 交错列主布局将同一 AIE 列的 tile 连续存放，消除大步长访问，支持 K、N 维度高达 32K。

**混合精度微内核**：
- W4A16：解压 packed INT4（每字节两个 4-bit 值）→ 展宽为 INT8 → 反量化为 BF16 → 存入本地缓冲区 → GEMM/GEMV。
- 复用策略：每个权重块只反量化一次，存储在本地缓冲区，多次复用。
- W8A16：INT8 直接转 BF16 × 缩放因子（对称量化，无零点）。

**GEMV 微内核优化**：
- 基线每次加载 16×8 权重块，仅处理 16 个输出元素。
- TileFuse 加载 64×8 权重块（8 个 8×8 子块），复用 1×8 激活片段，每迭代累积 64 个输出元素。

**GEMV 数据流重设计**：
- 基线：shim 核直接流式传输权重到一行计算核（仅用 8/32 核）。
- TileFuse：shim 核将 4 个权重 tile 打包到 memory 核 → memory 核分发到 4 行计算核（全 32 核利用）。

**近金属 XDNA2 可重构性利用**：
- 计算核级：自定义混合精度微内核替换 BF16 GEMM/GEMV 数据路径。
- 内存/DMA 级：离线预分块匹配 AIE 阵列访问模式。
- 阵列级：通过 memory 核配置 GEMV 权重分发路径。
- 限制：核分发和 AIE 配置有运行时开销（毫秒级），适合大 GEMM 但对小 GEMV 不利。

### 2.4 端到端 LLM 部署

- 自定义 C++ 框架 + Python 绑定，加载 Hugging Face safetensors 权重。
- **混合 NPU+iGPU 架构**：线性层（注意力投影、MLP 投影）→ NPU；FlashAttention-2、softmax、归一化等 → iGPU。
- 按算子级别选择设备（非并行执行），以隔离 NPU 增益。
- 利用 AMD Ryzen 统一内存，跨 CPU/iGPU/NPU 无一致性开销。

---

## 三、关键实验结果与数据

### 3.1 核级别性能

**平台**：Ryzen AI 7 350 (Krackan Point, 8-CU iGPU) + Ryzen AI 9 HX 370 (Strix Point, 16-CU iGPU)。两者 XDNA2 NPU 架构相同。

**GEMM 性能**：
- Krackan Point 峰值 12 TOPS，Strix Point 峰值 9 TOPS（差异归因于硅片质量/热设计/内存行为，非架构差异）。
- iGPU：8-CU Krackan Point ~5 TOPS，16-CU Strix Point ~7 TOPS。
- CPU 仅约 200 GOPS。
- NPU 在形状变化时表现平滑（无锯齿状吞吐量波动），归功于自定义权重布局。

**GEMV 性能**（1×4096×14336）：
- Krackan Point NPU：W4A16 = 206 GOPS, W8A16 = 104 GOPS。
- Strix Point NPU：W4A16 = 181 GOPS, W8A16 = 97 GOPS。
- CPU 在 GEMV 上表现更强（接近 DRAM 带宽极限），因为 NPU 为计算优化而非内存带宽优化。

### 3.2 端到端 LLM 性能

**预填充（Prefill）延迟 — Ryzen AI 7 350（W4A16，Llama3-8B）**：

| Prompt | GPU (ms) | NPU (ms) | 加速比 |
|--------|----------|----------|--------|
| 256 | 869.7 | 650.8 | 1.34x |
| 512 | 1801.0 | 1101.5 | 1.64x |
| 1024 | 3700.7 | 2048.5 | 1.81x |
| 2048 | 8246.9 | 4129.9 | 2.00x |
| 4096 | 18141.9 | 9209.2 | 1.97x |
| 8192 | 44707.0 | 23506.2 | 1.90x |

- W4A16 在中等和长 prompt 上 NPU 显著优于 iGPU，短 prompt 因 NPU 固定开销（核分发 + 布重构）反而较慢。
- 随着 prompt 增长，固定开销被均摊，NPU 优势逐渐显现。

**Ryzen AI 9 HX 370（W4A16，Llama3-8B）**：

| Prompt | GPU (ms) | NPU (ms) | 加速比 |
|--------|----------|----------|--------|
| 256 | 569.3 | 722.2 | 0.79x |
| 512 | 1116.6 | 1210.1 | 0.92x |
| 1024 | 2240.7 | 2219.4 | 1.01x |
| 2048 | 4858.9 | 4194.9 | 1.16x |
| 4096 | 10380.7 | 8700.4 | 1.19x |
| 8192 | 24544.4 | 20043.8 | 1.22x |

- HX 370 的更强 iGPU（16-CU）抵消了 NPU 增益，预填充延迟两平台相近。

**Token 生成吞吐（tok/s，W4A16）**：

| 模型 | AI 7 350 GPU | AI 7 350 NPU | AI 9 HX 370 GPU | AI 9 HX 370 NPU |
|------|-------------|-------------|----------------|----------------|
| Gemma-2B | 31.44 | 28.91 | 12.64 | 14.03 |
| Qwen2.5-3B | 19.22 | 15.05 | 38.31 | 34.84 |
| Llama3-8B | 7.73 | 7.42 | 15.73 | 15.05 |

- NPU 在 token 生成上略慢于 iGPU，因为 GEMV 操作在几百微秒级，但 NPU 驱动和配置开销在毫秒级。

**能量效率（Llama3-8B，4096-token prompt）**：
- AI 7 350：NPU 385.98 J vs GPU 1091.81 J → **节能 64.6%**。
- AI 9 HX 370：NPU 322.89 J vs GPU 684.59 J → **节能 52.8%**。

### 3.3 与其他 NPU 工作对比

| 模型 | 前作 | 速度 (tok/s) | TileFuse | 速度 (tok/s) | 加速 |
|------|------|-------------|----------|-------------|------|
| Llama-3-8B | FastFlowLM | 345.9 | 501.9 | 1.45x |
| Qwen2.5-3B | Scaling NPU | 550.0 | 890.4 | 1.61x |

### 3.4 消融研究

- **仅预分块**：GEMM 提升约 50%，支持输出维度超过 8K（基线仅支持 8K）。
- **混合精度微内核**：在预分块基础上再提升约 50%，大尺寸最高 121.6%。
- **GEMV 微内核+数据流优化**：基线+混合精度提升 20%-40%，加上微内核和数据流优化后最高 **281%**。

---

## 四、创新点分析

### 4.1 核心创新

1. **直接支持 AWQ-style 量化格式**：不要求模型适配 NPU 的专有量化方案，而是让 NPU 直接运行已有预量化模型。这与 ScalingLLM（Qualcomm 专用块量化）形成本质区别。

2. **融合核设计（Fused Kernel）**：解压→反量化→矩阵计算三步合一，避免 BF16 中间量的全局内存往返。复用本地内存存储反量化结果，避免重复计算。

3. **交错列主预分块（Interleaved Pre-tiling）**：创新性地将同一 AIE 列的权重 tile 连续存放，消除 DMA 大步长，支持 32K 维度。这是解决大 MLP 层的关键。

4. **GEMV 全阵列数据流**：通过 memory 核作为中间分发层，将 GEMV 从单行计算扩展到全 4×8 阵列，是 NPU 空间架构的独特利用方式。

5. **混合 NPU+iGPU 架构**：认识到 NPU 优势（大 GEMM）和劣势（小 GEMV 延迟敏感），将线性层交给 NPU，其余交给 iGPU。利用 AMD 统一内存特性实现低开销协同。

### 4.2 方法论贡献

TileFuse 展示了如何系统性地利用 NPU 的可重构性（计算核级、内存/DMA 级、阵列级），同时诚实地量化了其局限性（配置开销对小算子不利）。消融研究清晰地分离了各优化组件的贡献。

---

## 五、局限性与未来方向

### 5.1 论文指出的局限

1. **Token 生成瓶颈**：NPU 配置开销（毫秒级）远大于 GEMV 操作时间（微秒级），导致 token 生成 NPU 略慢于 iGPU。
2. **模型维度不匹配**：Qwen2.5-3B 的 MLP 隐藏维度不是最小 tile-size 的倍数，padding 导致过度计算。
3. **当前非并行执行**：NPU 和 iGPU 按依赖顺序串行执行，未实现真正的并发。
4. **平台差异未完全解释**：Krackan Point NPU 性能高于 Strix Point，但公开规格无法完全解释，可能涉及有效流带宽、热设计、运行时调度等。

### 5.2 潜在改进方向

1. **真正的 NPU+iGPU 并行执行**：预填充 NPU + Token 生成 iGPU 的混合策略能结合两者优势。
2. **动态 tile-size 适配**：自动适应不同模型的 MLP 维度。
3. **其他 NPU 架构移植**：预分块思想（离线重组 AWQ 权重匹配硬件消费模式）可移植到其他 GPU/NPU。
4. **W4A8 / W4KV4 等更低精度格式**：支持更激进的量化方案。

---

## 六、借鉴点评估（关联 Hermes Agent / Jetson Orin / 量化交易）

### P0 — 可直接移植

**1. 权重预分块思想 → Jetson TensorRT 优化**

- **原理**：离线重组权重布局以匹配硬件消费模式，消除运行时分块开销。
- **关联**：Jetson Orin TensorRT 部署量化模型时，也可预计算最优权重分块和元数据打包。
- **工作量**：中等（需要研究 TensorRT plugin 接口）。
- **优先级**：P0 — 直接提升已有量化部署效率。

**2. 融合核设计思路 → TensorRT 自定义层**

- **原理**：解压→反量化→矩阵计算融合，减少内存往返。
- **关联**：TensorRT 支持 custom plugin，可类似地实现 W4A16/W8A16 融合内核。
- **工作量**：较大（需要 CUDA kernel 编程）。
- **优先级**：P0 — 核心效率提升路径。

### P1 — 需工程改造

**3. 混合 NPU+iGPU 架构 → Jetson NPU+GPU 混合调度**

- **原理**：NPU 处理大 GEMM，GPU 处理延迟敏感操作。
- **关联**：Jetson Orin 同样有 NPU + GPU + 统一内存，可直接借鉴该调度策略。
- **关键障碍**：Jetson NPU 软件栈（NVLM/TensorRT-LLM）的 API 限制。
- **优先级**：P1 — 与 Jetson 平台深度集成相关。

**4. 交错列主布局思想 → 通用权重重排**

- **原理**：将逻辑上分散但物理上连续的访问模式提前整理好。
- **关联**：可用于任何需要大矩阵内存访问的深度学习推理场景。
- **优先级**：P1 — 通用优化技术，可泛化。

### P2 — 长期参考价值

**5. GEMV 全阵列数据流设计 → Jetson NPU 并行优化**

- **原理**：利用 memory 核分发权重到全部计算核。
- **关联**：Jetson NPU 有类似的 DMMA 阵列，可参考此数据流设计。
- **优先级**：P2 — 需要深入研究 Jetson NPU 架构。

**6. 可重构性带来的利弊权衡 → 通用边缘推理设计原则**

- **原理**：可重构硬件提供灵活性，但配置开销需被大算子均摊。
- **关联**：对任何可编程边缘 AI 芯片（RISC-V NPU、FPGA 等）的部署策略有参考意义。
- **优先级**：P2 — 设计哲学层面。

### ❌ 暂不适用

**7. 量化交易场景**

- TileFuse 的核心是矩阵计算优化，与量化交易的 Alpha 研究、回测框架无直接关联。量化交易中虽有大量矩阵运算（如 PCA、协方差矩阵计算），但规模远小于 LLM 推理，现有 numpy/TensorFlow 优化已足够。

---

## 七、关联论文

- **Kara (2607.01237)**：KV Cache 滑动窗口压缩，与 TileFuse 互补 — TileFuse 降低权重内存需求，Kara 降低 KV Cache 内存需求。
- **ScalingLLM (Hao et al.)**：Qualcomm NPU 上的硬件感知块量化，TileFuse 的直接对比对象。TileFuse 优势在于直接支持 AWQ 而非平台专用量化。
- **FastFlowLM**：AMD Ryzen AI 上的 LLM 部署框架，TileFuse 提供了其底层内核细节和开源实现。
- **MaxEVA**：AIE 上的矩阵乘法优化，展示了 AIE 架构的性能潜力，TileFuse 在此基础上增加了量化格式支持。
- **QServe / MARLIN / PowerInfer**：GPU 侧的量化推理优化，TileFuse 将类似思想移植到 NPU。
- **ReasoningEffort (2607.02436)**：推理投入而非工具访问提升 agent 代码生成可靠性 — 互补方向，TileFuse 关注"如何高效推理"，ReasoningEffort 关注"需要多少推理投入"。


## 相关笔记

- [Kara 滑动窗口KV Cache压缩](./2026-07-04-Kara-KVCache压缩.md) — 推理型LLM长CoT缓存压缩
- [KV Cache量化三大突破](./2026-07-05-KVCache量化压缩-TurboQuant-RotorQuant.md) — TurboQuant/RotorQuant向量量化
- [TileFuse AMD NPU量化推理核库](./2026-07-07-TileFuse-AMD-NPU量化推理核库.md) — 本文：AMD NPU融合混合精度核

## 相关笔记

- [KV Cache 量化压缩三突破](./2026-07-05-KVCache量化压缩-TurboQuant-RotorQuant.md) — TurboQuant/RotorQuant
- [Kara 滑动窗口 KV Cache 压缩](./2026-07-04-Kara-KVCache压缩.md) — 高效推理服务
- [LLM 推理优化 2026 全景](../2026-07-08-LLM推理优化2026突破-SMoE端侧部署-SpecSA稀疏推测解码.md) — SMoE/SpecSA 端侧部署

## 相关笔记

- [KV Cache 量化压缩 TurboQuant/RotorQuant](./2026-07-05-KVCache量化压缩-TurboQuant-RotorQuant.md) — 量化算法上游
- [Kara KV Cache 压缩](./2026-07-04-Kara-KVCache压缩.md) — 缓存压缩方案
- [ESP-VISION 边缘 AI 视觉框架](../2026-07-08-ESP-VISION-乐鑫边缘AI视觉低代码框架分析.md) — 边缘端 AI 部署交叉

## 相关笔记

- [KV Cache 量化压缩 2026 三大新突破](./2026-07-05-KVCache量化压缩-TurboQuant-RotorQuant.md) — KV Cache 量化全景
- [Kara：滑动窗口 KV Cache 压缩](./2026-07-04-Kara-KVCache压缩.md) — 滑窗压缩方法
- [SPORK 自推测分叉](./2026-07-08-SPORK自推测分叉.md) — Agent 推理加速
- [LLM推理优化2026突破-SMoE端侧部署](./2026-07-08-LLM推理优化2026突破-SMoE端侧部署-SpecSA稀疏推测解码.md) — 端侧部署
