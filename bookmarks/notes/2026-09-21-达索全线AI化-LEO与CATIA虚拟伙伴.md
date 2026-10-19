# 达索全线AI化：LEO替你画图，CATIA听你说话，工程师还剩什么？

> 原文：微信公众号（工业数智化领域系列）
> URL_ID: mid=2247484219&sn=890da9fae8f16834af5750470a2c4b5c
> 阅读日期：2026-09-21 | 评分：★★★★☆（4.5/5，行业洞察+工程落点双高）
> tag: #AI #CAD #达索系统 #CATIA #世界模型 #物理AI #工业AI #生成式设计

## 一、核心内容摘要

达索系统正在把 AI 从"独立功能按钮"升级为 3DEXPERIENCE 平台的**原生交互方式**，核心架构是三个分工明确的虚拟伙伴（Virtual Companions）：

| 伙伴 | 定位 | 嵌入位置 | 职责 |
|------|------|----------|------|
| **LEO** | 执行型 | CATIA / SOLIDWORKS 三维环境 | 生成式装配、AI 工程图、BREP 转参数化、Image to Mesh、材料管理 |
| **AURA** | 知识型 | ENOVIA 等管理模块 | 项目管理、流程串联、跨部门知识梳理（"哪个零件卡审批了"） |
| **Marie** | 生命科学型 | BIOVIA | 材料科学验证、制药公式合规检查 |

关键跨越发生在 AURA→LEO 之间：从"动嘴"（告诉你怎么做）到"动手"（直接替你画图+仿真）。

**标志性演示**（2026-02 3DEXPERIENCE World）：SOLIDWORKS CEO Manish Kumar 向 LEO 描述"设计一个支撑水塔的钢架结构，考虑马萨诸塞州风载"——不到 5 分钟返回完整装配体、3D 草图、结构系统特征、经验证的线性静力分析、重量/占地面积/安全系数报告。原话："We are going from requirements to delivering a full functional model."

**技术底座**：达索 CEO 与黄仁勋联合宣布长期战略合作——"shared industrial architecture for mission-critical AI"。LEO 被设计为**基于物理规律与因果逻辑推理**（reason with physics and causality），而非仅靠文本模式；明确拒绝幻觉创作，定义为"经科学验证的工业世界模型（Industry World Models）"。

## 二、CATIA 本体的 AI 重构（三个层次）

1. **生成式设计体验**
   - 草图生成式约束：底层 GNN 学习庞大工业标准图纸数据集，粗略草图→自动生成最符合工程标准的几何约束
   - 功能驱动生成设计（GDE Role）：输入 3D 边界空间+载荷+材料+制造工艺（3D打印/铸造），像生物骨骼生长一样数小时内生成成百上千种拓扑结构
2. **建模意图预测**
   - Technia 命令智能预测：分析操作上下文，预测下一步指令并推送快捷工具栏
   - 机械接口预测：自动分析几何表面运动学关系，预测轴孔配合/法兰连接，批量生成装配约束
3. **工业知识激活（Knowledgeware 升级）**：40 年知识库+大模型融合，宣称 **80% 核心零部件标准化复用**、产品上市后**质保成本降低 10%**

## 三、全线 AI 化产品矩阵

| 产品线 | AI 能力 |
|--------|---------|
| SOLIDWORKS | 虚拟伙伴（出图、装配、转模型） |
| CATIA | 虚拟伙伴、自然语言建模、智能助手 |
| SIMULIA | 一句话仿真设置、AI 网格加速 |
| NETVIBES | 数据智能分析（打通 ERP/MES/PLM 与外部互联网）、研发优先级 |
| 3DEXPERIENCE | 全平台 AI 连接 |

**交付模式转变**：放弃"每年 10 月一次大发布"，改为 Functional Deliveries 全年持续交付（每年 5 次增强发布）——AI 能力每个 Service Pack 都可能上新。

## 四、达索 vs PTC 路线对比（本文最有分析价值的部分）

| 维度 | PTC（text-to-code-to-CAD） | 达索（AI Agent 直接操作 CAD） |
|------|---------------------------|-------------------------------|
| 核心思路 | AI 写 FeatureScript 参数化代码，代码驱动 Onshape 造模 | LEO 不写代码，直接在 3D 里搭装配、出图、设仿真 |
| 标志案例 | 管壳式换热器：2100 行 FeatureScript、532 参数、节省 150-200 工程小时 | 水塔钢架：5 分钟需求→建模+仿真+验证全套报告 |
| 优势 | 透明、可审计、可追溯 | 直觉、闭环快、体验震撼 |
| 劣势 | 链路长 | 黑盒程度高 |
| 适配行业 | 航空航天等高合规行业更有底气 | 快速迭代的设计场景 |

作者判断：短期达索体验更震撼，长期 PTC 可追溯性在高合规行业更有底气——非绝对，Siemens/Autodesk/Leap 71/Prometheus 各走各路，长期观察。

## 五、💡 对我们的价值分析

### ✅ 已在做的（印证方向）
- **StructGen（struct-gen-agent skill）**："从需求到 CATIA 模型的全自动编排，支持 CCAR-25"——与 LEO 的"requirements → full functional model"是同一命题，且我们绑定了适航合规约束，比通用 LEO 在航空垂域更聚焦
- **catia-automation / catia-caa**：pycatia COM 自动化与 CAA 二次开发底座已在手，等于掌握了 LEO"动手层"的本地接口
- **Hermes 多 Agent 编排**：AURA/LEO/Marie 的"知识型/执行型/领域型"三伙伴分工 = 我们 Agents/Skills/Hooks 三原语 + 编排器模式的工业界镜像

