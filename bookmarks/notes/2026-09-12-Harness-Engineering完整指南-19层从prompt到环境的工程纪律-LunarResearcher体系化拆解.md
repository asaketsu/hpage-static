# Harness Engineering 完整指南：19 层从 prompt 到环境的工程纪律——LunarResearcher 体系化拆解 × Hermes 对照审计

> **来源**：X/Twitter @LunarResearcher（Lunar）Article《Harness Engineering: The Complete Guide to Building AI Agents That Don't Fall Apart》2026-09 初
> **原文链接**：https://x.com/LunarResearcher/status/2096570562625655088
> **Substack**：substack.com/@lunarresearcher
> **抓取方式**：X Article 直读全文
> **笔记日期**：2026-09-12（21:14 date 实测确认）
> **关联笔记**：harness 簇全系列（SoL-Pi/Engram/TTFT/Gipp/beamnxw/AGENTS.md/Harness API/OUI-1/Skill 九条/Loop 与 Graph/A100 优化/GPU 互联/KV-Cache）——**本篇是簇的收官纲领**

---

## 零、结论先行

**19 条不是平行清单——是从"模型≠agent"到"harness 也会腐烂"的完整生命周期工程纪律，核心命题一句话："A prompt changes one attempt. A harness changes every attempt."（prompt 改变一次尝试，harness 改变每次尝试）。** 对我们最直接的价值：这是对本周 harness 簇 13 篇笔记的一次系统性回照——几乎每条都能在我们已有实践中找到对应，但文章把散落的实践编成了有序的层级（L1-L6 最小可行 harness）。**不形成新 skill**（harness-architecture skill 已覆盖理论层，AGENTS.md 准则 1-5 已覆盖实践层），但 §六审计清单是下次 hermes-system-audit 的现成 checklist。

## 一、核心命题

> "Many agent failures are not reasoning failures. They are environment failures."

> "A powerful model inside a weak harness is still a weak agent."

| 层 | 职责 | 失败如果缺失 |
|----|------|-------------|
| **Model** | 推理/生成/比较/选择 | 无智能 |
| **Harness** | 理解任务/找上下文/选工具/保状态/守权限/查结果/恢复失败/证明完成 | 有智能但不可靠——"impressive individual responses, but inconsistent across long tasks" |

> "The goal of harness engineering is not to remove uncertainty from the model. It is to contain that uncertainty inside a system that can observe, verify, and recover."（目标不是消除模型的不确定性，是把它装进一个能观察、验证、恢复的系统里）

## 二、19 条逐条拆解（按原文序）

### 第 1 条：模型不是 agent

模型能推理——agent 还必须与环境交互。harness = 让推理可操作的一切。

### 第 2 条：任务契约（Task Contract）

模糊意图→自主执行前→harness 转为**任务契约**，回答五问：

| 问 | 例子 |
|----|------|
| 什么结果必须存在？ | 产出物 |
| 什么在范围内？ | scope |
| 什么不能变？ | 不变量 |
| 什么证据证明完成？ | 验收标准 |
| 哪些操作需要人审批？ | 权限边界 |

> "Without a contract, the agent optimizes for plausible activity. With a contract, it can optimize for verified completion."（没有契约→agent 优化"看起来在干活"；有契约→优化"已验证完成"）

### 第 3 条：给地图，不给手册

> "Dumping the entire repository into context is not good context engineering. It is context flooding."

渐进式披露——上下文应因任务需要而扩展，不因信息存在而扩展。目标不是最大上下文，是**maximum signal per token**（每 token 最大信号量）。

### 第 4 条：工具网关，不是工具堆

给 agent 20 个工具=给它 20 种犯错方式。每个工具应有清晰契约。harness 控制：隐藏无关工具/验证参数/限制路径/加超时/幂等重试/归一化输出/风险操作需确认/返回证据非"success"。

> "The model can propose an action. The tool gateway decides whether that action is valid enough to execute."（模型提议，网关裁决）

### 第 5 条：分离脑、手、史

| 职责 | 需要什么 |
|------|---------|
| Brain（模型） | 当前正确的状态（不是每个原始事件） |
| Hands（沙箱） | 安全执行有界动作（不需要理解全部目标） |
| History（会话日志） | 保留发生了什么（不需要推理） |

混合在一起=脆弱的长 transcript；分离后可独立替换/恢复/审查。

### 第 6 条：记忆→持久状态

对话历史不是可靠记忆——是事件流。至少保留四类：

| 类别 | 用途 |
|------|------|
| 决策（Decisions） | 为什么选 A 不选 B |
| 不变量（Invariants） | 什么不能变 |
| 教训（Lessons） | 什么试过不行 |
| 状态（State） | 当前进展到哪 |

> "Store raw history for auditability. Compile durable state for execution."（存原始历史供审计，编持久状态供执行）

