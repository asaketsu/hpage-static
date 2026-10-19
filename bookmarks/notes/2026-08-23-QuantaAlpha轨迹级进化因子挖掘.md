# QuantaAlpha：轨迹级进化式 LLM 因子挖掘框架

#量化交易 #LLM因子挖掘 #自进化Agent #alpha #CSI300

**出处**：QuantaAlpha: An Evolutionary Framework for LLM-Driven Alpha Mining. 上海财经大学 AIFin Lab, 2026-02. arXiv:2602.07085. 代码: github.com/QuantaAlpha/QuantaAlpha

---

## 一、内容整理

### 1.1 定位与核心问题

金融市场监管噪声、非平稳，因子挖掘对回测噪声和 regime 突变极其敏感。现有 LLM agentic 框架（AlphaAgent、RD-Agent）三大缺陷：

| 缺陷 | 表现 |
|------|------|
| 脆弱可控性 | 迭代精化由噪声回测反馈驱动，导致语义漂移，逐步偏离预期经济机制、滑向伪相关 |
| 信任缺失 | 随机重生成不继承已验证的经验，无 lineage 可审计 |
| 探索受限 | 过度开发初始种子邻域，因子拥挤（crowding），长周期发现能力弱 |

### 1.2 核心抽象：挖掘轨迹（mining trajectory）

把每次端到端挖掘（假设生成→因子构造→代码实现→回测评估）表示为轨迹 τ=(s0,a0,s1,...,sn)，终端奖励 R(τ)=L(f_τ(X),y)−λR(f_τ)。目标：找轨迹生成机制 π 最大化 E[R(τ)]。**进化对象是轨迹而非因子表达式**——这是与遗传编程/AlphaEvolve 类方法的本质区别。

### 1.3 单轨迹工作流（多 Agent 分工）

1. **假设生成（idea agent A_i）**：三输入——当前市场观察/历史轨迹、金融理论先验、参数规格（如"10日高低点"），产出可操作的机制假设。
2. **可控因子构造（factor agent A_f）**：直接生成代码很脆（语法错误/依赖错配/语义漂移），引入中间层——**标准算子库 O + AST 抽象表示**。h→语义描述 d→符号表达式 f（叶节点绑 $high/$volume 等原始特征，内部节点是 TS_MIN/SMA/RANK 等算子）→AST→编译成代码；编译失败触发 LLM 修复。
3. **一致性验证（LLM verifier）**：检查 h↔d↔f 对齐 + f↔代码忠实性，失败则重写直到通过或预算耗尽。
4. **复杂度与冗余正则**：复杂度 C(f)=α₁·SL(f)+α₂·PC(f)+α₃·log(1+|F_f|)（符号长度+自由参数+特征数）；冗余用 **AST 最大同构子树** s(f_i,f_j) 对比既有 alpha zoo，超限直接拒绝重写。
5. **评估（evaluation agent A_e）**：标准化回测三组指标（预测力 IC 系/收益表现/风险控制），维护评估历史并总结成败因子的系统性模式。

### 1.4 进化机制：变异 + 交叉

**多样化规划初始化**：初始化 agent 被要求在语义与结构两层最大化假设互补性——信号源（价 vs 量）、时间尺度（短 vs 长）、机制类型（动量 vs 均值回归 vs regime 条件触发），避免过早收敛。

**变异（定位式修订）**：自反思诊断导致低终端奖励的最差决策节点 k，冻结 s0..sk 前缀，只重写 Refine(a_k)，其后步骤在固定前缀条件下重新生成，保持轨迹连贯。可改假设/符号表达式/代码，能引入机制级变化（换时间尺度、加 regime 条件）。

**交叉（已验证组件重组）**：从高奖励父代轨迹中识别持续贡献高累计奖励的片段（假设模板、构造模式、修复动作），合并成单一连贯子代。案例：Parent1"散户投机驱动的脆弱动量"+ Parent2"机构活动支撑的可持续动量"→交叉合成 Institutional_Momentum_Score_20D。

