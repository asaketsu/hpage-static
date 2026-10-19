# 📚 2026 AI Agent 与量化交易前沿学习笔记

**学习日期**: 2026-05-26  
**学习主题**: AI Agent 架构演进、结构化输出最佳实践、量化 Alpha 因子工程  
**深度评级**: L4 (可复用工作流/方法)  
**预计复用次数**: 15+ (Agent 开发 + 量化研究)

---

## 核心发现 (≥3个)

### 发现一：LLM 结构化输出已进入「生产级」时代

**关键洞察**: 2026 年 LLM 输出控制已从 Prompt Engineering (80-95% 可靠) 演进到原生结构化输出 (100% 可靠)，通过有限状态机 (FSM) 约束 token 生成。

**技术细节**:
- **Level 1 (Prompt Engineering)**: 80-95% 可靠，静默失败，无类型保证
- **Level 2 (Function Calling)**: 95-99% 可靠，schema 是提示而非约束
- **Level 3 (Native Structured Output)**: **100% 可靠**，FSM 强制约束

**FSM 工作原理**:
```
正常生成:
Token 概率: {"hello": 0.3, "{": 0.1, "The": 0.2, ...}
→ 任意 token 可选

约束生成 (期望 JSON 对象开始):
Mask: {"hello": 0, "{": 1, "The": 0, ...}
→ 仅 "{" 和空白 token 有效
```

**生产模式**:
1. **验证三明治**: 即使使用结构化输出也要二次验证 (捕获 JSON Schema 无法表达的业务逻辑违规)
2. **重试+升级**: 3 次重试 + 指数退避
3. **多 Provider 降级**: OpenAI → Anthropic → 报错
4. **流式结构化输出**: 支持 partial JSON 实时预览

**代码示例 (OpenAI Python)**:
```python
from openai import OpenAI
from pydantic import BaseModel

class SentimentAnalysis(BaseModel):
    sentiment: str
    confidence: float
    key_phrases: list[str]
    reasoning: str

response = client.beta.chat.completions.parse(
    model="gpt-5-mini",
    messages=[...],
    response_format=SentimentAnalysis,
)
result = response.choices[0].message.parsed  # 100% schema 有效
```

**代码示例 (Anthropic Tool Use 模式)**:
```python
response = client.messages.create(
    model="claude-sonnet-4-20260514",
    tools=[{
        "name": "extract_contact",
        "input_schema": ExtractedData.model_json_schema(),
    }],
    tool_choice={"type": "tool", "name": "extract_contact"},
    messages=[...]
)
tool_result = next(b for b in response.content if b.type == "tool_use")
data = ExtractedData(**tool_result.input)
```

**性能代价**:
| Schema 复杂度 | Tokens/s | 首 token | 总时间 |
|--------------|----------|---------|--------|
| 无 schema | 85 tok/s | ~200ms | ~500ms |
| 简单 (3 fields) | 78 tok/s | ~250ms | ~550ms |
| 中等 (10 fields, 1 enum) | 65 tok/s | ~350ms | ~800ms |
| 复杂 (20+ fields, nested) | 45 tok/s | ~500ms | ~1.5s |

---

### 发现二：多 Agent 框架选型需关注「编排模型」而非功能列表

**关键洞察**: 2026 年多 Agent 框架的核心差异在于编排模型 (graph-based vs role-based vs swarm)、状态管理 (checkpointed vs ephemeral vs event-sourced)、通信模式 (handoffs vs shared memory vs message queues)。

**六大框架对比**:

**1. OpenAI Agents SDK (2025.03)**
- 核心抽象: **Handoffs** — 显式 Agent 间控制转移 + 对话上下文
- 内置原语: Handoffs, Guardrails (I/O 验证), Tracing (可观测性)
- 模式: 分流 Agent → 专业 Agent (计费/支持/账户管理)
- 语言: Python-first, 无 TypeScript
- 模型锁定: OpenAI 模型 (GPT-5.4, GPT-5)
- 适用: 已在 OpenAI 生态的团队，最小抽象
- 局限: 8-10+ Agent 类型时 handoff 模式变得臃肿

