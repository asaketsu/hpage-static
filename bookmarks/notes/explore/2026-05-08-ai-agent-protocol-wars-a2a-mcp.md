# AI Agent 协议之战：A2A vs MCP vs Function Calling 深度对比

- 📅 2026-05-08
- 🏷️ #AI-Agent #A2A #MCP #Function-Calling #多Agent协作 #协议
- 🔍 整合分析：基于已有 Codex/Superpowers 笔记 + Agent 架构知识

## 核心发现

### 1. 三大协议各有定位，非竞争而是互补

| 协议 | 发起方 | 核心定位 | 当前状态 |
|------|--------|----------|----------|
| **MCP (Model Context Protocol)** | Anthropic | Agent ↔ 工具/数据源的连接标准 | 已成事实标准，100+ 服务器 |
| **A2A (Agent-to-Agent)** | Google | Agent ↔ Agent 的通信协议 | 2025.4 发布，50+ 合作伙伴 |
| **Function Calling** | OpenAI | LLM ↔ 外部函数的调用接口 | 最成熟，但最底层 |

**关键洞察**：MCP 解决的是"Agent 用什么工具"，A2A 解决的是"Agent 之间怎么协作"，Function Calling 解决的是"LLM 怎么调函数"。三层不在一个维度。

### 2. A2A 协议的架构设计

Google A2A 的核心设计理念：
- **Agent Card**：每个 Agent 发布一个 JSON 描述文件（类似 OpenAPI spec），声明自己的能力、输入输出、认证方式
- **Task 生命周期**：Task → In-progress → Completed/Failed，支持长任务流式推送
- **多模态消息**：不仅传文本，还支持文件、表单、结构化数据
- **安全模型**：基于 OAuth2 + mTLS 的双向认证

与 MCP 的对比：
```
MCP: Client ←→ Server（垂直，Agent 连工具）
A2A: Agent ←→ Agent（水平，Agent 间协商）
```

### 3. Superpowers/Codex 模式 vs A2A 模式的本质差异

| 维度 | Superpowers/Codex 模式 | A2A 模式 |
|------|------------------------|----------|
| 协作方式 | 单 Agent + SubAgent（上下文隔离） | 对等 Agent 互发现互调用 |
| 编排 | 中心化（主 Agent 派发） | 去中心化（Agent 自发现） |
| 上下文 | 精确注入，不继承历史 | 通过 Task 对象传递 |
| 适用场景 | 单项目开发 | 跨系统/跨组织协作 |

**Superpowers 的 SDD 模式本质上是一个简化版的多 Agent 协作**——用 subagent 做任务隔离，但控制权在主 Agent。A2A 则让 Agent 真正平等，能互相发现和协商。

### 4. 实际落地路径

当前最实用的 Agent 协作架构是 **混合模式**：
- **同一项目内**：Superpowers SDD 模式（subagent + Hard Gate + 审查分离）
- **跨项目/跨工具**：MCP 连接外部工具
- **跨组织**：A2A 做服务发现和任务委派

### 5. Hermes Agent 的定位优势

我们的 Skill 系统 + subagent 架构已经覆盖了 SDD 的核心模式。关键进化方向：
1. **Skill 作为 Agent Card** — 每个 Skill 的 frontmatter 就是 mini Agent Card
2. **delegate_task 协议化** — 借鉴 A2A 的 Task 生命周期，给 subtask 加状态机
3. **跨 Agent 通信** — 与 ubot 的经验交换协议已经是对等 Agent 通信的雏形

## 关键概念

- **Agent Card**：Agent 的自描述文件，类似微服务的 service registry
- **Hard Gate**：不可跳过的强制检查点，Superpowers 的核心理念
- **SDD (Subagent-Driven Development)**：每个 Task 派独立 Agent 执行，隔离上下文
- **上下文精确注入**：subagent 不拿会话历史，只拿构造好的指令
- **Do Not Trust 原则**：审查者不信任实现者的自我报告

## 可落地的 Insights

