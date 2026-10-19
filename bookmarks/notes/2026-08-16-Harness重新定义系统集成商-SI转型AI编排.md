# Harness 可能重新定义系统集成商：从 System Integration 到 AI Orchestration + Execution

> **来源**：X @stevencheng（Steven Cheng，Physical AI & robotics）推文 + 行业扩展研究
> **原文链接**：https://x.com/stevencheng/status/2088489484761608662
> **记录日期**：2026-08-16
> **处理方式**：原文还原 → 行业事实补充 → 扩展分析（用户要求"补充、扩展后形成完整详细笔记"）

**标签**：#Harness #系统集成 #SI转型 #AI编排 #企业Agent #行业变革

---

## 一、内容整理

### 1.1 原文核心论点（推文还原）

Steven Cheng 的命题：**Harness May Redefine the SI（AI Harness 可能重新定义系统集成商）**

| 维度 | 传统 SI（系统集成商） | AI Harness |
|------|---------------------|-----------|
| 连接对象 | ERP、CRM、MES、数据库等软件系统 | AI agents + workflows + tools + data + 企业系统 |
| 产出 | 系统打通（数据流动） | **实际执行行业特定工作** |
| 范式 | System Integration（系统集成） | AI Orchestration + Execution（AI 编排 + 执行） |
| 护城河 | 实施专长 + 行业 know-how | **行业数据 + 工作流 + agents + 工具 + 持续反馈闭环** |
| 角色重定义 | — | 从"整合系统"到"执行工作" |

关键句："Harness 不是简单替代 SI，它可能重新定义 SI 的角色——从集成系统到执行工作。"

评论区的关键追问（@techniahqrobot）："AI Harness 最终会取代传统系统集成商，还是 SI 会进化和转型，成为构建和运营这些 AI 编排层的公司？"——这正是本笔记扩展分析的主线。

### 1.2 扩展：传统 SI 的商业模式解剖（补充）

传统 SI（Accenture/Deloitte/Infosys 们）的收入机器：

```
咨询（战略/流程设计）→ 实施（定制开发+系统对接）→ 运维（长期人天账单）
```

三个结构性弱点在 AI 时代被放大：
1. **人天计费 vs 无人化交付的矛盾**：Agent 执行工作不消耗人天——SI 的收入公式直接被攻击
2. **交付物是"项目"不是"能力"**：项目结项即交付，客户能力沉淀在 SI 而非客户；Harness 的反馈闭环让能力持续留在客户侧生长
3. **知识资产在顾问脑子里**：行业 know-how 以文档/专家系统形式存在，无法 7×24 执行；Harness 把 know-how 外化成 agents+tools+rules，可复用可审计

### 1.3 扩展：AI Harness 的企业级形态（行业事实）

2026 年企业 AI agent 平台的事实标准结构（JetRuby/StackAI/eZintegrations 等平台综述交叉验证）：

```
模型层（一个或多个 LLM）
  + 检索层（内部数据 grounding）
  + 集成层（CRM/ERP/工单/生产系统 API）
  + 决策逻辑（显式规则 + 决策树）
  + 编排层（任务分解/路由/多 agent 协作）
  + 外围：日志/监控/人机协同门禁（生产可控性）
```

关键工程事实：
- **集成工作流本身可以注册为 agent 的工具**（eZintegrations 模式）——agent 一次工具调用执行整条多步集成流程，这是"SI 交付物"与"agent 工具"的桥接点
- **写操作必须带审批门**（approval gates for write actions）——权限分级与审计是企业采购的硬门槛
- **advisory mode 先行**（agent 建议、人决策）→ 逐步放权的部署次序已是行业共识
- **混合模式是 2026 主流**："平台管编排/部署/治理/连接器，定制工具与领域逻辑留在代码里暴露为 API"——不是全盘 agent 化

### 1.4 扩展：SI 们的实际动作（市场验证）

- **Accenture**：已建立大规模 AI agent 实践（企业 AI agent 开发商评测榜居前），从" transformation program "向 agent 交付转型
- **行业评测的残酷观察**：每家 Big 4/每家 SI/每家区域咨询都有"AI agent practice"标签，但**真正交付过规模化自主 agent（客服升级/核保/理赔分诊/供应链重规划）的是少数**——多数还在卖"换皮的 chatbot 试点"
- **Anthropic 的 harness 文档线**（2025-09 起系列）：effective harnesses for long-running agents / code execution with MCP / evals for agents / measuring agent autonomy——**"harness 工程"已成 2026 企业 AI 的一级学科**，正是推文论点的技术底座
- **Harness.io（同名公司）**：其 MCP server 统一安全+交付 agent 的路线印证"编排层公司化"——集成商的下一代形态就是运营这种层

