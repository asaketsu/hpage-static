# KV Cache 浪费与 PagedAttention 救赎：从 80% 浪费到 98% 利用率——vLLM 内存管理全链拆解 + 连续批处理/前缀缓存/推测解码/ disaggregated serving 演进

> **来源**：X/Twitter @vicky_grok（Vikas Gupta）Article《Your KV Cache Is Mostly Waste: How PagedAttention Fixed LLM Serving》2026-09-10
> **原文链接**：https://x.com/vicky_grok/status/2098385343439618151
> **原始论文**：arXiv:2309.06180（SOSP 2023，UC Berkeley，vLLM 团队）
> **抓取方式**：X Article 直读全文
> **笔记日期**：2026-09-12
> **关联笔记**：《LLM八种精度格式全解》（FP8/INT4/GPTQ 量化族）《TTFT首字延迟全解》（Prefill/Decode 分离与访存瓶颈）《Engram条件记忆》（确定性寻址→可预取→异步隐藏传输）

---

## 零、结论先行

**PagedAttention = 把操作系统 1960 年代的虚拟内存分页搬到 GPU KV Cache，把 80% 内存浪费降到 <4%，同硬件吞吐 2-4 倍。** 这不是新发明——是经典 OS 概念对 AI 瓶颈的一次完美复用。对我们最深的增量：**文章把 vLLM 2023 基础论文到 2026 现代部署的完整演进链一次讲透**——Chunked Prefill/Prefix Caching/Speculative Decoding/Disaggregated Serving 四大升级全部是 PagedAttention 之上的增量层，且与我们已写笔记多处互证。**不形成新 skill**（部署推理已有 llm-inference-deploy/llm-inference-optimization 两个 skill 覆盖），但作为教学参考笔记有高复用价值。

## 一、问题层：KV Cache 为什么爆炸

### 1.1 什么是 KV Cache

LLM 自回归生成时不能每生成一个词就重读全部前文——它把每个已处理词的数学表示（Keys 和 Values）存入临时存储区，**这个存储区就是 KV Cache**。

**每 token 的内存消耗**（文章给的公式）：

```
Bytes/token = 2 × Layers × Attention Heads × Head Dimension × 2 bytes (FP16)
```

现代模型一个 token 在 KV Cache 里约占 **~1MB VRAM**。

### 1.2 三种浪费（旧式连续分配的死穴）

| 浪费类型 | 餐厅类比 | 实际场景 |
|---------|---------|---------|
| **内部碎片** | 预定 10 人桌只来 1 人，9 把椅子空着 | 服务器为 2000 词预分配但用户只问 10 词笑话 |
| **外部碎片** | 桌位之间留出奇怪大小的缝，新客进不去 | 用户进出后留下不连续空隙，新请求需连续块但拼不出 |
| **共享浪费** | 三桌客点同样的系统提示词，复制三份存三处 | 3 个用户同一 system prompt → KV Cache 复制 3 份 |

**UC Berkeley 2023 年实测：高达 80% 的 KV Cache 内存被浪费。GPU 在饥饿的同时持有大量空空间。**

## 二、救赎层：PagedAttention 机制

### 2.1 核心类比（文章最好的设计）

| 旧方式 | PagedAttention |
|--------|---------------|
| 所有人坐 10 人大桌 | 只用 1 人小方桌 |
| 来了就预分配整块 | **按需分配一个 block（16-32 token）** |
| 桌必须物理相邻 | 桌可散布任意位置，**逻辑上拼接** |
| 系统提示词复制 3 份 | **Page Table 指向同一物理 block** |

### 2.2 逻辑块 vs 物理块

- **逻辑块**：用户看到的连续对话（流式句子）
- **物理块**：数据实际居住的 GPU 芯片位置（散落各处）
- **Page Table**：每个请求一张映射表，连接逻辑→物理

**三种浪费的消灭**：
- 内部碎片 → block 太小（16-32 token），浪费 <4%
- 外部碎片 → block 可散布任意位置，无形状不匹配
- 共享浪费 → 多个 Page Table 指向同一物理 block（系统提示词共享）

### 2.3 字节级布局（最硬核的一段）

24GB VRAM 的 GPU 跑 7B 模型（FP16）：

```
VRAM 总量: 24 GB
 ├─ 模型权重（静态）: 14 GB（永驻不动）
 └─ KV Cache 工作区（动态）: 10 GB

旧式：预分配 2GB/用户（假设 2000 token × 1MB）→ 最多 5 并发
      5 用户只问 10 词笑话 → 10GB 全被锁死 → OOM

PagedAttention: 10GB 切成 ~640 个 16MB 物理块
      用户问 10 词笑话 → 分配 1 个 16MB block
      剩余 9984 MB 全可用于其他数千用户
```

## 三、批处理层：从静态到连续

