# 手写 PTX Tensor-Core GEMM 内核：NVIDIA L4 多精度研究

> **来源**：arXiv 2608.10103（X @vintcessun / 恒星sun 推文荐读）
> **原文链接**：https://arxiv.org/html/2608.10103v1
> **作者**：MattJBorowski1991（开源 artifact：github.com/MattJBorowski1991/TensorCorePTX）
> **记录日期**：2026-08-15

**标签**：#GPU优化 #PTX #TensorCore #量化 #LLM推理 #GEMM

---

## 一、内容整理

### 1.1 核心问题：什么时候值得从 WMMA 下沉到手写 PTX？

Tensor Core 有两级访问接口：
- **WMMA C++ API**（高层）：方便可移植，但固定 fragment 形状、加载模式、累加器布局，隐藏底层指令流
- **PTX 路径**（低层）：`cp.async`（全局→共享异步拷贝）+ `ldmatrix`（协作式共享→寄存器加载）+ `mma.sync`（矩阵乘本体）——程序员直接控制 tile 形状、流水深度、寄存器映射，代价是复杂度剧增

**流行假设是"手写 PTX 必然更快"。本文用受控单 GPU 实验证明：这个假设只在特定精度和规模下成立。**

### 1.2 实验设计（方法论亮点）

- 平台：NVIDIA L4（Ada 架构 SM89，72W 推理卡，FP16 TC 242 TFLOPS / INT8 TC 485 TOPS）
- 全部内核共享同一分块配置（WMMA_M=N=16、4×2 warp-tile、8 warps/block），**一次只改一个维度**（加载路径/mma形状/累加器类型/流水深度）——保证每个加速都能归因到具体机制
- 规模扫描 N=512→8192 方阵，Nsight Compute `--set full` 全指标剖析
- 四组实验：Run1 FP16 族 / Run2 INT8 族 / Run3 INT4 基础 / Run4 最优 INT4 k64 消融

### 1.3 结果总表

| 精度 | PTX vs 同精度 WMMA | 机制 | 最优内核 |
|------|-------------------|------|---------|
| FP16 | **1.0×（无收益）** | 指令级增益被操作数打包开销抵消 | fp16_wmma（基线即最优） |
| INT8 | **1.4×–1.8×** | 指令数减少 25–43% + 全局访存合并近乎完美（浪费 sector 仅 0.4%） | int8_ptx_mma_k32 |
| INT4 | **2.9×–4.3×** | 原生 `mma.sync.m16n8k64.s4` 绕过 WMMA 的软件模拟展开 | k64（大 N）/ 3stage（小 N） |

**相对 FP16 WMMA 基线的端到端加速（N=8192）：INT8 最优 34.4×，INT4 最优 98.7×。**

### 1.4 Run 1 — FP16：PTX 打不过编译器

- 6 个 FP16 内核，所有规模下手写 PTX 均不快于编译器优化过的 WMMA，差距 ±5% 以内
- 计算受限段（N≤4096）所有内核都跑出 1280–1500 GFLOPS；manual_pack 虽然 SM 吞吐最高（~57%）但打包开销最大（N=512 慢 22%）
- N=8192 时 ~537MB 工作集溢出 L2，全部内核卡死在 DRAM：L1/TEX 吞吐从 ~90% 崩到 ~38%，GFLOPS 减半，所有差异缩到 1% 以内——**带宽成为唯一瓶颈，指令组合变得无关紧要**
- 反直觉发现：FP16 累加器变体把占用率提到 70–82%（其他 56–66%），**GFLOPS 却不涨**——占用率不缺 warp 时不是吞吐的驱动因素

### 1.5 Run 2 — INT8：k32 靠指令数和合并访存赢

- int8_ptx_mma_k32 全规模最快（N=512 快 23% → N=8192 快 43%）
- 机制：把每个 K=32 tile 分解为两个紧致展开的 m16n8k16 MMA，指令数比 WMMA 少 25–43%；全局加载合并近乎完美——N=8192 只浪费 0.4% sector（其他内核约 50%）
- N=8192 时 **DRAM Active Cycles 与墙钟时间几乎 1:1 对应**：k32 记录 1.57B DRAM 活跃周期 vs WMMA 2.80B（-43.9%，正好对应 -43% 提速）——最清晰的证据：大 N 是 DRAM 延迟受限，排名由合并质量决定
- 反例对照：k16 中小规模反而慢于 WMMA（未合并加载每 32 字节 sector 浪费 31 字节）；3stage 在 N=4096 崩 +37%（三缓冲打满 MIO 队列）；dp4a 纯标量路径慢 4.8×（指令数多几倍且完全不用 Tensor Core）
- 占用率再次证伪：int8_wmma 占用率全规模最高，却稳定输给寄存器受限的 k32

