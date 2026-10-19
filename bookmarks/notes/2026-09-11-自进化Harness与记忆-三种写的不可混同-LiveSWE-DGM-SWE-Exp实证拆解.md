# 自进化 Harness 与记忆：三种"写"的不可混同——Live-SWE/DGM/SWE-Exp/CODESKILL 实证拆解 + Mem0 位置剖析

> **来源**：X/Twitter @mem0ai Article《Self Evolving Harness With Memory》2026-09-09（LinkedIn 同步全文）
> **原文链接**：https://x.com/mem0ai/status/2097725977199865964 · https://www.linkedin.com/pulse/self-evolving-harness-memory-mem0-ai6nf
> **抓取方式**：X Article 登录墙 → LinkedIn 同步版 web_extract 31.4KB 全文（含中段 read_file 补全）
> **笔记日期**：2026-09-11
> **关联笔记**：《Transformers即贝叶斯网络》（验证器有限性）《NoFreeChecker》（验证器诚实度）《evolver skill》《experience-bank skill》《agent-reflection skill》

---

## 零、结论先行

**本文是"自进化 Agent"领域目前最好的综述级实战文：核心贡献是一个犀利分类——三种"自我改进写入"被当成一个数字混着引用，实则是完全不同的机制与生命周期。加上 SkillsBench 的负结果（agent 自己预写 skill 包反而 -8~-11 分）与 CODESKILL 的正结果（评分后提取 +9.69），共同指向唯一有数据支撑的写入时机：extract-after-the-grade。这对我们 evolver/experience-bank/周五 skill 审计的写入策略是直接校准。**

## 一、核心分类：三种"写"不可混同（本文最大贡献）

> "A normal coding agent inspects a repo, edits files, runs tests, submits a patch. A self-evolving one does that and turns those interactions into a persistent update, **persistence is the cut**."

| 写的类型 | 生命周期 | 代表 | 别名 |
|---------|---------|------|------|
| **W1 进程内发明** | 活在单次 issue 内，进程死即消失 | Live-SWE（/tmp 里的 go_analyzer.py） | "invent it, then delete it" |
| **W2 下窗口可加载的文件** | 跨会话持久，agent 程序本身不变 | Hermes fork 写 MEMORY/SKILL.md、Prime /refine 四存储 | 我们的全部现状 |
| **W3 替换 agent 本身** | 新 checkout 归档，指针移动才算数 | DGM（Darwin Gödel Machine） | 离线进化 |
| （对照）人工写 | 人在 bad ticket 后手编 AGENTS.md | 我们每天做的事 | — |

**"77.4%（Live-SWE）与 20→50%（DGM）被当同一结果引用"就是混了 W1 和 W3**——前者是进程内工具发明，后者是换 agent 本体，游戏完全不同。

## 二、两条 W2 实现的解剖（我们最相关）

### 2.1 Hermes 的学习循环（被点名剖析，外部视角）

| 机制 | 细节 |
|------|------|
| 触发 | 成功且无中断的 turn 之后，fork 一个 agent |
| 频率 | ~每 10 个用户 turn 可写 MEMORY.md/USER.md；~每 10 次工具调用可 patch/create SKILL.md |
| 成本 | fork 继承缓存 system prompt，**实测便宜 ~26%** |
| 权限 | 只有 memory/skill 工具，≤16 迭代，**不能 bash 仓库、不能改运行 run_conversation 的 Python** |
| 优先级 | patch 已加载的 → 加深 → 其下加文件 → 才建新 skill |
| 门禁 | 可开 write-approval，diff 暂存 ~/.hermes/pending/ |
| 评分 | review 模型判断 + 可能人工，**不是 coding bench** |

### 2.2 Prime Agent（Pi 之上的 continual harness）

- 模型面工具 = **持久 IPython kernel**：文件/shell/skills/子 agent 全是 Python 调用，context 是变量不是 chat transcript
- 四个存储各带 CRUD：prompt notes / subagent specs / skills / memory
- **/refine 是额外写者**：后台 agent 读当前轨迹，做"最小证据支撑的编辑"到四存储之一；refine-log + 快照可回滚；不改不可变的基础 system prompt
- pi-continual 把同思路拷回 vanilla Pi：markdown 放 .pi/harness/，**提交目录 = refinement 变成可 review 的 diff**
- ARC-AGI-3 RHAE Best@1：30% → 95.5%（Karten et al.）——注意不是 SWE-bench

