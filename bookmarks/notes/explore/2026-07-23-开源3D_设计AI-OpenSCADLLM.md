# 开源3D/设计AI: OpenSCAD+LLM

> 嗅探学习笔记 | 2026-07-23 | auto-explore

## 摘要

LLM + OpenSCAD 组合正在成为 AI 驱动 3D 设计的核心范式。核心思路：用自然语言描述 → LLM 生成 OpenSCAD 代码（或 build123d/Python CAD 代码）→ 渲染为可编辑的参数化 3D 模型 → 导出 STL/STEP/DXF 用于打印或制造。相比直接生成 mesh/点云的方法，代码生成路线的最大优势是**完全参数化、可编辑、可验证**。

## 关键发现

### 1. 技术路线分化：两条主流路径

**路径 A：OpenSCAD 代码生成（参数化代码即模型）**
- 代表项目：CADAM（⭐4847）、Agentic3D（UC Berkeley）、BambuAgent
- 原理：LLM 直接输出 OpenSCAD 脚本，浏览器 WASM 渲染预览，参数通过滑块交互调整
- 优势：输出完全可编辑、参数化，导出 STL/SCAD/DXF，支持 BOSL2 库

**路径 B：Python CAD Kernel + MCP 协议**
- 代表项目：CAD/CAE Copilot（⭐41）、Kiln（⭐39）
- 原理：Agent 通过 MCP 协议调用 build123d/OpenCASCADE 几何引擎，输出 STEP（工业标准）
- 优势：支持拓扑指针（稳定面引用）、确定性批评验证、CAD→CAE 闭环（FEA 仿真）

### 2. 核心项目速览

**CADAM（⭐4847，最成熟）**
- 开源 Text-to-CAD Web 应用，React + Supabase + OpenSCAD WASM
- 自然语言 + 图片输入 → 实时 Three.js 预览 → 参数滑块调整 → 一键导出
- Benchmark 展示：V8 引擎、涡扇发动机、径向航空引擎等复杂装配体（22+ 参数维度）
- 在线试用：adam.new/cadam

**Kiln（⭐39，端到端打印）**
- MCP Server for 3D 打印，pip install kiln3d 即装即用
- AI Agent 全链路：设计 → 切片 → 排队 → 监控摄像头 → 故障恢复 → 发货
- 支持 Bambu Lab/Prusa/Creality/Elegoo/Voron 等 12+ 打印机品牌
- 一句话生成杯垫："a coaster with my dog Ash's photo" → 41 分钟全自动完成

**CAD/CAE Copilot（⭐41，工业级）**
- build123d/OpenCASCADE 真实几何内核（非 mesh 渲染）
- 输出 STEP（工业标准）+ STL/GLB，支持材料/载荷/网格/求解器全 CAE 链路
- 每个操作生成 `.aieng` 可复现工程包，含拓扑指针和设计规则校验
- 机器可读 FEA benchmark 语料库，CI 自动回归

**Agentic3D（UC Berkeley 研究）**
- 多 Agent 框架（Autogen 编排），LLM 生成 OpenSCAD → VLM 视觉评估 → 迭代修正
- 模态切换反馈闭环：文本→代码→渲染→视觉分析→代码修正

### 3. 技术架构共性

- **代码即模型**：3D 模型以程序代码（OpenSCAD/Python）形式存在，天然支持参数化和版本管理
- **渲染闭环**：LLM 生成 → 渲染验证 → VLM/确定性检查 → 迭代修正
- **MCP 协议集成**：越来越多项目把 CAD 引擎包装为 MCP Server，让任意 AI Agent 可调用
- **WASM 浏览器化**：OpenSCAD 编译为 WebAssembly，实现纯前端零安装体验

## 对工作的价值

1. **硬件项目加速**：我们已有 open-source-hardware-project Skill 做 OpenSCAD 参数化设计。引入 LLM 代码生成可以大幅缩短从需求到模型的时间——用自然语言描述零件意图，自动生成参数化 SCAD 代码
2. **MCP 集成机会**：Kiln 和 CAD/CAE Copilot 都是 MCP Server，可以直接接入 Hermes Agent，实现"对话即设计→打印"全流程
3. **验证范式参考**：CAD/CAE Copilot 的 `.aieng` 可复现工程包 + 确定性批评模式，值得借鉴到我们的代码生成质量门禁中
4. **参数化模型库**：CADAM 的参数滑块交互模式，可以作为我们硬件项目 3D 打印零件库的前端参考

## 行动建议

- **短期**：试用 CADAM 在线版（adam.new/cadam），评估其生成的 OpenSCAD 代码质量
- **中期**：在 Hermes 中集成 Kiln MCP Server，实现"对话→设计→3D打印"闭环（我们有 Jetson + 打印机环境）
- **长期**：研究 CAD/CAE Copilot 的 build123d 路线，对比 OpenSCAD 方案，为工业级零件设计选择更合适的 CAD kernel

## 来源

- CADAM: https://github.com/Adam-CAD/CADAM (⭐4847)
- Kiln: https://github.com/codeofaxel/Kiln (⭐39)
- CAD/CAE Copilot: https://github.com/armpro24-blip/cad-cae-copilot (⭐41)
- Agentic3D: https://github.com/reetm09/agentic3d (UC Berkeley)
- DoodleMe: https://github.com/RohanDwivedi/DoodleMe (Claude LLM + ROS2 + OpenSCAD + URDF + KiCad)


## 相关笔记

- [开源3D: LLM空间推理](./2026-07-24-开源3D_设计AI-LLM空间推理-(Antigravit.md) — 80 模型空间推理基准
- [开源3D: AI编程3D建模](./2026-07-22-开源3D_设计AI-AI编程3D建模.md) — AI 3D 建模综述
- [开源3D: text-to-3D](./2026-07-22-开源3D_设计AI-text-to-3D.md) — 文本生成 3D 路线
- [开源3D: OpenSCAD+LLM (07-21)](./2026-07-21-开源3D_设计AI-OpenSCADLLM.md) — 早期 OpenSCAD 探索