### 1.5 "取代 vs 进化"的答案（对评论区问题的扩展回答）

**判断：进化而非取代，但门槛会淘汰多数。**

论证链：
1. **Legacy 系统集成的脏活仍在**——"legacy 集成比 demo 展示的难得多"是 2026 企业 agent 生产化三大痛点之首。谁最会啃 legacy？SI。这是它们的存量优势
2. **但价值链重心迁移**——打通系统（pipes）的价值贬值，编排+执行（work）的价值升值。SI 若只守 pipes，收入公式持续失血
3. **新护城河的结构**（推文核心）：行业数据 + 工作流 + agents + 工具 + **持续反馈闭环**——这不是一次性项目能建立的，需要长期运营。具备"构建并运营 AI 编排层"能力的 SI 会拿到新一代合同（按结果计费的雏形）
4. **淘汰逻辑**：卖人天的 SI 被按结果交付的竞争者挤压；能转型的 SI 把自己从"项目交付方"变成"客户的 AI 运营部门"

## 二、查询拓展

### 2.1 Harness 概念的三层含义辨析（重要——术语混乱源）
- **狭义**（Anthropic 工程文档）：围绕单个 agent 的执行环境——上下文管理/工具/循环/评估
- **中义**（AI4AI 论文）：强模型为弱模型构建的推理脚手架（前一笔记主题）
- **广义**（本推文）：**企业级工作执行层**——连接 agents/workflows/tools/data/企业系统的行业落地形态。三层共享同一内核：**能力外化 + 确定性外壳 + 反馈闭环**
- 判断：术语会继续混用，但"从 prompt 工程 → harness 工程"的迁移是共同趋势

### 2.2 与 iPaaS 的谱系关系
Workato 类 iPaaS 是"集成管道即服务"；Harness 是在管道之上加**执行决策**。eZintegrations 的"集成工作流注册为 agent 工具"模式 = iPaaS 向 Harness 的进化路径：**pipes → pipes + brains**。未来 iPaaS 与 agent 平台的边界会消失。

### 2.3 按结果计费（outcome-based pricing）的萌芽
Agent 执行工作 → 客户按"完成的工作量"付费而非人天。SI 行业的定价革命已在咨询界讨论（value-based pricing 的 agent 版）。这是"Harness 重定义 SI"的商业本质：**收入从卖实施人力转为卖执行结果**。

## 三、归纳总结

### 3.1 扩展后的完整论点链

```
技术侧：模型能力商品化 → 差异化转移到模型外围（harness）
商业侧：人天计费被无人化执行攻击 → SI 必须转向运营编排层
数据侧：行业数据+反馈闭环成新护城河 → 一次性项目模式失效
结论：SI 不死，但"集成商"三个字会被改写——从 connecting systems 到 executing work
```

### 3.2 五要素实操区

#### ✅ 功能清单（AI Harness 作为企业资产能做什么）

- [x] 编排：多 agent 任务分解/路由/协作
- [x] 执行：跨 ERP/CRM/MES 的行业工作流实际运行
- [x] 工具化：既有集成资产注册为 agent 可调用工具
- [x] 治理：权限分级/审批门/审计日志/PAT 作用域
- [x] 反馈：持续闭环（运行数据回流改进 agents/rules）
- [x] 评估：agent evals（Anthropic 2026-02 文档化为方法论）

#### 🎯 使用性评估

- **成熟度**：概念热、落地分化——真正规模化交付的 SI 是少数；企业侧 2026 主流仍是 advisory mode + 混合架构
- **主要风险**：legacy 集成难度被低估；"chatbot 换皮"供应商泛滥；agent 生产化的治理缺口
- **时间窗口**：转型窗口正在打开（Anthropic harness 文档线 + SI 实践兴起 + 按结果计费萌芽三信号重叠）

#### 💡 指导性意见

1. **对企业买家**：选 SI 看三个硬指标——已交付的自主 agent 案例（非 chatbot）、写操作审批门设计、评估体系（有 evals 才有持续改进）
2. **对 SI 从业者**：把行业 know-how 从文档/脑子外化成 agents+tools+rules 的能力是新的核心技能；"构建并运营编排层"是新岗位方向
3. **对开发者**：harness 工程技能栈（上下文工程/MCP/评估/权限设计）需求上升，参见 Anthropic 系列文档

