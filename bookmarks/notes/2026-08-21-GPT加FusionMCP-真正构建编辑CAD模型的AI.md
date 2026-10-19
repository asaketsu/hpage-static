# GPT + Autodesk Fusion MCP：能真正构建和编辑 CAD 模型的 AI

> **来源**：X/Twitter @irinatoxi 长推（完整技术评述，56.1K views）
> **原文链接**：https://x.com/irinatoxi/status/2089997971089703423
> **发布时间**：2026-08-19 16:48
> **记录日期**：2026-08-21

**标签**：#MCP #Fusion #CAD #ComputerUse #CADAgent #Codex #设计自动化 #参数化建模

---

## 一、内容详细整理

### 1.1 核心区分：不是又一个 text-to-3D 生成器

**开篇立论**：多数 AI 生成的 3D demo，一问"最终图像背后实际存在什么"就不那么令人印象深刻了——机械零件在渲染里可以完全可信，但**没有可用尺寸、没有可编辑草图、没有设计历史、特征之间没有关系**。"It looks engineered, but there is often very little engineering behind it."（看起来像工程设计，背后往往几乎没有工程。）

**GPT + Fusion MCP 的本质差异**：不是生成"长得像 CAD 模型的东西"，而是**与真实的 Fusion 会话交互**——使用 Fusion MCP 暴露的工具、执行操作、检查设计信息、运行脚本、修改几何，并且在第一版创建后**继续在同一模型上工作**。

**角色转变**：通过 Codex 这类 agentic 环境连接 Fusion MCP，GPT 不再"坐在软件外面解释该按哪些按钮"——**直接参与 CAD 工作流**。

> "The problem is that you are still doing everything."（普通 chatbot 给你教程，但活还是你干。）

### 1.2 为什么 GPT 在 Fusion 内部有意义

**CAD 是 AI 的困难环境**：几乎每个操作都依赖之前的决策——改一个尺寸→草图变→草图控制拉伸→影响孔→影响阵列→改变时间线更下游的组件。

**有用的 CAD agent 需要的能力**（超出"写一个聪明脚本"）：

- 追踪现有设计状态
- 理解哪个部分应该变
- **保全所有不应动的部分**
- 操作失败时正确反应
- **从当前状态继续**而非反复从头开始

**反馈环（feedback loop）**：GPT 请求操作→看 Fusion 是否接受→检查返回信息→调整方法→继续。

> "A model that only writes instructions has to assume they worked. A model connected to the actual software can at least find out when they did not."（只写指令的模型只能假设指令生效了；连接真实软件的模型至少能发现指令没生效。）

### 1.3 实际工作流示例

**迭代场景（电子项目外壳）**：矩形壳体 2.5mm 壁厚、圆角、四个内部安装柱、通风孔、USB-C 开口、可拆顶盖——GPT 创建基础体→建壁厚→生成安装特征→切开口→产出可编辑初版。然后："USB-C 开口太低、安装柱太近、通风孔近边缘去料太多、盖子还差 1mm 间隙"——**每个观察在传统流程里都是一次穿越 Fusion 界面的小旅行**（开草图→找尺寸→改值→完成草图→检查下游特征→发现别的动了→再修）。MCP 连接后这些修改表达为指令即可：上移 USB-C 开口 4mm、加宽安装柱但保持中心位置、矩形通风孔换圆孔阵列、加宽壳体但不动特定安装特征。

**结构化保持是难点**：模型必须处理结构化设计并**保持部件间关系**——这比从 prompt 生成一个漂亮 3D 物体难得多。

### 1.4 安装配置（小到惊人的 setup）

Fusion 运行时本地暴露 MCP server，兼容的 MCP client 连接该端点、发现可用工具、与活动 Fusion 会话交互。Codex 支持 MCP 连接（含 Streamable HTTP），Fusion 配置为 agent 的外部工具源：

```toml
[mcp_servers.fusion]
url = "http://127.0.0.1:27182/mcp"
```

（实际地址端口取决于 Fusion 配置。）

**去机械化的价值**：你仍需知道要什么，但**不再需要手动执行每个微小操作**——只因为 CAD 软件传统上通过菜单、对话框和鼠标点击通信。

### 1.5 Python 让工作流更灵活

Fusion 有成熟的脚本与 API 系统——当任务**用程序描述比逐个建模命令更容易**时给 GPT 另一条操作路径：

