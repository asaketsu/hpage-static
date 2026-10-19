# Loop Engineering vs Harness：AI 编程新范式演进

- 📅 2026-06-14
- ⭐ 5/5 — 概念辨析极其清晰，三层递进 + 真实案例 + 刹车机制，可直接对标我方 Hermes 体系
- 🏷️ #AI编程 #LoopEngineering #Harness #Agent架构 #Claude Code
- 🔗 https://mp.weixin.qq.com/s/Dy__4Ivw77bMrgxDsKL6lw

## 摘要

2026 年 6 月 AI 编程圈被一个六个单词的推文引爆：**"不要去 prompt agent，去设计 prompt agent 的 loops"**。Addy Osmani 随即系统化命名为 **Loop Engineering（循环工程）**。文章拆解了三层概念递进（Harness → Loop → Goal）、底层动因（单 agent 三大病）、关键设计（writer/judge 分离）、提出者自己的刹车（理解债 + 认知投降），以及落地路径。

---

## 一、引爆事件时间线

| 时间 | 事件 |
|------|------|
| 5/28 | Anthropic 在 Claude Code 上线 Dynamic Workflows，模型能自己写 harness |
| 6/02 | Anthropic 发深度长文《A harness for every task》 |
| 6/07 | Peter Steinberger（OpenClaw/OpenAI）发推引爆 |
| 6/08 | Addy Osmani（Google）发博客正式命名 **Loop Engineering** |

三句关键引用：

> **Steinberger**：你不该再去 prompt 编程 agent 了。你该去设计那些 prompt agent 的循环。

> **Boris Cherny**（Claude Code 负责人）：我已经不 prompt Claude 了。我让一堆 loop 跑着去 prompt Claude。我的工作是写 loop。

> **Osmani**：loop engineering 就是 harness，但它装了个定时器、会派小弟、还会自己喂自己。

---

## 二、三层概念辨析（核心）

| 层级 | 名字 | 是什么 | 谁来停 | 自驱？ |
|------|------|--------|--------|--------|
| 底层 | **Harness** | 模型外面那套系统：拆活、派 sub-agent、给工具、验收 | 脚本跑完 | 否 |
| 触发 | **`/loop`** | 按节奏（cron/interval）重跑一个 prompt | 时间/次数 | 半自驱 |
| 上层 | **`/goal`** | 给完成条件，agent 自己干到条件为真 | 独立验证模型 | 是 |

**一句话**：
- Harness = **怎么干活的骨架**
- Loop = **让骨架自己定时跑、自己喂自己、自己判断该不该停**

> Harness 是静态的一次性编排，Loop 是让 harness 活过来、自己转起来。

---

## 三、Harness 层：为什么需要

### 单长上下文 Agent 的三大病

| 病 | 症状 | 本质 |
|----|------|------|
| **Agentic laziness** | 50 项审查做到第 35 项就宣布"完成了" | 偷懒 |
| **自我偏好偏差** | 写代码的 Agent 给自己代码打分总是手松 | 给自己批作业太仁慈 |
| **目标漂移** | 多轮有损压缩后，"不要做 X" 类约束悄悄丢失 | 失忆 |

**Harness 的解法**：给每个 sub-agent 独立的上下文窗口、聚焦的小目标、以及一个**和它无关的验证者**。

### Dynamic Workflows 运行时限制

- 单次最多 **16 个并发 agent**
- 累计 **1000 个 agent** 上限
- 防止 loop 失控烧钱

### 实锤案例：Bun 移植

Jarred Sumner 将约 **100 万行 Zig** → Rust 逐文件忠实移植：
- 生成 **75 万行 Rust**
- 原测试套件 **99.8% 通过**
- 一个 workflow 算生命周期，另一个 workflow 派几百个并行 agent，每个文件配两个独立 reviewer

---

## 四、Loop 层：六个零件

Osmani 拆解的六个组成部分：

