# LLM 推理服务架构 2026 进化：PD 解耦、vLLM/SGLang 收敛、EAGLE-3/MTP 推测解码与 FP8 量化工业实践

> 来源：zylos.ai 2026 LLM Inference Optimization、Ant Group vLLM/SGLang 社区史、Jonas Geiping LLM Inference Seminar、llm-d 社区博客、arXiv DualPath (2602.21548)
> 主题：LLM 推理优化全栈技术、PD 解耦架构、推测解码新进展、量化选型
> 评分：⭐⭐⭐⭐⭐ (5/5) — 2026 年最完整的 LLM 推理优化工程参考

## 核心结论

**LLM 推理引擎在 2025-2026 年完成了一次范式收敛：vLLM 和 SGLang 从激烈竞争走向功能趋同。** 两者现在都支持连续批处理、PagedAttention、RadixAttention、分块预填充、推测解码、PD 解耦服务、CUDA Graphs，以及 FlashInfer/FlashAttention/DeepGEMM 算子库。DeepSeek 开源的 PD 解耦架构（prefill 和 decode 分配到不同 GPU）已成为大规模推理的工业标准。优化技术按影响力排序：连续批处理(23x) > PagedAttention(2-4x) > FP8 量化(30%) > FlashAttention-3(1.5-2x) > 推测解码(2-3x 延迟)。

## 优化技术栈：按影响力排序

| 排名 | 技术 | 加速倍数 | 原理 |
|------|------|----------|------|
| 1 | 连续批处理 | 最高 23x | 动态插入/移除请求，消除 GPU 空闲 |
| 2 | PagedAttention | 2-4x | OS 虚拟内存式 KV Cache 管理，浪费从 60-80% 降到 <4% |
| 3 | FP8 量化 | 30-33% | Hopper GPU 原生支持，近无损（0.1-0.3% PPL 增加） |
| 4 | FlashAttention-3 | 1.5-2x | H100 上 840 TFLOPS（85% 利用率） |
| 5 | 推测解码 | 2-3x 延迟 | 小模型起草 + 大模型验证，输出数学等价 |

## 量化方法对比矩阵

| 方法 | 位宽 | 目标硬件 | 质量保持率 | 最佳场景 |
|------|------|----------|-----------|----------|
| **FP8** | 8-bit | NVIDIA Hopper+ | ~99% | 生产 GPU 服务（推荐） |
| **AWQ** | 4-bit | GPU | ~95% | 创意写作、代码生成 |
| **GPTQ** | 4-bit | GPU | ~90% | 极致吞吐量 |
| **GGUF** | 2-8 bit | CPU/Apple Silicon | ~92% | 本地/边缘部署 |
| **INT8** | 8-bit | 通用 | ~97-99% | 广泛兼容 |
| **INT4** | 4-bit | 通用 | ~90-95% | 内存受限场景 |

### FP8 量化（生产推荐）

- 近无损质量：PPL 增加 0.1-0.3%
- 比 FP16 快 33%，吞吐量提升 31%
- KV Cache 内存减半
- H100/H200 原生硬件加速

```python
# vLLM FP8 配置
from vllm import LLM
llm = LLM(
    model="meta-llama/Llama-3.1-70B",
    quantization="fp8",
    kv_cache_dtype="fp8"
)
```

### GGUF 量化等级

| 等级 | 位/权重 | 质量 | 推荐场景 |
|------|---------|------|----------|
| Q2_K | ~2.5 | 极端压缩，质量损失大 | 极端资源限制 |
| **Q4_K_M** | ~4.5 | 良好平衡 | **推荐默认** |
| **Q5_K_M** | ~5.5 | 更高质量，仍然快 | **质量优先** |
| Q8_0 | 8.0 | 近无损 | 最高质量需求 |

**关键洞察**：GGUF 在 vLLM 中性能差——GGUF 应配合 llama.cpp/Ollama 使用，而非 vLLM。

### 算子比算法更重要

GPTQ + Marlin 内核比原始 GPTQ 快 2.5x。**相同的量化权重，优化的 CUDA 内核带来 2.5 倍加速**。选量化方案时，不能只看算法，必须考虑配套内核的优化程度。

## vLLM vs SGLang：从竞争到收敛

### 性能基准（100 并发，GPT-OSS-120B）

| 引擎 | 吞吐量 (toks/sec) | 特点 |
|------|-------------------|------|
| **vLLM** | **4,741** | 生产标准，稳定性强 |
| **SGLang** | 3,221 | Agent/RAG 场景更优（RadixAttention） |
| TensorRT-LLM | 1,942 | NVIDIA 硬件极致性能 |

### 功能收敛（2025 末）

两个引擎现在都支持的核心能力：

- ✅ 连续批处理 (Continuous Batching)
- ✅ PagedAttention
- ✅ RadixAttention（KV Cache 复用）
- ✅ 分块预填充 (Chunked Prefill)
- ✅ 推测解码 (Speculative Decoding)
- ✅ PD 解耦服务 (Disaggregated Serving)
- ✅ CUDA Graphs
- ✅ FlashInfer / FlashAttention / DeepGEMM 算子库
- ✅ 张量并行 + 量化

