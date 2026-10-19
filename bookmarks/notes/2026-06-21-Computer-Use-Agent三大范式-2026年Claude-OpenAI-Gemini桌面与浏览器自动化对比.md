# Computer Use Agent 2026 三大范式：Claude vs OpenAI vs Gemini 桌面与浏览器自动化深度对比

> 📅 2026-06-21 | 夜间自学习
> 🔗 来源：DigitalApplied / WorkOS / JobsByCulture / Anthropic Docs / Browser-Use GitHub
> 🏷️ 关键词：Computer Use、CUA、桌面自动化、浏览器自动化、OSWorld、Function Calling

---

## 一、核心概念

**Computer Use** 指 AI Agent 通过感知屏幕（通常截图）并产生输入动作（鼠标移动、点击、滚动、按键、系统命令）来自动化操作软件。

**核心价值**：自动化**没有 API 的软件**——遗留企业系统、无集成的 SaaS、内部仪表盘、Windows 桌面应用、小众创意软件。

> "这不是 Selenium 2.0。这些 Agent 不依赖脆弱的 CSS 选择器或 XPath，它们**看**屏幕、理解上下文，在界面变化时自适应。"

---

## 二、三大架构赌注

2026 年中，三家头部厂商对 Computer Use 做出了截然不同的架构选择：

| 厂商 | 架构范式 | 核心特点 | 发布时间 |
|------|---------|---------|---------|
| **Anthropic** | 便携式工具使用（Portable Tool Use） | 截图+鼠标键盘工具，跨 OS 可移植 | 持续迭代，Opus 4.7 加入高分辨率视觉 |
| **OpenAI** | 桌面原生后台会话（Desktop-Native） | macOS 优先，隔离后台桌面会话 | Codex Background Computer Use, 2026-04-16 |
| **Google** | 浏览器锚定（Browser-Anchored） | DOM 感知 > 像素解析，源自 Project Mariner | 有限预览至 2026-05 |

### 2.1 Anthropic：便携式工具使用

**设计哲学**：通用 Computer Use 工具——接收截图，返回结构化输入动作，运行时环境由客户负责。

**技术细节**：
- 不是独立产品，而是通过标准 Messages API 暴露的工具
- 开发者传入 computer_use 工具定义，Claude 返回结构化动作，运行时执行
- 可通过 AWS Bedrock / Google Vertex AI / Microsoft Foundry 企业级部署
- Opus 4.7（2026-04-16）支持高达 2,576px 的高分辨率视觉

**优势**：
- 跨 OS 可移植——Linux / Windows / macOS / 容器 / VM
- 一等公民审批循环语义（通过 tool-use API）
- 文档完善，参考 harness 生态活跃
- 最适合**混合桌面+浏览器**工作流

**局限**：
- 需要构建或采用 harness 用于生产环境
- 需管理屏幕流、沙箱运行时、审批循环逻辑

> "可移植性的回报是显著的。Claude 可以驱动 Docker 容器、Linux VM、Windows 桌面、通过 VNC 的远程 Mac mini——任何它能接收像素的屏幕。"

### 2.2 OpenAI：桌面原生后台会话

**Codex Background Computer Use**（2026-04-16 发布）：
- 平台：macOS 优先，更广泛的 OS 支持在路线图上
- 执行模型：后台会话，与工程师主工作站并行
- 支持多个并发 Codex 会话

**优势**：
- 在隔离桌面会话中运行 Agent
- 工程师继续工作的同时 Agent 驱动独立的 macOS 环境
- 与 Codex agent runtime 紧密集成——比 Claude 少很多胶水代码
- 继承 ChatGPT Enterprise SSO、审计日志、数据驻留

> "在 Anthropic 发布 Claude Opus 4.7 的同一天推出桌面原生 Computer Use，OpenAI 在插旗：如果你的机构主要使用 Mac 且想要最低摩擦的后台桌面 Agent 路径，Codex 现在是一个可靠的一方选择。"

### 2.3 Google：浏览器锚定

**设计哲学**：源自 Project Mariner 的浏览器自动化研究，优先 **DOM 感知**而非原始像素解析。

**技术细节**：
- 查询 DOM 获取表单字段，读取 ARIA 角色，检查 CSS 选择器
- 直接在浏览器中触发合成事件
- 融合截图分析 + DOM 结构 + 可访问性树
- 与 Google Workspace 紧密集成

