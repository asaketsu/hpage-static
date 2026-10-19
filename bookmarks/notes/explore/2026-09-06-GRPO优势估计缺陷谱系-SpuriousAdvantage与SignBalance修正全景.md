# GRPO 优势估计缺陷谱系 — Spurious Advantage、SignBalance 与 Dr.GRPO/DAPO 修正全景

#GRPO #RLVR #SpuriousAdvantage #SignBalance #DrGRPO #DAPO #优势估计 #强化学习 #LLM训练 #arXiv精读

## 出处

- 主论文：arXiv 2609.04063《Spurious Advantage Hidden in GRPO》（Jiamian Wang, Samyadeep Basu, Koustava Goswami et al.），2026-09
- 综述底稿：Cameron R. Wolfe《GRPO++: Tricks for Making RL Actually Work》（Deep Learning Focus newsletter，2026-01），覆盖 DAPO (arXiv 2503.14476)、Dr.GRPO (arXiv 2503.20783)、Off-Policy 引擎差异 (Feng Yao)
- 关联论文：arXiv 2601.08521《Your Group-Relative Advantage Is Biased》、arXiv 2506.10947《Spurious Rewards: Rethinking Training Signals in RLVR》
- 笔记日期：2026-09-06（夜间自学习）

## 一、内容详细整理

### 1.1 GRPO 优势估计器的数学骨架（理解一切缺陷的地基）

GRPO 对每个问题 q 采样 G 条 rollout，二元验证奖励 rᵢ∈{+1,−1}，组内标准化得优势：

$$\hat{A}_i = \frac{r_i - \mu}{\sigma + \varepsilon}$$

代入二元奖励的 μ=(n⁺−n⁻)/G、σ=2√(n⁺n⁻)/G，闭式化简为（Mroueh 2025 并行推导）：

$$\hat{A}^+ = \sqrt{n^-/n^+}, \qquad \hat{A}^- = -\sqrt{n^+/n^-}$$

**关键观察：per-rollout 幅值完全由组内组成 (n⁺,n⁻) 决定——rollout 的内容、策略对该问题的置信度都不进入公式。** 这是所有后续缺陷的总根源。

### 1.2 缺陷一：Spurious Advantage——"猜对也得高分"（arXiv 2609.04063 核心）

**放大机制**：G=16 时，稀有正确组（n⁺=1）给唯一正确的 rollout 幅值 |Â⁺|=√15≈3.87，平衡组（n⁺=8）只给 1——**同为 +1 奖励，梯度权重差 3.87 倍**。且 PPO clip 只约束重要性比 w_{i,t}，不约束 |Âᵢ|；首个 inner update 时 w≈1，放大效应全额进入梯度。

**猜测成分分解**：把成功概率按来源拆开：

$$p_q = \underbrace{p_r}_{推理答对} + \underbrace{(1-p_r)\cdot p_g}_{非推理（猜）答对}$$

组内计数 n⁺~Binomial(G, p_q) 同时继承两个来源。稀有正确组的"大推力"里混着 p_g 驱动的分量——**策略被推向模仿幸运猜测而非推理**。

**三种成灾场景**（p_g 不小时）：

| 场景 | 猜中概率 p_g | 说明 |
|------|-------------|------|
| ① 有界答案任务 | k 选项多选 ≈1/k；4 选 G=16 时期望 4 条纯靠猜答对 | 猜的 rollout 和推理答对的拿同样幅值 |
| ② 开放答案集藏有界子集 | 见下表 MATH-7.5K 分析 | 名义开放 ≠ 真开放 |
| ③ 多轮搜索 Agent | 预算 B 内 (Tᵢ,aᵢ) 路径空间大，冗余/无效搜索也能撞对终点 | outcome-only reward 不看路径质量 |

**MATH-7.5K 答案形态实测**（论文 Table 1，55.95% 属有界形态）：

