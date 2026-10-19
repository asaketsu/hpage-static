# Agent 记忆离线整理范式：Auto-Dreamer 区域重写与 Sleep-time Compute 精读

> 探索日期 2026-09-10（夜间自学习） | 兴趣等级 L4 | 来源 5 篇 | 前序笔记：`2026-09-08-Agent记忆迁移性`、`2026-06-20-Agent Memory 2026 架构分化`、`2026-07-21-LLM自进化为何崩溃`

## 核心问题

Agent 记忆系统的公认痛点：**采集与整理耦合在同一个在线流程里**。每条记忆在会话结束的瞬间被写入，此后再无人回头审视——冗余不除、矛盾不解、跨会话模式无人抽象。本篇精读两篇互补工作：Letta 的 Sleep-time Compute（范式提出，arXiv 2504.13171）与 UIUC+UCSD 的 Auto-Dreamer（学习方法化，arXiv 2605.20616），并映射到 Hermes 自身记忆体系。

## 核心发现（5 条）

1. **Sleep-time Compute 的本质是"上下文预计算"**：把 raw context 在空闲期转化为 learned context，测试时直接复用。Letta 实测在 AIME/GSM 上实现 Pareto 改进——计算负载从高延迟用户交互期迁移到空闲期，性能不降。前提是 **stateful agent**：无持久记忆的无状态模型做 sleep-time 推理，醒来即忘，毫无意义。
2. **双代理架构是工程关键**：Letta 0.7.0 的 sleep-time agent 独占 memory 编辑工具，primary agent 只读。这解决了 MemGPT 单代理"边聊天边管记忆"的慢与不可靠。**sleep-time agent 可以配更强的模型**——它不受延迟约束（夜间 cron 本来就该用最强模型）。
3. **Auto-Dreamer 把"整理"变成可学习的决策问题**：受互补学习系统（CLS）理论启发——海马体快速编码单次情节，新皮层慢速提取跨情节共享结构。Auto-Dreamer = 慢时间尺度的 consolidator，用 **GRPO** 训练，reward 直接用下游任务成功率，**不是**记忆格式评分。
4. **Region Rewriting（区域重写）是核心原语**：选中记忆库的一个区域 R，视为只读证据（可回溯源轨迹 provenance），合成一个全新的紧凑替换集取代 R。替换语义让"遗忘成为默认"——旧条目不再默认存活，信息只有被重新合成才存活。去重、抽象、矛盾消解全部内化为替换的副产品。
5. **反事实效用（counterfactual utility）识别 load-bearing 记忆**：reward 中加入随机屏蔽记忆项的反事实项——屏蔽后任务表现不掉的记忆 = 冗余，罚；屏蔽后掉分的记忆 = 承重墙，奖。这是对"哪些记忆真正有用"的可操作定义。

## 关键数据（Auto-Dreamer 实测）

| 指标 | Auto-Dreamer | 最强基线 | 差距 |
|------|-------------|---------|------|
| ScienceWorld 成功率 | 41.1% | UMEM 34.1% | **+7.0pp** |
| ScienceWorld 活跃记忆 | 6.9k tokens | UMEM 80.9k | **12× 更小** |
| ALFWorld（零样本迁移） | 60.2% | — | 6× 更小记忆仍领先 |
| WebArena（零样本迁移） | 52.3% | — | 全部基线中第一 |
| find-entity 案例 | 72.5% / 7.4步 | AWM 26.2% / 20.0步 | 负面教训致胜 |

迁移性证据：仅在 ScienceWorld 轨迹上训练，零样本迁移到 ALFWorld/WebArena 仍领先，且扛住了 writer 骨干从 Qwen3-14B 换到 Gemini-3.1-flash-lite-preview 的切换——**consolidator 学到的是整理能力，不是领域知识**。

## 负面教训案例（对 error-case-library 的学术验证）

find-entity 案例是全篇最有价值的分析：AWM（success-only 工作流归纳）在 80 个任务中有 20 次第一步就 `focus on <错误物体>`，其中 11 次立即终局（score -1.0）。这些失败从不进入 AWM 的成功导出工作流池。Auto-Dreamer 却能从**失败轨迹**中合成"避免错误聚焦"类的负面规则。

```
成功轨迹库  →  只能学到 "做什么"（正规则）
失败轨迹库  →  才能学到 "不做什么"（负规则）
              两者缺一，长尾任务必翻车
```

> 用户的 error-case-library（非平凡问题→落盘）正是这个模式的工程实现。Auto-Dreamer 给出了理论背书：**负面教训不是锦上添花，是 success-only 归纳法结构性缺失的那一半**。

## 与现有工作的关联（改进建议）

### Hermes 记忆体系对照表

