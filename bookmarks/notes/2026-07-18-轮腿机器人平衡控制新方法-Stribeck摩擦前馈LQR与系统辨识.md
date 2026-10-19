# 轮腿机器人平衡控制新方法——Stribeck 摩擦前馈 LQR 与系统辨识

> **来源**：
> - Zhang A. et al. *Balance Control Method for Bipedal Wheel-Legged Robots Based on Friction Feedforward Linear Quadratic Regulator* — Sensors (Basel), 25(4):1056, Feb 2025. DOI: 10.3390/s25041056. PMID: 40006286.
> - Zhu Y. et al. *Whleaper: A 10-DOF Flexible Bipedal Wheeled Robot* — arXiv:2504.21767, IROS 2024.
> - Petri JF, Lacey G. *Passive wheels on legged robots: a survey* — Front. Robot. AI, 13:1857985, Jun 2026.
> - Feng X. et al. *Research on wheel-legged robot based on LQR and ADRC* — Sci. Rep. 13:15122, 2023 (PMC10499820).
>
> **记录日期**：2026-07-18
> **关联项目**：`/home/jc/uclaw/project/wheel-legged-robot-v2/`（等待硬件实装）

**标签**：#轮腿机器人 #LQR #Stribeck摩擦 #系统辨识 #PSO #欠驱动 #平衡控制 #STM32H743

---

## 一、内容详细整理

### 1.1 问题背景：为什么标准 LQR 在轮腿机器人上不够好？

轮腿机器人（Wheel-Legged Robot）是典型的**欠驱动系统**——其自由度多于执行器数量。常用的平衡控制方法是把机器人建模成**轮式倒立摆（Wheeled Inverted Pendulum, WIP）**，用线性二次型调节器（LQR）求解状态反馈增益 K，控制转矩输出。

| 标准状态向量 | 物理含义 |
|---|---|
| θ (pitch) | 车身俯仰角 |
| θ̇ | 俯仰角速度 |
| x (wheel pos) | 轮子位置 |
| ẋ | 轮子速度 |

`τ = -K·[θ, θ̇, x, ẋ]ᵀ`

**核心痛点**：真实电机存在**非线性摩擦**（特别是低速 Stribeck 效应），模型未补偿时会出现：

- **极限环振荡**（Limit Cycle Oscillation）：低速时持续抖动无法收敛
- **静摩擦导致控制死区**：小信号被摩擦吸收
- **PID 积分饱和**：积分项试图补偿摩擦但响应滞后

这正是用户 V2 项目 P1（LQR 增益离线计算 + 上电必抖振）问题的学术化描述。

### 1.2 摩擦模型——Stribeck 曲线

电机摩擦由四部分组成：

```
F_total = F_coulomb·sign(v) + F_viscous·v + F_static·(1 - exp(-(v/v_s)²))·sign(v) + F_presliding
```

| 项 | 含义 | 数量级（小型 BLDC 如 4015） |
|---|---|---|
| F_coulomb | 库仑摩擦（干摩擦） | 0.05–0.2 N·m |
| F_viscous | 粘性摩擦（与速度成正比） | 0.01–0.1 N·m·s/rad |
| F_static（Stribeck） | 静摩擦，低速时从静摩擦向动摩擦过渡的"负斜率"区 | 引起低速抖动 |
| F_presliding | 预滑动（位移小于 μm 级时，呈弹性而非塑性变形） | 高精度伺服才需考虑 |

**Stribeck 效应**是低速抖动的元凶：速度从零开始增加时，摩擦力先**下降**（从静摩擦 → 动摩擦），再上升（粘性主导），形成"负阻尼"区域。

### 1.3 论文方法：摩擦前馈 LQR

Zhang et al. (2025) 在 GAC R&D 中心的工作给出了完整流水线：

