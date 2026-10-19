　　# Mnemosyne：零依赖、亚毫秒 AI 记忆系统

- 📅 2026-05-05
- ⭐⭐⭐⭐ 4.5/5 — BEAM 三层架构设计精巧，benchmark 98.9%，架构思想值得吸收
- 🏷️ #AI记忆 #Hermes生态 #SQLite #向量检索 #知识图谱
- 📰 GitHub AxDSan/mnemosyne
- 🔗 https://github.com/AxDSan/mnemosyne

关联：[memory-system](hermes-memory-system-guide.md) [[exchange-protocol]] [evolver](2026-04-05-capability-evolver-self-upgrade.md)

## 摘要

Mnemosyne 是专为 Hermes Agent 设计的本地优先记忆系统，采用 SQLite 原生存储，实现亚毫秒级读写延迟。核心创新是 BEAM 三层架构（Working Memory → Episodic Memory → Scratchpad），配合自动 sleep 整合机制将热记忆压缩为冷记忆。在 LongMemEval 基准上达到 98.9% 召回率，远超 Mem0（84%）和无记忆基线（60%）。完全离线、零云依赖、MIT 协议。

## 核心内容

### BEAM 架构（Bilevel Episodic-Associative Memory）

三层记忆各有明确职责和生命周期。Working Memory 是热上下文，在每次 LLM 调用前自动注入 prompt，通过 TTL 驱逐过时条目。Episodic Memory 是长期存储层，使用 sqlite-vec 向量搜索和 FTS5 全文搜索的混合检索。Scratchpad 是 Agent 临时推理工作区，不持久化。

整合机制 mnemosyne_sleep() 模拟人脑睡眠整理：扫描过期的 working memory 条目，用 LLM 生成摘要，压缩后写入 episodic memory，同时清理原条目。整个过程在 33ms 内完成（300条旧记忆）。

### 混合检索算法

检索权重分配为向量相似度 50% + FTS5 排名 30% + 重要性分数 20%。这比纯向量检索或纯关键词检索都更鲁棒——语义匹配找"意思相近"的，关键词匹配找"精确提及"的，重要性权重确保关键偏好不被淹没。

### 时间知识图谱

TripleStore 不是简单的三元组存储，而是带时间有效性的知识图谱。三元组有 valid_from 和 valid_until 字段，查询时可指定 as_of 时间点，自动过滤已失效的关系。例如"Maya 被分配到 auth-migration 项目"这条三元组，项目结束后自动失效。

### 实体抽取（零依赖）

不依赖 spaCy、PyTorch 等重型 NLP 库，而是用正则 + Levenshtein 模糊匹配。能捕获 @mention、#hashtag、"引号短语"、大写序列（2-5词）。模糊匹配容错：查询"Abdias"能找到"Abdias J"（相似度 0.925）。

### 跨 Provider 迁移

支持从 Mem0、Letta(MemGPT)、Zep、Cognee、Honcho、SuperMemory 六个平台导入记忆数据，保留元数据、时间戳、身份关系。用 --dry-run 可以验证不实际写入。

## 🔍 借鉴点

BEAM sleep 整合机制 → 可应用到 evolver 流程：当前 Hermes memory 没有自动降级机制，记忆要么在要么不在。可设计 cron 定期扫描 memory，将过时但可能有用的条目压缩为摘要存入经验池，而非直接遗忘。实现路径：auto-dream cron 增加记忆整合逻辑。

混合检索权重公式（50%vec+30%FTS+20%importance） → 当前 memory tool 只有精确匹配，session_search 是关键词搜索。如果未来引入 RAG 索引（已有 rag-index-rebuild skill），可参考此权重分配。

时间知识图谱带有效期 → 当前经验池 JSONL 是扁平追加式，没有时间有效性概念。可在 exchange-protocol 的经验条目中增加 valid_until 字段，让过期经验自动降权。

## 🔗 关联性

- 关联已有 skill：memory-system — 当前三层记忆架构（永久/今日/临时）与 BEAM 的 working/episodic/scratchpad 概念相似但实现更轻，可借鉴 sleep 整合思路
- 关联已有 skill：exchange-protocol — 双机经验池可增加时间有效期，类似 TripleStore 的 valid_until
- 关联已有 skill：evolver — 自动压缩机制与 sleep() 思路一致，可将记忆降级纳入 evolver 闭环
- 关联已有笔记：[[2026-05-04-Hermes-多Bot方法论]] — 同属 Hermes 生态项目
- 关联竞品索引：Mnemosyne 加入 Hermes 生态竞品（DeepSeek/SkillClaw/jcode/AutoCLI/Workspace）

## 💡 启发

记忆的生命周期管理比记忆的存储更重要。Mnemosyne 的核心价值不在于"存得多快"（虽然确实快），而在于 sleep() 这个概念——主动整理记忆，把热的变冷的，把临时变永久的，把冗余压缩为精炼。这跟人脑的睡眠整理机制高度一致。

我们的 exchange-protocol 经验池目前是只增不减的 JSONL，长期运行后信息熵会持续升高。引入类似 sleep 的周期性整理（压缩、去重、降权、失效标记）是必要的。

## 🔮 预判

短期（1-3月）：Mnemosyne 会成为 Hermes 生态的标准记忆插件，pip install 一键接入的体验太好。Cloud 记忆服务（Mem0/Zep）会被挤压到纯企业场景。

中期（3-6月）：Hermes 官方可能会将 Mnemosyne 的 BEAM 架构纳入核心，类似 SQLite 之于 session persistence 的定位。本地优先 + 离线可用会成为 Agent 框架的标配要求。

长期：记忆系统的竞争焦点从"存取性能"转向"记忆质量"——自动整理、时间感知、跨 Agent 共享记忆。TripleStore 的时间有效性是正确方向。

## 相关笔记
- [[2026-05-04-Hermes-多Bot方法论]] - 同生态项目分析
- [[2026-05-05-得否-X-Article转Markdown工作流]] - 同日分析的 Hermes 生态用户工具
