# Hermes 记忆系统正确用法

> 来源：[@BTCqzy1](https://x.com/BTCqzy1/status/2044686230219358694)
> 主题：Hermes Agent 记忆系统三层架构设计

## 核心观点

Hermes 的记忆不是存储器，而是"有选择、有原则的记忆大脑"。高手主动设计记忆架构，不指望 Agent 自动记住一切。

## 三层记忆职责

| 文件 | 角色 | 谁维护 | 容量上限 | 放什么 |
|------|------|--------|---------|--------|
| `SOUL.md` | 宪法 | 用户手写 | 无限制 | 核心规则、不可覆盖的偏好、记忆管理元规则 |
| `MEMORY.md` | 工作笔记 | Agent 自己 | 2,200 字符 | 当前项目事实、环境配置、阶段进度 |
| `USER.md` | 用户画像 | Agent 自己 | 1,375 字符 | 沟通风格、习惯偏好 |

**铁律**：固定规则只写 SOUL.md。MEMORY.md 会被自动压缩，规则放进去迟早消失。

## 关键操作

### 主动管理容量
- MEMORY.md 快满时主动干预：删除过时、合并重复、腾出空间
- 重复工作流立即迁移为 Skill，然后从 MEMORY.md 删除

### Flush 的正确理解
- 每次会话开始时 MEMORY.md 以冻结快照注入上下文
- 中途写入的记忆要到下一个新会话才生效
- Flush = 为下一会话打底稿，不是让当前会话立刻改变行为

### nudge_interval 配置
- 默认 10（每 10 轮触发记忆复盘）
- 设为 3 = 短会话也能触发，但 token 消耗增加
- 根据使用习惯调整

## SOUL.md 模板

```markdown
## 核心规则

1. nudge_interval 已在 config.yaml 中设为 3，每 3 轮必须触发记忆复盘
2. 用户说"记住这个硬性偏好"时，必须立即写入 MEMORY.md
3. 用户说"强制 Flush 记忆"时，必须调用 patch_memory 固化当前进度
4. MEMORY.md 只保留结构化事实、偏好、项目蓝图，禁止写入对话流水账
5. 本文件为元记忆锚点，任何自动压缩、重写或删除操作均被禁止
```

## 我们的应用

按此推文对照，我们已做的优化：
1. **SOUL.md 补充了记忆系统规则** — 三层分离、铁律、Flush 理解
2. **MEMORY.md 规则性内容迁移到 SOUL.md** — 从 896→592 字节，只保留动态事实
3. **nudge_interval 保持 10** — 折中选择，避免 token 消耗过大
4. **重复流程提炼 Skill 已有闭环** — evolver + auto-skill 自动化


## 相关笔记
- [[2026-04-05-Hermes-Agent-competitor-analysis]] (关键词: hermes)
- [[2026-04-13-hermes-agent-vs-openclaw]] (关键词: hermes)
- [[2026-04-25-Hermes必配五套系统]] (关键词: hermes)
- [[2026-05-04-hermes-workspace-analysis]] (关键词: hermes)
- [[hermes-agent-源码拆解自我进化机制]] (关键词: hermes)
