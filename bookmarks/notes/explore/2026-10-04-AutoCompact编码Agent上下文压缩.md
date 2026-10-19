# AutoCompact：训练编码Agent学习何时压缩上下文

> **来源**：arXiv (cs.CL)
> **原文链接**：https://arxiv.org/abs/2610.02163
> **作者**：Xuan Zhang, Longtao Zheng, Cunxiao Du, Bo An, Xin Dong
> **发布日期**：2026-10-01
> **记录日期**：2026-10-04

**标签**：#LLM-Agent #上下文压缩 #编码Agent #强化学习 #上下文管理

---

## 一、内容整理

### 1.1 核心问题

编码 Agent 在处理仓库级软件工程任务时，轨迹会积累大量代码片段、工具输出和中间发现。随着任务推进，早期探索信息（如过时的假设、失败的尝试、冗长的工具输出）变成"陈旧上下文"，填充 context window 但当前阶段并不需要。

现有上下文管理方法只解决了部分问题：
- **长度触发式**（如 CompactionRL）：仅在剩余 context 预算低于固定阈值时压缩，将压缩与上下文长度而非任务进度绑定——陈旧探索累积到阈值才触发，压缩可能发生在仍需证据的未解决阶段中间
- **主动式**（如 SelfCompact/SWE-Compressor）：让 Agent 自行决定何时压缩，但仅解决"何时"问题，未处理"压缩后工作状态是否准确"和"压缩后如何继续执行"两类失败

AutoCompact 的核心主张：有效上下文管理需要 Agent 同时学会三件事——何时压缩、保留什么工作状态、如何从压缩状态继续执行。

### 1.2 方法论：AutoCompact 三阶段训练

**阶段 0：compact() 动作注入**

Agent 被赋予一个 `compact()` 动作，可在执行过程中主动调用。当 Agent 判定当前阶段已充分解决、累积历史可以摘要时，可在到达 context 限制前主动调用。压缩将早期交互历史替换为模型生成的工作状态摘要（标题为 `# Auto Context Summary`），保留原始任务不变。摘要旨在保留已确立的发现、相关代码与工作区状态、剩余动作，省略先前探索的不必要细节。

关键设计：压缩是模型决策而非仅对 context window 压力的响应。

**阶段 1：Judge-Guided 在线数据收集 + SFT**

直接 prompt 无法诱导主动压缩——基础模型在 context 限制前极少调用 `compact()`。因此需要收集带 judge 纠正的训练轨迹：

- 在软件工程任务上 rollout 基础策略
- Judge（GPT-5.5-Codex）在每步审查策略提案，仅使用当前执行历史
- 三类纠正对应三大失败模式：
  - **触发纠正**（Trigger correction）：检查当前点是否适合压缩——当前阶段已充分解决时应压缩，中间证据仍需要时应继续探索
  - **工作状态纠正**（Working-state correction）：检查 `# Auto Context Summary` 是否准确保留后续执行所需信息，包括相关结论、代码与工作区状态、剩余动作
  - **续接纠正**（Continuation correction）：检查压缩后首批动作是否遵循工作状态，而非重复已完成探索或忽略预期下一步

- 纠正在执行前应用——Judge 写出纠正后的输出，环境执行纠正版本而非原始版本，策略从纠正后的历史生成后续动作。这与事后标注（post-hoc annotation）本质不同，后者纠正不影响后续状态。
- 收集 1,052 条 judge 纠正轨迹（24% 监督压缩触发，53% 监督工作状态构建，23% 监督压缩后续接），训练 2 个 epoch，学习率 5×10⁻⁷，batch size 8

**阶段 2：联合 RL 优化编码与压缩**

从 SFT checkpoint 出发，在 SWE-Gym 上用端到端多轮 RL（GRPO）进一步训练。每个任务采样 8 条轨迹，分配二元结果奖励——最终 patch 是否通过任务测试套件。RL 学习率 1×10⁻⁶，batch size 64，rollout 上限 50 个环境步骤和 32K token。

核心设计：RL 不使用压缩专用奖励，仅用任务成功作为唯一奖励信号，但奖励通过压缩后的续接动作传导回压缩决策。

### 1.3 关键实验结果

**主实验（Table 1）— SWE-bench Verified + SWE-PolyBench Verified 全量通过率**

