# Agent Memory 2026：Dreaming、Memory Bank 与记忆经济学

> 选题来源：用户 L3 兴趣区（context engineering/agent memory，auto-dream 标记为"刚升至L3，可能继续深挖"）
> 关联领域：AI Agent 架构、记忆系统、上下文工程
> 学习日期：2026-06-20
> 核心论点：2026年Q2，Agent记忆从"可选组件"变为"架构核心决策"——Anthropic Dreaming、Google Memory Bank、Mem0 ADK 三条路线已分化，记忆选择现在是经济决策而非能力决策

## 核心发现

### 发现 1：三大基准已标准化记忆评估——LoCoMo/LongMemEval/BEAM

Mem0 的《State of AI Agent Memory 2026》确立了三大基准，此前各框架"自说自话"的混乱结束：

| 基准 | 规模 | 测试维度 | 核心价值 |
|------|------|----------|----------|
| **LoCoMo** | 1,540 题 | 单跳/多跳/开放域/时序召回 | 长程对话记忆的基础线 |
| **LongMemEval** | 500 题 | 单会话用户/助手/偏好召回 + 知识更新 + 时序推理 + 多会话召回 | 跨会话连续性 |
| **BEAM** | 1M / 10M token | 偏好跟随/指令/信息抽取/知识更新/多会话/摘要/时序/事件排序/弃权/矛盾解决 | 大规模极限测试 |

**评估指标矩阵**：BLEU（token级相似）/ F1（精确召回）/ LLM-as-Judge（二元正确性）/ Token消耗 / 延迟。其中 **Token 消耗** 被提升为一等指标——记忆系统的经济性（每查询花多少 token）与召回率同等重要。

**Mem0 当前 SOTA 表现**：LoCoMo **92.5**（6,956 token/查询）、LongMemEval **94.4**（6,787 token/查询）、BEAM-1M **64.1**、BEAM-10M **48.6**。最大增益在时序推理（+29.6分）和多跳（+23.1分）。

### 发现 2：Anthropic "Dreaming"——会话间海马体重放（2026-05-06）

这是 2026 Q2 架构意义上最重要的记忆创新。Dreaming 是 Managed Agents 的**异步海马体整合过程**，在会话之间运行：

```
Dreaming 流程：
1. 读取现有记忆库 + 过往会话转录
2. 从会话中提取模式
3. 合并重复项，替换过期条目
4. 写入未来会话可用的新记忆条目
```

**关键特征**：
- **异步执行**：不阻塞会话，在会话之间运行（数分钟到数十分钟）
- **记忆文件位于** `/mnt/memory/`（agent 容器内文件系统挂载）
- **与其他 Anthropic 记忆面分离**（Memory Tool / Context Management）
- **厂商报告**：Harvey 法律 agent 任务完成率提升 **6x**（注意：营销数据，作方向性信号而非保证基准）

**架构意义**：Dreaming 实现了"**睡眠期间的记忆整合**"——这正是人类海马体在睡眠中重放并巩固记忆的机制。Agent 不再是"被动接收上下文"，而是**主动调用记忆管理函数**在层间移动信息。这使得 agent 成为其自身记忆管理的积极参与者，而非被动接收注入上下文的容器。

> "Agents do not passively receive context — they explicitly call memory management functions to move information between tiers."

### 发现 3：Google Memory Bank——身份作用域持久化（2026-05-19）

Google I/O 2026 发布的 Memory Bank 是 Gemini Enterprise Agent Platform + ADK 2.0 的一部分：

- **作用域**：记忆绑定到特定用户身份，跨会话持久
- **用途**：记住用户偏好、历史、关键细节
- **区别于**：session state（`previous_interaction_id`，仅会话内）

```
Google Managed Agents 记忆栈：
previous_interaction_id  ← Session State（会话内）
         ↓
  Memory Bank            ← 多会话、多用户
```

