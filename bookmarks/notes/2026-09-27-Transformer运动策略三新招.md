# Transformer 运动策略三新招：body tokenization、地形记忆与传感器掩码注意力

#机器人 #强化学习 #Transformer #运动控制 #DUCK项目关联

## 出处/来源

- 论文一：Generalized Locomotion in Out-of-distribution Conditions with Robust Transformer（ROLT，arXiv:2507.04039，2025-07-05）
- 论文二：Look Forward to Walk Backward: Efficient Terrain Memory for Backward Locomotion with Forward Vision（LF2WB，arXiv:2603.03138，2026-03-03）
- 论文三：Masked Sensory-Temporal Attention for Sensor Generalization in Quadruped Locomotion（MSTA，arXiv:2409.03332，2024-09-05，ICRA25，被引 4）
- 检索路径：TinyFish Search（Tavily 432 降级）→ curl 直取 arXiv abs
- 关联本地笔记：[2026-09-21 Transformer策略训练稳定性](2026-09-21-Transformer策略训练稳定性-熵坍缩到价值爆炸.md)、[2026-09-25 双足机器人站立学习三大新方案](2026-09-25-双足机器人站立学习三大新方案.md)

## 内容整理

### 论文一 ROLT：body tokenization + consistent dropout

问题设定：足式机器人策略的分布外（OOD）鲁棒性——动力学 gap（载荷/摩擦/执行器变化）与感知 gap（传感器噪声/缺失）。前人靠精细训练课程与在线适配，ROLT 只改网络结构。

两个关键设计：

1. **Body tokenization（肢体 token 化）**：不把全状态向量整体输入，而是按肢体（腿）切 token。注意力机制天然支持跨肢体知识共享——一条腿学到的动力学模式可被其他腿复用。四足/六足同架构直接泛化，跨构型共享是 MLP 做不到的（MLP 权重与输入维数绑定）。
2. **Consistent dropout（一致性 dropout）**：训练时对感知输入做**时间上一致**的随机丢弃（同一段 episode 内丢同样的传感器通道，而非逐步独立采样）。逐步独立 dropout 会让策略对"每步都可能换一套传感器"过度防御，学出保守策略；一致性 dropout 模拟的是"这台机器今天就是坏了一个传感器"的真实故障模式。结果：干净观测训练的模型，测试时能扛住强感知噪声 corruption。

对 DUCK 的映射：DuckTransformerModel 当前是全状态扁平输入 → MLP head。若做肢体 token 化改版，15 关节按 6 条腿链（hip/knee/ankle × 2）+ 头颈组切 token，理论上能让左右腿共享动力学知识——与我们 action_symmetry 奖励（env 级镜像惩罚）目标一致但实现层不同：**token 化在表征层共享，对称奖励在梯度层惩罚**，前者不需要手工构造镜像样本。

### 论文二 LF2WB：delta-rule 地形记忆

问题：前向深度相机写记忆、倒退走时读记忆——无后视传感器的倒退运动。

- 记忆写入用 **delta-rule 选择性更新**：先沿活跃子空间软删除旧值再写入新值（类似 DeltaNet 线性注意力），不是覆盖也不是纯累加。
- 部署时**恒定时间、恒定大小状态**的循环推理——每步计算量与地形复杂度无关，适配低成本机载处理器。
- 训练用硬件高效的并行计算（linear-recurrence 并行扫描）。

对 DUCK 的映射：当前 TRANS 策略的 64 帧滑窗是"无压缩的 FIFO 记忆"——窗口外的历史全部丢失，窗口内平权。delta-rule 记忆是"有损压缩的状态记忆"——无限历史压进恒定状态。若鸭子要学"走过斜坡后记住脚下地形"类任务（如真机在不平整地面往返），滑窗 64 帧可能不够；但站立/行走平衡任务中滑窗已够用，不必跟风。**真正值得借的是其"训练并行化 + 部署循环化"的双形态实现**——DuckTransformerModel 导出 ONNX 时遇过的冷启动零帧漂移问题（span=64 banded attention 修复），delta-rule 线性记忆天然没有这个问题，因为它的状态是累积的而非窗口的。

### 论文三 MSTA：传感器级掩码注意力

问题：不同机器人/不同传感器组合的泛化——策略要能处理"缺一路输入"的情况。

- **传感器级 attention**：每个传感器通道独立 token 化后做注意力，而非拼接成大向量——缺失通道直接 mask 掉，注意力自动重分配到可用通道。
- 大比例信息缺失下仍能理解自身状态；长输入序列仍可实机部署。

对 DUCK 的映射：鸭子 obs 64 维含 IMU（gyro/accel/gravity）、关节角、关节速度、cmd。真机已知故障模式：IMU 死零（grav 全 0 假象，09-22 教训）、gyro 零偏漂移。若训练时对 IMU 通道做一致性 mask（借 ROLT 的 consistent dropout），策略可学会"IMU 不可信时靠关节本体感觉站立"——这正好是 STAND2 物理真相（无静态稳定站姿，100% 靠动态平衡）下的一层保险。

## 三篇交叉对比

| 维度 | ROLT | LF2WB | MSTA |
|------|------|-------|------|
| 核心机制 | 肢体 token 共享 | delta-rule 状态记忆 | 传感器掩码注意力 |
| 解决的 gap | 动力学 OOD | 感知视野 OOD | 传感器组合 OOD |
| 记忆形式 | 无（纯注意力） | 恒定状态压缩记忆 | 无 |
| 训练技巧 | consistent dropout | 并行扫描训练 | 传感器级 mask |
| 对 DUCK 最可借 | 左右腿表征共享 | 双形态部署（并行训/循环部署） | IMU 故障容忍 |

