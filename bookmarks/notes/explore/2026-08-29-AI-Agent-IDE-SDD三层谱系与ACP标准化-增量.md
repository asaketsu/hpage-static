# AI Agent IDE：SDD 三层谱系、JetBrains Air 转向与 ACP 标准化（2026-08-29 增量更新）

> 嗅探学习 | 2026-08-29 | 来源：HN Algolia + TinyFish Search（Tavily/web_search 432 降级）+ curl 直取
> 前序笔记：[2026-08-28-AI-Agent-IDE-Intent-spec-driven多Agent协调.md](2026-08-28-AI-Agent-IDE-Intent-spec-driven多Agent协调.md) / [2026-08-25-AI-Agent-IDE-Intent-SpecDriven多Agent协调.md](2026-08-25-AI-Agent-IDE-Intent-SpecDriven多Agent协调.md)
> 本主题为第 3 次触发，本次为 1 天后的增量追踪

## 摘要

1 天后的增量追踪。领域无颠覆性范式转移，但出现 5 条前序笔记完全未覆盖的显著进展，核心是**第三方权威（Thoughtworks/Fowler）对 SDD 给出了可操作的分层判据**，直接证伪了前序笔记基于厂商博客的判断：

- **SDD 三级谱系**：Spec-first → Spec-anchored → Spec-as-source。Tessl（私有 beta）是唯一明确追求 spec-anchored 并探索 spec-as-source 的工具
- **独立第三方证据链**：前序两篇笔记的证据全部来自厂商博客 + 个人研究站，本次首次拿到 Thoughtworks Distinguished Engineer 的系统评估
- **JetBrains 战略转向**：2025-12-22 起 Fleet 停下载，转向 Air agentic IDE，官方定义新工作流为"开发者不写代码，只引导 agent 并审查其输出"
- **ACP 标准化**：JetBrains + Zed 联合发布 ACP Agent Registry，"像 LSP 之于语言，之于 AI coding agent"
- **SDD 生态工具链成型**：验证类（Rudder/SpecOps）、成本类（Cost.dev）、安全类（Cordon/Sieve）、记忆类（Project Brain）—— 前序笔记只覆盖 spec 工具本体，未覆盖治理外围

## 关键发现（增量）

### 1. SDD 三层谱系 —— 前序笔记完全缺失的判据框架

Thoughtworks Birgitta Böckeler《Understanding Spec-Driven-Development: Kiro, spec-kit, and Tessl》（2025-10-15）提出当前最清晰的分类：

**Spec-first**：spec 先于代码写好，用于当前任务
**Spec-anchored**：任务完成后 spec 保留，持续用于该功能的演进与维护
**Spec-as-source**：spec 成为唯一主源文件，人只编辑 spec、永不触碰代码

关键结论：**所有 SDD 工具都是 spec-first，但并非都追求 spec-anchored 或 spec-as-source，且多数工具对 spec 的长期维护策略含糊甚至完全空白。**

### 2. 对前序笔记的证伪与纠正（P0）

前序 08-25 笔记称 GitHub Spec Kit 是"repo 原生 markdown、spec 提交进 repo 成为事实源"。Fowler 的独立评估指出：**spec-kit 实际仍是 spec-first only，不是 spec-anchored**。证据是 spec-kit 为每个 spec 创建一条 branch —— 说明其视 spec 生命周期为「单次变更请求」而非「整个功能」。spec-kit 官方博客确实宣称要"living, executable artifacts"，但工程实现与该宣称不符。

同理 Kiro：Fowler 观察到的所有用例都是 spec-first（单个任务或 user story），未见到 spec-anchored 用法。

**这条修正很重要**：前序笔记把"living spec"当作 SDD 的已实现能力来写，实际它是 spec-kit 的宣称而非其行为。

### 3. Spec ≠ Memory bank —— 概念分层澄清

Fowler 明确区分两类 artifact（前序笔记混为一谈）：

**Memory bank**（rules 文件、产品/代码库高层描述）：跨所有 AI 编码会话生效，整个代码库级
**Spec**：仅对相关创建/变更该功能的任务生效，任务级

工具命名映射：Kiro 叫 **steering**（默认三文件 product.md / structure.md / tech.md）；Spec Kit 叫 **constitution**（不可变高层原则，本质是强力 rules 文件）；Tessl 无此概念。

对本机价值：AGENTS.md / USER.md / MEMORY.md 本质就是 memory bank 层，而 plan/writing-plans 的产出是 spec 层。前序笔记未做此区分，导致"把 spec 当记忆层"的表述在架构上不准确。

