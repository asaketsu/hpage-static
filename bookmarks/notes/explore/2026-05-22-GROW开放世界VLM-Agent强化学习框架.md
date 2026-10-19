# GROW: Aligning GRPO with State-Action Modeling for Open-World VLM Agents

- 📅 2026-05-22
- ⭐ 4.5/5 — 将 GRPO 成功适配开放世界多轮 VLM Agent 场景，轨迹分解思路简洁有效，800+ 任务 SOTA
- 🏷️ #强化学习 #VLM-Agent #GRPO #开放世界 #Minecraft #轨迹分解 #论文精读
- 📰 arXiv:2605.20246 | cs.LG
- 🔗 https://arxiv.org/abs/2605.20246

## 摘要

GROW 是一个专为开放世界 VLM Agent 设计的强化学习框架。核心创新在于将标准 GRPO 中「完整轨迹作为优化单元」改为「轨迹分解为状态-动作样本」，解决了开放世界任务中轨迹过长导致上下文溢出和噪声干扰的问题。在 800+ Minecraft 任务上达到 SOTA，GUI 任务成功率从 39.1% 提升到 68.4%，且泛化到未训练任务仍显著提升。

## 核心问题与研究动机

### 背景问题

- VLM Agent 在开放世界任务中需要多轮视觉感知和动作执行
- 现有方法主要依赖 SFT（监督微调）+ 专家演示，数据获取成本高且难以扩展
- GRPO（Group Relative Policy Optimization）在单轮任务中表现优异，但直接迁移到多轮开放世界面临两大障碍：
  1. **上下文过长**：完整轨迹作为训练样本，交互步数累积导致 context 超出 token 限制
  2. **噪声过多**：长轨迹中大量无关信息干扰策略梯度估计

### 研究目标

将 GRPO 有效地适配到开放世界 VLM Agent 的多轮强化学习场景中。

## 方法论（详细）

### 整体框架

GROW 框架分为两个阶段：

1. **Cold-start 阶段**：在状态-动作样本上进行冷启动训练
2. **GRPO-based 策略精炼阶段**：通过轨迹分解进行策略优化

### 关键技术 1：轨迹分解（Trajectory Decomposition）

- **问题**：标准 GRPO 中，每条完整轨迹 τ = {(s₁,a₁), (s₂,a₂), ..., (sₕ,aₕ)} 作为一个训练样本
- **GROW 方案**：将每条轨迹按步分解为独立的状态-动作样本 (sᵢ,ₜ, aᵢ,ₜ)
- **奖励传播**：使用折扣因子 γ 向后传播稀疏回合奖励

  rᵢ,ₜ = γ^(Hᵢ-t) · R(τᵢ)

  其中 γ ∈ (0,1) 是折扣因子，Hᵢ 是轨迹长度

- **关键效果**：
  - 接近任务完成的步骤获得更强的学习信号
  - 每个样本的上下文长度固定（只有当前状态的短历史）
  - 避免了完整轨迹的上下文累积问题

### 关键技术 2：状态-动作样本的策略优化

- **优势计算**：在同一个 rollout 组的状态-动作样本上计算相对优势

  Aᵢ,ₜ = (rᵢ,ₜ - μ) / σ

  其中 μ 和 σ 是同一 rollout 组内所有状态-动作样本奖励的均值和标准差

- **训练目标**：类似 PPO 的 clip 目标函数，但优化单元从完整轨迹变为细粒度状态-动作样本
- **概率比**：ρᵢ,ₜ(θ) = πθ(aᵢ,ₜ|sᵢ,ₜ) / πold(aᵢ,ₜ|sᵢ,ₜ)

### 关键技术 3：代理分析（Surrogate Analysis）

- **理论问题**：轨迹分解后，组内样本不再是「同一 prompt 的不同回答」，而是基于不同局部状态的条件策略
- **核心证明**：在简化假设（同一任务的轨迹长度近似一致 Hᵢ ≈ H）下：
  - 均值奖励 μ ≈ Cγ · S（S 是轨迹级平均回报，Cγ 是时间折扣系数）
  - 分解后的优化目标仍保留了 GRPO 的核心相对策略优化信号
- **意义**：为轨迹分解的有效性提供了理论保障

### 技术细节

