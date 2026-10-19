# 开源 AI 模型 2025：DeepSeek、Qwen 引领新格局

> 📅 2026-05-05 | 🏷️ 开源AI, DeepSeek, Qwen, Open Weight, 模型生态
> 来源：SoftwareSeni / Red Line / Red Hat Developer

## 摘要

2025 年是开源 AI 模型的分水岭。DeepSeek-R1 以纯强化学习训练突破推理能力天花板，Qwen 系列超越 Llama 成为 HuggingFace 下载量最高的 LLM 家族。同时，"open weight" 与 "open source" 的区分变得关键——大多数"开源"模型实际上只是开放权重。

## 关键要点

### 1. 三大里程碑模型

| 模型 | 发布方 | 核心突破 | 影响 |
|------|--------|----------|------|
| **DeepSeek-R1** | 深度求索 | 纯 RL 训练，无需标注数据 | 登上 Nature 封面，全球首个经同行评议的主流 LLM |
| **Qwen 3** | 阿里云 | 多模态 + 推理能力逼近 GPT-4 | HF 下载量超越 Llama，Airbnb 生产环境使用 |
| **gpt-oss** | OpenAI | 开放权重推理模型，性能≈o4-mini | 8 月发布，本地 PC/手机可运行 |

### 2. Open Weight ≠ Open Source

- **Open Source**：公开训练代码、数据集、全流程（极少模型做到）
- **Open Weight**：公开模型参数，可自由部署和微调（当前主流）
- **关键风险**：中国实验室模型（Qwen/DeepSeek/Kimi K2）占 open weight 主导地位，带来供应链安全考量

### 3. 小模型革命

- Mistral Small 3、Llama 4 等小模型在特定任务上媲美大模型
- 微软 Phi 系列持续领跑小模型赛道
- Writer 声称其模型参数仅需大模型的 1/20 即可达到相近性能
- 端侧部署成为可能：手机、PC 本地运行

### 4. 推理效率突破

- **llm-d**：新型推理框架
- **vLLM**：持续迭代，吞吐量大幅提升
- **LMCache**：KV Cache 优化，减少重复计算

## 生态格局

```
2025 Open AI Model Ecosystem:
├── 中国势力（主导 open weight）
│   ├── DeepSeek（RL 路线领导者）
│   ├── Qwen（下载量第一）
│   └── Kimi K2（新秀）
├── 美国势力
│   ├── Meta Llama（被 Qwen 超越）
│   ├── Mistral（欧洲，小模型专家）
│   └── Google Gemma
└── 新玩家
    └── OpenAI gpt-oss（战略转型）
```

## 个人分析

2025 年开源 AI 格局最深刻的变化是 **"中国主导 open weight"**。这不只是技术竞赛，更是一场治理权的博弈：

1. **Airbnb CEO 公开表示使用 Qwen 而非 OpenAI**，因为"更快更便宜"
2. **DeepSeek 的 Nature 封面论文** 标志着中国 AI 研究获得西方学术界认可
3. **open weight ≠ open governance** — 用户可以自由部署，但无法审计训练决策

对开发者的建议：
- 通用场景优先考虑 Qwen/DeepSeek（性价比最高）
- 需要可审计性时选择真正 open source 的模型
- 关注 gpt-oss 的实际表现，可能改变部署策略

---
*本文由嗅探队列自动生成 | 主动搜集*

