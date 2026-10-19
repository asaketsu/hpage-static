# 🐾 AI Agent 2026 前沿趋势学习笔记

**学习日期**: 2026-05-27  
**学习主题**: AI Agent 2026 最新趋势 + 量化交易新技术  
**学习时长**: 约45分钟  
**信息源**: arXiv最新论文、GitHub Trending、技术博客

---

## 📌 核心发现

### 发现一：多Agent编排架构的"原语化"趋势

**现象**：2026年AI Agent系统架构正在从"单体智能体"向"原语组合系统"演进。

**技术细节**：
- **GENESIS框架**（arXiv:2605.27360，2026年5月26日提交）提出三原语架构：
  - **Agents（智能体）**：执行单元，负责具体任务
  - **Skills（技能）**：可复用能力模块
  - **Hooks（钩子）**：事件触发和状态同步机制
  - **SYNAPSE知识层**：作为"事实来源"和"产物接收器"，实现能力跨运行累积

- **ECC系统**（GitHub 195k⭐）验证了这一模式的工业级可行性：
  - 技能库、本能层、记忆系统、安全护栏、研究优先开发
  - 支持Claude Code、Codex、Opencode、Cursor等多平台

- **MUSE-Autoskill**（华为，arXiv:2605.27366）提出自进化Agent：
  - 技能创建 → 记忆管理 → 评估反馈闭环
  - 30页论文，含8图13表

**代码示例**（GENESIS伪代码）：
```python
class GENESIS:
    def __init__(self):
        self.agents = AgentPool()
        self.skills = SkillRegistry()
        self.hooks = HookManager()
        self.synapse = KnowledgeLayer()  # 持久化知识层
    
    def execute(self, intent: str) -> Solution:
        # 1. 意图解析 → 技能匹配
        skills = self.synapse.match(intent)
        # 2. 编排Agent执行
        agents = self.agents.compose(skills)
        # 3. 执行并反馈
        result = agents.run()
        # 4. 知识沉淀
        self.synapse.store(result, artifacts)
        return result
```

**实践启发**：
- 构建Agent系统时应采用"原语分离"设计，而非单体大模型
- 知识层（SYNAPSE模式）是实现能力累积的关键，需设计持久化存储
- 技能注册表应支持跨Agent共享，避免重复开发

**知识缺口**：
- GENESIS框架的开源代码尚未发布，需等待后续更新
- SYNAPSE知识层的具体数据结构和技术实现细节不明

---

### 发现二：交互式知识图谱成为Agent理解代码的新范式

**现象**：GitHub Trending第一名 `Understand-Anything`（37.4k⭐，+4.7k/天）展示代码理解的新方向。

**技术细节**：
- **核心理念**："Graphs that teach > graphs that impress"（教学型图谱 > 展示型图谱）
- **功能**：将任意代码转换为可探索、可搜索、可问答的交互式知识图谱
- **平台兼容**：Claude Code、Codex、Cursor、Copilot、Gemini CLI等
- **技术栈**：TypeScript，547次提交，活跃开发中

**架构分析**：
```
代码 → 语义解析 → 知识图谱 → 交互界面
         ↓
    嵌入向量 + 关系抽取
         ↓
    图数据库存储
         ↓
    前端交互式探索
```

**实践启发**：
- Agent系统应集成知识图谱作为"第二记忆层"
- 代码库理解不应仅靠向量检索，需结合结构化图关系
- 图谱的"教学性"设计（可探索、可问答）比"展示性"更重要

**知识缺口**：
- 图谱构建的自动化程度和人工干预需求
- 大规模代码库（10万+文件）的性能优化策略

---

### 发现三：Agent插件生态标准化加速

**现象**：Anthropic官方推出 `knowledge-work-plugins`（16.9k⭐），标志着Agent插件生态进入标准化阶段。

**技术细节**：
- **插件类型**：主要为知识工作者设计的工具插件
- **生态规模**：80个提交，42个分支，77个PR
- **标准化方向**：
  - MCP（Model Context Protocol）集成
  - 插件验证和安全性扫描
  - Workload Identity Federation认证

**插件分类**（从目录结构推断）：
- bio-research：生物研究工具
- cowork-plugin-management：协作插件管理
- 各平台适配插件（.claude-plugin, .codex-plugin等）

**实践启发**：
- 未来Agent开发应优先考虑插件化设计
- 插件需遵循标准化协议（如MCP）以便跨平台复用
- 安全性扫描和身份认证是插件生态的基石

**知识缺口**：
- 插件开发的具体SDK和API文档
- 插件市场的商业模式和分发机制

---

## 🔬 技术深度分析

### 1. 自进化Agent架构

**MUSE-Autoskill** 提出的自进化闭环：
```
┌─────────────────────────────────────────────┐
│              自进化闭环                       │
│  ┌──────────┐    ┌──────────┐               │
│  │ 技能创建  │───▶│ 记忆管理  │               │
│  └──────────┘    └──────────┘               │
│       ▲                │                     │
│       │                ▼                     │
│  ┌──────────┐    ┌──────────┐               │
│  │ 评估反馈  │◀───│ 执行应用  │               │
│  └──────────┘    └──────────┘               │
└─────────────────────────────────────────────┘
```

**关键创新**：
- 技能不再是静态配置，而是动态创建和演化
- 记忆系统支持技能间的知识迁移
- 评估机制确保进化方向的正确性

### 2. 知识层（SYNAPSE）设计模式

GENESIS框架的知识层设计：
- **双重角色**：既是"事实来源"（source of ground truth），也是"产物接收器"（recipient of artifacts）
- **能力累积**：每次运行的成果都沉淀到知识层，实现跨运行能力增长
- **持久化存储**：确保技能、经验、错误模式等可跨会话复用

