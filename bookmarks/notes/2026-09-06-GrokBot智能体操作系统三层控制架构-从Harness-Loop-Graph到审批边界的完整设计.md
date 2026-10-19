# Grok Bot 智能体操作系统解析 — 三层控制架构与十步落地流程

#GrokBot #Grok4.6 #AI智能体 #Harness #智能体循环 #多智能体图 #审批边界 #常驻智能体 #一人公司 #AgentOS

## 出处

- 原文：X Article《The Grok 4.6 model, persistent computer, loops, graphs, routines, and approval system behind agents that finish real work》
- 作者：rari @0xwhrrari（Substack 实践派博主，专注 AI agent/工作流/生产系统拆解）
- 2026-09-03 发布 | 17.3 万浏览
- 提取：fxtwitter blocks（442 块 / 18.6K 字，完整）
- 笔记日期：2026-09-06 | 指令语义：**分析形成笔记**

## 一、内容详细整理

### 1.1 核心命题：产品不是模型，是模型周围的操作系统

> **The product is not the model. The product is the operating system around the model.**

工作单元的迁移：**chatbot 返回答案，Bot 返回完成的工作**（"a teammate that owns a result"）——输出不再是"解释你该做什么的段落"，而是**改变后的 CRM、备好的草稿、复现的 bug、整理的文件夹、更新过的表格**。

五组件分工（原文排比）：

| 组件 | 职责 |
|------|------|
| Grok 4.6 | 推理（the reasoning） |
| Harness | 环境（the environment） |
| Loop | 改进（the improvement） |
| Graph | 协调（the coordination） |
| Approval system | 自治边界（where autonomy ends） |

**反模式开场**（多数人的用法）：建一个 Bot → 给模糊请求 → 连接全部账号 → 等魔法——"把 always-on agent 变成 always-on confusion 的最快方式"。

### 1.2 Grok 4.6：大脑而非全部智能体

- 为长任务智能体训练：**更长的补充训练 + 跨不同 harness 重生 SFT 轨迹 + 跨编码/知识工作/Web 开发/CAD/工具环境的 RL**
- 长工作与单轮聊天**失败方式不同**：跨多动作保持目标 / 决定下一步看什么 / 工具意外输出后恢复 / **测试自己的工作而不是把第一个看起来合理的输出当完成**
- 基准更强（CursorBench/DeepSWE/FrontierCode/APEX-Agents/AA-Briefcase）——但**基准分不决定 Bot 能开哪个账号、不记得审批策略、不保护发布按钮**："The smarter the model becomes, the more important its operating boundaries become."（模型越聪明，运行边界越重要）

### 1.3 一模型三层控制（架构核心）

> 弱系统把模型+三层控制**全塞进一个巨大 prompt**——角色/历史/工作流/审批/检查/重试全在一个 prompt 里。**每次失败看起来都像 prompt 问题，其实不是**：

| 症状 | 真因 |
|------|------|
| Bot 忘记偏好 | **state 问题** |
| 开错工具 | **routing 问题** |
| 发出本该是草稿的东西 | **permission 问题** |
| 重复失败动作 | **loop 问题** |
| 五个 Bot 互相问谁干啥 | **graph 问题** |

> **Better prompts can improve a run. Better architecture improves every future run.**（更好的 prompt 改善一次运行；更好的架构改善所有未来运行）

### 1.4 Layer 1 Harness（环境层）七件事

1. **先给 job 再给 task**：角色描述是**持久基础设施**，下一条消息只是当前任务——混在一起=Bot 每天早上重新学自己的工作
2. **最小可用工具面**：更多权限≠更好 agent，是更大失败面
3. **连接一次、按角色授权**：连接是账号级管道——连过一次，同账号其他 Bot 都可能用它；"一次粗心的连接比一个 Bot 影响更大"
4. **工作存在对话之外**：消息管协调，文件+结构化状态管连续性——"下一个 Bot 应继承**工作的状态**，不是 30 条消息的有损摘要"
5. **共享计算机是特性也是安全边界**（最易被忽略）：多 Bot 共享一个用户级持久计算机（文件/浏览器会话/登录态）——**屏幕不是安全边界，登录态对该账号所有 Bot 可见**；"不要把礼貌的指令当安全控制"——需要不同信任级就分开底层账号/环境/凭证
6. **交接登录态，绝不交接密码**：无 API 的软件走 computer use——Bot 导航到认证墙→暂停→人直接在会话里登录→Bot 从同一状态继续。"chat 是协调面，不是秘密仓库"
7. **审批线按可逆性画**：不看任务大小，看**能否安全撤销**——好运行=可逆步全做完+不可逆步清晰呈staged状态；"Bot 不该因未来某步需要审批就停在 10%，应完成其他 90%、展示确切拟执行动作、停在边界上"

