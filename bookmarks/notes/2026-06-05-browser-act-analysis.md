# browser-act 项目分析笔记

## 项目概览

**browser-act/skills** 是一个专为 AI Agent 设计的浏览器自动化 CLI 工具集，GitHub 星标 1.9k，Fork 63。

### 核心定位

- **AI Agent 专用浏览器自动化 CLI**
- 突破反 bot 检测墙
- 支持人机协作（遇到验证码/交互挑战时转交人类）
- 并行多任务执行、独立多会话操作、隔离多账号浏览

---

## 技术架构

### 两层 Skill 架构

| 层级 | 名称 | 作用 |
|------|------|------|
| **静态层** | Entry Skill | 预置的常用网站操作模板（如登录、表单提交） |
| **动态层** | get-skills CLI | 运行时根据查询动态生成/检索 Skill |

### 三层反检测机制

1. **环境伪装**：浏览器指纹、User-Agent、Canvas 指纹等
2. **执行伪装**：模拟人类行为模式（鼠标移动、滚动、输入节奏）
3. **网络伪装**：代理支持、请求头伪造

### 多身份并发隔离

- 每个浏览器会话独立 Profile
- Cookie/Session 完全隔离
- 支持多账号并行操作

---

## 核心功能

### 1. 轻量级提取（Lightweight Extraction）

- 快速获取 JS 渲染内容
- 替代 WebFetch/curl
- 无需完整浏览器会话

### 2. 会话管理（Session Management）

- 多浏览器隔离
- 多账号并行操作
- 会话日志轮转

### 3. 验证协助（Verification Assistance）

- 遇到验证码时转交人类完成
- 仅上传验证码图片（不含 Cookie/页面内容）

### 4. 复杂交互（Complex Interaction）

- DOM 内容提取
- 截图
- 表单填写
- 文件上传

### 5. 人机协作（Human-Agent Collaboration）

- Headed 模式
- 远程协助手动步骤

### 6. 安全控制（Safety Controls）

- Confirmation Gate 协议
- 浏览器创建/删除/敏感操作需显式用户确认

---

## 安装方式

```bash
uv tool install browser-act-cli --python 3.12
```

**使用前必做**：
```bash
browser-act get-skills core --skill-version 2.0.2
```

> ⚠️ 不要跳过此步骤！它包含环境状态、可用浏览器、操作指令和完整交互流程。

---

## SKILL.md 关键信息

```yaml
name: browser-act
description: Browser automation CLI for AI agents.
version: "2.0.2"
install: "uv tool install browser-act-cli --python 3.12"
homepage: "https://www.browseract.com"
allowed-tools: Bash(browser-act:*)
```

### 权限声明

| 权限 | 说明 |
|------|------|
| 网络访问 | CLI 安装、可选验证协助 API（仅发送验证码图片） |
| 文件系统 | 浏览器 Profile、会话日志 |
| CDP 连接 | chrome-direct 类型需显式用户确认 |

### 数据隐私

- **本地处理**：Cookie、登录会话、页面内容、凭证、浏览器 Profile 数据全部本地存储处理
- **唯一外发数据**：仅验证码挑战图片（当调用 solve-captcha 时）

---

## 与 Hermes 内置浏览器工具对比

| 特性 | Hermes 内置浏览器 | browser-act |
|------|------------------|-------------|
| 反检测 | ❌ 无 | ✅ 三层反检测 |
| 多身份并发 | ❌ 单会话 | ✅ 多浏览器隔离 |
| 人机协作 | ❌ 无 | ✅ 验证码转交人类 |
| 网络捕获 | ✅ XHR/Fetch/HAR | ✅ DOM 提取（v2.0.2 替换） |
| 安装方式 | 内置 | `uv tool install` |
| Skill 系统 | Hermes Skills | 两层 Skill 架构 |

---

## 适用场景

### 推荐使用 browser-act 的场景

1. **反 bot 严格的网站**：需要突破检测墙
2. **多账号操作**：需要隔离的浏览器会话
3. **验证码处理**：需要人机协作
4. **复杂表单/流程**：需要完整的交互能力
5. **网络调试**：需要 XHR/Fetch/HAR 捕获

### 推荐使用 Hermes 内置浏览器的场景

1. **简单内容获取**：静态页面、无需 JS 渲染
2. **内部系统**：无反检测要求
3. **快速原型**：无需安装额外工具

---

## 项目结构

```
browser-act/skills/
├── .github/workflows/    # CI 同步工作流
├── browser-act/          # 核心 Skill (v2.0.2)
│   └── SKILL.md
├── browser-act-skill-forge/  # Skill 生成工具 (v1.0.6)
├── docs/                 # 文档
├── solutions/            # 解决方案示例
├── .gitignore
├── LICENSE
└── README.md
```

---

## 关键发现

### 1. 版本演进

- v2.0.2：用 DOM 提取替换网络捕获（隐私改进）
- 持续更新：最近提交在 4 小时前（2026-06-05）

### 2. Skill Forge

- `browser-act-skill-forge` 目录包含 Skill 生成工具
- 版本 1.0.6，支持从网站探索自动生成 Skill

### 3. 解决方案库

- `solutions/` 目录包含预置解决方案
- 最近添加：小红书用户资料（xiaohongshu-user-profile）

---

## 与 Hermes 集成建议

### 方案 A：作为外部工具调用

```bash
browser-act get-skills core
browser-act browser list
browser-act fetch <url>
```

### 方案 B：创建 Hermes Skill

基于 browser-act 的 SKILL.md 创建 Hermes Skill，实现：
- 统一的 Skill 管理
- 与 Hermes 其他工具联动
- 符合 Hermes 的安全协议

---

## 总结

browser-act 是一个功能强大的 AI Agent 浏览器自动化工具，核心优势在于：

1. **反检测能力**：三层反检测机制突破 bot 墙
2. **多身份隔离**：支持多账号并行操作
3. **人机协作**：验证码/交互挑战可转交人类
4. **隐私保护**：数据本地处理，仅验证码图片外发
5. **Skill 系统**：两层架构（静态 Entry + 动态 get-skills）

对于 Hermes Agent，建议：
- 简单场景使用内置浏览器工具
- 复杂/反检测场景集成 browser-act
- 可创建 Hermes Skill 封装 browser-act 调用

---

*分析时间：2026-06-05*
*来源：https://github.com/browser-act/skills*

## 相关笔记
- [BrowserAct-Skills分析](2026-06-05-BrowserAct-Skills分析.md)
