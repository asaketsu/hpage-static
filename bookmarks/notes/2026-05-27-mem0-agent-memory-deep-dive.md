# Mem0 AI Agent 记忆框架深度研究

> **日期**: 2026-05-27
> **主题**: Mem0 — 2026 年最主流的 AI Agent 记忆层
> **来源**: Mem0 官方博客/文档/GitHub + vectorize.io 对比评测 + 社区评测
> **相关技能**: agent-memory-selection, mcp-integration
> **深度评级**: L4（可复用工作流/方法）

---

## 一、核心发现

### 发现1：Mem0 在三大基准测试中全面领先（2026 年新算法）

Mem0 于 2026 年 4 月发布了全新的 token 高效记忆算法，基于「单次提取 + 多信号检索」架构，在三大标准化基准上取得突破性成绩：

- **LoCoMo**（1540 题，多会话记忆）: **92.5 分**（旧算法 71.4，提升 +21.1）
- **LongMemEval**（500 题，6 类记忆场景）: **94.4 分**（旧算法 67.8，提升 +26.6）
- **BEAM 1M token 规模**: **64.1 分**（首次有方案在百万 token 级别给出可用结果）
- **BEAM 10M token 规模**: **48.6 分**（千万级 token，仍是开放问题）

关键指标：平均 **~6,900 tokens/query**（对比旧方案 ~26,000），延迟 p50 **<1.1s**。

两大核心改进：
1. **Single-pass ADD-only extraction**：只做 ADD 不做 UPDATE/DELETE，记忆只增不改。Agent 生成的事实（如确认操作、推荐建议）与用户陈述的事实同等权重存储。
2. **Multi-signal retrieval**：三路并行打分——语义相似度 + BM25 关键词 + 实体匹配，融合后输出。时序推理提升 **+29.6 分**，多跳推理提升 **+23.1 分**。

**实践意义**：这证明「记忆不是存对话历史，而是结构化提取 + 智能检索」。对于 Hermes Agent 的启示是——现有 memory 系统（纯 key-value 文本存储）在时序推理和多跳关联方面有明显短板。

### 发现2：记忆分为「个性化记忆」和「机构知识」两大类别

2026 年的 AI Agent 记忆领域已明确分裂为两个正交问题：

| 维度 | 个性化记忆 (Personalization) | 机构知识 (Institutional Knowledge) |
|------|-----|------|
| 目标 | 记住用户偏好、习惯、上下文 | 积累领域经验、操作规则、纠错记录 |
| 跨会话 | 是 | 是（且跨任务/跨用户） |
| 复杂度 | 低（扁平 key-value + 向量即可） | 高（需要图结构、时序推理、实体链接） |
| 典型框架 | LangMem, Mem0, LlamaIndex Memory | Hindsight, Letta, Cognee, Zep/Graphiti |
| Mem0 定位 | **强项**（核心设计目标） | 部分支持（通过 Graph Memory 扩展） |

**Mem0 的架构**：Vector + Graph 混合。基础层用向量数据库存储记忆条目，Graph Memory 层通过实体链接构建知识图谱。这使 Mem0 在个性化记忆方面是当前最强方案，但在深度机构知识（如「供应商 X 需要 Y 格式的 PO」这类操作规则积累）方面不如 Hindsight 和 Letta。

**对 Hermes 的启示**：Hermes 当前的 memory 系统偏向「机构知识」（存储环境配置、工具命令等），缺少「个性化记忆」层（用户偏好、交互习惯）。Mem0 可以补足这块短板。

### 发现3：Mem0 的集成生态极其成熟（21 框架 + MCP 支持）

Mem0 在集成深度上远超竞品：

- **21 个 AI 框架集成**：LangChain, CrewAI, Vercel AI SDK, AutoGen, LangGraph 等
- **20 个向量数据库支持**：Qdrant（默认）, Chroma, Milvus, Pinecone, Weaviate, PGVector 等
- **MCP Server**：`https://mcp.mem0.ai`，任何支持 MCP 的客户端可直接接入
- **CLI 工具**：`mem0 add/search` 命令行操作，Agent 可在 <5 秒内自注册 API Key（无需邮箱）
- **Skills 标准**：为 Claude Code/Codex/Cursor 等 AI 编程工具提供了标准化 Skill

