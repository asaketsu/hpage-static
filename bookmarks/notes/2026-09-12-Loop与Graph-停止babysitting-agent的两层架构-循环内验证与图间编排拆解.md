# Loop 与 Graph：停止 babysitting agent 的两层架构——循环内验证+图间编排+学习边与爆炸半径门禁拆解

> **来源**：X/Twitter @hanakoxbt（Hanako）Article《Loops and Graphs: how to stop babysitting agents and only approve the last step (full course)》2026-09 初
> **原文链接**：https://x.com/hanakoxbt/status/2091515787366306154
> **配套课程**：agent-layers.vercel.app（20 课含模板/配置/构建顺序）
> **抓取方式**：X Article 直读全文
> **笔记日期**：2026-09-12
> **关联笔记**：《Skill 九条原则》（代码胜于推理/预判借口）《SoL-Pi》（harness 四机制）《Gipp 3-15%》（为失败率设计）《beamnxw Lane》（身份/记忆分离）《自进化 Harness》（三种写）

---

## 零、结论先行

**文章核心拆分：Loop（循环）让单个工作单元在没有你的情况下正确——Graph（图）决定哪些单元存在、什么并行、什么等待、什么永远不跑。两者不是选择而是分层：Loop 住在 node 内部，Graph 住在 node 之间。** 对我们最深的增量：①"学习边"（learning edge）——被接受的结果不回到 worker 指令而是回到 splitter 的 brief 作为约束——这是 mem0 三种写里 W2（持久化写入）的 graph 层实现，我们 evolver 的"门禁后写入"是 node 内版；②"爆炸半径门禁"替代"置信度阈值"——不可逆操作不设高阈值而是**车道直接关闭**，阈值可被调整但关闭的车道不会——这打脸我们 content-judge/zhipu-quota 的阈值设计。**不形成新 skill**（与我们 AGENTS.md 准则 2/3 + harness 簇多篇已有覆盖），但学习边和爆炸半径门禁两个 Nugget 直接记入审计清单。

## 一、核心拆分：Loop vs Graph

> "A loop makes a unit of work correct without you. A graph decides which units exist at all."

| 层 | 职责 | 失败模式 |
|----|------|---------|
| **Loop（循环）** | 让一个工作单元正确——produce/check/correct/repeat until green | 没有 check=只是调度器不是循环 |
| **Graph（图）** | 决定哪些单元存在/什么并行/什么等待/什么不跑/结果回哪 | 没有 graph=很好的 agent 跑错误的步骤在错误的顺序 |

**一句话定关系**："The loop lives inside a node. The graph lives between them."（循环住在 node 内，图住在 node 间）

## 二、Loop 层：能失败的 check 才是循环

### 2.1 四件套

```
produce → check → correct → repeat until green
```

**check 是全部**——没有能在你不在时让工作失败的 check，你有的不是循环而是调度器。

### 2.2 两个最狠的 check 设计陷阱

| 陷阱 | 表现 | 后果 |
|------|------|------|
| **两个乐观主义者同意** | 工作做完→末端 bolt 一个 review→review 是另一个模型看输出 | "Two optimists agreeing" |
| **错误不存在≠正确** | check 只查"有没有报错"不查"对不对" | 系统自信地重复错误直到预算耗尽，全程日志干净 |

> "Absence of an error is not evidence of correctness."（错误的缺失不是正确的证据）

### 2.3 Loop 的天花板

Loop 让一个单元更好——但**不能决定哪些单元存在/顺序/注意到五个步骤中有两个从不需要等彼此**。

> "So you get a very good agent running the wrong three steps, in the wrong order, one at a time. Every step is correct. The result is still slow and still wrong-shaped."

**这是人们怪模型的时刻——也是 graph 层开始回本的时刻。**

## 三、Graph 层：工作的形状

### 3.1 两种元素，仅此而已

| 元素 | 定义 |
|------|------|
| **Node** | 一个工作单元：一个有界任务，一个输入，一个输出 |
| **Edge** | 依赖：这个 node 的输出喂那个 node 的输入 |

### 3.2 最常见的浪费："and then"不是 edge

> "Summarize the file and then check the weather has no edge between them. The weather does not consume the summary."

**诊断方法**：对你管线里每个箭头问——下一步实际读取了上一步的输出吗？如果你说不出跨越的变量名，就没有 edge，等待是纯浪费。

> "Most chains have two or three arrows like that, and finding them is usually the largest single speedup available."

### 3.3 四种 Node

