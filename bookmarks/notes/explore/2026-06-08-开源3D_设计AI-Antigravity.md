# Google Antigravity：Agent-First 开发平台深度调研

> 嗅探日期：2026-06-08 | 来源：HN(1088pts) + GitHub + Google Codelab + TinyFish

## 📋 摘要

**Google Antigravity** 是 Google 推出的 Agent-First IDE，2026年5月 I/O 大会发布 2.0 版本。它不是传统代码编辑器，而是一个以 AI Agent 为核心的"开发操作系统"——开发者通过高层任务指令驱动 Agent 团队自主完成编码、测试、浏览器验证等端到端工作流。配合 Google Stitch（设计生成工具）通过 MCP 协议桥接，实现了从设计稿到可运行代码的全自动化流水线。

## 🔑 关键发现

### 1. 产品定位：Agent-First IDE（非"又一个 VS Code"）

- 核心概念：开发者不再逐行写代码，而是以任务粒度指挥 Agent 团队
- 工作模式：Editor View（传统 IDE）+ Manager View（Agent 编排控制台）双视图
- Agent 能力：跨编辑器、终端、浏览器自主工作，执行端到端任务
- 2.0 更新：新增桌面应用 + CLI 工具，脱离浏览器运行

### 2. Stitch + Antigravity 联动工作流（Design-to-Code）

Google Codelab 披露了完整的自动化流水线：

1. **Stitch 生成设计**：用自然语言描述 UI，Gemini 3 生成高保真设计稿
2. **MCP 桥接**：Stitch 通过 MCP Server 将设计 Token 传递给 Antigravity
3. **Agent 自动实现**：Antigravity Agent 读取 Design DNA，自动生成 React/Tailwind 代码
4. **Vibe Check 验证**：内置浏览器对比设计与代码，像素级验证

这套流程的亮点在于 MCP 协议使设计工具和 IDE 之间的数据传递标准化。

### 3. 开源替代品：open-antigravity（501⭐）

- **仓库**：ishandutta2007/open-antigravity
- **定位**：通用 AI Gateway + Agent-First IDE 的开源实现
- **核心特性**：
  - 模型无关：支持 OpenAI/Claude/Gemini/Llama/Grok/Qwen 等所有主流 LLM
  - 多 Agent 协作：支持并行多 Agent 编码、测试、验证
  - 隐私优先：无数据外传，支持自部署
  - 基于 VSCodium 的 Editor View + Agent Manager 双视图
  - 容器原生架构：FastAPI Gateway + Docker Workspace Manager
- **技术栈**：TypeScript
- **状态**：早期社区项目，愿景宏大但仍在建设中

### 4. 社区反应（HN 1088pts 热帖）

- 正面：工作流有创新（Nano Banana → Mockup → Agent 编码 → 验证），MCP 标准化有价值
- 质疑："又一个 VS Code？"、"Google 产品两年后必被砍"（kill 文化担忧）
- 期待：Agent-First 范式确实代表了 IDE 的演进方向，但实现质量待验证

## 💡 对工作的价值

1. **MCP 协议实践参考**：Antigravity + Stitch 的 MCP 联动是 MCP 在设计-开发工作流的典型案例，可参考 Hermes 的 MCP 集成
2. **Agent 编排模式**：多 Agent 并行（编码+测试+验证）的编排思路，可借鉴到 Hermes 的 subagent 架构
3. **Design-to-Code 自动化**：Stitch → Design Token → 代码的流水线，是 AI 驱动前端开发的标准范式
4. **开源替代品跟踪**：open-antigravity 的模型无关 Gateway 思路值得持续关注

## 🎯 行动建议

1. **短期**：体验 Antigravity 2.0 的免费版，重点关注 MCP 集成方式和 Agent 编排 UI
2. **中期**：评估 open-antigravity 是否可作为 Hermes Agent 的 IDE 前端（模型无关 + 自部署）
3. **长期**：Design-to-Code 范式（Stitch 模式）可融入内容生产 Skill 链，实现"描述→设计→代码"全自动

## 相关笔记

- [2026-05-28-开源3D_设计AI-Antigravity.md](2026-05-28-开源3D_设计AI-Antigravity.md)
- [2026-06-05-开源3D_设计AI-Antigravity.md](2026-06-05-开源3D_设计AI-Antigravity.md)
- [2026-05-31-开源3D_设计AI-OpenSCAD+LLM.md](2026-05-31-开源3D_设计AI-OpenSCAD+LLM.md)
