# Microduck 双足机器鸭：从推文到可运行全栈仿真项目

> **出处**：https://x.com/tspy/status/2093222346501107739 （yishan《Microduck 开源双足机器鸭技术架构》长文）
> **项目落地**：`~/uclaw/project/microduck/`（32 测试全绿 + 5 demo 通过）
> **关联**：[Microduck 开源双足机器鸭-Rust 微服务与 SimToReal 全栈拆解](./2026-08-28-Microduck开源双足机器鸭-Rust微服务与SimToReal全栈拆解.md)（上游文档拆解层）
> **日期**：2026-08-29 · 系列第 2 篇（工程实现篇）

---

## 1. 这篇笔记解决什么

上一篇拆解了 Microduck（Hugging Face/Pollen Robotics 出品的 25cm/800g/$399 开源双足机器鸭）**是什么**。这一篇记录把它**做出来**的过程：用纯 NumPy 复刻其核心架构，在 Jetson Orin Nano 上跑通从物理仿真到 OTA 自愈的全链路，并把三个物理 bug 的根因定位过程完整留存。

| 交付物 | 位置 | 验证 |
|--------|------|------|
| 8 模块仿真代码 | `src/microduck_sim/` | 32/32 pytest |
| 5 段演示 | `scripts/demo.py` | 全部 PASSED |
| 13 节详细教程 | `docs/tutorial.md` | 含踩坑表+差距表 |
| 打印件情报 | `references/hardware/` | 官方+自制双路线 |

## 2. 用户最关心的答案：打印件模型在哪

### 官方 Microduck：STL 未发布

| 项 | 状态 |
|----|------|
| 软件（microduck / microduck_rl） | ✅ Apache-2.0 已开源 |
| 硬件设计文件 | ⚠️ 声明 **CC BY-SA-NC**（非商用署名相同方式共享），**STL 尚未放出** |
| 获取方式 | $399 整机预售（2026-08-27 开启，圣诞前发货，四配色） |

### 真正可打印的答案：Open Duck Mini v2（同作者！）

调研关键发现：Microduck 核心团队成员 **Antoine Pirrone**（GitHub: apirrone，Pollen Robotics R&D 工程师，Rhoban 成员）的 Microduck **前身项目** Open Duck Mini v2 完全开源可自制：

| 资源 | 地址 |
|------|------|
| 主仓库（35 个 STL 直接下载） | github.com/apirrone/Open_Duck_Mini（Apache-2.0，3.5k★） |
| Onshape CAD 源文件 | cad.onshape.com/documents/64074dfcfa379b37d8a47762/... |
| BOM（英文/中文） | Google Sheets / zihao-ai.feishu.cn/wiki/AfAtw69vRigXaRk5UkbcrAiLnJw |
| 端侧运行时 | Open_Duck_Mini_Runtime（树莓派 Zero 2W） |
| GPU 训练场 | Open_Duck_Playground |

- **整机 BOM <$400**（与官方整机同价，但可自制可改装）
- 打印参数：PLA 15% infill（唯一例外足底 TPU 40%）
- 社区实测提醒：最大坑是 sim2real——MuJoCo 完美步态遇到真机关节旷量/舵机延迟就会摔，有玩家做了 **40+ 次逐关节偏移标定**才走稳
- 血统链：Open Duck Mini v2 (2025) → 作者入职 Pollen → Microduck (2026-08-27)。同鸭形、同 RL 路线（MuJoCo+PPO+ONNX）、同 BDX 灵感

全套打印指南/装配指南/电机配置/接线图已存 `references/hardware/`（7 个文件）。

## 3. 复刻了什么：架构对照表

| 层 | 上游（生产级） | 本机（教学级缩影） | 保真点 |
|----|--------------|------------------|--------|
| 策略契约 | obs[61]→action[14] @50Hz | **逐 bit 相同** | 布局/未绑定槽位/切换阈值全对齐 obs.rs |
| 安全层 | safety.rs 唯一写句柄 | 语义相同 | NaN 拒绝/200ms 跌倒去抖/deadman 站立不软瘫 |
| 执行器 | BAM M6 电压控制律 | 结构保留 | 电池 sag→力矩上限、20ms 延迟队列、三因子 DR |
| 动力学 | MuJoCo Warp 3D | 平面 LIP+倒立摆 | ZMP 钳制足底 ±4cm、接地腿耦合 |
| 训练 | rsl_rl PPO 4096 envs | NumPy PPO 单 env | clip/GAE/minibatch/熵退火全骨架 |
| 端侧 | Rust 19 crate 守护进程 | Python 线程仿真 | JSON-RPC 2.0 总线/意图隔离/策略热切换 |
| OTA | updaterd A/B+minisign | 状态机仿真 | 签名→切换→健康门禁→自愈回滚三路径 |

## 4. 实测数据（全部本机真跑）

```
[物理] 零控制 8.6° 倾斜: 0.86s 跌倒（不稳定平衡验证 ✓）
[控制] 站立恢复: 5.7° → θ=0.000°（1500 ticks 不倒）
[控制] 行走: cmd 0.30 m/s → 实际 0.26 m/s（87% 跟踪，x+9.95m）
[控制] 鲁棒性: 10/10 DR seeds 存活（电池/摩擦/延迟随机化下）
[PPO ] 40 iter 平均回报 −462 → −11（4 秒，含 vs 零动作对照）
[OTA ] 崩溃固件自动回滚 / 坏签名中止告警 / 正常提交三路径 ✓
[测试] 32/32 通过（关节索引/奖励符号/NaN 防护锁死）
```

