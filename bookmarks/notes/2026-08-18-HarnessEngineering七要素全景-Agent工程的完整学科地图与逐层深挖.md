# Harness Engineering七要素全景 — Agent工程的完整学科地图与逐层深挖

#HarnessEngineering #Agent工程 #Context管理 #Workflow循环 #State #SubAgents #权限沙箱 #可观测性 #评估 #自我改进 #控制平面 #Agent工程学科化

> **出处**：用户提供的方法论框架（2026-08-18）——Harness Engineering 七要素清单：
> Context（prompts/tools/actions/memory）· Workflow/loop · State · Sub-Agents/Agent Teams · Permissions & sandboxing · Observability & Evaluations · Self-improvement
> 研究补充：本仓 harness-architecture（六层架构+Externalization 理论+腾讯生产八模块）、agent-orchestration-pattern（Beam AI/Deloitte/STAR 数据）、deterministic-guardrails、以及 2026 H2 "Harness = Control Plane" 行业共识
> 主题：把七要素逐个展开成可落地的设计问题、方案选型与坑点——一张 Agent 工程的完整学科地图

## 一、内容整理

### 0. 框架总览：七要素是什么关系

Harness Engineering 的定义：**模型是数据平面（执行推理），Harness 是控制平面（约束、路由、验证、回滚、监控）**——生产级 Agent 成败 90% 取决于控制平面。七要素就是控制平面的七个Subsystem：

```
┌─────────────────────────────────────────────────────┐
│              Harness = Agent 的控制平面               │
├─────────────────────────────────────────────────────┤
│ ① Context        模型看到什么（输入侧）               │
│ ② Workflow/loop  模型下一步做什么（调度侧）           │
│ ③ State          跨步骤连续性（时间侧）               │
│ ④ Sub-Agents     谁帮模型做（组织侧）                 │
│ ⑤ Permissions    模型被允许做什么（安全侧）           │
│ ⑥ Observability  怎么知道做得对不对（验证侧）         │
│ ⑦ Self-improve   怎么越用越好（进化侧）               │
└─────────────────────────────────────────────────────┘
```

七要素与六层架构（本仓 skill）的映射：①=上下文管理；②=执行编排；③=状态与记忆；④=编排模式的组织形态；⑤=约束与恢复的安全半区；⑥=评估与观测+恢复的检测半区；⑦=六层之外的进化维度（Self-Evolving Harnesses 前沿）。

**一句话**：①决定上限，②③决定能否长跑，④决定能否扩展，⑤决定炸不炸，⑥决定能不能信，⑦决定会不会越用越好。

### 1. Context（上下文：prompts / tools / memory）

**设计问题**：模型每次推理看到什么、看多少、以什么结构。

**三个子件**：
- **Prompts**：system prompt（身份/边界/输出契约）+ 任务 prompt。Anthropic Poka-yoke 原则：工具描述要当"给初级开发者的 docstring"写（示例/边界/格式/与其他工具的边界）
- **Tools/actions**：模型可见的行动空间。**15-tool ceiling**：单 agent 工具>15 个，调用准确度 F1 断崖下跌（39-70%）——必须拆分专有工具集
- **Memory**：跨会话的持久信息（用户偏好/项目事实/经验）。与 Context 的关系：memory 是被选择性注入 context 的外部存储

**核心矛盾与解法**：

| 矛盾 | 解法 |
|---|---|
| 全量灌入→注意力稀释 vs 缺上下文→瞎猜 | 分层按需加载（L1 常驻/L2 按需/L3 查询），"不多不少刚好够" |
| 长任务 token 膨胀（1.59亿/80万=200倍浪费） | 压缩=投影不删除：日志全量、模型可见历史受控（DeepSeek Harness 压缩模型） |
| 历史相关性衰减 | Agent-Radar 时空衰减：时间指数衰减×语义相关性加权 |
| 多源记忆冲突 | 选择性 QA：证据融合+弃权机制（冲突时宁可弃权） |

