# Transformer 作者开源 Command A+：2180亿参数 Apache 2.0 真开源旗舰

> **来源**：新智元 · 36kr · 2026-05-22
> **原文**：https://www.36kr.com/p/3820298133819778
> **格式**：双格式(MD + HTML) · 含借鉴进化点
## 相关笔记

- [[2026-05-10-DeepSeek-V4-开源模型新格局]]
- [[2026-04-05-Google-Gemma4-open-source]]
- [[2026-05-05-开源AI模型2025-DeepSeek-Qwen新格局]]
- [[2026-05-21-MLA多头潜在注意力-DeepSeek-KV缓存压缩与推理优化]]
- [[2026-05-11-5月AI模型大战-GPT55-DeepSeekV4]]


## 摘要

Cohere 联合创始人 Aidan Gomez（Transformer 论文 8 位作者之一，当时仅 20 岁）发布 Command A+，这是 Cohere 首个 MoE 架构模型，218B 总参数 / 25B 激活参数，Apache 2.0 许可证，可跑在单张 B200 或双 H100 上。这是 AI 头部公司首次将旗舰模型以真正开源（非 NC）许可发布，意义重大。

## 核心内容

### 1. MoE + 量化双重压缩
- 218B 总参数，每次只激活 25B，通过 MoE 路由到最擅长的「专家」网络
- W4A4 量化方案：MoE 专家压到 4-bit，注意力通路保留全精度
- 量化感知蒸馏（Quantization-Aware Distillation）技术，号称接近无损
- W4A4 版本低并发下 375 tokens/s，首 token 延迟 113ms

### 2. 单卡部署的工程突破
- 最低配置：1× NVIDIA B200 或 2× H100
- 从千亿级模型需要整个 GPU 集群 → 一台机器搞定
- BF16 / FP8 / W4A4 三种精度版本可选

### 3. Apache 2.0：真开源的里程碑
- 此前 Command R/R+ 使用 CC-BY-NC 4.0（禁止商用）
- Command A+ 切换到 Apache 2.0（OSI 认可的真正开源）
- 任何人可使用、修改、分发并商业化，无授权费，无竞业条款
- 由联合创始人 Nick Frosst（Hinton 门生）力主推动

### 4. 原生引用（Native Citation）
- 模型原生生成 grounding spans（溯源标记）
- 每条事实声明直接链接到引用的具体文档/数据库记录
- 面向金融、医疗、法律等需要可信输出的生产环境

### 5. 性能数据（Cohere 自发布）
- T-Bench Telecom：37% → 85%
- Terminal-Bench Hard（智能体编码）：3% → 25%
- AIME 25 数学：57% → 90%
- ⚠️ 注意：这些是 Cohere 自己发布的数据，非第三方独立评测
- VentureBeat 评价：推理和数学可媲美更大模型，但深度 Agent 编码和综合智能广度仍落后于 DeepSeek 等

## 关键概念

- **MoE（Mixture of Experts）**：混合专家架构，将输入路由到最擅长的子网络，其余休眠，降低运行时算力
- **量化感知蒸馏（QAD）**：在训练/蒸馏阶段就考虑量化误差，使量化后模型接近无损
- **W4A4 量化**：权重 4-bit，激活 4-bit 的高度压缩方案
- **Apache 2.0**：OSI 认可的开源许可证，允许商用、修改、分发，无竞业限制

## 能力边界

- 单卡运行需要 B200（数据中心级），非消费级显卡
- Agent 编码和综合智能广度仍落后于中国头部开源模型（如 DeepSeek）
- 性能数据来自自发布，未经第三方独立验证
- 128K 上下文窗口，相比竞品的更长上下文仍有差距

## 🔍 借鉴学习进化点（必填）

| # | 点 | 原文要点 | 对当前系统的借鉴 | 行动计划 |
|---|-----|---------|---------------|---------|
| 1 | 量化策略 | MoE 专家 4-bit + 注意力全精度，关键路径保精度 | Hermes 本地模型部署可采用类似分层量化策略 | 评估 llama.cpp GGUF 量化时的注意力层保留方案 |
| 2 | 原生引用设计 | 模型输出嵌入溯源标记，链接到原始文档 | Agent 输出可增加来源标注，提升可信度 | 在 Hermes skill 输出中增加 source annotation 格式规范 |
| 3 | 开源许可选择 | 从 CC-BY-NC 转 Apache 2.0 的决策逻辑 | 自研 skill/template 的许可策略参考 | 审查 Hermes skill 发布许可，确保与目标一致 |
| 4 | MoE 效率范式 | 25B 激活实现 218B 级知识，算力效率极大化 | Agent 系统可借鉴：按任务路由到专业 skill，不全部加载 | 优化 skill 路由机制，避免全量加载 |
| 5 | 蒸馏+量化联合 | 量化感知蒸馏解决「量化税」问题 | 本地小模型部署可复用类似技术栈 | 关注 Ollama/llama.cpp 的 QAD 支持进展 |

## 🔗 RAG / Wiki 联动

### 当前状态
- 本地已有 AI 基础设施相关笔记（Colossus2, GPU 优化, Anthropic 盈利等）
- 建立了开源模型追踪体系

### 改进方案
1. 将 Command A+ 加入本地可选模型评估清单
2. 跟踪 Apache 2.0 开源模型的生态发展

### 已执行操作
- ✅ 笔记已写入 bookmarks/notes
- ⏳ 待评估 Command A+ 作为本地推理候选的可行性

## 关联

- [Anthropic Colossus2 GB200 AI基础设施军备竞赛](2026-05-22-Anthropic-Colossus2-GB200-AI基础设施军备竞赛.md)
- [Anthropic首度盈利 击碎AI泡沫论](2026-05-22-Anthropic首度盈利-击碎AI泡沫论.md)
- [不加GPU多榨15%算力 大模型网络优化](2026-05-22-不加GPU多榨15%算力-大模型网络优化.md)
