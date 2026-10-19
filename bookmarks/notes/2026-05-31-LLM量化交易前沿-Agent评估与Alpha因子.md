# LLM 量化交易前沿 2026 — 从 Agent 评估到 Alpha 因子挖掘

**学习时间**: 2026-05-31
**数据来源**: arXiv 最新论文 (2026年5月) + GitHub Trending
**主题**: LLM 交易 Agent 评估、时序增强推理、金融合规、多 Agent 信用归因

---

## 一、核心发现

### 发现 1: LLM 交易 Agent 的评估陷阱与修正方案

**论文**: "From Knowing to Doing: A Memory-Controlled Benchmark for LLM Trading Agents" (arXiv:2605.28359)

**问题根源**: 当前 LLM 交易 Agent 的评估存在两个系统性偏差：

1. **知识截断污染 (Knowledge Cutoff Contamination)**
   - 长回测区间（如 2020-2024）与前沿 LLM 的训练数据存在大量重叠
   - LLM 可能"记住"了特定日期的股价走势、财报数据、甚至市场叙事
   - 模型在回测中的"超额收益"可能完全来自记忆而非推理能力
   - 实验证据：当引入 Memory-Control 后（限制 LLM 使用训练数据中的价格信息），Agent 表现大幅下降

2. **原始回报率作为评估指标的缺陷**
   - 原始回报率是股票选择能力的噪声代理
   - 未控制市场 Beta、行业暴露、风险因子
   - 一个简单的"买入并持有"策略在牛市中就能产生高回报

**Memory-Controlled Benchmark 设计**:
```
评估框架:
├── 记忆控制层
│   ├── 盲区回测: 使用 LLM 训练数据之后的时间段
│   ├── 信息遮蔽: 移除 LLM 可能记住的具体价格数据
│   └── 反事实测试: 用虚构的公司名替换真实公司名
│
├── 能力评估层
│   ├── 因子调整 Alpha (控制市场/行业/风格因子)
│   ├── 信息比率 (IR): Alpha / 跟踪误差
│   ├── 最大回撤与 Calmar 比率
│   └── 换手率惩罚 (避免高频交易幻觉)
│
└── 推理质量层
    ├── 决策理由的一致性 (多次独立运行)
    ├── 对市场事件的响应合理性
    └── 风险意识的体现程度
```

**关键结论**: 当正确控制了知识泄漏后，LLM 交易 Agent 的真实表现远低于之前报告的水平。这并不意味着 LLM 无法用于交易，而是我们需要更严谨的评估方法。

### 发现 2: StockR1 — 统一定性推理与定量预测的 RL 框架

**论文**: "Reasoning through Verifiable Forecast Actions: Consistency-Grounded RL for Financial LLMs" (arXiv:2605.21975)

**核心矛盾**: 金融市场的三个本质特征使传统方法失效：
- 极端非平稳性 (Non-stationarity): 昨天的规律今天可能不再适用
- 低信噪比 (Low SNR): 真正的 Alpha 信号被大量噪声淹没
- 外部信息依赖: 新闻、基本面、宏观信号的融合是关键

**StockR1 的三层架构**:

```
Layer 1: 时序增强编码
├── 将 OHLCV 时间序列编码为 LLM 可理解的 token
├── 保留数值精度（不粗暴截断为文本描述）
└── 多尺度时间窗口：日/周/月/季度的并行编码

Layer 2: 推理-预测统一
├── Chain-of-Thought: 自然语言分析推理链
├── Verifiable Forecast: 结构化预测输出
│   ├── direction: up/down/neutral
│   ├── magnitude: 具体涨跌幅预测
│   ├── horizon: 预测时间窗口
│   └── reasoning: 决策理由
└── 一致性约束: 对同一标的的多次推理必须自洽

Layer 3: RL 优化
├── 可验证奖励: 预测是否被市场实际走势验证
├── 一致性奖励: 多次推理是否一致
├── 风险惩罚: 高置信度但错误预测的重惩罚
└── 与 GRPO 的联系: 组采样多个预测，组内比较选最优
```

