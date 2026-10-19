# Skill 九条原则：从"被选中"到"活着"——Bibryam 三幕生命周期拆解 × Hermes skill 库对照审计

> **来源**：X/Twitter @bibryam（Bilgin Ibryam）Article《9 Principles That Separate Useful Skills From Markdown Essays》2026-09 初
> **原文链接**：https://x.com/bibryam/status/2098407839748214983
> **原始发布**：The Generative Programmer
> **抓取方式**：X Article 直读全文
> **笔记日期**：2026-09-12
> **关联笔记**：《AGENTS.md 手册模式》（指令层资产化）《SoL-Pi》（harness 可 RSI 优化 40:1 死亡率）《自进化 Harness 与记忆》（SkillsBench 负结果 -8~-11）《text-to-cad×CATDS判定》（SKILL.md 写作范本）

---

## 零、结论先行

**九条原则按三幕组织——被选中→可靠执行→接触现实存活——不是泛泛建议，是 skill 生命周期三个失败时刻的逐一对策。** 对我们最直接的价值：这是**对我们 600+ skill 库的一次系统性审计框架**——用九条逐条扫描，暴露"beautifully written but fails"的 skill。与我们已有的 skill-health-tier/skill-review/auto-skill 形成互补：它们管"创建和分级"，九条管"为什么会失败"。**不形成新 skill**（九条本身是元原则，审计动作用现有 skill-review 即可执行），但**立即用九条做一次抽样审计**（§六）。

## 一、三幕框架（文章结构）

> "A skill can be beautifully written and still fail in three different moments: It is never selected. It loads but does not reliably change behavior. It works today and quietly decays tomorrow."

| 幕 | 失败时刻 | 原则 |
|----|---------|------|
| **Act 1: 被选中** | 从未被加载 | 1. Metadata is the gate / 2. Disclose progressively / 3. Process over prose |
| **Act 2: 可靠执行** | 加载了但不改变行为 | 4. Explain the why / 5. Anticipate the excuse / 6. Code over inference / 7. Stay in scope |
| **Act 3: 接触现实** | 今天有效明天失效 | 8. Skills decay / 9. Run before you ship |

## 二、Act 1: Getting Selected（被选中）

### 原则 1: Metadata is the gate（元数据是门）

- 会话开始时模型不读每个 SKILL.md——它看的是 skill listing：**主要就是 name 和 description**
- description 不是摘要——**它是首要的选中信号**。说清：skill 做什么、哪些请求该触发它、哪些附近的工作不该
- **"If a skill loses the metadata-only round, nothing inside the body can rescue it."**（元数据轮输了，正文再好也救不回来）

### 原则 2: Disclose progressively（渐进式披露）

上下文是共享预算——每个花在某 skill 的 token 与对话、项目上下文、其他能力竞争。分层加载：

| 层 | 时机 | 内容 |
|----|------|------|
| metadata | 会话开始 | name + description |
| SKILL.md | 被触发时 | 工作流/约束/坑 |
| references | 任务需要时 | 深度文档 |
| scripts | 执行时 | 只有输出进上下文 |

**"Assume the model already knows general concepts. Spend tokens on your workflow, constraints, examples, and domain-specific gotchas."**（假设模型已懂通用概念，token 花在你的工作流/约束/坑上）

### 原则 3: Process over prose（流程胜于散文）

- 关于好测试的长文可以被读、被摘要、被忽略——**带检查点的工作流改变 agent 实际做什么**
- **"If a competent junior engineer could not tell what to do next, the file is reference material—not a skill."**（一个合格初级工程师看不出下一步做什么，那文件是参考材料不是 skill）
- 有退出标准的步骤胜过没有退出标准的建议

## 三、Act 2: Running Reliably（可靠执行）

### 原则 4: Explain the why（解释为什么）

- 满篇 ALWAYS/NEVER/MUST 鼓励字面遵从而非判断——**给规则，然后给理由**
- 理由在模型遇到你没预见的边缘案例时变成 rubric（评判标准）
- 理由还帮助区分**真不变量 vs 偏好**

### 原则 5: Anticipate the excuse（预判借口）

即使规则和理由都清楚，能力强的模型仍可能合理化跳过：
- "改动很小"
- "用户在赶时间"
- "昂贵的验证这次大概不需要"

**对不可商量的步骤，显式记录常见捷径并反驳它。** 如果同一个合理化在重复运行中出现，把它变成 guardrail。