**MCP 成本警示**：MCP 工具 schema 加载 32K-82K token vs CLI 等效操作 200 token——工具接入方式本身就是 context 决策。

**坑**：上下文过载（质量下降）；自评失真的温床（自己看不到自己的盲区）；prompt injection 面（不可信内容混入 context——检索片段当数据不当命令）。

### 2. Workflow / Loop（工作流与循环）

**设计问题**：单步执行循环长什么样，多步怎么编排。

**微观循环（二十行心脏）**：
```
while not done:
    response = model(context)          # 模型提出下一步
    if tool_call := parse(response):   # 工具调用
        result = execute(tool_call)    # 执行
        context.append(result)         # 回填
    else:
        return response                # 完成
```
循环不需要智能——工程量全在循环外（DeepSeek Harness 二十万行的启示）。

**宏观编排（谱系而非二元）**：

| 模式 | 确定性 | 适用 | 失败模式 |
|---|---|---|---|
| 固定 DAG（LangGraph） | 最高 | 高风险主流程 | 死板，探索性框不住 |
| Workflow 包 Agent | 高 | 生产标准形态：触发→分诊→**Agent调查**→结构化→评估→通知 | 分诊错误路由错 |
| Plan-and-Execute | 中 | 复杂任务先规划后执行 | 计划脱离实际 |
| ReAct 自由循环 | 低 | 探索性任务 | 死循环/冗余（61-93% 推理步骤冗余） |
| Supervisor 编排 | 中 | 宽并行任务（+80%效率） | 强顺序任务上下文碎片化（-39~70%） |

**关键数据**：Sequential Pipeline 4-agent 协调开销 950ms vs 实际处理 500ms；3 agent 29K token vs 单 agent 10K。**并行工具调用**（LLMCompiler 3.7x）与**投机执行**（PASTE 降 48.5% 延迟）是微观循环的性能优化层。

**坑**：无终止条件的循环（每个 agent 必须有不可绕过的 max_iterations）；早停 vs 深思的预算平衡；循环内冗余检测（连续相同 thought+action+observation=幻觉信号）。

### 3. State（状态）

**设计问题**：跨步骤/跨会话/跨 agent 的连续性怎么保持。

**三层状态**：

| 层 | 内容 | 载体 |
|---|---|---|
| 会话内 | 消息历史、中间结果 | context + 检查点 |
| 跨会话 | 任务进度、可恢复断点 | checkpoint 文件（harness-checkpoint 模式） |
| 长期 | 知识/偏好/经验 | memory（L1/L2/L3 分层） |

**不变量设计**（DeepSeek Harness 的核心贡献）：**日志全量 vs 模型投影分离**——会话日志只增不删（审计/恢复/重放的依据），模型可见历史是投影（可压缩可遮蔽）。关掉"模型可见必先进日志"不变量，恢复/审计/重放立即失联。

**状态机化**（高德 OPC 模式）：DISPATCHED→ACKED→RUNNING→SUCCEEDED/FAILED，辅以 TIMED_OUT（300s 未 ACK）/STALLED（1200s 无进展）/BLOCKED（风控）。每步有 condition 前置条件，防跳步。

**断点恢复**（ScienceFlow 思想）：长任务拆带可执行状态的存档段——ESTRA 决定从 live 还是 archived state 续接；evidence-aware 按已验证进展分配算力。

**坑**：状态分散多处（DB+文件+内存）不一致——以仓库为准原则；崩溃后从头重跑（无 checkpoint）；状态膨胀无清理（memory 需要 consolidation 定期整理）。

### 4. Sub-Agents / Agent Teams（子代理与团队）

**设计问题**：什么时候拆、怎么拆、拆完怎么合。

**SubAgent vs Agent Teams**：

| | SubAgent | Agent Teams |
|---|---|---|
| 通信 | 互相看不到 | 可互发消息、共享任务列表 |
| 适合 | 结果导向并行任务 | 需要反馈协商的任务（质检/评审） |
| 开销 | 省 token | 高 |