| Auto-Dreamer 概念 | Hermes 对应物 | 现状差距 |
|-------------------|--------------|---------|
| fast writer（每会话写入） | memory-write skill + session 结束钩子 | ✅ 已有 |
| slow consolidator（跨会话整理） | auto-dream cron + memory-refiner | ⚠️ 逐条 CRUD，无区域重写 |
| typed memory（semantic/procedural） | MEMORY.md / skills / error-case-library | ✅ 三型齐全 |
| provenance（源轨迹链接） | error-case 里的会话引用 | ⚠️ 不系统 |
| counterfactual utility | 无 | ❌ 完全缺失 |
| region rewriting | MEMORY 全库单条目 replace | 🔥 契合度极高 |

### 按 P0/P1/P2 排序

- **P0 — MEMORY 压缩采用"区域重写"而非逐条删减**：MEMORY 当前 27%（2186/8000 字符），逼近半满。memory 工具的 replace 语义本来就是整条目替换（09-09 两次误操作事故的根源恰是这个特性）——与其视为坑，不如顺势利用：夜间压缩时把"拓朴/硬件"等区块整体读出→重写为紧凑版，信息只有被重新合成的才存活。这与 09-09 用户指令"记忆满了=扩容+精练一次到位"完全一致。
- **P1 — error-case-library 条目补 provenance 链接**：每条 case 增加 `session_id` 字段，consolidator（夜间自学习）可回溯原始上下文验证规则是否过时。
- **P1 — 引入轻量 counterfactual 检验**：记忆条目 30 天未被任何 session 检索命中且内容与近期行为无交集 → 标记候选淘汰名单，供 memory-refiner 决策。不需要真做屏蔽实验，检索日志即代理指标。
- **P2 — 夜间 cron 明确"更强模型"原则**：Letta 实践显示 sleep-time agent 该用更强模型。当前夜间自学习用 GLM-5.2 已符合；可固化到 auto-dream 合规清单。

## 关键风险与盲点

- **ScienceWorld 训练域窄**（来源级别：官方论文）：consolidator 仅在一个文本环境训练，零样本迁移虽有数据支撑，但到开放域（如 Hermes 的运维/量化/机器人混合场景）是否成立未经验证。社区复现尚缺。
- **reward 依赖可测的下游成功率**：Hermes 场景没有 ScienceWorld 式打分器，"任务成功率"需替换为代理指标（用户反馈、cron 成功率、error-case 复发率）——映射时这是最大的失真点。
- **Letta 双代理与 Claude Code autoDream 的关系**（来源级别：第三方博客+源码泄露）：mywrittenword.com 已更正声明——Anthropic 并未发表论文，autoDream 是泄露源码中的工程实现，与 Letta 学术工作是独立平行演化。引用时不可混为一谈。

## 一页速查

> - Sleep-time compute = 空闲期把 raw context 算成 learned context；前提 stateful。
> - 双代理：primary 只读记忆，sleep-time agent 独占写权 + 用更强模型。
> - Auto-Dreamer：GRPO 训 consolidator，reward=任务成功 + 反事实效用。
> - Region rewriting：区域只读→合成替换集→旧条目默认死亡。
> - 数据：+7pp 成功率，记忆 12× 更小，跨域零样本迁移成立。
> - 负面教训（失败轨迹）是 success-only 归纳的结构性补集 → error-case-library 路线正确。
> - Hermes 行动：MEMORY 压缩走区域重写；error-case 补 provenance；30 天未命中记忆进淘汰候选。

## 待深入

1. LightMem（arXiv 2505.18834）：在线 writer + 周期离线整理的 prompted 管线，与 Auto-Dreamer 的学习方法对比——Hermes 短期更易落地 prompted 版。
2. 开源实现 dreamweave（graph+vector 三层 + 遗忘曲线，OpenClaw 生态）可否直接嫁接 Hermes 记忆栈。
3. 反事实效用在本地的可计算近似：用 session 检索命中率做代理，设计 memory-refiner 的淘汰打分公式。

## 来源列表

1. Letta Blog — *Sleep-time Compute*（2025-04-21）: https://www.letta.com/blog/sleep-time-compute
2. arXiv 2504.13171 — *Sleep-time Compute: Beyond Inference Scaling* （Letta/UC Berkeley）
3. arXiv 2605.20616 — *Auto-Dreamer: Learning Offline Memory Consolidation for Language Agents*（UIUC+UCSD, 2026-05-20, HTML 全文精读）
4. mywrittenword.com — *Claude Code AutoDream*（2026-03，含 2026-08-18 更正声明）
5. GitHub topics/memory-consolidation — OpenDream、dreamweave、engrava 开源生态扫描


## 相关笔记

- [patent-disclosure-skill精读](./2026-09-09-patent-disclosure-skill精读-YAML状态机与路径交接合同.md) — 单协调者+状态机，Agent 工程架构对照
- [SKILL.state长程Agent状态架构](./2026-09-01-SKILL.state长程Agent状态架构-16倍Token削减与准确率反升.md) — 长程状态压缩同族
- [AI工程化终极路线图](./2026-09-09-AI工程化终极路线图-十域拆解与Hermes体系自检.md) — Hermes 记忆体系自检互证
- Agent Memory 长时程前沿 2026（~/explore/ 目录，跨根目录）— 记忆系统 frontier 综述
