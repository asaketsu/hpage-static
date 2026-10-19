# 全球 CAD 厂家 AI 布局现状与战略对比（海外权威信源更新版）

> 来源：达索/西门子官方新闻 + Enterprise Times + Digital Engineering 24/7 + WSJ + ARC Advisory + 官方 AI 功能清单
> 日期：2026-08-13（第二版，补充海外权威信源）
> 主题：达索/西门子/PTC/Autodesk 四大 CAD 巨头 AI 战略布局全景对比
> 评分：⭐⭐⭐⭐⭐ (5/5) — 基于 8 个英文权威信源的交叉验证分析

## 核心结论

**2026 年全球 CAD 厂家的 AI 竞赛已从"加 AI 功能"进入"重构商业模式"阶段。** 达索用"知识即货币（Knowledge as currency）"重新定义工业软件经济学；西门子用"物理感知生成式 AI（Physics-Aware Generative AI）"重新定义仿真。两家公司不约而同地推出了**工业级 Agentic AI 编排平台**——西门子的 Intelligence Center X 和达索的 Virtual Companions 本质上都是"工业版 AI Agent 平台"。

## 一、达索系统 — 知识平台化路线

### 1.1 战略愿景：Industry World Model

> CEO Pascal Daloz（3DEXPERIENCE World 2026, Houston, 2026-02-04）：
> *"In the last century, industry was about producing objects. Now, industry produces knowledge and know-how that generates those objects."*

> *"The real world doesn't consist of text and images. It consists of physics, materials, energy and constraints. In the digital world, many things look great, but in the physical world, they have to work."*

达索不建通用 LLM，而是建 **Industry World Model** — AI 理解物理世界的运作方式。

### 1.2 三款 Virtual Companions

| 伴侣 | 命名来源 | 角色 | 状态 |
|------|----------|------|------|
| **AURA** | AI 自选 = "Assisting You to Realise your Ambitions" | 战略顾问：连接组织内外知识、商业决策 | ✅ R2025x FD03 已上线 |
| **LEO** | Leonardo da Vinci（工程师/发明家） | 机械工程师：可制造性验证、装配生成、系统完整性 | R2026x FD02-FD03（2026 夏） |
| **MARIE** | Marie Curie（科学家） | 科学家：物理学/材料科学研究、分子建模 | R2026x FD02-FD03（2026 夏） |

### 1.3 LEO 官方 AI 功能全量清单（来自 3ds.com 官方）

这是达索官网公开的 **LEO 在 CATIA 中的完整 AI 功能矩阵**，按版本排列：

| 功能域 | 具体能力 | 首次可用 |
|--------|----------|---------|
| **3D Navigation** | 视口控制（pan/zoom/reframe/树展开隐藏） | R2026x FD02 |
| **Design Insight** | 规范树导航、装配结构检查、零件特征检查 | R2026x FD02 |
| **Parametric Design** | 参数/关系/草图/线框/实体创建修改 | R2026x FD02 |
| **Product Structure** | 产品结构管理 | R2026x FD02 |
| **Material Assignment** | 材料属性分配 | R2026x FD02 |
| **Product Structure Generation** | 装配产品层级结构生成 | R2026x FD02 |
| **Design Review** | 设计评估、模型摘要、3D 区域标记、截图分享 | R2026x FD03 |
| **Assembly Design** | 多零件装配管理 | R2026x FD03 |
| **Part Generation** | 从边界表示（BREP）自动生成特征规范 | R2026x FD03 |
| **Mechanical Interfaces Prediction** | 预测零件间机械接口 | R2026x FD03 |
| **Assembly Generation** | 复杂装配任务自动化 | R2026x FD03 |
| **Drafting** | 自动生成工程图 | R2026x FD03 |
| **Functional Tolerances** | 生成功能公差 | R2026x FD03 |
| **Template Instantiation** | 知识模板自动实例化 | R2026x FD03 |
| **(Re)generate model from documents** | 从文档/图片理解并生成模型 | R2026x FD03 |
| **System model quality analysis** | SysML 模型质量分析 | R2026x FD03 |
| **System Model insight** | 自然语言揭示 SysML 模型 | R2026x FD03 |
| **Generate Systems Requirement** | 系统需求定义 | R2026x FD03 |
| **Generate Systems Structure** | 系统结构生成（加速 Global Illumination 渲染） | R2026x FD03 |
| **Generate Systems Behavior** | 系统行为（活动图/状态机） | R2026x FD03 |
| **Generate Diagrams** | SysML V1 图表生成 | R2026x FD03 |

