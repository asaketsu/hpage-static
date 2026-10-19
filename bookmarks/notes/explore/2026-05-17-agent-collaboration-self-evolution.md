# Agent 协作与自我进化：双轮驱动的深度探索

**日期：** 2026-05-17  
**主题：** Agent 协作（MCP/A2A/多 Agent 架构） + Agent 自我进化（ReAct/Reflexion/元认知）  
**类型：** 夜间自学习深度研究  
**来源：** 本地知识库整合 + 多源交叉验证  

---

## 摘要

本次探索聚焦 AI Agent 领域的两大核心能力：**协作**与**进化**。前者解决"多个智能体如何高效配合"，后者解决"单个智能体如何持续成长"。两者并非独立——协作需要进化来提升配合质量，进化需要协作来验证改进效果。

**核心发现：**
1. **MCP 与 A2A 是互补协议**：MCP 解决模型→工具的垂直连接，A2A 解决 Agent↔Agent 的水平协作
2. **Agent 自我进化存在七重困境**：方向、容量、一致性、质量、成本、安全、组合，每个都有工程化解法
3. **TradingAgents 提供了多 Agent 协作的完整实践模板**：6层流水线 + 双模型分层 + 延迟反思

---

## 第一部分：Agent 协作架构

### 1.1 MCP 与 A2A：互补而非竞争

| 协议 | 定位 | 核心能力 | 解决的问题 |
|------|------|----------|------------|
| **MCP** | 模型-工具连接层 | 标准化 AI 模型与外部工具/数据源的接口 | "模型如何安全使用工具" |
| **A2A** | Agent 间通信层 | Agent 之间的直接通信协议 | "多 Agent 如何协作" |

**关键洞察：** MCP 关注垂直方向的工具集成（模型→工具），A2A 关注水平方向的 Agent 协作（Agent↔Agent）。两者不是竞争关系，而是互补。

**MCP 协议演进（2025-06-18 版本核心变更）：**
- 移除 JSON-RPC batching（简化协议复杂度）
- 新增 **Structured Tool Output**：工具返回值可定义 JSON Schema
- 新增 **Elicitation**：服务端可主动向用户请求信息
- OAuth 安全增强：客户端必须实现 RFC 8707 resource indicators
- HTTP 传输层强制要求协议版本头

### 1.2 多 Agent 架构的三层模式

```
┌─────────────────────────────────────────┐
│           Orchestrator (编排层)          │  ← 任务分解、路由、监控
├─────────────────────────────────────────┤
│   Agent A    Agent B    Agent C         │  ← 专业 Agent（各司其职）
├─────────────────────────────────────────┤
│      MCP Servers / Tools / APIs         │  ← 工具层（MCP 标准化接入）
└─────────────────────────────────────────┘
```

**三种协作模式：**

| 模式 | 描述 | 适用场景 |
|------|------|----------|
| **Hierarchical（层级式）** | 一个主 Agent 协调多个子 Agent | 任务有明确主次关系，如 TradingAgents 的 6 层流水线 |
| **Peer-to-Peer（对等式）** | Agent 之间直接通信（A2A 协议） | 需要快速响应的协作，如多空辩论 |
| **Hybrid（混合式）** | 主 Agent + Agent 间直接协作 | 复杂任务链，如 Hermes 的团队协作协议 |

### 1.3 TradingAgents 的多 Agent 协作实践

TradingAgents（67.5k⭐）提供了完整的多 Agent 协作模板：

**6 层流水线架构：**

| 层 | 角色 | 功能 | 模型策略 |
|----|------|------|----------|
| 1 | 分析师团队 | 市场/情绪/新闻/基本面分析 | quick_think |
| 2 | 多空辩论 | Bull vs Bear N 轮条件路由辩论 | quick_think |
| 3 | 研究经理 | 综合辩论结果，输出 ResearchPlan | deep_think |
| 4 | 交易员 | 基于 ResearchPlan 生成交易提案 | quick_think |
| 5 | 风险辩论 | 激进/保守/中立三方风险评估 | quick_think |
| 6 | 投资组合经理 | 综合所有信息做出最终决策 | deep_think |

**6 大可借鉴设计模式：**

