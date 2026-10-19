---
title: 文档解析工具：Contextual Retrieval 数学对比（vs Late Chunking）
date: 2026-10-18
source: Anthropic 官方 / arXiv 2504.19754 (ECIR 2025) / Jina AI Part II / KX Systems / CDE (ICLR 2025)
tags: [RAG, chunking, contextual-retrieval, late-chunking, 文档解析]
---

#RAG #chunking #contextual-retrieval #late-chunking

# 文档解析工具：Contextual Retrieval 数学对比（vs Late Chunking）

> 探索日期: 2026-10-18 | 兴趣等级: L2 | 类型: auto-explore（增量深挖）
> 前序笔记: 2026-10-15-jina-embeddings-v3-Late-Chunking文档级嵌入 / 2026-10-18-文档解析工具-Parent-Child分层索引 / 2026-10-10-文档解析工具-三引擎分层pipeline_vlm_hybr

## 摘要（归纳总结）

三种方法都在逼近同一个理想量 E_true(Dᵢ | D)，差别只有两点：**上下文以什么形式进入嵌入**，以及**代价按什么规模增长**。Late Chunking 让上下文经注意力隐式进入，代价是注意力项变成 O(|D|²)（等于块数倍的 naive）；Contextual Retrieval 让上下文以 ≤100 token 的自然语言显式拼进块再嵌入，代价是每块一次 LLM 调用。本篇把成本模型算到可复算：Anthropic 口径下缓存版 **USD 1.03/M doc token**（官方报 1.02，误差 1%），无缓存 2.92；同语料嵌入本身只要 0.018/M，即 **57× / 162×** 的相对倍数。ECIR 2025 统一实验的判决是 Contextual 小幅胜出（同子集 NDCG@5 0.317 vs 0.309；NDCG@10 0.308 vs 0.294），但 Late 便宜一个数量级；且 Late 有硬前置条件——**必须 mean pooling**，在 CLS 池化的 BGE-M3 上直接崩（NDCG@5 0.246 → 0.070，-72%）。结论：先做零成本的确定性 context prefix（标题路径），再谈这两个贵方案。

## 关键发现与内容整理

### 1. 统一数学表述：三个算子，一个目标

设文档 D = 词元序列 {d₁…dₙ}，按任意边界切分为块 {D₁…Dₖ}，第 k 块占用的词元区间记 s_k，Pool 为均值/CLS 池化，Enc 为嵌入模型前向。

| 方法 | 嵌入表达式 | 条件化方式 | 失误来源 |
|---|---|---|---|
| Naive | v_k = Pool(Enc(D_k)) | 无（i.i.d.） | 指代链断裂："its"/"该城市"找不到 Berlin |
| Late Chunking | ϑ = Enc(D) 全篇词元状态；v_k = (1/\|s_k\|) Σ_{t∈s_k} ϑ_t | 注意力，**双向** | 只在长文档 + mean pooling 前提下成立 |
| Contextual Retrieval | v_k = Emb(S(D, D_k) ⊕ D_k) | 自然语言前缀 S，50–100 token | S 是 ≤100 token 有损瓶颈；依赖 LLM 质量 |
| CDE（第三条路） | v = Enc(ψ) ，ψ 为语料级 context 条件 | encoder 内交叉注意力 | 需训练；语料漂移后要重算 |

- **双向性很容易被搞错**：Jina 在 Part II 明确写 v_k ∼ Q(c_k | D)，而非 Q(c_k | c₁…c_{k−1})——encoder-only 的注意力矩阵全连接，块的嵌入同时看到前文和后文。所以 Late Chunking 不是"前向上下文累积"，它与自回归模型的因果掩码是两件事。
- **等价性只在"目标"层面成立，通道层面不等价**：Late 的信息通道是 attention（无损、不可读、无法进 prompt）；Contextual 的通道是 text bottleneck（有损、可读、可人工修正、能直接给生成模型看）。这是 Contextual 唯一的、也是决定性的工程优势——KX 用它解释"为什么 Contextual 还能提升下游生成质量，而 Late 只能提升检索"。
- **Contextual 的 S() 是"任务条件压缩"**：Anthropic 的 prompt 明确要求"说明本块在全文中的位置，以提升检索"，即 LLM 判断"这块缺什么才能被检索到"。这是 query-agnostic 但有目的的压缩，和摘要（document summary）不是一回事——Anthropic 实测"给块加通用文档摘要"收益非常有限。
- **数据侧证据**：Jina-V2-small 在 NFCorpus 上 baseline 23.5 → Late 30.0（+27.7% 相对）；但 Jina 同时给了反例——"不存在弱模型 + late chunking 打赢强模型"的情况（Late+Jv3 36.7 < Jv3 本身在其他数据集的优势），说明它不能替代换模型。

### 2. 成本数学（本次复算，可校验）

