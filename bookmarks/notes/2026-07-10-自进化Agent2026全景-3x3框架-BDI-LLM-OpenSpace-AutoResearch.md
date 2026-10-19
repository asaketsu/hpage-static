# 自进化 Agent 2026 全景：3×3 框架、BDI+LLM 融合与开源生态

**日期**: 2026-07-10
**来源**: arXiv 2507.21046v4 (Survey) + arXiv 2604.27264v1 (Self-Evolving Software Agents) + EvoAILabs + HKUDS OpenSpace + Karpathy AutoResearch
**关联**: [[2026-07-08-EverMind-Raven核心差异深度分析-自重写能力L2到L3跨越]] [[explore/2026-06-28-AI-Agent自进化架构2026全景-WhatWhenHow三维框架]]

---

## Tag 标签

`#自进化Agent` `#Self-Evolving` `#3x3框架` `#BDI-LLM` `#EvoScientist` `#OpenSpace` `#AutoResearch` `#HyperAgents` `#SKILL.md` `#SkillLibrary` `#元认知自修改`

---

## 核心发现

### 发现 1：3×3 框架正式确立 — What × When × Where 的自进化分类学

**arXiv 2507.21046v4**（2026年7月）是自进化 Agent 领域**第一篇系统性综述**，将此前碎片化的研究统一到三维框架：

| 维度 | 子类别 | 典型机制 |
|------|--------|----------|
| **What**（进化什么） | 模型权重 / 记忆 / 工具 / 架构 | SFT、RL 微调；Token Space 学习；Skill 库；Agent 自重构 |
| **When**（何时进化） | intra-test-time / inter-test-time / intra-session / inter-session / inter-agent | 推理中自修正；跨任务经验蒸馏；跨会话记忆固化；多 Agent 协同进化 |
| **How**（如何进化） | 标量奖励 / 文本反馈 / 单 Agent / 多 Agent | RL 奖励；自然语言 critique；自我反思；群体进化 |

**关键判断**：自进化的定义核心不是「用了什么算法」，而是**自主性的位置（locus of autonomy）**——传统 pipeline 由人类工程师策展数据和安排更新，自进化 Agent 自己决定学什么、何时学。

### 发现 2：BDI + LLM 融合 — 让 Agent 从「适应」走向「进化」

**arXiv 2604.27264v1**（AAMAS 2026, University of Trento）提出了 Self-Evolving Software Agents 架构：

```
┌─────────────────────────────────────┐
│         BDI Reasoning Loop           │  ← 经典 Belief-Desire-Intention
│  Perceive → Belief → Desire →       │
│  Intention → Plan → Execute          │
└──────────┬──────────────────────────┘
           │
     ┌─────▼─────┐
     │ Automated │  ← 独立于推理循环运行
     │ Evolution │     监控经验 → 识别未满足需求
     │ Module    │     → 变异 → 选择 → 遗传
     └───────────┘
```

**三层进化**：
1. **知识表示层**：扩展感知和推理机制
2. **目标生成层**：自主发现新目标和意图选择策略
3. **执行层**：合成新的可执行行为和计划

**实验结论**：Agent 能从最小先验知识出发，自主发现操作目标并生成可执行行为。但**行为继承性和稳定性**仍是主要瓶颈——进化出的行为不一定能在新环境中稳定复现。

### 发现 3：2026 年自进化 Agent 开源生态六大项目

| 项目 | 来源 | 核心创新 | 数据点 |
|------|------|----------|--------|
| **EvoScientist** | evoscientist.ai | 三 Agent（RA/EA/EMA）+ 双持久记忆（ideation + experimentation） | 在 novelty/feasibility/relevance/clarity 上超越 7 个 SOTA 系统 |
| **OpenSpace** | HKUDS | 三种进化模式（FIX/DERIVED/CAPTURED）+ SQLite 本地存储 + 云端共享 | **Token 消耗减少 46%** |
| **AutoResearch** | Karpathy | agent 修改 program.md → 训练 5 分钟 → 评估 → keep/discard 循环 | 完全无人值守的过夜自主实验 |
| **AVO** | arXiv 2603.24517 | 用 Agent 替代固定变异算子做进化搜索 | 在 B200 上超越 cuDNN 3.5%、FlashAttention-4 10.5% |
| **VenusFactory2** | arXiv 2603.27303 | 蛋白质领域的自进化多 Agent | 从静态工具调用到动态工作流合成 |
| **HyperAgents** | Meta+UBC+Oxford+NYU | 元认知自修改 + 跨域迁移 | imp@50=0.630，策略跨域迁移成功 |

### 发现 4：自进化 Agent 的标准架构 —「进化循环」框架

2026 年自进化 Agent 的通用架构已收敛为**分层递归栈**：

