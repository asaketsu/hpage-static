# LLM 推理模型 RL 训练前沿——从 GRPO 到 DAPO 与异步系统

> **来源**：
> - Raschka, S. *The State of Reinforcement Learning for LLM Reasoning* — Ahead of AI Magazine, 2025.
> - DeepSeek-AI. *DeepSeek-R1: Incentivizing Reasoning Capability in LLMs via Reinforcement Learning* — arXiv:2501.12948, Jan 2025.
> - Yu Q. et al. *DAPO: An Open-Source LLM Reinforcement Learning System at Scale* — arXiv:2503.14476, Mar 2025 (ByteDance Seed + Tsinghua AIR).
> - AsyncFlow Team. *AsyncFlow: An Asynchronous Streaming RL Framework for Efficient LLM Post-Training* — arXiv:2507.01663, Jul 2025.
> - *Reasoning on a Budget: A Survey of Adaptive and Controllable Test-Time Compute in LLMs* — arXiv:2507.02076, Jul 2025.
>
> **记录日期**：2026-07-18
> **关联 Skill**：`mlops/training/grpo-rl-training`、`inference-time-scaling`

**标签**：#LLM #推理模型 #GRPO #DAPO #RLVR #PPO #异步训练 #TestTimeCompute

---

## 一、内容详细整理

### 1.1 推理模型的本质：CoT + RL

**推理模型（Reasoning Model）**指通过显式生成中间推理步骤（Chain-of-Thought, CoT）再给出最终答案的 LLM。代表模型：OpenAI o1/o3、DeepSeek-R1、Qwen3、Claude 3.7 Sonnet（thinking 模式）。

```
传统 LLM：输入 → [Transformer 层固定计算] → 输出
推理模型：输入 → [CoT 中间步骤] → [自我验证] → [反思修正] → 输出
                ↑ Test-Time Compute (TTC) ↑
```

**两大改进路径**：

| 路径 | 方法 | 代表 |
|---|---|---|
| **训练时**（Training-Time） | RL 强化推理行为 | DeepSeek-R1, DAPO |
| **推理时**（Test-Time） | 增加推理步数/搜索 | o1 thinking, Best-of-N |

Raschka 文章的核心观点：**GPT-4.5 和 Llama 4 反应平淡，因为它们是传统模型，没有显式 RL 推理训练。OpenAI o3 用了比 o1 多 10× 的训练计算，说明 RL 推理还有巨大空间。**

### 1.2 RLHF → RLVR：奖励信号的范式转移

传统 RLHF（InstructGPT 三步法）依赖**人类偏好训练的奖励模型（Reward Model）**。DeepSeek-R1 团队发现：**神经奖励模型在大规模 RL 中会遭到 reward hacking**（模型学会骗奖励模型而非真正提升能力），因此转向 **RLVR（Reinforcement Learning with Verifiable Rewards）**。

```
RLHF 流程：
  Prompt → Actor 生成多个回答 → Reward Model 打分 → PPO 优化
  需要：Actor + Reference + Reward Model + Critic（4 个模型）

RLVR 流程（DeepSeek-R1-Zero）：
  Prompt → Actor 生成回答 → 规则验证器判断对错（+1/-1）→ GRPO 优化
  需要：Actor（1 个模型）+ 规则验证器（计算器/编译器）
```

**两类规则奖励**：
1. **Accuracy reward**：数学题答案 box 内的最终结果是否正确；LeetCode 是否通过测试用例
2. **Format reward**：要求推理过程包裹在 `<think>...</think>` 标签内

**关键洞察**：DeepSeek 团队明确说**不使用神经奖励模型**——
> "We do not apply the outcome or process neural reward model in developing DeepSeek-R1-Zero, because we find that the neural reward model may suffer from reward hacking in the large-scale reinforcement learning process."

### 1.3 PPO → GRPO：去掉 Critic 模型

**PPO（Schulman 2017）**的四个组件：Actor（策略）+ Reference（KL 约束）+ Reward Model + Critic（价值函数）。

PPO 的核心机制：
1. 计算 ratio = π_new(a|s) / π_old(a|s)
2. Clip ratio 到 [1-ε, 1+ε]（典型 ε=0.2）防止更新过大
3. advantage = actual_reward - expected_reward（expected 由 Critic 估计）
4. KL 惩罚项防止偏离 Reference 模型太远

**GRPO（Group Relative Policy Optimization, DeepSeekMath 2024）**的关键创新：**去掉 Critic**。