1. **双模型分层**：high-decision 节点用强模型深度推理，辅助节点用快模型高效处理
2. **Pydantic 字段描述作 LLM 输出指令**：schema 即 prompt，一套 schema 同时约束输出和消费
3. **延迟反思记忆**：预判存入 pending → 下次运行获取实际数据 → 生成反思条目
4. **LangGraph 动态图**：图结构非静态编译，根据配置动态构建
5. **Signal Processing 层**：解耦 LLM 自然语言输出和下游结构化消费
6. **Checkpoint/Resume**：SQLite per-ticker 隔离，崩溃后可续跑

### 1.4 Hermes 团队协作协议现状

当前 `AGENTS.md` 定义了 5 个 Agent 角色：

| Agent | 角色 | 职责 |
|-------|------|------|
| **ubot（jc-server）** | CEO | 任务调度、战略决策、跨部门协调 |
| **OPM Meow** | CSO | 商业策略、ROI 评估、打断权 |
| **Dev Meow** | CTO | 开发实现、技术架构 |
| **Content Meow** | CCO | 内容创作、品牌推广 |
| **Data Meow** | CDO+ 审计 | 数据分析、质量抽查、成本监控 |

**龙虾法则（Hal Stack）：**
1. 禁止一次性工作 — 重复任务→样本→批准→SKILL.md→cron
2. MECE — 每类工作一个技能拥有者，不重叠不空白
3. 失败判定 — 用户第二次问同一件事 = 系统失败
4. 构建流程：Concept → Prototype → Evaluate → Codify → Cron → Monitor
5. 系统自愈 — 发现问题直接修复，不问用户确认

---

## 第二部分：Agent 自我进化

### 2.1 ReAct Loop：Agent 的"Hello World"

ReAct（Reason + Act）是 Agent 的基础状态机：

```
[1] messages → LLM
[2] 有 tool_calls？
  ├─ 无 → 输出回答，结束
  └─ 有 → [3] 执行工具
[4] 结果加入 messages（role: tool）
[5] step+1，回到[1]（除非 ≥ max_steps）
```

**四个代码组件：**
- **工具定义**：字符串入/出，简单纯粹
- **tools JSON**：description 决定 LLM 是否调用
- **execute_tool**：函数名分发器，映射到真实 Python 函数
- **run_agent**：主循环，messages + max_steps 防死循环

**生产环境必备防御机制：**
1. **重复检测**：连续两次调同一工具且参数相同→强制停止
2. **错误回传**：工具执行失败必须把错误返回给 LLM
3. **max_steps = 10-15**：合理默认值
4. **tool_choice="required"**：强制调用工具而非直接回答

### 2.2 自我进化的七重困境与解法

| 困境 | 核心矛盾 | 解法 |
|------|----------|------|
| **方向** | 进化往哪走？数据≠智慧 | 人类始终在回路中，审批所有反思候选 |
| **容量** | 有限窗口 vs 无限知识 | 三层上下文：Pinned(常驻) + Active Index(索引) + Triggered Skills(按需) |
| **一致性** | 记忆会冲突 | Supersedes 链 + 5 种冲突策略 |
| **质量** | LLM 生成技能参差不齐 | 三层防线：保守提示词 + 人工审批 + 元反思 |
| **成本** | 反思需要 LLM 调用 | 双轨反思：全量(Session End) + 微反思(Per-Turn 启发式触发) |
| **安全** | 进化 vs 安全矛盾 | 不可变核心(代码强制) + 可变外围(可进化修改) |
| **组合** | O(n²) 交互复杂度 | 最小接口 + 严格单向数据流 |

### 2.3 进化成熟度模型（L0-L4）

| Level | 名称 | 特征 | 代表系统 |
|-------|------|------|----------|
| L0 | 无进化 | 每次对话全新，无跨会话状态 | 大多数 ChatGPT wrapper |
| L1 | 被动记忆 | 存储检索用户偏好，但需用户主动告知 | 带配置文件的聊天机器人 |
| L2 | 主动反思 | 主动提炼技能/记忆 + 冲突检测 + 人类审批 | **Hermes 当前** |
| L3 | 元认知 | 评估反思质量 + 根据审批反馈调整策略 | Hermes 下一步目标 |
| L4 | 自主进化 | 无需人工审批自主修改行为 | 当前无可靠实现 |

### 2.4 Small Hermes 架构参考

