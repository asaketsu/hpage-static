# 免费高效 Office Skills 全家桶！建议每个打工人都用上

- 📅 2026-04-02
- ⭐⭐⭐ 3/5 — 实用工具介绍，Office 文档生成的 Skill 参考
- 🏷️ #MiniMax #OfficeSkills #PPT #Excel #PDF #Word #开源
- 📰 公众号：爱AI的大刘
- 🔗 GitHub: MiniMax-AI/skills（MIT 协议，5.3K Star）

## 概述

MiniMax 官方开源了一套 Office 文档生成 Skills，共 11 个 Skill，核心 4 个：
- **PPTX Skill** — 专业 PPT 生成
- **PDF Skill** — 专业 PDF 报告
- **XLSX Skill** — 投行级 Excel
- **DOCX Skill** — 专业 Word 文档

## 四大 Skill 详解

### 1. PPTX Skill
- 底层：PptxGenJS
- 18 套配色方案，4 种视觉风格
- 5 种标准页面：封面/目录/章节/内容/总结
- 指令：`帮我做一份 [主题] PPT，包含 [章节]`

### 2. PDF Skill
- 底层：Python ReportLab + Node.js Playwright
- 三种模式：CREATE（创建）、FILL（填表）、REFORMAT（重排）
- 封面风格可选（如 magazine）
- 指令：`帮我创建一份 [主题] PDF 报告，使用 [风格名] 封面风格`

### 3. XLSX Skill（最亮眼）
- 底层：Python pandas + openpyxl
- **投行级配色规范**：蓝色=输入值，黑色=公式，绿色=跨表引用
- 核心规则：每个计算值必须是 Excel 公式，不能写死数字
- 改一个数全表联动
- 五种模式：创建/编辑/分析/格式化/转换

### 4. DOCX Skill
- 底层：.NET + OpenXML SDK 3.2.0（不用 python-docx，控制力更强）
- 13 种排版预设，完整 CJK 中日韩字体支持
- 学术论文（IEEE/APA）、招投标、合同、技术文档
- 指令：`帮我生成一份 [预设名] 格式的 [文档类型]`

## 依赖环境

| Skill | 技术栈 | 安装 |
|-------|--------|------|
| PPTX | Node.js + PptxGenJS | `npm install -g pptxgenjs` |
| PDF | Python 3.9+ + Node.js 18+ + Playwright | `pip install reportlab pypdf` |
| XLSX | Python + pandas | `pip install pandas openpyxl` |
| DOCX | .NET 运行时 + OpenXML SDK | `bash scripts/setup.sh` |

## 延伸阅读

- GitHub: github.com/MiniMax-AI/skills


## 相关笔记
- [[2026-04-29-竞品吸收笔记-khazix-skills]] (关键词: skills)
- [[skills-overview]] (关键词: skills)
- [[2026-05-05-开源AI模型2025-DeepSeek-Qwen新格局]] (关键词: 开源)
- [[2026-05-06-lewislulu-html-ppt-skill-analysis]] (关键词: ppt)
- [[2026-05-15-数据目录工具全景指南]] (关键词: 开源)
