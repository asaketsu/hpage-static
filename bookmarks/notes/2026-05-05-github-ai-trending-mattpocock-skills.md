# GitHub AI 榜单分析 & mattpocock/skills 吸收融合

> 日期：2026-05-05 | 类型：周榜分析 + 知识吸收

---

## 一、GitHub 本周 AI 榜单 Top 5

| 排名 | 项目 | 星标 | 周增量 | 定位 |
|------|------|------|--------|------|
| 🥇 | mattpocock/skills | 59k | +31k/周 | Skills for Real Engineers |
| 🥈 | TradingAgents | 67k | — | 四层 Agent 协作交易 |
| 🥉 | ruflo | 41k | — | 多 Agent 编排平台 |
| 4 | maigret | 25k | — | OSINT 信息收集 |
| 5 | awesome-codex-skills | 6.5k | — | 50+ 技能分类索引 |

---

## 二、mattpocock/skills 深度分析

### 定位

**"Skills for Real Engineers"**——不是玩具 prompt，而是解决真实工程痛点的可组合技能包。

### 解决 AI 编码四大顽疾

| 痛点 | Skill | 机制 |
|------|-------|------|
| AI 不听话，我行我素 | `grill-me` | 强制 AI 先提问再动手 |
| AI 输出太冗长 | `grill-with-docs` | 基于文档约束输出范围 |
| AI 写的代码不工作 | `tdd` + `diagnose` | 测试驱动 + 系统诊断 |
| 代码变成球意面 | `zoom-out` + `improve-architecture` | 全局视角重构 |

### 核心设计哲学

- **小而美可组合**：每个 Skill 单一职责，按需组合
- **跨模型通用**：不绑定特定 LLM，Claude/GPT/Gemini 均可用
- **来自实战 .claude 目录**：源自 Matt 多年 .claude 配置的提炼
- **一键安装器**：`npx skills@latest add` 零配置接入

---

## 三、三档吸收结果

### ① 有利进化（已落实 3 个 Skill Patch）

**systematic-debugging 增强**
- 新增 Phase 0 反馈循环：先复现再分析
- 引入 3-5 假说法：强制生成多个候选根因
- 仪表化标记：在代码中插入诊断探针

**test-driven-development 增强**
- 加入水平切片反模式警告：禁止"先写所有测试再写所有实现"
- 引入垂直 Tracer Bullet：端到端打通一个场景后再扩展

**hermes-agent-skill-authoring 增强**
- description 触发词规范：明确 skill 何时被触发
- what-to-do / supporting-info 分层：执行指令与上下文信息分离
- CONTEXT.md 领域语言：用业务词汇而非技术术语描述 skill 语境

### ② 有价值（已写 Memory）

**ruflo 多 Agent 编排平台**
- 100+ Agent 模板，Swarm 协调机制
- 自学习记忆系统 SONA：Agent 跨会话积累经验

**jcode Self-Dev 模式**
- Agent 修改自身源码 → 编译 → 测试 → 热重载
- 闭环自我进化，无需人工干预

**TradingAgents 四层协作**
- 分析师 → 研究员 → 交易员 → 风控
- 分层决策 + 独立风险评估

### ③ 知识库（只存笔记）

- **awesome-codex-skills**：50+ 技能分类体系，覆盖开发/运维/写作/分析等场景
- **maigret OSINT 模式**：用户名 → 多平台关联 → 数字足迹画像

---

## 四、榜单趋势

1. **Skill 标准化浪潮**：Top 5 中 3 个项目（skills / awesome-codex-skills / ruflo）都与 Skill/Agent 能力模块相关
2. **Agent 编排升温**：多 Agent 协作框架密集涌现，编排层成为新战场
3. **免费/开源替代需求旺盛**：用户用脚投票，商业 SaaS 的开源替代持续高星

---

## 五、预判

| 时间维度 | 趋势 |
|----------|------|
| 短期（1-3 月） | 能力模块化（Skill）成为 AI Agent 基础设施，类似 npm 之于 Node.js |
| 中期（3-6 月） | Agent 编排框架之争白热化，Swarm/DAG/层级式编排百花齐放 |
| 长期（6-12 月） | Self-Dev（Agent 自修改）成为新范式，AI 系统进入自我进化阶段 |

---

*Tags: #github-trending #ai-agent #skills #mattpocock #agent-orchestration #self-dev*

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