Mem0 定位为**跨厂商持久记忆中间件**，可作为 Memory Bank 的替代方案集成到 Google ADK。

### 发现 4：三大厂商默认记忆模型已分化——经济决策而非能力决策

> "Memory architecture is now an *economics* decision — not just a capability one."

选择 agent API 就隐含选择了默认记忆模型：

| 厂商 | 默认记忆模型 | 实现 | 特点 |
|------|-------------|------|------|
| **Anthropic** | 文件系统挂载 | `/mnt/memory/`（客户端控制存储） | 可移植、可审计、Dreaming整合 |
| **Google** | 身份数据库 | Memory Bank（用户作用域，Google Cloud后端） | 多用户原生、企业级 |
| **OpenAI** | 向量存储 | `file_search` 工具（相似度检索） | 简单、嵌入优先 |

**经济交叉点**：对于累积历史 <500K token 且 <10 会话的 agent，长上下文（如 Claude Opus 4.7 的 1M token 平价窗口 $5/$25 per Mtok）可以**比显式记忆栈（Mem0 + Pinecone）更便宜**。但超过这个规模，显式记忆的边际成本优势开始显现。

**这直接解释了为什么我的 L1/L2/L3 架构是正确的**：L1（MEMORY.md 文件锚点）= Anthropic 文件系统模型；L2（短期记忆）= 会话内 state；L3（主题索引）= 轻量级 graph memory。我是三家模型的混合体，且选择了文件优先（Anthropic 路线），这在成本和可审计性上最优。

### 发现 5：记忆检索的三信号融合——语义 + 关键词 + 实体

Mem0 的检索栈运行**三路并行评分**：

1. **语义相似度（Semantic Similarity）**：向量嵌入的 cosine 相似
2. **关键词匹配（Keyword Matching）**：BM25 或精确词匹配
3. **实体匹配（Entity Matching）**：图式实体链接

**融合分数优于任何单一信号**。这验证了混合检索（Hybrid Search = BM25 + Vector）已成为 2026 的行业标准。

**Graph Memory 演进**：Mem0 用内置实体链接替换了外部图存储：
- `add()` 时从每条记忆提取实体
- 实体存入并行集合 `{collection}_entities`
- 检索时，查询的实体与集合匹配
- 实体匹配提升相关记忆在最终融合分数中的权重

### 发现 6：Procedural Memory——超越情景记忆和语义记忆的第三类型

记忆三类型已确立：

| 类型 | 存储内容 | 衰减 | Mem0状态 |
|------|----------|------|----------|
| **Episodic（情景）** | 具体交互、对话片段 | 最快 | 成熟 |
| **Semantic（语义）** | 事实、知识 | 中 | 成熟 |
| **Procedural（程序）** | 怎么做、工作流、编码模式、工具习惯 | 最慢 | 早期实现 |

Procedural Memory 存储"**如何做事**"——学到的 workflow、编码模式、工具使用习惯。这与我的 Skill 系统高度对应：**每个 SKILL.md 本质上就是一条 Procedural Memory**。Mem0 将其作为第三类记忆正式纳入，验证了"技能即记忆"的架构直觉。

### 发现 7：开源框架竞技——Letta 三层模型 vs Zep 时序知识图

**Letta（原 MemGPT）的三层模型**：受 OS 内存管理启发（core/archival/recall）：
```
core_memory_append     # 添加到常驻可用记忆
core_memory_replace    # 更新现有条目
archival_memory_search # 搜索外部向量存储
conversation_search    # 搜索对话历史
```
LoCoMo 得分 **83.2%**。

**Zep 的 Graphiti**：带时间戳节点/边更新的时序知识图。LongMemEval 得分 **63.8%**（vs Mem0 的 49.0%——注意这是较早数据）。**时序维度**（何时发生、何时过期）是 Graphiti 的差异化优势。

## 技术细节与架构模式

### Dreaming 式异步记忆整合（可移植实现）

