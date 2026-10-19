# KV Cache 量化压缩 2026 三大新突破：TurboQuant / RotorQuant / L2 异步预取

> **核心论文**：TurboQuant (ICLR 2026) · RotorQuant (社区复刻) · Async KV Prefetch (AAAI-26)
> **日期**：2026-07-05 | **记录**：夜间自学习引擎
> **前序笔记**：2026-07-04-Kara-KVCache压缩 · 2026-06-26-LLM长上下文KV-Cache压缩四新法 · 2026-06-28-SharQ

**标签**：#LLM推理优化 #KV-Cache #向量量化 #在线压缩 #ICLR2026 #边缘部署

---

## 一、核心问题：KV Cache 才是真正的显存瓶颈

权重不是最大问题。每个 decoder token 都会在**每一层 attention** 存储 key/value 向量，KV Cache 随上下文长度**线性增长**：

- 70B 模型 + 512 并发用户 → KV Cache 独占 **~512GB**，约为模型权重本身的 **4 倍**
- Llama-3.1-8B + 128K 上下文 → KV Cache 显存可超过参数显存
- 早期量化方法的通病：每个 block 还要留 1-2 bit 存归一化常数，开销吃掉了压缩收益

**关键转向**：2026 年的研究重心从「静态权重量化（GPTQ/AWQ/GGUF）」彻底转向「**动态 KV Cache 在线向量量化**」——前者是离线标量量化，后者是实时向量量化，目标函数完全不同。

| 维度 | 权重量化 (GPTQ/AWQ) | KV Cache 量化 (TurboQuant) |
|------|--------------------|--------------------------|
| 目标 | 静态参数 | 推理时动态 cache |
| 时机 | 离线校准 | 实时在线压缩 |
| 数据访问 | 全数据集 | 无未来数据访问 |
| 开销 | 每 block 归一化常数 | 零开销设计 |

---

## 二、TurboQuant：近最优失真率的在线向量量化（ICLR 2026）

**来源**：Google Research，2026-03-24 发表，Amir Zandieh、Vahab Mirrokni（Google Fellow）等。arXiv 待公开，社区 24h 内出现多份独立复刻。

### 2.1 两阶段流水线

```
输入向量 x  ──▶  Stage 1: PolarQuant  ──▶  Stage 2: QJL 残差校正  ──▶  无偏注意力估计
```

**Stage 1 — PolarQuant**：
1. 提取向量范数 γ，单位化 x̂ = x/γ
2. 乘随机正交矩阵 Π（QR 分解预计算）→ 旋转后坐标服从 Beta 分布（≈ N(0,1/d)）
3. 用**预计算的量化质心**（centroids）做标量量化，**无需逐 block 归一化**（消除 1-2 bit 开销的根因）
4. 只存范数 γ + 量化索引 idx

```python
def turboquant_quantize(x, Pi, centroids):
    gamma = np.linalg.norm(x)
    x_hat = x / gamma
    y = Pi @ x_hat                       # 随机旋转
    idx = find_nearest(y, centroids)     # 逐坐标标量量化
    # Stage 2: QJL 处理残差
    y_recon = centroids[idx]
    residual = y - y_recon
    qjl_bits = np.sign(S @ residual)     # S 为随机投影矩阵，每坐标 1 bit
    return idx, qjl_bits, gamma
```

**Stage 2 — QJL（Quantized Johnson-Lindenstrauss）**：
- 对 Stage 1 的残差误差做随机投影，**每坐标只花 1 bit** 取符号
- 核心价值：修正 Stage 1 标量量化在点积估计上的系统性偏差，产出**无偏内积估计器**
- 两个变体：`TurboQuant_prod` 优化内积保真度（给 key 向量）；`TurboQuant_mse` 优化重建误差（给 value 向量）

### 2.2 为什么理论最优

- 压缩后仅 **3 bit/value**（离群点感知策略可降到 **2.5 bit**）
- 跨各 bit 宽度，与理论失真极限只差 **~2.7×**（之前的 PQ/RabitQ 差距大得多）
- **无需重新训练或微调**，对问答、代码生成、摘要任务无可测精度损失

### 2.3 实测性能

| 指标 | 数值 |
|------|------|
| 压缩比 | 相对 FP16 至少 **6×** |
| Needle-in-a-Haystack | 104K tokens 内 **100% 检索准确率**，与全精度持平 |
| H100 attention logit 计算 | 比 32-bit 基线快至 **8×** |
| 向量检索召回 | 优于 PQ / RabitQ，索引时间近乎为零 |

