# Tool Permission Graph：AI Agent 工具调用权限图

> 类型: auto-explore | 日期: 2026-06-16
> 来源: arxiv 2512.11147 (MiniScope), Scalekit Blog, BVP Atlas

## 摘要

Tool Permission Graph 是 2025-2026 年兴起的 AI Agent 安全核心概念：用图结构建模 Agent 可调用的工具及其权限关系，自动推导最小权限边界，防止过授权 Agent 被注入后造成灾难性破坏。代表工作 MiniScope（UC Berkeley / IBM Research）通过重建"权限层级图"实现自动最小权限执行，仅 1-6% 延迟开销。

## 关键发现

### 1. 核心问题：授权时间 vs 意图时间的结构性鸿沟

OAuth Authorization Code Flow 假设人类在授权时就知道自己需要什么。但 Agent 在推理时（inference time）才决定执行哪个动作，授权往往在数天甚至数周前就已完成。这导致：
- Agent 拿到的 scope 永远比单个任务实际需要的大
- LLM 没有"可逆/不可逆"的原生理解，会把每个可用 scope 都用一遍
- "过度授权不是配置错误，而是每个不主动约束 scope 的 Agent 框架的默认输出"

### 2. MiniScope：权限层级图重建（arxiv 2512.11147）

- 提出方法：重建反映工具调用间关系的"权限层级"（permission hierarchy），本质就是 Permission Graph
- 结合移动端权限模型（mobile-style permission model）平衡安全性和易用性
- 不依赖手工编写策略，也不把 LLM 放在 confinement loop 中
- 评估：基于 10 个真实应用构建合成数据集，延迟仅 1-6%，权限最小化显著优于 LLM baseline

### 3. Scope-Action Map：工程落地的正确工件

Scalekit 提出的核心设计工件——每个工具的版本化声明，记录每个 agent action 实际需要的最小 OAuth scope：

- 独立于 agent 代码维护（agent 代码可被模型替换、可被 prompt 注入，不可审计）
- 强制执行放在 connector 层，不在 agent 代码层
- Token 物化时机是关键架构决策：grant-time / invocation-time / call-time 三种方案有不同的爆炸半径
- 正确模式：call-time 物化——每次工具调用时注入最小权限凭证

### 4. BVP 三阶段安全框架

- Stage 1 Visibility：清点所有 Agent 及其工具、权限
- Stage 2 Configuration：攻击前缩小爆炸半径（最小权限、scope-action map）
- Stage 3 Runtime Protection：机器速度检测和响应

### 5. 行业现状（2026 数据）

- 仅 21.9% 的工程团队将 AI Agent 视为独立的、有身份的实体并赋予 scoped credentials
- 45.6% 仍依赖共享 API Key 进行 agent 间认证
- 27.2% 使用自定义硬编码授权逻辑
- 48% 安全从业者认为 Agent AI 是最危险的攻击面

## 对工作的价值

直接适用于 Hermes Agent 的安全治理：
- Hermes 有大量 Skills/Cron/MCP 工具，每个都有不同权限级别
- 当前权限模型是"确认/禁止/允许"三层，缺乏**图级别的权限关系建模**
- 可借鉴 scope-action map 模式：为每个 Skill 声明最小所需的工具权限集，运行时动态注入
- 对 MCP Server 集成尤其重要——每个 MCP Server 自带大量工具，过授权风险极高

## 行动建议

1. 评估当前 Hermes Skill 的权限粒度——是否存在"一次性授予大权限"的问题
2. 为高风险 Skills（文件操作、外部 API、生产部署）引入 scope-action map 式声明
3. 研究 MiniScope 的 permission hierarchy 重建方法，看是否可用于 Hermes 的 Skill 权限自动最小化
4. 对 MCP Server 工具做权限审计——当前是全量暴露还是有选择性注册
5. 考虑在 Skill frontmatter 中增加 `required_permissions` 字段，connector 层强制校验

## 相关笔记
- [CSA Agentic Trusted](2026-06-16-网络安全:-CSA-Agentic-Tr.md) (关键词: 网络安全, Agent, 权限)
- [Security Automation](2026-05-23-网络安全-security-autom.md) (关键词: 网络安全, 安全自动化)
- [2025全球网络安全威胁](2026-05-09-2025全球网络安全威胁-AI双刃剑.md) (关键词: 网络安全, AI安全)