### 各自最佳场景

| 维度 | vLLM | SGLang |
|------|------|--------|
| **定位** | 生产标准 | 高吞吐/RAG/Agent |
| **社区** | PyTorch Foundation（AMD/Google/Meta/NVIDIA 联合治理） | xAI/Skywork/Oracle/LinkedIn 核心 |
| **生产案例** | Amazon Rufus、LinkedIn AI、Microsoft Azure | xAI Grok-2.5、DeepSeek-R1 (AMD MI300X)、LMSYS Arena |
| **吞吐量** | 120-160 req/s | 比 vLLM 高 3.1x（70B 模型） |
| **TTFT** | 50-80ms | 因场景而异 |
| **最佳场景** | 高并发通用服务 | 多轮对话、RAG、Agent 工具链 |

### 194 位交叉贡献者

数据揭示了一个有趣事实：194 位开发者同时为 vLLM 和 SGLang 贡献代码，约占 SGLang 总贡献者的 30%。两个项目同源于 UC Berkeley（导师 Ion Stoica，也是 Spark 和 Ray 的缔造者），技术基因高度同源。

## PD 解耦架构（Prefill-Decode Disaggregation）

### 核心思想

将 LLM 推理的 prefill（预填充）和 decode（解码）阶段分配到不同 GPU：

| 阶段 | 计算特征 | GPU 需求 |
|------|----------|----------|
| **Prefill** | 计算密集（并行处理整个 prompt） | 高算力 GPU |
| **Decode** | 内存带宽密集（逐 token 生成） | 高带宽 GPU |

### 为什么解耦有效

1. **消除干扰**：prefill 和 decode 混在一起时，prefill 的长计算会阻塞 decode 的低延迟需求
2. **独立优化**：每个阶段可以用不同的并行策略和硬件配置
3. **SLO 解耦**：TTFT（首 token 延迟）和 TPOT（每 token 输出时间）可以独立优化

### Mooncake（DeepSeek 推理系统）

DeepSeek 在开源周公布的推理系统核心设计：

- **解耦 KVCache Pool**：prefill 和 decode 之间通过共享 KV Cache 池传递中间状态
- 激进利用解耦和 KV 缓存实现极致性价比
- Google 在 TPU 上也采用类似架构优化首 token 延迟

### llm-d 社区项目

llm-d 基于相同的 vLLM KV Connector API，提供可插拔的缓存方案：

- 前缀缓存复用（跨请求共享公共前缀的 KV Cache）
- KV 卸载到主机内存/远程存储
- 集成 LMCache 等外部系统

### DualPath：Agent 负载的 I/O 瓶颈

arXiv 2602.21548 指出 Agent 工作负载的新瓶颈：

- Agent 场景需要频繁从外部缓存层加载大量 KV-Cache
- 传统单一数据路径成为存储带宽瓶颈
- DualPath 提出双路径并行 I/O 方案

## 推测解码（Speculative Decoding）2025-2026 进展

### 基本原理

1. **起草阶段**：小模型快速生成 K 个候选 token
2. **验证阶段**：大模型单次前向传播验证全部 K 个 token
3. **接受/拒绝**：接受匹配的 token，拒绝并重新生成不匹配的
4. **保证**：输出与大模型单独生成数学等价

### 关键技术演进

| 技术 | 加速倍数 | 核心创新 |
|------|----------|----------|
| 基础推测解码 | 2-3x | 需要独立草稿模型 |
| **EAGLE-3** | 2.5-3x | 轻量预测头，无需独立草稿模型 |
| Apple ReDrafter | 2.8x | 基于 RNN 的草稿头 |
| **PEARL** | **4.43x** | 自适应草稿长度 + 预验证/后验证 |
| **MTP (Multi-Token Prediction)** | 高接受率 | 原生多 token 预测训练目标 |

### MTP：DeepSeek-V3 的原生方案

DeepSeek-V3 在训练时就内置了 MTP（Multi-Token Prediction）模块，推理时直接作为草稿头使用：

- **无需外部草稿模型**：训练时与主模型联合优化
- **高接受率**：草稿和主模型共享表示空间
- vLLM 和 SGLang 均已支持 MTP 推测解码

### vLLM 推测解码配置

```python
# 方案 1：独立草稿模型
llm = LLM(
    model="meta-llama/Llama-3.1-70B",
    speculative_model="meta-llama/Llama-3.1-8B",
    num_speculative_tokens=5,
    speculative_draft_tensor_parallel_size=1
)

# 方案 2：n-gram 推测（无需草稿模型）
llm = LLM(
    model="meta-llama/Llama-3.1-70B",
    speculative_model="[ngram]",
    num_speculative_tokens=5,
    ngram_prompt_lookup_max=4
)
```

### 何时用/何时不用

