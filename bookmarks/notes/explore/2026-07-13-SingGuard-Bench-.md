# SingGuard-Bench：策略自适应多模态 LLM 护栏基准

> 来源：arxiv 2606.22873 | 团队：Ant Group AI Security Lab | 代码：https://github.com/inclusionAI/Sing-Guard

## 摘要

SingGuard-Bench 是一个多模态护栏（guardrail）评测基准，包含 56,340 个样本，覆盖 80+ 细粒度风险类型，横跨 35 个数据集、6 个基准族。配套模型 SingGuard 的核心创新：**将安全策略视为运行时输入（runtime input），而非训练时固化（training-time artifact）**——部署时传入自然语言规则，模型逐条匹配判定，无需重训即可适配不同产品/地区/法规的策略变更。

## 关键发现

1. **策略自适应架构**
   - 传统护栏（Llama Guard / WildGuard / Qwen3Guard）依赖固定标签集，策略变更需重训
   - SingGuard 接收自然语言策略作为推理输入，逐条规则匹配，输出安全标签 + 触发的具体规则
   - 统一三级安全分类法作为默认规则空间，支持推理时扩展

2. **快-慢推理光谱（Fast-to-Slow Reasoning Spectrum）**
   - Fast 模式：直接输出标签，低延迟，适用高吞吐常规审核
   - Hybrid 模式：先做快速判断，不确定时路由到策略推理
   - Slow 模式：逐条规则审议，产出可审计推理链，适用复杂/边界/监管敏感场景
   - 训练方法：快慢解耦强化学习（fast-slow decoupled RL），排除首个快速 token 对后续推理的锚定效应

3. **跨模态联合风险（Cross-Modal Joint-Risk）**
   - 单独看图片无害、单独看文本无害，但组合后暗示不安全意图
   - 这是基准的特色评测维度，传统单模态分类器无法覆盖

4. **动态策略评测**
   - 策略在运行时切换时，策略遵循准确率从 0.6465（Qwen3-VL-8B baseline）提升到 0.7415
   - 6 个基准族全部达到 SOTA 平均 F1

5. **工程优化：RI-Mask（Rule-Isolation Mask）**
   - 内容前缀共享，各规则分支独立注意力，单次前向并行检查所有规则
   - 30 条规则场景下，2B 模型多模态推理加速 5×+

## 诚实保留

- **自评测偏差**：基准和模型同一团队构建，自评基准通常倾向于美化自身系统
- **残余失败率**：0.7415 意味着约 25% 策略切换场景仍判定错误，医疗/金融等高风险部署中不可忽视
- **未解决问题**：自然语言规则歧义/重叠时的行为未讨论；Slow 模式的生产延迟成本未量化

## 对工作的价值

- **Agent 安全治理**：我们的 agent-security-governance / agent-security-redteam 体系可借鉴"策略即运行时配置"的思路——安全规则不必硬编码进模型，而是运行时可配置的自然语言策略
- **多模态内容审核**：如果未来 Hermes 需要处理图片/多模态输入，跨模态联合风险检测是必须考虑的维度
- **快慢推理范式**：fast-hybrid-slow 三级路由思路可迁移到 agent 的其他决策场景（如工具调用复杂度路由）

## 行动建议

1. 关注 inclusionAI/Sing-Guard 仓库，待权重发布后可作为 Hermes 多模态输入审核的可选护栏层
2. 将"策略运行时注入"模式纳入 agent-security-governance skill 的架构演进考量
3. 跨模态联合风险概念值得在 proactive-push / content-judge 等内容安全场景中引入

---
*笔记类型：auto-explore | 生成时间：2026-07-13*

## 相关笔记

- [SingGuard-Bench（同日另一篇）](./2026-07-13-SingGuard-Bench.md) — 同一基准的不同角度分析
- [SingGuard-Bench（07-09）](./2026-07-09-SingGuard-Bench-.md) — 策略自适应护栏早期分析
- [SingGuard-Bench（07-05）](./2026-07-05-SingGuard-Bench-.md) — SingGuard系列首篇
- [LLM Agent失败模式综合分类法](./2026-07-09-LLM-Agent失败模式综合分类法.md) — Agent安全与失败模式分类
