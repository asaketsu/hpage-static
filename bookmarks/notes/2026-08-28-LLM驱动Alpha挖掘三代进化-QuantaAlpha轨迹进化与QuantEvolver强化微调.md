# LLM驱动Alpha挖掘三代进化-QuantaAlpha轨迹进化与QuantEvolver强化微调

> **来源**：QuantaAlpha（arXiv:2602.07085v2, AIFin Lab）+ QuantEvolver（arXiv:2605.15412v1, 北大+阿里）+ FactorMiner（清华+鹏城，Medium 解读）综合
> **原文链接**：https://arxiv.org/html/2602.07085v2 ；https://arxiv.org/html/2605.15412v1
> **记录日期**：2026-08-28
> **性质**：技术研究笔记（三篇论文精读 + 谱系对比）
> **本地关联**：用户已有 Hubble skill（LLM 因子挖掘，arXiv:2604.09601）、rd-agent-quant skill、量化铁律体系

**标签**：#量化交易 #Alpha挖掘 #LLM #智能体 #因子研究 #QuantaAlpha #QuantEvolver #强化微调

---

## 一句话总纲

> **LLM 驱动 Alpha 挖掘正经历三代范式跃迁：一代"提示词反馈循环"（RD-Agent/AlphaAgent）→ 二代"轨迹进化"（QuantaAlpha：把每次端到端挖掘当作轨迹做变异/交叉，CSI300 上 IC 0.1501、年化 27.75%、回撤 7.98%）→ 三代"强化微调"（QuantEvolver：把可执行回测转化为策略参数更新，≤30B 轻量模型内化优化经验，高频截面基准最强基线 +109.5% RankIC）。核心洞察：金融低信噪比环境下，"把经验写进参数"比"把经验堆进上下文"更稳。**

---

## 二、内容整理

### 2.1 问题定义：为什么 Alpha 挖掘是 LLM Agent 的硬骨头

Alpha 因子 = 把市场观测映射为预测信号的数学表达式 f(X)。形式化：

```
f* = argmax_{f∈F} L(f(X), y) − λ·R(f)
```

F 为因子表达式空间，L 衡量预测效力，R 正则化鼓励简洁与新颖。三重困难：

1. **组合爆炸**：变量 × 算子 × 时间窗 × 归一化方案的组合空间天文级
2. **低信噪比**：金融信号弱、带噪、依赖市场状态（regime-dependent）——回测反馈本身就是噪声
3. **冗余诅咒**（FactorMiner"相关红海"）：遗传规划跑一晚出 500 个候选，相关性过滤后活 3 个，其余全是已有因子库的换皮

### 2.2 第一代：提示词反馈循环及其天花板

代表：Alpha-GPT / FAMA（交互式）→ QuantAgent / AlphaBench / AlphaAgent（反馈驱动）→ R&D-Agent / QuantaAlpha 前身（搜索增强+多智能体）。

工作流模拟人类研究员：假设生成 → 因子构建 → 回测评估 → 反馈迭代。AlphaAgent 加正则抑制因子拥挤与 alpha 衰减；RD-Agent 做全栈自动化与因子-模型协同优化。

天花板（QuantEvolver 论文诊断）：

- **上下文爆炸与反馈漂移**：历史候选+评估结果+反馈反复追加进 prompt，循环越长推理成本越高、有用信息被稀释、优化目标逐渐漂移
- **大模型依赖与搜索停滞**：依赖超大 LLM，其稳定生成偏好导致结构相似表达式反复出现——探索多样性受限、候选冗余

### 2.3 第二代 QuantaAlpha：轨迹级进化（arXiv:2602.07085）

**核心抽象**：把每次端到端挖掘运行视为**挖掘轨迹** τ = (s₀,a₀,s₁,a₁,…,sₙ)——从假设生成到回测评估的完整决策序列，终局奖励 R(τ) = L(f_τ) − λR(f_τ)。优化目标是找轨迹生成机制 π 最大化期望终局奖励（本质是把 Alpha 挖掘变成轨迹空间的进化搜索）。

**挖掘工作流四智能体**：

| 智能体 | 职责 |
|--------|------|
| Idea Agent | 基于市场观察/前序轨迹/金融理论先验/参数规格生成可行动市场假设 |
| Factor Agent | 假设 → 算子库符号表达式 → AST 中间表示 → 可执行代码（编译失败触发 LLM 修复） |
| Verifier | LLM 一致性校验：假设↔语义描述↔符号式对齐 + 符号式↔代码忠实性 |
| Evaluation Agent | 标准化回测（预测力/收益/风控三组指标）+ 维护评估历史与成败模式总结 |

