# AI Scientist v2（SakanaAI）— 阅读笔记

来源：GitHub — SakanaAI/AI-Scientist-v2
日期：2026-04-06
评分：⭐⭐⭐⭐⭐（5/5，里程碑级项目）

## 核心定位
全自主科学研究系统 v2。**首个完全由 AI 撰写并被同行评审接受的 workshop 论文**。

## v1 → v2 关键升级
| 维度 | v1 | v2 |
|---|---|---|
| 模板依赖 | 需要人类编写模板 | 去除模板，自主生成 |
| 领域泛化 | 单一领域 | 跨 ML 领域通用 |
| 搜索策略 | 线性执行 | **渐进式树搜索（Tree Search）** |
| 成功率 | 高（有模板兜底） | 较低（探索性更强） |
| 适用场景 | 目标明确的任务 | 开放式科学探索 |

## 架构核心：渐进式树搜索
- Experiment Manager Agent 引导搜索方向
- 多 worker 并行探索（num_workers 可配置，通常 3）
- 最大探索节点数 steps 可控（默认 21）
- 失败节点自动调试（max_debug_depth + debug_prob 概率控制）
- 多棵独立树并行生长（num_drafts）

## 工作流程
1. **Ideation** — 生成研究方向 JSON（人类可引导，也可全自动）
2. **Tree Search 实验** — 多路径并行实验，渐进式扩展
3. **结果分析** — 自动分析实验数据
4. **论文撰写** — 生成完整科学论文草稿
5. **自动评审** — AI 模拟同行评审

## 对我们的启发
1. **树搜索思维** — 复杂问题不应线性执行，多路径并行 + 渐进淘汰是更优策略
2. **失败恢复机制** — debug_prob 概率控制调试尝试，不是每条失败路径都死磕
3. **无模板泛化** — 去除硬编码模板，靠 agent 能力自主适应

→ 相关：2026-04-05-Hermes-Agent竞品分析.md（Agent 自主性对比）
→ 相关：2026-04-05-capability-evolver自我升级.md（进化管线对比）

→ 相关：2026-04-07-OpenClaw自主性与Harness循环机制.md
→ 相关：2026-04-07-OpenClaw摄像头RTSP本地视觉模型智能家居.md


## 相关笔记
- [[2026-05-03-ai-agent-resources-ecosystem]] (关键词: ai)
- [[2026-05-14-航空结构设计AI短期基础设施]] (关键词: ai)
- [[2026-04-09-SKILL-md-ai-agent-skills]] (关键词: ai)
- [[2026-04-13-rag-vs-mcp-architecture]] (关键词: ai)
- [[2026-04-30-Meta-Hyperagents自适应Agent框架]] (关键词: ai)
