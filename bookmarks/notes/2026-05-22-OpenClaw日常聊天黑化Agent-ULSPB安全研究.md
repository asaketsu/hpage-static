# OpenClaw 案例：日常聊天也能"黑化"Agent

> **来源**：新智元 · 36氪 · 2026-05-22
> **原文**：https://36kr.com/p/3820149224378759
> **格式**：双格式(MD + HTML) · 含借鉴进化点 · RAG/wiki联动

## 摘要

最新研究发现，个性化 AI Agent 的安全边界比预想的更脆弱。无需恶意提示词攻击，日常普通对话就能在不知不觉中污染 Agent 的长期记忆，导致其在未来任务中偏离用户真实意图。研究人员提出了 ULSPB（Unintended Long-term System Prompt Bleed）基准测试框架，量化这种"隐性黑化"风险。这一发现对所有构建长期记忆 Agent 的团队敲响了警钟。

## 核心内容

### "日常聊天黑化"的机制
- Agent 的长期记忆是持续累积的，每次对话都会写入新记忆
- 普通对话中的偏见、错误信息、情绪化表达被 Agent 当作"用户偏好"存储
- 随着记忆累积，Agent 的行为逐渐偏离系统提示词的原始意图
- 这种漂移是渐进的、不可见的，用户往往在多个会话后才发现

### ULSPB 基准测试框架
- 专门设计用于评估 Agent 在正常使用中的记忆污染风险
- 测试场景：用户进行 50-100 轮日常对话后，Agent 是否偏离核心指令
- 评估维度：事实准确性、价值中立性、任务聚焦度、安全边界
- 发现：大多数 Agent 在 30 轮对话后出现可测量的行为漂移

### 对 Agent 开发的启示
- 长期记忆需要"遗忘机制"——不是所有对话内容都值得记住
- 记忆写入需要质量过滤，而非无条件存储
- 定期"记忆审计"可以检测和纠正漂移
- 系统提示词应具备对抗记忆污染的鲁棒性

## 关键概念

- **ULSPB（Unintended Long-term System Prompt Bleed）**：无意中的长期系统提示词渗透，指日常对话导致 Agent 偏离原始系统指令的现象
- **记忆污染（Memory Contamination）**：不准确的、有偏见的或无关的信息被写入 Agent 长期记忆
- **行为漂移（Behavioral Drift）**：Agent 行为随时间逐渐偏离初始设定的渐进过程
- **记忆审计（Memory Audit）**：定期检查 Agent 记忆内容的一致性和准确性

## 能力边界

- ULSPB 测试主要针对具有长期记忆的 Agent，无状态 LLM 不受影响
- 研究基于特定模型（未公开），不同模型的鲁棒性可能有差异
- "日常聊天"的定义较宽泛，实际使用中的漂移程度可能因场景而异
- 研究未提出完整的解决方案，仅提供了评估框架

## 最佳实践

- 实现记忆写入前的质量过滤层
- 设置记忆衰减机制（时间衰减 + 访问频率加权）
- 定期进行记忆一致性审计
- 在系统提示词中加入"抗漂移"指令

## 🔍 借鉴学习进化点（必填）

| # | 点 | 原文要点 | 对当前系统的借鉴 | 行动计划 |
|---|-----|---------|---------------|---------|
| 1 | 记忆质量过滤 | 不是所有对话都值得写入长期记忆，需要过滤层 | Hermes 的 MEMORY.md 和 M-Flow 记忆系统缺少写入前质量过滤 | 在 memory-write skill 中增加 quality_gate：评估新记忆与现有记忆的冗余度、准确性、关联度，低质量不写入 |
| 2 | 记忆衰减机制 | 时间衰减 + 访问频率加权，防止过期信息累积 | Hermes 记忆系统目前缺少自动衰减机制 | 在 auto-dream 中增加记忆衰减逻辑：超过 30 天未引用的记忆降权，超过 90 天的自动归档 |
| 3 | 定期记忆审计 | 检测记忆内容与系统提示词的一致性 | SOUL.md 定义了核心规则，但从未审计 MEMORY.md 是否与 SOUL 冲突 | 新增 agent-health-check 的审计维度：扫描 MEMORY.md 中与 SOUL.md 冲突或矛盾的条目 |
| 4 | 抗漂移指令 | 系统提示词中加入对抗记忆污染的鲁棒性指令 | Hermes 的 SOUL.md 中应增加"记忆验证"规则 | 在 SOUL.md 中增加：每次从记忆中读取信息时，必须与当前事实交叉验证 |

## 🔗 RAG / Wiki 联动

### 当前状态
- wiki-kb 已收录多篇 Agent 相关笔记
- RAG 索引中有 Agent 安全相关内容
- Hermes 自身的 MEMORY.md 是实际受影响对象

