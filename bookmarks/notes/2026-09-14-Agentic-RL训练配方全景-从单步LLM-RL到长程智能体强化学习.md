#AI-Agent #强化学习 #LLM #自进化

# Agentic RL 训练配方全景：从单步 LLM-RL 到长程智能体强化学习

> 2026-09-14 夜间学习 | 桥接用户两条主线（DUCK 足式 RL + Hermes Agent 自进化）。论文计划候选方向：训练配方与课程的跨域统一性。

## 内容整理

### 1. 两大 2026 综述确立领域框架

**《The Landscape of Agentic RL for LLMs》**（arXiv 2509.02547，TMLR 已发表，500+ 文献）：

- 核心范式转移论断：传统 LLM-RL 是**退化单步 MDP**（一条 prompt→一条回复即一个 episode），Agentic RL 是**时间延展的 POMDP**——LLM 从被动序列生成器变成嵌在动态环境中的自主决策者。
- 双分类法：按能力（规划/推理/工具使用/记忆/自我改进/感知）× 按应用（代码/数学/GUI/视觉具身/多智能体）。
- 关键论断：传统 agent 依赖 MCTS 等外部算法做规划，Agentic RL 的目标是**把这些能力内化进 LLM 策略本身**——训练出"先思考再行动"的快慢双系统。
- 开放挑战：可信任性、训练规模化、**环境规模化**（环境比模型更是瓶颈）。

**《Training Recipes for Agentic RL in LLMs》**（TechRxiv 2026，GitHub blacksnail789521/Agentic-RL-Training-Recipes，45 star）：

- 工程师视角的配方库，三大板块：Training Schemes（训练方案）/ Training Infrastructure（训练基础设施）/ Training Environments（训练环境+基准）。
- 每篇论文一条 TLDR + 组件分类，是快速选型的索引表。

### 2. 四大组件族的代表性配方（从 GitHub 配方表提炼）

**Rollout 与数据策略**：
| 方法 | 核心思想 |
|---|---|
| ReST (2023) | 迭代自改进：生成→过滤高质量轨迹→再训练 |
| GRPO (DeepSeekMath 2024) | 组相对策略优化，组内采样比优势，去掉 value head |
| Down-sampling Rollouts (2504.13818) | 不是所有 rollout 都有用，下采样省算力 |
| Lookahead Tree Rollouts (2510.24302) | 高不确定步骤分支展开，轨迹级探索 |
| Reverse Curriculum (2402.05808) | 从"接近目标"反向倒推起点，解决稀疏奖励冷启动 |
| VCRL (2509.19803) | 用组奖励**方差**选中难度任务——太大太难、太小太易 |
| RLVE (2511.07317) | 按当前 agent 表现动态生成任务（自适应可验证环境） |

**反馈与信用分配**：
- Process vs Outcome 之争是主线：Search-R1 精确匹配结果奖励 / StepSearch 步级 PPO / VinePPO rollout 分支统计信用 / GRPO-λ 无 value head 的细粒度更新 / Group-in-Group 两层分组（任务内步+任务间）。
- Reflexion（2023）是"语言强化学习"鼻祖：用自然语言自我反思替代标量奖励。

**训练时记忆**（与我们 Agent 记忆研究直接相关）：
- MemLLM：微调 LLM 执行显式 read/write API；Memory-R1：用 PPO/GRPO 训练专门的**记忆管理 agent**；MEM1：RLVR 把上下文压缩到常数足迹；MemAgent：流式文档多轮 RL。
- 趋势：记忆从"外挂检索"走向"训练内化的读写策略"。

**训练基础设施**：
- 异步系统（AReaL/LlamaRL）+ 陈旧性校正（V-trace/AIPO）；FP8/FP4 训练；**训练-推理失配**（training-inference mismatch）被单列为独立失效模式——MiniMax-M1 用 FP32 输出头修熵坍缩，DeepSeek-V3.2 用 off-policy 序列掩码。

### 3. Multi-turn 的两大哲学（Medium 综述 + NeurIPS 实践指南）

- **哲学一：轨迹级 MDP**——整个多轮交互当一个不断增长的 token 序列，一条轨迹一个回报（GRPO 系）。
- **哲学二：步级 MDP**（Agent-R1，USTC 开源，1.4k star）——每步交互是一等公民 RL transition，有自己的 state/action/observation，dense per-turn reward + token 级信用分配。
- NeurIPS 2025 实践指南三支柱实验：**环境、策略先验、奖励**对 multi-turn RL 的影响——sparse vs dense per-turn 奖励对比是核心结论来源；模型先验（SFT 起点）显著影响后续 RL 上限。

## 归纳总结

1. **范式定位论**：Agentic RL = 把"推理时工程"（MCTS/反思/记忆检索）通过训练内化为策略权重。训练一次，推理时不再付外挂算力成本。
2. **配方的两大轴**：时间轴（outcome↔process 奖励光谱）× 空间轴（轨迹级↔步级 MDP 建模）。选配方=在这两轴上定位你的任务。
3. **环境是新瓶颈**：两篇综述都把"环境规模化"列为开放挑战——RLVE/VCRL 这类"按 agent 水平动态生成任务"的课程方法，本质是把 locomotion 的 curriculum learning 思想搬到了语言 agent。
4. **与我们自进化体系的映射**：Hermes 的 evolver/error-case-library/reflexion 式反思全是推理时外挂，Agentic RL 指出了"内化"这条路——但成本是训练，对小团队仍是研究性选项。

## 关联分析

