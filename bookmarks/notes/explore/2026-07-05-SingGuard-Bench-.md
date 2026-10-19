# SingGuard-Bench：策略自适应多模态护栏基准

> 来源：蚂蚁集团 inclusionAI（AI 安全实验室）| 论文 arXiv:2606.22873 | 代码 github.com/inclusionAI/Sing-Guard | Apache-2.0

## 摘要

SingGuard-Bench 是蚂蚁集团发布的多模态护栏（guardrail）评测基准，配套 SingGuard 模型族（2B/4B/8B，基于 Qwen3-VL）。其核心创新是：**把安全策略当作运行时输入**，而非训练时固定的标签集——部署团队可用自然语言规则动态切换审核策略，无需重训模型。

## 关键发现

- 规模：56,340 个样本，覆盖 80+ 细粒度风险类型，横跨 6 大基准族（35 个数据集）
- 评测维度：多模态 QA 安全、纯图像安全、文本 query 侧/ response 侧安全、多语言安全、动态规则评估
- **跨模态联合风险（cross-modal joint-risk）**：每个单模态（图/文）单独看无害，但组合起来暗示不安全意图——这是该基准的差异化亮点，直接针对"图文拼图式越狱"
- 推理模式：fast（紧凑二分类判断）→ hybrid → slow（策略逐条推理），用 fast-slow 解耦强化学习优化
- 性能：在所有 6 个基准族上达到 SOTA 平均 F1；动态策略遵循准确率从 0.6465 提升到 0.7415（+9.5 个百分点）
- 默认策略含 8 个顶级风险类别，可通过 `policy` 参数运行时注入自定义规则

## 对工作的价值

1. **跨模态联合风险检测思路**：可借鉴用于 Hermes 的内容安全层——当前多偏文本单模态审核，图文组合攻击是盲区
2. **运行时策略注入**：与 Agent 安全治理（agent-security-governance skill）理念一致，策略与模型解耦，便于不同场景定制
3. **基准复用**：若需评测自有护栏/红队效果，SingGuard-Bench 的 56K 样本可直接作为评测集
4. **模型即用**：2B 版本适合 Jetson 边缘部署，可作为本地内容审核层

## 行动建议

- 关注项：SingGuard-Bench 数据集标注 "Coming soon"，暂未完全释放，持续跟踪 HuggingFace collection
- 可落地：SingGuard-2B 模型已开源（Apache-2.0），可在 Jetson Orin 上试跑本地护栏，集成到 Hermes 输入/输出过滤层
- 深读点：fast-slow 解耦 RL 的训练细节（论文 v3），对自研轻量护栏有参考价值

## 相关笔记

- [[2026-07-06-SingGuard-Bench]] — 同主题后篇，SingGuard 模型系列学习笔记，含三档推理模式分析
- [[2026-07-02-SingGuard-Bench-]] — SingGuard 系列早期跟踪，护栏模型族初探
- [[2026-07-01-SingGuard-Bench-]] — SingGuard-Bench 首篇，基准结构梳理
- [[2026-06-30-SingGuard-Bench]] — SingGuard 最早跟踪笔记


## 相关笔记

- [SingGuard-Bench 策略自适应护栏(07-05)](./2026-07-05-SingGuard-Bench-.md) — 本文：56K样本/80+风险类型
- [SingGuard-Bench 学习笔记(07-06)](./2026-07-06-SingGuard-Bench.md) — 三档推理模式+6基准家族SOTA

## 相关笔记

- [SingGuard-Bench 学习笔记](./2026-07-06-SingGuard-Bench.md) — 护栏基准概览

## 相关笔记

- [SingGuard-Bench 学习笔记](./2026-07-06-SingGuard-Bench.md) — 同主题深度笔记

## 相关笔记

- [SingGuard-Bench](./2026-07-09-SingGuard-Bench.md) — 最新补充版
- [SingGuard-Bench 学习笔记](./2026-07-06-SingGuard-Bench.md) — 简要学习版
- [MCP协议安全攻防前沿](./../2026-06-29-MCP协议安全攻防前沿.md) — 安全协议视角