| 答案类别 | 占比 | 猜中率 p_g | 有界 |
|---------|------|-----------|------|
| int_small [-10,10] | 24.41% | 4.76% | ✓ |
| int_medium [-100,100] | 22.99% | 0.50% | ✓ |
| expression | 20.87% | 0% | – |
| int_large | 16.30% | 0% | – |
| simple_fraction | 7.51% | 1.00% | ✓ |
| finite_set_listed | 0.62% | **20.00%** | ✓ |
| percent | 0.42% | 0.99% | ✓ |

### 1.3 SignBalance 修正：三步剥离猜测成分

| 步骤 | 做法 | 消除的依赖 | 残留问题 |
|------|------|-----------|---------|
| 1. per-class 归一化 | 正确/错误子组各自标准化 | 不平衡组里正确 rollout 不再对着一堆错误做缩放 | σ⁺ 仍依赖 n⁺ |
| 2. sign-only 幅值 | Â=sign(rᵢ)·c，全局常数 c | 幅值与 (n⁺,n⁻) 彻底解耦 | 破坏批级零均值（正负力不等） |
| 3. 力平衡恢复 | **Â⁺=c，Â⁻=−c·sg[n⁺/n⁻]**（stop-gradient） | 恢复 Σ⁺|Â|=Σ⁻|Â| 零均值 | ——（最终形态） |

**性质**：参数免费（除全局 c）、PPO-style surrogate 不变、无外部模型、零推理成本、drop-in 替换式 (1)。

**实验**（Qwen2.5-0.5B-IT 主线 + 3B 泛化 + 7B 搜索 Agent，G=16，MATH 训练，lr 1e-6，KL β=1e-3，≤1000 步）：

| 方法 | GSM8K | MATH-500 | MMLU-m | SAT-M | AQuA | AMC | Avg-8 |
|------|-------|----------|--------|-------|------|-----|-------|
| GRPO | 49.89 | 56.60 | 52.94 | 65.62 | 29.53 | 6.02 | 34.24 |
| Dr.GRPO | 48.90 | 55.60 | 52.27 | 68.75 | 25.98 | 7.23 | 34.23 |
| DAPO | 48.82 | 55.40 | 55.88 | 71.88 | 36.22 | 7.23 | 36.27 |
| **SignBalance** | 49.66 | 53.60 | 54.14 | 71.88 | 35.43 | **10.84** | **36.61** |

开放答案（GSM8K/MATH-500）持平，**有界答案（AMC 6.02→10.84 近翻倍）和搜索 Agent 提升显著**——正好印证缺陷定位。

### 1.4 缺陷二/三：Dr.GRPO 揭示的长度偏差与难度偏差（arXiv 2503.20783）

| 偏差 | 机制 | 后果 |
|------|------|------|
| 响应级长度偏差 | 按序列 token 数归一化损失 | advantage<0 时长回答惩罚被稀释→**错误答案越写越长**（"过度思考"假象，reward 平台期后长度仍在涨） |
| 问题级难度偏差 | 分母 σ 在全对/全错组爆炸或退化 | 太易/太难问题获得异常大梯度 |

**Dr.GRPO 两改**：① 损失除以固定常数 MAX_TOKENS 而非序列长度；② 去掉分母 σ 项。Qwen2.5-Math-7B 达 AIME 2024 43.3%（该规模 SOTA），**更少 token 更好表现**，8×A100 仅 27 小时。

### 1.5 DAPO 四件套（arXiv 2503.14476，字节+清华）

1. **Clip Higher**：ε_low=0.2 / ε_high=0.28 解耦——原对称 clip 压制低概率探索 token 上升空间（0.01×1.2=0.012 vs 0.9×1.2 可到 1.08），熵崩塌的根源
2. **Dynamic Sampling**：过采样+过滤全对组（全对组梯度为零，白白缩水有效 batch）
3. **Token-level loss**：全 batch token 平均，消除长样本稀释（与 Dr.GRPO ①同源）
4. **Overlong reward shaping**：软惩罚区间 [L_max−L_cache, L_max]（16K/4K），替代一刀切负奖励——"推理对但太长"不应与"胡说"同罚

