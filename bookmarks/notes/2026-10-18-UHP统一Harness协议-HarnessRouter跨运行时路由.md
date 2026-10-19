# UHP 统一 Harness 协议：HarnessRouter 让 Codex/Claude Code/Hermes 变成可路由的执行层

`#Agent` `#Harness` `#UHP` `#协议` `#路由` `#Hermes` `#Codex` `#架构`

> 原文：Akshay Pachaar (@akshay_pachaar, 29万粉, LightningAI 前AI工程师) — X Article
> 链接：https://x.com/akshay_pachaar/status/2100888166219886818
> 项目：github.com/HarnessRouter/harnessrouter (Apache 2.0)
> 评分：⭐⭐⭐⭐⭐（4.7/5）— Agent 基础设施标准化的重要一步，且 Hermes 是一等公民

## 归纳总结

**一句话：模型路由选"谁推理"，harness 路由选"谁干活"——UHP 把后者标准化了。**

当产品集成一个 agent harness（如 Codex CLI）后，后端开始依赖它的任务格式、事件流、会话模型和文件系统行为。再加第二个 harness 不是改配置，而是加一整套新 runtime。UHP（Unified Harness Protocol）用一份仿 OpenAI Responses API 的 HTTP 契约统一了任务生命周期（创建/进度/会话/文件/取消/错误），HarnessRouter 是它的自托管开源实现，内置 11 个 harness——**包括 Hermes**。

核心洞察：模型调用 ≠ 完整任务。agent harness 包含控制循环（调工具/管文件/定权限/判完成），换 harness 换的是整个"操作系统"，不是换一个推理端点。

## 内容整理：UHP 协议与 HarnessRouter 架构

### 两层路由的本质区别

| 维度 | 模型路由（已有共识） | Harness 路由（UHP 新增） |
|------|---------------------|-------------------------|
| 选择对象 | 推理端点（哪个模型） | agent runtime（哪套执行系统） |
| 不变量 | agent loop 不变 | 产品任务流不变 |
| 变化量 | 价格/延迟/质量 | 工具/技能/工作区/权限/事件流 |
| 配置形式 | model 参数 | metadata.harness_id |
| 典型场景 | 降级兜底/成本优化 | 客户指定 provider/配额耗尽/A-B 评测 |

### UHP 协议核心契约（版本 2026-09-12）

- **API 形状**：仿 OpenAI Responses API，`POST /v1/responses` 启动任务
- **请求字段**：任务输入 + model + harness_id + 可选执行限额
- **概念层级**：Response(单次任务) → Session(共享会话状态+工作目录) → Configured Harness(基座+模型+指令+技能+工具+MCP+限额)
- **实时事件**：SSE 流，每事件带 type + 序号（有序处理）
- **续接**：`previous_response_id` 续会话（同 harness）
- **跨 harness 交接**：不是恢复会话，而是新会话+上下文摘要+文件传递（"把任务交给另一个开发者"）
- **文件**：小文件内联请求，大文件走上传；产物成为 artifact 可列出下载
- **交付物**：书面规范 + OpenAPI 3.1 schema + JSON Schema + 可运行一致性测试

### HarnessRouter 部署架构（自托管）

- **三服务 Docker**：Console（浏览器 UI，唯一对外端口）+ Gateway（UHP API + harness 配置）+ Runner（在 session 工作区内启动 harness 进程）
- **数据卷**：/data 存数据库 + 已装 harness CLI + provider 集成 + session 文件 + 工作区
- **11 个内置 harness**：Codex / Claude Code / **Hermes** / DeepSeek Harness / Gemini CLI / OpenCode / Qwen Code / Cline / Goose 等
- **自定义 harness** = 基座 harness + 默认模型 + 指令 + 工具 + 技能 + MCP servers → 生成 Harness ID
- **资源要求**：Docker + ~4GB 磁盘 + 一个模型 provider API key

### 安全与隔离边界（诚实披露）

- Session 用独立 OS 用户 + 工作区，但**非容器隔离**（Runner 需要建用户权限）
- Provider 凭证必须在 agent 工具读不到的环境
- 应用 API key 禁止进浏览器代码
- loopback 之外部署需 TLS + UHP 安全规范

## 关联分析

