# LLM 推理引擎竞争 2025-2026：vLLM vs SGLang 深度分析

> 来源：INCLUSION AI / Ant Open Source 社区报告 (2025-08) + Zylos Research 推理优化综述 (2026-01) + 行业基准测试
> 日期：2026-08-14

## 核心结论

vLLM 和 SGLang 从激烈竞争走向**功能趋同**——两者现在都支持连续批处理、PagedAttention、RadixAttention、分块预填充、推测解码、分离式服务和 CUDA Graphs。核心差异从"谁功能更多"转向"谁的架构更优雅、CPU调度开销更低、生态更广"。

## 1. 两大引擎起源与核心技术

### vLLM：PagedAttention 革命

| 维度 | 详情 |
|------|------|
| **起源** | 2023年 UC Berkeley，Woosuk Kwon，论文 "Efficient Memory Management for LLM Serving with PagedAttention" |
| **核心创新** | 从操作系统借鉴分页和缓存管理——PagedAttention 实现细粒度 KV Cache 内存管理 |
| **导师** | Ion Stoica（Spark + Ray 创始人）|
| **治理** | 2025年5月转入 PyTorch Foundation，AMD/Google/Meta/NVIDIA 多方治理 |
| **生产部署** | Amazon Rufus, LinkedIn AI, Microsoft Azure |
| **社区** | 740+ 贡献者，27K 月下载，~33% 贡献者来自中国 |

### SGLang：RadixAttention + 零开销调度

| 维度 | 详情 |
|------|------|
| **起源** | 2023年底（比vLLM晚约半年），Lianmin Zheng + Ying Sheng + Liangsheng Yin，LMSYS Org |
| **核心创新** | RadixAttention（基数树缓存，扩展PagedAttention）+ 高效 CPU 调度设计 |
| **技术精髓** | 在请求间保留和复用 KV Cache——当 prefix 匹配时，削减预填充计算 30-50% |
| **导师** | 同为 Ion Stoica（Berkeley）|
| **生产部署** | xAI Grok-2.5, DeepSeek-R1 on AMD MI300X, LMSYS Chatbot Arena（300K+ GPU）|
| **社区** | 更精简，~52% 贡献者来自中国 |

### 交叉贡献

**194 名开发者**同时为 vLLM 和 SGLang 贡献代码——约占 SGLang 总代码贡献者的 **30%**。这解释了两者为何快速趋同。

## 2. 核心技术对比

### PagedAttention vs RadixAttention

```
vLLM PagedAttention（空间优化）:
┌─────┬─────┬─────┬─────┬─────┐
│ Blk │ Blk │ Blk │ Blk │ Blk │  ← 非连续物理块，逻辑→物理映射
│  A  │  A  │  B  │  A  │  B  │  ← 同一请求的块可散布在任意位置
└─────┴─────┴─────┴─────┴─────┘
内存利用率：38% → 96%（2.5-5x 提升）

SGLang RadixAttention（时间优化）:
     [System Prompt]          ← 共享 prefix，复用 KV Cache
      /         \
  [User A]    [User B]        ← 分叉点开始独立计算
   /    \       |
[T1]  [T2]   [T1]              ← 树状结构，prefix 匹配时削减 30-50% 冗余计算
```

- **vLLM 优化空间**（内存利用率）：PagedAttention 将碎片化内存从 38% 利用率提升到 96%
- **SGLang 优化时间**（计算复用）：RadixAttention 在多轮对话中削减 30-50% 冗余预填充计算

### 2025 功能趋同矩阵

| 技术 | vLLM | SGLang | 说明 |
|------|------|--------|------|
| 连续批处理 (Continuous Batching) | ✅ 核心特性 | ✅ 内置 | Orca 论文首创 |
| PagedAttention | ✅ 核心特性 | ✅ 内置 | vLLM 原创 |
| RadixAttention | ✅ 已集成 | ✅ 原创 | SGLang 原创 |
| 分块预填充 (Chunked Prefill) | ✅ | ✅ | 长 prompt 分块处理 |
| 推测解码 (Speculative Decoding) | ✅ | ✅ | 小模型预测→大模型验证 |
| 分离式服务 (Disaggregated Serving) | ✅ | ✅ | prefill/decode 分离到不同 GPU |
| CUDA Graphs | ✅ | ✅ | 消除 kernel launch 开销 |
| FlashInfer / FlashAttention | ✅ | ✅ | 共享算子库 |
| DeepGEMM | ✅ | ✅ | FP8 GEMM 算子 |

## 3. 基准测试数据（2025-2026）

### 100 并发 GPT-OSS-120B 吞吐量

| 引擎 | tokens/sec | 相对性能 |
|------|-----------|----------|
| **vLLM** | **4,741** | 1.00x（基准）|
| **SGLang** | 3,221 | 0.68x |
| **TensorRT-LLM** | 1,942 | 0.41x |

### 各引擎最佳场景基准

