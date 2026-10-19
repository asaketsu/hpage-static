# MCP 已死？CLI-First 策略与 Skills 模式的回归

> **来源**：Chloe Kim (Quandri Backend Engineer) · Quandri Engineering Blog · 2026-05-29
> **原文**：https://www.quandri.io/engineering-blog/mcp-is-dead
> **评分**：⭐4.5/5
> **标签**：#MCP #Agent工具 #CLI #Skills #上下文管理

## 摘要

Quandri 工程团队基于实际测量数据，论证 MCP（Model Context Protocol）存在三大核心问题：上下文窗口吞噬、运营可靠性低、与现有 CLI/API 重叠。测量显示 4 个 MCP Server 的工具定义占用 10.5% 的 200K 上下文窗口，CLI 查询同一个 Linear Issue 比 MCP 节省 65 倍 token。文章提出 CLI-First 策略和 Skills 模式作为替代方案。注意：Claude Code 已推出 Tool Search with Deferred Loading，将上下文占用降低 85%+。

## 核心内容

### 1. 上下文吞噬问题
测量数据（Quandri Stack）：

| MCP Server | 工具数 | 字符数 | Token 数 |
|-----------|--------|--------|----------|
| Linear | 42 | 51,229 | 12,807 |
| Notion | 14 | 16,156 | 4,039 |
| Slack | 12 | 15,168 | 3,792 |
| Postgres | 9 | 1,755 | 438 |
| **合计** | **77** | **84,308** | **21,077** |

200K 上下文窗口下，工具定义占 10.5%；128K (GPT-4o) 下占 16.5%。

### 2. 运营可靠性低
- 初始化失败、反复重认证
- 需要启动和维护独立进程
- 每次 Tool Call 增加外部服务器往返
- Session 中途 MCP Server 进程崩溃
- 权限不透明

性能实测：Jira MCP 比 REST API 慢 3 倍/次调用，首次调用慢 9.4 倍。

### 3. 与 CLI/API 重叠

| 方面 | CLI/API | MCP |
|------|---------|-----|
| 人机对等 | 人类和 LLM 使用相同命令 | 仅存在于 LLM 对话 |
| 可组合性 | 管道、jq、grep 自由组合 | 锁定在 Server 返回格式 |
| 调试 | 终端立即复现 | 仅在对话上下文可复现 |
| 训练数据 | 已从 man 页面和 StackOverflow 学习 | 需要单独工具定义 |
| 安装成本 | 大多已安装 | 需 Server 设置、Auth、进程管理 |

### 4. 替代方案

**CLI-First 策略**：提供 CLI → API → 文档，按优先级。LLM 已经从 man 页面和 StackOverflow 学会了 CLI 使用。

**Skills 模式**：按需加载而非全部预加载。"问图书管理员要你需要的书"而非"把所有菜单铺满桌面"。

### 5. 已有缓解措施
Claude Code 已推出 Tool Search with Deferred Loading，按需加载 MCP Tool Schema，上下文占用降低 85%+。

## 关键概念

- **Context Window Bloat**：MCP 工具定义占用大量上下文空间
- **Deferred Loading**：按需加载工具定义，减少上下文占用
- **CLI-First**：优先使用 CLI 命令，复用人类已有的工具生态
- **Skills Pattern**：按需加载知识/工具，类似"图书馆员"模式

## 能力边界

- 数据来自 Quandri 特定技术栈，其他栈的工具定义大小可能不同
- Claude Code 的 Deferred Loading 已缓解核心问题
- MCP 在标准化连接方面仍有价值（统一协议）
- 文章未充分讨论 MCP 在多 Agent 协调中的价值

## 最佳实践

- 评估每个 MCP Server 的实际使用频率，删除低频工具
- 对高频操作优先使用 CLI/API 直接调用
- 利用 Deferred Loading 减少上下文开销
- 对自定义场景考虑 Skills 模式而非 MCP Server

## 🔍 借鉴学习进化点

