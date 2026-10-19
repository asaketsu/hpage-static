# Self-GC：长周期 LLM Agent 的自主上下文生命周期管理

> **来源**：arXiv
> **原文链接**：https://arxiv.org/abs/2607.00692
> **作者**：Xubin Hao, Hongjin Meng, Xin Yin, Jiawei Zhu, Chenpeng Cao
> **记录日期**：2026-07-03

**标签**：#LLM-Agent #上下文管理 #运行时优化 #garbage-collection #生产部署

---

## 一、内容详细整理

### 1.1 核心问题

长周期 LLM Agent 会积累大量结构化运行时数据——工具调用结果、文件内容、执行计划、用户约束。当前上下文管理面临一个尖锐的权衡困境：

- **基于位置/类型的启发式裁剪**（如 oldest-turn-fold、tool-prune）：成本低，但对未来依赖完全盲目。一条旧的工具输出可能持有后续步骤唯一需要的 URL、文件路径或表格值
- **接近上下文上限时的最终摘要**：保留了叙事状态，但把精确证据压缩成了散文，无法再被定位、审计或恢复

> **关键洞察**：Agent 上下文不是被动的 token 缓冲区，而是具有不同生命周期需求的运行时对象集合。有些对象已过时可删除，有些重复但需保留结构提示，还有些庞大但必须完全可恢复。

### 1.2 Self-GC 框架

Self-GC 的名称刻意呼应"垃圾回收"（Garbage Collection）——系统不仅回收无用 token，而是治理 Agent 上下文对象的生命周期。

**Harness 可移植接口**：只需在 Agent harness 与模型输入构建之间插入一个上下文引擎钩子，不需要重写整个 Agent。Harness 需要暴露的能力：
- 识别对话轮次和工具跨度边界
- 分配稳定对象标识符
- 在每次模型调用前投影活跃视图
- 完整 transcript 始终保留在活跃视图之外供审计和恢复

**索引上下文对象**：
- `conversation:user:k` — 用户请求及其后续执行跨度
- `function:tool:n` — 可独立编辑的工具级跨度
- 助手轮次不是一等 GC 目标（它们通常包含连接性文本和工具调用信封），在相邻对象变化时由 harness 保留或标准化
- 对象 ID 由会话级单调分配器分配

**三种生命周期动作**（每个对象接收一个动作）：

> **Fold（折叠）**：将精确 payload 移到 sidecar 存储，在活跃视图中留下紧凑恢复指针。适用于生成的报告体等大体积内容——后续轮次可能需要精确引用或修订

> **Mask（遮蔽）**：保留对象结构边界提示，同时省略重复或低信号的中间内容。适用于重复的浏览器快照

> **Prune（修剪）**：从活跃视图移除过时内容，不保证可恢复。适用于失败命令日志

**反思式规划、预演与提交**：
- 当 token 压力、轮次边界或策略触发治理轮次时，Self-GC 分叉当前上下文前缀，附加 planner-only 指令
- Planner 看到索引对象，输出基于现有标识符的结构化计划
- Planner prompt 被写为对象-动作契约而非摘要 prompt——依次处理排除优先级、未来依赖、粒度、动作语义和合理性检查
- Harness 本地预演计划：解析目标、丢弃无效编辑、标准化重叠动作、生成投影活跃视图、估算 token 节省
- 计划在安全轮次边界提交：合并视图、修复父系血统到最近的存活祖先、持久化 sidecar、标准化 provider 消息
- **被拒绝的计划永远不会影响主 Agent 循环**——模型提供语义判断，harness 执行协议有效性、可恢复性和提交纪律

**可恢复性与缓存感知提交**：
- Fold 元数据作为控制平面提醒附加到相关用户消息，不是助手生成的散文
- 提交收益公式：`CommitBenefit ≈ N_future × (C - C') - L_cache_break - L_GC`
  - 在 token 节省、缓存失效惩罚和 GC 开销之间权衡

### 1.3 实验设计

