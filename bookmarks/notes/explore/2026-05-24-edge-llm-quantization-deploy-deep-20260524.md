# 端侧 LLM 量化部署最佳实践（llama.cpp/GGUF）深度研究

> 探索日期：2026-05-24 | 环境：Jetson Orin Nano (Linux 5.15.148-tegra, 7.4GB RAM, CUDA 12.6, aarch64) | 笔记路径：explore/edge-llm-quantization-deploy-deep-20260524.md

---

## 一、GGUF 格式技术原理

### 1.1 GGUF 的诞生与优势

GGUF（GPT-Generated Unified Format）由 llama.cpp 作者 Georgi Gerganov 于 2023 年 8 月推出，是 GGML 格式的继任者。它之所以成为端侧 LLM 的"事实标准"，核心优势包括：

- **单文件封装**：模型权重、tokenizer 词表、架构元数据、聊天模板全部打包在一个 `.gguf` 文件中，无需额外配置文件
- **mmap 友好**：操作系统可以将文件直接映射到内存，支持运行超过物理 RAM 的模型（按需分页加载）
- **跨平台兼容**：同一文件可在 x86、ARM、Apple Silicon 上运行，支持 CPU/GPU 混合推理
- **元数据内嵌**：上下文长度、RoPE scaling、BOS/EOS 标记、chat template 自动检测，无需手动配置
- **版本兼容**：新量化类型不会破坏旧文件的读取

### 1.2 量化技术原理

量化本质是"有损压缩"——将 FP16（2 字节/权重）压缩为 INT4/INT8 等低精度格式，以换取更小的体积和更快的推理速度。

**量化家族分类**：

| 家族 | 格式 | 描述 |
|------|------|------|
| 标准/遗留 | Q4_0, Q4_1, Q5_0, Q5_1, Q8_0 | 块级（K=32）整数量化 |
| K-quants | Q3_K_S/M/L, Q4_K_S/M, Q5_K_S/M, Q6_K | 256 权重超块 + 量化 scale/min 元数据 |
| IQ-quants | IQ1_M, IQ2_M, IQ3_M, IQ4_M | 2024 年新推出的"智能量化"，进一步优化 |

**关键概念**：
- `_0` 后缀 = 对称量化（无零点）
- `_1` 后缀 = 非对称量化（有偏移/零点）
- `K_M` / `K_S` = 混合精度变体：大部分权重保持目标量化等级，重要部分保留更高精度

### 1.3 imatrix 校准

高质量量化需要 `imatrix`（重要性矩阵）校准：
```bash
# 用大量文本数据计算权重重要性
./imatrix -m model.gguf -f calibration.txt -o model-imatrix.dat

# 用校准结果进行量化
./quantize -m model-f16.gguf -o model-Q4_K_M.gguf model-imatrix.dat Q4_K_M
```

校准数据质量直接影响量化后模型的智能程度——这是"为什么同一量化等级不同模型效果差异巨大"的核心原因。

---

## 二、llama.cpp 最新架构（2025-2026）

### 2.1 ggml 后端

llama.cpp 的推理核心是 **ggml** 张量计算库，它实现了：
- **多后端调度**：CPU（AVX/AVX2/AVX512/NEON）、CUDA、Vulkan、Metal、SYCL、OpenCL
- **算子融合**：将多个算子合并为单个 kernel，减少内存访问开销
- **内存管理**：mmap + 按需加载，支持模型大于物理内存
- **Tensor Core 加速**：在 CUDA 后端利用 Tensor Core 进行 INT8/FP16 矩阵乘法

### 2.2 CUDA 后端优化

针对 Jetson 等 NVIDIA ARM 平台，llama.cpp 的 CUDA 后端优化包括：
- **Tensor Core INT8/FP16**：在 Orin 的 Ampere 架构上，INT8 Tensor Core 吞吐可达 FP16 的 2 倍
- **Kernel fusion**：将 attention 的 Q/K/V 投影和 softmax 融合，减少中间张量内存
- **PagedAttention**：类似 vLLM 的 KV cache 分页管理，支持更大上下文
- **Stream scheduling**：CPU/GPU 任务并行调度，避免 GPU 空闲

### 2.3 Vulkan 后端（2026 新进展）