**2. LangGraph (LangChain)**
- 核心抽象: **有向图 + 类型化状态** — 节点=Agent/函数, 边=转移
- 突出特性: **内置检查点** — 支持时间旅行调试、人在回路审批、中途失败恢复
- 附加特性: 每节点 token 流、子图组合、LangSmith 可观测性
- 模型无关: ✅ 每节点可用不同 LLM
- 适用: 复杂分支工作流、监管行业、条件路由
- 局限: 冗长 — 简单 2-Agent 流也需要状态 schema、节点、边、编译

**3. CrewAI**
- 核心抽象: **基于角色的隐喻** — Agent 有角色、目标、背景故事
- 流程类型: 顺序式 / 层级式 (Manager 分派) / 共识式 (投票决策)
- 开发者体验: **20 行 Python 内完成多 Agent 系统**
- 模型无关: ✅ OpenAI, Anthropic, Ollama, 任意 OpenAI 兼容 API
- 适用: 快速原型、多 Agent 概念新手
- 局限: 无内置检查点、粗粒度错误处理、通信仅通过任务输出

**4. AutoGen / AG2 (Microsoft)**
- 核心抽象: **对话式 Agent 团队** — Agent 通过多轮对话交互
- v0.4 (AG2) 改进: 事件驱动核心、async-first、可插拔编排
- 主要模式: **GroupChat** — 多 Agent 共享对话，selector 决定发言者
- 适用: 代码生成 (write→review)、内容生成 (writer+editor+fact-checker)、数据分析
- 关键局限: 高 token 成本 — 4-Agent 辩论 × 5 轮 = **至少 20 次 LLM 调用**
- 不适用: 高吞吐实时场景 (如客服)

**5. Google ADK (Agent Development Kit, 2025.04)**
- 核心抽象: **层级 Agent 树** — root → sub-agents → sub-sub-agents
- 突出特性: 原生 **A2A (Agent-to-Agent) 协议** — 跨框架 Agent 通信
- 多模态: 图像/音频/视频 via Gemini API
- 会话状态: 内存/数据库/Vertex AI 管理
- 跨框架互操作: ADK Agent 可通过 A2A 调用 LangGraph 或 CrewAI Agent
- 适用: Google Cloud 原生团队、多模态场景、需要托管基础设施的企业

**6. Claude Agent SDK (Anthropic)**
- 核心抽象: **Tool-use-first** — Agent = Claude 模型 + 工具 (含子 Agent 作为工具)
- 差异化: **Extended thinking** — CoT 推理可见于 API 响应
- 计算机使用: Agent 可交互桌面应用和浏览器
- MCP (Model Context Protocol): 标准化工具发现 (VS Code, JetBrains 等支持)
- 安全: Constitutional AI 原则在模型层

**选型决策树**:
```
是否需要人在回路审批?
├─ 是 → LangGraph (内置检查点)
└─ 否
    ├─ 需要跨框架互操作?
    │   ├─ 是 → Google ADK (A2A 协议)
    │   └─ 否
    │       ├─ 需要最小代码量?
    │       │   ├─ 是 → CrewAI (20 行)
    │       │   └─ 否
    │       │       ├─ 需要代码生成/辩论?
    │       │       │   ├─ 是 → AutoGen/AG2
    │       │       │   └─ 否 → OpenAI Agents SDK (最小抽象)
```

---

### 发现三：Agentic Alpha 研究架构 — 四角色 + 双层人在回路

**关键洞察**: Jonathan Kinlay (2026) 的 12 周 FX Carry 研究案例证明，**架构是承重件，不是提示词或模型选择**。正确架构下，Agent 研究效率提升 2× (非营销的 10×)，但需要严格的人在回路和类型化 handoff。

**四角色架构**:

| 角色 | 输入 | 输出 | 关键约束 |
|------|------|------|----------|
| **Proposer** | 文献 + 研究日志 | 单一可证伪假设 (固定 schema) | 无价格数据访问；schema 强制: 经济主张、因变量、预测因子、样本、零假设 |
| **Implementer** | 批准的假设 | 测试 notebook | 无 prior 结果访问 (防止锚定) |
| **Critic** | notebook + 输出 | 对抗性检查清单 (含严重程度) | 不能修复 — 仅提交发现 |
| **Replicator** | Critic 发现 + 原 notebook | 稳健性面板 (替代样本/成本/消融) | 推广阶段: 必须仅从假设 schema 独立重实现信号 |

