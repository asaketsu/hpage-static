# DocsChisel：LLM Agent 工具文档自适应优化框架

> **来源**：arXiv preprint
> **原文链接**：https://arxiv.org/abs/2608.10037
> **作者**：Lu You, Zhang Kun, Chen Bihuan, Peng Xin（软件工程方向，匿名投稿 ISESE 风格）
> **记录日期**：2026-08-13

**标签**：#LLM-Agent #工具文档 #文档优化 #工具调用 #Agent框架 #Trace分析

---

## 一、内容详细整理

### 1.1 核心问题

LLM Agent 依赖外部工具完成复杂任务，而工具文档（tool documentation）是 Agent 理解和调用工具的关键 grounding 资源。现有研究聚焦于提升 Agent 的工具使用能力（tool construction/retrieval/invocation），却几乎把工具文档当作**固定输入**，没有系统性研究文档本身如何影响 Agent 性能。

关键发现：同一信息字段在不同任务领域、不同 LLM backbone、不同 agent 范式下，效果可能**完全相反**——固定文档无法跨场景泛化。

### 1.2 大规模经验研究（RQ1 + RQ2）

**数据规模**：
- 14 个代表性数据集，共 24,955 个工具
- 3 个 LLM backbone：GPT-4o、GLM-5、Claude Haiku 4.5
- 2 种 agent 范式：ReAct（LangChain）、Multi-Agent（AutoGen）

**17 类信息字段识别**（Table II 覆盖率）：
- ✅ **全量覆盖（14/14）**：Tool Name（工具名）、Functionality Description（功能描述）
- ✅ **高度覆盖（10-13/14）**：Input Parameter Name/Type/Description、Parameter Required Flag
- ⚠️ **中度覆盖（4-7/14）**：Return Parameter Name/Type/Description、Usage Example、Parameter Optional Flag
- ❌ **极少覆盖（2-3/14）**：Usage Guidance、Invocation Constraint、Default Parameter Value、Response Template

**影响分析核心发现**：
- 17 个字段中只有 **6 个**在三个领域中效果方向一致
- 移除 Tool Name / Task Domain / Return Parameter Type / Response Template / Parameter Optional Flag → 一致降低成功率
- 添加 Invocation Constraint → 一致提升成功率（+0.75~11.25 pp）
- **同一字段跨域效果相反**：添加 Parameter Required Flag 在数据分析域 +2.50pp，在邮件域 -5.61pp，在日历域 +0.75pp
- 平均来看，增删单个信息字段会使任务成功率变化 **6.34 个百分点**

### 1.3 DocsChisel 方法论（三步迭代优化）

**整体架构**：Domain-Aware Execution Profiling → Iterative Optimization Loop → Best Candidate Selection

**步骤 1 — Domain-Aware Execution Profiling（领域感知执行画像）**
- 按任务领域组织工具和查询
- 将每个工具的关联查询切分为 optimization set（5/6）和 validation set（1/6）
- 用原始文档执行 Agent，收集失败 trace + 初始成功率

**步骤 2 — Memory-Guided Documentation Optimization（记忆引导文档优化）**

每个工具迭代优化，每轮三步：

> **三步分解的精妙之处**：不直接让 LLM 重写文档（EasyTool/DRAFT 的做法），而是拆解为诊断→规划→生成，每步可独立审视和积累经验。

1. **Failed Trace Diagnosis（失败 trace 诊断）**：LLM 审查每个失败 trace，总结失败证据，识别 Agent 行为与期望调用的不匹配，推断可能负责的信息字段。诊断记忆（diagnosis memory）积累领域级失败模式。
2. **Field Operation Planning（字段操作规划）**：将诊断结果映射到三类字段级操作——**Add**（补充缺失字段）、**Remove**（删除干扰/冗余字段）、**Refine**（细化模糊/不完整字段）。
3. **Optimized Documentation Generation（文档生成）**：LLM 应用规划的操作，生成新版本文档。

**步骤 3 — Re-execution Feedback + Candidate Selection**
- 新文档在 optimization set 上重新执行，收集新失败 trace
- 在 validation set 上评估成功率，更新 candidate set
- 达到最大迭代数后，选最优候选作为最终文档

**记忆机制的双重设计**：
- **Diagnosis Memory**：领域级失败模式，避免重复分析孤立 trace
- **Field Optimization Memory**：记录哪些字段操作在什么场景下有效，指导后续规划

### 1.4 评估结果（RQ3-RQ6）

**数据集**：WorkBench（5 域 26 工具）+ API-Bank（4 域 48 工具），共 9 域 74 工具 2072 查询，5:1:4 切分

**有效性（RQ3）**：
- 相比原始文档：TC +34.69%，TS +95.89%
- 相比基线（EasyTool + DRAFT）：平均 TC +30.83%，TS +75.15%
- 即便对比每个场景下最强基线：TC +26.23%，TS +46.11%
- 跨 9 个领域一致最优；在邮件管理、CRM、健康管理、智能家居等域，原始文档成功率极低，DocsChisel 提升尤为显著

