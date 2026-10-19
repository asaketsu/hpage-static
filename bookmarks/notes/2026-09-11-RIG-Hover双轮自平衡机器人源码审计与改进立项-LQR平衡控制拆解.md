# RIG-Hover 双轮自平衡桌面机器人：源码审计 + 改进立项 + LQR 平衡控制拆解——rig-hover-enhanced 项目开篇

> **来源**：微信公众号《免费开源，RIG-Hover 双轮桌面AI机器人，ESP32 主控、六轴IMU 自平衡、语音交互、萌表情动画、MCP 远程控制》2026-09-10
> **原文链接**：https://mp.weixin.qq.com/s/GYEdyB7uKYxo9zq2NQobow
> **上游仓库**：https://github.com/LuwuDynamics/rig_omni（Apache 2.0，已 clone 完整源码审计）
> **项目落地**：`~/uclaw/project/rig-hover-enhanced/`（upstream 快照 + 审计文档 + 改进路线图，已 git init）
> **抓取方式**：微信桌面 UA + js_content 提取 3.1KB + GitHub 源码 clone 逐文件精读
> **笔记日期**：2026-09-11
> **关联笔记**：《为不信任而设计》（MCP 鉴权改进依据）《Jetson跑24小时》（遥测方法论）《dual-mcu-robot-architecture》《servo-arm-control》

---

## 零、结论先行

**RIG-Hover 是 ESP32 桌面机器人里工程完成度最高的开源项目之一：单颗 ESP32-S3 上跑离散 LQR 全状态反馈平衡控制 + 三任务优先级架构（自平衡>表情>语音）+ MCP 工具框架 + Web 调参服务器 + CLAUDE.md AI 协作宪法。已立项为独立改进项目 `rig-hover-enhanced`，审计发现 1 个 P0（增益硬编码）+ 2 个 P1（安全层缺失/死代码）+ 2 个 P2（UART 时序矛盾/MCP 裸奔）+ 2 个 P3，改进路线图 A/B/C 三阶段已落盘。**

## 一、这是什么：硬件与架构（微信文 + 源码双重核实）

| 维度 | 规格（源码/文互证） |
|------|-------------------|
| 主控 | ESP32-S3-WROOM-1 双核 240MHz |
| 平衡传感 | QMI8658C 六轴 IMU（I2C，SDA=14/SCL=48） |
| 动力 | 2×FOC 无刷电机（实时解算转子位置换相）+ 高分辨率编码器 |
| 头部 | EM3 总线舵机 ±70°（UART，TX=46/RX=38） |
| 显示 | 1.09 寸 240×240 圆形 TFT（LVGL + EAF 动画引擎） |
| 电池 | 500mAh 高倍率，续航 1.5h |
| 构型创新 | **低重心极窄双轮**（反传统平衡车宽轮距高重心）——桌面/书本/键盘碎片场景滑行 |

**软件架构三板型**（CLAUDE.md 源码核实）：单代码库三产品（Puppy 机器狗/Hover 双轮/Arm 机械臂），板级抽象层 + 共享子系统 + Kconfig 编译时选择——"一份共用核心，各形态独立扩展"。

## 二、平衡控制核心拆解（xgo.cc 785 行精读，最有价值的部分）

### 2.1 离散 LQR 全状态反馈（L517-545 逐行核实）

```cpp
// u = -K·x, Ts≈6ms
// x1 位置误差(m)  x2 速度误差(m/s)  x3 俯仰误差(deg)  x4 俯仰角速度(deg/s)
const float pitch_ref = imu_zero * cosf(q_head * PI / 180.0f);  // 头部姿态前馈补偿
lqr_x  = wheel_x - stable_pos;      // 轮位置
lqr_vx = wheek_vx - vx;             // 轮速
lqr_q  = pitch - pitch_ref;         // 俯仰
lqr_dq = dq;                        // 俯仰角速度
temp_u = -(lqr_k[0]*lqr_x + lqr_k[1]*lqr_vx + lqr_k[2]*lqr_q + lqr_k[3]*lqr_dq);
```

