# OpenClaw Skills 完整使用手册：怎么装、怎么用、怎么写

> **来源**：OpenClaw 官方公众号 | mp.weixin.qq.com/s/Od0vSc-zJgSfE6jYlJMY3Q
> **日期**：2026-04-07
> **标签**：OpenClaw、Skill、教程、技能开发
> **评分**：⭐⭐⭐（3/5）— 入门级教程，对我们有部分参考价值

---

## 核心观点

Skill 是给 AI 装工具的方式——本质是一个文件夹（含 SKILL.md + scripts/ + references/），装上什么 AI 就会什么。

## 关键要点

| 要点 | 说明 |
|------|------|
| 安装方式 | 内置（开箱即用）、ClawHub 一条命令、自己开发 |
| 核心文件 | SKILL.md（YAML frontmatter + Markdown 说明），决定触发条件和使用流程 |
| 目录结构 | scripts/ 放可执行脚本、references/ 放文档、assets/ 放模板资源 |
| Skill 优先级 | workspace > managed（ClawHub）> bundled（内置） |
| 使用方式 | 直接自然语言描述需求，AI 自动匹配 Skill |

### 推荐 Skill 清单（文章观点）

| Skill | 能干啥 | 文章建议 |
|-------|--------|----------|
| feishu-calendar | 管日历、约会议 | 必装 |
| feishu-doc | 读写飞书文档 | 必装 |
| feishu-bitable | 操作多维表格 | 必装 |
| wechat-publish-pro | 发公众号文章 | 有号必装 |
| multi-search-engine | 全网搜索17平台 | 建议装 |

### SKILL.md 写法要点

1. **description 决定触发率** — 要列出所有可能的触发词，越具体越好
2. **步骤要具体** — `调用 API` ❌ → `调用 web_fetch 访问 URL，取 JSON 的 results 字段` ✅
3. **错误处理必须写** — 不写 AI 遇异常会瞎猜
4. **多种说法都要测试** — 中英文触发词都写

---

## 💡 对我们的价值分析

### ✅ 已在做的
- 自定义 Skill 开发（已有 evolver/task-executor/bookmark-reader/scholar-assist 等）
- SKILL.md 结构规范（YAML frontmatter + Markdown 正文）
- scripts/references/assets 目录分离
- ClawHub 安装和管理

### ⚠️ 可改进的
- **description 字段不够具体** — 部分自研 Skill 的触发词覆盖不够全面，可参考文章建议扩充
- **错误处理文档化** — 部分 Skill 的错误处理只在代码里，没在 SKILL.md 正文中明确说明

### 🔥 重点行动
- 审查现有自研 Skill 的 description，补充更多触发关键词
- 在 SKILL.md 正文中补充错误处理说明块

---

## 优化自我

**对我有什么提升**：文章是入门教程，深度有限，但验证了我们的 Skill 架构设计方向正确。description 优化和错误处理文档化是可立即改进的点。

**如何实施**：
1. 本周审查 evolver/task-executor/bookmark-reader 的 description，各补 3-5 个触发词
2. 在 SKILL.md 末尾统一加 `## 错误处理` 段落

---

→ 相关：2026-04-02-skill-evaluation笔记（Skill评估决策）
→ 相关：2026-04-06-OpenClaw自主性笔记（Skill架构设计）

→ 相关：2026-04-03-OpenClaw-4.2-Flow.md
→ 相关：2026-04-05-Clawith团队版OpenClaw.md
→ 相关：2026-04-07-OpenClaw自主性与Harness循环机制.md
→ 相关：2026-04-09-SKILL.md模式-AI智能体技能.md（技能系统设计模式）

