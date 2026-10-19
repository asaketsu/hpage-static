# 10 万行 Rust + AI 开发实战：Code Contracts、Spec-Driven 与极致性能优化

> **来源**：Cheng Huang · 个人博客 · 2025-12-01
> **原文**：https://zfhuang99.github.io/rust/claude%20code/codex/contracts/spec-driven%20development/2025/12/01/rust-with-ai.html
> **评分**：⭐5/5
> **标签**：#AI编程 #Rust #CodeContracts #SpecDriven #性能优化 #Paxos #分布式系统

## 摘要

作者用 3 个月时间，借助 AI 编程代理（Claude Code + Codex CLI 为主力），从零构建了一个 Rust 实现的多 Paxos 共识引擎，复现 Azure RSL 全部功能并现代化。4 周写 10 万行代码，3 周将吞吐从 23K ops/sec 优化到 300K ops/sec。文章系统性地分享了三大关键技术：AI 驱动的 Code Contracts、轻量级 Spec-Driven Development、以及 AI 协助的性能工程闭环。

## 核心内容

### 1. 项目背景：为什么重写 Azure RSL

Azure 的 Replicated State Library (RSL) 实现了多 Paxos 协议，支撑 Azure 大部分核心服务。但 RSL 超过十年历史，存在三大缺陷：

  无流水线：投票进行中新请求必须等待，延迟膨胀
  无 NVM 支持：非易失内存已普及但 RSL 未利用
  硬件感知不足：未利用 Azure 数据中心普遍部署的 RDMA

### 2. AI 生产力飞跃

  6 周完成 13 万行 Rust 代码，覆盖多 Paxos、leader 选举、日志复制、快照、配置变更
  主力工具：Claude Code（命令行异步工作流） + Codex CLI（分担速率限制）
  心理技巧：$100/月订阅费成为"不做就亏"的强迫函数

### 3. Code Contracts —— AI 写、AI 验

三层防御体系：

  第一层：AI 编写前置条件、后置条件和不变量（GPT-5 High 写的合约质量最高）
  第二层：从合约自动生成针对性测试用例
  第三层：将合约转化为 Property-Based 测试，随机探索输入空间

  实战成果：process_2a 方法有 16 个合约；一个 AI 生成的合约发现了 Paxos 安全性违规，避免了一次严重的复制一致性问题

### 4. 轻量级 Spec-Driven Development

作者从严格 SDD（需求→设计→任务列表）转向更灵活的流程：

  /specify 生成用户故事 + 验收标准
  /clarify 让 AI 自我批评并改进规格
  单个用户故事作为 AI 编码代理的"甜蜜点"工作单元

### 5. 性能优化闭环（23K → 300K）

  反复循环：AI 埋点 → 运行性能测试 → AI 分析瓶颈 → 提出优化 → 重测
  关键发现：锁竞争、冗余内存拷贝、不必要的 task spawn
  Rust 的安全模型让激进的零拷贝和去 async 优化更有信心

## 关键概念

  Code Contracts：前置条件、后置条件、不变量的运行时断言（测试启用、生产禁用）
  Spec-Driven Development（SDD）：从形式化规格推导代码，AI 时代可轻量化
  Property-Based Testing：基于属性的随机测试，从合约自动生成海量测试输入
  Multi-Paxos：分布式共识协议，Azure RSL 的核心实现

## 能力边界

  AI 编写合约的质量依赖模型能力，GPT-5 High > Opus 4.1
  性能优化闭环需要人类判断优先级，AI 不能自主决定优化方向
  单用户故事作为工作单元适合当前 AI 上下文窗口限制，但不适合超大型重构

## 最佳实践

  CLI 异步工作流比 IDE 集成更高效（Claude Code 命令行模式）
  多订阅分担速率限制（一个周一周三，一个周四周六）
  合约优先于测试：合约是测试的"元信息"，指导 AI 生成更精准的测试
  性能优化从度量开始，AI 写分析脚本比人类手写更快

## 🔍 借鉴学习进化点

| # | 点 | 原文要点 | 对当前系统的借鉴 | 行动计划 |
|---|---|---------|---------------|---------|
| 1 | Code Contracts 模式 | AI 写合约→从合约生成测试→Property-Based 验证 | 为 Hermes Skill 系统引入合约概念 | 设计 skill-contracts 规范，为关键 skill 定义前置/后置条件 |
| 2 | 性能优化闭环 | AI 埋点→测试→分析瓶颈→优化→重测的迭代循环 | Agent 任务执行后自动度量并优化 | 在 task-executor skill 中加入性能度量和迭代改进循环 |
| 3 | 轻量 Spec-Driven | /specify → /clarify → 单用户故事编码 | 用 spec 驱动 skill 和工具开发 | 在 plan skill 中引入 specify + clarify 两步法 |
| 4 | CLI 异步工作流 | 命令行模式让 AI 和人类异步协作效率最高 | Hermes 的 cron 任务本质就是 CLI 异步 | 优化 cron 输出格式，便于人类异步审阅 |
| 5 | 多工具分担限制 | 双订阅分流速率限制 | 搜索/生图等工具降级链已实现 | 强化 simple-image-gen 的多通道降级逻辑 |

## 🔗 RAG / Wiki 联动

### 当前状态
- 已有 agent-search-edit skill 实现精准搜索编辑
- 已有 verification-gate skill 实现三级验证
- 缺少"合约"概念的系统性实现

### 改进方案
1. 为 skill 系统引入 contracts 字段（前置条件 + 后置条件）
2. 在 evolver 闭环中加入合约验证环节

### 已执行操作
- ✅ 笔记已写入
- ⏳ 待评估 skill-contracts 规范的可行性


## 相关笔记
- [[2026-04-09-SKILL-md-ai-agent-skills.md|SKILL.md 模式：如何写出真正能用的 AI 智能体技能]]
- [[2026-04-13-4-ai-agent-frameworks-comparison.md|4大AI智能体框架对比：Hermes、OpenClaw、LangChain、OpenAI Agent SDK]]
- [[2026-04-26-数字孪生低代码平台项目方案.md|数字孪生低代码可视化平台 — 独立项目方案]]
- [[2026-05-08-企业AI转型三步法-知识库技能化智能体.md|企业 AI 转型三步法：知识库 → 技能化 → 智能体]]
- [[2026-05-16-OpenHuman-记忆树AI智能体-i龙虾.md|OpenHuman — 通过记忆树记住你全部的AI智能体]]
- [微软推出专属编程模型 MAI-Code-1-Flash](2026-06-03-mai-code-1-flash.md)
