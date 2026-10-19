# CAD/CAE AI 布局增量更新（2026-09-16）：Virtual Companions Competency 框架 × Neural CAD 基础模型 × CVPR2026 学术突破 × Ansys 2026 R1

> **来源**：3DS 官方/Softprom/AEC Magazine/Ansys 官方/CVPR 2026/arXiv
> **记录日期**：2026-09-16
> **增量性质**：本次为 08-13 CAD 厂商 AI 布局三篇笔记 + 08-25 飞机结构 AI 知识图谱的增量更新（34 天后追踪）

**标签**：#CAD #CAE #VirtualCompanions #NeuralCAD #CVPR2026 #Ansys2026R1 #GeomAI #Competency #基础模型 #工业AI #增量笔记

---

### 7 模块索引

- 模块 | 对应章节
- tag 标签 | 头部标签行
- 出处 | 头部出处行
- 内容整理 | 第一~四章（四大增量逐项展开）
- 查询拓展 | 第五章（概念背景补充）
- 归纳总结 | 第六章（增量与旧笔记差异矩阵）
- 趋势判断 | 第七章（4 条趋势预测）
- 关联分析 | 第八章（与历史笔记和项目的映射）
- 拓展应用推荐 | 第九章（落地行动建议）
- 指南分析 | 第十章

---

## 前序笔记

- [全球 CAD 厂家 AI 布局现状-达索西门子PTC-Autodesk对比](2026-08-13-全球CAD厂家AI布局现状-达索西门子PTC-Autodesk对比.md) — 08-13 第一篇（8 英文权威信源交叉验证版）
- [CAD 厂家 AI 平台化布局-达索西门子战略深度分析](2026-08-13-CAD厂家AI平台化布局-达索西门子战略深度分析.md) — 08-13 第二篇（中文信源版）
- [达索系统与西门子 CAD-AI 战略对比](2026-08-13-达索系统与西门子CAD-AI战略对比.md) — 08-13 第三篇（达索/西门子双雄深度对比）
- [车身结构智能层 C123 到飞机结构设计迁移研究](2026-08-25-车身结构智能层C123到飞机结构设计迁移研究-PhysicsAI前置结构智能.md) — 08-25（PhysicsAI 航空迁移）
- [AeroStruct-FM 飞机结构垂域模型策划书精读](2026-08-25-AeroStructFM飞机结构垂域模型策划书精读-四层一闭环四大Agent五级验证.md) — 08-25（飞机结构 AI 知识图谱）

---

## 摘要

本次为 34 天后的增量追踪。领域未出现颠覆性范式转移，但 **4 条显著进展** 补全了 08-13 笔记的结构性盲区：

1. **达索 Virtual Companions 的 19 Competencies 框架正式发布**（2026-07-23）—— 旧笔记只列了 LEO 的功能清单，未覆盖 Competency 作为"知识封装单元"的系统架构
2. **Autodesk Neural CAD 基础模型首次深度阐述**（2026-06-16 AEC Magazine）—— 旧笔记仅列 Fusion 360/Forma 表层，未触及"Neural CAD 作为独立基础模型品类"的战略定位
3. **CVPR 2026 学术爆发**：CADFS（45 万 CAD 模型×15 操作）、IterCAD（闭环多模态 Agent）、CAD-Refiner —— 旧笔记完全未覆盖学术前沿
4. **Ansys 2026 R1 首次纳入**：GeomAI 概念探索 + SimAI 双层级 + Synopsys 合并首成果 —— 旧笔记完全未覆盖 Ansys

---

## 一、内容整理（四大增量逐项展开）

### 1.1 达索 Virtual Companions — 19 Competencies 框架（增量）

> **与旧笔记的差异**：08-13 笔记详细列出了 LEO 在 CATIA/DELMIA 中的 21 项功能清单（3D Navigation → Generate Diagrams），但未覆盖 Competency 作为系统架构层的正式框架。

**2026-07-23 官方发布**（3ds.com 新闻稿 + Softprom 分发报告）：