**AST 中间表示是关键工程创新**：直接生成代码脆弱（语法错误/依赖失配/语义漂移）；符号表达式+AST 让计算依赖与数据流完全透明，代码生成锚定在显式符号规范而非自由生成。

**三重生成约束**：

1. 语义一致性校验（见上）
2. 复杂度控制：C(f) = α₁·SL(f) + α₂·PC(f) + α₃·log(1+|F_f|)（符号长度+自由参数数+特征数）
3. 冗余控制：AST 最大公共同构子树度量 s(f_i,f_j)，对候选因子取其与已有 alpha zoo 的最大相似度 S(f)，超限拒绝重写

**进化算子**：

- **多样化规划初始化**：初始化智能体在语义与结构双层最大化假设互补性（信号源价格vs成交量、时间尺度短vs长、机制类型动量vs均值回归），并行探索多个假设区域，防早熟收敛
- **变异（Mutation）**：自我反思定位导致低终局奖励的最劣决策节点 k，冻结前缀到 s_k，只重写 a_k（可能是假设/符号式/代码），其余按固定前缀重新生成保持轨迹连贯
- **交叉（Crossover）**：按轨迹奖励选父代，识别持续贡献高累积奖励的片段（假设模板/构建模式/修复行为）合并为高连贯子代——继承的是"已验证的决策"而非表达式平均

**主实验（CSI 300，2022-01~2025-12 测试期四年）**：

| 方法（GPT-5.2） | IC | ICIR | RankIC | ARR% | MDD% |
|----------------|-----|------|--------|------|------|
| 最强 ML（LightGBM） | 0.0247 | 0.2055 | 0.0423 | 0.07 | 21.80 |
| 最强 DL（TRA） | 0.0421 | 0.3402 | 0.0511 | 6.81 | 8.51 |
| Alpha158 | 0.0131 | 0.0817 | 0.0334 | 2.66 | 10.15 |
| RD-Agent | 0.0531 | 0.4300 | 0.0633 | 9.91 | 14.82 |
| AlphaAgent | 0.0966 | 0.6344 | 0.0942 | 15.54 | 12.89 |
| **QuantaAlpha** | **0.1501** | **0.9110** | **0.1465** | **27.75** | **7.98** |

跨五模型（Qwen3-235B 到 GPT-5.2）一致增益，说明改进来自框架而非模型特异性。vs RD-Agent：IC +0.0970、ARR +17.84%、MDD −6.84%；vs AlphaAgent：IC +0.0535、ARR +12.21%。

**消融（关键数字）**：

- 去掉变异损失最大：IC −0.0292、ARR −9.81%——变异是有效探索与轨迹修复的主驱动
- 去掉规划初始化：IC 仅微降但 ARR −7.78%、MDD +2.73%——主要稳定策略层而非预测层
- 去掉交叉：IC −0.0070、ARR −2.82%——继承已验证模式的效率贡献
- 三约束（一致性/复杂度/冗余）各自非平凡；复杂度控制移除时策略层退化最重（ARR −8.44%、MDD +2.57%）

**零样本跨市场迁移**：CSI 300 挖的因子直接部署 CSI 500 / S&P 500，四年累计超额分别 ~160% / ~137%；2023-12 起竞争方法在市场微观结构 shift 下停滞，QuantaAlpha 持续上行——分布漂移下的鲁棒性证据。

回测协议：topk=50、n_drop=5、买费 0.05%、卖费 0.15%、次日开盘成交、涨跌停 9.5% 剔除。

### 2.4 第三代 QuantEvolver：强化微调范式（arXiv:2605.15412）

**范式宣言**：From Feedback Loops to Policy Updates——用参数学习内化历史优化经验，替代 prompt 级反馈堆积。每轮训练只用有界的生成-评估反馈，跨轮优化经验写进策略参数（隐式优化记忆替代显式长上下文历史）。

**五组件流水线**：

