---
title: microduck_rl 分析学习：Sim2Real Playbook 与双足 RL 实战规则
date: 2026-08-31
source: https://github.com/pollen-robotics/microduck_rl
tags: [RL, sim2real, microduck, mjlab, PPO, reward-design, 双足机器人, 课程学习]
---

# microduck_rl 分析学习：Sim2Real Playbook 与双足 RL 实战规则

> **仓库**：[pollen-robotics/microduck_rl](https://github.com/pollen-robotics/microduck_rl)（786★，Apache-2.0，默认分支 develop）
> **定位**：Microduck（~800g、~25cm 双足、14 个 Dynamixel XL330 舵机）的 RL 训练环境，基于 [mjlab](https://github.com/mujocolab/mjlab)（MuJoCo Warp）+ PPO（rsl_rl）。策略在此 50Hz 训练 → ONNX 导出 → `pollen-robotics/microduck` 运行时部署真机。**Sim2Real 转移就是全部意义**：这份 playbook 里的每条约定都是因为破坏它曾产出"viewer 里能跑、硬件上失败"的策略。
> **本次增量**：上游 08-26/27 刚更新——AGENTS.md 被 "make canonical"（PR#4），此前全仓法语注释/plan 批量翻成英文（10+ commits）。本笔记的增量价值在于把这份 canonical playbook 提炼成可复用资产。

## 1. 项目画像

| 维度 | 数据 |
|------|------|
| 规模 | 49.7MB / 432 文件（src+scripts+tests+docs+uv.lock） |
| 任务数 | **17 个环境 cfg**：velocity（行走基础）/ velocity_rollers / velocity_swizzle / velstand / standup / roller_standup / sitstand / roulade / spin / ground_pick / ball_kick / roller_crouch / roller_slope / backlash 变体 / slope_terrain / symmetry / testbench |
| 技术栈 | mjlab（MuJoCo Warp GPU 仿真）+ rsl_rl（PPO）+ uv + wandb + ONNX |
| 训练控制 | 50Hz；simple trick ~1000 iters @4096 envs，gait/curriculum 恢复 4000–6000 |
| 测试 | 154 passed / 1 skipped（CPU，本机实测 23s） |

**架构精髓**：`velocity` 是主行走配方**同时**是共享基座（robot、DR、obs、commands），其他 env 在它上面构建或镜像——这保证了 DR / obs / noise / delays 自动同步。从零搭独立 env 必须手动搬运整个 DR + obs-noise + NaN-guard 栈。

## 2. 六大核心不变量（obs 契约与 obs 家族共享机制）

```
61D actor obs = 48D base proprioception + 13D command block
13D command   = [twist(3), head_pose(4), body_pose(6)]   顺序固定
```

| # | 不变量 | 破坏后果 |
|---|--------|---------|
| 1 | **Obs 61D 全家共享**，unused slot 用 ZERO-PAD（保留 obs term，采样极小区间）而非删除 | 破坏 → policy 不可热切换，walk/stand/trick 不能同一 obs 接口 |
| 2 | **关节布局不硬编码**：被动关节（轮子/backlash 铰链）会 INTERLEAVE。用 `_servo_joint_ids`/`_servo_joint_pos` helper（plain 模型上恒等，其他模型正确） | 写死索引 → 在 roller 模型上把指令发到轮子（真实案例见 `roller_standup_policy_summary.md`：`[0-4, 9-13]` 对无轮模型正确，在轮模型上指到轮子） |
| 3 | **passive_* 命名约定**：所有未驱动关节以此前缀；选择器用 `^(?!passive_).*`；新 passive regex 不能误匹配 backlash 关节（`^passive_.*wheel` 而非 `^passive_.*`） | — |
| 4 | **BAM 执行器**（电压控制的 XL330 模型，摩擦由 actuator 算）：独立 env 必须注册 `expand_bam_friction_fields`；joint-friction DR 要 scale `friction_scale`——`dof_frictionloss` 在 BAM 下被清零，改它是**静默 no-op** | 静默失效的 DR |
| 5 | **Obs 归一化 ON → normalizer 必须 bake 进 ONNX**（`scripts/export.py`）。in-sim play 会自己 apply normalizer，掩盖 bug——绝不手转 checkpoint | 部署 obs 分布错位 = 策略失效 |
| 6 | **策略 UNFILTERED**（训练不加 action 低通）。要加滤波必须同步 runtime flag + 转移测试——trained-with/deployed-without 双向都破坏转移 | — |

## 3. Reward 设计铁律（每条都是"the hard way"学到的）

**符号约定（坑掉 4 个 env）**：mdp.py 有两种 penalty 风格——mjlab 基础 cost 函数返回 ≥0 → 用负权重；自否定函数（`*_penalty`、`*_l1` 返回 ≤0）→ 用**正权重**。给自否定 penalty 配负权重 = 双重否定变成"奖励违反行为"，policy 会 farm 它（butt-hopping、crash-sits）。**铁检查：每 run 的每个 `Episode_Reward/<penalty>` 必须 ≤0**。

| 规则 | 因果 |
|------|------|
| **RL 优化奖励的字面意思** | 每个未定义的自由度都会被 exploit（弹道挥鞭代替翻滚、肩滚代替矢状面、头三脚架代替站立）。把"什么算完成动作"编码进硬状态 gate（支撑接触、朝向轴检查、latch），不是小 penalty nudge |
| **No jackpots** | "到达 X" 奖励必须限速或 slew。提前到达目标态再每步打钱 = 买任意暴力。命令式转换要跟踪 slewed 内部目标（恒速 blend）——超前 ramp 不付费，**慢才是 argmax**。速度上限惩罚只会积成有界成本，必败 |
| **正面奖励绝不门控在坏状态** | policy 会停在最便宜的合格姿势 farm。改用 potential-based shaping（付 Δprogress，如 Δcos(tilt)：上升付费、保持零、不可 farm）。休息任务要审每个正项对每种稳定躺姿（仰/俯/侧）——躺下还保留大部分奖励栈，policy 就躺 |
| **落地姿态任务用单一固定 target** | t=0 就定死（Gaussian + L1 on joints 和 height，宽 std）+ `\|a_z\|` 冲击惩罚 + 双层 upright。**不用 keyframe/waypoint 轨迹**——policy 会 camp 在 waypoint。**路径正是 RL 该发现的东西** |
| **两类正则器分开** | motion-blocker（body_ang_vel、angular_momentum、pose std）惩罚动态动作物理所需的东西 → 动态任务保持 LOW；smoothness（action_rate、joint_torque_rate）阻尼抖动不挡慢大动作 → 可加权，但**在技能习得后再引入**（curriculum 从 ~0 起步）——探索期任何 attempt-tax 都让"什么都不做"胜出 |
| **跨 env 复制正则器比奖励量级不比权重** | PPO 看相对 advantage：同一 action_rate 权重在 4× 更大的正奖励栈下弱 4 倍 |
| **Gaussian std ≈ 还在意的误差** | 太松在小区间没梯度。但收紧前先问误差是策略可逃的还是行为固有的——38% 体重的头走路必然摆动，tight 瞬时 head-tracking std 惩罚了走路到让 policy 站死。**只收可逃部分**：如 1s EMA 上的 L1 收 DC 偏置、放过振荡 |
| **乘法组合优于加法求和** | 加法栈有妥协盆地（靠 lean 拿每项 80%），Gaussian 乘积在任一不足因子处坍塌；但 std 要宽到当前策略可见分，否则梯度不可见 |
| **关节卡硬限** | qpos-side limit-proximity 惩罚加在问题关节上；stock `dof_pos_limits` 只在量程最后 ~7.5% 触发，command-side 惩罚无效（宽 ctrlrange 是刻意的——低 kp 舵机需要 overshoot） |

## 4. Command 与"死权重"陷阱

- 永不非零的 command 输入 → 死权重 forever。每个 slot 从 step 0 就采样小非零区间（即使 reward 权重 0），让输入神经元活着等后续 curriculum
- **零命令行为必须显式训练**（`zero_command_prob` 式精确零采样）：均匀采样几乎永远采不到全零命令，而全零正是部署空闲态
- 稀有但重要的命令区域要显式 bucket（如 `rel_turn_in_place_envs`）：独立均匀采样让 spinning 只占 ~2% experience，永远学不会

## 5. Curriculum 规则

| 要点 | 说明 |
|------|------|
| steps 语义 | `iteration × 24`（`NUM_STEPS_PER_ENV = 24`） |
| 调度通道 | `mdp.reward_weight` 管权重 + 独立 params-curriculum 管 command/event 区间。`reward_weight` 是 **step function 不是插值**——ramp 必须离散成 stage |
| 改 term 的正确方式 | 走 `env.event_manager.get_term_cfg(...)`；**绝不写 `env.cfg.events[...]`**——manager init 时 deepcopy，改 `env.cfg` 是静默 no-op（连强制 spawn state 的 eval 脚本都会踩） |
| 阶段对齐学到的能力 | 当前 slice 没固化前不要硬化 spawn 混合；技能不存在前不要引入 tax。**wandb 指标恰在 curriculum stage 边界下台阶 = pacing 错**，拉长 stage 或延后引入，绝不提前 |
| 逆向课程 spawn | 从动作中部（包括接近完成）开始 spawn，是解决"学会开头学不会最后一英里"的可靠方法——正序 frontier 拿不到 on-policy 数据 |

## 6. 训练判读与"先测量后理论"

- 每 iteration 看：mean reward 上升 **且** episode length 按任务要求表现；每个 penalty 项 ≤0；**主任务项真的在增长**（总奖励可能纯靠正则器涨而 trick 根本没发生）
- `Episode_Reward/<term>` 记的是**加权值**——权重 0 的 term 无论行为如何都读 0，必须对照权重调度解读
- 预算参考：simple episodic trick ~1000 iters @4096 envs；gait 和课程重的恢复 4000–6000
- **Measure before theorizing**：run "失败"时先跑 headless eval 真 checkpoint（per-spawn 电池、end-state 聚类、角速率曲线）再动 reward。历史上的"失败"其实是早期 checkpoint、成功判据把一个行为簇切成两半、pay cap 与实测物理打架
- sim metrics 可以过而视频不过人眼——**看视频且查哪个 geom/axis 接触**
- 如实汇报 rollout 表现（"会滚但 3 次里 1 次脸着地"），不要说"it works!"。用户决定何时够好

## 7. Sim2Real footguns（每次坑掉数周）

**Wheels 按架构分**（aarch64/DGX Spark/GB10 特有）：PyPI 的 linux-aarch64 torch wheel 是 **CPU-only**（`2.9.1+cpu`，`torch.version.cuda is None`）→ `torch.cuda.device_count() == 0` → mjlab 的 `select_gpus()` 索引空列表 → 第 0 次迭代前就 `IndexError`。修法：`[tool.uv.sources]` 只为 aarch64 把 torch 路由到 cu129 index（cu129 匹配 CUDA toolkit warp bundle；x86_64/HF Jobs 留在 PyPI）。**两个静默断点**，都用 `tests/test_aarch64_cuda_torch.py` 锁死：① torch 必须是 DIRECT 依赖（uv 只对 direct deps 应用 `[tool.uv.sources]`——删掉"看似冗余"的 `torch==` pin 会让路由变 no-op）；② pin 必须 `==`，因为 CUDA index 有比 PyPI 新的 build（`>=` 曾静默拖 torch 2.9.1 → 2.13.0）。

> 本机（Jetson Orin）实测对应：`uv sync` 成功且 torch 2.9.1+cu129 正确识别 Orin sm_87——sm_87 兼容性担忧被排除。

| 其他 footgun | 要点 |
|-------------|------|
| fresh `uv sync` 才是 ground truth | HF Jobs 跑的就是 fresh sync；只靠手装本地包能跑的东西在远端必死。pyproject.toml 保持诚实 |
| 物理对齐的限幅 | 25cm 机器人 3.5–5.5 rad/s **自然**翻倒——别用人类速度直觉通过 cap 施加；反暴力压力放在 impact/thrash（`\|a_z\|`、action_rate、support gates），不是旋转速度 |
| IMU DR 零中心 | 它训练对 misalignment 幅值的容忍，**不能**补偿系统性安装偏置（那是 runtime 标定） |
| 真机热切换 ONNX | walk/stand/trick 共享 obs 契约热插拔；上真机前用 `scripts/infer_policy.py` 预演，command-slot 姿势旗标在 twist vx slot——喂全零 = "stand"，看起来像"策略忽略按钮" |

## 8. 新环境工作流（5 步）

1. **选最接近的模板扩展，不从零搭**：locomotion → velocity 配方；以姿态结尾的 episodic trick → standup；双态命令 → sitstand；动态机动 → roulade（读它 cfg docstring——编码了一个 5-run lesson arc）。`make_microduck_velocity*_env_cfg` 让 DR/obs/noise/delays 免费同步
2. **训练前先验证物理假设**（最大时间节省项）：① 目标/rest pose 必须是稳定平衡——从噪声 init 撑 ctrl 3s，查 **TILT 不只 height**（只记 z 的 settle test 会把跌倒状态报成"resting fine"）；② 目标高度从当前模型在 sim 里量（如站立策略下的 trunk z），**不跨模型版本带旧值**（一次 5mm 错的 STAND_Z 让目标变不可能，耗掉数天）
3. 配置约定：`ENABLE_*` toggles + tuned constants 在 cfg 顶部；`make_..._env_cfg(play: bool, rough: bool)` 工厂；`tasks/__init__.py` 注册（含 `_BACKLASH_TASKS` 表）；独立 `RslRl...RunnerCfg` + 不同 `experiment_name`。symmetry mirror-loss 可用（`symmetry.py` 61D 表）——默认关，**绝不用**于非对称任务
4. 写 cfg 测试（`tests/test_*_cfg.py`）：joint 索引在真实模型上解析、reward 权重符号正确、gate 按预期开闭。CPU 可跑，锁死不变量
5. **Smoke test（64 envs × 5 iters）**：构建过、NaN-free、obs 61D、每 reward term 计算、ONNX 导出。**5 轮 × 64 envs 抓 ~95% 配置错误，成本几分钱——绝不做长训练前不跑它**
6. 训练、看 log、预期 2–5 轮 reward-hacking 打地鼠——那很正常

## 9. 本机状态与 DUCK-Pi_5 关联

**microduck-rl-sim mirror 实测**（2026-08-30，详见项目 `docs/local_feasibility.md`）：

| 层级 | 结果 |
|------|------|
| `uv sync` | ✅ torch 2.9.1+cu129 识别 Orin sm_87 |
| `pytest tests/` | ✅ **154 passed / 1 skipped**（23s，CPU） |
| CPU 冒烟训练 | ✅ 16 envs × 2 iters 完整跑通，reward 正常 |
| GPU 冒烟（64 envs） | ❌ warp 内核编译 OK 但 NvMap 分配 OOM（7.4GB 统一内存不足）→ 本机 GPU 训练判死 |

**与 DUCK-Pi_5 的三大适配差距**（项目 README 已列）：舵机 14→15、obs 61D→48D、BAM 执行器模型替换。本 playbook 中最该被 DUCK-Pi_5 直接继承的：

- **obs 家族共享契约** → DUCK-Pi_5 的 M1-M5 策略必须共享 obs 布局（追加不删），否则 M1 到 M5 不能热切换
- **符号约定铁检查**（每个 `Episode_Reward/<penalty>` ≤0）→ 直接抄进 DUCK-Pi_5 训练检查清单
- **先验证物理假设再训练** → DUCK-Pi_5 站稳前先做 noise-init 撑 3s 查 TILT，不要拿 microduck 的 STAND_Z 值（我们 15 舵机 + 不同腿长）
- **aarch64 torch wheel 陷阱** → AutoDL 训练机若走 ARM 实例必须锁 `[tool.uv.sources]`；若用 4090（x86_64）无此问题
- **逆向课程 spawn** → DUCK-Pi_5 若训练"从跌倒中站起"类任务，正序学不会最后一步，用 mid-action spawn

## 10. 沉淀产出

| 产物 | 位置 |
|------|------|
| Skill（可复用资产） | `~/.hermes/skills/robotics/bipedal-rl-sim2real/SKILL.md`（git committed） |
| 上游完整 mirror | `~/uclaw/project/microduck-rl-sim/`（17 个 env cfg + 154 tests 实测通过） |
| 本文 | 学习笔记 |

## 出处

- 上游仓库：https://github.com/pollen-robotics/microduck_rl（develop 分支，pushed 2026-08-30）
- AGENTS.md：上游 canonical playbook 245 行（本地 mirror 与上游 md5 一致 `ca35ed71`）
- 近期演进：PR#4 docs/make-agents-guidance（08-27）、PR#3 法语→英文翻译 revert（08-26）、PR#2 aarch64 CUDA torch fix（08-26）
- 本机验证：`~/uclaw/project/microduck-rl-sim/`（uv sync / pytest 154 通过 / CPU 训练跑通 / GPU OOM 判死）
- 相关笔记：[microduck_rl 本地可行性](~/uclaw/project/microduck-rl-sim/docs/local_feasibility.md)、DUCK-Pi_5 项目 docs/07_vla_phase2.md

→ 相关：[[2026-09-01-机器人路径规划5大主流算法详解.md]]（导航规划五大流派全景）

→ 相关：[[2026-09-01-MuJoCo仿真到Three.js可视化全链路-千问工程还原.md]]（仿真状态流→Web渲染工程层）

→ 相关：[[2026-09-03-MicroduckLab源码精读-MacCPU训练全流程与代码功能详解.md]]（官方栈的 CPU 原型环：奖励五规则+servo-ladder+验证六纪律）
