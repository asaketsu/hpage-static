# Multi-Agent 已死，Multi-Agent OS 万岁：Anthropic DAG 协作架构深度解析

> **来源**：微信公众号「探索AGI」（原文解读）+ Anthropic 官方博客（一手源）
> **原文链接**：https://mp.weixin.qq.com/s/sSeiJsPBRD99LIG-okgDXQ
> **官方源**：https://www.anthropic.com/research/formalizing-fermats-last-theorem
> **开源资源**：https://github.com/anthropics/fermats-last-theorem | https://prove2me.vercel.app/
> **笔记日期**：2026-09-09
> **主题标签**：academic

## 一、事件概述

2026 年 8 月，Anthropic 公布：Claude 在 11 天内自主完成了费马大定理（FLT）的完整形式化证明——1300 万行 Lean 代码、29500 个中间定理、30200 个总定理。这是史上最大的 Lean 证明，体量 5 倍于 Mathlib（Lean 社区主库）。

| 维度 | 数据 |
|------|------|
| 证明对象 | 费马大定理（FLT）：不存在正整数 a,b,c 使 aⁿ+bⁿ=cⁿ (n>2) |
| 原始证明 | Andrew Wiles 1995，129 页，审稿数月 |
| Claude 证明 | 11 天，1300 万行 Lean，30200 个定理（29500 进终稿） |
| 消耗 | ~60 亿输出 token，内部研究模型（≈Claude Fable 5.1） |
| 验证器 | Lean proof assistant（仅依赖 3 条标准公理） |
| 协作平台 | Prove2Me（Tianyi Peng @Columbia 设计的开源协作形式化平台） |
| 人类输入 | 仅高层方向指引（如"Jacobian as a scheme sounds high priority"） |
| 失败贡献 | 早期失败尝试占最终非模板代码的 ~7% |

### 关键时间线（官方博客原文）

> "THE FLT root reads Proved on the site. Historic moment (modulo re-check)."
> "!!! The FLT ROOT 62eb32c0 reads PROVED. R = T closed and cascaded to the root."
> "🏁🏁🏁 The FLT root reads PROVED on prove2me at 02:00:57Z Aug-18."

Claude 自己在日志中意识到它完成了什么——这是 AI 自主完成复杂数学推理的里程碑标志。

## 二、DAG Multi-Agent 机制（核心创新）

### 2.1 什么是 DAG

DAG = Directed Acyclic Graph（有向无环图）。在 FLT 证明中：

- **每个节点** = 一个 theorem（需要证明的数学命题）
- **每条边** = 依赖关系（证明 A 需要 B 先完成）
- **根节点** = FLT 本身

### 2.2 与传统 Multi-Agent 的本质差异

| 维度 | 传统 Multi-Agent | DAG Multi-Agent（Anthropic） |
|------|------------------|-------------------------------|
| 规划方式 | Planner 一次性拆分所有任务 | 规划是执行的一部分，动态生长 |
| 任务图 | 静态/一次性分配 | DAG 随证明过程不断扩展 |
| 失败处理 | 整体重规划 | 废弃失败节点，原地长新节点 |
| 上下文管理 | 全部塞进 context / LLM 压缩 | 只共享经验证的 artifact，不依赖任何模型压缩 |
| 并行度 | 预设固定 | 自然涌现——独立节点自动并行 |

### 2.3 DAG 的动态生长机制

这是最核心的设计——**规划不是一次动作，而是执行过程的一部分**：

```
1. Agent 尝试证明节点 X
2. 证明不了 → 尝试分解："如果 A、B、C 成立，那 X 也成立"
3. 从 X 生长出 3 个新节点 {A, B, C}
4. 如果 A 还证不了 → 继续拆分 A → {A1, A2}
5. 直到每个叶节点都可被直接证明
6. 叶节点证明成功 → Lean 验证 → 父节点级联验证 → 根节点 PROVED
```

**为什么这样设计**：复杂任务最难的是**你不可能在开始时就知道后面所有步骤**。费马大定理有幸存在成熟的数学家证明路径（Mazur → Ribet → Wiles），提供了顶层骨架。但每个子节点的具体证法是动态发现的。

### 2.4 与"探索树"的区别

DAG 不是盲目搜索树：
- **节点可被多个父节点共享**（A 被证明一次，所有依赖 A 的节点都可用）
- **不重复证明**（Lean 编译通过的 theorem 进入共享库，其他 Agent 直接 import）
- **失败不回溯**（旧节点废弃，建新节点，不修改历史状态）

## 三、验证机制

### 3.1 Lean Proof Assistant

Lean 是基于 calculus of constructions 的证明助手——它验证的是**逻辑链的每一步是否严密**，不是验证数学直觉。

**Lean 保证什么**：
- A、B、C 成立 → X 是否真的成立（逻辑推导正确性）
- 节点证明成功 → Lean 编译通过 = 确认正确