1. **种子构造**：场景精化 φ_refine(u) → oracle LLM 生成原始候选 → DSL 校验（语法/算子/类型约束）→ 经验评分 → 规范化去重 → 高质量种子池
2. **任务库构建**：种子 × 不同时间切分 = regime-aware 训练任务（每任务含种子表达式/时间分割/因子族/变异提示/场景元数据）
3. **Miner LLM（≤30B 轻量模型）**：迭代生成因子 DSL 表达式
4. **Regime Backtest 可执行评估**：编译后在历史数据上跑，奖励回传
5. **DiCo Reward（Diversity-Complementarity）**：用新颖性/冗余/行为多样性/互补性校准原始预测表现——鼓励生成"不仅预测强，且结构多样、行为 distinct、对现有池互补"的因子；训练全程高质量因子持续存入 Mined Factor Database 作为最终产出

**训练算法 GRPO（组相对策略优化）**：同 prompt 采样 K 个输出，组内归一化算相对优势 A_i = (R_i − mean)/std——提升组内优于同伴者概率、抑制较差者。适配结构化生成：多个候选语法均合法但任务级质量差异大，组间比较天然贴合。

**主实验（三基准）**：

- 单资产方向预测：方向准确率相对提升 **7.8%**
- 高频截面因子挖掘：最优样本外 RankIC 超最强基线 **109.5%**、top-10 样本外 RankIC 均值超 **186.9%**
- 日频股票 ETF：常规协议下强样本外 RankIC + 高质量可融合因子池
- 组合层：2025-11~2026-04 净值 1.00→2.26（累计 +125.6%），vs Alpha158 终值 1.85、Alpha101 1.37

### 2.5 FactorMiner：经验记忆路线补充（清华+鹏城）

自进化 Agent + **结构化经验记忆**：挖掘 110 个可解释 alpha 因子，记住什么有效/什么失败/为什么，用机构知识导航指数级收缩的搜索空间——针对"相关红海"：LLM 检索已有因子库做新颖性预判，而非生成后再过滤。定位介于二代（经验显式存储）与三代（经验入参数）之间的"经验入记忆库"变体。

### 2.6 三代谱系总表

| 维度 | 一代 反馈循环 | 二代 轨迹进化 | 三代 强化微调 |
|------|--------------|--------------|--------------|
| 代表 | RD-Agent / AlphaAgent | **QuantaAlpha** | **QuantEvolver** |
| 经验载体 | prompt 上下文 | 轨迹池+进化算子 | 策略参数（GRPO 更新） |
| 上下文压力 | 爆炸（漂移风险） | 中（轨迹选择性继承） | 有界（每轮固定） |
| 模型需求 | 超大 LLM | 大 LLM（五档均验） | **≤30B 轻量** |
| 核心机制 | 生成-评估-反馈 | 变异（定位修复）+交叉（复用） | DiCo 奖励 + 组相对优势 |
| 冗余对策 | 事后过滤 | AST 同构子树预拒绝 | DiCo 奖励内嵌 + DSL 去重 |
| 最强数字 | IC~0.097 (AlphaAgent) | IC 0.1501 / ARR 27.75% | RankIC +109.5% 相对提升 |

---

## 三、查询拓展

### 3.1 与经典遗传规划（GP）的对照

QuantaAlpha 的变异/交叉是**语义级**的（定位失败决策节点、继承已验证片段），经典 GP 的变异/交叉是**语法级**的（子树随机交换）——语义级算子继承经济机制而非表达式碎片，这是 LLM 进化超越 GP 的根本点。QuantaAlpha 论文自己点出：语法级操作产出"复杂、不可解释、易过拟合"的表达式。

### 3.2 RFT 用于金融的独特风险

GRPO 组内归一化假设组内奖励可比；但金融奖励本身是低信噪比样本——若回测窗口恰逢单边行情，组内相对优势可能学到的是 regime 偏好而非因子质量。QuantEvolver 用 regime-aware 任务库（种子×多时间切分）缓解，属于工程级补丁而非理论解决。这呼应铁律体系"回测可疑"触发条件：任何 RFT 挖出的因子仍需走 walk-forward 与样本外验证。

### 3.3 与本机 Hubble skill 的差距定位

Hubble（arXiv:2604.09601）核心主张：LLM 作为**受限搜索启发式**跑在确定性评估框架内（代码注入/死循环/语义无效的安全护栏）。对照三代谱系，Hubble 属于一代半（反馈循环+安全约束）。可吸收的增量：

- QuantaAlpha 的 **AST 中间表示 + 三重生成约束**（一致性/复杂度/冗余）——护栏从"执行安全"升级到"生成质量"
- QuantEvolver 的 **DiCo 奖励**——把多样性/互补性从后置过滤内嵌到优化目标
- QuantaAlpha 的**变异定位**（自我反思找最劣决策节点只改局部）——比整条重生成省 token 且保连贯

