# Loop Engineering：Prompt Engineering 之后的下一个范式

- 📅 2026-06-15
- ⭐ 4/5 — 概念清晰，实操案例可直接复用，适合 Hermes Agent 用户对齐
- 🏷️ #LoopEngineering #Agent #PromptEngineering #MCP #Skills
- 📰 微信公众号
- 🔗 https://mp.weixin.qq.com/s/GQCupbRqdB0TTZ3GVQS4gA

---

## 摘要

Prompt Engineering 正在被 Loop Engineering 取代。核心观点来自 Anthropic 工程师 Boris Cherny（Claude Code 创始人）和 OpenClaw 创始人 Peter Steinberger：**开发者不再手动写 prompt 驱动 Agent，而是设计持续提示、调度和约束 Agent 的循环系统。** Google Cloud AI 总监 Addy Osmani 在 6 月 9 日长文中正式系统化了这一概念，将其拆解为五大组件：定时任务、工作树隔离、Skills、MCP、子 Agent。文章以"文献检索"为实战场景，演示了完整 Loop 的搭建流程。

---

## 一、范式转移：从 Prompt 到 Loop

### 1.1 Prompt Engineering 的瓶颈

> 想让 AI 检索论文，敲一大段 prompt，跑完不满意，再补一段，再跑……改到第五轮开始怀疑——到底是 AI 在干活，还是我们在干活。

核心矛盾：**prompt 很难一次到位指导 AI 达到目标**，人被迫变成了 AI 的实时驾驶者。

### 1.2 行业领袖的转向

| 人物 | 角色 | 核心观点 |
|------|------|---------|
| **Boris Cherny** | Anthropic 工程师，Claude Code 创始人 | "我不再提示 Claude 了，我有一堆循环在运行，它们才是在提示 Claude。我的工作变成了写循环。" |
| **Peter Steinberger** | OpenClaw 创始人 | "你不再需要为 coding agent 写 prompt 了。你应该设计循环来驱动你的 Agent。" |
| **Addy Osmani** | Google Cloud AI 总监 | 6 月 9 日发文正式梳理 Loop Engineering 概念，称其为"未来与编程助手协作的新范式" |

---

## 二、Loop Engineering 五大组件

Addy Osmani 将一个完整 Loop 拆解为五个部分：

### 组件架构图

```
┌─────────────────────────────────────────────────┐
│              Loop System                         │
│                                                  │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐      │
│  │ ① 定时    │  │ ② 工作树  │  │ ③ Skills │      │
│  │  任务     │  │  隔离     │  │  知识继承 │      │
│  │ (心跳)   │  │ (防冲突)  │  │ (记忆)   │      │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘      │
│       │             │             │              │
│  ┌────┴─────────────┴─────────────┴─────┐      │
│  │         ④ MCP (外部世界接入)            │      │
│  │    GitHub / Linear / Slack / DB        │      │
│  └───────────────────┬───────────────────┘      │
│                      │                           │
│  ┌───────────────────┴───────────────────┐      │
│  │    ⑤ 子 Agent (职责分离 + 质量守门)      │      │
│  │    探索 Agent → 实现 Agent → 验证 Agent  │      │
│  └───────────────────────────────────────┘      │
└─────────────────────────────────────────────────┘
```

### 2.1 定时任务 — 心跳

| 维度 | 说明 |
|------|------|
| **作用** | 自动启动循环，去完成既定任务 |
| **行为** | Agent 自动执行；发现问题 → 待处理队列；无问题 → 自动归档 |
| **与 prompt 的本质区别** | 人不再是主动检查者，Agent 自主运转 |

### 2.2 工作树隔离 — 防冲突

| 维度 | 说明 |
|------|------|
| **作用** | 给每个 Agent 独立工作空间，防止文件冲突 |
| **场景** | 同时跑多个 Agent 时，各自独立工作，最后汇总 |
| **不隔离的后果** | Agent 互相覆盖成果，重复劳动 |

### 2.3 Skills — 知识继承

> **核心价值：让 Agent 每次都能继承之前的知识体系。**

- AI 每次新对话从零开始，代码规范/项目架构/历史踩坑全部遗忘
- Skills 将这些知识固化，让 Agent 启动即了解项目
- **在 Loop 中尤其关键**：Loop 自动跑，人不在场，没有固定规范就指导不了 Agent

### 2.4 MCP — 外部世界接入

- 拓展 Agent 超越文件系统的能力
- 连接 GitHub、Linear、Slack、数据库等真实工作环境
- 实现真正的**闭环**：发现问题 → 解决问题 → 通知人类

### 2.5 子 Agent — 职责分离与质量守门

| 要点 | 说明 |
|------|------|
| **为什么需要** | 写代码的 Agent 不能自己给自己打分（AI 有自我偏好偏差） |
| **怎么做** | 用**不同 Agent + 不同模型**检查前一个 Agent 的输出 |
| **人不在场时** | 这个"检查者"是唯一能信任的守门人 |
| **常见分工** | 一个探索，一个实现，一个验证 |

---

## 三、实战：Loop Engineering 用于文献检索

### 五步搭建流程

| 步骤 | 对应组件 | 核心动作 |
|------|---------|---------|
| 第一步 | ① 定时任务 | 每 3 天自动从 arXiv/Scholar/顶会抓取新论文 |
| 第二步 | ② 工作树隔离 | 为每篇论文创建独立 Git Worktree 解析环境 |
| 第三步 | ③ Skills | 加载 SKILL.md 定义学术锚点和提取范式 |
| 第四步 | ④ MCP | 自动写入 Zotero + 飞书通知 |
| 第五步 | ⑤ 子 Agent | Reviewer Agent 做苛刻二次审核 |

