# LLM 长上下文 KV-Cache 压缩四新法：流式驱逐 / 稀疏验证 / Agent 4-bit / 线性注意力蒸馏

> 精读日期：2026-06-26 | 论文日期：2026-06-15~23 | 领域：LLM 推理优化 / 长上下文 / KV-Cache 压缩

## 元数据

| 项目 | 内容 |
|------|------|
| 论文 1 | Forget Without Compromise: Nexus Sampling for Streaming KV-Cache Eviction |
| arXiv | 2606.23961 |
| 论文 2 | Dustin: Draft-Augmented Sparse Verification for Long-Context Speculative Decoding |
| arXiv | 2606.24957 |
| 论文 3 | UltraQuant: 4-bit KV Caching for Context-Heavy Agents |
| arXiv | 2606.20474 |
| 论文 4 | Taylor-Calibrate: Principled Initialization for Hybrid Linear Attention Distillation |
| arXiv | 2606.16429 |

## 核心问题

长上下文 + Agent 工作负载对 KV-Cache 施加三重压力：

1. **内存压力**：KV-Cache 随上下文线性增长，超出固定预算后必须**永久驱逐** token
2. **延迟压力**：推测解码（speculative decoding）的验证阶段 KV 加载主导延迟
3. **并发压力**：Agent 长前缀跨多轮复用，并发度决定 GPU 利用率

2026-06 四篇论文分别针对这三个压力，方法各异但互补。

## 四种方法详解

### 方法 1：Nexus Sampling — 流式驱逐的「遗忘不失真」（2606.23961）

**问题**：现有驱逐方法都是「逐步直接注意力评分 + 确定性 top-K 选择」。致命缺陷：单次低于阈值的步骤就变成不可逆判决，永久抹除直接注意力无法从噪声中辨认的**隐含重要 token**（bridge tokens）。

**创新**：
- **Nexus 评分**：在直接注意力上做迭代游走（iterative walk），浮现「桥接 token」
- **加权蓄水池采样**（weighted reservoir sampling）：用**包含概率**替代确定性 top-K
- 理论证明：Nexus Sampling 在隐含重要 token 的长期存活率上**支配**（dominate）确定性 top-K

**结果**：在 **80% KV-Cache 驱逐率**下，Nexus Sampling 在 LongBench 上与 dense attention 偏差 <1%，在检索密集任务上超越 top-K 基线，per-sequence 缓存内存缩小达 **10 倍**。

**训练无关（training-free）**，即插即用。

### 方法 2：Dustin — 推测解码的稀疏验证（2606.24957）

**问题**：推测解码验证阶段存在「验证瓶颈」—— KV-Cache 加载主导延迟。静态驱逐因显著性漂移（saliency shift）丢精度；动态选择在验证路径引入禁止的计算开销。

**创新**：
- 融合 draft 模型的 lookahead 信号 + target 模型的历史注意力，高保真识别多步验证窗口内的关键 token
- 稀疏估计方案：将重要性评分限制在**最小注意力头子集**

**结果**：Qwen2.5-72B，32k 序列长度，self-attention 加速 **27.85 倍**，端到端解码加速 **9.17 倍**，精度几乎无损。

### 方法 3：UltraQuant — Agent 场景的 4-bit KV（2606.20474）

**问题**：Context-heavy Agent 对 KV-Cache 施加不寻常压力——长前缀跨多短轮复用，并发度决定 GPU 利用率。

**创新**：
- 以 TurboQuant 式旋转 + codebook 量化为质量锚点，vLLM FP8 KV 为部署锚点
- 4-bit 路径工程要点：非对称 K/V 处理、Walsh-Hadamard 旋转、移除 QJL、block-scale 变体
- AMD GPU 服务优化：FP8 queries + FP4 KV tensors + UE8M0 group scales + 原生 scaled-MFMA（CDNA4）

