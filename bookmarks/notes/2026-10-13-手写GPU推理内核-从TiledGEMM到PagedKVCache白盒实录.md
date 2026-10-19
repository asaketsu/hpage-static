# 手写GPU推理内核全景：从Tiled GEMM到Paged KV Cache的白盒引擎实录

> **来源**：微信公众号【程序猿编码】
> **原文链接**：https://mp.weixin.qq.com/s/gOQdQ9KGzqF6P7GsGFGASw
> **记录日期**：2026-10-13

**标签**：#CUDA #推理优化 #算子融合 #量化 #FlashAttention

---

## 一、内容详细整理

### 1.1 核心命题：白盒推理引擎——不依赖 PyTorch/TensorRT 的完整手写栈

一个专为 Transformer 推理设计的轻量引擎，全部底层算子手写 CUDA：GEMM/Softmax/Flash Attention/INT8 量化/Paged KV Cache。设计哲学=白盒化与极致掌控——精确控制 Shared Memory Bank Conflict、L1/L2 命中率、指令流水线重叠、算子间数据流转。

**四层架构**：

```
[Bindings (Python/pybind11)]
        ↓
[Engine (Model Assembly, KV Cache, Sampler)]
        ↓
[Layers (Linear, LayerNorm, Embedding, Attention)]
        ↓
[Kernels (GEMM, Softmax, Flash Attention, Quantize)]
        ↓
[Hardware (A100/Ampere)]
```

### 1.2 五个核心算子实现

**① Tiled GEMM + Bank Conflict 消除**
大矩阵划成 TILE_SIZE 小块，A/B 块载入 Shared Memory 后乘加。关键技巧是 Padding：`__shared__ float As[TILE_SIZE][TILE_SIZE + 1]` ——第二维 +1 使行起始地址偏移 TILE_SIZE+1 个元素，与 32 Bank 互质，打破 Bank 映射冲突。实测 **10%~20% 性能提升**。

**② Fused LayerNorm + Linear**
标准流程：LayerNorm 写回 HBM → Linear 再读——中间结果白走两次显存。融合后：Warp 归约（block_reduce_sum）算 mean/var → 归一化结果**只存 Shared Memory** → Linear 直接从 smem 读做投影 → 结果一次写 HBM。`__restrict__` 提示无指针别名，助编译器激进调度。

**③ Online Softmax（单遍历）**
标准 3-pass（求 max→求 exp 和→归一化）压成 1-pass：维护运行时 `m_new = max(m_old, x_i)`、`d_new = d_old * exp(m_old - m_new) + exp(x_i - m_new)`。跨线程归约用 `__shfl_down_sync`。是 Flash Attention 的关键前提。实测 **2.9~3.0x 加速**（与理论 3 倍 HBM 访问减少吻合）。

**④ INT8 量化 GEMM（dp4a 指令）**
`x_q = round(x/scale) + zero_point`；权重静态量化+激活动态量化。4 个 INT8 打包进 1 个 INT32 寄存器，`__dp4a` 单周期完成 4 对 INT8 乘加（FP32 吞吐的 4 倍+）。INT8 端到端 **3.8x 加速**（vs FP32），显存减半。

**⑤ Paged KV Cache**
KV Cache 划固定大小物理块（如 16 token/块），Page Table 记录逻辑块→物理块映射。三大收益：免预分配最大长度连续显存/支持动态 Batch 不同长度/布局紧凑提升 L2 命中率。

### 1.3 关键 Benchmark（A100 80GB SXM4，100 次均值）

- **GEMM vs cuBLAS**：512/1024/4096 方阵达到 **79%/81%/80% Peak TFLOPS**（手写实现逼近工业库）
- **Flash Attention**（seq=2048, d=64）：内存 **8.59GB→384MB（22x 减少）**，延迟 18.4→6.1ms（3.0x）
- **GPT-2 124M 生成速度**：FP32 312 / FP16 641 / **INT8 1180 tok/s**
- **vs TensorRT**（batch=1, seq=512）：该引擎 INT8 1180 ≈ TensorRT FP16 1190（打平！）；TensorRT INT8 2340 仍领先 ~2x（差距来自图级融合+自动调优）

