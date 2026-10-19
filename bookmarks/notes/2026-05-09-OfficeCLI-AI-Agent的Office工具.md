# OfficeCLI — AI Agent 的 Office 手

- 📅 2026-05-09
- ⭐⭐⭐⭐ 4/5 — 定位精准的 Agent 工具，SKILL.md 自动发现机制值得借鉴
- 🏷️ #AI-Agent #MCP #Office #CLI #工具生态 #SKILL.md
- 📰 GitHub iOfficeAI
- 🔗 https://github.com/iOfficeAI/OfficeCLI

## 摘要

OfficeCLI 是全球首个专门为 AI Agent 构建的 Office 文档操作命令行工具，以单一二进制文件支持 Word/Excel/PPT 的创建、读取、编辑和渲染。内建 Agent 友好的渲染引擎（HTML/PNG），无需安装 Office，零依赖，跨平台运行。通过 MCP 协议集成到 Claude Code、Cursor、Windsurf 等工具，并提供 SKILL.md 机制让 Agent 自动理解如何使用。

## 项目画像

| 维度 | 信息 |
|------|------|
| 定位 | AI Agent 的 Office 操作 CLI |
| 语言 | C# (.NET 10.0) |
| 许可证 | Apache 2.0 |
| Star | 3,567 |
| Fork | 289 |
| 版本 | v1.0.80 (2026-05-09) |
| Commits | 2,659 |
| 姊妹项目 | AionUi (24.2k⭐ TypeScript AI Cowork 桌面应用) |

## 核心功能

### 1. 文档全生命周期
- 创建：`officecli create deck.pptx`
- 读取：`officecli view deck.pptx outline`
- 编辑：`officecli add` / `officecli set` / `officecli remove` — XPath 风格寻址
- 校验：`officecli check` — 格式校验、风格一致性

### 2. 三层操作策略
- L1（Read）：`view` / `get` / `query`
- L2（DOM Edit）：`add` / `set` / `remove` + `--prop` 键值对
- L3（Raw XML）：底层 XML 直接操作，高级定制逃生舱

### 3. 内建渲染引擎
- 从零构建，支持形状、图表（趋势线/误差线/瀑布图/K线/迷你图）、公式（OMML→MathJax）、3D .glb 模型
- Watch 模式：`officecli watch deck.pptx` → localhost:26315 实时预览

### 4. MCP Server
- `officecli mcp` 启动 stdio JSON-RPC 2.0 服务器
- 手写 Utf8JsonWriter，零反射，适配 AOT/Trimmed

### 5. Skill 系统（10个专业包）

| Skill | 用途 |
|-------|------|
| officecli-pptx | PowerPoint 通用 |
| officecli-docx | Word 文档 |
| officecli-xlsx | Excel 表格 |
| officecli-pitch-deck | 融资路演 PPT |
| officecli-academic-paper | 学术论文 |
| officecli-financial-model | 财务建模 |
| officecli-data-dashboard | 数据仪表盘 |
| officecli-word-form | Word 表单 |
| morph-ppt | Morph 动画 PPT |
| morph-ppt-3d | 3D Morph 动画 |

### 6. Agent 自动发现
- `officecli install` — 自动检测所有已安装的 AI 编码 Agent 并注入 Skill
- `curl -fsSL https://officecli.ai/SKILL.md` — Agent 一行获取指令

## 技术架构

### 极简依赖（仅3个 NuGet 包）

| 包 | 用途 |
|----|------|
| DocumentFormat.OpenXml 3.4.1 | OOXML 文件格式 |
| OpenMcdf 3.1.3 | OLE Compound File |
| System.CommandLine 3.0.0-preview | CLI 解析 |

### 源码结构
```
src/officecli/
├── Core/                  # 核心逻辑
├── Handlers/              # 文档格式处理器
├── Help/                  # Schema 驱动 Help
├── Resources/             # 嵌入资源（preview.css/js）
├── CommandBuilder.cs      # 命令构建器主文件
├── CommandBuilder.*.cs    # 按命令拆分 Partial Class（15+文件）
├── McpServer.cs           # MCP 协议（手写 JSON-RPC 2.0）
├── McpInstaller.cs        # MCP 注册器
└── ResidentServer.cs      # Watch 模式后台服务器
```