**战果**：Qwen-2.5-32B RL-Zero AIME 0%→50%（DeepSeek-R1 报告 47%，vanilla GRPO 仅 30%），训练步数减半。

### 1.6 缺陷四：引擎鸿沟导致的隐性 Off-Policy（Feng Yao）

sampler（vLLM/低精度推理）与 learner（FSDP/DeepSpeed）两引擎即使参数完全相同，**token 概率也有实质差异**——名义 on-policy 实际 off-policy。修法：截断重要性采样 TIS，策略梯度乘 capped importance ratio π_learner/π_sampler。工程法（逐一对齐实现）只能缩小无法根除（推理本身非确定）。

### 1.7 RL 训练健康监控四指标（DAPO 实践）

| 指标 | 健康形态 | 异常信号 |
|------|---------|---------|
| 响应长度 | 随长 CoT 能力形成缓增 | 停滞/下降；reward 平台期后仍涨=长度偏差 |
| 训练 reward | 稳定上升 | 噪声混沌、大幅波动 |
| 策略熵 | 合理区间，缓慢上行有利 | 崩塌=探索死亡；过高=输出乱码 |
| Held-out 评测 | 与训练 reward 同步 | 背离=reward hacking/过拟合训练集 |

另有数据侧两常识：batch 不能小（Olmo 3 用 512 batch / 64 prompts / 8 rollouts）；**易猜问题（多选类）直接从训练集移除**是常见做法——与 SignBalance 的诊断互为印证。

## 二、查询拓展

- SignBalance 的 stop-gradient 力平衡在 G 值小（如 4-8）时是否稳定
- 组成依赖幅值 ω⁺(p)=√((1−p)/p) 的自适应加权在开放答案上是"特性"（稀有推理轨迹获大权重，Mroueh 论点）——SignBalance 把这个特性也一起扔了，开放任务持平是否恰好说明特性不重要
- Dr.GRPO 去 σ 与 SignBalance 全局 c 的关系（都是"幅值与组统计解耦"）
- 连续控制（机器人 PPO）中 advantage whitening 的对应缺陷与争论

## 三、归纳总结

1. **总根源一句话**：GRPO 幅值 = f(n⁺,n⁻) 纯组内计数函数，rollout 内容与策略置信度不进入——所有已知缺陷（猜测放大、难度偏差、长度偏差）都是这个"组成依赖"的不同侧面
2. **修正谱系统一观**：Dr.GRPO 去 σ（去难度依赖）→ SignBalance 全局常数幅值（去全部组成依赖）→ 力平衡 sg 项只用于恢复零均值不进梯度——**演进方向是"信号归信号（sign），缩放归全局（scale）"**
3. **"猜对≠推理对"是 RLVR 的数据结构问题**：55.95% 的 MATH 题答案有界意味着连"纯开放数学"都是混合体；训练集答案形态分析应成为 RLVR 数据管线标配
4. **clip 管不住幅值**：PPO clip 作用于重要性比而非 advantage 标量——常见误解是"clip 了就安全"，实际上 3.87× 的幅值放大全额穿透
5. **系统级缺陷与算法级缺陷同样致命**：引擎概率不一致这种"工程缝隙"能把 on-policy 偷偷变成 off-policy——RL 是系统工程，不只是损失函数设计
6. **健康监控先于调参**：四指标（长度/reward/熵/held-out）是低成本的体检，比盲改超参便宜一个数量级

## 四、趋势判断

1. **优势估计器进入"精细化修补期"**：2025 的 DAPO/Dr.GRPO 修外围（clip/归一化/采样），2026 的 SignBalance/2601.08521 直接动估计器本体——估计器公式本身成为研究对象
2. **答案空间结构分析会成为数据管线的标准步骤**：论文已给出按答案形态分类的范式（11 类/猜中率列），预计训练集"去猜化"（移除或降权高 p_g 子集）将普及
3. **SignBalance 式"参数免费修正"最容易落地**：不引外部模型不加推理成本，开源 RL 框架（verl/OpenRLHF）集成门槛低
4. **有界答案/Agent 多路径场景受益最大**：AMC 翻倍与搜索 Agent 提升指示了适用边界——纯开放数学任务收益近零，选型时先看任务答案空间
5. **与 reward hacking 治理合流**：猜测行为本质上是最朴素的 reward hacking（钻验证器空子），优势估计修正与 reward 设计修正将组成组合拳

