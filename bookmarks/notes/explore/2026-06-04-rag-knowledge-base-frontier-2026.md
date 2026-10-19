# RAG 与知识库前沿 2026：架构演进、检索策略与 WikiKB 升级路线
> 探索日期：2026-06-04 | 兴趣等级：L3 | 来源数量：14

## 核心发现（6个）

### 1. RAG 已分裂为三大架构范式，不再是单一技术
2026 年 RAG 不再是"向量检索+生成"的简单管道，而是演化为三种独立架构（来源：Medium "Choosing the Right RAG Architecture in 2026"）：

1. **Pipeline RAG**（经典管道）：当答案存在于单一 chunk 时，延迟/成本/可预测性最优。适用于 FAQ、文档问答。
2. **Agentic RAG**（智能体驱动）：Agent 自主决定何时检索、检索什么、是否需要反思重试。适合多步推理、跨文档分析。核心模式包括：ReAct 交替推理行动、Tree-of-Thoughts 多路径探索、反思循环（Iterative Retrieval with Reflection）。
3. **Knowledge Graph RAG**（图增强）：利用实体关系图发现隐式关联，适合需要跨文档推理的场景。

**关键洞察**：三种架构解决的是不同故障模式。Pipeline 解决"找不到答案"，Agentic 解决"答案分散在多处"，Graph 解决"需要推理链连接"。

### 2. Agentic RAG 六大模式详解（Digital Applied 深度指南）
Agentic RAG 不是简单地在 RAG 上加 Agent，而是有明确的设计模式（来源：digitalapplied.com 2026-05-28）：

1. **Iterative Retrieval with Reflection**：检索→评估→反思→重检索，循环直到满意度阈值
2. **Query Decomposition**：复杂查询自动分解为子查询，每个子查询独立检索后合并
3. **Hypothesis-Driven Retrieval**：先生成假设答案，然后检索证据验证/反驳假设
4. **Cross-Corpus Triangulation**：从多个知识源交叉验证同一事实
5. **Evidence-Weighted Synthesis**：根据证据来源可靠性加权合成最终答案
6. **Iteration Budgets**：设定最大迭代次数和停止条件，防止 Agent 无限循环

**WikiKB 启示**：当前 WikiKB 的 UnifiedSearch 是 Pipeline RAG。Agentic 模式可通过 Hermes Agent 天然实现——Agent 调用 search 作为 tool，自主决定是否需要多次检索。

### 3. CAG（Cache-Augmented Generation）成为 RAG 的同级架构
CAG 的核心思路：将整个知识库预加载到 LLM 的长上下文窗口（128K-2M token），利用 prompt caching 实现低成本高速查询（来源：futureagi.com RAG vs CAG 2026）。

**七轴决策框架**：
| 维度 | RAG | CAG |
|------|-----|-----|
| 语料规模 | 无上限 | 受上下文窗口限制（<2M token） |
| 新鲜度 | 实时检索 | 需刷新缓存 |
| 延迟 | embed+rerank+生成 | 缓存命中后极快 |
| 成本 | 按查询计费 | 一次性缓存+折扣读取 |
| 引用追踪 | 天然支持 | 需额外标注 |
| 多租户 | 各租户独立索引 | 缓存隔离复杂 |
| 查询分布 | 适合长尾 | 适合热点集中 |

**WikiKB 适用性评估**：笔记库（bookmarks/notes）约 500-2000 篇文档，符合 CAG 场景（<500 文档或知识更新不频繁）。建议混合模式：CAG 处理热点查询 + RAG 处理长尾查询。

### 4. Lightweight Query Routing：TF-IDF + SVM 击败语义分类器
RAGRouter-Bench（arXiv 2604.03455，2026 年最新基准）的关键发现：
- **TF-IDF + SVM** 在查询分类上达到 macro-F1 0.928，比 sentence embedding 高 3.1 个点
- 表面关键词模式是查询复杂度的强预测因子——不一定需要昂贵的 embedding
- 三种查询类型：factual（事实型）、reasoning（推理型）、summarization（摘要型）
- 路由到最便宜的足够范式可节省 3.5x token 消耗

**WikiKB 直接应用**：当前 DOMAIN_KEYWORDS 手动列表 + 简单包含匹配的路由方式可升级为 TF-IDF 分类器，无需 API key，本地可训练，准确率更高。

### 5. Chunking 策略 2026 定论：Chunk Overlap 无收益
2026 年 1 月系统分析确认（来源：digitalapplied.com RAG Chunking Playbook）：
- **最常见默认（chunk overlap）无可衡量收益**，打破行业惯例
- 分块策略影响 > 模型选择（Weaviate 实测：最佳和最差方法召回率差 9%）
- 推荐起点：recursive 512-token splits
- 升级条件：当检索指标 justify 时才升级到 semantic/hierarchical/late chunking

