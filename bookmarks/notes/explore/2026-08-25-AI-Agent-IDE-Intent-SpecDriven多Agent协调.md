# AI Agent IDE：Intent Spec-Driven 多 Agent 协调

> 探索日期 2026-08-25 | 兴趣等级 L3 | 来源 2 篇深度 + 4 篇搜索摘要 | 前序笔记：2026-08-16 AI-Agent-IDE-Cursor竞品全景.md

## 摘要

Spec-Driven Development (SDD) 正在从"开发者生产力技巧"演化为"AI 原生工程的组织操作系统"。核心命题：**Intent Drift（意图漂移）是 Agent 编码的第一失败模式**——代码能跑但偏离功能本意，根因是跨会话上下文失忆，而非模型质量问题。解法是把 spec 变成 Agent 的"有状态记忆层"：结构化契约先于代码提交，每个会话显式加载。Augment Intent 把这一范式产品化为 Coordinator→Specialists→Verifier 三层多 Agent 编排，定位"IDE 之后的形态"。

## 核心发现

### 1. Intent Drift 的架构学定位：不是 Bug，是缺失的记忆层

- Agent 上下文窗口有限：session 1 的决策（数据模型/错误处理/auth 模式）到 session 3 不可见，除非显式重载
- Agent 用"统计上合理的代码"填补空白 → 编译通过但服务错对象
- **关键洞察：spec 是 Claude Code 从未拥有的有状态记忆层的架构补丁**（"a spec is the stateful memory layer Claude Code was never designed to have"）
- Spec ≠ 需求文档：需求描述业务想要什么；spec 约束 AI 被允许构建什么。"constrain"（约束）而非"guide"（引导）——从引导 AI 到治理 AI 的分水岭

### 2. 四大 SDD 工具的分层定位（2026-07 格局）

- GitHub Spec Kit：repo 原生 markdown、编辑器无关、MIT 开源，`specify` CLI 初始化，兼容 11+ Agent（Copilot/Claude Code/Cursor/Gemini CLI/Codex CLI/OpenCode）
- Kiro（AWS）：IDE+流水线级 spec 合规强制，适合"赶工期会跳步"的团队
- BMAD-METHOD：Agent 编排器，多 Agent 流水线控制
- OpenSpec：API schema 契约，防服务边界层漂移（OpenAPI 传统）

选择规则：编辑器无关选 Spec Kit / 流水线强制是瓶颈选 Kiro 或 BMAD / 漂移发生在服务边界选 OpenSpec。

### 3. Augment Intent：SDD × 多 Agent 编排的产品化

三 Agent 架构：

```
Coordinator（分析代码库，起草 spec，分解任务）
     ↓ 并行分发
Specialists ×6（实现/架构/测试等 persona，各自 git worktree 隔离）
     ↓ 汇聚
Verifier（对照 spec 验证，再交人类审查）
```

- **Living Spec**：自维护文档，代码变更时 spec 自动更新，人和 Agent 始终同源
- BYOA 支持 Claude Code/Codex/OpenCode，但最佳体验绑定 Augment Context Engine（1 亿行级代码库理解）
- Prism 模型路由器（2026-05）：按轮次选模型，质量持平最优单模 + 单任务成本降 20-30%
- 商业：$472M B 轮 / macOS-only 公测 / 复杂任务可烧 4000+ credits，多 Agent 编排会倍增消耗
- 社区声量弱：上线 4 个月无独立 HN/Reddit 实质讨论，母公司 Augment 因 2025-10 涨价有持续负面口碑

### 4. Heeki Park 实操五步法（Claude Code 内落地）

1. 打开 Claude Code **之前**写 spec——这是本体工作不是开销
2. spec 提交进 repo，成为事实源而非临时便签
3. 每个会话开头显式加载："Read specs/feature-name.md and treat it as the authoritative contract… Do not deviate"
4. 生成中歧义决策锚定 spec："这符合 spec 的行为边界吗？"
5. 需求变更时**更新 spec 而非只改代码**——过期的决策日志就是待发生的漂移

