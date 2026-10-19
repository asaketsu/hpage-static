# 从 RL 到蒸馏再到软蒸馏：Why RL Matters（posttrain 定位全解）

> **出处**：@qingke_ai（青稞社区）X 长文 2026-08-15，作者 ybq，知乎原文 zhuanlan.zhihu.com/p/2067725096886785009
> **原文链接**：https://x.com/qingke_ai/status/2088637945972654080
> **记录日期**：2026-08-16

**标签**：#RL #蒸馏 #软蒸馏 #posttrain #CoT-pattern #GRPO #agent训练

---

## 一、原文核心内容（完整还原）

### 1.1 核心论点：SFT 定 pattern 上限，RL 做本土化+可控化

文章用一条主线串起 posttrain 全景：**SFT 定型 cot pattern（决定上限）→ RL 把 pattern 改造成模型自身的最佳表达（本土化）+ 压制坏 pattern（可控化）→ 蒸馏是偷看学习笔记（捷径）→ 软蒸馏是借 SOTA 之力（明牌竞争）**。

### 1.2 CoT Pattern 三分法（原文最精彩的例子）

给定 997 × 1003，三种 pattern：

| Pattern | 解法 | 特点 |
|---------|------|------|
| **good** | (1000−3)(1000+3) = 1000²−3² = 999991 | 短、准、易泛化 |
| **mediocre** | 1003×(900+90+7) 逐项展开 | 步骤多→出错率高→token 效率低 |
| **bad** | 直接 = 999991 | 记答案不学法——小模型学到后见 997×任何数都答 999991 |

**关键论断**：好的 cot pattern = 更短 + 更准 + 更易泛化。SFT 阶段的 pattern 定型**几乎决定 posttrain 效果上限**；很多优质 pattern 在 RL 阶段无法靠 explore 撞出来（agent 训练同理：不教，main agent 想不到开 sub_agent）。

**Agent 时代延续**：构造 environment trajectories 本质仍是"寻找更优质的 cot pattern"——reasoning 与 agent 是同一件事。

### 1.3 RL 的四大作用

1. **本土化改造**：同一 pattern（99×99=99×(100−1)），强模型一步到 9900−99=9801；弱模型要写 5 步。SFT 数据多来自强模型/人工（极简优雅），弱模型消化不了，需 RL explore 找到与自身知识量+tokenizer 契合的表达
2. **解释"SFT 起点低 RL 终点高"**：起点低是 pattern 与能力不匹配，不是数据质量差
3. **基因突变+进化**：算力够大 rollout_n 够大，RL 总能 explore 到新优质 pattern，GRPO 负责给强学习信号
4. **可控化（被低估的作用）**：pretrain 几十 T 语料里的坏 pattern（多个 think 标签/中英混杂/反思次数失控），SFT **没有打压能力**只能靠 RL 惩罚 loss 压制；"思考档位"= RL 给不同档位配不同上下文窗口即可实现

### 1.4 蒸馏：偷看学习笔记

- **RL 收益可被蒸馏窃取**：RL 本质是找更好 pattern，寻找过程不具价值——用 RL 后模型当 teacher 蒸馏，student 指标接近 teacher
- **业界合版标配**：多个 RL 子模型 reject sampling SFT（或 OPD）
- **1T→100B 的 pattern 平移**：大模型 explore 的 pattern 更丰富，喂给小模型+RL 适配表达（同尺寸同词表屡试不爽）
- **student 可超 teacher**：改数据分布（如只保留英文 cot）——但作者警告：任何让 student 超 teacher 的操作应回流去提升 teacher
- **金句**：认为蒸馏无用，大抵没亲自训过大模型；认为蒸馏是全部，大抵只想做追赶者

### 1.5 软蒸馏：借 SOTA 之力（明牌竞争）

高级蒸馏不止学 response：用 SOTA 合成能力边界数据 / 分析自家 pattern 缺点 / 优化 RL verifier。
"任何国内厂商都不敢说自己没用 GPT/Claude 的帮助。"
**终局判断**：纯训练阶段已是明牌竞争——比谁更能 scaling（model parameters / RL data / agent environments）；领头羊必须重投 RL 摆脱（软）蒸馏依赖，应用价值追赶者蒸馏即是最好选择。

---

## 二、五要素展开

### 2.1 功能清单（本文提供的认知工具）

| 工具 | 用途 |
|------|------|
| cot pattern 三分法 | 评估 SFT 数据质量的直观框架 |
| RL 四作用模型 | 本土化/进化/可控化/解释起点低现象 |
| 蒸馏=偷笔记 心智模型 | 快速理解 reject sampling/合版/1T→100B 平移 |
| 软蒸馏清单 | 合成边界数据/找 pattern 缺点/优化 verifier |
| 决策规则 | 领头羊投 RL vs 追赶者用蒸馏 |

