# What is a Harness？——从攀岩安全带到 Agent Harness 的完整解析

> **来源**：X/Twitter @shao__meng 推文（中文解读）→ Earendil 博客原文
> **原文链接**：https://x.com/shao__meng/status/2090461025032392844
> **配套材料**：
> - Blog 原文：https://earendil.com/posts/what-is-a-harness（Earendil 联合创始人 Colin Raymond 著，2026-08-20 前后发布，10.4K 字符全文已取）
> - Pi 官推 @pidotdev 同步发布（1.2K views）
> **记录日期**：2026-08-21

**标签**：#AgentHarness #系统提示词 #AgenticLoop #翻译层 #开源中立 #用户主权 #Pi

---

## 一、内容详细整理

### 1.1 词源隐喻：攀岩安全带

作者 Colin Raymond 从剑桥词典的 harness 定义出发（名词：用于控制或固定人/动物/物体的带具；动词：控制某物以利用其力量），引入中学攀岩回忆——**安全带（harness）支撑你、保护你**：连接主锁与绳索、防坠、调节节奏、约束路线；还能挂载粉袋、岩塞、快挂等工具。

攀岩安全带与 agent harness 的三点同构：

1. **支撑与安全**：harness 承托模型运行，提供防坠机制（约束框架）
2. **工具挂载**：gear loops = tools，可按地形换装
3. **可携可改**：换一座山同一个带；杂技演员和树艺师也用——**归主人所有、可个性化改造**

> "This was written for those who may be curious to know what an agent harness is, but don't, and have been too embarrassed to ask."（写给那些好奇但不好意思问的人。）

### 1.2 核心命题

- **Agent = Model + Harness**——这个公式被喊滥但方向正确（Pi 团队承认"过于简化"）
- Model 负责理解和生成；**真正让它能"做事"的是 Harness**
- 定义：**agent harness 是一段软件，为 AI 模型提供运行环境**
- 与多数 AI 软件不同：**终端用户可以拥有自己的 agent harness**（模型不可拥有，harness 可拥有）
- 交互形态：软件工程师用 Terminal 直连（如 Pi）；也有 iMessage/聊天 app/邮件形态（OpenClaw）；Earendil 的 Lefos 主要通过邮件交互

### 1.3 四个组成部分（Harness 的解剖学）

**I. System Prompt（系统提示词）**

- 模型自带训练阶段内化的规则（Claude Opus 4.5 的 "soul document" 最著名——告诉模型它是什么、该如何行动）
- Harness 的 system prompt **不那么内嵌**——"更像新员工入职第一天拿到的操作手册：尚未内化，但工作时须遵循"
- 随每次对话注入，约束模型在该 harness 语境下的行为

**II. Tools（工具）**

- 用代码实现、可供模型"调用"的能力：WebSearch、WriteCode、ComposeEmail
- Harness 既**描述**工具，也**提供实现**
- 关键设计哲学：**harness 通常不规定何时使用哪个工具**——把工具摆好、讲清楚，由模型自行判断调用时机与方式

**III. Agentic Loop（智能体循环）——行为骨架**

以"对比本地小学排名与成绩并给建议"为例（邮件型 harness + 三工具）：

```
1. 理解请求 → 用预训练权重理解"小学/本地/排名"
2. 构造搜索查询 → WebSearch 取数
3. 自评结果：不足 → 自行决定再搜（第一次"循环"）
4. WriteCode 生成电子表格（所有表格皆代码）、算数、格式化
5. 对照原始请求自检：不满意 → 回到搜索（再次"循环"）
6. 满足 → ComposeEmail：总结+写邮件+附表格
7. 自审完成 → 循环关闭 → 用户数秒内收到邮件
```

- **"loop"的本质**：模型基于**自己的评估**决定再次调用工具——这是 agentic 区别于一次性问答的核心
- 模型自主决定是否重做、何时收尾

**IV. Translation Layer（翻译层）**

