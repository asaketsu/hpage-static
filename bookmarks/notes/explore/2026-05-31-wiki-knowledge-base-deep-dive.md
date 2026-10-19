# Wiki 知识库系统深度蒸馏 — 双引擎架构、已知缺陷与进化路线
> 探索日期: 2026-05-31 | 兴趣等级: L3 | 来源: 本地知识蒸馏（6 源码文件 + SKILL.md Pitfall 记录）
> 来源: wiki-kb 核心模块源码 + PageIndex 工程 + auto-learner skill 中的 RAG 经验

## 核心发现

### 发现1: 三引擎实际运行状态 — 向量层是伪向量搜索

**现状**：wiki-kb 名义上有"三层混合检索"（关键词→向量→渐进披露），但 `hybrid_search.py` 的 `vector_stage()` 函数（第 202-295 行）中，`vector_score` 硬编码为 `0.0`（第 263 行），实际只做 `has_embedding` 标记加权（×1.2）。搜索退化为纯关键词 TF 打分。

**根因**：`vector_stage()` 需要调用 embedding 模型生成查询向量，再与索引向量做 cosine similarity。但当前代码缺少"查询 → 向量"的调用链——`rag_adapter.semantic_search()` 虽然有 Gemini embedding 调用，但 `hybrid_search.py` 没有复用它，而是自己维护了一个独立的 `EMBEDDINGS_DIR` 路径。

**代码证据**（hybrid_search.py:263）：
```python
c["vector_score"] = 0.0  # 需要查询向量才能计算真正相似度
# 标记该文件有向量表示，提升信任度
c["has_embedding"] = True
```

**修复方案**：在 `vector_stage()` 中调用 `rag_adapter.semantic_search()` 生成查询向量，做 cosine similarity + RRF(k=60) 融合。需要 `GOOGLE_API_KEY` 或替代 embedding 模型。

### 发现2: 两套评分标准不一致导致排序偏斜

**问题**：`pageindex_adapter._keyword_score()` 和 `rag_adapter.keyword_search()` 使用完全不同的评分标准：

| 匹配类型 | PageIndex 权重 | RAG 权重 | 比值 |
|----------|---------------|----------|------|
| 完全匹配 | 10.0 | 20.0 | 1:2 |
| 英文词 | 2.0 | 3.0 | 1:1.5 |
| 中文 bigram | 1.5 | 2.0 | 1:1.33 |
| 中文单字 | 0.3 | 0.5 | 1:1.67 |
| 标题加权 | 无 | ×1.5 | — |

**后果**：`UnifiedSearch._search_domain()` 同时调用 PageIndex 和 RAG，合并去重后分数不可比——RAG 结果天然排名更高。这不是"相关度差异"，纯粹是量纲不统一。

**修复方案**（已记录在 SKILL.md，三种选择）：
1. **RRF 替代原始分数**（推荐，无需调参）：`score = Σ 1/(k + rank_i)`，k=60
2. Min-Max 归一化到 [0,1] 后融合
3. LLM Reranker（高价值查询）

RRF 模板已在 SKILL.md 中给出：
```python
def rrf_merge(results_list, k=60):
    scores = defaultdict(float)
    for results in results_list:
        for rank, r in enumerate(results):
            rid = r.get('file') or r.get('doc_id') or r.get('title', '')
            scores[rid] += 1.0 / (k + rank + 1)
    return sorted(scores.items(), key=lambda x: -x[1])
```

### 发现3: wiki_graph 独立运行但未集成到主搜索流

**现状**：`wiki_graph.py`（674 行）实现了完整的图引擎：
- `build_graph()`: 扫描 .md 文件，提取 `[[wikilinks]]`，构建邻接表 + 反向索引
- `expand()`: BFS 多跳扩展，支持 hop 分布统计
- `multi_wiki_search()`: 多路径并行搜索

但 `UnifiedSearch` 的三个搜索路径（`_search_document_reference` / `_search_domain` / `_search_general`）都没有调用图引擎。

**遗漏的影响**：当关键词和向量搜索都返回空时，图扩展可以发现隐式关联页面。例如笔记 A 链接笔记 B，B 链接笔记 C，用户搜索 A 的关键词可能在 C 中也找到相关信息。