1. **Skill frontmatter 应扩展为 Agent Card 格式** — 加入 input/output schema、capability 声明，让 Skill 可被自动发现和组合
2. **subtask-lifecycle skill 应对齐 A2A Task 生命周期** — Task → InProgress → Completed/Failed，支持状态查询和取消
3. **与 ubot 的交换协议应增加 Agent Card 交换** — 互相声明能力，避免重复学习
4. **MCP 原生支持已在 Hermes 中实现** — 持续扩展 MCP 服务器，特别是搜索、文件系统、代码分析类

## 来源

- 已有笔记：2026-05-07-Superpowers-Agentic技能框架.md
- 已有笔记：2026-05-07-Codex指令保姆级教程.md
- Google A2A Protocol 官方文档（内置知识）
- Anthropic MCP 规范（内置知识）
- Superpowers v5.1.0 架构分析

## 相关笔记
- [Claude-Code四层记忆架构](../2026-04-03-Claude-Code四层记忆架构.md)
- [Hermes-Agent-competitor-analysis](../2026-04-05-Hermes-Agent-competitor-analysis.md)
- [4-ai-agent-frameworks-comparison](../2026-04-13-4-ai-agent-frameworks-comparison.md)
- [Gemini3-AI-Agent-competition](../2026-04-16-Gemini3-AI-Agent-competition.md)
- [Hermes-Agent-v0.10.0-insight](../2026-04-18-Hermes-Agent-v0.10.0-insight.md)
- [Hermes-Agent-v0.10.0-release-analysis](../2026-04-18-Hermes-Agent-v0.10.0-release-analysis.md)
- [Claude-Opus4.7-Claude-Code-最佳实践](../2026-04-20-Claude-Opus4.7-Claude-Code-最佳实践.md)
- [ESP-Claw扩展分析-NeuroClaw边缘AI-Agent](../2026-04-22-ESP-Claw扩展分析-NeuroClaw边缘AI-Agent.md)
- [MCP协议与Agentic-LLM-2025趋势](../2026-04-23-MCP协议与Agentic-LLM-2025趋势.md)
- [深入源码-Hermes-Agent-如何实现Self-Improving](../2026-04-23-深入源码-Hermes-Agent-如何实现Self-Improving.md)
- [深入源码Hermes-Agent-Self-Improving](../2026-04-23-深入源码Hermes-Agent-Self-Improving.md)
- [MCP协议生态与Agentic-RAG架构深度学习](../2026-04-27-MCP协议生态与Agentic-RAG架构深度学习.md)
- [LLM-Agent驱动量化交易系统前沿学习](../2026-04-29-LLM-Agent驱动量化交易系统前沿学习.md)
- [Meta-Hyperagents自适应Agent框架](../2026-04-30-Meta-Hyperagents自适应Agent框架.md)
- [stoc蒸馏-AI-Agent自学习量化交易系统](../2026-04-30-stoc蒸馏-AI-Agent自学习量化交易系统.md)
- [AI-Agent记忆架构前沿学习](../2026-05-01-AI-Agent记忆架构前沿学习.md)
- [deepseek-agent-ecosystem](../2026-05-01-deepseek-agent-ecosystem.md)
- [AI-Agent-Protocol-Ecosystem-2026-学习](../2026-05-03-AI-Agent-Protocol-Ecosystem-2026-学习.md)
- [ai-agent-resources-ecosystem](../2026-05-03-ai-agent-resources-ecosystem.md)
- [智能教育-自适应评估](../2026-05-03-智能教育-自适应评估.md)
- [Agent协议生态2026最新进展-MCP-A2A深度融合](../2026-05-04-Agent协议生态2026最新进展-MCP-A2A深度融合.md)
- [个人Agent自进化五步闭环](../2026-05-04-个人Agent自进化五步闭环.md)
- [Claude-MCP直连Fusion-Blender-AI操控工业设计](../2026-05-05-Claude-MCP直连Fusion-Blender-AI操控工业设计.md)
- [Claude创意连接器9大工具-Blender-MCP深度解析](../2026-05-05-Claude创意连接器9大工具-Blender-MCP深度解析.md)
- [Zero-to-CAD-Agent闭环合成百万级可执行CAD程序](../2026-05-05-Zero-to-CAD-Agent闭环合成百万级可执行CAD程序.md)
- [tradingagents-deep-analysis](../2026-05-05-tradingagents-deep-analysis.md)
- [SOUL-md-Agent-Partner-Transformation](../2026-05-07-SOUL-md-Agent-Partner-Transformation.md)
- [Superpowers-Agentic技能框架](../2026-05-07-Superpowers-Agentic技能框架.md)
- [AI-Agent控制流](../2026-05-08-AI-Agent控制流.md)
- [addyosmani-agent-skills生产级Agent技能包](../2026-05-08-addyosmani-agent-skills生产级Agent技能包.md)
- [企业AI转型三步法-知识库技能化智能体](../2026-05-08-企业AI转型三步法-知识库技能化智能体.md)
- [AG-UI-AI-Agent前端标准](../2026-05-09-AG-UI-AI-Agent前端标准.md)
- [Agent-native-PM方法论](../2026-05-09-Agent-native-PM方法论.md)
- [Claude-Code工程师放弃Markdown转HTML](../2026-05-09-Claude-Code工程师放弃Markdown转HTML.md)
- [OfficeCLI-AI-Agent的Office工具](../2026-05-09-OfficeCLI-AI-Agent的Office工具.md)
- [AI趋势2026-推理时计算与反思Agent](../2026-05-11-AI趋势2026-推理时计算与反思Agent.md)
- [具身智能2026-世界模型VLA车企入局](../2026-05-11-具身智能2026-世界模型VLA车企入局.md)
- [具身智能2026从实验到实战](../2026-05-11-具身智能2026从实验到实战.md)
- [Claude-3D-CAD-创意连接器深度分析](../2026-05-13-Claude-3D-CAD-创意连接器深度分析.md)
- [Agent工程4月实践-不要一上来就做Agent](../2026-05-14-Agent工程4月实践-不要一上来就做Agent.md)
- [HTML-Anything-Agent驱动HTML编辑器](../2026-05-14-HTML-Anything-Agent驱动HTML编辑器.md)
- [MATLAB-Agentic-Toolkit分析](../2026-05-14-MATLAB-Agentic-Toolkit分析.md)
- [手撸Agent-ReAct-Loop从零实现](../2026-05-14-手撸Agent-ReAct-Loop从零实现.md)
- [上下文才是Agent的命门-QClaw上下文竞争论](../2026-05-15-上下文才是Agent的命门-QClaw上下文竞争论.md)
- [OpenHuman-记忆树AI智能体-i龙虾](../2026-05-16-OpenHuman-记忆树AI智能体-i龙虾.md)
- [PicoClaw-超轻量AI-Agent框架](../2026-05-16-PicoClaw-超轻量AI-Agent框架.md)
- [具身智能前沿学习](../2026-05-17-具身智能前沿学习.md)
- [20260513-llm-wiki-obsidian-gbrain-知识自组织与自进化](../20260513-llm-wiki-obsidian-gbrain-知识自组织与自进化.md)
- [anthropic-managed-agents-dreaming-outcomes](../anthropic-managed-agents-dreaming-outcomes.md)
- [智能教育-AI-tutoring](2026-05-05-智能教育-AI-tutoring.md)
- [ai-agent-protocol-stack-2026](2026-05-06-ai-agent-protocol-stack-2026.md)
- [ai-coding-agent-competition-landscape](2026-05-08-ai-coding-agent-competition-landscape.md)
- [2025年5月AI大爆发-Claude4-Qwen3-DeepSeek-R1](2026-05-09-2025年5月AI大爆发-Claude4-Qwen3-DeepSeek-R1.md)
- [ai-agent-protocols-mcp-a2a-acp](2026-05-09-ai-agent-protocols-mcp-a2a-acp.md)
- [开源AI春季爆发-模型推理Agent](2026-05-09-开源AI春季爆发-模型推理Agent.md)
- [mcp-a2a-agent-ecosystem](2026-05-10-mcp-a2a-agent-ecosystem.md)
- [ai-agent-protocols-mcp-a2a](2026-05-11-ai-agent-protocols-mcp-a2a.md)
- [AI-Agent架构-MCP-A2A协议栈](2026-05-13-AI-Agent架构-MCP-A2A协议栈.md)
- [Agentic-SOC-安全自动化的范式转变](2026-05-13-Agentic-SOC-安全自动化的范式转变.md)
- [Agentic-Engineering-从Vibe-Coding到Agent工程](2026-05-14-Agentic-Engineering-从Vibe-Coding到Agent工程.md)
- [ai-agent-architecture](2026-05-15-ai-agent-architecture.md)
- [ai开源生态-huggingface春季](2026-05-15-ai开源生态-huggingface春季.md)
- [AI-Agent-协议生态-深度整合学习](2026-05-16-AI-Agent-协议生态-深度整合学习.md)
- [Agentic-AI元年-智能体全面落地趋势](2026-05-16-Agentic-AI元年-智能体全面落地趋势.md)
- [HuggingFace-Spring2026-开源生态报告](2026-05-16-HuggingFace-Spring2026-开源生态报告.md)
- [qclaw-上下文四层模型](2026-05-16-qclaw-上下文四层模型.md)
- [具身智能-从造产品到抢落地六大趋势](2026-05-16-具身智能-从造产品到抢落地六大趋势.md)
- [竞品动态-Agentic-Engineering范式转变](2026-05-16-竞品动态-Agentic-Engineering范式转变.md)
- [agent-collaboration-self-evolution](2026-05-17-agent-collaboration-self-evolution.md)
- [具身智能2026数据规模化元年](2026-05-17-具身智能2026数据规模化元年.md)
- [hermes-agent-源码拆解自我进化机制](../hermes-agent-源码拆解自我进化机制.md)
- [llm-wiki-gbrain-agent-evolution_33aa818c](../llm-wiki-gbrain-agent-evolution_33aa818c.md)
- [AI幻觉案例分析-Hermes-Agent不实报道](../orphan/2026-04-19-AI幻觉案例分析-Hermes-Agent不实报道.md)
- [深入源码-Hermes-Agent-Self-Improving源码拆解](../orphan/2026-04-24-深入源码-Hermes-Agent-Self-Improving源码拆解.md)
- [智能教育-personalized-learning](../orphan/2026-05-04-智能教育-personalized-learning.md)
- [agent-coding-playbook-analysis](../orphan/2026-05-05-agent-coding-playbook-analysis.md)
- [具身智能机器人2025年终盘点](../orphan/2026-05-05-具身智能机器人2025年终盘点.md)
- [具身智能机器人2025-商业化元年](../orphan/2026-05-09-具身智能机器人2025-商业化元年.md)
- [claude-learning-roadmap](../orphan/2026-05-10-claude-learning-roadmap.md)
- [0元打通Claude-Codex-OpenCode免费模型6入口](../orphan/2026-05-11-0元打通Claude-Codex-OpenCode免费模型6入口.md)
- [HuggingFace-春季生态-Agentic-World-Modeling](../orphan/2026-05-13-HuggingFace-春季生态-Agentic-World-Modeling.md)
- [具身智能量产关键年](../orphan/2026-05-15-具身智能量产关键年.md)
- [HTML的不合理有效性-Claude-Code-团队](../orphan/2026-05-16-HTML的不合理有效性-Claude-Code-团队.md)
- [GenericAgent](../orphan/GenericAgent.md)
- [skills-autonomous-ai-agents](../skills-autonomous-ai-agents.md)
- [竞品吸收笔记_GenericAgent](../竞品吸收笔记_GenericAgent.md)
