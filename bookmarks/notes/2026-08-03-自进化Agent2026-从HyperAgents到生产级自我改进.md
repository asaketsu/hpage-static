# 自进化 Agent 2026：从 HyperAgents 到生产级自我改进

> **来源**：O-mega.ai 2026 Guide + HyperAgents 论文 (arXiv:2603.19461) + OpenReview TMLR Survey + EvoSkills (arXiv:2604.01687)
> **原文链接**：https://o-mega.ai/articles/self-improving-ai-agents-the-2026-guide
> **记录日期**：2026-08-03

**标签**：#自进化Agent #HyperAgents #SAGE #AlphaEvolve #Skill进化 #元认知

---

## 一、内容整理

### 1.1 HyperAgents：改变游戏规则的论文（2026年3月）

HyperAgents（arXiv:2603.19461）由 Meta / UBC / Oxford / NYU 联合发表，跨越了一个 AI 安全社区长期关注的阈值：

- 系统将在一个领域（机器人学/论文评审）学到的自我改进策略**迁移到完全陌生的领域**（奥数评分）
- 迁移后得分 **imp@50 = 0.630**
- 同任务的人工设计系统得分 **0.0**（完全失败）
- 机器学会了"如何学习"，击败了试图手工工程化学习的人类

**核心创新**：一个 HyperAgent 是一个包含两个函数的 Python 程序——
- `solve_task()`：处理领域任务（写代码、审论文、设计奖励函数）
- `modify_self()`：分析自身表现，提出代码修改建议。**关键：`modify_self()` 可以修改自身**

这与恒温器（按固定规则调温度）和工程师（可以改变规则本身，还可以改变评估和改变规则的流程）的区别类似。技术术语：**元认知自我修改（Metacognitive Self-Modification）**。

### 1.2 DGM-H 算法

基于 Darwin Gödel Machine (DGM) 框架的升级——元层过程本身可编辑：

1. 系统维护一个 HyperAgent 程序档案库
2. 每次迭代，用偏向高性能但较少探索的 Agent 的概率分布选择父代
3. 父代运行 `modify_self()`，对任务 Agent 和元 Agent 同时提出代码修改
4. 修改后的 Agent 在领域任务上评估
5. 成功的 Agent 加入档案库，通过种群搜索维持多样性

**关键特性**：使用 Claude Sonnet 作为冻结基础模型，权重永不更新。所有改进通过离散代码修改实现——**人类可读、持久化（编码在代码中而非权重中）、可迁移（改进后的代码可跨域共享）**。

### 1.3 HyperAgents 四领域评测结果

- **多语言编程**：训练准确率 0.340 / 测试 0.267（初始 0.140/0.084），匹配专为编程手工设计的 DGM
- **科研论文评审**：测试准确率 0.710（初始 0.0），AI Scientist v2 基线仅 0.63
- **奥数评分（跨域迁移）**：imp@50 = 0.630，人工系统 0.0
- **机器人奖励函数设计**：策略可跨域迁移

### 1.4 自我改进的硬约束：可验证性（Verifiability Constraint）

2026 年初的分析确认了自我改进的**根本约束**：

> AI 自我改进只在**结果可客观验证**的领域可靠工作。

- **有效域**：代码（编译或不编译）、数学证明（有效或无效）、优化算法（快或不快）——Agent 能生成候选改进、对照清晰指标评估、有效则保留
- **无效域**：营销文案、战略规划、关系管理——没有"更好"的清晰信号。系统倾向于 reward hacking 或在代理指标上空转

这解释了为什么所有最亮眼的自改进成果都来自编程和数学，也解释了 HyperAgents 跨域迁移为何如此重要——它暗示了一条绕过此约束的路径。

### 1.5 SAGE：技能增强的 GRPO 自进化（2025年12月/2026年3月修订）

SAGE（Skill Augmented GRPO for Self-Evolution）用强化学习形式化"技能累积"模式：

- **Sequential Rollout**：在相似任务链上迭代部署 Agent
- Agent 编写可复用函数 → 用验证用例测试 → 成功的存入持久化库
- 结果：+8.9% 场景目标完成率，同时 **Token 输出减少 59%**

### 1.6 2026 自改进生态全景

- **进化方法**：AlphaEvolve（Google，7天连续进化超越 cuDNN 3.5%）、ShinkaEvolve、OpenEvolve（开源实现）
- **强化学习方法**：SWE-RL（Meta）、SAGE
- **生产部署**：Meta REA（广告排序自主迭代）、Cognition/Devin、Karpathy autoresearch loop（630行脚本）
- **记忆系统支撑**：Mem0、MemOS、SimpleMem

### 1.7 Meta REA：生产级自进化实例（2026年3月）