### 3.4 为什么金融是 Agent 自进化的试金石

低信噪比 + 非平稳 + 反馈延迟——任何自进化机制若能在金融数据上稳定收敛，其"经验复用不放大噪声"的设计就经过了最严苛检验。QuantaAlpha 的轨迹冻结前缀、QuantEvolver 的有界反馈窗，本质都是**防噪声放大器**。这与 MSCE（08-27 笔记）"证据接地的技能晋升"同构：晋升/进化必须有证据链，否则自进化变自我投毒（EVOMAL，08-27 笔记）。

---

## 四、归纳总结

### 4.1 三代演进主线一句话

**经验存放位置的迁移**：上下文（prompt）→ 轨迹库（选择继承）→ 模型参数（梯度内化）。每一代都在解决上一代"经验堆积导致的漂移与爆炸"。

### 4.2 五条工程要点

1. AST/DSL 中间表示是 LLM 因子工程的标配——代码直接生成不可控
2. 冗余控制必须前置（生成时 AST 同构检测/奖励内嵌），事后过滤浪费算力
3. 变异式局部修复 > 整体重生成（token 省 + 语义连贯）
4. 轻量模型 + RFT 可超越大模型 + prompt 循环（QuantEvolver ≤30B）
5. 跨市场零样本迁移是鲁棒性的金标准（QuantaAlpha CSI300→CSI500/S&P500）

### 4.3 局限与诚实披露

- 两篇论文回测期均含 2024-2025 A股/美股具体行情，IC 绝对值有市场依赖性
- QuantEvolver +125.6% 为论文报告组合层结果，未披露扣除冲击成本
- LLM 挖掘的因子可解释性仍依赖符号约束，放松约束立即退回黑箱
- 三代方法均未解决"因子容量"问题（topk=50 策略的资金上限）

---

## 五、趋势判断

### 趋势 1：Alpha 挖掘 Agent 从"提示工程"转向"训练工程"

依据：QuantEvolver 明确以 RFT 替代 prompt 循环为主线贡献；QuantaAlpha 引用 CSE（controllable self-evolution）作为从随机生成到反馈驱动进化的关键转变。因子工厂的竞争单位从"谁的 prompt 好"变成"谁的奖励设计+任务库好"。

### 趋势 2：轻量化是方向——≤30B 模型 + 参数内化

依据：QuantEvolver 用 ≤30B 模型实现最强结果；QuantaAlpha 在 Qwen3-235B 到 GPT-5.2 五档模型上一致有效但增益随模型增强而扩大（说明框架增益与模型能力正交叠加）。对本地部署（Jetson/单卡）友好。

### 趋势 3：多样性/互补性从评价指标升格为优化目标

依据：DiCo Reward 把 novelty/redundancy/behavioral diversity/complementarity 四信号直接编入奖励；QuantaAlpha 用 AST 同构预拒绝；FactorMiner 用因子库检索预判。三代共识：相关红海是第一敌人。

### 趋势 4：regime-aware 成为标配

依据：QuantEvolver 任务库按时间切分构造 regime-aware 任务；QuantaAlpha 零样本迁移实验专门考察 2023-12 分布 shift 后的表现。与用户周期模型（Wyckoff 吸筹→拉升→派发→回落）的 regime 思想一致——学术侧正在把 regime 从"事后解释"变成"训练时先验"。

---

## 六、关联分析

### 6.1 与本地量化体系

| 本地资产 | 关联点 |
|---------|--------|
| Hubble skill（llm-factor-mining） | 一代半定位；可吸收 AST 约束/DiCo 奖励/变异定位三个增量（P1） |
| rd-agent-quant skill | RD-Agent 是 QuantaAlpha 对照基线，其因子-模型协同思想被 QuantaAlpha 继承 |
| quant-evidence-governance skill | "回测可疑→当天回测+外源本地验证"铁律对 RFT 因子同样适用（3.2 节风险） |
| walk-forward-validation skill | RFT 因子上线前必须过 walk-forward（3.2 节结论） |
| stock-iron-rules 体系 | 铁律是规则系统（无学习），QuantaAlpha 轨迹进化提供了"给铁律加因子层"的学术参照——但半仓制/止损铁律不可被因子信号覆盖，分层：因子层只做候选筛选增强 |
| 周期模型 cycle-records.json | regime-aware 训练的本地对应物：因子评估按周期阶段分层统计 |

