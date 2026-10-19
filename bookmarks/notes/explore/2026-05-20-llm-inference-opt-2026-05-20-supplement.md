# LLM 推理优化补充笔记（2026-05-20）

> 探索日期：2026-05-20
> 主题：知识蒸馏新范式 + 量化选型矩阵更新 + RadixAttention 深度分析
> 来源：ICML 2025 DA-KD, NeurIPS 2024 Compact LM, vrlatech.com 量化对比, SGLang RadixAttention 文档

---

## 核心发现

### 发现 1：知识蒸馏 2025-2026 三大范式升级

知识蒸馏已从简单的 logit 匹配演进为三大互补方向：

#### 1.1 难度感知蒸馏 DA-KD（ICML 2025）

- **核心思想**：不同样本难度差异大，简单样本的蒸馏是不必要的浪费
- **方法**：动态调整蒸馏数据集，根据样本难度筛选 — 简单样本跳过，困难样本集中训练
- **优化改进**：针对困难样本集中时优化不稳定的问题，设计了新的 KD loss
- **收益**：训练成本显著降低，同等计算资源下蒸馏质量提升
- **实践启发**：做蒸馏数据集时，不要均匀采样，按样本难度加权采样

#### 1.2 数据集蒸馏 DD

- **核心思想**：不蒸馏模型，蒸馏数据集 — 从教师模型合成紧凑高信息量的数据集
- **技术路径**：
  - 优化梯度匹配（gradient matching）
  - 潜空间正则化（latent space regularization）
  - 生成式合成（generative synthesis）
- **与 KD 的关系**：DD 是 KD 的互补技术 — DD 产生高质量小数据集，KD 在其上训练学生模型
- **关键洞察**：对 LLM 而言，DD 的价值在于能将教师模型的复杂知识压缩到少量精炼样本中，降低蒸馏的推理成本

#### 1.3 多教师 + 跨模态蒸馏

- **多教师蒸馏**：从多个专家模型（不同领域/能力）向单一学生模型迁移知识
- **跨模态蒸馏**：从多模态教师（如 GPT-4V）向轻量单模态学生迁移高维理解能力
- **2025 趋势**：开放权重模型（LLaMA 3、Mistral）使得大规模蒸馏成为可能，蒸馏从"效率技巧"变为"知识转移协议"

**蒸馏 vs 量化 vs 剪枝 选型指南：**

| 场景 | 首选技术 | 理由 |
|------|----------|------|
| 需要保持模型大小不变 | 量化（FP8/INT4） | 零训练成本，即插即用 |
| 需要大幅缩小模型 | 蒸馏 | 产生更小的新模型 |
| 特定领域任务优化 | 任务蒸馏 | 保留领域能力，丢弃无关知识 |
| 边缘部署 | 蒸馏 + 量化 | 先蒸馏到小模型，再量化 |
| 需要自定义模型大小 | 剪枝 + 蒸馏 | 结构化剪枝再蒸馏恢复精度 |

### 发现 2：2026 量化方案精确选型矩阵

基于最新基准测试的精确推荐：

| 精度等级 | 显存占用（7B 模型） | 质量保持 | 速度 | 适用场景 |
|----------|---------------------|----------|------|----------|
| BF16 | 14 GB | 100% | 基准 | 训练、全精度验证 |
| FP8 | 7 GB | ~99.8% | 1.5x | H100+ 推理首选 |
| INT8 (Q8_0) | 8.5 GB | ~99.5% | 1.5x | 最大质量保持 |
| 6-bit (Q6_K) | 6.7 GB | ~98% | 2x | **非英文最佳平衡** |
| 4-bit (Q4_K_M) | 4.7 GB | ~95% | 2.5x | VRAM 受限首选 |
| 2-bit (IQ2_M) | 2.5 GB | ~85% | 3x | 极端压缩 |

**关键决策规则：**

1. **FP8 是 2026 年的实用甜点**：质量和 BF16 几乎无差别，显存减半。H100/RTX 5090 原生支持
2. **Q6_K 是非英文语言的安全选择**：4-bit 量化非英文质量掉到 90-95%，Q6_K 保持 98-99%。多花 2GB VRAM 换全语言质量
3. **GPTQ-Int4 是 multi-LoRA 唯一选择**：唯一支持 LoRA adapter 的 4-bit 格式，vLLM 原生兼容
4. **AWQ vs GPTQ**：AWQ 在多数基准上质量略高，GPTQ 工具链更成熟、预量化模型更多
5. **GGUF 优势**：CPU + GPU 混合推理、Apple M 系列原生支持、llama.cpp 生态

**70B 模型量化后显存需求对照：**

| 格式 | 显存 | 可运行硬件 |
|------|------|-----------|
| BF16 | 140 GB | 2x H100 80GB |
| FP8 | 70 GB | 1x H100 80GB |
| INT4 AWQ/GPTQ | 35-40 GB | 1x RTX PRO 6000 96GB / 2x A6000 |
| INT4 GGUF (Q4_K_M) | ~40 GB | 同上 + CPU offload |

