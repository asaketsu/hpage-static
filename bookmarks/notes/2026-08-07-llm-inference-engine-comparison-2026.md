---
title: "LLM 推理引擎 2026 对比：vLLM vs SGLang vs LMDeploy vs TensorRT-LLM"
date: 2026-08-07
category: LLM Inference
tags: [vLLM, SGLang, LMDeploy, TensorRT-LLM, inference-optimization]
source: ["premai.io/blog/vllm-vs-sglang-vs-lmdeploy", "deploybase.ai/articles/best-llm-inference-engine", "yottalabs.ai/post/best-llm-inference-engines-in-2026"]
---

# LLM 推理引擎 2026 对比：vLLM vs SGLang vs LMDeploy vs TensorRT-LLM

## 核心发现与内容整理

2026 年开源 LLM 推理引擎格局已高度成熟，五大引擎各有明确生态位。核心结论：**推理引擎选择比模型选择更重要**——选错引擎会导致硬件利用率瓶颈。

### 1. 性能基准总览（H100 GPU, Llama 3.1 8B）

| 引擎 | 吞吐量 (tok/s) | TTFT (ms) | 核心技术 | 最适场景 |
|------|---------------|-----------|---------|---------|
| **SGLang** | ~16,200 | 80-120 | RadixAttention | 多轮对话/Agent 工作流 |
| **LMDeploy** | ~16,100 | 最低 | TurboMind (C++) | 量化模型/内存受限 |
| **vLLM** | ~12,500 | 150-200 | PagedAttention | 通用生产/生态兼容 |
| **TensorRT-LLM** | ~4,500 (70B) | 150-200 | 编译优化 | NVIDIA 极限性能 |
| **TGI** | ~2,500 (70B) | 200-300 | HF 生态集成 | HF 原生用户 |

**关键数字**：SGLang/LMDeploy 比 vLLM 快 **29%**，在百万日请求规模下 ≈ 每月节省 $15,000 GPU 成本。

### 2. 四大引擎深度解析

#### vLLM — 生产标准（PagedAttention）

**核心创新**：将 KV cache 当作虚拟内存管理。固定大小页（通常 16 token/页）按需分配，序列需要更多空间时分配下一个可用页，无需物理连续。

**效果**：内存利用率从 ~30% 提升到 >90%，吞吐量提升 2-4x。

**适用场景**：
- 优先稳定性而非极限优化
- 单轮交互为主的工作负载
- 需要广泛模型兼容性
- 使用 Ray/Kubernetes 集成

**配置最佳实践**：
```python
llm = LLM(
    model="meta-llama/Llama-3.1-70B",
    tensor_parallel_size=4,
    gpu_memory_utilization=0.95,  # 7B:0.95, 13B:0.85, 70B:0.90
    enable_chunked_prefill=True,
    enable_prefix_caching=True,
    quantization="fp8",
    kv_cache_dtype="fp8"
)
```

#### SGLang — Agent/多轮之王（RadixAttention）

**核心创新**：传统引擎在请求完成后丢弃 KV cache。SGLang 将缓存前缀存储在 **Radix Tree**（基数树）中，新请求匹配到相同前缀时直接复用已计算结果。

**缓存命中率因工作负载而异**：
- Few-shot 学习（共享示例）：85-95%（vs PagedAttention 15-25%）
- 多轮对话（历史上下文）：75-90%（vs 10-20%）
- 代码分析（公共模式）：60-80%（vs 5-15%）
- 无共享的单请求：0%（等效性能）

**v0.4 关键升级**：零开销批调度器，CPU 调度开销 <2%（之前 15-25%）。

**结构化输出**：内置压缩有限状态机进行约束解码。JSON 解码速度比非约束生成 + 后处理快 **3x**。

**生态规模**：已部署于 400,000+ GPU，用户包括 xAI/AMD/NVIDIA/LinkedIn/Cursor。

**SGLang 有状态计算模型**（一次调用替代多次 API 往返）：
```python
sgl.gen(name="reasoning", max_tokens=500)
sgl.gen(name="final_answer", max_tokens=200)
# RAG、多步推理、结构化输出合并为一次调用
```

#### LMDeploy — 量化模型之王（TurboMind）

**核心创新**：纯 C++/CUDA 后端（vLLM/SGLang 是 Python-first），无解释器开销。

**关键性能**：
- Int4 推理比 FP16 快 **2.4x**
- 70B 模型可量化到单 GPU
- 请求吞吐量比 vLLM 高 **1.8x**
- TTFT 全引擎最低

