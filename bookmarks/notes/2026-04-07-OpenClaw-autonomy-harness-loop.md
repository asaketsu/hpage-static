# OpenClaw 自主性与 Harness 循环机制

**来源**：https://mp.weixin.qq.com/s/EhkgJRpUIn5rNJdDXwVLSw
**日期**：2026-04-07
**评分**：⭐⭐⭐⭐⭐（5/5）
**标签**：OpenClaw、Agent架构、Harness设计、模型自主性、GPT

---

## 核心观点

自主性不是模型属性，是 harness 属性。GPT 在 OpenClaw 里频繁停下来等用户说"继续"，不是因为 GPT 笨，而是因为 OpenClaw 的外层提供了 `sessions_yield` 显式停机工具，而 GPT 恰好倾向于使用它。

同一个 GPT 模型放到 Codex CLI 或 OpenCode 里会一路推进到稳定点才停。

## 关键概念：稳定点（Fixed Point）

一个回合真正结束的条件不是模型说了一句话，也不是模型没再调工具，而是：

**再跑一轮也不会产生任何新动作，系统状态不再变化。**

好的 harness 推进到稳定点才停；不够好的 harness 在到达稳定点前就停了——不是因为任务完成，而是某个机制打断了循环。

## 三个 Harness 对照

| Harness | 循环结构 | 停机判断 | 自主性 |
|---------|---------|---------|--------|
| **Codex CLI** | Rust双层（Task loop + Sampling loop） | `needs_follow_up` 为 false + stop hook 可注入 continuation prompt | ⭐⭐⭐⭐⭐ |
| **OpenCode** | Go 单层 loop | pending tool_calls 为空 | ⭐⭐⭐⭐ |
| **OpenClaw** | Node.js 外层 + `sessions_yield` | 模型主动调用 yield 或无新工具调用 | ⭐⭐⭐ |

**Codex CLI 的关键设计**：
- 即使被安全策略拦截，也会注入 continuation prompt 给模型收尾机会
- `needs_follow_up` 精确判断是否还有待推进状态

**OpenClaw 的问题**：
- `sessions_yield` 作为显式工具暴露给模型
- GPT 系列倾向于"做完一步问一下用户"
- 两者叠加 → 频繁在非稳定点停机

## 合理停 vs 不合理停

**应该停**：需要外部输入（验证码、人工确认）、不可逆操作（删除、支付）、等待异步事件（webhook）

**不该停**：工具结果已返回但差一步总结、文件没写完、测试没跑 — 这些 agent 应该自己闭环

## 诊断框架：四问定位法

遇到模型自主性差的问题，用四个问题定位：

1. **循环写在哪？** （Rust/Go/JS — 语言层面决定了循环能否被打断）
2. **停机条件是什么？** （什么机制决定"这一轮结束"）
3. **模型能不能主动停？** （有没有 yield/pause 这类工具暴露给模型）
4. **停了之后能不能恢复？** （是硬停机还是可以接续推进）

---

## 吸收：与我们的关联

### 直接相关
1. **我们的 GLM-5-turbo 是否存在同样问题？** — GLM 系列"先做后报"风格与 GPT 不同，可能影响较小，但 `sessions_yield` 仍存在被滥用的风险
2. **神探盯盘 cron** — 如果神探在扫描过程中 yield 等用户确认，预警会延迟。应检查 shentan agent instructions 是否明确禁止中途 yield
3. **Cron 任务执行** — 所有 cron 任务的 agent 都可能中途 yield，导致任务不完整

### 间接启发
1. **Agent instructions 优化** — 在关键 agent（ubot/dev/神探）的 instructions 中明确写："不要在任务完成前 yield，推进到稳定点"
2. **团队调度协议** — sessions_send 分派任务时，目标 agent 可能 yield 导致不完整执行。应在 task-executor SOP 中加入"确认完成"检查

---

## 优化自我

### 对我的提升
这篇文章揭示了一个我们一直忽视的问题：**我们的 cron 任务和 subagent 可能因为模型中途 yield 而未能执行完整**。这解释了为什么有些 cron 报告"完成"但实际产出不完整。

### 实施计划
1. **立即**：在 SOUL.md / agent instructions 中加入"禁止中途 yield"规则
2. **短期**：审查所有 cron 任务的 prompt，确保明确要求"一次性完成所有步骤，不要中途停顿"
3. **中期**：在 HEARTBEAT 检查中加入"cron 产出完整性"检查项
4. **监控**：统计 cron 任务中 yield 的使用频率，识别问题模型

→ 相关：2026-04-05-Clawith团队版OpenClaw.md

→ 相关：2026-04-04-OpenClaw4.2后台不再翻车.md

→ 相关：2026-04-05-Hermes-Agent竞品分析.md

→ 相关：2026-04-06-AI-Scientist-v2.md

→ 相关：2026-04-07-OpenClaw-Skills完整使用手册.md
→ 相关：2026-04-07-邮件不是复兴了是Agent终于开始需要它了.md
→ 相关：2026-04-07-OpenClaw摄像头RTSP本地视觉模型智能家居.md
→ Related: 2026-04-07-agent-loop-core-scheduling.md
→ 相关：claude-code-tool-execution-orchestration


## 相关笔记
- [[2026-04-04-OpenClaw-4.2-stable-backend]] (关键词: openclaw)
- [[2026-04-03-OpenClaw最佳实践15条精华版]] (关键词: openclaw)
- [[2026-04-10-OpenClaw-4-things-persistent-tasks]] (关键词: openclaw)
- [[2026-04-04-OpenClaw 为什么越用越好用？本质就是一堆 md 文件]] (关键词: openclaw)
- [[2026-04-05-Clawith-team-OpenClaw]] (关键词: openclaw)
