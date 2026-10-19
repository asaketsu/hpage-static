# Cloudflare Agents Week 2026：Agentic Cloud 全栈基础设施

> **来源**：Ming Lu & Anni Wang · Cloudflare Blog · 2026-04-20
> **原文**：https://blog.cloudflare.com/agents-week-in-review
> **笔记ID**：sniff-20260524-cloudflare-agents-week
> **格式**：双格式(MD + HTML) · 含借鉴进化点 · RAG/wiki联动

## 摘要

Cloudflare 举办首届 Agents Week，发布了完整的 Agentic Cloud 基础设施栈。核心产品包括：Sandboxes GA（Agent 专属持久隔离环境）、Artifacts（Git 兼容版本化存储）、Durable Object Facets（每个 Agent App 独立 SQLite 数据库）、Agent Readiness Score（网站 Agent 适配评分）。Cloudflare 的核心论点：传统云的"一应用服务多用户"模型无法支撑 Agent 时代的"每用户多 Agent 并行"需求，需要全新的 Cloud 2.0。

## 核心内容

### 计算层
1. **Sandboxes GA**：给 Agent 一台真正的电脑——持久的隔离环境，有 shell、文件系统、后台进程，按需启动并恢复状态
2. **Artifacts**：Git 兼容的版本化存储，Agent 可创建数百万 repo、fork 远程仓库、对接任意 Git 客户端
3. **Durable Object Facets**：Dynamic Workers 可为每个 AI 生成的 App 实例化独立 SQLite 数据库
4. **Workflows 控制面重构**：支持 50,000 并发 + 300 创建/秒，专为长时间运行的 Agent 设计

### 安全层
5. **Sandbox Egress 控制**：零信任出口代理，可注入凭证和执行动态安全策略
6. **私有网络**：Agent 安全连接内部服务
7. **身份感知安全**：默认内置安全，而非事后补充

### 工具层
8. **Agent Toolbox**：模型、工具、上下文的统一框架
9. **AI Gateway**：模型路由和管理
10. **浏览器自动化**：Agent 可操作真实浏览器

### Web 层
11. **Agent Readiness Score**：检测网站是否 Agent-ready
12. **Shared Dictionaries**：为 Agentic Web 优化的压缩方案
13. **Flagship**：AI 时代的 Feature Flags

## 关键概念

| 概念 | 定义 |
|------|------|
| Agentic Cloud | 为 Agent 工作负载设计的基础设施，区别于传统 Web 服务 |
| Sandboxes | 持久、隔离的计算环境，Agent 的"个人电脑" |
| Artifacts | Git 兼容的版本化存储系统 |
| Agent Readiness | 网站对 Agent 访问的适配程度 |
| Cloud 2.0 | 以 Agent 为主要工作负载的下一代云架构 |

## 能力边界

- Cloudflare 平台绑定较深，迁移成本高
- Sandbox 性能受 Cloudflare 边缘节点限制
- 仍在早期阶段，生产稳定性需验证
- Agent Readiness Score 是 Cloudflare 自家标准，非行业共识

## 最佳实践

1. Agent 需要三种计算环境：全 OS（Sandbox）、轻量隔离（Worker）、持久状态（Durable Object）
2. 安全必须是默认选项，不是可选配置
3. Agent 生成的代码需要版本化管理和 Git 兼容
4. Agentic Web 需要新的压缩和缓存策略

## 🔍 借鉴学习进化点（必填）

| # | 点 | 原文要点 | 对当前系统的借鉴 | 行动计划 |
|---|-----|---------|---------------|---------|
| 1 | Agent持久环境 | Sandbox 给 Agent 一台"真正的电脑"，持久化+隔离 | Hermes 的 subagent 可借鉴此模式，为每个 coding agent 提供隔离 workspace | 在 claude-code/codex skill 中增加 workspace 隔离机制 |
| 2 | Agent Readiness | 检测网站是否适配 Agent 访问 | Hermes 的 gateway 可增加"Agent Friendliness Score"检测 | 在 gateway 健康检查中增加 Agent 可访问性维度 |
| 3 | 三层计算模型 | 全OS + 轻量隔离 + 持久状态 | Hermes 可根据任务复杂度自动选择执行环境 | 在 task-executor skill 中增加环境适配逻辑 |
| 4 | Artifacts版本化 | Git 兼容存储，Agent 生成代码有版本管理 | Hermes 的 skill 和 memory 系统都应 Git 化 | 推进 skill-curator-review 中的版本管理实践 |

## 🔗 RAG / Wiki 联动（必填）

### 当前状态
- 与之前的 Agent 相关笔记（Agent 记忆污染、Superset IDE）形成 Agent 基础设施专题
- wiki-knowledge-base 可用于索引 Agent 基础设施知识

### 改进方案
1. 创建 "Agent 基础设施" 专题，关联 Cloudflare、Anthropic、Agent 安全等笔记
2. 将 Agent Readiness 概念融入 Hermes 的 self-healing-gateway

### 已执行操作
- ✅ 笔记生成完成
- ⏳ 专题索引待创建


## 相关笔记