| # | 点 | 原文要点 | 对当前系统的借鉴 | 行动计划 |
|---|-----|---------|---------------|---------|
| 1 | 上下文预算管理 | 77 个工具定义吃掉 10.5% 上下文 | Hermes native-mcp 配置的 MCP Server 需审计工具数量和 token 开销 | 检查 ~/.hermes/config.yaml 中所有 MCP Server 的工具定义大小 |
| 2 | Deferred Loading 启发 | Claude Code 按需加载工具，减少 85% 上下文占用 | Hermes skill-auto-inject 应实现按需加载而非全量注入 | 优化 skill_auto_inject 的加载策略，仅注入相关 skill 摘要 |
| 3 | CLI-First 策略 | LLM 已学会 man 页面，CLI 更省 token | Hermes 的 terminal 工具本身就是 CLI-First 的最佳实践，应持续强化 | 确保 MCP 工具与 terminal 命令不重复配置 |
| 4 | Skills Pattern | 按需加载而非全部预加载 | Hermes Skill 系统已实现此模式（load on demand），验证其效率 | 审计当前可用 Skills 列表大小，评估对 system prompt 的影响 |
| 5 | Token 成本核算 | MCP 查询 Linear Issue 比 CLI 多 65 倍 token | 在 agent-health-check 中加入工具调用 token 成本追踪 | 为 observability-dashboard 增加工具 token 消耗指标 |

## 🔗 RAG / Wiki 联动

### 当前状态
- Hermes 使用 native-mcp 客户端连接多个 MCP Server
- Skill 系统按需加载，但 system prompt 中的 available_skills 列表较长
- agent-health-check 定期评估系统健康

### 改进方案
1. 审计 MCP 配置中的工具定义总量
2. 为 skill-auto-inject 设计摘要模式（仅加载描述，按需全量）
3. 在 observability-dashboard 增加上下文预算追踪

### 已执行操作
- ✅ 笔记已写入
- ⏳ 待审计 MCP Server 工具定义开销

## 关联笔记

[2026-05-22-Multi-Stream-LLMs-并行流解锁语言模型](2026-05-22-Multi-Stream-LLMs-并行流解锁语言模型.md)
[2026-05-23-150个任务30个Skill实测-7个反直觉结论](2026-05-23-150个任务30个Skill实测-7个反直觉结论.md)
[2026-05-22-No-Slop-Grenade-停止在对话中扔AI文字墙](2026-05-22-No-Slop-Grenade-停止在对话中扔AI文字墙.md)

