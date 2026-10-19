# GitHub 10万星！Hermes Agent 越用越聪明的秘密 — 源码深度解析

- 📅 2026-05-20
- ⭐ 4/5 — 对 Hermes 架构拆解到位，五层记忆和 Skill Loop 讲得清晰，但部分技术细节（Honcho辩证法、Atropos RL）偏营销化，缺乏源码级佐证
- 🏷️ #HermesAgent #Agent架构 #记忆系统 #Skill系统 #NousResearch
- 📰 GPUS开发者
- 🔗 https://mp.weixin.qq.com/s/bcT7hqXM1UajFtfnnm324w

## 摘要

一篇关于 Hermes Agent 的技术解析文章。核心论点：Agent 的价值不在于单次任务完成，而在于长期积累的知识和对用户的理解。文章拆解了五层记忆架构、Skill Loop 自动进化、Honcho 辩证法用户建模、MCP 异步桥接、Atropos RL 飞轮等关键设计，构建了"Agent 越用越聪明"的完整技术路径。

## 核心内容

### 1. 设计哲学

> "Agent 的价值不在于单次任务完成得多好，而在于它能记住多少、成长多快。"

目标：从"无状态问答机器"进化为"长期在线的数字员工"。运行时间越长，理解越深，能力越强。

### 2. 主循环：ReAct + 工程加固

四步流程：
1. 分析任务需求 → 拆解意图，识别工具
2. 工具调用验证 → 参数构造后先验证
3. 执行与自愈 → 失败时自动 Fallback
4. 双重迭代保护 → 防止无限循环，强制终止异常

工程基础：三种 API 模式适配（OpenAI/Anthropic/自定义），支撑 200+ 模型接入。

### 3. 五层记忆架构（核心亮点）

| 层级 | 名称 | 机制 | 作用 |
|------|------|------|------|
| L1 | 短期上下文 | 当前会话对话窗口 | 实时推理 |
| L2 | MEMORY.md | 结构化 Markdown 持久文件 | 用户偏好/项目背景，每轮注入 |
| L3 | FTS5 全文检索 | SQLite FTS5 索引 | 精准关键词召回历史对话 |
| L4 | 向量检索 | 语义相似度 | 找"意思相近"的历史 |
| L5 | LLM 自动摘要 | 长会话压缩 | 避免上下文膨胀 |

**关键洞察**：为什么不纯用向量数据库？→ 纯向量检索对精确匹配（项目名、人名、代码片段）效果差，FTS5 关键词检索补足短板。两者组合才是生产级方案。

### 4. Skill Loop：从"做过"到"精通"

闭环：做过 → 总结 → 改进 → 再用

- 复杂任务（>5次工具调用）完成后自动提炼 SKILL.md
- 渐进披露加载：Level 0（标题+描述）→ Level 1（完整内容）
- 使用中发现可优化 → skill_manage 自动更新

### 5. Honcho 用户建模：黑格尔辩证法

正题（当前画像）+ 反题（新信息）→ 合题（融合更新）

每次对话结束 → 提取观察 → 与现有画像 LLM 融合 → 下次注入系统提示

### 6. MCP 集成：异步桥接

核心矛盾：MCP 需要长生命周期异步上下文，但工具调用是同步的

解法：独立后台线程 MCPServerTask + run_coroutine_threadsafe() 桥接
- 白名单机制：只有"并行安全"的工具才同步执行
- 路径重叠检测：防止并行写冲突

### 7. Atropos RL 飞轮

每次任务执行生成标准化轨迹数据 → 训练下一代工具调用模型 → 产品-飞轮-模型协同进化

## 🔍 深度分析与自检

### 文章准确度验证（作为 Hermes 用户）

| 维度 | 文章描述 | 实际情况 | 评估 |
|------|----------|----------|------|
| 五层记忆 | L1-L5分层 | ✅ 我们实际使用 L1(MEMORY.md) + L2(short-term) + L3(topics) + FTS5(session_search) | 大致准确，我们的三级架构更精简 |
| Skill Loop | 自动提炼SKILL.md | ✅ skill_manage 工具确实存在，我们日常使用 | 准确 |
| 渐进披露 | Level 0/1 加载 | ✅ skills_list → skill_view 两步加载 | 准确 |
| 200+ 模型 | 多模型适配 | ✅ 我们用 zai/glm-5.1，支持多 provider | 准确 |
| 15+ 平台 | 消息平台接入 | ✅ 我们用飞书，确认支持多平台 | 准确 |
| Honcho 辩证法 | 用户画像自动更新 | ⚠️ 我们用 memory 工具手动/自动管理，非辩证法驱动 | 部分夸大 |
| Atropos RL | 轨迹数据收集 | ⚠️ 未见显式配置，可能在后台静默运行 | 无法确认 |
| 10万星 | GitHub Stars | 需验证 | 可能属实，增长很快 |

