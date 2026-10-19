# 智谱 AutoClaw 自进化 + Skill 商店：不需要研究 Hermes

- 📅 2026-04-17
- ⭐⭐⭐⭐ 4/5 — 直接竞品动态，值得跟踪
- 🏷️ #AutoClaw #智谱 #自进化 #Skill商店 #竞品分析 #GLM-5.1
- 📰 公众号：智谱

## 核心内容

### 🧬 自进化机制
- Agent 扫描对话：纠正、新方法、偏好、踩坑 → 弹出「进化请求」卡片 → 用户审批 → 写入记忆
- 两种触发：关键词触发（"以后""记住""永远"）+ 自动检测（多次失败重试后沉淀经验）
- 高质量进化：宁可每周 1-3 次，不要每天 50 条噪音
- 用户可控：所有进化需审批，可随时查看"学会了什么"

### 📎 GLM Office Skills 五件套
- PPT / DOCX / XLSX / PDF / Charts，基于 GLM-5.1 办公场景专项优化
- 细分场景不同技术路线（HTML/LaTeX）
- 交付前自检（格式/排版/内容正确性）
- 文档格式互转（markdown↔doc↔pdf）
- **一键联动输出**：一行命令同时生成调研 PPT + 讲稿 DOCX

### 🛒 专家共创 Skill 商店
- 女娲 Skill：把人的思维方式浓缩成可运行的人物 skill
- 横纵分析法：多源检索→交叉验证→结构化归纳→带引用报告
- Frontend Slides：代码生成幻灯片，内置转场交互

## 关键洞察

**定位差异**: 标题直接喊"不用研究Hermes"，主打开箱即用 vs Hermes 需要自配置。本质是 SaaS 产品 vs 开源方案的路线之争。

**Skill 商店模式**: 专家共创是好的商业化路径。不是所有人都愿意自己写 SKILL.md，付费买现成的方法论更符合大众需求。

## 启发与借鉴

1. **进化审批机制**: 我们已经落地为 `evolution-control` skill，质量评估 + 用户审批卡片
2. **Office 联动 pipeline**: 已落地为 `office-pipeline` skill，一键出 PPT+DOCX+XLSX
3. **人物建模**: 已落地为 `persona-modeler` skill，调研→决策DNA→可复用 persona
4. **结构化分析**: 已落地为 `deep-analysis` skill，多源交叉验证

## 竞品对比

| 维度 | AutoClaw | 我们 |
|------|----------|------|
| 进化机制 | 卡片审批 | evolution-control（质量评分+审批）|
| Office | 五件套 | ppt-generator+xlsx-generator+nano-pdf+office-pipeline |
| Skill 数量 | 商店3万+ | 精品138个 |
| 部署模式 | SaaS下载 | 自部署开源 |
| 人物建模 | 女娲Skill | persona-modeler |
| 深度分析 | 横纵分析法 | deep-analysis |

## 相关笔记
- [2026-04-13-hermes-agent-vs-openclaw](2026-04-13-hermes-agent-vs-openclaw.md) - Hermes vs OpenClaw 对比
- [2026-04-13-4-ai-agent-frameworks-comparison](2026-04-13-4-ai-agent-frameworks-comparison.md) - 4大Agent框架对比
- [2026-04-05-Hermes-Agent-competitor-analysis](2026-04-05-Hermes-Agent-competitor-analysis.md) - Hermes竞品分析
