# 五种 LLM 微调技术图解 — LoRA 家族 PEFT 变体谱系

`#LoRA` `#PEFT` `#微调` `#LLM` `#参数高效训练`

> 来源：Avi Chawla (@_avichawla) · 2026-10-19 · https://x.com/_avichawla/status/2112109554687525360
> 作者：Daily Dose of DS 联合创始人，IIT Varanasi，ex-Mastercard AI Engineer，7.9 万粉丝
> 数据：14.8k 浏览 / 348 赞 / 54 转

## 归纳总结

一篇面向实践者的 PEFT 变体速查：全参微调对 LLM（数十亿参数、数百 GB 权重）不可行，PEFT 的核心思路是**对权重矩阵做低秩适配**——找到一个仍能表达原矩阵信息的小维度矩阵。作者以 LoRA 为基线，沿三条正交演化轴展开 5 种变体：**冻结谁**（LoRA-FA 冻 A）、**共享什么**（VeRA 全层共享随机 A/B 只学缩放向量）、**动不动 W**（Delta-LoRA 用 A·B 差分喂给 W）、**怎么配学习率**（LoRA+ 给 B 更高学习率）。核心洞察：五者不是竞争关系，而是"可训练参数量 vs 表达能力 vs 收敛质量"三角的不同取舍。

## 内容整理：五种技术逐个拆解

**背景（数学铺垫）**
- LLM 权重 = 数字矩阵，微调 = 调整矩阵数值
- 多数 PEFT 技术 = 找矩阵的低秩适配（lower-rank adaptation）

**1) LoRA（基线，2021）**

| 要素 | 说明 |
|------|------|
| 结构 | 权重矩阵 W 旁挂两个低秩可训练矩阵 A、B |
| 训练对象 | 冻结 W，只更新 A、B |
| 内存 | 即使最大 LLM，LoRA 矩阵也只占几 MB |

**2) LoRA-FA（Frozen-A）**
- 痛点：LoRA 虽降了可训练参数量，但更新低秩权重仍需可观**激活内存**
- 方案：冻结矩阵 A（随机初始化后不动），只更新 B
- 收益：激活内存进一步下降

**3) VeRA（Shared-AB + 缩放向量）**
- LoRA：A、B 每层独有一份
- VeRA：A、B 冻结、随机初始化、**全层共享同一份**
- 可训练部分：每层仅学缩放向量 b 和 d（标量级参数）
- 定位：极低参数量场景（边缘/多任务微调）

**4) Delta-LoRA（W 也动）**
- 突破点：唯一让 W 参与更新的变体，但非传统全参训练
- 机制：把相邻两个训练步 A·B 乘积的**差分（delta）**加到 W 上
- 效果：W 获得低秩更新量的累积，表达能力超过纯旁路方案

**5) LoRA+（学习率差异化）**
- 洞察：LoRA 对 A、B 用同一学习率是次优的
- 方案：给矩阵 B 设更高学习率
- 效果：更好的收敛性

**谱系总览**

| 变体 | A | B | W | 可训练参数 | 独特收益 |
|------|---|---|---|-----------|---------|
| LoRA | 训 | 训 | 冻 | 低（几 MB） | 基线 |
| LoRA-FA | 冻 | 训 | 冻 | 更低 | 激活内存大降 |
| VeRA | 冻+共享 | 冻+共享 | 冻 | 极低（缩放向量） | 参数量最少 |
| Delta-LoRA | 训 | 训 | 差分更新 | 低 | W 获得表达能力 |
| LoRA+ | 训(低lr) | 训(高lr) | 冻 | 低 | 收敛更好 |

## 关联分析

- **与 [[2026-05-22-LoRA-GRPO最优配置实证-RL场景的Rank选择与超参数.md]]**：该笔记实证了 RL（GRPO）场景下 rank 选择与超参数的最优配置；本篇补上游——变体层面的选型菜单。两者合成"变体选型 → rank/超参调优"完整决策链。LoRA+ 的 B 高学习率结论可直接并入其超参搜索空间。
- **与 mlops/training 技能族（peft-fine-tuning / unsloth / fine-tuning-with-trl）**：本笔记的五变体谱系是这些工具链背后的算法菜单；unsloth 等加速框架的默认配置实质是其中若干技巧的组合（如冻结 A 近似于 LoRA-FA 思路）。
- **与 domain-llm-training-pipeline（领域 LLM 训练流水线）**：领域微调选型时可参考——显存极紧（Jetson 类边缘设备）选 VeRA/LoRA-FA；追求领域知识深度灌注（不止风格适配）可试 Delta-LoRA；默认 LoRA+ 起步。
- **低秩思想的普遍性**：与 MLA（DeepSeek KV 缓存压缩）同源——都是"高维矩阵信息可由低秩结构近似"这一线性代数事实的应用，一个用于压缩推理缓存，一个用于压缩训练更新量。