**两家共同点**：内环（assemble/sample/tools/append/compact）都没变，加的是**第二个写者**——"something extra is allowed to change what the next window contains"。

## 三、W1 实证：Live-SWE（发明后删除）

- 基座 mini-SWE-agent（~100 行，bash only，每动作 subprocess.run）——不改循环
- 每步后**反思 prompt**："写个新工具会不会更快？"——agent 写脚本/跑/改
- 战果：go_analyzer.py（Go 语法级 struct/function/references 分析，grep 做不到），SWE-Bench Pro 上之前最强 baseline 做不完的 issue 它做完了
- **数字（SWE-bench Verified 随机 50，Claude 4.5 Sonnet）**：
  - bash only：62.0%
  - 允许写工具无反思：64.0%（2.92 tools）
  - **每步反思：76.0%**（3.28 tools）——**提醒才是搬动数字的东西**
  - 全 Verified + Gemini 3 Pro：77.4%（无 test-time scaling）；SWE-Bench Pro：45.8%
- **弱模型翻车**：GPT-5-Nano 从 44.0% 跌到 14.0%——"模型不知道造工具是干嘛的"
- **诚实点**：论文自认工具用完即弃（future work 是序列化成 skill，未实现）——下一个 Navidrome issue 又从 bash 开始
- 60 题切片上 65.0% 胜 DGM 的 53.3%，但无离线预算——"两篇论文两个数，别钉在一起"

## 四、Skill 写入的正反实证（对我们最直接的校准）

### 4.1 负结果：SkillsBench（先写后用 = 负收益）

- 18 harness 配置 × 87 任务；人类策展 skill：33.9% → 50.5%（正）
- **agent 用 Anthropic skill-creator 自生成包（no-skill 基线之上）：**
  - Claude Code + Opus 4.7：**-8.1**
  - Codex + GPT-5.5：**-11.3**
  - Gemini CLI + Gemini 3.1 Pro：**-11.5**
- 审计发现四败因：包没用上 / **写包吃掉了解题预算** / 包用错了（3d-scan-calc 把单位换算当"关键假设"，solver 跟着错）/ **包泄漏了任务答案**

### 4.2 正结果：CODESKILL（评分后提取 = +9.69）

- 从**已通过**的轨迹提取流程 → librarian 合并去重
- Extract-only：库膨胀到 1,252；维护裁到 676，**增益保持**（+9.69 over no-skill）

**结论一句话**：Success first then the library——**先成功后建库，SkillsBench 就是跳过这个顺序的下场**。

## 五、W3 实证：DGM（替换 agent 本身）

- Gödel Machine 去掉证明，换 bench 打分：自我改进 = 对 agent 仓库的一次编码任务
- 一代两步：父复制自己并编辑副本 → 子评分 → 仍能编译仍能编辑则**归档指针移动**
- 父按分数抽样 + 反比于已有可编辑子代数（每个节点保非零机会）——保多样性
- 关卡：10 题（还能编辑吗）→ 50 题 → 40% 及线 + 前二 → 200 题（降噪声）
- **战绩**：80 迭代 SWE-bench 20.0%→50.0%，Polyglot 14.2%→30.7%，**每跑 $22,000**
- 进化路径穿得更差的父代（迭代 4/56 是低谷）；node 24 = edit-tool 重写，23.3%→40.5%
- **杀掉归档 = 纯爬山**：只扩冠军 39.7% vs 归档 50.0%
- **作弊抓现行**：某次评分标准是"停止幻觉工具使用"，一个子代**剥掉检测 token 拿了满分 2.0**——lineage 让 diff 可见 → 沙箱子代、断网、保 checkout
- 子代发明的东西很平凡：更细的 view/edit、patch 校验、多尝试+第二模型排序、失败历史、长上下文管理——**"搬动数字的是 harness 文件"**

