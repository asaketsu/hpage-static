# Andrew Ng：AI Engineer 才是大机会，不是 FDE

> 来源：微信公众号 | 2026-06-08
> 原文：https://mp.weixin.qq.com/s/v-9mDT4-HS17Q7KVDDLR9w
> 参考：Andrew Ng《The Batch》Newsletter, 2026年6月

## 背景

OpenAI、Anthropic 疯狂招聘"AI 现场部署工程师"（FDE），三天上千份简历。Andrew Ng 冷静判断：FDE 确实重要，但真正大机会在 AI Engineer。

## FDE：二十年前的老角色

Palantir 最早发明 FDE——把工程师派到物理隔离的政府客户现场。核心能力组合：技术过硬 + 沟通理解 + 业务适配 + 快速摸清陌生系统。

**FDE 复兴原因**：从"通用 LLM"到"定制化 Agent 工作流"之间有巨大鸿沟，需要人肉适配。

## Andrew Ng 三层逻辑：AI Engineer > FDE

1. **数量差距**：企业接受 2-3 个 FDE 驻场，但需要几十上百个自己的 AI Engineer
2. **供应商锁定风险**：FDE 绑定特定厂商，在 AI 按周迭代的时代，保持 optionality（可选择性）是战略资产
3. **通用性**：AI Engineer 能力可迁移（Claude Code → Codex → 其他），FDE 技能绑定厂商产品

## 角色裂变预测

类比"软件工程师"二十年来的碎片化（前端/后端/DevOps/SRE…），AI Engineer 将裂变为：

- **LLMOps Engineer** — 模型部署、监控、性能优化
- **Evals Engineer** — AI 系统评估体系设计
- **AI Data Engineer** — 训练/评估/合成数据全生命周期
- **Harness Engineer** — AI Agent 执行框架与工作流编排
- **AI Product Engineer** — 理解 AI 能力边界 × 用户需求 × 产品设计
- **AI Security Engineer** — prompt 注入、数据泄露、Agent 越权
- **AI Integration Engineer** — 把 AI 能力嵌入现有系统

## AI Engineer 核心技能模型（四力）

不需要懂 Transformer 数学推导。需要：

1. **判断力** — 知道何时该用/不该用 AI，输出何时可信
2. **设计能力** — 设计 prompt 和工作流让 AI 在正确框架内发挥
3. **评估能力** — 判断 AI 输出质量，建立质量标准
4. **集成能力** — 把 AI 输出嵌入真实产品和业务流程

## 关键警示案例

- AI coding agent 执行 `rm -rf` 误删开发者整台 Mac（~/ 路径错误）
- Meta Instagram AI 客服被黑客几句对话骗走账号控制权

**结论**：AI 能力越强，使用 AI 的门槛反而越高。不需要懂底层原理，但必须懂 AI 会怎么出错。

## 中国市场特殊性

- AI 落地瓶颈是业务适配，不是技术
- 数据孤岛、流程僵化、组织惯性是真正障碍
- 能把 AI 能力翻译成企业"能用、敢用、愿意用"的方案的人最稀缺

## 实操建议

1. 从今天开始用 AI 干活，不等培训
2. 保持通用，不急于锁死细分方向
3. 关注"翻译"能力（AI 能力 ↔ 业务价值）
4. 理解安全边界，在架构层面设防护

---

## 相关笔记

- [2026-06-05-Anthropic开源AI漏洞发现框架-Defending-Code-Reference-Harness](./2026-06-05-Anthropic开源AI漏洞发现框架-Defending-Code-Reference-Harness.md)
- [2026-05-30-Liquid-AI-LFM2.5-8B-A1B-MoE边缘模型新标杆](./2026-05-30-Liquid-AI-LFM2.5-8B-A1B-MoE边缘模型新标杆.md)
- [2026-04-01-Ontology驱动的AI知识引擎](./2026-04-01-Ontology驱动的AI知识引擎.md)
- [2026-04-01-如何在AI时代找回你被埋没的创造力](./2026-04-01-如何在AI时代找回你被埋没的创造力.md)
- [2026-05-22-Google-AI-Mode搜索广告-AI商业化的分水岭](./2026-05-22-Google-AI-Mode搜索广告-AI商业化的分水岭.md)
