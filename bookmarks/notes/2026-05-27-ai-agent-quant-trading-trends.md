# 2026 AI Agent 与量化交易前沿技术学习笔记

**学习日期**: 2026-05-27  
**学习主题**: AI Agent 多智能体编排 & 量化交易新技术  
**来源**: arXiv 最新论文 (2026年4-5月)

---

## 一、核心发现

### 发现1: STAR-PólyaMath — 多智能体推理框架的突破性进展

**论文**: arXiv:2605.19338 — "STAR-PólyaMath: Multi-Agent Reasoning under Persistent Meta-Strategic Supervision"  
**作者**: Jiaao Wu, Xian Zhang, Hanzhang Liu, Sophia Zhang, Fan Yang, Yinpeng Dong  
**提交日期**: 2026年5月19日

**核心贡献**:
- 提出了一种**状态机编排的多智能体框架**，通过元级监督解决长程推理中的根本性问题
- 三大痛点解决: 幻觉累积(hallucination accumulation)、记忆碎片化(memory fragmentation)、推理-工具权衡失衡(imbalanced reasoning-tool trade-offs)
- **关键创新**: 持久化元战略家(Persistent Meta-Strategist) — 维护跨尝试记忆，发出高层战略指导或强制指令，使系统能够跳出无效循环而非停滞或过度依赖工具

**架构设计**:
```
STAR-PólyaMath 架构:
┌─────────────────────────────────────────────────────────────┐
│  Orchestrator (Python, reasoning-free)                      │
│  ├─ 嵌套的 challenge-step-replan 循环                       │
│  ├─ 控制与推理分离                                          │
│  └─ 通过 trace-back 和 re-planning 限制错误传播             │
│                                                             │
│  Meta-Strategist (持久化)                                   │
│  ├─ 跨尝试记忆                                              │
│  ├─ 高层战略指导                                            │
│  └─ 强制指令 (escape unproductive loops)                    │
│                                                             │
│  Reasoner-Verifier 交互                                     │
│  ├─ 结构化交互                                              │
│  └─ 避免单一模型偏差                                        │
└─────────────────────────────────────────────────────────────┘
```

**性能表现**:
- 在8个顶级竞赛基准上取得**SOTA**: AIME 2025-2026, MathArena Apex Shortlist, MathArena Apex 2025, Putnam 2025, IMO 2025, HMMT February 2026, USAMO 2026
- **完美分数**: AIME, Putnam, HMMT
- **最大优势**: Apex 2025 — 93.75% vs 最强基线 GPT-5.5 的 80.21% (差距13.54%)
- 消融实验证明: 增益来自**框架编排**而非模型多样性

**代码仓库**: https://github.com/Julius-Woo/STAR-PolyaMath

---

### 发现2: 深度强化学习在量化交易中的新范式

**论文**: arXiv:2605.17307 — "Deep Reinforcement Learning Framework for Diversified Portfolio Management Across Global Equity markets"  
**作者**: Kamil Kashif, Robert Ślepaczuk  
**提交日期**: 2026年5月17日

**核心贡献**:
- 开发并评估了**深度强化学习框架**用于全球股票市场动态资产配置
- 使用**Soft Actor-Critic (SAC)** 算法在马尔可夫决策过程中学习连续投资组合权重
- 奖励函数整合: 交易成本、换手惩罚、分散化约束

**实验设计**:
```
模型配置 (5种变体):
├─ 奖励公式变化
├─ 策略结构: flat vs hierarchical Dirichlet
├─ 投资组合约束
└─ 时序编码器: LSTM vs Transformer

评估方法:
├─ Walk-forward optimization
├─ 16个样本外折叠 (2003-2026)
└─ 三大市场: Nasdaq-100, Nikkei 225, Euro Stoxx 50
```

**关键发现**:
- RL策略在**Euro Stoxx 50**实现统计显著的超额收益
- 中心假设**仅部分证实**: 在HAC稳健推断下，没有策略在所有市场都实现统计显著的超额收益(相对于Buy and Hold)
- **Regime分析**: RL在**高不确定性时期**价值最大
- **Ensemble聚合**跨市场改善风险调整后收益，证实地理分散化优势

