# DCPM 双过程记忆架构 — 腾讯的昼夜分工与 supersedes 链设计

#Agent #memory #self-evolution #Hermes

> 嗅探学习 | 2026-10-07 | 来源: arXiv 检索
> 前序笔记: [2026-10-06-Agent记忆2026-自进化与基准](./2026-10-06-Agent记忆2026-自进化与基准.md)

## 内容整理

**核心命题**（Tencent LLM Dept, arXiv:2606.09483）：现有一切 Agent 记忆系统（Mem0/Zep/长上下文）都把"记忆=检索问题"，把信念修正、因果耦合、跨域抽象压进同一个检索面，于是在"隐式个性化推理"（需推理用户如何演化）上集体翻车。DCPM 的答案是把记忆按**认知能力层级**重组，并用双过程理论（Kahneman System 1/2）做架构分工。

**能力层级（五层，自下而上）**：
1. 原始输入（vector store 兜底，零丢失）
2. 原子事实 + 身份项（identity items：长期用户属性）
3. **supersedes 双向链**（信念修正轨迹：SUPERSEDE 时不删旧条目，双向指针串成链，读时一次命中可遍历整条演化弧——含 embedding 相似度通常漏掉的"因果中间态"）
4. 域内 schemas（行为规律）+ intentions（潜在关切，可主动关怀）
5. 跨域 core schemas（行为相似但语义距离远的 schema 对，抽象成更高层核心图式）

**System 1 白天写手（同步，秒级预算）四步**：①raw persist（LLM 调用前先落盘原始输入，下游失败不丢内容）②抽取 LLM 单次调用产出 identity+facts（带 type/topic/salience/timestamp）③reconcile LLM 对每条新项判 ADD/SUPERSEDE/UPDATE（精确重复静默丢弃）④批量嵌入 upsert + supersedes 双指针。

**System 2 夜间引擎（异步，数十秒预算）三阶段**：
- Phase 1 无 LLM 预处理：事实分诊（未入 schema 的）→ 两阶段 DBSCAN 聚类（语义嵌入粗聚+细分过大簇）
- Phase 2 归纳 agent（每簇一次调用，四工具：create_schema / create_intention / add_evidence / add_edge），图增量演化非重建
- Phase 3 跨域扫描器：每个 schema 生成行为描述（如"沉没成本后加码"）嵌入行为-认知空间，与语义空间比对——**行为相似但语义距离远=碰撞**，union-find 聚合后 LLM 归纳 core schema

**读路径零 LLM**：向量检索 + supersedes 链遍历 + evidence_vdb_ref 反查图节点，延迟由向量搜索主导。

**主表硬数据**（deepseek-v4-flash / kimi-2.5 双列，准确率%）：

| 系统 | PersonaMem 32k | LongMemEval S | PersonaMem-v2 32k |
|---|---|---|---|
| B1 长上下文 | 72.07 / 77.59 | 88.43 / 80.61 | 50.82 / 58.46 |
| B2 Mem0 | 69.07 / 65.23 | 56.84 / 48.87 | 42.53 / 41.25 |
| B3 Zep/Graphiti | 58.93 / 64.21 | 67.83 / 62.35 | 39.54 / 38.27 |
| DCPMlite（仅S1） | 69.15 / 74.32 | 84.73 / 85.81 | 46.85 / 54.10 |
| DCPMfull（S1+S2） | 70.46 / 76.73 | 85.17 / 86.14 | 49.36 / 59.30 |

三个关键读数：①Mem0 在 LongMemEval 上 56.84 比裸长上下文 88.43 还低 31.6 分——记忆系统做得不好反而不如不做；②System 2 增益在 PersonaMem-v2（隐式推理）最大、span 召回最小，与双过程假设的预测精确吻合；③评测用 no-think 协议，比 CoT 评测更贴近部署现实。

**实现细节**：Qdrant HNSW（M=16 ef=64）+ bge-m3 1024 维 + dense/sparse 混合（BM25）检索；抽取用 deepseek-v4-flash 或 kimi-2.5 no-think；碰撞阈值在 PersonaMem-v2 留出集上调。

