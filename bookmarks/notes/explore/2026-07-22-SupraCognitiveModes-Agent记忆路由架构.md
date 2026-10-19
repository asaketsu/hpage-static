# Supra Cognitive Modes: Agent 记忆的路由架构

> **来源**：arXiv:2607.19096
> **原文链接**：https://arxiv.org/abs/2607.19096
> **作者**：Joshua Tobkin, David Yang
> **提交日期**：2026-07-21
> **领域**：cs.AI / cs.CL
> **记录日期**：2026-07-22

**标签**：#Agent记忆 #记忆路由 #检索增强 #多跳推理 #认知架构

---

## 一、内容详细整理

### 1.1 核心问题：记忆三元困境

论文指出，LLM Agent 的记忆层面临三类异构查询需求，单一检索策略无法同时满足：

- **直接事实查找**（Direct Lookup）— 只需要一个近期事实，如"用户上周说了什么"
- **关系链推理**（Relation-Chain）— 需要串联多条关联记录，如"用户对哪些项目表达过负面反馈"
- **广域综合**（Broad Synthesis）— 需要综合数百条对话历史，如"总结用户过去三个月的偏好演变"

这三种查询形态对延迟、成本、覆盖率的要求截然不同。论文将此称为 **记忆三元困境（Memory Trilemma）**：答案质量、响应时间、成本三者相互制约。

> **核心洞察**：激进的 ingest-time 提取可以减少查询时工作量，但在未来查询量未知时提前付费；广域多遍综合能提升覆盖率，但对只需一个事实的问题增加了不必要的延迟和模型开销。

### 1.2 架构核心：Mode-Payload-Procedure 接口

SCM 架构的核心创新是将 Agent 记忆操作点暴露为 **per-query 控制**，而非固定策略。三层分离：

- **Mode（模式）**：语义标签，如 single-fact / long-form / time-anchored / latest-version
- **Payload（载荷）**：从 Mode 映射而来的具体检索+综合配置（retrieval config、top_k、synth mode、force-tier flags）
- **Procedure（过程）**：实际执行的程序族（直接查找 / 图多跳 / 长篇综合）

关键设计：**Mode 与 Procedure 不是一对一映射**。多个 Mode 可以映射到同一初始 Payload，Runtime Gates（运行时门控）可以在执行前修改最终 tier。

```
Query
  │
  ▼
Mode Source (explicit or classify)
  │
  ▼
Payload Map + Runtime Gates
  │
  ▼
┌──────────────┬───────────────────┬──────────────────┐
│ Direct       │ Graph /           │ Long-form        │
│ Lookup       │ Iterative         │ Synthesis        │
│              │ Multi-hop         │                  │
└──────┬───────┴────────┬──────────┴────────┬─────────┘
       │                │                   │
       └────────────────┼───────────────────┘
                        │
                        ▼
              Shared Substrate
         (embeddings, triples, supplements)
                        │
                        ▼
         Synthesis / Answer Policy → Answer or Abstain
```

### 1.3 四种语义模式与调度逻辑

冻结分类器（frozen classifier）输出四种语义标签，无法解析时默认走 single-fact：

- **Single-fact** / **Time-anchored** / **Latest-version** → 三者共享 forced-simple tier（top 100，Sonnet 综合）
- **Long-form** → graph-capable 配置（top 100，narrative 检索 + bullets-expand 标志）
- **Examples route** → PATTERN_FROM_EXAMPLES 路由，处理 in-context-learning 语料

Runtime Gates 可以进一步修正：
- 多选题强制走 simple tier
- 摘要请求走 summary tier
- 含多个关系标记的查询走 multi-hop
- 检索形状检测可重路由 in-context-learning 语料

调度伪代码：

```
mode = explicit_mode or classify(query)
payload = mode_to_payload(mode)
payload = runtime_gates(payload, query, retrieved_context)
procedure = procedure_for(payload.final_tier)
return execute(procedure, query, payload)
```

### 1.4 三大程序族

