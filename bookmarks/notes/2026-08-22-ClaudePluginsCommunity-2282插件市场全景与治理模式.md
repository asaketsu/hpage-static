# Claude Plugins Community — 2282 个插件的官方市场：生态全景与治理模式

> **来源**：[anthropics/claude-plugins-community](https://github.com/anthropics/claude-plugins-community)（GitHub，355 Star / 92 Fork / 2,282 commits，Apache-2.0）
> **数据**：`.claude-plugin/marketplace.json`（2026-08-22 拉取，2,282 个插件全量）
> **记录日期**：2026-08-22
> **关联仓库**：[claude-plugins-official](https://github.com/anthropics/claude-plugins-official)（官方维护）· [knowledge-work-plugins](https://github.com/anthropics/knowledge-work-plugins)（角色级）

**标签**：#ClaudePlugins #插件市场 #Agent生态 #Skills经济 #市场治理

---

### 7 模块索引（本报告内容映射）

| 模块 | 对应章节 | 说明 |
|------|---------|------|
| tag 标签 | 头部标签行 | 6 个标签 |
| 出处 | 头部出处行 | GitHub + marketplace.json 实测数据 |
| 内容整理 | 第一~三章 | 市场机制/插件全景/分类统计 |
| 查询拓展 | 第四章 | 三仓库分层 + 与 Skill 生态对照 |
| 归纳总结 | 第五章 | 生态地图 + 治理模式 |
| 趋势判断 | 第六章 | 3 条预测 |
| 关联分析 | 第七章 | 与本机 skill 生态 + 近期笔记交叉 |
| 拓展应用推荐 | 第八章 | 高相关插件深挖清单 |
| 指南分析 | 第九章 | 治理模式评估 |

---

## 一句话总纲

> **Anthropic 用"只读镜像 + 内部审核管线"的模式治理社区插件市场：2,282 个插件每夜同步、全部经自动化安全扫描与人工审批——Agent 插件经济的 App Store 时刻，但其治理哲学（PR 自动关闭/单向流）比 Apple 更中心化。**

---

## 一、内容详细整理

### 1.1 这个仓库是什么

**社区插件市场的只读镜像**：

- `.claude-plugin/marketplace.json` = 可安装社区插件的完整清单
- **每夜从 Anthropic 内部审核管线同步**
- 每个插件：经 claude.ai 提交 → 通过自动化安全扫描 → 人工审批分发

**治理铁律**：

> 直接对本仓库开的 PR 会被自动关闭——所有变更只能从内部审核管线流入。

### 1.2 安装方式

| 产品 | 入口 |
|------|------|
| Claude Cowork | claude.com/plugins |
| Claude Code | `/plugin` 命令安装（marketplace 机制） |

### 1.3 插件全景（marketplace.json 实测统计）

**总量：2,282 个插件**

**来源类型**：

| 类型 | 数量 | 说明 |
|------|------|------|
| url（git 仓库直连） | 1,876 | 插件源码在独立 GitHub 仓库 |
| git-subdir | 401 | 从大仓库的子目录引用 |
| 直连 | 5 | 少数特例 |

**分类统计**（按 description 关键词，非官方分类）：

| 类别 | 数量 | 占比 | 典型 |
|------|------|------|------|
| 测试/QA | 424 | 19% | a11y-fixer、ab-testing、Meticulous 视觉回归 |
| 文档/Spec | 284 | 12% | adr-creator、PRD 生成、图表 |
| 工作流/编排 | 218 | 10% | agent-handoff、multi-agent debate、pipeline |
| Agent 记忆 | 156 | 7% | agent-recall、agent-knowledge、agent-memory |
| 代码评审 | 148 | 6% | adversarial-review、security scan |
| DevOps/部署 | 49 | 2% | CI/CD、K8s、Terraform |
| 垂直领域 | 29 | 1% | SAP 四件套、Salesforce、Shopify |
| 其他 | 974 | 43% | 长尾（营销/设计/数据/个人效率…） |

### 1.4 插件条目结构（标准 schema）

```json
{
  "name": "adaptive-agent",
  "description": "Make your AI agent get stronger with use...",
  "source": {
    "source": "url",
    "url": "https://github.com/truenorth-lj/adaptive-agent-skill.git",
    "sha": "0167bbb..."   // 锁定 commit
  },
  "homepage": "https://github.com/..."
}
```

**关键设计**：source 锁定 sha——插件市场引用的是**固定版本**而非浮动分支，保证可复现与安全审计。

### 1.5 与本机生态高相关的插件（实测筛选）

**记忆/进化类**（与本机 TieredMemory/evolver 同构）：

| 插件 | 描述 | 对应本机 |
|------|------|----------|
| `adaptive-agent` | 越用越强：/skill-review 周期审计 + /build-user-profile | skill-review + memory |
| `agent-recall` | SQLite 知识图谱 + scoped 实体 + LLM 摘要简报 | TieredMemory + memorygraph |
| `agent-knowledge` | git 同步 Markdown 知识库 + 混合检索 + 11 种边类型图谱 + 置信度衰减 | knowledge-graph + RAG |
| `agent-memory` | 工具输出压缩 60-90% token + memory bus 跨 agent 共享 | context-compressor |

**对抗评审类**（与 skill-stress-test/EnvHarness 借鉴同构）：

| 插件 | 描述 | 对应本机 |
|------|------|----------|
| `adversarial-review` | Claude 出方案 + Codex 批判的对抗收敛循环 | 执行/评判分离 |
| `adversarial-spec` | 多模型辩论迭代精化 spec 直到共识 | EnvHarness 借鉴的对抗验证 |
| `agent-runway` | 注入项目架构上下文防 subagent 技术债 | AGENTS.md 上下文一次性 |

**运维类**：

- `agent-advisor`：subagent 状态实时仪表盘（对应本机 observability-dashboard）
- `agent-comm`：跨 AI 编码 agent 通信（对应 exchange-protocol 三机经验交换）
- `agent-ping`：Claude 完成/提问时播放提示音

---

## 二、查询拓展

### 2.1 Anthropic 插件三仓库分层

| 仓库 | 定位 | 治理 |
|------|------|------|
| **claude-plugins-official** | Anthropic 官方维护 | 官方开发 |
| **knowledge-work-plugins** | 角色级知识工作插件 | 官方+精选 |
| **claude-plugins-community**（本仓库） | 社区贡献 | 提交→自动安全扫描→人工审批→每夜同步 |

三层结构 = 官方核心 / 精选垂直 / 社区长尾——与 npm 的 official/scoped/community 或 VS Code 的 verified/publisher/community 分层同构。

### 2.2 Plugin vs Skill 的关系

插件是 Skill 的**打包分发单位**（可含多个 skills/commands/hooks/MCP servers/agents）。从 marketplace 数据看：

- 插件 ≈ npm 包（marketplace.json 锁 sha）
- Skill ≈ 包内的模块（渐进式加载的最小单元）
- 一个插件可携带多个 skill（如 adaptive-agent 含 /skill-review 和 /build-user-profile 两个 skill）

**与本机对照**：Hermes 的 skill 是裸目录（400+），无打包/版本/分发层——这是生态位差异。

### 2.3 审核管线的治理意义

提交 → 自动安全扫描 → 人工审批 → 锁 sha 分发 → 每夜同步：

- **安全扫描**：针对恶意 skill（提示注入/凭证窃取/数据外传）——Miles 文章的"第三方 Skill 按软件包审查"由平台层承担
- **锁 sha**：防止"审核后改代码"的供应链攻击
- **PR 自动关闭**：社区不可直接改清单——中心化治理换安全性，牺牲了开源社区的去中心化修正能力（争议点）

---

## 三、归纳总结

### 3.1 生态地图

```
Anthropic 插件生态（2,282+ 社区插件）
├─ 官方层 claude-plugins-official
├─ 精选层 knowledge-work-plugins（角色级）
└─ 社区层 claude-plugins-community（本仓库）
    ├─ 测试/QA 19% ← 工程质量是最大需求
    ├─ 文档/Spec 12% ← 写作自动化
    ├─ 工作流/编排 10% ← Agent 协作
    ├─ 记忆 7% ← 跨会话上下文（本机最成熟的方向）
    ├─ 评审 6% ← 对抗验证
    └─ 垂直/长尾 43% ← 无所不包
```

### 3.2 治理模式对比

| 模式 | Apple App Store | npm | Claude Plugins |
|------|----------------|-----|----------------|
| 审核 | 人工+自动，周级 | 无前置 | 自动扫描+人工审批，夜级同步 |
| 版本锁定 | 版本号 | semver 浮动 | **sha 锁定** |
| 社区修正 | 无 | PR 自由 | **PR 自动关闭**（单向流） |
| 撤销 | 下架 | unpublish | 内部管线撤除 |

---

## 四、趋势判断

### 趋势 1：Agent 插件市场进入爆发期（年内万级）

> 依据：2,282 个插件 × 2,282 commits 的迭代密度 + 提交需排审核队。测试/QA 占 19% 说明工程化需求真实存在。按 npm 早期增速，年内破万可期。

### 趋势 2：sha 锁定 + 安全扫描将成为 Agent 分发标配

> 依据：skill 天然是"可执行知识"（含脚本/hooks），供应链风险高于传统包。Claude 的治理模式（锁 sha+扫描+人工审批）会被其他 Agent 平台复制。

### 趋势 3：插件经济的垂直深挖才刚开始

> 依据：垂直领域（SAP/Salesforce/Shopify）仅 29 个（1%）——企业系统的 Agent 化插件是蓝海。对照 pm-skills（职业级）和同花顺（金融数据），每个行业都会出"官方插件"。

---

## 五、关联分析

### 5.1 与本机 400+ Skill 生态的对照

| 维度 | Claude Plugins | Hermes Skills | 差距 |
|------|----------------|---------------|------|
| 数量 | 2,282 | 400+ | 量级差但人均产出高 |
| 打包 | plugin（多skill+hooks+MCP） | 裸 skill 目录 | 无打包层 |
| 版本 | sha 锁定 | 无版本管理 | 🔴 无（skill-review 待补） |
| 分发 | marketplace 每夜同步 | 本地/exchange-protocol 三机 | 内部共享无公开分发 |
| 审核 | 自动扫描+人工审批 | skill-vetter（安全审查） | ✅ 理念一致 |
| 发现 | /plugin 命令 | skills_list+description | 同构（渐进式加载） |

**核心差距是版本与分发**——本机 skill 无版本管理（curator 的 git 回滚是唯一防线），skill 的"sha 锁定"思想可借鉴（至少给关键 skill 加 git tag）。

### 5.2 与 [2026-08-22-Skills从入门到精通-Miles万字长文-AgentSkills工程化.md](2026-08-22-Skills从入门到精通-Miles万字长文-AgentSkills工程化.md) 的关联

Miles 讲"单个 Skill 怎么写好"，本仓库展示"Skill 怎么打包分发治理"。Miles 的企业治理章节（安全分级/版本责任/共存测试）正是 Claude 平台在 marketplace 层统一提供的——**平台治理 vs 企业自治理的分工**。

### 5.3 与 [2026-08-22-PMSkill2.0-产品经理工作蒸馏工厂-21个Skill三层架构.md](2026-08-22-PMSkill2.0-产品经理工作蒸馏工厂-21个Skill三层架构.md) 的关联

pm-skills 是垂直 Skill 集合的样板——理论上可直接提交到这个 marketplace（Agent Skills Standard 兼容）。**pm-skills 915 Star vs marketplace 2,282 插件**：前者证明了内容价值，后者证明了分发渠道价值——两者结合才是完整商业闭环。

### 5.4 与 [2026-08-22-同花顺FinancialAPI-官方A股数据与AgentSkill全家桶.md](2026-08-22-同花顺FinancialAPI-官方A股数据与AgentSkill全家桶.md) 的关联

同花顺的 hithink-finance Skill 是"数据服务商进 Agent 市场"的先行者。如果同花顺把它提交到 Claude marketplace，就是金融数据插件的 first mover——**每个数据服务商都会走这条路**（趋势 3 的实证）。

### 5.5 与 adaptive-agent 插件的特殊关联

`adaptive-agent`（越用越强：skill 周期审计 + 用户画像构建）与本机 evolver + auto-memory-keeper + memory-refiner 的组合完全同构——**独立生态收敛到相同设计**，交叉验证了"自适应 agent"架构的必然性。其 /skill-review 的"staleness/missing gotchas/improvements"三维审计与本机 skill-review 的"退化/冗余/僵尸化"三维几乎逐字对应。

---

## 六、拓展应用推荐

### 6.1 高相关插件深挖清单（值得逐个研究）

| 优先级 | 插件 | 深挖点 |
|--------|------|--------|
| P0 | `adaptive-agent` | /skill-review 的审计维度与自动触发机制 |
| P0 | `agent-knowledge` | 11 种边类型图谱 + 置信度衰减设计 |
| P1 | `adversarial-review` | Claude×Codex 对抗收敛的循环终止条件 |
| P1 | `agent-memory` | 工具输出压缩 60-90% 的具体策略 |
| P2 | `agent-advisor` | subagent 仪表盘的可视化维度 |
| P2 | `agent-comm` | 跨 agent 通信协议（对比 exchange-protocol） |

### 6.2 可借鉴的机制

1. **sha 锁定思想**：给本机关键 skill 加 git tag（版本可回滚可引用）——低成本高价值
2. **安全扫描前置**：skill-vetter 已有，可在 skill_manage create 时强制跑（现在可能是可选）
3. **staleness 审计**：adaptive-agent 的"过期检测"维度可加进本机 skill-review（skill 引用的工具/API 失效检测）

### 6.3 商业视角（OPM 层）

本机的 skill 生态如果对外：哪些 skill 有 marketplace 价值？（量化铁律引擎/笔记双格式/飞书全家桶是三个候选）——Agent Skills Standard 兼容意味着技术门槛已经消失，剩下的是包装与文档。

---

## 七、指南分析

### 7.1 治理模式评估

**优点**：
- 安全第一：自动扫描+人工审批+锁 sha，供应链攻击面最小化
- 单一事实源：marketplace.json 机器可读，客户端实现简单
- 质量下限：审核淘汰低质/恶意插件

**争议**：
- **PR 自动关闭**是极端中心化——社区无法自助修正清单错误（如失效链接），必须走内部管线
- 审核带宽是瓶颈（2,282 已收录，提交队列未知）
- 无公开的评分/使用量数据——发现机制弱于 npm/VS Code 市场

### 7.2 数据质量

- marketplace.json 结构干净（name/description/source/homepage 四字段）
- description 质量参差（部分是完整段落，部分是碎片）——与 Miles 说的"description 要认真写"形成对照
- sha 锁定是亮点，但 homepage 与 source.url 有时不一致（镜像/重命名）

---

## 八、金句摘录

> "A read-only mirror of the community plugin marketplace... synced nightly from Anthropic's internal review pipeline."

> "Pull requests opened directly against this repo are closed automatically — all changes flow from the internal review pipeline."（中心化治理的极端形态）

> 插件条目的 source 锁定 sha——市场引用固定版本而非浮动分支，保证可复现与安全审计。

---

## 九、行动启示

- **P0：关键 skill 加版本标记**——借 sha 锁定思想，给 iron-rules/note-dual-format/bookmark-reader 等核心 skill 打 git tag，改动可回滚可引用
- **P1：深挖 adaptive-agent 源码**——其 /skill-review 与本机 skill-review 的同构收敛值得逐行对比，找差异补盲区
- **P1：staleness 检测进 skill-review**——skill 引用的外部 API/工具失效检测（adaptive-agent 的第三维审计）
- **P2：本机 skill 的 marketplace 价值评估**——量化/笔记/飞书三系 skill 若包装发布，是 Agent 经济的潜在入场券
- **生态监控**：定期拉 marketplace.json 做增量 diff——Agent 插件经济的实时脉搏（可挂 cron）

---

> **延伸阅读**：
> - 仓库：https://github.com/anthropics/claude-plugins-community
> - 官方插件：https://github.com/anthropics/claude-plugins-official
> - 知识工作插件：https://github.com/anthropics/knowledge-work-plugins
> - 插件提交：https://clau.de/plugin-directory-submission
> - [Skills 从入门到精通](2026-08-22-Skills从入门到精通-Miles万字长文-AgentSkills工程化.md) — Skill 写法 vs 插件分发
> - [PM-Skill 2.0](2026-08-22-PMSkill2.0-产品经理工作蒸馏工厂-21个Skill三层架构.md) — 垂直 Skill 集合的 marketplace 潜力

## 相关笔记

- [Skills 从入门到精通](2026-08-22-Skills从入门到精通-Miles万字长文-AgentSkills工程化.md) — Skill 写法 vs 插件分发的对照
- [PM-Skill 2.0](2026-08-22-PMSkill2.0-产品经理工作蒸馏工厂-21个Skill三层架构.md) — 垂直 Skill 集合的 marketplace 潜力
- [Agent = LLM + Harness](2026-08-20-Agent大约等于大模型加Harness-结构设计企业操作指导.md) — 插件经济的 Harness 视角