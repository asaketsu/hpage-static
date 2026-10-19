# Agent 自我进化与量化交易策略：深度整合研究

**日期：** 2026-05-18  
**主题：** Agent 自我进化（ReAct/Reflexion/元认知） + 量化交易（策略回测/风险模型/执行算法）  
**类型：** 夜间自学习深度研究（静默模式）  
**来源：** 本地知识库整合 + 多源交叉验证  
**状态：** ⚠️ 网络受限（Tavily 搜索失败），依赖本地知识蒸馏

---

## 摘要

本次探索聚焦两大核心领域：**AI Agent 的自我进化机制**与**量化交易的风险管理**。两者在底层逻辑上高度相通——都需要从历史数据中学习、需要评估决策质量、需要建立反馈闭环。

**核心发现：**

1. **Agent 自我进化存在七重困境**：方向、容量、一致性、质量、成本、安全、组合，Hermes 当前处于 L2（主动反思），L3（元认知）是下一步目标
2. **量化回测与实盘存在三大鸿沟**：滑点（固定模型严重低估）、延迟（UI 自动化 2-10 秒 vs API 毫秒级）、熔断（模拟无法完全复现）
3. **双轨反思机制可迁移**：Agent 的"全量+微反思"与量化交易的"回测+实盘偏差日志"本质相同，都是"预判→验证→修正"闭环

---

## 第一部分：Agent 自我进化深度解析

### 1.1 ReAct Loop：Agent 的基础状态机

ReAct（Reason + Act）是所有 Agent 的"Hello World"，一个简洁的状态机循环：

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

| 防御机制 | 说明 | 实现方式 |
|---------|------|---------|
| 重复检测 | 连续两次调同一工具且参数相同→强制停止 | 记录最近 N 次 tool_calls |
| 错误回传 | 工具执行失败必须把错误返回给 LLM | try-catch + error message |
| max_steps | 合理默认值 10-15 | 防止无限循环 |
| tool_choice="required" | 强制调用工具而非直接回答 | 避免 LLM 偷懒 |

### 1.2 自我进化的七重困境与解法

| 困境 | 核心矛盾 | 解法 |
|------|----------|------|
| **方向** | 进化往哪走？数据≠智慧 | 人类始终在回路中，审批所有反思候选 |
| **容量** | 有限窗口 vs 无限知识 | 三层上下文：Pinned(常驻) + Active Index(索引) + Triggered Skills(按需) |
| **一致性** | 记忆会冲突 | Supersedes 链 + 5 种冲突策略 |
| **质量** | LLM 生成技能参差不齐 | 三层防线：保守提示词 + 人工审批 + 元反思 |
| **成本** | 反思需要 LLM 调用 | 双轨反思：全量(Session End) + 微反思(Per-Turn 启发式触发) |
| **安全** | 进化 vs 安全矛盾 | 不可变核心(代码强制) + 可变外围(可进化修改) |
| **组合** | O(n²) 交互复杂度 | 最小接口 + 严格单向数据流 |

### 1.3 进化成熟度模型（L0-L4）

| Level | 名称 | 特征 | 代表系统 |
|-------|------|------|----------|
| L0 | 无进化 | 每次对话全新，无跨会话状态 | 大多数 ChatGPT wrapper |
| L1 | 被动记忆 | 存储检索用户偏好，但需用户主动告知 | 带配置文件的聊天机器人 |
| L2 | 主动反思 | 主动提炼技能/记忆 + 冲突检测 + 人类审批 | **Hermes 当前** |
| L3 | 元认知 | 评估反思质量 + 根据审批反馈调整策略 | Hermes 下一步目标 |
| L4 | 自主进化 | 无需人工审批自主修改行为 | 当前无可靠实现 |

### 1.4 双轨反思机制（关键发现）

**全量反思（Session End）**：
- 触发时机：会话结束时
- 输入：完整对话历史
- 输出：技能建议、记忆更新、规则修改
- 成本：高（需要完整上下文）

**微反思（Per-Turn）**：
- 触发时机：启发式触发（如连续错误、用户纠正、工具调用异常）
- 输入：当前 turn 的上下文
- 输出：即时修正建议
- 成本：低（异步执行，不阻塞主流程）

