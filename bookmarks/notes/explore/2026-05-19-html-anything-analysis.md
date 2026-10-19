# html-anything 深度分析：Agentic HTML Editor

> 日期：2026-05-19 | 团队：nexu-io (Open Design 40k Star 同团队) | License: Apache-2.0
> GitHub：https://github.com/nexu-io/html-anything | Star 3.2k | Fork 362
> 关键词：Agentic HTML Editor、Coding Agent、SKILL.md、SSE Streaming、WeChat Export

---

## 一、项目定位

**一句话**：本地 AI Agent 驱动的 HTML 编辑器 -- Agent 写 HTML，用户直接发布。

**核心理念**：
- Markdown 是草稿，HTML 才是读者真正想要的
- 用户不手写 HTML，Agent 写，用户审核+发布
- 零 API Key -- 复用已登录的 CLI 会话

**关键数据**：

| 指标 | 数值 |
|------|------|
| 支持 Coding Agent | 8 个 (Claude Code/Cursor/Codex/Gemini/Copilot/OpenCode/Qwen/Aider) |
| 内置 Skill 模板 | 75 个 |
| 输出面 (Surface) | 9 种 (magazine/deck/resume/poster/XHS/tweet/prototype/data report/Hyperframes) |
| 导出目标 | WeChat/X/Zhihu/HTML/PNG |
| 代码量 | ~15,000 行 |
| Star | 3.2k (发布数天) |

---

## 二、技术架构

### 2.1 整体架构

```
+----------------------- Browser (Next.js 16) -----------------------+
|  Editor + agent picker + template picker + sandboxed iframe       |
+----------+----------------------------------+---------------------+
           | Cmd+Enter                        |
           v                                  v
  +------------------+             +---------------------+
  | GET /api/agents  |             | POST /api/convert   |
  | scan PATH, list  |             | SSE - spawn CLI     |
  | installed CLIs   |             | pipe stdin/stdout   |
  +------------------+             +----------+----------+
                                              | spawn + stdin
                                              v
                             +-------------------------------+
                             |  本地 Coding Agent CLI        |
                             |  claude/codex/cursor-agent/   |
                             |  gemini/copilot/opencode/     |
                             |  qwen/aider                   |
                             +-------------------------------+
                                              |
                                              v
                             stdout JSON-line -> SSE event
                                              |
                                              v
                            iframe srcdoc append (实时渲染)
```

### 2.2 技术栈

| 层 | 技术 |
|----|------|
| 前端 | Next.js 16 App Router + Turbopack / React 19 / Tailwind v4 / zustand |
| Server Routes | GET /api/agents (检测) / POST /api/convert (SSE 流式生成) |
| Agent Transport | child_process.spawn / 每 CLI 一个 stdin/stdout 适配器 |
| 浏览器处理 | juice (CSS inline) / modern-screenshot (PNG) / xlsx+papaparse / DOMPurify |
| 预览沙盒 | iframe[sandbox] + srcdoc |
| 部署 | 本地 pnpm dev / Vercel (仅 Web 层，Agent 始终在本地) |

### 2.3 Agent 检测机制

启动时扫描 PATH（包括 ~/.local/bin, ~/.bun/bin, /opt/homebrew/bin, ~/.npm-global/bin），识别已安装的 CLI。每个 CLI 有一个适配器定义检测二进制、argv 构建、stdin/stdout 协议、流解析器。

**核心设计**：不自带 Agent，复用用户已有的 CLI 会话。零 API Key。

---

## 三、六大核心设计理念

### 3.1 不发 Agent，你的够用了

复用已登录的 CLI 会话 (claude login / cursor login / gemini auth)。不需要第二份 API Key。

### 3.2 Skills 是文件夹，不是插件

遵循 Claude Code 的 SKILL.md 协议：SKILL.md + assets/ + references/ + example.html。放入 next/src/lib/templates/skills/ 即自动发现。

### 3.3 硬约束阻止 AI 乱画

每个模板硬编码：
- CJK 优先字体栈 (Noto Sans/Serif SC + Inter/Manrope)
- 8px 基线网格 (所有间距/行高/字号都是 8 的倍数)
- 圆角 + 柔阴影 + 禁纯黑纯白
- 色彩对比度 >= 4.5
- 必须使用用户真实数据，禁 lorem ipsum

### 3.4 流式渲染 = 看 AI 实时画

POST /api/convert 返回 SSE。Agent stdout 解析为 JSON-line -> text delta -> SSE event -> iframe srcdoc 实时更新。随时可中断，不浪费完整生成。

