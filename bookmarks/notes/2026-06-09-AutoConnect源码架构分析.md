# AutoConnect 源码架构分析

> ESP8266/ESP32 WiFi 运行时配置库，Captive Portal 方式免除硬编码 SSID/密码。
> 版本 1.4.2 · MIT License · 作者 Hieromon Ikasamo
> 仓库：https://github.com/Hieromon/AutoConnect

## 一、项目概览

| 指标 | 值 |
|------|-----|
| 核心代码 | 9,889 行（src/） |
| 文件数 | 33 个 .h/.cpp + 5 个 .hpp 模板 |
| 依赖 | ArduinoJson, PageBuilder |
| 架构 | ESP8266 / ESP32 双平台，C++ 模板分层 |

## 二、架构分层

```
┌─────────────────────────────────────┐
│  AutoConnect.h (完整版入口)          │  ← 用户 #include
│  AutoConnectCore.h (精简版入口)      │
├─────────────────────────────────────┤
│  AutoConnectExt / AutoConnectCore   │  ← 模板类主体
│  (AutoConnectCoreImpl.hpp)          │
├─────────────────────────────────────┤
│  AutoConnectAux (自定义页面引擎)     │
│  AutoConnectElement (UI 元素体系)    │
├─────────────────────────────────────┤
│  AutoConnectCredential (凭据存储)    │
│  AutoConnectOTA (固件更新)           │
│  AutoConnectUpdate (远程更新)        │
│  AutoConnectTicker (状态 LED)        │
├─────────────────────────────────────┤
│  AutoConnectConfigBase/Ext (配置)    │
│  AutoConnectDefs.h (编译宏/常量)     │
│  AutoConnectTypes.h (枚举定义)       │
└─────────────────────────────────────┘
```

## 三、核心连接状态机

`begin()` 方法实现了一个 4 阶段连接状态机：

1. **WiFi.begin 直连**：尝试用已保存凭据直接连接
2. **autoReconnect**：加载历史凭据按 RECENT/RSSI 策略重试
3. **Captive Portal**：连接失败后启动 SoftAP + DNS 欺骗，弹出配置页面
4. **whileCaptivePortal 循环**：阻塞等待用户配置或超时退出

关键标志位（`AC_PORTALSTATE_t`）：
- `AC_ESTABLISHED` — 连接成功
- `AC_AUTORECONNECT` — 自动重连生效
- `AC_TIMEOUT` — Portal 超时
- `AC_CAPTIVEPORTAL` — Portal 活跃
- `AC_INPROGRESS` — WiFi.begin 进行中

## 四、Captive Portal 机制

```
WiFi连接失败
    ↓
启用 SoftAP (默认 IP: 192.168.244.1)
    ↓
启动 DNSServer (劫持所有 DNS → SoftAP IP)
    ↓
浏览器任意 URL → 重定向到配置页面
    ↓
用户输入 SSID + 密码 → WiFi.begin(new_credential)
    ↓
连接成功 → 关闭 Portal → 回调 onConnect()
```

核心技巧：
- DNS 劫持：所有 URL 请求都通过 `_captivePortal` 处理
- 超时控制：`portalTimeout` 可配，超时后可选保持/关闭 Portal
- `retainPortal`：超时后仍保持 Portal 状态供后续连接

## 五、凭据存储 (AutoConnectCredential)

- **ESP8266**：EEPROM 扇区存储，`station_config_t` 结构体（SSID + 密码 + BSSID + DHCP/Static + IP 配置）
- **ESP32**：Preferences (NVS) 存储（通过 `AUTOCONNECT_USE_PREFERENCES` 宏切换）
- 支持多条凭据存储，按 RECENT（最近使用）或 RSSI（信号最强）排序
- 可导出/导入到文件系统（SPIFFS/LittleFS/SD）

## 六、UI 元素体系 (AutoConnectElement)

11 种 UI 元素，双层实现（Basis 层 + JSON 层）：

