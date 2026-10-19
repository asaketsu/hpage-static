# SkillEffect：内存受限 Agent 工具的已检查降阶运行时的内容整理与指南分析

> **来源**：arXiv
> **原文链接**：https://arxiv.org/abs/2608.17007
> **作者**：Wang, Yinuo；Shi, Yiyu
> **日期**：2026-08-17
> **arXiv ID**：2608.17007
> **领域**：cs.AI / cs.LG（Agent 工具运行时、内存受限执行、检查式编译）
> **记录日期**：2026-08-20

**标签**：#Agent工具 #内存受限 #已检查降阶 #Skill运行时 #cgroup #SkillEffect #Hermes借鉴

---

## 一、内容整理

### 1.1 核心问题与研究动机

Agent Skills 越来越多地向 LLM 提供"该调用哪个工具、该关注哪些字段、结果如何校验"的程序化知识。问题是：同一条程序化指导可以编译为**物理执行差异巨大的多种具体程序**。

论文指出一个被严重低估的系统性瓶颈——**单工具调用的峰值内存**：

- 调用 `read_csv` 可能物化整张表（300+ MiB 峰值）
- 同样的聚合任务，lazy scan 只保留投影/过滤/聚合的常数态（<15 MiB）
- 在 100 MiB 的工具执行内存上限下，二者的区别不是"快慢"，而是"能否完成"

> **关键事实**：在作者的 smolagents harness 实验中，全部 16 个"语义正确"的工具调用在无资源反馈时都选择了 eager access 模式——LLM 天然偏好"读完再处理"，而非流式降阶。

该问题的工程背景并非纸面假设，而是现代 Agent 平台的标准基础设施约束：

- Modal Functions/Sandboxes：默认 128 MiB
- E2B：512 MiB 起步，付费可定制
- Cloudflare Workers：单 isolate 128 MB 上限
- AWS Lambda：默认 128 MB
- Daytona：一 agent 一 sandbox，组织级池化

因此"为 eager 最坏情况预留"会浪费池，"乐观放行"会在 LLM 已消耗 tokens 和延迟后再被 OOM-kill。**有用的控制点被精确定位在 pending dispatch 阶段**——模型已把 plan 具体化，但工具进程尚未消耗租户的内存额度。

### 1.2 相关工作的系统性缺口

论文梳理了 Skill 编译 + 资源推理 + 预算执行三条工作线，定位出一个**具体缺口**：

- **Skill 压缩（SkillZip / Control Under Compression）**：能保留程序化契约，但**不**为模型选定的具体程序分配物理 live-set 效应
- **Cost-aware planner（CATP-LLM）**：用 profile 偏好廉价工具，但 profile **不构造**保持语义的有界实现
- **计划门/cgroup（Agent libOS / AgentCgroup）**：能拒绝或终止不安全进程，但**无法恢复**预期结果
- **pandas → 数据库/流式算子替换**：只是用了更少内存并不代表正确——过滤器、输出键、归约语义、边界情况必须匹配声明的任务

SkillEffect 精准定位于"语义正确的 plan"到"内存有界的执行"之间的这段缺口。

### 1.3 方法论：已检查降阶（Checked Lowering）运行时的三大支柱

SkillEffect 提出一个可重用的**关系（relation）契约**，把异构的、资源敏感的计算统一为一个检查边界。核心是一个五元组：

```
r = ⟨ Sr, Ir, Lr, Ar, Gr ⟩
Sr  : 源识别器（recognize source computation）
Ir  : 输入事实提取器（immutable input facts）
Lr  : 有界 IR 构造器（bounded-IR constructor）
Ar  : arena 边界函数（peak memory 推导）
Gr  : 发布前后置条件（publication postcondition）
```

运行时分**三阶段 proposal-check-execute 信任边界**：

```
模型（builder）                运行时（trusted）
  └─ 生成工具程序 p                     │
      └─ 提交有界降阶提议 z              │
                                ┌──────┤
                                │ Sr reparses 完整 AST
                                │ Ir 检查不可变输入
                                │ Lr 重建规范有界 IR
                                │ Ar 推导 live-set 峰值
                                │ Gr 注册发布检查
                                │ 校验 z 与重建值一致
                                │ U ≤ B（容量租赁）
                                └──────┤
                                        └─ 接受 → bounded VM 执行
                                          └─ Gr 通过后 staged publish
                                          └─ 拒绝/歧义 → abstain，返回控制权
```

