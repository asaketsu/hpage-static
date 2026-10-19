#机器人 #强化学习 #sim2real #域随机化 #DUCK

# Sim2Real 域随机化新范式：CDR 持续随机化与 Real2Sim2Real

> 主题：域随机化（DR）的 2024-2026 演进——从"一次性全参数随机"到"持续域随机化（CDR）"与"Real2Sim2Real 系统辨识"，以及对 DUCK-Pi_5 H1D/H1A 双路实验的直接指导。

## 内容整理

### 1. 传统 DR 的固有缺陷：过度随机化问题

主流 DR 从训练起点就同时随机化全部参数（质量/摩擦/惯性/延迟等）。两篇论文共同指出其结构性缺陷：

- **任务难度爆炸**：多参数联合随机化显著增加系统不确定性，策略在仿真中更难收敛，产出次优策略、训练时间拉长
- **参数选择前置锁定**：要求训练开始前就精确识别所有关键随机化参数——对复杂系统这本身就不现实
- **范围设定靠猜**：过度随机化单参数同样致命——10% 的箱子位置噪声 = ±200mm 不确定性，直接让抓取任务不可解

### 2. CDR 持续域随机化（arXiv:2403.12193）

核心思想：把 DR 视为持续学习（CL）问题。流程：

1. 先在**零随机化的理想仿真**中训练（任务最易解）
2. 之后**每次只随机化一个参数子集**，视每个随机化配置为一个 CL 任务
3. 用 EWC（Elastic Weight Consolidation）及其在线变体防止灾难性遗忘——记住先前随机化的效果
4. 基座算法 PPO；提供 offline/online 两版实现

实验（机械臂 reaching + grasping，sim2real 零样本迁移）：CDR 匹配或超过"全程联合随机化"基线，且比"顺序微调"（只优化最新随机化、遗忘旧的）**更稳定、对随机化顺序更不敏感**。

**已知局限**（作者自陈）：①一次一个参数的因子化分解，无法捕获参数间交互效应，可能得到次优解——改进方向是定义相交参数组；②未解决"每个参数随机化范围怎么定"——可与自动 DR（随机化范围随策略性能渐进加宽）或主动 DR（从宽范围学出最有信息量的区间）组合。

### 3. Real2Sim2Real（arXiv:2608.22629，力矩控制机械臂）

另一条正交路线：与其"随机化覆盖误差"，不如"先把仿真校准到贴近真机"。流程（7-DOF Franka Panda）：

1. 真机录关节轨迹 → 遗传算法优化摩擦/惯量/重力补偿参数，最小化真机与仿真轨迹差
2. 在校准后参数附近做 DR（而非默认参数附近的盲目 DR）训练 TQC 智能体
3. Sim2Sim 双仿真器验证（MuJoCo + Gazebo）→ 真机部署

关键结论：**物理感知的系统辨识（尤其自定义摩擦函数+惯量调节，而非直接调仿真器摩擦参数）显著提升仿真保真度**；TQC 在评测的 DDPG/SAC/TD3/TQC 四算法中最可靠；真机在背隙/线缆拖拽/未建模延迟等扰动下仍鲁棒。

### 4. 第三条路：抽象仿真（arXiv:2604.15289，RA-L 2026）

用近似信息状态（Approximate Information States）做"抽象 Sim2Real"：不再追求高保真仿真，而是训练策略利用**抽象仿真器**（只保留任务相关信息）。COMPASS 方法随机化摩擦/位置噪声/速度噪声/航向偏置/动作参数/控制时步，在导航任务上以抽象状态策略逼近原生状态策略上限。对"仿真越真实越好"的主流假设提出了反例：抽象仿真更易指定，且心理学证据表明人类本就用抽象模型规划动作。

### 5. 三范式对比

| 范式 | 核心假设 | 成本 | 适用 |
|---|---|---|---|
| 传统 DR（联合随机） | 鲁棒性靠覆盖 | 低（纯仿真） | 参数少、gap 已知 |
| CDR（持续+分批随机） | 逐步扩域防灾难遗忘 | 中（多阶段训练） | 参数多、交互复杂 |
| Real2Sim2Real（辨识+定点 DR） | gap 可被辨识校准 | 高（需真机数据） | 力矩控制/精密控制 |
| 抽象仿真（COMPASS） | 任务相关状态足够 | 中 | 导航/决策类 |

## 查询拓展

- CDR 与课程学习（Curriculum）框架的组合——mjlab 的 Curriculum 权重调度是否天然兼容 EWC 正则
- EWC 在 2048 并行环境的 PPO 大批量更新下的 Fisher 信息估计稳定性（DUCK 场景 num_envs=2048）
- Real2Sim2Real 的遗传算法轨迹匹配能否用 DUCK 的双踝零位标定数据（EEPROM 台账）热启动
- 自动 DR（ADR）与 CDR 的实证对比——OpenAI ADR 原始方法论在足式上的复现案例

## 归纳总结

1. **"DR 越宽越好"是误区**：过度随机化提升任务难度、产出次优策略。H1D 实验（push ±0.5、friction 0.5-1.5 等全面加宽）正处在这个风险区——若 mR 显著下滑且 standing_fraction 不升，按本范式判断应是"随机化过宽压垮任务"，回退方向不是继续加宽而是分批/渐进。
2. **CDR 的可迁移洞察：随机化可以分批上**——先窄域练出稳定站姿，再逐参数扩域+EWC 防遗忘。DUCK 当前"一次配置定全程"的训练模式可改为两阶段：无 DR 基线 → 渐进 DR 微调。
3. **Real2Sim2Real 与 G9 根因分析互证**：G9 model_9750 的 sim2real gap（训练 env 单 env 无 DR 也 FELL@23-34）说明校准比覆盖更根本——BAM 执行器参数提取（kt/R/kp_fw 实测值进 edit_spec）本质就是一次手工 Real2Sim 辨识，方向正确，缺的是轨迹匹配级的系统量化。
4. **Sim2Sim 双仿真器验证值得抄**：DUCK 部署链（MuJoCo 训练 → asa MuJoCo 播放）可加一步 Gazebo/IsaacLab 交叉验证，域间能站 = 鲁棒性证据比单仿真器强得多。
5. 抽象仿真路线提醒：61 维 obs（gyro/关节角/指令历史）中可能有任务无关维度——obs 裁剪本身是一种"抽象"，与 obs_normalizer std=0 维度除零问题的清理逻辑同源。