三款 Virtual Companions（AURA/LEO/MARIE）正式全球上线 3DEXPERIENCE 平台，同时发布 **19 个 Competencies** 框架——每个 Competency 定义为"一组技能（skills）的集合"，覆盖：

- **业务**（Business）
- **产品设计**（Product Design）
- **工程**（Engineering）
- **仿真**（Simulation）
- **制造**（Manufacturing）
- **运营**（Operations）

> "As these companions are released, we are also going to release more and more competencies, and we are going to release each competency with a certain number of skills."
> — Manish Kumar, SOLIDWORKS CEO

**关键架构发现：Virtual Twin Factories**

旧笔记未覆盖的新概念——达索将 Virtual Twin Factories 定义为"新型工厂"：

- **Virtual Companions = 工人**（on par with humans）
- **Generative Experiences = 高度自动化流程**
- **Virtual Twin as a Service = 预定义行业世界模型**

> "Virtual Twin Factories are the new factories bringing together Virtual Companions as workers on par with humans, Generative Experiences as highly automated processes, and Virtual Twin as a Service as predefined Industry world models."

**增量价值**：08-13 笔记中"达索把工业软件 Agent 化"的判断在此得到官方架构确认——Competency = Hermes Skill 的工业版正式落地。旧笔记中的"Know-how 计费单元"从概念变为 19 个可枚举的 Competency 实体。

---

### 1.2 Autodesk Neural CAD 基础模型（增量）

> **与旧笔记的差异**：08-13 笔记对 Autodesk 的覆盖仅 1 行——"Fusion 360 生成式设计、AI 参数优化 / Forma AI 建筑布局生成"。完全未触及 Neural CAD 作为独立基础模型品类的战略定位。

**Mike Haley（Autodesk SVP Research）2026-06-16 AEC Magazine 深度文章**：

**核心命题**：Neural CAD 不是"给现有 CAD 加 AI 功能"，而是**全新品类的 AI 基础模型**——直接对 CAD 几何推理和生成，而非用 LLM 包一层。

> "Imagine Midjourney for CAD, but with fully editable results and a smoother, more intuitive human-to-computer interface."
> — Mike Haley, SVP Research, Autodesk

**关键特征**：
- **多模态输入**：说话、打字、画图、上传图片均可启动
- **直接几何推理**：不是 LLM→代码→CAD 的间接路径，而是模型直接对曲面/边/拓扑推理
- **可编辑输出**：生成的是一等公民 CAD 几何（first-class editable CAD geometry），可立即在 Fusion/ Forma 中参数化编辑
- **完整历史链**：对于特定任务，生成完整的 CAD 命令序列（design history）——不只是结果，还有可追溯的过程

**World Labs $2 亿投资**（2026 年宣布）：
- Autodesk 向 World Labs 投资 $200M
- 合作构建"基础世界模型"——能感知、生成、推理并与 3D 世界交互
- 目标：通过共享发现和协作交付 Neural CAD 平台

**15 年研究积累**：Autodesk AI Lab 成立于 2018 年，但 Neural CAD 研究超过 15 年——这些模型需要全新的神经网络架构，不是 fine-tune 现有 LLM 能实现的。

> "These neural CAD AI models are incredibly difficult to train and need entirely new forms of neural network architectures."

**增量价值**：旧笔记将 Autodesk 列为"AEC+MFG 双轨"的追随者角色，但 Neural CAD 基础模型定位使其与达索 Industry World Model、西门子 PhysicsAI 形成三足鼎立——各自走不同的技术路线：

- 达索：物理世界模型 + Competency 封装
- 西门子：几何深度学习 + 扩散模型生成
- Autodesk：Neural CAD 直接几何推理 + World Labs 世界模型

---

### 1.3 CVPR 2026 学术爆发：CAD 基础模型集群（增量）

> **与旧笔记的差异**：08-13 笔记完全未覆盖学术前沿。旧笔记聚焦工业厂商战略，学术研究是结构性盲区。

**CADFS（CVPR 2026）— 大规模 CAD 程序数据集与框架**