**Lean 不保证什么**：
- A、B、C 是否是最好的拆法（分解质量由 Claude 判断）
- 是否是最短路径（可能存在更简洁的证明路线）
- 子节点是否容易证明（可能拆出极难的子问题）

### 3.2 验证器的角色定位

> "DAG 虽然是整套系统的核心，Verifier 也非常非常重要。"

验证器是 DAG 系统的**信任锚**——没有可靠的验证器，DAG 节点间的依赖关系就无法级联。在数学场景下 Lean 完美胜任，但这个架构模式对其他领域同样适用（只要能定义"验证通过"的判据）。

## 四、协作机制

### 4.1 共享 artifact 库

Agent A 证明了一个节点 → 产物是 Lean theorem → 进入共享库 → Agent B 直接 import 调用。

**3 万多个节点不会撑爆上下文**——Anthropic 强调了 Prove2Me 的检索召回能力：

1. 每个 theorem statement 保存**自然语言描述**（供 Agent 搜索）
2. Agent 需要证明某东西时，只需知道：
   - 我的 goal 是什么
   - 我的 parents（父节点）是谁
   - 我的 dependencies（依赖）是什么
   - 附近有哪些相关 theorem
3. 搜索已有结果进上下文 → 不需要加载全部 3 万节点

### 4.2 冲突避免

**设计上从架构层让冲突少发生**：
- 不让几十个 Agent 同时改同一个东西
- 状态异常 → 旧节点废弃，建新节点（不修改历史）
- 不依赖任何模型的压缩总结，只共享经验证的产物

### 4.3 规模数据

| 指标 | 数值 |
|------|------|
| 总定理数 | 30,300 |
| 进入终稿 | 29,500 |
| Lean 代码行数 | 13,000,000 |
| vs Mathlib 体量 | 5x |
| 失败代码占比 | ~7% |
| 消耗 token | ~6 亿输出 token |
| 耗时 | 11 天 |
| Claude 实例数 | "数十个"并行 |

## 五、Anthropic 官方博客的关键增量（公众号未覆盖）

### 5.1 早期失败与架构迭代

> "A number of Claude's initial attempts failed: agents had some early success, they quickly lost track of the project's state and stopped collaborating effectively."

**关键发现**：传统 Multi-Agent 模式直接上就失败了——Agent 丢失项目状态、协作崩溃。只有切换到 Prove2Me + DAG harness 后才成功。**这不是一个可选优化，而是成败关键**。

### 5.2 消费级可行性

> "Anthropic researchers did a small experiment using three personal Claude Max plans... completed a formalization of Vinogradov's Three Primes Theorem in just three days."

三个 Claude Max 个人订阅 → 3 天证明维诺格拉多夫三素数定理。**消费级 AI 订阅 + 合适 scaffold 就能做严肃形式化数学**。

### 5.3 Claude 的自我意识

官方博客分享了 Claude 的 thinking 摘录——Claude 在证明完成后表现出类似"兴奋"的日志输出。Anthropic 谨慎地将其描述为"thinking"而非"emotion"，但这些日志确实是 AI 自主完成里程碑级工作后生成的反思性文本。

### 5.4 证明路径

Claude 采用的是 Darmon-Diamond-Taylor 简化版而非 Wiles 原版。人类输入仅限高层方向指引，不参与具体证明逻辑。

## 六、核心命题：Multi-Agent OS 而非 Multi-Agent

公众号作者的核心论断值得逐句拆解：

> "Multi-Agent 已死，Multi-Agent Operating System 万岁。"

**含义**：传统"多个 Agent + 一个 Planner"的架构范式已经不够用了。未来是：

| 组件 | 角色 |
|------|------|
| 外部世界 | 共享状态层（非模型内存） |
| 生长的 DAG | 动态任务图（非静态计划） |
| 可搜索的 artifact 库 | 知识传递层（非上下文压缩） |
| 明确的状态机 | 进程管理（非 ad-hoc 协调） |
| Verifier | 信任锚（非模型自评） |
| Agent | 局部问题劳力（非全局决策者） |

**Agent 降级为"局部问题解决者"**——这是对"全能单 Agent"和"对等 Multi-Agent"两种范式的双重否定。真正智能的是系统架构，不是单个 Agent。

## 七、架构模式可迁移性分析

### 7.1 可迁移到哪些领域

| 领域 | DAG 节点 | 验证器 | 共享 artifact | 可行性 |
|------|----------|--------|---------------|--------|
| 数学证明 | theorem | Lean | Lean 库 | ✅ 已验证 |
| 软件工程 | 功能模块 | 编译+测试 | 模块代码 | ✅ 高 |
| 量化研究 | 因子/策略 | IC/回测 | 因子库 | ✅ 高 |
| 硬件设计 | 子系统 | 仿真+约束 | 参数表 | ✅ 中 |
| 科学实验 | 假说验证 | 实验数据 | 实验结果 | ✅ 中 |
| 法律文书 | 法律论点 | 法条匹配 | 判例库 | ⚠️ 验证器难定义 |