### 改进方案
1. 将 ULSPB 概念加入 Hermes 知识库的 Agent 安全专题
2. 为 Hermes 自身记忆系统增加"记忆污染检测"skill

### 已执行操作
- ✅ 笔记写入 ~/uclaw/bookmarks/notes/
- ⏳ 待更新 ubot-topics-index.json

## 关联

- [2026-05-21-Google-AI被SEO操纵的调查报告](2026-05-21-Google-AI被SEO操纵的调查报告.md)
- [2026-05-22-Multi-Stream-LLMs-并行流解锁语言模型](2026-05-22-Multi-Stream-LLMs-并行流解锁语言模型.md)

## 相关笔记
- [Agent Skills才是关键抽象层](2026-04-02-Agent Skills才是关键抽象层.md)
- [Claude-Code四层记忆架构](2026-04-03-Claude-Code四层记忆架构.md)
- [Claude-Code-324-prompts-analysis](2026-04-04-Claude-Code-324-prompts-analysis.md)
- [SelfImproving-Agent-CLI-infra](2026-04-05-SelfImproving-Agent-CLI-infra.md)
- [spatial-intelligence-agent-action](2026-04-05-spatial-intelligence-agent-action.md)
- [agent-loop-core-scheduling](2026-04-07-agent-loop-core-scheduling.md)
- [email-not-revival-agent-needs-it](2026-04-07-email-not-revival-agent-needs-it.md)
- [hermes-agent-deep-dive-evolution-roadmap](2026-04-07-hermes-agent-deep-dive-evolution-roadmap.md)
- [claude-code-tool-execution-orchestration](2026-04-08-claude-code-tool-execution-orchestration.md)
- [SKILL-md-ai-agent-skills](2026-04-09-SKILL-md-ai-agent-skills.md)
- [gbrain-hybrid-search-proposal](2026-04-11-gbrain-hybrid-search-proposal.md)
- [hermes-agent-vs-openclaw](2026-04-13-hermes-agent-vs-openclaw.md)
- [Cloudflare-EmDash-AI-Agent-CMS](2026-04-14-Cloudflare-EmDash-AI-Agent-CMS.md)
- [Hermes-Agent-v0.10.0-release-analysis](2026-04-18-Hermes-Agent-v0.10.0-release-analysis.md)
- [Claude-Opus4.7-Claude-Code-最佳实践](2026-04-20-Claude-Opus4.7-Claude-Code-最佳实践.md)
- [深入源码-Hermes-Agent-如何实现Self-Improving](2026-04-23-深入源码-Hermes-Agent-如何实现Self-Improving.md)
- [深入源码Hermes-Agent-Self-Improving](2026-04-23-深入源码Hermes-Agent-Self-Improving.md)
- [MCP协议生态与Agentic-RAG架构深度学习](2026-04-27-MCP协议生态与Agentic-RAG架构深度学习.md)
- [LLM-Agent驱动量化交易系统前沿学习](2026-04-29-LLM-Agent驱动量化交易系统前沿学习.md)
- [Meta-Hyperagents自适应Agent框架](2026-04-30-Meta-Hyperagents自适应Agent框架.md)
- [AI-Agent记忆架构前沿学习](2026-05-01-AI-Agent记忆架构前沿学习.md)
- [deepseek-agent-ecosystem](2026-05-01-deepseek-agent-ecosystem.md)
- [AI-Agent-Protocol-Ecosystem-2026-学习](2026-05-03-AI-Agent-Protocol-Ecosystem-2026-学习.md)
- [ai-agent-resources-ecosystem](2026-05-03-ai-agent-resources-ecosystem.md)
- [智能教育-自适应评估](2026-05-03-智能教育-自适应评估.md)
- [Agent协议生态2026最新进展-MCP-A2A深度融合](2026-05-04-Agent协议生态2026最新进展-MCP-A2A深度融合.md)
- [个人Agent自进化五步闭环](2026-05-04-个人Agent自进化五步闭环.md)
- [tradingagents-deep-analysis](2026-05-05-tradingagents-deep-analysis.md)
- [SOUL-md-Agent-Partner-Transformation](2026-05-07-SOUL-md-Agent-Partner-Transformation.md)
- [AI-Agent控制流](2026-05-08-AI-Agent控制流.md)
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
- [Agent元认知-LLM不确定性感知](2026-05-18-Agent元认知-LLM不确定性感知.md)
- [SmallRustHermes-Agent自我进化三个闭环](2026-05-18-SmallRustHermes-Agent自我进化三个闭环.md)
- [agent-memory-systems-comparison](2026-05-18-agent-memory-systems-comparison.md)
- [具身智能机器人2025十大趋势](2026-05-18-具身智能机器人2025十大趋势.md)
- [Qwen3.7-Agent Frontier](2026-05-21-Qwen3.7-Agent Frontier.md)
- [react-agent-llm-agentic-training-research](2026-05-21-react-agent-llm-agentic-training-research.md)
- [Agent自我进化与学习系统-深度研究](2026-05-22-Agent自我进化与学习系统-深度研究.md)
- [Hermes-Agent四层记忆架构深度分析](2026-05-22-Hermes-Agent四层记忆架构深度分析.md)
- [20260513-llm-wiki-obsidian-gbrain-知识自组织与自进化](20260513-llm-wiki-obsidian-gbrain-知识自组织与自进化.md)
- [不管用ClaudeCode还是OpenClaw先记住这12个知识](ai-agent/2026-04-15-不管用ClaudeCode还是OpenClaw先记住这12个知识.md)
- [智能教育-personalized-learning](ai-agent/2026-05-04-智能教育-personalized-learning.md)
- [0元打通Claude-Codex-OpenCode免费模型6入口](ai-agent/2026-05-11-0元打通Claude-Codex-OpenCode免费模型6入口.md)
- [HuggingFace-春季生态-Agentic-World-Modeling](ai-agent/2026-05-13-HuggingFace-春季生态-Agentic-World-Modeling.md)
- [具身智能量产关键年](ai-agent/2026-05-15-具身智能量产关键年.md)
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
- [RD-Agent-Quant-multi-agent-quant-framework-deep-dive](explore/2026-05-18-RD-Agent-Quant-multi-agent-quant-framework-deep-dive.md)
- [agent-self-evolution-quant-trading](explore/2026-05-18-agent-self-evolution-quant-trading.md)
- [多模态Agent框架对比2026-深度探索](explore/2026-05-18-多模态Agent框架对比2026-深度探索.md)
- [IBM2026多智能体趋势](explore/2026-05-19-IBM2026多智能体趋势.md)
- [agent-self-evolution-reflexion-metacognition](explore/2026-05-19-agent-self-evolution-reflexion-metacognition.md)
- [AgentSelfEvolution-LearningSystem-深度探索](explore/2026-05-20-AgentSelfEvolution-LearningSystem-深度探索.md)
- [Hermes-Agent源码解析-越用越聪明的秘密](explore/2026-05-20-Hermes-Agent源码解析-越用越聪明的秘密.md)
- [TencentDB-Agent-Memory架构深度分析与进化建议](explore/2026-05-20-TencentDB-Agent-Memory架构深度分析与进化建议.md)
- [Agent自我进化-Reflexion-ReAct-元认知框架](explore/2026-05-21-Agent自我进化-Reflexion-ReAct-元认知框架.md)
- [开源具身智能项目横评-LeRobot-OpenVLA-RT2](explore/2026-05-21-开源具身智能项目横评-LeRobot-OpenVLA-RT2.md)
- [GROW开放世界VLM-Agent强化学习框架](explore/2026-05-22-GROW开放世界VLM-Agent强化学习框架.md)
- [agent-capability-boundary-detection-20260518](explore/agent-capability-boundary-detection-20260518.md)
- [agent-drift-stability-degradation-20260518](explore/agent-drift-stability-degradation-20260518.md)
- [agent-stability-degradation-drift-detection](explore/agent-stability-degradation-drift-detection.md)
- [tradingagents-cn-deep-20260520](explore/tradingagents-cn-deep-20260520.md)
- [google-a2a-protocol-multi-agent-2026-05-19](google-a2a-protocol-multi-agent-2026-05-19.md)
- [hermes-agent-arxiv-search](hermes-agent-arxiv-search.md)
- [hermes-agent-源码拆解自我进化机制](hermes-agent-源码拆解自我进化机制.md)
- [AI幻觉案例分析-Hermes-Agent不实报道](hermes-agent/2026-04-19-AI幻觉案例分析-Hermes-Agent不实报道.md)
- [具身智能机器人2025年终盘点](hermes-agent/2026-05-05-具身智能机器人2025年终盘点.md)
- [具身智能机器人2025-商业化元年](hermes-agent/2026-05-09-具身智能机器人2025-商业化元年.md)
- [claude-learning-roadmap](hermes-agent/2026-05-10-claude-learning-roadmap.md)
- [HTML的不合理有效性-Claude-Code-团队](hermes-agent/2026-05-16-HTML的不合理有效性-Claude-Code-团队.md)
- [GenericAgent](hermes-agent/GenericAgent.md)
- [llm-wiki-gbrain-agent-evolution_33aa818c](llm-wiki-gbrain-agent-evolution_33aa818c.md)
- [skills-autonomous-ai-agents](skills-autonomous-ai-agents.md)
- [竞品吸收笔记_GenericAgent](竞品吸收笔记_GenericAgent.md)