### 4. JetBrains 退出 IDE 军备赛，押注 agentic 工作流（新增事件）

JetBrains 官方宣布（devclass 2025-12-09 报道）：**Fleet 自 2025-12-22 起停止下载**，公司转向新 agentic 开发产品 **Air**（当前 public preview，基于 Fleet 平台）。

官方原话（Prigara & Stukalov）：
- 停止原因："两条 IDE 家族线造成混淆并稀释了公司聚焦"，"既无法用 Fleet 替代 IntelliJ IDEA，也无法把它收窄成清晰差异化的细分领域"
- Air 的工作流定义："开发者不写代码本身。他们引导 agent 并审查其输出"

意义：Fleet 2021 年立项、从未走出 public preview，是"从零架构、轻量、远程优先"路线的失败实验；JetBrains 用 4 年验证了自建 IDE 架构无法对抗 VS Code 生态，转而把筹码押在 agentic 工作流层而非编辑器层。这是对"IDE 是 AI 编码的入口"这一定位的产业级否定。

### 5. ACP：Agent Client Protocol 标准化（新增协议）

JetBrains + Zed 联合发布 **ACP Agent Registry**（beta），官方定位："像 Language Server Protocol，但针对 AI coding agent"。

核心主张：任意 AI coding agent 可在任意支持 ACP 的编辑器中运行，实现一次、多端复用，无 vendor lock-in。Registry 提供发现 + 一键安装，替代手动配置。首批覆盖 Gemini CLI、Claude Code、Auggie、OpenCode、Copilot。

Mistral AI 工程师背书（已用于 Mistral Vibe 集成）："从底层设计良好、社区驱动、快速演进……不仅简化集成，也契合我们对开放灵活工具的聚焦。"

**与前序笔记的关系**：前序笔记的"隔离三件套"解决的是单厂商内的多 Agent 并行；ACP 解决的是跨厂商的 agent-editor 互操作。两者层级不同，不冲突。

### 6. SDD 治理外围工具链（前序笔记完全空白）

前序笔记只覆盖 spec 工具本体（Spec Kit / Kiro / BMAD / OpenSpec），完全未触及治理生态。2026-06 至 08 出现的四类新工具：

**验证类**
- RudderCode/Rudder（Apache-2.0，2026-06-05 创建，2026-08-19 最后推送，22★）：把单元测试"反用"为度量工具 —— 衡量 coding agent 在 spec 边界外即兴发挥（improvise）了多少。与 08-28 笔记的"验证分层铁律"互补：前者是运行时验证，Rudder 是事后审计
- SpecOps（dotlabshq/spec-ops）：SDD 扩展到 Infrastructure as Code 领域

**成本类**
- Cost.dev（YC W21，HN 48pts）：让 agent 成本感知、降低调用成本
- 支撑 08-28 笔记的模型路由经济性论证，但提供工具层实现

**安全类**
- Cordon（marras0914/cordon）：MCP tool calls 的安全网关，支持 HITL 审批
- Sieve：扫描 Cursor / Claude chat history 中的泄露 API keys（HN 18pts）

**记忆类**
- Project Brain：跨 Claude Code / Windsurf / Cursor 的持久化 second brain（对应 Fowler 的 memory bank 层）

### 7. "Your role isn't just to steer. It's to verify" —— 人机分工再定位

GitHub spec-kit 官方博文中的这句被 Fowler 引用，是当前最精炼的人机分工表述：**工程师的角色不是引导（steer），而是验证（verify）**，且在每个阶段都要 reflect and refine。

这与 08-28 笔记的 CIV 模式（Coordinator-Implementor-Verifier）方向一致，但措辞更激进：不是"人审查 Verifier 的输出"，而是"人就是那层验证"。

## 对工作的价值（增量）

