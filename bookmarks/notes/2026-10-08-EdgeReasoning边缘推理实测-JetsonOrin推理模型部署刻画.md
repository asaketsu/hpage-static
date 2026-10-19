# EdgeReasoning边缘推理实测-JetsonOrin推理模型部署刻画

> **来源**：arXiv 2511.01866（EdgeReasoning: Characterizing Reasoning LLM Deployment on Edge GPUs）
> **原文链接**：https://arxiv.org/abs/2511.01866
> **记录日期**：2026-10-08

**标签**：#LLM推理优化 #边缘计算 #JetsonOrin #量化 #推理模型 #实测刻画

---

## 一、内容整理

### 1.1 核心问题：推理模型上边缘 GPU 的延迟-精度权衡全景图

在 Jetson AGX Orin 64GB（2048 CUDA 核 / 64 Tensor 核 / 275 INT8 TOPS / 64GB LPDDR5 @204.8GB/s / 15-60W）上系统刻画 DeepSeek-R1 蒸馏系（1.5B/8B/14B）推理模型的部署特性。这张表直接回答"我们这台 Jetson 能跑什么推理模型、跑多快、费多少电"。

### 1.2 推理模型 vs 非推理模型：20 倍延迟代价

MMLU-Redux 准确率 / 延迟 / 能耗实测（vLLM 引擎，FP32 单批）：

- DSR1-Qwen-14B：80.6% / 207s / 2599 J/题
- DSR1-LLama-8B：61.7% / 143s / 4206 J/题
- DSR1-Qwen-1.5B：38.3% / 45s / 404 J/题
- 对照非推理：qwen2.5-7B 60.8% / 0.6s / 26J；llama3.1-8B 58.3% / 2.5s / 78J

> **核心数字：同规模（7-8B）下推理模型准确率只高 7%，但延迟和能耗高 20 倍以上。推理链是延迟的主体，不是模型参数。**

### 1.3 Decode 主导：99.5% 的时间在解码

- token 比例 prefill:decode = 1:7.3（Qwen 系更啰嗦），但延迟比例 1:521（1.5B）、1:192（8B）、1:569（14B）
- 解码占比 >99.5% —— 边缘部署优化只该砸在 decode 上
- TBT（token 间延迟）几乎不随上下文增长：8B 从 1k 到 4k 输入只涨 3.1%
- 实测 TBT：1.5B = 0.024s（41 tok/s）、8B = 0.10s（10 tok/s）、14B = 0.186s（5.4 tok/s）

### 1.4 解析性能模型（MAPE < 2%）

- Prefill：L = a·I_pad² + b·I_pad + c，I_pad 按 128 对齐（CUTLASS/Tensor Core padding 效应，实测呈台阶状）
- Decode：L = nO + m(IO + O(O-1)/2)，m 极小 ≈ TBT 恒定
- 功率：短输入恒定（低利用率），长输入对数增长（1.5B 仅 6W，8B/14B 4k 输入超 20W）
- 能耗/token：约 300 token 处最低（权重复用最优），之后进入 attention 主导的平台期
- 模型价值：14B 全量 MMLU 实测要 8 天，解析模型秒级出结果——**先建模后实测**是大规模扫参的正路

### 1.5 边缘 vs 云的成本账

DeepScaleR-1.5B（RL 微调数学推理模型）在 Orin 上：

- 单批 FP32：$0.302/百万 token（电 $0.024 + 硬件摊销 $0.278）
- batch 30：$0.027/百万 token —— **比 OpenAI o1-preview（$60）低三个数量级，AIME2024 准确率 43.1% vs 40.0% 反超**
- 结论：小推理模型+RL 微调+边缘部署 = 准确率可比云端大模型，成本低 100-2000 倍

### 1.6 量化与测试时扩展

- W4A16（LLM Compressor AWQ）在 Orin 上回退 INT8 执行（Ampere 架构不支持 INT4 kernel）——量化收益打折的硬件级根因
- 并行 test-time scaling（多路推理+投票）在不增加延迟的前提下提精度，前提是硬件利用率未饱和
- 序贯扩展（更长推理链）线性增加延迟，实时任务禁用

## 二、查询拓展

