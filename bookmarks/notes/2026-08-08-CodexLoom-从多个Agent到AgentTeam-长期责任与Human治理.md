# CodexLoom — 从多个 Agent 到真正的 Agent Team（长期责任×直接协作×Human 治理）

> **来源**：微信公众号文章（CodexLoom 官方长文）
> **产品**：[codexloom.ai](https://codexloom.ai)
> **发布时间**：2026-08-04（时间戳 1785460930）
> **标签**：Agent Team、多 Agent 协作、Codex、组织治理、External Interface

---

## 一句话定义

> **多个 Agent 并不会自动成为一支 Team。** 只有当原本全部集中在 Human 脑子里的责任、关系、交接方式、当前状态和边界，开始被逐渐外化，成为整个 Team 可以查询、使用和持续验证的工作结构，它们才真正成为一支 Team。CodexLoom 就是把一条条独立的 Codex Thread 织成一支长期负责、能够协作、由 Human 治理的 Agent Team 的产品。

---

## 完整原文核心论述保留

### 楔子：一次意外的外发

作者本意是先上线 Landing Page 再慢慢打磨。结果负责 Web 的 Agent 完成上线后，按照已有协作关系通知了 Community Agent。Community Agent 判断这是大新闻，直接整理素材发到飞书群。等作者看到时消息已发出去了。

> 但工作仍然沿着已有的责任、协作关系和授权边界继续向前走。这正是我做 CodexLoom 的原因。

### 核心演化路径

```
Task Agent → Long-running Agent → Domain 分化 → Multiple Agents → Agent Team
                                                                    ↑
                                                            Human 从 Router 变成 Owner
```

---

### 第一章：一个 Agent 怎么变成多个 Agent

**Task Agent**：一次性任务，边界清楚，用完即弃。但真实工作不是彼此独立的 Task——一篇文章写完后还会修改，一个页面上线后还要迭代。

**Long-running Agent**：同一类责任开始有持续存在的主体。Human 反复合作后形成对它的判断：什么时候找它、擅长什么、哪些边界要提醒。

> Task 是工作切片，真实工作是一条持续流动的责任线。

**Domain 分化**：Agent 变好用了→人不断把更多工作交给它→Scope 扩张→不同 Context 和判断互相干扰→能力劣化。于是需要分化：研究交给 Research Agent、页面上线交给 Web Agent、写作交给 Writer Agent。

| 阶段 | 核心特征 | 瓶颈 |
|------|---------|------|
| Task Agent | 一次性，用完即弃 | 反复冷启动 |
| Long-running Agent | 同一责任持续存在 | Scope 过大导致能力劣化 |
| Domain Agents | 分化为多个专业 Agent | **Human 成为唯一 Router** |
| Agent Team | Agent 之间直接协作 | Human 上移为 Owner |

> 核心判断：真实工作反复回来，逼出了 Long-running Agent；Scope 扩张与能力劣化，逼出了多个 Domain Agents；Agent 的分化，又把协作瓶颈集中到了 Human。

---

### 第二章：让"谁负责什么"离开 Human 的脑子

**Profile** 回答三个问题：

| 维度 | 含义 |
|------|------|
| **Identity** | 它是谁 |
| **Domain** | 它长期负责什么 |
| **Scope** | 它在哪里停止 |

> Profile 不是最终答案，而是当前采用的组织假设。

**Organization**：parent/child 长期责任边界（一个大责任下分化出稳定子责任）。

**Collaboration**：有方向的长期协作接口（两个独立 Domain 之间反复出现的协作）。

**Activity**：从真实 Message 中聚合的协作迹象（运行证据 vs 声明结构）。

> 声明和实际工作分开记录：Profile/Organization/Collaboration 是声明，Activity 是运行证据。

**Team 查询命令**：
```bash
loom team              # 整支 Team 视图
loom team <agent>      # Agent 完整 Profile + 关系 + Activity
loom profile get <agent>  # 只读 Identity/Domain/Scope
loom team links <agent>   # 协作关系
```

---

### 第三章：让 Agent 自己开始协作

**Agent Message**：发送方和接收方明确，进入接收方的长期 Thread。发送方的完整 Context 不会复制过去。

| 消息类型 | 说明 |
|---------|------|
| **Request**（`--response required`） | 需要对方返回判断、行动或结果 |
| **Notification**（`--response none`） | 同步状态变化，不要求回复 |
| **Reply** | 对 Request 的因果回复 |

```bash
loom msg TARGET --from SELF --subject "有界请求" \
  --response required --body "问题、边界、证据要求"
```

> 协作责任分层：发送方判断+交出 Context → 接收方专业判断+返回结果 → 负责收口的 Agent 整合 → Human 保留方向/选择/Review/授权

---

### 第四章：Message 负责沟通，Topic 负责收口

**Topic**：跨 Agent 工作的唯一当前版本。

| 角色 | 职责 |
|------|------|
| **Responsible** | 唯一收口人，维护 current brief，拆问题找 Participant |
| **Participant** | 在自己 Thread 中完成专业工作，返回局部结果 |

> Topic 不是群聊。每条 Topic 只有一个 Responsible。Participant 不共享全部 Context，只收到与自己那一段相关的 Topic Context 和 Message。

**Topic current brief** 持续保存：
- 这项工作目前采用的事实、判断、下一步和限制
- 每个 Participant 负责什么
- 工作正在等待谁、等待什么
- 关键证据锚点和阶段结果
- Topic 是否已被标记为收口

**Artifact**：正式结果的稳定版本快照（稳定 ID + 校验值）。

> current brief 说明"我们怎样理解这项工作"，Artifact 保存"这个判断对应哪个文件版本"。

**Needs You**：在正确位置找回 Human。Agent 先说明已确认了什么、具体缺少哪个判断、有哪些选项，再把问题交回 Human。

> **协作边界**：本地完成不等于协作完成。只有局部结果回到 Responsible 并被整合进当前版本，这一段责任才真正闭环。

---

### 第五章：Overview — 让持续变化的 Agent Team 可治理

**核心管理哲学**：从精益管理借鉴——可视化不是把更多数据堆到屏幕上，而是让问题先显露出来。

| 视图 | 观察什么 |
|------|---------|
| **Status** | 正在执行什么、等待什么、是否有积压 |
| **Capacity** | New-work wait（新工作排队多久才第一次处理）、当前 backlog |
| **Daily Activity** | 按时间对齐的执行、Turn 和 Token 活动行 |
| **Token Usage** | input/cached/output/reasoning 分布 |

> **Signal 不是 Diagnosis。** Overview 不替 Owner 得出结论。忙不代表有价值，低执行不代表无用，Token 多不代表结果更好。

**治理循环**：
```
发现 Signal → 下钻 Evidence → 判断原因 → 选择干预 → 用后续真实工作验证
```

> Human 的新位置：从每一段工作的人工 Router，上移成了观察、追问、诊断和调整整支 Team 的 Owner。

---

### 第六章：Agent Team 进入真实外部关系

**五个问题**：

1. 谁在代表这支 Agent Team
2. 它在当前外部关系中扮演什么角色
3. 什么输入可以触发它，它可以行动到哪一步
4. 需要其他专业能力时，怎样调用内部 Domain Team
5. 什么情况必须停止，把事实/选择/Review/授权交回 Human

**外部架构**：

| 层 | 功能 |
|----|------|
| **Connection** | Provider app/bot/account/tenant 的连接和能力 |
| **Agent Address** | 外部 identity 绑定到长期 Agent |
| **Conversation Membership** | 每个 Conversation 的局部角色、guidance、通信边界 |
| **Inbox** | 外部入站消息记录（handled、attempt、Membership version） |
| **Outbox** | 外部出站记录（目标、内容、幂等、Provider receipt） |

> Interface Agent 拥有的是外部入口、意图翻译、内部路由、受众表达和结果回流——不是背后每个 Domain 的事实所有权。

**权限层级**（从低到高）：
知道一个答案 → 可以起草表达 → 可以回复已有问题 → 可以主动发布 → 可以代表别人作承诺 → 可以执行具有现实副作用的动作

> Human 保留的是外部后果的最终边界。

---

### 第七章：CodexLoom 在织什么

**核心矛盾**：稳定的 Agent，动态的 Team。

> 稳定的是长期责任主体，动态的是当前组织假设。

从 Multiple Agents 到 Agent Team，真正发生的不是 Agent 数量的变化，而是：
> 原本全部集中在 Human 脑子里的责任、关系、交接方式、当前状态和边界，开始被逐渐外化，成为整个 Team 可以查询、使用和持续验证的工作结构。

**CodexLoom 的六个核心能力**：
1. 让 Thread 成为长期 Agent（Identity/Domain/Scope）
2. 让 Agent 查询 Profile 和声明关系，通过 Message 直接协作
3. 让跨 Agent 工作通过 Topic 保存由 Responsible 维护的当前版本
4. 让 Human 在需要事实/选择/Review/授权时重新进入（Needs You）
5. 让 Owner 通过 Overview 观察 Team 真实运行
6. 通过受治理的 External 把内部能力带入外部关系

---

## 结合最新研究与技术变化

### 1. 与 Hermes Agent 架构的直接对标

| CodexLoom 概念 | Hermes 对应 | 差距/启示 |
|---------------|-------------|----------|
| **Profile (Identity/Domain/Scope)** | Skill 描述 + AGENTS.md | Hermes 缺少 Agent 级 Scope 边界声明 |
| **Agent Message** | delegate_task | delegate_task 是单向的，缺少 reply 回流和因果链 |
| **Topic (Responsible/Participant)** | 无直接对应 | Hermes 缺少跨 Agent 工作的收口机制 |
| **Overview (Status/Capacity/Token)** | observability-dashboard | Hermes 有监控但缺少治理视角（瓶颈发现） |
| **External Interface** | Feishu/WeChat Gateway | Hermes 的外部连接缺少 Conversation Membership 级的角色/权限分层 |
| **Needs You** | clarify | Hermes 有 clarify 但缺少"阻断点持久化" |
| **Artifact** | 文件系统 + Memory | Hermes 缺少带校验值的正式结果快照 |

### 2. 与 Coding Agent Harness 解剖学笔记的关联

Mastra 文章说"Harness 工程才是竞争力"。CodexLoom 把这个判断推向了组织级——不仅单个 Agent 的 Harness 重要，**Agent 之间的协作结构（Message/Topic/Overview）才是 Team 级 Harness**。

### 3. 与 YC QM 的关联

QM 的 Scope 隔离 + Skill Pack + Admin Control 面向的是多人场景。CodexLoom 面向的是单人多 Agent 场景——**两个产品互补**：QM 解决"多人如何共享一个 Agent"，CodexLoom 解决"一个人如何治理多个 Agent"。

### 4. 与 Agent 编排设计模式的关联

CodexLoom 的 Responsible/Participant 模式是 `agent-orchestration-pattern` Skill 的一种具体实现——但比通用编排模式更注重**长期身份和声明结构的演化**。

### 5. 与自进化四波浪潮的关联

CodexLoom 的"Profile 不是最终答案而是组织假设"+"后续工作继续验证和修正"正是自进化的核心——声明→验证→修正→沉淀的持续循环。

---

## 学习进化借鉴点

| CodexLoom 的设计 | 可借鉴到 Hermes | 优先级 |
|-----------------|----------------|--------|
| **Profile = Identity + Domain + Scope** | 为每个 Hermes 实例建立 Scope 边界声明 | 高 |
| **Topic Responsible/Participant 收口** | delegate_task 增加 reply 回流和收口机制 | 高 |
| **声明 vs 运行证据分离** | Profile 是声明，Activity 是证据，两者不能互替 | 高 |
| **Signal 不是 Diagnosis** | observability-dashboard 只提供调查入口不自动诊断 | 高 |
| **Needs You 阻断点持久化** | clarify 增加 Context/选项/恢复路径的结构化 | 中 |
| **Conversation Membership** | 外部连接的角色/权限按 Conversation 独立配置 | 中 |
| **治理循环（Signal→Evidence→干预→验证）** | Agent Team 的持续改善方法论 | 高 |
| **"稳定的 Agent，动态的 Team"** | Agent 身份稳定，协作关系动态调整 | 高 |

---

## 趋势判断

1. **Agent Team 是下一个范式**——从单 Agent 到 Multiple Agents 再到 Agent Team，协作结构外化是关键
2. **Human 从 Router 变成 Owner**——不再串联每一步，而是在方向/事实/选择/Review/授权的位置回来
3. **声明结构与运行证据必须分离**——Profile/Organization/Collaboration 是假设，Activity 是证据
4. **Topic 不是群聊**——群聊共享全部 Context，Topic 只共享当前状态，专业过程留在各自 Thread
5. **External 风险模型完全不同**——内部不准确的判断是工作误差，外部就是产品事实或承诺
6. **治理是持续改善不是一次性 Reorg**——先让问题显露，再小幅可逆调整，用后续工作验证
7. **"Signal 不是 Diagnosis"是核心管理哲学**——指标帮助理解系统，不排名 Agent

---

## 关联分析

- **与 YC QM**：QM=多人共享 Agent，CodexLoom=单人治理多 Agent，互补
- **与 Coding Agent Harness**：CodexLoom 把 Harness 从单 Agent 推向 Team 级
- **与 agent-orchestration-pattern**：Responsible/Participant 是编排模式的具体实现
- **与 observability-dashboard**：CodexLoom 的 Overview 增加了治理视角
- **与自进化四波浪潮**：声明→验证→修正是自进化的组织级体现
- **与 AI for Physics**："没有可优化的目标函数"=CodexLoom 说的"Signal 不是 Diagnosis"

---

*笔记创建：2026-08-08 · 来源：CodexLoom 官方长文（微信公众号）*