**人在回路 (2 处)**:
1. **Proposer → Implementer**: 此假设值得计算资源吗?
2. **Replicator → "Promoted to Candidate"**: 稳健性面板令人信服吗?

**关键不变量**:
> "每个角色不将其 prior 输出视为 ground truth。每次 handoff 都是 fresh context，仅含 schema-typed artifact。"

**复合目标函数**:
```
U = IR_oos - λ₁|IR_is - IR_oos| - λ₂ k_eff - λ₃ S_tc - λ₄ log(1 + N_trials) - λ₅ C_frag
```

| 项 | 含义 |
|----|------|
| IR_oos | 样本外信息比率 |
| λ₁|IR_is - IR_oos| | IS/OOS 差距惩罚 (过拟合) |
| λ₂ k_eff | 有效参数计数惩罚 |
| λ₃ S_tc | 交易成本敏感性 |
| λ₄ log(1 + N_trials) | 多重测试惩罚 (White, Bailey et al.) |
| λ₅ C_frag | 稳健性面板脆弱性 |

**Critic 验证结果** (25 个缺陷 notebook + 25 个干净控制):

| 缺陷类别 | 注入 | 捕获 | 漏报 | 假阳性 |
|---------|------|------|------|--------|
| Look-ahead | 5 | 5 | 0 | 0 |
| 样本边界漂移 | 5 | 4 | 1 | 1 |
| 成本遗漏 | 5 | 5 | 0 | 0 |
| 状态选择 cherry-picking | 5 | 3 | 2 | 2 |
| 不稳定参数 | 3 | 2 | 1 | 1 |
| 特征名冲突 | 2 | 1 | 1 | 0 |
| **总计** | **25** | **20** | **5** | **4** |

**80% 捕获率** — 不足以单独使用，需 Critic + 时间点封装 + Replicator 独立重实现 + 人在回路形成分层防御。

**12 周结果 (FX Carry)**:

| 指标 | 基线 (2025) | Agent 栈 (2026) | 比率 |
|------|------------|----------------|------|
| 正式测试假设 | 11 | 38 | **3.5×** |
| 假设→首次回测时间 | ~2 天 | ~3 小时 | **~5×** |
| 通过 Critic | n/a | 14/38 (37%) | — |
| 通过稳健性面板 | n/a | 4/14 (29%) | — |
| **推广至候选** | **1** | **2** | **2×** |
| 研究者小时/周 | ~22 | ~18 | 0.8× |
| API 花费/周 | ~$0 | ~$340 | — |

> "2× 提升在 10× 营销数字面前显得谦虚，但这是真实、可审计、可重复的。"

---

### 发现四：Alpha 因子工程 — 从数据到信号的完整流水线

**核心概念**: Alpha = 资产回报中**未被基准暴露解释的部分**。Alpha 因子 = 市场/基本面/替代数据的变换，包含预测信号。

**因子类别**:

| 类型 | 示例 |
|------|------|
| 宏观经济 | 增长、通胀、波动率、生产力、人口风险 |
| 投资风格 | 市场组合、价值-成长、动量 |
| 行为 | 未被套利消除的投资者偏差 |
| 机构 | 金融市场的经济/结构 |

**理想属性**: 正交 (独立)、正风险溢价、完整覆盖风险维度。

**关键工具库**:

**数据工程**:
- `NumPy/pandas`: 数据操作和因子计算
- `TA-Lib`: 技术指标 (仅价格/成交量数据)
- `PyKalman`: Kalman 滤波信号平滑/去噪
- `PyWavelets`: 小波变换噪声预处理

**回测与评估**:
- `Zipline`: 事件驱动回测 (避免前瞻偏差)
- `alphalens`: Alpha 因子性能分析 (Quantopian 开源)
- `pyfolio`: 投资组合性能和风险分析

**核心指标**:
- **Information Coefficient (IC)**: 因子信号与后续回报的相关性
- **Factor Turnover**: 指示潜在交易成本
- **Signal-to-Noise Ratio**: 通过 Kalman 滤波/小波处理

