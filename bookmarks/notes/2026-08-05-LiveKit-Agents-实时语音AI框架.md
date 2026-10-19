# LiveKit Agents — 实时多模态语音 AI Agent 框架

> **来源**：[github.com/livekit/agents](https://github.com/livekit/agents)
> **License**：Apache-2.0（轮次检测模型为 LiveKit Model License）
> **Stars**：12.6K · **Forks**：3.5K
> **语言**：Python（另有 [JS/TS 版](https://github.com/livekit/agents-js)）
> **Topics**：agents, ai, openai, real-time, video, voice

---

## 一句话定义

> 一个用于构建**实时、可编程**语音 AI Agent 的开源框架——Agent 能看、能听、能理解，通过 WebRTC 与终端用户低延迟交互。

---

## 核心特性

| 特性 | 说明 |
|------|------|
| **灵活集成** | STT / LLM / TTS / Realtime API 自由组合，支持主流模型提供商 |
| **内置任务调度** | dispatch API 将终端用户连接到 Agent，支持多实例负载均衡 |
| **WebRTC 客户端** | 基于 LiveKit 开源 SDK，覆盖所有主流平台 |
| **电话集成** | 与 LiveKit SIP 电话栈无缝对接，Agent 可拨打/接听电话 |
| **客户端数据交换** | RPC + Data API 与客户端双向通信 |
| **语义轮次检测** | Transformer 模型检测用户说完没有，减少误打断 |
| **MCP 原生支持** | 一行代码集成 MCP Server 提供的工具 |
| **内置测试框架** | 写测试 + LLM-as-Judge 确保 Agent 行为符合预期 |
| **全开源** | 整个栈可自部署，包括 LiveKit Server（最广泛使用的 WebRTC 媒体服务器之一） |

---

## 架构概念

```
终端用户 (浏览器/手机/电话)
      ↓ WebRTC
LiveKit Server (媒体服务器)
      ↓ dispatch API
AgentServer (主进程，任务调度)
      ↓ 启动 Agent 实例
AgentSession (STT → LLM → TTS 管线)
      └── Agent (带 instructions + tools 的 LLM 应用)
```

| 概念 | 类比 | 说明 |
|------|------|------|
| **Agent** | 一个角色 | 有 instructions 和 tools 的 LLM 应用 |
| **AgentSession** | 一个会话容器 | 管理 STT/LLM/TTS 管线与用户的交互 |
| **entrypoint** | 请求处理器 | 交互会话的起点，类似 Web 服务器的 request handler |
| **AgentServer** | Web 服务器 | 主进程，协调任务调度并为用户会话启动 Agent |

---

## 安装

```bash
pip install "livekit-agents[openai,deepgram,cartesia]"
```

---

## 最小示例：语音 Agent

```python
from livekit.agents import (
    Agent, AgentServer, AgentSession, JobContext,
    RunContext, cli, function_tool, inference,
)

@function_tool
async def lookup_weather(context: RunContext, location: str):
    """Used to look up weather information."""
    return {"weather": "sunny", "temperature": 70}

server = AgentServer()

@server.rtc_session()
async def entrypoint(ctx: JobContext):
    session = AgentSession(
        vad=inference.VAD(),
        # 可自由组合任意 STT / LLM / TTS / Realtime API
        stt=inference.STT("deepgram/nova-3", language="multi"),
        llm=inference.LLM("google/gemma-4-31b-it"),
        tts=inference.TTS("cartesia/sonic-3", voice="9626c31c-..."),
    )
    agent = Agent(
        instructions="You are a friendly voice assistant built by LiveKit.",
        tools=[lookup_weather],
    )
    await session.start(agent=agent, room=ctx.room)
    await session.generate_reply(
        instructions="greet the user and ask about their days"
    )

if __name__ == "__main__":
    cli.run_app(server)
```

**环境变量**：`LIVEKIT_URL` · `LIVEKIT_API_KEY` · `LIVEKIT_API_SECRET`

---

## 多 Agent 切换（Handoff）

LiveKit 支持 Agent 间的动态切换——一个 Agent 收集完信息后，可以切换到另一个专用 Agent：

```python
class IntroAgent(Agent):
    """收集用户信息"""
    @function_tool
    async def information_gathered(
        self, context: RunContext, name: str, location: str,
    ):
        """用户提供了信息后触发"""
        return StoryAgent(name, location), "Let's start the story!"

class StoryAgent(Agent):
    """根据信息讲故事"""
    def __init__(self, name, location):
        super().__init__(
            instructions=f"用户叫 {name}，来自 {location}，讲个性化故事",
            # 可切换到 Realtime API
            llm=openai.realtime.RealtimeModel(voice="echo"),
        )
```

---

## 运行模式

| 命令 | 用途 |
|------|------|
| `python myagent.py console` | **终端测试** — 本地音频输入输出，无需外部服务器 |
| `python myagent.py dev` | **开发模式** — 连接 LiveKit Cloud，支持热重载，多 Agent 并发 |
| `python myagent.py start` | **生产部署** — 生产级优化 |

---

## 内置测试框架

```python
@pytest.mark.asyncio
async def test_no_availability() -> None:
    async with AgentSession(llm=google.LLM()) as sess:
        await sess.start(MyAgent())
        result = await sess.run(user_input="Hello, I need to place an order.")
        
        result.expect.next_event().is_function_call(name="start_order")
        result.expect.next_event().is_function_call_output()
        
        # LLM-as-Judge 验证语义
        await (
            result.expect.next_event()
            .is_message(role="assistant")
            .judge(llm, intent="assistant should be asking the user what they would like")
        )
```

---

## 官方示例矩阵

| 场景 | 说明 |
|------|------|
| 🎙️ Starter Agent | 针对语音对话优化的入门 Agent |
| 🔄 多用户 Push-to-talk | 响应房间内多个用户 |
| 🎵 背景音频 | 环境音 + 思考音提升真实感 |
| 🛠️ 动态工具创建 | 运行时动态创建 function tools |
| ☎️ 外呼 Agent | 主动拨打用户电话 |
| 📋 结构化输出 | LLM 结构化输出引导 TTS 语调 |
| 🔌 MCP 支持 | 集成 MCP Server 工具 |
| 💬 纯文本 Agent | 跳过语音，同代码用于文本场景 |
| 📝 多用户转录 | 房间内所有人的实时转录 |
| 🎥 视频头像 | Tavus / Bithuman / LemonSlice 等 AI 头像 |
| 🍽️ 餐厅客服 | 完整的餐厅点餐+预订 Agent |
| 👁️ Gemini Live 视觉 | 能"看见"的视觉 Agent（含 iOS App） |

---

## 生态系统

### Agent SDK
- **Python**（本仓库）· **[Node.js](https://github.com/livekit/agents-js)**

### 客户端 SDK（全平台）
Browser · Swift · Android · Flutter · React Native · Rust · Node.js · Python · Unity · Unity WebGL · **ESP32** · C++

### UI 组件
React · Android Compose · SwiftUI · Flutter

### 服务端 SDK
Node.js · Go · Ruby · Java/Kotlin · Python · Rust · PHP (社区) · .NET (社区)

### LiveKit Server OSS
- [LiveKit Server](https://github.com/livekit/livekit) — WebRTC 媒体服务器
- [Egress](https://github.com/livekit/egress) — 录制/导出
- [Ingress](https://github.com/livekit/ingress) — 输入处理
- [SIP](https://github.com/livekit/sip) — 电话集成

---

## 技术栈

| 层 | 技术 |
|----|------|
| **传输层** | WebRTC（LiveKit Server） |
| **VAD** | Transformer 模型（语义轮次检测） |
| **STT** | Deepgram Nova-3 / OpenAI Whisper / 其他 |
| **LLM** | OpenAI / Google Gemma / Realtime API / 其他 |
| **TTS** | Cartesia Sonic-3 / OpenAI / 其他 |
| **工具** | function_tool 装饰器 + MCP 原生支持 |
| **调度** | AgentServer + dispatch API |
| **包管理** | uv (Astral) |
| **测试** | pytest + LLM-as-Judge |

---

## AI 编码辅助

LiveKit 官方提供两个工具辅助 AI 编码助手开发：

1. **[LiveKit Docs MCP Server](https://docs.livekit.io/mcp)** — 给 AI 访问最新文档、代码搜索、示例
2. **[LiveKit Agent Skill](https://github.com/livekit/agent-skills)** — 架构指导和最佳实践
   ```shell
   npx skills add livekit/agent-skills --skill livekit-agents
   ```

---

## 📎 关键链接

- 📖 官方文档：[docs.livekit.io/agents](https://docs.livekit.io/agents/)
- 🎮 Agents Playground：[agents-playground.livekit.io](https://agents-playground.livekit.io/)
- 💬 Slack 社区：[livekit.io/join-slack](https://livekit.io/join-slack)
- 📦 PyPI：`pip install livekit-agents`
- 🔍 DeepWiki：[deepwiki.com/livekit/agents](https://deepwiki.com/livekit/agents)

---

---

## 内容整理

LiveKit Agents 是目前最成熟的开源实时语音 AI Agent 框架，核心价值在于：

- **实时 WebRTC 基础设施**：LiveKit Server 是最广泛使用的开源 WebRTC 媒体服务器之一，支持全平台客户端（含 ESP32）
- **STT-LLM-TTS 管线自由组合**：不锁定模型提供商，Deepgram/OpenAI/Cartesia/Google 等即插即用
- **语义轮次检测**：用 Transformer 模型而非静音 VAD 判断用户是否说完，大幅减少误打断
- **生产级调度**：AgentServer + dispatch API 内置任务调度和负载均衡，不需要自己搭
- **电话集成**：SIP 栈支持 Agent 直接拨打/接听电话，打通了语音 Agent → 电话场景

## 查询拓展

- LiveKit 的语义轮次检测模型基于什么架构？（Transformer encoder，开源在 LiveKit Model License 下）
- 与 Vapi / Retell AI / Pipecat 等竞品对比，LiveKit 的差异化在哪？（全开源 + 自部署 + WebRTC SFU 架构）
- ESP32 客户端 SDK 意味着可以直接在微控制器上跑 LiveKit 客户端，这对边缘语音 Agent 意味着什么？
- Realtime API（OpenAI）vs 传统 STT→LLM→TTS 管线的延迟差异？
- AgentServer 的水平扩展方案？（多进程 + dispatch API 负载均衡）

## 归纳总结

LiveKit Agents 解决的核心问题是：**把实时语音 AI Agent 从 Demo 变成产品**。它提供了从音视频传输（WebRTC）、模型集成（STT/LLM/TTS）、任务调度（AgentServer）、电话打通（SIP）到测试验证（LLM-as-Judge）的完整栈，且全部开源可自部署。12.6K Stars 和活跃的生态（全平台 SDK + UI 组件 + 服务端 SDK）说明这是当前语音 Agent 赛道的事实标准之一。

## 趋势判断

- **语音 AI Agent 2026 年爆发**：LiveKit Stars 从 5K → 12.6K 快速增长，说明实时语音 Agent 赛道正在快速升温
- **WebRTC 成为语音 Agent 标准传输层**：相比 WebSocket，WebRTC 天然支持低延迟音频、NAT 穿透和多端同步
- **开源全栈 vs API 服务**：Vapi/Retell 走 API 服务路线，LiveKit 走开源全栈路线，两条路线长期共存但企业级更倾向后者（数据主权 + 自部署）
- **MCP 标准化**：LiveKit 原生支持 MCP，说明 MCP 正在成为 Agent 工具调用的事实标准
- **ESP32 SDK 意味着边缘语音 Agent 的可能性**：微控制器直接连 LiveKit Server → 低成本语音 Agent 硬件

## 关联分析

- **与用户研究方向的关联**：LiveKit 的 ESP32 SDK + 语音 Agent 能力，与用户的具身智能（VLA/灵巧手）和边缘 AI（ESP-Claw）方向高度互补——可以用 LiveKit 做语音控制接口
- **与 Hermes Agent 的关联**：Hermes 的语音功能（STT→LLM→TTS）是文本消息驱动，LiveKit 是实时流式驱动。如果要给 Hermes 加实时语音交互能力，LiveKit 是最自然的集成方案
- **与 LuxTTS 的关联**：LuxTTS 是本地 TTS 引擎，而 LiveKit 的 TTS 插件体系支持自定义 TTS。理论上可以把 LuxTTS 作为 LiveKit 的 TTS plugin，实现本地化的实时语音 Agent
- **与 SO-ARM101 的关联**：SO-ARM101 使用 LeRobot 的遥操作架构，LiveKit 的 WebRTC 音视频流可以作为远程操控机器人的低延迟通信层

---

*笔记创建：2026-08-05 · 来源：github.com/livekit/agents README*


## 相关笔记

- Hermes LuxTTS语音系统（devops skill: luxtts-jetson）— 本地TTS引擎对比参考
- [自进化Agent三定律](./2026-08-05-自进化Agent三定律与可验证性约束-从理论框架到工程边界.md) — Agent可验证性设计原则
- 飞书实时消息流API（~/explore, 08-05）— 实时通信协议架构对比
- 开源ASR模型推荐与实测（uclaw/notes, 07-01）— 中文语音识别引擎选型