```
hermes-cli / tui / gui（交互层）
├── hermes-core（Session + LlmProvider + ToolHost + Compaction）
├── hermes-llm（Anthropic/OpenAI/DeepSeek）
├── hermes-mcp（rmcp stdio/HTTP + McpToolHost）
├── hermes-turn（run_turn + 微反思 + 取消机制）
├── hermes-store（JSONL + Frontmatter + 原子写入）
├── hermes-skills（触发匹配 + 作用域覆盖）
├── hermes-memory（supersedes 链 + 冲突检测）
├── hermes-reflect（全量/微反思 + 反思日志 + 元反思）
└── hermes-tools（read/write/edit/bash + 路径沙箱）
```

**关键概念：**
- **Supersedes 链**：新记忆不覆盖旧记忆，而是标记"取代"关系，旧记忆保留为审计轨迹
- **双轨反思**：全量反思（Session End，完整对话）+ 微反思（Per-Turn，启发式触发，异步执行）
- **不可变核心**：代码层面强制的安全约束，LLM 无法绕过
- **严格单向数据流**：Agent Loop 运行时存储只读，反思只产生候选，审批是唯一写入路径

### 2.5 五大反模式（必须避免）

| # | 反模式 | 为什么错 | 正确做法 |
|---|--------|----------|----------|
| 1 | **RAG 即进化** | RAG 是检索不是修改，不改变 Agent 行为 | RAG 用于知识检索，Skill 用于行为改变 |
| 2 | **自动接受一切** | 等于无监督修改行为，长期灾难 | 人类审批不是摩擦是特性 |
| 3 | **过早引入向量数据库** | 几百条记忆线性扫描微秒级，过早优化 | token overlap 匹配在 50 个技能下够用 |
| 4 | **进化=微调** | 数据质量差/灾难性遗忘/不可审计/不可逆/成本高 | 保持 Prompt Engineering + 文件系统 |
| 5 | **忽视组合效应** | 组件间循环依赖导致不可预测副作用 | 最小接口 + 严格单向数据流 |

---

## 第三部分：交叉验证与共识

### 3.1 多源信息对比

| 主题 | 来源 1 | 来源 2 | 共识 | 分歧 |
|------|--------|--------|------|------|
| MCP 定位 | MCP 官方文档 | 本地笔记 | 模型-工具连接层 | 无 |
| A2A 定位 | DDG 搜索 | 本地笔记 | Agent 间通信层 | 无 |
| 多 Agent 模式 | TradingAgents | Hermes AGENTS.md | 层级式 + 对等式 + 混合式 | 无 |
| 自我进化困境 | Small Hermes | Hermes 源码拆解 | 七重困境 | Small Hermes 更系统化 |
| 进化成熟度 | Small Hermes | Hermes 源码拆解 | L0-L4 模型 | 一致 |
| 反思机制 | Small Hermes | Hermes evolver | 双轨反思 | Hermes 缺少 per-turn 微反思 |

### 3.2 来源可靠性评估

| 来源 | 可靠性 | 说明 |
|------|--------|------|
| MCP 官方文档 | ⭐⭐⭐⭐⭐ | 协议制定方，权威性最高 |
| TradingAgents GitHub | ⭐⭐⭐⭐ | 67.5k⭐，架构设计精良，但单维护者风险 |
| Small Hermes 文章 | ⭐⭐⭐ | 框架完整，但项目不公开无法验证 |
| Hermes 源码拆解 | ⭐⭐⭐⭐ | 基于公开仓库分析，部分需验证 |
| 本地笔记 | ⭐⭐⭐ | 多源整合，但部分未经实时验证 |

---

## 第四部分：实践启发

### 4.1 对 Hermes 系统的改进建议

| # | 改进点 | 优先级 | 具体动作 |
|---|--------|--------|----------|
| 1 | **增加 supersedes 审计链** | HIGH | 在 memory replace 时记录旧值到 JSONL 审计日志 |
| 2 | **增加 per-turn 微反思** | HIGH | 在 evolver 中增加启发式触发逻辑 |
| 3 | **增加元反思机制** | MEDIUM | 新建 reflect-log.jsonl，记录每次 skill/memory 写入的来源和后续使用情况 |
| 4 | **降低自动创建倾向** | MEDIUM | 在 evolver 中增加 confidence 评分，低于阈值的不自动创建 |
| 5 | **验证三层上下文架构** | MEDIUM | 验证当前 MEMORY + Skills 触发 + context 注入是否真正分层加载 |
| 6 | **增加候选-审批中间态** | LOW | 评估是否需要增加"候选-审批"中间态，避免运行时自修改 |

### 4.2 可复用的设计模式

