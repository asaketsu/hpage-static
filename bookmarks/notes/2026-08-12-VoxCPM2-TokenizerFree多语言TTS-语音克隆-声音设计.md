# VoxCPM2 — Tokenizer-Free 多语言 TTS + 语音克隆 + 声音设计（OpenBMB）

> GitHub: https://github.com/OpenBMB/VoxCPM
> HuggingFace: https://huggingface.co/openbmb/VoxCPM2
> 技术报告: https://arxiv.org/abs/2606.06928
> 许可证: Apache-2.0（可商用）
> 评分: ⭐⭐⭐⭐⭐ (5/5) — 无 tokenizer 的端到端扩散自回归 TTS，2B 参数，30 语言，48kHz

## 一句话定位

**OpenBMB 出品的 tokenizer-free TTS 系统，2B 参数，200 万小时多语言训练，支持 30 语言 + 中文方言，48kHz 录音室级音质，Voice Design（文字描述创造音色）+ 可控克隆 + 终极克隆三种模式，Apache-2.0 完全开源可商用。**

## 核心技术亮点

| 特性 | 说明 |
|------|------|
| **Tokenizer-Free** | 直接生成连续语音表示，跳过离散 tokenization，实现高自然度和高表现力合成 |
| **扩散自回归架构** | End-to-end diffusion autoregressive，基于 MiniCPM-4 backbone |
| **2B 参数** | 200 万小时多语言语音数据训练 |
| **30 语言** | 阿拉伯语/中文/英语/法语/德语/日语/韩语/俄语/西班牙语等 30 种，无需指定语言标签 |
| **中文方言** | 四川话/粤语/吴语/东北话/河南话/陕西话/山东话/天津话/闽南话 |
| **48kHz 音质** | 接收 16kHz 参考音频，直接输出 48kHz，AudioVAE V2 非对称编解码内置超分辨率 |
| **RTF ~0.13** | Nano-vLLM 加速后 RTX 4090 上 RTF 0.13（标准实现 ~0.30） |
| **~8GB VRAM** | 2B 模型仅需 ~8GB 显存 |

### 四种语音生成模式

| 模式 | 输入 | 特点 |
|------|------|------|
| **🗣️ Text-to-Speech** | 纯文本 | 标准合成，自动推断韵律和表现力 |
| **🎨 Voice Design** | 文字描述音色（如"年轻女性，温柔甜美"） | **无需参考音频**，从自然语言描述创造全新音色 |
| **🎛️ Controllable Cloning** | 参考音频 + 风格控制指令 | 克隆音色同时可控情感/语速/风格 |
| **🎙️ Ultimate Cloning** | 参考音频 + 参考文本（transcript） | 音频续写式克隆，忠实再现音色/节奏/情感/风格的每个细节 |

## 快速上手

### 安装

```bash
pip install voxcpm
# 要求: Python ≥3.10(<3.13), PyTorch ≥2.5.0, CUDA ≥12.0
```

### Python API

```python
from voxcpm import VoxCPM
import soundfile as sf

model = VoxCPM.from_pretrained("openbmb/VoxCPM2", load_denoiser=False)

# 基础 TTS
wav = model.generate(text="你好，欢迎使用 VoxCPM2。", cfg_value=2.0, inference_timesteps=10, seed=42)
sf.write("demo.wav", wav, model.tts_model.sample_rate)

# Voice Design — 文字描述创造音色
wav = model.generate(
    text="(年轻女性，温柔甜美的声音)你好，欢迎来到 VoxCPM2！",
    cfg_value=2.0, inference_timesteps=10, seed=42,
)

# Controllable Cloning — 克隆 + 风格控制
wav = model.generate(
    text="(稍快语速，欢快的语调)这是一个带风格控制的克隆语音。",
    reference_wav_path="path/to/voice.wav",
)

# Ultimate Cloning — 终极克隆
wav = model.generate(
    text="这是终极克隆演示。",
    prompt_wav_path="path/to/voice.wav",
    prompt_text="参考音频的完整文本转写。",
    reference_wav_path="path/to/voice.wav",  # 可选，提升相似度
)

# 流式输出
import numpy as np
chunks = []
for chunk in model.generate_streaming(text="流式语音合成非常简单！"):
    chunks.append(chunk)
wav = np.concatenate(chunks)
```

### CLI 使用

```bash
# Voice Design（无需参考音频）
voxcpm design --text "VoxCPM2 brings studio-quality multilingual speech synthesis." --output out.wav

# 带风格控制的设计
voxcpm design \
  --text "VoxCPM2 brings studio-quality multilingual speech synthesis." \
  --control "Young female voice, warm and gentle, slightly smiling" \
  --seed 42 --output out.wav

# 语音克隆（参考音频）
voxcpm clone --text "This is a voice cloning demo." --reference-audio path/to/voice.wav --output out.wav

# 终极克隆（参考音频 + 转写）
voxcpm clone \
  --text "This is a voice cloning demo." \
  --prompt-audio path/to/voice.wav --prompt-text "reference transcript" \
  --reference-audio path/to/voice.wav --output out.wav

# 批量处理
voxcpm batch --input examples/input.txt --output-dir outs

# 带时间戳输出（word/char 级别）
pip install "voxcpm[timestamps]"
voxcpm design --text "..." --output out.wav --timestamps --timestamp-level word --timestamp-language en
```

## 部署方案对比

| 方案 | 引擎 | RTF (4090) | 并发 | 适用场景 |
|------|------|-----------|------|----------|
| **标准 PyTorch** | voxcpm | ~0.30 | 单请求 | 开发/测试 |
| **Nano-vLLM** | nano-vllm-voxcpm | ~0.13 | 批量并发 + async API | 中小规模生产 |
| **vLLM-Omni** | vllm-omni | — | PagedAttention + 连续批处理 + OpenAI 兼容 API | 大规模多租户 |
| **llama.cpp-omni** | C++ (GGUF) | M4 Pro ~1.76 | 单设备 | **端侧/边缘部署（无 Python）** |

