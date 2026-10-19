# AI Agent 协议生态 2026 全景：MCP/A2A/ACP/UCP 四层协议栈

> 📅 2026-06-04 | 夜间自学习
> 🔗 来源：Digital Applied、Knit API、OneReach.ai、Vellum AI、Truthifi、MCP 官方规范
> 🏷️ 关键词：MCP、A2A、ACP、UCP、Agent 协议栈、多 Agent 编排、OAuth 2.1

---

## 一、核心发现：2026 Agent 协议四层栈

Agent 协议生态已从碎片化收敛为**四层互补协议栈**，不再是竞争关系：

```
┌──────────────────────────────────────────────────┐
│               商业层 (Commerce)                    │
│   ACP (开放 Agent 商务)  │  UCP (Google 生态商务)   │
├──────────────────────────────────────────────────┤
│             编排层 (Coordination)                   │
│       A2A (Agent 发现、委派、安全通信)               │
├──────────────────────────────────────────────────┤
│             工具层 (Tool Access)                    │
│       MCP (标准化 Agent-工具/数据连接)              │
├──────────────────────────────────────────────────┤
│           模型/运行时 (Runtime)                      │
│  Claude/GPT-4o/Gemini/Llama + LangChain/CrewAI     │
└──────────────────────────────────────────────────┘
```

### 1.1 MCP：Agent-to-Tool 基础设施（事实标准）

**关键数据**：
- PyPI 月下载量：**1.64 亿**
- 公开 MCP Server 数量：**10,000+**（2026 年 4 月）
- 所有主流 AI 平台均已支持：Claude、ChatGPT、Perplexity、Grok、Mistral
- Linux Foundation AAIF（Agentic AI Foundation）接管治理

**技术架构**：
- 协议：JSON-RPC 2.0
- 传输层：`stdio`（本地）+ `Streamable HTTP`（远程，已取代旧 SSE）
- 三大原语：Tools（可调用函数）、Resources（只读数据）、Prompts（模板）
- 运行时发现（vs 设计时集成）：Agent 动态读取 `tools/list` schema 后自主决策

**核心洞察**：MCP 将 N×M 集成问题压缩为 N+M。写一个 MCP Server，所有兼容 Agent 都能用。

### 1.2 A2A：Agent-to-Agent 编排协议

**发起方**：Google（2025 年 4 月），50+ 行业合作伙伴
**市场预测**：Gartner 预测 2026 年 40% 企业应用将内嵌 AI Agent（2025 年 <5%）

**核心机制**：
- **Agent Card**：JSON 元数据文档，描述 Agent 能力、输入/输出、认证需求
- **Task 对象**：结构化任务，生命周期：`submitted → working → input-required → completed`
- **异步设计**：基于 HTTP + JSON-RPC + SSE，支持长时间运行任务
- **安全模型**：HTTPS + TLS 1.2+、OAuth 2.0/mTLS/API Key、RBAC、审计追踪

**三层通信框架**：
```
[User] → [Client Agent] ←(A2A Protocol)→ [Remote Agent]
```
Agent 可动态切换 Client/Server 角色。

### 1.3 ACP：开放 Agent 商务协议

**发起方**：IBM Research + Linux Foundation
**定位**：B2B Agent 交易的标准化词汇表

**交易流程**：
```
Discovery → RFQ → Offer → Negotiation → Acceptance → Confirmation
```
适用场景：自主 B2B 采购、API 市场、跨供应商 Agent 服务市场。

### 1.4 UCP：Google 生态商务协议

Google Shopping/Merchant Center 生态内的专用 Agent 交易协议。

---

## 二、Agent 架构三级演进模型

### Level 1：AI Workflow（输出决策）
- 模型决定输什么，架构静态
- 典型：标准 Prompt → LLM → 输出

### Level 2：Router Workflow（任务决策）⭐ 当前主流
- AI 选择工具和执行路径，但不能修改流程
- 企业创新的主要阵地
- Hermes 当前处于此层级

### Level 3：Autonomous Agent（流程决策）
- Agent 完全控制应用流，可自创工具和任务
- 代表：Devin、BabyAGI、MetaGPT
- 状态：大多实验性，未广泛生产就绪

### Agent 四大核心组件

```
[Planning] → [Execution] → [Refinement] → [Interface]
```

- **Planning**：CoT/ReAct/Self-Refine/RAISE/Reflexion/LATS
- **Execution**：工具访问 + LATM（LLM as Tool Maker，Agent 自写工具）
- **Refinement**：LLM 评估 + 记忆系统（短期上下文 / 长期向量库+KV+图谱）
- **Interface**：人机协作 UI + Agent-Computer Interface（ACI）

---

## 三、MCP 生态 2026 兼容性矩阵

