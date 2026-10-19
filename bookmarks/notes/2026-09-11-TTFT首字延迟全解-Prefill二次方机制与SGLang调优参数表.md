# TTFT 首字延迟全解：Prefill 二次方增长机制 + SGLang 调优参数表 + 海光 DCU 访存瓶颈诊断——千问对话精读 + 推理体系整合

> **来源**：千问（Qwen）分享对话《模型推理中的首字延迟》2026-09-10
> **原文链接**：https://qianwen.my.cn/share/chat/0be7c2a50b1f4e329a2b717529d8e07f
> **抓取方式**：本地 Chromium CDP 渲染直读（新 tab 开页面 + innerText 提取，2.5KB 全文；滚动确认无懒加载增量）
> **笔记日期**：2026-09-11
> **关联笔记**：《LLM八种精度格式全解》（KV Cache 是另一半内存成本）《PushingLocalAIForward》（DGX Spark 推理 recipe）《显卡微调小模型精度选择指南》《LLM推理优化技术》（PagedAttention/连续批处理）

---

## 零、结论先行

**这份对话回答三个递进问题：①TTFT 是什么（推理指标非训练指标）②为什么长（Prefill 阶段近似二次方计算 + 排队 + 网络）③怎么治（SGLang 分块预填充/调度保守度/显存比例/NUMA 绑定，海光 DCU 专属 LightOp 算子族）。**

价值定位：**这是 TTFT 主题的"参数级实操"补充**——精度格式笔记讲了"KV Cache 是另一半内存成本"，本篇给出 KV Cache 挤占导致卡停的具体调优参数表。与我们体系的对接点：智谱 pool@8899 并发≈1 必 429 的排队延迟、sparkDash 的 tok/s 监控、未来自建推理服务的参数基线。

## 一、TTFT 概念澄清（忠实还原）

**第一问：训练中的 TTFT 是什么？**

千问先纠正概念误区：**TTFT 不是训练指标，是推理/服务部署指标**——从请求发出到收到流式输出第一个 Token 的时间间隔，决定用户感知的"反应速度"。

**构成链**：
```
用户请求 → [网络传输] → [服务排队] → [Prefill 预填充] → 第一个 Token
                                      ↑ 几乎完全由这个决定
```

**Prefill 阶段机制**：模型不逐字计算，一次性**并行处理所有输入 Token**，构建 KV Cache。TTFT 几乎完全由 Prefill 耗时决定。

### 1.1 四个关键影响因素

| 因素 | 机制 |
|------|------|
| **Prompt 长度** | Prefill 计算量**近似二次方增长**（注意力 O(n²)） |
| 模型规模 | 参数量越大 Prefill 越耗时 |
| 并发压力 | 负载高时排队等 GPU 算力 |
| 硬件与引擎 | PagedAttention/连续批处理/前缀缓存等优化 |

### 1.2 体验阈值表

| 场景 | 推荐 TTFT |
|------|----------|
| 用户体验感知阈值 | < 1000ms（超过明显卡顿） |
| 实时对话/客服 | < 300-500ms |
| 代码助手 | < 500ms-1s |
| 长文档分析/创意写作 | < 2-3s |

## 二、实战问题一：海光 DCU TTFT 2 秒 + 输出 170 字卡停（SGLang）

**第二问的答案是一张参数级调优清单**（对话核心价值）：

### 2.1 核心参数调优

| 参数 | 推荐值 | 机制 |
|------|--------|------|
| `--chunked-prefill-size` | 4096 | **长 Prompt 分块与 Decode 交错**——防止单次 Prefill 阻塞全局（卡停的第一嫌疑） |
| `--schedule-conservativeness` | 0.8-1.2 | 调度保守度：太激进→OOM/频繁 GC 卡顿；太保守→GPU 算力空洞 |
| `--mem-fraction-static` | 0.85-0.95 | 为 KV Cache 预留足够连续显存 |
| `--max-running-requests` | 64-256 压测 | 太大→OOM/上下文切换延迟；太小→算力不满 |

### 2.2 海光 DCU 专属优化

| 项 | 内容 |
|----|------|
| NUMA 绑定 | **提升 20%-40% 多卡并行效率**——GPU 访问最近的 CPU 内存节点 |
| DTK 版本对齐 | 深算二号 K100 → DTK 26.04 + 对应 ROCm 版 PyTorch |
| 设备节点映射 | Docker 必须 `--device=/dev/kfd --device=/dev/dri --device=/dev/mkfd`，否则底层通信降级 |
| 环境变量 | `SGLANG_USE_LIGHTOP=1` 等 DCU 专用变量 |

## 三、实战问题二：K100 AI 跑 DeepSeek-Flash-v4 的访存瓶颈诊断

**第三问给出的是诊断方法论**（比参数表更有价值）：

### 3.1 诊断：先确认瓶颈类型再动手

```
rocprof / rocm-smi 采集内核耗时
    ↓
显存控制器繁忙度 >90% 且 VALU（向量计算单元）利用率低
    ↓
= 典型"访存瓶颈"（memory-bound）
    ↓
此时单纯增加算力毫无意义——核心方向必须是减少显存读写
```

**这个诊断模式与 GPU 容量估算笔记的"先测瓶颈再扩容"完全同构**——避免"加卡解决一切"的误区。

### 3.2 访存瓶颈的算子级优化（DCU 专属环境变量族）