**集成方案**：BFS 扩展作为 `_search_general()` 的第三路检索，用 RRF(k=60) 融合三路结果。图扩展权重应低于关键词/向量（建议 0.6-0.8），因为 hop>0 的结果相关性天然较低。hop 惩戒用指数衰减：`score = 10.0 * (0.6 ** hop)`。

### 发现4: _search_general() 完全跳过 PageIndex

**位置**：`unified_search.py:176-182`

```python
def _search_general(self, query: str, top_k: int) -> List[Dict]:
    """泛知识搜索"""
    results = self.rag.search(query, top_k=top_k)
    for r in results:
        r["engine"] = "rag"
        r["type"] = "note"
    return results
```

general 查询只走 RAG，完全跳过 PageIndex。如果用户搜索的内容恰好在某个 PDF 中有索引但不在 RAG 笔记中，就搜不到。

**修复**：在 `_search_general()` 中增加 PageIndex fallback：
```python
# 2. PageIndex fallback（当 RAG 返回空或不足时）
if len(results) < top_k:
    docs = self._get_doc_cache()
    for doc_id, doc_info in docs.items():
        try:
            sr = self.pageindex.search_tree(doc_id, query)
            if sr["matched_nodes"]:
                results.append({...})
        except Exception:
            pass
```

### 发现5: 查询分类依赖静态关键词列表，不稳定

**问题**：`_classify_query()` 用关键词包含匹配，效果取决于 `DOMAIN_KEYWORDS` 列表的完整性。实测：
- "注意力机制" → general（无匹配）
- "attention机制" → domain（命中 "attention"）
- "embedding" → domain（命中 AI 关键词）

**改进方向**：
1. **短期**：扩展 DOMAIN_KEYWORDS，加入同义词和中文翻译
2. **中期**：引入 embedding-based semantic router（需 API key）
3. **长期**：用 LLM 做查询理解，输出结构化检索计划

## 技术细节与代码示例

### 1. 中文分词策略（三种实现对比）

wiki-kb 中有三种不同的中文分词实现：

**PageIndex 适配器**（pageindex_adapter.py:190-226）：
```python
# 完全匹配: 10.0, 英文词: 2.0, bigram: 1.5, 单字: 0.3
for word in query_lower.split():
    if len(word) >= 2 and word in text:
        score += 2.0
for i in range(len(query_lower) - 1):
    bigram = query_lower[i:i+2]
    if bigram in text:
        score += 1.5
for ch in query_lower:
    if '\u4e00' <= ch <= '\u9fff' and ch in text:
        score += 0.3
```

**RAG 适配器**（rag_adapter.py:44-103）：
```python
# 完全匹配: 20.0, 英文词: 3.0, bigram: 2.0, 单字: 0.5 + 标题×1.5
# 预计算查询特征，避免重复计算
query_bigrams = [query_lower[i:i+2] for i in range(len(query_lower) - 1)]
query_chars = [ch for ch in query_lower if '\u4e00' <= ch <= '\u9fff']
```

**Hybrid Search**（hybrid_search.py:54-69）：
```python
# 英文按空格/标点，中文 bigram + 单字
tokens.extend(w.lower() for w in re.findall(r"[a-zA-Z0-9]+", text) if len(w) >= 2)
chinese_chars = re.findall(r"[\u4e00-\\u9fff]", text)
tokens.extend(chinese_chars)
for i in range(len(chinese_chars) - 1):
    tokens.append(chinese_chars[i] + chinese_chars[i + 1])
```

**问题**：三种实现各自的权重和策略不同，UnifiedSearch 合并结果时分数不可比。需要统一为一种评分函数。

### 2. TF 打分的改进空间

当前 TF 打分（hybrid_search.py:84-112）：
```python
def _tf_score(content, query_tokens, query_raw):
    # 完全匹配
    if query_raw.lower() in content_lower:
        exact_bonus = 10.0
    # TF = 词频 / 文档长度（归一化）
    tf = count / doc_length
    score += (1.0 + math.log(1.0 + tf * 1000)) * len(token)
```

