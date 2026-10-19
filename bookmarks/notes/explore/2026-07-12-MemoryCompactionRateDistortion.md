# What to Keep, What to Forget: A Rate–Distortion View of Memory Compaction in LLMs and Agents

> **arXiv**: 2607.08032 | **日期**: 2026-07-09 | **作者**: Ashwin Gerard Colaco, Nada Lahjouji
> **领域**: LLM 推理优化 / Agent 记忆系统 / 信息论

---

## 核心问题与研究动机

LLM 和 Agent 面临一个共同的瓶颈：**记忆不够用**。模型权重之外，注意力 KV cache、长 prompt、循环状态、跨会话记忆——每个都在疯狂占用资源。四个独立的研究社区各自发展了压缩技术（KV eviction/quantization、prompt compression、architectural state、agent memory），但彼此几乎不交流。

**本文核心论点**：这四个方向的压缩本质上都是同一个问题——**率失真决策**（rate–distortion decision）：在资源预算约束下，保留什么信息、丢弃什么信息、以什么精度保留，以最大化下游任务效用。

---

## 方法论：统一形式化框架

### 核心公式

压缩方案是一个二元组 $(\mathcal{C}_\theta, \mathcal{U})$：
- **压缩算子** $\mathcal{C}_\theta: H \mapsto Z$：将历史信息 $H$ 压缩为紧凑表示 $Z$，满足 $\text{rate}(Z) \leq B$
- **使用算子** $\mathcal{U}$：消费 $Z$ 进行下游计算

**统一优化目标**：
$$\min_\theta \mathbb{E}_{(H,Q,Y)}[\ell(\mathcal{U}(\mathcal{C}_\theta(H), Q), Y)] \quad \text{s.t.} \quad \text{rate}(Z) \leq B$$

这是一个信息瓶颈问题：最大化 $I(Z; Y|Q)$，约束 $I(Z;H) \leq B$。

### 不可逆性下界

令 $I^\star(Q) = I(Y; H|Q)$ 为任务条件信息量。当预算 $B < I^\star(Q)$ 时：

$$P_e \geq \frac{H(Y|Q) - B - 1}{\log|\mathcal{Y}|}$$

**该下界对任何压缩记忆 $Z$ 均成立**——无论是 KV cache、gist 向量、循环状态还是 Agent 笔记存储。

### 三条直接推论

1. **低于信息需求必出错**：当 $B < I^\star(Q)$，所有层都必须犯错误，无架构特例
2. **压缩比依赖任务**：压缩比 $\propto 1/I^\star(Q)$。精确/多跳检索任务压缩性差，分类/冗余摘要压缩性好——这就是同一个 KV evictor 在摘要任务上几乎无损、在检索任务上崩溃的原因
3. **查询无关的代价**：查询无关算子的有效预算约 $B - H(Q)$；查询条件算子可全额使用 $B$。差距 $H(Q)$ 就是不知道查询的精确代价

---

## 七轴分类法

论文提出七个正交维度分类所有压缩方法：

1. **压缩粒度**：bit → rank → token → page → layer → NL span → soft token → recurrent state → semantic item → visual token → inter-agent message
2. **生命周期阶段**：预训练 → prompt/prefill → prefill-to-decode → decode-time → serving → within-task → between-task → offline indexing
3. **损失性与保真度**：无损 / 近无损 / 均匀有损 / 多保真度（小型高保真层 + 大型有损层）
4. **查询/任务自适应性**：查询无关离线缓存 / 查询条件在线 / 任务感知学习
5. **可学习性**：无训练启发式 / 后训练适配器 / 从头训练架构 / RL学习策略 / LLM-as-controller
6. **机制**：evict / select-retrieve / merge / quantize / factorize / summarize / encode-to-latent / recurrent write-forget / structure / internalize
7. **存储介质**：On-GPU KV / host-SSD-remote / parameters / external text+vector / knowledge graph / in-context dense / hybrid

**核心发现**：层间差异集中在三个维度——**粒度、生命周期、查询自适应**。

---

## 四层压缩全景

### 第1层：KV-Cache 压缩（§4）

