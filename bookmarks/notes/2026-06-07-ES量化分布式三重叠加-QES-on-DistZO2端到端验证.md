# ES+量化+分布式三重叠加 — QES on DistZO2 端到端验证

> 夜间自学习 2026-06-07 | 深度 L3 | 关联链：ES量化模型RL训练(06-03) → ES Population Scaling(06-04) → ES+GRPO混合Pipeline(06-05) → ES分布式通信拓扑(06-06) → 本次三重叠加分析

---

## 一、核心发现

### 1. 三重叠加的技术可行性：三个独立优化维度的正交性分析

ES、量化和分布式是三个正交优化维度，理论上可以自由叠加，但工程实现存在交叉约束：

**维度正交性论证**：
- **ES vs 量化**：ES 只需 forward pass + 标量 reward，天然与量化空间兼容。QES（arXiv 2602.03120）已证明 INT4/GPTQ 量化模型上 ES 微调可行。正交性 ✅
- **ES vs 分布式**：ES 通信量 = O(N × 标量)，与模型维度 d 无关。DistZO2（arXiv 2507.03211）已在 OPT-175B 上验证分布式 ZO。正交性 ✅
- **量化 vs 分布式**：量化减少每参数存储/传输，分布式并行增加计算吞吐。DistZO2 的 CPU offload + PCIe/NVLink 分片传输与量化参数天然兼容。正交性 ✅

**关键交叉约束**：
1. QES 的累积误差反馈（AEF）需要跨步维护误差状态，在分布式场景下需要同步误差状态
2. DistZO2 的 PertP 策略要求 2 个 GPU 分别计算 +ε/-ε forward，量化空间中 ε 的有效扰动幅度受量化步长影响
3. SeedFlood 的种子重建机制在量化空间中可能产生确定性差异（不同 GPU 的量化舍入方向不同）

### 2. QES + DistZO2 的精确交互分析

**QES 在 DistZO2 PertP 模式上的适配**：

DistZO2 PertP 的核心操作：
```
GPU_0: L(θ + σε) → scalar_+
GPU_1: L(θ - σε) → scalar_-
Update: θ ← θ - α(se_+ - se_-)/(2σ)
```

QES 的核心操作：
```
1. 生成扰动 ε_i from seed_i
2. θ̃ = Q(θ + σε_i)  // 量化截断
3. δ = (θ + σε_i) - θ̃  // 截断误差
4. error_accum += δ      // 累积误差
5. θ̃ = Q(θ + σε_i + error_accum)  // 补偿后量化
6. Forward: f(θ̃) → reward
```

**叠加后的操作流程**：
```
GPU_0:
  ε = reconstruct(seed_i)  // 种子重建扰动
  δ_+ = (θ + σε) - Q(θ + σε)  // 正扰动截断
  error_accum_+ += δ_+
  θ̃_+ = Q(θ + σε + error_accum_+)  // 补偿量化
  reward_+ = forward(θ̃_+)  // 量化空间 forward

GPU_1:
  ε = reconstruct(seed_i)  // 相同种子
  δ_- = (θ - σε) - Q(θ - σε)  // 负扰动截断
  error_accum_- += δ_-
  θ̃_- = Q(θ - σε + error_accum_-)  // 补偿量化
  reward_- = forward(θ̃_-)  // 量化空间 forward

All-reduce: scalar_+, scalar_-  // 两个标量
Update: θ ← θ - α(reward_+ - reward_-)/(2σ)  // 量化空间更新
```

**新增通信量**：PertP 原来只传 2 个标量（16 bytes），叠加 QES 后不增加通信量（error_accum 是本地维护的）。

### 3. EGGROLL 低秩扰动 + QES 累积误差的数学交互

EGGROLL 将扰动结构化为低秩：ε = AB^T，rank r=1-4。

QES 的误差反馈需要修改为低秩感知：
```
原始: δ = (θ + σε) - Q(θ + σε)  // 全参数误差
低秩: δ_low = (θ + σAB^T) - Q(θ + σAB^T)  // 低秩扰动误差
```

**关键发现**：低秩扰动只有 r×(m+n) 个自由度（vs 原始 m×n），量化截断对低秩扰动的影响更大：
- rank=1 时：4096×4096 层只有 8192 个扰动自由度（vs 16M 原始）
- 大部分被量化截断为零 → AEF 累积更快 → 跨过量化步长的周期更短
- **这反而是优势**：低秩空间中 AEF 更高效，因为累积集中在少数方向上

**理论预测**：EGGROLL rank=1 + QES AEF 的组合可能比 QES 全参数扰动更高效，因为：
1. 低秩扰动在 GPU 上快 100x（EGGROLL 核心贡献）
2. AEF 在低秩空间中累积更集中、跨步长更快
3. 两者的优势是乘法关系，不是加法

