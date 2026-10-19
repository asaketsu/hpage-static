# Hermes Agent Deep Dive — 进化路线图

> **Sources**: turingpost.com/p/hermes + mranand.substack.com + lushbinary.com + dev.to
> **Date**: 2026-04-07
> **Rating**: ⭐⭐⭐⭐⭐（竞品深度对标，直接指导进化）
> **Status**: 已分析，7项进化计划

---

## 一、Hermes 核心优势提取

### 1. 自我改进循环（Self-Improvement Loop）⭐ 最核心差异

**Hermes 的做法：**
- 每个任务完成后，agent 自动评估是否值得记录
- 触发条件：≥5 次工具调用 / 错误恢复 / 用户纠正 / 非显而易见的工作流
- 自动创建 skill 文件（不是日志，是可复用指令集）
- Skill 使用中发现更好路径时，用 `patch`（而非全量重写）更新
- 6 个 skill 操作：create, patch, edit, delete, write_file, remove_file

**我们的现状：**
- ✅ task-executor Step 5 有 skill 提炼规则（≥3步可复用→auto-generated/）
- ✅ evolver skill 有扫描+晋升机制
- ❌ 缺少**自动触发**：没有在每次任务完成后自动检查是否该提炼 skill
- ❌ 缺少 **patch 优先**策略
- ❌ auto-generated/ 目录尚未创建（从未被触发过）

### 2. 四层记忆架构

| 层 | Hermes | 我们 | 差距 |
|---|---|---|---|
| L1 始终在线 | MEMORY.md(2200字符) + USER.md(1375字符) | SOUL.md + 永久记忆四分类 | ❌ 我们没有字符上限，容易膨胀 |
| L2 会话搜索 | SQLite + FTS5 全文搜索 | LCM (lcm_grep/expand) | ✅ 功能对等 |
| L3 程序记忆 | Skills 目录，按需加载（只注入摘要） | skills/ 目录，全部注入名称 | ⚠️ 我们注入全部内容 |
| L4 用户建模 | Honcho（12层身份建模，跨session积累） | user.md 手动维护 | ❌ 缺少动态建模 |

**关键设计差异：**
- Hermes **刻意限制 L1 为 3575 字符**（~1300 token），强制策展而非堆积
- Skill 加载采用**渐进式披露**：系统提示只含名称+摘要，内容按需加载
- Session 搜索和 Prompt 记忆分离：自动判断信息属于哪一层
- 记忆修改**下一 session 才生效**（非 mid-conversation）

### 3. Gateway 架构差异

| 维度 | OpenClaw | Hermes |
|------|----------|--------|
| 核心控制 | Gateway = 中央控制平面 | Agent Loop = 核心同步引擎 |
| 职责 | 路由/工具/状态/会话 | 所有功能统一在同一循环内 |
| 跨平台 | Session 绑定平台 | Session 绑定 ID（可跨平台续接） |
| Gateway 与学习的关系 | 分离 | 学习循环是 gateway 的一部分 |

### 4. Safety by Default

- 用户授权/审批检查
- 会话隔离
- 凭证过滤（不泄露 API key 到 prompt）
- 上下文扫描（检测注入攻击）
- 记忆条目安全扫描（防止 prompt injection via memory）

### 5. Cache-Aware 设计

- 系统提示从稳定源构建 → 前缀一致 → API provider 缓存命中率高
- Skill 渐进式加载 → token 成本不随 skill 数量增长
- 压缩 sentinel 在硬限制前触发 → 辅助模型提取关键信息到 3575 字符限制内
- **Lineage** 引用链：压缩后的对话可追溯到原始记录

### 6. Periodic Nudge

- Session 中定期触发内部系统提示
- Agent 扫描近期活动，评估是否值得持久化
- 不需要用户输入，自主决定写什么、不写什么

---

## 二、进化计划（7项）

### Plan A: Skill 自动提炼闭环（P1 高优先级）🔥

**目标：** 每次 cron/subagent 任务完成后，自动检查是否值得提炼 skill

**实现方案：**
1. 修改 task-executor Step 5 → Step 5.5（自动提炼检查）
2. 触发条件：任务完成 + 工具调用≥3次 + 无对应 skill
3. 创建 `skills/auto-generated/` 目录
4. 采用 Hermes 的 **patch 优先** 策略：已有 skill 则 patch，无则 create
5. 在 evolver-scan.sh 中加入 skill 使用效果跟踪

**文件变更：**
- `skills/task-executor/SKILL.md` — Step 5.5 新增
- `skills/evolver/scripts/evolver-scan.sh` — 新增 skill 效果检测
- `rules/evolution.md` — 新增 skill 自动提炼规则

### Plan B: 记忆预算制（P1 高优先级）🔥

**目标：** 防止永久记忆无限膨胀，强制策展

