# 航空结构 Agentic MDAO：多 Agent LLM 自动化多学科设计优化 2026 前沿

> **来源**：arXiv 2511.17511（MDO Agent 全文）、UMich IDEAS Lab（OpenAeroStruct LLM Agent 官方页）、ScienceDirect Array 26000445（Hasan & Nguyen）、Digital Twin Consortium 官网（NARTP 联合验证 + Industrial AI Agent Manifesto）、Elsevier Measurement（CMAD）
> **记录日期**：2026-09-15
> **作者**：MeowBot 研究管线（多源检索 + 交叉验证）

**标签**：#AgenticMDAO #航空数字孪生 #多Agent编排 #结构健康监测 #适航合规 #OpenAeroStruct #LLM工程应用

---

## 一、内容详细整理

### 1.1 MDO Agent：四 Agent 协同 + 三项核心能力（arXiv 2511.17511，2026-11）

浙江大学团队（Bingkun Guo 等，Zhejiang University）发表 MDO Agent 框架，是 2026 年最完整的 MDO 自动化论文之一。框架由 **四个协同 Agent** 组成：

- **Designer Agent**（设计者）：接收自然语言需求，通过 RAG 从知识库检索，生成结构化设计方案描述
- **Modeler Agent**（建模者）：将文字描述转为 CadQuery 参数化 CAD 代码，生成 3D 模型，带 VLM 视觉自校正
- **Verifier Agent**（验证者）：集成 FEA 工具接口，自动生成仿真代码、执行分析、提取关键指标
- **Optimizer Agent**（优化者）：集成优化算法，与 Modeler + Verifier 协作做参数迭代优化

三项核心能力：

1. **自然语言驱动参数化建模**：LLM 将用户文本指令映射为 CadQuery Python 脚本。生成公式为 y₀ ~ P_LLM(y|x, E_g)，其中 E_g 是 few-shot 示例。代码执行报错时，错误信息 F_err 反馈 LLM 进入自校正循环。
2. **RAG 知识锚定概念生成**：多源知识库（设计手册 + 工程标准 + 历史案例）分段编码为向量，用 bge-large-zh-v1.5 做 embedding，查询时计算余弦相似度取 top-K 片段。关键公式：sim(q, v_i) = (q·v_i) / (||q||·||v_i||)，抑制 LLM 幻觉。
3. **ReAct 式工具调用优化**：9 个工程工具函数（load_geometry / init_physics_field / create_entity_set / define_material_properties / set_meshing_options / apply_boundary_conditions / execute_solver / visualize_results / execute_python_code），LLM 从被动文本生成器变成能规划、执行、评估的工程 Agent。

视觉自校正闭环（Modeler Agent 核心创新）：

```
[生成] VLM 生成 CAD 代码 y_i
   ↓
[渲染] 执行脚本 → 多视图 3D 渲染图 M_i
   ↓
[校正] VLM 对比渲染图 vs 子任务描述 T_i
   ↓ 若发现偏差（尺寸错误/特征缺失）
   VLM 诊断根因 → 生成修正代码 y_{i+1}
   ↓ 循环直到收敛或达最大迭代数
```

Chain-of-Thought 任务分解：复杂结构拆为有序子任务列表 {T₁, T₂, …, T_N}，每步含精确空间约束（形状、尺寸、定位）。例如"设计椅子"→ 创建座面 → 添加腿 → 构建靠背。

**定量结果（3 案例验证）**：

- 参数化建模代码工作量减少 **70%+**
- FEA 仿真流程自动化约 **70–75%**
- 3 个案例：燃气涡轮叶片、机床立柱、分形散热片
- 从自然语言输入到已验证优化设计的完整管线跑通

### 1.2 UMich OpenAeroStruct LLM Agent：航空专用 MDAO 自动化（UMich IDEAS Lab）

UMich 的 Cinar 组（gokcincinar.com）发布的 OpenAeroStruct LLM Agent 是航空结构域最成熟的 agentic MDAO 工具：

