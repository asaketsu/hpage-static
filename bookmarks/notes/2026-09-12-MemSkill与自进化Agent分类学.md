# MemSkill与自进化Agent分类学 #AI-Agent #记忆系统 #自进化

## 出处

- 主源1：Medium @Micheal-Lanham《Self-Evolving Agents: Real Learning, or Memory in a Costume?》(2026)
- 主源2：Shilong Liu《A Taxonomy of Self-evolving Agents》(lsl.zone, 2026-07)
- 辅源：MemSkill (arXiv 2602.02474) —— 本篇增量补充，论文本体精读见前篇 [2026-08-25-MemSkill记忆技能自进化](2026-08-25-MemSkill记忆技能自进化-从固定四原语到可进化技能银行.md)
- 检索路径：web_search "AI agent memory architecture self-evolution agent skills 2026" → 三源交叉精读
- 本篇定位：**增量研究**——前篇已覆盖 MemSkill 架构/RL训练/实验细节，本篇只写新增量：三档审计框架 + Model/Harness/Artifact 分类学 + Hermes 体系自审计

## 一、内容整理（忠实还原）

### 1.1 记忆 vs 学习之辩：三档划分

| 档位 | 定义 | 删库后能力存活？ | 代表 |
|---|---|---|---|
| L1 记忆累积 | 外部存储变富，生成器（模型）不变 | ✗ | GenericAgent、ReasoningBank |
| L2 策略级学习 | **使用记忆的策略**变了（检索/管理策略） | 部分（策略结构存活） | MemRL、AgeMem、Memory-R1 |
| L3 参数内化 | 技能进权重，运行时无需技能检索 | ✓ | SKILL0、SDAR |

2026 年诚实结论：大多数"自进化 agent"是有状态 agent + 结构化记忆，非强意义自学习。真正的分界线是 policy-learned management。

### 1.2 MemSkill 增量回顾（本体精读见前篇 08-25）

| 组件 | 职责 | Hermes 对应物 |
|---|---|---|
| Controller | 按当前 span + 记忆状态选 Top-K 技能（共享 scorer，技能库可增删） | 技能路由 = skills 索引 + adaptive-tool-selection |
| Executor | 固定 LLM，按选中技能指令产出结构化记忆更新 | memory-refiner / memory-write |
| Designer | **定期复盘 Hard-Case Buffer 失败案例，提炼/进化技能集** | error-case-library + evolver（差最后闭环一步） |

（架构图/RL训练细节/实验对比均见前篇，此处不重复。本篇只取一个新视角：**MemSkill 的 Designer 机制是 L1→L2 晋级的最便宜实现路径**——已有 Hard-Case Buffer 的系统只需补"定期复盘→技能进化"一步闭环。）

### 1.3 三因子分类学（Model / Harness / Artifact）

| 层 | 什么在进化 | 反馈 | 代表 |
|---|---|---|---|
| Artifact 迭代优化 | 产出物（算法/论文/策略） | 人工目标+评估 | AlphaEvolve、FARS（417h 166 篇 AI 论文 $180k） |
| Harness 自我改进 | prompt/记忆/工具/技能 | 任务成败信号 | GEPA、Mem0、Alita、**Hermes skills 体系** |
| 模型弱监督学习 | 权重 | 自生成/弱反馈 | SDAR、SKILL0 |

关键判词：**Artifact 优化改的是产出，Harness 改进改的是 agent 自身**——这是与我们最相关的分界。三问定位法：What evolves? What feedback drives it? Where does the loop close?（循环闭合在物理世界 → agent 成为构建/改进真实系统的新方式——对 DUCK-Pi_5 直接背书）

## 二、查询拓展（深挖实验数据）

**MemRL 硬数字**（L2 的最强公开证据）：ALFWorld 迁移准确率 MemRL **0.479** vs MemP 0.421 vs RAG 0.336；探索密集场景比 MemP 高 ~56%、比无记忆基线高 ~82%。训练后冻结记忆库、held-out 测试仍胜出——学到的是"记忆的效用结构"，不是"更多例子"。

**技能家族谱系**（2026 上半年爆发）：SkillRL（递归技能增强 RL）、SkillOS（技能策展）、Memento-Skills（agent 设计 agent）、SkillClaw（技能集体进化）、Trace2Skill（轨迹局部教训蒸馏）、AutoMem（记忆作为认知技能）、MemEvolve（记忆系统元进化）。共性：**技能 = 压缩上下文的容器 + 可进化的复用单元**。