**实现方案：**
1. 设定永久记忆预算：每个 permanent/*.md 文件上限 2000 字符
2. 在记忆自动记录 cron 中加入预算检查
3. 超预算时触发**压缩合并**：合并相似条目、移除过时信息
4. 记忆修改**下一 session 生效**（模拟 Hermes 行为，避免 mid-session 注入不稳定）

**文件变更：**
- `rules/memory.md` — 新增预算规则
- 记忆自动记录 cron prompt — 加入预算检查逻辑

### Plan C: Skill 渐进式加载（P2 中优先级）

**目标：** Skill 越多 token 开销不增长

**实现方案：**
1. 当前 OpenClaw 的 SOUL.md Rules 表已列出 skill 触发场景
2. 这就是渐进式加载的雏形：不全部注入，按场景激活
3. 优化：Rules 表只保留 name + description（1行），不保留路径
4. Agent 需要 skill 时先 read SKILL.md，按需加载
5. 当前已基本实现 ✅（SOUL.md 只列触发场景，不列 skill 内容）

### Plan D: Safety by Default 增强（P2 中优先级）

**目标：** 防止 prompt injection via memory/工具

**实现方案：**
1. 记忆写入时扫描注入模式（`ignore previous instructions` 等）
2. evolver-scan.sh 已有 MAX_DEBUG_DEPTH=3 防止无限调试
3. 新增：工具输出 sanitizer（检测异常内容在写入 memory 前）

**文件变更：**
- `rules/evolution.md` — 新增记忆安全扫描
- `permanent/errors.md` — 记录首次安全事件

### Plan E: Honcho 式用户建模（P3 低优先级）

**目标：** 跨 session 动态积累用户画像

**实现方案：**
1. 当前 user.md 已有手动积累（从 capability-evolver 落地）
2. 升级为半自动：记忆自动记录 cron 检测到偏好变化时自动更新 user.md
3. 分区设计：偏好/习惯/领域/沟通风格/决策模式
4. 不需要完整 Honcho 12层，4-5个关键维度足够

**文件变更：**
- `permanent/user.md` — 加入分区结构
- 记忆自动记录 cron prompt — 加入用户偏好检测

### Plan F: Lineage 引用链（P3 低优先级）

**目标：** LCM 压缩后仍可追溯到原始对话

**现状：**
- OpenClaw 的 LCM 已有 summary ID + expand 机制
- 基本等价于 Hermes 的 Lineage ✅
- 无需额外开发

### Plan G: Cache-Aware 系统提示（P4 观察中）

**目标：** 保持系统提示前缀稳定，提高 API 缓存命中率

**现状：**
- SOUL.md + AGENTS.md + 桌面文件注入 → 前缀相对稳定
- OpenClaw 4.5 已有 cacheRead 95%+ ✅
- 无需额外开发

---

## 三、优先级排序

| 优先级 | Plan | 预计工作量 | 预期收益 |
|--------|------|-----------|----------|
| **P1** | A: Skill 自动提炼闭环 | 半天 | 从未触发→每次任务后自动评估 |
| **P1** | B: 记忆预算制 | 2小时 | 防止 memory 膨胀，强制策展质量 |
| **P2** | C: Skill 渐进式加载 | 已实现 ✅ | 无需额外工作 |
| **P2** | D: Safety 增强 | 1小时 | 防 prompt injection |
| **P3** | E: 用户建模升级 | 2小时 | user.md 从手动→半自动 |
| **P3** | F: Lineage | 已实现 ✅ | LCM 已覆盖 |
| **P4** | G: Cache-Aware | 已实现 ✅ | 95%+ cacheRead |

---

## 四、我们的差异化优势（Hermes 缺少的）

| 能力 | 我们 | Hermes |
|------|------|--------|
| 多 Agent 团队协作 | ✅ 5 agent 多角色 | ❌ 单 agent |
| 知识编译体系 | ✅ 月度编译+三层对标 | ❌ 无 |
| 嗅探系统（机会学习） | ✅ sniff-interests + 队列 | ❌ 无 |
| 进化熔断机制 | ✅ 连续错误→ESCALATE | ⚠️ 有限 |
| Cron 精细化 | ✅ 26+ 定制任务 | ⚠️ 自然语言 cron（粗粒度） |
| 飞书原生集成 | ✅ WebSocket 实时 | ⚠️ 第三方适配 |
| 本地项目深度集成 | ✅ 脚本/cron/数据全链路 | ⚠️ 通用 |

**结论：Hermes 的优势在"自我改进循环"和"记忆架构的克制设计"。我们的优势在"团队协作"和"精细化运营"。最优策略是吸收 Hermes 的核心设计思想（预算制、自动提炼、patch 优先），补强我们的短板，同时保持团队+精细化运营的差异化。**
→ Related: 2026-04-05-Hermes-Agent-competitor-analysis.md
→ Related: 2026-04-07-agent-loop-core-scheduling.md
→ Related: 2026-04-05-capability-evolver-self-upgrade.md
→ 相关：2026-04-09-SKILL.md模式-AI智能体技能.md（按需加载+description质量）
→ 相关：2026-04-13-hermes-agent-vs-openclaw.md（Hermes vs OpenClaw对比落地）


## 相关笔记
- [[2026-04-13-hermes-agent-vs-openclaw]] (关键词: agent, hermes)
- [[hermes-agent-源码拆解自我进化机制]] (关键词: agent, hermes)
- [[2026-05-14-Small-Hermes-自我进化深度解析]] (关键词: agent, hermes)
- [[2026-04-18-Hermes-Agent-v0.10.0-insight]] (关键词: agent, hermes)
- [[2026-04-18-Hermes-Agent-v0.10.0-release-analysis]] (关键词: agent, hermes)
