# 开源具身智能项目横评 — LeRobot vs OpenVLA vs RT-2

> 探索日期: 2026-05-21 | 来源: GitHub API

## 核心对比

| 项目 | 机构 | Stars | 定位 |
|------|------|-------|------|
| **LeRobot** | HuggingFace | 24,197 | 端到端机器人学习库，降低门槛 |
| **OpenVLA** | Stanford | 6,221 | 视觉-语言-动作模型，仿真→真实迁移 |
| **RT-2** | Google DeepMind | - | 机器人 Transformer v2，多模态策略 |

## 技术路线差异

**LeRobot**: 工程化优先
- 支持多种策略架构（ACT、Diffusion Policy、TRPO）
- 内置数据集加载、训练、推理全流程
- 适合快速原型验证

**OpenVLA**: 模型驱动
- 基于 LLaVA 架构扩展
- VLA (Vision-Language-Action) 统一建模
- 强调 sim-to-real 迁移能力

**RT-2**: 规模驱动
- PaLI + PaCa 多模态基础
- 大规模预训练 + 机器人微调
- 闭源权重，研究导向

## 选型建议

- **快速上手** → LeRobot（文档完善，社区活跃）
- **仿真研究** → OpenVLA（sim-to-real 路径清晰）
- **生产部署** → 需结合具体硬件，当前无成熟方案

## 下一步

- [ ] 深入 LeRobot ACT 策略实现
- [ ] 测试 OpenVLA 在 Isaac Gym 的表现
- [ ] 评估 Jetson 端部署可行性

---
*标签: #robotics #embodied-ai #open-source*

## 相关笔记
- [Qwen3.7-Agent Frontier](../2026-05-21-Qwen3.7-Agent Frontier.md)
- [react-agent-llm-agentic-training-research](../2026-05-21-react-agent-llm-agentic-training-research.md)
- [RD-Agent-Quant-multi-agent-quant-framework-deep-dive](2026-05-18-RD-Agent-Quant-multi-agent-quant-framework-deep-dive.md)
- [IBM2026多智能体趋势](2026-05-19-IBM2026多智能体趋势.md)
- [agent-self-evolution-reflexion-metacognition](2026-05-19-agent-self-evolution-reflexion-metacognition.md)
- [AgentSelfEvolution-LearningSystem-深度探索](2026-05-20-AgentSelfEvolution-LearningSystem-深度探索.md)
- [Hermes-Agent源码解析-越用越聪明的秘密](2026-05-20-Hermes-Agent源码解析-越用越聪明的秘密.md)
- [TencentDB-Agent-Memory架构深度分析与进化建议](2026-05-20-TencentDB-Agent-Memory架构深度分析与进化建议.md)
- [Agent自我进化-Reflexion-ReAct-元认知框架](2026-05-21-Agent自我进化-Reflexion-ReAct-元认知框架.md)
- [agent-capability-boundary-detection-20260518](agent-capability-boundary-detection-20260518.md)
- [agent-drift-stability-degradation-20260518](agent-drift-stability-degradation-20260518.md)
- [agent-stability-degradation-drift-detection](agent-stability-degradation-drift-detection.md)
- [tradingagents-cn-deep-20260520](tradingagents-cn-deep-20260520.md)