**拆分判据**：15-tool ceiling（工具数）；领域差异（编码/评审分离——执行/评判分离原则）；并行收益（4+ 独立任务削减 75% 墙钟时间）。**并行上限 3 个**（超过错误率显著上升）。

**委派契约**（SearchSwarm 四原则）：鼓励委派/全面简报（目标+约束+已有工作+验收标准）/主 agent 保留核心判断/引用支撑报告。委派行为不会自发涌现，需显式设计。

**反面数据**：多 agent 协作效果可能**低于**单 agent 基线（MoltBook 770K 实验：协作成功率仅 6.7%，Cohen's d=-0.88）；成本复合模型 `总成本(n)=n×C_agent+n²×C_coordination+n×C_error`——3 agent ≈ 10×C_agent。**默认单 agent+丰富工具集，证明协调收益>成本才升级**。

**坑**：幻觉共识（合成者把实际分歧捏造成一致）；孤儿 agent（结果无人消费）；上下文遗漏（子 agent 不知道父级约束——契约式简报解决）。

### 5. Permissions & Sandboxing（权限与沙箱）

**设计问题**：模型被允许做什么、在哪做、错了能不能兜住。

**权限三件套**（确定性护栏）：
- **状态机**：只允许合法状态转换（completed→writeback），InvalidTransition 拒绝
- **权限矩阵**：动作→前置条件集（transfer_funds 需 authenticated+authorized+mfa）——默认拒绝，显式允许
- **审计日志**：哈希链（每条含 previous_hash），不可篡改可验证

**守卫只能否决**（DeepSeek Harness 教训）：类型系统里没有 allow 返回值——若允许守卫主动放行，`bash rm -rf` 能否执行只取决于注册顺序，且无任何异常。**约束的价值只有在删除后才显现**。

**沙箱分层**：只读（查询类）→ 写临时区（生成类）→ 白名单写（受控变更）→ 全权限（永不给 agent）。执行环境隔离：容器化+网络白名单+超时/预算强制终止。

**Lethal Trifecta**（Simon Willison）：私有数据访问+不可信内容暴露+出站通信，三腿同开=数据泄露。**确定性切断腿 3（网络白名单）优先**——不能依赖 AI 判断拦 AI。Action-level 拦截：0.8B 安全分类器 50ms/判断（SingGuard-NSFA 模式），事前静态评估+事中动态拦截互补。

**坑**：过度拦截比不拦截更危险（用户绕过护栏）——benign 误拦率 <5% 是硬指标；prompt injection 防御率仅 ~89%——必须假设注入会成功，设计纵深防御。

### 6. Observability & Evaluations（可观测性与评估）

**设计问题**：怎么知道 agent 做得对、错在哪一步、怎么归因。

**可观测性三层**：
- **Trace**：一条链路贯穿全流程（跨 agent/语言/队列——Worker 模式的实时可观测性）
- **Trajectory Eval**：不只看答案，评估**步骤**是否必要/顺序合理/是否重复循环——只看最终答案会漏掉"用了未授权数据源/调十次无意义工具/重试撞对"
- **遥测仪表盘**：token 消耗/错误率/工具调用分布/任务完成率（On the Loop 的人类界面）

**评估方法谱系**：

| 方法 | 适用 | 要点 |
|---|---|---|
| 确定性测试 | 代码/统计节点 | exit_code=0 && tests>0，机器可验证 |
| 独立 Reviewer | 高质量产出 | Agent Teams 独立核查（写代码的不许自评） |
| Evaluator-Optimizer | 有明确标准的迭代 | 生成→评估→带反馈重生成（≤3轮） |
| 影子对比 | 上线前 | agent 输出 vs 人类结论并行，一致率>80% 才放 |
| 快速失败门 | 评审流水线 | L1 静态（秒级）→L2 语义→L3 动态（分钟级），早层挂了不跑深层 |