- **20 个同款安装板变体**（不同宽度/厚度/孔距）：手动做不难，只是重复到让下午变得漫长。GPT 生成参数化脚本→通过 Fusion 执行→检查结果→不对就改代码
- 适用任务：重复组件创建、批量参数修改、命名、导出、测量收集、项目清理——"不需要多 impressive 的推理，但手动跨大设计执行时消耗真实时间"
- **实践优势**：代码跑在真实项目上而非孤立聊天窗——脚本失败时，失败成为下一次迭代的一部分，"GPT 可以从错误或结果模型继续，而不是自信地递给你一段孤立看正确的代码"

### 1.6 从零开始变得容易

空白 Fusion 文档是 CAD 工作流最无趣的阶段——在设计好到可评估之前，必须建草图、定尺寸、组织组件、建初始体、加孔和阵列、设参数……单独看都简单，合起来是**到达"能判断设计好坏"之前的巨量工作**。

- 描述基本需求让 GPT 建出足够结构——"**给你一些具体可批评的东西**"。比例可能不对、特征要挪、初版可能比预期丑，但**"不完美的可编辑模型仍比空白文档好得多"**
- **学习曲线的改变**：初学者不必先背完所有建模命令——从 AI 生成的起点开始，检查草图和特征、看模型怎么建的、逐渐接管手动控制。"学习曲线没有消失，只是不再是任何有趣事情发生前的入场费。"

### 1.7 处理设计信息而非只有几何

Fusion 项目包含远多于视口形状的内容：组件、草图、参数、尺寸、体、材料、属性、关系。通过 API 驱动的工作流，这些信息对 AI agent 有用——GPT 可检查结构化项目数据而非只看屏幕上的样子：

- 找未赋材料的组件
- 列出匹配条件的参数
- 检查装配层级
- 从多个体收集测量
- 跨组件组自动化导出

> "Some of the most practical applications will probably look incredibly boring in a demo."（最实用的应用在 demo 里可能无聊得难以置信——自动命名、检查几十个属性、收集尺寸、导出 20 个文件。但**这正是人们最想先自动化的工作**。）

### 1.8 它仍不知道设计是否好（边界诚实）

**访问专业 CAD 软件不会自动带来专业工程判断**：

- 满足 prompt 每个数字的支架仍可能** unnecessarily heavy**
- 包含所有要求开口的外壳仍可能**难装配**
- 看起来机械合理的组件可能因一个有经验设计师会立刻删掉的特征而**制造成本高昂**
- 模型不会自动知道哪些约束最重要——制造方法、材料选择、载荷、公差、装配顺序、成本、维护、可靠性**完全改变什么算好设计**

**人机分工**：设计师定方向（壁太薄/安装点位置差/零件太重/制造约束被忽略）→ GPT 执行修改和重复实现。

> "It does not need to become a better engineer than the engineer. It needs to become good enough at operating the software that the engineer spends less time operating it manually."（它不需要成为比工程师更好的工程师，只需要熟练到让工程师少手动操作软件。）

### 1.9 直接控制也让错误更快

**双刃剑**：允许快速做出有用修改的同一连接，也允许同样快速地做出错误修改。

- **模糊指令风险**："simplify the model"可以意味着去多余圆角/减组件数/清理草图/改制造特征/删看似冗余的几何——agent 可能选一个**完全合理但与你完全不同的解释**
- **时间线级联**：改一个参数影响多个下游依赖特征；清理脚本如果范围不清，改动可能远超预期

**无聊的预防措施仍然有用**：存版本、指令收窄、审查重要操作、大自动化改动后检查设计。

> "Giving an agent direct access to CAD is valuable precisely because it can change many things quickly, so giving it completely unrestricted freedom is probably not the clever part of the experiment."（给 agent CAD 直接访问的价值恰恰在于改得快，所以给它完全不受限的自由大概不是这个实验聪明的部分。）

### 1.10 真正的转变：想法与可编辑模型之间的距离

**不是**"一句话描述整个机械产品→收到可制造的成品设计"——严肃工程仍涉及材料/公差/载荷/制造方法/装配/成本/可靠性等无法只看几何判断的约束。

**改变的是**：这些决策开始之前所需的**重复工作量**。GPT 帮建初始几何、改参数、自动化重复特征、写测脚本、查项目信息、批量编辑、在同一可编辑 Fusion 项目里继续工作——**操作对象背后的结构而非产出最终图像**。

> "A render captures appearance, while a Fusion project contains sketches, dimensions, features, bodies, parameters, components, and relationships that can continue through an actual engineering workflow."

