# Ecdysis 论文：模型特异迁就 vs harness 级修复——跨任务失败模式聚合与 FDCR 四角色协作拆解（1.84×/18.56%）

> **来源**：X/Twitter @dair_ai 推荐论文 → arXiv:2609.11677（cs.SE/cs.AI）
> **论文**：《Ecdysis: Efficient and Effective Training of Runtime Harnesses for LLM Agents》
> **抓取方式**：arXiv HTML 全文直读（60.9K 字符，含完整实验表）
> **笔记日期**：2026-09-12（21:18 date 实测确认）
> **关联笔记**：harness 簇全系列 14 篇——**本篇是簇的学术收口**（之前多为工程/概念文，本篇给出实验证据）；SoL-Pi（152→4 的 RSI 对应）、自进化 Harness 与记忆（SkillsBench 负结果）、Loop 与 Graph（learning edge）、Skill 九条（腐烂与重跑）

---

## 零、结论先行

**论文核心洞察：执行失败不是同等可行动的——有的反映模型特异局限，有的反映 harness 系统性缺陷；把单个失败当直接修改信号会过度迁就模型（model-specific accommodation），损害跨模型泛化。Ecdysis 用"跨任务复发的失败模式"作为系统性缺陷的更强证据，配合 FDCR 四角色协作诊断，1.84× 训练加速 + 18.56% 推理精度提升 + 跨 LLM 泛化更强 + token 更省 + 1/4 数据匹配全量训练。** 对我们最深的增量：①"model accommodation ratio"（模型迁就比）的量化框架——我们 evolver/sensor-grid 从未区分"修 harness 还是迁就模型"；②**"至少两个不同任务复发的失败才建立跨任务机制"**——与我们 error-case-library 的"repeat 2 次=系统性"判定完全同构（独立提出，论文验证）；③FDCR 的 Analyst/Critic/Engineer/Moderator 四角色与我们 Dev/OPM/Data Meow 团队结构惊人相似。

## 一、论文要解决的两大实践问题

| 问题 | 现状 | Ecdysis 解法 |
|------|------|-------------|
| **搜索慢** | 每个候选 harness 需要重复 agent 运行+代码编辑 | 批级失败聚合——每轮只调一次 coding agent（N_round ≤ N_serial） |
| **修复过拟合** | 每个失败都当 harness bug 打补丁——即使模型才是原因 | 跨任务复发模式才修——隔离模型特异迁就 |

> "An observed failure can reflect either model-specific deficiencies or systematic harness deficiencies, and directly optimizing against individual failures can lead to unnecessary model-specific accommodation."

## 二、核心理论：ΔH 分解与迁就比 t

把一轮 harness 更新量分解为：

```
ΔH = t·ΔH_model + (1−t)·ΔH_harness,  t ∈ [0,1]
```

- **t = 模型特异迁占比**：大 t 能快速解决观察到的问题但**过拟合到当前模型和训练任务**
- 假设：**跨不同任务实例复发的失败模式**是系统性 harness 缺陷的更强证据（作为归纳偏置而非因果证明）
- 实验验证：降低 model accommodation 与更强的跨模型泛化**相关**

## 三、方法：三阶段 × 两组件

### 3.1 演化循环（每轮）

```
① 执行训练任务收集失败证据（trajectories → 结构化失败记录）
② FDCR 诊断 → 结构化修改规格（specification）
③ coding agent 按规格改 harness → 候选 H_c
④ 验证：J_train(H_c) > J_train(H_{i-1}) 才接受，否则保留旧版
```

**接受准则只看训练集总分**——不要求每个任务都改善。

### 3.2 批级失败聚合（Batch-Level Failure Aggregation）

- 失败记录（任务 ID/失败决策/终止原因/工具调用史/执行上下文）组织成**失败组**
- **优先覆盖 ≥2 个不同任务的组**——单任务重复失败不足以建立跨任务机制
- 失败组是**诊断证据非强制修复目标**——候选 harness 不必解决每个组
- 效率收益：每轮一次 coding agent 调用 vs 每失败一次

### 3.3 FDCR（Failure-Driven Collaborative Refinement）四角色

