# 后训练技术：拒绝采样 —— 从 RAFT 到 Reinforce-Rej 的谱系

> 探索日期 2026-08-16 | 兴趣等级 L3 | 来源 2 篇深度 + 1 代码库 | 前序笔记：`notes/2026-07-18-LLM推理模型RL训练前沿-从GRPO到DAPO与异步系统.md`、`notes/2026-08-02-LLM后训练RL框架2026全景-slime-Miles-verl-vime生态.md`

---

## 摘要

拒绝采样（Rejection Sampling, RS）是后训练中被使用最广却文档最少的方法：**采样多个候选回答 → 用奖励模型/验证器过滤 → 只在优质样本上做 SFT**。本文增量补充现有 GRPO/DAPO 笔记未覆盖的谱系：RAFT（纯 RS 基线）→ RAFT++（+重要性采样与 clip）→ Reinforce-Rej（过滤全对全错）→ GRPO（组内归一化隐式实现了同样的过滤）→ DAPO 动态采样（重采样替换无效组）。核心结论：**GRPO 相对简单 RS 的优势主要来自"丢弃全错 prompt 组"，而非奖励归一化本身**——这重塑了对 RL 训练本质的理解。

## 关键发现（4 个）

### 1. RS 是"计算统计学"思想的迁移，流水线只有 4 步

源自 Gilks & Wild 1992 的自适应拒绝采样：无法直接从复杂分布采样时，从简单分布采样 + 启发式过滤。LLM 场景映射：

```
目标分布   = 高质量回答
采样分布   = 当前模型 πθ
过滤器     = 奖励模型 RM 或可验证奖励 (verifier)
```

四步流水线（rlhfbook Ch.9）：
1. 选 prompt（通常复用 SFT/IFT 集，注意过拟合风险）
2. 从待优化 checkpoint 生成 N 个候选（temperature 0.7–1.0，每 prompt 10–30+ 个）
3. RM 打分排序，两种选择策略（见下）
4. 在选中样本上做标准指令微调

**选择策略对比**：
- **Top per prompt**：每个 prompt 取 argmax reward，保证覆盖均衡
- **Top-K overall**：全局取 K 个最高分对，`argsort(R_flat)[-K:]`，可能集中在少数 prompt 上
- 单 prompt Best-of-N 场景下两者等价（K=1 时退化）

**历史地位**：WebGPT、Anthropic HH (Helpful and Harmless)、OpenAI PRM 论文（Let's Verify Step by Step）、Llama 2 Chat 全部以 RS 为核心组件；RAFT (Dong et al. 2023) 将其形式化到多模态对齐，RSO (Liu et al. 2024) 给出与其他偏好学习目标的原则性统一。

### 2. 惊人实证：纯 RAFT 基线可打平 GRPO/PPO（arXiv 2504.11343）

RLHFlow 团队的消融研究：
- **RAFT（只在正奖励样本上 SFT）性能与 GRPO、PPO 相当**
- 分解 GRPO 组件后发现：其优势主要来自**隐式丢弃"全错"prompt 组**（组内全错 → 归一化后 advantage 无梯度信号），而非 reward normalization 本身
- 据此提出 **Reinforce-Rej**：极简策略梯度扩展，**同时过滤全错与全对样本**（全对组 advantage 恒零，同样无学习信号），KL 效率与稳定性优于 GRPO/PPO，已发布 Qwen2.5-Math-7B-Zero-Reinforce-Rej 模型

> 与 DAPO 动态采样的关系（作者亲自回应社区提问）：DAPO dynamic sampling 是**重采样新数据替换**无效组；Reinforce-Rej 是**直接置零 advantage 跳过**。两者本质同源（都源于 GRPO 的 mean-zero 隐式过滤），可组合使用。这条问答直接打通了本文与 7-18 DAPO 笔记的知识链。

### 3. RAFT++ = 拒绝采样 + 重要性采样 + clip（RLHFlow/Minimal-RL）

Minimal-RL 仓库将 RAFT 定位为"LLM 后训练最基础的 RL 算法"，并给出增强变体：

```
RAFT:    只取正样本 → SFT（离线，无 off-policy 校正）
RAFT++:  在 RAFT 上加 importance sampling ratio + clipping
         st(θ) = πθ(at|x) / πold(at|x)   ← 与 GRPO 的 token 级 ratio 同构
```

谱系一图流：

```
SFT → RAFT(纯RS, 只学正样本)
        ↓ +重要性采样+clip
      RAFT++（接近离线策略梯度）
        ↓ +过滤全对全错
      Reinforce-Rej（极简在线 RL）
        ↓ +组内归一化(隐式过滤)
      GRPO（DeepSeek-R1 同款）
        ↓ +动态重采样+解耦clip
      DAPO（工业级，见 7-18 笔记）
```

关键洞察：**这条谱系不是算法更替，而是"如何处理负样本"的渐进设计**。RAFT 丢弃负样本；GRPO 用负样本做 baseline 但隐式丢弃无效组；论文主张未来方向是"更原则性的负样本利用"而非无差别使用。

### 4. RS 与 Best-of-N 是训练时/推理时的对偶

- **Best-of-N**：同样的 generate-and-score，但**不训练**，推理时选最优（"Pro" 档模型常用，额外算力换更好回答）
- **RS/RAFT**：把 BoN 的选出的优质样本**沉淀回模型权重**
- BoN 是评估 RLHF 训练方法的合法 baseline（模型不变，仍可测 KL 距离）
- 实操细节：batch RM 推理时按 completion 长度排序组 batch，减少 padding，吞吐显著提升

