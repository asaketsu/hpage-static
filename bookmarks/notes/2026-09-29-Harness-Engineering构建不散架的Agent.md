# Harness Engineering：构建不会散架的 AI Agent

> 原文：@0xwhrrari《Harness Engineering: How to Build AI Agents That Don't Fall Apart》(X Article, 2026-09, **3.9M views / 1535 赞**——该作者又一篇爆款)
> URL: https://x.com/0xwhrrari/status/2093685107534000560
> 阅读日期：2026-09-29 | 评分：★★★★★（5/5，Harness 工程的完整方法论，与我们 harness 架构 skill 族全面互证）
> tag: #Harness #Agent架构 #上下文工程 #权限 #trace #可靠性

## 一、核心命题：问题不在智能，在环境

Agent 失败时大多数人的动作序列：改提示词→换模型→加上下文窗口。Agent 依然忘决策/用错工具/跳过验证/死循环。**"问题不总是智能，问题是它周围的环境——那个环境就是 harness。"**

Dario Amodei 谈 Claude Code 诞生："你需要一个接口、一个 harness 来使用它们。" OpenAI 构建 agent-first 代码库时同样发现：**早期进展慢是因为"环境规定不足（the environment was underspecified）"，不是模型缺能力**——回应不是让 agent 更努力，而是把缺失的能力变得**可读且可强制（legible and enforceable）**。

层级定义：
```
PROMPT  -> 指令
CONTEXT -> 工作视图
HARNESS -> 操作系统
LOOP    -> 局部改进
GRAPH   -> 协调
```

**同一个模型，放进聊天框=问答机；放进带终端/测试/浏览器/项目记忆/隔离 worktree/评审循环的仓库=能交付软件的工程师。权重没变，harness 变了。**

## 二、生产 Harness 的七项职责

| # | 职责 | 要点 |
|---|------|------|
| 1 | 定义成功（先于执行） | 成功标准在开始前写死，非事后评感觉 |
| 2 | 选择性加载知识 | **地图保留上下文，巨手册消耗上下文**——详细知识贴近它管辖的代码/工具，按需加载 |
| 3 | 暴露正确的工具 | 每个工具有清晰目的/可预测输出/显式失败态/权限边界；**好工具在模型推理变坏之前就消除歧义** |
| 4 | 记忆外置为持久状态 | **对话不是 system of record**——决策/工件/失败/风险存上下文窗口外；下个会话继承的是工作状态而非"对话的有损转述" |
| 5 | 先加传感器再加自主 | Agent 无法纠正它观察不到的东西：测试/linter/截图/日志/schema 校验把模糊质量变证据；**模型造工件，环境产证据，harness 判定证据是否足够继续** |
| 6 | 权限在模型外强制 | MODEL SUGGESTS → POLICY CHECKS → TOOL EXECUTES；**不要让同一个概率系统发明计划、批准风险、执行副作用** |
| 7 | 记录 trace + 本地恢复 | 每次运行留下可读轨迹（请求/选中上下文/工具调用/状态变更/验证结果/重试/成本/最终工件/回滚点）；**没有 trace 失败是谜，有 trace 失败是下一次 harness 改进的输入** |

工具权限阶梯示例：READ FILES 默认允许 / RUN TESTS 沙箱内 / WRITE FILES 工作区内 / ACCESS NETWORK 按任务 / DEPLOY·DELETE DATA 需审批。

## 三、指令变基建（规则编码两次）

多数团队把重要规则留在散文里：agent 读了，最终还是漏掉一条。更强的模式是**编码两次**：
1. GUIDE：agent 能理解的指引（"UI 代码不得直接查数据库"）
2. CHECK：agent **无法绕过**的机械检查（lint 规则/CI 门禁）

这正是"质量门禁机械化"原则的独立再发现——可归因、可审计、防止最终答案掩盖坏过程。

## 四、从最小闭环开始（成熟度四层）

```
LEVEL 0  prompt + model
LEVEL 1  项目指引 + 工具
LEVEL 2  结构化状态 + 测试 + 有界循环
LEVEL 3  权限 + trace + 恢复 + 人工闸门
```
**只在任务配得上复杂度时升级**。短低危任务可能只需一条 prompt+一次评审；六小时能改文件/上网/开 PR 的编码运行需要真 harness。**harness 应小于它控制的故障面**。

## 五、上线前 12 问 checklist

成功先定义？知识不靠全量加载？工具契约清晰？执行与生产隔离？重要决策存在对话外？危险转换有证据？不可逆动作有审批？每个循环有重试上限+预算？中断后可恢复？每个工具调用可解释？失败会更新指引/测试/工具/策略？最终工件可回滚？

**多个"否"= 更强的模型不会让系统可靠，只会让失败更昂贵。**

## 六、💡 对我们的价值分析

### ✅ 已在做的（几乎逐条命中）
- 七职责全部有对应物：成功先定义=验收门禁/判据先行；知识分层=L1/L2/L3；工具契约=skill 系统带 pitfalls；记忆外置=PROGRESS.md/三级记忆/session DB；传感器先行=验收机械化+exit_code≠0 不算完成；权限外置=三层权限模型+生产部署二次确认；trace=session DB+evolution_log
- "编码两次"= 我们的门禁脚本化（AGENTS.md"检查通过不算通过，exit_code=0 才算"）
- 四层成熟度= harness 架构 skill 的分级同构