### 1.5 Layer 2 Loop（循环层）

- "keep trying until it works" 不是循环，是"**绑在未定义结果上的无限预算**"——生产级循环五要素（预算/验证器/修复路径/升级路径/硬停）
- **模型选择怎么修局部缺口，harness 决定是否允许再试一次**——防止模型悄悄扩大自己的预算
- **演示变例行（routine）**：Bot 看一遍工作流→存为路径→按需/按计划运行。最佳首个 routine：每周至少重复+跨两个以上工具+稳定可演示+结果可见可验证+最后一步前全可逆
- **验证独立于第一答案**（金句）："Never use one vague prompt for generation and approval"——代码=测试+干净 diff；视觉=截图+清单；研究=信源覆盖+矛盾检查+**论断-证据映射**；运维=变更前后计数。"The loop should move because evidence changed, not because the Bot still feels optimistic."

### 1.6 Layer 3 Graph（图协调层）

- "One Bot is a loop. A team of Bots is a graph."——多智能体并发后**路由比 prompt 更重要**
- **chief（主管）不做每件事**：管 intake/分解/路由/共享优先级/状态/升级；specialist 干车道内的活；群线程收**目标**而非预写任务清单
- 检验标准："如果人还在复制 artifact、指派每一步、告诉每个 specialist 何时开始——那不是协调系统，**只是一堆聊天窗口**"
- **雇专家不雇性格**：五个"smart assistant" 不如五个清晰的**所有权边界**——专业化减少上下文污染+让失败可归因（"specialist 失败时你知道修哪份合同"）
- **传所有权不传转录**：最差多智能体系统把完整对话复制给每个 agent；好的传**紧凑交接包**（handoff packet）——"artifact 载细节、handoff 载状态、thread 载讨论，别让一个巨型上下文窗口当三样"
- **只并行真正独立的工作**："目标不是最大并行度，是**最小的不必要等待**"——有依赖就保边，无依赖才切
- **图变成组织**：路线固化为角色/权限/节奏后，架构"看起来不再像软件，像一家公司"——一人公司配置：chief 收一个目标→分解→路由→追共享截止期→**只在需要人的判断或身份的决策处拉人进来**。"这不是 prompt engineering，是**被编码成图的管理学**"

### 1.7 十步 Grok Bot 操作系统（落地顺序）

1. 从**真实重复工作**开始（可见结果、易判断）
2. 一句话定义角色（"角色需要六个不相关动词=该拆了"）
3. **执行前定义完成**（definition of done 前置）
4. 只连角色所需工具（"不预授权假设性工作"）
5. 演示工作流一次（解释每个判断的原因；首个产出在同线程纠正）
6. 成功路径存为 routine（含输入/输出位置/验证/计划/审批边界）
7. **加自治前先加 checker**（跑几次+同一 rubric 对比，不因成功一次就升级）
8. 限定重试+定义升级
9. **瓶颈出现才加 specialist**（研究/写作分离于上下文变吵时；检查/构建分离于自审变弱时；运维/分析分离于权限分化时——"图应从真实压力生长，不是想看起来复杂"）
10. **每周审计系统**："always-on automation rots quietly"（常驻自动化悄悄腐烂）——站点变/凭证过期/routine 漂移；要每周 receipt+**人抽查一个 artifact**（"Bot 可以总结自己的历史，但不该是唯一裁判"）；三个不舒服的问题→第三个答"否"就删除或重设计。"目标不是积累自动化，是**在不积累隐形失败的前提下移除工作**"

### 1.8 自治阶梯（autonomy ladder）

