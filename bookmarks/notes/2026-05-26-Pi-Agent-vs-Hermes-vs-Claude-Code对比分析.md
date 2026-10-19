# Pi Agent vs Hermes vs Claude Code 对比分析

> 2026-05-26 | 基于公开信息 + Hermes 现状梳理

## 核心数据对比

- **Pi Agent**：系统提示词 <1500 字，本地 Agent，串联多 skill，Token 消耗仅为 Claude Code 的 1/3，响应速度快
- **Claude Code**：系统提示词 ~20,000 字，云端 Claude + 本地工具，Skills 模块，Token 消耗基准
- **Hermes**：系统提示词 ~3,000+ 字（含 skill 注入），本地 Agent + 多平台 + 多模型，100+ skills

## 架构差异

| 维度 | Pi Agent | Claude Code | Hermes |
|------|----------|-------------|--------|
| 系统提示词 | <1,500 字 | ~20,000 字 | ~3,000+ 字（含 skill 注入） |
| 定位 | 本地 Agent，串联多 skill | 云端 Claude + 本地工具 | 本地 Agent + 多平台 + 多模型 |
| Token 消耗 | Claude Code 的 1/3 | 基准 | 取决于模型选择 |
| 响应速度 | 快（短提示词 + 本地） | 慢（长提示词 + 云端） | 取决于模型 |
| Skill 系统 | 多 skill 串联 | Skills 模块 | 100+ skills |
| 并发限制 | 本地模型无限制 | 受 API 配额限制 | 取决于模型 provider |
| 多平台支持 | 有限 | 无 | 飞书/Telegram/Discord/微信等 |
| 模型灵活性 | 单模型 | Claude 系列 | 多 provider 多模型切换 |

## Pi Agent 的核心设计理念

1. **极简提示词**：<1500 字的系统提示词，远低于 Claude Code 的 2 万字，降低 token 开销
2. **Skill 串联模式**：通过多个小 skill 串联完成任务，而非单一巨型提示词
3. **本地优先**：强调本地模型运行，避免云端延迟和 API 限制
4. **Token 效率**：通过提示词压缩实现 Claude Code 1/3 的 token 消耗

## 对 Hermes 的启示

### 可借鉴
- **提示词瘦身**：Hermes 的 skill 注入机制已是按需加载，但核心提示词仍有优化空间
- **Skill 粒度**：Pi Agent 的细粒度 skill 串联思路与 Hermes 的 100+ skill 体系方向一致
- **本地模型利用**：Hermes 已有 nexa-local-inference（Ollama on Jetson），可作为 fallback 降低 API 依赖

### Hermes 的差异化优势
- **多平台网关**：飞书/Telegram/Discord/微信全覆盖，Pi Agent 和 Claude Code 均不具备
- **多模型切换**：provider 路由 + failover 链，不受单一模型绑定
- **Cron 调度**：内置定时任务系统，支持自主巡检和自动化工作流
- **记忆系统**：L1/L2/L3 三级记忆 + session 搜索，跨会话连续性

## 结论

Pi Agent 的核心价值在于证明了**极简提示词 + skill 串联**可以在大幅降低 token 成本的同时保持 Agent 能力。这对 Hermes 的启示是：继续坚持 skill 按需加载策略，避免 Claude Code 式的提示词膨胀。Hermes 的多平台/多模型/Cron 三大差异化能力是 Pi Agent 短期内无法复制的护城河。

## 相关笔记
- [[2026-05-24-PiAgent深度分析|Pi Agent 深度分析]]
- [[2026-04-03-Claude-Code四层记忆架构|Claude Code 记忆架构]]
- [[2026-04-04-Claude-Code-324-prompts-analysis|Claude Code 提示词分析]]
- [[2026-04-02-Agent Skills才是关键抽象层|Agent Skills 抽象层]]
- [[2026-04-05-Hermes-Agent-competitor-analysis|Hermes 竞品分析]]
- [[2026-04-08-claude-code-tool-execution-orchestration|Claude Code 工具执行]]
- [[skills-autonomous-ai-agents|自主 Agent 技能]]

