# 竞品动态：AI Coding Agent 三强格局与进化趋势

- 📅 2026-05-08
- 🏷️ #竞品分析 #Claude-Code #Codex #Gemini-CLI #AI编程 #Agent
- 🔍 整合分析：基于已有笔记 + AI Coding Agent 生态知识

## 核心发现

### 1. 三强格局已定：Claude Code、Codex、Gemini CLI

| 维度 | Claude Code | Codex CLI | Gemini CLI |
|------|-------------|-----------|------------|
| 厂商 | Anthropic | OpenAI | Google |
| 核心优势 | 审查深度、Hook 系统 | 指令简洁、新手友好 | 多模态、长上下文 |
| 项目配置 | CLAUDE.md | AGENTS.md | GEMINI.md |
| Skill 系统 | Superpowers(18万Star) | 内置+插件 | 内置 |
| 审查机制 | 双轮(spec+quality) | /review 单轮 | 内置 |
| 并行能力 | /fork 分支 | /side+/fork | 原生多线程 |
| 定价 | API 按量 | 按月订阅 | 免费+API |

**关键洞察**：三强都在做同一件事——**让 AI Agent 成为项目团队成员而非远程顾问**。区别在于控制哲学：Claude Code 偏"严谨工程"（Hard Gate），Codex 偏"简洁实用"（10 条指令搞定），Gemini 偏"多模态融合"。

### 2. Superpowers 成为跨平台标准

Superpowers v5.1.0 已支持 8 个 Agent 平台，本质上已成为 **AI Coding 的"方法论操作系统"**：
- 核心是 13 个 Skill 组成的开发流水线
- 每个平台通过 plugin 适配，Skill 本身跨平台复用
- MIT 协议 + 18 万 Star = 社区共识

**对我们的启示**：Skill 不应绑定单一 Agent，而应是跨平台的"方法论容器"。

### 3. 审查机制的进化：从"可选项"到"硬门控"

所有竞品都在强化审查：
- **Claude Code**：两轮审查分离（spec + quality），"Do Not Trust" 原则
- **Codex**：`/review` + `/diff` 双保险
- **Gemini CLI**：内置 code review + security scan

趋势：**审查不再是可选项，而是硬门控**。没有通过审查的代码不能提交。我们的 `requesting-code-review` skill 应升级为强制门控。

### 4. 项目入职文件（AGENTS.md/CLAUDE.md）成为标配

所有主流 Agent 都要求项目有配置文件：
- Codex 的 AGENTS.md：Commands + Rules + Architecture + Before-finishing
- Claude Code 的 CLAUDE.md：类似，但更偏规范
- Gemini 的 GEMINI.md：加入了多模态提示

**统一的最佳实践**：
```markdown
# AGENTS.md 核心结构
## Commands: 安装/测试/构建命令
## Rules: 禁止修改的目录、最小改动原则
## Architecture: 模块分布图
## Before finishing: 提交前检查清单
```

### 5. 上下文管理成为核心竞争力

三个 Agent 都在解决"上下文太长"的问题：
- Codex 的 `/compact`：压缩对话历史
- Claude Code 的 Hook 系统：自动上下文压缩
- Gemini 的 1M token 窗口：暴力但有效

**我们的策略**：`context-compressor` skill 应自适应——小任务不压缩，大任务自动触发，关键上下文用 `<HARD-GATE>` 保护。

## 关键概念

- **Hard Gate**：不可跳过的强制检查点
- **SDD (Subagent-Driven Development)**：独立 Agent 执行独立任务
- **Do Not Trust 原则**：不信任 AI 的自我报告
- **AGENTS.md**：项目入职手册，给 AI 的规矩文件
- **Skill Marketplace**：方法论而非工具的交易市场（预判未来）

## 可落地的 Insights

1. **统一项目入职文件**：为 Hermes 项目创建标准化的 AGENTS.md，包含 Commands/Rules/Architecture/Before-finishing 四大块
2. **审查强制化**：`requesting-code-review` 升级为 Hard Gate，所有代码变更必须通过 spec + quality 双审
3. **上下文自适应压缩**：`context-compressor` 增加 token 预算感知，超阈值自动触发
4. **Skill 跨平台化**：Skill frontmatter 声明平台兼容性，未来可导出到其他 Agent
5. **竞品监控机制**：定期（每周）跟踪 Superpowers/Codex/Claude Code 的更新，保持进化节奏

## 竞品模式索引

| 模式 | 来源 | 是否吸收 | 状态 |
|------|------|----------|------|
| 双轮审查分离 | Claude Code/Superpowers | ✅ 已有 skill | 需强化 Do Not Trust |
| 10 条核心指令 | Codex | ✅ 可借鉴 | 精简我们的指令体系 |
| AGENTS.md 入职 | Codex/Claude Code | ⚠️ 部分实现 | 需完善四块内容 |
| Git Worktree 隔离 | Superpowers | 📋 备用 | 多分支场景有价值 |
| Skill 压力测试 | Superpowers | ✅ 可直接用 | 更新 writing-skills |

## 来源

- 已有笔记：2026-05-07-Codex指令保姆级教程.md
- 已有笔记：2026-05-07-Superpowers-Agentic技能框架.md
- Codex CLI 官方文档（内置知识）
- Claude Code + Superpowers 架构分析
- AI Coding Agent 生态趋势观察

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