## 与现有工作的关联（增量定位）

**P1 — 补全后训练技术栈拼图**：现有笔记覆盖了 SFT→DPO→GRPO/RLVR 主线（7-18 训练范式笔记）与 DAPO 四改进（7-18 RL前沿笔记），但缺失"GRPO 之前的简单方法为什么也有效"。本笔记的谱系分析填补该空白，且 Reinforce-Rej ↔ DAPO dynamic sampling 的同源性问答是两篇笔记间的关键交叉链接。

**P1 — Jetson 端侧/小模型的实操启示**：RAFT 不需要 critic、不需要复杂 RL 基础设施，仅需"生成 + 验证 + SFT"循环。对于 LFM2.5 端侧 Agent 模型（8-08 笔记）的持续训练场景，RAFT 是算力受限下的首选基线——用 TRL 的 `RejectionSamplerTrainer` 或 Minimal-RL 代码库即可启动。

**P2 — 对 self-evolution 闭环的方法论输入**：Hermes 的 evolver/skill-stress-test 机制本质是"生成变体 → 验证 → 保留优质"，与 RS 同构。Reinforce-Rej 的发现提示：**验证信号二元化（全对/全错）的样本对进化无增益，应聚焦"部分成功"的边界样本**——这直接适用于 skill A/B 测试的样本筛选策略。

## Actionable Insights

1. **实验入口**：`github.com/RLHFlow/Minimal-RL`（RAFT/RAFT++/Reinforce-Rej/GRPO 四算法统一实现）+ rlhfbook 配套 `code/rejection_sampling/`（GSM8K 完整管线，含 random control 对照）
2. **匹配对照实验设计**：rlhfbook 的 treatment/control 配对法（top_per_prompt vs random_per_prompt）可直接迁移到 skill 有效性验证——"奖励选择的样本没跑赢随机基线 = 信号无用"
3. **超参速记**：temperature 0.7–1.0；每 prompt 采样 10–30+；太少则训练有偏/噪声大
4. **RL 不收敛时降级路径**：GRPO 训练不稳定时先退回 RAFT 验证奖励信号质量，再逐步加组件（与"先跑通再优化"原则一致）

## 关键风险与盲点

- **RS 偏向简单任务**（emergentmind 综述指出 oversampling simpler tasks 风险）：正样本天然集中在模型已会的简单题，长尾难题持续无梯度——与 DAPO 动态采样要解决的是同一个问题（官方论文验证 ✅）
- **奖励模型质量决定上限**：RM 打分无信号时 RS 退化为随机 SFT（rlhfbook 强调用 random control 检测，官方建议 ✅）
- **Reinforce-Rej 的负样本丢弃策略仍有争议**：论文自己承认"无差别使用负样本"不可取，但"原则性利用"的方案尚未收敛（社区讨论，未定论 ⚠️）
- **异构模型生成**（多模型产候选）的最佳实践未建立（官方文档确认空白 ⚠️）

## 一页速查

> **拒绝采样 = 生成 N 候选 → RM/verifier 过滤 → 优质样本 SFT**。
> 四步：选prompt → 采样(0.7–1.0温度, 10–30个/prompt) → 选择(top-per-prompt 或 top-K overall) → SFT。
> 谱系：RAFT → RAFT++(+IS+clip) → Reinforce-Rej(滤全对全错) → GRPO(组归一化隐式过滤) → DAPO(重采样)。
> 核心实证：纯 RAFT ≈ GRPO/PPO；GRPO 优势主来自丢弃全错组而非归一化。
> BoN = 推理时版 RS（不训练）；RS = 把 BoN 结果写进权重。
> 降级路径：RL 不稳 → 先 RAFT 验证奖励信号。

## 待深入

- RSO (Statistical Rejection Sampling Optimization) 与 DPO 的数学关系（Liu et al. ICLR 2024）
- ReST-EM (Google 自我蒸馏迭代版 RS) 在 Agent 场景的应用
- 负样本的原则性利用：对比学习式 reward shaping vs 简单丢弃

## 来源

1. Lambert, N. *RLHF Book* Ch.9 Rejection Sampling — rlhfbook.com/c/09-rejection-sampling（2026 Manning 出版配套在线版）
2. Liu, Z. et al. *A Minimalist Approach to LLM Reasoning: from Rejection Sampling to Reinforce* — arXiv:2504.11343 + HuggingFace 论文页作者问答
3. RLHFlow/Minimal-RL 代码库 — github.com/RLHFlow/Minimal-RL（RAFT++/Reinforce-Rej 官方实现）

## 相关笔记

- [LLM推理模型RL训练前沿-从GRPO到DAPO](../../notes/2026-07-18-LLM推理模型RL训练前沿-从GRPO到DAPO与异步系统.md) — RL训练前沿全景
- [LLM后训练RL框架2026全景](../../notes/2026-08-02-LLM后训练RL框架2026全景-slime-Miles-verl-vime生态.md) — RL框架生态
- [SkillShapley技能归因估值](./2026-08-17-SkillShapley技能步骤归因估值.md) — Agent训练环节归因
- [CodeAct范式与沙箱逃逸](./2026-08-17-codeact-paradigm-sandbox-escape.md) — Agent训练到执行
- [OPS-D自蒸馏思考时间计算](../../explore/2026-08-09-opsd-on-policy-self-distillation-overthinking-test-time-compute-2026.md) — 推理阶段优化
