# Transformer 策略训练稳定性：熵坍缩、价值爆炸与序列策略优化

> 综述笔记 · 2026-09-21 · arXiv 文献扫描
> 关联：DUCK H1T/TRANS4 熵坍缩与 farming 事故解剖（docs/71、docs/81、docs/86）· W2 TRANS 计划

## 查询拓展

DUCK 的 TRANS 路线连吃三败：H1T 熵坍缩（entropy=-0.69）、TRANS4 急性 farming（value_loss 0.19→52.7 爆炸、reward -268 断崖、熵_coef 四调 0.02/0.01/0.005/0.0075 全失败）。用户已明确"我更喜欢 transformer""两架构缺一不可"，W2（W1 配方 + TRANS + F1 σ-gate）是 TRANS 复活的最后一搏。本笔记扫描 2026 年序列/transformer 策略训练稳定性的文献面，回答三个查询：① TRANS 策略的失稳机理有哪些理论解释？② LLM-RL 社区的熵管理解法能否移植到机器人？③ 若 W2 再败，下一代 TRANS 的设计选项是什么？

一个结构性发现先行：arXiv 上 "entropy collapse + PPO" 的 2026 年命中几乎全部来自 **LLM 推理强化学习（RLVR/RLHF）**，机器人侧 transformer 策略论文很少把熵动力学当核心贡献点。这意味着 DUCK 遇到的 TRANS 熵坍缩是跨域共性问题——两边用同一套 PPO/ratio-clipping 数学，LLM-RL 的解法可以移植。

## 内容整理

### A. LLM-RL 侧：熵坍缩的四个 2026 解法

| 文献 | 日期 | 核心机制 | 对 TRANS 策略的适配点 |
|---|---|---|---|
| Optimistic Policy Regularization | 2026-03-06 | 反转传统 KL/熵正则的"悲观"限制，主动维持探索覆盖 | 熵衰减过快时的正则形态选项 |
| BandPO（arXiv:2603.04045） | 2026-03-05 | 概率感知界弥合信赖域与 ratio clipping——clip 不再对概率质量分布盲 | 抑制输出分布尖锐化时 ratio 估计失真（TRANS4 死前形态） |
| SAFE（arXiv:2602.04318） | 2026-02-04 | 熵感知预测控制（MPC 式）做稳定对齐——熵不坍缩当约束而非超参艺术 | 把熵管理从"调 coef"升级为"显式约束" |
| Soft Sequence Policy Optimization | 2026-02-22 | 序列级策略优化 + soft 化，直接针对序列模型策略的信用分配与方差 | 序列输出策略（transformer）的方差控制 |

### B. 机器人侧：TRANS 策略可以很稳的三条证据

1. **RecoverFormer（arXiv:2604.22911）**：50 步观测历史因果 transformer + 潜在模式头 + 接触可供性头，Unitree G1 上 +25% 质量错配 75.5% 恢复率、30ms 延迟 89%、100-300N 推扰开场地→有墙环境零样本 100%。transformer 策略本身不是不稳定的原罪，配套设计到位时鲁棒性极高。
2. **观测历史蒸馏（arXiv:2606.21562）**：关键论断——循环/窗口 transformer 与全历史 transformer 的性能差距"不源于架构限制，而源于学习压缩过去信息的方式不同"；直接监督学生记忆对齐教师瓶颈表征可大幅缩小差距。启示：64 帧滑窗 TRANS 学不好时，问题可能不在窗口长度，而在窗口内信息没有被显式压缩目标监督。
3. **TransCurriculum（2026-03-14）**：Fast & Stable Locomotion 的多维课程学习框架，与 DUCK 现有 curriculum（action_rate -0.1→-1.0）同型但多维化。TRANS 策略对课程编排更敏感（序列模型梯度信噪比低）。

### C. 病程对照：TRANS4 的死法在文献坐标里的位置

TRANS4 实测六点采样：熵 7.71→5.8→0.002→-2.0（先坍缩）→ value_loss 0.19→52.7（后爆炸）→ reward -268 断崖、action_rate -8.1 乱动、熵回弹 0.77（策略变随机）。这符合"尖锐策略→advantage 估计失真→价值函数追不上→PPO 更新方向错"的级联，BandPO 论文描述的 ratio 失真与 SAFE 描述的熵管理缺位分别对应级联的第 1、2 环。

## 归纳总结