### 2.1 为什么 decode 在边缘是带宽瓶颈
Orin 的 FP16 FLOPs:bytes ≈ 1375，远高于 batch=1 GEMV 的算术强度——单批解码是纯带宽受限。这解释了为什么 14B（权重更大）TBT 是 1.5B 的 8 倍：每 token 都要把全部权重从 204.8GB/s 的 LPDDR5 搬一遍。边缘 SoC 与数据中心卡的差距主要在带宽而非算力。

### 2.2 与 NVIDIA 官方 Jetson 优化路径的关系
NVIDIA 技术博客（Frontier Reasoning Reaches the Edge）给出 NVFP4+推测解码在 Jetson 上最高 6.28× decode 吞吐提升，但 NVFP4 需 Blackwell 级硬件；Orin（Ampere）的现实选项是 FP8/INT8+推测解码。两篇对照读：官方给上限，本文给 Orin 实测下限。

### 2.3 DeepScaleR 路线
纯 RL（无蒸馏）微调 1.5B 底座在数学任务上追平 o1-preview，是"小模型+RL 微调"路线的代表作。与我们关注的"Agent 即策略模型"同源：任务特化的小策略网络 > 通用大网络。

## 三、归纳总结

### 3.1 Orin 部署决策框架

```
延迟预算 → 模型尺寸选择（解析模型反解）:
  ≤10s 级任务   → 1.5B 推理模型 (41 tok/s) 或 7-8B 非推理
  30-60s 任务   → 8B 推理模型 (10 tok/s), W4 量化提吞吐
  离线/批量     → 14B + batch (精度 80.6% 值得等)

优化杠杆优先级（边缘 decode 主导场景）:
  1. 砍推理链长度（prompt 控制/预算指令）→ 直线降延迟
  2. 量化 W4A16（Orin 实际 INT8 执行）
  3. 并行 TTS 多路投票（不增延迟, 硬件未饱和时免费提精度）
  4. 推测解码（草稿模型 draft 1.5B 服务 14B）
```

### 3.2 三个反直觉发现

- **上下文长度对 TBT 几乎无影响**（4k 才 3.1%）：不必为长上下文焦虑延迟恶化
- **能耗/token 在 300 token 处最优**：超长 prompt 的边际能耗是平台期而非恶化
- **小模型能效比是数量级优势**：1.5B 每 token 能耗是 14B 的 1/7，批量场景小模型+RL 微调完胜

## 四、趋势判断

### 趋势1：边缘推理模型进入"RL 微调小模型"时代
依据：DeepScaleR 1.5B 用 RL 微调追平 o1-preview（43.1% vs 40.0% AIME）而成本低三个数量级。蒸馏大模型（DSR1 系列）不再是小推理模型唯一来源。

### 趋势2：性能解析模型将成为部署标配前置步骤
依据：本文 MAPE<2% 的拟合模型把 8 天实测压缩到秒级；DUCK 的黄金档扫描、eval 门禁共享同一逻辑——先解析模型粗筛再定点实测。

### 趋势3：decode 带宽墙推动边缘专用注意力优化
依据：99.5% 时间在 decode + GEMV 带宽受限，量化只解决权重搬运量（且 Orin 上 INT4 回退 INT8），结构性出路在推测解码与稀疏注意力。

### 趋势4：机器人端侧推理的成本闭环成立
依据：$0.027/百万 token（batch）让"每台机器人本地跑推理"比云端 API 经济上可持续，与 EdgeReasoning 开篇的自主系统叙事闭合。

## 五、关联分析

### 5.1 与本机环境（jbot = Jetson 或同级）的关联
- 本机 luxtts-daemon、nexa-local-inference（Ollama on Jetson）当前都跑非推理模型；若引入本地推理模型做复杂任务规划，TBT 表（41/10/5.4 tok/s @1.5/8/14B）就是直接选型依据
- jbot 作为 Hermes Gateway 主机，其 20:35 OOM 事件（可用内存 290MB）说明内存预算紧张——1.5B FP16 约 3GB、W4 后约 1GB，部署前必须留 Gateway 余量
- 推理模型 20× 延迟对交互式 Agent 不可接受，但对夜间自学习（本 cron 任务）完全可行——**夜间本地深度推理、白天轻量响应**的分时架构有了数据支撑

