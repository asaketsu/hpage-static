# 从零构建 AI CLI 方法论：ChainlessChain 项目拆解

- 📅 2026-05-04
- ⭐ 5/5 — 极高质量的 Agentic CLI 架构拆解，方法论可直接复用于构建任何 AI CLI
- 🏷️ #AI-CLI #Agent架构 #Prompt-Caching #工具系统 #权限系统 #MCP #ChainlessChain
- 📰 X/Twitter @IceBearMiner（小八）转载，原作者 RiverAi7z/longfa
- 🔗 https://x.com/IceBearMiner/status/2037888800341610684
- 🔗 GitHub: https://github.com/chainlesschain/chainlesschain（3,280+ commits, 7 stars, 4 forks）

## 摘要

原作者以 Claude Code 为参照，从零用纯 TypeScript 两天构建了一个生产级 Agentic CLI。文章系统性拆解了 AI CLI 的每一层架构：SSE 流式通信、分段式 System Prompt 与三级缓存、Agent Loop 骨架、21 个内置工具、Deferred Tools 按需加载、双阶段权限系统、MCP 集成、Skills 模板系统、后台 Agent 并发、三层记忆模拟。完整方法论覆盖从 API 层到用户体验的全栈设计。项目代码仓库 chainlesschain/chainlesschain 已迭代到 3,280+ commits，包含 Android App、Web Panel、Desktop 等完整产品线。

## 核心内容

### 一、整体架构（五层分层）

```
├── api/      — 多 Provider 适配层（Anthropic/OpenAI/Google/OpenAI-Compatible）
├── core/     — 引擎层：Agent Loop、SSE 客户端、Context 管理、Compact 逻辑
├── tools/    — 工具系统：21 个内置工具 + MCP 客户端
├── ui/       — 终端渲染层：流式文本、进度指示、颜色主题
└── skills/   — 技能库：参数化 prompt 模板（/commit, /pr 等）
```

### 二、API 层与 SSE 流式通信

SSE（Server-Sent Events）是 CLI 与 LLM 通信的核心协议。设计要点：

- **统一事件类型**：不同 Provider 的事件格式差异在 SSE 客户端内做适配，将 OpenAI 的 delta 结构翻译成统一的内部事件类型。Agent Loop 层完全不感知 API 格式差异。
- **格式参数化**：初始化时传入 `format: 'openai'` 参数，在事件解析层做格式适配。
- **默认支持御三家**（Anthropic/OpenAI/Google）+ OpenAI 兼容格式（Ollama、LM Studio 等）。

### 三、System Prompt 分段与三级缓存

这是全文最有价值的架构设计。完整请求体的 system 字段是一个**有序 block 数组**，顺序固定：

```
身份 → 工具指南 → 编码规范 → 安全规则 → 风格指南 → 环境信息 → Git 上下文 → CLAUDE.md → MCP 指令
```

**Prompt Caching 三个施力点**：

| 缓存层 | 位置 | 策略 |
|--------|------|------|
| 静态系统提示 | system prompt blocks | 排在前面的静态内容越稳定，缓存命中率越高 |
| 工具定义 | tools 数组 | 最后一个 tool definition 打 `cache_control` 标记 |
| 动态断点 | 最后一条 tool_result message | 作为缓存断点 |

**核心洞察**：Anthropic 的 prompt caching 按 block 数组的**前缀匹配**来识别缓存。这个粒度的 cache 意识在大多数 LLM 应用里是缺失的。

### 四、Agent Loop 骨架

```
while (iterations < 25) {
  1. 构建 messages 数组 + system prompt blocks
  2. 调用 API（流式）
  3. SSE 事件解析 → 增量渲染到终端
  4. 累积 assistant response
  5. 检查 stop_reason:
     - tool_use → 执行工具 → tool_result 追加到 messages → 继续循环
     - end_turn / max_tokens → 结束循环
}
```