**与 RLVR 的对比**:
- RLVR 在数学/代码上验证"对/错"
- StockR1 在金融上验证"预测是否准确"——但金融验证是概率性的，非二值
- StockR1 引入了一致性约束作为额外的监督信号，弥补了金融验证的模糊性

### 发现 3: FinGuard — 金融 LLM 合规检测的范式突破

**论文**: "FinGuard: Detecting Financial Regulatory Non-Compliance in LLM Interactions" (arXiv:2605.29427)

**颠覆性结论**: 8B 参数模型 + 领域 RL 可以**大幅超越** 397B 模型 (Qwen3.5-397B-A17B) 和 GPT-5.1

**为什么小模型能赢**:
- 通用安全模型的 harm taxonomy 不覆盖金融监管特有的违规类型
- 金融监管文本高度专业化，通用模型的预训练数据中覆盖不足
- 领域 RL 使小模型在金融合规的决策边界上更加精确

**管线设计**:
```
监管文档 → 自动诱导分类体系 → 合成训练数据 → SFT + 自博弈 RL
```

**自博弈 RL 的关键机制**:
- 模型同时扮演"攻击者"（生成可能的违规交互）和"防御者"（检测违规）
- 攻防博弈使模型的检测能力持续提升
- 无需人工标注违规样本

### 发现 4: 多 Agent 信用归因 — 从全局黑盒到精准定位

**论文**: "Unifying Temporal and Structural Credit Assignment in LLM-Based Multi-Agent Prompt Optimization" (arXiv:2605.30227)

**金融场景的映射**:

在量化交易系统中，多个 Agent 分别负责：
- 新闻情绪分析 Agent
- 技术指标分析 Agent
- 风控检查 Agent
- 执行优化 Agent

当最终交易决策错误时，如何归因到特定 Agent？

**双轴分解**:
- **时序信用**: 哪个分析步骤是关键转折点？（如新闻 Agent 的误判导致了错误方向）
- **结构信用**: 如果替换某个 Agent 的输出，最终决策会怎样变化？（反事实推理）

**代理梯度 (Proxy Gradient)**:
- 不直接计算梯度（离散系统不可微）
- 而是用 LLM 分析薄弱环节，生成"方向性改进建议"
- 类似于人类 code review 中的"这个函数的逻辑有问题，建议改为..."

### 发现 5: FinBoardBench — 从静态测试到动态博弈

**论文**: "FinBoardBench: Benchmarking Dynamic Wealth Management" (arXiv:2605.27896)

**设计思想**: 用经典金融桌游（现金流游戏、Acquire、大富翁）作为 LLM 金融决策能力的测试环境

**为什么用桌游而不是真实市场**:
- 真实市场不可重复——无法做对照实验
- 桌游有明确的规则、可重复的初始条件、可控的随机性
- 桌游保留了金融决策的核心要素：风险管理、资源配置、博弈思维

**评估维度**:
- 战略决策质量（长期规划能力）
- 风险管理意识（分散投资、止损）
- 对手行为预测（博弈论推理）
- 动态适应能力（根据游戏进程调整策略）

---

## 二、技术实现细节

### 2.1 Memory-Controlled Trading Evaluation