**数据集构建**：
- 原始 trace 行数：15,141
- 触发压缩的 trace：9,075
- Production Suite 会话数：332（覆盖办公、浏览器、shell、web-fetch 工作流）
- Hard Set 会话数：33（最高工具压力案例，偏向浏览器/shell/web-fetch）

**在线分流规则**（生产监控）：
- Self-GC 组：账号 email 首字母 ≥ o
- 对照组：账号 email 首字母 < o
- 覆盖 context-gc（交互式聊天清理）和 skill-gc（长期技能状态修剪）

**评估指标**：
- **Pruning Rate（修剪率）**：活跃视图中被移除的 prefix token 比例
- **No-impact Rate（无影响率）**：保留上下文是否仍支持真实的未来续写——用 GPT-5.5 judge 检查精确 URL、路径、行值、任务标识符、可编辑体和源支持证据是否仍可用
- **Online Input Tokens（在线输入 token）**：生产流量下主 Agent 模型的平均输入 token

**Planner 配置**：
- 默认 planner：Qwen3.6-Plus
- 备选 planner：Qwen3.7-Max、GLM-5.1
- 离线 judge：GPT-5.5
- 压缩阈值：30%
- 最后轮次保留：强制

### 1.4 关键实验结果

**Hard Set（33 个高难度会话）**：

- Self-GC：修剪率 43.95%，无影响率 84.85% [69.08, 93.35]
- Oldest-turn：修剪率 63.45%，无影响率 66.67% [49.61, 80.25]
- Tool-prune：修剪率 67.93%，无影响率 69.70% [52.66, 82.62]
- Tool-mask+prune：修剪率 61.90%，无影响率 54.55% [37.99, 70.16]
- Hybrid：修剪率 69.87%，无影响率 57.58% [40.81, 72.76]

> **解读**：Self-GC 牺牲了部分修剪率（43.95% vs 基线 61-70%），但无影响率从基线的 54-70% 跃升到 84.85%——在关键任务中大幅减少了上下文裁剪导致的任务中断

**Production Suite（332 个生产会话）**：

- Self-GC (Qwen3.6)：修剪率 31.51%，无影响率 92.77% [89.47, 95.09]
- Self-GC (Qwen3.7)：修剪率 33.98%，无影响率 94.58% [91.59, 96.54]
- Self-GC (GLM-5.1)：修剪率 31.04%，无影响率 91.27% [87.74, 93.85]
- Oldest-turn：修剪率 40.19%，无影响率 87.46% [83.46, 90.60]
- Tool-prune：修剪率 47.76%，无影响率 77.71% [72.93, 81.86]

> **解读**：在更大规模的生产数据上，Self-GC 的优势更稳定——三个 planner backbone 都达到了 91-95% 的无影响率，而最强基线只有 87.46%

**在线生产效果**：
- 白天平均输入 token 降低 10-15%
- 峰值降低接近 20%
- 这是运营监控数据，非完全随机化质量实验

### 1.5 失败模式分析

论文定义了五类固定启发式方法无法区分的依赖丢失模式：

- **证据细节丢失**：精确行值、SQL 过滤器、图表选择器、堆栈帧——未来轮次能继续叙事但无法复现或审计具体结果
- **定位器/句柄丢失**：文件路径、文档 ID、回调 URL、恢复路径——Agent 知道产物存在但无法重新打开或交付
- **行为契约丢失**：用户修正（如"不要替换表头"）、schema 规则、策略约束——后续编辑偏离请求规则
- **逐字源丢失**：原始措辞、引述、字段标签——摘要语义合理但无法回答恢复或精确复制请求
- **活跃状态丢失**：当前阻塞、修正后的重跑结果、最新成功交接——未来轮次缺乏当前进展状态

> **关键发现：工作负载不对称**。工具修剪在 BI 密集型会话中有竞争力（很多 dump 可重新查询），而按时间折叠在文档/代码密集型会话中更强（短工具输出常含唯一标识符）。Agent 从同一个位置/类型策略无法区分这些情况——这正是 Self-GC 的对象级规划优势所在

