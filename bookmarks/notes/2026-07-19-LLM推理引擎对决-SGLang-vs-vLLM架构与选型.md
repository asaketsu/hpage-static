# 2026 LLM 推理引擎对决：SGLang vs vLLM 架构与选型

> **学习日期**：2026-07-19
> **学习类型**：夜间自学习（静默 cron）
> **资料来源**：Particula、TECHSY、CallSphere、Modular 2026 年度对比
> **关联 Skill**：`llm-inference-optimization`、`serving-llms-vllm`

---

## 一、核心结论（先讲结果）

**2026 年 Hugging Face 已把 TGI 转入维护模式，新部署应选 vLLM 或 SGLang。**两者的根本差异在于 **KV Cache 管理策略**，这决定了你的工作负载在谁上面跑得更快：

| 选 SGLang | 选 vLLM |
|-----------|---------|
| 多轮对话 / Agent | 批处理 + 每条 prompt 独特 |
| RAG（共享文档前缀） | 多硬件环境（TPU/Trainium/Gaudi） |
| 结构化 JSON 输出 | encoder-decoder 模型（T5/BART） |
| **DeepSeek 系列模型** | 最大模型兼容性 + 最广社区 |

**一句话决策**：你的工作负载有没有"共享前缀"？有 → SGLang；没有 → vLLM。

---

## 二、架构对比：PagedAttention vs RadixAttention

### vLLM 的 PagedAttention（操作系统思路）
借鉴操作系统**虚拟内存分页**：
- 不再为每个请求分配一大块连续 GPU 内存（浪费 60-80%）
- KV Cache 拆成小块，存在 GPU 内存任意位置
- 每个序列按需逐块增长，请求结束立即释放
- **结果**：GPU 内存浪费从 60-80% 降到 <4%，配合 continuous batching，同硬件可服务更多并发

### SGLang 的 RadixAttention（缓存思路）
在分页管理基础上加一个关键洞察：**请求完成后别扔 KV Cache**。
- 维护一棵 **radix tree**（基数树）作为 KV 计算的 LRU 缓存
- 新请求到达时，对树做**前缀匹配**
- 若与历史请求共享前缀（多轮对话、RAG 共享文档、few-shot prompt 常见），**直接复用缓存计算**
- 配套 **cache-aware 调度器**：不按 FIFO，优先处理共享前缀长的请求（近似深度优先遍历 radix tree，最大化缓存命中）

**实际效果**：10 个用户查询同一篇 10000 字文档的 RAG 流水线，SGLang **处理一次**，vLLM **处理 10 次**。

### 架构对照表

| 特性 | vLLM（PagedAttention） | SGLang（RadixAttention） |
|------|----------------------|------------------------|
| 内存管理 | 分页块，<4% 浪费 | 分页块 + radix tree 缓存 |
| 缓存复用 | 仅请求内 | 跨请求，前缀匹配 |
| 调度 | 连续批处理（FIFO） | 缓存感知（前缀优先） |
| 内存基线开销 | 较低 | 较高（保留缓存树） |
| 最佳场景 | 独特 prompt，批作业 | 共享前缀，多轮 |

---

## 三、基准对比：数字会说话

### 标准 H100 吞吐（Llama 3.1 8B）

| 指标 | SGLang | vLLM | 差距 |
|------|--------|------|------|
| 总吞吐 | ~16,200 tok/s | ~12,500 tok/s | **SGLang +29%** |
| 输出 token 吞吐 | 894 tok/s | 413 tok/s | **SGLang +117%** |
| TTFT | 79 ms | 103 ms | SGLang 快 23% |
| Token 间延迟 ITL | 6.0 ms | 7.1 ms | SGLang 快 15% |

**关键**：输出 token 吞吐翻倍才是用户感知到的"速度"。

### DeepSeek V3/V4（SGLang 的杀手锏）
DeepSeek 官方背书 SGLang，性能差距悬殊：
- DeepSeek V3 上 **SGLang 比 vLLM 快 3.1 倍**
- 优化来源：MLA（Multi-head Latent Attention）后端 —— FlashAttention3 / FlashInfer / FlashMLA / CutlassMLA
- 支持 EAGLE 多 token 预测推测解码：H200 上 batch=1 加速 1.8×，batch=32 加速 1.5×

### 前缀密集负载（SGLang 主场）
RAG、few-shot 分类、多轮 Agent 场景下，RadixAttention 提供 **最高 6.4 倍吞吐提升** —— 这是 vLLM 架构层面无法竞争的场景。

### 独特 prompt 批处理（vLLM 反超点）
Spheron 测 Llama 3.3 70B FP8 on H100，prompts 全独特（无共享前缀）时：

| 并发 | vLLM (tok/s) | SGLang (tok/s) | 差距 |
|------|-------------|---------------|------|
| 1 | 120 | 125 | ~4% |
| 10 | 650 | 680 | ~5% |
| 50 | 1850 | 1920 | ~4% |
| 100 | 2400 | 2460 | ~2% |

**差距几乎抹平** —— 此时应选生态更广的 vLLM。

### 高并发稳定性
SGLang 在高并发下保持 30-31 tok/s/请求；vLLM 从 22 跌到 16 tok/s。SGLang 的缓存感知调度让单请求质量在总负载上升时保持稳定。

---

## 四、生态与生产就绪

### 社区与成熟度

| 指标 | SGLang | vLLM |
|------|--------|------|
| GitHub stars | ~25K | ~75K |
| Contributors | ~600 | ~2,400 |
| License | Apache 2.0 | Apache 2.0 |
| Issue 响应 | 3-5 天 | 12 小时 - 3 天 |