关键设计选择：

- **builder 的降阶是不可信的**——可以是 LLM、启发式前端或传统优化器，其目标/witness/bindings 都是提议
- **checker 独立重建**——不接受 builder 提供的目标 IR，而是从源 AST + 不可变输入重新推导，比对后判定一致性
- **唯一性规则**：恰好一条关系通过 = 执行；0 条 = abstain；多条 = 歧义拒绝。该规则把"多个候选中选最省内存"的非确定性风险转化为硬性 abstain
- **builder 不知道任务语义或 family 标签**，只拿到被接受的有界 IR

论文定义了完整的内存模型（公式 1）：

```
We(x) =  max( ne(x), ℓe )           // eager 模式峰值
We_b(x) = min( ne(x), ℓe )          // bounded 模式峰值（受窗口上限约束）

Uπ(p,x) = Fπ + Mπ + max_t Σ e∈A_p(t) [ απ,e · We(x) + Re(x) ]
         // 固定运行态 + 平台预留 + 重叠激活效应峰值
```

checker 从已接受的源语法派生 live window，加上平台预留，得到有界峰值 Ũr，作为原子容量租赁的请求上限 Ui。

### 1.4 六个运算符族与五种有界执行模式

论文在 6 个工具族上实例化同一个五义务契约：

- **CSV/Polars**：Streaming relational pipeline，投影+过滤器+整数归约，窗口输入+常数聚合
- **FASTA/Biopython**：Iterator/record reduction，窗口输入+固定直方图
- **FCS/FlowIO**：Metadata projection，从 header/TEXT 投影，有界元数据态
- **Zarr**：Chunked incremental reduction，单 chunk + 固定直方图
- **XLSX**：Iterator/row-window reduction，行窗口 + 常数聚合
- **Audit Top-k**：Bounded-heap Top-k，窗口输入 + k 条记录

6 个运算符族 × 4 参数化 = 24 个 task-Skill 对，每个都有确定性生成器 + 验证器。

## 二、查询拓展

### 2.1 已检查降阶（Checked Lowering）是什么

已检查降阶借鉴编译器领域的"检查式优化"思想：编译器不"信任"前端优化的正确性，而是独立重建等价 IR 并比对。SkillEffect 把这一模式第一次系统化应用于 Agent 工具运行时。

类比：pandas → Polars streaming 的转换中，前端说"我把 `read_csv` 换成 `scan_csv(...).collect(engine='streaming')`"，checker 独立重建这个等价关系，验证过滤器、输出键、归约语义、边界情况**完全一致**，才放行执行。否则 abort。

这与传统 "prompt 层告诉 LLM 用 streaming" 的根本区别在于：prompt-only guard 不能建立"生成的程序确实 streaming"的证明，而 SkillEffect 检查的是**已提交的具体 AST**。

### 2.2 cgroup v2 内存会计

论文运行测试使用 Linux 6.8/aarch64 + cgroup v2 环境：
- 每个容器 2 vCPU + 256 进程上限 + 明确的 memory.max + 禁用 swap
- 记录 `memory.events.max pressure` 而非错误分类成功的 reclaim-bound 执行
- SkillEffect 发布时要求所有四个 limit-event 计数器为 0

cgroup v2 提供的"memory.events 四计数器"是 SkillEffect 实现"发布前零超限"承诺的关键基础设施。

### 2.3 agent 沙盒内存约束的行业现实

论文点出的 128-512 MB 区间不是"论文特设"，而是整个 agent 平台行业的真实约束。Hermes Gateway 的 subagent / tool sandbox 如果采用类似约束，SkillEffect 的检查边界直接对应到 tool 调度层，不需要改动模型端。

## 三、归纳总结

### 3.1 SkillEffect 架构总框架（五阶段信任链）

