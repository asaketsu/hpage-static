# Understand Anything — 源码精读

> **项目**: [Lum1104/Understand-Anything](https://github.com/Lum1104/Understand-Anything)
> **Stars**: 18.9k | **License**: MIT | **版本**: v2.7.3 (2025-05-19)
> **定位**: AI 编码平台通用插件，将任意代码库转为交互式知识图谱
> **精读日期**: 2026-05-24

---

## 一、项目全貌

Understand Anything 是一个跨平台 AI 编码插件（支持 Claude Code / Codex / Cursor / Copilot / Gemini CLI / Hermes 等 14 个平台），核心能力是将代码库通过多 Agent 流水线分析后生成交互式知识图谱，提供可视化仪表盘、语义搜索、Diff 影响分析、Onboarding 指南生成等功能。

### 技术栈

| 层级 | 技术 |
|------|------|
| 语言 | TypeScript (strict mode, ESM) |
| 构建工具 | pnpm monorepo + workspaces |
| 静态分析 | tree-sitter (WASM 版 web-tree-sitter) |
| 仪表盘 | React + React Flow + Zustand + TailwindCSS v4 |
| 测试 | Vitest |
| 插件分发 | 原生 Plugin Marketplace + 14 平台 symlink 安装脚本 |

### 核心架构

```
understand-anything-plugin/
├── agents/          # 7 个 Agent 的 prompt 定义（.md 文件）
│   ├── project-scanner.md    (233 行) — 文件发现 + 语言/框架检测
│   ├── file-analyzer.md      (520 行) — 节点+边提取（核心）
│   ├── architecture-analyzer.md (480 行) — 架构层识别
│   ├── tour-builder.md       (378 行) — 导览路径生成
│   ├── graph-reviewer.md     (239 行) — 图质量验证
│   ├── domain-analyzer.md    (124 行) — 业务域分析
│   └── article-analyzer.md   (92 行)  — 知识库文章分析
├── src/             # TypeScript 源码（辅助构建器）
│   ├── context-builder.ts    (147 行) — Chat 上下文构建
│   ├── diff-analyzer.ts      (198 行) — Diff 影响分析
│   ├── explain-builder.ts    (196 行) — 深度解释构建
│   ├── onboard-builder.ts    (124 行) — Onboarding 指南生成
│   └── understand-chat.ts    (29 行)  — Chat prompt 拼装
└── hooks/           # post-commit 自动更新钩子
```

---

## 二、核心设计模式精析

### 1. Tree-sitter + LLM 混合架构（最有价值的设计）

**核心理念**: 确定性分析和语义分析各司其职。

- **确定性层 (tree-sitter)**: 解析源码为 CST，提取 imports/exports/functions/classes/call-sites/inheritance → `importMap`。同输入 = 同输出，完全可复现。还用于增量更新的指纹变更检测。
- **语义层 (LLM)**: 读取 tree-sitter 结构 + 原始源码，生成 parser 无法提供的内容：自然语言摘要、标签、架构层归属、业务域映射、导览步骤、语言模式说明。

**借鉴价值**: 这与我们的 `agent-search-edit` Skill（意图分析→搜索计划→精准定位）思路一致，但 Understand Anything 在"确定性+语义"的分工上做到了极致——LLM **绝不**重复做 parser 已完成的工作（明确约束："Do NOT re-read source files to re-extract functions that the script already captured"）。

### 2. 两阶段 Agent 编排模式

**每个 Agent 的统一结构**:

```
Phase 1 — 结构化脚本执行（确定性）
  ├── 准备输入 JSON
  ├── 执行 bundled script
  └── 读取脚本输出

Phase 2 — LLM 语义分析（基于 Phase 1 结果）
  ├── 信任脚本结果，不重复分析
  └── 产出最终 JSON
```

**关键设计决策**:
- Agent 不返回中间结果到上下文，而是写入磁盘 `.understand-anything/intermediate/`
- 所有 Agent 的 model 字段从 frontmatter 中省略，让每个平台回退到默认模型（`inherit` 是 Claude Code 专属关键字，其他平台会报错）

### 3. 知识图谱数据模型

**16 种节点类型** (13 结构 + 3 业务域):
`file`, `function`, `class`, `module`, `concept`, `config`, `document`, `service`, `table`, `endpoint`, `pipeline`, `schema`, `resource`, `domain`, `flow`, `step`

**29 种边类型** (26 结构 + 3 业务域):
`imports`, `exports`, `contains`, `inherits`, `implements`, `calls`, `depends_on`, `tested_by`, `configures`, `documents`, `deploys`, `migrates`, `defines_schema`, `triggers`, `serves`, `provisions`, `routes`, `related`, `similar_to`, `subscribes`, `publishes`, `middleware`, `reads_from`, `writes_to`, `transforms`, `validates`, `contains_flow`, `flow_step`, `cross_domain`

**节点 ID 命名规范**: `<type>:<path>` 或 `<type>:<path>:<name>`（如 `function:src/utils.ts:formatDate`）

### 4. Chat 上下文构建策略（context-builder.ts）

```
用户 Query → SearchEngine 搜索相关节点
  → 1-hop 边扩展（邻接节点）
  → 收集涉及的 Layers
  → 格式化为 Markdown Prompt
  → 注入到 LLM 回答
```

**限制**: 最多 15 个相关节点。这避免了上下文爆炸，是一个实用的 token 预算控制策略。

### 5. Diff 影响分析（diff-analyzer.ts）

```
变更文件列表 → 映射到知识图谱节点
  → 1-hop 邻接发现受影响节点
  → 跨层影响评估
  → 风险评级（高复杂度 / 跨层 / 大爆炸半径 / 未映射文件）
```

**风险评估维度**:
- 高复杂度组件变更
- 跨架构层影响
- 下游影响范围 > 5 个组件
- 存在图谱外新文件

### 6. 导览生成算法（tour-builder.md）

```
Phase 1 脚本计算:
  ├── Fan-In 排名（重要性）
  ├── Fan-Out 排名（广度）
  ├── 入口点评分（文件名+路径+fan-out/fan-in）
  ├── BFS 遍历（依赖链）
  ├── 紧耦合集群检测
  └── 非代码文件分类

Phase 2 LLM 编排:
  README → 入口点 → 直接依赖 → 功能模块 → 基础设施
  （按 BFS depth 映射到 5-15 个教学步骤）
```

### 7. 并行批处理 + 增量更新

- file-analyzer 最多 5 个并发，每批 20-30 个文件
- 基于文件指纹（tree-sitter hash）检测变更，只重新分析变更文件
- post-commit hook 自动增量更新图谱

### 8. 图谱质量门禁（graph-reviewer）

**9 项检查**，分为 Critical（阻断）和 Warning（允许）:
- Schema 验证、引用完整性、完整性、Layer 覆盖率、唯一性、Tour 验证、质量检查、非代码节点质量、类型/前缀一致性

---

## 三、与 Hermes 体系的关系

### 三档分类

#### ① 有利进化 — 可借鉴到 Hermes

| 模式 | 借鉴方式 | 对应 Hermes |
|------|----------|-------------|
| **确定性+语义 分工** | Hermes 的 Skill 编写中，凡是能用脚本确定性完成的（grep/ripgrep/tree-sitter），LLM 绝不重复执行 | `agent-search-edit`, `small-batch-execution` |
| **磁盘中间结果** | 大型分析任务的中间结果写入文件而非保持在上下文中，防止 context 溢出 | `context-compressor` Skill |
| **1-hop 上下文扩展** | Chat/搜索场景下，先匹配核心节点再扩展邻接关系的模式 | 通用搜索策略 |
| **并行批处理 + 增量** | 大文件集处理时分批并发 + 基于指纹的增量检测 | 大规模代码库分析 |

#### ② 有价值备用 — Memory 存储

| 模式 | 价值 |
|------|------|
| 16 种节点 + 29 种边的知识图谱 Schema | 如果未来做代码库知识图谱，这是成熟的参考模型 |
| BFS depth → 教学步骤的映射 | 项目 Onboarding 导览生成的算法框架 |
| Agent model 省略回退 | 跨平台兼容的实用经验（避免平台专属关键字） |
| 9 项图质量门禁 | 复杂分析产出的质量验证模板 |

#### ③ 知识库 — 仅笔记

- 14 平台安装脚本的 symlink 策略
- React Flow + Zustand 仪表盘的 UI 架构
- `.understandignore` 文件过滤机制
- tree-sitter WASM 版的选择原因（原生绑定在 darwin/arm64 + Node 24 失败）

---

## 四、关键洞察

### 做得好的

1. **Agent prompt 工程**: file-analyzer.md（520行）堪称 Agent prompt 写作的教科书——精确的输入格式、严格的字段约束、详尽的 edge signal 参考表、明确的"不要做"列表
2. **确定性优先**: 所有能脚本化的工作都用 bundled script，LLM 只做语义理解
3. **增量设计**: 图谱可以 commit 到 Git 团队共享，新成员跳过分析管线
4. **跨平台兼容**: 一套 Agent prompt + 安装脚本适配 14 个 AI 编码平台

### 可改进的

1. 仪表盘只支持深色主题，无浅色模式
2. 非 tree-sitter 语言（Swift/Kotlin/Shell）只有基础 regex 提取，质量差距大
3. 风险评估是硬编码规则（> 5 组件、complex 标签），没有基于历史数据的自适应

---

*生成工具: MeowBot 分析引擎 | 源码仓库版本: v2.7.3*

## 相关笔记
- [HTML-Anything-Agent驱动HTML编辑器](2026-05-14-HTML-Anything-Agent驱动HTML编辑器.md)
- [html-anything-analysis](explore/2026-05-19-html-anything-analysis.md)
