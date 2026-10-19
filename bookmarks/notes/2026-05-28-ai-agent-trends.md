# 2026 AI Agent 技术趋势学习笔记

**学习日期**: 2026-05-28
**来源**: web_search + web_extract
**主题**: AI Agent 架构演进、记忆系统、自进化机制

---

## 核心发现

### 发现一：AI Agent 记忆系统已成为生产级架构的核心组件

2026 年，AI Agent 记忆从"可有可无的插件"进化为"第一等架构组件"。Mem0 发布的《State of AI Agent Memory 2026》报告揭示了三个关键变化：

**标准化基准测试体系已建立**
- **LoCoMo**: 1540 个问题，涵盖单跳/多跳/开放域/时序记忆召回
- **LongMemEval**: 500 个问题，测试知识更新和多会话召回
- **BEAM**: 在 1M 和 10M token 规模下测试记忆系统，无法通过单纯扩大上下文窗口解决

**性能数据**
- Mem0 在 LoCoMo 达到 92.5 分，LongMemEval 达到 94.4 分，查询成本约 6900 tokens
- 最大增益来自时序推理 (+29.6 分) 和多跳推理 (+23.1 分)

**未解决的开放问题**
1. 跨会话身份识别 (Cross-session identity)
2. 大规模时序抽象 (Temporal abstraction at scale)
3. 记忆陈旧性 (Memory staleness)

### 发现二：8 大记忆框架对比，选型决策树清晰化

Vectorize 的对比研究将 8 个框架按场景分类：

**个人化场景 (Personalization)**
- Mem0: 向量+图混合，Apache 2.0，~48K stars，无厂商锁定
- LangMem: 扁平 KV+向量，MIT，LangGraph 绑定
- LlamaIndex Memory: 可组合缓冲区，MIT，LlamaIndex 生态

**机构知识场景 (Institutional Knowledge)**
- Hindsight: 多策略混合架构，MIT，~4K stars（增长快）
- Cognee: KG+向量，开源核心，~12K stars
- Letta: 分层架构（操作系统启发），Apache 2.0，~21K stars

**时序知识场景**
- Zep/Graphiti: 时序知识图谱，Graphiti 开源，~24K stars

**选型决策树**
- 需要对话上下文 + 用户偏好 → Mem0 / LangMem
- 需要积累操作知识（如采购流程修正） → Hindsight / Cognee
- 需要时间序列推理 → Zep / Graphiti
- 需要操作系统式分层记忆 → Letta

### 发现三：自进化 Agent 从研究走向生产

Meta/UBC/Oxford/NYU 联合发布的 HyperAgents 论文（2026-03-19）标志着一个阈值被跨越：

**核心突破**
- 自进化策略可以从一个领域（机器人、论文评审）迁移到完全新领域（奥林匹克数学评分）
- 在 Olympiad math 上达到 imp@50 = 0.630

**METR 观测数据**
- AI Agent 自主完成的任务长度 **每 7 个月翻倍**（R² = 0.98，持续 6 年）
- 这意味着 Agent 的自主能力呈指数增长

**自进化机制分类**
1. **元认知自进化**: 修改自身修改过程（meta-learning）
2. **递归自我修改**: 直接改写代码/提示词/工作流拓扑
3. **进化优化**: 基于反馈的遗传算法式参数调整

**实践启发**
- Hermes Agent 的 idle-busy-loop 机制（空闲时自动学习）是元认知自进化的简化实现
- 当前 Hermes 的 evolver 技能已实现"错误模式分析→规则沉淀→经验闭环"
- 可进一步集成：从 session_search 自动提取高频任务模式，生成新 skill

---

## 技术细节与代码示例

### Redis Agent Memory Server 双层级架构

```
┌─────────────────────────────────────────────────────────┐
│                    Redis Agent Memory                    │
├─────────────────────┬───────────────────────────────────┤
│   Short-term Memory │     Long-term Memory              │
│   (In-memory)       │     (Vector Search)               │
│                     │                                   │
│  - 会话状态         │  - 语义检索                        │
│  - 工具调用历史      │  - 跨会话知识                      │
│  - 决策上下文       │  - 用户偏好                        │
│  - 即时访问 (<1ms)  │  - 持久化存储                      │
└─────────────────────┴───────────────────────────────────┘
```

### 记忆系统架构模式对比

**Orchestrator-Worker 模式**
```
                    ┌─────────────┐
                    │ Orchestrator │
                    │  (Coordinator)│
                    └──────┬──────┘
                           │ 任务分发
         ┌─────────────────┼─────────────────┐
         │                 │                 │
    ┌────▼────┐       ┌────▼────┐       ┌────▼────┐
    │ Worker  │       │ Worker  │       │ Worker  │
    │ Agent A │       │ Agent B │       │ Agent C │
    │(合规检查)│       │(数据检索)│       │(推理)   │
    └─────────┘       └─────────┘       └─────────┘
```

