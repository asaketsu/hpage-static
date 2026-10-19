# MuJoCo 入门：Ubuntu 安装、机械臂模型与末端位置追踪

> **来源**：微信公众号「机器人开发圈」（作者：LitchiCheng，原文：EEWorld 论坛）
> **原文链接**：https://mp.weixin.qq.com/s/u4oRfbf7ZIUNXpWSTE1ddg
> **记录日期**：2026-06-26

---

## 一、文章概要

MuJoCo（Multi-Joint dynamics with Contact）是 DeepMind 开发的高性能物理仿真引擎，核心功能包括动力学模拟、接触力建模及多关节系统仿真。本文是实战入门教程，涵盖：**Ubuntu 安装 MuJoCo 3.3.0 → 使用 mujoco_menagerie 获取机械臂模型 → Python + GLFW 实现末端位置实时追踪 → 关节空间运动控制**。

---

## 二、内容详细整理

### 2.1 Ubuntu 安装 MuJoCo 3.3.0

**安装步骤**：

```bash
mkdir MuJoCoBin
cd MuJoCoBin
wget https://github.com/google-deepmind/mujoco/releases/download/3.3.0/mujoco-3.3.0-linux-x86_64.tar.gz
tar xvzf mujoco-3.3.0-linux-x86_64.tar.gz

# 导入环境变量
echo "export PATH=$PATH:/home/dar/MuJoCoBin/mujoco-3.3.0/bin" >> ~/.bashrc
source ~/.bashrc

# 测试
simulate ~/MuJoCoBin/mujoco-3.3.0/model/humanoid/humanoid.xml
```

**关键要点**：
- MuJoCo 3.3.0 是 DeepMind 开源版本（2024年）
- 解压即用，无需编译
- `simulate` 命令可直接加载 XML 模型文件运行仿真

### 2.2 mujoco_menagerie：高质量模型集合

**获取模型**：

```bash
git clone git@github.com:google-deepmind/mujoco_menagerie.git
# 约 346MB，含 Franka Panda、UR、SO-ARM100、ALOHA 等
```

**可用模型**：

| 模型 | 路径 | 说明 |
|------|------|------|
| Franka Panda | `mujoco_menagerie/franka_emika_panda/scene.xml` | 7-DOF 协作机械臂 |
| SO-ARM100 | `mujoco_menagerie/trs_so_arm100/scene.xml` | 100kg 负载机械臂 |
| ALOHA | `mujoco_menagerie/aloha/scene.xml` | 双机械臂操作平台 |
| UR 系列 | `mujoco_menagerie/universal_robots_*` | Universal Robots 机械臂 |

### 2.3 末端位置实时追踪（Python + GLFW）

**核心代码结构**：

```python
import mujoco, numpy as np, glfw

# 加载模型
model = mujoco.MjModel.from_xml_path('scene.xml')
data = mujoco.MjData(model)

# GLFW 初始化
glfw.init()
window = glfw.create_window(1200, 900, 'Panda Arm Control', None, None)

# 渲染初始化
cam = mujoco.MjvCamera()
opt = mujoco.MjvOption()
mujoco.mjv_defaultCamera(cam)
mujoco.mjv_defaultOption(opt)
pert = mujoco.MjvPerturb()
con = mujoco.MjrContext(model, mujoco.mjtFontScale.mjFONTSCALE_150.value)
scene = mujoco.MjvScene(model, maxgeom=10000)

# 查找末端执行器
end_effector_id = mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_BODY, 'hand')

# 主循环
while not glfw.window_should_close(window):
    end_effector_pos = data.body(end_effector_id).xpos  # 世界坐标系位置
    print(f"End effector position: {end_effector_pos}")
    mujoco.mj_step(model, data)
    mujoco.mjv_updateScene(model, data, opt, pert, cam, mujoco.mjtCatBit.mjCAT_ALL.value, scene)
    mujoco.mjr_render(viewport, scene, con)
    glfw.swap_buffers(window)
    glfw.poll_events()
```

**核心 API 说明**：

| API | 功能 |
|-----|------|
| `MjModel.from_xml_path()` | 从 XML 加载模型 |
| `MjData(model)` | 创建动态数据实例 |
| `mj_name2id()` | 按名称查找 body/joint 的 ID |
| `data.body(id).xpos` | 获取 body 在世界坐标系的位置 |
| `mj_step()` | 执行一步仿真 |
| `mjv_updateScene()` | 更新渲染场景 |
| `mjr_render()` | 渲染到视口 |