- **团队**：Pyatov et al.（Skoltech + TU Wien + Onshape）
- **数据集**：450,000 个真实 CAD 模型，覆盖 15 种建模操作（远超传统 sketch-extrude 两操作）
- **表示方法**：FeatureScript（Onshape 原生脚本语言）—— 首次突破 sketch-extrude 限制
- **成果**：在 VLM 上 fine-tune 后，text-conditioned CAD 生成和 image-based reconstruction 均达 SOTA
- **论文**：CVPR 2026 Open Access

**IterCAD（arXiv:2606.13368）— 闭环多模态 CAD Agent**

- **核心创新**：从 open-loop one-shot 生成转向 **closed-loop iterative** 生成
- **框架**：多模态 Agent + 可执行 CAD sandbox 的多轮交互
- **三大任务**：Drawing-to-Code / Text-to-Code / Image-to-Code
- **意义**：首次将"设计师迭代修改"的真实工作流形式化为 Agent 交互范式——与达索 LEO"Anything you can do in CATIA, LEO can do at scale"形成学术对应

**CAD-Refiner（CVPR 2026）— 统一生成+编辑框架**

- **团队**：Yuan et al.
- **核心**：将 CAD 生成和迭代编辑统一在一个框架中（以往是分离的两个任务）
- **论文**：CVPR 2026, pages 3244-3253

**STEP-LLM（DATE 2026）— 自然语言→STEP 标准模型**

- **论文**：arXiv:2601.12641, accepted to DATE 2026
- **核心**：从自然语言直接生成标准 STEP 格式 CAD 模型

**增量价值**：学术前沿揭示了工业厂商战略背后的技术成熟度——CADFS 的 45 万模型×15 操作数据集说明训练数据瓶颈已被突破；IterCAD 的闭环交互范式与达索 LEO 的 Competency 架构在方法论上趋同。**工业产品（LEO/PhysicsAI）与学术论文（IterCAD/CADFS）在 2026 年同步收敛到"迭代式多模态 Agent"范式。**

---

### 1.4 Ansys 2026 R1 — 首次纳入分析版图（增量）

> **与旧笔记的差异**：08-13 笔记完全未覆盖 Ansys。四巨头对比中 Ansys 缺席。

**Ansys 2026 R1 核心增量（官方 Release Highlights）**：

**GeomAI — AI 概念探索**
- 从参考设计中学习 → 生成新颖概念 → 精简探索流程
- 定位：概念设计阶段的 AI 生成工具（与西门子 PhysicsAI Generate 同层竞争）

**SimAI 双层级架构**
- **SimAI Premium**：完整云端规模化解决方案
- **SimAI Pro**：桌面版，快速本地 AI 训练和预测
- 战略含义：AI 仿真不再只走云端，本地部署选项对标西门子 Simcenter 本地+云策略

**Synopsys 合并首成果**
- Ansys 被 Synopsys 收购后的首个联合发布版
- 半导体领域：Synopsys 2026.03 + Ansys 半导体产品联合方案
- 三大方向：增强多物理设计能力 / 更高精度多物理签核 / 高速模拟和 3DIC 新电磁能力
- 安全分析：Ansys medini analyze + Synopsys VC-FSM 统一功能安全工作流

**Engineering Copilot in medini analyze**
- 安全分析工作流中的 AI 助手
- 智能辅助 + 集中式资源 + 知识库访问

**AnsysGPT**
- 多语言虚拟助手，24/7 回答产品/物理/工程问题
- 仅面向商业客户

**optiSLang 2026 R1 — SimAI 全集成**
- SimAI 云平台完全集成进 optiSLang 工作流
- 工程师在 optiSLang 内直接训练 AI 模型预测高保真运行间的响应
- DLS 方法校准模型匹配实测行为

**Discovery 2026 R1 — 前置仿真增强**
- 流体网格改进：锐边捕捉 + 薄结构捕捉
- 流体虚拟墙：简化热建模
- CHT with Joule Heating + 灵敏度分析

