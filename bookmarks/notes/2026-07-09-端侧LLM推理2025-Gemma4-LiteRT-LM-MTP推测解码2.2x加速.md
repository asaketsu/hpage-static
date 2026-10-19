# 端侧 LLM 推理 2025 突破：Gemma 4 + LiteRT-LM + MTP 推测解码 2.2x 加速

> 学习笔记 · 2026-07-09 · 夜间自学习
> 来源：Google AI Edge 官方博客 + sanj.dev + NVIDIA Developer Forums
> 关联：Jetson Orin 平台、TinyML、LLM 推理优化

## 一句话结论

Google AI Edge 推出 **LiteRT-LM** 引擎，配合 **Gemma 4** 模型与 **Multi-Token Prediction (MTP) 推测解码**，在移动端实现 **2.2x 推理加速**和 **4.2x 内存压缩**（2.58GB 模型仅占 607MB 物理内存），标志着端侧 LLM 从"能跑"进入"跑得快、跑得起 Agent"的新阶段。

## 一、LiteRT-LM 引擎核心

LiteRT-LM = LiteRT（原 TensorFlow Lite）运行时 + Google AI Edge 加速栈，已驱动 Chrome、ChromeOS、Pixel Watch、AI Edge Gallery 等产品。

### 跨平台覆盖

| 平台 | 后端 | API |
|------|------|-----|
| Android | CPU / GPU / NPU | 原生 |
| iOS | Apple Silicon | 全开源 Swift API |
| Web | WebGPU | JavaScript API |
| 桌面 | LiteRT-LM CLI | 跨平台 |

核心理念：**"build once, peak performance everywhere"**。

## 二、MTP 推测解码 — 2.2x 加速的关键

### 传统推测解码的瓶颈

推测解码（Speculative Decoding）通常用"小模型起草 + 大模型验证"，但端侧的瓶颈在于**跨硬件 IP 的数据搬运**——draft 模型和主模型在不同加速器上时，KV cache 传输开销吞噬了加速收益。

### MTP 的三个工程突破

| 突破 | 做法 | 收益 |
|------|------|------|
| **内存局部性** | MTP drafter 与主模型跑在**同一硬件 IP** | 消除跨核搬运 |
| **共享 KV cache** | 主模型和 drafter 共享 KV cache 与 activation | 省内存 + 省计算 |
| **核优化** | 验证阶段 kernel 最大化并行 | 提升验证吞吐 |

最终效果：**最高 2.2x 端到端加速**。

> 💡 与 SpecSA（我们 07-08 笔记覆盖的稀疏推测解码）互补——MTP 走"硬件亲和 + 共享缓存"路线，SpecSA 走"稀疏激活降低 draft 成本"路线。

## 三、内存优化 — 4.2x 压缩

LiteRT-LM 的内存策略：

1. **Per-Layer Embeddings (PLEs) 不驻留内存** — 按需加载
2. **图像/音频编码器动态加载** — 仅在该任务需要时载入
3. **Session Save/Restore** — 大 KV cache 状态可序列化跨 session 保存，回归用户跳过 prefill 阶段

实测：Gemma 4 E2B 模型（~2.58GB）在 Apple 移动 CPU 上仅占 **607MB 物理内存**。

## 四、Agentic 能力 — 端侧跑 Agent

LiteRT-LM 不只是推理引擎，内置 Agent 工作流支持：

| 能力 | 说明 |
|------|------|
| **Thinking Mode** | 独立 scratchpad 做逐步推理后再行动，提升输出质量 |
| **Constrained Decoding** | 强制 JSON schema / 输出语法，彻底消除 parser 报错 |
| **Function Calling** | 暂停执行 → 返回结构化 tool-call → 收到结果后恢复 |

这意味着端侧设备可以跑完整 Agent 循环（推理→工具调用→恢复），不只是单轮问答。

## 五、小模型生态对比（2025）

