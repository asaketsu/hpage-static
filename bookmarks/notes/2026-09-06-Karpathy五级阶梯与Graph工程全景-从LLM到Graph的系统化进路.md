# Karpathy 五级阶梯与 Graph 工程全景 — 从 LLM 到 Graph 的百分比进路和"删除一切保留图"

#Karpathy #GraphEngineering #Software3.0 #AI工程 #Agent #Loop #DAG #知识图谱 #autoresearch #AgentHub #Anthropic动态工作流

## 出处

- 信源：X 推文 @AISimplifyX（AI Simplify，2026-09-06，136 赞 1.1 万浏览）——推荐 Karpathy 斯坦福 1 小时讲座
- 底稿核心（推文 528 字）：**10% → LLM；30% → Prompt；50% → Agent；70% → Loop；100% → Graph** + "Delete everything, keep Graph."
- 外网研究（本笔记主体）：YouTube 讲座结构页（philia 频道 12.6 万浏览的逐级拆解）+ dooza.ai 19K 字综合研究文（autoresearch/AgentHub/Anthropic 三线全考据）+ Latent.Space swyx Software 3.0 分析
- 笔记日期：2026-09-06 | 指令语义：**结合下文查询外网分析 Graph，记笔记**——外网检索挖底稿没有的硬增量

## 一、内容详细整理

### 1.1 底稿：五级阶梯（推文原文）

```
10% → LLM        模型本体：可即时重编程的裸计算机
30% → Prompt     自然语言成为新编程语法（Software 3.0：prompt 即程序）
50% → Agent      连接记忆/工具/上下文，预测触发执行
70% → Loop       推理期推理与权重优化严格分离（验证反馈循环）
100% → Graph     复杂 agent 工作流变成有向消息传递图
```

核心主张：**AI 工程不只是写更好的 prompt，是围绕模型建系统**——上下文、记忆、工具、反馈环、数据流。"Delete everything, keep Graph."（把其他都删掉，保留图。）

### 1.2 外网研究增量①：五级的讲座级定义（YouTube 逐级拆解交叉）

| 级 | 卡帕西定义（讲座口径） |
|----|----------------------|
| 10% LLM | 把 LLM 当**随时可重编程的裸计算机**（raw computer you reprogram on the fly） |
| 30% Prompt | **自然语言是新编程语法**——context window 是程序，LLM 是解释器（Sequoia Ascent 2026 命名 Software 3.0） |
| 50% Agent | 连接记忆/工具/上下文，让**预测触发执行**（predictions trigger execution） |
| 70% Loop | **推理时推理（inference-time reasoning）与权重优化严格分离**——模型不变，靠验证反馈循环改进输出 |
| 100% Graph | 把复杂 agent 工作流变成**有向的、消息传递的图**（directed, message-passing graphs） |

### 1.3 外网研究增量②：Loop 级的实证——autoresearch（2026-03，86K stars）

**棘轮循环**（ratchet loop，照录）：

```
LOOP FOREVER:
1. 读当前 train.py + 近期历史
2. 提出一个有动机的改动
3. 提交候选（git commit）
4. 训练 ~5 分钟
5. 测量 val_bpb
6. 崩溃? 检查/修复/回退
7. 改进? 保留. 变差? git reset.
8. 记录结果. 从不问人.
```

**战绩**：2 天 **~700 次实验 → ~20 个保留优化 → ~11% 训练加速**（Karpathy 手调多年的模型）；Shopify CEO Tobi Lütke 在内部模型上复现 **19%**。

**三文件结构**：
- `prepare.py`（**锁定**）——固定数据准备与评测，agent 不许碰 → **不能靠放水作弊**
- `train.py`（可编辑）——~630 行实验面：模型/优化器/超参，agent 唯一可改的东西
- `program.md`（**老板**）——纯英文指令：指标/规则/崩溃处理/提交回退策略/何时升级。Karpathy 称之为 **"programming the program"（给程序编程）**

**为什么循环有效——环境为自治而工程化（四条件清单）**：
1. **输出可验证**：数字要么改进要么没有——没有品味之争，没有 "looks good to me"
2. **每个动作可逆**：git reset 回到最后已知良好态，失败实验只花时间
3. **反馈周期短**：5 分钟一跑 = 每天数百次学习循环（而非三次）
4. **动作空间有界**：只有一个可编辑文件，agent 不能跑出去搞坏世界

> "The model's intelligence is almost beside the point. The loop works because the environment was engineered for autonomy."（模型的智力几乎无关紧要——循环有效是因为**环境为自治而工程化**。）

### 1.4 外网研究增量③：Graph 级的双实体

