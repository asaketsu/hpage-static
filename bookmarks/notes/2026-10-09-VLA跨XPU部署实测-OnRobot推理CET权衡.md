# VLA跨XPU部署实测-OnRobot推理CET权衡

> **来源**：arXiv 2604.24447（Characterizing Vision-Language-Action Models across XPUs: Constraints and Acceleration for On-Robot Deployment，上海交大）
> **原文链接**：https://arxiv.org/abs/2604.24447
> **记录日期**：2026-10-09

**标签**：#VLA #机器人基础模型 #边缘部署 #JetsonOrin #CET权衡 #推理加速 #DualSystem架构

---

## 一、内容整理

### 1.1 核心问题：VLA 模型部署在哪种 XPU 上才"合身"

此前 VLA 评测几乎全在 RTX 4090 上做，掩盖了边缘加速器（GPU/NPU/XPU）的真实权衡。本文对 π0/SmolVLA/Gr00t/OpenVLA/Diffusion Policy 做**模型-硬件协同刻画**，横跨 6 平台：RTX 4090、Jetson Thor、AGX Orin、Ascend 310B/310P、Intel B60 Pro、i7-11700 CPU。用 **CET 三维**（Cost 成本 / Energy 能耗 / Time 延迟）替代单一延迟指标做排行榜。

### 1.2 π0 六平台实测榜（LIBERO 86 分固定）

| 硬件 | 显存 | 带宽 | 成本$ | 能耗kJ | 延迟ms |
|---|---|---|---|---|---|
| RTX 4090 | 24GB | 1000GB/s | 3500 | 2.398 | **102.3** |
| Jetson Thor | 128GB | 273GB/s | 3400 | **1.282** | 246.0 |
| AGX Orin | 64GB | 204GB/s | 1999 | 1.866 | 920.6 |
| Intel B60 Pro | 24GB | 456GB/s | **599** | 6.363 | 306.5 |
| Ascend 310P | 48GB | 204.8GB/s | 1030 | 2.618 | 818.0 |

- **延迟优先**（动态任务）→ 4090 最快，Thor 备选
- **成本优先**（规模化部署）→ B60 Pro 最便宜，310P 备选
- **能耗优先**（电池机器人）→ **Thor 第一，AGX Orin 第二**——这个结论对我们 Jetson 系边缘机器人选型直接可用

### 1.3 Finding #1：模型大小不能预测推理频率（反直觉）

Diffusion Policy（小模型）推理频率**低于** π0（大模型）——因为 Small Consumer 要跑 **100 步串行去噪**，而 π0 的 Action Expert 只需 4 步 flow matching。**迭代步数 > 参数量**，是延迟的第一决定因素。

### 1.4 Finding #3：双相位计算失衡（最重要的系统洞察）

Nsight Systems 剖析 π0 三阶段（vision / VLM backbone / Action Expert）：

- **VLM backbone**：SM 利用率 >90%，compute-bound，但延迟占比小
- **Action Expert**：SM 利用率仅 20-40%，**memory-bound**，却占 2× 于 VLM 的延迟
- Roofline 分界：4090 ridge point = 330 FLOPs/Byte；Action Expert 的算术强度远低于此 → 带宽受限

推论：单一平台很难同时喂饱两个相位——旗舰卡在 Action Expert 相位大量空转，这解释了"峰值吞吐规格 ≠ 实测控制频率"的落差。**与 EdgeReasoning 的 decode 带宽墙同构：机器人控制的最后一公里都是带宽问题**。

### 1.5 两个免训练加速方法

- **DP-Cache**：缓存迭代去噪过程中跨步不变的中间特征，π0@4090 提速 1.29×，成功率仅掉 0.6%（62.6%→62.0%）
- **V-AEFusion**：VLM 与 Action Expert 异步流水线并行，掩盖低利用率相位延迟
- 组合效果：GPU 上最高 **2.9×**、边缘 NPU 上最高 **6×**，任务成功率仅边际退化

### 1.6 硬件规格速查（附录 A.1）

| 硬件 | BF16/FP16 | 显存 | 带宽 |
|---|---|---|---|
| Ascend 310B | 10 TFLOPS | 12GB | 51.2GB/s |
| Ascend 310P | 88 TFLOPS | 48GB | 204.8GB/s |
| Intel B60 Pro | 90 TFLOPS | 24GB | 456GB/s |
| AGX Orin | 42 TFLOPS | 64GB | 204GB/s |
| RTX 4090 | 330 TFLOPS | 24GB | 1000GB/s |
| Jetson Thor | 258 TFLOPS | 128GB | 273GB/s |