- 用户用**自然语言**输入翼型设计需求，系统自动处理网格划分、分析、优化、可视化、报告
- 当前支持主气动目标：升力（lift）和阻力（drag）
- 几何设计变量： taper（后掠角）、sweep（后掠角）、dihedral（上反角）、chord（弦长）、twist（扭转角）
- 执行底座：OpenAeroStruct（UMich 开源多物理场航空结构框架）+ Kriging surrogate + SLSQP 优化器

与 MDO Agent（浙大）的差异：UMich 框架是**航空专用**（翼型 + 气弹结构），浙大框架是**通用机械结构**（CAD + FEA + 优化通用管线）。

论文原句（UMich Cinar 组 PP 2025）："*the framework employs a specialized coding agent pattern... Minimizing computational overhead is critical for the framework's intended application within the digital twin paradigm, which demands rapid, iterative design cycles.*"

### 1.3 Hasan & Nguyen 七层集成框架（Array 2026，DOI: 10.1016/j.array.2026.100721）

ScienceDirect Array 期刊 2026 年 4 月发表，被引 9 次，是当前 agentic DT 最权威的分层参考：

```
┌─────────────────────────────────────────────────┐
│  L7  Feedback Adaptation 层                     │
│       闭环反哺 Knowledge 层                       │
├─────────────────────────────────────────────────┤
│  L6  Action Execution 层                        │
│       物理系统指令执行                             │
├─────────────────────────────────────────────────┤
│  L5  Decision-Making 层                         │
│       策略选择（RL / 优化器 / 规则引擎）           │
├─────────────────────────────────────────────────┤
│  L4  Learning 层                                │
│       在线微调 / 反馈学习                          │
├─────────────────────────────────────────────────┤
│  L3  LLM Reasoning 层（Cognitive Core）          │
│       目标推理、任务分解、语义理解                   │
├─────────────────────────────────────────────────┤
│  L2  Knowledge & Data 层                        │
│       本体 + RAG + 时序数据湖                      │
├─────────────────────────────────────────────────┤
│  L1  Perception 层                              │
│       传感器 / 仿真 / 日志采集                     │
└─────────────────────────────────────────────────┘
```

**航空落地含义**：适航场景下 LLM 仅允许在 L1–L3 做"辅助认知"（读 FMEA、生成故障假设、调用 SHM 数据、给出候选处置方案），L5 决策必须由确定性规则/优化器完成，最终需人签字。这是当前唯一能通过 EASA/DCA/CAAC 审查的架构。

### 1.4 DTC × NARTP 航空多 Agent DT 联合验证（2026-04-29）

Digital Twin Consortium + NARTP 签 liaison 协议，是产业联盟做标准化的标志性事件：

**技术栈**：

- **AMD Ryzen AI**：Hybrid NPU + 集成 GPU 边缘计算，Lemonade Server 支持设备端本地 LLM 部署
- **XMPro MAGS**（Multi-Agent Generative Systems）：运行在 AMD 底座上的 Agent 编排层，部署/管理/协调 AIA CPT 框架定义的 AI Agent
- **Rowan University DEHub / Pythia**：本地 HPC + 物理信息 AI + 实时传感器集成 + 机器人测试台，支撑航空组件（涡轮叶片、机身结构、先进材料）的太字节级 DT 验证
- **DTC 双 CPT 框架**：Digital Twin Capabilities Periodic Table（定义 Twin 保真度层级、数据集成深度、自主权等级、生命周期管理）+ AI Agent Capabilities Periodic Table（AIA CPT，分类 Agent 能力：感知/推理/规划/执行/协调）

**DTC Agent 分类体系（5 级，0–4）**：从对话式半自主（L0）到全自主多 Agent 系统（L4）。关键洞察（DTC CTO Dan Isaacs 原话）："only 8% of the source code is for integrating the LLM, while 92% is about business processes and governance"——LLM 只是冰山一角，92% 的代码是治理和业务流程。

**工作领域**：

- Air Traffic Management（空管，含 eVTOL 城市空中交通 + UAS 高密度操作）
- Cybersecurity（航空网络安全）
- Autonomy（自主性验证）

**验证环境**：NARTP 紧邻 FAA 的 William J Hughes Technical Center（WJHTC），有实时航空测试台——不是在合成基准上测试，而是在真实操作约束下。

### 1.5 DTC Industrial AI Agent Manifesto：可信 AI Agent 治理十法（2026-02）

