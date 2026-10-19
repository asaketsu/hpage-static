---
title: Anthropic Managed Agents 三大新功能分析
date: 2026-05-08
tags: [AI-Agent, Anthropic, Claude, 自进化, 多 Agent 协作]
source: 金色传说大聪明 (赛博禅心)
url: https://mp.weixin.qq.com/s/ovZ5v7jJkqDKSu9xmxwt8w
---

# Anthropic 上线「做梦」功能，让 Agent 越睡越聪明

## 核心要点

Anthropic 在 Claude Managed Agents 托管服务中上线了三项新功能：**Dreaming（做梦）**、**Outcomes（成果评估）**、**Multi-Agent Orchestration（多 Agent 协作）**。

---

## 一、Dreaming（做梦）— Agent 的反思整理

### 问题背景

Agent 在每次 session 中会向 memory store 写入学习成果，但长期运行后会出现：
- 重复条目堆积
- 过时信息未被更新
- 相互矛盾的记录

### 解决方案

Dreaming 是一个**异步任务**，在 session 之间运行：

| 输入 | 处理 | 输出 |
|------|------|------|
| 现有 memory store + 最多 100 个 session 记录 | 重复合并、过时替换、交叉分析发现新模式 | 全新整理后的 memory store |

### 核心原则

1. **不修改原始数据** — 输入保持原样，输出写入新 store，不满意可直接丢弃
2. **即时学习 vs 反思整理** — memory 负责记住学到了什么，dreaming 负责想明白这些经验意味着什么
3. **按标准 API token 费率计费** — 耗时几分钟到几十分钟

### 支持模型

- `claude-opus-4-7`
- `claude-sonnet-4-6`

### 状态

Research Preview，需单独申请访问权限

---

## 二、Outcomes（成果评估）— 自动化质量把关

### 机制

```
用户编写 rubric (评分标准 Markdown)
    ↓
Agent 完成任务
    ↓
独立 grader 在独立上下文窗口逐项打分
    ↓
不达标 → 反馈给 Agent → 迭代修改
    ↓
达标 或 达到最大迭代次数 (默认 3 次，最多 20 次)
```

### 效果数据

| 任务类型 | 成功率提升 |
|----------|-----------|
| 整体任务 | +10% |
| docx 生成 | +8.4% |
| pptx 生成 | +10.1% |

> 越难的任务提升越明显

### Rubric 示例

DCF 模型 rubric 会要求：
- 营收预测用过去 5 年历史数据
- WACC 计算标注假设来源
- 敏感性分析必须包含

### 集成

配合 Webhooks 实现异步通知，无需人工盯守

---

## 三、Multi-Agent Orchestration（多 Agent 协作）— 正义的群殴

### 架构

```
Lead Agent (拆解任务)
    ↓
Specialist Agent 1 ─ Specialist Agent 2 ─ Specialist Agent 3 (并行处理)
    │                    │                    │
    └── 独立模型/prompt/工具集 ───────────────┘
    └── 上下文隔离 ───────────────────────────┘
    └── 共享文件系统 ─────────────────────────┘
```

### 特点

| 特性 | 说明 |
|------|------|
| 线程持久化 | Lead Agent 可回头找之前调用的 agent 继续对话 |
| 全程追踪 | Claude Console 可见每个 agent 的每一步操作 |
| 一层委托限制 | Lead 可调用 specialist，但 specialist 不能再调用下一层 |

> 一层委托限制是有意为之，防止链式调用失控

---

## 四、实战案例

### Harvey（法律科技）

| 项目 | 内容 |
|------|------|
| 场景 | 长文法律文书起草 |
| 功能 | Dreaming |
| 效果 | 完成率涨约 **6 倍** |
| 机制 | 记住文件格式技巧和工具使用模式 |

### Netflix（平台工程）

| 项目 | 内容 |
|------|------|
| 场景 | 日志分析 Agent，处理几百个 build 的日志 |
| 功能 | Multi-Agent |
| 效果 | 并行分析，只浮出反复出现的问题模式，忽略一次性噪音 |

### Spiral / by Every（写作工具）

| 项目 | 内容 |
|------|------|
| 场景 | 写作任务生成 |
| 方案 | Haiku 当领队接需求 → Opus 子 Agent 并行写作 → Outcomes 自动质检 |
| 亮点 | 模型分层 + 成本优化 + 质量保障 |

