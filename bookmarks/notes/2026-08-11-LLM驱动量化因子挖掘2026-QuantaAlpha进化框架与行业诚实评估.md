# LLM 驱动的量化因子挖掘 2026：QuantaAlpha 进化框架与行业诚实评估

> 2026-08-11 夜间自学习 · AI+量化交叉方向
> 来源：QuantaAlpha (arXiv:2602.07085) + Zerve 行业报告 + Awesome-LLM-Quant-Trading 论文列表

---

## 一、核心矛盾：LLM 能挖 alpha 吗？

2026 年量化圈关于 LLM 的辩论已基本结束，但结论可能让很多人失望。

**行业诚实结论（来自 Zerve 2026 报告）**：

> "LLMs do not generate alpha. They do not propose novel research directions that produce genuine signal. The funds that treated LLMs as alpha-generation infrastructure have not benefited."

翻译：**把 LLM 当 alpha 生成引擎的基金都失败了。把 LLM 当研究生产力基础设施的基金受益了。**

| 工作流 | 真实加速 | 备注 |
|--------|----------|------|
| 代码生成和迭代 | 2-4x | 样板代码增益最高，新颖逻辑增益低 |
| 调试 | 2-3x | 类型错误/形状错误尤其强 |
| 文档 | 3-5x | 最大增益；以前不写文档的研究员现在写了 |
| 数据探索 | 2-3x | 有好的 schema 上下文时强，没有则弱 |
| 方法学验证 | 10-30% | 有限；严谨性靠人驱动 |
| **假设生成** | **几乎为零** | 建议很少能通过验证 |
| **策略设计** | **几乎为零** | LLM 实现，人设计 |

**LLM 的三个致命弱点**：
1. **不强制方法学严谨**：LLM 会愉快地写出有前视偏差/幸存者偏差/不当测试窗口的代码
2. **不确定下的多步推理有限**：能实现指定的策略，但无法设计需要同时平衡多个约束的策略
3. **市场预测不产生增量信号**：尽管 demo 好看，LLM 产生超越其他模型的市场方向信号证据很弱

**但这只是"当前 LLM 直接生成 alpha"的结论。QuantaAlpha 代表了一个新范式：不是让 LLM 直接生成 alpha，而是让 LLM 驱动一个结构化的进化搜索过程。**

---

## 内容整理：QuantaAlpha — 进化型 Alpha 挖掘框架

### 论文核心信息

- **论文**：QuantaAlpha: An Evolutionary Framework for LLM-Driven Alpha Mining
- **arXiv**：2602.07085v3（2026年2月发布）
- **团队**：上海财经大学(SUFE) + QuantaAlpha + 中山大学 + 北京大学
- **代码**：https://github.com/QuantaAlpha/QuantaAlpha
- **使用模型**：GPT-5.2（主实验），同时测试 Qwen3-235B、DeepSeek-V3.2、Gemini-3-pro、Claude-4.5-Sonnet

### 解决什么问题

现有 LLM Agent 因子挖掘系统存在**三大局限**：

| 局限 | 说明 | 后果 |
|------|------|------|
| **可控性脆弱** | 迭代改进由噪声回测反馈驱动，容易产生语义漂移 | 逐步偏离预期经济机制，滑向虚假相关 |
| **可信度有限** | 依赖基于瞬时上下文的随机重生成，不显式继承已验证的经验 | 缺乏可追溯谱系，产出因子难以审计和信任 |
| **探索受限** | 搜索过度利用初始种子附近的局部邻域 | 因子拥挤，假设空间覆盖不足 |

### 核心创新：轨迹级进化

QuantaAlpha 将每次端到端的因子挖掘运行视为一条**挖掘轨迹 (mining trajectory)**：

```
τ = (s₀, a₀, s₁, a₁, ..., sₙ)
```

其中 s₀ 是初始挖掘上下文（市场环境+用户种子），aᵢ 是多 Agent 系统在第 i 步采取的动作，sₙ 是包含评估结果的终态。

**关键区别**：不是简单地"生成因子→回测→再生成"，而是显式地**进化整条研究轨迹**。

#### 两个进化算子

**变异 (Mutation)**：
1. 对轨迹进行自反思，定位导致低终态奖励的次优决策节点 k
2. 只重写局部的动作 aₖ（或短局部段），保持其余步骤不变
3. 前缀冻结到 sₖ，后续步骤基于固定前缀重新生成

```
τ_child = (s₀, a₀, ..., sₖ, Refine(aₖ), s'ₖ₊₁, a'ₖ₊₁, ..., s'ₙ)
```

