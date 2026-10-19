# Transformers are Bayesian Networks：Sigmoid 前向 = 置信传播 + 幻觉的结构性根因——arXiv:2603.17063 全文精读 + 形式化定理拆解 + 体系映射

> **来源**：arXiv:2603.17063v1 [cs.AI]，Greg Coppola，2026-03-17
> **原文链接**：https://arxiv.org/pdf/2603.17063
> **抓取方式**：web_extract 全文 76KB（完整论文正文 + 参考文献 + 目录），逐章精读
> **笔记日期**：2026-09-11
> **关联笔记**：《NoFreeChecker》（verifier 需要有限概念空间）、《为不信任而设计》（模型本身可能无概念）、《LLM推理优化技术》《agent-reliability-engineering》

---

## 零、结论先行

**这篇论文给出了一个精确的数学命题：sigmoid Transformer 的前向传播就是置信传播（Belief Propagation, BP）——不是近似、不是类比，而是按架构定义、对任意权重都成立的等式。五条 Lean 4 形式化定理 + 实验双见证。**

**论文最炸裂的推论不在架构侧，在幻觉侧**：

> "Hallucination is not a bug that scaling can fix. It is the structural consequence of operating without concepts."

幻觉不是能被 scaling 修复的 bug——它是**无概念空间操作的结构性后果**。这与昨日《NoFreeChecker》"model-intrinsic verifier 可信度最低"和《为不信任而设计》"模型本身可能就是威胁"构成**三份独立来源收敛到同一结论**。

## 一、五条核心定理（全部 Lean 4 形式化验证）

| 定理 | 内容 | Lean 4 仓库 |
|------|------|------------|
| 1.1 General BP | 任意 sigmoid Transformer 权重 W，存在隐式因子图 G(W)，一次前向 = 一轮加权 loopy BP | sigmoid-transformer-lean |
| 1.2 BP Implementation | 存在显式构造权重，使 Transformer 对任意因子图实现精确 BP；深度 d × ⌈log₂k⌉ 次前向 = 完整精确 BP | transformer-bp-lean |
| 1.4 Uniqueness | 产生精确后验的 sigmoid Transformer 必然有 BP 权重——不存在通向精确后验的第二条路径 | sigmoid-transformer-lean |
| 5.1 Turing Complete | 任意 Turing 机可被 Transformer 模拟（Boolean 电路构造） | universal-lean |
| 9.1 Finite Concept Space | 有限验证器最多区分有限个概念；无 grounding = 无概念空间 = "正确"无定义 | godel |

**Corollary 1.3（树结构无幻觉）**：BP 权重 + 树结构因子图 + T≥diameter 轮 → 每个节点精确后验，零幻觉，无需经验假设。

**Corollary 4.1（幻觉需要 ungroundedness）**：在 grounded 树结构 + BP 权重下，幻觉在结构上不可能。幻觉需要三条件之一：错误权重 / 错误路由 / 缺乏 grounding。

## 二、核心机制拆解

### 2.1 Sigmoid = 对数概率的精确代数

**为什么是 sigmoid 不是 ReLU**——论文 §3.5 最关键的论证：

- `logit(p) = log(p/(1-p))` 和 `σ` 互为精确逆函数
- 两条独立证据的组合：`P(H|e₀,e₁) = σ(logit(m₀) + logit(m₁))`
- 这个代数来自 **Turing 和 Good 在 Bletchley Park 破译 Enigma 时发展的 weight-of-evidence 方法**（1950 Good 正式发表）
- Pearl 1988 年的 sum-product 算法在二元变量上 reduce 到同一个公式——但 Pearl 没有把它与 Turing-Good 传统连接

**Sigmoid FFN 的 `σ(w₀·logit(m₀) + w₁·logit(m₁) + b)` 就是加权对数概率加法**——不是设计选择（梯度流/输出归一化），是**执行 Turing-Good-Pearl 代数所需的精确函数**。

### 2.2 AND/OR 布尔结构（§8 最有创意的论证）

| Transformer 组件 | 布尔角色 | 机制 |
|-----------------|---------|------|
| Attention | **AND（合取）** | 多头写入共享残差流——FFN 运行前所有必需输入必须同时在场（残差流是共享工作区） |
| FFN (sigmoid) | **OR（析取）** | `σ(logit(m₀)+logit(m₁))` = 概率析取，正确归一化 |
| 严格交替层 | **Pearl 的 gather/update** | AND→OR→AND→OR... = QBBN 二部图推理展开 |

**关键洞察**：AND 不在单个 head 内——在残差流的结构中。Head 0 写入 dim 4，Head 1 写入 dim 5，FFN 读整个残差流或根本不跑——没有"收到一半输入"的状态。

### 2.3 三个 Softmax 的精确分工（§10）