```
[1] 模型生成工具程序 p         ← builder（不可信）
    ↓
[2] 提交有界降阶提议 z_r       ← builder 提议，含配置 ρ=(w,s) 和目标 IR
    ↓
[3] 独立重建与校验             ← checker（可信，核心）
    ├─ θr = Sr(AST(p))        # 从源 AST 重建语义参数
    ├─ fr = Ir(x)              # 从输入提取不可变事实
    ├─ T̂r = Lr(θr, fr; ρ)     # 重建规范有界 IR
    ├─ Ũr = Ar(T̂r, fr)         # 推导峰值内存
    └─ 校验 z.θ=θr ∧ z.f=fr ∧ z.T=T̂r ∧ z.U=Ũr ∧ Ũr≤B
    ↓
[4] 容量租赁 + bounded VM 执行  ← capacity lease（原子）
    ↓
[5] staged publication         ← Gr 通过后发布，限值计数器全零
```

**核心洞察**：generalization 来自**架构层面的可复用**（一次信任边界 + 通用调度机制），而非"自动处理任意程序"。每个新计算都需要审计一个 relation plugin。

### 3.2 关键实验结果

**24 任务 × 3 规模的硬 cap 完成率（Table 主表）**：

- Direct eager：0/24 任务通过（72/72 失败）
- Always-pin prompt：9/24 通过（仅靠资源 clause prompt 提示）
- Retry with resource feedback：4/24 通过
- Composition baseline：9/24 通过（四种生成策略中任选一个有界方案）
- **SkillEffect bounded lowering：24/24 通过（72/72 全部完成）**

SkillEffect 是**唯一**在全硬 cap 设定下 100% 完成任务的方案，且所有被拒绝的提案都被正确拒绝。

**对抗提案检查（Table 对抗实验）**：

- 200/200 资源低估 → 全部拒绝
- 80/80 源语义篡改 → 全部拒绝
- 80/80 不可变输入绑定攻击 → 全部拒绝
- 40/40 输出门绑定 → 全部拒绝
- 40/40 平台绑定 → 全部拒绝
- 40/40 源-目标不一致 → 全部拒绝
- 良性配置 60/60 → 全部接受

**延迟开销（Table 延迟对比）**：

- XLSX：eager 24.4s → bounded 19.7s（比值 0.81）
- FlowIO：0.53s → 0.45s（0.83）
- AnnData：1.36s → 1.10s（0.85）
- Zarr：1.22s → 1.06s（0.88）
- Polars：1.07s → 0.79s（0.74）
- Biopython：3.14s → 1.95s（0.62）

**关键发现**：有界模式在**多数场景下比 eager 更快**（比值 0.62-0.88），不是"换时间换空间"，而是**换空间同时换时间**。

**新关系接入成本（XLSX 扩展 + Top-k 扩展）**：

- XLSX：checker 216 行 + VM 算子 63 行 + builder 197 行 + 12 行 wiring
- Top-k：recognizer + facts + heap target + arena + postcondition
- **核心路径不变（dispatch + freeze 7 个核心文件全部未改）**

该结果证明了"架构通用性"的承诺：接入新关系只需要实现五元组契约，共享运行时完全不动。

## 四、趋势判断

### 4.1 Agent 工具运行时必走"检查式编译"路线

LLM 生成工具程序→运行时执行的链路中，语义正确性 ≠ 物理可执行性。Prompt 层提示和 post-hoc 拒绝都无法填补这段缺口。**趋势**：未来 Agent 平台的 tool dispatcher 会越来越多地内建"检查式降阶"层，把模型的程序化输出当作不可信输入，运行时独立重建和校验。

依据：论文实证 24/24 任务通过率 vs 所有 baseline ≤9/24；且所有对抗提案 500/500 被正确拒绝。

### 4.2 Skill 的"资源义务"将成为一等公民

Skill 当前的作用主要停留在"该用什么工具、传什么参数"，缺少"这个工具调用会消耗多少物理资源"的声明。**趋势**：Skill 定义层将扩展为包含 (procedure + resource obligation + postcondition)，运行时据此执行检查。

### 4.3 有界降阶可能反过来成为 Agent 训练的奖励信号

SkillEffect 证明"有界实现"不仅可用，而且常更快。这个信号可回流到训练/微调层——LLM 在 fine-tuning 或 RL 阶段可以明确奖励"选择 bounded access 模式"的行为，进一步降低默认 eager 选择率。

### 4.4 从确定性计算扩展到状态化/远端效应

论文坦承当前实现只覆盖"确定性、本地、只读"的计算。Email、支付、可变服务调用需要幂等性、授权和补偿协议。**趋势**：下一个版本会把 checked-lowering 扩展到有副作用的工具调用，涉及 transaction 边界。

## 五、关联分析