变异可更新：假设、符号表达式、编译代码；可引入机制级变更如改变时间尺度、添加制度条件。

**交叉 (Crossover)**：
1. 从高质量父代中选择互补的子轨迹
2. 识别持续贡献高累积奖励的轨迹段（假设模板、因子构造模式、修复行为）
3. 将这些段合并成高度连贯的新序列

交叉模拟了人类组合不同方案互补优势的实践。

### 四 Agent 协作架构

| Agent | 职责 | 关键设计 |
|-------|------|----------|
| **Idea Agent (𝒜ᵢ)** | 生成市场假设 | 结构化知识整合：市场观测 + 金融理论先验 + 参数规范 |
| **Factor Agent (𝒜բ)** | 因子构造 | 基于标准化算子库 𝒪 + AST 中间表示，不是直接生成代码 |
| **Evaluation Agent** | 因子评估 | 标准化回测：预测能力 + 收益表现 + 风险控制 |
| **Initialization Agent (𝒜₀)** | 多样化初始化 | 最大化假设间的语义和结构互补性 |

### 三重质量控制门

1. **语义一致性验证**：LLM 验证器检查假设 h ↔ 语义描述 d ↔ 符号表达式 f ↔ 代码 c 的对齐
2. **复杂度正则化**：𝒞(f) = α₁·SL(f) + α₂·PC(f) + α₃·log(1+|F_f|)（符号长度+自由参数+特征数）
3. **冗余过滤**：AST 最大公共子树匹配 → 结构去重 + 输出级相关性过滤 → 功能去重

### 实验结果：CSI 300 四年回测

| 方法 | IC | Rank IC | ARR(%) | MDD(%↓) |
|------|-----|---------|--------|---------|
| **传统ML最佳** Transformer | 0.0331 | 0.0451 | 5.21 | 13.81 |
| **传统ML最佳** TRA | 0.0421 | 0.0511 | 6.81 | 8.51 |
| Alpha158 因子库 | 0.0131 | 0.0334 | 2.66 | 10.15 |
| RD-Agent (GPT-5.2) | 0.0286 | 0.0250 | 3.58 | 16.76 |
| AlphaAgent (GPT-5.2) | 0.0347 | 0.0334 | 1.11 | 13.89 |
| **QuantaAlpha (GPT-5.2)** | **0.0472** | **0.0459** | **4.68** | **11.80** |
| QuantaAlpha (DeepSeek-V3.2) | 0.0461 | 0.0450 | 4.53 | 15.10 |
| QuantaAlpha (Qwen3-235B) | 0.0450 | 0.0444 | 2.06 | 16.36 |

**关键发现**：
- IC 0.0472 是所有方法中最高的（包括传统深度学习 TRA 的 0.0421）
- vs RD-Agent：IC +0.0186，ARR +1.10%，MDD -4.96%
- vs AlphaAgent：IC +0.0125，ARR +3.57%，MDD -2.09%
- **跨 LLM 一致**：不同骨干模型都有类似增益，说明改进来自框架而非单一 LLM

### 消融实验：什么组件最重要？

| 配置 | IC | Rank IC | ARR(%) | MDD(%) |
|------|-----|---------|--------|--------|
| QuantaAlpha 完整 | 0.0461 | 0.0450 | 4.53 | 15.1 |
| - 去掉 Planning | -0.0013 | -0.0013 | -0.72 | +1.62 |
| **- 去掉 Mutation** | **-0.0079** | **-0.0079** | **-1.26** | +0.48 |
| - 去掉 Crossover | -0.0060 | -0.0031 | -0.51 | +0.93 |

**变异是探索主驱动**，交叉主要支持已验证模式的复用。去掉复杂度控制导致 ARR -0.95%、MDD +2.31%。

### 跨市场零样本迁移

CSI 300 上挖掘的因子**直接部署**到 CSI 500 和 S&P 500：
- CSI 500：约 40.28% 累积超额收益（4年）
- S&P 500：约 19.1% 累积超额收益（4年）

零样本迁移可行因为因子使用标准 OHLCV 算子 + 日频截面归一化消除了跨市场尺度差异。

### Alpha 衰减分析

2023 年 A 股市场发生重大制度转换（大盘核心资产 → 小盘主题股），基线方法 IC 崩塌。QuantaAlpha 发现了**结构性因子**（如 Mean-Reverting Range Deviation、Overnight Gap Structure），这些因子反映持续的微观结构效应（波动率聚类、隔夜信息纳入），对市值风格不敏感。

### 最优迭代轮次

