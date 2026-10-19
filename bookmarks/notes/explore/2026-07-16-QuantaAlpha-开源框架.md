# QuantaAlpha：LLM 驱动的进化式 Alpha 挖掘框架

来源：arXiv 2602.07085 (QuantaAlpha: An Evolutionary Framework for LLM-Driven Alpha Mining, 2026-02)
代码仓库：https://github.com/QuantaAlpha/QuantaAlpha

## 摘要

QuantaAlpha 将量化 Alpha 挖掘的端到端研究流程建模为"轨迹（trajectory）"，在轨迹层面执行变异（mutation）和交叉（crossover）操作。通过定位子步骤并定向修订、重组高收益片段，实现结构化探索与精炼。因子生成时强制假设、因子表达式与可执行代码之间的语义一致性，并约束复杂度与冗余以缓解因子拥挤。

## 关键发现

- 核心指标（GPT-5.2）：IC = 0.1501，年化回报率 ARR = 27.75%，最大回撤 MDD = 7.98%
- 方法创新：轨迹级进化（非逐因子进化），将完整研究流程作为进化单元
- 语义一致性约束：假设→因子表达式→可执行代码的三层语义对齐，防止语义漂移
- 拥挤控制：约束因子复杂度与冗余度，避免过拟合与拥挤效应
- 跨市场验证：在多个市场/ regime 下展示稳健性与分布转移韧性
- 多 Agent 系统：负责假设生成、因子构建、回测评估的协作 Agent

## 对工作的价值

- 与本项目量化交易 Agent 架构高度相关：可直接借鉴轨迹级进化方法优化 alpha 因子发现流程
- 语义一致性约束可作为当前 LLM 因子生成 pipeline 的质量门禁
- 进化式因子挖掘（变异+交叉）为 Agent 自主迭代提供可复用范式
- 交叉验证与 regime 韧性设计对量化 Agent 的系统评估有参考价值

## 行动建议

- 研究 https://github.com/QuantaAlpha/QuantaAlpha 仓库代码结构
- 评估将轨迹级进化方法集成到现有 A 股量化 Agent 中的可行性
- 重点关注语义一致性约束的实现细节，用于改进因子生成质量门禁

## 相关笔记

- [LLM量化因子挖掘-进化搜索与认知Agent](./2026-06-16-LLM量化因子挖掘2026-进化搜索与认知Agent.md) — LLM驱动因子挖掘
- [LLM量化因子挖掘-RFT-DAG自进化三范式](./2026-06-28-LLM量化因子挖掘2026-RFT-DAG-自进化三范式.md) — 自进化范式对比
