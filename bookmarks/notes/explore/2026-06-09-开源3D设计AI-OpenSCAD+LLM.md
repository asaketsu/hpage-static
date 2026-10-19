# 开源3D/设计AI: OpenSCAD + LLM

> 嗅探学习 | 2026-06-09 | 来源: TinyFish Search + HN Algolia + arXiv + curl直取

## 摘要

OpenSCAD 作为文本驱动的参数化3D建模语言，天然适配 LLM 代码生成能力。2024-2026年间，"自然语言→OpenSCAD代码→3D模型"的技术栈快速成熟，涌现出 SynapsCAD（开源IDE）、AdamCAD/CADAM（商业+开源）、CADCodeVerify（学术验证框架）等代表性项目。核心范式是：LLM生成CAD脚本代码 → 渲染引擎编译为3D模型 → 视觉反馈闭环迭代修正。

## 关键发现

**1. SynapsCAD — 开源AI驱动的3D CAD IDE**
- GitHub: github.com/ierror/synaps-cad (61pts on HN)
- Rust 编写的桌面应用，集成 OpenSCAD 编辑器 + 实时3D视口 + AI助手
- 支持多LLM后端：Anthropic/OpenAI/Gemini/DeepSeek/Ollama（本地离线）
- 自然语言修改设计，支持3D点击交互上下文
- 跨平台：Linux/macOS/Windows

**2. AdamCAD/CADAM — Text-to-CAD 商业+开源双轨**
- HN 188pts（商业版）+ 179pts（开源版 CADAM）
- 浏览器端 Text-to-CAD 应用，AI co-pilot 模式
- 开源版本在 GitHub: github.com/Adam-CAD/CADAM

**3. CADCodeVerify — 学术验证框架（arXiv:2410.05340）**
- 问题：LLM生成的CAD代码可能不满足要求，但3D对象正确性难以文本验证
- 方案：VLM（视觉语言模型）生成验证问题 → 视觉反馈 → 迭代修正
- CADPrompt：首个CAD代码生成基准，200个NL提示+专家标注代码
- GPT-4 + CADCodeVerify：点云距离降低7.30%，成功率提升5.0%

**4. OpenSCAD MCP Server — 工作流集成**
- 通过MCP协议连接LLM和OpenSCAD
- VSCode集成，免复制粘贴，直接在编辑器内生成+预览
- Sergio Carracedo 实测：GitHub Copilot + 图片输入 → 直接生成3D房屋模型

**5. 技术栈核心特征**
- OpenSCAD 是纯文本描述语言（类似Logo），无GUI学习曲线
- 参数化设计天然适合LLM：变量、函数、模块化结构与编程范式一致
- 闭环迭代模式：LLM生成 → 渲染 → VLM验证 → 反馈修正

## 对工作的价值

- **快速原型设计**：描述需求即得3D模型，适合非专业设计师快速迭代
- **MCP集成模式**：OpenSCAD MCP Server 可集成到 Hermes Agent 工具链，实现"对话式3D建模"
- **视觉验证闭环**：CADCodeVerify 的 VLM 反馈模式可迁移到其他代码生成场景
- **Jetson部署潜力**：SynapsCAD支持Ollama本地模型，可在Jetson Orin上离线运行

## 行动建议

1. 试用 SynapsCAD + Ollama 本地模型，验证离线3D建模效果
2. 评估 OpenSCAD MCP Server 集成到 Hermes 的可行性
3. 关注 CADCodeVerify 论文的视觉反馈模式，考虑泛化到代码审查场景

## 参考来源

- SynapsCAD: https://github.com/ierror/synaps-cad
- AdamCAD: https://www.adamcad.com/ | https://github.com/Adam-CAD/CADAM
- CADCodeVerify: arXiv:2410.05340 (2024.10, revised 2025.02)
- OpenSCAD MCP: Reddit r/openscad
- Sergio Carracedo 博客: https://sergiocarracedo.es/designing-physical-items-with-llms/
- ScienceDirect: LLM-based 3D Model Generation of MHE for OpenSCAD (2026)

## 相关笔记
- [开源3D_设计AI-OpenSCAD+LLM](2026-06-09-开源3D_设计AI-OpenSCAD+LLM.md)
- [开源3D_设计AI_OpenSCAD+LLM](2026-06-09-开源3D_设计AI_OpenSCAD+LLM.md)
- [ESP32语音助手方案-本地Docker+云端LLM](../2026-06-09-ESP32语音助手方案-本地Docker+云端LLM.md)
- [TinyML边缘AI-2026年微控制器端侧推理现状与演进](../2026-06-09-TinyML边缘AI-2026年微控制器端侧推理现状与演进.md)
- [具身智能TL面经-数据训练SFT与Sim2Real闭环](../2026-06-09-具身智能TL面经-数据训练SFT与Sim2Real闭环.md)
- [llm-inference-optimization-2026](../2026-06-10-llm-inference-optimization-2026.md)
- [Code2LoRA超网络代码适配器](2026-06-07-Code2LoRA超网络代码适配器.md)
- [YouZhi金融LLM高并发推理](2026-06-08-YouZhi金融LLM高并发推理.md)
- [Q-Evolve自进化LLM-Agent](2026-06-09-Q-Evolve自进化LLM-Agent.md)
