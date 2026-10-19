# ESP32 Marauder — ESP32 WiFi/Bluetooth 攻防工具套件

> GitHub: https://github.com/justcallmekoko/ESP32Marauder
> Wiki: https://github.com/justcallmekoko/ESP32Marauder/wiki (161 页)
> ⭐ 11.9k stars | 1.4k Forks | MIT License
> 官方商店: https://www.justcallmekokollc.com
> 评分: ⭐⭐⭐⭐⭐ (5/5) — ESP32 平台最完整的无线安全攻防工具，安全研究必备

## 一句话定位

**基于 ESP32 的 WiFi/Bluetooth 进攻和防御工具套件，11.9k stars，覆盖扫描/嗅探/攻击/伪装/wardriving 全链路，支持 ESP32 全系列芯片（含最新 C5），Flipper Zero 集成，161 页 wiki 文档。**

## 核心能力矩阵

### WiFi 攻击

| 功能 | 命令 | 说明 |
|------|------|------|
| **Beacon Spam** | `attack` | 广播虚假 AP，随机/列表/克隆三种模式 |
| **Deauthentication** | `sniffdeauth` | 发送去认证帧，强制设备断开 |
| **Probe Request** | `attack` | 主动探测目标 AP |
| **PMKID 捕获** | `sniffpmkid` | 抓取 PMKID 用于离线破解 |
| **Karma 攻击** | `karma` | 伪装成目标设备信任的 AP |
| **Evil Portal** | `evilportal` | 钓鱼 WiFi 热点 |
| **Pwnagotchi** | `sniffpwn` | 捕获握手包 |

### WiFi 防御/侦察

| 功能 | 命令 | 说明 |
|------|------|------|
| **AP 扫描** | `scanap` | 扫描周围所有接入点 |
| **Station 扫描** | `scansta` | 扫描已连接的设备 |
| **MAC 跟踪** | `mactrack` | 跟踪特定 MAC 地址 |
| **Ping 扫描** | `pingscan` | 主动探测 |
| **信号监控** | `sigmon` | 信号强度实时监控 |
| **Raw 嗅探** | `sniffraw` | 原始 802.11 帧捕获 |
| **Beacon 嗅探** | `sniffbeacon` | 信标帧捕获 |
| **ESP 设备探测** | `sniffesp` | 发现其他 ESP32 设备 |
| **信道扫描** | `channel` | 指定信道扫描 |
| **SSID 列表** | `ssid` / `list` | 管理 SSID 列表 |

### Bluetooth 攻击

| 功能 | 命令 | 说明 |
|------|------|------|
| **BT Spam** | `btspamall` | 蓝牙垃圾消息广播 |
| **Samsung BLE Spam** | `samsungblespam` | 针对 Samsung 设备的 BLE 弹窗攻击 |
| **Swift Pair** | `swiftpair` | Windows Swift Pair 弹窗攻击 |
| **Sour Apple** | `sourapple` | iOS AirDrop 弹窗攻击 |
| **蓝牙嗅探** | `sniffbt` | 蓝牙流量捕获 |
| **FindMy** | `findmy` | Apple FindMy 网络探测 |

### Wardriving（GPS 记录）

| 功能 | 命令 | 说明 |
|------|------|------|
| **WiFi Wardriving** | `wardrive` | 记录 WiFi AP 地理位置信息 |
| **BT Wardriving** | `btwardrive` | 记录蓝牙设备地理位置信息 |
| **GPS 数据** | `gpsdata` | 读取 GPS 模块数据 |

### 系统功能

| 功能 | 命令 |
|------|------|
| 固件 OTA 更新 | `update` |
| 保存/加载配置 | `save` / `load` |
| 设置 | `settings` |
| LED 控制 | `led` |
| 重启 | `reboot` |
| Headless 模式 | 无屏幕纯命令行 |
| SAE 嗅探 | `sniffsae` (WPA3) |
| 欺骗 AT | `spoofat` |

## 支持硬件

| 硬件 | 说明 |
|------|------|
| **Marauder v4 / v6 / v7 / v8** | 官方硬件版本（商店购买） |
| **BFFB** (Big F***ing Flipper Board) | Flipper Zero 扩展板 |
| **Dev Board Pro** | ESP32 开发板 Pro 版 |
| **ESP32-C5-DevKitC-1** | 最新 ESP32-C5 支持（WiFi 6） |
| **ESP32 Marauder Kit** | DIY 套件 |
| **Flipper Zero** | 作为 Flipper Zero 外设模块 |

