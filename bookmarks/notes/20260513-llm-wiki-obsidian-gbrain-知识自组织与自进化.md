# 深度解析 LLM Wiki / Obsidian-Wiki / GBrain：Agent 时代知识的"自组织"与"自进化"

> 原文：飞樰 · 阿里云开发者 · 2026-05  
> 链接：https://mp.weixin.qq.com/s/48XpgAMHeaKYj26PrJK-hw  
> 系列：《项目深度解析》第四篇（前篇：OpenClaw / Claude Code / Hermes Agent）  
> 笔记时间：2026-05-13  
> 标签：#Agent #KnowledgeEngineering #RAG #LLM-Wiki #GBrain #Obsidian-Wiki #自进化

---

## 一、核心论点

本文从**知识工程（Knowledge Engineering）**视角，分析 Agent 时代知识管理的范式转移：

| 阶段 | 特征 | 代表 | 本质 |
|------|------|------|------|
| 传统智能知识库（2016-2022） | 人工分类打标 → 关键词检索 | 客服系统 | 人维护索引 |
| RAG 时代（2023+） | 前置小模型检索 + 后置大模型生成 | NotebookLM / 大多数 RAG | 每次查询从头检索 |
| Agent 时代 | LLM 主动编译知识、渐进式披露 | LLM Wiki / GBrain / Obsidian-Wiki | 一次学习，永久可用 |

**核心论断**：知识质量直接决定 Agent 效果上限。Prompt Engineering 教模型"做什么"，Knowledge Engineering 教模型"知道什么"以及"如何运用已知"。

---

## 二、两类知识的划分

1. **经验性知识**（Implicit Knowledge）  
   - 完成任务的策略、步骤、隐性经验  
   - 在系统中封装为 **Skill（SKILL.md）**  
   - 例子：编码习惯、命名规范、注释风格、测试策略

2. **事实性知识**（Explicit Knowledge）  
   - 概念定义、报错原理、最佳实践、文档 FAQ  
   - 在系统中存储为 **Wiki 页面 / RAG 文档**

> 🔑 关键洞察：Skill 本质是"结构化的经验沉淀"，告诉 Agent 在特定场景下按什么步骤、用什么工具、遵循什么标准行动。

---

## 三、LLM Wiki：三层架构的知识闭环

### 架构

```
┌─────────────────┐
│   Raw Sources    │  ← 只读原始资料（文章/论文/笔记），不可变
├─────────────────┤
│   The Wiki       │  ← LLM 生成的结构化 Markdown 页面（摘要/实体/概念/对比）
├─────────────────┤
│   The Schema     │  ← 元指令文件（CLAUDE.md / AGENTS.md），定义如何更新和校验
└─────────────────┘
```

### 两个关键文件

- **index.md**（面向内容）：所有页面的目录，按类别组织，LLM 查询时先读索引
- **log.md**（面向时间）：追加式记录——ingest、query、lint 的时间线

### 三个操作

| 操作 | 说明 |
|------|------|
| **Ingest（摄入）** | 新知识源 → LLM 深度处理 → 提取要点 → 生成摘要 → 更新全局索引及实体页面。一个来源联动更新 10-15 个 Wiki 页面 |
| **Query（查询）** | LLM 定位相关页面 → 阅读后综合带引用的答案 → 高质量答案归档为新页面 |
| **Lint（维护）** | 类似代码静态检查，定期健康检查：矛盾识别、过期清理、孤儿页面修复、缺失引用补全 |

### 与传统 RAG 对比

| 对比项 | 传统 RAG | LLM Wiki |
|--------|----------|----------|
| 知识检索 | 每次查询重新检索原始文档 | 知识被提前编译到 Wiki 中 |
| 交叉引用 | 运行时发现 | 已提前建立 |
| 矛盾处理 | 每次重新发现 | 已标记 |
| 综合分析 | 每次重新推导 | 随来源添加而累积 |

**核心差异**："编译型语言 vs 解释型语言"——知识被编译一次后保持更新，而非每次重新解释。

---

## 四、Obsidian-Wiki：工程化实现

### 定位

基于 **Skill 的多 Agent 框架**，实现了 Karpathy 的 LLM Wiki 模式。

