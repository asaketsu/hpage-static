# 🔧 运维管理 (DevOps)

> 本分类共 **22** 个 Skills。

[← 返回总览](skills-overview.md)

---

| # | Skill 名称 | 功能简介 |
|---|-----------|---------|
| 1 | `agent-health-check` | Agent 三维度健康自检 — 长期运行稳定性 + 工具调用效率 + 指令遵循质量。定期或按需运行，发现退化风险。 |
| 2 | `auto-dream` | Nightly system health scan and memory maintenance cron job. Scans memories, hooks, cron jobs, and generates a health report. Runs at 03:00 daily. |
| 3 | `auto-memory-keeper` | Auto-capture hourly session highlights and update daily memory files. Keeps long-term memory continuous without manual recording. Use when: user sa... |
| 4 | `cron-bulk-management` | 批量管理 cron job 的模型分配、清除、迁移。cronjob tool 的限制及绕过方法。 |
| 5 | `doc-qa` | 通用文档质量校验 — 所有文档（PPT/DOCX/XLSX/PDF/HTML）输出前的自检层。检查格式、内容、排版、一致性，确保交付质量。 |
| 6 | `evening-summary` | Nightly summary cron job — cron completion analysis, system resources, error patterns, and daily highlights. |
| 7 | `evolution-control` | 进化审批与摘要系统 — memory 写入前的质量过滤与用户审批机制，以及进化摘要查询命令。解决自进化"噪音太多"和"不可控"的问题。 |
| 8 | `evolver` | Self-evolution engine for the cat system. Analyzes error logs, identifies recurring patterns, and auto-generates fix protocols encapsulated as "gen... |
| 9 | `feishu-group-setup` | 在 Hermes Gateway 中配置飞书群组角色系统 — 多群多角色注入 |
| 10 | `free-image-generation` | Free image generation integration — Qwen Image (DashScope), Pollinations.ai, Google Gemini Image fallback chain. |
| 11 | `hermes-code-mod` | Modifying Hermes Agent core code — paths, gotchas, restart procedures. |
| 12 | `hermes-disaster-recovery` | Hermes Gateway 防灾容灾体系部署 — 进程守护、自动备份、健康检查、日志轮转、一键恢复 |
| 13 | `hermes-system-audit` | Systematic audit and optimization of a Hermes Agent installation — disk cleanup, memory verification, config validation, and feature gap analysis. |
| 14 | `memory-system` | 自研三层记忆恢复系统。解决session重启后"忘记一切"的问题，提供永久记忆、今日记忆、临时记忆的完整架构。 |
| 15 | `selective-proxy` | Inject HTTP proxy only for specific models (google/gemini-*) while keeping others direct. Config-driven, no code changes needed. |
| 16 | `self-evolver` | 自进化引擎 — 错误自动发现→修复→沉淀为规则的闭环系统 |
| 17 | `skill-optimizer` | 技能自我迭代系统。定期评估现有 skill 的效果，自动优化低效 skill，淘汰废弃 skill。确保每个 skill 都在最佳状态运行。Use when: 周度 skill 审计、skill 运行失败、用户要求优化、evolver 触发。 |
| 18 | `system-info` | 无描述 |
| 19 | `watchdog` | Monitor all OpenClaw cron jobs for failures and auto-fix common errors (model-not-allowed, timeouts). Posts to Slack only when issues are found. Ru... |
| 20 | `webhook-subscriptions` | Create and manage webhook subscriptions for event-driven agent activation. Use when the user wants external services to trigger agent runs automati... |
| 21 | `weixin-markdown-fix` | Fix WeChat black block/garbled text caused by unconverted Markdown block elements |
| 22 | `zai-quota-monitor` | 无描述 |

## 相关笔记
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
- [CyberVerse公众号HTML模板分析](orphan/2026-05-03-CyberVerse公众号HTML模板分析.md)
- [国自然申请书AI-Skill流水线](orphan/2026-05-04-国自然申请书AI-Skill流水线.md)
- [数据血缘-lineage-工具全景](orphan/2026-05-09-数据血缘-lineage-工具全景.md)
- [论文写作Skill工具链组合方案](orphan/2026-05-12-论文写作Skill工具链组合方案.md)
- [HTML的不合理有效性-Claude-Code-团队](orphan/2026-05-16-HTML的不合理有效性-Claude-Code-团队.md)
- [20260512-10-skill-学术去ai味框架](orphan/20260512-10-skill-学术去ai味框架.md)
- [build-ai-cli](orphan/build-ai-cli.md)
- [hermes-skill-top10-2026w18](orphan/hermes-skill-top10-2026w18.md)
- [skills-apple](orphan/skills-apple.md)
- [skills-catalog](orphan/skills-catalog.md)
- [skills-data-science](orphan/skills-data-science.md)
- [skills-dogfood](orphan/skills-dogfood.md)
- [skills-email](orphan/skills-email.md)
- [skills-github](orphan/skills-github.md)
- [skills-leisure](orphan/skills-leisure.md)
- [skills-logo-generator-skill](orphan/skills-logo-generator-skill.md)
- [skills-smart-home](orphan/skills-smart-home.md)
- [skills-social-media](orphan/skills-social-media.md)
- [skills-team-roles](orphan/skills-team-roles.md)
- [skills-autonomous-ai-agents](skills-autonomous-ai-agents.md)
- [skills-creative](skills-creative.md)
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