### 1.6 Run 3 — INT4：原生 MMA 碾压 WMMA 软件模拟（最大收益）

- 根因：WMMA 的 INT4 路径（`wmma::experimental::precision::s4`）是**软件展开模拟**——指令数膨胀+重度 lane 依赖分支发散
- N=8192 时 int4_wmma 每 warp 只有 **16.89 个活跃线程** + **461 万条发散分支**；原生 PTX 内核满 32 线程/warp + **零发散**，每调度器指令数少 6–7×
- PTX 内部也有分水岭：3stage 小 N 最快（预取重叠深），但 N 增大后 L1 命中率崩到 14.5%（被 L2 吞吐 95.6% 主导）；k64 在 N=8192 保住 61.6% L1 命中率，N≥2048 后全程最优——**交叉点是内存层级效应，不是 Tensor Core 利用率差异**（两者用同一个 m16n8k64 MMA）

### 1.7 Run 4 — INT4 k64 消融：真正的局部最优

固定 m16n8k64 策略扫三个旋钮：A 加载器分片（x1/x2/x4 ldmatrix）、缓存驱逐策略（.ca vs .cg）、B 操作数布局（转置 vs 非转置）。

- 选定配置（x4 A + x2 B + 非转置 + .ca）确实坐在局部最优盆地里，非转置 .ca 变体只差几个百分点
- **转置 B 变体灾难性崩溃**：每 32 字节 sector 只用上 ~2.2 字节，每调度器可执行 warp 从 0.57 掉到 0.20，大 N 慢 3.1×——再次确认**合并访存质量（而非 MMA 算术）统治这个内核族**
- .cg 策略把流量从 L1 推给 L2（命中 64%→20%），温和但一致的延迟退化

## 二、查询拓展

### 2.1 WMMA vs mma.sync 的指令层级
WMMA 是 CUDA C++ 的 `nvcuda::wmma` 命名空间，m16n16k16 固定形状，fragment 对程序员不透明；PTX 的 `mma.sync.aligned` 暴露 m16n8k16/m16n8k64 等原生形状，`ldmatrix` 按 lane 协作加载寄存器 fragment。WMMA 缺 INT4 原生支持（experimental 的 s4 是模拟），这是本文 INT4 巨大差距的根源。

### 2.2 cp.async 流水线
`cp.async`（Ampere 引入）16 字节全局→共享拷贝不占寄存器不阻塞发射 warp；`commit_group`/`wait_group` 括住飞行中的拷贝。双缓冲=一块 shared 在填、一块在算；三缓冲（wait_group 1）多一块在途换更长 L2 延迟隐藏，代价是 shared memory 压力。

### 2.3 L4 定位
Ada 代 72W 单槽低姿态推理卡：FP32 30.3 TFLOPS、FP16 TC 242、INT8 TC 485 TOPS、24GB/300GB/s。论文的量化收益部分来自"L4 带宽相对算力偏紧"的卡型特征——带宽越紧，量化缩小工作集逃出 DRAM 悬崖的收益越大。

### 2.4 与 NVIDIA 论坛历史疑问的呼应
NVIDIA 开发者论坛早有"INT8 WMMA 为何不比 FP16 快"的老问题（RTX 2060 实测两者同速）——本文给出了系统性答案：WMMA 层面 INT8 的理论双倍吞吐被指令流/访存掩盖，只有下沉 PTX（k32）才兑现部分差距。

## 三、归纳总结

### 3.1 决策规则（论文核心产出）

```
是否值得手写 PTX？
├─ FP16 → 不值得。编译器 WMMA lowering 已近最优，大 N 带宽受限，
│          PTX 无可回收的开销
├─ INT8 → 中等值得（1.4–1.8×）。机制性收益：更少指令+更好合并
└─ INT4 → 非常值得（2.9–4.3×）。结构性收益：绕过 WMMA 软件模拟，
           原生 m16n8k64.s4 单指令完成

统一原则：PTX 的工程复杂度，只在【它能消除 WMMA 路径无法避免的
指令开销】时才值得付出——最戏剧化的是 INT4（WMMA 在软件里模拟）
```

### 3.2 两条反直觉工程认知