**双轨反思的价值**：
1. 全量反思保证系统性改进
2. 微反思捕捉即时错误模式
3. 两者互补，覆盖不同时间尺度

### 1.5 五大反模式（必须避免）

| # | 反模式 | 为什么错 | 正确做法 |
|---|--------|----------|----------|
| 1 | **RAG 即进化** | RAG 是检索不是修改，不改变 Agent 行为 | RAG 用于知识检索，Skill 用于行为改变 |
| 2 | **自动接受一切** | 等于无监督修改行为，长期灾难 | 人类审批不是摩擦是特性 |
| 3 | **过早引入向量数据库** | 几百条记忆线性扫描微秒级，过早优化 | token overlap 匹配在 50 个技能下够用 |
| 4 | **进化=微调** | 数据质量差/灾难性遗忘/不可审计/不可逆/成本高 | 保持 Prompt Engineering + 文件系统 |
| 5 | **忽视组合效应** | 组件间循环依赖导致不可预测副作用 | 最小接口 + 严格单向数据流 |

---

## 第二部分：量化交易策略与风险管理

### 2.1 回测与实盘的三大鸿沟

| 维度 | 回测/模拟 | 实盘 | 差距评估 |
|------|----------|------|---------|
| **滑点** | 固定百分比（如 0.1%）或零滑点 | 动态、非对称、依赖流动性 | ⚠️ 严重低估 |
| **延迟** | 理想化（即时成交） | UI 自动化 2-10 秒，API 50-200ms | ⚠️ 分钟级策略致命 |
| **熔断** | 代码逻辑拦截 | 真实封单量、券商风控、流动性危机 | ⚠️ 无法完全模拟 |

### 2.2 滑点建模：从固定到动态

**固定滑点模型（回测常用，过于简化）：**
```python
slippage = 0.001  # 0.1%
```

**盘口深度感知滑点模型（推荐）：**
```python
def estimate_slippage(order_size, bid_depth, ask_depth, avg_volume):
    """
    根据委托量与盘口深度估算滑点
    """
    volume_ratio = order_size / avg_volume
    depth_ratio = order_size / min(bid_depth, ask_depth)
    
    base_slippage = 0.0005  # 0.05%
    impact_cost = 0.002 * (volume_ratio ** 0.5) + 0.01 * (depth_ratio ** 1.5)
    
    return base_slippage + impact_cost
```

**关键洞察：**
- 买入滑点：实际成交价往往**高于**信号价（追单效应）
- 卖出滑点：实际成交价往往**低于**信号价（恐慌性抛售）
- 极端行情：流动性枯竭时滑点可达 3-5% 甚至更多

### 2.3 延迟敏感型策略的延迟预算

| 策略类型 | 最大可容忍延迟 | 推荐通道 |
|---------|--------------|---------|
| 日线趋势跟踪 | >10 秒 | UI 自动化 (xdotool) |
| 小时线均值回归 | 1-5 秒 | UI 自动化 + 超时熔断 |
| 分钟线动量 | 200-500ms | 券商 API (QMT/PTrade) |
| 秒线/Tick 级 | <50ms | 穿透式接口 |

### 2.4 动态止损策略对比

| 对比维度 | ATR 动态止损 | 固定百分比止损 | 追踪止损 |
|---------|:-----------:|:-------------:|:--------:|
| **波动适应性** | ★★★★★ | ★★☆☆☆ | ★★★☆☆ |
| **抗噪音能力** | ★★★★★ | ★★★☆☆ | ★★★★☆ |
| **利润保护** | ★★★★☆ | ★☆☆☆☆ | ★★★★★ |
| **趋势跟踪** | ★★★★☆ | ★★☆☆☆ | ★★★★★ |
| **实现难度** | 中等 | 极低 | 低-中等 |

**ATR 止损参数经验值：**

| 参数 | 保守型 | 适中型 | 激进型 |
|------|--------|--------|--------|
| ATR 周期 | 20 日 | 14 日 | 7 日 |
| ATR 倍数 | 3×~4× | 2×~2.5× | 1.5× |
| 适用场景 | 长线持仓 | 波段交易 | 短线/日内 |

**A 股特殊规则注意事项：**

