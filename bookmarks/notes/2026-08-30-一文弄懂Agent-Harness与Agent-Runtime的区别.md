---
title: 一文弄懂 Agent Harness 与 Agent Runtime 的区别（X Article）
date: 2026-08-30
source: https://x.com/Smartpigai/status/2094035177492164795
author: Smartpig (@Smartpigai)
tags: [Agent架构, Harness, Runtime, LLM工程, 概念辨析]
---

# 一文弄懂 Agent Harness 与 Agent Runtime 的区别（X Article）

> **原文**：[x.com/Smartpigai/status/2094035177492164795](https://x.com/Smartpigai/status/2094035177492164795)（X Article 正文 App/登录独占）
> **作者**：Smartpig（@Smartpigai，蓝V）｜发布 2026-08-30

## 0. 素材获取说明（忠实性边界）

- ✅ **原文数据照录**：标题（封面大字）+ 文内两张概念图的**全部文字逐字提取**（GLM-4.6V 视觉识别，布局关系按图还原）
- ❌ 正文全文被 X 登录墙锁定（syndication/oembed/nitter/Googlebot/playwright 五路实测均无转载）
- ⚠️ §2 概念展开为领域通识补全（非原文），标注明确

## 1. 核心主张（从标题与概念图还原）

Agent 系统里两个高频混用的词——**Harness（驾驭层/驱动程序）** 与 **Runtime（运行时/执行环境）**——职责完全不同：前者"开车"，后者"修路养车"。

### 1.1 概念图一：五层链路总览（原文逐字）

```
用户 → Agent Harness → LLM模型 → Agent Runtime → 工具/系统
```

| 层 | 图中标签 | 职责（据图位推断） |
|----|---------|------------------|
| 用户 | 用户 | 发起目标任务 |
| 驾驭层 | **Agent Harness** | 位于用户与模型之间的驱动程序 |
| 模型 | LLM模型 | 推理决策，产出动作/工具调用 |
| 运行时 | **Agent Runtime** | 位于模型与工具之间的执行环境 |
| 外部 | 工具/系统 | 真实被操作对象（命令、文件、API） |

### 1.2 概念图二：完整调用时序（原文逐字，含箭头语义）

```
用户          Harness（驱动程序）      LLM模型        Runtime（执行环境）    工具/系统
 │                │                     │                 │                  │
 ├─发送请求──────▶│                     │                 │                  │
 │（目标任务）    ├─构造Prompt并调用模型▶│                 │                  │
 │                │◀───────模型返回动作（或工具调用请求）──┤                  │
 │                │         [模型请求工具]               │                  │
 │                ├─将工具调用分派给Runtime──────────────▶│                  │
 │                │                     │                ├─在沙箱执行工具/命令▶│
 │                │                     │                │◀──返回执行结果────┤
 │                │◀────将工具结果返回给Harness──────────┤                  │
 │                │   （返回错误信息或重试特定）           │                  │
 │◀─返回最终结果──┤                     │                 │                  │
```

**时序要点（图中原词）**：
1. 用户「发送请求（目标任务）」
2. Harness「构造Prompt并调用模型」
3. 模型「返回动作（或工具调用请求）」，进入 `[模型请求工具]` 分支
4. Harness「将工具调用分派给Runtime」
5. Runtime「在沙箱执行工具/命令」
6. Runtime「返回执行结果」「将工具结果返回给Harness」
7. 异常路径：「返回错误信息或重试特定」
8. Harness「返回最终结果」给用户

## 2. 概念辨析（领域通识，非原文）

| 维度 | Agent Harness | Agent Runtime |
|------|---------------|---------------|
| 一句话 | **驱动程序**：编排"模型↔工具"循环的框架代码 | **执行环境**：让工具调用安全落地的沙箱 |
| 类比 | 汽车司机+行车电脑（决定何时给油门/刹车） | 发动机+变速箱+安全笼（提供受控动力输出） |
| 核心职责 | Prompt 构造、上下文管理、循环控制（agent loop）、工具注册与分发、结果聚合 | 进程/沙箱隔离、文件系统与网络访问、命令执行、超时与资源限制 |
| 典型失败模式 | Prompt 膨胀、循环失控、上下文溢出、工具选错 | 沙箱逃逸、权限泄漏、命令超时、环境污染 |
| 代表实现 | Claude Code 的 agent loop、OpenClaw/Hermes 的 session-gateway、LangGraph | Docker 容器、Firecracker microVM、E2B、终端沙箱 |

**记忆锚点**：Harness 决定「模型看到什么、下一步做什么」；Runtime 决定「动作在哪个隔离边界内真实发生」。前者是**控制面**，后者是**数据面/执行面**。

## 3. 对照：我们自己的系统

Hermes Agent 本身就是这个分层的教学级案例（对应关系客观存在，非强行映射）：

| 原文概念 | Hermes 中的对应物 |
|---------|------------------|
| Harness（驱动程序） | Gateway 的会话循环：上下文注入（memory/skills）、工具分发、递归 delegation、steer 钩子 |
| 构造Prompt并调用模型 | system prompt 组装（persona + skills 索引 + MEMORY 注入） |
| 将工具调用分派给Runtime | terminal/browser_exec/execute_code 的调度层 |
| Runtime（执行环境） | 本机 Linux 沙箱 + browser-use 独立浏览器会话 + execute_code 受限解释器 |
| 在沙箱执行工具/命令 | 每个 terminal 调用的真实进程执行 + 超时控制 |
| 返回错误信息或重试特定 | 自动重试机制 + error-case-library 沉淀 |

与技能库 [六层 Harness 架构] 的关系：该 skill 讲的是 Harness 内部再分层（六层）；本文讲的是 Harness 与 Runtime 的**边界划分**——两者互补，一个纵向一个横向。

## 4. 价值评估

- **为什么值得记**：中文社区对这两个词的混用极普遍（"Agent 框架"一词同时指代两者）。本文两张图是目前见过的最清晰中文表达——第一张讲静态分层，第二张讲动态时序，且画出了常被忽略的**错误重试路径**
- **局限**：正文未获取，图之外的展开论证（如两者是否必须同进程、Runtime 的弹性伸缩等）未知；§2 为通识补全
- **相关笔记**：[图解大语言模型部署](https://hpage.top/bookmarks/notes/2026-08-29-图解大语言模型部署.html)（LLM 推理侧的姊妹篇：模型如何被服务化）、六层 Harness 架构 skill（内部纵深）

## 出处

- 原推（含 Article 链接）：https://x.com/Smartpigai/status/2094035177492164795
- Article 直链：https://x.com/i/article/2094031229096267776
- 概念图一：https://pbs.twimg.com/media/HQ9-1YIaMAA5G1J.png（逐字提取：用户/Agent Harness/LLM模型/Agent Runtime/工具/系统）
- 概念图二：https://pbs.twimg.com/media/HQ9-mXfbsAAoIiu.png（完整时序，§1.2 逐字还原）
- 封面：https://pbs.twimg.com/media/HQ-By8JawAAF3hW.jpg（经视觉模型确认仅含大标题，无其他文字）
- 提取方法：syndication API 元数据 + pbs 原图 + GLM-4.6V 视觉逐字识别（2026-08-30）

## 相关笔记

- [AI-Agent-IDE 6条多Agent设计原则共识](explore/2026-08-30-AI-Agent-IDE-6条多Agent设计原则共识-增量.md) — 同日姊妹篇，Harness 理念落地到 IDE 多 Agent 协调
- [AI-Agent-IDE Intent-SpecDriven多Agent协调](explore/2026-08-25-AI-Agent-IDE-Intent-SpecDriven多Agent协调.md) — Intent 驱动协调，Runtime 层任务分发的工程对照
- 多Agent编排治理 2026（~/explore 根目录，2026-08-29）— 编排层治理框架，Harness 外围生态视角
