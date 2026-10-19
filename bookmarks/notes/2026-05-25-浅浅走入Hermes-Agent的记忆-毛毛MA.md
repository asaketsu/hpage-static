# 浅浅走入Hermes Agent的记忆

> **来源**：毛毛MA · 微信公众号 · 2026-05-25
> **原文**：https://mp.weixin.qq.com/s/6YgQlb8RsiGORuLgHkQt8A
> **关联**：[[2026-05-22-Hermes-Agent四层记忆架构深度分析]] [[Hermes Agent]] [[memory-system]] [[session-search]]
> **格式**：双格式(MD + HTML) · 含借鉴进化点 · RAG/wiki联动

## 摘要

毛毛MA从用户视角浅入Hermes Agent的记忆体系，重点体验了三层记忆结构：Prompt Memory（系统提示词注入）、Session Search（SQLite+JSONL双存储会话检索）、fact_store（结构化事实存储）。文章特点是实践驱动——逐条尝试 `hermes sessions` 系列命令（list/export/delete/prune/stats/rename/browse），而非纯理论分析。对于Prompt Memory在本地模型下"不那么听话"的问题，作者留待后续研究。

## 核心内容

### 三层记忆结构

1. **Prompt Memory** — config.yaml 中配置，直接注入系统提示词。每次对话都在，但本地模型参数差异可能导致"不那么听话"
2. **Session Search** — 每次对话自动保存为Session（与模型无关），双存储结构：
   - SQLite: `~/.hermes/state.db`（FTS5全文索引，支持跨会话搜索）
   - JSONL: `~/.hermes/sessions/`（原始对话记录，含工具调用细节）
3. **fact_store** — 结构化存储和查询事实信息，支持复杂组合查询（文章未深入）

### Sessions CLI 命令实践

作者逐条尝试了所有 sessions 子命令：
- `hermes sessions list --source weixin` — 按平台查看会话列表
- `hermes sessions delete <session_id> -y` — 删除指定会话（作者实测删除+验证）
- `hermes sessions export` — 导出会话
- `hermes sessions prune` — 清理旧会话
- `hermes sessions stats` — 查看统计信息
- `hermes sessions rename` — 重命名会话
- `hermes sessions browse` — 交互式选择器

## 关键概念

- **FTS5**：SQLite 全文检索扩展，Hermes 用它实现跨会话关键词搜索
- **双存储**：SQLite（索引查询）+ JSONL（完整记录），兼顾检索效率和数据完整性
- **fact_store**：Hermes 内置工具，用于结构化事实的存储与组合查询

## 能力边界

文章是入门级体验笔记，不涉及：
- 外置记忆插件（Mem0/Honcho/Supermemory）
- Obsidian 知识库联动
- 记忆压缩/清理策略
- RAG 语义检索
- fact_store 的具体用法

## 最佳实践

- 用户应善用 `hermes sessions` CLI 管理会话历史
- `--source` 参数可按平台过滤（weixin/feishu等）
- 删除操作可用 `list` 验证确认

## 🔍 借鉴学习进化点

| # | 点 | 原文要点 | 对当前系统的借鉴 | 行动计划 |
|---|-----|---------|---------------|---------|
| 1 | 生态观察 | 毛毛MA是Hermes生态活跃内容创作者 | 关注其后续文章可能有fact_store等深度实践 | 已在记忆中记录 |
| 2 | Prompt Memory本地模型问题 | "实操发现本地模型参数不同，毛小马有时不那么听话" | 我们用zai/glm-5.1作为主模型，也可能遇到类似问题 | 已有memory-system skill处理，无需额外行动 |
| 3 | sessions browse | 交互式会话选择器 | 我用session_search（FTS5+窗口滚动），browse是CLI交互模式 | CLI场景有用，当前agent场景已覆盖 |
| 4 | fact_store未深入 | "以后再继续研究" | fact_store是内置工具，我当前用memory tool替代 | 暂无需改动，memory tool已满足需求 |

**三问自检结果**：
- ✅ 可复用方法/模式？无新增（sessions CLI已熟练使用）
- ✅ 可优化自身配置？无（已有memory-system skill覆盖）
- ✅ 关键事实？毛毛MA为Hermes生态观察对象

## 🔗 RAG / Wiki 联动

### 当前状态
- Session Search：✅ 已通过 session_search skill 全覆盖（FTS5发现+窗口滚动）
- fact_store：⚠️ 未深入探索（当前用memory tool替代）
- 外置记忆：❌ 未激活（provider为空）

### 改进方案
1. 关注毛毛MA后续fact_store深度文章
2. 与已有 [[2026-05-22-Hermes-Agent四层记忆架构深度分析]] 交叉参考

### 已执行操作
- ✅ 三问自检完成，无新增skill/memory改动
- ✅ 关联已有笔记建立双链

## 相关笔记
- [Agent Skills才是关键抽象层](2026-04-02-Agent Skills才是关键抽象层.md)
- [Claude-Code四层记忆架构](2026-04-03-Claude-Code四层记忆架构.md)
- [Claude-Code-324-prompts-analysis](2026-04-04-Claude-Code-324-prompts-analysis.md)
- [Hermes-Agent四层记忆架构深度分析](2026-05-22-Hermes-Agent四层记忆架构深度分析.md)
- [OpenClaw日常聊天黑化Agent-ULSPB安全研究](2026-05-22-OpenClaw日常聊天黑化Agent-ULSPB安全研究.md)
- [Domain-Camouflaged-Injection-Attacks-域伪装注入绕过多Agent检测](2026-05-23-Domain-Camouflaged-Injection-Attacks-域伪装注入绕过多Agent检测.md)
- [Microsoft取消ClaudeCode许可-AI编码战企业政治](2026-05-23-Microsoft取消ClaudeCode许可-AI编码战企业政治.md)
- [Superset-YC-P26-AI-Agent-IDE](2026-05-23-Superset-YC-P26-AI-Agent-IDE.md)
- [AI编码工具战争-CodexClaudeCodeCursor收敛为分层架构](2026-05-24-AI编码工具战争-CodexClaudeCodeCursor收敛为分层架构.md)
- [Cloudflare-Agents-Week-2026-Agentic-Cloud全栈基础设施](2026-05-24-Cloudflare-Agents-Week-2026-Agentic-Cloud全栈基础设施.md)
- [PiAgent深度分析](2026-05-24-PiAgent深度分析.md)
- [Claude-Code之父Boris-Cherny-编程已死千级Agent夜间打工](2026-05-25-Claude-Code之父Boris-Cherny-编程已死千级Agent夜间打工.md)
- [高德OPC自主增长系统-Harness多Agent架构](2026-05-25-高德OPC自主增长系统-Harness多Agent架构.md)
- [零信任安全2026-Agent系统新攻击面与安全基线-深度蒸馏](explore/2026-05-21-零信任安全2026-Agent系统新攻击面与安全基线-深度蒸馏.md)
- [GROW开放世界VLM-Agent强化学习框架](explore/2026-05-22-GROW开放世界VLM-Agent强化学习框架.md)
- [agent-evolution-rag](explore/2026-05-23-agent-evolution-rag.md)
- [Harness-工程-AI-编程智能体成功率从20%到100%](explore/2026-05-24-Harness-工程-AI-编程智能体成功率从20%到100%.md)
- [MOSS自主Agent源码级自进化](explore/2026-05-24-MOSS自主Agent源码级自进化.md)