**上限 25 次**：足够完成大多数真实任务（通常 10 轮内），同时防止 runaway loop 耗尽 API 额度。

**自动 Compact 机制**：每轮迭代开始时估算 token 数（总字符数 ÷ 4），超过上下文限制的 85% 时触发压缩——发起独立 API 调用生成摘要，用 `[summary, "Understood."]` 替换原 messages 数组。

### 五、工具系统（21 个内置工具）

| 工具 | 实现 | 关键设计 |
|------|------|----------|
| Read | `fs.readFile` + 行号前缀 | 支持 offset/limit 分页 |
| Write | `fs.mkdir({recursive:true})` | 先确保父目录存在 |
| Edit | 精确字符串替换 | `old_string` 必须唯一出现，多次则报错 |
| Bash | `child_process.exec` | 120s 超时，>500 行截断（前200+后100） |
| Grep | 自实现 regex 引擎 | 三种输出模式、上下文行、跨行匹配 |
| WebFetch | fetch + HTML 剥离 + 截断 | — |
| WebSearch | DuckDuckGo | — |

**Deferred Tools 优化**：低频工具（NotebookRead、TodoWrite）不放入每次请求的 tools 数组，标记为 deferred——模型需要时通过 `ToolSearch` 按关键词查询获取 schema，下一轮再调用。**tools 数组固定开销降低约 40%**。

### 六、权限系统（双阶段安全）

**三种模式**：

| 模式 | 行为 |
|------|------|
| default | safe 工具自动执行，dangerous/write 需用户确认 |
| auto | 绕过所有交互（CI 环境），deny rules 仍生效 |
| plan | 只读沙箱，dangerous/write 静默拒绝 |

**Bash 权限双阶段判定**：

- **Stage 1**：模式匹配（已知安全/危险命令规则表），覆盖 90%+，零延迟
- **Stage 2**：未覆盖的命令发给 Haiku 模型判定（allow/deny/ask_user），延迟约 300-500ms

**工具分类**：
- safe: Read, Glob, Grep, WebFetch, WebSearch
- dangerous: Bash, Agent
- write: Write, Edit

### 七、MCP（Model Context Protocol）集成

- **协议**：JSON-RPC 2.0 over stdio
- **启动序列**：initialize 握手 → tools/list 获取工具定义
- **工具定义**：JSON Schema 格式的 inputSchema，与 Anthropic API 工具格式直接兼容
- **命名空间**：工具名加 `mcp server_name` 前缀做隔离
- **McpManager**：管理多个 server 的生命周期

### 八、Skills 系统

比自定义 Agent 更轻量的复用单元——参数化的 prompt 模板。用户输入 `/commit` 时，skill 系统展开模板、注入上下文，提交给当前 agent loop。

8 个内置 skill：
- commit / pr / review — Git 操作
- simplify — 审查代码重复/低效
- update-config — 修改 CLI 自身配置

### 九、后台 Agent 与并发

后台 Agent 通过 `run_in_background: true` 标记，Promise 存入 Map，完成时以 `tool_result` 形式通知主 Agent。

### 十、三层记忆系统

| 层 | 内容 |
|----|------|
| user | 用户偏好（角色、习惯、专长） |
| project | 项目约定（不可从代码/git 推导的上下文） |
| reference | 外部资源指针（URL、看板、文档链接） |

## 🔍 借鉴点

### 可直接用于 Hermes 体系的模式

1. **Prompt Caching 三级策略** → Hermes 的 system prompt 也可以做分段缓存优化，特别是静态段+工具定义的缓存命中
2. **Deferred Tools 按需加载** → Hermes 的 ~100+ skills 可以分高频/低频，低频走 ToolSearch 按需获取 schema，大幅减少每次请求的 token 开销
3. **双阶段权限判定** → Hermes 的 Bash 执行可以参考 Stage 1 模式匹配 + Stage 2 轻量模型判定的分层策略
4. **自动 Compact 85% 阈值** → 上下文管理可以借鉴字符数÷4的快速估算 + 摘要替换策略
5. **SSE 格式适配层** → 多 Provider 的统一事件类型设计模式，适合 Hermes 的多模型切换场景

