# 解放模型：Replit 的薄 Harness 与模型自主委派

> 原文：@yibie 转述 Replit AI 团队（Daniel Furman 等 5 人）《Free the Models》(replit.com/blog/free-the-models, 2026-09)
> URL: https://x.com/yibie/status/2105136465692737582
> 阅读日期：2026-09-30 | 评分：★★★★★（5/5，"harness 该做多厚"之争目前最硬的实证）
> tag: #Harness #多Agent #委派 #Replit #BitterLesson #路由器悖论

## 一、一句话论断（router 悖论）

**"无论基于先进启发式，还是用一个读每一轮对话的小模型来挑该用哪个 LLM，router 永远比它正在为其选择模型的那个模型更弱。"**

这句话把整个 router 范式逼到墙角：**router 更弱，凭什么替更强的模型做决定？** Replit 的答案：不改进 router，**拿掉它**——核心循环自己决定子 agent 用什么档位和多少 effort，随任务展开调整。GPT-6 Astra 把日常实现交给更便宜的子 agent，自己决定哪些 token 值得花。

## 二、为什么"少"搭脚手架

- **每次模型发布都让 harness 里烘焙的假设作废**
- 模型在长时程任务上变强，**自己就越来越倾向委派**（用子 agent 做上下文管理和并行）
- **但前沿是锯齿状的**：最强编码模型≠最强 UI/幻灯片/邮件；每个前沿模型文风独特到可凭文本辨认（编码腔绰号"Claudish"）
- 设计原则：让每个模型按自己的方式工作，保留仍需要的护栏，最低成本拿质量
- **"每一个新模型都把我们送回原点，重新测试那些我们曾确信的东西"**

## 三、三个决定 × 四个委派原语

核心循环每步做三个决定：**①该想多用力**（effort 逐步设置，新模型上中途改 effort 不破缓存）**②什么时候交出去**（自己做/交出去/一次两个；小任务零派生）**③交给谁**（锯齿前沿→每个专家跑各自最强模型）。

| 原语 | 设计 |
|------|------|
| ①领域感知子 agent | 通用 worker+只读 explorer+浏览器 tester+reviewer+设计子 agent；**harness 决定存在哪些专家，核心循环决定何时怎么用** |
| ②档位×effort | 小/标准/大三档×effort 级别，每次派发时选（机械重命名=小+低；顽固 bug 假设生成=大+高） |
| ③可复用子 agent | 回到已交代过的子 agent 而非从头开始；**没有全会长保活的 sidekick**——任意数量子 agent 跨种类跨档位保持温热，核心循环决定唤醒谁（更长缓存寿命压低成本） |
| ④动态 effort 调整 | 训了个升级系统：每步检查轨迹，把 effort 匹配任务难度——**对正在做的事中途反应，而非对请求一次判断**（与 router 的本质区别） |

## 四、模型自己会委派（生产数据）

三模型 medium effort 生产对照：

| 指标 | Fable 5 | Fable 5.1 | GPT-6 Astra |
|---|---|---|---|
| 派发子 agent 的轮次 | 32% | 21% | 36% |
| 交给通用 worker 的轮次 | 0.9% | 2.3% | **20%** |
| **回到已有子 agent 的派发占比** | 17% | 29% | **42%** |

- Fable 系很少用通用 worker：派 explorer/reviewer，实现留给自己
- **Astra 是第一个会例行把活交给通用 worker 且不需吩咐的模型**；回访率随代际上升
- 真实回合（09-17 trace）：派 1 explorer+2 worker+1 tester，五次 worker 派发三次是回访

## 五、结果与诚实边界

Max 模式（核心循环 Astra），四次重复均值：

| 配置 | 分数@成本 |
|---|---|
| **Replit Agent** | **49% @ $2.53/任务**（另一基准 72%） |
| Astra low | 42% @ $2.25 |
| Astra xhigh | 60% @ $5.86 |
| **Sidekick 架构** | **33% @ $1.84**（两个基准上输 11-16 点） |

读法：①Replit Agent 对 sidekick 高 11-16 点；②Astra 单跑只有花 2 倍多钱才高 2-11 点；③**两个基线都无法同时在成本和分数上取胜——Replit Agent 对单跑 Astra 帕累托有效**；④完全按交付用户的样子跑，零提示词改动（生产数据量级）。

诚实边界（yibie 整理）：自家产品+自家基准；Astra 数字来自公开榜单且 harness 不同；xhigh 下 DeepSWE 74% 高于 Replit 72% 但贵一倍多（"更好"准确说是**同等成本下更好**）；四模型只有一个强委派倾向；代号是 Replit 叫法。

## 六、理论框架：Bitter Lesson 的 harness 版

"把人类知识烘焙进 agent 短期有用，长期平台期，最终被随计算规模扩展的通用方法超越。**僵硬的 harness 迫使模型按一种方式工作；可组合的 harness 让它自己选。模型越聪明，harness 就该替它做越少的决定。**"

三件收获：①押注扩展律（依赖模型品味的委派随每次发布自动改善）②适配任务（小任务零派生/搜索派 explorer/大构建派团队）③复用而不持久化（子 agent 保留上下文以防再用；没被用就不持久化任何东西）。

## 七、💡 对我们的价值分析