### 第 7 条：完成需要证据

> "An agent saying 'done' is not evidence that the task is done. It is only another model output."

harness 先跑最便宜的确定性检查——不用模型 where 编译器/schema/checksum/查询/测试能回答。

> "Use models for ambiguity. Use code for plumbing."（模型处理歧义，代码做管道）

> "A model can propose that the task is complete. Only the environment can prove it."（模型能提议完成，只有环境能证明）

### 第 8 条：验证应该攻击结果

worker 和 evaluator 不共享同一目标：
- worker：创造最强方案
- evaluator：**找拒绝的理由**

> "Verification is not a second opinion. It is an attempted disproof."（验证不是二次意见，是试图反驳）

同一 agent 同一上下文"自查"=保留了产生错误的假设。

### 第 9 条：模型提议，策略授权

> "Some rules should never depend on whether the model remembers them. They are not prompt suggestions. They are policy."

策略在推理循环之外。后果越严重→门越硬。

> "Autonomy is not the absence of control. It is the ability to operate freely inside a clearly enforced boundary."（自主不是没有控制，是在清晰执行的边界内自由操作）

### 第 10 条：恢复应针对失败类别

> "Something failed. Try again." — That is not recovery. It is repetition.

harness 先分类失败再选下一步——重试应改变至少一个相关条件，否则是在付钱复现同一失败。每个 loop 需要 budget：最大尝试/时间/花费/破坏范围/升级条件。

> "Reliable agents know how to continue. They also know when continuing is no longer rational."（可靠的 agent 知道怎么继续，也知道什么时候继续不再理性）

### 第 11 条：指令→基础设施

> "Instructions are useful when they explain local reality. But instructions alone are weak enforcement."

**指令阶梯**（instruction ladder）：prompt → skill → tool gateway → code → policy

> "Move important knowledge as far down that ladder as practical. The prompt should explain judgment. The harness should enforce invariants."（prompt 解释判断，harness 强制不变量）

### 第 12 条：观察运行，不只看最终答案

> "A clean final artifact can hide a terrible process."

有用 trace 记录：状态转换/上下文来源/工具 IO/环境变化/验证结果/重试原因/审批决策/成本和延迟。

> "The goal is not surveillance. The goal is local repair."（目标不是监控，是局部修复）——失败在第 18 步时可从可信检查点重启而非从头重放。

### 第 13 条：每次运行需要变更收据

不是"模型说了什么"的摘要——是"系统能证明什么"的摘要。给人和下一个 session 一个可信起点。

> "The best handoff is not 'here is the conversation.' It is 'here is the state, the evidence, and the unresolved risk.'"（最好的交接不是"这是对话"，是"这是状态、证据、未解决风险"）

### 第 14 条：每次失败升级 harness

> "The weakest teams fix the failed output. The strongest teams also fix the system that allowed it."

问：什么不变量本应阻止它？为什么没阻止？哪个检查漏了？转为可复用改进。

> "A corrected answer helps one run. A corrected harness helps every future run."（修正的答案帮助一次运行，修正的 harness 帮助每次后续运行）

### 第 15 条：harness 也会腐烂

> "More harness is not always better."

模型改进/工具改进/任务变化→旧安全措施可能变成不必要的摩擦。为昨天模型做的 workaround 可能阻止今天模型用更好的策略。

> "The best harness is not the largest one. It is the smallest system that reliably closes the gap between intent and evidence."（最好的 harness 不是最大的，是可靠弥合意图与证据之间差距的最小系统）

> **"Build to delete."（为删除而构建）**

### 第 16 条：最小可行 harness（L1-L6）

| Level | 内容 |
|-------|------|
| L1 | 有界任务（目标/scope/约束/验收检查） |
| L2 | 可读环境（项目地图/命令/本地指令/已知依赖） |
| L3 | 受控操作（类型化工具/参数验证/路径权限边界/结构化结果） |
| L4 | 持久执行（显式运行状态/检查点/决策/教训） |
| L5 | 证据（确定性检查/对抗性验证/变更收据） |
| L6 | 恢复与学习（失败分类/有界重试/升级/harness 更新） |

> "Build the smallest layer that eliminates the failure you actually have."——不为偶尔需要澄清的 prompt 搭多 agent 架构。**复杂度应由观察到的失败来挣得。**

### 第 17 条：可复用 harness 规格

给 agent 有意义自主前定义：scope/boundaries/tools/memory model/verification/escalation——未定义=agent 在即兴表演不是自主。

### 第 18 条：正确层级度量

token 数不是最终指标——**accepted work**（被接受的工作）才是。实用指标：

| 指标 | 说明 |
|------|------|
| first-pass acceptance rate | 首次通过率 |
| recovery rate after tool failure | 工具失败后恢复率 |
| repeated failure rate | 重复失败率 |
| human interventions per task | 每任务人工干预次数 |
| unsupported completion claims | 无证据的完成声明 |
| time from request to verified outcome | 请求到验证完成时间 |
| harness overhead by component | 各组件 harness 开销 |