**1. Direct Lookup（直接查找）**
- 嵌入查询 + 两个轻量改写
- BM25 + Dense Retrieval 并行检索（chunk / sentence / paragraph 三级索引）
- Reciprocal-Rank Fusion（RRF）合并候选
- 最终深度上限 100 chunks
- 单次 Sonnet 调用综合答案
- 弃权行为（abstention）由 prompt 指导，非确定性后检索过滤

**2. Graph / Iterative Multi-hop（图多跳推理）**
- 目标：关系链 + 当前状态问题
- 提取的三元组存储：normalized subject/predicate/object + source memory + confidence + version number + active status + temporal fields
- Planner 选择种子实体和 hop 序列（限定谓词词汇表）
- Grounded walker 在实际入边/出边中选择
- 三元组按 version number 降序排列（新值优先用于当前状态查询，旧值保留用于溯源）
- 图规划失败时降级为迭代 dense 检索

**3. Long-form Synthesis（长篇综合）**
- 按时间序列采样语料，目标 200 chunks
- 多遍 bullets-expand 过程
- 源形状分类器（narrative / research / technical / log / mixed）
- 形状控制覆盖规划 prompt 和扩展 prompt

### 1.5 共享异步底座（Shared Asynchronous Substrate）

所有三个程序族读取同一个 ingest 底座，这是架构的关键设计：

**Tier-1 强制路径（查询就绪边界）**：
- 写入 chunks + 可选的 sentence/paragraph 段
- Embeddings + lexical-index fields + extracted triples
- 完成后即可支持 fused lookup，graph 依赖保留的 triples，长篇综合可直接从分层 chunks 操作

**异步补充任务（可选，nullable）**：
- 文档形状（document shape）
- 预期关键点（anticipated keypoints）
- 规范实体（canonical entities）
- 事件链（event chains）
- 问题模式（question patterns）
- 结构重要性（structural importance）
- 实体类型（entity types）

> **关键设计**：缺失的补充信号会降级为在线检测或省略，而非阻塞查询就绪。这些字段是 nullable 的，查询代码仅在对应 payload flag 启用时读取。

### 1.6 三基准评估结果

在三个记忆基准上的表现：

- **LoCoMo（n=1,986）**— 长期对话记忆：
  - Factoid categories：84.87%（修正后）
  - Adversarial abstention：68.61%
  - Mixed full set：81.22%
- **MemoryAgentBench（n=3,671）**— 记忆代理任务套件：
  - 总体 61.49%（两次运行 61.72% / 61.26%）
  - AR（准确检索）78.62% | TTL（测试时学习）50.05% | LRU（长程理解）54.67% | SF（选择性遗忘）62.62%
- **LongMemEval（n=500）**— 纵向个人记忆：
  - 86.00% overall

对比基线：Mem0 v2 OSS（geometric mean 22.02%）、Production Comparator（57.27%）、SCM（75.45%）

> **⚠️ 重要警示**：论文明确声明，因存储行不保留所有最终 runtime decisions 且未运行 fixed-policy 控制组，这些结果**不支持将路由效果或单一过程归因为基准差异的原因**。这是描述性表征，不是因果分析。

### 1.7 失败模式诊断（关键价值）

论文的 mode-conditioned failure analysis 揭示了高密度错误分层：

- **LongMem 时间失败**：long-form（14/25）+ time-anchored（9/25）— 错误集中在两个语义路由
- **MAB FC-MH 失败**：long-form（214/229）— 关系链错误高度集中
- **MAB Movie-Rec 失败**：single-fact（179/179）— 推荐问题被路由到不适合的程序
- **LoCoMo abstention 失败**：single-fact（110/139）— 残留拒绝错误集中在 lookup

> **诊断价值**：Movie-Rec 全部 179 个失败都走了 single-fact 路由，说明该论文的分类器对推荐类问题存在系统性误路由——这是一个极具工程价值的发现。

### 1.8 诚实的证据边界声明

论文最突出的特质是对证据边界的严格声明：

