# Agent 在线 KV Cache 压缩：代理查询选型实证研究

> **来源**：arXiv 2608.00902
> **原文链接**：https://arxiv.org/abs/2608.00902
> **作者**：Yujian Liu, Jiabao Ji, Li An, Rohit Jain, Gungor Polatkan, Siyu Zhu, Shiyu Chang
> **记录日期**：2026-08-04

**标签**：#KV-Cache压缩 #LLM-Agent #推理优化 #token-eviction #attention-matching

---

## 一、内容详细整理

### 1.1 核心问题：Agent 场景下 KV Cache 为何需要"在线"压缩

LLM Agent（代码编写、深度研究、网页浏览、个人助手）的核心能力来自持续维护上下文——推理步骤、工具调用、环境反馈不断追加。但这造成了一个直接的推理瓶颈：**KV Cache 随轨迹增长而膨胀**，成为显存占用的主要来源和每步解码成本的决定因素。

> **静态压缩 vs 在线压缩的本质区别**：
> - 静态：完整上下文在生成前可用，可离线采样真实查询信号做 query-aware 压缩
> - 在线：信息逐步到达，**压缩时未来相关性未知**，且**压缩必须在推理路径内完成**（延迟预算极紧）

论文聚焦两个关键约束：
1. **未来相关性不可观测**：当某个 turn 被压缩时，若干 turn 之后才需要的信息可能与当前 turn 或紧接的下一个 turn 关注的内容完全不同
2. **延迟预算极紧**：额外 rollout、长合成续写、梯度优化在离线可行，但在 Agent 推理路径内会叠加严重延迟

### 1.2 方法论：两大压缩族 × 三种代理查询源

论文不提出新算法，而是系统隔离**压缩器放入 Agent 循环后的哪些选择最重要**。

**两大压缩族**：

- **Token Eviction (TE)** — 纯选择方法：用代理查询 Q 对每个缓存位置打分（root-mean-square attention mass），保留得分最高的 m 个位置的**原始 K/V**，不做任何修改
- **Attention Matching (AM)** — 同样的 key 选择，但额外拟合加性偏置 β 和重建值 V_C，使压缩后注意力输出尽量匹配全缓存的注意力输出（两阶段优化：先拟合 β 使选中 key 吸收未归一化注意力质量，再拟合 V_C 匹配注意力输出）

> **核心差异**：TE 承诺保留原始 KV 不变（纯选择），AM 保留选中 key 但允许调整注意力偏置和值（拟合优化）

**三种代理查询源**（从便宜到贵）：

- **❶ Boundary queries（当前轮）** — 提取结构性结束/过渡 token 的 query 向量（如 Qwen3.5 的 `<|im_end|>` token），零额外前向传播，极低成本
- **❷ Repeat-prefill queries（当前轮）** — 受 KVzip 启发，在已完成内容后追加重建提示，teacher-force 模型重复刚完成的 turn，从重复内容的 query 向量提取代理信号
- **❸ Future-generation queries（延迟 k 轮）** — 推迟压缩 k 轮，用 Agent 自身后续轮次生成时产生的真实 query 向量作为代理信号

### 1.3 实验设置

- **基准**：BrowseComp-Plus（固定语料深度搜索，答案可验证）+ WideSearch（开放网络广度搜索，原子事实收集组织成表格）
- **模型**：Qwen3.5 和 Gemma-4（均为 hybrid attention 模型，只压缩 full-attention 层）
- **规模**：4B（主实验）→ 27B/31B（服务效率分析）
- **评判**：Qwen3.5-397B judge 模型
- **压缩比**：主实验固定 0.2（每个可压缩段缩减到原始长度的 20%）

### 1.4 关键实验结果

**Table 1 核心发现（压缩比 0.2，4B 模型）**：

