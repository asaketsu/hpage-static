# TensorRT Edge-LLM：Jetson 纯 C++ 推理运行时实战

> **来源**：Jetson AI Lab 2.0 教程 + NVIDIA Developer Blog + arXiv 综述
> **日期**：2026-07-20
> **主题**：cyber / 边缘 AI 推理
> **评分**：⭐⭐⭐⭐☆ (4/5)

---

## 核心发现

NVIDIA 发布了 **TensorRT Edge-LLM**——一个面向 Jetson 平台的**纯 C++ LLM/VLM 推理运行时**。关键突破：**运行时无 Python 解释器在推理路径中**。一个小型原生二进制加载预编译的 TensorRT 引擎直接服务请求，彻底消除了 Python GIL 和 JIT 开销。

这对 Jetson Orin Nano（8GB 统一内存）这类资源受限设备意义重大——终于可以在不牺牲延迟的前提下跑 4B 级别模型。

## 工作流程三步走

```
Step 1: 模型导出（x86 主机）     Step 2: 构建运行时（每台 Jetson）    Step 3: 纯 C++ 推理
┌──────────────────────┐       ┌──────────────────────────┐       ┌─────────────────────┐
│ PyTorch → ONNX 导出   │  →    │ ONNX → TensorRT 引擎构建  │  →    │ C++ binary 加载引擎  │
│ 量化：INT4/NVFP4/FP8  │       │ 针对具体 Jetson 芯片优化   │       │ handleRequest() API  │
│ 需 6x VRAM / 20x RAM  │       │ make -j4 (Nano 内存有限)  │       │ 零 Python 开销       │
└──────────────────────┘       └──────────────────────────┘       └─────────────────────┘
```

## 两个标杆案例

| 模型 | 类型 | 参数量 | 量化方案 | 目标设备 |
|------|------|--------|----------|----------|
| Cosmos-Reason2-8B | VLM | 8B | NVFP4 | Jetson Thor |
| Qwen3-4B-Instruct | LLM | 4B | INT4 AWQ | Jetson Orin Nano 8GB |

**Qwen3-4B + INT4 AWQ 在 Orin Nano 8GB 可用**——这是目前最务实的边缘 LLM 部署方案之一。

## 量化方案对比

| 方案 | 比特/权重 | 适用场景 | 内存需求 |
|------|-----------|----------|----------|
| INT4 AWQ | ~4.5 bits | Orin Nano / 内存受限 | 最低 |
| NVFP4 | 4 bits (FP) | Thor / 新架构 | 低 |
| FP8 | 8 bits | Thor / 高精度需求 | 中 |
| FP16 | 16 bits | 基准 / 不推荐边缘 | 高 |

### 关键陷阱

- **FP8 ONNX 导出需 6x GPU VRAM + 20x CPU RAM**（8B 模型导出可能 OOM）→ 用 INT4 AWQ 替代
- **Orin Nano 编译用 `make -j4`**，不要 `make -j$(nproc)`，会 OOM 崩溃
- **不能用 `pip install torch`**——PyPI 的 torch wheel 不兼容 Jetson，必须用 NVIDIA 容器的 Jetson 构建

## C++ API 极简

生产环境集成只需三个调用：

```cpp
// 1. 创建运行时
auto runtime = createRuntime(enginePath);

// 2. 捕获 CUDA Graph（优化重复推理）
runtime->captureCudaGraphs();

// 3. 处理请求
auto response = runtime->handleRequest(prompt);
```

这比 Python 推理路径（vLLM/HF Transformers）的延迟低一个数量级，因为没有：
- Python 解释器开销
- GIL 锁竞争
- JIT 编译
- 动态图构建

## Edge AI 2026 现状（Medium 技术指南要点）

Jensen Huang 在 2026 CES 宣称"物理 AI 的 ChatGPT 时刻到了"。但实际：

| 能力 | 状态 | 现实 |
|------|------|------|
| Jetson 本地 LLM | ✅ 可用 | 4B 模型 + INT4 已可流畅运行 |
| Jetson 本地 VLM | ⚠️ 部分 | 8B 需 Thor，Nano 仅能跑小 VLM |
| 端侧实时控制 | ⚠️ 挑战 | 延迟仍高于专用 ASIC |
| 端侧训练 | ❌ 不现实 | 仅推理，训练仍需云端 |
| 纯本地隐私 | ✅ 优势 | 无 API 调用，数据不出设备 |

## 对 Hermes Jetson 部署的启示

### 1. 迁移路径：Python → C++

当前 Hermes 在 Jetson 上的 LLM 推理走 Ollama（Python 绑定）。对于**高频低延迟场景**（如语音助手实时响应），可考虑：
- 高频路径：TensorRT Edge-LLM C++ binary
- 低频路径：Ollama（灵活性优先）

### 2. Qwen3-4B-INT4 是当前最优选

结合 Orin Nano 8GB 的内存限制，Qwen3-4B-Instruct + INT4 AWQ 是**性能/资源比最优**的方案。相比之前的 Llama-3-8B 量化尝试，4B 模型在 8GB 设备上留有更多 KV 缓存空间。

### 3. 模型导出分离策略

在 x86 主机上完成 ONNX 导出 + 量化 → 只把 .engine 文件拷贝到 Jetson。避免在 Jetson 上做编译（内存不够）。

### 4. edge-llm-quantization Skill 更新建议

当前 Skill 记录了 GGUF/llama.cpp 方案，应补充：
- TensorRT Edge-LLM 作为**低延迟优先**方案的补充
- INT4 AWQ vs GGUF Q4_K_M 的对比基准
- x86 导出 + Jetson 运行的分离工作流

## 实操清单

```bash
# 在 x86 主机上（有 GPU）
docker run --gpus all nvidia/jetson-pytorch:latest
python3 export_model.py --model Qwen3-4B-Instruct --quant int4_awq
# 产出: qwen3-4b-int4.engine

# 拷贝到 Jetson
scp qwen3-4b-int4.engine jetson:~/models/

# Jetson 上构建运行时（用 -j4！）
cd TensorRT-Edge-LLM && mkdir build && cd build
cmake .. && make -j4

# 运行
./llm_inference --engine ~/models/qwen3-4b-int4.engine
```

## 相关笔记

- `2026-06-07-llm-inference-optimization.md` — CLSA/SAGE-PTQ 等推理优化
- `robot-kinematics-simulation` 相关笔记 — 机器人边缘计算
- `esp32-edge-impulse` 相关 — TinyML 端侧部署对比

## 关键词

`tensorrt` `edge-llm` `jetson-orin` `int4-quantization` `c++-inference` `qwen3` `nvfp4` `edge-ai`
