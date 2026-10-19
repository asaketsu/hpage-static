# Qwen Audio Agent：让 Agent 始终在场的实时语音运行时

> **来源**: [github.com/QwenAudio/qwen-audio-agent](https://github.com/QwenAudio/qwen-audio-agent)
> **团队**: 阿里通义千问 QwenAudio
> **许可证**: Apache 2.0 | **Stars**: 582 | **语言**: JavaScript (Node.js)
> **v1.0.0**: 2026-07-30
> **日期**: 2026-07-31
> **标签**: `语音Agent` `实时语音` `ACP` `Qwen-Audio` `全双工` `个人助理`

---

## 核心结论

阿里通义千问团队开源的实时语音运行时，核心创新：**前台对话不阻塞 + 后台任务异步执行**。传统语音助手"说完就等"，Qwen Audio Agent 让 Agent 始终在场——对话继续，任务也在继续。通过 ACP 协议统一接入各类编码 Agent（OpenCode/OpenClaw/Hermes 等）。

---

## 一、核心差异化

| 传统语音助手 | Qwen Audio Agent |
|---|---|
| 用户说完→等待→回复→等待 | 用户说话→即时回复+后台异步处理 |
| 调用工具时对话暂停 | **对话继续，任务也在继续** |
| 一次一个任务 | 多后台任务并行，可追问进度/取消 |

### 工作流示例

```
用户: "帮我查航班，顺便明天天气"
  ├── 前台即时: "好的，马上帮你查"
  ├── 后台异步: 航班查询任务 → 后台 Agent
  ├── 前台继续: 用户可继续说话
  │             "对了，提醒下午3点开会"
  │             "没问题，已设置提醒"
  └── 后台完成: 航班结果自然回到对话
                "已经查到了，最近的航班是..."
```

---

## 二、技术定位

| 维度 | 值 |
|------|-----|
| **语言/运行时** | Node.js 22.22.2+ / JavaScript |
| **语音前端** | Qwen Audio 3.0 Realtime（DashScope/百炼 API） |
| **后台协议** | ACP (Agent Communication Protocol) stdio |
| **模型** | qwen-audio-3.0-realtime-plus（默认）/ flash |
| **界面** | WebUI / TUI / macOS 桌面悬浮球 |
| **部署** | npm / macOS .dmg / 用户后台服务 |

---

## 三、三层架构

| 层 | 职责 |
|---|---|
| **第一层：语音前台** | Qwen Audio 3.0 Realtime，全双工实时语音，自然打断，多轮对话 |
| **第二层：Gateway** | 路由决策（即时 vs 后台）、任务管理（创建/追踪/取消/回传）、用户记忆 |
| **第三层：后台 Agent** | ACP 接入可插拔 Agent，复用已有工具/MCP/Skill，异步执行 |

> 用户面对的始终是同一个助理。

---

## 四、后台 Agent 生态

| Agent | 接入方式 | 推荐指数 |
|-------|---------|---------|
| OpenCode | 原生 ACP，自动安装 | ★★★★★ |
| OpenClaw | 内置 ACP 桥接，自动安装 | ★★★★★ |
| Qoder | 原生 ACP | ★★★★★ |
| Kimi Code | 原生 ACP | ★★★★★ |
| **Hermes** | **原生 ACP** | ★★★★☆ |
| CodeBuddy | 原生 ACP | ★★★★☆ |
| Codex | 外部 ACP 适配 | ★★★★☆ |
| Claude Code | 外部 ACP 适配 | ★★★★☆ |
| 任意 ACP Agent | 通用入口 | — |

### ACP 通用接入

```dotenv
AGENT_PROTOCOL=acp
ACP_COMMAND=your-agent
ACP_ARGS=["--acp"]
ACP_LABEL=My Agent
ACP_WORKSPACE=/path/to/project
```

---

## 五、功能特性

| 能力 | 说明 |
|------|------|
| 全双工实时语音 | 全链路实时，macOS 带回声消除 |
| 自然打断 | 说话即打断 AI 回复 |
| 后台任务并行 | 前台不停，后台多任务异步 |
| 任务生命周期 | 创建/追踪/取消/结果回传 |
| 多 Agent 接入 | ACP 协议统一接入 |
| 跨会话记忆 | USER.md + frontend-memory.json |
| 多平台界面 | WebUI / TUI / macOS 悬浮球 |
| 后台常驻 | `gateway install` 为系统服务 |

### 平台音频模式

| 平台 | 默认模式 | 打断方式 |
|------|---------|---------|
| macOS | 全双工+回声消除 | 直接说话 |
| Linux/Windows | 半双工 | 播报时按 `x` |
| Linux/Windows(耳机) | 全双工无回声消除 | `--audio-mode full` |

---

## 六、与 HF Speech-to-Speech 功能对比

| 维度 | Qwen Audio Agent | HF Speech-to-Speech |
|------|------------------|---------------------|
| **来源** | 阿里通义千问 | HuggingFace |
| **语言** | JavaScript (Node.js) | Python |
| **语音模型** | Qwen Audio 3.0 Realtime（百炼 API） | 可插拔（Parakeet/Whisper/Qwen3-TTS 等） |
| **核心创新** | **前台对话+后台任务并行** | **全模块化流水线（VAD→STT→LLM→TTS）** |
| **后台任务** | ✅ 多任务异步，结果回对话 | ❌ 无（LLM Proxy 可做侧任务但非核心） |
| **Agent 协议** | ACP | OpenAI Realtime 兼容 |
| **LLM 灵活度** | 前台绑定 Qwen Audio，后台可选 | 任意 OpenAI 兼容 LLM |
| **部署方式** | npm/macOS .dmg/系统服务 | pip/Docker |
| **界面** | TUI/WebUI/macOS 悬浮球 | 客户端自建 |
| **记忆** | ✅ USER.md + 跨会话记忆 | ❌ 无 |
| **生态** | 接入编码 Agent（OpenCode/Hermes 等） | 接入推理引擎（vLLM/llama.cpp） |
| **目标** | 个人助理（始终在场） | 语音 Agent 应用开发 |
| **Stars** | 582（新项目，7月底开源） | 8,700+ |

### 选型建议

| 场景 | 推荐 | 理由 |
|------|------|------|
| 个人语音助理（始终在场） | **Qwen Audio Agent** | 前台对话+后台任务并行 |
| 语音 Agent 应用开发 | **HF S2S** | 模块化流水线，组件全可换 |
| 需要后台执行代码/任务 | **Qwen Audio Agent** | ACP 接入编码 Agent |
| 需要自定义 STT/TTS/LLM | **HF S2S** | 全栈可替换 |
| macOS 桌面常驻 | **Qwen Audio Agent** | 悬浮球+内置 Gateway |
| 机器人/设备后端 | **HF S2S** | 生产验证（Reachy Mini 量产） |
| **Hermes 集成** | **两者都可** | QAA 接 Hermes 为后台 Agent；HF S2S 接 LLM |

---

## 七、与 Hermes 的直接关系

**Qwen Audio Agent 官方支持 Hermes 作为后台 Agent**（★★★★☆，原生 ACP）。

```
用户语音 → Qwen Audio Agent Gateway
              ├── 即时回答 → Qwen Audio 3.0 Realtime
              └── 后台任务 → ACP → Hermes (jc-server)
                              ├── 复用已有工具/MCP/Skill
                              ├── 异步执行复杂任务
                              └── 结果回到语音对话
```

### 集成配置

```dotenv
AGENT_PROTOCOL=hermes
QWEN_AUDIO_AGENT_BACKEND_MODEL=qwen3.7-max  # 或留空复用 Hermes 配置
```

---

## 八、安装快速参考（暂不部署）

```bash
npm install -g qwen-audio-agent
qwenaudio config  # 填入 DASHSCOPE_API_KEY
qwenaudio         # 启动 Gateway
qwenaudio tui     # 启动 TUI
```

---

## 九、与现有笔记的关联

| 关联笔记 | 关系 |
|---------|------|
| **HF Speech-to-Speech** | 同赛道竞品，功能对比见上文 |
| **SGLang vs vLLM** | QAA 后台 Agent 的模型推理底层引擎 |
| **ESP-Claw** | OpenClaw 是 QAA 的五星后台 Agent |
| **ABot-N1** | "慢-快双系统"类比"前台即时+后台异步" |
| **Gemini Robotics 2** | 机器人语音交互场景，QAA 可作为语音层 |

## 相关笔记

- [语音智能体闭环 Typeless VoxCPM2](explore/2026-06-14-语音智能体闭环-Typeless-VoxCPM2.md) — 全双工语音交互闭环架构，QAA 的竞品/互补方案
- [语音克隆 TTS 2026 开源新势力格局](explore/2026-06-05-语音克隆TTS-2026开源新势力格局.md) — TTS 引擎选型，QAA 语音输出层的后端候选
- [端侧离线语音待办工程实践](explore/2026-05-22-端侧离线语音待办工程实践.md) — 离线 ASR+TTS 工程化，QAA 边缘部署的参考
- [VLA Action Head 动作生成四种路线](2026-07-31-VLA-Action-Head动作生成四种路线.md) — 机器人语音+动作协同，QAA 作为具身语音层