- AutoCompact（SFT→RL）：SWE-bench 39.6%，SWE-PolyBench 24.5%
- Base（无压缩）：SWE-bench 30.4%，SWE-PolyBench 19.5%
- 绝对提升：SWE-bench +9.2%，SWE-PolyBench +5.0%
- AutoCompact-SFT（仅SFT）：SWE-bench 32.2%，SWE-PolyBench 21.7%
- CompactionRL（长度触发+RL）：SWE-bench 32.7%，SWE-PolyBench 19.8%
- SelfCompact（推理时rubric）：SWE-bench 31.7%，SWE-PolyBench 20.6%
- SWE-Compressor（离线SFT）：SWE-bench 31.0%，SWE-PolyBench 20.1%
- Fixed Compaction（固定阈值）：SWE-bench 28.8%（低于Base），SWE-PolyBench 18.6%

**成本效率（Figure 3）— 六档推理预算 $0.10 至 $4.00**

- 256K context（无轨迹触及强制压缩阈值）：AutoCompact-SFT 在所有预算上超越 Base，证明即使全历史能放入 context window，保留完整交互历史也不是最优选择
- 16K context（共享强制压缩 fallback）：AutoCompact 在所有预算上超越 Base，证明学习式主动压缩与长度触发 fallback 组合仍然有效
- SFT→RL 增量：RL 在低预算区间增益最大——低预算截断 rollout，更大增益说明 RL 使 Agent 更具成本效率而非依赖更长轨迹
- 压缩执行本身的贡献：同一训练 checkpoint，执行压缩 vs 跳过压缩（Summary-ignored），执行版本在 $0.10 预算下高 19.9%，$4.00 预算下高 1.9%

**压缩行为分析（Figure 4）**

- Base 极少主动调用 `compact()`
- AutoCompact-SFT：44.3% 任务调用 `compact()`
- AutoCompact（RL后）：58.5% 任务调用 `compact()`
- 关键状态遗漏：SFT 3.1% → RL 0.2%
- 下一步动作遗漏：SFT 8.2% → RL 2.2%
- 两个趋势互补：压缩使用更广泛，同时摘要质量更高

**摘要自洽性案例（Figure 5）— SWE-bench task django-13809**

- AutoCompact-SFT 摘要：记录了未解决的语法错误，但仍提议"完成无需进一步动作"——状态与提议的动作不自洽，最终评估失败（SyntaxError）
- AutoCompact（RL后）摘要：报告参数和条件逻辑修改已完成，提议提交前验证——状态与提议自洽，最终通过测试
- 根因分析：SFT 模仿已演示摘要，不保证记录的状态约束下一步动作；RL 仅通过后续动作的成功奖励摘要，天然鼓励自洽性

### 1.4 核心发现总结

- **主动压缩在 context 溢出前就有收益**：即使 256K 全历史能放入，用简洁工作状态替换陈旧历史也能提升性能
- **在线 judge 纠正优于离线插入**：AutoCompact-SFT 比 SWE-Compressor 高 1.2%/1.6%，因为纠正后的轨迹是实际执行的（纠正影响后续状态），而非事后插入到已完成轨迹
- **RL 在低预算区间增益最大**：任务成功奖励通过压缩后续接动作传导回压缩决策，使 Agent 更具成本效率
- **压缩执行本身有独立贡献**：同一 checkpoint 执行 vs 跳过压缩，执行版本收益不来自训练改善而是来自运行时压缩
- **摘要自洽性是被 RL 隐式学到的关键质量维度**：超越信息覆盖率的指标，SFT 无法保证

---

## 二、查询拓展

### 2.1 SWE-bench Verified

SWE-bench 的子集，由 OpenAI 人工验证。包含 GitHub 上真实 Python 仓库的 issue 解决任务，要求 Agent 生成能通过测试套件的 patch。SWE-bench Verified 是评估编码 Agent 的标准基准，满分通过率目前顶尖系统约 40-50%。AutoCompact 以 Qwen3-Coder-30B-A3B 达到 39.6%，接近最强水平。

### 2.2 SWE-Gym

SWE-Gym 是 SWE-bench 的训练环境扩展，提供可执行的任务环境用于 Agent 训练。与 SWE-bench 的评估任务不同，SWE-Gym 任务用于 RL rollout 采样，Agent 在环境中执行代码检查、编辑、测试，获得二元成功信号。AutoCompact 在 SWE-Gym 上做 GRPO 训练。

### 2.3 GRPO（Group Relative Policy Optimization）

