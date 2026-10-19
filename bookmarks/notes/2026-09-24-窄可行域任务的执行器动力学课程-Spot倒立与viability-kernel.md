---
title: 窄可行域任务的执行器动力学课程——Spot倒立与viability kernel分析
source: https://arxiv.org/abs/2609.09492
date: 2026-09-24
tags: [legged-robot, reinforcement-learning, curriculum, sim2real]
---

#rl #足式机器人 #强化学习 #课程学习

# 窄可行域任务的执行器动力学课程——Spot 倒立与 viability kernel 分析

## 内容整理

**论文**: Actuator Dynamics Curricula for Narrow-Viability Tasks in Legged Robot Learning (arXiv:2609.09492v1, 2026-09-08)

**核心问题**: 一类足式机器人任务在标准 RL 训练下永远不收敛——不是因为奖励稀疏，而是因为"既追奖励又避免早终止"的轨迹集合在任何实际采样预算下趋近于零。论文称之为 **narrow-viability tasks（窄可行域任务）**。代表案例：Boston Dynamics Spot 从四足站姿转移到前腿倒立（handstand），需要在约 1 秒内 pitch 转 90°，中途经过"身体半倾、后腿离地、持续旋转"的状态区域——该区域内大多数动作都会摔倒触发早终止，策略梯度拿不到连贯训练信号。

**方法: Actuator Dynamics Curriculum (ADC)**
- 每个关节初始化为**高于系统辨识值的刚度** K₀，阻尼按保持临界阻尼选取；随策略进步把刚度退火回辨识值 K*。部署时策略运行在真实执行器动力学下。
- 直觉：高关节刚度 = 位置指令跟踪更激进 = 训练早期策略从不完美动作中恢复的余量更大。
- 参数只有一个物理意义明确的标量（关节刚度），只要求仿真器能在训练时变执行器参数（现代物理引擎都支持）。

**理论支撑（cart-pole Proposition 1）**: 对位置由 PD 跟踪的 cart-pole 系统，在临界阻尼下提高闭环自然频率 ω_n 会**单调扩大 viability kernel**（从任务约束可被无限期满足的状态集合），即提高任务可行的初始状态占比。实验在 θ₀ ∈ [-0.8, 0.8] rad、θ̇₀ ∈ [-5, 5] rad/s 网格上用内环 PD + 外环 LQR 验证：可行区域随 ω_n 单调增长。

**实验数据（Spot handstand, 10 seeds）**:
- 训练栈：IsaacLab + RSL-RL + PPO，RTX 5000 Ada/32GB，端到端约 1.5 小时/seed。
- K₀ 选择协议：从 K*=40 出发以步长 5 递增，取 1000 条仿真 episode 上任务成功率超过 **98% 阈值**的最小值 → K₀=60。
- 无课程：ep_len 略增后在 **400 步附近平台期**卡 10000 次策略更新，reward 持续低迷——rollout 早终止到策略梯度无法产生连贯信号。
- 有课程：reward 与 ep_len 单调上升，1.5 小时内收敛到最大值，**zero-shot 迁移到硬件**（机载 Jetson Nano 推理，Spot SDK 通信）成功，跨 seed 一致。
- 退火触发依据：**已完成 episode 的长度增长**（completed episode lengths），不是固定时间表。

**结论**: 仿真闭环关节动力学是设计课程的有用轴——适用于"探索被终止条件卡死而非被奖励信号卡死"的任务。

## 查询拓展

- viability kernel 的计算方法（level-set/HJB）能否用于离线预估 DUCK 蹲→站链路的可行域宽度，替代纯试错？
- ADC 与 initial state curriculum（DUCK 的 prone_init_prob 爬坡）正交性验证：两者同时开是否叠加收益？
- 论文引用的 Leuven/ETH 系 actuator net 系统辨识（CMA-ES 辨识 K*）与 DUCK 的 slew 执行器课程（H1X-R）在"执行器建模保真度"轴上的位置。
- 退火调度敏感性：论文用 episode 长度增长做触发，若换成 fell 比例（DUCK 现行课程触发）是否有等价性？

## 归纳总结

1. **不收敛的本质分类学**：RL 足式任务不收敛有两类病因——奖励信号缺失（exploration starvation）与终止条件过杀（termination starvation）。ADC 只治后者，且给出了判别签名：reward 有形状但 ep_len 卡死在低位、rollout 大量早终止。
2. **ep_len 卡 400 步的双义性**（对判读日志至关重要）：同样的"存活恒 400 步"签名，一种含义是环境 episode 上限（8s×50Hz，DUCK stand_eval 冤案），另一种是训练真不收敛（本文 baseline）。区分方法：看 reward 是否同时停滞 + 看 fell 比例是否异常高。
3. **课程的本质是扩可行域而非降难度**：常规理解课程=从易到难；ADC 的视角是先扩大 viability kernel 让策略有梯度信号，再收缩回真实动力学。这解释了为什么"先虚后实"必须退火——部署域是硬约束，课程域只是训练脚手架。
4. **物理意义标量参数 > 多维课程旋钮**：单一刚度标量（配临界阻尼闭式解）比一组课程超参更可复现、可跨任务迁移。

## 趋势判断

