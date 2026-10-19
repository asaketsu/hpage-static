# Winhance — Windows 11 一键瘦身清理工具

- 📅 2026-05-20
- ⭐ 4/5 — 实用开源工具，WinUI 3 界面，一键清理+隐私优化+配置导入导出
- 🏷️ #Windows #系统优化 #开源工具 #隐私 #WinGet
- 📰 开源日记（微信公众号）
- 🔗 https://mp.weixin.qq.com/s/XM51Py7d_A-BljGH5GhXdA
- 📦 https://github.com/memstechtips/Winhance

## 摘要

Winhance 是一款 Windows 11 系统清理优化开源工具（v5.0.0，6.7K⭐），由开发者 Marco du Plessis 创建。使用 WinUI 3 重写界面，与 Windows 11 设置风格一致。核心功能：一键移除预装应用（Edge/OneDrive/Copilot/Recall）、隐私与性能优化集中管理、配置文件导入导出换机无忧。

## 核心内容

### 1. 软件管理 — 一键移除/批量安装

| 功能 | 说明 |
|------|------|
| 移除内置应用 | Edge、OneDrive、Copilot、Recall 等 |
| 移除遗留组件 | Legacy Capabilities、Optional Features |
| 批量安装 | 通过 WinGet 一次装完浏览器/播放器等 |

### 2. 隐私与性能优化（Optimize 模块）

- UAC 通知级别调节
- 隐私数据收集开关
- 游戏性能优化
- 电源计划选择
- 更新策略控制
- 所有设置集中到一个界面，开关式操作，无需改注册表

### 3. 配置导入导出

- 导出当前设置 → 配置文件
- 换机/重装系统 → 导入配置一步到位
- 官方推荐配置可直接套用

### 4. 安装方式

```powershell
irm "https://get.winhance.net" | iex
```

- 包含安装版 + 便携版
- 操作前自动创建系统还原点
- ⚠️ 注意仿冒版本，务必从官方 GitHub 或 winhance.net 下载

## 🔍 借鉴点

- **WinUI 3 原生体验** → 开发桌面工具时优先用系统原生 UI 框架，降低学习成本
- **配置文件导入导出** → 任何工具类软件都应支持配置迁移，提升用户留存
- **一键 PowerShell 安装** → `irm url | iex` 模式值得所有开源工具学习

## 💡 启发

- Jetson/Windows 混合架构中，Windows 端的 easytrader 执行机可用 Winhance 瘦身，减少后台干扰
- 隐私优化模块的思路可借鉴到 Linux 端的 Jetson 系统精简

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
- [开源AI模型工具2025春季爆发](../2026-05-18-开源AI模型工具2025春季爆发.md)
- [OpenClaw核心机制Skills全解析](../ai-agent/2026-04-02-OpenClaw核心机制Skills全解析.md)
- [OpenClaw-Skills-handbook](../ai-agent/2026-04-07-OpenClaw-Skills-handbook.md)
- [国自然申请书AI-Skill流水线](../ai-agent/2026-05-04-国自然申请书AI-Skill流水线.md)
- [build-ai-cli](../ai-agent/build-ai-cli.md)
- [skills-apple](../ai-agent/skills-apple.md)
- [skills-dogfood](../ai-agent/skills-dogfood.md)
- [skills-email](../ai-agent/skills-email.md)
- [skills-github](../ai-agent/skills-github.md)
- [skills-leisure](../ai-agent/skills-leisure.md)
- [skills-logo-generator-skill](../ai-agent/skills-logo-generator-skill.md)
- [skills-smart-home](../ai-agent/skills-smart-home.md)
- [skills-team-roles](../ai-agent/skills-team-roles.md)
- [论文写作Skill工具链组合方案](../cad-design/2026-05-12-论文写作Skill工具链组合方案.md)
- [CyberVerse公众号HTML模板分析](../creative/2026-05-03-CyberVerse公众号HTML模板分析.md)
- [skills-social-media](../cyber-security/skills-social-media.md)
- [数据血缘-lineage-工具全景](../data-governance/2026-05-09-数据血缘-lineage-工具全景.md)
- [skills-catalog](../data-governance/skills-catalog.md)
- [skills-data-science](../data-governance/skills-data-science.md)
- [f5-tts-voice-cloning-incremental](2026-05-18-f5-tts-voice-cloning-incremental.md)
- [skill-lifecycle-management-deep-dive](2026-05-18-skill-lifecycle-management-deep-dive.md)
- [autotts-analysis](2026-05-19-autotts-analysis.md)
- [tts-stt-pipeline-optimization-deep-dive](2026-05-19-tts-stt-pipeline-optimization-deep-dive.md)
- [llm_wiki分析与Skill进化](2026-05-20-llm_wiki分析与Skill进化.md)
- [哈佛机器人教育的启示-从技术工具到完整创造者](2026-05-20-哈佛机器人教育的启示-从技术工具到完整创造者.md)
- [voicebox-flow-matching-tts-deep-dive](2026-05-21-voicebox-flow-matching-tts-deep-dive.md)
- [f5-tts-zero-shot-voice-cloning-deep-dive-20260518](f5-tts-zero-shot-voice-cloning-deep-dive-20260518.md)
- [local-tts-stt-optimization-20260519](local-tts-stt-optimization-20260519.md)
- [HTML的不合理有效性-Claude-Code-团队](../hermes-agent/2026-05-16-HTML的不合理有效性-Claude-Code-团队.md)
- [frontend-slides-skill](../hermes-agent/frontend-slides-skill.md)
- [hermes-skill-top10-2026w18](../hermes-agent/hermes-skill-top10-2026w18.md)
- [20260512-10-skill-学术去ai味框架](../orphan/20260512-10-skill-学术去ai味框架.md)
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
