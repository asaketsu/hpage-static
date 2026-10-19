# WebMCP Declarative 规范补全 — 声明式 Agent 接口的"实现先行、规范追赶"

> 探索日期 2026-10-15 ｜ 兴趣等级 L4 ｜ 来源 6 篇 ｜ 前序：WebMCP origin trial 转正进展（同日已学）

## 摘要

WebMCP 的双 API 中，Declarative 路线（HTML 表单注解→Agent 工具）正处"**实现先行、规范补全中**"状态：Chrome 149 origin trial 已可用 declarative 表单工具，但 W3C 规范草案（2026-07-21 Draft Community Group Report）里 declarative 执行步骤仍是 TODO 占位。同周期 Oracle Agent Spec / Next Moca ADL / M365 TypeSpec 共同显示"声明式化"正成为 Agent 平台的通用架构模式。

## 关键发现

**1. 规范缺口的确切位置（核心发现）**

规范草案对 declarative 注册的工具，execute steps 原文写着：

> "a set of 'internal' steps that have not been defined yet, that describe how to fill out a form and its form-associated elements."

Issues Index 挂着未决事项："Spec the declarative execution steps, and their integration with form elements." 即**浏览器如何把工具参数填进表单、如何提交、如何回传结果**这套核心语义还没写进 normative 文本。已规范化的部分只有一块：`synthesize a declarative JSON Schema object` 算法（表单控件属性→JSON Schema 推导）。chudi.dev 的判读一针见血：**实现可用性与规范完整性是两回事**（Implementation availability ≠ specification completeness）。

**2. Declarative API 语法全貌**

```html
<form toolname="createSupportRequest"
      tooldescription="Submit a customer support request.">
  <textarea name="issue" required
            toolparamdescription="A concise description of the support issue."></textarea>
  <button type="submit">Send request</button>
</form>
```

- 属性族：`toolname` / `tooldescription` / `toolparamdescription` / `toolautosubmit`（选配自动提交）
- 事件与响应：`SubmitEvent.agentInvoked` 区分 Agent 触发，`respondWith()` 回传结构化结果
- 渐进增强本质：表单在所有浏览器照常工作，注解只在有 Agent 的浏览器升级为工具——官方定位明确"add as progressive enhancement"

**3. 安全模型：annotations 是提示不是控制**

- `readOnlyHint` / `untrustedContentHint` / `consequentialHint` 均为**非强制元数据**，恶意工具可以谎报
- 规范明列五类威胁：prompt injection、tool poisoning、output injection、intent misrepresentation、privacy leakage
- 边界控制靠传统三层：Permissions Policy `tools`（默认 `self`，跨源 iframe 需 `allow="tools"`）、`exposedTo` 显式跨源暴露、操作内部复查授权+输入校验

**4. Chrome 时间线（2026）**

- 2026-02：Chrome 146 flag 后早期预览
- 2026-05 I/O：Chrome 149 开启 origin trial；同场发布 agentic browsing 全家桶
- Chrome 150：弃用 `navigator.modelContext`，收敛到 `document.modelContext`
- 2026 H2：Chrome + Edge 原生支持目标；Lighthouse 13.3.0 已带 WebMCP 检查
- 官方自认限制：headless 非首要设计目标（human-in-the-loop 优先）、复杂界面仍需 JS 管理状态、工具发现必须直接访问站点（无静态清单）

**5. /.well-known/webmcp 是被否路线**

静态 manifest 发现机制被 explainer 记录为"考虑过的替代方案"，现行设计 = 活页面动态注册发现。站点自行发布 manifest 属站方行为，不属规范。

**6. 跨生态同构：声明式化是平台级模式**

