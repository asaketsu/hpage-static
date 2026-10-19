# LLM 驱动量化因子挖掘 2026：QuantaAlpha 进化框架与反方观点

> 2026-07-07 夜间自学习 | 主题：LLM for Alpha Discovery
> 来源：arXiv 2602.07085 (QuantaAlpha) + Emergent Mind 五阶段分类 + Zerve 实践报告 + FactorMiner (Tsinghua)

## 🎯 核心结论

**2026 年 LLM 量化因子挖掘出现两条分裂路径：** 学术界用进化框架（QuantaAlpha）在 CSI 300 拿到 IC=0.1501、ARR 27.75%、MDD 7.98%；而一线对冲基金实践（Zerve）却直言"LLM 不产生 alpha，只是生产力基础设施"。**真相在两者之间——LLM 是优秀的因子工程师，但不是因子来源；进化框架的核心价值在于把人类研究员的轨迹作为变异/交叉的种子。**

## 🏆 QuantaAlpha：轨迹级进化框架（arXiv 2602.07085）

### 设计思想

把每次端到端因子挖掘流程视为一条**轨迹（trajectory）**，在轨迹层面做变异和交叉，而非在因子表达式层面随机重生成。

### 三大创新

**1. 可控因子构造（Controllable Factor Construction）**
- 用算子库 𝒪 + AST 作为中间符号表示，桥接市场假设与可执行代码
- **语义一致性强制**：假设 h → 语义描述 d → 因子表达式 f → 可执行代码 c，三层必须自洽，失败则局部重写
- 复杂度约束：𝒞(f) = α₁·SL + α₂·PC + α₃·log(1+|Ff|)，控制符号长度/参数/特征数
- 冗余控制：通过 AST 匹配量化与已有因子的相似度

**2. 变异（Mutation）—— 精准定位失败步骤**
- 自反思诊断轨迹中"贡献最低终端奖励的决策节点" k
- 仅重写第 k 步动作，保留其余步骤：`τ_child = (s₀,a₀,…,sₖ,Refine(aₖ),s'ₖ₊₁,a'ₖ₊₁,…,s'ₙ)`
- 消融实验：移除变异导致 **IC -0.0292、ARR -9.81%**（最大跌幅），证明变异是核心

**3. 交叉（Crossover）—— 复用高奖励片段**
- 从不同父代轨迹中识别"持续贡献高累积奖励"的片段（假设模板、因子构造模式、修复策略）
- 合并为单一连贯序列

### 实验结果

| 市场 | 指标 | 结果 |
|------|------|------|
| CSI 300（GPT-5.2） | IC | 0.1501 |
| CSI 300 | ARR | 27.75% |
| CSI 300 | MDD | 7.98% |
| CSI 500 | 4年累计超额 | 160% |
| S&P 500 | 4年累计超额 | 137% |

**关键发现**：2023 年 12 月市场微观结构切换时，基线方法开始停滞，QuantaAlpha 仍维持稳定上升——证明进化框架对分布漂移的鲁棒性。最优性能在约 11-12 轮迭代（350 个因子）后达到。

## 📈 五阶段分类法（Emergent Mind）

系统性金融从人工到 LLM Agent 的演化路径：

1. **人工与基本面启发式** — 专家选股，不可扩展
2. **统计因子模型** — CAPM、Fama-French，线性刚性
3. **经典机器学习** — 非参数，无结构化数据能力
4. **深度学习与多模态** — 神经架构，易过拟合
5. **Agentic LLM Alpha Miner** — 感知→推理→工具调用→持续学习的完整闭环

第 5 阶段的架构组件：
- **表征学习**：文本 Transformer、时序 TCN/LSTM、表格自编码器
- **多模态融合**：注意力/门控融合层 + 机制感知加权
- **工具增强**：回测、订单管理、风险分析（VaR/场景分析）、持久记忆
- **三种推理模式**：Free（全自主，牛市最佳但易过度交易）/ Guided（参考专家策略）/ Strict（严格遵守，最小回撤）
- **关键经验**：~35B 参数模型在 Strict 模式合规性最佳，100B+ 模型在 Guided/Free 模式更强

