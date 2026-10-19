# QuantaAlpha 轨迹级进化因子挖掘与 FactorMiner 经验记忆：2026 自进化 Alpha 挖矿双范式

> **来源**：arXiv 2602.07085（QuantaAlpha）+ arXiv 2602.14670（FactorMiner）
> **原文链接**：https://arxiv.org/html/2602.07085v2
> **记录日期**：2026-09-04

**标签**：#量化因子挖掘 #LLM-Agent #自进化 #AlphaMining #A股

---

## 一、内容整理

### 1.1 两篇论文解决的同两个痛点

- **可控性脆弱**：迭代精化由噪声回测反馈驱动，导致语义漂移（semantic drift），更新逐渐偏离预期经济机制、滑向伪相关
- **经验不可复用**：多数方法依赖"瞬态上下文的随机再生成"，没有显式继承已验证的 rationale，因子缺乏可追溯谱系（lineage），难审计

### 1.2 QuantaAlpha：轨迹级进化（进化算子派）

把每次端到端挖掘（假设→因子→回测）视为**挖掘轨迹 τ=(s0,a0,...,sn)**，进化的对象是轨迹而非因子表达式：

- **多样化规划初始化**：初始假设集在语义/结构两层强制互补（信号源 price vs volume、时间尺度短 vs 长、机制动量 vs 均值回归），防过早收敛
- **变异（Mutation）= 定点修复**：自反思定位导致低回报的关键决策步 k，冻结前缀，只重写 ak（可改假设/符号表达式/代码/机制层如加 regime 条件），其余步基于固定前缀重生成保持连贯
- **交叉（Crossover）= 已验证模式复用**：从高回报父代轨迹中提取持续贡献高累积回报的片段（假设模板/因子构造模式/修复动作）重组为子代——显式继承已验证决策，谱系可信
- **生成三重门控**：①语义一致性验证（hypothesis↔符号表达↔代码 LLM verifier，不过就重写）②复杂度正则 C(f)=α1·SL+α2·PC+α3·log(1+|Ff|) ③冗余控制（AST 最大同构子树 vs alpha zoo，超限拒绝重写）

### 1.3 FactorMiner：技能+经验记忆（记忆派）

- 轻量自进化 agent：模块化挖掘技能（Modular Mining Skill）+ **经验记忆**（Experience Memory）持续积累
- 记忆的不是因子本身，而是"什么有效、什么失败、为什么"的结构化经验
- 产出 **110 个可解释公式化因子库** + 标准化评估协议，形成可复现发现资产
- 核心约束："Correlation Red Sea"——随库增长新信号发现越来越难（500 候选过相关性过滤活 3 个），FactorMiner 在库扩张时保持低冗余

### 1.4 QuantaAlpha 关键实验数据（CSI 300，测试期 2022-01~2025-12）

- **GPT-5.2 下 IC=0.1501、ARR=27.75%、MDD=7.98%**；全基线最优
- vs RD-Agent（GPT-5.2）：IC +0.0970、ARR +17.84%、MDD −6.84%
- vs AlphaAgent（GPT-5.2）：IC +0.0535、ARR +12.21%、MDD −4.91%
- 消融：**去 Mutation 损失最大**（IC −0.0292、ARR −9.81%）> 去 Planning（ARR −7.78%、MDD +2.73%）> 去 Crossover（IC −0.0070、ARR −2.82%）
- 门控消融：**去复杂度控制策略级损失最大**（年化超额 −8.44%、MDD +2.57%）
- 零样本跨市场：CSI 300 挖的因子直接部署 CSI 500 累计超额 ~160%、S&P 500 ~137%（4 年）
- Alpha 衰减诊断：2023 年 A 股风格切换（大盘核心资产→小盘题材+日内噪声+隔夜跳空），基线崩塌，QuantaAlpha 靠结构性因子（Mean-Reverting Range Deviation、Overnight Gap Structure）穿越 regime

### 1.5 底座模型横评（RD-Agent 行内的规律）

