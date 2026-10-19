## 第四章 六大 Harness 架构模式在载具设计中的适配

基于 Anthropic、OpenAI、Cursor 的实践，以及载具设计的独特需求，本章提出六种 Harness 架构模式在载具设计中的适配方案。

### 4.1 Planner-Worker-Judge 三层分离

**来源**：Cursor 多 Agent 协作实践

**载具设计适配**：

```
┌──────────────────────────────────────┐
│  Planner Agent（总师 Agent）          │
│  • 解析设计需求，拆解为子任务          │
│  • 确定子任务依赖关系和执行顺序        │
│  • 分配学科（结构/气动/动力...）       │
│  • 全局约束管理（质量预算、进度）       │
└──────────────┬───────────────────────┘
               │ 派发任务
      ┌────────┼────────┐
      ▼        ▼        ▼
┌──────────┐┌──────────┐┌──────────┐
│ Worker 1 ││ Worker 2 ││ Worker N │
│ 结构设计  ││ 气动分析  ││ 系统集成  │
│ Agent    ││ Agent    ││ Agent    │
└────┬─────┘└────┬─────┘└────┬─────┘
     │           │           │
     └───────────┼───────────┘
                 ▼
┌──────────────────────────────────────┐
│  Judge Agent（评审 Agent）             │
│  • 多学科接口协调性检查                │
│  • 适航合规性综合评审                  │
│  • 质量预算闭环验证                    │
│  • 生成评审报告，建议修改              │
└──────────────────────────────────────┘
```

**实施要点**：
- Planner 掌握全局约束（质量预算、载荷分配），这是**不可逾越的硬约束**
- Worker 之间通过 Git 锁文件实现并发隔离（借鉴 Cursor 教训——20 Agent 并行时锁机制是关键）
- Judge 的评审标准必须**形式化**，不能依赖 LLM 的"直觉判断"

### 4.2 Generator-Evaluator 对抗（GAN-Style Loop）

**来源**：Anthropic 三篇 Harness 论文

**载具设计适配**：

```
┌─────────────────┐     ┌──────────────────────┐
│  Generator      │     │  Evaluator           │
│  (设计生成器)    │◄────│  (合规评审器)          │
│                 │     │                      │
│  • 读取设计需求  │────►│  • 检查物理可行性      │
│  • 调用工具生成  │反馈  │  • 校验适航合规性      │
│  • 输出设计方案  │     │  • 评估可制造性        │
│                 │     │  • 评分 + 修改建议     │
└─────────────────┘     └──────────────────────┘
```

**Anthropic V2 创新——Sprint Contract 在载具设计中的映射**：

每轮迭代前，Generator 和 Evaluator **自行协商验收标准**：

| 迭代轮次 | 验收标准（示例） | 评判依据 |
|----------|-----------------|----------|
| Sprint 1 | 最大应力 < 300 MPa | 初始估算，留裕度 |
| Sprint 2 | 疲劳寿命 > 40000 FH | 初步评估 |
| Sprint 3 | 疲劳寿命 > 60000 FH + Kt < 2.5 | 收紧至设计目标 |
| Sprint 4 | 全部适航条款通过 | 最终验收 |

**核心发现**：Agent 互相评估比自评估有效几个数量级（Anthropic 实验）。在载具设计中，这意味着"设计 Agent"和"审查 Agent"的对抗比单个 Agent 自检更可靠。

### 4.3 Coordinator Mode（主 Agent 当工头）

**来源**：Claude Code 的 Coordinator 架构

**载具设计适配**：

```
┌──────────────────────────────────────┐
│  Coordinator Agent（总师/PM Agent）    │
│  • 接收设计任务，分配给各学科 Worker    │
│  • 管理设计基线（当前有效的设计状态）    │
│  • 审批危险操作（材料替换、安全系数变更）│
└──────────────┬───────────────────────┘
               │ 通过"邮箱"请求/审批
      ┌────────┼────────┐
      ▼        ▼        ▼
  结构Agent  气动Agent  动力Agent
  (提交设计  (提交翼型  (提交推力
   变更请求)  修改请求)  分配方案)
```

**"邮箱"机制在载具设计中的含义**：
- 每个学科 Agent **不能直接修改**其他学科的设计参数
- 所有跨学科修改必须通过 Coordinator **审批**
- Coordinator 维护一个**设计冻结/释放**状态机

**现实映射**：这与航空企业的**工程更改控制流程（ECR/ECO）**高度一致。Harness Coordinator Mode 本质上是将企业的工程管理流程自动化。

### 4.4 Repo-as-Truth（环境管住认知）

**来源**：OpenAI Codex 团队——5 个月构建 100 万行代码生产系统

**载具设计适配**：

