# 米谋 (mimofan) — Rust 终端 AI 编程助手

> GitHub: https://github.com/XiaomingX/mimofan
> ⭐ 11 stars | 462 commits | Rust 实现 | MIT 协议
> 最新版本 v0.0.17 | 最新提交 1 小时前（极度活跃）

## 一句话定位

**对标 Claude Code / OpenCode 的开源终端 AI 编程助手，Rust 实现，默认小米 MiMo 模型，兼容 DeepSeek/OpenAI/通义千问。** 差异化：本地优先 · MIT 协议 · 默认 MiMo。

## 核心架构

| 维度 | 说明 |
|------|------|
| **语言** | Rust（原生编译，零运行时依赖） |
| **核心循环** | 模型决策 → 工具执行 → 结果回灌 → 再决策（经典 Agent Loop） |
| **Provider 模式** | 三种：`openai-compatible` / `anthropic-compatible` / `gemini-compatible` |
| **默认模型** | 小米 MiMo（mimo-v2.5-pro），开箱零配置 |
| **包管理** | Cargo（Rust）+ Bun（JS 侧脚本） |
| **覆盖率** | 验收测试覆盖率 99%（`benchmark_to_test.md`） |

### 项目结构亮点

```
crates/           ← Rust workspace 多 crate 架构
config/           ← 配置管理（含 CostBudget 成本上限告警）
benchmark/        ← 性能评测框架
evals/            ← 评测指标体系（MECE 基准框架）
integrations/     ← 外部集成
.claudeignore     ← AI 上下文忽略（支持 Claude/Cursor/Windsurf 三种格式）
```

### 关键文档（项目根目录）

| 文档 | 内容 |
|------|------|
| `ARCHITECTURE_CN.md` | 中文架构说明 |
| `ARCHITECTURE_IMPROVEMENT_PLAN.md` | 架构改进计划（含「代码为准」核对纪律） |
| `MEMORY_MECHANISM_COMPARISON.md` | 记忆机制对比分析 |
| `PROVIDER_MODES_ANALYSIS.md` | Provider 模式分析 |
| `EVAL_METRICS.md` | 评测指标体系 + 竞品对比 |

## 核心能力

### 1. 多模型支持

| 服务商 | 模型 | Provider 配置 |
|--------|------|--------------|
| **小米 MiMo** | mimo-v2.5-pro | 默认（`openai-compatible`） |
| Anthropic | claude 系列 | `anthropic-compatible` |
| DeepSeek | deepseek-v4-pro / flash | `openai-compatible` |
| 通义千问 | qwen-max | `openai-compatible` + dashscope |
| OpenAI | gpt-4 系列 | `openai-compatible` |

### 2. 操作模式

| 模式 | 说明 |
|------|------|
| 交互模式 | 全屏 TUI 终端界面 |
| 单次模式 | `mimofan exec "指令"` 命令行直接调用 |
| Plan 模式 | 先列计划，审核后再执行 |
| YOLO 模式 | 全自动执行（信任仓库时使用） |

### 3. 高频场景

- **Bug 修复**：给报错信息 → 自动分析→修复→写测试→跑验证
- **代码重构**：拆分大函数→保持功能不变→跑测试防回归
- **单元测试**：读函数签名→生成测试用例→添加 mock/fixture
- **代码审查**：读 diff → 分析安全和性能问题 → 改进建议
- **文档生成**：分析模块结构→提取公开 API→生成文档

## 差异化亮点（值得学习的设计）

### 🔥 Spec Freeze（计划冻结）

```text
> /freeze 只修复登录页面的 bug，不要改动其他模块
```

**防止 Agent 偏离既定计划**——Agent 严格在冻结范围内工作，任何越界操作需要用户确认。这解决了一个真实痛点：AI 编程 Agent 容易「改着改着就跑偏了」。

### 🔥 Issue Monitor（Issue 监控）

```text
> /monitor create fix-auth --issues 123,456 --repo owner/repo
```

监控 GitHub Issue 状态变化，自动创建或更新关联 PR。实现 Issue → PR 的自动化闭环。

### 🔥 /compact 自定义指令

```bash
/compact 重点保留认证重构的决策，测试调试过程可以省略
```

**上下文压缩时可指定保留重点**，而非盲目摘要。支持 AGENTS.md 中的 `# Compact Instructions` 段落做常驻配置，命令行临时指令优先级更高。

### 🔥 其他值得关注

| 功能 | 说明 |
|------|------|
| **CostBudget** | 成本上限阈值告警（`config/` 下），闭环 #620 |
| **Memory Consolidation** | 记忆整合模块 + MemoryEntry 重要性评分（最新正在开发，#716） |
| **Telemetry** | mimofan-telemetry crate，OTel 桥接（feature-gated） |
| **Sub-agents** | 并行子智能体处理复杂任务 |
| **Fleet** | 舰队管理（多 Agent 编排） |
| **MCP 支持** | Model Context Protocol 集成 |

## 完整斜杠指令表

### 基础指令

| 指令 | 说明 |
|------|------|
| `/help` `/clear` `/exit` | 常规 |
| `/model` | 切换模型 |
| `/provider` | 切换服务商 |

### 模式切换

| 指令 | 说明 |
|------|------|
| `/plan` | 进入规划模式 |
| `/auto` | 自动模式 |
| `/yolo` | 全自动模式 |
| `/fast` `/normal` | 快速/恢复正常 |

### 代码管理

