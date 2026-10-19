# BrowserAct Skills 深度分析

> 仓库：https://github.com/browser-act/skills
> 分析日期：2026-06-05
> 定位：AI Agent 专用浏览器自动化 CLI 工具的 Skills 仓库

## 📋 项目画像

| 维度 | 内容 |
|------|------|
| Stars | 新项目（2025-2026），生态扩展中 |
| 语言 | Python（CLI），Shell |
| 许可证 | MIT |
| 一句话 | 面向 AI Agent 的浏览器自动化 CLI，强调反检测、多身份并行、人机协作 |
| 安装 | `uv tool install browser-act-cli --python 3.12` |

## 🏗️ 核心架构

### 1. 两层 Skill 架构（最重要）

```
Layer 1: Entry Skill（静态 SKILL.md）
  → 作用：告诉 Agent "browser-act 存在"
  → 特点：轻量、稳定、极少变更

Layer 2: Runtime Content（动态，通过 `get-skills` CLI 获取）
  → 作用：告诉 Agent "怎么用它"
  → 特点：环境感知、版本匹配、按需加载
```

**核心洞察：** Entry Skill 是安装时一次性下载的静态文件；运行时指令通过 CLI 命令动态获取，确保始终与当前环境版本一致。这种「静态入口 + 动态加载」模式解决了 Skill 版本与工具版本不同步的经典问题。

### 2. Agent-Centric 设计哲学

- **Compact Indexed Text**：页面状态用 token 友好的索引文本表示，而非完整 DOM JSON
- **Indexed Interaction**：Agent 直接用索引号操作 `[N]`，无需 XPath/CSS 选择器
- **desc 语义记忆**：每个浏览器带自然语言描述，Agent 按语义匹配任务到浏览器
- **Delta 标记**：`*[N]` 标记变化的元素，帮 Agent 聚焦增量

### 3. 三层反检测系统

| 层级 | 解决什么 | 手段 |
|------|---------|------|
| 环境层 | 防止验证触发 | 指纹伪装、TLS 轮换、住宅代理 |
| 执行层 | 自动解决验证 | solve-captcha、stealth-extract |
| 人类层 | 自动化搞不定 | remote-assist 远程接管 |

### 4. 并发与隔离模型

- **跨浏览器并行**：独立指纹/IP/Cookie，零交叉污染
- **同浏览器多 Session**：共享登录态，独立执行
- **隐私模式**：零残留，每次全新身份

### 5. Skill Forge（亮点）

从网站探索自动生成可复用 Skill 包（SKILL.md + Python 脚本）。流程：探索 API → DOM 降级 → 验证 → 生成 Skill。探索一次，永久复用。

### 6. Solutions 生态

预构建 50+ 现成 Skill：
- 电商（Amazon 竞品分析、产品搜索、评论抓取）
- 社交监听（Instagram/Facebook/Reddit/X/TikTok/YouTube）
- 潜客生成（LinkedIn、Google Maps、GitHub）
- 搜索研究（Google SERP、新闻、图片）

## 🔍 差距分析

| 我们的实践 | BrowserAct 概念 | 差距 |
|-----------|----------------|------|
| Hermes 内置 browser 工具 | browser-act CLI | ⚠️ Hermes browser 功能有限（无反检测、无多身份） |
| browser_snapshot 快照 | indexed state（紧凑文本+索引） | ⚠️ Hermes 用 accessibility tree，token 效率可优化 |
| 无并发隔离 | 三级并发模型 | ❌ 缺失 |
| CDP 直连 Chrome | chrome-direct + profile import | ✅ 类似方案已有（chatgpt-image skill） |
| 无反检测 | 三层反检测 | ❌ 缺失（Hermes Playwright 易被检测） |
| 无人机协作 | remote-assist | ❌ 缺失 |
| Skill 静态加载 | 两层 Skill（静态+动态） | ⚠️ 可借鉴改进 |
| 单次脚本 | Skill Forge（自动生成 Skill） | ❌ 缺失（但我们有类似思路的 skill-maker） |
| 无代理池 | 动态代理 + 静态代理 | ❌ 缺失 |

## 💡 借鉴学习进化点

### ① 有利进化（应落实）

1. **两层 Skill 架构理念** → 可优化 Hermes Skill 加载机制：静态 frontmatter 做快速索引，运行时通过 CLI 获取详细指令。当前 Hermes Skill 是全量注入，token 开销大
2. **Indexed Interaction 模式** → browser_snapshot 的 accessibility tree 输出可参考 compact indexed text 格式优化 token 效率
3. **Skill Forge 模式** → 已有 lark-skill-maker，可借鉴其「探索→验证→生成」流水线

### ② 有价值（存 Memory）

- browser-act 的 Entry Skill → Runtime Content 分离模式值得记忆
- 反检测三层架构可作为浏览器自动化的参考设计

### ③ 知识库（仅笔记）

- 50+ Solutions Skill 的业务模式（电商/社交/搜索领域的标准 API 化提取）
- Skill Forge 的探索→降级→验证→生成流程

## 📊 预判

| 时间维度 | 预判 |
|---------|------|
| 短期 | 作为 Hermes 内置 browser 工具的补充工具，适合需要反检测/多身份的场景 |
| 中期 | 其 Skill Forge 模式可能被更多 Agent 框架借鉴 |
| 长期 | Agent 专用浏览器工具将成为标配，Hermes 需要在反检测能力上跟进 |

## 关联

- [[Hermes-Agent]] — 当前 Agent 架构
- [[CDP-浏览器自动化]] — 已有 CDP 相关 skill
- [[Skill-Forge]] — Skill 自动生成
- [[Playwright]] — 当前浏览器自动化后端

## 相关笔记
- [MCP已死-CLI-First策略与Skills模式回归](2026-05-30-MCP已死-CLI-First策略与Skills模式回归.md)
- [Google关闭GeminiCLI-AI编码工具从开放走向封闭](2026-06-02-Google关闭GeminiCLI-AI编码工具从开放走向封闭.md)
- [MCP已死-上下文膨胀与CLI优先替代方案](2026-05-30-MCP已死-上下文膨胀与CLI优先替代方案.md)
