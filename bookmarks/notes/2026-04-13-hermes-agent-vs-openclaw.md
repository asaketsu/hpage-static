# Hermes Agent vs OpenClaw：Agent框架的路径之争

> 来源：36氪/极客公园/澎湃新闻多篇综合 | 2026-04-13

## 一、技术分析

### Hermes Agent 核心架构

**Closed Learning Loop（闭环学习循环）**——任务完成后自动复盘三层：

1. **策划记忆**：判断什么值得记住，写入 SQLite + FTS5 全文索引。按需检索，不全量加载
2. **自主创建 Skill**：复杂任务后自动提炼为 `~/.hermes/skills/` 下的 Markdown 文件，下次直接加载不重新推理
3. **Skill 自改进**：用 patch 方式局部修改，不整体重写，保留已验证逻辑

**三层记忆架构**（对应认知科学）：
- 情景记忆（会话层）：SQLite + FTS5，按需召回
- 语义记忆（持久层）：MEMORY.md/USER.md，严格限制字符数，满了自动合并压缩
- 程序性记忆（技能层）：Markdown 技能文件，遵循 agentskills.io 开放标准

**关键设计**：有限记忆——刻意设上限，迫使 Agent 做信息筛选，少量精准记忆 > 大量模糊记忆。

**辅助模型机制**：高频侧任务（图像分析、网页提取、记忆整理）切给便宜模型（默认 Gemini Flash），主模型专注推理。

**其他特性**：Camoufox 隐身浏览器、子智能体并行、cron 调度、18+ LLM 提供商一行命令切换、原生微信支持。

### OpenClaw 架构（对比视角）

**Gateway 架构**：核心是连接和协调——统一管理会话、路由、渠道，汇聚入口后分发。优势是生态扩展快。

**记忆机制演进**：
- 早期：全量存储 + RAG 检索，token 消耗大、噪音随时间递增
- v2026.4.5 新增"梦境"系统：模拟睡眠记忆巩固，离线提纯高价值信息

**技能系统**：人类预设为主（ClawHub 社区），确定性高但不随用户使用自动进化。

## 二、特点分析

| 维度 | OpenClaw | Hermes Agent |
|------|----------|-------------|
| 设计哲学 | 确定性、广连接 | 进化式、深学习 |
| 核心架构 | Gateway 网关调度 | Closed Learning Loop |
| 技能来源 | 人工编写 + 社区共享 | 自动提炼 + 持续自改进 |
| 记忆策略 | 全量存 + 梦境提纯 | 有限记忆 + 强制筛选 |
| 模型绑定 | 多模型但倾向自家 | 一行命令切换，零锁定 |
| 生态成熟度 | 万级技能，庞大社区 | 早期，40+ 预置 Skill |
| 安全性 | Gateway 级权限控制 | 容器隔离 + 只读文件系统 |
| 适用场景 | 批量/金融/团队协作 | 探索性编程/创意/长期陪伴 |
| 上手门槛 | 低 | 高 |

**社区共识**：互补而非替代——OpenClaw 负责"干活"（多通道 + 工作流），Hermes 负责"动脑"（记忆 + 自进化）。

## 三、对我们的启发

### 1. 有限记忆理念值得借鉴

我们当前的 permanent/ 四文件 + MEMORY.md 架构虽然有三层分层，但缺少**主动压缩淘汰机制**。Hermes 的"记忆满了自动合并旧条目"设计可以引入——当 MEMORY.md 接近上限时，自动触发压缩合并。

### 2. Skill 自改进闭环

我们的 evolver + experience-bank 已经在做类似的事（错误→修复→经验→规则），但 Hermes 的 patch 式局部修改比整体重写更安全。可以在 skill-optimizer 中引入这个理念。

### 3. 辅助模型分层

我们目前所有任务走同一个模型。Hermes 的 Auxiliary Models 机制（侧任务切给便宜模型）在我们的 cron 任务中可以直接落地——天气预报、新闻推送等低推理任务用 GLM，复杂分析用主力模型。

### 4. agentskills.io 开放标准

Hermes 技能遵循 agentskills.io 标准，30+ 工具互通。我们的 SKILL.md 格式可以考虑兼容或对接这个标准，降低跨平台迁移成本。

### 5. 记忆的"关于你的模型"

Hermes 的 Honcho 用户建模不只记录说了什么，而是从行为模式推断偏好。我们的 permanent/user.md 目前是显式记录，可以增加行为推断层——从历史交互中自动归纳隐含偏好。

## 四、优化融合建议（可落地项）

| 优先级 | 建议 | 实现方式 |
|--------|------|----------|
| P0 | cron 任务按推理需求分模型 | 低推理任务指定 GLM，高推理任务用默认模型 |
| P1 | MEMORY.md 自动压缩机制 | 接近上限时触发合并脚本 |
| P1 | Skill patch 式更新 | skill-optimizer 改为局部修改而非重写 |
| P2 | 行为推断层 | 分析交互历史自动更新 user.md 隐含偏好 |
| P2 | agentskills.io 兼容 | SKILL.md 增加 agentskills.io 元数据字段 |
→ 相关：2026-04-05-Hermes-Agent-competitor-analysis.md（Hermes竞品原始分析）
→ 相关：2026-04-07-hermes-agent-deep-dive-evolution-roadmap.md（Hermes深度演进路线）


## 相关笔记
- [[hermes-agent-源码拆解自我进化机制]] (关键词: agent, hermes)
- [[2026-05-14-Small-Hermes-自我进化深度解析]] (关键词: agent, hermes)
- [[2026-04-07-hermes-agent-deep-dive-evolution-roadmap]] (关键词: agent, hermes)
- [[hermes-memory-system-guide]] (关键词: hermes)
- [[2026-04-18-Hermes-Agent-v0.10.0-insight]] (关键词: agent, hermes)
