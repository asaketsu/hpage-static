# Newton Physics Engine — 机器人仿真的新纪元

> 嗅探学习笔记 · 2026-07-19 · auto-explore

## 摘要

Newton 是由 **Disney Research + Google DeepMind + NVIDIA** 三方联合发起、托管于 **Linux Foundation** 的开源 GPU 加速物理仿真引擎，2025 年 3 月 GTC 发布，2026 年 7 月已迭代到 **v1.4.0**。它构建于 NVIDIA Warp 之上，以 **MuJoCo Warp** 为后端核心，面向机器人学家与仿真研究者，强调可微性（differentiability）、OpenUSD 支持、模块化与可扩展性。GitHub 5.2k stars / 600 forks。

项目地址：https://github.com/newton-physics/newton

## 关键发现

### 1. 定位：补齐现有引擎的四大短板
- MuJoCo、PhysX、Isaac Sim 等在 **精度、实时自适应、软体仿真、AI 集成** 上各有缺陷
- Newton 直接瞄准这些痛点，做"AI 原生"的物理引擎

### 2. 核心技术栈
- **底座**：NVIDIA Warp（Python DSL → CUDA，autodiff，零拷贝与 PyTorch/JAX 互操作）
- **主后端**：MuJoCo Warp（DeepMind 出品，在 RTX GPU 上对 MJX 有显著吞吐增益）
- **数据格式**：OpenUSD（业界标准场景描述），配套 Newton USD Schema 开发中

### 3. Solver 矩阵（亮点）
- MuJoCo-Warp（刚体）
- XPBD（粒子/约束）
- Featherstone（铰接多体解析）
- VBD（布料）
- 隐式 MPM（颗粒物/沙/雪）
- **Camino**（Disney Research，娱乐机器人专用）
- Neural solver（学习增强）

支持**混合耦合**：刚体+布料+沙一次性仿真，1-way / 2-way coupling 可选。

### 4. 可微物理 → 端到端策略学习
- Warp 的自动微分能力，可在仿真循环内计算梯度并喂给 PyTorch
- 意味着可以在仿真器内做基于梯度的控制器优化，而不是只用 RL 黑盒采样

### 5. 生态对接
- **Isaac Lab**：实验分支已集成，可在 DGX Spark 上跑
- **Isaac Sim**：计划作为额外物理后端接入
- **MuJoCo Playground**：兼容
- 支持 URDF / MJCF / USD 三种资产导入

### 6. 路线图
- 当前 Beta → Beta-2 → GA
- Camino 正走在 GA 路径上
- 与 Disney BDX 机器人（星球大战仿生机器人）形成闭环验证

## 对工作的价值

1. **具身智能/机器人项目**：若做 ESP32+STM32 双 MCU 机械臂或仿生机器人，Newton 可作为比 Gazebo/PyBullet 更现代的仿真后端，且 GPU 加速能跑大规模并行训练
2. **合成数据策略**：Newton 的核心卖点之一是"real ↔ synthetic ↔ internet-scale"数据闭环，这与本项目做 LLM Agent 训练数据的思路同源
3. **Jetson Orin 适配性**：Warp 已支持 aarch64 Linux，Jetson Orin 理论可作边缘端推理仿真宿主，但需验证 CUDA 12 / Maxwell+ 限制
4. **学习架构参考**：Newton 的"模块化 + 统一 API + 可微"设计哲学，对自研 Skill 编排架构有借鉴意义

## 行动建议

- **短期（本周）**：克隆仓库，跑 `python -m newton.examples basic_pendulum` 验证 Jetson Orin 是否可运行
- **中期**：关注 Camino solver —— Disney 在娱乐机器人上的工程经验对仿生表情/动作项目极具参考价值
- **长期**：若启动具身智能项目，优先评估 Newton + Isaac Lab 作为仿真底座，替代传统 PyBullet 方案
- **知识沉淀**：可吸收其"不同iable physics"思路到现有 `embodied-ai-control` Skill 中

## 参考资料

- 官方仓库：https://github.com/newton-physics/newton
- GTC25 Session S72709：MuJoCo-Warp 与 Newton 联合发布
- NVIDIA Omniverse 直播：Newton's Classroom（2025-10-23）
- 文档：https://newton-physics.github.io/newton/


## 相关笔记

- [Newton Physics Engine 开源引擎（07-18）](./2026-07-18-Newton-Physics-.md) — 同主题前序笔记，基础架构解读
- [Genesis World 1.0 评估优先范式（07-18）](./2026-07-18-Genesis-World-1.0.md) — 与 Newton 并列的机器人仿真引擎对比
- [Genesis World 1.0 补充篇（07-18）](./2026-07-18-Genesis-World-1.0-.md) — Genesis 引擎细节深化
- [AWS Strands 与 LeRobot 具身智能（06-17）](./2026-06-17-aws-strands-lerobot-embodied-ai.md) — 具身智能上游框架，物理引擎是其基础
- [人形机器人全身控制 RL/MPPI/VLA（06-26）](./2026-06-26-人形机器人全身控制RL-MPPI-VLA三路线.md) — sim-to-real 需要高保真物理引擎支撑
