# Coding Agent Harness 解剖学 — 构建能运行数小时的编码 Agent

> **来源**：[mastra.ai/blog/anatomy-of-a-coding-agent](https://mastra.ai/blog/anatomy-of-a-coding-agent)
> **作者**：Sam Bhagwat（Mastra CEO，Gatsby 联合创始人，斯坦福毕业）
> **发布日期**：2026-06-05（27 min read）
> **标签**：Coding Agent、Harness、Agent Loop、上下文管理、Mastra Code

---

## 一句话定义

> 一个 naive agent loop 到能运行数小时的 harness 之间，差的不只是更大的上下文窗口——而是**对话即通道、事件流→单一显示状态归约、工具可暂停等人、观测记忆三层架构、有序审批链**。Mastra Code 用这 8 个设计决策把编码 Agent 从"demo 级别"推向"生产级别"。

---

## 原文内容整理（完整保留核心论述 + 代码）

### 开篇：为什么 Agent 会在 Compaction 处"死亡"

> **Compaction is where coding agents go to die.** You can't hand your harness a `/goal` and go to sleep if it lobotomizes itself every 40 minutes.

一个 Agent 要升级为 harness，必须独立完成三件事：
1. **管理自己的上下文**
2. **在重启后存活**
3. **在无人纠正时仍能坚持决策**

大部分 Agent 做到了零项。

### 编码 Agent 的两种模式

| 模式 | 说明 | 代表产品 |
|------|------|---------|
| **Interactive（交互式）** | 你留在循环中，看每一步并随时纠偏 | Cursor, Windsurf, Cline, Claude Code（终端） |
| **Headless（无头）** | 你给出目标，收集 diff/PR，无人监督 | Claude Code, OpenAI Codex, Google Jules, Cursor Background Agents |

> **Mastra Code 更偏向自主行为**——因为"你可以走开的 Agent"必须自己管理上下文、在重启后存活、并在无人纠正时坚持你之前的决策。

### Naive Agent Loop 为什么失败（三种静默失败）

#### 1. Context Rot（上下文腐烂）

默认情况下，原始历史随着每次工具调用和响应不断增长。过时的结果、被取代的编辑、中间推理过程堆积，上下文的**信号密度**下降。模型要读更多文本才能获得更少的有用信息。

**危险之处**：没有任何东西会报错，模型继续在低信号上下文中产出。**更长的上下文窗口解决不了这个问题**——一个在 180k 无用 Token 上工作的 Agent 会显著差于一个在 40k 高质量 Token 上工作的 Agent。

#### 2. Lossy Compaction（有损压缩）

通常对 Context Rot 的回应是压缩——Agent 等到上下文接近限制时，把所有东西总结一下，用摘要替换原始历史。

这在纸面上可行，但**摘要会丢失需求的精确措辞、你提供的特定指令、以及你之前标记的边界情况**。

> Claude Code 用户广泛描述的 bug："session 在压缩边界后读取质量急剧下降，Agent 开始与自己压缩前做的决策矛盾。"

#### 3. Stateless Sessions（无状态会话）

没有线程存储，每次会话从零开始。之前的决策和文件级上下文全部丢失。你必须把上下文粘贴到 `CLAUDE.md` 文件中，每次重新解释架构——**你变成了 Agent 的记忆**。

> **三种失败的共同点**：Agent 从不停止产出，所以没有任何崩溃来警告你。

### Harness 架构核心设计

#### 设计 1：对话即通道（Conversation as Channel）

Harness 把对话当作一个**保持开启的通道**，而不是一个调用一次就等待的函数。

**函数调用 = 一次 HTTP 请求**：发请求 → 流式响应 → 连接关闭 → 什么都不剩。

**通道 = WebSocket / Pub-Sub Topic**：Harness 连接到会话线程一次，此后不断推入消息并接收 Agent 发回的一切。返回一个 **subscription**，提供 chunk 流、活跃运行 ID、以及 abort/unsubscribe 控制。

**开放通道使四件事成为可能**（一次性函数调用做不到）：

| 能力 | 说明 |
|------|------|
| **Interrupt（中断）** | 在 Agent 执行任务中输入，折叠进正在运行的工作，不停止它 |
| **Queue（排队）** | Agent 忙时说接下来的事，Harness 持有消息，当前运行结束后立即发送 |
| **Steer（转向）** | 告诉 Agent 停下来做别的，Harness 放弃当前运行，清除队列，重新开始 |
| **Crash Recovery（崩溃恢复）** | 对话存在于线程而非运行进程中，可以退出、重开、重新连接同一个线程 |

> 多个客户端可以同时订阅同一个线程——终端和 Web 视图跟随同一个对话。

#### 设计 2：原始模型输出 → 结构化事件

`processStreamChunk` 函数把每个原始 chunk 类型映射到一个干净的语义化 harness 事件。

**隔离原则**：一个重命名字段、一个拆分 chunk 类型、或一个新的流式阶段，只影响这一个函数，不影响下游任何东西。

**敏感数据处理**：工具可以在结果上附加 display transform——实际值仍保存到消息并发送给模型，但屏幕上渲染为 `••••••`。

#### 设计 3：事件 → 单一显示状态（Reducer 模式）

UI 不应该通过逐个回放事件来组装界面。Harness 用 **reducer** 把每个事件折叠成一个对象。

**DisplayState 对象包含**：Agent 是否在工作、正在写的消息、哪些工具在运行、任何待审批/问题、子 Agent 活动、记忆进度、变更的文件、实时任务列表。

渲染器只问一个问题：**"世界现在长什么样？"** 读对象并绘制。从不解析原始事件。

**两种订阅方式**：
- `subscribe(listener)`：给你每个事件，有序，不合并——适合日志和分析
- `subscribeDisplayState(listener)`：给你合并后的最新状态快照——适合终端或 Web UI

**批处理重绘**：`DisplayStateScheduler` 在 250ms 窗口内批处理普通更新，硬上限 500ms。突发事件（工具请求审批、问题、计划审批、Agent 启动/结束、线程/模式/模型变更）跳过队列立即刷新。

#### 设计 4：工具暂停等人（Back-Channel 机制）

工具在执行中可以"暂停"。从模型角度看，它只是调用了一个耗时较长的工具。底层 Harness 保持工具开启直到你回答。

**后通道**：在每次运行前，Harness 在工具上下文中附加一个小对象——一条回到 Harness 的私有线路，模型永远看不到。

通过这条线路，工具可以：
- 在屏幕上绘制提示
- 注册一个问题或计划审批
- 读写 Harness 状态
- 访问线程身份和 abort 信号

**纯文本降级**：后通道是可选的。如果同一个工具在没有 Harness 的 CI 管道中运行，它降级到纯文本路径继续工作而不是崩溃。

**askUser 工具核心代码**（完整保留）：

```typescript
export const askUserTool = createTool({
  id: 'askUser',
  description: 'Ask the user a question and wait for their response. ...',
  inputSchema: z.object({ /* question, options, selectionMode */ }),
  execute: async ({ question, options, selectionMode }, context) => {
    const harnessCtx = context?.requestContext?.get('harness') as HarnessRequestContext | undefined;

    // No harness callbacks present? Degrade to plain text instead of blocking.
    if (!harnessCtx?.emitEvent || !harnessCtx?.registerQuestion) {
      return { content: `[Question for user]: ${question}`, isError: false };
    }

    const questionId = `q_${++questionCounter}_${Date.now()}`;
    const answer = await new Promise<HarnessQuestionAnswer>((resolve, reject) => {
      const signal = harnessCtx.abortSignal;
      // ... wire `signal` to reject() so Ctrl-C cancels the wait cleanly ...
      harnessCtx.registerQuestion!({ questionId, resolve }); // park a resolver
      harnessCtx.emitEvent!({ type: 'askQuestion', questionId, question, options }); // draw the prompt
    });

    return { content: `User answered: ${formatQuestionAnswer(answer)}`, isError: false };
  },
});
```

> 工具注册回调 → 发射事件让 UI 绘制提示 → 在 Promise 上等待 → 你回答 → Harness 找到回调 → 触发 → Promise resolve → 工具返回结果 → 循环精确地从暂停处继续。

**submitPlan 工具**：相同的 callback + Promise 机制。计划被批准后，Harness **自动切换到 Build 模式**（从只读计划阶段进入执行阶段）。被拒绝则把反馈交回模型让它修改重新提交。

#### 设计 5：实时任务列表

三个工具操作同一个任务列表（存在 Harness 的 display state 中）：
- `taskWrite`：整体替换列表
- `taskUpdate` / `taskComplete`：按 ID 修改单个任务
- `taskCheck`：只读，确认所有任务完成后 Agent 才结束

**任务 ID 稳定性设计**：`assignTaskIDs` 函数确保即使模型重写整个列表，已有任务的 ID 也能被复用——通过内容匹配回前一次的任务 ID。

#### 设计 6：子 Agent — 隔离 vs 缓存复用

| 路径 | 说明 | 用途 |
|------|------|------|
| **Non-forked（非分叉）** | 全新 Agent，独立指令和受限工具集，不携带父 Agent 历史 | 需要无偏见的审查者——例如"审查这段代码有没有 bug"的子 Agent，不应被父 Agent 的推理影响 |
| **Forked（分叉）** | 克隆父线程，在父 Agent 上运行，模型看到完全相同的对话，**prompt cache 保持温热** | 更便宜更快。安全措施：fork 保留所有工具 schema（匹配缓存），但运行时替换被阻止的工具——子 Agent 尝试再 spawn 子 Agent 或编辑共享任务列表时会撞到 stub |

#### 设计 7：会话、模式与线程持久化

**模式 = Agent 的保存配置**：名称、标签、颜色、默认模型、运行的 Agent。

- **Build**（默认）：全工具访问，运行在 `anthropic/claude-opus-4-6`
- **Plan**（只读）：生成结构化计划（Overview + Complexity + Steps + Verification），运行在 `openai/gpt-5.2-codex`。批准后自动切换到 Build
- **Fast**：跳过计划阶段，运行在 `cerebras/zai-glm-4.7`
- **YOLO**：自动审批一切，不问权限

> 切换模式时，Harness 记住你在离开模式中使用的模型，切回来时恢复——**一整天在两个模式间切换，各自保持各自的模型**。

**线程持久化**：所有状态（模式、模型、Token 计数、记忆设置）保存在**对话本身**中而非运行程序中——所以它能在重启后存活。

**多窗口锁**：两个终端可以同时打开同一个会话。Harness 加锁——获取新锁之前释放旧锁，如果失败则撤销。两个窗口永远不可能同时认为它们拥有同一个会话。

#### 设计 8：工具审批有序链

每个工具调用在运行前解析为三种结果之一：**allow / deny / ask**。Harness 按有序规则链判定，第一个匹配获胜：

```typescript
private resolveToolApproval(toolName: string): PermissionPolicy {
    // 1. Per-tool deny — 绝对阻断，下游无法重新开放
    if (toolPolicy === 'deny') return 'deny';
    // 2. YOLO mode — 自动审批所有未被 deny 的
    if (state.yolo === true) return 'allow';
    // 3. Explicit per-tool allow/ask
    if (toolPolicy) return toolPolicy;
    // 4. Session tool grant — 本次会话中已批准的工具
    if (this.sessionGrantedTools.has(toolName)) return 'allow';
    // 5. Session category grant — 按类别(read/edit/execute/mcp/other)
    if (this.sessionGrantedCategories.has(category)) return 'allow';
    // 6. Explicit per-category policy
    if (categoryPolicy) return categoryPolicy;
    // 7. Default — ask
    return 'ask';
}
```

> **规则序列本身就是策略**。Per-tool deny 最高优先（让你围栏单个危险命令），然后 YOLO，然后显式策略，然后会话级授予，然后类别策略，最后默认询问。

### 观测记忆（Observational Memory, OM）

> 解决 Lossy Compaction 的核心创新。

OM 是一个 **LLM 摘要器**，在可定制的阈值（默认 40k Token）激活，将长对话转换为小得多的内容（100-1500 Token），清除上下文，替换为观察者摘要后的 Token。

**两个模型协作**：
- **Observer model（观察者）**：读取对话，写下结构化观察——决策、事实和状态变更
- **Reflector model（反射器）**：当观察堆积时压缩它们，合并同时保留完成标记和日期

**主 Agent 读取三层**：
1. 最近的原始消息（直到上下文限制）
2. 观察日志
3. 反射摘要

> 例如，不再携带四十轮原始工具输出，Agent 看到最后几条消息的逐字内容、一条简短的日志（"我们选了 Postgres，构建通过，auth 文件不可触碰"）、以及上面的压缩摘要。**决策作为决策存活，而不是埋在摘要中的转述。**

**OM 触发时机**：
- 默认 40k Token，但提前 20% 间隔运行（通常在限制到达前就准备好了）
- 空闲一段时间后触发（按 Provider 匹配 prompt cache 保活时间：Anthropic ~5min, DeepSeek/OpenAI ~1h, Groq ~2h, Gemini ~24h）
- Provider 切换时触发（新 Provider 无法复用之前的缓存，不如给压缩后的图片）

**失败策略**：如果观察者或缓冲步骤失败，Harness **终止运行而非在损坏的会话画面上继续**。

### Mastra Code vs Claude Code vs OpenAI Codex 对比

| 任务 | Mastra Code | Claude Code | OpenAI Codex |
|------|-------------|-------------|--------------|
| **长时间运行不降质** | 后台持续蒸馏对话，Agent 保持密集工作记忆，永不单步 summarize-and-discard | 等到上下文接近满才总结全部历史并替换 | 同 Claude Code |
| **恢复中断的任务** | 重开线程，带着相同的模式、模型、记忆阈值和 Token 计数回来 | `--continue` 恢复上个会话或 `--resume` 选一个，每次重新喂 `CLAUDE.md` | CLI 恢复过去会话，`AGENTS.md` 供应项目上下文 |
| **任务中转向** | 输入折叠进运行中的任务、排队下一条消息、终止并重定向、退出后重连 | 中断运行中的 turn 发新指令 | 同 Claude Code |
| **审批** | 有序规则链，per-tool 或 per-category 设置 allow/deny，加一个开关全部自动审批 | 危险操作前请求许可，构建白名单 | suggest → auto-edit → full-auto 三级模式 |
| **模型选择** | 跨 Provider 统一选择器，每个模式可不同模型 | 仅 Anthropic | 仅 OpenAI |
| **可扩展性** | 完全开源（harness 库 + CLI） | 闭源 | CLI 开源 |

### MCP / Skills / 插件

- **MCP servers**：添加 JSON 片段到配置文件即可接入新数据源和工具，不改一行代码
- **Skills**：Markdown 文件，给 Agent 持久化、可复用的任务模式指令——捕获项目约定、工作流步骤、约束规则

### 四个总结性洞察

> 1. **对话是通道**（你保持订阅），不是函数（调用一次等待）——这是 Agent 可中断、可转向、重启后可恢复的基础
> 2. **原始模型输出被翻译成干净事件**，然后折叠成单一快照——任何 UI 只读快照不解析流
> 3. **工具可以暂停等人**——通过后通道，没有人回答时降级为纯文本
> 4. **会话状态存在于线程**——关闭终端保留模式、模型、Token 计数和记忆设置

---

## 结合最新研究与技术变化

### 1. 与"自进化四波浪潮"笔记的交叉验证

本文的 **Observational Memory（OM）** 直接回应了"验证是自进化最终瓶颈"的论点。OM 不是简单的 summarize-and-discard，而是**观察者+反射器双模型架构**——观察者提取结构化决策，反射器压缩时保留完成标记和日期。这与 Prime Agent 的 Continual Harness `/refine` 机制理念一致：**持久化聚焦的、可审查的课程**，而非模糊的摘要。

### 2. 与 SkillOpt 的关联

Mastra Code 的 **Skills 系统**（Markdown 文件给 Agent 持久化指令）与 SkillOpt 优化的对象完全一致。Mastra 的洞察"Writing one removes that re-context work for every session after it"说明 Skill 的核心价值是**减少每会话的重复上下文重建**——这正是 SkillOpt 通过训练优化这些 Skill 文档的动力。

### 3. 与 LLM 微调成本工程笔记的关联

Mastra Code 的**多模式多模型架构**（Build=Opus, Plan=GPT-5.2-codex, Fast=glm-4.7）是"混合路由"的实践版本——不同复杂度的任务自动使用不同成本的模型。这与微调笔记中"40% 团队用 SLM 处理 80-95% 请求"的策略对应。

### 4. 2026 最新技术变化

- **Prompt Cache 保活时间成为架构约束**：OM 的触发时机直接绑定各 Provider 的缓存保活时间（Anthropic 5min, OpenAI 1h, Gemini 24h）——这是 2026 年的新工程约束
- **YOLO 模式成为标配**：Mastra/Claude Code/Codex 都有类似的"全自动审批"模式——说明业界已接受"在沙箱中全自主"的范式
- **Plan→Build 自动切换**：从只读计划到执行的自动化移交——这比手动模式切换更接近真正的自主 Agent
- **Forked Subagent 保持 prompt cache 温热**：用分叉子 Agent 来省钱的策略——2026 年 Prompt Cache 成本优化已深入到子 Agent 层

### 5. 与 ACM Agentic Context Management 的关联

本文的 **Context Rot** 和 **Lossy Compaction** 问题描述的正是 ACM 论文中的核心挑战。Mastra 的 OM 方案（观察者+反射器+三层读取）是 ACM 论文"渐进式压缩"理念的工程实现。

---

## 学习进化借鉴点（对 Hermes Agent 的启示）

| Mastra Code 设计 | Hermes Agent 现状 | 可借鉴方向 |
|-----------------|-------------------|-----------|
| **对话即通道**（interrupt/queue/steer） | ❌ 当前无 mid-turn steering | 实现 OUT-OF-BAND 消息机制，允许用户中途纠偏 |
| **OM 观测记忆**（Observer + Reflector 双模型） | ⚠️ 有 L1/L2/L3 三级记忆但无运行时观察者 | 添加 Observer 模型在 40k Token 时提取结构化决策，替代粗暴 compaction |
| **Plan→Build 自动模式切换** | ❌ 无模式概念 | 添加 Plan（只读）/Build（全权限）/Fast（快速回答）三模式 |
| **有序审批链**（7 层 per-tool→YOLO→session→category→ask） | ⚠️ 有简单的"确认"层但不分层 | 实现细粒度审批策略，支持 per-tool deny + YOLO + category 白名单 |
| **Forked Subagent 保持缓存温热** | ❌ delegate_task 全新上下文 | Fork 模式复用父线程上下文 + prompt cache |
| **DisplayState Reducer**（250ms 批处理 + 突发立即刷新） | N/A（飞书场景不同） | 飞书卡片消息可以用类似 reducer 模式组装 |
| **任务 ID 稳定性**（assignTaskIDs 内容回溯） | ⚠️ todo 工具每次替换全列表 | 实现基于内容匹配的 ID 复用 |
| **线程持久化**（模式+模型+Token 计数全保存在线程上） | ⚠️ 有 session 但模式/模型不持久 | 在 session metadata 中保存模式选择和模型偏好 |
| **多窗口锁**（防两个终端踩对方） | ❌ 无锁机制 | 如果多 session 并发操作同一项目需要加锁 |

### 最值得优先借鉴的 3 个设计

1. **OM 观测记忆**——直接解决 Hermes 的 context compaction 问题。当前 Hermes 的 compaction 就是"summarize-and-discard"，Mastra 的 Observer+Reflector 双模型架构可以在 Hermes 上实现
2. **Plan→Build 自动模式切换**——Hermes 可以加一个 Plan 模式（只读分析+生成计划→用户批准→自动切 Build 执行），大幅提升复杂任务的质量
3. **有序审批链**——Hermes 当前的权限模型是"允许/禁止/确认"三层，可以升级为 Mastra 的 7 层有序链，支持更灵活的 per-tool 策略

---

## 趋势判断

- **Harness 工程成为独立学科**：从"Agent = LLM + 工具"到"Agent = LLM + 工具 + Harness"，Harness 层（上下文管理 + 模式切换 + 审批链 + 记忆系统 + 多窗口协调）正在成为专门的工程领域
- **Context Rot 是 2026 年的核心战场**：更长的上下文窗口解决不了信号密度下降的问题。OM/Continual Harness/SkillOpt 都在用不同方式攻击同一个问题——**不是保留更多，而是保留更好的**
- **Prompt Cache 时间窗口成为架构决策因素**：OM 的触发时机、Provider 切换策略、Forked Subagent 设计都围绕 prompt cache 保活时间展开——这是 2026 年的新工程约束
- **开源 Harness 追赶闭源**：Mastra Code 完全开源 harness 库+CLI，加上 MCP/Skills/Plugin 扩展——开源 Agent 框架正在系统性地缩小与 Claude Code/Cursor 的差距
- **对话即通道会成为标准**：从"一次函数调用"到"保持开放的 Pub/Sub 通道"——这个范式迁移将影响所有 Agent UI 设计
- **多模式多模型成为标配**：Build/Plan/Fast/YOLO 四模式 + 不同模式用不同 Provider 的模型——2026 年的 Agent 不再绑定单一模型
- **Compaction 不再是唯一选择**：从 summarize-and-discard → Observer+Reflector 双模型蒸馏 → 三层读取（原始+观察+反射）——上下文管理正在分层化

---

## 关联分析

- **与 harness-architecture Skill 的直接关联**：你的 `harness-architecture` Skill 定义了六层 Harness 设计模式，Mastra 这篇文章是其中"上下文管理层"和"交互管理层"的最佳实践参考
- **与 context-engineering-patterns Skill 的关联**：本文的 OM 是 context engineering"预算化检索"支柱的工程实现
- **与 agent-reliability-engineering Skill 的关联**：Mastra 的"如果观察者失败就终止运行而非继续在损坏的画面上"是优雅降级的具体实践
- **与 steer-hook Skill 的关联**：Mastra 的 interrupt/queue/steer 三种通道行为正是 steer-hook 要实现的功能
- **与 state-machine-loop Skill 的关联**：Mastra 的 Plan→Build 模式切换 + DisplayState reducer 是状态机循环的具体实现
- **与 OttoClaw 项目的关联**：OttoClaw 的 message_bus（FreeRTOS 队列）是"对话即通道"在嵌入式硬件上的简化实现

---

## 📎 关键链接

- 📖 原文：[mastra.ai/blog/anatomy-of-a-coding-agent](https://mastra.ai/blog/anatomy-of-a-coding-agent)
- 💻 Mastra GitHub（26.8K⭐）：[github.com/mastra-ai/mastra](https://github.com/mastra-ai/mastra)
- 🚀 Mastra Code：[code.mastra.ai](https://code.mastra.ai/)
- 📖 Sam Bhagwat 著作：《Principles of Building AI Agents》(2025)

---

*笔记创建：2026-08-07 · 来源：mastra.ai Harness 解剖学*

## 相关笔记

- [DeepSeek-Agent-Harness执行栈全景图](2026-08-06-DeepSeek-Agent-Harness执行栈全景图.md)
- [Harness-vs-Loop-vs-Graph三层实践指南](2026-08-01-Harness-vs-Loop-vs-Graph三层实践指南.md)
- [Awesome-LLM-Apps与AI-Harness课程](2026-08-07-Awesome-LLM-Apps与AI-Harness课程.md)

---
