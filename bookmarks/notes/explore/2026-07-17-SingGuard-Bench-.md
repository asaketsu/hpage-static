# SingGuard-Bench: 策略自适应多模态安全护栏基准

> 来源: arxiv 2606.22873 | inclusionAI | 2026-06
> 标签: #guardrail #multimodal #safety #benchmark #runtime-policy

## 摘要

SingGuard 是 inclusionAI（蚂蚁系）发布的策略自适应多模态护栏模型家族。核心突破：**把安全策略当作运行时输入而非训练时固定的标签集**——部署时传入自然语言规则，模型逐条比对判定，输出 safe/unsafe 标签及触发的规则类别。配套的 SingGuard-Bench 包含 56,340 个样本、覆盖 80+ 细粒度风险类型和 35 个数据集。

## 关键发现

**架构创新**
- 基于 Qwen3-VL 构建，提供 2b/4b/8b 三个规格
- Fast-to-slow 动态推理：低延迟场景用 fast 模式（仅输出二分类），高风险/策略变更场景用 slow 模式（逐条规则推理）
- 输出格式：第一行 `safe`/`unsafe` 二分类 + `<category>...</category>` 触发规则

**基准覆盖范围**
- 纯文本查询安全 / 纯文本响应安全
- 图像安全 / 多模态QA安全
- 跨模态隐藏意图攻击（cross-modal joint-risk：单独模态无害但组合有害）
- 多语言审核（query-side + response-side）
- 动态规则评估（运行时切换策略）

**核心指标**
- 动态规则策略遵循准确率：0.6465 → 0.7415（静态→动态策略）
- 六大基准家族均达到 SOTA 平均 F1
- 默认 8 个风险类别（A 性内容 / B 现实犯罪 / C 不道德行为 / D 网络安全 / E Agent安全 / F 政治敏感 / G 动物虐待 / Safe）

**工程可用性**
- Apache-2.0 开源，GitHub 79 stars
- 支持 Transformers 原生推理和 vLLM 部署
- `policy` 参数直接传入自然语言规则，零训练切换策略

## 对工作的价值

1. **飞书图文消息审核**：cross-modal joint-risk 检测正好覆盖"文字无害+图片无害但组合有害"的灰色场景，当前系统缺失这层
2. **多场景策略切换**：runtime policy 机制允许同一模型服务不同群组（内部群宽松/对外群严格），无需多模型
3. **Agent 安全层**：E 类（Agent Safety）专门检测 system prompt 泄露、内部策略探测——直接对应 Hermes 的安全需求
4. **延迟可控**：Fast 模式适合实时消息流，Slow 模式适合批量复审

## 行动建议

- 低优先级跟踪：SingGuard-Bench 数据集尚未完全公开（GitHub 标注 Coming soon），等发布后评估是否可用于内部审核质量基线
- 可选实验：Sing-Guard-2b 规格适合 Jetson 边缘部署，若飞书消息量增长需实时审核可评估本地化
- 不急于接入：当前消息量级下人工+规则过滤已够用，待 cross-modal 场景成为瓶颈再引入

## 相关笔记

- [2026-07-16-SingGuard-Bench-.md](./2026-07-16-SingGuard-Bench-.md) — 前一篇 SingGuard 同系列追踪
- [2026-07-15-SingGuard-Bench.md](./2026-07-15-SingGuard-Bench.md) — 早期版本对比
- [2026-07-05-SingGuard-Bench-.md](./2026-07-05-SingGuard-Bench-.md) — 首篇 SingGuard 基准分析
- [2026-06-30-GILP.md](./2026-06-30-GILP.md) — Guardrails-in-the-Loop 关联方法
- [2026-06-30-AI-Agent工具链安全新攻击面-MCP协议脆弱性.md](./2026-06-30-AI-Agent工具链安全新攻击面-MCP协议脆弱性.md) — Agent 安全护栏背景
