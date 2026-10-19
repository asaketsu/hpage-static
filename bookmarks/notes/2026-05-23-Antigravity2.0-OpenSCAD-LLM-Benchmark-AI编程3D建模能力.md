# Antigravity 2.0 与 OpenSCAD LLM Benchmark：AI 编程工具的 3D 建模能力

> **来源**：TechCrunch / ModelRift Blog · 2026-05-19
> **原文**：https://techcrunch.com/2026/05/19/google-launches-antigravity-2-0/ | https://modelrift.com/blog/openscad-llm-benchmark
> **评分**：⭐⭐⭐⭐/5
> **标签**：#Google #Antigravity #AI编程 #LLM基准 #OpenSCAD #3D建模
> **关联**：[Claude Code](2026-05-21-10万行Rust-AI开发实战-Code-Contracts与性能优化.md) [Python 3.15 隐藏特性](2026-05-22-Python315-隐藏特性-被大新闻掩盖的实用改进.md)

## 摘要

Google IO 2026 发布 Antigravity 2.0，包含更新版桌面应用、CLI 工具和自定义工作流 SDK。同时，ModelRift 发布 OpenSCAD LLM 基准测试，以「用 OpenSCAD 构建万神殿」为任务，对比 Codex 5.5 High、Claude Sonnet、Claude Opus、Cursor Composer、Google Antigravity 和 ModelRift 的 3D 建模能力。结果显示：Antigravity 2.0 在 architectural 3D 建模任务中表现最佳。

## 核心内容

### Antigravity 2.0 发布要点

Google Antigravity 是 2025 年 11 月发布的 AI 编程工具，对标 Cursor。2.0 版本新增：

1. **桌面应用更新**：更完整的本地开发环境集成
2. **CLI 工具**：命令行接口，支持脚本化工作流
3. **SDK**：自定义工作流开发，允许用户构建专属 Agent 流程
4. **AI Ultra 订阅**：$100/月，使用量是 AI Pro 的 5 倍

### OpenSCAD LLM Benchmark

ModelRift 设计了一个实用基准：给多个 AI 编程工具相同的任务——从参考图片构建万神殿（Pantheon）的 OpenSCAD 参数化 CAD 代码。

**为什么选 OpenSCAD？**
- 纯文本代码，词汇量紧凑
- 需要空间理解和几何推理
- 可自动化验证（OpenSCAD CLI 渲染预览）
- 处于「简单几何」和「复杂建模」之间的中间地带

**参与模型/工具：**
- Codex 5.5 High
- Claude Sonnet
- Claude Opus
- Cursor Composer
- Google Antigravity
- ModelRift

**结果**：Antigravity 2.0 在 architectural 3D 建模基准中排名第一，展示了 Google 在空间推理和参数化建模方面的优势。

### 空间理解仍是弱项

Sebastian Raschka 的 LLM 架构分析指出：尽管 LLM 在代码生成方面进步显著，但空间理解能力仍然薄弱。OpenSCAD 基准揭示了这一点——即使是最好的模型，在复杂几何体的参数化建模上仍有改进空间。

## 关键概念

| 概念 | 定义 |
|------|------|
| OpenSCAD | 基于代码的 3D 建模语言，适合参数化设计 |
| Parametric CAD | 参数化计算机辅助设计，用代码定义几何关系 |
| Architectural Benchmark | 建筑学基准，测试 AI 的空间理解和几何推理能力 |
| Antigravity | Google 的 AI 编程工具，对标 Cursor |

## 能力边界

1. OpenSCAD 基准仅测试参数化建模能力，不覆盖自由曲面建模
2. 空间理解仍是 LLM 的弱项，复杂几何体建模仍有局限
3. Antigravity 2.0 作为闭源工具，无法像开源模型那样本地部署
4. 基准测试规模较小（仅一个万神殿任务），需要更多场景验证

## 最佳实践

1. 使用「代码渲染预览」作为自动验证手段，而非仅靠人工检查
2. 参数化建模适合 LLM 基准测试：代码紧凑、可验证、有明确输出
3. CLI + SDK 组合提供更大的灵活性，适合集成到现有工作流
4. 空间推理能力需要专门的基准和训练，不能依赖通用代码能力

## 🔍 借鉴学习进化点（必填）