- 不要从第一条消息跳到无人值守——按**证据背书的等级**晋升，级间移动需要证明
- **降级机制**：routine 退化时**下阶梯**——"Autonomy is a runtime privilege, not a permanent personality trait."（自治是运行时特权，不是永久人格）

### 1.9 三个可抄的生产模式

| 模式 | 流程 | 关键 |
|------|------|------|
| **隔夜研究台** | Scout（只搜批准车道）→ Source Checker（拒无信源主张）→ Cluster Bot（合并重复）→ Brief Bot（写摘要）→ 人早上收一个紧凑审查队列 | 分工+把关 |
| **bug 复现与修复** | 第一个 Bot 只管**复现**（捕获步骤/日志/截图/环境）→ 调试 Bot 才接手 | "防止 builder 修复一个想象中的失败" |
| **带公共闸门的内容系统** | 全部可逆步自动完成 → **公开内容必须审批** → 人审一个包而非管五个 Bot | 可逆性闸门 |

### 1.10 九大失败模式（照录）

1. **一个通才包揽一切**：记忆塞满无关偏好/线程无法审计/权限远超任务
2. **给任务不给完成定义**：Bot 停在"看起来合理"处
3. **每个 Bot 收完整转录**：上下文比有用状态长得快，交接变成"摘要的摘要"
4. **把共享计算机当隔离**：不同 Bot 名字是视觉边界，不是凭证边界
5. **循环没有硬停**：换措辞重试坏路径，成本涨信息不涨
6. **checker=builder 同一上下文**：同样假设存活到评审，"信心变成证据"
7. **一切等审批**：Bot 变成你仍手动管理工作的更慢界面
8. **一切不等审批**：系统能替你花钱/删数据/改生产
9. **routine 从不删除**："最好的自动化组合不是最大的，是**每个 routine 被删掉都会被想念**的那个"

### 1.11 结尾定调

> "未来不属于写出最惊艳答案的模型，属于**能完成工作、证明发生了什么、知道何时停**的系统。"

## 二、查询拓展

- Grok 4.6 官方技术报告：补充训练/SFT 轨迹重生/RL 环境的细节与数据
- Grok Bot beta 的持久计算机规格（虚拟机/容器、隔离模型、账号级凭证共享机制）
- CursorBench/DeepSWE/APEX-Agents/AA-Briefcase 基准具体口径
- 与 Claude Code/Claude Agent SDK hooks、OpenAI Agents SDK 的 approval 流对比
- routine 的可迁移格式（能否导出为类似 AGENTS.md/技能的资产）

## 三、归纳总结

1. **"模型 vs 操作系统"的切分是全文骨架**：Grok 4.6 只是推理引擎——环境/循环/图/审批才是"完成工作"的来源；**产品价值在 OS 不在模型**
2. **五类故障对应五层问题**（state/routing/permission/loop/graph）——**先归层再动手**，prompt 只是其中一层：这条归因表是排查智能体故障的速查卡
1. **审批线按可逆性画**是全文最实用单条：可逆自动跑完、不可逆 staged 停界——既不瘫痪（一切等审批）也不裸奔（一切不等）
4. **共享计算机=便利与风险同源**：登录态是账号级资产，"礼貌指令不是安全控制"——多 Bot 隔离必须落到凭证层
5. **验证独立原则**贯穿：checker ≠ builder（上下文分离）、"loop 因证据变化而推进，不因 Bot 乐观"——与执行/评判分离同构
6. **图层的经济学**：specialist 让失败可归因（修合同）而非可抱怨（骂通才）；传 handoff packet 不传 transcript——**上下文经济学是多智能体的第一约束**
7. **自治阶梯+周审计**：自治是运行时特权（可升可降）；always-on 自动化悄悄腐烂→周 receipt+人工抽查 artifact
8. **反 over-engineering**：第 9 步"瓶颈出现才加 specialist"、"图从真实压力生长"——**先证明单 Bot 可靠再扩张**（Start with proof, not spectacle）

## 三b、与自有 Hermes 体系逐条对照（学习点判定）

> 对照对象：Hermes 架构（Gateway/skills/cron/delegate_task/subagent）、AGENTS.md 准则、既有 agent 架构技能群