- Raw baseline outputs 不可用（无法审计 prompt parity）
- LoCoMo/LongMem 的 timing 与 token 使用量未持久化（无法做三轴对齐比较）
- 大多数单元格是 single-run（无正式方差估计）
- Mem0 用 ChromaDB，SCM 和 production comparator 用 pgvector（系统非不变性）
- 存储行保留语义标签但不保留所有 post-gate tier / graph strategy / fallback
- Active graph 字段和修正记录不一致

> **论文原话**："Causal routing effects, efficiency gains, and statistical significance remain outside the available evidence."

---

## 二、查询拓展

### 2.1 MemGPT / Letta 分层记忆

MemGPT 将 LLM 记忆组织为 main-context、recall、archival 三层，灵感来自操作系统的虚拟内存分层。SCM 的 shared substrate 与其理念相似——mandatory ingest 创建可查询索引（类似 page table），异步补充添加 nullable 信号（类似 lazy loading 的 swap-in）。区别在于 SCM 的分层是 per-query 的（运行时动态选择），而 MemGPT 是 per-context-window 的固定分层。

### 2.2 Reciprocal-Rank Fusion（RRF）

RRF 是一种无参数的排名合并方法，公式 `RRF(d) = Σ 1/(k + rank_i(d))`，其中 k 通常取 60。SCM 用 RRF 合并 BM25（sparse lexical）和 Dense Retrieval（dense embedding）的排名——这是因为 lexical 和 dense 检索是互补的：lexical 擅长精确匹配（关键词、专有名词），dense 擅长语义匹配（同义、概念关联）。RRF 的优势在于不需要训练、不依赖分数分布，是 RAG 系统的工业标准合并方法。

### 2.3 Temporal Knowledge Graph（时序知识图谱）

SCM 的 graph 程序族使用带有 version number 和 temporal fields 的三元组，这与 Zep/Graphiti 的 temporal knowledge graph 一脉相承。传统知识图谱是静态快照，时序知识图谱保留了关系的演变历史（如"用户对项目A的态度从2024年的积极变为2025年的消极"）。SCM 的创新在于按 version number 降序排列——默认返回最新值用于当前状态查询，同时保留旧值用于溯源。

### 2.4 Adaptive-RAG 与路由检索

SCM 在 Related Work 中明确对比了 Adaptive-RAG（将问题分类为 no-retrieval / single-step / multi-step）。SCM 的差异在于路由粒度——不是仅暴露检索深度或模型选择，而是将 per-query 语义标签映射到一个可同时选择检索策略、substrate 读取、prompt family、综合过程的完整 payload。这是从"检索路由"到"记忆架构路由"的范式升级。

---

## 三、归纳总结

### 3.1 核心框架：记忆三元困境 × 三层分离

```
记忆三元困境                    解决方案：三层分离
┌──────────────┐               ┌──────────────────┐
│ 答案质量     │               │ Mode (语义标签)  │
│ 响应时间     │  ──────────→  │ Payload (配置)   │
│ 成本         │               │ Procedure (执行) │
└──────────────┘               └──────────────────┘
       ↕                              ↕
   三种查询形态                   Runtime Gates
   - 直接查找                    (运行时修正)
   - 关系链                      
   - 广域综合                    共享异步底座
                                  (查询就绪 + 渐进丰富)
```

### 3.2 与同类记忆系统的设计哲学对比

- **SCM**：per-query 路由控制 + 共享底座，程序族分离但读取同一数据
- **Mem0**：ingest-time 持久化用户记忆，查询时统一检索
- **MemGPT/Letta**：分层 context 管理，OS 式虚拟内存
- **Zep/Graphiti**：时序知识图谱为主轴，查询围绕图遍历
- **GraphRAG**：图+层次综合，适用于大文本集合

SCM 的独特定位：**不发明新原语，而是将已有原语组织成程序族拥有的路径，共享一个底座**。架构创新在于组合和控制接口。

### 3.3 失败模式的工程启示