## 五、关联分析（对自有体系）

1. **与 DUCK-Pi_5 RL 训练直接同构**：鸭子"站桩"= spurious reward 的连续控制实体版——存活 reward 存在"不动也能拿"的低成本路径（p_g 分量），策略学到 lucky-guess（站桩）而非目标行为（位移）。**已用的对策与本文修正一一对应**：三关训档制（站立→行走→专项）= 移除易猜问题；验收盯真实位移而非 reward/ep_len = 拒绝代理指标被污染；哨兵盯 err_vel_xy+fell_over+body_pose 多指标 = 健康监控四指标思路
2. **body_pose 课程 500iter 拉太猛侵蚀步态的教训**：混合 reward 里辅助项权重突变会让梯度被非目标分量劫持——与"组成变化污染学习信号"同因。V3 重训的对称 reward 罚右漂 + 缓拉 0→1.0 正是"信号解耦"的手工版
3. **对 microduck 训练脚本的实操启示**：rsl_rl 的 PPO advantage whitening 若按 batch 而非组归一化，长度/难度偏差的对应物也存在——值得在 V3 训前对 advantage 处理路径做一次代码审计（对照 §1.4 两偏差）
4. **与推理优化笔记链互补**：本文补齐"训练侧"信号质量，与部署侧（TTFT/TPOT/TwoTower 并行生成）构成"训推全链路信号/带宽经济学"两端
5. **量化因子研究方法论迁移**：因子正交化/中性化（剥离已知风险因子暴露）与 SignBalance（剥离猜测成分、只留验证器符号）是同一数学动作——"净化信号"跨域同构

## 六、指南分析

| 场景 | 查哪节 |
|------|--------|
| 快速理解 GRPO 为什么会被猜坏 | §1.1 闭式 + §1.2 放大机制 |
| SignBalance 怎么实现 | §1.3 三步表 + 公式 (11) |
| 训练响应越来越长怎么办 | §1.4 长度偏差 + Dr.GRPO 两改 |
| 熵崩塌/全对组浪费 | §1.5 Clip Higher + Dynamic Sampling |
| 训前该做什么检查 | §1.7 四指标 + 数据侧两常识 |
| 机器人/连续控制怎么对应 | §五.1-3 |

**核心口诀**：幅值=f(n⁺,n⁻) 是病根 / 猜对与推理对同权是毒 / sign 留信号、scale 归全局、sg 保零均值 / clip 管不住幅值 / 先体检再调参。

## 七、拓展应用推荐

- **V3 重训前**：审计 rsl_rl advantage 归一化路径（§五.3），把"多指标哨兵"与四指标体检表对齐
- **给 RL 训练 skill**：microduck-training / bipedal-rl-sim2real 可补一段"advantage 污染检查清单"
- **延伸阅读**：arXiv 2601.08521（组成偏差理论）、2506.10947（Spurious Rewards——随机奖励也能涨分的更激进发现）

---

→ 相关：[[2026-09-05-NVIDIA-TwoTower扩散语言模型-冻结上下文塔与去噪塔的双塔解耦.md]]（训推两端：信号质量 × 生成带宽）
→ 相关：GRPO 前置知识可参考 Cameron Wolfe《GRPO》入门篇（substack）


## 相关笔记

- [2026-08-23-MileGPO-里程碑式步骤信用分配](./2026-08-23-MileGPO-里程碑式步骤信用分配.md) — 信用分配修正路线
- [2026-08-29-ESvsGRPO-进化策略后训练推理覆盖](./2026-08-29-ESvsGRPO-进化策略后训练推理覆盖.md) — GRPO对照算法
- [2026-09-01-trl-verl-post-training-frameworks-2026](./2026-09-01-trl-verl-post-training-frameworks-2026.md) — 工程框架落地侧
