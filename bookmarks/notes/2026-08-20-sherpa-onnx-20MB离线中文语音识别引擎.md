# 开源的中文语音识别模型只有 20MB，不用显卡也不用联网

> **来源**：微信公众号
> **原文链接**：https://mp.weixin.qq.com/s/-OzY1mPA3VonGsVW4JZCvg
> **作者**：微信公号（转载/整理自 k2-fsa/sherpa-onnx）
> **记录日期**：2026-08-20

**标签**：#sherpa-onnx #端侧ASR #离线语音 #ONNXRuntime #离线实时字幕

---

## 一、内容详细整理

### 1.1 项目身份：sherpa-onnx 是什么

`sherpa-onnx`（GitHub: `k2-fsa/sherpa-onnx`，Apache-2.0）是一套**跑在 ONNX Runtime 上**的语音处理引擎，不依赖 PyTorch、不依赖显卡、不依赖联网。

- **覆盖能力 5 合一**：语音转文字（ASR）/ 文字转语音（TTS）/ 静音检测 VAD（voice activity detection）/ 说话人识别 / 说话人分离
- **底层引擎**：ONNX Runtime —— 而不是 PyTorch/JAX。这决定了它的"CPU 主场"定位，而不是"GPU 加速器"定位。
- **官方支持的运行环境**：树莓派、Android、iOS、HarmonyOS，以及 x86、ARM、RISC-V 三种架构。跨端覆盖面几乎覆盖当前所有主流嵌入式与移动端场景。
- **接口**：C++ / Python / C# / Java / Go / Rust / Swift / Kotlin / Dart 等 12 种语言绑定。
- **活跃度**：截至文章发布（2026-08-18 仍有 commit）；开放 issue 616 个（对 12 语言绑定的项目属可接受量级，但提示边缘场景仍有坑）。
- **仓库地址**：https://github.com/k2-fsa/sherpa-onnx

### 1.2 中文识别模型家族（模型体积实测数据）

文章作者在 releases 页面**逐个核过**中文识别模型的体积：

- `streaming-zipformer-small-ctc-zh-int8` —— **20.3 MB**（int8 量化，最小可用中文流式识别）
- Zipformer 系列（fp32 版）—— 中等
- Paraformer 系列 —— 中等偏高
- SenseVoice 多语言模型 —— **999 MB**（旗舰，支持多语种）

**关键洞察**：决定门槛的是**模型**不是引擎。同一套 sherpa-onnx 引擎，可以随机器强弱换不同大小的模型，"机器弱换小的，要精度换大的"，不需要整套方案重来。

### 1.3 流式 vs 非流式：两个场景两把刀

- **流式（streaming）**：说一句出一句。适用场景：实时字幕、会议同传。
- **非流式（offline）**：给整段录音出整段文字。适用场景：会议纪要、录音转写。

### 1.4 部署形态与真实"开箱"感受

文章作者明确区分"能跑"和"好用"：

- **能跑**：CPU 即可；最低 20MB 模型；不依赖 CUDA；不联网。
- **但不好开箱**：sherpa-onnx 是**库**，不是**软件**。官方**没有 Windows 图形界面**。想跑要么写几行 Python、要么编译一个示例。Android 提供预编译 APK。
- **速度不承诺**：官方没有对具体机型给出速度承诺。树莓派上"跑得动"和"跑得实时"是两回事。CPU 速度与机型直接相关。

### 1.5 模型与引擎的解耦设计

- 引擎（sherpa-onnx）是一个薄封装，模型单独下、单独换。
- 这意味着：同一份部署代码可以在树莓派上跑 int8 小模型、在 PC 上跑 fp32 大模型，代码不改、依赖不改，只换模型文件路径。
- 这是 sherpa-onnx 相比传统 ASR 部署栈（如 Kaldi、WeNet、Whisper.cpp）的一个核心差异化：把"模型选择"下放给了部署方。

### 1.6 三条前置说明（作者原话整理）