```
┌──────────────────────────────────────────────────────────┐
│  Phase 1: 动力学建模 → 基础 LQR                            │
│  • WIP 线性化模型 (θ, θ̇, x, ẋ)                            │
│  • 解 Riccati 方程得 K                                     │
│  • τ_LQR = -K·x                                            │
├──────────────────────────────────────────────────────────┤
│  Phase 2: Stribeck 摩擦模型参数辨识                         │
│  • 设计恒速激励轨迹（匀速旋转）                              │
│  • 在多个恒定速度下记录电流（∝ 转矩）                       │
│  • 用 PSO 算法拟合 F_c, F_v, v_s, F_s 参数                 │
│  • 最小标准差 ≈ 0.30                                       │
├──────────────────────────────────────────────────────────┤
│  Phase 3: 前馈补偿                                          │
│  • τ_feedforward = F̂_friction(v_measured)                 │
│  • τ_total = τ_LQR + τ_feedforward                         │
└──────────────────────────────────────────────────────────┘
```

**关键工程细节**：

- **恒速激励**比白噪声激励更稳健——低速区 Stribeck 曲线需要密集采样
- **PSO 优于最小二乘**：Stribeck 是强非线性模型，最小二乘易陷入局部最优；PSO 全局搜索稳定
- 4 参数模型 `(F_c, F_v, v_s, F_s)` 在 30 维粒子 × 200 代迭代后收敛

### 1.4 实验对比：基础 LQR vs 摩擦前馈 LQR

论文在三种场景下对比：

| 场景 | 基础 LQR | 摩擦前馈 LQR | 改进 |
|---|---|---|---|
| 平地静平衡 | pitch σ ≈ 1.2°，极限环明显 | pitch σ ≈ 0.4° | 抖动减少 67% |
| 单边过桥（地形扰动） | 收敛时间 ≈ 2.5 s | 收敛时间 ≈ 1.0 s | 快 2.5× |
| 外部冲击 | 振荡持续 3+ s | 0.8 s 内收敛 | 鲁棒性显著提升 |

**核心结论**：**前馈补偿是最小代价解决低速抖动的工业级方案**，不需要修改 LQR 增益矩阵或引入复杂自适应控制。

### 1.5 10-DOF Whleaper：高自由度髋关节设计

Zhu et al. (2024) 在 IROS 提出的 Whleaper 是另一条改进路径——**增加机械自由度**：

| 设计维度 | 传统双轮腿 | Whleaper |
|---|---|---|
| 每腿髋关节 | 1–2 DOF（俯仰+偏航） | **3 DOF**（俯仰+偏航+滚转） |
| 总自由度 | 4–6 DOF | **10 DOF** |
| 控制挑战 | 状态空间 4 维 | 状态空间扩展到 8–10 维 |
| 优势 | 结构简单 | 横向稳定性、转弯灵活性显著提升 |

这呼应了用户 V2 项目讨论的"L3 偏航关节"扩展方案——Whleaper 验证了高 DOF 髋关节在仿真和实物上都能提升稳定性，但需要 MPC+WBC 两层架构（而非纯 LQR）才能发挥全部潜力。

### 1.6 被动轮综述：能量效率的另一种思路

Petri & Lacey (2026) 的综述提出一个反直觉的方向——**被动轮（Passive Wheels）**：

- 不给轮子装电机，**靠腿部摆动驱动轮子滚动**（像人类滑旱冰）
- 机械简单、腿质量轻、CoT（Cost of Transport）降低 70–80%
- 代价：非完整约束 + 欠驱动动力学，控制问题极难

**对用户项目的启示**：被动轮是远期研究方向，对当前 V2（主动轮 + ODrive）暂不适用。但综述整理了 40+ 机器人的表格，是设计参考的宝库。

---

## 二、查询拓展

### 2.1 PSO 算法在机器人辨识中的应用

粒子群优化（Particle Swarm Optimization）是 Kennedy & Eberhart (1995) 受鸟群觅食启发的元启发式算法。在机器人参数辨识中的优势：

- **不要求可微性**：Stribeck 模型含 `sign(v)` 和 `exp()` 项，梯度法易卡死
- **全局搜索**：100 粒子能覆盖整个参数空间
- **天然并行**：每个粒子评估独立，适合 STM32 + 上位机协同