- **P0 —— 修正本机 plan/writing-plans 的定位**：按 Fowler 框架，plan 产出是 spec 层，AGENTS.md/MEMORY.md 是 memory bank 层。08-28 笔记把二者混谈。建议在本机 skill 文档中显式补一句分层说明，避免后续再把"计划文件"误当"记忆层"使用
- **P0 —— Tessl 值得列入观察**：它是三工具中唯一 spec-anchored + 探索 spec-as-source 的，且 spec 文件头部带 `// GENERATED FROM SPEC - DO NOT EDIT` 标记、当前 1:1 映射 spec↔code 文件。对 Hermes 的 skill/plan 体系是"约束即代码"的最激进参照（但仍在 private beta，不宜立即采用）
- **P1 —— Rudder 的"单元测试反用为即兴度量"可直接迁移**：本机 verification-gate skill 是运行时门禁，缺事后审计维度。Rudder 的思路（用既有测试集检测 agent 是否在 spec 外自由发挥）几乎零成本可借鉴
- **P1 —— ACP 标准化降低工具锁定的战略价值**：本机 kanban-workflows / subagent-driven-development 目前绑定特定 agent CLI。ACP 路线若成，可让 Hermes 编排层与具体 coding agent 解耦
- **P2 —— 安全外围工具**：Cordon（MCP tool calls + HITL）与 AGENTS.md 三层工具权限模型（允许/确认/禁止）同构，可评估是否作为执行层实现

## 行动建议（增量）

- 【P0，半小时】在 plan / writing-plans skill 顶部补一条：产出属 spec 层（任务级），与 AGENTS.md/MEMORY.md 的 memory bank 层（代码库级）分离
- 【P0，1 天】读 Rudder README 全文，评估"测试反用为 agent 即兴度审计"是否可接入 verification-gate 作为事后审计子流程
- 【P1，观察】关注 Tessl public alpha 发布 + Air 退出 preview 的节点，两者分别代表 spec-as-source 与 agentic-first IDE 的产业验证
- 【P2，顺手】把 ACP Agent Registry 作为 Hermes 多 agent CLI 编排解耦的候选方案记入 agent-orchestration-pattern 的参考

## 关键风险与盲点

- Fowler 评估基于 2025-09 的工具版本（文章 2025-10-15 发布），距今 10 个月，工具演进极快，spec-kit/Kiro 是否已转向 spec-anchored 需重新验证
- Tessl 仍在 private beta，spec-as-source 的 1:1 映射被其团队自己视为"未来方向"而非当前承诺
- JetBrains Air 仍 public preview，且 Fleet 组件复用不等于 Air 会成功 —— Fleet 本身就是"从零架构"路线失败的实验
- Rudder 仅 22★，成熟度极低，其"即兴度"度量方法学未经验证
- ACP Registry 是 beta；与已有 MCP 协议的边界关系官方未清晰说明，可能重复造轮子
- 本次搜索降级至 HN Algolia + TinyFish，未覆盖中文技术社区与企业博客，增量可能不完整

## 相关笔记

- [2026-08-28-AI-Agent-IDE-Intent-spec-driven多Agent协调.md](2026-08-28-AI-Agent-IDE-Intent-spec-driven多Agent协调.md) —— 直接前序（CIV 模式 / VeriMAP / 五大失败模式）
- [2026-08-25-AI-Agent-IDE-Intent-SpecDriven多Agent协调.md](2026-08-25-AI-Agent-IDE-Intent-SpecDriven多Agent协调.md) —— 首版（Intent Drift / 四工具矩阵 / 五步法）
- [2026-08-27-EVOMAL-自进化编码Agent的自我投毒漏洞与安全边界迁移.md](2026-08-27-EVOMAL-自进化编码Agent的自我投毒漏洞与安全边界迁移.md) —— coding agent 安全（Cordon/Sieve 同域）
- [2026-08-28-SARA-工具输出变命令的动作诱导与运行时授权分离.md](2026-08-28-SARA-工具输出变命令的动作诱导与运行时授权分离.md) —— HITL 授权（Cordon 同域）

## 参考来源（增量，全部为本轮实时获取）

1. Martin Fowler / Birgitta Böckeler（Thoughtworks）— *Understanding Spec-Driven-Development: Kiro, spec-kit, and Tessl*（2025-10-15）：curl 直取全文 20KB
2. devclass — *JetBrains abandons Fleet IDE, pins hopes on forthcoming Air agentic development tool*（2025-12-09）：curl 直取
3. JetBrains AI Blog — *ACP Agent Registry Is Live: Find and Connect AI Coding Agents in Your JetBrains IDE*（2026-01）：curl 直取
4. GitHub API — RudderCode/Rudder 仓库元数据 + README：22★ / Apache-2.0 / 2026-06-05 创建 / 2026-08-19 推送
5. TinyFish Search — Agentic IDE 2026 榜单（datacamp / paralect / nimbalyst / marktechpost）：仅作格局佐证，未精读
6. HN Algolia — SDD / agentic IDE / coding agent 三条查询共 36 条去重结果（SpecOps / Cost.dev / Cordon / Sieve / Project Brain / DeepSWE 来源）