### 5.1 与 Hermes Skill/Agent 工具调用的关联

Hermes Agent 的 `delegate_task`、`tool_call`、`terminal` 调用都涉及"模型生成一段程序→网关执行"的链路。当前网关侧**没有任何"峰值内存检查 + 有界执行"层**——工具调用要么成功，要么被系统 OOM-kill。SkillEffect 提出的 checked-lowering 架构可以直接映射到 Hermes Gateway 的 tool dispatcher：

- **builder** = Hermes Gateway 的 subagent 生成的 tool program
- **checker** = 网关新增的独立验证层（从程序 AST + 输入重建有界 IR）
- **bounded VM** = 现有 terminal/subprocess 沙盒 + cgroup v2 内存上限
- **postcondition** = Skill 定义的验收条件（当前 SKILL.md 已有"完成定义"条款，可扩展为机器可验证的 postcondition）

具体到日常场景：当 subagent 生成一个 Python 数据分析脚本时，网关可以在执行前检查它是否会物化整个 DataFrame，若会则拒绝或提示改 streaming。

### 5.2 与 Jetson Orin 边缘部署的关联

Jetson Orin Nano Super 的内存约束（8GB/16GB，与 LLM 推理竞争）使得"单进程峰值内存"是真实瓶颈。SkillEffect 的方法论——**在 dispatch 时就把有界 IR 和峰值预算算清楚**——可以直接用于：

- 边缘端的工具调用（如数据预处理 pipeline）
- 量化交易系统的行情处理模块（实时性 + 内存确定性）
- 本地 LLM 推理 + 工具调用的联合预算分配

### 5.3 与之前精读论文的交叉映射

- **[SPyCE 2607.13854]**：技能-策略协同进化；SkillEffect 与之互补——SPyCE 解决"技能如何进化"，SkillEffect 解决"技能执行时如何保证资源边界"。二者可组合：SPyCE 进化的技能产物，进入 SkillEffect 的检查边界执行。
- **[Memory Compaction 2607.08032]**：率失真框架下的记忆压缩；SkillEffect 的"bounded window ℓe"概念与之呼应——都是有界状态下保持语义正确的压缩/降阶。
- **[OpenForgeRL 2607.21557]**：Harness-native RL 训练；SkillEffect 的"有界模式反而更快"实验结果为 RL 奖励信号提供方向。
- **[Screenshots or Tools 2608.03327]**：混合 GUI-MCP 工具采纳鸿沟；SkillEffect 解决的是"采纳后执行时"的资源问题，与之互补。

## 六、拓展应用推荐

### 6.1 Hermes Gateway tool dispatcher 加检查层

对高风险工具调用（数据处理、文件操作）加轻量 checker：先解析生成程序的 AST，识别是否有 `read_csv`/`read_excel` 等物化调用，若无 streaming 参数则提示或拒绝。工作量估算：2-3 天（实现核心 checker + 3-5 个 relation plugin）。

### 6.2 Skill.md 增加 resource obligation 字段

在 SKILL.md frontmatter 中扩展字段：

```yaml
resource_obligation:
  peak_memory: "<128 MiB"
  bounded_access: true
  postcondition: "返回行数 == 输入行数过滤后结果"
```

网关在 dispatch 时据此执行检查。工作量：半天（schema 扩展 + hook 校验）。

### 6.3 Jetson 边缘端工具调用的内存预算

为 Jetson 上本地工具（数据 ETL、行情处理、模型推理前处理）建立统一的有界执行清单，每类工具指定 capped 模式 + 峰值内存预算。工作量：1 周（盘点现有工具 + 建立 budget table）。

## 七、指南分析

### 7.1 对 Agent 平台架构设计的启示

**核心建议**：Agent 平台的"语义正确性"和"物理可执行性"必须分离。模型端只负责"生成语义正确的程序"，运行时端负责"把它降到有界可执行的形态并验证等价性"。把检查责任放在运行时，而非靠 prompt 让模型自我约束。

### 7.2 对 Hermes Skill 体系设计的启示

SKILL.md 目前定义了"完成定义"清单，但没有"资源义务"。建议新增字段：

- **peak_memory**：执行该 Skill 所需峰值内存（供 dispatcher 检查）
- **bounded_mode**：是否有 streaming/chunked 模式
- **postcondition**：机器可验证的验收条件（当前多为自然语言描述）