## 趋势判断

- DR 研究重心从"随机什么"转向"何时随机、随机多宽、怎么定范围"——自动化范围设定（ADR/主动 DR）与 CL 结合是 2026 活跃方向
- Real2Sim 系统辨识随真机数据积累成本下降（示教/遥操作数据复用），"辨识+定点 DR"在力矩控制场景正在替代盲目宽 DR
- 双仿真器交叉验证（MuJoCo+Gazebo/Isaac）正在成为 sim2real 论文的标配消融环节

## 关联分析

- **H1D（DR 加宽版）**：本笔记归纳第 1 条直接给出判读框架——加宽 DR 的两个可能结局（鲁棒性↑ / 任务压垮），11:00 盯盘 cron 的评估标准可加一条"若 standing_fraction 掉且 fall_over 增，标记 DR 过宽候选，下一版改 CDR 渐进式"
- **H1A（action_rate_l2=0.2 动作平滑）**：与 CDP 论文（arXiv:2403.12193）中"低 jerk 值=更平滑运动、真机更理想"的平滑度量直接对应——H1A 的 action_rate 曲线可对照该论文的 smoothness 指标定义解读
- **G9 部署根因链**（docs/63）：Real2Sim2Real 范式验证了"BAM 参数提取→edit_spec 复刻"的路线正确性，且指明升级方向——从静态参数复制升级为轨迹匹配校准（用 asa 上录制的关节轨迹反推摩擦/阻尼残差）
- **bipedal-rl-sim2real / rl-policy-diagnosis skills**：CDR 的"分批随机化+防遗忘"应作为新条目补进 sim2real 手段清单（当前清单偏 DR/teacher-student/Ident 等经典法）
- **执行器域匹配铁律**（memory）：sts3025_12V_m1 域 kp 差 83% 零迁移的教训与 Real2Sim2Real 结论同向——域匹配是 DR 的前置条件，DR 无法弥补执行器域错配

## 出处

- Continual Domain Randomization — arXiv:2403.12193（CDR 方法、EWC+PPO、reaching/grasping 实验、局限自陈）
- Enhancing Sim2Real Transfer for Torque-Controlled Robots through Real2Sim Dynamics Estimation and RL — arXiv:2608.22629（遗传算法轨迹匹配、TQC、Franka、Sim2Sim 双验证）
- Abstract Sim2Real through Approxosite Information States — arXiv:2604.15289, RA-L 2026（COMPASS、抽象仿真、随机化参数范围）
- Domain Randomization for Sim2Real Transfer — Lilian Weng 博客（DR 方法谱系：ADR/主动 DR/Sim-to-sim via RCAN 等）

## 指南分析

对 DUCK 训练管线的操作级指导：

1. H1D 判读新增门禁：若出分后 standing_fraction 低于 H1-MLP 基线且 fall_over 增多 → 标记"DR 过宽"，候选修复=CDR 两阶段（先窄后宽）而非回滚到原 DR。
2. CDR 两阶段模板：阶段一零 DR 训至稳定（复用 H1-MLP 配方）→ 阶段二逐参数加 DR + EWC 正则（mjlab/rsl_rl 层面需确认 EWC 可挂载点，若无现成实现，可用 reward 正则近似）。
3. Real2Sim 升级路径：asa 播放时录关节轨迹 → 与仿真轨迹做差 → 遗传算法/贝叶斯优化反推摩擦/阻尼残差 → 修订 edit_spec。此为 G9 sim2real gap 的治本候选之一。
4. Sim2Sim 交叉验证：完训模型先在第二仿真器（Gazebo 或 IsaacLab）跑 500 步站立测试，通过才进 asa 真机队列——补上"单仿真器过拟合"盲区。

## 拓展应用推荐

- **DUCK H1D 后继版本 H2-CDR**：按 CDR 范式重排随机化次序（质量→摩擦→延迟→传感器噪声），每阶段 3k iter，EWC 或 reward 正则防遗忘
- **asa 轨迹辨识工具**：录制 v3f 稳定行走关节轨迹（30s@50Hz），离线反推 BAM 执行器残差参数，闭环校准 edit_spec
- **obs 抽象化实验**：对 61 维 obs 做任务相关性消融（逐维 mask 看站立分数变化），裁掉无关维度=免费鲁棒性


## 相关笔记

- [ROLT 稳健运动 Transformer（explore/）](./explore/2026-09-17-ROLT稳健运动Transformer-足式机器人OOD泛化架构.md) — 足式 OOD 泛化架构，DR 之外的抗分布偏移路线
- [RL 训练失败模式与 Reward Hacking 自动检测（explore/）](./explore/2026-09-17-RL训练失败模式与RewardHacking自动检测.md) — H1D/H1A 训练诊断配套
- [PhysicalAI 价值栈十一层拆解](./2026-09-16-PhysicalAI价值栈十一层拆解-任务优先视角的机器人系统瓶颈定位法.md) — sim2real 层在整机价值栈中的定位