## 5. 三个物理 bug 的根因定位（最有价值的部分）

按用户调试偏好（先根因后动手，不堆补丁），每次翻车都做了完整定位：

### Bug 1：足底固定 vs 自由关节（LIP 发散到 1e30）

- **症状**：任何控制器下质心 x 爆炸到 10²⁹
- **根因**：第一版把关节角当无负载自由积分——舵机是**位置伺服弹簧**（τ=K(a−q)），接地腿的 q 被重力顶住不会归零，位置误差持续存在才是"持续力矩"的物理来源。自由关节模型里误差追踪完就消失，ZMP 支撑随之消失
- **修法**：接地耦合 q_hip≈θ、q_ank≈(x−foot_c)/z，力矩从伺服误差产生

### Bug 2：齿隙建模成力矩死区（机器人停在 23° 倾斜）

- **症状**：PD 站立稳态误差 23°，小力矩全被吞
- **根因**：我把 ±1° 齿隙实现成 `|τ|<0.02 → 0`——非物理。上游 BacklashEncoderBamActuator 的齿隙是**位置域**现象（被动铰 + 编码器在输出侧读"穿过"齿隙的位置），观测维度都不变
- **修法**：删力矩死区；齿隙只作为观测层概念保留在 constants（BACKLASH_DEG）

### Bug 3：upright 奖励符号反（value loss 34506）

- **症状**：PPO value loss 爆到 5 万，奖励曲线锯齿
- **根因**：`0.5·(−cos θ − 1)` 在直立时=−1 而非 0——投影重力 z=−cos θ，直立=−1，正确式是 `0.5·(−pgz + 1)`
- **修法**：一行修正 + 测试锁死符号约定（对齐上游"reward sign conventions"测试哲学）

另有一个控制器结构发现：踝 ZMP 控制里回灌 q_ank 反馈会在 dz 饱和时与位置环对拉、速度锁死在 0——**纯 ZMP 偏置结构**才有效。数值扫描出稳定窗口 g∈[0.5,1.2]，已写进 controllers.py docstring。

## 6. 教程文档（docs/tutorial.md，13 节）

0. 仓库定位与三层对照表 → 1. 环境（仅需 numpy）→ 2. 五分钟上手 →
3. 模块地图（阅读序=学习路径）→ 4. 61 维契约逐 index 讲解（含上游坑点表）→
5. 安全层四规则 → 6. BAM 执行器滤波链 → 7. 双足动力学三构件+两个非显然决策 →
8. 解析控制器（RL 对手盘）→ 9. PPO 骨架 → 10. robotd 微服务+OTA →
11. **踩坑 FAQ 表（5 个真踩过的坑）** → 12. **与上游诚实差距表** → 13. 延伸路径

## 7. 与本机体系的关联分析

| Microduck 模式 | 本机可借鉴点 |
|---------------|-------------|
| 全策略共享 61 维观测契约 | Hermes tool 层可借鉴：工具输出 schema 统一后，模型/技能可热切换 |
| 安全层唯一写句柄（借用检查器强制） | 危险操作收敛到单一入口 + 校验，上层只提交"意图" |
| 执行器保真度>物理引擎保真度 | 边缘部署的仿真验证要建到硬件非理想性（电压/延迟/摩擦），而非理想刚体 |
| updaterd 三服务存活 robotd 死亡 | 看门狗架构：恢复路径（配置/更新/网络）绝不依赖被监控对象 |
| OTA 健康门禁+自愈回滚 | 本机 Hermes 升级流程可加 health gate（升级后自检不过自动回退） |

## 8. 下一步

- 真机自制路线已铺好：按 `references/hardware/` 的 Open Duck Mini v2 BOM 采购（Feetech STS 舵机+树莓派 Zero 2W，<$400）
- 真训练需 CUDA 机器：microduck_rl Quickstart（`uv run train Mjlab-Velocity-Flat-MicroDuck`，4096 envs 1-2h）
- 待办：robotd JSON-RPC 权限隔离模式移植到 Hermes tool 层的可行性评估

## 9. 出处与许可

| 内容 | 来源 | 许可 |
|------|------|------|
| 触发长文 | x.com/tspy/status/2093222346501107739 | 作者 yishan |
| 上游软件 | github.com/pollen-robotics/microduck + _rl | Apache-2.0 |
| Microduck 硬件 | 未发布 | CC BY-SA-NC |
| Open Duck Mini v2 | github.com/apirrone/Open_Duck_Mini | Apache-2.0 |
| 上游源码快照/设计文档 | 本机 `project/microduck-analysis/`（第一篇笔记产物） | 上游同许 |
| 本项目代码 | 本机 `project/microduck/` | 原创缩影 |


## 相关笔记

- [DUCK-Pi_5树莓派主控移植完整方案](./2026-08-29-DUCK-Pi_5树莓派主控移植完整方案.md) — 同日姊妹篇，硬件主控移植
- [Microduck开源双足机器鸭-Rust微服务与SimToReal全栈拆解](./2026-08-28-Microduck开源双足机器鸭-Rust微服务与SimToReal全栈拆解.md) — 系列第 1 篇，架构拆解层