| 指标 | vLLM | SGLang | TensorRT-LLM | llama.cpp |
|------|------|--------|--------------|-----------|
| 吞吐量 | 14-24x vs HF | 多调用场景高达 5x | 最佳单请求 | — |
| TTFT | 50-80ms | — | **35-50ms** | — |
| 每token延迟 | — | **4-21ms 最稳定** | — | — |
| vs vLLM (Llama-70B) | — | 高达 3.1x | — | — |
| 并发/秒 | 120-160 req/s | — | — | — |

### 阿里云第三方对比（Qwen 系列）

整体单 GPU/双 GPU 结果**倾向 SGLang**，但结果因硬件/模型/配置而异。

## 4. vLLM V1 重构

2024年，vLLM 遭遇经典软件工程瓶颈：

| 问题 | 详情 |
|------|------|
| **CPU 调度开销** | 第三方研究显示，某些场景下 vLLM 的 CPU 调度开销**超过总推理时间的 50%** |
| **架构债务** | 功能和硬件支持快速扩张导致难以合并独立开发的功能 |
| **解决方案** | 2025年初 V1 基础重构，之后增长重新加速 |

SGLang 同期表现更少的功能/模型/硬件支持，却凭借更可扩展的架构、优秀的 CPU 调度、以及后来的"零开销"调度设计交付了同等强劲的结果。

## 5. 选型决策矩阵

| 场景 | 推荐引擎 | 理由 |
|------|----------|------|
| 高并发 + 吞吐量优先 | **vLLM** | 4,741 tok/s @ 100 并发 |
| Agent 工作流 + RAG | **SGLang** | RadixAttention 复用多轮对话 prefix |
| NVIDIA + 极致性能 | **TensorRT-LLM** | 最佳单请求，B200 上最强 |
| 边缘/便携性 | **llama.cpp** | INT4/INT8，CPU/低配 GPU |
| HuggingFace 生态 | **TGI** | 原生集成 |
| 企业多模型 | **Triton** | 多模型编排 |

### 硬件建议

| 硬件 | 配置 |
|------|------|
| 生产 (H100) | FP8 量化 + FlashAttention-3 + vLLM/SGLang |
| 边缘 (RTX 40xx) | llama.cpp + INT4/INT8 |
| 次世代 (Blackwell) | NVFP4 + FA-4 + TensorRT-LLM |

## 6. 推理优化技术全景

### KV Cache 优化

传统方法预分配连续内存，60-80% 内存浪费。PagedAttention 方案：
- 将 KV Cache 分成固定大小块（blocks）
- 非连续物理存储 + 逻辑→物理映射表
- 内存利用率 38% → 96%
- 支持 copy-on-write 共享（beam search/parallel sampling 零拷贝）

### 连续批处理 vs 静态批处理

```
静态批处理：
Req1: [████████████████]  ← 等最慢的请求
Req2: [██████]            ← 完成后空等
Req3: [████████████████████████]  ← 拖慢整批

连续批处理（Continuous Batching）：
Req1: [████████████████]
Req2: [██████][新请求...]
Req3: [████████████████████████]
         ↑ 每个iteration级别动态插入/移除请求
```

## 7. 对 Jetson Orin 边缘部署的借鉴

当前 Hermes Agent 运行在 Jetson Orin Nano Super（67 TOPS, 8GB unified memory），本地推理用 Ollama。以下是从 vLLM/SGLang 中可借鉴的优化思路：

1. **KV Cache 是内存瓶颈**：Jetson unified memory 架构下，KV Cache 直接吃系统 RAM。8GB 环境下 7B 模型 + 长上下文可能 OOM
2. **PagedAttention 思路适用于边缘**：减少 KV Cache 碎片化可提升可服务序列数
3. **RadixAttention 的 prefix 复用在 Agent 场景价值极高**：Hermes 的系统提示+MEMORY+USER profile 是固定 prefix，每次请求重复计算。RadixAttention 可削减这部分计算
4. **推测解码适合边缘**：小模型预测 + 大模型验证，在延迟敏感场景（语音 TTS/STT）有应用价值
5. **CPU 调度开销在边缘更致命**：Jetson CPU 核心有限，vLLM V1 的"零开销调度"思路值得 Ollama 借鉴

### 关键引用

- vLLM 论文：*"Efficient Memory Management for Large Language Model Serving with PagedAttention"* (SOSP 2023)
- SGLang 论文：*"SGLang: Efficient Execution of Structured Language Model Programs"*
- vLLM V1 发布博客：blog.vllm.ai/2025/01/27/v1-alpha-release.html
- CPU 调度开销分析：mlsys.wuklab.io/posts/scheduling_overhead/
- 社区报告：inclusion-ai.org/blog/llm-landscape-vllm-sgl


## 相关笔记

- [LLM推理引擎2026格局-SGLang崛起与架构收敛](./2026-08-05-LLM推理引擎2026格局-SGLang崛起与架构收敛.md) — 同主题前篇，SGLang 架构深度解析
- [LLM推理加速2026-MTP与推测解码实战全景](./2026-07-02-LLM推理加速2026-MTP与推测解码实战全景.md) — 推理加速技术，两大引擎均支持
- SSD-KV-Cache-oMLX本地部署前沿（~/explore）— KV Cache 优化，推理引擎核心组件