> "An agent can look highly productive while creating expensive review work."（agent 看起来高效但制造昂贵的审查工作）

> "The objective is not more agent activity. It is more trusted outcomes per unit of human attention."（目标不是更多 agent 活动，是每单位人类注意力产生更多可信结果）

### 第 19 条：什么时候不需要重 harness

简单 prompt 够用的条件：任务短/输出易检/失败便宜/无外部副作用/人在回路。

加 harness 的条件：跨多工具或 session/环境可变/操作有真实后果/完成难手动判断/同一失败反复出现/人审成瓶颈。

## 三、与本周 harness 簇 13 篇笔记的交叉对照

| 文章条 | 对应笔记 | 判定 |
|--------|---------|------|
| ② Task Contract | AGENTS.md 准则"完成定义"五项 | ✅ 已满足 |
| ③ 地图非手册 | AGENTS.md 准则 1"上下文分层加载" | ✅ 已满足 |
| ④ Tool Gateway | AGENTS.md 权限三层模型 | ✅ 已满足 |
| ⑤ 脑/手/史分离 | Skill 九条原则 ②渐进式披露 | ✅ 互补 |
| ⑥ 记忆→持久状态 | 三级记忆架构（L1/L2/L3） | ✅ 已满足且更系统 |
| ⑦ 完成需证据 | AGENTS.md"退出码≠0=未完成" + golden set | ✅ 已满足 |
| ⑧ 验证攻击结果 | Loop/Graph"两个乐观主义者同意" + Skill 九条⑤ | ✅ 互补 |
| ⑨ 模型提议策略授权 | Loop/Graph"爆炸半径车道" + AGENTS.md 权限三层 | ✅ 互证 |
| ⑩ 恢复针对失败类 | AGENTS.md"3+ fixes=停下问架构" + systematic-debugging | ✅ 已满足 |
| ⑪ 指令→基础设施 | Skill 九条⑥"代码胜于推理" + AGENTS.md 准则 5 | ✅ 已满足 |
| ⑫ 观察运行 | observability-dashboard skill | ✅ 有机制 |
| ⑬ 变更收据 | PROGRESS.md 状态子系统 | ✅ 已满足 |
| ⑭ 每次失败升级 harness | evolver skill + AGENTS.md 准则 5"规范即活文档" | ✅ 已满足 |
| ⑮ harness 腐烂 | Skill 九条⑧"Skills decay" + skill-review | ✅ 互补 |
| ⑯ L1-L6 最小可行 | hermes-system-audit skill 的分层 | ✅ 可对标 |
| ⑱ 正确层级度量 | 观察到的：first-pass rate/recovery rate | 🟡 我们没系统追踪这些指标 |
| ⑲ 何时不需要重 harness | AGENTS.md"简单任务直接分配" | ✅ 已满足 |

**13 篇笔记的合流点**：几乎每条原则都能在簇中找到 1-2 篇笔记的独立互证——**本周的笔记选择不是随机的，是在无意识中覆盖了 harness engineering 的完整谱系**。

## 四、三条最增量 Nugget

### 4.1 "Build to delete"（为删除而构建）

这是对 Skill 九条⑧"Skills decay"的补全——不只"skill 会腐烂"，harness 本身也会。且方向明确：**每次加一层时问"如果删了会怎样"**——这是我们 600+ skill 库从未问过的问题。

### 4.2 "Complexity should be earned by observed failure"（复杂度应由观察到的失败挣得）

> "Do not begin with a multi-agent architecture because a single prompt occasionally needs clarification."

这是对 SoL-Pi 152→4 的 harness 层表述——不是"少做多做"的品味，是**没有失败证据不加复杂度**的纪律。

### 4.3 "Accepted work"作为度量单位

> "The objective is not more agent activity. It is more trusted outcomes per unit of human attention."

我们追踪 token/任务数/笔记数——但**从未追踪"被用户接受的工作"比率**。这是 hermes-system-audit 应该加的指标。

## 五、与 AGENTS.md 准则的逐条映射

| AGENTS.md 准则 | 文章条 | 关系 |
|----------------|--------|------|
| 1. 上下文分层加载 | ③ 地图非手册 | 同构 |
| 2. 执行/评判分离 | ⑧ 验证攻击结果 | 同构 |
| 3. 质量门禁机械化 | ⑦ 完成需证据 | 同构 |
| 4. Dry Run 先行 | ⑯ L1-L6 最小可行 | 互补 |
| 5. 规范即活文档 | ⑭ 每次失败升级 harness | 同构 |

