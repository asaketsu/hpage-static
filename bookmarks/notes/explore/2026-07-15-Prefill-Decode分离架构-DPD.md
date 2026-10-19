# Prefill-Decode 分离架构：LLM 推理服务的范式级变革

> 深度学习笔记 | 2026-07-15 | 兴趣等级 L3 | 来源: web_search(10篇) + 已有笔记交叉
> 说明：本轮 web_extract/Tavily 全挂，走 search-fallback-chain 降级，综合搜索摘要 + 已有笔记产出

## 一、核心问题：为什么要把 Prefill 和 Decode 拆开？

LLM 推理的每一个请求都经过两个截然不同的阶段，而它们对硬件的要求完全相反：

- **Prefill（预填充）**：对用户的完整 prompt 做一遍前向传播，生成所有 token 的 KV Cache。这是 **compute-bound（计算密集型）**——GPU 的 Tensor Core 满载，内存带宽不是瓶颈。
- **Decode（解码）**：一次只生成一个 token，再重复。每轮都要从内存读取完整的模型权重 + 增长的 KV Cache。这是 **memory-bound（内存带宽密集型）**——Tensor Core 大量空闲，等待 DRAM。

传统框架（包括早期 vLLM）将 Prefill 和 Decode **colocate（同址混合）**在同一个 GPU 上。这造成一个结构性问题：当一条超长 prompt 的 Prefill 正在运行时，它占住了 GPU 的计算单元，Decode 请求被迫排队等待——**长 prompt 会拖垮所有并发请求的每 token 延迟**。

> **核心矛盾**：用一台 GPU 同时跑两种对硬件需求截然相反的工作负载，本质上是在用同一个桶装两种不同密度的液体。

## 二、Disaggregated Prefill-Decode（DPD）：架构设计

DPD 的核心思想极为简洁——**把 Prefill 和 Decode 放到不同的 GPU 池上，各取所需**：

```
用户请求 → Router（路由层）
          ├→ Prefill Node（H100/B200）→ 前向传播 → 生成 KV Cache
          │                                ↓
          │                          RDMA 传输 KV Cache
          │                                ↓
          └→ Decode Node（H200） → 接收 KV Cache → 生成输出 tokens
```

### 关键技术要点

**1. KV Cache 跨节点传输**

Prefill 完成后，KV Cache 必须从 Prefill Node 传到 Decode Node。这是整个架构的关键瓶颈。传输方式演进：

- **NIXL**（vLLM 主推）：底层用 RDMA + GDS，支持 `NixlConnector`、`MultiConnector`、`OffloadingConnector`、`FlexKVConnectorV1` 等多种连接器
- **AMD MORI-IO**：2026-04 发布，实现**单节点内**的 Prefill-Decode 分离，无需多节点 RDMA 集群
- **MoonCake**：KV-Cache 为中心的分离层，提供分布式内存池，让 KV 块在 Prefill-Decode 边界保持存活

**2. Router 的两种模式**（vLLM MORI-IO 实现）：

| 模式 | 行为 | 延迟特性 |
|------|------|---------|
| **READ** | Proxy 等待 Prefill 完成 → 提取 remote_block_ids → 转发给 Decode | 串行，延迟更高但可控 |
| **WRITE** | Prefill 和 Decode **并发**调度，Proxy 不等 Prefill | 延迟更低，需要 Decode 实例已就位 |

**3. vLLM 官方接入方式**（实验性，v0.7+）：

```bash
# Prefill 实例
vllm serve MODEL --kv-transfer-config '{"kv_connector":"NixlConnector","kv_role":"kv_prefill"}'

# Decode 实例  
vllM serve MODEL --kv-transfer-config '{"kv_connector":"NixlConnector","kv_role":"kv_decode"}'
```

核心抽象三层：`KVConnector`（传输层）→ `KVTransferAgent`（调度层）→ `KVCacheTransfer`（接口层），全部位于 `vllm/distributed/kv_transfer`。

## 三、生产落地现状（18个月演进）

DistServe 团队 2025 年中回顾显示，DPD 已从研究走向工业标配：

- **已采用框架**：NVIDIA Dynamo、llm-d、Ray Serve LLM、**SGLang**、**vLLM**、LMCache、MoonCake——几乎全部主流生产框架都在跑分离架构
- **AWS SageMaker HyperPod**：已提供原生 DPD 部署，通过 Elastic Fabric Adapter (EFA) + RDMA 实现 GPU 间零拷贝传输
- **实测收益**：长 prompt 场景下 per-token 延迟显著降低；goodput（有效吞吐）提升；吞吐更可预测

## 四、多轮对话的增量 Prefill 问题（2026 新发现）

arXiv 2602.14516v1（AMPD）指出：现有 DPD 系统忽略了**多轮推理中的 interleaved prefill-decode 模式**——每一轮对话都带来增量 Prefill（新对话的 prompt 部分），这些增量 Prefill 该如何调度？

AMPD 的方案：基于实时负载自适应决定 Prefill 在哪里执行、如何调度，以最大化 SLO 达成率。同时针对两阶段设计最优资源分配与并行策略规划算法。

> **关键启示**：DPD 对单轮推理效果显著，但在 Agent 多轮对话场景下，"增量 Prefill 调度"才是真正难题——这也是为什么 LLM Agent 的延迟问题在 2026 年仍未根治的深层原因之一。

## 五、单节点 DPD 的崛起（2026 突破）

AMD MORI-IO（2026-04）实现了**单节点内**的 Prefill-Decode 分离，不需要多节点 RDMA 集群。这意味着：