代理查询选型对性能影响巨大：
- 无压缩基线 BrowseComp-Plus：Qwen3.5-4B 46.00% / Gemma-4-E4B 33.00%
- **立即压缩（repeat-prefill）严重掉分**：Qwen3.5-4B 32.75%（TE）/ 31.25%（AM），Gemma-4-E4B 仅 9.00%（TE）/ 11.25%（AM）
- **Boundary queries 大幅挽回**：Qwen3.5-4B 从 32.75% → 45.25%（TE-boundary），接近无压缩
- **延迟 1 轮的未来查询效果最佳**：四个模型×基准组合中，延迟查询在三个组合中优于所有当前轮代理

> **TE 对不完美代理更鲁棒**：尽管 AM 设计更精巧（拟合 β 和 V_C），TE 在代理质量下降时性能衰减更小。论文认为原因在于 TE 的纯选择机制对代理噪声不敏感——选错位置也比"选对位置但拟合出错误值"更安全。

**更多代理源 ≠ 更好**：
- 对 TE，三种代理源组合（future + boundary + tool-response）与单种性能差距 ≤2 分
- 对 AM，添加 repeat-prefill 和 tool-response 作为优化目标无可靠增益
- **结论：只要 future assistant generation 可用，TE 不需要额外代理源**

**压缩改变 Agent 行为**（重大发现）：
- Qwen3.5-4B 在压缩下显著延长轨迹：BrowseComp-Plus 中位数从 20 轮 → 30-39 轮
- Gemma-4-E4B 轨迹长度基本不变
- 搜索查询重复率上升：TE-boundary 的 nearest-neighbor 相似度从 0.72 → 0.78，重复率从 11.7% → 21.3%

> **行为补偿假说**：Qwen3.5-4B 通过额外搜索和重复查询来补偿被压缩弱化的上下文，从环境中"找回"信息。这意味着压缩后保持的准确率部分来自行为适应，而非纯粹的信息保真。

**大模型服务效率（Table 2，BrowseComp-Plus，27B/31B）**：
- Qwen3.5-27B：峰值 KV 从 612.9K → ~175K tokens（3.5× 压缩），批处理从 8 → 32，吞吐 217 → 918（AM）/ 717（TE）queries/hour（4.2×/3.3× 提升）
- Gemma-4-31B：峰值 KV 从 272.1K → 99.6K（AM）/ 121.3K（TE），批处理 8 → 16，吞吐提升 1.7×/1.5×
- 两个大模型上 TE 和 AM 的准确率几乎无损（Qwen3.5-27B：无压缩 52.50% vs TE 52.00% vs AM 51.00%）

### 1.5 结论与局限性

**核心结论**：代理查询选择是实用在线 KV 压缩的核心设计选择。延迟使用 Agent 自身未来生成查询比任何当前轮代理都更有效，而简单 TE 在不完美代理下比复杂 AM 更鲁棒。

**三大局限性**：
1. 仅覆盖搜索/文档阅读类 Agent 任务，未覆盖代码编辑、GUI 控制、状态变更任务（未来相关性结构不同）
2. 仅研究低成本在线代理源，未探索额外 rollout / 学习型压缩器 / 梯度优化（更大延迟预算下可能更强）
3. 评估固定压缩比和延迟窗口，未研究自适应策略（根据内存压力、轮次长度、工具类型、不确定性动态选择压缩时机和力度）

---

## 二、查询拓展

### 2.1 Token Eviction vs Attention Matching 的理论背景

TE 属于 query-aware eviction 方法族，代表性工作包括 SnapKV (Li et al., 2024) 和 PyramidKV。核心思想是用注意力质量（attention mass）作为 token 重要性的代理指标。AM 则源于 KVzip (Zweiger et al., 2026) 和 StreamingLLM 的注意力偏置优化思路——不是简单丢弃，而是重建一个"等效"的短缓存。

### 2.2 Hybrid Attention 模型架构

Qwen3.5 和 Gemma-4 都是 hybrid attention 模型——部分层使用 full attention，部分层使用 sliding window attention 或 recurrent 结构。论文只压缩 full-attention 层，因为非 full-attention 层（如 Mamba-style state）本身就有固定大小的状态，不需要压缩。这与 Hermes Agent 生态中关注的 MLA（Multi-head Latent Attention）和 MHA→MLA 迁移方案直接相关。