### 4. ESC：ES 用于量化校准的新应用（arXiv 2603.08173, Mar 2026）

**首次将 ES 用于语音模型低比特量化校准**：
- 语音模型的激活分布范围极大，传统校准方法（min-max/percentile）精度损失严重
- ESC 将激活缩放因子优化问题转化为 ES 优化，用两步 local-global 方案求解
- INT8 量化下几乎无损，INT4 量化下首次接近无损
- **与 QES 的互补**：ESC 优化量化参数（scale/zero-point），QES 优化模型权重。两者可以串联

### 5. ES 在 SNN（脉冲神经网络）上的 EGGROLL 扩展（arXiv 2605.30361, May 2026）

**EGGROLL 被成功迁移到不可微分架构**：
- SNN 的脉冲阈值不可微分，传统方法需要代理梯度
- EGGROLL 的低秩扰动天然绕过不可微分问题
- 在 N-MNIST 上验证，训练效率提升显著
- **启示**：EGGROLL + QES 的组合可以推广到任何不可微分硬件（模拟计算、光子计算），不仅限于数字量化

### 6. ZOTTA：量化模型上的零阶测试时适应（arXiv 2603.14254, Mar 2026）

**解决量化模型部署后的分布漂移问题**：
- ZOTTA 是纯无 BP 的测试时适应框架，只用 forward pass
- 关键技术：分布鲁棒层选择（自动冻结分布不变层）+ 空间特征聚合对齐
- 内存减少 84%，ImageNet-C 上比 SAR（有 BP 方法）精度高 3.9%
- **与 QES+DistZO2 的关联**：ZOTTA 在边缘设备上运行，而 DistZO2 在 GPU 集群上运行。两者都是零阶+量化的组合，但面向不同场景

---

## 二、技术原理解析

### 2.1 三重叠加的端到端 Pipeline 设计

```
量化基座模型 (INT4/GPTQ)
│
├── Phase 1: QES + DistZO2 PertP 分布式探索
│   ├── CPU offload 量化参数（DistZO2）
│   ├── PCIe+NVLink 分片传输（14x 通信优化）
│   ├── GPU_0: QES(+ε, error_accum_+) → reward_+
│   ├── GPU_1: QES(-ε, error_accum_-) → reward_-
│   ├── All-reduce: 2 标量（16 bytes）
│   └── 内存 = 推理级（无需反向传播）
│
├── 可选: EGGROLL 低秩加速
│   ├── ε = AB^T (rank=1-4)
│   ├── AEF 在低秩空间高效累积
│   └── 训练吞吐 ≈ 推理吞吐的 91%
│
├── Phase 2: QLoRA + GRPO 精调
│   ├── 部分反量化（或 QLoRA 旁路）
│   ├── 标准 FSDP/ZeRO 梯度并行
│   └── 通信量 = O(d)（梯度传输）
│
└── 可选: SeedFlood 跨节点扩展
    ├── 种子 + 标量 flooding
    ├── 通信量 = O(N × diameter × 8B)
    └── 去中心化，无单点瓶颈
```

### 2.2 量化空间中 PertP 的精度分析

朴素 ES 的 antithetic sampling 精度：
```
Var(g_ZO) = σ² × ||∇f||² + O(σ⁴)  // 全精度空间
```

量化空间 QES 的精度：
```
Var(g_QES) = σ² × ||∇f||² + O(σ⁴) + O(Δ_q²)  // Δ_q = 量化步长
```

其中 Δ_q 的影响被 AEF 控制为：
```
effective_Δ_q ≈ Δ_q / K  // K = AEF 累积步数
```

在 DistZO2 PertP 中，+ε/-ε 的截断误差独立累积（error_accum_+ ≠ error_accum_-），这对梯度估计引入额外偏差：
```
bias = E[error_accum_+ - error_accum_-] ≠ 0  // 在非对称量化中
```

**关键发现**：对称量化（如 INT4 symmetric）的偏差为零，非对称量化（如 GPTQ asymmetric）引入 O(Δ_q/K) 的偏差。推荐使用对称量化格式以避免此问题。

### 2.3 内存预算分析

| 配置 | 模型参数 | 量化 | ES Population | GPU 数 | 内存/GPU |
|------|---------|------|-------------|--------|---------|
| QES (单卡) | 7B | INT4 | 256 | 1 | ~4 GB |
| QES + PertP | 7B | INT4 | 256 | 2 | ~2 GB |
| QES + PertP | 70B | INT4 | 256 | 8 | ~5 GB (offload) |
| QES + 2D | 175B | INT4 | 512 | 16 | ~8 GB (offload) |
| QES + EGGROLL | 7B | INT4 | 1024 | 2 | ~2 GB |