### 6.2 与 Agent 自进化系列（用户另一主线）

- QuantaAlpha 轨迹 = MSCE 技能晋升的"证据链"在金融域的形态：终局奖励+冻结前缀=可审计
- QuantEvolver 参数内化 vs Hermes Skill 体系（知识外挂）：前者适合高频重复任务，后者适合低频长尾任务——两路线按任务频率分治
- EVOMAL 自我投毒警告直接适用：RFT 奖励被噪声劫持 = 经验放大噪声的金融版

---

## 七、拓展应用推荐

1. **Hubble skill 增量评估（P1，建议下次会话执行）**：对照 3.3 节三个增量点（AST 约束/DiCo 奖励/变异定位），评估哪个可低成本移植到现有 Hubble 工作流——AST 中间表示优先（纯工程，无训练成本）
2. **铁律体系×因子层分层实验（P2）**：在 short_term_screener.py 候选池生成后加因子重排序层（先用 Alpha158/Alpha360 现成因子库，不上 LLM 挖掘），验证"因子增强筛选"对备选池质量的边际贡献——符合"分析完就停是技术债"原则的实验化落地
3. **regime 分层评估（P2）**：对现有监控列表的历史信号按周期阶段（吸筹/拉升/派发/回落）分层统计胜率——本地数据即可完成，无需新数据源
4. **跟踪清单**：QuantaAlpha GitHub（github.com/QuantaAlpha/QuantaAlpha）与 QuantEvolver（github.com/QuantLLM/QuantEvolver）均开源，可作 repo-absorption 候选

---

## 八、指南分析

**质量**：★★★★☆——两篇均为方法扎实的系统性工作：QuantaAlpha 的轨迹抽象+消融完整（每个组件贡献量化）；QuantEvolver 范式主张清晰（反馈循环→策略更新）且三基准验证。
**局限**：①两篇的回测窗口重叠且均含特殊行情期，绝对收益数字需谨慎外推；②QuantaAlpha 依赖 GPT-5.2 档模型才达最强数字（开源档 0.1252 IC 仍强但折扣明显）；③QuantEvolver 的 DiCo 奖励权重敏感性未充分披露；④FactorMiner 仅有 Medium 二手解读，原文未核（已在出处标注）。
**读法建议**：先读 QuantEvolver 引言的两挑战诊断（上下文爆炸/搜索停滞）建立问题框架，再读 QuantaAlpha 方法节学工程细节。

---

## 九、出处

1. QuantaAlpha: An Evolutionary Framework for LLM-Driven Alpha Mining — arXiv:2602.07085v2（AIFin Lab，开源 github.com/QuantaAlpha/QuantaAlpha）
2. From Feedback Loops to Policy Updates: Reinforcement Fine-Tuning for LLM-Based Alpha Factor Discovery (QuantEvolver) — arXiv:2605.15412v1（北大+阿里，开源 github.com/QuantLLM/QuantEvolver）
3. FactorMiner: LLM + Experience Memory — 清华+鹏城（2026-02，Medium JIN System Architect 解读，原文未直接核验）
4. Hubble: An LLM-Driven Agentic Framework for Safe and Automated Alpha Factor Discovery — arXiv:2604.09601（本地 skill 已收录）
5. RD-Agent / AlphaAgent / Alpha-GPT / QuantAgent 等一代方法谱系 — 见论文 1/2 Related Work 综述

## 相关笔记

- [2026-08-28-什么是Eval-为什么它决定了AI项目能不能真正落地](2026-08-28-什么是Eval-为什么它决定了AI项目能不能真正落地.md) — 因子挖掘策略上线前的Eval门禁
- [2026-08-28-WAM设计空间三轴分类-NVIDIA官方系统综述与VLA路线对决](2026-08-28-WAM设计空间三轴分类-NVIDIA官方系统综述与VLA路线对决.md) — 跨模态Agent谱系对照
- Hubble: An LLM-Driven Agentic Framework for Safe and Automated Alpha Factor Discovery（本地 skill，arXiv:2604.09601）— 一代方法谱系基线
- rd-agent-quant skill（微软 R&D-Agent-Quant 多智能体框架）— 上游 CoSTEER 代码生成
- a-stock-lianban-strategy / stock-iron-rules skill — 下游可落地策略实现

