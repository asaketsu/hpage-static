# YouTube 自动标签 AI 生成视频：内容透明化里程碑

> **来源**：The YouTube Team · blog.youtube · 2026-05-27
> **原文**：https://blog.youtube/news-and-events/improving-ai-labels-viewers-creators/
> **笔记ID**：sniff-20260528-youtube-ai-labels
> **格式**：双格式(MD + HTML) · 含借鉴进化点 · RAG/wiki联动

## 摘要

YouTube 宣布两项重大更新：将 AI 生成/修改内容的标签移至更显眼位置（长视频放在播放器下方、Shorts 直接叠加在视频上），以及推出自动 AI 检测系统。自 2024 年起 YouTube 已要求创作者手动披露 AI 使用，现在新增内部信号自动识别高逼真度 AI 内容。创作者保留控制权可申诉，但使用 YouTube 自家 AI 工具（Veo、Dream Screen）或含 C2PA 元数据的内容标签不可撤除。标签不影响推荐和变现。

## 核心内容

### 1. 标签位置升级

旧版：AI 使用披露藏在视频描述中，观众容易忽略。
新版：
- 长视频：标签出现在播放器正下方、描述上方——第一眼可见
- Shorts：标签直接叠加在视频画面上

这是"单一标签格式"——所有高逼真度/实质性 AI 修改内容统一展示。低风险内容（动画、轻微修改）仍在展开描述中显示。

### 2. 自动 AI 检测

2026 年 5 月开始部署内部信号系统：
- 如果创作者未披露但系统检测到"显著高逼真度 AI 使用"，自动贴标
- 创作者可在 YouTube Studio 中更新披露状态
- 例外：不可撤除标签的情况——
  - 使用 YouTube 自家 AI 工具（Veo、Dream Screen）生成的内容
  - 含 C2PA 元数据标记为"完全 AI 生成"的内容

### 3. 标签与推荐/变现解耦

关键设计决策：AI 标签本身不改变推荐算法和变现资格。YouTube 选择"透明但不惩罚"路线——可能为了避免创作者抵触和误伤。

### 4. C2PA 元数据集成

C2PA（Content Authenticity Initiative 的技术标准）是内容溯源的行业标准。YouTube 直接读取 C2PA 元数据作为 AI 检测信号之一，与 Adobe、Microsoft、BBC 等主导的联盟标准对接。

## 关键概念

1. **AI Content Labeling**：AI 生成/修改内容的强制性披露标签，从自愿走向自动检测
2. **C2PA (Coalition for Content Provenance and Authenticity)**：内容来源和真实性联盟标准，通过元数据记录内容创建和修改历史
3. **Veo / Dream Screen**：YouTube/Google 自家的 AI 视频生成工具
4. **Photorealistic AI Detection**：高逼真度 AI 内容自动识别，YouTube 内部信号系统

## 能力边界

- 自动检测刚上线，准确率未知——误报会引发创作者反弹
- "不影响推荐"的承诺可能随政策变化
- 仅覆盖 YouTube 平台，短视频竞品（TikTok、Reels）未跟进
- C2PA 标准的覆盖率仍然很低，大多数 AI 生成内容不带此元数据
- 非高逼真度的 AI 内容（如 AI 辅助剪辑）不在自动检测范围

## 最佳实践

1. 内容创作者应主动披露 AI 使用——被动等待自动检测可能导致争议
2. 企业使用 AI 生成视频营销内容时，应准备好合规披露方案
3. C2PA 元数据是未来趋势——内容生产工具应开始集成此标准

## 🔍 借鉴学习进化点（必填）

| # | 点 | 原文要点 | 对当前系统的借鉴 | 行动计划 |
|---|-----|---------|---------------|---------|
| 1 | 透明但不惩罚 | AI 标签不影响推荐和变现 | Hermes 产出内容（笔记/报告）也应标注 AI 辅助程度 | 在 note-dual-format HTML 中添加 AI-assisted 元标签 |
| 2 | 自动检测+人工覆盖 | 系统自动标记但创作者可申诉 | proactive-sniff 的笔记质量评估可借鉴此模式——自动标记低质量但允许 override | 给 sniff 产出的笔记添加 confidence 字段 |
| 3 | 分层标签策略 | 高逼真度→显著位置；低风险→描述中 | 笔记重要性分层——关键洞察突出显示，辅助信息折叠 | 在 HTML 模板中优化 insight-box 的视觉层级 |
| 4 | C2PA 元数据 | 通过行业标准元数据追踪内容来源 | 笔记系统应记录"知识来源链"——从原始素材到最终笔记的完整路径 | 在 MEMORY 系统中增强 source tracing |
| 5 | 自家工具特权 | YouTube 自家 AI 工具标签不可撤除 | Hermes 自研 skill 产出应有可区分标记 | skill 产出添加 skill_name 标签到笔记元信息 |

## 🔗 RAG / Wiki 联动（必填）

### 当前状态
- wiki-kb: 已有 AI-SEO操纵、Agent记忆污染等相关安全笔记
- RAG: AI内容治理类笔记已有基础索引
- Memory: 无 YouTube AI 标签相关记录

### 改进方案
1. 在 ubot-topics-index.json 添加 youtube-ai-labeling 条目
2. 建立"AI 内容治理"专题索引，关联 Google AI Mode 广告、AI-SEO 操纵等笔记

### 已执行操作
- ✅ 关联已有笔记：[[2026-05-21-Google-AI被SEO操纵的调查报告]]、[[2026-05-22-OpenClaw日常聊天黑化Agent-ULSPB安全研究]]
- ✅ 加入 sniff-queue.json

## 相关笔记
- [[2026-04-18-Hermes-LLM-Wiki-学习笔记]] (关键词: agent, hermes, wiki)
- [[2026-05-10-知识体系架构设计]] (关键词: memory, rag, wiki)
- [[2026-05-24-nashsu-llm_wiki项目分析_deep-blue]] (关键词: agent, skill, wiki)
- [[2026-04-13-4-ai-agent-frameworks-comparison]] (关键词: agent, hermes, openclaw)
- [[2026-04-13-hermes-agent-vs-openclaw]] (关键词: agent, hermes, openclaw)
