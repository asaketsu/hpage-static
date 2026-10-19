# Agent 蒸馏与长程规划 2026：MAD-OPD 与 Physics of Planning

> **学习日期**: 2026-07-29
> **来源**: arXiv 2607.24720, 2605.01347 精读
> **核心论点**: 2026 年 Agent 蒸馏出现两大突破——多教师辩论打破单教师能力天花板（MAD-OPD），以及首次系统性揭示长程规划能力的获取、塑形与整合三阶段（Physics of Planning）。

出处：arXiv 2607.24720 / 2605.01347 | 2026-05 ~ 2026-07

## 一、两篇核心论文（内容整理）

### 1.1 MAD-OPD：多 Agent 辩论驱动蒸馏

**arXiv**: 2605.01347 | 2026-05-02

**解决的问题**：On-Policy Distillation (OPD) 受限于单教师能力天花板——教师犯错，学生继承错误。且 OPD 在 agentic 任务中几乎未被探索，因为**多步错误在长轨迹中复合**导致训练不稳定。

**两大技术创新**：

**① MAD-OPD（Multi-Agent Debate-driven OPD）**
- 将蒸馏教师重构为**辩论集体**（deliberative collective）
- 多个教师对学生 on-policy 状态进行辩论
- 辩论产生**涌现集体智能**，提供 token 级监督
- 每个教师的贡献按其**辩论后置信度**加权

**② OPAD（On-Policy Agentic Distillation）**
- 为多步 agentic 任务扩展 OPD
- 添加 **step-level sampling** 稳定多步错误复合下的训练
- 推导 **task-adaptive divergence principle**：
  - JSD（Jensen-Shannon divergence）→ agentic 稳定性
  - Reverse KL → 代码生成

**实验结果**（6 种教师-学生配置，5 个 benchmark）：
- 6/6 配置中排名第一
- 14B+8B→4B 配置：agentic 平均 +2.4%，代码平均 +3.7%
- 超越更强的单教师 OPD

**核心洞察**：单教师蒸馏 = 复制天花板；多教师辩论 = **超越任何单一教师的涌现能力**。这跟量化领域 Agora 的"评估器保留分歧而非投票"思想异曲同工。

### 1.2 The Physics of Multi-Turn Long-Horizon Planning

**arXiv**: 2607.24720 | 2026-07-27（最新！）

**解决的问题**：Agent 的长程规划能力是如何获取、塑形和整合的？现有模型在不可控的互联网数据上训练，无法精确识别规划能力的来源。

**三阶段统一框架**：

**阶段一：规划能力获取（Pre-training）**
- **数据格式效应**：显式世界模型构建（CoT 状态转移建模）→ 更强的长程泛化
- **关键发现**：原子技能单独不足以实现组合泛化，**少量长程数据即可**
- **陷阱**：次优轨迹严重损害性能，因为**错误在长程中放大**

**阶段二：规划能力塑形（Post-training: GRPO + OPD）**
- 通过**互信息**区分：
  - 通用规划模式（general planning patterns）
  - 任务特定规划知识（task-specific planning knowledge）
- **通用模式的三个区域**：
  - 不必要区域（unnecessary）：post-training 无增益
  - 有效区域（effective）：post-training 有改善
  - 不支持区域（unsupported）：post-training 有害
- **关键发现**：OPD 比 GRPO 有更宽的有效区域——在低质量和长程设置下提供更一致的更新方向

**阶段三：规划能力整合（Post-training: MOPD）**
- 多教师 on-policy 蒸馏（MOPD）通过收敛到**跨环境共享规划模式**来整合能力
- 三种模式兼容性：
  - 兼容模式 → 跨环境泛化
  - 部分共享模式 → 持续学习
  - 完全冲突模式 → 严重干扰

**一个深刻警告**：蒸馏教师未见过的流程可能**损害学生已有的世界建模**，而未能完全建立新知识。即"硬教新东西"可能"搞坏旧东西"。