Qwen3-235B < Deepseek-V3.2 < Gemini-3-pro < Claude-4.5-sonnet < GPT-5.2 单调递增——因子挖掘质量对底座推理能力高度敏感，框架收益独立于模型。

## 二、查询拓展

### 2.1 与既有四代架构谱系的关系

已有笔记（[LLM量化因子挖掘2026](2026-07-29-LLM量化因子挖掘2026-从Prompt循环到自进化架构.md)）梳理的三代：prompt 循环 → 程序级生成 → RFT 内化。QuantaAlpha 开出第四条路：**不改参数、不堆 prompt，进化"工作流轨迹"本身**——与 AlphaEvolve（代码中心进化）同族但把进化单元上移到假设-构造-修复全链路。

### 2.2 AST 同构子树冗余度量

把两个因子表达式解析成 AST，最大同构子树的节点数作为结构相似度。相比相关性过滤（需回测后算），AST 匹配在**生成时即可拦截**近重复结构——把"相关性红海"的过滤从评估阶段前移到生成阶段。

### 2.3 Hubble 框架（Semantic Scholar 检索发现的同族工作）

LLM + 领域算子语言 + AST 执行沙箱 + 双通道 RAG + family-aware 选择，联合优化有效性/多样性/可解释性/家族级泛化——与 QuantaAlpha 的符号中间表示路线趋同，2026 年中该方向正在收敛。

## 三、归纳总结

### 3.1 双范式对照

```
QuantaAlpha（进化算子派）          FactorMiner（记忆派）
├─ 进化单元：轨迹（假设→因子→回测）  ├─ 记忆单元：经验卡片（成败+归因）
├─ 探索机制：Mutation 定点修复       ├─ 积累机制：Memory 持续沉淀
│           + Crossover 模式复用    ├─ 产出：110 因子库+标准协议
├─ 门控：一致性/复杂度/冗余三重      ├─ 约束：Correlation Red Sea
├─ 强项：跨 regime 稳健性           ├─ 强项：轻量可复现
└─ 数据：CSI300 IC 0.1501          └─ 定位：高频/微观结构因子
```

### 3.2 可复用的四条设计原则

- **谱系可追溯**：每个因子记录完整进化路径（哪个父代哪个片段），审计与复盘有据
- **生成时门控 > 评估后过滤**：AST 冗余检查在生成阶段拦截，省回测算力
- **假设驱动 > 表达式驱动**：Crossover 合成的是新假设而非公式平均——保证子代捕获新颖市场机制
- **经验记忆沉淀成败归因**：不只存成功因子，失败模式同样是一级公民

## 四、趋势判断

### 趋势1：因子挖掘的进化单元从表达式上移到轨迹/工作流
依据：QuantaAlpha 消融显示 Mutation（机制级修改）> Crossover > 初始化；AlphaEvolve/CSE 同族进化范式在 2026 集中出现。

### 趋势2：门控三件套（一致性/复杂度/冗余）将成为 agentic 因子挖掘标配
依据：三者消融全部非平凡贡献，缺任何一个性能显著退化；Hubble 等并行工作独立采用同构设计（AST+算子库）。

### 趋势3：A股 regime 切换（2023 风格切换）成为因子框架的试金石
依据：基线在 2023 集体崩塌而 QuantaAlpha 穿越的结构性因子分析；与我们的 Wyckoff 周期模型"先判阶段再建议"哲学同构。

## 五、关联分析

### 5.1 与 stock-iron-rules / quant 体系的关联

- **AST 冗余门控可直接植入 short_term_screener.py**：我们 30 只备选池+14 条铁律本质是"因子库"，新信号入池前用 AST/逻辑结构比对防重复——与 quant-evidence-governance（外源因子本地验证）互补
- **经验记忆 ≈ error-case-library + experience-bank**：FactorMiner 的记忆哲学与猫仔"两个本本"体系完全同构——成败归因沉淀为一级公民，跨会话复用。已有 EC 条目机制就是 QuantaAlpha 的 trajectory summary
- **2023 regime 切换诊断与 Wyckoff 周期判定互证**：论文用风格轮动解释基线崩塌，我们用吸筹→拉升→派发→回落阶段模型——两者可在 cycle-records.json 上对齐验证