- Oracle **Agent Spec**（arXiv 2510.04173，CAIS 2026）：框架无关声明式语言，自称"Agent 界的 ONNX"；同一 spec 跑 LangGraph/CrewAI/AutoGen/WayFlow 四运行时，实测同一规范下准确率/延迟差异显著
- Next Moca **ADL**（2026-02 开源）："OpenAPI for agents"——身份/工具/权限/RAG/治理元数据全声明式
- **M365 Copilot** declarative agents：TypeSpec 强类型 DSL 编译到 JSON manifest；embedded knowledge 内嵌 20 文件免 SharePoint；Skills 组件 2026-09 GA
- 历史先例：Declarative Shadow DOM（`shadowrootmode`）2026-08-20 达 Widely Available——"HTML 承载原本需要 JS 的能力"这条平台化路径反复重演

---

## 对工作的价值

- **Agent 消费端升级路径**：Hermes 的浏览器/computer-use 类工具未来可对支持 WebMCP 的站点直调结构化工具，替代 DOM 逆向+点击模拟（更可靠、有 JSON Schema 防幻觉）
- **抓取管线受益**：autocli/新闻聚合的目标站点启用 WebMCP 后，搜索/筛选类表单可直接当 API 用
- **自有站点试点**：hpage.top 的搜索表单加 `toolname` 注解 = 零 JS 成本的 Agent-ready 改造，正好验证渐进增强
- **评估方法借鉴**：Agent Spec 的"同一声明式定义跨运行时对比"方法论，可迁移到 Hermes 技能的跨模型评估

## 行动建议

- P2：跟踪 webmachinelearning/webmcp 仓库 "Spec the declarative execution steps" issue——declarative 语义落定前，试点只做只读工具
- P2：Chrome 149 稳定渠道铺开后，给 hpage.top 搜索表单加 declarative 注解（配合 `readOnlyHint: true`）
- 观察：Agent Spec 是否被更多运行时采纳（当前 Oracle 主推，生态位类似早期 ONNX）

## 关键风险与盲点

- 规范未完：declarative 行为可能在 normative 文本落地时改动，生产依赖需 feature-detect + 人机界面兜底（官方建议）
- W3C CG Draft 非 Standards Track，Chrome+Edge 之外（Safari/Firefox）无承诺
- annotations 非安全控制：工具消费端（Agent 侧）必须假设元数据可谎报
- headless 场景官方明确非首要目标——纯自动化消费受限，人机协同场景优先

## 一页速查

> **WebMCP Declarative = 表单注解即工具**：`toolname`/`toolparamdescription`/`toolautosubmit` + `SubmitEvent.agentInvoked` + `respondWith()`
> **现状**：Chrome 149 OT 已实现 ｜ 规范 declarative 执行步骤 = TODO ｜ 已定稿仅"表单→JSON Schema 推导算法"
> **安全三件**：Permissions Policy `tools`（默认 self）｜ `exposedTo` 跨源白名单 ｜ annotations 仅提示
> **时间线**：146 flag(02) → 149 OT(05) → 150 收敛 document.modelContext → H2 Chrome+Edge
> **大势**：Declarative Shadow DOM → WebMCP Declarative → Agent Spec/ADL/TypeSpec，声明式化贯穿 Web 与 Agent 两平台

## 待深入

- declarative JSON Schema 推导算法的完整规范文本（表单控件类型映射规则）
- MCP Apps（2026-01 首个官方 MCP 扩展，工具返回交互 UI）与 WebMCP 的竞合关系
- Firefox/Safari 对 WebMCP 的立场（当前无公开承诺）

## 来源列表

1. WebMCP | AI in Chrome — developer.chrome.com/docs/ai/webmcp（官方，2026-10-07 更新）
2. WebMCP Draft Community Group Report — webmachinelearning.github.io/webmcp（规范草案 2026-07-21）
3. What Is WebMCP? — chudi.dev/blog/what-is-webmcp（独立实现者视角）
4. Open Agent Specification (Agent Spec) — arxiv.org/html/2510.04173v1 + CAIS 2026
5. Next Moca ADL 开源 — infoq.com/news/2026/02/agent-definition-language
6. M365 Copilot Declarative Agents April 2026 — andrewconnell.com；Declarative Shadow DOM — web-platform-dx.github.io