```python
# 伪代码：Stribeck 参数 PSO 辨识
def stribeck(v, Fc, Fv, vs, Fs):
    return Fc*np.sign(v) + Fv*v + Fs*(1 - np.exp(-(v/vs)**2))*np.sign(v)

def fitness(params, data):
    Fc, Fv, vs, Fs = params
    v_measured, torque_measured = data
    torque_pred = stribeck(v_measured, Fc, Fv, vs, Fs)
    return np.std(torque_pred - torque_measured)

# PSO 主循环
for iter in range(200):
    for particle in particles:
        particle.fitness = fitness(particle.position, data)
        if particle.fitness < particle.best_fitness:
            particle.best = particle.position
        if particle.fitness < global_best.fitness:
            global_best = particle
    for particle in particles:
        particle.velocity = w*v + c1*r1*(p_best - p) + c2*r2*(g_best - p)
        particle.position += particle.velocity
```

### 2.2 系统辨识 vs 强化学习：两条路径

传统系统辨识（System Identification）与 RL 学派在机器人控制上的分野：

| 维度 | 系统辨识 + LQR/MPC | RL（如 Boston Dynamics + RAI Institute Atlas）|
|---|---|---|
| 数据需求 | 几十次激励实验 | 数百万次仿真步 |
| 模型依赖 | 强（需动力学方程） | 弱（端到端学习） |
| Sim2Real | 直接（模型即真实） | 困难（域随机化） |
| 部署成本 | 低（STM32 可跑 LQR） | 高（需神经网络推理） |
| 可解释性 | 强 | 弱 |

Boston Dynamics 2025 年 3 月发布的 Atlas RL 演示（"Walk, Run, Crawl, RL Fun"）显示：**基于人类动捕参考的 RL 策略已能生成稳定的多步态运动**。但工业级产品（GAC、UBTECH）仍以模型法为主，原因在于可解释性和安全验证。

### 2.3 Riccati 方程的实时求解

LQR 增益矩阵 K 的计算需要解代数 Riccati 方程：

`AᵀP + PA - PBR⁻¹BᵀP + Q = 0`

- **离线求解**：在 PC 上用 SciPy `control.lqr(A, B, Q, R)` 一次算完
- **在线求解**：STM32H743 的 M7 双精度 FPU @ 480MHz 可在 ~10 ms 内完成 4×4 矩阵 Riccati 求解，但每次更新增益会引入控制不连续
- **折中方案**：**增益调度（Gain Scheduling）**——预先离线计算 5–10 组 K（对应不同腿长 / 负载），运行时根据状态切换

---

## 三、归纳总结

### 3.1 轮腿平衡控制算法谱系

```
              轮腿平衡控制
        ┌──────────┴──────────┐
     模型法                    学习法
   ┌────┴────┐             ┌────┴────┐
  线性     非线性          模仿      强化
  LQR     MPC/WBC        Learning    Learning
   │         │             │           │
 基础     前馈补偿        DAgger     PPO/SAC
 LQR     摩擦/重力                      │
   │                                    │
 PID ←─── 降级备用         Boston Dynamics Atlas
                                  (RL + 动捕)
```

### 3.2 摩擦前馈 LQR 的工程决策矩阵

| 你的痛点 | 推荐方案 | 工作量 |
|---|---|---|
| 低速极限环抖动 | **Stribeck 前馈** | 2–4 h |
| 不同负载下漂移 | **增益调度** | 1–2 h |
| 大冲击后失稳 | **LQR + ADRC**（Feng 2023） | 8+ h |
| 复杂地形通过性 | **MPC + WBC** | 40+ h |
| 端到端跳跃/跑酷 | **RL（sim2real）** | 100+ h |

### 3.3 用户 V2 项目改进路线图

将论文方法映射到 V2 项目（STM32H743 + ODrive + 4015 BLDC + MT6701）：

