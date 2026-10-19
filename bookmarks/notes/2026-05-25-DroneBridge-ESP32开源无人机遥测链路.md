# DroneBridge for ESP32：开源无人机遥测链路

> **来源**：DroneBridge 组织 · GitHub · 2018-08 开源 / 2026-05-16 v2.2.1
> **原文**：https://github.com/DroneBridge/ESP32
> **关联**：[[esp32-projects.md]] [[esp32-lcd-display.md]] [[esp32-s3-voice-gesture-lamp-analysis.md]] [[ESP-IDF 嵌入式开发]]
> **格式**：双格式(MD + HTML) · 含借鉴进化点 · RAG/wiki联动

## 摘要

DroneBridge for ESP32 是 Espressif ESP32 系列芯片的开源无人机遥测/低数据率通信固件，807 star / 187 fork，使用 Apache 2.0 协议。核心功能是将飞行控制器的 UART 串口数据通过 WiFi / ESP-NOW / BLE 转换为双向无线链路，支持 MAVLink、MSP、LTM 等协议，成本约 7 欧元，重量 <8g。最新 v2.2.1 已升级至 ESP-IDF 5.4.4，新增 ESP32-C3/C5/C6 支持、WiFi6 (OFDMA) 和 5GHz 频段。

## 核心内容

### 架构概览

```
┌──────────────┐     UART      ┌──────────────┐    WiFi/ESP-NOW/BLE    ┌──────────────┐
│  飞行控制器   │ ←──────────→ │  ESP32 固件    │ ←──────────────────→ │  地面站/GCS    │
│ (ArduPilot/   │   3.3V UART   │  DroneBridge  │   UDP 14550 / TCP 5760 │ (QGC/Mission   │
│  INAV/Pixhawk)│              │               │                        │  Planner)      │
└──────────────┘              └──────────────┘                        └──────────────┘
```

### 三大通信模式

| 模式 | 协议 | 范围 | 加密 | 适用场景 |
|------|------|------|------|---------|
| **WiFi 标准** | 802.11 b/g/n | ~150m | AES-GCM 256 | 近距离遥控 |
| **WiFi LR** | 802.11 长距离模式 | ~1km | AES-GCM 256 | 中距离遥测 |
| **ESP-NOW** | ESP-NOW LR | >1km | AES-GCM 256 | 无人机编队/蜂群 |
| **BLE** | Bluetooth LE | ~50m | — | 配置/调试 |

### 代码结构

```
main/
├── main.c              # 入口
├── db_serial.c/h       # UART 串口通信
├── db_esp_now.c/h      # ESP-NOW 协议实现
├── db_ble.c/h          # BLE 实现
├── db_mavlink_msgs.c/h # MAVLink 消息解析
├── msp_ltm_serial.c/h  # MSP/LTM 协议解析
├── db_parameters.c/h   # 参数管理
├── http_server.c/h     # Web 配置界面
├── tcp_server.c/h      # TCP 服务端
├── db_timers.c/h       # 定时器管理
├── db_led_indicator.c/h# LED 状态指示
└── db_crc.c/h          # CRC 校验
```

语言分布：C (96%) / JavaScript / Python / HTML / CSS / Shell

### 关键特性

1. **双向透明透传**：串口 ↔ WiFi，支持任意协议（不限于 MAVLink）
2. **连接无关模式**：v2.0 起 MAVLink 和透明模式不再需要连续数据流
3. **AES-GCM 256 全加密**：所有模式包括 ESP-NOW 广播均加密
4. **Web 配置界面**：AP 模式下 `dronebridge.local` 或 `192.168.2.1` 访问
5. **GCS 自动发现**：UDP 14550 自动广播，QGC/Mission Planner 自动连接
6. **LTM/MSPv2 解析**：提高连接可靠性，减少丢包
7. **MAVLink Radio Status 注入**：在 GCS 显示 RSSI

### Drone Light Show Edition (DLSE)

- Skybrush 灯光秀协议支持
- 远程电源管理（sleep/wakeup）
- OTA 空中升级
- WiFi6 (OFDMA) & 5GHz 支持
- ESP32-C3 / C5 / C6 支持

### 开发规则（来自 AGENTS.md）

