# OpenClaw + 摄像头 + 本地视觉模型 = 智能家居

> **来源**：微信公众号（澳哥） | mp.weixin.qq.com/s/1njBYo-YDu1U-g3tCEh1tg
> **日期**：2026-04-07
> **标签**：OpenClaw、智能家居、摄像头、RTSP、本地视觉模型
> **评分**：⭐⭐⭐⭐

---

## 核心观点

通过小米开源 Miloco 服务将摄像头转为 RTSP 流，再用 OpenClaw 调用本地视觉大模型（如 Qwen3-VL）解析画面，实现定时人体检测 + 智能开关灯，全程隐私不上云。

## 关键要点

| # | 要点 | 说明 |
|---|------|------|
| 1 | Miloco 转流 | 小米开源项目，将米家摄像头视频流转为 RTSP 协议，Docker 部署 |
| 2 | RTSP 地址格式 | `rtsp://<server_ip>:<port>/<camera_did>`，在 server_config.yaml 中配置 |
| 3 | OpenClaw 直接读取 RTSP | 将 RTSP 地址发给 OpenClaw，Agent 自动建立连接获取视频流/截图 |
| 4 | 本地视觉模型解析 | Qwen2.5-VL-7B / Qwen3-VL-4B/8B/30B，Ollama(Linux) 或 LM Studio(Mac) 部署 |
| 5 | 隐私不上云 | 图片仅在本地模型解析，不上传云端 |
| 6 | Cron 自动化 | 定时 cron 每 2 分钟调用模型检测画面，无人关灯、有人开灯 |

## 实现架构

```
小米摄像头 → Miloco(Docker) → RTSP流 → OpenClaw Agent → 本地视觉模型(Qwen-VL) → 智能判断 → HA开关灯
```

## 关键配置

- **Miloco RTSP**：`server_config.yaml` 中 `rtsp_server.enabled: true`，端口默认 8554
- **摄像头ID (DID)**：通过 Miloco 获取，用于 RTSP URL 路径
- **视频质量**：默认 low，可按 DID 单独配置 high
- **模型选择**：NVIDIA 显卡用 Ollama，Mac 用 LM Studio

## 应用场景

- 无人自动关灯（10分钟无活动）
- 傍晚/夜间有人自动开灯
- 可扩展：入侵检测、宠物监控、老人看护

---

## 💡 对我们的价值分析

### ✅ 已在做的
- OpenClaw cron 自动化已成熟（26+ cron 任务运行中）
- Jetson Orin Nano 有 GPU，本地推理是我们的方向

### ⚠️ 可改进的
- **Jetson 上的视觉模型**：Qwen-VL 系列 aarch64 支持需要验证（内存限制 7.4GB 共享）
- **摄像头集成**：目前无任何摄像头/视频处理能力，这是一个新方向

### 🔥 重点行动

| 行动 | 优先级 | 说明 |
|------|--------|------|
| 评估 Jetson 视觉模型可行性 | P3 | 7.4GB 共享内存，小模型如 Qwen3-VL-4B 或 Gemma 可能可行 |
| Miloco 部署调研 | P3 | 如果有小米摄像头可尝试，Docker 部署 |
| RTSP → Agent 桥接 | P3 | OpenClaw 如何消费 RTSP 流，需要验证 |

### 📌 备注
这篇文章的核心价值是展示了 OpenClaw 作为**智能家居中枢**的实战案例，将视觉感知、定时任务、设备控制串成闭环。对我们来说，Jetson 天然适合做边缘 AI 推理，但需要先解决内存限制问题。
→ 相关：2026-04-07-OpenClaw自主性与Harness循环机制.md
→ 相关：2026-04-06-AI-Scientist-v2.md
→ 相关：2026-04-05-空间智能Agent行动能力.md
→ Related: 2026-04-07-tactile-multimodal-fusion-embodied-intelligence-survey.md


## 相关笔记
- [[2026-04-04-OpenClaw-4.2-stable-backend]] (关键词: openclaw)
- [[2026-04-03-OpenClaw最佳实践15条精华版]] (关键词: openclaw)
- [[2026-04-10-OpenClaw-4-things-persistent-tasks]] (关键词: openclaw)
- [[2026-04-04-OpenClaw 为什么越用越好用？本质就是一堆 md 文件]] (关键词: openclaw)
- [[2026-04-05-Clawith-team-OpenClaw]] (关键词: openclaw)