```
Phase A (现在)：基础 LQR 离线参数 (M=2.5, L=0.15, J=0.02)
    ↓ 上电后用 PID 粗调能站住
Phase B (新)：白噪声激励 + sysid_logger 记录 → 离线拟合真实 M/L/J
    ↓ 得到精确物理参数
Phase C (新)：恒速激励辨识 4015 的 Stribeck 摩擦参数
    ↓ PSO 在 PC 上跑，参数烧入 Flash
Phase D (新)：摩擦前馈 LQR 部署
    ↓ τ_total = -K·x + F̂_friction(v)
最终：稳定无抖动平衡
```

**新增代码量**：~150 行 C（STM32 端前馈补偿）+ ~80 行 Python（PC 端 PSO 辨识脚本）

---

## 四、趋势判断

### 4.1 摩擦前馈将成为 LQR 标配

**依据**：Zhang et al. (2025) 是 GAC R&D 中心（广汽研究院）的工作，代表了汽车工业界对机器人控制的工程化要求。论文方法**不需要修改 LQR 增益矩阵**，只需在转矩输出后加一项前馈补偿，实施成本极低。预计 1–2 年内成为轮腿机器人开源项目的标配组件。

### 4.2 高 DOF 髋关节是下一代主流

**依据**：Whleaper（10-DOF）展示了 3-DOF 髋关节对横向稳定性的巨大提升。人类髋关节本身就是 3-DOF（屈伸/外展内收/内旋外旋），限制在 1–2 DOF 是工程妥协而非生物学最优。随着无框力矩电机（Frameless Torque Motor）价格下降，3-DOF 髋关节将在 2026–2027 年成为高端轮腿机器人标准。

### 4.3 RL + 模型法的混合架构将主导

**依据**：Boston Dynamics 与 RAI Institute（原 Boston Dynamics AI Institute）的合作演示了 RL 策略在 Atlas 上的成功。但纯 RL 在安全验证和可解释性上的劣势使其难以独立部署。**模型法提供安全基线 + RL 提供性能上限**的混合架构将是 2026–2028 年的主流方向。用户的 V2 项目先用 LQR 打基础，未来可在此基础上叠加 RL 微调。

### 4.4 被动轮将开辟新应用场景

**依据**：Petri & Lacey (2026) 综述显示，被动轮机器人的 CoT 比主动轮低 70–80%，在长距离巡检、仓储物流等场景有独特优势。但控制难度极高，目前仅在学术界验证。预计 3–5 年后才有商业化产品。

---

## 五、关联分析

### 5.1 与 wheel-legged-robot-v2 项目的关联

> 项目路径：`/home/jc/uclaw/project/wheel-legged-robot-v2/`

本笔记的核心方法**直接解决项目 P1 问题**（LQR 增益离线计算 → 上电必抖振）：

| 项目要素 | 论文对应 | 改进建议 |
|---|---|---|
| `scripts/lqr_design.py` 离线 K 计算 | Phase 1 基础 LQR | ✅ 已实现，保留 |
| `scripts/sysid_fit.py` 参数拟合 | Phase 2 辨识 | 🔧 需补充 Stribeck 项，不能只辨识 M/L/J |
| `robot_config.h` K 矩阵 | Phase 1 输出 | ✅ 已实现 |
| 缺失：摩擦前馈 | Phase 3 核心创新 | 🔴 **必须新增 `friction_feedforward.c`** |

**具体行动项**：
1. 新增 `scripts/stribeck_pso_fit.py`——PC 端 PSO 辨识脚本
2. 在 `servo_driver.c` / `odrive_driver.c` 中新增 `friction_compensate(v)` 函数
3. 在 `balance_control.c` 的 `Balance_Update()` 末尾加 `τ += friction_compensate(wheel_vel)`
4. `sysid_logger` 增加**恒速激励模式**（不只是白噪声）

### 5.2 与强化学习入门完全指南的关联

> 2026-07-14 笔记

论文综述部分提到 Boston Dynamics Atlas 使用 RL + 动捕的策略学习。这验证了笔记中"PPO/SAC 是机器人 RL 主流算法"的判断。但**控制频率差异巨大**：Atlas 的 RL 策略在 GPU 上以 50 Hz 运行，而 V2 项目的 LQR 在 STM32 上以 1 kHz 运行——频率差 20×。对小型机器人而言，模型法在实时性上仍有压倒性优势。

