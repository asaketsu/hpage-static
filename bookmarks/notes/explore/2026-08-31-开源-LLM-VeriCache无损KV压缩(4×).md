# VeriCache: 将有损 KV Cache 变为无损 LLM 推理

> 探索日期: 2026-08-31 | 来源: arXiv 2605.17613

## 要旨

VeriCache 是首个能将任意有损 KV Cache 压缩方法（token dropping / 量化）无损化的推理框架，核心思路借鉴 speculative decoding：用压缩 KV 做 draft，用完整 KV 做 verify，输出与 full-KV 完全一致。

## 核心设计

- **Cross-resource staggering**: Draft 是 HBM 带宽瓶颈（读压缩 KV + weights），verify 是 PCIe/互联带宽瓶颈（加载完整 KV）。把两者错峰调度，互补资源瓶颈，避免排队等待
- **高接受率**: 压缩 KV 保留了相同的模型权重和注意力模式，每轮 verify 可接受 25-40 个 token（传统小模型 drafter 仅 2-3 个），大幅摊薄每次 verify 的开销
- **统一 Compressor 接口**: 支持 7 种压缩方法（KVzip/KIVI/KVQuant/RotateKV 等），即插即用
- 构建于 vLLM + LMCache 之上

## 关键结果

- **长上下文解码**: 1.92×–2.73× full-KV 吞吐（Llama-70B 从 102→256 tok/s）
- **远程前缀缓存**: 1.33×–2.11× full-KV 吞吐
- **+EAGLE 组合**: 4.26×–4.35×（Qwen-32B）
- **KL 散度 < 0.01 nats**（仅来自硬件非确定性，验证输出与 full-KV 完全一致）
- 内存越紧张（大模型/小 HBM），VeriCache 的加速比越大（1.61×→2.71×）

## 对工作的价值

- 解决了我系统中有损 KV 压缩（量化和 token dropping）在代码生成和 tool calling 场景下精度崩塌的痛点
- 尤其适合 Llama-70B 等大模型的长上下文服务场景
- 7 种压缩方法可互相替代，适配不同硬件约束

## 行动建议

- 关注 VeriCache 开源情况（built on vLLM+LMCache，代码应较易整合）
- 在需要高精度输出（代码/结构化/工具调用）的 LLM 服务场景中替换纯有损压缩方案
- 关注组合方案 VeriCache+EAGLE，提速最显著

## 相关笔记

- [ReCache-Agent-KVCache复用与压缩](./2026-08-22-ReCache-Agent-KVCache复用与压缩.md) — Agent 场景 KV 复用，与无损压缩组合的近亲方案
- [KVarN-KV-Cache量化后端](./2026-08-01-KVarN-KV-Cache量化后端.md) — 有损量化路线代表，VeriCache 的对照面
- [Agent在线KV-Cache压缩-代理查询选型实证](./2026-08-04-Agent在线KV-Cache压缩-代理查询选型实证.md) — 在线压缩选型实证，损失率权衡依据
- [Nexus-MCP工具路由加速与KV拼接边界](./2026-08-25-Nexus-MCP工具路由加速与KV拼接边界.md) — 跨集群桥接：MCP 工具路由 × KV 拼接边界
- KVarN KV Cache 量化 vLLM 后端（~/explore/2026-08-24-kvarn-kv-cache-quantization-vllm-backend.md）— 跨目录：vLLM 后端量化部署细节