- **占用率是诊断量不是优化目标**：两次实验证伪（FP16 累加器占用率 82% 不涨 GFLOPS；int8_wmma 占用率最高却稳定输给寄存器受限的 k32）
- **推理规模下真正的约束是内存不是算术**：量化收益不只来自每操作数字节减半/减四分之一，更来自工作集缩到能驻留 L2——INT4 因此逃过了把 FP16 卡死在 N=8192 的 DRAM 悬崖（INT4_wmma 的 DRAM 活跃只 0.88%，L2 命中 99.7%）

### 3.3 性能数据速查（N=8192 墙钟）

- **内核**：fp16_wmma 16500ms > int8_wmma 858ms > int4_wmma 713ms > int8_k32 480ms > int4_3stage 198ms > int4_k64 **167ms**
- **vs FP16 WMMA**：int8_k32 34.4× / int4_3stage 83.5× / int4_k64 **98.7×**

## 四、趋势判断

### 趋势1：低精度原生化是推理栈的持续方向
依据：INT4 从"WMMA 模拟"到"原生单指令"带来 4.3× 结构性收益；行业同构趋势——Blackwell 已原生 FP4/FP8 block-scaled（cuBLAS 12.9 报 FP8 vs BF16 1.5–2.2×）。
判断：未来推理卡每代新增的原生低精度格式，谁先吃到原生指令红利谁拿走数量级加速。

### 趋势2：单卡推理优化的重心从算子调优转向内存层级工程
依据：本文所有大 N 排名由合并访存质量+缓存驻留决定（转置 B 崩 3.1×、.cg 退化、DRAM cycles 与墙钟 1:1）；L4 这类带宽紧算力松的卡尤其如此。
判断：量化→L2 驻留→合并访存这条链路，比追求 Tensor Core 利用率百分比更值得投入。

### 趋势3：手工 PTX 的价值窗口收窄但不会消失
依据：FP16 上编译器已追平手写；但 WMMA 抽象层存在结构性盲区（INT4 模拟、fragment 布局不透明）。Triton/CUTLASS 等中间层持续吃掉两端。
判断：下沉 PTX 的决策将越来越像本文的判据式回答——先问"WMMA 路径有没有无法避免的开销"，再决定是否投入。

## 五、关联分析

### 5.1 与 Jetson 本地推理笔记的关联
本机 Jetson Orin Nano（8GB 统一内存、带宽 ~102GB/s）是比 L4 更极端的"带宽紧"案例。本文的结论直接映射：本地跑量化模型（GGUF Q4/Q8、TensorRT INT8/INT4）的收益不仅是算得快，更是工作集缩进缓存/统一内存带宽预算——`edge-llm-quantization`、`jetson-tensorrt-deploy` 两个 skill 的理论基础再添一实证。

### 5.2 与 LLM 推理部署实践的关联
论文明确面向"单张 L4 级卡服务量化开源模型（Llama/Mistral/Qwen/Nemotron）"。对 llama.cpp（GGUF 路线）和 TensorRT-LLM（原生低精度 MMA 路线）的分野给出了解释框架：后者走的就是本文"原生 INT4/INT8 MMA"路线，前者部分场景仍在模拟展开的等价物上消耗指令预算。

### 5.3 与 arXiv 2608.10103 的方法论关联
"一次只改一个变量 + 全指标剖析 + 机制归因"的实验设计，与自身量化回测中的 walk-forward 验证同构：不止问"快多少"，必须问"为什么快、瓶颈在哪层"。可借鉴到 `gpu-capacity-estimation` skill 的并发压测设计——把"占用率"当诊断量的思路同样适用于并发批大小调优。

## 六、金句摘录

> "PTX is worth its complexity exactly when it removes instruction overhead that the WMMA path cannot avoid."

> "Treat occupancy as a diagnostic, not a target."

> 推文版："别急着为榨性能就下沉手写 PTX：在 NVIDIA L4 上，FP16 甚至赢不了双缓冲 WMMA。"

## 七、行动启示

- **启示**：本地 Jetson 量化推理遇到瓶颈时，先查访存合并与缓存驻留（Nsight 的 DRAM Active Cycles / L1/L2 命中率），再考虑更深的流水或手写 PTX
- **行动**：把本文决策规则补进 `edge-llm-quantization` skill 的"量化方案选择"章节（INT4 原生 MMA vs 模拟的差距依据）；artifact 仓库（TensorCorePTX）留作内核参考实现