### 5.2 与既有笔记/技能的关联
- [HuggingFace详细教程-从调用模型到微调与部署](2026-10-07-HuggingFace详细教程-从调用模型到微调与部署.md)：LoRA 微调+Spaces 部署的下一步就是本地推理模型部署，本文提供 Orin 实测基准
- llm-inference-optimization skill（PagedAttention/量化/推测解码/连续批处理）：本文是这些技术在边缘端的实测校准——PagedAttention 在边缘单用户场景收益有限，量化+推测解码才是边缘主角
- edge-llm-quantization skill（GGUF/TensorRT-LLM）：Orin 上 INT4 量化回退 INT8 的坑（Ampere 无 INT4 kernel）应补进该 skill 的硬件兼容性清单
- [Agent记忆2026-自进化与基准](2026-10-06-Agent记忆2026-自进化与基准.md)：夜间自学习 cron 与推理模型的延迟特性天然匹配

### 5.3 与 DUCK 项目的关联
DUCK 真机 54ms/拍的策略推理循环要求 <20ms 模型前向；本文方法（解析延迟模型先拟合再扫参）可直接迁移到"策略网络尺寸×控制频率"的可行性预算表——与 jetson-tensorrt-deploy 的 INT8 转换实测互补。

## 六、金句摘录

> 「Reasoning models incur over 20× higher inference latency than non-reasoning models.」——推理能力的价格是 20 倍延迟，先想清楚要不要付

> 「Decode dominating over 99.5% of total inference time.」——边缘优化只该砸在 decode，prefill 优化是伪需求

## 七、行动启示

- **edge-llm-quantization skill 增补**：Orin（Ampere）上 W4A16 回退 INT8 执行的硬件兼容性条目——这是部署前必须知道的算力打折
- **本机部署决策**：jbot 若跑本地推理模型，选 1.5B 级（41 tok/s 可交互）；8B+ 只适合后台批量任务
- **夜间学习管线**：本 cron 任务的深度分析环节可考虑本地推理模型承担（延迟不敏感），白天交互保持轻量
- **解析模型先行**：任何"尺寸-延迟"决策先用本文公式族拟合本地实测 3-5 点，再外推全域——避免 8 天级实测

## 八、拓展应用推荐

1. **Hermes 推理路由层**：按任务延迟敏感度分流——交互用 1.5B/云端，夜间批量用本地 8B+，与 adaptive-inference-routing skill 的预算自适应路由直接对接
2. **DUCK 上位机推理预算表**：策略前向 <20ms 硬约束下，用 TBT 模型反推最大可行网络尺寸，写入 duck-h1-deployment 的部署前检查
3. **成本看板**：把 $0.027-0.302/百万 token 的边缘成本账加进 observability-dashboard，与云端 API 成本对照展示

## 九、指南分析

**方法论价值**：实测刻画→解析建模→模型加速扫参的三段式，是所有"设计空间大而实测贵"问题的通用解法。DUCK 的黄金档扫描（全档 12ep 验收太贵→中间档抽查）已是同构实践。

**可复用的实验设计**：
- 拟合验证用 50 个 held-out 问题、MAPE<2% 才可信——比"看着像"的曲线 eyeballing 严格
- 功率/能耗分 prefill/decode 单独建模，与延迟模型解耦——避免单一指标掩盖两阶段的不同物理瓶颈

**局限与保留**：单硬件平台（Orin 64GB MAXN 模式）、单引擎（vLLM）、DSR1 蒸馏系模型——数字不可直接外推到 Thor/其他引擎/其他模型系；W4A16 的 INT8 回退是 vLLM+CUTLASS 组合行为，TensorRT-LLM 路径可能不同。MMLU-Redux 准确率与数学类基准的排序不完全一致。


## 相关笔记

- [MiniCPM-Robot 1.5B VLA 开源](./2026-10-07-MiniCPM-Robot-1.5B-VLA开源.md) — 端侧 1.5B 机器人模型，部署硬件同域
- [HuggingFace 详细教程：微调与部署](./2026-10-07-HuggingFace详细教程-从调用模型到微调与部署.md) — 上游微调→部署管线视角
- [Harness 内模型路由降本 64% 实录](./2026-10-02-Harness内模型路由-LangChain降本64%实录.md) — 推理成本路由决策层
- [Qwen3.8-27B FP8 使用指南](./2026-08-21-Qwen3.8-27B-FP8使用指南-三条推理路线完整代码.md) — 三条推理路线部署对照
