# LLM 推理优化 2026Q1 增量笔记：引擎对决与架构革命

> 主动学习 | 2026-05-18 | Topic: llm-inference-opt
> 增量更新 v3 | 聚焦：推理引擎对比、SSM架构、KV Cache压缩、量化新标准
> 前序笔记：llm-inference-opt-deep-dive.md → incremental-20260517.md → 2026-05-18-update.md

---

## 核心发现

### 发现1：推理引擎三足鼎立格局已定——vLLM vs SGLang vs TensorRT-LLM

2026 年初，生产级 LLM 推理引擎已形成明确的三方格局：

| 引擎 | 核心创新 | 最佳场景 | H100 70B FP8 吞吐 |
|------|---------|---------|-------------------|
| vLLM | PagedAttention | 通用部署、多模型支持 | ~1,600 tok/s |
| SGLang | RadixAttention | 多轮Agent、共享前缀 | ~1,750 tok/s |
| TensorRT-LLM | 图编译优化 | 固定模型极致吞吐 | ~2,100 tok/s |

**关键洞察**：问题不再是"用哪个引擎"，而是"这个工作负载用哪个引擎"。

- **vLLM**：行业标准，最广泛的模型支持，PagedAttention 以虚拟内存分页方式管理 KV cache
- **SGLang**：RadixAttention 用基数树自动发现并复用跨请求的共享前缀，Agent 工作流性能突出
- **TensorRT-LLM**：NVIDIA 生态深度绑定，编译时优化极致，但灵活性差

**实践启发**：Jetson Orin 上应优先用 llama.cpp + GGUF，因为 TensorRT-LLM 对 ARM64 CUDA 支持有限。云端部署可按工作负载选择 vLLM/SGLang。

### 发现2：RadixAttention vs PagedAttention——Agent 时代的内存革命

PagedAttention 的局限：60-80% 的预留 KV 内存被浪费（内部碎片+外部碎片），在复杂多轮 Agent 工作流中问题更严重。

**RadixAttention（SGLang）**：
- 将 KV cache 重构为基数树（Radix Tree）
- 自动发现并零成本复用跨请求的共享前缀（system prompt）
- 在 Agent swarm 场景（100+ agent 共享同一 system prompt）性能提升显著
- Fish Audio S2（4B 参数 TTS）已原生利用 SGLang 的所有优化

**MLA（Multi-Head Latent Attention，DeepSeek-V2/V3）**：
- 用低秩联合压缩替代完整 KV cache
- KV cache 压缩比可达 4-40x
- 已被 SGLang 和 vLLM 支持
- GQA 和 MLA 可统一视为"线性下投影到潜空间→上投影使用"的框架

### 发现3：Mamba-3（2026.03）——线性时间推理的转折点

Mamba-3 于 2026 年 3 月由 CMU/Princeton/Together AI（Albert Gu + Tri Dao）发布：
- 语言建模基准比 Transformer 基线高 **4%**
- 长序列推理速度 **7x** 快于 Transformer
- Apache 2.0 开源
- 固定大小隐状态，context 增长不影响内存占用

**架构本质**：SSM 将整个输入序列压缩为固定大小隐状态，逐 token 单次前向处理，复杂度 O(n) 而非 O(n²)。

**生产级应用**：
- Mistral Codestral Mamba：代码生成
- IBM Granite 4.0：内存减少 70%
- 混合架构（Mamba + Transformer）成为主流选择

**实践启发**：Jetson Orin Nano（8GB VRAM）上 Mamba 架构可能是长上下文推理的唯一可行方案，因为 KV cache 零增长。

---

## 技术细节

### KV Cache 五大优化家族（2026 工程实践）

根据最新工程指南，KV cache 优化分为五个家族：

| 优化技术 | 原理 | 适用场景 | 压缩比 |
|---------|------|---------|--------|
| PagedAttention | 虚拟内存分页 | 通用部署 | 减少 60-80% 碎片 |
| Prefix Caching | 前缀复用 | 多轮对话、Agent | 共享前缀零成本 |
| MQA/GQA | 头共享 | 注意力密集型 | 2-8x KV 减少 |
| MLA | 低秩压缩 | DeepSeek 模型 | 4-40x |
| KV Cache 量化 | INT8/FP8 | 长上下文 | 2x（精度损失<0.1%） |