| Softmax | 位置 | 职责 | BP 中的角色 |
|---------|------|------|-------------|
| 1 | Attention 内 | 路由 | 可微 argmax = 查找表（按索引取邻居信念） |
| 2 | FFN 内（sigmoid） | 推理 | 贝叶斯后验 = `updateBelief` |
| 3 | 输出 | 生成 | 词汇表分布（标准 LLM = pattern-match；QBBN = 边际分布） |

**"QBBN 不是替换 softmax，是替换 logits"**——同一个数学操作在标准 LLM 里是推理的近似，在 QBBN 里是精确推理。架构一直有能力做后者，只是需要正确的 logits。

### 2.4 Sigmoid vs ReLU：精确 vs 兼容（§10.4）

- **Sigmoid**：Lean 证明的内部计算就是 BP 量——不仅输出匹配，内部表示也匹配。架构不给替代路径留空间。
- **ReLU/GELU**：保持非负性（概率质量的必要条件），但不强制精确归一化。梯度下降仍能找到 BP-like 权重（val MAE 0.000752），但内部表示不一定对应 BP 命名量。
- **"Compatibility is not identity"**——ReLU 实验证实机制可找到，但 sigmoid 证明机制是唯一路径。

### 2.5 有限概念空间定理（§9，最有哲学冲击力）

**Theorem 9.1**：有限状态机 n 个状态最多区分 nⁿ 种行为。任何有限验证器只能区分有限个概念。

**推论链**（精确逻辑链）：
1. 你想要可验证推理 → 需要有限验证器
2. 有限验证器 → 有限概念空间
3. 有限概念空间 → 概念是离散可数的
4. 概念空间外的东西不是"错的"——是"无意义的"
5. 无 grounding 的 LLM 没有有限验证器 → 没有"正确"的定义 → 幻觉不是 bug 而是结构后果

**Leibniz 的 characteristica universalis 实现了**：
- 原始概念 = grounded Horn clauses（2n² 个）
- calculus ratiocinator = belief propagation
- 机械实现 = Transformer
- 正确性保证 = Lean 4 证明
- "Calculemus"（让我们计算）

## 三、实验确认（每个形式化结果都有双见证）

### 3.1 BP 权重从零学习（bayes-learner）

- 20,000 随机因子图（18K train / 2K val）
- 标准 TransformerEncoder（2 层 2 头 d=32 ~5K 参数）
- **val MAE 0.000752**——后验匹配到三位小数
- 无构造提示、无权重初始化偏置 → 梯度下降自己找到了 BP 权重

### 3.2 Turing 机模拟（learner）

- 5 种结构不同的 TM（二进制自增/自减/按位取反/左移/右移）
- 相同超参、无逐机调参 → 全部 100% 验证准确率

### 3.3 Loopy BP 实测（loopy）

| 图结构 | 变量数 | 环数 | 收敛率 | Avg KL | Avg MAE |
|--------|--------|------|--------|--------|---------|
| Triangle | 3 | 1 | 100/100 | 0.000045 | 0.002091 |
| Square | 4 | 1 | 100/100 | 0.000002 | 0.000382 |
| Dating graph | 5 | 1 | 100/100 | 0.000102 | 0.003590 |
| Two loops | 4 | 2 | 100/100 | 0.000086 | 0.003111 |
| QBBN chain | 6 | 1 | 100/100 | 0.000021 | 0.001055 |

500 次试验全部收敛。最差 KL 0.000102——Bethe 近似在这些图结构上"实际上精确"。

## 四、与我们体系的三重映射

### 4.1 与 NoFreeChecker 的收敛

| 本文概念 | NoFreeChecker 对应 |
|---------|-------------------|
| 有限概念空间 = 有限验证器 | NoFreeChecker §6.1 固定集一致性协议 |
| model-intrinsic verifier 可信度最低 | 本文：ungrounded LLM 的验证无定义 |
| verifier 被优化会失效 | 本文：无 grounding 的"正确"本身无定义 |
| Proxy gain 协议 | 本文的 grounded vs ungrounded 区分 |

**三份独立收敛**：昨日《为不信任》"模型本身是威胁"→《NoFreeChecker》"model-intrinsic 最低"→本文"无概念空间 = 幻觉结构性"。三个不同方向（安全架构/验证理论/形式化证明）指向同一结论。

### 4.2 对 Hermes Evals 体系的映射

| 本文定理 | 我们的实践 |
|---------|-----------|
| 有限概念空间需要有限验证器 | golden set = 我们的有限验证器（23 篇固定集 + G1-G6 检查） |
| 无 grounding = "正确"无定义 | 笔记内容质量判不了（G1-G6 只判格式/上线/出处）——正是放弃项，因为内容质量需要概念空间 |
| Corollary 4.1 幻觉需要 ungroundedness | 我们让 LLM 判内容质量 = 在 ungrounded 空间问"正确吗"——结构上不可能精确 |
| 树结构精确 BP | 笔记 → 出处 → 线上验证的链式验证是树结构（每个检查节点只有一条上游） |