### 可吸收进化的设计模式

#### 1. ⭐ 记忆层级优化 — 我们的三级架构可以更好

当前：L1 MEMORY.md(4000字符) / L2 short-term(7天) / L3 topics(永久)
文章揭示的理想架构应增加：
- **FTS5 + 向量混合检索** — 我们已有 session_search(FTS5)，但缺少语义向量层
- **自动摘要压缩** — 长会话压缩，我们的 context-compressor Skill 在做类似事情

#### 2. ⭐ Skill 进化闭环强化

文章描述的闭环：做过 → 总结 → 改进 → 再用
我们已有但可以加强：
- **自动触发条件细化** — 不只是">5次工具调用"，应加上"遇到新错误并解决"、"用户纠正过方法"等触发器
- **Skill 质量评分** — 使用效果追踪，自动淘汰低效 Skill

#### 3. Honcho 辩证法 — 值得借鉴的用户画像更新方式

当前：memory 工具手动 add/replace
可进化：
- 每次会话结束自动提取"与现有画像矛盾的信息"
- 辩证融合而非简单追加
- 更精准的用户理解

#### 4. MCP 异步桥接 — 工程参考

我们的 MCP native-mcp Skill 已在使用，但异步桥接细节值得学习：
- 白名单并行安全检测
- 路径重叠检测（agent-file-conflict-detection Skill 已有雏形）

### 超越文章的思考

文章没有提到的 Hermes 真正优势：
1. **Cron 调度系统** — 让 Agent 有"时间感知"，能自主定时执行（我们的37个cron job）
2. **进化闭环** — sniff-interests → evolver → skill_manage 的自动化进化链
3. **多 Agent 协作** — delegate_task + team roles 的分工模式
4. **交换池协议** — jbot/ubot 双机经验共享
5. **小批推进法** — context window 管理的实用策略

## 🔍 借鉴点

- **"FTS5 + 向量"混合检索优于纯向量** → 我们的 session_search(FTS5) 是对的，应考虑加语义层
- **辩证法用户画像** → memory 更新从"追加式"升级为"辩证融合式"
- **Skill 自动进化触发器** → 不只看工具调用次数，还要看错误/纠正/新发现
- **产品-飞轮-模型协同** → 我们的 evolver + exchange-sync 就是这个思路的实践

## 🔗 关联性
- 关联 [agentskills.io 规范](2026-05-20-agentskills.io开放标准分析.md) — Skill 系统的渐进披露与 agentskills.io 的 progressive disclosure 一致
- 关联 [自中心数据](2026-05-20-自中心数据机器人赛道五大核心能力.md) — 五大能力中的"数据结构化"类似 Skill Loop 的"经验提炼"
- 关联 [VLA Action Head](2026-05-20-VLA原理3-机器人动作生成action-head.md) — VLA 的四类输入框架与 Hermes 的四层输入（上下文+指令+状态+历史）同构

## 💡 启发
- **"记忆"是 Agent 的核心竞争力** — 不在于单次推理能力（模型会趋同），而在于个性化积累（越用越懂你）
- **混合检索 > 单一检索** — 关键词 + 语义各有盲区，组合互补
- **辩证法思维** — 不只是 AI 领域，任何"知识更新"系统都应采用正-反-合模式，而非简单覆盖

## 🔮 预判
- Agent 记忆系统会成为下一个竞争焦点 — 2026下半年会出现更多"记忆框架"开源项目
- FTS5+向量混合检索会成为 Agent 标配 — 类似 RAG 领域的 hybrid search 趋势
- 辩证法用户建模会被更多项目采用 — 优于简单的 preference store
- Hermes 的 RL 飞轮如果真正运作，将在 6-12 个月内显著提升工具调用模型质量