## 相关笔记
- [wencai-stock-picker-notes](2026-04-06-wencai-stock-picker-notes.md)
- [OpenClaw-4-things-persistent-tasks](2026-04-10-OpenClaw-4-things-persistent-tasks.md)
- [stock-trading-discipline-washout](2026-04-11-stock-trading-discipline-washout.md)
- [通达信tdxquant量化模拟交易封装](2026-04-24-通达信tdxquant量化模拟交易封装.md)
- [LLM-Agent驱动量化交易系统前沿学习](2026-04-29-LLM-Agent驱动量化交易系统前沿学习.md)
- [stoc蒸馏-AI-Agent自学习量化交易系统](2026-04-30-stoc蒸馏-AI-Agent自学习量化交易系统.md)
- [MACD-KDJ共振策略](2026-05-08-MACD-KDJ共振策略.md)
- [蒸馏量化联合策略-QAD-LBLLM-CapacityGap](2026-05-10-蒸馏量化联合策略-QAD-LBLLM-CapacityGap.md)
- [RSI布林带组合策略](2026-05-11-RSI布林带组合策略.md)
- [板块轮动资金流向分析](2026-05-11-板块轮动资金流向分析.md)
- [技术指标组合策略-multi-indicator](2026-05-12-技术指标组合策略-multi-indicator.md)
- [板块轮动-北向资金](2026-05-14-板块轮动-北向资金.md)
- [RSI布林带组合交易策略](2026-05-15-RSI布林带组合交易策略.md)
- [板块轮动概念轮动](2026-05-18-板块轮动概念轮动.md)
- [板块轮动-主力资金-2026年5月](2026-05-20-板块轮动-主力资金-2026年5月.md)
- [MACD-KDJ-RSI-BOLL-复合量化交易策略体系与动态回测优化](2026-05-23-MACD-KDJ-RSI-BOLL-复合量化交易策略体系与动态回测优化.md)
- [MoE多模态训练-视觉语言MoE路由策略特殊挑战](2026-05-27-MoE多模态训练-视觉语言MoE路由策略特殊挑战.md)
- [MACD-KDJ共振](cyber-security/2026-05-15-MACD-KDJ共振.md)
- [rsi-bollinger-strategy](explore/2026-05-06-rsi-bollinger-strategy.md)
- [板块轮动与北向资金流向](explore/2026-05-06-板块轮动与北向资金流向.md)
- [MACD-KDJ共振策略-实战指南](explore/2026-05-09-MACD-KDJ共振策略-实战指南.md)
- [技术指标组合策略-多指标确认](explore/2026-05-09-技术指标组合策略-多指标确认.md)
- [MACD-KDJ共振策略](explore/2026-05-14-MACD-KDJ共振策略.md)
- [A股量化策略回测框架对比-backtrader-vs-vnpy-vs-自研](explore/2026-05-16-A股量化策略回测框架对比-backtrader-vs-vnpy-vs-自研.md)
- [ths-auto-trader-xdotool-stability](explore/2026-05-16-ths-auto-trader-xdotool-stability.md)
- [动态止损策略对比](explore/2026-05-17-动态止损策略对比.md)
- [北向资金主力资金流向指标有效性验证-深度研究](explore/2026-05-17-北向资金主力资金流向指标有效性验证-深度研究.md)
- [北向资金主力资金流向指标有效性验证](explore/2026-05-17-北向资金主力资金流向指标有效性验证.md)
- [实盘模拟vs真实交易技术差异](explore/2026-05-17-实盘模拟vs真实交易技术差异.md)
- [ths-auto-trader-2025-2026-tech-ecosystem-update](explore/2026-05-18-ths-auto-trader-2025-2026-tech-ecosystem-update.md)
- [VLA-AD视觉语言动作策略蒸馏](explore/2026-05-19-VLA-AD视觉语言动作策略蒸馏.md)
- [ths-auto-trader-api-era-ecosystem](explore/2026-05-19-ths-auto-trader-api-era-ecosystem.md)
- [板块轮动-北向资金](explore/2026-05-19-板块轮动-北向资金.md)
- [板块轮动-概念轮动](explore/2026-05-19-板块轮动-概念轮动.md)
- [VPO向量策略优化多样性训练提升推理搜索](explore/2026-05-23-VPO向量策略优化多样性训练提升推理搜索.md)
- [向量策略优化VPO](explore/2026-05-25-向量策略优化VPO.md)
- [easytrader-deep-dive-2026-05-17](explore/easytrader-deep-dive-2026-05-17.md)
- [ths-auto-trader-2025-2026-ecosystem-update](explore/ths-auto-trader-2025-2026-ecosystem-update.md)
- [ths-auto-trader-2026](explore/ths-auto-trader-2026.md)
- [ths-auto-trader-20260517](explore/ths-auto-trader-20260517.md)
- [ths-auto-trader-architecture-deep-dive-20260517](explore/ths-auto-trader-architecture-deep-dive-20260517.md)
- [ths-auto-trader-deep-dive](explore/ths-auto-trader-deep-dive.md)
- [ths-auto-trader-deep-learn](explore/ths-auto-trader-deep-learn.md)
- [ths-auto-trader-ecosystem-update-20260518](explore/ths-auto-trader-ecosystem-update-20260518.md)
- [ths-auto-trader-proactive-learn-7-2026-05-20](explore/ths-auto-trader-proactive-learn-7-2026-05-20.md)
- [ths-auto-trader-production-ops-20260517](explore/ths-auto-trader-production-ops-20260517.md)
- [ths-auto-trader-qmt-xtquant-tick-strategy-20260518](explore/ths-auto-trader-qmt-xtquant-tick-strategy-20260518.md)
- [ths-auto-trader-update-20260519](explore/ths-auto-trader-update-20260519.md)
- [ths-auto-trader-深度研究-2026-05-17](explore/ths-auto-trader-深度研究-2026-05-17.md)
- [ths-jqktrader-ecosystem-update-20260518](explore/ths-jqktrader-ecosystem-update-20260518.md)
- [动态止损策略深度研究-2026-05-17](explore/动态止损策略深度研究-2026-05-17.md)
- [MoE混合专家模型-路由策略-负载均衡-训练稳定性](orphan/2026-05-06-MoE混合专家模型-路由策略-负载均衡-训练稳定性.md)
- [stock-analysis-system](stock-analysis-system.md)
- [tdx-quant-trader](tdx-quant-trader.md)
- [Agent Skills才是关键抽象层](2026-04-02-Agent Skills才是关键抽象层.md)
- [MiniMax Office Skills全家桶](2026-04-02-MiniMax Office Skills全家桶.md)
- [OpenClaw-paper-review-skill](2026-04-03-OpenClaw-paper-review-skill.md)
- [SelfImproving-Agent-CLI-infra](2026-04-05-SelfImproving-Agent-CLI-infra.md)
- [SKILL-md-ai-agent-skills](2026-04-09-SKILL-md-ai-agent-skills.md)
- [distill-skill-yupi](2026-04-12-distill-skill-yupi.md)
- [AutoClaw-自进化与Skill商店](2026-04-17-AutoClaw-自进化与Skill商店.md)
- [hack-skills-给AI装上黑客大脑](2026-04-17-hack-skills-给AI装上黑客大脑.md)
- [Lima轻量级虚拟机管理工具](2026-04-22-Lima轻量级虚拟机管理工具.md)
- [歸藏PPT-Skill-电子杂志风网页演示](2026-04-24-歸藏PPT-Skill-电子杂志风网页演示.md)
- [竞品吸收_OpenCLI](2026-04-28-竞品吸收_OpenCLI.md)
- [竞品吸收笔记-khazix-skills](2026-04-29-竞品吸收笔记-khazix-skills.md)
- [SkillClaw-analysis](2026-05-02-SkillClaw-analysis.md)
- [从零构建AI-CLI方法论-ChainlessChain](2026-05-04-从零构建AI-CLI方法论-ChainlessChain.md)
- [Claude创意连接器9大工具-Blender-MCP深度解析](2026-05-05-Claude创意连接器9大工具-Blender-MCP深度解析.md)
- [github-ai-trending-mattpocock-skills](2026-05-05-github-ai-trending-mattpocock-skills.md)
- [lewislulu-html-ppt-skill-analysis](2026-05-06-lewislulu-html-ppt-skill-analysis.md)
- [addyosmani-agent-skills生产级Agent技能包](2026-05-08-addyosmani-agent-skills生产级Agent技能包.md)
- [Claude-Code工程师放弃Markdown转HTML](2026-05-09-Claude-Code工程师放弃Markdown转HTML.md)
- [OfficeCLI-AI-Agent的Office工具](2026-05-09-OfficeCLI-AI-Agent的Office工具.md)
- [Skill盈利死结与Plugin演进](2026-05-09-Skill盈利死结与Plugin演进.md)
- [skill-building-invoice-automation](2026-05-10-skill-building-invoice-automation.md)
- [softwarecopyright-skill-analysis](2026-05-10-softwarecopyright-skill-analysis.md)
- [nTop-Automate-CLI-完整测试文档](2026-05-12-nTop-Automate-CLI-完整测试文档.md)
- [中文学术去AI味10步Skill框架](2026-05-12-中文学术去AI味10步Skill框架.md)
- [30个网络抓包调试工具速查](2026-05-14-30个网络抓包调试工具速查.md)
- [HTML-Anything-Agent驱动HTML编辑器](2026-05-14-HTML-Anything-Agent驱动HTML编辑器.md)
- [SkillFactory-测试驱动Skill生成工厂](2026-05-14-SkillFactory-测试驱动Skill生成工厂.md)
- [Supertonic-闪电般本地TTS](2026-05-14-Supertonic-闪电般本地TTS.md)
- [数据目录工具全景指南](2026-05-15-数据目录工具全景指南.md)
- [开源AI模型工具2025春季爆发](2026-05-18-开源AI模型工具2025春季爆发.md)
- [机器人仿真工具选择指南](2026-05-22-机器人仿真工具选择指南.md)
- [150个任务30个Skill实测-7个反直觉结论](2026-05-23-150个任务30个Skill实测-7个反直觉结论.md)
- [AI编码工具战争-CodexClaudeCodeCursor收敛为分层架构](2026-05-24-AI编码工具战争-CodexClaudeCodeCursor收敛为分层架构.md)
- [html-ppt-skill分析融合](2026-05-24-html-ppt-skill分析融合.md)
- [CATIA-CAA-mkmk编译器Skill创建指南](2026-05-25-CATIA-CAA-mkmk编译器Skill创建指南.md)
- [agent-skills-ai-操作手册](2026-05-26-agent-skills-ai-操作手册.md)
- [Rosalind-Rust基因组学工具包-笔记本全基因组分析](2026-05-27-Rosalind-Rust基因组学工具包-笔记本全基因组分析.md)
- [taste-skill-analysis](2026-05-27-taste-skill-analysis.md)
- [darwin-skill-2-evolver-absorption](2026-05-29-darwin-skill-2-evolver-absorption.md)
- [MCP已死-上下文膨胀与CLI优先替代方案](2026-05-30-MCP已死-上下文膨胀与CLI优先替代方案.md)
- [OpenClaw核心机制Skills全解析](ai-agent/2026-04-02-OpenClaw核心机制Skills全解析.md)
- [OpenClaw-Skills-handbook](ai-agent/2026-04-07-OpenClaw-Skills-handbook.md)
- [国自然申请书AI-Skill流水线](ai-agent/2026-05-04-国自然申请书AI-Skill流水线.md)
- [build-ai-cli](ai-agent/build-ai-cli.md)
- [skills-apple](ai-agent/skills-apple.md)
- [skills-dogfood](ai-agent/skills-dogfood.md)
- [skills-email](ai-agent/skills-email.md)
- [skills-github](ai-agent/skills-github.md)
- [skills-leisure](ai-agent/skills-leisure.md)
- [skills-logo-generator-skill](ai-agent/skills-logo-generator-skill.md)
- [skills-smart-home](ai-agent/skills-smart-home.md)
- [skills-team-roles](ai-agent/skills-team-roles.md)
- [论文写作Skill工具链组合方案](cad-design/2026-05-12-论文写作Skill工具链组合方案.md)
- [CyberVerse公众号HTML模板分析](creative/2026-05-03-CyberVerse公众号HTML模板分析.md)
- [skills-social-media](cyber-security/skills-social-media.md)
- [数据血缘-lineage-工具全景](data-governance/2026-05-09-数据血缘-lineage-工具全景.md)
- [skills-catalog](data-governance/skills-catalog.md)
- [skills-data-science](data-governance/skills-data-science.md)
- [f5-tts-voice-cloning-incremental](explore/2026-05-18-f5-tts-voice-cloning-incremental.md)
- [skill-lifecycle-management-deep-dive](explore/2026-05-18-skill-lifecycle-management-deep-dive.md)
- [autotts-analysis](explore/2026-05-19-autotts-analysis.md)
- [html-anything-analysis](explore/2026-05-19-html-anything-analysis.md)
- [tts-stt-pipeline-optimization-deep-dive](explore/2026-05-19-tts-stt-pipeline-optimization-deep-dive.md)
- [Winhance-Windows11瘦身清理工具](explore/2026-05-20-Winhance-Windows11瘦身清理工具.md)
- [llm_wiki分析与Skill进化](explore/2026-05-20-llm_wiki分析与Skill进化.md)
- [哈佛机器人教育的启示-从技术工具到完整创造者](explore/2026-05-20-哈佛机器人教育的启示-从技术工具到完整创造者.md)
- [voicebox-flow-matching-tts-deep-dive](explore/2026-05-21-voicebox-flow-matching-tts-deep-dive.md)
- [the-book-of-secret-knowledge-运维安全工具百科](explore/2026-05-24-the-book-of-secret-knowledge-运维安全工具百科.md)
- [voicebox-flow-matching-next-gen-heavyweight-tts](explore/2026-05-24-voicebox-flow-matching-next-gen-heavyweight-tts.md)
- [SkillOpt-Agent技能自进化](explore/2026-05-26-SkillOpt-Agent技能自进化.md)
- [f5-tts-zero-shot-voice-cloning-deep-dive-20260518](explore/f5-tts-zero-shot-voice-cloning-deep-dive-20260518.md)
- [local-tts-stt-optimization-20260519](explore/local-tts-stt-optimization-20260519.md)
- [HTML的不合理有效性-Claude-Code-团队](hermes-agent/2026-05-16-HTML的不合理有效性-Claude-Code-团队.md)
- [frontend-slides-skill](hermes-agent/frontend-slides-skill.md)
- [hermes-skill-top10-2026w18](hermes-agent/hermes-skill-top10-2026w18.md)
- [20260512-10-skill-学术去ai味框架](orphan/20260512-10-skill-学术去ai味框架.md)
- [skills-autonomous-ai-agents](skills-autonomous-ai-agents.md)
- [skills-creative](skills-creative.md)
- [skills-devops](skills-devops.md)
- [skills-gaming](skills-gaming.md)
- [skills-mcp](skills-mcp.md)
- [skills-media](skills-media.md)
- [skills-mlops](skills-mlops.md)
- [skills-note-taking](skills-note-taking.md)
- [skills-openclaw-imports](skills-openclaw-imports.md)
- [skills-overview](skills-overview.md)
- [skills-productivity](skills-productivity.md)
- [skills-red-teaming](skills-red-teaming.md)
- [skills-research](skills-research.md)
- [skills-software-development](skills-software-development.md)
- [达尔文Skill2.0深度分析-Evolver对比吸收](达尔文Skill2.0深度分析-Evolver对比吸收.md)