**增益**（L411-414 硬编码）：`lqr_k = {1400.0, 6.8, 32.0, 1.6}`

### 2.2 四个工程细节（源码级发现，微信文没讲的）

| 细节 | 实现 | 评价 |
|------|------|------|
| **头部姿态前馈** | `pitch_ref = imu_zero·cos(q_head)`——头转动改变质心 | 优雅：把头部交互（转头看人）与平衡解耦 |
| 静摩擦死区补偿 | \|u\|>20 时额外 ±10 | 工程近似，但阈值硬编码 |
| yaw 差动解耦 | `yaw_u = k_yaw·(yaw - q_head - stable_yaw)`，叠加到双轮 | 头部角度参与 yaw 目标——头转=身体不转 |
| 停机保护（半套） | `robot_state==0` → 零转矩；IMU 未初始化 → 零转矩 | 有基础保护但无 pitch 超限关断（P1 缺口） |

### 2.3 任务时序（实测矛盾点）

- `XGO_TASK_INTERVAL_MS=4`（board_config.h）vs 注释 `Ts≈6ms`——**宏与实际周期不一致**（P2）
- `xgo_control()` 内三个 `vTaskDelay(2ms)` 串行（舵机写→转矩写→反馈读）≈6ms 实际周期
- 反馈轮询：rx_index 循环读 5 个寄存器（轮1/轮2/2 个编码器/舵机）——每个寄存器刷新率 ≈30ms

## 三、MCP 工具框架亮点（mcp_server.cc 665 行）

- **通用工具前置**利用 prompt cache（源码注释明说）——工具列表排序影响缓存命中，细节见功力
- 板级扩展点：`InitializeTools` 虚函数——Hover 板增运动工具不碰通用框架
- **P2 缺口**：无鉴权——LAN 可接受，公网暴露即遥控后门。改进方向：《不信任八模式》模式 7（任务级权限租约）+ 会话 token

## 四、审计发现汇总（P0-P3 八项）

| 级 | 发现 | 改进 |
|----|------|------|
| **P0** | lqr_k/pid_*/k_yaw/死区阈值全部硬编码 | 参数 NVS 化 + hover_debug_server 扩展增益下发（扩展点现成） |
| P1 | 无 pitch 超限保护（倒地会持续抽搐） | FALLING→DOWN 状态机 + soft-stop + 显式恢复命令 |
| P1 | 60 行注释掉的旧 PID 级联（L491-516） | 删除（git 有历史） |
| P2 | Ts 注释 6ms vs 宏 4ms 矛盾；UART 三段 2ms 串行 | 注释校准 + 反馈事件驱动化 |
| P2 | MCP 运动工具无鉴权 | 会话 token + confirm 标志 |
| P3 | 电压 1 次/分钟（500mAh 瞬态失明） | 1-10Hz 采样 + 两级阈值（3.5V 警告/3.3V 停机） |
| P3 | 无平衡遥测导出 | 环形缓冲 + CSV 导出（调参基建） |

## 五、项目立项（rig-hover-enhanced）

**目录已建**：`~/uclaw/project/rig-hover-enhanced/`
- `upstream/` 完整快照（只读铁律——与上游可 diff）
- `docs/00_source_audit_and_roadmap.md` 审计+路线图 8.5KB
- README + git init

**改进路线三阶段**：

| 阶段 | 内容 | 工作量 |
|------|------|--------|
| A（安全与可调） | 参数 NVS 化 + 安全状态机 + 清死代码 | 2.5-3.5 天 |
| B（通信与保护） | UART 事件驱动 + MCP 鉴权 + 电池两级保护 | 3.5-4.5 天 |
| C（研究价值） | 遥测环形缓冲 + **LQR 增益自整定**（辨识→建议闭环） | 4-6 天 |

**执行原则**：upstream 只读，改进走 patches/ overlay（duck-p3-pilot 零侵入模式同源）；本机不编译 ESP32 固件（无 idf 环境），代码就绪留待真机/CI。

