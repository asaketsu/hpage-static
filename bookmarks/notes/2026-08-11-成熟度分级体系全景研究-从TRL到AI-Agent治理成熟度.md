# 成熟度分级体系全景研究 — 从 TRL 到 AI Agent 治理成熟度的四套框架对比

> **来源**：多源研究综合（Sema4.ai / appliedAI / arXiv AAGMM / NASA TRL）
> **发布日期**：2026-08-11
> **标签**：成熟度模型、AI Agent 治理、TRL、CMMI、企业 AI 能力评估

---

## 一句话定义

> **成熟度分级体系的核心功能是"把模糊的能力变成可衡量的阶梯"**——从 NASA 的 TRL 1-9（技术成熟度），到 CMMI 的 5 级过程成熟度，到 2026 年 AI Agent 的 5 级治理成熟度（AAGMM），所有框架共享同一个底层逻辑：**渐进能力（每级建立在前一级之上）+ 可衡量的结果差异（高级别产出显著优于低级别）**。

---

## 一、四套主流成熟度框架对比

| 框架 | 领域 | 级数 | 来源 | 核心评估对象 |
|------|------|------|------|------------|
| **TRL** | 技术/硬件 | 1-9 | NASA 1995 | 单项技术从原理到部署的成熟度 |
| **CMMI** | 软件工程过程 | 1-5 | ISACA 2018 | 组织的开发过程规范性 |
| **Sema4.ai AI Maturity** | 企业 AI | 5 级 | Sema4.ai 2026 | 组织 AI 嵌入深度（5 支柱×5 阶段） |
| **appliedAI Framework** | 企业 AI（欧洲） | 4 级 | appliedAI 2026 | 9 维度组织 AI 能力 |
| **AAGMM** | AI Agent 治理 | 5 级 | arXiv 2604.16338 | Agent 生态治理能力（12 域×5 级） |

---

## 二、NASA TRL（Technology Readiness Level）— 技术成熟度鼻祖

### 9 级定义

| TRL | 名称 | 含义 |
|-----|------|------|
| 1 | Basic Principles Observed | 基本原理观察/报告 |
| 2 | Technology Concept Formulated | 技术概念形成 |
| 3 | Experimental Proof of Concept | 实验性概念验证 |
| 4 | Technology Validated in Lab | 实验室验证 |
| 5 | Technology Validated in Relevant Environment | 相关环境验证 |
| 6 | Technology Demonstrated in Relevant Environment | 相关环境演示 |
| 7 | System Prototype Demonstration in Operational Environment | 运行环境原型演示 |
| 8 | System Complete and Qualified | 系统完成并鉴定 |
| 9 | Actual System Proven in Operational Environment | 实际系统验证 |

### TRL 的衍生框架

| 框架 | 全称 | 用途 |
|------|------|------|
| **MRL** | Manufacturing Readiness Level | 制造成熟度 |
| **SRL** | System Readiness Level | 系统集成成熟度（结合各子系统 TRL） |
| **IRL** | Integration Readiness Level | 集成成熟度 |
| **CRL** | Commercial Readiness Level | 商业化成熟度 |
| **MLTRL** | ML Technology Readiness Level | ML/AI 系统成熟度（Nature Communications 2022） |

> **TRL 核心**：子系统 TRL 的最低值决定系统整体 TRL。MLTRL 扩展到数据管线、模型、软件模块的组合评估。

---

## 三、CMMI（Capability Maturity Model Integration）— 过程成熟度

| 级别 | 名称 | 特征 |
|------|------|------|
| 1 | Initial | 混乱、英雄主义、不可重复 |
| 2 | Managed | 有基本项目管理、可重复成功 |
| 3 | Defined | 过程标准化、组织级标准存在 |
| 4 | Quantitatively Managed | 用数据和统计管理过程 |
| 5 | Optimizing | 持续改进、关注过程优化 |

> **CMMI 对 AI 的启示**：AAGMM 和 Sema4.ai 都明确借鉴了 CMMI 的"渐进能力+结果导向"设计。

---

## 四、Sema4.ai AI 成熟度模型（2026）— 5 支柱 × 5 阶段

### 5 支柱

| 支柱 | 范围 |
|------|------|
| **Strategy & Alignment** | AI 项目与业务目标对齐、高层赞助 |
| **Data & Integration** | 数据治理、集成架构、跨系统连接 |
| **Technology & Tooling** | 平台能力、开发工具、运维 |
| **Talent & Culture** | 技能发展、变更管理、AI 增强文化 |
| **Governance & Risk** | 安全、合规、伦理、审计追踪 |

### 5 阶段