### 5.3 与机器人学习范式对比的关联

> 2026-06-11 笔记

那篇笔记对比了模仿学习（IL）和强化学习（RL）。本笔记补充了第三条路径——**经典控制理论（LQR/MPC）**。三种范式在机器人控制上的分工：

- **经典控制**：平衡、轨迹跟踪（高频、低维度、强模型依赖）
- **模仿学习**：复杂技能学习（动捕数据、中等频率）
- **强化学习**：极限运动（跑酷、跳跃、低频率但高策略复杂度）

### 5.4 与 STM32 嵌入式开发的关联

> Skill: stm32-embedded-dev

本笔记的工程实现深度依赖 STM32H743 的能力：
- **双精度 FPU**：Riccati 方程求解和矩阵运算的硬件基础
- **FDCAN1**：与 ODrive 3.6 的高速通信（500 kbps）
- **FreeRTOS**：1 kHz 平衡环 + 200 Hz 安全监控的任务调度
- **DMA + TC 中断**：STS3025 半双工方向控制的关键

---

## 六、金句摘录

> "电机摩擦会导致低速运动时的收敛性差和振荡，这是基础 LQR 控制器在轮腿机器人上的核心瓶颈。" — Zhang et al. (2025)

> "Stribeck 摩擦辨识的最小标准差约为 0.30，辨识值与实际值高度吻合，表明 PSO 是有效的辨识方法。"

> "轮子结合了腿的适应性和轮的能量效率，但被动轮机器人的非完整约束使控制问题极为复杂。" — Petri & Lacey (2026)

> "增加髋关节自由度可以显著提升轮腿机器人的稳定性和灵活性。" — Zhu et al. (Whleaper, 2024)

> "模型法提供安全基线，RL 提供性能上限——混合架构将主导未来机器人控制。" — 笔者归纳

---

## 七、行动启示

| 启示 | 行动 | 优先级 |
|---|---|---|
| 摩擦是 LQR 抖动的根因 | 在 V2 项目增加 Stribeck 摩擦辨识流程 | **P0** |
| PSO 优于最小二乘辨识 | 编写 `stribeck_pso_fit.py` 脚本 | **P0** |
| 恒速激励是辨识关键 | `sysid_logger` 增加恒速激励模式 | **P1** |
| 高 DOF 髋关节是趋势 | V2 的"L3 偏航关节"扩展方案有学术支撑 | P2 |
| RL + 模型法混合是未来 | 关注 Boston Dynamics + RAI Institute 后续工作 | P3 |
| 被动轮是新方向 | 长期关注 Petri 综述的引用论文 | P4 |

### 立即可执行的代码改进（针对 V2 项目）

```c
// robot_config.h 新增
#define FRICTION_COULOMB     0.08f    // N·m, 待 PSO 辨识
#define FRICTION_VISCOUS     0.02f    // N·m·s/rad
#define FRICTION_STRIBECK_VS 0.05f    // rad/s, Stribeck 临界速度
#define FRICTION_STATIC      0.12f    // N·m, 静摩擦

// balance_control.c 新增
static float friction_compensate(float wheel_vel_rad_s) {
    float v = wheel_vel_rad_s;
    float sign = (v > 0) ? 1.0f : ((v < 0) ? -1.0f : 0.0f);
    float abs_v = fabsf(v);
    return FRICTION_COULOMB * sign
         + FRICTION_VISCOUS * v
         + FRICTION_STATIC * (1.0f - expf(-(abs_v/FRICTION_STRIBECK_VS)*(abs_v/FRICTION_STRIBECK_VS))) * sign;
}

// 在 Balance_Update() 末尾
ctrl->torque_left  += friction_compensate(ctrl->wheel_vel_left);
ctrl->torque_right += friction_compensate(ctrl->wheel_vel_right);
```

## 相关笔记
- [双轮腿机器人V2功能分析与扩展说明](2026-07-16-双轮腿机器人V2功能分析与扩展说明.md)
