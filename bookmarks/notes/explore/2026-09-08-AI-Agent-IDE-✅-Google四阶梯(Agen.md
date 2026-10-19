# AI Agent IDE ✅：Google 四阶梯（Agent Studio / Antigravity 2.0 / Managed Agents API / ADK 2.0）

> 探索日期 2026-09-08 | 兴趣等级 L3 | 来源 4 篇官方文档 | 任务来源：嗅探队列 auto-explore
> 前序笔记: [2026-09-05 Cursor 估值狂飙](2026-09-05-AI-Agent-IDE-Cursor-估值狂飙.md) | [领域知识基](../../../.hermes/skills/productivity/recurring-topic-incremental-research/references/ai-agent-ide-knowledge-bank.md)

## 摘要

Google 在 I/O '26（2026-05）发布统一 agent 开发工具链，官方以「四阶梯」（four rungs）框架自述其版图：Agent Studio（低代码）→ Managed Agents API（配置优先托管）→ Antigravity 2.0 + CLI（编码与编排）→ ADK 2.0（code-first 全控）。四阶梯刻意设计为**可叠加**（additive）——低阶梯起步不锁定，可随时晋升高阶梯；底层统一跑在 **A2A 协议**上，第一阶梯搭的 agent 可被第四阶梯当 sub-agent 调用。这是继 Cursor $60B 并购（09-05 笔记）后，本域第二个平台级玩家的完整战略摊牌，也是 Google 对「IDE 是否 AI 编码入口」的官方回答：入口开放（Claude Code/Cursor 可接入），价值收敛到 agent 基础设施层。

## 关键发现（增量，均为知识基未覆盖）

### 1. 四阶梯 = 从配置到代码的连续滑杆，而非四个孤立产品

官方原文（Addy Osmani / Alan Blount，cloud.google.com）明确「additive ladder」设计：起点低不锁死，路径可晋升。四档定位：
- **Rung 1 Agent Studio**：可视化工作台，Model Garden 选模型 + prompt 工程 + 工具接线，零代码。跑在与其余三档完全相同的运行时上。
- **Rung 2 Managed Agents API**（I/O 新发布）：「manage the mission, not the machine」——打包 instructions/skills/tools POST 上去，Google Cloud 代建代跑。配套 Interactions API 调用。卖点是 Google Cloud sandbox 安全沙箱：harness 跑在 Google 服务器，每个 agent 独立临时沙箱（ephemeral sandbox），预装 skills、MCP servers、server-side tools。
- **Rung 3 Antigravity 2.0 + CLI**：Google 编码战略收敛为单一 harness 多表面共享。2.0 是独立桌面应用，集中式 steering/定制/编排编码 agent；CLI 同 harness 同 agent 同智能，与桌面共享认证/上下文/skills/配置。企业模式：Cloud OAuth 登录 + Agent Platform Project ID，推理全部跑在自有云边界内，支持区域端点。
- **Rung 4 ADK 2.0**：engineering-first。统一图引擎，从「模型主导动态推理」到「严格确定性工作流」连续可调。协作工作流三模式：chat（全交互+手动归还）/ task（澄清交互+自动归还）/ single-turn（零交互并行+自动归还，即 agent-as-tool）。

### 2. A2A 协议是四阶梯的公共地基

「Rung 1 的 agent 可被 Rung 4 当 sub-agent 调用，整个架构在同一基础设施上无缝扩展」。这回答了知识基记录的 ACP（JetBrains+Zed）标准化竞逐：Google 押 A2A，且已把协议做成产品间互操作的实现而非纸面规范。

### 3. AGENTS.md + SKILL.md 成为 Google 官方 agent 定义原语

Managed Agents 发布博客（blog.google，DeepMind）核心示范：不写编排代码，用 markdown 文件定义 agent——`base_environment.sources` 把 `.agents/AGENTS.md` 与 `.agents/<skill>/SKILL.md` 以 inline 方式挂载进沙箱，注册为 versioned managed agent。Antigravity agent 文档（更新至 2026-08-18）确认沙箱内目录结构即 `.agents/AGENTS.md` + `.agents/skills/`。**与本机 Hermes 的 AGENTS.md + skills 体系完全同构**——Google 在 API 层复制了同一套文件约定。

### 4. Antigravity agent（Gemini API 侧）：模型已从 3.5 Flash 升至 3.7 Flash

发布时基于 Gemini 3.5 Flash，当前文档已标注 3.7 Flash，与 Antigravity IDE 同一 harness。默认工具集：code_execution / google_search / url_context，设 `environment` 参数自动启用文件系统工具；支持 custom functions 与 remote MCP servers。多模态输入 text + image（base64）。限制：不支持 temperature/top_p 等采样参数、file_search、computer_use。

### 5. 托管 agent 每任务成本锚点（行业首个官方定价表）

官方按任务类别的成本估算：研究综合类 $0.30–1.00（100K–500K in / 10K–40K out tokens）；数据处理类最高 $3.25（300K–3M in）；复杂 agentic 工作流单次交互可累积 3–5M tokens、成本至 ~$5。50–70% 输入 tokens 通常命中缓存。预览期沙箱计算（CPU/内存）免费。此表可直接用作本机 delegate_task 成本对标基线。

### 6. Hooks：沙箱内同步拦截工具执行

可在远程沙箱内同步拦截并校验 code_execution 与 filesystem 工具执行（agent-hooks 文档）。这是知识基「CIV 验证分层/确定性检查先行」的厂商级落地——Google 把 Verifier 挂进了 harness 本身。

### 7. 开放姿态反转 06-02「走向封闭」判断

官方明示「bring whatever coding agent your team prefers」：Agent CLI + ADK 允许 Claude Code 等第三方编码 agent 接入，推理跑 Google Cloud。Skills for Google products（github.com/google/skills）设计为多工具兼容。与本机 2026-06-02 笔记（Google 关闭 Gemini CLI、判断走向封闭）对照，I/O '26 是明确的战略反转证据——封闭的是 Gemini CLI 旧壳，开放的是新 agent 基础设施。

## 对工作的价值

- **AGENTS.md/SKILL.md 同构 = 经验直接迁移**：本机 uclaw/AGENTS.md 协作协议与 Hermes skills 的写法，理论上可平移为 Gemini Managed Agents 的 agent 定义。可做一次低成本实验验证。
- **成本表 = delegate 预算标尺**：单任务 $0.30–5 的托管 agent 价格带，为评估「本机子任务委派 vs 云端托管」提供行业基准。
- **四阶梯 = 平台选型地图**：快速原型（Agent Studio）→ 托管部署（Managed Agents API）→ 本机编码（Antigravity CLI）→ 全控编排（ADK 2.0），对应本机不同任务档位，A2A 保证不锁定。
- **ADK 协作三模式可借鉴**：chat/task/single-turn 的「agent 归还语义」分类，比本机现有 subtask-lifecycle 的描述更清晰，值得吸收。

## 行动建议

1. 用 Gemini API 免费层试跑一次 `antigravity-preview-05-2026`（HN 摘要→PDF 官方 quickstart），实测沙箱与成本表偏差。
2. 将本机一个现有 SKILL.md 改写为 `base_environment.sources` inline 格式验证兼容性（30 分钟内可完成）。
3. 知识基已更新本次增量（第 5 次嗅探），下次触发建议聚焦 ADK 2.0 协作工作流与 A2A/ACP 竞合进展。

## 参考来源

- What Google I/O '26 means for developing agents on Google Cloud — cloud.google.com/blog/topics/developers-practitioners/io26-news-for-agent-developers-on-google-cloud（Addy Osmani, 2026-05-20）
- Introducing Managed Agents in the Gemini API — blog.google/innovation-and-ai/technology/developers-tools/managed-agents-gemini-api（DeepMind, 2026-05-19）
- Antigravity agent | Gemini API — ai.google.dev/gemini-api/docs/antigravity-agent（更新 2026-08-18）
- Managed Agents API on Agent Platform overview — docs.cloud.google.com/gemini-enterprise-agent-platform/build/managed-agents（更新 2026-09-02）

## 相关笔记

- [2026-09-05 Cursor 估值狂飙](2026-09-05-AI-Agent-IDE-Cursor-估值狂飙.md)
- [2026-06-02 Google关闭GeminiCLI](../2026-06-02-Google关闭GeminiCLI-AI编码工具从开放走向封闭.md)
