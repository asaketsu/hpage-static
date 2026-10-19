# LLM 推理优化技术深度笔记（2026 最新）

> 探索日期：2026-05-19
> 主题：LLM Inference Optimization — 量化/推理引擎/蒸馏/投机解码
> 来源：MorphLLM, Google Research TurboQuant (ICLR 2026), vLLM/SGLang/TRT-LLM 基准测试, AWS P-EAGLE, HuggingFace EAGLE-3 实战

---

## 核心发现

### 发现 1：三层优化栈（Model → System → Application）

LLM 推理优化已形成清晰的三层架构，各层互补叠加可实现 **80%+ 成本削减**：

| 层级 | 核心技术 | 典型收益 | 实施难度 |
|------|----------|----------|----------|
| **Model 层** | 量化/剪枝/蒸馏 | 2-4x 内存，~50% 成本 | 低（量化）/ 高（蒸馏） |
| **System 层** | 连续批处理/PagedAttention/投机解码 | 3-10x 吞吐，2-5x 延迟 | 低（引擎配置） |
| **Application 层** | 上下文压缩/提示缓存/模型路由 | 50-70% token 减少，80-90% 延迟 | 低（API 调用） |

**关键洞察**：大多数团队只关注 System 层（换引擎），但 Application 层（压缩上下文、缓存提示）才是 ROI 最高的优化点，因为它们直接减少了进入推理管线的 token 数量。

### 发现 2：TurboQuant — KV Cache 3-bit 量化零精度损失（Google ICLR 2026）

这是 2026 年最重大的推理优化突破之一：

- **核心算法**：PolarQuant（基于旋转变换的坐标变换）+ 1-bit QJL 残差校正
- **压缩效果**：KV Cache 压缩到 **3 bit/坐标**，实现 **6x 内存缩减**
- **精度**：在 LongBench 基准上 **零精度损失**
- **理论保证**：失真不超过 4^(-b) 缩放因子的约 2.7 倍信息论极限
- **实用性**：数据无关（data-oblivious），无需训练，无需校准数据，开箱即用
- **集成**：已有 vLLM 集成 + Triton kernel 实现

**实际影响**：
- Llama-3.1-8B 在 128K 上下文下，KV Cache 单独就可能超过模型权重本身
- TurboQuant 让 128K 长上下文推理在消费级 GPU 上成为可能
- 在 RTX 5090 (32GB) 上跑 Qwen3.5-27B-AWQ，TurboQuant 释放了 **30GB KV Cache**

### 发现 3：推理引擎 2026 格局 — 四强争霸

在 H100 上跑 Llama 3.3 70B Instruct FP8 的基准：

| 引擎 | 吞吐量 | TTFT | 编译时间 | 最佳场景 |
|------|--------|------|----------|----------|
| **SGLang v0.4.3** | 16,200 tok/s | ~115ms | ~8 min | 前缀密集型（RAG、多轮对话） |
| **LMDeploy** | 16,200 tok/s | ~110ms | ~8 min | 高吞吐通用服务 |
| **vLLM v0.7.3** | 12,500 tok/s | ~120ms | ~5 min | 灵活性优先，频繁换模型 |
| **TensorRT-LLM** | 最高（高并发） | 105ms | ~28 min | 单模型长期生产部署 |

**选型建议**：
- **vLLM**：最灵活，社区最大，适合频繁换模型
- **SGLang**：RadixAttention 前缀缓存对 RAG/多轮对话场景极强
- **TensorRT-LLM**：需编译但编译后吞吐最高，适合固定模型大规模部署
- **Modular MAX**：新兴第五选项，Mojo 编译 kernel 在高并发下超越 vLLM

### 发现 4：投机解码最新进展 — EAGLE-3 → P-EAGLE

投机解码技术迭代飞快：

| 方法 | 年份 | 核心创新 | 加速比 |
|------|------|----------|--------|
| **EAGLE-2** | 2024 | 基于特征层面的草稿生成 | 2-3x |
| **EAGLE-3** | 2025 | 更强的草稿模型，off-the-shelf 可用 | 2-3x (通用), 5x (优化) |
| **P-EAGLE** | 2026 | **并行草稿生成**，一次前向生成 K 个 token | EAGLE-3 基础上再 1.05-1.69x |

**P-EAGLE 突破**：
- 传统 EAGLE 的隐藏瓶颈：自回归草稿生成本身也是序列化的
- P-EAGLE 在**单次前向传播**中生成所有 K 个草稿 token，消除了序列化瓶颈
- 在 NVIDIA B200 上验证，已支持 GPT-OSS 120B/20B、Qwen3-Coder 30B
- vLLM 已原生支持

**核心发现**：草稿模型的延迟比准确率更重要！基准测试显示草稿模型准确率与最终吞吐量相关性很弱，草稿生成速度才是真正的瓶颈。

---

## 技术细节

### 1. 量化技术对比

| 方法 | 类型 | 精度损失 | 内存缩减 | 适用场景 |
|------|------|----------|----------|----------|
| **SmoothQuant** | 权重+激活量化 | <1% | 2x | 通用推理 |
| **GPTQ** | 权重量化（校准） | 1-3% | 2-4x | 离线量化 |
| **AWQ** | 权重量化（感知） | 1-2% | 2-4x | 保护关键通道 |
| **TurboQuant** | KV Cache 量化 | ~0% | 6x | 长上下文推理 |
| **FP8** | 全模型 | <1% | 2x | H100/B200 原生 |