1. **它不是一个双击就能用的软件，是一套引擎** —— 拿到的是库和示例代码，要么写 Python、要么编译示例程序，没有官方 Windows GUI。想开箱即用的读者会失望。
2. **"不用显卡"不等于"随便什么机器都快"** —— CPU 上能跑是真的，但速度和你的 CPU 直接相关，树莓派上跑得动和跑得实时是两回事，官方也没有对具体机型给出速度承诺。
3. **616 个开放 issue 不算少** —— 对覆盖十几个平台、十几种语言绑定的项目来说可以理解，但也说明边缘场景踩坑的概率不低，真要上生产得自己先压测。

---

## 二、查询拓展

### 2.1 ONNX Runtime 在端侧 ASR 中的角色

ONNX Runtime 是微软主导的跨平台 ML 推理引擎，支持 CPU / GPU / NPU / 移动端。与 PyTorch/TensorFlow 训练框架不同，ONNX Runtime **只做推理**（inference-only），不做训练。sherpa-onnx 选择 ONNX Runtime 的核心逻辑：

- **训练与推理解耦**：ASR 模型在 PyTorch 训练好后，导出 ONNX 格式，由 sherpa-onnx 加载。这一解耦避免了推理侧的 PyTorch 依赖（~2GB Python 包），把部署体积压到 MB 级。
- **多平台统一**：同一份 ONNX 模型可在 PC / 手机 / 嵌入式上跑，无需为每个平台训练一套模型。
- **硬件后端**：ONNX Runtime 原生支持 CPU、CUDA、CoreML、DirectML、TensorRT、QNN（Qualcomm NPU）等多个 ExecutionProvider。但 sherpa-onnx 在大多数场景下走 CPU 后端 —— 20MB int8 模型跑在树莓派 CPU 上都够。

**与同类方案对比**：Whisper.cpp（ggerganov 维护）同样走离线 CPU 推理，但专注 ASR，不支持 TTS/VAD；sherpa-onnx 是语音"全家桶"。

### 2.2 Zipformer / Paraformer / SenseVoice 三代中文 ASR 模型

| 模型 | 架构特点 | 训练方 | 特点 |
|------|---------|--------|------|
| Zipformer | 深度卷积+流式 attention，专为实时流式 ASR 设计 | Kaldi/icefall 社区 | 流式延迟低、量化友好、小模型精度损失小 |
| Paraformer | Non-Autoregressive (NAR) 端到端 ASR | PaddleSpeech | 推理速度快（非自回归）、精度好、但流式支持弱 |
| SenseVoice | 多语言大模型 ASR | SenseTime | 多语种、支持情感/性别/语言识别、体积大 |

**为什么 20MB int8 够用**：ZIPformer 架构在设计时就考虑了量化，INT8 相比 FP32 在中文 WER（词错误率）上退化 <1%，这决定了"20MB 就能用"是**工程可行**而非"勉强糊弄"。

### 2.3 sherpa-onnx 与 sherpa（Kaldi Next-Gen）的历史关系

- `sherpa` 是 k2-fsa 团队做的下一代 Kaldi（C++ 原生 ASR 工具链）。
- `sherpa-onnx` 是其"离线化变体"—— 把 Kaldi 的 C++ 后端换成 ONNX Runtime 推理，去掉 GPU/CUDA 依赖，主打端侧和离线。
- 因此 sherpa-onnx 继承了 Kaldi 社区的模型生态（Zipformer、Conformer 系列）和工程规范（流式解码图、状态对齐解码器）。

---

## 三、归纳总结

### 3.1 一句话结论

> **sherpa-onnx = 一个 20MB 就能跑起来的中文语音全家桶引擎，跑在 CPU 上、不联网、12 种语言接口、开源 Apache-2.0。**

### 3.2 sherpa-onnx 五要素实操区

### ✅ 功能清单（实测可勾选）

- [ ] 中文 ASR 流式识别（Zipformer int8 20MB）
- [ ] 中文 ASR 非流式整段转写（Zipformer/Paraformer/SenseVoice）
- [ ] 文字转语音 TTS
- [ ] 静音检测 VAD（判断有没有人在说话）
- [ ] 说话人识别（判断是谁在说话）
- [ ] 说话人分离（谁在什么时候说了话）
- [ ] 语音降噪
- [ ] 人声伴奏分离
- [ ] 12 种语言 API（C++/Python/C#/Java/Go/Rust/Swift/Kotlin/Dart 等）
- [ ] Android 预编译 APK
- [ ] Apache-2.0 商用无限制

