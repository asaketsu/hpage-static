# DeepTutor（HKUDS）— 阅读笔记

来源：GitHub — HKUDS/DeepTutor
日期：2026-04-06
评分：⭐⭐⭐⭐（4/5，架构参考价值高）

## 核心定位
港大数据科学实验室出品的 Agent-Native 个性化学习助手。两层插件模型（Tools + Capabilities），多 channel bot，持久记忆，主动心跳。

## 核心特性
- **Soul System** — 每个 bot 有独立"灵魂"（人格 prompt），塑造回复风格
- **独立工作空间** — 每个 bot 有独立目录（memory/sessions/skills/config），完全隔离
- **主动心跳** — Heartbeat 系统支持定期学习打卡、复习提醒、定时任务
- **全工具访问** — RAG 检索、代码执行、网页搜索、论文搜索、深度推理、头脑风暴
- **技能学习** — 通过 skill 文件扩展 bot 能力（类似我们的 ClawHub skill）
- **Co-Writer** — 协作写作模式
- **Guided Learning** — 引导式学习路径
- **多 LLM 支持** — v0.4.0 起支持多 provider
- **持久会话** — v0.6.0 session 持久化 + 增量文档上传 + 全中文本地化

## 与我们的相似度
极高。DeepTutor 几乎是我们的"教育版镜像"：
| 维度 | DeepTutor | 我们 |
|---|---|---|
| 心跳 | Proactive Heartbeat | HEARTBEAT.md ✅ |
| 记忆 | Persistent Memory | 六分类 + WAL ✅ |
| 技能 | Skill System | ClawHub Skills ✅ |
| 独立工作空间 | Per-bot Workspace | Per-agent ✅ |
| 人格 | Soul System | SOUL.md ✅ |
| 多渠道 | TutorBot multi-channel | 飞书 ✅ |
| RAG | 内置 | rag-quick-search ✅ |
| 团队协作 | ❌ 无 | 5 agent ✅ 差异化优势 |
| 进化引擎 | ❌ 无 | evolver ✅ 差异化优势 |

## 启发
1. **Soul System 概念** — "灵魂塑造每个回复"，比我们的 SOUL.md 更有仪式感，但实质相同
2. **Heartbeat 的教育应用** — 定期学习提醒、复习打卡，是心跳机制的经典场景
3. **引导式学习（Guided Learning）** — 渐进式知识引导，可借鉴到嗅探系统的知识探索流程

→ 相关：2026-04-05-Hermes-Agent竞品分析.md（Agent 架构对比）
→ 相关：2026-04-06-AI-Scientist-v2.md（AI 自主研究系统对比）


## 相关笔记
- [阅读笔记：你的能量频率有多高？出现这7个特征，已超越99%的人](2026-03-30-荣格个体化七特征.md)
- [张雪峰生前力荐的 6 个计算机专业 - 阅读笔记](2026-03-31-张雪峰推荐的6个计算机专业.md)
- [AI Scientist v2（SakanaAI）— 阅读笔记](2026-04-06-AI-Scientist-v2.md)