### 2.4 实用场景

1. **长上下文服务**：现有硬件上扩展上下文窗口，降每 token 成本
2. **边缘/端侧推理**：8-16GB RAM 设备跑 32K+ 上下文
3. **向量搜索 / RAG**：召回更高且索引时间近乎为零
4. **Agentic AI**：复杂多轮交互的实用更长上下文

---

## 三、RotorQuant：用 Clifford 代数 rotor 重构 TurboQuant

社区（scrya-com）在 NVIDIA 论坛披露：用几何代数 Cl(3,0) 的 **Clifford rotor** `R = exp(B/2)` 替换 TurboQuant 中的 d×d 随机正交旋转矩阵 Π。

| 对比 | TurboQuant（随机正交矩阵） | RotorQuant（Clifford rotor） |
|------|--------------------------|----------------------------|
| 表示 | d×d 矩阵 | 指数映射 B（44× 更少参数） |
| 计算 | 矩阵乘 | rotor 作用，**10-19× 更快** |
| 保真度 | 基准 | 在真实 LLM attention 上**持平** |

**实测细节（DGX Spark / GB10）**：
- GLM-4.7-Flash INT4 AutoRound：TQ3（TurboQuant 3-bit）比 FP8 快 **13-21%**，精度相同
- 三阶段落地：Stage 1 内存槽仍存 FP8（FlashInfer 兼容）→ Stage 2 token 率已上升 → Stage 3 CUDA kernel 真正吃到带宽红利

**意义**：说明 TurboQuant 的核心是「旋转去相关 + 标量量化 + 残差投影」这个**范式**，旋转矩阵的具体实现可被更高效的代数结构替换——这为后续变体（如用 Hadamard 变换、学习型旋转）打开了空间。

---

## 四、L2 Cache 异步预取：从压缩转向带宽隐藏（AAAI-26）

**论文**：Accelerating LLM Inference Throughput via Asynchronous KV Cache Prefetching（AAAI 2026，NVIDIA H20 实测）

**思路**：不再压 cache，而是**隐藏 HBM 访问延迟**——在计算活跃窗口期，主动把后续需要的 KV Cache 预取进 **GPU L2 Cache**，让后续访问直接命中 L2。

**vLLM XFormers 后端实测瓶颈**（Llama2-7B，bs=64，4096 输出 token）：

| 指标 | 数值 |
|------|------|
| Compute Throughput | 仅 23.35%（**计算严重不饱和**） |
| Memory Throughput | 47.10% |
| L2 Cache Hit Rate (Load) | **0.06%**（几乎全 miss） |

→ 说明 attention kernel 是**带宽受限**而非计算受限，L2 命中率有巨大提升空间。

**效果**：
- attention kernel 效率提升 **2.15×**
- 端到端吞吐提升至 **1.97×**，超越 FlashAttention-3
- 方法与压缩正交，可叠加使用

---

## 五、对现有 Skill / 笔记体系的改进建议

### 5.1 llm-inference-optimization Skill 应补的内容
当前 Skill 覆盖 PagedAttention / 量化 / 推测解码 / 连续批处理，但缺少：
- **向量量化（VQ）vs 标量量化**的区分——KV Cache 场景应优先 VQ
- **TurboQuant 两阶段范式**（旋转去相关 + 残差 JL 投影）作为 2026 KV 量化的新基线
- **L2 预取**作为带宽优化的独立手段，与压缩正交可叠加

### 5.2 edge-llm-quantization Skill（Jetson 部署）的启示
- TurboQuant 的 6× 压缩 + 零重训，对 Jetson Orin（显存受限）跑长上下文是**直接收益**
- 但需注意：社区复现多为 H100/GB10，**ARM64 + CUDA Jetson 上的 Triton kernel 适配是空白**，落地前需验证 SM 架构兼容性（参考 antigravity-tools-mod 的 ARM64 编译经验）
- RotorQuant 的 10-19× 提速对算力受限的边缘设备更有吸引力

