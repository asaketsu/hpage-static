# html-ppt-skill 分析融合笔记

> **来源**：lewislulu/html-ppt-skill · GitHub · 2026-04-15
> **原文**：https://github.com/lewislulu/html-ppt-skill
> **格式**：双格式(MD + HTML) · 含借鉴进化点 · RAG/wiki联动
> **关联**：[[2026-04-17-AutoClaw-自进化与Skill商店]] [[html-slides-skill]]

## 摘要

html-ppt-skill 是一个 4.5k⭐ 的 AgentSkill，用纯静态 HTML/CSS/JS 生成专业演示文稿。核心差异化在于 Token-based 主题架构（36 主题仅需 CSS 变量覆盖）、Presenter Mode（BroadcastChannel 双窗口同步 + 逐字稿 + 计时器）、20 种 Canvas 特效、以及模板驱动工作流（15 全 deck + 31 布局）。与我们现有 html-slides（12 风格、单文件内联）互补，而非替代。

## 核心内容

### 1. Token-based 设计系统

base.css 定义约 40 个 CSS 变量（`--bg`, `--text-1`, `--accent`, `--shadow`, `--radius` 等），主题文件仅需覆盖 `:root` 块中的变量值。例如 cyberpunk-neon.css 仅 1.3KB，完全通过变量覆盖实现赛博朋克风格。添加新主题成本极低。

### 2. Presenter Mode（演讲者模式）

技术实现：
- 按 S 键弹出独立窗口，通过 BroadcastChannel 与主窗口同步
- 4 个可拖拽 magnetic cards：当前页(iframe) / 下一页(iframe) / 逐字稿 / 计时器
- iframe 预览用 `?preview=N` 参数实现像素精确渲染
- 导航时 `postMessage({type:'preview-goto', idx:N})` 实现无刷新切换
- 逐字稿规则：150-300 字/页，口语化，关键词加粗

### 3. Canvas FX 引擎

fx-runtime.js 实现：
- 自动加载 20 个 canvas 特效模块
- `data-fx` 声明式 API：`<div data-fx="knowledge-graph">...</div>`
- 生命周期管理：slide 进入时 init，离开时 stop
- 注册到全局 `window.HPX` 对象

### 4. 模板驱动工作流

- full-decks/：15 个完整 deck（pitch-deck、tech-sharing、presenter-mode-reveal 等）
- single-page/：31 个单页布局（bullets、chart-bar、kpi-grid、timeline 等）
- 原则："Always start from a template, never author from scratch"
- runtime.js 36KB，包含键盘导航、主题循环、全屏、概览、动画预览

### 5. 与 html-slides 的关键差异

| 维度 | html-slides (我们) | html-ppt-skill |
|------|-------------------|----------------|
| 输出 | 单文件内联 | 多文件外部资源 |
| 主题 | 12 风格（手写 CSS） | 36 主题（变量覆盖） |
| 演讲者模式 | ❌ | ✅ 逐字稿+计时器+双窗口 |
| Canvas 特效 | ❌ | ✅ 20 种声明式 |
| 模板库 | 无 | 15 deck + 31 布局 |
| 导航 | scroll-snap | absolute positioning |
| 适用 | 快速分享 | 正式演示/演讲 |

## 能力边界

**优势**：主题丰富、演讲者模式专业、模板成熟、声明式特效
**劣势**：多文件依赖不便传输、外部资源需联网加载字体、初始学习曲线高于单文件方案
**不适用**：需要单文件自包含的场景（邮件附件、离线查看）

## 最佳实践

1. 选主题时先看 audience → pitch-deck-vc/corporate-clean(商业)、tokyo-night/terminal-green(技术)、xiaohongshu-white(社交媒体)
2. 演讲场景必用 presenter-mode-reveal 模板，逐字稿 150-300 字/页
3. 用 `data-anim` 加入场动画，`data-fx` 加 canvas 特效
4. 所有颜色用 CSS 变量，不要硬编码

## 🔍 借鉴学习进化点

| # | 点 | 原文要点 | 对当前系统的借鉴 | 行动计划 |
|---|-----|---------|---------------|---------|
| 1 | 安装为独立 skill | AgentSkill 标准 SKILL.md 格式，4.5k⭐ | 与 html-slides 互补，正式演示场景用它 | ✅ 已安装到 skills/creative/html-ppt/ |
| 2 | Token 主题架构 | CSS 变量分离，新主题仅需 override :root | html-slides 当前手写 CSS 风格，可借鉴变量模式 | 未来 patch html-slides 增加变量支持 |
| 3 | Presenter Mode | BroadcastChannel + iframe 精确预览 | 演讲场景极有价值，用户经常做技术分享 | ✅ 安装即获得，直接可用 |
| 4 | 模板驱动 | "Always start from a template" | html-slides 从零生成，可增加模板库 | 记录为未来优化方向 |
| 5 | Canvas FX | data-fx 声明式 + 生命周期管理 | 动态视觉效果增强演示冲击力 | ✅ 安装即获得 |
| 6 | Skill 路由策略 | 两 skill 并存需路由 | html-slides 简单/单文件场景，html-ppt 专业/演讲场景 | 需在路由层区分触发条件 |

## 🔗 RAG / Wiki 联动

### 当前状态
- html-ppt-skill 已安装到 `~/.hermes/skills/creative/html-ppt/`
- html-slides 保留在 `~/.hermes/skills/creative/html-slides/`
- 两者触发关键词重叠（ppt/slides/演示）

### 改进方案
1. html-slides SKILL.md 增加路由说明：简单场景用自己，正式/演讲场景推荐 html-ppt
2. html-ppt SKILL.md 的 Install 章节更新为已安装状态

### 已执行操作
- ✅ git clone → skills/creative/html-ppt/
- ✅ SKILL.md 原样保留，agent 可直接使用
- ⏳ 路由策略待 patch html-slides

## 三问自检

1. **有无可复用方法？** ✅ Token 主题架构、Presenter Mode、Canvas FX 生命周期 → 已通过安装 skill 获得
2. **有无可优化配置？** ✅ html-slides 触发条件需增加路由区分 → 待 patch
3. **有关键事实？** ✅ html-ppt-skill 路径和定位 → 写 Memory

## 相关笔记
- [机器人仿真工具选择指南](2026-05-22-机器人仿真工具选择指南.md)
- [150个任务30个Skill实测-7个反直觉结论](2026-05-23-150个任务30个Skill实测-7个反直觉结论.md)
- [html-anything-analysis](explore/2026-05-19-html-anything-analysis.md)
- [Winhance-Windows11瘦身清理工具](explore/2026-05-20-Winhance-Windows11瘦身清理工具.md)
- [哈佛机器人教育的启示-从技术工具到完整创造者](explore/2026-05-20-哈佛机器人教育的启示-从技术工具到完整创造者.md)
- [voicebox-flow-matching-tts-deep-dive](explore/2026-05-21-voicebox-flow-matching-tts-deep-dive.md)