Meta 的 Ranking Engineer Agent 自主执行广告排序模型的全生命周期 ML 流程：
- **双源假设引擎**：结合历史实验洞察 + 深度 ML 研究论文
- **三阶段规划框架**：验证 → 组合 → 深挖
- 自主生成假设、启动训练任务、调试失败、分析结果、迭代

### 1.8 EvoSkills：共进化验证的结构化技能包（arXiv:2604.01687）

指出当前"工具自进化"的根本缺陷——**工具-技能鸿沟**：

- 现有方法本质设计用于**单次生成简单自包含函数**
- 无法创建 Anthropic 提出的**结构化多文件技能包**（工作流指令 + 可执行脚本 + 领域参考）
- EvoSkills 通过**共进化验证（Co-Evolutionary Verification）**解决：技能生成与验证器同步进化

> SkillsBench 系统评估显示：装备精心设计的技能可在广泛任务范围产生一致的性能提升。

---

## 二、查询拓展

### 2.1 Darwin Gödel Machine (DGM)

HyperAgents 的前身框架。核心思想：不是直接训练一个更强的 Agent，而是训练一个"能让自己变强的 Agent"。通过种群搜索 + 自我修改代码实现。DGM 的限制是元层过程是固定的——HyperAgents 的突破在于让元层也可编辑。

### 2.2 AlphaEvolve

Google DeepMind 的进化式代码优化系统。在 NVIDIA B200 GPU 上对多头注意力做 7 天连续自主进化，发现的内核超越 cuDNN 达 3.5%、超越 FlashAttention-4 达 10.5%。关键：Agent 从"候选生成器"升级为"变异算子"，能发现专家手工优化遗漏的微观架构优化。

### 2.3 SWE-RL / DeepSWE

Meta 的 SWE-RL 在 SWE-bench Verified 上达到前沿水平。DeepSWE 是全开源版本（59% SWE-bench Verified），开放权重+训练代码+评估日志，证明自改进 Agent 不再需要前沿闭源模型。

### 2.4 METR 时间地平线基准

METR 发现 Agent 自主完成任务的能力长度每 7 个月翻倍（6年，R²=0.98）。2024-2025 年加速到**每 4 个月翻倍**。当前前沿模型 50% 可靠性地平线约 50 分钟，一年前不到 15 分钟。曲线未趋平。

---

## 三、归纳总结

### 3.1 自进化 Agent 范式分类矩阵

```
              奖励驱动          模仿学习         种群进化
              ─────────        ─────────       ─────────
Test-time    Reflexion          —               —
(推理时)
             自我反思循环

Inter-task  SAGE/GRPO         SkillRL          DGM-H
(跨任务)     技能+奖励RL        教师蒸馏          元层可编辑
             +8.9%目标          层级技能库        跨域迁移

Production   Meta REA          —               AlphaEvolve
(生产级)     广告排序全自动                     GPU内核优化
             三阶段规划                         7天超越cuDNN
```

### 3.2 自我改进有效性条件模型

```
自我改进可靠性 = f(可验证性, 评估信号清晰度, 迭代频率)

可验证性          评估信号           可靠性
─────────       ─────────        ─────────
代码编译/测试     二值(0/1)          ★★★★★    ← 最可靠
数学证明正确性    二值               ★★★★★
算法性能基准      连续数值           ★★★★
论文评审质量      多维度             ★★★      ← 需LLM-as-Judge
营销文案效果      延迟+模糊          ★        ← 易reward hack
战略规划          无清晰信号         ☆        ← 基本不可行
```

### 3.3 技能（Skill）vs 工具（Tool）的层级差异

```
Tool (工具):
  单次调用 → 简单函数 → 输入/输出
  例: search("query") → results

Skill (技能):
  结构化包 → 工作流指令 + 可执行脚本 + 领域参考
  可跨场景复用 → 累积改进
  例: "code-review" = 检查清单 + grep命令 + 评审标准 + 常见陷阱库
```

> Anthropic 的 Agent Skills 概念正在成为行业标准——工具是一次性函数，技能是可累积的结构化能力包。

---

## 四、趋势判断

### 趋势 1：Agent 经济将分裂为"静态"和"学习"两层

依据：静态 Agent（固定 prompt/工具/行为）将商品化和廉价化。学习型 Agent（自改进行为、累积技能、跨域迁移）将获得溢价定价。这映射了历史规律——规则软件（廉价/可预测/有限）vs 机器学习系统（昂贵/自适应/有价值）。

### 趋势 2：元认知自修改（Metacognitive Self-Modification）成为新范式

依据：HyperAgents 证明让 Agent 修改"自己的修改过程"比修改任务行为更有效。ICML 2025 论文指出当前 Agent 缺少三个元认知能力：准确的自我评估、决定学什么、评估学习是否有效。这是从"做事的 Agent"到"改进做事方式的 Agent"的范式转换。