### 5.3 与 Kara / SharQ 笔记的关系
- Kara（2026-07-04）：**滑动窗口双向注意力**做 token 级重要性筛选 → 选哪些 token 保留（**结构压缩**）
- SharQ（2026-06-28）：激活稀疏 + FP4 → **精度-计算联合压缩**
- TurboQuant（本篇）：**向量量化**压缩每个保留下来的 KV → **表示压缩**
- 三者作用于流水线不同环节：**重要性筛选（Kara）→ 表示量化（TurboQuant）→ 计算稀疏（SharQ）**，理论上可级联，但需实测叠加收益与开销

---

## 六、关键风险与盲点

1. **官方代码未发布**：TurboQuant 论文称 Q2 2026 放代码，当前全是社区复刻，质量参差（MLX 版 5× 压缩 + 99.5% 质量；PyTorch Triton 版声称 2-bit 字符级一致但未经独立验证）。**引用具体数字前务必标注「社区复现，未官方验证」**。
2. **量化对 Agent 长程依赖的影响未充分测试**：NIAH 只测单针检索，但 Agent 多步工具调用对中间步骤 KV 的精确依赖未被基准覆盖——实际 Agentic 场景可能比基准表现差。
3. **离群点感知 2.5-bit 策略细节缺失**：公开材料未给离群点检测阈值和分布假设，复现风险高。

---

## 七、一页速查

> **2026 KV Cache 优化的三层栈**：
> - **选**（Kara / SnapKV / AdaKV）：滑动窗口 + 双向注意力选重要 token
> - **压**（TurboQuant / RotorQuant）：随机旋转 + 标量量化 + JL 残差，3 bit/value，6× 压缩
> - **藏**（L2 异步预取）：计算间隙预取进 GPU L2，2.15× kernel 提速
>
> 三层正交可叠加。边缘部署优先级：压 > 藏 > 选。

## 相关笔记

- [[2026-07-04-Kara-KVCache压缩]] — Kara 滑动窗口 + 双向注意力 KV Cache 压缩
- [[2026-06-26-LLM长上下文KV-Cache压缩四新法]] — LLM KV Cache 压缩四大新方向全景
- [[2026-06-28-SharQ-激活稀疏与FP4量化]] — SharQ 激活稀疏与 FP4 量化
- [[2026-06-25-CompressKV]] — CompressKV 滑动窗口 KV 压缩方法
- [[2026-06-30-推测解码Speculative-Decoding-2026五大新方向]] — 推测解码与推理优化综合


## 相关笔记

- [Kara 滑动窗口KV Cache压缩](./2026-07-04-Kara-KVCache压缩.md) — 滑动窗口驱逐策略
- [KV Cache量化三大突破](./2026-07-05-KVCache量化压缩-TurboQuant-RotorQuant.md) — TurboQuant/RotorQuant/异步预取（本文）
- [TileFuse AMD NPU量化推理核库](./2026-07-07-TileFuse-AMD-NPU量化推理核库.md) — NPU侧混合精度量化

## 相关笔记

- [TileFuse: AMD NPU 量化推理核库](./2026-07-07-TileFuse-AMD-NPU量化推理核库.md) — NPU 融合混合精度量化
- [Kara 滑动窗口 KV Cache 压缩](./2026-07-04-Kara-KVCache压缩.md) — 高效推理服务
- [LLM 推理优化 2026 全景](../2026-07-08-LLM推理优化2026突破-SMoE端侧部署-SpecSA稀疏推测解码.md) — SMoE/SpecSA

## 相关笔记

- [Kara KV Cache 压缩](./2026-07-04-Kara-KVCache压缩.md) — 滑动窗口压缩前序
- [SPORK 自推测分叉](./2026-07-08-SPORK自推测分叉.md) — 推测解码并行加速
- [TileFuse AMD NPU 量化推理核库](./2026-07-07-TileFuse-AMD-NPU量化推理核库.md) — 混合精度量化部署

## 相关笔记

- [TileFuse: AMD NPU 量化推理核库](./2026-07-07-TileFuse-AMD-NPU量化推理核库.md) — NPU 侧量化推理
- [Kara：滑动窗口 KV Cache 压缩](./2026-07-04-Kara-KVCache压缩.md) — 前序笔记，滑窗压缩
- [SPORK 自推测分叉](./2026-07-08-SPORK自推测分叉.md) — 推理加速交叉
- [LLM推理加速2026-MTP与推测解码](./../2026-07-02-LLM推理加速2026-MTP与推测解码实战全景.md) — 推测解码全景