六个子方向：
- **Token Eviction**（不可逆丢弃）：H2O、SnapKV——按累积注意力分数 evict
- **Dynamic Sparse Retrieval**（全保留选择性读取）：Quest——永不 evict，按查询检索
- **Quantization**：KIVI——2-bit/4-bit 存储
- **Low-Rank**：MLA (DeepSeek)——低秩分解 KV
- **Cross-Layer Sharing**：跨层共享 KV
- **Cross-Cutting Tensions**：量化 × 低秩 × evict 的组合效果

### 第2层：Context/Prompt 压缩（§5）

- **Hard compaction**：LLMLingua（基于困惑度的 token 剪枝）、gisting（NL span → 学习的"gist"向量）
- **Soft compaction**：学习潜在表示替代文本 span

### 第3层：架构级有界状态（§6）

- Mamba/SSM：固定大小状态压缩全部历史
- 循环写-忘机制：参数化记忆

### 第4层：Agent 语义记忆压缩（§7）——最长时间尺度

这是与 Hermes Agent 最直接相关的层。

**第一族：任务内轨迹压缩**
- **MemGPT/Letta**：操作系统分页隐喻，LLM 窗口=主存，外部存储=磁盘
- **ACON**：失败驱动的压缩准则迭代优化
- **Context-Folding**（FoldGRPO）：分支子任务→折叠中间步骤→只留结果摘要
- **MEM1**：常数大小内部状态，每轮重写合并
- **ReSum**：周期性摘要工具压缩搜索历史
- **IterResearch**：每轮从核心输出重建工作空间

> 报告 3-10× 活跃上下文缩减，但全部不可逆折叠/剪枝/重写——**结构风险**：策略判定不重要的细节永久丢失。

**第二族：跨任务记忆固化**
- **Generative Agents**：时间戳+重要性+相关性评分的记忆流，周期性合成高层反思
- **Reflexion**：失败后写语言自批评，下一轮前置
- **ExpeL**：成功/失败轨迹对比提炼 NL 洞见
- **Mem0**：extract-then-update，ADD/UPDATE/DELETE/NOOP 操作
- **A-MEM**：Zettelkasten 风格原子笔记，动态链接自组织
- **MemoryBank**：Ebbinghaus 遗忘曲线衰减
- **MIRIX**：六类型模块（core/episodic/semantic/procedural/resource/knowledge-vault）

> **核心病理**：错误反思或过度泛化规则被存储后，会偏置每次未来检索——这是 Agent 级别的"evicted needle"类比，但更糟：Agent 不仅丢失好记忆，还会按需重建坏记忆。

---

## 推理 ↔ Agent 记忆桥接（§10）——核心创新

### 三层记忆层次

1. **KV Cache**：亚秒级，GPU 上，近无损，token 粒度
2. **工作上下文**：任务跨度内，context window 中，轨迹+工具结果
3. **长期存储**：跨会话，外部语义存储

> 三层跨越多个数量级的时间尺度，但都回答同一个公式：在预算下保留未来查询需要的信息。

### 五个共享设计旋钮

| 旋钮 | KV Cache 层 | Agent 长期记忆层 |
|------|-------------|-----------------|
| 重要性信号 | attention score | LLM-judged salience |
| 遗忘机制 | sliding window / eviction | decay curve |
| 查询条件 | per-query pages | recall-time retrieval |
| 可逆性 | keep-all vs evict | archive vs summarize |
| 停止规则 | output-error bound | **（空白——研究机会）** |

### 三个跨层移植案例

1. **MemoryBank 遗忘曲线 → KV evictor 先验**：H2O 纯按注意力 evict 偏向早期 token，加入基于重访统计的衰减先验作为替代评分
2. **Quest 无 evict 检索 → Agent 记忆设计**：Agent 在召回时从归档存储检索（可逆+查询条件）优于急切摘要
3. **Ada-KV 输出误差界 → Agent 摘要停止规则**：不再按固定计划压缩，而是压缩到诱导输出误差的有界估计

### 五条压缩感知设计原则

**P1. 永不不可逆地丢弃你无法廉价重建的内容**
- 可逆算子弱优于不可逆算子（等预算下，只在被丢弃证据的查询上有差异，可逆的赢）
- Quest 遵循 P1；H2O 和固定计划摘要违反它