### 原则 6: Code over inference（代码胜于推理）

- 别让模型每次调用都重新创建同一个验证器/提取器/归一化器
- 能确定性的步骤→ship as code——**脚本更快、可重复、上下文便宜（只有结果进对话）**
- **"Use the model for judgment. Use programs for repeatable mechanics."**（模型做判断，程序做重复机械）

### 原则 7: Stay in scope（守在范围内）

- 一行修复变成 40 行 diff 跨 3 文件 = 不helpful
- 无关重构/改名/清理增加审查成本和风险
- **告诉 skill 只碰任务需要的——scope discipline 是 agent 改动可合并性的最强预测器**

## 四、Act 3: Surviving Contact with Reality（接触现实存活）

### 原则 8: Skills decay（技能会腐烂）

- 库更新、API 迁移、团队约定变化、模型随时间对指令的理解不同
- **"A stale skill is worse than a stale comment because the agent may execute it confidently."**（腐烂的 skill 比腐烂的注释更坏——因为 agent 会自信地执行它）
- 把 skill 当活的操作工件：有 owner、review date、versioning、regression scenarios
- **"A skill you have not rerun in months is a liability you have not measured."**（几个月没重跑的 skill 是你还没测量的负债）

### 原则 9: Run before you ship（先跑再发布）

- 仅凭想象写的 skill 编码的是**作者希望的工作流，不是 agent 实际遵循的工作流**
- 跑 2-3 个真实案例→读 transcript→把重复的 helper 提到 scripts/→给重复的合理化加反驳→记录抓过多次的坑→然后重跑
- **"The skill is debugged from observed behavior, not polished into correctness from the editor."**（skill 从观察到的行为调试，不是在编辑器里打磨到正确）

## 五、三条地基

> "All nine matter, but three carry the structure:

| 地基 | 一句话 | 为什么是地基 |
|------|--------|-------------|
| **Metadata is the gate** | 不触发的 skill 永不帮忙 | 没选中=没有一切 |
| **Process over prose** | 没有动作的 skill 不控制行为 | 散文可以被忽略 |
| **Run before you ship** | 没有观察运行的 skill 编码猜测 | 想象≠实际 |

其余六条修正"已能被选中+执行+测试"的 skill 内部的具体失败模式。

## 六、Hermes skill 库对照审计（600+ skills × 九条）

### 6.1 我们做得好的

| 原则 | 我们的实践 | 判定 |
|------|-----------|------|
| 1. Metadata is the gate | auto-skill 生成的 description 含 trigger 条件；skill 索引注入系统提示 | ✅ 已满足 |
| 2. Disclose progressively | AGENTS.md 准则 1"上下文分层加载"L1/L2/L3 | ✅ 已满足且更系统 |
| 6. Code over inference | notes_eval_gate.py/scan_data.py/pub_pipeline.py 等确定性脚本 | ✅ 已满足 |
| 8. Skills decay | skill-review/skill-health-tier 定期回顾 | ✅ 有机制 |
| 9. Run before you ship | auto-skill 的"门禁后写入"；skill-ab-testing 候选版验证 | ✅ 有机制 |

### 6.2 我们有差距的

| 原则 | 差距 | 严重度 | 修复动作 |
|------|------|--------|---------|
| **3. Process over prose** | 部分 skill 是散文非流程——"分析型 skill"尤其是 | 🟡 中 | 下次 skill-review 逐条查"有退出标准的步骤" |
| **4. Explain the why** | 部分铁律只有 ALWAYS/NEVER 没给理由——记忆里的铁律尤其 | 🟡 中 | 下次审计给每条铁律补"因为…"一句 |
| **5. Anticipate the excuse** | 几乎没有 skill 显式预判借口 | 🔴 高 | 挑 top 10 高频 skill 补"常见捷径+反驳" |
| **7. Stay in scope** | AGENTS.md 有"禁止一次性工作"但没有 skill 级的 scope 约束 | 🟡 中 | 考虑在 skill 模板加 scope 声明段 |
| **8. Skills decay** | 有 skill-review 但**没有 review_date 字段**——不知道谁该审了 | 🔴 高 | skill 模板加 `last_reviewed:` 日期字段 |

### 6.3 最狠的两句对照

