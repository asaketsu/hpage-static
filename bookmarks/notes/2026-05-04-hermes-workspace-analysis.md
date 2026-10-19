---
title: Hermes Workspace 项目实测分析
date: 2026-05-04
source: 微信公众号·极客BIM设计工坊
author: 朗朗晴空
url: https://mp.weixin.qq.com/s/0KKzrNrIGCJievPGbRlfXg
tags: [hermes, agent-ui, swarm,竞品分析]
---

# Hermes Workspace 项目实测分析

　　Hermes Workspace 是 NousResearch 出品的 Hermes Agent 官方 Web 工作区。将聊天、终端、内存浏览、技能管理、多代理调度全部集成到一个 Web 界面。仓库 github.com/outsourc-e/hermes-workspace，TypeScript，MIT 协议，2.8k Stars，最新版 v2.1.3。

## 项目画像

| 维度 | 数据 |
|------|------|
| 语言 | TypeScript |
| 协议 | MIT |
| Stars | 2,823（母项目 128k） |
| 贡献者 | 5人（主导 outsourc-e） |
| 最新版 | v2.1.3（2026-05-01） |
| 迭代节奏 | 11天3个版本 |

## 核心功能矩阵

1. 实时聊天 — SSE 流式连接，查看代理输出和工具调用
2. 终端集成 — 内嵌终端，实时查看命令输出
3. 内存浏览器 — 浏览/搜索/编辑三层记忆系统
4. 技能管理 — 查看/安装/编辑/搜索 2000+ 技能
5. Swarm Mode — 多代理编排+Kanban 任务板+角色路由+检查点审查
6. 8套主题 — Official/Classic/Slate/Mono 等，亮暗变体
7. PWA — Tailscale 远程访问
8. macOS 桌面版 — 529MB Electron 应用

## 架构演进

v2.0 从 fork 模式改为 zero-fork 架构，直接对接原版 Hermes Agent，不再需要自定义网关。这是一个重要的架构决策，降低了维护成本。

## 竞品定位

不是通用 AI 聊天界面，而是 Hermes Agent 的专属控制中心。竞品是：直接跑 CLI、用 hermes web、或自搭前端。优势在于可视化完整度和开箱即用。

## 借鉴分析

### 有价值（记入 Memory）

Swarm Mode 的 Kanban 任务板+角色路由+检查点审查模式，与我方 AGENTS.md 团队架构（ubot/Dev/OPM/Content/Data Meow）有对标价值。特别是检查点审查机制，可以增强我方 subtask-lifecycle skill。

### 知识库（仅笔记）

Workspace 完整功能矩阵是 Hermes 生态的重要参考，了解即可。

### 不落实

安装 Workspace 本身——我方以飞书+微信为交互层，通过 gateway 已实现多平台调度，不需要额外 Web UI。

## 文章质量

AI 生成的项目介绍文，本质是 README 的中文翻译+格式化整理。"实测"标题但缺乏实际使用体验。信息准确但无独立见解。适合作为项目信息的快速获取渠道，不适合作为深度评测参考。

## 预判

短期（1个月）：Stars 突破 5k，Swarm Mode 功能进一步完善。
中期（3个月）：成为 Hermes Agent 事实标准 UI，插件生态开始形成。
长期（半年）：可能被集成进 Hermes Agent 核心仓库，成为官方默认 UI。

## 关联

- [Hermes Agent](2026-04-13-hermes-agent-vs-openclaw.md)
- [[kanban-orchestrator]]
- [[AGENTS.md 团队架构]]


## 相关笔记
- [[hermes-memory-system-guide]] (关键词: hermes)
- [[2026-04-05-Hermes-Agent-competitor-analysis]] (关键词: hermes)
- [[2026-04-13-hermes-agent-vs-openclaw]] (关键词: hermes)
- [[2026-04-25-Hermes必配五套系统]] (关键词: hermes)
- [[hermes-agent-源码拆解自我进化机制]] (关键词: hermes)
