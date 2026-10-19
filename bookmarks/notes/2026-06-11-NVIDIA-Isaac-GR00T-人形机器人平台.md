# NVIDIA 发布 Isaac GR00T 人形机器人平台

- **日期**：2026年3月16日 (GTC 2026)
- **来源链接**：[NVIDIA Newsroom](https://nvidianews.nvidia.com/)

---

## 核心要点
* **生成式物理世界模拟**：推出 Cosmos 3 首个统一视觉动作世界基础模型与医疗版 Cosmos-H，让机器人具备物理世界推理能力。
* **物理引擎与仿真生态演进**：更新 Isaac Lab 3.0，深度融合 Newton 物理引擎 1.0，突破高难度灵巧操作与多物理系统验证。
* **双模并行推进**：GR00T 基础模型形成“商业落地的通用技能 (N1.7)”与“极限性能探索的世界动作模型 (N2)”双轨布局，N2 在 VLA 任务中成功率翻倍。
* **算力硬件全场景覆盖**：从边缘实时模块、车规级/机器人级 Thor 平台到高功能安全 IGX，提供从仿真到部署的闭环算力。

---

## 技术架构拆解
1. **应用 & 技能层 (GR00T Foundation Models)**
   * **GR00T N1.7** (Early Access)：面向商业落地，开箱即用的通用机器人控制技能。
   * **GR00T N2** (Preview)：新一代世界动作模型架构（WAM），基于 DreamZero 架构，相比主流 VLA 模型成功率提升 2 倍以上。
2. **仿真 & 训练层 (Isaac Simulation & Learning Workspace)**
   * **Isaac Lab 3.0**：基于 Newton 1.0 物理引擎及 PhysX SDK，提供极速的多物理仿真和灵巧操作训练环境。
   * **Isaac Sim**：用于合成数据生成、数字孪生构建以及生成式世界模型的闭环验证。
3. **物理世界模型层 (Cosmos World Models)**
   * **Cosmos 3**：连接视觉与物理动作的底层基座，实现统一合成世界生成和视觉推理。
   * **Cosmos-H**：针对医疗与手术机器人定制的专用仿真模型。
4. **硬件计算底座 (Jetson / IGX Compute Hardware)**
   * **Jetson Thor**：整机计算大脑，提供从仿真到物理机部署的端端芯片算力支持。
   * **Jetson Modules**：提供边缘低功耗实时 与 AI 推理能力。
   * **IGX Thor**：为高门槛医疗机器人场景提供工业级/医疗级功能安全保障。

---

## 生态合作方分类

### 1. 工业制造与双臂装配
* **FANUC / ABB / YASKAWA**：工业自动化集成。
* **KUKA**：推进虚拟调试技术（Virtual Commissioning）。
* **Skild AI + Foxconn**：部署于 Blackwell 产线的双臂装配系统。
* **PTC**：开发 CAD-to-OpenUSD 的桥接工具链。
* **WORKR + ABB**：实现免编程机器人快速部署（No-code).

### 2. 人形机器人本体厂商
* **海外头部**：1X、Agility Robotics、Boston Dynamics、Figure。
* **中国厂商**：宇树科技 (Unitree)、智元机器人 (AGIBOT) 等。

### 3. 物流仓储与自动驾驶
* **KION + Accenture + GXO**：智能自主叉车车队协同作业。

### 4. 医疗健康与辅助手术
* **CMR Surgical**：用于 Versius 手术系统的仿真与控制。
* **Johnson & Johnson**：探索智能手术辅助技术。

### 5. 中国生态企业 (特写)
* **宇树科技 (Unitree)**、**智元机器人 (AGIBOT)**、**加速进化/逐际微光 (Humanoid/LimX)**、**光轮智能 (Lightwheel)**

---

## 个人注释区
> ✍️ *（待补充：关于 GR00T-N2 的评测表现、行业装配线的具体反馈等）*


## 相关笔记
- [NVIDIA Isaac Sim 机械臂仿真全流程指南](2026-05-22-NVIDIA-Isaac-Sim机械臂仿真全流程指南.md) (关键词: isaac, nvidia)