性能不随迭代线性增长。约第 11-12 轮（约 350 个因子）达到收益与风险控制的最优平衡点。超过后新引入的因子带来冗余信息，反而降低鲁棒性。

---

## 2026 LLM 量化论文全景（来自 Awesome-LLM-Quant-Trading）

### 因子挖掘方向最新论文

| 论文 | 团队 | 时间/会议 | 核心方法 |
|------|------|-----------|----------|
| **QuantaAlpha** | SUFE/PKU | 2026-02 | 轨迹级进化（变异+交叉） |
| **FactorMiner** | THU | 2026-02 | 技能+经验记忆的自进化 Agent |
| **CogAlpha** | HKU/GIM | ACL 2026 | LLM 驱动的代码级进化 |
| **AlphaAgentEvo** | SYSU/NTU | ICLR 2026 | 面向进化的 Agentic RL |
| **AlphaForge** | — | 2025 | 动态组合公式化因子 |
| **AlphaSAGE** | — | 2025 | GFlowNet 结构感知挖掘 |
| **Alpha Jungle (MCTS)** | — | AAAI 2026 | LLM+蒙特卡洛树搜索 |
| **Alpha-R1** | Finstep/SJTU | 2025-12 | RL 驱动的 alpha 筛选 |
| **FactorMAD** | THU | ICAIF 2025 | 多 Agent 辩论框架 |

### 交易 Agent 方向

| 论文 | 团队 | 时间/会议 | 核心方法 |
|------|------|-----------|----------|
| **AlphaCrafter** | NJU | 2026-05 | 全栈多 Agent 框架 |
| **Trade in Minutes** | TJU/MSRA | ICLR 2026 | 理性驱动的 Agentic 系统 |
| **TradeTrap** | Shanghai AI Lab | 2025-12 | LLM 交易 Agent 可靠性质疑 |
| **QuantAgent** | SBU | 2025-09 | 价格驱动高频交易多 Agent |

---

## 查询拓展

- **QuantaAlpha 的 AST 中间表示对 Hermes Skill 体系的启发**：将自然语言假设映射到标准化算子库+AST，而非直接生成代码——这与 Skill 的"声明式 vs 命令式"设计原则高度一致
- **变异+交叉进化是否可用于 Hermes Skill 自进化**：当前 evolver skill 偏重错误模式→规则沉淀，缺少结构化的变异/交叉机制。QuantaAlpha 的轨迹级进化提供了一个可迁移的框架
- **A 股市场制度转换的因子鲁棒性**：2023 年制度转换（大盘→小盘）导致经典因子失效。用户当前交易体系（五条铁律+十条操作）如何应对类似的制度转换？
- **TradeTrap 论文（2025-12）**：质疑 LLM 交易 Agent 是否真正可靠——这是一个重要的反方声音，值得单独精读

---

## 归纳总结

1. **LLM 不直接生成 alpha，但 LLM 驱动的结构化搜索过程可以**：QuantaAlpha 的 IC 0.0472 超越传统深度学习最佳（TRA 0.0421），证明关键不是让 LLM "想出"因子，而是让 LLM 驱动一个有变异、交叉、选择压力的进化搜索

2. **轨迹级进化 >> 随机重生成**：把每次因子挖掘视为完整轨迹并显式进化（而非在噪声反馈上随机重生成），是 QuantaAlpha 超越 RD-Agent/AlphaAgent 的核心原因。变异提供探索，交叉提供复用

3. **AST 中间表示是连接"语义"和"代码"的桥梁**：直接让 LLM 生成代码容易产生语法错误和语义漂移。标准化算子库+AST 中间表示使生成可控、可验证、可编译

4. **因子跨市场迁移是真实的**：CSI 300 上挖的因子直接用于 S&P 500 获得 19.1% 超额收益，说明好的因子反映的是市场微观结构（波动率聚类、隔夜信息），而非市场特定的历史规律

5. **行业对 LLM 的定位正在分化**：一方（Zerve 报告）坚持"LLM 是生产力基础设施，不是 alpha 引擎"；另一方（学术论文）在证明"结构化的 LLM Agent 系统确实能超越传统方法"。两者不矛盾——区别在于是否给 LLM 足够的结构约束

---

## 趋势判断