```
核心思想：不管理 Agent 行为，而是确保它感知的整个世界都是准确的
         ──────────────────────────────────────────────
         在载具设计中："世界"= 设计数据环境

┌─────────────────────────────────────────────────┐
│              Design-Repo-as-Truth                 │
│                                                  │
│  ┌──────────┐  ┌──────────┐  ┌──────────────┐  │
│  │ 3D 模型库 │  │ 仿真数据库│  │ 适航知识库    │  │
│  │ (STEP/   │  │ (结果+    │  │ (条款+判据+  │  │
│  │  IGES)   │  │  元数据)  │  │  案例)       │  │
│  └──────────┘  └──────────┘  └──────────────┘  │
│  ┌──────────┐  ┌──────────┐  ┌──────────────┐  │
│  │ 材料数据库│  │ 工艺知识库│  │ 项目管理基线  │  │
│  │ (疲劳S-N │  │ (DFM规则 │  │ (需求+接口+  │  │
│  │  曲线等) │  │  + 约束)  │  │  更改记录)   │  │
│  └──────────┘  └──────────┘  └──────────────┘  │
│                                                  │
│  ↑ Agent 的所有感知都来源于这个统一的"真实世界"    │
└─────────────────────────────────────────────────┘
```

**关键原则**：
1. **单一数据源（Single Source of Truth）**：所有 Agent 共享同一个设计数据环境
2. **自动维护**：CI/CD 流水线自动更新模型、仿真结果、知识库
3. **可追溯性**：每次设计变更都有完整的审计日志

**OpenAI Codex 团队的核心洞察**：流程管住行为，**环境管住认知**。如果 Agent 感知到的环境是准确的，它的行为自然更可靠。在载具设计中，这意味着**投资建设高质量的设计数据环境比优化 Agent 本身更重要**。

### 4.5 Sprint Contract（冲刺合同）

**来源**：Anthropic V2 创新

**载具设计适配**：

在每个设计迭代"冲刺"开始前，Agent 自签验收合同：

```yaml
sprint_contract:
  sprint_id: "wing-root-fitting-v3"
  objective: "优化机翼-机身连接接头，目标减重 8%"
  
  # Agent 自协商的验收标准
  acceptance_criteria:
    - criterion: "最大 von Mises 应力"
      threshold: "< 380 MPa"
      basis: "CCAR-25.305 + 1.15 安全系数"
    - criterion: "疲劳寿命"
      threshold: "> 60000 FH"
      basis: "CCAR-25.571 损伤容限要求"
    - criterion: "质量"
      threshold: "< 12.5 kg"
      basis: "质量预算分配 WBS-3.2.1"
    - criterion: "可制造性"
      threshold: "DFM 检查零违规"
      basis: "3D 打印工艺规范"
  
  # 不满足验收标准的后果
  on_failure: "回滚至上一版本，Generator 重新分析失败原因"
  
  # 人类介入条件
  human_gate: "安全系数变更 > 0.1 或材料替换时触发"
```

**价值**：Sprint Contract 将隐性的设计要求显性化，使每次迭代都有**明确的完成定义（Definition of Done）**。

### 4.6 Depth-First Working（深度优先构建）

**来源**：OpenAI 实践——大目标拆小构件，逐个构建后解锁更复杂任务

**载具设计适配**：

```
Level 0: 全机级概念设计
  ├── Level 1: 机翼设计
  │     ├── Level 2: 机翼蒙皮（先完成）
  │     ├── Level 2: 机翼翼肋（先完成）
  │     └── Level 2: 机翼大梁（先完成）──→ 解锁 Level 1 验收
  ├── Level 1: 机身设计
  │     ├── Level 2: 机身框（先完成）
  │     └── Level 2: 机身蒙皮（先完成）──→ 解锁 Level 1 验收
  └── Level 1 全部完成 ──→ 解锁 Level 0 全机级多学科优化
```

**核心原则**：
- 自底向上构建，每个最小构件独立验证
- 上层任务只有在所有下层任务完成后才能开始
- 避免在未经验证的基础上构建复杂设计

### 4.7 架构模式选择矩阵

| 载具类型 | 推荐主架构 | 辅助架构 | 理由 |
|----------|-----------|----------|------|
| 民用飞机 | Coordinator Mode + Generator-Evaluator | Sprint Contract | 安全关键、多学科、需人工审批 |
| 航天器 | Repo-as-Truth + Depth-First | Planner-Worker-Judge | 数据环境质量是核心、自底向上构建 |
| 无人机 | Planner-Worker-Judge | Generator-Evaluator | 迭代快、多目标、成本敏感 |
| 运载火箭 | Sprint Contract + Coordinator Mode | Repo-as-Truth | 任务级约束严格、一次性使用 |

## 相关笔记
- [harness-vehicle-report-06-conclusion](_drafts/harness-vehicle-report-06-conclusion.md)
- [harness-vehicle-report-01-abstract-intro](_drafts/harness-vehicle-report-01-abstract-intro.md)
- [langchain-harness-memory-analysis](langchain-harness-memory-analysis.md)
- [Harness-Engineering-载具设计研究报告](Harness-Engineering-载具设计研究报告.md)
- [垂域模型_p4_harness](_drafts/垂域模型_p4_harness.md)
