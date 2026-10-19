# Cloudflare Flagship：Feature Flag 服务正式发布

> **来源**：Cloudflare 官方文档 · HN #7, 203 pts, 100 comments · 2026-05-27
> **原文**：https://developers.cloudflare.com/flagship/
> **笔记ID**：sniff-20260527-cloudflare-flagship
> **格式**：双格式(MD + HTML) · 含借鉴进化点 · RAG/wiki联动

## 摘要

Cloudflare 正式发布 Flagship — 基于 Workers 的 Feature Flag 服务。核心特性：原生 Workers 绑定、OpenFeature CNCF 标准兼容、11 种比较运算符的目标规则、百分比灰度发布、多类型变量（bool/string/number/JSON 对象）。定位为 Agentic Cloud 基础设施的一部分，与之前的 Agents Week 产品线（Sandbox、Artifacts、Agent Readiness Score）形成完整生态。对 Hermes 系统的启发：Feature Flag 是多模型、多 Skill 编排的关键基础设施。

## 核心内容

### 产品架构

Flagship 的技术栈：

1. **Workers Binding** — 原生绑定，类型安全，自动回退默认值
2. **OpenFeature SDK** — CNCF 开放标准，一套代码切换 Feature Flag 供应商
3. **Targeting Rules** — 11 种比较运算符，逻辑 AND/OR 分组，顺序评估
4. **Percentage Rollouts** — 一致性哈希确保同一用户始终获得相同 flag 值
5. **Multi-type Variations** — bool/string/number/JSON 对象，单 flag 交付整个配置块

### Agentic Cloud 生态定位

Flagship 是 Cloudflare "Agentic Cloud" 战略的一部分：

- Agents Week 2026 已发布：Sandbox GA、Artifacts、Agent Readiness Score
- Flagship 补充了"功能开关"层 — Agent 行为可动态控制
- llms.txt / llms-full.txt 支持 — 直接面向 AI Agent 提供文档

### OpenFeature 标准的意义

OpenFeature 是 CNCF 沙箱项目，定义了 Feature Flag 的标准化接口：
- 供应商无关：从 LaunchDarkly/Unleash 迁移只需改一行配置
- 统一评估 API：`@cloudflare/flagship` SDK 可用于 Workers、Node.js、浏览器
- 未来可能成为 Feature Flag 的 "SQL" 级别标准

## 对比/框架

| 维度 | Cloudflare Flagship | LaunchDarkly | Unleash (开源) |
|------|-------------------|--------------|--------------|
| 部署模式 | Cloudflare Workers（边缘） | SaaS | 自托管/SaaS |
| 延迟 | <5ms（边缘） | ~50ms | ~20ms（本地） |
| 定价 | Workers 计费内 | $10/seat起 | 免费开源 |
| OpenFeature | 原生支持 | 支持 | 支持 |
| 目标规则 | 11种运算符 | 更丰富 | 基础 |
| JSON Flag | 支持 | 支持 | 有限 |

## 关键概念

- **Feature Flag**：不重新部署代码即可控制功能可见性的机制
- **OpenFeature**：CNCF 沙箱项目，Feature Flag 的供应商中立 API 标准
- **Percentage Rollout**：按百分比分批发布功能，一致性哈希保证用户稳定
- **Workers Binding**：Cloudflare Workers 原生集成，无需 HTTP 调用直接读取 flag
- **Targeting Rules**：基于用户属性的条件规则，支持逻辑组合

## 能力边界

- 目前仅限 Cloudflare Workers 生态
- 目标规则比 LaunchDarkly 简单（11 种 vs 数十种）
- 没有实验/AB 测试功能（纯功能开关）
- Dashboard 管理为主，API/CLI 支持有限
- 依赖 KV 存储，超大规模可能有延迟

## 最佳实践

1. 使用 JSON 对象类型的 flag 交付整个配置块，而非多个 bool flag
2. 设置合理的默认值（flag 不可用时自动回退）
3. 利用 Targeting Rules 做精准的灰度发布（按地区/用户属性）
4. OpenFeature SDK 保证供应商独立性 — 不要直接用 Cloudflare 私有 API

## 🔍 借鉴学习进化点（必填）

| # | 点 | 原文要点 | 对当前系统的借鉴 | 行动计划 |
|---|-----|---------|---------------|---------|
| 1 | Feature Flag 模式 | 不重新部署即可控制功能可见性 | Hermes 多模型/Skill 编排可用 flag 控制 A/B 测试 | 设计 hermes-feature-flag 配置层，控制 Skill 启用/禁用 |
| 2 | JSON 对象 Flag | 单 flag 交付整个配置块 | 模型配置（provider/model/params）可打包为 JSON flag | 将 model-adapter 的配置改为 flag 式管理 |
| 3 | 百分比灰度发布 | 一致性哈希保证用户稳定体验 | 新 Skill 上线时可灰度 10%→50%→100% | 在 skill-auto-inject 中添加灰度发布逻辑 |
| 4 | OpenFeature 标准 | CNCF 供应商中立 API | Hermes 的配置接口应保持供应商无关 | 审查 config.yaml 的 provider 配置是否可抽象化 |
| 5 | llms.txt 文档模式 | 为 AI Agent 提供专用文档索引 | Hermes Skills 的文档也应提供结构化索引 | 检查 batch-skill-doc-generator 是否已支持 |

## 🔗 RAG / Wiki 联动

### 当前状态
- Cloudflare 笔记已有：`2026-05-24-Cloudflare-Agents-Week-2026-Agentic-Cloud全栈基础设施`
- Agent 基础设施相关：多个笔记

### 改进方案
1. 与 Cloudflare Agents Week 笔记交叉引用
2. Feature Flag 模式加入 Hermes 系统设计知识库

### 已执行操作
- ✅ 笔记已创建
- ⏳ 待更新 topics-index.json

## 相关笔记
- [[2026-05-24-Cloudflare-Agents-Week-2026-Agentic-Cloud全栈基础设施]] (关键词: cloudflare, feature)
- [[2026-05-24-AI编码工具战争-CodexClaudeCodeCursor收敛为分层架构]] (关键词: feature, config)
- [[2026-04-12-cloudflare-email-routing]] (关键词: cloudflare)

## 关联

- [Cloudflare Agents Week 2026](2026-05-24-Cloudflare-Agents-Week-2026-Agentic-Cloud全栈基础设施.md)
- [AI 编码工具战争](2026-05-24-AI编码工具战争-CodexClaudeCodeCursor收敛为分层架构.md)
- [Superset YC P26](2026-05-23-Superset-YC-P26-AI-Agent-IDE.md)
