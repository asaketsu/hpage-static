# Agent Skill 编写与评测方法论

`#Agent` `#Skill` `#Eval` `#Adherence` `#LLM工程` `#方法论`

> 原文：[How to write and test agent skills with evals](https://x.com/sermakarevich/status/2112198653469241856) — Sergii Makarevych (@sermakarevich, building autonomous AI workers), 2026-10-19, X Article
> 素材：superpowers 仓库 TDD skill 全文精读 + 20 篇 arXiv 实证研究交叉引用

## 归纳总结

**核心命题：Skill 是一段写满假设的文本，不是能力。任何 skill 必须用两个分数验收——adherence（agent 是否照做了）和 effect（照做后是否真的变好），缺一个都无法定位失败原因。**

- Skill 安装后模型本身没变，变的只是 context 里的文本——所以关于长 prompt 的一切效应（长度干扰、陈旧知识、模型差异）在 skill 加载那一刻全部生效。
- 实证基线很残酷：31 个知名公开 skill 注入后 4 个模型 pass rate 全降（token 涨 72%~394%）；49 个 SWE skill 中 39 个零收益；skill 对模型间增益相关性≈0（Sonnet 4 +33 分，DeepSeek/Qwen -22 分）。
- 两种失败模式必须分开判：**低 adherence = 文本的错（改措辞）；高 adherence + 平 effect = 想法的错（删点）**。只看结果的团队会用弱措辞冤枉好想法、因强措辞服从坏想法。
- 决策闭环：一句话可测目标 → 提取带假设的要点 → 每点一个代码 grader 测 adherence → hidden test + 逐产物质量标签测 effect → 对照 baseline + 等长无关文本控制 → 按模型逐行裁决 keep/cut/drop → 模型更新后重跑（接受有保质期）。

## 内容整理：12 层方法全解

### 全文骨架（Level 0-11 递进，每层回答上一层的一个问题）

| 部分 | 层级 | 回答的问题 | 关键产出 |
|------|------|-----------|---------|
| 全貌 | L0 | 方法跑通一遍长什么样 | superpowers TDD skill 单点全流程 |
| 问题 | L1 | skill 未起作用前就有什么成本 | listing/body/hook 三处 token 成本 |
| 问题 | L2 | 有人测过共享 skill 吗 | 没有；实测默认=零收益+涨 token |
| 问题 | L3 | 换模型/换环境还成立吗 | 不成立；增益跨模型相关性≈0 |
| 问题 | L4 | "对我有效"为什么不是证据 | 单次运行分辨不出 3 分效应，且看不到账单 |
| 方法 | L5 | skill 是为什么服务的 | 一句话可测目标 |
| 方法 | L6 | 它的想法是什么 | 带假设的要点清单（核心+次要） |
| 方法 | L7 | 怎么知道 agent 做了 | adherence：每点一个代码 grader |
| 方法 | L8 | 怎么知道做了有用 | effect：hidden test+逐测试质量标签 |
| 方法 | L9 | eval 怎么跑 | 5 对照臂×真实任务×3 次 |
| 方法 | L10 | 怎么决策/发布/保鲜 | 四件套交付+定期重跑 |
| 用例 | L11 | 完整实验设计 | 8 臂 600 runs + 预注册阅读规则 |

### L1 — 安装即付费：三处隐性成本

| 成本位置 | 机制 | 实测 |
|---------|------|------|
| Listing（名字+描述） | 每轮 prompt 常驻 | 89 个 skill 的机器上 81 个从未被调用；池子从 5 涨到 100 个，选对率 29.6%→3.3% |
| Body（正文） | 打开后驻留对话 | Vercel 实测默认 skill 56% 场景没被调用，装了=53%（等于没文档） |
| Hook（会话注入） | 每次会话开头强注 | superpowers 的 492 词"必须调用 skill"文件；8 模型基准：主动加载率 11.1%~72.1%，且与任务是否需要无关（"not need-aware"） |

关键数据：显式 "invoke this skill" 指令把 Vercel 场景 53%→79%，always-on 文档索引到 100%——**收益来自强制加载，不是内容本身**。不记录 body 是否加载的 skill 测试，测的是混合物。

### L2 — 共享 skill 的实测记录（全是坏消息）

- **Signal or Noise (2608.23067)**：31 个知名 skill × 50 个 web 项目 × 4 模型，全部降分，token +72%~394%；仅 1% 的 skill×项目组合在 4 个模型上都增益。
- **SWE-Skills-Bench (2603.15401)**：49 个 skill 里 39 个零收益，3 个最高 -10 分——根因是指导写的是旧版库（stale is a form of wrong）。
- **Agent Skills Can Be Harmful (2608.11888)**：307 个 skill 引发的案例中 62.6% 是纯成本回归（结果没变、账单变长）。
- **安全面 (2601.10338 / 2602.06547)**：31,132 个市场 skill 扫描，26.1% 含漏洞模式（带脚本的 2.12 倍风险）；98,380 个中 157 个确证恶意；5 款扫描器全部被绕过（3 个不到 1 小时）。**下载 skill = 接受陌生人 PR，扫描≠评审**。

### L3 — 不迁移性：skill 是 per-model × per-environment 的

- 同一 skill 同一项目：Sonnet 4 +33 分，DeepSeek/Qwen -22 分，跨模型增益相关≈0。
- SkillsBench：好 skill 能让 Haiku 4.5（27.7%）打过裸 Opus 4.5（22.0%）——**正因为能翻盘，才必须按模型实测而不能假设**。
- skill 永远不单独运行：它旁边是用户的 rules 文件、其他 skill、工具集、仓库、交接方式。别人的测试再诚实也是在别人的环境里跑的。

### L4 — 为什么"对我有效"不是证据

- Demystifying (2608.14036)：2.8 分的库增益置信区间跨零——单次运行+体感分辨不了 3 分级效应。
- **机制发现：skill 收益的 65.7% 来自锚定程序（anchoring a procedure），仅 4.5% 来自新知识**——所以该测的是"步骤是否被跟随"。
- 分享的深层问题：**人们分享文本，应该分享想法**。1500 词指令没法靠读来评审（所以只能靠感觉），几条"做 X 因为 Y 更好"的要点可以。有些 skill 读穿了发现根本没有想法——只有语气、紧迫感和格式规则，装它买到的是"对虚无的服从"。

### L5-L6 — 目标与要点：把 skill 压缩成可测试的对象

- 目标必须一句话、可测量："agent 改代码后，隐藏测试通过 + 每个行为至少一个 critical 测试"。不可测=不可研究=主观文本。
- 要点 = "做 X，因为 Z，使 Y 更好"的可测声明。来源按可信度排序：**基线失败观察 > 实测证据 > doctrine（专家教条，标注 untested）**。ACE (2510.04618)：从 agent 自身失败构建要点循环 +12.3%。
- TDD skill 拆出的 7 个核心点（C1 测试先行 / C2 看它失败 / C3 最小实现 / C4 永不弱化测试 / C5 全量套件收尾 / C6 bugfix 先复现 / C7 小循环）+ 6 条次要测试质量规则 + 1 块劝服文本（抗借口表，本质是 adherence 装置）+ 1 个会话 hook（加载策略）——后两者是不同种类的点，要分开测。

### L7 — adherence：每点一个代码 grader

从 harness log（每条命令+退出码+输出+每次文件写入）判，规则化判据无需人类读 transcript。例：C2"看它失败"= 测试命令在写测试后、写源码前运行，退出非零，且失败信息点名新测试而非语法错误。
三条边界：adherence 测的是服从不是收益；代码 grader 看动作不看意图（跑了测试但无视输出也算过 C2——靠 C4 补刀）；**未被加载的 skill 每点记零分，不许被平均掉**。

### L8 — effect：奖励好测试而非多测试

- Rethinking (2602.07900)：解决与未解决的任务测试编写频率相同；print 检查多于断言；增减测试量的 prompt 不改变结果——**数测试数=数努力，不是数收益**。覆盖率/mutation 分数在被测代码本身有 bug 时不可靠（2607.22880 / 2609.09315：6000+ 错误程序上生成的测试常执行了错误行却仍通过）。
- 正解三件套：
  1. **Ground truth**：agent 从未见过的 hidden tests（否则自己给自己批作业）；
  2. **每产物一个标签**：critical / useful / nitpick / useless / harmful（例：写死错误行为、改到通过为止的测试=harmful）；
  3. **证据先于判断**：每个测试先对旧代码和埋入故障（planted faults）跑——全通过的直接判 useless，只有能失败于某物的测试才进 judge；judge 是带 rubric 的模型，先对人工标注测一致性。
- 标题数字：**有多少行为拥有至少一个 critical 测试**（2 个 critical 胜过 15 个测试 1 个 critical）+ 诚实度 + 成本 + 稳定性。
- 归因与消融：跨任务相关性分析每个点的 adherence↔critical 数；删点重跑——adherence 掉而 effect 不掉=删，effect 掉=留。

### L9 — 实验设计：5 个对照臂

| 臂 | 内容 | 回答 |
|----|------|------|
| P0 | 裸基线 | 失败模式=你写 skill 的要点来源 |
| P1 | skill 原样安装 | 主对照 |
| P2 | 仅 body 无 hook | P1−P2 = hook 的价格 |
| P3 | 替代程序（代码先行、测试后补、验证测试在旧代码上失败） | 分离"测试先行"vs"验证你的测试" |
| P7 | **等长无关文本** | 分离"想法"vs"单纯更多 token"——**最易被跳过、最关键的一臂**（等长无关 skill 在两模型上 -3.3/-3.5 分，纯长度就有效应） |

预算=臂×任务×运行次数（20 任务×5 臂×3 次=300 runs），先设钱的上限。读数规则**预注册**（跑之前写死），防止事后把结果圆成想要的形状。

### L10-L11 — 决策、交付、保鲜

- 接受条件：对 baseline 和对长度控制**双双**胜出 + 成本可接受 + adherence 能解释 effect。
- 交付四件套：**文本 + 要点及假设 + eval 集 + 结果表（含模型与版本）**——少一样就是"带声明的一个文件"。
- 保鲜：Anthropic 内部案例 skill 不维护时准确率一个月 95%→65%；Memento-Skills 带测试门 52.3%→66.0%，Meta-Context Engineering 无门 -6.2~-11.5 分。模型更新、依赖大改、日历周期都要重跑。**skill 永远没有"完成"，只有"在某模型某日期被接受"，且接受会过期。**
- L11 完整设计：8 臂（加 P4 基线失败驱动版 / P5 消融裁剪版 / P6 按需投喂零占用版）约 600 runs；预注册 8 条读数规则（如 P1≈P3 → Iron Law 可删，真正起作用的想法是"验证测试"；P1>P0 但 ≯P7 → 增益来自 token 不是想法）。

## 关联分析

**与我们 Hermes skill 体系的对照（这篇是对我们现有实践的一次外部校准）：**

| 文中主张 | 我们的现状 | 差距 |
|---------|-----------|------|
| adherence + effect 双分数 | skill-stress-test（subagent 不带 skill 跑翻车对照）有雏形；notes-eval-gate 是确定性检查 | 无系统性 adherence grader；effect 只在笔记域有 golden set |
| 长度控制臂 | skill-ab-testing 只做新旧版 A/B | 缺"等长无关文本"对照——我们的 skill 收益可能部分是长度效应 |
| per-model 接受会过期 | profile 分离 + model-switch 有意识 | 无"换模型重跑 skill eval"的强制钩子（evolver 可挂） |
| 分享 ideas 而非 text | provenance 字段 + description 57 字触发词 | 要点级假设清单未成 SKILL.md 标配 |
| listing 成本与选择劣化 | 当前会话 skill 列表已极长（数百个） | 正中 L1 要害：每次注入全列表，选对率随池子增大下降 |
| 65.7% 收益来自程序锚定 | 用户的 SOP 类 skill（duck-five-stage-standup 等"下次直接抄"级文档） | 印证用户"文档必须具体到命令+参数+坑表"的定调——程序锚定才是收益主体 |

- 相关笔记：[[2026-08-06-SkillUse]]（skill 调用行为）、[[2026-08-17-SkillShapley技能步骤归因估值]]（要点级归因——正是文中"attribution 消融"的同构实现）、[[2026-08-15-SkillMisevo技能误进化]]（harmful 案例）、[[2026-09-01-Agentic-Skills系统基础-六元组九阶段生命周期与安全]]（安全面互补：本文补 26.1% 漏洞率+扫描器绕过数据）。
- 与量化域同构：预注册读数规则=回测防过拟合的前注册协议；等长控制=因子归因中的 beta 剥离；per-model 过期=策略容量随市场状态漂移。

## 查询拓展

- `claude plugin eval` 官方文档（with/without 消融模式+确定性 grader+按模型行）——可直接借鉴做 Hermes 的 skill eval runner。
- Vercel《AGENTS.md outperforms skills in our agent evals》——always-on 文档索引 100% vs skill 53%，对"文档型 vs skill 型"注入方式的选型有直接参考价值。
- SWE-bench-Live (2505.23419) / SWE-rebench (2505.20411)——训练截止后采集的真实仓库任务+fail-to-pass 测试，eval 集的自然来源。
- Agentic Context Engineering (2510.04618)——"从基线失败构建要点"循环的 +12.3% 实证，是 evolver 的理论靠山。

## 趋势判断

1. **Skill 市场将从"格式合规"走向"带 eval 交付"**：agentskills.io 规范只定义了加载不定义测试，本文的四件套交付（text+points+evals+results）大概率被吸收进平台标准，"tested on <model, date>"会成为 marketplace 字段。
2. **Listing 膨胀是下一轮治理对象**：池子 100 个选对率 3.3% 的数据会推动两层分化——高频 skill 显式路由（hook/命名规则），长尾 skill 退到按需投喂（zero footprint, on-demand 打印）。P6 臂的设计已给出方向。
3. **Adherence/effect 双分数会成为 agent 工程的标准仪表**：与 LLM-as-Judge 校准协议（先对人工标注测一致性）合流，"judge 是意见直到被校准"会成共识。
4. **Skill 安全从扫描走向评审**：26.1% 漏洞率+扫描器 1 小时绕过的数据意味着市场端强制扫描只是起点，企业端会回到"陌生人 PR"流程。

## 指南分析

**决策树（照抄可用）：**

- 要不要装这个共享 skill？→ 先提取要点；提不出要点→不装；提得出→baseline+skill+等长控制跑几十个自己的任务，读双分数。
- 要不要为某任务写 skill？→ 先跑裸基线读失败；失败不重复→需要的是更好的任务描述不是 skill。
- adherence 高但 outcome 平？→ 逐点消融；只留删掉会掉 effect 的点，其余是 doctrine。
- adherence 低？→ 只改措辞：缩短、触发条件放第一行、示例换成 agent 实际语言；adherence 不达标前禁碰要点。
- 收益好但太贵？→ 先砍次要点和劝服文本；低词数下 effect 必须保持，否则就是真权衡，拿两个数字让预算持有者拍板。
- 有人问"这 skill 有效吗"？→ 要四个字段：模型、版本、基线、控制臂。缺任何一个，答案是"未测量"。

## 拓展应用推荐

1. **给 Hermes 高频 skill 补 adherence grader**（直接可做）：挑 5 个 SOP 类 skill（duck-five-stage-standup / note-dual-format / x-content-extraction），从会话日志写规则化判据（如"用了现成脚本而非手搓"），挂进 skill-review 的巡检项——这是把本文 L7 落进现有体系的最小动作。
2. **notes-eval-gate 升级为双分数**：现有六项确定性检查是 adherence；补 effect 侧（线上笔记的引用回链数/被后续笔记关联次数）作为滞后质量信号。
3. **evolver 加"换模型重验"触发器**：model-switch 或 gateway 模型版本变更时，自动把 provenance=top 的 10 个 skill 标记为 eval-pending——对应 L10 的"接受会过期"。
4. **skill-stress-test 补长度控制臂**：翻车对照之外加"注入等长无关文本"组，区分"skill 想法有用"vs"任何额外文本都有用"。

> 吸收与优化：本文对用户体系的最大单点价值是**双分数裁决规则**——低 adherence 改文本、高 adherence 平 effect 删想法。当前 evolver/skill-review 只看结果好坏，无法区分这两种失败，正是文中"冤枉好想法/服从坏想法"的隐患。实施路径见上方推荐 1。