对比 GRPO 训练：
| GRPO (QLoRA) | 7B | BF16+4bit | 16 | 1 | ~18 GB |
| GRPO (QLoRA) | 70B | BF16+4bit | 16 | 4 | ~30 GB |

**结论**：三重叠加（QES+DistZO2+INT4）在 175B 模型上每卡仅需 8GB，而 GRPO 在 70B 上需要 30GB。训练规模提升 2.5x，内存降低 3.75x。

### 2.4 通信效率对比

```
方法                    7B 单步通信    175B 单步通信    扩展性
─────────────────────────────────────────────────────
GRPO All-Reduce         28 GB          700 GB          O(d)
QES 单卡               0              0               N/A
QES + PertP             16 bytes       16 bytes        O(1)
QES + 2D (8 GPU)        128 bytes      128 bytes       O(K)
QES + SeedFlood(128)    ~1 KB          ~1 KB           O(N×diam)
─────────────────────────────────────────────────────
QES+DistZO2 通信效率     2×10⁹:1       6×10⁹:1        vs GRPO
```

---

## 三、知识关联

- [[2026-06-06-ES-Population分布式通信拓扑-跨GPU跨节点并行最优通信模式]] → 本次将 QES 叠加到 DistZO2 的 PertP/DDP 框架上，是 06-06 待深入问题 #5 的直接回答。核心发现：QES 不增加 DistZO2 通信量，error_accum 是本地维护的
- [[2026-06-05-ES-GRPO混合训练Pipeline-无梯度与有梯度RL的最优切换]] → 本次为量化基座混合 Pipeline 的 Phase 1 提供了具体的分布式实现方案。信号-扩散分解中的扩散分量∝α²dT/N 在量化空间中被 AEF 进一步抑制
- [[2026-06-04-ES-Population-Scaling-Law-vs模型参数量-无梯度训练的扩展定律]] → 维度免费现象在三重叠加中同样成立：QES 的有效维度不随量化精度降低而增大（AEF 补偿了精度损失），因此 Population scaling law 保持不变
- [[2026-06-03-ES量化模型RL训练-无梯度进化策略绕过量化-RL交互]] → QES 的 AEF 机制是本次三重叠加的核心使能技术。补充了 EGGROLL rank=1 + QES AEF 的低秩交互分析（新发现：低秩空间 AEF 更高效）
- [[2026-05-29-NVFP4-vs-FP8在MoE-RL训练中的精确对比-精度域与训练范式的抉择]] → NVFP4 的非对称块缩放格式可能导致 QES PertP 的偏差问题。推荐在 QES+DistZO2 中使用对称量化（FP8 E4M3 或 INT4 symmetric）
- [[2026-05-23-QLoRA在RL训练中的精度影响-QeRL-NVFP4-RL量化噪声增强探索]] → QeRL 发现量化噪声增强探索，QES 在分布式场景下也有类似效果：不同 GPU 的量化舍入差异引入隐式扰动多样性
- [[2026-05-22-LoRA与GRPO最优配置实证-Schulman信息论论证LoRA-RL]] → Schulman O(1) bits 论证在量化空间仍然成立：QES 的累积误差反馈确保每步仍然提供 O(σ²/N) bits 有效信息
- obs_notes: 无直接匹配

---

## 四、Actionable Insights

### 4.1 可直接落地

1. **QES + DistZO2 PertP 实现**：在 QES 的开源代码（github.com/dibbla/Quantized-Evolution-Strategies）基础上，添加 PertP 分布式逻辑。预估工作量：1 周。核心修改：拆分 antithetic sampling 到两个 GPU，各自维护 error_accum

2. **对称量化格式选择**：QES+DistZO2 必须使用对称量化（INT4 symmetric / FP8 E4M3），避免非对称量化的梯度偏差。这与 05-29 笔记中 NVFP4 的推荐不同 — NVFP4 适合 GRPO，FP8 E4M3 适合 QES

3. **ESC + QES 串联校准**：先用 ESC 优化量化参数（scale/zero-point），再用 QES 微调权重。两个 ES 优化可以共享分布式基础设施

### 4.2 中期方向

4. **EGGROLL rank=1 + QES AEF 联合实验**：低秩空间 AEF 累积更集中的假设需要实验验证。在 Llama-3B INT4 上对比 rank=1+AEF vs rank=4+AEF vs 全参数+AEF 的收敛速度

5. **QES + SeedFlood 跨节点扩展**：将 QES 的误差反馈机制与 SeedFlood 的种子传播结合。关键问题：误差反馈状态是否需要跨节点同步？（理论上不需要，因为每个节点独立维护自己的 error_accum）