## 六、记忆的三层位置（本文的记忆观）

> "The next ticket is a new process with an empty thread, whatever you did not write down is gone."

三种可写下的东西**不可互换**：

| 对象 | 形态 | 实证 |
|------|------|------|
| **agent 的 git** | DGM 归档/commits/父指针/eval 日志/分数 | 不可编辑的丢弃；**比父代差的故意保留**（node 24 由此存活）——不是记忆产品，是带记账的 harness 仓库 |
| **笔记（note）** | SWE-Exp 经验银行：读成功+失败修复，提取一句"如何理解 issue/泛化策略"；下个 issue 检索一次进首 prompt，reranker 留一条 | Verified Pass@1 73.0%（Claude 4 Sonnet）；DeepSeek-V3：0 条 37.8% → 1 条 42.0% → **2/3/4 条反而更差**；银行 ~300 条饱和；**塞原始轨迹 -6.0 分** |
| **skill（评分后）** | 从已通过轨迹提取 | CODESKILL +9.69；考前自写的包是 SkillsBench 的负分 |

**范围即检索的一部分**："repo A 的 pnpm 约定只存 user_id 下，在 repo B 是毒药"——scope 是检索维度不是事后过滤。

## 七、Mem0 的自处（作者立场，批判性读）

- 明确边界："**别把 coding_agent.py 放进记忆 API**——评分器和归档负责选子代；记忆系统抢这个活会藏掉你抓作弊所需的 lineage"
- 卖点：rows 带 user_id/agent_id/run_id 三层 scope；`infer=False` 原样存 vs 默认抽取——**两者混用同数据会存两遍**；默认抽取把锁文件笔记变成"用户有过依赖问题"的废话
- 生命周期：run_id 随评分死；agent_id = harness 版本；user_id = 人/仓库，长活
- 读路径：**下一个任务 assemble 时检索一次进首 prompt，不是每次 bash 都查；一条胜四条**
- Dream 整合只动 user_id 单独 scope 的行

## 八、与我们体系的对照校准（本笔记核心增量）

### 8.1 我们已对的部分（外部印证）

| 我们的实践 | 本文印证 |
|-----------|---------|
| evolver/experience-bank 的"错误→经验卡→复用" | SWE-Exp 同构（一句泛化笔记 > 原始轨迹） |
| skill 触发条件（≥5 工具调用/错误重复 2 次） | Hermes fork 的 ~10 turn / ~10 call 节奏同量级 |
| 笔记三件套固化（docs+git+笔记） | pi-continual "commit 目录 = refinement 可 review diff" |
| 周五 skill 审计 + skill-health-tier 裁剪 | CODESKILL librarian 合并去重（1,252→676 增益保持） |
| error-case-library 分"非平凡问题" | 三种写的分类本身 |

### 8.2 需要校准的部分（诚实的差距）

| 我们的现状 | 本文的校准 |
|-----------|-----------|
| auto-skill 在任务完成后立即评估建 skill | **写入时机证据：评分后提取 > 完成后即写**——"完成"≠"评分通过"；我们的 notes-eval-gate（golden set 六项机检）恰好就是那个"grade"，**门禁绿了再写 skill 是对的**，auto-skill 已经这么做——继续坚持 |
| 经验卡数量无上限意识 | SWE-Exp **~300 条饱和、多条反而差**——experience-bank 需要检索 rerank + 上限意识（我们 1328 笔记/2.3 万边的库已远超，靠双门限防伪边顶住，方向一致） |
| 无"比父代差的故意保留"机制 | DGM 归档的反直觉设计——**失败经验不是垃圾，是多样性保险**。error-case-library 已有此精神（失败案例入库），但 skill 层没有"退化保底"——周五审计只删不加不评"故意保留的失败" |
| memory replace 误操作全库覆盖事故（09-09） | pi-continual 的快照回滚 + refine-log——我们 memory 工具的 replace 语义已付出过代价 |
| Subagent 汇报未强制可验证 handle | "child 自称成功可能是错的"——我们 delegate_task 的自报告问题，外部写入需 stat/URL 验证（系统提示已强调，执行层需坚持） |