---

## 二、查询拓展

### 2.1 Context Window 压缩技术谱系

当前 LLM Agent 上下文管理主要有三条技术路线：
- **位置启发式**：按消息年龄/长度/类型裁剪（如 Claude Code 的 tool result masking、Cursor 的 conversation truncation）。简单但不感知语义依赖
- **LLM 摘要**：接近上下文上限时让模型生成摘要（如 MemGPT、ConversationSummaryBufferMemory）。保留叙事但丢失精确证据
- **结构化对象管理**：Self-GC 提出的新范式——将上下文建模为有生命周期的索引对象

### 2.2 Garbage Collection 比喻的深层含义

Self-GC 不是简单借用 GC 术语，而是真正映射了 GC 的核心机制：
- **可达性分析** → planner 判断对象是否为未来依赖（类似 GC root tracing）
- **标记-清理** → fold/mask/prune 三种回收策略（类似 GC 的不同回收算法）
- **安全点** → 安全轮次边界提交（类似 GC safe point）
- **分代回收** → 不同类型对象（user turn vs tool span）的差异化生命周期策略

### 2.3 Sidecar 模式

Sidecar（边车）来自微服务架构——主服务旁挂载辅助容器。Self-GC 中 sidecar 指：被 fold 的对象精确 payload 不在活跃上下文中，但存储在可寻址的旁路存储中，通过恢复指针可在需要时取回。这与 Hermes 的 `context-compressor` skill 中"大工具输出存储为文件，仅保留摘要预览"的模式高度一致。

### 2.4 AgentDiet / AgentFold / LongCodeZip

论文提到的同类方法（截至发表时未公开比较）：
- **AgentDiet**：可能是一种 Agent 上下文"节食"方案
- **AgentFold**：折叠式上下文压缩
- **LongCodeZip**：长上下文代码压缩

这些方法可能也在探索对象级管理，但 Self-GC 的差异化在于 harness 可移植性和 sidecar 可恢复性。

### 2.5 DeepSeek-V3.2 的上下文管理策略

论文引用 DeepSeek-V3.2 报告的 Search Agent 策略：Summary、Discard-75%、Discard-all——当 rollout token 使用超过上下文窗口大比例时触发。这些被 Self-GC 视为工业策略参考而非直接实验基线。

---

## 三、归纳总结

### 3.1 核心范式转变

```
传统范式: 上下文 = 线性 token 缓冲区 → 按位置/类型裁剪
Self-GC:  上下文 = 索引对象集合     → 按生命周期治理

关键区别: 从 "这个 token 够不够老可以删？" 
         到 "这个对象对后续步骤还有依赖吗？"
```

### 3.2 三层架构模型

```
┌─────────────────────────────────────────┐
│         Agent Harness (可移植)           │
│  ┌─────────────────────────────────┐    │
│  │   索引上下文对象层               │    │
│  │  conversation:user:k            │    │
│  │  function:tool:n                │    │
│  │  ↕ 稳定标识符 + 生命周期状态     │    │
│  └─────────────────────────────────┘    │
│  ┌─────────────────────────────────┐    │
│  │   Side-channel Planner (旁路)    │    │
│  │  输入: 分叉的上下文前缀           │    │
│  │  输出: 对象-动作契约 (非摘要)     │    │
│  └─────────────────────────────────┘    │
│  ┌─────────────────────────────────┐    │
│  │   Rehearsal + Commit (安全提交)  │    │
│  │  本地预演 → 验证 → 安全点提交     │    │
│  │  Sidecar 持久化 + 缓存感知       │    │
│  └─────────────────────────────────┘    │
│  ┌─────────────────────────────────┐    │
│  │   活跃视图 (Active View)         │    │
│  │  ← 投影后的紧凑上下文            │    │
│  │  完整 transcript 始终在外部保留   │    │
│  └─────────────────────────────────┘    │
└─────────────────────────────────────────┘
```

### 3.3 Planner 契约设计的五步决策规则