| # | 原文主张 | 自有体系现状 | 判定 |
|---|---------|-------------|------|
| 1 | 模型/harness/loop/graph/审批 五分离 | Hermes 已有（provider 层/工具层/cron/delegate/权限三层模型） | ✅ 已同构，验证方向正确 |
| 2 | 五类故障归因表（state/routing/permission/loop/graph） | 散见各 skill，未成速查卡 | ✅ **吸收**：归因表并入 harness-architecture |
| 3 | 审批线按**可逆性**画 | 权限模型按"允许/禁止/确认"分层，未显式引入可逆性轴 | ✅ **吸收**：确认层增加可逆性判据 |
| 4 | 共享计算机≠安全边界（凭证级隔离） | 多 profile 隔离已有；同 profile 内 bot 共享凭证未警示 | ⚠️ **已达标**，补充账号级泄漏警示 |
| 5 | handoff packet ≠ transcript（传状态不传对话） | delegate_task 的 context 一次写透原则 | ✅ 已同构（AGENTS.md"上下文一次性原则"） |
| 6 | 自治阶梯+级间需证明 | delegate/subagent 有粒度但无显式阶梯 | ✅ **吸收**：阶梯概念并入 subtask-lifecycle |
| 7 | 周审计+三问题+删 routine | cron-watchdog 有失败监控；**缺价值审计**（"跑着但没用"检测） | ✅ **吸收**：cron 增加"被删会被想念吗"周问 |
| 8 | 定义完成（DoD）前置 | AGENTS.md 完成定义表（退出码门槛） | ✅ 已同构且更严格（机器可验证） |
| 9 | 最小工具面 | enabled_toolsets 参数已有 | ✅ 已同构 |
| 10 | routine 从不删除=失败 | skill-review 技能已有防僵尸机制 | ✅ 已同构，方向一致 |

**净吸收 4 条**：故障归因速查卡 / 可逆性审批轴 / 自治阶梯 / 周价值审计。已同构 6 条——**Hermes 体系与本文主张重合度极高，属相互印证**。

## 四、趋势判断

1. **"agent OS" 成为 2026 产品竞争主轴**：xAI 把模型+Bot 作为同一 rollout 联合改进——**模型-环境协同进化**取代"模型单点升级"叙事；OpenAI/Anthropic 同路线（Agent SDK/Computer Use），竞争从 benchmark 转向 harness 体验
2. **持久计算机是 agent 的"工作台"标配**：与 chatbot 的本质分野——**状态外置**（文件/会话/登录态）让"隔夜完成"成为可能；传闻中前沿实验室的 48L×2 与此同向：**算力与状态都在往"持续存在"迁移**
3. **一人公司图**会先于企业采用落地：chief+specialist+审批边界的配置对 solo 操作者 ROI 最直接——**管理学被编码成图**是 agent 时代的组织创新
4. **审批经济学成熟**：可逆性轴（非任务大小）会成为 agent 权限设计的行业共识——与 Hermes 权限三层模型可互补融合
5. **反脆弱审计兴起**：always-on 自动化的"静默腐烂"问题催生 receipt+抽查的审计层——**监控（monitoring）之上的价值审计（value audit）**是新层
6. **内容系统公共闸门模式**可复制到笔记/公众号发布管线：全部可逆步自动跑、公开动作过人审——与我们的"笔记上线+线上验证"流程同构

## 五、关联分析

> 关联对象：harness-architecture / agent-orchestration-pattern / subtask-lifecycle / enterprise-agent-governance / watchdog / AGENTS.md / 前苹果设计六技法

1. **与 harness-architecture skill 直接互补**：本文的三层（harness/loop/graph）+审批是六层 Harness 的产品化叙事版本——**五类故障归因表可直并入该 skill 作为排查层**
2. **与 agent-orchestration-pattern 同题**：本文"传所有权不传转录/最小不必要等待"与编排模式的"紧凑交接"原则一致——**handoff packet 概念可加入编排技能**作为标准工件
3. **与前苹果设计六技法（挑刺官）同构**：设计篇"Fresh Context 只看截图不看代码"=本文"checker ≠ builder 同一上下文"——**执行/评判分离在设计与智能体两域的双重验证**（该原则已在 AGENTS.md 准则 2）
4. **与 enterprise-agent-governance 互补**：自治阶梯（evidence-backed levels）是治理框架的运行时版本——**权限分级+证据晋升**可合并为统一治理层
5. **与 watchdog/价值回归原则呼应**：MeowBot 灵魂的"自动化无人用=系统失败"与本文"routine 被删会被想念吗"同一哲学——**周审计三问可直接落地为 cron 检查项**
6. **与 xiaoman 企业知识库交付的"测试集验收"同构**：DoD 前置+机器可验证完成——验收独立于执行者
7. **与 DeepLoop/TwoTower 的对照**（同周笔记）：模型层改进（循环深度/双塔）与系统层改进（OS 三层）并行——**2026 的智能体进步是"模型内+模型外"双线并进**，本文代表系统线