**P2. 条件化于查询分布，而非仅当前查询**
- 查询无关算子被收取 $H(Q)$ 的熵代价
- 可训练稀疏注意力和查询感知压缩代价更低

**P3. 分离廉价可逆情景层与有损语义层**
- 多保真度记忆优于单一有损层：便宜可恢复地保留原始情景，只抽象证明可复用的
- MIRIX 类型模块和 Compressive Transformer 双层就是这样设计的

**P4. 使压缩异步且可学习，而非阻塞启发式**
- 当"决定保留什么"本身是关键路径上的 LLM 调用时，它侵蚀了它买入的节省
- RL 学习策略和 sleep-time 整合将决策移出关键路径

**P5. 独立测量每个轴的预算**
- 没有基准同时保持一个预算轴穿过所有层并测量重复压缩

---

## 关键实验结果

### 实验1：统一精度-预算前沿

- **设置**：Qwen2.5-1.5B-Instruct，RTX 4060 8GB，needle-in-a-haystack 检索
- **方法**：SnapKV、StreamingLLM、TOVA、Knorm、expected-attention、random-eviction，各5个预算点
- **结果**：1395 次生成。满缓存准确率 1.00；预算低于约 1/4 时**所有方法趋近零**
- **关键发现**：预算低于任务信息需求 $I^\star(Q)$ 时，没有任何评分器能恢复答案——公式(2)的精确预测

### 实验2：重复压缩下的误差累积

- **设置**：Agent 分块阅读长文档，累积12个KV事实，周期性压缩工作记忆
- **可逆算子**：归档全部 chunk，查询时检索（Quest/MemGPT-archival 纪律）
- **不可逆算子**：用 LLM 摘要覆盖工作记忆
- **结果**：可逆算子 recall 维持 ~0.95；不可逆算子在 0.33-0.56 之间
- **关键发现**：**单轮 needle 测试无法区分两个算子**——只在重复压缩时差距才显现。相同平均预算下差距约 0.5 recall。

---

## COMPACT-Bench 提案（§13）

现有基准的两大缺陷：
1. **预算轴不统一**：KV 报 GPU bytes，prompt 报压缩比，recurrent 报状态维度，agent 报存储大小——单位永不对齐
2. **未测量重复压缩**：当前所有 suite 只测单轮长上下文的固定质量比率，Agent 实际所处的"重复压缩"体制完全未测

COMPACT-Bench 的三个组件：
- **统一预算轴**：bytes-per-token-of-history (BPT)，所有方法在同一标尺上比较
- **能力测量**：方法是否知道它丢弃了什么、能否取回、信心是否反映保留内容
- **重复压缩测量**：跨多次压缩事件追踪误差累积

---

## 创新点分析

1. **统一形式化**：首次用单一率失真目标 + 可证明下界统一四个独立社区的工作，而非描述性分组
2. **跨层可移植性**：KV eviction 的 attention score 和 Agent memory 的 LLM salience 被识别为同一个量的不同估计器，使设计跨层可移植
3. **失败模式的统一诊断**：查询无关 + 不可逆 = 所有层的共同失败根源，由同一个下界预测
4. **COMPACT-Bench**：填补重复压缩测量空白，且在统一预算轴上使异构方法可比
5. **五条设计原则**：直接从形式化推导，每条附带预测的失败模式

---

## 局限性与未来方向

### 论文自述局限
- 这是综述：提出形式化和基准协议但未提供大规模实证验证
- 下界假设查询无关算子的最简形式，$I^\star(Q)$ 对真实任务的估计本身是开放问题
- "算子代数"是经验组合图而非已证定律
- 参考实验在小规模运行（小模型+单GPU），绝对数字应视为方法论说明而非排行榜

### 七大开放问题
1. **查询条件+可逆+多保真度的全层压缩**（最高杠杆）
2. **信息损失归因与校准压缩置信度**
3. **堆叠算子的组合图**（量化×低秩×evict 的协同/冗余/冲突）
4. **预测性压缩标度律**（$I^\star(Q)$ 的估计公式）
5. **情景→语义固化桥与停止规则**
6. **廉价、异步、RL 稳定的 Agent 自策展**
7. **多模态×多智能体共享记忆压缩**

---