**实现建议**：
```python
class SYNAPSE:
    def __init__(self, storage_backend):
        self.storage = storage_backend  # 支持向量+图+文档混合存储
        self.index = HybridIndex()  # 关键词+语义双索引
    
    def store(self, artifact: Artifact, context: dict):
        # 结构化存储
        self.storage.save(artifact, metadata=context)
        # 更新索引
        self.index.update(artifact.embedding, artifact.keywords)
        # 触发关联技能更新
        self._update_related_skills(artifact)
    
    def retrieve(self, query: str, top_k=5) -> List[Artifact]:
        # 混合检索
        semantic = self.index.semantic_search(query)
        keyword = self.index.keyword_search(query)
        return self._rerank(semantic, keyword, top_k)
```

### 3. Agent安全护栏演进

从ECC和Anthropic插件生态可以看出安全护栏的三大方向：
- **Prompt防御基线**：防止prompt注入和越狱
- **技能权限控制**：限制Agent可调用技能的边界
- **执行沙箱**：隔离Agent执行环境，防止恶意操作

---

## 💡 实践启发

### 对Hermes Agent系统的启示

| 趋势 | 当前状态 | 改进建议 |
|------|----------|----------|
| 原语化架构 | 已有Dev/OPM/Content/Data四只猫分工 | 需明确各角色的"技能"定义和"钩子"触发机制 |
| 知识层 | 有memory和session_search | 需构建SYNAPSE式持久化知识层，支持跨会话累积 |
| 插件生态 | 有skill系统 | 需标准化skill格式，支持MCP协议兼容 |
| 自进化 | 有evolver技能 | 需完善技能创建→评估→沉淀闭环 |
| 知识图谱 | 无 | 可探索Understand-Anything的集成方案 |

### 可立即行动的建议

1. **技能标准化**：将现有skill系统升级为MCP兼容格式
2. **知识层增强**：在memory系统中增加"技能关联"字段
3. **安全加固**：为skill系统添加权限控制和执行沙箱
4. **图谱实验**：评估Understand-Anything的集成可行性

---

## 📚 知识缺口与后续探索

### 待深入研究的问题

1. **GENESIS开源进展**
   - 关注arXiv后续更新
   - 搜索作者实验室（Cornell/CMU等）的开源项目

2. **SYNAPSE技术实现**
   - 混合存储架构的具体选型
   - 跨会话知识迁移的算法

3. **量化交易新技术**
   - LLM在量化策略生成中的应用
   - Agent在高频交易中的实时决策能力
   - 多Agent协同的量化研究框架

4. **知识图谱集成**
   - Understand-Anything的API和集成方式
   - 代码库图谱构建的自动化程度

### 建议关注的资源

- **GitHub Trending**: 持续关注AI Agent相关项目
- **arXiv cs.AI**: 每日浏览最新提交
- **Anthropic博客**: 插件生态和Agent最佳实践
- **HuggingFace**: 开源Agent框架和模型

---

## 🔄 进化评估

### 可采纳的新技能/方法

| 类型 | 内容 | 采纳理由 | 动作 |
|------|------|----------|------|
| 工作流 | GENESIS三原语架构设计模式 | 可减少未来Agent系统设计复杂度 | 创建skill: `agent-primitive-architecture` |
| 方法 | 自进化Agent闭环（MUSE-Autoskill） | 可改进现有evolver技能 | patch `evolver` skill |
| 工具 | Understand-Anything知识图谱 | 可提升代码理解能力 | 记录到sniff-interests.md，标记L4 |
| 配置 | MCP插件标准格式 | 可提升skill兼容性 | 更新hermes-agent skill |

### 进化动作日志

```json
{
  "timestamp": "2026-05-27T07:52:00Z",
  "action": "create",
  "type": "skill",
  "detail": "agent-primitive-architecture: 基于GENESIS框架的三原语（Agents/Skills/Hooks）+ SYNAPSE知识层设计模式"
}
```

---

## 📖 参考来源

1. **GENESIS论文**: arXiv:2605.27360 - "Harnessing AI Agents for Autonomous 6G RAN Synthesis, Research, and Testing"
2. **MUSE-Autoskill论文**: arXiv:2605.27366 - "Self-Evolving Agents via Skill Creation, Memory, Management, and Evaluation"
3. **ECC**: GitHub - affaan-m/ECC (195k⭐) - Agent harness performance optimization system
4. **Understand-Anything**: GitHub - Lum1104/Understand-Anything (37.4k⭐) - Interactive knowledge graphs for code
5. **ai-engineering-from-scratch**: GitHub - rohitg00/ai-engineering-from-scratch (21.3k⭐)
6. **knowledge-work-plugins**: GitHub - anthropics/knowledge-work-plugins (16.9k⭐)
7. **arXiv cs.AI Recent**: 2026年5月27日最新AI论文列表

---

**学习完成时间**: 2026-05-27  
**笔记字数**: ~3500字  
**进化动作**: 2项skill相关，1项工具评估，1项配置更新
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
- [mem0-agent-memory-deep-dive](2026-05-27-mem0-agent-memory-deep-dive.md)
- [Agent需要RAG吗-协同vs高可信](2026-05-28-Agent需要RAG吗-协同vs高可信.md)
- [ai-agent-trends](2026-05-28-ai-agent-trends.md)
- [nt-structured-output-multi-agent-alpha-research](2026-ai-agent-structured-output-multi-agent-alpha-research.md)
- [20260513-llm-wiki-obsidian-gbrain-知识自组织与自进化](20260513-llm-wiki-obsidian-gbrain-知识自组织与自进化.md)
- [Pi-Agent-vs-Hermes-vs-Claude-Code对比分析](Pi-Agent-vs-Hermes-vs-Claude-Code对比分析.md)
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
