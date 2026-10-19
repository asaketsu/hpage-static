# Google A2A 协议：多 Agent 协作标准

> 探索日期: 2026-05-19
> 来源: Google Cloud Next 2025 发布, IBM/DeepLearning.AI 联合课程, 150+ 组织支持

## 核心概念

**Agent-to-Agent (A2A)** 是 Google 2025年4月发布的开放协议，标准化 AI Agent 间通信。2026年4月满一周年，已获 150+ 组织支持（Google/Microsoft/AWS 三大云平台深度集成），移交 Linux Foundation 托管。

### 设计目标
- 解决跨框架 Agent 互操作性（crewAI/LangChain/ADK 等各自闭环）
- 标准化 Agent 发现、通信、协作流程
- 与 MCP 互补：MCP 管 Agent↔工具，A2A 管 Agent↔Agent

## 架构三要素

1. **Agent Card** — JSON 格式的 Agent 能力描述文件，通过 URL 可访问。类似 OpenAPI spec 但面向 Agent
2. **A2A Client** — 发起请求的 Agent（调用方）
3. **A2A Server** — 响应请求的 Agent（服务方）

### 通信协议
- 传输层: HTTP/HTTPS + **JSON-RPC 2.0**
- 支持三种模式: Request/Response、SSE 流式推送、异步 Push 通知
- 消息结构: Message → Parts（文本/文件/结构化数据）

## A2A vs MCP 定位

| 维度 | MCP | A2A |
|------|-----|-----|
| 方向 | Agent → 工具/数据 | Agent → Agent |
| 类比 | USB 接口 | 网络协议 |
| 关注 | 单 Agent 能力扩展 | 多 Agent 协作编排 |
| 互补 | 底层 | 上层 |

## 与 IBM ACP 合并

IBM 的 Agent Communication Protocol (ACP, 来自 BeeAI) 已与 A2A 合并，A2A 成为事实行业标准。DeepLearning.AI 联合 Google Cloud 和 IBM Research 推出免费课程。

## 实战案例：医疗多 Agent 系统

课程 Demo 架构：
- **QA Agent** (Claude on Vertex AI) → A2A Server
- **Health Research Agent** (Google ADK) → A2A Server
- **Sequential Chain Agent** (ADK) → A2A Server
- **Healthcare Provider Agent** (LangGraph + MCP) → A2A Server
- **Client** (Microsoft Agent Framework) → 调度各 Agent

关键洞察：**不同框架构建的 Agent 通过 A2A 协议无缝协作**，无需了解彼此内部实现。

## 关键技术细节

1. **Agent Card 是核心** — 类似于 Web Service 的 WSDL，描述 Agent 的能力、输入输出、认证方式
2. **任务生命周期** — 创建→执行→完成/失败，支持长时间运行任务
3. **安全模型** — 支持 OAuth/API Key 等认证，Agent 间通信可加密
4. **流式支持** — SSE 使 Agent 能实时推送进度（类似 LLM streaming）

## 对 Hermes 的启示

Hermes 当前的 delegate_task 是进程内子 Agent 模式，A2A 提供了跨进程、跨框架的标准化思路：
- Agent Card → 可借鉴为 Skill 的 self-description（已有 skill-vetter / agent-card-protocol skill）
- JSON-RPC → 可作为 exchange-protocol 的底层通信格式
- MCP + A2A 双栈 → 工具层用 MCP，协作层用 A2A

## 参考资料
- GitHub: github.com/a2aproject/A2A (Apache 2.0)
- 课程: deeplearning.ai/courses/a2a-the-agent2agent-protocol
- IBM: ibm.com/think/topics/agent2agent-protocol
- 一周年: prnewswire.com (2026-04-09, 150+ organizations)


## 相关笔记