```python
# 知识截断控制评估框架
class MemoryControlledEvaluator:
    def __init__(self, llm_trader, market_data):
        self.trader = llm_trader
        self.data = market_data
        self.cutoff_date = llm_trader.training_cutoff  # LLM 训练截止日期
    
    def evaluate(self):
        # 1. 只使用 cutoff 之后的日期
        test_period = self.data[self.data.index > self.cutoff_date]
        
        # 2. 信息遮蔽：移除具体价格，只保留趋势描述
        masked_data = self.mask_price_info(test_period)
        
        # 3. 反事实测试：用虚构名称替换真实公司
        counterfactual_data = self.replace_company_names(test_period)
        
        # 4. 运行三组对比实验
        results = {
            'standard': self.run_backtest(test_period, use_memory=True),
            'masked': self.run_backtest(masked_data, use_memory=False),
            'counterfactual': self.run_backtest(counterfactual_data, use_memory=False)
        }
        
        # 5. 计算 Alpha（因子调整后超额收益）
        alpha = self.compute_factor_adjusted_alpha(results)
        return alpha
    
    def compute_factor_adjusted_alpha(self, results):
        """Fama-French 因子调整"""
        # 回归: R_portfolio = α + β_mkt * R_mkt + β_smb * SMB + β_hml * HML
        # Alpha = 截距项 α
        import statsmodels.api as sm
        factors = self.load_fama_french_factors()
        portfolio_returns = results['standard']['daily_returns']
        X = sm.add_constant(factors[['Mkt-RF', 'SMB', 'HML']])
        model = sm.OLS(portfolio_returns, X).fit()
        return {
            'alpha_annualized': model.params['const'] * 252,
            't_stat': model.tvalues['const'],
            'information_ratio': model.params['const'] / model.resid.std() * (252 ** 0.5)
        }
```

### 2.2 StockR1 一致性约束 RL

```python
# 一致性约束的 RL 训练
class ConsistencyRLTrainer:
    def __init__(self, base_llm, reward_fn):
        self.llm = base_llm
        self.reward_fn = reward_fn
    
    def compute_reward(self, predictions, actual_returns):
        """综合奖励函数"""
        rewards = []
        
        for pred, actual in zip(predictions, actual_returns):
            # 1. 准确性奖励（方向 + 幅度）
            accuracy_reward = self.accuracy_score(pred, actual)
            
            # 2. 一致性奖励（多次预测的自洽性）
            consistency_reward = self.consistency_score(
                pred['reasoning'], 
                pred.get('previous_reasonings', [])
            )
            
            # 3. 置信度校准奖励（高置信度预测必须更准确）
            if pred['confidence'] > 0.8:
                calibration_penalty = -2.0 if not pred['direction_correct'] else 0.5
            else:
                calibration_penalty = 0
            
            # 4. 风险意识奖励
            risk_reward = 0.5 if pred.get('stop_loss_set', False) else -0.2
            
            total = (accuracy_reward * 0.4 + 
                    consistency_reward * 0.3 + 
                    calibration_penalty + 
                    risk_reward)
            rewards.append(total)
        
        return rewards
```

---

## 三、实践启发与 Skill 改进建议

### 3.1 quant-trading Skill 改进建议

**当前缺陷**:
- 缺少"知识截断控制"机制——回测时可能使用 LLM 训练数据中的信息
- 缺少"因子调整 Alpha"的计算——当前只用原始收益率
- 缺少"一致性检查"——对同一标的的多次分析是否自洽

**建议 patch**:
1. 添加 `evaluate_with_memory_control()` 方法
2. 添加 Fama-French 因子调整的 Alpha 计算
3. 添加推理一致性检查模块

### 3.2 新 Skill 建议: financial-llm-compliance

基于 FinGuard 的发现：
- 金融 AI 系统需要专门的合规检测层
- 管线：监管文档 → 分类体系 → 合成数据 → SFT+RL
- 可作为量化交易系统的"护栏"(Guardrail) Skill

### 3.3 对 Hermes Agent 评估方法的改进

**从 PTCG-Bench 和 FinBoardBench 的启示**:
- Hermes Skill 的评估应该从"能否完成任务"升级到"在动态环境中持续表现如何"
- 引入"Harness 消融实验"：定期禁用单个 Skill，观察系统整体表现变化
- 自进化的标准应该是"持续稳定改进"而非"偶尔一次成功"

---

## 四、知识缺口