| # | 零件 | 作用 |
|---|------|------|
| 1 | **Automations** | 定时调度（`/loop`、cron、hooks）— loop 之所以是 loop 的关键 |
| 2 | **Worktrees** | git 工作树隔离，多 agent 文件不撞车 |
| 3 | **Skills** | 沉淀项目知识 |
| 4 | **Connectors** | 接上你的工具 |
| 5 | **Sub-agents** | **把"写"和"查"分开** |
| 6 | **State file** | 跨次运行的状态文件 — "agent 每次都会忘，文件不会" |

---

## 五、`/goal`：Loop 理念最纯粹实现

**Claude Code v2.1.139**（5/11 发布）的核心机制：

```
给定完成条件（如 "npm test 退出码 0 且 git status 干净"）
    ↓
agent 一轮一轮干
    ↓
每轮结束后 → 独立小快模型（默认 Haiku）读对话判断条件
    ↓                           ↓
不成立："为什么还没完成"     成立：清除 goal，标记达成
→ 作为提示再来一轮
```

本质：**会话级的、基于 prompt 的 Stop hook**。

> VentureBeat：**"把干活的 agent，和判断它干完没的 agent，分开。"**

⚠️ **真实坑**：
- 验证模型**不能调工具**，只能看 agent 晒出来的东西
- 完成条件必须写成"agent 输出能自证"的形式
- 必须加"或 20 轮后停止"兜底，防 token 烧穿

---

## 六、提出者自己的刹车

### 两个长期风险

| 风险 | 含义 |
|------|------|
| **Comprehension debt（理解债）** | loop 把没写过的代码越铺越快，"仓库里有什么"和"你理解什么"之间鸿沟越来越大 |
| **Cognitive surrender（认知投降）** | "算了别想了，loop 给啥我收啥"的引力 |

### 四个"值得上 loop"条件（缺一赔本）

1. 任务会重复
2. 验证能自动化
3. token 预算扛得住浪费
4. agent 已有资深工程师该有的工具

### 最清醒的一句话

> 设计 loop 只是一半。另一半是往 loop 里塞一个**能说"不行"的东西**：一个测试、一次类型检查、一个真实的报错。

否则你不是在造产品，你是在造一个**用 token 计价的官僚机构**——一边疯狂烧钱一边掩盖偏移。

---

## 七、落地路径（倒过来走）

```
Step 1 → 先把 Harness 搞明白（让 Claude 写 Workflow，看它怎么拆活、怎么互查）
Step 2 → 再上 /goal（完成条件能被输出自证的任务，体会 writer/judge 分离）
Step 3 → 最后才谈 /loop（任务确实重复 + 验证能自动化时，用 worktree + state file）
Step 4 → 永远保留那个会说"不行"的东西（测试/类型检查/真实报错）
```

> **Loop 是新的 prompt。但在你把方向盘交给它之前，先确认你还看得懂仪表盘。**

---

## 💡 启发

- **writer/judge 分离是 Multi-Agent 最核心的设计模式** — 不能让写代码的 agent 给自己打分
- **"agent 每次都会忘，文件不会"** — 状态持久化比 context 记忆更可靠
- **理解债（Comprehension debt）** 是 loop 时代的新型技术债，比代码债更危险
- **"能说不行的东西"** 是 loop 价值的前提——没有验证器的 loop 只是更贵的随机数生成器

## 🔮 预判

- Harness → Loop → Goal 三层递进会成为 AI 编程工具标准架构
- writer/judge 分离将渗透到所有 agent 系统（不只是编程领域）
- "理解债管理"会成为新岗位/新工具类别（监控你和代码库的理解鸿沟）

## 相关笔记
- [Anthropic开源AI漏洞发现框架-Harness](2026-06-05-Anthropic开源AI漏洞发现框架-Defending-Code-Reference-Harness.md) (关键词: Harness, AI编程)
- [OpenClaw autonomy harness loop](2026-04-07-OpenClaw-autonomy-harness-loop.md) (关键词: Harness, loop)
- [生产级Multi-Agent Harness设计](2026-06-14-生产级Multi-Agent-Harness设计全拆解.md) (关键词: Harness, 工程范式)
