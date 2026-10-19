# ProvenanceGuard: MCP-Based LLM Agents 的源感知事实性验证

**arXiv ID**: 2606.18037 | **日期**: 2026-06-17 | **领域**: AI / 多智能体系统 / RAG评估

## 元数据

- 标题: ProvenanceGuard: Source-Aware Factuality Verification for MCP-Based LLM Agents
- 领域: cs.AI, cs.CL, cs.MA (多智能体系统)
- 核心问题: MCP工具调用场景下，LLM Agent回答的事实性验证不仅要看"是否被支持"，还要看"是否归因于正确的源"

## 核心问题与研究动机

**问题定义**: 当LLM Agent通过MCP调用多个工具（搜索、API、数据库、临床记录等）生成回答时，一个事实主张可能被某个源支持，但被错误地归因到另一个源。这种"跨源混淆"（cross-source conflation）是源盲验证器无法检测的。

**例子**: Agent回答"根据患者病历，empagliflozin降低了死亡率"。死亡率数据可能来自临床试验摘要，而非患者病历。源盲验证器看到 pooled evidence 会标记为"支持"，但源感知验证器应拒绝——归因错误。

**为什么重要**: 在数据敏感领域（医疗、企业），将患者记录事实归因到文献、或将文献事实归因到患者病历，可能导致误导性决策。

## 方法论（ProvenanceGuard Pipeline）

ProvenanceGuard是一个8阶段顺序验证管道：

**1. Trace Interface（追踪接口）**
- 输入: 工具调用追踪对象，包含 `(tool_id, source_id, text)` 三元组
- 关键设计: 永不将证据对象合并为匿名上下文，保留source_id用于后续归因检查

**2. Atomic Claims Decomposition（原子主张分解）**
- 将回答分解为可验证的原子事实主张
- 保留数值、单位、日期、标识符等精确值
- 过滤通用安全声明（除非包含具体事实断言）

**3. Source Routing（源路由）**
- 对每个主张，用embedding计算与每个源centroids的cosine相似度
- 选择最高分源作为路由目标，记录top-2 margin
- Top-k路由用于多源场景

**4. Support & Alignment Check（支持度与对齐检查）**
- NLI（自然语言推理）判断主张与路由源的关系
- Token-alignment proxy作为辅助信号
- 比较声明的归因与路由源是否一致

**5. Calibrated Claim Decision（校准决策）**
- 使用RandomForest校准器整合路由、NLI、对齐、词汇特征
- 输出每主张的 verdict（supported/unsupported/contradicted/not-enough-evidence）
- 含block P/R/F1和source accuracy

**6. Attribution & Conflation Check（归因与混淆检查）**
- 独立检查 stated attribution vs routed source
- 检测源混淆（同一主题但错误源）

**7. Answer Gate（回答门控）**
- 综合所有主张 verdict，输出allow/block决策
- Block recall优先（fail-closed策略）

**8. Repair & Re-verification（修复与重验证）**
- 被block的回答通过RAG-style修订修复
- 修复后重新验证

## 关键实验结果

**数据集**: 281条医疗领域MCP-Agent追踪，含合成/去标识化患者记录和文献数据

**主评估（40条held-out追踪，361条主张，260条源可评估主张）**:

- Block F1: 0.802
- Block Recall: 0.993（极高，几乎不漏掉有问题的回答）
- Block Precision: 0.673
- Source Accuracy: 0.858
- Source+Relation Accuracy: 0.681

**多源基准（更难的59题扩展基准，263条提取主张）**:

- Block F1: 0.846（保持强劲）
- Source Accuracy: 0.503（显著下降）
- Source+Relation Accuracy: 0.229（精确归属极难）

**压力切片分析**:

- 图表+文献混合: Block F1 0.927, Src+Rel Acc 0.400
- 文献摘要vs精确引用: Block F1 0.941, Src+Rel Acc 0.778
- 同主题错误图表/患者: Block F1 0.813, Src+Rel Acc 0.127（最难场景）
- 计数/资源汇总: Block F1 0.800, Src+Rel Acc 0.179

**50个控制混淆探针**: 检测所有注入的归因交换，零保留错误归因

## 创新点分析

1. **首次将"源归属"作为独立评估维度**: 现有RAG评估（RAGAS、ALCE）关注"是否被支持"或"引用是否指向正确段落"，但不区分"支持源"vs"归属源"。ProvenanceGuard在MCP工具层实现claim-to-source ID追踪。

2. **MCP Trace Interface**: 定义标准化的 `(tool, source, text)` 追踪格式，保留工具级source ID，为离线验证器提供可追溯的证据链。

3. **校准器设计**: 使用RandomForest而非神经网络，输出可解释的特征权重，便于设置fail-closed操作点。

4. **两轴评估框架**: 支持检测（binary blocking）和源归属（source ownership）应分开报告——一个保守blocker可能支持检测很好但归属很差。

## 局限性与未来方向

- 仅评估单一医疗Agent栈，缺乏跨领域泛化
- 标签由LLM辅助生成，非完全人工标注
- Held-out split较小（40条追踪）
- 控制混淆探针是人工注入的，非自然分布
- 源+关系准确率在多源场景下显著下降（0.229），精确归属仍是开放问题

## 借鉴点（关联Hermes/Jetson/量化交易）

- **P1 可直接移植**: MCP追踪接口设计可直接用于Hermes Agent的工具调用追踪。当前Hermes调用外部工具（飞书API、搜索、数据库）时，可捕获完整的 `(tool, source, text)` 追踪，用于回答质量验证。
- **P1 可直接移植**: 原子主张分解+源路由模式可用于量化交易Agent——将交易决策分解为事实主张（"某股票RSI>70"），路由到数据源（行情API/技术指标计算），验证归因是否正确。
- **P2 需工程改造**: NLI+校准器需要embedding模型和分类器，Jetson Orin上可部署sentence-transformer + sklearn模型，但需量化优化以满足延迟要求。
- **P2 需工程改造**: 修复+重验证机制可用于Hermes的自动纠错——当检测到归因错误时，自动触发检索增强修订。
- **P3 暂不适用**: 医疗领域的跨源混淆探针设计对通用Agent场景需要重新设计（如量化场景的"数据来源混淆"探针）。

## 关联论文

- ALCE: 评估LLM生成答案的引用质量（最接近的现有任务，但在passage级别而非工具级）
- FActScore / MiniCheck / VeriScore: 细粒度事实一致性评估，但不保留claim-to-MCP-source ID
- Atomic Information Flow: 将工具输出、LLM调用、响应建模为原子信息流
- RAGAS: RAG忠实度评估框架


## 相关笔记

- [MCP 协议与 Agentic LLM 2025 趋势](../2026-04-23-MCP协议与Agentic-LLM-2025趋势.md)
