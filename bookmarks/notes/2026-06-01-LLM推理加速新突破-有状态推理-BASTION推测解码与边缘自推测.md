# LLM 推理加速新突破：有状态推理、BASTION 推测解码与边缘自推测

> 📅 2026-06-01 | 夜间自学习
> 🔗 来源：arXiv:2605.26289 (Stateful Inference) + arXiv:2605.29727 (BASTION) + arXiv:2605.26558 (Cassandra)
> 🏷️ 关键词：LLM 推理优化、推测解码、有状态推理、边缘部署、KV Cache

---

## 一、核心问题

LLM 推理加速有三个关键场景：
1. **多轮 Agent 工具调用**：85-95% 的 prompt 在轮次间不变，但现有框架每次从头处理
2. **推测解码效率**：block-diffusion 方法可以一次预测多个 token，但贪心路径选择效果差
3. **边缘设备推理**：消费级 GPU 缺乏高性能推测解码方案

---

## 二、有状态推理：从 O(n) 到 O(Δ)

**论文**：arXiv:2605.26289 — "Stateful Inference for Low-Latency Multi-Agent Tool Calling"

### 2.1 问题定义

多 Agent 工具调用是当前 LLM 系统的主流交互模式。但在 6 轮 agentic 工作流中，每轮工具调用都重新处理整个对话——即使 85-95% 的内容完全相同。

### 2.2 核心架构

```
传统推理：每轮处理 O(n_t) tokens（n_t = 完整对话长度）
有状态推理：每轮只处理 O(Δ_t) tokens（Δ_t = 新增内容）
```

**三大组件**：

1. **持久 KV Cache**：跨轮次存活，仅摄入新增 token
2. **Radix 前缀缓存**：跨交错多 Agent 流量共享前缀（多个 Agent 并行时共享公共上下文）
3. **Prompt-Lookup 推测解码器**：加速结构化输出（JSON/工具调用格式）

### 2.3 实验结果

| 场景 | vs vLLM | vs SGLang |
|------|---------|-----------|
| 6 轮工作流（每轮加速） | **2.1x** | - |
| 35 轮工作流（中位轮次） | **4.2x** | - |
| 端到端墙钟时间 | **减半** | - |

**关键洞察**：加速来自"有状态复用 + 推测"，而不仅仅是缓存。传统 KV Cache 复用 + Radix 前缀匹配 + 结构化输出推测三者协同，效果远超单一优化。

### 2.4 对 Hermes 的直接价值

Hermes cron 任务频繁调用 LLM，且许多工作流是多轮 Agent 模式（如 kanban worker、coding agent）。如果能实现有状态推理：
- 多轮 delegate_task 的上下文传递开销减少 4x+
- cron 任务的 LLM token 消耗大幅降低
- 特别适合"工具调用密集"场景（如代码生成→编译→修复循环）

---

## 三、BASTION：预算感知树状推测解码

**论文**：arXiv:2605.29727 — "BASTION: Budget-Aware Speculative Decoding with Tree-structured Block Diffusion Drafting"

### 3.1 Block-Diffusion 的问题

Block-diffusion drafter 可以一次并行预测多个未来 token 的分布。但由于这些预测来自逐位置的边际分布（而非完整条件序列），选择单一贪心路径往往无法捕捉目标模型偏好的轨迹。

### 3.2 BASTION 的三组件协同

```
[Block-Diffusion Drafter] → 生成候选树
    ↓
[1] 接受度代理（Acceptance Surrogate）
    → 通过路径置信度估算期望接受长度
    ↓
[2] 在线延迟估计器（Online Latency Estimator）
    → 校准硬件感知的 Roofline 模型
    ↓
[3] 自适应最佳优先展开（Adaptive Best-First Expansion）
    → 持续展开树直到边际收益不再验证额外验证成本
```

### 3.3 关键特性

- **免训练**：不需要额外训练 draft 模型或目标模型
- **保持分布**：严格保持目标模型的输出分布（无损加速）
- **免调参**：无需针对特定硬件或工作负载手动调参
- **动态树拓扑**：不同于静态树方法，BASTION 根据查询内容动态构建树

### 3.4 实验结果

- 最高 **6.61x** 加速（超过标准自回归解码）
- 比最先进的 block-diffusion 基线高出 **39%**
- 跨多种 benchmark 和 GPU 架构一致有效

---

## 四、Cassandra：边缘设备自推测解码

**论文**：arXiv:2605.26558 — "Cassandra: Enabling Reasoning LLMs at Edge via Self-Speculative Decoding"

### 4.1 边缘推理的痛点