DTC Composability Framework Working Group 发布，是安全关键工业环境部署 AI Agent 的首个行业治理框架：

**五条不可协商的基础需求**：

1. **可复现上下文**：恢复 Agent 决策时的完整操作状态（设备状态、活跃约束、相关历史、环境条件）
2. **领域约束作为硬边界**：架构上证明 Agent 不能违反关键领域规则，而非通过监控
3. **执行前验证**：Agent 推荐与动作执行架构分离——Agent 提议，验证层校验，只有通过验证的动作才执行
4. **完整审计轨迹**：即时回答"约束 X 活跃时 Agent 做了什么决策、考虑了哪些备选方案"
5. **舰队级策略管理**：约束更新一次即可传播到所有 Agent，无需手动重配置

**十法核心（与航空适航直接相关）**：

- **Law 2 物理感知**：Agent 必须尊重物理约束、编码过程模型，而非仅统计模式
- **Law 3 符号优先**：符号推理在架构上优先于子符号 AI，创造内在的可信度和可审计性
- **Law 5 紧急停止 + 人工覆写 + 优雅降级**：非可协商能力，Agent 突然停止可能把物理系统留在未定义或危险状态
- **Law 6 与运营系统互操作**：Agent 与领域系统（飞行/制造/电网）的交互必须通过语义模型中介，而非直接协议接口
- **Law 8 渐进式自主**：自主权等级必须映射到人类角色、审批和安全关键性

**行业预警**：Gartner 预测 **2028 年 40% 的 agentic AI 部署将失败**——不是因为 AI 能力不足，而是因为治理基础设施不存在。

### 1.6 CMAD：统一 ML-DIC 框架把"检测+定位+预测"合一（Elsevier Measurement 2025）

传统航空 SHM 把 crack detection / localization / growth forecasting 拆成三张表三个模型，CMAD 框架合并为一个 ML-based DIC（Digital Image Correlation）管线：

**Algorithm 1: CMAD – Crack Monitoring and Analysis DeepNet**

- **输入**：DIC 图像序列数据集 D + 裂纹地面真值标签 L（可选）+ 载荷元数据 Φ（可选）
- **输出**：裂纹起始状态 + 预测裂纹尖端位置 + 裂纹路径分割图 + 裂纹长度预测
- **预处理阶段**：每帧 x_i ∈ D → resize + 归一化 → 从 DIC 计算应变/位移图 → 附加载荷元数据 Φ_i

对国内启示：在代理模型层做统一表征，让下游 Agent 消费更简单——一个模型输出四项指标，而非三个模型各输出一项。

### 1.7 Boeing 结构疲劳专利族与无线传感器面板

Boeing 2020–2025 结构疲劳专利族（US 2025 active filings）+ Future Market Insights 2026 报告：

- 机翼/机身关键承载接头区：机载传感器阵列 + 回归模型已成主流
- **wireless sensor access panels**：可拆卸无线面板替代传统钻孔穿线
- 维护人员下载应力剖面到地面移动站，不需穿透压舱壳穿铜线
- 可绕过传统检查间隔（"bypass traditional inspection intervals entirely"）
- 必须与 AI 预测维护软件架构无缝集成，否则假阳性会瘫痪机务

市场数据：数字孪生市场 60% CAGR；航空与国防段 $2.49B（2025）→ $3.07B（2026），CAGR 23.3%（ResearchAndMarkets 2026）。每个避免的 AOG 事件单点成本 $150k–$500k。

---

## 二、查询拓展

### 2.1 MDAO 自动化的演进脉络

MDAO（Multidisciplinary Design and Optimization）是航空数字孪生的核心技术难点——一次气动/结构/热/重量多学科协同优化动辄 3–8 周，人工写 OpenAeroStruct/Dymos 脚本占一半时间。2026 年的突破是用 agentic LLM 把"高层需求 → MDAO 工作流代码"自动化：

```
传统：需求 → 人工写脚本（数天） → 配置优化器 → 跑 3–8 周 → 人工分析结果
Agentic MDAO：需求 → LLM 合成代码（分钟级） → surrogate 优化（30–90 分钟） → 自动报告
```

