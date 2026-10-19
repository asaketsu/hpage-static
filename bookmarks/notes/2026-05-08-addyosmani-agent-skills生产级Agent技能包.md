# Addy Osmani agent-skills：生产级 AI 编码 Agent 技能包

- 📅 2026-05-08
- ⭐ 4.5/5 — 目前最成熟的 AI Agent 编码 skill 体系，工程实践深度远超同类项目，值得深度吸收
- 🏷️ #Agent技能 #AI编程 #Harness工程 #Skill设计 #Google工程实践
- 📇 来源：GitHub - addyosmani/agent-skills
- 🔗 https://github.com/addyosmani/agent-skills

关联：[Harness-Engineering-载具设计研究报告](Harness-Engineering-载具设计研究报告.md) — Addy Osmani 是 Harness Engineering 概念的提出者，本仓库是其方法论的产品化落地
关联：[2026-04-09-SKILL-md-ai-agent-skills](2026-04-09-SKILL-md-ai-agent-skills.md) — SKILL.md 格式设计的源头之一
关联：[2026-05-08-ai-agent-protocol-wars-a2a-mcp](explore/2026-05-08-ai-agent-protocol-wars-a2a-mcp.md) — Skill 是 Agent 协议栈中的应用层

## 摘要

Addy Osmani（Google Chrome 团队）开源的 **agent-skills** 是一套面向 AI 编码 Agent 的生产级技能包，包含 20 个结构化 Skill、7 个生命周期命令、3 个专家 Persona。核心理念是"AI Agent 默认走最短路径，Skill 强制其走工程最佳实践路径"。项目已获得 32.9k Star、3.8k Fork，支持 Claude Code / Gemini CLI / Cursor / Windsurf / OpenCode / GitHub Copilot / Codex 等主流编码 Agent。

## 核心内容

### 1. 架构设计：六阶段开发生命周期

```
DEFINE → PLAN → BUILD → VERIFY → REVIEW → SHIP
/spec    /plan   /build   /test   /review   /ship
```

每个阶段有对应的 Skill 自动激活，覆盖从需求定义到上线部署的完整链路。

### 2. 20 个 Skill 分类

| 阶段 | Skill | 核心价值 |
|------|-------|----------|
| **Define** | idea-refine, spec-driven-development | 发散→收敛思维 + PRD 先行 |
| **Plan** | planning-and-task-breakdown | 原子化任务拆解 + 依赖排序 |
| **Build** | incremental-implementation, TDD, context-engineering, source-driven, frontend-ui, api-design | 垂直切片 + 测试先行 + 上下文工程 |
| **Verify** | browser-testing-with-devtools, debugging-and-error-recovery | DevTools 运行时验证 + 五步排障 |
| **Review** | code-review, code-simplification, security, performance | 五轴审查 + Chesterton's Fence + OWASP |
| **Ship** | git-workflow, CI/CD, deprecation, documentation, shipping | Trunk-based + 特性标记 + 分阶段上线 |

### 3. Skill 解剖结构

```
SKILL.md
├── Frontmatter（name + description + trigger）
├── Overview（做什么）
├── When to Use（触发条件）
├── Process（步骤化工作流）
├── Rationalizations（借口反驳表 — 关键创新）
├── Red Flags（异常信号）
└── Verification（证据要求 — 必须通过才算完成）
```

**三个关键设计决策**：
- **Process, not prose** — Skill 是工作流不是参考文档，有步骤、检查点、退出条件
- **Anti-rationalization** — 每个 Skill 包含"Agent 常见借口反驳表"（如"我稍后加测试"→ 反驳理由），这是独创的
- **Verification non-negotiable** — "看起来对了"不算通过，必须测试通过 + 构建输出 + 运行时数据

### 4. Agent Persona（专家角色）

| Persona | 角色 | 审查标准 |
|---------|------|----------|
| code-reviewer | Senior Staff Engineer | "Staff 级工程师会批准吗？" |
| test-engineer | QA Specialist | 覆盖率 + Prove-It 模式 |
| security-auditor | Security Engineer | 威胁建模 + OWASP 评估 |

### 5. Google 工程文化基因

Skill 中嵌入了大量 Google 工程实践：
- **Hyrum's Law**（API 设计）— 有用户依赖的接口行为就是契约
- **Beyonce Rule**（测试）— 如果没测试覆盖，那就是不存在的功能
- **Change Sizing ~100 lines**（代码审查）— 单次变更控制在 100 行内
- **Trunk-based Development**（Git）— 主干开发，特性标记替代长分支
- **Shift Left**（CI/CD）— 尽早发现问题
- **Code as Liability**（废弃管理）— 代码是负债，能删就删

### 6. 项目热度与生态

- **32.9k Star / 3.8k Fork / 162 Commits** — 2026 年最火的 Agent Skill 项目
- 支持 8+ 主流编码 Agent（Claude Code、Gemini CLI、Cursor、Windsurf、OpenCode、GitHub Copilot、Kiro、Codex）
- 有完整的 CI 验证 + Plugin 格式支持

## 🔍 借鉴点