**改进方向**：引入 BM25 替代纯 TF：
```python
def bm25_score(doc_tokens, query_tokens, avgdl, N, df_map, k1=1.5, b=0.75):
    """BM25: 比 TF 更好的信息检索基线"""
    score = 0.0
    dl = len(doc_tokens)
    for qt in query_tokens:
        tf = doc_tokens.count(qt)
        df = df_map.get(qt, 1)
        idf = math.log((N - df + 0.5) / (df + 0.5) + 1)
        numerator = tf * (k1 + 1)
        denominator = tf + k1 * (1 - b + b * dl / avgdl)
        score += idf * numerator / denominator
    return score
```

### 3. wiki_graph BFS 扩展的实现模式

```python
def expand(query_pages, wiki_path, max_hops=2, max_pages=20):
    graph = build_graph(wiki_path)
    adjacency = graph["adjacency"]
    
    # BFS
    visited: dict[str, int] = {}  # page -> hop
    queue: deque[tuple[str, int]] = deque()
    
    for s in seeds:
        if s not in visited:
            visited[s] = 0
            queue.append((s, 0))
    
    while queue:
        page, hop = queue.popleft()
        if hop >= max_hops:
            continue
        for neighbor in adjacency.get(page, set()):
            if neighbor not in visited:
                visited[neighbor] = hop + 1
                if len(visited) < max_pages:
                    queue.append((neighbor, hop + 1))
```

**关键设计决策**：
- 种子页面不受 max_pages 限制
- 悬空链接（链接目标不存在）仍保留在图中
- 重复 stem 时保留路径更短的文件（更接近根目录优先）
- 反向索引（reverse map）支持"谁引用了我"

### 4. UnifiedSearch 路由策略

```
查询 → _classify_query()
  ├─ document（文档引用）→ RAG关键词 + PageIndex树搜索
  ├─ domain（专业领域）→ PageIndex优先 + RAG补充
  └─ general（泛知识）→ 纯RAG ← [BUG: 跳过PageIndex]
```

分类依据：
- DOC_KEYWORDS: `.pdf`, `文档`, `手册`, `规范`, `报告`, `论文`, `源码`, `设计`
- DOMAIN_KEYWORDS: 结构工程(28词) + AI/技术(12词) + 产品(7词) = 47个关键词

### 5. 渐进式披露模式

`hybrid_search.py` 实现了三层渐进式披露：
1. **默认**：只返回 snippet（前 200 字）
2. `include_full=True`：返回完整内容
3. `--load-content <file>`：按需加载指定文件

这是一个好模式——先给概览，确认相关后再花 token 加载全文。可以推广到 UnifiedSearch 的所有搜索路径。

## 实践启发

### 1. 评分归一化是知识库融合的必解问题

任何多引擎知识库都会遇到评分标准不一致的问题。wiki-kb 的三种搜索（PageIndex关键词、RAG关键词、RAG语义）各自的评分量纲不同，直接比较是错误的。

**教训**：不要在合并时比较原始分数。用 RRF 或 Min-Max 归一化。RRF 是最简单的方案——只需要排名，不需要分数。

### 2. 向量搜索的"最后一公里"问题

wiki-kb 的向量搜索实现是"伪向量搜索"——有向量索引但没有查询向量的生成。这不是罕见的失误：很多 RAG 系统在离线索引阶段做了 embedding，但在在线检索阶段忘记了生成查询 embedding。

**检查清单**：
1. 索引阶段：文档 → embedding → 存储 ✓
2. 查询阶段：query → embedding → cosine similarity ← 缺失
3. 融合阶段：关键词分数 + 向量分数 → 排序 ← 无法执行

### 3. 图搜索的权重衰减

从 GraphRAG 实践中学到：hop>0 的结果相关性天然较低。如果图搜索权重与关键词/向量相同，会拉入噪音。建议用指数衰减：`weight = base_weight * (decay ** hop)`，decay=0.6 时：
- hop=0: 1.0（种子页面）
- hop=1: 0.6（一跳关联）
- hop=2: 0.36（二跳关联）