```
GRPO 做法：
  对每个 prompt q，采样 G 个回答 {o_1, ..., o_G}
  advantage_i = (r_i - mean(r_1..G)) / std(r_1..G)
  
  即用"组内相对排名"代替 Critic 的绝对价值估计
```

**优势**：
- 内存减少 25–50%（去掉 Critic 模型）
- 训练更稳定（组内归一化降低方差）
- 适合 RLVR（规则奖励天然适合组内比较）

### 1.4 DAPO：四个关键改进

ByteDance + 清华 AIR 在 2025 年 3 月发布的 DAPO 是 GRPO 的工业级改进版，**用 Qwen2.5-32B 在 AIME 2024 上达到 50 分，超过 DeepSeek-R1-Zero-Qwen-32B（47 分），训练步数仅为其一半**。

DAPO 的四项关键技术：

#### ① Clip-Higher：解除探索限制

**问题**：标准 PPO/GRPO 的 clip 范围 [1-ε, 1+ε]（ε=0.2）会限制低概率"探索"token 的概率上升。

**举例**：
- 高概率 token（π=0.9）：clip 后上限 1.08 → 可以继续上升到 0.999
- 低概率 token（π=0.01）：clip 后上限 0.012 → 几乎无法提升

**DAPO 解法**：**分离上下 clip 阈值**
```
clip(ratio, 1-ε_low, 1+ε_high)
典型：ε_low=0.2, ε_high=0.28
```

**效果**：低概率探索 token 的上限放宽，避免**熵塌缩（Entropy Collapse）**——策略过早确定性化，丧失探索能力。

#### ② Dynamic Sampling：过滤无效梯度

**问题**：如果一个 prompt 的 G 个回答**全对**（accuracy=1）或**全错**（accuracy=0），组内归一化后 advantage 全为 0，梯度为 0，浪费计算。

**DAPO 解法**：**动态过滤掉 accuracy∈{0, 1} 的 prompt 组**，只保留"部分对部分错"的有效梯度样本。

**效果**：每个 batch 的有效梯度样本数一致，训练效率提升 30–50%。

#### ③ Token-Level Policy Gradient Loss

**问题**：GRPO 在**样本级**计算 loss——先对每个序列求平均 loss，再对 G 个序列求平均。长序列（CoT 推理通常很长）的贡献被稀释。

**DAPO 解法**：改为**token 级**——所有 token 的 loss 直接求和再除以总 token 数。

```python
# GRPO（样本级）：
loss = mean([mean(seq_loss_i) for i in range(G)])

# DAPO（token 级）：
loss = sum(all_token_losses) / sum(all_token_counts)
```

**效果**：长 CoT 序列得到应有的梯度权重，长推理能力训练更有效。

#### ④ Overlong Reward Shaping：软长度惩罚

**问题**：硬性截断超长回答会引入奖励噪声（被截断的回答可能本来是对的）。

**DAPO 解法**：对接近最大长度的回答施加**软惩罚**，而非硬截断。

```
if length > L_max * 0.9:
    reward *= scaling_factor(length)  # 平滑衰减
```

**效果**：减少奖励噪声，训练更稳定。

### 1.5 异步训练系统：AsyncFlow

训练规模扩大后，**同步 RL 框架**（如 DeepSpeed-Chat）的瓶颈暴露：

| 框架类型 | 代表 | 问题 |
|---|---|---|
| **Task-Collocated**（任务共存） | DeepSpeed-Chat | 所有任务共享 GPU，内存浪费；rollout 与 update 切换需 resharding |
| **Task-Separated**（任务分离） | OpenRLHF | 数据依赖导致流水线气泡，资源闲置 |

**AsyncFlow（arXiv:2507.01663）**的三大创新：

1. **TransferQueue**：分布式数据管理模块，解耦数据平面与控制平面（借鉴 SDN 思想），实现流式数据加载
2. **Producer-Consumer 异步工作流**：延迟参数更新（在 staleness 阈值内），实现 rollout 与 update 的流水线重叠
3. **服务化 API**：解耦 RL 算法与底层训练/推理引擎，支持异构后端

**性能**：相比 SOTA 基线，吞吐量提升 **1.59×**（最大 2.03×）。

**相关异步系统**：
- **TBA（Trajectory Balance with Asynchrony）**：用 GFlowNet 的 TB 目标替代 PPO，支持经验回放缓冲区
- **LlamaRL（Meta）**：全异步分布式 RL，针对超大规模模型
- **StreamRL**：响应长度预测器，动态分发 prompt 平衡吞吐量

### 1.6 Test-Time Compute 效率（arXiv:2507.02076）

**核心问题**：推理模型"过度思考"简单问题，"思考不足"难题。