1. **知识截断的精确检测**: 如何自动判断 LLM 是否在回测中使用了训练数据中的信息？
2. **金融 RL 的奖励稀疏性**: 市场反馈周期长（天/周级），如何提供足够密集的训练信号？
3. **多策略组合的信用归因**: 当量化系统同时运行多个策略时，如何归因收益到具体策略？

---

## 五、参考资源

- arXiv:2605.28359 — From Knowing to Doing: Memory-Controlled Benchmark (2026-05-27)
- arXiv:2605.21975 — StockR1: Consistency-Grounded RL for Financial LLMs (2026-05-21)
- arXiv:2605.29427 — FinGuard: Financial Regulatory Compliance Detection (2026-05-28)
- arXiv:2605.27896 — FinBoardBench: Dynamic Wealth Management (2026-05-27)
- arXiv:2605.30227 — Unifying Temporal and Structural Credit Assignment (2026-05-28)

---

**笔记字数**: ~2800 字
**核心发现数**: 5 个
**实践启发**: quant-trading Skill 改进、financial-llm-compliance 新 Skill 建议、评估方法改进

---

## 相关笔记

- [2026-04-05-Hermes-Agent-competitor-analysis](./2026-04-05-Hermes-Agent-competitor-analysis.md)
- [2026-04-07-hermes-agent-deep-dive-evolution-roadmap](./2026-04-07-hermes-agent-deep-dive-evolution-roadmap.md)
- [2026-04-13-hermes-agent-vs-openclaw](./2026-04-13-hermes-agent-vs-openclaw.md)
- [2026-05-22-Hermes-Agent四层记忆架构深度分析](./2026-05-22-Hermes-Agent四层记忆架构深度分析.md)
- [2026-04-18-Hermes-Agent-v0.10.0-insight](./2026-04-18-Hermes-Agent-v0.10.0-insight.md)
- [2026-04-18-Hermes-Agent-v0.10.0-release-analysis](./2026-04-18-Hermes-Agent-v0.10.0-release-analysis.md)
- [hermes-agent-arxiv-search](./hermes-agent-arxiv-search.md)
- [2026-04-23-深入源码-Hermes-Agent-如何实现Self-Improving](./2026-04-23-深入源码-Hermes-Agent-如何实现Self-Improving.md)
- [2026-04-23-深入源码Hermes-Agent-Self-Improving](./2026-04-23-深入源码Hermes-Agent-Self-Improving.md)
- [hermes-agent-源码拆解自我进化机制](./hermes-agent-源码拆解自我进化机制.md)
- [2026-05-25-浅浅走入Hermes-Agent的记忆-毛毛MA](./2026-05-25-浅浅走入Hermes-Agent的记忆-毛毛MA.md)
- [2026-05-26-hermes-agent-5-usage](./2026-05-26-hermes-agent-5-usage.md)
- [2026-05-18-SmallRustHermes-Agent自我进化三个闭环](./2026-05-18-SmallRustHermes-Agent自我进化三个闭环.md)
- [2026-04-02-Agent Skills才是关键抽象层](./2026-04-02-Agent Skills才是关键抽象层.md)
- [2026-05-30-SQLite足以支撑持久化工作流-Agent时代的极简基础设施](./2026-05-30-SQLite足以支撑持久化工作流-Agent时代的极简基础设施.md)
- [2026-04-05-SelfImproving-Agent-CLI-infra](./2026-04-05-SelfImproving-Agent-CLI-infra.md)
- [2026-04-05-spatial-intelligence-agent-action](./2026-04-05-spatial-intelligence-agent-action.md)
- [2026-04-07-agent-loop-core-scheduling](./2026-04-07-agent-loop-core-scheduling.md)
- [2026-04-07-email-not-revival-agent-needs-it](./2026-04-07-email-not-revival-agent-needs-it.md)
- [2026-05-29-AI-Agent自进化系统2026-闭环设计-记忆架构与工程实践](./2026-05-29-AI-Agent自进化系统2026-闭环设计-记忆架构与工程实践.md)
- [2026-04-09-SKILL-md-ai-agent-skills](./2026-04-09-SKILL-md-ai-agent-skills.md)
- [2026-05-22-Agent自我进化与学习系统-深度研究](./2026-05-22-Agent自我进化与学习系统-深度研究.md)
- [2026-04-13-4-ai-agent-frameworks-comparison](./2026-04-13-4-ai-agent-frameworks-comparison.md)
- [2026-04-14-Cloudflare-EmDash-AI-Agent-CMS](./2026-04-14-Cloudflare-EmDash-AI-Agent-CMS.md)
- [2026-04-16-Gemini3-AI-Agent-competition](./2026-04-16-Gemini3-AI-Agent-competition.md)
- [skills-autonomous-ai-agents](./skills-autonomous-ai-agents.md)
- [2026-05-21-react-agent-llm-agentic-training-research](./2026-05-21-react-agent-llm-agentic-training-research.md)
- [2026-05-28-五大LLM在67%事实上有分歧-Agent可靠性警钟](./2026-05-28-五大LLM在67%事实上有分歧-Agent可靠性警钟.md)
- [2026-04-22-ESP-Claw扩展分析-NeuroClaw边缘AI-Agent](./2026-04-22-ESP-Claw扩展分析-NeuroClaw边缘AI-Agent.md)
- [2026-04-23-MCP协议与Agentic-LLM-2025趋势](./2026-04-23-MCP协议与Agentic-LLM-2025趋势.md)
- [2026-05-28-George-Hotz-警告-Coding-Agents-是昂贵错误](./2026-05-28-George-Hotz-警告-Coding-Agents-是昂贵错误.md)
- [2026-05-28-AI-Coding-Agents-GitHub-蔓延-开发范式被改写](./2026-05-28-AI-Coding-Agents-GitHub-蔓延-开发范式被改写.md)
- [2026-04-27-MCP协议生态与Agentic-RAG架构深度学习](./2026-04-27-MCP协议生态与Agentic-RAG架构深度学习.md)
- [2026-05-01-deepseek-agent-ecosystem](./2026-05-01-deepseek-agent-ecosystem.md)
- [2026-04-29-LLM-Agent驱动量化交易系统前沿学习](./2026-04-29-LLM-Agent驱动量化交易系统前沿学习.md)
- [2026-04-30-Meta-Hyperagents自适应Agent框架](./2026-04-30-Meta-Hyperagents自适应Agent框架.md)
- [竞品吸收笔记_GenericAgent](./竞品吸收笔记_GenericAgent.md)
- [2026-04-30-stoc蒸馏-AI-Agent自学习量化交易系统](./2026-04-30-stoc蒸馏-AI-Agent自学习量化交易系统.md)
- [2026-05-01-AI-Agent记忆架构前沿学习](./2026-05-01-AI-Agent记忆架构前沿学习.md)
- [2026-05-03-AI-Agent-Protocol-Ecosystem-2026-学习](./2026-05-03-AI-Agent-Protocol-Ecosystem-2026-学习.md)
- [2026-05-21-Qwen3.7-Agent Frontier](./2026-05-21-Qwen3.7-Agent Frontier.md)
- [2026-05-03-ai-agent-resources-ecosystem](./2026-05-03-ai-agent-resources-ecosystem.md)
- [2026-05-04-Agent协议生态2026最新进展-MCP-A2A深度融合](./2026-05-04-Agent协议生态2026最新进展-MCP-A2A深度融合.md)
- [2026-ai-agent-structured-output-multi-agent-alpha-research](./2026-ai-agent-structured-output-multi-agent-alpha-research.md)
- [2026-05-04-个人Agent自进化五步闭环](./2026-05-04-个人Agent自进化五步闭环.md)
- [proactive-learn-2026-05-27-ai-agent-quant](./proactive-learn-2026-05-27-ai-agent-quant.md)
- [2026-05-05-tradingagents-deep-analysis](./2026-05-05-tradingagents-deep-analysis.md)
- [2026-05-05-Zero-to-CAD-Agent闭环合成百万级可执行CAD程序](./2026-05-05-Zero-to-CAD-Agent闭环合成百万级可执行CAD程序.md)
- [2026-05-27-mem0-agent-memory-deep-dive](./2026-05-27-mem0-agent-memory-deep-dive.md)
- [2026-05-27-ai-agent-quant-trading-trends](./2026-05-27-ai-agent-quant-trading-trends.md)
- [2026-05-28-Agent需要RAG吗-协同vs高可信](./2026-05-28-Agent需要RAG吗-协同vs高可信.md)
- [2026-05-07-SOUL-md-Agent-Partner-Transformation](./2026-05-07-SOUL-md-Agent-Partner-Transformation.md)
- [2026-05-07-Superpowers-Agentic技能框架](./2026-05-07-Superpowers-Agentic技能框架.md)
- [anthropic-managed-agents-dreaming-outcomes](./anthropic-managed-agents-dreaming-outcomes.md)
- [2026-05-08-addyosmani-agent-skills生产级Agent技能包](./2026-05-08-addyosmani-agent-skills生产级Agent技能包.md)
- [2026-05-08-AI-Agent控制流](./2026-05-08-AI-Agent控制流.md)
- [2026-05-09-Agent-native-PM方法论](./2026-05-09-Agent-native-PM方法论.md)
- [2026-05-09-AG-UI-AI-Agent前端标准](./2026-05-09-AG-UI-AI-Agent前端标准.md)
- [2026-05-09-OfficeCLI-AI-Agent的Office工具](./2026-05-09-OfficeCLI-AI-Agent的Office工具.md)
- [google-a2a-protocol-multi-agent-2026-05-19](./google-a2a-protocol-multi-agent-2026-05-19.md)
- [2026-05-11-AI趋势2026-推理时计算与反思Agent](./2026-05-11-AI趋势2026-推理时计算与反思Agent.md)
- [llm-wiki-gbrain-agent-evolution_33aa818c](./llm-wiki-gbrain-agent-evolution_33aa818c.md)
- [2026-05-14-MATLAB-Agentic-Toolkit分析](./2026-05-14-MATLAB-Agentic-Toolkit分析.md)
- [2026-05-27-45个HermesAgent自动化案例（上）](./2026-05-27-45个HermesAgent自动化案例（上）.md)
- [2026-05-14-Agent工程4月实践-不要一上来就做Agent](./2026-05-14-Agent工程4月实践-不要一上来就做Agent.md)
- [2026-05-14-HTML-Anything-Agent驱动HTML编辑器](./2026-05-14-HTML-Anything-Agent驱动HTML编辑器.md)
- [2026-05-14-手撸Agent-ReAct-Loop从零实现](./2026-05-14-手撸Agent-ReAct-Loop从零实现.md)
- [2026-05-15-上下文才是Agent的命门-QClaw上下文竞争论](./2026-05-15-上下文才是Agent的命门-QClaw上下文竞争论.md)
- [2026-05-26-Agent架构关键变化-Harness成为新后端](./2026-05-26-Agent架构关键变化-Harness成为新后端.md)
- [2026-05-27-ai-agent-2026-deep-dive](./2026-05-27-ai-agent-2026-deep-dive.md)
- [Pi-Agent-vs-Hermes-vs-Claude-Code对比分析](./Pi-Agent-vs-Hermes-vs-Claude-Code对比分析.md)
- [2026-05-27-ai-agent-quant-trends](./2026-05-27-ai-agent-quant-trends.md)
- [2026-05-26-ai-agent-mas-production](./2026-05-26-ai-agent-mas-production.md)
- [2026-05-25-Claude-Code之父Boris-Cherny-编程已死千级Agent夜间打工](./2026-05-25-Claude-Code之父Boris-Cherny-编程已死千级Agent夜间打工.md)
- [2026-05-25-高德OPC自主增长系统-Harness多Agent架构](./2026-05-25-高德OPC自主增长系统-Harness多Agent架构.md)
- [2026-05-26-agent-skills-ai-操作手册](./2026-05-26-agent-skills-ai-操作手册.md)
- [2026-05-29-LLM-Agent组合一致性边界研究](./2026-05-29-LLM-Agent组合一致性边界研究.md)
- [2026-05-29-AI-Agent-Quant-2026-Trends](./2026-05-29-AI-Agent-Quant-2026-Trends.md)
- [ai-agent-2026-trends-learning](./ai-agent-2026-trends-learning.md)
- [2026-05-28-ai-agent-trends](./2026-05-28-ai-agent-trends.md)
- [2026-05-16-PicoClaw-超轻量AI-Agent框架](./2026-05-16-PicoClaw-超轻量AI-Agent框架.md)
- [2026-05-18-agent-memory-systems-comparison](./2026-05-18-agent-memory-systems-comparison.md)
- [2026-05-18-Agent元认知-LLM不确定性感知](./2026-05-18-Agent元认知-LLM不确定性感知.md)
- [2026-05-22-OpenClaw日常聊天黑化Agent-ULSPB安全研究](./2026-05-22-OpenClaw日常聊天黑化Agent-ULSPB安全研究.md)
- [2026-05-23-Domain-Camouflaged-Injection-Attacks-域伪装注入绕过多Agent检测](./2026-05-23-Domain-Camouflaged-Injection-Attacks-域伪装注入绕过多Agent检测.md)
- [2026-05-25-Agent-Harness-Engineering-从Prompt到Harness的范式跃迁](./2026-05-25-Agent-Harness-Engineering-从Prompt到Harness的范式跃迁.md)
- [2026-05-23-Superset-YC-P26-AI-Agent-IDE](./2026-05-23-Superset-YC-P26-AI-Agent-IDE.md)
- [2026-05-24-PiAgent深度分析](./2026-05-24-PiAgent深度分析.md)
- [2026-05-24-Cloudflare-Agents-Week-2026-Agentic-Cloud全栈基础设施](./2026-05-24-Cloudflare-Agents-Week-2026-Agentic-Cloud全栈基础设施.md)
- [2026-05-25-DeepSeek-Reasonix-开源省钱Agent](./2026-05-25-DeepSeek-Reasonix-开源省钱Agent.md)
- [2026-05-31-LLM-Agent多智能体信用归因与自进化](./2026-05-31-LLM-Agent多智能体信用归因与自进化.md)
- [2026-04-03-Claude-Code四层记忆架构](./2026-04-03-Claude-Code四层记忆架构.md)
- [2026-04-04-Claude-Code-324-prompts-analysis](./2026-04-04-Claude-Code-324-prompts-analysis.md)
- [2026-04-08-claude-code-tool-execution-orchestration](./2026-04-08-claude-code-tool-execution-orchestration.md)
- [2026-04-20-Claude-Opus4.7-Claude-Code-最佳实践](./2026-04-20-Claude-Opus4.7-Claude-Code-最佳实践.md)
- [2026-05-09-Claude-Code工程师放弃Markdown转HTML](./2026-05-09-Claude-Code工程师放弃Markdown转HTML.md)
- [2026-05-08-MACD-KDJ共振策略](./2026-05-08-MACD-KDJ共振策略.md)
- [2026-05-23-MACD-KDJ-RSI-BOLL-复合量化交易策略体系与动态回测优化](./2026-05-23-MACD-KDJ-RSI-BOLL-复合量化交易策略体系与动态回测优化.md)
- [2026-04-24-通达信tdxquant量化模拟交易封装](./2026-04-24-通达信tdxquant量化模拟交易封装.md)
- [tdx-quant-trader](./tdx-quant-trader.md)
- [2026-05-26-proactive-learn-mcp-llm-quant-evolution](./2026-05-26-proactive-learn-mcp-llm-quant-evolution.md)