> "The useful question is not whether GPT can replace the engineer. It is how much of the tedious distance between having an idea and getting a usable CAD version of that idea can now be delegated to the model."（有用的问题不是 GPT 能否取代工程师，而是**从有想法到可用 CAD 版本之间的乏味距离，有多少现在可以委托给模型**。）

> "Unlike most AI 3D demos, there is still a real project left when the demo ends."（demo 结束时还留着一个真实项目——这是与多数 AI 3D demo 的区别。）

---

## 二、查询拓展

### 2.1 Autodesk Fusion MCP server 技术背景

Autodesk 2026 年在 Fusion 中内置了 MCP server（Add-In 形式），运行时在本地暴露工具端点。暴露能力覆盖：草图创建与编辑、特征操作（拉伸/旋转/倒角/阵列）、参数读写、组件与装配层级查询、材料赋值、测量、导出（STEP/STL/F3D 等）、**执行 Fusion Python API 脚本**。端口默认 27182（本文配置所示）。这是**商业 CAD 三巨头中第一家官方内置 MCP**——对比 Siemens NX/OpenAPI 走 FOXGLOVE 类中间件、PTC Creo 依赖自研 Toolkit，Fusion 抢占了 MCP 原生的先发位置。

### 2.2 Codex 作为 MCP 客户端

Codex（OpenAI 的 agentic CLI）原生支持 MCP（TOML 配置 `[mcp_servers.*]`，含 Streamable HTTP 与 stdio 两种传输）。文中选择 Codex 而非 ChatGPT 的原因：**agentic loop 需要多轮工具调用+结果消化+调整再试**——普通聊天界面每轮都要人肉粘贴，Codex 能把 MCP 响应作为持续任务的一部分。这与 Hermes 的 native-mcp（config.yaml 配置 server，自动工具发现）完全同构——**本机 Hermes 也可以同样接 Fusion MCP**。

### 2.3 "设计历史感知"是 CAD agent 区别于生成器的分水岭

Fusion 是**参数化+历史基于特征**（timeline-based）的 CAD——每个特征依赖前序特征。这意味着 CAD agent 的核心难点不是生成几何，而是**在依赖图上做外科手术式修改**（改 A 不伤 B）。这正是原文 1.2 节强调的能力清单（追踪状态/理解变化/保全不变/错误恢复/继续当前状态）。谱系对比：text-to-3D（无历史）→ 脚本 API（有 API 但无 agent 判断）→ **MCP agent（API+agent 反馈环+历史感知）**。第三档才可能"改一处而不重建整个东西"。

### 2.4 与七部曲⑦认知设计系统（ADS）的对照

本推文的 GPT+Fusion 与昨日笔记⑦的 ADS 认知设计系统构成**CAD AI 的两极**：

| 维度 | GPT+Fusion MCP（本篇） | ADS 认知设计（⑦） |
|------|----------------------|------------------|
| 路线 | 通用 LLM + 商用 CAD 直连 | 专用确定性 AI 闭环平台 |
| 优化引擎 | GPT 即兴+用户指令驱动 | 确定性核心+KPI 评分闭环 |
| 认证性 | 可编辑项目（人审） | 完整数据链（可认证） |
| 效率承诺 | "缩短想法→可编辑模型的距离" | 天线支架 100h→1h+45% 减重 |
| 成熟度 | 工作流增强（辅助） | 工业部署（泰雷兹/赛峰） |

**互补判断**：GPT+Fusion 是"**操作层自动化**"（会用软件），ADS 是"**决策层自动化**"（知道该设计成什么样）。未来融合点：ADS 式确定性闭环的"AI 层建议"由通用 LLM 担任，"确定性核心"由 Fusion MCP 操作执行——**MCP 正在把这两极接通**。

### 2.5 CAD agent 的学术前沿呼应

CVPR/SIGGRAPH 2025-2026 的 CAD 生成研究（CADTalk、Text2CAD、SkexGen 等）走的是"从文本/草图生成 B-rep/草图序列"的**生成式路线**——产物恰好是原文批评的"没有设计历史的几何"。工业路线（MCP 直连）绕开了生成难题：**不生成模型，操作现成软件**——用参数化 CAD 的原生历史结构规避了生成式 CAD 的结构保真难题。这是一个"生成 vs 操作"的路线分叉：学术圈赌生成，工业界赌操作。

---

## 三、归纳总结

### 3.1 一句话结论