**LEO 在 DELMIA（制造）中**：

| 功能域 | 具体能力 | 首次可用 |
|--------|----------|---------|
| **Manufacturing Operations** | 实时生产洞察 + 基于知识的决策指导 | R2026x FD03 |
| **NC Machine Programming** | 自动分类零件几何→模板→刀路→工序排序 | R2026x FD03 |
| **Process Engineering** | 制造工程师辅助决策 | R2026x FD02 |

### 1.4 SOLIDWORKS 2026 生成式 AI

| 功能 | 说明 | 版本 |
|------|------|------|
| **Generative Self-Healing** | AI 检测/解释建模错误（草图/零件/装配/工程图）→ 根因分析 + 修复 | R2026x FD01 |
| **Generative Assembly Design** | 自然语言→装配层级→零件→SOLIDWORKS 文件 | R2026x FD01 |
| **Generative Drawings** | 标准 2D 制造图（视图/剖切/尺寸/BOM） | R2026x FD02 |
| **Generative Part Design** | STEP/IGES→参数化 3D 模型（恢复特征历史和设计意图） | R2026x FD02 |
| **Generative Design Analytics** | 模型 + PLM 数据洞察（版本/成熟度/所有权/引用） | R2026x FD02 |
| **Generative Model Health** | 装配性能瓶颈识别 + 简化建议 | R2026x FD02 |
| **Generative Impact Analysis** | 设计变更影响评估（下游使用/高风险条件） | R2026x FD02 |

### 1.5 NVIDIA 深度合作

> Jensen Huang（NVIDIA CEO, 3DEXPERIENCE World 2026）：
> *"This is the biggest partnership our two companies have ever had."*

| 维度 | 详情 |
|------|------|
| **整合技术** | CUDA-X + RTX + AI + Omniverse 深度集成到 3DEXPERIENCE |
| **仿真加速** | **100-1000 倍** |
| **Jensen Huang 原话** | "What used to be pre-rendered or offline simulations becomes the virtual twin vision we always envisioned. Everything now happens in real-time." |
| **反向合作** | NVIDIA 使用达索 MBSE 软件设计自己的 AI 工厂 |

### 1.6 IP Lifecycle Management（IPLM）— 全新概念

> Morgan Zimmerman（3DEXPERIENCE CEO）：
> *"In the AI era, the biggest problem isn't so much the algorithms, because they're reasonably available. The data is what matters."*

**核心洞察**：传统 PLM 管理产品数据生命周期，但 AI 时代需要 **IP Lifecycle Management** — 管理知识/数据的"可学习"权限。

**案例（Valeo）**：Valeo 向大众/宝马/雷诺共享车灯设计——以前客户只能安装使用。现在 AI 让客户能从所有共享数据中学习如何自己造车灯。**这是全新的风险维度。**

达索 3DEXPERIENCE 平台实现细粒度 IP 追踪：组织可指定每个数据集是否允许用于机器学习。

### 1.7 新商业模式：从 License 到"智能密度"

> Pascal Daloz: *"Virtual companions aren't real users. Do we keep counting users, or must we measure something else?"*

| 维度 | 过去（40 年） | 未来 |
|------|-------------|------|
| **计费单位** | 按用户数卖 License | 按"Know-how 单元"和"工作量单元"计费 |
| **Companion 角色** | — | Leo 可部署为机械工程师/化学家/制造专家，各持认证知识 |
| **可用时间** | 人类工程师 40 小时/周 | AI Companion **168 小时/周（24×7）** |
| **行业定制** | — | 同一 Companion 在汽车 vs 航空有不同 Know-how |
| **基础设施** | 客户本地 | 达索 AI Factory（自有 SaaS 基础设施） |

> Zimmerman: *"No customer can afford the GPU power needed for AI on their own infrastructure."* — GPU 单卡 £200,000，18-24 个月即过时。

### 1.8 ArisGlobal 18 亿美元收购 — 跨界生命科学

| 维度 | 详情 |
|------|------|
| **金额** | $1.8B 现金 + $200M AI 收入里程碑 = 总计 ~$2B |
| **时间** | 2026-07-23 签署协议，H2 2026 交割 |
| **标的** | ArisGlobal — AI-native 生命科学合规平台 |
| **核心 AI** | NavaX — 生成式 AI，年处理 1200 万+患者安全报告 |
| **客户** | 200+ 家，含全球前 50 大药企的一半 |
| **合规市场** | 2030 年达 $75 亿，双位数增长 |

