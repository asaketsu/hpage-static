# 🔊 LuxTTS GPU 使用指南

> Jetson Orin Nano · GPU 常驻服务 · RTF 0.15-0.25x (4-6倍实时)
> 创建日期: 2026-07-11

---

## 一、日常使用（零配置）

LuxTTS 已设为 Hermes 默认 TTS 引擎。

| 方式 | 操作 | 说明 |
|------|------|------|
| **强制语音回复** | 会话中发 `/voice tts` | 之后所有回复自动转语音 |
| **语音到语音** | 会话中发 `/voice on` | 发语音给 bot，bot 回复也转语音 |
| **关闭** | 会话中发 `/voice off` | 恢复纯文本 |
| **MeowBot 直调** | `text_to_speech(text="你好")` | 自动生成语音气泡 |

---

## 二、情感预设

| 情感 | 适用场景 | 语速 | 特点 |
|------|----------|------|------|
| `neutral` | **默认** 日常对话、技术播报 | 中 | 清晰自然 |
| `happy` | 好消息、庆祝、通知 | 偏快 | 活泼有活力 |
| `calm` | 晚安、冥想、安慰 | 偏慢 | 温柔舒缓 |
| `news` | 新闻、正式公告 | 中 | 字正腔圆 |
| `narration` | 讲故事、有声书 | 慢 | 娓娓道来 |
| `energetic` | 运动、快讯 | 快 | 高能量 |

wrapper 会自动检测情感（`!≥2` → happy，关键词 → calm），手动指定更精确。

---

## 三、HTTP API 直接调用

```bash
# 基础用法
curl -X POST http://127.0.0.1:8765/tts \
  -H 'Content-Type: application/json' \
  -d '{"text":"你好世界","emotion":"happy"}' \
  -o output.wav

# 自定义参数覆盖预设
curl -X POST http://127.0.0.1:8765/tts \
  -H 'Content-Type: application/json' \
  -d '{"text":"慢慢说","emotion":"calm","speed":0.6,"num_steps":6}' \
  -o output.wav

# 健康检查
curl http://127.0.0.1:8765/health
# → {"status":"ready","gpu":true,"gpu_mem_mb":1398}

# 查看情感列表
curl http://127.0.0.1:8765/emotions
```

**返回 Header 性能指标：**

| Header | 含义 |
|--------|------|
| `X-RTF` | 实时倍率（<1 = 快于实时） |
| `X-Duration` | 音频时长（秒） |
| `X-Gen-Time` | 生成耗时（秒） |
| `X-GPU-Mem-MB` | GPU 显存峰值 |

---

## 四、参数调优

| 参数 | 范围 | 默认 | 效果 |
|------|------|------|------|
| `speed` | 0.5-1.2 | 0.85 | <0.8 慢速，>1.0 加速 |
| `num_steps` | 3-8 | 4 | 越高音质越好但越慢（4 是效率甜点） |
| `t_shift` | 0.5-1.0 | 0.9 | 类似温度，越高变化越多 |
| `return_smooth` | bool | false | true 更平滑但细节略损 |
| `rms` | 0.005-0.02 | 0.01 | 音量控制，越高越响 |

---

## 五、最佳实践

**文本长度：**
- ✅ 最佳：单句 < 60 字（RTF 0.15-0.25x）
- ✅ 可用：60-120 字（自动分段，RTF 0.15-0.3x）
- ⚠️ 避免：> 200 字（多段拼接，延迟增加但稳定）

**中英文混输：**
- 中文自动转拼音，英文保留原文
- ✅ `"今天学习 Python 编程"` → 自然混输
- ✅ `"使用 VS Code 打开文件"` → 完美

**中文必须降速：** 默认 `speed=0.85`，否则听起来像加速。

---

## 六、性能基准

| 场景 | 音频时长 | 生成耗时 | RTF | 实时倍率 |
|------|----------|----------|-----|----------|
| 英文短句 | 8.8s | 1.4s | 0.16x | **6.3x** |
| 中文短句 | 16s | 2.7s | 0.17x | **5.9x** |
| 中英混输 | 15s | 2.7s | 0.18x | **5.6x** |
| 长文本(64字) | 72s | 11s | 0.15x | **6.5x** |

GPU 常驻 1398MB / 7620MB（18%），不影响其他 GPU 任务。

---

## 七、服务管理

```bash
# 查看状态
sudo systemctl status luxtts-daemon

# 重启（更新代码后）
sudo systemctl restart luxtts-daemon

# 查看日志
tail -50 /tmp/luxtts_daemon.log

# 健康检查
curl http://127.0.0.1:8765/health
```

服务配置：开机自启 + 崩溃 10s 自动重启 + 4GB 内存上限。

---

## 八、常见问题

| 问题 | 解决方案 |
|------|----------|
| 语音听起来像加速 | 中文必须 `speed<1.0`（默认 0.85 已设置） |
| 长文本卡顿 | daemon 自动分段，每段间 0.15s 静音 |
| GPU OOM | daemon 预留 800MB 池，`Restart=always` 自动恢复 |
| 想换音色 | 替换 `ref_audio_zh.wav`，重启 daemon |
| 不想用 LuxTTS | `hermes config set tts.provider edge` 切回 Edge TTS |
| 服务没启动 | `sudo systemctl start luxtts-daemon` |

---

## 九、技术架构

```
Hermes (tts.provider=luxtts)
  └─ /home/jc/bin/luxtts_hermes.py (wrapper, 自动情感检测)
       └─ http://127.0.0.1:8765 (daemon)
            └─ systemd: luxtts-daemon.service (开机自启 + 崩溃自恢复)
                 └─ GPU 1398MB 常驻 (800MB 预热 + 598MB 模型)
```

**关键文件：**
- Daemon: `/home/jc/uclaw/project/luxtts/luxtts_daemon.py`
- Hermes wrapper: `/home/jc/bin/luxtts_hermes.py`
- Systemd: `/etc/systemd/system/luxtts-daemon.service`
- 参考音频: `/home/jc/uclaw/project/luxtts/ref_audio_zh.wav`
- 模型权重: `/home/jc/uclaw/project/luxtts/model/` (491MB)