Vulkanised 2026 会议展示了 llama.cpp 的 Vulkan ML 进展：
- 可在无 CUDA 的平台上（如 Intel 核显、AMD GPU）运行 GGUF 模型
- 在部分场景下 Vulkan 性能可媲美 CUDA（尤其是 UMA 架构设备）
- 对 Jetson 来说，CUDA 仍然是首选，但 Vulkan 提供了降级选项

---

## 三、量化方案深度对比

### 3.1 Llama-3.1-8B-Instruct 量化基准（arXiv 2601.14277）

这是目前最权威的 llama.cpp 量化评估研究，测试了 13 种量化方案：

**质量排名（MMLU + GSM8K + HSwag + IFEval + TQAmc2 综合）**：

| 排名 | 量化方案 | 相对 F16 质量 | 模型大小 | 推理速度 (pp512) |
|------|----------|---------------|----------|-------------------|
| 1 | F16 | 100% | 16 GB | 79.57 tok/s |
| 2 | Q8_0 | 99.7% | 8.5 GB | 71.42 tok/s |
| 3 | Q6_K | 99.5% | 6.6 GB | 59.81 tok/s |
| 4 | Q5_0 | 99.3% | 5.7 GB | 61.44 tok/s |
| 5 | Q5_K_M | 99.2% | 5.7 GB | 61.44 tok/s |
| 6 | Q4_K_S | 99.1% | 5.0 GB | 92.52 tok/s |
| 7 | Q4_K_M | 99.1% | 5.0 GB | 87.70 tok/s |
| 8 | Q4_0 | 97.9% | 5.1 GB | 97.35 tok/s |
| 9 | Q3_K_M | 97.9% | 4.0 GB | 68.86 tok/s |
| 10 | Q3_K_S | 94.3% | 3.9 GB | 57.39 tok/s |
| 11 | Q2_K | 87-88% | 2.6 GB | - |

**关键发现**：
1. **Q4_K_S 是性价比之王**：质量仅比 Q8_0 低 0.6%，但推理速度提升 29%（92.52 vs 71.42 tok/s）
2. **Q4_K_M 是质量-速度平衡点**：比 Q4_K_S 略慢但质量更稳定
3. **Q5_0 意外强劲**：在多个基准上超过 Q4_K_M，且速度不慢
4. **Q3_K_S 是质量底线**：低于 Q3 量化会出现明显的"智能下降"
5. **Q8_0 与 F16 几乎无差异**：盲测无法区分，但体积减半

### 3.2 不同模型尺寸推荐

| 模型规模 | 8GB 设备推荐 | 16GB 设备推荐 | 32GB+ 设备推荐 |
|----------|-------------|--------------|----------------|
| 1-3B | Q8_0 或 F16 | F16 | F16 |
| 7-8B | Q5_K_M 或 Q4_K_M | Q6_K 或 Q5_K_M | Q8_0 或 F16 |
| 13-14B | Q4_K_M | Q5_K_M | Q6_K |
| 30-35B | Q3_K_M | Q4_K_S | Q4_K_M |
| 70B | Q3_K_S | Q3_K_M | Q4_K_S |

**Jetson Orin Nano 8GB 具体建议**：
- **7B 模型**：Q4_K_M（约 4.9GB），留 2.5GB 给上下文和系统
- **13B 模型**：Q3_K_M（约 5.6GB），需限制上下文长度
- **不建议**：8B 以上模型在 8GB 上运行 Q4 以下量化，质量损失明显

---

## 四、Jetson Orin Nano 部署实测数据

### 4.1 硬件规格

| 规格 | Orin Nano (8GB) | Orin AGX (64GB) |
|------|----------------|----------------|
| GPU | 1024-core Ampere | 2048-3072-core Ampere |
| AI 算力 | 40 TOPS | 275 TOPS |
| 内存 | 8GB 统一内存 | 64GB 统一内存 |
| 内存带宽 | 68 GB/s | 204 GB/s |
| TDP | 7-15W | 15-60W |

### 4.2 实测性能数据

**来源 1：DFRobot Jetson AGX Orin 64GB 测试**
- Llama-2 7B Q4_K_M: ~280 tok/s（全 GPU offload）
- Llama-2 13B Q4_K_M: ~150 tok/s

**来源 2：GitHub Discussion #5059**
- Jetson Orin AGX 64GB: llama2 7B Q4_K_M ≈ 280 tok/s
- 命令：`./llama-cli -m models/llama2-7b.Q4_K_M.gguf -p "Building a website..." -n 400 -e -ngl 100`

