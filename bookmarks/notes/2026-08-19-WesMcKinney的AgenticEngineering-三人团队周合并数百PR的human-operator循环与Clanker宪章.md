# WesMcKinney的AgenticEngineering — 三人团队周合并数百PR的human-operator循环与Clanker宪章

#AgenticEngineering #WesMcKinney #Kenn #Superpowers #roborev #ClankerConstitution #loop是扯淡 #human-in-the-loop #对抗性审查 #自建工具栈 #Forge #Kata #AgentsView #PR流水线 #code-slop

> **出处**：Wes McKinney 博客《How Kenn is doing Agentic Engineering》（2026-08-12，wesmckinney.com/blog/agentic-engineering-aug-2026/）——pandas 作者、 Kenn Software 联合创始人
> 数据锚点：**3 人团队每周合并数百 PR，百万行生产代码经验性低 bug 率**；作者 30 天 token 消耗按 API 价 $56,836（token leaderboard 常年榜首，靠订阅补贴）
> 主题：反对全自治 loop 的极端立场 + 一套完整的 human-operator 循环工程实践

## 一、内容整理

### 1. 核心立场："I think loops are bullshit"

原推（2026-07-22）+ 本文澄清：

| 层 | 主张 |
|---|---|
| 反对的 | **全自动无人 loop**："agent 相互循环处理输出，你离开键盘，另一端产出高质量结果"——持此论者 a) 无知 或 b) 在卖东西 |
| 不反对的 | **human-operator loops**：人主导的循环（review until converge）——循环里掌握方向盘的是人不是 clanker |
| 背景吐槽 | 被 X/LinkedIn 上铺天盖地的 "loop engineering" / "graph engineering" 帖子淹没后的反击 |

> "Vibe coding is not caring at scale."（vibe 编码 = 大规模的不在乎）——引 Jesse Vincent（Superpowers 作者）对 vibe coding vs agentic engineering 的定义："planning, architecture, and… caring about the output"

### 2. 九步工作流（How Kenn Builds）

| 步 | 做什么 | 关键细节 |
|---|---|---|
| ① 选对工具 | Superpowers（流程框架）+ roborev（持续本地审查验证） | 底座选型 |
| ② 一起设计 | **人参与每个重要 brainstorm 与设计决策**——设计与品味不委托给 agent | 设计权不外包 |
| ③ 第二意见 | 决策不明朗时，开**独立 agent 会话（最好异构模型家族）**挑战方案再定稿 | 对抗性设计审查 |
| ④ 写 spec 给实现者 | Superpowers 把设计转成精确规格——**spec 是指令文档，不是给人逐行读着安心的** | 人机分工点 |
| ⑤ 对抗性审 spec | 独立 agent 审规格，修复发现，**循环直到收敛** | 收敛才放行 |
| ⑥ 小块实现+验证 | spec→实施计划→子 agent 开发（Claude）或内联执行（Codex，因其子 agent 不行）；Superpowers 在验证 spec 一致性后频繁 commit；roborev 异步对抗验证；计划完成后 roborev-fix 清零所有 review | 高频提交 |
| ⑦ 分支级 bug 猎杀 | 前沿模型（5.6-Sol、Fable）产出"极其潦草，几乎从不能直接上生产"——大变更集上**花数百美元 token 用 roborev 磨 bug**，否则代码库变雷区 | 质量税 |
| ⑧ 工作持久化 | **spec/plan 文档不留在仓库**——全部转成"活架构文档"（living architecture documents），既给人看也给未来 agent 当上下文 | 文档即资产 |
| ⑨ 人拥有合并 | agent 打字检查，**人对结果负责**；PR 描述用平实语言、结论先行，拒绝 robospeak 长墙（点名 Claude Fable 默认这毛病） | 问责在人 |

### 3. Clanker 宪章（agent 操作系统原则，7 条）

clanker = 对 coding agent 的蔑称（"叫 agent 太抬举它们"）。开源在 github.com/kenn-io/constitution：

| # | 原则 | 内涵 |
|---|---|---|
| 1 | Honor the request | 指令即合同；贴入内容≠命令；review 模式就只 review，不许惊喜式改动 |
| 2 | Act with judgment | 安全可逆的事直接做；只有**实质改变结果**或**破坏性**操作才来问；无授权永不 merge |
| 3 | Finish the job | 授权了实现就不许停在诊断/半吊子修复；穷尽替代方案才能宣布受阻 |
| 4 | Protect existing work | 未经明确许可永不 reset/overwrite/amend；叫停就停 |
| 5 | Verify reality | 测行为，不测 mock 或源码文本；**没有新鲜证据不许宣称成功** |
| 6 | Communicate for humans | 结论先行，跳过流水账；按 PR 现状描述，禁 robospeak |
| 7 | Learn in the right place | 持久指引写进**共享指令文件**，不进 agent 私有记忆 |

### 4. 自建工具栈（"legacy stack 配不上 agent 时代的吞吐量"）