**适用场景**：量化模型服务（Int4/Int8/AWQ/GPTQ）、内存受限部署、最低 TTFT 需求。

**限制**：TurboMind 针对 NVIDIA GPU 优化，ROCm 支持成熟度较低。

#### TensorRT-LLM — NVIDIA 极限性能

**核心**：为特定 GPU（A100/H100/L4/L40S）生成编译代码——kernel 融合 + tensor 优化 + 内存布局调优。

**性能**：H100 上 Llama 70B 达 4,500 tok/s，所有引擎最高。

**代价**：
- 编译时间 30-60 分钟
- 编译后模型锁定到特定 GPU 类型和 CUDA 版本
- 更新模型需重新编译
- LangChain/LlamaIndex 需自定义适配器

**适用**：大规模生产环境中挤压极限性能的团队。20-30% 吞吐增益是否值得编译开销需要评估。

### 3. 引擎收敛趋势

vLLM 和 SGLang 正在功能趋同：两者都已支持 Continuous Batching、PagedAttention、RadixAttention、Chunked Prefill、Speculative Decoding、Disaggregated Serving、CUDA Graphs，以及 FlashInfer/FlashAttention/DeepGEMM 算子库。差异化正在缩小，未来竞争焦点转向**特定工作负载优化深度**。

### 4. FP8 量化已成为 Hopper GPU 新默认

2026 年 FP8 在 H100/H200 上成为标准——近乎无损 + 30%+ 速度提升。GGUF 在 vLLM 中性能较差，应使用 llama.cpp。

## 查询拓展（待深入）

1. **Disaggregated Serving（分离式服务）**：Prefill 和 Decode 分离到不同 GPU 集群，2026 年成为新范式，具体架构和收益待深入
2. **Speculative Decoding 的最新进展**：2026 年声称 2-3x 加速，但不同 draft model 策略（自回归/前瞻/多头）的优劣对比
3. **Jetson 边缘部署适配**：当前 Hermes 跑在 Jetson Orin Nano 上，TensorRT-LLM 的 ARM64 + Jetson 兼容性如何？LMDeploy 的 TurboMind 是否支持 Jetson？
4. **多模型路由策略**：7B→简单查询，70B→复杂查询的智能路由（DeployBase 提到吞吐提升 40-60%），生产中如何实现？
5. **KV Cache 量化**：fp8 kv_cache_dtype 的质量影响量化，以及不同量化方案（INT4 KV vs FP8 KV）的精度/速度权衡

## 归纳总结（一页速查）

```
2026 LLM 推理引擎选型决策树
┌──────────────────────────────────────────────┐
│  通用生产, 广泛兼容？      → vLLM             │
│  多轮对话, Agent 工作流？  → SGLang           │
│  量化模型, 内存受限？      → LMDeploy         │
│  NVIDIA 极限性能？         → TensorRT-LLM     │
│  CPU/边缘设备？            → llama.cpp        │
│  HF 生态原生？             → TGI              │
└──────────────────────────────────────────────┘

关键性能数字 (H100, Llama 3.1 8B)：
- SGLang: 16,200 tok/s, TTFT 80-120ms
- LMDeploy: 16,100 tok/s, TTFT 最低
- vLLM: 12,500 tok/s, TTFT 150-200ms
- 差距 29% = 百万日请求月省 $15K

量化方案选择：
- Hopper GPU (H100/H200) → FP8 (新默认)
- 通用 GPU → AWQ/GPTQ Int4
- GGUF → 仅用 llama.cpp (vLLM 中性能差)

vLLM 内存调优：
- 7B:  gpu_memory_utilization=0.95
- 13B: gpu_memory_utilization=0.85
- 70B: gpu_memory_utilization=0.90
```

## 趋势判断

1. **SGLang 正在接管 Agent 工作负载**：RadixAttention 对多轮对话/共享前缀的天然优势，使 SGLang 在 AI Agent 场景（如 Hermes 的多轮工具调用）中成为最优选。400K+ GPU 部署量验证了这一趋势
2. **引擎功能趋同 → 竞争转向工作负载特化**：vLLM 和 SGLang 的核心功能集已高度重叠，未来差异化在于"谁对特定场景（Agent/RAG/代码）优化更深"，而非"谁的功能更全"
3. **FP8 成为量化新标准**：Hopper GPU 普及后，FP8 取代 INT4/INT8 成为首选量化方案。这对 Jetson（无 FP8 硬件支持）意味着边缘部署将继续依赖 INT4/GGUF
4. **分离式服务（Prefill-Decode 分离）是下一代架构**：将计算密集的 Prefill 和内存密集的 Decode 分配到不同 GPU 集群，是突破单 GPU 资源利用瓶颈的关键方向
5. **编译式引擎（TensorRT-LLM）的天花板**：编译开销（30-60min）使其难以适应快速迭代的研发场景，但在超大规模稳定生产中仍有不可替代的价值