Planner prompt 不是自由摘要，而是结构化的对象-动作契约，按以下顺序决策：

1. **排除优先级**：什么必须保留（精确标识符、路径、URL、行值、查询字段、产物体、源支持证据）
2. **未来依赖判断**：哪些 live handles、job IDs、回调 URL、文件路径是必需保留锚点
3. **行为契约检查**：指令、策略、schema、任务契约读取——永不 GC 用户修正
4. **动作粒度选择**：工具级 fold 优于整轮 fold；仅 prune 废弃搜索/失败尝试
5. **合理性检查**：大量稳定体优先 fold 而非 mask（可能需幂等恢复）

---

## 四、趋势判断

### 趋势1：上下文管理将从"文本压缩"升级为"运行时对象生命周期控制"

依据：Self-GC 的生产数据显示，对象级管理的无影响率（91-95%）显著优于启发式（77-87%），且在线 A/B 确认 10-15% 的真实 token 节省。这表明工业界正在从"事后文本清理"转向"前置生命周期控制"。

### 趋势2：Side-channel Planner 成为 Agent 架构的标准组件

依据：Self-GC 的 planner 与主 Agent 完全解耦——它分叉上下文前缀，输出结构化动作计划，harness 负责验证和提交。这种"主 Agent + 旁路 planner"的双通道架构，与 Anthropic 的 Claude Code context window 管理、OpenAI 的 Codex memory 系统在设计哲学上趋同。

### 趋势3：可恢复性将成为上下文管理的硬约束

依据：Fold 动作的核心创新不是"移走大对象"，而是"移走后可精确恢复"。这直接解决了摘要方法的致命弱点——信息丢失不可逆。随着 Agent 任务复杂度增加，可恢复性（而非最大压缩率）将成为评价上下文管理系统的首要指标。

### 趋势4：生产验证将成为上下文管理论文的新标准

依据：Self-GC 不止做离线评估，还报告了在线账号级分流的实际 token 节省。DeepSeek-V3.2 也报告了类似的 Search Agent 策略。这意味着纯 benchmark 的上下文管理论文将越来越难发表——工业级生产验证正在成为门槛。

---

## 五、关联分析

### 5.1 与 Hermes Agent context-compressor skill 的关联

Hermes 的 `context-compressor` skill 当前实现的是 Self-GC 论文中的"策略 B"——"渐进式上下文压缩，大工具输出存储为文件，仅保留摘要预览在上下文中"。这对应 Self-GC 的 Fold 动作的部分功能。

Self-GC 的增量价值在于：
- **索引化**：Hermes 当前按文本块压缩，Self-GC 按对象 ID（`function:tool:n`）管理——可精确定位和恢复
- **三分法**：Hermes 只有"压缩 or 保留"二元选择，Self-GC 有 Fold/Mask/Prune 三种策略
- **Planner 契约**：Hermes 的压缩策略是固定规则，Self-GC 用 LLM planner 按未来依赖动态决策

### 5.2 与 context-engineering-patterns skill 的关联

Hermes 的 `context-engineering-patterns` skill 提到了四大支柱：静态/动态分离、对话历史管理、预算化检索、工具输出修剪。Self-GC 的框架直接实现了这四大支柱：
- 静态/动态分离 → 索引对象层（稳定 ID）vs 活跃视图（动态投影）
- 对话历史管理 → 三种生命周期动作 + sidecar 恢复
- 预算化检索 → 30% 压缩阈值 + cache-aware commit
- 工具输出修剪 → `function:tool:n` 对象的 Fold/Mask/Prune

### 5.3 与 evolver / agent-reflection 的关联

Self-GC 的 side-channel planner 本质上是一种"微型反思"——它不参与任务执行，而是审视当前上下文、判断哪些信息对后续有价值。这与 Hermes 的 `agent-reflection` skill（双轨反思机制）在设计哲学上一致：都是分离"执行"与"反思"两个通道。

---

## 六、借鉴点与可落实评估

### P0：对象级上下文索引（可立即实施）

