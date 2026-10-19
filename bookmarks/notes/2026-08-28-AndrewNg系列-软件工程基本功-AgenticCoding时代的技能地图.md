---
title: AndrewNg系列-软件工程基本功-AgenticCoding时代的技能地图
date: 2026-08-28
source: https://x.com/AndrewYNg/status/2093388974194872781
author: Andrew Ng (吴恩达)
tags: [AndrewNg, AgenticCoding, 软件工程, AI工程技能图谱, 系列笔记]
theme: engineering
series: AI Engineering Skills Map 系列
series_index: 2
prev: 2026-08-15-AndrewNg-AI工程技能图谱.md
---

# Andrew Ng：软件工程基本功 — Agentic Coding 时代的技能地图（系列第 2 篇）

> **来源**：https://x.com/AndrewYNg/status/2093388974194872781（2026-08-28 17:23，130.3K 阅读）
> **系列**：[AI 工程技能图谱总纲（08-15）](./2026-08-15-AndrewNg-AI工程技能图谱.md) 的技能二展开专篇
> 一句话核心：**Coding agent 让写代码变便宜了，但没让架构决策变便宜——不懂权衡的人，Agent 会替你做权衡，而你根本不知道。**

## 0. 系列版图（持续维护）

| # | 篇目 | 状态 | 笔记 |
|---|------|------|------|
| 0 | 总纲：AI Engineering Skills Map（四技能概览） | ✅ 已笔记 08-15 | [总纲](./2026-08-15-AndrewNg-AI工程技能图谱.md) |
| 1 | 技能一：构建与部署 AI 应用 | 待发 | - |
| 2 | **技能二：软件工程基本功（本篇）** | ✅ 本文 | - |
| 3 | 技能三：用好编码 Agent | 待发 | - |
| 4 | 技能四：塑造构建方向 | 待发 | - |

## 1. 核心命题：为什么 vibe coding 会翻车

原文开篇立论（照录因果链）：

> A novice who vibe codes without understanding software fundamentals can create simple applications, but this often leads to the coding agent making bad tradeoffs in **latency, availability, consistency, reliability, maintainability, simplicity, and/or cost**. In such cases, the developer didn't know such tradeoffs even existed and therefore did not steer the agent to make the right decisions for their application context.

拆解：
- 新手 vibe coding **能**做出简单应用（这是 agent 时代的真实赋能）
- 但 agent 会在七个维度上替你做权衡：**延迟 / 可用性 / 一致性 / 可靠性 / 可维护性 / 简洁性 / 成本**
- 翻车的根因不是 agent 笨，而是**开发者根本不知道这些权衡存在** → 无从引导（steer）
- 结论：软件基本功的价值从"会写"转移到了"**知道要什么、并能用精确语言告诉 agent**"

另一层：AI 应用的核心往往包裹在一个更大的软件应用里——你仍然要参与构建或塑造这个外壳。

## 2. 五大能力域（原文骨架）

吴恩达团队从 AI Engineering Skills 研究中提炼的软件工程最重要五件事：

```
① Building full-stack applications   构建全栈应用
② Managing data                      管理数据
③ Designing system architectures     设计系统架构
④ Making systems secure & reliable   让系统安全可靠
⑤ Scaling & operating in production  规模化与生产运维
```

### 2.1 构建全栈应用（Building full-stack applications）

- **角色泛化**：agentic coding 让原本专精一域的开发者（前端/移动端）可以承担更宽的全栈角色；agent 补你生疏的部分
- **但要懂全栈怎么真正运作**，关键组件与概念清单（照录）：
  - UI 组件 / 缓存 / 页面渲染
  - **API 选型与设计**
  - 认证（authentication）
  - **状态与会话管理**
  - 异步处理 / 数据持久化
  - 测试 / 安全 / **无障碍（accessibility）**

### 2.2 管理数据（Managing data）——本篇着墨最重

**为什么数据特殊**：数据是软件建于其上的地基，且**相对难改**（即使 agent 能帮忙做迁移）。

懂管理数据意味着（照录要点）：