**战略意图**：分子→患者→真实世界结果的统一 AI 平台。虚拟孪生 + 临床/上市后数据 = 药物研发的闭环 AI 学习。

## 二、西门子 — 物理感知生成式 AI 路线

### 2.1 战略愿景

> Sam Mahalingam（Simulation/HPC/AI EVP, Siemens）：
> *"Engineering simulation isn't limited by physics - it's limited by how quickly we can explore possibilities. Our strategy is to help customers learn from past work, accelerate exploration, and use AI as a prescriptive engine for innovation. We're not replacing deterministic truth - we're making it scalable and immediate."*

### 2.2 Altair $100 亿收购 — 仿真全栈整合

| 维度 | 详情 |
|------|------|
| **金额** | **$100 亿**（2025-03 宣布） |
| **Altair 核心能力** | 结构仿真 + 生成式设计 + 制造建模 + 电磁分析 + HPC + 数据科学 + ML |
| **整合范围** | Simcenter + HyperMesh + Inspire + OptiStruct + HPCWorks → 统一 Simcenter 产品组合 |
| **整合状态** | 2026-07-28 首次以统一 Simcenter 产品组合发布 |

### 2.3 Simcenter PhysicsAI Generate — 核心技术

**底层技术：几何深度学习（Geometric Deep Learning）+ 扩散模型（Diffusion-based Generative AI）**

| 维度 | 详情 |
|------|------|
| **训练方式** | 在历史仿真数据上训练 AI 代理模型 |
| **推理速度** | 比传统求解器快 **1000 倍** |
| **核心创新** | **PhysicsAI Generate** — 从性能需求直接生成物理一致的 3D 设计概念 |
| **技术路线** | 扩散模型（Diffusion-based）训练历史设计→学习几何/参数/KPI 之间的深层关联 |
| **关键区别** | 传统生成式工具是后处理加物理约束；PhysicsAI Generate **从设计之初即物理一致** |

### 2.4 Simcenter PhysicsAI 2026.1 关键更新（2026-07-29）

| 能力 | 详情 |
|------|------|
| **Generate** | 从性能/尺寸需求秒级生成 3D 设计概念（扩散模型驱动） |
| **Spatial Conditioning** | 用点云定义空间约束（安装点/载荷区/夹具位置）→ 生成的模型有真实空间感知 |
| **训练加速** | **5× faster training, 50% reduced peak memory**（峰值从 175 GiB 降到 75 GiB） |
| **Multi-GPU** | Simcenter STAR-CCM+ 支持 Multi-GPU 训练，10×+ 速度提升 |
| **SPH 粒子支持** | 光滑粒子流体动力学（鸟撞/冲击/流固耦合）AI 预测 |
| **Eigen 频率预测** | 自动提取固有频率 + 模态形状关联（NVH 工作流） |
| **应力/应变热点** | 直接在元素上预测，绕过插值→更清晰的热点图 |
| **Inspire 制造集成** | 铸造/注塑/冲压/挤出工艺仿真与 AI 预测无缝衔接 |
| **HyperMesh 集成** | 数据训练更高效，结果可信度更高 |

### 2.5 Simcenter Simsolid + Designcenter — 无网格仿真

| 维度 | 详情 |
|------|------|
| **能力** | 直接在 CAD 几何上运行结构仿真，**无需创建网格** |
| **效果** | 分析时间从数小时→**数分钟** |
| **工作流** | Designcenter 几何→Simsolid→加载/约束→仿真→评估 |

### 2.6 Intelligence Center X — 工业 AI 编排平台

> 关键发现：西门子推出了 **Intelligence Center X** — 全新的工业 AI 编排软件。

Simcenter PhysicsAI 的数据和模型可被 Intelligence Center X 调用。这是一个**工业级 Agentic AI 编排平台**，标志着西门子从"工具提供者"向"AI 工作流编排者"转型。

### 2.7 2026 路线图（Jean-Claude Ercolanelli, Senior VP）

> 来源：Digital Engineering 24/7 专访

| 优先级 | 方向 |
|--------|------|
| **1** | 更深的 AI 集成（AI-driven physics 即将出现在 Simcenter） |
| **2** | 统一仿真体验（Siemens + Altair 组合产品线统一工作流） |
| **3** | **单一许可证**：仿真 Token 模式（跨全组合工具灵活使用） |
| **4** | 技术协调：短期/中期/长期对齐解决方案、工作流和数据模型 |
| **5** | 强化数字主线：概念→设计→仿真→验证→运营 |

### 2.8 Agentic AI 扩展

Digital Engineering 报道的西门子最新动态：