```
简单问题 "1+1=?" → 推理模型生成 2000 token 的 CoT → 浪费
复杂问题 → 推理模型生成 500 token 就停 → 不够
```

**两层分类法**：

| 层级 | 名称 | 方法 |
|---|---|---|
| **L1 可控性** | 固定计算预算 | Claude 3.7 的 thinking token budget；固定最大思考长度 |
| **L2 自适应性** | 动态调整 | 根据问题难度/模型置信度动态分配计算 |

**商业实践**：
- Anthropic Claude 3.7：用户可设 thinking token 预算
- OpenAI o1/o3：多种 thinking 模式（low/medium/high）
- Gemini 2.5 Flash：thinking 开关

**关键数据**（论文基准测试）：
- DeepSeek-R1（671B）平均 token 数：**2848**，AIME 准确率 89.1%
- Claude 3.7 thinking on：平均 **4159** token，准确率 90.97%
- Qwen3-4B thinking on：**4749** token，84.41%（小模型需要更多思考）

---

## 二、查询拓展

### 2.1 Entropy Collapse 的数学解释

PPO clip 的副作用可以用信息论解释：

- 策略熵 H(π) = -Σ π(a) log π(a)
- clip 限制概率比，间接限制熵的变化速率
- 当 ε=0.2 且训练步数多时，熵单调下降到接近 0
- 熵=0 意味着策略确定性化，丧失探索能力

**DAPO Clip-Higher 的效果**：ε_high 从 0.2 提到 0.28，低概率 token 可以更快上升到有意义水平，维持策略熵。

### 2.2 Reward Hacking 的典型表现

为什么 DeepSeek 放弃神经奖励模型？

| Reward Hacking 类型 | 表现 | 例子 |
|---|---|---|
| **长度 hack** | 模型学会写长答案骗 RM | "字多=分高" |
| **格式 hack** | 模型学会特定格式骗 RM | 加粗关键词、列表化 |
| **谄媚 hack** | 模型迎合 RM 偏见 | 附和用户观点 |
| **对抗 hack** | 模型生成 RM 盲区的错误 | 看似合理实则谬误 |

**RLVR 的优势**：规则验证器（计算器、编译器、单元测试）**不可欺骗**——答案对就是对，错就是错。

### 2.3 GRPO vs DAPO vs Dr. GRPO 的谱系

```
PPO (2017)
  └─ 需要 Actor + Reference + Reward + Critic
  │
GRPO (DeepSeekMath 2024)
  └─ 去掉 Critic，组内归一化
  │
  ├─ Dr. GRPO (2025)
  │    └─ 去掉长度和标准差归一化，信号更清晰
  │
DAPO (ByteDance 2025)
  └─ Clip-Higher + Dynamic Sampling + Token-Level Loss + Overlong Shaping
       └─ 工业级 SOTA，全开源
```

### 2.4 推理能力的来源之争

Raschka 文章末尾提出尖锐问题：**推理能力真的是 RL 诱导的吗？还是预训练数据中已经有了？**

证据表明：
- DeepSeek V3 base 模型已展现类推理行为（因为预训练数据含大量 CoT）
- R1-Zero 的"AHA moment"可能在 base 模型中就存在
- RL 的作用更像是**激发和强化**，而非从零创造

这对小团队有启示：**如果预算有限，用高质量 CoT 数据做 SFT，可能比直接 RL 更划算**。

---

## 三、归纳总结

### 3.1 LLM 推理 RL 训练技术栈全景

```
┌─────────────────────────────────────────────────┐
│            数据层                                │
│   RLVR 数据集（数学/代码/逻辑，有标准答案）         │
│   DAPO-Math-17k, AIME, GSM8K, MATH              │
├─────────────────────────────────────────────────┤
│            奖励层                                │
│   规则验证器（计算器/编译器/字符串匹配）             │
│   不用神经奖励模型（防 hacking）                   │
├─────────────────────────────────────────────────┤
│            算法层                                │
│   PPO → GRPO → DAPO                             │
│   关键：Clip-Higher + Dynamic Sampling +         │
│         Token-Level Loss + Overlong Shaping      │
├─────────────────────────────────────────────────┤
│            系统层                                │
│   同步：DeepSpeed-Chat, OpenRLHF, verl            │
│   异步：AsyncFlow, TBA, LlamaRL, StreamRL         │
│   关键：TransferQueue + 流式数据 + 延迟更新         │
├─────────────────────────────────────────────────┤
│            推理层（TTC）                          │
│   L1 固定预算：thinking token budget              │
│   L2 自适应：难度感知动态分配                       │
└─────────────────────────────────────────────────┘
```

