# 开源3D/设计AI: OpenSCAD+LLM

> 嗅探学习笔记 | 2026-07-14 | auto-explore

## 摘要

OpenSCAD 作为纯文本代码定义 3D 几何的 DSL，正成为 LLM 生成 3D 模型的最佳目标语言。2026 年多个基准测试显示，顶级 LLM（Gemini 3.5 Flash、Claude Sonnet 4.6、Codex 5.5）已能从自然语言+参考图直接生成可渲染的参数化 OpenSCAD 代码，质量达到"初稿可用"水平。开源生态形成 CadQuery（Python，输出 STEP）+ OpenSCAD（DSL，输出 STL）+ Zoo.dev ML-CAD（端到端 mesh）三层格局。

## 关键发现

### 1. ModelRift Pantheon 基准测试（2026-05-21）

ModelRift 让 6 个 AI 编码工具用 OpenSCAD 构建罗马万神殿（含圆厅、穹顶、柱廊、山花），评估空间推理能力：

- **Google Antigravity 2.0 / Gemini 3.5 Flash High — 最佳自主结果（4.5/5）**
  - 唯一搜索真实万神殿尺寸而非凭图片"目测"的 Agent
  - 唯一实现标志性内部藻井天花板（5 圈×28 格）的自主 Agent
  - 支持剖面模式切换 `show_cutaway`，内外兼顾
  - 包含混合灰/红柱材质、可读铭文（M AGRIPPA...）
  - 耗时约 12 分钟，速度评分 1/5

- **ModelRift + Gemini Flash 3.0 — 人机协作最佳（3.8/5）**
  - 核心工作流：生成模型 → 浏览器检查 → 在渲染图上画箭头/标注 → 反馈给 AI 修改 OpenSCAD
  - 视觉标注比纯文本指令更精准，尤其适合空间几何纠错

- **Codex 5.5 High — 密度最高但导出翻车（3.0/5）**
  - 包含最丰富细节：铭文、穹顶肋骨、眼洞、砌体层
  - 预览渲染良好但最终 STL 导出在柱廊屋顶处出现非流形几何问题
  - 暴露关键风险：预览正确 ≠ 最终 mesh 正确

- **Claude Sonnet 4.6 — 原始批次最干净（3.4/5）**
  - 比例最协调，整体读起来像一栋建筑而非拼接体
  - 但速度最慢（2-3x 于 Codex）

- **Cursor Composer 2.5 — 最快但最弱（1.4/5）**
  - 速度第一但质量垫底，像简化占位符

- **Claude Opus 4.7 — 中间水平（3.0/5）**
  - 结构完整但色彩单一，细节缺乏层次

### 2. 为什么 OpenSCAD 是 LLM 的理想目标语言

- 纯文本代码，词汇表紧凑（cube/cylinder/difference/union/for 循环）
- LLM 可直接说"在半径上重复 28 根柱子"或"从穹顶减去眼洞"
- 结果可检查、可复现、易修改（改参数而非场景状态）
- 比 Blender MCP 等 UI 驱动方式更自然——几何本身就是产物
- 局限：不适合有机曲面/雕塑/角色，擅长布尔运算/径向对称/挤出/构造实体

### 3. 开源 Text-to-CAD 三层格局（Leo AI 综述）

- **CadQuery + LLM — 参数化输出最佳**
  - 基于 OpenCASCADE 内核，输出 BRep 几何体 + STEP 文件
  - 可导入 SolidWorks/Creo/NX，尺寸参数化
  - 擅长棱柱几何（外壳、支架、夹具），弱于有机曲面/多体装配

- **OpenSCAD + AI 封装 — 3D 打印友好**
  - CSG 构造实体几何，输出 STL 直接切片
  - 语言比 Python 简单，LLM 生成正确率更高
  - 缺点：无倒角/圆角操作，默认导出 STL 非 STEP

- **Zoo.dev ML-CAD — 端到端推理最快**
  - 直接从文本预测 3D mesh，非代码生成
  - 秒级输出但精度低，尺寸不可控
  - 可本地 GPU 运行，完全免费私密

### 4. DesignBench（Build Great AI / Dan Becker）

- 多模型并行生成 OpenSCAD 代码 → 转 STL → 3D 打印
- 使用 LLaMA 3.1、GPT-4、Claude 3.5 并行而非依赖单模型
- 设计时间从小时级降至分钟级
- 用多模型策略应对 LLM 空间推理局限性

## 对工作的价值

1. **参数化设计自动化** — 我们已有 open-source-hardware-project Skill 涉及 OpenSCAD 3D 打印。LLM 生成 OpenSCAD 代码可直接嵌入该工作流，从需求描述到可打印 STL 全自动
2. **视觉标注反馈循环** — ModelRift 的 Annotation Mode（在渲染图上画箭头反馈）是一种通用的人机协作模式，可借鉴到我们的 Hermes 图文交互中
3. **预览 ≠ 导出的教训** — 任何 LLM 生成 → 渲染 → 导出的流水线，都必须对最终产物做独立验证，不能只信中间预览
4. **多模型并行策略** — DesignBench 的并行生成思路适用于所有"单模型空间推理弱"的场景

## 行动建议

- 短期：在 open-source-hardware-project Skill 中增加 LLM→OpenSCAD→CLI 渲染→STL 验证的标准流程
- 中期：评估 CadQuery+LLM 作为 OpenSCAD 的补充（需要 STEP 输出的工程场景）
- 参考：ModelRift 的 Annotation Mode 理念可融入我们任何涉及视觉反馈的 Agent 工作流

## 参考来源

- ModelRift: OpenSCAD LLM Benchmark: Building the Pantheon (2026-05-21)
  https://modelrift.com/blog/openscad-llm-benchmark
- Leo AI: Open-Source Text-to-CAD Tools (2026-05-15)
  https://www.getleo.ai/blog/open-source-text-to-cad-tools-free
- ZenML LLMOps: LLM-Powered 3D Model Generation (DesignBench)
  https://www.zenml.io/llmops-database/llm-powered-3d-model-generation-for-3d-printing
- Reddit r/openscad: DayDream — LLM based CAD generator
- ScienceDirect: LLM-based 3D Model Generation of MHE for OpenSCAD (ELhadad, 2026)

## 相关笔记

- [开源3D/设计AI: LLM空间推理 (Antigravity)](./2026-07-13-开源3D_设计AI-LLM空间推理-(Antigravit.md) — Antigravity 2.0 空间推理评估
- [开源3D/设计AI: AI编程3D建模](./2026-07-12-开源3D_设计AI-AI编程3D建模.md) — AI 编码工具 3D 建模能力对比
- [开源3D/设计AI: text-to-3D](./2026-07-10-开源3D_设计AI-text-to-3D.md) — 文本生成 3D 模型方法综述
- [开源3D/设计AI: OpenSCAD+LLM](./2026-06-12-开源3D_设计AI-OpenSCAD+LLM.md) — 早期 OpenSCAD+LLM 探索
