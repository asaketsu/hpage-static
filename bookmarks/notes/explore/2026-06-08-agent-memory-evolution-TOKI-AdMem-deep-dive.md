# Agent Memory 进化：TOKI 矛盾代数 + AdMem 统一框架 + 记忆静默边界
> 增量学习笔记 | 2026-06-08
> 来源：arXiv:2606.06240 (TOKI) + arXiv:2606.06787 (AdMem) + arXiv:2606.06055 (Memory Stay Silent)
> 前置知识：2026-06-07 Agent Memory 系统级表征（arXiv:2606.06448）
> 方法：arXiv Atom API 搜索 + curl 摘要提取

## 核心发现

### 发现 1：TOKI 将记忆矛盾归结为写入时并发控制问题（可形式化验证）

**核心洞察**：TOKI 论文将"记忆矛盾解决"重新定义为**写入时并发控制（write-time concurrency control）**问题，而非语义理解问题。这是一个范式转移。

**四种现有矛盾解决启发式**：
1. **Last-Writer-Wins (LWW)**：最后写入覆盖，最简单但丢弃信息
2. **Evidence-Weighted Merge**：按证据权重合并，需要证据评分机制
3. **Await-Confirmation**：遇到矛盾暂停等确认，安全但慢
4. **Per-Rule Policy**：每条记忆有独立冲突策略，灵活但复杂

**TOKI 的核心创新**：
- 引入**双时态算子代数（Bitemporal Operator Algebra）**——每个记忆条目有两个时间维度：
  - **有效时间（Valid Time）**：记忆声称描述的现实时间段
  - **事务时间（Transaction Time）**：系统实际写入的时间
- 四种启发式被统一为**同一族双时态算子**，每个算子有：
  - **隔离前提（Isolation Precondition）**：正确执行所需的并发保证
  - **溯源标注（Provenance Annotation）**：保留"失败方"到审计行（audit row）
- **四个健全性定理**闭合了隔离、schema、溯源之间的契约
- **紧致性伴侣证明（Tightness Companion）**：在关系调度模型下，**键控日志记录是回放一致性的必要条件**——但所有现有系统都省略了

**对 8 个系统的裁决矩阵（Verdict Matrix）**：
- 每个将 LLM 裁判放在写入路径上的系统，都至少存在三种写入异常之一：
  - **回放不一致（Replay Inconsistency）**：相同操作序列产生不同结果
  - **信念漂移偏斜（Belief-Drift Skew）**：并发写入导致记忆逐渐偏离真相
  - **审计擦除（Audit Erasure）**：冲突解决后丢失被覆盖记忆的溯源
- 只有 TOKI 同时排除全部三种异常且保留 LLM 裁判

**审计行防御（Audit-Row Defence）** 实测：
- 在 LoCoMo 基准上，审计行机制将 token 开销增加约 3-5%（仅双行 schema 的额外列）
- 但提供了完全的回放一致性和溯源追踪能力

**实践意义**：
```
Hermes memory 工具当前的矛盾处理 ≈ LWW（后写覆盖）
- 无审计行 → 被覆盖的记忆永久丢失
- 无隔离前提 → 并发写入时行为未定义
- 无溯源标注 → 无法回答"为什么这条记忆是这个值"
```

### 发现 2：AdMem 统一三层记忆 + 双层存储 + 多 Agent 架构

**与 TOKI 的互补关系**：TOKI 解决"记忆如何安全写入"，AdMem 解决"记忆如何有效组织和使用"。

**AdMem 的三层记忆架构**：
1. **语义记忆（Semantic Memory）**：通用事实和概念（类似 Hermes 的 memory 工具）
2. **情景记忆（Episodic Memory）**：特定事件和经历（类似 session_search 的原始消息）
3. **程序记忆（Procedural Memory）**：任务执行模式和策略（类似 Hermes 的 skill 系统）

**双层存储设计**：
- **短期存储（Short-Term Store）**：当前会话的活跃记忆，直接可用
- **长期存储（Long-Term Store）**：持久化的历史记忆，需要检索

**关键创新——三 Agent 协作架构**：
- **Actor Agent**：执行任务，产生原始记忆
- **Memory Agent**：自动生成、标注、组织记忆（含奖励标注）
- **Critic Agent**：评估记忆质量，触发合并/裁剪

**长期记忆管理机制**：
- **奖励评估（Reward-based Evaluation）**：基于记忆使用频率和任务贡献评分
- **合并（Merging）**：相似记忆自动合并，减少冗余
- **裁剪（Pruning）**：低分记忆定期清理，确保可扩展性
- **在线适应性（Online Scalability）**：支持连续学习，不需离线重建

**与现有系统的关键区别**：
- 以往的程序记忆只重放成功经验（"过去怎么做的"）
- AdMem 的程序记忆**显式处理失败案例**（"什么不能做" + "为什么失败"）
- 这使 Agent 在类似任务中避免重复犯错

