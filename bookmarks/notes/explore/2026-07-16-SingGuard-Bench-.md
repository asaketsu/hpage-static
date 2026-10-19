# SingGuard-Bench 多模态安全评测基准

来源：arXiv 2606.22873 (SingGuard: A Policy-Adaptive Multimodal LLM Guardrail with Dynamic Reasoning, 2026-06)
代码仓库：https://github.com/inclusionAI/Sing-Guard

## 摘要

SingGuard-Bench 是伴随 SingGuard 模型家族推出的多模态安全护栏评测基准。核心创新在于将"活跃安全策略（active policy）"作为运行时输入，而非训练时固定标签集。模型接收自然语言规则后，逐条校验内容，同时输出安全标签与触发的具体规则。

## 关键发现

- 数据规模：56,340 测试样本，80+ 细粒度风险类型，三层安全分类法，覆盖 35 个数据集
- 评测覆盖：图像审核、多模态问答、对抗攻击（字体变形/语义同构/角色扮演等）、跨模态联合风险（图文各自无害但组合后隐含恶意）、动态规则评估、多语言安全
- 核心指标：动态策略评估中，策略遵循准确率从 0.6465 提升至 0.7415（相对 Qwen3-VL-8B 基线）
- 推理模式：支持 fast（直接判断，低延迟）、hybrid（混合路由）、slow（逐规则深度推理）三种模式
- RL 优化：fast-slow 解耦强化学习，避免 fast token 对后续推理产生锚定效应
- 加速技术：RI-Mask（基于 PyTorch FlexAttention 的块稀疏注意力），30 条活跃规则下推理加速 5 倍以上

## 对工作的价值

- 安全护栏架构参考：运行时策略注入范式，可应用于 Hermes Agent 内容安全审核场景
- 多模态安全：VLM 部署场景下的跨模态联合风险检测思路
- 推理弹性：fast-to-slow 推理谱系设计，平衡延迟与可解释性，适用于不同吞吐量的审核负载
- RL 训练方法：解耦 fast-slow 的强化学习目标，值得借鉴到 Agent 的决策流程优化

## 行动建议

- 关注 https://github.com/inclusionAI/Sing-Guard 仓库，追踪模型权重和推理代码
- 评估是否需要将 SingGuard 的运行时策略注入思想引入 Hermes 内容审核 pipeline
- 记录 RI-Mask 技术，作为多标签/多维度评估加速方案的技术储备

## 相关笔记

- [AI安全红队技术2026深度探索](./2026-05-17-AI安全红队技术2026-深度探索.md) — AI安全攻防全景