> **Fusion 内置 MCP server 让 GPT（经 Codex）从"坐在软件外面讲教程"变成"坐在软件里面干活"——操作真实参数化设计（草图/特征/时间线/参数），带失败反馈环，迭代已有模型而非每次重新生成；它不带来工程判断，但把"想法→可编辑 CAD 模型"的乏味距离显著缩短——demo 结束时还留着一个真实项目。**

### 3.2 本篇在近日笔记连续体中的位置

```
08-21 笔记①：Fuzz Testing（agent 科研反馈环）      —— 反馈架构
08-21 笔记②：Harness 四组件（Pi/Earendil）          —— 运行环境
08-21 笔记③：OpenBot + AG-UI（CopilotKit）          —— 交互协议（MCP/A2A/AG-UI 三栈）
08-21 笔记④：GPT + Fusion MCP（本篇）               —— MCP 落到垂直工具（CAD）
```

笔记③给出三协议地图（MCP=手），本篇是 **"MCP 之手"握住垂直专业软件的第一个高完整度样本**：通用 agent + 垂直工具的 MCP 化 = 垂直领域 agent 化的最短路径——不需要训练领域模型，只需要领域软件开口说话。

### 3.3 核心机制速查

| 机制 | 内容 | 意义 |
|------|------|------|
| 本地 MCP server | Fusion 运行时暴露 `127.0.0.1:27182/mcp` | 商用 CAD 首家官方 MCP 内置 |
| 反馈环 | 请求操作→看接受与否→检查返回→调整→继续 | 与"只写指令"的本质区别 |
| 双路径操作 | Fusion 工具调用 + Python API 脚本 | 重复任务走脚本，单点修改走工具 |
| 历史感知 | 时间线依赖图上的外科修改 | 改 A 不伤 B 是 CAD agent 分水岭 |
| 数据面操作 | 查参数/材料/装配层级/批量导出 | "无聊但最想被自动化"的任务 |
| 人的方向权 | 设计师判好坏，GPT 执行 | 工程判断不外包 |

### 3.4 三条最诚实的边界声明（原文的价值所在）

1. **"It does not know whether the design is good"**——满足所有尺寸的支架仍可能过重/难造/贵；约束重要性不会自动知晓
2. **"Direct control also makes mistakes faster"**——模糊指令的多解性+时间线级联=快速出错与快速改进同源
3. **"不是一句话到成品"**——改变的是决策前重复工作量，不是工程判断本身

---

## 四、趋势判断

### 4.1 专业软件 MCP 化将在 12-24 个月内席卷 CAx 全家桶

Fusion 内置 MCP 的示范效应：CAD/CAE/CAM/PLM 工具的 MCP 化是**垂直领域 agent 化的基础设施**。判断：Siemens NX、SolidWorks、CATIA 会跟进（或被第三方 Add-In 强行 MCP 化）；接下来是 ANSYS/Abaqus（CAE）——届时七部曲⑥的"高保真机理模型+PINN/FNO 双引擎"可以通过 MCP 被 agent 直接调度，**"可微分力学求解器"的入口之争从 API 层上移到 MCP 层**。

### 4.2 "操作现成软件"路线正在击败"生成式复刻"路线

学术圈的 text-to-3D/CAD 生成研究产出"无历史几何"，工业界 MCP 直连路线直接复用数十年积累的参数化内核。判断：**垂直工具的 agent 化主流路线将是 MCP 操作而非端到端生成**——生成式路线的价值收窄到"从零冷启动"场景（原文 1.6 节恰是 MCP 路线也能覆盖的场景）。这与 LLM 领域"tool use 战胜 world model 内化"的走势同构。

### 4.3 CAD 工程师角色将复现"意图定义者+流程编排者"转型

与⑦认知设计系统的判断合流：GPT+Fusion 让"建草图/改参数/批量导出"这类操作劳动贬值，工程师价值向**方向判断（什么算好设计）与指令精度（收窄歧义）**集中。原文的"无聊预防措施"（存版本/窄指令/审查操作）就是 AI 时代的 CAD 工程纪律——**未来 CAD 培训会加入"如何给 agent 下建模指令"课程**。

### 4.4 反馈环+结构化数据操作是 agent 落地垂直领域的通用最小组合

本篇样本提炼的通用模式：**本地 MCP 端点 + 失败反馈环 + 结构化项目数据读写 + 人的方向权**——这四件套可平移到任何垂直专业软件（EDA/CFD/金融终端/MES）。判断：这是 2026-2027 "vertical agent" 创业的公式化模板，Fusion 只是第一个被完整记录的案例。