## ⚖️ 反方观点：LLM 不产生 Alpha（Zerve 2026 实践报告）

一线对冲基金的真实数据，提供了必要的冷静视角：

| 工作流 | 实际加速 | 备注 |
|--------|---------|------|
| 代码生成与迭代 | 2-4x | 样板代码收益最大，新颖逻辑收益低 |
| 调试 | 2-3x | 类型错误、shape 错误尤其强 |
| 文档 | 3-5x | **最大收益**——研究员现在真的写文档了 |
| 数据探索 | 2-3x | 有 schema 上下文时强，无则弱 |
| 方法学验证 | 10-30% | 有限，严谨性靠人类 |
| **假设生成** | **几乎为零** | **建议极少通过验证** |
| **策略设计** | **几乎为零** | **LLM 实现，人类设计** |

三个关键清醒判断：
1. **"LLMs do not generate alpha"** — 假设生成的建议连贯、有趣，但极少产生通过验证的信号
2. **方法论严谨性不强制** — LLM 会乐意生成有 lookahead bias、幸存者偏差的代码，训练数据不推动方法学谨慎
3. **生产力增益来自 grounding，而非前沿模型** — "把模型锚定在实际环境中，而非用最新模型，带来绝大部分收益"

**安全模式**：Bring-Your-Own-LLM + Bring-Your-Own-Key，基金持有自己的 LLM 合同和密钥，模型调用从基金环境直连供应商。

## 🔬 FactorMiner（清华 + 鹏城实验室，2026-02-16）

解决"相关性红海"（Correlation Red Sea）——因子库充斥冗余信号：
- **自进化 Agent + 经验记忆**：LLM 因子生成 + 结构化经验记忆
- 挖掘出 **110 个可解释 alpha 因子**，每次迭代持续变聪明
- 与 QuantaAlpha 互补：QuantaAlpha 走轨迹进化，FactorMiner 走经验记忆积累

## 💡 对 Hermes 量化系统的启示

1. **进化框架可移植**：QuantaAlpha 的变异/交叉机制可直接增强 `llm-factor-mining` Skill——当前版本若只做单轮生成，应引入轨迹级记忆和变异
2. **语义一致性三层校验**：假设→表达式→代码的自洽检查是防止语义漂移的关键，应纳入 `quant-ic-validation` Skill 的因子构造流程
3. **清醒定位**：遵循 Zerve 实践——Hermes 量化系统应把 LLM 定位为"因子工程师/代码生成器/文档撰写者"，而非"alpha 来源"。`a-stock-quant-system` 的盯盘神探用 LLM 做收盘分析是正确姿势（生产力增强），不应幻想 LLM 直接预测涨跌
4. **经验记忆方向验证**：FactorMiner 的经验记忆与 Hermes `experience-bank` + `evolver` 架构高度吻合，证实了"经验卡片化 + 迭代复用"路线在量化领域的有效性
5. **GPT-5.2 性能参考**：QuantaAlpha 用 GPT-5.2 达 IC=0.15，说明前沿模型在结构化框架约束下确有价值，但需配合严格的语义一致性校验和复杂度控制

## 📚 关键引用

- arXiv 2602.07085 — *QuantaAlpha: An Evolutionary Framework for LLM-Driven Alpha Mining*
- Zerve — *LLMs in Quant Research: What Actually Works in 2026*
- Emergent Mind — *LLM as Alpha Miner in Quant Finance*（五阶段分类）
- FactorMiner — Tsinghua University & Peng Cheng Laboratory（2026-02-16）
- GitHub: Tom-roujiang/Awesome-LLM-Quantitative-Trading-Papers（论文集）

## 相关笔记

- `topics/` 下量化相关笔记
- `达尔文Skill2.0深度分析-Evolver对比吸收.md` — 自进化机制与因子挖掘的共性
- `竞品吸收笔记_GenericAgent.md` — Agent 框架在量化的应用
