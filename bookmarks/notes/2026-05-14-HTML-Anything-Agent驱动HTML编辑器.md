# HTML Anything — Agent 驱动 HTML 编辑器

- 📅 2026-05-14
- ⭐ 3.5/5 — 思路清晰的开源项目，Skill模板体系与Hermes高度同构，设计约束系统值得借鉴
- 🏷️ #HTML生成 #Agent #设计系统 #模板引擎 #SSE #跨平台发布
- 📰 微信公众号
- 🔗 https://mp.weixin.qq.com/s/cqW77zHN1NXn6Sud4liU-Q

## 摘要

HTML Anything 是一个本地优先的 Agent 驱动 HTML 编辑器（Apache-2.0 开源）。核心理念：Markdown 是中间格式，HTML 才是最终交付形态。支持 8 种本地 AI Agent（Claude Code/Cursor/Codex 等），75 套 Skill 模板覆盖 9 种交付形态，SSE 流式渲染，一键导出到微信/知乎/X/小红书。项目采用 Next.js 16 + Turbopack 构建。

## 核心内容

### 1. 架构设计
- **Agent 自动发现**：启动时扫描 PATH，自动检测已安装 CLI，零配置
- **Skill 模板 = SKILL.md**：frontmatter 定义 mode/scenario/surface 三维分类 + markdown 正文
- **JSON-line 协议**：Agent 每行输出独立 JSON，SSE 推送到 iframe 沙箱实时渲染
- **沙箱隔离**：iframe sandbox 确保生成内容安全

### 2. 模板体系（75套 × 2维组织）
- **模式（mode）**：web原型(21)/deck演示(20)/帧特效样机(12)/social社交(8)/office办公(14)
- **场景（scenario）**：design/marketing/engineering/product/finance/hr/personal
- 可通过搜索、筛选快速定位，支持自定义开发

### 3. 硬约束设计系统
- 8px 基线网格（间距必须是 8 的倍数）
- 禁纯黑 #000 / 纯白 #fff（用柔和色调）
- 色彩对比度 ≥ 4.5（WCAG AA）
- 中文字体栈：Noto Sans/Serif SC 优先
- 强制 :focus 状态
- 禁止 Lorem Ipsum

### 4. 导出能力
- 微信公众号：juice 库 CSS 内联
- 知乎：LaTeX 公式兼容
- X/微博/小红书：modern-screenshot 2x 高清 PNG 剪贴板
- 独立 HTML / PNG 下载

## 🔍 借鉴点

- **Skill 模板三维分类** → 已融合到 html-slides skill 和 claude-design skill（mode/scenario/surface 维度参考）
- **硬约束设计系统** → 已融合到 html-slides + claude-design（8px网格/禁纯黑白/对比度/中文字体栈/focus状态）
- **SSE 流式渲染 + JSON-line** → 记入 Memory 备用，未来可用于实时预览生成过程
- **Agent 自动发现机制** → Hermes 已有类似能力（skill_view/skills_list），但 PATH 扫描模式可借鉴

## 🔗 关联性

- 关联已有 skill：[[html-slides]] — 已 patch 融合设计约束
- 关联已有 skill：[[claude-design]] — 已 patch 融合硬约束
- 关联已有 skill：[[design-md]] — Google DESIGN.md token 规范，互补
- 关联已有 skill：[[wechat-pb]] — 微信公众号排版，导出方式互补
- 关联已有笔记：[[2026-05-04-Modly-AI浏览器插件平台]] — 同为 Agent 生态项目

## 💡 启发

- **Skill 即模板 = 普适模式**：HTML Anything 用 SKILL.md 做模板定义，Hermes 用 SKILL.md 做能力定义，格式完全相同但用途不同。这种"同格式不同语义"的模式值得思考——未来是否可以做 Skill 格式的统一协议？
- **"反 AI Slop" 是设计刚需**：项目把"禁 Lorem Ipsum""禁纯黑纯白"等硬约束写进模板，说明 AI 生成内容的质量问题已成共识。我们生成 HTML 时应有类似硬约束层。
- **本地优先的隐私价值**：所有 Agent 在本地运行，内容不经过外部服务器。这个卖点在数据敏感场景（航空、金融）特别重要。

## 🔮 预判

- **短期**：项目 v0.1.0 较早期，模板质量和稳定性待验证，但思路方向正确
- **中期**：Agent + HTML 生成赛道会越来越拥挤，差异化在于模板品质和导出兼容性
- **长期**：Markdown → HTML 的自动转换可能成为 Agent 的标配能力，类似 code review 之于开发工具

## 相关笔记
- [[2026-05-04-Modly-AI浏览器插件平台]] - 同为 Agent 生态项目
- [[2026-05-03-CyberVerse-开源数字人实时互动平台]] - HTML 模板分析


## 相关笔记
- [2026-05-12-网络安全-security-automation](2026-05-12-网络安全-security-automation.md)
- [2026-05-12-数据治理-data-catalog](2026-05-12-数据治理-data-catalog.md)
- [20260513-llm-wiki-obsidian-gbrain-知识自组织与自进化](20260513-llm-wiki-obsidian-gbrain-知识自组织与自进化.md)
- [llm-wiki-gbrain-agent-evolution_33aa818c](llm-wiki-gbrain-agent-evolution_33aa818c.md)
- [2026-05-15-上下文才是Agent的命门-QClaw上下文竞争论](2026-05-15-上下文才是Agent的命门-QClaw上下文竞争论.md)