---

## 五、关联分析

### 5.1 与近日笔记的关联

- [08-21 OpenBot/AG-UI](2026-08-21-OpenBot开源GrokBot与AGUI协议-三协议生态位.md)：三协议栈中 MCP=手——本篇是"手握住 Fusion"的完整案例；OpenBot 的"工具调用过网关+allowlist+记录"对本篇的"直接控制让错误更快"是现成的治理答案
- [08-21 Harness 四组件](2026-08-21-什么是AgentHarness-从攀岩安全带到四组件解剖.md)：GPT+Fusion 是 harness 生态的垂直实例——Codex(harness) 的 agentic loop 消化 MCP 工具响应；"harness 管运行、MCP 管手"在本篇具象化
- [08-21 Fuzz Testing](2026-08-21-科研目标不是赢-AgenticAutoResearch即模糊测试.md)：本篇反馈环（请求→看接受→检查→调整）与 fuzz loop（bet→settle→doors）同构——**操作型 agent 的可靠性来自反馈环，与科研 agent 相同**

### 5.2 与飞机结构七部曲的关联

- [⑦认知设计系统](2026-08-20-认知设计系统-确定性AI重构航空结构件设计流程.md)：见 2.4 对照表——两极互补，MCP 是接通点；ADS 的"AI 层建议→确定性核心执行"未来可由"LLM 经 MCP 操作 Fusion/NX"实现执行层
- [六部曲⑥机理深化版](2026-08-20-结构数字-数字孪生驱动验证预测与智能决策研究报告-机理深化版.md)：⑥的"高保真机理模型（XFEM/CZM）与 PINN/FNO 双引擎互馈"若经 MCP 化，agent 可直接调度仿真迭代——**数字孪生的"实时互馈"获得 agent 入口**
- `struct-gen`/`struct-gen-agent` 项目：本篇是 struct-gen"从需求到 CATIA 模型全自动编排"的**执行层技术底座**——CATIA CAA 若 MCP 化，struct-gen 的工具调用层即插即用

### 5.3 与 Hermes 的关联（可操作性最强）

- **本机可复刻**：Hermes 的 native-mcp 支持 Streamable HTTP server——装 Fusion 的机器上加 `[mcp_servers.fusion] url=...` 即可让 Hermes 直接操作 CAD（与 Codex 同构能力）
- 本篇的"20 个变体参数化脚本"模式与 quant 管线"318 日训练窗批量回测"同构——**参数化批量+失败反馈迭代**是通用工程模式
- "模糊指令多解性"教训直接映射 Hermes 技能设计：skill 的 trigger 越窄越安全（对照 OpenBot "keep instructions narrow"）

---

## 六、金句摘录

> "It looks engineered, but there is often very little engineering behind it."（看起来像工程设计，背后往往几乎没有工程。）

> "A model that only writes instructions has to assume they worked. A model connected to the actual software can at least find out when they did not."（只写指令的模型只能假设生效；连接真实软件的模型至少能发现没生效。）

> "An imperfect editable model is still a much better starting point than an empty document."（不完美的可编辑模型仍远胜空白文档。）

> "The learning curve does not disappear. It just stops being the entrance fee."（学习曲线没有消失，只是不再是入场费。）

> "It does not need to become a better engineer than the engineer."（它不需要成为比工程师更好的工程师。）

> "Giving an agent direct access to CAD is valuable precisely because it can change many things quickly, so giving it completely unrestricted freedom is probably not the clever part of the experiment."

> "There is still a real project left when the demo ends."（demo 结束时还留着一个真实项目。）

---

## 七、拓展应用推荐

- **struct-gen 接入 MCP 路线评估（P1）**：评估 CATIA CAA/secondary API 封装为 MCP server 的可行性——struct-gen-agent 的"需求→模型"编排若获得 MCP 执行层，可复刻 GPT+Fusion 模式；Fusion 可先作为原型验证工具链
- **垂直 agent 四件套模板沉淀（P1）**：把"本地 MCP 端点+失败反馈环+结构化数据读写+人的方向权"提炼为技能模板——下一个垂直工具（EDA/CAE）接入时直接套用
- **模糊指令防护写入技能（P2）**：CAD/自动化类技能加入"指令收窄"检查清单（禁用 simplify/clean up 类多解动词，要求明确目标特征与范围）——直接吸收本篇 1.9 教训
- **Fusion MCP + Hermes 实测（P2）**：有 Fusion 环境时实测 native-mcp 接入（TOML 等价 config.yaml 配置），验证"批量变体脚本+失败迭代"工作流在本机的可复刻性

