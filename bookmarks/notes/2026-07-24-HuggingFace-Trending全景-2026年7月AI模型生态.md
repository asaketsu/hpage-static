# 2026年7月 HuggingFace Trending 全景：AI 模型生态前沿速览

> 从 HuggingFace Trending API 抓取本周热门模型/数据集，提炼出 5 个值得关注的趋势：极限量化革命、975B MoE 开源、OCR 无限长解析、推理蒸馏工业化、端侧 WebGPU 推理。

📅 2026-07-24 | 🔖 HuggingFace, Trending, LLM, MoE, OCR, 量化, 蒸馏

---

## 本周 Top 5 趋势速览

| 排名 | 项目 | 类型 | 核心数据 | 趋势信号 |
|------|------|------|---------|---------|
| 1 | baidu/Unlimited-OCR | Model | 2.4M dl, 2860 likes | OCR 无限长文档一次解析 |
| 2 | thinkingmachines/Inkling | Model | 975B/41B MoE, 1494 likes | Mira Murati 新公司首个开源大模型 |
| 3 | prism-ml/Bonsai-27B | Model | 1.9M dl, 615 likes | 1-bit 极限量化，27B 塞进 3.9 GB |
| 4 | zai-org/GLM-5.2 | Model | 596K dl, 4360 likes | 我们正在用的模型，MoE DSA 架构 |
| 5 | SupraLabs/reasoning-corpus-5M | Dataset | 500万条推理链 | 推理蒸馏数据集工业化 |

---

## 深度拆解

### 1. Baidu Unlimited-OCR：长文档解析的范式跃迁

**一句话：** 基于 Deepseek-OCR 的进一步突破，实现任意长文档的一次性端到端解析（One-shot Long-horizon Parsing）。

- **架构：** 3.3B 参数 image-text-to-text 模型，MIT 协议
- **能力：** 无需分页/分块，直接处理超长文档（论文、报表、书籍）
- **生态：** 已支持 vLLM、ModelScope、ms-swift 训练，Baidu Cloud 部署
- **对标：** 比 Deepseek-OCR 更进一步，定位"无限长度"

**价值评估：** 对我们文档数字化管线（软著材料生成、PDF 摘要）有直接价值——当前 pipeline 依赖分页 OCR 再拼接，Unlimited-OCR 可简化为单次调用。

---

### 2. Thinking Machines Inkling：975B MoE 开源 multimodal

**一句话：** Mira Murati（前 OpenAI CTO）的 Thinking Machines Lab 发布首个开源大模型，975B 总参数 / 41B 激活 MoE，原生多模态（文本+图像+音频）。

**架构亮点：**
- 66 层 decoder-only transformer
- **稀疏 MoE：** 256 个专家中每个 token 路由到 6 个 + 2 个共享专家
- **混合注意力：** local + global 层混合
- **原生多模态：** 图像/视频通过层次化 patch encoder，音频通过离散 token 编码，投影到共享隐藏空间
- 支持 BF16 和 NVFP4 精度

**Benchmark 表现（effort=0.99）：**

| 基准 | Inkling | GLM 5.2 | Claude Fable 5 (max) | GPT 5.6 Sol (xhigh) |
|------|---------|---------|---------------------|---------------------|
| AIME 2026 | 97.1% | 99.2% | – | 99.9% |
| GPQA Diamond | 87.2% | 89.5% | 92.6% | 94.1% |
| SWE-Bench Verified | 77.6% | – | 95.0% | – |
| Terminal Bench 2.1 | 63.8 | 82.7 | 84.6 | 89.5 |
| MCP Atlas | 74.1% | 77.8% | 83.3% | 81.8% |
| HLE (text) | 29.7% | 40.1% | 53.3% | 47.2% |

**洞察：**
- Inkling 在开源权重模型中第一梯队，但 HLE（最难推理基准）仍落后 GLM 5.2 约 10 个点
- **GLM 5.2 的 Terminal Bench 82.7 极为突出**——在 agentic coding 方面超过了大部分开源对手，仅次于 Claude Fable 5 和 GPT 5.6
- MCP Atlas（工具调用）GLM 5.2 也达 77.8%，说明我们当前使用的模型在 agentic 场景有竞争力

---

### 3. Bonsai 极限量化：1-bit 时代到来

（详见独立笔记 `2026-07-24-Bonsai-1bit-Ternary极限量化-27B模型塞进手机.md`）

核心：Qwen3.6-27B → 1.125 bit/权重 → 3.9 GB → 保留 89.5% 智能推理能力。**量化不再是压缩，而是重新训练。**