- 让同一套 harness 对接不同厂商模型（Anthropic / OpenAI / 开源权重模型）
- 价值两层：
  1. **能力组合**：同一次 agentic loop 中按任务特长混用不同模型
  2. **用户主权**：把议价权和选择权从 AI 实验室转移到终端用户——同一请求可分别发给三家模型，比较结果与成本，**所有会话保留在本地一份副本**，而非散落在三个 app

### 1.4 Making a Harness Yours（拥有你的 Harness）

- Pi 是极简 agent harness：system prompt 短、工具集最小、开箱即"让路"（get out of the way）
- 用户在使用中扩展和塑形：改 system prompt、为工作流设计 extension
- **Pi 用户已共享 5000+ extensions**；免费开源、跑在自己笔记本上——"人们拥有了一个属于自己的、跑在自己硬件上的、驾驭 AI 的工具"

### 1.5 中立开源 Harness 作为能动的工具

- **Harness 起源并不中立**：第一个流行 harness **Claude Code** 不是为无偏翻译层而生，而是"在本地用 Claude 模型写代码"的应用
- 此后开源中立 harness 兴起：**OpenClaw、OpenCode、Hermes、Pi**
- Earendil 的立场：不回避技术——"**我们挥舞锤子，而不是让锤子挥舞我们**"（wield the hammer, the hammer does not wield us）

---

## 二、查询拓展

### 2.1 Claude Opus 4.5 "soul document" 事件

原文引用的 gist（Richard-Weiss 泄露）是 2026 年 Claude Opus 4.5 系统提示词泄露事件的存档—— Anthropic 把模型身份、行为准则、写作风格写成一份长文档内嵌训练。该事件引发了"模型人格是训练出来的还是提示词写出来的"的讨论。原文用它的意义在于**区分两层规则**：soul document=训练内化（换 harness 仍在）；harness system prompt=外挂操作手册（每次对话注入）。这个区分对理解"同一个模型在不同 agent 产品里表现迥异"是关键。

### 2.2 四大开源中立 Harness 横评（原文点名的四家）

| Harness | 定位 | 备注 |
|---------|------|------|
| **OpenClaw** | 多平台聊天形态（iMessage/聊天app/邮件） | 原文归类为 UI 多形态代表 |
| **OpenCode** | 终端编码 | |
| **Hermes** | 多平台网关型（飞书/微信/Telegram…） | **即本助手自身运行的环境** |
| **Pi** | 极简终端 harness（Earendil 出品） | 5000+ extensions、免费开源、本地运行 |

有意思的是原文把 **Claude Code 定性为"第一个流行 harness 但不中立"**——绑定 Anthropic 模型的应用，而非可换模型的翻译层。这个叙事框架（Claude Code → 开源中立浪潮）是 Earendil 的竞争定位话术，但也符合行业演化事实。

### 2.3 "Agent = Model + Harness" 公式的谱系

这个公式在 2025-2026 年被反复提出（Sholto Douglas/Trenton Bjori 等的访谈、各家 agent 公司博客）。批评视角：①过于简化（忽略记忆系统/评估层/安全护栏）；②harness 内部复杂度被低估（本机 Hermes 的 skill 体系、cron、multi-agent 编排都超出四组件模型）。Pi 团队自己也承认"太过简化，但方向是对的"。**四组件是教学模型，不是工程完备清单**。

### 2.4 Translation Layer 的技术形态

跨厂商翻译层的工程实现：①API 协议适配（OpenAI-compatible endpoint 已成事实标准，各家 provider 套壳兼容）；②工具调用格式转换（function calling schema 差异）；③上下文窗口/系统提示词裁剪（不同模型的 prompt 特性差异）；④成本路由（按 cost-per-task 选模型——原文特别提到 open weight 模型的"great value-for-money"）。本机 Hermes 的 model-fallback-chain（zai→sensenova 链）就是翻译层+成本路由的实例。

### 2.5 "Session 所有权"的隐议题