## 与现有工作的关联

- **对 kanban-workflows / subagent-driven-development skill**：Coordinator-Implementor-Verifier 三角色与现有编排模式同构，但 Intent 的差异化在"living spec 作为唯一共享上下文"——Agent 间不靠重复 prompt 传递上下文，靠 spec 文件。可借鉴到 Hermes 多猫协作：任务委派时 context 一次写透（AGENTS.md 已有此原则）本质就是手写 living spec
- **对 plan / writing-plans skill**：P0 借鉴——五步法中的"会话开头显式加载 spec + 歧义锚定"两条可直接并入 plan skill 的执行纪律；计划文件即 spec，验证步骤即 Verifier
- **对 AGENTS.md 三层工具权限模型**："constrain vs guide" 的区分与现有"允许/确认/禁止"三层同哲学：确定性边界优于自然语言劝导

## Actionable Insights

1. 【可立即用】多会话项目（如 voicebox、uclaw 改造）在 repo 根放 `specs/<feature>.md`，用五步法管理跨会话开发——消除"每次会话重新解释一遍背景"的浪费
2. 【工具试用】GitHub Spec Kit 是零成本入口（MIT + `uvx specify init`），下次起新项目时试用并评估是否沉淀为 skill
3. 【架构参考】Intent 的 Coordinator 起草 spec → 并行 Specialist → Verifier 对照 spec 验收，与"执行/评判分离"Harness 准则完全一致，可作为 kanban worker 池设计的参考实现

## 关键风险与盲点

- 来源多为厂商博客与个人研究站（traversaal.ai / rywalker.com），**Augment Intent 的质量声称无独立基准佐证**（社区验证级别：弱）
- SDD 前置成本真实存在：单 prompt 任务不值得写 spec，仅多会话特性开发 ROI 为正（官方也承认）
- Intent 公测期稳定性未知 + macOS 锁定 + credit 消耗随编排倍增——生产采用需谨慎（社区负面集中于定价）

## 一页速查

> Intent Drift = Agent 编码第一失败模式；根因是跨会话失忆而非模型质量
> Spec = 可执行契约（约束 Agent 能建什么）≠ 需求文档（描述业务要什么）
> 四工具：Spec Kit(repo无关) / Kiro(流水线强制) / BMAD(多Agent编排) / OpenSpec(服务边界)
> Augment Intent = living spec + Coordinator→Specialists(并行,worktree隔离)→Verifier，$472M，macOS公测
> 落地五步：先写spec→进repo→每会话显式加载→歧义锚定spec→改需求先改spec
> ROI边界：多会话特性开发正收益；单prompt任务别用

## 待深入

- GitHub Spec Kit 的 specify CLI 具体产物结构（spec.md/plan.md/tasks.md 三件套？）——试用后补
- BMAD-METHOD 的 Agent 编排流水线细节，与 LangGraph 编排的异同
- Living spec 自动更新机制的实现方式（diff 钩子还是 Agent 自写回？）

## 来源

1. Traversaal.ai — Spec-Driven Development: How Writing a Spec Before Code Eliminates AI Agent Intent Drift (2026-07)
2. Ry Walker Research — Augment Intent 深度评测 (2026-06)
3. Augment Code — Spec-Driven AI Code Generation With Multi-Agent Systems / Best AI Tools for SDD
4. GitHub Blog — Spec-driven development with AI: Spec Kit 开源工具包

## 相关笔记

- [2026-08-26-AgentWeave-先路由后推理.md](./2026-08-26-AgentWeave-先路由后推理.md) — 多 Agent 路由与工具调用（Agent 协调同域）
- [2026-08-23-visual-prompt-design-mode-agentic-ide.md](../../../../explore/2026-08-23-visual-prompt-design-mode-agentic-ide.md) — Agentic IDE 视觉 Prompt 设计（跨根目录，~/explore）