| 能力 | 具体内容 |
|------|---------|
| 访问模式思维 | 从访问模式反推**存什么、存多久** |
| 数据建模 | 识别正确的数据模型；选对存储类型（**关系表 / 文档 / 键值 / 图**）与基础设施——直接影响速度、扩展性、可用性、可靠性、成本 |
| 事务与并发 | 理解 transactions、concurrency |
| 数据质量 | 保证数据**干净、一致、新鲜（fresh）** |
| 合规 | 按需保证隐私、治理、合规 |
| 生命周期 | 管理数据全生命周期 |
| 演进 | 随应用演进**演进数据架构** |

**最有洞察的一段**（照录）：

> Your AI systems will get their own input context from your data source, so **if data architecture is chosen poorly, the AI doesn't know what it doesn't know**. This is why it takes skilled intervention from someone with the relevant context and skilled at AI engineering — you! — to set it right.

- 数据架构选错 → AI 的输入上下文就错 → **AI 不知道自己不知道什么**（unknown unknowns）
- 修正它需要"懂业务语境 + 懂 AI 工程"的人的介入——这就是你的价值
- 前沿方向：**为 agent 而非只为人类/传统软件构建数据基础设施**，最佳实践仍在快速演进，需持续调整

### 2.3 设计系统架构（Designing system architectures）

前提：先懂全栈各组件（2.1）和数据（2.2），才有资格谈"怎么组装"。

好的系统设计要求先理解软件要干什么（照录反问清单）：
- 多少用户？
- 延迟多重要？
- 成本多重要？

然后才能决策（照录决策清单）：
- 应用平台选型
- **前后端边界**（boundary between frontend and backend）
- 系统分解（decomposition）
- 应用状态摆放（application state placement）
- **架构粒度：单体 vs 微服务**（monolith vs. microservices）
- 技术栈选择（语言 / 运行时 / 前后端框架 / 数据技术）——有时要**先跑实验评估再定**

**架构是移动靶**（照录）：

> The simple architecture you choose to build a quick prototype may not be the right architecture to build the first production system, and that too may change as the application scales.

原型架构 ≠ 首个生产系统架构 ≠ 规模化后的架构。做这些决策需要"软件组件 + 应用语境"的双重深度知识，才能**设计和演进**架构。

### 2.4 让系统安全可靠（Making systems secure and reliable）

**测试策略**：
- 单元测试 vs 集成测试的配比
- 框架选择、覆盖率达到什么水平

**面向失败设计**（照录）：
- 处理失败（如 API 撞 rate limit 怎么办）
- 内建**优雅降级**（graceful degradation）
- **最小化故障爆炸半径**（minimize the blast radius）

**安全左移（shift left）**：
- 不是先写完软件再考虑安全，而是把安全工作移到生命周期更早处（传统时间线的"左边"）
- 趋势判断（照录）：正如所有开发者都在变成全栈，**很多开发者现在也部分是安全工程师**
- AI 工具链：扫代码漏洞 / 查依赖供应链注入 / 查云配置攻击面——**但用好这些工具仍然需要安全知识**

### 2.5 规模化与生产运维（Scaling and operating in production）

**SDLC 全流程**：配置部署环境 → 发布策略 → 部署自动化（CI/CD）→ 理解 IaaS。

**生产运维三件套**：可观测性工具 / 告警 / 事件管理（incident management）。

**扩展能力**（照录）：
- 理解真实负载
- 扩容服务器 / 负载均衡
- 数据基础设施适配：**分片（sharding）/ 索引（indexing）/ 复制（replication）**
- 必要时改架构让系统适应规模

**长期演进的最佳实践**：版本控制 / 代码评审 / 依赖维护 / **技术债管理**。

## 3. 收束：什么在贬值，什么在升值

原文结尾（照录+拆解）：

> Coding agents have changed how we build software, including software that does not contain any AI components. Some parts of coding knowledge — **like memorizing coding syntax** — are becoming obsolete. But **developers who deeply understand how software works vastly outperform those who vibe code without understanding**.