### 2.3 BrowseComp-Plus 与 WideSearch 基准

BrowseComp-Plus 源自 Anthropic 的 BrowseComp 深度搜索评估，要求 Agent 迭代检索固定语料库获取证据，答案可验证。WideSearch 来自 Cohere/Wong et al.，要求广泛收集原子事实并组织成表格，衡量信息完整性（item-level F1）。两个基准互补：一个测深度推理，一个测广度覆盖。

---

## 三、归纳总结

### 3.1 在线 KV 压缩设计空间全景

```
┌─────────────────────────────────────────────────────┐
│            在线 KV Cache 压缩设计空间                 │
├─────────────────────────────────────────────────────┤
│                                                     │
│  维度1: 压缩算法族                                   │
│  ├── TE (Token Eviction) ─── 纯选择, 保原始KV        │
│  └── AM (Attention Matching) ─ 选key + 拟合β+V_C    │
│                                                     │
│  维度2: 代理查询源 (Proxy Query)                     │
│  ├── 当前轮 (delay=0)                               │
│  │   ├── ❶ Boundary ── 结构token的query向量          │
│  │   └── ❷ Repeat-prefill ── teacher-force重复       │
│  └── 未来轮 (delay=k)                               │
│      └── ❸ Future generation ── Agent自身后续查询     │
│                                                     │
│  维度3: 压缩比 (compaction ratio)                    │
│  ├── 0.1 (激进, 10x压缩)                            │
│  ├── 0.2 (推荐, 5x压缩, 精度基本无损)                │
│  └── 0.4 (保守, 2.5x压缩)                           │
│                                                     │
│  维度4: 延迟窗口 (delay window)                      │
│  ├── 0 (立即压缩, 信息丢失风险高)                    │
│  ├── 1 (推荐, 1轮延迟, 精度大幅恢复)                 │
│  ├── 3 (更多上下文, 边际递减)                        │
│  └── 5 (最完整, 但显存峰值更高)                      │
│                                                     │
└─────────────────────────────────────────────────────┘
```

### 3.2 TE vs AM 决策框架

- **TE 更优场景**：代理质量不可靠 / 在线延迟敏感 / 模型行为补偿能力强 / 跨越多种任务需要鲁棒性
- **AM 更优场景**：代理查询质量高（有真实未来查询）/ 离线压缩 / 精确注意力匹配至关重要
- **通用推荐**：delay=1 future-generation + TE，压缩比 0.2

---

## 四、趋势判断

### 趋势1：Agent 推理的"行为补偿"效应将成为评估新维度

论文揭示压缩不只影响注意力近似质量，还**改变了 Agent 与环境的交互模式**（更多搜索、更多重复查询）。这意味着评估压缩方法不能只看准确率和内存节省，还必须看**轨迹长度变化、工具调用频率变化、查询重复率变化**。预计未来 Agent 压缩基准会纳入行为指标。

依据：Table 3 明确显示 TE-boundary 的搜索查询重复率从 11.7% → 21.3%，Qwen3.5 轨迹长度翻倍。

### 趋势2：延迟压缩（delayed compaction）将成为在线压缩标配

当前轮代理（boundary / repeat-prefill）无法预见未来信息需求，延迟 1 轮即可大幅恢复精度。这个"用未来 1 轮的真实查询指导压缩"的思路简单而有效，预计会成为在线 KV 压缩的默认配置。

依据：四个模型×基准组合中三个组合，delay=1 优于所有 delay=0 方案。

### 趋势3：简单选择 > 复杂拟合，在线场景下 TE 将超越 AM

AM 的拟合优化（β 和 V_C）在静态离线场景下优势明显，但在在线场景中，代理噪声使拟合变得不稳定。TE 的纯选择机制天然抗噪。预计在线 Agent 压缩的主流方案会趋向 TE。

