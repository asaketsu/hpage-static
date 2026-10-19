# OpenBot：开源版 Grok Bot 与 AG-UI 协议——企业 Agent 平台的三协议生态位

> **来源**：X/Twitter @shao__meng 推文（中文解读）+ CopilotKit 官方产品页 + 原推 @ataiiam
> **原文链接**：https://x.com/shao__meng/status/2090348345802002842
> **配套材料**：
> - 产品页：https://copilotkit.ai/openbot（4.1K 全文已取）
> - 原推：@ataiiam（Atai Barkai，CopilotKit 团队，2026-08-19 发布 OpenBot，2026-08-20 中文解读）
> **记录日期**：2026-08-21

**标签**：#OpenBot #AGUI #CopilotKit #GrokBot开源替代 #MCP #A2A #企业Agent平台 #生成式UI #ComputerUse

---

## 一、内容详细整理

### 1.0 定位一句话

> **OpenBot = 开源版 Grok Bot**：跑在自己基础设施里的企业 agent 平台，来自 CopilotKit 团队，技术底座是自家发起的 **AG-UI 协议**（Agent–User Interaction Protocol）——"works with ANY agent harness, designed for real companies"。

原文推（Atai Barkai）列出的五大能力：AI Coworkers / Generative UI / Computer use (remote/local) / Agent-human handoffs / **Full data recording, owned by you**。

### 1.1 三协议生态位（本篇最有价值的框架）

当前智能体生态有三个互补的开放协议：

| 协议 | 发起方 | 管什么 | 一句话 |
|------|--------|--------|--------|
| **MCP** | Anthropic | 智能体 ↔ 工具/数据 | 智能体如何接入外部工具和知识 |
| **A2A** | Google | 智能体 ↔ 杀能体 | 智能体之间如何协作分工 |
| **AG-UI** | CopilotKit | 智能体 ↔ 用户界面 | 智能体的工作如何变成人能看到、能质疑、能打断的交互 |

**AG-UI 的定义**（产品页原文）：开放、基于事件的标准，规定 agent 如何与"人正在看的那个应用"对话。**"It is the leg the other two do not cover."**（它是另外两条腿不覆盖的那条。）

**互操作性红利**：任何说 AG-UI 的 agent——LangGraph、Mastra、PydanticAI、或自研——注册为 endpoint 就获得一个 channel。**不对单一框架下注**。

### 1.2 核心产品概念（四大件）

**1. Bot 即"角色"（Role），而非聊天机器人**

- 每个 agent 有自己的频道（类似同事的私聊线程）、名称、职责描述
- **最小权限原则**：只被授予其工作所需的技能和数据源
- 官方示例角色：公司知识问答、数仓分析师（只读）、桌面调研、工具操作员、收件箱分拣、新人入职助手
- 自带三个示例同事：General Assistant / Knowledge / Risk Analyst
- **"是配置而非代码"**：通过 `agents.yaml` 或 UI 的 /agents 页面即可新增

**2. 每个 Bot 一台自己的电脑**

- supervisor 服务为每个 Bot 分配**独立容器**：
  - 独立的 Chromium 浏览器（**带真实登录态**）
  - 独立的 /workspace 文件卷
  - 独立的浏览器配置
- **无 API 时的降级路线**：Bot 像人一样登录并操作界面
- **屏幕实时展示**在对话旁边——"work is visible rather than something you are told about afterwards"（工作可见，而非事后被告知）
- **人随时"接管方向盘"（take the wheel）**：处理登录墙、2FA 等机器卡点后交还
- **关键设计**：人操作期间，**Bot 的动作会被拒绝而非排队**——避免人机同时对同一界面操作的冲突

**3. 用组件回答，而不只是文字（Generative UI）**

- Bot 可返回**编译好的 React 组件**（图表、卡片等生成式 UI）
- 沙箱组件可在 /admin/playground 在线编写并**无部署发布**
- **每个组件调用都经过服务端三重校验**：存在性、发布状态、授权

**4. Skills 是指令而非能力**

- 通过 `/` 在输入框唤起（与 Claude Code/Hermes 的 slash 命令同构）
- **个人技能只附着于作者自己拥有的 Bot**
- **部署级技能由管理员管理**——两级技能治理

### 1.3 企业级安全设计（产品页"Security review 预答题"）

产品页明确"AI 试点失败的原因通常不是模型，而是没人说得清数据去了哪"——六条防线：