## 趋势判断

Transformer 运动策略 2025-2026 的演进主线清晰：**注意力从"堆时间窗"转向"用结构"**。2023-2024 的做法是把滑窗越拉越长（Ours 64 帧、H1T-TRANS 同族），2025 后 top 工作转向按肢体切 token（ROLT）、按传感器通道掩码（MSTA）、按任务状态压缩（LF2WB delta-rule）。判断依据：三篇都不约而同回避了"更长窗口"，因为窗口长度与部署成本线性增长而收益边际递减；结构化注意力让同样的参数量获得更强的归纳偏置。对 DUCK 的预判：DuckTransformerModel 的 64 帧滑窗在站立/行走任务上够用，但若进入"记忆地形/跨任务"领域（三模型拼接后的上层任务），滑窗族会到天花板，届时 delta-rule 线性记忆是现成的下一格。

## 拓展应用推荐

- **ROLT body tokenization A/B 实验**：DuckTransformerModel 改肢体 token 版（6 腿链 token + 头颈 token），与现 env 级 action_symmetry 奖励做同配方对照——验收=hip_yaw 共模偏差（28.5° 病理）与对称性和=0±4°门槛。若 token 化可替代对称奖励，训练配置更简洁且无 reward-hack 风险
- **MSTA 掩码训练增强 IMU 容错**：在现有 obs 噪声注入基础上，加 10-20% episode 级一致性 IMU mask（借 ROLT consistent dropout 思想）——策略学会"IMU 不可信时靠关节本体感觉站"，对 pi5 双 IMU 污染问题（0x6B 头部 IMU 陷阱）是直接疫苗
- **LF2WB 双形态部署模式**：借"训练并行扫描 + 部署循环状态"的实现模式改造 TRANS 导出链——滑窗模型的 ONNX 冷启动零帧问题（span=64 banded attention 修复）在循环状态模型下天然不存在，可作为下一代 DuckTransformer 的架构选型依据

## 指南分析

给 DUCK 团队的操作指南：

1. **优先级排序**：MSTA 掩码训练（改 obs 配置即可，零架构改动）> ROLT token 化（改模型结构，需重训）> LF2WB 记忆（任务暂不需要）。当前 S 系主线在训，禁中途换架构——三个改动都应作为下一轮变体排队，不干扰现役线
2. **与既有铁律的兼容性检查**：ROLT token 化与 symmetry.py 的 obs 表硬编码 61 维 monkey-patch 冲突——token 化后 obs 维度语义变化，_OBS_PERM/_OBS_SIGN 需同步重推（H1X 加 base_lin_vel 时已踩过此坑）
3. **掩码训练与"疫苗剂量"原则的关系**：sim 噪声大于真机是故意的疫苗（imu_ang_vel ±0.2）；掩码是另一维度疫苗（通道级消失 vs 通道级污染），两者叠加时注意总噪声预算——建议先小规模 A/B 验证不伤主训指标再合入

## 查询拓展

- ROLT 的 body tokenization 与我们的 env 级 action_symmetry 奖励做 A/B：同一训练配方，分别用"token 化无对称奖励" vs "扁平输入+对称奖励"，比较共模偏差（hip_yaw 同向拧 28.5° 病理）治愈效果
- DuckTransformerModel 的 64 帧滑窗 vs delta-rule 线性记忆的参数量/推理延迟对比（Jetson Orin 侧部署预算）
- MSTA 的掩码训练是否与 obs 噪声注入（我们的"疫苗剂量"策略，sim 噪声大于真机）冲突——掩码是"通道级消失"，噪声注入是"通道级污染"，两者是否需要独立训练阶段

## 一句话总结

Transformer 运动策略的 2025-2026 演进主线是"把注意力用在结构上而不是时间上"——肢体 token 共享（ROLT）、传感器通道掩码（MSTA）都比堆时序窗口更对症；对 DUCK 最直接的启发是 ROLT 的肢体 token 化可替代 env 级对称奖励，且与我们已踩过的 ONNX 冷启动坑（span=64）同属"注意力结构决定部署形态"一族。

---
*学习笔记 · 生成于 2026-09-27 04:47 · 夜间自学习 cron（Tavily 432 降级链：TinyFish → curl 直取）*

## 相关笔记

- [2026-09-21 Transformer策略训练稳定性](2026-09-21-Transformer策略训练稳定性-熵坍缩到价值爆炸.md) — Transformer 策略训练病谱系，与本文三招互补（训稳→部署形态）
- [2026-09-23 Mamba SSM 机器人策略前沿](../../../explore/2026-09-23-mamba-ssm-robot-policy-frontier.md) — 序列模型路线对比：Mamba vs Transformer 运动策略
- [2026-09-21 自然步态模仿学习2026](2026-09-21-自然步态模仿学习2026-从AMP到流匹配先验.md) — 步态先验路线，与注意力结构改造正交
- [2026-09-24 窄可行域任务的执行器动力学课程](2026-09-24-窄可行域任务的执行器动力学课程-Spot倒立与viability-kernel.md) — 执行器约束下的策略学习，DUCK slew 域适配同族
- [2026-09-26 sim2real执行域适配](2026-09-26-sim2real执行域适配.md) — 同期姊妹篇：sim 侧适配 vs 本文策略结构侧改造
