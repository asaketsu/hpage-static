# Google AI Mode 搜索广告：AI 商业化的分水岭时刻

> **来源**：Google Ads & Commerce Blog · Hacker News #4, 347 pts · 2026-05-20
> **原文**：https://blog.google/products/ads-commerce/google-marketing-live-search-ads/
> **笔记ID**：sniff-google-ai-mode-ads
> **格式**：双格式(MD + HTML) · 含借鉴进化点 · RAG/wiki联动

## 摘要

Google 正式宣布在 AI Mode 搜索结果中引入广告，标志着搜索引擎的 AI 化进入商业化阶段。基于 Gemini 模型，Google 推出了三种新广告格式：Conversational Discovery ads（对话式发现广告）、Highlighted Answers（高亮回答广告）和 AI-powered Shopping ads（AI 购物广告）。数据显示 75% 用户表示 AI Mode 帮助他们更快做出购买决策。这一变化将深刻影响 SEO 生态、广告主策略和用户搜索行为。

## 核心内容

### 1. 三种新广告格式

**Conversational Discovery ads**
用户在 AI Mode 中进行多轮对话时，广告以"建议"形式自然融入对话流。不是传统关键词匹配，而是基于对话上下文的语义投放。广告会解释"为什么这个产品适合你"。

**Highlighted Answers**
在 AI 生成的回答中，品牌内容以"高亮答案"形式出现，类似知识面板但带有商业属性。品牌可以直接在 AI 回答中获得突出展示位。

**AI-powered Shopping ads**
购物广告升级为 AI 对话代理，可以实时回答用户关于产品的具体问题（尺码、材质、兼容性等），并直接引导购买。

### 2. 技术架构

  所有新广告格式基于 Gemini 模型生成
  广告内容与搜索 AI 回答共享同一推理管线
  Performance Max 和 AI Max 工具是投放新广告格式的前置条件
  Direct Offers 功能扩展至原生结账和旅游预订

### 3. 行业影响

  传统 SEO 可能被"AEO"（AI Engine Optimization）取代
  广告主需要适应对话式广告的全新创意形式
  Google 核心搜索广告业务的 ARPU 可能因 AI 广告而显著提升
  竞争对手（Perplexity、Bing Copilot）面临更大商业化压力

## 关键概念

**AI Mode**：Google 搜索的 AI 增强模式，用户可以与 Gemini 进行多轮对话式搜索，获取深度分析而非链接列表

**Conversational Discovery**：在对话流中插入的商业推荐，模拟"朋友推荐产品"的自然体验

**Performance Max**：Google 的 AI 驱动广告投放平台，利用机器学习自动优化跨渠道广告投放

## 能力边界

  新广告格式仍在测试阶段，尚未全量上线
  广告透明度问题——用户可能难以区分 AI 回答和广告
  Gemini 的广告生成质量仍有不确定性
  对中小广告主的门槛可能提高（需要理解 AI 广告机制）

## 最佳实践

  广告主应立即设置 Performance Max 和 AI Max，为 AI 广告格式做好准备
  内容策略需从"关键词优化"转向"语义场景优化"
  监控 AI Mode 广告的 ROAS 表现，与传统搜索广告对比
  关注 Google 的广告透明度政策变化

## 🔍 借鉴学习进化点（必填）

| # | 点 | 原文要点 | 对当前系统的借鉴 | 行动计划 |
|---|-----|---------|---------------|---------|
| 1 | AEO 取代 SEO | AI 搜索中传统 SEO 失效 | 笔记/内容的 RAG 检索应考虑 AI 搜索优化，而非仅关键词 | 在 knowledge-lint 中加入语义可发现性检查 |
| 2 | 对话式商业融合 | 广告自然融入 AI 对话 | Hermes Gateway 的对话中可设计"智能推荐"模式，在适当时机推荐 skill/工具 | 探索 skill-auto-inject 的"智能推荐"变体 |
| 3 | 透明度与信任 | 用户难以区分 AI 回答和广告 | AI Agent 的输出应明确标注来源和置信度，建立用户信任 | 在所有 AI 生成内容中加入来源标注模板 |
| 4 | Performance Max 模式 | AI 自动优化跨渠道投放 | Hermes 的 model-adapter 可借鉴自动选择最优模型/provider 的思路 | 优化 selective-proxy 的智能路由逻辑 |
| 5 | 多轮对话上下文 | 广告基于完整对话上下文 | 笔记系统应利用完整会话上下文而非单次查询 | 在 session-boot 中加入上下文感知的内容推荐 |

## 🔗 RAG / Wiki 联动（必填）

### 当前状态
- bookmarks/notes 中已有 AI SEO 操纵相关笔记 (2026-05-21-Google-AI被SEO操纵的调查报告.md)
- RAG 索引覆盖搜索优化相关内容

### 改进方案
1. 将 AI Mode 广告格式加入 RAG 索引，与 SEO 操纵笔记交叉关联
2. 更新 content-meow skill 的内容优化策略，加入 AEO 指导

### 已执行操作
- ✅ 笔记已生成并存入 bookmarks/notes
- ⏳ 与 Google AI 被SEO操纵笔记的交叉关联待更新

关联：[Google AI 被SEO操纵的调查报告](2026-05-21-Google-AI被SEO操纵的调查报告.md)


## 相关笔记

- [[2026-05-21-Google-AI被SEO操纵的调查报告.md]]
- [[2026-04-05-Google-Gemma4-open-source.md]]
- [[google-fonts-china-direct-access.md]]
- [[google-a2a-protocol-multi-agent-2026-05-19.md]]
- [[2026-04-01-Ontology驱动的AI知识引擎.md]]