**错误归因四分法**（内容缺口/检索问题/生成问题/权限问题）——修法完全不同，别全推给"模型不行"。

**成本观测**：单位业务结果成本（每完成一个合格任务多少钱）是核心运营指标；分级降级（绿>50%正常/黄 20-50% 压缩/红 5-20% 切小模型/熔断<5% 强制收束）。

**坑**：自评失真（自评几乎一定是"还不错"）；只评结果不评轨迹；评测集与真实分布脱节（要含拒答题/权限题/注入题）。

### 7. Self-improvement（自我改进）

**设计问题**：系统怎么从错误和经验中变好，而不是重复犯错。

**进化阶梯**（由易到难）：
1. **错误案例库**：非平凡问题→根因/症状/解法入库，下次先查库（error-case-library 模式）
2. **经验沉淀**：可复用工作流→经验卡片（experience-bank 模式）——解决"第二次问同一件事=系统失败"
3. **Skill 自动化**：≥5 次同类工具调用/同类错误≥2 次→自动建 skill 或 patch 现有 skill（触发式规则）
4. **轨迹分析优化**：分析执行轨迹自动优化编排策略（Self-Evolving Harnesses 前沿）
5. **反思机制**：全量反思（session 结束）+微反思（per-turn 启发式触发）双轨

**Externalization 理论支撑**（arXiv:2604.08224）：Agent 设计核心问题是"多少能力放模型内 vs 外部"——self-improvement 本质是**把经验从模型内部（不可控的权重）迁移到外部确定性结构（skill/memory/protocol）**。

**本仓活样本**：evolver（错误模式分析→规则沉淀→经验闭环）+ auto-skill（任务后自动评估建 skill）+ sensor-grid（质量信号闭环反馈）+ idle-busy-loop（空闲自学习）——七要素中最早被工程化的一个。

**坑**：无治理的自进化=知识库腐烂（错误经验被沉淀）；改进无验证（patch 引入新问题——需 A/B 测试 skill-ab-testing 模式）；反思空转（只分析不执行——"分析完就停"是失败模式，推荐必须同 session 执行）。

### 8. 七要素协同：一个完整的生产形态

以 issue 自动处理为例（接《企业Agent技术选型》笔记）：
```
触发（webhook）
→ ②Workflow: DAG 分类路由（确定性节点）
→ ①Context: 按节点加载该节点的工具+RAG+system prompt（不灌全量）
→ ③State: 每节点 checkpoint+证据存档（ScienceFlow 式），日志全量
→ ④Sub-Agent: "分析判断"节点起子 agent（沙箱+契约+预算，并发≤3）
→ ⑤Permissions: 写回前状态机+权限矩阵+审计链；子 agent 无写权限
→ ⑥Observability: Trajectory eval（步骤必要性）+影子对比（结论一致率）
→ ⑦Self-improve: 错题入 case-library，重复模式→skill，月度轨迹分析调编排
```

## 二、查询拓展

1. 七要素的量化基准——有没有 HarnessBench 类的标准评测（各要素成熟度打分）
2. Context 工程的自动分诊——context 放什么的决策本身能否交给小模型（meta-context routing）
3. State 的 CRDT 化——多 agent 并发写共享状态的一致性协议（对照 agent-file-conflict-detection）
4. Self-improvement 的安全边界——自进化系统如何防止"学坏"（错误经验沉淀的验证门）
5. 权限系统的形式化验证——权限矩阵+状态机的组合能否用 TLA+ 验证不可达危险状态
6. Sub-agent 的 A2A 标准化——跨组织 agent 团队的权限与审计如何互认（Agent Card 安全模型）
7. Observability 的采样策略——全量 trace 的成本 vs 采样的漏检，动态采样率算法

## 三、归纳总结