原文"keep local copies of the sessions that over time will constitute their correspondence with machines"——**会话历史 = 人与机器的通信档案**，归属权应在用户。这与本机实践（session.db 本地存储、session_search 全文检索）一致。反例是云端 app 的会话锁定效应。这个议题在 agent 时代会越来越重：会话不仅是隐私，更是**可检索的个人知识资产**。

---

## 三、归纳总结

### 3.1 一句话结论

> **Agent Harness 是让 Model 变成 Agent 的运行环境软件——由 system prompt（操作手册）、tools（工具挂载）、agentic loop（行为骨架）、translation layer（跨厂商翻译）四件套构成；它可拥有、可改造、可本地运行，开源中立 harness（OpenClaw/OpenCode/Hermes/Pi）正在把"用谁的模型、数据留在哪"的选择权从 AI 实验室还给终端用户。**

### 3.2 四组件速查表

| 组件 | 类比（攀岩） | 本质 | 关键设计哲学 |
|------|------------|------|------------|
| System Prompt | 上墙前教练叮嘱 | 每次对话注入的行为手册 | 不内化于模型，harness 语境专属 |
| Tools | gear loops 上的装备 | 代码实现的可调用能力 | 不规定何时用——模型自主判断 |
| Agentic Loop | 攀爬节奏本身 | 评估→再调用→自审的循环 | 自评驱动的重做/收尾决策 |
| Translation Layer | 换山不换带 | 跨厂商模型适配 | 能力组合+用户主权双价值 |

### 3.3 本文在 harness 话语谱系中的位置

- **科普定位**：写给"好奇但不好意思问的人"——不是技术深水文，是**概念普及文**
- **竞争定位**：Earendil（Pi 母公司）联合创始人执笔，结尾自然引向 Pi 的 5000+ extensions——**软广与科普的边界处理得当**（先立概念再谈产品）
- **历史定位**：把 Claude Code 定性为"第一代不中立 harness"、把 OpenClaw/OpenCode/Hermes/Pi 列为"开源中立浪潮"——**为 harness 的演化史给出了一个 vendor 视角的分期框架**

---

## 四、趋势判断

### 4.1 Harness 正在成为独立的价值层

公式 Agent = Model + Harness 的隐含推论：**模型层的差异化在收窄（前沿模型能力趋同），harness 层的差异化在放大**（工具生态、循环设计、翻译层质量、扩展市场）。Pi 的 5000+ extensions 与 Claude Code 的 plugin 生态都是这个判断的证据。2026-2027 年 harness/工具生态的竞争权重会继续上升——**"模型是引擎，harness 是整辆车"**，用户买的是车不是引擎。

### 4.2 "中立性"将成为 harness 的核心卖点与审查标准

原文把 Claude Code 的"绑定单一厂商"定性为历史局限——这个叙事会扩散。判断：**中立性（模型可换、协议开放、本地运行）会从加分项变成 harness 品类的准入门槛**。同时"中立"声明需要验证：真正的中立=翻译层无性能惩罚+模型切换无功能损失。用户会越来越精于分辨"真中立"与"名义中立"。

### 4.3 Session 所有权与本地优先会汇成隐私合规议题

"与机器的通信档案归用户所有"这个视角，在 GDPR/数据可携带权框架下有法理支点。判断：**会话导出/本地存储/跨 harness 迁移**会在 2027 年前后成为 agent 产品的合规要求与选型标准——类似浏览器书签导出的"数据可携"惯例。

### 4.4 Harness 概念正在外溢出编码场景

原文强调 harness "first application was for coding"但"Now sit at the core of all types of AI agents"——邮件（Lefos）、消息（OpenClaw）、多平台网关（Hermes）。判断：**垂直场景 harness**（科研 harness、量化 harness、CAD harness）是下一波——七部曲研究的"飞机结构智能体"本质上是**航空工程垂直 harness** 的愿景（感知工具+力学世界模型+决策循环+适航约束的四个组件映射）。

---

## 五、关联分析

### 5.1 与 Hermes（本助手自身）的镜像关系

这篇笔记的特殊性：**本助手就是文中四组件的活体样本**——