### 2.4 关节空间运动控制

**核心代码**：

```python
# 获取初始关节角度
initial_q = data.qpos[:7].copy()

# 控制某个关节
initial_q[0] += 0.1
initial_q[0] = limit_angle(initial_q[0])  # 归一到 ±π 内

# 设置关节目标位置
data.qpos[:7] = new_q
mujoco.mj_step(model, data)
```

**关键约束**：关节角度需归一到 ±180°（±π 弧度）内，否则 MuJoCo 会报错（DOF 异常）。

**角度归一化函数**：

```python
def limit_angle(angle):
    while angle > np.pi:
        angle -= 2 * np.pi
    while angle < -np.pi:
        angle += 2 * np.pi
    return angle
```

### 2.5 依赖安装

```bash
pip3 install mujoco glfw
```

**说明**：`mujoco_py` 已废弃，最新版使用 `mujoco` Python 包。

---

## 三、查询拓展

### 3.1 MuJoCo 版本演进

| 版本 | 时间 | 关键变化 |
|------|------|---------|
| MuJoCo 2.x | 2019-2021 | 闭源，学术免费许可 |
| MuJoCo 3.0 | 2024 | DeepMind 开源，支持 GPU 加速 |
| MuJoCo 3.1 | 2024 | 改进渲染质量，新增传感器 |
| MuJoCo 3.3.0 | 2025 | 当前最新，修复稳定性问题 |

### 3.2 MuJoCo vs mujoco_py

| 对比项 | mujoco_py | mujoco（官方） |
|--------|-----------|---------------|
| 维护状态 | 已废弃 | 官方维护 |
| Python 版本 | 仅 Python 3.6-3.8 | Python 3.8+ |
| MuJoCo 版本 | 2.x | 3.x |
| 安装方式 | 编译安装 | pip install |
| API 风格 | Cython 绑定 | 原生 Python 绑定 |

### 3.3 MuJoCo 与强化学习的结合

MuJoCo 在 RL 领域的生态：

| 框架 | 说明 |
|------|------|
| RLlib | Ray 的 RL 库，原生支持 MuJoCo |
| Stable-Baselines3 | 常用 RL 库，需 mujoco-py 或 gym |
| Gymnasium | OpenAI Gym 继任者，含 MuJoCo 环境 |
| Brax | Google 的 JAX 版 MuJoCo，GPU 加速 |

### 3.4 MuJoCo 与用户已有笔记的交叉

- **上一篇（仿真工具选型）**：MuJoCo 定位为"动力学/控制/RL 研究工具"，本文是具体实践
- **上上一篇（主动SLAM）**：主动SLAM的MPC预测需要仿真环境验证，MuJoCo 是合适选择
- **再上一篇（无图智驾不用SLAM）**：BEV+Occ 的训练需要合成数据，MuJoCo 可生成物理仿真数据

---

## 四、归纳总结

### 4.1 MuJoCo 开发流程

```
1. 安装 MuJoCo 3.x → 解压即用
2. 获取模型 → mujoco_menagerie 或自建 XML
3. Python 加载 → MjModel.from_xml_path()
4. 初始化渲染 → GLFW + MjvCamera + MjvScene
5. 主循环 → mj_step() + mjv_updateScene() + mjr_render()
6. 控制 → 关节空间（qpos）或末端位置（xpos）
```

### 4.2 MuJoCo 核心数据结构

```
MjModel（模型）
  ├─ nbody：body 数量
  ├─ njnt：joint 数量
  ├─ nq：广义坐标数量
  ├─ nv：自由度数量
  └─ XML 描述文件（scene.xml）

MjData（数据）
  ├─ qpos：广义坐标（关节位置）
  ├─ qvel：广义速度（关节速度）
  ├─ xpos：body 世界坐标
  ├─ cvel：body 速度
  └─ 仿真状态（每步更新）
```

### 4.3 两种控制方式对比

| 控制方式 | 接口 | 适用场景 |
|---------|------|---------|
| 关节空间控制 | `data.qpos[:n] = target` | 已知关节目标位置 |
| 末端位置控制 | 通过逆运动学计算 qpos | 已知末端目标位置 |

---