### ⚠️ 可改进的（差距）
- "地图 vs 巨手册"原则未彻底执行：部分 skill SKILL.md 过长（全量塞 L2），违背"详细知识贴近管辖物按需加载"——references 机制就是为此存在的，该把超长正文下沉
- "失败更新指引/测试/工具/策略"（12 问第 11 条）依赖手动——session-evolution-scan 已建但尚未跑出首个闭环案例
- 循环预算：部分 cron 无重试上限（12 问第 8 条）

### 🔥 重点行动
1. **skill 目录"地图化"瘦身**：对超长 SKILL.md 做"正文≤骨架+细节下沉 references"改造，先试点 3 个最长 skill
2. **本文与 harness-engineering-principles skill 互链吸收**：七职责表+12 问 checklist 是现成的审计模板，作为季度架构评审的评分卡
3. **cron 循环预算补齐**：高频巡检类 job 加重试上限参数

## 七、内容整理（归纳总结与关联分析）

**归纳总结**：Agent 失败根因常在环境不在模型——harness 决定模型能看到什么/能碰什么/什么在会话间存活/什么算证据/何时必须停。七职责：成功先定义/知识选择性加载/工具契约化/记忆外置/传感器先于自主/权限外置于模型/trace+本地恢复。规则编码两次（GUIDE+CHECK）。四层成熟度从最小闭环起步。12 问上线门禁。收束句："最好的建造者不只问哪个模型最聪明，而是问哪个环境让智能变得可靠。"

**关联分析**：本文是 rari 的 Harness 篇（3.9M views）与他的 Jev 篇构成组合拳——Jev 篇讲决策层（harness 的一号组件），本篇讲整个 harness。与我们体系的关系是**全面互证**：AGENTS.md 的 Harness Engineering 五准则（2026-05-07）在五个月后获得工业界爆文的独立背书，且本文多了"四层成熟度"和"12 问"两个可操作件。与 09-28 Agent 策略模型笔记的关系：那篇定义"Agent=控制循环里的策略模型"，本篇是"控制循环的建造手册"——理论篇+工程篇。DUCK 训练体系（开训三层门禁/指纹比对/验收器）是本文七职责在物理 Agent 域的实例化。

## 八、查询拓展

- OpenAI《Harness engineering: leveraging Codex in an agent-first world》（"environment was underspecified" 出处）
- Dario Amodei 谈 Claude Code 起源的完整访谈
- rari 的 Substack（同系列生产系统文章）
- Anthropic "Building effective agents"（同期官方 harness 观点对照）

## 九、趋势判断

1. **Harness Engineering 成为正式学科**：3.9M views 说明行业痛点共识已达临界——2026 内会出现标准教材/认证，"prompt engineer" 职位全面转向 "harness engineer"
2. **"指令变基建"是下一阶段竞争核心**：散文规则→机械检查的迁移率会成为团队 AI 成熟度指标
3. **模型月抛，harness 复利**：模型下月就换，工具/测试/状态/策略/trace 持续增值——投资在 harness 上的每一分钟都在复利，投在 prompt 调优上的会贬值（本文核心投资论）
4. **最小闭环原则对抗过度平台化**：先观察-验证-恢复再谈平台——与 AGENTS.md"dry run 先行"同源，预测"agent 平台"类产品会因违背此原则而失败

## 十、指南分析（怎么用这篇文章）

- 团队自审：拿 12 问当评分卡过一遍现有 agent 系统，"否"最多的三条就是下季度路线图
- 说服资源：用"更强的模型只会让失败更昂贵"和"权重没变 harness 变了"两句话管上管下
- 新系统冷启动：严格按 L0→L3 走，抵抗一开始建平台的诱惑

## 十一、拓展应用推荐

- 与 [[2026-09-28-Jev-Engineering决策层架构]] 组合读（同作者：决策层+harness 全景）
- 与 [[2026-09-28-Agent即策略模型-四层解剖与跨体系验证]] 组合读（理论+工程）
- Hermes 落地：第六节三条行动（skill 瘦身/审计模板/循环预算）可挂进季度架构评审
- 与 AGENTS.md Harness 五准则对照：作为 dev-meow 团队的必读材料

## 相关笔记
- [[2026-05-25-Agent-Harness-Engineering-从Prompt到Harness的范式跃迁]]
- [[2026-07-31-Agent-Harness-Engineering知识体系总纲]]
- [[2026-06-15-Agentic-Engineering三层体系-Loop-Harness-FDE]]
- [[2026-04-30-Harness-Engineering即控制论]]
- [[2026-09-29-Jev与LangGraph构建生产系统]]

→ 张力篇：[解放模型-Replit薄Harness与自主委派](2026-09-30-解放模型-Replit薄Harness与自主委派.md)（厚薄之争：厚护栏薄决策的调和点）