### 3.5 一键导出 = 零二次排版

- WeChat MP: juice inline CSS + data-tool markers -> 粘贴即用
- X/微博/小红书: modern-screenshot 渲染 2x PNG -> ClipboardItem
- 知乎: 同上 + LaTeX 图片占位符替换
- 下载 .html / .png

### 3.6 沙盒 iframe = 安全隔离

HTML 在 sandboxed iframe 中渲染，第三方脚本可用但 cookies/localStorage 隔离。

---

## 四、75 个 Skill 模板分类

### 4.1 Web 原型 (prototype, 19 个)

通用网页/SaaS落地页/等待列表/定价页/仪表盘/文档站/博客/移动端原型/引导流/游戏化/约会/杂志海报/营销海报/编辑风格/野蛮主义/柔暖风格/长文杂志/电子指南/简历/营销邮件/线框手绘

### 4.2 演示文稿 (deck, 20 个)

Swiss International / Guizang Editorial (from op7418) / Open Slide Canvas / Magazine Web / Hermes Cyber / Replit / XHS Pastel / XHS White / XHS Post / Tech Sharing / Product Launch / Pitch / Blueprint / Presenter Mode / Course Module / Directional Key-Nav / Graphify Dark / Obsidian Claude / Safety Alert / Simple

### 4.3 视频帧 (frame/vfx/mockup, 12 个)

Liquid Hero / NYT Data Chart / Sticky-note Flowchart / Glitch Title / Cinema Light-leak / macOS Notification / Logo Outro / Motion Frames / Hyperframes / Sprite Animation / Text Cursor VFX / 3D Device Mockup

### 4.4 社交卡片 (social, 8 个)

X Post Card / Spotify Card / Reddit Card / Carousel (3-card) / XHS Card / Twitter Pull-quote / Social Dashboard / Social Matrix

### 4.5 办公文档 (office/doc, 16 个)

Kami Parchment / PM Spec / Team OKRs / Meeting Notes / Weekly Update / Kanban Board / Eng Runbook / Finance Report / Invoice / HR Onboarding / Data Report / Live Dashboard / Team Dashboard / Keynote Deck

---

## 五、SKILL.md 协议分析

每个 Skill 文件夹结构：

```
next/src/lib/templates/skills/<skill-name>/
  SKILL.md          # frontmatter (mode/scenario/surface/preview/design_system) + 正文
  example.html       # 示例输出（可在浏览器直接打开）
  assets/            # 可选：字体/图片等
  references/        # 可选：参考文档
```

Frontmatter 双轴分类：
- **mode**: prototype / deck / frame / social / office / doc
- **scenario**: design / marketing / engineering / product / finance / hr / sale / personal

这个协议直接复用自 nexu-io/open-design，与 Hermes 的 SKILL.md 完全兼容。

---

## 六、对我们最有价值的部分

### 6.1 直接可吸收

| 模式/技术 | 来源 | 适配场景 |
|-----------|------|----------|
| SKILL.md frontmatter 双轴分类 | html-anything | 我们的 Skill 体系已有类似结构 |
| Agent CLI 检测 + 适配器模式 | open-design/multica | Hermes 已有类似机制 |
| SSE 流式渲染 | html-anything | 可用于 HTML 笔记实时预览 |
| juice CSS inline + WeChat 粘贴 | mdnice | 我们的微信排版需求 |
| 8px 基线网格 + 硬约束 | huashu-design | 所有 HTML 输出的质量标准 |
| iframe sandbox 预览 | html-anything | 安全预览用户生成的 HTML |

### 6.2 可以立即借鉴的改进

1. **HTML 笔记硬约束标准化**：将 8px 基线/CJK 字体栈/对比度>=4.5/禁纯黑纯白 写入我们的 HTML 笔记 Skill
2. **一键 WeChat 导出**：juice inline CSS 路径，粘贴即用
3. **SSE 流式生成**：当前我们是一次性输出完整 HTML，可以改为流式
4. **example.html 标准**：每个 Skill 附带可独立打开的示例

### 6.3 局限性

1. **需要本地运行 Next.js**：不是纯 CLI 工具，需要 Node.js 环境
2. **依赖外部 Agent CLI**：核心能力完全依赖已安装的 Agent
3. **75 个 Skill 质量参差**：部分 Skill 可能只是 prompt 模板
4. **仅 HTML 输出**：不支持 PDF/DOCX 等格式
5. **单文件 HTML 限制**：无法生成多页应用

---

## 七、与现有工具对比

