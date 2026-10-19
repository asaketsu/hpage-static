# Zenoh：云到 MCU 的统一 pub/sub/query 协议
> 探索日期 2026-08-15 | 兴趣等级 L2 | 来源 5（官方 README + what-is-zenoh + NTU 性能论文 + zenoh-pico 对比 + ROS2 对比研究）| 领域：IoT

## 摘要
Eclipse Zenoh（Z**ero** **E**ndpoint **N**etwork **O**verhead **H**andover）由 DDS 规范组联席主席 Angelo Corsaro 设计，用一个协议统一 **data in motion（pub/sub）+ data at rest（geo-distributed query）+ computation（queryable）**，覆盖从数据中心到裸机 MCU 的全谱系。NTU 独立实测：peer 模式吞吐比 MQTT 高 1-2 个数量级（8B payload 时 110x，32KiB 时 8x+），单机延迟 10µs，wire overhead 仅 4-6 字节。

---

## 核心发现

### 1. 解决"协议拼凑"问题
现有协议各有断点：DDS 有 pub/sub 位置透明性但上不了互联网尺度、下不到 MCU；CoAP 云中心+CS 架构；MQTT 有 **broker 悖论**（同局域网两设备仍要绕道云端 broker）。Zenoh 三个统一抽象：
- **put/get（pub/sub + query）**：key expression（如 `demo/example/**`）寻址，发布与查询同构
- **queryable**：把"计算"也变成可寻址资源（分布式查询/聚合的载体）
- **首个实现 data at rest 位置透明**：查询无需知道数据在哪个库，Zenoh 负责定位最优存储节点执行

### 2. 性能数据（NTU 2023 论文 + 官方博客，100GbE）
- 单机吞吐：peer 模式最高 **67 Gbps**；多机 51 Gbps
- 对比（8B payload）：**2x DDS / 55x Kafka / 110x MQTT**；32KiB payload 时 2x DDS / 4x MQTT / 8x Kafka
- 延迟：Zenoh P2P **10µs** vs brokered 21µs vs MQTT 73µs vs Kafka 27µs；CycloneDDS 8µs（UDP multicast 优势）略胜
- 嵌入式（zenoh-pico）：吞吐 ~10x XRCE-DDS / 40x MQTT / 55x OPC-UA；wire overhead 比 MQTT 小 64%、比 OPC-UA 小 98%；MQTT 和 zenoh-pico 是唯二能发 8KB+ payload 的
- ⚠️ 社区质疑：DDS 测试用了 RELIABLE QoS（吞吐吃亏），best-effort 下 DDS 与 Zenoh 接近——引用数据时注意测试条件

### 3. 部署形态与运维
```
拓扑：peer-to-peer / brokered(zenohd) / 混合，运行时决定
传输：tcp / udp / tls / quic，默认监听 tcp/[::]:7447
scouting：组播自动发现（--no-multicast-scouting 可关）
REST 插件：端口 8000，curl 直接 put/get ——  curl -X PUT -d '"Hi"' http://localhost:8000/demo/example/test
存储插件：memory/磁盘 volume，按 key_expr 订阅存储 + 查询时返回最新值
admin space：curl http://localhost:8000/@/router/local/** 运行时改配置（热加载插件）
版本注意：v0.6+ 插件不再全量加载，仅加载配置项；git 构建时生态组件必须同源编译（ABI 不稳）
```

### 4. 生态位与 ROS2
- 机器人 R2R 通信和互联网级遥操作的主流选择；CARMA、Indy Autonomous Challenge 自动驾驶项目采用
- **ROS2 官方已有 rmw_zenoh 实现**；学术对比（2023 Turku 团队）：以太网下 CycloneDDS 更快，**WiFi/4G 下 Zenoh 更稳**——无线边缘场景是 Zenoh 的主场
- 2026 IFIP 研究：无人机群 BATMAN-adv mesh 网络上用 Zenoh 做主题中心通信；数字孪生同步中 Zenoh vs ZeroMQ 的 brokerless 对比在进行中
- 双许可 EPL-2.0 / Apache-2.0，Rust 实现（≥1.71），zenoh-pico 支持 MCU（C API）

## 关键概念
> **key expression** 是 Zenoh 的寻址核心：层级式通配（`**` 多层、`*` 单层），put 订阅与 get 查询共用同一命名空间，这是"运动数据与静止数据统一"的实现基础。