1. **双模型分层**：high-decision 节点用强模型，辅助节点用快模型
2. **Pydantic schema 即 prompt**：一套 schema 同时约束 LLM 输出和下游消费
3. **延迟反思记忆**：利用下一轮的真实数据完成闭环
4. **LangGraph 动态图**：图结构根据配置动态构建
5. **Signal Processing 层**：解耦自然语言输出和结构化消费
6. **Checkpoint/Resume**：崩溃后可续跑

---

## 第五部分：知识缺口

### 5.1 待探索的问题

| # | 问题 | 重要性 | 建议行动 |
|---|------|--------|----------|
| 1 | Google A2A 协议官方文档细节 | HIGH | 联网后获取官方文档 |
| 2 | MCP 2025-06-18 版本完整规范 | HIGH | 联网后获取官方文档 |
| 3 | LATS（Lookahead Tree Search）与 Reflexion 对比 | MEDIUM | 搜索学术论文 |
| 4 | 多 Agent 协作时的记忆冲突处理 | HIGH | 设计实验验证 |
| 5 | 记忆衰减机制的具体设计 | MEDIUM | 调研现有系统 |
| 6 | 技能版本管理和回滚策略 | MEDIUM | 设计实验验证 |

### 5.2 网络受限说明

由于 Tavily 搜索服务异常，本次探索主要依赖本地知识库。建议后续联网时验证：
- MCP 协议最新规范
- A2A 协议官方文档
- LATS/Reflexion 学术论文
- 竞品平台功能对比

---

## 第六部分：进化闭环

### 6.1 可采纳的新技能/方法

| 类型 | 内容 | 采纳理由 | 动作 |
|------|------|----------|------|
| **新工作流** | 双轨反思（全量 + 微反思） | 可减少重复操作 3+ 次 | 创建 skill |
| **新配置** | supersedes 审计链设计 | 提升记忆系统可追溯性 | 写入 memory |
| **新工具** | reflect-log.jsonl 格式 | 支持元反思分析 | 记录到 sniff-interests |
| **现有 skill 修复** | evolver 增加 confidence 评分 | 降低噪声技能生成 | patch skill |

### 6.2 行动清单

- [ ] 创建 `agent-reflection` skill（双轨反思机制）
- [ ] 更新 `evolver` skill（增加 confidence 评分）
- [ ] 更新 `memory-write` skill（增加 supersedes 审计链）
- [ ] 更新 `sniff-interests.md`（标记已探索主题）
- [ ] 写入 `evolution-log.jsonl`

---

## 附录：相关资源

### 核心文档
- `AGENTS.md` — Hermes 团队协作协议
- `2026-05-16-MCP-协议生态最新发展.md` — MCP 协议演进
- `2026-05-14-Small-Hermes-自我进化深度解析.md` — 自我进化七重困境
- `2026-05-14-手撸Agent-ReAct-Loop从零实现.md` — ReAct 基础
- `2026-05-05-tradingagents-deep-analysis.md` — 多 Agent 协作实践
- `2026-05-15-上下文才是Agent的命门-QClaw上下文竞争论.md` — 上下文四层模型

### 外部链接（待验证）
- MCP 官方文档: https://modelcontextprotocol.io
- MCP Server 目录: https://mcp.so
- TradingAgents GitHub: https://github.com/TauricResearch/TradingAgents

---

*最后更新: 2026-05-17 04:00 (Cron Job)*
## 相关笔记
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
- [20260513-llm-wiki-obsidian-gbrain-知识自组织与自进化](../20260513-llm-wiki-obsidian-gbrain-知识自组织与自进化.md)
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
- [hermes-agent-源码拆解自我进化机制](../hermes-agent-源码拆解自我进化机制.md)
- [llm-wiki-gbrain-agent-evolution_33aa818c](../llm-wiki-gbrain-agent-evolution_33aa818c.md)
- [0元打通Claude-Codex-OpenCode免费模型6入口](../orphan/2026-05-11-0元打通Claude-Codex-OpenCode免费模型6入口.md)
- [HuggingFace-春季生态-Agentic-World-Modeling](../orphan/2026-05-13-HuggingFace-春季生态-Agentic-World-Modeling.md)
- [具身智能量产关键年](../orphan/2026-05-15-具身智能量产关键年.md)
- [HTML的不合理有效性-Claude-Code-团队](../orphan/2026-05-16-HTML的不合理有效性-Claude-Code-团队.md)