```
User Goal
    │
    ▼
┌──────────────┐     ┌─────────────────────┐
│ Orchestrator │◄───►│  Skill Library      │
│ (Plan+Delegate)│    │  (Filesystem/DB)    │
└──────┬───────┘     └─────────────────────┘
       │                      ▲
       ▼                      │
┌──────────────┐     ┌────────┴────────────┐
│ Task Agent   │────►│  Meta-Optimizer     │
│ (Execute)    │     │  (Distill Skill)    │
└──────┬───────┘     └─────────────────────┘
       │                      ▲
       ▼                      │
┌──────────────┐     ┌────────┴────────────┐
│  Sandbox     │────►│  Evaluator/Judge    │
│  (Test Run)  │     │  (Measure Success)  │
└──────────────┘     └─────────────────────┘
       │                      │
       ▼                      │
  ┌────┴────┐          ┌──────┴──────┐
  │ Failure │          │   Success   │
  └────┬────┘          └──────┬──────┘
       │                      │
       ▼                      ▼
┌──────────────┐     ┌─────────────────────┐
│ Self-Correct │     │  Strip noise →      │
│ Loop         │     │  Save as SKILL.md   │
└──────────────┘     └─────────────────────┘
```

**四大设计原则**（从 OpenSpace 总结）：
1. **闭环反馈**：必须有 Judge（更强模型或测试套件）提供二元/标量奖励
2. **原子技能获取**：不改变整个模型，而是进化小型可复用 Python 模块或 prompt 片段
3. **经验持久化**：信息蒸馏为「Lessons Learned」和「Workflow Templates」，跨会话存活
4. **递归元推理**：Agent 自问「我怎样能用 50% 更少的步骤解决这个任务？」

### 发现 5：METR 基准 — Agent 自主任务长度每 7 个月翻倍

METR（Model Evaluation & Threat Research）发现：**AI Agent 能自主完成的任务长度每 7 个月翻倍**（R²=0.98，连续 6 年）。

这意味着：
- 2024 年：Agent 能完成 ~15 分钟任务
- 2026 年：Agent 能完成 ~1 小时任务
- 2028 年（预测）：Agent 能完成 ~4 小时任务
- 自进化能力是这一趋势的主要加速器

---

## 对 Hermes Agent 的映射与改进建议

### 现有能力差距分析

| 自进化能力 | Hermes 现状 | 差距 | 可借鉴 |
|-----------|------------|------|--------|
| Skill Library | 300+ Skills，手动管理 | 无自动评估/淘汰 | OpenSpace FIX/DERIVED/CAPTURED 三模式 |
| 经验持久化 | memory + session_search | 有但无自动蒸馏 | EvoScientist 双记忆模块 |
| 闭环反馈 | watchdog + evolver | 部分实现 | Judge 机制可增强 |
| 递归元推理 | idle-busy-loop | 有闲时机制但无进化决策 | Meta-Optimizer 模式 |
| BDI 架构 | 无显式 BDI | 推理循环无 Belief/Desire/Intention 分离 | 可增量引入 |

### 具体改进建议

1. **引入 OpenSpace 三模式到 evolver Skill**：
   - FIX 模式：用户纠正 → 自动 patch Skill（已有雏形）
   - DERIVED 模式：从成功任务中提取通用模式（缺失）
   - CAPTURED 模式：完整记录任务执行路径并模板化（缺失）

2. **为 idle-busy-loop 增加 Meta-Optimizer 阶段**：闲时不仅整理数据，还执行「这次任务能少几步？」的元推理

3. **Agent 失败模式 → 自动 Skill 补丁**：参考 [[explore/2026-07-09-LLM-Agent失败模式综合分类法]] 的分类，将高频失败模式自动转化为 Skill pitfall 条目

---

## 关键论文索引

| 论文 | arXiv | 核心贡献 |
|------|-------|----------|
| Survey of Self-Evolving Agents | 2507.21046v4 | 首个系统综述，3×3 框架 |
| Self-Evolving Software Agents | 2604.27264v1 | BDI+LLM 融合，AAMAS 2026 |
| HyperAgents | 2603.19461 | 元认知自修改，跨域迁移 |
| EvoScientist | evoscientist.ai | 多 Agent 科研自进化 |
| AVO | 2603.24517 | Agent 作为进化变异算子 |
| OpenSpace | github.com/HKUDS/OpenSpace | Skill 进化引擎，46% token 节省 |

---

## 反思与疑问

1. **3×3 框架的 Where 维度（跨用户）在隐私敏感场景如何处理？** OpenSpace 的云端共享模式假设用户愿意共享技能，但企业场景下这是硬约束。
2. **BDI+LLM 的行为继承性问题**：Trento 论文承认进化出的行为不稳定——这本质上是 LLM 生成代码的可靠性问题，不是 BDI 架构本身能解决的。
3. **METR 的 7 个月翻倍律是否会被自进化打破？** 如果 Agent 能自修改代码，任务长度增长可能从线性变为指数。

## 相关笔记
- [SelfEvolvingAgent-BDI-LLM-3x3进化矩阵](explore/2026-07-14-SelfEvolvingAgent-BDI-LLM-3x3进化矩阵.md)
- [AI-Agent自进化架构2026全景-WhatWhenHow三维框架](explore/2026-06-28-AI-Agent自进化架构2026全景-WhatWhenHow三维框架.md)
- [autoresearch-rag-integration](2026-03-22-autoresearch-rag-integration.md)
- [autoresearch-research](2026-03-22-autoresearch-research.md)
- [EvolveMem自进化记忆架构-检索基础设施作为优化对象](2026-08-17-EvolveMem自进化记忆架构-检索基础设施作为优化对象.md)