### 1.4 Roadmap 与 FP8 展望

已规划：Flash Attention v2（warp 级任务划分）/LLaMA-3 支持/多 GPU 张量并行/CUTLASS 对比/**FP8**（H100：`__nv_fp8_e4m3` 权重 + `__hmma_fp8` Tensor Core 替换 dp4a，量化数学不变）。FP8 对 LLM 激活值动态范围更友好——专门治 INT8 的离群值精度损失。

## 二、查询拓展

### 2.1 dp4a 指令
Ampere 及之前架构的 INT8 点积指令（dot product of 4×int8 accumulate），一条指令算 4 对 INT8 乘加。A100 上 INT8 密集算力 624 TOPS vs FP32 19.5 TFLOPS（32x），但 dp4a 是 CUDA Core 路线非 Tensor Core 路线；Hopper 起改用 Tensor Core 的 FP8/INT8 MMA 指令拿满吞吐。

### 2.2 Flash Attention 内存复杂度
Naive attention 显式物化 N×N 注意力矩阵（O(N²) 显存）；Flash Attention 用 online softmax 分块计算，从不物化完整矩阵，显存 O(N)。22x 内存减少正是 seq=2048 时的实测体现。v1（2022 Tri Dao）→v2（warp 并行度优化，~2x）→v3（Hopper WGMMA+异步）。

### 2.3 cuBLAS 80% 的含金量
工业 GEMM 库（CUTLASS/cuBLAS）靠软件流水（double buffering）+Tensor Core 指令（mma.sync）+自动调优拿满峰值。手写 FP32 CUDA Core 版本能到 80% 说明分块+Padding 的基本功到位；再往上必须上 Tensor Core——这正是文中"CUTLASS 对比"Roadmap 项的潜台词。

## 三、归纳总结

### 3.1 白盒引擎性能阶梯（GPT-2 124M, tok/s）

```
PyTorch eager FP32  198  (0.17x TensorRT FP16)  ← 黑盒基线
该引擎 FP32         312  (0.26x)                ← 手写 Kernel +1.6x
该引擎 FP16         641  (0.54x)                ← 半精度 +2.1x
该引擎 INT8        1180  (~1.0x)                ← dp4a 量化 +1.8x = 打平 TensorRT FP16
TensorRT INT8      2340  (1.97x)                ← 工业天花板(图融合+auto-tune)
```

### 3.2 优化技术层级（每层独立收益可叠加）

- **内存布局层**：Bank Conflict Padding（+10-20%）
- **访存消除层**：算子融合（消中间 HBM 往返）/Online 算法（3 遍→1 遍，3x）
- **算法复杂度层**：Flash Attention（O(N²)→O(N) 显存，22x）
- **数值精度层**：INT8/dp4a（3.8x）
- **系统调度层**：Paged KV Cache（内存碎片→动态 Batch 可行）

### 3.3 与 TensorRT 剩余 2x 差距的归因

图级算子融合（编译期把更多层合并）+ 自动调优（按硬件选 Kernel 参数）——两者都是**编译器工程**而非 Kernel 工程，印证了推理优化的最后一公里在图编译层。

## 四、趋势判断

### 趋势1：INT8 已是 Ampere 世代性价比顶点，FP8 是 Hopper 世代标配
依据：文章实测 INT8=3.8x；而 FP8 迁移路径已被明确规划（e4m3+Tensor Core），量化数学不变只换指令——精度格式迭代快于算法迭代。

### 趋势2：手写引擎的价值在"可控性"而非"超越工业库"
依据：作者定位明确（学习/原型/实验平台），性能目标=逼近而非超越；真正领先 TensorRT 的项目（llama.cpp/vLLM）靠的是开放生态+持续调优，不是单人 Kernel 功力。

### 趋势3：Paged KV Cache 从创新变标配
依据：文中作为核心卖点之一的分页 KV，与 vLLM 的 PagedAttention 同构——2023 论文到 2026 教学项目标配，说明该技术已完成从前沿到常识的沉淀。

### 趋势4：GPU 底层优化知识正在"教程化扩散"
依据：此类公众号长文（含完整代码结构+Benchmark 方法论）把原属大厂 infra 团队的知识平民化；配合开源参考实现，中小团队也能做定制推理后端。

## 五、关联分析

### 5.1 与 edge-llm-quantization / tts-deployment 的关联
我们的 Jetson 边缘 LLM 部署线（GGUF 量化/TensorRT）用的正是本文的手写栈下游产品——TensorRT-LLM 的 INT8/FP8 路线与本文 Roadmap 完全同构。本文补上了"TensorRT 里到底发生了什么"的白盒认知。

### 5.2 与 llm-inference-optimization 技能的关联
该技能的 PagedAttention/量化/推测解码/连续批处理四大主题，本文全部覆盖其底层实现（Paged KV/INT8 dp4a/Online Softmax）——可作为技能 references 的案例补强素材。

### 5.3 与 Jetson 部署实践的关联
Jetson Orin 是 Ampere 类 SM 架构（compute 8.7），dp4a 路线适用；我们 edge 端 LuxTTS/量化推理的下一步（INT8 化）可直接参考本文量化公式与打包策略。

### 5.4 与今日 LLM 优化数学谱系笔记的关联
今晨笔记《LLM不在猜测而在优化——从牛顿法到万亿参数的数学谱系》讲优化算法的数学统一性；本文是其工程镜像——每一条数学优化（online softmax 的递推）都对应一次 HBM 访存消除。数学谱系+访存谱系是同一枚硬币两面。

## 六、金句摘录

> 「选择自己手写推理引擎，并非为了重新发明轮子，而是为了深入理解轮子的转动原理。」— 白盒化的学习价值定位。

> 「计算能力往往不是唯一的瓶颈，内存带宽和延迟才是决定推理性能的关键。」— 推理优化的第一性原理。

> 「TILE_SIZE + 1 与 32 互质，这打破了原有的 Bank 映射规律。」— 一行注释 +1 换 10-20% 性能。

## 七、行动启示

- **Jetson 实践**：Orin（SM 8.7）dp4a 可用，edge LLM INT8 化可走本文路线——先做量化感知的 Profile（Nsight Compute 看 Tensor Core 利用率）再动手
- **教学素材**：五个算子+四层架构+Benchmark 方法论是完整课程骨架，可作为 edge-llm-quantization skill 的案例库
- **对标方法**：所有优化用"vs cuBLAS %Peak / vs TensorRT 倍数"双基准——我们的 Benchmark 报告应学习这种工业对标格式
- **警惕点**：文末"完整源码加微信"——这是引流付费项目，核心代码结构真实但获取有门槛；原理层面已全在文中

## 八、拓展应用推荐

- 面试准备场景：五个算子（GEMM Padding/融合 LN+Linear/Online Softmax/INT8 dp4a/Paged KV）是 GPU 优化面试题的标准答案集
- 边缘部署场景：Orin/NX 上做 INT8 量化推理时，dp4a 打包策略+动态激活量化公式可直接套用
- 性能调优场景：用 Nsight Compute 的 Bank Conflict 指标验证 Padding 效果——把"10-20%提升"在自己硬件上复现
- 教学课程场景：四层架构（Bindings/Engine/Layers/Kernels）是讲解推理引擎分层的最佳脚手架

## 九、指南分析

- **方法论价值**：完整的"从零造轮子"教学范本——每个优化点都有数学原理（公式）+工程手段（代码）+量化收益（Benchmark）三件套闭环
- **可复用结构**：①优化技术分层法（内存布局→访存消除→算法复杂度→数值精度→系统调度）②双基准对标法（cuBLAS %Peak + TensorRT 倍数）
- **反例警示**：与 TensorRT INT8 的 2x 差距被诚实归因（图融合+自动调优）而非掩饰——工程叙事的诚实度范本
- **判据**：判断一个"手写引擎"项目的成色——看它敢不敢和 cuBLAS/TensorRT 对标并公布差距；只讲原理不给数字的都是纸面项目
