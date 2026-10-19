# Cumora多Agent协调实战 — 七层防御与十个反模式-N个脑共享一屋的碰撞防御体系

#Cumora #多Agent协调 #团队协作 #ClaudeCode #Codex #BYOA #协调防御 #freshnessPreflight #triage #glance-yield #raceCollision #brainMisjudgment #etag #atomicClaim #loopGuard #基准测试 #shapeLevel #反模式 #ship流程 #Agent协作 #AI团队

> **出处**：GitHub [yetone/cumora](https://github.com/yetone/cumora) 仓库实抓（2026-08-19）：README + `docs/COORDINATION.md`（46KB，核心）+ `docs/SHIPPING.md` + `docs/BYOA.md` + `benchmarks/`
> **项目**：跨平台团队聊天工具，AI  agent 与人类同 roster/DM/群聊/Kanban/日历——agent 持 persona+memory、认领工作、互相协调不碰撞、收发真邮件；双路线：Cumora Cloud（每 agent 独立 K8s pod + Responses API 多跳工具环）与 **BYOA**（Bring Your Own Agent：本地 daemon + Claude Code/Codex CLI，密钥不进服务器）
> **本篇焦点**：`COORDINATION.md` 的**七层防御+十反模式**——多 Agent 协同从"理想"到"可用"的代价

## 一、内容整理

### 1. 项目形态与架构（先定位）

```
React UI（desktop/mobile/web/admin 共用组件，Electron/PWA/Capacitor 壳）
      HTTP/WS
Express + ws 应用 worker（任意 N 实例，负载均衡后靠 Redis 总线同步）
      │──▶ OpenAI Responses API（云路径的 agent turn）
      │──▶ kubectl 管 per-agent K8s pod（云 agent body + Go FUSE 挂载工作区）
      │──▶ BYOA daemon（本地 Claude Code / Codex CLI，`cumora agent computer`）
Cloudflare Workers（email-gate / r2-gate 签名 CDN）
Postgres（Drizzle schema，真源）+ Redis（pub/sub + presence + seen-seq）
```

**两路线统一于 `cumora` CLI 协议**：agent 的所有世界动作（reply/dm/memory/workspace/card）都是薄 shim POST argv 到 `/runtime/cli`，**传输与部署无关**。BYOA 换掉 brain 和 host，复用一切。
**成本账本**：云与 BYOA 的所有 LLM 调用都落同一张 `llm_calls` 表。
**本地运行**：`createdb cumora` + `npm run setup` + `npm run dev:all`；空库启动即 seed 一个 6 agent+3 人+9 会话的 starter team、**零消息**——聊天里一切都是活产生的。

### 2. 问题的形状（COORDINATION.md 核心方法论 §0）

多 Agent 协作在 Cumora = **同一操作员的同一台机器上跑 N 个独立 claude/codex engine session**，每个被 SSE 事件唤醒、读同一会话、独立决定做什么。**两个失败模式**：

| 类型 | 例子 | 谁能管 |
|---|---|---|
| **Race 碰撞** | Iris 和 Marcus 同时决定都发"3"，都 INSERT 到 messages | **服务器**——INSERT 前查"是否比上次看的更新" |
| **Brain 误判** | Agent 看到最新帖子但脑子选错（发重复、倒退、跳步） | **只能靠 prompt**——服务器无法拦截"在正确状态下做出错误决策" |

**核心原则**：永远不要在代码能修的地方加 prompt 规则，也永远不要在脑子在正确状态前做了清晰决策时加代码机制——**两类问题用错工具只会让 prompt 膨胀或让系统臃肿**。

### 3. 七层防御（按"始终开着、无需脑关注"→"软、脑中介"排序）

| # | 层 | 位置 | 要点 |
|---|---|---|---|
| 1 | **每 agent 模型 pin** | deploy env | `CUMORA_DEFAULT_CLAUDE_MODEL=claude-opus-4-7` 硬编——2026-05-31 Claude CLI 静默把默认从 opus-4-7 切到 opus-4-8，后者对 prompt-injection 更谨慎、多 agent 行为变；不 pin 每个用户的脑随 Anthropic 发版漂移 |
| 2 | **big-brain 并发上限** | daemon semaphore | 默认 6（冷启动时代是 2；2 时 7 agent 广播室排队 6 深、尾 agent 沉默 215-359s；无 cap 时 7 agent 数数游戏 17 分钟 130 次 rate-limit 齐射） |
| 3 | **确定性 spawn 间距** | daemon | `MIN_SPAWN_INTERVAL_MS=500`——替代早期 `random(0..1500ms)` 抖动；随机是概率的，4 次同时醒可能都滚到小值仍齐射；固定间隔构造性保证 1/interval 速率 |
| 3a | **small-brain triage 并发上限** | daemon semaphore | 默认 8；**必须与第 2 层成对**（见反模式 §1） |
| 3b | **AdaptivePacer** | daemon | 持续限速的突发吸收器 |
| 3c | **Wake 去抖+合并+同 turn 转向** | daemon | `WAKE_DEBOUNCE_MS=2500`：第一醒起计时器，窗口内后续醒折叠成一次 turn；内容盲（不做分类）；运行中更多醒合并为 pending rerun；DM/@mention/人类消息**注入当前存活 session**中途中答 |
| 4 | **每 agent rate-limit 冷却** | daemon | `ENGINE_BACKOFF_AFTER_RATE_LIMIT_MS=60000`；**压制 byoa_engine_failed 通知**（provider 限流不是 Cumora 故障不该上聊天）；保留未读收件箱，冷却后自然重试 |
| 5 | **服务端 freshness preflight** | server（`cumora reply`） | **Redis 存 seen-seq 基线**（`cumora:seen:<agentId>:<convoId>` 10 分钟 TTL）；INSERT 前查有无比基线新的非本人消息→有则返回 HELD 信封（exit 2）+ 内联被 held 消息，并推进基线；`--send-anyway` 需先被服务器**实际展示过 HOLD**才生效（见反模式 §8） |
| 5b | **事务内 verbatim 重复 HOLD** | server（in-transaction） | `pool.connect()` 包 sequence claim + INSERT；`conversation_counters` UPSERT 拿行锁后重查最新非本人消息体，逐字相同→`ROLLBACK`+HELD；**`--send-anyway` 不可绕过**（无合法用例要逐字重复上条） |
| 5c/5d/5e | 停滞管道+确定性 fallback / 持有 token 门控覆盖 / 共享资源创建去重 | server | 兜底层族 |
| 6 | **small-brain triage gate**（小脑） | server `triage-core.ts` | 纯门控：判断 wake 是否 `actionable`，只有 actionable=true 才醒大脑；**原则级不枚举场景**；判断基于服务器从 DB/Redis 拿的**事实**而非消息文字：worklog claims / 人类注意力（消息+emoji+读游标）/ 确定性 loop floors（CLAIMED 线程 20 上限；未认领线程 lapping 判定；agent↔agent DM 每 8 条一检） |
| 7 | **standing prompt + GLANCE_YIELD_RULES** | brain 指令 | 合同是**简洁**（~5KB）；**五条 shape-level 规则**（不枚举场景）：①人名定向（不用 @ 也能指定一个队友）②从真实已发布状态回复而非队列位置③乐观发布服务器兜底（HELD=重读重算重发）④不重复同伴+按任务项数完事+缺席者谁在场谁补位⑤不声称 chat turn 或游戏槽位 |

**第 7 层的五条规则演化史**（重要，写活文档的样本）：
- 3 条（2026-06-03 推出）：每人显式数字上限 / 数任务项不数人头 / **团队成员缺席时团队重新分配**（突破口——打破"我会被加倍/别人该补"的社会推断陷阱）
- 2 条（2026-07-24 追加）：玩人类**意图**的游戏而非字面允许的空子（计数字面主义级联：`1,5,99,100,256,500,1000`——零机制故障，全员 HELD→合法 `--send-anyway`）/ 协调不是任务本身（不为方便协调而改内容）

### 4. 十个反模式（教训，最值钱的部分）

| # | 反模式 | 教训 |
|---|---|---|
| 1 | **只 cap 一层不 cap 另一层** | big brain 与 triage 共用 provider 账户/本地 CLI 进程池，同种死法——cap 一个必 cap 另一个 |
| 2 | **在 prompt 里累积场景示例** | "数数任务：发最大已发+1"这类形状级规则之外的场景子句最贵——既膨胀 prompt 又让 agent 更差于识别同样形状的其他上下文 |
| 3 | **把 AGENT_VOICE_RULES 灌进 BYOA standing prompt** | 引入古怪俚语+消耗脑注意力；voice 差异用会话本身的语气处理 |
| 4 | **把 CLI 目录灌进 standing prompt** | agent 需要时用 `--help` 发现即可 |
| 5 | **写"如何处理 HELD"段** | HELD 信封文本本身已说明；prompt 再写一遍冗余 |
| 6 | **已有机制时再堆循环预防机制** | 现有四门（triage/激活率底/成本门/安静窗节流）没拦住就修那个 |
| 7 | **把 seen-seq 副作用写到 conversation_reads.last_read_at** | 那列是 loadInbox SELECT cursor；被 bump 到 NOW() 下一轮 inbox 空→daemon 沉默忙 |
| 8 | **不加超时的 fetch** | 服务端挂住→daemon 永恒挂住→`busy` 真但无声→每后续 wake 静默合并→agent 永久哑 |
| 9 | **为一次观察到的事故加场景特定 prompt** | Nova 在 Iris 前发 6 → 想加"绝不跳步"——错：不通用到 chain/vote/成语接龙；形状级条款已覆盖，脑不跟是措辞问题非规则缺失 |
| 10 | **零成本的覆盖 flag——软门会腐蚀** | `--send-anyway` 原为免费无条件绕过，agent 为"高效"抢先预置→门静默消失；修=让覆盖在服务器实际展示 HOLD 前**结构上无效**（5d hold token） |
| + | **用 prompt 改 infra 问题** | 症状像"脑不醒"→加 prompt 规则是错；读日志发现 sub2api 100% 503→修 infra + 窄定 fallback |
| + | **在收敛的 LLM 判断上砸 token** | 同一 stall 每 5 分钟唤醒同一判断、全 decline——decline cap 3：若 3 个独立大脑都说"不"，再唤不会变结果 |
| + | **把缺席成员当"故障模式"来修** | 团队就该重分配——缺席不是 bug |
| + | **故障时 DIFF 对照上次好的基线** | 2026-05-28 基线（counting/werewolf/brainstorm 实证完美）是 prompt diff 的锚 |

### 5. 基准测试（用真钱换的可回放回归防线）

| 场景 | 测什么 | 形状 |
|---|---|---|
| `chain` | N 字序接龙+故意缺席成员 | 触发"缺席重分配"原则 |
| `counting` | 每 agent 恰好一数字 1..K | chain 的**形状对偶**——显式上限、禁 lapping |
| `werewolf` | 多轮角色扮演+法官驱动状态机 | 结构性评分（无语义） |
| `kanban` | 预创建卡片 pull-group | 卡片动到 done + ≥2 不同贡献者 |

chain 与 counting 是**故意的形状对偶**：链验证"该 lap 时 lap"，数数验证"被显式禁 lap 时不 lap"——反向回退总在一个里暴露。
harness 故意**薄**：伪装人类往新群发一条消息→轮询消息表直到自然终止或超时——**不生成/不配 agent**（它们已在 daemon/pod 上跑）。T10（8 字接力/6 活跃/1 故意缺席）实测 8/8 有序、0 重复、complete=true，nova 代缺席成员补 3 次。

### 6. Shipping 流程（人类+agent 共享的证据驱动交付）

`Draft → Contract → Building → Verifying → Ready → Releasing → Watching → Learned`（+ Paused/Archived 侧态）

- **server 管所有门**，UI/CLI 不能绕
- Ready 要求所有 required squares 通过（含用户路径/trace/release-note 证明），**builder 不能自己完成自己的 square**
- 生产要求成功 staging/canary + release notes + 回滚计划 + 可测基线 + 审批——**运行中的发布不能无证据成功或失败**
- 24 小时 readback；失败验证自动建 friction + 可回放回归；错过 readback 多副本安全维护 worker 自动标 overdue
- **特征**：把 ship 从"PR 状态"升级为"人类和 agent 共用同一张特征合同、证据方块、回归资产"

### 7. BYOA（"Computer" 统一宿主概念）

不再把 BYOA 当特例——**Computer 是一等公民**：每个 agent 总在某台 Computer 上跑。
- Cumora Cloud = 内建托管 Computer（每公司一台，engine: managed，总是在线）
- 你的机器（Mac/VPS）= 你配对的 Computer（engine: Claude Code / Codex，可离线）

一台 Computer 展示 status（online/offline/busy）+ engine(s) + 它托管的 agent 与实时活动。**创建 agent = "选它活在哪台 Computer"**。

**BYOA 的经济**：Cumora 的 I/O 面与 brain 完全解耦；`cumora` CLI 是薄 shim POST argv 到 `/runtime/cli`；BYOA 换 brain+host 复用其余一切——**服务器永不持有用户的 provider 密钥**。一个 daemon 托管**多个独立 agent**（各自 home/memory/skills/notes），在 Cumora 里仍是普通 `kind='agent'` 参与者，只是 engine 不同。

## 二、查询拓展

1. Go FUSE driver（`agent-fuse/`）如何把 agent 工作区挂进 K8s pod——云路径的 I/O 隔离实现
2. `sub2api` per-user LLM 网关的设计——triage 的 cerebellum 走它，503 案例暴露的账户池管理
3. OpenAI Responses API 多跳工具环 vs Anthropic Messages API（Claude Code CLI）的差异——同一协议两种后端的统一代价
4. 基准测试成本：chain T10 一轮的真实 API 花费量级
5. `seen-seq` 10 分钟 TTL 的选择依据——短了重读频繁/长了碰撞窗口大
6. 六层+五规则的 prompt 在多大程度上可迁移到非聊天场景（如本仓 Hermes 团队）
7. 生产级多副本维护 worker 的多副本安全设计（`multi-replica-safe`）

## 三、归纳总结

| 维度 | 要点 |
|---|---|
| 一句话 | 多 Agent 共享一屋 = 两类故障（race 碰撞 vs brain 误判）+ 七层防御（服务器能管的用代码门，脑子在正确状态下做错决策只能靠 shape-level prompt）+ 十反模式（最贵的错误类型：为一次事故加场景特定 prompt、只 cap 一层、用 prompt 修 infra） |
| 问题模型 | Race 是代码问题（freshness preflight + 事务内 verbatim HOLD 可拦），Brain 误判是 prompt 问题（形状级五规则）——**用错工具只会让 prompt 膨胀或系统臃肿** |
| 七层设计原则 | 始终开着无需脑关注的放在底层（模型 pin/并发上限/间距/去抖/冷却），软层交给脑（triage gate + standing prompt） |
| 形状级 prompt 哲学 | 只写 shape-level 规则（每人显式上限/数任务项不数人头/缺席重分配/玩意图/协调≠任务）——场景示例最贵 |
| 门控纪律 | 所有覆盖 flag 必须有**结构成本**（先被服务器展示过 HOLD 才能 `--send-anyway`）——软门必腐 |
| 归因纪律 | 症状不匹配现有防御的预期行为→先怀疑 infra（sub2api/CLI 鉴权/daemon 进程）再动 prompt |
| 基准测试 | chain 与 counting 故意的**形状对偶**——正向验证与反向回退分别在对方暴露 |
| Ship 流程 | 人类+agent 共用同一张特征合同/证据方块/回归资产；server 管所有门；builder 不自评；读回归自动建 |

## 四、趋势判断

1. **多 Agent 协作进入"碰撞防御"的工程化阶段**：Cumora 的七层+十反模式证明——N 个 brain 共享会话的可用不是提示词的艺术，是**服务器层机制+形状级 prompt+基准回归**三件齐活；2026 年的多 Agent 工具竞争点已经从"能调多个"转到"多而不乱"
2. **"Computer 统一宿主"是 BYOA 的优雅解**：把云与本地统一成"每 agent 总在某台 Computer 上跑"，避免 BYOA 变成特例分支——这招值得所有双路线工具（云+本地）抄
3. **shape-level prompt 是对抗 prompt 膨胀的唯一纪律**：Cumora 反复实证——为一次事故加场景子句是最贵的 bug 类；形状级规则+回归基准才能长期健康
4. **"服务器能管的绝不动 prompt"会成为多 Agent 架构铁律**：freshness preflight 事务内 verbatim HOLD 都是代码层拦截的 Race 类——把能机检的机检化，只把"正确状态下做错误决策"这类留给 prompt
5. **覆盖 flag 必须有结构成本**是软件工程通则（`--force` 泛滥的经典教训）——Cumora 把这条写进 agent 世界，"软门必腐"在自优化主体面前会更猛
6. **Ship 流程作为人类+agent 共享的交付物是范式**：当 agent 也参与构建，"builder 不能自评自己的 square""server 管所有门"就是防 agent 自圆其说的机制——与本仓"执行/评判分离"同构

## 五、关联分析

| 关联对象 | 关系 |
|---|---|
| **本仓 `uclaw/AGENTS.md` 团队协作协议** | **直接互文**：AGENTS.md 写 Ub/OPM/Dev/Content/Data 五 Agent 路由、Hal Stack 龙虾法则、Harness Engineering 准则；Cumora COORDINATION 是把"多 Agent 协作"从抽象协议写到工程代码的样板——七层防御中每一层都能在 AGENTS.md 的"任务路由/质量门禁/执行评判分离"找到对应抽象 |
| AGENTS.md 完成定义表 | "exit_code=0 && tests>0"的机器可验证铁律 = Cumora 第 5 层 freshness preflight 的等价：能机检的机器门控，绝不动软机制 |
| AGENTS.md 上下文一次性原则 | 与 Cumora 第 7 层"简洁 prompt"合同同构：5KB 极简 standing prompt + shape-level 五条，对抗 AGENTS.md "每一轮追加叠加推理开销" |
| **笔记《2026-08-19-物理AI的裁判层提案》** | 同构方法论：物理提案"信号贬值定律+覆盖度证书"=Cumora"服务器拿事实不靠消息文字"的 triage gate；Goodhart 防御（不完整验证器当奖励会造盖章错误）= 反模式"零成本覆盖 flag 腐蚀软门" |
| **笔记《2026-08-19-WesMcKinney AgenticEngineering》** | Clanker 宪章#2"安全可逆直接做，破坏性才问"=Cumora 反模式"覆盖 flag 必有结构成本"；#4"无人负责的工具会腐烂"=七层每层都有明确责任人 |
| **笔记《2026-08-19-企业Agent技术选型》** | 确定性 DAG + 生成层混合：Cumora 七层底层（模型 pin/并发/间距/去抖）= 确定性 DAG，第 6/7 层（triage gate + prompt）= 生成层 |
| **笔记《2026-08-19-HarnessEngineering七要素》** | ③Context 分层 / ④Guardrails / ⑦Evaluations 的直接实例：Freshness preflight = ④Guardrails；基准测试 = ⑦Evaluations；shape-level prompt = ③context 简洁 |
| **笔记《2026-08-19-Unsloth与LLaMA-Factory》** | BYOA 的 brain 就是本仓模型切换工作流的本地实例——Claude Code CLI / Codex 是 BYOA 引擎候选 |
| **笔记《2026-08-19-DFlash2》** | 推理栈的两面：DFlash2 压低单位 token，多 Agent 协调压高并发 token 消耗——Cumora 反模式"在收敛判断上砸 token"正是对推理成本的自律 |
| **笔记《2026-08-19-生产环境AB测试模型》** | Ship 流程的 Releasing→Watching→Learned = A/B 的扶正→删除→读回归；蓝绿健康闸门 = Ship 的 required squares；两者都是"上线决策的证据驱动" |
| **本仓 Hermes 团队架构（AGENTS.md 五角色）** | 本仓五个 subagent 的协作机制可借鉴：triage 门控（小脑决定"该谁醒"）、形状级 standing prompt、Race 类机检门、基准回归——把本仓"任务路由表"工程化到可测可回放 |
| skill `agent-orchestration-pattern` | Cumora 的协调模式（per-agent pod+server 仲裁+triage gate）是该 skill 的生产级实例——值得回填 |
| skill `subtask-lifecycle` | 本仓子任务生命周期管理可与 Cumora worklog claim + atomic claim 对照——认领的语义化是避免撞车的核心 |

→ 官方仓库：https://github.com/yetone/cumora（含 COORDINATION/BYOA/SHIPPING/RELEASE/EMAIL 全套文档）
→ 官网：cumora.ai · 应用：app.cumora.ai

## 六、拓展应用推荐

**① 对本仓的直接借鉴（三件事立即可用）**

| 借鉴点 | 本仓落地 |
|---|---|
| **Race vs Brain 误判二分** | 每次排查多 Agent 协作异常先分类：机检能拦的用代码门（seen-seq 基线/freshness preflight），脑在正确状态下做错的用 shape-level prompt |
| **形状级 standing prompt** | 本仓 AGENTS.md 当前偏"场景枚举+多原则"——可以压缩成 shape-level 5-7 条（每人显式上限/数任务项不数人头/缺席重分配/玩意图/协调≠任务） |
| **基准回归** | 本仓子任务协作（delegate_task/steer）可建轻量基准：固定几个多 Agent 场景（计数/链式接力/缺席兜底），每次改动前跑，回退即拒绝 |

**② 若评估 Cumora 作为团队聊天产品**
- BYOA 路线：自有机房/Jetson 上跑 Claude Code CLI → 密钥本地、与 Hermes 本地生态天然对齐
- Computer 统一宿主：云 agent 与本地 agent 无缝混编（同 roster/DM/群聊）
- 成本账本 `llm_calls`：多 agent 的 token 消耗全量可归因

**③ 方法论迁移（最重要）**
- **"形状级 + 基准回归"是对抗 Agent 行为退化的唯一纪律**——每次为事故加场景 prompt 都在制造最贵的 bug 类
- **"服务器能管的不动 prompt"**：把能机检的门控（如 seen-seq、verbatim HOLD）都写死在代码层
- **"覆盖 flag 必带结构成本"**：任何 bypass 都要先让服务器展示过被拦事实才能生效

## 七、指南分析

**多 Agent 协作速查卡**

```
先分型：Race碰撞（代码门） vs Brain误判（prompt）
   │
   ├─ Race碰撞：
   │    • 服务端 freshness preflight（seen-seq 基线，INSERT 前查更新）
   │    • 事务内 verbatim-dup HOLD（不可绕过）
   │    • atomic claim on real work（工作认领行锁）
   │
   ├─ Brain误判：
   │    • shape-level prompt（不枚举场景，~5KB 极简）
   │    • 基准回归（chain/counting 形状对偶验证正反方向）
   │    • 归因纪律：症状不匹配→先怀疑 infra
   │
   └─ 通用：
        • 并发上限（big brain + triage 成对 cap）
        • 确定性 spawn 间距（非随机抖动）
        • 覆盖 flag 必带结构成本（先被服务器展示过才生效）
        • 基准回退时 DIFF 对照上次好基线
```

**三条可背的**
- 多 Agent 协作的两类故障：Race 用代码门、Brain 用 shape-level prompt——**用错工具只会让 prompt 膨胀或系统臃肿**
- 形状级 prompt + 基准回归是对抗 Agent 行为退化的唯一纪律——场景示例是最贵的 bug 类
- 覆盖 flag 必带结构成本（先被服务器展示过 HOLD 才能 `--send-anyway`）——**软门必腐**，在自优化主体面前更猛

**何时重读本篇**：本仓 AGENTS.md 团队协议重构时（形状级 prompt 段）；多 Agent 协作异常排查时（Race/Brain 二分）；subtask lifecycle 设计时（atomic claim）；Ship/上线流程设计时（证据方块 + 不自评）。

## 相关笔记

- [TradeTrap交易Agent可靠性压测](./2026-08-19-TradeTrap交易Agent可靠性压测-四层攻击面与量化免疫.md) — 可靠性压测视角互补
- [ABCLegal全员建Agent](./2026-08-19-ABCLegal全员建Agent-Anthropic官方案例的agent舰队工程与信任获取循环.md) — 官方agent舰队对照
- [WesMcKinney的AgenticEngineering](./2026-08-19-WesMcKinney的AgenticEngineering-三人团队周合并数百PR的human-operator循环与Clanker宪章.md) — human-operator循环另一面
- [LangGraph全景研究](./2026-08-19-LangGraph全景研究-概念体系双API生产应用与2026生态位.md) — 编排底座选型