| 特性 | html-anything | Hermes (我们) |
|------|---------------|---------------|
| Agent 后端 | 8 个外部 CLI | 内置 Agent |
| Skill 协议 | SKILL.md (frontmatter) | SKILL.md (frontmatter) |
| 输出格式 | HTML/PNG | HTML/MD/PPT/DOCX/XLSX/PNG |
| WeChat 导出 | 一键粘贴 | 需要 wechat-pb 技能 |
| 流式渲染 | SSE 实时 | 批量生成 |
| 部署 | 本地/Vercel | 本地 CLI |
| 模板数 | 75 | 100+ (Skills) |
| 设计约束 | 内置硬约束 | Skill 级别约束 |

**核心差异**：html-anything 是"Agent 写 HTML 的编辑器"，我们是"Agent 就是编辑器"。他们的优势在 UI 交互和导出流程，我们的优势在端到端自动化和多格式输出。

---

## 八、总结

html-anything 是 nexu-io 团队（Open Design 40k Star）的新项目，核心理念：

> Markdown 是草稿，HTML 是最终形态。Agent 写 HTML，用户直接发布。

**三个最值得吸收的设计**：
1. **硬约束体系**：8px 基线/CJK 优先/对比度>=4.5/禁纯黑纯白/禁 lorem ipsum
2. **一键 WeChat 导出**：juice CSS inline + data-tool markers
3. **SKILL.md 双轴分类**：mode x scenario 的矩阵式组织

**一个关键洞察**：他们不造 Agent，只做"Agent 输出的最后一公里"（设计约束 + 导出流程）。这是一个聪明的定位 -- 在 Agent 生态中做最薄但最有价值的层。

---

*参考：https://github.com/nexu-io/html-anything | Apache-2.0 | 2026-05*

## 相关笔记
- [Agent Skills才是关键抽象层](../2026-04-02-Agent Skills才是关键抽象层.md)
- [MiniMax Office Skills全家桶](../2026-04-02-MiniMax Office Skills全家桶.md)
- [OpenClaw-paper-review-skill](../2026-04-03-OpenClaw-paper-review-skill.md)
- [SelfImproving-Agent-CLI-infra](../2026-04-05-SelfImproving-Agent-CLI-infra.md)
- [SKILL-md-ai-agent-skills](../2026-04-09-SKILL-md-ai-agent-skills.md)
- [distill-skill-yupi](../2026-04-12-distill-skill-yupi.md)
- [歸藏PPT-Skill-电子杂志风网页演示](../2026-04-24-歸藏PPT-Skill-电子杂志风网页演示.md)
- [竞品吸收_OpenCLI](../2026-04-28-竞品吸收_OpenCLI.md)
- [竞品吸收笔记-khazix-skills](../2026-04-29-竞品吸收笔记-khazix-skills.md)
- [SkillClaw-analysis](../2026-05-02-SkillClaw-analysis.md)
- [github-ai-trending-mattpocock-skills](../2026-05-05-github-ai-trending-mattpocock-skills.md)
- [lewislulu-html-ppt-skill-analysis](../2026-05-06-lewislulu-html-ppt-skill-analysis.md)
- [skill-building-invoice-automation](../2026-05-10-skill-building-invoice-automation.md)
- [softwarecopyright-skill-analysis](../2026-05-10-softwarecopyright-skill-analysis.md)
- [开源AI模型工具2025春季爆发](../2026-05-18-开源AI模型工具2025春季爆发.md)
- [机器人仿真工具选择指南](../2026-05-22-机器人仿真工具选择指南.md)
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
- [CyberVerse公众号HTML模板分析](../creative/2026-05-03-CyberVerse公众号HTML模板分析.md)
- [skills-social-media](../cyber-security/skills-social-media.md)
- [数据血缘-lineage-工具全景](../data-governance/2026-05-09-数据血缘-lineage-工具全景.md)
- [skills-catalog](../data-governance/skills-catalog.md)
- [skills-data-science](../data-governance/skills-data-science.md)
- [f5-tts-voice-cloning-incremental](2026-05-18-f5-tts-voice-cloning-incremental.md)
- [skill-lifecycle-management-deep-dive](2026-05-18-skill-lifecycle-management-deep-dive.md)
- [autotts-analysis](2026-05-19-autotts-analysis.md)
- [tts-stt-pipeline-optimization-deep-dive](2026-05-19-tts-stt-pipeline-optimization-deep-dive.md)
- [Winhance-Windows11瘦身清理工具](2026-05-20-Winhance-Windows11瘦身清理工具.md)
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
