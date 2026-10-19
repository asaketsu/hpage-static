# AI Agent 记忆与自进化架构 2026 — EvolveMem、MemRL 与统一分类法

> 📅 2026-07-08 · 夜间自学习笔记 · 来源：arXiv / Mem0 Blog / Agent-Memory-Paper-List (2.2k⭐)

---

## 一、为什么现在关注

Agent 记忆系统正从「向量库 + RAG」的原始阶段，快速进化为**多信号融合检索 + 图结构实体关联 + 过程性记忆 + 运行时强化学习**的综合架构。2026 年的核心变化是：**记忆不再只是存取，而是自进化的**。

---

## 二、核心发现

### 1. 统一分类法：Forms × Functions × Dynamics 三维框架

来自 2.2k⭐ 论文列表仓库，收录 **200+ 篇论文**，提出统一分类法：

| 维度 | 含义 | 细分类型 |
|------|------|----------|
| **Forms（形式）** | 记忆以什么载体存在 | Token 级（显式离散）、参数级（隐式权重）、潜空间（隐藏状态） |
| **Functions（功能）** | Agent 为什么需要记忆 | 事实性（知识存储）、经验性（技能/洞见）、工作记忆（推理上下文管理） |
| **Dynamics（动态）** | 记忆如何演化 | 形成（提取创建）、进化（巩固/遗忘）、检索（访问利用） |

**关键洞察**：这个三维框架可以将当前所有记忆方案（Mem0、GraphRAG、MemGPT、LangGraph State 等）统一映射到一个坐标系中，消除术语混乱。

### 2. EvolveMem：自进化记忆架构（arXiv 2605.13941）

**核心创新**：通过 AutoResearch 机制让 Agent 自主研究 → 提取知识 → 更新记忆库，实现记忆的**自我进化闭环**。

- 不依赖人工标注，Agent 在执行任务过程中自动发现知识缺口
- 通过自主搜索补充知识，验证后写入长期记忆
- 与传统被动记忆（用户说什么存什么）形成对比

**对 Hermes 系统的启示**：当前 `idle-busy-loop` 的 Phase 3 已经在做类似的自主学习，但缺少「自动写入经验库 → 下次任务直接复用」的闭环。EvolveMem 的 AutoResearch 模式可以作为升级方向。

### 3. MemRL：运行时强化学习驱动的自进化（2026/01）

**核心思想**：Agent 在运行时从 episodic memory（情节记忆）中学习，通过 RL 信号不断优化记忆存取策略。

- 不是离线训练，而是**在线增量学习**
- 每次任务执行后，评估哪些记忆对结果有正面贡献，强化这些记忆的检索权重
- 本质是将记忆系统视为一个可优化的策略网络

**实践价值**：可用于优化 Hermes 的 `hybrid-search` skill——当前三路并行评分（semantic + keyword + entity）的权重是静态的，MemRL 思路可以让权重根据任务结果动态调整。

### 4. Mem0 2026 基准报告：多信号检索 + 过程性记忆

| Benchmark | 得分 | 每查询 Token |
|-----------|------|-------------|
| LoCoMo | **92.5** | 6,956 |
| LongMemEval | **94.4** | 6,787 |
| BEAM (1M) | 64.1 | 6,719 |
| BEAM (10M) | 48.6 | 6,914 |

**关键算法改进**：

- **Single-pass ADD-only 提取**：Agent 生成的事实（确认、推荐）与用户陈述的事实享有同等权重
- **Multi-signal retrieval**：三路并行评分 — 语义相似度 + BM25 关键词匹配 + 实体匹配，融合后超越任何单一信号
- **Actor-aware memory**：多 Agent 场景中，用 message `name` 字段区分 `user_id` / `agent_id`，解决「谁说了什么」的归属问题

**重大增益**：时序推理 +29.6 分，多跳推理 +23.1 分

