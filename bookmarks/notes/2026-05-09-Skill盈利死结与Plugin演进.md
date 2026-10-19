# 面对Skill的盈利死结，OpenAI和Cursor交了同一份答卷

- 📅 2026-05-09
- ⭐ 4.5/5 — 少见的从商业模式本质分析Skill/Plugin差异的深度文章，框架清晰，对Skill生态方向判断有直接参考价值
- 🏷️ #Skill #Plugin #OpenAI #Cursor #商业模式 #平台战略 #AI生态
- 📰 yage.ai / Superlinear Academy
- 🔗 https://yage.ai/share/skill-plugin-evolution-20260507.html

关联：[2026-05-09-Agent-native-PM方法论](2026-05-09-Agent-native-PM方法论.md) [2026-04-02-Agent Skills才是关键抽象层](2026-04-02-Agent Skills才是关键抽象层.md) [2026-04-05-Hermes-Agent-competitor-analysis](2026-04-05-Hermes-Agent-competitor-analysis.md)

## 摘要

OpenAI和Cursor在2026年4-5月同时从Skill转向Plugin，表面相同但战略目标完全不同。文章提出Skill的"自杀基因"三层论证（复制成本为零/托管可下载/飞轮数据不经过作者），解释了Skill无法独立承载商业模式的根本原因。Plugin通过三件套（运行环境绑定+认证凭证+分发渠道）把"知识"变成"服务"来破局。OpenAI的动机是建执行层防线（防模型商品化），Cursor的动机是建差异化层（防供应商替代）。

## 核心内容

### Skill的自杀基因

| 层级 | 问题 | 根因 |
|------|------|------|
| 复制层 | 买家拿到文件后免费分发 | 明文.md，复制成本=0 |
| 托管层 | 做成SaaS收费 | 用户可下载本地运行 |
| 飞轮层 | 拿不到执行数据 | 数据进LLM日志，不经过作者 |

三层叠加=定价权为零。Agensi、skills.sh等marketplace都卡在同一环节。

### Plugin比Skill多什么

1. **运行环境绑定** — Codex用agents/openai.yaml声明依赖，Cursor用MCP server声明工具。用户获得的是可运行的能力而非文件
2. **认证凭证** — OAuth/API Key在平台侧管理，收费从"卖文件"变成"卖服务链"
3. **分发渠道** — Plugin Catalog提供持续曝光+安装+更新

> Plugin把"知识"变成了"服务"。知识传出去收不回来，但服务需要持续维护。

### OpenAI：执行层防线

- 威胁：模型商品化→降级为"众多提供商之一"
- 手段：Codex Plugin让工作在Codex里完成，绑定的不是模型选择而是工作流
- 数据：Codex周活从3万→300万（100x），半数非编码任务
- 引用Forbes："界面层优势驱动使用量，执行层优势塑造运营依赖和长期锁定"

### Cursor：差异化层

- 威胁：Claude Code直接竞争+模型调用成本高于收入（2025年底前毛利为负）
- 手段：Plugin+.cursorrules+MCP绑定编辑器体验，迁移成本不是一键能完成
- Composer自研模型+Kimi低成本模型才实现企业毛利转正，个人仍亏损

### 未来推演

| 路径 | 逻辑 | 判断 |
|------|------|------|
| 分化 | Codex运行时 vs 编辑器体验是不同控制点 | 概率高 |
| 收敛 | SKILL.md+MCP标准成熟后覆盖Plugin需求 | 取决于现金流压力 |
| 窗口期 | 2026投入期0%抽成，SKILL.md在30工具通用 | 短期安全 |

## 🔍 借鉴点

- **Plugin三件套框架** → exchange-protocol升级时需考虑：共享的Skill是否需要服务化（运行环境+认证+分发）？目前exchange-protocol是纯知识共享，不涉及这三层
- **SKILL.md标准生命力** → 30工具通用验证了Hermes押注方向正确，短期内不会过时
- **自杀基因论证** → 自用Skill体系不面临此问题，但未来如果做Skill marketplace/商店需重新审视
- **分化vs收敛判断** → 2026年投入期是写通用Skill的好时机，各平台还在兼容而非封闭

## 🔗 关联性

- [2026-05-09-Agent-native-PM方法论](2026-05-09-Agent-native-PM方法论.md) — 同一时期的AI产品管理趋势，Skill/Plugin演进是Agent-native产品的基础设施
- [2026-04-02-Agent Skills才是关键抽象层](2026-04-02-Agent Skills才是关键抽象层.md) — Skill作为抽象层的定位，本文补充了其商业局限性和Plugin升级路径
- [2026-04-05-Hermes-Agent-competitor-analysis](2026-04-05-Hermes-Agent-competitor-analysis.md) — 竞品格局分析，本文是OpenAI/Cursor策略的最新动态
- 关联skill：exchange-protocol — 纯知识共享模式，目前不涉及Plugin三件套，但长期需关注
- 关联skill：hermes-agent — Skill体系设计方向确认

## 💡 启发

- **"知识→服务"的转变是平台级杠杆** — 不只AI领域，任何内容型产品都面临同样困境（电子书/模板/教程），解法都是附加服务层
- **Hermes的自用定位反而是优势** — 不需要解决商业化变现，可以专注质量而非分发。但这也意味着Skill生态不会像Plugin生态那样快速增长
- **收敛窗口期的策略** — 在各平台还兼容SKILL.md的窗口期，应该多写高质量通用Skill，而非绑定特定平台的高级特性

## 🔮 预判

- **短期(2026)** — SKILL.md标准继续扩大采用，各平台Plugin生态处于投入期，开发者不需要选边站
- **中期(2027)** — OpenAI和Cursor的Plugin开始分化，出现平台独占的高级能力；MCP标准成为跨平台的最大公约数
- **长期(2028)** — 要么收敛到统一标准（SKILL.md+MCP覆盖所有需求），要么彻底分化为各平台独立生态。取决于谁的现金流先承压

## 相关笔记

- [2026-05-09-Agent-native-PM方法论](2026-05-09-Agent-native-PM方法论.md) - Agent-native产品管理，四步循环框架
- [2026-04-02-Agent Skills才是关键抽象层](2026-04-02-Agent Skills才是关键抽象层.md) - Skill抽象层论
- [2026-04-05-Hermes-Agent-competitor-analysis](2026-04-05-Hermes-Agent-competitor-analysis.md) - Hermes竞品分析