**诚实自检**：我们的 golden set 门禁只覆盖"有限概念空间"的格式部分——内容深度的"概念空间"我们没有也不应该用 LLM 建（因为 LLM 本身是 ungrounded 的）。用户审查 = 唯一的 grounded verifier。

### 4.3 对 CDTDS 的映射

| 本文概念 | CDTDS 映射 |
|---------|-----------|
| grounding = 概念对应真实世界 | CDTDS 的"设计对象对应真实零件/适航条款" |
| BP 权重 = 精确推理 | 设计规则链 = 树结构因子图 → 设计推论可验证 |
| ungrounded = "正确"无定义 | 无对应适航条款的设计决策 = 无法验证合规性 |
| 有限概念空间 | 适航的 MC0-MC9 验证方法 = 有限验证器 |

## 五、批判性审视

1. **Sigmoid 假设是强约束**：论文标题"Transformers are Bayesian Networks"严格只在 sigmoid 激活下成立。主流 LLM（GPT/Claude/Gemini）用 GELU/ReLU——论文 §10.4 论证"兼容但不等同"，但标题的"are"在 ReLU 情况下是降级的。**"Compatibility is not identity"是论文自己说的**。
2. **Lean 证明的依赖链**：六个 Lean 仓库的证明依赖 Coppola 自己的 QBBN 定义 [2]——QBBN 是作者的先前工作，其自身的正确性假设未被独立验证。形式化证明的力量 = 依赖公理的力量。
3. **Loopy BP 的 500 次试验规模有限**：五种图结构 × 100 次随机参数，覆盖了简单环但未覆盖深层密集环——论文 §10.5 诚实承认"当前缺乏收敛理论保证"
4. **概念数 2n² 的界限**：这是上界不是下界——实际概念空间可能远小于 2n²（许多 routing key 不对应任何 grounded 概念）
5. **Turing 完备性 ≠ 实际能力**：§5 证明存在权重可模拟任意 TM，但不意味着训练出的权重有此能力——存在性和可达性是不同的
6. **"幻觉不是 bug"的论证力**：§9.4 的逻辑链（有限验证器 → 有限概念 → 概念外无意义）对**有限计算系统**成立，但人脑也是有限系统却能做"有意义"的推理——这暗示 grounding 的定义可能比论文给出的更宽

## 六、金句提取

> "Transformers are Bayesian networks. Not approximately. Not under certain training conditions. Not as a useful analogy. By architecture, for any sigmoid weights, provably and formally."

> "Hallucination is not a bug that scaling can fix. It is the structural consequence of operating without concepts."

> "The architecture that has won empirically across modern AI is exactly the architecture that the analysis of reasoning already required."

> "Gradient descent did not discover something new. It rediscovered the structure that was always there."

> "Compatibility is not identity."（Sigmoid vs ReLU）

> "Grounding is what makes the question 'is this output correct?' answerable. Without it, there is no fact of the matter."

> "Calculemus."（让我们计算——Leibniz 1670s 的愿景，2026 年用 Transformer + Lean 实现）

## 七、局限性

1. 本笔记基于 web_extract 全文 76KB 精读——数学证明步骤未逐行验证 Lean 源码（六个仓库未 clone）
2. QBBN [2] 是作者先前工作，其定义的合理性未独立核实
3. 实验数字（MAE 0.000752 / 500 次收敛 / 100% TM 精度）为论文自报
4. 第四五章体系映射为本笔记扩展，非论文原文论述
5. Sigmoid vs ReLU 的"精确 vs 兼容"区分对主流 LLM（GELU/ReLU）的实际含义需要更多实验确认

## 出处标注

| 章节 | 来源类型 |
|------|---------|
| 一至三 | **论文原文忠实还原**（76KB 全文精读，定理/实验/数字逐条核对） |
| 四 | **体系映射**（本笔记扩展，与 NoFreeChecker/为不信任/CDTDS 交叉） |
| 五 | **批判性审视**（本笔记扩展） |

## 相关笔记

- [贝叶斯与神经网络世纪和解-BBT两阶段配方](./2026-09-01-贝叶斯与神经网络世纪和解-BBT两阶段配方与人脑偏爱简单.md) — 贝叶斯×神经网络另一条线
- [RAG技术演进路径-五代全景](./2026-08-06-RAG技术演进路径-五代全景.md) — 幻觉治理工程侧
- [SKILL.state长程Agent状态架构](./2026-09-01-SKILL.state长程Agent状态架构-16倍Token削减与准确率反升.md) — 前向即推断的架构含义
