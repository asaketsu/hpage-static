# SingGuard-Bench: 策略自适应多模态 LLM 护栏基准

> 来源: [arXiv 2606.22873](https://arxiv.org/abs/2606.22873) | [GitHub: inclusionAI/Sing-Guard](https://github.com/inclusionAI/Sing-Guard)
> 日期: 2026-07-09

## 摘要

SingGuard 是 inclusionAI 提出的**策略自适应多模态护栏模型族**，核心创新是：将安全策略作为**运行时输入**（而非训练时固化），支持自然语言规则在推理时动态注入。配套发布的 SingGuard-Bench 是一个 56,340 样本的多模态护栏基准，覆盖 80+ 细粒度风险类型，跨 6 大基准族 / 35 个数据集。

## 关键发现

1. **策略即输入（Policy-as-Input）**: 与 Llama Guard / WildGuard 等固定分类法护栏不同，SingGuard 接受自然语言安全规则，逐条匹配判断内容是否违规，无需重训即可适应新产品/地区/阶段的合规要求。

2. **三档推理谱（Fast-Hybrid-Slow）**:
   - Fast: 直接输出安全标签，低延迟
   - Hybrid: 先快速判断，再决定是否需策略推理
   - Slow: 逐条规则审议，适合审计敏感场景
   - 训练采用 **快慢解耦强化学习**：排除首个 fast token 的锚定效应

3. **跨模态联合风险**: Bench 包含"单模态无害但组合有害"的样本（如图片+文字各自正常，合在一起暗示不安全意图），这是传统单模态分类器难以捕获的。

4. **动态规则评估**: 运行时策略切换下，策略遵循准确率从 0.6465 提升到 0.7415（+9.5pp）。

5. **RI-Mask 加速**: 30 条规则并行推理时，2B 模型多模态推理加速 5×+，通过共享内容前缀编码避免重复计算。

6. **SOTA 表现**: 在全部 6 个基准族（35 数据集）中取得最优平均 F1。

## 对工作的价值

- **Agent 安全治理**: 我们的 Hermes Agent 部署涉及多模态输入（飞书图片/语音），SingGuard 的策略即输入范式可直接启发 agent-security-governance skill 的护栏设计——按场景动态切换安全规则而非硬编码。
- **快慢推理分层**: Fast/Hybrid/Slow 三档对应我们 agent 可靠性工程中的降级链思路——日常 fast，边界 case 升级 slow，可复用此模式。
- **跨模态攻击意识**: cross-modal joint-risk 攻击向量提示我们在多模态 agent 场景中，不能只看单模态安全性。

## 行动建议

- 低优先级监控：关注 inclusionAI/Sing-Guard 仓库后续发布（模型权重尚未完全放出）
- 概念吸收：将"策略即运行时输入"思路纳入 agent-security-redteam skill 的护栏章节
- 暂不部署：当前 Hermes 单模态文本场景为主，多模态护栏需求尚未触发

## 相关笔记

- [SingGuard-Bench: 策略自适应安全基准（7-11更新）](./2026-07-11-SingGuard-Bench-.md) — 同主题后续精读笔记
- [LLM Agent 失败模式综合分类法](./2026-07-09-LLM-Agent失败模式综合分类法.md) — Agent 安全与可靠性分类
