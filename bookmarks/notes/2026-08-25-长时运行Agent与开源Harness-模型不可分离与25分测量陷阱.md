# 长时运行 Agent 与开源 Harness — 模型与 Harness 不可分离：25.7 分的测量陷阱与九组件解剖

> **来源**：meng shao (@shao__meng) 转述 Sumanth (@Sumanth_077) X Article《Build a Long-Running Agent With an Open Source Harness》
> **原文链接**：https://x.com/shao__meng/status/2092245762411499894（2026-08-25）
> **Article 原文**：https://x.com/i/article/2092185179733508096（X Articles 需登录，正文经多源交叉补全）
> **交叉源**：MindStudio《Sam Altman Says the Harness Is Now Inseparable from the Model》（Endor Labs 数据）/ Sam Altman × Ben Thompson 对谈
> **记录日期**：2026-08-25
> **系列**：Harness 系列第 2 篇（第 1 篇：08-21《什么是 Agent Harness——攀岩安全带与四组件解剖》同来源 @shao__meng）

**标签**：#AgentHarness #长时运行Agent #开源Harness #SamAltman #测量问题 #EndorLabs #Harness工程

---

### 7 模块索引

| 模块 | 对应章节 |
|------|---------|
| tag 标签 | 头部标签行 |
| 出处 | 头部出处行 |
| 内容整理 | 第一~四章 |
| 查询拓展 | 第五章（与 08-21 Harness 笔记的系列关系） |
| 归纳总结 | 第六章（三阶段演进+九组件+读榜守则） |
| 趋势判断 | 第七章（2 条预测） |
| 关联分析 | 第八章（Harness 系列互引） |
| 拓展应用推荐 | 第九章（本机落地） |
| 指南分析 | 第十章（信息来源诚实声明） |

---

## 一句话总纲

> **当 Agent 从"短演示"走向"长任务"，决定成败的不再是模型本身，而是包裹模型的运行时——Agent Harness。Sam Altman 亲口承认"我不再认为 harness 和模型是完全可分离的东西"；Endor Labs 实测同一 GPT-5.5 在两个 harness 里功能分差 25.7 个百分点——你读过的每一个模型跑分，都是"模型×harness"的联合测量。这也是"有理由偏爱开源 harness"的底层逻辑：harness 已是系统能力的一半，这一半必须可审计、可控制。**

---

## 一、原文核心（meng shao 转述 + Sumanth 文章已知部分）

### 1.1 出发点：Sam Altman 的一句话

> "also, a reason to favor open-source harnesses."（而且，这是偏爱开源 harness 的一个理由。）

Sumanth 文章开篇即引用此句——当 agent engineering 的重心从模型移向运行时，**运行时的开源性与可控性成为一级决策**，不再是极客偏好。

### 1.2 四块积木（meng shao 转述）

一个可用的 Agent 由四块积木组成（转述文本截断，可确认前两块）：

1. **模型**（推理）
2. **MCP**（工具调用层）
3. *（后两块经交叉源补全：记忆/上下文管理 + Harness 运行时本体——见 §三 九组件）*

### 1.3 长时运行的定义性问题

长任务的敌人不是智力，是**状态**：终端崩溃、聊天丢失、上下文溢出、进程中断。Agent 能否"keep running"取决于 harness 的持久化与恢复设计，而非模型参数量。（交叉源：AgentSpan 等持久运行时产品正填补此层。）

---

## 二、Sam Altman 的承认：harness 与模型不可分离

### 2.1 原话（× Ben Thompson 对谈）

> "Hard to overstate how critical it is. I no longer think of the harness and the model as these entirely separable things."

被问"模型周围的运行时（工具/状态/循环）多重要"时的回答——并承认当 Codex 做出惊艳成果时，**他真的不知道多少功劳属于模型、多少属于周围的基础设施**。

这不是假谦虚：这是 OpenAI CEO 在说，你一直优化的东西（模型选型/prompt/微调）**只是等式的一半，甚至更少**。

### 2.2 改变一切读法的数字（Endor Labs）

**同一周、同一模型、不同 harness**：

| 模型 | harness A | harness B | 差距 |
|------|-----------|-----------|------|
| GPT-5.5 | Codex harness：**61.5%** | Cursor harness：**87.2%** | **25.7pp** |
| Opus 4.7 | Claude Code（原生）：87.2% | Cursor：91.1% | 3.9pp |