关键转折：LLM 只做"翻译员 + 调度员"，刻意避免直接接触重型 CAD/CFD 计算图。真正的多学科计算走 OpenAeroStruct 已有的 Kriging surrogate + SLSQP 优化。

### 2.2 RAG 在工程设计中的抑制幻觉机制

浙大 MDO Agent 用 RAG 解决 LLM 在机械领域的两个致命短板：内部知识过时/缺乏深度 + 幻觉倾向。实现细节：

- 知识库：设计手册 + 工程标准 + 历史设计案例，分段为语义连贯的 chunk
- Embedding：bge-large-zh-v1.5（中文优化）
- 检索：余弦相似度 top-K 片段
- 生成：C* = {c₁*, c₂*, …, c_K*} 与原始查询整合为结构化 prompt

这个模式直接可迁移到航空 FMEA 文档检索——FMEA 本体作为 RAG 知识库，LLM 生成故障假设时自动锚定到可信的故障模式库。

### 2.3 DTC 双 CPT 框架的互补设计

DTC 同时在推进两个互补框架：

- **Digital Twin CPT**：定义 Twin 保真度层级、数据集成深度、自主权等级、生命周期管理——回答"这个 Twin 能做到什么程度"
- **AIA CPT**（AI Agent Capabilities Periodic Table）：分类 Agent 能力——感知、推理、规划、执行、协调——回答"这个 Agent 能做到什么"

两者组合定义了 MAGS 架构：数字孪生作为操作环境，AI Agent 作为在 Twin 内部和之上行动的智力层。航空是同时验证两个框架的"练兵场"。

这类似 ROS2 之于机器人——第一次有了跨厂商的多 Agent + DT 组合标准。

### 2.4 治理基础设施是 agentic AI 落地的真正瓶颈

DTC Manifesto 揭示了一个反直觉的洞察：**LLM 代码只占系统代码的 8%**，92% 是治理和业务流程。Gartner 预测 2028 年 40% 的 agentic AI 部署失败——不是因为 AI 能力不足，而是因为治理基础设施不存在。

这对航空业的含义：不是"要不要用 LLM 做 MDAO"的问题，而是"治理基础设施能不能跟上"的问题。MC0–MC9 分层、CCAR/EASA/DCA 审查流程、审计轨迹要求——这些"92% 的代码"才是航空 agentic AI 的真正壁垒。

---

## 三、归纳总结

### 3.1 航空结构 Agentic MDAO 全景架构

```
┌─────────────────────────────────────────────────────────┐
│                    自然语言需求输入                         │
│         "优化某机翼在巡航条件下的升阻比"                     │
└──────────────────────┬──────────────────────────────────┘
                       ↓
┌──────────────────────────────────────────────────────────┐
│  Agent 编排层（LLM Cognitive Core）                       │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐   │
│  │ Designer │→│ Modeler  │→│ Verifier │→│ Optimizer│   │
│  │ Agent    │ │ Agent    │ │ Agent    │ │ Agent    │   │
│  └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘   │
│       │            │            │            │          │
│  RAG知识库    CadQuery+VLM   FEA工具调用   优化器调用     │
│  (FMEA/      (自校正渲染)   (9个函数)   (SLSQP/Kriging) │
│   设计手册)                                          │   │
└──────────────────────┬───────────────────────────────────┘
                       ↓
┌──────────────────────────────────────────────────────────┐
│  验证门禁层（确定性代码，非 LLM）                           │
│  CCAR-25 合规检查 → EASA 审查 → 人工签字                    │
│  (通过 → 执行 | 不通过 → HUMAN_REVIEW_REQUIRED)            │
└──────────────────────┬───────────────────────────────────┘
                       ↓
┌──────────────────────────────────────────────────────────┐
│  执行层：OpenAeroStruct MDAO solver                       │
│  Kriging surrogate + SLSQP 优化（30–90 分钟/轮）            │
└──────────────────────┬───────────────────────────────────┘
                       ↓
┌──────────────────────────────────────────────────────────┐
│  反馈层：结果写回 Knowledge 层                             │
│  FMEA 更新 + 设计经验积累 + 审计日志                        │
└──────────────────────────────────────────────────────────┘
```

### 3.2 五条关键设计原则