> **broker 悖论（MQTT）**：局域网内两设备通信被迫绕行云端 broker，延迟和能耗双输。Zenoh peer 模式 + scouting 让局域通信留在本地，跨网时再走路由——这也是其能效设计（4-6B 开销 + 通信局部性利用）的来源。

## 与现有工作的关联（对 Skill/笔记改进建议）
- **P1**：与既有 `dual-mcu-robot-architecture`（ESP32+STM32 UART）笔记互补——多机器人/机器人-云场景下 UART 点对点不可扩展，Zenoh（zenoh-pico 跑 ESP32 + zenohd 跑 Jetson）是现成的通信骨架；Jetson Orin 本机即可装 `apt install zenoh` 验证
- **P1**：`embodied-ai-control`（ROS2+Gazebo）笔记可补 rmw_zenoh 选项——WiFi 部署时 DDS multicast 不稳是常见痛点
- **P2**：三机 Hermes（jbot/ubot/abot）跨机协调目前走 NFS 共享文件，高频场景可评估 Zenoh queryable 替代轮询（低优先级，现有 NFS 方案够用）

## Actionable Insights
1. 选型速判：局域有线 + 极低延迟 → DDS 仍优；**跨网/无线/4G/MCU 混合 → Zenoh**；纯云端消息队列 → Kafka 生态不可替代
2. zenoh-pico 的 40x MQTT 吞吐 + 4-6B wire overhead，对电池供电传感器网络（LTN 低吞吐网络）意味着显著续航收益
3. REST 插件让 Zenoh 天然可被 curl/脚本即插即测——原型验证成本极低（一条命令起 router + 一条 curl 收发）
4. 插件 ABI 陷阱：`zenohd` 与插件必须同 Rust 版本同源构建，否则 SIGSEGV——生产部署锁定版本组合

## 关键风险与盲点（来源级别标注）
- 【官方验证】性能数字主要来自 ZettaScale 关联的 NTU 测试；【社区观点】DDS 阵营指出 QoS 设置偏不利于 DDS，best-effort 下差距缩小
- 【官方验证】git 主干与发布包兼容性断裂风险（README 明示警告）
- 【盲点】企业级安全（mTLS 细节、多租户隔离）文档较薄，tls/quic 端点存在但治理能力未在本次资料中展开
- 【盲点】大規模 broker 集群运维经验（vs EMQX/Kafka 的成熟运维生态）资料不足

## 一页速查
> Zenoh = pub/sub + 存储查询 + 计算统一协议，云→MCU 一个栈
> 吞吐 67Gbps；8B 时 110x MQTT / 55x Kafka / 2x DDS；延迟 P2P 10µs
> wire overhead 4-6B；zenoh-pico 吞吐 40x MQTT
> 拓扑 P2P/brokered/混合；tcp/udp/tls/quic；默认 7447，REST 8000
> ROS2 rmw_zenoh；以太网 DDS 快、WiFi/4G Zenoh 稳
> 起步：sudo apt install zenoh && zenohd；curl PUT/GET 8000 端口即收发

## 待深入
- zenoh-pico 在 ESP32（本团队 dual-MCU 架构）上的实测集成
- rmw_zenoh 与 rmw_fastrtps 在 Jetson+WiFi 场景的延迟对比
- Zenoh 1.x 与 v0.6 的 API 变更清单（README 仍为 0.6 文档，1.x 的 workspace/session API 有重构）

## 来源列表
1. GitHub README（v0.6 文档）: https://github.com/eclipse-zenoh/zenoh
2. What is Zenoh（官方概念+起源）: https://zenoh.io/docs/overview/what-is-zenoh/
3. NTU 性能论文: arXiv 2303.09419 "A Performance Study on the Throughput and Latency of Zenoh, MQTT, Kafka, and DDS"
4. 官方性能博客: https://zenoh.io/blog/2023-03-21-zenoh-vs-mqtt-kafka-dds
5. zenoh-pico 嵌入式对比: https://zenoh.io/blog/2022-06-09-zenoh-pico-above-and-beyond

## 相关笔记

- [Cron 可靠性工程：从静默失败到生产级定时任务](./2026-08-15-Cron可靠性工程-从静默失败到生产级定时任务.md) — 分布式定时协同的锁与幂等问题
- [ESP32 Marauder WiFi蓝牙攻防工具套件](./2026-08-12-ESP32-Marauder-WiFi蓝牙攻防工具套件.md) — 同为 ESP32 生态，无线协议攻防视角
- [Flix ESP32四旋翼飞控项目](./2026-08-14-Flix-ESP32四旋翼飞控项目.md) — MCU 侧实时通信与控制代表