**数据库类比**（最实用的工程心智模型）：加行 = 记忆；改 schema/索引 = 检索策略学习。agent 记忆含摘要/矛盾处理/选择性遗忘，schema 是"半符号半 prompt 编码"。

## 三、归纳总结

1. 「自进化」营销话术拆成三档审计：记忆累积 < 学到的记忆管理策略 < 参数内化；审计标准 = "删掉记忆库后能力是否存活"。
2. MemSkill 的核心贡献是把记忆操作原语变成**可进化的技能**，Designer（失败案例复盘→技能进化）是闭环关键。
3. 我们 Hermes 体系已有 Hard-Case Buffer（error-case-library）和技能进化机制（skill_manage patch），缺的只是"定期自动复盘→技能集变化"的全自动闭环——L1→L2 最便宜的晋级路径。
4. 三问定位法是评估任何自进化系统的万能尺子。

## 四、趋势判断

- 2026 是"技能进化"论文大年（SkillRL/SkillOS/SkillClaw/Trace2Skill 扎堆），共识正在形成：技能是 harness 层进化的最佳载体。
- 研究前沿从"存更多"转向"学管理"：Memory-R1/AgeMem/MemRL 都在把记忆操作变成 RL 可训练的策略动作。
- 参数内化（L3）仍是后训练方法非在线学习；对无法改权重的部署环境（我们），L2 是实际天花板。
- 分类学作者点名 Hermes 的 automatic reusable skills——我们的 skills 体系在学术界视野内。

## 五、关联分析（×Hermes 体系自我审计）

| 我们的能力 | 档位 | 证据 |
|---|---|---|
| 三级记忆+memory-refiner+RAG | L1 上部 | 删库后能力不存活 |
| evolver+error-case-library | **L1→L2 过渡** | 有 Buffer 有技能进化，缺全自动闭环 |
| sensor-grid+quality-gate+golden set | L1→L2 | 质量信号闭环有雏形 |
| 600+ skills 按需加载 | L1 | 技能即压缩上下文（与 MemSkill 同构），选择靠 LLM 判断非学习策略 |

三个缺口对应三条最便宜路径（Designer 启示）：①error-case-library 缺定期触发的"失败聚类→技能补丁"管线 ②技能缺淘汰信号（最后调用时间维度） ③五问审计清单可嵌入 skill-review 周检（技能压力测试常态化）。

## 六、拓展应用推荐

1. **evolver 闭环补全**（最优先）：给 error-case-library 加 cron 定期触发，聚类分析失败模式 → 自动生成 skill patch 候选 → 走 skill-ab-testing 验证后合入。
2. skill-health-tier 加"最后调用时间"维度：>90 天未触发的技能标记 dormant，周检时评估降级/合并。
3. 五问审计清单写进 skill-review 模板：每技能问"删掉它后任务表现掉多少"。
4. 三问定位法用于 agent-trading-safety / evolver 等自改进系统的年度审计。

## 七、指南分析（可操作清单）

- [ ] evolver 加 cron 触发（建议周频）：失败案例聚类 → 技能补丁候选清单
- [ ] skill-health-tier 巡检脚本加 last-used 时间戳字段（skills 元数据已有 provenance，加 invoked_at）
- [ ] skill-review 周检嵌入五问审计（删库存活/泛化/反馈源/复现成本）
- [ ] 观察项：MemSkill 的 span 级处理思想是否适用于 memory-refiner（当前 turn 级处理的效率对比）

## 内部资产关联

`evolver`、`error-case-library`、`sensor-grid`、`skill-health-tier`、`skill-review`、`memory-refiner`、`agent-reflection`（双轨反思）、`skill-stress-test`

## 相关笔记

- [MemSkill记忆技能自进化—可进化技能银行](./2026-08-25-MemSkill记忆技能自进化-从固定四原语到可进化技能银行.md) — 论文本体精读，本篇前置
- [MAPLE记忆增强规划与进化](./explore/2026-09-11-MAPLE记忆增强规划与进化.md) — 记忆×规划交叉近作
- Agent记忆长程前沿 2026（~/explore 目录）— 记忆系统跨会话迁移视角
