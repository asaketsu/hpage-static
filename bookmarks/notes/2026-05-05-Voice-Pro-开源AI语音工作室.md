# Voice-Pro：开源免费 AI 语音工作室

- 📅 2026-05-05
- ⭐ 4/5 — 功能最全的开源语音工具箱，8260⭐，GPL-3.0，但 Windows 优先 + 资源消耗大
- 🏷️ #开源 #TTS #STT #语音克隆 #Gradio #Whisper #F5-TTS #CosyVoice
- 📰 GitHub: abus-aikorea/voice-pro
- 🔗 https://github.com/abus-aikorea/voice-pro

## 摘要

Voice-Pro 是一个基于 Gradio WebUI 的全能 AI 语音处理平台，集成了 STT（Whisper全系）、TTS（Edge-TTS/Kokoro/F5-TTS/CosyVoice）、零样本语音克隆、YouTube下载、人声分离（Demucs）、RVC变声、实时翻译等功能。韩国团队 ABUS-AIKorea 开发，8260⭐，v3.2.0，完全免费开源（GPL-3.0）。单维护者项目，2024年7月创建，代码量约4.2万行Python（230个文件），内嵌了 CosyVoice 和 RVC 子项目。最大亮点是一站式语音处理管线和名人语音克隆库，但深度依赖 Windows/CUDA 环境，8GB 设备跑不动。

## 核心内容

### 项目画像

| 维度 | 数据 |
|------|------|
| Stars | 8,260 |
| Forks | 1,031 |
| 语言 | Python（100%） |
| 许可证 | GPL-3.0 |
| 代码量 | 42,457 行 / 230 个 .py 文件 |
| 版本 | v3.2.0（最新 tag） |
| 创建时间 | 2024-07-29 |
| 维护者 | ABUS-AIKorea（韩国），单维护者 |
| 最近更新 | 2026-05-05（活跃维护中） |
| 平台 | Windows 优先，Linux 部分支持 |

### 功能模块一览

| 模块 | 技术 | 说明 |
|------|------|------|
| Dubbing Studio | Gulliver 管线 | YouTube下载→STT→翻译→TTS→配音，一站式 |
| Whisper 字幕 | Whisper/Faster-Whisper/Whisper-Timestamped/WhisperX | 四引擎可选 |
| 翻译 | Azure Translator / DeepL | VOD翻译 + 实时翻译 |
| Edge-TTS | edge-tts 库 | 微软免费TTS，多语言多音色 |
| F5-TTS | SWivid/F5-TTS + E2-TTS | 零样本语音克隆，单人和多人模式 |
| CosyVoice | 阿里 CosyVoice2-0.5B | 零样本克隆 + 名人语音库（30s样本） |
| Kokoro TTS | kokoro 库 | 轻量高质量 TTS |
| RVC 变声 | RVC (Retrieval-based Voice Conversion) | 实时变声 |
| 人声分离 | Demucs (htdemucs/htdemucs_ft) | 音频分离 |
| AI Cover | RVC + Demucs | AI 翻唱（当前被注释掉） |
| Karaoke | Demucs + 歌词同步 | 卡拉OK模式 |
| 视频超分 | Upscaler | 视频画质增强 |

### 架构特点

1. **Gradio WebUI**：所有功能通过 Gradio Tabs 组织，端口 7870，暗色主题
2. **模块化设计**：每个 TTS/ASR 引擎独立类文件（abus_tts_*.py / abus_asr_*.py），Gradio tab 文件独立（tab_*.py）
3. **模型管理**：HF_File 类统一管理 HuggingFace 模型下载，JSON 配置文件指定模型路径和大小
4. **内嵌子项目**：直接包含 CosyVoice 和 RVC 完整源码（不是 pip 依赖），third_party/ 下还有 Matcha-TTS
5. **Windows 深度绑定**：多处 `winreg` 操作修改注册表、CUDA/cuDNN 路径硬编码、espeak-ng 路径处理均仅 Windows

### 模型资源需求

| 模型 | 大小 | 备注 |
|------|------|------|
| CosyVoice2-0.5B | ~9GB | 语音克隆核心模型 |
| Demucs htdemucs_ft | ~312MB | 人声分离 |
| F5-TTS 模型 | ~1.2GB | 零样本克隆 |
| Kokoro + eSpeak NG | ~18MB | 轻量 TTS |
| Whisper large-v3 | ~3GB | 最佳 STT 质量 |
| RVC 预训练模型 | ~500MB | 变声 |
| **总计** | **~14GB+** | 不含 Whisper large |

## 🔍 借鉴点

### ① 有利进化（需评估是否落实）

1. **名人语音库模式**（celebrities30s.json5）：预置名人语音样本 + 元数据索引，用户可直接选择克隆。对 jbot TTS 系统的语音选择体验有参考价值 → **不落实**：当前 TTS 用 edge-tts 已有足够音色，语音克隆需求不明确
2. **Dubbing Studio 一站式管线**：YouTube→STT→翻译→TTS→合成，完整配音工作流 → **不落实**：jbot 无配音需求，但管线编排思路可参考

### ② 有价值（记入 Memory）

- Gradio 作为语音工具 UI 框架的模式，如果未来需要给非技术用户提供语音操作界面可参考
- HF_File 模型下载管理器设计（JSON配置 + 大小校验 + 自动解压），比手动管理模型文件更优雅

### ③ 知识库

- CosyVoice2-0.5B 是阿里开源的语音克隆模型，9GB，支持零样本克隆
- Kokoro TTS 是一个新兴的轻量高质量 TTS 引擎，仅需 ~18MB
- F5-TTS 支持多人零样本克隆（Multi 模式），这在开源 TTS 中较少见
- 项目以 single commit 开源全部代码，之前是闭源商业软件

## 🔗 关联性

- 关联已有笔记：[2026-05-05-Horizon-analysis](20260505-Horizon-analysis.md) — 同为开源 AI 工具分析
- 关联已有 skill：hermes-voice-stt-diagnosis — STT/TTS 诊断相关
- 关联技术栈：edge-tts（jbot 当前 TTS 后端）、faster-whisper（jbot 当前 STT 后端）
- 关联记忆：Ollama 暂不常驻（8GB 设备限制）— Voice-Pro 的模型需求远超 jbot 承载能力

## 💡 启发

- **一站式 vs 模块化**：Voice-Pro 把所有语音功能塞进一个 Gradio，用户友好但对硬件要求极高。jbot 的策略（按需调用 edge-tts/faster-whisper，不常驻模型）更适合资源受限设备
- **开源策略转变**：从闭源商业到完全开源（single commit），说明语音 AI 工具的商业化困难，开源是更好的获客路径
- **Kokoro TTS 值得关注**：仅 18MB 模型，质量不错，可能适合边缘设备。如果 jbot 需要离线 TTS，Kokoro 比当前 Ollama 方案更轻量

## 🔮 预判

- **短期**（1-3月）：Voice-Pro 持续迭代，可能加入更多 TTS 模型（Qwen3-TTS 等），Stars 破万
- **中期**（3-6月）：开源语音克隆工具（F5-TTS/CosyVoice）将成为标配，Voice-Pro 类工具涌现竞争者
- **长期**：本地化语音 AI（STT+TTS+翻译一体）将在边缘设备普及，但 8GB 设备仍需等模型压缩技术进步
- **jbot 行动**：暂无。关注 Kokoro TTS 的 ARM/CUDA 兼容性，如确认可在 Jetson 运行则可作为离线 TTS 备选

## 相关笔记
- [2026-05-05-Horizon-analysis](20260505-Horizon-analysis.md) - AI新闻雷达分析
