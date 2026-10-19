# Agent-native Product Management — AI时代的PM方法论

- 📅 2026-05-09
- ⭐ 4/5 — 一人PM+AI Agent的实操手册，两个可安装Skill思路值得借鉴
- 🏷️ #AI产品管理 #Agent-native #PM方法论 #CompoundEngineering
- 📰 Every.to
- 🔗 https://every.to/guides/ai-product-management-guide

## 摘要

Every旗下写作产品Spiral的独立开发者Marcus Moretti，分享了如何用AI Agent（Claude Code）重新定义产品管理工作。核心是两个可安装Skill：ce:strategy（面试式引导生成策略文档）和ce:product-pulse（每日自动产品脉搏报告）。文章提出PM工作从"跨工具搬砖"转向"对话即工作"，80%规划+20%执行的新范式，以及一人PM团队靠AI放大产能的实战经验。

## 核心内容

### PM 学科演进

PM起源于1930年代P&G的"Brand Man"理念——每个产品需要专人负责（ownership + accountability）。1940-50年代HP让PM成为客户和工程师的中间人。互联网时代加入UX设计、敏捷开发、A/B测试。到今天，PM要全能（设计+外交+销售+统计），平均公司有100+ SaaS订阅，导致严重过载。LLM的出现让大量跨学科工作从小时级降到分钟甚至秒级。

### 主循环：Plan → Ship → Review → Repeat

产品管理主要发生在Plan和Review阶段：
- Plan：从策略文档开始——解决什么问题、如何解决、目标用户、成功指标、核心工作轨道
- Ship：构建并部署
- Review：收集学习，上线后检查指标

关键洞察：每次上线都是实验，用户反应不可预知。上线越多学习越多，学习累积后需重新审视策略。

### ce:strategy — 策略文档生成器

基于《Good Strategy Bad Strategy》（Richard Rumelt）设计，AI通过面试式对话产出strategy.md：

- Target Problem：用户反复遇到的昂贵痛点
- Approach：1-2句描述产品的独特解题角度（不是功能列表，不是目标）
- Who it's for：参考《Crossing the Chasm》，早期聚焦1个persona
- Key Metrics：3-5个SMART指标，避免虚荣指标，至少追踪"人数+收入"
- Tracks：2-4条核心能力线（超过4条=缺乏聚焦）

可选部分："Not working on"排除干扰项，"Marketing/positioning"支持增长。

**关键设计**：面试式引导而非填表。如果回答模糊，Agent会追问"具体谁的处境？他们现在怎么做的？为什么不行？"

### ce:product-pulse — 产品脉搏报告

每日自动生成，一页纸（30-40行终端输出），四段结构：

- Headlines：3行要点，只读这3行就知道发生了什么
- Usage：核心事件数、转化率、策略指标 + 环比变化
- System：p50/p95/p99延迟 + Top 5错误签名
- Followups：1-5个值得深挖的可行动项

数据源支持（只需1个也能跑）：
- 产品分析：PostHog/Mixpanel/Amplitude
- 应用追踪：Datadog/Sentry/Logfire/Honeycomb
- 支付：Stripe/Paddle
- 只读数据库连接（写权限会被拒绝）

每次运行保存Markdown到 ~/pulse-reports/，历史积累形成产品记忆。可设置每日定时运行。

**Agent充当分析师**：不只是拉数据，还评估数据——如某端点错误率高，会深挖是单用户问题还是第三方服务中断。第二遍自动追加前瞻性分析。

### 工作方式变革

- 不再写ticket——有了策略文档和工作轨道，用ce:ideate/brainstorm/plan技能决定建什么
- Issue tracker必须有MCP或Agent集成（GitHub Issues/Linear）
- Kanban看板：Now/Next/Later，不做Sprint
- 定性反馈不可替代——邮件+15分钟通话链接是最佳反馈渠道

## 🔍 借鉴点

- 面试式引导生成结构化文档 → 可用于Hermes Skill的task-executor/planning，改进交互式任务启动
- Pulse四段报告结构 → 可改进watchdog cron的报告格式（增加Headlines摘要+Followups可行动项）
- strategy.md模板 → 可作为产品策略文档的标准结构，Target Problem → Approach → Persona → Metrics → Tracks
- "对话即工作"理念 → 与Hermes的Skill+对话式工作流理念一致，验证了方向正确性
- Compound Engineering插件模式 → Skill可组合形成闭环（strategy → ideate → plan → pulse），与我们的skill-pipeline思路一致

## 🔗 关联性

- 关联已有笔记：[2026-04-04-AI-work-paradigm](2026-04-04-AI-work-paradigm.md) — AI工作范式转变，与本文"80%规划20%执行"呼应
- 关联已有笔记：[2026-04-05-SelfImproving-Agent-CLI-infra](2026-04-05-SelfImproving-Agent-CLI-infra.md) — Agent CLI基础设施，本文的Claude Code实践
- 关联已有 skill：watchdog — Pulse报告模式可借鉴改进watchdog的cron输出格式
- 关联已有 skill：skill-pipeline — Skill组合管道，与Compound Engineering的skill组合理念一致
- 关联已有 skill：task-executor — 面试式引导可改进任务启动流程

## 💡 启发

- "策略文档不包含产品需求"这个区分很重要——策略是方向，需求是路径，混在一起会导致视野模糊
- 面试式引导比填表式更适合AI场景——人在对话中比在表单中表达更清晰，AI可以实时追问
- Pulse报告保存为Markdown而非数据库——轻量但可搜索，历史积累本身就是价值
- "质量>数量"的数据源策略——1个好数据源胜过4个配置不当的
- 定性+定量闭环——Pulse管定量，用户访谈管定性，缺一不可

## 🔮 预判

- 短期（3月内）：更多团队会采用Agent-native PM工具，Claude Code/Codex的plugin生态会快速扩张
- 中期（6月内）：面试式引导会取代传统PRD模板成为主流，策略文档即代码（strategy-as-code）
- 长期（1年+）：PM角色会进一步分化——战略型PM（定义方向）和执行型PM（已被AI替代），中间层消失

## 相关笔记

- [2026-04-04-AI-work-paradigm](2026-04-04-AI-work-paradigm.md) - AI工作范式转变
- [2026-04-05-SelfImproving-Agent-CLI-infra](2026-04-05-SelfImproving-Agent-CLI-infra.md) - Agent CLI基础设施
- [2026-04-05-xiaolongxia-one-person-company](2026-04-05-xiaolongxia-one-person-company.md) - 一人公司模式
- [2026-05-03-AI-Agent-Protocol-Ecosystem-2026-学习](2026-05-03-AI-Agent-Protocol-Ecosystem-2026-学习.md) - Agent协议生态