| 阶段 | 名称 | 特征 | 典型状态 |
|------|------|------|---------|
| 1 | **Ad hoc** | 无协调的零散实验 | 各团队 shadow IT，无标准化 |
| 2 | **Opportunistic** | 孤立成功案例，难以复制 | 技术债积累，部门各自为政 |
| 3 | **Systematic** | 建立 AI CoE、路线图、治理框架 | 关键过渡：从实验到企业能力 |
| 4 | **Integrated** | AI 嵌入全组织，语义数据模型 | 业务用户自主构建 Agent |
| 5 | **Optimized** | Agent 驱动自主运营，持续创新 | 7×24 端到端流程，仅异常升级人工 |

> **行业现状**：MIT 数据显示 95% 的 AI 项目在全面投产前停滞。大多数企业处于 Stage 2-3 之间。

### Sema4.ai 的关键洞察

1. **AI 开发 ≠ AI 成熟度** — 技术上精巧的自定义 Agent 如果仍然是孤立的、无治理的、依赖稀缺开发者的，组织成熟度依然很低
2. **角色分离是 Stage 4 的前提** — 业务用户用自然语言构建 Agent，开发者专注于企业集成
3. **最成功的用例有三个共同特征**：① 传统 RPA/自动化已失败 ② 消耗大量运营成本/资源 ③ 有明确的 SLA 但当前未达标

---

## 五、appliedAI 成熟度框架（2026）— 9 维度 × 4 级

### 9 维度

| 维度 | 范围 |
|------|------|
| AI Ambition & Steering | 战略、治理、合规、价值衡量 |
| Use Cases | 发现、优先级排序、产品思维、流程集成 |
| Organization | 运营模型、角色、问责 |
| Expertise | 技能、赋能、知识管理 |
| Culture | 采用、责任、变革准备度 |
| Data | 策略、质量、访问、隐私 |
| Technology | 平台、架构、工具、安全设计 |
| AI Ecosystem | 厂商、模型、合作伙伴、IP、FinOps |
| Execution | 交付、生命周期、LLMOps/MLOps、评估、运维 |

### 4 级

| 级别 | 名称 | 特征 |
|------|------|------|
| L1 | **Experimenter** | 活跃实验中；治理萌芽 |
| L2 | **Practitioner** | 选定领域运营使用；可重复交付初现 |
| L3 | **Professional** | 规模化企业能力；治理嵌入；价值可衡量 |
| L4 | **Shaper** | AI 作为组织 DNA；持续优化；生态影响力 |

### 欧洲 187 家企业实测基准

| 发现 | 数据 |
|------|------|
| **最强维度** | Culture, Expertise, Ambition（平均 1.92） |
| **最弱维度** | Use Cases, Technology, AI Ecosystem（平均 1.48） |
| **意图-执行差距** | 0.44 分（近半个成熟度级别） |
| **L1 占比** | ~60% 的组织仍停留在实验者级别 |
| **L3+ 占比** | 仅 9% 达到 Professional 或 Shaper |
| **Culture 方差最高** | 1.07（有 AI 正向文化 vs 抵触文化） |
| **Execution 方差最低** | 0.48（所有组织都普遍困难） |

### appliedAI 的四大假设

1. **Agent 是阶跃变化，不是增量** — 从助手（响应 prompt）到 Agent（追求目标），AI 从工具变成劳动力
2. **Context Engineering 成为核心能力** — 不是 prompt engineering，而是系统性为 Agent 提供正确的信息、正确的结构、正确的时间
3. **端到端流程重设计不再可选** — 局部优化 10-20%；流程重设计 10x+
4. **适应速度是新的竞争护城河** — 不是采用（adopt）而是适应（adapt）

---

## 六、AAGMM（Agentic AI Governance Maturity Model）— 5 级 × 12 域

> 来源：arXiv 2604.16338，基于 NIST AI RMF 1.0 和 ISO/IEC 42001。750 次模拟验证，所有级别差异 p < 0.001。

### 5 级治理成熟度

| 级别 | 名称 | 特征 | 活跃控制措施 | 预期结果 |
|------|------|------|------------|---------|
| L1 | **Ad-hoc** | 无正式治理；Agent 无协调部署 | 无 | 高蔓延；不可控成本 |
| L2 | **Reactive** | 基础注册表；事件触发治理 | 注册表、事件响应 | 减少盲区 |
| L3 | **Defined** | 正式策略；集中目录；RBAC；HITL | 注册+IAM+可观测+策略+HITL+审计+风险分级 | 蔓延遏制；可衡量合规 |
| L4 | **Managed** | 定量指标；自动化执行 | L3 全部 + 自动策略+蔓延检测+生命周期 | 主动风险降低 |
| L5 | **Optimized** | 自我改进；预测性蔓延；治理即代码 | L4 全部 + 持续改进+预测+GaC | 最大价值；最小开销 |

### 12 治理域（按 4 组）

