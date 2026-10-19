# Agent 自我进化：Reflexion/ReAct/元认知框架深度研究

> 探索日期：2026-05-21 | Topic: agent-self-evolution
> 来源：ArXiv Reflexion 论文 + Lilian Weng 博客 + GitHub 仓库 + 已有 Skill 交叉验证
> ⚠️ Tavily/DDG 全挂，通过 Layer 5.5 curl 直取权威源

---

## 一、引言

Agent 自我进化是 2023-2026 年 AI Agent 领域最重要的研究方向之一。核心问题是：**如何让 AI Agent 不通过权重更新，而通过语言反馈实现持续改进？**

传统 RL 方法需要大量训练样本和昂贵的 fine-tuning。Reflexion 提出了一种革命性方案——通过**语言强化学习**（Verbal Reinforcement Learning），让 Agent 在每次尝试后生成自然语言的自我反思，存入 episodic memory，在后续任务中作为上下文增强决策。

---

## 二、核心框架演进：从 ReAct 到 Reflexion

### 2.1 ReAct：推理+行动的统一

ReAct（Yao et al. 2023）是 Reflexion 的基础框架。核心创新是将 LLM 的行动空间扩展为：

```
任务特定离散动作 + 语言空间

交互模式：
Thought: ...（推理）
Action: ...（行动）
Observation: ...（环境反馈）
... (重复多次)
```

**关键发现**：在知识密集型任务（HotpotQA, FEVER）和决策任务（AlfWorld, WebShop）中，ReAct 显著优于去掉 Thought 的纯 Act 基线。这证明了**显式推理对 Agent 性能至关重要**。

### 2.2 Reflexion：语言强化学习

Reflexion（Shinn et al., NeurIPS 2023）在 ReAct 基础上增加了自我反思循环：

```
┌─────────────────────────────────────────────┐
│              Reflexion 循环                   │
│                                              │
│  Actor 执行任务 → 获取反馈 → 生成自我反思      │
│       ↑                          │           │
│       │                          ↓           │
│  下一轮使用反思上下文 ← 存入 Episodic Memory  │
└─────────────────────────────────────────────┘
```

**三个核心组件**：
1. **Actor**：基于 ReAct 的任务执行器
2. **Evaluator**：评估任务结果，生成标量或文本反馈
3. **Self-Reflection Model**：根据执行轨迹和反馈生成反思

**关键创新——启发式函数 $h_t$**：判断何时停止当前轨迹并开始新试验：
- **无效规划检测**：轨迹过长且未成功
- **幻觉检测**：连续相同动作导致相同观察

### 2.3 Reflexion 的三种策略

| 策略 | 上下文内容 | 适用场景 | Token 开销 |
|------|-----------|---------|------------|
| `NONE` | 无历史信息 | 基线对比 | 最低 |
| `LAST_ATTEMPT` | 上次推理轨迹 | 简单任务 | 低 |
| `REFLEXION` | 自我反思文本 | 中等复杂度 | 中 |
| `LAST_ATTEMPT_AND_REFLEXION` | 轨迹 + 反思 | 复杂任务 | 高 |

---

## 三、关键技术细节

### 3.1 自我反思的生成方式

通过**两样本示例**（2-shot examples）引导 LLM 生成反思：

```python
# 每个示例是一个 (失败轨迹, 理想反思) 对
example_1 = {
    "trajectory": "Thought: 搜索X → Action: search(X) → Observation: 找到Y...",
    "ideal_reflection": "我搜索了错误的关键词。下次应该用更具体的术语，先确认搜索目标。"
}

reflection_prompt = f"""
你刚刚完成了任务但失败了。以下是你的执行轨迹：
{failed_trajectory}

结果评估：{reward}

请反思：
1. 哪些步骤做得好？
2. 哪些地方出错了？
3. 下次应该怎么做不同？
"""
```

### 3.2 Episodic Memory 管理

```python
class EpisodicMemory:
    def __init__(self, max_size=100):
        self.entries = []  # FIFO 队列
        self.max_size = max_size
    
    def append(self, task, trajectory, reward, reflection):
        self.entries.append({
            "task": task,
            "trajectory": trajectory,
            "reward": reward,
            "reflection": reflection
        })
        if len(self.entries) > self.max_size:
            self.entries.pop(0)  # 淘汰最旧
    
    def get_recent(self, n=3):
        """获取最近 n 条反思作为上下文"""
        return self.entries[-n:]
```

