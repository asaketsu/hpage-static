# llm_wiki 开源项目分析与 Skill 进化报告

> **日期**: 2026-05-20
> **来源**: [nashsu/llm_wiki](https://github.com/nashsu/llm_wiki) — 8.2k ⭐ / 1k Fork / GPL v3
> **作者**: nashsu
> **基础**: Andrej Karpathy's [LLM Wiki pattern](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f)

---

## 项目概况

LLM Wiki 是一个**跨平台桌面应用**（Tauri + Rust 后端 + Web 前端），将文档自动转化为结构化、互联的知识库。与 RAG 每次"从头检索"不同，它**增量构建并维护持久化 Wiki**。

| 维度 | 数据 |
|---|---|
| 技术栈 | Tauri (Rust) + Vue.js + sigma.js |
| 版本 | v0.4.12（活跃开发中，443 commits） |
| 知识图谱 | sigma.js + graphology + ForceAtlas2 |
| 向量搜索 | LanceDB + OpenAI Embedding（可选） |
| 社区检测 | Louvain 算法 |
| 格式支持 | PDF/DOCX/PPTX/XLSX/图片/视频/音频 |
| 扩展 | Chrome Web Clipper |
| Deep Research | Tavily/SerpApi/SearXNG |

## 核心创新（vs 传统 RAG）

### 1. 两步 Chain-of-Thought Ingest

将文档处理拆为两步：
- **Step 1 (Analysis)**: LLM 读取源 → 提取实体/概念/与已有知识的矛盾/关联
- **Step 2 (Generation)**: 基于分析结果 → 生成 Wiki 页面 + 更新索引

这比单步（边读边写）质量更高，减少了漏改和重复。

### 2. 4-Signal Relevance Model

查询时利用 Wiki 的链接结构做相关性扩展：

| 信号 | 权重 | 说明 |
|---|---|---|
| Direct link | ×3.0 | `[[wikilink]]` 直接链接 |
| Source overlap | ×4.0 | 共享同一原始来源 |
| Adamic-Adar | ×1.5 | 共享邻居节点 |
| Type affinity | ×1.0 | 同类型页面 |

向量搜索启用后 recall 从 58.2% → 71.4%。

### 3. Louvain 社区检测

自动发现知识集群，识别"主题岛"和知识缺口。

### 4. purpose.md

显式定义 Wiki 的存在目的，防止内容走偏。

### 5. Review Queue

低置信度/矛盾内容推入异步人工审核队列。

### 6. 知识缺口自动检测

Ingest 时识别关键但缺失的实体/概念，自动触发 Deep Research。

## 与我们的对比

| 维度 | llm_wiki | 我们的 llm-wiki Skill v2.2 |
|---|---|---|
| 形式 | 桌面应用 | Agent Skill（纯文本） |
| 知识图谱可视化 | ✅ sigma.js | Obsidian Graph View |
| 向量搜索 | ✅ LanceDB | ✅ Gemini/OpenRouter Embedding |
| 社区检测 | ✅ Louvain | ✅ Label Propagation（lint） |
| 多领域路由 | ❌ 单实例 | ✅ ROUTER.md |
| 记忆整合 | ❌ | ✅ Memory+Wiki+RAG+Notes 四源 |
| 矛盾处理 | ❌ | ✅ contradictions frontmatter |
| 标签治理 | ❌ | ✅ 严格 taxonomy + 审计 |
| 增量哈希 | ❌ | ✅ sha256 漂移检测 |
| 双格式输出 | ❌ | ✅ MD + HTML |
| 自动化 | 手动上传 | ✅ Cron + Watchdog |

## 进化行动（已执行）

### 已 patch 到 llm-wiki Skill v2.2.0

| 改进 | 描述 | 状态 |
|---|---|---|
| **两步 Ingest** | Analysis → Generation 拆分，先生成结构化分析再写页面 | ✅ P0 |
| **链接感知检索** | Query 时沿 Markdown 链接 2-hop 扩展，加权打分 | ✅ P0 |
| **知识缺口检测** | Ingest 后检测缺失关键实体，推入 Review Queue | ✅ P1 |
| **Review Queue** | `_review/queue.md` 自动汇总低置信度/矛盾/缺口 | ✅ P1 |
| **社区检测** | Lint 中 Label Propagation 发现知识集群和孤岛 | ✅ P2 |
| **purpose.md** | SCHEMA 模板增加 Purpose 段 | ✅ P2 |
| **架构层** | 新增 Layer 2.5 Review Queue + _archive 目录 | ✅ |

### 已 patch 到 knowledge-query Skill v1.1

| 改进 | 描述 | 状态 |
|---|---|---|
| **链接感知路由** | Wiki 查询时增加 link expansion 步骤 | ✅ |

## 关键学习

1. **两步 Ingest 是质量关键** — 先分析后生成比边读边写好得多
2. **链接结构是知识图谱** — Markdown 链接本身就是人工策展的知识图谱，查询时应利用
3. **知识缺口是增长机会** — 每次 ingest 后检查缺失内容，闭环补充
4. **审核队列防止知识腐化** — 低置信度内容不静默沉淀，显式推给人审核

## 引用

- Karpathy's LLM Wiki: https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f
- nashsu/llm_wiki: https://github.com/nashsu/llm_wiki
- 深度分析参考: https://yuv.ai/blog/agency-agents

## 相关笔记
- [Agent Skills才是关键抽象层](../2026-04-02-Agent Skills才是关键抽象层.md)
- [MiniMax Office Skills全家桶](../2026-04-02-MiniMax Office Skills全家桶.md)
- [OpenClaw-paper-review-skill](../2026-04-03-OpenClaw-paper-review-skill.md)
- [SelfImproving-Agent-CLI-infra](../2026-04-05-SelfImproving-Agent-CLI-infra.md)
- [SKILL-md-ai-agent-skills](../2026-04-09-SKILL-md-ai-agent-skills.md)
- [distill-skill-yupi](../2026-04-12-distill-skill-yupi.md)
- [歸藏PPT-Skill-电子杂志风网页演示](../2026-04-24-歸藏PPT-Skill-电子杂志风网页演示.md)
- [竞品吸收笔记-khazix-skills](../2026-04-29-竞品吸收笔记-khazix-skills.md)
- [SkillClaw-analysis](../2026-05-02-SkillClaw-analysis.md)
- [github-ai-trending-mattpocock-skills](../2026-05-05-github-ai-trending-mattpocock-skills.md)
- [lewislulu-html-ppt-skill-analysis](../2026-05-06-lewislulu-html-ppt-skill-analysis.md)
- [skill-building-invoice-automation](../2026-05-10-skill-building-invoice-automation.md)
- [softwarecopyright-skill-analysis](../2026-05-10-softwarecopyright-skill-analysis.md)
- [开源AI模型工具2025春季爆发](../2026-05-18-开源AI模型工具2025春季爆发.md)
- [f5-tts-voice-cloning-incremental](2026-05-18-f5-tts-voice-cloning-incremental.md)
- [skill-lifecycle-management-deep-dive](2026-05-18-skill-lifecycle-management-deep-dive.md)
- [autotts-analysis](2026-05-19-autotts-analysis.md)
- [tts-stt-pipeline-optimization-deep-dive](2026-05-19-tts-stt-pipeline-optimization-deep-dive.md)
- [f5-tts-zero-shot-voice-cloning-deep-dive-20260518](f5-tts-zero-shot-voice-cloning-deep-dive-20260518.md)
- [local-tts-stt-optimization-20260519](local-tts-stt-optimization-20260519.md)
- [OpenClaw核心机制Skills全解析](../orphan/2026-04-02-OpenClaw核心机制Skills全解析.md)
- [OpenClaw-Skills-handbook](../orphan/2026-04-07-OpenClaw-Skills-handbook.md)
- [CyberVerse公众号HTML模板分析](../orphan/2026-05-03-CyberVerse公众号HTML模板分析.md)
- [国自然申请书AI-Skill流水线](../orphan/2026-05-04-国自然申请书AI-Skill流水线.md)
- [数据血缘-lineage-工具全景](../orphan/2026-05-09-数据血缘-lineage-工具全景.md)
- [HTML的不合理有效性-Claude-Code-团队](../orphan/2026-05-16-HTML的不合理有效性-Claude-Code-团队.md)
- [20260512-10-skill-学术去ai味框架](../orphan/20260512-10-skill-学术去ai味框架.md)
- [build-ai-cli](../orphan/build-ai-cli.md)
- [frontend-slides-skill](../orphan/frontend-slides-skill.md)
- [hermes-skill-top10-2026w18](../orphan/hermes-skill-top10-2026w18.md)
- [skills-apple](../orphan/skills-apple.md)
- [skills-catalog](../orphan/skills-catalog.md)
- [skills-data-science](../orphan/skills-data-science.md)
- [skills-dogfood](../orphan/skills-dogfood.md)
- [skills-email](../orphan/skills-email.md)
- [skills-github](../orphan/skills-github.md)
- [skills-leisure](../orphan/skills-leisure.md)
- [skills-logo-generator-skill](../orphan/skills-logo-generator-skill.md)
- [skills-smart-home](../orphan/skills-smart-home.md)
- [skills-social-media](../orphan/skills-social-media.md)
- [skills-team-roles](../orphan/skills-team-roles.md)
- [skills-autonomous-ai-agents](../skills-autonomous-ai-agents.md)
- [skills-creative](../skills-creative.md)
- [skills-devops](../skills-devops.md)
- [skills-gaming](../skills-gaming.md)
- [skills-mcp](../skills-mcp.md)
- [skills-media](../skills-media.md)
- [skills-mlops](../skills-mlops.md)
- [skills-note-taking](../skills-note-taking.md)
- [skills-openclaw-imports](../skills-openclaw-imports.md)
- [skills-overview](../skills-overview.md)
- [skills-productivity](../skills-productivity.md)
- [skills-red-teaming](../skills-red-teaming.md)
- [skills-research](../skills-research.md)
- [skills-software-development](../skills-software-development.md)
- [Karpathy-LLM-Wiki-second-brain](../2026-04-05-Karpathy-LLM-Wiki-second-brain.md)
- [Hermes-LLM-Wiki-学习笔记](../2026-04-18-Hermes-LLM-Wiki-学习笔记.md)
- [LLM推理优化前沿技术2026](../2026-04-28-LLM推理优化前沿技术2026.md)
- [LLM-Agent驱动量化交易系统前沿学习](../2026-04-29-LLM-Agent驱动量化交易系统前沿学习.md)
- [边缘AI与On-Device-LLM前沿学习](../2026-04-30-边缘AI与On-Device-LLM前沿学习.md)
- [deepseek-agent-ecosystem](../2026-05-01-deepseek-agent-ecosystem.md)
- [LLM对齐训练范式RLHF-DPO-GRPO-DAPO](../2026-05-04-LLM对齐训练范式RLHF-DPO-GRPO-DAPO.md)
- [开源AI模型2025-DeepSeek-Qwen新格局](../2026-05-05-开源AI模型2025-DeepSeek-Qwen新格局.md)
- [PageIndex-无向量推理式RAG](../2026-05-07-PageIndex-无向量推理式RAG.md)
- [大模型量化技术全景-GGUF-GPTQ-AWQ-FP8-BitNet](../2026-05-07-大模型量化技术全景-GGUF-GPTQ-AWQ-FP8-BitNet.md)
- [推理加速深度解析-投机解码-KVCache-连续批处理](../2026-05-08-推理加速深度解析-投机解码-KVCache-连续批处理.md)
- [LLM知识蒸馏技术全景](../2026-05-09-LLM知识蒸馏技术全景.md)
- [DeepSeek-V4-开源模型新格局](../2026-05-10-DeepSeek-V4-开源模型新格局.md)
- [蒸馏量化联合策略-QAD-LBLLM-CapacityGap](../2026-05-10-蒸馏量化联合策略-QAD-LBLLM-CapacityGap.md)
- [5月AI模型大战-GPT55-DeepSeekV4](../2026-05-11-5月AI模型大战-GPT55-DeepSeekV4.md)
- [AI趋势2026-推理时计算与反思Agent](../2026-05-11-AI趋势2026-推理时计算与反思Agent.md)
- [LLM冲击下PINN应用变化与发展](../2026-05-11-LLM冲击下PINN应用变化与发展.md)
- [MoE蒸馏与压缩-专家路由迁移-稀疏结构处理](../2026-05-11-MoE蒸馏与压缩-专家路由迁移-稀疏结构处理.md)
- [JAX-NVIDIA-GPU-微调Llama3.1实战方案](../2026-05-15-JAX-NVIDIA-GPU-微调Llama3.1实战方案.md)
- [LoRA高效微调前沿技术全景](../2026-05-17-LoRA高效微调前沿技术全景.md)
- [SGLang高性能LLM推理框架深度分析](../2026-05-17-SGLang高性能LLM推理框架深度分析.md)
- [Agent元认知-LLM不确定性感知](../2026-05-18-Agent元认知-LLM不确定性感知.md)
- [MoE模型LoRA微调最佳实践](../2026-05-18-MoE模型LoRA微调最佳实践.md)
- [蒸馏量化RL三联流水线-后训练范式统一](../2026-05-19-蒸馏量化RL三联流水线-后训练范式统一.md)
- [Active-Data-Selection-LLM训练动态数据选择前沿](../2026-05-20-Active-Data-Selection-LLM训练动态数据选择前沿.md)
- [AutoSearch 自主训练任务](../AutoSearch 自主训练任务.md)
- [2025年5月AI大爆发-Claude4-Qwen3-DeepSeek-R1](2026-05-09-2025年5月AI大爆发-Claude4-Qwen3-DeepSeek-R1.md)
- [开源AI春季爆发-模型推理Agent](2026-05-09-开源AI春季爆发-模型推理Agent.md)
- [LLM推理优化-MoE量化加速全景](2026-05-16-LLM推理优化-MoE量化加速全景.md)
- [LLM推理优化技术](2026-05-16-LLM推理优化技术.md)
- [llm-inference-opt-incremental2](2026-05-18-llm-inference-opt-incremental2.md)
- [llm-inference-opt-update](2026-05-18-llm-inference-opt-update.md)
- [llm-self-prompt-optimization](2026-05-18-llm-self-prompt-optimization.md)
- [MoE-稀疏激活微调工程实践](2026-05-19-MoE-稀疏激活微调工程实践.md)
- [SGLang-vs-vLLM-推理引擎对比](2026-05-19-SGLang-vs-vLLM-推理引擎对比.md)
- [llm-inference-opt-2026-05-17](llm-inference-opt-2026-05-17.md)
- [llm-inference-opt-incremental-20260517](llm-inference-opt-incremental-20260517.md)
- [llm-pid-tuner](../llm-pid-tuner.md)
- [分布式训练技术全景-FSDP-DeepSpeed-Megatron](../orphan/2026-05-05-分布式训练技术全景-FSDP-DeepSpeed-Megatron.md)
- [表达清晰的5个训练](../orphan/2026-05-16-表达清晰的5个训练.md)
- [tinyedge-lora](../tinyedge-lora.md)
- [前瞻性问题-AI垂域LLM载具设计](../前瞻性问题-AI垂域LLM载具设计.md)