### 🎯 使用性评估

> **一句话结论**：做"离线语音原型/嵌入式 ASR/TTS 集成"的神器，做"开箱即用语音 App"要自己写壳。

- **上手成本**：低（`pip install sherpa-onnx` + 挑模型 + 几行 Python），但**没有官方 GUI**，写壳是必做工作。
- **速度上限**：取决于 CPU。树莓派 int8 可跑但未必实时；中端 PC CPU 跑旗舰模型可行；旗舰手机 CPU 跑 int8 小模型实时可行。
- **短板**：(1) 边缘场景 616 个 open issue，生产级需要自压测；(2) 多语言 API 一致性靠手动对齐，Swift/Kotlin 版本可能滞后于 C++；(3) 量化模型精度退化虽有数据支持，但**多语种/长音频/重噪声**场景下的真实退化率文章未给出，需要自行复测。

### 💡 指导性意见

1. **用 sherpa-onnx 当**：离线语音原型验证 / 嵌入式 ASR（车机、IoT、机器人）/ 桌面端语音转写工具 / 端侧实时字幕。—— 理由：CPU 即可、20MB 模型、Apache-2.0 无商用限制。
2. **不用 sherpa-onnx 当**：需要开箱即用 App 的方案 / 需要 GPU 加速高吞吐 ASR 的方案（此时 whisper.cpp 或商业 API 更合适）/ 需要严格 SLA 的语音生产系统（616 open issue 意味着仍需自测兜底）。

### 📌 案例（文章实测）

1. **Android 端离线 ASR**：下载预编译 APK → 装上断网也能用 → 挑 20MB int8 模型 → 实时字幕。
2. **桌面端整段录音转写**：`pip install sherpa-onnx` → 挑 SenseVoice 或 Paraformer → 一段 Python 调用 `offline_recognizer` → 出文字。
3. **嵌入式（树莓派/RISC-V）**：下载对应平台的 prebuilt → 挑 int8 小模型 → 跑流式识别。

### 🔧 使用方法借鉴（可直接抄）

```bash
# 1. 安装
pip install sherpa-onnx

# 2. 从 releases 页挑一个中文识别模型下载（官方提供国内镜像）
# 最小入门：streaming-zipformer-small-ctc-zh-int8 (20.3 MB)
# 旗舰：SenseVoice 多语言 (999 MB)

# 3. Python 调用（伪代码，参考仓库 examples）
import sherpa_onnx
# 建 recognizer → 喂音频 → 拿结果
# 详细调用看 github.com/k2-fsa/sherpa-onnx 的 Python examples
```

### 3.3 sherpa-onnx 与 Hermes Agent 语音栈的关系

- 当前 Hermes 语音栈：STT 走 OpenRouter（付费 API）或本地 whisper；TTS 走 LuxTTS（本地 GPU）。
- sherpa-onnx 可作为**离线 STT 降级通道**：当 OpenRouter 402/429/限流时，本地 CPU 上跑 sherpa-onnx 完成 STT，不依赖外网。
- 与现有的 `FunASR-speech-recognition` 项目互补：FunASR 侧重中文训练/微调生态，sherpa-onnx 侧重跨端离线部署。

---

## 四、趋势判断

### 4.1 端侧 ASR 正在从"能用"跨越到"好用"

2025-2026 年，开源 ASR 生态出现了三个关键信号：

1. **模型体积持续压缩**：从 Whisper-Large（1.5GB）到 sherpa-onnx 的 20MB int8，模型体积下降 75×，且精度退化 <1%。
2. **推理引擎脱离训练框架**：sherpa-onnx 选择 ONNX Runtime 而非 PyTorch 是范式转变——推理侧不再需要 GB 级的训练框架依赖。
3. **12 语言绑定 + 跨架构覆盖**：x86/ARM/RISC-V + 12 语言意味着 sherpa-onnx 可以跑在任何现代设备上。

**判断**：2026-2027 年，端侧离线 ASR 将从"科研 demo"跨越到"生产级可用"，尤其是在 IoT / 车机 / 桌面语音工具场景。