| 角色 | 职责 | 对应我们 |
|------|------|---------|
| **Analyst** | 识别 harness 缺陷，提出最小针对性更新 | Dev Meow（定位根因） |
| **Critic** | 评估提案风险：过宽触发/误阻合法行为/违反运行时契约/已成功任务回归 | Data Meow（审计） |
| **Engineer** | 追踪共识与分歧，标记待澄清问题 | OPM Meow（协调） |
| **Moderator** | 保守仲裁——合并提案/解决分歧/优先复发模式/避免不必要变更 | ubot（CEO 收口） |

**关键分离**：FDCR 诊断（不碰代码）与 coding agent 实施（按规格改）分离——**分析与实施分离**，与我们 AGENTS.md 准则 2"执行/评判分离"同构。

## 四、实验证据（精选表）

### 4.1 基线启示（Preliminary，六组 Qwen3 平均）

| 配置 | 准确率 |
|------|--------|
| 移除全部 harness 层 | 29.72% |
| 人工固定配置 harness | **50.28%** |
| 失败后串行修改（coding agent） | 43.33% —— **低于人工配置！** |

**关键启示**：朴素的"失败即修"不仅不如人工配置，还倒退——**无原则的失败驱动演化比不动更糟**。这是 SoL-Pi 152→4 死亡率的学术版证据。

### 4.2 主结果（五模型 × AgentBench 等）

| 模型 | Direct | Human-Aug | Self-Evo | Ecdysis w/o FDCR | **Ecdysis w/ FDCR** |
|------|--------|-----------|----------|------------------|---------------------|
| Qwen3-8B | 10.0 | 85.0 | 90.0 | 85.0 | **90.0** |
| Qwen3-14B | 28.3 | 80.0 | 85.0 | 85.0 | **90.0** |
| Qwen3-32B | 40.0 | 75.0 | 85.0 | 85.0 | **90.0** |
| MiniMax-M2.7 | 80.0 | 78.3 | 83.3 | 86.7 | **90.0** |
| Llama-3.1-8B | 5.0 | 68.3 | 70.0 | 80.0 | **90.0** |

**Llama-3.1-8B 最戏剧**：Direct 5% → Ecdysis 90%（+85pt）——弱模型从 harness 演化获益最大，**印证 Minara"harness 可测量且对弱模型影响更大"**。

### 4.3 效率与成本

| 指标 | 结果 |
|------|------|
| 训练加速 | 最高 **1.84×** |
| 推理精度 | **+18.56%** |
| 训练时间（AgentBench） | Self-Evo 1955s vs Ecdysis 1137s/1891s |
| 缓存命中率 | FDCR 94.59%（vs Self-Evo 92.41%） |
| 总成本 | $1.51-1.83 vs Self-Evo $2.03 |
| **1/4 数据** | Reduced $0.291 vs Full $5.763——**20× 成本差**，精度 71.67 vs 75.00 |

### 4.4 跨 LLM 泛化

Ecdysis 训练的 harness 换模型仍强——因为迁就比 t 低（修复的是系统性缺陷而非模型怪癖）。

## 五、与本周 harness 簇的交叉对照（学术收口）

| 论文概念 | 簇中对应 | 互证关系 |
|---------|---------|---------|
| 失败≠同等可行动 | Loop/Graph"错误的缺失不是正确的证据" | 同构 |
| 跨任务复发才修 | error-case-library"repeat 2 次=系统性" | **独立同构**（我们 09-10 从实战提炼，论文用实验验证） |
| t（迁就比）量化 | 无对应 | 🟡 **最大增量**——我们从未量化过 |
| FDCR 四角色 | Dev/OPM/Data Meow + ubot | 结构同构 |
| 分析/实施分离 | AGENTS.md 准则 2 | 同构 |
| 接受准则：总分提升才接受 | golden set 门禁（六项全绿才通过） | 同构 |
| "至少 2 任务"阈值 | SoL-Pi 40:1 死亡率的正面解法 | 互补 |
| 失败驱动演化倒退（43.33<50.28） | SkillsBench -8~-11（考前自写 skill 包降分） | **互证**——两个独立负结果 |
| 1/4 数据匹配全量 | "Complexity earned by observed failure"（Harness 指南） | 互补 |
| 弱模型获益最大 | Minara 笔记（58 分差） | 互证 |

## 六、对 evolver/sensor-grid 的改造启示