| 趋势 | 信号强度 | 判断依据 |
|------|----------|----------|
| LLM 因子挖掘从"直接生成"转向"结构化搜索" | ⭐⭐⭐⭐⭐ | QuantaAlpha/CogAlpha/FactorMiner 都采用 Agent+进化/RL 架构 |
| 轨迹级进化成为新范式 | ⭐⭐⭐⭐ | QuantaAlpha 超越 RD-Agent/AlphaAgent，变异+交叉明确有效 |
| AST/符号中间表示成为标配 | ⭐⭐⭐⭐ | 解决直接代码生成的语义漂移问题 |
| ICRL 2026/ACL 2026 大量收录 | ⭐⭐⭐⭐⭐ | FactorMiner(ICLR)/CogAlpha(ACL)/AlphaAgentEvo(ICLR)/Trade in Minutes(ICLR) |
| LLM 交易 Agent 可靠性质疑出现 | ⭐⭐⭐ | TradeTrap(2025-12) 是重要的反方声音 |
| 因子跨市场迁移成为标准评测 | ⭐⭐⭐ | QuantaAlpha 首次系统验证 CSI300→CSI500/S&P500 零样本迁移 |

---

## 关联分析

### 与用户量化交易体系的关联

用户有完整的 15 条铁律选股体系和实时盘中扫描系统。QuantaAlpha 的启示：

- **变异/交叉思路可迁移到选股策略迭代**：当前选股策略靠人工经验（五条铁律），是否可以用 LLM 驱动的进化搜索自动发现新的选股规则？关键是将铁律编码为可变异的"假设"
- **AST 中间表示可用于策略代码生成**：用户 short_term_screener.py 的选股逻辑可以用标准化算子表示，让 LLM 在此基础上探索变体
- **2023 制度转换的教训**：用户当前持仓分析中，000790 华神科技违反铁律❶（低价股），这本身就是"经典规则在新制度下可能失效"的体现

### 与 Hermes Agent 体系的交叉

- **轨迹级进化 ≈ evolver skill 的增强方向**：当前 evolver 是"错误→规则"的单次映射，缺少多轮变异+交叉的结构化进化。QuantaAlpha 的轨迹表示（τ=(s₀,a₀,...,sₙ)）可直接应用于 Skill 进化
- **三重质量控制门 ≈ Harness 质量门禁**：语义一致性验证/复杂度正则化/冗余过滤，与 Hermes 的"质量门禁机械化"原则完全一致
- **多 Agent 协作（Idea/Factor/Eval/Init）≈ 猫仔团队**：QuantaAlpha 的四 Agent 分工与 Hermes 的 Dev/OPM/Content/Data 四猫分工在结构上高度相似

### 与 VLA 笔记的交叉（同日学习）

- **进化搜索**：QuantaAlpha 的变异+交叉是"在解空间中结构化搜索"，VLA 的异构数据协同训练是"在数据空间中结构化混合"——两者都是用结构化方法扩展搜索/泛化边界
- **中间表示**：QuantaAlpha 用 AST 连接假设和代码，VLA 用 action chunk 连接语义和关节控制——都是"用中间表示桥接抽象和具体"

---

## 出处

- QuantaAlpha 论文 — https://arxiv.org/html/2602.07085v3
- QuantaAlpha 代码 — https://github.com/QuantaAlpha/QuantaAlpha
- LLMs in Quant Research: What Actually Works in 2026 (Zerve) — https://www.zerve.ai/blog/llms-in-quantitative-research
- Awesome-LLM-Quantitative-Trading-Papers — https://github.com/Tom-roujiang/Awesome-LLM-Quantitative-Trading-Papers
- CogAlpha (ACL 2026) — https://aclanthology.org/2026.acl-long.538
- Alpha Jungle MCTS (AAAI 2026) — https://ojs.aaai.org/index.php/AAAI/article/view/37069
- BigAlpha 2026 竞赛 — https://bigquant.com/square/competition/76ad3f56-ec2b-431a-890e-139a7f4bbcba
- FAME AI & Finance Paper Hub — https://fame-ai.org/hub

---

*笔记生成于夜间自学习 cron（2026-08-11）。核心素材为 QuantaAlpha 论文全文 + Zerve 行业报告 + Awesome 论文列表交叉验证。*


## 相关笔记

- [LLM 量化多智能体 AlphaCracker 与可持续 Alpha 挖掘](2026-07-04-LLM量化多智能体2026-AlphaCrafter与可持续Alpha挖掘.md) — 多智能体协同挖因子，QuantaAlpha 的进化路径前身
- [QuantaAlpha LLM Evolutionary Alpha Mining](../explore/2026-07-10-quantaalpha-llm-evolutionary-alpha-mining.md) — 同框架早期版本分析（explore 目录）
- [LLM 推理加速 MTP 与推测解码全景](2026-07-02-LLM推理加速2026-MTP与推测解码实战全景.md) — 量化推理部署的底层加速技术
