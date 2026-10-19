# Claude 直连 Fusion/Blender：AI 正式"坐进"设计师的椅子

- 📅 2026-05-05
- ⭐⭐⭐⭐ 4/5 — MCP协议进入工业设计软件的标志性事件，技术架构分析到位，EchoCAD项目值得关注
- 🏷️ #MCP #Claude #Fusion360 #Blender #工业设计 #CAD #EchoCAD
- 📰 PLM之家（微信公众号）
- 🔗 https://mp.weixin.qq.com/s/DmotuFNseMbUMRzYxswWRQ

## 摘要

2026年4月28日，Anthropic联合Blender、Autodesk、Adobe等公司发布9个面向创意与工业软件的官方Claude MCP连接器。核心区别：Claude不是用text-to-3D"生成"模型，而是通过MCP协议"操作"专业软件本身——调用原生API一步步执行建模操作。文章详细拆解了技术架构（Blender Python插件+MCP Server TCP桥接）、实际案例（1235零件机械键盘爆炸图）、交互范式的三层颠覆，以及对Text-to-CAD初创公司的冲击。作者还透露了自研EchoCAD项目，已打通NX/Three.js/Catia/Solidworks。

## 核心内容

### 技术架构：MCP协议实现AI操控

- MCP（Model Context Protocol）开放标准协议是技术核心
- Blender方案：Python插件在Blender内开启TCP socket → MCP server通过socket翻译Claude指令为bpy API调用 → Blender执行并回传结果（含视口截图）
- 关键区别：不是text-to-3D生成网格塞进场景，而是调用软件原生建模工具（新建网格→细分修改器→调整材质节点→设置光照），每步可撤销、可被其他插件识别
- Fusion 360：同样的MCP路线，但强调"有边界的、被引导的访问权限"，执行锁定在Fusion的CAD内核里

### 实际案例：1235零件机械键盘

- Claude打开1235零件装配体 → 检查坐标系（Z-Up）→ 扫视图截图 → 诊断键位问题（键悬浮在外、轴体位置错误、键帽缺失）
- 用户要求爆炸图 → Claude自动规划底壳→背板→PCB→定位板→键帽轴体的装配顺序，按30mm间距拆开排列
- 展示能力：读懂复杂装配→识别问题→拆解步骤→在Fusion里执行

### 交互范式三层颠覆

1. 从"学习软件"到"描述需求"：学习成本从数月降到自然语言描述
2. 从"专家工具"到"可对话协作者"：软件从被动执行变成双向对话
3. 从"单一软件"到"跨平台工作流"：Claude桥接不同工具，翻译格式、保持资产同步

### 技术局限

- Claude在CAD里会操作但不会设计——不擅长公差设计、材料选择、结构强度、DFM
- 自然语言模糊性与CAD精确参数系统存在根本矛盾
- "做一个支架"时AI实际上在"瞎补设计参数"

### EchoCAD项目（作者自研）

- 已打通Three.js（可视化+绘制）、NX（工业建模）
- 核心不仅是生成CAD，还包括STP文件可视化/分析、文生图、图生3D、mesh建模+精确建模
- 统一架构设计，不同软件通过相同方式接入
- 结合SKILLS和知识库进行输入内容分析，调用相关技能进行设计

## 🔍 借鉴点

- MCP协议作为Agent操控专业软件的标准通道 → 我们的Hermes已有native-mcp skill，可以参考这种"Python插件+TCP桥接+MCP Server"的架构模式，未来接入各类专业工具
- EchoCAD的统一架构思路（不同软件通过统一接口接入） → 可借鉴到我们的能力域策略，用统一的Agent层对接不同工具
- "操作而非生成"的理念 → 比text-to-3D更实用，Agent应该操控已有工具而非重新造轮子

## 🔗 关联性

- 关联已有 skill：native-mcp — MCP协议是技术底层，这篇文章是MCP在工业设计领域的落地案例
- 关联已有笔记：[2026-05-05-Hermes-NotebookLM知识管理自动挡](2026-05-05-Hermes-NotebookLM知识管理自动挡.md) — 同属Agent作为"中间层"连接工具的趋势
- 关联竞品索引：MCP协议生态 — Anthropic推动MCP生态扩展到创意/工业软件领域
- 关联能力域策略：分层YAML选择器 → MCP连接器可作为能力域的具体实现方式

## 💡 启发

- MCP的真正价值不是让AI"生成"内容，而是让AI"操控"专业工具。这比生成式方案高一个维度——保留工具的全部能力和精度，只是改变了交互方式
- Text-to-CAD初创公司面临生存危机——当AI可以直接操作Fusion/Blender时，中间层的"AI生成CAD"就没有意义了。同样的逻辑可能蔓延到其他领域：AI生成代码→AI直接操作IDE，AI生成文案→AI直接操作发布工具
- "会操作但不会设计"是当前AI能力的精确描述。短期内AI是效率工具，不是创意替代。设计师的价值从"会用软件"转向"会做设计决策"

## 🔮 预判

- 短期：MCP连接器会快速扩展到更多专业软件（Adobe全家桶、Solidworks、Rhino等），形成Agent操控专业工具的生态
- 中期：EchoCAD这类统一架构项目会越来越多，不同软件通过MCP统一接入Agent层。Agent成为专业软件的"上层界面"
- 长期：设计师的核心能力从"操作熟练度"转向"设计思维+AI协作能力"。专业软件的竞争维度从功能丰富度转向"AI可连接性"

## 相关笔记

- [2026-05-05-Hermes-NotebookLM知识管理自动挡](2026-05-05-Hermes-NotebookLM知识管理自动挡.md) - Agent作为中间层连接工具的趋势
- [2026-05-04-Agent协议生态2026最新进展-MCP-A2A深度融合](2026-05-04-Agent协议生态2026最新进展-MCP-A2A深度融合.md) - MCP协议生态的宏观进展
