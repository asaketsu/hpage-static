# Rachel 数字人口播实战攻略 — MiniMax 声音克隆 + HeyGen 驱动 + Codex Skill 全流程

> **来源 1**：[@Zesee (Rachel🥥) 的 X Article](https://x.com/Zesee/status/2077723280534851786) — 970.9K 阅读
> **来源 2**：[github.com/Jingyi-Wu-Richael/rachel-digital-human-production](https://github.com/Jingyi-Wu-Richael/rachel-digital-human-production) — 877 Stars, MIT
> **发布日期**：2026-07-16
> **标签**：数字人、口播视频、MiniMax、HeyGen、Codex Skill、声音克隆

---

## 一句话定义

> **把数字人口播视频的全流程做成 Codex Skill**——MiniMax 海外版负责声音克隆和 TTS，HeyGen 负责人像驱动口型表情，Codex 负责检查素材、调用流程、记录状态、控制风险。核心设计：**声音和画面拆开**，先 15 秒样片确认再生成完整版。

---

## 完整原文核心内容

### 一、整条链路怎么分工

| 组件 | 职责 |
|------|------|
| **MiniMax** | 声音克隆和 TTS |
| **HeyGen** | 人像驱动、口型、表情和动作 |
| **Codex** | 检查素材、调用流程、记录状态、控制风险 |

**完整链路**：
```
素材检查 → MiniMax 生成配音 → HeyGen 15秒样片 → 人工确认 → HeyGen 完整版 → 下载验片 → 状态归档
```

> ⚠️ **最容易犯的错**：声音已经由 MiniMax 克隆完成，却又让 HeyGen 重新配音。如果目标是保留 MiniMax 的克隆音色，应该把 MiniMax 生成的音频上传到 HeyGen，用这个音频驱动画面。**不要切回 HeyGen 的 `script + voice_id` 方案**。

### 二、HeyGen 和 MiniMax 模式选择

**HeyGen**：

| 模式 | 适合场景 | 成本 |
|------|---------|------|
| **Image-to-Video** | 单条测试（轻量） | ~$2/2min 视频 |
| **Photo Avatar** | 固定账号长期生产 | 需训练 |

> 建议：单条测试先 Image-to-Video，固定账号长期生产再做 Photo Avatar。没验证前不要急着训练 Avatar。

**MiniMax**：

| TTS 模型 | 适合场景 |
|---------|---------|
| `speech-2.8-hd` | 追求质量 |
| `speech-2.8-turbo` | 追求速度和批量预览 |

### 三、素材准备

**声音样本**（MiniMax 官方要求）：
- 格式：MP3、M4A 或 WAV
- 时长：至少 10 秒，最多 5 分钟
- 文件大小：不超过 20 MB
- 可选提示音频：少于 8 秒，且要提供完全对应的文字
- **实操建议**：录 30~90 秒，单人、无背景音乐、无明显混响和电流声，音量稳定

**人像要求**：
- 正脸看镜头，五官无遮挡
- 露出头、肩和上半身，人物占画面约 50%~70%
- 嘴部清晰，不要被头发/手/滤镜遮挡
- 竖屏优先 9:16
- HeyGen Assets API 支持 PNG/JPEG，单文件上限 32 MB

> 嘴部越清晰，口型越稳定；声音越干净，克隆越像本人。

### 四、Codex Skill 目录结构

```
project/
├── inputs/
│   ├── portrait.jpg         # 正面人像
│   ├── voice-source.mp3     # 真人声音样本
│   └── script.md            # 口播文案
├── work/
│   ├── voiceover-full.mp3   # MiniMax 生成的完整配音
│   ├── preview-15s.mp3      # 15秒预览音频
│   └── job-state.json       # 任务状态追踪
└── outputs/
    ├── preview-15s.mp4       # 15秒样片
    └── final-1080p.mp4      # 完整1080p视频
```

### 五、Codex Skill 固定了什么

| 固定项 | 说明 |
|--------|------|
| ✅ 固定目录结构 | inputs/work/outputs 三层 |
| ✅ 先检查素材 | preflight 脚本验证格式/大小/时长 |
| ✅ MiniMax 负责声音，HeyGen 负责画面 | 声音和画面拆开 |
| ✅ 永远先生成 15 秒样片 | 强制步骤，不跳过 |
| ✅ 样片确认后才生成完整版 | `approved_by_user: false` 阻断 |
| ✅ 记录 voice_id/asset_id/video_id | job-state.json |
| ✅ 失败不盲目重试 | 避免重复扣费 |
| ✅ 最终 MP4 必须完整检查 | decode-check |
| ✅ 不泄露密钥/授权头/临时链接 | 安全红线 |

### 六、job-state.json 状态追踪

```json
{
  "project": "digital-human-demo",
  "minimax": {
    "source_file_id": "redacted",
    "voice_id": "brand_person_yyyymmdd",
    "tts_model": "speech-2.8-hd",
    "full_audio": "work/voiceover-full.mp3",
    "preview_audio": "work/preview-15s.mp3"
  },
  "heygen": {
    "image_asset_id": "redacted",
    "preview_audio_asset_id": "redacted",
    "preview_video_id": "redacted",
    "full_audio_asset_id": "redacted",
    "full_video_id": "redacted"
  },
  "status": {
    "preview": "not_started",
    "approved_by_user": false,
    "final": "not_started"
  },
  "outputs": {
    "preview_video": "outputs/preview-15s.mp4",
    "final_video": null
  }
}
```

### 七、preflight 脚本（Python，零外部依赖）

`scripts/preflight_assets.py` 在调用付费 API 之前检查：
- 脚本文件：`.md` 或 `.txt`
- 人像：PNG/JPEG，≤ 32 MB
- 声音：MP3/M4A/WAV，≤ 20 MB，时长 10~300 秒（用 ffprobe 检测）
- 输出 JSON 报告（ok/issues/files/voice_duration_seconds）

### 八、安全设计

| 安全边界 | 实现 |
|---------|------|
| **授权确认** | 使用前确认声音/人像/文案/最终用途均已获授权 |
| **不提供法律建议** | 合规/披露/肖像权问题建议用户自查 |
| **显式调用** | `allow_implicit_invocation: false`，防止意外触发付费流程 |
| **密钥隔离** | 只从环境变量读取，不写入 job-state.json |
| **公开分享检查清单** | 不包含 .env/密钥/真实声音样本/客户视频 |

---

## Codex Skill 的工程细节

### SKILL.md frontmatter

```yaml
---
name: rachel-digital-human-production
description: Public-safe MiniMax overseas voice clone and HeyGen API workflow
  for creating digital-human talking-head videos.
---
```

### Required Workflow（7 步）

```
1. Ingest → 收集脚本/人像/声音样本
2. Validate Assets → 检查格式/大小/时长
3. Voice Clone → MiniMax /v1/voice_clone
4. TTS → MiniMax /v1/t2a_v2 生成配音
5. Preview → HeyGen Image-to-Video（15秒，低分辨率）
6. Approval Gate → 等待用户确认
7. Full Video → HeyGen Image-to-Video（1080p）
```

### API 端点参考

| 服务 | 端点 |
|------|------|
| MiniMax 文件上传 | `/v1/files/upload` |
| MiniMax 声音克隆 | `/v1/voice_clone` |
| MiniMax TTS | `/v1/t2a_v2` |
| HeyGen 素材上传 | Assets API |
| HeyGen 图生视频 | Image-to-Video API |

---

## 结合最新研究与技术变化

### 1. 与 shuohao-skills 的关联

两者都是 Codex Skill，但方向不同——shuohao-skills 做小说角色拆解（创意分析），rachel 做数字人口播制作（内容生产流水线）。共同点：**零依赖 Python 脚本 + 显式调用 + 强制校验步骤**。

### 2. 与 AI 短剧分账笔记的关联

数字人口播是 AI 短剧/短视频生产链路的核心环节。Rachel Skill 把这个环节做成了可复用的 Codex 流程——从文案到成品视频的自动化。

### 3. 与 LuxTTS 的关联

Hermes 已有 LuxTTS（Jetson 上的语音克隆），Rachel 用的是 MiniMax 海外版云端 TTS。两者互补——LuxTTS 适合本地低延迟场景，MiniMax 适合高质量批量生产。

### 4. 与 CodexLoom Agent Team 的关联

Rachel Skill 的 job-state.json 是 CodexLoom Topic 的微缩版——追踪工作状态、ID 和结果。15 秒预览门禁 = CodexLoom 的 Needs You（在正确位置找回 Human）。

### 5. 与 Awesome Journal Skills 的关联

三者都是 Codex/Claude Code Skill，展示了 Skill 正在从"个人工具"进化为"专业领域流水线"。

---

## 学习进化借鉴点

| 洞察 | 可借鉴到 Hermes | 优先级 |
|------|----------------|--------|
| **声音和画面拆开** | 数字人生产架构 | 高 |
| **15秒样片门禁** | 付费操作前强制 Human 确认 | 高 |
| **job-state.json** | 任务状态持久化 | 高 |
| **preflight 脚本** | 付费 API 前的确定性检查 | 高 |
| **allow_implicit_invocation: false** | 防止意外触发付费流程 | 高 |
| **不泄露密钥到状态文件** | 安全红线 | 高 |
| **失败不盲目重试** | 避免重复扣费 | 中 |
| **decode-check 完整 MP4** | 产出质量校验 | 中 |

---

## 趋势判断

1. **数字人口播正在标准化**——从手工操作到 Codex Skill 自动化，门槛大幅降低
2. **MiniMax + HeyGen 组合是当前最优解**——MiniMax 声音克隆质量高且便宜，HeyGen 口型驱动效果好
3. **声音和画面拆开是核心设计**——不要让一个平台做两件事，各取所长
4. **15 秒预览门禁是成本控制关键**——先验证再付费，避免浪费
5. **Codex Skill 正在成为内容生产的标准格式**——从代码工具扩展到创意/内容生产流水线

---

## 适用场景

| 场景 | 说明 |
|------|------|
| **知识口播** | 教育类短视频批量生产 |
| **短视频批量** | 多条文案同一 IP 数字人 |
| **课程讲解** | 课件配音+数字人讲解 |
| **产品介绍** | 多语言产品演示 |
| **固定 IP 数字人账号** | 长期运营的虚拟主播 |

---

## 关联分析

- **与 shuohao-skills**：同为 Codex Skill，不同领域（角色拆解 vs 数字人制作）
- **与 AI 短剧分账**：数字人口播是 AI 短剧生产链核心环节
- **与 LuxTTS**：本地 TTS vs 云端 TTS 的互补
- **与 CodexLoom**：job-state.json ≈ Topic 的状态追踪
- **与 TTS 多引擎后端适配器 Skill**：声音和画面拆开的策略模式

---

*笔记创建：2026-08-08 · 来源：@Zesee X Article (970.9K Views) + GitHub rachel-digital-human-production*
