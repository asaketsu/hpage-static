# Hermes Agent 四层记忆架构 — 深度分析与进化笔记

> **来源**：微信公众号文章 · Hermes Agent 记忆系统拆解 · 2026-05-22
> **原文**：https://mp.weixin.qq.com/s/_DuJNVUIFFILCHZi9vgiRA
> **格式**：双格式(MD + HTML) · 含借鉴进化点 · RAG/wiki联动
> **关联**：[[Hermes Agent]] [[memory-system]] [[neurofeedback]] [[obsidian]] [[wiki-knowledge-base]]

## 摘要

文章系统拆解了 Hermes Agent 的四层记忆架构：①内置 Markdown 记忆（MEMORY.md + USER.md）、②FTS5 会话历史搜索（state.db）、③外置记忆插件（Honcho/Mem0/Hindsight/Supermemory）、④Obsidian 知识库。每层设计都有明确的技术权衡和容量限制。核心洞察：当前系统只用了前两层，第三层未激活（provider 为空），第四层知识库虽已配置 skill 但未与外置记忆联动。文章提供了具体的配置方法和踩坑指南，有直接可执行的改进点。

## 核心内容

### 第一层：内置 Markdown 记忆

两个文件位于 ~/.hermes/memories/：
- MEMORY.md（Agent 笔记）：项目进展、环境配置、工作流偏好、踩坑记录。上限 2200 字符（默认，当前系统已扩至 4000）
- USER.md（用户画像）：角色、偏好、说话风格、工作习惯。上限 1375 字符（当前已扩至 1500）

**关键机制：冻结快照（Freeze Snapshot）**
- 会话中途写入的 memory，磁盘立刻更新但当前会话不生效
- 原因：系统提示词有缓存（prompt caching），中途改了缓存失效导致 token 成本翻倍
- 设计哲学：牺牲实时性换性能

### 第二层：FTS5 全文搜索（state.db）

- SQLite 数据库，索引所有会话（微信/飞书/Telegram/CLI）
- session_search 工具，FTS5 全文检索 + 摘要
- 局限：关键词匹配，非语义检索。"手表 App"搜不到"腕表项目"
- 与第一层互补：第一层是"一直带着的笔记本"，第二层是"随时能翻的档案室"

### 第三层：外置记忆插件

| 插件 | 核心特点 | 部署方式 | 费用 |
|------|---------|---------|------|
| Honcho | 用户动态模型，跨会话理解决策风格和思维习惯 | 云端/自部署(Docker+Ollama) | $2/百万消息，新用户$100额度 |
| Mem0 | LLM 提取语义化知识单元，向量检索 | 云端/自部署 | 免费1万写入/1千检索，付费$19/月 |
| Hindsight | 知识图谱+实体解析+多策略检索+Reflect推理 | 本地Embedded/云端 | 完全开源免费 |
| Supermemory | 多容器分区，独立保留策略+上下文围栏 | 仅云端 | 免费$5/月，付费$19/月 |

**关键限制：同一时间只能跑一个插件，切换不迁移数据。**

配置命令：
```bash
hermes memory setup    # 交互式选择
hermes memory status   # 查看状态
hermes memory off      # 关闭（内置不受影响）
```

### 第四层：Obsidian 知识库

- 不是记忆插件，是 skill
- Agent 读写 Markdown 文件，用 [[wikilink]] 互联
- 适合长期结构化知识：行业调研、竞品分析、知识体系
- 配置：OBSIDIAN_VAULT_PATH 环境变量
- 不会自动注入上下文，需主动触发

### 四层协作场景

以"HVAC AI报价工具"为例：
- 第一层：项目名称、用户角色 → memory.md
- 第二层：历史讨论细节 → state.db 检索
- 第三层：用户决策风格建模 → Honcho 自动推理
- 第四层：竞品分析、供应商数据 → Obsidian Wiki

## 能力边界

- 四层架构设计合理，但实际启用率低——大多数用户只用前两层
- session_search 的 FTS5 关键词匹配是明确的短板（非语义检索）
- 第三层插件互斥（只能选一个），切换成本高
- 第四层 Obsidian skill 不自动注入，依赖用户主动触发
- 冻结快照机制意味着紧急记忆需要等到下一轮会话才生效