| Node | 作用 | 最易错的地方 |
|------|------|-------------|
| **Splitter** | 切分工作→单元 | 切错维度=下游全废（按文件夹切→4 个审计员审同样 3 文件；按爆炸半径切→各有独占视角） |
| **Worker** | 做一个单元（一个视角/自己的上下文） | **给 4 个审计员共享窗口→收敛成 1 个观点+3 个回声**（花了 4 倍的钱） |
| **Code Node** | 合并/排序/去重/比对 | **最被遗忘的 node**——"能不用 judge/decide/assess/summarize 描述的变换就是代码" |
| **Gate** | 门禁 | 见 §五 |

> "A graph where every edge is an agent pays rent on its own wiring."（每个 edge 都是 agent 的 graph 在为自己的接线付租金）

## 四、两条返回路径（文章最大增量）

### 4.1 Correction Edge（纠正边）vs Learning Edge（学习边）

| 边 | 长度 | 作用 | 建了没 |
|----|------|------|--------|
| **Correction edge** | 短——Gate 拒绝一个单元回到产生它的步骤 | 修复**当前运行** | 多数人建了 |
| **Learning edge** | 长——被接受的结果回到 splitter 作为约束 | 修复**之后每次运行** | **几乎所有人跳过** |

> "The tell is a system that is fast and never gets smarter."（又快又不变聪明的系统的特征=没有学习边）

### 4.2 Learning edge 的关键设计

学习边不携带输出——**它携带从输出中提炼的约束**：

> "Notice where it lands. Not in the worker's instructions, in the brief that shapes how the work gets cut."（不是落在 worker 指令里，而是落在决定工作怎么切的 brief 里）

**被确认的原因变成规则→下次切分从这次结束的地方开始**——与 OUI-1 的"幸存程序当训练集"同构（都是"被接受的结果改变下次运行的输入"）。

### 4.3 与 mem0 三种写的映射

| Graph 层 | mem0 三种写 | 我们的对应 |
|----------|-----------|-----------|
| Learning edge（结果→splitter brief 约束） | W2（持久化写入文件，下窗口加载） | evolver（错误模式→规则沉淀） |
| Correction edge（Gate→worker 重做） | W1（进程内发明，用完即弃） | execute_code 重试 |

## 五、爆炸半径门禁（打脸我们阈值设计的一节）

### 5.1 置信度是最弱输入

> "Confidence is the weakest input in that decision, for a reason that is easy to miss: it is the only one the model can influence."

### 5.2 正确变量：爆炸半径（错了多贵才能撤销）

| 车道 | 特征 | 门禁 |
|------|------|------|
| **可逆且contained** | 文案改/测试/有覆盖的孤立函数 | 先开 |
| **可逆但wide** | 共享工具/schema 新增/ dozen callers | 确定性检查+干净轨迹 |
| **不可逆** | 迁移/删除/写生产数据/动钱 | **车道不开放，不论分数多高** |

> "That third row is not a threshold set very high. It is a lane that does not open, and the distinction matters because thresholds get adjusted and closed lanes do not."（第三行不是很高的阈值，是关闭的车道——阈值可被调整，关闭的车道不会）

### 5.3 Gate 内证据读取顺序

1. 确定性结果（测试/lint/exit code）
2. 本次运行轨迹
3. 这个 node 之前被回滚的频率
4. **模型的自我评估最后**

## 六、返回单元不返回批次（最贵错误）

> "Four slices were ported. One fails its tests. If the whole batch goes back, three correct slices get rewritten."

**批回的连锁灾难**：
- 3 个正确的被重写→下一版"不同但不更好"（本来就没问题）
- 重新验证全部 4 个→可能有 3 个因无关原因失败
- **一次失败变成四次不确定结果，还付了钱**
- 做两次→永不收敛

### 4 件随返回同行物

| 物品 | 作用 |
|------|------|
| 缺陷描述 | worker 知道改什么 |
| **Scope line** | **限制 worker 只改这个**——没有它返回单元会膨胀（开门+发现相邻问题→4 文件 diff 没人审） |
| 上次输出 | 参考 |
| 失败原因 | 精确定位 |

**3 次上限**：单元失败 3 次纠正→问题在 plan 不在执行→loop 看不到 plan。

## 七、与我们体系的对照

| 文章主张 | 我们的实践 | 判定 |
|---------|-----------|------|
| Loop 内 check 可程序化 | AGENTS.md 准则 3"质量门禁机械化" | ✅ 已满足 |
| "and then"不是 edge→找假依赖 | execute_code 批处理原则；pub_pipeline 的 `&&` 串联 | 🟡 有意识但没系统审计 |
| Code node 不用模型 | notes_eval_gate.py/scan_data.py 等确定性脚本 | ✅ 已满足 |
| Splitter 切错维度全废 | delegate_task 的 context 分配 | 🟡 未审计过切分维度 |
| Learning edge→splitter brief | evolver（错误→规则）但**没到 brief 层** | 🟡 最增量 |
| 爆炸半径替代阈值 | content-judge/zhipu-quota 用阈值 | 🔴 **打脸**——需审 |
| 返回单元不返回批次 | patch 最小 diff 原则 | ✅ 精神已有 |
| 3 次上限 | AGENTS.md"3+ fixes failed=停下问架构" | ✅ 已满足 |
| 人放在最高后果最低可逆点 | AGENTS.md 权限三层模型 | ✅ 已满足 |