### Wisedocs（医疗文档质检）

| 项目 | 内容 |
|------|------|
| 场景 | 文档质量审核 |
| 效果 | AI+人类协作比纯人类快 **50%**，多抓 **30%** 错误 |
| 洞察 | Managed Agents 成本高（7 倍速度，1/10 成本），只用于 QA 审核环节 |

---

## 五、对 ubot 的启示

### 1. Dreaming vs auto-dream

| 对比项 | Anthropic Dreaming | ubot auto-dream |
|--------|-------------------|-----------------|
| 触发方式 | Session 间异步任务 | Cron 定时任务 |
| 核心理念 | 反思整理 memory | 系统健康检查 + 记忆维护 |
| 可借鉴点 | memory 去重、过时替换、交叉分析发现模式 | — |

**行动**：auto-dream 可增强 memory 整理逻辑，引入"合并重复、替换过时、发现模式"机制

### 2. Outcomes vs review-processor

| 对比项 | Anthropic Outcomes | ubot review-processor |
|--------|-------------------|----------------------|
| 机制 | Rubric 评分 + 迭代修改 | Review 队列处理 |
| 可借鉴点 | 结构化 rubric 评估 | — |

**行动**：review-processor 可引入 rubric 概念，让评估更结构化

### 3. Multi-Agent vs delegate_task

| 对比项 | Anthropic Multi-Agent | ubot delegate_task |
|--------|----------------------|-------------------|
| 委托深度 | 只支持一层 | max_spawn_depth=1 |
| 结论 | 当前架构已符合最佳实践 | 无需改动 |

### 4. Memory 退化问题

文章明确指出 memory 会堆满重复条目、过时信息和矛盾记录——这正是 ubot 需要主动解决的。

**行动**：
- auto-dream 增强 memory 去重逻辑
- evolver 增强 memory 更新机制
- 定期清理过时记忆

---

## 参考链接

- 官方博客: `claude.com/blog/new-in-claude-managed-agents`
- 开发文档: `platform.claude.com/docs/en/managed-agents/overview`
- 申请访问: `claude.com/form/claude-managed-agents`