### 1.5 实验硬数据（CSI 300，Qlib 回测）

| 方法族 | 代表 | IC | ARR% | MDD% |
|--------|------|-----|------|------|
| 机器学习 | LightGBM | 0.0247 | 0.07 | 21.80 |
| 深度学习 | TRA | 0.0421 | 6.81 | 8.51 |
| 因子库 | Alpha158 | 0.0131 | 2.66 | 10.15 |
| LLM Agentic | RD-Agent (GPT-5.2) | 0.0531 | 9.91 | 14.82 |
| LLM Agentic | AlphaAgent (Claude-4.5) | 0.1092 | 16.48 | 8.14 |
| **QuantaAlpha** | **GPT-5.2** | **0.1501** | **27.75** | **7.98** |
| QuantaAlpha | Qwen3-235B（开源模型） | 0.1252 | 20.55 | 8.99 |

关键点：①QuantaAlpha 用 Qwen3-235B 就能打平甚至超过 AlphaAgent 用 Claude-4.5 的成绩——**框架收益大于模型档位收益**；②ICIR 0.9110，IC 稳定性极强；③CSI 300 挖出的因子迁移到 CSI 500 与 S&P 500，四年累计超额 **160% / 137%**，跨市场分布偏移下鲁棒。

回测口径：TopkDropout（topk=50，每次调仓换 5 只，等权），买入费 0.05%/卖出费 0.15%，次日开盘价成交，涨跌停 9.5% 视为停牌——执行假设相当严格（不是理想化成交）。

## 二、查询拓展

- **谱系定位**：FactorMiner（THU 2026-02，技能+经验记忆的自进化 agent，解决"相关红海"）、AlphaAgentEvo（SYSU/NTU ICLR 2026，进化导向 agentic RL）、Cognitive Alpha Mining（HKU ACL 2026，代码进化）、Chain-of-Alpha、AlphaCrafter（NJU 2026-05 全栈多 Agent）——2026 上半年 LLM 因子挖掘已爆发成独立赛道，QuantaAlpha 是其中把"进化单元"提到轨迹层级的代表。
- **与 AlphaEvolve/CSE 的承继**：论文自述受 AlphaEvolve（编码中心进化+重采样）与 CSE（可控自进化，随机生成→反馈驱动进化）启发，金融域适配点是低信噪比+非平稳下的稳定优化单元。
- **权威索引**：Awesome-LLM-Quantitative-Trading-Papers（github.com/Tom-roujiang/Awesome-LLM-Quantitative-Trading-Papers，229 star）系统收录该赛道论文+代码，是持续跟踪入口。
- **执行现实主义动向**：Beyond Agent Architecture（2026）与 TradeTrap（Shanghai AI Lab 2025-12）指出 LLM 交易系统普遍存在执行假设过度理想、可复现性差的问题——QuantaAlpha 的次日开盘成交+涨跌停约束口径是对此的直接回应，但换手率约束仍是事后过滤而非内生目标（论文自己承认）。

## 三、归纳总结

1. **进化单元的选择决定搜索稳定性**：在噪声环境里进化"轨迹"（含假设、构造逻辑、修复历史的完整决策链）比进化"表达式"抗噪——单点因子 IC 的噪声被轨迹级奖励平均掉，且 lineage 可审计。
2. **符号中间层是 LLM 生成金融代码的正确姿势**：AST+算子库把"自由文本→代码"拆成"假设→语义描述→符号表达式→编译"，每步可校验、可正则（复杂度/冗余），彻底解决语义漂移。这个模式对一切"LLM 生成可执行领域 DSL"的场景通用。
3. **框架收益 > 模型收益**：Qwen3-235B+QuantaAlpha ≥ Claude-4.5+AlphaAgent，对小团队是重要杠杆——不必追最贵模型，把搜索结构做对。
4. **与用户体系的共鸣**：变异=定位最差决策节点只改局部（同"根因定位后一次性干净重写"）；AST 同构子树去重=因子层面的"近邻冗余控制"（同 E13 语境门防止无语境形态复用）。