| 产品/动作 | 说明 |
|-----------|------|
| **Industrial-Scale Agentic AI Orchestration Platform** | 全新工业级 AI Agent 编排平台 |
| **Self-Verifying Agentic AI**（NVIDIA DAC 2026） | 半导体/PCB 设计的自验证 AI Agent 工作流 |
| **Virtual Assistants** | 设计/仿真中的 AI 助手（引导设置、建议网格策略、推荐设计变更） |

## 三、PTC — 云原生 AI 实验路线

| 维度 | 详情 |
|------|------|
| **平台** | Onshape 云原生 CAD + PDM |
| **AI 计划** | **Onshape Labs**（2026-07-14 发布）— 早期体验计划 |
| **AI 后端** | Amazon Bedrock（AWS AI 服务） |
| **理念** | 每 3 周一个版本迭代 vs 达索年度大版本 |
| **首批功能** | AI Quick Render + NVIDIA Omniverse Publisher |
| **Creo GTO/GDX** | 本地拓扑优化 + 云端生成式设计 |

## 四、Autodesk — AEC + 制造业双轨 AI

| 平台 | AI 能力 |
|------|---------|
| **Fusion 360** | 生成式设计、AI 参数优化 |
| **Forma**（AEC） | AI 建筑布局生成、日照/风环境分析 |
| **Maya/3ds Max** | AI 辅助动画、材质生成 |

## 五、四大厂家终极对比矩阵

### AI 战略路线对比

| 维度 | 达索 | 西门子 | PTC | Autodesk |
|------|------|--------|-----|----------|
| **底层理念** | Industry World Model | Physics-Aware AI | 数据驱动快速迭代 | AEC+MFG 双轨 |
| **核心技术** | LEO/AURA/MARIE Companions | PhysicsAI Generate（扩散模型） | Onshape Labs AI | Forma/Fusion AI |
| **Agentic AI 平台** | Virtual Companions = AI Agent | **Intelligence Center X** | — | — |
| **收购策略** | 跨界（ArisGlobal $2B） | 同业整合（Altair $10B） | 无重大收购 | — |
| **云锁定** | 必须 3DEXPERIENCE | NX/Simcenter 本地+云 | 仅 Onshape | Fusion/Forma 云 |
| **NVIDIA 合作** | 深度（25 年→"biggest ever"） | 深度（DAC 2026 自验证 AI） | Omniverse Publisher | — |
| **计费模式** | Know-how 单元 + 工作量 | 仿真 Token | 订阅 | 订阅 |

### AI 功能深度对比

| 能力 | 达索 LEO | 西门子 PhysicsAI | PTC | Autodesk |
|------|----------|-----------------|-----|----------|
| **AI 导航/检查** | ✅ 3D Nav + Design Insight | ✅ HyperMesh AI | ⚠️ | — |
| **AI 参数化设计** | ✅ Parametric Design | — | ⚠️ | ⚠️ |
| **AI 生成几何** | ✅ Part/Assembly Gen | ✅ **扩散模型 Generate** | ⚠️ | ✅ Forma/Fusion |
| **AI 调用仿真** | ✅ LEO→SIMULIA | ✅ **1000x 加速** | ❌ | ⚠️ |
| **AI 闭环优化** | ✅ 设计→仿真→建议 | ✅ **核心优势** | ❌ | ⚠️ |
| **AI 生成工程图** | ✅ Drafting | — | ❌ | ⚠️ |
| **AI 公差生成** | ✅ Functional Tolerances | — | ❌ | — |
| **AI NC 编程** | ✅ DELMIA NC | — | ❌ | — |
| **AI 自修复** | ✅ Self-Healing (SW) | — | ❌ | — |
| **跨行业数据闭环** | ✅ **ArisGlobal 跨界** | ⚠️ Altair 数据 | ❌ | ⚠️ |

## 六、五大趋势判断

### 趋势 1：工业 Agentic AI 平台化

| 厂家 | Agentic AI 平台 |
|------|----------------|
| 达索 | Virtual Companions（LEO/AURA/MARIE）= 工业 AI Agent |
| 西门子 | Intelligence Center X + Industrial-Scale Agentic AI Orchestration |

**两家巨头不约而同推出"工业级 AI Agent 编排平台"**——这标志着工业软件从"工具集"向"Agent 平台"的范式跃迁。

### 趋势 2：仿真从"后验证"变成"前生成"

| 达索 | 西门子 |
|------|--------|
| LEO→SIMULIA 闭环 | PhysicsAI Generate（扩散模型） |
| 从文档/图片生成模型 | 从性能需求秒级生成物理一致设计 |