| 启示 | 现状 | 动作 |
|------|------|------|
| **区分"修 harness vs 迁就模型"** | evolver 不区分——所有错误模式都沉淀为规则 | 下次 audit 时给 error-case 加 `attribution` 字段（model/harness/ambiguous） |
| **跨任务复发阈值** | "repeat 2 次"是会话级不是任务级 | 升级为"≥2 个不同任务类型复发"才入主线 |
| **接受准则** | evolver"门禁后写入"无总分对比 | skill-ab-testing 已有候选版机制——补"总分必须提升" |
| **FDCR 分离** | 一体化流程 | delegate_task 已支持多角色——evolver 大改时可参考 |

**不立即动**（分析阶段禁改代码），记入下次 hermes-system-audit 的 checklist。

## 七、批判性审视

1. **基准规模小**：主表准确率以 5% 为粒度（60 任务×5=300？）——90 vs 85 差 3 个任务；无置信区间报告（部分表 ±std 有，主表没有）
2. **"1/4 数据"的 Reduced 版精度 71.67 vs Full 75.00**——降了 3.3pt，说"comparable"略乐观，但成本 20× 差距下确实划算
3. **t（迁就比）的测量靠"细粒度人工分析"**——论文自己说是 manual，无自动化方法——**最核心的理论量无法自动测量**，限制了实践迁移
4. **FDCR 固定轮数、顺序执行角色**——为什么这个配置？没消融角色顺序/轮数
5. **harness 的定义偏代码层**（"the source code of the current harness"）——prompt 层/skill 层的演化未覆盖（我们的 skill 库比这个宽）
6. **训练时模型冻结**——model+harness 联合演化（另一篇 arXiv 摘要提到的方向）未讨论
7. **单机单领域**（AgentBench/推理任务）——生产环境多用户多领域的 harness 演化未验证

## 八、金句提取

> "Execution failures are not uniformly actionable: they may reflect model-specific limitations rather than harness deficiencies."

> "Treating individual failures as direct modification signals can therefore over-accommodate the evolving model and compromise harness generalization."

> "Cross-task recurrence is used as an inductive bias rather than as proof of causal attribution."

> "Serially modifying the harness with a coding agent after each failure achieves 43.33%, which remains below the 50.28% achieved by the fixed human configuration."（失败即修比不修更糟）

> "Effective harness evolution requires not only correcting failures, but also determining which failures constitute reliable evidence for changes that generalize beyond the model and tasks used during evolution."

## 九、局限性

1. 本笔记基于 arXiv HTML v1 全文（60.9K 字符）——图表以 HTML 表格还原，部分公式渲染不完整
2. §4.2 主表缺置信区间——批判 1 基于表面观察
3. §六改造启示是分析非实施——evolver 实际改造需另开会话
4. 论文代码未公开（GitHub 链接未见）——复现依赖细节不足
5. 与 SoL-Pi/SkillsBench 的对照基于笔记记忆，未重读原文核对数字

## 出处标注

| 章节 | 来源类型 |
|------|---------|
| 一至四 | **原文忠实还原**（arXiv HTML 全文直读） |
| 五 | **体系映射**（本周 14 篇笔记交叉） |
| 六 | **改造启示**（本笔记扩展，未实施） |
| 七 | **批判性审视**（本笔记扩展） |


## 相关笔记

- [Harness-Engineering 19层完整指南](./2026-09-12-Harness-Engineering完整指南-19层从prompt到环境的工程纪律-LunarResearcher体系化拆解.md) — harness 簇收官纲领，本篇是学术收口
- [Loop与Graph-停止babysitting-agent](./2026-09-12-Loop与Graph-停止babysitting-agent的两层架构-循环内验证与图间编排拆解.md) — 循环内验证与FDCR四角色互补
- [Skill九条原则-Bibryam三幕生命周期](./2026-09-12-Skill九条原则-从被选到活着-Bibryam三幕生命周期拆解与Hermes-skill库对照审计.md) — skill腐烂与重跑，Ecdysis提供批量聚合训练法
- [自进化Harness与记忆-三种写法](./2026-09-11-自进化Harness与记忆-三种写的不可混同-LiveSWE-DGM-SWE-Exp实证拆解.md) — 三种写法对照，Ecdysis给出批量聚合改进
- [SoL-Pi英伟达自我优化Harness](./2026-09-11-SoL-Pi英伟达开源自我优化Harness-四大机制与152选4的RSI流水线拆解.md) — RSI优化，Ecdysis训练数据1/4精选
- [Ecdysis精简版](./explore/2026-09-12-Ecdysis-Harness自进化失败归因.md) — 同源精简版笔记
