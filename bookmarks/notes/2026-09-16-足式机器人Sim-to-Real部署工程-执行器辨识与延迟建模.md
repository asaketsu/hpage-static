# 足式机器人 Sim-to-Real 部署工程：执行器辨识与延迟建模的系统化方法

> 探索日期：2026-09-16 ｜ 兴趣等级：L3 ｜ 来源：5 篇（IJRR 2026 + MIT + MDPI + 实践博客）
> 关联项目：DUCK-Pi_5 V7 双路训练（position 域，今晨训完待部署评估）
> 前序笔记：2026-09-14-足式机器人跌倒爬起策略 / 2026-09-15-GPO生长式策略优化

## 核心命题

Sim-to-Real 的瓶颈不在"多加域随机化"，而在**把仿真执行器建得像真执行器**。2026 年的前沿共识是：域随机化解决"分布外鲁棒性"，执行器动力学辨识解决"分布内保真度"，两者缺一不可——而后者恰是低成本硬件平台（如 STS 舵机）最常缺的一环。

## 核心发现

### 1. ETH PACE 框架：白盒执行器辨识优于黑盒 Actuator Network（IJRR 2026）

ETH Zürich Hutter 组的系统性 sim-to-real 框架（arXiv:2509.06342，IJRR 2026 正式发表）：

```
自底向上三层辨识：
① 单执行器台架表征（悬空、无接触 chirp 激励）
② 全系统级动力学参数估计
③ 跨平台运动控制验证（ANYmal + 多形态）
```

- 对比基线 = ANYbotics 的 LSTM Actuator Network（黑盒学习执行器模型）
- 结论：**物理落地的白盒辨识（PACE）匹配或超越黑盒 actuator network**，且可解释、可迁移
- 关键量化：高负载 locomotion 增益（P=60 N·m/rad, D=2）下，二阶模型在 **4.35 Hz 出现增益跌落**——舵机内环带宽是策略可用水频段的硬上限

### 2. MIT UAN：无监督执行器网络做 real-to-sim 校正

MIT 的 Unsupervised Actuator Network（RSC 论文）走第三条路：

- 映射关系：**关节位置/速度误差历史 → 修正力矩 δτ**（不学完整动力学，只学残差）
- 管线：UAN 训练 → WBC 用随机运动参考预训练 → UAN 在环微调 athletic 任务 → 部署
- 定位：为**复杂传动机构**（谐波减速/连杆传动）闭合 sim-to-real 差距——正是 DUCK 摆臂连杆 + STS 舵机减速箱的场景

### 3. 延迟建模是被低估的杀手

实践 playbook（2026-01）点名最大盲区：

> "Policies trained with 'perfect timing' often break hardest when timing becomes imperfect."

标准注入配方：
```
obs_delay_ms   = (0, 40)    # 观测延迟
act_delay_ms   = (0, 30)    # 动作延迟
motor_strength = (0.85, 1.05)  # 电机强度乘数
sensor_noise   = (0.0, 0.02)
+ 控制周期抖动（rate jitter）
```

DUCK 部署栈 v4 是 50Hz SyncRead+SyncWrite，串口往返 + 舵机响应延迟毫秒级抖动客观存在，当前训练管线未见延迟注入——这是 V7 部署前值得补的一项。

### 4. 域随机化的"有计划"配方（数字可直接抄）

| 参数 | 范围 | 说明 |
|------|------|------|
| 摩擦系数 | [0.1, 2.0] | 地面/脚垫 |
| 基座质量 | ±5 kg | 负载变化 |
| PD 增益 | 随机化 | 对抗标称值误差 |
| 推力扰动 | 随机冲量 | push recovery |
| action_scale | 0.25 | 位置目标缩放 |
| decimation | 10 | 1000Hz 物理 → 100Hz 策略 |

### 5. Sim-to-Sim 交叉验证是硬件部署前的标准闸门

成熟管线（rl-bipedal-walking 等）普遍插入 **Isaac → MuJoCo 的 sim-to-sim 验证步**：用第二物理引擎交叉验证策略，防止"过拟合到单一引擎的物理怪癖"。DUCK 训练（AutoDL Isaac）→ 部署（asa MuJoCo）链路天然就是这个结构，asa 侧验证失败应首先怀疑域失配而非策略本身。