1. **T+1 限制**：当日买入无法当日止损，隔日开盘可能跳空越过止损位
2. **涨跌停板**：10%/20% 涨跌停可能无法成交
3. **集合竞价**：9:25 确定开盘价，可能直接跳过止损价

### 2.5 多层止损架构（最佳实践）

```
第一层：硬止损（固定百分比 -8%~-10%）
  → 保护极端风险，永远不会被移除

第二层：ATR 动态止损（2.5×ATR(14)）
  → 根据波动自适应，日内主止损

第三层：追踪止损（盈利 > 3% 后激活）
  → 盈利时逐步锁定利润
  → 使用 Chandelier Exit 或百分比追踪 5%
```

### 2.6 实盘验证的渐进式路径

```
回测 (历史数据) → 样本外测试 → Walk-Forward → Paper Trade (1-2 周) → 
小资金实盘 (1-3 个月) → 逐步放量
    ↑                                              │
    └──── 任一环节不达标则返回调参/优化 ←────────────┘
```

**关键门槛（ths-auto-trader 标准）：**
- 样本内夏普 > 1.0，样本外夏普 > 0.8
- 最大回撤 < 15%
- 至少 3 年历史数据回测
- Walk-Forward 衰减 < 30%
- Paper Trade 实际收益率与回测偏差 < 20%

---

## 第三部分：交叉验证与共识

### 3.1 多源信息对比

| 主题 | 来源 1 | 来源 2 | 共识 | 分歧 |
|------|--------|--------|------|------|
| 自我进化困境 | Small Hermes | Hermes 源码拆解 | 七重困境 | Small Hermes 更系统化 |
| 进化成熟度 | Small Hermes | Hermes 源码拆解 | L0-L4 模型 | 一致 |
| 反思机制 | Small Hermes | Hermes evolver | 双轨反思 | Hermes 缺少 per-turn 微反思 |
| 滑点建模 | ths-auto-trader | TradingAgents | 固定模型不足 | 无 |
| 延迟影响 | ths-xdotool 笔记 | 量化社区经验 | UI 自动化延迟大 | 无 |

### 3.2 来源可靠性评估

| 来源 | 可靠性 | 说明 |
|------|--------|------|
| TradingAgents GitHub | ⭐⭐⭐⭐ | 67.5k⭐，架构设计精良 |
| Hermes 源码拆解 | ⭐⭐⭐⭐ | 基于公开仓库分析 |
| ths-auto-trader 项目 | ⭐⭐⭐ | 实战项目，但需验证 |
| 本地笔记 | ⭐⭐⭐ | 多源整合，部分未经实时验证 |

---

## 第四部分：实践启发

### 4.1 Agent 自我进化对量化交易的启发

| Agent 概念 | 量化对应 | 迁移价值 |
|-----------|---------|---------|
| 双轨反思 | 回测 + 实盘偏差日志 | 建立"预判→验证→修正"闭环 |
| Supersedes 链 | 策略版本管理 | 保留策略迭代审计轨迹 |
| 元反思 | 策略质量评估 | 评估策略在不同市场环境的表现 |
| 不可变核心 | 风控硬约束 | 代码强制的风控底线 |

### 4.2 量化交易对 Agent 进化的启发

| 量化概念 | Agent 对应 | 迁移价值 |
|---------|-----------|---------|
| Walk-Forward 验证 | Skill 压力测试 | 在真实场景中验证技能有效性 |
| 滑点模型 | 工具调用成本估算 | 量化工具调用的"损耗" |
| 多层风控 | 多层安全约束 | 防御性设计，逐层过滤风险 |
| Paper Trade | Skill 灰度发布 | 新技能先在有限范围测试 |

### 4.3 可复用的设计模式

1. **双模型分层**：high-decision 节点用强模型，辅助节点用快模型
2. **延迟反思记忆**：利用下一轮的真实数据完成闭环
3. **多层风控架构**：从硬约束到软约束逐层过滤
4. **渐进式验证路径**：回测→样本外→Paper Trade→小资金→放量
5. **审计链设计**：保留所有修改的历史轨迹

---

## 第五部分：知识缺口