## 八、与今日/昨日笔记的合流

| 篇 | 连接 |
|----|------|
| Skill 九条原则 | 原则⑥"代码胜于推理"=本文 Code node；原则⑤"预判借口"=本文 correction edge 的 scope line |
| SoL-Pi | Action Fusion（编辑+验证合并）=消灭假 edge（"and then"不需要等）；ObservationPack=code node |
| Gipp 3-15% | "为失败率设计"=本文 Gate；"幂等键先于重试"=返回单元不返回批次 |
| mem0 三种写 | Learning edge=W2（持久化）；Correction edge=W1（进程内） |
| OUI-1 | Learning edge 与"幸存程序当训练集"同构——被接受的结果改变下次输入 |
| beamnxw Lane | "人只批准最后一步"=beamnxw 的"one seat writes" |

## 九、批判性审视

1. **Loop vs Graph 的二分过强**：真实系统里 Loop 和 Graph 常混在一起——一个 node 内可以有子 graph（delegate_task 就是），一个 graph 的 edge 可以是 Loop 的 check——文章的清晰拆分是教学设计不是架构现实
2. **"两条返回路径"未给失败数据**：Learning edge 的收益无实测——"又快又不变聪明"是观察，不是量化
3. **爆炸半径三车道**的边界模糊：什么是"contained"什么是"wide"——文章没给判定方法（我们的权限三层模型有更明确的命令级判定）
4. **课程导流**：agent-layers.vercel.app 和 DM "Graph" 是营销——文章是课程的第一章
5. **Splitter 的"切错维度"**：文章说"按爆炸半径切"但没说怎么算爆炸半径——最有决策权的一步最缺操作手册

## 十、金句提取

> "A loop makes a unit of work correct without you. A graph decides which units exist at all."

> "Without something that can fail the work while you are out of the room, you do not have a loop. You have a scheduler."

> "Two optimists agreeing."（review 只是另一个模型看输出）

> "Absence of an error is not evidence of correctness."

> "If you cannot name the variable that crosses, there is no edge, and the wait is pure waste."

> "A graph where every edge is an agent pays rent on its own wiring."

> "The tell is a system that is fast and never gets smarter."（没有学习边）

> "Thresholds get adjusted and closed lanes do not."（爆炸半径车道 vs 置信度阈值）

> "Any failure you do not turn into a permanent constraint, you will meet again."

## 十一、局限性

1. X Article 约 2000 字——教学文/课程导流，无实测数据
2. agent-layers.vercel.app 课程内容未读取——20 课的模板/配置未核
3. Learning edge 的"约束提炼方法"未给——只知道"落在 splitter brief"但不知道怎么提炼
4. §七对照基于本机架构理解，未实际改造 graph
5. 爆炸半径三车道的判定标准未给出实操方法

## 出处标注

| 章节 | 来源类型 |
|------|---------|
| 一至六 | **原文忠实还原**（X Article 全文直读） |
| 七 | **体系映射**（本笔记扩展） |
| 八 | **笔记联动**（今日/昨日 harness 簇交叉） |
| 九 | **批判性审视**（本笔记扩展） |


## 相关笔记

- [Harness-Engineering 19层完整指南](./2026-09-12-Harness-Engineering完整指南-19层从prompt到环境的工程纪律-LunarResearcher体系化拆解.md) — 19层中的编排层
- [Ecdysis论文-FDCR四角色拆解](./2026-09-12-Ecdysis论文-模型特异迁就vs-harness级修复-跨任务失败聚合与FDCR四角色拆解.md) — FDCR四角色与图间编排
- [Skill九条原则-Bibryam三幕生命周期](./2026-09-12-Skill九条原则-从被选到活着-Bibryam三幕生命周期拆解与Hermes-skill库对照审计.md) — 代码胜于推理/预判借口
- [SoL-Pi英伟达自我优化Harness](./2026-09-11-SoL-Pi英伟达开源自我优化Harness-四大机制与152选4的RSI流水线拆解.md) — harness四机制
- [一人后台办公室Lane制](./2026-09-11-一人后台办公室Lane制-AI员工身份记忆分离与Pin宪法-beamnxw实战.md) — 身份/记忆分离