| 指令 | 说明 |
|------|------|
| `/freeze` `/unfreeze` | 冻结/解冻计划 |
| `/stash` | 暂存更改 |
| `/anchor` | 设置锚点 |

### 任务管理

| 指令 | 说明 |
|------|------|
| `/monitor` | Issue 监控 |
| `/subagents` | 子智能体 |
| `/fleet` | 舰队管理 |

### 上下文管理

| 指令 | 说明 |
|------|------|
| `/compact` | 压缩上下文（可附带自定义指令） |
| `/context` | 查看上下文用量分布 |
| `/purge` | Agent 外科式清理上下文 |
| `/tokens` | 查看 token 统计 |

## 快速上手

```bash
# 安装
cargo install --path crates/tui --locked
# 或下载预编译二进制

# 零配置启动（小米 MiMo）
export XIAOMI_MIMO_API_KEY="你的key"
mimofan

# 单次指令模式
mimofan exec "帮我写一个正则表达式匹配邮箱"

# 系统诊断
mimofan doctor
```

## 💡 对 Hermes Agent 的借鉴分析

### ✅ 我们已有的

| mimofan 功能 | Hermes 对标 |
|--------------|-------------|
| Agent Loop（决策→执行→回灌→再决策） | ✅ 核心循环一致 |
| 多 Provider 支持 | ✅ config.yaml providers |
| 上下文压缩 /compact | ✅ session 管理 + context 压缩 |
| CostBudget 成本告警 | ✅ zhipu-quota-monitor |
| Sub-agents | ✅ delegate_task |
| MCP 支持 | ✅ native MCP client |

### 🔥 值得借鉴的设计

| mimofan 设计 | 对 Hermes 的启发 | 实施难度 |
|--------------|-----------------|---------|
| **Spec Freeze 计划冻结** | 我们的 `steer-hook` skill 有类似概念，但 mimofan 的 `/freeze` 更工程化——直接约束 Agent 的操作范围。可在 Hermes 中实现 skill 级 freeze guard | 中 |
| **/compact 自定义指令** | 压缩时保留重点的能力，我们目前是全量压缩。可在 session 压缩逻辑中加入用户自定义保留关键词 | 中 |
| **Memory Consolidation + 重要性评分** | MemoryEntry 重要性评分字段——我们的 memory-refiner skill 做记忆精炼，但没有显式评分。可借鉴打分模型 | 中 |
| **AGENTS.md Compact Instructions** | 项目级压缩指令常驻配置——我们的 AGENTS.md 可增加 `# Compact Instructions` 段落 | 低 |
| **Rust 原生实现** | Hermes 是 Python，性能瓶颈在 Gateway 层。如果未来要重构核心循环，Rust 是值得考虑的方向 | 高（不现实） |
| **多 AI 工具 ignore 兼容** | `.claudeignore` + `.cursorignore` + `.windsurfignore` 三格式——我们的 Hermes 没有统一的 ignore 机制 | 低 |
| **MECE 评测框架** | evals/ 目录 + MECE 基准——我们有 skill-stress-test 但不够系统化 | 中 |
| **多 AI 协作文件（CLAUDE.md / CODEBUDDY.md）** | 同时兼容多种 AI 工具的项目约定文件 | 低 |

### 📊 关键差异

| 维度 | mimofan | Hermes Agent |
|------|---------|--------------|
| **定位** | 终端 AI 编程助手（coding-first） | 全能 AI Agent（多场景） |
| **语言** | Rust | Python |
| **平台** | 终端 TUI | 飞书/微信/CLI 多平台 |
| **语音** | ❌ | ✅ STT + TTS + 克隆 |
| **Cron** | ❌ | ✅ 完整调度系统 |
| **技能系统** | ❌ | ✅ 300+ Skills |
| **多 Agent** | Sub-agents + Fleet | delegate_task + cron 编排 |
| **记忆** | 开发中（consolidation） | ✅ L1/L2/L3 三级记忆 |

## 趋势判断

1. **终端 AI 编程助手赛道正在爆发**：Claude Code / OpenCode / Aider / Cursor CLI / mimofan——都在做「终端内 Agent Loop」范式
2. **Rust 正在成为 Agent 工具的首选语言**：性能 + 安全 + 单二进制分发，相比 Python 有分发优势
3. **国产模型生态分化**：mimofan 默认小米 MiMo，说明国产大模型已有足够质量支撑 coding agent 场景
4. **Spec Freeze 是关键创新**：解决 AI Agent 越界操作这个核心痛点，所有 coding agent 都需要
5. **成本管理成为标配**：CostBudget + token 统计 + 上下文压缩，成本控制是 Agent 工程化的必修课

## 关联

- → 相关：Claude-Code-源码泄露深度分析.md
- → 相关：agent-primitive-architecture（Agent 三原语架构）
- → 相关：context-engineering-patterns（上下文工程四大支柱）

## 相关笔记

- [Claude Code 源码泄露深度分析](../../explore/2026-08-05-claude-code-source-leak-analysis.md) — 同类终端编程 Agent 的架构剖析
- [Herdr 编码Agent tmux终端复用器](./2026-07-31-Herdr编码Agent的tmux终端复用器.md) — 终端 Agent 工程实践
- [脚手架比接口更重要 MCP vs CLI](./explore/2026-08-12-脚手架比接口更重要-MCP-vs-CLI对照实验.md) — Agent 工具调用成本分析，终端 Agent 相关