### 第一步：定时检索论文

设定每 3 天后台触发，按主题+作者列表从 arXiv / Google Scholar / 顶会接收列表抓取。以公司金融为主题的筛选 prompt 示例：

```markdown
# Role
你是一个精通金融学与人工智能交叉领域的顶级资深审稿人。

# Screening Criteria
1. **重点关注**：资本结构、公司治理、M&A、ESG 数据挖掘、LLM 处理 10-K 年报
2. **严格过滤**：纯量化交易策略、无关宏观经济学、底层算法改进

# Execution Workflow
- Step 1 [相关性评估]：REJECT 或 KEEP
- Step 2 [高价值提取]：调用 SKILL.md 提取研究问题/方法/贡献

# Output Format
[STATUS]: KEEP / REJECT
[Title]: 论文标题
[Review]: 结构化关键信息
```

### 第二步：论文解析工作隔离

不同论文需不同解析环境（Python Marker vs Java Grobid），用 Git Worktree 隔离：

```bash
# 为新论文创建独立工作区
git worktree add ../paper-A-parse main
cd ../paper-A-parse

# 环境判断分支
if [ "包含大量公式" ]; then
    docker run -t --rm -p 8070:8070 lfoppiano/grobid
elif [ "扫描版/大量插图" ]; then
    marker_single paper-A.pdf --output_dir ./results
fi
```

> **Git Worktree vs 新建文件夹**：Worktree 让所有解析脚本在主仓库更新后自动同步，而数据和临时文件互不干扰，结束 `git worktree remove` 即可无痕销毁。

### 第三步：论文提取 Skills

加载预写的 SKILL.md，锁定学术锚点，拒绝盲目摘要：

```markdown
# Execution Rules
1. 拒绝盲目摘要：严禁无指引的泛泛摘要
2. 技能优先调用：处理前必须读取并遵循 SKILL.md
3. 专家视角对齐：以 SKILL.md 定义的学术关注点为唯一最高准则
```

### 第四步：学术生态 MCP 工具

```json
"mcpServers": {
  "zotero-connector": {
    "command": "node",
    "args": ["/path/to/mcp-zotero/build/index.js"],
    "env": { "ZOTERO_API_KEY": "..." }
  },
  "feishu-notifier": {
    "command": "python3",
    "args": ["/path/to/mcp-feishu/main.py"],
    "env": { "WEBHOOK_URL": "飞书群机器人链接" }
  }
}
```

### 第五步：核对 Sub-Agents

```bash
# 主 Agent 输出交给 Reviewer Agent 二次审核
cat report.md | claude -p \
  "你是顶刊苛刻审稿人。审查这份文献总结：
   1.质疑创新点：性能提升是否掩盖了假设条件？
   2.查找逻辑漏洞：方法与结论是否存在推导断层？
   输出【避坑指南】追加到原报告末尾。" \
  > final_report.md
```

---

## 🔍 借鉴点

| 文章概念 | Hermes 对应 | 吸收方式 |
|---------|------------|---------|
| 定时任务 = Loop 心跳 | Hermes `cronjob` | ✅ 已有 40+ cron jobs 运行中 |
| 工作树隔离 | Hermes `delegate_task` 隔离 context | ✅ 已有，但 Git Worktree 可用于代码类任务 |
| Skills = 知识继承 | Hermes `skills/` 系统 | ✅ 已有 200+ Skills，正是 Loop 的知识层 |
| MCP = 外部世界 | Hermes native MCP + mcporter | ✅ 已有 MCP 集成 |
| 子 Agent = 质量守门 | Hermes `delegate_task` 角色 | ⚠️ 需强化：编码 Agent 和审查 Agent 必须用不同模型 |

---

## 🔗 关联性

- [Agentic Engineering 三层体系：Loop-Harness-FDE](2026-06-15-Agentic-Engineering三层体系-Loop-Harness-FDE.md) — 本文是 Loop 层的独立验证
- [Agent 三原语架构](2026-06-15-Agent三原语架构.md) — Skills/Hooks 对应本文的 Skills + 子 Agent
- [Harness Architecture](2026-06-15-Harness-Architecture.md) — Harness 层是 Loop 之上的约束层

---

## 💡 启发

- **Loop Engineering 本质是"把人的判断力编码为机器可执行的循环"** — 不是让 AI 更聪明，而是让 AI 的工作流更可预测
- **"我的工作变成了写循环"** — 这句话精准描述了 Hermes cronjob + skills 体系的设计哲学
- **子 Agent 的"不同模型"原则** — 当前 Hermes 的 delegate_task 默认用同模型，这是一个可改进点：审查类子任务应强制用不同 provider

---

## 🔮 预判

- Loop Engineering 将成为 2026 下半年的主流范式 → 已在 Hermes 中验证可行性
- 文献检索 Loop 模板可直接复用到量化因子挖掘 → 定时抓取论文 → Skills 提取 Alpha 思路 → 子 Agent 验证有效性
- Prompt Engineering 不会消失，而是**降级为 Loop 内部的单个组件**（Loop 负责调度，Prompt 负责单次执行）

---

## 相关笔记

- [2026-06-15-Loop-Engineering-Prompt之后的下一个范式](./2026-06-15-Loop-Engineering-Prompt之后的下一个范式.md)
- [2026-06-15-超大规模点阵结构智能设计与基元数学表达](./2026-06-15-超大规模点阵结构智能设计与基元数学表达.md)
- [2026-06-15-大规模点阵电磁功能结构设计与适航数据闭环方案](./2026-06-15-大规模点阵电磁功能结构设计与适航数据闭环方案.md)