### 3.1 Prefill vs Decode（两种完全不同的负载）

| 阶段 | 做什么 | 特点 |
|------|--------|------|
| **Prefill** | AI 读你的 prompt | 大规模并行计算，瞬间完成 |
| **Decode** | AI 写回答 | 逐词串行，慢循环 |

### 3.2 静态批处理（校车模型）

等满 4 人上车→出发→User A 5 词就完了但**不能下车**→等 User B 写完 500 词→A 的内存空坐全程浪费。

### 3.3 连续批处理（摩天轮模型）

PagedAttention 使内存块独立→**每个词生成后评估队列**：User A 做完 5 词→立即驱逐→User C 秒级加载空位。摩天轮永不停转，永远没有空座。

## 四、数字层：2-4 倍从哪来

| 指标 | 旧式 | vLLM |
|------|------|------|
| KV Cache 浪费 | ~80% | **<4%** |
| 吞吐（vs 2023 最佳 TGI/Orca/FasterTransformer） | 基线 | **2x-4x** |
| GPU 内存利用率 | 不可预测 | **98%** |
| 硬件升级 | 需要 | **不需要**（纯软件优化） |

> "Without upgrading the physical hardware, without buying newer GPUs, the researchers allowed servers to handle up to four times as many users simply by organizing the memory blocks intelligently."

## 五、2023→2026 演进层（文章最大增量价值）

### 5.1 Chunked Prefill（分块预填）

100,000 词 prompt 一次性读会暂时独占 GPU → **切成小块与正常 decode 流量交错执行**，服务器永不暂停。与我们 TTFT 笔记的"长 prompt 阻塞 decode 队列"问题精确对应——这是解法。

### 5.2 Prefix Caching（前缀缓存）

50 个员工用同一 1000 词系统提示词 → **只读一次，KV Cache 存共享 Page Table**。与 SGLang RadixAttention（确定性前缀缓存）同族——Engram 笔记的"确定性寻址天然适合预取"同源。

### 5.3 量化族（与精度笔记全面对齐）

| 格式 | 文章口径 | 我们笔记的补充 |
|------|---------|--------------|
| FP8/MXFP8/MXFP4/NVFP4 | Nvidia 原生格式 | 《八种精度》已全解——Engram 196B 表用 FP8 是理想负载 |
| INT8/INT4 | 模型缩到 1/4 | 边缘部署核心路径 |
| GPTQ/AWQ | 保精度的专用算法 | 与 PagedAttention 叠加可把 $30k 机架塞进单卡 |
| GGUF | CPU RAM 无 GPU 时 | Jetson 路径之一 |

### 5.4 Speculative Decoding（推测解码/编辑模型）

```
小 Draft Model 快猜 5 词 → 大模型当编辑 → 正确则一次接受 5 词
→ 5 词的生成时间 ≈ 1 词的时间
```

现代支持：n-gram、suffix matching、EAGLE、DFlash。与 OUI-1 笔记的"窄域小模型当助手"同构——但这里是"小模型加速大模型"而非"小模型自教自己"。

### 5.5 Disaggregated Serving（分离式部署）

Prefill（读）和 Decode（写）用硬件方式不同 → **拆到不同服务器机架**：一台专读 prompt，KV Cache 经网络传给另一台专写回答。与 V4.1 Flash 的 PD 不对称（prefill 8B < decode 16B）同一趋势——**读写分离从模型架构层到部署架构层一以贯之**。

## 六、实操层：何时用什么

| 场景 | 用什么 |
|------|--------|
| 笔记本跑测试/离线批量 PDF 摘要 | HuggingFace transformers 够（静态批处理，原型阶段） |
| 开端口多用户实时 | **vLLM 强制**（HF 静态批处理必 OOM） |

### 生产四旋钮

| 旋钮 | 建议 | 理由 |
|------|------|------|
| Block Size | 16-32 | 太大→内部碎片回来；太小→Page Table 过重拖 CPU |
| enforce_eager | **Off** | CUDA/HIP Graphs 回放不经过 CPU 省 latency |
| Prefix Caching | **常开** | 用户共享 system prompt 时收益巨大 |
| Quantization | VRAM 不够时 | 最容易把大模型塞进便宜服务器 |
| Speculative Decoding | 严格低延迟（实时语音 AI）时 | 配置复杂但大幅提升 token 间延迟 |

## 七、与我们体系的对接

