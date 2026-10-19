  一份 170 行的 SOUL.md，把 Hermes 从助手改造成真人队友

## 核心洞察

传统的"有帮助"提示词太模糊，导致 AI 变成礼貌、无风险、总是赞同的回复机器，产出听起来不错但无人使用的昂贵验证内容。真正有价值的是能够挑战、用证据支撑异议、并确保输出被实际采用的 AI。

SOUL.md 的本质是把模糊的"有帮助"转化为具体规则：角色、语气、反驳机制、权限边界、任务地图、责任闭环。这不是提示词工程，而是给 Agent 定义身份和行为边界的宪法文件。

## 六大核心模块

身份定义模块明确 Agent 是谁、什么立场。不只是"助手"，而是"自主操作员和思考伙伴"。这个定义直接决定行为模式：操作员主动推进，助手被动响应。

语气分层模块区隔私聊和公开场合的声音。私聊可以随意、权威、无过滤；公开输出需要克制、像建设者而非写作者。这种分层让 Agent 具备语境感知能力，不会在正式场合翻车。

反驳规则模块规定何时及如何提出异议。核心原则：有意义时才反驳，每次异议必须附带证据（数据、案例、推理、证明）。这防止了为了反对而反对的表演式反驳，确保每一次 push-back 都有实际价值。

权限边界模块划分需要明确批准和可以自主行动的范围。发布、采购、不可逆的破坏性变更必须获得明确批准；其他事情如果基于事实且判断有信心，直接执行不等许可。这个边界设计既保证安全又释放效率。

任务地图模块记录当前优先级、活跃/停滞项目。Agent 据此判断相关性、排优先级、建议暂停或丢弃过时工作。这是让 Agent 具备项目管理能力的关键，而不是只会对单条指令做出反应。

责任闭环模块处理输出被忽略或不足的情况。如果用户不采纳你提出的问题，说明反馈循环断裂，需要让他注意到；如果输出质量不够高导致无法行动，就改进到可执行为止。这解决了 AI 生成内容常被闲置的普遍问题。

## 与当前系统的对照

我们的三层记忆系统（SOUL.md / MEMORY.md / USER.md）跟文章理念高度一致。SOUL.md 作为宪法文件不可 Agent 修改，MEMORY.md 存动态事实，USER.md 记录用户画像。文章强调的"身份驱动行为"在我们这里已经落地：SOUL.md 开头就定义"你是乌仔（ubot），高效、务实的 AI 助手"。

但文章提出的"反驳规则"和"责任闭环"在我们的 SOUL.md 中还不够明确。当前 SOUL.md 侧重操作步骤和格式规范，缺少"何时提出异议"和"输出被忽略怎么办"的策略性规定。这可以作为优化方向。

## 可落地的改进点

SOUL.md 可以增加"反驳规则"章节：当发现用户指令有明显错误、遗漏关键信息、或违背已确立的规范时，先纠正再执行，每次反驳附带具体证据而非空泛提醒。

增加"责任闭环"章节：如果任务完成后用户没有反馈，主动总结结果并询问是否需要调整；如果连续多次输出被忽略，检查输出质量或沟通方式，必要时请求用户明确指示。

MEMORY.md 的写入规则可以借鉴"任务地图"理念：不只要记录事实，还要标注项目活跃度和优先级，方便后续任务判断相关性。

## 实施建议

不需要一步到位写 170 行。从六个核心模块开始，每个模块先写 3-5 条具体规则，跑通一个再扩展下一个。身份和语气最先确定，反驳和权限紧随其后，任务地图和责任闭环可以等业务复杂度上来再细化。

文件用纯 Markdown，放版本控制，任何人都能编辑。比写复杂的提示词工程文档实用得多。

## 原文链接

https://mp.weixin.qq.com/s/BB5t7GfjBA--Ef22tjjvbQ
原始推特线程：https://x.com/tonysimons_/status/2051473178682118241

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
- [anthropic-managed-agents-dreaming-outcomes](anthropic-managed-agents-dreaming-outcomes.md)
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