**Structures 2026 R1**
- Mechanical：Direct Morphing + GPU 资源预测 + Sherlock 无缝访问
- LS-DYNA：电池热建模 + (S-)ALE 网格 + 后处理加速
- Motion：行星齿轮建模增强 + 求解器加速

**MBSE 2026 R1**
- SysML v2 语言支持扩展
- Minerva：更清洁界面 + 更快数据导航 + 更智能表单 + 更强治理

**增量价值**：Ansys 2026 R1 使四大厂商对比矩阵从"四巨头"变为"五巨头"——GeomAI 与西门子 PhysicsAI Generate 直接竞争概念探索市场；SimAI 双层级对标西门子本地+云策略；Synopsys 合并使 Ansys 独家拥有半导体+仿真跨域能力。旧笔记的四大对比矩阵需要升级为五维。

---

## 二、查询拓展

### 2.1 Competency 架构 vs Skill 架构的深层对应

08-13 笔记已发现"达索 LEO Competency = Hermes Skill"的范式平行。本次 19 Competencies 框架的发布进一步确认：

- **达索 Competency**：一组 skills 的集合，有输入/输出/约束/失败处理，可被 AI Agent 自动发现和调用
- **Hermes Skill**：SKILL.md + 脚本/模板/引用，trigger 条件自动匹配，delegate_task 编排

差异在于工业级 Competency 需要额外的**物理约束验证**和**适航合规审计**——这是通用 Agent Skill 目前不具备的维度。

### 2.2 Neural CAD 的"直接几何推理"技术路线

Autodesk 声称 Neural CAD 不走 LLM→代码→CAD 间接路径，而是模型直接对几何推理。这在学术上对应：
- **几何深度学习（Geometric Deep Learning）**：西门子 PhysicsAI 的底层技术
- **3D 原生 Transformer**：直接处理点云/mesh/BREP 表示，而非投影到 2D
- **World Labs 世界模型**：Autodesk 投资 $2亿 的方向——能感知、生成、推理并与 3D 世界交互

这条路线与达索 Industry World Model（物理约束）和西门子 PhysicsAI（历史仿真数据训练）形成第三条路径：**从几何本身学习**而非从物理约束或仿真数据学习。

### 2.3 CVPR 2026 CAD 生成技术的成熟度信号

CADFS 数据集（45 万模型×15 操作）的规模说明：
- 传统 sketch-extrude 两操作的 CAD 生成已被突破
- FeatureScript 表示法使 VLM 能生成复杂设计历史（非简单几何体）
- 学术界已具备训练工业级 CAD 生成模型的数据基础

这与 08-13 笔记中"达索 LEO 的 Part Generation 从 BREP 自动生成特征规范"形成呼应——工业产品和学术研究在同一时间窗口达到了相近的能力边界。

### 2.4 Ansys-Synopsys 合并的工业软件格局影响

Ansys 被 Synopsys 收购是 08-13 笔记时尚未完成的行业事件。2026 R1 是合并后首个联合发布版，影响：
- **半导体+仿真跨域**：Synopsys 芯片设计 + Ansys 多物理仿真 = 芯片到系统全链
- **安全分析独占**：medini analyze + VC-FSM 统一功能安全工作流——航空/汽车认证领域
- **竞争格局变化**：Ansys 不再是纯仿真公司，而是 Synopsys 旗下的仿真+半导体事业部

---

## 三、归纳总结

### 3.1 增量与旧笔记差异矩阵

| 增量主题 | 08-13 笔记覆盖 | 本次新增 | 增量性质 |
|----------|---------------|---------|---------|
| 达索 Competency 框架 | LEO 21 项功能清单 | 19 Competencies 系统架构 + Virtual Twin Factories 概念 | **架构层补全** |
| Autodesk Neural CAD | 1 行 Fusion/Forma 表层 | Mike Haley 深度阐述 + World Labs $2亿 + 15年研究 | **战略层重构** |
| 学术 CAD 基础模型 | 完全未覆盖 | CADFS/IterCAD/CAD-Refiner/STEP-LLM 四篇 | **结构性盲区补全** |
| Ansys | 完全未覆盖 | 2026 R1 全量：GeomAI/SimAI双层级/Synopsys合并/AnsysGPT | **新厂商纳入** |