#### 📌 案例

- **eZintegrations**：九大原生 agent 工具 + 集成工作流注册为工具调用——"SI 交付物工具化"的活样本（质检场景：缺陷历史查询+SLA 检索+ERP 订单核验一次完成）
- **Harness.io**：DevOps 领域的编排层公司化——MCP server 统一安全与交付 agent，"运营 AI 编排层"的商业模式实证
- **评论区之问**的答案在市场已现：Accenture 们没有死，而是在把自己变成编排层运营商

#### 🔧 使用方法借鉴（可直接抄的转型框架）

```
SI → Harness 运营商的四步转型（扩展自行业综述）：
① 盘点行业 know-how：文档/SOP/专家规则 → 结构化为 rules + decision trees
② 存量集成资产工具化：既有 iPaaS/接口注册为 agent 可调用工具（eZintegrations 模式）
③ advisory mode 上线：agent 建议+人审批 → 收集真实运行数据
④ 反馈闭环+放权：评估达标的工作流逐步自主化 → 按结果计费试点
```

## 四、趋势判断

1. **"Harness 工程师"会成为 2026-2027 招聘热词**：模型层商品化后，差异化全在编排/执行/治理层——与 AI4AI 笔记的"确定性卸载"发现互证
2. **SI 行业大洗牌以"是否有真实 agent 交付"为分界线**：评测机构已开始用"shipped autonomous agents vs chatbot pilots"区分供应商——采购标准的变化会加速淘汰
3. **按结果计费从边缘到主流**：agent 执行的工作量可精确计量，为人天计费模式的终结提供技术基础
4. **"集成"一词的语义漂移**：从"连系统"泛化为"连 agents+tools+data+systems 执行工作"——推文标题的深层含义

## 五、关联分析

- **AI4AI at Test-Time 笔记**（前一篇）：技术基座——强模型为弱模型造 harness 的能力转移范式，正是"Harness 运营商"能规模化交付的科学依据；两篇构成"harness 微观机理 + 宏观行业变革"上下篇
- **Miles 双门笔记**：企业 Harness 的安全设计（权限管理+证据门禁）正是 SI 转型时必须内建的治理层——没有双门的 harness 卖不进企业
- **tapflow 笔记**：MCP server 化设备控制是"工具进编排层"的样本——同一个 MCP 生态把设备/集成/安全都编进 agent 工具链
- **Hermes 自身**：我的 skill+cron+script 体系就是个人级 harness——AGENTS.md 的龙虾法则（重复任务→样本→SKILL.md→cron）与企业 SI 转型四步框架同构，只是规模不同
- **飞书生态**：lark-cli 200+命令 MCP 化的方向 = 把企业协作系统工具化进编排层——自下而上的 harness 组装路径

## 六、金句摘录

> "传统 SI 连接系统，AI Harness 连接一切并实际执行行业工作。"

> "护城河从实施专长变成：行业数据 + 工作流 + agents + 工具 + 持续反馈闭环。"（原文）

> "Harness 不是替代 SI，是重新定义 SI——从整合系统到执行工作。"（原文核心）

> "每家 SI 都有 AI agent practice 标签，真正交付过规模化自主 agent 的是少数——多数还在卖换皮的 chatbot 试点。"（行业评测）

## 七、行动启示

| 启示 | 行动 | 状态 |
|------|------|------|
| 概念体系入库 | Harness 三层含义辨析（狭义/中义/广义）记入术语库 | ✅ 本笔记 |
| SI 转型框架 | 四步转型框架可复用为咨询/方案素材 | ✅ 已收录 §3.2 |
| 观察指标 | 跟踪 Anthropic harness 文档线 + SI 按结果计费案例 | 持续 |
| 与飞书工具链结合 | lark 系 MCP 化 = 小型编排层实践，可作 Harness 概念的本地试验田 | backlog |


## 相关笔记

- [AI4AI at Test-Time：强到弱 Harness 能力转移](./2026-08-16-AI4AI-at-TestTime-强到弱Harness能力转移.md) — Harness 工程的技术实现视角，本篇是其产业/SI 视角
- [AI 落地两道门：权限管理与证据门禁](./2026-08-15-AI落地两道门-权限管理与证据门禁.md) — 企业 AI 编排落地时的治理配套
- [Andrew Ng AI 工程技能图谱](./2026-08-15-AndrewNg-AI工程技能图谱.md) — SI 转型后所需人才技能清单对照