| 组 | 域 | 应对的蔓延模式 |
|----|-----|-------------|
| **生命周期与身份** | GD-01 Agent 生命周期管理、GD-02 身份与访问控制 | SP-03 孤儿 Agent、SP-04 权限蔓延 |
| **运行时治理** | GD-03 可观测性、GD-04 策略执行、GD-05 数据治理、GD-06 人工监督 | SP-02 影子 Agent、SP-05 未监控委派 |
| **组合治理** | GD-07 蔓延遏制、GD-08 审计合规、GD-09 Agent 间协调、GD-10 风险分级 | 全部 |
| **改进与韧性** | GD-11 事件响应、GD-12 持续改进 | 全部 |

### 5 种 Agent 蔓延模式

| ID | 模式 | 定义 | 业务影响 |
|----|------|------|---------|
| SP-01 | 功能重复 | 多个团队做相同任务的 Agent | 算力浪费 2-5x，输出不一致 |
| SP-02 | 影子 Agent | 未经 IT 治理部署的 Agent | 安全盲区、合规违规 |
| SP-03 | 孤儿 Agent | 目的已过期但仍在运行的 Agent | 持续成本零价值、安全面扩大 |
| SP-04 | 权限蔓延 | Agent 累积超出原始范围的权限 | 权限提升、监管不合规 |
| SP-05 | 未监控委派 | 多 Agent 链无可见性或授权追踪 | 问责丢失、级联失败 |

### 蔓延成本公式

```
C_sprawl = C_redundancy + C_security + C_compliance + C_operational + C_opportunity
```

> **核心结论**：治理是投资，不是开销——存在一个成熟度级别使净业务价值最大化。

### 模拟实验关键数据

| 指标 | L1→L5 变化 | 最大跳变点 |
|------|-----------|-----------|
| 蔓延指数（SI） | 0.520 → 0.028（↓94.6%） | L3→L4（自动蔓延检测 GD-07 激活） |
| 风险事件率（RIR/千次） | 59.08 → 2.05（↓96.5%） | L2→L3（策略执行+访问控制激活） |
| 有效任务完成率（ETCR） | 0.699 → 0.930（↑33.0%） | L2→L3 |
| 委派安全率（DSR） | 0.602 → 0.992（↑60.2%） | L2→L3 |
| 净业务价值（NBV） | 0.625 → 0.944（↑51.0%） | 持续单调上升 |

> **三个实践结论**：
> 1. **L3 是最低可行治理** — Defined 级别的 RBAC+HITL+审计是生产环境的底线
> 2. **自动蔓延检测是最高杠杆** — L3→L4 的 SI 下降 74.4%
> 3. **L5 交付自动化红利** — 治理即代码实现最大价值+最小开销

---

## 七、四套框架的交叉映射

| TRL | CMMI | Sema4.ai | appliedAI | AAGMM | 统一描述 |
|-----|------|----------|-----------|-------|---------|
| 1-3 | 1 Initial | 1 Ad hoc | L1 Experimenter | L1 Ad-hoc | 概念/实验/无协调 |
| 4-5 | 2 Managed | 2 Opportunistic | L1-L2 | L2 Reactive | 实验室验证/孤岛成功 |
| 6-7 | 3 Defined | 3 Systematic | L2 Practitioner | L3 Defined | 系统化/策略化/可重复 |
| 8 | 4 Quant. Managed | 4 Integrated | L3 Professional | L4 Managed | 量化管理/全组织嵌入 |
| 9 | 5 Optimizing | 5 Optimized | L4 Shaper | L5 Optimized | 实际部署验证/持续优化/自主 |

### 统一规律

1. **所有框架都是渐进能力模型** — 每级建立在前一级之上，不能跳级
2. **L3/Stage 3 是关键转折点** — 从实验到生产、从孤岛到系统化
3. **最高级都指向自主/自我改进** — Optimizing/Optimized/Shaper/L5
4. **评估对象不同但结构相同** — TRL 评技术、CMMI 评过程、AI 模型评组织/治理

---

## 八、Gartner 七支柱模型（补充）

Gartner 的五级 AI 成熟度模型覆盖七个支柱：

| 支柱 | 范围 |
|------|------|
| Strategy | 战略 |
| Product Portfolio | 产品组合 |
| Governance | 治理 |
| Engineering | 工程 |
| Data | 数据 |
| Operating Models | 运营模型 |
| People and Culture | 人才与文化 |

> Gartner + McKinsey（十二项扩展实践 × 六维度）+ Deloitte + Forrester 各有变体，但核心结构与上述四套一致。

---

## 九、结合 Hermes Agent 架构的成熟度自评

### Hermes 在各框架中的位置