1. **单部署单公司**：无共享租户、无席位计数；Docker Compose 起演示，**Helm 是生产支持路径**
2. **内容不出域**：文档、向量、权限、对话全部存在**你自己的 Postgres**；不向任何未配置的地方发送
3. **模型密钥自持**：管理员持有 provider 凭证；**密钥用你的 KEK 加密存储**，永不返回、永不记日志、可撤销
4. **不捆绑模型**：内置 agent 在管理员配置 provider 前**保持不可用**——"Nothing silently falls back to somebody else's LLM"（绝不静默降级到别人家的 LLM）
5. **检索 fail-closed**：源系统权限归一化为 allow/deny principals，**deny 赢**；权限映射模糊的文档**根本不返回**
6. **工具调用过网关**：敏感 MCP 调用经过显式 per-tool allowlist 网关，**每次调用与结果都被记录**

另有知识问答的三原则：**引用而非断言**（每个答案注明来源文档）、权限 fail-closed、来源可查。

### 1.4 @shao__meng 推文的增量判断

- 定位判断："**开源替代类产品，可用性先不说，抱着学习的目的还是很不错的**"——务实的评估姿态
- 把 OpenBot 的底座归结为 AG-UI 而非 runtime 本身——**协议卡位比产品卡位更值钱**的隐含判断

---

## 二、查询拓展

### 2.1 AG-UI 协议技术细节

AG-UI（Agent-User Interaction Protocol）是 CopilotKit 2025 年发起的开放协议，核心设计：

- **事件驱动（event-based）**：agent 与前端之间传输标准事件流——RunStarted / TextMessageContent / ToolCallStart / ToolCallResult / StateSnapshot / StateDelta 等约 16 种标准事件类型
- **传输层无关**：HTTP SSE / WebSocket 皆可
- **双向**：前端不仅能看（订阅事件），还能打断（interrupt）、发人类输入（human-in-the-loop）
- **状态同步**：StateSnapshot/StateDelta 事件让 agent 的内部状态与前端共享状态双向同步——这是"生成式 UI"的协议基础
- 与 MCP/A2A 的分层：MCP 管 agent 的"手"（工具），A2A 管 agent 的"同事关系"（协作），AG-UI 管 agent 的"脸"（呈现与交互）

三协议拼起来是一个完整的**多智能体人机协作架构栈**——这个分层框架是 @shao__meng 推文的最大贡献。

### 2.2 Grok Bot 是什么（被开源的对象）

Grok Bot 是 xAI 2026 年在 X 平台推出的 agent 产品：用户在 X 内给 Grok 派任务，Grok 操作浏览器完成任务（订票/填表/调研），过程截图可见，可人工接管。特色：浏览器操作+实时可视+频道化交互。OpenBot 把这套体验**开源化+企业内网化**（数据不出域）。"Grok Bot 的开源版"是营销定位，但准确抓住了产品形态。

### 2.3 Computer Use 的安全边界：独立容器+登录态

"每个 Bot 一台电脑"的设计哲学值得展开：

- **隔离**：独立容器（Chromium+文件卷+配置）= Bot 间不串数据，风险半径受控
- **真实登录态**：Bot 用自己的账号会话登录内部系统——像员工而非像爬虫
- **人机冲突协议**："人操作期间 Bot 动作被拒绝而非排队"——这是个精妙的细节：排队会导致人走后 Bot 重放陈旧上下文的动作；拒绝强制 Bot 重新观察世界
- 与 Anthropic Computer Use / OpenAI Operator 的区别：那两家是**单实例云侧**浏览器，OpenBot 是**每 Bot 一容器+企业内网**——安全模型完全不同

### 2.4 Generative UI 的工程化：从 Vercel AI SDK 到协议化

生成式 UI 谱系：Vercel AI SDK 的 Generative UI（React Server Components 流式返回）→ **协议化（AG-UI 事件流）**→ 沙箱化（OpenBot 的 /admin/playground 在线编写无部署发布）。关键工程问题与 OpenBot 的答案：

- **安全**：服务端三重校验（存在性/发布状态/授权）——组件不是任由 LLM 生成的，是**白名单化的预编译组件库**
- **治理**：组件是"注册资产"而非"生成产物"——LLM 只能选择和填充参数，不能发明新组件
- 这是"自由度 vs 安全"的折中：纯生成 UI（LLM 写代码）不可审计，白名单组件流不可创新但可治理——企业场景显然选后者

### 2.5 Skills 双级治理与 Claude Code/Hermes 对比

