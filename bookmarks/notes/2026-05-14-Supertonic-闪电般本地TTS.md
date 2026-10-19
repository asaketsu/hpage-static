# Supertonic — Lightning Fast, On-Device, Accurate TTS

- 📅 2026-05-14
- ⭐ 4.5/5 — 架构优秀、模型轻量、离线可用、31语言、ONNX跨平台，Hermes 可直接集成
- 🏷️ #TTS #ONNX #FlowMatching #边缘推理 #本地AI #语音合成 #Supertone
- 🏢 Supertone Inc.（韩国）
- 🔗 https://github.com/supertone-inc/supertonic
- 📄 论文：arXiv:2503.23108（架构）/ arXiv:2509.11084（LARoPE）/ arXiv:2509.19091（SPFM）
- 📜 MIT（代码）+ OpenRAIL-M（模型）

## 摘要

Supertonic 是一个基于 ONNX Runtime 的纯本地 TTS 系统，~99M 参数，31 语言支持，CPU 即可实时推理。核心技术为 Flow Matching + Speech AutoEncoder + LARoPE。在金融表达式、电话号码、技术单位等复杂文本朗读上，击败 ElevenLabs/OpenAI/Gemini 等云端竞品。支持 11 种 runtime（Python/JS/Browser/Java/C++/C#/Go/Swift/Rust/iOS/Flutter）。

## 核心架构

```
Text Input
  → Text Normalization（完美处理金融/电话/技术单位）
  → Flow Matching TTS（8步去噪，speed=1.05）
  → Speech AutoEncoder Decoder
  → 16-bit WAV Output（采样率见 sample_rate）
```

### 技术栈
- 推理：ONNX Runtime 1.23.1
- 模型：~99M 参数（对比竞品 0.7B-2B）
- 依赖：numpy + soundfile + librosa + PyYAML（Python SDK）
- Web：onnxruntime-web + Vite
- PyPI 包：`pip install supertonic`（auto_download from HuggingFace）

### 三篇论文
1. **SupertonicTTS** (arXiv:2503.23108) — Flow Matching + Speech AE 整体架构
2. **LARoPE** (arXiv:2509.11084) — Length-Aware RoPE，改进文本-语音对齐
3. **Self-Purifying FM** (arXiv:2509.19091) — 噪声标签训练自净化技术

## 竞品对比

| 维度 | Supertonic | ElevenLabs | OpenAI TTS | Gemini TTS |
|---|---|---|---|---|
| 金融文本 | ✅ | ❌ | ❌ | ❌ |
| 电话号码 | ✅ | ❌ | ❌ | ❌ |
| 技术单位 | ✅ | ❌ | ❌ | ❌ |
| 离线运行 | ✅ | ❌ | ❌ | ❌ |
| 模型大小 | 99M | 云端 | 云端 | 云端 |
| CPU RTF | 0.3× (RPi) | N/A | N/A | N/A |
| 语言 | 31 | 32+ | 7 | 24+ |
| 价格 | 免费开源 | 付费 | 付费 | 付费 |

## 性能数据

- 树莓派实时 RTF 0.3×
- Onyx Boox Go 6 墨水屏 RTF 0.3×
- 比云端大模型（A100 GPU 跑的）还快
- WER/CER 与 VoxCPM2 等大模型处于同一竞争区间
- 模型 99M vs 竞品 0.7B-2B（小 7-20 倍）

## 11 种 Runtime 支持

Python / Node.js / Browser / Java / C++ / C# / Go / Swift / iOS / Rust / Flutter

## 表达式标签

支持 `<laugh>`, `<breath>`, `<sigh>` 等情感标签。

## Voice Builder

商业产品：录制声音→训练→部署为边缘 TTS。永久拥有声音。

## 🔍 对 Hermes 的价值

### 🔴 可直接集成
- **离线 TTS 备选**：当前 Hermes 依赖 Edge/OpenAI 在线 TTS，Supertonic 99M 可在 Jetson Orin 本地跑
- **多语言覆盖**：31 语言含中日韩，比 Edge TTS 更广
- **隐私**：语音数据不离开设备
- **延迟**：纯计算延迟，无网络依赖

### 集成方案
```python
from supertonic import TTS
tts = TTS(auto_download=True)
style = tts.get_voice_style(voice_name="M1")
wav, duration = tts.synthesize(text, voice_style=style, lang="zh")
```

### 风险
- 中文质量需实测（README 主要是英文 demo）
- 99M 模型下载约 200-400MB
- Jetson ARM64 兼容性需验证（ONNX Runtime 支持 ARM）

## 已有生态项目

- TLDRL（Chrome 扩展，网页朗读）
- Read Aloud（开源浏览器扩展）
- PageEcho（iOS 电子书阅读器）
- VoiceChat（浏览器语音聊天）
- Transformers.js（HuggingFace JS 库已集成）

## 💡 启发

- **99M 打赢 2B**：模型不是越大越好，架构设计和训练技术更重要
- **ONNX 是边缘 AI 的正确路径**：跨平台、零依赖、CPU 友好
- **Text Normalization 是隐形杀手锏**：金融/技术文本朗读是刚需但被大厂忽视
- **Voice Builder 商业模式**：声音克隆+永久拥有，面向企业

## 🔮 预判

- Supertonic 将成为边缘 TTS 的事实标准（MIT 许可 + 跨平台 + 小模型）
- 浏览器端 TTS 将是下一个增长点（onnxruntime-web）
- Voice Builder 可能催生"声音 NFT"市场

## 相关笔记
- Hermes TTS 配置（hermes-agent skill）
- [[2026-05-14-手撸Agent-ReAct-Loop从零实现]] - Agent 生态


## 相关笔记
- [2026-05-12-数据治理-data-catalog](2026-05-12-数据治理-data-catalog.md)
- [2026-05-15-JAX-NVIDIA-GPU-微调Llama3.1实战方案](2026-05-15-JAX-NVIDIA-GPU-微调Llama3.1实战方案.md)
- [2026-05-15-序列并行与上下文并行-长上下文训练的第四维并行](2026-05-15-序列并行与上下文并行-长上下文训练的第四维并行.md)
- [index](index.md)
- [2026-05-15-数据治理-governance-framework](explore/2026-05-15-数据治理-governance-framework.md)
