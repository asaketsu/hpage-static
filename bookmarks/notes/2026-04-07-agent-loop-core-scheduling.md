# Agent Loop: The Core of AI Agent Scheduling

> **Source**: WeChat (mp.weixin.qq.com/s/GXMgtuSwcwrtqqmb8Gr9mg)
> **Date**: 2026-04-07
> **Tags**: agent-loop, tool-use, LLM, autonomous-agent, claude-code
> **Rating**: ⭐⭐⭐⭐⭐
> **Series**: AI Agent 三大核心概念系列 (LLM + Tool Use + Agent Loop)

---

## Core Thesis

Agent 的本质就是一个 while 循环：不断调 LLM、执行工具、喂回结果，直到任务完成。整个调度逻辑几行代码就能写完，复杂度在于模型能力和工具设计，而非编排逻辑。

引用 Anthropic《Building effective agents》：
> Agents can handle sophisticated tasks, but their implementation is often straightforward. They are typically just LLMs using tools based on environmental feedback in a loop.

## Key Concepts

| Concept | Detail |
|---------|--------|
| Agent vs Workflow | Workflow = 预定义流程；Agent = 模型自主决定下一步 |
| Message History = Memory | LLM 无状态，消息历史就是 Agent 的"记忆" |
| stop_reason | "tool_use" → 继续循环；"end_turn" → 输出结果退出 |
| Max Loop Counter | 防止 LLM 陷入死循环（重复调用同一工具），必须加计数器 |

## The Loop (Pseudocode)

```python
while True:
    response = call_llm(message_history)
    if response contains tool_use:
        result = execute_tool(tool_use)
        message_history.append(tool_result)
        continue  # loop
    else:
        output_final_answer()
        break  # exit
```

## Real Example: Bug Fix in 9 Rounds

| Round | Decision | Tool | Result |
|-------|----------|------|--------|
| 1 | Find login endpoint | search("login") | Found src/auth/login.ts |
| 2 | Read source | read_file() | Got source code |
| 3 | Check token logic | read_file(token.ts) | Found generateToken |
| 4 | Fix bug | write_file() | Patched |
| 5 | Run tests | bash("npm test") | 2 tests failed |
| 6 | Check test code | read_file(test.ts) | Tests need update |
| 7 | Fix tests | write_file(test.ts) | Updated |
| 8 | Re-run tests | bash("npm test") | All pass ✅ |
| 9 | Done | — | Summary output |

Key insight: 中间经历了一次测试失败后的自我纠正。不是按脚本执行，而是根据每步实际结果动态调整。

## Three Key Details

1. **消息历史是关键** — 每轮的 tool_use + tool_result 都追加到历史，下一轮带上完整历史。这就是 Agent 的"记忆"。
2. **stop_reason 决定走向** — 工具调用 vs 直接回答，由模型自主判断。
3. **循环不能无限跑** — 必须设最大次数，防止 token 费用失控。

---

## Value Analysis

### ✅ 与我们系统的直接对应

| 论文概念 | 我们的实现 | 文件 |
|----------|-----------|------|
| Agent Loop | OpenClaw agentTurn 循环 | SOUL.md Hook 2 Anti-Yield |
| Tool Use | 20+ tools (read/exec/search...) | TOOLS.md |
| Message History | LCM (Lossless Context Management) | MEMORY.md |
| stop_reason | sessions_yield / NO_REPLY | SOUL.md |
| Max Loop Counter | cron timeoutSeconds / subagent runTimeout | rules/cron.md |
| Autonomous vs Workflow | cron isolated sessions = autonomous | HEARTBEAT.md |
| 自我纠正 | 9轮bug修复 ≈ 我们的 task-executor 6-step SOP | skills/task-executor/ |

### ⚠️ Improvement Opportunities

| Insight | Current Gap | Action |
|---------|-------------|--------|
| "根据中间结果动态决定" | 我们的 cron 大多是单轮执行 | 考虑 multi-turn agent session for complex crons |
| "消息历史就是记忆" | LCM 会压缩历史，可能丢失上下文 | 关键决策立即 WAL 写入永久记忆（已有，可加强） |
| "最大循环次数" | cron 有 timeout，但无显式 loop counter | Anti-Yield Protocol 已覆盖（不中途停） |

### 🔥 Actionable

| Action | Priority | Note |
|--------|----------|------|
| Anti-Yield Protocol 验证 | P2 | 确认当前实现与论文 loop 模式一致 |
| Multi-turn cron 实验 | P3 | 让复杂 cron（如神探）支持多轮工具调用 |
| Hook 2 文档补充 loop counter | P4 | 明确最大轮次和退出条件 |
→ Related: 2026-04-07-OpenClaw-autonomy-harness-loop.md
→ Related: 2026-04-07-email-not-revival-agent-needs-it.md
→ Related: 2026-04-05-xiaolongxia-one-person-company.md
→ Related: 2026-04-07-hermes-agent-deep-dive-evolution-roadmap.md
→ 相关：claude-code-tool-execution-orchestration


## 相关笔记
- [[2026-05-03-ai-agent-resources-ecosystem]] (关键词: agent, ai)
- [[2026-05-08-AI-Agent控制流]] (关键词: agent, ai)
- [[skills-autonomous-ai-agents]] (关键词: agent, ai)
- [[2026-05-03-AI趋势-ByteByteGo2026五大趋势]] (关键词: agent, ai)
- [[2026-04-05-SelfImproving-Agent-CLI-infra]] (关键词: agent, ai)