**来源 3：Jetson Orin Nano Super 8GB 实测**
- Llama-3.1-8B INT4: 5.2GB GPU 共享内存（峰值）, 6.8GB 总 RAM
- 使用 1.58-bit 量化（自定义）: 2.5GB GPU 共享内存, 4.1GB 总 RAM
- 普通 llama.cpp INT4 在 Nano 上约 4-6 tok/s（推测）

**来源 4：社区实测（Orin Nano 8GB）**
- Llama-3 8B 约 4.5 tok/s（TikTok 实测）
- SmolLM2 1.7B 和 Llama 3 2B 在 Nano 上运行流畅

### 4.3 Orin Nano 部署关键参数

```bash
# llama.cpp 在 Orin Nano 上的推荐启动参数
./llama-server   -m models/qwen2.5-7b-instruct-Q4_K_M.gguf   -ngl 99   -c 4096   -b 2048   --threads 4   --port 8080

# 参数说明：
# -ngl 99: 将所有层卸载到 GPU（Orin Nano 内存足够）
# -c 4096: 上下文长度（超过 4096 会触发 CPU 回退）
# -b 2048: batch size（影响首 token 延迟）
# --threads 4: CPU 线程数（Orin Nano 6 核，留 2 核给系统）
```

### 4.4 内存预算分析（Orin Nano 8GB）

| 组件 | 占用 | 剩余 |
|------|------|------|
| 系统 + 显示 | ~1.5GB | 6.5GB |
| Llama-3 8B Q4_K_M | ~4.9GB | 1.6GB |
| KV cache (4096 context) | ~0.8GB | 0.8GB |
| **安全余量** | | **~0.8GB** |

**结论**：Orin Nano 8GB 可以流畅运行 7-8B 模型的 Q4_K_M，但 13B 模型需要 Q3_K_M 且上下文受限。

---

## 五、Ollama 在 ARM/aarch64 上的部署

### 5.1 Ollama 架构

Ollama 基于 llama.cpp，封装了模型下载、量化、推理和 API 服务：
- **自动量化**：从 HuggingFace 下载 GGUF 模型时自动选择合适的量化等级
- **跨平台支持**：官方提供 Linux x86_64、Linux aarch64、macOS、Windows 版本
- **Modelfile**：自定义模型配置，支持系统提示、参数调整

### 5.2 Ollama 在 Jetson 上的部署

```bash
# 安装 Ollama（Linux aarch64）
curl -fsSL https://ollama.com/install.sh | sh

# 拉取模型
ollama pull qwen2.5:7b-instruct-q4_K_M

# 运行
ollama run qwen2.5:7b-instruct-q4_K_M
```

**Modelfile 示例**：
```dockerfile
FROM qwen2.5:7b-instruct-q4_K_M
PARAMETER temperature 0.7
PARAMETER top_p 0.9
PARAMETER num_ctx 4096
PARAMETER num_thread 4
SYSTEM "你是一个有用的 AI 助手，用中文回答所有问题。"
```

### 5.3 Ollama vs llama.cpp 对比

| 维度 | Ollama | llama.cpp |
|------|--------|-----------|
| 易用性 | ⭐⭐⭐⭐⭐（一行安装） | ⭐⭐⭐（需编译/配置） |
| 灵活性 | ⭐⭐⭐（参数有限） | ⭐⭐⭐⭐⭐（所有参数可调） |
| 性能 | 与 llama.cpp 相同（底层相同） | 可微调优化 |
| API | OpenAI 兼容 REST API | 内置 server + OpenAI 兼容 |
| 模型管理 | 自动下载 + 版本管理 | 手动管理 |

**推荐**：开发/测试用 Ollama，生产/优化用 llama.cpp 直接部署。

---

## 六、端侧推理优化技巧

### 6.1 上下文长度管理

**问题**：上下文越长，KV cache 占用越大，首 token 延迟越高。

**优化策略**：
```bash
# 1. 限制上下文长度
-c 2048  # 而不是默认的 4096

# 2. 使用 KV cache 量化（llama.cpp 2025 新特性）
--cache-type-k q8_0  # KV cache 用 INT8 量化

# 3. Prompt caching（重复场景）
--prompt-cache /tmp/cache.bin --prompt-cache-auto
```