## 六、指南分析

| 场景 | 查哪节 |
|------|--------|
| 快速理解 Grok Bot 架构 | §1.1 五组件 + §1.3 三层 |
| 排查智能体故障 | §1.3 归因表 + §1.10 九失败模式 |
| 设计审批策略 | §1.4-7 可逆性审批线 |
| 设计循环/routine | §1.5 + §1.7 十步 |
| 多 Bot 协作设计 | §1.6 图层 |
| 自治权限管理 | §1.8 阶梯 |
| 借鉴生产模式 | §1.9 三模式 |
| 对照自有体系 | §三b 对照表 |

**核心口诀**：产品是 OS 不是模型 / 五故障五层归因 / 审批按可逆性画 / 传状态不传转录 / 最小不必要等待 / 自治是运行时特权 / 周审计删 routine。

## 七、拓展应用推荐

- **给 harness-architecture**：并入五类故障归因表（state/routing/permission/loop/graph 速查卡）
- **给 subtask-lifecycle / enterprise-agent-governance**：吸收自治阶梯+级间证据晋升+降级机制
- **给 watchdog/cron 体系**：增加"周价值审计"三问（上次人工抽查是什么时候/哪个 routine 被删会被想念/静默失败检测）
- **给 AGENTS.md**：权限三层模型的"确认"层引入可逆性判据（不可逆动作必确认）
- **延伸阅读**：Grok 4.6 技术报告 / Claude Agent SDK hooks / OpenAI Agents SDK guardrails

---

→ 相关：[[2026-09-05-DeepLoop循环Transformer深度扩展-访问对齐系数与残差缩放指数修正.md]]（模型内改进 vs 系统层改进对照）
→ 相关：[[2026-09-05-NVIDIA-TwoTower扩散语言模型-冻结上下文塔与去噪塔的双塔解耦.md]]（同上）
→ 相关：[[2026-09-04-前苹果设计师的AI网页设计六技法-打碎Token平庸惯性的双钻三阶段工作流.md]]（执行/评判分离的设计域验证）
→ 相关：[[2026-09-03-企业AI知识库从0到1真实交付指南-数据治理权限边界与验收的全链路陷阱地图.md]]（DoD 前置+验收独立同构）
→ 相关：自有体系 harness-architecture / agent-orchestration-pattern / subtask-lifecycle


## 相关笔记

- [YC开源QM多人Agent-Harness](./2026-08-02-YC开源QM多人Agent-Harness.md) — 多Agent Harness 另一实现样本
- [前苹果设计师的AI网页设计六技法](./2026-09-04-前苹果设计师的AI网页设计六技法-打碎Token平庸惯性的双钻三阶段工作流.md) — 执行/评判分离的设计域验证
- [企业AI知识库从0到1真实交付指南](./2026-09-03-企业AI知识库从0到1真实交付指南-数据治理权限边界与验收的全链路陷阱地图.md) — DoD 前置+验收独立同构
- [Agent记忆三阶段进化](./2026-09-05-Agent记忆三阶段进化-Storage到Experience与2026基准盘点.md) — 常驻智能体的记忆层配套
- [Karpathy五级阶梯与Graph工程全景](./2026-09-06-Karpathy五级阶梯与Graph工程全景-从LLM到Graph的系统化进路.md) — 同一地图的教育叙事版，两文交叉验证

→ 相关：[Jev-Engineering决策层架构](2026-09-28-Jev-Engineering决策层架构.md)（LLM/JEV/CODE 三层分工与本文 Harness-Loop-Graph 同构互证）