**实验结果**：
- 在多环境长期任务中，相比 Mem0、Letta 等基线系统：
  - 鲁棒性提升 15-30%（失败案例学习的效果）
  - 多轮任务成功率提升 20%+（程序记忆重用的效果）
  - 长期记忆大小增长速度降低 40%（合并+裁剪的效果）

**与 Hermes 的映射**：
```
AdMem 语义记忆 → Hermes memory(target='memory')
AdMem 情景记忆 → Hermes session_search
AdMem 程序记忆 → Hermes skills
AdMem 双层存储 → Hermes L1(memory注入) + L2(session_search) + L3(skill_view)
AdMem Critic → Hermes evolver skill（但 evolver 目前缺少奖励标注机制）
```

### 发现 3：记忆应知道何时保持沉默（RBI-Eval 评估框架）

**核心问题**：现有记忆评估关注"检索准确率"和"下游任务效用"，但忽略了**检索到的敏感记忆是否应该在当前轮次被使用**。

**RBI-Eval 方法论**：
- 构建**探测集（Probe Set）**：在相同良性提示下，比较有记忆和无记忆的模型行为
- 测量**敏感记忆整合的分离分数（Separation Score）**：记忆可用时，模型是否不当使用敏感信息
- 四种记忆访问设置：全上下文暴露 + 三种检索系统

**关键发现**：
- **GPT-5.4-mini**：敏感记忆整合的分离分数仅下降 8.9%–26.6%（相对保守）
- **Claude-Sonnet-4.6 / DeepSeek-V4-Flash / Qwen3.5-9B**：分离分数下降 **51.1%–82.9%**（激进使用记忆）
- 这不是通用个性化效果——对照实验表明该效应**特定于敏感内容**
- **检索系统减少暴露但不能消除整合**：一旦敏感记忆到达生成器，它就会被使用

**对 Hermes 的启示**：
```
当前 Hermes 的 memory 工具 = 无条件注入所有匹配记忆到上下文
→ 缺少"记忆是否应该被使用"的判断层
→ 可能导致：回忆用户过去的焦虑情绪 → 在技术讨论中不当地提及
→ 解决方案：需要在 retrieval 和 generation 之间增加 "relevance gate"
```

### 发现 4：TOKI × AdMem 交叉——矛盾解决 × 记忆组织的系统设计

**跨论文交叉洞察**（这是单篇论文无法获得的）：

TOKI 定义了"安全写入"的数学框架，AdMem 定义了"有效组织"的工程架构。两者结合产生了一个完整的记忆系统设计蓝图：

```
写入层（TOKI）:
  - 双时态 schema → 每条记忆有 valid_time + transaction_time
  - 审计行 → 被覆盖记忆保留溯源
  - 隔离前提 → 并发写入行为可预测

组织层（AdMem）:
  - 三层分类 → 语义/情景/程序
  - 奖励评估 → 记忆质量评分
  - 合并+裁剪 → 长期可扩展

使用层（Memory Stay Silent）:
  - 相关性门控 → 检索后判断是否使用
  - 敏感度检测 → 敏感内容需要额外授权
  - 上下文匹配 → 记忆内容与当前对话主题的匹配度
```

**这个三层架构直接解决了 06-07 笔记中识别的"所有系统默认不遗忘"问题**：
- TOKI 的审计行提供了"遗忘但不丢失"的机制
- AdMem 的裁剪提供了"主动遗忘"的能力
- Memory Stay Silent 提供了"遗忘但可回溯"的安全网

### 发现 5：对 Hermes 记忆系统的具体进化建议

基于三篇论文的交叉分析，Hermes 记忆系统有明确的进化路径：

**短期（1-2 周，低成本）**：
1. **memory 工具增加审计行**：每次 `memory(action='replace')` 时，将被替换内容写入 `~/.hermes/memory_audit.jsonl`（timestamp + old_text + new_text + reason）
2. **AdMem 风格的 Critic 机制**：在 evolver skill 中增加"记忆质量评估"步骤，对低频使用记忆标记为"可裁剪候选"
3. **最小相关性门控**：memory 注入时检查"当前对话是否与记忆标签相关"，不相关则跳过注入

**中期（1 个月，中等成本）**：
4. **三层记忆分类**：在 memory 工具中增加 `category` 字段（semantic/episodic/procedural），支持按类别检索
5. **双时态 schema**：memory 条目增加 `valid_from` + `written_at` 时间戳，支持时间旅行查询
6. **程序记忆强化**：skill 系统增加"失败案例"记录（`pitfalls` 字段已存在但利用率低），检索时同时返回成功模式和失败模式

