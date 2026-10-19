# 文档解析工具: Parent-Child 分层索引

> 来源: 嗅探队列 auto-explore | 日期: 2026-10-18
> 信源: FutureAGI《Advanced RAG Chunking 2026》、Glukhov《Chunking Strategies in RAG Comparison》、H-RAG (arXiv 2605.00631, SemEval-2026 Task 8)

## 摘要

Parent-Child 分层索引（又称 small-to-big）是 RAG 分块架构中解耦"检索单元"与"生成单元"的方案：小块 child（128-256 token）做嵌入与向量检索，命中后返回大块 parent（512-1024 token，乃至全文）给 LLM 生成。2026 年已成生产栈默认（LangChain `ParentDocumentRetriever` / LlamaIndex `HierarchicalNodeParser` + `AutoMergingRetriever`），并有 SemEval-2026 H-RAG 系统级学术验证。本质是对"检索精度 vs 上下文连贯性"Pareto 折中的工程化解法。

## 关键发现

### 1. 核心机制：为什么必须两级
- 大块嵌入质量差：2000 词块的单一 768 维向量要同时表达多个概念，导致"对什么都中等相似、对什么都不精确命中"。
- 小块缺语境：答案句可召回，但脱离定义/约束/前置条件后 LLM 易幻觉。
- 解法：child 管精度（嵌入向量语义聚焦），parent 管语境（LLM 读到完整段落/章节）。检索粒度与生成上下文彻底解耦。

### 2. 两种成熟实现
- 两级式（LangChain `ParentDocumentRetriever`）：parent_splitter 1000 / child_splitter 200；child 入向量库（带 parent_id），parent 存 docstore。命中 child → 查 parent_id → 返回 parent 全文。
- 多级树式（LlamaIndex `HierarchicalNodeParser` chunk_sizes=[2048,512,128] + `AutoMergingRetriever`）：三层粒度树。检索时若同一父节点下多数子节点被命中（如 2/3），自动上卷（merge）返回整个父块。附带收益：避免 top-k 槽位被同一语义邻域的兄弟碎片重复占用——4 个相邻碎片上卷成 1 个完整父节，等于动态扩容了有效上下文。

### 3. H-RAG（SemEval-2026 Task 8）实战配方，全部超参公开
- 切块：3 句/子块、stride 2 滑窗（保局部连贯）；全文为父。
- 检索：混合 dense-sparse，α=0.7（70% 语义 + 30% 词法），初始 k=50 子块。
- 父聚合：子块最大分 = 父分（max child score），top-5 父文档进 LLM。
- 模型：bge-large-en-v1.5 嵌入 + bge-reranker-v2-m3 重排 + GPT-5 生成，全零样本微调。
- 结果：Task A nDCG@5=0.4271；消融显示 α 与排序策略对最终 grounding 质量敏感。
- 多轮对话关键件：轻量查询改写（T=0.2），prompt 里写明"已是独立问题则原样返回"——防止短事实型问题被 LLM 过度改写。

### 4. 聚合与排序是可调超参，不是实现细节
- 两种排序策略实测有差异：① child-first 排完再聚合去重父级；② 先去重候选父，再对父级内容直接重排。
- max 聚合（子块最高分代表父）是简单有效基线；比 sum 更抗噪声子块稀释。

### 5. 适用边界与互补技术
- 最佳域：强结构、内部交叉引用的长材料——政策/RFC/标准/法律/大手册。固定长度切块会切断表格、分离定义与引用，此类损失在结构化文档上最致命。
- 互补非互斥（成熟管线可叠用）：
  - element-based 结构切块（按标题/元素边界）：SEC filings 研究实测——检索质量提升且 chunk 数量约减半（索引成本同步降）。
  - late chunking（Jina, arXiv 2409.04701）：先全文嵌入后按块池化，治跨块语义。
  - RAPTOR（arXiv 2401.18059）：聚类+LLM摘要建树，治多跳问答，离线成本最高。
- FutureAGI 决策路径：recursive 300-500 token 基线 → 召回低上 semantic → 要"召回+大上下文"上 parent-child → 跨块语义上 late chunking → 多跳再叠 RAPTOR。不要跳过前三步直接堆贵方案。

### 6. 成本账
- 双粒度存储 = 内存/存储翻倍级增长；parent 返回可能膨胀 prompt，需 top-n 与去重控制。
- 索引侧 child 数多 → 向量库规模大；但 element-based 父块切法可对冲（块数减半）。

## 对工作的价值

- 本地 RAG 管线（rag-index-rebuild / knowledge-query）当前若为平铺切块，parent-child 是性价比最高的第一升级：无需换嵌入模型、无需重训，纯索引结构改造。
- 笔记体系天然带结构层级（Markdown 标题树 + 双格式 HTML），element-based 父块切分（H2/章节为父、段落为子）零成本对齐，且 heading path 可直接做元数据过滤。
- DUCK 项目 docs（148/152/156 系列）与适航类长文档正是"内部交叉引用长材料"——分层索引 + auto-merge 是教科书适用域；长训教训类知识跨文档引用多，平铺切块已可见检索断 context 问题。

## 行动建议

1. rag-index-rebuild 增加 parent-child 模式：child=段落级（~200 token），parent=H2 章节（1000-1500 token），child 记录 parent_id + heading path 元数据。
2. 检索侧：混合检索 α=0.7 起步 → 子块重排 → max-child-score 聚合到父 → top-5 父文档，参数照抄 H-RAG 表。
3. 父块严格按标题边界切（element-based），禁固定长度硬切表格/代码块/定义段。
4. 若后续有多跳问答需求，再评估 RAPTOR 层，先不做。