### 关键设计模式
1. **Partial Class 按命令拆分** — 每个命令独立文件
2. **Schema 驱动 Help** — JSON Schema 嵌入二进制，Agent 可读
3. **SKILL.md 嵌入** — 构建时打包，运行时无需磁盘文件
4. **零反射 JSON-RPC** — 适配 PublishTrimmed
5. **后台热更新** — MCP Server 内建定时升级检查

## 竞品对比

| 维度 | OfficeCLI | Hermes Agent | Codex CLI | Claude Code |
|------|-----------|-------------|-----------|-------------|
| 定位 | Agent 的 Office 工具 | 通用 Agent 框架 | OpenAI CLI Agent | Anthropic CLI Agent |
| 核心能力 | .docx/.xlsx/.pptx | 多工具调度 | 代码生成执行 | 代码生成执行 |
| 协议 | MCP Server | 工具协议 | MCP | MCP |
| 渲染引擎 | ✅ 内建 | ❌ | ❌ | ❌ |
| Skill 系统 | ✅ 10 个领域包 | ✅ Skill View | ❌ | ❌ |
| 安装 | 单二进制 curl | pip/npm | npm | npm |

> 关键区别：OfficeCLI 不是 Agent，是 Agent 的工具——通过 MCP/Skill 被其他 Agent 调用。

## 优缺点

### ✅ 优点
1. **定位精准** — 唯一专注 Agent+Office 的工具
2. **分发体验极致** — 单二进制、零依赖、一行安装、8 平台
3. **SKILL.md 自动发现** — 一个 URL 就是 Agent 完整手册
4. **Schema 驱动 Help** — 机器可读，比 man page 更适合 AI
5. **渲染引擎内建** — Agent 可以"看到"自己创建的文档
6. **极简依赖** — 仅 3 个 NuGet 包，供应链风险低
7. **开发节奏极快** — 2659 commits, 81 tags, 几乎每天更新

### ❌ 缺点
1. **Bus Factor = 1** — 主贡献者仅 goworm 一人
2. **文档不完善** — 无独立 docs/，深度文档依赖 README
3. **功能缺口** — 不支持 PDF，部分 Excel 公式未实现
4. **可替代性** — python-pptx/openpyxl 虽繁琐但免费可用
5. **29-31MB** — 单文件体积对简单操作偏重

## 🔍 可借鉴点

### 1. SKILL.md URL 自动发现
```
curl -fsSL https://officecli.ai/SKILL.md
```
**一 URL 即手册** — Agent 无需预装，fetch 即用。可用于任何 Agent 工具分发。

### 2. Schema 驱动 Help 系统
```bash
officecli help pptx shape --json   # Agent 获取机器可读 Schema
```
**比 man page 更适合 AI 消费** — 构建时嵌入，零网络依赖。

### 3. 三层操作策略（L1→L2→L3）
90% 场景 L2 解决，10% L3 逃生舱。适合所有"高级 API + 低级逃生"工具。

### 4. Agent 自动检测注册
`officecli install` 扫描系统已安装的 Claude Code/Cursor/Windsurf，自动注入 Skill。**安装即集成**。

### 5. Watch 模式视觉闭环
Agent 创建 → 渲染 → 查看 → 修改，Agent 可以"看到"自己的工作成果。

## 🔮 预判

- **短期（1-3月）**：随着 MCP 生态爆发，OfficeCLI 会成为 Agent 工具链标配之一
- **中期（3-6月）**：微软可能推出官方 MCP Office 工具，形成正面竞争
- **长期**：SKILL.md + Schema Help 的"Agent 工具分发范式"可能成为行业标准

## 相关笔记
- [2026-05-09-Skill盈利死结与Plugin演进](2026-05-09-Skill盈利死结与Plugin演进.md) — Skill 生态对比分析
- [2026-05-08-addyosmani-agent-skills生产级Agent技能包](2026-05-08-addyosmani-agent-skills生产级Agent技能包.md) — Agent Skill 框架
- [2026-05-09-AG-UI-AI-Agent前端标准](2026-05-09-AG-UI-AI-Agent前端标准.md) — Agent 前端协议标准
