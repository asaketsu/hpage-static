# Reasoning Effort, Not Tool Access, Buys First-Try Reliability in Agentic Code Generation

> **一句话总结**：90 次独立 agent 编码实验证明——提高推理强度（reasoning effort）比增加工具能力（如浏览器测试）更能提升首次成功率，前者将完美运行率从 28% 提升到 89%，后者仅增加 42-68% 成本而无任何质量提升。

## 元数据

- **标题**：Reasoning effort, not tool access, buys first-try reliability in agentic code generation: an observational study
- **作者**：Achint Mehta (TrendAI)
- **日期**：2026-07-02
- **arXiv ID**：2607.02436
- **领域**：Software Engineering (cs.SE); Artificial Intelligence (cs.AI)
- **页数**：22 pages, 5 figures, 10 tables
- **数据集**：公开于 Zenodo (DOI: 10.5281/zenodo.21134406) + GitHub

## 核心问题与研究动机

### 被检验的假设

业界普遍认为：给 AI 编码助手增加更多能力（浏览器测试工具、设计导向的 prompt）就能产出更好的软件。**本研究直接检验这一假设**。

### 为什么这个问题重要

公开的编码 agent 评测通常使用单条简短指令 + 每个模型只跑一次，这种设计隐藏了两个实际中至关重要的因素：
1. **运行间方差**（run-to-run variation）——同一个配置跑多次结果可能差很多
2. **首次可靠性**（first-try reliability）——模型第一次就做对的能力，而非靠人工纠正后的"最终分数"

## 实验设计

### 任务

所有 agent 运行构建同一个应用：**实时回顾看板**（real-time retrospective board），基于一份详细的 OpenSpec 规格文档。

### 规模

- **90 次独立运行**，跨多种配置
- 每次运行独立生成、构建、测试完整应用

### 模型家族

- Claude Opus 4.7（48 次运行）
- Claude Opus 4.6（27 次运行）
- Claude Sonnet 4.6（10 次运行）
- Gemini 3.1（3 次运行）
- Qwen 3.6 Coder Next（2 次运行，本地模型）

### 变量

1. **推理强度**：High vs xHigh
2. **测试工具**：Playwright（浏览器自动化测试）有无
3. **设计 prompt**：无 / 完整版 / 一段话精简版
4. **Agent 框架**：Claude Code v2.1.132 vs Antigravity

### 评分体系

- **14 项功能标准**，每项 3 分（首次成功）/ 2 分（纠正后成功）/ 1 分（未解决），满分 42 分
- **视觉质量**：1-5 分（由 LLM 评分 + 人工验证）
- **修复负担**：每运行平均纠正次数（rated 2 的标准数量）

## 关键实验结果

### 1. 模型能力层级是最大变量（非工具/prompt/effort）

- 前沿模型家族均值接近天花板：Opus 4.7 ≈ 41.3/42，Opus 4.6 ≈ 40.7/42，Sonnet 4.6 ≈ 41.0/42
- 本地模型 Qwen 大幅落后：均值仅 30.5/42（24-37 分范围）
- Qwen 的 token 消耗是前沿模型中位数的 12-50 倍（大量低效迭代）
- **关键洞察**：在前沿模型内部，花费更多（$1-$8 范围）并不买到更高分

### 2. 总分掩盖了首次可靠性的巨大差异

这是本文最具方法论价值的发现：

- Opus 4.6 与 Opus 4.7 均值差不到 1 分（40.7 vs 41.3）
- 但 Docker 首次通过率：Opus 4.6 仅 19% → Opus 4.7 达 75%（Fisher p < 0.001）
- **结论**：后修复总分严重低估了模型间的真实差异，首次可靠性和修复负担才是更有信息量的指标

### 3. 失败模式集中分布

跨 90 次运行的 100 次首次失败中：
- Docker 部署失败：44%（40/90 次）——原生 SQLite 模块在容器中无法编译
- 本地开发环境失败：17%（15/90 次）——包安装、框架 breaking change
- **两项环境标准合计占所有首次失败的 55%**
- 界面侧最大贡献者：拖拽功能 19%（14/90 次）
- 其余 12 项标准各自失败率 ≤ 6%

### 4. 测试工具：花钱不办事（核心发现）