**Hierarchical Agent 模式**
```
┌───────────────────────┐
│   High-level Agent    │  ← 战略规划、任务分解
├───────────────────────┤
│  Sub-task Agent 1     │  ← 执行具体子任务
│  Sub-task Agent 2     │
│  Sub-task Agent 3     │
└───────────────────────┘
```

### 自进化 Agent 工作流伪代码

```python
class SelfEvolvingAgent:
    def __init__(self, base_model, memory, tools):
        self.model = base_model
        self.memory = memory  # 持久记忆层
        self.tools = tools
        self.evolution_log = []
    
    def execute(self, task):
        result = self._execute_with_tools(task)
        
        # 闭环反馈
        if result.success:
            self.memory.store("successful_pattern", {
                "task": task,
                "method": self._capture_method(),
                "metrics": result.metrics
            })
        else:
            # 错误模式分析
            error_pattern = self._analyze_error(result.error)
            self.memory.store("error_pattern", error_pattern)
            
            # 自动修正
            if self._should_evolve(error_pattern):
                self._evolve(error_pattern)
        
        return result
    
    def _should_evolve(self, pattern):
        """判断是否需要进化（减少未来 3+ 次重复操作）"""
        frequency = self.memory.query("similar_patterns", pattern)
        return frequency >= 3
    
    def _evolve(self, pattern):
        """执行进化：生成新 skill 或更新现有 skill"""
        new_skill = self._generate_skill_from_pattern(pattern)
        self._apply_skill(new_skill)
        self.evolution_log.append({
            "timestamp": now(),
            "type": "skill_creation",
            "pattern": pattern,
            "skill": new_skill.name
        })
```

---

## 实践启发

### 1. 记忆工程是 2026 年 Agent 开发的核心技能

- 推理层升级容易（换模型即可），但记忆层的长期维护、衰减、合并是真正难点
- 企业级 Agent 必须考虑：身份边界、治理执行、行为可观测性、设计故障模式

### 2. 量化交易 Agent 的新范式

- AI 驱动 89% 的全球交易量
- 期权交易 Agent 需要：实时市场感知 + 上下文推理 + 严格风控护栏
- 从静态脚本 → 可理解投资组合目标、规划多步策略、与定价引擎交互、从结果中学习

### 3. 自进化闭环的可落地实现

当前 Hermes 的 idle-busy-loop 已实现 Phase 1-3：
- Phase 1: 数据整理
- Phase 2: 记忆整理  
- Phase 3: proactive-learn

**可增强点**：
- 从 session_search 自动提取高频任务 → 生成候选 skill
- 从 error-case-library 自动提取失败模式 → 触发 skill patch
- 从 evolution-log.jsonl 统计技能使用频率 → 识别僵尸技能

---

## 知识缺口

1. **跨会话身份识别的工业级方案** — 现有方案（Mem0 等）在多用户共享记忆池时存在隐私和隔离问题
2. **大规模时序抽象的算法** — 当记忆条目达到百万级时，如何保持时序推理的准确性
3. **自进化 Agent 的安全边界** — 元认知自进化可能导致"过度优化"或"目标漂移"，需要护栏机制
4. **Hermes Agent 与外部记忆框架的集成** — 当前 Hermes 使用本地 SQLite + file-based memory，未集成 Mem0/Hindsight 等生产级记忆层

---

## 进化评估

### 可采纳的新技能/方法

| 类型 | 内容 | 采纳理由 |
|------|------|----------|
| 工作流 | 从 session_search 自动提取高频任务生成 skill | 减少未来 3+ 次重复的 skill 创建操作 |
| 工具 | Mem0 作为生产级记忆层候选 | 可替代当前 file-based memory，支持跨会话持久化 |
| 方法 | 错误模式分析 → 自动 patch skill | 已有 error-case-library 技能，可增强自动化程度 |

### 需要评估的工具/库

- **Mem0**: 开源记忆层，支持向量+图混合，MIT 协议，可自托管
- **Hindsight**: 专注机构知识记忆，MIT 协议，增长快
- **Graphiti**: 时序知识图谱，适合需要时间序列推理的场景

### 现有 skill 缺陷发现

- **error-case-library**: 仅记录错误，未实现自动触发 skill patch
- **evolver**: 依赖手动触发，未与 session_search 自动联动
- **memory-refiner**: 仅精炼记忆，未与进化闭环集成

---

## 参考来源

1. Vectorize - Best AI Agent Memory Systems in 2026: https://vectorize.io/articles/best-ai-agent-memory-systems
2. Mem0 - State of AI Agent Memory 2026: https://mem0.ai/blog/state-of-ai-agent-memory-2026
3. Redis - AI Agent Architecture: https://redis.io/blog/ai-agent-architecture
4. o-mega.ai - Self-Improving AI Agents: The 2026 Guide: https://o-mega.ai/articles/self-improving-ai-agents-the-2026-guide
5. Emergent Mind - Self-Evolving AI Agents: https://www.emergentmind.com/topics/self-evolving-ai-agent
6. Digiqt - AI Agents for Options Trading: https://digiqt.com/blog/ai-agents-for-options-trading

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