### 4. 查询分类的稳定性

关键词匹配路由简单但不稳定。依赖静态关键词列表意味着：
- 新领域术语不会自动识别
- 中英文混合查询可能误分类
- 关键词粒度不好控制（"注意力" vs "注意力机制"）

短期可以维护更完整的关键词表（含同义词、翻译），中期应该用 embedding semantic router。

## 知识缺口

1. **真正的多路融合尚未实现**：RRF 模板有了但还没集成到 UnifiedSearch。需要实现 `_merge_with_rrf()` 方法，替换当前的简单去重+截断。

2. **语义搜索依赖 Gemini API**：`rag_adapter.semantic_search()` 需要 `GOOGLE_API_KEY`。没有 key 时完全退化为关键词。应该支持本地 embedding 模型作为 fallback（如 sentence-transformers）。

3. **增量索引未实现**：SKILL.md 提到 `.manifest.json` + SHA-256 Delta 追踪的增量索引设计，但代码中没有实现。每次 `build.py add-all` 都会重新处理所有文件。

4. **查询分类缺乏评估**：没有标注数据集来评估 `_classify_query()` 的准确率。不知道当前关键词路由的 precision/recall。

5. **图搜索与主搜索流的集成方案**：wiki_graph.py 功能完整但未接入 UnifiedSearch。需要设计第三路检索的 API 和权重配置。

6. **BM25 替代 TF 的可行性**：当前纯 TF 打分在长文档中有偏斜（短文档更容易获得高 TF 分数）。BM25 能否在不引入外部依赖的情况下改善检索质量？

7. **Agentic RAG 升级路径**：SKILL.md 提到 PageIndex 已演进为 Agentic Vectorless RAG（支持 OpenAI Agents SDK、MCP Server 模式），但 wiki-kb 还没有利用这些新能力。

## 进化评估

| 发现 | 可复用性 | 行动 |
|------|---------|------|
| RRF 多路融合模板 | 高（3+ 次使用） | 已在 SKILL.md，需实现集成 |
| 评分归一化问题 | 高（每次搜索都受影响） | 需 patch UnifiedSearch |
| 向量搜索伪实现 | 高（影响检索质量） | 需 patch hybrid_search.py |
| BM25 替代 TF | 中（改善长文档检索） | 待评估 |
| 图搜索集成 | 中（扩展发现能力） | 待设计集成方案 |
| 查询分类改进 | 中（影响路由准确性） | 待收集评估数据 |

## 来源列表

1. `~/uclaw/project/wiki-kb/core/unified_search.py` — 291 行，统一搜索入口
2. `~/uclaw/project/wiki-kb/core/pageindex_adapter.py` — 262 行，PageIndex 适配器
3. `~/uclaw/project/wiki-kb/core/rag_adapter.py` — 263 行，RAG 适配器
4. `~/uclaw/project/wiki-kb/scripts/hybrid_search.py` — 483 行，三层混合检索
5. `~/uclaw/project/wiki-kb/scripts/wiki_graph.py` — 674 行，图引擎
6. `~/uclaw/project/wiki-kb/utils/query_router.py` — 38 行，查询分类
7. `~/.hermes/skills/data-science/wiki-knowledge-base/SKILL.md` — Pitfall 记录和改进方案
8. `~/.hermes/skills/research/auto-learner/SKILL.md` — RAG 搜索经验积累


## 相关笔记
- [Hermes Agent Deep Dive — 进化路线图](../2026-04-07-hermes-agent-deep-dive-evolution-roadmap.md)
- [FastMCP Python SDK 深度精读（v1.27.1 源码级）](../2026-05-26-fastmcp-sdk-deep-dive.md)
- [Mem0 AI Agent 记忆框架深度研究](../2026-05-27-mem0-agent-memory-deep-dive.md)
- [AI Agent 2026 前沿趋势与量化交易新技术 — 深度学习笔记](../2026-05-27-ai-agent-2026-deep-dive.md)
- [nashsu/llm_wiki 项目分析 — 桌面应用 vs Agent Skill](../2026-05-24-nashsu-llm_wiki项目分析_deep-blue.md)