- 中小规模部署也能享受 DPD 的收益
- 降低了硬件门槛（不需要 InfiniBand/EFA 等 RDMA 网络）
- **对我们的价值**：Hermes/Jetson 这类单机部署，未来可借助 MORI-IO 或类似方案优化长 prompt 处理

## 六、与现有工作（Skill/笔记）的关联与改进建议

### 对本项目的直接价值

| 维度 | 关联 | 建议 |
|------|------|------|
| **vLLM 部署** | 已有 `llm-inference-optimization` skill | 应补充 DPD 配置章节，尤其是 `--kv-transfer-config` 参数详解 |
| **KV Cache 量化** | 已有 KVarN/TurboQuant 笔记 | DPD 与 KV 量化叠加使用——跨节点传输时 KV 量化可显著降低带宽开销 |
| **Jetson 边缘部署** | 已有 edge-llm-quantization skill | 单节点 DPD（MORI-IO 模式）是边缘部署长 prompt 的新选项 |
| **三层优化栈** | 已有 2026-07-11 笔记 | DPD 应作为系统层（Layer 2）的独立技术加入三层栈表 |

### P0：更新 `llm-inference-optimization` skill

技能中"推理引擎横评"和"系统层优化"章节缺少 DPD 内容。应追加：
- DPD 架构简介（1段）
- vLLM `--kv-transfer-config` 参数示例
- READ/WRITE 模式决策
- 与 KV 量化叠加策略

### P1：更新三层栈笔记

`2026-07-11-LLM推理优化2026全景` 中系统层仅列了 PagedAttention/连续批处理/推测解码，应新增 DPD 行。

### P2：边缘部署技能补充

`edge-llm-quantization` skill 中增加"单节点 DPD 是长 prompt 边缘推理的候选方案"说明。

## 七、关键风险与盲点

| 风险 | 说明 | 来源级别 |
|------|------|---------|
| **RDMA 依赖** | 多数 DPD 实现需要 RDMA（InfiniBand/EFA），硬件成本高 | 官方文档验证 |
| **生产成熟度** | vLLM DPD 仍标记为 experimental，API 可能变动 | 官方文档 |
| **多轮增量 Prefill** | 现有系统未充分处理，Agent 场景延迟改善有限 | arXiv 论文（社区复现） |
| **KV 传输带宽** | 长 prompt 场景 KV Cache 巨大，跨节点传输成为新瓶颈 | 工程实践推断 |
| **单节点收益有限** | 单节点 DPD 省掉了 RDMA 成本，但吞吐提升幅度远小于多节点 | 社区 benchmark |

## 八、Actionable Insights

1. **DPD 不是万能药**：只在长 prompt + 高并发 decode 混合场景有显著收益。纯短文本服务用 colocated 更简单
2. **DPD + KV 量化是必杀组合**：跨节点传输的 KV Cache 若先量化，带宽开销可降低 3-6 倍，使 DPD 在低成本网络上可行
3. **Agent 场景的真正痛点在增量 Prefill**：AMPD 的思路（自适应 Prefill 调度）值得关注，可能成为 Agent 延迟优化的突破口
4. **MORI-IO 单节点 DPD 降低门槛**：2026 年中小规模部署可无成本试用 DPD 理念

## 九、一页速查

> **Prefill = compute-bound**（跑 prompt 前向传播，Tensor Core 满载）
> **Decode = memory-bandwidth-bound**（逐 token 生成，等 DRAM）
> **DPD = 两阶段分池，各取所需**
> **关键挑战 = KV Cache 跨节点 RDMA 传输**
> **vLLM 接入 = `--kv-transfer-config` + NixlConnector**
> **2026 新方向 = 单节点 DPD（MORI-IO）+ 增量 Prefill 调度（AMPD）**
> **DPD + KV 量化 = 长 prompt 高并发推理的最优组合**

## 十、待深入

- [ ] AMPD（arXiv 2602.14516）全文精读：增量 Prefill 自适应调度算法
- [ ] MoonCake KV-Cache 分布式的架构细节
- [ ] SGLang 的 RadixAttention + DPD 叠加实测
- [ ] MORI-IO 在 AMD GPU 上的部署实测（本地不可用，记录待办）

## 十一、来源列表

- web_search 结果：jarvislabs.ai (DPD 架构详解)、haoailab.com (DistServe 18个月回顾)、AWS SageMaker HyperPod 博客、vLLM MORI-IO 官方博客、vLLM 官方 disagg_prefill 文档
- 论文：AMPD (arXiv 2602.14516v1)
- 已有笔记：`2026-07-11-LLM推理优化2026全景`、`2026-06-05-KVarN-华为vLLM原生KV-Cache量化后端`
- 来源标注：本轮 web_extract 全挂，综合搜索摘要 + 已有笔记交叉产出

## 相关笔记

- [本地模型部署: vLLM V1 APC](./2026-07-14-本地模型部署-vLLMV1-APC.md) — vLLM V1自适应预分配缓存
- [FreqDepthKV: KV Cache压缩新范式](./2026-07-14-FreqDepthKV-VeriCache-KVCache压缩新范式.md) — 频率深度感知KV压缩
- [MemDecay: 区域感知KV Cache驱逐](./2026-07-15-MemDecay.md) — Agent场景KV驱逐（跨集群）
- [Memory Compaction Rate Distortion](./2026-07-12-MemoryCompactionRateDistortion.md) — KV压缩率失真理论