| 维度 | OpenBot | Claude Code | Hermes |
|------|---------|-------------|--------|
| 唤起方式 | 输入框 `/` | 终端 `/` | 消息内自然语言/skill_view |
| 个人级 | 附着于作者自己的 Bot | ~/.claude/skills 个人目录 | profile skills 目录 |
| 部署级 | 管理员管理 | 企业版 managed skills | AGENTS.md+共享 skills |
| 本质 | **指令模板**（instruction） | 指令+脚本+资源 | 指令+脚本+references |

"Skills 是指令而非能力"这句值得咀嚼：能力（capability）是工具层的事（MCP），skills 只是**把使用某工具的正确姿势写成可复用指令**——与 Hermes 的 skill=程序性记忆定义一致。

---

## 三、归纳总结

### 3.1 一句话结论

> **OpenBot 是"跑在自己机房的开源 Grok Bot"：以 AG-UI 协议为底座（agent↔UI 交互的事件标准，补齐 MCP/A2A 之外的第三条腿），用频道化 AI 同事+每 Bot 独立容器浏览器+白名单生成式 UI+fail-closed 权限，把"人能看到、能质疑、能打断"做成了企业安全评审能过的产品形态。**

### 3.2 与昨日笔记的连续性

```
2026-08-21 笔记①：Harness 四组件（Pi/Earendil）——Model 变 Agent 的运行环境
2026-08-21 笔记②：OpenBot + AG-UI（本篇）——Agent 与人交互的协议层
```

两篇构成一个完整的**agent 基础设施栈视图**：

| 层 | 关注点 | 代表 |
|----|--------|------|
| Model | 理解与生成 | GPT/Claude/GLM |
| Harness | Agent 运行环境（prompt/tools/loop/translation） | Hermes/Pi/OpenCode/OpenClaw |
| **交互协议** | **Agent↔人（可视/质疑/打断）** | **AG-UI（本篇）** |
| 工具协议 | Agent↔工具/数据 | MCP |
| 协作协议 | Agent↔Agent | A2A |

**Harness 管运行，AG-UI 管呈现，MCP 管手，A2A 管同事**——五层栈齐了。OpenBot 之所以"works with ANY agent harness"，正是因为它卡在 harness 之上的交互层，不与 harness 竞争而是承接所有 harness。

### 3.3 设计哲学速查

| 设计 | OpenBot 选择 | 反面（主流做法） |
|------|------------|----------------|
| 权限失败时 | fail-closed（不返回） | fail-open（尽量给答案） |
| 模型降级 | 显式不可用 | 静默 fallback |
| 人机并发 | 拒绝 Bot 动作 | 排队重放 |
| UI 生成 | 白名单组件 | LLM 自由生成 |
| 部署 | 单租户自有设施 | SaaS 共享租户 |
| 数据 | 全在自有 Postgres | 厂商云端 |

一以贯之的原则：**企业场景宁可不可用，不可不受控**。

### 3.4 关键细节的匠心（容易被略读略过的）

1. "人操作期间 Bot 动作被拒绝而非排队"——人机冲突的最优解，值得所有 computer-use 产品抄
2. "密钥用你的 KEK 加密，never returned, never logged"——凭证治理的教科书表述
3. "检索 fail-closed + deny wins + 模糊不返回"——把权限模型做进检索层的完整表述
4. "Full data recording, owned by you"——全程记录+数据主权，呼应昨日笔记"session 所有权"主题
5. agents.yaml 配置化新增同事——Bot 的边际成本趋零（对照：招一个真员工 vs 写一段 YAML）

---

## 四、趋势判断

### 4.1 "三协议栈"正在成为 agent 基础设施的共识分层

MCP（Anthropic）/A2A（Google）/AG-UI（CopilotKit）三家分治的格局若稳定下来，等于 agent 世界的 TCP/IP 分层时刻——**每层都可以独立创新和替换**。判断：2026-2027 年"是否说 AG-UI"会成为 agent UI 工具（如 assistant 前端、copilot 面板）的兼容性分水岭，正如 2025 年"是否支持 MCP"成为工具生态分水岭。

### 4.2 Computer use 的企业化落地要靠"容器+登录态+接管"三件套

OpenBot 的每 Bot 一容器+真实登录态+take the wheel 是 computer use 从演示到企业落地的最短路径——**不是把浏览器做得更智能，而是把人的监督成本降到最低**。判断：next 12 个月企业内部"Bot 员工化"部署的最大瓶颈不是模型能力而是 IT 安全审批，OpenBot 式的安全预答题设计会成为标配。

### 4.3 生成式 UI 的务实路线：白名单组件流将胜出