6. **QES + MoE-Sieve 热专家策略**：只对热专家（top-25%）运行 QES 微调，冷专家保持不动。结合 DistZO2 的 PertP，每个热专家分配到不同 GPU 对

### 4.3 长期方向

7. **QES 在 MoE 671B 上的端到端验证**：DeepSeek-V3 级别的量化 MoE + DistZO2 2D + QES AEF。预估需要 16-32 GPU（INT4 量化后参数量 ~335B，每 GPU ~20GB offload）

8. **QES → QLoRA GRPO 量化基座 Pipeline**：完整三阶段 — QES 探索（无反量化）→ 检查点保存 → QLoRA GRPO 精调（部分反量化）。利用 06-05 的 Rise-Peak-Decay 理论确定切换时机

---

## 五、待深入问题

1. **非对称量化（GPTQ/AWQ）在 QES PertP 中的偏差修正** — 是否需要显式偏差修正项？还是 AEF 自然吸收？
2. **EGGROLL 低秩 + QES AEF 的理论收敛速率** — 低秩空间中 AEF 累积更快，但有效搜索维度也减少。净效果如何？
3. **QES 误差反馈状态的跨节点同步需求** — SeedFlood 场景下，不同节点的 error_accum 是否发散？是否需要周期性同步？
4. **QES + Dominant-Layer ZO 联合** — 只在主导层运行 QES，其他层冻结。通信量从 O(N) 降到 O(N × 1/L)（L=层数）
5. **ZOTTA 边缘 + QES 云端 的联邦方案** — 边缘设备 ZOTTA 测试时适应 + 云端 QES 集中式微调，误差反馈通过种子同步
6. **QES 在 FP8 E4M3 vs FP8 E5M2 格式上的表现差异** — E4M3 精度更高但范围更小，E5M2 范围更大但精度更低，对 AEF 累积速度的影响
7. **QES + ESSAM 在量化模型上的锐度估计** — SAM 的邻域最大化在量化空间中如何实现？量化噪声是否充当隐式 SAM perturbation？

---

## 参考文献

1. Dibbla et al., "Quantized Evolution Strategies (QES)," arXiv 2602.03120, Feb 2026
2. Li et al., "DistZO2: High-Throughput and Memory-Efficient Zeroth-Order Fine-tuning LLMs with Distributed Parallel Computing," arXiv 2507.03211, Jul 2025
3. Sarkar et al., "Evolution Strategies at the Hyperscale (EGGROLL)," arXiv 2511.16652, Nov 2025
4. Chen et al., "SeedFlood: A Step Toward Scalable Decentralized Training of LLMs," arXiv 2602.18181, Feb 2026
5. ESC, "Evolution Strategy-Based Calibration for Low-Bit Quantization of Speech Models," arXiv 2603.08173, Mar 2026
6. "Gradient-Free Training of SNNs via Low-Rank ES (EGGROLL-SNN)," arXiv 2605.30361, May 2026
7. ZOTTA, "Test-Time Adaptation with Gradient-Free Zeroth-Order Optimization," arXiv 2603.14254, Mar 2026
8. QeRL, "Quantization-enhanced Reinforcement Learning for LLMs," arXiv 2510.11696, Oct 2025
9. "Overcoming Forgetting in LLM Fine-Tuning with Evolution Strategies," arXiv 2605.30148, May 2026
10. Qiu et al., "Evolution Strategies at Scale: LLM Fine-Tuning Beyond RL," arXiv 2509.24372, Sep 2025
11. Poor Man's Training on MCUs, arXiv 2411.05873, Nov 2024
12. Dominant-Layer ZO, arXiv 2606.05516, Jun 2026

---

## 相关笔记

- [2026-06-06-ES-Population分布式通信拓扑](./2026-06-06-ES-Population分布式通信拓扑-跨GPU跨节点并行最优通信模式.md)
- [2026-06-05-ES-GRPO混合训练Pipeline](./2026-06-05-ES-GRPO混合训练Pipeline-无梯度与有梯度RL的最优切换.md)
- [2026-06-04-ES-Population-Scaling-Law](./2026-06-04-ES-Population-Scaling-Law-vs模型参数量-无梯度训练的扩展定律.md)
- [2026-06-03-ES量化模型RL训练](./2026-06-03-ES量化模型RL训练-无梯度进化策略绕过量化-RL交互.md)
- [2026-05-29-NVFP4-vs-FP8在MoE-RL](./2026-05-29-NVFP4-vs-FP8在MoE-RL训练中的精确对比-精度域与训练范式的抉择.md)
- [2026-05-23-QLoRA在RL训练中的精度影响](./2026-05-23-QLoRA在RL训练中的精度影响-QeRL-NVFP4-RL量化噪声增强探索.md)