> 在 128K context 以上，KV cache 占 GPU VRAM 70-90%。量化是最简单直接的优化手段。

### GGUF 量化新标准（llama.cpp 2026）

**I-quant（Importance Matrix Quantization）** 已成为激进压缩的首选：

```bash
# 生成重要性矩阵（推荐步骤，提高低比特量化质量）
./bin/imatrix -m models/llama3-70b-f16.gguf \
  -f data/wiki.train.raw \
  -o models/llama3.imatrix.dat -ngl 99

# 使用 imatrix 进行 I-quant 量化
./bin/imatrix -m models/llama3.imatrix.dat \
  models/llama3-70b-f16.gguf \
  models/llama3-70b-iq4_xs.gguf IQ4_XS
```

**量化方案推荐（2026）**：
- **Q5_K_M**：5-bit，质量/体积最佳平衡，适合消费级 GPU
- **IQ4_XS**：4-bit I-quant，最激进压缩，需要 imatrix
- **Q6_K**：6-bit，接近 FP16 质量，适合高端硬件
- **Q4_K_M**：4-bit K-quant，legacy 但广泛兼容

**关键数据**：
- 123B 模型 Q4_K_M ≈ 48GB → DGX Spark 可运行（~4 t/s）
- 70B 模型 Q5_K_M ≈ 4.6GB/权重块，M4 Max 128GB 统一内存可跑

### LLM API 价格暴跌趋势

2025-2026 年 LLM API 价格下跌约 **80%**：
- GPT-4 级性能：$0.40/M tokens（2026）vs $30/M tokens（2023.03）
- 推理优化是成本下降的核心驱动力

---

## 实践启发

1. **Jetson Orin 策略**：Mamba 混合架构 + GGUF I-quant 是边缘推理的甜蜜组合。长上下文场景 Mamba 唯一可行（KV cache 零增长）。

2. **Agent 工作流选 SGLang**：RadixAttention 自动复用 system prompt 的 KV cache，100+ agent swarm 场景吞吐提升显著。

3. **量化决策树**：先选架构（Transformer vs SSM），再选引擎（vLLM/SGLang/llama.cpp），最后选量化（Q5_K_M 起步，内存不够降 IQ4_XS）。

4. **价格趋势**：如果 API 成本已不是瓶颈，优先优化延迟而非吞吐。

---

## 知识缺口

1. **Mamba-3 实际部署案例不足**：目前主要是论文和基准测试，生产级部署经验（容错、监控、A/B 测试）缺失
2. **MLA 在非 DeepSeek 模型上的适配**：其他模型架构如何借鉴 MLA 低秩压缩？
3. **Modular MAX 引擎**：新兴第五引擎，Mojo 内核编译，声称在密集模型高并发下超过 vLLM，但实际数据少
4. **SSM + Transformer 混合架构的工程实践**：如何决定哪些层用 SSM，哪些用 Attention？
5. **FP8 训练-推理一体化**：训练时量化 vs 推理时量化的质量差异缺乏系统对比

---

*本笔记基于 2026-05-18 web_search 多源检索，覆盖 8 组关键词搜索结果*
*前序笔记：llm-inference-opt-deep-dive.md | incremental-20260517.md | 2026-05-18-update.md*