**Agent 自注册机制**（极其创新）：
```bash
mem0 init --agent --agent-caller claude-code  # 5秒内获得 API key
mem0 add "I prefer dark mode"                  # 写入记忆
mem0 search "interface preference"             # 检索记忆
```
人类 owner 后续可通过 `mem0 init --email` 认领账号，记忆无缝转移。

---

## 二、技术细节与代码示例

### 2.1 安装配置

```bash
# 基础安装（纯 Python SDK）
pip install mem0ai

# 增强版（含 NLP 支持：BM25 关键词 + 实体提取）
pip install mem0ai[nlp]
python -m spacy download en_core_web_sm

# CLI 工具
pip install mem0-cli
# 或
npm install -g @mem0/cli

# 自托管（Docker 一键部署）
cd server && docker compose up -d
```

### 2.2 核心API：写入/检索/更新/删除

**Platform 模式**（托管服务，推荐）：

```python
from mem0 import MemoryClient

client = MemoryClient(api_key="your-api-key")

# 写入记忆（支持消息列表格式）
client.add(
    [{"role": "user", "content": "我喜欢用 Python 写量化策略"}],
    user_id="jc"
)

# 检索记忆
results = client.search("编程语言偏好", user_id="jc")
# 返回: [{"id": "...", "memory": "喜欢用 Python", "score": 0.92, ...}]

# 获取全部记忆
all_memories = client.get_all(user_id="jc")

# 更新记忆
client.update(memory_id="mem_xxx", data="偏好 Python + Rust 双语言")

# 删除
client.delete(memory_id="mem_xxx")
client.delete_all(user_id="jc")
```

**OSS 模式**（自托管，需要配置 LLM 和 Embedding）：

```python
from mem0 import Memory

# 默认使用 OpenAI（需 OPENAI_API_KEY）
m = Memory()

# 自定义 LLM（如用本地 Ollama）
from mem0 import Memory

config = {
    "llm": {
        "provider": "ollama",
        "config": {
            "model": "qwen2.5:7b",
            "base_url": "http://localhost:11434",
        }
    },
    "embedder": {
        "provider": "ollama",
        "config": {
            "model": "nomic-embed-text",
            "base_url": "http://localhost:11434",
        }
    },
    "vector_store": {
        "provider": "chroma",
        "config": {
            "collection_name": "hermes_memories",
            "path": "./mem0_db",
        }
    }
}

m = Memory.from_config(config)

# CRUD 操作同 Platform，但不需要 API key
m.add("Jetson Orin Nano 是我的主要开发环境", user_id="jc", metadata={"category": "env"})
results = m.search("开发环境", user_id="jc")
```

### 2.3 记忆分层机制

Mem0 支持三级记忆作用域：

```python
# User 级别：跨会话的个人偏好
m.add("偏好简洁输出", user_id="jc")

# Session 级别：单次会话上下文
m.add("正在调试 ESP32 固件", user_id="jc", session_id="sess_123")

# Agent 级别：Agent 自身的状态和知识
m.add("已知 Jetson Orin GPU 驱动版本 35.x", agent_id="hermes")
```

### 2.4 Graph Memory（图记忆）

2026 年新增的 Graph Memory 功能，通过实体链接构建知识图谱：

```python
# 启用 Graph Memory
client.add(
    [{"role": "user", "content": "Alice 是项目经理，Bob 是开发负责人"}],
    user_id="jc",
    graph_memory=True
)

# 图查询
graph_results = client.search(
    "项目经理是谁",
    user_id="jc",
    graph_memory=True
)
```

### 2.5 与 LangChain/LangGraph 集成

```python
from langchain.memory import ConversationBufferMemory
from mem0 import Memory

memory = Memory()

# 作为 LangChain 的记忆后端
from langchain.agents import AgentExecutor

# LangGraph 集成（推荐用于复杂 Agent 工作流）
from langgraph.graph import StateGraph
# Mem0 提供 langgraph_checkpoint 兼容的记忆存储
```

### 2.6 MCP 接入

Mem0 提供了官方 MCP Server，任何支持 MCP 的 Agent 可直接使用：

```json
{
  "mcpServers": {
    "mem0": {
      "url": "https://mcp.mem0.ai",
      "headers": {
        "Authorization": "Bearer your-api-key"
      }
    }
  }
}
```

---

## 三、与竞品对比

