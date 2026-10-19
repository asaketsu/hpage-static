# 数据治理框架（Data Governance Framework）学习笔记

> 日期: 2026-05-21
> 触发: sniff-auto 队列
> 来源: IBM Think, Google Cloud 文档（Tavily 432 降级至 curl 直取）

## 核心摘要

数据治理是一套管理数据全生命周期（采集→存储→使用→销毁）的原则、策略和流程体系，核心目标是确保数据**安全、准确、可用**。2026 年的治理框架已从传统合规驱动转向 **AI-Ready 数据治理**。

## 关键发现

### 1. AI 时代的数据治理新要求
- 治理范围扩展到非结构化数据（RAG 系统输入/输出、向量数据库、AI Agent 数据）
- 数据治理需确保 AI 模型训练数据质量，防止幻觉和偏见
- Agent 替代人类访问数据时，RBAC 权限模型需要重新设计

### 2. 数据治理框架核心组件
- **角色体系**: 治理委员会(C-level) → 数据所有者(域级) → 数据管家(日常管理) → 利益相关者(数据消费)
- **政策标准**: 数据格式、数据模型、MDM、元数据、命名规范
- **审计流程**: 持续审计 → 合规验证 → 演进优化
- **工具链**: 自动数据发现/分类、RBAC、元数据管理、数据目录、数据血缘追踪

### 3. 数据治理 vs 数据管理
- 数据治理是数据管理的**子集**，聚焦策略制定和质量保证
- 数据管理范围更广：存储、处理、安全、架构
- 两者需紧密协作：治理定规则，管理执行落地

### 4. Google Cloud AI-First 治理五要点
- 加速 AI 驱动的洞察
- 消除数据孤岛降低成本
- 前瞻性合规（GDPR/CCPA）
- 数据民主化 + 自服务目录
- 实时风险监控

## 对工作的价值

1. **量化/AI 项目**: 数据质量是模型表现的基石，治理框架直接影响策略回测可靠性
2. **多 Agent 系统**: Agent 访问数据的权限管控需要治理框架支撑
3. **合规压力**: 金融/医疗场景数据治理是监管硬要求

## 行动建议

1. 评估当前项目数据管理现状，识别治理缺口
2. 优先建立数据质量指标体系（错误率、一致性、完整性）
3. 为 AI/Agent 数据流设计最小权限访问模型
4. 建立数据血缘追踪机制，确保可审计性

## ⚠️ 标注
- Tavily 432 不可用，通过 curl 直取 IBM/Google Cloud 页面获取
- Dataversity 页面 404，未纳入

## 相关笔记
- [数据治理-Data-Catalog](../2026-05-03-数据治理-Data-Catalog.md)
- [数据治理-Data-Lineage血缘分析](../2026-05-05-数据治理-Data-Lineage血缘分析.md)
- [数据治理-Data-Quality数据质量](../2026-05-05-数据治理-Data-Quality数据质量.md)
- [数据治理-data-quality](../2026-05-08-数据治理-data-quality.md)
- [数据治理趋势AI工程化](../2026-05-10-数据治理趋势AI工程化.md)
- [数据治理-data-catalog](../2026-05-12-数据治理-data-catalog.md)
- [数据治理-data-quality](../2026-05-12-数据治理-data-quality.md)
- [数据治理框架2026趋势](../2026-05-16-数据治理框架2026趋势.md)
- [数据治理-data-catalog](../2026-05-18-数据治理-data-catalog.md)
- [Active-Data-Selection-LLM训练动态数据选择前沿](../2026-05-20-Active-Data-Selection-LLM训练动态数据选择前沿.md)
- [数据治理-data-quality-2026前沿](../2026-05-20-数据治理-data-quality-2026前沿.md)
- [data-lineage-governance](../ai-agent/2026-05-08-data-lineage-governance.md)
- [数据治理-data-catalog](../data-governance/2026-05-05-数据治理-data-catalog.md)
- [数据治理-框架演进](../data-governance/2026-05-08-数据治理-框架演进.md)
- [数据血缘-lineage-工具全景](../data-governance/2026-05-09-数据血缘-lineage-工具全景.md)
- [数据治理-governance-framework](../data-governance/2026-05-15-数据治理-governance-framework.md)
- [skills-catalog](../data-governance/skills-catalog.md)
- [skills-data-science](../data-governance/skills-data-science.md)
- [数据治理-data-quality-v2](2026-05-04-数据治理-data-quality-v2.md)
- [数据治理-lineage-v2](2026-05-04-数据治理-lineage-v2.md)
- [data-catalog-数据治理](2026-05-05-data-catalog-数据治理.md)
- [data-governance-framework](2026-05-06-data-governance-framework.md)
- [data-governance-framework-2026](2026-05-07-data-governance-framework-2026.md)
- [data-quality-governance](2026-05-07-data-quality-governance.md)
- [data-catalog](2026-05-08-data-catalog.md)
- [data-catalog-governance](2026-05-09-data-catalog-governance.md)
- [data-lineage-governance-tools](2026-05-09-data-lineage-governance-tools.md)
- [data-quality-framework](2026-05-09-data-quality-framework.md)
- [数据治理-governance-framework](2026-05-09-数据治理-governance-framework.md)
- [数据治理框架-2025对比](2026-05-09-数据治理框架-2025对比.md)
- [data-quality-governance-2026](2026-05-10-data-quality-governance-2026.md)
- [数据治理-数据血缘-lineage](2026-05-10-数据治理-数据血缘-lineage.md)
- [数据治理框架-2026最佳实践](2026-05-10-数据治理框架-2026最佳实践.md)
- [data-lineage-governance](2026-05-11-data-lineage-governance.md)
- [data-quality-governance-framework](2026-05-11-data-quality-governance-framework.md)
- [data-governance-data-catalog](2026-05-12-data-governance-data-catalog.md)
- [data-quality-ai-driven-automation](2026-05-13-data-quality-ai-driven-automation.md)
- [数据治理框架](2026-05-14-数据治理框架.md)
- [数据治理-data-catalog](2026-05-19-数据治理-data-catalog.md)
- [数据治理-data-quality](2026-05-19-数据治理-data-quality.md)
- [数据治理-lineage](2026-05-19-数据治理-lineage.md)
