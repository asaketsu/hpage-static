#rl #entropy-collapse #reinforcement-learning #duck-pi5

# RL 熵坍缩修复三篇：Entropy-Preserving REPO/ADAPO 与 IPS-GRPO

## 内容整理

围绕一个核心问题：**为什么 policy gradient 训练中策略分布会不可逆地收窄（熵坍缩/模式坍缩），以及 2025-2026 年的三篇修复工作**。直接对应 DUCK-Pi_5 Transformer 试点"白训"（reward 123 但 action std 全塌 0.06~0.18，静态策略）的根因解释与下次训练修复方案。

### 论文一：Entropy-Preserving Reinforcement Learning（Petrenko et al., ICLR 2026, arXiv:2603.11682）

**核心定理（Theorem 1）**：policy gradient 更新后熵的期望变化：

```
ΔH ≈ -α · E[A(s,a) · L(s,a') · u(s,a)ᵀu(s,a')]
```

其中 `L(s,a) = logπ(a|s) - E[logπ]` 是均值中心化对数概率。熵变化由 **advantage 与 log-prob 的相关性**驱动：给高概率动作分配正 advantage → 分布锐化 → 熵降。这解释了"站着不动"陷阱——低能耗动作既是高概率动作又拿正 advantage（能量惩罚返还），相关性恒正，熵单调下滑。

**各算法的熵动力学**：
- PPO：多次 off-policy 重复更新**放大**熵坍缩；但 clipping 本身界定熵变化 `(1-ε_low)·H_old ≤ H_new ≤ (1+ε_high)·H_old`（Theorem 2）
- DAPO：非对称裁剪 `ε_low=0.2 < ε_high=0.28` → 允许更大概率上升、限制下降 → 隐式保熵
- GSPO：序列级裁剪（几何平均 ratio），短轨迹界更紧（<600 token 时比 DAPO 紧）
- RLOO：严格 on-policy 避免**放大**效应但根除不了底层动力学

**数值精度重磅发现（§4）**：BF16 cast 概率后计算 ratio 会产生**乘法向上偏差**（Theorem 3），效果等同 `ε_low > ε_high` 的反向非对称裁剪——**与 DAPO 保熵方向正好相反**，系统性压熵。修复：importance ratio 计算全程用全精度；FP16（尾数多 3 位）比 BF16 训练更稳。作者直言："某些已报告的熵坍缩现象可能是数值精度伪影而非算法本质属性"。

**REPO（Regulated Entropy Policy Optimization）**：直接修改 advantage 函数：

```
A_REPO(s,a) = A(s,a) - β_s · L(s,a)
```

- REPO-D（Decorrelate）：β ∝ -ΔH，精确抵消每步熵坍缩；几何解释是在 (logp, Adv) 空间旋转去相关
- REPO-R（Rescale，实用版）：`β = ζ·|A(s,a)|`，只需采样动作的 log-prob（零额外显存），等效于用 REINFORCE 成对采样估计的熵 bonus
- 自适应控制器：第 1 轮记录初始熵 H_init；每轮熵 < H_init 则 ζ×2，> H_init 则 ζ÷2；|ζ| 裁剪到 [1e-4, 0.05]（REPO-R）

**ADAPO（Adaptive Asymmetric Clipping）**：ε_low=0.2 固定，ε_high ∈ [0.2, 0.32] 自适应——熵低于初始 → ε_high×1.05（放宽熵增），高于 → ×0.95。

**实验结果（AppWorld，Qwen3-8B/32B）**：GRPO 训练中熵掉近 90%；数值修复后纯 on-policy RLOO 拿当时 SOTA：79% Test Normal / 71% Test Challenge（Qwen3-32B）；REPO-R/ADAPO 是最强 off-policy 方法，且顺序训练（先 AIME 后 AppWorld）时保留继续探索能力——熵坍缩的 checkpoint 已丧失可训练性。

**关键方法论**："it's not the destination, it's the journey"——训练**全程熵轨迹**比最终熵更能预测性能；熵轨迹前 90% 相同、只在末段分岔的运行，最终性能几乎无差。

### 论文二：Expected Return Causes Outcome-Level Mode Collapse（arXiv:2601.21669）

**最强结论（Theorem 3.1）**：softmax 参数化 + 梯度流下，任意两个终止 outcome 的概率比对数变化率：

```
d/dt log[p_i(t)/p_j(t)] = p_i(t)·a_i(t) − p_j(t)·a_j(t)
```

即使 reward 完全相等（a_i = a_j），初始概率稍高者的更新信号 g = p·a 更大 → log-ratio 线性增长 → 概率比指数发散 → **正反馈锁死到单一 outcome**。该坍缩**独立于探索策略、熵正则、KL 正则、优化算法**——只要目标还是 expected return，坍缩就结构性存在。"哪个 outcome 赢"由初始 p·a 决定，但"坍缩本身"不可避免。