**实践启示**:
- 单一市场的RL策略难以在所有市场都超越简单基准
- 跨市场ensemble是更稳健的选择
- 高不确定性时期的策略价值更高

---

### 发现3: 市场规则感知的神经网络 — 领域知识嵌入的新范式

**论文**: arXiv:2605.09061 — "A Market-Rule-Informed Neural Network for Efficient Imbalance Electricity Price Forecasting"  
**作者**: Runyao Yu, Julia Lin, Derek W. Bunn, Jochen Stiasny, Wentao Wang, Yujie Chen, Tara Esterl, Peter Palensky, Jochen L. Cremer  
**提交日期**: 2026年5月9日

**核心贡献**:
- 提出**市场规则感知神经网络(MRINN)** — 将不平衡价格形成规则嵌入神经网络的潜在空间
- 保留原始信号信息的同时利用**透明的市场规则先验**
- 分析操作鲁棒性: 移除价格组件信息后的性能

**技术细节**:
```
MRINN 架构特点:
├─ 将市场规则嵌入 latent space
├─ 保留原始信号信息
├─ 利用透明先验知识
└─ 可解释性增强

优势:
├─ 可训练参数大幅减少
├─ 训练时间显著缩短
└─ 性能与通用深度学习基线相当
```

**应用背景**:
- 实时不平衡电价预测
- 电池资产和自动竞价管道参与平衡市场
- 解决: 非线性市场规则价格形成、异构输入信号、数据不完整(通信延迟、发布滞后、测量中断)

**代码仓库**: https://runyao-yu.github.io/MRINN/

---

### 发现4: AI Agent 的欧盟法律合规框架

**论文**: arXiv:2604.04604 — "AI Agents Under EU Law"  
**作者**: Luca Nannini, Adam Leon Smith, Michele Joshua Maggini, Enrico Panai, Sandra Feliciano, Aleksandr Tiulkanov, Elena Maran, James Gealy, Piercosma Bisconti  
**提交日期**: 2026年4月6日

**核心贡献**:
- 首次系统性**监管映射** — 为AI Agent提供商提供合规框架
- 整合9项法规: AI Act、GDPR、Cyber Resilience Act、Digital Services Act、Data Act、Data Governance Act、NIS2 Directive、Product Liability Directive
- 提出**9类Agent部署分类**和**12步合规架构**

**关键结论**:
- **高风险Agent系统**若存在不可追踪的行为漂移，当前无法满足AI Act的基本要求
- 提供商的基础合规任务是**详尽的Agent外部行动、数据流、连接系统和受影响人员的清单**

**合规挑战**:
- 网络安全
- 人类监督
- 多方行动链的透明度
- 运行时行为漂移

---

## 二、技术细节与代码示例

### STAR-PólyaMath 框架核心代码模式

基于论文描述，框架核心逻辑如下:

```python
"""
STAR-PólyaMath 框架伪代码
基于: arXiv:2605.19338
"""

class MetaStrategist:
    """持久化元战略家 — 跨尝试记忆与高层控制"""
    
    def __init__(self):
        self.cross_attempt_memory = []  # 跨尝试记忆
        self.strategy_history = []
        
    def issue_guidance(self, current_state, attempt_count):
        """发出高层战略指导"""
        # 分析当前状态和历史
        # 判断是否陷入无效循环
        if self._is_unproductive_loop(current_state):
            return self._generate_escape_strategy()
        return self._generate_strategic_guidance()
    
    def _is_unproductive_loop(self, state):
        """检测无效循环"""
        # 基于跨尝试记忆判断
        pass


class Orchestrator:
    """Python编排器 — 控制与推理分离"""
    
    def run(self, problem):
        """嵌套的 challenge-step-replan 循环"""
        for challenge in self.challenges:
            for step in challenge.steps:
                result = self._execute_step(step)
                if self._needs_replan(result):
                    self._replan(challenge, step, result)
                self._trace_back(result)  # 错误传播限制
    
    def _execute_step(self, step):
        """执行单个步骤"""
        # 调用 Reasoner
        pass
    
    def _replan(self, challenge, step, result):
        """重新规划"""
        # 基于trace-back结果调整策略
        pass


class ReasonerVerifierPair:
    """结构化 Reasoner-Verifier 交互"""
    
    def solve(self, problem):
        reasoner_output = self.reasoner.generate(problem)
        verifier_result = self.verifier.check(reasoner_output)
        
        if not verifier_result.passed:
            # 触发重新推理
            return self._refine(reasoner_output, verifier_result)
        return reasoner_output
```