1. **LLM 只做认知，不做决策**：compliance.verify 是硬门禁，CCAR/EASA 未通过直接返回人工审核
2. **代码生成而非直接推理**：LLM 生成的是可审查、可版本控制、可审计的 Python 代码
3. **surrogate model 而非全仿真**：Kriging 代理把 MDAO 从 3–8 周压到 30–90 分钟
4. **RAG 锚定可信知识库**：抑制幻觉，确保设计方案的工程可行性
5. **治理基础设施优先于 AI 能力**：92% 的代码是治理，不是 LLM

### 3.3 四 Agent 分工 vs 单 Agent 一把梭

```
单 Agent 模式：
  需求 → [全能Agent] → 结果
  问题：幻觉高、上下文溢出、错误难定位

四 Agent 模式（UMich + 浙大共识）：
  需求 → [Designer] → [Modeler] → [Verifier] → [Optimizer] → 结果
  优势：每个 Agent 职责单一、上下文可控、错误可定位、可并行
```

---

## 四、趋势判断

### 趋势 1：2026–2027 进入"治理基础设施"竞赛阶段

依据：DTC Industrial AI Agent Manifesto 2026-02 发布 + Gartner 40% 失败预测 + NARTP 联合验证 2026-04。Agentic AI 的技术能力已经不是瓶颈，治理基础设施（审计轨迹、约束管理、策略传播）才是。预计 2027 年前后出现类似 ISO/IEC 的行业标准。

### 趋势 2：LLM 只做认知、确定性代码做决策——适航架构定式

依据：Hasan & Nguyen L1–L3 vs L5 分层 + DTC Law 4 执行前验证 + UMich 框架刻意避免 LLM 接触重型计算图。这不是过渡方案，是航空业的最终架构——与 MC0–MC9 分层天然适配。

### 趋势 3：MDAO 自动化从"通用机械"向"航空专用"分化

依据：浙大 MDO Agent（通用 CAD+FEA）vs UMich OpenAeroStruct（专用翼型+气弹）。通用框架负责原型验证，航空专用框架负责生产级交付。预计 2027 年出现国产航空专用 agentic MDAO 框架。

### 趋势 4：SHM 从"三模型三张表"向"统一代理模型"收敛

依据：CMAD 框架把检测+定位+预测合一 + Boeing 无线传感器面板。统一表征让下游 Agent 消费更简单，是 agentic SHM 的前提。

### 趋势 5：CCAR 场景 multi-agent DT 是明确的国内空白

依据：DTC/NARTP 是北美联盟，CCAR 场景下无公开标准。这是空白也是机会——谁先建立 CCAR 场景的 multi-agent DT 治理框架，谁就掌握标准制定权。

---

## 五、关联分析

### 5.1 与已有笔记的关联

- [2026-05-16 数字主线 AI 融合航空结构设计-深度蒸馏](2026-05-16-数字主线-AI融合航空结构设计-深度蒸馏.md)：该笔记侧重 Digital Thread 知识蒸馏，本篇聚焦 agentic MDAO 自动化——两者互补，前者管"知识怎么沉淀"，后者管"知识怎么自动化执行"
- [2026-07-23 航空数字主线-AIAA](2026-07-23-航空数字主线-AIAA.md)：AIAA 视角的数字主线全景，本篇补充 MDAO 自动化的最新进展（四 Agent 框架 + 70%+ 效率提升）
- [2026-07-28 航空数字主线-Digital-Thread](2026-07-28-航空数字主线-Digital-Thread.md)：Digital Thread 架构，本篇的 RAG 知识库 + FMEA 本体可直接映射到 Digital Thread 的知识层

### 5.2 与已有项目的关联

- [ai-aircraft-structural-design](../../../project/ai-aircraft-structural-design/)：该项目的 FMEA 本体 + 结构分析模块可直接作为 agentic MDAO 的 RAG 知识库底座

### 5.3 与 Hermes Agent 生态的可迁移模式

1. **Specialized Coding Agent 分工**（UMich 模式）→ 对应 Hermes 的 subagent-driven-development + skill-pipeline
2. **认知层 vs 决策层分离 = 零信任执行**（Hasan 模式）→ 对应 Hermes 的 deterministic-guardrails + agent-security-governance
3. **Composability Framework 思维**（DTC 模式）→ 对应 Hermes 的 agent-card-protocol + skill/plugin 架构