## 相关笔记
- [Hermes-LLM-Wiki-学习笔记](2026-04-18-Hermes-LLM-Wiki-学习笔记.md)
- [MCP协议与Agentic-LLM-2025趋势](2026-04-23-MCP协议与Agentic-LLM-2025趋势.md)
- [垂域LLM指导航空结构设计](2026-04-27-垂域LLM指导航空结构设计.md)
- [LLM推理优化前沿技术2026](2026-04-28-LLM推理优化前沿技术2026.md)
- [LLM-Agent驱动量化交易系统前沿学习](2026-04-29-LLM-Agent驱动量化交易系统前沿学习.md)
- [边缘AI与On-Device-LLM前沿学习](2026-04-30-边缘AI与On-Device-LLM前沿学习.md)
- [deepseek-agent-ecosystem](2026-05-01-deepseek-agent-ecosystem.md)
- [LLM对齐训练范式RLHF-DPO-GRPO-DAPO](2026-05-04-LLM对齐训练范式RLHF-DPO-GRPO-DAPO.md)
- [Awesome-LLM-Apps-109K星应用模板库](2026-05-05-Awesome-LLM-Apps-109K星应用模板库.md)
- [PageIndex-无向量推理式RAG](2026-05-07-PageIndex-无向量推理式RAG.md)
- [大模型量化技术全景-GGUF-GPTQ-AWQ-FP8-BitNet](2026-05-07-大模型量化技术全景-GGUF-GPTQ-AWQ-FP8-BitNet.md)
- [ollama-vllm-llamacpp-deploy-comparison](2026-05-08-ollama-vllm-llamacpp-deploy-comparison.md)
- [推理加速深度解析-投机解码-KVCache-连续批处理](2026-05-08-推理加速深度解析-投机解码-KVCache-连续批处理.md)
- [LLM知识蒸馏技术全景](2026-05-09-LLM知识蒸馏技术全景.md)
- [DeepSeek-V4-开源模型新格局](2026-05-10-DeepSeek-V4-开源模型新格局.md)
- [蒸馏量化联合策略-QAD-LBLLM-CapacityGap](2026-05-10-蒸馏量化联合策略-QAD-LBLLM-CapacityGap.md)
- [5月AI模型大战-GPT55-DeepSeekV4](2026-05-11-5月AI模型大战-GPT55-DeepSeekV4.md)
- [AI趋势2026-推理时计算与反思Agent](2026-05-11-AI趋势2026-推理时计算与反思Agent.md)
- [LLM冲击下PINN应用变化与发展](2026-05-11-LLM冲击下PINN应用变化与发展.md)
- [MoE蒸馏与压缩-专家路由迁移-稀疏结构处理](2026-05-11-MoE蒸馏与压缩-专家路由迁移-稀疏结构处理.md)
- [MoE投机解码-稀疏激活与推理加速深度解析](2026-05-13-MoE投机解码-稀疏激活与推理加速深度解析.md)
- [从零训练GPT完整指南](2026-05-13-从零训练GPT完整指南.md)
- [JAX-NVIDIA-GPU-微调Llama3.1实战方案](2026-05-15-JAX-NVIDIA-GPU-微调Llama3.1实战方案.md)
- [序列并行与上下文并行-长上下文训练的第四维并行](2026-05-15-序列并行与上下文并行-长上下文训练的第四维并行.md)
- [LoRA高效微调前沿技术全景](2026-05-17-LoRA高效微调前沿技术全景.md)
- [20260513-llm-wiki-obsidian-gbrain-知识自组织与自进化](20260513-llm-wiki-obsidian-gbrain-知识自组织与自进化.md)
- [AutoSearch 自主训练任务](AutoSearch 自主训练任务.md)
- [2025年5月AI大爆发-Claude4-Qwen3-DeepSeek-R1](explore/2026-05-09-2025年5月AI大爆发-Claude4-Qwen3-DeepSeek-R1.md)
- [开源AI春季爆发-模型推理Agent](explore/2026-05-09-开源AI春季爆发-模型推理Agent.md)
- [2026年5月AI模型大战-GPT5.5-Grok4.3-DeepSeekV4](explore/2026-05-13-2026年5月AI模型大战-GPT5.5-Grok4.3-DeepSeekV4.md)
- [开源AI模型新格局-DeepSeek冲击波](explore/2026-05-13-开源AI模型新格局-DeepSeek冲击波.md)
- [LLM推理优化-MoE量化加速全景](explore/2026-05-16-LLM推理优化-MoE量化加速全景.md)
- [LLM推理优化技术](explore/2026-05-16-LLM推理优化技术.md)
- [llm-pid-tuner](llm-pid-tuner.md)
- [llm-wiki-gbrain-agent-evolution_33aa818c](llm-wiki-gbrain-agent-evolution_33aa818c.md)
- [分布式训练技术全景-FSDP-DeepSpeed-Megatron](orphan/2026-05-05-分布式训练技术全景-FSDP-DeepSpeed-Megatron.md)
- [MoE混合专家模型-路由策略-负载均衡-训练稳定性](orphan/2026-05-06-MoE混合专家模型-路由策略-负载均衡-训练稳定性.md)
- [多目标GRPO-GDPO-AW-GRPO-Reward融合与冲突消解](orphan/2026-05-14-多目标GRPO-GDPO-AW-GRPO-Reward融合与冲突消解.md)
- [MegatronCore模块化重构与MoE训练前沿](orphan/2026-05-16-MegatronCore模块化重构与MoE训练前沿.md)
- [表达清晰的5个训练](orphan/2026-05-16-表达清晰的5个训练.md)
- [tinyedge-lora](tinyedge-lora.md)
- [前瞻性问题-AI垂域LLM载具设计](前瞻性问题-AI垂域LLM载具设计.md)