**AgentHub（2026-03，"GitHub for agents"）**：
- 设计哲学是**删除**：无主分支/无 PR/无合并队列——人类 Git 假设少数贡献者+规范主线+合并为目标；agent 研究全部反转：**数千 agent 并行探索，多数结果永不合并，失败实验仍是有价值的证据**
- 核心操作不是 "merge into main" 而是 **"traverse the search graph"（遍历搜索图）**
- CLI 即图接口：`ah push`（HEAD 作 DAG 新节点）/ `ah children`（此结果上试过什么）/ `ah leaves`（未探索前沿）/ `ah lineage`（溯源）/ `ah diff` / `ah log -agent X`
- **关键洞察：commit DAG 就是知识图谱**——节点=提交（携带假设/代码 diff/指标/agent 身份/保留或丢弃裁决），边=父链。能问出普通 Git 里很别扭的问题：*内存限制下哪个保留结果指标最好？哪些实验是 batch-size 改动的后代？哪些叶子还没评测？*
- **现实核查**：README 自称 "Just a sketch"，数日内转私——**教训是架构性的不是产品性的**：agent 变多时，单主线思维/人类节奏评审/转录式记忆最先崩

**Anthropic 三层生产化**：
1. **五工作流模式**（2024-12《Building Effective Agents》）：链式/路由/并行/编排者-工人/评估者-优化器——"找能用的最简单模式，更简单的形态确实失败才加结构"
2. **动态工作流**（2026-05）：Claude 自己写 JS 编排脚本，**fresh-context 子 agent 并行（16 并发/单次 1000 上限）**→过滤→评审 agent 反驳→综合成带引用报告。实证：Bun **535,496 行 Zig→Rust 11 天，99.8% 测试通过**
3. **知识图谱 cookbook**：Haiku 抽取带类型实体关系（Pydantic schema）→Sonnet 语义消歧（"Edwin Aldrin"="Buzz Aldrin"——零字符重叠也能抓住）→NetworkX 组图→**答案引用确切用到的边**

> 注意转变：2024 指南说"**你**建工作流"，2026 功能说"**Claude 建工作流**"。不变的是人仍拥有：目标/范围/权限/验证策略/预算/回滚规则。

### 1.5 外网研究增量④：Graph 工程的定义与"记忆放置"总表

**Graph 工程定义**（综合研究文）：多 agent 系统需要**持久共享记忆**——agent 读写带类型、带出处的实体/主张/关系（知识图谱），而不是把全部转录塞进上下文窗口。口号：**"The agent forgets; the graph does not."（agent 会忘，图不会。）**

**核心命题**：瓶颈通常不是下一次模型调用，而是**记忆与评测的放置位置**——每种架构外化一种记忆：

| 架构 | 记住什么 |
|------|---------|
| 循环 Loop | 迭代与评测——试过什么、得了什么分 |
| 链 Chain | 任务顺序——什么在什么之后 |
| 蜂群 Swarm | 并行搜索——多个独立上下文同时探索 |
| 提交 DAG | 实验谱系——什么是从什么繁衍来的 |
| 知识图谱 | 共享事实与出处——知道什么、来自哪个源 |

**危险清单**（原文明示）：指标被博弈（棘轮只优化它看得见的）/ 实体消歧可能灾难性合并错的东西 / 1000-agent 运行烧钱极快 / 知识图谱的诚实度=最弱信源的诚实度。**收尾检验标准**：*每个重要输出都能追溯到——一个目标、一个计划、一个工件、一个来源、一条图路径、一个评测器决定、一条有界执行记录。*

### 1.6 外网研究增量⑤：决策指南（何时用什么）

**黄金法则：用能解决问题的最少架构。**

| 你的处境 | 从什么开始 | 为什么 |
|---------|-----------|--------|
| 简单低风险问题 | 单次 AI 调用 | 最低成本与延迟，无需系统 |
| 输出可客观检验 | 循环（生成→评测→修订） | 重复反馈可测地改进工件 |
| 稳定可预测的步骤 | 链/固定工作流 | 可测试、无聊、可靠——无聊是好事 |
| 大量独立工作单元 | 并行 agent | 砍墙钟时间，留清晰 reducer |
| 可变可分解任务 | 编排者+工人 | 按子任务动态分工 |
| 事实必须跨会话存活 | 持久记忆/知识图谱 | 转录会忘，存储的状态不会 |

**加任何复杂度前的三问**：成功能否验证？动作能否撤销？业务能否负担成本与延迟？——任何一答为否，先修那个，**更多 agent 只会放大问题**。

## 二、查询拓展