| 文章金句 | 对我们的打脸 |
|---------|-------------|
| "几个月没重跑的 skill 是你还没测量的负债" | 我们 600+ skill 中多少跑过？auto-skill 只加不减——SoL-Pi 的 40:1 死亡率说明大部分应该是死的 |
| "skill 从观察到的行为调试，不是在编辑器里打磨到正确" | 我们 skill-ab-testing 有这个精神但执行不够——大部分 skill 是"写完上线"不是"跑完修" |

## 七、与今日/昨日笔记的合流

| 篇 | 与九条原则的连接 |
|----|-----------------|
| SoL-Pi（152→4） | 原则 9 的终极版——152 个"想象中的优化"只 4 个通过真实运行 |
| 自进化 Harness（SkillsBench -8~-11） | 原则 3 的反证——考前自写 skill 包=散文非流程→降分；CODESKILL 跑后提取=流程→+9.69 |
| AGENTS.md 手册模式 | 原则 2 的仓库级版——四部件分层加载=渐进式披露 |
| text-to-cad×CATDS | 原则 9 的正面教材——build123d 的 SKILL.md 有默认值/何时不用/版本钉住=流程非散文 |
| OUI-1 | 原则 6 的训练版——"代码胜于推理"=只修 parser 报的缺陷不重写 |

## 八、批判性审视

1. **九条是"好 skill"的充分条件不是必要条件**：一个 skill 可以满足全部九条仍不够用（领域知识不足/模型能力不够）——文章没讨论 skill 质量的天花板
2. **"description 是首要选中信号"依赖 skill listing 的注入方式**：不同 agent 框架注入方式不同——Hermes 注入系统提示（全量索引），Claude Code 注入方式未公开——九条的普适性需框架校正
3. **原则 8"review date"字段是好主意但没给执行机制**：谁来审？审什么标准？多久？——只提了问题没给解法（我们的 skill-review 有解法但比文章深）
4. **原则 9"跑 2-3 个真实案例"对非编码 skill 不适用**：分析型/创意型 skill 怎么"跑"？——文章隐含的是编码 skill 视角
5. **作者背景**：Bilgin Ibryam 是分布式系统/中间件背景（Apache Committer）——skill 的"活工件"类比可能受运维视角影响

## 九、金句提取

> "A skill can be beautifully written and still fail."

> "If a skill loses the metadata-only round, nothing inside the body can rescue it."

> "If a competent junior engineer could not tell what to do next, the file is reference material—not a skill."

> "Use the model for judgment. Use programs for repeatable mechanics."

> "A stale skill is worse than a stale comment because the agent may execute it confidently."

> "A skill you have not rerun in months is a liability you have not measured."

> "The skill is debugged from observed behavior, not polished into correctness from the editor."

## 十、局限性

1. X Article 约 1500 字——概念文/原则文，无实测数据无代码示例
2. "9 Principles"的来源未给——是作者经验总结还是调研结果不清楚
3. 九条之间的优先级/依赖关系只给了三条地基，其余六条未排序
4. §六审计基于本机 skill 库自查——未实际逐条扫描 600+ skills（抽样判断）
5. 与 skill-review/skill-health-tier 的互补关系是本笔记推断，未验证

## 出处标注

| 章节 | 来源类型 |
|------|---------|
| 一至五 | **原文忠实还原**（X Article 全文直读） |
| 六 | **本机对照审计**（600+ skill 库抽样自查） |
| 七 | **笔记联动**（今日/昨日笔记交叉） |
| 八 | **批判性审视**（本笔记扩展） |


## 相关笔记

- [Harness-Engineering 19层完整指南](./2026-09-12-Harness-Engineering完整指南-19层从prompt到环境的工程纪律-LunarResearcher体系化拆解.md) — 19层中的指令层资产化
- [Ecdysis论文-FDCR四角色拆解](./2026-09-12-Ecdysis论文-模型特异迁就vs-harness级修复-跨任务失败聚合与FDCR四角色拆解.md) — 批量聚合训练法对应skill进化
- [AGENTS.md手册模式-Skill必要性判定](./2026-09-12-AGENTS.md手册模式-厂商文件薄适配器化与三重验证法-Skill必要性判定.md) — 指令层资产化
- [自进化Harness与记忆-三种写法](./2026-09-11-自进化Harness与记忆-三种写的不可混同-LiveSWE-DGM-SWE-Exp实证拆解.md) — SkillsBench负结果(-8~-11)
- [text-to-cad×CATDS判定](./2026-09-11-text-to-cad×CATDS逐项判定-模型脚本范式与新鲜度门禁的借鉴分析.md) — SKILL.md写作范本
