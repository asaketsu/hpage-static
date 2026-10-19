# LLM 推理优化技术深度笔记

> 本地知识蒸馏 | 2026-05-16 | Topic: llm-inference-opt
> 难度: L4（深度探索）| 字数: ~3500

---

## 1. 核心发现

### 发现 1：Prefill-Decode 分离架构成为主流

传统 LLM 推理将请求处理分为两个阶段：
- **Prefill 阶段**：处理所有 input tokens，计算 KV Cache（计算密集型，可高度并行）
- **Decode 阶段**：逐 token 自回归生成（访存密集型，受限于 GPU 显存带宽）

**关键洞察**：这两个阶段对硬件资源的需求截然不同。Prefill 需要大量算力（FLOPS），Decode 需要大量带宽（HBM bandwidth）。

**最新架构趋势**（2025-2026）：
- **Splitwise**（Microsoft, 2024）：将 prefill 和 decode 分配到不同 GPU 集群
- **DistServe**（UC Berkeley, 2024）：独立资源池，按需扩缩容
- **Mooncake**（Kimi/Moonshot AI, 2024）：基于 KV Cache 的分离式调度

这种分离使得：
- Prefill 节点可以用高算力 GPU（如 H100 SXM）
- Decode 节点可以用高带宽 GPU 或甚至 CPU/NPU
- KV Cache 可以跨节点迁移，实现请求的"断点续传"

**实践启发**：对于自建推理服务，先搞清楚你的瓶颈是 prefill 还是 decode，然后针对性优化，比通用优化有效得多。

### 发现 2：投机解码（Speculative Decoding）从理论走向工程化

投机解码的核心思想：用一个小的"草稿模型"（draft model）快速生成 K 个候选 token，然后用目标模型并行验证这些 token，接受正确的、拒绝错误的。

**数学原理**：
- 草稿模型每 token 生成时间：`T_draft`
- 目标模型验证时间：`T_verify`（与序列长度无关，并行处理）
- 如果接受率（acceptance rate）为 `α`，每个验证步骤的期望 token 数为 `1/(1-α)`
- 加速比上限：`1/(1-α)`（当 `T_draft << T_verify` 时）

**2025-2026 关键进展**：

| 方案 | 特点 | 加速比 |
|------|------|--------|
| **Medusa** | 多头并行预测，无需独立草稿模型 | 2.0-3.0x |
| **Eagle** | 特征级草稿，利用最后一层隐状态 | 2.5-3.5x |
| **SpecInfer** | 树结构投机，多个草稿模型组合 | 2.0-2.8x |
| **Self-Speculative** | 同一模型早退作为草稿 | 1.5-2.2x |
| **Eagle-2**（2025） | 动态草稿长度调整 | 3.0-4.0x |

**工程实现要点**：
```python
# vLLM 中的投机解码配置示例
from vllm import LLM, SamplingParams

# 方法1：使用独立草稿模型
llm = LLM(
    model="meta-llama/Llama-3.1-70B",
    speculative_model="meta-llama/Llama-3.1-8B",  # 草稿模型
    num_speculative_tokens=5,  # 候选 token 数
    speculative_max_model_len=2048,
)

# 方法2：使用 Medusa（无需独立模型）
llm = LLM(
    model="meta-llama/Llama-3.1-70B",
    speculative_model="[medusa]",
    num_speculative_tokens=6,
)
```

**知识缺口**：
- 投机解码在非自回归任务（如翻译、摘要）中的效果不明确
- 草稿模型与目标模型的"分布对齐"问题尚未完全解决
- 多轮对话场景下 KV Cache 管理的投机解码优化方案较少

### 发现 3：量化进入 FP8 时代，GPTQ/AWQ/GGUF 三足鼎立

**量化格式对比**：

