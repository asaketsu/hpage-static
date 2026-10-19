# 微信小程序 AI Builder：用 AI 把小程序做成睡后收入

> **来源**: [github.com/chenjin-cmd/wechat-miniprogram-builder](https://github.com/chenjin-cmd/wechat-miniprogram-builder)
> **许可证**: MIT
> **Stars**: 160 | **Forks**: 18
> **创建**: 2026-08-01
> **日期**: 2026-08-01
> **标签**: `微信小程序` `AI` `Skill` `变现` `方法论` `Vibe-Coding` `矩阵运营`

---

## 核心结论

这是一个**工具无关的 AI 方法论 Skill**——把微信小程序从 0 到变现的全生命周期（选题→备案→开发→变现→审核→推广→矩阵）编写成程序化工作流，给任意 AI 助手当系统指令用。核心特点：**不绑定单一工具**（Cursor/Claude/Cline/通义灵码都能用），用决策树自动加载对应阶段的方法论。

---

## 一、全生命周期 8 阶段

```
选题 → 注册备案 → AI 开发 → 广告变现 → 审核发布 → 小红书推广 → 矩阵化运营
```

| 阶段 | 参考文件 | 做什么 |
|------|---------|--------|
| **① 变现逻辑** | `01-monetization-logic.md` | 广告 vs 订阅 vs 激活码（已违规） |
| **② 选题** | `02-topic-selection.md` | 选题与需求判断 |
| **③ 注册备案** | `03-register-filing.md` | 注册、备案、认证、个人 vs 企业 |
| **④ 开发+广告** | `04-dev-and-ads.md` | 开发流程、提示词写法、广告变现 |
| **⑤ 云开发/AI** | `05-cloud-activation-ai.md` | 云开发 / AI 接入（需企业资质） |
| **⑥ 审核发布** | `06-submit-review.md` | 上传、审核、被拒修复 |
| **⑦ 推广增长** | `07-promotion-growth.md` | 小红书冷启动与增长 |
| **⑧ 矩阵运营** | `08-matrix.md` | 批量复制运营 |

---

## 二、核心能力

| 能力 | 说明 |
|------|------|
| **全生命周期覆盖** | 从"我想做个小程序"到"矩阵化批量运营" |
| **程序化决策树** | 说一句需求，AI 自动加载对应阶段方法论 |
| **即取即用模板** | 万能提示词、上线检查清单、小红书笔记模板 |
| **合规红线内建** | 激活码违规、个体主体限制、不承诺收益已标红 |
| **工具无关** | 不绑定任何单一 AI 工具 |

---

## 三、两种使用方式

### 方式 ①：任意 AI 工具（推荐）

把整个仓库作为**项目上下文/系统指令**提供给 AI：

> "先读 `UNIVERSAL.md` 和 `references/02-topic-selection.md`，帮我想 5 个适合个人开发者做的小程序方向。"

适用工具：Cursor / Claude / Claude Code / Cline / 通义灵码 / CodeBuddy / ChatGPT 自定义指令 / WorkBuddy 等。

### 方式 ②：WorkBuddy 用户（可选）

```bash
# 复制到 WorkBuddy skills 目录
cp -r wechat-miniprogram-builder ~/.workbuddy/skills/
# 重启后自动作为 Skill 触发
```

---

## 四、项目结构

```
wechat-miniprogram-builder/
├── SKILL.md                # WorkBuddy 入口（触发元数据）
├── UNIVERSAL.md            # 工具无关版（核心）
├── README.md               # 中英双语
├── assets/
│   ├── prompt-recipes.md       # 万能提示词模板
│   ├── release-checklist.md    # 上线检查清单
│   └── xhs-note-templates.md   # 小红书笔记模板
└── references/             # 8 阶段详细方法论
    ├── 01-monetization-logic.md
    ├── 02-topic-selection.md
    ├── 03-register-filing.md
    ├── 04-dev-and-ads.md
    ├── 05-cloud-activation-ai.md
    ├── 06-submit-review.md
    ├── 07-promotion-growth.md
    └── 08-matrix.md
```

---

## 五、⚠️ 合规红线（重要）

> 以下雷区踩中会被下架甚至封号：

| 红线 | 说明 |
|------|------|
| **平台规则会变** | 类目/流量主门槛/广告能力/API 权限以官方最新文档为准 |
| **不承诺收益** | 所有收入/UV/eCPM/案例仅供参考 |
| **激活码模式已违规** | 2026/4/21 标注违规，仅学习用，**请勿上线** |
| **个体主体限制** | 个人主体无法接入微信支付；程序内直接调 AI 通常审核不过（需企业资质） |
| **密钥安全** | AppSecret/API Key/云环境密钥仅存环境变量，勿公开仓库 |

---

## 六、方法论价值评估

### 做对了什么

| 做对的点 | 说明 |
|---------|------|
| **程序化方法论** | 不是教程文章，是给 AI 读的系统指令——Skill 范式 |
| **决策树驱动** | 按需求自动路由到对应阶段，不是线性阅读 |
| **工具无关** | UNIVERSAL.md 可被任意 AI 工具消费 |
| **合规意识** | 明确标注违规模式和红线 |
| **全生命周期** | 覆盖从选题到矩阵运营完整链条 |

### 本质

这是一个**领域知识 Skill**——把微信小程序变现的隐性经验（选题直觉、审核话术、推广策略）结构化为 AI 可执行的程序化工作流。与通用编程 Skill 不同，它封装的是**商业运营方法论**。

---

## 七、与现有笔记/项目的关联

| 关联项目 | 关系 |
|---------|------|
| **Hermes Agent Skills** | 这是 Hermes Skill 体系的同类实践——领域知识程序化。可直接作为 Hermes 的一个 Skill 安装 |
| **学 Agent 正确顺序** | 这个仓库是"Phase 5 之后"的应用——用 Agent 做实际业务变现 |
| **ESP-Claw / Qwen Audio Agent** | 这些 Agent 框架的"Chat Coding"理念与本仓库的"AI Vibe Coding"异曲同工 |
| **Agent Harness 知识体系** | Skill 层的典型实践——领域知识封装为可触发的能力 |
| **位置共享系统** | 如果该系统要做成微信小程序，这个方法论 Skill 可指导全流程 |


## 相关笔记

- [TudouFlow把视频变成生产线](./2026-08-01-TudouFlow把视频变成生产线.md) — 都是 AI 工具化产品实践
- [BitBang-CLI把机器变成URL](./2026-07-31-BitBang-CLI把机器变成URL.md) — 另一种工具产品化思路
- [Agent公司终局两种活法](./2026-08-01-Agent公司终局两种活法.md) — Agent 产品化路径分析
