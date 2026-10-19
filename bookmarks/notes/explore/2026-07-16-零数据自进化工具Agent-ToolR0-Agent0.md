# 零数据自进化工具 Agent：Tool-R0 与 Agent0 框架

> 论文 1：[Tool-R0 (arXiv:2602.21320)](https://arxiv.org/abs/2602.21320) — Self-Evolving LLM Agents for Tool-Learning from Zero Data
> 论文 2：[Agent0 (arXiv:2511.16043)](https://arxiv.org/abs/2511.16043) — Unleashing Self-Evolving Agents via Tool-Integrated Reasoning
> 综述：[Self-Improving AI Agents: The 2026 Guide](https://o-mega.ai/articles/self-improving-ai-agents-the-2026-guide)

## 核心结论

2026 年 AI Agent 领域最重要的范式转变：**从"人类标注数据训练工具使用"转向"Agent 通过自博弈 RL 零数据自主进化工具能力"**。Tool-R0 和 Agent0 代表了这一方向的两个里程碑工作，HyperAgents 则进一步实现了跨域元认知迁移。

---

## 1. 范式转变：为什么零数据自进化是关键

### 1.1 传统方法的瓶颈

| 传统范式 | 核心问题 |
|----------|----------|
| 人工标注工具调用数据 | 成本极高，无法覆盖长尾场景 |
| LLM 合成训练数据 | 冗余度高，不保证泛化，68× 过量 |
| 固定工具集微调 | 工具更新即过时，无法动态适应 |

### 1.2 自进化的经济逻辑

> 静态 Agent 是工具；每周提升 1% 的 Agent 是**增值资产**。一年后 68% 更强，两年后近 3 倍。

**可验证性约束**：自进化只在结果可客观验证的领域可靠（代码编译、数学证明、算法速度）。在营销文案等无清晰信号的领域容易 reward hacking。

## 2. Tool-R0：零数据工具调用自进化

### 2.1 架构：Generator-Solver 共进化

```
┌─────────────┐         ┌─────────────┐
│  Generator   │ ──────→ │   Solver     │
│  (出题者)    │  任务    │  (解题者)    │
│              │ ←────── │              │
│  在 Solver   │  奖励   │  使用真实    │
│  能力前沿    │         │  工具调用    │
│  生成挑战    │         │  解决任务    │
└─────────────┘         └─────────────┘
       ↑                        │
       └────── 共同进化 ────────┘
```

### 2.2 核心机制

- **互补奖励（Complementary Rewards）**：Generator 因提出 Solver 做不出的任务而受奖，Solver 因解决 Generator 提出的任务而受奖
- **零人数据假设**：两个 Agent 从同一 base LLM 初始化，完全通过自博弈 RL 进化
- **真实工具调用**：Solver 执行实际的工具 API 调用，非模拟
- **能力前沿探索**：Generator 自动定位 Solver 的"甜蜜区"——不太简单也不太难的任务

### 2.3 关键设计：避免退化循环

自博弈 RL 的经典风险是两个 Agent 串通退化（互相放水）。Tool-R0 通过互补奖励设计确保：
- Generator 不能提太简单的任务（Solver 会做，Generator 不得分）
- Solver 不能跳过工具（工具调用是奖励的必要条件）

## 3. Agent0：工具集成推理的全面框架

### 3.1 与 Tool-R0 的异同

| 维度 | Tool-R0 | Agent0 |
|------|---------|--------|
| 侧重点 | 工具调用能力 | 推理能力 + 工具集成 |
| Agent 角色 | Generator + Solver | Curriculum Agent + Executor |
| 基座模型 | 通用 LLM | Qwen3-8B-Base |
| 成果 | 工具调用 benchmark | 数学推理 +18%，通用推理 +24% |
| 代码开源 | 待确认 | ✅ [github.com/aiming-lab/Agent0](https://github.com/aiming-lab/Agent0) |

### 3.2 Agent0 的创新

- **工具感知课程（Tool-Aware Curriculum）**：Curriculum Agent 不仅出题，还会考虑 Executor 有哪些工具可用，设计需要特定工具组合的任务
- **多步共进化（Multi-step Co-evolution）**：超越单轮交互，支持多步推理链的任务进化
- **共生竞争（Symbiotic Competition）**：两个 Agent 的提升相互驱动，形成正反馈循环

## 4. HyperAgents：元认知自我修改的突破

### 4.1 关键结果

HyperAgents（Meta/UBC/Oxford/NYU, 2026-03）实现了**跨域自我改进策略迁移**：
- 在机器人控制、论文评审中学到的自我修改策略
- 迁移到全新领域（奥林匹克数学评分）
- 得分 **imp@50 = 0.630**，而人类专家手工设计系统得分 **0.0**

### 4.2 技术本质

一个 Python 程序包含两个函数：
- `solve_task()` — 执行领域任务
- `modify_self()` — **可以修改自身代码**的自我改进函数

> 这是从"恒温器"到"工程师"的跨越：恒温器按固定规则调节温度，工程师可以改变规则本身。

## 5. METR 时间线数据：Agent 自主任务时长

| 时间 | 50% 可靠性时长 | 倍增周期 |
|------|---------------|----------|
| 2024 | <15 分钟 | 每 7 个月翻倍 |
| 2025 末 | ~50 分钟 | **加速至每 4 个月翻倍** |
| 2026 预测 | 2-4 小时 | 曲线未趋平 |

R² = 0.98 的指数增长趋势。

## 6. 对我们 Hermes 系统的启示

### 6.1 可直接借鉴的模式

| 模式 | Hermes 对应 | 改进方向 |
|------|------------|----------|
| Generator-Solver 共进化 | evolver + skill-stress-test | 可引入"自博弈"出题机制，Skill 自动生成测试用例 |
| 工具感知课程 | auto-skill + auto-learner | 让 auto-learner 考虑已有 Skill 组合，设计需要协作的任务 |
| 元认知自我修改 | skill_manage(patch) | `modify_self()` 模式已在 skill 系统中部分实现 |
| 可验证性约束 | requesting-code-review | 退出码 = 0 是验证信号；非代码任务需额外设计 |

### 6.2 具体改进建议

1. **引入自博弈 Skill 压测**：让一个 Agent 生成"困难任务"测试另一个 Agent 的 Skill 覆盖率，形成共进化
2. **Tool-Aware 选题**：夜间自学习选题时，考虑当前 Skill 库的覆盖盲区，针对性学习
3. **可验证性优先**：自进化 cron 应聚焦有明确成功信号的任务（代码编译、测试通过、API 返回 200），而非主观质量判断

### 6.3 风险警示

- **Reward Hacking**：在无清晰验证信号的领域（内容质量、用户体验），自进化容易优化代理指标而非真实价值
- **退化循环**：两个自博弈 Agent 可能串通退化，需互补奖励设计 + 外部基准周期性校准

---

## 参考链接

- Tool-R0：https://arxiv.org/abs/2602.21320
- Agent0：https://arxiv.org/abs/2511.16043 | 代码：https://github.com/aiming-lab/Agent0
- HyperAgents：https://arxiv.org/abs/2603.19461
- 自进化 Agent 2026 综述：https://o-mega.ai/articles/self-improving-ai-agents-the-2026-guide
- TT-SI 测试时自改进：https://arxiv.org/abs/2510.07841
- METR Agent 时间线：https://metr.org/blog/2026-1-29-time-horizon-1-1/

*学习日期：2026-07-16 | 来源：夜间自学习 cron*

## 相关笔记

- [SPyCE技能策略协同进化](./2026-07-16-SPyCE技能策略协同进化.md) — 技能-策略协同进化Agent框架
- [AI Agent自进化架构2026全景](./2026-06-28-AI-Agent自进化架构2026全景-WhatWhenHow三维框架.md) — 自进化架构全景综述
