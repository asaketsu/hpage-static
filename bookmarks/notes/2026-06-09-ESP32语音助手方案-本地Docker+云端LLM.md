# ESP32 AI 语音助手 — 本地 Docker + 云端 LLM 方案

> 项目类型：新项目方案 | 日期：2026-06-09
> 基于：xiaozhi-esp32-server 开源项目

---

## 🎯 项目目标

在 Jetson Orin 上通过 Docker 部署 xiaozhi-esp32-server，实现 ESP32 语音终端 ↔ 本地服务端 ↔ 云端 LLM 的 AI 语音助手。ASR/TTS 本地运行（零延迟、零成本），LLM 调用云端 API（高质量、低门槛）。

---

## 🏗️ 系统架构

```
┌─────────────────────────────────┐
│   ESP32 语音终端（每个房间一个）   │
│   麦克风 + 扬声器 + WiFi + OTA   │
└──────────┬──────────┬───────────┘
           │ WebSocket:8000
           │ HTTP:8003
           ▼
┌─────────────────────────────────┐
│  Jetson Orin: Docker 服务端      │
│                                 │
│  ┌────────────┐  本地离线运行    │
│  │ ASR        │  SenseVoiceSmall│
│  │ (CPU/CUDA) │  ~900MB 模型    │
│  └────────────┘                 │
│  ┌────────────┐  本地免费运行    │
│  │ TTS        │  EdgeTTS        │
│  │ (免费)     │  无需 Key       │
│  └────────────┘                 │
│  ┌────────────┐  云端 API       │
│  │ LLM        │  DeepSeek / Qwen│
│  │ (云端API)  │  按量付费       │
│  └────────────┘                 │
│                                 │
│  可选：MCP Vision Explain       │
└─────────────────────────────────┘
```

### 数据流

```
用户语音 → ESP32 麦克风采集
  → WebSocket 流式传输到服务端
  → ASR(SenseVoice) 本地识别为文字
  → LLM(DeepSeek API) 生成回复
  → TTS(EdgeTTS) 本地合成语音
  → WebSocket 流式回传 ESP32
  → 扬声器播放
```

---

## 📦 硬件清单

- **服务端**: Jetson Orin Nano Super（已有）
  - 8GB RAM, 67 TOPS, Docker 支持
  - ASR 用 CPU 即可跑，CUDA 可选加速
- **语音终端**: ESP32-S3 开发板（需采购）
  - 推荐：ESP32-S3-BOX-3 或自制板
  - 需：I2S 麦克风 + I2S 功放/扬声器 + WiFi
  - 预估成本：￥30-80/个（取决于是否用开发套件）
- **网络**: 局域网 WiFi（ESP32 和 Jetson 同网段）

---

## 🔧 部署步骤

### Step 1: 准备项目目录

```bash
mkdir -p ~/esp32-ai-assistant/{data,models/SenseVoiceSmall}
cd ~/esp32-ai-assistant/
```

### Step 2: 下载配置文件

```bash
# docker-compose.yml
wget https://raw.githubusercontent.com/xinnan-tech/xiaozhi-esp32-server/main/main/xiaozhi-server/docker-compose.yml

# 配置模板
wget https://raw.githubusercontent.com/xinnan-tech/xiaozhi-esp32-server/main/main/xiaozhi-server/config.yaml -O data/.config.yaml
```

### Step 3: 下载 ASR 模型（离线语音识别）

```bash
# SenseVoiceSmall ~900MB，首次下载需耐心
wget https://huggingface.co/FunAudioLLM/SenseVoiceSmall/resolve/main/model.pt \
  -O models/SenseVoiceSmall/model.pt
```

### Step 4: 配置云端 LLM

编辑 `data/.config.yaml`，核心配置项：