| 原文组件 | Hermes 对应 |
|---------|------------|
| System Prompt | 本会话 system prompt（MeowBot soul + 用户偏好 + AGENTS.md 注入） |
| Tools | 80+ 工具（terminal/browser/web_search/lark 全家桶…） |
| Agentic Loop | 每条消息的"理解→工具调用→自评→再调用→交付"循环 |
| Translation Layer | zai/sensenova 多 provider + model-fallback-chain + model-switch 技能 |

Hermes 被原文点名为"开源中立 harness"四家之一——**本笔记是 harness 写的关于 harness 的笔记**，自指结构完整。

### 5.2 与 skill 体系的关系

- **Skills = harness 的"可改造性"实例**：原文"change the system prompt, or design an extension"在 Hermes 的对应物是 skill_manage/skill_view 体系——技能即扩展，5000+ Pi extensions 与本机 300+ skills 同构
- **Agent-optimization 类技能**（adaptive-tool-selection 等）本质是在优化 agentic loop 的工具选择效率

### 5.3 与科研方法论笔记（fuzz testing）的关联

- research-fuzzer 的五规则（bet/settle/doors/gate）是**往 agentic loop 里注入科学方法的 harness 扩展**——证明 loop 是可编程行为骨架，不只有"搜索→代码→邮件"一种模式
- "translation layer 能力组合"（同一 loop 混用多模型）与 fallback-chain 的模型分工（贵模型做推理/便宜模型做格式化）互相印证

### 5.4 与飞机结构七部曲的关联（点到为止）

七部曲⑤宣讲版的"具身结构认知体"三层架构（SNN 感知→力学世界模型→多 Agent 决策）映射到 harness 四组件：**智能蒙皮+相控阵=Tools，力学世界模型+EDL=System Prompt 级约束，诊断-飞控-运维循环=Agentic Loop，多专业模型调度=Translation Layer**——"飞机结构智能体"可重新解读为"航空结构的垂直 harness"。这是原文 4.4 趋势判断的领域实例，非强行映射。

---

## 六、金句摘录

> "Agent = Model + Harness."（方向对但过于简化。）

> "It's more like a set of instructions a new employee might get on their first day of a job."（system prompt = 入职第一天的操作手册。）

> "The harness usually does not dictate when and how the AI model should use the tool."（harness 摆好工具讲清楚，何时用模型自己定。）

> "This decision to call the tool again based on its own assessment is the first clear example of the 'loop'."（基于自评再次调用工具，就是"循环"的第一个清晰例证。）

> "Keep local copies of the sessions that over time will constitute their correspondence with machines."（会话是与机器的通信档案，应留在本地。）

> "Ensuring that we wield the hammer, the hammer does not wield us."（确保我们挥舞锤子，而不是让锤子挥舞我们。）

---

## 七、拓展应用推荐

- **Harness 概念卡片（P1）**：四组件表 + 攀岩类比可做成一页概念卡，纳入"AI Agent 架构"主题笔记索引——后续遇到 harness 相关讨论（如 Agent 三原语架构技能）直接引用
- **中立性验证清单（P2）**：为 harness 选型（个人或团队）设计验证清单：模型切换无功能损失？会话可导出？扩展生态活跃度？本地运行可行性？——可发展为独立评估技能
- **垂直 harness 趋势跟踪（P2）**：跟踪科研 harness（ARA）、编码 harness（OpenCode/Claude Code）、航空 harness（七部曲愿景）的演化——"harness 外溢到垂直行业"是 2026-2027 的结构性机会
- **Session 资产化实践（P3）**：定期导出高价值会话摘要到笔记体系（现有 session_search+note 流程已部分实现），强化"通信档案"的检索资产属性

---

## 八、指南分析

**科普文+软广的写作工艺（本篇方法论价值）**：

