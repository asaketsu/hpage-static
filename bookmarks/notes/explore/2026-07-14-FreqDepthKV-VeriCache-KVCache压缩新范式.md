# FreqDepthKV & VeriCache：KV Cache 压缩两大新范式

> 📅 2026-07-14 | 🏷️ LLM 推理优化、KV Cache 压缩、Speculative Decoding
> 来源：arXiv 2607.06519 + arXiv 2605.17613

## 核心发现

### 1. FreqDepthKV：频率引导的深度共享压缩

**问题：** 长上下文推理中 KV Cache 线性增长，现有压缩方法（token 驱逐、量化）要么丢弃检索关键证据，要么忽略相邻 Transformer 层间的冗余结构。

**核心思路：** 将相邻层的 KV 状态分解为：
- **低频深度分量**（shared）— 多层共享，可压缩
- **高频残差**（sparse）— 保留检索敏感证据，不可压缩

**三种缓存模式（每 attention head 独立分配）：**

| 模式 | 适用场景 | 压缩率 | 精度影响 |
|------|---------|--------|---------|
| **Shared-depth** | 层间冗余高、非关键 head | 最高 | 低 |
| **Residual-depth** | 需要保留残差校正 | 中等 | 极低 |
| **Exact** | 检索/推理关键 head | 无压缩 | 零 |

**在线探针（Online Probe）：** 在 prefill 阶段轻量计算每个 head 对 attention logits 重建的贡献度，动态分配缓存模式 — 无需重训练，自适应 prompt 结构。

**性能数据（32k token prefill）：**

| 指标 | Full KV | FreqDepthKV | 提升 |
|------|---------|-------------|------|
| Exact Match | 58.5 | 58.3 | ≈无损 |
| F1 | 63.2 | 63.0 | ≈无损 |
| pass@1 | 48.0 | 48.1 | ≈无损 |
| 解码吞吐 | ~18 tok/s | 70.4 tok/s | **3.9×** |
| TTFT | ~8s | 2.06s | **3.9×** |
| 峰值 KV 内存 | ~24 GB | 6.2 GB | **3.9× 压缩** |

**关键洞察：** 层级冗余不是均匀分布的 — 某些层在平均值上看似冗余，但包含高频残差信息，对于 needle 检索、代码依赖追踪、推理链维护至关重要。均匀深度压缩（如 MiniCache）会删除这些残差导致答案改变。

### 2. VeriCache：有损 KV → 无损推理

**问题：** KV Cache 压缩（token dropping、量化）本质有损 — 短输出时影响小，但长输出时偏差累积，导致代码生成和工具调用灾难性失败。

**核心思路：** 借鉴 Speculative Decoding — 用压缩 KV Cache 快速 draft token，再用完整 KV Cache 验证，确保输出与全量 KV 完全一致。

**两大系统级洞察：**

1. **并行化** — 压缩 KV 解码是 HBM 带宽受限，完整 KV swap-in 是 PCIe/网络受限 → 两者可并行
2. **长 draft horizon** — 压缩 KV 输出通常与全量 KV 相似 → 长 draft 窗口可摊销每次 swap 开销

**架构：**

```
压缩 KV Cache → 快速 draft N 个 token
                    ↓ (并行)
完整 KV Cache ← 从 CPU/远程 swap 到 GPU
                    ↓
              验证 draft token
              ├─ 匹配 → 接受（免重新计算）
              └─ 不匹配 → 用全量 KV 重新生成
```

**性能：** 最高 **4× 吞吐提升**，输出与全量 KV **完全一致**（greedy decoding 下）。

**与传统 Speculative Decoding 的组合：** VeriCache 的外层 draft + Eagle/MTP-head 的内层 draft 可叠加，接受长度公式：

```
γ(x,c) · x · [1 + γₑ(dₑ) · (dₑ - 1)]
```

其中 γ(x,c) 是压缩 KV 的接受率，x 是外层 draft 长度，γₑ(dₑ) 是内层 drafter 的接受率。

### 3. 两种方法的互补性

| 维度 | FreqDepthKV | VeriCache |
|------|-------------|-----------|
| **压缩目标** | 深度维度（层间共享） | 序列/精度维度 |
| **精度保证** | 近似无损（经验） | **数学精确无损** |
| **需要重训练** | 不需要 | 不需要 |
| **与量化兼容** | ✅ 正交 | ✅ 通过统一 compressor 接口 |
| **与 token eviction 兼容** | ✅ 正交 | ✅ 支持 |
| **最佳场景** | 长上下文 QA/摘要/代码 | 代码生成/工具调用（高精度需求） |

## 技术细节

### FreqDepthKV 的深度-频率分解

相邻层 KV Cache 存在结构性冗余，但不是简单的"层 i ≈ 层 i+1"：

```
KV_layer_i = SharedDepth (低频) + Residual_i (高频)
KV_layer_{i+1} = SharedDepth (低频) + Residual_{i+1} (高频)
```

- SharedDepth 被多层共享存储 → 大幅省内存
- Residual 仅对需要精确 attention 的 head 保留 → 稀疏存储
- Online Probe 在 prefill 时计算重建误差 vs attention logits 偏移的敏感度

### VeriCache 的 swap 策略优化

关键挑战：完整 KV Cache 太大，不能常驻 GPU 内存。

**优化器自动选择策略：**
- 短输出 → P1 策略（频繁 swap-in 验证）
- 长输出 → P2 策略（长 draft horizon 摊销 swap）
- 本地内存充足 → cached verification
- 本地计算充足 → stateless verification
- 无收益时 → 回退到基线路径

## 对现有 Skill/Memory 的改进建议

| 优先级 | 建议 | 关联 Skill |
|--------|------|-----------|
| P1 | 更新 `llm-inference-optimization` Skill，补充 FreqDepthKV 深度维度压缩方法 | llm-inference-optimization |
| P1 | 更新 KV Cache 压缩知识库，区分"近似无损"和"数学无损"两条路线 | context-engineering-patterns |
| P2 | VeriCache 的 draft-verify 范式可借鉴到 Hermes 的 Skill 验证流程 | verification-gate |
| P3 | 跟踪 FreqDepthKV 开源实现（论文未提及代码发布） | — |

## 参考文献

- [FreqDepthKV: Frequency-Guided Depth Sharing](https://arxiv.org/abs/2607.06519) — 3.9× 压缩，近无损
- [VeriCache: Turning Lossy KV Cache into Lossless](https://arxiv.org/abs/2605.17613) — 4× 吞吐，数学无损
- [KV Cache Optimization Strategies](https://arxiv.org/abs/2603.20397) — 五大方向系统综述
- [Awesome-KV-Cache-Optimization](https://github.com/jjiantong/Awesome-KV-Cache-Optimization) — 持续更新的论文列表


## 相关笔记

- [vLLM V1本地模型部署架构](./2026-07-14-本地模型部署-vLLMV1-APC.md) — 推理部署与KV管理
- [Kara KVCache压缩](./2026-07-04-Kara-KVCache压缩.md) — KV压缩早期方案
- [MemoryCompaction 速率失真](./2026-07-12-MemoryCompactionRateDistortion.md) — 压缩理论通篇
- [推理加速2026-MTP与推测解码](../2026-07-02-LLM推理加速2026-MTP与推测解码实战全景.md) — 推理优化全景