| 工具 | 层 | 解决什么 |
|---|---|---|
| **Kenn Forge** | PR 审查/落地 | GitHub 网站退化（独角兽故障页、九分之一可用性都难）；本地缓存全量 GitHub 数据，PR 秒切；活动倒序展示；一键在隔离 worktree 开内联 agent 工作区改 PR |
| **Ghosthub** | 终端 | 复用器原生（tmux/Herdr/Zellij）+ 远程开发（Tailscale+SSH）专用终端 |
| **Kata** | 意图记录 | agent-native issue tracker；中央 hub daemon 走 Tailscale，各机器 agent 联邦接入——本地即时（断网可用）+ 团队 30-60 秒同步；**intent 的 system of record**，取代散乱 Markdown 和重型 GitHub issue |
| **AgentsView** | 观测 | 开源 session/token 智能系统（$56,836 的账就是它算的） |
| **roborev** | 验证 | 持续本地代码对抗验证 + GitHub CI bot——"防止我们运出 slop 的问责引擎" |

## 二、查询拓展

1. Superpowers 框架（obra/superpowers）的 spec→plan→implement 三段式与本仓 writing-plans/subagent-driven-development skill 的映射关系
2. roborev 的"持续本地审查"与 CI 门禁的差异——为何 GitHub Actions 式验证不够
3. Kata 的联邦架构（中央 hub + 本地 daemon）——与 LangGraph Platform 的 task queue 模式对比
4. "异构模型第二意见"（不同模型家族交叉审查）的实践效果数据——与同模型自审的盲区对比
5. Clanker Constitution 七条与 Anthropic ABC Legal 案例（PR 控制面）的互补性——前者管 agent 行为，后者管 agent 资产
6. Wes 的 "loops are bullshit" 与 Andrej Karpathy 式 autonomy 光谱（L1-L5）的对话——他们各自反对的具体是什么 loop
7. living architecture documents 与 ADR（Architecture Decision Records）的差异——"给 agent 当上下文"如何改变文档写法

## 三、归纳总结

| 维度 | 要点 |
|---|---|
| 一句话 | 3 人团队周合并数百 PR 的秘诀不是更强的自治，而是**人始终在环的对抗性流程**+自建高吞吐工具栈 |
| 反直觉点 | 顶级 token 消耗者（$56K/月）恰恰是全自治最响亮的反对者——用得越多越知道 loop 的边界 |
| 流程核心 | 设计不外包→spec 对抗审查收敛→小块实现→roborev 异步对抗验证→人拥有合并 |
| 质量观 | 前沿模型产出"几乎从不能直接上生产"——质量来自**验证循环的美元投入**，不来自模型选择 |
| 文档观 | spec/plan 用完即焚，沉淀为活架构文档——过程文档≠资产，系统理解才是 |
| 工具观 | GitHub/IDE/裸终端的"legacy stack"配不上 agent 吞吐量——每层自建一个专用工具 |

## 四、趋势判断

1. **"loop engineering" 叙事退潮，"harness engineering" 叙事接棒**：Wes 对 loop/graph engineering 的公开反感代表一线重 token 用户的集体转向——投资从"让 agent 自转"移向"造更好的方向盘"（观测/验证/审查工具）
2. **对抗性验证成为独立产品层**：roborev（验证）、AgentsView（观测）、Forge（审查）各自成公司/产品——agent 时代的"质检产业"比 agent 本身先赚钱
3. **issue tracker 的 agent-native 重做**：Kata 把"意图记录"从人的待办清单变成 agent 的任务源——与 ABC Legal 的 issue 触发 agent、企业选型的"PM 软件 issue 驱动"是同一趋势的三个独立实现
4. **异构模型交叉审查会标准化**：单一模型家族的自我审查有系统性盲区，"second opinion from a different model family" 会变成 harness 常识（类似本仓 content-judge 思路）
5. **Clanker 宪章类"agent 行为公约"会开源化传播**：Kenn 把 constitution 放 GitHub 公开维护——agent 行为规范正在从各家私有 prompt 变成可引用的公共标准，与系统提示工程的宪法化趋势（Claude 4.5 宪法式系统提示）合流
6. **GitHub 的产品退化给第三方留出窗口**："struggle to hold even one nine" 的吐槽若普遍成立，Forge 类本地缓存+高吞吐 PR 工具会蚕食开发者日常工作流

## 五、关联分析