| 框架 | 评估 | 理由 |
|------|------|------|
| **TRL** | TRL 7-8 | 系统原型在运行环境中演示（Jetson+飞书+多平台），持续运行中 |
| **CMMI** | Level 3 Defined | Skill 系统=过程标准化；AGENTS.md=组织级标准；但缺乏定量指标 |
| **Sema4.ai** | Stage 3-4 Systematic→Integrated | AI CoE（MeowBot 团队）存在；Agent 嵌入日常工作流；但跨领域整合仍在进行 |
| **appliedAI** | L2-L3 Practitioner→Professional | Use Cases 活跃（笔记/项目/cron/量化）；Execution（LLMOps）在建设中 |
| **AAGMM** | L2-L3 Reactive→Defined | 有注册表（Skill 索引）和事件响应（error-case-library），但 RBAC/HITL 不完善 |

### Hermes 到 L4/L4+ 的差距

| 维度 | 当前 | 目标 | 需要补齐 |
|------|------|------|---------|
| **可观测性** | 日志+session_search | 定量仪表盘 | observability-dashboard Skill 完善 |
| **蔓延检测** | 手动 skill-review | 自动扫描重复/孤儿 Skill | skill-review 自动化 |
| **策略执行** | AGENTS.md 规则 | policy-as-code | 策略可程序化验证 |
| **人工监督** | [ACTION REQUIRED] 标记 | HITL 断点+审批流 | 统一的 HITL 框架 |
| **审计追踪** | terminal 日志 | 结构化审计日志 | 审计日志标准化 |
| **定量管理** | 定性判断 | NBV/ETCR/RIR 等指标 | 定义并采集指标 |

---

## 十、学习进化借鉴点

| 洞察 | 可借鉴到 Hermes | 优先级 |
|------|----------------|--------|
| **L3 是最低可行治理** | 确保所有 Skill 有 RBAC+审计 | 高 |
| **自动蔓延检测是最高杠杆** | 自动扫描重复/冲突/孤儿 Skill | 高 |
| **成熟度不是均匀爬升** | 不同维度可以不同级别 | 高 |
| **"意图-执行差距"是结构性问题** | Culture 强≠Execution 强 | 高 |
| **Agent 蔓延 5 模式** | 对照检查 Hermes Skill 生态 | 高 |
| **治理是投资不是开销** | 投入治理 → NBV 最大化 | 中 |
| **Context Engineering > Prompt Engineering** | 已在实践（L1/L2/L3 加载） | 中 |
| **适应速度是护城河** | 快速迭代 > 完美实现 | 中 |
| **MLTRL 评估 AI 系统成熟度** | 每个 Skill/组件的 TRL 评级 | 中 |

---

## 十一、趋势判断

1. **成熟度模型正在从"通用 AI"细化到"Agent 治理"** — AAGMM 是第一个专门针对 Agent 蔓延的实证框架
2. **L3 成为生产门槛共识** — Sema4.ai/appliedAI/AAGMM 都将第三级定义为"可生产使用"的起点
3. **自动蔓延检测（GD-07）是 L3→L4 的最大跳变** — 74.4% 的 SI 降幅集中在此
4. **治理即代码（GaC）是 L5 的标志** — 从手动策略到代码定义+自动执行+预测性预防
5. **95% 的 AI 项目在全面投产前停滞**（MIT 2025） — 成熟度差距是结构性的
6. **Agent 从工具变为劳动力** — 治理问题从"输出好不好"变为"该不该允许这个动作"
7. **成熟度评估需要多维度同时** — 按 team/department/function/location 分别评估

---

## 关联分析

- **与 Managed Agent 课件**：三件套（Agent/Environment/Session）的成熟度直接映射到 Sema4.ai 的 Stage 3-4
- **与 Hermes 架构**：Hermes 目前处于多个框架的 L2-L3/Stage 3 位置，向 L4 迈进
- **与 enterprise-agent-governance Skill**：AAGMM 的 12 域为治理 Skill 提供了结构化参考
- **与 observability-dashboard Skill**：定量指标（NBV/ETCR/RIR）定义了仪表盘应该展示什么
- **与 skill-review Skill**：自动蔓延检测（GD-07）是 skill-review 的目标形态
- **与 Context Engineering 四大支柱**：appliedAI 明确提出 Context Engineering 为核心能力
- **与 CodexLoom**：Agent Team 的长期责任分配需要 AAGMM L3+ 的治理支撑

---

*笔记创建：2026-08-11 · 来源：Sema4.ai / appliedAI / arXiv AAGMM / NASA TRL 综合研究*

## 相关笔记
- [工程应用成熟度分级标准实操手册-TRL-MRL-IRL-SRL评估准则与里程碑门禁](2026-08-11-工程应用成熟度分级标准实操手册-TRL-MRL-IRL-SRL评估准则与里程碑门禁.md)
- [工业成熟度等级划分体系全景](2026-06-11-工业成熟度等级划分体系全景.md)