| 格式 | 精度保持 | 推理速度 | 内存占用 | 灵活性 | 适用场景 |
|------|---------|---------|---------|--------|---------|
| **FP8 (E4M3/E5M2)** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | H100/AMD MI300 训练+推理 |
| **GPTQ (INT4)** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ | GPU 批量推理 |
| **AWQ (INT4)** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | GPU 实时推理 |
| **GGUF (Q4_K_M)** | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | CPU/混合推理（Jetson 适用） |
| **BitsAndBytes NF4** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | 训练时量化（QLoRA） |

**FP8 量化的关键突破**：
- NVIDIA H100 原生支持 FP8 Tensor Core
- **Calibration-free**：无需校准数据集，直接缩放即可
- 训练和推理统一格式，消除量化/反量化开销
- Google 研究表明 FP8 在大多数任务上精度损失 <0.1%

**AWQ vs GPTQ 深度对比**：
- **AWQ（Activation-aware Weight Quantization）**：
  - 保护"显著权重"（salient weights）：通过激活值大小识别
  - 缩放而非裁剪：对显著通道乘以缩放因子再量化
  - 推理更快：支持 Tensor Core，无需反量化
  - 代表实现：`autoawq` 库，vLLM 原生支持

- **GPTQ（Gradient-based Post-Training Quantization）**：
  - 基于 Hessian 矩阵的逐层量化
  - 需要校准数据集（通常 128 条样本）
  - 量化精度高，但推理速度略逊于 AWQ
  - 代表实现：`auto-gptq`，`gptq_marlin`（vLLM 最快后端）

**Jetson Orin 场景推荐**：
```
Jetson Orin Nano (8GB) → GGUF Q4_K_M（CPU推理）+ CUDA offload
Jetson Orin NX (16GB) → AWQ INT4（GPU推理）或 GGUF Q5_K_M
```

---

## 2. 技术深度：推理引擎架构对比

### 2.1 vLLM（UC Sky Lab）

**核心创新：PagedAttention**
- 类比操作系统虚拟内存管理
- KV Cache 按"页"分配，无需连续显存
- 解决显存碎片化问题，支持更大 batch size

**关键特性**：
```
vLLM PagedAttention 工作流：
1. 每个 sequence 的 KV Cache 按固定大小的 block 分配
2. Block Table 映射 logical block → physical block
3. 新 token 只需分配新 block，不需重分配整个 cache
4. 支持 prefix caching（共享 prompt 的 KV Cache 复用）
```

**vLLM 0.6+ 新特性**：
- Chunked Prefill：将长 prompt 分块处理，避免一个请求独占 GPU
- Prefix Caching：相同 system prompt 的请求共享 KV Cache
- 多模态支持：LLaVA、Phi-3-Vision 等
- 投机解码：原生支持 Medusa/Eagle/Ngram

### 2.2 TensorRT-LLM（NVIDIA）

**核心优势**：极致性能优化
- Kernel fusion：将多个 CUDA kernel 合并
- IN-Flight Batching：动态批处理
- KV Cache 量化：FP8/INT8 KV Cache 减少 50% 显存
- Tensor Parallelism：多 GPU 并行

**适用场景**：
- 生产环境部署（延迟敏感）
- NVIDIA GPU 专属优化
- 需要极致吞吐量的场景

### 2.3 TGI（HuggingFace）

**核心优势**：易用性 + 生态
- Flash Attention 2 集成
- Safetensors 快速加载
- 水线批处理（Continuous Batching）
- OpenAI 兼容 API

### 2.4 SGLang（UC Berkeley）

**2025 黑马**：
- RadixAttention：基于 Radix Tree 的 KV Cache 复用
- 在多轮对话和复杂 prompt 场景下显著优于 vLLM
- 支持 OpenAI 兼容 API

**性能对比**（2025 基准，Llama-3.1-70B，A100）：

| 引擎 | 吞吐量 (tok/s) | 首 token 延迟 (TTFT) | P99 延迟 | 显存效率 |
|------|---------------|---------------------|---------|---------|
| vLLM 0.6 | ~2800 | ~180ms | ~800ms | 85% |
| TensorRT-LLM | ~3500 | ~120ms | ~500ms | 90% |
| SGLang | ~3200 | ~150ms | ~600ms | 88% |
| TGI 2.0 | ~2600 | ~200ms | ~900ms | 82% |