## 六、与既有资产的协同

| 资产 | 协同 |
|------|------|
| dual-mcu-robot-architecture | RIG-Hover 是"单 MCU 全栈"的反例样本——ESP32-S3 单芯片扛实时控制+WiFi+语音+显示，对照我们双 MCU（ESP32+STM32）架构的适用边界 |
| servo-arm-control | EM3 与 STS3215 同源 Feetech 协议族——串行舵机协议层可互换验证 |
| esp32-edge-impulse | GC0308 摄像头的人脸检测转头——端侧推理升级位 |
| microduck 训练链 | C2 的 LQR 辨识与 RL 训练的模型辨识同源——控制理论路线 vs RL 路线的对照样本 |

## 七、批判性审视

1. **微信文的"毫米级运动控制"是营销话术**：FOC+高分辨率编码器是硬件能力，实际控制精度受 UART 30ms 反馈刷新率限制——控制带宽瓶颈在通信不在电机
2. **"二次方增长"没出现在这但"6ms 周期"的余量存疑**：ESP32-S3 双核 240MHz 上 LQR 四态计算本身微秒级，但 WiFi+LVGL+音频共享 CPU——注释说平衡任务"优先级最高会抢占"，实际抢占延迟未量化
3. **Apache 2.0 + 商业公司（LuwuDynamics）开源**：典型产品引流模式——代码质量高于纯社区项目（有 CLAUDE.md/CI 三向构建），但长期维护依赖公司战略
4. **500mAh/1.5h 续航的矛盾**：高倍率放电 + 1.5h 续航意味着平均电流 ~333mA——FOC 双电机全速时可能远超，续航数据大概率是静态交互场景
5. **我们立项的诚实定位**：无真机情况下 A/B 阶段验收只能到代码 review 级——C2（LQR 辨识）依赖真机遥测数据，采购决策前 C2 只是规划

## 八、金句提取

> "自平衡是高频实时任务，优先级最高，会抢占 CPU 完成姿态稳定，避免机器人摔倒。"（架构哲学：控制优先于一切）

> "To speed up the response time, we add the common tools to the beginning of the tools list to utilize the prompt cache."（MCP 源码注释——工具排序优化缓存命中的细节功力）

> "不是简单的屏幕聊天，而是一个有物理存在感、能用身体表达情绪的智能生命体。"（微信文的产品定位）

## 九、局限性

1. 源码审计基于静态精读（xgo.cc/hover_board.cc/application.cc/mcp_server.cc 四核心文件 + CLAUDE.md），未编译验证——P2 的时序矛盾结论来自代码推算非实测
2. 微信文 3.1KB 为产品宣传口径，技术细节以源码为准（已交叉，硬件规格两源一致）
3. EAF 表情引擎/LVGL/audio 子系统未逐文件审（非本次关注核心）
4. C2 工作量估算基于控制理论经验外推，未做可行性验证
5. 未联系上游确认改进 PR 接受意愿——patches 模式先自用

## 出处标注

| 章节 | 来源类型 |
|------|---------|
| 一 | 微信文 + **源码交叉核实**（board_config.h 引脚/QMI8658C） |
| 二至四 | **源码逐行精读**（xgo.cc L25-605 / mcp_server.cc / CLAUDE.md） |
| 五 | **项目落地**（rig-hover-enhanced 目录 + 审计文档，git init） |
| 六至七 | **协同分析与批判**（本笔记扩展） |

## 相关笔记

- [ESP32-S3与Kindle8物联网交互项目](./2026-08-07-ESP32-S3与Kindle8物联网交互项目-TCP通信与多线程实战.md) — ESP32 工程实战
- [ESP32-CAM车库门AI自主开发实战](./2026-08-01-ESP32-CAM车库门AI自主开发实战.md) — ESP32 AI 端侧
- 项目落地：~/uclaw/project/rig-hover-enhanced/（PROGRESS.md 与审计文档）