**适合用**：
- 延迟敏感场景（聊天、实时交互）
- 单用户场景
- 长文本生成任务

**不适合**：
- 高吞吐批量场景（连续批处理更高效）
- 极短输出
- 内存受限环境

## KV Cache 优化：从浪费到高效

### 问题规模

- 70B 模型 + 8K 上下文 = 每请求 ~20GB KV Cache
- 批处理 32 个请求 = ~640GB Cache 内存
- 传统系统内存利用率仅 20-38%

### PagedAttention 革命

借鉴 OS 虚拟内存：

- KV Cache 分成固定大小页面
- 非连续存储 + 间接寻址表
- 细粒度分配/释放
- 支持请求间内存共享

**效果**：浪费从 60-80% 降到 <4%，等效于 GPU 投资翻倍。

### FP8 KV Cache

在 Hopper GPU 上，FP8 KV Cache 比 INT8 更推荐（精度损失更小）：

```python
llm = LLM(
    model="meta-llama/Llama-3.1-70B",
    kv_cache_dtype="fp8"  # vs "auto" (fp16)
)
```

### LMCache 多级缓存

GPU → CPU DRAM → 本地磁盘的三级缓存：
- 重复上下文延迟降低 3-10x
- 支持跨实例缓存共享

## 生产部署选型决策树

```
START
│
├─▶ 生产大规模部署?
│   ├─▶ 高吞吐需求?
│   │   ├─▶ SGLang 或 TensorRT-LLM
│   │   └─▶ vLLM（可靠默认）
│   │
│   └─▶ 否: 本地/边缘?
│       ├─▶ 有 GPU: Ollama 或 llama.cpp
│       └─▶ 仅 CPU: llama.cpp + GGUF
│
└─▶ 开发/原型: Ollama
```

### 量化选型速查

| 场景 | 推荐方案 | 原因 |
|------|----------|------|
| 生产 GPU (Hopper) | **FP8** | 最佳质量/速度平衡 |
| 生产 GPU (Ampere) | **AWQ 或 INT8** | Ampere 无原生 FP8 |
| 高吞吐批量 | **GPTQ + Marlin** | 速度优先 |
| 质量优先 | **AWQ 或 FP8** | 最佳保持率 |
| 本地/笔记本 | **GGUF Q5_K_M** | 通用性强 |
| 移动/边缘 | **GGUF Q4_K** | 内存效率 |

### 生产级 H100 配置示例

```python
from vllm import LLM

llm = LLM(
    model="meta-llama/Llama-3.1-70B",
    tensor_parallel_size=4,
    quantization="fp8",
    kv_cache_dtype="fp8",
    gpu_memory_utilization=0.9,
    enable_prefix_caching=True,    # 前缀复用
    enable_chunked_prefill=True,   # 分块预填充
)
```

## 性能优化清单

- [ ] 启用 FlashAttention（现代框架自动启用）
- [ ] 使用合适量化（Hopper 用 FP8）
- [ ] 配置连续批处理
- [ ] 启用前缀缓存（如果 prompt 共享前缀）
- [ ] 设置 gpu_memory_utilization（0.85-0.95）
- [ ] 大模型使用张量并行
- [ ] 延迟敏感场景考虑推测解码
- [ ] 根据 workload 调优 max_num_seqs

## 常见陷阱

| 陷阱 | 后果 | 正确做法 |
|------|------|----------|
| GGUF 放 vLLM | 性能差 | 用 llama.cpp/Ollama |
| 忽略内核优化 | GPTQ 慢 2.5x | 用 Marlin 内核 |
| 过度分配显存 | KV Cache 溢出 | 留 10-15% 余量 |
| 静态批处理 | GPU 空闲 | 用连续批处理 |
| 跳过校准 | GPTQ 质量差 | 选好校准数据集 |

## 关联

- → 相关：2026-08-12-LLM推理时扩展七大方法分类与工业实践.md
- → 相关：2026-08-11-GPUStack-开源GPU集群管理平台-推理部署与统一调度.md
- → 相关：2026-08-11-主流LLM注意力机制全景科普-四维正交分解与2026代表模型归类.md
- → 相关：2026-08-13-AI-Agent记忆架构2026前沿-MemoryOS-三层存储-Mem0-vs-Letta选型.md


## 相关笔记

- [推测解码2026-SSD并行化与EAGLE3实战](./explore/2026-08-04-推测解码2026-SSD并行化与EAGLE3实战.md) — SSD并行推测解码实战
- [LLM推理优化2026-Speculative-Decoding前沿突破](./2026-08-10-LLM推理优化2026-Speculative-Decoding前沿突破.md) — 推测解码前沿综述
- [本地模型部署-ROI决策框架](./explore/2026-08-04-本地模型部署-ROI决策框架.md) — 部署成本与ROI选型
- [Agent在线KV-Cache压缩-代理查询选型实证](./explore/2026-08-04-Agent在线KV-Cache压缩-代理查询选型实证.md) — KV-Cache压缩实证