**最优压缩管线**：P-KD-Q — 先剪枝(Prune)，再蒸馏(Distill)，最后量化(Quantize)。每步效果叠加。

### 2. 连续批处理 vs 静态批处理

```
静态批处理：等一个 batch 全部完成才接受新请求
→ 短请求等长请求，GPU 大量空闲

连续批处理：旧请求完成立即插入新请求
→ 3-10x 吞吐提升
→ Anyscale 实测：生产负载 23x 聚合吞吐提升
```

### 3. PagedAttention 内存管理

传统方式：为最大序列长度预分配 KV Cache → **浪费 90% GPU 显存**

PagedAttention（vLLM 首创）：
- 将 KV Cache 分割为小的可复用页
- 按需分配，减少 90% 内存浪费
- 支持最多 24x 更高的服务吞吐

### 4. 上下文压缩 — Agent 场景的关键优化

Agent 工作流的核心问题：上下文膨胀
- 第 30 轮对话时，input token 可能是第 1 轮的 **5-10 倍**
- 大部分 token 是过时信息（旧对话轮、样板文件头、已处理的文件内容）

**两种压缩策略对比**：

| 策略 | 方法 | 准确性评分 | Agent 轨迹影响 |
|------|------|-----------|---------------|
| **摘要式** | LLM 重写内容 | 3.4-3.7/5 | 轨迹长 13-15%（信息被改写后 agent 需重新推导） |
| **逐字式** | 删除低信息 token，保留原文 | 5/5 | 无影响 |

JetBrains 研究发现：摘要导致 agent 轨迹变长 13-15%，因为文件路径、错误码等关键信息被改写后丢失。

逐字式压缩（Morph Compact）：33,000 tok/s，50-70% 压缩率，可在每次 LLM 调用前执行。

### 5. 提示缓存的经济效益

- Anthropic/OpenAI/Google 都已支持
- 10K+ token 共享前缀 → 80-90% 延迟减少
- Anthropic 实现：缓存 token 不计入 rate limit → 80% 命中率下 **5x 吞吐提升**

---

## 实践启发

### 对 Jetson Orin Nano 部署的启示

1. **量化是必须的**：67 TOPS 算力下，INT4 量化是唯一可行的方案
2. **TurboQuant 可能不适用**：Jetson 显存有限（8GB），但 KV Cache 压缩对短上下文意义不大
3. **TensorRT-LLM 是最佳选择**：编译优化 + CUDA kernel 优化对 Jetson 的 Orin GPU 架构最优
4. **投机解码有限**：小模型上草稿模型选择范围窄，加速效果不如云端显著

### 对 Agent 系统的启示

1. **上下文管理是第一优先级**：不是换引擎，而是减少输入 token
2. **逐字压缩 > 摘要压缩**：对 coding agent 尤其关键
3. **提示缓存是免费午餐**：多轮对话天然有共享前缀
4. **模型路由可省 12x**：简单任务用小模型

### 实际优化栈推荐

```
自部署场景：
  量化(INT4/AWQ) → vLLM/SGLang(PagedAttention+连续批处理) → TurboQuant(KV Cache) → 投机解码(EAGLE-3)
  预期：80%+ 成本削减

API 调用场景：
  逐字上下文压缩 → 提示缓存 → 模型路由（简单任务→小模型）
  预期：60-80% token 削减
```

---

## 知识缺口

1. **TurboQuant 在 Jetson Orin 上的适配性**：Triton kernel 需要 CUDA compute capability 7.0+，Orin 是 8.7，理论上支持但未验证
2. **P-EAGLE 的边缘部署可行性**：目前仅在 B200 上验证，消费级 GPU 表现未知
3. **Modular MAX 的成熟度**：Mojo 编译内核很诱人但生产案例尚少
4. **KV Cache 量化与投机解码的交互效应**：两者叠加是否有负面的精度累积影响
5. **SGLang RadixAttention 在非 RAG 场景的收益量化**
6. **逐字压缩的算法细节**：Morph Compact 是商业产品，开源替代方案（如 LLMLingua）的效果对比

---

## 参考

- MorphLLM: LLM Inference Optimization Guide (2026) — 三层优化栈 + 引擎对比
- Google TurboQuant (ICLR 2026, arXiv:2504.19874) — 3-bit KV Cache 零损失量化
- AWS P-EAGLE — 并行投机解码，vLLM 原生支持
- Spheron: vLLM vs TRT-LLM vs SGLang H100 Benchmarks (2026)
- Thoughtworks: EAGLE-3 实战验证（GLM-4.7-Flash）
- JetBrains: Agent 轨迹对比（摘要 vs 逐字压缩）

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
- [llm-inference-opt-2026-05-20-supplement](llm-inference-opt-2026-05-20-supplement.md)
- [llm-inference-opt-deep-dive](llm-inference-opt-deep-dive.md)
- [llm-inference-opt-incremental-20260517](llm-inference-opt-incremental-20260517.md)
- [llm-pid-tuner](../llm-pid-tuner.md)
- [分布式训练技术全景-FSDP-DeepSpeed-Megatron](../orphan/2026-05-05-分布式训练技术全景-FSDP-DeepSpeed-Megatron.md)
- [tinyedge-lora](../tinyedge-lora.md)
- [前瞻性问题-AI垂域LLM载具设计](../前瞻性问题-AI垂域LLM载具设计.md)