### 3.2 五巨头 AI 路线升级矩阵（08-13 四巨头→五巨头）

- **达索**：Industry World Model + 19 Competencies + Virtual Twin Factories → 知识平台化
- **西门子**：PhysicsAI Generate（扩散模型）+ Altair $100亿整合 → 物理感知生成
- **Autodesk**：Neural CAD 基础模型 + World Labs $2亿 → 直接几何推理（新增战略定位）
- **PTC**：Onshape Labs + Amazon Bedrock → 云原生快速迭代（无增量，停滞）
- **Ansys**（新增）：GeomAI + SimAI 双层级 + Synopsys 合并 → 概念探索+仿真+半导体跨域

### 3.3 三条技术路线的收敛与分化

```
路线 A：物理世界模型（达索）
  Competency 封装 + Industry World Model + 物理约束验证
  → 适合高合规行业（航空/医疗）

路线 B：几何深度学习（西门子）
  历史仿真数据训练 + 扩散模型生成 + 1000x 加速
  → 适合仿真密集型行业（汽车/制造）

路线 C：Neural CAD 直接推理（Autodesk）
  全新神经网络架构 + World Labs 世界模型 + 15年积累
  → 适合创意设计/AEC（建筑/产品/动画）

路线 D：AI 概念探索（Ansys）
  GeomAI 从参考设计学习 + SimAI 双层级 + Synopsys 半导体跨域
  → 适合多物理/芯片/安全认证
```

---

## 四、趋势判断

### 趋势 1：Competency/Skill 范式从 Agent 框架扩散到工业软件

08-13 笔记发现"达索正在做的事本质上是把工业软件 Agent 化"。本次 19 Competencies 框架 + Virtual Twin Factories（Companion=工人）使这一判断从推论变为官方架构。**Competency 作为"知识封装单元"正在成为工业软件和 AI Agent 的共享原语。**

依据：3DS 官方新闻稿明确将 Virtual Companions 定位为"workers on par with humans"，Competency 有正式的 skills 集合定义和持续发布路线图。

### 趋势 2：CAD 生成从"一次性"转向"迭代闭环"

CVPR 2026 两篇论文（IterCAD/CAD-Refiner）和达索 LEO 的 Generative Experiences 同步转向迭代式生成。**open-loop one-shot → closed-loop iterative 是 2026 年 CAD AI 的范式跃迁。**

依据：IterCAD 论文明确指出"existing methods predominantly rely on open-loop, one-shot generation, creating a mismatch with iterative real-world practices"——学术和工业在同一时间窗口识别了同一个问题。

### 趋势 3：Neural CAD 基础模型成为第三极

旧笔记将 Autodesk 列为"AEC+MFG 双轨"的追随者。Neural CAD 基础模型 + World Labs $2亿投资使其升级为与达索/西门子并列的技术路线——三条路径（物理世界模型/几何深度学习/直接几何推理）各有独立的底层架构和投资规模。

依据：Mike Haley 原话"these neural CAD AI models need entirely new forms of neural network architectures"——这不是 fine-tune LLM，是全新的模型品类。

### 趋势 4：Ansys-Synopsys 合并重塑仿真竞争格局

Ansys 2026 R1 是合并后首个联合版，使仿真市场从"达索 SIMULIA vs 西门子 Simcenter vs Ansys"三足鼎立变为"达索 vs 西门子（+Altair） vs Synopsys-Ansys"三角+半导体跨域。GeomAI 直接进入概念探索市场与西门子 PhysicsAI Generate 竞争。

依据：2026 R1 Release Highlights 明确列出 GeomAI 为"AI concept-exploration solution that learns from reference designs to generate novel concepts"。

---

## 五、关联分析

### 5.1 与 08-13 三篇笔记的关联

