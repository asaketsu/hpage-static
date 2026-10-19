# ESP32-H4：双核 RISC-V + BLE 5.4 + Thread/Matter SoC

> 探索日期: 2026-08-18 | 兴趣等级: L3 | 来源数量: 6 篇 | 类型: auto-explore

## 摘要

ESP32-H4 是乐鑫 2024 年 4 月发布的低功耗双核 RISC-V SoC，集成 802.15.4（Thread 1.3 / Zigbee 3.0 / Matter）与自研蓝牙 5.4 双无线收发器。96MHz 双核 + 384KB SRAM + 最多 4MB PSRAM，无 Wi-Fi。是 ESP32-H2（单核/BLE 5.0）的增强迭代，定位电池供电的智能家居边缘节点、LE Audio 可穿戴、医疗传感器、低功耗传感网络。与 ESP32-C6（Wi-Fi 6 + Thread/BLE 5.0 的全能选手）形成互补：H4 主打极致低功耗 + BLE 5.4 蓝牙音频。

## 核心发现

### 1. 双核 RISC-V 96MHz + DSP 扩展 — H2→H4 的最大升级

- 2× 32-bit RISC-V @ 96 MHz（H2 为单核同频）
- 集成 DSP 扩展指令集（加速浮点/信号处理，对传感器融合/LE Audio 解码有用）
- 384KB on-chip SRAM（H2 为 320KB）+ 128KB ROM + 外部 PSRAM 最高 4MB
- GPIO: 36 个（H2 为 24），含触摸感应 GPIO
- 双核的意义：一核跑协议栈（Thread/BLE 控制面），另一核跑应用逻辑，避免协议栈中断干扰实时任务 — 这是 H2 单核做 Thread Mesh 节点时的痛点

### 2. BLE 5.4 — 乐鑫首个，且支持 LE Audio 全栈

- **Bluetooth Low Energy Audio (LE Audio)**：BIS（Broadcast Isochronous Stream）+ CIS（Connected Isochronous Stream）
- **Connection Subrating**：极低占空比，电池寿命显著延长
- **Bluetooth Mesh 1.1**：Mesh 网络节点
- **LE Code PHY**：长距离通信（4x range）
- 这是乐鑫 H2 之后首次大幅提升蓝牙版本（H2 停在 BLE 5.0），也是整个 ESP32 家族最高蓝牙版本
- **对 Hermes/Jetson 场景的关联**：Jetson 跑 STT/TTS 时，LE Audio 可作为低功耗音频输入通路（参考 voice-assistant-service-stack 的蓝牙接入层）

### 3. Thread 1.3 + Matter 支持 — 智能家居标配

- IEEE 802.15.4 收发器原生支持 Thread 1.3、Zigbee 3.0
- Matter 协议支持通过 ESP-Matter 库提供，官方文档明确 "ESP-Matter will provide support for ESP32-H4, enabling battery-operated Matter devices"
- 适合 Matter over Thread 电池设备（开关、传感器、锁具）
- **与 Hermes 智能家居场景的关联**：若未来在 Jetson 上搭建 Matter Controller 网关，ESP32-H4 可作为 Thread 边界路由器或末端节点

### 4. 安全能力 — 首次引入 Power Glitch Detector

- ECC 安全启动（Secure Boot）
- AES-128/256-XTS Flash 加密
- 密码学加速器（加密运算硬件加速）
- TRNG（真随机数生成器）
- **Power Glitch Detector**：与 ESP32-C61 同级，防电源毛刺侧信道攻击（H2 没有）

### 5. ESP-IDF 支持状态（截至 2026-08）

- ESP-IDF master 分支已提供预览支持
- 功能支持度仍有部分 "⏳ Unsupported"，非全量 GA
- 建议开发时使用 ESP-IDF HEAD of master，待正式发布版本后再生产部署

## 与现有工作的关联

- **IoT 笔记积累**：explore/ 目录下 ESP32 系列笔记已有 ESP32-H2 等，H4 作为 H2 增强版应纳入对照
- **Jetson/嵌入式 AI**：H4 的 PSRAM + DSP 扩展使其在传感器预处理场景有潜力（参考 tinyml 笔记）
- **ESP-IDF 开发**：H4 与已部署的 ESP32-S3 项目在 SDK 层面兼容，但 802.15.4 协议栈需独立集成
- **LLM 推理优化关联**：H4 不适合跑 LLM，但 LE Audio + Jetson 的语音管线（STT→LLM→TTS）是一个完整的 Edge AI 语音助手架构