Playwright 工具的效果：
- 功能分数：**无变化**（与无工具完全一致）
- 成本：**增加 42-68%**
- 首次可靠性：**无改善**（即使对界面可见的缺陷）
- 成本溢价的去向：**不是更多工程代码，而是上下文重读**——cache read tokens 增加 2-3 倍

关键分析（Table 4 Token 分解）：
- 工具版 median output tokens 基本持平（42k vs 46k）
- 工具版 median cache read tokens 飙升（5.3M vs 2.3M at High）
- **工具溢价 = 反复重新读取被工具交互和截图膨胀的会话上下文**

为什么工具无效？因为主要失败发生在构建/环境层（55%），而界面测试工具根本无法触及这些故障。当 Docker 构建失败时，根本没有界面可以测试。

### 5. 推理强度：廉价且高效的可靠性提升（核心发现）

High → xHigh 的效果（Opus 4.7）：
- 首次完美运行率：28% → 89%（Fisher p < 0.001）
- 纠正次数：16 次 → 3 次（约 5 倍下降）
- 成本溢价：仅 9%（base 配置）
- xHigh base 配置：6/6 次全部首次完美（42 分）

对比工具 vs 推理强度：
- 工具：+42-68% 成本，0% 可靠性提升
- 推理强度：+9% 成本，+61 个百分点可靠性提升
- **同样的预算花在推理强度上远比花在工具上划算**

### 6. 设计 prompt 提升视觉但不提升功能

- 无 prompt：视觉评分恒定 3.0/5
- 有 prompt（完整或精简）：4.5-5.0/5
- 功能分数：基本不变，甚至微降
- **关键**：一段话精简版 prompt 效果与完整第三方 prompt 完全一致
- 功能代价：拖拽功能失败率上升（更复杂的交互动画更容易出错）
- xHigh 也无法消除设计 prompt 带来的功能代价

### 7. 同配置运行间方差真实且显著

Opus 4.6 High base 配置 7 次重复运行：
- 源文件数：10-17 个
- CSS 行数：41-626 行（约 15 倍差异！）
- 功能分数：38-42（窄带）
- 结构指标与分数无相关性

xHigh 大幅压缩方差：功能分数全部 = 42

行业趋势：前沿模型锁定 temperature=1，无法通过调参降低随机性，推理强度是唯一剩余的方差压缩杠杆。

## 创新点分析

1. **方法论创新——标准级分析**：不依赖聚合总分，拆解到每个评分标准的首次通过/修复/失败。暴露了总分掩盖的巨大差异。这对 Agent 基准测试有范式级影响。

2. **Token 经济学分解**：将工具/prompt 的成本溢价分解到 output tokens vs cache read tokens，精确定位成本去向。工具的成本不是"写了更多代码"而是"重新读了更多上下文"。

3. **设计 prompt 的消融实验**：一段话 vs 完整 prompt 的对比证明——模型的能力是内在的，prompt 只是"触发器"（invocation），不需要长篇大论。

4. **首次可靠性作为评估维度**：提出 first-try reliability 和 repair burden 应作为 Agent 基准的标准报告维度，而非仅报后修复总分。

## 局限性与未来方向

### 作者自述局限

- 单一任务（实时回顾看板）
- 单人评分 + LLM 视觉评分
- 前沿模型分数接近天花板，headroom 有限
- xHigh 仅在 Opus 4.7 上测试
- 观察性研究而非随机对照试验（Fisher p 值仅为描述性）
- abridged prompt 批次间隔数周（残余混杂）

### 额外评估

- **泛化性存疑**：单一任务 + 主要是 Claude 家族，结论是否适用于其他领域（如后端 API、数据分析、DevOps）未知
- **工具选择偏差**：只测了 Playwright（前端测试工具），如果换成构建/部署工具（如 Docker linter、CI 管道）可能结论不同。作者自己也承认"matched to the failure mode"才是关键
- **成本模型局限**：本地模型的 $41-$179 是按 hosted 定价估算的 token 量，非真实成本
- **缺少推理强度的边际递减分析**：xHigh 之后再加还有收益吗？

## 借鉴点（关联 Hermes Agent / Jetson Orin / 量化交易）

### P0：推理强度优先于工具堆叠（直接可执行）

