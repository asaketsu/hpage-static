# Bonsai 极限量化：把 27B 推理模型塞进 3.9 GB

> Prism ML 发布的 Bonsai 量化家族，将 Qwen3.6-27B 压缩到 **1.125 bit/权重**（3.9 GB），在 Apple M5 Pro 笔记本上跑出 44 tok/s，保留 FP16 智能的 89.5%。iPhone 17 Pro Max 上也能跑。

📅 2026-07-24 | 🔖 量化, LLM, 边缘部署, llama.cpp, 1-bit, ternary

---

## 核心发现

### 1. 极限压缩的两个操作点

| 变体 | 真实 bit/权重 | 部署体积 | vs FP16 智能保留 | 定位 |
|------|-------------|---------|----------------|------|
| **1-bit Bonsai** | 1.125 | 3.9 GB | 89.5% (76.11/85.07) | 手机级，最小占用 |
| **Ternary Bonsai** | 1.71 | 7.2 GB | 94.6% (80.49/85.07) | 质量优先，标准笔记本 |
| Qwen3.6-27B Q4_K_XL | 5.2 | 17.6 GB | 99.9% | 常规 4-bit 基线 |
| Qwen3.6-27B IQ2_XXS | 2.8 | 9.4 GB | 85.5% | 常规 2-bit（崩溃） |
| Qwen3.6-27B FP16 | 16.0 | 54 GB | 100% | 全精度基线 |

**关键洞察：** 常规量化在 sub-4-bit 区间会选择性崩溃——IQ2_XXS 的 AIME26 从 93 跌到 57.5，LiveCodeBench 从 87 跌到 56。而 Bonsai 在这些需要持续推理链的任务上几乎无损。

### 2. 量化编码方案

**Q1_0_g128（1-bit）：**
- 每个权重仅一个符号位：`0 → -scale`，`1 → +scale`
- 每 128 个权重共享一个 FP16 scale factor
- 有效 1.125 bit/权重（1 sign bit + 16-bit scale 分摊到 128 个权重）

**Q2_0_g128（Ternary）：**
- 权重取值 `{−1, 0, +1}`，三进制编码
- 三进制携带 log₂3 ≈ 1.585 bit 信息
- 有效 1.71 bit/权重
- 额外的零状态提供更强表达能力，恢复更多全精度行为

**端到端覆盖：** embeddings、attention 投影、MLP 投影、LM head 全部低比特化，没有高精度逃逸通道。

### 3. 关键工程加速

**DSpark 推测解码：**
- 六层 block-parallel drafter transformer
- 从目标模型 5 个均匀间隔层抽取 hidden states 作为条件
- CUDA 路径无损加速 **1.37x**（H100: 104.8 → 143.8 tok/s）
- 验证保证目标分布精确不变，drafter 精度只影响速度不影响输出质量

**混合注意力架构（Qwen3.6-27B 固有）：**
- ~75% 线性注意力 + ~25% 全注意力
- 64 层中仅 16 层增长 full-attention KV cache
- 262K 上下文全量 KV cache 仅 ~4.3 GB
- 配合 4-bit KV 量化，262K 上下文峰值 ~9.4 GB

### 4. 跨平台吞吐实测

| 平台 | 体积 | TG128 (tok/s) | PP512 (tok/s) |
|------|------|-------------|-------------|
| Apple M5 Max (Metal) | 3.9 GB | 66.4 | 874 |
| Apple M5 Pro (Metal) | 3.9 GB | 44.2 | 421 |
| Apple M4 Pro (Metal) | 3.9 GB | 26.0 | 133 |
| 单卡 H100 (CUDA) | 3.9 GB | 104.8 | 2755 |

- 解码能耗 M5 Pro: **0.275 mWh/token**（含 DSpark drafter）
- 比 GPU 数据中心（0.63-1.32 mWh/token）低一个数量级
- iPhone 17 Pro Max via MLX Swift: ~11 tok/s

### 5. 能力分布（Thinking 模式）