DeepSeek 提出的 RL 算法，通过对同一 prompt 采样一组（group）轨迹，用组内相对优势作为 baseline 计算 advantage。相比 PPO 无需训练 value function，减少计算开销。AutoCompact 用 GRPO 的二元结果奖励（patch 是否通过测试）训练，每任务采样 8 条轨迹。

### 2.4 Model-Harness Co-design

论文提出的核心概念：harness（脚手架）提供压缩机制（`compact()` 动作），模型学习何时调用、保留什么、如何续接。这与"分离式压缩模块"不同——压缩不是独立的后处理，而是模型策略的有机组成部分。类似 Codex 和 Claude Code 目前用长度触发自动压缩，论文建议可结合学习式主动压缩进一步改进。

### 2.5 Summary Self-Consistency

论文定义的新概念：摘要不仅要保留相关信息（覆盖率指标）和提议下一步动作，还需保证记录的状态约束提议的动作。SFT 模仿演示摘要但不保证这种约束关系；RL 通过后续动作成功与否奖励摘要，天然鼓励自洽性。这是超越信息覆盖率的摘要质量维度。

---

## 三、归纳总结

### 3.1 三大失败模式 × 三类纠正映射框架

AutoCompact 的核心贡献是将"上下文压缩"拆解为三个正交子问题，每个对应一类失败模式和一类纠正：

- **何时压缩**（When）→ 触发纠正：当前阶段是否充分解决
- **保留什么**（What）→ 工作状态纠正：摘要是否准确保留关键信息
- **如何续接**（How）→ 续接纠正：压缩后首批动作是否遵循工作状态

这三者是因果链——错误的触发时机导致压缩在证据仍需时发生；错误的工作状态导致后续执行基于错误信息；错误的续接导致重复探索或忽略意图。

### 3.2 训练范式分层

```
Level 0: Prompt-only（无训练）
  └→ 基础模型极少主动压缩（仅 context 溢出时被动触发）

Level 1: SFT（监督模仿）
  └→ 学会基本压缩行为（44.3% 任务主动调用）
  └→ 但不保证摘要自洽性（状态不约束动作）

Level 2: RL（结果优化）
  └→ 压缩使用更广（58.5%）+ 质量更高（遗漏率骤降）
  └→ 隐式学到摘要自洽性（通过任务成功传导）
  └→ 低预算区间增益最大（成本效率而非更长轨迹）
```

### 3.3 对比基线的定位

- Fixed Compaction（固定阈值）→ 负效果（-1.6%），证明纯长度触发有害
- CompactionRL（长度触发+RL）→ 有限增益，因触发时机绑定长度而非进度
- SelfCompact（推理rubric）→ 有增益，但无训练信号无法改善摘要质量
- SWE-Compressor（离线SFT）→ 有增益，但离线插入不纠正后续动作
- AutoCompact（在线纠正+RL）→ 最高增益，因为纠正影响后续状态+RL 优化最终效果

---

## 四、趋势判断

### 趋势1：Agent 上下文管理从"被动溢出处理"转向"主动策略决策"

依据：论文证明即使 256K context 能放入全历史，主动压缩仍有收益。这意味着上下文管理的价值不在于防止溢出，而在于减少干扰。未来 Agent 的 context management 将像人类工作记忆一样——主动遗忘过时信息是认知效率的核心。

### 趋势2：Judge-Guided 在线纠正成为 SFT 数据构建新范式

依据：AutoCompact-SFT 比 SWE-Compressor 高 1.2-1.6%，核心差异是"纠正后轨迹实际执行"vs"离线插入到已完成轨迹"。在线纠正使每个纠正塑造后续轨迹，产生因果连贯的训练信号。这预示 SFT 数据构建从静态标注转向动态在线纠正。

### 趋势3：RL 隐式学到训练目标中未显式定义的质量维度

依据：论文发现 RL 学到了"摘要自洽性"——一个 SFT 无法保证、训练目标（二元任务成功）中未显式提及的维度。RL 通过奖励的因果传导（摘要→续接动作→任务成功），隐式优化了中间步骤质量。这预示未来 RL 训练可依赖更少的显式奖励工程。

### 趋势4：Model-Harness Co-design 成为 Agent 架构主流

依据：论文明确将"harness 提供 compact() 动作 + 模型学习调用策略"定义为 co-design。这与当前主流（harness 和模型分离、压缩由 harness 硬编码）不同。未来 Agent 系统中，harness 将暴露更多模型可调用的元操作（compact/retrieve/branch），模型策略将涵盖这些元操作的使用。