| # | 点 | 原文要点 | 对当前系统的借鉴 | 行动计划 |
|---|-----|---------|---------------|---------|
| 1 | 代码渲染验证 | OpenSCAD CLI 渲染预览作为自动验证手段 | 当前笔记缺乏视觉验证环节 — 对于生成 HTML/CSS 的笔记，应自动截图验证渲染效果 | 在 note-dual-format skill 中加入自动截图验证步骤 |
| 2 | 参数化基准设计 | 用 OpenSCAD 作为 LLM 空间理解基准 | 可设计类似的「参数化任务基准」测试 Hermes 的生成质量，如自动生成可运行的 HTML 页面 | 创建 Hermes 生成质量基准测试脚本 |
| 3 | CLI + SDK 组合 | Antigravity 提供 CLI 和 SDK 双重接口 | Hermes 的 skill 系统可借鉴此模式：每个 skill 既有 CLI 入口又有 API 接口 | 为高频 skill 添加 API 层，支持程序化调用 |
| 4 | 空间推理基准 | LLM 空间理解仍是弱项 | 当前系统缺乏空间推理能力评估 — 可在 evolver 中加入空间理解测试维度 | 在 evolver 评估框架中增加「空间/几何理解」评分项 |
| 5 | 对标竞品迭代 | Google 对标 Cursor 推出 Antigravity | 当前系统可定期对标 Cursor/Codex 等竞品，评估自身能力差距 | 在 auto-learner skill 中加入竞品对标模块 |

## 🔗 RAG / Wiki 联动

### 当前状态
- wiki-kb：已有 AI 编程实践笔记（Rust Code Contracts）
- RAG：已有 Google 相关笔记（AI Mode 搜索广告）
- Memory：需更新 Google 生态动态

### 改进方案
1. 在 topics-index 中新增 antigravity-llm-coding 条目
2. 关联已有 ai-coding-practice 和 google-ai-mode-ads
3. 将 OpenSCAD 基准方法加入评测知识库

### 已执行操作
- ✅ 笔记已生成
- ⏳ 待更新 topics-index.json
- ⏳ 待更新 sniff-queue.json

## 相关笔记
- [增材制造结构件静力与疲劳研究笔记](2026-05-22-增材制造结构件静力与疲劳研究笔记.md)
- [CAD模型检索完结篇-从分类到相似性检索的系统化落地](explore/2026-05-20-CAD模型检索完结篇-从分类到相似性检索的系统化落地.md)
- [MLA多头潜在注意力-DeepSeek-KV缓存压缩与推理优化](2026-05-21-MLA多头潜在注意力-DeepSeek-KV缓存压缩与推理优化.md)
- [llm-finetune-dataflow-dataflex-pipeline](2026-05-21-llm-finetune-dataflow-dataflex-pipeline.md)
- [react-agent-llm-agentic-training-research](2026-05-21-react-agent-llm-agentic-training-research.md)
- [If-youre-an-LLM-please-read-this-Anna-Archive-LLM伦理契约](2026-05-22-If-youre-an-LLM-please-read-this-Anna-Archive-LLM伦理契约.md)
- [LoRA-GRPO最优配置实证-RL场景的Rank选择与超参数](2026-05-22-LoRA-GRPO最优配置实证-RL场景的Rank选择与超参数.md)
- [Multi-Stream-LLMs-并行流解锁语言模型](2026-05-22-Multi-Stream-LLMs-并行流解锁语言模型.md)
- [OpenAI后训练团队Yann-Dubois深度访谈](2026-05-23-OpenAI后训练团队Yann-Dubois深度访谈.md)
- [QLoRA在RL训练中的精度影响-量化与强化学习深度解析](2026-05-23-QLoRA在RL训练中的精度影响-量化与强化学习深度解析.md)
- [边缘AI推理优化-Jetson平台深度研究](explore/2026-05-21-边缘AI推理优化-Jetson平台深度研究.md)
- [llama-cpp预编译二进制与本地LLM推理](explore/2026-05-22-llama-cpp预编译二进制与本地LLM推理.md)
- [VPO向量策略优化多样性训练提升推理搜索](explore/2026-05-23-VPO向量策略优化多样性训练提升推理搜索.md)
- [llm-inference-opt-deep-dive](explore/llm-inference-opt-deep-dive.md)