**设计师构思阶段就能得到 AI 性能预测和候选方案。**

### 趋势 3：云平台锁定 + 新计费模式

> 达索: "No customer can afford the GPU power needed for AI on their own infrastructure."
> 西门子: 单一仿真 Token 许可证模式

| 模式 | 达索 | 西门子 |
|------|------|--------|
| **新计费** | Know-how 单元 + 工作量 | 仿真 Token |
| **核心逻辑** | Companion 24×7 工作 = 4.2 倍人类工程师 | 跨全组合灵活使用 |

### 趋势 4：IP 治理成为关键能力

> 达索 Morgan Zimmerman: "In the AI era, the biggest problem isn't so much the algorithms. The data is what matters."

达索首创 **IP Lifecycle Management（IPLM）** 概念——从"能读什么数据"变成"能从什么数据学习"。这是 AI 时代的全新风险维度。

### 趋势 5：NVIDIA 成为所有工业 AI 的基础设施

| 厂家 | NVIDIA 合作深度 |
|------|----------------|
| 达索 | CUDA-X/RTX/AI/Omniverse 深度集成 → 100-1000x 仿真加速；NVIDIA 反向使用达索 MBSE 设计 AI 工厂 |
| 西门子 | NVIDIA DAC 2026 推出自验证 Agentic AI 工作流（半导体/PCB） |
| PTC | Omniverse Publisher 集成 |

## 七、关键洞察：达索/西门子与 Hermes Agent 的范式平行

| 达索 LEO | 西门子 PhysicsAI/ICX | Hermes Agent |
|----------|---------------------|-------------|
| Virtual Companion | Agentic AI Orchestration | 四猫团队 |
| Competency（知识封装） | PhysicsAI 代理模型 | Skill（技能模块） |
| Industry World Model | 几何深度学习 | L1/L2/L3 三级记忆 |
| 可被 AI 调用的服务 | Intelligence Center X 编排 | skill_view + delegate_task |
| IP Lifecycle Management | — | 记忆权限管理 |
| 3DEXPERIENCE 云平台 | Xcelerator 平台 | 飞书/微信多平台 |
| Know-how 计费单元 | 仿真 Token | — |

**核心发现：工业软件巨头（达索/西门子）正在做的事，本质上是"把工业软件 Agent 化"——这与 Hermes 把日常任务 Agent 化是完全相同的范式。** 达索的 LEO Competency = Hermes 的 Skill；西门子的 Intelligence Center X = Hermes 的 delegate_task 编排层。2026 年，工业软件和 AI Agent 框架殊途同归。

## 八、数据来源清单

| # | 来源 | 类型 | URL |
|---|------|------|-----|
| 1 | Enterprise Times: Dassault Virtual Companions | 深度报道 | enterprisetimes.co.uk/2026/02/04/... |
| 2 | 3ds.com AI Intended Purpose | **官方功能清单** | 3ds.com/trust-center/trusted-ai/ai-intended-purpose |
| 3 | Siemens News: Simcenter Summer 2026 | **官方新闻稿** | news.siemens.com/en-us/siemens-simcenter-summer-2026 |
| 4 | Siemens Blog: PhysicsAI 2026.1 | **官方技术博客** | blogs.sw.siemens.com/simcenter/whats-new-in-simcenter-physicsai-2026-1 |
| 5 | Digital Engineering 24/7: Siemens+Altair Q&A | VP 专访 | digitalengineering247.com/article/siemens-altair-... |
| 6 | GlobeNewsWire: ArisGlobal 收购 | 官方新闻稿 | globenewswire.com/.../dassault...arisglobal... |
| 7 | ARC Advisory: ArisGlobal 分析 | 行业分析 | arcweb.com/blog/dassault-systemes-acquire-arisglobal... |
| 8 | WSJ: ArisGlobal $2B | 金融报道 | wsj.com/health/dassault-systemes-to-buy-arisglobal... |

## 关联

- → 相关：2026-08-13-CAD厂家AI平台化布局-达索西门子战略深度分析.md（第一版，中文信源）
- → 相关：2026-08-12-全球十大CAD几何建模内核-NX-CATIA-SolidWorks.md
- → 相关：2026-06-18-PTC-Cloude-Onshape-AI-生成工程级CAD模型深度解析.md
- → 相关：2026-06-26-西门子CEO物理AI工业AI革命-VivaTech2026.md
- → 相关：text-to-cad-自然语言驱动参数化CAD深度分析.md
- → 项目：~/uclaw/project/catia-caa/
