# Self-Evolving Software Agents：BDI-LLM 架构与 3×3 进化矩阵

> 📅 2026-07-14 | 🏷️ AI Agent 自进化、BDI 架构、LLM 代码生成
> 来源：AAMAS 2026 论文 + Xinming Tu 技术博客

## 核心发现

### 1. BDI-LLM 自进化架构（AAMAS 2026）

传统自主 Agent 能适应环境变化，但目标、需求、能力在设计时固化，无法真正"进化"。本文提出 **Self-Evolving Software Agents**，将 BDI（Belief-Desire-Intention）推理循环与 LLM 结合，实现目标、推理、可执行代码的自主进化。

**架构核心：**

| 组件 | 功能 | 传统 BDI | 自进化 BDI-LLM |
|------|------|---------|--------------|
| Belief | 环境感知 | 预定义 | LLM 从经验中 elicite 新需求 |
| Desire | 目标生成 | 设计时固定 | 自主发现新目标 |
| Intention | 执行计划 | 预编码 | LLM 合成可执行代码 |
| **进化模块** | — | 无 | 独立于推理循环运行 |

**进化模块三阶段：**
1. **变异（Variation）**：从经验中识别当前知识/目标/行动库无法满足的新需求
2. **选择（Selection）**：通过环境交互验证新行为的有效性
3. **继承（Inheritance）**：成功行为被保留和复用，无效行为被丢弃

**关键设计决策：** 进化模块与运行时决策分离，保证行为连贯性的同时允许自主长期进化。

**实验发现：**
- ✅ Agent 能从最小先验知识出发，自主发现操作目标并生成可执行行为
- ⚠️ 行为继承性和鲁棒性仍是当前 LLM 驱动进化的瓶颈
- ⚠️ 环境复杂度增加时，进化稳定性下降

### 2. 3×3 进化矩阵（Xinming Tu 框架）

**两大进化动机：**
1. **经验降低边际成本** — 相似任务越做越便宜（更少 token、更少工具调用、更少重试）
2. **经验扩展能力边界** — 不仅更便宜，还能触达更难的任务

**三条进化轴：**

| 进化层 | 内容 | 修改成本 | 持久性 |
|--------|------|---------|--------|
| **外部文件** | memory、knowledge、skill 库 | 最低 | 可逆 |
| **Agent Harness** | prompts、tools、workflow、控制流 | 中等 | 中等 |
| **模型权重** | 参数化记忆、核心模型 | 最高 | 不可逆 |

**三个持久化时间线：**

| 时间线 | 外部文件 | Agent Harness | 模型权重 |
|--------|---------|-------------|---------|
| **单会话** | 工作记忆、scratchpad | 动态编排（运行时创建分支/工具/修复循环） | Test-time training |
| **跨会话** | Skill 库 & memory | 编译式 workflow harness | 参数个性化 |
| **跨用户** | 知识 & skill 共享池 | 平台级 harness 飞轮 | Checkpoint bootstrapping |

### 3. 关键洞察

**"同一个对象可以是静态文件，也可以是动态 harness 逻辑"** — 外部状态不再只存储事实，还可以存储 skills、workflows、policies、可执行算子。当 runtime 发现并加载一个 Python 函数/脚本时，它就从文件变成了 harness 的一部分。

**信任问题是跨用户进化的核心挑战：**
- 全局 skill 库若无 provenance、sandboxing、eval gate，会变成供应链漏洞或幻觉放大器
- Harness 更新本质是产品更新，需要回归测试、灰度发布、可审计性

## 技术细节

### BDI-LLM 进化触发机制

```
感知 → 当前知识/目标能否解释？
  ├─ 是 → 正常 BDI 推理循环
  └─ 否 → 触发进化模块
         → LLM 生成新需求描述
         → LLM 合成设计修订
         → LLM 生成可执行代码
         → 环境验证
           ├─ 成功 → 保留 & 复用
           └─ 失败 → 丢弃
```

### 与现有系统的映射

| 3×3 矩阵单元格 | 现有系统实例 |
|---------------|------------|
| 跨会话 / 外部文件 | Claude Code Skills、AGENTS.md、项目笔记 |
| 单会话 / Harness | Claude Code 动态 workflow（JS 编排脚本 + 子 Agent） |
| 跨用户 / 外部文件 | Alita-G（轨迹→MCP 工具→检索增强工具选择） |
| 跨用户 / Harness | ADAS（Agent 设计搜索）、Darwin Gödel Machine |
| 跨用户 / 模型权重 | Cursor Tab online RL（接受/拒绝→奖励信号） |

## 对 Hermes Agent 的实际应用价值

1. **Hermes 的 Skill 系统对应"跨会话/外部文件"格** — 已实现，但缺乏自动验证 gate
2. **Evolver/Skill-Review 对应"跨会话/Harness"格** — 需要加强行为继承机制
3. **当前缺失：Test-time training**（单会话/模型权重） — 短期不实际，但值得跟踪
4. **进化模块独立于推理循环**的设计原则值得借鉴 — 当前 Hermes 的 skill_manage 已部分实现

## 改进建议

| 优先级 | 建议 | 对应矩阵格 |
|--------|------|-----------|
| P1 | Skill 创建时增加自动验证 gate（dry-run） | 跨会话/外部文件 |
| P2 | 引入行为继承评分 — 成功行为权重提升，失败行为自动降级 | 跨会话/Harness |
| P3 | 跟踪 ADAS/Darwin Gödel Machine 跨用户进化方向 | 跨用户/Harness |

## 参考文献

- [Self-Evolving Software Agents](https://arxiv.org/abs/2604.27264) — AAMAS 2026, University of Trento
- [The What & When of Self-Evolving Agents](https://xinmingtu.cn/blog/2026/self-evolving-agents) — Xinming Tu
- [A Survey of Self-Evolving Agents](https://arxiv.org/abs/2507.21046) — What/When/How/Where 框架
- [EvoScientist](https://evoailabs.medium.com/) — 持久记忆 + 自进化的多 Agent AI 科学家框架


## 相关笔记

- [AI-Agent自进化架构](../2026-06-27-AI-Agent自进化架构.md) — 自进化架构核心
- [Agent记忆自进化2026-WorldEvolver](../2026-07-01-AI-Agent记忆自进化2026-WorldEvolver与神经程序记忆.md) — 记忆维度自进化
- [Agent记忆自进化2026-MemRL](../2026-07-04-Agent记忆自进化2026-MemRL运行时学习与三阶段框架.md) — 运行时学习维度
- [EvoSOP自进化工具优化](./2026-07-10-EvoSOP自进化工具优化.md) — 工具维度自进化