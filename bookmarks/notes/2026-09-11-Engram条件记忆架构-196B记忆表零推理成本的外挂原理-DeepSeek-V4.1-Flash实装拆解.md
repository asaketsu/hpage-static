# Engram 条件记忆架构：196B 记忆表零推理成本的外挂原理——DeepSeek V4.1 Flash 实装拆解 + N-gram 哈希查表机制 + 三层存储分层

> **来源**：X/Twitter @Michaelzsguo（Michael Guo）推文《DeepSeek V4.1 Flash 能把模型做到极致，离不开这项关键技术：Engram》2026-09-10（987 字全文直读）
> **原文链接**：https://x.com/Michaelzsguo/status/2098021103792734493
> **交叉验证**：deepseek-ai/Engram GitHub（4.6k stars，Apache 2.0，含 33 页论文 PDF）+ DeepSeek V4.1 Tech Report（HuggingFace）+ 量子位《DeepSeek V4最大的遗憾》+ Introl/VERTU 分析
> **抓取方式**：vxtwitter 全文 + web_search 四源交叉 + GitHub README
> **笔记日期**：2026-09-11
> **关联笔记**：《LLM八种精度格式全解》（FP8 表精度）《TTFT首字延迟全解》（预取-计算重叠）《Transformers即贝叶斯网络》（前几层重建静态关系的浪费）《自进化Harness与记忆》

---

## 零、结论先行

**Engram = 给 Transformer 外挂一张 196B 参数的"N-gram 哈希查表"，但每个 token 只查极少数条目（O(1)），推理几乎零成本——"让便宜的存储负责记住，让昂贵的 GPU 负责思考"。** DeepSeek V4.1 Flash 用它实现 748B 总参数（552B backbone + 196B Engram）却只激活 8B（prefill）/16B（decode）。这是与 MoE 正交的第二条稀疏轴：MoE 稀疏化计算（这次调哪些神经元），Engram 稀疏化存储（这次开哪几个抽屉）。推文基本准确，但有三处需校正（见 §六）。

## 一、问题：Transformer 没有"查表"原语

**核心观察（论文原命题）**：语言建模混着两种性质完全不同的任务——

| 任务类型 | 例子 | 传统 Transformer 的浪费 |
|---------|------|----------------------|
| 深度动态计算 | 组合推理 | 这是该 GPU 干的 |
| **检索静态知识** | 常见人名/固定表达/代码模式 | **前几层 Attention+FFN 每次运行时重新构建静态关系** |

论文的例子：识别 "Diana, Princess of Wales" 要走 6 层——前几层纠结"Wales 是地区"“Princess of Wales 是头衔"这些中间状态，最后一层才反应过来是戴安娜王妃。推文的类比更狠：**"就像每次看到一个熟人，都要重新分析一遍他是谁"**。量子位类比：做数学题，公式不必每次从头推，翻表代进去就行——Transformer 之前没这张表，只能每道题从公理走起。

## 二、机制：Engram 怎么查表（推文+论文+技术报告三源合并）

### 2.1 数据流（四步）

```
当前 token + 前几个 token
   ↓ 组成 N-gram（2/3/4-gram）
确定性 Hash（8 个 hash heads）
   ↓ 直接定位记忆表中少数几个 Embedding（O(1)）
门控 Gate（按当前上下文判断相关性）
   ├─ 相关 → 注入 Transformer 隐状态（与文本 embedding 联合处理）
   └─ 不相关 → 抑制掉（防 Hash 冲突/一词多义噪声）
```

**门控的价值示例**（量子位）："张"是常见姓氏，但"张仲景"三字凑一起是固定历史实体——门控负责识别这种区别。

### 2.2 V4.1 Flash 的实装参数（技术报告核对）

| 参数 | 值 |
|------|-----|
| Engram 总参数 | **196B**（均匀分给两个模块） |
| 插入位置 | **第 1 层和第 14 层**（早期层解除静态模式重建） |
| N-gram 阶数 | {2, 3, 4} |
| Hash heads | 8 个/阶 |
| 每阶 embedding 维度 | 2048 |
| 每头索引表 | ~16M 条目，**表大小取互异素数**（分布均匀性） |
| 精度 | **表与 KV 投影全 FP8** |
| 训练优化 | 动量更新 + Sinkhorn 平衡 |
| 并行 | 按行分区 engramparallel 组；优化器状态再分片 |

