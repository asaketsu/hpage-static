# Hands-On Modern RL — 从经典控制到 LLM 对齐、RLVR 和 Agentic 系统的实战课程

> **来源**：[github.com/walkinglabs/hands-on-modern-rl](https://github.com/walkinglabs/hands-on-modern-rl)
> **在线课程**：[walkinglabs.github.io/hands-on-modern-rl](https://walkinglabs.github.io/hands-on-modern-rl/)
> **License**：CC BY-NC-SA 4.0
> **Stars**：3,485 · **Forks**：258 · **语言**：Python
> **创建日期**：2026-04-10 · **最后更新**：2026-08-07（活跃开发）
> **标签**：RL、RLHF、DPO、GRPO、LLM Alignment、Agentic RL、PyTorch

---

## 一句话定义

> 3.5K Stars 的开源强化学习实战教程——从 CartPole/DQN/PPO 经典控制，一路到 RLHF/DPO/GRPO/RLVR 的 LLM 后训练，再到 Agentic RL（代码智能体/浏览器/Computer Use）和多模态 VLA 模型。**29 章 + 4 个附录**，每一章都有可运行实验代码。

---

## 内容整理

### 课程结构（7 大部分，29 章）

| Part | 主题 | 章节 | 核心 |
|------|------|------|------|
| **序章** | 导论 | RL 发展史、环境配置 | — |
| **Part I** | 基础与经典 RL | Ch 1-4 | CartPole、MDP、贝尔曼方程、DP/MC/TD |
| **Part II** | 深度强化学习 | Ch 5-9 | DQN、策略梯度、Actor-Critic、PPO、SAC、AlphaZero |
| **Part III** | 高级 RL 方法 | Ch 10-12 | 离线 RL（Decision Transformer）、模仿学习、多智能体、分层 RL |
| **Part IV** | **LLM 对齐与后训练** | Ch 13-19 | **RLHF、DPO、GRPO、RLVR、PRM、推理模型、Constitutional AI** |
| **Part V** | **Agentic RL** | Ch 20-23 | **工具调用 RL、代码智能体（SWE-RL）、浏览器/GUI Agent** |
| **Part VI** | **多模态 RL** | Ch 24-27 | **VLM RL、音频 RL、VLA 具身智能、视觉生成 RL** |
| **Part VII** | 安全、评估与前沿 | Ch 28-29 | **奖励黑客、自我博弈、RL Scaling Laws** |

### Part IV: LLM 对齐与后训练（最核心部分）

#### Ch 13: RLHF 训练流水线

- 基座模型到指令对齐
- SFT 指令微调
- Bradley-Terry 奖励模型
- RL 微调流程
- 大规模训练工程
- 评测方法
- **veRL PPO 训练 GSM8K**（可运行实验）

#### Ch 14: 大模型 RL 工业实战

- 训练框架对比与双轨奖励
- 现代后训练流水线范式
- 优化器与训练稳定性
- 分布式同步/异步与 **MoE 训练**

#### Ch 15: 偏好对齐与 DPO 家族

- DPO 推导
- DPO 训练指标
- DPO 原理、数学与家族选型

#### Ch 16: GRPO、RLVR 与 Verifier 工程

- **GRPO 核心机制**
- **R1-Zero 范式 / DAPO**
- **RLVR 可验证奖励**
- GRPO 改进家族
- RL Environments 与 **Verifier 工程**
- **金融 API 工具调用 GRPO 实验**
- OPD 在线蒸馏
- veRL 代码生成 RL 实验

#### Ch 17: 推理模型与 Test-Time Scaling

- 推理模型的兴起
- R1-Zero 纯 RL 训练
- Test-time Compute Scaling
- **Hybrid Thinking 思考预算**
- 自适应思考
- 推理链的可读性与对齐

#### Ch 18: 过程奖励模型（PRM）与推理时搜索

- Outcome vs Process 奖励
- 判别式 PRM 路线
- 生成式 PRM 路线
- 形式化 PRM Verifier
- **推理时搜索**
- 并行协调推理总结

#### Ch 19: Constitutional AI 与 RLAIF

- HHH 原则 Claude 实践
- RLAIF 工程化宪法扩展

### Part V: Agentic 强化学习（最新前沿）

#### Ch 20: 工具调用、多轮交互与多智能体 RL

- Agentic RL 总览
- 多轮 RL 形式化
- **轨迹信用分配**
- **工具调用 RL**
- **Search-Augmented RL**
- **Code Interpreter RL 工业实战**
- **多智能体协作与 Agent Swarm**

#### Ch 21: 代码智能体强化学习

- **SWE-RL 基础实验**
- **Code World Model 与 DeepSWE**
- Self-Play SWE-RL 总结

#### Ch 22: Deep Research 与浏览器智能体

- 浏览器 RL harness 工程
- 评测基准与开源项目

#### Ch 23: Computer Use 与 GUI Agent

- **GUI Agent 训练实践**
- **指令层级 Prompt Injection 防御**

### Part VI: 多模态强化学习

#### Ch 24: 视觉语言模型 RL

- 视觉奖励挑战
- 视觉反思 RL
- 中国多模态前沿
- **GeoQA 几何推理实验**

#### Ch 26: 具身智能与 VLA 模型

- VLA（Vision-Language-Action）模型的 RL 训练

#### Ch 27: 视觉生成 RL

- DanceGRPO
- 多奖励视频 RLHF 与物理感知生成

### Part VII: 安全、评估与研究前沿

#### Ch 28: 奖励黑客与 RL 评估

- **经典失败模式**
- **RLVR 假性收益与工业失败案例**
- Anthropic 失准研究
- 防御机制总结
- 评估原则与现代评估 Harness

#### Ch 29: 自我博弈、规模化与未来方向

- 自我博弈基础与 **LLM 自我博弈**
- **RL Scaling Laws**
- In-Context RL 与未来十年
- **进化式 LLM 搜索与科学发现**

### 附录（4 个）

| 附录 | 内容 |
|------|------|
| **A. 训练调试与工程实践** | 训练调试指南、训练系统底座、Agent 沙箱、评测基准 |
| **B. 核心算法实现** | SFT/KL、PPO/GAE、DPO 家族、GRPO/奖励模型、Softmax/交叉熵、采样方法、注意力机制、DAPO |
| **C. 学习资源与参考资料** | 论文阅读路线图、GPU 小时估算表、训练指标词典、工业实战练习 |
| **D. 数学基础** | 线性代数（贝尔曼矩阵/收敛/信任域）、概率（回报/价值/采样/GAE）、微积分（策略梯度/PPO/Adam）、信息论（熵/交叉熵/KL/RLHF/DPO） |

### 实验代码（部分）

| 章节 | 实验 | 文件 |
|------|------|------|
| Ch 1 | CartPole PPO 训练 | `1-ppo_cartpole.py`, `2-pytorch_ppo.py` |
| Ch 3 | 贝尔曼方程验证、GridWorld Q-Learning | `bellman_equation_verify.py` |
| Ch 4 | DQN（CartPole/Atari/LunarLander/宝可梦红） | `dqn_atari_sb3.py`, `dqn_pokemon_red_pyboy.py` |
| Ch 5 | REINFORCE + Actor-Critic | `reinforce_cartpole.py`, `actor_critic_cartpole.py` |
| Ch 7 | PPO 从零实现 + GAE 可视化 | `ppo_from_scratch.py`, `gae_visualization.py` |
| Ch 8 | RLHF 全流程 | `sft_pipeline.py`, `reward_model_training.py`, `rlhf_ppo_train.py` |
| Ch 8 | veRL GSM8K 奖励 | `gsm8k_reward.py` |
| Ch 9 | DPO 实操 | `dpo_hands_on.py`, `dpo_math_reward.py` |
| Ch 9 | PPO/TD3/SAC 对比 | `ppo_td3_sac_comparison.py` |
| 附录 | 奖励黑客调试 | `debug_reward_hacking.py` |
| 附录 | 训练崩溃调试 | `debug_training_collapse.py` |

### 课程特色

| 特色 | 说明 |
|------|------|
| **逐行代码聚焦** | 关键 PPO/DPO/GRPO 实现包含代码地图，公式与可读代码一一对应 |
| **训练指标可视化** | 真实曲线 + 指标解释 + 失败信号，边跑实验边调试 |
| **LLM 后训练流水线** | RLHF/DPO/GRPO/RLVR 通过流程图、工件和案例串联 |
| **Agentic RL 实验** | DeepCoder 风格 GRPO 训练曲线连接工具使用、响应长度和奖励动态 |
| **中英双语** | 完整中文版 + 英文版 |

---

## 查询拓展

- veRL 框架的 PPO 训练 GSM8K 实验的具体配置和 GPU 需求？
- GRPO 在金融 API 工具调用场景的奖励函数设计？
- SWE-RL 和 DeepSWE 的 Code World Model 架构？
- 浏览器 RL harness 的工程实现细节？
- VLA 模型的 RL 训练（Ch 26）具体涉及哪些模型（OpenVLA/RT-2/Gemini-Robotics）？
- 奖励黑客的工业失败案例（Ch 28）有哪些具体例子？
- RL Scaling Laws（Ch 29）与预训练 Scaling Laws 的关系？
- 进化式 LLM 搜索与科学发现（Ch 29.4）的前沿进展？

---

## 归纳总结

这是目前**最完整的现代强化学习开源教程**——从 1991 年的 MDP 到 2026 年的 GRPO + Agentic RL，29 章覆盖了整个 RL 领域。最大的价值在于**把经典 RL 和 LLM 后训练打通**——学习者可以沿着同一条路径从 CartPole → DQN → PPO → RLHF → DPO → GRPO → RLVR → Agentic RL → VLA 一路走到前沿。

三个最值得关注的部分：
1. **Part IV（LLM 对齐与后训练）**：RLHF/DPO/GRPO/RLVR/PRM/推理模型——这是当前最重要的 AI 工程能力
2. **Part V（Agentic RL）**：工具调用 RL、代码智能体、浏览器/GUI Agent——这是 Agent 的 RL 训练前沿
3. **Ch 28（奖励黑客与评估）**：失败模式 + 工业案例 + 防御机制——这是"验证是最终瓶颈"的 RL 版

---

## 结合最新研究与技术变化

### 1. 与自进化四波浪潮笔记的直接关联

Ch 28（奖励黑客与评估）直接回应了"验证是自进化最终瓶颈"的论点。RLVR 的"可验证奖励"正是用程序化验证替代模型互评——与 SkillOpt 的 validation gate 和 Prime Agent 的 `/refine` 证据门禁同源。

### 2. 与 LLM 微调成本工程笔记的关联

Ch 13-14（RLHF/GRPO 工业实战）是微调笔记中"FermiSense 用 GRPO 做 3.5 天 $500 后训练"的理论基础。GRPO 正在取代传统 SFT 成为窄领域任务后训练的主流方法。

### 3. 与 Coding Agent Harness 解剖学笔记的关联

Ch 20-21（Agentic RL / 代码智能体 RL）——用 RL 训练 Coding Agent 是 Mastra Harness 的下一阶段。SWE-RL 和 DeepSWE 把软件工程任务建模为 RL 环境，Agent 通过试错学习编码策略。

### 4. 与具身智能方向的关联

Ch 26（VLA 模型 RL）直接对应用户的研究方向——用 RL 训练 Vision-Language-Action 模型做机器人控制。这是 Gemini-Robotics / OpenVLA / ActionHead 等前沿工作的训练方法。

### 5. 与量化交易方向的关联

Ch 16 的"金融 API 工具调用 GRPO 实验"直接关联用户的量化交易策略——用 GRPO 训练 LLM 自主调用金融 API 做交易决策。

### 6. 2026 最新技术覆盖

课程覆盖了几乎所有 2025-2026 最新技术：
- **GRPO + RLVR**（DeepSeek R1 范式）
- **DAPO**（GRPO 改进）
- **推理模型 Test-Time Scaling**
- **Hybrid Thinking 思考预算**
- **Agentic RL**（SWE-RL/DeepSWE/浏览器 Agent/GUI Agent）
- **多模态 RL**（VLA/DanceGRPO）
- **自我博弈 + RL Scaling Laws**

---

## 学习进化借鉴点

| 章节/概念 | 可借鉴到 | 说明 |
|----------|---------|------|
| **Ch 16 GRPO + RLVR** | Hermes Skill 优化 | RLVR 的"可验证奖励"可以用于 SkillOpt 的 validation gate——把 Skill 质量验证做成 RL reward |
| **Ch 17 Test-Time Scaling** | Agent 推理预算 | Hybrid Thinking 的思考预算可以用于 Hermes 的模型路由（简单任务少想，复杂任务多想） |
| **Ch 20 Agentic RL** | Hermes Agent 训练 | 工具调用 RL = 让 Agent 通过试错学习何时调用什么工具 |
| **Ch 28 奖励黑客** | Agent 评估 | 经典失败模式 + 工业案例 = Hermes 质量评估的检查清单 |
| **Ch 29 自我博弈** | 自进化系统 | LLM 自我博弈 = 自进化系统的 RL 实现路径 |
| **附录 B 算法实现** | 代码参考 | PPO/DPO/GRPO 从零实现的代码可以直接参考 |

---

## 趋势判断

- **RL 是连接 LLM 和物理世界的桥梁**——从文本对齐（RLHF）到工具使用（Agentic RL）到物理控制（VLA），RL 正在成为 AI 的通用训练框架
- **GRPO + RLVR 取代纯 SFT 成为主流后训练**——DeepSeek R1 验证了"纯 RL + 可验证奖励"可以训练推理能力
- **Agentic RL 是下一个爆发点**——代码智能体（SWE-RL）、浏览器 Agent、GUI Agent 都在用 RL 训练，而非纯 SFT
- **奖励黑客是 RL 的核心风险**——Ch 28 的"RLVR 假性收益"说明验证器本身可能被模型 exploit
- **多模态 RL（VLA）将定义具身智能的下一阶段**——把语言模型的推理能力通过 RL 注入到机器人控制中
- **RL 教程正在从"学术"走向"工程"**——这门课程包含了 GPU 小时估算、训练框架对比、工业失败案例等实用内容

---

## 关联分析

- **与 grpo-rl-training Skill 的直接关联**：用户的 `grpo-rl-training` Skill 是 GRPO/RL 训练的专家指导，这门课程是系统学习路径
- **与 inference-time-scaling Skill 的关联**：Ch 17（推理模型与 Test-Time Scaling）是该 Skill 的理论扩展
- **与 agent-orchestration-pattern Skill 的关联**：Ch 20（多智能体协作与 Agent Swarm）是 Agent 编排的 RL 训练方法
- **与 embodied-ai-control Skill 的关联**：Ch 26（VLA 模型 RL）是具身智能控制的 RL 训练
- **与 quant-trading 方向的关联**：Ch 16 的金融 API 工具调用 GRPO 实验直接关联量化交易
- **与自进化四波浪潮/SkillOpt/Prime Agent 的关联**：Ch 28（奖励黑客）+ Ch 29（自我博弈）= 自进化系统的 RL 理论基础

---

## 📎 关键链接

- 💻 GitHub（3.5K⭐）：[github.com/walkinglabs/hands-on-modern-rl](https://github.com/walkinglabs/hands-on-modern-rl)
- 📖 在线课程：[walkinglabs.github.io/hands-on-modern-rl](https://walkinglabs.github.io/hands-on-modern-rl/)
- 📄 PDF 下载：[Releases 页面](https://github.com/walkinglabs/hands-on-modern-rl/releases/latest)
- 💬 微信交流群：见 README 中二维码

---

*笔记创建：2026-08-07 · 来源：walkinglabs/hands-on-modern-rl*

## 相关笔记

- [AI for Physics 全景图](./2026-08-07-AI-for-Physics全景图-五条路线与AI落点分析.md) — 物理AI研究路线，RL 是控制层核心
- [基于ADAMS的机器人动力学可靠性](./2026-08-07-基于ADAMS的具身机器人动力学可靠性分析.md) — 动力学仿真+RL控制理论交叉
- [深入理解 AI Agent](./2026-08-07-深入理解AIAgent-设计原理与工程实践-10章92实验.md) — Agent=LLM+上下文+工具，RL对齐是核心章节
- [LLM 推理加速-推测解码](./explore/2026-08-04-推测解码2026-SSD并行化与EAGLE3实战.md) — 推测解码与RL训练优化的推理侧互补
