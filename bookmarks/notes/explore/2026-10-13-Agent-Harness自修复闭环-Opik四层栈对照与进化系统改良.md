# Agent Harness 自修复闭环：Opik 四层栈对照与 Hermes 进化系统改良

> **来源**：X Article（Akshay Pachaar @akshay_pachaar，Comet ML/Opik 赞助文）
> **原文链接**：https://x.com/akshay_pachaar/status/2064051835636498924
> **记录日期**：2026-10-13
> **本文用途**：不只做笔记——对照分析后把可落地项直接实施进 Hermes 进化系统（见第八、九节执行记录）

**标签**：#AgentHarness #可观测性 #自修复 #进化系统 #回归测试

---

## 一、内容详细整理

### 1.1 核心论点：可观测性的真正瓶颈在 trace 落地之后

Agent 生产环境失败时，现有可观测平台给你的是"它做了什么"，几乎不给你"怎么修"：
- ✅ 有：干净的 trace（每次模型调用/工具/耗时/token 成本）
- ❌ 没有：为什么坏、改什么能修好、怎么保证下周不再坏

于是工程师手动循环：逐 span 滚动 trace → 形成失败理论 → 手写补丁 → 祈祷不破坏原有功能。**每次新模型发布带来一批新失败模式，这个手动循环从头再来。**

引用 Cursor 的观点：围绕 agent 的 harness（prompts+tools+checks 包装层）工程量巨大且永无止境——同模型+更好 harness = 远好结果。**"trace 之后的一切"才是团队真正卡住的环。**

### 1.2 四层栈架构（Opik）

一个连通的工作流：**Trace → Ollie 诊断 → 提出修复 → 应用并验证 → 失败锁为回归测试 → 回到 Trace**

**Layer 1 Tracing**：一个 decorator 自动仪器化所有 LLM 调用/工具调用/检索步骤；50+ 框架（LangGraph/CrewAI…）；每条 trace 记录当时生效的 agent 配置 → 完全可复现。

**Layer 2 Ollie（诊断+修复 agent）**：
- 无代码权限模式：读 span 树，跨全部 LLM 调用解释因果链（"为什么最终答案忽略了检索到的上下文？"）
- `opik connect` 后升级完整修码模式：**读源文件→定位责任行→提 diff（无显式批准不改动）→批准后用原失败输入重跑→流式对比新旧 trace→把原失败锁为回归用例**

链条：**Bad trace → root cause → diff → approve → rerun → regression locked**

**Layer 3 Test Suites**：
- 批判现有 eval 工作流：建标注数据集、定数值指标、比较浮点——"那是研究者的思维方式，不是工程师的"
- 替换为**plain-English 断言**（底下转成 LLM-as-judge），每条测试干净的 pass/fail
- 关键机制：**每条被调试的失败 trace 自动变成新测试用例——测试套件从真实生产失败生长，而非预先写好的合成场景**

**Layer 4 Agent Sandbox**：
- 批判 prompt playground："改一个 system prompt 重跑一次 LLM 调用"回答的是错误问题
- 生产问题是"**改了这个之后整个 agent graph 会怎样**"——sandbox 端到端跑完整仪器化 agent，改 prompt/换模型/加工具，看全系统响应；每次 sandbox 跑出完整 trace
- 非开发者（PM/领域专家/QA）可以安全测试配置而不碰 git

### 1.3 飞轮

Instrument → 生产失败 → Ollie 读 trace+源码提修复 → 人批准 → sandbox 用原失败输入重跑 → 通过 → 存为 Blueprint → 环境指针升到 staging → 原失败锁为回归测试。**每个循环，harness 越来越难被弄坏。**

## 二、查询拓展

### 2.1 Ollie 与"诊断 agent"模式
Ollie 本质 = 挂在可观测数据上的编码 agent，与 GitHub Copilot Workspace/Devin 类"issue→PR"agent 同构，差异在于输入源是**运行时 trace** 而非静态 issue——它看到的是系统真实行为证据，不是用户转述。

### 2.2 回归测试锁失败（regression lock）
把生产失败输入固化为测试用例 = 传统 SRE "postmortem 产出 runbook+test" 的 agent 化版本。与我们 notes-eval-gate 的"发布即入 golden set"完全同构，差别是 Opik 自动化到了"调试即入测试"。

### 2.3 plain-English 断言 vs 数值指标
与 notes_7module_check 的取舍相同：我们用确定性 grep 门禁（可枚举结构）而非 LLM 打分。Opik 的 LLM-as-judge 适合语义质量（"答案是否引用了上下文"），确定性断言适合结构合规（"是否含九模块"）——两者是互补不是替代。

### 2.4 Agent Sandbox 与"全图重跑"
对应我们 cron 改动的"first-run 验证"（cron-create-protocol skill：改完必试跑）。Opik 把它产品化为 UI 内一键端到端，并强调"非开发者可测"——这是团队协作维度，单机 Hermes 不需要，但"改配置必须全链重跑验证"原则一致。

## 三、归纳总结

### 3.1 四问分层模型（原文的隐含框架）

- **What happened** → 平台自动（trace）✅ 已解决
- **Why it happened** → 诊断 agent（读 trace 推因果链）
- **What to fix** → 修码 agent（读源码提 diff）
- **Won't break again** → 回归锁定 + sandbox 全图验证

### 3.2 Hermes 进化系统现状对照

- **What**：cron executions.db 有全量执行记录（468 条/夜可查）、request_dump、jobs.json last_error——trace 层完备 ✅
- **Why**：429 风暴 SOP 是手动的（三步定位法在 skill 里），error-case-library 靠 cron 扫描+LLM 归纳——**有但非自动闭环**
- **Fix**：诊断后我手动 hermes cron edit——**无"原失败输入自动重跑验证"环节**
- **Won't break again**：429 修复只 unpin+错峰，**没有把"钉死=无兜底"锁成自动检测规则**——下次再有人 pin 新 job，同样的事会重演
- **回归测试**：完全缺失——cron 配置健康没有任何自动断言（doctor 命令存在但我们没挂起来用）