| 维度 | 要点 |
|---|---|
| 一句话 | Harness=控制平面，七要素=七个子系统：①定上限②③定长跑④定扩展⑤定安全⑥定可信⑦定进化 |
| 共同设计哲学 | 确定性优先：能不用模型决策的地方（路由/验证/权限/统计）就不用 |
| 反复出现的定律 | 15-tool ceiling；并行≤3；守卫只能否决；日志全量-投影分离；执行/评判分离；benign 误拦<5% |
| 成本意识 | MCP 32K-82K vs CLI 200；多 agent 成本 O(n²)；61-93% 推理冗余；单位业务结果成本 |
| 与六层架构关系 | 七要素=六层的重组+进化维度：⑤⑥合并自"约束与恢复+评估观测"，⑦是新增前沿 |
| 学科化判断 | Harness Engineering 正从"高级技巧"变成独立工程学科——七要素就是它的课程目录 |

## 四、趋势判断

1. **Harness Engineering 学科化加速**：七要素清单式知识结构=学科成熟的标志（对照 DevOps/SRE 的成熟路径）；2027 会出现认证/教材/标准岗位
2. **Context 工程成为第一竞争维度**：模型能力商品化后，"喂什么"比"用什么模型"更决定产出——context 分诊/压缩/衰减会专业分工
3. **State 与可观测性走向统一**：日志全量+投影分离 + Trajectory eval 合并成"执行事实层"——审计、恢复、评估、改进共用同一数据底座
4. **Self-improvement 从前沿变标配**：错误案例库/经验沉淀/skill 自动化已是本仓现实——企业级 harness 会内建"改进闭环"作为默认能力
5. **权限与沙箱的监管化**：EU AI Act 类监管要求可审计决策路径——哈希链审计+权限矩阵从最佳实践变成合规必需
6. **"二十行循环"与二十万行 harness 的分工永久化**：模型端做能力涌现，harness 端做确定性保障——两端各自进化互不吞噬

## 五、关联分析

| 关联对象 | 关系 |
|---|---|
| skill `harness-architecture` | 直接母体：六层架构是七要素的前身组织方式；本笔记按用户七要素框架重组并补⑦进化维度 |
| **笔记《2026-08-18-DeepSeekHarness二十万行拆解》** | 七要素的活体解剖：①压缩投影③日志/历史分离⑤守卫七拦截点②二十行循环——四要素在二十万行里的实现 |
| **笔记《2026-08-18-企业Agent技术选型》** | 七要素的企业落地场景：DAG骨架+agent节点=②④的组合决策；灰度四阶段=⑤⑥的实施路径 |
| skill `deterministic-guardrails` | 要素⑤的完整实现模式库：状态机/权限矩阵/审计链/Lethal Trifecta/NSFA |
| skill `agent-orchestration-pattern` | 要素④的数据与模式主库：六编排模式+失败率+成本复合模型 |
| skill `context-engineering-patterns` | 要素①的四大支柱展开（静态动态分离/历史管理/预算检索/输出修剪） |
| skill `harness-checkpoint` / `subtask-lifecycle` | 要素③的落地：断点保存与子任务全生命周期 |
| skill `evolver` / `auto-skill` / `error-case-library` / `experience-bank` | 要素⑦的本仓实现四件套 |
| **笔记《2026-08-18-ScienceFlow》** | 要素③的学术前沿：ESTRA 存档段+evidence-aware 调度 |
| **笔记《2026-08-18-知识库从入门到精通》** | 要素①中 memory/knowledge 的治理面：负责人/有效期/权限进索引 |
| AGENTS.md（本仓） | 七要素的制度化文本：完成定义=⑥；上下文一次性原则=①；Token 70% 断点=②③；三层权限模型=⑤ |

→ 相关：~/.hermes/skills/devops/harness-architecture/SKILL.md
→ 相关：2026-08-18-企业Agent技术选型-全自治vs确定性DAG的混合架构共识与落地设计.md

## 六、拓展应用推荐

**① 七要素自评清单（给自己的 Agent 系统打分）**