### ✅ 已在做的
- "harness 提供选项+护栏，核心循环做决定" = 我们 delegate_task 的方向（max_concurrent_children 限制=护栏）；"领域感知子 agent"=四猫分工
- "回访温热子 agent" = delegation 的会话保持机制的雏形

### ⚠️ 可改进的（差距）
- 我们的"路由"大量烘焙在 cron prompt 里（哪个 job 用哪个模型硬编码）——**router 悖论同样适用**：调度层的模型判断弱于执行模型
- 无 effort 分档：所有任务同 reasoning effort——机械任务浪费、顽固问题欠配
- 子代理无"温热复用"：每次 delegate 都冷启动（上下文重建成本）

### 🔥 重点行动
1. **cron 模型路由改为"核心会话自选"**：高频 cron 的模型档位不再硬编码，产出质量反馈驱动升降档（数据已有=cron-execution-metrics）
2. **委派原语对照升级**：给 delegate_task 场景补"回访温热"语义（同 topic 的子 agent 优先复用）——省上下文重建
3. **Effort 分档试点**：机械巡检类 job 显式降 effort/检查复杂分析类升——成本立省（Astra low→xhigh 差 2.6 倍成本）

## 八、内容整理（归纳总结与关联分析）

**归纳总结**：router 悖论（路由器永远弱于被选模型）→ 拿掉 router，核心循环自决三件事（多用力/何时交/交给谁）→ 四原语（专家菜单/档位×effort/温热复用/动态 effort）→ 生产数据（Astra 42% 派发率/20% 通用 worker/42% 回访）→ 对 sidekick 高 11-16 点、对单跑 Astra 帕累托有效（49%@$2.53）→ 定位为 Bitter Lesson 实例：模型越聪明 harness 越薄。

**关联分析**：与 [[2026-09-29-Harness-Engineering构建不散架的Agent]]（rari 篇）形成**正面张力**——rari 说"harness 是操作系统、越强越好"，Replit 说"解放模型、越薄越好"。调和点：**七职责（安全/状态/trace）不薄，决策权（路由/effort/委派）全放**——厚护栏薄决策。与 Harness-Zero（DAIR 周榜，harness 蒸馏进权重）构成同一趋势的两面：harness 的"判断性内容"正在消亡，"结构性内容"（权限/状态/trace）长存。与 Agent 策略模型笔记互证：核心循环=策略内核，委派原语=动作空间设计——**"解放模型"本质是把策略改进的压力从 harness 层移回模型层**（正是 EXPO-FT/微调路线的主场）。

## 九、查询拓展

- replit.com/blog/free-the-models（原文含完整表格与 trace）
- Sutton《The Bitter Lesson》（理论框架源头）
- mini-swe-agent（Astra 公开榜单基线）
- 对照阅读：Anthropic "building effective agents"（厚 harness 流派）——两派的基准对齐比较

## 十、趋势判断

1. **Router 层将在 2027 年前大面积拆除**：模型自主委派随代际免费改善（回访率 17→29→42% 的斜率），硬编码路由的技术债开始计息
2. **"sidekick 架构"进入反模式名单**：一主一副形态输 11-16 点的数据会改变默认设计直觉
3. **effort 成为新的成本杠杆**：中途调 effort 不破缓存后，"动态 effort"系统（对轨迹反应）取代"请求级路由"——实时性从请求级升到步级
4. **Bitter Lesson 的 harness 界定收敛**："该保留的 harness"=权限/状态/trace/恢复（结构性），"该消失的 harness"=路由/风格/流程（判断性）——与 rari 七职责的并集即终局形态

## 十一、指南分析（怎么用这篇文章）

- 自查：数一数系统里"替模型做决定"的点（路由/effort/委派/风格），每个都问"模型自己能不能选"
- 迁移节奏：先放 effort（零风险）→再放委派（中风险）→最后放路由（需质量反馈闭环）
- 引用注意：帕累托有效≠绝对最优，引用时带"同等成本"限定

## 十二、拓展应用推荐

- 与 [[2026-09-29-Harness-Engineering构建不散架的Agent]] 对读（厚薄之争两极，第八节调和点）
- 与 [[2026-09-28-Agent即策略模型-四层解剖与跨体系验证]] 互证（策略内核与动作空间）
- Hermes 落地：第七节三行动（cron 自选模型/温热复用/effort 分档）
- 周综合候选：**"厚护栏薄决策"**——9 月 Harness 文献（rari/Replit/Harness-Zero/LangGraph 四篇）的统一结论

## 相关笔记

- [2026-09-29-Harness-Engineering构建不散架的Agent](./2026-09-29-Harness-Engineering构建不散架的Agent.md) — Harness 厚薄之争的另一极：职责完整性派
- [2026-09-06-GrokBot智能体操作系统三层控制架构-从Harness-Loop-Graph到审批边界的完整设计](./2026-09-06-GrokBot智能体操作系统三层控制架构-从Harness-Loop-Graph到审批边界的完整设计.md) — Loop/Graph 控制栈对照，审批边界即厚 harness 实例
- [2026-09-06-Karpathy五级阶梯与Graph工程全景-从LLM到Graph的系统化进路](./2026-09-06-Karpathy五级阶梯与Graph工程全景-从LLM到Graph的系统化进路.md) — LLM→Graph 进路中"决策权上收 vs 下放"的谱系参照
