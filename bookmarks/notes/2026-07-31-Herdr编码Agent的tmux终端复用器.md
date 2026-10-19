# Herdr：编码 Agent 的 tmux——终端复用器

> **来源**: [herdr.dev](https://herdr.dev)
> **类型**: Agent Multiplexer（编码 Agent 终端复用器）
> **许可证**: 开源
> **平台**: Linux/macOS（稳定）+ Windows（preview beta）
> **无**: Electron / 账号 / 遥测 / Web 视图 / 托管控制面
> **日期**: 2026-07-31
> **标签**: `Herdr` `tmux` `Agent-Multiplexer` `CLI` `远程` `编码Agent` `终端`

---

## 核心结论

**Herdr is to coding agents what tmux is to terminals。** Herdr 是一个**编码 Agent 终端复用器（multiplexer）**——一个二进制文件（不是 App），在一个终端里管理所有编码 Agent（Claude Code / OpenCode / Codex 等）。Agent 在服务器上运行、SSH 远程附着、手机也能连、关闭笔记本后 Agent 继续跑。一眼看到哪个 Agent 在 blocked/working/done。

---

## 一、解决什么问题？

### 现有工具的缺陷

| 工具类型 | 问题 |
|---------|------|
| **tmux / Zellij** | 拥有持久终端会话，但**不理解 Agent**——不知道哪个窗口在 blocked/working/done |
| **桌面 Agent 应用** | 理解 Agent，但**绑死在一台有 GUI 的机器上**——无法远程 |
| **Worktree 编排器** | 远程项目，但**工作流自有**（不可被 Agent 自身编排） |

### Herdr 的定位

> tmux 和 Zellij 拥有持久终端会话但不理解 Agent。桌面 Agent 应用理解 Agent 但只活在一台机器上。**Herdr 在你的终端里保持复用器特性，同时让它对 Agent 感知。**

---

## 二、核心能力

### 2.1 终端内的 Agent 感知复用

```
┌─ herdr 终端 ──────────────────────────────────────┐
│                                                   │
│  spaces (侧边栏)                                   │
│  ├── herdr (master)                               │
│  ├── llm-proxy (master)                           │
│  └── qmp-auto/research                            │
│                                                   │
│  agents (分组)                          │
│  ● herdr      working · claude                    │
│  ○ explore    idle · opencode                     │
│  ● llm-proxy  blocked · claude  ← 需要审批         │
│  ● qmp        done · codex                        │
│                                                   │
│  [点击侧边栏 → 切换到对应 Agent 的真实终端 pane]    │
│                                                   │
└───────────────────────────────────────────────────┘

每个 Agent 运行在自己的真实终端 (PTY) 中
侧边栏一目了然: ●working / ○idle / ●blocked / ●done
```

### 2.2 三种使用模式

| 模式 | 场景 | 命令 |
|------|------|------|
| **local** | 本机，分屏/标签，关终端 Agent 继续跑 | `$ herdr` |
| **over SSH** | 在服务器上运行 Herdr，SSH 连入 | `$ ssh you@server` → `$ herdr` |
| **thin client** | 本地客户端连远程会话，自动装 Herdr，桥接剪贴板（含图片粘贴），保持你的快捷键 | `$ herdr --remote workbox` |

> 关键：**Agent 跑在服务器上（服务器在 Agent 关闭后保持存活），你从任何终端（含手机）附着**。桌面 Agent 管理器做不到这点。

### 2.3 移动端友好

> 手机/平板 SSH 连入时，终端变窄，Herdr 自动切换到**触屏尺寸的切换菜单**。

---

## 三、关键特性

| 特性 | 说明 |
|------|------|
| **不是终端模拟器** | 你的 Ghostty/Kitty/iTerm/Alacritty 不变——Herdr 在它里面运行 |
| **不是浏览器仪表盘** | 无 Web 视图、无账号、无托管控制面 |
| **持久 PTY 会话** | Agent 在真实终端里跑，detach 后继续 |
| **语义 Agent 状态** | blocked / working / done / idle——不只是"有输出" |
| **直接 Agent 附着** | 可直接附着到特定 Agent（tmux 做不到） |
| **Agent 可编排它** | Agent 自身可以编排 Herdr（tmux 仅可脚本化） |
| **150+ 社区插件** | [市场](https://herdr.dev/plugins)，可发布自己的 |
| **无遥测** | 无 Electron / 无账号 / 无遥测 |

---

## 四、与同类工具对比

| 能力 | tmux/Zellij | 桌面 Agent 应用 | Worktree 编排器 | **Herdr** |
|------|-------------|----------------|----------------|-----------|
| **运行在终端内** | ✅ | ❌ | ❌ | ✅ |
| **持久 PTY 会话** | ✅ | 有限 | 嵌入式 | ✅ |
| **远程 SSH 附着** | ✅ | 有限 | 远程项目 | ✅ |
| **语义 Agent 状态** | ❌ | 部分 | 工作区状态 | ✅ |
| **直接 Agent 附着** | ❌ | ❌ | ❌ | ✅ |
| **Agent 可编排它** | 可脚本化 | 部分 | 工作流自有 | ✅ |

---

## 五、安装

```bash
# Linux/macOS 稳定版
curl -fsSL https://herdr.dev/install.sh | sh

# Homebrew
brew install herdr

# Nix flake
# (见文档)

# Windows preview beta
irm https://herdr.dev/install.ps1 | iex
```

---

## 六、为什么不是 App？

| 维度 | 桌面 App（如 Cursor 内置 Agent 管理） | Herdr（二进制 multiplexer） |
|------|-------------------------------------|---------------------------|
| **离开机器** | ❌ 绑死在有 GUI 的机器 | ✅ Agent 跑在服务器，任何终端附着 |
| **SSH** | ❌ 无法 SSH | ✅ 手机 SSH 也能用 |
| **资源** | Electron 重 | 单二进制，极轻 |
| **账号** | 通常需要 | **不需要** |
| **编排** | 人操作 | **Agent 可编排它** |

> Agent 跑在"工作发生的地方"（服务器/Mac Mini/沙箱 VM），你从任何终端附着。

---

## 七、支持的编码 Agent

从首页 mock 可见支持：

| Agent | 状态 |
|-------|------|
| **Claude Code** | ✅（v2.1.198，含 Max/Fable 模式） |
| **OpenCode** | ✅（含 Zen 模式） |
| **Codex** | ✅（gpt-5.5 medium） |
| 其他 | 通过 PTY 可管理任意 CLI Agent |

---

## 八、使用场景

| 场景 | 怎么用 |
|------|--------|
| **多 Agent 并行开发** | 一个终端管 Claude Code + OpenCode + Codex |
| **远程开发** | Agent 跑服务器，笔记本关了继续跑 |
| **手机审批** | SSH 从手机连入，审批 blocked Agent |
| **服务器 CI/批量** | Agent 在服务器批量执行，Herdr 管理状态 |
| **Agent 自编排** | Agent 通过 Herdr API 编排其他 Agent |

---

## 九、社区评价

首页引用了三个独立评测：

| 来源 | 时长 | 评价 |
|------|------|------|
| **Jilles** | 6:37 | "Herdr in about 6 minutes"——最快实用入门 |
| **DevOps Toolbox** | 16:40 | "This Tmux 'Rewrite' Is Actually Brilliant"——深度 hands-on |
| **Better Stack** | 7:10 | "Is This the Ultimate Agent Multiplexer?"——tmux 对比 |

---

## 十、关键术语速查

| 术语 | 说明 |
|------|------|
| **Multiplexer** | 复用器——一个终端管理多个会话（如 tmux） |
| **PTY** | 伪终端，Agent 运行在真实 PTY 中 |
| **Attach/Detach** | 附着/分离——分离后会话继续 |
| **Agent State** | 语义状态：blocked/working/done/idle |
| **Thin Client** | 本地客户端连远程会话 |
| **Worktree Orchestrator** | 基于 git worktree 的多 Agent 编排器 |

---

## 十一、与现有笔记/项目的关联

| 关联项目 | 关系 |
|---------|------|
| **Kun 的 Pi Agent 配置** | Kun 管理多终端 Pi Agent 标签页的痛点，Herdr 正好解决——语义状态 + 一眼看清哪个 Agent 在工作 |
| **Agent Harness 知识体系** | Herdr 属于 Harness 层的"运行时管理"——管理多个 Agent Loop 的执行环境 |
| **学 Agent 正确顺序** | Phase 5（Multi-Agent）的实用工具——Herdr 让多 Agent 协同可观察可管理 |
| **BitBang CLI** | BitBang 解决"人到机器"远程访问，Herdr 解决"人到多个 Agent"管理——互补 |
| **Hermes Agent** | Hermes 的 delegate_task 管理子 Agent，Herdr 管理终端里的编码 Agent——不同层级的 multiplexing |
| **Qwen Audio Agent** | QAA 接入多个后台编码 Agent（Claude Code/Hermes 等），Herdr 可作为这些 Agent 的统一终端管理界面 |