| # | 问题 | 重要性 | 建议行动 |
|---|------|--------|----------|
| 1 | LATS（Lookahead Tree Search）与 Reflexion 对比 | HIGH | 联网后搜索学术论文 |
| 2 | 多 Agent 协作时的记忆冲突处理 | HIGH | 设计实验验证 |
| 3 | A 股实盘滑点统计数据 | HIGH | 收集 100+ 笔实盘成交记录 |
| 4 | QMT/PTrade 接口性能实测 | MEDIUM | 申请测试账户实测 |
| 5 | 技能版本管理和回滚策略 | MEDIUM | 设计实验验证 |
| 6 | 记忆衰减机制的具体设计 | MEDIUM | 调研现有系统 |

---

## 第六部分：进化闭环

### 6.1 可采纳的新技能/方法

| 类型 | 内容 | 采纳理由 | 动作 |
|------|------|----------|------|
| **新工作流** | 双轨反思（全量 + 微反思） | 可减少重复操作 3+ 次 | 创建 skill |
| **新配置** | supersedes 审计链设计 | 提升记忆系统可追溯性 | 写入 memory |
| **新工具** | reflect-log.jsonl 格式 | 支持元反思分析 | 记录到 sniff-interests |
| **现有 skill 修复** | evolver 增加 confidence 评分 | 降低噪声技能生成 | patch skill |
| **新工作流** | 量化实盘偏差日志 | 记录信号价 vs 成交价差异 | 创建 skill |

### 6.2 行动清单

- [x] 完成深度笔记生成
- [ ] 创建 `agent-reflection` skill（双轨反思机制）
- [ ] 更新 `evolver` skill（增加 confidence 评分）
- [ ] 更新 `memory-write` skill（增加 supersedes 审计链）
- [ ] 更新 `sniff-interests.md`（标记已探索主题）
- [ ] 写入 `evolution-log.jsonl`
- [ ] 写入 `experience-pool.jsonl`

---

## 附录：相关资源

### 核心文档
- `AGENTS.md` — Hermes 团队协作协议
- `2026-05-17-agent-collaboration-self-evolution.md` — Agent 协作与自我进化
- `2026-05-16-simulated-vs-live-trading-differences.md` — 实盘模拟 vs 真实交易
- `2026-05-17-动态止损策略对比.md` — ATR vs 固定百分比 vs 追踪止损
- `evolver/SKILL.md` — 自我进化引擎

### 外部链接（待验证）
- MCP 官方文档: https://modelcontextprotocol.io
- TradingAgents GitHub: https://github.com/TauricResearch/TradingAgents
- Wilder (1978) ATR 原始论文

---