### ChainlessChain 项目本身值得关注

- 3,280+ commits 说明项目活跃度极高
- 包含 Android App + Web Panel + Desktop 全平台
- 有完整的 `.claude/rules` 配置（AI 辅助开发规则）
- 151 个 Tags 说明版本管理规范

## 🔗 关联性

- 关联已有笔记：[2026-04-28-竞品吸收_OpenCLI](2026-04-28-竞品吸收_OpenCLI.md) — 同属 AI CLI 竞品分析
- 关联已有笔记：[2026-04-27-MCP协议生态与Agentic-RAG架构深度学习](2026-04-27-MCP协议生态与Agentic-RAG架构深度学习.md) — MCP 协议深度参考
- 关联已有笔记：[2026-04-24-深入源码-Hermes-Agent-Self-Improving源码拆解](2026-04-24-深入源码-Hermes-Agent-Self-Improving源码拆解.md) — Hermes 自身架构对比
- 关联已有笔记：[2026-05-01-AI-Agent记忆架构前沿学习](2026-05-01-AI-Agent记忆架构前沿学习.md) — 记忆系统设计参考
- 关联已有笔记：[2026-05-03-AI-Agent-Protocol-Ecosystem-2026-学习](2026-05-03-AI-Agent-Protocol-Ecosystem-2026-学习.md) — Agent 协议生态全景
- 关联 Skill：note-dual-format — 本笔记使用的输出格式
- 关联技术栈：Hermes Agent → 可借鉴 Agent Loop 设计、Prompt Caching 策略

## 💡 启发

- **分段式 System Prompt 是工业级 AI 产品的标配** — 不是把所有指令塞进一个字符串，而是有序 block 数组，配合缓存策略。这个设计理念可以直接应用到 Hermes 的 prompt 构建中。
- **工具系统的按需加载是性能关键** — 40% 的 token 节省意味着更低的成本和更快的响应。Hermes 的 100+ skills 如果也做 deferred 处理，效果会更显著。
- **权限系统不能一刀切** — 双阶段设计（快速规则 + 模型兜底）是用户体验和安全性的最佳平衡点。
- **"两天构建"背后是对架构的深度理解** — 这不是从零开始，而是对 Claude Code 架构的精确还原。真正的能力在于"拆解"而非"构建"。

## 🔮 预判

- **Agentic CLI 将成为 AI 应用的标准交互形态** — 从 Claude Code 到 Codex CLI 到 Gemini CLI，大厂都在押注终端 Agent。ChainlessChain 证明了开源社区也能做出生产级实现。
- **Prompt Caching 将成为 AI 工程的必修课** — 随着上下文窗口越来越大，缓存策略的收益会指数级增长。
- **MCP 生态将加速工具集成** — JSON-RPC over stdio 的简洁协议设计让工具集成变得标准化，ChainlessChain 的 McpManager 模式会被更多项目采用。

## 相关笔记

- [2026-04-28-竞品吸收_OpenCLI](2026-04-28-竞品吸收_OpenCLI.md) - 另一个 AI CLI 竞品
- [2026-04-27-MCP协议生态与Agentic-RAG架构深度学习](2026-04-27-MCP协议生态与Agentic-RAG架构深度学习.md) - MCP 协议生态
- [2026-04-24-深入源码-Hermes-Agent-Self-Improving源码拆解](2026-04-24-深入源码-Hermes-Agent-Self-Improving源码拆解.md) - Hermes 架构
- [2026-05-01-AI-Agent记忆架构前沿学习](2026-05-01-AI-Agent记忆架构前沿学习.md) - 记忆系统设计
- [2026-05-03-AI-Agent-Protocol-Ecosystem-2026-学习](2026-05-03-AI-Agent-Protocol-Ecosystem-2026-学习.md) - Agent 协议生态
