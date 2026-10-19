# 6条多Agent设计原则共识：五维设计空间 × 生产工程六原则

> 探索日期：2026-08-30 | 兴趣等级：L3 | 来源数量：4 篇 | 前序：[2026-08-28 CIV模式与living spec](2026-08-28-AI-Agent-IDE-Intent-spec-driven多Agent协调.md) / [2026-08-25 Intent SpecDriven](2026-08-25-AI-Agent-IDE-Intent-SpecDriven多Agent协调.md)

## 摘要

多 Agent 设计知识正在收敛为两条互补主线：**架构维度学派**（arXiv 实证研究提炼的"五维设计空间"，任何 MAS 都可分解为五个正交维度的配置组合）与**工程原则学派**（app.build 生产经验总结的六条工程原则，回答"怎么把架构跑稳"）。本笔记为同主题第三篇，聚焦增量：五维分类法 + 六原则与前序 CIV 笔记的交叉映射。

## 关键发现

### 1. 五维设计空间（arXiv 实证研究 → Cobus Greyling 提炼）

每维度 2-4 个选项，正交组合而非单选架构：

```
Flow Control      ── Explicit (预定义图/agentic workflow) vs Dynamic (LLM 运行时决策)
Interaction       ── Handoff (prompt 传递) vs Tool Flow (叶节点执行工具, 中间节点协调)
History Sharing   ── Full reasoning trace vs Final results only
Network Config    ── Supervisor / Swarm / Hierarchical / Single Info Environment
Human Interaction ── Human-in-the-loop (审批+中断) vs Human-on-the-loop (仅监督)
```

实证背景：三个真实试点（安全/财务管理/客服）一个月内交付可用方案，但随机 LLM 行为带来对齐、错误传播和扩展性难题。

### 2. 生产工程六原则（app.build / Arseni Kravchenko）

1. **投资系统提示**——当 API 文档写：直接、详细、清晰、无矛盾，不搞情感操控
2. **拆分上下文**——默认最少必要知识 + 工具按需拉取；巨大单一上下文导致"注意力衰减"
3. **精心设计工具**——把 Agent 当"聪明但容易分心的初级开发者"设计 API
4. **设计反馈循环**——Actor-Critic：LLM 自由创造 + 确定性 Critic 程序验证
5. **用 LLM 驱动错误分析**——构建 meta-Agent 分析失败日志，找系统性根因
6. **令人沮丧的行为是系统问题的信号**——先调试自己的系统再怪模型（真实案例：Agent 固执用假数据，根因是开发者忘了配 API key，Agent 连续调用失败后自己找了一条错路）

### 3. Single vs Multi 实证（Tau-bench +6 干扰任务）

- 单一任务 + 工具少 → **Single Agent 最佳**（路径简单，无协调开销）
- 任务多元 + 工具繁杂 → **Multi-Agent (Handoff) 略胜**，Supervisor 模式次之（多一层 Lead 转述）
- 结论：默认 Single + context compression，可拆分并行的场景才上 Multi

### 4. 跨笔记交叉洞察（本篇核心增量）

- **原则六与龙虾法则同构**："令人沮丧的行为是系统信号" ↔ AGENTS.md 龙虾法则 3"用户第二次问同一件事 = 系统失败"。两套体系独立收敛到同一元原则：**挫败感是缺陷检测器**
- **六原则是 CIV 的工程前提**：原则二（拆分上下文）= CIV 输入隔离；原则四（反馈循环）= Verifier 独立角色。六原则答"为什么"，CIV 答"怎么组"
- **History Sharing 是 CIV 未覆盖的独立轴**：Full trace（审计友好、token 昂贵）vs Final only（经济、丢失推理链）——这是五维分类法对 CIV 模型的真正补充

## 对工作的价值

- **P0**：Hermes kanban/subagent 多 Agent 设计可用五维做配置自检清单（当前缺 History Sharing 显式决策）
- **P1**：六原则可固化为 agent-orchestration-pattern 的 pre-flight checklist
- **P1**：三层方法论闭环——CIV（角色层）+ 五维（结构层）+ 六原则（工程层）

## 行动建议

- 给 agent-orchestration-pattern skill 补"五维设计空间选型表"（P1，半天）
- 六原则 checklist 引入 harness-checkpoint / subtask-lifecycle 的任务启动检查（P2）

## 关键风险与盲点

- 五维来自单一 arXiv 论文的三试点，样本小，社区复现级（非官方验证）
- 六原则为厂商博客经验，无对照实验支撑
- Medium 原文配图全部为空占位符，图表细节不可考

## 一页速查

> **五维选型**：Flow(显式图/动态) × Interaction(Handoff/ToolCall) × History(全trace/仅结果) × Network(Supervisor/Swarm/分层/SIE) × Human(in/on-the-loop)
> **六原则速记**：提示=API文档 → 上下文最小 → 工具防滥用 → Actor-Critic 反馈 → meta-Agent 查错 → 怪系统别怪模型
> **决策默认**：Single + context compression 优先；可并行拆分才 Multi；Handoff > Supervisor（少一层转述）
> **元原则**：挫败感 = 系统缺陷信号（六原则⑥ ≡ 龙虾法则③）

## 待深入

- arXiv 原论文 "LLM-Enabled Multi-Agent Systems: Empirical Evaluation and Insights"（三试点完整数据）
- SIE（Single Information Environment）架构细节——数据密集场景的动态路由

## 来源列表

1. Cobus Greyling (Medium/Kore.ai) — Six Core Design Principles for Multi-AI Agent Systems（2026，精读）
2. Tony Bai — 构建生产级 Agent 所需的 6 大工程原则（app.build Kravchenko 六原则中文详解，精读）
3. ihower — Multi-Agent 或 Single Agent（Tau-bench 扩展实验 + OpenAI Agents SDK PoC）
4. Google ADK Codelabs — 构建多智能体系统（LoopAgent/SequentialAgent 编排参照）

## 相关笔记

- [2026-08-28 CIV模式与living spec](2026-08-28-AI-Agent-IDE-Intent-spec-driven多Agent协调.md) — 前序，意图驱动编排
- [2026-08-25 Intent SpecDriven](2026-08-25-AI-Agent-IDE-Intent-SpecDriven多Agent协调.md) — 系列首篇
- [2026-08-29 SDD三层谱系与ACP标准化](2026-08-29-AI-Agent-IDE-SDD三层谱系与ACP标准化-增量.md) — 规格驱动谱系
- 跨目录参考：multi-agent-orchestration-governance-2026（~/explore）— 治理维度互补