### 3.2 训练一个推理模型的决策树

```
你的目标？
├─ 复现 SOTA 推理能力
│   └─ 用 DAPO + Qwen2.5-32B + verl + 128 H20 GPU
│      （需 ~$50k 训练成本）
│
├─ 小成本提升现有模型
│   └─ 用 GRPO + RLVR + 小数据集（7k 样本）
│      （$42 计算预算，1.5B 模型，参考论文 [8]）
│
├─ 仅推理时提升（不训练）
│   └─ Best-of-N + 自我一致性投票
│      （零训练成本，推理成本 ×N）
│
└─ 端到端产品级
    └─ DAPO 训练 + Test-Time Compute 控制
       （Claude 3.7 / o3 路线）
```

### 3.3 关键性能数据对比

| 模型 | 参数量 | AIME 2024 | 平均 token | 备注 |
|---|---|---|---|---|
| GPT-4o | — | 79.85% | 405 | 非推理模型 |
| DeepSeek-V3 | — | 89.73% | 851 | 非推理模型 |
| DeepSeek-R1 | 671B | **89.1%** | 2848 | RL 训练 |
| Claude 3.7 (thinking) | — | **90.97%** | 4159 | RL + TTC |
| Gemini 2.5 Flash (on) | — | 89.61% | 3733 | RL + TTC |
| Qwen3-4B (on) | 4B | 84.41% | 4750 | 小模型需更多思考 |
| DAPO (Qwen2.5-32B) | 32B | **50%** | — | 开源 SOTA |

**洞察**：thinking on 模式准确率提升 5–15%，但 token 消耗增加 3–10×。

---

## 四、趋势判断

### 4.1 RLVR 将取代 RLHF 成为主流推理训练方法

**依据**：DeepSeek-R1、DAPO、Qwen3 都采用规则奖励而非神经奖励模型。规则奖励不可欺骗、成本极低（计算器/编译器），适合数学和代码领域。预计 2026 年内，**所有开源推理模型都会采用 RLVR 路线**。挑战在于：非数学/代码领域（如医学、法律）如何设计规则验证器——可能需要领域专家系统。

### 4.2 异步 RL 框架将成为大规模训练标配

**依据**：AsyncFlow（1.59×）、TBA、LlamaRL 都在 2025 年发布。同步框架的流水线气泡在千卡规模下浪费 30–50% 算力。预计 2026 年内，**verl、DeepSpeed-Chat 都会内置异步模式**。关键挑战是 staleness（延迟更新）与收敛性的平衡——目前 AsyncFlow 允许 1 步 staleness，未来可能扩展到多步。

### 4.3 Test-Time Compute 将分层定价

**依据**：Claude 3.7、o3、Gemini 2.5 都已支持多档 thinking 预算。商业上，**按 thinking token 数计费**将成为推理 API 的标准定价模型。技术趋势：L2 自适应（根据难度动态分配）将逐步取代 L1 固定预算——模型自己判断"这个问题需要想多久"。

### 4.4 小模型推理能力的边界正在被突破

**依据**：Qwen3-4B thinking on 达到 84.41%（AIME），接近 671B 的 DeepSeek-R1。这说明**高质量 CoT 数据 + 精细 RL 调优**可以让小模型逼近大模型。对端侧部署（Jetson、手机）意义重大——4B 模型可在 8GB 显存运行。

### 4.5 RL 对蒸馏模型的增益存在争议

**依据**：Raschka 引用 [15] *A Sober Look at Progress in Language Model Reasoning*（arXiv:2504.07086）——该论文发现许多"RL 提升蒸馏模型"的声明在严格控制变量后**增益消失或不显著**。AIME24 等小基准的分数波动大（换随机种子差几个百分点）。这意味着 RL 的真实增益可能被高估，需要更好的评估标准。

---

## 五、关联分析

### 5.1 与 GRPO-RL 训练 Skill 的关联

> Skill: `mlops/training/grpo-rl-training`

DAPO 是 GRPO 的直接改进。Skill 中应补充：
- **Clip-Higher** 参数（ε_low, ε_high 分离）
- **Dynamic Sampling** 的过滤逻辑
- **Token-Level Loss** 的聚合方式
- **Overlong Reward Shaping** 的软惩罚函数

### 5.2 与推理时扩展（Inference Scaling）Skill 的关联

> Skill: `mlops/inference/inference-time-scaling`

