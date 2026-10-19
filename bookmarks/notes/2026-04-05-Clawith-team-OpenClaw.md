# 团队版 OpenClaw 开源：Clawith 多智能体协作平台

来源：逛逛 GitHub（微信公众号）
链接：https://mp.weixin.qq.com/s/R195ylqcqM6BNW5OJZ-Stg
日期：2026-04-05
评分：⭐⭐⭐（3/5）
仓库：github.com/dataelement/Clawith

## 核心内容
Clawith 是一个开源的多 OpenClaw 协作平台（Multi-OpenClaw Collaboration Platform），为每个 Agent 提供持久身份、长期记忆、独立工作区。两大创新：

1. **Aware 持续感知** — 替代 Heartbeat 的闹钟模式。作者认为"30分钟跳一次不叫心跳，叫闹钟"。Aware 让 Agent 实时感知环境变化，有变化立刻响应，而非定时轮询
2. **Relationship 关系图谱** — Agent 之间的组织关系网络。每个数字员工有人格设定、技能配置、权限配置，能发动态、分享发现、评论（"广场"=公司朋友圈）

**其他特性**：运行时发现安装新工具（Smithery + ModelScope）、可迁移 agency-agents 开源项目的虚拟公司 AI 角色、Docker/脚本两种部署方式。

## 对我们有什么提升

1. **持续感知 vs 心跳** — 我们的 HEARTBEAT.md 机制确实是闹钟式（每天4次固定时间），中间有大量空白期。Clawith 的 Aware 思路有价值，但 OpenClaw 架构限制下无法实现真正的持续感知。可改进方向：将部分关键监控缩短间隔（如团队状态从每天4次→每2小时），或用 cron `--every` 实现更短周期

2. **关系图谱** — 我们的 AGENTS.md 定义了团队角色和协作流程，但是静态文档。Clawith 的 Relationship 是动态的。我们可以借鉴：在 SESSION-STATE.md 中维护团队实时状态（谁在线、正在做什么、上次活跃时间），每次心跳更新

3. **广场/动态** — Agent 间公开分享发现和进展。我们目前通过 sessions_send 点对点通信，没有广播机制。可以借鉴：每日晨报中增加"Agent 动态"板块，各成员主动上报发现

## 如何实施

1. **缩短关键监控间隔**：团队心跳从 `02,06,10,14,18,22`（每4h）改为 `*/2`（每2h），模型用 glm-5.1 lightContext 控制成本
2. **SESSION-STATE.md 团队状态区**：增加 `## 🤖 团队实时状态` 分区，心跳时自动更新各 agent 在线状态和当前任务
3. **晨报增加 Agent 动态**：在每日 08:00 心跳回复中，各活跃 agent 增加一句"今日发现/进展"字段

> ⚠️ 注意：文章质量一般（~60%废话，公众号引流风格），Clawith 项目实际成熟度未知，不建议盲目切换。核心价值在思路启发。
→ 相关：2026-04-05-Karpathy-LLM-Wiki第二大脑.md（知识编译+月度编译cron）
→ 相关：2026-04-05-Hermes-Agent竞品分析.md（闭环学习/skill自动创建竞品对标）

→ 相关：2026-04-07-OpenClaw自主性与Harness循环机制.md

→ 相关：2026-04-07-OpenClaw-Skills完整使用手册.md
→ 相关：2026-04-07-邮件不是复兴了是Agent终于开始需要它了.md
→ 相关：claude-code-tool-execution-orchestration

→ 相关：2026-04-09-SKILL.md模式-AI智能体技能.md


## 相关笔记
- [[2026-04-04-OpenClaw-4.2-stable-backend]] (关键词: openclaw)
- [[2026-04-03-OpenClaw最佳实践15条精华版]] (关键词: openclaw)
- [[2026-04-10-OpenClaw-4-things-persistent-tasks]] (关键词: openclaw)
- [[2026-04-04-OpenClaw 为什么越用越好用？本质就是一堆 md 文件]] (关键词: openclaw)
- [[2026-04-07-OpenClaw-autonomy-harness-loop]] (关键词: openclaw)
