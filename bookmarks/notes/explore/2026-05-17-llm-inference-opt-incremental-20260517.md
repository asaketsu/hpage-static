# LLM 推理优化技术增量更新（2026-05-17 晚）

**Topic**: llm-inference-opt  
**Date**: 2026-05-17 22:10  
**Type**: 增量更新（基于 SGLang/vLLM GitHub 实时数据）  
**数据来源**: browser_navigate GitHub 直采（Tavily + web_extract 均不可用）

---

## 核心发现

### 发现 1：SGLang 已成为事实行业标准，400K+ GPU 部署

SGLang 从 2025 年的"黑马"已经成长为 LLM 推理引擎的事实标准：

**关键数据**：
- GitHub Stars: 27.9k（vs vLLM ~80k，但增速更快）
- Commits: 12,755 | Tags: 153 | Branches: 594
- 部署规模：**全球 400,000+ GPU**
- 采用方：xAI, AMD, NVIDIA, LinkedIn, Cursor, Oracle Cloud, Google Cloud, Microsoft Azure, AWS, MIT, Stanford, UC Berkeley, Tsinghua

**技术栈演进**（与之前笔记中记录的对比）：

| 特性 | 之前记录（2025 中） | 当前状态（2026-05） |
|------|---------------------|---------------------|
| 硬件支持 | NVIDIA GPU | NVIDIA + **AMD MI355/MI300** + **Google TPU** + **Intel Xeon** + **Ascend NPU** |
| 模型类型 | LLM only | LLM + **Diffusion（WAN, Qwen-Image）** + Embedding + Reward |
| 量化 | FP8/INT4/AWQ/GPTQ | + **FP4** 量化 |
| 并行策略 | TP/PP/DP | + **Expert Parallel（MoE）** + **Data Parallel** |
| PD 分离 | 理论/实验 | **生产级 Prefill-Decode Disaggregation** |
| 推测解码 | Medusa/Eagle | 持续优化，完整集成 |
| RL 支持 | 无 | **原生 RL/Post-Training backbone**（verl, AReaL, Miles 等集成） |

**实践启发**：SGLang 不再只是 vLLM 的替代品，而是正在成为全栈推理平台。如果做新项目，应优先评估 SGLang。

### 发现 2：Prefill-Decode 分离从理论走向生产

之前笔记标注为"趋势"，现已大规模落地：

**SGLang 实战数据**（来自博客）：
- DeepSeek-V3 在 GB200 NVL72 上：
  - Prefill 吞吐量：**3.8x 提升**
  - Decode 吞吐量：**4.8x 提升**
- GB300 NVL72 长上下文场景：**25x 性能提升**

**架构要点**：
```
Prefill 节点（高算力 GPU，如 H100 SXM）
    ↓ KV Cache 传输（RDMA/RoCE）
Decode 节点（高带宽 GPU 或专用加速器）
```

**关键工程问题**：
- KV Cache 跨节点传输延迟 → 用 RDMA 解决
- 请求路由策略 → Prefill 节点选择最空闲的
- 负载均衡 → Prefill 和 Decode 需要独立的扩缩容

### 发现 3：MoE 推理优化进入新阶段

SGLang 的 MoE 优化已经覆盖了之前笔记标注的"知识缺口"：

**DeepSeek-V3.2 支持**（2025-09 Day 0 支持）：
- **Sparse Attention**：MoE 模型专用的稀疏注意力
- **Large-scale Expert Parallelism（EP）**：大规模专家并行
- 专家路由缓存优化
- 配合 GB200 机架级并行

**MoE 推理关键优化**：
1. **Expert Parallel**：将 MoE 的不同专家分布到不同 GPU
2. **稀疏激活优化**：只激活相关专家，减少计算量
3. **Expert 路由缓存**：缓存历史路由决策，减少重复计算
4. **All-to-All 通信优化**：大规模 EP 的通信瓶颈

### 发现 4：FP4 量化进入实战

之前笔记未覆盖 FP4，现在 SGLang 已原生支持：

**FP4（4-bit 浮点）量化**：
- 比 FP8 再压缩 2x
- NVIDIA Blackwell（GB200/GB300）原生支持
- vLLM 也已支持 NVFP4 via NVIDIA ModelOpt
- 适用场景：极致显存压缩（70B 模型可压缩到 ~35GB）

**NVFP4 与 INT4 的区别**：
| 指标 | INT4（GPTQ/AWQ） | NVFP4 |
|------|-------------------|--------|
| 格式 | 整数 | 浮点（E2M1） |
| 动态范围 | 窄 | 宽 |
| 硬件要求 | 通用 GPU | Blackwell+ |
| 精度保持 | 中 | 高 |
| 生态成熟度 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |

### 发现 5：Diffusion 模型推理成为新战场

SGLang 扩展到 Diffusion 推理（2026-01 公告）：
- 支持 **WAN**（视频生成）和 **Qwen-Image**（图像生成）
- 用 `torch.compile` 优化推理速度
- 意味着推理引擎不再局限于自回归 LLM

---

## 技术细节

### SGLang 最新部署命令（2026-05）