**现状**：Hermes 的 tool result 和对话轮次没有稳定标识符，压缩时只能按文本块操作。
**借鉴方案**：在 Hermes 的 message 构建流程中，为每个 user turn 和 tool result 分配稳定 ID（如 `conv:user:3`、`tool:search:7`），写入 message metadata。压缩策略基于 ID 而非文本位置。
**工作量**：1-2 天（修改 message 构建 + 压缩逻辑）
**收益**：高——使上下文压缩可追溯、可恢复

### P1：Fold 动作 + Sidecar 文件恢复（可部分实施）

**现状**：`context-compressor` skill 已实现"大工具输出存文件"，但恢复机制不完善——存了之后取回的路径不可寻址。
**借鉴方案**：参考 Self-GC 的 sidecar 模式，为每个被折叠的工具输出生成恢复指针（文件路径 + 对象 ID + 内容摘要），在上下文中保留紧凑指针。
**工作量**：3-5 天
**收益**：中高——解决"压缩后信息不可恢复"的核心痛点

### P1：Planner 契约式压缩 prompt（可直接移植）

**现状**：Hermes 的上下文压缩用固定规则或简单的"总结这段对话"prompt。
**借鉴方案**：将 Self-GC 的 planner prompt 设计为结构化契约——按排除优先级、未来依赖、行为契约、动作粒度、合理性检查五步决策，输出 JSON 格式的 `{object_id: action}` 映射。
**工作量**：1 天（设计 prompt 模板）
**收益**：高——直接提升压缩质量，减少任务中断

### P2：缓存感知提交策略（需工程改造）

**现状**：Hermes 不考虑 KV cache 局部性，每次压缩都可能破坏前缀缓存。
**借鉴方案**：参考 Self-GC 的 `CommitBenefit` 公式，在 token 节省收益 > 缓存失效惩罚 + GC 开销时才提交压缩。
**障碍**：需要 provider 暴露 cache 命中信息（目前部分 provider 不支持）
**工作量**：1-2 周
**收益**：中——主要影响延迟敏感场景

### P3：安全轮次边界提交（暂不适用）

**现状**：Hermes 在任意时机触发压缩。
**借鉴方案**：只在用户轮次边界提交压缩结果，避免在工具调用中途修改上下文。
**原因**：Hermes 的工具调用模式（function calling）不像论文中的交互式 Agent 那样有明确的轮次边界——很多任务是单轮多工具调用。
**工作量**：需重新评估 Hermes 的会话模型

---

## 七、金句摘录

> 「Heuristics are cheap but blind to future dependencies; summaries preserve narrative state but often hide exact evidence, locators, and editable artifacts.」— 启发式廉价但对未来盲目；摘要保留叙事但隐藏精确证据

> 「Whether an edit is safe or harmful is therefore not decided by chronological position alone, but by whether an object will serve as a future dependency.」— 编辑是否安全不由时间顺序决定，而由对象是否是未来依赖决定

> 「Context management as runtime lifecycle control over indexed, recoverable objects rather than post hoc text cleanup.」— 上下文管理是对索引化可恢复对象的运行时生命周期控制，而非事后文本清理

## 相关笔记

- [Agent 记忆系统 2026 四模块框架](./2026-07-03-Agent记忆系统2026-四模块框架与MAGMA多图架构.md) — 记忆维护模块的理论框架
- [Agent 自进化：经验蒸馏进参数](./2026-07-05-Agent自进化-经验内化参数-EvoSC-MemSkill.md) — 经验内化减少上下文负担
- [LLM Agent 失败模式分类法](./2026-07-09-LLM-Agent失败模式综合分类法.md) — 上下文管理失效的失败模式
- [Tool-Making 自进化 Agent](./2026-07-11-ToolMakingSelfEvolving.md) — 低延迟系统中的上下文策略
- [Kara KV Cache 压缩](./2026-07-04-Kara-KVCache压缩.md) — 推理层 KV Cache 压缩（交叉：上下文优化）
