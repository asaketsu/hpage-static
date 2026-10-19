# Supabase：开源 Firebase 替代方案深度分析

- 📅 2026-05-02
- ⭐ 4.5/5 — 10万+星、Postgres生态、自托管友好、AI/Vector内置，但学习曲线比Firebase陡
- 🏷️ #BaaS #PostgreSQL #Firebase替代 #自托管 #pgvector #实时数据库
- 📰 GitHub supabase/supabase
- 🔗 https://github.com/supabase/supabase
- 关联：[2026-04-26-RAG与MCP架构差异](2026-04-26-RAG与MCP架构差异.md) [2026-04-23-MCP协议与Agentic-LLM-2025趋势](2026-04-23-MCP协议与Agentic-LLM-2025趋势.md)

## 摘要

Supabase 是一个基于 PostgreSQL 的开源后端即服务（BaaS）平台，定位为 Firebase 的替代方案。核心思路是不造轮子，而是将企业级开源工具（PostgreSQL、PostgREST、GoTrue、Deno）整合为统一的开发平台。提供数据库、认证、自动API（REST+GraphQL）、实时订阅、边缘函数、文件存储、AI/向量工具包七大核心能力。101,711 Stars、Apache 2.0 协议、支持自托管。2026年最新版本为 v1.26.04，活跃迭代中。

## 核心内容

### 架构：开源组件的组合艺术

Supabase 不是重新发明轮子，而是将成熟的 OSS 组件拼装成 Firebase 体验：

| 组件 | 底层技术 | 功能 |
|------|---------|------|
| **Database** | PostgreSQL | 关系型数据库，支持扩展（pgvector、PostGIS等） |
| **Auth** | GoTrue | 认证授权，支持OAuth/SSO/MFA/魔法链接 |
| **REST API** | PostgREST | 自动从数据库 schema 生成 RESTful API |
| **GraphQL** | pg_graphql | 自动生成 GraphQL API |
| **Realtime** | Elixir/Phoenix | WebSocket 实时订阅（INSERT/UPDATE/DELETE） |
| **Storage** | 自研 | S3兼容对象存储，带图片变换（imgproxy） |
| **Edge Functions** | Deno | TypeScript 边缘计算函数 |
| **AI/Vector** | pgvector | 原生向量搜索、嵌入存储 |
| **API Gateway** | Kong | 统一入口，路由到各微服务 |
| **Connection Pool** | Supavisor | Elixir写的PostgreSQL连接池 |

### Docker 自托管架构

docker-compose.yml 包含14个服务，完整自托管只需一条命令：

```
studio → kong(网关) → [auth, rest, realtime, storage, functions]
                      ↓
              supavisor(连接池) → db(PostgreSQL)
                      ↓
              vector(pgvector) + meta + analytics + imgproxy
```

所有服务都有 healthcheck，支持 `docker compose up -d` 一键启动。

### 与 Firebase 对比

| 维度 | Supabase | Firebase |
|------|----------|----------|
| 数据库 | **PostgreSQL**（关系型、SQL全功能） | Firestore（文档型、NoSQL限制） |
| 自托管 | ✅ 完全支持 | ❌ Google锁定 |
| 协议 | Apache 2.0 | 私有 |
| API | REST + GraphQL（自动生成） | REST + SDK |
| 实时 | WebSocket（基于WAL） | Snapshot监听 |
| AI/向量 | **pgvector原生** | 需Vertex AI |
| 查询能力 | **完整SQL** | 有限查询（不支持JOIN等） |
| 事务 | **ACID完整事务** | 有限事务支持 |
| 数据迁移 | **标准SQL导出** | 导出困难 |
| 边缘函数 | Deno（TypeScript） | Cloud Functions（Node.js） |
| 学习曲线 | 需要SQL知识 | 更低门槛 |

### 多语言 SDK

官方维护 JS/Flutter/Swift/Python 四套 SDK，每套都拆分为独立子包（postgrest、auth、realtime、storage、functions），可按需引入。

### AI 能力（pgvector）

这是 Supabase 相比 Firebase 的重要差异化：
- 原生支持 pgvector 扩展，直接在 PostgreSQL 中存储和搜索向量嵌入
- 支持 HNSW 索引（高性能近似最近邻）
- 嵌入生成可配合 OpenAI 等模型
- 向量搜索 + 关系查询合一（不需要额外的向量数据库）

## 🔍 借鉴点