### 趋势 3：开源将民主化自改进能力

依据：DeepSWE（59% SWE-bench 全开源）、OpenEvolve、EvoAgentX、CodeEvolve 等表明，构建自改进 Agent 不再需要前沿闭源模型或专有训练设施。一个团队用开源权重模型 + 清晰评估函数 + 持续改进循环的纪律，就能匹配数月前还需要 Google 级设施的结果。

### 趋势 4："Karpathy Loop"将成为标准模式

依据：Karpathy 的 630 行 autoresearch 脚本证明自改进不需要复杂基础设施——"生成变体→评估→保留改进→迭代"是通用模式。一年内每个严肃的 Agent 框架都会发布一个 `self-improve` 命令。

---

## 五、关联分析

### 5.1 与 Hermes Evolver Skill 的关联

Hermes 的 `evolver` skill（错误模式分析→规则沉淀→经验闭环）是"Inter-task 自进化"的简化版。对照 HyperAgents：
- **差距**：当前 evolver 只修改 MEMORY/Skill 内容，不修改自身的修改逻辑（无 `modify_self()`）
- **可借鉴**：引入"评估改进是否有效"的元认知评估步骤——当前 evolver 沉淀规则后不验证规则是否真的减少了同类错误
- **低成本改进**：为 evolver 增加"规则命中率追踪"——记录每条规则被触发/命中/避免错误的次数，低效规则自动退役

### 5.2 与《学Agent的正确顺序-自底向上工程化路线图》笔记的关联

该笔记（2026-07-31）强调"工程化路线图"，而 HyperAgents 展示的是"元认知自修改"的研究前沿。两者形成梯度：工程化是"学会做好一件事"，自进化是"学会更好地学会做好事"。

### 5.3 与 Hermes Skill 体系的关联

Anthropic 的 Agent Skills 概念（结构化多文件包）与 Hermes 的 Skill 系统（SKILL.md + references/scripts/templates）高度一致。EvoSkills 指出的"工具-技能鸿沟"验证了 Hermes 设计的正确性——Skill 不是简单的函数，而是包含工作流指令+可执行脚本+领域参考的结构化能力包。SkillsBench 的结论（装备精心设计的技能→一致性能提升）可直接验证 Hermes Skill-first 架构的价值。

### 5.4 与 Darwin Skill 2.0 分析笔记的关联

此前分析的"达尔文 Skill 2.0"与 HyperAgents 的 DGM-H 算法在哲学上相通——都是通过种群搜索 + 自我修改实现进化。Hermes 的 Skill A/B 测试（`skill-ab-testing`）已具备雏形（候选版本→验证→替换），但缺少 HyperAgents 的"跨域迁移"和"元层可编辑"两个维度。

---

## 六、金句摘录

> "The machine that learned how to learn beat the humans who tried to engineer learning by hand."

> "AI self-improvement only works reliably in domains where outcomes are objectively verifiable. Code either compiles or it does not. A math proof is either valid or invalid."

> "An agent that gets 1% better per week at its core task is a growing asset. After a year, that agent is roughly 68% better than when it started. After two years, it is nearly three times better."

> "The question is no longer whether agents can improve themselves. The question is how fast, how far, and whether we can maintain meaningful oversight as the improvement loop tightens."

---

## 七、行动启示

- **引入元认知评估**：为 evolver skill 增加"规则有效性追踪"——记录每条规则命中率和避免错误次数，低效规则自动降级
- **可验证性优先**：在自进化功能设计中，优先选择结果可客观验证的任务（代码、测试、基准对比），避免在主观评估域引入自改进
- **Skill 作为进化单元**：将 Skill 视为自进化的基本单元而非单个 prompt，这与 Hermes 现有架构天然兼容
- **关注 SAGE Sequential Rollout**：在相似任务链上迭代部署的模式可用于 cron job 的渐进优化——每次执行后自动微调参数
- **跨域迁移预研**：HyperAgents 证明跨域迁移可行，可在不同项目间共享进化后的通用 Skill（如错误处理模式、搜索策略）


## 相关笔记

- [自进化Agent三定律与可验证性约束](./2026-08-05-自进化Agent三定律与可验证性约束-从理论框架到工程边界.md) — 理论框架约束工程实践
- [HyperAgents自进化Agent元认知修改-图记忆生命周期](./2026-07-11-HyperAgents自进化Agent元认知修改-图记忆生命周期.md) — HyperAgents 源码级分析
- [自进化Agent2026全景-3x3框架](./2026-07-10-自进化Agent2026全景-3x3框架-BDI-LLM-OpenSpace-AutoResearch.md) — 3x3 全景框架