### 2.3 三层存储分层（推文最有价值的段落）

| 层 | 介质 | 内容 |
|----|------|------|
| 热层 | GPU HBM | 常用条目缓存 |
| 主表 | **CPU Host Memory（服务器 DDR / Apple Silicon 统一内存 LPDDR）** | 主要记忆表 |
| 长尾 | **NVMe SSD** | 冷数据 |

**卸载可行的根本原因：确定性寻址**——Engram 的地址完全由输入 token 决定，系统**提前知道需要哪些记忆** → GPU 算前几层 Transformer 的同时，CPU 已异步预取对应 Embedding，传输隐藏在计算里。**实测：100B 参数表放 Host Memory，额外性能开销 <3%**（论文）。

### 2.4 两条稀疏轴的正交性

| 轴 | 稀疏化什么 | 问句 |
|----|-----------|------|
| MoE | 计算 | "这次调用哪些神经元？" |
| **Engram** | 存储 | "这次打开哪几个抽屉？" |

推文的总结句：**"MoE 是条件计算，Engram 是条件记忆。"** 两者互补不冲突——V4.1 同时用了两者。

## 三、实证结果（论文+技术报告+社区）

### 3.1 论文级（Engram-27B，严格 iso-parameter/iso-FLOPs 对照）

| 指标 | 提升 |
|------|------|
| 知识/推理/代码/数学 | 一致 +3~5 分 |
| **Needle-in-a-Haystack** | **84.2% → 97%**（最惊人的一项） |
| 机制分析 | Engram 解放早期层免于静态模式重建，**为复杂推理保留有效深度** |

### 3.2 产品级（V4.1 Flash）

- 748B 总参（552B+196B）激活 8B/16B；**PD 不对称**（prefill 8B < decode 16B——Agent 时代输入远多于输出，降 prefill 算力=省成本，知乎刘延观点）
- Benchmark 超 DeepSeek V4 Pro；DeepSWE v1.1 得 74.2（接近 GPT-6 Astra/Claude Opus 5 的 ~74——**该基准接近饱和**）
- 1-100 整数连续可控推理强度
- 300+ TPS 有疯狂查表的功劳（查表算力远低于计算）

### 3.3 反直觉实验（量子位报道，值得记录）

论文发布第 11 天，TaoLin 单作者发《A Collision-Free Hot-Tier Extension for Engram-Style Conditional Memory》：把高频 N-gram 用 Minimal Perfect Hash **完全消除冲突**（无冲突热层+多头哈希冷层）——**严格 iso-parameter 下无稳定 loss 提升**。结论：哈希冲突不是瓶颈，门控聚合已消化它。*（很好的"显然的优化不成立"案例。）*

### 3.4 谱系（量子位考古）

- 2026-01-12：DeepSeek+北大 33 页论文《Conditional Memory via Scalable Lookup》（一作程鑫，末位作者**梁文锋**）
- V4 正式版**没用上**（"V4 最大的遗憾"）——首个实装的开源大模型是**阿里 Qwen Next 3.8**（表更小）
- V4.1 Flash 是 DeepSeek 自家首次大规模实装（196B，远超 Qwen）

## 四、与我们体系的全景对接

### 4.1 架构哲学的三重呼应

| Engram 原则 | 我们体系的对应 |
|------------|---------------|
| **计算/记忆/存储分离扩展** | 三级记忆架构（L1 铁律常驻/L2 短期/L3 topic 按需）——**同一个洞察的模型层与 agent 层实现** |
| 确定性寻址→可预取→异步隐藏传输 | 发布管线幂等链的前置计算；流式语音笔记"说话期间并行检索"同构 |
| 让便宜层干记住的活，贵层干思考 | L1 注入 <8K 字省 token；cache 友好的 prompt 三层（stable 左缘） |