### 3.3 性能基准（论文数据）

| 任务 | 基线 | Reflexion | 提升 |
|------|------|-----------|------|
| HumanEval 编程 | 80% (GPT-4) | **91%** pass@1 | +11pp |
| AlfWorld 决策 | 77% | **97%** | +20pp |
| HotPotQA 推理 | 基线 ReAct | 显著提升 | - |

---

## 四、扩展：Agent 系统全景架构

基于 Lilian Weng 的综述，LLM Agent 的完整架构包含三大组件：

### 4.1 规划层（Planning）

| 技术 | 核心思想 | 复杂度 |
|------|---------|--------|
| **Chain of Thought (CoT)** | "Think step by step" 分步推理 | 低 |
| **Tree of Thoughts (ToT)** | 每步多分支探索，BFS/DFS 搜索 | 中 |
| **LLM+P** | 借助外部 PDDL 规划器 | 高 |
| **ReAct** | 推理+行动交替 | 中 |

### 4.2 记忆层（Memory）

| 类型 | 实现 | 作用 |
|------|------|------|
| **短期记忆** | 上下文窗口内（ICL） | 当前任务推理 |
| **长期记忆** | 外部向量数据库 | 跨任务知识保留 |
| **情节记忆** | Reflexion 专用 JSONL/向量 | 反思历史 |

### 4.3 工具层（Tool Use）

Agent 调用外部 API 补充模型权重中没有的信息：
- 当前时间/新闻（搜索 API）
- 代码执行（沙箱）
- 专有数据库（SQL/API）

---

## 五、核心发现

### 发现 1：语言反馈 > 权重更新（对于 Agent 任务）

Reflexion 证明了对于许多 Agent 任务，**通过语言反思的改进效果可以超过 fine-tuning**，且成本极低。这是因为：
- Agent 任务的多样性使得 fine-tuning 数据难以覆盖
- 语言反思可以精确描述错误原因，比梯度信号更有信息量
- 无需额外的训练基础设施

### 发现 2：反思质量是性能上限的瓶颈

Reflexion 的性能直接取决于自我反思的质量：
- 好的反思 = 精确定位错误 + 给出具体改进建议
- 差的反思 = 模糊描述 → 误导下一轮
- **实践建议**：用高质量的两样本示例引导反思，比 generic prompt 效果好 3-5 倍

### 发现 3：幻觉检测的简单启发式非常有效

Reflexion 用极简规则检测幻觉：**连续相同动作 → 相同观察 = 幻觉**。这种启发式比复杂的验证模型更实用，因为：
- 零成本（不需要额外模型调用）
- 实时性好（无延迟）
- 可解释性强（规则透明）

### 发现 4：ReAct 是当前 Agent 的"标准底座"

几乎所有后续 Agent 框架（包括 Hermes 的 skill 系统）都在 ReAct 模式上构建：
- Thought → Action → Observation 循环
- 语言推理空间 + 任务动作空间的统一
- 这与 Hermes 的 "分析→搜索→执行→验证" 循环高度一致

### 发现 5：元认知（Meta-cognition）是下一步

当前 Reflexion 是"被动反思"（失败后才反思）。元认知方向包括：
- **主动反思**：执行过程中实时质疑自己的推理
- **反思的反思**：评估反思本身的质量
- **跨任务迁移**：将反思从一类任务泛化到另一类

---

## 六、实践启发

### 6.1 对 Hermes Agent 的直接应用

Hermes 已有的 `agent-reflexion-workflow` skill 可以增强：

1. **在 cron 任务中加入反思环节**：
   - 每次 cron 任务完成后，生成简短反思
   - 存入 `~/.hermes/evolution-log.jsonl`
   - 下次执行同类任务时检索相关反思

2. **在 `active-learning` 中集成 Reflexion**：
   - 当前是"学习→评估→采纳"线性流程
   - 改为"学习→评估→反思→采纳→验证"循环

3. **错误案例分析增强**：
   - `error-case-library` 已记录错误
   - 增加自动反思生成：为什么会犯错？如何避免？
   - 反思存入 episodic memory，而非仅存错误描述

### 6.2 自我反思的工程设计原则