1. **熵坍缩研究主战场在 LLM-RL 不在机器人**——跨域移植是合法操作（同为 PPO 数学），DUCK 无需等机器人社区给出答案。
2. **transformer 策略不稳的锅在"优化器-架构失配"不在架构本身**——RecoverFormer 证明配套设计到位的因果 transformer 策略极其鲁棒。
3. **压缩监督是被忽视的杠杆**——64 帧滑窗缺的不是长度而是显式压缩目标；MLP 冠军蒸馏 TRANS 学生是有文献依据的下一代选项。
4. **熵_coef 盲调已穷尽**——四调全败（0.02/0.01/0.005/0.0075）与文献共识一致：熵管理需要机制化（正则/界/约束），不是超参艺术。
5. **课程编排对 TRANS 更敏感**——W2 若启动失败，先查课程曲线陡度再怪架构。

## 趋势判断

- **短期（W2 判读窗口）**：σ-gate 稳 value + H1YAW 配方稳奖励的工程拼接若成功，验证"两半各取一半"路线；若失败，按决策表转正则/蒸馏，不再碰 entropy_coef。
- **中期**：LLM-RL 的熵管理工具（BandPO 式界、乐观正则）向机器人策略训练扩散是大概率事件——两边共享 PPO 内核，迁移成本低。
- **长期**：序列策略的"压缩监督"（蒸馏瓶颈表征）可能成为标准配置，正如 obs 归一化从 trick 变成默认。

## 拓展应用推荐

1. **W2 训练判读决策表**（直接可用）：

| 症状（W2 训练中） | 文献解释 | 处置 |
|---|---|---|
| 熵单调降但 >0.5 且 reward 稳升 | 正常确定性化 | 不动，继续 |
| 熵穿零 + value_loss 同步爬升 | TRANS4 复现（尖锐→advantage 失真→value 爆） | 立即 kill，转 F2：乐观正则/BandPO 式界 |
| 熵稳但 air_time=0 | 趴地 farming（velstand 型） | kill，奖励结构问题与 TRANS 无关 |
| value_loss>30 突发 | 价值函数爆炸前段 | 降 lr 或 value 单独 clip |
| TRANS 恒弱于同配方 MLP | 压缩策略未学到位（2606.21562） | 蒸馏：MLP 冠军教师→TRANS 学生 |

2. **MLP→TRANS 蒸馏路线**：DUCK 已有四模型横评冠军 H1YAW（MLP），可当教师监督 TRANS 学生的窗口压缩——比从零训 TRANS 便宜且有文献背书。
3. **守护 cron 判据升级**：现役 duck-train-guard-15min 的熵/value 阈值判读可吸收本表，区分"正常确定性化"与"坍缩前奏"。

## 指南分析

- **现路线不动**：W1/W2 按计划验收（评测即杀铁律），本笔记只提供判读坐标和败后路线图，不干预在训实验。
- **证据边界**：本笔记基于 arXiv 摘要级扫描（全文未精读），LLM-RL 侧解法（BandPO/SAFE/乐观正则）在机器人 TRANS 上的实证效果无直接文献支持，移植属合理推断而非已验证事实。
- **互链**：docs/71（H1T 熵坍缩原始案例）、docs/81（修复三件套）、docs/86 §16（TRANS4 急性 farming 解剖+W1/W2 方案）、《2026-09-19-熵保持强化学习与PPO熵坍缩修复.md》（前作，本文为 TRANS 专项续篇）。

## 来源

- Optimistic Policy Regularization — arXiv:2603.06133 (2026-03-06)
- BandPO — arXiv:2603.04045 (2026-03-05)
- SAFE — arXiv:2602.04318 (2026-02-04)
- Soft Sequence Policy Optimization — arXiv:2602.xxxx (2026-02-22)
- RecoverFormer — arXiv:2604.22911 (2026-04-24)
- Compressing Observation History — arXiv:2606.21562 (2026-06-19)
- TransCurriculum — arXiv:2603.xxxx (2026-03-14)
- 检索方式：arXiv API 直连（Tavily 432 / 智谱 -401 双故障夜，降级链第三级）

## 相关笔记

- [自然步态模仿学习](./2026-09-21-自然步态模仿学习2026-从AMP到流匹配先验.md) — DUCK 完美版双子星：稳定性×自然度
- [RL训练失败模式与RewardHacking](./explore/2026-09-17-RL训练失败模式与RewardHacking自动检测.md) — farming/失败模式同族
- [ROLT稳健运动Transformer](./explore/2026-09-17-ROLT稳健运动Transformer-足式机器人OOD泛化架构.md) — TRANS 策略架构选项