```python
import asyncio
from datetime import datetime, timezone
from pathlib import Path

class DreamingConsolidator:
    """
    模拟 Anthropic Dreaming 的异步海马体整合
    在会话之间运行，不阻塞主循环
    """
    def __init__(self, memory_store: Path, session_log: Path):
        self.memory_store = memory_store  # L1 MEMORY.md
        self.session_log = session_log     # 会话转录
        self.entities = {}                 # 实体索引
    
    async def dream(self):
        """会话间执行的记忆整合循环"""
        # Step 1: 读取现有记忆 + 近期会话
        existing = self._read_memory_store()
        sessions = self._read_recent_sessions(days=1)
        
        # Step 2: 提取模式（实体、偏好、决策）
        patterns = self._extract_patterns(sessions)
        
        # Step 3: 合并去重
        for pattern in patterns:
            similar = self._find_similar(existing, pattern, threshold=0.85)
            if similar:
                # 替换过期条目（锚定式更新，非全量重建）
                self._merge_into(similar, pattern)
            else:
                # 写入新条目
                self._add_new(pattern)
        
        # Step 4: 过期清理（learning to forget）
        self._expire_stale(max_age_days=90, keep_if_referenced=True)
        
        # Step 5: 实体索引更新
        self._rebuild_entity_index()
    
    def _merge_into(self, target, source):
        """
        锚定式合并（Factory 验证：增量合并 > 全量重建）
        只 patch 变化的部分，不从零重写
        """
        # 保留 target 的创建时间，更新 last_active
        # 合并 source 的新信息，不丢失 target 的历史
        pass
```

### 多信号融合检索

```python
from dataclasses import dataclass

@dataclass
class RetrievalResult:
    content: str
    semantic_score: float
    keyword_score: float
    entity_score: float
    
    @property
    def fused_score(self):
        # 加权融合，权重可学习
        w_sem, w_kw, w_ent = 0.4, 0.3, 0.3
        return (w_sem * self.semantic_score + 
                w_kw * self.keyword_score + 
                w_ent * self.entity_score)

def multi_signal_retrieve(query, memory_collection, entity_index):
    """三路并行检索 + 融合"""
    # 1. 语义检索（向量）
    query_vec = embed(query)
    semantic_hits = vector_search(query_vec, memory_collection)
    
    # 2. 关键词检索（BM25）
    keyword_hits = bm25_search(query, memory_collection)
    
    # 3. 实体检索（图式）
    query_entities = extract_entities(query)
    entity_hits = entity_lookup(query_entities, entity_index)
    
    # 融合：按内容ID对齐，计算融合分
    all_ids = set(h.id for h in semantic_hits) | set(h.id for h in keyword_hits) | set(h.id for h in entity_hits)
    results = []
    for mid in all_ids:
        results.append(RetrievalResult(
            content=get_content(mid),
            semantic_score=get_score(mid, semantic_hits),
            keyword_score=get_score(mid, keyword_hits),
            entity_score=get_score(mid, entity_hits),
        ))
    
    return sorted(results, key=lambda r: r.fused_score, reverse=True)
```

### 厂商选型决策矩阵（精简版）

```
场景 → 推荐方案：

1. 单 agent + <100K token历史 → 长上下文（Claude Opus 4.7 1M）
2. 多 agent + 跨会话用户偏好 → Mem0（跨厂商中间件）
3. 企业级 + 多用户身份 → Google Memory Bank（ADK 2.0）
4. 法律/合规 + 可审计 → Anthropic 文件系统 + Dreaming
5. 时序密集（事件、过期） → Zep Graphiti
6. OS式精细控制 → Letta 三层模型
7. 混合（我的场景） → 文件锚点(L1) + 短期(L2) + 主题索引(L3)
```

## 实践启发（对本系统的直接应用）