"LLM 自由生成 UI"在企业场景已死（不可审计）；白名单组件流（LLM 选组件+填参数）+沙箱发布通道是可治理的中间态。判断：**组件市场会成为 agent 生态的新资产类别**——正如 Pi 的 5000+ extensions，OpenBot 的组件也会走向社区共享。

### 4.4 开源替代的速度在加快：Grok Bot 发布到开源复刻的周期

Grok Bot（xAI）2026 年发布，OpenBot 数周内开源复刻——**闭源 agent 产品的护城河窗口期在缩短**。判断：agent 产品的可持续差异化在**数据飞轮+垂直场景深度+合规资产**，不在交互形态本身（交互形态会被开源快速抹平）。

---

## 五、关联分析

### 5.1 与昨日 Harness 笔记的关联（承接）

- [2026-08-21-什么是AgentHarness](2026-08-21-什么是AgentHarness-从攀岩安全带到四组件解剖.md)：OpenBot 是 harness 之上的交互层——**"works with ANY agent harness" 正是翻译层中立性（昨日笔记组件 IV）的外化**：harness 中立=承接所有 harness
- Pi 的 5000+ extensions 与 OpenBot 的组件沙箱都是"**可拥有可改造**"哲学的实例——两篇笔记共同指向"agent 基础设施的主权化"浪潮

### 5.2 与 Hermes 的对照（自反性）

| OpenBot 概念 | Hermes 对应 |
|-------------|------------|
| Channel per agent（频道化同事） | Topic-Session 管理 + 多平台会话隔离 |
| agents.yaml 配置化角色 | team-roles 技能（Dev/OPM/Content/Data Meow）+ AGENTS.md |
| Skills 双级治理 | 个人 skills 目录 + 共享 skills + curator adopt 机制 |
| Computer use 容器 | browser_use 会话隔离（session 参数） |
| 人机接管（take the wheel） | steer-hook 技能（用户中途介入）+ OUT-OF-BAND 消息机制 |
| Full data recording | state.db 会话本地存储 + session_search |
| Fail-closed 检索 | （待补）Hermes 无强制 fail-closed 权限层——差距点 |

**差距清单**：OpenBot 的 fail-closed 检索权限、组件调用三重校验、人机冲突拒绝协议是 Hermes 当前没有的企业级设计——可作为演进参考。

### 5.3 与科研方法论笔记（fuzz testing）的关联

- AG-UI 事件流的 StateSnapshot/StateDelta 与 research-fuzzer 的 notebook（append-only 记录）同构——**都是把过程状态外化成可观测流**："work is visible rather than something you are told about afterwards" 与 fuzz 面板的"make partial understanding observable"是同一原则在 UI 层与科研层的投影
- "人能打断"（interrupt 事件）对应科研中的 kill-shot bet——**外部质疑通道是可信度的来源**

### 5.4 与飞机结构七部曲的有限关联（点到为止）

- 七部曲④论证篇的 ASIB（结构智能大脑）多 Agent 架构与 OpenBot 的"频道化 AI 同事"在**组织形态**上同构（诊断/飞控/运维 Agent ≈ 数仓分析师/工具操作员/收件箱分拣）；"每个 Bot 一台电脑"的安全隔离哲学与④的六级 V&V 中"验证环境与生产环境隔离"同源——但两者无直接技术依赖，是设计原则的跨域共鸣

---

## 六、金句摘录

> "An agent is a role, not a chatbot."（Agent 是角色，不是聊天机器人。）

> "It is the leg the other two do not cover."（AG-UI 是另外两条腿不覆盖的那条。）

> "The work is visible rather than something you are told about afterwards."（工作可见，而非事后被告知。）

> "The reason most AI pilots stall is not the model. It is that nobody can say where the data went."（多数 AI 试点失败不是因为模型，而是没人说得清数据去了哪。）

> "Nothing silently falls back to somebody else's LLM."（绝不静默降级到别人家的 LLM。）

> "Permissions are fail-closed... When permissions are unclear, it returns nothing rather than guessing."（权限 fail-closed；权限不清时返回空，而不是猜。）

---

## 七、拓展应用推荐