### 发现 3：SGLang RadixAttention 深度机制分析

RadixAttention 是 SGLang 相对 vLLM 的核心差异化优势：

#### 机制：Token-Level Radix Tree vs Block-Level Hashing

| 维度 | SGLang RadixAttention | vLLM Automatic Prefix Caching |
|------|----------------------|-------------------------------|
| 数据结构 | **Radix Tree**（前缀树） | **Block-level Hash Table** |
| 匹配粒度 | Token 级别精确匹配 | Block 级别（默认 16 token 块） |
| 缓存复用 | 共享前缀自动复用（含生成结果） | 仅共享前缀复用 |
| 树操作 | 动态插入/删除/合并 | Hash 查找 + LRU 淘汰 |
| 内存效率 | 前缀重叠零额外开销 | Block 对齐可能有 padding 浪费 |

#### 实测收益

- **多轮对话场景**：系统 prompt + 工具定义固定时，cache hit rate 达 **75-95%**
- **Agent swarm**：多 Agent 共享相同 prompt 模板时效果最显著
- **TTFT 降低**：prefix 重叠 60%+ 时 TTFT 显著下降
- **整体吞吐**：相比 vLLM 在多轮场景约 **10% boost**

#### 何时选 SGLang（基于 RadixAttention）

```
if (multi_turn_conversation || agent_swarm) && shared_prefix_ratio > 0.5:
    choose SGLang  # RadixAttention 收益最大化
elif single_turn_batch_inference:
    choose vLLM or TensorRT-LLM  # 批处理吞吐更优
elif nvidia_hardware && max_throughput_critical:
    choose TensorRT-LLM  # Kernel fusion 最深
```

---

## 技术细节与代码示例

### 知识蒸馏实践模板（HuggingFace TRL）

```python
from transformers import AutoModelForCausalLM, AutoTokenizer
from trl import SFTTrainer, SFTConfig

# 教师模型生成蒸馏数据
teacher = AutoModelForCausalLM.from_pretrained("meta-llama/Llama-3.1-70B")
tokenizer = AutoTokenizer.from_pretrained("meta-llama/Llama-3.1-70B")

# 用教师模型批量生成高质量训练数据
def generate_distill_data(prompts, teacher, tokenizer, temperature=0.7):
    """用教师模型为每个 prompt 生成高质量回答"""
    results = []
    for prompt in prompts:
        inputs = tokenizer(prompt, return_tensors="pt").to(teacher.device)
        outputs = teacher.generate(**inputs, max_new_tokens=512, temperature=temperature)
        response = tokenizer.decode(outputs[0][inputs.input_ids.shape[1]:], skip_special_tokens=True)
        results.append({"prompt": prompt, "response": response})
    return results

# 学生模型训练（在教师生成的数据上 SFT）
student = AutoModelForCausalLM.from_pretrained("meta-llama/Llama-3.1-8B")

trainer = SFTTrainer(
    model=student,
    train_dataset=distill_dataset,  # 教师生成的数据
    args=SFTConfig(
        max_seq_length=2048,
        per_device_train_batch_size=4,
        gradient_accumulation_steps=8,
        learning_rate=2e-5,
        num_train_epochs=3,
    ),
)
trainer.train()
```

### vLLM 量化 + 推测解码完整配置

```python
from vllm import LLM, SamplingParams

# 量化 + EAGLE-3 推测解码
llm = LLM(
    model="meta-llama/Meta-Llama-3.1-8B-Instruct-AWQ",
    quantization="awq",
    gpu_memory_utilization=0.9,
    max_model_len=8192,
    speculative_config={
        "method": "eagle3",
        "model": "yuhuili/EAGLE3-LLaMA3.1-Instruct-8B",
        "num_speculative_tokens": 3,
    },
)

# 基准测试
sampling_params = SamplingParams(temperature=0, max_tokens=256)
outputs = llm.generate(["Explain KV caching in one paragraph."], sampling_params)
```

### SGLang 多轮对话 RadixAttention 配置

```python
import sglang as sgl

# SGLang server 启动（自动启用 RadixAttention）
# python -m sglang.launch_server \
#   --model-path meta-llama/Meta-Llama-3.1-8B-Instruct \
#   --mem-fraction-static 0.85 \
#   --enable-prefix-caching  # RadixAttention 默认开启

# 多轮对话自动复用 KV Cache
@sgl.function
def multi_turn_chat(s, system_prompt, user_messages):
    s += sgl.system(system_prompt)  # 第一轮后缓存
    for msg in user_messages:
        s += sgl.user(msg)
        s += sgl.assistant(sgl.gen("response", max_tokens=256))
```

---

## 实践启发