- **MDP 建模**：M = ⟨C, S, A, R, γ⟩
  - C：任务空间（kill zombie, mine gold ore 等）
  - S：状态空间（当前观测 + 短历史 + 任务指令）
  - A：动作空间（键盘/鼠标操作：KEYDOWN, MOUSE_MOVE 等）
  - R：稀疏可验证奖励（成功=1，失败=0）
- **模型**：7B 参数 VLM（基于 Qwen2.5-VL）
- **并行 rollout**：G 个并行环境同时采集轨迹

## 关键实验结果与数据

### 主实验（800+ Minecraft 任务）

**三类任务对比（成功率 ASR）**：

**Embodied 任务（导航/操控）**：
- GROW: 59.6%（128 步）
- 前最佳 Game-TARS: 50.4%（373 步）
- 提升 +9.2%，步数减少 66%

**GUI 任务（合成/冶炼）**：
- GROW: 68.4%（248 步）
- 前最佳 Game-TARS: 39.1%（406 步）
- 提升 +29.3%，步数减少 39%

**Combat 任务（战斗）**：
- GROW: 49.0%（172 步）
- 前最佳 MAIN-VLA: 39.2%（248 步）
- 提升 +9.8%，步数减少 31%

### 泛化能力（RL 未训练任务）

**RL-trained 任务**：
- Embodied: 35.0% → 90.0%
- GUI: 10.0% → 92.5%
- Combat: 45.0% → 85.0%

**RL-unseen 任务**（完全未见过）：
- Embodied: 41.9% → 59.2%
- GUI: 21.3% → 68.2%
- Combat: 19.8% → 47.5%

### 消融实验

**GROW vs PPO**：
- GROW 在所有任务类别上都优于 PPO
- 收敛更快，学习曲线更平滑
- 尤其在延迟奖励和多步交互任务上优势明显

**折扣因子 γ 的影响**：
- γ=0.9：性能较差（局部信号太强）
- γ=0.95：中等性能
- γ=0.995：最佳性能（保留长程信号）

### 行为级分析

三个诊断任务揭示了 GROW 学到的具体技能：
1. **稳定目标锁定**：挖黑曜石 63.3%（基线 0%）
2. **主动目标再捕获**：击杀视野外女巫 50.0%（基线 0%）
3. **抗干扰 GUI 操作**：在干扰项存在时合成蛋糕

## 创新点分析

1. **轨迹分解范式**：首次将 GRPO 的优化单元从「完整轨迹」改为「状态-动作样本」，同时保持相对策略优化信号
2. **代理分析**：提供了理论证明，即使分组样本基于不同局部状态，优化目标仍然有效
3. **统一框架**：同时支持 embodied 交互和 GUI 操作，验证了方法的通用性
4. **冷启动 + GRPO 精炼**：两阶段训练策略，先在状态-动作样本上冷启动，再通过 GRPO 精炼策略

## 局限性与未来方向

### 局限性
1. **原子任务为主**：当前 Agent 主要执行原子任务，缺乏记忆模块
2. **长序列任务不足**：需要记忆的长时序任务尚未探索
3. **环境限制**：依赖专有的高保真开放世界模拟器，扩展到更多环境受限

### 未来方向
1. **记忆模块**：探索在若干步后总结历史的策略
2. **更多环境**：扩展到更多可访问的环境，增加技能库
3. **长时序任务**：需要记忆和规划的复合任务

## 借鉴点

### 对 Hermes Agent 的启发
- **轨迹分解思想**：Hermes 的多轮对话场景可借鉴此方法，将长会话分解为独立的「状态-动作」单元进行训练，避免上下文溢出
- **GRPO 适配**：GROW 证明了 GRPO 可以通过简单改造适配多轮场景，Hermes 的 skill 选择策略可用类似方法优化
- **稀疏奖励 + 折扣传播**：任务完成/失败作为稀疏信号，通过折扣传播分配信用，适合 Hermes 的任务成功/失败反馈

### 对 Jetson Orin 边缘部署的启发
- **状态-动作建模**：分解后的样本上下文更短，推理成本更低，适合边缘部署
- **7B 模型**：在 Jetson Orin 上可推理的模型规模，验证了 VLM Agent 的边缘可行性

