# OpenClaw 为什么越用越好用？本质就是一堆 md 文件

> **来源**：稻森 @ 阿里云开发者 | mp.weixin.qq.com/s/jEp6evc4DsCj-AKk5OwgPA
> **日期**：2026-04-04
> **标签**：OpenClaw、Agent、Workspace、MD文件、最佳实践
> **评分**：⭐⭐⭐⭐⭐（5/5）

---

## 核心观点

OpenClaw 越用越好用的本质是：**一个自我进化的 md 文件系统**。每次对话前把 md 拼进 prompt，对话后让 agent 把新学到的东西写回 md 文件。简单循环构成巨大飞轮。

## 为什么很多人觉得不好用

| 原因           | 说明                                              |
| ------------ | ----------------------------------------------- |
| 模型没选对        | OpenClaw 不生产智能，是让模型发挥更好的框架，底层模型决定上限             |
| 把 Agent 当通才  | 应配置多 Agent 专精不同领域，各有独立 workspace/memory/session |
| 没有"培训" Agent | 新装不等于好用，需要多对话、积累偏好、固化经验                         |

## 7 个核心 MD 文件

1. **SOUL.md** — Agent 人格（语气、风格、边界、价值观，可自我进化）
2. **USER.md** — 用户画像（偏好、工作习惯）
3. **IDENTITY.md** — 身份信息（名字、形象、签名 emoji）
4. **MEMORY.md** — 长期记忆索引（跨 session 持久）
5. **HEARTBEAT.md** — 心跳任务（定时检查）
6. **AGENTS.md** — 多 Agent 协作协议
7. **BOOTSTRAP.md** — 一次性初始化引导（完成后自毁）

## Skill 加载优先级（低→高）

1. 内置 skill → 2. 全局 skill → 3. 项目 skill → 4. Workspace skill

用户 workspace skill 优先级最高，可覆盖任何内置行为。

## 关键推论

1. **Agent 的价值在 workspace 文件夹里** — 代码公开、模型通用，真正不可替代的是 md 文件里的偏好、工作流、经验、项目上下文
2. **调教 Agent 就是写 md** — 不需要编程，用自然语言写经验规范放到 workspace 即可
3. **换电脑拷 workspace 就行** — 删掉 workspace 则一切从零

## 💡 对我们的价值分析

### ✅ 已在做的

- SOUL.md v3.0 自进化机制 + 三大核心 Hook
- MEMORY.md 索引化 + 永久记忆四分类
- 多 Agent 团队（dev/content/data/opm）
- 22 个 Cron 自动化 + Watchdog

### ⚠️ 可改进的

- BOOTSTRAP.md 我们是 MISSING 状态，可考虑补充一次性初始化流程
- IDENTITY.md 未填写（Name/Creature/Vibe/Emoji/Avatar 全空）

### 🔥 重点行动

- 文章对 OpenClaw 本质的理解非常精准，与我们的实践高度一致
- **workspace skill 优先级最高**这一点值得注意：我们的自研 skill（memory-system、planning-with-files 等）放在 `~/jclaw/skills/` 就是最高优先级，天然正确


## 相关笔记
- [[2026-04-04-OpenClaw-4.2-stable-backend]] (关键词: openclaw)
- [[2026-04-03-OpenClaw最佳实践15条精华版]] (关键词: openclaw)
- [[2026-04-10-OpenClaw-4-things-persistent-tasks]] (关键词: openclaw)
- [[2026-04-05-Clawith-team-OpenClaw]] (关键词: openclaw)
- [[2026-04-07-OpenClaw-autonomy-harness-loop]] (关键词: openclaw)
