# 不管用ClaudeCode，还是OpenClaw，先记住这12个知识！

📌 **元数据**
- 来源: 小蛋壳的Agent日记（公众号）
- 作者: 蛋壳
- 链接: https://mp.weixin.qq.com/s/r0eTJNAQW-YTeMzvUlRtHw
- 日期: 2026-04-15

---

## 核心观点

工具会换，底层的东西不会换。Token 怎么算、上下文怎么管、规则怎么写、技能怎么搭，这些搞明白了，换什么工具都不慌。

## 12个知识点

### 1. Agent 是什么
你把活儿丢给它，它自己去干。能改文件，能跑命令，不用你手动一步步操作。跟网页版 AI 聊天不同——以前是它给你建议，你自己动手；Agent 是直接帮你动手。

### 2. Agent 的三要素
- **模型**（脑子）— 决定聪不聪明
- **工具**（手）— 决定能干什么操作
- **上下文**（脑子里装的东西）— 决定怎么想、怎么做

真正拉开差距的是**上下文**。记忆、知识库、规则、技能，本质上都是上下文。

### 3. 窗口有上限
窗口上下文有容量限制（如 Claude 200K）。塞满了要么换新窗口，要么压缩。压缩 = 前面对话做摘要 → 细节丢失。

**关键链路：窗口装满 → 压缩 → 遗忘。**

### 4. Token 计量
- 消耗的不只是当前两条消息的 Token，是**整个窗口所有内容**的 Token
- 窗口越满，每条消息越贵
- 200KB 中文文档 ≈ 100K-200K Token，同样大小英文只需 50K 左右

### 5. 记忆靠文件，不靠脑子
窗口一压缩或一关，脑子里的东西全没了。想记住就必须**写在文件里**，下次需要时再读。自动记忆不完全靠谱，重要的事得手动让它记。

### 6. WWH 沟通原则
- **What** — 做什么
- **Why** — 为什么做（不说 Why，Agent 会按自己理解瞎猜）
- **How** — 怎么做

### 7. 上下文少即是多
聊得越多 ≠ 干活越好。上下文太多反而注意力分散。**新任务开新窗口**，清爽的脑子比熟悉你的脑子好使。

### 8. 渐进加载
启动时只加载最少的内容，需要时再读详细信息，一层一层往下。技能文件也一样——启动只读摘要，用到了才加载完整内容。

### 9. 知识管理 = 文件分类
不需要大工程，就是文本文件分好类放好目录。然后在默认上下文里告诉 Agent 什么文件放哪。不说清楚它就"随地大小便"。还可以建索引，省 Token。

### 10. 文件读写机制（冷知识）
Agent 想在文件末尾加个句号，也得**先把整个文件完整读一遍**。所以别把所有东西存一个大文件里，否则光读文件上下文就满了。

### 11. 规则设计
Agent 会偷懒、耍小聪明、走捷径。有效规则需四要素：
1. **具体要求**
2. **原因说明**
3. **反合理化条款** — 提前堵死 Agent 可能找的借口
4. **历史证据** — 证明规则有效

堵不如疏——告诉它应该怎么做、做了有什么好处，比一堆禁止管用。

### 12. Skill = 操作手册
物理结构就是一个文件夹 + 说明文档。安装就是拷贝粘贴。关键：**需要 100% 稳定的环节让 Agent 写脚本处理**，代码没有灵感没有即兴发挥，跑一万次结果一样。

## 多 Agent 协作

- **接力模式**：一个做完交给下一个。大坑——新 Agent 倾向推翻前人的工作，需保留主窗口做验收
- **Sub-Agent 模式**：主 Agent 拆活儿派临时工，用户只跟主 Agent 打交道
- **独立评审**：写代码的 Agent 不能自己审自己的代码，必须新建独立 Agent

## AI 味儿
AI 默认给统计上最安全的答案，不求有功但求无过。去味儿没捷径：犯错→反思→写规则→再犯→再改，循环往复。

大模型本质是函数映射（Y = 2X + 3 的超大号版本），看着像在想，其实是在算。遇到冷门/最新信息，必须用规则逼它先调研再回答。

## 附：系列课程清单（22篇）

**第一阶段：Agent 基础知识**
- 笔记01-09：基础概念、记忆机制、Skill、Rule、多Agent接力、Sub-Agent、多Agent档案与会议

**第二阶段：Harness 基础知识**
- 笔记11-16：养上下文、AI味儿来源、时间价值、模型选择

**第三阶段：上下文管理**
- 笔记17-21：少即是多、上下文管理、Rule设计、Skill设计、脚本封装

---

> 💡 **一句话总结**：Agent 的核心不是工具，是上下文管理。少即是多，渐进加载，文件分类，规则要堵疏结合，稳定环节靠脚本。