1. **蒸馏 ROI 分析**：如果需要部署 10+ 个领域专用模型，蒸馏 ROI 极高（一次蒸馏永久收益）。如果只有 1-2 个模型，直接量化更划算
2. **量化选型的"非英文陷阱"**：很多基准测试只报告英文质量保持率，非英文在 4-bit 下质量掉 5-10%。面向中文用户必须考虑 Q6_K 或 FP8
3. **RadixAttention 是 Agent 架构的关键基础设施**：Agent 系统通常有固定 system prompt + 工具定义（占 60-80% token），RadixAttention 使多 Agent 共享推理成为可能
4. **三层优化叠加效果**：量化(2x 内存) + PagedAttention(3x 吞吐) + 投机解码(2x 延迟) = 不是 12x 而是 ~5-6x（存在效率天花板），但已足够将推理成本降低一个数量级

---

## 知识缺口

1. **蒸馏 + 量化叠加效应**：先蒸馏到小模型再量化，精度损失的累积规律
2. **RadixAttention 在 RAG 长文档场景的表现**：当 prefix 不是固定系统 prompt 而是检索到的长文档时
3. **GGUF 在 Jetson Orin 上的最优量化配置**：ARM Cortex + CUDA 的混合推理性能
4. **DA-KD 的开源实现**：目前只有论文，是否有 TRL/DeepSpeed 集成
5. **SGLang 与 vLLM 在投机解码场景的直接对比**：两者都支持 EAGLE-3，性能差异几何

---

## 参考

- DA-KD (ICML 2025): Difficulty-Aware Knowledge Distillation for Efficient LLMs
- NeurIPS 2024: Compact Language Models via Pruning and Knowledge Distillation
- Springer Survey 2025: Knowledge distillation and dataset distillation of LLMs
- vrlatech.com: LLM Quantization Explained — INT4/INT8/FP8/AWQ/GPTQ (2026)
- Spheron Network: SGLang RadixAttention Production Guide (2026)
- RunPod: SGLang vs vLLM KV Cache Reuse Benchmark
- LMSYS: RadixAttention and SGLang (原始论文)
- EAGLE-3 arXiv:2503.01840 — 6.5x Speedup via Training-Time Test

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
- [MLA多头潜在注意力-DeepSeek-KV缓存压缩与推理优化](../2026-05-21-MLA多头潜在注意力-DeepSeek-KV缓存压缩与推理优化.md)
- [llm-finetune-dataflow-dataflex-pipeline](../2026-05-21-llm-finetune-dataflow-dataflex-pipeline.md)
- [react-agent-llm-agentic-training-research](../2026-05-21-react-agent-llm-agentic-training-research.md)
- [If-youre-an-LLM-please-read-this-Anna-Archive-LLM伦理契约](../2026-05-22-If-youre-an-LLM-please-read-this-Anna-Archive-LLM伦理契约.md)
- [LoRA-GRPO最优配置实证-RL场景的Rank选择与超参数](../2026-05-22-LoRA-GRPO最优配置实证-RL场景的Rank选择与超参数.md)
- [Multi-Stream-LLMs-并行流解锁语言模型](../2026-05-22-Multi-Stream-LLMs-并行流解锁语言模型.md)
- [Antigravity2.0-OpenSCAD-LLM-Benchmark-AI编程3D建模能力](../2026-05-23-Antigravity2.0-OpenSCAD-LLM-Benchmark-AI编程3D建模能力.md)
- [OpenAI后训练团队Yann-Dubois深度访谈](../2026-05-23-OpenAI后训练团队Yann-Dubois深度访谈.md)
- [QLoRA在RL训练中的精度影响-量化与强化学习深度解析](../2026-05-23-QLoRA在RL训练中的精度影响-量化与强化学习深度解析.md)
- [AutoSearch 自主训练任务](../AutoSearch 自主训练任务.md)
- [表达清晰的5个训练](../ai-agent/2026-05-16-表达清晰的5个训练.md)
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
- [边缘AI推理优化-Jetson平台深度研究](2026-05-21-边缘AI推理优化-Jetson平台深度研究.md)
- [llama-cpp预编译二进制与本地LLM推理](2026-05-22-llama-cpp预编译二进制与本地LLM推理.md)
- [VPO向量策略优化多样性训练提升推理搜索](2026-05-23-VPO向量策略优化多样性训练提升推理搜索.md)
- [llm-inference-opt-2026-05-17](llm-inference-opt-2026-05-17.md)
- [llm-inference-opt-deep-dive](llm-inference-opt-deep-dive.md)
- [llm-inference-opt-incremental-20260517](llm-inference-opt-incremental-20260517.md)
- [llm-inference-optimization-2026](llm-inference-optimization-2026.md)
- [llm-pid-tuner](../llm-pid-tuner.md)
- [分布式训练技术全景-FSDP-DeepSpeed-Megatron](../orphan/2026-05-05-分布式训练技术全景-FSDP-DeepSpeed-Megatron.md)
- [tinyedge-lora](../tinyedge-lora.md)
- [前瞻性问题-AI垂域LLM载具设计](../前瞻性问题-AI垂域LLM载具设计.md)