- **pgvector + 关系查询合一** → 当前 Hermes RAG 用的是关键词+语义双索引，如果用 Supabase + pgvector 可以把向量存储和元数据查询合并到一层，简化架构。特别是 `~/obs_notes` + `~/uclaw/bookmarks/notes` 的 RAG 索引可以用 pgvector 替代
- **PostgREST 自动API生成** → 从数据库 schema 自动生成 REST API 的模式，适用于 sanjiangyuan（Vue3/Express/MongoDB）项目的后端快速迭代。如果迁移到 PostgreSQL + PostgREST 可省掉大量 CRUD 代码
- **Realtime 订阅机制** → 基于 PostgreSQL WAL 的实时推送，可用于 Hermes 的 webhook/事件驱动架构。当数据库变更时自动通知 Agent，而不是轮询
- **Docker 自托管** → 14个服务一键启动，适合本机开发环境或 VPS 部署。Supabase CLI 支持 `supabase init` + `supabase start` 本地开发
- **Supavisor 连接池** → Elixir 实现的 PostgreSQL 连接池，比 PgBouncer 更现代。如果项目规模扩大需要连接池管理时可参考

## 🔗 关联性

- 关联已有笔记：[2026-04-26-RAG与MCP架构差异](2026-04-26-RAG与MCP架构差异.md) — Supabase 的 pgvector 可作为 RAG 向量存储层，与 MCP 架构互补
- 关联已有笔记：[2026-04-23-MCP协议与Agentic-LLM-2025趋势](2026-04-23-MCP协议与Agentic-LLM-2025趋势.md) — Supabase 可作为 MCP Server 的后端存储
- 关联已有 skill：`devops/hermes-upgrade` — 如果 Hermes 后端迁移到 PostgreSQL，Supabase 的工具链可简化管理
- 关联技术栈：sanjiangyeno（Vue3/Express/MongoDB）— 可考虑迁移到 Supabase（PostgreSQL）替代 MongoDB + Express

## 💡 启发

- **"不造轮子，组合轮子"的哲学** → Supabase 的每个组件都是独立开源项目，自己只做胶水和体验层。这种模式值得借鉴：Hermes 的 skill 体系本质也是组合现有工具而非重新发明
- **PostgreSQL 作为统一后端** → 关系数据 + 向量搜索 + 实时推送 + 全文搜索全部在一个 PostgreSQL 中完成，避免了多数据库的运维复杂度。AI Agent 的记忆/知识/RAG 如果统一到 PostgreSQL 会大幅简化
- **自托管是杀手锏** → 在数据主权和隐私越来越重要的趋势下，自托管能力让 Supabase 在企业市场有独特优势。对 AI Agent 场景尤其重要——用户数据不应该锁定在第三方云

## 🔮 预判

- **BaaS 向 AI-Native 演进** → Supabase 的 pgvector 只是开始，预计会深度集成 LLM 推理、Agent 编排能力，成为 AI 应用的默认后端
- **Firebase 的 NoSQL 劣势会扩大** → 随着 AI 应用需要复杂关联查询（知识图谱、RAG），PostgreSQL 的关系型优势会越来越明显
- **行动建议**：当前优先级为笔记存档。如果 sanjiangyeno 项目需要重构后端，Supabase 是首选方案。短期可在本机 Docker 跑一个 Supabase 实例测试 pgvector RAG

## 可行性评估

| 条件 | 要求 | 本机 | 状态 |
|------|------|------|------|
| Docker | 必需 | ✅ 已安装 | ✅ |
| RAM | ≥4GB（自托管） | 7.4GB | ✅ |
| 磁盘 | ≥2GB | 充足 | ✅ |
| 网络 | 可选（云同步） | ✅ | ✅ |

**结论**：条件满足，可以本机 Docker 自托管。优先级取决于项目需求。

## 相关笔记
- [2026-04-26-RAG与MCP架构差异](2026-04-26-RAG与MCP架构差异.md)
- [2026-04-23-MCP协议与Agentic-LLM-2025趋势](2026-04-23-MCP协议与Agentic-LLM-2025趋势.md)
- [2026-04-13-rag-vs-mcp-architecture](2026-04-13-rag-vs-mcp-architecture.md)
- [2026-05-02-OpenVoice即时语音克隆分析](2026-05-02-OpenVoice即时语音克隆分析.md)
- [2026-05-02-SkillClaw-analysis](2026-05-02-SkillClaw-analysis.md)
