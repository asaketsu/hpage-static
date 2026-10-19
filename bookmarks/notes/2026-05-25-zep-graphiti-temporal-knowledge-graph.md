# Zep Graphiti - 时序知识图谱MCP服务器深度笔记

> 主题：Zep Graphiti - 时序知识图谱MCP服务器，需FalkorDB/Neo4j
> 日期：2026-05-25
> 深度要求：≥3000字，含核心发现、技术细节、实践案例、知识缺口

---

## 📌 核心发现

### 发现1：Graphiti是AI Agent记忆基础设施的革命性突破

Graphiti（GitHub 20K+ stars，14个月达成）是一个**时序感知型知识图谱引擎**，专门为AI Agent构建持久化、可查询、多租户的记忆层。它解决了传统RAG框架的致命缺陷：静态文档检索无法应对动态演化的知识。

关键突破点：
- **Bi-temporal模型**：同时追踪事件时间（event time）和摄入时间（ingestion time），实现真正的时序推理
- **Deep Memory Retrieval (DMR) 基准**：94.8%准确率 vs MemGPT的93.4%
- **LongMemEval基准**：相比基线准确率提升高达18.5%，响应延迟降低90%
- **MCP Server 1.0**：支持Claude Desktop、Cursor等MCP客户端直接读写知识图谱

### 发现2：FalkorDB是Graphiti的默认数据库，性能优势显著

Graphiti MCP Server 1.0已将FalkorDB设为默认数据库（Neo4j仍完全支持）。FalkorDB作为Redis模块运行，相比Neo4j：
- **低延迟**：专为AI/ML工作负载优化，GraphRAG场景下查询速度快496倍
- **Bolt协议兼容**：可直接使用Neo4j驱动和工具
- **单容器部署**：Graphiti + FalkorDB可打包为单一Docker镜像，简化运维
- **性能基准**：在8线程并发负载下，FalkorDB吞吐量超过Neo4j和Memgraph

### 发现3：MCP协议使跨AI应用共享记忆成为可能

Graphiti MCP Server让Claude Desktop、Cursor等AI应用通过统一协议访问知识图谱，实现：
- **跨客户端记忆共享**：在不同AI应用间无缝切换而不丢失上下文
- **多租户隔离**：通过`group_id`参数实现租户级内存隔离，"Project A记忆"永远不会泄露到"Project B"
- **标准化接口**：无需编写自定义集成代码，MCP协议提供统一接口

---

## 🔬 技术细节

### 时序知识图谱架构

Graphiti的核心数据结构是三元组 `(Node, Edge, Node)`，其中边（Edge）存储事实（Fact）作为属性。时序信息通过双时间戳实现：

```
Graphiti Knowledge Graph: G = (N, E, φ)

节点类型：
- Episode Nodes (N_e)：包含原始输入数据（消息、文本、JSON）
- Entity Nodes (N_s)：从Episode中提取并解析的实体

边类型：
- Semantic Edges (E_s)：实体间的语义关系
- Temporal Markers：边的时间属性（created_at, expired_at）

Bi-temporal模型：
- Event Time (T)：事件实际发生的时间
- Ingestion Time (T')：数据被摄入图谱的时间

当新Episode中的信息否定或使现有边失效时：
- 设置 expired_at = 当前时间戳
- 保留历史边用于回溯查询
```

### MCP Server 1.0 配置架构

**YAML配置取代环境变量**（breaking change）：

```yaml
# config/config.yaml
database:
  provider: falkordb  # 或 neo4j
  uri: redis://falkordb:6379
  password: ""
  database: default_db

llm:
  provider: openai
  model: gpt-4o
  api_key: ${OPENAI_API_KEY}

embedding:
  provider: openai
  model: text-embedding-3-small

mcp:
  transport: http  # 或 stdio
  host: 0.0.0.0
  port: 8000
```

**支持的LLM提供商**：
- OpenAI (包括GPT-5)
- Anthropic (Claude 4.5)
- Google (Gemini 2.5)
- Groq
- Azure OpenAI

**支持的Embedding提供商**：
- OpenAI
- Voyage AI
- Google Gemini
- Anthropic
- Local models

### 预配置本体（Ontology）

MCP Server 1.0新增9种预配置实体类型，优化真实场景提取精度：

| 实体类型 | 用途 |
|---------|------|
| Preference | 用户偏好、习惯 |
| Requirement | 需求、约束条件 |
| Procedure | 流程、步骤 |
| Location | 地理位置、场所 |
| Event | 事件、活动 |
| Organization | 组织、公司 |
| Document | 文档、文件 |
| Topic | 主题、话题 |
| Object | 物体、对象 |

### 确定性提取与去重机制

**问题**：纯LLM提取在高吞吐场景下产生方差、重试循环和token消耗。