---

### 4. GLM-5.2（我们正在使用的模型）

- **架构标签：** `glm_moe_dsa` — MoE + DSA（Dynamic Sparse Attention）
- MIT 协议，中英双语
- 关联论文：arxiv:2602.15763, arxiv:2603.12201
- HLE (text only) 40.1% — 在开源模型中领先
- Terminal Bench 2.1 达 82.7 — agentic coding 极强
- **MCP Atlas 77.8%** — 工具调用能力第一梯队

---

### 5. Reasoning Corpus 5M：推理蒸馏工业化

**一句话：** SupraLabs 汇编了 500 万条来自 DeepSeek-v4、Qwen3.6、Gemma4 等顶级模型的推理链，专门用于训练 SLM（小语言模型）。

**数据组成 Top 5 来源：**

| 来源 | 占比 | Token 数 | 行数 |
|------|------|---------|------|
| glaiveai/reasoning-v1-20m | 19.52% | 1.75B | 1.05M |
| PrimeIntellect/INTELLECT-3-SFT science | 9.87% | 883M | 298K |
| PrimeIntellect/INTELLECT-3-SFT am_chat | 8.28% | 741M | 407K |
| BAAI/OpenSeek-Synthetic-Reasoning | 6.34% | 568M | 674K |
| nvidia/Nemotron-Cascade-SFT | 4.93% | 441M | 305K |

**价值：** 将大模型的 thinking trace 蒸馏到小模型，是 2026 年端侧 AI 的核心路径。配合 Bonsai 量化，可实现"小而精"的边缘推理模型。

---

## 其他值得关注

| 项目 | 类型 | 说明 |
|------|------|------|
| webml-community/bonsai-webgpu-kernels | Space | Bonsai 在浏览器 WebGPU 中运行，300 likes |
| openbmb/UltraX-Preview | Dataset | OpenBMB 新数据集 |
| ICML-2026-agent-repro/challenge | Space | ICML 2026 Agent 复现挑战赛 |
| markov-ai/gaming-500-hours | Dataset | 游戏场景数据，209 likes |
| Manusagents 蒸馏数据集 | Dataset | GPT-5.5+Gemini-3.1+Grok-4+Claude-Fable-5 多模型蒸馏 |

---

## 对我们系统的启示

### 🎯 可执行项

1. **评估 Unlimited-OCR 替换当前 OCR pipeline** — 软著 PDF、文档摘要等场景，减少分页拼接复杂度
2. **Bonsai 量化在 Jetson 上验证** — Ternary 版本 7.2 GB 可能在 Orin Nano 上可行，用于离线推理备份
3. **Reasoning Corpus 用于 Skill 优化** — 提取推理链模式，改进 Agent 的 thinking trace 质量
4. **WebGPU Bonsai kernels** — 浏览器端推理值得关注，可能成为 homepage 交互式 AI 功能的基础

### 📊 竞争格局判断

- **开源 vs 闭源差距收窄：** GLM 5.2 在 Terminal Bench 已超越多数场景需求，agentic coding 可用性大幅提升
- **量化不再是事后处理：** Bonsai 证明从训练阶段对齐低比特表示是正确路径，传统 PTQ 在 sub-4-bit 会崩溃
- **多模态成为标配：** Inkling（文+图+音）、Unlimited-OCR（长文档）、GLM-5.2（多模态 MoE）都指向原生多模态

---

## 来源

- 🤗 [HuggingFace Trending API](https://huggingface.co/api/trending)（2026-07-24 抓取）
- 🤗 [baidu/Unlimited-OCR](https://huggingface.co/baidu/Unlimited-OCR)
- 🤗 [thinkingmachines/Inkling](https://huggingface.co/thinkingmachines/Inkling)
- 📄 [Unlimited-OCR arXiv](https://arxiv.org/abs/2606.23050)
- 🤗 [SupraLabs/reasoning-corpus-4K-5M-v1](https://huggingface.co/datasets/SupraLabs/reasoning-corpus-4K-5M-v1)


## 相关笔记

- [Bonsai 1bit 极限量化 27B 模型塞进手机](./2026-07-24-Bonsai-1bit-Ternary极限量化-27B模型塞进手机.md) — 极限量化革命代表
- [KV-Cache 压缩与长上下文推理优化全栈](./2026-07-27-KV-Cache压缩与长上下文推理优化全栈.md) — 推理优化系统侧
- [嵌入式 AI TinyML 现状](./2026-07-19-嵌入式AI-TinyML现状-从MCU感知到端侧小语言模型.md) — 端侧 WebGPU 推理趋势