论文最有价值的部分是 mode-conditioned failure strata。这些数据揭示了一个关键问题：**分类器的系统性误路由是性能瓶颈的主要来源**，而非底层检索原语。Movie-Rec 全部走错路由（single-fact），FC-MH 214/229 走 long-form 却大面积失败——说明路由准确性比检索质量更关键。

---

## 四、趋势判断

### 趋势1：Agent 记忆从"单一策略"走向"per-query 自适应路由"

论文的 mode-payload-procedure 接口预示了 Agent 记忆架构的演进方向：不再是"一个记忆系统处理所有查询"，而是"每个查询选择最合适的记忆操作模式"。这与 Adaptive-RAG、Self-RAG、FLARE 的趋势一致——检索策略从静态走向动态、从单一走向分类。

依据：SCM 的四模式+runtime gates 设计在三个独立基准上均超越固定策略的 baseline。

### 趋势2：诚实评估将成为高质量论文的标志

这篇论文最引人注目的不是分数，而是其对证据边界的极致诚实——明确声明无法归因路由效果、缺乏 statistical significance、baseline raw outputs 不可用。在 AI 研究普遍存在 evaluation gaming 的当下，这种诚实评估范式可能成为新的质量标准。

依据：论文用了整个 Section 6.3（Threats to Validity）列述六类有效性威胁，并在 abstract 和 conclusion 中反复声明证据边界。

### 趋势3：异步底座分层（Tier-1 mandatory + async supplements）成为 RAG 工程化标配

SCM 的 mandatory ingest（查询就绪边界）+ nullable async enrichments 设计，将 ingest 工作量按查询需求分层——类似数据库的 lazy loading。这对高并发 Agent 系统的 cost placement 优化有直接参考价值。

依据：missing enrichments 降级为 online detection 或 omission，而非阻塞查询，这保证了系统的可用性优先。

---

## 五、关联分析

### 5.1 与 Hermes Agent 上下文/记忆架构的关联

Hermes 的 skills/memory/context 三层信息架构与 SCM 的三层分离有结构同构性：
- Hermes skills = SCM 的 procedure families（按任务选择不同执行路径）
- Hermes memory (MEMORY.md / USER.md) = SCM 的 shared substrate
- Hermes 的 skill_view 动态加载 = SCM 的 per-query mode 选择

**关键差异**：Hermes 目前缺乏 runtime gates——即无法在 skill 加载后根据检索到的内容动态调整执行路径。SCM 的 `payload = runtime_gates(payload, query, retrieved_context)` 这一步是 Hermes 的缺失环节。

关联笔记：[上下文质量是Agent可靠性前置指标](2026-07-18-上下文质量是Agent可靠性前置指标.html)、[evolvemem-agent-memory-self-evolution](2026-07-20-evolvemem-agent-memory-self-evolution.html)

### 5.2 与 MemDecay 区域感知记忆的关联

MemDecay（2607.10582）的 region base priority + decay rate 思路与 SCM 的 mode-conditioned 路由互补：MemDecay 解决的是"记忆随时间如何衰减"，SCM 解决的是"不同查询如何选择记忆访问策略"。两者可以组合——用 SCM 的路由决定访问哪些区域，用 MemDecay 的衰减决定该区域内记忆的优先级。

关联笔记：[SlotGuard-Agent转录本隐私边界](2026-07-21-SlotGuard-Agent转录本隐私边界.html)（共享 Agent 转录本处理主题）

### 5.3 与 MAS 信息瓶颈的关联

MAS Information Bottleneck（2607.16133）的 IB 理论框架可以用于评估 SCM 的路由效果——当 query 被路由到"错误"的 procedure（如 Movie-Rec 走 single-fact），实际上是在增加 relay 复杂度 δ。SCM 的失败模式数据可以作为 MAS 信息瓶颈理论的实证案例。

关联笔记：[多Agent何时有效-信息瓶颈视角](2026-07-20-多Agent何时有效-信息瓶颈视角.html)

---

## 六、金句摘录