*📅 2026-05-18 04:00 (Cron Job - 夜间自学习)*  
*⚠️ 网络受限，Tavily 搜索失败，依赖本地知识蒸馏*
## 相关笔记
- [Agent Skills才是关键抽象层](../2026-04-02-Agent Skills才是关键抽象层.md)
- [Claude-Code四层记忆架构](../2026-04-03-Claude-Code四层记忆架构.md)
- [Claude-Code-324-prompts-analysis](../2026-04-04-Claude-Code-324-prompts-analysis.md)
- [SelfImproving-Agent-CLI-infra](../2026-04-05-SelfImproving-Agent-CLI-infra.md)
- [spatial-intelligence-agent-action](../2026-04-05-spatial-intelligence-agent-action.md)
- [agent-loop-core-scheduling](../2026-04-07-agent-loop-core-scheduling.md)
- [email-not-revival-agent-needs-it](../2026-04-07-email-not-revival-agent-needs-it.md)
- [hermes-agent-deep-dive-evolution-roadmap](../2026-04-07-hermes-agent-deep-dive-evolution-roadmap.md)
- [claude-code-tool-execution-orchestration](../2026-04-08-claude-code-tool-execution-orchestration.md)
- [SKILL-md-ai-agent-skills](../2026-04-09-SKILL-md-ai-agent-skills.md)
- [gbrain-hybrid-search-proposal](../2026-04-11-gbrain-hybrid-search-proposal.md)
- [hermes-agent-vs-openclaw](../2026-04-13-hermes-agent-vs-openclaw.md)
- [Cloudflare-EmDash-AI-Agent-CMS](../2026-04-14-Cloudflare-EmDash-AI-Agent-CMS.md)
- [Hermes-Agent-v0.10.0-release-analysis](../2026-04-18-Hermes-Agent-v0.10.0-release-analysis.md)
- [Claude-Opus4.7-Claude-Code-最佳实践](../2026-04-20-Claude-Opus4.7-Claude-Code-最佳实践.md)
- [深入源码-Hermes-Agent-如何实现Self-Improving](../2026-04-23-深入源码-Hermes-Agent-如何实现Self-Improving.md)
- [深入源码Hermes-Agent-Self-Improving](../2026-04-23-深入源码Hermes-Agent-Self-Improving.md)
- [MCP协议生态与Agentic-RAG架构深度学习](../2026-04-27-MCP协议生态与Agentic-RAG架构深度学习.md)
- [LLM-Agent驱动量化交易系统前沿学习](../2026-04-29-LLM-Agent驱动量化交易系统前沿学习.md)
- [Meta-Hyperagents自适应Agent框架](../2026-04-30-Meta-Hyperagents自适应Agent框架.md)
- [AI-Agent记忆架构前沿学习](../2026-05-01-AI-Agent记忆架构前沿学习.md)
- [deepseek-agent-ecosystem](../2026-05-01-deepseek-agent-ecosystem.md)
- [AI-Agent-Protocol-Ecosystem-2026-学习](../2026-05-03-AI-Agent-Protocol-Ecosystem-2026-学习.md)
- [ai-agent-resources-ecosystem](../2026-05-03-ai-agent-resources-ecosystem.md)
- [智能教育-自适应评估](../2026-05-03-智能教育-自适应评估.md)
- [Agent协议生态2026最新进展-MCP-A2A深度融合](../2026-05-04-Agent协议生态2026最新进展-MCP-A2A深度融合.md)
- [个人Agent自进化五步闭环](../2026-05-04-个人Agent自进化五步闭环.md)
- [tradingagents-deep-analysis](../2026-05-05-tradingagents-deep-analysis.md)
- [SOUL-md-Agent-Partner-Transformation](../2026-05-07-SOUL-md-Agent-Partner-Transformation.md)
- [AI-Agent控制流](../2026-05-08-AI-Agent控制流.md)
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
- [20260513-llm-wiki-obsidian-gbrain-知识自组织与自进化](../20260513-llm-wiki-obsidian-gbrain-知识自组织与自进化.md)
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
- [hermes-agent-arxiv-search](../hermes-agent-arxiv-search.md)
- [hermes-agent-源码拆解自我进化机制](../hermes-agent-源码拆解自我进化机制.md)
- [llm-wiki-gbrain-agent-evolution_33aa818c](../llm-wiki-gbrain-agent-evolution_33aa818c.md)
- [不管用ClaudeCode还是OpenClaw先记住这12个知识](../orphan/2026-04-15-不管用ClaudeCode还是OpenClaw先记住这12个知识.md)
- [AI幻觉案例分析-Hermes-Agent不实报道](../orphan/2026-04-19-AI幻觉案例分析-Hermes-Agent不实报道.md)
- [智能教育-personalized-learning](../orphan/2026-05-04-智能教育-personalized-learning.md)
- [具身智能机器人2025年终盘点](../orphan/2026-05-05-具身智能机器人2025年终盘点.md)
- [具身智能机器人2025-商业化元年](../orphan/2026-05-09-具身智能机器人2025-商业化元年.md)
- [claude-learning-roadmap](../orphan/2026-05-10-claude-learning-roadmap.md)
- [0元打通Claude-Codex-OpenCode免费模型6入口](../orphan/2026-05-11-0元打通Claude-Codex-OpenCode免费模型6入口.md)
- [HuggingFace-春季生态-Agentic-World-Modeling](../orphan/2026-05-13-HuggingFace-春季生态-Agentic-World-Modeling.md)
- [具身智能量产关键年](../orphan/2026-05-15-具身智能量产关键年.md)
- [HTML的不合理有效性-Claude-Code-团队](../orphan/2026-05-16-HTML的不合理有效性-Claude-Code-团队.md)
- [GenericAgent](../orphan/GenericAgent.md)
- [skills-autonomous-ai-agents](../skills-autonomous-ai-agents.md)
- [竞品吸收笔记_GenericAgent](../竞品吸收笔记_GenericAgent.md)