### 深度强化学习投资组合管理代码模式

```python
"""
深度强化学习投资组合管理框架
基于: arXiv:2605.17307
"""

import gymnasium as gym
from stable_baselines3 import SAC

class PortfolioMDP(gym.Env):
    """投资组合马尔可夫决策过程"""
    
    def __init__(self, market_data, config):
        self.market_data = market_data
        self.transaction_cost = config.get('transaction_cost', 0.001)
        self.turnover_penalty = config.get('turnover_penalty', 0.01)
        self.diversification_constraint = config.get('diversification', True)
        
    def step(self, action):
        """action: 连续的投资组合权重"""
        # 计算收益
        returns = self._calculate_returns(action)
        
        # 计算交易成本
        turnover = self._calculate_turnover(action)
        cost = turnover * self.transaction_cost
        
        # 计算惩罚
        penalty = self._calculate_penalty(action)
        
        # 奖励 = 收益 - 成本 - 惩罚
        reward = returns - cost - penalty
        
        return next_state, reward, done, truncated, info
    
    def _calculate_penalty(self, action):
        """分散化约束惩罚"""
        if self.diversification_constraint:
            # Dirichlet分布约束
            return self._dirichlet_penalty(action)
        return 0


# SAC算法训练
model = SAC(
    "MlpPolicy",
    env=portfolio_env,
    policy_kwargs={
        'net_arch': [512, 512, 256],
        'activation_fn': 'relu'
    },
    learning_rate=3e-4,
    buffer_size=100000,
    batch_size=256,
    gamma=0.99,
    tau=0.005,
    train_freq=1,
    gradient_steps=1,
    verbose=1
)

model.learn(total_timesteps=1000000)
```

### 市场规则感知神经网络架构

```python
"""
市场规则感知神经网络 (MRINN)
基于: arXiv:2605.09061
"""

import torch
import torch.nn as nn

class MarketRuleInformedNN(nn.Module):
    """市场规则感知神经网络"""
    
    def __init__(self, input_dim, market_rules):
        super().__init__()
        self.market_rules = market_rules  # 嵌入的市场规则先验
        
        # 编码器
        self.encoder = nn.Sequential(
            nn.Linear(input_dim, 256),
            nn.ReLU(),
            nn.Linear(256, 128),
            nn.ReLU()
        )
        
        # 规则嵌入层
        self.rule_embedding = self._create_rule_embedding()
        
        # 融合层
        self.fusion = nn.Sequential(
            nn.Linear(128 + self.rule_dim, 64),
            nn.ReLU(),
            nn.Linear(64, 32),
            nn.ReLU()
        )
        
        # 输出层
        self.output = nn.Linear(32, 1)
        
    def _create_rule_embedding(self):
        """创建市场规则嵌入"""
        # 将市场规则编码为可学习的嵌入
        pass
    
    def forward(self, x):
        # 编码原始信号
        encoded = self.encoder(x)
        
        # 获取规则嵌入
        rule_emb = self.rule_embedding()
        
        # 融合
        fused = torch.cat([encoded, rule_emb], dim=-1)
        fused = self.fusion(fused)
        
        return self.output(fused)
```

---

## 三、实践启发

### 1. 多智能体编排的核心原则

