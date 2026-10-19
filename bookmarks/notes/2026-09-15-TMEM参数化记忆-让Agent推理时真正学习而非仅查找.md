# TMEM：参数化记忆——让 Agent 在推理时真正「学习」而非仅「查找」

> 论文：Scaling Self-Evolving Agents via Parametric Memory (arXiv:2606.04536, 2026, 阿里通义)
> 综述背景：Self-Improvements in Modern Agentic Systems (arXiv:2607.13104, 312 篇论文, 2026)

## 核心命题

当前所有 LLM Agent 的记忆系统（summary-based / retrieval-based）有一个结构性缺陷：**Agent 可以「查阅」经验，但不能「内化」经验**。模型参数在 rollout 期间冻结不变，任何从上下文截断的信息永久丢失。TMEM 打破这个限制——让 Agent 在推理时把经验写进自己的 LoRA 快权重，真正改变后续行为。

## 关键发现

### 1. 三层记忆架构

TMEM 将 Agent 记忆形式化为三个通道：

| 通道 | 符号 | 机制 | 特点 |
|------|------|------|------|
| 工作上下文 | h_t | 当前 prompt（token 级） | 快但容量有限，attention 成本 O(n²) |
| 显式记忆 | m_t | 文本摘要/检索片段 | 可压缩但 lossy，依赖检索质量 |
| **参数化记忆** | **Δ_t** | **在线 LoRA 快权重** | **直接改变策略，不占 prompt 空间** |

当 Δ_t ≡ 0 时，TMEM 退化为标准显式记忆 Agent——**现有所有记忆方法都是 TMEM 的特例**。

### 2. 快权重 Rollout 动力学

TMEM 的核心创新——将在线 LoRA 更新纳入 Agent 的决策过程：

```
标准 Agent:  a_t ~ π_θ(h_t, m_t)         # θ 固定
TMEM Agent:   a_t ~ π_{θ₀+Δ_t}(h_t, m_t)  # Δ_t 随经验增长
```

当上下文预算耗尽时，Agent 进入「记忆写入模式」：
1. 将当前会话蒸馏为 QA 式监督数据
2. 对 Δ_t 施加轻量在线 SFT 更新
3. 后续动作从 adapted policy π_{θ₀+Δ_t} 采样

**关键**：base 参数 θ₀ 在 rollout 内固定，只有 Δ_t 变化。

### 3. SVD 初始化加速在线收敛

LoRA 的投影矩阵 A 用预训练权重 W 的 SVD 分解初始化：

- A ← SVD(W) 的前 r 个左奇异向量
- 训练时固定 A，只更新系数矩阵 B
- 锚定到高能量方向 → 少步收敛 → 降低每次触发的计算成本

这个技巧的物理含义：**新知识应该先写入模型最「活跃」的参数子空间**，而非随机子空间。

### 4. Stop-Gradient 策略优化

记忆提取不再 是预处理步骤，而是 **RL 可优化的动作**：

- 梯度按段分配：任务行为段 / QA 提取段 / 终端响应段
- 通过在线更新算子 T 做梯度截断（stop-gradient）
- 结果：base 模型不仅学会做任务，还学会**产出对自己未来 LoRA 更新有用的监督数据**

这是 meta-learning 的一种实例化——模型学习「如何学习」。

### 5. 实验结果

在 LoCoMo、LongMemEval-S、Multi-Objective Search、CL-Bench 四个基准上：

| 方法 | Qwen3-4B | Qwen3-8B |
|------|----------|----------|
| No Memory | 4.63 | 4.90 |
| MemAgent (summary) | 4.11 | 4.90 |
| A-MEM (retrieval) | 4.11 | 4.37 |
| **TMEM** | **5.00** | **5.16** |

TMEM 在两个模型规模上均超越所有 baseline，且 8B 增益更大（参数化记忆容量随模型增大而增强）。

## 对 Hermes Agent 自进化架构的启示

### 当前 Hermes 记忆体系对照

| Hermes 层 | TMEM 对应 | 差距分析 |
|-----------|----------|---------|
| MEMORY (system prompt 注入) | h_t 工作上下文 | ✅ 已有 |
| Skills (SKILL.md) | m_t 显式记忆 | ✅ 已有（结构化） |
| session_search (FTS5 检索) | m_t 检索通道 | ✅ 已有 |
| **参数化记忆 Δ_t** | **缺失** | ❌ Hermes 无法在推理时改变模型参数 |

