# AI 编码工具战争：Codex/Claude Code/Cursor 收敛为分层架构

> **来源**：The New Stack · 2026-05-19
> **原文**：https://thenewstack.io/ai-coding-tool-stack
> **笔记ID**：sniff-20260524-coding-agent-stack
> **格式**：双格式(MD + HTML) · 含借鉴进化点 · RAG/wiki联动

## 摘要

2026 年 AI 编码工具格局发生根本性变化：OpenAI Codex、Anthropic Claude Code、Cursor 三大工具从竞争走向融合，形成"编排层 + 执行层 + 审核层"的分层架构。这一趋势标志着 AI 编码从单点工具向可组合栈演进，开发者不再需要"选一个工具"，而是可以按需组合不同工具的优势。

## 核心内容

### 1. 三大工具收敛趋势

| 工具 | 定位 | 核心优势 | 收敛角色 |
|------|------|----------|----------|
| OpenAI Codex | 执行层 | GPT-5.5 代码质量提升，多模型路由 | 默认执行引擎 |
| Claude Code | 审核层 | 代码审查、安全分析、架构建议 | 质量把关 |
| Cursor | 编排层 | IDE 集成、上下文管理、多 Agent 调度 | 工作流中枢 |

### 2. 分层架构详解

**编排层（Orchestration）**
- 负责任务分解、上下文管理、多 Agent 调度
- Cursor 作为 IDE 集成中枢，管理整个编码工作流
- 支持 tab/subagent 模式，并行处理多个功能点

**执行层（Execution）**
- 负责实际代码生成、修改、执行
- Codex 凭借 GPT-5.5 在代码质量上领先
- 支持多模型路由，根据任务类型选择最优模型

**审核层（Review）**
- 负责代码审查、安全分析、架构评估
- Claude Code 在安全审查和架构建议上表现突出
- 提供"buffet"式信息输出，辅助决策

### 3. 市场动态

- OpenAI 向 Claude Code 用户提供免费 Codex 访问
- Anthropic 以 50% 增量作为回应
- OpenCode 开源项目 GitHub Star 数超越 Claude Code（160K+ vs 122K+）
- Apple Xcode 集成 Claude Agent 和 Codex 双引擎

## 对比/框架

### 工具选择矩阵

| 场景 | 推荐工具 | 理由 |
|------|----------|------|
| 快速原型 | Codex | 生成速度快，质量稳定 |
| 复杂架构 | Claude Code | 架构建议能力强 |
| IDE 集成 | Cursor | 原生 VS Code 集成 |
| 开源偏好 | OpenCode | 160K+ Star，完全开源 |
| 企业级 | 分层组合 | 编排+执行+审核分离 |

### 2026 年 AI 编码工具排名（MightyBot 4 月评测）

1. **Codex** - GPT-5.5 带来代码质量质变
2. **Claude Code** - 安全审查和架构建议领先
3. **Cursor** - IDE 集成体验最佳
4. **OpenCode** - 开源首选，功能对标 Claude Code
5. **Apple Xcode AI** - 移动端开发新选择

## 关键概念

**可组合 AI 栈（Composable AI Stack）**
指将 AI 工具按功能分层（编排/执行/审核），允许开发者按需组合而非选择单一工具的模式。核心思想是"工具即服务"，每个层可以独立替换或升级。

**Agentic Coding**
指 AI 具备自主执行能力，不仅能生成代码，还能理解上下文、执行命令、修复错误、进行多轮迭代。2026 年是 Agentic Coding 成熟元年。

**Model Routing**
根据任务类型（代码生成/审查/调试）自动选择最优模型的技术。例如：生成用 GPT-5.5，审查用 Claude 3.5，调试用专用模型。

## 能力边界

**当前局限**
- 分层架构仍处于早期阶段，工具间协作需手动配置
- 上下文管理仍是痛点，跨文件理解能力有限
- 审核层工具对复杂架构的评估仍需人工介入
- 开源工具（OpenCode）功能仍在追赶商业工具

**适用场景**
- ✅ 日常编码任务（CRUD、API 开发）
- ✅ 代码审查和安全分析
- ✅ 原型快速搭建
- ⚠️ 复杂系统架构设计（需人工深度参与）
- ⚠️ 遗留系统重构（上下文理解有限）

## 最佳实践

1. **分层使用**：编排层用 Cursor，执行层用 Codex，审核层用 Claude Code
2. **上下文管理**：保持工作区整洁，使用 `.cursorrules` 定义项目规范
3. **多轮迭代**：不要期望 one-shot 完成，接受 AI 需要多轮反馈
4. **安全审查**：所有 AI 生成代码必须经过 Claude Code 或类似工具审查
5. **开源优先**：非敏感项目优先使用 OpenCode 等开源工具

## 🔍 借鉴学习进化点

| # | 点 | 原文要点 | 对当前系统的借鉴 | 行动计划 |
|---|-----|---------|---------------|---------|
| 1 | 分层架构 | 编排/执行/审核三层分离 | Hermes 技能系统可借鉴分层设计 | 评估技能分类为 orchestration/execution/review 三类 |
| 2 | 模型路由 | 根据任务选择最优模型 | 当前 Hermes 单一模型，可引入路由 | 研究 zhipu/glm-5.1 与其他模型路由配置 |
| 3 | 开源竞争 | OpenCode 160K+ Star 超越 Claude Code | 开源工具质量已接近商业级 | 评估 OpenCode 作为 Hermes 编码技能备选 |
| 4 | 上下文管理 | Cursor 通过 `.cursorrules` 管理上下文 | 可借鉴定义 Hermes 项目规范文件 | 创建 `.hermes/rules.md` 定义 Agent 行为准则 |
| 5 | 工具组合 | 不再选单一工具，而是组合使用 | 技能系统可设计为可组合模块 | 设计技能组合模式，如 `skill-compose` |

## 🔗 RAG / Wiki 联动

### 当前状态
- **wiki-kb 状态**：~/uclaw/ 下存在知识库，但 AI 编码工具相关笔记较少
- **RAG 状态**：RAG 索引已重建，但编码工具类内容覆盖不足
- **Memory 状态**：Memory.md 存在，但技能系统分类未明确

### 改进方案
1. 补充 AI 编码工具对比笔记到知识库
2. 更新技能系统分类，增加"编码/开发"类别
3. 创建 `.hermes/rules.md` 定义 Agent 编码行为规范
4. 评估 OpenCode 作为 Hermes 编码技能集成选项

### 已执行操作
- ✅ 生成本笔记（MD + HTML）
- ✅ 更新 index.md
- ⏳ 评估 OpenCode 集成可行性
- ⏳ 创建 `.hermes/rules.md`

## 相关笔记
- [[2026-04-03-Claude-Code四层记忆架构.md]]
- [[2026-04-04-Claude-Code-324-prompts-analysis.md]]
- [[2026-04-02-Agent Skills才是关键抽象层.md]]
- [微软推出专属编程模型 MAI-Code-1-Flash](2026-06-03-mai-code-1-flash.md)
