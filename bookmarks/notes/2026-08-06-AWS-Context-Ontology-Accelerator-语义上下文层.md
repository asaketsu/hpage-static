# AWS Context Ontology Accelerator — 基于本体的 AI Agent 语义上下文加速器

> **来源**：[github.com/aws/context-ontology-accelerator](https://github.com/aws/context-ontology-accelerator)
> **License**：Apache-2.0
> **Stars**：359 · **Forks**：31
> **语言**：Python 3.12 + TypeScript
> **创建时间**：2026-07-28
> **机构**：AWS（Amazon Web Services）

---

## 一句话定义

> AWS 开源的**基于本体的语义上下文层**——结合知识图谱、形式化本体和规则系统与现代 AI，让 Agent 能检索上下文、根据业务逻辑验证、并确定正确的行动。

---

## 内容整理

### 核心架构：Scan → Model → Serve

```
┌─────────────────────────────────────────────────┐
│                   SERVE 层                       │
│  MCP Server → AI Agent                           │
│  SPARQL 联邦查询 (VKG)                            │
│  知识图谱遍历                                     │
│  Context Manager（查询编排）                       │
├─────────────────────────────────────────────────┤
│                   MODEL 层                       │
│  本体归纳与推理 (HermiT/ELK)                      │
│  指标定义与解析                                   │
│  统一语义图谱构建                                  │
├─────────────────────────────────────────────────┤
│                   SCAN 层                        │
│  数据源连接 → Schema 发现 → 元数据富化             │
│  结构化数据 + 非结构化文档摄入                      │
└─────────────────────────────────────────────────┘
```

### 关键能力

| 能力 | 说明 |
|------|------|
| **数据源摄入** | 连接数据库 + 非结构化文档，自动发现 schema，富化元数据 |
| **本体工程** | 本体归纳与推理（基于 HermiT/ELK 推理引擎） |
| **语义图谱** | 构建统一的知识图谱，连接结构化和非结构化数据 |
| **虚拟知识图谱 (VKG)** | 基于 Ontop 的 SPARQL 联邦查询，虚拟映射不移动数据 |
| **指标系统** | 指标定义和解析服务 |
| **MCP 工具** | 为 AI Agent 提供 MCP (Model Context Protocol) 工具接口 |
| **上下文管理** | Context Manager 编排查询，对接上游客户端 |

### 访问控制模型

双层 RBAC：

| 层级 | 角色 |
|------|------|
| **命名空间级** | owner、maintainer、data-steward、data-analyst |
| **平台级** | `platform-admin`、`platform-viewer`（跨所有命名空间） |

### 仓库结构

```
semantic-context/
├── models/              # Smithy API 模型（API 合约的 source of truth）
├── smithy-generated/    # 从 Smithy 自动生成（OpenAPI + Python接口 + TS客户端）
├── infra/               # AWS CDK (TypeScript) — 基础设施 + 按服务 stack
├── packages/
│   ├── control-plane/   # 控制面 API
│   ├── data-layer/      # 数据层 API（查询、检索、遍历）
│   ├── sources/         # 统一数据源摄入（数据库 + 文档）
│   ├── ontology-engine/ # 本体归纳与推理（HermiT/ELK）
│   ├── metric-service/  # 指标定义与解析
│   ├── vkg/             # 虚拟知识图谱（Ontop）
│   ├── mcp-server/      # AI Agent 的 MCP 工具
│   ├── context-manager/ # Serve 层 Context Manager
│   └── web-app/         # React + Cloudscape 前端
├── libs/                # 共享 Python/TS 配置
├── scripts/             # CI 无关的构建/测试/部署脚本
└── ci/                  # GitLab CI pipeline
```

### 技术栈

| 层 | 技术 |
|----|------|
| **语言** | Python 3.12, TypeScript |
| **API 合约** | Smithy → OpenAPI + Python 接口 + TypeScript 客户端 |
| **IaC** | AWS CDK (TypeScript) |
| **前端** | React + Cloudscape Design System |
| **包管理** | uv (Python), pnpm (TypeScript) |
| **Monorepo 编排** | Nx |
| **测试** | pytest (单元 + 集成) |
| **Lint** | ruff, mypy (strict) |
| **代码生成** | Smithy CLI (Java 17 + Gradle) |
| **本体推理** | HermiT / ELK (OWL 推理机) |
| **VKG** | Ontop (Virtual Knowledge Graph) |

### 前置条件

- Python 3.12, Node.js 22+, Docker
- pnpm, Java 17+ (Smithy codegen), Gradle
- uv (Python 包管理器)

### 外部依赖许可注意

| 依赖 | License | 风险 |
|------|---------|------|
| PyMuPDF | **AGPL-3.0** | ⚠️ 传染性开源许可，商用需注意 |
| owlready2 | LGPL-3.0 | 动态链接例外，相对安全 |

---

## 查询拓展

- AWS 为什么选择 Smithy 而非 Protobuf/OpenAPI 作为 API 合约的 source of truth？
- VKG (Virtual Knowledge Graph) 基于 Ontop 的 SPARQL 联邦查询性能如何？大规模数据下的延迟？
- HermiT/ELK 推理引擎在本体归纳中的具体角色——是前置推理还是运行时推理？
- MCP Server 暴露了哪些具体工具给 AI Agent？查询语义图谱的接口设计？
- 命名空间隔离的底层实现——物理隔离还是逻辑隔离？
- 这套系统的部署成本如何？是否强依赖 AWS 服务（CDK/RDS/Neptune）？

---

## 归纳总结

AWS Context Ontology Accelerator 是一个企业级的**语义上下文基础设施**项目。核心价值在于：把散落在数据库、文档、API 中的异构数据，通过本体建模和知识图谱统一为**可被 AI Agent 查询和推理的语义层**。

它解决的是 Agent 进入企业生产环境的**信任问题**——Agent 不再是"根据训练数据猜答案"，而是"查询经过业务逻辑验证的语义图谱，推理出符合规则的行动"。这是 Agent 从"聊天机器人"到"可信决策系统"的关键一跳。

技术亮点：
- **VKG 虚拟知识图谱**：不移动数据，用 SPARQL 联邦查询直接映射数据库
- **Smithy API 合约**：从单一 source of truth 自动生成多语言接口
- **MCP 工具接口**：原生支持 Model Context Protocol，可直接对接 AI Agent
- **形式化本体推理**：HermiT/ELK 提供基于 OWL 的逻辑推理能力

---

## 趋势判断

- **本体工程回归 AI 主流**：知识图谱 + 本体推理曾被深度学习边缘化，但 Agent 时代对"可解释、可审计、可验证"的需求让形式化方法重新成为关键基础设施
- **语义上下文层成为 Agent 基础设施**：相当于 Agent 的"企业数据仓库"——把异构数据统一为 Agent 可理解的概念模型
- **MCP 成为 Agent↔知识层的标准协议**：AWS 选择 MCP 作为 Agent 查询接口，进一步确认 MCP 的标准地位
- **VKG 模式优于 ETL 模式**：虚拟知识图谱不移动数据，避免了数据湖/仓库的同步延迟和维护成本
- **企业级 Agent 的信任链**：本体验证 + 规则推理 + 语义查询 = 可解释的决策路径，这是企业采购 Agent 系统的前提

---

## 关联分析

- **与 Hermes Agent 知识层的关联**：Hermes 有 `knowledge-fusion`（知识融合引擎）和 `knowledge-query`（统一知识查询入口）Skill。AWS 的 Scan→Model→Serve 架构是这两个 Skill 的企业级实现方案——可以作为 Hermes 知识层升级的参考架构
- **与 MCP 生态的关联**：项目直接提供 MCP Server，Agent 通过 MCP 工具查询语义图谱。这与用户的 `mcp-integration` 和 `mcp-server-development` 技能直接对接
- **与用户航空结构 AI 研究方向的关联**：用户研究"航空结构 AI（知识图谱+专家模型）"，AWS 的本体工程 + 知识图谱 + 推理引擎架构可以直接用于航空结构领域的知识建模——把设计规范、材料属性、载荷工况、适航条款建模为本体，Agent 查询推理
- **与 SkillOpt 的关联**：SkillOpt 需要可靠验证器来训练技能。AWS 的语义上下文层可以作为验证器——Agent 行动结果与本体规则对比验证
- **与 RAG 的关联**：VKG 虚拟知识图谱是 RAG 的升级版——不是向量相似度检索，而是语义精确查询+逻辑推理

---

## 📎 关键链接

- 📖 仓库：[github.com/aws/context-ontology-accelerator](https://github.com/aws/context-ontology-accelerator)
- 📦 目录结构：`packages/` 下 9 个子包（control-plane, data-layer, sources, ontology-engine, metric-service, vkg, mcp-server, context-manager, web-app）
- 🔧 Smithy API 模型：`models/` 目录
- 🚀 基础设施：AWS CDK (TypeScript)

---

*笔记创建：2026-08-06 · 来源：github.com/aws/context-ontology-accelerator*


## 相关笔记

- [DeepSeek Agent Harness 执行栈全景图](./2026-08-06-DeepSeek-Agent-Harness执行栈全景图.md) — Agent 执行栈架构对照
- [SkillOpt 微软技能优化器](./2026-08-06-SkillOpt-微软Agent技能训练优化器.md) — Skill 优化方法论互补
- [Skill-Use Benchmark](./explore/2026-08-06-SkillUse.md) — Skill 使用能力评估基准，上下文层验证靶标
