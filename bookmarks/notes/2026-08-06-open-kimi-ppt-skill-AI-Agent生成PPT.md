# open-kimi-ppt-skill — 逆向 Kimi Slides 的 AI Agent PPT 生成技能

> **来源**：[github.com/Binaryify/open-kimi-ppt-skill](https://github.com/Binaryify/open-kimi-ppt-skill)
> **License**：MIT
> **Stars**：37 · **Forks**：19
> **语言**：Node.js（需要 Node.js ≥18）
> **npm 包**：`open-kimi-ppt-skill`
> **作者**：Binaryify

---

## 一句话定义

> 逆向 Kimi Slides 实现的非官方 AI Agent PPT 生成技能——让任意兼容 SKILL.md 规范的 Agent（Codex/Claude Code/Cursor/WorkBuddy）生成**可编辑的 PPTD + PPTX**，附带本地浏览器编辑器。

---

## 内容整理

### 核心价值

每次生成默认交付**两份成果**：
1. **PPTD 项目**（可继续编辑的 YAML DSL 中间格式）
2. **PPTX 成品**（自动嵌入字体 + 淡入淡出切换动画）

### PPTD 格式——Agent 友好的演示文稿 DSL

PPTD 是基于 YAML 的演示文稿中间格式，是 OOXML 的简化抽象层：

```
deck/
├── deck.pptd    # 清单文件（主题、布局、元素位置）
├── pages/       # 每页一个 .page 文件（YAML）
├── media/       # 本地媒体资源
└── deck.pptx    # 默认同步生成的 PPTX
```

保留主题、页面布局、元素位置等核心信息，去除 Master 等复杂嵌套，每页自包含、所见即所得。

### 与其他 PPT 方案对比

| 维度 | open-kimi-ppt | 代码拼 PPTX (pptxgenjs) | 整页图片 PPT | 网页 HTML PPT |
|------|--------------|------------------------|-------------|--------------|
| **交付物** | PPTD + PPTX | 仅 PPTX | 仅 PPTX | 单文件 HTML |
| **Agent 友好度** | YAML 逐页描述 | 坐标/API 细节多 | 依赖出图模型 | HTML/CSS 约束强 |
| **PowerPoint 可编辑** | 文本/形状/图片可改 | 可改但难精修 | 整页位图难改 | 非原生 PPTX |
| **视觉质量** | 真实版式 + 多模态质检 | 依赖手调布局 | 海报感 | 动效强 |
| **二次编辑** | 浏览器可视化 + 自动保存 | 改代码重导出 | 需重新出图 | 改 HTML 源码 |

### 功能清单

| 功能 | 说明 |
|------|------|
| **PPTD 生成** | 从零创作 / 风格迁移 / 模板复用 / 图片&PDF 复刻 |
| **预设主题** | ~30 套官方同款 design system，点名即用（如 `pine-green-strategy`）|
| **元素动画** | 默认不加，Prompt 加「要求带元素入场动画」即可启用 |
| **PPTX 生成** | 自动嵌字体 + 淡入淡出翻页切换 |
| **视觉质检** | 多模态模型导出前逐页截图 + 总览图检查（变形/遮挡/出界/对比度/排版/溢出），修复后复检 |
| **在线编辑** | 浏览器查看编辑 PPTD 项目，自动保存 |
| **手动导出** | 编辑器中随时导出 PPTX |
| **格式互转** | PPTX → PPTD 转换后继续修改 |

### 安装方式

```bash
# 推荐：npx 安装（不要 clone，仓库图片多体积大）
npx open-kimi-ppt-skill@latest install -y

# 或让 AI 帮你装
# 对 AI 说：「帮我用 npx 安装 open-kimi-ppt skill」
```

默认装到 `~/.agents/skills/open-kimi-ppt`（跨 Agent 通用目录）。

### 启动本地编辑器

```bash
npx open-kimi-ppt-skill serve
# 打开 http://127.0.0.1:55173/
# 选择包含 .pptd 的项目文件夹即可编辑/导出
```

### 使用示例

```text
# 基础生成
使用 open-kimi-ppt 做一个介绍小米 yu7的 PPT, 要求图片做背景, 素材从网上找, 8 页左右

# 带动画
使用 open-kimi-ppt 做一个介绍小米 yu7的 PPT, 要求图片做背景, 素材从网上找, 8 页左右
要求带元素入场动画

# 指定主题
使用 pine-green-strategy 主题做一份战略汇报 PPT
```

### 安全边界

- CLI 只在 `127.0.0.1` 启动，不监听局域网
- 浏览器只在用户主动授权后读取项目目录
- 保存回调只允许修改 `.pptd` 和 `.page` 文件，拒绝路径越界
- 不提供或注入 Kimi 登录令牌，不访问用户私有文稿
- PPTD 内容由本地宿主交给公开的 Kimi 网页编辑器处理

### Windows 特殊行为

导出 PPTX 时会启动一个常驻调试浏览器（Chrome 或 Edge），因为 Windows 下 agent-browser 无法自行启动 Chrome。以 `--remote-debugging-port`（默认 9337）启动，设计为「最多一个，反复复用」。

---

## 查询拓展

- PPTD 的 YAML schema 完整定义是什么？能否自定义主题和元素类型？
- 视觉质检的多模态模型用的是什么？精度如何？
- Kimi Slides 的 PPTD 格式和 iframe/RPC 协议是怎么被逆向的？
- 30 套预设主题的完整列表和预览图？
- 能否集成到 Hermes Agent 作为 Skill？需要适配什么？

---

## 归纳总结

open-kimi-ppt-skill 是一个精巧的逆向工程项目，核心创新在于 **PPTD 中间层**：用 YAML DSL 描述 PPT，让 AI Agent 好写、人好看、PowerPoint 能改。相比直接拼 OOXML 或整页出图，PPTD 方案兼顾了 Agent 友好度和人类可编辑性。

项目走的是"逆向 Kimi Slides 公开前端行为 → 兼容宿主"的路线，不依赖官方 API 或模型绑定，可以在任意兼容 Agent 中用 DeepSeek 等低成本模型生成。37 Stars 说明项目刚起步，但技术路线设计清晰。

---

## 趋势判断

- **AI Agent 生成 PPT 的三种路线之争**：PPTD 中间层（open-kimi-ppt）vs 直接拼 OOXML（pptxgenjs）vs 整页出图（图片型）。PPTD 路线最有前景——兼顾可编辑性和 AI 友好度
- **逆向 SaaS 产品成为 Agent 技能**：把 Kimi Slides 的前端编辑器 + PPTD 格式逆向出来变成开源 Skill，这种模式会被复制到其他 SaaS 领域
- **SKILL.md 规范成为 Agent 生态标准**：open-kimi-ppt 同时支持 Codex/Claude Code/Cursor/WorkBuddy，说明 SKILL.md 规范正在成为跨 Agent 的通用技能格式
- **多模态视觉质检成为 PPT 生成标配**：导出前自动截图 + 总览图检查 + 修复复检，这种质检闭环正在成为 AI 生成内容的必备环节

---

## 关联分析

- **与 Hermes Agent 的关联**：Hermes 支持 Skill 体系，open-kimi-ppt 可以适配为 Hermes 的 PPT 生成 Skill。Hermes 用户只需说"帮我做一个 PPT"即可触发，生成的 PPTX 通过飞书发送
- **与用户已有 PPT 工具的关联**：用户已有 `ppt-from-notes`（从笔记生成 PPT）和 `wan-pptx-generator`（阿里云 qwen-doc 生成 PPT）技能，open-kimi-ppt 是第三条路线——PPTD 中间层 + 本地编辑器
- **与 FDE 商业模式的关联**：open-kimi-ppt + DeepSeek 低成本模型 = FDE 帮中小企业做 PPT 的工具链。一条 Prompt 生成可编辑 PPT，直接交付客户
- **与用户办公工具链的关联**：用户已有 `office-pipeline`（一键输出 PPT+DOCX+XLSX），open-kimi-ppt 可以作为 PPT 生成引擎的替代方案

---

*笔记创建：2026-08-06 · 来源：github.com/Binaryify/open-kimi-ppt-skill*


## 相关笔记

- [SkillOpt 微软技能优化器](./2026-08-06-SkillOpt-微软Agent技能训练优化器.md) — Skill 可优化性方法论
- [DeepSeek Agent Harness](./2026-08-06-DeepSeek-Agent-Harness执行栈全景图.md) — Skill 运行时环境
