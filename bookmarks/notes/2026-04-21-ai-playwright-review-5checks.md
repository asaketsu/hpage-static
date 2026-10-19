---
title: "AI生成Playwright，先审这5关"
date: 2026-04-21
source: 微信公众号"测试论道"
author: Summer Stone
url: https://mp.weixin.qq.com/s/ZLvyGvcJprYy34rH3d1y1Q
tags: [AI, 测试, Playwright, CodeReview, 自动化]
rating: 4/5
---

# AI生成Playwright，先审这5关

- 📅 2026-04-21
- ⭐ 4/5 — 实战经验总结，Review Checklist 落地可用
- 🏷️ #AI #Playwright #CodeReview #自动化测试 #质量门禁
- 📰 测试论道 · Summer Stone
- 🔗 [原文链接](https://mp.weixin.qq.com/s/ZLvyGvcJprYy34rH3d1y1Q)

## 摘要

文章针对 AI 生成 Playwright 测试用例的流行趋势，提出 5 关 Review 标准：覆盖面（关键路径而非 happy path）、定位器（语义化而非脆 CSS）、断言（业务结果而非页面打卡）、等待（auto-wait 而非固定超时）、证据链（trace/截图排障）。核心论点是"AI 生成测试最危险的不是写不出来，而是写出来后你没认真审"。

## 核心内容

### 第 1 关：覆盖面
- AI 擅长补 happy path，不是门禁资产
- **标准**：用例失败时你会不会真的拦版本？

### 第 2 关：定位器
- ❌ `div:nth-child(3) button` → ✅ `getByRole('button', {name:'Submit'})`
- 要跟用户语义或测试契约绑定

### 第 3 关：断言
- ❌ 只 `toBeVisible()` → ✅ 先断业务状态，再断页面提示
- 关注：状态更新、接口结果、权限变化、金额正确

### 第 4 关：等待
- ❌ `waitForTimeout(3000)` 是 CI 定时炸弹
- ✅ auto-wait、状态断言、web-first assertions

### 第 5 关：证据链
- 配 `trace: 'on-first-retry'`、截图、日志上下文
- 失败后能判断：真 bug / 环境抖动 / 脚本脆

## 🔍 借鉴点

- **Review Checklist 直接可用** → 已创建 `ai-test-review` skill，5 条标准结构化
- **"先断业务再断页面"原则** → 适用于所有自动化测试场景，不仅限 Playwright
- **证据思维** → Hermes 自身的错误处理也应留 trace（日志、上下文），方便回溯
- **反 happy path 意识** → 写 skill 和工具时，加入边界条件和异常场景的要求
- **定位器语义化** → 代码生成时优先 getByRole/getByTestId，避免脆定位

## 🔗 关联性

- 关联 skill：[[ai-test-review]] — 从此文提炼出的 5 关 Review 标准化 skill
- 关联 skill：`requesting-code-review` — 代码 review 流程，可集成测试 review 环节
- 关联 skill：`test-driven-development` — TDD 流程中 AI 生成测试的质量把关
- 关联笔记：[2026-04-18-Hermes-Agent-v0.10.0-insight](2026-04-18-Hermes-Agent-v0.10.0-insight.md) — Hermes 的质量门禁设计
- 关联笔记：[2026-04-18-竞品吸收-OpenLovable](2026-04-18-竞品吸收-OpenLovable.md) — AI 代码生成的质量保障

## 💡 启发

- **"看起来像测试"是最大的陷阱** → AI 生成内容的危险性不在于质量差，而在于"看起来对"，麻痹了审查者
- **Review 是不可省略的层** → 省下的生成时间会在 flaky、误报、低价值用例上全吐回去——这个逻辑适用于所有 AI 生成场景
- **自检机制设计** → Hermes 生成代码后应有自检层，不只是"能跑就行"，要验证是否覆盖关键风险
- **"5 关"模式可推广** → 这种"5 个维度审查"的结构化思维，可以应用到 AI 生成的任何类型代码

## 🔮 预判

- **趋势**：AI 生成测试的 review 标准化会成为团队必须建立的流程，类似代码规范
- **趋势**：测试框架会内置 AI 代码质量检测（如 Playwright 可能加入 AI linter）
- **趋势**：门禁系统会从"能不能跑"演进到"测得有没有价值"的量化评估
- **行动**：将 5 关 Checklist 集成到 Hermes 的代码生成后置检查流程
- **行动**：在团队推广时，将此文作为 AI 测试生成的 review 标准
- **延伸思考**：当 AI 能自动完成 5 关 review 时，是否还需要人工审查？人审的不可替代性在哪？


## 相关笔记
- [[2026-04-06-AI-Scientist-v2]] (关键词: ai)
- [[2026-05-03-ai-agent-resources-ecosystem]] (关键词: ai)
- [[2026-05-14-航空结构设计AI短期基础设施]] (关键词: ai)
- [[2026-04-09-SKILL-md-ai-agent-skills]] (关键词: ai)
- [[2026-04-13-rag-vs-mcp-architecture]] (关键词: ai)
