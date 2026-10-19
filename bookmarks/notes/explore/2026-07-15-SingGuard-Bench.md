# SingGuard-Bench 学习笔记

> 来源: arxiv 2606.22873v3, Ant Group AI Security Lab, 2026
> 仓库: https://github.com/inclusionAI/Sing-Guard

## 摘要

SingGuard 是蚂蚁集团 AI Security Lab 发布的**策略自适应多模态 LLM 安全护栏模型族**，配套发布 SingGuard-Bench 基准（56,340 样本、80+ 细粒度风险类型）。核心突破：将"安全策略"作为运行时输入，而非训练时固定的分类标签集。

## 关键发现

1. **策略自适应设计** — 现有护栏（Llama Guard、WildGuard、Qwen3Guard 等）依赖固定分类法，部署后难改。SingGuard 把自然语言规则作为 runtime 输入，逐条匹配内容并预测标签+推理过程，实测动态策略下准确率从 0.6465 提升到 0.7415。

2. **快-慢推理双通道** — 大多数审核场景策略稳定、输入明确，直接判断已足够且更快；仅对策略变更/边界案例触发慢速推理（policy-grounded reasoning）。还设计了 fast-slow 解耦的强化学习目标，避免快速判断对推理产生锚定效应。

3. **SingGuard-Bench 覆盖全面** — 包含：多模态问答、对抗攻击（排版攻击、语义同构、叙事攻击、角色扮演）、跨模态联合风险（图文各自安全但组合后暗示不安全意图），以及动态规则配对（每个样本配匹配/不匹配的策略）。

4. **SOTA 性能** — 在六个基准族、35 个底层数据集上平均 F1 领先，2B/4B/8B 三个规模均超越 GPT-5.1、Gemini 3-Pro、Qwen3-VL-235B 等。

## 对工作的价值

- 我们的 Hermes 多模态对话场景（vision_analyze + 飞书/微信交互）同样需要内容安全护栏，SingGuard 的"策略即运行时输入"架构可直接借鉴：不同群聊/租户可配置不同安全规则，无需重新训练模型。
- 快-慢双通道推理设计对我们做 Agent 推理分层有启发：简单判断快通道、复杂/边界案例慢通道，兼顾吞吐和精度。

## 行动建议

- 跟踪仓库 https://github.com/inclusionAI/Sing-Guard，评估 2B 模型在本地 Jetson Orin 的可行性（边缘侧部署）。
- 研究 SingGuard-Bench 的动态规则构造方法，可迁移到我们的内容审核数据集构建。

## 相关笔记

- [SingGuard-Bench (07-13-a)](./2026-07-13-SingGuard-Bench-.md) — 策略自适应安全护栏深度
- [SingGuard-Bench (07-13-b)](./2026-07-13-SingGuard-Bench.md) — 多模态安全基准分析
- [SingGuard-Bench (07-09)](./2026-07-09-SingGuard-Bench-.md) — 首篇笔记/安全分类体系
