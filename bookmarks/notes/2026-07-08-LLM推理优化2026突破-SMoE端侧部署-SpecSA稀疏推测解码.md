# LLM 推理优化 2026 突破 — SMoE 端侧部署、SpecSA 稀疏推测解码、SSD 自推测

> 📅 2026-07-08 · 夜间自学习笔记 · 来源：ISCA 2026 / arXiv / 信通院报告 / EmergentMind

---

## 一、为什么现在关注

推理优化是 AI 从实验室到产业的「最后一公里」。信通院 2026 报告指出：**全球推理计算量较上年增长 100 倍以上**，推理成本超越训练成本成为企业瓶颈。三大方向同步突破：模型级（MoE/量化）、引擎级（推测解码/稀疏注意力）、系统级（PD 分离/弹性调度）。

---

## 二、核心发现

### 1. SMoE：MoE 模型端侧推理加速（ISCA 2026，南京大学）

**问题**：边缘设备 GPU 显存不足，MoE 专家频繁在 GPU 显存 ↔ CPU 内存间卸载，PCIe 传输慢 10-100 倍。

**核心洞察 — 专家重要性差异**：
```
每次推理激活 Top-k 专家，但实际上：
  少数专家 → 高门控分数（高分活跃）→ 对输出影响大
  其余专家 → 低门控分数（低分活跃）→ 对输出影响极小
                                    ↑ 现有策略不区分这两类！
```

**SMoE 三大协同机制**：

| 机制 | 原理 | 效果 |
|------|------|------|
| **低分专家替换** | 将低分活跃专家直接替换为 GPU 显存中已缓存且功能相似的闲置专家 | 减少 PCIe 传输，缓存命中率 >60% |
| **高分专家预取** | 仅针对预测出的高分专家做针对性加载 | 数据加载与计算重叠 |
| **CPU 辅助调度** | 两指针动态调度算法平衡 CPU 计算与 PCIe 传输 | 防流水线停滞 |

**实验结果**：

| 硬件 | Batch | 延迟降低 |
|------|-------|---------|
| A6000 | 1 | **48%** |
| 平均 | 1 | 24% |
| 平均 | 3 | 35% |

**精度**：专家替换阈值 <0.35 时，Gaokao/MMLU/HumanEval 精度损失可忽略不计。

**对 Jetson Orin 的价值**：Jetson 显存仅 8GB，正好是 SMoE 的目标场景。如果 MoE 模型（如 DeepSeek-MoE）部署到 Jetson，SMoE 的专家替换策略可以直接借鉴——不需要加载全部专家，用缓存中的近似专家替代低分专家。

### 2. SpecSA：推测解码 + 稀疏注意力的融合（arXiv 2605.19893）

**核心问题**：推测解码（Speculative Decoding）和稀疏注意力（Sparse Attention）各自有效，但直接组合有**结构性冲突**：

- 推测解码依赖跨查询的 KV-cache 复用（多个候选 token 共享同一前缀）
- 稀疏注意力为每个查询分配不同的稀疏布局（query-specific）
- → 稀疏布局破坏了 KV-block 复用，增加了 NSA 分支级开销

**SpecSA 解决方案**：

1. **Overlap-aware Grouped-Query Execution** — 按重叠模式组织查询，最大化 KV-block 共享
2. **Refresh/Reuse-based NSA Kernel Fusion** — 融合稀疏注意力内核，减少分支开销
3. **Profile-Guided Prompt-Adaptive Orchestration** — 根据输入 prompt 特征自适应选择验证策略

**结果（H100 GPU）**：

| 指标 | 提升 |
|------|------|
| 端到端吞吐量 | **3.49×** vs 自回归 NSA 解码 |
| 内核加速 | **6.86×** |

**实际意义**：64K 上下文下，Llama-3.1-8B 注意力计算占解码步骤的 **97.20%** 时间。SpecSA 的价值在于同时解决「带宽瓶颈」（推测解码）和「KV-cache 访问量」（稀疏注意力），而不是二选一。

### 3. Sparse Self-Speculative Decoding (SSD)：无损加速新范式

**核心思想**：不需要单独的 draft 模型，直接从目标 LLM **动态派生**稀疏草稿模型：

```
完整 LLM → [稀疏化算子] → 稀疏草稿模型（同权重，不同执行模式）
                                    ↓
                        生成 k 个候选 token
                                    ↓
                    完整 LLM 并行验证 → 接受/拒绝
```

**稀疏化方式**：

| 方式 | 论文 | 原理 |
|------|------|------|
| **层跳跃** | CLaSp (2025/05) | 动态选择跳过部分 Transformer 层 |
| **背包优化** | KnapSpec (2026/02) | 将子网络选择建模为 0/1 背包问题 |
| **块稀疏注意力** | (2025/12) | 强制块级稀疏注意力模式 |
| **KV-cache 剪枝** | (2026/05) | 剪枝 KV-cache 减少内存访问 |

**无损保证**：由于 draft 和 verify 共享相同权重和架构，SSD 的输出分布与原始模型**数学等价**（在贪心或采样模式下）。