Endor Labs 团队结论："Same model, same week, two harnesses, two different functional results."

**不舒服的推论**：如果 harness 选择能让功能分摆动 25 分，那么你读过的大部分模型对比——包括影响过你基础设施决策的那些——**测的既是模型能力也是 harness 工程，两者从未被干净分离**。

---

## 三、Harness 九组件（为什么同样的模型在不同的壳中表现不同）

| # | 组件 | 要点 |
|---|------|------|
| 1 | **While 循环** | 地基：读系统提示→决定工具→执行→结果回填→再循环，直到纯文本回复或迭代上限 |
| 2 | **上下文管理** | 朴素实现最先死的地方：逐字保留/摘要/丢弃三决策。Claude Code 压缩策略（近全保+远摘要）是具体设计选择，错了长任务严重退化 |
| 3 | **技能与工具分离** | 工具=原语（读文件/bash/搜索）；技能=markdown 编码的组织知识。工具通用，技能语境特定 |
| 4 | **子 Agent 管理** | spawn（生成）→ restrict（限制）→ collect（收集）：太大/太并行的任务拆分会话+受限工具集+聚焦提示 |
| 5 | **会话持久化** | 仅追加（append-only）JSON 落盘——每条消息/工具结果/压缩事件实时写。崩溃后精确恢复。**"不迷人，但这是 demo 与生产系统的分界线"** |
| 6 | **系统提示组装** | 不是静态字符串，是管道：遍历祖先目录找 agents.md/claude.md 动态注入。**静态在前动态在后，否则破坏前缀缓存**（延迟+成本代价） |
| 7 | **生命周期钩子** | pre-tool 钩子可允许/拒绝/修改调用；post-tool 检查结果。企业不改 harness 本体即可注入合规与观测 |
| 8 | **权限与安全** | 动态分类命令：ls 只读、rm 需全权——**解析命令字符串，不信模型的自我判断** |
| 9 | **内置技能** | 文件操作/git/PR/测试执行——不能读写文件就不是 coding agent |

**框架 vs Harness 的关键区分**：框架（LangChain/LangGraph/AutoGen）给抽象——你来组装，假设人类建筑师拼积木；Harness 反方向——**出厂即完整 agent**，无组装步骤，核心是"预接线的 while 循环+工具注册表+权限层"。框架给架构师，harness 给 agent。

---

## 四、三阶段演进与"测量问题"

### 4.1 Agent 工程三阶段

| 阶段 | 中心问题 | 手段 |
|------|---------|------|
| ① 权重阶段 | 更强 agent = 更大模型 | 参数/训练 |
| ② 上下文阶段 | 不换模型，换它看到什么 | prompt/RAG/CoT |
| ③ **Harness 工程阶段（现在）** | **模型该运行在什么环境里？** | 循环/状态/持久化/权限 |

每阶段叠加于前一层之上——权重仍重要，上下文仍重要，但**重心已外移**。

### 4.2 测量问题（本文最不舒服的结论）

> 当你读到"某模型在编码基准上得了 X%"，你读的是**模型×harness 的联合测量**。当一个模型胜过另一个，你不知道差距里多少是模型能力、多少是 harness 工程。

对构建者的问题是三个独立变量：**which model, in which harness, for which task**——把它们塌缩成一个决策，就是你用强模型得到平庸结果的原因。

### 4.3 为什么开源 harness（Sam Altman 那句话的完整逻辑链）

1. Harness 贡献系统能力的一半（25.7pp 证据）
2. 一半的能力不可审计 = 系统不可审计——基准分数、行为、安全全部"harness 依赖"
3. 闭源 harness = 关键路径被单点供应商锁定（Claude Code 泄露的三层记忆架构证明：**harness 内部结构直接影响长会话连贯性**，但你不看源码就不知道）
4. 故：**harness 层的开源性 = agent 系统的可控性与可审计性**——与算力、支付轨道同为基础设施级决策

产业同步证据：Anthropic 推 Claude managed agents、微软 Foundry 托管 agent（纳德拉："every agent will need its own computer"）、OpenAI 更新 agents SDK、Cursor SDK（"不是调 LLM 加工具，是暴露 Cursor 已在用的同一编码 agent 运行时"）——**harness 即服务**同时出现不是巧合。