推理 LLM（如带 chain-of-thought 的模型）在解码阶段开销大，而近似方法会降低准确率。现有的自推测解码方法（层跳过、结构化 KV 压缩）在低批次场景下效率不足。

### 4.2 Cassandra 的算法-硬件协同设计

**核心思路**：通过精细的数据选择，从目标模型本身构建一个高性能的"免费"draft 模型。

```
目标模型（BF16 精度）
    ↓ 优化的剪枝 + 尾数截断
    ↓ 识别权重和 KV Cache 中最显著的值
Draft 模型（Cassandra 表示）
    ↓ 快速生成候选 token
目标模型（全精度并行验证）
```

### 4.3 硬件加速模块

为减少 Cassandra 表示和标准浮点格式之间的转换开销，引入轻量级 encoder-decoder 硬件模块，可与商用 GPU 和 NPU 无缝集成。

### 4.4 实验结果

- 最高 **2.41x** 加速（vs BF16 基线，无需额外训练）
- 在 Llama 3 系列上验证有效
- 特别适合消费级 GPU 的低批次场景

### 4.5 对 Jetson Orin 的意义

Cassandra 专为"消费级设备"优化：
- **无需训练**：直接在现有模型上应用
- **低批次最优**：Jetson Orin 上的推理通常是 batch=1，正是 Cassandra 的最佳场景
- **NPU 兼容**：硬件加速模块支持 NPU，Jetson 的 Tensor Core 可直接利用
- **推理模型加速**：Hermes 的长链推理（如 deep-analysis skill）可用 Cassandra 加速

---

## 五、横向洞察：三条推理加速技术路线

| 路线 | 代表方法 | 核心思路 | 适用场景 | 加速比 |
|------|----------|----------|----------|--------|
| **有状态复用** | Stateful Inference | 跨轮次复用 KV Cache | 多轮 Agent 工具调用 | 2.1-4.2x |
| **推测解码** | BASTION | 动态树状 draft+verify | 通用 LLM 推理 | 最高 6.61x |
| **自推测** | Cassandra | 目标模型自身做 draft | 边缘设备低批次 | 2.41x |

**三路线互补**：
- 有状态复用解决"多轮"问题
- 推测解码解决"单轮生成"问题
- 自推测解决"边缘部署"问题

理论上可以叠加：有状态 KV Cache + Cassandra 自推测 + BASTION 树状验证 → 边缘 Agent 推理的终极加速方案。

---

## 六、对 Hermes 的改进建议

### 6.1 直接可落地

1. **有状态推理适配**：评估 vLLM/SGLang 的有状态推理支持状态，为 cron 多轮任务配置 KV Cache 复用
2. **Cassandra on Jetson**：在 Jetson Orin 上测试 Cassandra 自推测解码，预期 2x+ 加速本地推理
3. **推测解码升级**：当前 `llm-inference-optimization` skill 已记录 EAGLE-3 和 Mirror-SD，需追加 BASTION

### 6.2 需要进一步研究

- 有状态推理与 MCP 工具调用的兼容性（MCP 的状态管理 vs KV Cache 状态）
- Cassandra 在 Arm 架构（Jetson）上的硬件加速模块适配
- BASTION 的动态树构建在 Jetson 有限 VRAM 下的内存效率

---

## 七、参考资料

- arXiv:2605.26289 — Stateful Inference for Low-Latency Multi-Agent Tool Calling
- arXiv:2605.29727 — BASTION: Budget-Aware Speculative Decoding with Tree-structured Block Diffusion Drafting
- arXiv:2605.26558 — Cassandra: Enabling Reasoning LLMs at Edge via Self-Speculative Decoding
- arXiv:2605.29707 — Domino: Decoupling Causal Modeling from Autoregressive Drafting in Speculative Decoding
- arXiv:2605.29343 — Draft-OPD: On-Policy Distillation for Speculative Draft Models

## 相关笔记
- [[2026-05-31-LLM-Agent多智能体信用归因与自进化|05-31-LLM-Agent多智能体信用归因与自进化]]
- [[2026-05-31-agent两条路线-harness-vs-protocol|05-31-agent两条路线-harness-vs-protocol]]
- [[2026-06-01-AI-Agent安全前沿-AIRGuard运行时权限控制与越权行为检测|06-01-AI-Agent安全前沿-AIRGuard运行时权限控制与越权行为检测]]
- [[2026-05-21-MLA多头潜在注意力-DeepSeek-KV缓存压缩与推理优化|05-21-MLA多头潜在注意力-DeepSeek-KV缓存压缩与推理优化]]