## 二、两篇论文的交叉发现

| 维度 | MAD-OPD | Physics of Planning |
|------|---------|-------------------|
| **核心对象** | 蒸馏机制 | 规划能力本身 |
| **多教师** | 辩论集体，置信度加权 | MOPD，收敛到共享模式 |
| **分歧处理** | 辩论涌现集体智能 | 保留三种兼容性分类 |
| **稳定性** | OPAD step-level sampling | OPD > GRPO（更宽有效区域） |
| **关键风险** | 单教师错误继承 | 次优轨迹 + 冲突模式干扰 |

**共同结论**：
1. **多教师 > 单教师**：无论蒸馏还是整合，多源信息都比单源更鲁棒
2. **On-Policy > Off-Policy**：学生用自己的轨迹训练，比学习教师的轨迹更稳定
3. **一致性方向是关键**：OPD/MOPD 的优势在于提供比 RL 更一致的梯度方向

## 三、趋势判断与查询拓展

**趋势判断**：

1. **多教师辩论将成为 Agent 蒸馏标配**：MAD-OPD 的 6/6 配置第一证明了多源信息的系统性优势，未来蒸馏框架默认多教师
2. **On-Policy 方法在 Agent 领域超越 Off-Policy**：Physics of Planning 和 MAD-OPD 一致表明 on-policy 在长程任务中更稳定
3. **规划能力研究从黑箱走向可控实验**：Physics of Planning 的统一环境标志着 Agent 规划研究进入"可精确控制"阶段

**查询拓展方向**：
- MAD-OPD 的"辩论后置信度加权"具体如何计算？是否可迁移到 Hermes 的多猫决策？
- Physics of Planning 的统一环境是否开源？数据格式设计细节？
- OPAD 的 step-level sampling 与 PPO 的 clip 机制有何区别？
- Structured Distillation for Agent Memory (2603.13017) 的 11x token 压缩如何实现？

## 四、对 Hermes Agent 架构的启发

### 4.1 直接可用

1. **OPD 思想验证当前架构**：Hermes 的 delegate_task 本质是 off-policy——subagent 学习的不是自己的轨迹。Physics of Planning 表明 on-policy 更稳定。当前 subagent 模式在长任务中不稳定可能与此有关。

2. **多教师辩论 → 决策增强**：当前四只猫（Dev/OPM/Content/Data）的分发模式可以升级——关键决策不只分配给一只猫，而是让 2-3 只猫从不同角度**辩论**后由置信度加权聚合。

3. **模式兼容性分类**：跨 skill 迁移知识时，应判断是兼容模式还是冲突模式。完全冲突的技能不应强制整合（如 RL 训练的 agent vs 规划型 agent）。

### 4.2 中期改进

4. **次优轨迹过滤**：Physics of Planning 发现次优轨迹在长程中严重损害性能。Hermes 的 auto-dream / auto-learner 从 web 获取的轨迹质量参差不齐，应增加**质量门控**——只有高置信度轨迹才进入学习池。

5. **少量长程数据 > 大量原子技能**：当前 auto-learner 倾向收集碎片化知识。研究表明，少量但完整的长程任务数据对组合泛化更有效。应优先收集端到端任务执行记录。

### 4.3 论文警告的实际映射

6. **"蒸馏未见流程会损害已有世界建模"** → 对 Hermes 意味着：**不要盲目从外部 agent（如 Claude Code）蒸馏所有行为**。如果外部 agent 的某些流程与 Hermes 的既有架构冲突，强制整合可能破坏已有能力。应先评估模式兼容性。

## 五、技术术语对照表（关联分析）