## 相关笔记
- [Claude-Code四层记忆架构](2026-04-03-Claude-Code四层记忆架构.md)
- [Hermes-Agent-competitor-analysis](2026-04-05-Hermes-Agent-competitor-analysis.md)
- [4-ai-agent-frameworks-comparison](2026-04-13-4-ai-agent-frameworks-comparison.md)
- [Gemini3-AI-Agent-competition](2026-04-16-Gemini3-AI-Agent-competition.md)
- [Hermes-Agent-v0.10.0-insight](2026-04-18-Hermes-Agent-v0.10.0-insight.md)
- [Hermes-Agent-v0.10.0-release-analysis](2026-04-18-Hermes-Agent-v0.10.0-release-analysis.md)
- [Claude-Opus4.7-Claude-Code-最佳实践](2026-04-20-Claude-Opus4.7-Claude-Code-最佳实践.md)
- [ESP-Claw扩展分析-NeuroClaw边缘AI-Agent](2026-04-22-ESP-Claw扩展分析-NeuroClaw边缘AI-Agent.md)
- [MCP协议与Agentic-LLM-2025趋势](2026-04-23-MCP协议与Agentic-LLM-2025趋势.md)
- [深入源码-Hermes-Agent-如何实现Self-Improving](2026-04-23-深入源码-Hermes-Agent-如何实现Self-Improving.md)
- [深入源码Hermes-Agent-Self-Improving](2026-04-23-深入源码Hermes-Agent-Self-Improving.md)
- [MCP协议生态与Agentic-RAG架构深度学习](2026-04-27-MCP协议生态与Agentic-RAG架构深度学习.md)
- [LLM-Agent驱动量化交易系统前沿学习](2026-04-29-LLM-Agent驱动量化交易系统前沿学习.md)
- [Meta-Hyperagents自适应Agent框架](2026-04-30-Meta-Hyperagents自适应Agent框架.md)
- [stoc蒸馏-AI-Agent自学习量化交易系统](2026-04-30-stoc蒸馏-AI-Agent自学习量化交易系统.md)
- [AI-Agent记忆架构前沿学习](2026-05-01-AI-Agent记忆架构前沿学习.md)
- [deepseek-agent-ecosystem](2026-05-01-deepseek-agent-ecosystem.md)
- [AI-Agent-Protocol-Ecosystem-2026-学习](2026-05-03-AI-Agent-Protocol-Ecosystem-2026-学习.md)
- [ai-agent-resources-ecosystem](2026-05-03-ai-agent-resources-ecosystem.md)
- [智能教育-自适应评估](2026-05-03-智能教育-自适应评估.md)
- [Agent协议生态2026最新进展-MCP-A2A深度融合](2026-05-04-Agent协议生态2026最新进展-MCP-A2A深度融合.md)
- [个人Agent自进化五步闭环](2026-05-04-个人Agent自进化五步闭环.md)
- [Claude-MCP直连Fusion-Blender-AI操控工业设计](2026-05-05-Claude-MCP直连Fusion-Blender-AI操控工业设计.md)
- [Claude创意连接器9大工具-Blender-MCP深度解析](2026-05-05-Claude创意连接器9大工具-Blender-MCP深度解析.md)
- [Zero-to-CAD-Agent闭环合成百万级可执行CAD程序](2026-05-05-Zero-to-CAD-Agent闭环合成百万级可执行CAD程序.md)
- [tradingagents-deep-analysis](2026-05-05-tradingagents-deep-analysis.md)
- [SOUL-md-Agent-Partner-Transformation](2026-05-07-SOUL-md-Agent-Partner-Transformation.md)
- [Superpowers-Agentic技能框架](2026-05-07-Superpowers-Agentic技能框架.md)
- [AI-Agent控制流](2026-05-08-AI-Agent控制流.md)
- [addyosmani-agent-skills生产级Agent技能包](2026-05-08-addyosmani-agent-skills生产级Agent技能包.md)
- [企业AI转型三步法-知识库技能化智能体](2026-05-08-企业AI转型三步法-知识库技能化智能体.md)
- [AG-UI-AI-Agent前端标准](2026-05-09-AG-UI-AI-Agent前端标准.md)
- [Agent-native-PM方法论](2026-05-09-Agent-native-PM方法论.md)
- [Claude-Code工程师放弃Markdown转HTML](2026-05-09-Claude-Code工程师放弃Markdown转HTML.md)
- [OfficeCLI-AI-Agent的Office工具](2026-05-09-OfficeCLI-AI-Agent的Office工具.md)
- [AI趋势2026-推理时计算与反思Agent](2026-05-11-AI趋势2026-推理时计算与反思Agent.md)
- [具身智能2026-世界模型VLA车企入局](2026-05-11-具身智能2026-世界模型VLA车企入局.md)
- [具身智能2026从实验到实战](2026-05-11-具身智能2026从实验到实战.md)
- [Claude-3D-CAD-创意连接器深度分析](2026-05-13-Claude-3D-CAD-创意连接器深度分析.md)
- [Agent工程4月实践-不要一上来就做Agent](2026-05-14-Agent工程4月实践-不要一上来就做Agent.md)
- [HTML-Anything-Agent驱动HTML编辑器](2026-05-14-HTML-Anything-Agent驱动HTML编辑器.md)
- [MATLAB-Agentic-Toolkit分析](2026-05-14-MATLAB-Agentic-Toolkit分析.md)
- [手撸Agent-ReAct-Loop从零实现](2026-05-14-手撸Agent-ReAct-Loop从零实现.md)
- [上下文才是Agent的命门-QClaw上下文竞争论](2026-05-15-上下文才是Agent的命门-QClaw上下文竞争论.md)
- [OpenHuman-记忆树AI智能体-i龙虾](2026-05-16-OpenHuman-记忆树AI智能体-i龙虾.md)
- [PicoClaw-超轻量AI-Agent框架](2026-05-16-PicoClaw-超轻量AI-Agent框架.md)
- [具身智能前沿学习](2026-05-17-具身智能前沿学习.md)
- [20260513-llm-wiki-obsidian-gbrain-知识自组织与自进化](20260513-llm-wiki-obsidian-gbrain-知识自组织与自进化.md)
- [智能教育-AI-tutoring](explore/2026-05-05-智能教育-AI-tutoring.md)
- [ai-agent-protocol-stack-2026](explore/2026-05-06-ai-agent-protocol-stack-2026.md)
- [ai-agent-protocol-wars-a2a-mcp](explore/2026-05-08-ai-agent-protocol-wars-a2a-mcp.md)
- [ai-coding-agent-competition-landscape](explore/2026-05-08-ai-coding-agent-competition-landscape.md)
- [2025年5月AI大爆发-Claude4-Qwen3-DeepSeek-R1](explore/2026-05-09-2025年5月AI大爆发-Claude4-Qwen3-DeepSeek-R1.md)
- [ai-agent-protocols-mcp-a2a-acp](explore/2026-05-09-ai-agent-protocols-mcp-a2a-acp.md)
- [开源AI春季爆发-模型推理Agent](explore/2026-05-09-开源AI春季爆发-模型推理Agent.md)
- [mcp-a2a-agent-ecosystem](explore/2026-05-10-mcp-a2a-agent-ecosystem.md)
- [ai-agent-protocols-mcp-a2a](explore/2026-05-11-ai-agent-protocols-mcp-a2a.md)
- [AI-Agent架构-MCP-A2A协议栈](explore/2026-05-13-AI-Agent架构-MCP-A2A协议栈.md)
- [Agentic-SOC-安全自动化的范式转变](explore/2026-05-13-Agentic-SOC-安全自动化的范式转变.md)
- [Agentic-Engineering-从Vibe-Coding到Agent工程](explore/2026-05-14-Agentic-Engineering-从Vibe-Coding到Agent工程.md)
- [ai-agent-architecture](explore/2026-05-15-ai-agent-architecture.md)
- [ai开源生态-huggingface春季](explore/2026-05-15-ai开源生态-huggingface春季.md)
- [AI-Agent-协议生态-深度整合学习](explore/2026-05-16-AI-Agent-协议生态-深度整合学习.md)
- [Agentic-AI元年-智能体全面落地趋势](explore/2026-05-16-Agentic-AI元年-智能体全面落地趋势.md)
- [HuggingFace-Spring2026-开源生态报告](explore/2026-05-16-HuggingFace-Spring2026-开源生态报告.md)
- [qclaw-上下文四层模型](explore/2026-05-16-qclaw-上下文四层模型.md)
- [具身智能-从造产品到抢落地六大趋势](explore/2026-05-16-具身智能-从造产品到抢落地六大趋势.md)
- [竞品动态-Agentic-Engineering范式转变](explore/2026-05-16-竞品动态-Agentic-Engineering范式转变.md)
- [agent-collaboration-self-evolution](explore/2026-05-17-agent-collaboration-self-evolution.md)
- [具身智能2026数据规模化元年](explore/2026-05-17-具身智能2026数据规模化元年.md)
- [hermes-agent-源码拆解自我进化机制](hermes-agent-源码拆解自我进化机制.md)
- [llm-wiki-gbrain-agent-evolution_33aa818c](llm-wiki-gbrain-agent-evolution_33aa818c.md)
- [AI幻觉案例分析-Hermes-Agent不实报道](orphan/2026-04-19-AI幻觉案例分析-Hermes-Agent不实报道.md)
- [深入源码-Hermes-Agent-Self-Improving源码拆解](orphan/2026-04-24-深入源码-Hermes-Agent-Self-Improving源码拆解.md)
- [智能教育-personalized-learning](orphan/2026-05-04-智能教育-personalized-learning.md)
- [agent-coding-playbook-analysis](orphan/2026-05-05-agent-coding-playbook-analysis.md)
- [具身智能机器人2025年终盘点](orphan/2026-05-05-具身智能机器人2025年终盘点.md)
- [具身智能机器人2025-商业化元年](orphan/2026-05-09-具身智能机器人2025-商业化元年.md)
- [claude-learning-roadmap](orphan/2026-05-10-claude-learning-roadmap.md)
- [0元打通Claude-Codex-OpenCode免费模型6入口](orphan/2026-05-11-0元打通Claude-Codex-OpenCode免费模型6入口.md)
- [HuggingFace-春季生态-Agentic-World-Modeling](orphan/2026-05-13-HuggingFace-春季生态-Agentic-World-Modeling.md)
- [具身智能量产关键年](orphan/2026-05-15-具身智能量产关键年.md)
- [HTML的不合理有效性-Claude-Code-团队](orphan/2026-05-16-HTML的不合理有效性-Claude-Code-团队.md)
- [GenericAgent](orphan/GenericAgent.md)
- [skills-autonomous-ai-agents](skills-autonomous-ai-agents.md)
- [竞品吸收笔记_GenericAgent](竞品吸收笔记_GenericAgent.md)
