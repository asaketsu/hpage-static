# Kun 的 Pi Agent 配置：极简、实用、优雅

> **来源**: [blog.kunchenguid.com - Kun's Pi Agent Config](https://blog.kunchenguid.com/p/kuns-pi-agent-config)
> **作者**: Kun Chen（前 Meta L8 工程师，现独立开发者）
> **博客**: Kun's Field Notes（agentic engineering / solo building / 软件前沿）
> **日期**: 2026-07-31
> **标签**: `Pi-Agent` `Agent-Harness` `配置` `dotfiles` `CLI` `实战配置`

---

## 核心结论

Kun 分享了他使用 Pi agent 的实际配置。Pi 是一个 provider-neutral、极简、深度可定制的 AI agent harness。配置哲学：**"这不是 100 个花哨技巧，而是我真正在用、离不开的东西"**。核心只有几个配置项 + 3 个第三方扩展 + 1 个自定义主题 + 1 个自定义终端标题扩展。

---

## 一、为什么选 Pi？

| 维度 | 说明 |
|------|------|
| **何时用** | 除 Claude 外的所有模型（Anthropic 禁止第三方 harness 使用订阅配额） |
| **Claude 怎么办** | 只能用 Claude Code |
| **选 Pi 的理由** | Provider-neutral（厂商中立）+ Minimal（极简）+ Deeply customizable（深度可定制） |
| **核心理念** | AI 模型不断进步，harness 需足够灵活以跟随模型进化 |

> 作者：前 Meta/Microsoft/Atlassian L8 工程师，现为独立开发者，写 agentic engineering 和 solo building 实战笔记。

---

## 二、主配置：settings.json

路径：`~/.pi/agent/settings.json`

```json
{
  "images": { "blockImages": false },
  "terminal": { "showImages": false },
  "hideThinkingBlock": true,
  "quietStartup": true,
  "theme": "rose-pine-moon",
  "steeringMode": "all",
  "followUpMode": "all",
  "collapseChangelog": true,
  "packages": [
    "npm:pi-web-access@0.14.0",
    "npm:@ryan_nookpi/pi-extension-codex-fast-mode@0.2.6",
    "git:github.com/algal/pi-openai-server-compaction@c6d593087709e9481223dc6c6c2269b371b5e055"
  ]
}
```

### 关键配置项解读

| 配置项 | 值 | 为什么这么配 |
|--------|-----|-------------|
| **hideThinkingBlock** | true | 终端更干净，LLM 思考过程没有观看价值 |
| **steeringMode** | all | 发了多个 steering prompt，当然要全部尽快发出 |
| **followUpMode** | all | **最重要**——模型工作时持续排队 follow up，一次性发送比逐个发出高效得多 |
| **quietStartup** | true | 安静启动 |
| **collapseChangelog** | true | 折叠更新日志 |

---

## 三、三个第三方扩展

### 1. pi-web-access（网页访问）

```
npm:pi-web-access@0.14.0
```

| 维度 | 说明 |
|------|------|
| **功能** | 搜索和浏览网页内容 |
| **为什么必需** | 原版 Pi 极简到连搜索和浏览网页的能力都没有——"no-brainer"（无需犹豫的必装项） |

### 2. pi-extension-codex-fast-mode（Codex 快速模式）

```
npm:@ryan_nookpi/pi-extension-codex-fast-mode@0.2.6
```

| 维度 | 说明 |
|------|------|
| **功能** | 使用 GPT 模型时激活快速模式（on/off 开关） |
| **代价** | 2x tokens 换 2.5x 速度 |
| **场景** | 需要 Codex 后端快速推理时 |

### 3. pi-openai-server-compaction（OpenAI 服务端压缩）

```
git:github.com/algal/pi-openai-server-compaction@c6d593087709e9481223dc6c6c2269b371b5e055
```

| 维度 | 说明 |
|------|------|
| **功能** | 当上下文窗口太长需要压缩时，使用 OpenAI 的"服务端压缩"（secret sauce） |
| **价值** | 服务端压缩是 Codex 默认使用的，是 Codex 长任务能力强的主要原因——尽管 GPT 模型上下文窗口短 |
| **效果** | 让 Pi 在 GPT 模型上也获得 Codex 级别的长任务能力 |

---

## 四、模型覆盖：models.json

路径：`~/.pi/agent/models.json`

```json
{
  "providers": {
    "openai-codex": {
      "modelOverrides": {
        "gpt-5.6-luna": { "contextWindow": 272000 },
        "gpt-5.6-sol": { "contextWindow": 272000 },
        "gpt-5.6-terra": { "contextWindow": 272000 }
      }
    }
  }
}
```

### 为什么设 272k？

| 原因 | 说明 |
|------|------|
| **OpenAI 实际支持更长** | GPT 模型实际可支持更长上下文请求 |
| **但超过 272k 会翻倍计费** | 超 272k input tokens 时成本 ×2 |
| **策略** | 将 contextWindow 设为 272k，超过时自动触发压缩回落 |
| **效果** | 避免快速消耗配额或 API 费用 |

> 这是一个精妙的成本控制技巧——通过设上限触发自动压缩，而非无限膨胀上下文导致翻倍计费。

---

## 五、自定义主题：rose-pine-moon

路径：`~/.pi/agent/themes/rose-pine-moon.json`

| 维度 | 说明 |
|------|------|
| **主题** | Rose Pine Moon 配色（个人偏好） |
| **核心要点** | 你可以直接跟 Pi 对话，让它帮你生成任何你想要的主题 |
| **方法** | 指向一个你喜欢的官方配色主题，Pi 会帮你做 |

> 主题完全可编程——定义 vars（变量）+ colors（颜色映射），涵盖 UI 每个元素的配色。

---

## 六、自定义扩展：终端标题状态

路径：`.pi/agent/extensions/terminal-status-title.js`

| 维度 | 说明 |
|------|------|
| **功能** | 将实时 Agent 状态打印为终端标题 |
| **状态指示** | ⠋ 旋转（working）/ ✓ 完成（done）/ ✗ 错误（error）/ ○ 空闲（idle） |
| **显示内容** | `状态指示 | π | 会话名或目录名` |
| **价值** | 开多个 Pi agent 终端标签时，一眼看出哪个在工作、哪个在等待输入 |

### 核心逻辑

```javascript
// 监听 Agent 生命周期事件
pi.on("session_start", ...);  // idle
pi.on("agent_start", ...);    // working (旋转动画)
pi.on("agent_settled", ...);  // done (✓)
pi.on("session_shutdown", ...); // 清理
```

---

## 七、额外彩蛋：/calm 平静模式

路径：`~/.pi/agent/extensions/calm`

| 维度 | 说明 |
|------|------|
| **功能** | 添加 `/calm` 命令，切换平静模式 |
| **开启效果** | 隐藏所有工具调用 → 终端极简安静 |
| **思考指示器** | 替换为小船在平静海面上航行的动画 |
| **用途** | 需要专注时，屏蔽所有工具调用噪音 |

---

## 八、配置哲学总结

| 原则 | 体现 |
|------|------|
| **极简** | 不装花哨扩展，只装真正离不开的 3 个 |
| **实用** | 每个配置都有明确理由（followUpMode/compaction/272k 上限） |
| **优雅** | 自定义主题 + 平静模式，追求体验 |
| **成本意识** | 272k 上限触发自动压缩，避免翻倍计费 |
| **可定制** | 终端标题扩展 + calm 模式，深度个性化 |

> "That's everything - no fancy skills or workflows. Just the minimum to give me the core primitives I need, help me achieve good efficiency, and remove distractions."

---

## 九、Pi Agent 与其他 Harness 对比

| 维度 | Pi | Claude Code | Cursor | Hermes |
|------|-----|-------------|--------|--------|
| **Provider 中立** | ✅ 核心卖点 | ❌ 仅 Claude | ✅ 多模型 | ✅ |
| **极简** | ✅ 极致极简 | 中 | 功能多 | 中 |
| **可定制** | ✅ 深度（扩展/主题） | 中 | 中 | ✅ 深度 |
| **服务端压缩** | ✅ 通过扩展 | ✅ 内置 | ❌ | ❌ |
| **适用场景** | 非 Claude 模型的 CLI agent | Claude 专属 | IDE 内编码 | 多平台 Agent |

---

## 十、公开配置仓库

所有配置公开在作者的 dotfiles 仓库：

| 仓库 | 链接 |
|------|------|
| **dotfiles** | [github.com/kunchenguid/dotfiles](https://github.com/kunchenguid/dotfiles) |
| **calm 扩展** | [dotfiles/.../extensions/calm](https://github.com/kunchenguid/dotfiles/tree/main/home/.pi/agent/extensions/calm) |

---

## 十一、关键术语速查

| 术语 | 说明 |
|------|------|
| **Pi** | Provider-neutral 的极简 AI agent harness |
| **Harness** | Agent 控制框架，定义 Agent 怎么工作 |
| **steeringMode** | 多个 steering prompt 的发送模式 |
| **followUpMode** | follow up prompt 的排队发送模式 |
| **Server Side Compaction** | OpenAI 的服务端上下文压缩（Codex 的 secret sauce） |
| **contextWindow** | 上下文窗口上限 |
| **272k 阈值** | OpenAI 超 272k tokens 翻倍计费的临界点 |
| **Fast Mode** | Codex 快速模式（2x tokens 换 2.5x 速度） |

---

## 十二、与现有笔记的关联

| 关联笔记 | 关系 |
|---------|------|
| **Agent Harness 知识体系总纲** | Pi 是一个典型的极简 Harness 实践案例——provider 中立 + 可定制 + 扩展机制 |
| **学 Agent 的正确顺序** | Kun 的配置体现了 Phase 4（状态管理/日志）的工程化实践 |
| **AI Agent 从玩具走向生产系统** | Pi 的服务端压缩 + 成本控制（272k 上限）正是生产级工程化思维 |
| **Hermes Agent** | Hermes 与 Pi 是同类（可定制 Harness），Pi 的扩展机制和成本控制策略可借鉴到 Hermes |

## 相关笔记
- [pi-agent配置指南](2026-05-30-pi-agent配置指南.md)
- [PiAgent深度分析](2026-05-24-PiAgent深度分析.md)
- [DeepSeek-Agent-Harness执行栈全景图](2026-08-06-DeepSeek-Agent-Harness执行栈全景图.md)
- [Pi-Agent-vs-Hermes-vs-Claude-Code对比分析](2026-05-26-Pi-Agent-vs-Hermes-vs-Claude-Code对比分析.md)
