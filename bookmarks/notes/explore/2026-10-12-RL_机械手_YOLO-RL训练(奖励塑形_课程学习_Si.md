# RL机械手灵巧操作：奖励塑形、课程学习与Sim2Real

> 嗅探学习笔记 | 2026-10-12 | auto-explore

## 摘要

机械手灵巧操作（dexterous manipulation）是机器人RL的前沿难题。2024-2025年三项代表性工作——CyberDemo（CVPR 2024）、Lin et al.（CoRL 2025, arXiv:2502.20396）、CO-HER——从不同角度推进了sim-to-real在灵巧操作上的突破：CyberDemo用仿真数据增强+课程学习+少量真机微调；Lin et al.提出四模块recipe（自动real-to-sim标定+通用化奖励+分治蒸馏+混合感知表征）实现零人类演示的双臂视觉RL；CO-HER用环境迁移课程解决稀疏奖励下的探索效率问题。共同主线：奖励设计的通用化（从任务特定到接触目标+物体目标分解）、课程学习的反向化（从目标附近起步逐步加难）、sim-to-real的自动化标定（4分钟真机数据自动校准物理参数）。

## 关键发现

### 1. Lin et al. 2025 — Sim-to-Real RL Recipe for Humanoid Dexterous Manipulation

- **机构**：UC Berkeley + NVIDIA + UT Austin（Toru Lin, Linxi "Jim" Fan, Jitendra Malik, Yuke Zhu）
- **平台**：Fourier GR-1人形机器人，双多指手，第三视角相机+自我中心相机+本体感知
- **三项任务**：grasp-and-reach（抓取递送）、box lift（抬箱）、bimanual handover（双手交接）
- **四模块方法**：
  - **A. Real-to-Sim自动标定**：采样物理参数组合（摩擦/阻尼/URDF惯量/关节限位），以最小化真机轨迹跟踪误差选参，仅需4分钟真机数据采集，消除手工调参
  - **B. 通用化奖励设计**：用"接触贴纸"（contact stickers，物体表面程序化生成标记点）指定指尖接触位置，奖励=指尖到标记点逆距离惩罚 + 物体状态偏差惩罚。将复杂任务分解为接触目标+物体目标两个可解释组件
  - **C. 分治蒸馏**：复杂多物体任务拆为单物体子任务→训练专家策略→筛选高质量rollout→蒸馏为统一通用策略。专家策略充当"专家演示者"引导通用策略学习
  - **D. 混合物体表征**：稀疏表征（点云关键点）+稠密表征（体素/深度图），模态特异性增强，弥合sim-to-real感知gap
- **核心成果**：零人类演示，策略泛化到未见物体（不同形状/尺寸/颜色/材质/质量），抗外力扰动（ poking/pulling/pushing后快速恢复），涌现失败恢复行为（掉落物体后自动重新抓取）
- **训练细节**：任务感知初始化——每集从约30秒人类遥操作采集的手-物体构型起步，显著改善早期探索效率

### 2. CyberDemo（CVPR 2024）— 仿真演示增强

- **核心思路**：在仿真中采集人类遥操作演示→利用仿真器的采样能力和oracle状态信息大规模增强数据（视觉/运动学/几何多样性）→自动课程学习训练→少量真机演示（3分钟轨迹）微调→真机部署
- **关键洞察**：仿真增强数据在真机迁移中**优于**传统真机域内演示数据
- **泛化实证**：训练只见三阀（tri-valve）物体，真机能旋转四阀（tetra-valve）和五阀（penta-valve）未见物体
- **课程学习**：Automatic Curriculum Learning——训练中逐步增加难度，从简单构型到复杂扰动

### 3. CO-HER — 环境迁移课程 + 稀疏奖励 + 多目标RL

- **问题**：HER（Hindsight Experience Replay）在目标距初始状态远时效率低下
- **方法**：Co-adapting Hindsight Experience Replay with Environment shifts——通过环境迁移生成渐进复杂课程，与稀疏奖励+多目标RL协同
- **机制**：初始状态和目标距离由近到远渐进扩展，障碍物从无到有渐进引入
- **验证**：PickAndPlace + FetchPush，样本效率优于vanilla HER；PickAndPlace完成Sim2Real（Franka机器人）

### 4. 反向课程（Reverse Curriculum）— 双臂装配场景

- **来源**：MDPI Machines 2024，双臂PegInHole任务
- **方法**：从接近目标状态起步训练（插入几乎完成），随策略性能提升逐步增加初始条件难度
- **机制**：利用装配任务的可逆性——大多数装配任务在状态空间有限区域内有稀疏奖励，反向课程让策略从"已知答案"区域向"未知起点"扩展
- **架构**：分层控制——低层阻抗控制（接收期望轨迹）+高层RL策略（输出期望轨迹）

### 5. 物理信息奖励塑形（Physics-Informed Reward Shaping）

- **来源**：Fareh et al. 2025（13次引用，ScienceDirect）
- **核心**：将物理先验知识注入奖励函数塑形项，与域随机化结合实现sim-to-real
- **定位**：奖励塑形+域随机化的组合范式，适用于无精确系统模型的model-free控制

## 对工作的价值

### 与DUCK训练的直接对照

- **反向课程 = push课程化的理论支撑**：DUCK E31g/E21的失败（push 0.5→0.7跳档热启=策略坍缩到退化解）正是反向课程的反面教材。CO-HER和反向课程方法都证明：难度必须从近目标起步渐进增加，DUCK的push升级应0.5→0.55→0.6→0.65→0.7每500iter课程化（已在docs/148定案但缺理论背书，此处补上文献依据）
- **接触贴纸奖励 = 奖励通用化新范式**：DUCK的tracking奖励用exp(-err/std²)方向盲给分（倒走13-30%分源），Lin et al.的contact stickers方法提供替代——用物理接触点而非距离误差定义奖励，天然方向敏感
- **分治蒸馏 = BC自蒸馏的理论支撑**：DUCK E47的BC自蒸馏管线（专家rollout筛选→蒸馏）与Lin et al.的分治蒸馏框架同构，但DUCK缺"多专家→一通用"的分治步骤，只做了单教师融合
- **Real-to-Sim自动标定 = CoM gap的解法路径**：DUCK的CoM未标定（docs/141）导致sim直立=真机前倾17°，Lin et al.的4分钟自动标定（采样参数组合+最小化跟踪误差）直接可迁移——只需在真机采集几段平衡站立轨迹，自动优化XML的trunk CoM参数
- **任务感知初始化 = STAND2锚定的理论支撑**：DUCK的STAND2锚定+接管前归位（v4/v5实验定案）与Lin et al.的30秒遥操作初始化同构——从信息丰富的初始状态起步而非随机初始化，改善探索效率

### 对ASC自瞄项目的间接价值

- YOLO检测+RL控制的组合：Lin et al.的视觉策略（第三视角+ego-centric+本体感知三路输入）可参考，但ASC当前用YOLO检测→PD控制的开环链路，RL闭环控制是远期升级路径

## 行动建议

1. **[高优先] Real-to-Sim自动标定落地DUCK**：在pi5采集3-5段平衡站立轨迹（含关节角+IMU），写自动标定脚本采样trunk CoM参数组合，最小化sim轨迹与真机轨迹偏差。直击docs/141 CoM gap未解问题
2. **[中优先] 反向课程理论入skill**：将CO-HER/反向课程的文献依据补进skill `duck-rl-training-cycle`的push课程化铁律，从"教训驱动"升级为"理论+教训双背书"
3. **[低优先] 接触贴纸奖励原型**：在MuJoCo中为DUCK脚底生成接触标记点，实验contact-based奖励替代tracking exp核，验证是否天然解决方向盲问题（E45非对称tracking核的替代方案）
4. **[观望] 分治蒸馏框架**：当前DUCK单任务单教师蒸馏已够用，若未来扩展到站立+行走+抗推多任务统一策略，Lin et al.的分治蒸馏（专家→通用）是直接框架

## 参考文献

1. Lin, T., Sachdev, K., Fan, L., Malik, J., Zhu, Y. Sim-to-Real Reinforcement Learning for Vision-Based Dexterous Manipulation on Humanoids. arXiv:2502.20396, 2025. (CoRL 2025)
2. Wang, J., Qin, Y., Kuang, K., Korkmaz, Y., Gurumoorthy, A., Su, H., Wang, X. CyberDemo: Augmenting Simulated Human Demonstration for Real-World Dexterous Manipulation. CVPR 2024.
3. CO-HER: Curriculum learning for robot manipulation tasks with sparse reward through environment shifts. IRIS UNITN.
4. Fareh, R. et al. Physics-informed reward shaped reinforcement learning for robotic manipulation. 2025. (13 citations)
5. Curriculum Design and Sim2Real Transfer for RL in Robotic Dual-Arm Assembly. MDPI Machines, 12(10), 682, 2024.