---

## 五、关联分析

### 5.1 与 Hermes Agent 上下文管理的关联

Hermes Agent 的 context-engineering-patterns skill 定义了"对话历史管理"和"工具输出修剪"两大支柱。AutoCompact 的三大失败模式（何时/保留什么/如何续接）直接映射：
- Hermes 的 `context-compressor` skill 做"渐进式上下文压缩"——对应 AutoCompact 的"何时"问题
- Hermes 的 `harness-checkpoint` skill 做"任务检查点机制"——对应"保留什么"问题
- Hermes 的 `session-boot` skill 做"会话启动检查恢复上下文"——对应"如何续接"问题

AutoCompact 的贡献在于证明这三者应作为**统一策略**训练而非分离处理。

### 5.2 与 MemDecay / Memory Compaction 系列论文的关联

此前精读的 MemDecay（2607.10582）和 Memory Compaction Rate-Distortion（2607.08032）都从记忆系统角度处理上下文压缩。AutoCompact 的差异：
- MemDecay 关注 KV cache 层面的区域感知驱逐（系统层）
- Memory Compaction 提供率失真理论框架（理论层）
- AutoCompact 关注 Agent 策略层面的压缩决策（策略层）

三者构成"系统→理论→策略"的完整栈。AutoCompact 补齐了策略层的空白——如何训练模型做压缩决策。

### 5.3 与 Beyond the Leaderboard（2607.05775）Agent 失败模式分类法的关联

此前精读的 Beyond the Leaderboard 定义了 Agent 六大失败模式。AutoCompact 的三大失败模式可映射：
- 触发错误 → "脚手架边际递减"失败模式（压缩在错误时机触发）
- 工作状态错误 → "组合性鸿沟"失败模式（摘要丢失关键组合信息）
- 续接错误 → "非线性复合"失败模式（压缩后行为与状态不一致导致级联失败）

---

## 六、拓展应用推荐

### 6.1 P0：Hermes Gateway 主动压缩决策门禁

**借鉴点**：AutoCompact 证明主动压缩在 context 溢出前就有收益。Hermes Agent 当前依赖长度触发式压缩（context-compressor skill 在接近窗口限制时触发）。

**可执行改进**：在 Hermes Gateway 层面增加"任务阶段感知"压缩触发器——当检测到任务阶段切换（如从"探索"切换到"实现"、从"调试"切换到"验证"）时，主动建议压缩。无需训练模型，先用规则式触发器（类似 SelfCompact 的 rubric），评估收益后考虑 SFT。

**优先级**：P0（收益高 × 可行性高，规则式触发器可立即实现）

### 6.2 P1：Hermes 工具输出修剪增加"工作状态摘要"模板

**借鉴点**：AutoCompact 的 `# Auto Context Summary` 格式——压缩后保留"已确立发现 + 相关代码与工作区状态 + 剩余动作"三段式。

**可执行改进**：Hermes 的 context-compressor skill 当前做"渐进式压缩"（大工具输出存文件+摘要预览），但摘要格式不统一。增加 `# Auto Context Summary` 模板，明确要求三段式结构，特别是"剩余动作"——这是 AutoCompact 证明最影响续接质量的部分。

**优先级**：P1（收益中 × 可行性高，修改 skill 模板即可）

### 6.3 P1：Hermes Skill 审查增加"摘要自洽性"检查

**借鉴点**：AutoCompact 定义并验证了"摘要自洽性"——记录的状态必须约束提议的下一步动作。SFT 无法保证，但可用程序化检查。

**可执行改进**：在 Hermes 的 harness-checkpoint skill 中增加检查点摘要的自洽性校验——如果检查点记录了"未解决问题"，提议的下一步动作必须与解决该问题相关；如果记录了"已完成"，下一步必须是验证或新任务。

**优先级**：P1（收益高 × 可行性中，需要实现校验逻辑）

### 6.4 P2：考虑 Hermes Agent 轨迹的在线纠正数据收集

**借鉴点**：AutoCompact 的 Judge-Guided 在线纠正——纠正后的输出被环境执行，塑造后续轨迹，产生因果连贯的训练数据。

**可执行改进**：Hermes Agent 的 evolver skill 当前做"错误模式分析→规则沉淀"，但分析是事后的。可在关键 cron job（如 defense-check）中增加"在线纠正"模式——Judge（更强的模型）审查每步输出，纠正后执行，收集纠正轨迹用于未来优化。