核心设计：
- **Agent 无关**：支持 9+ 种 Agent（Claude Code / Cursor / Windsurf / Codex / OpenClaw / Hermes / Gemini CLI / Kiro）
- **Skill 驱动**：所有操作通过标准化 Markdown Skill 文件定义
- **Obsidian 原生**：利用 wikilink / 图谱视图 / Dataview

### 架构增强

| 增强 | 说明 |
|------|------|
| **Delta 追踪** | .manifest.json 用 SHA-256 哈希追踪来源变更（new/modified/touched/unchanged/deleted） |
| **来源可信度边界** | 来源文档视为不可信，LLM 永远不执行来源中的命令（防 prompt injection） |
| **溯源标记** | `^[extracted]` / `^[inferred]` / `^[ambiguous]` 标注可信度 |
| **可见性标签** | visibility/internal / visibility/pii 过滤敏感内容 |
| **hot.md 热缓存** | 500 字语义快照，快速上下文感知 |

### 知识图谱 Skills

- **cross-linker**：自动发现页面间联系并建立交叉引用，带置信度评分（精确匹配 +4 分，共享标签 +2 分等）
- **graph-colorize**：可视化着色
- **graph-query**：支持多跳查询（如 `graph-query <slug> --depth N`）

### Agent 历史摄入 Skills

- 自动读取 ~/.claude/、~/.codex/ 下的 CLI 会话、Memory 文件
- 增量扫描、优先级解析（Memory > 近期笔记 > 会话记录）、隐私过滤、主题聚类、蒸馏沉淀

---

## 五、GBrain：混合检索与图谱关系

### 架构哲学

> **Thin Harness, Fat Skills**——把 Harness 做薄，精力放在丰富 Skills 上。

### 核心概念：潜在空间 vs 确定性

| | 潜在空间（Latent Space） | 确定性（Deterministic） |
|--|------------------------|------------------------|
| 含义 | LLM 决定**做什么** | 代码保证**在哪做**和**如何做** |
| 适合场景 | 判断、分析、综合 | SQL、计算、链接构建 |
| 例子 | 判断信息是否属于某人页面 | 代码构建交叉验证链接 |

### 混合检索架构："Chunk 确认 → 整页加载 → 分层呈现"

1. **混合搜索**（Hybrid Search）：关键词 + 语义向量 → 快速筛选相关 Chunks（~2KB）
2. **确认相关性**后加载完整页面
3. **分层喂给模型**：先"编译真相"（最新摘要），后"时间线证据"（历史记录/原始来源）

### Benchmark 效果

| 指标 | GBrain（带图谱） | 仅混合搜索（无图谱） | 提升 |
|------|-----------------|---------------------|------|
| P@5 | 49.1% | 17.7% | +31.4 pp |
| R@5 | 97.9% | — | — |

### 图谱构建 Pipeline

1. **实体抽取**：正则匹配 Markdown 链接 + wikilink + 关键词模式（"founded"、"invested in"）
2. **页面生成**：自动为实体生成 Markdown 页面（people/xxx.md、companies/xxx.md）
3. **关系分类**：基于规则判断（works_at / founded / invested_in / advises）
4. **反向链接强制化**：A 提到 B → 自动在 B 页面添加指向 A 的反向链接

### 多模态支持

支持解析视频、音频、PDF、截图，通过自动转录、OCR、实体抽取转化为结构化信息。

**关键对比**：Memory 的无脑堆积 → 越来越慢越来越乱；GBrain 的工程化体系 → 有效清洗、组织、维护，实现"自进化"而非"自混乱"。

---

## 六、适用场景与局限

### 适合场景

1. **个人深度研究**：长期跟踪、渐进式构建知识体系，像写书一样不断补充修正
2. **结构化读书笔记**：为每本书建立伴侣 Wiki，拆解概念/人物/观点并关联
3. **项目知识管理（PKM）**：跟踪 ADR、架构演变、Post-mortem
4. **Agent 记忆固化**：从 Agent 交互历史自动提取隐性知识
5. **小型团队内部 Wiki**：由 LLM 维护的低成本知识库

### 局限性