## 与 DUCK-Pi_5 的映射

| 论文机制 | DUCK 现状 | 改进建议 |
|----------|-----------|---------|
| ETH chirp 悬空辨识 | STS 舵机仅有 FD 软件读数 + 零位台账 | 悬空发小幅扫频 step 序列，记录响应延迟/超调 → 估二阶模型带宽 |
| UAN 残差修正 | 无（XML 原生 position kp≈0.5 直用） | 若 V7 部署站不稳，先辨识再考虑残差网络 |
| 延迟注入 | 无 | 训练域加 obs/act delay 20-40ms 随机化，V8 候选项 |
| Sim-to-sim 闸门 | ✅ 已有（asa headless_test） | 保持，失败先查执行器域（铁律已固化） |
| motor_strength 随机化 | 无 | kp 随机化 ±15% 覆盖舵机个体差异 |

**关键洞察**：用户 09-15 六轮实测的"执行器域匹配铁律"（BAM kp200 域训的 v22a 在 position 域 0.2s 崩）本质就是 PACE 论文说的增益失配极端案例（100× 刚度差）。V7 回到 position 域训练是正确方向；下一步的真机差距大概率来自**延迟与摩擦**，而非刚度。

## Actionable Insights

1. **P0（V7 部署评估时）**：若 asa 仿真稳但真机抖动/失稳，优先测舵机实际延迟（串口 echo 时间戳），对齐 50Hz 控制环预算
2. **P1（V8 配方）**：加 obs/act delay 注入 + kp ±15% 随机化，成本一行配置，直接提升真机迁移率
3. **P2**：悬空 chirp 辨识 STS 舵机二阶参数，写进 duck_pi5.yaml 作为标定资产

## 关键风险与盲点

- ETH PACE 的对比基线是 ANYbotics 官方 LSTM actuator network 的**部署版而非重训版**（原始训练集不可得）——"白盒优于黑盒"的结论在低成本舵机场景未必成立（来源：官方论文 v2，社区验证有限）
- vnrobo/Medium 配方数字来自 humanoid 大厂平台（Unitree H1/XBot-L），STS 舵机带宽低一个量级，随机化范围需缩窄
- UAN 需要 WBC 预训练 + 参考轨迹，对纯 MLP 策略栈（rsl_rl）的迁移成本未验证

## 一页速查

> **Sim-to-Real 三层保险**：①执行器建模（白盒辨识 PACE / 黑盒 AN / 残差 UAN）→ ②域随机化（摩擦/质量/增益/延迟）→ ③sim-to-sim 交叉验证。
> **延迟注入标准配方**：obs (0,40)ms + act (0,30)ms + motor_strength (0.85,1.05)。
> **增益带宽硬上限**：舵机内环增益跌落频率（4.35Hz@P60/D2）决定策略可用频段。
> **DUCK 判定序**：asa 站不稳 → 查执行器域匹配 → 查延迟预算 → 才怀疑奖励设计。

## 待深入

- PACE 的 chirp 激励信号设计（频率扫描范围/幅值）——需要读原文 Section III
- action_delay 对 50Hz 控制环的具体影响量化（1 个周期 = 20ms，已占配方预算一半）

## 来源列表

- ETH IJRR 2026: arXiv:2509.06342 (Bjelonic, Tischhauser, Hutter) — PACE 框架 + 白盒执行器辨识
- MIT RSC: uan.csail.mit.edu/rsc/paper.pdf — Unsupervised Actuator Network
- MDPI Machines 2026, 14(9):1031 — 高减速比四足执行器动力学扩展辨识
- vnrobo.com/en/blog/rl-bipedal-walking — RL 双足全管线实践（obs/reward/DR 数字）
- github.com/darshmenon/rl-bipedal-walking — sim-to-sim + ROS2 部署参考实现
- Medium: Sim-to-Real RL: Closing the Gap Without Magic — 延迟建模配方

---
*笔记日期：2026-09-16 ｜ 来源：IJRR 2026 精读 + 5 源交叉 ｜ 关联项目：DUCK-Pi_5*
