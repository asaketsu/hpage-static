# RTC (Real-Time Chunking) — VLA 实时推理的异步执行框架
> 探索日期 2026-08-26 | 兴趣等级 L3 | 来源 5 篇 | 前序：π0.5 笔记(2026-08-11)、FLOWER VLA(2026-07-13)

## 摘要
Physical Intelligence 发布、NeurIPS 2025 录用的 RTC（arXiv 2506.07339）是一个纯推理时算法：让 π0/π0.5/SmolVLA 这类高延迟 flow-matching VLA 在 50Hz 控制频率下输出平滑连续动作。核心是把异步 action chunking 表述为 inpainting 问题——机器人执行上一个 chunk 的同时后台生成下一个 chunk，冻结必然执行的前缀动作，"补全"剩余部分。无需重训练，即插即用。

## 关键发现
1. **延迟是 VLA 落地的第一物理约束**：π0（3B）在 RTX 4090 上仅 KV cache prefill 就要 46ms，而 50Hz 控制周期仅 20ms；远程推理再加 13ms+ 网络延迟。同步推理 = 每个 chunk 边界停顿 + OOD jerk（训练分布外动力学）。
2. **RTC = 异步执行 + inpainting 一致性**：基于 pseudoinverse guidance（ΠGDM）在去噪每步加梯度引导项，强制新 chunk 与已执行前缀对齐；soft masking（指数衰减权重 1→0）覆盖全部 H−s 重叠步而非仅 d 步前缀；guidance weight clipping β=5 防止少步去噪（n=5）下发散——这三件套缺一不可（消融验证）。
3. **实验证据**：Kinetix 12 个高动态任务（投掷/接取/平衡）中 RTC 全面胜出 temporal ensembling 和 bidirectional decoding（BID），且延迟越大优势越大；真机 π0.5 双臂 6 任务（点蜡烛、插网线、叠衣）在 d≈6/11/16 注入延迟下保持高成功率，吞吐量显著提升。BID 需要 64 个采样 batch，RTC 计算量远低。
4. **演进：Training-Time RTC**（arXiv 2512.05964）：推理时 inpainting 需每步反传 vector-Jacobian product，有开销；改在训练时模拟推理延迟、直接 condition on action prefix，零推理开销，π0.6 上装箱/做咖啡任务性能持平且更便宜，高延迟场景反超。
5. **生态可用性**：LeRobot 已内置（`lerobot-rollout --inference.type=rtc`）；Intel Open Edge Platform 提供 Pi0.5+RTC OpenVINO 端侧管线（MuJoCo 验证→ALOHA 真机部署）。

## 核心概念
```
时间线（H=50, s=25, d=6, Δt=20ms）:
t=0    观测 o_t → 后台开始推理（约 97ms）
t=0..6 继续执行上一 chunk 的重叠动作（frozen prefix, W=1）
t=6    新 chunk 就绪：前 6 步冻结=旧值，6..H-s 指数衰减权重，
       H-s..H 权重 0（自由生成）→ 无缝切换，无停顿无跳变
```
ΠGDM 引导项（每个去噪步）：v' = v + min(β, (1−τ)/(τ·r²)) · (Y − Â)ᵀ diag(W) ∂Â/∂Aᵗ——本质是把"与已执行动作保持一致"变成可微软约束。

关键超参（LeRobot 实测）：execution_horizon 8–12 步；max_guidance_weight 10.0（10 步 flow matching）；prefix_attention_schedule 用 EXP 衰减。

## 对工作的价值
- 与 embodied-ai-control skill 的大脑-小脑分离设计互补：RTC 不改架构、不加 System 1 小模型，纯执行层技巧，Jetson 边缘部署 VLA 时可直接套用（4090 级延迟数据是现成参考）。
- "异步生成 + 冻结前缀 + 软约束补全"是通用模式：适用于任何"生成慢于消费"的流式场景（如 TTS 流式合成、Agent 工具调用的 action pipeline）。

## 行动建议
1. P1：为 embodied-ai-control skill 补充 RTC 小节（π0.5 部署执行层参考 + LeRobot 命令 + 超参表）。
2. P2：若做 Jetson VLA 实验，优先 LeRobot RTC 而非自研异步逻辑；注意 RTC 相对 baseline 增加约 21ms 模型耗时（97 vs 76ms）。

## 关键风险与盲点
- RTC 有计算开销（vector-Jacobian product 每去噪步一次反传），边缘设备上可能得不偿失——training-time RTC 是替代路线（官方验证）。
- 位置控制机器人上同步推理本可用，RTC 收益主要在吞吐和延迟鲁棒性；力控场景（Kinetix 类）才是刚需（官方论文）。
- SmolVLA 的 async 算法不解 chunk 间不连续问题，不能等同 RTC（社区对比已确认）。

## 一页速查
> RTC = 异步 chunk 推理 + ΠGDM inpainting + soft mask + β clipping。冻结 d 步前缀，补全 H−s 剩余。免训练、即插即用，LeRobot 一行启用。延迟越大越能打，BID/TE 全面下风。下一代：training-time action conditioning 零开销。

## 待深入
- Training-Time RTC 的延迟分布模拟如何选（论文 VI 节承认需按预期延迟调参）
- A2C2 / VLASH 两个并发工作的 correction head 路线对比

## 来源
1. arXiv 2506.07339 (NeurIPS 2025) — Real-Time Execution of Action Chunking Flow Policies
2. LeRobot 官方文档 — Real-Time Chunking (RTC)
3. arXiv 2512.05964 — Training-Time Action Conditioning for Efficient RTC
4. Intel Open Edge Platform — Pi0.5 with RTC (OpenVINO)
5. NeurIPS 2025 Poster 117747 + Medium 解读


## 相关笔记

- [FLOWER-VLA高效Flow-Matching机器人策略](../2026-07-13-FLOWER-VLA高效Flow-Matching机器人策略.md) — 前序：RTC 所加速的 flow-matching VLA 一族
- [Jetson-PI端侧VLA实时控制8.66倍加速](../2026-07-24-Jetson-PI端侧VLA实时控制8.66倍加速.md) — π0.5 端侧实时控制，同一延迟战场
- [VLA视觉语言动作模型2026进展](../2026-06-18-VLA视觉语言动作模型2026进展.md) — VLA 系列总览，RTC 属其推理部署分支