**最深的连接**：Engram 论文的" relieving early layers from static pattern reconstruction"与 Transformers=BP 笔记的推论互证——**静态知识检索与动态推理混在一起是架构级浪费**，BP 视角下前几层重建的是"固定置信传播链"，本可以直接查表短路。

### 4.2 对量化/部署笔记的增量

- FP8 表精度（§2.2）是《LLM 八种精度格式》的实战补章：**embedding 表是 FP8 的理想负载**（静态、访问稀疏、容错高）
- "100B 表卸载 DRAM 开销 <3%"给 TTFT 笔记的访存瓶颈讨论加了正样本：**确定性寻址的负载天然适合预取**——与 SGLang 的 RadixAttention 前缀缓存（确定性前缀）同族

### 4.3 周论文选题钩子

今日记忆主题三连（mem0 三种写 → beamnxw 三级记忆 → Engram 条件记忆）形成完整光谱：**模型内记忆（Engram）— agent 文件记忆（Pin/SKILL.md）— 外部记忆系统（Mem0）**。选题候选：《记忆的三个层位：从 Engram 查表到 Agent 知识库的同构性分析》——三问检验：收敛（分层+稀疏访问共识）/矛盾（何时记忆进权重 vs 进文件）/空白（agent 层缺 Engram 式的"确定性寻址"——我们的 link_weaver 双门限是语义寻址，非确定性）。

## 五、批判性审视（推文三处需校正）

| # | 推文说法 | 校正 |
|---|---------|------|
| 1 | "查找复杂度接近 O(1)" | 准确但需限定：**每次查表是 O(K) 聚合**（K 个 hash head），对序列总量是每 token 常数次——工程上成立，数学上"接近"用得诚实 |
| 2 | "额外性能开销可以控制在 3% 以内" | 这是**论文中 27B/40B 规模的实验数字**，推文隐含这是 V4.1 生产数字——技术报告口径是集成 SGLang 端到端吞吐损失 <5%（量子位），**量级一致但数字不同** |
| 3 | "DeepSeek V4.1 Flash 能够变得更强…的重要原因之一" | "之一"用得诚实；但 196B 表的贡献无法与 CED 架构/CSA2 注意力重构分离——**单一归因是推文体裁的通病**，benchmark 提升是组合效果 |

其他：①"服务器 Host Memory 通常是 DDR"正确但 Engram 论文的 CXL 探索（量子位提及"为 CXL 量身定做"）推文没展开——CXL 内存池化是这个方向的产业走势；②Qwen Next 3.8 先于 DeepSeek 实装的事实推文未提（"DeepSeek 提出→DeepSeek 首用"的叙事省略了中间者）。

## 六、金句提取

> "**让便宜的存储负责'记住'，让昂贵的 GPU 负责'思考'。**"

> "MoE 是条件计算：这次调用哪些神经元。Engram 是条件记忆：这次打开哪几个抽屉。"

> "就像每次看到一个熟人，都要重新分析一遍他是谁。"（传统 Transformer 的浪费）

> "未来大模型的扩展，可能不再只是继续堆 GPU 和计算参数，而是把计算、记忆和存储彻底分开，各自扩展。"

> 论文摘要："While MoE scales capacity via conditional computation, Transformers lack a native primitive for knowledge lookup."

## 七、局限性

1. 推文 987 字为科普口径，参数细节以技术报告/GitHub README 为准（已交叉核对 §2.2）
2. 论文 PDF（33 页）未逐页精读——U 形 scaling law 的具体形式、Sinkhorn 平衡的推导未展开
3. V4.1 Flash benchmark 数字为官方口径（DeepSWE 74.2 有社区"接近饱和"的质疑背景）
4. TaoLin 反直觉实验为二手转述（量子位），原文未核
5. 4.1/4.3 节体系对接为本笔记扩展

## 出处标注

| 章节 | 来源类型 |
|------|---------|
| 一、二.1 | **推文忠实还原**（987 字全文） |
| 二.2-2.4 | **技术报告+GitHub 论文核对**（交叉源） |
| 三 | 论文 README + 量子位/知乎/Introl 多源 |
| 四 | **体系映射**（本笔记扩展） |
| 五 | **批判性审视**（三处校正为本笔记增量） |