## 查询拓展

- `LoRA+ paper` — Hayou et al., LoRA+: Efficient Low Rank Adaptation of Large Models（B 学习率的理论依据）
- `VeRA paper` — Kopiczko et al., VeRA: Vector-based Random Matrix Adaptation（共享随机矩阵 + 缩放向量）
- `LoRA-FA paper` — Zhang et al., Frozen-A LoRA（激活内存分析）
- `Delta-LoRA paper` — Zi et al., Delta-LoRA: Fine-Tuning High-Rank Parameters with Delta of Low-Rank Matrices
- `DoRA / rsLoRA / QLoRA` — 谱系之外的后续变体（权重分解/秩稳定缩放/4bit 量化基座），作者未覆盖但同属一张菜单
- `low-rank adaptation survey 2025` — PEFT 全景综述，补全本篇 5 技术之外的方法

## 趋势判断

1. **PEFT 已从"省显存技巧"进化为"算法设计空间"**：五变体分别动了冻结策略/共享策略/W 更新/学习率分配四个正交旋钮，说明社区已把低秩适配当作可系统探索的设计空间而非单一 trick。
2. **参数量竞赛转向"有效参数"竞赛**：VeRA 的缩放向量路线表明，随机矩阵 + 少量可调标量的组合能逼近全 LoRA，"trainable params" 这一指标的解释力在下降。
3. **W 是否更新成为新的分水岭**：Delta-LoRA 代表一类"让基座也吃到梯度"的折中——纯旁路方案在需要灌注新知识（而非适配格式/风格）时存在天花板，这一矛盾会驱动更多混合方案。
4. **工程框架默认配置会吸收这些结论**：LoRA+ 的差分学习率这类零成本改进，预计将像 AdamW 之于 Adam 一样成为框架默认。

## 指南分析

**选型决策树（按约束驱动）**

| 约束场景 | 推荐 | 理由 |
|---------|------|------|
| 显存充足，通用微调 | LoRA+ 起步 | 零成本收敛增益 |
| 激活内存瓶颈（长序列/大 batch） | LoRA-FA | 冻 A 直击激活开销 |
| 极端显存/边缘设备/多任务轻量适配 | VeRA | 参数量最小 |
| 需灌注领域新知识（非风格适配） | Delta-LoRA | W 参与更新突破旁路天花板 |
| RLHF/GRPO 等 RL 场景 | LoRA + rank 实证调优 | 见关联笔记的实证结论 |

**实施提示**
- 变体可组合：LoRA+ 的学习率技巧理论可叠加在 LoRA-FA 上（A 冻结时只需给 B 设高 lr）
- 评估变体收益时控制变量：同 rank、同数据、同步数下比较，避免"参数少=好"的错觉

## 拓展应用推荐

1. **domain-llm-training-pipeline 增补**：领域文档训练流水线的配置模板中加入变体选型段（当前默认 LoRA，可加 LoRA+/LoRA-FA 选项），下次领域微调任务直接引用本表。
2. **dp5/AutoDL 训练预算优化**：训练前按显存公式预判——若激活内存是瓶颈，LoRA-FA 可在同等 GPU 上放更大 batch，等效提升梯度估计质量。
3. **Jetson 边缘微调实验**：本机 Orin 上对小模型做 VeRA 实验（参数量最小，适合验证边缘微调可行性），与 nexa-local-inference 技能联动。
4. **量化训练菜单补全**：本篇五变体 + QLoRA 组合（4bit 基座 + 低秩适配）是消费级显卡微调的标准配置，可作为后续笔记选题。

→ 相关：LoRA-GRPO最优配置实证-RL场景的Rank选择与超参数.md