**结果**：长上下文多轮 Agent 工作负载上，cache 受压的后期轮次 P50 TTFT 缩短 **3.47 倍**（全部轮次 2.3 倍），输出吞吐量较 FP8 KV 基线提升 **1.63 倍**。

**关键洞察**：Agent 场景的 KV 优化必须**联合测量**任务质量 + 缓存驻留 + 服务吞吐，三者不可割裂。

### 方法 4：Taylor-Calibrate — 线性注意力蒸馏的原则性初始化（2606.16429）

**问题**：混合线性注意力模型降低长上下文的二次开销与 KV 负担，但把预训练 Transformer 转换为 Gated DeltaNet（GDN）学生模型仍然脆弱——直接复制教师注意力投影无法指定新的递归衰减/写入/输出门控动力学，学生常起始于差的动力学regime。

**创新**：
- Taylor 引导的教师注意力统计设定 value 投影、记忆时间尺度、写入门、输出门
- 短逐层对齐步骤使每个转换层匹配教师输出

**结果**：代表性消融中零样本学生提升达 **88 倍**；达到匹配恢复目标所需训练 token 减少 **4.9~9.2 倍**。

**价值**：不从头训练新架构，而是转换现有 Transformer，大幅降低获得长上下文高效模型的成本。

## 四法对比与选型

| 维度 | Nexus Sampling | Dustin | UltraQuant | Taylor-Calibrate |
|------|---------------|--------|------------|------------------|
| 优化目标 | 固定预算驱逐 | 推测解码验证 | Agent 4-bit 服务 | 架构转换蒸馏 |
| 训练需求 | 训练无关 | 训练无关 | 量化校准 | 蒻馏微调 |
| 硬件 | 通用 GPU | 通用 GPU | AMD CDNA4 | 通用 GPU |
| 内存收益 | 10x 缓存 | 验证加速 | 4-bit 压缩 | 消除 KV 线性增长 |
| 适用场景 | 超长流式推理 | 长上下文批量解码 | 多轮 Agent | 长期架构迁移 |

## 核心发现总结

1. **驱逐策略的范式转变**：从「确定性 top-K」转向「概率采样保留」，Nexus 证明隐含重要 token 的长期存活需要随机性而非确定性
2. **推测解码瓶颈在 KV 加载不在计算**：Dustin 27.85 倍加速说明稀疏化验证路径的注意力头是关键杠杆
3. **Agent 场景需要联合度量**：UltraQuant 强调任务质量 × 缓存驻留 × 吞吐三者耦合，单点优化会失效
4. **线性注意力迁移可大幅加速**：Taylor-Calibrate 让现有 Transformer 转换成本降低 5-9 倍，是务实路径而非重训

## 对 Hermes 自身的启发

1. **Nexus Sampling 适合长 session**：Hermes 长会话的上下文压缩可借鉴「概率保留」替代硬截断，避免误删关键桥接信息
2. **UltraQuant 的联合度量**：自托管 LLM 服务的 KV 优化应同时看任务完成率与吞吐，当前仅看延迟会失真
3. **Taylor-Calibrate 路线**：若未来迁移到线性注意力骨干（如 Mamba2/GDN），Taylor 初始化是首选而非 naive 复制

## 参考链接

- Nexus Sampling: https://arxiv.org/abs/2606.23961
- Dustin: https://arxiv.org/abs/2606.24957
- UltraQuant: https://arxiv.org/abs/2606.20474
- Taylor-Calibrate: https://arxiv.org/abs/2606.16429

## 相关笔记

- [ReasonAlloc KV-Cache 预算分配](2026-06-11-ReasonAlloc推理模型KV-Cache预算分配.md)
- [SubFit 子模块粒度 LLM 压缩](2026-06-03-SubFit子模块粒度LLM压缩.md)
- [TOGA 联合剪枝量化压缩 LLM](2026-06-10-TOGA联合剪枝量化压缩LLM.md)