- **三协议栈概念卡（P1）**：MCP/A2A/AG-UI 分层表做成一页概念卡，与昨日 Harness 四组件卡合并成"Agent 基础设施五层栈"专题——后续讨论 agent 架构的基础引用件
- **人机冲突协议吸收（P2）**：把"人操作期间拒绝 Bot 动作而非排队"写入 computer-use 类技能的 pitfalls——本机 browser_use 若有人工介入场景可参考
- **Fail-closed 权限层评估（P2）**：对照 OpenBot 六条安全设计做 Hermes 的差距清单——检索权限/组件校验/凭证治理三项是本机短板，评估补齐成本
- **OpenBot 源码学习清单（P3）**：repo（copilotkit.ai/openbot 页脚）重点读 supervisor 容器编排、AG-UI 事件流实现、权限归一化（allow/deny principals）三块

---

## 八、指南分析

**开源替代产品的评估方法论（本篇 @shao__meng 推文+产品页的工艺）**：

1. **先定位生态位再看产品**：推文第一层是三协议框架（MCP/A2A/AG-UI）——**先给地图再给景点**，OpenBot 的价值在地图上立刻可读（AG-UI 参考实现）
2. **"抱着学习的目的"**：对开源替代品的务实姿态——不吹可用性，先学设计（容器/登录态/接管/白名单 UI）
3. **产品页的"安全评审预答"结构**：把 CISO 会问的六个问题预先答完（数据去哪/密钥谁持/降级策略/权限模型/调用记录/部署形态）——**B 端产品的文档即销售**
4. **协议>产品的卡位叙事**：CopilotKit 的核心资产不是 OpenBot 而是 AG-UI 协议本身——"we wrote it, we maintain it, we ship the reference implementation"（标准+参考实现+产品三件套是基础设施公司的经典打法，对照 Anthropic 之于 MCP）

**阅读指南**：推文 3 分钟+产品页 5 分钟即可；笔记 3.2 节的五层栈视图和 3.4 的五个匠心细节是本篇核心增量；与昨日 Harness 笔记连读形成完整栈图景。

---

## 九、行动启示（可学到的点）

- **可学到 1——三协议分层地图**：MCP=手（工具）、A2A=同事（协作）、AG-UI=脸（交互）——讨论任何 agent 系统先问"这条腿谁覆盖"，避免框架混淆
- **可学到 2——Bot 即角色+最小权限**：agent 的组织学（频道/名称/职责/最小授权）比 agent 的智能更重要——"是配置而非代码"让角色边际成本趋零
- **可学到 3——人机冲突的拒绝语义**：人接管时拒绝 Bot 动作而非排队——并发控制的通用原则（陈旧上下文的动作重放是事故之源）
- **可学到 4——fail-closed 优于 fail-open**：企业场景权限不清时返回空、不捆绑模型、不静默降级——**三个"不"比一百个功能值钱**
- **可学到 5——可见性即信任**：屏幕实时展示+来源引用+全程记录——"能看见"是 agent 获得人类信任的最短路径，比提高准确率更直接
- **可学到 6——协议卡位战略**：产品会过时、协议会长存——写协议+维护标准+出参考实现是基础设施公司的三件套打法

---

## 十、出处

- **推文**：https://x.com/shao__meng/status/2090348345802002842（meng shao，2026-08-20 16:00，1.1K views，中文解读）
- **产品页**：https://copilotkit.ai/openbot（CopilotKit 官方，4.1K 全文）
- **原推**：@ataiiam（Atai Barkai，CopilotKit 团队，2026-08-19 发布）
- **关联协议**：AG-UI（ag-ui.com，CopilotKit 发起维护）、MCP（Anthropic）、A2A（Google）
- **抓取链路**：web_extract 432 → Playwright headless 渲染推文（正文+引用原推 2.9K）→ r.jina.ai 拉产品页 4.1K → 整理
- **连续阅读**：本笔记与 [2026-08-21-什么是AgentHarness](2026-08-21-什么是AgentHarness-从攀岩安全带到四组件解剖.md) 构成 agent 基础设施连续篇——Harness（运行层）+ AG-UI（交互层），建议连读

## 相关笔记

- [什么是 Agent Harness](2026-08-21-什么是AgentHarness-从攀岩安全带到四组件解剖.md) — Harness 概念搭档，连读
- [Agent 记忆与自进化架构 2026 前沿](2026-08-21-Agent记忆与自进化架构2026前沿-超图技能库分段固化与在线Harness编译.md) — AG-UI/HyperSkill 学术层对照
- [Agentic Zero Trust](explore/2026-08-21-网络安全-Agentic-Zero-Trust.md) — Agent 安全治理层；OpenBot 治理落地参照

→ 相关：[[2026-09-01-GrokBot25核心概念全解析-Bot本体运行环境能力协作控制权.md]]（Grok Bot 平台概念全景，与 OpenBot 篇构成内外视角）