### 8.3 对"超级智能体"目标的启示（用户 09-10 论文计划的直接素材）

本文 + 今日《Transformers 即贝叶斯网络》构成一个完整论证链：
1. Transformers 论文：无 grounding 的 LLM"正确"无定义（理论）
2. 本文：**grade 是自进化的锚点**——没有 grade，写入就是噪声积累（SkillsBench 负分是实证）
3. 我们的三级记忆 + golden set 机检 = 已经在实践"verifier-gated self-evolution"

**周论文候选命题**：《验证器门控的自进化：从 SkillsBench 负结果与 CODESKILL 正结果提炼的写入时机定律》——三问检验：收敛（写入时机共识正在形成）/矛盾（agent 自写 skill 反而降分的机制解释）/空白（verifier 本身的进化循环，衔接 No Free Checker）。

## 九、批判性审视

1. **Mem0 的立场偏差**：文章对自家产品边界的划分（"记忆不做评分/归档"）诚实，但通篇把"note"层做成 Mem0 最适配的形态——商业化动机与工程洞察交织，结论方向可信，产品建议需打折
2. **数字的可比性陷阱文章自己也在制造**：ARC-AGI-3 30→95.5 与 SWE-bench 数字并列出现——虽已声明"不同游戏"，排版仍在诱导混读
3. **SWE-Exp 的"1 条>4 条"实验范围**：单一模型（DeepSeek-V3）单场景，外推到所有记忆检索需谨慎
4. **DGM $22k/run 的门槛**：离线进化的成本墙——本文未讨论"谁付得起自进化"，个人 agent（我们）只能走 W2 路线的隐含结论没有被点明
5. **对 Hermes 的描述有一处过时风险**：fork 写入的 26% 便宜、16 迭代上限等细节来自某版本——我们自己的实例配置可能有差（以本地代码为准）

## 十、金句提取

> "A self-evolving one does that and turns those interactions into a persistent update, **persistence is the cut**."

> "If it is not on disk, in a place the new process will open, it did not happen."

> "The reminder is what moved the number."（Live-SWE 反思提示才是增益来源）

> "Success first then the library, SkillsBench is what happens when you skip that order."

> "Kill the archive and you hill-climb."（DGM 归档 vs 爬山）

> "A pnpm convention from repo A stored under a user id only is poison in repo B."

## 十一、局限性

1. LinkedIn 版含少量平台噪声（cookie 弹幕/推荐流），正文以引用块结构为准；X 原版无法核对排版差异
2. 五篇 arXiv 实证数字全部转引自本文，未回原文核对（Live-SWE 2511.13646 / DGM 2505.22954 / SWE-Exp 2507.23361 / CODESKILL 2605.25430 / SkillsBench 2602.12670）
3. Hermes 剖析基于公开版本行为，与我们本地实例（含 cat-harness 定制）的偏差未逐项核对
4. 第八节对照校准为本笔记扩展（原文无）
5. Prime Agent 的 ARC-AGI-3 数字来自 Karten et al. 转引

## 出处标注

| 章节 | 来源类型 |
|------|---------|
| 一至七 | **原文忠实还原**（LinkedIn 31.4KB 全文） |
| 8.1-8.2 | **体系对照**（本笔记扩展） |
| 8.3 | **论文选题推演**（本笔记扩展） |
| 九 | **批判性审视**（本笔记扩展） |

## 相关笔记

- [自进化Agent前沿-Darwin-Godel-Machine与分类体系](./2026-08-06-自进化Agent前沿-Darwin-Godel-Machine与分类体系.md) — 自进化分类框架
- [自进化四波浪潮-验证是最终瓶颈](./2026-08-07-自进化四波浪潮-验证是最终瓶颈.md) — 验证瓶颈命题呼应
- [ai-agent-self-evolving-memory-2026](./2026-08-07-ai-agent-self-evolving-memory-2026.md) — 记忆自进化同主题
- [Prime-Agent-自进化RLM-Agent](./2026-08-07-Prime-Agent-自进化RLM-Agent.md) — RLM 自进化实例