### vLLM-Omni 生产部署（OpenAI 兼容 API）

```bash
vllm serve openbmb/VoxCPM2 --omni --port 8000

# OpenAI 客户端直接调用
curl http://localhost:8000/v1/audio/speech \
  -H "Content-Type: application/json" \
  -d '{"model":"openbmb/VoxCPM2","input":"Hello from VoxCPM2!","voice":"default"}' \
  --output out.wav
```

### llama.cpp-omni 端侧部署

```bash
# 下载 GGUF 权重（Q8_0 质量损失可忽略，体积减半）
./build/bin/voxcpm2-cli \
    -t "Hello, this is VoxCPM2 running on edge." \
    -o output.wav \
    VoxCPM2-BaseLM-Q8_0.gguf VoxCPM2-Acoustic-F16.gguf
```

支持 CPU / Metal / CUDA / Vulkan 后端。

## 版本对比

| 维度 | VoxCPM2 (最新) | VoxCPM1.5 | VoxCPM-0.5B |
|------|---------------|-----------|-------------|
| **参数** | 2B | 0.6B | 0.5B |
| **采样率** | 48kHz | 44.1kHz | 16kHz |
| **语言** | 30 | 2 (zh, en) | 2 (zh, en) |
| **克隆模式** | 独立参考 + 续写 | 仅续写 | 仅续写 |
| **Voice Design** | ✅ | ❌ | ❌ |
| **可控克隆** | ✅ | ❌ | ❌ |
| **RTF (4090)** | ~0.30 | ~0.15 | ~0.17 |
| **RTF (Nano-vLLM)** | ~0.13 | ~0.08 | ~0.10 |
| **VRAM** | ~8GB | ~6GB | ~4GB |

## 💡 对我们的借鉴分析

### 与现有 TTS 方案对比

| 维度 | VoxCPM2 | LuxTTS (当前主力) | F5-TTS (克隆) | ElevenLabs |
|------|---------|-------------------|---------------|------------|
| **参数** | 2B | — | ~1.3GB | 闭源 |
| **语言** | 30 (含中文方言) | 中英文 | 任意（参考音频） | 多语言 |
| **采样率** | 48kHz | 48kHz | 24kHz | — |
| **VRAM** | ~8GB | ~2.2GB | ~1.3GB | 云端 |
| **Voice Design** | ✅ 文字描述 | ❌ | ❌ | ✅ |
| **可控克隆** | ✅ 风格控制 | ❌ | 仅克隆 | ❌ |
| **端侧部署** | ✅ GGUF/C++ | ❌ Python | ❌ Python | ❌ |
| **许可证** | Apache-2.0 | 开源 | 开源 | 商业 |

### 🔥 关键启发

| 启发点 | 内容 |
|--------|------|
| **Tokenizer-Free 架构** | 绕过离散 tokenization 直接生成连续语音——这可能是 TTS 的范式转换。当前主流 TTS（VITS/F5-TTS/LuxTTS）都依赖某种形式的 tokenizer |
| **Voice Design** | 用自然语言描述创造音色（"年轻女性，温柔甜美"），无需参考音频。这对数字人场景极有价值——可以为不同数字人角色快速定制专属音色 |
| **可控克隆** | 克隆音色 + 风格控制指令，比 F5-TTS 的纯克隆更进一步 |
| **Jetson 可行性评估** | 2B 参数需 ~8GB VRAM。Jetson Orin Nano 8GB unified memory 勉强够。但需要配合 llama.cpp-omni 的 GGUF 量化（Q8_0）才有可能跑起来 |
| **vLLM-Omni OpenAI API** | `/v1/audio/speech` 端点与 OpenAI TTS API 兼容，可无缝替换 |
| **端侧 GGUF 部署** | llama.cpp-omni 支持 CPU/Metal/CUDA/Vulkan，Jetson 可用 CUDA 后端。Q8_0 量化体积减半质量损失可忽略 |

### 📊 Jetson Orin Nano 部署评估

| 维度 | 评估 | 说明 |
|------|------|------|
| VRAM | ⚠️ 临界 | 2B fp16 需 ~8GB，Jetson 8GB 刚好。需 Q8_0 量化才安全 |
| 推理速度 | ⚠️ 待测 | RTX 4090 RTF 0.3，Jetson 算力约为 4090 的 1/15，预计 RTF 4-5（不可实时） |
| 端侧方案 | ✅ 可行 | llama.cpp-omni + GGUF Q8_0，CPU/CUDA 后端 |
| 替代定位 | 云端推理 | Jetson 上做 LuxTTS/F5-TTS，云端部署 VoxCPM2 做高质量生成 |

### 🎯 可实施的行动

1. **短期**：在 Jetson 上试跑 VoxCPM2 GGUF Q8_0，测 RTF 是否可接受
2. **中期**：如果 RTF < 3，可作为 LuxTTS 的高质量替代（非实时场景如视频制作）
3. **Voice Design 集成**：为数字人 pipeline 项目（digital-human-pipeline）的 Step 2（音色确定）提供新方案——文字描述即可创造音色，无需录制参考音频

## 关联

- → 相关：2026-06-14-语音智能体闭环-Typeless-VoxCPM2.md
- → 相关：2026-05-14-Supertonic-闪电般本地TTS.md
- → 相关：explore/2026-05-18-f5-tts-voice-cloning-incremental.md
- → 项目：~/uclaw/project/digital-human-pipeline/（VoxCPM2 可作为 Step 2 TTS 方案）