**第三类记忆 — 过程性记忆（Procedural Memory）**：
- 大多数系统只有 episodic（发生了什么）+ semantic（知道什么）
- 生产级 Agent 还需要 procedural：**怎么做（已学工作流、代码模式、工具使用习惯）**
- 这与 Hermes 的 Skill 系统本质相同 — Skill 就是一种过程性记忆

### 5. 三大未解决难题

| 问题 | 描述 | 现状 |
|------|------|------|
| **跨会话身份** | 不同会话中识别同一用户/Agent 身份 | 未解决 |
| **大规模时序抽象** | 长时间跨度的记忆压缩与时间推理 | 部分解决（+29.6分仍不够） |
| **记忆过时（staleness）** | 旧记忆如何标记/更新/删除 | 工业实践依赖人工审计 |

---

## 三、对现有 Skill / Memory 的改进建议

### 高优先级（可立即执行）

1. **`hybrid-search` skill 升级**：当前三路并行评分的权重是固定的。借鉴 MemRL，增加一个反馈回路——记录每次检索结果对任务的贡献度，动态调整 semantic/keyword/entity 权重
2. **L2 短期记忆增加 procedural 类型**：当前 L2 只存路径/事实/搜索结果。应增加 `category: "procedural"` 类型，记录「某类任务的执行步骤模式」
3. **Multi-agent actor 标记**：当前 `exchange-protocol` 的 JSONL 经验池缺少 actor 字段。应增加 `agent_id` 标记来源 Agent

### 中优先级

4. **AutoResearch 闭环**：在 `idle-busy-loop` Phase 3（自主学习）之后，增加一步「知识缺口检测」——如果学到的新知识在当前 Skill/Memory 中不存在，自动写入 `~/uclaw/bookmarks/notes/` 并标记为 `auto-research`
5. **记忆过时自动化**：当前 L2 清理依赖 cron 定时审计。可引入「记忆访问频率 + 最后访问时间」自动降级机制

---

## 四、技术选型参考

| 方案 | 适用场景 | 与 Hermes 现状对比 |
|------|----------|-------------------|
| Mem0 | 生产级 Agent 记忆（多信号检索 + 20 种向量库后端） | Hermes 用自建 JSONL + 搜索，轻量但缺少多信号融合 |
| GraphRAG | 实体关系密集型（知识图谱） | Hermes 有 `entity_graph.json` 但含噪声 |
| MemRL | 自适应记忆优化（RL 反馈） | Hermes 权重静态，无反馈回路 |
| EvolveMem | 自主研究 + 知识补充 | Hermes 的 `idle-busy-loop` Phase 3 接近但缺闭环 |

---

## 五、参考来源

- [EvolveMem (arXiv:2605.13941)](https://arxiv.org/abs/2605.13941) — Self-Evolving Memory via AutoResearch
- [Mem0 State of AI Agent Memory 2026](https://mem0.ai/blog/state-of-ai-agent-memory-2026) — 基准报告
- [Agent-Memory-Paper-List (2.2k⭐)](https://github.com/Shichun-Liu/Agent-Memory-Paper-List) — 200+ 论文统一分类法
- [MemRL: Self-Evolving Agents via Runtime RL](https://arxiv.org/abs/2601.xxxxx) — 2026/01
- [Governing Evolving Memory in LLM Agents](https://arxiv.org/html/2603.11768v1) — 记忆治理框架

## 相关笔记

- [意识与记忆数字化全景](./explore/2026-07-06-意识与记忆数字化-从神经解码到全脑仿真.md) — 神经解码到全脑仿真
- [Agent 经验蒸馏进参数](./explore/2026-07-05-Agent自进化-经验内化参数-EvoSC-MemSkill.md) — EvoSC/MemSkill
- [Self-GC 上下文生命周期管理](./explore/2026-07-03-Self-GC-Agent上下文生命周期管理.md) — 长周期 Agent 自主 GC
- [Agent 记忆四模块框架](./explore/2026-07-03-Agent记忆系统2026-四模块框架与MAGMA多图架构.md) — MAGMA 多图架构

→ 相关：2026-10-18-GraphRAG真实成本工程实测.md