---

## 六、金句摘录

> "Minimizing computational overhead is critical for the framework's intended application within the digital twin paradigm, which demands rapid, iterative design cycles." — UMich Cinar 组，PP 2025

> "Only 8% of the source code is for integrating the LLM, while 92% is about business processes and governance." — DTC CTO Dan Isaacs

> "In regulated environments, proof matters more than promise. When an agent influences structural integrity, operators and regulators require evidence of three things: what the system decided, why it decided it, and whether unsafe outcomes were structurally prevented." — DTC Industrial AI Agent Manifesto, 2026

> "You cannot certify a multi-agent aviation system in isolation — emergent behaviors only surface under realistic operational load." — John Fredrick, Veracity Engineering

> "Autonomy does not eliminate human judgment — it encodes it, preserves it, and ensures that automation strengthens resilience rather than undermining it." — DTC Manifesto

---

## 七、行动启示

| 启示 | 具体行动 | 优先级 |
|------|---------|--------|
| Agentic MDAO 四 Agent 模式可迁移到航空 FMEA 自动化 | 用 FMEA 本体做 RAG 知识库 + CadQuery 式代码生成，验证可行性 | P1 |
| 治理基础设施是真正壁垒 | 评估 CCAR-25 合规检查自动化方案，对标 DTC 十法 | P1 |
| CCAR 场景 multi-agent DT 是空白 | 跟踪 DTC 标准进展，评估国产标准制定窗口 | P2 |
| CMAD 统一表征模式可借鉴 | 评估现有 SHM 项目是否可从三模型收敛为统一代理模型 | P2 |
| 8% LLM / 92% 治理的启示 | 在 agent-security-governance skill 中标注"航空场景强制 L3→L2 降级" | P3 |

---

## 八、拓展应用推荐

### 8.1 航空结构设计企业直接可用的三个方向

**方向 A：FMEA 自动化生成管线**

用 MDO Agent 的 RAG 模式，把现有 FMEA 文档（手册 + 标准 + 历史案例）向量化，构建故障假设生成 Agent。用户输入"某部位应力超标"，Agent 自动检索相关故障模式 + 生成候选处置方案 + 输出 CCAR 合规检查报告。

**方向 B：MDAO 工作流自动合成**

在现有 MDAO 流程（OpenAeroStruct / Dymos）上加一层 LLM Agent，把自然语言需求自动翻译为可执行的工作流代码。先从翼型优化入手（变量少、验证快），再扩展到结构拓扑优化。

**方向 C：SHM 预测维护 Agent**

CMAD 统一表征 + 无线传感器面板 + 边缘 AI 推理 = 可预测式 SHM。Agent 读取传感器数据流，自动调用 CMAD 模型输出裂纹状态，结合 FMEA 生成维护建议，输出适航文档。

### 8.2 对 Hermes Agent 生态的三条借鉴

1. **subagent-driven-development skill 补充航空场景约束**：四 Agent 分工模式（Designer/Modeler/Verifier/Optimizer）比单 Agent 一把梭稳定性高得多，适合重代码任务
2. **agent-security-governance skill 增加"航空 profile"模板**：L1/L2/L3 自主权分层中，航空/适航场景强制把 L3 决策降到 L2（人工签字）
3. **agent-card-protocol skill 借鉴 DTC composability**：给每个 SHM sensor type 生成标准化 Agent Card，支持跨厂商可组合

---

## 九、指南分析

### 9.1 如何评估一个 agentic MDAO 系统的成熟度

| 维度 | 入门级 | 进阶级 | 生产级 |
|------|--------|--------|--------|
| 自然语言→代码 | 手动 prompt | 自动合成 | RAG 锚定 + 自校正 |
| 验证 | 人工审查 | 自动 FEA + 人工复核 | CCAR 合规自动检查 + 人签字 |
| 优化 | 单次 SLSQP | surrogate 加速 | 多目标 Pareto 前沿 |
| 审计 | 无 | 代码版本控制 | 完整决策轨迹 + 约束日志 |
| 治理 | 无 | 人工审批流 | 舰队级策略管理 + 自动传播 |