真机 Franka 臂验证：约 5Hz 可行平台（4090/Thor/B60）中 **Thor 端到端能效最优**，4090 任务完成时间最短。

## 二、查询拓展

### 2.1 与 EdgeReasoning（Orin 上 LLM 推理刻画）的互补关系
两篇构成"边缘机器人推理"姊妹篇：EdgeReasoning 管 LLM 推理模型（decode 带宽墙、20× 延迟代价），本文管 VLA 策略模型（双相位失衡、CET 选型）。共同结论：**边缘瓶颈是内存带宽不是算力峰值**——Orin 204GB/s vs 4090 1000GB/s 的 5 倍差距，直接映射到 Action Expert 相位的延迟惩罚（102→920ms）。

### 2.2 双系统架构趋势确认
领域正从单体自回归动作 token 转向双系统管线（Hi-robot/π0/Gr00t）：高频控制与低频感知推理解耦。这与 DUCK 的"分层决策（策略网络 20Hz + 未来上位规划）"及 Agent 决策层升级路径（logprobs→决策契约化）同构。

### 2.3 加速方法四族谱系（可当检索地图）
冗余削减（Cache-VLA/Deer/SparseVLM）/ 架构压缩蒸馏（RoboMamba/TinyVLA/一致性模型）/ 推测推理（Spec-VLA/TS-DP）/ 系统流水线（Real-Time Chunking/SmolVLA）。选型先看瓶颈相位再选族。

## 三、归纳总结

### 3.1 部署选型三步法（论文给出的可复用流程）

```
① 选模型 → 查 leaderboard 拿全平台剖析
② 可行性过滤 → VRAM 硬约束（装不下直接淘汰）+ 控制频率门槛
③ 按场景排序 → 延迟优先/成本优先/能耗优先三档不同答案
```

### 3.2 三个反直觉发现

- **小模型更慢**：100 步去噪的 Diffusion Policy 比 3B+ 的 π0 慢——迭代结构 > 参数规模
- **旗舰卡不是默认答案**：CET 联合排序下 4090 只在 π0+延迟优先场景胜出；SmolVLA 的 CET 最优解是 Thor
- **7B OpenVLA 塞 CPU 会跌破 1Hz**：swap 内存盘 IO 停摆——VRAM 是硬可行性约束不是软偏好

### 3.3 对我们 Jetson 线的定位

- AGX Orin 跑 π0 要 920ms/步（约 1Hz）→ **当前 Orin 只够跑 Small Consumer（SmolVLA 级）或自训 MLP 策略**
- Thor 是 VLA 时代的目标硬件（273GB/s 带宽 + 128GB 显存 + 能效第一），预算允许时的升级路径
- B60 Pro（599$）是成本敏感批量的黑马，但生态成熟度需验证

## 四、趋势判断

### 趋势1：VLA 部署评测从"延迟单指标"转向 CET 三维
依据：电池机器人（人形已降到 $10k 级）的成本/能耗约束与延迟同为一级指标；论文 leaderboard 已开源可交互。

### 趋势2：双相位失衡将催生"异构配对"硬件设计
依据：compute-bound VLM + memory-bound Action Expert 串行，单芯片两头不讨好；V-AEFusion 式流水线是软件补丁，硬件侧异构配对（大小核/NPU+DRAM 旁路）是下一步。

### 趋势3：边缘 VLA 加速进入"免训练"时代
依据：DP-Cache/V-AEFusion 均不改权重，NPU 上 6× 加速对部署侧零门槛——与 LLM 侧 PagedAttention/推测解码的"系统工程红利"路径一致。

### 趋势4：right-sized 边缘设备经济性反转旗舰卡
依据：Thor 能效最优 + B60 成本最优 + 4090 仅赢绝对延迟；当控制频率门槛（5Hz）满足后，多付 6 倍电费买不回边际收益。

## 五、关联分析

### 5.1 与本机环境的关联
- jbot = AGX Orin：π0 级 VLA 在本机 920ms/步不可用（<2Hz）；**本机现实选项 = SmolVLA 级小 VLA 或继续 MLP 策略 + 规则层**。若做 VLA 实验须借 Thor 级设备或云端推理
- luxtts/nexa-local-inference 与 VLA 抢 64GB 统一内存，部署前须做内存预算表（VRAM 硬约束先行的三步法直接适用）

