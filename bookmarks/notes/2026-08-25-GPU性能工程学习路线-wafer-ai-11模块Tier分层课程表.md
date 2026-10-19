# GPU 性能工程学习路线 — wafer-ai 1.3k Star 课程表：从 CUDA 基础到前沿 AI Lab 的 11 模块 Tier 分层

> **来源**：微信公众号导流帖 + [wafer-ai/gpu-perf-engineering-resources](https://github.com/wafer-ai/gpu-perf-engineering-resources)（GitHub，1.3k Star / 165 Fork）
> **导流帖**：https://mp.weixin.qq.com/s/uSAQ4xt6ryIrwDOxNX82qg
> **定位**：GPU 性能工程课程表——"from scratch to what the frontier AI labs do"
> **记录日期**：2026-08-25

**标签**：#CUDA #GPU性能工程 #学习路线 #Triton #CUTLASS #FlashAttention #vLLM #LLM生成内核

---

### 7 模块索引

| 模块 | 对应章节 |
|------|---------|
| tag 标签 | 头部标签行 |
| 出处 | 头部出处行 |
| 内容整理 | 第一~二章 |
| 查询拓展 | 第三章（本机选路建议） |
| 归纳总结 | 第四章（Tier 学习法） |
| 趋势判断 | 第五章 |
| 关联分析 | 第六章 |
| 拓展应用推荐 | 第七章 |
| 指南分析 | 第八章 |

---

## 一句话总纲

> **这是目前最系统的 GPU 性能工程开源课程表：11 大模块（基础→GEMM→TensorCore→Attention→编译器→调优→AMD→生产推理→LLM 生成内核→分布式→行业视野），每模块按 Tier 1/2/3 分层（必读→进阶→前沿）。最大特色是"LLM-Generated Kernels"独立成章——AI 写 GPU 内核已从论文走向工程实践（KernelBench/AlphaEvolve/CUDA-L1）。本机价值：Jetson TensorRT 优化的系统性学习地图。**

---

## 一、内容整理

### 1.1 项目定位

wafer-ai（招聘中的 AI infra 公司）维护的学习指南，覆盖"从零基础到前沿 AI 实验室在做什么"的完整路径。**质量门禁严格**：只要一手来源（论文/官方文档）+ 实践者博客 + 活跃维护或永恒基础——拒绝表面教程和 AI 生成未验证内容。

**阅读方法**：按 Tier 横切——先读所有主题的 Tier 1，再读所有 Tier 2，依次递进。

### 1.2 11 模块 × Tier 分层精选

| # | 模块 | Tier 1（必读） | 亮点 |
|---|------|---------------|------|
| 1 | **Fundamentals** | PMPP 教科书（第 5 版含 Ampere/Hopper/Blackwell）/ GPU Mode 讲座（23k Discord）/ CUDA 编程指南 | 架构深潜：Hopper TMA/WGMMA、Blackwell 微基准（arXiv 2507.10789） |
| 2 | **GEMM** | siboehm 经典教程（tiling/共享内存/向量化）/ Aleksa Gordić 47 图解剖（PTX/SASS/roofline） | DeepGEMM：DeepSeek 的 ~300 行干净 FP8 GEMM |
| 3 | **Tensor Cores** | SemiAnalysis 进化史（WMMA→MMA→WGMMA→tcgen05）/ PyTorch Hopper TMA | Blackwell 专章：tcgen05/TMEM/2SM MMA/CuTeDSL 流水线 |
| 4 | **Attention** | FlashAttention 1/2/3 三部曲论文 | FlashInfer（MLSys 2025 最佳论文）/ MLA 低秩压缩 8x |
| 5 | **编译器与 DSL** | Triton 官方+编译管线深潜（Python→MLIR→PTX→CUBIN） | CUTLASS/CuTe/TileLang（1075x 加速）/ThunderKittens/Mojo/cuTile（CUDA 13.1 新） |
| 6 | **调优** | Nsight Roofline / Occupancy Calculator / Hopper 调优指南 | CUDA Graphs（5x）/ Warp 特化（Tawa 自动化达 FA-3 水平） |
| 7 | **AMD 与异构** | ROCm 上写 Triton（MI300X） | HipKittens（ThunderKittens AMD 版）/ Pallas TPU / vLLM TPU 后端 |
| 8 | **生产推理** | vLLM / SGLang / TensorRT-LLM / cuDNN 9 | Orca 连续批处理（36.9x）/ Medusa/EAGLE 投机解码 |
| 9 | **LLM 生成内核** ⭐ | KernelBench（Stanford）/ KernelLLM（Meta 8B，胜 GPT-4o）/ TritonBench | AlphaEvolve（FA 32.5% 加速）/ Kevin 多轮 RL（82% 正确率）/ CUDA-L1（3.12x） |
| 10 | **分布式** | NCCL / Demystifying NCCL / Meta NCCLX（10 万卡） | Megatron-LM（47% MFU）/ TP 教程 / Horovod（90% 扩展效率） |
| 11 | **行业视野** | Michal Pitr / cudaforfun / Lei Mao / Aleksa Gordić 四博客 | GPU Mode 社区（周讲座+内核排行榜） |

### 1.3 特色：LLM-Generated Kernels 独立成章（模块 9）

这是本课程表最前沿的部分——**AI 写 GPU 内核已成工程方向**：

| 方向 | 代表 | 成绩 |
|------|------|------|
| 基准 | KernelBench（250 个 PyTorch 负载，fast_p 指标） | 评测标准 |
| 专用模型 | KernelLLM（Meta，8B，25k PyTorch→Triton 对训练成） | 胜 GPT-4o |
| Agent 进化 | Sakana AI CUDA Engineer / AlphaEvolve | 10-100x（含刷榜争议）/ FA 32.5% |
| RL 训练 | Kevin（多轮 RL）/ CUDA-L1（对比 RL） | 82% 正确率 / 3.12x 平均加速 |
| AMD 侧 | GEAK（Triton 内核 Agent） | MI300X 上 1.81x |

### 1.4 导流帖诚实声明

公众号原文自己说："这份仓库是学习资源索引，**没有实操代码**。想要真正掌握需要搭配 GPU 硬件、CUDA/ROCm 工具链动手实践。"

---

## 二、查询拓展

### 2.1 与本机 Jetson 工作的关系

Jetson Orin（本机）的 TensorRT 部署优化对应模块 6（Profiling）+ 模块 8（Production Inference）：

| 本机需求 | 课程表对应 |
|----------|-----------|
| TensorRT 引擎转换/FP16/INT8 | 模块 3 精度格式（E4M3/E5M2/NVFP4） |
| 推理延迟优化 | 模块 6 Nsight Roofline + CUDA Graphs |
| KV Cache 管理（LuxTTS/LLM） | 模块 4：PagedAttention/MLA 8x 压缩 |
| 边缘部署 | 模块 8 vLLM/SGLang（Jetson 可跑） |

### 2.2 与 CUDA vs MLX 笔记（同日）的衔接

同日 CUDA/MLX 对比笔记给出了"选哪边"，本文给出"CUDA 边怎么学"——两者构成完整的 GPU 工程决策+学习路径。

---

## 三、归纳总结：Tier 学习法

```
Tier 1（全部主题）：建立全景——PMPP/官方文档/经典论文（FA 系列）
    ↓
Tier 2（全部主题）：深入实现——架构微基准/CUTLASS/连续批处理
    ↓
Tier 3（按需）：前沿专精——PTX/SASS 逆向/Blackwell tcgen05/投机解码
```

**横切而非纵切**是核心设计：先把所有模块的 Tier 1 读完（全景），而不是一头扎进单模块到底——避免"只会 GEMM 不懂推理系统"的偏科。

---

## 四、趋势判断

### 趋势 1：LLM 生成内核将从研究走向工程标配

> 依据：模块 9 的密度（基准+专用模型+Agent 进化+RL 训练+AMD 全链条）——AlphaEvolve 已给 FlashAttention 提速 32.5%，CUDA-L1 在 KernelBench 平均 3.12x。当 KernelLLM 类 8B 专用模型开源可跑，**"AI 写内核+人审"会成为性能工程的标准工作流**——与本机"AI 写代码+人验证"的判断归属框架（忆流笔记）同构。

### 趋势 2：GPU 性能工程知识正在从"部落知识"标准化为课程

> 依据：PMPP 第 5 版覆盖到 Blackwell、GPU Mode 社区 23k 人周讲座、本课程表 11 模块 Tier 化——原本散落在 NVIDIA 博客/个人 worklog/arXiv 的碎片知识正在被结构化。**性能工程师的培养周期将从"多年学徒"压缩到"系统性课程+实操"**——与评测三部曲的"能力地图"逻辑一致：先有地图，再谈精通。

---

## 五、关联分析

| 笔记/Skill | 关系 |
|-----------|------|
| [CUDA vs MLX 深度对比](2026-08-25-CUDAvMLX深度对比-架构生态性能选型.md) | 同日姊妹篇——那边"选哪边"，这边"怎么学" |
| [jetson-orin-platform skill](skill:jetson-orin-platform) | 本机实践——TensorRT 部署对应模块 3/6/8 |
| [LLM 推理 KVCache 全景](2026-08-21-LLM推理KVCache全景-原理管理与修改利用.md) | 模块 4 KV cache 优化的展开版 |
| [serving-llms-vllm skill](skill:serving-llms-vllm) | 模块 8 生产推理的实操版 |
| [为什么 AI 越强越需要提升个人能力（忆流）](2026-08-25-为什么AI越强越需要提升个人能力-忆流与可审计成长轨迹.md) | 模块 9 AI 写内核 = 判断归属框架的 GPU 版 |
| [大模型评测三部曲](2026-08-25-大模型评测终极指南三部曲-当尺子变成靶子与评测的评测.md) | KernelBench = 内核领域的 benchmark——Sakana 刷榜争议正是 Goodhart 实例 |

---

## 六、拓展应用推荐

1. **Jetson 优化按模块 6 补课**：Nsight Roofline 分析 + CUDA Graphs（小内核 5x）——本机 TensorRT 管线的下一步优化方向
2. **KV Cache 优化对应 LuxTTS**：模块 4 的 MLA 低秩压缩思路可用于本地 TTS 推理显存优化
3. **Tier 1 清单当 screening**：PMPP 第 5 版 + FA 三部曲 + Orca 论文——本机 GPU 工程的核心阅读清单
4. **KernelBench 关注**：AI 写内核的评测标准——与评测三部曲的"benchmark 审计"视角结合

---

## 七、指南分析

**质量**：★★★★★——11 模块 × 3 Tier 的结构化程度罕见；资源筛选严格（一手来源+实践验证）；LLM 生成内核独立成章显示前沿敏感度；连"怎么读"都给了明确方法（横切 Tier）。
**局限**：纯索引无代码（作者诚实声明）；Tier 3 部分资源极新（2025 arXiv），稳定性待观察；AMD/TPU 侧深度明显弱于 NVIDIA 侧。

**与导流帖的关系**：公众号只给了 11 个模块标题（500 字），实质内容全在 GitHub README——按"分析补充"指令已深挖原仓库补全。

## 相关笔记

- [2026-08-01-本地模型部署-消费级GPU推理.md](./2026-08-01-本地模型部署-消费级GPU推理.md) — 消费级 GPU 推理（Tier 1 实战对接）
- [2026-08-01-KVarN-KV-Cache量化后端.md](./2026-08-01-KVarN-KV-Cache量化后端.md) — KVarN 量化后端（Tier 3 量化深入）