从STAR-PólyaMath可以提炼出以下通用原则:

| 原则 | 说明 | 应用场景 |
|------|------|----------|
| 控制与推理分离 | Orchestrator只负责流程控制，不直接推理 | 任何多智能体系统 |
| 持久化记忆 | 跨尝试/跨会话的记忆机制 | 长期任务、迭代优化 |
| 元级监督 | 高层战略指导而非细节控制 | 复杂问题分解 |
| 错误传播限制 | 通过trace-back和re-planning控制错误 | 高可靠性需求场景 |
| 结构化交互 | Reasoner-Verifier配对 | 需要验证的场景 |

### 2. 量化交易RL策略的实用建议

基于arXiv:2605.17307的发现:

- **不要期望单一策略在所有市场都有效**: 不同市场有不同的动态特性
- **高不确定性时期是RL的价值窗口**: 传统方法在这些时期表现较差
- **跨市场ensemble是稳健选择**: 地理分散化带来风险调整收益
- **奖励函数设计至关重要**: 交易成本、换手惩罚、分散化约束必须整合
- **Walk-forward验证是必须的**: 避免过拟合

### 3. 领域知识嵌入的范式转移

MRINN展示了**规则感知神经网络**的价值:

- 将领域规则嵌入latent space而非作为后处理
- 减少可训练参数同时保持性能
- 提高可解释性和透明度
- 适用于任何有明确规则约束的领域

### 4. AI Agent合规性设计

从欧盟AI Agent法律框架:

- **行动清单**是合规基础: 记录所有外部行动、数据流、连接系统
- **行为漂移监控**是高风险系统的关键
- **多方透明度**需要设计在架构层面
- **人类监督机制**必须内建而非外挂

---

## 四、知识缺口与后续探索

### 待深入领域

1. **STAR-PólyaMath 代码实现分析**: 需要深入阅读GitHub仓库代码，理解具体实现细节
2. **SAC算法在金融时间序列的调参技巧**: 论文提到5种配置变体，需要理解具体差异
3. **MRINN的市场规则编码方法**: 如何将非结构化的市场规则转化为可学习的嵌入
4. **AI Agent合规架构的具体实现**: 12步合规架构如何落地为技术组件

### 技术趋势观察

| 趋势 | 证据 | 影响评估 |
|------|------|----------|
| 多智能体编排成为主流 | STAR-PólyaMath SOTA结果 | 高 — 需掌握编排模式 |
| RL在量化中从实验走向实用 | 67页完整实证研究 | 中高 — 需评估适用性 |
| 领域知识嵌入神经网络 | MRINN参数效率提升 | 高 — 通用模式 |
| AI Agent合规成为刚需 | 欧盟系统性监管映射 | 高 — 影响系统设计 |

---

## 五、进化评估

### 可采纳的新技能/方法

1. **多智能体状态机编排模式** — 高价值，可复用
   - STAR-PólyaMath的challenge-step-replan循环
   - 控制与推理分离架构
   - 持久化元战略家模式

2. **市场规则感知神经网络模式** — 中价值，特定领域适用
   - 领域规则嵌入latent space
   - 规则-数据融合架构

3. **Walk-forward验证框架** — 高价值，量化通用
   - 时间序列模型的稳健验证方法

### 新工具/资源

- STAR-PólyaMath代码: https://github.com/Julius-Woo/STAR-PolyaMath
- MRINN实现: https://runyao-yu.github.io/MRINN/

### 现有技能缺陷

- 需要补充多智能体编排的具体实现模式
- 量化交易的walk-forward验证需要标准化

---

**笔记字数**: ~3200字  
**核心发现数**: 4个  
**技术细节**: 3个代码示例  
**实践启发**: 4个方面  
**知识缺口**: 4个待探索领域

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
- [ai-agent-quant-trends](2026-05-27-ai-agent-quant-trends.md)
- [mem0-agent-memory-deep-dive](2026-05-27-mem0-agent-memory-deep-dive.md)
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
