# Nobody knows how to build with AI yet：AI 编程的范式迷雾

> **来源**：Hacker News · Andrej Karpathy · 2026 年讨论
> **原文**：https://news.ycombinator.com/item?id=44616479
> **笔记ID**：sniff-20260602-build-with-ai
> **格式**：双格式(MD + HTML) · 含借鉴进化点 · RAG/wiki联动

## 摘要

Hacker News 上关于"Nobody knows how to build with AI yet"的讨论揭示了一个核心困境：尽管 AI 编程工具（如 Claude Code、Codex、Copilot）已经普及，但业界仍然缺乏系统性的方法来构建可靠的生产级软件。Andrej Karpathy 的观点进一步指出，AI 正在改变软件开发的本质——从"编写代码"转向"验证 AI 生成的代码"。这种范式转变意味着传统的软件工程方法可能不再适用，我们需要新的方法论来应对 AI 时代的开发挑战。

## 核心内容

### 讨论的核心观点

**theferret 的观点**：
> "I feel like we've been here before... there was a time when if you're going to be an engineer, you needed to know core equations, take a lot of derivatives, perform mathematical analysis on paper..."

类比历史：
- 过去工程师需要掌握核心方程、微积分、纸上推导
- 现在 AI 编程工具让"写代码"变得容易，但"理解代码"变得困难
- 我们可能正在经历类似的范式转变

**scorpioxy 的观点**：
> "My feelings exactly."

确认了普遍存在的困惑：AI 编程工具的普及并没有解决"如何构建可靠软件"的根本问题。

### Andrej Karpathy 的演变

从 Karpathy 的多个观点可以看出他的思考演变：

**早期观点（Software 2.0）**：
- 神经网络是新的编程范式
- 传统代码将被神经网络权重取代
- 但硬件约束限制了这种转变的适用范围

**中期观点（AI 编程辅助）**：
- AI 适合"throwaway weekend projects"
- 对于生产级项目，仍然需要"close and careful human supervision"
- AI 生成的代码需要人工仔细审查

**近期观点（2026 年）**：
- 停止用 AI 生成"raw code"
- 转向用 AI 构建"Second Brain"（知识组织系统）
- 将 AI 用于"idea file"架构设计，让 AI 代理构建系统

### 关键洞察

1. **AI 编程不是"写代码"，而是"验证代码"**
   - 传统：工程师编写代码 → 测试 → 部署
   - AI 时代：工程师描述需求 → AI 生成代码 → 工程师验证 → 部署

2. **AI 加速了"生产"，但可能空心化了"理解"**
   - 代码生成速度大幅提升
   - 但对代码的理解和掌控可能下降
   - 长期可能导致"代码素养"退化

3. **范式转变需要新方法论**
   - 传统的 TDD、Code Review、CI/CD 可能需要调整
   - 需要新的"AI 辅助开发"最佳实践
   - 需要重新定义"工程师"的角色

## 对比/框架

| 维度 | 传统开发 | AI 辅助开发 | 范式转变 |
|------|---------|------------|---------|
| 核心技能 | 编写代码 | 验证代码 | 从创造到审查 |
| 生产力 | 受限于人力 | 受限于验证能力 | 瓶颈转移 |
| 代码质量 | 依赖工程师水平 | 依赖 AI 模型 + 验证 | 双重依赖 |
| 学习曲线 | 学习语言/框架 | 学习提示/验证 | 技能重构 |
| 团队协作 | 代码审查 | AI 生成 + 人工审查 | 流程调整 |

## 关键概念

**Software 2.0**：Andrej Karpathy 提出的概念，指用神经网络权重替代传统代码的编程范式。但在硬件约束下，适用范围有限。

**AI 辅助编程（AI-Assisted Programming）**：使用 AI 工具生成代码片段或完整功能，工程师负责验证和集成。

**Second Brain**：用 AI 组织和管理知识，构建个人知识库和思维框架，而非直接生成代码。

**Vibe Coding**：依赖 AI 生成代码，工程师主要进行"感觉式"验证，而非深度理解。

## 能力边界

- 本文讨论的是软件开发的范式转变，不涉及具体的 AI 模型能力
- 假设 AI 模型能力持续进化，但人类验证能力是瓶颈
- 不同领域的适用性不同：简单项目受益更多，复杂系统仍需深度理解

## 最佳实践

1. **明确 AI 的边界**：知道 AI 擅长什么，不擅长什么
2. **重视验证而非生成**：将精力放在验证 AI 生成的代码上
3. **保持代码素养**：即使使用 AI，也要保持对代码的深刻理解
4. **建立新的审查流程**：调整 Code Review 流程以适应 AI 生成代码
5. **从"写代码"转向"设计系统"**：用 AI 辅助架构设计和知识管理

## 🔍 借鉴学习进化点

| # | 点 | 原文要点 | 对当前系统的借鉴 | 行动计划 |
|---|-----|---------|---------------|---------|
| 1 | 验证比生成重要 | AI 时代核心技能是验证代码 | 需要建立 AI 代码验证流程 | 在 hermes-code-mod skill 中增加 AI 生成代码验证步骤 |
| 2 | 保持代码素养 | 不能空心化对代码的理解 | 需要定期人工代码审查 | 在 hermes-code-mod 中强制人工审查环节 |
| 3 | 从写代码到设计 | 转向用 AI 构建 Second Brain | 需要优化知识管理流程 | 在 reading-notes skill 中增加 AI 辅助知识组织 |
| 4 | 新的审查流程 | 传统 Code Review 需要调整 | 需要 AI 辅助的代码审查 | 在 hermes-code-mod 中增加 AI 辅助审查模式 |
| 5 | 明确 AI 边界 | 知道 AI 擅长和不擅长什么 | 需要明确任务分配原则 | 在 SOUL.md 中增加 AI 任务分配指南 |

## 🔗 RAG / Wiki 联动

### 当前状态
- wiki-kb：已建立开发方法论知识库
- RAG：支持语义检索，但缺乏 AI 编程最佳实践
- Memory：包含系统配置信息，但缺乏 AI 开发经验

### 改进方案
1. 建立 AI 编程最佳实践索引
2. 增加"验证优先"原则的定义和案例
3. 在 RAG 中增加 AI 辅助开发的范式转变分析

### 已执行操作
- ✅ 创建本文笔记
- ⏳ 更新 wiki-kb AI 开发索引
- ⏳ 增加"验证优先"概念定义到 RAG

## 相关笔记
- [[2026-05-31-领域专长才是真正的护城河-AI时代的价值反转]] (相关度: 6)
- [[2026-05-28-George-Hotz-警告-Coding-Agents-是昂贵错误]] (相关度: 5)
- [[2026-05-28-AI-Coding-Agents-GitHub-蔓延-开发范式被改写]] (相关度: 5)