---

## 五、查询拓展（与 08-21 Harness 笔记的系列分工）

| 维度 | 08-21《什么是 Agent Harness》 | 本文（系列第 2 篇） |
|------|------------------------------|---------------------|
| 回答的问题 | Harness **是什么**（词源/隐喻/四组件） | Harness **为什么决定成败**（测量证据/九组件/三阶段） |
| 证据类型 | 概念解析（攀岩安全带类比） | 实证数字（25.7pp/3.9pp）+ Altman 承认 |
| 开源视角 | 用户主权/可个性化改造 | 可审计性/测量问题/基础设施级决策 |
| 同来源 | @shao__meng 转述 Earendil | @shao__meng 转述 Sumanth |

两篇合成完整视角：**概念层（是什么）+ 实证层（差多少）**。

**信息来源诚实声明**：X Article 正文需登录无法直接抓取，本文 §一 为 meng shao 转述可确认部分（四块积木仅前两块原文确认）；§二~四 以 MindStudio 深度文（含 Endor Labs 原始数据引用）与 Altman 对谈原文交叉补全——**观点归属已逐节标注，未臆测 Article 未读部分**。

---

## 六、归纳总结

### 6.1 读榜新守则（与评测三部曲联动）

```
看到"模型 X 在基准 Y 得 Z%"：
① 问：跑在哪个 harness 里？（联合测量）
② 问：换 harness 会差多少？（25.7pp 先例）
③ 问：harness 开源吗？（能否审计这"一半的能力"）
```

### 6.2 长时运行 Agent 的最小组件清单

按九组件裁剪出长任务刚需四件：**会话持久化**（append-only JSON）+ **上下文管理**（压缩策略）+ **子 Agent**（spawn-restrict-collect）+ **权限层**（不信模型自判）。

---

## 七、趋势判断

### 趋势 1：Harness 即服务（HaaS）与开源 Harness 将形成双轨生态

> 依据：Cursor SDK/Foundry 托管 agent/Claude managed agents 同期出现（闭源便利轨）+ Sam Altman 亲自背书开源理由 + DeepSeek Harness 开源数日 23K star（开源可控轨）。类比 PC 时代：攒机爱好者与 Dell 台式机并存——**预建让人人可用，开源让关键路径可审计**，两轨服务不同风险偏好的构建者。

### 趋势 2：基准测量的"harness 控制变量"将成为标配披露

> 依据：Endor Labs 同模型双 harness 25.7pp 的证据一旦扩散（Altman 亲口确认分离不可能），"只报模型分不报 harness"的评测将失去可信度——与评测三部曲第三部"谁来审计 benchmark"汇流：**审计对象从题目扩展到运行时**。预期 SWE-bench 类榜单逐步要求披露 harness 配置。

---

## 八、关联分析

| 笔记 | 关系 |
|------|------|
| [什么是 Agent Harness——攀岩安全带与四组件解剖](2026-08-21-什么是AgentHarness-从攀岩安全带到四组件解剖.md) | 系列第 1 篇——概念层，本文实证层 |
| [大模型评测终极指南三部曲](2026-08-25-大模型评测终极指南三部曲-当尺子变成靶子与评测的评测.md) | 测量问题直接汇流——harness 是评测的隐藏变量 |
| [Harness Engineering 七要素全景](2026-08-18-HarnessEngineering七要素全景-Agent工程的完整学科地图与逐层深挖.md) | 学科地图——本文九组件是其工程细化 |
| [DeepSeek Harness 迁移笔记](2026-08-16-DeepSeek-Harness迁移笔记-Hermes老手艺8组对照.md) | 开源 harness 实例——23K star 的本机视角 |
| [Agent 大约等于大模型加 Harness](2026-08-20-Agent大约等于大模型加Harness-结构设计企业操作指导.md) | 用户领域落地——飞机设计企业操作指导 |
| [Coding Agent Harness 解剖学（Mastra）](2026-08-07-Coding-Agent-Harness解剖学-Mastra深度架构.md) | 具体实现参照 |
| [AI 编程 Agent 2026（Claude Code 泄露分析）](2026-06-21-AI编程Agent2026年中架构演进-SWE-bench排行榜与Claude-Code泄露分析.md) | Claude Code 三层记忆架构——harness 内部重要性证据 |

