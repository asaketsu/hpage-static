# Web 开发 / Agent: headless 支持 — 深度学习笔记

> 深度研究笔记 | 2026-10-18 | 类型: auto-explore
> 来源: TinyFish blog (headless-browser-vs-ai-agents), The New Stack (why-headless-browsers-are-key-for-ai-agents, 2026-10-05), Playwright 官方文档 (getting-started-mcp), Mastra/Firecrawl 2026 综述, dev.to Browser Tools 系列

---

## 一、摘要

「headless 支持」在 2026 年的 Web 开发语境里已经从"无头浏览器跑测试"演化为 **AI Agent 抓取/操作 Web 的基础设施层**。核心分层：headless browser（指令跟随，determinism 高）→ AI web agent（目标导向，自适应强）→ 云端托管浏览器基础设施（Browserbase / Cloudflare Browser Run / Bright Data）。对 Hermes 这类本地 Agent 而言，落地要点是 Playwright MCP 的 `--headless` 模式 + accessibility snapshot（省 token），以及 MCP 工具定义本身的 context 开销权衡。

## 二、关键发现

### 2.1 两种范式的本质区别（TinyFish）

- headless browser = **instruction-following**：你写精确步骤（`page.click('#submit-btn')`），浏览器执行。selector 变了就挂，维护成本高但确定性强。
- AI web agent = **goal-directed**：你描述结果（"提交表单并返回确认号"），Agent 自己规划步骤。对布局变化有韧性，但路径不可复现。
- 选型判据：UI 测试、稳定站点低频抓取、本地开发 → Playwright；动态站点、目标型任务、生产规模 → agent。
- 永远不该用 agent 的场景：需要对特定 DOM 状态做确定性断言的测试、字节级可复现工作流、需要精确定位 selector 失败点的调试。

### 2.2 Headless 成为 Agent 关键技术的原因（The New Stack）

- LLM 规划能力成熟（GPT-4o/Claude 4/Gemini 2.5 级模型能读懂页面结构）+ 托管浏览器基础设施成熟（Browserbase/Steel 解决了 headless 规模化问题），两条件 2025-2026 同时到位。
- 生产级架构的分离原则：**reasoning（LLM）/ execution（Playwright）/ infrastructure（云浏览器）三层解耦**——混在一层里会变脆、难调试、难扩展（browserless.io 实践结论）。

### 2.3 Playwright MCP 的 headless 实操（官方文档）

- 默认 headed（可见浏览器便于观察），无显示环境或无人值守时加 `--headless`。
- 核心机制：**accessibility tree snapshot 而非截图**，不需要 vision 模型。snapshot 给出元素 ref（如 `ref=e5`），LLM 用 ref 交互——这是 token 效率的关键。
- 三种 profile 模式：Persistent（默认，跨会话保 cookie，按 workspace hash 隔离）、Isolated（`--isolated` 每次全新）、`--storage-state` 加载初始状态。
- `browser_run_code_unsafe` 可跑任意 Playwright JS，**等价 RCE**，只对可信客户端开启。
- 实验性 WebMCP：页面可向 Agent 注册自己的工具（`webmcp_<tool>`），工具名/schema 由页面提供=不可信输入。
- Docker 官方镜像只支持 headless Chromium；本地版可选 chrome/firefox/webkit/msedge。

### 2.4 Token 经济学（dev.to 实测口径）

- Playwright MCP 工具定义本身约烧 ~15,000 token（还没干活先扣）；PinchTab 类 HTTP 方案每页 snapshot 约 800 token，远低于截图模式的数千 token。
- 结论：MCP 便利性与 context 开销有真实权衡；对 context 敏感的长会话 Agent（Hermes 正是），轻量 HTTP/CLI 桥可能更划算。

### 2.5 生态版图速览

- 云基础设施：Browserbase（会话持久化+录制回放，Playwright 兼容）、Cloudflare Browser Run（边缘 headless Chrome，Puppeteer/Playwright/CDP）、Bright Data Agent Browser（带指纹/验证码/IP 轮换）。
- CLI 直控：Vercel Labs Agent Browser（Rust，`agent-browser click @e2` 式命令，35k+ stars）。
- 一体化 API：TinyFish（同一 key 既能当 CDP 云浏览器也能当 Web Agent，按任务切换）。

## 三、对工作的价值

1. **搜索降级链补强**：本地 Hermes 已有 Chrome CDP（google-search-cdp / chatgpt-image 等技能依赖）。Playwright MCP headless 可作为 web_extract 失败后的下一级兜底——accessibility snapshot 模式比截图+vision 省 token 一个数量级。
2. **反爬场景**：微信文章/X 抓取链（wechat-article-extraction / x-article-extraction 技能）遇到 JS 渲染墙时，headless 是正解而非反复换 UA。
3. **上下文预算意识**：MCP 工具定义 15k token 的账要算进 routing 决策（与 adaptive-inference-routing 技能的预算思想一致）——按需挂载而非常驻。
4. **三层解耦原则**可迁移到 Hermes 的工具设计：推理层（模型）/执行层（脚本）/基础设施层（守护进程）分离，与现有 hermes-disaster-recovery 的分层思路同构。

## 四、行动建议

- [ ] 短期：给 Hermes 的 Chrome CDP 链补一个 accessibility-tree 抓取模式（省 token，先于截图方案）。
- [ ] 中期：评估 Playwright MCP 作为 web_extract 的第三级降级（排在 Tavily/智谱 MCP 之后），`--headless --isolated` 起步，禁开 `browser_run_code_unsafe`。
- [ ] 观察项：WebMCP（页面自注册工具）标准化进展，落地后站点抓取可从"解析 DOM"变"调页面 API"。

---

*笔记由 auto-explore 嗅探任务生成；来源均经 web_search + web_extract 实抓。*