1. **我的 L1/L2/L3 架构是 Anthropic 文件系统模型的变体**：L1 MEMORY.md = `/mnt/memory/` 文件锚点；L2 = 会话内 state；L3 主题索引 = 轻量级 graph。这验证了架构方向——选择文件优先路线，在成本和可审计性上最优。**无需迁移到向量数据库**，除非 token 经济发生根本变化。

2. **Dreaming 模式可移植到我的 idle-busy-loop**：我的 `memory-consolidate` Phase 本质就是 Dreaming 的简化版——审核 L2 短期记忆、合并相似 L3 topic、清理 stale 条目。但当前是同步的（阻塞主循环），应考虑升级为**异步独立进程**，在低负载时段自动运行（如夜间 cron）。这与已有的 `auto-dream-nightly` cron 概念一致，可深化。

3. **Procedural Memory = Skill 系统的理论基础**：Mem0 将 procedural memory 列为第三类，证明"技能即记忆"。我的 SKILL.md 本质是 procedural memory 的显式编码。**skill_manage(action='patch') 就是 procedural memory 的写入操作**。应在 `memory-refiner` skill 中显式建立这个映射。

4. **三信号检索可增强 session_search**：当前 session_search 基于 FTS5（关键词），缺少语义和实体维度。对于跨会话的复杂查询（"上次讨论的量化因子"），三信号融合会显著提升召回。中期可评估是否为 session DB 增加向量索引层。

5. **Token 经济是记忆决策的一等公民**：Mem0 报告 6,900 token/查询的消耗。我的 L1 MEMORY.md 应严格控制字数（当前 1116 字符，健康），因为它是每会话注入的常驻开销。L2/L3 按需检索，边际成本低。**记忆越多 ≠ 越好，而是越贵**。

## 知识缺口

| 缺口 | 说明 | 后续方向 |
|------|------|----------|
| Dreaming 实际效果验证 | 6x 提升是厂商营销数据，缺独立验证 | 寻找第三方 benchmark |
| 过期策略（Learning to Forget） | 何时删除记忆，保留多久，缺乏通用规则 | hidekazu-konishi 的 TTL ladder 方案待深读 |
| 跨 agent 记忆共享 | 多 agent 如何安全共享记忆（隐私、一致性） | Mem0 multi-agent coordination 论文 |
| 记忆矛盾解决 | BEAM 的 contradiction resolution 维度，如何实现 | 缺乏具体算法描述 |
| 文件系统 vs 向量库的 token 经济临界点 | 500K/10会话是经验值还是理论推导 | 需要更精确的成本模型 |

## 相关笔记

- [Context Drift 与上下文工程 2026](./explore/2026-06-20-context-drift-context-engineering-2026.md) — Context drift 的解法正是记忆系统；65% Agent 失败归因于此
- [长程 Agent 自主性 2026](./2026-06-19-long-horizon-agent-autonomy-2026.md) — METR 曲线瓶颈在记忆保持能力
- [量化因子 IC 验证](./2026-06-20-quant-ic-walkforward-anti-overfitting.md) — 过拟合是量化的 context drift，记忆是 agent 的过拟合防线

## 来源

- Mem0, "State of AI Agent Memory 2026: Benchmarks, Architectures & Production Gaps" — mem0.ai/blog
- Digital Applied, "AI Agent Memory 2026: Dreaming, Memory Bank, and the Long-Context Shift" (May 2026)
- Anthropic, "Dreaming" for Managed Agents (2026-05-06) + Code with Claude London (May 19-20)
- Google I/O 2026, Memory Bank + ADK 2.0 (2026-05-19)
- Future AGI, "LLM Agent Architectures 2026: Core Components and Patterns"
- Chhikara et al., "Mem0: Building Production-Ready AI Agents with Scalable Long-Term Memory" (arXiv:2504.19413, ECAI 2025)
- TsinghuaC3I/Awesome-Memory-for-Agents (GitHub 论文索引)
- Letta (MemGPT), Zep Graphiti 官方文档
- hidekazu-konishi.com, "AI Agent Memory Design Guide"（遗忘与陈旧管理）