**五条准则 = 文章 19 条的压缩版**——我们的 AGENTS.md 在 2026-05-07 就已经把这 19 条蒸馏成了 5 条。文章给的是展开版，适合做审计 checklist。

## 六、批判性审视

1. **19 条是"完整指南"的声称未经验证**——文章无实测数据、无案例、无代码——是概念框架不是工程文档（与 beamnxw Lane 的身份/记忆分离实测形成对比）
2. **"harness 也会腐烂"的检测方法太抽象**——"Measure whether they still provide lift"——怎么测？lift 的定义？文章停在提问不给解法
3. **L1-L6 分层隐含线性递进**——但真实系统可能 L4（持久执行）比 L3（受控操作）更急需——文章说"按你实际有的失败建"，但没给优先级判定方法
4. **"Accepted work"指标无操作性**——怎么定义"被接受"？用户没拒绝就算？还是需要显式确认？——我们的 golden set 门禁是更具体的版本
5. **Substack 导流**：文章末尾 "Follow my Substack" + "Send this article to someone"——概念文的营销属性
6. **与我们已有实践的偏差未讨论**：我们的三级记忆（L1/L2/L3）比文章四类（Decisions/Invariants/Lessons/State）更细——文章没讨论记忆的分层策略

## 七、金句提取

> "A prompt changes one attempt. A harness changes every attempt."

> "Many agent failures are not reasoning failures. They are environment failures."

> "The goal is not to remove uncertainty from the model. It is to contain that uncertainty inside a system that can observe, verify, and recover."

> "Without a contract, the agent optimizes for plausible activity. With a contract, it can optimize for verified completion."

> "The model can propose an action. The tool gateway decides whether that action is valid enough to execute."

> "Use models for ambiguity. Use code for plumbing."

> "A model can propose that the task is complete. Only the environment can prove it."

> "Verification is not a second opinion. It is an attempted disproof."

> "Autonomy is not the absence of control. It is the ability to operate freely inside a clearly enforced boundary."

> "Reliable agents know how to continue. They also know when continuing is no longer rational."

> "The prompt should explain judgment. The harness should enforce invariants."

> "A corrected answer helps one run. A corrected harness helps every future run."

> "The best harness is not the largest one. It is the smallest system that reliably closes the gap between intent and evidence."

> "Build to delete."

> "Complexity should be earned by observed failure."

> "The objective is not more agent activity. It is more trusted outcomes per unit of human attention."

> "The best handoff is not 'here is the conversation.' It is 'here is the state, the evidence, and the unresolved risk.'"

## 八、局限性

1. X Article 约 4000 字——概念文/框架文，无实测数据无代码无案例
2. 19 条来源未给——是作者经验总结还是调研结果不清楚
3. L1-L6 的"最小可行"判定方法未给——只说"按实际失败建"但没给优先级
4. "Accepted work"等指标无操作性定义
5. §三对照基于本机笔记库和 AGENTS.md 自查——未实际改造 harness
6. 文章面向"building AI agents"的通用读者——与我们 Hermes 特定架构的偏差未讨论
7. 与 harness-architecture skill（已存在）的重叠度约 70%——本笔记的增量在 §三交叉对照和 §四 Nugget

## 出处标注

| 章节 | 来源类型 |
|------|---------|
| 一至二 | **原文忠实还原**（X Article 全文直读，19 条逐条） |
| 三 | **体系映射**（本周 13 篇笔记 + AGENTS.md 交叉对照） |
| 四 | **Nugget 提炼**（本笔记扩展） |
| 五 | **批判性审视**（本笔记扩展） |


## 相关笔记

- [Ecdysis论文-FDCR四角色拆解](./2026-09-12-Ecdysis论文-模型特异迁就vs-harness级修复-跨任务失败聚合与FDCR四角色拆解.md) — harness 簇学术收口，19层的实验证据
- [Loop与Graph-停止babysitting-agent](./2026-09-12-Loop与Graph-停止babysitting-agent的两层架构-循环内验证与图间编排拆解.md) — 两层架构是19层中的编排层
- [Skill九条原则-Bibryam三幕生命周期](./2026-09-12-Skill九条原则-从被选到活着-Bibryam三幕生命周期拆解与Hermes-skill库对照审计.md) — skill生命周期对应19层中的指令层
- [SoL-Pi英伟达自我优化Harness](./2026-09-11-SoL-Pi英伟达开源自我优化Harness-四大机制与152选4的RSI流水线拆解.md) — 自我优化harness实例
- [AGENTS.md手册模式-Skill必要性判定](./2026-09-12-AGENTS.md手册模式-厂商文件薄适配器化与三重验证法-Skill必要性判定.md) — 指令层资产化
- [自进化Harness与记忆-三种写法](./2026-09-11-自进化Harness与记忆-三种写的不可混同-LiveSWE-DGM-SWE-Exp实证拆解.md) — harness三种写法对照