### 对量化交易的启发
- **轨迹分解 = 交易序列分解**：可将完整交易序列分解为独立决策点，用 RL 优化每个决策
- **相对优势**：跨 rollout 组的相对优势计算，类似于多策略回测中的相对排名

## 关联论文

1. **GRPO** — DeepSeek-R1 提出的 Group Relative Policy Optimization
2. **JARVIS-VLA** — Minecraft 中的 VLM Agent（分阶段训练）
3. **ROCKET-1/3** — 视觉-时序上下文提示 + 跨视角推理
4. **VPT** — Video Pre-Training，大规模视频预训练
5. **STEVE-1** — 文本到行为生成
6. **UI-TARS-1.5** — GUI Agent（同一团队的前作）
7. **Game-TARS** — 游戏 Agent，SFT 基线方法
8. **PPO** — 经典策略优化算法（对比基线）
9. **Qwen2.5-VL** — 底层 VLM 基座模型

## 引用

```bibtex
@article{wu2026grow,
  title={GROW: Aligning GRPO with State-Action Modeling for Open-World VLM Agents},
  author={Wu, Xiongbin and Luo, Zhihao and Lei, Shanzhe and Zhang, Lechao and Wang, Xuhong and Yang, Jie and Zheng, Zhonglong and Zheng, Yuanjie and Tan, Xin and Liu, Wei},
  journal={arXiv preprint arXiv:2605.20246},
  year={2026}
}
```

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
- [具身智能机器人2025十大趋势](../2026-05-18-具身智能机器人2025十大趋势.md)
- [Qwen3.7-Agent Frontier](../2026-05-21-Qwen3.7-Agent Frontier.md)
- [react-agent-llm-agentic-training-research](../2026-05-21-react-agent-llm-agentic-training-research.md)
- [Agent自我进化与学习系统-深度研究](../2026-05-22-Agent自我进化与学习系统-深度研究.md)
- [Hermes-Agent四层记忆架构深度分析](../2026-05-22-Hermes-Agent四层记忆架构深度分析.md)
- [OpenClaw日常聊天黑化Agent-ULSPB安全研究](../2026-05-22-OpenClaw日常聊天黑化Agent-ULSPB安全研究.md)
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
- [Agent自我进化-Reflexion-ReAct-元认知框架](2026-05-21-Agent自我进化-Reflexion-ReAct-元认知框架.md)
- [开源具身智能项目横评-LeRobot-OpenVLA-RT2](2026-05-21-开源具身智能项目横评-LeRobot-OpenVLA-RT2.md)
- [agent-capability-boundary-detection-20260518](agent-capability-boundary-detection-20260518.md)
- [agent-drift-stability-degradation-20260518](agent-drift-stability-degradation-20260518.md)
- [agent-stability-degradation-drift-detection](agent-stability-degradation-drift-detection.md)
- [tradingagents-cn-deep-20260520](tradingagents-cn-deep-20260520.md)
- [google-a2a-protocol-multi-agent-2026-05-19](../google-a2a-protocol-multi-agent-2026-05-19.md)
- [hermes-agent-arxiv-search](../hermes-agent-arxiv-search.md)
- [hermes-agent-源码拆解自我进化机制](../hermes-agent-源码拆解自我进化机制.md)
- [AI幻觉案例分析-Hermes-Agent不实报道](../hermes-agent/2026-04-19-AI幻觉案例分析-Hermes-Agent不实报道.md)
- [具身智能机器人2025年终盘点](../hermes-agent/2026-05-05-具身智能机器人2025年终盘点.md)
- [具身智能机器人2025-商业化元年](../hermes-agent/2026-05-09-具身智能机器人2025-商业化元年.md)
- [claude-learning-roadmap](../hermes-agent/2026-05-10-claude-learning-roadmap.md)
- [HTML的不合理有效性-Claude-Code-团队](../hermes-agent/2026-05-16-HTML的不合理有效性-Claude-Code-团队.md)
- [GenericAgent](../hermes-agent/GenericAgent.md)
- [llm-wiki-gbrain-agent-evolution_33aa818c](../llm-wiki-gbrain-agent-evolution_33aa818c.md)
- [skills-autonomous-ai-agents](../skills-autonomous-ai-agents.md)
- [竞品吸收笔记_GenericAgent](../竞品吸收笔记_GenericAgent.md)
