# 开源3D/设计AI：OpenSCAD + LLM

> 嗅探学习 · 2026-07-21 · auto-explore

## 摘要

OpenSCAD 是一款纯代码驱动的 3D 建模工具（脚本进、网格出），因其**函数式 DSL、词表紧凑、确定性输出、天然沙箱**四大特性，正成为 LLM 生成 3D 几何的最优目标语言。2026 年围绕 OpenSCAD+LLM 已形成完整生态：ModelRift（AI 编辑器）、DayDream（多轮 LLM 渲染）、Energent.ai（蓝图→脚本）等，Manifold 渲染后端将复杂模型渲染速度提升 20-200 倍，使实时交互编辑可行。

## 关键发现

**1. 为什么是 OpenSCAD 而不是 CadQuery/Blender**
- OpenSCAD 语言表面积小（几十个函数、无类、无状态），LLM 生成代码"一次过"率高；CadQuery 依赖完整 Python + OpenCASCADE API，LLM 常在拓扑/边选择上出错
- 安全沙箱极简：OpenSCAD 无文件 I/O、无网络、无系统调用，最坏情况只是畸形网格；Python 沙箱逃逸向量上千
- 输出确定性：同一段代码永远产生同一模型，便于 review 与 diff

**2. STL vs STEP 的根本取舍**
- OpenSCAD 输出 STL/3MF（网格），不输出 STEP（B-Rep）。$fn 控制圆弧近似段数，圆柱 $fn=32→7KB，$fn=256→54KB
- 3D 打印 STL 足够；CNC/注塑需 STEP 时应选 CadQuery（基于 OpenCASCADE，原生 B-Rep）

**3. Manifold 后端是分水岭**
- 传统 CGAL 内核用任意精度有理数，健壮但极慢（复杂模型 20 分钟）
- 2024 年加入 Manifold：双精度浮点 + 拓扑保证 + 并行算法，基准模型快 20-200 倍（540s→27s，1132s→11s）
- 这是让 AI 实时渲染迭代成为可能的关键基础设施

**4. ModelRift Pantheon 基准测试（2026）**
六款 AI 工具用 OpenSCAD 构建万神殿的横向对比：
- Google Antigravity 2.0 / Gemini 3.5 Flash High — 最佳自主结果（4.5/5），唯一实现内部穹顶方格天花
- ModelRift + Gemini Flash 3.0 — 人机协同最佳（3.8/5），用标注迭代工作流
- Cursor 3.5 / Composer 2.5 — 最快但最差（1.4/5），速度不等于质量
- 所有工具均能正确调用 OpenSCAD CLI 渲染预览，瓶颈不在工具调用而在几何判断力
- 预览≠导出：Codex 渲染好看但 STL 导出有几何问题

**5. 2026 开源 Text-to-CAD 工具谱系**
- CadQuery + LLM：最强参数化/STEP 输出，适合机械零件（支架、夹具、外壳）
- OpenSCAD + AI Wrapper：CSG 构造、3D 打印友好、Maker 社区最大（Thingiverse Customizer 生态）
- Zoo.dev ML-CAD：开源 ML 模型路线
- 商业：Leo AI、Energent.ai（94.4% 文档解析准确率）

## 对工作的价值

- **硬件项目流水线加速**：Jetson/ESP32 项目的 3D 打印外壳、传感器支架可用自然语言生成 OpenSCAD 脚本，无需手动建模。结合已有的 `open-source-hardware-project` Skill 可实现"描述→脚本→渲染→STL→打印"全自动
- **Agent 编排新场景**：OpenSCAD CLI 是纯命令行、确定性输入输出，天然适合作为 Agent 工具调用节点。可嵌入硬件项目脚手架，LLM 生成 .scad → OpenSCAD CLI 渲染 PNG 预览 → 视觉模型判断 → 迭代修正
- **Manifold 性能启示**：复杂几何渲染从 20 分钟降到秒级，说明"选对底层引擎"对 AI 交互式工作流至关重要——同理适用于本地 LLM 推理引擎选型

## 行动建议

1. **立即可做**：在 Jetson 上 `apt install openscad`（或 snap），验证 Manifold 后端可用性，将 OpenSCAD CLI 加入硬件项目脚手架的可用工具清单
2. **短期（1-2周）**：写一个 Skill `openscad-llm-design`——输入自然语言描述 → LLM 生成 .scad → CLI 渲染 STL+PNG → 返回文件路径。覆盖外壳/支架/夹具三类高频零件
3. **中期**：探索 OpenSCAD + 图片标注的人机协同工作流（ModelRift Annotation Mode 的开源自实现），用于复杂结构件设计
4. **观察项**：STEP 导出需求若出现，转向 CadQuery 路线（已有 BOSL2 库可补足部分 OpenSCAD 短板，但 B-Rep 仍需 OCCT）

## 参考链接
- ModelRift 为什么选 OpenSCAD: https://modelrift.com/blog/why-openscad
- Pantheon LLM 基准测试: https://modelrift.com/blog/openscad-llm-benchmark
- 开源 Text-to-CAD 工具综述: https://www.getleo.ai/blog/open-source-text-to-cad-tools-free
- DayDream（LLM OpenSCAD 生成器）: https://daydream.cariboolabs.ca/
- Manifold 几何库: https://github.com/elalish/manifold


## 相关笔记

- [开源3D设计AI-OpenSCAD+LLM](./2026-07-14-开源3D_设计AI-OpenSCADLLM.md) — 同主题前序笔记，OpenSCAD DSL 生态
- [开源3D设计AI-AI编程3D建模](./2026-07-16-开源3D_设计AI-AI编程3D建模.md) — AI 编程驱动的 3D 建模范式
- [开源3D设计AI-text-to-3D](./2026-07-15-开源3D_设计AI-text-to-3D.md) — Text-to-3D 生成路径对比
- [开源3D设计AI-LLM空间推理](./2026-07-13-开源3D_设计AI-LLM空间推理-(Antigravit.md) — LLM 空间推理能力与 3D 设计
