# Hands-On Modern RL — 现代强化学习实战课程

- 📅 2026-05-04
- ⭐ 4/5 — 目前最系统的"经典RL→LLM后训练→Agentic RL"课程，实践优先设计优秀，但尚在快速迭代中
- 🏷️ #强化学习 #RLHF #DPO #GRPO #RLVR #AgenticRL #LLM对齐 #开源课程
- 📰 GitHub: walkinglabs/hands-on-modern-rl
- 🔗 https://github.com/walkinglabs/hands-on-modern-rl

## 摘要

Hands-On Modern RL 是由 WalkingLabs 团队开源的现代强化学习实战课程，采用"实践优先"教学路径：从CartPole第一行代码出发，经过MDP、DQN、PPO等经典理论，直达RLHF、DPO、GRPO、RLVR等LLM后训练前沿，最终覆盖Agentic RL和VLM强化学习。课程12章+4个附录，每章配有可运行代码和训练指标可视化。375 Stars，Python 95%，CC BY-NC-SA 4.0协议。2026年5月2日刚开源，目前快速迭代中。

## 核心内容

### 项目画像

| 维度 | 信息 |
|------|------|
| Stars | 375 |
| Forks | 17 |
| 语言 | Python 95% / JavaScript 4.9% / Shell 0.1% |
| 协议 | CC BY-NC-SA 4.0 |
| Commits | 202 |
| 定位 | 现代RL实战课程（经典→LLM→Agent全覆盖） |
| 一句话 | 从CartPole到RLHF到Agentic RL的完整学习路径，实践优先，代码可运行 |

### 四大模块课程体系

**第一部分：基础导论（Ch01-02）**
- Ch01 CartPole倒立摆：在真实环境中理解状态、动作、奖励、策略、价值、熵
- Ch02 DPO偏好微调：直接从偏好对齐切入，锚定LLM后训练动机
- 设计哲学：先跑代码看现象，再回溯数学结构

**第二部分：核心理论与方法（Ch03-07）**
- Ch03 MDP与价值函数：从老虎机到贝尔曼方程
- Ch04 Q-Learning与DQN：经验回放、目标网络、Double/Dueling/Rainbow
- Ch05 策略梯度与REINFORCE：直接优化策略，Baseline降方差
- Ch06 Actor-Critic：优势函数、TD误差、AlphaGo简单复现项目
- Ch07 PPO：截断机制、GAE、奖励模型，LunarLander实战

**第三部分：大模型RL（Ch08-10）**
- Ch08 RLHF全流程：SFT→RM→PPO-RLHF→评估→Reward Hacking识别
- Ch09 后训练对齐：DPO/IPO/KTO家族→GRPO组优势→DeepSeek-R1→RLVR可验证奖励
- Ch10 Agentic RL：多轮信用分配、工具调用、轨迹合成、Code Agent项目、Deep Research Agent项目

**第四部分：前沿与高级系统（Ch11-12）**
- Ch11 VLM强化学习：GRPO训练VLM、视觉奖励与幻觉、Open-R1/R1-V
- Ch12 未来趋势：具身智能、Model-Based RL、Self-Play、多智能体RL、离线RL

**附录**：训练调试指南、RL工程实践（Agent沙箱/Benchmark）、数学基础（线代/概率/优化/信息论）

### 课程六大特色

1. **代码逐行聚焦**：PPO、DPO、GRPO关键实现配有代码地图，公式落到可读代码
2. **训练指标可视化**：真实曲线+指标解释+失败信号，边跑实验边诊断
3. **LLM后训练流水线**：RLHF→DPO→GRPO→RLVR以流程、artifact、案例串联
4. **Agentic RL项目化**：从单工具调用到Deep Research复杂轨迹合成
5. **调试能力一等公民**：Reward Hacking、KL漂移、熵衰减、OOM视为核心内容
6. **实践优先路径**：先看代码和直观现象，再引入数学抽象

### 实验代码结构