- 执行器动力学课程是 sim2real 社区从"域随机化"转向"域课程化"的最新一环：CDR（09-18 已读）随机化执行器参数抗过拟合，ADC 单向退火救可行域——两者可组合（先退火到 K*，再在 K* 附近随机化）。
- termination starvation 问题会随任务谱系变难（倒立/跳跃/窄支撑面）越来越常见，"改环境动力学救探索"会成为一个独立的课程设计轴，与奖励塑形/模仿学习并列。
- 论文局限自认：仅验证单一任务（handstand）+ 定量成功指标与失败模式分析有待补——这是单任务方法论论文的通病，规模化验证（多平台多任务）是下一个缺口。

## 关联分析

**与 DUCK 训练的直接对照**:
- **R3-R5 坏 init 三连（docs/101）= 典型 narrow-viability**: joint_pos={} 抄漏 → 出生 tilt 87° 躺平，签名 ep_len 14-16 + fell 138（健康 24-26/80）。当时修复走的是 init 分布修正（直腿 reset），本文提供了正交备选：不动 init，把仿真刚度临时拉高扩大出生状态的可行域——适用于 init 分布本身不能动（如真机对接姿态固定）的场景。
- **W5R2 slew 执行器课程是 ADC 的镜像**: DUCK 的 slew 课程是"降低执行器带宽贴近真机速度寄存器分族"，ADC 是"提高刚度再退火回真机"。方向相反但同一思想：执行器动力学本身是课程变量。DUCK 未来若再遇"配方对但就是不收敛"的 variant，可试"高刚度起步 + 按 ep_len 增长退火"三件套。
- **R9 系 prone_init_prob 爬坡课程**（0.4 爬坡中，ep_len 降至 15/fell 升至 139 = 课程机械现象）与 ADC 的"按完成 episode 长度退火"对照：DUCK 现行按固定 iter 爬坡，若爬坡后 ep_len 长期不恢复，可借鉴"ep_len 增长才继续退火"的自适应门控，避免课程速度快于策略学习速度。
- **98% 成功率阈值选 K₀ 的协议**可直接抄：DUCK 选 slew 限幅/增益档位时，用"1000 episode 上成功率超阈值的最小档"替代逐档真机试错。

**与已读论文的关联**:
- 与《双足机器人域随机化新范式 CDR》（09-18）构成执行器轴的两种操作：随机化（抗过拟合）vs 退火（救探索）。
- 与《企鹅摇摆步态》（09-22）共同点：都在低可行域物理条件下重新设计训练/形态干预，前者靠形态（躯干侧摆），本文靠动力学（刚度）。

## 指南分析

**可操作步骤（若 DUCK 需要引入 ADC）**:
1. 辨识当前执行器等效刚度 K*（DUCK 用 STS 舵机位置伺服，等效 K 可由阶跃响应 overshoot 估计，04_servo_sweep 已有工具链）。
2. mjlab/IsaacLab 侧把 PD 刚度做成 curriculum 参数（类似 standing_stages 注入路径，注意 interval 参数 TypeError 坑）。
3. 按 +5 步进扫 K₀，用 1000 episode × 98% 阈值定档。
4. 退火触发挂 ep_len 增长（非固定 iter），写进 runtime_guard 的课程监控段。
5. 完训验收仍走 stand_eval_v2（time_out 语义已修），防"高刚度域训练绿、真机域部署红"的假闭环。

**风险提示**: 高刚度训练域与部署域差距过大时，退火末段可能出现策略突变（论文未报失败 seed）；DUCK 若采用，退火最后 20% 建议放缓并在中间档做 stand_eval 抽检。

## 拓展应用推荐

- **P0（对 DUCK R 线）**: 把"ep_len 增长门控退火"思想加进现行 prone_init 课程监控——若 prone 概率爬坡后 ep_len 连续 500 iter 不恢复，自动暂停爬坡（只改课程调度，不动奖励结构，属授权范围内）。
- **P1**: 为下一轮"配方对但不收敛"的 variant 准备 ADC 备选方案文档（docs/NN 落盘），含 K₀ 扫描协议。
- **P2**: Hermes 自进化侧借鉴——launch_gate.sh 的"死法签名"体系本质是 termination starvation 的验尸版；ADC 是预防版，两者对偶。可在 gate 文档中加一条：若新 variant 首训 ep_len 卡低位 + fell 暴高，优先怀疑 narrow-viability 而非超参。

## 出处

- 论文: Actuator Dynamics Curricula for Narrow-Viability Tasks in Legged Robot Learning
- arXiv: 2609.09492v1, submitted 2026-09-08, cs.RO
- HTML 全文: https://arxiv.org/html/2609.09492v1
- 训练栈: IsaacLab + RSL-RL + PPO；部署: Jetson Nano 机载推理
- 相关本地文档: DUCK-Pi_5/docs/101（R3-R5 坏 init 三连）、docs/86 §18（W1 三病）、docs/98（静站验收门禁）

## 相关笔记

- [没有免费的检验器——验证器150篇综述](./2026-09-24-没有免费的检验器-机器人策略验证器150篇综述.md) — 同日姊妹篇：课程侧 vs 验证侧
- [ROLT稳健运动Transformer](./explore/2026-09-17-ROLT稳健运动Transformer-足式机器人OOD泛化架构.md) — 足式 OOD 泛化另一路线
- [Sim2Real本体感知分布匹配](./explore/2026-09-04-Sim2Real本体感知分布匹配-无动捕残差执行器学习.md) — 执行器动力学 sim2real 直接相关
- Mamba/SSM 机器人策略前沿（~/explore/2026-09-23-mamba-ssm-robot-policy-frontier.md）— 策略架构候选谱系