**效率（RQ4）**：
- 文档长度：189.23 tokens/tool（比原始 +24.02%，与 DRAFT 相当）
- 优化 token 开销：4480.81 tokens/tool（比 DRAFT 少 6.35%）
- 优化时间：12.65 min/tool（高于 EasyTool 0.23 min 和 DRAFT 2.26 min，因为反复诊断+重执行）

**模型敏感性（RQ5）**：
- Claude Haiku 4.5 最优（TC 93.75%，TS 56.25%），GLM-5 次之，GPT-4o 最差
- 更强的指令遵循和推理能力 = 更好的文档优化质量
- 5 轮迭代后边际收益收敛；1→5 轮 TS 提升 80%

**消融实验（RQ6）**：
- 关闭记忆机制后（DocsChisel-NoMem），第 5 轮 TS 下降 76.47%
- 前 2 轮两版差异不大，但随着经验积累记忆的优势指数级扩大
- 没有记忆，指标在第 2 轮后基本停滞

### 1.5 统计严谨性

- 每个设置 3 次独立优化 × 5 次独立评估 = 15 次运行
- Mann-Whitney U test + Holm 校正，p_adj < 0.05
- Cohen's kappa = 0.862（信息字段标注一致性）

---

## 二、查询拓展

### 2.1 EasyTool
EasyTool（[58]）是 DocsChisel 的主要基线之一。它使用 LLM + 预定义模板将多样化文档压缩为简洁统一的工具使用指令。核心理念是"少即是多"——通过减少上下文开销来提升 Agent 效率。局限在于只在**现有字段内做压缩/标准化**，不增减字段。

### 2.2 DRAFT
DRAFT（[42]）是另一个基线。它利用 LLM 基于工具执行输出（而非失败 trace 诊断）迭代精炼文档。比 EasyTool 更动态（有反馈循环），但优化视角仍然是工具级别的独立改写，不跨工具积累经验。

### 2.3 WorkBench
WorkBench（[48]）是工具使用 Agent 的 benchmark，包含沙盒环境、真实办公任务、数据库和可执行工具。覆盖数据分析、邮件管理、日历管理、项目管理、CRM 五个领域。是本文 RQ2 影响分析的主要实验平台。

### 2.4 ReAct vs Multi-Agent 范式差异
ReAct 是单 Agent "推理-行动" 循环（Thought → Action → Observation），Multi-Agent（AutoGen）是多 Agent 协作编排。论文发现文档优化在两种范式下都有效，但不同范式对信息字段的需求有差异——Multi-Agent 可能更需要 Usage Guidance 和 Invocation Constraint 来协调多 Agent 间的工具分工。

---

## 三、归纳总结

### 3.1 核心洞察框架

```
工具文档 = 17 类信息字段的组合
         ↓
固定组合无法泛化（同一字段跨域效果相反）
         ↓
解法：自适应优化 = 失败 trace 驱动 + 字段级操作 + 迭代记忆
         ↓
Add / Remove / Refine 三类原子操作
         ↓
跨工具共享领域级失败模式记忆
```

### 3.2 三类基线的方法学差异

- **EasyTool**：模板压缩（静态，字段内）
- **DRAFT**：执行反馈迭代精炼（动态，工具级独立）
- **DocsChisel**：失败 trace 诊断 + 字段级增删改 + 领域级记忆积累（动态，跨工具协同）

### 3.3 关键数字速记
- 24,955 个工具 / 14 数据集 → 17 类字段 / 仅 6 类跨域一致
- 单字段增删 → 6.34pp 成功率变化
- DocsChisel → 原始文档 TS +95.89% / 基线 TS +75.15%
- 记忆机制 → 5 轮后 TS 贡献 +76.47%
- 优化成本 → 12.65 min/tool / 4480 tokens/tool

---

## 四、趋势判断

### 趋势1：工具文档将从"人写给人"转向"Agent 为 Agent 优化"
传统 API 文档面向人类开发者，强调可读性和完整性。LLM Agent 时代，文档的消费者变成了 Agent 本身——它不需要"优雅的散文"，需要的是精确的 invocation constraint、parameter type、return format。DocsChisel 证明 Agent 自己的失败 trace 就是最好的文档优化信号。
依据：RQ2 实验显示 Usage Guidance 和 Invocation Constraint 这两个"Agent 专用"字段覆盖率极低（2/14），但添加后效果显著。

### 趋势2：文档优化将成为 Agent 框架的标准离线管线
正如模型训练有数据清洗管线，Agent 部署也应该有"文档优化管线"。论文展示的 12.65 min/tool 离线成本远低于在线推理的反复试错成本。
依据：效率评估（RQ4）显示 DocsChisel 的优化 token 开销与 DRAFT 持平但效果大幅领先，说明"诊断-规划-生成"三步分解比暴力重写更高效。