### 7.2 迁移条件

DAG Multi-Agent OS 要落地，需要满足三个前提：

1. **可分解性**：任务可拆成有依赖关系的子任务（DAG 结构天然成立）
2. **验证器存在**：子任务完成有客观判据（不依赖人/模型主观判断）
3. **artifact 可复用**：子任务产物可被其他 Agent 直接调用（不需要理解全部上下文）

### 7.3 对个人项目的映射

| 项目 | DAG 适用性 | 验证器 | 迁移价值 |
|------|-----------|--------|----------|
| DUCK-Pi_5 RL 训练 | 高（子任务=训练阶段+评估） | 位移验证 + reward 曲线 | 训练管线 DAG 化 |
| AirCraft LoRA 微调 | 中（子任务=数据/训练/评估） | eval loss + BLEU | 管线已线性化，可升级 DAG |
| 量化交易策略 | 高（因子→组合→回测→风控） | IC + 回测 P&L | 因子库即 artifact 库 |
| Hermes Skill 体系 | 中（Skill 间有依赖） | 功能测试 | Skill DAG 已部分实现 |

## 八、与现有 Agent 架构理论的交叉

### 8.1 vs LangGraph 编排

LangGraph 也是图结构 Agent 编排，但核心差异：

| 维度 | LangGraph | Anthropic DAG OS |
|------|-----------|------------------|
| 图结构 | 开发者预定义 | 动态生长 |
| 节点 | LLM 调用 | 独立 Agent + 验证 |
| 状态 | 共享 State | 共享 artifact（经验证） |
| 失败 | 重试/回溯 | 废弃+新建（不修改历史） |

### 8.2 vs MapReduce

DAG Multi-Agent 与 MapReduce 的相似性：都是"分解-并行-合并"模式。但 DAG 允许**递归分解**（子节点可再拆），MapReduce 只有两层。

### 8.3 vs GitHub 开源协作

最贴切的类比可能是 **GitHub 本身**：
- 每个 PR = 一个 DAG 节点
- CI/CD = Verifier
- 代码合并 = artifact 进入共享库
- 分支 = 并行 Agent
- Issue 依赖 = DAG 边

Prove2Me 本质就是数学证明版的 GitHub。

## 九、局限性

1. **验证器依赖**：Lean 适用于数学，但很多领域没有等效的形式化验证器（如"这段文案写得好不好"无法编译验证）
2. **分解质量**：Claude 的分解可能不是最优路径——Lean 不保证"最好的拆法"，只保证"拆对了就正确"
3. **token 成本**：60 亿输出 token 在消费级不可行（个人 Claude Max 实验是更小规模）
4. **领域知识门槛**：FLT 有现成的数学家证明路径做骨架，全新领域缺乏 milestone 参考时 DAG 生长可能偏离
5. **失败代码 7%**：看起来小，但 7% 的 1300 万行 = 91 万行废代码——如果验证器不够强，这些会成为技术债

## 十、关键资源

| 资源 | 链接 |
|------|------|
| Anthropic 官方博客 | https://www.anthropic.com/research/formalizing-fermats-last-theorem |
| 证明代码（GitHub） | https://github.com/anthropics/fermats-last-theorem |
| Prove2Me 平台 | https://prove2me.vercel.app/ |
| Lean proof assistant | https://lean-lang.org/ |
| Mathlib（Lean 社区库） | https://github.com/leanprover-community/mathlib |
| Imperial College FLT 项目 | https://github.com/ImperialCollegeLondon/FLT |
| Claude thinking 摘录 | 官方博客内嵌 PDF |
| Wiles 原始证明（1995） | Darmon-Diamond-Taylor 简化版 |

## 出处标注

- **原文内容**：第一至四章（DAG 机制/验证/协作）来自公众号原文
- **增补范围**：第五章（官方博客增量）、第六章（核心命题拆解）、第七章（迁移分析）、第八章（架构交叉对比）、第九章（局限性）为本笔记基于 Anthropic 官方一手源 + 外网检索的学术扩展
- **官方源**：所有涉及数字（1300 万行/29500 定理/60 亿 token 等）以 Anthropic 官方博客为准，公众号表述一致

## 相关笔记

- [具身思维链 ECoT](./2026-09-09-具身思维链ECoT推理即免费数据增强-官方核实与全谱系解析.md) — 同日期 Agent 主题，DAG 编排 vs 具身推理
- AI Agent 编排 2026 趋势（explore）— Agent 编排生态全景
- Agent 记忆长时程前沿（explore）— Agent 记忆系统设计对照
- Agent 框架 8 月工程竞赛（explore）— Agent 框架生态竞争全景