## 相关笔记
- [Agent Skills才是关键抽象层](../2026-04-02-Agent Skills才是关键抽象层.md)
- [Claude-Code四层记忆架构](../2026-04-03-Claude-Code四层记忆架构.md)
- [Claude-Code-324-prompts-analysis](../2026-04-04-Claude-Code-324-prompts-analysis.md)
- [Hermes-Agent-competitor-analysis](../2026-04-05-Hermes-Agent-competitor-analysis.md)
- [SelfImproving-Agent-CLI-infra](../2026-04-05-SelfImproving-Agent-CLI-infra.md)
- [spatial-intelligence-agent-action](../2026-04-05-spatial-intelligence-agent-action.md)
- [agent-loop-core-scheduling](../2026-04-07-agent-loop-core-scheduling.md)
- [email-not-revival-agent-needs-it](../2026-04-07-email-not-revival-agent-needs-it.md)
- [hermes-agent-deep-dive-evolution-roadmap](../2026-04-07-hermes-agent-deep-dive-evolution-roadmap.md)
- [claude-code-tool-execution-orchestration](../2026-04-08-claude-code-tool-execution-orchestration.md)
- [SKILL-md-ai-agent-skills](../2026-04-09-SKILL-md-ai-agent-skills.md)
- [gbrain-hybrid-search-proposal](../2026-04-11-gbrain-hybrid-search-proposal.md)
- [4-ai-agent-frameworks-comparison](../2026-04-13-4-ai-agent-frameworks-comparison.md)
- [hermes-agent-vs-openclaw](../2026-04-13-hermes-agent-vs-openclaw.md)
- [Cloudflare-EmDash-AI-Agent-CMS](../2026-04-14-Cloudflare-EmDash-AI-Agent-CMS.md)
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
- [智能教育-AI-tutoring](../explore/2026-05-05-智能教育-AI-tutoring.md)
- [ai-agent-protocol-stack-2026](../explore/2026-05-06-ai-agent-protocol-stack-2026.md)
- [ai-agent-protocol-wars-a2a-mcp](../explore/2026-05-08-ai-agent-protocol-wars-a2a-mcp.md)
- [ai-coding-agent-competition-landscape](../explore/2026-05-08-ai-coding-agent-competition-landscape.md)
- [2025年5月AI大爆发-Claude4-Qwen3-DeepSeek-R1](../explore/2026-05-09-2025年5月AI大爆发-Claude4-Qwen3-DeepSeek-R1.md)
- [ai-agent-protocols-mcp-a2a-acp](../explore/2026-05-09-ai-agent-protocols-mcp-a2a-acp.md)
- [开源AI春季爆发-模型推理Agent](../explore/2026-05-09-开源AI春季爆发-模型推理Agent.md)
- [mcp-a2a-agent-ecosystem](../explore/2026-05-10-mcp-a2a-agent-ecosystem.md)
- [ai-agent-protocols-mcp-a2a](../explore/2026-05-11-ai-agent-protocols-mcp-a2a.md)
- [AI-Agent架构-MCP-A2A协议栈](../explore/2026-05-13-AI-Agent架构-MCP-A2A协议栈.md)
- [Agentic-SOC-安全自动化的范式转变](../explore/2026-05-13-Agentic-SOC-安全自动化的范式转变.md)
- [Agentic-Engineering-从Vibe-Coding到Agent工程](../explore/2026-05-14-Agentic-Engineering-从Vibe-Coding到Agent工程.md)
- [ai-agent-architecture](../explore/2026-05-15-ai-agent-architecture.md)
- [ai开源生态-huggingface春季](../explore/2026-05-15-ai开源生态-huggingface春季.md)
- [AI-Agent-协议生态-深度整合学习](../explore/2026-05-16-AI-Agent-协议生态-深度整合学习.md)
- [Agentic-AI元年-智能体全面落地趋势](../explore/2026-05-16-Agentic-AI元年-智能体全面落地趋势.md)
- [HuggingFace-Spring2026-开源生态报告](../explore/2026-05-16-HuggingFace-Spring2026-开源生态报告.md)
- [qclaw-上下文四层模型](../explore/2026-05-16-qclaw-上下文四层模型.md)
- [具身智能-从造产品到抢落地六大趋势](../explore/2026-05-16-具身智能-从造产品到抢落地六大趋势.md)
- [竞品动态-Agentic-Engineering范式转变](../explore/2026-05-16-竞品动态-Agentic-Engineering范式转变.md)
- [agent-collaboration-self-evolution](../explore/2026-05-17-agent-collaboration-self-evolution.md)
- [具身智能2026数据规模化元年](../explore/2026-05-17-具身智能2026数据规模化元年.md)
- [hermes-agent-arxiv-search](../hermes-agent-arxiv-search.md)
- [hermes-agent-源码拆解自我进化机制](../hermes-agent-源码拆解自我进化机制.md)
- [llm-wiki-gbrain-agent-evolution_33aa818c](../llm-wiki-gbrain-agent-evolution_33aa818c.md)
- [AI幻觉案例分析-Hermes-Agent不实报道](2026-04-19-AI幻觉案例分析-Hermes-Agent不实报道.md)
- [深入源码-Hermes-Agent-Self-Improving源码拆解](2026-04-24-深入源码-Hermes-Agent-Self-Improving源码拆解.md)
- [智能教育-personalized-learning](2026-05-04-智能教育-personalized-learning.md)
- [agent-coding-playbook-analysis](2026-05-05-agent-coding-playbook-analysis.md)
- [具身智能机器人2025年终盘点](2026-05-05-具身智能机器人2025年终盘点.md)
- [具身智能机器人2025-商业化元年](2026-05-09-具身智能机器人2025-商业化元年.md)
- [claude-learning-roadmap](2026-05-10-claude-learning-roadmap.md)
- [0元打通Claude-Codex-OpenCode免费模型6入口](2026-05-11-0元打通Claude-Codex-OpenCode免费模型6入口.md)
- [HuggingFace-春季生态-Agentic-World-Modeling](2026-05-13-HuggingFace-春季生态-Agentic-World-Modeling.md)
- [具身智能量产关键年](2026-05-15-具身智能量产关键年.md)
- [HTML的不合理有效性-Claude-Code-团队](2026-05-16-HTML的不合理有效性-Claude-Code-团队.md)
- [GenericAgent](GenericAgent.md)
- [skills-autonomous-ai-agents](../skills-autonomous-ai-agents.md)
- [竞品吸收笔记_GenericAgent](../竞品吸收笔记_GenericAgent.md)
