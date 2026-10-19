# Pocket TTS CPU 实测 — 100M参数本地语音合成的Jetson验证

#PocketTTS #TTS #CPU推理 #Kyutai #本地语音 #Jetson #零API成本 #配音

> **出处**：微信公众号「零壹界点」《一个 100M 的小模型，装上你的 CPU 就会开口说话》，2026-08-16 20:10
> 原文链接：https://mp.weixin.qq.com/s/ew_DpCMP4KIfTDf29d_vDA
> 项目实测：/home/jc/uclaw/project/pocket-tts-cpu/（benchmark/full_test/stream_test 三脚本全部真实运行）
> 主题：Kyutai（Moshi 团队）开源 100M 参数 TTS，pip 一装 CPU 就跑——本笔记含 Jetson Orin Nano 真机实测数据

## 一、内容整理

### 0. 核心事件

Kyutai 实验室开源 **Pocket TTS**：100M 参数语音合成模型，官方明说装 CPU 版 PyTorch 就够。目标场景：给视频配音的人还在按字符付 API 费、排队等响应、断网罢工——Pocket TTS 把这件事搬回本地。

### 1. 文章声称的性能卡

| 项 | 声称 |
|---|---|
| 硬件要求 | 任意现代 CPU（MacBook Air M4 约 6 倍实时） |
| 首包延迟 | ~200ms |
| 资源占用 | 仅 2 个 CPU 核 |
| 预制声音 | 26 个（英文 alba → 意大利语 giovanni） |
| 语言 | 英/法/德/葡/意/西 6 种，**无中文** |
| 克隆 | --voice 接 wav 即克隆（会连录音质量一起复现） |
| 生态 | 已有人移植浏览器（WASM）、树莓派 |
| GPU | 不总是更快：M4 无加速；4 核 x86 换 T4 有 2.6 倍 |

### 2. 用法三层

```bash
pip install pocket-tts           # 安装
pocket-tts generate --text "..." --voice alba   # CLI 出片
uvx pocket-tts serve             # 网页界面 :8000，模型常驻
pocket-tts export-voice x.wav    # 声音固化秒开
```
```python
from pocket_tts import TTSModel
import scipy.io.wavfile
tts = TTSModel.load_model()
voice = tts.get_state_for_audio_prompt("alba")
audio = tts.generate_audio(voice, "Hello world")
scipy.io.wavfile.write("out.wav", tts.sample_rate, audio.numpy())
```

### 3. 边界与条款

- 不支持文本插静音停顿（官方待支持清单）
- 克隆仅限有权使用的声音；未经同意冒充真人属禁止用途

## 二、查询拓展

1. **浏览器 WASM 版**如何实现——WebGPU 推理 + 100M 模型的加载策略
2. **中文空位**：Piper 中文（拼接感）与神经中文 CPU TTS 的质量差距，会不会有 Chinese-Pocket 级开源
3. **Moshi 技术传承**：全双工对话模型团队的流式优化（200ms 首包）如何下沉到 TTS
4. **与 Piper/RHVoice 传统 CPU TTS 对比**：神经小模型 vs 拼接引擎的 MOS 分差
5. **配音 API 经济学**：按字符计费（火山/阿里）在中低质量场景的定价权还能守多久

## 三、归纳总结

| 维度 | 要点 |
|---|---|
| 一句话 | 100M 参数 TTS 让任意 CPU 免费开口——装好即用、零 API、断网可用 |
| 定位 | 无 GPU 环境的英文离线 TTS 生态位（树莓派/老机器/浏览器/服务器无卡） |
| 快的机制 | 小模型 + 单批处理 + 强单核 CPU 流式输出（1 秒听完时已生成 6 秒） |
| 本机实测 | Jetson Orin CPU：RTF 2.02-2.16x（**慢于实时**）、流式首包 622ms——与 M4 差距明显但批量可用 |
| 克隆真相 | pip 默认装的是 without-voice-cloning 变体，真克隆需 HF 接受条款+登录（gated 权重） |
| 部署坑 | pip 会拖 2GB CUDA13 依赖（CPU 用不到）；HF 连接不稳时设 HF_HUB_OFFLINE=1 |

