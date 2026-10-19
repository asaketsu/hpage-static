# Scaling Law 新解：GLM-5.3 的对照实验与「Lab 即 Infra」（X/推文笔记）

> 来源: X.com [@jietang《Thoughts About Scaling Law》](https://x.com/jietang/status/2089941544581403107)（2026-08-19）+ [@MaxForAI 解读](https://x.com/MaxForAI/status/2090131950753464435)（2026-08-20）
> 作者: 唐杰（智谱 GLM 团队）· Max For AI（解读篇）
> 类别: Scaling Law · MoE · Post-training · AI Lab 工程

---

## 一、核心概念（内容整理）

两篇构成"原文 + 解读"配对：唐杰借 GLM-5.3 发布写 Scaling Law 的演化史，MaxForAI 顺势提出「大家最后拼的是 Infra」。

**核心论断**：Scaling Law 没死，是我们把它理解得太窄了。以前 Scale 参数/Token/GPU，现在 Scale 数据生产、RL、Environment、Verifier、实验速度——甚至团队和组织方式。

**GLM-5.3 = 一个受控实验**：与 GLM-5.2 同 Base、同架构、同总参数量与激活参数量，只做一个月 long-horizon environment + RL post-training，能力继续明显上涨 → **证明 post-training 这个旋钮还有大量余量**。

## 二、技术要点（指南分析）

### 2.1 Scaling Law 三部曲（jietang 原文主线）

| 阶段 | 结论 | 代表 |
|------|------|------|
| ① Kaplan 2020 | 参数增长快于数据（≈2.7:1） | GPT-3、Gopher、MT-NLG 跟随 |
| ② Chinchilla (Hoffmann 2022) | 400 模型重拟合：**20 tokens/参数**；算力足够时两者应同速增长 | 纠正万亿参数弯路 |
| ③ 推理成本时代 | 模型每天被调用数十亿次，**推理主导生命周期成本** → 最优解移向小模型 + 刻意过训 | Llama-2-7B（290 TPP）、Gemma-2-9B（889 TPP） |

关键教训：Kaplan 指数拟合的误差**随算力每加一个数量级而复利放大**——那一代最大的模型恰恰是最错配的。万亿参数竞赛是全行业一起走过又退回的弯路。

### 2.2 MoE 改变了目标函数

MoE 模型必须区分两个量：

| 量 | 管什么 |
|----|--------|
| **总参数量** | 模型能"装"多少——知识、事实、长尾 |
| **激活参数量 + 有效深度** | 模型能"想"多远——因果链能扛多少步不断线 |

稠密 20:1 比例**不可迁移**到 MoE。且比例根本不是单值：Roberts et al. (2025) 发现最优 TPP 是**任务相关**的——记忆型任务偏更多参数，推理型任务偏更多数据。后续 MoE 研究观察到：固定 TPP 下推高总参反而伤推理，激活更多专家则稳定提升。

**安全场景的印证**：找漏洞不是检索问题——不来自背了更多 CVE，而来自**把二十步推理链走完不丢线索**。这个能力不住在总参数量里。

### 2.3 GLM-5.3 的实验设计

- 同 Base/架构/总参/激活参（对照变量控制到极致）
- 一个月只 Scale **long-horizon environments + RL**
- "gains are not marginal"
- 结论：总参数有阈值效应（够装下世界即可），之后增量能力来自**有效深度 + post-training**

"dials do not have to be turned together"——旋钮不必一起拧；下一个值得拧的很少是上一个值得拧的。下次可能是 mid-training、pre-training。

### 2.4 MaxForAI 解读：Lab 即 Infra

段子"数据就是 Infra，Infra 就是算法，算法就是数据"在 frontier model 语境下不再像废话：

```
更好的 RL → 需要稳定 Infra 跑 rollout
更长的 rollout → 需要 Environment / Sandbox / Verifier / Reward
这些跑起来 → 源源不断产生新训练数据（闭环）
```

引用 OpenAI post-training 翁家翌（WhyNotTV 播客）：**每家 Infra 都有 Bug，谁修掉的 Bug 越多，谁的模型训得越好。**

Infra 的外延清单（远超 GPU 集群）：
- Data Pipeline / RL 系统 / Environment+Verifier+Eval / 训练框架
- **实验迭代速度**（idea → 实验 → 结果进下一轮训练的周期）
- 甚至：团队构成、研究员-工程师配合方式、信息流动、发现问题-修复问题的速度——**人是 Infra，组织也是 Infra**

**结语**：AI Lab 真正的核心产品不是某个模型，而是那套能持续稳定高效制造更强模型的系统。**你 Scale 的是整个 Lab。**

## 三、复现验证（归纳总结）

- GLM-5.3 = 5.2 的受控对照（变量只动 post-training）——这是Scaling 论文里罕见的"单变量实验"证据
- 78 万阅读、4.3K 赞、2.8K 转——社区高度认可
- 评论中 Nick Emb 补充：Qwen 3.8 27B 与 GLM-5.3 都是"密度仍有增长空间"的例证
- TPP 数字可查证：Llama-2-7B ≈ 290、Gemma-2-9B ≈ 889（2T tokens / 7B、~8T / 9B 口径）

## 四、可学到的点（归纳总结·续）

1. **Scaling Law 是多旋钮系统**：参数/数据/算力只是最初三个；post-training、RL environment、有效深度、实验速度都是新的可 Scale 维度。
2. **单变量实验是金标准**：GLM-5.3 的说服力来自"只动一个旋钮"——比堆料发布会可信得多。
3. **总参数有阈值效应**："够装下世界"之后，能力增量来自别处——别再无脑堆总参。
4. **MoE 的二象性**：总参管记忆、激活管推理——两个量要分开调，稠密比例不可迁移。
5. **推理成本主导时代**：TPP 升到几百是常态（过训换推理便宜），"训练一次评测一次"的 Chinchilla 假设已过时。
6. **Infra 是全栈概念**：从 GPU 到数据管线到组织协作方式——翁家翌"修 Bug 多少决定模型好坏"是工程视角的 Ground Truth。
7. **突破 ≠ 灵光一现**：多数"突破"是系统终于有能力把算法 Scale 起来了。

## 五、趋势判断（拓展应用）

1. **Post-training/RL 是当前余量最大的旋钮**：GLM-5.3、DeepSeek-R1 一致指向"同 Base + 强化学习 = 明显增量"。与《LLM 技术选型》笔记中"RL 从加分项变标配"判断吻合。
2. **Mid-training 将成下一个热词**：jietang 明示"next time, maybe mid-training"—— annealing/合成数据/课程学习在中段训练的 Scale 化。
3. **AI Lab 竞争 = 系统工程竞争**：模型性能差异的根因在 Infra 完备度（数据管线/环境/验证器/迭代速度），与 GPU 数量解耦。
4. **组织设计进入 Scaling 范畴**："人是 Infra"意味着 Lab 的人员结构与协作流是可优化、可度量的工程对象。
5. **对小团队的含义**：Scale 不了参数和数据，但可以 Scale 实验→数据闭环的迭代速度——这是资源受限团队的唯一出路。

## 查询拓展与出处（引用与关联）

| 关联笔记/Skill | 关联 |
|---------------|------|
| 同日《LLM 技术选型决策指南》 | RL/RFT 层 = 本文 post-training 旋钮的落地路径 |
| 同日《从零训练语言模型》 | 小模型先跑通 = "总参阈值前"的工程实践 |
| `train-lm-pipeline` 项目 | 27M→7B 放大路径表正是 Chinchilla 时代 TPP 逻辑 |
| `grpo-rl-training` skill | long-horizon RL 的具体训练方法 |
| `quant-trading` / 铁律体系 | "修 Bug 多少决定模型好坏"与量化策略迭代同理 |

- 原推: https://x.com/jietang/status/2089941544581403107（唐杰，2026-08-19，780K 阅读）
- 解读: https://x.com/MaxForAI/status/2090131950753464435（2026-08-20，6.4K 阅读）
- 文献: Kaplan et al. 2020 / Hoffmann et al. 2022 (Chinchilla) / Roberts et al. 2025


## 相关笔记

- [唐杰：万亿参数是弯路，后训练旋钮时代](./2026-08-20-唐杰万亿参数是全行业弯路后训练旋钮时代.md) — 同主题权威观点篇，GLM-5.3 对照实验的行业解读
- [后训练全景：SFT / DPO / RLHF 原理与实操](./2026-08-20-后训练全景SFT-DPO-RLHF原理与实操.md) — 后训练旋钮的技术基础，Scaling Law 新解→实操落地
- [LLM 后训练 RL 效率与可靠性](./2026-08-20-LLM后训练RL效率与可靠性-RLVR调度Debate抗Hack与ES换道.md) — 后训练 RL 的前沿技术，RLVR/ES 是旋钮效率的实证