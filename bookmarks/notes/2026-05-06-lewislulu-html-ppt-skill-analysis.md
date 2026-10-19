---
title: lewislulu/html-ppt-skill 项目分析
date: 2026-05-06
source: https://github.com/lewislulu/html-ppt-skill
tags: [竞品分析, HTML PPT, AgentSkill, 演示文稿]
---

## 项目画像

| 属性 | 值 |
|------|-----|
| 仓库 | lewislulu/html-ppt-skill |
| Stars | 2,774 |
| Forks | 281 |
| 语言 | HTML (静态资源) |
| 创建时间 | 2026-04-15 |
| 最后更新 | 2026-05-06 |
| 开源协议 | MIT |
| 定位 | AgentSkill — 面向 AI Agent 的专业 HTML 演示文稿生成工具 |

**一句话总结**：世界级的 HTML PPT Studio，纯静态 HTML/CSS/JS，零构建步骤，专为 AI Agent 设计，36 主题 × 15 全 deck 模板 × 31 布局 × 47 动画（27 CSS + 20 Canvas FX），内置真·演讲者模式。

## 核心架构

**工作流**：用户请求 → Agent 加载 html-ppt Skill → 根据内容选择模板/主题/布局 → 生成单文件 HTML deck → 可选 Headless Chrome 导出 PNG。

**模块划分**：
| 模块 | 路径 | 说明 |
|------|------|------|
| 主题系统 | `assets/themes/*.css` (36个) | 从 minimal-white 到 cyberpunk-neon，含小红书专用 xiaohongshu-white |
| 布局库 | `templates/single-page/*.html` (31个) | 单页布局模板，带真实 demo 数据 |
| 全 deck 模板 | `templates/full-decks/` (15个) | 完整多页演示文稿，含真实场景脚手架 |
| 动画系统 | `assets/animations/` | 27 种 CSS 动画 + 20 种 Canvas FX（粒子、烟花、矩阵雨等） |
| 运行时 | `assets/runtime.js` | 键盘导航、主题切换、演讲者模式弹出 |
| FX 运行时 | `assets/animations/fx-runtime.js` | Canvas FX 自动初始化与清理 |
| 演讲者模式 | 内置 S 键触发 | 4 个磁性卡片（当前页/下一页/逐字稿/计时器），iframe 像素级预览，postMessage 无刷新导航 |
| Skill 定义 | `SKILL.md` | AgentSkill 标准格式，含触发词、使用指南、演讲者模式写作规范 |

**技术栈评价**：纯静态，无构建工具，无 npm 依赖（仅 CDN webfonts）。运行时轻量，核心是 `runtime.js` 的键盘/消息机制。Canvas FX 用原生 JS，无第三方库。

## 亮点与不足

### 亮点 ✅
1. **演讲者模式设计极佳** — 4 卡片磁性布局、像素级 iframe 预览、postMessage 无刷新同步、BroadcastChannel 双窗口通信。这是目前见到的最完整的 Agent-generated PPT 演讲支持。
2. **主题覆盖全面** — 36 主题，从学术到赛博朋克，含小红书专用主题，场景覆盖完整。
3. **动画系统分层** — CSS 动画（简单轻量）+ Canvas FX（视觉冲击），共 47 种，通过 `data-anim` / `data-fx` 属性声明式使用。
4. **AgentSkill 设计专业** — SKILL.md 包含清晰的触发词、三问引导（内容/风格/起点）、逐字稿写作三原则，引导 Agent 不盲目生成。
5. **零依赖零构建** — 单 HTML 文件，内联或外链 CSS/JS，任何环境可打开。
6. **Headless Chrome 渲染脚本** — 提供 PNG 导出能力，适合自动化截图。

### 不足 ⚠️
1. **无响应式断点细节** — 相比我们的 html-slides skill 的 `clamp()` + 多高度断点体系，它的响应式处理较简单（主要靠 viewport 单位）。🔴 中等严重性（大屏/小屏可能溢出）。
2. **无内容密度限制** — 未规定每页最大内容量，Agent 可能生成过于拥挤的幻灯片。🟡 低严重性（可通过 Skill 引导缓解）。
3. **无反 AI Slop 字体禁令** — 仍可能生成 Arial/Inter 默认字体页面。🟡 低严重性（主题 CSS 已定义字体，但 Agent 可能不遵守）。
4. **Canvas FX 可能性能开销** — 20 种 FX 全加载，低端设备可能卡顿。🟡 低严重性。
5. **无在线编辑能力** — 纯静态，不支持浏览器内编辑文字（我们的 html-slides 可选支持）。🟡 低严重性。

## 可借鉴模式