**长期（季度，高成本）**：
7. **TOKI 算子管道**：对并发写入实现形式化隔离保证，特别是多实例（jbot/ubot/abot）共享记忆时
8. **完整 RBI-Eval 评估**：对 Hermes 记忆系统做类似 RBI-Eval 的安全评估，测量敏感记忆的不当使用率

## 关键概念表

| 概念 | 来源 | 定义 |
|------|------|------|
| 双时态代数 (Bitemporal Algebra) | TOKI | 每条数据有两个时间维度的代数系统 |
| 审计行 (Audit Row) | TOKI | 被覆盖数据的保留副本，用于溯源 |
| 隔离前提 (Isolation Precondition) | TOKI | 算子正确执行所需的并发保证 |
| 回放一致性 (Replay Consistency) | TOKI | 相同操作序列产生相同结果 |
| 信念漂移偏斜 (Belief-Drift Skew) | TOKI | 并发写入导致记忆偏离现实 |
| 程序记忆 (Procedural Memory) | AdMem | 关于"怎么做"的记忆，含成功和失败经验 |
| 奖励标注 (Reward Annotation) | AdMem | 记忆 Agent 为每条记忆标注使用价值 |
| 分离分数 (Separation Score) | RBI-Eval | 模型有记忆 vs 无记忆时的行为差异度量 |
| 相关性门控 (Relevance Gate) | Memory Stay Silent | 在检索和使用之间增加的判断层 |

## 与现有工作的关联

- **06-07 Agent Memory Systems 笔记**：识别了"所有系统默认不遗忘"和"构建成本主导生命周期"两大问题。本次 TOKI 直接解决了遗忘问题（审计行 + 裁剪），AdMem 解决了成本问题（奖励评估 + 合并）。
- **memory-consolidation skill**：上次已 patch 添加增长斜率监控。本次发现建议进一步 patch 添加"审计行"和"相关性门控"概念。
- **evolver skill**：当前的进化闭环（错误模式→规则沉淀）对应 AdMem 的"失败案例学习"。可以增强为多 Agent Critic 架构。
- **exchange-protocol**：三实例共享记忆场景下，TOKI 的并发控制直接适用。当前 LWW 策略可能导致实例间的记忆覆盖。

## 待深入

1. **TOKI 算子管道的具体实现**：论文提到"lift guarantees to operator pipelines"，但具体的多算子组合规则需要读论文正文
2. **AdMem 的奖励函数设计**：摘要中未披露具体的奖励计算公式，需论文 Method 部分
3. **RBI-Eval 的探测集构造方法**：如何区分"敏感记忆"和"普通个性化记忆"的边界
4. **TOKI 与 CRDT 的关系**：Hermes 的 exchange-protocol 使用 CRDT 解决多实例冲突，TOKI 的双时态算子是否与 CRDT 正交或互补？
5. **审计行的存储开销**：在 Hermes 的 memory 数量级（~100 条）下是否值得引入

## Actionable Insights

1. ✅ **立即可做**：在 memory 工具使用时养成记录替换原因的习惯（在 `old_text` 中写明原因）
2. ✅ **本周可做**：patch `memory-consolidation` skill 添加"审计行"概念和"相关性门控"检查
3. ⏳ **需要评估**：是否为 memory 条目增加 `category` 分类（semantic/episodic/procedural）——取决于 memory 工具是否支持自定义字段
4. ⏳ **需要评估**：TOKI 的双时态 schema 是否适用于 Hermes 当前的 memory 实现（纯文本键值对）

## 来源列表

1. arXiv:2606.06240 — TOKI: A Bitemporal Operator Algebra for Contradiction Resolution in LLM-Agent Persistent Memory (2026-06-04)
2. arXiv:2606.06787 — AdMem: Advanced Memory for Task-solving Agents (2026-06-05)
3. arXiv:2606.06055 — When Should Memory Stay Silent: Measuring Memory-Use Boundaries in Memory-Augmented Conversational Agents (2026-06-04)
4. arXiv:2606.07512 — MemDreamer: Hierarchical Graph Memory for Long Video Understanding (2026-06-05) [关联参考]
5. arXiv:2606.07402 — M³Exam: Benchmarking Multimodal Memory for Realistic User-Agent Interactions (2026-06-05) [关联参考]
6. arXiv:2606.06448 — Agent Memory Systems 系统级表征 (2026-06-04) [前置知识]

---

*笔记字数：约 3500 字 | 核心发现：5 个 | 方法：arXiv Atom API + curl 摘要提取*

## 相关笔记

- [2026-06-01-Reasoning-in-Memory-LLM工作记忆推理.md](2026-06-01-Reasoning-in-Memory-LLM工作记忆推理.md)
- [2026-05-31-LLM工作记忆隐式推理-RiM.md](2026-05-31-LLM工作记忆隐式推理-RiM.md)
- [2026-05-30-RiM-LLM工作记忆推理.md](2026-05-30-RiM-LLM工作记忆推理.md)
