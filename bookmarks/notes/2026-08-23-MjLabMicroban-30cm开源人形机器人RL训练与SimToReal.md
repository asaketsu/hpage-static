# MjLab Microban — 30cm 开源人形机器人的 RL 训练环境与 Sim-to-Real 全链路

> **来源**：[Rhoban/mjlab_microban](https://github.com/Rhoban/mjlab_microban)（Apache-2.0）
> **作者**：Rhoban 团队（法国波尔多机器人实验室）· Marc Duclusaud
> **机器人**：[Microban](https://github.com/MarcDcls/microban) — 30cm 紧凑型低成本全开源人形机器人
> **框架**：[MjLab](https://github.com/mujocolab/mjlab)（MuJoCo 并行 RL 框架）
> **记录日期**：2026-08-23
> **项目**：`~/uclaw/project/mjlab-microban-rl/`

**标签**：#Microban #人形机器人 #强化学习 #SimToReal #MuJoCo #MjLab

---

### 7 模块索引（本报告内容映射）

| 模块 | 对应章节 | 说明 |
|------|---------|------|
| tag 标签 | 头部标签行 | 6 个标签 |
| 出处 | 头部出处行 | GitHub + Rhoban/Microban 生态 |
| 内容整理 | 第一~四章 | 任务定义/使用流程/训练/导出部署 |
| 查询拓展 | 第五章 | BAM 执行器建模 + 域随机化 |
| 归纳总结 | 第六章 | 技术栈分层 + sim-to-real 三支柱 |
| 趋势判断 | 第七章 | 2 条预测 |
| 关联分析 | 第八章 | 与机器人项目/具身智能笔记交叉 |
| 拓展应用推荐 | 第九章 | 可运行路线 + 借鉴点 |
| 指南分析 | 第十章 | 工程质量评估 |

---

## 一句话总纲

> **Rhoban 用 MjLab（MuJoCo GPU 并行）给 30cm 开源小人形 Microban 训速度跟踪策略——4096 并行环境训练，域随机化 + BAM 执行器精细建模（延迟/摩擦/压降/电流限幅）攻克 sim-to-real，已成功迁移到真实机器人。**

---

## 一、内容详细整理

### 1.1 项目定位

**Microban**：30cm 紧凑型、低成本、全开源的小人形机器人（[独立仓库](https://github.com/MarcDcls/microban)，可自建）。

**本仓库**：Microban 的 RL 训练环境——基于 MjLab 框架（MuJoCo 的 GPU 并行 RL 训练框架）。

**当前实现的任务**：**速度控制（velocity control）**——机器人跟随目标线速度/角速度，同时抵抗外部扰动。

### 1.2 安装与使用（预训练 agent）

```bash
# 需要 uv 包管理器
git clone <repo> && uv sync

# GPU 上运行预训练速度策略（随机速度指令）
uv run play Mjlab-Velocity-Microban --checkpoint-file src/mjlab_microban/agents/velocity.pt
```

**仿真交互**：
- 蓝色箭头 = 线速度指令；绿色垂直箭头 = 角速度指令
- **推机器人测试**：双击躯干 → 按住左 Ctrl + 右键拖拽施加外力（扰动恢复测试）

### 1.3 训练自己的 agent

**环境配置**：`src/mjlab_microban/tasks/microban_velocity_env_cfg.py`

```bash
# 训练前先用零策略/随机策略验证环境
uv run play Mjlab-Velocity-Microban --agent zero
uv run play Mjlab-Velocity-Microban --agent random

# 正式训练：4096 并行环境
uv run train Mjlab-Velocity-Microban --env.scene.num-envs 4096

# 回放 checkpoint
uv run play Mjlab-Velocity-Microban --checkpoint-file logs/rsl_rl/mjlab_microban_velocity/[date]/model_[number].pt

# 从 wandb 回放
uv run play Mjlab-Velocity-Microban --wandb-run-path [path]
```

**训练器**：RSL-RL（日志路径 `logs/rsl_rl/`）——Isaac Lab 系的标准 PPO 训练器。

### 1.4 Sim-to-Real 迁移（本项目最大亮点）

> "真实机器人迁移始终是挑战（sim-to-real gap），但本仓库训练的策略**已成功迁移到真实 Microban**。"

**成功的两大支柱**：

1. **域随机化（Domain Randomization）**
2. **执行器精细建模（用 [BAM](https://github.com/Rhoban/bam) 库）**：
   - 延迟（delays）
   - 摩擦（friction）
   - 压降（voltage drop）
   - 电流限幅（current clipping）

**实证视频**：https://youtu.be/1pnFrT_jfXQ

### 1.5 ONNX 导出

```bash
# 训练时自动生成最新 checkpoint 的 ONNX
# 手动导出特定 checkpoint：
uv run python src/mjlab_microban/scripts/export_onnx.py --checkpoint [path]
```

部署链路：PyTorch checkpoint → ONNX → 机载推理。

---

## 二、查询拓展

### 2.1 BAM 库：执行器建模的关键

Rhoban 自家的 [BAM](https://github.com/Rhoban/bam)（Biped Actuation Model？）库——把真实电机的不完美（延迟/摩擦/压降/限流）建模进仿真：

| 现象 | 仿真若忽略的后果 |
|------|------------------|
| 通信/控制延迟 | 真机响应滞后 → 策略在真机上震荡 |
| 关节摩擦 | 仿真过强/过弱 → 步态能量特征失真 |
| 电池压降 | 高负载扭矩骤降 → 仿真策略依赖不可达的扭矩 |
| 电流限幅 | 峰值扭矩被削 → 策略依赖瞬间大扭矩会摔 |

**核心理念**：sim-to-real gap 的主要来源不是场景渲染，而是**执行器物理**——把执行器建准比域随机化更根本。

### 2.2 MjLab vs Isaac Lab

| 维度 | MjLab | Isaac Lab |
|------|-------|-----------|
| 物理引擎 | MuJoCo（MJX GPU 后端） | PhysX GPU |
| 开源程度 | 全开源 | NVIDIA 生态（开源但绑定） |
| 许可 | Apache | BSD-3 |
| 硬件要求 | GPU（MJX） | RTX GPU |
| 训练器 | RSL-RL 兼容 | RSL-RL |
| 生态 | 新兴（mujocolab 组织） | 成熟（NVIDIA 背书） |

MjLab 是 MuJoco 社区对 Isaac Lab 的回应——GPU 并行 + MuJoCo 的接触动力学质量。

### 2.3 Microban 的生态位

30cm 级开源小人形对标：

| 机器人 | 高度 | 特点 |
|--------|------|------|
| Microban | 30cm | 全开源/低成本/Rhoban（法国科研） |
| Bertrand | 类似量级 | 国内开源社区 |
| Darwin-OP | 45cm | 老牌（ROBOTIS，约 $12k） |
| Unitree G1 | 130cm | 商用（$16k 起） |

Microban 的卖点：**"affordable" + 全开源（硬件+软件+训练）**——个人可复现的完整 sim-to-real 闭环标本。

---

## 三、归纳总结

### 3.1 技术栈分层

```
┌─ 硬件层：Microban 30cm 人形（开源 BOM）
├─ 物理仿真：MuJoCo MJX（GPU 并行）
├─ RL 框架：MjLab（环境定义 + 任务配置）
├─ 训练器：RSL-RL（PPO，4096 并行 env）
├─ 执行器建模：BAM（延迟/摩擦/压降/限流）
├─ 鲁棒化：Domain Randomization
└─ 部署：ONNX 导出 → 机载推理
```

### 3.2 Sim-to-Real 三支柱

1. **执行器建模 > 域随机化**（BAM 把物理不完美建准）
2. **扰动测试内建**（仿真中推机器人验证恢复能力）
3. **4096 并行采样效率**（GPU 并行让域随机化的采样成本可承受）

---

## 四、趋势判断

### 趋势 1：开源小人形 + GPU 并行 RL = 个人可复现的具身智能时代

> 依据：Microban（硬件全开源）+ MjLab（仿真框架）+ BAM（执行器建模）全链路 Apache/MIT——单个研究者用一台 GPU 工作站可复现顶会级 sim-to-real。类比 2012 年 AlexNet 之于 CV。

### 趋势 2：执行器精细建模成为 sim-to-real 的竞争焦点

> 依据：本项目明示 sim-to-real 成功归因于"domain randomization + well-tuned actuator modelisation"——后者（BAM 的延迟/摩擦/压降/限流）是更被低估的功臣。机器人公司间的差距越来越取决于对自家执行器的建模精度。

---

## 五、关联分析

### 5.1 与本机机器人项目的关联

本机已有的机器人方向项目（servo-arm-control ESP32 机械臂、dual-mcu-robot-architecture、embodied-ai-control）——Microban 代表**动态运动控制**的进阶形态（双足步态 vs 机械臂/轮式）。`robotics-project-setup` skill 的标准流程可直接套用于 clone 此仓库。

### 5.2 与 [2026-08-21-KimiK3-BlenderMCP-能看能改的3D场景Agent工作流.md](2026-08-21-KimiK3-BlenderMCP-能看能改的3D场景Agent工作流.md) 的关联

两者都是"仿真环境 + AI 迭代"：Kimi+Blender 是视觉反馈闭环（截图→修改），Microban+MjLab 是物理反馈闭环（rollout→reward→更新）。vision-in-the-loop 与 RL 的本质差异：前者优化离散产物，后者优化连续控制策略。

### 5.3 与 [2026-08-21-EnvHarness环境脚手架-环境与Agent共进化的Google新范式.md](2026-08-21-EnvHarness环境脚手架-环境与Agent共进化的Google新范式.md) 的关联

EnvHarness 的"环境侧进化"思想在机器人 RL 的对应物就是**域随机化课程**——环境（物理参数分布）根据策略表现动态调整。BAM 的执行器建模则是"环境保真度"的具身版本。

### 5.4 与 embodied-ai-control skill 的关联

该 skill 讲"大脑-小脑分离设计 + 多层安全级联"——Microban 的速度策略是小脑层（反射级控制），大脑层（任务规划）是缺失的。完整架构 = Microban 小脑 + LLM 大脑（本机 Hermes 可扮演）。

---

## 六、拓展应用推荐

### 6.1 可运行路线（分阶段）

**阶段 0（零成本，仿真 only）**：
```bash
# 本机 Jetson 或任意 GPU 机器
git clone https://github.com/Rhoban/mjlab_microban && cd mjlab_microban
uv sync
uv run play Mjlab-Velocity-Microban --checkpoint-file src/mjlab_microban/agents/velocity.pt
```
⚠️ 注意：本机 Jetson Orin 8GB 可跑 MJX 仿真回放，但 4096 并行训练需更大显存——训练留给 A100 局域网池或云。

**阶段 1（环境改造实验）**：
- 修改 `microban_velocity_env_cfg.py` 的奖励/观测/指令分布
- 用 zero/random agent 验证环境正确性（README 推荐的流程）

**阶段 2（自训练）**：
- 小规模并行（`--num-envs 256`）在 Jetson 验证训练管线
- 大规模（4096）转到 A100 池

### 6.2 值得借鉴的工程实践

1. **训练前 zero/random agent 验证**——本机嵌入式项目可借鉴：先跑空策略确认环境接口正确
2. **扰动测试内建到 play 命令**（Ctrl+右键施力）——验收不只看正常路径
3. **ONNX 导出脚本独立成 scripts/**——训练产物到部署产物的标准化链路
4. **BAM 执行器建模清单**（延迟/摩擦/压降/限流）——任何伺服系统仿真都该检查这四项

### 6.3 学习方向

- MjLab 框架文档（环境定义 DSL）
- BAM 库源码（执行器建模的具体实现）
- RSL-RL（PPO 变体在机器人上的配置经验）
- Microban 硬件仓库（BOM/结构/电控——若未来自制）

---

## 七、指南分析

### 7.1 工程质量

- **README 简洁完整**：安装→播放→训练→迁移→导出，全链路命令可复制
- **sim-to-real 诚实**：明示 gap 挑战并给出两大支柱归因（域随机化+BAM）
- **预训练权重附带**：`agents/velocity.pt` 可直接体验
- **扰动测试交互**：play 时可推机器人——验证鲁棒性的贴心设计

### 7.2 局限

- 目前只有速度跟踪一个任务（转向/地形/操作未覆盖）
- Star/社区规模小（新仓库），文档深度有限
- 硬件 BOM 成本未在 README 披露（需去 Microban 仓库查）
- 训练硬件门槛（4096 env 需要 RTX 级 GPU）

---

## 八、金句摘录

> "The transfer on the real robot is always a challenge due to the sim-to-real gap. However... due to a combination of domain randomization and a well-tuned modelisation of the actuators (delays, friction, voltage drop, current clipping, etc.)."

> "a compact, low-cost, fully open-source small humanoid robot"——个人可复现的完整具身智能标本

---

## 九、行动启示

- **项目骨架已建**：`~/uclaw/project/mjlab-microban-rl/`
- **Jetson 可跑阶段 0**：仿真回放预训练策略（8GB 显存可承受），训练任务按用户铁律留给其他机器
- **BAM 四项检查清单进嵌入式 skill**：延迟/摩擦/压降/限流——servo 仿真项目都该过一遍
- **zero/random agent 验证流程借鉴**：embodied 项目脚手架的 dry-run 环节可具象化为这个模式

---

> **延伸阅读**：
> - 仓库：https://github.com/Rhoban/mjlab_microban
> - Microban 硬件：https://github.com/MarcDcls/microban
> - MjLab 框架：https://github.com/mujocolab/mjlab
> - BAM 执行器建模：https://github.com/Rhoban/bam
> - 真机迁移视频：https://youtu.be/1pnFrT_jfXQ

## 相关笔记

- [Microban与2026双足RL前沿-低成本平台同构与重训校准](./2026-09-01-Microban与2026双足RL前沿-低成本平台同构与重训校准.md) — 同主题前沿跟踪与重训校准
- [Microduck开源双足机器鸭全栈拆解](./2026-08-28-Microduck开源双足机器鸭-Rust微服务与SimToReal全栈拆解.md) — 30cm 级双足平台工程对照