# 这次再给Openclaw开发一个论文审稿Skill！
> **来源**：Ai4Scholar · 李孚博士 | 微信公众号
> **日期**：2026-04-03
> **标签**：OpenClaw、论文审稿、学术Skill、AI科研
> **评分**：⭐⭐⭐⭐ (4/5)

---

## 核心内容

文章介绍了 **ai4scholar-skill-hub**，一个开源的学术论文 Skill 集合，适配 OpenClaw 和腾讯 Workbuddy。包含两个 Skill：

### 1. ai4scholar-审稿助手 (paper-review)
模拟五位顶刊审稿人组成的"学术预审委员会"，五个审查维度：

| 审稿人角色 | 维度 | 职责 |
|-----------|------|------|
| Reviewer 1 | **理论贡献** | 概念定义、理论框架、创新性 |
| Reviewer 2 | **方法论** | 数据透明度、研究设计、饱和度 |
| Reviewer 3 | **文献对话** | Research Gap、引用充分性、前沿覆盖 |
| Reviewer 4 | **逻辑链条** | 论证结构、因果推理、跳跃点 |
| Editor | **主编预筛** | 标题/摘要/引言三秒判断，Desk Reject 风险 |

**三种使用模式**：
- `全面审稿` — 五维度依次审查 + 综合评分 + 修改优先级
- `针对性审查` — 单维度深度检查（如仅方法论）
- `主编预筛` — 快速判断投稿命运

**核心原则**：批评尖锐直接，禁止讨好型套话，所有批评必须指向具体段落。

### 2. ai4scholar-排版助手 (academic-writing)
覆盖四类论文排版任务：参考文献格式化、三线表生成、摘要结构润色、换投期刊适配。

---

## 💡 价值分析

### ✅ 已在做的
- 我们已有搜索/检索双层 RAG 系统，可辅助文献对话维度
- Scratch 记忆系统可积累审稿经验

### ⚠️ 可改进的
- 目前缺少专门的论文审稿 Skill，这是一个高价值的补位
- 五维度审稿框架设计精良，直接可用

### 🔥 重点行动
- **安装 paper-review Skill**：GitHub: `literaf/ai4scholar-skill-hub`
- **安装 academic-writing Skill**：同样值得集成
- **对接本地 RAG**：审稿助手 + 本地文献库 → 更精准的文献对话审查

---

*GitHub: https://github.com/literaf/ai4scholar-skill-hub*
- **相关笔记**：`bookmarks/notes/2026-04-10-dual-system-reasoning.md` - 多维度审稿框架与双系统推理的多角度验证相似

## 相关笔记
- [Agent Skills才是关键抽象层](2026-04-02-Agent Skills才是关键抽象层.md)
- [MiniMax Office Skills全家桶](2026-04-02-MiniMax Office Skills全家桶.md)
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
- [OpenClaw核心机制Skills全解析](orphan/2026-04-02-OpenClaw核心机制Skills全解析.md)
- [OpenClaw-Skills-handbook](orphan/2026-04-07-OpenClaw-Skills-handbook.md)
- [CyberVerse公众号HTML模板分析](orphan/2026-05-03-CyberVerse公众号HTML模板分析.md)
- [国自然申请书AI-Skill流水线](orphan/2026-05-04-国自然申请书AI-Skill流水线.md)
- [数据血缘-lineage-工具全景](orphan/2026-05-09-数据血缘-lineage-工具全景.md)
- [论文写作Skill工具链组合方案](orphan/2026-05-12-论文写作Skill工具链组合方案.md)
- [HTML的不合理有效性-Claude-Code-团队](orphan/2026-05-16-HTML的不合理有效性-Claude-Code-团队.md)
- [20260512-10-skill-学术去ai味框架](orphan/20260512-10-skill-学术去ai味框架.md)
- [build-ai-cli](orphan/build-ai-cli.md)
- [frontend-slides-skill](orphan/frontend-slides-skill.md)
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