## 查询拓展

- PersonaMem-v2 是 2026 最严苛记忆基准（前沿模型仅 37-48%），可作为 Hermes memory-refiner 的对标基准——当前 Hermes 三级记忆（L1/L2/L3）在"隐式偏好推理"上无任何测评。
- supersedes 链与 memorygraph MCP 的 relationship 类型对齐成本：现有 create_relationship 是否支持双向 supersede/supersededBy 语义，值得查一次 schema。
- 未决：DCPM 的 nighttime engine 每晚跑全量聚类，记忆库到 10 万条事实级的聚类成本曲线论文未给；两阶段 DBSCAN 的参数（ε₁/ε₂）对中文语料的迁移性未验证。
- 检索关键词备忘：`supersedes chain belief revision agent memory` / `dual process memory day writer night consolidation` / `PersonaMem-v2 implicit preference`。

## 归纳总结

一页速查：**DCPM = 一个"不删除"原则 + 一次昼夜分工**。不删除=信念演化全程可回溯（读时一次命中拉整条修正链）；昼夜分工=白天只做秒级写入（在线延迟友好），夜间做无 LLM 聚类+LLM 归纳（成本移到闲时）。增益不对称性（隐式推理≫显式召回）证明：**System 2 的钱花在抽象层，不在检索层**。

| 设计点 | DCPM 选择 | 反例（业界常见） |
|---|---|---|
| 信念修正 | 双向 supersedes 链，不删旧 | update-in-place（丢失演化弧） |
| 写入时机 | 显式 add_memory 触发 | 每轮对话都写（噪声+成本） |
| 抽象时机 | 夜间异步批处理 | 白天同步做（延迟爆炸） |
| 跨域发现 | 行为相似×语义距离远的碰撞对 | 纯语义聚类（同域冗余） |
| 读路径 | 零 LLM（向量+指针遍历） | 检索后 LLM 重写（慢+贵） |

## 趋势判断

2026 记忆系统的竞争轴已从"检索分"转向"时间+抽象"：检索层基本饱和（LongMemEval 88+），PersonaMem-v2 的隐式推理（49-59%）才是新战场。DCPM、EverMemOS、SEARL、Experience compression spectrum 在同一季度涌现，共同信号是**记忆中间件从"存取设施"升格为"认知架构"**。判断：supersedes 链（可回溯修正）会像 2025 年的"分层记忆"一样成为下一批系统的标配组件；夜间异步抽象引擎会与 sleep-time compute 路线合流。

## 关联分析

- 与 [2026-10-06-Agent记忆2026-自进化与基准](./2026-10-06-Agent记忆2026-自进化与基准.md)：该篇梳理了 MemSkill/MemEvolve/Evo-Memory 谱系，DCPM 补上了缺失的"信念修正可回溯"维度——前者管"经验→技能"，DCPM 管"事实→图式"，两者在能力层级上互补。
- 与 [2026-10-03-EvolveMem检索自进化](./2026-10-03-EvolveMem检索自进化与Agent记忆中间件化.md)：EvolveMem 把检索策略本身作为进化对象，DCPM 把抽象引擎作为异步组件——同为"记忆中间件化"但进化对象不同；DCPM 的 no-LLM 读路径是对 EvolveMem"检索也要 LLM"路线的反驳。
- 与 [2026-10-05-MemSkill记忆技能自进化](./2026-10-05-MemSkill记忆技能自进化Agent.md)：MemSkill 的"技能银行"与 DCPM 的 schema 层同构——都是把行为规律固化为可复用单元；差异在 MemSkill 可执行、DCPM schema 仅用于检索增强。
- 与 Hermes 自身的三级记忆（L1 MEMORY.md / L2 short-term / L3 topics）：DCPM 层级几乎一一对应（L1≈identity+core schemas，L2≈raw+facts，L3≈域内 schemas），**Hermes 缺的是 supersedes 链**——USER.md 的"决策风格"条目多次被用户行为推翻重写，但演化过程不可回溯，导致"为什么 9 月的结论 10 月被推翻"无法回答。
- 与 Hermes 的 auto-dream-nightly cron：DCPM System 2 是 auto-dream 的学术定形——Hermes 已有"夜间异步"骨架，缺的是"无 LLM 聚类前置+行为-语义双空间碰撞检测"两个组件。