### 4.2 "模型 vs 引擎"解耦将成为开源 ASR 标准

sherpa-onnx 的核心差异化不在于"识别准"，而在于"模型与引擎解耦"。训练框架（PyTorch）、推理引擎（ONNX Runtime）、部署平台（12 语言绑定）三者各自独立、可单独升级。

**判断**：未来开源 ASR 项目的竞争力不在于"谁训练了更好的模型"，而在于"谁能把别人的模型在最小的设备上跑起来"。sherpa-onnx 踩在了这个拐点。

### 4.3 616 个 open issue 是双刃剑

- 正面：社区活跃，项目还在快速迭代。
- 负面：生产级使用时，边缘场景（Swift/Kotlin 版本一致性、长音频内存泄漏、多声道分轨等）可能踩坑。

**判断**：sherpa-onnx 在 2026 年适合**原型验证和离线降级**，2027 年若 issue 收敛到 <200 个，可考虑作为**生产主通道**。

---

## 五、关联分析

### 5.1 与 Hermes 现有语音栈的关联

> **关联项目**：[Hermes 语音系统](~/uclaw/project/) 多项目协同

| 现有项目 | 关联 | 互补方向 |
|---------|------|---------|
| `luxtts-jetson` / `f5tts-voice-clone` | Hermes TTS 主通道（GPU 合成） | sherpa-onnx 可承接**离线 STT**，形成 GPU-TTS + CPU-STT 双栈 |
| `FunASR-speech-recognition` | 中文 ASR 训练/微调生态 | sherpa-onnx 侧重**离线跨端部署**，两者可组合：FunASR 训模型 → sherpa-onnx 部署 |
| `jetson-voice-assistant` | 端侧语音助手 | sherpa-onnx 的 20MB int8 模型天然适配 Jetson Orin 的 CPU 通道（GPU 留给 TTS） |
| `voicebox` / `bidi-voice` | 语音代理系统 | sherpa-onnx 可作为 voicebox Phase 2 的**离线 STT 通道** |
| `openrouter-transcribe` | 远程 STT API | sherpa-onnx 是**离线降级通道**，当 OpenRouter 限流时本地兜底 |

**关键映射**：当前 Hermes 的 STT 依赖外网（OpenRouter），TTS 依赖本地 GPU（LuxTTS）。sherpa-onnx 可以在**STT 层**补齐"完全离线"能力——形成"外网 STT（默认）+ 本地 sherpa-onnx STT（降级）"的双通道。

### 5.2 与 Hermes Voice 现有 STT 链路的关联

**现状**：Voice STT 主链路 = OpenRouter API（付费，限流 402/429 时需降级）；
**建议**：当检测到 OpenRouter 402/429 时，自动 fallback 到本地 sherpa-onnx CPU 推理，牺牲一点精度换取"完全可用"。

**可行性估算**：
- Jetson Orin CPU：4 核 Cortex-A78AE @ 2.0 GHz，跑 20MB int8 Zipformer 流式识别，RTF（实时因子）预估 0.5-1.0（需实测验证）。
- 精度损失：相比 Whisper-Large，Zipformer-int8 中文 WER 退化约 2-4%（需实测）。

### 5.3 与端侧语音笔记的关联

- [2026-05-22-端侧离线语音待办工程实践](explore/2026-05-22-端侧离线语音待办工程实践.md)：探讨端侧离线语音的技术路线，sherpa-onnx 是该笔记的**最佳实践落地方案**。
- [2026-06-14-语音智能体闭环-Typeless-VoxCPM2](explore/2026-06-14-语音智能体闭环-Typeless-VoxCPM2.md)：Typeless 走 GPU 合成，VoxCPM2 走语音模型；sherpa-onnx 可补齐"输入端"的离线 STT。

---

## 六、拓展应用推荐

### 6.1 Hermes Voice STT 离线降级通道（P1）

**应用场景**：当 OpenRouter API 限流/402/429 时，自动 fallback 到 sherpa-onnx 本地 CPU 推理。

**实施路径**：
1. 在 `openrouter-transcribe` skill 中添加降级检测（402/429 → 触发本地 STT）
2. 在项目 `sherpa-onnx-stt-fallback` 下部署 sherpa-onnx 引擎 + 20MB int8 中文模型
3. 在 Jetson Orin 上实测 RTF 和 WER