**强项**：营销仪表盘、广告管理器、CRM、分析平台等 Web 工作流

**弱项**：
- 无 Web 界面的原生桌面应用
- 复杂创意软件、遗留 Windows 应用
- OS 级自动化任务

---

## 三、全景观：6 大 Computer Use Agent

### 3.1 全桌面 vs 浏览器专属

| 类型 | 代表 Agent | 特点 |
|------|-----------|------|
| **全桌面** | Claude Computer Use | 控制任何应用——浏览器、终端、文件管理器、原生应用 |
| **浏览器专属** | OpenAI Operator / Gemini / Stagehand / browser-use / Browser MCP | 范围限于 Web 导航——更安全、更快、更易沙箱化 |

### 3.2 六大 Agent 对比矩阵

| Agent | 范围 | 模型 | 开源 | 最适合 |
|-------|------|------|------|--------|
| **Claude Computer Use** | 全桌面 | Claude | API | 跨应用工作流 |
| **OpenAI Operator** | 仅 Web | CUA (GPT-4o 变体) | 否（托管） | Web 任务、表单填写 |
| **Gemini Computer Use** | 浏览器 | Gemini | API | Google 生态 |
| **Stagehand** | 浏览器 | 任意 (BYOM) | ✅ MIT | 生产自动化 |
| **browser-use** | 浏览器 | 任意 (BYOM) | ✅ MIT | Python Agent / LangChain |
| **Browser MCP** | 浏览器 | 任意 MCP host | ✅ | Agent 工具集成 |

### 3.3 关键性能指标

| 指标 | 数据 |
|------|------|
| OpenAI Operator Web 任务成功率 | **87%**（WebVoyager 基准） |
| 传统工具抗性 | Computer Use Agent 的弹性是传统工具的 **3 倍** |
| Claude Computer Use 动作延迟 | 2-5 秒/动作 |
| OSWorld 头部分数 | 30-40%（远低于 SWE-bench 的 90%+） |

---

## 四、开源方案深度解析

### 4.1 Stagehand（Browserbase）

> "开发者爱 Stagehand 的原因：自带模型无供应商锁定；Playwright 基础——所有 Playwright API 仍可用；Zod schema 结构化提取；14,000+ GitHub stars"

```typescript
import { Stagehand } from "@browserbasehq/stagehand";

const stagehand = new Stagehand({ env: "LOCAL", modelName: "claude-sonnet-4" });
await stagehand.init();
await stagehand.goto("https://example.com/jobs");

// AI 驱动的元素选择——无需 CSS 选择器
await stagehand.act("Click the Remote toggle switch");
await stagehand.act("Select 'Engineering' from the role filter");

// 结构化数据提取
const jobs = await stagehand.extract({
  instruction: "Extract all job titles and company names",
  schema: { title: "string", company: "string" }
});
```

### 4.2 browser-use

- **60,000+ GitHub stars**——Python 优先的开源浏览器 Agent
- 原生 LangChain 集成
- 多标签浏览支持
- 内置视觉 + DOM 提取

```python
from browser_use import Agent
from langchain_openai import ChatOpenAI

agent = Agent(
    task="Find remote ML engineer jobs at companies with good culture ratings",
    llm=ChatOpenAI(model="gpt-4o")
)
result = await agent.run()
```

### 4.3 Browser MCP

- 标准化浏览器工具，可组合到任何 MCP host
- 框架无关
- 适合已有 Agent 框架的浏览器能力扩展

---

## 五、OSWorld 基准与真实难度

### 5.1 OSWorld 是什么

- 369 个桌面自动化任务，跨 Linux / Windows / macOS
- 测试鼠标移动、点击、输入、屏幕阅读
- **头部分数仅 30-40%**——远低于 SWE-bench 的 90%+

### 5.2 为什么 OSWorld 分数低

| 挑战 | 说明 |
|------|------|
| 像素级精确操作 | 需要精确坐标点击，截图压缩后细节丢失 |
| 多步推理 | 真实桌面任务需要 10+ 步连续操作 |
| 意外对话框 | 系统更新提示、权限弹窗等打断流程 |
| 跨应用协调 | 在不同应用间复制粘贴数据 |
| 状态追踪 | 需要记住之前操作的结果 |

### 5.3 三大范式在 OSWorld 的表现

- **Claude**（全桌面+便携）：最灵活，跨应用能力最强
- **OpenAI CUA**（桌面原生）：macOS 场景深度优化
- **Gemini**（浏览器）：Web 任务场景最优，桌面任务受限

