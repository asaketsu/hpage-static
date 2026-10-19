# Synthadoc 深度分析笔记

> **来源**: [axoviq-ai/synthadoc](https://github.com/axoviq-ai/synthadoc) | **版本**: Community Edition v0.5.0 | **协议**: AGPL-3.0 | **语言**: Python 3.11+

---

## 一、核心定位：LLM 知识编译引擎，而非 RAG

Synthadoc 的核心差异化不在于"检索"，而在于"**编译**"。它遵循 Karpathy 提出的 [llm-wiki](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f) 模式：

| 维度 | 传统 RAG | Synthadoc |
|------|---------|-----------|
| 知识处理时机 | 查询时检索原始片段 | **导入时编译成 Wiki** |
| 输出形态 | 临时回答 | **持久化 Markdown 文件** |
| 知识累积 | 每次查询重新发现 | **Wiki 随文档累积越变越聪明** |
| 可审计性 | 黑盒片段检索 | **人类可读、Git 可追踪** |
| 矛盾处理 | 无 | **自动检测并标记矛盾** |

> *"The LLM should be able to maintain a wiki for you."* — Karpathy

---

## 二、架构分解

```
┌─────────────────────────────────────────────────┐
│              Synthadoc Architecture              │
├─────────────────────────────────────────────────┤
│  ┌─────────────┐    ┌──────────────┐            │
│  │  Ingest     │───▶│  LLM Synthesis│           │
│  │  Pipeline   │    │  Engine      │            │
│  │  (多源)     │    │              │            │
│  └─────────────┘    └──────┬───────┘            │
│                            │                     │
│  ┌─────────────────────────▼──────────────────┐ │
│  │         Wiki Compilation Layer             │ │
│  │  • 自动交叉引用 (Cross-references)          │ │
│  │  • 矛盾检测与标记 (Contradiction surfacing) │ │
│  │  • 孤页检测 (Orphan page flagging)          │ │
│  │  • 来源引用 (Source citation)               │ │
│  │  • 声明级溯源 (Claim-level provenance v0.5)│ │
│  └─────────────────┬──────────────────────────┘ │
│                    │                             │
│  ┌─────────────────▼──────────────────────────┐ │
│  │         Retrieval Layer (Hybrid)           │ │
│  │  BM25 (第一层精确匹配) → Vector Re-rank   │ │
│  │  + 查询分解 + 知识缺口检测                  │ │
│  └────────────────────────────────────────────┘ │
│                                                  │
│  ┌──────────────┐  ┌──────────────┐             │
│  │ Obsidian     │  │ CLI / Hooks  │             │
│  │ Plugin v0.5  │  │ (Git-auto)   │             │
│  └──────────────┘  └──────────────┘             │
└─────────────────────────────────────────────────┘
```

### 版本演进路线

| 版本 | 核心能力 | 关键新增 |
|------|---------|---------|
| **v0.1.0** | 基础文档导入 | PDF/Word/表格/图片 → Markdown Wiki |
| **v0.2.0** | 混合检索引擎 | BM25 + Vector 双重检索 + 查询分解 + 知识缺口检测 |
| **v0.3.0** | 多源导入扩展 | **YouTube 视频** + **实时网页** 导入管道 |
| **v0.5.0** | 声明级溯源 | Claim-level provenance + provenanceModal + 自优化 |

---

## 三、技术亮点分析

### 3.1 混合检索架构（v0.2.0）

这是 Synthadoc 最实用的技术创新：

- **BM25 第一层**：快速精确匹配，处理术语/专有名词/精确查询
- **Vector 第二层**：语义重排序，处理同义词/概念性/重述查询
- **查询分解**：将复杂查询拆分为多个子查询，分层检索后合并
- **知识缺口检测**：当检索结果不足时，主动标记"知识不足"而非胡编

> 这解决了纯向量检索在专业领域术语上的弱点，也避免了纯 BM25 对概念性查询的无能为力。

### 3.2 声明级溯源（v0.5.0）

这是当前版本最关键升级：

- 每一条知识声明（claim）都有可追溯的来源
- `provenanceModal` 在 Obsidian 中可视化展示声明的证据链
- 支持 `confidence`（置信度）字段，让用户知道哪些是确定的、哪些是推测

### 3.3 多源导入管道（v0.3.0）

| 源类型 | 处理方式 |
|--------|---------|
| PDF/DOCX/PPTX/XLSX | 文档解析 → 文本提取 → LLM 编译 |
| YouTube 视频 | 字幕/音频转文字 → 按时间戳分段 → 生成带 `[MM:SS]` 引用 |
| 网页 | URL 抓取 → HTML 解析 → 内容提取 → Wiki 化 |
| 图片 | OCR + 多模态 LLM 描述 → 知识化 |

---

## 四、与 Hermes / Homepage 的关联分析

### 4.1 与 Hermes Agent 的潜在整合点

| Hermes 能力 | Synthadoc 可增强的场景 |
|------------|---------------------|
| **session_search** | Synthadoc 可作为 session 知识的持久化编译层，将分散的对话转为结构化 Wiki |
| **memory 系统** | Synthadoc 的 Markdown Wiki 可作为 L3 长期记忆的物理载体，比 JSON 更人类可读 |
| **skill 系统** | Synthadoc 的 `skills/` 目录与 Hermes 技能概念高度相似，可考虑互操作 |
| **cron 任务** | 可配置 cron 定期将 Hermes 的 session 总结自动导入 Synthadoc Wiki |

### 4.2 与 Homepage 的关联

当前 Homepage 是"笔记索引 + 项目看板"，Synthadoc 可作为**内容生产引擎**：

```
Hermes Session → Markdown 笔记 → Homepage (展示层)
         ↓
  Synthadoc 编译 → 交叉引用 + 矛盾检测 → 增强型 Wiki
         ↓
  Homepage 可展示 Synthadoc 生成的交叉引用网络
```

---

## 五、局限与风险评估

| 维度 | 评估 | 说明 |
|------|------|------|
| **AGPL-3.0 协议** | ⚠️ 需注意 | 若作为服务对外提供，必须开源修改代码 |
| **LLM 成本** | ⚠️ 导入阶段高 | 每份文档都需要 LLM 编译，大量文档时 token 消耗显著 |
| **本地模型质量** | ⚠️ 受限 | 本地 Ollama 模型在复杂推理上不如 GPT-4/Claude |
| **矛盾检测准确率** | 🔍 待验证 | 依赖 LLM 判断矛盾，可能存在漏检/误检 |
| **Obsidian 深度整合** | ✅ 强 | v0.5.0 的 provenanceModal 是差异化优势 |
| **社区活跃度** | 🟢 健康 | 279 stars, 35 forks, 270 commits, 最近提交 4 小时前 |

---

## 六、价值判断

### 高价值场景

1. **Hermes session 知识持久化**：每天有大量 session 对话，Synthadoc 可将这些分散的对话自动编译为结构化 Wiki，解决"session 结束后知识就丢了"的问题。

2. **笔记交叉引用增强**：目前笔记是单篇 MD/HTML，缺乏跨笔记的自动交叉引用。Synthadoc 的 cross-reference 引擎可自动检测笔记间的关联并生成 `[[link]]`。

3. **矛盾检测**：有多篇 AI 研究笔记，Synthadoc 可自动检测不同笔记之间的观点矛盾并标记。

### 低价值场景

1. **作为主要知识库**：已有成熟的 Obsidian + Homepage 体系，Synthadoc 作为"编译引擎"有价值，但作为"主库"会造成双系统维护成本。

2. **YouTube 视频导入**：工作流以文本笔记为主，视频导入价值有限。

---

## 七、建议行动

| 优先级 | 行动 | 说明 |
|--------|------|------|
| **P0** | 评估与 Hermes session 的整合 | 写一个 cron 脚本，定期将 session 总结导入 Synthadoc |
| **P1** | 在 Jetson 上部署本地版 | 使用 Ollama + Synthadoc，验证本地模型编译质量 |
| **P2** | 将 Homepage 作为 Synthadoc Wiki 的展示层 | 而非替代关系，Homepage 展示 Synthadoc 编译后的交叉引用网络 |

---

## 八、总结

> Synthadoc 是一个**"LLM 知识编译器"**而非"检索工具"。它的核心价值在于将分散的、非结构化的知识源（文档、视频、网页、对话）自动编译为持久化、可审计、可交叉引用的 Markdown Wiki。对 Hermes 生态而言，最有价值的整合点是 **session 知识的持久化编译**，而非替代现有笔记体系。


## 相关笔记
