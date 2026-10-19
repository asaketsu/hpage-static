# AI Agent 协议生态 2026：MCP / A2A / ACP / ANP 四栈全景对比

> 2026-07-07 夜间自学习 | 主题：Agent 互操作协议生态
> 来源：arXiv 2505.02279v1 综述 + Coalition for Secure AI MCP 安全白皮书 + DigitalApplied 生态图

## 🎯 核心结论

**2026 年 Q1，四大 Agent 通信协议已形成分工明确的"协议栈"，而非相互替代关系。** 一句话定位：

- **MCP**（Anthropic→Linux Foundation AAIF）= Agent ↔ Tool，"AI 的 USB-C"，JSON-RPC，97M 下载量
- **A2A**（Google→Linux Foundation）= Agent ↔ Agent，能力卡片（Agent Card）点对点任务委派，50+ 合作伙伴
- **ACP**（IBM BeeAI→Linux Foundation AI & Data）= 多模态消息，REST + MIME multipart，天生多模态
- **ANP** = 去中心化 Agent 发现，DID（did:wba）+ JSON-LD，跨公司 Agent 市场

学术综述（arXiv 2505.02279）给出的**渐进式采纳路线图**：MCP（工具接入）→ ACP（多模态消息）→ A2A（协作任务）→ ANP（去中心化市场）。这与企业实际落地路径高度吻合。

## 📊 四协议深度对比

| 维度 | MCP | ACP | A2A | ANP |
|------|-----|-----|-----|-----|
| 架构模型 | Client–Server | Brokered C/S | Peer-to-Peer | 开放网络 |
| 传输层 | Stdio / HTTP / SSE | HTTP REST | HTTP + SSE + JSON-RPC | HTTP(S) |
| 数据格式 | JSON-RPC 2.0 | MIME multipart | JSON（Agent Card） | JSON-LD (Schema.org) |
| 核心抽象 | Tools / Resources / Prompts / Sampling | Agent Detail / Task Request / Message | Agent Card / Skills / Task / Artifacts | DID / Agent Description / 发现目录 |
| 身份机制 | Host 继承 | 服务端注册 | Agent Card 能力声明 | 去中心化身份（did:wba） |
| 定位 | 模型↔工具上下文 | 异构 Agent 消息 | 点对点任务外包 | 去中心化发现与互操作 |
| 主导方 | Anthropic | IBM BeeAI | Google | 开放社区 |
| 2026 采用 | Fortune 500 达 28% | 企业内部协作 | 50+ 合作伙伴 | 早期探索 |

## 🔒 MCP 安全要点（Coalition for Secure AI 白皮书 2026-03）

白皮书按部署模式给出差异化安全建议，值得直接落地：

| 部署模式 | 风险 | 关键建议 |
|---------|------|---------|
| **DP1 本地 stdio** | DNS 重绑定攻击 | **强烈推荐 stdio 而非 HTTP**，避免 DNS rebinding |
| **DP2 单租户远端** | 凭证泄露 | 单租户隔离，传输加密 |
| **DP3 多租户共享** | 数据交叉污染 | 必须沙箱化防止权限提升 |

通用风险清单：工具投毒（tool poisoning）、凭证窃取、沙箱逃逸、命令注入、版本漂移、权限持久化、配置漂移。**核心原则：MCP server 继承 host 的安全态势，因此 host 的安全姿态决定了整个链路上限。**

## 🧩 A2A 的 Agent Card 机制

A2A 最值得关注的设计是 **Agent Card**——一份 JSON 格式的能力描述文档，通过 HTTP GET 公开获取：

- 每个 Agent 发布自己的 `skills`、`authentication`、`endpoint`
- Client Agent 读取 Card 后决定是否委派任务
- 这是**Agent 间发现与信任建立**的标准化方案

与 Hermes 已有的 `agent-card-protocol` Skill 方向一致——Agent Card 正在从"可选自描述"演变为"A2A 协议的强制身份层"。

## 💡 对 Hermes 系统的启示

1. **MCP 已是基础设施级标准**（Fortune 500 28%、97M 下载），Hermes 的 `native-mcp` + `mcporter` 架构选型正确，应持续投入而非自研协议
2. **stdio > HTTP 本地部署**：白皮书明确建议本地 MCP server 用 stdio 传输以规避 DNS rebinding，应写入 `mcp-integration` Skill 的部署指南
3. **Agent Card 升级**：现有 `agent-card-protocol` Skill 应对齐 A2A 的 Agent Card 规范（skills + authentication + endpoint 三字段），使其可作为 A2A 兼容的身份层
4. **四协议不是竞争**：Hermes 应明确自身在每个协议层的角色——MCP（已有）、A2A（待评估，多 Agent 编排时）、ACP/ANP（暂不需要）
5. **安全白皮书可直接吸收**：`mcp-security-audit` Skill 应补充 Coalition for Secure AI 的三部署模式检查清单

## 📚 关键引用

- arXiv 2505.02279v1 — *A Survey of Agent Interoperability Protocols: MCP, ACP, A2A, ANP*
- Coalition for Secure AI — *Model Context Protocol (MCP) Security*（2026-03 PDF）
- DigitalApplied — *AI Agent Protocol Ecosystem Map 2026*
- Synvestable — *Model Context Protocol for Enterprise: 2026 Deployment Guide*（Fortune 500 28% 数据源）

## 相关笔记

- `竞品吸收笔记_GenericAgent.md` — Agent 框架吸收
- `前瞻性问题-AI垂域LLM载具设计.md` — 垂域 Agent 设计
- `达尔文Skill2.0深度分析-Evolver对比吸收.md` — Agent 自进化与协议