### 7.3 对工具调用安全性的启示

当前 Hermes 的 `terminal`/`execute_code` 调用完全信任 subagent 生成的命令/脚本。**风险**：subagent 生成 `python3 -c "df = pd.read_csv('huge.csv')" ` 直接 OOM。**建议**：在 dispatcher 层加入"AST 级资源检查"——识别 pandas 物化模式，若无 streaming 则拒绝或自动降阶。

### 7.4 实验方法论借鉴

论文的评测设计值得借鉴：

- **24 任务 × 3 规模**的矩阵设计，覆盖 6 个异构工具族
- **两种 cap 协议**：development cap（机制研究）+ external fixed cap sweep（工程可行性）
- **基线对照**：always-pin / retry / composition / direct eager / SkillEffect 五条平行线
- **稳定性规则**：run 只有同时满足正常退出 + 验证器通过 + cgroup 测量有效 + swap=0 + 无 OOM/OOM-kill 才算成功
- **对抗提案**：明确定义 6 类攻击面 + 全部拒绝的硬性目标

## 八、金句摘录

> "The useful control point is therefore the pending dispatch: after the model has made its plan concrete, but before the tool process consumes the tenant's allocation."

> "Skill compression can preserve procedural contracts, but does not generally assign a physical live-set effect to the program selected by the model."

> "A plan gate or cgroup can reject or stop an unsafe process, but cannot recover the intended result."

> "The system's generality therefore comes from reusing one trusted dispatch architecture across audited relation plugins, rather than from accepting arbitrary generated programs."

> "Bounded access substantially reduces peak memory and improves completion under externally fixed caps."

## 九、可落实借鉴点评估（P0/P1/P2/P3）

- **P0 🔨**：Hermes Gateway tool dispatcher 加 AST 级资源检查层（识别 pandas 物化 → 自动提示 streaming 模式）。直接复用 SkillEffect 的"Sr reparses AST"思路。工作量 2-3 天。
- **P1 ⚠️**：SKILL.md frontmatter 扩展 `resource_obligation` / `peak_memory` / `postcondition` 字段。需要 schema 更新 + hook 校验。工作量 0.5 天，但涉及全量 Skill 迁移。
- **P1 🔨**：在 SkillEffect 论文基础上写一个最小 1-2 个 relation plugin（Polars streaming + XLSX read_only）的演示实现，放到 `~/uclaw/project/skill-effect-demo/`。工作量 1 周，与 OpenForgeRL 训练场景可联合。
- **P2 🔨**：Jetson 边缘端工具内存预算清单（盘点常用工具的 eager vs bounded 模式峰值）。工作量 1 周。
- **P3 ✅**：将"bounded 模式更快"的实验结论纳入 Agent fine-tuning / RL 的奖励信号设计参考——已有 Skill（SPyCE/OpenForgeRL）可作为落地点。

## 十、关联论文索引

- [SPyCE 2607.13854 技能-策略协同进化](2026-07-16-SPyCE-技能策略协同进化.md)
- [Memory Compaction 2607.08032 记忆压缩率失真](2026-07-12-MemoryCompaction-率失真.md)
- [OpenForgeRL 2607.21557 Harness-native RL](2026-07-27-OpenForgeRL-HarnessRL.md)
- [Screenshots or Tools 2608.03327 工具采纳鸿沟](2026-08-09-ScreenshotsOrTools-工具采纳鸿沟.md)
- [EvoSOP 2607.07321 Agent 自进化工具](2026-07-10-EvoSOP-自进化工具.md)

## 相关笔记

- [Screenshots or Tools 2608.03327 工具采纳鸿沟](2026-08-09-ScreenshotsOrTools-工具采纳鸿沟.md) — 工具选择对比
- [Agent记忆治理-SSGM框架](../2026-08-10-Agent记忆治理-SSGM框架与进化型记忆风险.md) — 记忆治理层
- [Memory Compaction 2607.08032 记忆压缩率失真](2026-07-12-MemoryCompaction-率失真.md) — 压缩技术背景
- [OpenForgeRL Harness-native RL](2026-07-27-OpenForgeRL-HarnessRL.md) — RL训练框架
- [Agent记忆事务安全与自进化](../2026-08-09-Agent记忆事务安全与自进化-2026前沿论文综述.md) — 事务安全