### 9.2 知识缺口（诚实标注）

1. **浙大 MDO Agent 代码未开源**：arXiv 论文无 code repo，可复现性待验证
2. **UMich OpenAeroStruct LLM Agent 无定量 benchmark**：官方页无收敛速度/准确率对比数字
3. **Hasan & Nguyen 框架未开源**：Array 2026 是学术论文，无 code repo
4. **CMAD 论文只看到摘要**：Elsevier Measurement 全文未获取，DIC 表征细节待确认
5. **国产适配空白**：CCAR 场景下无公开 multi-agent DT 标准，DTC 是北美联盟

### 9.3 下一步动作评估

- ✅ **应 patch aircraft-structural-digital-twin skill**：补 agentic MDAO 子章节（七层框架 + 四 Agent 模式 + 治理十法）
- ⚠️ **暂不新建 skill**：具体代码尚未跑通，等浙大/UMich 开源后再 skill 化
- ✅ **应写入 memory**：UMich + 浙大 + Hasan + DTC 四个权威参照点
- ✅ **应加入 sniff-interests L3**：DTC ODP Composability Framework（航空多 Agent 组合标准，CCAR 空白）

---

## 附：关键引用

1. Guo B, Li W, Luo J, et al. "A Multidisciplinary Design and Optimization (MDO) Agent Driven by Large Language Models." *arXiv 2511.17511*, 2026. https://arxiv.org/html/2511.17511v1
2. UMich IDEAS Lab. "OpenAeroStruct LLM Agent." 2025. https://www.gokcincinar.com/software/openaerostruct
3. Cleeay C, Ram J, Cinar N. "Aerodynamic Design and Optimization via a Specialized Agentic Framework." *PP 2025*. https://deepblue.lib.umich.edu/bitstreams/1986c947-bc2b-4a9b-9a3e-2ee66df5d98c/download
4. Hasan A, Nguyen DT. "Integrating agentic AI and digital twins for intelligent decision-making systems." *Array*, 2026. DOI: 10.1016/j.array.2026.100721
5. Digital Twin Consortium. "NARTP Strategic Innovation Center and DTC Collaborate to Test and Develop Multi-Agent AI Digital Twins Across Aviation." 2026-04-29. https://www.digitaltwinconsortium.org/press-room/nartp-strategic-innovation-center-and-digital-twin-consortium-collaborate-to-test-and-develop-multi-agent-ai-digital-twins-across-aviation
6. van Schalkwyk P, Whiteley S. "The Industrial AI Agent Manifesto: Governance Requirements for Trustworthy Autonomous Operations." *DTC Composability Framework Working Group*, 2026-02. https://www.digitaltwinconsortium.org/2026/02/the-industrial-ai-agent-manifesto-governance-requirements-for-trustworthy-autonomous-operations
7. "A novel enhanced digital image correlation framework for structural health monitoring of aircraft." *Measurement*, Elsevier, 2025. https://www.sciencedirect.com/science/article/abs/pii/S0263224125026235
8. "Agentic AI for Digital Twin." *AAAI 2025 Demo*. IBM Research. arXiv 2605.26066

---

## ✅ 落实情况

| 借鉴点 | 动作 | 状态 |
|--------|------|------|
| Agentic MDAO 七层框架 + 四 Agent 模式 | patch aircraft-structural-digital-twin skill references | ✅ 已落实（Phase 3 proactive-learn） |
| DTC ODP Composability Framework | 加入 sniff-interests L3 跟踪 | ✅ 已落实（Phase 3 proactive-learn） |
| 治理十法 → agent-security-governance 航空 profile | 待落实（需评估具体改法） | ⚠️ 已记录，待落实 |
| CMAD 统一表征 → SHM 项目评估 | 待落实（需评估现有项目） | ⚠️ 已记录，待落实 |


## 相关笔记

- 航空结构 Agentic MDAO 深度探索版（~/explore 2026-09-15-agentic-mdao-aircraft-structure-frontier）— 同日姊妹篇：本篇为书签管线版，该篇为 Phase 3 深度版
- [门控记忆路由多Agent编排](./2026-09-14-门控记忆路由多Agent编排.md) — 多Agent编排的基建层视角
