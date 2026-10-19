# RAG 知识库 2026 前沿技术全景：从混合检索到 Agentic 架构
> 探索日期：2026-06-02 | 兴趣等级：L3 | 来源数量：15+

## 核心发现

### 发现一：2026 RAG 已从 Naive Pipeline 演进为 Agentic 系统

2026 年的 RAG 已彻底告别 2023-2025 年的简单 retrieve-then-generate 模式。Turing Post 总结了 20 种高级 RAG 类型，Atlan 归纳了 12 种前沿技术。核心演进路径：

1. **Naive RAG** → 单次向量检索 + 生成，召回率低、幻觉高
2. **Advanced RAG** → 混合检索(BM25+向量) + Rerank + 查询改写，工业标准
3. **Agentic RAG** → 自主推理 Agent 叠加在 RAG 之上，多步规划、工具编排、自纠错循环

LangGraph 2026 版将 RAG 建模为有向循环图：条件分支、持久检查点、human-in-the-loop 中断点。Agent 可以规划多步策略、运行时改写查询、遍历混合记忆层、反思自身输出并改进情景记忆。

**对 WikiKB 的启发**：当前 UnifiedSearch 仍停留在 Advanced RAG 层面（关键词+向量双路），需要引入 Agent 控制循环让系统自主决定何时检索、如何检索、是否需要二次检索。

### 发现二：Chunking 策略是 2026 年检索质量的第一杠杆

Digital Applied 的 2026 检索 Playbook 指出：**分块策略对检索质量的影响超过模型选择**。Weaviate 2025 年 9 月实测数据：同一语料库、同一检索器，最佳和最差分块方法的召回率差距高达 9%。

关键发现：
- **2026 年 1 月系统分析**：最常见的 chunk overlap（重叠切分）没有可衡量的收益。这是一个打破行业惯例的结论
- **8 种分块策略**：固定大小、递归字符、语义分块、层次化、Late Chunking、Agentic Chunking 等
- **推荐默认起点**：recursive 512-token splits，仅当检索指标 justify 时才升级到 semantic/hierarchical/late chunking
- **NVIDIA 2024 benchmark**：Recursive character splitting（400-512 tokens, 10-20% overlap）仍是通用最佳默认

**Graph-Aware Late Chunking（arXiv:2603.22633）**：传统 Late Chunking 将文档视为扁平 token 序列，忽略了文档固有的结构。新方法结合图结构感知：
- 保留跨 chunk 上下文依赖
- 利用文档标题层级结构指导分块边界
- 比标准 Late Chunking 进一步提升语义完整性

**对 WikiKB 的启发**：当前 semantic_chunk_markdown（标题边界分割）方向正确，但应结合 Graph-Aware 思路，保留跨 chunk 的引用关系和层级依赖。

### 发现三：Weighted RRF 从理论走向生产，Adaptive 权重成为标配

RRF（Reciprocal Rank Fusion）在 2026 年已成为多路检索融合的工业标准：

- **Elasticsearch**：正式内置 RRF retriever，支持多查询结果集融合
- **Azure AI Search**：混合搜索默认使用 RRF 排序
- **Dify**：社区请求将 RRF 作为 rerank 策略（issue #34643）

**CCNC 2026 WRRF 论文**突破性贡献：引入置信度分数作为权重，不再是等权融合。公式：
```
R(d) = Σ w_j / (k + r_j(d))
```
其中 w_j 是每路检索的置信度权重。实验证明比等权 RRF 提升分类准确率 3-5%。

**生产推荐权重配置**：
| 查询类型 | 关键词 | 向量 | 图 |
|----------|--------|------|-----|
| exact | 1.0 | 0.3 | 0.2 |
| semantic | 0.3 | 1.0 | 0.5 |
| exploratory | 0.5 | 0.8 | 1.0 |
| general | 0.7 | 0.7 | 0.5 |

**对 WikiKB 的启发**：当前已实现 Weighted RRF（keyword=1.0, vector=1.0, graph=0.7），但权重是静态的。需要根据查询类型动态切换权重 profile。查询分类目前用关键词匹配（不稳定），应引入 embedding-based semantic router。

