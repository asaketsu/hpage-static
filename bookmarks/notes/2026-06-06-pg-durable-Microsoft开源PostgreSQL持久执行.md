# pg_durable：Microsoft 开源 PostgreSQL 数据库内持久执行引擎

> **来源**：Microsoft · GitHub · 2026-06
> **原文**：https://github.com/microsoft/pg_durable
> **格式**：双格式(MD + HTML) · 含借鉴进化点

## 摘要

Microsoft 开源 pg_durable——一个将持久执行（Durable Execution）引入 PostgreSQL 的扩展。它让长运行、容错的 SQL 函数成为可能，将工作流的每个步骤都 checkpoint 到数据库中。崩溃后自动恢复、重启后从断点续执行，无需额外的基础设施服务。这是 Microsoft "将计算拉近数据"战略的关键一步，也是 Azure HorizonDB 云服务的内置组件。

## 核心内容

### pg_durable 是什么

pg_durable 是一个 PostgreSQL 扩展（Rust 编写），在数据库内部实现持久执行。核心思想：一个 pg_durable 函数是一个 SQL 步骤图，PostgreSQL 逐步执行并 checkpoint。如果数据库崩溃，重启后自动从最后一个 checkpoint 恢复。

### 适用场景

1. **后端/数据工程师**：工作流与数据放在一起，不需要额外的队列/Worker/Cron 拼凑
2. **DBA/SRE**：自动化运维手册，可审计、可恢复
3. **数据/AI Pipeline 团队**：按行/文档/批次的持久执行

### 技术特点

- Rust 编写的 Postgres 扩展，高性能
- SQL 原生定义工作流，无需额外语言
- 自动 checkpoint + 崩溃恢复
- 已集成到 Azure HorizonDB（Microsoft 新一代 PostgreSQL 云服务）
- 677 Stars, 10 Forks（开源首周）

### 与竞品对比

Temporal / Cadence 等持久执行框架需要独立服务，pg_durable 直接嵌入数据库，运维成本极低。但功能丰富度和生态成熟度尚不及 Temporal。

## 关键概念

Durable Execution（持久执行）：一种编程模式，工作流的每一步都被持久化记录。如果执行中断（崩溃/重启），可从断点自动恢复，而不需要从头开始。是构建可靠后台任务的标准行业模式。

## 能力边界

- 目前是早期项目（256 commits），生产环境需谨慎评估
- 工作流复杂度受限于 SQL 表达能力
- 只支持 PostgreSQL，不适用于 MySQL/SQLite 等其他数据库
- 需要 Rust 编译环境（pg_durable 本身用 Rust 编写）

## 最佳实践

1. 从简单工作流开始（2-3 步），逐步增加复杂度
2. 利用 SQL 的审计能力追踪工作流状态
3. 在 Docker 环境中测试崩溃恢复场景

## 🔍 借鉴学习进化点（必填）

| # | 点 | 原文要点 | 对当前系统的借鉴 | 行动计划 |
|---|-----|---------|---------------|---------|
| 1 | 数据库内持久执行 | 工作流状态与数据同存一个 PG | Hermes Agent 的任务延续机制可借鉴：用 SQLite 存储任务 checkpoint | 评估在 task-continuity skill 中引入类似 checkpoint 机制 |
| 2 | SQL 步骤图模式 | 函数=步骤图，逐步 checkpoint | skill-pipeline 的 skill 串联执行可设计类似 checkpoint | 在 subtask-lifecycle skill 中加入步骤级持久化 |
| 3 | 崩溃自动恢复 | 重启后从最后 checkpoint 恢复 | Hermes Gateway 重启后任务恢复 | 评估 pg_durable/SQLite 作为 agent 任务持久层的可行性 |
| 4 | 嵌入式 vs 独立服务 | 无需额外队列/Worker/Cron | Hermes 系统的 cron + exchange-sync 可简化 | 长期评估用数据库持久执行替代 cron 拼凑模式 |

## 🔗 RAG / Wiki 联动

### 当前状态
- 已有 harness-checkpoint 和 task-continuity skill
- 无持久执行相关笔记

### 改进方案
1. 将 pg_durable 的 checkpoint 模式与现有 task-continuity 对比
2. 评估作为 Hermes 任务持久层的可行性

### 已执行操作
- ✅ 本笔记已创建
- ⏳ 待与 harness-checkpoint skill 交叉验证

关联：[Redis 8.8](2026-05-21-Redis-8-8-新数组结构-限流-性能提升.md)

## 相关笔记
- [SQLite 足以支撑持久化工作流](2026-05-30-SQLite足以支撑持久化工作流-Agent时代的极简基础设施.md) — Agent 持久化基础设施对比
- [OpenClaw 知识库加载攻略](2026-04-02-OpenClaw知识库加载攻略.md) — 数据持久化模式
- [Karpathy LLM Wiki second brain](2026-04-05-Karpathy-LLM-Wiki-second-brain.md) — 知识管理系统设计