口径（Anthropic 官方假设）：文档 8,000 token、块 800 token（10 块）、每块生成 context 100 token、instruction 50 token；Claude 3 Haiku 定价 input USB 0.25/M、output 1.25/M、cache write 0.3125/M、cache read 0.03/M。

```
无缓存：每块输入 = 8000 + 50 + 800 = 8,850 tok
        10 块 = 88,500 tok = 文档 token 的 11.06 倍
        成本 = (88500×0.25 + 1000×1.25)/1e6 = USD 0.02337/doc
        → USD 2.92 / M doc token

有缓存：文档只写一次 cache
        8000×0.3125 + 10×8000×0.03 + 10×850×0.25 + 1000×1.25（均为 每 M token 单价）
        = 0.00250 + 0.00240 + 0.00213 + 0.00125 = USD 0.00827/doc
        → USD 1.03 / M doc token   ← 官方报 1.02，偏差 1%
```

由此确认三件事：

1. **prompt caching 是 Contextual 能成立的前提**，不是优化项。没有缓存就是 2.8× 成本、11× 输入 token。
2. **嵌入侧通胀只有 12.5%**（每块 +100 token / 800），但 BM25 必须建在"拼接后文本"上，否则丢一半收益（Anthropic：只做 contextual embeddings 是 35%，叠加 contextual BM25 才 49%）。
3. **相对倍数大、绝对额小**：embedding 单价按 0.018/M token 量级算，同一语料的嵌入成本 $0.018/M，Contextual 预处理 $1.03/M → **57×**；无缓存 2.92 → **162×**。本机 notes 语料 2,195 篇 / 22.2 MB ≈ 6.95 M token：嵌入 USD 0.125，Contextual 预处理 USD 7.16（cached）/ 20.29（no-cache）。"太贵"是相对嵌入而言，不是相对人而言。

复杂度与内存的账（容易被忽略的一半）：

| 维度 | Naive | Late | Contextual |
|---|---|---|---|
| 注意力 FLOPs | k·c² | (k·c)² → **k 倍** | 同 naive |
| 词元级中间态 | 逐块，可流式 | 整篇常驻：8192×1024 fp32 ≈ **32 MiB/doc** | 同 naive |
| 索引存储 | 1× | 1× | 文本 **+12.5%**，维度不变 |
| 生成侧峰值显存 | 0 | 0 | 长文档实测逼近 **20 GB**（RTX 4090 24GB 只能跑 20% 子集） |

- 注意力项的放大**等于块数 k**（8k 文档、800 token 块 = 10×），但 FFN 项随 token 数不变，所以整体算力放大远小于 10×——不要拿 10× 去吓自己，也不要以为免费。
- ECIR 2025 的显存数字很实在：长文档做 contextualization 时 VRAM 打到约 20 GB，被迫砍批大小、只能用 NFCorpus 的 20% 子集与 50 query / 300 doc 评测。

### 3. 硬前置条件与失败模式（都有数字）

- **Pooling 是生死线**：ECIR 2025（arXiv 2504.19754，NFCorpus，512 字符固定窗）里 BGE-M3 用 Late Chunking，NDCG@5 从 0.246 掉到 0.070（**-72%**）。Jina 的判据同构：Late 要求 long-context + **mean pooling**，CLS / max pooling 模型不兼容。照抄 `late_chunking: true` 不看池化方式 = 事故。
- **文档长度决定收益符号**：MSMarco（短 passage）上 Stella-V5 的 Late 0.503 vs Early 0.630 NDCG@5（**-20%**）。Late 的收益来自"全文上下文远大于块"这个前提；文档本身就是一个段落时前提不成立，只剩长上下文编码的噪声。
- **Contextual 的收益依赖整栈**：Jina-V3 上 FUC+RFR（混合+重排）0.289 → FCC+RFR 0.317 NDCG@5（**+9.7%**）；但去掉 rank fusion 与 rerank，FCC+TR 0.312 vs FUC+TR 0.303（仅 +3%）。上下文必须在混合检索 + 重排框架里才吃满，这正好对应 Anthropic"三者叠加、收益可加"的结论。
- **生成模型质量是一阶变量**：ECIR 用 Phi-3.5-mini-int4 当 contextualizer，作者明确指出"更小更高效的模型表现更差"。用本地小模型做 contextualizer，收益必须打折测量，不能引用 Haiku 的 49%。
- **边界鲁棒性方向相反**：Late 对边界 cue 不敏感（固定长度边界 ≈ 语义边界，Jina 给的三模型 × 四数据集表格基本持平）；Contextual 依赖块本身可读——LLM 读不懂碎块就写不出对的上下文。所以 Contextual 对"语义切分"的依赖高于 Late，这是二者在工程上的隐性耦合。

### 4. 几何解释：两种"上下文"把向量场塑造成不同形状