| 类别 | FP16 | 1-bit | Ternary |
|------|------|-------|---------|
| 数学 (GSM8K, MATH-500, AIME) | 95.33 | 91.66 | 93.40 |
| 编码 (HumanEval+, MBPP+, LiveCodeBench) | 88.74 | 81.88 | 85.96 |
| 知识推理 (MMLU-Redux, MuSR) | 83.15 | 73.39 | — |
| Agentic/工具调用 (BFCL v3, τ²-Bench) | 80.00 | 66.03 | 74.01 |
| 视觉 (MMMU-Pro, OCR Bench) | 72.61 | 59.57 | — |

**推理骨干完好：** 数学在 1-bit 下仍达 91.66（距全精度 4 分以内），这是常规 sub-4-bit 最先丢失的能力。

---

## 技术价值评估

### 🟢 对我们的直接价值

1. **Jetson 边缘部署路径：** 当前 Jetson Orin Nano（8GB 统一内存）完全可以跑 Ternary Bonsai（7.2 GB 含 KV cache 峰值约 8-9 GB，紧凑配置可行），将 27B 级推理能力带到边缘设备
2. **量化范式革命：** 传统 GGUF Q4_K 系列是"标注欺骗"——名为 4-bit 实际 5.2 bit。Bonsai 的真实 1.125 bit 是从训练阶段就对齐二值化的范式转变
3. **推测解码模板：** DSpark drafter 架构可作为我们边缘推理加速的参考模式

### 🔴 局限性

- **知识/视觉退化明显：** MMLU 从 93 跌到 83，MMMU-Pro 从 80 跌到 60，不适合纯知识检索或多模态任务
- **依赖 Qwen3.6 混合注意力：** 极致压缩效果部分来自 75% 线性注意力的 KV cache 天然小，换到标准 Transformer 架构效果会打折
- **自定义 kernel：** 需要 Prism ML 的 llama.cpp fork，不是标准 llama.cpp 即插即用

---

## 实操指南

```bash
# 克隆 Prism ML 的 llama.cpp fork（含 Q1_0_g128 hybrid-attention kernel）
git clone https://github.com/PrismML-Eng/llama.cpp
cd llama.cpp

# CUDA 构建
cmake -B build -DGGML_CUDA=ON && cmake --build build -j

# 下载 1-bit 权重
hf download prism-ml/Bonsai-27B-gguf Bonsai-27B-Q1_0.gguf --local-dir .

# 推理
./build/bin/llama-cli \
    -m Bonsai-27B-Q1_0.gguf \
    -p "Explain quantum computing in simple terms." \
    -n 256 \
    --temp 0.7 --top-p 0.95 --top-k 20 \
    -ngl 99
```

推荐生成参数：Temperature 0.7 / Top-p 0.95 / Top-k 20

---

## 来源

- 🤗 [prism-ml/Bonsai-27B-gguf](https://huggingface.co/prism-ml/Bonsai-27B-gguf) (615 likes, 1.9M downloads)
- 🤗 [prism-ml/Ternary-Bonsai-27B-gguf](https://huggingface.co/prism-ml/Ternary-Bonsai-27B-gguf) (977 likes, 576K downloads)
- 📄 [Whitepaper (PDF)](https://github.com/PrismML-Eng/Bonsai-demo/blob/main/bonsai-27b-whitepaper.pdf)
- 🔧 [llama.cpp fork](https://github.com/PrismML-Eng/llama.cpp) (CUDA + Metal kernel)
- 🔧 [MLX fork](https://github.com/PrismML-Eng/mlx) (Apple Silicon)


## 相关笔记

- [HuggingFace Trending 全景 2026年7月](./2026-07-24-HuggingFace-Trending全景-2026年7月AI模型生态.md) — 极限量化革命趋势来源
- [KV-Cache 压缩与长上下文推理优化全栈](./2026-07-27-KV-Cache压缩与长上下文推理优化全栈.md) — 推理优化另一路径
- [嵌入式 AI TinyML 现状](./2026-07-19-嵌入式AI-TinyML现状-从MCU感知到端侧小语言模型.md) — 边缘部署量化实践
- [边缘 AI 推理优化 TinyML 到 TinyLM](./2026-07-23-边缘AI推理优化-TinyML到TinyLM的2026现状.md) — 端侧量化演进