1. **词源隐喻先行**：从剑桥词典+攀岩回忆切入，把抽象软件概念锚定在身体经验（安全带承托/挂工具/可改造）——概念普及的第一杠杆
2. **四组件教学模型**：把复杂系统砍到四个可记忆的组件，每个配一个具体例子（soul document/三工具/小学排名案例/换模型）——**教学模型的完备性让位于可记忆性**，且作者明示"过于简化但方向对"
3. **场景走查代替抽象定义**：agentic loop 一节用完整案例（6 步循环）走一遍，让读者"看见"循环——比任何定义都有效
4. **软广的自然收口**：概念讲完才出现产品（Pi 的 5000 extensions），且放在"可拥有可改造"的论证需要处——**产品是论据而非主角**
5. **价值观收尾**："挥舞锤子"的能动性宣言把技术选择上升为立场——给读者一个可以站队的叙事

**阅读指南**：正文 10K 八分钟读完；四组件各取一句哲学句即可；与 @shao__meng 中文推文对照读（推文是忠实压缩版，加了一句 Pi 团队"公式过于简化"的自评，是原文没有的增量）。

---

## 九、行动启示（可学到的点）

- **可学到 1——两层规则的区分**：模型内化规则（训练出来，随模型走）与 harness 注入规则（每次对话，随环境走）——解释"同一模型不同产品表现迥异"，设计 agent 行为时先想清楚规则该放哪层
- **可学到 2——工具摆好不规定用法**：harness 的设计哲学是"描述清楚+自主判断"，不是 if-else 编排——过度规定调用时机的 harness 会压制模型的 agentic 能力
- **可学到 3——循环的判据是"自评驱动的再调用"**：判断一个系统是不是 agentic，看它的重做决策是外部脚本还是模型自评——自评驱动=真 agentic
- **可学到 4——翻译层=主权层**：模型可换不只是省钱，是把议价权从实验室移到用户——选 harness 时翻译层质量（无惩罚切换/成本路由/能力组合）是核心指标
- **可学到 5——会话即资产**：与机器的通信档案长期看是个人知识资产，本地副本+可导出+可检索是资产化的三条件
- **可学到 6——可拥有性是 harness 品类的本质差异**：模型不可拥有（权重在实验室），harness 可拥有（跑在自己机器）——这个不对称性是"harness 主权叙事"的根基

---

## 十、出处

- **推文**：https://x.com/shao__meng/status/2090461025032392844（meng shao，2026-08-20 23:28，1.2K views，中文解读）
- **Blog 原文**：https://earendil.com/posts/what-is-a-harness（Earendil 联合创始人 Colin Raymond 著；Pi 官推 @pidotdev 同步宣发）
- **关联实体**：Pi（pi.dev，极简开源 harness，5000+ extensions）；Lefos（Earendil 邮件型 harness）；OpenClaw/OpenCode/Hermes（开源中立 harness 同列）；Claude Code（被定性为第一代不中立 harness）；Claude Opus 4.5 soul document（gist 泄露存档）
- **抓取链路**：web_extract 432 → Playwright headless 渲染推文页（正文+引用推+评论区 3.9K）→ r.jina.ai 拉取 blog 全文 10.4K → 逐节整理
- **特殊标注**：Hermes（本助手运行环境）被原文点名为四大开源中立 harness 之一——本笔记为"harness 内部对 harness 概念的自反性整理"

## 相关笔记

- [OpenBot/AG-UI 协议](2026-08-21-OpenBot开源GrokBot与AGUI协议-三协议生态位.md) — Harness（运行层）+ AG-UI（交互层）连续篇
- [Agent 记忆与自进化架构 2026](2026-08-21-Agent记忆与自进化架构2026前沿-超图技能库分段固化与在线Harness编译.md) — 在线 Harness 编译学术版；本笔记为工程概念版
- [Agentic Zero Trust](explore/2026-08-21-网络安全-Agentic-Zero-Trust.md) — Agent 安全治理层，Hermes 作为中立 harness 的治理语境
- [GPT+Fusion MCP](2026-08-21-GPT加FusionMCP-真正构建编辑CAD模型的AI.md) — Harness 操作垂直工具的实例