**论文结论**：Reasoning effort > Tool access for first-try reliability。

**对 Hermes Agent 的直接启示**：
- 当前 Hermes 有大量 Skills（300+），但论文证明——工具多不等于结果好
- 核心策略应从"增加工具"转向"提升每次调用的推理深度"
- 具体可执行：对关键任务（代码生成、系统设计）使用更高 reasoning effort 的模型配置
- 验证方法：对比同一任务在 default vs high effort 下的首次成功率

**已有覆盖**：Hermes 有 `state-machine-loop` skill 提到"上下文压缩→token预算检查"，但未系统性地按"推理强度优先"原则配置模型路由。

### P0：首次成功率作为 Agent 质量指标（方法论移植）

**论文方法论**：first-try reliability + repair burden 替代后修复总分。

**对 Hermes 的直接应用**：
- cron job 评估应增加"首次执行成功率"维度，而非仅看"最终是否完成"
- 已有 `error-case-library` 和 `watchdog` 记录失败，但缺少"纠正次数"统计
- 可执行：在 cron job 报告中增加 `corrective_interventions` 计数

### P1：工具成本-收益审计（工具匹配原则）

**论文原则**："Match the fix to the failure mode"——工具必须匹配实际失败模式。

**对 Hermes 的应用**：
- 审计当前 Skills 中哪些是"界面测试工具"（看起来有用但实际无法触及核心失败）
- 量化交易领域：与其增加更多数据源工具，不如提升策略推理深度
- 可执行：对高频使用的 Skills 做 token 消耗审计（类似论文的 Table 4），识别"成本来自上下文重读"的低效工具

### P1：设计 prompt 的"触发器"模式

**论文发现**：模型能力是内在的，短 prompt 就能触发。

**对 Hermes 的应用**：
- 长 Skill 文档可能不是必须的——关键在于"明确说出要什么"
- `note-dual-format` 等 skill 中的"铁律"格式（短而明确的指令）恰好验证了这一点
- 可执行：评估现有 Skill 中哪些可以精简为"一段话触发器"

### P2：温度控制的行业趋势影响

**论文观察**：前沿模型锁定 temperature=1，无法降随机性。

**对 Hermes 的影响**：
- 意味着无法通过调参获得确定性输出
- 推理强度成为唯一可控的方差压缩手段
- 对量化交易 cron job（需要确定性）影响最大——需在 prompt 层面而非参数层面追求一致性

### P3：Agent 基准测试范式（长期）

论文提出的 first-try reliability 报告框架可指导 `skill-stress-test` 的评测维度升级。

## 关联论文

- **2603.01896 Agentic Code Reasoning**（Meta, 半形式化推理方法提升代码分析准确性）——互补方向：本文关注"投入什么资源"，该论文关注"如何结构化推理"
- **Kara (2607.01237)**（KV Cache 压缩，昨日精读）——关联点：推理强度提升需要更多 KV Cache，Kara 的滑动窗口压缩可以降低高推理强度的成本
- **LedgerAgent (2606.20529)**——关联点：工具调用账本可以记录"哪些工具调用在重读上下文"（本文发现的主要成本来源）

## 实践建议摘要

按优先级排序：

- P0：关键任务配置高 reasoning effort 模型，而非堆叠更多工具
- P0：引入"首次成功率 + 修复次数"作为 Agent 质量度量
- P1：对高频 Skills 做 token 消耗审计，识别"上下文重读税"
- P1：评估 Skill 文档精简为"触发器"模式的可行性
- P2：量化交易 cron job 用 prompt 层确定性替代 temperature 控制
- P3：升级 skill-stress-test 评测框架加入首次可靠性维度

## 相关笔记

- [推理优于工具(中文版)](./2026-07-06-推理优于工具-Agent代码生成实证研究.md) — 同一论文中文整理
- [Agent失败模式综合分类法](./2026-07-09-LLM-Agent失败模式综合分类法.md) — 六大失败模式分析
- [Agent组合一致性边界](../2026-05-29-LLM-Agent组合一致性边界研究.md) — 组合可靠性边界
- [Agent工程4月实践](../2026-05-14-Agent工程4月实践-不要一上来就做Agent.md) — 工程实践教训