| 局限 | 说明 |
|------|------|
| 无数据库依赖 | 纯 Markdown，搜索依赖 index.md + grep / QMD，复杂查询能力弱 |
| 规模天花板 | index.md 驱动检索在数百-低千页面后性能显著下降 |
| 无自动化调度 | 无内建 Cron，所有操作需手动触发或外部脚本 |
| 弱结构化图谱 | wikilink 缺乏类型化边，无法表达 A 投资于 B 等语义关系 |
| 非实时实体检测 | cross-linker 等需手动触发，新知识关联有延迟 |

### 最佳实践

> **混合架构**：向量检索/关键词索引做快速初筛（"找得快"） + 大模型深度阅读/渐进式披露/离线迭代（"答得准" + "记得牢"）

---

## 七、参考文献

1. [LLM-Wiki](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f) — Andrej Karpathy
2. [AI Maker：How I Took Karpathy's LLM Wiki and Built an AI-Powered Second Brain in Obsidian](https://aimaker.substack.com/p/llm-wiki-obsidian-knowledge-base-andrej-karphaty)
3. [GBrain](https://github.com/garrytan/gbrain) — Garry Tan（YC CEO）
4. [Obsidian-Wiki](https://github.com/ar9av/obsidian-wiki)
5. [Medium：LLM Wiki: From Storing Knowledge to Compiling Understanding](https://medium.com/@ml-point/llm-wiki-from-storing-knowledge-to-compiling-understanding-94f448bfc917)

---

## 八、借鉴学习进化点

### 可立即借鉴的点

| # | 借鉴点 | 应用方向 | 优先级 |
|---|--------|----------|--------|
| 1 | **三层架构分离**（Raw Sources / Wiki / Schema） | ubot 的记忆系统可参考此分层，原始数据/加工知识/配置指令分开存储 | P0 |
| 2 | **Skillify 泛化**：Skill 不只是 SKILL.md，而是任何 Markdown 文件 | 将碎片笔记、知识片段都视为 Skill 的变体，减少"技能编写门槛"的心理障碍 | P0 |
| 3 | **Delta 追踪 + SHA-256**：只处理变更来源 | cron 巡检时可复用此思路，减少重复处理开销 | P1 |
| 4 | **渐进式披露（Progressive Disclosure）** | 大段 context 按优先级分层喂给模型，先结论后证据，降低 token 消耗 | P0 |
| 5 | **来源可信度边界**：来源不可信，LLM 不执行来源命令 | 安全加固，防 prompt injection through documents | P1 |
| 6 | **反向链接强制化** | 笔记系统自动建立双向链接，防止知识孤岛 | P1 |
| 7 | **分层检索：向量粗筛 + 文件精读** | 混合使用关键词 + 语义向量，平衡速度与精度 | P0 |
| 8 | **Lint 机制**：定期健康检查知识库 | 可 cron 化，自动发现矛盾、过期、孤立内容 | P1 |

### 对我们系统的具体行动项

1. **memory-system**：参考三层架构，分离原始输入/加工后知识/配置元指令
2. **wiki-knowledge-base**：引入 Delta 追踪机制，避免重复摄入
3. **search-fallback-chain**：可考虑加入渐进式披露策略，按相关性排序后分层喂入 context
4. **hermes-agent**：在 agent 配置中落实"Thin Harness, Fat Skills"哲学

---

*笔记由 `note-dual-format` + `note-content-deep-dive` 双技能流水线生成*


## 相关笔记

- [llm-wiki-gbrain-agent-evolution_33aa818c.md](llm-wiki-gbrain-agent-evolution_33aa818c.md)


## 相关笔记
- [2026-05-12-网络安全-security-automation](2026-05-12-网络安全-security-automation.md)
- [2026-05-12-数据治理-data-catalog](2026-05-12-数据治理-data-catalog.md)
- [llm-wiki-gbrain-agent-evolution_33aa818c](llm-wiki-gbrain-agent-evolution_33aa818c.md)
- [2026-05-15-上下文才是Agent的命门-QClaw上下文竞争论](2026-05-15-上下文才是Agent的命门-QClaw上下文竞争论.md)
- [2026-05-15-JAX-NVIDIA-GPU-微调Llama3.1实战方案](2026-05-15-JAX-NVIDIA-GPU-微调Llama3.1实战方案.md)
