# Agent 技能的测试时进化：SkillTTA / Trace2Skill / 下游适配实证

> 来源：arXiv 2605.16986（SkillTTA）/ 2605.21810（Trace2Skill）/ 2607.03238（下游适配实证研究）
> 关联：Hermes 递归自我进化循环（L1 扫描→L2 沉淀→L3 对账）；夜间自学习 2026-09-29

## 一句话结论（内容整理）

「技能不在训练时定死，而在测试时合成/进化」正在形成一个小型研究簇：SkillTTA 证明按任务临时合成技能比扩大上下文更省算力且上限更高；Trace2Skill 把自然语言技能当作可进化策略，用 oracle-mutator-selector 循环在 EDA 硬件 agent 上免微调提升；实证研究给出**复用悖论**——1126 个下游适配实例中开发者大量重写技能内部逻辑。三者合起来指向：**技能文本本身就是策略参数**。

## 三篇核心发现（指南分析）

### 1. SkillTTA（2605.16986）：测试时算力→能力转化难题

- 问题命名：**test-time compute-to-capability conversion**——加上下文/加 rollout 不必然涨能力。
- 方案：检索任务相关训练轨迹 → 为固定参数的 solver **临时合成一个技能**（不永久污染技能库）→ 用 **MPO（meta prompt optimization）** 优化"写技能的那个策略"，更新限定在 benchmark 特定的原子槽位，降低间接观测的方差。
- 战绩：ALFWorld / SpreadsheetBench / BigCodeBench / WebShop 四基准超 SOTA 复用与采样基线，**更低算力拿到更高上限**。

### 2. Trace2Skill（2605.21810）：技能=可进化策略（EDA 域）

- 场景：复杂 Verilog 设计问题（CVDP），稀疏隐藏 verifier 失败难恢复。
- 机制：挖掘重复 rollout 轨迹的成功/失败模式 → 转成密集诊断与 oracle 教训 → **oracle / mutator / selector 循环**产出任务专用技能，指导后续搜索/编辑/验证/恢复。
- 关键设计：有界运行时密集 verifier 反馈（只给消毒后的功能观测，隐藏 harness 与参考解）。
- 零模型微调，纯技能层进化。

### 3. 下游适配实证（2607.03238）：复用悖论

- 首个对公开 fork 中技能适配的实证研究：**1126 个适配实例、6 个主流技能仓库、46 种适配模式归入 13 族**。
- 核心发现（复用悖论）：技能本为易复用而生，下游开发者却花大量精力**重写技能做什么**、修可发现性、跨工具/语言翻译。
- 启示：需要更好的抽象、标准化接口、自动化适配。

## 对 Hermes 自进化系统的映射（归纳总结）

| 论文机制 | Hermes 现状 | 缺口 |
|---|---|---|
| SkillTTA 临时技能（不污染库） | 无——所有沉淀都进永久 skills/ | **临时技能层**：一次性任务合成的 prompt 放 /tmp 而非技能库，验证有效才转正（正好对上 skill-ab-testing 的候选版本思路，可合并） |
| Trace2Skill oracle-mutator-selector | evolver（错误模式→规则沉淀）有 mutator+selector，**无 oracle 密集反馈** | 验证器是四接口最弱环节（用户已有判断）——Trace2Skill 的"有界密集反馈"设计值得抄：只暴露功能观测不暴露内部 |
| MPO 原子槽位更新 | skill patch 是全文级 | 无槽位概念，改写方差大；Content Meow 的 prompt 优化可借鉴"限定原子槽位"降方差 |
| 复用悖论 | skills/ 已 400+，索引靠分类 | **可发现性债**：下游适配实证说明库越大重写越多——skill-review 定期合并机制是对的，另需"适配即信号"：用户改过我给的技能文本=该技能抽象不佳的 L1 信号 |

## 与 DUCK/用户关注线的交叉（趋势判断）

- 用户 09-22 定调的「递归自我进化：死法→发射前机械门禁」= Trace2Skill 的 trace 挖掘→技能进化，**但我们是手工 oracle（用户目测）**。Trace2Skill 证明 oracle 可以是程序化 verifier（launch_gate.sh 的 11 条检查就是雏形）——方向已被验证，缺的是把 guard 输出从"拦截/放行"升级为"密集诊断信号"反馈进技能文本。
- 周论文「软件 Agent 与物理 Agent 策略改进同构性」第二论据：技能文本=LLM agent 的策略参数，与 ONNX 权重=RL agent 的策略参数同构，两者都有"底座冻结+轻量层进化"（EXPO edit head ↔ SkillTTA 临时技能）。

## 行动项（拓展应用推荐）

1. evolver 技能补 Trace2Skill 引用与"密集诊断信号"改造方向（等用户拍板，先记笔记）。
2. session-evolution-scan 的 L1 信号定义扩展：**用户对技能文本的手工改动**也计入候选（现在只扫纠偏对话）。
3. 临时技能层提案：一次性合成 prompt 默认 /tmp，验证通过走 skill-ab-testing 转正——防止技能库膨胀加剧复用悖论。

## 查询拓展与出处（引用与关联）

- https://arxiv.org/abs/2605.16986 （SkillTTA）
- https://arxiv.org/abs/2605.21810 （Trace2Skill）
- https://arxiv.org/abs/2607.03238 （An Empirical Study of Downstream Adaptation for Agent Skills）

## 相关笔记
- [[2026-09-28-把经验教给AI的Skill制作方法论]]
- [[2026-09-26-agent技能自进化三篇]]
- [[2026-09-29-Jev与LangGraph构建生产系统]]
