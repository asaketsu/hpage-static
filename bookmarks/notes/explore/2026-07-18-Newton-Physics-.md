# Newton Physics Engine — 开源机器人物理仿真引擎

> 学习时间：2026-07-18 ｜ 类型：auto-explore ｜ 触发：嗅探队列

## 摘要

Newton 是由 **NVIDIA + Google DeepMind + Disney Research** 联合开发、**Linux Foundation** 托管的**开源 GPU 加速物理引擎**，专为机器人学习与 sim-to-real 设计。基于 NVIDIA Warp + OpenUSD 构建，核心解决"仿真-现实差距（sim-to-real gap）"。2025 年 3 月 GTC 首发预告，2025 年 9 月移交 Linux Foundation，当前 Newton 1.0 已发布，Apache 2.0 许可。

## 关键发现

### 核心定位
- **解决什么**：传统仿真器（PhysX/MuJoCo）在刚性体接触、可变形物（布料/沙子/食物）仿真上保真度不足，Newton 统一刚性体 + 软体 + 布料 + 颗粒物四类求解器
- **为谁服务**：机器人研究者、embodied AI 训练、sim-to-real 策略迁移

### 架构分层
- **底层**：NVIDIA Warp（Python DSL → CUDA kernel，支持自动微分 autodiff）
- **数据层**：OpenUSD（统一机器人/场景资产描述）
- **求解器（Solvers）**：
  - **MuJoCo-Warp**（主力，刚性体，DeepMind 贡献，对标 MJX，RTX 上吞吐大幅提升）
  - **XPBD**（位置约束动力学）
  - **Featherstone**（关节链）
  - **VBD**（布料）
  - **隐式 MPM**（颗粒物/沙）
  - **Camino**（Disney，角色动画）
  - **Neural solver**（神经求解器）

### 核心特性
- **可微物理（differentiable physics）**：梯度可在仿真循环中传播到 PyTorch/JAX，支持梯度优化控制器（JAX interop planned）
- **高加速**：人形仿真 **70x+**，手部操作 **100x+** speedup（相对 MuJoCo CPU 基线）
- **多物理耦合**：刚性体 + MPM 沙子可双向耦合
- **生态兼容**：Isaac Lab（已集成，experimental）、Isaac Sim（规划中）、MuJoCo Playground、Hugging Face

### 验证里程碑
- 已完成 Newton ↔ PhysX 策略互迁移验证
- **Newton 训练的步态策略已部署到 Unitree G1 真机**（sim-to-real 闭环验证）

### 现状（2026-07）
- Isaac Lab 3.0 Beta 在 develop 分支集成 Newton（实验性）
- 主要支持 MuJoCo-Warp 求解器，其他求解器陆续加入
- 支持经典 RL 与平地步态训练，复杂任务持续扩展
- API 仍有 breaking changes，官方支持有限

### 队列中并行学习的 Genesis
嗅探队列同时排了 **Genesis World 1.0**，它是另一个竞争性开源物理引擎（具身智能方向），下次单独学习对比。

## 对工作的价值

1. **embodied AI / 具身智能仿真方向**：如果未来涉及机器人/外骨骼/机械臂的强化学习训练，Newton 是 2026 年值得评估的 sim-to-real 基建，优于直接上 PhysX
2. **GPU 加速范式参考**：Warp 的 "Python DSL → CUDA kernel + autodiff + PyTorch zero-copy" 架构模式，对自研 CUDA 加速任务有借鉴价值
3. **Jetson Orin 平台评估**：Newton 依赖 NVIDIA GPU + CUDA，Jetson Orin Super 理论可跑（实验性已在 DGX Spark 验证），是本地仿真可能的路径
4. **多物理耦合模式**：可变形物 + 刚性体的双向耦合思路，对 robotics 项目中灵巧手操作布料/软物的仿真有价值

## 行动建议

- [ ] **不急上手**：Newton 仍在 Beta，breaking changes 多，生产项目暂观望，等 Isaac Lab 3.0 GA
- [ ] **追踪 Genesis 对比**：完成 Genesis World 1.0 学习后，做 Newton vs Genesis vs Isaac Sim 三者对比笔记
- [ ] **关注 sim-to-real 案例**：G1 真机部署是关键信号，持续追踪 Newton 在 H1/G1/Anymal 等开源机器人的 policy 迁移成功率
- [ ] **Warp 预研**：若 Jetson 项目需要自写 CUDA kernel，可先学 NVIDIA Warp（Newton 的底层，独立可用）

## 参考资料

- 官方主页：https://developer.nvidia.com/newton-physics
- GitHub：https://github.com/newton-physics/newton
- NVIDIA 博客（2025-03-18 发布）：https://developer.nvidia.com/blog/announcing-newton-an-open-source-physics-engine-for-robotics-simulation
- Isaac Lab 集成文档：https://isaac-sim.github.io/IsaacLab/main/source/experimental-features/newton-physics-integration/
- Linux Foundation 公告（2025-09-29）：https://www.linuxfoundation.org/press/linux-foundation-announces-contribution-of-newton
- GTC 2025 Session S72709：MuJoCo-Warp & Newton 深度解读
- Deep Dive 直播（Newton's Classroom）：YouTube NVIDIA Omniverse

## 相关笔记

- [aws-strands-lerobot-embodied-ai](./2026-06-17-aws-strands-lerobot-embodied-ai.md) — 具身AI生态，Newton 为 sim-to-real 提供物理基础
- [人形机器人全身控制RL-MPPI-VLA三路线](./2026-06-26-人形机器人全身控制RL-MPPI-VLA三路线.md) — RL/VLA 训练需高保真物理仿真支撑
- [开源具身智能项目横评-LeRobot-OpenVLA-RT2](./2026-05-21-开源具身智能项目横评-LeRobot-OpenVLA-RT2.md) — 开源 robot learning 栈横评