本笔记是 08-13 三篇的增量更新，差异矩阵见第三章。核心关系：
- **补全**：Competency 框架使旧笔记"Know-how 计费单元"概念变为可枚举实体
- **重构**：Autodesk 从"追随者"升级为"第三极"
- **扩展**：Ansys 从"未覆盖"变为"第五巨头"

### 5.2 与 08-25 飞机结构 AI 知识图谱的关联

08-25 AeroStruct-FM 提出的模型族 M_AS={LLM, Geo, Physics, Operator, Damage, Twin, Agent} 与本次增量有三处映射：
- **M_Geo（几何/拓扑）** ← Neural CAD 直接几何推理 + CADFS FeatureScript 表示
- **M_Agent（决策代理）** ← 达索 19 Competencies + IterCAD 闭环 Agent 范式
- **M_Physics（物理知识）** ← Ansys GeomAI 概念探索 + SimAI 双层级

### 5.3 与项目关联

- `~/uclaw/project/catia-caa/` — CATIA CAA 二次开发，Competency 框架直接影响"从写 CAA 插件到封装 Competency"的转型方向
- `~/uclaw/project/struct-gen/` — 航空结构 AI 设计 Agent，AeroStruct-FM 模型族的落地实现

### 5.4 与 Hermes Agent 的元启发

19 Competencies 框架进一步确认了 08-13 笔记的发现：达索的 Competency 架构与 Hermes Skill 系统高度同构。增量在于：
- **Competency 有明确的版本路线图**（"release more and more competencies, each with a certain number of skills"）→ Hermes Skill 也应有版本化路线
- **Virtual Twin Factories = Companion + Generative Experience + VTaaS** → 对应 Hermes 的 Agent + 自动化流程 + 领域知识库三层

---

## 六、金句摘录

> 「Virtual Twin Factories are the new factories bringing together Virtual Companions as workers on par with humans, Generative Experiences as highly automated processes, and Virtual Twin as a Service as predefined Industry world models.」— 3DS 官方新闻稿

> 「Imagine Midjourney for CAD, but with fully editable results.」— Mike Haley, Autodesk SVP Research

> 「Existing automated methods predominantly rely on open-loop, one-shot generation, creating a mismatch with iterative real-world practices.」— IterCAD 论文

---

## 七、行动启示

- **启示** | **行动**
- 达索 19 Competencies 框架正式落地 | 跟踪 Competency 发布路线图，对比 Hermes Skill 演化路径
- Autodesk Neural CAD 基础模型 | 关注 World Labs 模型发布时间线，评估对 Fusion API 的影响
- CVPR 2026 CADFS 数据集公开 | 评估 45 万 CAD 模型数据集对航空结构训练数据的补充价值
- IterCAD 闭环 Agent 范式 | 对比 AeroStruct-FM 的 M_Agent 设计，是否需要引入闭环迭代机制
- Ansys 2026 R1 GeomAI | 跟踪 GeomAI 与西门子 PhysicsAI Generate 的概念探索市场竞争
- Ansys-Synopsys 合并 | 评估半导体+仿真跨域对航空电子设备仿真链的影响

---

## 八、拓展应用推荐

### 8.1 飞机结构 AI 设计的 Competency 封装

基于达索 19 Competencies 框架，AeroStruct-FM 项目可参考将 M_Agent 拆分为：
- **结构概念设计 Competency**（对应 C1 拓扑/载荷路径）
- **多学科优化 Competency**（对应 C2 尺寸/总布置）
- **详细件设计 Competency**（对应 C3 详细/可制造性）
- **仿真验证 Competency**（对应 SimAI/optiSLang AI 预测）
- **适航合规 Competency**（对应 medini analyze + VC-FSM）

### 8.2 IterCAD 闭环范式在航空结构的适用性

IterCAD 的多轮交互（Agent ↔ CAD sandbox）可直接映射到航空结构设计迭代：
- Drawing-to-Code → 工程草图→CATIA 模型
- Text-to-Code → 设计要求→参数化模型
- Image-to-Code → 参考机型照片→初始布局