## 五、趋势判断

### 5.1 MuJoCo 3.x 正在成为机器人仿真新标准

DeepMind 开源 MuJoCo 3.x 后，其 GPU 加速能力和 Python 原生绑定使其在 RL 和机器人控制领域快速普及。预测 2026-2027 年 MuJoCo 3.x 将逐步取代 mujoco_py 和 Gym 中的 MuJoCo 环境。

### 5.2 mujoco_menagerie 将成为机器人仿真的"标准模型库"

类似 ROS 的 `ros-industrial`，mujoco_menagerie 提供高质量、经过验证的机器人模型，减少开发者自行建模的负担。预测未来会有更多厂商贡献模型。

### 5.3 MuJoCo + JAX（Brax）是 RL 训练的最优组合

Brax 是 MuJoCo 的 JAX 实现，支持 GPU 并行仿真，训练速度比传统 MuJoCo 快 10-100 倍。对于大规模 RL 训练，Brax 是更优选择。

---

## 六、关联分析

### 6.1 与用户机器人项目的映射

| 用户项目 | MuJoCo 应用 | 说明 |
|---------|------------|------|
| 双轮腿式机器人 | 仿真平衡控制策略 | 用 MuJoCo 验证 PID/RL 平衡算法 |
| 舵机机械臂 | 仿真 6-DOF 逆运动学 | 用 MuJoCo 验证 DH 逆解算法 |
| Jetson Orin 边缘推理 | RL 训练环境 | 用 MuJoCo 训练控制策略后部署到 Jetson |

### 6.2 与六篇笔记的完整认知链

```
① 西门子工业AI（宏观范式）→ Physical AI
② 200线激光雷达SLAM（传感器层）→ 高线束踩坑
③ 无图智驾不用SLAM（算法路线）→ BEV+Occ替代
④ 主动SLAM三大核心（理论层）→ 主动决策
⑤ 仿真工具选型（工程层）→ 四工具各司其职
⑥ MuJoCo入门（本篇 · 实践层）→ 具体安装和使用
```

**关键交叉**：⑤中 MuJoCo 定位为"动力学/控制/RL 研究工具"，⑥是⑤的具体实践——从选型到安装的完整闭环。

### 6.3 对 Hermes Agent 的启发

- **MuJoCo 思维**：Agent 的"仿真"能力——在虚拟环境中测试决策，而非直接在真实环境试错
- **mujoco_menagerie 思维**：Agent 需要"标准模型库"——预置的机器人/工具模型，减少从零建模的负担
- **实时追踪思维**：Agent 需要"状态监控"——类似末端位置追踪，实时监控任务执行状态

---

## 七、金句摘录

1. **「MuJoCo（Multi-Joint dynamics with Contact）是一款用于机器人学、生物力学等领域的高性能物理仿真引擎。」** — MuJoCo 定义
2. **「mujoco_py 这个库很老了，最新的版本可以通过 mujoco 的 python 库。」** — 版本更新提醒
3. **「关键代码就一行：data.qpos[:7] = new_q」** — MuJoCo 控制的简洁性
4. **「自增的量不能太大，不然控制台会输出 DOF 0 不对劲」** — 关节角度约束的实践教训

---

## 八、行动启示

| 启示 | 具体行动 |
|------|---------|
| MuJoCo 安装简单 | 在 Jetson Orin 上安装 MuJoCo 3.x，用于机器人仿真 |
| mujoco_menagerie 是标准模型库 | 克隆 mujoco_menagerie，获取 Franka Panda 等模型 |
| 关节角度需归一化 | 控制代码中加入 limit_angle() 函数，防止 DOF 异常 |
| MuJoCo + RL 是黄金组合 | 用 MuJoCo 训练平衡控制策略，部署到双轮腿机器人 |
| 仿真→真机闭环 | 在 MuJoCo 中验证算法 → 部署到真机 → 真机数据反馈到仿真 |

---

## 相关笔记

- [2026-06-26-四种机器人仿真工具选型指南](./2026-06-26-四种机器人仿真工具选型指南.md)
- [2026-06-26-主动SLAM三大核心思想入门](./2026-06-26-主动SLAM三大核心思想入门.md)
- [2026-06-26-无图智驾为何不用SLAM建立局部语义地图](./2026-06-26-无图智驾为何不用SLAM建立局部语义地图.md)
