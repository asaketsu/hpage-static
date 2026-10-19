# Web 开发/Agent: origin trial 转正状态 — Chrome 内置 AI 毕业 + WebMCP 入场

> 探索日期: 2026-10-15 | 兴趣等级: L2 | 来源数量: 5（Chrome 官方文档引用×2 + dev.to + http.dev + X/ChromiumDev）| 类型: auto-explore

## 摘要

2026 年是 Web 平台"实验特性毕业"的分水岭：Chrome 内置 AI 家族中 **Prompt API 已从 origin trial 转正为 stable**（extensions=Chrome 138，web=Chrome 148），Summarizer/Translator/Language Detector 同批转正（138）；**WebMCP 在 Chrome 149 开启新的 origin trial**——网页可向浏览器内 AI Agent 暴露带 JSON Schema 的结构化工具。origin trial 机制本身也跨引擎化：Firefox 接受同一 header 形式，Edge 有独立程序。

---

## 关键发现

### 1. 转正名单（Stable，无需 OT token）

- **Prompt API**：extensions 138+ / web 148+，页面 JS 直呼端上 Gemini Nano
- **Summarizer / Translator / Language Detector**：138+ stable
- 命名陷阱：现行 API 面是 `LanguageModel` 全局对象（`LanguageModel.availability()` → `LanguageModel.create()`），**不是** 2024 预览期的 `window.ai`——抄旧代码必报错

### 2. OT 结束但未转正（Developer trial 中间态）

- Writer / Rewriter / Proofreader 的 OT 窗口已过期（Writer/Rewriter 137–148，Proofreader 141–145），现列 Developer trial
- **OT 结束 ≠ 转正**：surface 仍会变，无 fallback 禁上生产

### 3. 新入场：WebMCP（Chrome 149 origin trial，I/O 2026-05-19 宣布）

```js
navigator.modelContext.registerTool({
  name: "addTodo",
  description: "Add a new item to the todo list",
  inputSchema: { type: "object", properties: { text: { type: "string" } }, required: ["text"] },
  execute: ({ text }) => { /* 页面自己的业务逻辑 */ return `Added todo: ${text}`; },
});
```

- 两种形态：命令式 JS（registerTool + JSON Schema + execute 回调）与声明式（HTML 表单标注）
- 解决 agent actuation 三痛点：慢（每步过 layout/paint）、脆（class 改名即断）、贵（每步读页面烧 token）
- 现状约束：仅 Gemini in Chrome 消费；需可见浏览器上下文（headless agent 用不了，刻意设计保人在环）；discovery 未解决（无 tools 版 robots.txt）；标准在 W3C Web Machine Learning 组

### 4. origin trial 机制演进（跨引擎化 + token 语义）

- Token 随 trial 本身过期（旧政策固定 6 周）；**trial 延长不延长已发 token**，须重新生成
- Chrome **静默忽略**过期 token——页面还在发 header 而特性已消失，无 console 报错，排障盲区
- 全局护栏：用量超全部页面加载 0.5% 自动停（deprecation trial 例外）
- iframe 不继承 token；第三方 token 只能走 external script 不能走 header
- 引擎格局：Firefox 接受同 header/meta；Edge 独立门户；Safari 只走 Develop 菜单 per-user flag（服务端 opt-in 只覆盖 Chromium+Gecko）

### 5. Prompt API 的 Chrome 149 增量（仍在演进）

- 多语言会话（en/es/ja/de/fr）、多模态输入（text/image/audio 入，text 出）、`responseConstraint` JSON-Schema 结构化输出
- `samplingMode` 参数仍 web OT only；extensions 走 legacy topK/temperature

---

## 对工作的价值（Hermes 映射）

