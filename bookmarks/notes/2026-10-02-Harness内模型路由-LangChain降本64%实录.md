# Harness 内模型路由：LangChain Open SWE 的 64% 降本实录

> 原文：Sydney Runkle（LangChain）《How to Build a Model Router in the Harness》(X Article, 2026-10-02, 43.6K views/120 赞)
> URL: https://x.com/sydneyrunkle/status/2105704739585565066
> 阅读日期：2026-10-02 | 评分：★★★★★（5/5，路由工程全流程实录：任务画像→模型选档→harness 落地→A/B 验证，数字完整可复算）
> tag: #模型路由 #Harness #降本 #A/B测试 #Jev #LangChain #OpenSWE

## 一、核心论断：路由决策属于 harness，不属于网关

前沿模型贵，而大多数 agent 任务不需要前沿智能（Anthropic 官方指南也承认 Haiku 起步常是最优）。好 agent = **model-harness-task fit**（对的任务配对的模型+上下文）。
**路由决策该在 harness 不在通用网关**——因为选对模型需要的领域/任务上下文，harness 已经组装好了，网关天然看不到。（评论区共鸣："这必须说——一堆公司还在推销 AI 网关来'省成本'"）

战绩：Open SWE（开源编码 agent）加路由器 vs 恒定顶级模型，**中位成本降 64%，质量无可测差异**。

## 二、四步法（全流程）

**Step 1 摸任务**：从 LangSmith trace 拉一周 thread 级数据，LLM 分类器打任务类型标签。分布：新功能 22%/bug 修复 17%/测试或 no-op 16%……特征工作调查类 thread 更长更贵，测试发布类短而便宜。复杂度双信号：总成本（大任务多 token）+调用次数（**高次数=更难，或模型需要多轮追问才搞定**——两个含义要区分）。

**Step 2 摸模型**：Artificial Analysis 智能指数画"智能-成本"曲线取 Pareto 前沿，选三档：
- Fast：**GLM-5.3-Flash (xhigh)**（开放模型站上 Pareto 前沿——"开放模型跨过门槛的又一标志"）
- Balanced：GPT-5.6 Sol (medium)
- Performance：GPT-6 Astra (low)
模型无关接口，换模型=一行改动。

**Step 3 harness 里建路由器**（thread 首条人类消息时三选一）：base prompt（告诉分类器"挑最便宜的可能完成任务的模型"）+ 每档平语言判据（**判据来自两源：自己的任务分析 × 厂商模型指南**）+ 分类器模型。初版 LLM 结构化输出，**现跑在 Jev 决策模型上——快了近 50 倍**。判据深度耦合 Open SWE 任务集——这正是"属于 harness"的又一理由。

**Step 4 追踪结果**（路由前先埋好测量）：离线 eval（难点=数据集要像真实流量且按用户在乎的分级）vs A/B（真实流量但用户暴露于次优路由）。两信号：**Merged PR 率**（主指标，每 thread 可测）+ 用户 👍👎（稀疏但能抓路由错误）。

## 三、实验数字（可复算级完整）