---

## 八、指南分析

**垂直工具 agent 化的叙事工艺（本篇写作方法论）**：

1. **先破后立**：开篇先打死"text-to-3D demo"（没有尺寸/草图/历史/关系的渲染骗术）——用否定句式给新事物腾出意义空间
2. **教程 vs 参与的对比轴**："问题是你还在干所有活"——一句话把 chatbot 降格，把 MCP 连接升格
3. **具体到可复现**：TOML 配置两行给出（url+端口）——"setup 小到惊人"与"能力大"的反差是传播点
4. **无聊场景的诚实呈现**："最实用的应用在 demo 里无聊得难以置信"（命名/检查/导出）——反 demo 审美，反而建立可信度
5. **三段边界声明**：不知道设计好坏/错误也更快/不是一句话到成品——**先说不能做什么，用户才会相信你说的能做什么**
6. **金句收尾**："demo 结束时还留着真实项目"——把全文主题（操作结构而非产出图像）压缩成一个可转述的判据

**阅读指南**：全文 14.9K 十五分钟；1.2（CAD agent 能力清单）+1.8/1.9（两条边界）+1.10（总结）是核心；与⑦认知设计笔记对照读可见 CAD AI 两极。

---

## 九、行动启示（可学到的点）

- **可学到 1——操作而非生成**：垂直专业软件的 agent 化，最优路径是让 agent 操作现成软件（复用数十年参数化内核），而非端到端生成复刻——**开口说话比学会模仿便宜**
- **可学到 2——反馈环是可靠性的来源**："只写指令的模型只能假设生效"——任何自动化交付前必须有机会发现失败；无反馈环的代码交付=自信地递给你孤立看正确的代码
- **可学到 3——历史感知是在依赖图上做手术**：改 A 不伤 B 的能力（追踪状态/保全不变/从当前继续）是结构化工作 agent 的分水岭——比单次聪明输出难得多也重要得多
- **可学到 4——不完美可编辑胜过完美渲染**：给你具体可批评的东西（imperfect editable）比漂亮的一次性产出有价值——**初版的价值是引发修正，不是展示完成**
- **可学到 5——双路径（工具调用+脚本）按任务形态切换**：单点修改走工具调用，批量重复走参数化脚本——重复任务"不需要 impressive 推理"但吃真实时间，是最先该自动化的
- **可学到 6——工程判断不可外包，指令精度是新工程纪律**：人定方向（壁太薄/太重/难造），agent 执行；存版本/窄指令/审操作/后检查四件无聊预防措施是 agent 时代的必守纪律
- **可学到 7——数据面操作比几何面更先被自动化**：查参数/找缺材料组件/批量导出/命名——结构化数据读写是最 boring 也最刚需的自动化起点

---

## 十、出处

- **推文**：https://x.com/irinatoxi/status/2089997971089703423（Rina @irinatoxi，2026-08-19 16:48，56.1K views，5 回复/51 转发/83 赞）
- **技术对象**：Autodesk Fusion MCP server（本地 127.0.0.1:27182，Add-In 形态）+ OpenAI Codex（MCP 客户端，TOML 配置，Streamable HTTP）
- **抓取链路**：web_extract 432 → Playwright headless 渲染推文页全文（article.innerText 完整 14.9K，两次分页读完）
- **连续阅读**：本篇与 [OpenBot/AG-UI](2026-08-21-OpenBot开源GrokBot与AGUI协议-三协议生态位.md)（MCP=手的地图）、[认知设计系统⑦](2026-08-20-认知设计系统-确定性AI重构航空结构件设计流程.md)（CAD AI 决策极 vs 本篇操作极）构成三角，建议连读

## 相关笔记

- [认知设计系统⑦](2026-08-20-认知设计系统-确定性AI重构航空结构件设计流程.md) — CAD AI 决策极；本篇为操作极，连读构三角
- [MCP 工具注入攻击](explore/2026-08-21-网络安全-MCP-tool-description-inj.md) — MCP 安全攻击面；本笔记讨论 Fusion MCP server 暴露形态
- [OpenBot/AG-UI](2026-08-21-OpenBot开源GrokBot与AGUI协议-三协议生态位.md) — MCP 生态位搭档，连读