| 论文术语 | 通俗解释 | Hermes 语境 |
|---------|---------|------------|
| OPD (On-Policy Distillation) | 学生用自己的轨迹，教师在 token 级指导 | delegate_task 的 on-policy 版本 |
| GRPO | 一种 RL 后训练方法 | 当前的 self-evolution 脚本 |
| Mutual Information | 区分通用 vs 特定知识 | skill 的通用性评估 |
| MOPD | 多教师 OPD | 多猫辩论决策 |
| World Model (CoT 状态转移) | 模型对环境的内部表征 | AGENTS.md 的协作心智模型 |
| Substrate-local promotion | 在本地基底上提升 | 各 skill 的本地验证 |

## 六、论文索引

| 论文 | arXiv | 日期 | 核心贡献 |
|------|-------|------|---------|
| Physics of Multi-Turn Long-Horizon Planning | 2607.24720 | 2026-07-27 | 三阶段规划能力框架 |
| MAD-OPD | 2605.01347 | 2026-05-02 | 多教师辩论蒸馏 |
| Structured Distillation for Agent Memory | 2603.13017 | 2026-03 | 11x token 压缩记忆蒸馏 |
| Knowledge-Based Pull Requests | 2606.26721 | 2026-06 | Agent 知识协作工作流 |
| Claim-Level Auditability | 2602.13855 | 2026-02 | 深度研究 agent 可审计性 |

## 六、归纳总结

**一句话总结**：2026 年 Agent 蒸馏的两大突破——多教师辩论打破单教师天花板（MAD-OPD），首次系统性揭示长程规划能力三阶段（Physics of Planning），共同指向"多源 > 单源、on-policy > off-policy、一致方向 > 梯度强度"。

**五大核心发现**：
1. **多教师辩论 > 单教师复制**：MAD-OPD 6/6 配置第一，涌现集体智能超越任何单一教师
2. **OPD 比 GRPO 有效区域更宽**：低质量和长程设置下，on-policy 蒸馏提供更一致的更新方向
3. **次优轨迹在长程中致命**：错误在多步中复合放大，少量次优数据可严重损害性能
4. **蒸馏未见流程会损害已有能力**：强制整合冲突模式比不整合更差
5. **少量长程数据 > 大量原子技能**：组合泛化需要完整的端到端任务数据

## 七、关联分析

**与现有 Skill 的关联**：
- `agent-orchestration-pattern` skill：多 Agent 编排可借鉴 MAD-OPD 的辩论机制
- `subtask-lifecycle` skill：delegate_task 的 off-policy 问题，长任务不稳定可能与此有关
- `agent-reflection` skill：反思机制应增加"次优轨迹过滤"门控
- `agent-reflexion-workflow` skill：Reflexion 的自我反思可参考 MOPD 的模式兼容性分类

**与之前笔记的知识链**：
- `2026-07-25-Agent记忆两极.md`：记忆的选择性持久化 vs OPD 的参数内化是同一问题的两个面
- `2026-07-21-LLM自进化为何崩溃.md`：自合成数据信息增益问题 → Physics of Planning 的"次优轨迹损害"提供了微观机制
- `2026-07-20-多Agent何时有效.md`：信息瓶颈视角 → MAD-OPD 的多教师辩论恰好突破单教师信息瓶颈
- `2026-07-22-SupraCognitiveModes.md`：记忆路由架构 → MOPD 的三种模式兼容性（兼容/部分共享/冲突）可映射

---

*关联笔记*: `2026-07-25-Agent记忆两极.md` | `2026-07-21-LLM自进化为何崩溃.md` | `2026-07-20-多Agent何时有效.md` | `agent-orchestration-pattern` skill

#Agent蒸馏 #MAD-OPD #长程规划 #多教师蒸馏 #OnPolicyDistillation


## 相关笔记

- [HiSkill分层技能图](./2026-07-29-HiSkill分层技能图.md) — 分层技能图与经验复用
- [EarnedAuthority](./2026-07-28-EarnedAuthority.md) — Agent能力获取与授权
- [多Agent何时有效](./2026-07-20-多Agent何时有效-信息瓶颈视角.md) — 多Agent信息瓶颈视角