**解决方案**：Graphiti引入确定性、经典信息提取方法：
- 实体解析和去重不再每次都需要模型调用
- 使用经典算法进行实体匹配和消歧
- 显著降低token成本和延迟

### Docker部署方案

**方案一：FalkorDB单容器（推荐）**
```bash
# 使用Docker Compose默认配置
docker compose up -d

# 包含：FalkorDB + FalkorDB Browser UI + Graphiti MCP Server
# 端口：8000 (MCP), 8081 (Browser UI)
```

**方案二：Neo4j分离容器**
```bash
# 使用neo4j专用配置
docker compose -f docker-compose-neo4j.yml up -d

# 包含：独立的Neo4j容器 + Graphiti MCP Server
# Neo4j端口：7687 (Bolt), 7474 (HTTP)
```

**健康检查命令**：
```bash
# 测试Redis连接
docker compose exec graphiti-falkordb redis-cli ping

# 查看FalkorDB日志
docker compose logs graphiti-falkordb

# 查看Neo4j日志
docker compose -f docker-compose-neo4j.yml logs neo4j

# 检查Redis内存
docker compose exec graphiti-falkordb redis-cli info memory
```

---

## 💡 实践案例

### 案例1：Claude Desktop集成

**场景**：在Claude Desktop中配置Graphiti MCP Server，实现跨会话记忆持久化。

**配置步骤**：
1. 启动Graphiti MCP Server（FalkorDB单容器）
2. 在Claude Desktop配置文件中添加MCP服务器：
```json
{
  "mcpServers": {
    "graphiti": {
      "command": "uv",
      "args": ["run", "graphiti_mcp_server.py"],
      "env": {
        "OPENAI_API_KEY": "sk-xxx",
        "DATABASE_PROVIDER": "falkordb"
      }
    }
  }
}
```
3. 重启Claude Desktop，Graphiti出现在可用工具列表中
4. 与Claude对话时，实体和关系自动提取到知识图谱
5. 后续会话可查询历史记忆，实现跨会话一致性

**效果**：用户反馈"可以在Claude Desktop和Cursor之间无缝切换而不丢失上下文"

### 案例2：多租户隔离

**场景**：同一Graphiti实例为多个项目提供记忆服务，确保数据隔离。

**实现方式**：
```python
# 每个请求必须携带group_id
await graphiti.add_episode(
    name="project_a_conversation",
    episode_body="用户讨论项目A的需求",
    group_id="project_a"  # 租户隔离键
)

await graphiti.add_episode(
    name="project_b_conversation", 
    episode_body="用户讨论项目B的需求",
    group_id="project_b"  # 独立命名空间
)

# 查询时自动隔离
results = await graphiti.search(
    query="项目需求",
    group_id="project_a"  # 只返回project_a的知识
)
```

**关键点**：
- `group_id`在存储层强制隔离，不是提示词层面的隔离
- 不同租户的图完全独立，不存在数据泄露风险
- 适合企业级多客户部署

### 案例3：时序推理场景

**场景**：追踪用户偏好随时间的变化。

**示例对话流**：
```
Episode 1 (2025-01-15): "我喜欢吃川菜"
→ 提取：User -> prefers -> Sichuan cuisine (created_at: 2025-01-15)

Episode 2 (2025-06-20): "我现在更喜欢粤菜了"
→ 提取：User -> prefers -> Cantonese cuisine (created_at: 2025-06-20)
→ 更新：Sichuan cuisine边的expired_at = 2025-06-20

查询 "用户当前喜欢什么菜系？"
→ 返回：Cantonese cuisine (active)
→ 历史查询 "用户过去喜欢什么？"
→ 返回：Sichuan cuisine (expired at 2025-06-20)
```

---

## ⚠️ 知识缺口

### 缺口1：Graphiti与现有RAG系统的集成模式

**问题**：Graphiti作为记忆层，如何与传统RAG系统（向量数据库+文档检索）协同工作？

**已知信息**：
- Graphiti专注于动态、时序性知识
- 传统RAG专注于静态文档检索
- 两者可以互补，但缺乏官方集成指南

**需要探索**：
- 混合检索策略：何时用Graphiti，何时用向量检索？
- 数据同步：文档更新如何同步到知识图谱？
- 性能权衡：图查询vs向量搜索的延迟对比

### 缺口2：大规模生产部署的最佳实践

**问题**：Graphiti在千级并发、TB级图谱场景下的扩展策略。

**已知信息**：
- Zep服务曾30倍扩展并在2周内完成
- FalkorDB作为Redis模块，内存消耗是关键瓶颈
- 多租户场景下资源隔离机制不明确