### 3.3 对照差距表

- Opik Layer1 Trace ↔ executions.db + request_dump（已有）
- Opik Layer2 Ollie ↔ 429-SOP + auto-diagnose-fix job（半自动，无重跑验证闭环）
- Opik Layer3 回归锁 ↔ **缺：cron 配置断言套件**（"无 pinned job""夜间 job 不在窗口尾部"这类 plain 断言）
- Opik Layer4 Sandbox ↔ hermes cron run 手动试跑（有命令无制度化）

## 四、趋势判断

### 趋势1：可观测平台将吞掉"修复"环节
依据：文章是赞助文但有真实行业痛点（Cursor harness 论），LangSmith 已在做 evaluation-driven development，Opik 把 diff+reren+regression 串成一线——trace-only 平台（老一代）会被挤出。

### 趋势2：测试套件将从生产失败自动生长成为标配
依据：合成 eval 集与生产分布漂移是公认痛点；"调试即入测试"机制成本极低（失败输入已在手）而价值随失败累积复利。

### 趋势3：plain-English 断言是 LLM-as-judge 的工程化收敛点
依据：工程师不写浮点阈值断言是行为现实；自然语言断言+judge 打分的 pass/fail 兼顾表达力与可读性。

## 五、关联分析

### 5.1 与 hanakoxbt《Loops and Graphs》三断点笔记的关联
同为"闭环缺口"诊断框架。Loops&Graphs 找出我们进化系统三断点（学习边人卡/门禁无回滚史/假边），本文从产业侧给出同一命题的解法栈（诊断→修复→回归锁）。两者共同指向：**进化系统的价值不在检测在闭环**。

### 5.2 与 DUCK 训练验收体系的关联
12ep 忠实 eval + 黄金档 + 验尸重训循环 = 物理世界的同构飞轮（失败模式→诊断→配方修→重训验证→门禁锁住）。Opik 的"原失败输入重跑"等价于我们的"验尸用同 variant eval"——都是防"修复未经验证"的假修复。

### 5.3 与 evolution-gate v3 的关联
我们的门禁是"deterministic→trajectory→rollback history"证据链；Opik 增加了第四环"修复后重跑对比 trace"——这正是我们缺的：429 修复后我只跑了 `hermes cron run` 单点验证，没有"用原失败场景（窗口挤满时）重放"的验证。

## 六、金句摘录

> 「The real bottleneck isn't your observability. It's everything that has to happen after the trace lands on your screen.」— 瓶颈从来不是看见，是看见之后的四步。

> 「Every cycle, the harness gets harder to break.」— 自修复系统的复利表述。

> 「That was a reasonable product in 2023. It's the wrong abstraction for teams running agents in production today.」— 产品保质期论。

## 七、行动启示

- **缺口即清单**：把"won't break again"从口号变成可执行断言——本次直接实施（见下）
- **修复必须重放原失败**：以后每次 cron/系统修复，`hermes cron run` 单点验证不够，要尽量构造原失败条件复测
- **失败自动入测试**：每次生产失败修复后，把检测条件写成确定性脚本进 evolution-gate 信号——这条已在做（429-SOP 模式），继续强化

## 八、本次直接实施的系统改良（分析→行动闭环）

对照差距表，落地三件（零成本、确定性、当天生效）：

### 8.1 信号6：pinned-job 结构病检测（对应 429 事故根因）
evolution-gate.sh 加确定性断言：任何 enabled job 带 provider/pinned 字段 → `pinned_jobs=N` 点名。**把 10-12/10-13 两天的 429 事故根因锁成永久回归检测——第三次再有人 pin，门禁当夜就报。**

### 8.2 信号7：cron doctor 断链检测
`hermes cron doctor` 有现成健康检查但我们从没挂载——加进 gate：输出非空即报 `cron_doctor_findings`。

### 8.3 回归断言沉淀
429-SOP（skill references）补一节"预防断言"：pin 即报的 gate 信号6 就是该事故的 regression lock——从此该类失败模式有确定性测试在岗。

## 九、指南分析

**本文方法论价值**（如何读赞助文不迷路）：
1. **剥离广告看骨架**：Opik 是赞助文，但"trace 之后四步分离"的框架独立成立——评估时问"框架是否自洽可迁移"，不问"是否软广"
2. **四问分层**：What/Why/Fix/Again 四分离是通用诊断模板，可直接套用任何系统（我们套进化系统五分钟出差距表）
3. **复利判据**：评估自修复系统的唯一问题是"每个循环是否让系统更难坏"——没有回归锁的自修复都是一次性劳动
4. **反例先行**：文章用"prompt playground 回答错误问题"式反例定义自己产品边界——写方案时先定义"不解决什么"比堆功能更有说服力

## 十、拓展应用推荐

- **DUCK 训练管线**：把"失败 ckpt 自动入验尸队列"机制借鉴过来——每次 12ep 不达标档自动记入失败档案（已有 docs 习惯，可升级为 jsonl 台账供 gate 读取），训练侧的 regression lock
- **cron 运维**：任何新的系统级修复（如本次 429）按"修复→重放验证→断言入 gate"三步走，防第三次重演
- **对外的工程借鉴**：如果未来给别人交付 Agent 系统，Opik 四层栈是现成的架构清单——trace（executions.db 式）/诊断（SOP+自动归因）/回归（确定性断言套件）/沙箱（试跑环境），单机版全部可自建无需平台