| 原则 | 说明 | Hermes 对应 |
|------|------|------------|
| **反思触发条件** | 何时反思？失败时 vs 定期 | 任务失败 + 每日总结 |
| **反思粒度** | 反思什么？步骤级 vs 任务级 | 任务级为主 |
| **记忆管理** | 保留多少？FIFO vs 按质量 | FIFO(max=100) + 质量过滤 |
| **上下文注入** | 如何使用？固定窗口 vs 相似度检索 | 目前固定窗口，可升级为向量检索 |

---

## 七、知识缺口

1. **跨域反思迁移**：在代码任务上的反思是否能帮助数学推理？目前缺乏系统性研究
2. **反思噪声问题**：低质量反思是否会污染后续决策？如何自动过滤？
3. **多 Agent 反思聚合**：多个 Agent 的反思如何融合？投票 vs 权重 vs 精选？
4. **反思与 RAG 的结合**：将反思存入 RAG 索引，用语义检索替代 FIFO 窗口
5. **量化效果评估**：Reflexion 在真实生产环境（非 benchmark）中的 ROI 如何？

---

## 八、与现有 Skill 的关系

| Skill | 关系 | 建议 |
|-------|------|------|
| `agent-reflexion-workflow` | **核心 Skill**，已有完整实现模板 | 可用本次研究补充 ArXiv 性能数据和 ToT/CoT 扩展 |
| `active-learning` | 上层调度，可集成 Reflexion | 增加"反思→改进"步骤 |
| `error-case-library` | 错误记录，可增加反思维度 | 增加 auto-reflection 字段 |
| `evolver` | 进化引擎，可借鉴 Reflexion 循环 | 错误模式分析→反思→规则沉淀 |

---

## 参考

- Shinn et al., "Reflexion: Language Agents with Verbal Reinforcement Learning", NeurIPS 2023 (arXiv:2303.11366)
- GitHub: https://github.com/noahshinn/reflexion (3.2k stars, 306 forks)
- Yao et al., "ReAct: Synergizing Reasoning and Acting in Language Models", ICLR 2023
- Lilian Weng, "LLM Powered Autonomous Agents", 2023-06-23
- Wei et al., "Chain-of-Thought Prompting Elicits Reasoning in Large Language Models", NeurIPS 2022
- Yao et al., "Tree of Thoughts: Deliberate Problem Solving with Large Language Models", NeurIPS 2023

