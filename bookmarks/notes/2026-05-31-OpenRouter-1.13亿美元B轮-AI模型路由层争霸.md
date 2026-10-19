# OpenRouter 1.13亿美元B轮融资：AI模型路由层争霸

> **来源**：OpenRouter Official · openrouter.ai · 2026-05-28
> **原文**：https://openrouter.ai/announcements/series-b
> **热度**：HN #3, 413 pts, 198 comments
> **格式**：双格式(MD + HTML) · 含借鉴进化点 · RAG/wiki联动

## 摘要

OpenRouter 宣布完成 1.13 亿美元 B 轮融资，由 CapitalG（Alphabet 旗下增长基金）领投，NVentures（NVIDIA）、ServiceNow、MongoDB、Snowflake、Databricks 等战略投资者跟投。半年内周 token 处理量从 5 万亿增长至 25 万亿，全年预计处理超过 1 千万亿（quadrillion）tokens，服务 800 万+ 开发者、400+ 模型。OpenRouter 定位为 AI 应用的路由网关层（routing & gateway），解决多模型生产环境中的路由、可靠性、成本优化和合规问题。

## 核心内容

### 1. 融资背景与战略意义

投资方阵容极具战略含义：
  CapitalG（Alphabet）— 搜索巨头的 AI 基础设施布局
  NVentures（NVIDIA）— GPU 巨头确保推理路由层的生态控制
  MongoDB/Snowflake/Databricks Ventures — 数据平台公司押注 AI 中间件

这不是简单的财务投资，而是整个企业基础设施生态对"多模型路由层"这一品类的集体确认。

### 2. 增长数据

  周 token 量：5T → 25T（6个月，5倍增长）
  开发者：8M+
  模型：400+
  年处理量预估：>1 quadrillion tokens

这个增速说明市场正在从"单模型试点"快速切换到"多模型生产系统"。

### 3. 产品能力矩阵

OpenRouter 已构建的能力：
  多模态推理：文本、图像、音频、语音、转录、嵌入、视频
  企业控制：Workspaces、支出管理、安全护栏、零数据保留策略
  智能路由：Provider 级故障转移、成本/延迟优化、质量感知路由

### 4. 竞争格局

AI 模型路由/网关赛道的玩家：
  OpenRouter — 开发者优先，B 轮后企业能力加强
  LiteLLM — 开源方案，功能类似但规模较小
  Portkey — 企业 AI 网关，侧重可观测性
  自建网关 — 大厂自研（如我们自己的 Hermes provider 系统）

## 关键概念

  模型路由（Model Routing）：根据请求特征（成本、延迟、质量）自动选择最优模型和 provider
  多模型生产系统（Multi-model production）：企业从单一模型试点转向多模型混合部署
  智能网关（Intelligent Gateway）：位于 Agent 和模型 Provider 之间的中间件层

## 能力边界

  OpenRouter 是中间层，不拥有模型，依赖上游 Provider 可用性
  对于需要数据不出境/完全本地化的场景，仍需自建网关
  路由质量取决于使用数据的积累，小用户可能不如大用户获得最优路由

## 最佳实践

  多 Provider 部署时，路由层是必要基础设施而非可选优化
  成本优化和质量感知路由应同时考虑，不能只看价格
  企业部署时应配置零数据保留策略和支出上限

## 🔍 借鉴学习进化点（必填）

| # | 点 | 原文要点 | 对当前系统的借鉴 | 行动计划 |
|---|-----|---------|---------------|---------|
| 1 | Provider 级故障转移 | OpenRouter 的 provider-level failover 机制 | Hermes 的 provider failover 可借鉴其健康检查和自动切换逻辑 | 完善 antigravity-model-failover skill，增加 provider 健康度评分 |
| 2 | 质量感知路由 | 根据请求质量需求动态选模型 | 当前 Hermes 的模型选择可加入"质量档位"参数 | 在 model-adapter skill 中增加 quality_tier 路由参数 |
| 3 | 多模态统一入口 | 文本/图像/音频/语音/视频统一 API | Hermes 可参考设计统一的 multimodal 网关接口 | 评估 Hermes 当前多模态支持，制定统一接口规范 |
| 4 | 企业级支出管控 | Workspaces + spend management + guardrails | 对 Token 成本管控有直接参考价值 | 在 zai-quota-monitor 基础上增加 workspace 级预算管理 |
| 5 | 战略投资者生态 | 基础设施公司集体押注路由层 | AI 应用开发应优先选择路由层方案而非直连模型 | 评估将更多模型调用迁移到 OpenRouter 或类似路由层 |

## 🔗 RAG / Wiki 联动

### 当前状态
  wiki-kb 中已有 AI 基础设施相关笔记（Anthropic Colossus2、GPU 网络优化）
  RAG 索引中模型路由相关内容较少
  Memory 中已有 provider failover 经验

### 改进方案
1. 将本文加入 AI 基础设施专题索引
2. 在 wiki-kb 中建立"AI 中间件"知识节点
3. 补充模型路由层的架构模式到知识库

### 已执行操作
- ✅ 笔记已写入 bookmarks/notes
- ⏳ 更新 ubot-topics-index.json
- ⏳ 写入交换池

---

## 相关笔记

- [2026-05-31-Rotary-GPU-消费级显卡运行35B-MoE模型](./2026-05-31-Rotary-GPU-消费级显卡运行35B-MoE模型.md)
- [2026-05-31-领域专长才是真正的护城河-Agent时代的价值重估](./2026-05-31-领域专长才是真正的护城河-Agent时代的价值重估.md)
- [2026-05-31-OpenRouter-113M-B轮-AI模型路由基础设施](./2026-05-31-OpenRouter-113M-B轮-AI模型路由基础设施.md)