### ⚠️ 可改进的（差距）
- 达索的 GNN 草图约束（学习工业标准图纸数据集）我们没有对应能力——现有 CATIA 接入是命令级，缺"设计意图识别"层
- "一句话设置 Abaqus 仿真"提示 SIMULIA 侧也在 Agent 化：StructGen 目前只到建模，仿真链（强度校核/静力分析）是下一站
- Functional Deliveries 每年 5 发的节奏意味着**达索 AI 能力月月在变**，跟踪机制需要从"一次性调研"升级为"季度复读"

### 🔥 重点行动
1. **StructGen 对标补课**：把 LEO 演示的输出物清单（装配体+3D草图+结构特征+静力分析+安全系数报告）设为 StructGen 的验收物模板——这是工业界刚定义的"完整交付"标准
2. **代码层 vs 操作层双轨**：借鉴 PTC 路线的可审计性，StructGen 保留"生成自动化脚本/CAA 调用序列"作为审计链——正好契合适航构型管理对可追溯的硬要求，这是我们对达索黑盒路线的差异化优势
3. **知识库激活**：达索"80% 标准件复用"数字提醒——企业 40 年图纸库+RAG 是我们已有基建，可先做"相似零部件检索"小闭环

## 内容整理（归纳总结与关联分析）

**归纳总结**：本文核心可压缩为一句话——达索把 AI 从功能按钮升级为原生交互（LEO 执行/AURA 知识/Marie 领域三伙伴分工），底座是与 NVIDIA 合建的"工业世界模型"，与 PTC 的 text-to-code-to-CAD 形成"操作层 vs 代码层"两条路线之争。五个关键数字：5 分钟需求到全功能模型、80% 标准件复用、10% 质保成本下降、每年 5 次增强发布、40 年知识库。

**关联分析**：三伙伴分工 = 编排器+执行 Agent+知识层的三原语架构在工业软件的镜像；达索黑盒操作层 vs PTC 可审计代码层的分歧，本质是"交互效率 vs 合规追溯"的取舍——适航构型管理场景天然站后者，这决定了 StructGen 的差异化路线选择（保留脚本审计链）。

## 六、查询拓展

- LEO 的 GNN 草图约束底层：搜索 "sketch generative constraint GNN CAD"（技术报告未见公开，需追 SIGGRAPH/ASME 论文）
- NVIDIA×达索 "Industrial World Model" 架构细节：GTC 2026 相关 session
- PC-DMIS/SIMULIA 一句话仿真的边界案例：搜 "SIMULIA AI simulation setup 2026"
- 对比阅读：Leap 71（NURBS 编程式设计）、Prometheus（贝索斯投资）、Siemens NX AI（另一条路线）

## 七、趋势判断

1. **CAD 交互范式迁移已过临界点**：2026 年 PTC/Autodesk/达索/西门子全部押注 AI 原生交互，"拉伸切除"式手工建模进入替代倒计时，但落地速度分层——标准件密集行业（钢构/工装）最先受益
2. **"物理 AI"成为工业软件新叙事**：黄仁勋"Physical AI is the next frontier"与达索"Industry World Models"合流，CAD 公司正在变成"物理世界模型公司"——估值逻辑随之改变
3. **合规行业是黑盒路线的减速带**：适航/军工要求每一步可追溯，text-to-code 路线在这类行业有结构性优势，短期不会被动摇
4. **工程师角色重定义**："AI is just an engine. You are the driver."——工程师从操作者转为审批者/决策者，价值向产品架构与业务创新上移（与知识型工作 Agent 化的大趋势一致）

## 八、指南分析（怎么用这篇文章）

- 给管理层讲 AI+CAD 趋势：直接用第四节双路线对比表+水塔钢架 5 分钟案例，最省沟通成本
- 立项 AI 结构设计工具：第五节"重点行动"三条即工作分解——验收物模板/审计链/知识库闭环
- 跟踪达索动态：Functional Deliveries 节奏下，盯 SOLIDWORKS 官方 AI 页 + 3DEXPERIENCE World keynote 即可，无需追每次 SP

## 九、拓展应用推荐

- 本笔记与 [[2026-04-22-catia-automation]]、[[2026-04-22-CATIA-接入-AI-大模型原理]] 构成 CATIA×AI 三部曲（工具底座→接入原理→厂商战略）
- [[2026-05-05-Zero-to-CAD-Agent闭环合成百万级可执行CAD程序]] 是 PTC 路线的学术镜像，可与本文第四节对照
- [[2026-04-27-垂域LLM指导航空结构设计]] + [[2026-04-27-AI赋能结构设计研究现状与课题申报]]：把本文趋势判断引入课题申报的"国内外现状"章节

→ 相关：[ROSClaw Physical AI Harness](2026-09-21-ROSClaw-Physical-AI-Harness-MuJoCo物理实验室.md)（达索'工业世界模型'叙事在 Agent 基础设施层的工程实现）

## 相关笔记

- [CAD厂家AI平台化布局](./2026-08-13-CAD厂家AI平台化布局-达索西门子战略深度分析.md) — 达索AI战略前作，纵向对照
- [达索系统与西门子CAD-AI战略对比](./2026-08-13-达索系统与西门子CAD-AI战略对比.md) — 双巨头战略对比视角
- [ROSClaw Physical AI Harness](./2026-09-21-ROSClaw-Physical-AI-Harness-MuJoCo物理实验室.md) — 工业世界模型叙事的基础设施层实现