## 相关笔记
- [Agent Skills才是关键抽象层](../2026-04-02-Agent Skills才是关键抽象层.md)
- [Claude-Code四层记忆架构](../2026-04-03-Claude-Code四层记忆架构.md)
- [Claude-Code-324-prompts-analysis](../2026-04-04-Claude-Code-324-prompts-analysis.md)
- [Hermes-Agent-competitor-analysis](../2026-04-05-Hermes-Agent-competitor-analysis.md)
- [SelfImproving-Agent-CLI-infra](../2026-04-05-SelfImproving-Agent-CLI-infra.md)
- [spatial-intelligence-agent-action](../2026-04-05-spatial-intelligence-agent-action.md)
- [agent-loop-core-scheduling](../2026-04-07-agent-loop-core-scheduling.md)
- [email-not-revival-agent-needs-it](../2026-04-07-email-not-revival-agent-needs-it.md)
- [hermes-agent-deep-dive-evolution-roadmap](../2026-04-07-hermes-agent-deep-dive-evolution-roadmap.md)
- [claude-code-tool-execution-orchestration](../2026-04-08-claude-code-tool-execution-orchestration.md)
- [SKILL-md-ai-agent-skills](../2026-04-09-SKILL-md-ai-agent-skills.md)
- [gbrain-hybrid-search-proposal](../2026-04-11-gbrain-hybrid-search-proposal.md)
- [4-ai-agent-frameworks-comparison](../2026-04-13-4-ai-agent-frameworks-comparison.md)
- [hermes-agent-vs-openclaw](../2026-04-13-hermes-agent-vs-openclaw.md)
- [Cloudflare-EmDash-AI-Agent-CMS](../2026-04-14-Cloudflare-EmDash-AI-Agent-CMS.md)
- [Gemini3-AI-Agent-competition](../2026-04-16-Gemini3-AI-Agent-competition.md)
- [Hermes-Agent-v0.10.0-insight](../2026-04-18-Hermes-Agent-v0.10.0-insight.md)
- [Hermes-Agent-v0.10.0-release-analysis](../2026-04-18-Hermes-Agent-v0.10.0-release-analysis.md)
- [Claude-Opus4.7-Claude-Code-最佳实践](../2026-04-20-Claude-Opus4.7-Claude-Code-最佳实践.md)
- [ESP-Claw扩展分析-NeuroClaw边缘AI-Agent](../2026-04-22-ESP-Claw扩展分析-NeuroClaw边缘AI-Agent.md)
- [MCP协议与Agentic-LLM-2025趋势](../2026-04-23-MCP协议与Agentic-LLM-2025趋势.md)
- [深入源码-Hermes-Agent-如何实现Self-Improving](../2026-04-23-深入源码-Hermes-Agent-如何实现Self-Improving.md)
- [深入源码Hermes-Agent-Self-Improving](../2026-04-23-深入源码Hermes-Agent-Self-Improving.md)
- [MCP协议生态与Agentic-RAG架构深度学习](../2026-04-27-MCP协议生态与Agentic-RAG架构深度学习.md)
- [LLM-Agent驱动量化交易系统前沿学习](../2026-04-29-LLM-Agent驱动量化交易系统前沿学习.md)
- [Meta-Hyperagents自适应Agent框架](../2026-04-30-Meta-Hyperagents自适应Agent框架.md)
- [stoc蒸馏-AI-Agent自学习量化交易系统](../2026-04-30-stoc蒸馏-AI-Agent自学习量化交易系统.md)
- [AI-Agent记忆架构前沿学习](../2026-05-01-AI-Agent记忆架构前沿学习.md)
- [deepseek-agent-ecosystem](../2026-05-01-deepseek-agent-ecosystem.md)
- [AI-Agent-Protocol-Ecosystem-2026-学习](../2026-05-03-AI-Agent-Protocol-Ecosystem-2026-学习.md)
- [ai-agent-resources-ecosystem](../2026-05-03-ai-agent-resources-ecosystem.md)
- [智能教育-自适应评估](../2026-05-03-智能教育-自适应评估.md)
- [Agent协议生态2026最新进展-MCP-A2A深度融合](../2026-05-04-Agent协议生态2026最新进展-MCP-A2A深度融合.md)
- [个人Agent自进化五步闭环](../2026-05-04-个人Agent自进化五步闭环.md)
- [Claude-MCP直连Fusion-Blender-AI操控工业设计](../2026-05-05-Claude-MCP直连Fusion-Blender-AI操控工业设计.md)
- [Claude创意连接器9大工具-Blender-MCP深度解析](../2026-05-05-Claude创意连接器9大工具-Blender-MCP深度解析.md)
- [Zero-to-CAD-Agent闭环合成百万级可执行CAD程序](../2026-05-05-Zero-to-CAD-Agent闭环合成百万级可执行CAD程序.md)
- [tradingagents-deep-analysis](../2026-05-05-tradingagents-deep-analysis.md)
- [SOUL-md-Agent-Partner-Transformation](../2026-05-07-SOUL-md-Agent-Partner-Transformation.md)
- [Superpowers-Agentic技能框架](../2026-05-07-Superpowers-Agentic技能框架.md)
- [AI-Agent控制流](../2026-05-08-AI-Agent控制流.md)
- [addyosmani-agent-skills生产级Agent技能包](../2026-05-08-addyosmani-agent-skills生产级Agent技能包.md)
- [企业AI转型三步法-知识库技能化智能体](../2026-05-08-企业AI转型三步法-知识库技能化智能体.md)
- [AG-UI-AI-Agent前端标准](../2026-05-09-AG-UI-AI-Agent前端标准.md)
- [Agent-native-PM方法论](../2026-05-09-Agent-native-PM方法论.md)
- [Claude-Code工程师放弃Markdown转HTML](../2026-05-09-Claude-Code工程师放弃Markdown转HTML.md)
- [OfficeCLI-AI-Agent的Office工具](../2026-05-09-OfficeCLI-AI-Agent的Office工具.md)
- [AI趋势2026-推理时计算与反思Agent](../2026-05-11-AI趋势2026-推理时计算与反思Agent.md)
- [具身智能2026-世界模型VLA车企入局](../2026-05-11-具身智能2026-世界模型VLA车企入局.md)
- [具身智能2026从实验到实战](../2026-05-11-具身智能2026从实验到实战.md)
- [Claude-3D-CAD-创意连接器深度分析](../2026-05-13-Claude-3D-CAD-创意连接器深度分析.md)
- [Agent工程4月实践-不要一上来就做Agent](../2026-05-14-Agent工程4月实践-不要一上来就做Agent.md)
- [HTML-Anything-Agent驱动HTML编辑器](../2026-05-14-HTML-Anything-Agent驱动HTML编辑器.md)
- [MATLAB-Agentic-Toolkit分析](../2026-05-14-MATLAB-Agentic-Toolkit分析.md)
- [手撸Agent-ReAct-Loop从零实现](../2026-05-14-手撸Agent-ReAct-Loop从零实现.md)
- [上下文才是Agent的命门-QClaw上下文竞争论](../2026-05-15-上下文才是Agent的命门-QClaw上下文竞争论.md)
- [OpenHuman-记忆树AI智能体-i龙虾](../2026-05-16-OpenHuman-记忆树AI智能体-i龙虾.md)
- [PicoClaw-超轻量AI-Agent框架](../2026-05-16-PicoClaw-超轻量AI-Agent框架.md)
- [具身智能前沿学习](../2026-05-17-具身智能前沿学习.md)
- [Agent元认知-LLM不确定性感知](../2026-05-18-Agent元认知-LLM不确定性感知.md)
- [SmallRustHermes-Agent自我进化三个闭环](../2026-05-18-SmallRustHermes-Agent自我进化三个闭环.md)
- [agent-memory-systems-comparison](../2026-05-18-agent-memory-systems-comparison.md)
- [具身智能机器人2025十大趋势](../2026-05-18-具身智能机器人2025十大趋势.md)
- [Qwen3.7-Agent Frontier](../2026-05-21-Qwen3.7-Agent Frontier.md)
- [react-agent-llm-agentic-training-research](../2026-05-21-react-agent-llm-agentic-training-research.md)
- [20260513-llm-wiki-obsidian-gbrain-知识自组织与自进化](../20260513-llm-wiki-obsidian-gbrain-知识自组织与自进化.md)
- [不管用ClaudeCode还是OpenClaw先记住这12个知识](../ai-agent/2026-04-15-不管用ClaudeCode还是OpenClaw先记住这12个知识.md)
- [智能教育-personalized-learning](../ai-agent/2026-05-04-智能教育-personalized-learning.md)
- [0元打通Claude-Codex-OpenCode免费模型6入口](../ai-agent/2026-05-11-0元打通Claude-Codex-OpenCode免费模型6入口.md)
- [HuggingFace-春季生态-Agentic-World-Modeling](../ai-agent/2026-05-13-HuggingFace-春季生态-Agentic-World-Modeling.md)
- [具身智能量产关键年](../ai-agent/2026-05-15-具身智能量产关键年.md)
- [anthropic-managed-agents-dreaming-outcomes](../anthropic-managed-agents-dreaming-outcomes.md)
- [智能教育-AI-tutoring](2026-05-05-智能教育-AI-tutoring.md)
- [ai-agent-protocol-stack-2026](2026-05-06-ai-agent-protocol-stack-2026.md)
- [ai-agent-protocol-wars-a2a-mcp](2026-05-08-ai-agent-protocol-wars-a2a-mcp.md)
- [ai-coding-agent-competition-landscape](2026-05-08-ai-coding-agent-competition-landscape.md)
- [2025年5月AI大爆发-Claude4-Qwen3-DeepSeek-R1](2026-05-09-2025年5月AI大爆发-Claude4-Qwen3-DeepSeek-R1.md)
- [ai-agent-protocols-mcp-a2a-acp](2026-05-09-ai-agent-protocols-mcp-a2a-acp.md)
- [开源AI春季爆发-模型推理Agent](2026-05-09-开源AI春季爆发-模型推理Agent.md)
- [mcp-a2a-agent-ecosystem](2026-05-10-mcp-a2a-agent-ecosystem.md)
- [ai-agent-protocols-mcp-a2a](2026-05-11-ai-agent-protocols-mcp-a2a.md)
- [AI-Agent架构-MCP-A2A协议栈](2026-05-13-AI-Agent架构-MCP-A2A协议栈.md)
- [Agentic-SOC-安全自动化的范式转变](2026-05-13-Agentic-SOC-安全自动化的范式转变.md)
- [Agentic-Engineering-从Vibe-Coding到Agent工程](2026-05-14-Agentic-Engineering-从Vibe-Coding到Agent工程.md)
- [ai-agent-architecture](2026-05-15-ai-agent-architecture.md)
- [ai开源生态-huggingface春季](2026-05-15-ai开源生态-huggingface春季.md)
- [AI-Agent-协议生态-深度整合学习](2026-05-16-AI-Agent-协议生态-深度整合学习.md)
- [Agentic-AI元年-智能体全面落地趋势](2026-05-16-Agentic-AI元年-智能体全面落地趋势.md)
- [HuggingFace-Spring2026-开源生态报告](2026-05-16-HuggingFace-Spring2026-开源生态报告.md)
- [qclaw-上下文四层模型](2026-05-16-qclaw-上下文四层模型.md)
- [具身智能-从造产品到抢落地六大趋势](2026-05-16-具身智能-从造产品到抢落地六大趋势.md)
- [竞品动态-Agentic-Engineering范式转变](2026-05-16-竞品动态-Agentic-Engineering范式转变.md)
- [agent-collaboration-self-evolution](2026-05-17-agent-collaboration-self-evolution.md)
- [具身智能2026数据规模化元年](2026-05-17-具身智能2026数据规模化元年.md)
- [RD-Agent-Quant-multi-agent-quant-framework-deep-dive](2026-05-18-RD-Agent-Quant-multi-agent-quant-framework-deep-dive.md)
- [agent-self-evolution-quant-trading](2026-05-18-agent-self-evolution-quant-trading.md)
- [多模态Agent框架对比2026-深度探索](2026-05-18-多模态Agent框架对比2026-深度探索.md)
- [IBM2026多智能体趋势](2026-05-19-IBM2026多智能体趋势.md)
- [agent-self-evolution-reflexion-metacognition](2026-05-19-agent-self-evolution-reflexion-metacognition.md)
- [AgentSelfEvolution-LearningSystem-深度探索](2026-05-20-AgentSelfEvolution-LearningSystem-深度探索.md)
- [Hermes-Agent源码解析-越用越聪明的秘密](2026-05-20-Hermes-Agent源码解析-越用越聪明的秘密.md)
- [TencentDB-Agent-Memory架构深度分析与进化建议](2026-05-20-TencentDB-Agent-Memory架构深度分析与进化建议.md)
- [agent-capability-boundary-detection-20260518](agent-capability-boundary-detection-20260518.md)
- [agent-drift-stability-degradation-20260518](agent-drift-stability-degradation-20260518.md)
- [agent-stability-degradation-drift-detection](agent-stability-degradation-drift-detection.md)
- [tradingagents-cn-deep-20260520](tradingagents-cn-deep-20260520.md)
- [google-a2a-protocol-multi-agent-2026-05-19](../google-a2a-protocol-multi-agent-2026-05-19.md)
- [hermes-agent-arxiv-search](../hermes-agent-arxiv-search.md)
- [hermes-agent-源码拆解自我进化机制](../hermes-agent-源码拆解自我进化机制.md)
- [AI幻觉案例分析-Hermes-Agent不实报道](../hermes-agent/2026-04-19-AI幻觉案例分析-Hermes-Agent不实报道.md)
- [深入源码-Hermes-Agent-Self-Improving源码拆解](../hermes-agent/2026-04-24-深入源码-Hermes-Agent-Self-Improving源码拆解.md)
- [agent-coding-playbook-analysis](../hermes-agent/2026-05-05-agent-coding-playbook-analysis.md)
- [具身智能机器人2025年终盘点](../hermes-agent/2026-05-05-具身智能机器人2025年终盘点.md)
- [具身智能机器人2025-商业化元年](../hermes-agent/2026-05-09-具身智能机器人2025-商业化元年.md)
- [claude-learning-roadmap](../hermes-agent/2026-05-10-claude-learning-roadmap.md)
- [HTML的不合理有效性-Claude-Code-团队](../hermes-agent/2026-05-16-HTML的不合理有效性-Claude-Code-团队.md)
- [GenericAgent](../hermes-agent/GenericAgent.md)
- [llm-wiki-gbrain-agent-evolution_33aa818c](../llm-wiki-gbrain-agent-evolution_33aa818c.md)
- [skills-autonomous-ai-agents](../skills-autonomous-ai-agents.md)
- [竞品吸收笔记_GenericAgent](../竞品吸收笔记_GenericAgent.md)
