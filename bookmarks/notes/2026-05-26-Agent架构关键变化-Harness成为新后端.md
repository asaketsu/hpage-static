# Agent 架构关键变化：Harness 正在成为新后端

- 📅 2026-05-26
- ⭐ 4/5 — 前瞻性架构思考，"一切皆 Worker"的类 Unix 哲学在 Agent 时代的回归
- 🏷️ #Agent架构 #Harness #后端 #Worker模式 #iii.dev
- 📰 iii.dev / Mike Piccolo
- 🔗 [原文](https://mp.weixin.qq.com/s/VYZq3CzaQ72-gq1FlzniMw)

## 摘要

Mike Piccolo（iii.dev 创始人）提出：当前 AI 基础设施最大问题不在选哪个模型，而在于 Harness（包裹 Agent 的层）与传统后端分离导致的复杂性爆炸。他提出三大原语（Function + Trigger + Worker）统一后端，让 Agent 也成为 Worker，实现类别坍缩——一切皆 Worker，从队列到 sandbox 到浏览器 tab。

## 核心内容

### 1. 当前 Harness 光谱

| 框架 | Harness 策略 | 核心特征 |
|------|-------------|---------|
| Anthropic | 极薄 | 优雅循环：组装 prompt → 调用模型 → 执行工具 → 重复 |
| OpenAI | 较结构化 | 指令栈、编排模式、显式交接 |
| CrewAI | 多路并行 | 确定性 Flows 处理路由和校验，其余交给自主 Agent |
| LangGraph | 最重 | 每个决策是节点，每次转移是边，工作流编码在 harness |

光谱两端：强烈信任模型+弱编码逻辑 vs 弱信任模型+强编码逻辑。

### 2. 分离架构的核心问题

**调试灾难**：Harness 与后端是两个独立世界，三层各自管理重试/超时，没有一条 trace 能连接分散系统。

**随机性放大**：概率空间 = agents² × services。1 agent + 5 后端 = 5 条路径，4 agents + 5 后端 = 80 条路径。

### 3. 三大原语：Worker + Trigger + Function

- **Function**：带稳定标识符的工作单元（如 `orders::validate`），可用任何语言编写
- **Trigger**：让 function 运行的机制（HTTP/cron/队列/状态变化/流事件），声明式
- **Worker**：连接到 engine 并注册 functions 和 triggers 的进程

**关键转变：Agent 也是 Worker。**

### 4. 三大涌现性质

1. **实时发现**：Worker 连接时收到完整 function 目录，新 functions 出现/消失时实时通知
2. **实时扩展**：添加新 workers 不需要重新部署、重启或配置变更
3. **实时可观测性**：基于 OpenTelemetry，一条 trace 贯穿整条链路，跨 workers/语言/队列

### 5. 递归能力：Agent 创建 Worker

- microVM sandbox 本身也是 worker
- Agent 可运行时启动新 sandbox worker
- Sandbox 注册自己的 functions → 立刻出现在实时目录
- 不可信代码隔离、临时专家 Agent、并行任务执行 → 同一组 primitives，不同模式

### 6. Harness 厚薄之争重新定义

薄与厚不是架构选择，而是同一系统内的模式差异。移除 scaffolding = 简化一个 function，不需要重新架构。

### 7. 无边界 Worker

浏览器 tab 和 Kubernetes pod 地位相同。从云服务到边缘设备到移动端，一切可成为 Worker。

## 🔍 借鉴点

- **Function + Trigger + Worker 三原语** → Hermes 的工具/插件系统可借鉴此抽象，统一 cron、webhook、内置工具为同一原语
- **类别坍缩哲学** → "Everything is a Worker" 类似 Unix "Everything is a file"，简化系统设计
- **实时发现** → Worker 连接时自动获取 function 目录，Agent 不依赖硬编码工具列表
- **OpenTelemetry 贯穿 trace** → 解决 Harness 与后端分离的调试难题
- **Agent 即 Worker** → Agent 不仅能调用工具，还能注册新能力供其他 Agent 使用

## 🔗 关联性

- [[2026-05-26-DeepSeek-Reasonix-成本优化架构解析]] — Reasonix 的并行工具派发与此文的 Worker 模式互补
- [[2026-05-26-MeowBot-L2到L3进化方案]] — Agent 自我进化需要递归能力（Agent 创建 Worker）
- MCP 协议 — iii 的 Worker 注册/发现与 MCP 的工具发现是同类抽象

## 💡 启发

- **Hermes 双机架构（jbot/ubot/abot）本质上就是 Worker 模式**：每台机器是 Worker，通过交换池注册/发现能力。但当前实现是手工配置，iii 的实时发现更优雅
- **Harness 厚薄之争在 Hermes 中的体现**：system prompt 中的 skill 加载 = 薄 harness（模型自主决定），cron job 的固定 prompt = 厚 harness（显式编排）
- **概率空间公式 agents² × services 解释了为什么多 Agent 系统难以规模化**：<25% 成功率不是偶然

## 🔮 预判

- **短期**（3个月）：iii 或类似框架会被更多 Agent 团队采用，Worker 模式成为编排标准
- **中期**（6个月）：MCP + Worker 模式融合，MCP 定义连接协议，Worker 定义运行时原语
- **长期**（1年）："一切皆 Worker"成为 Agent 后端的主流范式，类似微服务对单体架构的替代

## ✅ 落实情况

📋 借鉴点落实审计
├── ① 有利进化 项：2个
│   ├── 项1：harness-architecture skill 补充 iii Worker 模式 → 待评估是否 patch
│   └── 项2：agents²×services 概率空间公式 → 写入 memory（多Agent编排的失败率解释）
├── ② 有价值 项：3个
│   ├── Function+Trigger+Worker 三原语 → memory 写入
│   ├── 类别坍缩哲学 → 仅笔记
│   └── OpenTelemetry 贯穿 trace → 仅笔记
└── ③ 知识库 项：全部 → 仅笔记 ✅


## 相关笔记
- [[2026-04-02-Agent Skills才是关键抽象层.md|别再堆 Tools 了：Agent Skills 才是关键抽象层]]
- [[2026-04-07-OpenClaw-autonomy-harness-loop.md|OpenClaw 自主性与 Harness 循环机制]]
- [[2026-04-28-竞品吸收_OpenCLI.md|竞品吸收笔记：OpenCLI — Universal CLI Hub & AI-Native Runtime]]