---

## 3. 技术细节与代码示例

### 3.1 KV Cache 优化三件套

```python
# 1. KV Cache 量化（减少显存占用 50-75%）
# vLLM 启动参数
python -m vllm.entrypoints.openai.api_server \
    --model meta-llama/Llama-3.1-70B \
    --kv-cache-dtype fp8_e5m2 \      # FP8 KV Cache
    --gpu-memory-utilization 0.95

# 2. Prefix Caching（复用共享 prompt 的 KV Cache）
python -m vllm.entrypoints.openai.api_server \
    --model meta-llama/Llama-3.1-70B \
    --enable-prefix-caching \         # 开启前缀缓存
    --block-size 16

# 3. Chunked Prefill（避免长 prompt 阻塞）
python -m vllm.entrypoints.openai.api_server \
    --model meta-llama/Llama-3.1-70B \
    --max-num-batched-tokens 4096 \   # 每批最大 token 数
    --enable-chunked-prefill true
```

### 3.2 量化部署实战

```bash
# AWQ 量化（推荐用于 GPU 推理）
python -m awq.entry --entry_type autoawq \
    --model_path meta-llama/Llama-3.1-70B \
    --w_bit 4 --q_group_size 128 \
    --output_path ./llama-3.1-70b-awq

# GPTQ 量化（精度更高）
python -m auto_gptq quantize \
    --model meta-llama/Llama-3.1-70B \
    --bits 4 --group-size 128 \
    --desc-act True \                 # 启用激活排序
    --output_dir ./llama-3.1-70b-gptq

# GGUF 转换（llama.cpp，推荐 CPU/混合推理）
python convert_hf_to_gguf.py \
    meta-llama/Llama-3.1-70B \
    --outfile llama-3.1-70b.gguf \
    --outtype f16
# 然后量化
./llama-quantize llama-3.1-70b.gguf llama-3.1-70b-Q4_K_M.gguf Q4_K_M
```

### 3.3 知识蒸馏（Knowledge Distillation）

```python
"""
LLM 知识蒸馏核心流程：
大模型(Teacher) → 小模型(Student)

三种蒸馏范式：
1. Logit Distillation：匹配输出概率分布
2. Feature Distillation：匹配中间层表示
3. Data Distillation：用 Teacher 生成数据训练 Student
"""

import torch
import torch.nn.functional as F

def distillation_loss(student_logits, teacher_logits, labels, 
                      alpha=0.5, temperature=2.0):
    """
    经典 Hinton 蒸馏损失
    L = α * KL(soft_student || soft_teacher) + (1-α) * CE(student, labels)
    """
    # 软标签损失（KL 散度）
    soft_student = F.log_softmax(student_logits / temperature, dim=-1)
    soft_teacher = F.softmax(teacher_logits / temperature, dim=-1)
    kl_loss = F.kl_div(soft_student, soft_teacher, reduction='batchmean')
    kl_loss = kl_loss * (temperature ** 2)  # 补偿温度缩放
    
    # 硬标签损失（交叉熵）
    ce_loss = F.cross_entropy(student_logits, labels)
    
    return alpha * kl_loss + (1 - alpha) * ce_loss


# 最新进展：MiniLLM（2024）- 序列级蒸馏
# 使用 KL 散度的反向变体，避免 student 模式崩塌
# GKD（Google, 2024）- 无需 teacher 数据，on-policy 蒸馏
```

---

## 4. 实践启发

### 4.1 推理优化决策树