### 2.2 使用性评估

**强项**：一线 posttrain 从业者的实操视角（"sft 后多 think 标签""中英混杂屡教不改"全是真实生产 pain point）；三分法例子极好传播；把 reasoning/agent/posttrain 统一进"pattern"单一框架，解释力强。

**局限（原文自认"个人观点未必正确"）**：
- "RL 收益可被蒸馏窃取"成立的前提是 teacher 的 pattern 已收敛——若 RL 还在持续 explore（前沿能力），蒸馏只能拿到快照
- 无实验数据/引用支撑，是经验之谈（知乎体）
- "SFT 定上限"与业界"RLVR 涌现超越 SFT 上限"的报告（如 DeepSeek-R1 zero）存在张力，原文未处理
- 软蒸馏部分受限于国内视角，"国内 vs 国外"框架对通用读者有场景依赖

### 2.3 指导性意见

- **做小模型/垂直应用**：蒸馏路线（强 teacher + reject sampling + RL 适配）性价比最高——这正是我们 lan-llm-farm 0.8B 零件锻造的路线印证
- **做 SFT 数据**：用三分法审查每条轨迹——尤其剿灭 bad pattern（记答案型），它对同分布是毒药
- **agent 训练**：SFT 必须显式教"何时开 sub_agent / 怎么交换信息"，这些 explore 不出来；RL 只负责本土化"怎么用"
- **评估 posttrain 方案**：先问"pattern 由谁定"——teacher 定（蒸馏）还是自己 explore（RL），再谈算力分配
- **可控性问题**（格式混乱/语言混杂）：别再加 SFT 数据了，直接 RL 惩罚——SFT 无打压能力是本文最实用的工程结论

### 2.4 案例可寻

- 997×1003 三分法（可直接用于团队培训的示例）
- 1T model rl pattern → 100B student + RL 适配（同尺寸同词表屡试不爽——合版工程实践）
- 思考档位实现：RL 不同档位给不同上下文窗口（产品化细节）
- 中英 teacher 只留英文 cot 蒸馏出更强 student（数据分布改造案例）

### 2.5 使用方法借鉴

**SFT 数据审查 checklist（从三分法衍生）**：
1. 抽样轨迹问：这条是 good/mediocre/bad？
2. bad（直给答案无推理）→ 删
3. mediocre（步骤冗余但可学）→ 标注保留，量多时降权
4. good（简洁优雅）→ 优先，但注意超出学生消化力的"过优雅"需 RL 本土化

**posttrain 路线决策树**：
```
目标 = 应用价值/追赶 → 蒸馏（SOTA teacher + reject sampling + 小规模 RL 适配）
目标 = 领头羊/前沿能力 → 重投 RL（scaling rollout + GRPO 信号工程）
混合现实 → SFT 定 pattern（teacher 数据）+ RL 本土化+可控化 + 软蒸馏优化 verifier
```

---

## 三、查询拓展

1. **R1-zero 的反例张力**：DeepSeek-R1-Zero 纯 RL（无 SFT）也涌现出长反思 pattern——说明"优质 pattern 只能 SFT 给"不是铁律，算力极大时 RL 也能 explore 出（原文"基因突变"段其实自洽：rollout_n 足够大）
2. **OPD（On-Policy Distillation）**：文中提到但未展开——student 用 teacher 的 token 级分布做 on-policy 修正，是 2025-2026 蒸馏研究热点，比 response-level SFT 更贴近 RL
3. **reject sampling 合版**：多个 RL 子模型各自 explore 不同 pattern → 采样优质 response 合并 SFT——本质是"并行探索+串行收割"，与遗传算法的 population 思想同构
4. **GRPO 细节**：文中只点到"把握高质量数据给强信号"——GRPO 组内相对优势无需 value model，与"记住突变 pattern"的需求匹配
5. **对 Agent 训练的推论**：environment trajectories = agent 时代的 cot pattern → 谁掌握大量高质量 agent 轨迹（工具调用/委派/交换信息），谁就握住 agent 模型的"SFT 上限"——这解释了各家疯抢 agent 环境数据的现象

---

## 四、内容整理

**原文信息架构**：cot pattern 定义（三分法例子）→ SFT 定上限论 → RL 四作用（本土化/进化/可控化/解释现象）→ 蒸馏本质（偷笔记/可窃取 RL 收益/合版标配）→ 软蒸馏（借 SOTA/明牌 scaling 竞争）→ 决策规则（领头羊 vs 追赶者）。