| 要素 | 及格线 | 优秀线 |
|---|---|---|
| ①Context | 分层按需加载，不灌全量 | 动态分诊+压缩投影+时空衰减 |
| ②Workflow | 有终止条件+max_iterations | Workflow 包 Agent+并行工具调用+投机执行 |
| ③State | 有 checkpoint 可恢复 | 日志/投影分离+状态机+存档段回退 |
| ④Sub-Agents | 工具≤15 才考虑拆分 | 契约式委派+执行评判分离+并发≤3 |
| ⑤Permissions | 危险操作有确认门 | 状态机+权限矩阵+哈希审计+网络白名单 |
| ⑥Observability | 有 trace 可查 | Trajectory eval+影子对比+错误四归因 |
| ⑦Self-improve | 错误有记录 | 案例库+经验银行+自动 skill+轨迹分析 |

**② 本仓已有可直接复用的组件映射**
- 想加固①→ context-engineering-patterns skill
- 想加固③→ harness-checkpoint + ScienceFlow 的 ESTRA 思想
- 想加固⑤→ deterministic-guardrails 的五模式（抄代码级）
- 想加固⑥→ 三层评审+快速失败（harness-architecture §8）+ notes_7module_check 式门禁
- 想加固⑦→ evolver/error-case-library/experience-bank 三件套已运行

**③ 给团队培训的七讲课程结构**
每要素一讲：概念（10min）→ 本仓活样本（15min）→ 反面数据（10min）→ 自评作业（对团队系统打分）——直接用本笔记各节素材

## 七、指南分析

**实施顺序指南（资源有限时先建哪个）**

```
从零搭 Agent 系统：
① Context（先有输入管理，否则一切白搭）
→ ⑤ Permissions（第二天就要有安全底座，最便宜的保险）
→ ⑥ Observability（没有 trace 的系统无法调试）
→ ② Workflow（稳定后固化循环）
→ ③ State（任务变长时引入 checkpoint）
→ ④ Sub-Agents（单 agent 证明不够用才拆）
→ ⑦ Self-improve（系统稳定运行后才配进化）

已有系统补课（按 ROI 排序）：
⑤⑥ 最常见缺失且最便宜 → ①（context 卫生）→ ③（断点）→ ②④⑦
```

**每要素一句话军规**
- ①：不多不少刚好够——多则稀释少则瞎猜
- ②：每个循环必须有不可绕过的终止条件
- ③：日志只增不删，模型可见是投影
- ④：单 agent 是默认答案，拆分需要证据
- ⑤：守卫只能否决；网络限制必须确定性
- ⑥：写代码的不许自评；只看答案会漏轨迹
- ⑦：分析完必须执行；错误不沉淀必重复

**避坑总表**（七要素各一坑）
| 要素 | 头号坑 |
|---|---|
| ① | MCP schema 32K token 静默吃掉预算 |
| ② | 无终止条件的"勤奋循环"烧钱不产出 |
| ③ | 崩溃后从头重跑（没 checkpoint） |
| ④ | 为拆而拆——协调成本 O(n²) 吃掉收益 |
| ⑤ | 过度拦截→用户绕过→比没护栏更糟 |
| ⑥ | 自评失真："还不错"几乎总是错的 |
| ⑦ | 无验证的自进化=错误经验的复利 |


## 相关笔记

- [LangGraph全景研究](./2026-08-19-LangGraph全景研究-概念体系双API生产应用与2026生态位.md) — Workflow/loop 要素的框架级实现
- [ABCLegal全员建Agent](./2026-08-19-ABCLegal全员建Agent-Anthropic官方案例的agent舰队工程与信任获取循环.md) — 七要素在 1100 人组织的实证案例
- [企业Agent技术选型](./2026-08-18-企业Agent技术选型-全自治vs确定性DAG的混合架构共识与落地设计.md) — 控制平面确定性与自治的取舍
- 上下文管理的 POMDP 形式化（~/explore，2026-08-18）— Context 要素的理论前沿