**需要探索**：
- 水平扩展策略：多实例负载均衡？
- 分片策略：按group_id分片还是按时间分片？
- 备份恢复：图谱数据的备份和灾难恢复方案

### 缺口3：实体提取的精度优化

**问题**：如何针对特定领域优化实体提取质量？

**已知信息**：
- 预配置9种实体类型覆盖通用场景
- 支持自定义实体类型（use-custom-entities）
- 缺乏领域适配的具体指导

**需要探索**：
- 自定义实体类型的定义格式和最佳实践
- Few-shot提示词优化策略
- 提取质量评估指标和调优方法

### 缺口4：MCP协议的深度使用

**问题**：MCP协议除了基本的读写操作，还有哪些高级功能？

**已知信息**：
- MCP 1.0支持HTTP Streaming和STDIO传输
- 支持资源（Resources）、工具（Tools）、提示（Prompts）
- 缺乏高级用法的官方文档

**需要探索**：
- 如何实现双向实时同步（图谱变化推送给客户端）？
- MCP的订阅/通知机制如何使用？
- 与其他MCP服务器的协同模式

---

## 🛠️ 实践启发

### 启发1：MCP是AI Agent的"USB接口"

Graphiti MCP Server的成功证明：标准化协议可以极大降低AI应用集成的复杂度。未来应关注：
- MCP生态的其他服务器（数据库、文件系统、浏览器自动化等）
- 如何设计自己的MCP服务器
- MCP与Agent框架（LangChain、LlamaIndex）的集成

### 启发2：时序是Agent记忆的关键维度

传统记忆方案（向量存储、对话历史）缺乏时间维度，导致：
- 无法区分"过去"和"现在"的事实
- 无法追踪观点/偏好的演化
- 无法进行时间相关的推理

Graphiti的双时间戳模型为Agent记忆提供了新的范式，值得在以下场景探索：
- 用户行为分析（偏好变化、习惯形成）
- 项目进度追踪（任务状态演化）
- 知识更新管理（版本、时效性）

### 启发3：图数据库在AI场景的新定位

Graphiti+FalkorDB的组合展示了图数据库在AI时代的独特价值：
- 关系查询：比向量搜索更精确的语义关联
- 可解释性：图谱结构可人工审查和调试
- 多跳推理：支持跨实体的复杂推理链

对比传统方案：
| 维度 | 向量检索 | 知识图谱 |
|------|---------|---------|
| 语义相似度 | ✅ 优秀 | ⚠️ 需结合嵌入 |
| 关系推理 | ❌ 弱 | ✅ 强 |
| 可解释性 | ❌ 黑盒 | ✅ 透明 |
| 时序追踪 | ❌ 无 | ✅ 原生支持 |
| 多跳查询 | ❌ 困难 | ✅ 原生支持 |

---

## 📚 参考资源

- GitHub: https://github.com/getzep/graphiti
- 官方博客: https://blog.getzep.com/graphiti-hits-20k-stars-mcp-server-1-0
- 学术论文: https://arxiv.org/html/2501.13956v1
- FalkorDB集成指南: https://www.falkordb.com/blog/mcp-knowledge-graph-graphiti-falkordb
- Docker部署文档: https://contextqmd.com/libraries/graphiti/versions/0.28.2/pages/mcp_server/docker/README
- MCP服务器目录: https://mcpbro.com/mcp/graphiti-mcp-server

---

## 🎯 后续行动建议

1. **环境搭建**：在本地Docker环境部署Graphiti+FalkorDB，验证基本功能
2. **MCP集成**：在Claude Desktop或Cursor中配置Graphiti MCP，体验跨应用记忆
3. **领域适配**：针对特定业务场景定义自定义实体类型，测试提取精度
4. **性能测试**：模拟多租户场景，评估FalkorDB的并发性能和内存消耗
5. **生态探索**：研究Graphiti与传统RAG系统的混合架构方案

---

*笔记生成时间：2026-05-25*
*主题：Zep Graphiti - 时序知识图谱MCP服务器*

## 相关笔记

- [AI-Agent记忆架构前沿学习](2026-05-01-AI-Agent记忆架构前沿学习.md) — 记忆架构全景
- [Mnemosyne-零依赖AI记忆系统](2026-05-05-Mnemosyne-零依赖AI记忆系统.md) — 轻量记忆方案
- [M-Flow联想记忆引擎](2026-04-21-M-Flow联想记忆引擎.md) — 联想记忆机制
- [Ontology驱动的AI知识引擎](2026-04-01-Ontology驱动的AI知识引擎.md) — 知识图谱架构
- [AI-Agent控制流](2026-05-08-AI-Agent控制流.md) — Agent控制模式
*字数统计：约3500字*

→ 相关：2026-10-18-GraphRAG真实成本工程实测.md