| 元素 | 功能 | JSON 支持 |
|------|------|----------|
| AutoConnectElement | 通用 HTML 容器 | ✅ |
| AutoConnectButton | 按钮 | ✅ |
| AutoConnectCheckbox | 复选框 | ✅ |
| AutoConnectFile | 文件上传 | ✅ |
| AutoConnectInput | 文本输入 | ✅ |
| AutoConnectRadio | 单选按钮组 | ✅ |
| AutoConnectRange | 滑块 | ✅ |
| AutoConnectSelect | 下拉选择 | ✅ |
| AutoConnectStyle | CSS 样式注入 | ✅ |
| AutoConnectSubmit | 提交按钮 | ✅ |
| AutoConnectText | 文本/HTML 显示 | ✅ |

- Basis 层：纯 C++ 对象操作
- JSON 层：可通过 JSON 文件（PROGMEM/SPIFFS/SD）加载页面定义
- `AutoConnectAux` 作为容器管理元素集合，支持 `operator[]` 按名访问

## 七、OTA 更新 (AutoConnectOTA)

- 继承 `AutoConnectUploadHandler`，覆写 `_write()` 使用 `Update` 类写入固件
- 两种更新目标：固件 (`OTA_DEST_FIRM`) / 文件 (`OTA_DEST_FILE`)
- 状态机：IDLE → START → PROGRESS → SUCCESS/FAIL → RIP（重启就绪）
- 通过 `AutoConnectAux` 页面内嵌到菜单

## 八、配置参数 (AutoConnectConfigBase)

30+ 可配参数，关键项：

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `apip` | 192.168.244.1 | SoftAP IP |
| `autoRise` | true | 连接失败自动启动 Portal |
| `autoReconnect` | false | 自动重连历史凭据 |
| `immediateStart` | false | 跳过首次 WiFi.begin 直接启动 Portal |
| `portalTimeout` | 0 (无限) | Portal 超时 |
| `retainPortal` | false | 超时后保持 Portal |
| `autoSave` | AUTO | 自动保存凭据 |
| `principle` | RECENT | 凭据选择策略 |
| `auth` | NONE | HTTP 认证（Basic/Digest） |
| `ticker` | false | LED 闪烁指示连接状态 |

## 九、模板设计模式

项目使用 C++ 模板实现三级功能分层：

```
AutoConnectCore<ConfigBase>     ← 最小集（仅 WiFi 配置）
    ↓ 继承
AutoConnectExt<ConfigExt>       ← 完整集（+ Aux + JSON + OTA）
    ↓ typedef
AutoConnect = AutoConnectExt<AutoConnectConfigExt>
```

- `AutoConnectConfigBase` — 基础配置（30 个参数）
- `AutoConnectConfigExt` — 扩展配置（+ OTA/Update 相关）
- 用户通过 `#include "AutoConnect.h"` 或 `"AutoConnectCore.h"` 选择功能范围

## 十、关键设计模式提炼

1. **Captive Portal 模式**：SoftAP + DNS 劫持 + Web 配置页面，零 APP 依赖
2. **模板策略模式**：通过 C++ 模板参数注入配置类型，编译期决定功能集
3. **双平台适配**：`#ifdef ARDUINO_ARCH_ESP8266 / ESP32` 条件编译
4. **Element 组合模式**：`AutoConnectAux` 容器 + 11 种 Element 可组合，JSON 描述驱动
5. **凭据持久化策略**：EEPROM(ESP8266) / Preferences(ESP32) 双实现，统一接口

## 十一、实用价值评估

- **学习价值 ★★★★**：Captive Portal 完整实现、ESP 双平台适配、C++ 模板分层架构
- **复用价值 ★★★**：可直接用于 ESP 项目 WiFi 配置场景，但依赖 PageBuilder 略重
- **改进空间**：
  - 不支持 WiFiManager 风格的扫描列表展示
  - 配置页面仅英文，i18n 需自行替换字符串常量
  - OTA 仅支持固件级更新，不支持分区/文件系统级


## 相关笔记
