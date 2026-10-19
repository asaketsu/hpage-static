# How LLMs Actually Work：Transformer 架构从 Token 到生成的完整路径

> **来源**：0xkato · 0xkato.xyz · 2026-06-01
> **原文**：https://www.0xkato.xyz/how-llms-actually-work/
> **笔记ID**：sniff-20260606-how-llms-work
> **格式**：双格式(MD + HTML) · 含借鉴进化点 · RAG/wiki联动

## 摘要

这是一篇面向工程师的 LLM 架构深度解析，从 Token 化开始，逐步讲解 Embedding、位置编码（RoPE）、Self-Attention、Multi-Head Attention、Feed-Forward Network、Residual Stream 等核心组件，最终到 next-token prediction 的生成循环。文章特点是「去数学化」但保留精确性——用直觉和类比解释每个模块的工程意义，让读者能直接读懂现代 LLM 论文和模型卡。HN 570 pts，26 分钟长文，质量极高。

## 核心内容

### 1. Tokenization：文本→整数的桥梁

现代 LLM 使用子词分词（subword tokenization），而非整词或字符级。BPE（Byte Pair Encoding）是 GPT 系列的标准，SentencePiece 在 LLaMA 系中常见。

关键洞察：
- 「strawberry 有几个 R」的失败不是模型能力问题，而是 token 边界不对应字母边界
- 分词效率直接影响计算量：更少的 token = 更少的 FLOPs
- 不同模型家族的分词器不互通，这是迁移成本的一部分

### 2. Embedding：从整数到语义空间

Embedding Matrix 是 vocab_size × hidden_dim 的查找表。7B 模型通常 hidden_dim=4096。

关键性质：
- 语义相近的 token 在向量空间中距离近（king ≈ queen）
- 向量算术有效：king - man + woman ≈ queen
- 这些性质从训练中涌现，非硬编码

### 3. Positional Encoding：从 Sinusoidal 到 RoPE

位置编码的演进：
- Vaswani 2017：Sin/Cos 绝对位置，加到 embedding 上
- 问题：训练长度外的位置泛化差，且 embedding 同时承载语义和位置
- RoPE（2021）：旋转位置编码，通过旋转向量编码相对距离
- RoPE 优势：相对位置自然编码、长上下文泛化更好、不增加参数

### 4. Attention：Token 间的信息共享

Self-Attention 的核心公式 QKV：
- Q（Query）：当前 token 想知道什么
- K（Key）：每个 token 能提供什么信息
- V（Value）：实际传递的信息内容

注意力模式（Attention Pattern）的可解释性：可以可视化 token 间的信息流向。

### 5. Multi-Head Attention：并行多维度关系追踪

每个 head 独立学习不同类型的关系：语法、语义、指代、位置等。Head 数量和维度是架构选择的关键超参。

### 6. Feed-Forward Network：模型存储结构的主要容器

FFN 是 2 层 MLP，hidden 维度通常是 model dim 的 4 倍。文章指出 FFN 存储了模型大部分的「结构化知识」——这呼应了 recent research on knowledge neurons。

### 7. Residual Stream + LayerNorm：深度堆叠的可训练性

Residual connection 让梯度可以直接回传到任意浅层。LayerNorm 稳定训练。Pre-norm vs Post-norm 的选择影响训练稳定性。

### 8. Next-Token Prediction + Generation Loop

模型输出的是 vocab_size 维的 logits，经 softmax 变概率分布。生成策略（temperature、top-k、top-p）控制采样随机性。

## 关键概念

- **RoPE**：Rotary Position Embeddings，旋转位置编码，当前主流方案
- **Attention Pattern**：注意力权重矩阵，可视化 token 间信息流
- **Residual Stream**：残差流，Transformer 各层的共享信息通道
- **FFN as Memory**：前馈网络作为知识存储的核心载体

## 能力边界

- 文章不涉及训练细节（loss function、optimizer、数据配比）
- 未讨论 MoE、GQA、KV Cache 等现代优化
- 对 inference 优化（speculative decoding、continuous batching）未提及