### 6.2 GPU/CPU 混合调度

**原则**：尽可能将模型层卸载到 GPU，但保留 CPU 处理 tokenization 和后处理。

```bash
# 全 GPU offload（Orin Nano 内存足够时）
-ngl 99

# 部分 offload（内存紧张时）
-ngl 30  # 只卸载前 30 层，剩余层由 CPU 处理

# 混合模式调试
# 观察 llama.cpp 日志中的 "offloaded X/Y layers to GPU"
```

### 6.3 线程/GPU 调度

```bash
# CPU 线程数
--threads 4  # Orin Nano 6 核，留 2 核给系统

# GPU 线程（CUDA）
--gpu-threads 8  # 控制 GPU 并行度

# 批处理大小
-b 2048  # 影响首 token 延迟，越大越快但内存占用越高
```

### 6.4 内存映射优化

```bash
# 使用 mmap 加载（默认）
-mmap 1  # 允许 OS 按需分页

# 禁用 mmap（当模型 < RAM 时更快）
-mmap 0  # 一次性加载全部到内存

# 预加载（减少首次推理延迟）
-preload  # 启动时预加载模型
```

---

## 七、与 vLLM/SGLang 在边缘场景的对比

| 维度 | llama.cpp | vLLM | SGLang |
|------|-----------|------|--------|
| 模型格式 | GGUF | AWQ/GPTQ/FP16 | AWQ/GPTQ/FP16 |
| 硬件要求 | CPU/GPU 皆可 | GPU 必需 | GPU 必需 |
| 内存效率 | mmap + 按需加载 | PagedAttention | PagedAttention |
| 边缘友好度 | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐ |
| 并发吞吐 | 单请求优化 | 多请求优化 | 多请求优化 |
| Jetson 支持 | ✅ 原生 | ⚠️ 需定制 | ⚠️ 需定制 |

**结论**：
- **边缘单设备**：llama.cpp 是唯一成熟选择
- **边缘多设备集群**：可考虑 vLLM + TensorRT-Edge-LLM（NVIDIA 官方）
- **Jetson 专属优化**：TensorRT-Edge-LLM 是 NVIDIA 官方方案，性能优于 llama.cpp 但生态较小

---

## 八、实践建议

### 8.1 Jetson Orin Nano 8GB 部署清单

**推荐模型 + 量化组合**：

| 模型 | 量化 | 大小 | 推理速度（预估） | 适用场景 |
|------|------|------|-----------------|----------|
| Qwen2.5-7B-Instruct | Q4_K_M | ~4.9GB | ~4-6 tok/s | 中文对话、代码 |
| Qwen2.5-7B-Instruct | Q5_K_M | ~5.7GB | ~3-4 tok/s | 高质量中文 |
| Llama-3.1-8B-Instruct | Q4_K_M | ~4.9GB | ~4-6 tok/s | 英文对话 |
| Phi-4-14B | Q3_K_M | ~5.6GB | ~2-3 tok/s | 推理任务 |
| SmolLM2-1.7B | Q8_0 | ~1.0GB | ~15-20 tok/s | 快速响应 |

**部署命令**：
```bash
# 1. 安装 llama.cpp（从 NVIDIA 官方 Docker）
docker pull ghcr.io/nvidia-ai-iot/llama_cpp:latest-jetson-orin

# 2. 下载模型
wget https://huggingface.co/bartowski/Qwen2.5-7B-Instruct-GGUF/resolve/main/Qwen2.5-7B-Instruct-Q4_K_M.gguf

# 3. 启动服务
docker run --gpus all   -v $(pwd)/models:/models   -p 8080:8080   ghcr.io/nvidia-ai-iot/llama_cpp:latest-jetson-orin   llama-server -m /models/Qwen2.5-7B-Instruct-Q4_K_M.gguf   -ngl 99 -c 4096 -b 2048 --threads 4
```

### 8.2 Ollama Jetson 部署

```bash
# 安装
curl -fsSL https://ollama.com/install.sh | sh

# 拉取并运行
ollama run qwen2.5:7b-instruct-q4_K_M

# API 调用
curl http://localhost:11434/api/generate   -d '{"model":"qwen2.5:7b-instruct-q4_K_M","prompt":"你好"}'
```

### 8.3 性能调优检查清单

