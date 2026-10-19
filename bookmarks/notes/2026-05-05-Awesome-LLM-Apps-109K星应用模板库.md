# Awesome LLM Apps — 109K⭐ LLM应用模板集合

- 📅 2026-05-05
- ⭐ 3.5/5 — 最大的LLM应用模板库，学习价值高，但代码质量偏教学级
- 🏷️ #开源 #LLM #Agent #RAG #MCP #Streamlit #Agno #LangChain
- 📰 GitHub: Shubhamsaboo/awesome-llm-apps
- 🔗 https://github.com/Shubhamsaboo/awesome-llm-apps

## 摘要

Awesome LLM Apps 是一个拥有 109K Stars 的 LLM 应用模板集合，包含 115+ 个可运行的应用示例，覆盖 AI Agent、RAG、MCP、Voice AI、多Agent协作、Agent Skills、微调等方向。由 Shubham Saboo 创建并维护，Apache-2.0 许可。核心框架是 Agno（原 Phidata）+ Streamlit，RAG 部分走 LangChain 生态。定位是"可运行的LLM应用 Cookbook"而非生产框架，适合学习参考和快速原型验证。

## 核心内容

### 项目画像

| 维度 | 数据 |
|------|------|
| Stars | 109K（GitHub AI 类 Top 级别） |
| Forks | 16.1K |
| 语言 | Python |
| 许可证 | Apache-2.0 |
| Commits | 994 |
| 维护者 | Shubham Saboo + 社区贡献 |
| 最近更新 | 2026-05-04（活跃维护中） |
| 定位 | LLM 应用模板库 / Cookbook |

### 8大分类 × 115+ 应用

| 类别 | 数量 | 核心技术 | 亮点 |
|------|------|----------|------|
| Starter AI Agents | 16 | Agno + Streamlit | 单文件入门，API Key 即跑 |
| Advanced AI Agents | 36（含3子类） | Agno + 多工具 | 生产级：DevOps/研究/金融/法律等 |
| Multi-agent Teams | ~16 | Agno Teams / CrewAI | 多Agent协作完成复杂任务 |
| Voice AI Agents | 4 | Gemini Live / OpenAI SDK | 语音进出实时交互 |
| MCP AI Agents | 6 | Agno + MCPTools | Docker化MCP Server集成 |
| RAG Tutorials | 23 | LangChain + ChromaDB | 从基础Chain到Agentic RAG |
| Agent Skills | 20 | Gemini + ADK | 可复用技能文件，含自优化 |
| Advanced LLM Apps | 10 | 多框架 | 微调/记忆/优化等进阶主题 |

### 代码架构特征

**标准应用模板**（每个应用统一结构）：

    {app_name}/
    ├── README.md          # 说明文档
    ├── {main}.py          # 主程序（单文件，100-400行）
    └── requirements.txt   # 依赖

**Agent 代码模式**（以 travel_agent 为典型）：

    from agno.agent import Agent
    from agno.models.openai import OpenAIChat
    researcher = Agent(name="Researcher", tools=[SerpApiTools()])
    planner = Agent(name="Planner")
    # UI: Streamlit
    st.title("AI Travel Agent")
    result = planner.arun(query)

**RAG 代码模式**（LangChain LCEL 管道）：

    rag_chain = {"context": retriever | format_docs, "question": RunnablePassthrough()} | prompt | model | parser

**MCP 代码模式**（Docker化MCP Server）：

    async with MCPTools(url="ghcr.io/github/github-mcp-server") as tools:
        agent = Agent(tools=[tools])
        result = await agent.arun("List my repos")

### 技术栈全景

| 层级 | 技术 |
|------|------|
| Agent 框架 | Agno（主力）、CrewAI、OpenAI Agents SDK、Google ADK |
| RAG 框架 | LangChain（主力） |
| UI | Streamlit（统一） |
| LLM | GPT-4o、Gemini、Claude、Llama、Qwen、DeepSeek |
| 向量库 | ChromaDB |
| 协议 | MCP |
| 工具 | SerpAPI、Browser Use、Notion/GitHub MCP |
| 部署 | 本地 Streamlit / Docker（MCP Server） |

### 代码质量

✅ 结构一致性高、文档完善、每个示例可独立运行、Provider-agnostic
⚠️ 无测试、无配置管理、API Key明文、单文件架构缺模块化

## 🔍 借鉴点

### ① 有利进化

| # | 借鉴点 | 决定 |
|---|--------|------|
| 1 | Agno 框架作为 Agent 主力 | 不落实：Hermes已有原生agent能力 |
| 2 | Agent Skills 可复用技能文件 | 不落实：Hermes skill系统已覆盖 |
| 3 | Self-Improving Agent Skills | 记录备用，与evolver有交集 |

### ② 有价值

- Agno（原Phidata）轻量Agent框架值得持续关注
- 23种RAG变体分类体系是好的学习路径参考
- Streamlit 快速原型UI模式

### ③ 知识库

- 109K Stars 说明 LLM 学习需求远大于生产需求
- Agno 在 Agent 框架竞争中可能正在胜出
- Provider-agnostic 已成标配

## 🔗 关联性

- [2026-05-05-Voice-Pro-开源AI语音工作室](2026-05-05-Voice-Pro-开源AI语音工作室.md) - 同为开源AI工具分析
- [2026-05-03-AI-Agent-Protocol-Ecosystem-2026-学习](2026-05-03-AI-Agent-Protocol-Ecosystem-2026-学习.md) - MCP协议生态
- autonomous-ai-agents skill - Agno框架覆盖
- evolver skill - Self-Improving概念相关

## 💡 启发

- 模板库 > 框架：109K Stars 说明开发者要"能跑的代码"而非"能学的框架"
- Streamlit 是 LLM 时代的 jQuery：简单但非生产级
- MCP 正在成为标配：Agent连接外部工具的标准协议

## 🔮 预判

- 短期：Stars继续增长，新增Google ADK和MCP示例
- 中期：Agno可能成为Agent框架事实标准之一
- 长期：模板库将演变为LLM应用商店
- jbot行动：暂无。Agno列入观察名单

## 相关笔记
- [2026-05-05-Voice-Pro-开源AI语音工作室](2026-05-05-Voice-Pro-开源AI语音工作室.md)
- [2026-05-03-AI-Agent-Protocol-Ecosystem-2026-学习](2026-05-03-AI-Agent-Protocol-Ecosystem-2026-学习.md)