| 维度 | Mem0 | Zep/Graphiti | Hindsight | Letta | Hermes 内置 |
|------|------|-------------|-----------|-------|------------|
| **GitHub Stars** | ~48K | ~24K | ~4K | ~21K | N/A |
| **核心架构** | Vector + Graph | 时序知识图谱 | 多策略混合 | 分层(OS 式) | key-value 文本 |
| **个性化记忆** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐ |
| **机构知识** | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ |
| **时序推理** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | ⭐ |
| **自托管** | ✅ Docker | ✅ Graphiti | ✅ | ✅ | ✅ 原生 |
| **集成生态** | 21 框架 | 10+ | 5+ | 5+ | Hermes 专用 |
| **MCP 支持** | ✅ 官方 | ✅ | ❌ | ❌ | ✅ 原生 |
| **本地 LLM** | ✅ Ollama | ⚠️ 需配置 | ✅ | ✅ | ✅ |
| **token 效率** | 6.9K/query | 未公布 | 未公布 | 未公布 | N/A |

**Mem0 的核心优势**：
1. 个性化记忆领域绝对领先（LoCoMo 92.5, LongMemEval 94.4）
2. 集成生态最广，MCP 开箱即用
3. Agent 自注册机制极其创新
4. OSS 版本 Apache 2.0，无锁定

**Mem0 的不足**：
1. 深度机构知识不如 Hindsight（后者的多策略混合更适合操作规则积累）
2. 时序推理虽有大提升但仍不如 Zep/Graphiti（后者基于 FalkorDB 时序知识图谱）
3. Graph Memory 功能仍较新，生产可靠性待验证
4. 默认依赖 OpenAI（OSS 版可换，但需要额外配置）

---

## 四、实践启发：Hermes Agent 集成路径

### 4.1 推荐集成方式：OSS 模式 + Ollama

Hermes 运行在 Jetson Orin Nano 上，适合用 OSS 模式 + 本地 Ollama 运行 Mem0，避免外部 API 依赖：

```python
# Hermes Mem0 配置（适配 Jetson Orin）
config = {
    "llm": {
        "provider": "ollama",
        "config": {
            "model": "qwen2.5:7b",  # 已在本机运行
            "base_url": "http://localhost:11434",
        }
    },
    "embedder": {
        "provider": "ollama",
        "config": {
            "model": "nomic-embed-text",
            "base_url": "http://localhost:11434",
        }
    },
    "vector_store": {
        "provider": "chroma",
        "config": {
            "collection_name": "hermes_personalization",
            "path": "/home/jc/.hermes/mem0_db",
        }
    }
}
```

### 4.2 互补而非替代

Mem0 应作为 Hermes 现有 memory 系统的**补充层**，而非替代：

| 层次 | 工具 | 用途 |
|------|------|------|
| L1 | Hermes memory（现有） | 环境事实、工具命令、项目约定 |
| L2 | Mem0（新增） | 用户偏好、交互习惯、跨会话个性化 |
| L3 | Session search（现有） | 历史对话检索 |

### 4.3 具体场景

1. **用户偏好记忆**：`m.add("jc 偏好繁体中文回复", user_id="jc")` → 每次 session 启动时检索并注入 system prompt
2. **纠正记录**：`m.add("jc 纠正：不要在非授权操作中使用 rm -rf", user_id="jc")` → 逐步积累操作规范
3. **项目上下文**：`m.add("当前项目使用 ESP-IDF 5.3", user_id="jc", metadata={"project": "voicebox"})` → 项目切换时自动加载

---

## 五、知识缺口与待验证假设

1. **Jetson Orin 性能瓶颈**：Mem0 的 NLP 增强模式（BM25 + 实体提取）需要 spacy 模型，在 Jetson 上的推理延迟未验证。假设 qwen2.5:7b 足够处理记忆提取，但需实测。
2. **Graph Memory 成熟度**：Mem0 的 Graph Memory 是 2026 年新增功能，生产稳定性存疑。Zep/Graphiti 在时序知识图谱领域更成熟。
3. **与 Hermes memory 冲突**：两套记忆系统并存可能导致信息重复或不一致。需要设计去重/优先级策略。
4. **MCP Server 路由**：Mem0 MCP Server 托管在 `mcp.mem0.ai`，如果 Hermes 通过 MCP 接入，每次记忆操作都走外网。对于 Jetson 上的本地 Agent，应优先用 OSS 模式。
5. **记忆过期/遗忘机制**：Mem0 的 ADD-only 策略意味着记忆只增不减，长期运行后可能出现记忆膨胀。何时触发清理、如何判断过时，是未解决的问题。
6. **多 Agent 协作记忆**：Hermes 有多个 Agent（jbot/ubot/abot），Mem0 的 user_id/agent_id 分离是否能有效支持多 Agent 共享记忆，需要实验验证。