| 贬值中 | 升值中 |
|--------|--------|
| 语法记忆 | 权衡识别（七维度） |
| 手写样板代码 | 架构设计与演进 |
| 专精单域 | 全栈理解 |
| 先写后安全 | 安全左移 |
| "能跑就行" | 评测+失败设计+爆炸半径思维 |

- Coding agent 改变的是**所有**软件的构建方式（包括不含 AI 组件的软件）
- 懂软件原理的人**大幅跑赢**纯 vibe coder
- 软件基本功（叠加 AI 知识）还帮你判断**软件能做什么、不能做什么**——这是驾驭 coding agent 的重要上下文
- 系列预告：后续将展开讨论

## 4. 高赞回复精选（社区共识取样）

| 作者 | 观点 |
|------|------|
| @Ferbin08 | **Agents make testing more important, not less.** 旧的 bug 是"代码能不能跑"，新的 bug 是"它有没有悄悄做错事"（quietly do the wrong thing） |
| @R_umeshmaurya | Agents 让写代码变便宜了，但**没让架构变便宜**。不懂延迟/可靠性/成本/数据的权衡，agent 依然会替你做这些决策——只是你意识不到 |
| @GonnabeNikhil | 权衡（tradeoffs）那部分最重要。coding agent 降低的是实现成本，没取消延迟/一致性/可靠性/成本/安全/可维护性的决策 |

三条高赞全部聚焦同一命题：**agent 转移了工作重心，没有取消工程判断**。与本机 Eval 笔记（没有 Eval 你只有"感觉变好了"）构成同一论述的两面。

## 5. 本机对照（延伸分析，原文之外）

> 笔记惯例：仅列可直接借力的落点，不做过度映射。

| 原文概念 | 本机对应物 | 增量行动 |
|---------|-----------|---------|
| 七维权衡（latency/cost/...） | Hermes gateway 选型时的模型路由（免费链/付费链） | 已隐式执行；可在 config 变更时显式写权衡理由 |
| 数据架构："AI 不知道自己不知道" | RAG 索引质量决定回答上限（`rag-index-rebuild`） | 同构：索引差 = AI 的 unknown unknowns，已实践 |
| 安全左移 | `auto-defense-check`、skill-vetter 前置 | 已落地 |
| 爆炸半径最小化 | cron 失败隔离、deliver=local 静默采集 | 已落地（08-28 股票推送改造） |
| 测试策略（单测/集测配比） | `cron-output-verifier.py` 属集成层校验；skill 层缺单测 | 可补：新 skill 附 1 个冒烟脚本 |
| 技术债管理 | `skill-health-tier` 三级分类（skeleton=债） | 已落地（08-28） |

与昨天 Eval 笔记的关系：**Eval 回答"AI 输出好不好"，本文回答"AI 外壳的软件好不好"**——吴恩达技能一（evals 是心脏）与技能二（软件基本功）在 AI 应用里正好互补。

## 6. 出处

| 类型 | 链接/说明 |
|------|----------|
| 原帖 | https://x.com/AndrewYNg/status/2093388974194872781（2026-08-28 17:23，130.3K views） |
| 配图 | AI Engineering Skills Map: Software engineering fundamentals（HQ0yTnbaoAAuJH3.jpg） |
| 系列总纲 | [2026-08-15-AndrewNg-AI工程技能图谱](./2026-08-15-AndrewNg-AI工程技能图谱.md)（status/2088302050706686198，10,000+ 招聘启事研究） |
| 关联笔记 | [什么是Eval-为什么它决定了AI项目能不能真正落地](./2026-08-28-什么是Eval-为什么它决定了AI项目能不能真正落地.md)（同日，技能一的实操面） |

**忠实性说明**：第 1-3 节为原文忠实还原（含照录段）；第 4 节为原帖下高赞回复摘录；第 0 节系列版图与第 5 节本机对照为笔记增补。


## 相关笔记

- [AndrewNg-AI工程技能图谱](./2026-08-15-AndrewNg-AI工程技能图谱.md) — 系列上篇，AI 工程技能全景图
- [什么是Eval-为什么它决定了AI项目能不能真正落地](./2026-08-28-什么是Eval-为什么它决定了AI项目能不能真正落地.md) — 同日姊妹篇，技能一的实操面