1. **CDP 自动化路线的补充视角**：Hermes 的 google-search-cdp / chatgpt-image / Google AI Mode CDP 全是 actuation 路线（读 DOM + 模拟操作），WebMCP 的 typed-tool 契约正是同一问题的标准解。短期不动现役链路，但若目标站点开始注册 WebMCP 工具，CDP 侧可优先调 `navigator.modelContext` 省掉 DOM 解析 token
2. **免费本地推理兜底层**：Prompt API 转正 = 浏览器内零边际成本推理（无 API key 无账单）。轻量摘要/翻译/分类任务可作 zhipu 429 限流时的降级链新层（前提：硬件门槛达标）
3. **OT 坑表即排障手册**：token 静默过期 + 0.5% 用量护栏 + iframe 不继承，三条都可直接写进未来试用新 API 的操作手册

## 对现有 Skill/笔记改进建议

- **P2**：`search-fallback-chain` 可补一层"Chrome 内置 AI 降级"条目（Prompt API availability() 检测 + cloud fallback 模式），待实际验证后再入
- **P2**：跟踪项而非立即动作——WebMCP 消费端（Gemini in Chrome）成熟、或 Firefox/Safari 表态后再做 Hermes 侧 PoC

## Actionable Insights

- 判定一个 API 能否上生产的顺序：**官方 status 表 → availability() 四态检测（available/downloadable/downloading/unavailable）→ cloud fallback**。Chrome 自己的指导是"fail open"——硬件不满足时必须自己降级到云端
- 硬件门槛数据：Win10/11、macOS 13+、Linux、Chromebook Plus，22GB 可用磁盘 + >4GB VRAM GPU，覆盖率约六成——端上 AI 不是全量方案，是"新免费层"
- `chrome://on-device-internals` 是模型状态自查入口；本地试验走 `chrome://flags/#enable-webmcp-testing`（149）

## 关键风险与盲点

- ⚠️ Writer/Rewriter/Proofreader 状态来自第三方博主整理（引用官方表但未直读），标注为"社区转述，官方表为准"
- ⚠️ WebMCP 滥用面（恶意 iframe 注册危险工具）仍是 W3C 争论中，cross-origin 默认值只处理最简情形
- ⚠️ 覆盖率 "~60%" 为博主估算非官方数字
- ✅ Prompt API 转正版本号 / WebMCP 149 OT / token 过期语义：多源交叉一致（Chrome 官方文档引用 + ChromiumDev 官方 X + http.dev）

## 一页速查

> **转正（stable）**：Prompt API（web 148+ / ext 138+）、Summarizer、Translator、Language Detector（138+）——API 面是 `LanguageModel`，不是 `window.ai`
> **Developer trial**：Writer、Rewriter、Proofreader（OT 窗口已关，未转正，需 fallback）
> **新 OT**：WebMCP（149+）——`navigator.modelContext.registerTool`，仅 Gemini in Chrome 消费
> **OT 机制**：token 随 trial 过期且静默失效；0.5% 全局用量上限；iframe 不继承；Firefox 同 header / Edge 独立 / Safari 仅 flag
> **上线模式**：availability() 先行 → 稳定 API 直用 → 不稳定 API 云端兜底

## 待深入

- WebMCP 声明式 HTML 表单标注的完整语法（本次仅命令式细节）
- WebML 组对 discovery（tools 版 robots.txt）的提案进展
- extensions 侧 `LanguageModel.params()` legacy 接口与 `samplingMode` 并轨时间表

## 来源列表

1. Chrome Built-in AI in 2026: The Gemini Nano Guide — diego-rodriguez.work（2026-09-03，引用官方文档 2026-08-26 更新）
2. WebMCP in Chrome 149 — dev.to/thousand_miles_ai（含 Chrome 官方文档代码示例）
3. Origin-Trial HTTP header expert guide — http.dev（2026-09-21 更新）
4. Chrome for Developers @ X — WebMCP OT 官宣（2026-05-19, Google I/O）
5. developer.chrome.com/origintrials + docs/web-platform/origin-trials — 官方机制文档
