# GBrain 混合搜索方案（备用）

> 来源：[garrytan/gbrain](https://github.com/garrytan/gbrain) 分析，2026-04-11

## 目标
为记忆系统增加 **关键词+向量混合搜索**，提升召回精度。

## 方案对比

### 方案A：PostgreSQL + pgvector（GBrain方案）
- 优点：成熟、混合搜索原生支持、实体图谱可行
- 缺点：Jetson上跑PG吃资源（建议256MB+）、需Docker、维护成本高
- 适用时机：笔记规模 >500篇 或 需要实体图谱时

### 方案B：SQLite + sqlite-vss（轻量方案）
- 优点：零部署、单文件、Jetson友好
- 缺点：sqlite-vss需编译（arm64可能有问题）、功能不如pgvector全
- 适用时机：中等规模（100-500篇）

### 方案C：纯Python混合搜索（当前可行）
- 向量搜索：已有 embed-index.py（qwen3-embedding-8b）
- 关键词搜索：加 BM25/TF-IDF 层
- 融合：Reciprocal Rank Fusion (RRF)
- 优点：零依赖、立即可做
- 缺点：规模受限（纯内存）、无持久索引

### 推荐路径
**现在**：方案C（Python RRF混合）→ **规模增长后**：方案A（pgvector）

## 方案C 实现草图

```python
# hybrid_search.py
import json, math
from embed_index import cosine_search  # 已有

def bm25_search(query, docs, k1=1.5, b=0.75):
    """简单BM25实现"""
    # ... tokenize, tf-idf scoring

def reciprocal_rank_fusion(vector_results, keyword_results, k=60):
    """RRF融合两个排序列表"""
    scores = {}
    for rank, doc_id in enumerate(vector_results):
        scores[doc_id] = scores.get(doc_id, 0) + 1/(k + rank + 1)
    for rank, doc_id in enumerate(keyword_results):
        scores[doc_id] = scores.get(doc_id, 0) + 1/(k + rank + 1)
    return sorted(scores.items(), key=lambda x: -x[1])

def hybrid_search(query, top_k=10):
    vec_results = cosine_search(query, top_k=top_k*3)
    kw_results = bm25_search(query, load_docs(), top_k=top_k*3)
    return reciprocal_rank_fusion(vec_results, kw_results)[:top_k]
```

## 里程碑
- [ ] embed-index.py 加 BM25 关键词层
- [ ] RRF 融合排序
- [ ] 搜索结果缓存（避免重复embedding调用）
- [ ] 增量索引（只更新变更文件）
- [ ] 日志/评估：对比纯向量 vs 混合搜索召回率


## 相关笔记
- [[20260513-llm-wiki-obsidian-gbrain-知识自组织与自进化]] (关键词: gbrain)
