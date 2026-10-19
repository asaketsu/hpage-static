# NAS本地部署向量模型提升Hermes混合检索能力

> **来源**：设计虱聊科技 · 微信公众平台 · 2026-05-26
> **原文**：https://mp.weixin.qq.com/s/qjSOnPMbdkeW9GgfSIAvEA
> **笔记ID**：nas-embedding-hermes-hybrid
> **格式**：双格式(MD + HTML) · 含借鉴进化点 · RAG/wiki联动
> **关联**：[MCP协议生态与Agentic-RAG架构深度学习](2026-04-27-MCP协议生态与Agentic-RAG架构深度学习.md) [RAG与MCP架构差异](2026-04-26-RAG与MCP架构差异.md) [gbrain-hybrid-search-proposal](2026-04-11-gbrain-hybrid-search-proposal.md)

## 摘要

文章以绿联DX4600 NAS为例，讲解如何通过Docker部署Ollama + 向量模型（dmeta-embedding-zh / bge-base-zh-v1.5），实现Hermes的本地向量搜索，与FTS5关键词检索形成混合检索。核心观点：AI"记不住"不是模型笨，是搜索方式有天花板——关键词搜"字一样"的，向量搜"意思一样"的。

## 核心内容

### 1. 问题：FTS5关键词搜索的局限

- Hermes 历史会话存入 SQLite，FTS5 建索引
- FTS5 本质是关键词匹配，必须精确知道原文用了什么词
- 典型失败：聊过"Docker容器OOM被kill"，问"上次那个NAS内存问题"→搜不到
- 对话越多，匹配不精准问题越明显

### 2. 解法：向量搜索补位

- 向量 = 把文字变成数字串，代表"意思"
- "NAS内存不够用"和"Docker容器OOM"字面不同但向量接近
- 不用记原话，大概描述就能找到

### 3. 两种搜索各有优劣

| 维度 | 关键词搜索(FTS5) | 向量搜索 |
|------|-----------------|---------|
| 擅长 | 精确匹配：型号名、参数名 | 语义匹配：模糊描述、同义词 |
| 弱点 | 必须字面一致 | 精确术语可能不如关键词 |
| 最佳实践 | 混合使用，各取所长 | — |

### 4. 为什么本地部署

- 一次部署永远能用，不用月交API费
- 不依赖网络，断网也能用
- 数据不出门，对话记录留在本地

### 5. 部署方案（绿联DX4600为例）

Docker Compose 部署 Ollama：
```yaml
services:
  ollama:
    image: ollama/ollama:latest
    container_name: ollama
    network_mode: host
    environment:
      - OLLAMA_HOST=0.0.0.0
      - OMP_NUM_THREADS=2
    volumes:
      - ./ollama-data:/root/.ollama
    restart: unless-stopped
```

推荐模型：
- **herald/dmeta-embedding-zh** — 200MB，768维，低功耗CPU友好
- **bge-base-zh-v1.5** — 200MB，768维，中文优化
- bge-m3（1024维）— NAS CPU跑不动，经常超时

配置Hermes：告知向量模型地址 `NAS_IP:11434`，Hermes自动调用。向量化成功标志：Ollama日志返回200。

## 关键概念

| 概念 | 定义 |
|------|------|
| FTS5 | SQLite全文搜索引擎，基于关键词倒排索引，精确匹配 |
| 向量搜索 | 将文本转为向量（数字串），通过余弦相似度匹配语义 |
| 混合检索 | 关键词 + 向量双路检索，合并排序，兼顾精确和语义 |
| Ollama | 开源本地LLM运行框架，支持模型下载和管理 |
| dmeta-embedding-zh | 200MB中文向量模型，768维，适合低功耗设备 |
| 上下文窗口 | 128K~1M Token，存最近对话，满了就淘汰旧内容 |

## 能力边界

- 文章偏向入门教程，未涉及混合检索的具体融合算法（如何合并两路结果排序）
- 未讨论向量化历史会话的增量更新机制（新对话如何自动向量化）
- bge-m3 在 NAS 上失败，但未测试中间档模型（如 bge-large-zh）
- "下一篇讲踩坑"暗示还有后续，当前篇为上篇/部署篇

## 最佳实践

1. 低功耗设备选 200MB 级模型（dmeta / bge-base），别贪大
2. 混合检索是正解：关键词保精准，向量保语义
3. 不同设备多试几个模型，选最适合的
4. Docker Compose 部署，方便管理和重启

## 🔍 借鉴学习进化点（必填）

| # | 点 | 原文要点 | 对当前系统的借鉴 | 行动计划 |
|---|-----|---------|---------------|---------|
| 1 | 混合检索验证 | 关键词+向量各取所长 | ubot 已有 FTS5 + RAG 混合搜索（hybrid-search skill），可验证实际效果 | 检查当前 hybrid-search 配置是否最优，向量模型是否已启用 |
| 2 | 低功耗向量模型选择 | dmeta-embedding-zh 200MB/768维，N5105 CPU能跑 | jc-server 有 GPU，可用更高维模型，但 NAS 端 jbot 需轻量模型 | 确认 jbot 的向量模型配置，评估是否需降级到 dmeta |
| 3 | 增量向量化 | 文章未提及，但向量化历史会话后新对话需自动向量化 | hybrid-search skill 的 rag-index-rebuild 需支持增量更新 | rag-index-rebuild 增加 watch 模式，新笔记自动索引 |
| 4 | 搜索降级链整合 | 文章只讲向量，实际搜索需降级链 | search-fallback-chain skill 可将向量搜索纳入降级链 | 确认 hybrid-search 在 fallback chain 中的位置 |
| 5 | 向量化健康监控 | Ollama 返回200=成功 | 可增加向量搜索健康检查到 auto-dream | auto-dream 增加向量服务可用性检测 |

## 🔗 RAG / Wiki 联动（必填）

### 当前状态
- RAG：已有 hybrid-search skill，支持语义+关键词检索
- wiki-kb：已建立 [[wikilinks]] BFS 检索
- 向量模型：ubot(jc-server) 已配置，jbot 桌面端配置待确认

### 改进方案
1. 确认两端向量模型版本和维度一致性
2. rag-index-rebuild 增加增量更新模式（watch）
3. 向量搜索纳入 search-fallback-chain 降级链

### 已执行操作
- ✅ 笔记已存入 bookmarks/notes/，双格式输出
- ⏳ jbot 向量模型配置确认待执行
- ⏳ rag-index-rebuild 增量模式待开发


## 相关笔记
- [[2026-05-26-治好内耗的四句话见招拆招心态教育.md|治好内耗的四句话——"见招拆招"心态教育]]
- [[2026-05-26-AI时代科研人6个不可替代品质.md|AI时代科研人6个不可替代品质]]
- [[2026-05-22-Hermes-Agent四层记忆架构深度分析.md|Hermes Agent 四层记忆架构 — 深度分析与进化笔记]]