| 文章内容 | 已有笔记 | 判定 |
|---------|---------|------|
| 量化族全解 | 《LLM 八种精度格式全解》 | ✅ 已有且更深——FP8/NVFP4/MXFP4 实战补章 |
| Prefill/Decode 分离 | 《TTFT 首字延迟全解》 | ✅ 已有——文章补了 Chunked Prefill 解法 |
| 确定性寻址→共享前缀 | 《Engram 条件记忆》 | ✅ 互证——Engram 的确定性 hash 与 Prefix Caching 的确定性前缀同族 |
| PD 不对称 | DeepSeek V4.1 Flash（Engram 笔记引用） | ✅ 互证——Disaggregated Serving 是部署侧的 PD 分离 |
| 推测解码 | llm-inference-optimization skill | ✅ 已有 |
| vLLM 部署 | llm-inference-deploy skill | ✅ 已有 |

**判定：不形成新 skill**——llm-inference-deploy + llm-inference-optimization 两个已有 skill 覆盖了本文全部实操内容。本文的教学价值在于**从 OS 虚拟分页的类比把 PagedAttention 讲得最易懂**，但不引入我们体系没有的知识。

**Nugget 归宿**：文章的"餐厅/校车/摩天轮"三个类比是很好的教学设计——记入 llm-inference-deploy skill 的"教学类比库"（若有人问 PagedAttention 是什么，用这三个类比解释）。

## 八、批判性审视

1. **"80% 浪费"是 2023 年基线**——文章诚实标注了（"2023 年实测"），但 2026 年几乎所有主要 serving engine 都已采纳某种形式的连续批处理和内存分页——**现代部署的收益远小于 2-4 倍**（文章在"Honest Limits"节自己也说了）
2. **餐厅/校车/摩天轮类比极佳但掩盖了复杂度**：Page Table 的维护开销、block size 的调优、KV Cache 的驱逐策略（LRU？LFU？）——文章完全没展开
3. **speculative decoding 的"5 词全对"理想化**：实际 draft model 猜的 5 词可能只有 2-3 词被接受——加速比取决于 acceptance rate，文章给了概念没给数字
4. **Disaggregated Serving 的网络开销未讨论**：Prefill→Decode 跨机架传 KV Cache 的网络带宽和延迟——这是这个方案的核心成本
5. **文章是 ByteBuilders Newsletter 导流文**——末尾有 subscribe 链接；但教学质量高于平均，类比设计是认真的

## 九、金句提取

> "The math was not the bottleneck. The bottleneck was memory."

> "By looking at a bleeding-edge AI bottleneck and applying a decades-old operating system concept (virtual memory paging), researchers transformed LLM serving from a financially ruinous experiment into a scalable, highly profitable enterprise architecture."

> "Without upgrading the physical hardware, without buying newer GPUs, the researchers allowed servers to handle up to four times as many users simply by organizing the memory blocks intelligently."

> "The Ferris wheel never stops spinning, and there are never any empty seats."（连续批处理）

> "The KV Cache is no longer a graveyard of wasted memory. It is a dynamic, perfectly allocated engine powering the future of software."

## 十、局限性

1. X Article 约 3000 字，面向初学者（beginner-friendly guide）——深度受限于体裁
2. vLLM 2023 原始论文（arXiv:2309.06180）未逐页核对——数字以文章转述为准
3. Page Table 的实现细节（block 驱逐策略、跨请求共享的并发安全）未展开
4. §五四大升级为概述口径，每个的论文/实测数字未给（Chunked Prefill/Disaggregated Serving 是 2024-2026 的新发展，文章只指方向）
5. §七对接基于本机已有 skill 自查，未实际跑 vLLM 验证

## 出处标注

| 章节 | 来源类型 |
|------|---------|
| 一至六 | **原文忠实还原**（X Article 全文直读） |
| 七 | **体系映射**（本笔记扩展，对照已有笔记/skills） |
| 八 | **批判性审视**（本笔记扩展） |

## 相关笔记

- [GPU互联经济学](./2026-09-12-GPU互联经济学-KV缓存搬一次vs反复搬的带宽账-Mooncake共享到CXL光互连全景拆解.md) — KV搬一次vs反复搬的带宽账（同日姊妹篇）
- [TTFT首字延迟全解](./2026-09-11-TTFT首字延迟全解-Prefill二次方机制与SGLang调优参数表.md) — prefill二次方与延迟瓶颈
- [LLM八种精度格式全解](./2026-09-10-LLM八种精度格式全解-从FP32到NF4的内存精度权衡机制.md) — 量化省内存的精度代价
- [Engram条件记忆架构](./2026-09-11-Engram条件记忆架构-196B记忆表零推理成本的外挂原理-DeepSeek-V4.1-Flash实装拆解.md) — 确定性寻址→可预取→异步隐藏
- [A100跑DeepSeek-v4.1-Flash实录](./2026-09-12-A100跑DeepSeek-v4.1-Flash-存储格式不等于运算格式与五次前提砸碎-清水亮24小时优化实录.md) — 24小时实测优化对照
- vLLM V1 架构 APC 深拆（~/explore/2026-06-22-vllm-v1-architecture-apc-deep-dive.md）— 跨季度架构演进参照