---

## 技术细节与代码示例

### 1. 结构化输出完整模式

**验证三明治模式**:
```python
from pydantic import BaseModel, ValidationError

class ProductReview(BaseModel):
    product_id: str
    rating: int
    sentiment: str
    key_issues: list[str]

# 即使使用结构化输出也要二次验证
def validate_and_extract(result, schema):
    try:
        validated = schema.model_validate(result.model_dump())
        return validated
    except ValidationError as e:
        # 捕获业务逻辑违规
        logger.error(f"Business logic violation: {e}")
        raise

# 检查拒绝
if response.choices[0].message.refusal:
    # 处理模型拒绝
    pass
```

**重试+升级模式**:
```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=10))
def extract_with_retry(text, schema):
    response = client.beta.chat.completions.parse(
        model="gpt-5-mini",
        messages=[{"role": "user", "content": text}],
        response_format=schema,
    )
    return response.choices[0].message.parsed
```

**多 Provider 降级模式**:
```python
def extract_with_fallback(text, schema):
    # 尝试 OpenAI
    try:
        return openai_extract(text, schema)
    except Exception as e:
        logger.warning(f"OpenAI failed: {e}, trying Anthropic")
    
    # 降级 Anthropic
    try:
        return anthropic_extract(text, schema)
    except Exception as e:
        logger.error(f"All providers failed: {e}")
        raise
```

### 2. LangGraph 检查点模式

```python
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph, END

# 持久化检查点
checkpointer = MemorySaver()

builder = StateGraph(AgentState)
builder.add_node("agent", agent_node)
builder.add_node("tools", tool_node)
builder.set_entry_point("agent")
builder.add_conditional_edges("agent", should_continue)
builder.add_edge("tools", "agent")

graph = builder.compile(checkpointer=checkpointer)

# 时间旅行调试
config = {"configurable": {"thread_id": "session-1"}}
# 保存 checkpoint
checkpoint_id = graph.save(config)
# 恢复到特定 checkpoint
graph.get_state(config)  # 查看状态
```

### 3. Alpha 因子工程模式

**TA-Lib 技术指标**:
```python
import talib
import numpy as np

# 动量因子
mom = talib.MOM(close, timeperiod=10)

# RSI
rsi = talib.RSI(close, timeperiod=14)

# MACD
macd, macd_signal, macd_hist = talib.MACD(close, fastperiod=12, slowperiod=26, signalperiod=9)
```

**Kalman 滤波去噪**:
```python
from pykalman import KalmanFilter

kf = KalmanFilter(
    transition_matrices=[[1]],
    observation_matrices=[[1]],
    initial_state_mean=0,
    initial_state_covariance=1,
    observation_covariance=10,
    transition_covariance=0.1
)

state_means, _ = kf.filter(signal_values)
denoised = state_means.flatten()
```

**Alphalens 因子分析**:
```python
import alphalens

# 创建因子 DataFrame
factor_data = alphalens.utils.get_clean_factor_and_forward_returns(
    factor=factor_series,
    prices=price_data,
    groupby=sector_classification,
    quantiles=5
)

# 生成 tearsheet
alphalens.tears.create_full_tear_sheet(factor_data)
```

---

## 实践启发

### 1. Agent 开发

**架构优先原则**:
- 不要从提示词开始，从**状态 schema 和 handoff 协议**开始
- 每个 handoff 必须是**类型化的 artifact**，而非自由文本
- 人在回路必须嵌入在**关键决策点**，而非随机插入

**多 Agent 框架选型**:
- 需要人在回路审批 → LangGraph
- 需要最小代码量 → CrewAI
- 需要跨框架互操作 → Google ADK
- 需要代码生成/辩论 → AutoGen/AG2
- 已在 OpenAI 生态 → OpenAI Agents SDK

**生产模式**:
- 结构化输出必须配合**二次验证**
- 必须实现**重试+降级**
- 必须捕获**模型拒绝**场景

### 2. 量化研究

