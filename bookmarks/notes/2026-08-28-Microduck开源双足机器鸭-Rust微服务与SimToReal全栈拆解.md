# Microduck 开源双足机器鸭 — 800g 具身智能开发平台的软硬件全栈拆解

> **来源**：[@tspy（yishan）X 帖子](https://x.com/tspy/status/2093222346501107739)
> **原文**：[pollen-robotics/microduck](https://github.com/pollen-robotics/microduck)（Apache-2.0，93★ / 620 commits / v0.10.0）
> **训练侧**：[pollen-robotics/microduck_rl](https://github.com/pollen-robotics/microduck_rl)（MjLab + PPO）
> **背景**：Hugging Face 旗下开源机器人团队 Pollen Robotics
> **记录日期**：2026-08-28
> **项目**：`~/uclaw/project/microduck-analysis/`（34 份设计文档 + 源码快照，960KB）

**标签**：#Microduck #双足机器人 #具身智能 #SimToReal #强化学习 #Rust #MjLab #Sim2Real #微服务架构 #OTA

---

## 一句话总纲

> **Microduck 用 Rust 无框架微服务 + Unix Socket/JSON-RPC 守护进程集群驱动 15 个 Dynamixel 舵机的 800g 双足鸭，9 个 61 维共享观测契约的 ONNX RL 策略（MjLab/PPO + 物理级域随机化）实现走路/摔倒自起/捡东西/踢球/前滚翻/轮滑；其真正护城河不是模型而是工程可靠性——「客户端只提交意图、robotd 独占写句柄、updaterd 健康门控自愈回滚」三层设计让无人值守机器人永不变砖。**

**关键规格速览**：高 25cm / 重 800g / 15 舵机 14 DOF / Rockchip RK3566 / 50Hz 控制环 / 观测 `obs[1,61]→act[1,14]` / $399 起 / Apache-2.0

---

### 7 模块索引（本报告内容映射）

- **tag 标签** → 头部标签行（10 个标签）
- **出处** → 头部来源/原文/训练侧/记录日期行
- **内容整理** → 第一章（硬件 + RL/Sim2Real）+ 第三章（端侧软件 + OTA）
- **查询拓展** → 第二章（JSON-RPC 选型 / Intent 语义 / 版本治理 / 故障注入 / 无网络恢复 / IMU 失效）
- **归纳总结** → 第四章（四层护城河 + 三支柱 + 五类可移植模式）
- **趋势判断** → 第五章（4 条预测）
- **关联分析** → 第六章（6 条交叉映射）
- **拓展应用推荐** → 第七章（3 档借鉴落实 + 可运行路线）
- **指南分析** → 第八章（工程质量评分 + 可复现性判定）

---

## 一、内容详细整理

### 1.1 硬件架构与执行机构

Microduck 是一颗"能上手的机器人"而非仿真玩具：整机 25cm 高、800g 重，15 个执行机构中 14 个为 Dynamixel XL330 舵机，全部挂在 **同一条 UART 总线上**（`/dev/ttyS2` @ 1Mbps，Dynamixel v2 协议），外加 IMU、相机、ToF 深度传感器（VL53L5/8CX）、可抓取物体的仿生鸭嘴。主控为 **Rockchip RK3566**（A55 四核，支持 NPU），运行 Armbian。

**关节 ID 拓扑**（源码 `robotd-design.md` §1.1 原文，单总线单读事务）：

```text
                     robotd — control thread
                              │ serialport · TIOCEXCL
                              ▼
         /dev/ttyS2 · 1 Mbps · Dynamixel protocol v2
                              │
    ┌────────────┬────────────┴───────┬──────────────────┐
  id 200       20–24                30–34             10–14
imu_to_dxl   left leg        neck · head · mouth     right leg
v2 board     5 servos             5 servos            5 servos
```

**这个设计的选择比硬件清单更值得学**：IMU 不是独立外设，而是 `id 200` 的 `imu_to_dxl` 板子——它自己就坐在 Dynamixel 总线上，把片内 SFLP 四元数从与舵机同一个寄存器块吐出。**一次 `sync_read` 读全部 16 个设备**，不需要第二个总线、第二个端口、第二套 IMU 抽象。代价是 IMU 必须在 ID 向量里排第一，让它先应答、再走舵机 burst。

**总线所有权是个"约定"而非"强制"**（这是文档里少见的诚实）：`serialport` 设 `TIOCEXCL` 能让第二个 *非特权* open 返回 `EBUSY`，但 `robotd.service` 以 root 运行（电机控制需要字符设备），root 不受该标志约束。因此排除是"安排"出来的：`robotd` 独占运行期；`robot.init`/`robot.relax` 作为 IPC 方法从环内服务，避免第二个 writer 在同一总线交替发帧（那会被误读为硬件故障）；`setup-board.sh` 还要 `mask` 掉 Armbian 默认的 `serial-getty@ttyS2`，因为 agetty 占住串口会让所有舵机消失。

**硬件配置收敛是刻意的**：只支持 alpha 变体、只支持 Radxa、只支持 v2 `imu_to_dxl`。v1/v1.5/v1.6、另外四种 IMU、三种相机、树莓派全部砍掉。轮式构型不是硬件变体，而是一个 params 开关（`policy.mode = "roller"`），因为它选的是**策略集 + 调参预设**，不是硬件。

### 1.2 强化学习与 Sim2Real 迁移流水线

政策在邻居仓库 `microduck_rl` 训练，基于 **MjLab（MuJoCo Warp）+ PPO**，50Hz 控制周期与真机严格对齐，导出 ONNX 由本仓库加载。

**13 个训练任务**（`microduck_rl` README 任务表原文）：

- **主任务** `Mjlab-Velocity-{Flat,Rough}-MicroDuck`：线速度 + 角速度 + 头部姿态指令跟踪
- **摔倒恢复** `Mjlab-VelStand-{Flat,Rough}`：行走 + 摔倒恢复合一策略
- **站起来** `Mjlab-StandUp-{Flat,Rough}`：从趴面/仰面/坐姿起身，然后保持站立 + 身体姿态控制
- **坐↔站** `Mjlab-SitStand-{Flat,Rough}`：命令式坐下站起，动作温和，头部可指令
- **地面拾取** `Mjlab-GroundPick-{Flat,Rough}`：蹲下用嘴尖触地，回到站立
- **踢球** `Mjlab-BallKick-Flat`：踢 70mm/15g 球向前——**注意 actor 是 ball-blind**（策略不看球）
- **前滚翻** `Mjlab-Roulade-Flat`：从头翻过去、脚着地
- **轮滑家族**：`Rollers`（脚底被动轮滑行速度跟踪）、`Swizzle`（经典对称滑冰）、`RollerCrouch`（滑行中蹲下）、`RollerSlope`（下坡滑行）、`RollerStandUp`（从地面站到轮上）、`Spin`（轮上原地快转）

**训练成本**：单任务 4096 并行环境、CUDA GPU 上 1–2 小时得到可用步态；无 GPU 可加 `--hf-jobs` 走 Hugging Face Jobs。

**2.1 物理级误差拟真——本项目最硬的 sim2real 资产**

文档原文的判断是："在这个尺度（小舵机驱动 800g 双足）上，**执行器保真度就是 sim2real gap 的大部分**"，所以执行器建模到电压控制律而不是理想 PD：

- **BAM M6 执行器模型**（Rhoban/bam）映射 Dynamixel XL330：电压控制律、反电动势、Coulomb/Stribeck/负载相关摩擦
- **域随机化维度**（`FrictionDRBamActuator`）：电池电压、负载下电压 sag、指令延迟、摩擦幅度——全部 per-env 随机
- **齿隙（Backlash）显式建模**：每个主任务都有一个 **Backlash 孪生任务**（task id 中插 `-Backlash`），在 14 个舵机串联 ±1° 齿轮间隙（共 2°）。建模是"认真"的：每个舵机加一个无驱动的 `passive_<joint>_backlash` 铰链；因为真实编码器在间隙输出侧，固件 PD 仿真（`BacklashEncoderBamActuator`）和 `joint_pos`/`joint_vel` 观测都**穿过齿隙**读（`qpos[servo] + qpos[backlash]`）。观测/动作维度不变，ONNX 导出和运行时零改动。
- **MJCF 模型变体**：`robot_walk.xml`（剥离躯干/头部碰撞体——摔倒成本廉价）、`robot_allcollisions.xml`（身体能物理躺地上，用于 VelStand/StandUp/SitStand/GroundPick/BallKick/Roulade）、`robot_allcollisions_rollers.xml`（被动轮）、`robot_*_backlash.xml`（由 `add_backlash.py` 生成）。模型由 Onshape 经 `onshape-to-robot` 导出。

**2.2 导出与部署契约**

- 全部策略共享 **61 维观测契约**：`obs[1,61] → actions[1,14]`。51 维旧家族（`3 gyro + 3 gravity + 42 joints + 3 command`）已弃用；61 维换成统一 13 值命令 `[vel(3), head(4), body(6)]`
- **观测归一化器烧进 ONNX 图**：必须用 `scripts/export.py` 产出的 ONNX，不能手工转换 checkpoint——否则运行时策略看到的是未归一化观测
- **加载即校验，不在推理时发现**：观测宽度、动作数、ONNX Runtime 缺失都必须在"机器人静止、能告知调用方原因"时失败。`robotd` 把加载失败变成"保持姿态 + 报告 unhealthy"，于是 updater 会回滚而不是留下一只走不了路的机器人。真实错误信息示例：

```
policy unavailable: .../walking.onnx: observation width is 51, expected 61
```

- **9 个已发布策略的谱系**（`policies/README.md` 原文，从 `apirrone/microduck_runtime` commit `5f3b314` 复制）：

| 本仓库角色名 | 上游训练产物 | 用途 |
|---|---|---|
| `alpha_walking.onnx` | `BEST_alpha_walking_rough.onnx` | 行走 / 速度-站立切换 |
| `alpha_stand.onnx` | `BEST_alpha_stand_body_control.onnx` | 站立 + 身体姿态 |
| `alpha_sitstand.onnx` | `BEST_alpha_sitstand.onnx` | 坐↔站（姿态旗标） |
| `alpha_ground_pick.onnx` | `alpha_ground_pick.onnx` | 地面拾取（相位命令） |
| `ball_kick_left/right.onnx` | 同名 | 左右腿踢球 |
| `roller.onnx` | `BEST_roller.onnx` | 轮式运动 |
| `roller_crouch.onnx` | `BEST_roller_crounch.onnx` | 轮式蹲姿 |
| `roulade.onnx` | `roulade.onnx` | 前滚翻 |

> 策略命名是**角色**而非训练 run。"换哪个 run 当行走策略"不应该意味着改每台机器人的配置——这层间接性值得保留。

**推理线程数 = 1，是刻意选择**：原型用 2，但在四核 A55 上意味着控制线程会阻塞在自己不拥有的线程池上；对这么小的网络，池的同步开销超过并行收益。注释里写"值得在板上重新测，而不是相信任何一个数字"。

---

## 二、查询拓展（技术背景）

### 2.1 JSON-RPC 2.0 / NDJSON — 被低估的嵌入式 IPC 选择

Microduck 在控制面选型上做了一次罕见的"实测对比 + 逐项否决理由"（`architecture.md` §2.2），这本身就是可复用的决策记录：

- 依赖数实测（ARM-Linux 目标，unique deps）：JSON-RPC/NDJSON + tokio = **30**（选中）；`jsonrpsee-types` = 36；`varlink` = 24；`zbus`(D-Bus) = 66；`axum` over UDS = 66；`tarpc` = 71；`tonic`(gRPC) = 81；`jsonrpsee-server` = 112 且**根本不能 serve unix socket**（`jsonrpsee-ipc` 从未实现）
- 依赖数被明确声明为"参考记录，不是决定因素"。真正的决定因素是访问控制与失效模式

**为什么是 Unix Socket 而不是 localhost HTTP/WS**（三个理由，第三个是最重的）：

1. **文件系统权限就是免费的授权**。socket mode 0660 + 专用 group，只有允许的进程能到达；TCP 端口对机器上所有进程和用户可达，得自己建 auth 层才能追平
2. **`SO_PEERCRED`** 给出调用方 uid/gid/pid，用于审计日志（"谁触发了这次回滚"是支持工程师第一个问的问题）和**强制执行**。两层分工：socket group 决定谁能**说话**；`allow_uids`/`allow_gids` 决定谁能**改变机器人**（仅变更类调用）。只读调用刻意不加门——支持必须能检查它无权修改的机器人
3. **错误接口这个 bug 类别直接消失**。typo、配置错误或"让我从笔记本调试一下"的补丁，如果绑定到 `0.0.0.0` 会把**固件更新控制**暴露到网络上。在 unix socket 上这个错误**无法表示**。原文自评"不是今天的威胁模型，但是失效模式"

**为什么控制面不用 HTTP/WS**（独立于传输层）：协议需要服务端→客户端推送（进度）。HTTP 上意味着 POST 调用 **+** WebSocket/SSE 通知 = 两套机制，且 `curl` 无法消费流式那半，所以可调试性的收益只覆盖请求/响应。全走 WebSocket 恢复单一机制但要加握手、又丢掉 `curl`。**在持久 NDJSON 连接上，调用和通知是同一套机制且无握手：更少概念，这才是真正的目标。**

### 2.2 Intent 语义 — "客户端说想干什么，机器人决定能不能干"

这是本项目最可移植的架构模式。`safety.rs` 模块头注释把不变量讲透了：

```rust
//! **It owns the only write handle to the robot.** Nothing above it — not the
//! policy, not the arbiter, not a client — holds a [`RobotIo`], so nothing
//! above it *can* command a motor. The invariant is enforced by the borrow
//! checker rather than by a rule someone has to remember when adding the
//! eighth skill the night before a demo.
```

**不变量由借用检查器强制，而不是靠"加第八个技能那天晚上要记住的规则"。** 这是把"文档里写的安全准则"变成"编译不过"的工程化升级。

**两条无条件规则**：

- **非有限值拒绝**：`NaN` 目标不被 clamp，直接拒绝
- **范围 clamp**：目标限制在执行机构行程内

**死手开关（deadman）**：意图停止到达后速度归零。原文有一句很关键的澄清：**"Stop is not limp"** —— 通信丢失让机器人**站住不动**，因为站立才是双足的安全状态；失去平衡是另一件事，不属于这一层的职责。

**摔倒判定是报告，不是规则**：`Safety::fallen` 每 tick 跟踪并发布，但**不抢占**——倒地的机器人继续被驱动，人类保持控制权。理由：一个在重力误读一次倾斜就交权的机器人，会在被人搬动时反复坐下。要"怎么处理摔倒"是控制决策，在上层 `robotd` 的 limp-fall 模式（降增益、让机器人顺着倒下），基于 `FallPredictor` 而非这个判定。它通过 `apply` 像任何指令一样下发，**没有豁免、没有后门**——这正是写句柄住在这一层的意义。

### 2.3 执行机构行程 vs 解剖限位 —— 诚实文档的范本

`ACTUATOR_MIN/MAX = ±π`（XL330 一转，居中，来自计数↔弧度转换）。注释里明确：**这是执行机构的行程，不是逐关节的解剖限位**——alpha 机器人真实关节限位在 MJCF 里，而 MJCF 未被 vendored 到这里。

> "So this catches a policy emitting `NaN`, an absurd action scale, or a garbage tensor; it will not stop a joint being driven somewhere mechanically unwise. Recorded plainly rather than dressed up, **because a limit that looks per-joint but is not would imply protection nobody has.**"

这个注释是"不夸大保护"的教科书例子：写清楚限制能防什么、不能防什么，避免给运维者制造不存在的保护感。

### 2.4 JSON-RPC 版本治理 —— 一次自我纠错的完整记录

`duck-ipc-proto/src/lib.rs` 的 `API_VERSION` 常量注释是本项目最有价值的单一文档，记录了一次完整的架构反转：

- **v2** 加 `HelloResult::revision`；**v3** 加 `net.*`/`system.*`；**v4** 加 `system.authenticate`（BLE 客户端必须先过认证）；**v5** 加 `pad.*`（纯增量，但仍 bump）；**v6** 加 `robot.init`/`robot.relax`（给关节供电不再是与守护进程抢总线的子命令）；**v7** 加 `ApplyOptions::from_dir`；**v8** 加 `pad.input`
- **规则**："**A bump promises nothing in either direction.**" 不是"除注明外均为增量"——v5 是增量的而 v4 不是，常量不区分它们

**曾经的设计是错的，文档保留了纠错过程**：`updaterd` 曾按精确 `!=` 拒绝 `hello`。前提是对的（bump 不承诺任何东西），结论却推不出来——真正打垮版本不匹配的对端的是**它够不到的路由**或**搬了位置的参数形状**，而这两者各自在自己的那一个调用上按名字拒绝自己。握手门禁却对**所有**调用触发，包括完全可服务的调用，包括 `update apply`——这才是 skew 的成因。

**现在的收窄方案**：本版本没有的方法 → `METHOD_NOT_FOUND` 命名该方法；本版本不认识的 `params` 成员 → `INVALID_PARAMS` 命名该成员（所有 params 类型 deny unknown fields）。这正是握手想达到的严格度，**移动到了能区分"调用变了"和"调用没变"的地方**。

> v7 是关键案例：`from_dir` 是旧守护进程会愉快解析的可选字段，但仍 bump。因为 serde 会忽略不认识的字段，一个 v6 `updaterd` 会接受 `update.apply --from /some/dir` 并**静默地从它配置的源安装**——是操作者想侧载内容的镜像，或者干脆什么都没装。原文：**"Silence was the danger there, not disagreement."**

### 2.5 自愈 OTA —— 恢复路径必须活在故障之外

`updater-design.md` 的核心结构规则：**更新器必须是被更新物的独立 unit**——进程无法干净地替换自己的运行中二进制，且 updater 必须能熬过守护进程崩溃来执行回滚。

**推论（原文）——`updaterd` 必须常驻，且必须把自己排除在重启集之外**：`updaterd` 和 `btd` 都打包在 daemon 制品里，朴素的"重启所有"会在 swap 或健康门控中途杀死执行者。

**一个真实的 bug 被写进了文档**："排除在本次飞行中重启"被读成"跳过"，于是两者被无限期留在旧二进制上运行——常驻的 `updaterd` 会拒绝更新的 `robotctl`，理由是"client speaks API v4, daemon speaks v3"（那个拒绝是错的，**stale 二进制才是故障源，不是分歧**）；`btd` 的修复被测试在从未运行过的新二进制上。修复是 `RESTART_AFTER_REPLYING`：通过 systemd transient timer 在响应上线后 5 秒调度——足够一次写入，又短到没人等待。每个排除的理由在那一刻恰好到期：更新完成了，而 `btd` 携带的响应已送达。

**排除重启不等于已验证新 updaterd 能工作**。不重启只保护了*进行中*的更新；它推迟到下次启动才发现新 `updaterd` 是否可用——那时更新已提交、无人值守、而恢复住在 `Engine::recover_on_start` 里，即**正在启动失败的那个进程内部**。`Restart=on-failure` 会 crash-loop 几次然后放弃，留下一台没有更新守护进程、也无法更新出去的机器人——这违背了"机器人已经坏掉时恢复依然有效"的承诺。

**文档诚实地标注了完成度**：两层关闭它，第一层**已实现**，第二层**是自己的 PR**。

**故障注入是"最容易被静默弄坏的功能"的对策**：回滚只在别的东西已经出错时才运行，所以它是"回滚大概能工作"。`updater/src/faults.rs` 的注释把逻辑讲透，且**无条件编译**（而非 `#[cfg(test)]`），使出厂二进制也能在 bench 机器人上演练；启用任何一项都需要生产配置永不设置的可显式标志：

```rust
pub struct Faults {
    /// Corrupt the artifact after download, before verification. Must produce a
    /// hash mismatch and no install.
    pub corrupt_artifact: bool,
    /// Fail the post-install hook. Must roll back.
    pub fail_post_hook: bool,
    /// Report unhealthy after apply. Must roll back.
    pub fail_health: bool,
    /// Make the health probe hang rather than answer, to prove the timeout works
    /// (socket open, no reply — the case that stalls naive clients).
    pub hang_health: bool,
    /// Abort the process immediately after the symlink swap, to prove a
    /// `kill -9` mid-swap leaves a consistent state.
    pub abort_after_swap: bool,
    /// Pretend the filesystem is full during staging.
    pub simulate_disk_full: bool,
    /// Make rollback itself fail, exercising the worst path: failed update *and*
    /// failed recovery, which must be reported loudly rather than silently.
    pub fail_rollback: bool,
    /// Make the *apply action* fail while rolling back, with the swap succeeding.
    pub fail_rollback_apply: bool,
}
```

**`fail_rollback` 与 `fail_rollback_apply` 的区分是刻意的**：一个让机器人回到已知良好版本但有一个 unit 没重启。这条路径无需故障也可达（失败 release 留下的 unit 文件就会），但只在有 systemd 的机器上，所以才在这里留一个 seam。

**故障名解析失败也是闭合的**：解析 `--inject-fault` 名称时，**未知名也拒绝**——静默忽略 typo 会让测试看起来通过了，而它想注入的故障从未触发。

**重启顺序的权威文档**（`restart-order.md`）开篇理由值得抄进任何多服务系统："哪些守护进程重启、在什么时点"曾被三份文档给出三种答案，而答案决定如何诊断 skew。**一切从代码读取，每一步命名拥有它的函数；若别处叙述性注释与此页冲突，那个注释就是 bug。**

关键不变量：release 发七个 daemon，每个 `ExecStart` 一条 `/opt/robot/daemon/current/bin/` 下的路径，所以符号链接一移，每个都立刻变 stale。两个集合只差一个函数，且测试 `every_unit_held_back_is_restarted_once_the_answer_is_out` 断言 `NEVER_RESTART` 与 `RESTART_AFTER_REPLYING` 是同一集合。

> 最常被误报的事实："Nothing is held back until a reboot." 这是 `RESTART_AFTER_REPLYING` 出现之前也成立的，是这套系统最常见的过期声明。
>
> 且因为"调度重启"不是"发生了重启"的证据，**下一次 `updaterd` 启动会逐个核对 unit 与活动 release，重启任何 stale 的**。

**`[Install]` 节作为规则而非名单**：这是"更新会启动的 unit"的判据。理由是**已经有两处应用这条规则且彼此不一致**——`hooks/postinstall` 拒绝 `enable --now` 一个无 `[Install]` 的 unit，明说"`enable --now` 会在更新途中运行一次回滚检查，而那时 daemon 正合法地重启中"；引擎却读每个 `*.service` 并过一会儿照样重启它。以该节为键，两处**按构造一致**，下一个类似的 unit 不需要有人记住。不可读的 unit 文件算作要重启的——那更可能是权限问题而非刻意无触发器，**重启得响亮好过跳过得安静**。

### 2.6 无网络可恢复 —— 正确的失败面

更新需要机器人自有网络接口有可用互联网，因此 **wifi 配置是更新的前置条件而非独立功能**：bootstrap 顺序是 *BLE 配对 → 配置 wifi → 更新*，从未配置过的机器人完全无法更新。手机自己的连通性不能替代——考虑连接间隔与 iOS 节奏后，BLE 应用层可持续吞吐约 **10–30 kB/s**，daemon 制品要几十分钟、模型包要几小时。**那是链路的上限，不是协议，所以再多的帧设计也救不回来**，这就是载荷永不走 BLE 的原因。

**完全无网络仍能做的**：`rollback` 和 `reset-to-golden` 纯在磁盘上已存在的 release 之间操作，无需 manifest、无需源、不移动字节，所以在 BLE 内轻而易举，且 `robotd` 已死时 `btd` 仍服务它们。

> **"An unprovisioned or offline robot is therefore recoverable, just not upgradeable"** —— 这是正确的一侧去失败。

### 2.7 观测层与 IMU 失效的隐蔽性

`robotctl monitor` 的设计暴露了一个极易漏掉的失效模式：**一块停止融合的板子仍会应答总线**，于是什么都不会报错，而投影重力向量会无限期保持一个合理的姿态。所以 `orientation frozen — 25 stale reads` 只出现在 health 行、且**只出现在这一行**——`robot.health` 每两秒轮询，因为电量、最热舵机、板温都不在 state 流上。

电量是**倒计时而非仪表**：0% = `BATTERY_EMPTY_V`，那里 `robotd` 会把机器人坐下并切断电源。30% 黄、15% 红。未读取显示 `batt not read yet` 而非 `0.00 V`——那是启动头一秒与无法应答的总线共有的样子。**该行在完全没有 state 时依然绘制，而那正是它最关键的场景**：一块伺服电源关掉的板子永不完成控制 tick，因此流上什么也不到，原因只在 health 回答里。


---

## 三、内容详细整理（续）：端侧软件工程与 OTA

### 3.1 七个守护进程的分工矩阵

Rust 原生开发，**无框架、单 workspace、19 个 crate**。`Cargo.toml` 顶层注释本身就是设计决策记录（resolver = "3"、edition 2024、rust-version = "1.89" 为 `std::fs::File::try_lock`——单飞行更新锁的实现依赖它，且 edition 2024 需 1.85，声明它让用旧工具链的队友得到 "requires rustc 1.89" 而不是一堆方法不存在的报错）。

**源码规模**（`wc -l` 实测，核心 23745 行）：

- `robotd/src/main.rs` = **4654 行**（控制环主体）
- `updater/src/engine.rs` = **3828 行**（OTA 引擎）
- `duck-ipc-proto/src/lib.rs` = **4836 行**（IPC 契约，含全部版本注释）
- `robotd/src/chorale.rs` = 1320 行（合唱团合奏）、`sound.rs` = 947 行、`theremin.rs` = 489 行
- `duck-control/` 全部 3612 行：`safety.rs` 580 / `policy.rs` 509 / `bus.rs` 495 / `obs.rs` 390 / `imu.rs` 355 / `io.rs` 335 / `fall.rs` 272 / `model.rs` 225

**服务矩阵**（`architecture.md` §1 原文表格）：

- **`robotd`** — 拥有电机控制、感知、策略、安全、`robot.health`；听 `/run/robotd.sock`；触达 Dynamixel 总线。**唯一触碰机器人的东西**
- **`configd`** — 拥有 wifi、机器人身份与名字、配对 PIN、手柄绑定、重启；听 `/run/configd.sock`；触达 BlueZ 与 NetworkManager over D-Bus
- **`updaterd`** — 拥有 release：验证、安装、交换、健康门控、回滚；听 `/run/updaterd.sock`；触达 GitHub releases、`systemctl`、`robotd`
- **`btd`** — 拥有**无**（BLE 传输适配层）；GATT 服务；触达 `robotd`/`configd`/`updaterd`，**不触达 `padd` 和 `tofd`**——那种带宽的无线扛不住它们的流
- **`padd`** — 拥有**无**（手柄传输 + raw input tap）；听 `/run/padd/pad.sock`（仅 `pad.input`）；触达 `/run/robotd.sock`
- **`mediad`** — 拥有相机与音频管线，对机器人拥有**无**（WebRTC 传输 + 远程前置门）；TCP：console `:8080`、signalling `:8443`，**自己没有 unix socket**
- **`tofd`** — 拥有头部 ToF 传感器：发布无人读的 8×8 深度矩阵；听 `/run/tofd/tof.sock`（`tof.stream`）；触达 HAT 的 I²C 总线
- **`robotctl`** — 拥有**无**（CLI，且必须是"在坏机器人上也能工作"的那个工具）；触达以上所有 socket

**4 条不变量**（§1.1，逐字保留）：

1. **`btd`、`configd`、`updaterd` 熬得过死的 `robotd`**。它们是恢复路径；它们必须恰好在"有些东西坏了"的那个情境里工作。无 `robotd` systemd 依赖，全部 IPC 可选且超时有界，最小依赖面（无 ML 运行时、无媒体栈）。`configd` 在此有具体理由而非对称性：配置 wifi 恰恰是机器人在坏掉时你需要的，把配置放进 `robotd` 会让它在唯一重要的情形里不可达
2. **`robotd` 在安全上拥有权威**。任何远程或本地客户端都不能绕过摔倒检测、关节/热限位或安全姿态逻辑。**客户端发意图，`robotd` 决定什么可执行**
3. **`robotd` 的控制环永不阻塞在另一个服务上**。所有跨服务读是 last-value-wins 缓存，**永不**同步 RPC
4. **每块状态单写者**。每个值恰好一个拥有服务；其余人只读或订阅

**为什么把 `mediad` 从 `robotd` 拆开**：媒体/感知崩溃不能带走电机控制。`tofd` 是同一规则套在小传感器上，具体理由更有说服力——**带起一个 VL53L5/8CX 要通过 I²C 上传约 90KB 固件、耗时数秒**，总线还与音频编解码器共享，且**大多数鸭子根本没装传感器**——那个重试循环不属于拥有电机的进程。控制环里没有任何东西读深度，所以移出去不丢任何信息。刻意**不**并入 `mediad`：深度是总线上的传感器，不是媒体管线，而且在有相机可注释之前它就有用了。

**控制面 vs 数据面的经典错误**（§2.1）：把两者混为一谈是这里最经典的错误。

- 控制面：命令/配置/状态/感知事件，几十字节、≤100 Hz → unix socket RPC
- 数据面：视频/音频帧，640×480 RGB@30fps 约 **27 MB/s** → **永不穿过 socket**

### 3.2 动作意图与执行权限隔离

X 原文的概括是"特权隔离设计"，但源码注释揭示了它的实现强度：不是权限模型，是**类型系统**。

```text
   gamepad          phone          laptop              peer          GitHub release
      │ BLE/USB        │ BLE         │ ssh               │ WebRTC          │ https
      ▼                ▼             ▼                   ▼                 │
  ┌────────┐      ┌────────┐    ┌──────────┐       ┌──────────┐           │
  │  padd  │      │  btd   │    │ robotctl │       │  mediad  │           │
  └───┬────┘      └───┬────┘    └────┬─────┘       └────┬─────┘           │
      │  robot.*      │ a subset of the same API         │                 │
      ▼               ▼                  ▼                ▼                 │
  ┌────────────────────────────────────────────────────────────┐           │
  │  one unix socket per service · JSON-RPC 2.0, one obj a line│           │
  └────┬───────────────────────┬────────────────────┬──────────┘           │
       ▼                       ▼                    ▼                       │
  ┌───────────┐        ┌─────────────┐      ┌─────────────┐                 │
  │  robotd   │        │  configd    │      │  updaterd   │◄────────────────┘
  │ robot.*   │        │ net.* pad.* │      │ update.*    │
  │ 50 Hz     │        │ system.*    │      │ verify      │
  │ loop      │        │ wifi,name,  │      │ swap        │
  │ safety    │        │ pad bonding │      │ health gate │
  └─────┬─────┘        └──────┬──────┘      └──────┬──────┘
        │ Dynamixel           │ D-Bus               │ systemctl restart
        ▼                     ▼                     │ then robot.health
  15 servos + IMU      BlueZ · NM              /opt/robot/daemon/current
```

**完整 API 面**（从 `duck-ipc-proto` 提取，共 39 个方法，6 个命名空间）：

- **`robot.*`（17 个）** — `robot.move` `robot.head` `robot.stop` `robot.enable` `robot.subscribe` `robot.state` `robot.health` `robot.init` `robot.relax` `robot.mode` `robot.pose` `robot.do` `robot.look` `robot.mouth` `robot.sound` `robot.chorale` `robot.theremin` `robot.shutdown`
- **`update.*`（9 个）** — `update.apply` `update.check` `update.log` `update.pin` `update.progress` `update.rollback` `update.select` `update.show` `update.status` `update.subscribe`
- **`net.*`（4 个）** — `net.scan` `net.connect` `net.forget` `net.status`
- **`pad.*`（5 个）** — `pad.pair` `pad.forget` `pad.report` `pad.input` `pad.status`
- **`system.*`（4 个）** — `system.authenticate` `system.info` `system.reboot` `system.services`
- **`tof.*`（2 个）** — `tof.stream` `tof.frame`

**契约类型化**（`duck-ipc-proto` 注释原文）：方法与其参数永远通过 `Call` 配对——用 `Request::call` 构造请求，用 `Request::as_call` 读回。**"There is no way to send a method with another method's parameters."** 这是把编译期类型安全下沉到线上协议的做法。

**依赖纪律**：依赖保持在 serde、serde_json、semver。每个服务都讲这些类型，包括恢复路径上的服务，**所以这里不允许引入 http、tar、crypto 或 async runtime**。

### 3.3 高可用 OTA 固件交付机制

**目标（原文）**：独立更新**守护进程二进制**与**ML 步态模型 + 配置**（它们实际上永远不会一起发布）；支持多个独立版本化、同时加载、各自受守护进程兼容性门控的模型（walk/jump/stand…）；从手机触发并监控；通过最小版本地板强制升级掉已知坏版本；**永不弄砖机器人**：原子应用、自动回滚、签名制品；保持简单，无集群后端；**跨团队其他机器人可复用**；支持每组件 post-install hook。

**非目标（当前）**：OS/kernel/驱动 OTA；集群管理（分批发布、逐设备遥测、仪表盘）——模型是"最新版，全部机器人"；增量/diff 更新——全量制品在当前节奏下足够小。

**7 个关键决策**（§3 决策表原文）：

- **更新粒度**：应用级（非 A/B 镜像）——只改 daemon + 模型，OS 静态。A/B（RAUC/Mender）会过度工程
- **传输**：**机器人从 CDN 拉取**，走它自己的 wifi——手机只是触发器 + 进度显示。大载荷永不触碰 BLE
- **托管**：**GitHub Releases**（daemon）+ **HF Hub**（模型）——零后端，各自是制品的天然归宿。引擎把 "source" 当可插拔
- **签名**：**minisign**（CI 签，机器人验）——久经考验的格式、极小的验证 crate、简单密钥管理
- **通道**：每个独立版本化的东西一个：`daemon` + 每模型一个。节奏不同；模型重载无需完整重启
- **回滚**：版本化目录 + 原子符号链接交换 + 健康门控——简单、稳健、无需分区
- **复用**：配置驱动的通用引擎。同一引擎到处用；每个机器人声明自己的组件

**发布节奏**：面向客户的 daemon 前几个月每 2–3 周，之后每 2–3 个月；模型走自己独立的节奏。但**内部迭代热得多**（原型 3 天 ~8 个 tag），所以系统必须服务两种节奏：一条快的内部 `staging` 流和一条慢的、经策划的 `stable` 流——**这才是 staging 通道和脚本化回滚成为承重结构而非可选打磨的原因**。

**状态放置规则（一条规则管全部）**：`/etc/robot/robotd.toml` 与 `updater.toml` 是单板配置，安装器写一次、**永不覆盖**；`/var/lib/robot/config/config.json` 存机器人名与配对 PIN（文件 + `flock`，`configd` 拥有）；NetworkManager profile 存 wifi 凭证（**永不自己存**）；`/opt/robot/daemon/releases/<ver>/` 存二进制、策略与出厂默认（原子替换）；`/opt/robot/daemon/current` 符号链接说明哪个 release 在线；`/run/<service>/identity.json` 发布每个守护进程实际在跑什么。

> **`releases/<ver>/` 之外的一切都同时熬过更新和回滚。这就是全部规则**，也是单板配置不随 release 发布的原因。

**端到端更新路径**：

```text
  push a branch ──► CI builds and signs a release ──► robotctl update apply
                                                            │
                                                            ▼
                                          updaterd: verify signature, unpack,
                                          move `current`, restart the units
                                                            │
                                                            ▼
                                          health gate: ask robot.health
                                            ├─ healthy  ──► keep it
                                            └─ not      ──► put the old one back
```

**"变砖"防线是四层的**：签名验证 → 原子目录交换 → 健康门控（问 `robot.health`，不健康就把旧的放回）→ crash-loop 计数（boot counter 兜底）。**且一个"熬过健康门控的 crash-loop"由 boot 计数器捕获**（`robot-boot-check.service` + `robot-rescue`）。

**版本化依赖的单一真相源**（`Cargo.toml` 元数据，这段注释堪称范例）：

```toml
[workspace.metadata.onnxruntime]
floor  = "1.23"     # `ort` 接受的最低版本——与 ort 依赖同步提高
target = "1.28.0"   # 板子低于 floor 时安装的版本
[workspace.metadata.rknpu]
runtime = "v2.3.2"  # Rockchip rknn-toolkit2 的 tag，.so 就在那里
[workspace.metadata.gst-plugins]
repo    = "pollen-robotics/microduck-gst-plugins"
version = "v3"      # mpph264enc + webrtcsink/webrtcsrc，任何 Debian suite 都没有
```

> "`scripts/setup-board.sh` 是独立用 curl 拉取、读不到这个文件的，所以它带一个字面量，**而一个测试断言两者一致**。两份版本漂移，就是板子拿到了会让 `ort` panic 的 ONNX Runtime 的方式。"

**一个真实事故被写进了注释**：板子曾出现 ONNX Runtime 1.20.1 与 `ort` 1.23+ 不兼容。`ort` 在库缺失时**不返回错误而是 `expect`**（从懒路径、任何 API 调用可达），所以缺失库会 abort 触碰它的线程。控制环里意味着线程死掉、任何 tick 都到不了、`robot.health` 永远报 "loop has not completed a cycle"——**守护进程看起来卡死，而不是说 ONNX Runtime 没装**。

`ensure_runtime()` 用 `OnceLock` 预探测，把"库缺失"变成普通错误、带运维者的修复办法。但**注释诚实地自我纠正**：早前版本声称探测能防 panic，一块跑 ONNX Runtime 1.20.1 的板子证伪了它——库加载成功、探测通过，然后 `ort` 在自己的版本检查上 panic（`expected version >= '1.23.x', but got '1.20.1'`）。

> "**The probe proves the file loads; nothing more.**" 剩下的由 `catching_ort_panics` 覆盖，包括未见过的 panic。

**发布包不是补丁**：构建落为 `/opt/robot/daemon/releases/<version>/` 下的完整目录；`updaterd` 验证签名、移动 `current` 符号链接、重启 units、然后问 `robotd` 是否健康。不健康就自己把旧 release 放回。

### 3.4 工程质量的两处反直觉决策

**决策一：不做 `[profile.release]` 调优**。原文理由完整：

> "Binary size is not worth optimising for: model artifacts will dwarf a few MB of binary, and the tuning cost more than it bought — **`strip = true` in particular removes the symbol table, turning a panic backtrace in journald into bare addresses, which is exactly what you need when diagnosing a robot you cannot attach a debugger to.** `lto`/`codegen-units` only lengthened builds."

不 strip 的原因不是洁癖：**在无法挂调试器的机器人上，panic 回溯是唯一的诊断手段**。

**决策二：`duckctl` 被排除在 default-members 之外**。这个例外存在的原因写得很清楚：`cargo board --bins`（在 `dev-push.sh` 和 release workflow 里）为 aarch64 构建每个 default member，这对板子的守护进程是对的、对开发者在自己机器上运行的客户端是错的——它会为一个永不该看到它的板子、在 release 路径上、毫无意义地交叉编译一个蓝牙栈。备选是在两个调用点显式命名二进制，那两处得手工保持一致，**而"手工保持一致"正是这个仓库反复写下来的那种失效**。一份清单放这里，新守护进程自动被两处拾取，不需要谁记住。

**决策三：`robotctl configure` 的三条可信任性质**（`cheatshat.md` 原文）：

- **不会与守护进程不一致**：schema、默认值、校验来自 `robotd` 解析文件的**同一个 crate**，键列表由测试钉死完整——守护进程里新增一个 `[section]` 要么出现在这里、要么构建失败
- **不会吃掉你的文件**：注释、顺序、其他 release 的键原样保留，只写你改动的键。回退一个键是**删除它**（连同附着的注释）而不是钉住默认值，所以文件保持为**决策的列表**而非默认的副本
- **不会写出 `robotd` 拒绝启动的文件**：每次保存先通过守护进程自己的 loader 验证，原子写（临时文件 + rename），并带原因拒绝

**决策四：`robotctl monitor` 是一台可视化诊断台**。右侧把机器人**画成它站立的样子**——与策略训练所用的同一个视觉模型，由实测关节角定位、按 IMU 重力向量倾斜。**"一条腿折错方向、头扎进地板、鸭子侧躺在地上，都只不过是关节表里的数字；在这里每一样都显而易见。"**

ToF 帧到达时画进同一场景——命中黄色、地面绿色，**按机器人的自身身体做深度测试**，所以喙后面的点会被它遮住。**这就是"它看到我的手，还是看到它自己"变得可回答的方式**，不需要按键。

下方是**点字盲文里程图**：里程计从足部接触与 IMU 得出的轨迹，面板从不生长——**世界随轨迹缩放，整条路径保持画面内**。`+` 是起点，`●` 带短射线表示朝向。**没有磁罗盘，所以这是相对运动且会漂移——它回答"它是不是走了个圈"，不回答"它在哪里"。**

重定向或管道时每 tick 输出一行，所以 `> run.log` 和 `| grep FALLEN` 都能用。`robotctl version` 是**第一件事要跑的**：每个守护进程实际在跑的 vs 已安装的，不一致时给警告。

> "Run this before believing any other diagnosis — **a daemon serving old code after an update looks exactly like a bug in the fix you just shipped.**"

这是全文最实用的一句话：更新后跑旧代码的守护进程，看起来和你刚发布的修复有 bug 一模一样。


---

## 四、归纳总结

### 4.1 核心命题：模型是最便宜的一环，工程可靠性才是护城河

Microduck 的 13 个 RL 任务全部基于 MjLab + PPO——**算法层面没有一处创新**，与 `mjlab_microban`、DeepMind 的 legged-gym 是同一套配方。它的差异化全部来自工程层，可归纳为四层防线，从内到外：

```text
┌───────────────────────────────────────────────────────────────┐
│ 第 4 层 · 交付可靠性   updaterd：签名→原子交换→健康门控→回滚     │
│        ▲    boot counter 兜底 crash-loop；staging/stable 双流   │
├───────────────────────────────────────────────────────────────┤
│ 第 3 层 · 恢复路径     configd/updaterd/btd 熬过死的 robotd      │
│        ▲    无 ML 运行时、无媒体栈、无 systemd 依赖               │
├───────────────────────────────────────────────────────────────┤
│ 第 2 层 · 安全权威     Safety 独占 RobotIo 写句柄                │
│        ▲    借用检查器强制；NaN 拒绝 + 行程 clamp + deadman      │
├───────────────────────────────────────────────────────────────┤
│ 第 1 层 · 物理保真     BAM M6 执行器 + Backlash + 域随机化       │
│        ▲    电压控制律建模；±1° 齿轮间隙显式建链；per-env 随机    │
└───────────────────────────────────────────────────────────────┘
```

**关键洞察**：第 1 层保证"训练出的策略能落到真机"，第 4 层保证"更新后的机器人不会变成砖"，第 2、3 层保证"任何一层坏了都有东西还在工作"。这四层**互相独立**——第 3 层不依赖第 2 层的进程存活，第 4 层的回滚不依赖第 1 层的策略正确。

### 4.2 三支柱：把"文档准则"升级为"机器可验证"

Microduck 最值得学的是它把每条设计原则都变成了**可程序化验证的断言**，而不是靠人记住。这与 Hermes Agent 的 AGENTS.md 中"质量门禁机械化"准则完全同构：

- **契约类型化**：方法与参数通过 `Call` 配对 → "没有方式用另一个方法的参数发送一个方法"。跨服务协议错误在编译期消失
- **版本严格度下移**：所有 params 类型 `deny unknown fields` → 未知成员报 `INVALID_PARAMS` 并**命名该成员**。版本门禁从"握手处全拒绝"收窄到"在能区分调用变没变的地方拒绝"
- **故障注入 CI 化**：`Faults` 无条件编译（非 `#[cfg(test)]`）→ "回滚大概能工作"变成 CI 断言。8 个注入点每个都写清了期望结果（"Must produce a hash mismatch and no install"）
- **配置一致性测试**：`Cargo.toml` 元数据与 `scripts/setup-board.sh` 的字面量版本由测试断言一致 → 双份漂移从"事故"变成"构建失败"
- **服务清单自洽**：测试 `every_unit_held_back_is_restarted_once_the_answer_is_out` 断言 `NEVER_RESTART` 与 `RESTART_AFTER_REPLYING` 是同一集合 → 两个集合的对称性不需人盯
- **策略打包完整性**：`xtask` 的 `every_policy_in_the_repo_is_packaged` 测试把三个 workflow 的 `--include` 清单钉住 → "三份清单手工保持一致"这种失效被消除

### 4.3 五类可移植模式（脱离本项目独立可用）

- **① 意图/执行分离 + 独占写句柄** — 客户端只能提交 `robot.move`/`robot.head` 等抽象意图，安全层决定什么可执行；写句柄的排他性由借用检查器保证而非约定。适用于任何"多客户端 → 单一物理执行器"的系统（打印机、机械臂、无人机、3D 打印机）
- **② 恢复路径与故障域解耦** — "代码只在别的东西已经出错时才运行，所以它是最可能被静默弄坏的那部分，因此让坏的**状态不可表示**"。这是本项目反复出现的核心论证，可移植到任何自愈系统
- **③ 原子符号链接交换 + 健康门控** — 版本化目录 + 移动 `current` + 问被更新者是否健康 + 不健康自己放回。零分区、零 A/B 镜像、零集群后端，实现"永不弄砖"
- **④ 控制面/数据面严格分离** — 控制面 ≤100Hz 几十字节走 RPC，数据面 27MB/s **永不穿过 socket**。加上"控制环永不阻塞在另一个服务上，所有跨服务读是 last-value-wins 缓存"
- **⑤ 诚实文档模式** — 不夸大保护、记录自我纠错、标注完成度。`safety.rs` 明说限位"不是逐关节解剖限位"；`ensure_runtime()` 明说探测"只证明文件能加载，不多不少"；up 文档明说"第一层已实现，第二层是自己的 PR"

### 4.4 与 microban 的关键差异（同为 30cm 级开源 RL 机器人）

- **本体规模**：Microduck 800g / 25cm / 14 DOF；microban 约 30cm / 16 DOF
- **端侧栈**：Microduck 是 **Rust 无框架微服务 + Unix Socket/JSON-RPC**（19 crates、23745 行核心代码）；microban 侧重 Python/MjLab 训练侧
- **任务广度**：Microduck 有 13 个任务含摔倒自起、前滚翻、踢球、轮滑；microban 当前实现速度控制 + 扰动恢复
- **域随机化保真度**：Microduck 额外做了 **Backlash 孪生任务**（±1° 齿隙、编码器穿间隙读），这是 microban 笔记中未提及的层级
- **交付侧**：Microduck 有完整的 minisign 签名 + 健康门控 + 双层恢复 OTA；这是训练侧仓库不具备的
- **共同底座**：都用 MjLab（MuJoCo Warp）+ PPO + BAM 执行器模型 + 50Hz 控制周期对齐真机 + 4096 并行环境 + `onshape-to-robot` 导出 MJCF。**两者共享 Rhoban 的执行器建模技术栈**

### 4.5 一句话评价

> **Microduck 是一个"工程先行"的具身智能开源范本**：它的 RL 部分是标准配方，但它把 RL 社区通常不做的另一半——多服务进程模型、跨版本 IPC 治理、自愈 OTA、故障注入测试——做到了有 CI 断言守护的生产级水平。**对一个 93 star 的仓库而言，这个工程密度异常高**，也说明开源机器人的竞争正从"算法"转向"可靠性工程"。


---

## 五、趋势判断

### 趋势 1：开源小机器人的竞争主轴从"算法"转向"可靠性工程"

**依据**：Microduck 的 13 个任务全部是 MjLab + PPO 标准配方，与 microban 共享同一套执行器建模技术栈（BAM、50Hz 对齐、4096 并行环境、`onshape-to-robot` 导出）。差异全部在工程层：19 个 Rust crate、23745 行核心代码、39 个 IPC 方法、8 个故障注入点、minisign 签名 + 健康门控 + 双层 boot 恢复。而 microban 的训练侧仓库 README 直接指向 `CLAUDE.md` 作为"蒸馏后的 playbook"，同样把重心放在流程工程而非算法新颖性。当所有人用同一套 MuJoCo+PPO 配方时，**能把策略安全落到真机并永不弄砖的那个团队赢**。

**判断**：12–18 个月内，开源具身项目的 star 增长将主要来自 OTA/恢复路径文档的完整性，而非新算法。评价一个开源机器人项目"是否认真"的新标准是：它有没有 `updater`、有没有故障注入测试、有没有把回滚写进 CI 断言。

### 趋势 2：「客户端提交意图、守护进程拥有安全权威」会成为机器人 SDK 的默认契约

**依据**：本项目已经把这个契约做到编译期强制（`Safety` 独占 `RobotIo`，借用检查器保证上层无人持有写句柄），并把它推广为一条设计原则："让代码只在别的东西出错时才运行的那部分变得不可表示"。39 个 API 方法里 17 个是 `robot.*`，且**没有一个允许直接设关节角**——最小粒度也是 `robot.move`/`robot.head`/`robot.pose` 这类抽象意图。同时 `robotctl configure` 承诺"不会写出 robotd 拒绝启动的文件"，把配置错误也堵在写入门禁。

**判断**：ROS2 生态里长期存在的"任何节点都能直接写关节"的隐患会被逐步取代。可以预期出现一个"机器人意图层"（robot intent layer）成为 SDK 标配，类似 Hermes Agent 的"确定性护栏"但下沉到硬件契约。对上游 ROS2 用户的迁移门槛在于：意图层是**加法**，需要重画节点图，而直接写句柄是**减法**。

### 趋势 3：物理级域随机化的粒度会持续细化，「硬件非线性建模」成为 sim2real 主战场

**依据**：本项目已经把齿隙建模做到"认真"的程度——每个舵机加无驱动的 `passive_<joint>_backlash` 铰链，且因为**真实编码器在间隙输出侧**，固件 PD 仿真和 `joint_pos`/`joint_vel` 观测都穿过齿隙读（`qpos[servo] + qpos[backlash]`），同时保持观测/动作维度不变使 ONNX 导出与运行时零改动。域随机化覆盖电池电压、负载下电压 sag、指令延迟、摩擦幅度四个维度。文档明确判断："在这个尺度上，**执行器保真度就是 sim2real gap 的大部分**"。

**判断**：这比"增加随机化维度数量"重要得多——**正确的建模方向 + 维度不变的低成本集成**是可复制的技术路线。预期未来 12 个月开源 RL 机器人仓库的标配将从"域随机化开关"升级为"逐硬件非线性建模 + 孪生任务族"。对本机具身研究（双足/外骨骼/ESP32-STM32 双 MCU 项目）的直接启示是：**先量测真机的齿隙与摩擦曲线，再决定是否值得建链**——本项目给出了一个可验证的判据：如果执行器是非线性的（舵机、无刷直驱），那么建链的 ROI 极高。

### 趋势 4：Unix Socket + NDJSON 控制面在小规模多服务系统里会被重新发现

**依据**：本项目做了罕见的依赖实测对比（30 vs 66/71/81/112），并给出三条不可替代的理由：文件系统权限即免费授权、`SO_PEERCRED` 免费给出 uid/gid/pid 用于审计**和**强制执行、**"绑定到 0.0.0.0 暴露固件更新控制"这个 bug 类别在 unix socket 上无法表示**。文档自评第三条"不是今天的威胁模型，但是失效模式"。

**判断**：这不是新技术，但它在"少量服务 + 同主机 + 需要访问控制 + 需要服务端推送"的组合上被系统性低估。随着边缘 AI 设备增多（NPU 板卡、车载、机器人、NAS），可以预期出现一批以 Unix Socket + NDJSON 为控制面的开源项目，替代"为了标准化而引入 HTTP/gRPC"的默认选择。**关键判据**：如果你的系统 ≤7 个服务、都在同一台机器、需要 per-call 授权审计、需要进度推送，那么 JSON-RPC/NDJSON 的依赖面（30）与调试性（curl 可读全双工）优势会显著。

---

## 六、关联分析

### 6.1 与已有笔记的微ban 系列关联（最强关联）

本笔记与 [2026-08-23-MjLabMicroban-30cm开源人形机器人RL训练与SimToReal](2026-08-23-MjLabMicroban-30cm开源人形机器人RL训练与SimToReal.md) 构成**同族对照实验**：两者都是 30cm 级、开源、MjLab+PPO、BAM 执行器模型、50Hz 对齐真机、4096 并行环境、`onshape-to-robot` 导出 MJCF。差异维度恰好互补——microban 侧提供 Python/MjLab 训练视角，Microduck 侧提供 **Rust 端侧工程 + 自愈 OTA** 视角。**两篇合起来才是一份完整的"开源 RL 机器人端到端参考"**。建议后续把两篇做成专题聚合页（与记忆中"WAM/VLA 8 篇 + 具身 2 篇 + 机器人 5 篇系统跟踪，建议建专题聚合页"的待办合并处理）。

### 6.2 与 `agent-security-governance` / `agent-authorization-continuity` 的同构

本项目的"客户端提交意图、`robotd` 拥有安全权威、写句柄由借用检查器排他"与 Hermes Agent 的授权连续性理论（不可变效果天花板 + 过渡信封 + P_t = P_t^prop ∩ B 钳制）**在结构上同构**：

- 机器人的"意图" ≈ Agent 的"提议动作"
- `robotd` 的安全层 ≈ Agent 的"授权信封"
- `Safety` 独占写句柄 ≈ "不可变效果天花板"
- `S` 的 deadman（意图过期速度归零）≈ Agent 的"空闲自动收敛"

**新洞见**：Microduck 把这条原则推进到**类型系统层**——"意图"不是运行时检查的对象，而是**类型上唯一的入参形状**（`robot.move` 只接受速度指令，不存在"设关节角"的方法）。这比 Hermes Agent 当前的"运行时护栏"更强一档：**让不安全的调用不可表示，而不是调用后被拒绝**。

### 6.3 与 `hermes-disaster-recovery` / `updaterd` 的自愈 OTA 对照

Hermes Agent 的防灾容灾体系（进程守护、自动备份、健康检查、日志轮转、一键恢复）与 Microduck 的 `updaterd` 是同一问题域的两个解：

- **共同点**：更新器独立于被更新物；健康门控（问被更新者是否健康）；不健康自动回滚；符号链接/软切换原子性
- **Microduck 更强的一处**：**故障注入是 CI 断言**（8 个注入点无条件编译，每个写明期望结果），而不是"回滚大概能工作"。这正是 AGENTS.md "质量门禁机械化"准则在 Rust 上的落地形态
- **Hermes 更强的一处**：跨 profile/跨机器的经验交换（exchange-protocol），Microduck 明确"无集群后端"

**可借鉴**：把 Hermes 的 `updater` 类流程加上故障注入点（模拟磁盘满、模拟健康探针挂起、模拟回滚自身失败），让"回滚能工作"从信念变成断言。

### 6.4 与 `robotics-project-setup` / `servo-arm-control` 的硬件侧关联

本项目是**舵机直驱双足**，与现有 ESP32 舵机机械臂（6-DOF DH 运动学）不同层级但共享底层约束：

- **共享约束**：Dynamixel XL330 是本项目舵机型号，与用户已有舵机生态可能重叠
- **新增知识**：15 舵机 + IMU 挂**同一条 UART 总线**、单次 `sync_read` 读 16 设备、IMU 板坐在 Dynamixel 总线上（`id 200`）——这是"单总线多设备"的实战范本，比双总线设计少一颗 MCU、少一路布线、少一套时序
- **新增知识**：`TIOCEXCL` 排他是"约定"而非"强制"（root 不受约束），因此需要显式管理其他 claimant（agetty mask、`Conflicts=` unit、`robot.init`/`robot.relax` 从环内服务）

### 6.5 与 `robotics-project-setup` 技能的方法论补充

本项目的 `docs/robot/` 三件套（`cheatsheet.md` 793 行、`cheatsheet-dev.md`、`duckctl.md`）+ `docs/design/` 8 篇设计文档 + `docs/project/` 8 篇遗留问题记录，构成了**"操作手册 + 设计决策记录 + 已知缺陷追踪"三分离**的文档范式。`restart-order.md` 开篇的理由尤其值得记入技能：

> "哪些守护进程重启、在什么时点"曾被三份文档给出三种答案，而答案决定如何诊断 skew。**一切从代码读取，每一步命名拥有它的函数；若别处叙述性注释与此页冲突，那个注释就是 bug。**

**可执行化建议**：为 `robotics-project-setup` 增加"重启顺序单点权威文档"步骤——凡是涉及多 unit 生命周期的项目，必须有一份声明"每一步命名拥有它的函数"的顺序文档，并在其他文档中只链接不复制。

### 6.6 与 `jetson-orin-platform` / 本机资源保护的关系

用户规则明确"不要在本机（Jetson Orin）跑重型 ML 训练/部署测试"。本项目的训练侧（MjLab + 4096 并行环境 + CUDA GPU，单任务 1–2h）**明确不适合本机**——那需要一块 CUDA 训练 GPU。但端侧推理（ONNX Runtime 1.28 on RK3566 A55 四核、`INTRA_THREADS = 1`、单策略约 776KB）**理论上可在 Jetson 上跑通**——不过本机的定位是 Hermes Gateway 运行环境，不是机器人主控。**结论：本项目在本机只做代码精读与模式提炼，不部署**，与既有资源保护策略一致。


---

## 七、拓展应用推荐

### 7.1 三档借鉴判定（禁止走过场）

**① 档 · 有利进化 → 立即落实**

- **a. 「让不安全的调用不可表示」下沉到 Hermes 工具契约**
  本项目的 `Call` 类型把"方法与参数"配对到编译期，"没有方式用另一个方法的参数发送一个方法"。Hermes 的 `tool_call` 目前是运行时校验。可落地动作：为 cron 任务的高危工具（`terminal` 的 `rm -rf`、`write_file` 的跨 profile 写入）增加**类型层面的必填参数对**，让"缺参数的危险调用"在构造期失败而非执行期拒绝。这是 `agent-authorization-continuity` 技能的自然延伸。
- **b. 故障注入点 CI 化**
  `updater/src/faults.rs` 的 8 个注入点是本笔记最可复制的单一模式。Hermes 的 `updater`（`hermes-upgrade` skill）当前没有故障注入。可落地动作：为 `hermes-upgrade` 增加 `--inject-fault` 参数，覆盖 `corrupt_artifact`（模拟升级包损坏）、`fail_health`（模拟升级后健康检查失败）、`fail_rollback`（模拟回滚自身失败）三个点，并把"必须回滚"写成 CI 断言。**判断标准：注入后 CI 红，不注入 CI 绿。**
- **c. 「重启顺序单点权威文档」写入 `robotics-project-setup`**
  `restart-order.md` 的开篇理由（三份文档给出三种答案 → 收敛为一份从代码读取、每步命名拥有函数的文档）是可直接搬用的文档范式。可落地动作：patch `robotics-project-setup` 技能，增加"多 unit 生命周期项目必须建立重启顺序单点权威文档，其他文档只链接不复制"的步骤。

**② 档 · 有价值备用 → 记录 Memory**

- **Unix Socket + NDJSON 控制面**（依赖 30，per-call 授权，curl 全双工）——本机的 Hermes Gateway 已经是 Python + HTTP，改造成本高于收益。但**未来若做多进程边缘 AI 设备编排**（如多 Jetson 集群），这是首选控制面。已记入本笔记 7.1 与趋势 4，Memory 不必单开条目（避免膨胀）
- **Backlash 孪生任务族**（±1° 齿隙、编码器穿间隙读、维度不变）——本机的 ESP32 舵机项目目前无齿隙建链需求（6-DOF 机械臂负载小、精度要求低）。若未来做**载人外骨骼**（`exoskeleton-control` 技能域），这个模式 ROI 极高，因为外骨骼的关节间隙直接关系安全性

**③ 档 · 仅知识库 → 只记笔记**

- 9 个策略的谱系表（`policies/README.md`）：角色名与训练 run 分离的设计值得知道，但对本机无落地场景
- `sounds/` 合唱团合奏（1320 行 `chorale.rs`）与 `theremin.rs`：创意项目，与工程目标无关
- `duck-detect`（10MB ONNX）与 RKNN 3.7MB 转换：Rockchip NPU 专属，本机是 Jetson CUDA 栈

### 7.2 可运行路线（若真需要搭建）

**训练侧**（需要 CUDA 训练 GPU，**不在本机**）：

```bash
git clone https://github.com/pollen-robotics/microduck_rl && cd microduck_rl
uv sync
# 主任务：4096 并行环境，单任务约 1-2h 得可用步态
uv run train Mjlab-Velocity-Flat-MicroDuck --env.scene.num-envs 4096
# 摔倒恢复（同一个策略）
uv run train Mjlab-VelStand-Flat-MicroDuck --env.scene.num-envs 4096
# 带齿隙的孪生任务
uv run train Mjlab-Velocity-Flat-Backlash-MicroDuck --env.scene.num-envs 4096
# 导出 ONNX（观测归一化器烧进图）
uv run scripts/export.py Mjlab-Velocity-Flat-MicroDuck --wandb-run-path <...>
# 无 GPU：加 --hf-jobs 走 Hugging Face Jobs
```

**端侧**（需要 Radxa/RK3566 开发板 + alpha 变体硬件 + v2 `imu_to_dxl` 板，$399 整机）：

```bash
# 官方路径
robotctl version                    # 第一件事：跑的实际版本 vs 已安装版本
robotctl health                     # 硬件+软件一体报告，非零退出可门控脚本
robotctl monitor                    # 可视化诊断台（右侧机器人 pose + 点字里程图）
sudo robotctl configure             # 交互式编辑 /etc/robot/robotd.toml（三条可信任性质）
robotctl update apply               # 拉取并应用 release
robotctl update rollback            # 回滚到上一版本（无需网络）
```

**本机可做的**：`cargo test` 跑通 Rust 侧单元测试（`updater/tests/` 有 apply/download/install/ipc 四组集成测试，`test-support` 提供 `fake-release.rs` 与 `systemd-fixture.rs`），无需机器人硬件。**这是唯一可在本机验证的部分**，且不需要装 Rust 之外的大型依赖。

---

## 八、指南分析

### 8.1 工程质量评分

- **文档密度**：**极高**。8 篇 `docs/design/`（架构、robotd、updater、重启顺序、app 路径、boot 恢复、WebRTC 两篇）+ 8 篇 `docs/project/`（CI 设置、安装路径缺口、媒体 bringup、NPU bringup、手柄配对、路线图、slice-2 bringup、BLE 更新）+ 3 篇 `docs/robot/` 操作手册（cheatsheet 793 行）。`duck-ipc-proto/src/lib.rs` 单文件 4836 行，其中大量是版本决策注释
- **决策记录质量**：**罕见水平**。每个技术选择都带"为什么选它"和"为什么不选那个"，且**记录自我纠错**（`RESTART_AFTER_REPLYING` 的 bug 由来、`ensure_runtime` 探测的证伪、`updaterd` 版本门禁的反转）。`Architecture.md` 的 IPC 选型带 8 个方案的依赖数实测
- **可复现性**：**端侧高，训练侧中**。端侧有完整 `deploy/`（overlay、audio、trusted_keys、systemd、sysusers）、`scripts/setup-board.sh`、`hooks/preinstall`、minisign 签名链，且**版本字面量由测试断言一致**。训练侧依赖 wandb run path（`--wandb-run-path <entity/project/run_id>`），意味着**预训练策略的完整复现需要 wandb 数据**，仓库内 vendored 的是 9 个 ONNX 而非 checkpoint
- **测试体系**：**强**。集成测试覆盖 updater（apply/download/install/ipc）、xtask（artifact/rescue/sideload）、kinematics（`fk_against_mujoco.rs` 对 MuJoCo 做前向运动学回归、`fk_alpha.json` fixture）。故障注入无条件编译。配置完整性由测试钉死（`every_policy_in_the_repo_is_packaged`、configure 键列表完整）
- **许可证与开放度**：Apache-2.0，93★ / 5 fork / 620 commits，商业可售（$399 起）。**软件全开源，硬件 MJCF 由 Onshape 导出也开源**。唯一未开源的是 wandb 训练数据与部分 `.onnx` 的上游 run 命名

### 8.2 五个值得抄的工程习惯

- **① 每个技术选择带否决理由**。IPC 选型不写"我们选 JSON-RPC"，而写 8 个方案的依赖数、否决原因，以及"依赖数不是决定因素，真正决定因素是访问控制和失效模式"。**避免决策日志变成结论列表**
- **② 注释记录自我纠错**。`ensure_runtime()` 明说"早前版本声称探测能防 panic，一块板子证伪了它"。`updater-design.md` 明说"排除在本次飞行中重启被读成跳过，那是 bug"。**不美化历史 = 后人不必重犯**
- **③ 文档标注完成度**。`updater-design.md` 明说"两层关闭它，第一层已实现，第二层是自己的 PR"。**未完成的承诺标出来，胜过含糊的"支持"**
- **④ 每条设计原则有一个测试守护它**。写句柄排他 → 借用检查器；版本对称 → `every_unit_held_back_is_restarted_once_the_answer_is_out`；策略打包 → `every_policy_in_the_repo_is_packaged`；配置一致 → 版本字面量断言测试。**"文档说"→"测试说"**
- **⑤ 命名诚实**。`ACTUATOR_MIN/MAX` 的注释明说"这是执行机构行程，不是逐关节解剖限位"，并解释"一个看起来逐关节但并不是的限位，会暗示不存在的保护"。**不给运维者制造虚假的安全感**

### 8.3 三个真实局限（不美化）

- **单硬件配置锁死**：只支持 alpha 变体 + Radxa + v2 `imu_to_dxl`。v1/v1.5/v1.6、另外四种 IMU、三种相机、树莓派全部砍掉。`robotd-design.md` 明说"v1 目标是单一、规格良好的硬件配置"。**这是刻意选择，不是缺陷，但意味着它不是通用平台**
- **无集群后端**：更新模型是"最新版，全部机器人"，无分批发布、无逐设备遥测、无仪表盘。文档明确列为当前非目标。**对单机/小团队是对的，对量产是缺口**
- **策略托管未迁移**：`policies/README.md` 明说这是**临时归宿**——策略应该在 HF Hub 上作为独立版本化的 `model` 组件，`deploy/updater.toml` 已经描述了那个组件并刻意留空直到 repo 存在。vendored 进来是为了让 release 自包含、让更新路径可端到端测试。**迁移工作已被完整规划，只差执行**

### 8.4 一句话判定

> **本项目在 93 star 的体量下达到了生产级开源硬件软件的文档密度与测试强度，是"开源小机器人"品类里工程可靠性的当前标杆；其可复现性受限于 wandb 训练数据未开源，且单硬件配置锁定意味着它不是通用平台。对 Hermes 的直接价值在三处：意图/执行分离下沉到类型系统、故障注入 CI 化、重启顺序单点权威文档。**


---

## 九、产品与商业背景（补全项）

> 本节补全技术架构之外的产品事实，来源见文末出处节。

### 9.1 产品规格

- **定价**：$399 预购（首批 2026 圣诞前发货）；中国深圳制造，Seeed Studio 参与生产
- **配色**：奶油 / 石墨 / 薰衣草紫 / 天蓝
- **计算核心**：瑞芯微 RK3566（四核 Cortex-A55 + Mali G52）
- **传感套件**：RGB 摄像头、立体麦克风阵列、扬声器、2D LiDAR、Wi-Fi、BLE、2× IMU
- **抓取方式**：**无传统双臂**——可活动鸭嘴兼任抓取机构
- **出厂预置动作**：7 个
- **开箱动作全集**：走路（手柄直控）、摔倒后自己站起来、低头捡地上的东西（袜子、记号笔）、坐下/起立/踢球/前滚翻、跟随激光笔移动、NFC 触发、唱歌——**每台首次启动获得唯一声音身份，永久绑定该硬件**
- **装轮换脑**：加装脚底轮子 → 切换到另一套强化学习策略，可滑行、转圈、下坡，甚至能在轮滑状态下自己起身

### 9.2 官方定位与商业表现

- **官方口号**："Made to move · Ready to learn" / "为运动而生，也准备好摔倒"
- **Clem Delangue（Hugging Face CEO）定位**："首款可以通过强化学习教授新技能的平价 AI 机器人"
- **销售表现**：Thomas Wolf 称发布初期约 5 秒卖出一台，销售额已破 100 万美元
- **对比锚点**：$399 把双足机器人从实验室价格带直接拉到消费电子区间（对比 1X NEO 约 2 万美元）
- **产业意义**：Hugging Face 在具身智能领域复刻其机器学习开源路线，试图在机器人软件生态尚未定型时抢占开发者心智。定位不是家用家务机器人，而是**低成本物理 AI 实验平台 + 教育硬件 + 开发者平台**——**开源边界恰好停在物理层**（软件全 Apache-2.0，硬件本身仍需付费），与 Reachy Mini 的开源策略一致

### 9.3 一处需要订正的早期笔记

本主题在 30 分钟前曾有一版较短的笔记（已合并删除），其中有两处与源码不符的推测，特此订正以免后续引用出错：

- **旧笔记推测 `btd` = "Beak to Drive?"** —— 源码证实 `btd` 是 **Bluetooth daemon**（BLE GATT 传输层，`btd/src/bluez.rs`、`gatt.rs`、`pairing.rs`），**不拥有机器人任何状态**
- **旧笔记推测 `padd` = "上位外设/动作执行模块"** —— 源码证实 `padd` 是 **gamepad daemon**（读取手柄，`padd/src/tap.rs` 提供 raw input tap），同样**不拥有机器人任何状态**
- **旧笔记写主仓 1046★** —— 实测为 **93★**（web_extract 抓取时点，2026-08-28）

> 这正是 `architecture.md` §1 反复强调的那条设计原则的实例：**`btd`、`padd`、`mediad` 拥有无——它们是传输层**。猜错名字不会改变架构，但会让"谁拥有安全权威"这个关键问题答不出来。

---

## 十、出处节

### 10.1 原文来源

- **X 长文**：https://x.com/tspy/status/2093222346501107739（@tspy / yishan，Microduck 开源双足机器鸭技术架构）
- **主仓库**：https://github.com/pollen-robotics/microduck（Apache-2.0，93★ / 5 fork / 620 commits / v0.10.0）
- **训练仓库**：https://github.com/pollen-robotics/microduck_rl（MjLab + PPO）
- **产品页**：https://pollen-robotics.com/microduck（规格、$399、配色）
- **官方博客**：https://pollen-robotics.com/microduck/blog/introducing-microduck

### 10.2 新闻与商业来源

- IT之家 8月27日：https://www.ithome.com/0/995/306.htm（RK3566 处理器、摄像头、四种配色）
- BlockBeats 快讯：https://www.theblockbeats.info/flash/363929（Apache 2.0 许可、首批 2026 圣诞前发货）
- 搜狐/华尔街见闻：https://m.sohu.com/a/1068574726_130887（Seeed Studio 深圳生产、Clem Delangue 采访）

### 10.3 代码来源（已克隆精读，313 文件 / 48MB）

本笔记第一、三、四、七、八章的**全部技术细节、注释原文与数字均取自源码精读**，非二手转述：

- `docs/design/architecture.md`（622 行）— 服务矩阵、4 条不变量、IPC 选型对比
- `docs/design/robotd-design.md`（956 行）— 控制环、总线拓扑、ID 分配
- `docs/design/updater-design.md`（1467 行）— OTA 目标/非目标、7 决策、重启推论
- `docs/design/restart-order.md` — 重启顺序单点权威文档
- `docs/robot/cheatsheet.md`（793 行）— 操作手册、monitor 可视化、configure 三性质
- `duck-ipc-proto/src/lib.rs`（4836 行）— 39 个 API 方法、v2–v8 版本治理
- `duck-control/src/safety.rs`（580 行）— 写句柄排他、NaN 拒绝、deadman、摔倒判定
- `duck-control/src/policy.rs`（509 行）— 61 维契约、加载即校验、`ensure_runtime` 证伪
- `updater/src/faults.rs`（120 行）— 8 个故障注入点
- `Cargo.toml`（83 行）— workspace 元数据、版本单一真相源
- `policies/README.md`（74 行）— 9 个策略谱系、61 维族理由
- `microduck_rl/README.md`（191 行）— 13 个训练任务、BAM、Backlash 孪生族

**项目路径**：`~/uclaw/project/microduck-analysis/`（34 份文档快照 + 关键源码，960KB）

### 10.4 增补范围标注

- **原文忠实还原**：X 长文的 4 大板块（硬件架构 / RL 与 Sim2Real / 端侧软件工程 / OTA 自愈）在第一章完整保留
- **源码精读增补**（本笔记主体）：第一、三章的注释原文引用、数字、设计决策与自我纠错记录
- **查询拓展增补**：第二章 6 个技术背景主题，为本机读者补充 X 原文未展开的工程原理
- **归纳与判断增补**：第四至八章为本机读者产出的分析框架、趋势预测与关联映射，**非原文内容**
- **产品商业增补**：第九章来源为产品页与新闻报道
- **本机对照增补**：6.2–6.6 节为 Hermes 体系映射，**非原文内容，且遵循"就事论事、不强行关联"原则**

### 10.5 关联笔记

- [2026-08-23-MjLabMicroban-30cm开源人形机器人RL训练与SimToReal](2026-08-23-MjLabMicroban-30cm开源人形机器人RL训练与SimToReal.md) — 同族对照实验，与本篇互补成完整参考
- [2026-08-28-WAM设计空间三轴分类-NVIDIA官方系统综述与VLA路线对决](2026-08-28-WAM设计空间三轴分类-NVIDIA官方系统综述与VLA路线对决.md) — 具身智能范式对照
- [2026-05-11-具身智能2026-世界模型VLA车企入局](2026-05-11-具身智能2026-世界模型VLA车企入局.md) — 行业趋势背景

## 相关笔记

> 注：本笔记正文末尾已含若干链接条目；本节按标准 `## 相关笔记` 标题统一归档，便于检索。

- [2026-08-28-WAM设计空间三轴分类-NVIDIA官方系统综述与VLA路线对决](2026-08-28-WAM设计空间三轴分类-NVIDIA官方系统综述与VLA路线对决.md) — 具身智能范式对照
- [2026-08-28-什么是Eval-为什么它决定了AI项目能不能真正落地](2026-08-28-什么是Eval-为什么它决定了AI项目能不能真正落地.md) — 端到端Eval评估方法对机器人SimToReal适用