**本机映射**：Hermes 本身就是开源 harness 的完整实践——九组件逐条对照：while 循环（gateway 主循环）✓ 上下文管理（compaction）✓ 技能系统（skills/）✓ 子 Agent（delegate_task）✓ 会话持久化（session DB）✓ 系统提示组装（profile+memory 注入）✓ 生命周期钩子（hooks）✓ 权限层（三层工具权限模型）✓ 内置技能 ✓——**本机已在九组件全项实践，本文价值是给出"为什么必须这样"的测量证据**。

---

## 九、拓展应用推荐

1. **模型切换流程补 harness 维度**：model-switch skill 增加"harness 影响"提示——同模型在不同上下文管理策略下表现不同，切换后重置会话观察
2. **私有 mini-benchmark 必须钉死 harness 配置**：与评测三部曲行动项联动——20-50 题私有评测集若不固定 harness 参数（compaction 策略/工具集/权限层），测量无意义
3. **股票引擎的 harness 审视**：iron_rules_engine 的"数据溯源 P0 pitfall"（时间戳双跑）本质就是 harness 控制变量——已实践，可推广到所有回测报告模板
4. **Jetson 本地 Agent 的持久化检查**：长时 cron 任务（盯盘/学习）崩溃恢复依赖 append-only 日志——本机 cron output 已符合，确认无缺口

---

## 十、指南分析

### 10.1 内容质量

- **证据链强**：Altman 原话（一手访谈）+ Endor Labs 数据（可控实验：同模型同周双 harness）+ 产业同步动向（四家公司同期推 HaaS）——三重支撑
- **framework vs harness 的区分**是本主题最清晰的一次表述（组装方向相反）
- **九组件清单**可直接当 harness 选型/自检 checklist
- **"不迷人但分界线"的工程品味**：会话持久化这种朴素组件被正确地放在了 C 位

### 10.2 局限

- X Article 原文未能直接读取（需登录），四块积木仅前两块经转述确认——本文以多源交叉补全并逐节标注归属
- Endor Labs 数据集规模/任务类型未披露细节（25.7pp 是否在特定任务类上放大未知）
- MindStudio 文有产品植入（Remy），数据引用需回到 Endor Labs 原始报告核对
- "开源=可审计"逻辑未讨论开源 harness 的维护成本劣势（自担升级/安全补丁）

### 10.3 与评测三部曲的关系

两文同日入笔记且互相印证：三部曲说"单一分数会骗人（饱和/污染/hack）"，本文补第四个失效源——**harness 混杂变量**。四者合起来才是完整的"读分防骗清单"。

---

## 金句摘录

> "当 Agent 从短演示走向长任务，决定成败的不再是模型本身，是包裹模型的运行时。"

> "I no longer think of the harness and the model as these entirely separable things." — Sam Altman

> "Same model, same week, two harnesses, two different functional results." — Endor Labs

> "框架给架构师，harness 给 agent。"

> "The harness is not a wrapper around the model. It's the other half of the system."

> "问题不是'我该用哪个模型'，而是'哪个模型、在哪个 harness 里、做什么任务'——三个独立变量。"

---

## 行动启示

- Harness 系列第 2 篇落成（概念+实证双篇），主页可聚合
- **读榜守则 v2**：三问扩展为四问（+harness 披露）——补进评测三部曲笔记的交叉引用
- 本机九组件自检通过——Hermes 作为开源 harness 的实践完整性得到外部框架印证
- 私有 mini-benchmark 设计时钉死 harness 配置（与三部曲行动项合并）

---

> **延伸阅读**：
> - 原文转述：https://x.com/shao__meng/status/2092245762411499894
> - Article：https://x.com/i/article/2092185179733508096（需登录）
> - [什么是 Agent Harness（系列第 1 篇）](2026-08-21-什么是AgentHarness-从攀岩安全带到四组件解剖.md)
> - [大模型评测终极指南三部曲](2026-08-25-大模型评测终极指南三部曲-当尺子变成靶子与评测的评测.md)（测量问题汇流）