## 四、趋势判断

1. **TTS 硬件门槛归零**：100M 级模型把"开口说话"降到任意 CPU——配合本地 LLM（Ollama/Qwen3.8-27B 本地部署），完整离线语音栈闭环成型（我们 Jetson 上已有 ASR+LLM，缺的就是 CPU 兜底 TTS）
2. **配音按字符计费模式在中低端市场终结**：批量配音（视频字幕/文章朗读）本地免费无限——云端 API 的护城河收窄到高质量情感表达（IndexTTS2 级）与中文
3. **gated 克隆权重成行业标配**：Kyutai"接受条款才给克隆权重"是防 voice scam 的范式——开放生成、收紧克隆，将与 KYC 式身份验证结合
4. **小模型×强单核是被低估的组合**：M4 类 ARM 大核 + 100M 模型 = 无风扇静音语音——嵌入式语音交互（esp32-cam 项目、陪伴机器人）的工程新选项
5. **Jetson 类 SoC 的 CPU 推理价值重估**：GPU 被 LLM 占满时，TTS 走 CPU 通道可并行不争抢——Hermes 语音链路的负载分离思路

## 五、关联分析

### 与已有笔记/体系的关联

| 关联对象 | 关系 | 说明 |
|---|---|---|
| 项目 `pocket-tts-cpu`（本次创建） | 实测载体 | 三脚本真机运行：RTF/首包/克隆链路全验证，README 含与 6 个 TTS 项目对比矩阵 |
| skill `luxtts-jetson` | 主力对照 | LuxTTS=GPU 中文克隆（RTF 0.67x），pocket=CPU 英文兜底（RTF 2.1x）——场景路由器已写入 docs/jetson-integration.md |
| skill `f5tts-voice-clone` / `tts-deployment` | 技术谱系 | 三者构成 Jetson TTS 部署知识三角：零样本克隆/CUDA 部署/CPU 轻量 |
| 笔记《2026-08-18-AI时代个体内容变现八方向》 | 商业落地 | pocket-tts 直接支撑方向⑤数字产品——配音成本归零让"模板+音频"类产品毛利趋 100% |
| 项目 `kai-sound-tts` | 路线分叉实证 | 火山 API 付费路线 vs 本地免费路线的活对照，同一主人两条技术路线并存 |
| 笔记《2026-08-18-数字公地清单》 | 生态样本 | Kyutai 开源模式（研究非营利实验室）是数字公地清单第 21 项的候选 |

### 对我们的直接价值（吸收+优化自我）

1. **Hermes TTS 降级链新成员**：`text_to_speech` 可加 pocket provider（英文+无网络场景）——edge(云端)→luxtts(GPU)→pocket(CPU兜底) 三级链
2. **实测修正文章叙事**：Jetson CPU RTF 2.1x ≠ 文章 M4 的 6x 实时——硬件鸿沟必须本机实测，不能照抄宣传数字（这正是"项目实测"价值）
3. **pip 依赖瘦身模式**：`--no-deps` + 手动最小依赖，Jetson 上避免 2GB 无用 CUDA 包——可写入 jetson-orin-platform skill 的安装惯例
4. **批量配音管道素材**：视频/笔记朗读的音频化（homepage 笔记配音频）用 serve 常驻模式批处理，RTF 2x 下 10 分钟音频约 20 分钟出——夜间 cron 可完成

→ 项目实测：/home/jc/uclaw/project/pocket-tts-cpu/README.md
→ 相关：2026-08-18-AI时代个体内容变现八方向-从时间换钱到资产复利的完整阶梯.md
→ 相关：2026-08-18-数字公地清单-世界上最接近共产主义的地方20项.md

## 相关笔记
- [语音克隆TTS-2026开源新势力格局](explore/2026-06-05-语音克隆TTS-2026开源新势力格局.md)
- [fish-audio-s2-pro-deep-20260524](explore/2026-05-24-fish-audio-s2-pro-deep-20260524.md)
- [f5-tts-voice-cloning-incremental](explore/2026-05-18-f5-tts-voice-cloning-incremental.md)
- [Kai-Sound-TTS源码分析](2026-06-09-Kai-Sound-TTS源码分析.md)