依据：TE 在所有四个组合中与 AM 性能差距 ≤2 分，且更稳定。

---

## 五、关联分析

### 5.1 与 KVarN-KV-Cache 量化后端的关联

KVarN 探索的是 KV Cache 的**量化压缩**（降低每个 K/V 的精度），而本文探索的是**结构压缩**（减少 K/V 的数量）。两者正交互补——可以同时用量化降精度 + eviction 降数量，实现双重压缩。KVarN 的量化误差和 TE 的信息丢失需要联合评估。

### 5.2 与"压缩模型保真度不等于安全"的关联

前序笔记（2026-08-03）指出压缩模型的保真度提升不等于安全性提升。本文提供了类似洞察：**压缩保真度 ≠ Agent 性能**——即使注意力输出近似匹配（AM 的目标），Agent 行为仍可能因信息微弱丢失而退化（更多搜索、更长轨迹）。评估压缩效果必须在端到端 Agent 任务上进行，而非仅看注意力重建误差。

### 5.3 与 MemDecay / Kara 区域感知压缩的关联

MemDecay (2607.10582) 和 Kara (2607.01237) 都探索区域感知的 KV Cache 管理——对不同语义区域（system prompt / scratchpad / tool response）施加不同的保留策略。本文的 boundary queries 实际上就是一种隐式的区域感知——利用结构 token（`<|im_end|>`）的注意力模式来识别重要信息区域，与 MemDecay 的 region base priority 异曲同工。

---

## 六、金句摘录

> 「Agent trajectories differ from static settings: an agent does not begin with a fixed document to compress; it gradually constructs its context through interactions with an environment.」— 点明在线压缩与静态压缩的本质差异

> 「TE is surprisingly robust to imperfect proxies and remains competitive with AM across proxy, delay, and compaction-budget choices.」— 简单方法在线上场景中超越复杂方法

> 「Online KV compaction should be evaluated not only by model-side memory savings and final accuracy, but also by how it changes the agent's interaction pattern with the environment.」— 呼吁新的评估范式

---

## 七、行动启示

- **P0 借鉴点 — Hermes Agent 长会话 KV 管理**：Hermes Agent 的长会话（论文精读、多轮搜索、cron 任务链）同样面临 KV Cache 膨胀。可借鉴论文的 delay=1 + TE + ratio=0.2 配置，在 Gateway 层面实现 turn-level KV eviction，预期降低 3-5× 峰值显存
- **P1 借鉴点 — Jetson 边缘部署**：Jetson Orin Nano 16GB 显存极为有限，长 Agent 轨迹容易 OOM。TE 纯选择方法零额外计算，特别适合边缘场景。boundary queries 方案可直接从模型中间层提取 query 向量
- **P1 借鉴点 — 行为补偿检测**：在 Hermes cron 监控中加入 Agent 行为指标（轨迹轮次、工具调用重复率），当检测到压缩导致的补偿性行为时发出预警
- **P2 借鉴点 — 自适应压缩策略**：论文 Limitations 中提到的"根据内存压力、轮次长度动态选择压缩时机"是未来方向，可在 Hermes Gateway 中实现基于内存水位的自适应压缩触发器


## 相关笔记

- [本地模型部署-oMLX_SSD-KV-Cache](./2026-08-04-本地模型部署-oMLX_SSD-KV-Cache.md) — SSD offload 方案，与本篇 token eviction 路径互补
- [推测解码2026-SSD并行化与EAGLE3实战](./2026-08-04-推测解码2026-SSD并行化与EAGLE3实战.md) — 推测解码与 KV 管理的协同优化
- [Kara-KVCache压缩](./2026-07-04-Kara-KVCache压缩.md) — KV Cache 压缩方法系
- [KVCache量化压缩-TurboQuant-RotorQuant](./2026-07-05-KVCache量化压缩-TurboQuant-RotorQuant.md) — 量化路线的 KV 压缩
- SSD-KV-Cache-oMLX-本地部署前沿（~/explore）— KV Cache 基础设施化趋势深度分析