## 相关笔记
- [Agent Skills才是关键抽象层](../2026-04-02-Agent Skills才是关键抽象层.md)
- [MiniMax Office Skills全家桶](../2026-04-02-MiniMax Office Skills全家桶.md)
- [OpenClaw-paper-review-skill](../2026-04-03-OpenClaw-paper-review-skill.md)
- [SelfImproving-Agent-CLI-infra](../2026-04-05-SelfImproving-Agent-CLI-infra.md)
- [SKILL-md-ai-agent-skills](../2026-04-09-SKILL-md-ai-agent-skills.md)
- [distill-skill-yupi](../2026-04-12-distill-skill-yupi.md)
- [AutoClaw-自进化与Skill商店](../2026-04-17-AutoClaw-自进化与Skill商店.md)
- [hack-skills-给AI装上黑客大脑](../2026-04-17-hack-skills-给AI装上黑客大脑.md)
- [Lima轻量级虚拟机管理工具](../2026-04-22-Lima轻量级虚拟机管理工具.md)
- [歸藏PPT-Skill-电子杂志风网页演示](../2026-04-24-歸藏PPT-Skill-电子杂志风网页演示.md)
- [竞品吸收_OpenCLI](../2026-04-28-竞品吸收_OpenCLI.md)
- [竞品吸收笔记-khazix-skills](../2026-04-29-竞品吸收笔记-khazix-skills.md)
- [SkillClaw-analysis](../2026-05-02-SkillClaw-analysis.md)
- [从零构建AI-CLI方法论-ChainlessChain](../2026-05-04-从零构建AI-CLI方法论-ChainlessChain.md)
- [Claude创意连接器9大工具-Blender-MCP深度解析](../2026-05-05-Claude创意连接器9大工具-Blender-MCP深度解析.md)
- [github-ai-trending-mattpocock-skills](../2026-05-05-github-ai-trending-mattpocock-skills.md)
- [lewislulu-html-ppt-skill-analysis](../2026-05-06-lewislulu-html-ppt-skill-analysis.md)
- [addyosmani-agent-skills生产级Agent技能包](../2026-05-08-addyosmani-agent-skills生产级Agent技能包.md)
- [Claude-Code工程师放弃Markdown转HTML](../2026-05-09-Claude-Code工程师放弃Markdown转HTML.md)
- [OfficeCLI-AI-Agent的Office工具](../2026-05-09-OfficeCLI-AI-Agent的Office工具.md)
- [Skill盈利死结与Plugin演进](../2026-05-09-Skill盈利死结与Plugin演进.md)
- [skill-building-invoice-automation](../2026-05-10-skill-building-invoice-automation.md)
- [softwarecopyright-skill-analysis](../2026-05-10-softwarecopyright-skill-analysis.md)
- [nTop-Automate-CLI-完整测试文档](../2026-05-12-nTop-Automate-CLI-完整测试文档.md)
- [中文学术去AI味10步Skill框架](../2026-05-12-中文学术去AI味10步Skill框架.md)
- [30个网络抓包调试工具速查](../2026-05-14-30个网络抓包调试工具速查.md)
- [HTML-Anything-Agent驱动HTML编辑器](../2026-05-14-HTML-Anything-Agent驱动HTML编辑器.md)
- [SkillFactory-测试驱动Skill生成工厂](../2026-05-14-SkillFactory-测试驱动Skill生成工厂.md)
- [Supertonic-闪电般本地TTS](../2026-05-14-Supertonic-闪电般本地TTS.md)
- [数据目录工具全景指南](../2026-05-15-数据目录工具全景指南.md)
- [OpenClaw核心机制Skills全解析](2026-04-02-OpenClaw核心机制Skills全解析.md)
- [CyberVerse公众号HTML模板分析](2026-05-03-CyberVerse公众号HTML模板分析.md)
- [国自然申请书AI-Skill流水线](2026-05-04-国自然申请书AI-Skill流水线.md)
- [数据血缘-lineage-工具全景](2026-05-09-数据血缘-lineage-工具全景.md)
- [论文写作Skill工具链组合方案](2026-05-12-论文写作Skill工具链组合方案.md)
- [HTML的不合理有效性-Claude-Code-团队](2026-05-16-HTML的不合理有效性-Claude-Code-团队.md)
- [20260512-10-skill-学术去ai味框架](20260512-10-skill-学术去ai味框架.md)
- [build-ai-cli](build-ai-cli.md)
- [frontend-slides-skill](frontend-slides-skill.md)
- [hermes-skill-top10-2026w18](hermes-skill-top10-2026w18.md)
- [skills-apple](skills-apple.md)
- [skills-catalog](skills-catalog.md)
- [skills-data-science](skills-data-science.md)
- [skills-dogfood](skills-dogfood.md)
- [skills-email](skills-email.md)
- [skills-github](skills-github.md)
- [skills-leisure](skills-leisure.md)
- [skills-logo-generator-skill](skills-logo-generator-skill.md)
- [skills-smart-home](skills-smart-home.md)
- [skills-social-media](skills-social-media.md)
- [skills-team-roles](skills-team-roles.md)
- [skills-autonomous-ai-agents](../skills-autonomous-ai-agents.md)
- [skills-creative](../skills-creative.md)
- [skills-devops](../skills-devops.md)
- [skills-gaming](../skills-gaming.md)
- [skills-mcp](../skills-mcp.md)
- [skills-media](../skills-media.md)
- [skills-mlops](../skills-mlops.md)
- [skills-note-taking](../skills-note-taking.md)
- [skills-openclaw-imports](../skills-openclaw-imports.md)
- [skills-overview](../skills-overview.md)
- [skills-productivity](../skills-productivity.md)
- [skills-red-teaming](../skills-red-teaming.md)
- [skills-research](../skills-research.md)
- [skills-software-development](../skills-software-development.md)