---

## 六、参考资料

1. Mem0 官方博客：State of AI Agent Memory 2026 (https://mem0.ai/blog/state-of-ai-agent-memory-2026)
2. Mem0 GitHub (https://github.com/mem0ai/mem0) — ~48K stars, Apache 2.0
3. Mem0 官方文档 (https://docs.mem0.ai/overview)
4. vectorize.io: Best AI Agent Memory Systems in 2026 (https://vectorize.io/articles/best-ai-agent-memory-systems)
5. ECAI 2025 论文：arXiv:2504.19413
6. LoCoMo/LongMemEval/BEAM 基准测试：github.com/mem0ai/memory-benchmarks

---

> ⚠️ **进化评估待执行**：本笔记完成后需评估是否创建 mem0-integration skill 或 patch agent-memory-selection skill。

## 相关笔记
- [Agent Skills才是关键抽象层](2026-04-02-Agent Skills才是关键抽象层.md)
- [Claude-Code四层记忆架构](2026-04-03-Claude-Code四层记忆架构.md)
- [Claude-Code-324-prompts-analysis](2026-04-04-Claude-Code-324-prompts-analysis.md)
- [Hermes-Agent-competitor-analysis](2026-04-05-Hermes-Agent-competitor-analysis.md)
- [SelfImproving-Agent-CLI-infra](2026-04-05-SelfImproving-Agent-CLI-infra.md)
- [spatial-intelligence-agent-action](2026-04-05-spatial-intelligence-agent-action.md)
- [agent-loop-core-scheduling](2026-04-07-agent-loop-core-scheduling.md)
- [email-not-revival-agent-needs-it](2026-04-07-email-not-revival-agent-needs-it.md)
- [hermes-agent-deep-dive-evolution-roadmap](2026-04-07-hermes-agent-deep-dive-evolution-roadmap.md)
- [claude-code-tool-execution-orchestration](2026-04-08-claude-code-tool-execution-orchestration.md)
- [SKILL-md-ai-agent-skills](2026-04-09-SKILL-md-ai-agent-skills.md)
- [gbrain-hybrid-search-proposal](2026-04-11-gbrain-hybrid-search-proposal.md)
- [4-ai-agent-frameworks-comparison](2026-04-13-4-ai-agent-frameworks-comparison.md)
- [hermes-agent-vs-openclaw](2026-04-13-hermes-agent-vs-openclaw.md)
- [Cloudflare-EmDash-AI-Agent-CMS](2026-04-14-Cloudflare-EmDash-AI-Agent-CMS.md)
- [Gemini3-AI-Agent-competition](2026-04-16-Gemini3-AI-Agent-competition.md)
- [Hermes-Agent-v0.10.0-insight](2026-04-18-Hermes-Agent-v0.10.0-insight.md)
- [Hermes-Agent-v0.10.0-release-analysis](2026-04-18-Hermes-Agent-v0.10.0-release-analysis.md)
- [Claude-Opus4.7-Claude-Code-最佳实践](2026-04-20-Claude-Opus4.7-Claude-Code-最佳实践.md)
- [ESP-Claw扩展分析-NeuroClaw边缘AI-Agent](2026-04-22-ESP-Claw扩展分析-NeuroClaw边缘AI-Agent.md)
- [MCP协议与Agentic-LLM-2025趋势](2026-04-23-MCP协议与Agentic-LLM-2025趋势.md)
- [深入源码-Hermes-Agent-如何实现Self-Improving](2026-04-23-深入源码-Hermes-Agent-如何实现Self-Improving.md)
- [深入源码Hermes-Agent-Self-Improving](2026-04-23-深入源码Hermes-Agent-Self-Improving.md)
- [MCP协议生态与Agentic-RAG架构深度学习](2026-04-27-MCP协议生态与Agentic-RAG架构深度学习.md)
- [LLM-Agent驱动量化交易系统前沿学习](2026-04-29-LLM-Agent驱动量化交易系统前沿学习.md)
- [Meta-Hyperagents自适应Agent框架](2026-04-30-Meta-Hyperagents自适应Agent框架.md)
- [stoc蒸馏-AI-Agent自学习量化交易系统](2026-04-30-stoc蒸馏-AI-Agent自学习量化交易系统.md)
- [AI-Agent记忆架构前沿学习](2026-05-01-AI-Agent记忆架构前沿学习.md)
- [deepseek-agent-ecosystem](2026-05-01-deepseek-agent-ecosystem.md)
- [AI-Agent-Protocol-Ecosystem-2026-学习](2026-05-03-AI-Agent-Protocol-Ecosystem-2026-学习.md)
- [ai-agent-resources-ecosystem](2026-05-03-ai-agent-resources-ecosystem.md)
- [智能教育-自适应评估](2026-05-03-智能教育-自适应评估.md)
- [Agent协议生态2026最新进展-MCP-A2A深度融合](2026-05-04-Agent协议生态2026最新进展-MCP-A2A深度融合.md)
- [个人Agent自进化五步闭环](2026-05-04-个人Agent自进化五步闭环.md)
- [Claude-MCP直连Fusion-Blender-AI操控工业设计](2026-05-05-Claude-MCP直连Fusion-Blender-AI操控工业设计.md)
- [Claude创意连接器9大工具-Blender-MCP深度解析](2026-05-05-Claude创意连接器9大工具-Blender-MCP深度解析.md)
- [Zero-to-CAD-Agent闭环合成百万级可执行CAD程序](2026-05-05-Zero-to-CAD-Agent闭环合成百万级可执行CAD程序.md)
- [tradingagents-deep-analysis](2026-05-05-tradingagents-deep-analysis.md)
- [SOUL-md-Agent-Partner-Transformation](2026-05-07-SOUL-md-Agent-Partner-Transformation.md)
- [Superpowers-Agentic技能框架](2026-05-07-Superpowers-Agentic技能框架.md)
- [AI-Agent控制流](2026-05-08-AI-Agent控制流.md)
- [addyosmani-agent-skills生产级Agent技能包](2026-05-08-addyosmani-agent-skills生产级Agent技能包.md)
- [企业AI转型三步法-知识库技能化智能体](2026-05-08-企业AI转型三步法-知识库技能化智能体.md)
- [AG-UI-AI-Agent前端标准](2026-05-09-AG-UI-AI-Agent前端标准.md)
- [Agent-native-PM方法论](2026-05-09-Agent-native-PM方法论.md)
- [Claude-Code工程师放弃Markdown转HTML](2026-05-09-Claude-Code工程师放弃Markdown转HTML.md)
- [OfficeCLI-AI-Agent的Office工具](2026-05-09-OfficeCLI-AI-Agent的Office工具.md)
- [AI趋势2026-推理时计算与反思Agent](2026-05-11-AI趋势2026-推理时计算与反思Agent.md)
- [具身智能2026-世界模型VLA车企入局](2026-05-11-具身智能2026-世界模型VLA车企入局.md)
- [具身智能2026从实验到实战](2026-05-11-具身智能2026从实验到实战.md)
- [Claude-3D-CAD-创意连接器深度分析](2026-05-13-Claude-3D-CAD-创意连接器深度分析.md)
- [Agent工程4月实践-不要一上来就做Agent](2026-05-14-Agent工程4月实践-不要一上来就做Agent.md)
- [HTML-Anything-Agent驱动HTML编辑器](2026-05-14-HTML-Anything-Agent驱动HTML编辑器.md)
- [MATLAB-Agentic-Toolkit分析](2026-05-14-MATLAB-Agentic-Toolkit分析.md)
- [手撸Agent-ReAct-Loop从零实现](2026-05-14-手撸Agent-ReAct-Loop从零实现.md)
- [上下文才是Agent的命门-QClaw上下文竞争论](2026-05-15-上下文才是Agent的命门-QClaw上下文竞争论.md)
- [OpenHuman-记忆树AI智能体-i龙虾](2026-05-16-OpenHuman-记忆树AI智能体-i龙虾.md)
- [PicoClaw-超轻量AI-Agent框架](2026-05-16-PicoClaw-超轻量AI-Agent框架.md)
- [具身智能前沿学习](2026-05-17-具身智能前沿学习.md)
- [Agent元认知-LLM不确定性感知](2026-05-18-Agent元认知-LLM不确定性感知.md)
- [SmallRustHermes-Agent自我进化三个闭环](2026-05-18-SmallRustHermes-Agent自我进化三个闭环.md)
- [agent-memory-systems-comparison](2026-05-18-agent-memory-systems-comparison.md)
- [具身智能机器人2025十大趋势](2026-05-18-具身智能机器人2025十大趋势.md)
- [Qwen3.7-Agent Frontier](2026-05-21-Qwen3.7-Agent Frontier.md)
- [react-agent-llm-agentic-training-research](2026-05-21-react-agent-llm-agentic-training-research.md)
- [Agent自我进化与学习系统-深度研究](2026-05-22-Agent自我进化与学习系统-深度研究.md)
- [Hermes-Agent四层记忆架构深度分析](2026-05-22-Hermes-Agent四层记忆架构深度分析.md)
- [OpenClaw日常聊天黑化Agent-ULSPB安全研究](2026-05-22-OpenClaw日常聊天黑化Agent-ULSPB安全研究.md)
- [Domain-Camouflaged-Injection-Attacks-域伪装注入绕过多Agent检测](2026-05-23-Domain-Camouflaged-Injection-Attacks-域伪装注入绕过多Agent检测.md)
- [Microsoft取消ClaudeCode许可-AI编码战企业政治](2026-05-23-Microsoft取消ClaudeCode许可-AI编码战企业政治.md)
- [Superset-YC-P26-AI-Agent-IDE](2026-05-23-Superset-YC-P26-AI-Agent-IDE.md)
- [AI编码工具战争-CodexClaudeCodeCursor收敛为分层架构](2026-05-24-AI编码工具战争-CodexClaudeCodeCursor收敛为分层架构.md)
- [Cloudflare-Agents-Week-2026-Agentic-Cloud全栈基础设施](2026-05-24-Cloudflare-Agents-Week-2026-Agentic-Cloud全栈基础设施.md)
- [PiAgent深度分析](2026-05-24-PiAgent深度分析.md)
- [Agent-Harness-Engineering-从Prompt到Harness的范式跃迁](2026-05-25-Agent-Harness-Engineering-从Prompt到Harness的范式跃迁.md)
- [Claude-Code之父Boris-Cherny-编程已死千级Agent夜间打工](2026-05-25-Claude-Code之父Boris-Cherny-编程已死千级Agent夜间打工.md)
- [DeepSeek-Reasonix-开源省钱Agent](2026-05-25-DeepSeek-Reasonix-开源省钱Agent.md)
- [浅浅走入Hermes-Agent的记忆-毛毛MA](2026-05-25-浅浅走入Hermes-Agent的记忆-毛毛MA.md)
- [高德OPC自主增长系统-Harness多Agent架构](2026-05-25-高德OPC自主增长系统-Harness多Agent架构.md)
- [Agent架构关键变化-Harness成为新后端](2026-05-26-Agent架构关键变化-Harness成为新后端.md)
- [agent-skills-ai-操作手册](2026-05-26-agent-skills-ai-操作手册.md)
- [ai-agent-mas-production](2026-05-26-ai-agent-mas-production.md)
- [hermes-agent-5-usage](2026-05-26-hermes-agent-5-usage.md)
- [45个HermesAgent自动化案例（上）](2026-05-27-45个HermesAgent自动化案例（上）.md)
- [ai-agent-2026-deep-dive](2026-05-27-ai-agent-2026-deep-dive.md)
- [ai-agent-quant-trading-trends](2026-05-27-ai-agent-quant-trading-trends.md)
- [ai-agent-quant-trends](2026-05-27-ai-agent-quant-trends.md)
- [Agent需要RAG吗-协同vs高可信](2026-05-28-Agent需要RAG吗-协同vs高可信.md)
- [ai-agent-trends](2026-05-28-ai-agent-trends.md)
- [nt-structured-output-multi-agent-alpha-research](2026-ai-agent-structured-output-multi-agent-alpha-research.md)
- [20260513-llm-wiki-obsidian-gbrain-知识自组织与自进化](20260513-llm-wiki-obsidian-gbrain-知识自组织与自进化.md)
- [Pi-Agent-vs-Hermes-vs-Claude-Code对比分析](Pi-Agent-vs-Hermes-vs-Claude-Code对比分析.md)
- [ai-agent-2026-trends-learning](ai-agent-2026-trends-learning.md)
- [不管用ClaudeCode还是OpenClaw先记住这12个知识](ai-agent/2026-04-15-不管用ClaudeCode还是OpenClaw先记住这12个知识.md)
- [智能教育-personalized-learning](ai-agent/2026-05-04-智能教育-personalized-learning.md)
- [0元打通Claude-Codex-OpenCode免费模型6入口](ai-agent/2026-05-11-0元打通Claude-Codex-OpenCode免费模型6入口.md)
- [HuggingFace-春季生态-Agentic-World-Modeling](ai-agent/2026-05-13-HuggingFace-春季生态-Agentic-World-Modeling.md)
- [具身智能量产关键年](ai-agent/2026-05-15-具身智能量产关键年.md)
- [anthropic-managed-agents-dreaming-outcomes](anthropic-managed-agents-dreaming-outcomes.md)
- [智能教育-AI-tutoring](explore/2026-05-05-智能教育-AI-tutoring.md)
- [ai-agent-protocol-stack-2026](explore/2026-05-06-ai-agent-protocol-stack-2026.md)
- [ai-agent-protocol-wars-a2a-mcp](explore/2026-05-08-ai-agent-protocol-wars-a2a-mcp.md)
- [ai-coding-agent-competition-landscape](explore/2026-05-08-ai-coding-agent-competition-landscape.md)
- [2025年5月AI大爆发-Claude4-Qwen3-DeepSeek-R1](explore/2026-05-09-2025年5月AI大爆发-Claude4-Qwen3-DeepSeek-R1.md)
- [ai-agent-protocols-mcp-a2a-acp](explore/2026-05-09-ai-agent-protocols-mcp-a2a-acp.md)
- [开源AI春季爆发-模型推理Agent](explore/2026-05-09-开源AI春季爆发-模型推理Agent.md)
- [mcp-a2a-agent-ecosystem](explore/2026-05-10-mcp-a2a-agent-ecosystem.md)
- [ai-agent-protocols-mcp-a2a](explore/2026-05-11-ai-agent-protocols-mcp-a2a.md)
- [AI-Agent架构-MCP-A2A协议栈](explore/2026-05-13-AI-Agent架构-MCP-A2A协议栈.md)
- [Agentic-SOC-安全自动化的范式转变](explore/2026-05-13-Agentic-SOC-安全自动化的范式转变.md)
- [Agentic-Engineering-从Vibe-Coding到Agent工程](explore/2026-05-14-Agentic-Engineering-从Vibe-Coding到Agent工程.md)
- [ai-agent-architecture](explore/2026-05-15-ai-agent-architecture.md)
- [ai开源生态-huggingface春季](explore/2026-05-15-ai开源生态-huggingface春季.md)
- [AI-Agent-协议生态-深度整合学习](explore/2026-05-16-AI-Agent-协议生态-深度整合学习.md)
- [Agentic-AI元年-智能体全面落地趋势](explore/2026-05-16-Agentic-AI元年-智能体全面落地趋势.md)
- [HuggingFace-Spring2026-开源生态报告](explore/2026-05-16-HuggingFace-Spring2026-开源生态报告.md)
- [qclaw-上下文四层模型](explore/2026-05-16-qclaw-上下文四层模型.md)
- [具身智能-从造产品到抢落地六大趋势](explore/2026-05-16-具身智能-从造产品到抢落地六大趋势.md)
- [竞品动态-Agentic-Engineering范式转变](explore/2026-05-16-竞品动态-Agentic-Engineering范式转变.md)
- [agent-collaboration-self-evolution](explore/2026-05-17-agent-collaboration-self-evolution.md)
- [具身智能2026数据规模化元年](explore/2026-05-17-具身智能2026数据规模化元年.md)
- [RD-Agent-Quant-multi-agent-quant-framework-deep-dive](explore/2026-05-18-RD-Agent-Quant-multi-agent-quant-framework-deep-dive.md)
- [agent-self-evolution-quant-trading](explore/2026-05-18-agent-self-evolution-quant-trading.md)
- [多模态Agent框架对比2026-深度探索](explore/2026-05-18-多模态Agent框架对比2026-深度探索.md)
- [IBM2026多智能体趋势](explore/2026-05-19-IBM2026多智能体趋势.md)
- [agent-self-evolution-reflexion-metacognition](explore/2026-05-19-agent-self-evolution-reflexion-metacognition.md)
- [AgentSelfEvolution-LearningSystem-深度探索](explore/2026-05-20-AgentSelfEvolution-LearningSystem-深度探索.md)
- [Hermes-Agent源码解析-越用越聪明的秘密](explore/2026-05-20-Hermes-Agent源码解析-越用越聪明的秘密.md)
- [TencentDB-Agent-Memory架构深度分析与进化建议](explore/2026-05-20-TencentDB-Agent-Memory架构深度分析与进化建议.md)
- [Agent自我进化-Reflexion-ReAct-元认知框架](explore/2026-05-21-Agent自我进化-Reflexion-ReAct-元认知框架.md)
- [开源具身智能项目横评-LeRobot-OpenVLA-RT2](explore/2026-05-21-开源具身智能项目横评-LeRobot-OpenVLA-RT2.md)
- [零信任安全2026-Agent系统新攻击面与安全基线-深度蒸馏](explore/2026-05-21-零信任安全2026-Agent系统新攻击面与安全基线-深度蒸馏.md)
- [GROW开放世界VLM-Agent强化学习框架](explore/2026-05-22-GROW开放世界VLM-Agent强化学习框架.md)
- [agent-evolution-rag](explore/2026-05-23-agent-evolution-rag.md)
- [Harness-工程-AI-编程智能体成功率从20%到100%](explore/2026-05-24-Harness-工程-AI-编程智能体成功率从20%到100%.md)
- [MOSS自主Agent源码级自进化](explore/2026-05-24-MOSS自主Agent源码级自进化.md)
- [SkillOpt-Agent技能自进化](explore/2026-05-26-SkillOpt-Agent技能自进化.md)
- [ai-agent-quant-trading-2026-trends](explore/2026-05-27-ai-agent-quant-trading-2026-trends.md)
- [agent-capability-boundary-detection-20260518](explore/agent-capability-boundary-detection-20260518.md)
- [agent-drift-stability-degradation-20260518](explore/agent-drift-stability-degradation-20260518.md)
- [agent-stability-degradation-drift-detection](explore/agent-stability-degradation-drift-detection.md)
- [tradingagents-cn-deep-20260520](explore/tradingagents-cn-deep-20260520.md)
- [google-a2a-protocol-multi-agent-2026-05-19](google-a2a-protocol-multi-agent-2026-05-19.md)
- [hermes-agent-arxiv-search](hermes-agent-arxiv-search.md)
- [hermes-agent-源码拆解自我进化机制](hermes-agent-源码拆解自我进化机制.md)
- [AI幻觉案例分析-Hermes-Agent不实报道](hermes-agent/2026-04-19-AI幻觉案例分析-Hermes-Agent不实报道.md)
- [深入源码-Hermes-Agent-Self-Improving源码拆解](hermes-agent/2026-04-24-深入源码-Hermes-Agent-Self-Improving源码拆解.md)
- [agent-coding-playbook-analysis](hermes-agent/2026-05-05-agent-coding-playbook-analysis.md)
- [具身智能机器人2025年终盘点](hermes-agent/2026-05-05-具身智能机器人2025年终盘点.md)
- [具身智能机器人2025-商业化元年](hermes-agent/2026-05-09-具身智能机器人2025-商业化元年.md)
- [claude-learning-roadmap](hermes-agent/2026-05-10-claude-learning-roadmap.md)
- [HTML的不合理有效性-Claude-Code-团队](hermes-agent/2026-05-16-HTML的不合理有效性-Claude-Code-团队.md)
- [GenericAgent](hermes-agent/GenericAgent.md)
- [llm-wiki-gbrain-agent-evolution_33aa818c](llm-wiki-gbrain-agent-evolution_33aa818c.md)
- [proactive-learn-2026-05-27-ai-agent-quant](proactive-learn-2026-05-27-ai-agent-quant.md)
- [skills-autonomous-ai-agents](skills-autonomous-ai-agents.md)
- [竞品吸收笔记_GenericAgent](竞品吸收笔记_GenericAgent.md)