**与已有笔记的关系**：
- [[2026-06-15-Agentic-Engineering三层体系-Loop-Harness-FDE.md]] 的三层体系（Loop→Harness→FDE）中，UHP 标准化的是 Harness 层的对外契约——那篇讲"层是什么"，这篇讲"层间接口怎么统一"
- 我的 `model-fallback-chain` skill 是模型路由层的实践；UHP 是它的上一层——两层可叠加（UHP 请求里 model 和 harness_id 各自独立选）
- yibie/rari 的 Harness 生态系列关注"harness 是什么/为什么重要"，本文补上"多 harness 共存的工程解法"

**与我们系统的直接关联**：
1. **Hermes 是 11 个内置 harness 之一**——我们日常跑的 jbot/ubot/abot 体系在 UHP 生态里是可被路由的执行单元，不是旁路
2. **LanGPT 正是"产品绑死单 harness"的活案例**：现在绑 codex CLI，昨天升级断链事故=单 runtime 依赖的脆弱性实证。UHP 思路（统一任务接口+harness 可换）是 LanGPT 后端演进的参考架构
3. **多机体系可对标**：jbot/ubot/abot 三机分工是"人肉 harness 路由"，UHP 的 session 交接规范（摘要+文件+新会话）与我们 exchange-protocol 的经验池交接同构

## 趋势判断

1. **Harness 层正在重演"模型层标准化"的历史**：2023-24 年把模型 API 统一到 OpenAI 兼容格式（LiteLLM/OpenRouter 胜出），2026 年同样的整合压力落在 harness 层——UHP 仿 Responses API 的选择明显在复刻这条路径
2. **协议窗口期已开但未定**：UHP 版本 2026-09-12 很新，MCP 已成事实标准的先例说明：谁先拿到 harness 集成生态位（Codex/Claude Code/Hermes 全覆盖），谁就是候选人
3. **评测是隐藏刚需**：同任务跑两个 harness 对比成本/延迟/工具使用——这是选型刚需，我们现在 jbot(智谱) vs codex 的能力对比完全没有标准化口径，UHP 的一致性测试是现成方案
4. **风险**：单作者项目（Apache 2.0 但社区早期），规范会不会被 Anthropic/OpenAI 官方协议挤压待观察

## 指南分析

**适用场景判断**：
- ✅ 产品要在 UI 里给用户提供 harness 选择（客户有 OpenAI 也有 Anthropic）
- ✅ 同任务跨 harness A/B 评测（选型/验收）
- ✅ provider 配额/故障时切换 runtime 兜底
- ❌ 单人单机工作流（直接用 harness 本体更省）
- ❌ 需要 harness 会话无缝续接（UHP 明确不支持跨 harness resume，只能摘要交接）

**上手路径**（本地体验约 30 分钟）：
1. Docker 起 HarnessRouter（127.0.0.1 绑定 Console）
2. Integrations 加模型 provider API key（与 Console 密码/应用 key 三者独立）
3. Agent harnesses 面板看 11 个内置项，选 Hermes 直接建任务
4. /keys 生成应用 API key → 后端用 Responses 兼容端点发任务
5. 换 runtime 只改 `metadata.harness_id`

## 查询拓展

- UHP 规范原文与 schema：github.com/HarnessRouter/harnessrouter（含 conformance tests）
- OpenAI Responses API 设计（UHP 的形状来源）：platform.openai.com Responses 文档
- 横向对比：代理层标准化先例 LiteLLM/OpenRouter 的胜出路径
- MCP（Model Context Protocol）——工具层标准化如何与 harness 层标准化组合
- Claude Code / Codex 的 headless 模式文档（HarnessRouter 底层就是包它们）

## 拓展应用推荐

1. **给 LanGPT 后端画 UHP 演进线**（中优先级）：手机端不感知 harness，任务发到 221 主机的 UHP 端点，codex/Hermes/其他 runtime 可配置切换——昨天的单 runtime 断链事故在此架构下自动免疫
2. **jbot vs codex 的标准化对比评测**（高优先级，低成本）：用 UHP 的 conformance 思路给两个 runtime 跑同一组任务（翻译/代码修/文档摘要），产出成本/延迟/质量三线对比表——为"哪个任务交给谁"提供数据底座
3. **经验池跨机交接借鉴**（已有 exchange-protocol 的增强）：UHP 的跨 harness 交接规范（摘要+文件+新会话）可作为 jbot↔abot 任务移交的格式参考
4. **观察清单**：star HarnessRouter 仓库，跟踪 spec 版本演进；若 Anthropic/OpenAI 官方出同类协议，第一时间对比

---

→ 相关：2026-06-15-Agentic-Engineering三层体系-Loop-Harness-FDE.md
→ 相关：2026-05-30-SQLite足以支撑持久化工作流-Agent时代的极简基础设施.md