### 趋势3：跨工具经验迁移是 Agent 文档工程的核心壁垒
单工具独立优化（DRAFT）的天花板在第 2 轮就触顶。DocsChisel 的领域级记忆让"工具 A 的失败经验帮助工具 B 的文档优化"，这种跨工具迁移是关键差异化因素。
依据：消融实验 NoMem 版本在第 2 轮后停滞，而带记忆版本持续提升到第 5 轮。

---

## 五、关联分析

### 5.1 与 Hermes Agent Skill 系统的关联

Hermes 的 Skill（SKILL.md）本质上就是"工具文档"的扩展形式——包含 description、trigger conditions、步骤指令、pitfalls、references。DocsChisel 的发现直接适用：

- **字段异构性问题**：不同 Skill 的 frontmatter 完整度差异巨大（有些有详细 pitfalls，有些只有 description）
- **跨 backbone 泛化问题**：为 GLM-5 写的 Skill 切到 Claude 上可能效果不同
- **失败 trace 驱动优化**：Hermes Gateway 已记录 Agent 执行 trace，可用于诊断 Skill 文档缺陷

### 5.2 与 Screenshots-or-Tools（2608.03327）精读笔记的关联

近期精读的 Screenshots-or-Tools 论文发现混合 GUI-MCP Agent 中工具调用率仅 17.8%，同一工具在推理模型和非推理模型上效果符号反转（+4pp vs -5.9pp）。这与 DocsChisel 的核心发现完全呼应——**文档有效性高度依赖 agent 设置**，不存在"一刀切"的最优文档。两篇论文从不同角度证明了工具文档需要自适应优化。

### 5.3 与 Context-Engineering Quality（2607.14275）的关联

Context-Engineering Quality 论文提出七维上下文质量评分，其中 tool-schema 维度直接对应工具文档质量。DocsChisel 可视为 tool-schema 维度的专项优化方法——通过失败 trace 诊断定位 schema 缺陷，用字段级操作修复。两篇论文形成"评分 → 优化"的完整闭环。

### 5.4 与 Beyond the Leaderboard（2607.05775）Agent 失败模式的关联

该论文提出 LLM Agent 六大失败模式分类法，其中"工具参数编造"和"工具选择错误"与文档质量直接相关。DocsChisel 的经验研究为这些失败模式提供了根因分析——Invocation Constraint 缺失导致参数编造，Task Domain 缺失导致工具选择错误。

---

## 六、金句摘录

> 「Existing tool documentation shows cross-dataset heterogeneity... different information fields have different impacts on task success rate of LLM agents across task domains, LLM backbones, and agent paradigms.」

> 「The benefit of memory becomes more pronounced as optimization experience accumulates.」— 消融实验证明记忆机制的价值随迭代指数级增长。

> 「DocsChisel trades additional offline optimization time for substantially improved effectiveness.」— 12.65 min/tool 的离线成本换来 95.89% 的成功率提升。

---

## 七、行动启示

### 借鉴点评估（P0-P3）

**P0 — Skill 文档失败 trace 诊断器**
- 论文方法可直接移植到 Hermes：收集 Agent 执行 Skill 时的失败 trace → LLM 诊断 → 识别 SKILL.md 中的文档缺陷 → 建议 Add/Remove/Refine 操作
- 现有基础：Hermes Gateway 已记录执行 trace，evolver/error-case-library 已有错误模式积累
- 关键障碍：需要建立 Skill 级别的"字段分类法"（类似论文的 17 类），以及 optimization/validation 查询集
- 预估工作量：2-3 天原型

**P0 — Skill 字段完整度审计脚本**
- 论文识别了 17 类信息字段及覆盖率。可对 Hermes 全量 Skill 做 frontmatter 审计，生成覆盖率报告
- 发现缺失率最高的字段（如 Invocation Constraint → 对应 Hermes 的 trigger conditions / 权限声明），针对性补全
- 现有基础：skill-stress-test 和 skill-review 已有审计框架
- 预估工作量：0.5 天

**P1 — 跨模型 Skill 适配性测试**
- 论文证明同一文档在不同 backbone 上效果不同。Hermes 多模型切换（GLM/Claude/GPT）时，Skill 效果可能波动
- 可选取 5-10 个高频 Skill，在 3 个模型上跑同一任务，对比成功率差异
- 预估工作量：1 天

**P2 — 领域级记忆机制借鉴**
- 论文的 diagnosis memory + field optimization memory 双重设计可借鉴到 evolver
- 当前 evolver 的错误模式是全局的，论文建议按领域（devops/data-science/creative 等）分桶积累
- 预估工作量：1-2 天

**P3 — 在线文档自适应（远期）**
- 论文是离线优化。更远期的方向是在线自适应——Agent 运行时发现文档不清晰时，动态标记并触发离线优化
- 需要工程改造较大，暂列为 P3


## 相关笔记

- [脚手架比接口更重要 MCP vs CLI 对照实验](./2026-08-12-脚手架比接口更重要-MCP-vs-CLI对照实验.md) — Agent 工具接口设计方法论，与文档优化交叉
- [长视野 Agent 鸿沟](./2026-08-11-长视野Agent鸿沟.md) — Agent 框架能力边界，工具文档质量影响长程任务