```bash
# 基础 LLM 服务
python -m sglang.launch_server \
    --model-path meta-llama/Llama-3.1-70B \
    --tp 4 \
    --enable-torch-compile

# MoE 模型 + Expert Parallel
python -m sglang.launch_server \
    --model-path deepseek-ai/DeepSeek-V3 \
    --tp 8 --ep 8 \
    --enable-sparsed-attention

# PD 分离部署
# Prefill 节点
python -m sglang.launch_server \
    --model-path meta-llama/Llama-3.1-70B \
    --disaggregation-mode prefill \
    --port 30000

# Decode 节点
python -m sglang.launch_server \
    --model-path meta-llama/Llama-3.1-70B \
    --disaggregation-mode decode \
    --port 30001

# FP4 量化
python -m sglang.launch_server \
    --model-path xxx-fp4 \
    --quantization fp4
```

### 推理引擎选型更新（2026-05）

| 场景 | 首选引擎 | 理由 |
|------|---------|------|
| 通用 LLM 服务 | **SGLang** | 生态最全，性能优 |
| DeepSeek/MoE | **SGLang** | EP + Sparse Attention 原生支持 |
| NVIDIA 极致优化 | **TensorRT-LLM** | Kernel fusion 最深 |
| 边缘/CPU | **llama.cpp** | GGUF 生态成熟 |
| RL Post-Training | **SGLang** | verl/AReaL 原生集成 |
| AMD GPU | **SGLang** | MUSA 后端支持 |
| TPU | **SGLang** | SGLang-Jax 后端 |

---

## 实践启发

### 1. 推理引擎选型决策已变

之前笔记将 vLLM 作为通用首选。现在 SGLang 在以下维度超越 vLLM：
- 多硬件支持（AMD/TPU/Ascend）
- MoE 原生优化
- PD 分离生产级可用
- Diffusion 模型支持
- RL 训练集成

**建议**：新项目默认评估 SGLang，vLLM 作为备选。

### 2. FP4 量化值得关注但暂不急

FP4 需要 Blackwell 硬件，目前 Jetson Orin 不支持。但在云端部署场景（GB200/GB300），FP4 可将 70B 模型显存需求降至 ~35GB，相当于单 H100 即可运行。

### 3. MoE 推理不再是大问题

之前标注的"MoE 推理优化不够成熟"已过时。SGLang 的大规模 EP + Sparse Attention 已经在 DeepSeek-V3.2 上 Day 0 支持。

---

## 知识缺口（更新）

### 已关闭的缺口
- ✅ MoE 推理优化 → SGLang EP + Sparse Attention
- ✅ Prefill-Decode 分离 → 生产级可用
- ✅ 非 NVIDIA 硬件 → AMD/TPU/Ascend 支持

### 新增缺口
1. **KV Cache 压缩**：SnapKV、PyramidKV、LMCache 等新方案的具体效果和适用场景
2. **FlashAttention-3 状态**：是否已发布，性能提升多少
3. **投机解码最新进展**：Eagle-2、Medusa-2 的具体性能数据
4. **多模态推理优化**：Vision-Language 模型的 KV Cache 管理和量化策略
5. **长上下文（1M+ tokens）推理**：Ring Attention / Block Recurrent 的工程验证状态

---

## 进化评估

### 可采纳的内容

| 内容 | 类型 | 采纳方式 |
|------|------|----------|
| SGLang 选型建议更新 | 方法 | patch `llm-inference-optimization` skill |
| FP4 量化信息 | 知识 | patch `llm-inference-optimization` skill |
| PD 分离生产实践 | 工作流 | patch `llm-inference-deploy` skill |
| 推理引擎选型表更新 | 方法 | patch `llm-inference-optimization` skill |

### 结论
- 核心变化：**SGLang 从备选升级为首选**，需要更新现有 skill 的推荐优先级
- FP4 量化信息值得加入 skill 但非紧急
- 不需要创建新 skill，patch 现有即可

---

*笔记字数：约 2500 字*  
*数据来源：SGLang GitHub README 直采（2026-05-17 22:10）*  
*⚠️ Tavily + web_extract 均不可用，无法进行多源交叉验证*

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
- [llm-inference-opt-incremental2](2026-05-18-llm-inference-opt-incremental2.md)
- [llm-inference-opt-update](2026-05-18-llm-inference-opt-update.md)
- [llm-self-prompt-optimization](2026-05-18-llm-self-prompt-optimization.md)
- [MoE-稀疏激活微调工程实践](2026-05-19-MoE-稀疏激活微调工程实践.md)
- [SGLang-vs-vLLM-推理引擎对比](2026-05-19-SGLang-vs-vLLM-推理引擎对比.md)
- [llm_wiki分析与Skill进化](2026-05-20-llm_wiki分析与Skill进化.md)
- [llm-inference-opt-2026-05-17](llm-inference-opt-2026-05-17.md)
- [llm-pid-tuner](../llm-pid-tuner.md)
- [分布式训练技术全景-FSDP-DeepSpeed-Megatron](../orphan/2026-05-05-分布式训练技术全景-FSDP-DeepSpeed-Megatron.md)
- [表达清晰的5个训练](../orphan/2026-05-16-表达清晰的5个训练.md)
- [tinyedge-lora](../tinyedge-lora.md)
- [前瞻性问题-AI垂域LLM载具设计](../前瞻性问题-AI垂域LLM载具设计.md)