## 相关笔记
- [Karpathy-LLM-Wiki-second-brain](../2026-04-05-Karpathy-LLM-Wiki-second-brain.md)
- [Hermes-LLM-Wiki-学习笔记](../2026-04-18-Hermes-LLM-Wiki-学习笔记.md)
- [LLM推理优化前沿技术2026](../2026-04-28-LLM推理优化前沿技术2026.md)
- [LLM-Agent驱动量化交易系统前沿学习](../2026-04-29-LLM-Agent驱动量化交易系统前沿学习.md)
- [边缘AI与On-Device-LLM前沿学习](../2026-04-30-边缘AI与On-Device-LLM前沿学习.md)
- [deepseek-agent-ecosystem](../2026-05-01-deepseek-agent-ecosystem.md)
- [LLM对齐训练范式RLHF-DPO-GRPO-DAPO](../2026-05-04-LLM对齐训练范式RLHF-DPO-GRPO-DAPO.md)
- [开源AI模型2025-DeepSeek-Qwen新格局](../2026-05-05-开源AI模型2025-DeepSeek-Qwen新格局.md)
- [PageIndex-无向量推理式RAG](../2026-05-07-PageIndex-无向量推理式RAG.md)
- [大模型量化技术全景-GGUF-GPTQ-AWQ-FP8-BitNet](../2026-05-07-大模型量化技术全景-GGUF-GPTQ-AWQ-FP8-BitNet.md)
- [推理加速深度解析-投机解码-KVCache-连续批处理](../2026-05-08-推理加速深度解析-投机解码-KVCache-连续批处理.md)
- [LLM知识蒸馏技术全景](../2026-05-09-LLM知识蒸馏技术全景.md)
- [DeepSeek-V4-开源模型新格局](../2026-05-10-DeepSeek-V4-开源模型新格局.md)
- [蒸馏量化联合策略-QAD-LBLLM-CapacityGap](../2026-05-10-蒸馏量化联合策略-QAD-LBLLM-CapacityGap.md)
- [5月AI模型大战-GPT55-DeepSeekV4](../2026-05-11-5月AI模型大战-GPT55-DeepSeekV4.md)
- [AI趋势2026-推理时计算与反思Agent](../2026-05-11-AI趋势2026-推理时计算与反思Agent.md)
- [LLM冲击下PINN应用变化与发展](../2026-05-11-LLM冲击下PINN应用变化与发展.md)
- [MoE蒸馏与压缩-专家路由迁移-稀疏结构处理](../2026-05-11-MoE蒸馏与压缩-专家路由迁移-稀疏结构处理.md)
- [JAX-NVIDIA-GPU-微调Llama3.1实战方案](../2026-05-15-JAX-NVIDIA-GPU-微调Llama3.1实战方案.md)
- [LoRA高效微调前沿技术全景](../2026-05-17-LoRA高效微调前沿技术全景.md)
- [SGLang高性能LLM推理框架深度分析](../2026-05-17-SGLang高性能LLM推理框架深度分析.md)
- [Agent元认知-LLM不确定性感知](../2026-05-18-Agent元认知-LLM不确定性感知.md)
- [MoE模型LoRA微调最佳实践](../2026-05-18-MoE模型LoRA微调最佳实践.md)
- [蒸馏量化RL三联流水线-后训练范式统一](../2026-05-19-蒸馏量化RL三联流水线-后训练范式统一.md)
- [Active-Data-Selection-LLM训练动态数据选择前沿](../2026-05-20-Active-Data-Selection-LLM训练动态数据选择前沿.md)
- [AutoSearch 自主训练任务](../AutoSearch 自主训练任务.md)
- [2025年5月AI大爆发-Claude4-Qwen3-DeepSeek-R1](2026-05-09-2025年5月AI大爆发-Claude4-Qwen3-DeepSeek-R1.md)
- [开源AI春季爆发-模型推理Agent](2026-05-09-开源AI春季爆发-模型推理Agent.md)
- [LLM推理优化-MoE量化加速全景](2026-05-16-LLM推理优化-MoE量化加速全景.md)
- [LLM推理优化技术](2026-05-16-LLM推理优化技术.md)
- [llm-inference-opt-update](2026-05-18-llm-inference-opt-update.md)
- [llm-self-prompt-optimization](2026-05-18-llm-self-prompt-optimization.md)
- [MoE-稀疏激活微调工程实践](2026-05-19-MoE-稀疏激活微调工程实践.md)
- [SGLang-vs-vLLM-推理引擎对比](2026-05-19-SGLang-vs-vLLM-推理引擎对比.md)
- [llm_wiki分析与Skill进化](2026-05-20-llm_wiki分析与Skill进化.md)
- [llm-inference-opt-2026-05-17](llm-inference-opt-2026-05-17.md)
- [llm-inference-opt-incremental-20260517](llm-inference-opt-incremental-20260517.md)
- [llm-pid-tuner](../llm-pid-tuner.md)
- [分布式训练技术全景-FSDP-DeepSpeed-Megatron](../orphan/2026-05-05-分布式训练技术全景-FSDP-DeepSpeed-Megatron.md)
- [表达清晰的5个训练](../orphan/2026-05-16-表达清晰的5个训练.md)
- [tinyedge-lora](../tinyedge-lora.md)
- [前瞻性问题-AI垂域LLM载具设计](../前瞻性问题-AI垂域LLM载具设计.md)