| 规则 | 说明 |
|------|------|
| 每个函数必须有文档注释 | 安全/安全/可靠性/性能优先 |
| 字符串参数不通过 MAVLink 暴露 | 仅通过 REST API 和 Web 界面 |
| Web 界面编译为单文件 | 避免 ESP32 无法处理多请求 |
| **禁止 OTA 更新** | 明确限制 |
| **禁止 ESP32-C5 支持** | 明确限制 |
| **禁止 esp-idf 5.5+** | 锁定在 5.4.4 |
| **禁止灯光秀专用功能** | 由 DLSE 分支处理 |

## 关键概念

- **ESP-NOW LR**：ESP32 专有的低功耗对等协议，长距离模式需两端均启用 LR-Mode
- **MAVLink Radio Status**：注入的伪 MAVLink 消息，用于在地面站显示链路质量（RSSI）
- **透明透传模式**：不解析协议，直接透传原始字节，支持任意自定义协议
- **AES-GCM 256**：认证加密，同时提供机密性和完整性校验

## 能力边界

- **不支持视频传输**：ESP32 无视频编码能力，仅遥测/低数据率
- **不支持 OTA**：AGENTS.md 明确禁止
- **不支持 ESP32-C5**：AGENTS.md 明确禁止
- **不支持 esp-idf 5.5+**：锁定在 5.4.4
- **无 HTTPS 支持**：Web 界面仅 HTTP
- **UDP 需主动注册**：GCS 需至少发送一个包（如心跳）才能注册为端点

## 最佳实践

- 使用官方测试过的 PCB 板（非通用开发板），确保天线和电源设计
- 避免使用 ESP32 标有 TX/RX 的引脚（通常连接内部串口输出）
- 飞行控制器 UART 端口设为 3.3V 电平
- UDP 模式下 GCS 需添加 ESP32 为 UDP 目标
- 远程使用时优先选择 ESP-NOW LR 或 WiFi LR 模式

## 🔍 借鉴学习进化点

| # | 点 | 原文要点 | 对当前系统的借鉴 | 行动计划 |
|---|-----|---------|---------------|---------|
| 1 | **AGENTS.md 开发规则** | 明确的开发规则、禁止事项、构建流程文档化 | 项目级 AGENTS.md 是协作规范的最佳实践 | 已有 AGENTS.md，可参考其"禁止事项"写法来补充自己的 |
| 2 | **单文件 Web 界面** | Web 界面编译为单文件，避免 ESP32 无法处理多请求 | 嵌入式 Web 服务的稳健设计模式 | 可借鉴到任何嵌入式 Web 服务场景 |
| 3 | **MAVLink Radio Status 注入** | 注入伪消息补充链路质量信息 | 类似思路可用于 Hermes 的链路/健康状态注入 | 已有 agent-health-check skill，可参考此模式 |
| 4 | **协议无关透明透传** | 支持任意协议，不绑定 MAVLink | 通用通信架构设计思路 | 对多协议适配场景有参考价值 |
| 5 | **ESP-NOW 编队通信** | 低成本无人机蜂群通信方案 | 多节点通信架构参考 | 对多 Agent 协作场景有启发 |

**三问自检结果**：
- ✅ 可复用方法/模式？AGENTS.md 开发规则格式 + 单文件 Web 界面设计 → 可借鉴
- ✅ 可优化自身配置？无直接相关（嵌入式领域）
- ✅ 关键事实？DroneBridge 是 ESP32 无人机通信标杆项目，807 star，v2.2.1 升级 IDF 5.4.4 → 已记入 Memory

## 🔗 RAG / Wiki 联动

### 当前状态
- ESP32 相关笔记：已有 esp32-projects.md、esp32-lcd-display.md、esp32-s3-voice-gesture-lamp-analysis.md
- ESP-IDF 开发：已有 esp-idf-project-create skill
- 嵌入式 Web 服务：无专门笔记

### 改进方案
1. 将 DroneBridge 的 AGENTS.md 开发规则模式参考到自身项目规范
2. 与 esp-idf-project-create skill 联动，补充 ESP32 通信项目模板

### 已执行操作
- ✅ 三问自检完成
- ✅ 关联已有笔记建立双链
## 相关笔记

- [[esp32-projects.md]] — ESP32 项目总览
- [[esp32-lcd-display.md]] — ESP32 LCD 显示项目
- [[esp32-s3-voice-gesture-lamp-analysis.md]] — ESP32-S3 语音手势灯分析
- [[esp-idf-project-create]] — ESP-IDF 项目创建技能