---

## 九、指南分析

本笔记的评估维度：

- **新颖性**：4/5 — 19 Competencies 框架和 Neural CAD 定位是 08-13 笔记的结构性补全，CVPR 2026 学术爆发和 Ansys 纳入是全新增量
- **证据强度**：5/5 — 基于 3DS 官方新闻稿、AEC Magazine 专家文章、CVPR 2026 论文、Ansys 官方 Release Highlights
- **可操作性**：3/5 — 增量主要是战略层面，落地操作需要跟踪后续产品发布
- **与旧笔记差异清晰度**：5/5 — 每个增量主题都明确标注了与 08-13/08-25 笔记的差异

---

## 十、参考来源（增量）

- 3DS 官方 Virtual Companions 新闻稿 — https://www.3ds.com/newsroom/press-releases/dassault-systemes-expands-3dexperience-ai-native-agentic-platform-new-virtual-companion-skills-co-engineer-humans
- Softprom 分发报告（19 Competencies + VT Factories） — https://softprom.com/dassault-systemes-3dexperience-virtual-companions-ai
- 3DS Blog: Meet Your New AI Experts — https://blog.3ds.com/brands/enovia/meet-your-new-ai-experts-on-the-3dexperience-platform
- Engineering.com: A tale of three chatbots — https://www.engineering.com/a-tale-of-three-chatbots-aura-leo-and-marie
- AEC Magazine: Neural CAD AI foundational models (Mike Haley) — https://aecmag.com/opinion/neural-cad-ai-foundational-models
- Autodesk 官方 Neural CAD 公告 — https://adsknews.autodesk.com/en/news/upcoming-3d-generative-ai-foundation-models
- CADFS (CVPR 2026) — https://openaccess.thecvf.com/content/CVPR2026/html/Pyatov_CADFS_A_Big_CAD_Program_Dataset_and_Framework_for_Computer-Aided_CVPR_2026_paper.html
- IterCAD (arXiv:2606.13368) — https://arxiv.org/abs/2606.13368
- CAD-Refiner (CVPR 2026) — https://openaccess.thecvf.com/content/CVPR2026/html/Yuan_CAD-Refiner_A_Unified_Framework_for_CAD_Generation_and_Iterative_Editing_CVPR_2026_paper.html
- STEP-LLM (arXiv:2601.12641, DATE 2026) — https://arxiv.org/abs/2601.12641
- Ansys 2026 R1 Release Highlights — https://ansys.synopsys.com/products/release-highlights
- Ansys optiSLang 2026 R1 Blog — https://www.ansys.com/zh-cn/blog/ansys-2026-r1-whats-new-ansys-optislang-software
- LLM for CAD Survey (arXiv:2505.08137v2) — https://arxiv.org/html/2505.08137v2

## 相关笔记

- [全球 CAD 厂家 AI 布局现状-达索西门子PTC-Autodesk对比](2026-08-13-全球CAD厂家AI布局现状-达索西门子PTC-Autodesk对比.md)
- [CAD 厂家 AI 平台化布局-达索西门子战略深度分析](2026-08-13-CAD厂家AI平台化布局-达索西门子战略深度分析.md)
- [达索系统与西门子 CAD-AI 战略对比](2026-08-13-达索系统与西门子CAD-AI战略对比.md)
- [车身结构智能层 C123 到飞机结构设计迁移研究](2026-08-25-车身结构智能层C123到飞机结构设计迁移研究-PhysicsAI前置结构智能.md)
- [AeroStruct-FM 飞机结构垂域模型策划书精读](2026-08-25-AeroStructFM飞机结构垂域模型策划书精读-四层一闭环四大Agent五级验证.md)
- [全球十大 CAD 几何建模内核](2026-08-12-全球十大CAD几何建模内核-NX-CATIA-SolidWorks.md)
→ 相关：2026-09-16-CAD厂商AI布局全景研究完整版-原文全量二十章与增量补充.md（原文全量完整版，查厂商细节以此为准）