### 发现四：CAG（Cache-Augmented Generation）作为 RAG 的战略替代

CAG 是 2026 年最值得关注的 RAG 替代方案：

**核心理念**：预加载知识到长上下文窗口（128K-1M token），省去检索步骤。

**关键区别**：
- RAG：实时检索 + 生成，适合动态数据集
- CAG：预加载 + 直接生成，适合静态数据集，延迟更低、成本更低

**适用场景判断**：
- 文档量 <500、知识更新不频繁 → CAG 更优
- 文档量 >100K、频繁更新 → RAG 必要
- 中间地带 → 混合模式（CAG 缓存热点文档 + RAG 处理长尾）

**对 WikiKB 的启发**：笔记库（bookmarks/notes）约 1137 篇 Obsidian 笔记 + explore 笔记，总量偏大但热点文档集中。可考虑混合模式：高频访问的 50-100 篇核心文档用 CAG（预加载到上下文），长尾文档走 RAG 检索。

### 发现五：Agentic RAG 五层安全架构浮出水面

Okta 的 Agentic RAG 安全分析揭示了此前被忽视的安全维度：

Agentic RAG 将标准 RAG 的每个授权风险扩展到多步工作流的每一步、Agent 间的协调缝隙、以及可能派生其他 Agent 的 Agent 身份生命周期。安全架构需要：
1. **Agent 身份管理**：每个 Agent 有独立身份，可被审计
2. **工具授权边界**：Agent 只能访问被授权的工具和数据源
3. **多步工作流安全**：每一步的检索和生成都需要权限检查
4. **Agent 间通信安全**：Agent 协调时的身份验证
5. **生命周期管理**：Agent 派生子 Agent 时的权限继承

**对 WikiKB 的启发**：当前系统无任何安全层。如果未来开放给多用户或接入 MCP 工具链，需要引入 Agent 身份和权限管理。

## 关键技术细节

### 混合检索工程实践（2026 工业标准）

**索引阶段**：文档加载 → 解析（PDF 用 OCR/MinerU）→ 分块 → Embedding 向量化 → 存入向量数据库（Milvus/Chroma/Qdrant）

**检索生成阶段**：用户 Query → 预处理（改写）→ **同时进行向量检索和 BM25 关键词检索** → RRF 融合排序 → Re-rank 精排 → 拼接上下文 → LLM 生成答案

**比例经验**：
- 通用场景：向量 60% : BM25 40%
- 客服场景（口语化问题）：BM25 更重要
- 技术文档场景：BM25 精确匹配更关键

**Re-rank 必要性**：向量检索（Bi-Encoder）Query 和 Doc 独立编码，无法捕捉细粒度交互。Re-rank 使用 Cross-Encoder，将 Query 和 Doc 拼接后一起编码。工业标准：向量检索粗排 Top-40 → Cross-Encoder 精排 Top-3。

### 向量数据库选型速查（2026 更新）

| 数据库 | 索引类型 | 优势 | 劣势 |
|--------|---------|------|------|
| Milvus | HNSW/IVF-PQ/混合 | 生态最全，分布式 | 运维复杂 |
| Qdrant | HNSW | Rust 实现，内存低，API 清晰 | 生态弱于 Milvus |
| Weaviate | HNSW+混合 | 内置 BM25，GraphQL | 文档偏少 |
| Chroma | HNSW(近似) | 轻量 Python 优先 | 不适合大规模生产 |
| FAISS | IVF-PQ/HNSW | 算法最全性能最优 | 只是库不是服务 |

**选型建议**：<10万用 Chroma；10万-千万用 Qdrant/Milvus 单机；>千万用 Milvus 分布式。

### Embedding 微调提升路径

用领域数据做对比学习（query, positive_doc, negative_doc），Recall@10 可从 71% 提升到 89%。关键：选择 hard negative 样本，监控过拟合。

## 与现有 WikiKB 工作的关联