---

## 六、对 Hermes 系统的启示

### 6.1 Hermes 当前的 Computer Use 能力

Hermes 已有 `cdp-browser-automation` Skill（Chrome DevTools Protocol）和 `google-search-cdp` Skill，这些是**浏览器层**的自动化，但不具备全桌面 Computer Use 能力。

### 6.2 可落地路径

| 升级方向 | 方案 | 优先级 |
|---------|------|--------|
| **浏览器自动化增强** | 引入 browser-use 或 Stagehand 替代手写 CDP 脚本 | P1 |
| **MCP 浏览器工具** | 集成 Browser MCP，标准化浏览器操作接口 | P2 |
| **桌面 Computer Use** | Claude Computer Use API + VNC 沙箱（Jetson 不适合，需要 x86 主机） | P3 |
| **结构化提取增强** | Stagehand 的 Zod schema 提取模式可借鉴到 web_extract | P1 |

### 6.3 架构建议

```
用户请求 → Hermes 分析任务类型
    ├── 纯 Web 任务 → browser-use / Stagehand（BYOM，成本低）
    ├── 混合桌面+Web → Claude Computer Use API（最强但最贵）
    └── 已有 API 的系统 → 直接 API 调用（无需 Computer Use）
```

**关键原则**：不是所有自动化都需要 Computer Use。优先使用 API > 浏览器自动化 > 全桌面 Computer Use。

### 6.4 开源方案的选择

对于 Hermes 的嵌入式+Jetson 环境：
- **browser-use** 最合适——Python 优先、轻量、BYOM、可本地部署
- **Stagehand** 需要 Node.js 环境，但结构化提取能力强
- **Browser MCP** 如果 Hermes 已有 MCP 集成，最低摩擦接入

---

## 七、Function Calling vs Computer Use 演进

### 7.1 2026 年 Function Calling 2.0

传统 Function Calling（工具使用）和 Computer Use 正在融合：

| 维度 | 传统 Function Calling | Computer Use |
|------|---------------------|-------------|
| 交互对象 | API / SDK | GUI / 屏幕 |
| 精度 | 确定性高（结构化 I/O） | 概率性（截图→动作推断） |
| 适用场景 | 有 API 的系统 | 无 API 的遗留/GUI 系统 |
| 延迟 | 毫秒级 | 秒级（2-5s/动作） |
| 成本 | 低（token 少） | 高（截图=大量 token） |

### 7.2 混合策略

现代 Agent 系统越来越多地**按任务混合使用**：
1. 优先尝试 API/Function Calling
2. API 不可用时降级到浏览器自动化
3. 浏览器也不行时降级到全桌面 Computer Use

---

## 八、参考资料

- Computer Use Agents 2026 Matrix: https://www.digitalapplied.com/blog/computer-use-agents-2026-claude-openai-gemini-matrix
- Anthropic vs OpenAI CUA: https://workos.com/blog/anthropics-computer-use-versus-openais-computer-using-agent-cua
- Computer Use Guide 2026: https://jobsbyculture.com/blog/computer-use-agents-guide-2026
- Claude Computer Use Docs: https://platform.claude.com/docs/en/agents-and-tools/tool-use/computer-use-tool
- browser-use: https://github.com/browser-use/browser-use
- Best Open Source CUA Windows: https://fazm.ai/blog/best-open-source-computer-use-agent-windows-2026

## 相关笔记

- [AI 编程智能体 2026：从 SWE-Bench 到自主 AI 团队的演进](2026-06-17-AI编程智能体2026-从SWE-Bench到自主AI团队.md) (关键词: AI Agent, 编程智能体, SWE-Bench)
- [AI编程Agent2026年中架构演进-SWE-bench排行榜与Claude-Code泄露分析](2026-06-21-AI编程Agent2026年中架构演进-SWE-bench排行榜与Claude-Code泄露分析.md) (关键词: Claude, Agent架构, 同日同簇)
- [一文搞懂 Loop 工程、Harness 工程、FDE — Agentic Engineering 的三层体系](2026-06-15-Agentic-Engineering三层体系-Loop-Harness-FDE.md) (关键词: Agent范式, Engineering)
- [生产级 Multi-Agent Harness 设计全拆解](2026-06-14-生产级Multi-Agent-Harness设计全拆解.md) (关键词: Agent架构, Harness)