```
你的瓶颈是什么？
├── 延迟（Latency）→ 首 token 太慢
│   ├── Speculative Decoding（减少 decode 步数）
│   ├── Chunked Prefill（避免长 prompt 阻塞）
│   └── KV Cache 量化（减少内存搬运）
├── 吞吐量（Throughput）→ 单位时间处理请求太少
│   ├── Continuous Batching（vLLM/SGLang）
│   ├── Prefill-Decode 分离（大规模部署）
│   └── 量化（减少单请求资源占用 → 放更大 batch）
├── 显存（Memory）→ 模型放不下
│   ├── 量化 INT4/FP8（4x-8x 压缩）
│   ├── CPU Offloading（GGUF，牺牲速度）
│   └── 模型并行（TP/PP，多 GPU）
└── 成本（Cost）→ GPU 太贵
    ├── Spot Instance + 量化（性价比最高）
    ├── CPU 推理（llama.cpp + GGUF）
    └── 蒸馏到小模型（长期最优解）
```

### 4.2 Jetson Orin 本地推理最佳实践

```bash
# Jetson Orin Nano Super (8GB) 推荐配置
# 使用 llama.cpp + GGUF Q4_K_M
./llama-server \
    -m qwen2.5-7b-q4_k_m.gguf \
    -ngl 24 \                        # GPU 层数（按显存调整）
    -c 4096 \                        # 上下文长度
    --temp 0.7 \
    --batch-size 512

# 性能预期：
# Qwen2.5-7B Q4_K_M: ~15 tok/s (混合推理)
# Qwen2.5-3B Q4_K_M: ~30 tok/s (全 GPU)
# Qwen2.5-14B Q4_K_M: ~8 tok/s (大量 CPU offload)
```

### 4.3 生产部署 Checklist

- [ ] 量化选型：AWQ（GPU）/ GGUF（CPU/混合）/ FP8（H100）
- [ ] 推理引擎：vLLM（通用）/ SGLang（多轮对话）/ TRT-LLM（极致性能）
- [ ] KV Cache：FP8 量化 + Prefix Caching + Chunked Prefill
- [ ] 批处理：Continuous Batching（必须）
- [ ] 投机解码：Medusa（易用）/ Eagle（快）/ 小模型草稿（精度高）
- [ ] 监控：TTFT / TPOT / 吞吐量 / 显存利用率 / 请求队列深度

---

## 5. 知识缺口

1. **MoE 模型的推理优化**：Mixtral/DeepSeek-V3 等稀疏模型的 KV Cache 管理和量化策略还不够成熟
2. **长上下文推理**：100K+ token 的 KV Cache 管理仍是开放问题（Ring Attention / Block Recurrent 方案有待工程验证）
3. **非 NVIDIA 硬件**：AMD MI300 / Intel Gaudi / 华为昇腾的推理优化生态远不如 CUDA
4. **多模态推理**：Vision-Language 模型的推理优化与纯文本有本质区别，研究较少
5. **模型合并后的推理效率**：Mergekit 等模型合并工具的产物在推理时是否有额外开销，缺乏系统研究
6. **投机解码在 function calling 场景**：结构化输出（JSON/function call）场景下投机解码的接受率会显著下降

---

## 6. 进化评估

### 可采纳的新知识
| 内容 | 类型 | 采纳方式 |
|------|------|---------|
| vLLM 投机解码配置 | 工作流 | 已在 `llm-inference-deploy` skill 中覆盖 |
| AWQ vs GPTQ 选型决策 | 方法 | 已在 `gguf-quantization` skill 中覆盖 |
| Jetson Orin 推理配置 | 环境配置 | 已在 `nexa-local-inference` skill 中覆盖 |

**结论**：本次学习的核心知识已被现有 skill 体系覆盖，不需要创建新 skill。但笔记本身有参考价值，保留在 explore/ 目录。

---

*笔记完成 | 本地知识蒸馏模式（外部搜索不可用）| 产出字数: ~3500*