## 📚 延伸阅读线索
- Honcho (Plastic Labs) — 辩证法用户建模引擎
- Atropos RL — 强化学习轨迹训练框架
- MCPServerTask — MCP 异步桥接实现

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
- [Agent元认知-LLM不确定性感知](../2026-05-18-Agent元认知-LLM不确定性感知.md)
- [SmallRustHermes-Agent自我进化三个闭环](../2026-05-18-SmallRustHermes-Agent自我进化三个闭环.md)
- [agent-memory-systems-comparison](../2026-05-18-agent-memory-systems-comparison.md)
- [具身智能机器人2025十大趋势](../2026-05-18-具身智能机器人2025十大趋势.md)
- [Qwen3.7-Agent Frontier](../2026-05-21-Qwen3.7-Agent Frontier.md)
- [react-agent-llm-agentic-training-research](../2026-05-21-react-agent-llm-agentic-training-research.md)
- [20260513-llm-wiki-obsidian-gbrain-知识自组织与自进化](../20260513-llm-wiki-obsidian-gbrain-知识自组织与自进化.md)
- [不管用ClaudeCode还是OpenClaw先记住这12个知识](../ai-agent/2026-04-15-不管用ClaudeCode还是OpenClaw先记住这12个知识.md)
- [智能教育-personalized-learning](../ai-agent/2026-05-04-智能教育-personalized-learning.md)
- [0元打通Claude-Codex-OpenCode免费模型6入口](../ai-agent/2026-05-11-0元打通Claude-Codex-OpenCode免费模型6入口.md)
- [HuggingFace-春季生态-Agentic-World-Modeling](../ai-agent/2026-05-13-HuggingFace-春季生态-Agentic-World-Modeling.md)
- [具身智能量产关键年](../ai-agent/2026-05-15-具身智能量产关键年.md)
- [anthropic-managed-agents-dreaming-outcomes](../anthropic-managed-agents-dreaming-outcomes.md)
- [智能教育-AI-tutoring](2026-05-05-智能教育-AI-tutoring.md)
- [ai-agent-protocol-stack-2026](2026-05-06-ai-agent-protocol-stack-2026.md)
- [ai-agent-protocol-wars-a2a-mcp](2026-05-08-ai-agent-protocol-wars-a2a-mcp.md)
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
- [RD-Agent-Quant-multi-agent-quant-framework-deep-dive](2026-05-18-RD-Agent-Quant-multi-agent-quant-framework-deep-dive.md)
- [agent-self-evolution-quant-trading](2026-05-18-agent-self-evolution-quant-trading.md)
- [多模态Agent框架对比2026-深度探索](2026-05-18-多模态Agent框架对比2026-深度探索.md)
- [IBM2026多智能体趋势](2026-05-19-IBM2026多智能体趋势.md)
- [agent-self-evolution-reflexion-metacognition](2026-05-19-agent-self-evolution-reflexion-metacognition.md)
- [AgentSelfEvolution-LearningSystem-深度探索](2026-05-20-AgentSelfEvolution-LearningSystem-深度探索.md)
- [TencentDB-Agent-Memory架构深度分析与进化建议](2026-05-20-TencentDB-Agent-Memory架构深度分析与进化建议.md)
- [Agent自我进化-Reflexion-ReAct-元认知框架](2026-05-21-Agent自我进化-Reflexion-ReAct-元认知框架.md)
- [agent-capability-boundary-detection-20260518](agent-capability-boundary-detection-20260518.md)
- [agent-drift-stability-degradation-20260518](agent-drift-stability-degradation-20260518.md)
- [agent-stability-degradation-drift-detection](agent-stability-degradation-drift-detection.md)
- [tradingagents-cn-deep-20260520](tradingagents-cn-deep-20260520.md)
- [google-a2a-protocol-multi-agent-2026-05-19](../google-a2a-protocol-multi-agent-2026-05-19.md)
- [hermes-agent-arxiv-search](../hermes-agent-arxiv-search.md)
- [hermes-agent-源码拆解自我进化机制](../hermes-agent-源码拆解自我进化机制.md)
- [AI幻觉案例分析-Hermes-Agent不实报道](../hermes-agent/2026-04-19-AI幻觉案例分析-Hermes-Agent不实报道.md)
- [深入源码-Hermes-Agent-Self-Improving源码拆解](../hermes-agent/2026-04-24-深入源码-Hermes-Agent-Self-Improving源码拆解.md)
- [agent-coding-playbook-analysis](../hermes-agent/2026-05-05-agent-coding-playbook-analysis.md)
- [具身智能机器人2025年终盘点](../hermes-agent/2026-05-05-具身智能机器人2025年终盘点.md)
- [具身智能机器人2025-商业化元年](../hermes-agent/2026-05-09-具身智能机器人2025-商业化元年.md)
- [claude-learning-roadmap](../hermes-agent/2026-05-10-claude-learning-roadmap.md)
- [HTML的不合理有效性-Claude-Code-团队](../hermes-agent/2026-05-16-HTML的不合理有效性-Claude-Code-团队.md)
- [GenericAgent](../hermes-agent/GenericAgent.md)
- [llm-wiki-gbrain-agent-evolution_33aa818c](../llm-wiki-gbrain-agent-evolution_33aa818c.md)
- [skills-autonomous-ai-agents](../skills-autonomous-ai-agents.md)
- [竞品吸收笔记_GenericAgent](../竞品吸收笔记_GenericAgent.md)
