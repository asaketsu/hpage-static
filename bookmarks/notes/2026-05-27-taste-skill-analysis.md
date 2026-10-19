# Taste-Skill 21k⭐ 深度分析 — AI 前端 Anti-Slop 技能框架

> 分析日期：2026-05-27
> 来源：https://github.com/Leonxlnx/taste-skill
> 分类：AI Agent 技能框架 / 前端设计工程

## 摘要

Taste-Skill 是一个 21,466 Stars 的高人气项目，通过 SKILL.md 指令文件注入编码 Agent（Codex/Cursor/Claude Code），让 AI 生成的前端页面避免千篇一律的"slop"。核心机制是三旋钮参数化（风格变异/动画强度/视觉密度）+ 60+ AI Tells 黑名单 + 强制预飞检查清单。

## 项目画像

- **Stars:** 21,466 | **Forks:** 1,730 | **License:** MIT
- **语言:** Shell（实际内容为 Markdown SKILL.md 文件）
- **创建:** 2026-02-19 | **最近更新:** 2026-05-26
- **作者:** Leonxlnx (@lexnlin)
- **定位:** Anti-Slop Frontend Framework for AI Agents
- **生态:** Codex, Cursor, Claude Code, ChatGPT

## 核心架构

### 六层体系

1. **Brief Inference (§0)** — 设计读盘：推断页面类型/受众/氛围词，输出一行 Design Read
2. **Three Dials (§1)** — 三旋钮参数化：
   - DESIGN_VARIANCE: 1-10（对称 → 混沌）
   - MOTION_INTENSITY: 1-10（静态 → 电影级）
   - VISUAL_DENSITY: 1-10（画廊 → 仪表盘）
3. **Design System Map (§2)** — 路由到官方包（Material/Fluent/Carbon等）或标注美学近似
4. **Bias Correction (§4)** — 反偏见纠偏（禁AI紫、禁居中Hero、禁beige+brass奢侈品色盘）
5. **AI Tells (§9)** — 60+ 条 AI 特征黑名单（em-dash、假截图div、装饰文本条等）
6. **Pre-Flight Check (§14)** — 60+ 项交付前强制检查清单

### 技术栈

- React/Next.js + Tailwind v4 + Motion(原Framer Motion) + GSAP ScrollTrigger
- v2 实验版（当前默认）相比 v1 新增：Brief Inference、Design System Map、Dark Mode Protocol、Redesign Protocol、Block Library 契约、Out of Scope 声明

### Skills 矩阵

| Skill | 定位 |
|-------|------|
| taste-skill (v2) | 默认全能型，三旋钮+预飞检查 |
| gpt-tasteskill | GPT/Codex 专用严格版 |
| soft-skill | 高端视觉设计（Awwwards级别） |
| minimalist-skill | Notion/Linear 风格极简 |
| brutalalist-skill | 瑞士风格工业设计 |
| output-skill | 防截断强制完整输出 |
| image-to-code-skill | 图片→分析→代码流水线 |
| redesign-skill | 现有项目审计+修复 |
| brandkit / imagegen-* | 图片生成类 |

### 底层研究 (research/)

项目包含 LLM 懒惰性研究的完整框架：
- 根因：RLHF计算经济性 → 训练数据偏见 → 认知捷径 → 输出限制
- 修复：参数调优 → Prompt工程（语法绑定/XML结构/验证循环）→ 架构模式
- 实证数据引用学术研究

## 亮点与不足

### 亮点
- 🟢 **参数化设计方法**：三旋钮比纯文本规则可执行性更强
- 🟢 **60+ AI Tells 黑名单**：极其具体的反模式列表，来自生产测试
- 🟢 **Pre-Flight Checklist**：强制检查机制，不通过不交付
- 🟢 **Brief Inference 先读后写**：避免默认审美
- 🟢 **研究支撑**：不凭直觉，有数据
- 🟢 **诚实性原则**：Apple Liquid Glass 明确标注为"web approximation"

### 不足
- 🟡 SKILL.md 单文件 87KB/1206行，对 context window 压力极大
- 🟡 完全面向 React/Next.js 生态
- 🟡 Block Library 仅定义 schema，未填充实际组件

## 可借鉴模式

| 模式 | 说明 | 新颖性 | 可移植性 | 落实状态 |
|------|------|--------|---------|---------|
| AI Tells 黑名单 | 60+ 条反AI味禁令 | 高 | 高 | ✅ 已融入 html-quality-standards |
| Pre-Flight Checklist | 交付前强制检查 | 高 | 高 | ✅ 已融入 html-quality-standards |
| Brief Inference + 三旋钮 | 设计读盘+参数化 | 高 | 高 | ✅ 已融入 sketch skill |
| LLM 懒惰性研究框架 | 根因分析体系 | 中 | 中 | ✅ 已记入 Memory |
| GSAP 代码骨架 | StickyStack/HorizontalPan | 中 | 高 | ✅ 引用源在 taste-skill |
| Design System Map | Brief→官方包路由 | 中 | 低 | 仅记录（我们非React生态） |

## 预判

- **短期（1-3月）：** Block Library 逐步填充实际组件，成为前端Agent标配
- **中期（3-6月）：** 被更多 Agent 框架（Hermes/Continue/Cline）借鉴方法论
- **长期（6月+）：** 成为 AI 前端质量的事实标准之一，类似今天的 ESLint 之于代码质量

## ✅ 落实情况

```
📋 借鉴点落实审计
├── ①有利进化 项：4个
│   ├── AI Tells 黑名单 → skill_manage(patch html-quality-standards) ✅
│   ├── Pre-Flight Checklist → skill_manage(patch html-quality-standards) ✅
│   ├── Brief Inference + 三旋钮 → skill_manage(patch sketch) ✅
│   └── LLM懒惰性框架 → memory add ✅
├── ②有价值 项：2个 → memory 写入 ✅
└── ③知识库 项：5个 → 仅笔记 ✅
```

三问验证：
- Q1 行为改变：html-quality-standards 新增 AI Tells + Pre-Flight；sketch 新增 Brief Inference + 三旋钮
- Q2 可grep：AI Tells(3处)、Pre-Flight(2处)、Brief Inference(1处)、三旋钮(1处)
- Q3 机器验证：exit_code 全0

## 关联笔记

- [[html-quality-standards]] — 已融入 AI Tells 黑名单
- [[sketch]] — 已融入 Brief Inference + 三旋钮
- [[LLM 懒惰性研究]] — Memory 记录

## 相关笔记
- [Agent Skills才是关键抽象层](2026-04-02-Agent Skills才是关键抽象层.md)
- [AI编码工具战争-CodexClaudeCodeCursor收敛为分层架构](2026-05-24-AI编码工具战争-CodexClaudeCodeCursor收敛为分层架构.md)
- [CATIA-CAA-mkmk编译器Skill创建指南](2026-05-25-CATIA-CAA-mkmk编译器Skill创建指南.md)
- [agent-skills-ai-操作手册](2026-05-26-agent-skills-ai-操作手册.md)
- [the-book-of-secret-knowledge-运维安全工具百科](explore/2026-05-24-the-book-of-secret-knowledge-运维安全工具百科.md)
- [voicebox-flow-matching-next-gen-heavyweight-tts](explore/2026-05-24-voicebox-flow-matching-next-gen-heavyweight-tts.md)
- [SkillOpt-Agent技能自进化](explore/2026-05-26-SkillOpt-Agent技能自进化.md)