vLLM 社区基数 3 倍，凌晨 2 点踩坑更可能有现成解。

### 硬件支持（vLLM 完胜）
- **vLLM**：NVIDIA GPU、AMD CPU/GPU、Intel CPU/GPU、Google TPU（v4-v6e）、AWS Trainium/Inferentia、Intel Gaudi、Arm —— 还包括早期 Blackwell/GB200 优化（DeepSeek MoE 上 26,200 prefill tok/s）
- **SGLang**：主要 NVIDIA GPU，AMD GPU 支持通过 DeepSeek 合作在增长

**非 NVIDIA 加速器场景，vLLM 是当前唯一可行选项。**

### 模型兼容性
- **vLLM**：decoder-only、encoder-decoder（T5/BART）、MoE、embedding、多模态 —— 最广
- **SGLang**：decoder-only LLM、多模态、embedding、reward、diffusion —— **不支持 encoder-decoder**
- 多数 LLM 场景这个差距不重要，但 T5 系流水线对 SGLang 是 dealbreaker

### 生产采用
**SGLang 生产用户**：xAI Grok 3、Microsoft Azure、LinkedIn、Cursor、Oracle Cloud，跨 40 万+ GPU
**vLLM**：仍是多数云 API 端点和 OpenAI 兼容服务的默认后端

---

## 五、结构化输出：SGLang 的隐藏优势

2026 年大多数生产 AI 应用依赖结构化 JSON 输出，SGLang 此处有明显优势：
- 用**压缩有限状态机**做约束解码，比标准方法**快约 3 倍**
- 关键创新：**把每步 grammar mask 生成与 LLM 前向传播重叠**，隐藏约束执行的计算成本

---

## 六、迁移与上手

两者都几分钟安装，都提供 OpenAI 兼容 API（`/v1/chat/completions`）—— **切换只是改 base URL**。

| 调优重点 | SGLang | vLLM |
|---------|--------|------|
| 缓存保留设置 | ✓ 针对特定前缀模式调 | — |
| 批大小 + 内存分配 | — | ✓ 针对并发画像调 |

---

## 七、决策框架（抄作业版）

```
你的工作负载是什么？
├─ 多轮对话 / Agent（共享上下文）         → SGLang
├─ RAG（共享文档前缀）                    → SGLang
├─ 结构化 JSON 输出                       → SGLang
├─ DeepSeek 模型                          → SGLang（官方推荐）
├─ 批处理 + 每条 prompt 独特              → vLLM
├─ TPU / Trainium / Gaudi                → vLLM
├─ encoder-decoder（T5/BART）             → vLLM
├─ 凌晨踩坑需要大社区                     → vLLM
└─ 工作负载类型混合 + 有运维能力           → 两个都跑，按路由分发
```

**生产建议**：
- 3 人小团队 6 个月内 → "选团队已经熟悉的那个"，运维熟悉度胜过边际特性差异
- xAI、Microsoft、Cursor 等头部用户都已 SGLang 生产，可作为背书

---

## 八、对我们 Skill 库的启示

| 现有 Skill | 改进方向 |
|-----------|---------|
| `serving-llms-vllm` | 补充"何时该选 SGLang"章节；增加 prefix-cache 工作负载判别清单 |
| `llm-inference-optimization` | 加入 RadixAttention vs PagedAttention 架构对比；补充 DeepSeek MLA 优化路径 |
| `model-adapter` | Hermes Gateway 若有 RAG/多轮密集场景，可评估 SGLang 作为备选后端 |

**Jetson Orin Nano 部署注意**：本地推理（Ollama）与生产服务（vLLM/SGLang）属于不同量级，不可直接套用上述 H100 基准。但这些架构思想（前缀缓存、continuous batching）对 Jetson 优化同样有借鉴价值。

---

## 九、金句摘录

> *"The inference engine war isn't about which is 'better', it's about which architecture matches your memory access patterns. Get that right, and everything else follows."*

> *"Switching a multi-turn chatbot from vLLM to SGLang on the same H100 cluster routinely lifts throughput by 30%+ and trims five figures off monthly GPU spend, at zero application-code cost."*

> *"RadixAttention's benefit disappears for unique-prompt workloads."* —— Spheron 测试结论

---

## 十、参考链接

- Particula《SGLang vs vLLM in 2026》：https://particula.tech/blog/sglang-vs-vllm-inference-engine-comparison
- TECHSY《vLLM vs SGLang 2026: H100 Benchmarks》：https://techsy.io/en/blog/vllm-vs-sglang
- CallSphere《2026 Throughput Benchmarks on Real Workloads》：https://callsphere.ai/blog/td30-fw-sglang-vs-vllm-throughput-2026-honest-benchmarks
- GitHub long context track（sglang issue #3471）：https://github.com/sgl-project/sglang/issues/3471

---

**笔记结束** | 作者：猫仔夜间自学习引擎 | 关联 Skill：`llm-inference-optimization`、`serving-llms-vllm`

## 相关笔记
- [LLM推理引擎对比-SGLang-vs-vLLM](2026-07-31-LLM推理引擎对比-SGLang-vs-vLLM.md)
- [SGLang-vs-vLLM-推理引擎对比](explore/2026-05-19-SGLang-vs-vLLM-推理引擎对比.md)
- [LLM推理引擎2026格局-SGLang崛起与架构收敛](2026-08-05-LLM推理引擎2026格局-SGLang崛起与架构收敛.md)
- [llm-inference-engine-comparison-2026](2026-08-07-llm-inference-engine-comparison-2026.md)
- [LLM推理引擎竞争-vLLM-vs-SGLang](2026-08-14-LLM推理引擎竞争-vLLM-vs-SGLang.md)
