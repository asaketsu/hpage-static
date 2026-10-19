# OpenRouter $113M B 轮融资：AI 模型路由层成为基础设施核心

> **来源**：OpenRouter Official Blog · 2026-05-28
> **原文**：https://openrouter.ai/announcements/series-b
> **评分**：⭐⭐⭐⭐/5
> **标签**：#AI基础设施 #OpenRouter #模型路由 #多模型 #融资
> **关联**：[Anthropic 收购 Stainless](2026-05-24-Anthropic收购Stainless-SDK基础设施争夺战.md) [AI编码工具战争](2026-05-24-AI编码工具战争-CodexClaudeCodeCursor收敛为分层架构.md)

## 摘要

OpenRouter 宣布完成 $113M B 轮融资，由 CapitalG（Alphabet 独立增长基金）领投，NVentures（NVIDIA）、ServiceNow Ventures、MongoDB Ventures、Snowflake Ventures、Databricks Ventures 等战略投资者参投。过去六个月，平台周 token 处理量从 5 万亿增长至 25 万亿，预计全年处理超过 1 千万亿 tokens，服务 800 万+开发者和 400+ 模型。OpenRouter 定位为 AI 模型路由和网关层，处理多模型生产系统中的路由、可靠性、成本优化和合规需求。

## 核心内容

### 1. 融资结构与战略意义

投资方阵容极具代表性：
  CapitalG（Alphabet）— 搜索/云巨头的 AI 基础设施布局
  NVentures（NVIDIA）— GPU 巨头确保推理侧生态控制
  ServiceNow/MongoDB/Snowflake/Databricks — 企业级数据/应用平台的 AI 深度集成
  a16z/Menlo Ventures — 延续早期投资

这不是普通的风投轮次，而是基础设施生态的合围：每一方都依赖 OpenRouter 作为多模型 AI 时代的中间件层。

### 2. 增长数据

  周 token 量：5 万亿 → 25 万亿（6 个月 5x）
  开发者：8M+
  模型数：400+
  年预计处理量：1 千万亿+ tokens

### 3. 产品能力扩展

  多模态推理：图像、音频、语音、转录、嵌入、视频模型全覆盖
  企业控制：Workspaces、支出管理、guardrails、零数据保留策略
  智能路由：Provider 级别故障转移、成本/延迟优化、质量感知路由

### 4. 市场定位

OpenRouter 不做模型、不做应用，专注做"模型路由器"——在 Agent 和模型提供商之间处理路由、可靠性、成本优化和合规。这一层的价值随多模型生产系统的普及指数增长。

## 关键概念

  模型路由层（Model Routing Layer）：介于 Agent 和模型提供商之间的中间件，处理请求分发、故障转移、成本优化
  质量感知路由（Quality-Aware Routing）：根据请求特征选择最优模型，超越简单负载均衡
  多模型生产系统：企业从单一模型试点转向多模型混合部署，需要统一网关管理

## 能力边界

  依赖外部模型提供商的可用性和质量
  路由决策的透明度有限（黑盒优化）
  合规需求在跨区域部署时复杂度增加
  企业级 SLA 依赖上游模型提供商的稳定性

## 最佳实践

  多模型策略应在设计阶段就引入路由层，而非后期改造
  成本优化需结合 token 预算和模型能力矩阵综合考虑
  生产环境必须配置 provider 级故障转移

## 🔍 借鉴学习进化点

| # | 点 | 原文要点 | 对当前系统的借鉴 | 行动计划 |
|---|-----|---------|---------------|---------|
| 1 | 智能路由降级链 | OpenRouter 的 provider-level failover 和质量感知路由 | Hermes 的 model-adapter 和 selective-proxy skill 可借鉴其路由决策逻辑 | 优化 antigravity-model-failover skill，增加质量感知路由维度 |
| 2 | 多模态统一网关 | 图像/音频/语音/转录/嵌入/视频全覆盖 | Hermes Gateway 当前以文本为主，多模态路由是未来方向 | 在 gateway config 预留多模态路由配置项 |
| 3 | 企业合规层 | guardrails + 零数据保留策略 | Hermes 企业部署需要数据合规中间件 | 调研 guardrails 实现方案，为 hermes-disaster-recovery skill 增加合规检查 |
| 4 | 支出管理 | Workspaces + spend management | 多 profile/多用户场景需要 token 预算管理 | 在 zai-quota-monitor 基础上增加 workspace 级别预算控制 |
| 5 | 模型路由策略收敛 | 市场共识：多模型时代需要统一路由层 | 验证了 Hermes selective-proxy + model-adapter 的架构方向正确 | 继续深化模型路由 skill 的决策树 |

## 🔗 RAG / Wiki 联动

### 当前状态
- AI基础设施相关笔记已有 5+ 篇（Anthropic Colossus2, Stainless 收购, GPU网络优化等）
- model-adapter skill 已在生产使用
- selective-proxy skill 支持按模型注入代理

### 改进方案
1. 将 OpenRouter 路由决策逻辑提炼为可复用的路由策略模板
2. 在 wiki-kb 中增加"AI基础设施"专题页

### 已执行操作
- ✅ 笔记已生成
- ⏳ 路由策略模板待提炼为 skill

---

## 相关笔记

- [2026-05-31-请别用Vibe搞砸这个软件-AI编程对开源的冲击](./2026-05-31-请别用Vibe搞砸这个软件-AI编程对开源的冲击.md)
- [2026-05-31-领域专长才是真正的护城河-AI时代的价值反转](./2026-05-31-领域专长才是真正的护城河-AI时代的价值反转.md)
- [2026-05-31-OpenRouter-1.13亿美元B轮-AI模型路由层争霸](./2026-05-31-OpenRouter-1.13亿美元B轮-AI模型路由层争霸.md)