## 关联分析与趋势判断

### 与 Jetson Orin 平台的关联

Jetson Orin Nano（Hermes 运行平台）的约束：
- GPU: Ampere 架构（非 Hopper）→ 不支持 FP8 硬件加速
- 显存: 8GB（Super 模式）→ 70B 不可能，7B-13B 需重度量化
- 算力: 67 TOPS (INT8) / 20 TOPS (FP16)

**Jetson 适配结论**：
| 引擎 | Jetson 可行性 | 说明 |
|------|-------------|------|
| llama.cpp | ✅ 最佳 | GGUF 量化，CPU+GPU 混合，已有部署经验 |
| LMDeploy | ⚠️ 待验证 | TurboMind 可能不直接支持 Jetson 的 ARM64+GPU 组合 |
| vLLM | ⚠️ 有限 | 内存占用高，8GB 显存紧张 |
| SGLang | ⚠️ 待验证 | 对 Jetson 的 CUDA 支持未验证 |
| TensorRT-LLM | ⚠️ 可行 | Jetson 有 TensorRT 支持，但编译流程复杂 |

### 与 Hermes Agent 架构的关联

Hermes 当前主要通过云端 API（zai/GLM）调用 LLM，本地推理仅用于 Ollama（Jetson）。如果考虑本地部署增强：
- **SGLang 的 RadixAttention 对 Hermes 的多轮工具调用极为有利**——大量工具调用的 system prompt 和 skill 描述是共享前缀，缓存命中率可达 75-90%
- **结构化输出约束解码**对 Hermes 的 JSON tool_call 解析有直接价值（SGLang JSON 解码 3x 加速）
- 但 Jetson 硬件限制使本地 SGLang 部署不现实，这些优势更适合在云端推理服务中使用

### 与量化交易系统的关联

量化策略的 LLM 推理（如 LLM 因子挖掘、新闻情感分析）场景：
- 高频调用、共享 system prompt → **SGLang RadixAttention 最优**
- 批量回测、非实时 → vLLM 的高吞吐批处理更合适
- 因子描述结构化提取 → SGLang 的 JSON 约束解码直接适用

### 与现有 Skill 的关联

- `llm-inference-optimization` skill 可补充 SGLang RadixAttention 的详细配置指南和缓存命中率数据
- `llm-inference-deploy` skill 的量化方案选择需更新：FP8 在 Hopper 上已是新默认
- `jetson-tensorrt-deploy` skill 可补充 Jetson 上各引擎的可行性矩阵

## 出处

- vLLM vs SGLang vs LMDeploy (PreMAI) — https://www.premai.io/blog/vllm-vs-sglang-vs-lmdeploy-fastest-llm-inference-engine-in-2026
- Best LLM Inference Engines 2026 (DeployBase) — https://deploybase.ai/articles/best-llm-inference-engine
- Best LLM Inference Engines (Yotta Labs) — https://www.yottalabs.ai/post/best-llm-inference-engines-in-2026-vllm-tensorrt-llm-tgi-and-sglang-compared
- LLM Inference Optimization 2026 (Zylos) — https://zylos.ai/research/2026-01-15-llm-inference-optimization
- Community Stories of vLLM and SGLang — https://medium.com/@ant-oss/the-community-stories-of-vllm-and-sgl-d4675e77da6a
- PremAI Open-source Benchmarks — https://github.com/premAI-io/benchmarks

## 相关笔记

- [LLM推理引擎2026格局-SGLang崛起与架构收敛](2026-08-05-LLM推理引擎2026格局-SGLang崛起与架构收敛.md)
- [端侧LLM推理与持续学习-2026前沿论文综述](2026-08-09-端侧LLM推理与持续学习-2026前沿论文综述.md)
- [LLM微调从能力增强到成本工程-2026决策指南](2026-08-07-LLM微调从能力增强到成本工程-2026决策指南.md)

---
