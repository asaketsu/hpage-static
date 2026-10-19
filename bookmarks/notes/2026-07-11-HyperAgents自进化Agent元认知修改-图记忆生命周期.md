# HyperAgents 与自进化 Agent 2026 — 元认知自我修改 + 图记忆生命周期

> 深度学习笔记 | 2026-07-11 | 来源: arXiv:2507.21046, arXiv:2602.05665, o-mega 2026 Guide

## 一、核心发现

### 1. HyperAgents：元认知自我修改的突破（2026.03）

Meta/UBC/Oxford/NYU 联合发表的 HyperAgents（arXiv:2603.19461）实现了**跨域自我改进策略迁移**：

- 一个 Python 程序包含两个共享代码库的函数：`solve_task()` 和 `modify_self()`
- `modify_self()` 可以修改自身——这是**元认知自我修改**（metacognitive self-modification）
- 基于 Darwin Gödel Machine (DGM) 框架升级为 DGM-H 算法
- 使用 Claude Sonnet 作为冻结基础模型，所有改进通过**离散代码修改**实现（非权重更新）

**关键结果**：

| 测试域 | 初始分 | 改进后 | 对比 |
|--------|--------|--------|------|
| 多语言编程 | 0.140 | 0.340 (训练) / 0.267 (测试) | 匹配专门设计的 DGM |
| 科学论文评审 | 0.0 | 0.710 | 超越 AI Scientist v2 (0.63) |
| 跨域迁移（奥数评分） | — | imp@50=0.630 | 人类专家系统得分 0.0 |

### 2. 自进化的硬约束：可验证性约束（Verifiability Constraint）

AI 自我改进**只在结果可客观验证的领域可靠工作**：

- ✅ 代码编译 / 数学证明正确 / 算法更快
- ❌ 营销文案 / 战略规划 / 关系管理（无清晰"更好"信号）

不可验证域中，自改进系统倾向于**奖励函数黑客**或优化代理指标。

### 3. 复合改进的经济学逻辑

- 每周 1% 改进 → 1 年后 68% 提升 → 2 年后近 3 倍
- METR 数据：Agent 自主完成任务时长**每 7 个月翻倍**（6 年 R²=0.98），2024-2025 加速到每 4 个月
- 当前前沿模型 50% 可靠性时间窗口约 50 分钟（一年前 <15 分钟）

### 4. 图结构 Agent 记忆：从被动日志到拓扑经验模型（arXiv:2602.05665）

2025-2026 前沿从线性/非结构化存储转向**图结构记忆**：

- 知识图谱、时序图、超图、层次树/图、混合图
- 优势：建模关系依赖、组织层次语义、支持灵活遍历推理

**记忆生命周期四阶段**：

```
提取(Extraction) → 存储(Storage) → 检索(Retrieval) → 进化(Evolution)
   数据→内容         组织效率         相关性召回         持续更新
```

### 5. 11 个开源记忆库横向对比

| 库 | 许可证 | 图记忆 | 生命周期管理 | 时序 | 推理 | 个性化 | Agent集成 |
|----|--------|--------|-------------|------|------|--------|----------|
| Mem0 | Apache2 | ✓ | ✓ | — | — | ✓ | ✓ |
| Graphiti | Apache2 | ✓ | — | — | ✓ | — | — |
| OpenMemory | Apache2 | ✓ | ✓ | ✓ | — | ✓ | ✓ |
| LangMem | MIT | — | ✓ | — | — | ✓ | ✓ |
| LightMem | — | — | ✓ | — | ✓ | ✓ | ✓ |

## 二、技术深度：自进化 Agent 分类法（arXiv:2507.21046, TMLR 2026）

77 页综述提出 **What/When/How/Where** 四维分析框架：

- **What**: 进化目标——提示词/工具/记忆/代码/策略
- **When**: 触发时机——错误驱动/周期性/事件驱动
- **How**: 进化方法——RL/进化搜索/元学习/记忆累积
- **Where**: 进化位置——权重级/提示级/代码级/工具级

## 三、对我们 Skill/Memory 体系的启示

| 维度 | 当前状态 | 改进方向 |
|------|---------|---------|
| 记忆结构 | 扁平 key-value (memory tool) | 引入图结构实体关系（memorygraph 已有基础） |
| 自进化触发 | 错误次数≥2 → Skill patch | 增加"成功模式"提取（正向进化） |
| 可验证性 | 退出码=0 | 对非代码任务增加 LLM-as-Judge 验证层 |
| 进化粒度 | Skill 整体重写 | 支持函数级 `modify_self()` 模式 |

## 四、关键引用

- HyperAgents: arXiv:2603.19461 (2026.03)
- A Survey of Self-Evolving Agents: arXiv:2507.21046 (TMLR 2026.01, 77pp)
- Graph-based Agent Memory: arXiv:2602.05665
- Darwin Gödel Machine: arXiv:2505.22954
- Awesome-GraphMemory: github.com/DEEP-PolyU/Awesome-GraphMemory
- Mem0 (ECAI 2025): arXiv:2504.19413

## 五、行动项

1. ✅ **memorygraph 已部署**——下一步增加"成功经验"自动入库（不仅是 error/fix）
2. 将 `modify_self()` 模式引入 Skill 体系：Skill 内嵌自评估 + patch 建议
3. 对夜间自学习 cron 增加"可验证性检查"：产出必须有可量化质量指标

## 相关笔记
- [自进化Agent2026-从HyperAgents到生产级自我改进](2026-08-03-自进化Agent2026-从HyperAgents到生产级自我改进.md)
- [自进化Agent前沿-Darwin-Godel-Machine与分类体系](2026-08-06-自进化Agent前沿-Darwin-Godel-Machine与分类体系.md)
