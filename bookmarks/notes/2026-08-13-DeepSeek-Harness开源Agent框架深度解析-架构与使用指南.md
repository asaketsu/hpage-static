# DeepSeek Harness（dsh）开源 Agent 框架深度解析：架构与使用指南

> 检索日期：2026-08-13 | 来源：GitHub deepseek-ai/deepseek-harness（12.3k⭐）、官方文档、TeamoRouter 分析

---

## 一、核心结论

**DeepSeek Harness（`dsh`）** 是 DeepSeek AI 开发的开源 Agent Harness（智能体框架），目标是把裸模型的原始智能转化为可靠、可控、可大规模运行的 Agent 能力。直接竞品是 Claude Code。

- **关键定位**：2026 年 3 月开始内部开发，7 月 31 日随 DeepSeek-V4-Flash 发布首次公开亮相——旗舰 Agent benchmark 用 dsh 极简模式跑出，证明真实 Agent runtime 已经存在
- **核心哲学**：**一切皆插件（everything is a plugin）**——模型适配器、工具注册表、会话日志、甚至 Agent 循环本身都是插件，全部可从配置替换
- **底层框架**：[Cordis](https://github.com/cordiverse/cordis)，一个基于"时空可组合性编程范式"论文设计的插件框架
- **许可证**：MIT（模型与代码分离许可）
- **状态**：开发者预览（developer preview），明确警告"会有破坏兼容性的变更"

---

## 二、快速上手

### 2.1 通过 npm 一行启动（推荐）

```bash
# 需要 Node.js 22.19+ 或 24+
npx @deepseek-ai/dsh web
```

启动后默认在 `http://127.0.0.1:3080` 提供 Web UI。

### 2.2 使用步骤

1. **配置模型**：Settings → Models → 输入 DeepSeek API key → Save（也支持其他 OpenAI 兼容端点）
2. **选择工作区**：Choose workspace → 添加项目目录 → 选中
3. **运行任务**：新建会话，发送任务，Agent 可以读写文件、执行命令、委派子任务、维护计划

### 2.3 从源码构建

```bash
git clone https://github.com/deepseek-ai/deepseek-harness.git
cd deepseek-harness
pnpm install          # pnpm@11.7.0, 需要 Corepack
pnpm run build        # tsc + tsdown 构建
pnpm dsh web          # 启动 Web UI
```

**前置条件**：Node.js 22.19+ 或 24+；pnpm 11.7.0+（通过 Corepack）；Git 2.26+

### 2.4 Headless 模式（一次性任务）

```bash
# 需要 DEEPSEEK_API_KEY
pnpm dsh --profile headless "summarize this workspace"
```

### 2.5 关键环境变量

```bash
DEEPSEEK_API_KEY=sk-...
DEEPSEEK_BASE_URL=https://...   # 可选，默认官方 API
```

---

## 三、架构深度解析

### 3.1 Cordis 框架：五大核心理念

Cordis 是 dsh 的插件框架根基，设计理念来自论文 [A Programming Paradigm for Spatiotemporal Composability](https://github.com/cordiverse/paper)：

| 理念 | 说明 |
|------|------|
| **插件即 Service 对象** | 可以是带 `inject`/`apply(ctx)` 的函数，或 `Service` 子类，生命周期由 Cordis 挂载到当前上下文 |
| **上下文即服务仓库** | 服务通过 `ctx.tools`、`ctx.llm` 等稳定 key 声明，其他插件通过 key 查找而非导入具体实现 |
| **声明式依赖注入** | 插件通过 `inject` 声明所需服务，Cordis 等待依赖就绪——加载顺序通过依赖关系表达，无需手动排序 |
| **类型化事件通信** | 服务通过 TypeScript declaration merging 声明事件名，按 dispatch mode 分发 |
| **注册是可逆 effect** | 所有注册（prompt 段、工具 schema、适配器）通过 `ctx.effect()`/`ctx.on()` 安装，卸载时自动回滚 |

### 3.2 四种事件分发模式

| Mode | 是否 await | 执行顺序 | 有返回值 | 典型场景 |
|------|-----------|---------|---------|---------|
| `emit` | 否 | 注册顺序 | 否 | 观察者：记录日志、广播通知 |
| `waterfall` | 否 | 注册顺序 | 是 | 拦截器/中间件：包装请求、策略拦截 |
| `parallel` | 是 | 全部并行 | 否 | 扇出：多提供者同时执行 |
| `serial` | 是 | 注册顺序 | 是 | 顺序决策：审计链 |

**Waterfall 语义**：around-middleware，监听器收到 `(...args, next)`。调 `next()` 委托给下游；不调 `next()` 则短路。单决策事件可以不调 `next()` 来 short-circuit。

### 3.3 Profile 与 Bundle 层叠架构

```
[Profile] ─ 命名组合，存储在 Harness home
  ├── [Bundle] ─ Cordis config rows + 代码的分发格式
  │   ├── dsh-base     → 第一层：模型适配器、工具、持久化、沙箱、审批策略、设置、凭据
  │   ├── dsh-web-app  → 浏览器应用
  │   └── dsh-headless → 一次性 runner（无服务器）
  ├── profile/cordis.patch.yml  → profile 级补丁
  ├── home/cordis.patch.yml     → home 级补丁
  └── --patch overlay           → 命令行覆盖
```

**层叠规则**：每层依次应用到空 entry list 上。上层补丁可通过 id 替换整行 config 或插入新行。

```bash
# 查看实际启动的插件树
dsh --profile web --dump-config
```

### 3.4 核心子系统

| 包名 | 职责 | ctx key |
|------|------|---------|
| `core/session` | 只追加的 `SessionEvent` 日志 + 内存存储 | `ctx.sessions` |
| `core/system-prompt` | Prompt 段组装 + 工具 schema 汇编 | `ctx.systemPrompt` |
| `core/tools` | 作用域工具注册表 + 受保护执行管线 | `ctx.tools` |
| `core/agent` | `Agent` 接口 + 实时注册表 + `agent/*` 事件 | `ctx.agents` |
| `core/agent-loop` | 默认驱动器（实现 Agent 接口） | `ctx.agentLoop` |
| `core/scope` | 每 Agent 作用域注册原语 | 库，无 key |
| `llm/llm` | 消息/流词汇 + 适配器接缝 | `ctx.llm` |

### 3.5 Turn 流程（Agent 执行循环）

```
turn/start
  claim next-step input + queued message
  assemble prompt sections + tool schemas
  → agent/pre-step (reject | enter)
    step/start
      append entered messages
      derive model history from log
      agent/request → llm/stream → assistant/chunk* → assistant/message
      tool/call* → tools/pre-execute → tools/execute → tools/post-execute → tool/result*
    step/end
    (tools owe another request | next-step input arrived → next step)
  → agent/turn-stopping
turn/end
```

**Step** = 一次模型请求 + 调用的工具。**Turn** = 零或多个 step，在首次 input 被领取前打开，在无待处理时关闭。

### 3.6 会话日志：Model-visible ⟺ Logged

**铁律**：凡是到达模型请求的任何内容，都必须能从会话日志重建。运行时不变量会断言这一点。这就是为什么新的模型可见输入需要新的 SessionEvent——扩展 `SessionEventMap` 并从日志渲染。

### 3.7 Capability Seams（能力接缝）

一个完整的 capability seam 包含三个角色：

| 角色 | 职责 |
|------|------|
| **Service Definition** | 声明接口 |
| **Service Provider** | 实现接口 |
| **Consumer** | 使用接口（通常是模型面向工具） |

一个角色不构成 seam——只有三个角色齐全才算。**换一个 Provider 就改变整个产品行为**：例如把文件系统和子进程 provider 指向远程沙箱，Bash、PTY、LSP 都会跟着迁移，无需 provider 分叉。

### 3.8 扩展点速查表

| 目标 | 机制 |
|------|------|
| 添加模型 provider | `ctx.llm` 注册适配器 |
| 添加模型面向的能力 | `ctx.tools` 注册；schema 自动加入 prompt 组装 |
| 给某个会话不同能力集 | compose agent preset；service row 加 `isolate` realm |
| 添加 shell 执行 | `ctx.shell` backend；本地版通过 `ctx.subprocess` |
| 拦截请求/工具/turn | `agent/*` 或 `tools/*` 事件 |
| 添加模型面向上下文 | `agent.inject()`——下次请求生效 |
| 添加持久终端 | `ctx.terminals` backend + `dsh-tool-terminal` |
| Fork 会话 | `ctx.sessions.fork(source, boundary?, childSessionId?)` |

---

## 四、内容整理：项目全貌

### 4.1 仓库结构

| 目录 | 内容 |
|------|------|
| `packages/core/` | 产品 API 脊柱：session、system-prompt、tools、agent、agent-loop |
| `packages/llm/` | LLM 能力：Service Definition + DeepSeek providers |
| `packages/shell/` | Bash 能力：Service Definition + local/pwsh providers |
| `packages/subprocess/` | 子进程能力 + 本地进程树 provider |
| `packages/terminal/` | 持久终端会话 |
| `packages/fs/` | 文件系统能力 + 策略 |
| `packages/lsp/` | 语言服务器能力 |
| `packages/skill/` | Skill provider 注册表 + catalog/loader |
| `packages/web/` | Web 能力：search/fetch providers |
| `packages/subagent/` | Subagent 能力：delegation Consumers |
| `packages/bundle/` | 可安装的 dsh --profile patch-layer bundles |
| `packages/e2b/` | E2B 沙箱 POC |
| `packages/compaction/` | 上下文压缩能力 |
| `packages/context/` | 请求上下文插件 |
| `packages/workflow/` | 工作流能力 + worker-thread provider |
| `packages/plan/` | Plan mode as logged state |
| `packages/preset/` | 每 session agent 组合 |
| `packages/guard/` | Loop-hygiene + tool-timeout 插件 |
| `packages/self-modification/` | Agent 检查/挂载自己的插件 |
| `packages/hooks/` | Claude Code/Codex hook 桥接 |
| `packages/session/` | 持久会话数据 |
| `packages/sdk/` | JSON-RPC 协议 + 服务器 + TypeScript 客户端 |
| `python/` | Python SDK + 运行时 |
| `vendor/` | Vendored Cordis 源码 |
| `.agents/` | Agent 工作流和 Agent Notes |

### 4.2 技术栈

- **语言**：TypeScript（ESM everywhere，`"type": "module"`）
- **构建**：tsc + tsdown
- **包管理**：pnpm workspaces
- **测试**：Vitest（单元 + e2e + snapshot）
- **Lint**：Oxlint
- **Hook**：Lefthook
- **文档**：VitePress
- **Node 要求**：22.19+ 或 24+

### 4.3 开发命令

```bash
pnpm install              # 安装依赖
pnpm run typecheck        # 类型检查
pnpm run test             # 单元测试
pnpm run test:e2e         # 真实 API 测试（需要 DEEPSEEK_API_KEY）
pnpm run test:snapshot    # ACP/headless 回放测试
pnpm run build            # 构建
pnpm run hygiene          # knip + publint + workspace 约束
pnpm run doc-sync         # 文档同步检查
pnpm run website:build    # VitePress 构建
```

### 4.4 与 Claude Code 的对比定位

DeepSeek Harness 的战略目标明确——与 Claude Code 竞争编程 Agent 产品。DeepSeek 2026 年 5 月公开招聘了 Agent Harness 产品经理和研发工程师岗位。团队技术核心包括来自 Jane Street（9 年）和 TSY Capital 的量化交易背景成员。

关键差异点：
- **成本**：dsh 的设计论点是"Agent 应该便宜到可以大规模运行"——依托 DeepSeek 自有低成本 API
- **架构开放度**：一切皆插件，连 Agent 循环都是可替换的
- **Cordis 理论基础**：有学术论文支撑的时空可组合性编程范式

---

## 五、查询拓展

1. **Cordis "时空可组合性编程范式"论文具体内容**——[github.com/cordiverse/paper](https://github.com/cordiverse/paper)，理解 waterfall/serial/parallel 四种 dispatch mode 在时空维度的设计动机
2. **DeepSeek-V4-Flash 极简模式 benchmark 具体分数**——7 月 31 日公布的旗舰 Agent benchmark 的详细指标（SWE-bench 等）
3. **Python SDK 的完整 API**——`docs/user/guide/python-sdk.md` 中的 JSON-RPC 协议细节
4. **与 Hermes Agent 的架构对比**——两者都是插件化 Agent 框架，Cordis vs Hermes 的 Skill/Hook/Memory 三原语体系有何异同
5. **ACP（Agent Client Protocol）**——dsh 内置了 ACP 服务器，与 MCP 的关系和差异
6. **Self-modification 包的实现**——Agent 检查/挂载自己插件的安全边界和机制

---

## 六、归纳总结

DeepSeek Harness 的核心价值主张可以归纳为一句话：**把 Harness（让裸模型变成可靠 Agent 的工程层）做成一切皆插件的开放平台**。

| 维度 | 设计选择 | 竞品对比 |
|------|---------|---------|
| 插件架构 | Cordis 四模式事件 + 可逆注册 + capability seam | Claude Code: 闭源，无插件扩展 |
| 模型绑定 | 默认 DeepSeek 但支持任意 OpenAI 兼容端点 | Claude Code: 绑定 Anthropic 模型 |
| 成本策略 | 依托 DeepSeek 低成本 API，面向大规模运行 | Claude Code: 按量付费，成本高 |
| 会话模型 | 只追加事件日志 = 事实来源，可重建 | 类似设计但实现细节不公开 |
| 工具系统 | ctx.tools 注册表 + waterfall 执行管线 | 闭源工具系统 |
| 开放性 | MIT 许可 + 完整文档 + 双语 | 闭源 |

**最值得借鉴的架构思想**：
1. **Capability Seam 三角色完整性**——Service Definition / Provider / Consumer 缺一不可，换 Provider 即换产品
2. **Model-visible ⟺ Logged** 不变量——所有模型可见输入必须可从日志重建
3. **Profile/Bundle 层叠**——通过补丁层而非修改源码来定制行为
4. **四种事件 dispatch mode**——emit/waterfall/parallel/serial 各司其职，waterfall 的 around-middleware 语义尤其优雅

---

## 七、趋势判断

1. **Harness 工程化是 Agent 从 demo 走向生产的必经之路**：Anthropic 在 2025 年末至 2026 年初提出 Harness 概念，DeepSeek 快速跟进开源实现——说明行业共识已形成：裸模型 ≠ Agent，需要系统化的记忆/代码执行/工具调用/终止逻辑工程层
2. **"一切皆插件"正在成为 Agent 框架的主流范式**：dsh、Hermes Agent、LangGraph 等框架都在走向插件化/模块化，区别在于实现深度——dsh 把 Agent 循环本身都做成了插件
3. **Cordis 的学术化设计值得关注**：将"时空可组合性"作为编程范式论文来指导框架设计，这在 Agent 领域罕见，可能代表了 Agent 框架从工程实践走向理论化的早期信号
4. **成本战可能重塑编程 Agent 市场格局**：DeepSeek 的低成本 API + 开源 Harness 组合，可能对 Claude Code/Cursor 等收费产品形成价格压力
5. **2026 下半年 Agent 框架将进入快速洗牌期**：dsh 当前明确处于 developer preview，频繁 breaking change，但 12.3k⭐ 说明社区关注度极高

---

## 八、关联分析

本笔记属于 AI Agent 工程化领域。客观行业信号如下，不做强行关联：

- **对 Agent 框架设计实践的参考价值**：dsh 的 Capability Seam 三角色模型和 Model-visible ⟺ Logged 不变量，是高质量 Agent 工程实践的参考案例。Cordis 的四模式事件分发系统在复杂 Agent 编排场景下比简单的 hook 机制更表达力强
- **对 Harness 架构模式的验证**：Anthropic 提出的 Harness 概念（工具/记忆/子 Agent 编排/终止逻辑）在 dsh 中全部落地为独立包——fs/shell/subprocess/terminal/subagent/session/plan——验证了这一架构划分的工程可行性
- **Cordis vs Hermes Skill/Hook/Memory 三原语**：两者都是插件化设计但抽象层级不同。Cordis 更底层（Service Definition + 事件分发），Hermes 更高层（Skill 文件 + Hook 钩子 + Memory 存储）。各有适用场景

---

## 九、出处

| 来源 | 链接 |
|------|------|
| GitHub 仓库 | https://github.com/deepseek-ai/deepseek-harness |
| 官方 README（中文） | https://github.com/deepseek-ai/deepseek-harness/blob/master/README.zh.md |
| 架构文档 | https://github.com/deepseek-ai/deepseek-harness/blob/master/docs/architecture.md |
| Cordis Primer | https://github.com/deepseek-ai/deepseek-harness/blob/master/docs/cordis-primer.md |
| AGENTS.md | https://github.com/deepseek-ai/deepseek-harness/blob/master/AGENTS.md |
| 开发指南 | https://github.com/deepseek-ai/deepseek-harness/blob/master/docs/development.md |
| Web UI 指南 | https://github.com/deepseek-ai/deepseek-harness/blob/master/docs/user/guide/index.md |
| Cordis 框架 | https://github.com/cordiverse/cordis |
| Cordis 论文 | https://github.com/cordiverse/paper |
| TeamoRouter 分析 | https://teamorouter.com/blogs/deepseek-harness-agent-framework |
| 36氪报道 | https://eu.36kr.com/en/p/3818407956366208 |

## 相关笔记
- [DeepSeek-Harness迁移笔记-Hermes老手艺8组对照](2026-08-16-DeepSeek-Harness迁移笔记-Hermes老手艺8组对照.md)
- [deepseek-agent-ecosystem](2026-05-01-deepseek-agent-ecosystem.md)
- [DeepSeek-V4-开源模型新格局](2026-05-10-DeepSeek-V4-开源模型新格局.md)
- [DeepSeekHarness二十万行拆解-单文件学习网站与Agent工程可视化](2026-08-18-DeepSeekHarness二十万行拆解-单文件学习网站与Agent工程可视化.md)