- autoresearch 源码（630 行）的四条件在训练之外场景的移植（内容/运营/投研）
- Anthropic knowledge graph cookbook 的 Pydantic schema 模板与 Sonnet 消歧 prompt
- Sequoia AI Ascent 2026 演讲全文（Software 3.0 命名场）与斯坦福讲座原始视频
- "graph engineering" 综合笔记原文（12 引用考据版）的完整决策框架
- LangGraph/CrewAI 等图编排框架与 AgentHub 理念的实现差异

## 三、归纳总结

1. **五级阶梯的本质是"系统化程度"递进**：LLM（裸机）→ Prompt（编程语言）→ Agent（接外设）→ Loop（自我改进）→ Graph（组织化协作）——每一级都是把上一级的输出变成下一级的输入，**百分比是系统贡献占比，不是时间表**
2. **Loop 级的核心纪律是"可验证+可逆+短反馈+有界"四条件**——autoresearch 700 实验/2 天证明：**环境工程 > 模型智力**（"模型的智力几乎无关紧要"是全场最重的一句话）
3. **program.md = Software 3.0 的极致形态**：用英文写"给程序编程"的规格（指标/规则/回退/升级），锁 prepare.py 防作弊——**规格与评测面分离**是自治的安全底座
4. **Graph 级的两个面：协作图（AgentHub 的 DAG）+ 记忆图（知识图谱）**——前者解决"数千 agent 怎么共享探索"，后者解决"事实怎么跨会话存活"；共同底座是**节点带完整出处（假设/diff/指标/裁决）**
5. **"agent 会忘，图不会"是 Graph 级的一句话纲领**：每个 agent 在上下文窗口里重建世界 = 浪费学到的一切；读写共享的带类型带出处的图 = 跨会话复合彼此的工作
6. **人类保留的是"什么是好"的定义权**：五级演进每级删除一个人类瓶颈（写代码的→跑实验的→协调 agent 的），**从未删除定义"好"的人类**——与审批边界论同构
7. **决策指南的反 over-engineering**："用最少架构解决问题"+ 三问门禁——**图不是终点是选项**，多数场景到 Loop 级就够（链=无聊=可靠是美德）
8. **危险清单与可追溯检验**：指标博弈/消歧灾难/烧钱/信源诚实度——每个重要输出七重追溯（目标/计划/工件/源/图路径/评测决定/执行记录）是 Graph 级的验收标准

## 四、趋势判断

1. **"graph engineering" 正在成为 agentic engineering 之后的下一个命名阶段**：2024 模式→2026 动态工作流→知识图谱三层已由 Anthropic 产品化；Karpathy 的五级阶梯给了它教育级叙事——**2026 下半年至 2027 将出现图工程框架/平台的创业窗口**
2. **上下文窗口与知识图谱的分工定型**：窗口=工作记忆（快而忘），图=长期记忆（慢而存）——**"记忆放置"取代"模型选择"成为架构师的核心决策变量**
3. **动态工作流（Claude 写编排）是 50%→100% 的自动化跳板**：人写编排→AI 写编排，16 并发/1000 上限的 fresh-context 模式已被 Bun 移植实证——**编排本身也在被 Software 3.0 化**
4. **Git 形态面临 agent 时代的压力**：AgentHub 虽转私，"无主线 DAG+遍历搜索图"的理念已在 Anthropic 动态工作流中借尸还魂——**版本控制的下一代形态是图查询而非分支合并**
5. **对个人研究者的可复制性极强**：autoresearch 单 GPU/630 行/四条件——**"环境工程"取代"调参天赋"成为个人能上牌桌的技能**（与 DeepLoop 的小规模可复现趋势同向）

## 五、关联分析（对自有体系 + 既有笔记链）

> 关联对象：Grok Bot 三层架构笔记 / Hermes 架构（Gateway/skills/cron/delegate）/ AGENTS.md / 前苹果设计六技法 / agent 技能群

1. **与 Grok Bot 笔记构成"同一张地图的两次标注"**（昨日笔记，最直接对照）：
   - Grok Bot 的 harness/loop/graph 三层 = Karpathy 五级阶梯的 50%/70%/100% 三级的产品化命名
   - **两文独立收敛到同一结构**（xAI 产品实践 vs Karpathy 教育叙事）——交叉验证了"模型→系统"的架构共识
   - 差异点：Karpathy 多出的 10%/30% 两级（LLM=裸机/Prompt=编程语言）把**Software 3.0 认识论**补齐了——Grok 文讲"怎么建 OS"，本文讲"为什么 OS 是剩下的 90%"