## 关键对比

| 维度 | ESP32-H2 | ESP32-H4 | ESP32-C6 |
|------|---------|---------|---------|
| 核数 | 1 | 2 | 1 |
| 频率 | 96 MHz | 96 MHz | 160 MHz |
| SRAM | 320 KB | 384 KB | 256 KB |
| BLE | 5.0 | 5.4（含 Audio） | 5.0 |
| Wi-Fi | 无 | 无 | Wi-Fi 6 |
| Thread | ✓ | ✓ (1.3) | ✓ |
| Matter | ✓ | ✓ | ✓ |
| GPIO | 24 | 36 | - |
| Power Glitch | ✗ | ✓ | ✓ |

## 行动建议

- **P1**：评估 H4 在 Jetson 语音助手场景中的 LE Audio 接入可行性（低功耗音频输入 vs USB 麦克风）
- **P1**：跟踪 ESP-IDF master 中 H4 的 GA 版本发布时间
- **P2**：若智能家居项目需要 Matter over Thread 电池节点，H4 是 ESP32 家族最优选
- **P2**：H4 vs H2 选型决策树写入现有 ESP32 笔记（双核场景选 H4，单核极致低功耗选 H2）

## 关键风险与盲点

- ESP-IDF 对 H4 仍处于预览支持阶段，生产部署有 SDK 不稳定性风险
- 双核 96MHz 性能仍然有限（Dhrystone 约 50 DMIPS），不适合跑复杂协议栈 + 应用逻辑的重负载
- 无 Wi-Fi 限制：无法独立接入云端，必须配合 Thread Mesh 网关或 BLE 桥接
- 功耗数据官方尚未提供完整数据表，电池寿命估算需实测

## 一页速查

> **ESP32-H4 = 2× RISC-V 96MHz + BLE 5.4(含LE Audio) + Thread 1.3/Matter + 802.15.4 + 4MB PSRAM + 无 Wi-Fi**
> H2 增强版，多一核 + 蓝牙音频 + 更多内存 + 电源毛刺检测
> 适合：电池供电智能家居节点、LE Audio 可穿戴、低功耗医疗传感器
> 不适合：需 Wi-Fi 直连云端的场景（用 C6/S3 代替）
> ESP-IDF 预览支持中，生产部署需等 GA

## 来源

1. Espressif 官方产品页：https://www.espressif.com/en/products/socs/esp32-h4
2. Espressif 新闻 ESP32-H4 Sample：https://www.espressif.com/en/news/ESP32_H4_Sample
3. Espressif 新闻 Announcing ESP32-H4：https://www.espressif.com/en/news/ESP32-H4
4. Hackster.io ESP32-H4 发布报道：https://www.hackster.io/news/espressif-s-esp32-h4-offers-dual-core-low-power-bluetooth-5-3-low-energy-ieee-802-15-4-capabilities-a63157f6cd24
5. CNX Software ESP32-H4 规格详解：https://www.cnx-software.com/2024/04/15/esp32-h4-low-power-risc-v-soc-802-15-4-bluetooth-5-4-le
6. Ineltek ESP32-H4 技术解读：https://www.ineltek.com/en/esp32-h4-802-15-4-bluetooth-5-4-low-power-soc-von-espressif-angekuendigt
7. DroneBot ESP32 选型指南 2026：https://dronebotworkshop.com/esp32-2026
8. Espressif Developer Portal H4 状态：https://developer.espressif.com/hardware/esp32h4

## 相关笔记

- [ESP32给眼睛-本地视觉决策闭环](../2026-08-19-ESP32给眼睛-本地视觉决策闭环-反应契约策略层三升级路线的完整教程拆解.md) — ESP32视觉决策应用侧
- [ESP32-Marauder攻防套件](../2026-08-12-ESP32-Marauder-WiFi蓝牙攻防工具套件.md) — 同系硬件安全工具