### 可借鉴的三个机制

**① 经验蒸馏为 QA 监督**

Hermes 的 evolver/experience-bank 当前产出文本经验卡片。可增加一步：将经验卡片转为 QA 对（「遇到 X 症状→用 Y 解法」），为未来在线 LoRA 微调准备数据。

**② SVD 初始化的参数子空间选择**

当前 Hermes 的 Skills 是离散的 markdown 文件。TMEM 的 SVD 启示：**高频使用的 Skill 应该映射到模型参数的高能量子空间**——这可以通过分析 base model 的权重 SVD 与 Skill 使用频率的关联来验证。

**③ 记忆提取作为可优化动作**

当前 Hermes 的 auto-skill / auto-memory 是固定流程（检测到模式→创建 Skill）。TMEM 的思路：将「是否提取记忆」「提取什么」「如何蒸馏」本身作为可 RL 优化的决策——让 Agent 学会**更好的记忆策略**而非固定规则。

## 综述全景：312 篇论文的分类

| 大类 | 论文数 | 核心问题 |
|------|--------|---------|
| Foundation Model Improvement | 77 | 改模型本身（SFT/RL/自蒸馏） |
| Scaffolding Improvement | 176 | 改外围脚手架（prompt/memory/tool） |
| Evaluation & Benchmarking | 59 | 如何衡量改进 |

Scaffolding 是主流（176/312 = 56%），其中 Memory 子类 65 篇是最大单一类别。这说明：**业界已认识到记忆是 Agent 进化的核心瓶颈**，但大多仍在 prompt-space 打转，TMEM 的 parametric 路线是少数派但方向正确。

### Darwin Godel Machine（递归自改进代表）

作为 Full Scaffolding 分类的代表：Agent 不仅改进解决方案，还**进化自己的搜索和适应启发式**——meta-evolution。这是 Hermes evolver 技能的理论上限。

## 参考文献

- TMEM 原文：arXiv:2606.04536, 2026
- 综述：arXiv:2607.13104, 2026 (312 papers)
- 自进化 Agent 综述：arXiv:2507.21046, TMLR 2026 (77 pages)
- Agent Memory 综述：arXiv:2602.06052, TMLR 2026
- A-MEM：NeurIPS 2025
- Mem0：arXiv:2503, 2025

---

*笔记日期：2026-09-15 | 来源：arXiv 精读 | 关联：Hermes Agent 自进化架构 / evolver 技能*

## 相关笔记

- [自进化Harness与记忆-三种写的不可混同](./2026-09-11-自进化Harness与记忆-三种写的不可混同-LiveSWE-DGM-SWE-Exp实证拆解.md) — 三种"写"的边界划定，TMEM 属哪类可对照
- [MemSkill与自进化Agent分类学](./2026-09-12-MemSkill与自进化Agent分类学.md) — 自进化 Agent 分类学，TMEM 参属可归位
- [Agent记忆离线整理-AutoDreamer](./2026-09-10-Agent记忆离线整理-AutoDreamer区域重写与SleepTimeCompute精读.md) — 离线重写照应在线写参，互补对照
- [HanakoMemory-vs-Graphs长推精读](./2026-09-07-HanakoMemory-vs-Graphs长推精读-一条边替代一次运行的规则蒸馏学与五层堆栈校准.md) — 规则蒸馏 vs 参数化的两条记忆学习路线
- [Agent记忆迁移性-模型升级后记忆会悄悄丢失吗](./explore/2026-09-08-Agent记忆迁移性-模型升级后记忆会悄悄丢失吗.md) — 记忆迁移性问题，与 TMEM 参数化记忆跨模型稳定性呼应
- [Ecdysis-Harness自进化失败归因](./2026-09-12-Ecdysis论文-模型特异迁就vs-harness级修复-跨任务失败聚合与FDCR四角色拆解.md) — 自进化 harness 失败模式，对照 TMEM 训练侧风险
- Explore: self-evolving-agents-2026-frontier-deep-dive（uclaw/notes）— 自进化 Agent 综述背景，与本文综述 2607.13104 同源
