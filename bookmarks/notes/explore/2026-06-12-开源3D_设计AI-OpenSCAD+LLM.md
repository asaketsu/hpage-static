# 开源3D/设计AI: OpenSCAD + LLM

> 嗅探学习 · 2026-06-12

## 摘要

OpenSCAD 是基于代码的参数化 3D 建模工具，天然适合 LLM 生成——用自然语言描述需求，LLM 输出 .scad 代码，即可渲染出可打印的 3D 模型。当前生态已形成 PartCAD + MCP Server + AnchorSCAD 三条技术路线，可用性显著提升。

## 关键发现

**1. 核心范式：自然语言 → 代码 → 3D模型**
- OpenSCAD 用类 C 语法描述几何体（union/difference/intersection），LLM 擅长生成本类结构化代码
- 典型流程：描述物体 → LLM 生成 .scad → OpenSCAD 渲染 → 迭代修改
- 15 分钟可完成参数化钥匙扣等简单零件设计（传统 CAD 需数小时）

**2. 三个关键工具/项目**
- **PartCAD**（github.com/openvmp/partcad）：VS Code 扩展，内置 AI 生成流程，支持 OpenSCAD/CadQuery，可配置任意 LLM（OpenAI/Gemini/Ollama）
- **OpenSCAD MCP Server**（github.com/quellant/openscad-mcp）：基于 FastMCP 框架，让 AI Agent（Claude/Cursor）直接调用 OpenSCAD 渲染
- **AnchorSCAD**：Python 封装层，提供 anchor（锚点）隐喻——LLM 更易理解"放到这个面的中心"而非手动计算坐标

**3. 模型能力现状**
- ChatGPT/OpenAI：新内容生成质量更优
- Gemini：增量修改迭代表现更好
- 关键洞察：效果取决于 agentic workflow 逻辑而非模型质量（PartCAD 团队观点）
- build123d 框架：LLM 尚未充分学习，生成代码常无法运行

**4. 学术研究**
- ScienceDirect 2026 论文：LLM-based 3D Model Generation of MHE for OpenSCAD——用 LLM 自动生成物料搬运设备参数化模型
- SceneCraft（arXiv 2403）：LLM 生成 Blender Python 脚本组装 3D 场景，含视觉反馈闭环

## 对工作的价值

- **快速原型**：3D 打印零件无需学 CAD，自然语言即可出图
- **Agent 工具链**：OpenSCAD MCP Server 可直接集成到 Hermes 工具体系
- **参数化设计**：.scad 代码即设计文档，版本可控、可复用、可共享
- **结构工程辅助**：与 struct-gen Skill 结合，理论上可从验算结果直接生成连接件/节点 3D 模型

## 行动建议

1. **体验**：安装 OpenSCAD MCP Server，测试 Agent 直接生成简单零件
2. **评估 PartCAD**：VS Code 插件，对比如 Direct MCP 方案的易用性
3. **跟踪 AnchorSCAD**：Python 抽象层降低 LLM 出错率，适合做 Agent 的 CAD 中间件
4. **暂不投入**：build123d 等不成熟框架，等社区验证后再考虑

## 参考链接

- PartCAD: https://github.com/openvmp/partcad
- OpenSCAD MCP Server: https://github.com/quellant/openscad-mcp
- Reddit 讨论: https://www.reddit.com/r/openscad/comments/1bynbdh/generate_openscad_with_ai
- Sergio Carracedo 博文: https://sergiocarracedo.es/designing-physical-items-with-llms
- LLM+MHE 论文: https://www.sciencedirect.com/science/article/pii/S1877050926000773

## 相关笔记
- [开源3D设计AI-OpenSCAD+LLM](2026-06-09-开源3D设计AI-OpenSCAD+LLM.md) (关键词: OpenSCAD, LLM, 3D建模)
- [开源3D_设计AI-AI编程3D建模](2026-06-10-开源3D_设计AI-AI编程3D建模.md) (关键词: 3D, AI编程)
- [开源3D_设计AI:-text-to-3](2026-06-01-开源3D_设计AI:-text-to-3.md) (关键词: 3D, text-to-3D)
- [CAD模型检索完结篇](2026-05-20-CAD模型检索完结篇-从分类到相似性检索的系统化落地.md) (关键词: CAD)