**原生支持 OAuth 2.1 的平台（10+）**：
Claude Desktop、Claude Code、ChatGPT、VS Code Copilot、Zed、Kiro(AWS)、Amazon Q、OpenCode、Docker MCP Toolkit、Cursor、Gemini CLI

**需 Bridge 包的平台**：
Windsurf、Cline、Continue.dev

**尚未支持**：
Google Antigravity（在路线图中）

### 关键平台更新

- **Claude**：Customize > Connectors UI 面板 + Managed Agents（公开 Beta）
- **ChatGPT**：强制 OAuth 2.1 + DCR，Apps SDK 支持 MCP 交互式 UI 组件。旧 Assistants API 将于 2026 年 8 月废弃
- **VS Code Copilot**：通过 `.vscode/mcp.json` 配置，v1.101+ 免费支持
- **Cursor**：免费 Hobby 层级支持远程 MCP

---

## 四、MCP 生产部署反模式

### 🚫 "瑞士军刀"反模式
连接数十个 MCP Server 到单个 Agent：
- 每个 Server 的工具列表膨胀上下文窗口
- 工具名称冲突增加选择错误
- 浪费 token 在 `tools/list` 响应上

**正确做法**：构建专注的、目的特定的 Agent。

### Build vs Buy 决策框架

| 场景 | 策略 |
|------|------|
| 开发者工具（GitHub/Slack/Notion） | 用现有社区/官方 Server |
| 内部数据系统（自有数据库/API） | **自建**，不经过第三方代理 |
| 业务数据（HR/CRM/Payroll） | **用托管平台**，OAuth 流程太复杂不值得自建 |

---

## 五、对 Hermes Agent 的具体影响

### 5.1 协议栈对齐评估

| 协议层 | Hermes 当前状态 | 差距 | 行动建议 |
|--------|----------------|------|---------|
| MCP（工具层） | ✅ 已实现 native-mcp + mcporter | 完善 OAuth 远程 Server 支持 | 接入更多远程 MCP Server |
| A2A（编排层） | ⚠️ 三机协作用 JSON/文本 | 缺少标准 Agent Card | 定义 Hermes Agent Card 格式 |
| ACP（商务层） | ❌ 不适用 | — | 暂不需要 |
| 安全（OAuth 2.1） | ⚠️ 本地 MCP 不需要，但远程需增强 | PKCE + DCR 未实现 | 参考规范增强远程 MCP 安全 |

### 5.2 可直接落地的改进

1. **Agent Card 定义**：按 A2A 标准为 jbot/ubot/abot 生成 Agent Card JSON，描述能力、工具、认证需求
2. **MCP 工具发现优化**：当前 Hermes 的 MCP 集成已有工具发现，但需避免"瑞士军刀"反模式——按任务按需加载工具集
3. **LATM 模式引入**：让 Hermes 的 Skill 系统支持"Agent 自写工具"模式，从 Skill 进化到 Tool Maker

### 5.3 企业 Agent 采用数据参考

- PwC 300 位高管调研：88% 计划增加 Agent AI 预算，已采用者报告 66% 生产力提升
- IDC 预测：Agent AI 支出 2029 年将达 1.3 万亿美元（CAGR 31.9%）
- Forrester 预警：实施挑战将阻碍 50%+ 的 Agent AI 项目

---

## 六、知识缺口与后续探索

1. A2A Agent Card 与 Hermes 现有 Skill 系统的映射方案
2. MCP Streamable HTTP 传输层的具体实现（Hermes 当前用 stdio）
3. OpenAI Agents SDK 的沙箱化和子 Agent 编排机制
4. LATM（LLM as Tool Maker）在生产环境的安全边界

---

## 七、参考资料

- Digital Applied: AI Agent Protocol Ecosystem Map 2026 (2026-03-18)
- Knit API: The 2026 Guide to the MCP Ecosystem (2026-04-07)
- OneReach.ai: A2A Protocol Explained (2026)
- Vellum AI: Agentic Workflows in 2026 Guide
- Truthifi: The State of MCP 2026 (2026-02-27, updated 2026-05-22)
- MCP 官方 Authorization Specification (Draft)
- Aembit: MCP, OAuth 2.1, PKCE, and the Future of AI Authorization

---

*📅 2026-06-04 猫仔夜间自学习 | AI Agent 协议生态深度研究*

## 相关笔记
- [MCP-OAuth2.1安全规范深度解析](2026-06-04-MCP-OAuth2.1安全规范深度解析.md)
- [proactive-learn-mcp-llm-quant-evolution](2026-05-26-proactive-learn-mcp-llm-quant-evolution.md)
- [MCP协议2026最新生态演进](2026-05-30-MCP协议2026最新生态演进.md)