| 关联对象 | 关系 |
|---|---|
| **笔记《2026-08-18-企业Agent技术选型》** | 正面印证："全自治是 bullshit" = 该笔记"灰度四阶段+高风险人工门永不撤"；Wes 的九步流程就是"DAG 骨架+agent 节点"在研发领域的实例——spec→review→implement 是确定性管线，agent 只在⑥⑦两个节点干活 |
| **笔记《2026-08-18-HarnessEngineering七要素》** | Wes 栈是七要素的全套采购清单：Context（Superpowers spec）/Workflow（human-operator loop）/Permissions（Clanker 1-4 条）/Observability（AgentsView）/Evaluations（roborev）/Self-improvement（活架构文档=⑦）——独缺 Sub-Agents 要素，因为他明确不信任多 agent 循环 |
| **笔记《2026-08-19-ABCLegal全员建Agent》** | 双案例对照：ABC Legal 用 PR 当 agent 资产控制面（一切即代码），Kenn 用 PR 当人类问责面（own the merge）——PR 在两案例中分别是"agent 的生产物"与"人的责任状"，互补而非相同 |
| **笔记《2026-08-19-LangGraph全景》** | Wes 吐槽的 "graph engineering" 正是 LangGraph 叙事的极端版；但 Kenn 流程的 spec→review 循环本质是人肉 DAG——图没错，错的是把人从图里删掉 |
| skill `writing-plans` / `subagent-driven-development` | 本仓已有同款：计划先行+子 agent 执行；Wes 增量=①spec 独立对抗审查 ②异构模型第二意见 ③过程文档转活文档三步 |
| skill `critical-code-reviewer` | Clanker 第 5 条 "Verify reality—test behavior, not mocks" 与本仓 code-review 的零容忍原则同源 |
| 本仓 AGENTS.md 龙虾法则 | "重复任务→样本→批准→SKILL.md→cron" 对应 Clanker 第 7 条 "Learn in the right place"——经验进共享文件不进私有记忆，两套体系独立收敛到同一结论 |

→ 原文：https://wesmckinney.com/blog/agentic-engineering-aug-2026/
→ 宪章仓库：https://github.com/kenn-io/constitution
→ 相关：2026-08-18-企业Agent技术选型-全自治vs确定性DAG的混合架构共识与落地设计.md / 2026-08-18-HarnessEngineering七要素全景-Agent工程的完整学科地图与逐层深挖.md

## 六、拓展应用推荐

**① 可直接吸收进本仓（低成本高回报）**

| 借鉴点 | 本仓落地 |
|---|---|
| Clanker 宪章 7 条 | 写入 AGENTS.md 或独立 constitution.md 作为 agent 会话启动注入——比散落各 skill 的行为约束更系统 |
| 异构模型第二意见 | 本仓已有双模型（glm-5.3+sensenova 链）：重大设计决策时显式开第二会话交叉质询，写入决策模板 |
| spec 用完即焚→活文档 | 本仓 notes 体系已是活文档；补一条：临时 plan 文档完成后提炼进 SKILL.md/笔记，不留坟场 |
| PR 描述反 robospeak | 本仓飞书回复同样适用：结论先行、平实语言、按现状描述——写进沟通规范 |

**② 工具侧观察名单（不一定自建但值得盯）**
- AgentsView（开源）——本仓 observability-dashboard skill 的对照参考
- roborev——若开放自助，可接本仓 hermes-code-mod 的自动验证链
- Kata 联邦模式——与 exchange-protocol（三机经验池）互为参照：都是"本地即时+中央同步"

**③ 明确不跟的**
- 自建 Forge/Ghosthub 级工具——本仓吞吐量远未到 GitHub 痛点阈值，YAGNI
- 全盘照搬 3 人团队流程——本仓是"1 人+多 agent"，设计审查环节的密度可降频

## 七、指南分析

**human-operator loop 的最小可行版（个人/小团队可直接抄）**

```
1. 设计阶段：人写意图 → agent 出方案 → （重大时）换模型家族再问一遍"这方案哪里会死"
2. 规格阶段：方案固化成 spec → 独立 agent 对抗审查 → 修到收敛（通常 1-2 轮）
3. 实现阶段：切成半天粒度的小块 → 每块完成后跑验证（测试/lint/真实执行）
4. 验证阶段：验证不过不许报完成——"没有新鲜证据不许宣称成功"（Clanker #5）
5. 沉淀阶段：过程文档提炼进长期文档，临时 spec 归档或删除
6. 问责阶段：人审 diff、人按合并键——agent 永远不拥有最后一击
```

**三个防坑铁则**
- 区分两种 loop：agent 自转 loop（拒绝）≠ 人操作收敛 loop（必需）——判断标准是"谁决定停止"
- spec 审查的 agent 不要用实现者同一会话（会自我迎合）——独立会话起步
- 前沿模型产出默认"不能直接上生产"——验证预算（时间/token）要进计划，不是事后补

**何时该看这篇**：当你被"全自动 agent 流水线"营销打动时；当团队想砍掉 code review 环节时；当发现代码库 bug 率上升怀疑 agent 产出质量时——三个时刻都值得重读一遍 Wes 的 $56K 账单：**烧得最多 token 的人，最不相信 loop 会替你 caring**。

## 相关笔记

- [Cumora多Agent协调实战](./2026-08-19-Cumora多Agent协调实战-七层防御与十反模式-N个脑共享一屋的碰撞防御.md) — 多脑防御体系对照
- [ABCLegal全员建Agent](./2026-08-19-ABCLegal全员建Agent-Anthropic官方案例的agent舰队工程与信任获取循环.md) — 舰队规模化的信任侧