**Late Chunking 的精确定位**：在 naive chunking（便宜但丢上下文）和 ColBERT（精确但贵）之间的甜蜜点。Jina AI 提出，利用长上下文 embedding 模型先编码整文档，在 transformer 输出后、mean pooling 前分块。

### 6. GraphRAG 从研究走向生产：成本降低 10-90%
2026 年 GraphRAG 关键进展（来源：medium.com/graph-praxis）：
- 混合检索模式：关键词 BM25 + 向量 + 图遍历三路融合
- RRF（Reciprocal Rank Fusion）仍是主流融合方法，k=60 为默认
- 成本控制：增量图构建、选择性图遍历（只对高价值查询启用图扩展）
- Agentic GraphRAG：Agent 自主构建知识图谱 + 自适应检索（NODES AI 2026 大会主题）

## 技术细节与代码示例

### Adaptive Weighted RRF 实现（生产级）
```python
from collections import defaultdict

WEIGHT_PROFILES = {
    "exact":       {"keyword": 1.0, "vector": 0.3, "graph": 0.2},
    "semantic":    {"keyword": 0.3, "vector": 1.0, "graph": 0.5},
    "exploratory": {"keyword": 0.5, "vector": 0.8, "graph": 1.0},
    "general":     {"keyword": 0.7, "vector": 0.7, "graph": 0.5},
}

def adaptive_weighted_rrf(results_list, query_type="general", k=60):
    """根据查询类型动态调整多路检索权重"""
    weights_dict = WEIGHT_PROFILES.get(query_type, WEIGHT_PROFILES["general"])
    weights = [weights_dict.get("keyword", 1.0), 
               weights_dict.get("vector", 0.7), 
               weights_dict.get("graph", 0.5)]
    scores = defaultdict(float)
    for results, w in zip(results_list, weights):
        for rank, r in enumerate(results):
            rid = r.get('file') or r.get('doc_id') or r.get('title', '')
            scores[rid] += w / (k + rank + 1)
    return sorted(scores.items(), key=lambda x: -x[1])
```
来源：Elasticsearch 2026 Weighted RRF + CCNC 2026 WRRF 论文。比等权 RRF 提升分类准确率 3-5%。

### Lightweight Query Router（TF-IDF + SVM）
```python
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC
import joblib

class QueryRouter:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(ngram_range=(1, 2), max_features=5000)
        self.classifier = LinearSVC(C=1.0, max_iter=1000)
    
    def train(self, queries, labels):
        """labels: ['factual', 'reasoning', 'summarization']"""
        X = self.vectorizer.fit_transform(queries)
        self.classifier.fit(X, labels)
    
    def route(self, query):
        X = self.vectorizer.transform([query])
        return self.classifier.predict(X)[0]
    
    def save(self, path):
        joblib.dump({"vec": self.vectorizer, "clf": self.classifier}, path)
    
    @classmethod
    def load(cls, path):
        data = joblib.load(path)
        router = cls()
        router.vectorizer = data["vec"]
        router.classifier = data["clf"]
        return router
```

### Agentic RAG 迭代检索模式（Hermes 实现思路）
```
用户查询 → Agent 评估复杂度
  ├─ 简单(factual) → 一次检索 → 回答
  ├─ 中等(reasoning) → Query Decomposition → 并行检索 → 合成
  └─ 复杂(exploratory) → 假设生成 → 检索验证 → 反思 → 重检索(最多3轮) → 回答
  
停止条件：confidence > threshold OR iteration >= budget
```

### CAG 混合路由模式
```python
def hybrid_retrieval_router(query, corpus_size, cache_hit_ratio):
    """决定走 CAG 还是 RAG"""
    MAX_CAG_TOKENS = 2_000_000  # Gemini 2.5 Pro
    AVG_DOC_TOKENS = 500
    
    if corpus_size * AVG_DOC_TOKENS < MAX_CAG_TOKENS:
        # 小语料：CAG 更优
        return "CAG", {"cache_all": True}
    elif cache_hit_ratio > 0.8:
        # 热点集中：CAG 缓存热点 + RAG 长尾
        return "HYBRID", {"hot_cache": True, "cold_rag": True}
    else:
        # 大语料长尾：纯 RAG
        return "RAG", {"full_rag": True}
```

## 与现有 WikiKB 的关联与升级建议