> 「A single retrieval and synthesis policy is unlikely to serve all three shapes equally well.」
> — 论证了 per-query 路由的必要性

> 「Causal routing effects, efficiency gains, and statistical significance remain outside the available evidence.」
> — 论文对自身结果的诚实声明，堪称学术写作典范

> 「The architectural novelty is the composition and control interface, not the underlying retrieval primitives.」
> — 明确了创新边界：不是新原语，而是新组织方式

> 「Missing enrichments therefore degrade to online detection or omission rather than blocking query readiness.」
> — 异步底座的核心设计哲学：可用性优先

---

## 七、借鉴点评估（Hermes Agent / Jetson 边缘 / 量化交易）

### P0 — 高优先级

**1. Skill 选择 Runtime Gate 机制**
- 借鉴：SCM 的 `payload = runtime_gates(payload, query, retrieved_context)` — skill 加载后根据实际检索内容动态调整执行路径
- 对照：Hermes 目前 skill 加载是"一次加载走到底"，无中途路由修正
- 工作量：中（需要在 skill 执行流程中加入条件分支检查点）
- 增量价值：避免简单查询走重型 skill 路径的浪费

**2. 分类器误路由的系统性检测**
- 借鉴：SCM 的 mode-conditioned failure strata 揭示了 Movie-Rec 全部走错路由的问题
- 对照：Hermes 目前无法检测"哪些用户意图被路由到了错误的 skill"
- 落地：在 skill 执行日志中记录 query 意图标签 + 实际执行的 skill + 结果质量，定期分析误路由模式
- 增量价值：识别 skill 匹配的系统性盲区

### P1 — 中优先级

**3. 异步底座分层（Tier-1 mandatory + async supplements）**
- 借鉴：Mandatory ingest 立即可查询，async enrichments 渐进丰富
- 对照：Hermes memory 目前无"渐进丰富"机制——所有记忆写入后静态存在
- 落地：对 memory 条目增加 nullable enrichments（关联实体、时效性标签、重要性分级），按需异步补充
- 增量价值：平衡 ingest 成本和查询质量

**4. 时序三元组用于量化交易策略记忆**
- 借鉴：SCM graph 程序的三元组带 version number + temporal fields + active status
- 对照：量化策略记忆目前是"策略 + 回测结果"平面记录，无时序版本追踪
- 落地：策略迭代记录为三元组（策略, 参数, 表现），按 version 降序排列，支持"当前最优参数"查询
- 增量价值：策略版本演进可追溯

### P2 — 低优先级

**5. Per-query 抽象用于 Cron Job 路由**
- 借鉴：SCM 的 mode-to-payload 映射概念
- 对照：Hermes cron 目前是固定 job 固定执行，无条件路由
- 增量价值：较低（cron 任务通常已有明确执行路径）

**6. 弃权行为（Abstention）机制**
- 借鉴：SCM 的 prompt-directed abstention（"No information available"）
- 对照：Hermes 在不确定时倾向于"猜测"，缺乏显式弃权
- 增量价值：中（提高可信度，但需要用户接受"不知道"的回答）

### ❌ 暂不适用

**7. Graph Multi-hop 程序族**— Hermes 的查询模式目前以直接查找和顺序综合为主，关系链查询需求不强烈。Jetson 边缘推理更不适用（资源约束下 graph traversal 过重）。


## 相关笔记

- [SlotGuard Agent转录本隐私边界](./2026-07-21-SlotGuard-Agent转录本隐私边界.md) — Agent记忆隐私安全，认知架构互补视角
- [Memory Compaction Rate Distortion](./2026-07-12-MemoryCompactionRateDistortion.md) — 记忆压缩理论，信息论视角的记忆管理
- [Self-GC Agent上下文生命周期管理](./2026-07-03-Self-GC-Agent上下文生命周期管理.md) — 上下文回收机制，记忆路由底层基础设施
- [LLM自进化为何崩溃](./2026-07-21-LLM自进化为何崩溃-自合成数据信息增益.md) — 自合成数据的信息增益分析，记忆系统退化风险
