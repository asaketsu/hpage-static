# Claude Code工程师放弃Markdown转HTML — Thariq方法论分析

- 📅 2026-05-09
- ⭐⭐⭐⭐ 4/5 — AI时代文档格式演进的信号，实操性建议多
- 🏷️ #AI工具 #HTML #Markdown #ClaudeCode #文档工程 #Agent
- 📰 51CTO技术栈（林芯 编）
- 🔗 https://mp.weixin.qq.com/s/XPYA0SMll83igQEtdUkOEw
- 🔗 原始推文 https://x.com/trq212/status/2052809885763747935

## 摘要

Claude Code 团队工程师 Thariq 公开宣称已完全停止手动编辑 Markdown，改用 Claude Code 生成 HTML 作为主要输出格式。他的核心论点：AI 时代文档的消费方式变了 — 从"人写人读"变成"AI 写、人扫读/交互"，格式需求从极简标记转向富表达。文章总结了 HTML 的四大优势（表达力/阅读/分享/交互）、五大使用场景（发散思考/代码审查/设计原型/报告/自定义编辑器），以及三个核心权衡（token消耗/生成速度/版本控制）。

## 核心内容

### 1. 为什么放弃 Markdown？

Markdown 的三大痛点（在 AI Agent 时代被放大）：
- 长文件阅读困难（>100行自己都难读）
- 信息密度低（表格/颜色/复杂图表表达力不足）
- 分享不便（浏览器原生支持差，需附件）

### 2. HTML 四大优势

| 维度 | 具体表现 |
|------|----------|
| 信息表达 | 8种类型：表格/插图/颜色/图表/动画/交互组件/导航/响应式 |
| 视觉清晰 | 从"界面"角度组织内容，移动响应式 |
| 分享便利 | 上传即链接，非附件 |
| 双向交互 | 滑块/旋钮/按钮实时调参，结果可一键复制回 Claude Code |

### 3. 为什么选 Claude Code 不选 Claude Design？

Claude Code 上下文远更多：当前文件 + MCP（Slack/Linear等）+ 浏览器 + git 历史。Thariq 让 Claude Code 扫描整个代码文件夹，分类归组后自动生成带图表的 HTML。

### 4. 五大实战场景

- 发散思考探索：6种方案并排网格 → 选方向 → 深入 → 汇总实施计划
- 代码审查：HTML渲染diff+注释+流程图，优于GitHub默认视图
- 设计原型：HTML高保真草稿 → 转React/Swift/Kotlin实现
- 报告输出：多数据源整合 → HTML文档/交互式解释器/演示文稿
- 自定义编辑器：为特定数据构建一次性HTML编辑界面

### 5. 三个权衡

- Token消耗：HTML多2-4x，但Opus 4.7的1M上下文窗口使其可接受
- 生成速度：比Markdown慢2-4x，但"结果值得"
- 版本控制：最大缺点 — HTML diff嘈杂，结构/样式变化放大为大量噪音

## 🔍 借鉴点

- HTML发散网格法 → 已融入 planning-with-files skill（Phase 0），多方案探索时生成HTML并排比较
- 代码审查用HTML渲染diff → 可用于 claude-design / sketch skill 输出代码审查报告
- 自定义编辑器思路 → 与已有 sketch skill（一次性HTML mockup）理念一致，可强化为数据编辑场景

## 🔗 关联性

- 关联已有 skill：claude-design — HTML输出设计
- 关联已有 skill：sketch — 一次性HTML mockup
- 关联已有 skill：html-slides — HTML演示文稿
- 关联已有 skill：planning-with-files — 已融入发散网格法
- 关联已有笔记：[[2026-05-Skill-vs-Plugin产业分析]] — Skill作为交付格式的讨论

## 💡 启发

- "参与感"是核心动机 — Thariq 担心完全放手让AI决策，HTML的视觉丰富度让他保持审视能力。这暗示 AI 工具设计需要在"自动化"和"人类参与"之间找到平衡
- Markdown 不会死 — 版本控制友好这个优势在工程流程中不可替代，HTML更适合"最终输出"而非"工作文档"
- Agent 时代的文档分层：Markdown = 工作文档（人+AI共编） / HTML = 展示文档（AI生成、人消费）

## 🔮 预判

- 短期(3月)：更多 AI coding 工具将支持 HTML 作为输出格式选项
- 中期(6月)：会出现 Markdown→HTML 自动转换的 Agent 工作流（写用MD，展示用HTML）
- 长期：格式本身不再重要 — Agent 根据场景自动选择最优输出格式，用户不再关心底层是MD还是HTML

## 相关笔记
- [[2026-05-Agent-native-PM方法论]] — Agent时代的PM工作流