**修复（IPS, Inverse Probability Scaling）**：把终止奖励除以该 outcome 的出现概率：

```
r̃(o) = r(o) / p_θ(o)    （p_θ 不回传梯度）
```

平稳分布变为 **reward-proportional**：`π*_i ∝ r_i`（而不是 winner-take-all）。落地为 IPS-GRPO：按组内终止 outcome 的经验频率缩放奖励，drop-in 修改、零辅助模型、兼容 PPO clipping 与 KL。在网格环境、HypoSpace 3D 重建、分子生成上一致减少坍缩且不降基线性能。

### 论文三（脉络补充）：KL-Regularized RL is Designed to Mode Collapse（GX-Chen 2025）等

Jean Kaddour 博客《Causes of entropy collapse》给出谱系：Cui 2025（熵机制）、DAPO（Yu 2025）、Yue 2025（RL 不提升超越基模的探索）、GX-Chen 2025（KL 正则天然推向坍缩）、Tajwar 2026（Maximum Likelihood RL）、Osband 2026（Delightful Policy Gradient）。观测信号：**pass@1 升而 pass@k 停滞 = 熵坍缩的典型指纹**。

## 查询拓展

- rsl_rl / Isaac Lab 中 init_noise_std 与 entropy_coef 的交互：高斯策略下 action std 塌缩与离散 token 熵坍缩同构，`log_std` 参数化下熵 bonus 梯度如何作用（待深挖 rsl_rl 源码的 distribution.log_prob 与 entropy 计算）
- DAPO 原论文（Yu et al. 2025）四个组件：clip-higher、dynamic sampling、token-level PG loss、overlong reward shaping——其中 clip-higher 即本文分析的 ε_high=0.28
- Tajwar 2026 Maximum Likelihood RL：先 SFT 到最优再 RL 是否能绕开坍缩（与"预校准基模熵掉更快"的 RLOO 结论有张力）
- GRPO std 归一化引入的 bias（Liu et al. 2025b）：`A_GRPO = (R - mean)/std` 的除以 std 在奖励全组相同时放大噪声梯度
- 连续控制领域对应物：SAC 的最大熵目标函数、learned std 与 tanh-squash 的熵修正

## 归纳总结

三篇论文收敛到同一个结论：**熵坍缩不是 bug 而是 expected return 目标的结构性质**，修复必须在学习信号层面动手，且按侵入度排序：

1. 监控层（零成本）：全程记录熵/action std 曲线，设早停门禁——DUCK-Pi_5 已用 astd<0.3 门禁事后止损，应前置为训练中断准则
2. 数值层（近零成本）：ratio/熵计算保全程全精度，小模型直接 FP32
3. 裁剪层（低成本）：非对称 clip（ε_high > ε_low）或 ADAPO 自适应
4. Advantage 层（中成本）：REPO 式 `A' = A - β·L` 修正 + 自适应 ζ 控制器
5. 目标层（高成本）：IPS 按频率缩放奖励，把 winner-take-all 改为 reward-proportional

对连续控制（DUCK-Pi_5 场景）的映射：高斯策略的 `log_std → -∞` 等价于 token 熵坍缩；能量惩罚使"站立"成为高概率×正 advantage 的锁定点，正是 Theorem 3.1 的概率乘子正反馈通道——仅加熵 bonus 只能延迟，改 advantage 或奖励结构才能根治。

## 趋势判断

- 熵监控正在从"事后诊断"变成 RL 训练管线的**一等公民指标**（与 loss/reward 并列的必看曲线），Petrenko 的 "journey not destination" 判据会成为标准实践
- 数值精度（BF16 ratio 偏差）的曝光意味着一批历史实验结论需要复核——"算法 A 比 B 更易坍缩"的对比若未控制精度变量则不可信
- 修复方向从启发式（熵 bonus、KL）转向**带理论保证的目标函数修正**（REPO 的去相关几何、IPS 的 reward-proportional 平稳分布），2026 年预计出现统一框架
- 机器人 RL 社区（rsl_rl/Isaac Lab 生态）尚未内置这些修复，迁移窗口期存在

## 关联分析