## 四、趋势判断

- 轨迹级进化会成为 LLM 因子挖掘 2026 年的主流范式：AlphaAgentEvo、QuantaAlpha、Cognitive Alpha Mining 三线同报，方法收敛点是把假设-代码-回测全链路作为可继承资产。
- 执行约束内生化是下一个竞争点：换手率、容量、交易冲击从后置过滤变成优化目标的一部分（QuantaAlpha 未做，论文明确列为开放方向）。
- 开源模型可用性意味着该类框架会在中小量化团队快速落地，2026 下半年预计出现 A 股全市场（而非 CSI 300）的开源复现与本土化改造。
- 对个人体系：短线连板池的样本量（30 股×280 日）远小于 CSI 300 容量，直接照搬会过拟合；可借鉴的是**结构与流程**（AST 中间层、轨迹 lineage、多样化初始化），而非回测结论。

## 五、关联分析

- **与 llm-factor-mining skill（Hubble 框架）**：Hubble 是单轮生成-回测闭环，QuantaAlpha 补上"跨轮经验继承"——变异/交叉算子本质是结构化的经验复用，对应 Hermes 侧的 error-case-library + experience-bank 机制。skill 可补一节"轨迹级进化参考"。
- **与 quant-evidence-governance**：三档判定（采纳-存档-证伪）与 QuantaAlpha 的轨迹奖励+verifier 双闸同构；其 AST 冗余控制可直接吸收进外源因子登记流程——登记新因子时先跑 AST 同构子树比对，防止"新瓶旧酒"。
- **与 stock-iron-rules 体系**：引擎的 score_stock 是手工铁律，QuantaAlpha 证明了 LLM 假设生成+符号约束在该粒度上可自动化；但 A 股短线 pool 的容量约束意味着落地形态应是"周级离线挖掘+人工采纳"，不是日内自动上线。
- **与自进化 Agent 谱系**：变异/交叉算子与 Agent 侧 Reflexion/经验沉淀是同一思想在两个域的投影——金融域多了"奖励可量化（IC/ARR）"这一优势，反而进化机制跑得更靠前。

## 六、拓展应用推荐

| 场景 | 用法 | 收益点 |
|------|------|--------|
| A 股因子研究离线管线 | 借 AST+算子库中间层改造 short_term_screener 的因子表达 | 因子可校验、可去重、可审计 |
| 外源信号登记 | 登记时跑 AST 同构比对 trading-learning-log 既有因子 | 拦截语义重复的"新因子" |
| 假设库建设 | 多样化初始化的互补性维度（价/量、短/长、动量/回归）直接用作假设枚举清单 | 搜索覆盖面系统化 |
| Hermes 技能进化 | 轨迹 lineage 思想用于 skill 演进审计（provenance 字段的深化） | 技能变更可追溯因果 |

## 七、指南分析

复现路径：①代码开源（github.com/QuantaAlpha/QuantaAlpha），回测底座是 Qlib，A 股数据天然适配；②最小闭环=算子库定义（TS_MIN/SMA/RANK 等二十个以内）+AST 校验器+单 LLM 调度，先跑通"假设→符号式→回测"单轨迹再做进化；③成本控制：每轮进化的 LLM 调用集中在变异诊断与交叉合成，Qwen3-235B 级模型即可；④对个人短线体系，建议只吸收"符号中间层+冗余控制+lineage"三件套，进化搜索留给容量足够的池子；⑤注意其回测含 9.5% 涨跌停约束，对 A 股短线（10%/20% 涨跌幅制度）需按板块调整参数。

## 相关笔记

- [多指标共振的深度剖析](~/explore/2026-08-23-multi-indicator-resonance-deep-dive.md) — 多因子合成共振的方法论
- [量价背离的深度剖析](~/explore/2026-08-22-volume-price-divergence-deep-dive.md) — 因子挖掘的量化视角
- [同花顺量化自动化](~/explore/2026-05-19-ths-auto-trader-latest-dynamics.md) — 交易执行侧
