# LLM 推理优化 2026 最新进展：稀疏注意力、KV 缓存与超低比特量化

> 📅 2026-06-07 · 📂 LLM Inference · 🔬 来源：arXiv 2026-06-03/04 批次论文

## 核心发现

### 1. 跨层稀疏注意力：7.6x 解码加速（arXiv:2606.06467 · CLSA）

在 KV 共享架构（如 YOCO）基础上，提出跨层稀疏注意力（CLSA）。核心思路：**不仅共享 KV 缓存，还共享路由索引**。单一索引器一次性完成 token 级 top-k 选择，跨层复用索引结果。

**性能数据**：
- 解码加速：**7.6x**
- 整体吞吐提升：**17.1x**（128K 上下文）
- 同时优化预填充、KV 缓存存储、长上下文解码三大瓶颈

**对 Jetson 部署的启示**：CLSA 的索引复用大幅减少计算量，特别适合 Jetson Orin 的内存带宽受限场景。128K 上下文下的 17.1x 吞吐提升意味着相同硬件可服务 17 倍用户。

### 2. 非均匀 KV 缓存服务系统（arXiv:2606.06302 · Tangram）

多轮对话场景下 KV 缓存线性增长是 GPU 内存的主要压力源。Tangram 提出三项核心技术：

- **确定性预算分配**：为每个注意力头分配静态内存，消除动态调度开销
- **头组页面（Head Group Page）**：按保留需求聚类注意力头，独立页表管理
- **提前负载均衡（AOT）**：利用静态预算 profile 确保 GPU 利用率均匀

**性能**：吞吐提升 **2.6x**，完全保持模型精度。

**对 Jetson 部署的启示**：Jetson Orin 的统一内存架构（CPU/GPU 共享 8GB）使 KV 缓存压力更大。Tangram 的确定性预算分配可精确控制内存占用，避免 OOM。

### 3. MoE 模型量化路由一致性（arXiv:2606.05688 · VSRAQ）

MoE（混合专家）模型量化后，微小扰动可能导致专家选择路由改变，大幅降低模型质量。VSRAQ 提出双目标量化：

- **值对齐（Value Alignment）**：匹配路由相关的 logits/scores
- **结构对齐（Structure Alignment）**：保持专家排序和 top-k 决策边界

**关键优势**：零推理时额外开销，可集成到现有量化框架。

**对 Jetson 部署的启示**：Mixtral、DeepSeek-MoE 等 MoE 模型在 Jetson 上部署时，VSRAQ 可确保量化后路由一致性，避免因量化噪声导致的"专家错配"问题。

### 4. 超低比特量化新标杆（arXiv:2606.05429 · SAGE-PTQ）

SAGE-PTQ 将 LLM 量化推到极致：

- 平均 **1.03 weight bits + 0.004 scaling bits** per matrix
- LLaMA-3-8B：WikiText2 困惑度 **6.74**（BiLLM 为 55.8）
- GPU 内存占用不到 BiLLM 的 **50%**
- LLaMA-2-70B：单张 L40 GPU 上解码速度 **1.5x**

**技术路线**：
1. 分布统计分离显著/非显著权重
2. 稀疏图建模估计每层最优分组数
3. 双模量化：显著权重量化多比特，非显著权重二值化
4. 自适应显著性阈值选择

**对 Jetson 部署的启示**：1.03 bits/weight 意味着 70B 模型可压缩到约 9GB（原始 140GB 的 6.4%），理论上可在 Jetson Orin 8GB 上运行。实际部署需结合 SAGE-PTQ + Tangram KV 压缩。

## 技术对比

| 方法 | 核心优化 | 加速比 | 适用场景 | 硬件需求 |
|------|---------|--------|---------|---------|
| CLSA | 跨层索引复用 | 7.6x 解码, 17.1x 吞吐 | 长上下文推理 | 需 KV 共享架构 |
| Tangram | 非均匀 KV 缓存 | 2.6x 吞吐 | 多轮对话 | 通用 GPU |
| VSRAQ | MoE 路由保持 | N/A（精度） | MoE 模型量化 | 量化框架集成 |
| SAGE-PTQ | 超低比特量化 | 1.5x 解码 | 极致压缩部署 | 单张 GPU |

## 对 Hermes/Jetson 技术栈的实践建议

1. **短期**：在 llama.cpp + GGUF 量化基础上，评估 SAGE-PTQ 的二值化方案是否可替代当前 Q4_K_M 量化
2. **中期**：为 Jetson Orin 上的 Ollama 实例引入 Tangram 风格的 KV 缓存预算管理
3. **长期**：探索 CLSA 架构作为本地推理引擎的基础，实现 128K 上下文高效推理

## 参考文献

- arXiv:2606.06467 — You Only Index Once: Cross-Layer Sparse Attention with Shared Routing
- arXiv:2606.06302 — Tangram: Unlocking Non-Uniform KV Cache for Efficient Multi-turn LLM Serving
- arXiv:2606.05688 — Value-and-Structure Alignment for Routing-Consistent Quantization of MoE Models
- arXiv:2606.05429 — SAGE-PTQ: Graph-Guided Ultra-Low-Bit Quantization for LLMs

## 相关笔记
- [KVarN-华为vLLM原生KV-Cache量化后端](2026-06-05-KVarN-华为vLLM原生KV-Cache量化后端.md)