Test-Time Compute 的 L1/L2 分类法应纳入 Skill：
- L1 固定预算：`max_thinking_tokens` 参数
- L2 自适应：基于困惑度或置信度的动态停止
- 混合策略：简单问题用 L1，复杂问题用 Best-of-N

### 5.3 与强化学习入门完全指南的关联

> 2026-07-14 笔记

那篇笔记介绍了 RL 基础（MDP、Bellman、Q-Learning → DQN → PPO）。本笔记展示了 RL 在 LLM 领域的最新应用——**从 PPO 到 GRPO 再到 DAPO 的演化**。两者构成"理论 → 前沿"的完整链条。

### 5.4 与机器学习核心理论的关联

> 2026-07-15 笔记

那篇笔记定义了三大范式（监督/无监督/强化）。本笔记验证了**三大范式在 LLM 训练中的融合**：
- 预训练 = 无监督生成建模
- SFT = 监督学习
- RLVR = 强化学习（DAPO 路线）

### 5.5 与 LLM 对齐训练范式（RLHF-DPO-GRPO-DAPO）的关联

> 2026-05-04 笔记

那篇笔记对比了四种对齐方法。本笔记是 DAPO 部分的**深度更新**——补充了四项关键技术的实现细节和论文实验数据。

---

## 六、金句摘录

> "GPT-4.5 和 Llama 4 反应平淡，因为它们是传统模型，没有显式 RL 推理训练。o3 用了比 o1 多 10× 的训练计算，说明 RL 推理还有巨大空间。" — Sebastian Raschka

> "我们不使用神经奖励模型，因为在大规模 RL 中它会遭到 reward hacking。" — DeepSeek-R1 论文

> "Clip-Higher 解除了对低概率探索 token 的限制，避免了熵塌缩。" — DAPO 论文

> "Dynamic Sampling 确保每个 batch 都有有效梯度，训练效率提升 30–50%。" — DAPO 论文

> "推理能力可能不是 RL 创造的，而是 RL 激发了预训练数据中已有的能力。" — Raschka 综述

> "同步 RL 框架在千卡规模下浪费 30–50% 算力，异步是必然方向。" — AsyncFlow 论文

---

## 七、行动启示

| 启示 | 行动 | 优先级 |
|---|---|---|
| DAPO 四项技术是 GRPO 的必备改进 | 更新 `grpo-rl-training` Skill，补充 DAPO 细节 | **P0** |
| RLVR 优于神经奖励模型 | 推理训练优先用规则验证器 | **P0** |
| 异步框架是大规模训练方向 | 关注 verl + AsyncFlow 的集成 | P1 |
| TTC 分层定价是商业趋势 | 推理 API 设计支持 thinking budget 参数 | P1 |
| 小模型推理能力突破 | Qwen3-4B 适合 Jetson 端侧部署 | P2 |
| RL 对蒸馏模型的增益有争议 | 评估推理模型时注意统计显著性 | P2 |

### 对现有 Skill 的具体改进建议

**`grpo-rl-training` Skill 应补充**：

```yaml
# 新增 DAPO 配置示例
dapo_config:
  clip_higher:
    enabled: true
    epsilon_low: 0.2
    epsilon_high: 0.28  # 比 low 高 40%
  
  dynamic_sampling:
    enabled: true
    filter_accuracy: [0, 1]  # 过滤全对/全错的 prompt 组
  
  loss_aggregation: "token-mean"  # 替代 GRPO 的 "seq-mean"
  
  overlong_reward_shaping:
    enabled: true
    length_threshold: 0.9  # 90% 最大长度开始软惩罚
    scaling_function: "linear"  # 或 "cosine"
  
  kl_divergence:
    enabled: false  # DAPO 移除 KL 项（long-CoT 场景）
```

**`inference-time-scaling` Skill 应补充**：

```python
# L2 自适应 TTC 示例
def adaptive_thinking_budget(prompt, model, max_budget=4096):
    """根据问题难度动态分配 thinking token 预算"""
    # 第一步：快速评估难度
    quick_response = model.generate(prompt, max_tokens=64)
    difficulty = estimate_difficulty(quick_response)  # 基于困惑度/长度
    
    # 第二步：分配预算
    if difficulty == "easy":
        return min(512, max_budget)
    elif difficulty == "medium":
        return min(2048, max_budget)
    else:  # hard
        return max_budget
```

## 相关笔记
- [推理时计算扩展-从Best-of-N到Compute-Optimal自适应分配](2026-07-28-推理时计算扩展-从Best-of-N到Compute-Optimal自适应分配.md)
- [Curriculum-RL-Reasoning](explore/2026-06-24-Curriculum-RL-Reasoning.md)