KX 对 7 句话的小文档做了 PCA 对照（定性、单文档，只能当假设来源）：

- **Late**：块向量被强力"磁化"到文档向量附近，簇紧、方向一致 → 文档级一致性好，风险是**过度泛化**（块间差异被抹平，细粒度查询吃亏）。
- **Contextual**：簇落在 LLM prompt 诱导的某个方向，**并不指向文档向量** → 几何结构由提示词决定，提示词质量直接决定嵌入空间形状。
- **Naive**：散得很开、彼此无序 → 语义独立但缺全局关系。

由此得到一组比 nDCG 更便宜的体检指标（无需跑检索评测）：

```
mean cos(v_k, E(D))     ← Late 应显著高于 naive（磁化程度）
mean cos(v_i, v_j), i≠j ← Late 簇内相似度高
有效秩 / intrinsic dim  ← Late 应下降（区分度变差），naive 应最高
```

这三项能先回答"我的语料是否需要全局上下文"，再决定是否付 Late / Contextual 的钱。

### 5. 第三条路：CDE（Contextual Document Embeddings，ICLR 2025）

- 机制两段：Stage 1 用 512 篇代表性文档编出语料级 context；Stage 2 编码 query/doc 时把该 context 作为条件喂进 encoder（互相注意），**推理开销 ≈ 双塔模型、零 LLM 调用**。
- 数字：cde-small-v1（281M 参数）MTEB Retrieval 51.1（随机 context 基线）→ 53.3（真 context），**+2.2 点**；在小数据集/域外（ArguAna、金融/医疗小语料）优势更大。
- 定位：把"上下文"从**每次推理成本**转成**一次性训练成本**。适合语料与查询分布稳定；不适合天天换语料（corpus context 要重算）。

## 对工作的价值（关联分析）

- **本机 rag-index-rebuild 现在做不了 Late Chunking**：它建的是 BGE-M3 系（CLS pooling）索引，形状上不兼容；硬上就是 ECIR 里那条 -72% 曲线。要 Late 必须先换 mean-pooling 长上下文模型（jina-v3 家族），这是换模型级决策，不是加参数级决策。
- **Contextual 的钱不是问题，上下文从哪来才是问题**：全量 notes 预处理 USD 7.16（cached），比一张 GPU 小时便宜。真正的约束是"谁写 S()"——本地小模型写会掉质量，云端写就要出数据。而我们的笔记有 Markdown 标题树 + 日期 + 项目名，**这本身就是一个确定性、零 LLM、零出境的 S(D,Dᵢ)**。
- **三篇笔记串成一条链**：10-10 三引擎解决"PDF → 干净 Markdown"；10-18 Parent-Child 解决"检索单元 vs 生成单元解耦"，并把 heading path 当元数据；本篇把 heading path 再往前推一步——它同时是**嵌入侧的 contextual prefix**。一条 prefix 三层复用：过滤（元数据）→ 消歧（嵌入/BM25）→ 生成时交代出处（prompt）。
- **成本序（同语料，一次性）**：确定性 prefix ≈ 0 < Late（同嵌入量，仅注意力放大 k 倍）< Contextual（57× 嵌入成本）< Parent-Child（存储翻倍级）< Agentic 切分（10–50× 整套）。这个序应该成为默认升级路径。

## 行动建议与趋势判断

**P0（零成本，可直接做）**：给 rag-index-rebuild 的 chunk 生成加"确定性 context prefix" —— 文档标题 + 标题路径 + 日期 + 项目名，≤60 token，同时拼进 dense 文本与 BM25 文本（两路都要，否则丢一半收益的机理同 Anthropic）。等价于对结构化文档做免费版 S()，可逆、只需重建索引。

**P1（选型闸门，先花小钱做判断）**：50–100 条 golden query 建基线（指标用 `1 - recall@20`，与 Anthropic 口径一致、跨方法可比），再做几何体检（mean cos(chunk,doc)、块间 cos、有效秩）：
- 指代断裂型失败（查询命中不了"该城市/its"所在块）→ 考虑 Late，前提换成 mean-pooling 长上下文模型，小样本 20–50 篇长文档先验证。
- 术语/域外型失败（专有名词、缩写、项目代号）→ 换模型或 CDE 式条件化，不要上 LLM contextualizer。

**P2（明确不做）**：本机不全量跑 LLM contextualizer。理由三条：小模型收益缩水（ECIR 实锤）、长文档显存吃满（20 GB 级）、一次全量要串行几十分钟到数小时且不可增量。要做只对"被判定为 bad chunk"的少数块做（选择性 contextualization），并用 golden query 证明净收益。