## 关键概念

| 概念 | 定义 |
|------|------|
| 冻结快照 | 会话开始时加载 memory，中途写入下轮生效，当前会话不变 |
| FTS5 | SQLite 全文搜索引擎，关键词匹配，非语义 |
| 语义检索 | 基于向量嵌入的相似度搜索，"手表"能匹配"腕表" |
| 上下文围栏 | Supermemory 的机制，剥离已召回记忆防止递归污染 |
| 记忆插件互斥 | 同一时间只能激活一个第三方记忆提供者 |

## 🔍 借鉴学习进化点

| # | 点 | 原文要点 | 对当前系统的借鉴 | 行动计划 |
|---|---|---------|---------------|---------|
| 1 | 第三层记忆激活 | 当前 provider 为空，未启用任何外置记忆插件 | Hindsight 本地模式零成本，可直接启用提升语义检索能力 | 评估 Hindsight 本地部署可行性，执行 hermes memory setup → hindsight → local |
| 2 | session_search 技巧 | FTS5 默认 AND 逻辑，用 OR 扩大检索范围 | 更新 memory-system skill 的搜索指南 | patch memory-system skill，加入 FTS5 OR 搜索技巧 |
| 3 | Honcho 用户建模 | 跨会话持续更新用户画像，不只记内容还理解决策风格 | 双机共享用户画像可能提升协作一致性 | 调研 Honcho 自部署 + Ollama 方案，评估是否适合 ubot+jbot 共享 |
| 4 | Obsidian 自动注入 | 当前第四层不自动注入上下文，导致知识库利用率低 | 可设计 session-boot 时自动读取最近 wiki 笔记 | 评估在 session-boot skill 中加入 Obsidian 最近笔记预读 |
| 5 | 冻结快照认知 | 会话内写 memory 不立即生效，可能导致"写完以为生效"的误判 | 已知机制，但应在 memory-system skill 中显式标注 | patch memory-system skill 加入冻结快照说明 |
| 6 | Mem0 语义检索 | "手表App"能匹配"腕表项目"，解决 FTS5 关键词短板 | 作为 session_search 的语义补充层 | 评估 Mem0 免费额度（1万写入/月）是否够用 |

## 🔗 RAG / Wiki 联动

### 当前状态
- 第一层（MEMORY.md）：1755/4000 字符，使用率 44%
- 第一层（USER.md）：1054/1500 字符，使用率 70%
- 第二层（state.db）：存在，FTS5 正常
- 第三层：未激活（provider 为空）
- 第四层：Obsidian skill 存在但无自动注入
- Wiki KB：wiki-knowledge-base skill 已部署

### 改进方案
1. **激活第三层**：优先评估 Hindsight 本地模式（零成本、自部署门槛最低）
2. **session-boot 增强**：启动时预读 Obsidian 最近笔记摘要
3. **FTS5 搜索优化**：在 skill 中推广 OR 语法和关键词变体搜索

### 已执行操作
- ✅ 分析完成，三档分类已出
- ✅ 双格式笔记生成中
- ⏳ memory-system skill patch 待执行
- ⏳ 第三层插件评估待执行

## 三档分类决策

| 档次 | 项目 | 决策理由 |
|------|------|---------|
| ① 立刻进化 | patch memory-system skill 加入 FTS5 OR 搜索技巧和冻结快照说明 | 零成本，立刻改善搜索行为 |
| ① 立刻进化 | 笔记生成并更新 index.md | 流程闭环 |
| ② 有价值 | 评估 Hindsight 本地部署 | 需要研究配置细节和资源占用，不是一步能完成的 |
| ② 有价值 | 评估 Mem0 免费额度可行性 | 需要实测写入量 |
| ③ 知识库 | 四层架构细节、插件对比表 | 已记录在笔记中，需要时查阅 |

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
- [OpenClaw日常聊天黑化Agent-ULSPB安全研究](2026-05-22-OpenClaw日常聊天黑化Agent-ULSPB安全研究.md)
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