**优先级**：P1（中优先级，不影响当前可用性，但可彻底摆脱 STT 外网依赖）

### 6.2 会议录音离线转写工具（P2）

**应用场景**：本地录音文件（.wav/.mp3）一键转文字，不上传云端。

**实施路径**：sherpa-onnx 非流式识别 API + 简单 CLI 壳

### 6.3 桌面实时字幕工具（P3）

**应用场景**：本地麦克风输入 → 实时字幕输出，完全离线。

**实施路径**：sherpa-onnx 流式识别 API + PyQt/TK 界面

---

## 七、指南分析

### 7.1 上手指南（30 分钟完成首次运行）

**前提**：Python 3.8+ 环境（Jetson Orin / PC / 树莓派均可）

```bash
# Step 1: 安装（30 秒）
pip install sherpa-onnx

# Step 2: 下载中文识别模型（1-2 分钟）
# 仓库 releases 页有国内镜像，挑 streaming-zipformer-small-ctc-zh-int8 (20.3 MB)
# 或 SenseVoice 多语言 (999 MB)

# Step 3: 写 5 行 Python 调用流式识别
# 参考 github.com/k2-fsa/sherpa-onnx 的 examples/python/
```

**核心建议**：先用 `pip install` + 最小模型跑通，**不要一上来就上旗舰模型**。

### 7.2 生产级部署 checklist

- [ ] 在目标硬件上实测 RTF（实时因子）
- [ ] 在真实业务场景（噪声/长音频/多声道）压测 WER 退化
- [ ] 确认目标语言绑定的 API 是否与 C++ 主版本一致
- [ ] 监控 sherpa-onnx GitHub issue，跟踪相关 bug 修复
- [ ] 模型与引擎版本号锁定（模型体积/接口都可能随版本变化）

### 7.3 与 Hermes 集成实施建议

1. **短期（1-2 周）**：在 `sherpa-onnx-stt-fallback` 项目下完成引擎部署 + 最小 Python 调用验证。
2. **中期（1 月）**：在 Jetson Orin 上完成 RTF / WER 实测，形成"本地 STT 通道 vs OpenRouter STT 通道"对比表。
3. **长期（3 月）**：将 sherpa-onnx 接入 Hermes Voice STT 降级链路，实现"外网 STT 故障自动 fallback 到本地"。

---

## 八、出处

- **文章链接**: https://mp.weixin.qq.com/s/-OzY1mPA3VonGsVW4JZCvg
- **GitHub**: https://github.com/k2-fsa/sherpa-onnx
- **模型下载**: https://github.com/k2-fsa/sherpa-onnx/releases
- **获取方式**: 微信 curl 移动端 UA（Android Pixel 7）直取，2026-08-20 实测成功（RAW 3.1MB → 正文 1493 字 + 标题/描述）
- **选文策略**：用户直接提供链接，与 Hermes 语音栈 STT 降级方案强相关

---

## 九、行动启示

| 启示 | 行动 | 优先级 |
|------|------|--------|
| sherpa-onnx 补齐 Hermes 语音 STT 离线能力 | 创建 `sherpa-onnx-stt-fallback` 项目，部署 20MB int8 中文模型 | P1 |
| 外网 STT 限流时无缝降级 | 在 `openrouter-transcribe` 添加 402/429 检测 → fallback 到本地 sherpa-onnx | P1 |
| Jetson Orin 上做 RTF/WER 实测 | 在项目根目录放压测脚本，记录对比数据 | P1 |
| 与 FunASR 组合（训+署分离） | 研究 FunASR 训练的中文模型导出 ONNX → sherpa-onnx 加载 | P2 |

## 相关笔记
- [端侧离线语音待办工程实践](explore/2026-05-22-端侧离线语音待办工程实践.md)
- [AISmartDetect-多模态零训练视觉检测桌面工具](2026-08-13-AISmartDetect-多模态零训练视觉检测桌面工具.md)
- [Supertonic 99M参数离线TTS引擎树莓派也能跑](2026-06-08-Supertonic 99M参数离线TTS引擎树莓派也能跑.md)