| 模型 | 参数量 | RAM | 速度 (tok/s) | MMLU | 定位 |
|------|--------|-----|-------------|------|------|
| GPT-4o | 1T+ | N/A(云) | ~60 | 86% | 云端复杂推理 |
| Llama-3.1 8B | 8B | 8GB | 15-25 | 69% | 笔记本 CPU |
| Mistral 7B | 7B | 6GB | 45-80 | 60% | 消费级 GPU |
| Phi-3.5 Mini | 3.8B | 4GB | 12-20 | 69% | 移动 ARM |
| TinyLlama | 1.1B | 2GB | 25-40 | 25% | 边缘设备 |
| **Gemma 3 270M** | 0.27B | 0.7GB | 20-35 | N/A | **手机本地** |

### Gemma 3 270M 亮点

- 仅 270M 参数（170M embedding + 100M transformer），256k 词表，INT4 量化
- Pixel 9 Pro 上 25 轮对话耗电 **<1%**
- 擅长指令遵循、文本结构化、分类——不适合通用知识问答

## 六、何时不该用小模型

- 复杂推理（数学、代码生成、科研）
- 长上下文（长文档分析、多轮交叉引用）
- 多模态（图像/视频/音频）
- 通用知识与多语言创造力

> 选型原则：**通用智能选大模型，专用效率选小模型。**

## 七、对 Jetson/Hermes 体系的启示

| 维度 | 启示 |
|------|------|
| **Jetson Orin 部署** | MTP 共享 KV cache 思路可直接用于 Jetson TensorRT 部署，drafter 与主模型同 GPU 避免跨设备搬运 |
| **本地 Agent** | nexa-local-inference（Ollama on Jetson）可借鉴 LiteRT-LM 的 Thinking Mode + Function Calling 设计完整 Agent 循环 |
| **量化策略** | PLE 不驻留内存 + 编码器动态加载，是 INT4 之外的新优化维度 |
| **Session 持久化** | KV cache 序列化跨 session 恢复，可减少重复 prefill，值得引入 Hermes 会话管理 |
| **模型选型** | Gemma 3 270M 适合做端侧"指令路由器/分类器"，主推理走云端大模型 |

## 八、核心判断

- 端侧 LLM 的竞争焦点已从"参数量/精度"转向**"推理延迟、内存占用、Agent 能力"**
- MTP 推测解码 + 共享缓存是 2025 年端侧加速的最大工程突破，2.2x 是实打实的
- 端侧 Agent（Thinking + Function Calling + Constrained Decoding）意味着隐私优先的离线 Agent 工作流成为现实
- 小模型（<1B）定位清晰：专用任务 + 低功耗 + 隐私，不与大模型竞争通用能力

## 参考来源

- [Blazing fast on-device GenAI with LiteRT-LM - Google AI Edge](https://developers.googleblog.com/blazing-fast-on-device-genai-with-litert-lm)
- [Why Small LLMs Are the Future of AI in 2025 - sanj.dev](https://sanj.dev/post/small-llms-are-the-future)
- [Bringing AI Closer to the Edge with Gemma 4 - NVIDIA](https://forums.developer.nvidia.com/t/bringing-ai-closer-to-the-edge-and-on-device-with-gemma-4/365483)
- LiteRT-LM 代码：https://github.com/google-ai-edge/LiteRT-LM

## 相关笔记

- [LLM推理优化2026-SMoE端侧部署-SpecSA](./2026-07-08-LLM推理优化2026突破-SMoE端侧部署-SpecSA稀疏推测解码.md) — SpecSA稀疏推测解码，同为端侧加速前沿
- [20260506 MLA MTP技术分析](./20260506_MLA_MTP技术分析.md) — MTP技术深度分析，推测解码理论基础
- [推理加速深度解析-投机解码-KVCache](./2026-05-08-推理加速深度解析-投机解码-KVCache-连续批处理.md) — 投机解码与KVCache基础原理
- [LLM推理优化前沿技术2026](./2026-04-28-LLM推理优化前沿技术2026.md) — 推理优化全景，端侧部署趋势
- [ESP-VISION乐鑫边缘AI视觉](./2026-07-08-ESP-VISION-乐鑫边缘AI视觉低代码框架分析.md) — 同为端侧AI部署，ESP32视觉低代码框架
- [Coglet开源桌面陪伴机器人](./2026-07-08-Coglet-开源桌面陪伴机器人全栈架构深度分析.md) — 端侧LLM推理在陪伴机器人中的实际应用