| 环境变量 | 作用 |
|---------|------|
| `SGLANG_USE_LIGHTOP=1` | LightOp 轻量算子——降 Decode 延迟关键 |
| `SGLANG_USE_FUSED_TOPK_SOFTMAX=1` | 融合 TopK+Softmax——减少显存读写次数 |
| `SGLANG_USE_CAUSAL_CONV1D=1` | Causal Conv1D |
| `SGLANG_USE_AITER_LINEAR_ATTN=1` | AITER Linear Attention |
| `PYTORCH_HIP_ALLOC_CONF=max_split_size_mb:128,garbage_collection_threshold:0.8` | 减少高并发显存碎片，改善**长尾延迟 P99 TPOT** |

### 3.3 系统级四件套

1. **分块预填充**（同 2.1）
2. **前缀缓存** `--enable-prefix-caching`：SGLang 的 RadixAttention——多轮对话/共享 System Prompt 场景显著省显存加速生成
3. **NUMA 亲和绑定**（同 2.2）
4. **投机采样排查**：开着投机采样时先关掉观察卡停是否消失

## 四、与我们体系的对接点

### 4.1 概念层：补全推理性能的三指标

| 指标 | 含义 | 我们的相关经验 |
|------|------|---------------|
| **TTFT** | 首字延迟（Prefill 决定） | 智谱 MCP 快返=网关 SSE 失效时的体感 |
| TPOT | 每 Token 输出时间（Decode 决定，memory-bound） | 本对话卡停问题=TPOT 长尾 |
| 吞吐 | tokens/s（sparkDash 监控的正是这个） | Mia 笔记 LlmProbe 的多后端 tok/s |

**精度格式笔记的闭环**：那篇说"Prefill 是算力瓶颈（compute-bound）并行处理输入，Decode 是带宽瓶颈（memory-bound）逐 token 生成"——本篇的调优参数正是这个二分法的工程化：chunked-prefill 平衡两者、访存优化治 Decode、前缀缓存复用 Prefill。

### 4.2 参数表的实际用途

| 场景 | 用途 |
|------|------|
| 未来自建推理服务（ASA/AutoDL） | SGLang 参数基线（chunked-prefill/mem-fraction/max-running） |
| 智谱 pool@8899 排队延迟分析 | 理解"并发≈1 必 429"背后的排队+Prefill 机制 |
| sparkDash 类监控建设 | TTFT/TPOT/吞吐三指标分离监控 |

### 4.3 诊断方法论的同构

"显存控制器繁忙 >90% 且 VALU 低 = 访存瓶颈"与我们 GPU 容量估算的"先测瓶颈再扩容"、Jetson 24h 笔记的"七因诊断框架"同一模式——**先诊断瓶颈类型，再定向优化，反对盲目加资源**。这是今日第三份独立收敛的"诊断先于修复"。

## 五、批判性审视

1. **数字多为经验值无出处**：NUMA 提升 20%-40%、mem-fraction 0.85-0.95、max-running 64-256 等推荐值是社区经验非官方文档——方向可信但具体值需实测校准
2. **"Prefill 近似二次方增长"的限定**：严格说注意力是 O(n²) 但有 FlashAttention 类优化将显存降到 O(n)，计算量仍是平方级——"近似"用词准确但未展开
3. **海光 DCU 特异性**：LightOp/AITER 算子族是 DCU 生态专属，NVIDIA GPU 上对应 CUDA Graph/TensorRT-LLM 的融合算子——不可直接平移，但"减少显存读写"的方向通用
4. **TTFT 阈值表缺场景限定**：300ms 实时对话阈值隐含了网络 RTT 前提——跨国 API 调用光网络就吃掉 200ms+，纯服务端优化无法达标
5. **对话未覆盖 TTFT 的最重要优化**：模型侧的 KV Cache 压缩（如 MLA/GQA）比引擎参数调优收益更大——精度格式笔记里 DeepSeek V4 把 1M ctx cache 压到 1/10 就是这个方向，本对话完全没提

## 六、金句提取

> "TTFT 几乎完全由这个预填充阶段的耗时决定。"

> "输入的文本越长，预填充阶段的计算量（近似二次方增长）就越大。"

> "显存控制器繁忙度长期维持在 90% 以上，而向量计算单元利用率偏低——这就是典型的访存瓶颈。此时单纯增加算力毫无意义。"

> "将长 Prompt 分块与 Decode 任务交错执行，防止单次预填充阻塞全局。"

## 七、局限性

1. 千问对话为 AI 生成内容（页脚自带"可能不准确，请注意核实"）——参数推荐值未逐一对官方文档核实（SGLang 参数名真实存在，方向与官方文档一致，具体推荐区间为社区经验）
2. 海光 DCU/DTK 部分无法在我们环境验证（无海光硬件）
3. 对话结构是"一问一答 + 引用来源数"（6篇/3篇/4篇来源）——具体引用文献不可见
4. 第四章体系对接为本笔记扩展
5. 体验阈值表的原始出处（业界惯例？某大厂规范？）未标注

## 出处标注

| 章节 | 来源类型 |
|------|---------|
| 一至三 | **原文忠实还原**（CDP 直读 2.5KB 全文） |
| 四 | **体系映射**（本笔记扩展，与精度格式/sparkDash/GPU容量估算笔记交叉） |
| 五 | **批判性审视**（本笔记扩展） |

## 相关笔记

- [LLM推理引擎2026格局-SGLang崛起与架构收敛](./2026-08-05-LLM推理引擎2026格局-SGLang崛起与架构收敛.md) — SGLang 架构背景
- [LLM批处理三策略详解](./2026-09-01-LLM批处理三策略详解-静态动态连续与ChunkedPrefill.md) — ChunkedPrefill 与 TTFT 直接相关
- [llm-inference-engine-comparison-2026](./2026-08-07-llm-inference-engine-comparison-2026.md) — 引擎横评