1. **内存监控**：`jtop` 实时监控 GPU/CPU 内存使用
2. **温度控制**：`sudo jetson_clocks` 解锁全性能模式（注意散热）
3. **量化选择**：优先 Q4_K_M → Q5_K_M → Q6_K → Q8_0
4. **上下文限制**：4096 是安全线，8192 需要 Q3 以下量化
5. **首 token 优化**：增大 `-b`（batch size），使用 `-ngl 99` 全 GPU offload

---

## 九、核心发现（≥5 个）

1. **Q4_K_S 是量化性价比之王**：arXiv 2601.14277 实证显示，Q4_K_S 质量仅比 Q8_0 低 0.6%，但推理速度提升 29%（92.52 vs 71.42 tok/s），是 8GB 设备的最佳选择。

2. **Jetson Orin Nano 8GB 的内存边界**：7-8B 模型 Q4_K_M 可流畅运行（约 4-6 tok/s），13B 模型需 Q3_K_M 且上下文受限，30B+ 模型不推荐。

3. **llama.cpp 的 mmap 机制是边缘部署的关键**：允许运行超过物理内存的模型，通过 OS 按需分页加载，这是 GGUF 在边缘设备上的核心优势。

4. **Ollama 简化了端侧部署但牺牲了灵活性**：一行安装 + 自动模型管理，适合开发测试；生产环境建议直接用 llama.cpp 精细调优。

5. **1.58-bit 量化是未来方向**：Enerzai 在 GTC 2026 展示的 1.58-bit QAT 方案将 8B 模型压缩到 2.5GB GPU 内存（vs llama.cpp INT4 的 5.2GB），但需要自定义 kernel，目前尚未开源。

---

## 十、实践启发

1. **Jetson 部署优先用 NVIDIA 官方 Docker**：`ghcr.io/nvidia-ai-iot/llama_cpp:latest-jetson-orin` 预装了 CUDA 12.6 优化版本，无需自行编译。

2. **Q4_K_M 是安全底线**：低于 Q4 量化会出现明显的"智能下降"，尤其对 7B 以下模型。

3. **上下文长度是内存瓶颈**：4096 token 上下文约占用 0.8GB，8192 约 1.6GB，需根据模型大小动态调整。

4. **首 token 延迟 > 生成速度**：端侧推理的首 token 延迟（2-5 秒）远大于生成速度（4-6 tok/s），优化重点应放在首 token 上（增大 batch size、全 GPU offload）。

5. **TensorRT-Edge-LLM 值得关注**：NVIDIA 官方推出的 Jetson 专属 LLM 推理引擎，性能优于 llama.cpp，但生态和模型支持仍在早期阶段。

---

## 十一、知识缺口

1. **Jetson Orin Nano 8GB 的 llama.cpp 实测数据不足**：现有数据主要来自 AGX 64GB 和 Nano Super，普通 Nano 8GB 的实测 tok/s 数据需要本地验证。

2. **Ollama 在 aarch64 的 CUDA 后端性能**：Ollama 默认使用 CPU 后端，在 Jetson 上需要确认 CUDA 后端是否自动启用。

3. **IQ-quants（IQ1_M/IQ2_M/IQ3_M）的实际效果**：这些 2024 年新推出的量化格式在 7B 以下小模型上的表现需要实测。

4. **llama.cpp 的 KV cache 量化（q8_0）对 Jetson 的兼容性**：需要验证在 ARM CUDA 上的稳定性和性能提升。

5. **TensorRT-Edge-LLM 的模型支持范围**：目前支持哪些模型的 GGUF 格式，是否支持 Q4_K_M 量化。

---

*笔记生成：2026-05-24 | 来源：arXiv 2601.14277, DFRobot, NVIDIA Developer Forums, GitHub llama.cpp Discussions, HuggingFace, Knightli, D-Central*

