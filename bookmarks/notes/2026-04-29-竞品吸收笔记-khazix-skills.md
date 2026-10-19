# 竞品吸收笔记：khazix-skills

> 来源：[KKKKhazix/khazix-skills](https://github.com/KKKKhazix/khazix-skills)
> 吸收日期：2026-04-29
> Stars：6.6k | License：MIT | 语言：Python

## 项目概要

数字生命卡兹克开源的 AI Skills 合集。核心思路：**不是做万能Agent，而是从几个高价值场景做极致打磨**。把个人方法论变成可安装、可移植的能力模块。

## 三个核心 Skill

### 1. hv-analysis（横纵分析法）

**一句话**：双轴研究框架——纵向追时间深度+横向追同期广度+交叉产出洞察。

方法论溯源：融合索绪尔历时-共时分析、社会科学纵向-横截面研究设计、商学院案例研究法、竞争战略分析。

核心流程：
1. 明确研究对象（产品/公司/概念/人物）
2. 联网信息收集（并行子Agent分工）
3. 纵向分析（6000-15000字叙事故事体）
4. 横向分析（3000-10000字竞品对比）
5. 横纵交汇洞察（1500-3000字精华段）
6. 生成PDF报告

关键差异化：
- 信息充分性自检（纵向故事完整？横向竞品齐全？来源可靠？）
- 不同研究对象的适配（产品/公司/概念/人物各有侧重）
- 写作风格指南（叙事驱动、节奏感、敢下判断、绝对禁区词表）

### 2. khazix-writer（公众号长文写作）

**一句话**：讲人话，像个活人。AI时代最稀缺的是"活人感"。

核心价值：
- 四层自检体系（L1硬性规则→L2风格一致性→L3内容深度→L4活人感终审）
- 文章原型分类（方法论分享型/调查实验型/现象解读型/个人观点型）
- 情绪表达技巧（"我当时就愣住了"而不是"我很震撼"）
- 绝对禁区（套话、空洞形容词、教科书开头、踩雷词、空泛工具名）
- AI味检测和消除

### 3. neat-freak（洁癖整理）

**一句话**：知识库编辑（不是记录员），审查全局、合并重复、修正过期、删除废弃。

核心价值：
- 三层知识体系（Agent记忆/项目根配置/外部docs）各自受众不同不重叠
- 变更影响矩阵（新增API→改哪些文档的映射）
- 强制自检清单（漏一个文件不行）
- 编辑原则（合并>追加、删除>保留、精确>冗长、绝对时间）

## 可借鉴模式总结

| 模式 | 我们的对应 | 吸收方式 |
|------|-----------|---------|
| 横纵分析法 | deep-analysis（通用框架） | 新建 hv-analysis skill，专用双轴方法论 |
| 去AI味写作 | humanizer（去AI痕迹） | 写作风格+禁区词表写入 deep-analysis 和 hv-analysis |
| 洁癖知识同步 | memory-system + mflow | 新建 knowledge-sync skill，增加项目级同步审查 |
| 并行子Agent搜索 | delegate_task | 已有，无需新建 |
| 质检清单模式 | doc-qa | 已有，无需新建 |

## 沉淀产出

- ✅ `research/hv-analysis` — 横纵分析法 Skill
- ✅ `devops/knowledge-sync` — 知识库同步审查 Skill
- ✅ `research/deep-analysis` — 增强：写作风格+绝对禁区
- ✅ 本笔记 — 竞品吸收记录

## 对比反思

**khazix-skills 做得好的**：
- 方法论溯源（不只说怎么做，还说为什么这么做）
- 极其具体的触发词定义（降低误触发和漏触发）
- 禁区词表（明确的反面例子比正面指导更有效）
- 信息充分性自检（搜索后验证，不是搜完就写）

**我们已有的优势**：
- deep-analysis 的交叉验证矩阵更系统化
- memory-system 三层架构更完整
- delegate_task 并行能力更强
- doc-qa 通用文档质量校验覆盖面更广

## 相关笔记
- [AutoClaw-自进化与Skill商店](2026-04-17-AutoClaw-自进化与Skill商店.md)
- [hack-skills-给AI装上黑客大脑](2026-04-17-hack-skills-给AI装上黑客大脑.md)
- [Lima轻量级虚拟机管理工具](2026-04-22-Lima轻量级虚拟机管理工具.md)
- [歸藏PPT-Skill-电子杂志风网页演示](2026-04-24-歸藏PPT-Skill-电子杂志风网页演示.md)
- [竞品吸收_OpenCLI](2026-04-28-竞品吸收_OpenCLI.md)
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