## 最佳实践

- 理解架构有助于读懂模型卡和论文的 architecture section
- RoPE 是理解长上下文扩展技术（如 YaRN、LongRoPE）的基础
- Residual stream 视角有助于理解 mechanistic interpretability 工作

## 🔍 借鉴学习进化点（必填）

| # | 点 | 原文要点 | 对当前系统的借鉴 | 行动计划 |
|---|-----|---------|---------------|---------|
| 1 | Tokenization 影响 Agent 行为 | 「strawberry」失败是 token 边界问题，非推理能力问题 | Hermes Agent 处理文本时需注意分词边界对 LLM 计数/字符串操作的影响，在 skill 中添加分词陷阱提示 | 在 agent-health-check skill 中增加「LLM 字符/单词计数不可靠」的已知限制说明 |
| 2 | RoPE 长上下文扩展 | RoPE 通过旋转编码相对位置，天然支持外推 | 理解 RoPE 有助于评估不同模型的长上下文能力，指导 model-adapter skill 的模型选择逻辑 | 在 model-adapter skill 中添加「RoPE-based 模型通常长上下文表现更好」的选择指引 |
| 3 | FFN 存储结构化知识 | FFN 是模型「记忆」的主要载体，非 attention | 理解这一点有助于设计 knowledge injection 策略——修改 FFN 权重可能比修改 attention 更直接影响知识 | 在 RAG/wiki-knowledge-base 的知识注入策略中考虑 FFN 层面 |
| 4 | Residual Stream 作为信息总线 | 各层读写同一个 residual stream，类似总线架构 | Hermes Agent 的 MEMORY.md 设计可类比：多层 skill 读写同一记忆流，需确保不互相覆盖 | 在 memory-system skill 中明确「记忆写入需幂等，避免 skill 间覆盖」原则 |
| 5 | 去数学化的技术写作范式 | 文章用直觉+类比替代公式，26 分钟读完且精确 | 我们的 skill 文档和笔记也可采用这种风格：先给直觉再给细节 | 在 skill-doc-standard skill 中增加「直觉优先」写作指引 |

## 🔗 RAG / Wiki 联动（必填）

### 当前状态
- wiki-kb: PageIndex + RAG 双引擎运行中
- RAG: 关键词+语义向量混合检索
- Memory: 三层分离（SOUL/MEMORY/USER）

### 改进方案
1. 将本文的 Transformer 架构知识结构化为 wiki 页面，包含各组件的精确定义
2. 在 RAG 索引中增加「LLM 架构」主题向量，提升相关查询命中率

### 已执行操作
- ✅ 笔记已写入 bookmarks/notes/
- ⏳ wiki 页面待下次会话创建

## 关联

[How LLMs Actually Work](2026-06-06-How-LLMs-Actually-Work-Transformer架构从Token到生成_tech-blue.html)
[Multi-Stream LLMs](2026-05-22-Multi-Stream-LLMs-并行流解锁语言模型.md)
[Antigravity 2.0](2026-05-23-Antigravity2.0-OpenSCAD-LLM-Benchmark-AI编程3D建模能力.md)

## 相关笔记
- [2026-05-16-LLM推理优化-MoE量化加速全景](2026-05-16-LLM推理优化-MoE量化加速全景.md) (关键词: LLM, 推理优化)
- [2026-05-22-Multi-Stream-LLMs-并行流解锁语言模型](2026-05-22-Multi-Stream-LLMs-并行流解锁语言模型.md) (关键词: LLM, 语言模型)
- [2026-04-28-LLM推理优化前沿技术2026](2026-04-28-LLM推理优化前沿技术2026.md) (关键词: LLM, 推理优化)
- [2026-06-06-Gemma4-QAT量化感知训练-移动端推理优化](2026-06-06-Gemma4-QAT量化感知训练-移动端推理优化.md) (关键词: 推理优化)
