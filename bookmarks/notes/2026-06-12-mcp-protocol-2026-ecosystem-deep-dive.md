# MCP 协议 2026 生态全景：从工具集成到协作框架

> 学习日期：2026-06-12 | 来源：Digital Applied, WorkOS Blog, MCP 官方规范
> 标签：MCP / 工具集成 / AI Agent / 协议设计 / 生态系统

---

## 一、核心发现

### 1. MCP 已成为 AI-工具连接的事实标准

关键数据（2026 年 5 月验证）：

- **月 SDK 下载量**：9700 万+（Python + TypeScript 合计）
- **公开 MCP Server**：10,000+（Anthropic 官方数据）
- **官方注册表条目**：9,652（最新版本） / 28,959（含历史版本）
- **GitHub `mcp-server` 主题仓库**：15,926 个
- **主仓库 Star**：86,148（`modelcontextprotocol/servers`）
- **企业采用率**：41% 已在生产环境使用（29% 有限生产 + 12% 广泛生产）

2025 年 12 月，Anthropic 将 MCP 捐赠给 **Linux 基金会下的 Agentic AI Foundation**，成为厂商中立、社区治理的开放标准。

### 2. 架构演进：从工具执行到协作框架

MCP 已从单纯的「AI 调工具」协议演变为**完整的协作框架**：

| 能力 | 说明 |
|------|------|
| **Tools** | AI 可执行的操作（发送消息、创建记录、触发部署）——写端 |
| **Resources** | AI 可读取的数据（文件、DB 行、API 响应）——读端 |
| **Prompts** | 可复用的提示模板，引导 AI 完成特定任务 |
| **Sampling** | Server 可请求 AI 模型生成内容（用户可审查/编辑） |
| **Elicitation** | Server 暂停执行，向用户请求输入（URL 模式/表单模式） |
| **Async Tasks** | 「立即调用，稍后获取」模式，支持长时任务 |
| **MCP Apps** | 工具可返回富 HTML 界面，在聊天中渲染（iframe 沙箱） |

关键突破：**MCP Apps（2026 年 1 月）**，与 OpenAI 联合开发，工具可以返回交互式 HTML 界面。首发合作伙伴包括 Amplitude、Asana、Box、Canva、Figma、Slack、Salesforce 等。

### 3. 传输层简化：Streamable HTTP 替代 SSE

| 传输方式 | 适用场景 | 状态 |
|----------|----------|------|
| **stdio** | 本地 Server（子进程） | 标准 |
| **Streamable HTTP** | 远程 Server（SaaS） | 标准 |
| HTTP + SSE | 旧版 | **已废弃** |

实现建议：本地开发用 stdio（最简），远程集成用 Streamable HTTP（兼容负载均衡/代理/CDN）。

### 4. N×M 问题已解决

- **前 MCP 时代**：N 个 AI 应用 × M 个工具 = N×M 个定制集成（各自实现认证、数据格式、错误处理）
- **MCP 时代**：构建一次 MCP Server → 所有 MCP 兼容 Client 可用 → **N + M 个集成**

这不仅是开发者便利，更是生态系统从碎片化到复合增长的质变。

### 5. 企业部署模式：从只读到可控写入

**生产环境最佳实践**：

1. 从**只读、高价值集成**开始（文档、分析、问题追踪）
2. 将写操作、客户数据、破坏性操作放在**显式审批门禁**后
3. 所有操作配备**审计日志**

**主要用例**（按企业采用率排序）：
- 测试生成 / 代码审查 / 调试
- 漏洞修复 / 遗留代码理解
- CRM / 营销自动化 / 广告分析

---

## 二、协议设计精要

### 三角色模型

```
Host（AI 应用，如 Claude Desktop）
  └── Client（管理连接，一个 Client 对一个 Server）
        └── Server（暴露能力给 AI）
```

一个 Host 可运行多个 Client，一个请求可涉及多个 Server 协同工作。

### 请求流程

1. AI 模型决定调用哪个工具 + 参数
2. Client 将请求路由到对应 Server
3. Server 执行操作（调 API / 查数据库 / 操作 SaaS）
4. 模型将结果整合到响应中

### Elicitation 的两种模式

- **URL 模式**：安全关键交互（OAuth 流程、凭证输入、支付）——跳转外部 URL
- **Form 模式**：结构化输入/澄清——表单收集

### Server-Side Agent Loops