**与 DUCK RL 训练的跨域同构**（本文最有价值的观察）：

| Agentic RL 概念 | DUCK/PPO 训练对应物 |
|---|---|
| Reverse Curriculum（从近目标倒推） | prone ramp 1500-2500 从浅趴到 45% 深趴 |
| VCRL 方差选任务 | fell_over 500 放闸后"摔倒中探索"——都是控难度分布 |
| Dense per-turn reward | velstand 的 com_upward dense 项 |
| 稀疏 outcome reward | recovery 终点悬赏×10（v6 卡平台根因） |
| 训练-推理失配 | BAM 软件栈训练 vs XML 原生执行器 kp 差 300 倍的演示瘫软问题 |
| 环境规模化瓶颈 | 地形课程扩展（mujoco-scene-design） |

两边独立演化出同构解法（课程控难度、dense 化奖励、执行器建模对齐），**"课程学习是跨域通用武器"** 这个命题有双重实证——这是论文计划的现成选题素材。

**与 Agent 记忆技能簇的关联**：Memory-R1 的"专门记忆管理 agent"与我们的 memorygraph/hybrid-search 架构同型（管理器与主推理分离），差异在我们用启发式规则、他们用 RL 训练管理策略。

## 趋势判断

- 2025→2026 明显信号：**multi-turn RL 从研究走向工程化**（verl/AgentGym-RL/RAGEN 等开源栈成熟），RL for agents 工作坊进入 Hugging Face 主流课程。
- Ragen-2（2604.06268）提出 agentic RL 的"推理坍缩"失效模式——agent RL 不是万能药，有自己的病。
- 步级 MDP 派（Agent-R1）在长程任务上开始胜出轨迹级派，dense per-turn 奖励成为默认选择。
- GLM-5.2（即当前会话模型）被该领域文献列为"Built for Long-Horizon Tasks"的代表——模型层已在为 agentic RL 优化。

## 查询拓展

- Ragen-2 的"reasoning collapse"具体机制（与我们的 skill 退化/僵尸化是否同构）
- RLVE 的任务生成器实现（能否对接 Hermes 的 sniff-interests 队列做"自适应学习难度"）
- AgentGym-RL 的 horizon 扩展调度（greedy→exploratory）参数表
- VCRL 方差阈值与 DUCK prone ramp 百分比的换算关系

## 指南分析

对 Hermes 自进化架构的可执行建议：

1. **P2 级参考**（不建议现在动）：Memory-R1 式"RL 训练记忆管理策略"对我们成本过高，当前 hybrid-search 启发式已够用；但 error-case-library 的"案例匹配"可借鉴其"读记忆要学"思想——在 auto-learner 触发时先查案例库再搜索（已有此逻辑，维持）。
2. **立即采纳的索引**：Training Recipes GitHub 表作为论文选型速查表——写周论文若选 agentic RL 方向，从该表的"组件空格"找novelty 缺口（如：训练环境的 benchmark 表中 GUI+中文场景仍是空白）。
3. **论文选题落地**：《课程学习的跨域统一性：从足式机器人 PPO 到 LLM Agent RL 的同构课程机制》——素材已双备（DUCK v6/v7 放闸课程数据 + 本笔记配方表），新颖性判断：现有综述均按域分类，未见跨域同构性分析。

## 拓展应用推荐

- **直接应用**：Training Recipes 表作为周论文选题的"空白扫描器"（每周扫一次新增条目）。
- **迁移应用**：VCRL 方差选难度的思想可用于 auto-learner 的领域等级探索——嗅探队列按"预期学习增益方差"排序而非先进先出。
- **skill 沉淀**：本笔记的跨域同构表可补进 `agentic-alpha-research` 或新建 `agentic-rl-recipes` 索引 skill；Agent-R1/RAGEN-2 加入 auto-learner 嗅探候选词。

## 出处

- The Landscape of Agentic Reinforcement Learning for LLMs: A Survey — https://arxiv.org/abs/2509.02547（TMLR 2026，Oxford/SJTU/NUS 等 20+ 机构）
- Training Recipes for Agentic Reinforcement Learning in LLMs: A Survey — TechRxiv 2026，GitHub: https://github.com/blacksnail789521/Agentic-RL-Training-Recipes
- RL for LLMs in 2026: From PPO to DPO to GRPO to Multi-Agent RL — https://shivu-agr.medium.com/rl-for-llms-in-2026-from-ppo-to-dpo-to-grpo-to-multi-agent-rl-1c00e1dacba7
- A Practitioner's Guide to Multi-turn Agentic Reinforcement Learning — NeurIPS 2025，https://neurips.cc/virtual/2025/127960
- Agentic RL: Frameworks and Best Practices — cameronrwolfe.substack.com/p/agentic-rl
- HF RL for Agents Workshop (2026-04)：https://www.youtube.com/watch?v=cixmqTsi2A4


## 相关笔记

- [周综合-Harness工程之年-W37](./2026-09-14-周综合-Harness工程之年-W37.md) — 同周全景与上下文
- [足式机器人跌倒爬起策略](./2026-09-14-足式机器人跌倒爬起策略-从稀疏奖励到两阶段范式.md) — 课程与reward设计同源
- [RTR机器人训练机器人](./2026-09-13-RTR机器人训练机器人-机械臂教师真机RL与动力学潜变量微调全拆解.md) — 真机RL配方对照
- [扩散策略RL微调与ADEPT地形生成](./2026-09-12-扩散策略RL微调与ADEPT地形生成.md) — 课程化训练近亲