| 模式 | 说明 | 新颖性 | 可移植性 | 优先级 |
|------|------|--------|----------|--------|
| 演讲者模式磁性卡片 | 4 卡片可拖拽/缩放，iframe 像素级预览，postMessage 通信 | 高（我们系统缺失） | 高（可独立实现） | ⭐⭐⭐⭐⭐ |
| 逐字稿写作三原则 | 提示信号非讲稿、150-300字/页、口语化 | 中（我们已有类似理念但未成文） | 高（直接融入 Skill） | ⭐⭐⭐⭐ |
| AgentSkill 三问引导 | 内容/风格/起点，先确认再生成 | 中（我们 html-slides 有类似但不够系统） | 高 | ⭐⭐⭐⭐ |
| Canvas FX 动画库 | 20 种声明式 Canvas 特效，data-fx 属性驱动 | 高（我们缺失） | 中（需适配我们的运行时） | ⭐⭐⭐ |
| 主题×布局×动画组合矩阵 | 36×31×47 的组合空间，通过参数选择 | 低（我们已有类似） | 高 | ⭐⭐ |
| Headless Chrome 渲染脚本 | 自动化 PNG 导出 | 中（我们可加） | 高 | ⭐⭐⭐ |

## 与我们关联

### 直接关联
- 我们已有 **html-slides** skill（零依赖单文件 HTML 演示文稿）。两者定位高度重叠，但设计哲学不同：
  - **html-ppt-skill**：面向 AgentSkill 生态，强调主题/模板/动画的组合，演讲者模式是杀手功能。
  - **html-slides**：强调响应式断点、内容密度限制、反 AI Slop 字体，无演讲者模式。

### 可借鉴（应落实）
1. **演讲者模式** → 可融入 html-slides skill，增加 S 键弹出磁性卡片+逐字稿支持。
2. **逐字稿写作规范** → 融入 html-slides 的演讲场景指南。
3. **AgentSkill 三问引导** → 强化 html-slides 的 Phase 0 引导流程。

### 不应借鉴
- Canvas FX 动画库（我们可优先用 CSS 动画，保持轻量）。
- 部分主题设计（我们已有自己的风格预设）。

## 竞品定位

| 维度 | html-ppt-skill | html-slides (我们) |
|------|---------------|-------------------|
| 目标用户 | AI Agent (AgentSkill 生态) | 通用 AI Agent (Hermes) |
| 演讲者模式 | ✅ 完整实现 | ❌ 缺失 |
| 响应式体系 | ⚠️ 简单 viewport | ✅ 完整 clamp() + 断点 |
| 内容密度控制 | ❌ 无 | ✅ 有 |
| 反 AI Slop | ❌ 无明确禁令 | ✅ 明确禁忌清单 |
| 动画数量 | ✅ 47 种 | ⚠️ 基础 CSS 动画 |
| 零依赖 | ✅ 是 | ✅ 是 |
| 在线编辑 | ❌ 无 | ⚠️ 可选 |

**市场交叉点**：两者都是 AI Agent 生成 HTML PPT 的工具，但 html-ppt-skill 在演讲场景功能更强，html-slides 在响应式/内容规范上更严谨。

**竞争壁垒**：html-ppt-skill 的演讲者模式+逐字稿是独特优势，短期内难以复制；我们的优势是工程化规范（响应式、密度控制、反 Slop）。

## 预判

- **短期（1-2 周）**：我们可以将演讲者模式融入 html-slides，增强演讲场景竞争力。
- **中期（1-2 月）**：若用户频繁要求“带逐字稿的 PPT”，演讲者模式将成为标配功能。
- **长期**：HTML PPT 工具将向“演讲全流程支持”（提词器、计时、观众视图）演进，类似幻灯片软件的 Presenter Display。

## 三档借鉴点处理

### ① 有利进化（立即落实）
1. **演讲者模式** → 更新 html-slides skill，增加 S 键弹出磁性卡片（当前页/下一页/逐字稿/计时器），使用 iframe + postMessage 实现像素级预览。
   - 理由：我们系统缺此能力，能立即提升演讲场景质量。
   - 行动：patch html-slides SKILL.md，增加 Phase 2.5: 演讲者模式设计。
2. **逐字稿写作三原则** → 融入 html-slides 的演讲场景指南，作为新增章节。
   - 理由：已有理念但未成文，系统化后可提升 Agent 输出质量。
   - 行动：在 html-slides SKILL.md 中增加“演讲与逐字稿”章节。

### ② 有价值备用（记录 Memory）
- Canvas FX 动画库（20 种）— 未来若用户需要视觉冲击型动画时可快速引入。
- Headless Chrome 渲染脚本 — 未来若需要自动化截图/PNG 导出时可参考。

### ③ 其它（只记笔记）
- 主题×布局×动画组合矩阵思路（已记录于本文）。
- AgentSkill 三问引导（已通过更新 html-slides 落实，不单独记录）。

## 闭环沉淀

- ✅ 双格式笔记：`2026-05-06-lewislulu-html-ppt-skill-analysis.md` + `.html`
- ✅ Memory 更新：见②档内容
- ✅ 关联笔记：`[[html-slides]]` `[[AgentSkill设计模式]]`
- ✅ INDEX 更新：待 patch `~/uclaw/bookmarks/notes/INDEX.md`

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