2. **五级阶梯对 Hermes 自身的定位审计**：LLM（provider 层）✓ / Prompt（skills 即 Software 3.0 模块——"安装 skill=把 3.0 模块装进上下文窗口"）✓ / Agent（tools+memory）✓ / Loop（cron+watchdog+验证脚本）✓ / **Graph（delegate_task+session_search+memorygraph MCP 已有雏形但未成"共享记忆图"）**——自有体系当前在 70% 级，100% 级的差距=**跨会话带出处的共享状态**
3. **autoresearch 四条件 vs 自有验证门禁**：可验证（notes_7module_check/退出码）✓ / 可逆（git/备份）✓ / 短反馈（cron 周期）部分 / 有界（权限三层）✓——**"反馈周期短"是相对最弱的一项**（长训对齐关机窗口的做法正是在补这项）
4. **与"前苹果设计六技法"的挑刺官同构**：Loop 级"输出可验证"=设计篇"及格线不泄露+独立评审"——**验证独立于生成**在三域（设计/代码/研究）三验
5. **memorygraph MCP 工具的直接对标**：自带 create_relationship/recall_memories 的图记忆工具正是"agent 读写共享图"的现成接口——**Karpathy 的 Graph 级在自有工具箱里已有 80% 部件**（缺的是带出处的实体类型化 schema）
6. **与 MeowBot 灵魂的" Accountability Loop"对应**：周审计/receipt=Loop 级的验证；error-case-library=轻量知识图谱（带根因/症状/解法的结构化条目）——**自有体系早已在做图工程的事，缺的是统一命名与互链**
7. **对 DUCK-Pi_5 训练管线的启发**：autoresearch 的"锁 prepare.py 防作弊"与 RL 训练的"锁评测协议防 reward hack"同构——站桩鸭检测=四条件中"输出可验证"的实装

## 六、指南分析

| 场景 | 查哪节 |
|------|--------|
| 快速理解五级 | §1.1 阶梯图 + §1.2 讲座级定义 |
| 搭自改进循环 | §1.3 autoresearch 四条件 |
| 设计 agent 协作 | §1.4 AgentHub DAG + Anthropic 三层 |
| 记忆架构选型 | §1.5 记忆放置总表 |
| 何时上 Graph | §1.6 决策指南 + 三问 |
| 风险控制 | §1.5 危险清单 + 七重追溯 |

**核心口诀**：百分比=系统占比非时间表 / 四条件让环境自治 / 锁评测面防作弊 / agent 会忘图不会 / 用最少架构 / 人类保留定义"好"。

## 七、拓展应用推荐

- **给 harness-architecture / agent-orchestration-pattern**：补 Karpathy 五级作为"系统化程度"的度量轴；autoresearch 四条件作为 Loop 级检查清单
- **给 memorygraph 使用规范**：Anthropic cookbook 的"Haiku 抽取+Sonnet 消歧+答案引用边"三段管线可直接抄为 memorygraph 工作流
- **给 DUCK-Pi_5 / 训练任务**：autoresearch 式"锁 prepare/开 train/program.md 规格"三分离可作长训自治模板
- **延伸阅读**：Karpathy 斯坦福讲座原片 / autoresearch repo（社区 fork）/ Anthropic《Building Effective Agents》/ knowledge graph cookbook / Latent.Space swyx Software 3.0 分析

---

→ 相关：[[2026-09-06-GrokBot智能体操作系统三层控制架构-从Harness-Loop-Graph到审批边界的完整设计.md]]（同一地图的产品实践版，两文交叉验证）
→ 相关：[[2026-09-04-前苹果设计师的AI网页设计六技法-打碎Token平庸惯性的双钻三阶段工作流.md]]（验证独立于生成的设计域验证）
→ 相关：[[2026-09-03-RSI递归自我改进全景-AI造AI的三闭环进化机制与从理论到工程的演进地图.md]]（Loop 级的自动化版——self-improvement 谱系）
→ 相关：[[2026-09-05-DeepLoop循环Transformer深度扩展-访问对齐系数与残差缩放指数修正.md]]（小规模可复现研究范式）

## 相关笔记

- [[2026-09-06-GrokBot智能体操作系统三层控制架构-从Harness-Loop-Graph到审批边界的完整设计]] — Harness-Loop-Graph 三层架构同构
- [[2026-09-07-CLangXOR神经网络六版演进-从74行入门代码到教学级深度学习框架底座]] — 对话式共建工件实例
- [[2026-09-07-Agent记忆架构2026之争-文件系统74分打脸专业记忆栈与Mem0三信号融合反击]] — Graph 工程的记忆层落地争议
