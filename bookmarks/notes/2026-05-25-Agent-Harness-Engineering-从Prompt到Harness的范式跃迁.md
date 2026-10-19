# Agent Harness Engineering：从 Prompt 到 Harness 的范式跃迁

> **来源**：Phil Schmid Blog · LangChain Blog · HN #46641362 · Anthropic Report
> **原文**：https://www.philschmid.de/agent-harness-2026
> **笔记ID**：sniff-20260525-agent-harness-engineering
> **格式**：双格式(MD + HTML) · 含借鉴进化点 · RAG/wiki联动

## 摘要

2026 年 AI Agent 开发的核心范式已从"Prompt Engineering"进化到"Harness Engineering"。Agent Harness 是包裹在 AI 模型外部的基础设施层，负责管理长时间运行任务、上下文工程、工具调用生命周期和可靠性保障。Phil Schmid 将其类比为"操作系统"：模型是 CPU，上下文窗口是 RAM，Harness 是 OS，Agent 是应用。这一范式直接解释了为什么同一个模型在不同 Harness 中表现差异巨大——Claude Code、Codex CLI、Aider 的差异主要来自 Harness 而非模型本身。

## 核心内容

### 1. 什么是 Agent Harness

  定义：包裹 AI 模型、管理长时运行任务的基础设施系统
  不是 Agent 本身，而是 Agent 运行的"操作系统"
  高于 Agent 框架：框架提供构建块，Harness 提供完整的运行环境
  核心组件：提示预设、工具调用处理、生命周期钩子、规划能力、文件系统访问、子 Agent 管理

### 2. 经典类比：计算机体系

  模型 = CPU：提供原始处理能力
  上下文窗口 = RAM：有限的易失性工作记忆
  Agent Harness = 操作系统：管理上下文、处理"启动"序列、提供标准驱动
  Agent = 应用程序：运行在 OS 之上的具体用户逻辑

### 3. 为什么 Benchmark 不够了

  传统 Benchmark 只测单轮输出，无法反映多步可靠性
  模型在 50-100 步工具调用后可能出现"指令漂移"
  Leaderboard 上 1% 的差异无法检测长时间运行后的可靠性退化
  SWE-bench 等新型 Benchmark 也难以测量"耐久性"

### 4. Harness 的三大价值

  验证真实世界进展：在统一 Harness 中对比不同模型的真实表现
  赋能用户体验：发布 Harness 让开发者基于最佳实践构建
  爬山式改进：共享稳定环境创建反馈循环，让研究者可以迭代改进

### 5. Bitter Lesson 在 Agent 领域重演

  Manus 6 个月内重构 Harness 5 次，移除刚性假设
  LangChain 重构 Open Deep Research 架构
  通用方法（利用计算资源）持续击败人工编码的规则
  关键洞察：Agent 的质量上限由 Harness 设计决定，而非模型能力

### 6. Harness Engineering 的具体实践

  上下文压缩：减少上下文窗口占用，防止"遗忘"
  状态卸载：将中间状态存入外部存储
  任务隔离：拆分子 Agent 处理独立子任务
  多模型编排：大模型规划，小模型执行
  验证门控：每步执行后自动验证，不合格则回退

## 关键概念

  **Harness Engineering**：2026 年新兴工程领域，专注于设计和管理 AI Agent 的运行时基础设施。区别于 Prompt Engineering（优化输入）和 Context Engineering（优化上下文），Harness Engineering 关注整个系统的可靠性。

  **指令漂移（Instruction Drift）**：模型在长时间多步执行后，逐渐偏离初始指令的现象。这是当前 AI Agent 面临的最大可靠性挑战。

  **爬山式改进（Hill Climbing）**：通过结构化反馈循环，逐步优化系统性能的方法。Harness 将模糊的多步工作流转化为可记录、可评分的结构化数据。

  **验证器定律（Verifier's Law）**：验证比生成容易。利用这一不对称性，构建验证驱动的工作流可以显著提高 Agent 输出质量。

## 能力边界

  Harness Engineering 尚处早期，最佳实践仍在快速演变
  当前通用 Harness 稀少（Claude Code、LangChain DeepAgents 是少数例子）
  过度工程化风险：简单的 Harness 可能比复杂的更可靠
  文中类比（CPU/RAM/OS）是简化模型，实际边界更模糊

## 最佳实践

  1. 先用最简 Harness 跑通，再逐步增加复杂度
  2. 将验证逻辑与执行逻辑分离，利用"验证比生成容易"的不对称性
  3. 记录每步执行结果，建立可追溯的反馈循环
  4. 多模型编排：规划用强模型，执行用快模型
  5. 定期"断路测试"：模拟第 50/100 步时的指令遵循情况

## 🔍 借鉴学习进化点（必填）

| # | 点 | 原文要点 | 对当前系统的借鉴 | 行动计划 |
|---|-----|---------|---------------|---------|
| 1 | Harness 即 OS | "Harness 是 Agent 的操作系统" | Hermes 本质上就是一个 Agent Harness（技能系统、cron 管理、记忆系统都是 OS 层组件） | 将 Hermes 重新定位为"Agent Harness OS"，在文档中明确这一类比 |
| 2 | 上下文压缩 | "通过压缩减少上下文窗口占用" | 当前 context-compressor skill 正在做这件事，需要持续优化 | 在长任务中自动触发 context-compressor，而非等手动调用 |
| 3 | 验证器定律 | "验证比生成容易，构建验证驱动工作流" | sniff 笔记生成后缺少自动验证环节 | 引入笔记质量自动评分（信息密度、结构完整性、借鉴点数量） |
| 4 | 多模型编排 | "大模型规划，小模型执行" | 当前 cron 任务用 glm-5.1 执行简单任务就是好的实践 | 扩展为：复杂分析用强模型，cron 常规任务用轻量模型，进一步降低成本 |
| 5 | Bitter Lesson | "通用方法持续击败人工编码规则" | Hermes 的 skill 系统不应过度规定死流程，保持灵活性 | 审查 skill 中的刚性规则，适当放松为"建议"而非"强制" |

## 🔗 RAG / Wiki 联动（必填）

### 当前状态
- wiki-kb: 有 Claude Code 笔记、Agent 相关笔记
- RAG: 可通过 "Agent Harness" "上下文工程" "可靠性" 检索
- Memory: Hermes 本身就是 Harness 实践

### 改进方案
1. 将 Hermes 定位为"开源 Agent Harness OS"，在 MEMORY.md 中明确记录
2. 建立"Harness 设计模式"知识库，收集和分类各种 Harness 模式
3. 在 wiki 中创建 "Agent Harness vs Agent Framework" 对比页

### 已执行操作
- ✅ 笔记已生成双格式
- ⏳ Harness 设计模式知识库待创建
- ⏳ Hermes 定位更新待执行

## 关联
- [Claude Code 之父 Boris Cherny 编程已死](2026-05-25-Claude-Code之父Boris-Cherny-编程已死千级Agent夜间打工.md)
- [Cloudflare Agents Week 2026](2026-05-24-Cloudflare-Agents-Week-2026-Agentic-Cloud全栈基础设施.md)
- [150个任务30个Skill实测](2026-05-23-150个任务30个Skill实测-7个反直觉结论.md)

## 相关笔记

<!-- 使用 @note 链接相关笔记 -->
