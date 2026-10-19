# AgentSwarms：可自部署的 Agentic AI + BI 统一平台

> **来源**: [github.com/AgentSwarms-fyi/agentswarms](https://github.com/AgentSwarms-fyi/agentswarms)
> **官网**: [agentswarms.fyi](https://agentswarms.fyi)
> **许可证**: Elastic License 2.0（source-available，非 OSI 开源）
> **Stars**: 40 | **Forks**: 6 | **语言**: TypeScript
> **技术栈**: TanStack Start (React 19) + Supabase + LangChain/LangGraph
> **创建**: 2026-07-21
> **日期**: 2026-07-31
> **标签**: `AgentSwarms` `Multi-Agent` `Swarm` `BI` `RAG` `MCP` `自部署` `可视化编排`

---

## 核心结论

AgentSwarms 是一个**完整可自部署的 Agentic AI + 商业智能（BI）统一平台**。核心价值：Agent 对话 + 可视化多 Agent Swarm 编排画布 + RAG 知识库 + 连接 27 个数据源 + BI 仪表盘 + 全链路追踪，全部"bring-your-own-everything"（自带数据+密钥）。一个 Supabase 项目做后端，一条 Docker 命令部署。

---

## 一、核心能力矩阵

| 能力 | 说明 |
|------|------|
| 🤖 **Agent Chat** | 浏览器内构建 Agent + 工具，对话，全链路 trace，可视化 BI 图表，生成 PPT/Word/Excel |
| 🐝 **Swarm Canvas** | 基于 XYFlow 的可视化多 Agent 工作流画布，节点 = Agent/路由/条件/循环/审批/工具 |
| 📚 **Knowledge Base / RAG** | 上传文档 → 切分 → 嵌入（pgvector）→ Agent 基于自有数据回答 |
| 🏢 **Data Sources** | **27 个连接器**（22 个数据库/仓库 + 5 个 SaaS 应用） |
| 🔑 **Secrets Manager** | 凭证加密存储一次，到处用 `{{secret:NAME}}` 引用 |
| 🗂️ **Data Catalog** | 数据目录：爬取仓库/S3/Iceberg，Schema 推断，PII 检测，血缘追踪 |
| 📊 **Business Intelligence** | 拖拽式仪表盘，交叉筛选，行级安全+列级掩码，增量刷新 |
| 🔍 **Observability** | 每个工具调用/Token/成本的全链路 trace + 审计日志 |
| 🌐 **Web Search** | 内置 web_search/web_browse 工具（免费 DuckDuckGo 或 Firecrawl） |
| 🔌 **BYOK + MCP + A2A** | 加密用户密钥 + MCP 连接 + Swarm 导出到 LangGraph/CrewAI |
| 🛠️ **MCP Builder** | 用 FastMCP 写 MCP Server，部署到沙箱内核，自动注册 |
| 🛂 **IAM** | 超级管理员/组/用户，模型白名单，行过滤+隐藏列 |
| 📓 **Developer Workspace** | 沙箱 Python Notebook（真实 LangChain/LangGraph/LlamaIndex） |
| 🛡️ **Guardrails** | Prompt 注入测试、PII 脱敏、LLM-as-judge 评分 |

---

## 二、Swarm Canvas：可视化多 Agent 编排（核心亮点）

```
Swarm Canvas (基于 XYFlow):

  ┌──────────┐     ┌──────────┐     ┌──────────┐
  │ Router   │────→│ Agent A  │────→│ Approval │
  │ (路由)   │     │ (分析)   │     │ (人工审批)│
  └────┬─────┘     └──────────┘     └────┬─────┘
       │                                  │
       ▼                                  ▼
  ┌──────────┐                     ┌──────────┐
  │ Agent B  │                     │ Tool Call│
  │ (搜索)   │                     │ (生成报告)│
  └──────────┘                     └──────────┘

每个节点可配置:
  • Provider + Model (OpenRouter/OpenAI/Anthropic/Gemini/Ollama...)
  • Prompt / System 指令
  • Tools (工具集)
  • Knowledge Base (RAG 知识库)

运行方式:
  • 画布手动运行
  • API 调用
  • 定时调度 (cron)

关键特性:
  ✅ Checkpoint: 运行过程存盘, 重启/部署后继续
  ✅ 人工审批节点: 暂停等待人工决定 (非自动通过/失败)
```

---

## 三、数据源：27 个连接器

### 22 个数据库/仓库（只读查询）

PostgreSQL / MySQL / SQL Server(Azure) / Oracle / Redshift / Snowflake / Databricks / BigQuery / Azure Synapse / Trino(Presto) / Athena / **ClickHouse** / CockroachDB / TimescaleDB / AlloyDB / Greenplum / YugabyteDB / MariaDB / SingleStore / StarRocks / Apache Doris / PlanetScale

### 5 个 SaaS 应用（定时拉取为数据集）

Google Sheets / Stripe / Shopify / HubSpot / Salesforce

---

## 四、两种形态：自部署 vs 托管

| 维度 | 本仓库（自部署） | agentswarms.fyi（托管） |
|------|-----------------|----------------------|
| **定位** | 在自己基础设施上运行完整平台 | **学习优先**——课堂式 agentic AI 教育 |
| **运行** | 你的 Supabase + 你的密钥 + 你的 Docker | 托管基础设施 + 免费 AI 网关 |
| **适合** | 团队/折腾者想**拥有**平台 | 学习者想**练习** agentic AI |

> 名字和托管服务归项目作者，仓库是 source-available（Elastic License 2.0）。

---

## 五、技术架构

| 层 | 技术 |
|----|------|
| **前端** | TanStack Start (React 19) + XYFlow（画布） |
| **后端** | **Supabase**（Postgres + Auth + Storage + pgvector）——不是自建后端 |
| **语言** | TypeScript |
| **AI 框架** | LangChain / LangGraph / LlamaIndex（沙箱内核） |
| **部署** | Docker Compose / Node |
| **要求** | Node ≥20.19，最低 2vCPU/4GB VM（无 GPU） |

### BYOK（Bring Your Own Key）支持的 Provider

OpenRouter / OpenAI / Anthropic / Gemini / Bedrock / Azure / OCI / Qwen / Grok / Groq / Ollama / vLLM 等

---

## 六、快速部署

```bash
# 一键部署（创建 Supabase 项目 + 填 .env 后）
cp .env.example .env
bash scripts/setup.sh                    # Docker → http://localhost:8080
# bash scripts/setup.sh --dev            # 本地开发
# bash scripts/setup.sh --docgen         # + PPT/Word/Excel 渲染

# 或手动
git clone https://github.com/AgentSwarms-fyi/agentswarms.git
cd agentswarms && npm install
cp .env.example .env
npx supabase login && npx supabase link && npx supabase db push
npm run dev                              # → http://localhost:8080

# Docker
docker compose up --build
```

---

## 七、与其他 Multi-Agent 平台对比

| 维度 | AgentSwarms | LangGraph Cloud | CrewAI | Dify | Hermes |
|------|-------------|-----------------|--------|------|--------|
| **可视化编排** | ✅ Swarm Canvas | ❌ 代码 | ❌ 代码 | ✅ | ❌ |
| **BI 仪表盘** | ✅ 内置 | ❌ | ❌ | ❌ | ❌ |
| **数据源连接** | ✅ 27 个 | ❌ | ❌ | 部分 | ❌ |
| **RAG** | ✅ pgvector | 需自建 | 需自建 | ✅ | ✅ |
| **MCP** | ✅ Builder+连接 | ❌ | ❌ | ✅ | ✅ |
| **自部署** | ✅ Docker | 云服务 | 库 | ✅ | ✅ |
| **BYOK** | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Trace/审计** | ✅ 完整 | 部分 | ❌ | ✅ | 部分 |
| **人工审批节点** | ✅ | ❌ | ❌ | ❌ | ❌ |
| **许可证** | Elastic 2.0 | MIT | MIT | Apache 2.0 | — |

> AgentSwarms 的差异化：**Agentic AI + BI 一体化**——其他平台要么纯 Agent，要么纯 BI，AgentSwarms 把两者融合（Agent 对话直接查数据库生成图表/文档）。

---

## 八、适用场景

| 场景 | 怎么用 |
|------|--------|
| **企业内部 AI 分析平台** | 连接数仓 → Agent 自然语言查数据 → BI 仪表盘 |
| **多 Agent 工作流** | Swarm Canvas 设计审批流/分析流/报告流 |
| **RAG 知识库** | 上传企业文档 → Agent 基于私有知识回答 |
| **数据目录治理** | Data Catalog 爬取仓库 + PII 检测 + 血缘 |
| **定时 Agent 任务** | Swarm 定时调度 + Checkpoint |
| **MCP Server 开发** | MCP Builder 写+部署 MCP Server |

---

## 九、许可证注意

| 许可证 | 说明 |
|--------|------|
| **Elastic License 2.0** | source-available，**非 OSI 开源** |
| **允许** | 使用、修改、分发、自部署 |
| **限制** | 不能作为托管服务提供给他人（去掉 license key 管制功能） |
| **vs MIT/Apache** | 对自部署用户几乎无差异，对想做竞品 SaaS 的有限制 |

---

## 十、关键术语速查

| 术语 | 说明 |
|------|------|
| **Swarm** | 多 Agent 可视化工作流 |
| **Swarm Canvas** | 基于 XYFlow 的画布编辑器 |
| **BYOK** | Bring Your Own Key，自带 Provider 密钥 |
| **Checkpoint** | 运行过程存盘，重启后继续 |
| **pgvector** | PostgreSQL 向量扩展，RAG 底层 |
| **MCP Builder** | 在平台内编写部署 MCP Server |
| **IAM** | 身份与访问管理 |
| **Row-Level Security** | 行级安全（仪表盘共享） |
| **Incremental Refresh** | 增量刷新（只查尾部时间窗口） |
| **A2A** | Agent-to-Agent 协议端点 |

---

## 十一、与现有笔记/项目的关联

| 关联项目 | 关系 |
|---------|------|
| **Hermes Agent** | AgentSwarms 的 Swarm Canvas 可视化编排理念可借鉴——Hermes 目前是代码编排，AgentSwarms 是可视化编排 |
| **学 Agent 正确顺序** | AgentSwarms 是 Phase 5（Multi-Agent）的可视化工具候选 |
| **Agent Harness 知识体系** | AgentSwarms 的 Checkpoint + Trace + 审计 = Harness 底座的完整实现 |
| **AI Agent 从玩具走向生产系统** | AgentSwarms 内置了生产级需要的：Trace 审计/预算控制/IAM/行级安全/灰度 |
| **libSQL** | AgentSwarms 用 Supabase(Postgres)，如需嵌入式可考虑 libSQL |
| **MCP 协议** | AgentSwarms 的 MCP Builder 是 MCP 生态的实践工具 |