**优先级**：P2（收益高 × 可行性低，需要第二模型做 judge + 执行环境改造）

---

## 七、指南分析

### 7.1 适用场景判定

AutoCompact 的方法直接适用于：
- ✅ 长程编码 Agent 任务（>20步轨迹）——压缩收益最显著
- ✅ 有限推理预算场景——低预算区间增益最大
- ✅ 多阶段任务（探索→实现→验证）——阶段切换是自然压缩点
- ⚠️ 通用对话 Agent——需要适配"任务阶段"概念
- ❌ 短程单步任务——压缩开销可能超过收益

### 7.2 实施路径建议

对于想要借鉴 AutoCompact 的团队：
1. **先实现规则式主动压缩**（类似 SelfCompact 的 rubric）——零训练成本，验证收益
2. **收集压缩决策日志**——记录何时压缩、摘要内容、续接动作、任务结果
3. **用更强模型做离线 judge**——对日志做三类纠正标注
4. **SFT 训练**——用纠正轨迹微调
5. **GRPO 训练**——用任务成功奖励做 RL

### 7.3 关键陷阱警告

- **不要只训练"何时压缩"**：AutoCompact 的核心发现是三大失败模式需要同时监督。仅训练触发时机（如 SWE-Compressor 的离线插入）会忽略摘要质量和续接行为
- **不要依赖纯 SFT**：SFT 无法保证摘要自洽性。RL（即使是二元奖励）通过因果传导隐式学到此质量维度
- **不要忽略压缩执行本身**：同一 checkpoint 执行 vs 跳过压缩有显著差异（$0.10 预算下 19.9%），收益部分来自运行时压缩而非仅训练改善
- **RL 序列长度限制可接受**：论文 RL 用 32K 序列训练但评估用 256K，增益仍跨预算有效。不必等长训练序列

### 7.4 技术成熟度评估

- **理论贡献**：三大失败模式拆解 + 摘要自洽性概念——高价值理论框架
- **实验严谨度**：双基准 + 六档预算 + 多基线 + 消融——充分
- **可复现性**：使用 Qwen3-Coder-30B-A3B + SWE-Gym + GRPO，组件均开源，judge 用 GPT-5.5-Codex
- **实用就绪度**：方法需要训练流程，非即插即用。但核心思想（规则式主动压缩 + 工作状态摘要模板）可立即落地

---

## 八、关联论文

- **MemDecay (2607.10582)**：区域感知 KV cache 驱逐，系统层压缩。与本论文互补——MemDecay 管系统层，AutoCompact 管策略层
- **Memory Compaction Rate-Distortion (2607.08032)**：四层记忆压缩率失真框架，理论层。AutoCompact 的三大失败模式可映射到该框架的可逆/不可逆压缩
- **Beyond the Leaderboard (2607.05775)**：Agent 六大失败模式分类法。AutoCompact 的三大失败模式是其子集
- **CompactionRL (Li et al., 2026b)**：长度触发 + RL 联合训练，AutoCompact 的直接对比基线
- **SelfCompact (Li et al., 2026a)**：推理时 rubric 引导压缩，AutoCompact 的 SFT 前置基线
- **SWE-Compressor (Liu et al., 2026)**：离线 SFT 插入压缩调用，AutoCompact 的 SFT 对比基线
- **SPORK (2607.03333)**：自推测 fork 加速 Agent 工具调用，与 AutoCompact 都关注 Agent 执行效率但角度不同


## 相关笔记

- [ActKV动作导向KV缓存压缩精读](./2026-09-29-ActKV动作导向KV缓存压缩精读.md) — KV 缓存侧的压缩，与本文轨迹级压缩互补
- [当Agent何时能遗忘推理-长程上下文在线压缩与轨迹放大效应](./2026-09-28-ICLR论文精读-当Agent何时能遗忘推理-长程上下文在线压缩与轨迹放大效应.md) — 压缩时机与轨迹放大效应的理论对照
- [SparseEngine稀疏优先推理引擎精读](./2026-10-01-SparseEngine稀疏优先推理引擎精读-Agent多轮KV全生命周期抽象.md) — Agent 多轮 KV 全生命周期抽象，执行层视角
- LLM-as-a-Verifier（~/explore/ 目录）— 同为"何时该保留/丢弃信息"的决策机制，judge 引导数据收集同构
