# xiaozhi-esp32-server 本地后台搭建分析

> 来源：小许的嵌入式AI笔记 | 2026-06-01
> 链接：https://mp.weixin.qq.com/s/et7rStck5FNzNQ5hFlyoDw
> GitHub：https://github.com/xinnan-tech/xiaozhi-esp32-server

---

## 📋 项目概述

**xiaozhi-esp32-server** 是一个开源的 ESP32 AI 伴侣服务端，提供完整的语音对话后端能力。通过 Docker 单服务部署，可快速搭建本地化 AI 语音助手。

| 维度 | 内容 |
|------|------|
| **项目名** | xiaozhi-esp32-server |
| **作者** | xinnan-tech |
| **定位** | ESP32 语音 AI 助手后端服务 |
| **部署方式** | Docker Compose 单服务 |
| **协议** | 开源 |

---

## 🏗️ 技术架构

```
┌─────────────────────────────────────────┐
│           ESP32 硬件端                    │
│  (麦克风 + 扬声器 + WiFi + OTA)          │
└──────────┬──────────┬───────────────────┘
           │ WebSocket│ HTTP
           ▼          ▼
┌──────────────────────────────────────────┐
│       xiaozhi-esp32-server (Docker)       │
│                                          │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ │
│  │  ASR     │ │  LLM     │ │  TTS     │ │
│  │SenseVoice│ │ Qwen/DS  │ │ EdgeTTS  │ │
│  │ (离线)   │ │ (API)    │ │ (免费)   │ │
│  └──────────┘ └──────────┘ └──────────┘ │
│                                          │
│  端口: 8003(HTTP) / 8000(WebSocket)      │
│  视觉: /mcp/vision/explain               │
└──────────────────────────────────────────┘
```

### 核心组件

| 模块 | 技术 | 说明 |
|------|------|------|
| **ASR（语音识别）** | SenseVoiceSmall (离线) | FunAudioLLM 开源模型，本地运行 |
| **LLM（大语言模型）** | Qwen / DeepSeek | API 调用，支持阿里百炼和 DeepSeek |
| **TTS（语音合成）** | EdgeTTS（默认免费） | 无需 API Key |
| **通信协议** | WebSocket + HTTP | 端口 8000/8003 |
| **视觉理解** | MCP Vision Explain | 图片理解能力 |
| **部署** | Docker Compose | 单容器，含模型挂载 |

---

## 🚀 部署流程（4 步）

### Step 1: 项目目录
```bash
mkdir -p ~/esp32-server-docker/{data,models/SenseVoiceSmall}
cd ~/esp32-server-docker/
wget https://raw.githubusercontent.com/xinnan-tech/xiaozhi-esp32-server/main/main/xiaozhi-server/docker-compose.yml
wget https://raw.githubusercontent.com/xinnan-tech/xiaozhi-esp32-server/main/main/xiaozhi-server/config.yaml -O data/.config.yaml
```

### Step 2: 语音识别模型
```bash
wget https://huggingface.co/FunAudioLLM/SenseVoiceSmall/resolve/main/model.pt \
  -O models/SenseVoiceSmall/model.pt
```

### Step 3: 配置修改
- **LLM**: 阿里百炼(Qwen) 或 DeepSeek API Key
- **TTS**: 默认 EdgeTTS（免费）
- **服务地址**: WebSocket / HTTP 端口
- **Token 认证**: 自定义访问密码（烧录固件时需一致）

### Step 4: 启动
```bash
docker compose up -d
# 查看日志
docker logs -f xiaozhi-esp32-server
```

---

## 🎯 项目价值分析

### 与我们现有系统的关系

| 维度 | xiaozhi-esp32-server | 我们可借鉴 |
|------|---------------------|-----------|
| **ASR** | SenseVoiceSmall 离线 | 可用于 Jetson 本地语音识别 |
| **TTS** | EdgeTTS 免费 | 已有 EdgeTTS，一致 |
| **协议** | WebSocket 语音流 | 适合 ESP32 ↔ Jetson 架构 |
| **视觉** | MCP Vision Explain | 可扩展为多模态交互 |
| **部署** | Docker 单服务 | 适合快速验证 |

### 可行性评估

| 评估维度 | 评分 | 说明 |
|----------|------|------|
| **部署难度** | ⭐⭐ (简单) | Docker 4 步搞定 |
| **硬件成本** | ⭐⭐⭐ (低) | ESP32 + 无需 GPU（ASR 用 CPU） |
| **功能完整度** | ⭐⭐⭐ (中) | ASR+LLM+TTS 全链路，但缺主动唤醒 |
| **扩展性** | ⭐⭐⭐⭐ (好) | 模块化设计，可替换各组件 |
| **Jetson 适配** | ⭐⭐⭐⭐ (好) | Docker 兼容，CUDA 可加速 |

### 潜在新项目方向

1. **Jetson + ESP32 分布式 AI 助手**
   - Jetson Orin 运行服务端（含本地 LLM 推理）
   - ESP32 作为远程语音终端
   - 替代云端 API，全本地化

2. **多房间语音助手网络**
   - 每个 ESP32 独立房间节点
   - Jetson 中央服务器处理所有 LLM/TTS
   - WebSocket 多连接管理

3. **嵌入式 AI 教学项目**
   - 从 ASR→LLM→TTS 全链路理解
   - 模块替换实验（换 ASR/TTS/LLM）
   - 适合快速原型验证

---

## ⚠️ 注意事项

- SenseVoiceSmall 模型较大（~900MB），首次下载需时间
- LLM 依赖外部 API（阿里百炼/DeepSeek），需配额
- Docker 容器修改配置后需 `docker compose down && up -d` 重建
- Token 必须与 ESP32 固件一致，否则无法连接
- 视觉理解需要额外配置（文中未详述）

---

## 🔗 相关资源

- GitHub: https://github.com/xinnan-tech/xiaozhi-esp32-server
- SenseVoice: https://huggingface.co/FunAudioLLM/SenseVoiceSmall
- 测试页面: test/test_page.html（拨号测试）

---

*分析时间：2026-06-09 | MeowBot*


## 相关笔记
- [[2026-06-09-ESP32语音助手方案-本地Docker+云端LLM]]