**本笔记重组**：论点 → 证据强度分层（一线经验强/无数据支撑弱）→ 工程可抄物（checklist/决策树）→ 与 R1-zero 张力的补全。

**核心增量判断**：本文的最大价值不是"RL 有没有用"的站队，而是给出了**分工模型**——SFT 管 pattern 供给、RL 管表达适配与压制、蒸馏管跨模型搬运、软蒸馏管借力优化。四个组件各有不可替代位，争论"谁更 matter"是把分工问题误读为替代问题。

---

## 五、趋势判断

1. **"思考档位"类产品化能力会成为 RL 阶段标配**：上下文窗口分档这种低成本可控化手段，会被所有推理产品复制
2. **蒸馏与 RL 的边界继续模糊**：OPD/on-policy 修正让蒸馏越来越"像"RL——未来 posttrain 流水线是连续谱而非 SFT/RL 二分
3. **agent trajectories 数据成为新护城河**：environment trajectories = agent 版 cot pattern，数据工程的竞争从"题目+答案"升级为"环境+轨迹"
4. **可控化 RL 需求暴涨**：合成语料污染 pretrain 的坏 pattern 问题随语料规模恶化——RL 惩罚是唯一压制手段，这条工程刚需独立于"RL 提升智能"的争论
5. **scaling 明牌化利好算力持有者**：pattern/数据/环境三元 scaling 都是算力函数——8×A100 级别的局域网农场在"小模型+蒸馏+RL 适配"生态位有明确价值

---

## 六、归纳总结

**一句话**：SFT 定 cot pattern 上限、RL 做本土化改造+可控化压制、蒸馏偷学习笔记跨模型搬运、软蒸馏借 SOTA 之力——四者是不可替代的分工而非替代关系；纯训练已是明牌 scaling 竞争（参数/RL 数据/agent 环境）。

**结构记忆**：
- 三分法：good（短准泛化）/ mediocre（冗长易错）/ bad（记答案毒药）
- RL 四作用：本土化 / 基因突变 / 可控化（SFT 无打压能力）/ 解释起点低
- 蒸馏一句：偷笔记——RL 的收益可窃取，寻找过程不具价值
- 软蒸馏清单：合成边界数据 / 找 pattern 缺点 / 优化 verifier
- 决策规则：领头羊投 RL，追赶者用蒸馏

---

## 七、关联分析

| 关联 | 关系 |
|------|------|
| AI4AI at Test-Time | 同构映射：强模型造 harness（AI4AI）≈ 强模型当 teacher（蒸馏）——都是"借强者的结构化产出" |
| lan-llm-farm 0.8B 锻造 | 路线印证：小模型蒸馏+RL 适配正是"应用价值追赶者"的最优解 |
| Lean×AI | Lean 内核=确定性 verifier——软蒸馏"优化 RL verifier"的极致形态（零幻觉验证信号） |
| a100-training-playbook | 算力承接：scaling rollout_n/pattern explore 的底层是训练工程 |
| MIT 推理笔记 | 哲学对照：cot pattern=语言外壳的推理表达，RL 本土化=把表达适配到模型自身"非语言机制" |
| Qwen3.8-27B 部署 | 上下游：posttrain 成品（qwen 系列）的部署端消费 |

---

## 八、行动清单

- [x] X 长文全文提取（r.jina.ai）+ 7 模块笔记
- [ ] lan-llm-farm SFT 数据加"三分法审查"步骤（剿灭 bad pattern）
- [ ] posttrain 路线决策树挂入飞机设计实验室知识库
- [ ] 追踪 OPD（on-policy distillation）研究进展
- [ ] agent 环境轨迹数据建设纳入技术雷达

---

## 九、一句话总结

> SFT 供给 pattern、RL 适配表达并压制劣习、蒸馏搬运强者的学习笔记、软蒸馏借 SOTA 之力——posttrain 四件套各司其职；争论"RL 还是蒸馏更 matter"是把分工误读成了替代。


## 相关笔记

- [AI4AI-at-TestTime-强到弱Harness能力转移](./2026-08-16-AI4AI-at-TestTime-强到弱Harness能力转移.md) — 强到弱能力转移，蒸馏是落地手段
- [Qwen3.5-0.8B端侧零件工程使用指南](./2026-08-14-Qwen3.5-0.8B端侧零件工程使用指南.md) — 端侧小模型是蒸馏产物落地实例
- [Needle2-极简端侧AIoT模型架构](./2026-08-14-Needle2-极简端侧AIoT模型架构.md) — 极简架构与蒸馏压缩对照
- [遗传算法入门-让代码自己进化求解优化问题](./2026-09-14-遗传算法入门-让代码自己进化求解优化问题.md) — reject sampling 与 population 思想同构
