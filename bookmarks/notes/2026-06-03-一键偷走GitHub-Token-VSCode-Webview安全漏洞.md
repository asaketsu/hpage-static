# 一键偷走 GitHub Token：VSCode Webview 安全漏洞深度分析

> **来源**：Ammar Askar · ammaraskar.com · 2026-06-02
> **原文**：https://blog.ammaraskar.com/github-token-stealing
> **笔记ID**：vscode-github-token-stealing-20260603
> **格式**：双格式(MD + HTML) · 含借鉴进化点 · RAG/wiki联动
> **关联**：[[2026-05-21-Google-AI被SEO操纵的调查报告]] [[2026-05-23-Domain-Camouflaged-Injection-Attacks-域伪装注入绕过多Agent检测]]

## 摘要

安全研究员 Ammar Askar 发现了 VSCode 的 webview 安全边界漏洞，攻击者可通过一次点击（1-click）窃取用户的 GitHub OAuth Token，获取对用户所有仓库（包括私有仓库）的完整读写权限。漏洞利用链涉及 VSCode 的 postMessage 跨域通信机制、github.dev 的 OAuth Token 传递方式，以及 workspace trust 模型的缺陷。VSCode 团队已修复，但攻击思路对整个 Electron/Web 应用生态都有启示。

## 核心内容

### 1. 攻击面：github.dev
- GitHub 提供 github.dev 功能，将任意仓库在浏览器中用 VSCode Web 打开
- github.com 向 github.dev POST 一个 OAuth Token，赋予完整仓库操作权限
- Token 不限作用域——可以访问用户所有仓库，不限于当前浏览的仓库
- 这意味着：拿到 Token = 拿到用户所有 GitHub 仓库的读写权限

### 2. VSCode Webview 安全模型
- Webview 使用 `<iframe>` 沙箱隔离，origin 为 `vscode-webview://...`
- 主窗口 origin 为 `vscode-file://...`（桌面）或 github.dev 域（浏览器）
- 跨域隔离确保 webview 中的 JS 无法直接访问主窗口 API
- 通信只能通过 `Window.postMessage()` API

### 3. 漏洞核心：did-keydown 事件
- 为了让用户在 webview 内点击后仍能使用 Ctrl+Shift+P 等快捷键
- VSCode 在 webview 中注册了 `did-keydown` 事件处理器
- 攻击者可以通过构造特定的 postMessage 伪造键盘事件
- 通过命令面板执行恶意命令，安装恶意扩展
- 恶意扩展获取 GitHub Token 并发送到攻击者服务器

### 4. 攻击链
1. 诱导用户点击恶意链接（如恶意仓库的 github.dev）
2. 恶意 webview 通过 postMessage 触发命令面板
3. 安装 `.vscode/extensions` 中的本地恶意扩展
4. 扩展利用 VSCode API 访问 GitHub Token
5. Token 被发送到攻击者控制的远程服务器

### 5. Workspace Trust 缺陷
- github.dev 工作区默认被信任
- 受信任工作区可以直接安装 `.vscode/extensions` 中的扩展
- 没有额外的安全确认步骤

## 关键概念

| 概念 | 定义 |
|------|------|
| postMessage 沙箱 | 通过 iframe origin 隔离 + structured clone 通信的安全模型 |
| 1-Click Attack | 用户只需点击一个链接即可被攻击，无需其他交互 |
| Workspace Trust | VSCode 的信任模型，受信任工作区可执行更多特权操作 |
| OAuth Token Scope | Token 的权限范围，过大的 scope 是严重的安全风险 |

## 能力边界

1. 攻击需要用户主动点击链接（不是零点击）
2. 仅影响使用 github.dev 的场景
3. 需要 JavaScript 知识和 VSCode 内部机制理解
4. 漏洞已被修复（2026 年初）

## 最佳实践

1. Token 应最小化 scope——只授权当前仓库而非所有仓库
2. Webview 通信应白名单验证 message 来源和类型
3. 扩展安装应有额外的安全确认机制
4. 安全边界不应为了"用户体验"而妥协

## 🔍 借鉴学习进化点（必填）

| # | 点 | 原文要点 | 对当前系统的借鉴 | 行动计划 |
|---|-----|---------|---------------|---------|
| 1 | 最小权限原则 | GitHub Token 不限 scope，一个漏洞就泄露所有仓库权限 | Hermes 的 MCP tool 权限也应遵循最小权限原则 | 在 native-mcp skill 中增加 tool 权限审计步骤 |
| 2 | 消息来源验证 | postMessage 缺少 source origin 验证导致跨域攻击 | Agent 的 tool call 也需要验证"来源合法性"，防止 prompt injection 伪造工具调用 | 在 evolver 中增加 tool call source verification 规则 |
| 3 | 便利性 vs 安全 | 为了让快捷键在 webview 中工作，牺牲了安全边界 | Hermes 的 skill 自动执行也是便利与安全的权衡 | 在 skill-contracts 中增加危险操作确认清单 |
| 4 | Workspace Trust 模型 | github.dev 默认信任导致自动安装扩展 | Agent 的"上下文信任"模型也需要分层 | 在 hermes-agent config 中增加 workspace trust level 配置 |
| 5 | 攻击链分析思维 | 研究员展示的完整 kill chain 分析方法 | 可用于 Hermes 自身安全审计 | 在 auto-defense-check 中增加 kill chain 分析检查项 |

## 🔗 RAG / Wiki 联动

### 当前状态
- Agent 安全相关笔记已有 ULSPB 研究、域伪装注入等
- auto-defense-check skill 有基础安全检查
- native-mcp skill 有 MCP 安全配置

### 改进方案
1. 在 wiki-kb 中增加"Agent 安全漏洞"专题，系统整理已知攻击模式
2. auto-defense-check 增加 token scope 审计
3. 建立类似 VSCode webview 的 Agent 安全边界模型

### 已执行操作
- ✅ 笔记已生成
- ⏳ Wiki 安全专题待创建
- ⏳ auto-defense-check 增加新检查项


## 相关笔记

> 📌 笔记自动整理：待建立关联