### 硬件扩展

- GPS 模块（wardriving 必备）
- NRF24 修复（BFFB 版本）
- 外置天线改装
- 电池电量计
- 3D 打印外壳
- 触摸屏禁用选项

## 安装方式

### 方式一：预编译固件 OTA

下载 [latest release](https://github.com/justcallmekoko/ESP32Marauder/releases/latest)，通过 OTA 或 USB 烧录。

### 方式二：Arduino IDE 编译

```bash
# Arduino IDE 配置
# Board: ESP32 Dev Module / ESP32-C5 DevKitC-1
# 安装依赖：ArduinoJson, Adafruit GFX, Adafruit ST7735
```

### 方式三：源码编译

```bash
git clone https://github.com/justcallmekoko/ESP32Marauder.git
cd ESP32Marauder
# 使用 PlatformIO 或 Arduino CLI
```

## 工作流示例（Wiki 文档）

| 工作流 | 说明 |
|--------|------|
| **Random Beacon Spam** | 随机 SSID 广播 |
| **List Beacon Spam** | 自定义列表 SSID 广播 |
| **AP Clone Spam** | 克隆真实 AP 的 SSID |
| **Deauthentication Attack** | 针对目标 AP 的去认证攻击 |
| **Probe Request Attack** | 主动探测攻击 |
| **Targeted PMKID Sniff** | 定向 PMKID 捕获 |
| **Signal Monitor** | 信号强度监控 |

## 项目技术细节

| 维度 | 说明 |
|------|------|
| **代码覆盖率** | 有 Codecov 集成（develop 分支） |
| **CI/CD** | GitHub Actions: build_push.yml |
| **固件单元测试** | firmware-unit-tests flag |
| **屏幕支持** | TFT ST7735 / OLED |
| **输入方式** | 触摸屏 / 物理按钮 / 串口命令行 |
| **Headless 模式** | 无屏幕纯命令行操作 |
| **存储** | SD 卡 / SPIFFS |
| **固件版本** | 多版本并行（v4-v8 + BFFB + Dev Board Pro） |

## ⚠️ 安全/合规声明

> ESP32 Marauder 是安全研究工具，仅用于：
> - 授权渗透测试
> - 无线安全教学
> - 个人网络安全评估
>
> **未经授权对他人网络/设备执行攻击（deauth/beacon spam/evil portal/karma 等）在中国和大多数国家属于违法行为。** 工具的防御价值（扫描/嗅探/wardriving）大于攻击价值。

## 💡 分析与借鉴

### 对嵌入式安全的启发

| 启发点 | 内容 |
|--------|------|
| **ESP32 无线安全全栈** | 一个 ESP32 芯片实现完整的 WiFi+BT 攻防链——扫描→嗅探→攻击→记录，无需电脑 |
| **Headless 模式** | 无屏幕纯命令行，适合嵌入式自动化部署 |
| **OTA 固件更新** | 内置 OTA 能力，对任何 ESP32 项目都有借鉴价值 |
| **Flipper Zero 集成** | BFFB 模块化扩展设计，硬件插件化 |
| **多芯片适配** | ESP32 / ESP32-C5（WiFi 6）全覆盖，说明固件层抽象做得好 |
| **Wardriving 数据** | GPS + WiFi/BT 数据融合，是无线地理信息学的好案例 |

### 与 Hermes red-teaming skills 的关联

Hermes 有完整的 red-teaming 技能树（300+ 攻防 skill），其中无线安全相关：
- `recon-for-sec`: 侦察方法论
- `401-403-bypass-techniques`: 访问绕过
- 可将 Marauder 的 WiFi 侦察命令映射到 Hermes 的侦察 workflow

## 关联

- → 项目：~/uclaw/project/esp32-marauder/
- → 相关：red-teaming/recon-for-sec（侦察方法论）
- → 相关：embedded/stm32-embedded-dev（嵌入式开发）


## 相关笔记

- [IoT ESP-NOW 安全机制与最佳实践](./explore/2026-08-12-IoT-ESP-NOW-安全机制与最佳实践.md) — 同为 ESP32 无线通信安全，攻防视角互补
- [网络安全 Security Automation](./explore/2026-08-12-网络安全-security-automation.md) — 自动化安全工具链宏观视角