```yaml
# 选方案 A 或 B，二选一

# 方案 A: DeepSeek（推荐，性价比高）
llm:
  provider: deepseek
  api_key: "sk-xxx"           # DeepSeek API Key
  model: "deepseek-chat"      # 或 deepseek-reasoner

# 方案 B: 通义千问（阿里百炼）
llm:
  provider: qwen
  api_key: "sk-xxx"           # 阿里百炼 API Key
  model: "qwen-turbo"         # 或 qwen-plus / qwen-max

# TTS: 默认 EdgeTTS（免费，无需配置）
tts:
  provider: edge-tts

# 服务端口
server:
  ws_port: 8000               # WebSocket（ESP32 连接）
  http_port: 8003             # HTTP（管理/OTA）

# Token 认证（必须与 ESP32 固件一致）
auth:
  token: "your-secret-token"
```

### Step 5: 启动服务

```bash
docker compose up -d

# 查看日志确认启动
docker logs -f xiaozhi-esp32-server

# 验证端口
ss -tlnp | grep -E '8000|8003'
```

### Step 6: ESP32 固件烧录

1. 克隆 ESP32 客户端固件
2. 配置 WiFi SSID/密码 + 服务端地址（Jetson IP:8000）+ Token
3. 烧录到 ESP32-S3
4. 上电后自动连接服务端

---

## 💰 成本分析

| 项目 | 费用 | 说明 |
|------|------|------|
| **ASR** | ￥0 | SenseVoiceSmall 本地离线 |
| **TTS** | ￥0 | EdgeTTS 免费 |
| **LLM** | ~￥0.01-0.05/次对话 | DeepSeek 极低价，日常使用 <￥5/月 |
| **ESP32 终端** | ￥30-80/个 | 一次性硬件成本 |
| **Jetson 服务端** | ￥0 | 已有设备 |

**结论**: 月均运营成本 <￥10，硬件投入 ￥30-80/房间。

---

## ⚡ 性能预期

| 环节 | 延迟 | 说明 |
|------|------|------|
| ASR 识别 | <500ms | 本地 CPU 推理，Jetson 无压力 |
| LLM 生成 | 1-3s | 取决于网络和 API 响应 |
| TTS 合成 | <300ms | EdgeTTS 本地 |
| **端到端** | **2-4s** | 从说话到开始听到回复 |

---

## 🔮 扩展路线

### Phase 1（当前方案）
- 单 ESP32 + Jetson Docker + 云端 LLM
- 验证基础语音对话功能

### Phase 2: 多房间
- 2-3 个 ESP32 终端，Jetson 统一服务
- 多 WebSocket 连接管理
- 不同房间可配置不同人格/指令

### Phase 3: 本地 LLM（可选）
- Jetson Orin 跑 Ollama + Qwen2.5-7B
- 完全离线，无网络依赖
- 适合隐私敏感场景

### Phase 4: 多模态
- MCP Vision Explain 接入摄像头
- 语音 + 图像联合理解
- "这是什么？" → 拍照 + 语音回答

---

## ⚠️ 注意事项

1. **Token 一致性**: 服务端和 ESP32 固件的 Token 必须一致，否则连接失败
2. **网络要求**: ESP32 和 Jetson 需在同一局域网；LLM API 需要外网
3. **ASR 模型大小**: SenseVoiceSmall ~900MB，首次部署需预留下载时间
4. **配置生效**: 修改 config.yaml 后需 `docker compose down && docker compose up -d`
5. **ESP32 供电**: 建议独立 5V/2A 供电，USB 供电可能不稳定
6. **防火墙**: 确保 8000/8003 端口对局域网开放

---

## 🔗 参考资源

- GitHub: https://github.com/xinnan-tech/xiaozhi-esp32-server
- ASR 模型: https://huggingface.co/FunAudioLLM/SenseVoiceSmall
- DeepSeek API: https://platform.deepseek.com
- 阿里百炼: https://bailian.console.aliyun.com

---

*方案生成：2026-06-09 | MeowBot*


## 相关笔记
- [[2026-06-09-xiaozhi-esp32-server本地搭建分析]]
- [[2026-05-27-外包加本地AI-vs-前沿实验室-LLM经济学拐点]]