### 5.2 与既有笔记/技能的关联
- [EdgeReasoning边缘推理实测](./2026-10-08-EdgeReasoning边缘推理实测-JetsonOrin推理模型部署刻画.md)：姊妹篇，LLM 与 VLA 两半拼齐"边缘推理全景"
- [MiniCPM-Robot-1.5B-VLA开源](./2026-10-07-MiniCPM-Robot-1.5B-VLA开源.md)：1.5B VLA 属 Small Consumer，本文给出其在 Orin 上的可行性判断框架
- [LocoFormer通用运动模型](./2026-10-08-LocoFormer通用运动模型-长上下文跨试次适应.md)：策略模型侧的前沿，本文是部署侧的约束
- edge-llm-quantization / jetson-tensorrt-deploy skill：Orin 204GB/s 带宽墙条目应补充进硬件清单

### 5.3 与 DUCK 项目的关联
DUCK 20Hz 控制循环 = 50ms/步预算，π0@Orin 的 920ms 差 18 倍——**证实当前"小 MLP 策略 + 分层架构"路线在 Orin 上是唯一可行解**；若未来上 VLA 决策层，只能放低频环（1Hz 规划→高频 MLP 执行），恰是双系统架构的分工方式。

## 六、金句摘录

> 「"Right-sized" edge devices can be more cost-/energy-efficient than flagship GPUs while meeting control-rate constraints.」——合身比旗舰重要

> 「A compute-bound VLM backbone followed by a memory-bound Action Expert.」——机器人推理的最后一公里是带宽，不是算力

## 七、行动启示

- **edge-llm-quantization skill 增补**：六平台带宽/算力规格表 + "迭代步数>参数量决定延迟"条目
- **DUCK 上位机预算表**：把 CET 三步法写进未来 VLA 选型评审——先 VRAM 过滤再频率门槛最后能耗排序
- **本机 VLA 实验**：MiniCPM-Robot 1.5B 若上 jbot，先测 Action Expert 段延迟（本文证明它是隐藏瓶颈）

## 八、拓展应用推荐

1. **Hermes 边缘推理路由**：交互任务路由 1.5B 级、夜间批量路由 8B+ 的既有结论，可加 VLA 段（Orin 只接 Small Consumer）
2. **机器人选购决策卡**：Thor（能耗优先）/B60（成本优先）/4090（延迟优先）三档写进 robotics-bom-selection skill 的主控选型维度
3. **DP-Cache 思路迁移**：DUCK 的 MPC/滚动优化若有迭代结构，跨步不变量缓存是同款免训练加速

## 九、指南分析

**方法论价值**：模型-硬件协同刻画 + roofline 定位瓶颈相位 + 免训练优化闭环——"先剖析再优化"的教科书示范，避免在错误的相位上烧优化预算。

**可复用的实验设计**：
- 控制变量法拆相位（vision/VLM/ActionExpert 分别计时+利用率）——任何端侧管线性能分析都可套用
- 能耗用物理功率计实测而非 TDP 估算——CET 排行榜的可信度基础

**局限与保留**：π0 系为主，Gr00t/SmolVLA 数据在 leaderboard 网站但论文正文覆盖浅；Ascend 生态（torch.npu）成熟度与复现成本未讨论；LIBERO 仿真成功率≠真机成功率；Thor 的 BF16 算力是 INT8 TOPS 减半估算值非官方规格。

## 相关笔记

- [EdgeReasoning边缘推理实测-JetsonOrin推理模型部署刻画](./2026-10-08-EdgeReasoning边缘推理实测-JetsonOrin推理模型部署刻画.md) — LLM 侧姊妹篇，共同拼齐边缘推理带宽墙
- [MiniCPM-Robot 1.5B VLA 开源](./2026-10-07-MiniCPM-Robot-1.5B-VLA开源.md) — Small Consumer 级 VLA 实例
- [LocoFormer通用运动模型-长上下文跨试次适应](./2026-10-08-LocoFormer通用运动模型-长上下文跨试次适应.md) — 策略模型侧前沿对照
- [HuggingFace详细教程-从调用模型到微调与部署](./2026-10-07-HuggingFace详细教程-从调用模型到微调与部署.md) — 部署管线上游