**核心优势**：Plug-and-play，无需训练额外模型，无需辅助参数。对 Jetson 这种算力受限设备极其友好。

### 4. MoESD：推测解码对 MoE 模型的有效性（NeurIPS 2025）

**挑战**：推测解码一直被认为只对 dense 模型有效。MoESD 从理论和实验证明 SD 对 sparse MoE 同样有效：

- 稀疏激活特性使得 MoE 的计算瓶颈不同于 dense 模型
- 验证阶段多个候选 token 可以共享专家路由，减少重复激活
- 在 DeepSeek-V3 等 MoE 模型上获得显著加速

**与 SMoE 的互补关系**：SMoE 解决端侧显存受限问题，MoESD 解决云端高吞吐问题，两者可以叠加。

### 5. 信通院 2026 报告：三级优化体系

| 层级 | 核心方法 | 代表技术 |
|------|----------|----------|
| **模型级** | 量化/压缩/架构创新 | INT4/INT8、GQA/MLA、MoE、DeepSeekMoE |
| **引擎级** | 内存/调度/解码优化 | PagedAttention、连续批处理、推测解码、Chunked-Prefill |
| **系统级** | 分布式/分离/弹性 | PD 分离、AF 分离、Mooncake、Dynamo、弹性调度 |

**2026 趋势**：「模型-架构-场景」协同优化成为核心范式，从单点优化走向系统级全链路优化。

---

## 三、技术成熟度评估

| 技术 | 成熟度 | 边缘适用性 | 与 Jetson Orin 的距离 |
|------|--------|-----------|---------------------|
| **INT4/INT8 量化** | ✅ 生产级 | 高 | 已在用（GGUF/llama.cpp） |
| **层跳跃 SSD** | 🔄 实验到早期生产 | 高 | 可尝试（CLaSp 开源） |
| **SMoE 专家替换** | 🔄 学术验证 | 高 | 理论可用，需工程适配 |
| **SpecSA** | 🧪 学术阶段 | 低（需 H100） | 暂不适用 |
| **PD 分离** | ✅ 生产级（云端） | 不适用 | 不适用于单设备 |

---

## 四、对现有 Skill / 项目 的改进建议

### 高优先级

1. **`edge-llm-quantization` skill 更新**：增加 SMoE 专家替换策略的原理说明和实践指南。当前 skill 聚焦 GGUF 量化，应扩展 MoE 端侧部署章节
2. **`llm-inference-optimization` skill 补充 SSD 章节**：当前覆盖 PagedAttention/量化/推测解码/连续批处理，缺少 **Sparse Self-Speculative Decoding** 这一 2026 新范式。增加层跳跃（CLaSp/KnapSpec）和 KV-cache 剪枝两种实践路径
3. **Jetson Orin 部署实验**：用 CLaSp（层跳跃）在 Qwen3-4B 或 DeepSeek-R1-Distill-Llama-8B 上做实验，测量层跳跃对延迟和精度的影响

### 中优先级

4. **`llm-inference-deploy` checklist 更新**：信通院三级优化体系可作为部署检查清单的框架——模型级/引擎级/系统级逐层确认
5. **MoESD 理论价值**：如果未来在 Jetson 上部署 MoE 模型，MoESD + SMoE 可叠加使用（云端验证 + 端侧替换），值得提前建立知识储备

---

## 五、关键数据点

- 推理计算量年增 **100 倍**（信通院 2026）
- 64K 上下文 Llama-3.1-8B 注意力占解码时间 **97.20%**
- SMoE A6000 batch=1 延迟降 **48%**，精度损失可忽略
- SpecSA H100 吞吐量 **3.49×**，内核加速 **6.86×**
- SSD 无损保证：输出分布与原始模型**数学等价**

---

## 六、参考来源

- [SMoE (ISCA 2026)](https://cs.nju.edu.cn/lm/post/2026-04-17-isca-2026-smoe-edge-inference/index.html) — 南京大学，MoE 端侧推理
- [SpecSA (arXiv:2605.19893)](https://arxiv.org/html/2605.19893v1) — 推测解码 + 稀疏注意力融合
- [Sparse Self-Speculative Decoding](https://www.emergentmind.com/topics/sparse-self-speculative-decoding) — SSD 综述
- [MoESD (NeurIPS 2025)](https://openreview.net/forum?id=FAeU7516MR) — MoE 推测解码
- [信通院 大模型推理优化报告 2026](https://www.fxbaogao.com/detail/5354678) — 三级优化体系
- [vLLM Speculative Decoding Blog](https://vllm.ai/blog/2025-12-13-speculators-v030) — 训练支持

## 相关笔记

- [TileFuse: AMD NPU 量化推理核库](./explore/2026-07-07-TileFuse-AMD-NPU量化推理核库.md) — NPU 融合混合精度量化
- [KV Cache 量化压缩三突破](./explore/2026-07-05-KVCache量化压缩-TurboQuant-RotorQuant.md) — TurboQuant/RotorQuant
- [Kara 滑动窗口 KV Cache 压缩](./explore/2026-07-04-Kara-KVCache压缩.md) — 高效推理服务
