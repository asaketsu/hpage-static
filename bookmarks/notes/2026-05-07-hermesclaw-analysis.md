# HermesClaw 项目分析笔记

> 分析日期：2026-05-07 | 来源：https://github.com/AaronWong1999/hermesclaw

## 项目定位

HermesClaw 是微信 iLink 协议的多路路由代理，允许同一微信账号同时运行 Hermes Agent、OpenClaw、OpenCode 三个 AI 助手，通过 `/hermes` `/openclaw` `/opencode` `/both` `/three` 命令切换。

## 核心架构

- **唯一的 iLink 轮询者**：接管 iLink token，所有流量经 HermesClaw 路由分发
- **两个 HTTP 代理服务器**：Proxy A (:19999) → OpenClaw，Proxy B (:19998) → Hermes
- **一个 ACP 子进程桥接**：通过 JSON-RPC 2.0 over NDJSON 与 opencode acp 通信
- **单文件设计**：hermesclaw.py ~1,235 行 Python

## 关键技术点

1. **代理白名单**：只放行 6 个 iLink 端点，其他返回 404
2. **标签机制**：`/both` 和 `/three` 模式自动在消息前加 `[Hermes Agent]`/`[OpenClaw]`/`[OpenCode]` 标签
3. **OpenCode ACP 桥接**：subprocess stdin/stdout 管道通信，权限自动应答，死进程即时恢复
4. **媒体零处理**：不处理媒体解密，只转发原始 iLink 协议消息
5. **状态持久化**：router_state.json，支持 v1→v2 格式迁移

## 工程亮点

- 智能安装脚本 install.sh（669 行）：8 种情况自动检测、自动 Patch、systemd 服务
- 测试覆盖 117+ 用例：25 个路由矩阵参数化测试、ACP 权限应答、死进程恢复
- 被 Hermes Agent 官方 README Community 部分收录

## 局限性

- 依赖微信私有协议 iLink Bot API（无官方文档）
- 仅 Linux 完整支持（systemd 依赖）
- 无 Web UI、无数据库
- OpenCode 默认模型 minimax-m2.5-free

## 与我们系统的关系

- **互补关系**：我们用飞书通道，HermesClaw 解决微信多开问题
- **可借鉴**：代理路由模式、ACP 桥接设计、智能安装脚本思路
- **参考价值**：⭐⭐⭐ 中等（架构思路有价值，但通道不重叠）

## 可借鉴模式

1. **中间人路由模式**：作为唯一连接持有者，下游多实例通过代理接入 → 可类比我们的多平台消息路由
2. **ACP 协议桥接**：subprocess + JSON-RPC 2.0 over NDJSON → 我们 delegate_task 调用 Claude Code 已用类似模式
3. **智能安装脚本**：多路径检测 + 自动 Patch + systemd 生成 → 我们的 install/upgrade 流程可参考
4. **标签注入机制**：多路模式下自动标注来源 → 多 Agent 协作时可复用

## 相关笔记
- [[external-assistant]] — 外挂个人离线AI助理
- [[Auto-Dream]] — Auto-Dream 自动梦境项目
