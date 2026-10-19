# Kai-Sound-TTS 源码分析：ESP32 TTS 播报全链路方案

> 来源：[Kaiii-create/kai-sound-tts](https://github.com/Kaiii-create/kai-sound-tts) · [原文链接](https://mp.weixin.qq.com/s/X1Ud811saY39poEefazSjQ)
> 整理日期：2026-06-09

---

## 项目概述

一套完整的 **网页 + PHP + Python + MQTT + ESP32** TTS 播报方案（v1.0.0-mqtt），核心链路：

```
网页输入文本 → PHP 断句分段 + 预生成 → Python 火山引擎 TTS → MQTT 下发 → ESP32 HTTP 拉流 → I2S 播放
```

---

## 架构分层

| 层 | 组件 | 职责 |
|:---|:-----|:-----|
| 前端 | `index.html` | 深色玻璃拟态控制台，文本输入/音量/状态 |
| 调度层 | `tts_request_handler.php` | 断句分段 + 预生成 TTS + 顺序下发 MQTT |
| TTS 层 | `tts_bridge_server.py` | 火山引擎流式 TTS → MP3，HTTP 流 URL |
| 控制层 | Mosquitto MQTT | 控制命令（tts/stop/volume），不传音频 |
| 设备层 | `sound.ino` (ESP32) | HTTP 拉流 + 32KB 缓冲 + I2S 解码播放 |

---

## 核心设计决策

### 1. MQTT 控制链 vs HTTP 音频链分离

```
MQTT → 控制命令（tts + url / stop / volume）
HTTP → 实际音频流（ESP32 主动拉取）
```

这是整条链路最关键的设计。MQTT 只传指令，不传音频数据，避免 ESP32 自行处理缓冲、连续字节流等复杂逻辑。

### 2. PHP 智能断句分段

三级断句策略：

| 优先级 | 断句依据 | 标点 |
|:-------|:---------|:-----|
| 1 | 句末标点 | `。！？；换行` |
| 2 | 句内标点 | `，、：` |
| 3 | 长度兜底 | 硬切 `hardMaxChars=100` |

参数：`targetChars=70`（目标段长），`hardMaxChars=100`（硬上限）

### 3. 预生成策略

```
旧方案：播完一段 → 临时生成下一段 → 下发 → 播放（段间停顿明显）
新方案：PHP 一次性预生成所有段的 TTS URL → 按序下发（段间几乎无等待）
```

### 4. ESP32 本地缓冲

```cpp
AudioFileSourceBuffer(audioFile, 32 * 1024)  // 32KB
```

HTTP 流先缓冲到本地再喂解码器，WiFi 短暂抖动不中断播放。

---

## 关键踩坑记录

### 坑 1：长文本单条流必断

**原因**：文本越长 → 播放越久 → WiFi 抖动概率越高 → HTTP 流断。

**解法**：分段顺序播放，每段独立 HTTP 流。

### 坑 2：MQTT/HTTP 链路混淆

MQTT 是控制链，HTTP 是音频链。调试时必须分开看，否则容易误判问题出在哪层。

### 坑 3：插播不可靠

ESP32 在 HTTP 拉流播放时，MQTT 接收不稳定，强插播命令可能到不了设备。当前版本放弃抢占式插播，专注顺序播报。

### 坑 4：127.0.0.1 / HTTPS / M4A

- `127.0.0.1` 对 ESP32 无意义，TTS URL 必须用服务器公网 IP
- ESP32 不能直接播 HTTPS 地址
- M4A 不能当 MP3 解码

---

## 源码结构分析

### ESP32 固件 (`sound.ino`)

```
WiFi 连接 + 事件回调（断连检测）
  ↓
MQTT 订阅 device/{DEVICE_ID}/command
  ↓
命令处理：
  tts {url} → 启动 HTTP 拉流 + 32KB 缓冲 + MP3 解码 + I2S 输出
  stop      → 停止当前播放
  volume N  → 调整音量 (0-100)
  ↓
状态上报 → device/{DEVICE_ID}/status
心跳上报 → device/{DEVICE_ID}/heartbeat (10s)
```

关键常量：
- `AUDIO_BUFFER_BYTES = 32KB`
- `MQTT_RECONNECT_INTERVAL = 5000ms`
- `WIFI_RECOVER_TIMEOUT = 4000ms`
- I2S 引脚：DOUT=25, BCLK=27, LRC=26

### Python TTS 桥 (`tts_bridge_server.py`)

```
ThreadingHTTPServer (0.0.0.0:9100)
  ├── POST /api/tts     → 调用火山引擎 TTS → 返回 stream_url
  ├── GET  /api/tts/{id} → 查询 TTS 任务状态
  └── GET  /audio/{id}   → 音频流代理（ESP32 拉取）
```

火山引擎配置：
- API：`openspeech.bytedance.com/api/v3/tts/unidirectional`
- 音色：`zh_female_vv_uranus_bigtts`
- 格式：MP3 / 24000Hz
- TTL：600s

### PHP 调度层

```
public/index.html           → 前端控制台
public/api/command.php       → 通用 MQTT 命令下发
public/api/tts.php           → TTS 请求入口（断句+预生成+顺序下发）
public/api/tts-status.php    → TTS 状态查询代理
tts_request_handler.php      → 核心编排逻辑
config.php                   → MQTT/Python/TLS 配置
```

---

## 硬件 BOM

| 器件 | 说明 |
|:-----|:-----|
| ESP32 开发板 | WiFi + 蓝牙，I2S 输出 |
| MAX98357A | I2S 功放模块，3W D类 |
| 小喇叭 | 4Ω/3W 即可 |
| 杜邦线 | 3 根（DOUT/BCLK/LRC） |

---

## 优化改进方向

| 优先级 | 改进 | 思路 |
|:-------|:-----|:-----|
| P0 | 消除段间停顿 | 双缓冲交替播放，前段播完时后段已缓冲 |
| P0 | TTS 引擎可替换 | 抽象 TTS Provider 接口，支持 Edge-TTS/本地 Piper 等 |
| P1 | UDP 传输实验 | 替代 HTTP 拉流，降低延迟和断流概率 |
| P1 | 配置统一管理 | 四处占位配置合并为 `.env` 文件 |
| P2 | 强插播支持 | 双缓冲 + 命令队列 + 播放中断标记 |
| P2 | 多设备管理 | device_id 注册 + 分组播报 |

---

## 项目价值判断

**做得好的**：
- 全链路从网页到声音跑通，真实可用
- 踩坑记录极其诚实（失败的尝试比成功的方案更有价值）
- MQTT 控制链 / HTTP 音频链分离，职责清晰
- PHP 断句 + 预生成策略实用

**局限**：
- 四语言栈（JS/PHP/Python/C++）对部署和维护成本高
- 强绑定火山引擎 TTS
- 段间停顿仍可感知
- 无 HTTPS/WSS 支持

---

*项目路径：`/home/jc/uclaw/project/kai-sound-tts/`*


## 相关笔记
