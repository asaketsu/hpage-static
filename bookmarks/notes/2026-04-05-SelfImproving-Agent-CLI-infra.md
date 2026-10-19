# Self-Improving Agent + CLI 成为 AI 能力基础设施

来源：微信公众号（同一系列 capability-evolver 下一篇）
链接：https://mp.weixin.qq.com/s/2HC9mNCtnVu-tUvglOl9tw
日期：2026-04-05
评分：⭐⭐⭐⭐（4/5）

## 核心内容（两部分）

### Part 1: Self-Improving Agent
ClawHub #4 技能（15,962 下载，⭐132 星标全平台第一），与 capability-evolver 形成互补。

**三分类学习文件**（`.learnings/` 目录）：
- `LEARNINGS.md` — 纠正、知识缺口、最佳实践
- `ERRORS.md` — 命令失败、工具异常、API 故障
- `FEATURE_REQUESTS.md` — 用户提出但当前不具备的能力

**核心机制**：出问题时记入 `.learnings/`，成熟后提升到 AGENTS.md / TOOLS.md / SOUL.md / MEMORY.md。"错题本 + 复盘库 + 经验升级器"。

### Part 2: CLI 作为 AI 能力分发基础设施
**核心论点**：一个 CLI = 执行能力 + 通信协议 + 使用说明 = 完整的 AI 插件。跨平台、免审核、人和 AI 都能用。

**5 维 Agent 兼容度评分**：为 AI 设计 / 结构化输出 / 支持自查 / 支持预览 / 上下文大小控制

**当前缺口**：发现机制空白（AI 工具 App Store 不存在）、认证碎片化（每个服务一套登录）、安装体验差（npm/brew 假设使用者是开发者）

**关键设计原则**：
- field masks 控制 API 返回大小，避免 JSON 淹没有用信息
- "让 AI 管理自己的工具"而非用软件帮用户管理 AI 的工具
- AI 读 `--help` 自动生成工具描述

## 与我们系统的对比

| 维度 | Self-Improving Agent | 我们的 evolver + memory |
|------|---------------------|------------------------|
| 学习文件 | `.learnings/` 3文件 | `permanent/feedback.md` + `rules/` + `evolution-log.md` |
| 触发 | 被动（出错时记录） | 主动（cron 扫描 + 即时触发） |
| 升级路径 | learnings → AGENTS/TOOLS/SOUL/MEMORY | feedback → rules/ → SOUL.md |
| 覆盖范围 | 错误+纠正+需求 | 错误+偏好+项目+资源（更广） |
| CLI 管理 | AI 自管理工具安装 | 手动 + clawhub |

## 对我有什么提升 + 如何实施

1. **`.learnings/` 三文件分类 → 补充我们的 feedback.md**：我们用 feedback.md 统一记录所有反馈，不如拆分清晰。可在 `permanent/` 下增加 `errors.md`（命令失败/API 异常）和 `requests.md`（用户能力需求），与 feedback.md（纠正/偏好）互补
   → 创建 `permanent/errors.md` 和 `permanent/requests.md`，更新记忆 cron 路由规则

2. **"让 AI 管理自己的工具"理念 → 工具自检 cron**：定期让 AI 检查已安装 CLI 工具的状态（版本/健康/更新），而非等出问题才修。可以挂到夜梦 cron 的健康检查中
   → 夜梦 cron prompt 增加"检查关键 CLI 工具状态"步骤

3. **field masks 思路 → API 调用优化**：我们的 tavily_search、sessions_list 等调用经常返回大量无关数据。在 prompt 中明确指定需要的字段，减少上下文噪音
   → 在 rules/team.md 中增加"API 调用只请求必要字段"规则
→ 相关：2026-04-05-Karpathy-LLM-Wiki第二大脑.md（知识编译+月度编译cron）


## 相关笔记
- [[2026-04-23-深入源码-Hermes-Agent-如何实现Self-Improving]] (关键词: agent, improving, self)
- [[2026-05-03-ai-agent-resources-ecosystem]] (关键词: agent, ai)
- [[2026-05-09-OfficeCLI-AI-Agent的Office工具]] (关键词: agent, ai, cli)
- [[2026-05-05-github-ai-trending-mattpocock-skills]] (关键词: agent, ai, self)
- [[2026-05-08-AI-Agent控制流]] (关键词: agent, ai)