## 借鉴点评估

### 🔨 P0：可逆记忆架构（直接关联 Hermes）

**论文原则 P1 + P3 与 Hermes 当前实践高度相关**：
- Hermes 的 `memorygraph` 记忆系统目前是 ADD/UPDATE/DELETE 操作（Mem0 模式）——**不可逆**
- 论文实验证明：不可逆算子在重复压缩下 recall 仅 0.33-0.56，可逆算子维持 0.95
- **建议**：为关键记忆（USER.md、核心技术决策）实现 archival tier——删除操作前归档原值，支持 rollback。借鉴 MemGPT 分页模型：context window = 主存，外部 JSONL = 磁盘

### 🔨 P1：查询条件检索替代急切摘要

**论文原则 P2 + Quest 移植案例**：
- Hermes 的 `context-compressor` skill 当前做急切摘要——查询无关
- 论文证明：查询无关算子被收取 $H(Q)$ 熵代价
- **建议**：在工具输出压缩时，延迟摘要到查询时——先存储完整工具输出（带索引），按查询关键词检索相关片段，而非预摘要。这与 `hybrid-search` skill 方向一致

### ⚠️ P2：压缩停止规则

**论文 Ada-KV 界 → Agent 摘要停止规则**：
- Hermes 当前按固定阈值/计划触发记忆压缩——无停止规则
- **建议**：引入输出误差估计作为停止信号——当压缩诱导的估计误差超过阈值时停止进一步压缩

### ⚠️ P2：异步整合替代关键路径压缩

**论文原则 P4**：
- Hermes 的 `memory-refiner` 在对话中同步调用 LLM 策展记忆——侵蚀节省
- **建议**：将记忆策展移到 `idle-busy-loop` 的后台阶段（已有 `sleep-time` cron），与 `auto-memory-keeper` 整合

### ❌ P3：率失真下界实证

- $I^\star(Q)$ 对真实任务的估计是开放研究问题
- 对 Hermes 规模的系统暂不适用，但理论框架值得记录到 `memory-consolidation` skill 中

### 📝 概念借鉴：三性质检查清单

为 Hermes 记忆系统增加三性质审计（可加到 `memory-consolidation` skill）：
- **(P-rev) 可逆性**：这条记忆删除后能否重建？如果不能，是否值得保留原始记录？
- **(P-q) 查询条件**：这条记忆的保留决策是否考虑了未来可能的查询？
- **(P-fid) 保真度**：这条记忆是精确记录还是摘要？是否需要多保真度分层？

---

## 关联论文

- **MemGPT/Letta** (Packer et al., 2024) — Agent 记忆 OS 分页模型
- **Quest** (Tang et al., 2024b) — KV cache 无 evict 查询条件检索
- **Ada-KV** (Feng et al., 2025) — KV eviction 输出误差界
- **MemoryBank** (Zhong et al., 2023) — Ebbinghaus 遗忘曲线 Agent 记忆
- **MIRIX** (Wang and Chen, 2025) — 六类型记忆模块
- **Context-Folding** (Sun et al., 2025b) — FoldGRPO 轨迹折叠
- **A-MEM** (Xu et al., 2025) — Zettelkasten 原子笔记自组织网络
- **COMPACT-Bench** — 本文提出的统一压缩评估基准（扩展 SCBench + KVPress）
- **NoLiMa** (Modarressali et al., 2025) — 词汇匹配探针高估模型能力
- **EM-LLM** (Fountas et al., 2025) — KV cache 分割为情景事件并检索，推理-记忆桥接的实证标志

## 相关笔记

- [Kara: KV Cache 压缩](./2026-07-04-Kara-KVCache压缩.md) — KV eviction 实证方法
- [KV Cache 量化压缩：TurboQuant/RotorQuant](./2026-07-05-KVCache量化压缩-TurboQuant-RotorQuant.md) — 量化方向压缩技术
- [GLM-5.2 架构：IndexShare 长上下文](./2026-07-03-GLM-5.2架构深度解析-IndexShare长上下文.md) — 长上下文架构优化
- [Agent 记忆系统 2026](./2026-07-03-Agent记忆系统2026-四模块框架与MAGMA多图架构.md) — Agent 跨会话记忆框架