## 出处

- DCPM: Memory Beyond Recall — https://arxiv.org/abs/2606.09483（Tencent, 2026-06）
- PersonaMem-v2 基准 — https://arxiv.org/abs/2510.09600（Jiang et al., 前沿模型 37-48%）
- LongMemEval — https://arxiv.org/abs/2420.11952（Wu et al. 2024）
- Mem0 基线数据 — https://arxiv.org/abs/2504.19413

## 指南分析

**对 Hermes 记忆栈的可落地改进**（按成本排序）：
1. **P0（零成本，立即可做）**：USER.md/MEMORY.md 条目改写时保留 supersedes 标记——旧结论不删，标注"被 <日期><新证据> 修正"。memory 工具的 replace 操作已天然支持（旧文本可并入新条目尾部），缺的只是约定。
2. **P1（低成本）**：auto-dream-nightly 增加 Phase 1 式无 LLM 预处理——先用脚本对 L2 short-term 过期条目做关键词聚类统计，只把"簇≥3 条"的主题送 LLM 归纳，砍掉现在全量喂 LLM 的 token 消耗。
3. **P2（中成本）**：memorygraph MCP 增加双向 SUPERSEDES 关系类型，USER.md 画像条目与其推翻来源（session 证据）建链——回答"这个结论从哪来、被谁改过"。
4. **对标动作**：用 PersonaMem-v2 的题型（隐式偏好推理）构造 10 条 Hermes 私有测试集，注入 memory-refiner 的验收——当前记忆栈对"用户偏好在两个域的隐性关联"（如"训练保守偏好"+"消费决策保守"）零覆盖。
5. **反例警示**：Mem0 在 LongMemEval 上比裸长上下文低 31.6 分——记忆系统若只做"存取"不做"抽象"，负收益是完全可能的。Hermes 加记忆功能前先问：这条信息 System 2 能抽象出什么。

## 拓展应用推荐

- supersedes 链迁移到 error-case-library：每个 EC 案例的"根因结论"被后续案例推翻时建链，形成"误诊史"——排查时能看到"这个症状 3 次被误判为什么"，避开重复误诊。
- DCPM 碰撞检测迁移到 skill-review：两个 skill 的"行为描述"（做什么）相似但"语义域"（属于什么类别）不同=功能重复候选——比现在的名称/标签匹配更准地发现待合并 skill。
- 跨域 core schema 思想迁移到周论文选题：单域笔记（DUCK 训练/Agent 记忆/量化）各自归纳"域内 schema"，周综合时找"行为相似但域不同"的规律对（如"验证器是最弱环节"在三个域独立出现）——这正是 9 月元趋势"工程知识显式契约化"的发现方法论。

## 相关笔记
- [2026-09-30-Agent记忆不是搜索问题-时序图谱六类型](./2026-09-30-Agent记忆不是搜索问题-时序图谱六类型.md) — 同一命题的先声："记忆≠检索问题"，DCPM 用能力层级+双过程给出了架构答案
- [2026-10-06-Agent记忆2026-自进化与基准](./2026-10-06-Agent记忆2026-自进化与基准.md) — 直接前序：领域全景与三大基准，DCPM 是其中"信念修正"空白的具体解法
- [2026-10-03-EvolveMem检索自进化与Agent记忆中间件化](./2026-10-03-EvolveMem检索自进化与Agent记忆中间件化.md) — 检索侧自进化 vs DCPM 写入侧双过程分工，互补的两半
- [2026-10-04-SSGM进化记忆治理框架](./2026-10-04-SSGM进化记忆治理框架.md) — 记忆治理/淘汰视角，与 supersedes 链（不删旧条目）形成对照设计
