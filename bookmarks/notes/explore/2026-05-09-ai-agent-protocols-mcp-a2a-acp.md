# AI Agent 协议全景：MCP / A2A / ACP / AGP / A2A-Star

> 探索日期：2026-05-09 | 来源：getstream.io, dev.to, onereach.ai, tinyfish search

## 核心发现

### 1. 五大主流协议各司其职
2026 年 AI Agent 协议生态已形成明确分工：
| 协议 | 核心功能 | 发起方 | 适用场景 |
|------|----------|--------|----------|
| **MCP** | Agent ↔ 工具/数据源集成 | Anthropic | 单 Agent 调用外部 API/DB/文件系统 |
| **A2A** | Agent ↔ Agent 多智能体协作 | Google | 多 Agent 任务委派、跨系统协调 |
| **ACP** | Agent Communication Protocol | IBM | Agent 间消息传递与状态同步 |
| **AGP** | Agent Gateway Protocol | Linux Foundation (AAIF) | 网关级路由与协议翻译 |
| **A2A-Star** | A2A 增强版（流式+安全） | 社区 | 高吞吐实时 Agent 协作 |

### 2. AAIF（Agentic AI Foundation）统一生态
- **2025年12月成立**，隶属 Linux Foundation，6 个创始成员（Google、Anthropic、IBM 等）
- 目标：统一 MCP/A2A/ACP 等协议的互操作性，避免碎片化
- 关键产出：协议兼容矩阵 + 跨协议桥接标准

### 3. MCP 聚焦「工具调用」而非「Agent 通信」
- MCP 本质是 **Agent 连接外部资源的标准化接口**
- 通过 MCP Server 暴露能力（API、DB、文件系统），Agent 用结构化 schema 查询和调用
- 核心特性：能力发现（Capability Discovery）、工具抽象、结构化上下文 schema、解耦扩展
- **不负责 Agent 间通信**，这是 A2A 的领域

### 4. A2A 的三步协作生命周期
1. **Discovery**：Client Agent 根据 Agent Card 发现最合适的 Remote Agent
2. **Authorization**：验证权限，授予控制范围（scope）
3. **Communication**：通过 HTTPS + JSON-RPC 消息传递，支持 SSE 实时流式推送
- 核心特性：P2P 任务委派、动态协商（propose/accept/counter-offer）、流式状态同步

### 5. MCP + A2A 互补，不是竞争
- **MCP = Agent 的「手」**（连接工具和数据）
- **A2A = Agent 的「社交网络」**（Agent 间协调）
- 实际部署中通常 **同时使用**：Agent 通过 MCP 访问工具，通过 A2A 与其他 Agent 协作

## 关键概念

- **Agent Card**：A2A 中 Agent 的「名片」，声明能力、端点、认证方式
- **MCP Server**：封装外部系统为标准化接口的中介服务
- **SSE（Server-Sent Events）**：A2A 推荐的实时通信方式（优于 polling）
- **JSON-RPC**：A2A 的消息信封格式
- **AAIF**：Agentic AI Foundation，Linux Foundation 下的 Agent 协议统一组织

## 可落地的 Insights

1. **对 Hermes 的启示**：Hermes 的 MCP 集成已在正确轨道上（native MCP client）。可以探索 A2A 支持，让多个 Hermes 实例或不同 Agent 框架间协作
2. **Agentic 架构模式**：单 Agent + MCP 工具链适合大多数场景；多 Agent + A2A 适合需要专业化分工的复杂任务
3. **协议选择决策树**：需要外部数据/API → MCP；需要多 Agent 协调 → A2A；两者都要 → MCP + A2A
4. **AAIF 标准化意味着**：未来工具/Agent 应同时支持 MCP 和 A2A 接口，以获得最大互操作性

## 来源
- [Guide to AI Agent Protocols: MCP, A2A, ACP & More - GetStream.io](https://getstream.io/blog/ai-agent-protocols/)
- [MCP vs A2A: The Complete Guide to AI Agent Protocols in 2026 - dev.to](https://dev.to/pockit_tools/mcp-vs-a2a-the-complete-guide-to-ai-agent-protocols-in-2026-30li)
- [A2A Protocol v1 2026 - Medium](https://medium.com/@richardhightower/a2a-protocol-v1-2026-how-ai-agents-actually-talk-to-each-other-c500079bca73)

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
- [ai-agent-protocol-wars-a2a-mcp](2026-05-08-ai-agent-protocol-wars-a2a-mcp.md)
- [ai-coding-agent-competition-landscape](2026-05-08-ai-coding-agent-competition-landscape.md)
- [2025年5月AI大爆发-Claude4-Qwen3-DeepSeek-R1](2026-05-09-2025年5月AI大爆发-Claude4-Qwen3-DeepSeek-R1.md)
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