**信号验证流程**:
1. **IC 测试** (非回测): 确认信号稳定性，而非是否赚钱
2. **T-stats**: 确保信号在统计上显著不同于零
3. **滚动 IC/IR**: 视觉分析信号随时间的稳定性

**回测原则**:
- **费用优先**: 打开回测器立即添加滑点、手续费 (设得比实际高)
- **避免 Implementation Shortfall**: 理论回报与实际回报的差距
- **Walk-Forward Optimization**: 2010 年前训练，2010 年后验证

**AI Agent 使用边界**:
- AI Agent **不接触测试流程** (会做大量错误)
- 所有代码**手动编写** — 每行理解并验证
- "Vibe coding" 仅用于非交易项目

---

## 知识缺口

### 1. 结构化输出
- **Gemini 实现细节**: 文档较少，需要实际测试验证
- **本地模型支持**: Ollama + vLLM 的 structured output 实现状态需要调研
- **Schema 深度限制**: OpenAI 5 层 vs 其他无限制的实际影响

### 2. 多 Agent 框架
- **LangGraph 性能基准**: 大规模 (50+ 节点) 图的性能表现
- **CrewAI → LangGraph 迁移成本**: 实际项目中的迁移难度
- **Google ADK 生产案例**: 缺少足够案例研究

### 3. 量化研究
- **Agentic Alpha 研究的 λ 校准**: 如何在实际项目中校准复合目标函数的权重
- **Critic 缺陷分类扩展**: 除了已知的 6 类缺陷，还有哪些需要捕获
- **Replicator 独立重实现**: 如何确保真正实现独立而非复制

---

## 进化评估

### 可采纳的新技能/方法/工具/工作流

**1. 新可复用工作流: Agentic Alpha 研究四角色架构**
- **评估**: 能减少未来 10+ 次量化研究操作
- **行动**: 创建 skill `agentic-alpha-research`
- **理由**: 12 周案例证明 2× 效率提升，架构可迁移到其他量化领域

**2. 新环境配置/工具命令: 结构化输出生产模式**
- **评估**: 能减少未来 20+ 次 Agent 开发中的 JSON 解析错误
- **行动**: 写入 memory `target='memory'`
- **理由**: 生产级 Agent 必须使用 Level 3 结构化输出

**3. 新工具/库: PyKalman + TA-Lib 因子工程组合**
- **评估**: 能减少未来 5+ 次因子去噪操作
- **行动**: 记录到 `sniff-interests.md` 标记 L4
- **理由**: 现有 `quant-trading` skill 缺少去噪工具链

**4. 现有 skill 缺陷: `quant-trading` skill 缺少 Agentic 工作流**
- **评估**: 需要 patch 更新
- **行动**: patch `quant-trading` skill 添加 Agentic Alpha 研究模式
- **理由**: 当前 skill 仅覆盖传统量化，缺少 AI Agent 辅助研究

---

## 参考文献

1. **LLM Structured Output 2026**: https://dev.to/pockit_tools/llm-structured-output-in-2026-stop-parsing-json-with-regex-and-do-it-right-34pk
2. **Multi-Agent Frameworks 2026**: https://gurusup.com/blog/best-multi-agent-frameworks-2026
3. **Agentic Alpha Research**: https://jonathankinlay.com/2026/05/agentic-workflows-for-alpha-research/
4. **Quant Alpha Workflow**: https://setup4alpha.substack.com/p/my-scientific-workflow-for-generating-alpha
5. **Alpha Factor Engineering**: https://stefan-jansen.github.io/machine-learning-for-trading/04_alpha_factor_research
6. **Active Portfolio Management**: Grinold & Kahn (1999) — IC 框架
7. **Future Alpha 2026 Conference**: https://hedgefundalpha.com/conferences/future-alpha-2026

---

**学习总结**: 2026 年 AI Agent 和量化交易的核心演进在于**架构化**和**约束化**。结构化输出消除了 JSON 解析的静默失败，多 Agent 框架的编排模型成为选型核心，Agentic Alpha 研究通过四角色 + 双层人在回路实现了真实可审计的效率提升。量化研究仍需坚持「理解信号为何有效」的原则，AI Agent 可作为研究加速器但不能替代人类对经济逻辑的判断。

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