**趋势判断**：2024 年那两条对立路线（Late = 模型内隐式 vs Contextual = LLM 外显式）在 2025–2026 已收敛成同一句话——**上下文是输入的"条件"，可以训练、可以工程化、可以元数据化**（CDE 的 corpus-conditioning、结构化 prefix 的工程化）。成本重心从"每 chunk 一次 LLM"下移到"每语料一次""每次索引一次"。我们该押后者。

## 指南分析（若要在本机实施）

1. **先建对照组**：现状索引 + golden query 基线（recall@20 / nDCG@10），落盘成 json，不然后面所有改动都无法判分。
2. **做 P0 prefix**：按标题边界切（element-based，与 Parent-Child 笔记一致），prefix 模板固定为「《文档标题》· 章节路径 · 日期 · 项目」；块本身仍 200–400 token 级（子块）/ 1000–1500（父块）。
3. **验收 prefix 是否有效**：查"指代类查询"的 recall@20 是否上升；若无变化，说明自己的语料本来就不缺指代——省下后续所有钱。
4. **若上 Late**：确认 pooling=mean、上下文 ≥8k；块 800 token；预算注意力 k 倍与 32 MiB/doc 中间态；先小样本验证，防 BGE-M3 式事故。
5. **若上 Contextual**：文档进 cache 只写一次；context ≤100 token；dense 与 BM25 两路都要；只对 bad chunk 做；用 `1 - recall@20` 报告，别只报 nDCG。
6. **禁忌**：不要在同一批语料上既换切分策略又换嵌入模型又加 reranker——三个变量一起动，任何提升都无法归因（ECIR 的结论恰恰是"切分策略差异不显著，融合与重排才是大头"）。

## 拓展应用推荐

- 把确定性 prefix 用到 DUCK 项目 docs（148/152/156 系列）：这是"跨文档强引用"长材料，正是 Late/Contextual 的教科书适用域，且 prefix 里天然带"实验编号 + 日期 + 门禁结论"，消歧价值高于普通笔记。
- 文献空白可做：**"LLM 生成 context" vs "结构化元数据 prefix" 的受控对比**（同语料、同嵌入、同 reranker，只换 S() 的类型）。公开文献里这两种 S() 没有被直接比较过，而它决定"要不要为 contextual retrieval 付 57× 的钱"——这是个可发表的小实验。

## 查询拓展（待深入）

- Late Chunking 论文里的 span 级 InfoNCE 微调（arXiv 2409.04701）在"小语料 + 高专有名词"场景能否补上 Late 的过度泛化。
- CDE 的 corpus context 在语料持续增长（每天新增笔记）下的失效速度与重算成本曲线。
- 加权融合比例敏感度：ECIR 用 dense:BM25 = 1:0.25（照抄 Anthropic cookbook），我们的语料是否该重调。
- "bad chunk" 的分类器（哪些块离开上下文就不可检索）能否用确定性启发式替代 LLM 判断（如含代词开头、含缩写、含表格引用）。

## 出处

1. Anthropic — Introducing Contextual Retrieval（2024-09）：35% / 49% / 67% 失败率降幅、prompt caching、USD 1.02/M doc token 与 800 tok 块 / 8k 文档 / 50 tok 指令 / 100 tok context 假设。https://www.anthropic.com/engineering/contextual-retrieval
2. arXiv 2504.19754 — Reconstructing Context: Evaluating Advanced Chunking Strategies for RAG（ECIR 2025 Workshop，MIT 许可代码）：Late vs Contextual 统一实验；BGE-M3 0.246→0.070；Stella-V5 MSMarco 0.630→0.503；同子集 Contextual 0.317 vs Late 0.309（NDCG@5）、0.308 vs 0.294（NDCG@10）；4090 24GB / 20% 子集 / 约 20GB 显存。https://arxiv.org/abs/2504.19754
3. Jina AI — What Late Chunking Really Is & What It's Not: Part II（2024-10）：v_k ∼ Q(c_k | D) 双向条件、mean pooling 前置条件、边界 cue 鲁棒性表格、与 Contextual 的正面比较。https://jina.ai/news/what-late-chunking-really-is-and-what-its-not-part-ii
4. KX Systems / Michael Ryaboy — Late Chunking vs Contextual Retrieval: The Math Behind RAG's Context Problem（2024-12）：E_true(Dᵢ|D) 表述、PCA 几何观察、选择性 contextualization 建议。https://medium.com/kx-systems/late-chunking-vs-contextual-retrieval-the-math-behind-rags-context-problem-d5a26b9bbd38
5. arXiv 2410.02525 / ICLR 2025 — Contextual Document Embeddings：cde-small-v1 281M、MTEB Retrieval 51.1 → 53.3。https://arxiv.org/abs/2410.02525
6. 本机实测：notes 目录 2,195 篇 / 22,232,909 字节 ≈ 6.95 M token（3.2 字节/token 粗估，中文偏密，区间约 5–9 M）；成本公式见 §2，可用同参数复算。