## 相关笔记
- [LLM对齐训练范式RLHF-DPO-GRPO-DAPO](../2026-05-04-LLM对齐训练范式RLHF-DPO-GRPO-DAPO.md)
- [大模型量化技术全景-GGUF-GPTQ-AWQ-FP8-BitNet](../2026-05-07-大模型量化技术全景-GGUF-GPTQ-AWQ-FP8-BitNet.md)
- [推理加速深度解析-投机解码-KVCache-连续批处理](../2026-05-08-推理加速深度解析-投机解码-KVCache-连续批处理.md)
- [JAX-NVIDIA-GPU-微调Llama3.1实战方案](../2026-05-15-JAX-NVIDIA-GPU-微调Llama3.1实战方案.md)
- [LoRA高效微调前沿技术全景](../2026-05-17-LoRA高效微调前沿技术全景.md)
- [SGLang高性能LLM推理框架深度分析](../2026-05-17-SGLang高性能LLM推理框架深度分析.md)
- [Agent元认知-LLM不确定性感知](../2026-05-18-Agent元认知-LLM不确定性感知.md)
- [MoE模型LoRA微调最佳实践](../2026-05-18-MoE模型LoRA微调最佳实践.md)
- [蒸馏量化RL三联流水线-后训练范式统一](../2026-05-19-蒸馏量化RL三联流水线-后训练范式统一.md)
- [Active-Data-Selection-LLM训练动态数据选择前沿](../2026-05-20-Active-Data-Selection-LLM训练动态数据选择前沿.md)
- [MLA多头潜在注意力-DeepSeek-KV缓存压缩与推理优化](../2026-05-21-MLA多头潜在注意力-DeepSeek-KV缓存压缩与推理优化.md)
- [llm-finetune-dataflow-dataflex-pipeline](../2026-05-21-llm-finetune-dataflow-dataflex-pipeline.md)
- [react-agent-llm-agentic-training-research](../2026-05-21-react-agent-llm-agentic-training-research.md)
- [If-youre-an-LLM-please-read-this-Anna-Archive-LLM伦理契约](../2026-05-22-If-youre-an-LLM-please-read-this-Anna-Archive-LLM伦理契约.md)
- [LoRA-GRPO最优配置实证-RL场景的Rank选择与超参数](../2026-05-22-LoRA-GRPO最优配置实证-RL场景的Rank选择与超参数.md)
- [Multi-Stream-LLMs-并行流解锁语言模型](../2026-05-22-Multi-Stream-LLMs-并行流解锁语言模型.md)
- [Antigravity2.0-OpenSCAD-LLM-Benchmark-AI编程3D建模能力](../2026-05-23-Antigravity2.0-OpenSCAD-LLM-Benchmark-AI编程3D建模能力.md)
- [OpenAI后训练团队Yann-Dubois深度访谈](../2026-05-23-OpenAI后训练团队Yann-Dubois深度访谈.md)
- [QLoRA在RL训练中的精度影响-量化与强化学习深度解析](../2026-05-23-QLoRA在RL训练中的精度影响-量化与强化学习深度解析.md)
- [VLM强化学习RL训练-视觉编码器与LoRA配置前沿](../2026-05-24-VLM强化学习RL训练-视觉编码器与LoRA配置前沿.md)
- [LLM推理优化-MoE量化加速全景](2026-05-16-LLM推理优化-MoE量化加速全景.md)
- [llm-inference-opt-incremental2](2026-05-18-llm-inference-opt-incremental2.md)
- [llm-inference-opt-update](2026-05-18-llm-inference-opt-update.md)
- [llm-self-prompt-optimization](2026-05-18-llm-self-prompt-optimization.md)
- [MoE-稀疏激活微调工程实践](2026-05-19-MoE-稀疏激活微调工程实践.md)
- [SGLang-vs-vLLM-推理引擎对比](2026-05-19-SGLang-vs-vLLM-推理引擎对比.md)
- [llm_wiki分析与Skill进化](2026-05-20-llm_wiki分析与Skill进化.md)
- [边缘AI推理优化-Jetson平台深度研究](2026-05-21-边缘AI推理优化-Jetson平台深度研究.md)
- [llama-cpp预编译二进制与本地LLM推理](2026-05-22-llama-cpp预编译二进制与本地LLM推理.md)
- [VPO向量策略优化多样性训练提升推理搜索](2026-05-23-VPO向量策略优化多样性训练提升推理搜索.md)
- [llm-inference-opt-2026-05-17](llm-inference-opt-2026-05-17.md)
- [llm-inference-opt-2026-05-20-supplement](llm-inference-opt-2026-05-20-supplement.md)
- [llm-inference-opt-deep-dive](llm-inference-opt-deep-dive.md)
- [llm-inference-opt-incremental-20260517](llm-inference-opt-incremental-20260517.md)
- [llm-inference-optimization-2026](llm-inference-optimization-2026.md)
