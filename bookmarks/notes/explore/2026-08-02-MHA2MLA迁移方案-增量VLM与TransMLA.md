# MHA2MLA 迁移方案 — 增量更新（VLM 扩展 + TransMLA 平行方案）

> 日期: 2026-08-02 | 类型: 增量研究（auto-explore）
> 基础笔记: [[2026-07-22-DeepSeek-MLA多头潜注意力KV缓存压缩深度解析]]
> 本文聚焦 2025下半年-2026 的两条新进展，不重复 MLA 基础原理。

## 摘要

自 2025-02 原 MHA2MLA 论文（arXiv:2502.14837，复旦+海康+上海AI Lab）以来，该方向出现两条重要增量：
1. **MHA2MLA-VLM**（arXiv:2601.11464，AAAI 2026）— 把迁移扩展到视觉语言模型，首次解决多模态 KV 缓存瓶颈。
2. **TransMLA**（arXiv:2502.07864，NeurIPS 2025 Spotlight）— 平行方案，专攻 GQA→MLA，强调与 DeepSeek 推理生态（vLLM/SGlang）全兼容，8K context 10x 加速。

## 关键发现

### 发现一：MHA2MLA-VLM — 迁移到视觉语言模型

- **来源**：arXiv:2601.11464 | 复旦大学（同原 MHA2MLA 团队）| AAAI 2026
- **核心创新**：
  - **Modality-Adaptive Partial-RoPE** — 原版 partial-RoPE 只针对纯文本；VLM 版本区分视觉 token 和文本 token 的 RoPE 处理策略
  - 针对多模态场景的 KV cache 压缩，VLM 的长上下文（图像 token 数量大）使 KV 缓存瓶颈比纯文本 LLM 更严重
- **意义**：现有 VLM（LLaVA、Qwen-VL 等）无需重新预训练即可获得 MLA 的推理成本优势

### 发现二：TransMLA — GQA→MLA 的 DeepSeek 兼容路径

- **来源**：arXiv:2502.07864 | NeurIPS 2025 Spotlight | 孟繁旭、唐平治等
- **定位差异**（vs MHA2MLA）：
  - MHA2MLA 专注 MHA→MLA，从注意力机制层做 partial-RoPE + 联合 SVD
  - TransMLA 专注 **GQA→MLA**，且核心卖点是**转换后直接兼容 DeepSeek 推理代码库**（vLLM、SGlang 原生支持）
- **关键数据**：
  - LLaMA-2-7B 压缩 93% KV cache
  - 8K context 下 10x 推理加速
  - 仅需 6B tokens 微调即可恢复性能（跨多 benchmark）
- **理论洞察**：GQA 恒可被 MLA 等价表示（相同 KV cache 开销），反之不成立 → MLA 严格强于 GQA
- **兼容性**：支持 RoPE；absorb operation 版本开发中
- **社区落地**：已有转换模型 BarraHome/llama3.2-1b-mla、BarraHome/llama3_2-1B-deepseek

### 发现三：原 MHA2MLA 的工程进展（2025下半年）

- **2025-06**：重构代码，新增 Qwen 模型支持
- **2025-03**：发布 PyTorch 推理代码；发布 4 组 MLA checkpoints
  - SmolLM-135M/360M/1.7B 衍生（d_kv=8/16/32/128）
  - Llama-2-7B 衍生（d_kv=16/32/64/256）
- **GitHub**：JT-Ushio/MHA2MLA（211 stars，Apache-2.0）
- **待办**：MHA2MLA + FlashMLA + KV quanto 联合优化（进一步省显存）

## 迁移方案对比（纯文本）

- MHA2MLA（原版）：MHA→MLA | partial-RoPE + 联合SVD | 135M~1.7B 验证 | ACL 2025
- MHA2MLA-VLM：MHA/GQA→MLA | 多模态自适应 partial-RoPE | VLM 适用 | AAAI 2026
- TransMLA：GQA→MLA | DeepSeek生态原生兼容 | 7B验证93%压缩 | NeurIPS 2025 Spotlight

## 对工作的价值

1. **Jetson 边缘部署**：边缘设备 KV 缓存是最大瓶颈，MLA 迁移可让现有开源模型在同等显存下支持更长 context
2. **多模态 Agent**：如果要做 VLM 类应用（图像理解+对话），MHA2MLA-VLM 提供了降本路径
3. **DeepSeek 生态对接**：TransMLA 的 vLLM/SGlang 兼容性意味着迁移后可直接用现有高性能推理引擎

## 行动建议

- 短期：保持关注，无需立即迁移现有项目（这些方法还在学术验证阶段，7B+ 大模型迁移效果待更多实证）
- 中期：关注 TransMLA 的 absorb operation 支持（开发中），完成后推理加速会进一步提升
- 若启动新 VLM 项目：优先考虑已原生 MLA 的模型（DeepSeek-VL2 等），而非事后迁移


## 相关笔记

- [MLA多头潜在注意力](./2026-08-02-本地模型部署-MLA多头潜在注意力.md) — MLA核心原理，KV Cache低秩压缩
- [MHA2MLA迁移方案](./2026-08-02-本地模型部署-MHA2MLA迁移方案.md) — 基础迁移框架，Partial-RoPE+GQA
- MHA→MLA迁移深度分析（~/explore/2026-07-27） — 早期迁移方案系统性分析