**A/B-1（vs 恒定 GPT-6 Astra，973 threads）**：
- 质量：merged PR **29.2% vs 27.3%**（p=0.49），开 PR 率 38.9% vs 39.6%（p=0.82）——无可测差异
- 成本：**中位 $0.94 vs $2.61（-64%）**，均值 -42%，p90 -37%（不是少数便宜离群撑起来的）
- 路由分布：balanced 56%/fast 34%/**performance 仅 10%**——多数请求不需要最强模型
- 档间成本差 30 倍：fast $0.097/balanced $1.50/performance $2.88（中位）
- 用户反馈直接点名 overspend："这查询太贵了""这请求不该路由到 performance"

**A/B-2（vs 恒定 fast）**：一天内紧急终止——工程师立刻抱怨 fast-only 质量拖生产力，"没等到统计显著就结束了"。

## 四、What's next（诚实边界）

①DeepSWE 等受控基准补 A/B ②子 agent 的模型选择也路由（现在子 agent 独立选）③**mid-thread 重路由**：话题变了换模型可能值——代价是 prompt cache 作废（异步 agent 的 cache 本来就常过期，代价常可忽略）④trace 挖用户情绪（挫败 thread=可能需要更强模型）。

## 五、💡 对我们的价值分析

### ✅ 已在做的
- GLM-5.3-Flash 做 fast 档 = 我们免费模型链的主力（智谱）——**LangChain 官方认证它站上 Pareto 前沿**，选型背书到位
- cron-execution-metrics/质量反馈闭环的雏形=Step 4 的对应物

### ⚠️ 可改进的（差距=机会）
- **我们的 cron 模型是硬编码**（每 job 固定模型），无路由判据——fast 档跑巡检/performance 档跑分析完全可自动
- 无任务画像：没做过"一周 cron 任务分布"分析（Step 1 的缺失）
- 子任务路由：delegate_task 的子代理模型未按任务难度分档

### 🔥 重点行动
1. **Hermes 版三档路由表**：巡检/格式化/摘要→Flash 档；笔记/分析→balanced 档；架构决策/复杂 debug→performance 档——判据写在 cron prompt 模板里（Step 3 三件套直接抄）
2. **先跑 Step 1**：用 cron-execution-metrics 拉一周任务分布+成本，看我们的"performance 仅 10%"是否成立
3. **Jev 决策层试点就此闭环**：LangChain 官方已把路由判据跑在 Jev 上（50×提速）——我们的决策契约试点方向被生产验证

## 六、内容整理（归纳总结与关联分析）

**归纳总结**：路由属于 harness 不属于网关（任务上下文在 harness 手里）。四步：摸任务（trace 分类+成本/次数双复杂度信号）→摸模型（Pareto 前沿取三档）→harness 建路由（base prompt+平语言判据+Jev 分类器 50×快）→追踪结果（merged PR 主指标+用户反馈）。973 threads A/B：质量平（p=0.49）、中位成本-64%、仅 10% 任务真需要 performance、档间 30×价差。反向 A/B 一天杀（fast-only 拖生产力）。边界：mid-thread 重路由/子 agent 路由/情绪信号待做。

**关联分析**：与 Replit《解放模型》构成**路由问题的双子星**——Replit 说"拿掉 router 让模型自决"（核心循环自选 effort/委派），LangChain 说"router 要建在 harness"（判据+分类器）。表面矛盾，实际分层：**Replit 反对的是"网关式外置 router"（弱模型替强模型决策），LangChain 建的是"harness 内路由"（领域判据+决策模型）——两者共同杀死的是无上下文的通用网关**（评论区"kizuno18"的 harness 路由+本地 $0 工具混跑与我们 Jetson 本地推理路线同构）。Jev 在此完成生态闭环：LangGraph 编排（09-29 篇）→Replit 委派→**本篇路由判据**——决策模型三类落点（转移函数/委派原语/路由判据）全部出现在生产系统。GLM-5.3-Flash 上 Pareto 前沿=我们免费链的权威背书。

## 七、查询拓展

- Model routing middleware with Jev（LangChain 新发的中间件，可直接用）
- Artificial Analysis Intelligence Index（智能-成本曲线数据源）
- Building a Harness with Jev（判据写法细节）
- Open SWE on GitHub（trace 结构与 merged PR 记录方式）

## 八、趋势判断

1. **AI 网关创业窗口关闭**：harness 内路由（有任务上下文）对网关路由（只有请求）是降维打击——通用网关退化为计费/限流基础设施
2. **决策模型（Jev 类）成为路由层标配**：50× 提速让"每 thread 首消息即路由"零成本——LLM 分类器路由会被淘汰
3. **"仅 10% 需要 performance"成为普遍分布**：多数 agent 任务画像会复现这个比例——默认顶级模型=系统性 overspend
4. **mid-thread 重路由+cache 代价权衡成新课题**：换模型弃 cache 的成本模型（TTL 5min 场景常可忽略）会进框架层

## 九、指南分析（怎么用这篇文章）

- 立刻可抄：四步法当 checklist；三档判据写法（任务分析×厂商指南）直接套我们的 cron 模板
- 测量先行：没有 merged PR 类主指标就别开路由（Step 4 是前置不是事后）
- 引用注意：64% 是中位数且对照=最贵模型；引用时带"均值-42%/p90-37%"防夸大

## 十、拓展应用推荐

- 与 [[2026-09-30-解放模型-Replit薄Harness与自主委派]] 对读（路由双子星：自决 vs harness 判据，共同点=杀死网关）
- 与 [[2026-09-29-Jev与LangGraph构建生产系统]] 串联（Jev 生态三落点闭环）
- Hermes 落地：第五节三行动（三档路由表/任务画像/Jev 试点确认）
- 免费模型链维护：GLM-5.3-Flash 前沿地位=继续做 fast 档主力的依据