### 当前 WikiKB 架构评估
| 组件 | 当前状态 | 2026 最佳实践 | 差距 |
|------|---------|-------------|------|
| 查询路由 | 手动关键词列表 | TF-IDF + SVM 分类器 | 中 |
| 检索方式 | 关键词 + 伪向量 | 真向量 + 关键词 + 图 | 高（vector_stage 硬编码 0.0） |
| 分块策略 | 固定字符窗口 | Recursive 512-token + 标题边界 | 中 |
| 融合方法 | 原始分数（不可比） | Weighted RRF | 高（两套评分标准不一致） |
| Re-rank | 无 | Cross-Encoder 精排 | 中 |
| 图检索 | wiki_graph 存在但未集成 | BFS 扩展作为第三路检索 | 高 |
| 上下文增强 | 无 | Contextual Retrieval（-49% 失败率） | 低（易实现） |

### 升级优先级（投入产出比排序）
1. **P0**：修复 vector_stage() 硬编码 0.0 → 调用真实 semantic_search
2. **P0**：引入 RRF 替代原始分数融合（解决评分标准不一致问题）
3. **P1**：集成 wiki_graph BFS 作为第三路检索
4. **P1**：Contextual Retrieval（每个 chunk 前置文档摘要，零成本实现）
5. **P2**：Semantic Chunking（按 Markdown 标题边界分割，已有代码模板）
6. **P2**：Lightweight Query Router（TF-IDF+SVM 替代手动关键词）
7. **P3**：Cross-Encoder Re-rank（需要额外推理开销，高价值查询时启用）
8. **P3**：CAG 混合模式（笔记库场景适用，但需评估缓存成本）

## 实践启发

1. **先修基础设施再追前沿**：WikiKB 当前最大瓶颈不是缺少最新技术，而是基础设施缺陷（伪向量搜索、评分不一致）。修好这些比引入新架构价值更高。
2. **Agentic RAG 不需要重构**：Hermes Agent 天然支持 Agentic 模式——只需让 Agent 调用 search tool 并支持多轮检索即可，不需要重写 UnifiedSearch。
3. **TF-IDF > Embedding for 路由**：查询分类不需要语义理解，表面关键词就够了。这对 WikiKB 是好消息——不需要 API key 也能做好路由。
4. **CAG 在小知识库场景有颠覆性**：如果笔记库 <2M token，直接缓存到上下文窗口比检索更简单更可靠。
5. **Chunk Overlap 可以去掉**：现有 chunking 中的 overlap 策略可以安全移除，节省索引空间。

## 知识缺口（待深入）

1. **Re-rank 模型本地部署方案**：BGE-Reranker-v2-m3 的显存需求和推理延迟——WikiKB 服务器能否承受？
2. **GraphRAG 增量图构建**：新增文档时如何高效更新实体关系图，而不是全量重建？
3. **CAG prompt caching 成本模型**：OpenAI/Google 的 prompt caching 具体计费方式，与 RAG 的成本对比？
4. **Agentic RAG 的 stop condition 设计**：confidence threshold 如何校准？不同领域应有不同阈值？
5. **RAGRouter-Bench 数据集细节**：7,727 条标注数据的分布和覆盖领域，是否适合中文场景？
6. **Multimodal RAG**：图表/图片/表格的检索增强在 2026 年的最新进展（本次未深入搜索）

## 来源列表

1. "Agentic RAG Patterns 2026: Multi-Step Reasoning Guide" — digitalapplied.com (2026-05-28)
2. "20 Advanced RAG Types to Know in 2026" — turingpost.com
3. "RAG vs CAG: Cache-Augmented Generation 2026" — futureagi.com
4. "Lightweight Query Routing for Adaptive RAG: RAGRouter-Bench" — arXiv 2604.03455 (2026)
5. "RAG Chunking Strategies: A 2026 Retrieval Playbook" — digitalapplied.com
6. "Graph RAG in 2026: A Practitioner's Guide" — medium.com/graph-praxis
7. "RAG MCP and Agentic AI: Architecture Patterns for 2026" — aetherlink.ai
8. "Agentic RAG in 2026: Enterprise Guide" — datanucleus.dev
9. "Choosing the Right RAG Architecture in 2026" — medium.com/@skyhawkbytecode
10. "Late Chunking: Balancing Precision and Cost" — weaviate.io
11. "Late Chunking vs Contextual Retrieval" — medium.com/kx-systems
12. "RAG in 2026: Bridging Knowledge and Generative AI" — squirro.com
13. WikiKB SKILL.md — 已有知识库（本地）
14. "Agentic GraphRAG: Autonomous Knowledge Graph Construction" — NODES AI 2026 (YouTube)

## 相关笔记
- [rag-knowledge-base-2026-frontier](explore/2026-06-02-rag-knowledge-base-2026-frontier.md)