### 5.2 与既有因子挖掘笔记的关联

- 与 [QuantaAlpha-开源框架](2026-07-16-QuantaAlpha-开源框架.md)（工程侧）互补，本篇补齐算法侧（轨迹进化算子+门控消融全数据）
- 与 [RD-Agent-Quant](2026-05-18-RD-Agent-Quant-multi-agent-quant-framework-deep-dive.md) 形成对照组：RD-Agent 无生成门控被 QuantaAlpha 全面超越（IC 差距 0.097）
- 与 [LLM量化因子挖掘2026-进化搜索与认知Agent](2026-06-16-LLM量化因子挖掘2026-进化搜索与认知Agent.md) 的三代谱系衔接为第四代

## 六、金句摘录

> 「500 candidate factors, and after correlation filtering, maybe 3 survive.」— FactorMiner 对相关性红海的量化描述

> 「mutation broadens exploration via mechanism-level variations, while crossover reuses validated trajectory segments」— 两算子分工的一句话定义

## 七、行动启示

- **P1**：把 AST 冗余检查思路引入 stock-iron-rules 的信号池管理——新铁律/新因子入库前做结构去重（可用 Python ast 模块比对表达式树）
- **P2**：QuantaAlpha 开源（github.com/QuantaAlpha/QuantaAlpha），可在 asa 上跑 CSI300 复现；与 microduck 训练错峰使用 asa
- **P2**：Mutation 定点修复思想可用于交易策略复盘——定位失败决策步（入场日信号重建）只重写该步而非全盘推翻，与我们"进化太慢=修必须进算法本体"的用户铁律一致

## 八、拓展应用推荐

- 轨迹级变异+交叉算子可迁移到 **DUCK-Pi_5 训练超参搜索**：把每次训练配置→reward 曲线→eval 结果视为轨迹，CMA-ES 之外的另一条黑盒优化路径
- 经验记忆卡片结构（假设/结果/归因/适用 regime）可直接作为 error-case-library 条目 schema 的升级参考
- 底座横评数据（GPT-5.2>Claude-4.5>Gemini-3>Deepseek>Qwen3）可作为我们选择因子研究 LLM 的参考矩阵

## 九、指南分析

实践指南价值在**门控的工程实现**：①AST 冗余用最大同构子树节点数，Python 可用 difflib 或自写树匹配实现，无需重型依赖；②一致性验证是独立 LLM 调用，成本约为生成调用的 1/3，值得付出（消融显示全关性能崩得最狠）；③复杂度正则的三个分量（符号长度/自由参数/特征数）权重 α 需在验证集调，论文未给出具体值是复现的主要不确定点。边界：CSI300 大盘股训练的因子零样本迁移到我们的短线题材股场景未经验证——论文自己的分析表明 2023 后小盘题材 regime 下结构性微观因子更稳，方向一致但强度需回测。


## 相关笔记

- [2026-08-30 R&D-Agent(Q) 卖方实测与 AlphaAgentEvo（~/explore）](../../../explore/2026-08-30-rd-agent-field-test-alphaagentevo-two-routes.md) — LLM 因子挖掘另一条进化路线，本文 QuantaAlpha 轨迹级路线的直接对照系
- [QuantaAlpha LLM 驱动 Alpha 挖矿（~/explore，2026-06-28）](../../../explore/2026-06-28-quantaalpha-llm-driven-alpha-mining.md) — QuantaAlpha 早期版本精读，本文为 2026 进化版增量
- [量价关系进阶-换手率](./2026-08-21-量价关系进阶-换手率.md) — A股微观量价因子背景，FactorMiner 复杂度正则的因子工程地基
- [LLM金融多Agent交易系统评估可靠性](./2026-08-30-LLM金融多Agent交易系统评估可靠性.md) — 因子挖矿下游：评估体系可靠性决定进化方向是否可信