**与 DUCK-Pi_5 Transformer 白训的直接互证**：
- 症状同构：t2048 试点 reward 123 看似健康但 astd 全塌 0.06~0.18 = 熵坍缩的连续控制版本；"站着不动的低能耗解" = IPS 论文的 outcome-level mode collapse（多走路方式都可得高分，策略锁死在"站立"这一个 outcome）
- 三重根因叠加：①能量惩罚给"不动"持续正 advantage 且是高概率行为（Petrenko Corollary 1 的正相关通道）；②expected return 概率乘子正反馈（IPS Theorem 3.1）；③Transformer 窗口注意力对静态模式的自我确认
- 下次训练修复清单（按成本排序）：熵/astd 曲线前置监控 + 早停门禁；提高 entropy_coef 或 init_noise_std 并退火；非对称 clip 思路（若用 PPO 系）；REPO-R 简化版（在 rsl_rl 外挂包里改 advantage：减去 β·(logπ - mean_logπ) 项）；奖励结构加步态项打破"不动的局部最优"（见姊妹篇 STL 笔记）

**与 GRPO 优势估计缺陷谱系笔记（2026-09-06）互链**：GRPO std 归一化 bias（Liu 2025b）+ 熵坍缩机制（本文）构成 GRPO 系缺陷的两个面——信号尺度与信号多样性。

**与机器人走路训练 Transformer/MLP 等效性笔记（2026-09-07）互链**：等效性论证假设训练健康；熵坍缩是 Transformer RL 特有的失败模式之一（窗口注意力 + 噪声塌缩），等效性结论在坍缩场景下不成立。

## 拓展应用推荐

1. **DUCK-Pi_5 下次训练（P0）**：把 astd 监控从"训后推理诊断"升级为"训练中断 criterion"——每个 checkpoint 保存时同步记录 policy entropy 与 mean action std，低于阈值自动告警；这是三篇论文共同的最低成本最大收益项
2. **rsl_rl 外挂包扩展（P1）**：在 duck-p3-pilot 外挂包中实现 REPO-R 简化版（advantage 修正项），零侵入注入路径已有先例（resolve_callable）
3. **股票量化监控借鉴（P2）**：pass@1 升而 pass@k 停滞的"指纹检测"思想可迁移到策略信号监控——单标的胜率升而组合多样性降 = 策略过度拟合单一模式
4. **Hermes 自身（P3）**：论文的"熵轨迹比终点熵更重要"对 Agent skill 演化同样成立——skill 使用分布的多样性监控可防"工具收窄"

## 出处

- Entropy-Preserving Reinforcement Learning (Petrenko et al., ICLR 2026): https://arxiv.org/abs/2603.11682
- Expected Return Causes Outcome-Level Mode Collapse (arXiv:2601.21669): https://arxiv.org/html/2601.21669v1
- On-Policy Entropy Flow Optimization (arXiv:2605.11491): https://arxiv.org/html/2605.11491v1
- Jean Kaddour, Causes of entropy collapse: https://www.jeankaddour.com/blog/entropy_collapse
- Petrenko 推文串（REPO 几何解释）: https://x.com/petrenko_ai/status/2038714716550516767
- 关联：GRPO优势估计缺陷谱系笔记（2026-09-06，explore 目录）；机器人走路训练Transformer与MLP等效性笔记（2026-09-07）

## 指南分析

何时用哪层修复的决策指南：

- **训练早期（<500 iter）astd 即下滑** → 数值层检查 + 提高 entropy_coef/init_noise_std，多为 advantage 与 log-prob 正相关过强
- **训练中期缓慢塌缩** → 非对称 clip（ε_high 0.28 vs ε_low 0.2）或 ADAPO 自适应
- **reward 高但行为单一（局部最优锁定）** → 目标层动手：奖励结构加行为多样性项（步态/接触项），或 IPS 精神对高频 outcome 降权
- **顺序训练第二阶段性能崩** → 熵坍缩后遗症，checkpoint 已不可训练，需从熵健康的 ckpt 重启
- 监控铁律：熵/action std 曲线必须与 reward 曲线同图查看；任何"reward 升 + 熵单调降"的组合都应触发人工审查而非庆祝


## 相关笔记

- [步态奖励设计两篇：STL 时序逻辑规约](./2026-09-08-步态奖励设计两篇-STL时序逻辑与双足步态条件多阶段课程.md) — 同日姊妹篇：奖励结构层修复，本篇是探索分布层修复
- [GRPO 优势估计缺陷谱系](./explore/2026-09-06-GRPO优势估计缺陷谱系-SpuriousAdvantage与SignBalance修正全景.md) — GRPO 算法缺陷全景，本篇 IPS-GRPO 的谱系背景
- [机器人走路训练 Transformer 与 MLP 等效性深读](./2026-09-07-机器人走路训练Transformer与MLP等效性深读-2048envs如何追平4096envs的样本效率与在线系统辨识.md) — 熵坍缩直接解释该试点"白训"根因（action std 塌到 0.06~0.18）
- [Transformer 与 MLP 架构对比深度研究](./2026-09-07-Transformer与MLP架构对比深度研究-数学原理包含关系与从MLPMixer到MoE的演进路径.md) — 架构层理论背景