| 领域 | 代码路径 | 代表实验 |
|------|----------|----------|
| 经典控制 | code/chapter01_cartpole/ | CartPole训练，PPO对比 |
| 偏好微调 | code/chapter02_dpo/ | DPO偏好数据生成+训练 |
| MDP与价值 | code/chapter03_mdp/ | 老虎机、网格世界、贝尔曼更新 |
| DQN | code/chapter04_dqn/ | 经验回放、Double DQN |
| 策略梯度 | code/chapter05_policy_gradient/ | REINFORCE、Baseline对比 |
| PPO | code/chapter07_ppo/ | LunarLander、GAE可视化 |
| RLHF | code/chapter08_rlhf/ | SFT+RM+PPO完整流程 |
| 对齐与RLVR | code/chapter09_alignment/ | DPO奖励、GRPO、可验证奖励 |
| Agentic | code/chapter10_agentic_rl/ | 工具调用智能体、轨迹合成 |
| VLM | code/chapter11_vlm_rl/ | 多模态模型强化学习 |

### 技术架构

- 文档：VitePress（JavaScript 4.9%），在线阅读 walkinglabs.github.io/hands-on-modern-rl
- 代码：Python 95%，PyTorch实现
- CI：GitHub Actions + Puppeteer静态Mermaid渲染
- 许可：CC BY-NC-SA 4.0（非商用-相同方式共享）

## 🔍 借鉴点

- **"实践优先"课程设计 → 知识传递方法论**：先跑代码看现象→再回溯数学。这比传统"先公式后代码"效率高得多。可用于 ~/uclaw/ 项目的文档编写和技术教程制作
- **Agentic RL工程化视角 → Agent系统设计**：Ch10的多轮信用分配（ORM vs PRM）、工具调用轨迹合成、Badcase分析，直接可复用到Hermes Agent的RL训练管线设计思考
- **训练调试指南（附录A）→ RL工程实践**：Reward Hacking、KL漂移、熵衰减等失败模式的系统化诊断。这套诊断框架可转化为skill，用于量化交易策略调参诊断
- **课程路线图管理 → 开源项目迭代节奏**：明确的里程碑（05-10正式版→05下旬RLVR→06 Agentic→07 VLM），可作为项目管理参考

## 🔗 关联性

- 关联已有笔记：[2026-05-04-AI投资8层框架v3.1深度解析](2026-05-04-AI投资8层框架v3.1深度解析.md) — RL是L7模型层的核心技术，DPO/GRPO/RLVR是当前LLM后训练主流方法
- 关联已有skill：grpo-rl-training — GRPO/RL微调实践，本课程Ch09的GRPO实践可直接补充skill中的理论知识
- 关联已有skill：fine-tuning-with-trl — TRL库实践，本课程Ch08-09的RLHF/DPO实验可参考
- 关联竞品：Spinning Up (OpenAI)、Deep RL Bootcamp、huggingface/rl-course — 本课程的优势在于覆盖LLM后训练和Agentic RL

## 💡 启发

- **"调试能力一等公民"理念**：在AI/RL领域，调参和诊断bug的能力比写代码更重要。课程把Reward Hacking、训练崩溃等视为核心内容而非补充，这种"工程直觉优先"的教学法值得推广到所有AI教学材料
- **从经典RL到LLM的桥梁缺失**：市场上大量"RLHF教程"和"DQN教程"，但几乎没有人把两者串联成完整路径。WalkingLabs填补了这个空白——Ch01的CartPole到Ch08的RLHF，本质上都是"环境→策略→奖励→更新"的同一套循环
- **CC BY-NC-SA的平衡**：非商用许可保护了课程内容的商业化空间，同时允许自由学习分享。对于知识型开源项目，这是比MIT/Apache更合适的选择

## 🔮 预判

- **短期（1-2月）**：课程快速迭代期，社区反馈涌入，Stars有望破2K。Ch01-07基础部分将趋于稳定
- **中期（3-6月）**：RLVR实战和Agentic RL项目交付后，将成为LLM后训练领域最完整的开源教材。可能被大学课程采纳
- **长期（6-12月）**：如果具身RL（Unity环境）按时交付，将覆盖从数字到物理的完整RL谱系。WalkingLabs可能成为RL教育领域的知名品牌

## 相关笔记
- [2026-05-04-AI投资8层框架v3.1深度解析](2026-05-04-AI投资8层框架v3.1深度解析.md) - AI产业链分层
- [2026-05-04-OpenDataLoader-PDF解析器深度分析](2026-05-04-OpenDataLoader-PDF解析器深度分析.md) - 开源项目分析