- **Anti-rationalization 表** → Hermes 的 skill 可以加入"借口反驳"板块。例如 `note-dual-format` skill 中加入："我这次不用 markdown 库转换" → 反驳：上下文压缩后格式记忆会丢失，上次就是这样翻车的
- **Verification > Opinion** → 我们的 `requesting-code-review` skill 已有类似思路（静态扫描 + 测试 + exit_code=0），可以进一步强化为"必须提供证据链"
- **Persona 角色** → 我们的 Dev/OPM/Content/Data Meow 团队角色就是 Persona 思路，但缺少"审查标准"定义。可以借鉴"Staff 级工程师会批准吗？"这种可度量的标准
- **六阶段生命周期** → Hermes 的 `/init → /status → /plan → /mention → /diff → /review → /compact → /resume` 流程可以与之对齐，补齐 Define 和 Ship 阶段
- **跨 Agent 兼容** → 一个 Skill 包同时支持 Claude Code / Gemini CLI / Cursor 等，这暗示 Skill 的标准化趋势正在加速

## 🔗 关联性

- 关联已有笔记：[Harness-Engineering-载具设计研究报告](Harness-Engineering-载具设计研究报告.md) — Addy Osmani 的 Harness Engineering 理论的产品化实现，agent-skills 就是"载具"的具体形态
- 关联已有笔记：[2026-04-09-SKILL-md-ai-agent-skills](2026-04-09-SKILL-md-ai-agent-skills.md) — SKILL.md 格式分析的原始参考，agent-skills 的格式是当前最成熟的实践
- 关联已有 skill：`requesting-code-review` — 与 agent-skills 的 code-review-and-quality 思路一致，可对比优化
- 关联已有 skill：`writing-plans` — 与 planning-and-task-breakdown 互补，可以吸收原子化任务拆解方法
- 关联已有 skill：`hermes-agent-skill-authoring` — Hermes 的 Skill 编写规范可以参考 agent-skills 的 Frontmatter + Anti-rationalization 结构
- 关联已有笔记：[2026-05-08-企业AI转型三步法-知识库技能化智能体](2026-05-08-企业AI转型三步法-知识库技能化智能体.md) — agent-skills 是"技能化"阶段的典型案例——把工程经验编码为可复用的 Skill

## 💡 启发

- **Anti-rationalization 是杀手级特性**。AI Agent 最大的问题不是能力不足，是偷懒——跳过测试、跳过审查、跳过文档。传统 skill 只告诉 Agent "应该做什么"，agent-skills 的创新是同时告诉 Agent "你不想做的时候为什么也必须做"。这个思路可以直接移植到 Hermes 的所有 skill 中
- **Skill 标准化是必然趋势**。一个 Skill 包同时支持 8 种 Agent 工具，说明 Skill 格式正在走向标准化（类似 npm 包对 Node 生态的意义）。Hermes 的 Skill 格式应该主动对齐这个趋势
- **"Process, not prose"原则**。好的 Skill 不是知识库文章，而是可执行的工作流。Hermes 的很多 skill 偏向"参考文档"风格，可以重构为"步骤→检查点→退出条件"的结构
- **与我们的 Harness 准则高度一致**。上下文分层（L1/L2/L3）= context-engineering，质量门禁机械化 = Verification non-negotiable，执行/评判分离 = Persona 角色，规范即活文档 = Progressive disclosure

## 🔮 预判

- **Skill 会成为 Agent 的"操作系统"**。agent-skills 的 32.9k Star 说明开发者迫切需要给 Agent 装上"工程规范"。未来 Agent 的竞争力不仅是模型能力，更是 Skill 体系的完备度
- **Anti-rationalization 模式会被广泛复制**。这是一个简洁但强大的创新——任何 Agent 都需要"反对偷懒"机制。预计会变成 Skill 格式的标准组件
- **跨 Agent Skill 标准将在 2026 年形成**。目前每个 Agent 有自己的 Skill 格式（Claude 的 .claude/commands、Gemini 的 .gemini/commands），但像 agent-skills 这样的跨平台包正在推动统一。Hermes 应该关注并参与这个标准化进程
- **从 Skill 到 Agent Card 的演进**。agent-skills 的 Persona 角色概念与 Google A2A 协议的 Agent Card 高度相似，未来可能合并为标准化的 Agent 能力描述

## 相关笔记

- [Harness-Engineering-载具设计研究报告](Harness-Engineering-载具设计研究报告.md) - Harness Engineering 理论体系（Addy Osmani 原始概念）
- [2026-04-09-SKILL-md-ai-agent-skills](2026-04-09-SKILL-md-ai-agent-skills.md) - SKILL.md 格式设计分析
- [2026-05-08-ai-agent-protocol-wars-a2a-mcp](explore/2026-05-08-ai-agent-protocol-wars-a2a-mcp.md) - Agent 协议栈（A2A/MCP/FC 分层）
- [2026-05-08-企业AI转型三步法-知识库技能化智能体](2026-05-08-企业AI转型三步法-知识库技能化智能体.md) - 企业 AI 转型中的 Skill 化阶段
- [2026-04-17-hack-skills-给AI装上黑客大脑](2026-04-17-hack-skills-给AI装上黑客大脑.md) - 另一个方向（安全攻防）的 Skill 体系