Server 可以在 Sampling 请求中包含工具定义，指定工具选择行为，并在内部实现多步推理——无需自定义编排代码。这意味着 MCP Server 本身可以成为一个 mini Agent。

---

## 三、Hermes 的 MCP 集成现状与改进方向

### 现状评估

Hermes 已有 native-mcp 和 mcporter 两个 Skill 处理 MCP 集成：
- native-mcp：内置 MCP Client，连接 config.yaml 配置的 Server
- mcporter：CLI 桥接工具，用于临时 Server 交互

### 改进建议

**短期（立即可做）**：
1. **废弃 HTTP+SSE 配置**：检查现有 MCP Server 配置，将旧 SSE 传输迁移到 Streamable HTTP
2. **Elicitation 模式**：评估在飞书群交互中是否可以利用 Form 模式收集用户输入（替代纯文本指令）
3. **Async Tasks**：长时任务（回测/模型训练）可以用 async 模式，避免 blocking

**中期（架构级）**：
4. **MCP Apps**：如果 Hermes 未来有 Web UI，可以利用 MCP Apps 在聊天中渲染富交互界面
5. **Server-Side Agent Loops**：将部分复杂编排（如多步数据分析）下推到 MCP Server 内部，减少 Agent 和 Server 之间的往返
6. **Sampling 用法**：Server 可以请求 Agent 做推理，实现双向协作（而非单向调用）

**长期（生态）**：
7. **自建 MCP Server 发布**：Hermes 的各种工具（飞书/邮件/量化）可以包装为标准 MCP Server，贡献到官方注册表
8. **MCP Registry 集成**：利用官方注册表（9,652 个 Server）的发现机制，自动推荐可用工具

---

## 四、关键时间线

| 时间 | 里程碑 |
|------|--------|
| 2024-11 | Anthropic 开源 MCP（主要面向 AI 辅助编程） |
| 2025-03 | Spec v2：Streamable HTTP + OAuth 2.1。**同日 OpenAI 宣布全面支持** — 转折点 |
| 2025-04 | Google DeepMind 确认 Gemini 支持 MCP |
| 2025-06 | MCP Server 正式化为 OAuth Resource Server |
| 2025-09 | MCP Registry 上线 |
| 2025-11 | MCP Extensions 系统（首个扩展：MCP Apps） |
| 2025-12 | Anthropic 将 MCP 捐赠给 Linux 基金会（Agentic AI Foundation） |
| 2026-01 | MCP Apps 正式发布，联合 OpenAI |
| 2026-05 | 15,926 个 GitHub 仓库，9,652 个注册 Server |

---

## 五、知识缺口

1. MCP Apps 的 iframe 沙箱具体安全策略文档尚未详细公开
2. Server-Side Agent Loops 的编排复杂度和调试工具链尚不成熟
3. 企业场景中 MCP Server 的版本管理和灰度发布最佳实践缺少案例研究
4. MCP 在低资源边缘设备（如 Jetson Orin）上的本地 Server 运行性能未经验证

---

## 六、参考来源

1. Digital Applied (2026-05-24): MCP Adoption Statistics 2026 — https://www.digitalapplied.com/blog/mcp-adoption-statistics-2026-model-context-protocol
2. WorkOS Blog (2026-03-26): Everything Your Team Needs to Know About MCP in 2026 — https://workos.com/blog/everything-your-team-needs-to-know-about-mcp-in-2026
3. MCP 官方规范 (2025-06-18): Specification — https://modelcontextprotocol.io/specification/2025-06-18
4. MCP Roadmap (2026-03-05): Strategic Priorities — https://modelcontextprotocol.io/development/roadmap
5. Stacklok: State of MCP in Software 2026 Report


## 相关笔记
- [Hermes Agent Deep Dive — 进化路线图](2026-04-07-hermes-agent-deep-dive-evolution-roadmap.md) (关键词: dive, deep)
- [FastMCP Python SDK 深度精读（v1.27.1 源码级）](2026-05-26-fastmcp-sdk-deep-dive.md) (关键词: dive, deep)
- [Mem0 AI Agent 记忆框架深度研究](2026-05-27-mem0-agent-memory-deep-dive.md) (关键词: dive, deep)
- [AI Agent 2026 前沿趋势与量化交易新技术 — 深度学习笔记](2026-05-27-ai-agent-2026-deep-dive.md) (关键词: dive, deep)
- [Voicebox 语音生成系统深度研究](explore/voicebox-deep-dive-2026.md) (关键词: dive, deep)