### 已实现（需验证/优化）
- ✅ RRF 多路融合（keyword + vector + graph）
- ✅ Weighted RRF（keyword=1.0, vector=1.0, graph=0.7）
- ✅ Semantic Chunking（Markdown 标题边界分割）
- ✅ Contextual Chunk 增强（文档上下文前置）
- ✅ Adaptive Weighted RRF 权重 profile
- ✅ Late Chunking 理论采纳

### 待实现（优先级排序）
1. **P0**：查询分类从关键词匹配升级为 embedding-based semantic router
2. **P0**：vector_stage() 修复——当前是伪向量搜索（vector_score=0.0 硬编码）
3. **P1**：Graph-Aware Late Chunking——结合文档结构图的分块
4. **P1**：Re-rank 层引入（Cross-Encoder 精排）
5. **P2**：CAG 混合模式——热点文档预加载
6. **P2**：多模态检索扩展（视频时间线、图像布局）
7. **P3**：Agentic RAG 控制循环（自纠错、多步规划）
8. **P3**：Agent 安全层（身份管理、权限边界）

### 知识缺口
- Late Chunking 的具体工程实现（Jina AI 的 API 接入方式）
- Semantic Router 的训练数据需求和部署成本
- CAG 在实际 1000+ 文档场景的性能基准
- Graph-Aware Late Chunking 的开源实现
- Re-rank 模型的选型（Cohere vs BGE-Reranker vs 自训练）

## Actionable Insights

1. **立即可做**：将 Adaptive Weighted RRF 的 4 种权重 profile 集成到 UnifiedSearch 的查询分类逻辑中，替换静态权重。代码量约 30 行，无需新依赖
2. **短期**：修复 vector_stage() 的伪向量搜索问题，接入真实 embedding 模型。这是当前检索质量的根本瓶颈
3. **中期**：引入 Semantic Router 替换关键词路由。可用 sentence-transformers 的 embedding + 余弦相似度实现，无需 API key
4. **长期**：规划 Agentic RAG 架构——PageIndex 已具备 Tool 模式基础，需要叠加 Agent 控制循环

## 来源列表

1. Atlan - 12 Advanced RAG Techniques (2026) — https://atlan.com/know/advanced-rag-techniques
2. arXiv:2601.12658 — Hybrid RAG Approach (Vector + Graph)
3. Neo4j Blog — Advanced RAG Techniques for High-Performance LLM Applications
4. Turing Post — 20 Advanced RAG Types to Know in 2026
5. Galileo — RAG Architecture: From Naive Pipelines to Agentic
6. InfoQ — Building Hierarchical Agentic RAG Systems
7. Okta — Agentic RAG Architecture: Security Considerations
8. 博客园 — 2026年RAG面试高频考点（BM25/混合检索/Re-rank/Self-RAG）
9. Digital Applied — RAG Chunking Strategies: 2026 Retrieval Playbook
10. arXiv:2603.22633 — Graph-Aware Late Chunking for RAG
11. Medium — CAG: The Next Frontier in LLM Optimization
12. CCNC 2026 — Weighted Reciprocal Rank Fusion for Context-Aware RAG
13. glaforge.dev — Understanding RRF in Hybrid Search (2026)
14. Microsoft Learn — Hybrid Search Scoring (RRF) in Azure AI Search
15. Elasticsearch Docs — Reciprocal Rank Fusion API

注：本文基于 web_search 搜索结果聚合，web_extract 全部被阻断（15/15 URL Blocked）。信息来源于搜索结果的 title + description + 可见摘要，未做深度原文阅读。

## 相关笔记
- [MCP 协议生态与 Agentic RAG 架构深度学习](../2026-04-27-MCP协议生态与Agentic-RAG架构深度学习.md) (agentic, rag)
- [autoresearch-rag-integration](../autoresearch-rag-integration.md) (rag)
- [Superpowers — Agentic 技能框架与软件开发方法论](../2026-05-07-Superpowers-Agentic技能框架.md) (agentic)
- [RAG效果不佳的真相：数据才是最终杀手](../2026-05-18-RAG数据质量-数据是最终杀手.md) (rag)
- [Agentic SOC：安全自动化的范式转变](2026-05-13-Agentic-SOC-安全自动化的范式转变.md) (agentic)