## 相关笔记
- [Karpathy-LLM-Wiki-second-brain](../2026-04-05-Karpathy-LLM-Wiki-second-brain.md)
- [Hermes-LLM-Wiki-学习笔记](../2026-04-18-Hermes-LLM-Wiki-学习笔记.md)
- [MCP协议与Agentic-LLM-2025趋势](../2026-04-23-MCP协议与Agentic-LLM-2025趋势.md)
- [垂域LLM指导航空结构设计](../2026-04-27-垂域LLM指导航空结构设计.md)
- [LLM推理优化前沿技术2026](../2026-04-28-LLM推理优化前沿技术2026.md)
- [LLM-Agent驱动量化交易系统前沿学习](../2026-04-29-LLM-Agent驱动量化交易系统前沿学习.md)
- [边缘AI与On-Device-LLM前沿学习](../2026-04-30-边缘AI与On-Device-LLM前沿学习.md)
- [deepseek-agent-ecosystem](../2026-05-01-deepseek-agent-ecosystem.md)
- [LLM对齐训练范式RLHF-DPO-GRPO-DAPO](../2026-05-04-LLM对齐训练范式RLHF-DPO-GRPO-DAPO.md)
- [Awesome-LLM-Apps-109K星应用模板库](../2026-05-05-Awesome-LLM-Apps-109K星应用模板库.md)
- [开源AI模型2025-DeepSeek-Qwen新格局](../2026-05-05-开源AI模型2025-DeepSeek-Qwen新格局.md)
- [PageIndex-无向量推理式RAG](../2026-05-07-PageIndex-无向量推理式RAG.md)
- [大模型量化技术全景-GGUF-GPTQ-AWQ-FP8-BitNet](../2026-05-07-大模型量化技术全景-GGUF-GPTQ-AWQ-FP8-BitNet.md)
- [ollama-vllm-llamacpp-deploy-comparison](../2026-05-08-ollama-vllm-llamacpp-deploy-comparison.md)
- [推理加速深度解析-投机解码-KVCache-连续批处理](../2026-05-08-推理加速深度解析-投机解码-KVCache-连续批处理.md)
- [LLM知识蒸馏技术全景](../2026-05-09-LLM知识蒸馏技术全景.md)
- [DeepSeek-V4-开源模型新格局](../2026-05-10-DeepSeek-V4-开源模型新格局.md)
- [蒸馏量化联合策略-QAD-LBLLM-CapacityGap](../2026-05-10-蒸馏量化联合策略-QAD-LBLLM-CapacityGap.md)
- [5月AI模型大战-GPT55-DeepSeekV4](../2026-05-11-5月AI模型大战-GPT55-DeepSeekV4.md)
- [AI趋势2026-推理时计算与反思Agent](../2026-05-11-AI趋势2026-推理时计算与反思Agent.md)
- [LLM冲击下PINN应用变化与发展](../2026-05-11-LLM冲击下PINN应用变化与发展.md)
- [MoE蒸馏与压缩-专家路由迁移-稀疏结构处理](../2026-05-11-MoE蒸馏与压缩-专家路由迁移-稀疏结构处理.md)
- [MoE投机解码-稀疏激活与推理加速深度解析](../2026-05-13-MoE投机解码-稀疏激活与推理加速深度解析.md)
- [从零训练GPT完整指南](../2026-05-13-从零训练GPT完整指南.md)
- [JAX-NVIDIA-GPU-微调Llama3.1实战方案](../2026-05-15-JAX-NVIDIA-GPU-微调Llama3.1实战方案.md)
- [序列并行与上下文并行-长上下文训练的第四维并行](../2026-05-15-序列并行与上下文并行-长上下文训练的第四维并行.md)
- [LoRA高效微调前沿技术全景](../2026-05-17-LoRA高效微调前沿技术全景.md)
- [SGLang高性能LLM推理框架深度分析](../2026-05-17-SGLang高性能LLM推理框架深度分析.md)
- [Agent元认知-LLM不确定性感知](../2026-05-18-Agent元认知-LLM不确定性感知.md)
- [MoE模型LoRA微调最佳实践](../2026-05-18-MoE模型LoRA微调最佳实践.md)
- [蒸馏量化RL三联流水线-后训练范式统一](../2026-05-19-蒸馏量化RL三联流水线-后训练范式统一.md)
- [Active-Data-Selection-LLM训练动态数据选择前沿](../2026-05-20-Active-Data-Selection-LLM训练动态数据选择前沿.md)
- [MLA多头潜在注意力-DeepSeek-KV缓存压缩与推理优化](../2026-05-21-MLA多头潜在注意力-DeepSeek-KV缓存压缩与推理优化.md)
- [llm-finetune-dataflow-dataflex-pipeline](../2026-05-21-llm-finetune-dataflow-dataflex-pipeline.md)
- [react-agent-llm-agentic-training-research](../2026-05-21-react-agent-llm-agentic-training-research.md)
- [20260513-llm-wiki-obsidian-gbrain-知识自组织与自进化](../20260513-llm-wiki-obsidian-gbrain-知识自组织与自进化.md)
- [AutoSearch 自主训练任务](../AutoSearch 自主训练任务.md)
- [多目标GRPO-GDPO-AW-GRPO-Reward融合与冲突消解](../ai-agent/2026-05-14-多目标GRPO-GDPO-AW-GRPO-Reward融合与冲突消解.md)
- [MegatronCore模块化重构与MoE训练前沿](../ai-agent/2026-05-16-MegatronCore模块化重构与MoE训练前沿.md)
- [表达清晰的5个训练](../ai-agent/2026-05-16-表达清晰的5个训练.md)
- [2025年5月AI大爆发-Claude4-Qwen3-DeepSeek-R1](2026-05-09-2025年5月AI大爆发-Claude4-Qwen3-DeepSeek-R1.md)
- [开源AI春季爆发-模型推理Agent](2026-05-09-开源AI春季爆发-模型推理Agent.md)
- [2026年5月AI模型大战-GPT5.5-Grok4.3-DeepSeekV4](2026-05-13-2026年5月AI模型大战-GPT5.5-Grok4.3-DeepSeekV4.md)
- [开源AI模型新格局-DeepSeek冲击波](2026-05-13-开源AI模型新格局-DeepSeek冲击波.md)
- [LLM推理优化-MoE量化加速全景](2026-05-16-LLM推理优化-MoE量化加速全景.md)
- [LLM推理优化技术](2026-05-16-LLM推理优化技术.md)
- [llm-inference-opt-incremental2](2026-05-18-llm-inference-opt-incremental2.md)
- [llm-inference-opt-update](2026-05-18-llm-inference-opt-update.md)
- [llm-self-prompt-optimization](2026-05-18-llm-self-prompt-optimization.md)
- [MoE-稀疏激活微调工程实践](2026-05-19-MoE-稀疏激活微调工程实践.md)
- [SGLang-vs-vLLM-推理引擎对比](2026-05-19-SGLang-vs-vLLM-推理引擎对比.md)
- [llm_wiki分析与Skill进化](2026-05-20-llm_wiki分析与Skill进化.md)
- [边缘AI推理优化-Jetson平台深度研究](2026-05-21-边缘AI推理优化-Jetson平台深度研究.md)
- [llama-cpp预编译二进制与本地LLM推理](2026-05-22-llama-cpp预编译二进制与本地LLM推理.md)
- [llm-inference-opt-2026-05-17](llm-inference-opt-2026-05-17.md)
- [llm-inference-opt-incremental-20260517](llm-inference-opt-incremental-20260517.md)
- [llm-pid-tuner](../llm-pid-tuner.md)
- [llm-wiki-gbrain-agent-evolution_33aa818c](../llm-wiki-gbrain-agent-evolution_33aa818c.md)
- [分布式训练技术全景-FSDP-DeepSpeed-Megatron](../orphan/2026-05-05-分布式训练技术全景-FSDP-DeepSpeed-Megatron.md)
- [MoE混合专家模型-路由策略-负载均衡-训练稳定性](../orphan/2026-05-06-MoE混合专家模型-路由策略-负载均衡-训练稳定性.md)
- [tinyedge-lora](../tinyedge-lora.md)
- [前瞻性问题-AI垂域LLM载具设计](../前瞻性问题-AI垂域LLM载具设计.md)
