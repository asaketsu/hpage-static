# MOSS: 自主Agent系统通过源码级重写实现自进化

- 📅 2026-05-24
- ⭐ 4.5/5 — 首个在Agent harness层实现源码级自进化的系统，直接点名Hermes Agent，极具参考价值
- 🏷️ #AI-Agent #自进化 #源码重写 #OpenClaw #Hermes
- 📰 arXiv: 2605.22794 | 2026-05-21
- 🔗 https://arxiv.org/abs/2605.22794

## 元数据

- **标题**: MOSS: Self-Evolution through Source-Level Rewriting in Autonomous Agent Systems
- **作者**: Qianshu Cai, Yonggang Zhang, Xianzhang Jia, Wei Xue, Jun Song, Xinmei Tian, Yike Guo
- **机构**: 中国科学技术大学（MoE脑启发智能感知与认知重点实验室）、香港科技大学、香港浸会大学
- **arXiv ID**: 2605.22794v1
- **领域**: cs.AI（人工智能）
- **代码**: https://github.com/dav-joy-thon/MOSS

## 核心问题与研究动机

当前部署的自主Agent系统（如Hermes Agent、Claude Assistant等）在部署后本质上是**静态的**——它们无法从用户交互中学习，相同的失败模式会反复出现直到人工修复发布新版本。

现有的自进化Agent（Hermes Agent、SkillClaw、Capability Evolver、EvoAgentX等）将进化范围限制在**文本可编辑artifact**上：skill文件、prompt配置、memory schema、workflow graph。但**Agent harness**——路由、状态管理、dispatch、hook排序、mediator、session生命周期——从未被Agent自身修改。

这一限制是**物理层面的**：文本artifact的编辑只能改变"Agent自己怎么想"（说什么、调用哪个skill、如何分解子目标），无法改变"harness替Agent做的决定"。当失败源于harness层（消息路由错误、hook顺序错误、session状态损坏、并发skill间的原子性bug）时，无论怎么修改skill、prompt或memory都无法触及。

**核心论点**：源码级适配是一个根本性更强的进化媒介——它是图灵完备的，是所有文本可编辑scope的严格超集，确定性生效（不依赖base model compliance），且不会因长上下文漂移而退化。

## 方法论（详细）

### 系统架构（四层）

MOSS系统由四个组件构成：

1. **Substrate（基底）**：被进化的Agent系统本身（论文使用OpenClaw作为实验基底）。包含完整的harness层——路由、hook链、mediator、dispatch、session管理。

2. **Control Surface（控制面）**：MOSS的核心编排器，管理进化pipeline的每个阶段顺序和判定。不直接生成代码，而是将代码修改委托给外部coding-agent CLI。

3. **External Coding Agent（外部编码Agent）**：可插拔的代码生成器（如Claude Code、Codex CLI），接收MOSS的诊断信息和修复计划，生成具体的代码变更。

4. **Host-Daemon Supervision（宿主守护进程）**：负责构建candidate镜像、启动ephemeral trial worker、执行in-place container swap。包含健康检查探针和回滚机制。

### 进化流程（Directed Evolution + 7阶段Pipeline）

MOSS采用**定向进化**而非随机搜索：

**输入**：自动策划的**生产失败证据批次**（production-failure evidence batch）

**7阶段Pipeline**：
1. **Task-Evaluate**：对baseline transcript打分，生成keypoint matrix，锁定后续评估标准
2. **Locate**：分析baseline transcript，定位失败根因在harness中的具体位置
3. **Plan**：将诊断转化为具体修复方案（设计层面）
4. **Plan-Review**：人工/自动审查修复方案
5. **Implement**：外部coding-agent执行代码修改（single commit）
6. **Code-Review**：代码审查门禁
7. **Verdict**：在ephemeral trial worker中回放失败批次，对比keypoint matrix，决定是否收敛

### 部署机制

- **验证**：candidate镜像在ephemeral trial worker中回放原始失败批次
- **晋升**：用户同意门控（user-consent-gated）+ in-place container swap
- **回滚**：health-probe-gated rollback，确保新镜像不引入regression
- **效果**：代码修改直接作用于harness本身（路由、hook、mediator），不是任何文本artifact

## 关键实验结果与数据

### 实验设置
- **基底Agent**: OpenClaw + DeepSeek V3.2
- **测试任务**: 4个运维/合规审计类任务（中英文各2对）
  - T141zh/T142：SLA合规审计（中/英）
  - T137zh/T138：补货链检查（中/英）
- **评分**: 外部grader 0-1量表，0.75为通过阈值

### 核心结果

Baseline（进化前）：
- 四任务平均分：0.2526
- 所有任务远低于0.75通过线
- 典型失败：只列出部分相关ticket、标记其余为"数据不完整"、相邻ticket间客户名称混淆

Iteration-1（进化后）：
- 四任务平均分：0.6100（+0.3574，提升142%）
- T138（英文补货链检查）：0.9049，全部3次试验通过0.75阈值
- T141zh/T142（SLA审计）：从0.25-0.33提升至0.53-0.55
- T137zh（中文补货链检查）：1次通过、2次未过

### 具体修复内容
- 修改3个文件，177行新增，1行删除
- **新增annotation branch**：当execution path返回多实体payload时注入显式使用提示
- **新增pre-call deny gate**：阻止特定batched-shell模式，引导Agent使用单独的、可独立解析的调用
- **新增mediator测试文件**：覆盖两个修复面

关键结论：模型和任务定义完全不变，**harness变更是性能提升的直接原因**。

## 创新点分析

1. **首次在应用级Agent系统实现源码层自进化**：将可编辑范围从skill/prompt/memory/workflow扩展到harness本身（路由、状态管理、hook排序、dispatch），这是之前所有系统都无法触及的。

2. **确定性pipeline替代概率性推理**：MOSS不依赖base model来"遵守"文本指令，而是通过代码修改确定性改变行为，从根本上避免了长上下文漂移导致的退化。

3. **生产失败驱动而非benchmark驱动**：进化锚定在真实用户交互中产生的失败证据，而非标准化的benchmark分数。

4. **可插拔coding-agent架构**：代码修改委托给外部coding-agent CLI（如Claude Code），MOSS自身只负责pipeline编排和判定，实现关注点分离。

5. **Table 1直接点名Hermes Agent**：论文的对比表格明确列出Hermes Agent（Nous Research, 2024）在Skill/Prompt/Memory三个维度有进化能力，但在Harness维度为×，这正是MOSS要填补的gap。

## 局限性与未来方向

1. **单次迭代验证**：仅展示了iteration-1的结果（0.25→0.61），未展示多轮迭代的累积效果和收敛特性。

2. **任务范围窄**：仅测试了4个运维/合规审计任务，未覆盖更广泛的Agent能力（代码生成、创意写作、多模态等）。

3. **安全风险**：源码级自修改引入了更大的攻击面——如果production-failure evidence被恶意构造，可能导致harness被注入恶意代码。

4. **评估集即训练集**：进化用的批次也是测试用的批次，存在数据泄露嫌疑（论文承认了这一点，以可复现性换取真实性）。

5. **用户同意门禁的实用性**：生产环境中每次进化都需要用户确认，可能成为瓶颈；auto-acknowledge模式则削弱了安全门禁。

6. **未涉及多Agent协同进化**：仅针对单一Agent系统，未探讨多个Agent间的co-evolution。

## 借鉴点（关联 Hermes Agent / Jetson Orin / 量化交易）

### 对 Hermes Agent 的直接启发
- **当前gap确认**：论文Table 1明确指出Hermes Agent的进化局限在Skill/Prompt/Memory层，harness层的bug（如消息路由、hook顺序、session状态）无法通过现有机制修复。这与我们evolver skill的实际体验一致——harness层的结构性问题只能靠人工代码修复。
- **可行路径**：MOSS的7阶段pipeline（特别是Locate→Plan→Implement→Verdict）可以作为Hermes Agent下一步evolution的架构蓝图。特别是"失败证据批次自动策划"+"ephemeral trial worker回放验证"的组合，可以直接嫁接到现有cron/watchdog体系上。
- **与hermes-code-mod skill的关联**：hermes-code-mod已经具备修改Hermes核心代码的能力，但缺乏MOSS式的自动化pipeline（自动诊断→计划→实现→验证）。可以作为MOSS的"External Coding Agent"组件。

### 对量化交易系统的启发
- **策略引擎的源码级自进化**：量化策略的某些结构性问题（如信号组合逻辑、风控规则执行顺序）类似Agent harness的bug，单纯调参无法解决。MOSS的思路可迁移为：自动收集回测失败案例→定位策略引擎结构缺陷→生成修复commit→回放验证。

### 对 Jetson Orin 边缘部署的启发
- **推理pipeline的结构性优化**：TensorRT推理链的某些性能瓶颈（如内存分配策略、batch调度逻辑）不在模型权重层面，而是在推理引擎代码层面。MOSS式自动诊断+代码修复可应用于推理引擎优化。

## 关联论文

- **SICA**: 证明Agent可以编辑自身实现并提升SWE-Bench分数，建立可行性基线
- **Darwin Gödel Machine**: 将源码自进化重构为agent变体归档上的开放式搜索
- **HyperAgents**: 将进化元过程本身也变为可编辑
- **Meta-Harness**: 暴露过去执行trace给coding-agent proposer，增强迭代改进
- **Hermes Agent (Nous Research, 2024)**: 文本层进化代表，MOSS的直接对比对象
- **SkillClaw (Ma et al., 2026)**: 共享skill语料库的文本层进化
- **EvoAgentX**: prompt + workflow graph层面的文本进化
- **Capability Evolver**: behavioral genes + memory capsules层面的进化

## 相关笔记
- [Agent元认知-LLM不确定性感知](../2026-05-18-Agent元认知-LLM不确定性感知.md)
- [SmallRustHermes-Agent自我进化三个闭环](../2026-05-18-SmallRustHermes-Agent自我进化三个闭环.md)
- [agent-memory-systems-comparison](../2026-05-18-agent-memory-systems-comparison.md)
- [具身智能机器人2025十大趋势](../2026-05-18-具身智能机器人2025十大趋势.md)
- [Qwen3.7-Agent Frontier](../2026-05-21-Qwen3.7-Agent Frontier.md)
- [react-agent-llm-agentic-training-research](../2026-05-21-react-agent-llm-agentic-training-research.md)
- [Agent自我进化与学习系统-深度研究](../2026-05-22-Agent自我进化与学习系统-深度研究.md)
- [Hermes-Agent四层记忆架构深度分析](../2026-05-22-Hermes-Agent四层记忆架构深度分析.md)
- [OpenClaw日常聊天黑化Agent-ULSPB安全研究](../2026-05-22-OpenClaw日常聊天黑化Agent-ULSPB安全研究.md)
- [Domain-Camouflaged-Injection-Attacks-域伪装注入绕过多Agent检测](../2026-05-23-Domain-Camouflaged-Injection-Attacks-域伪装注入绕过多Agent检测.md)
- [Microsoft取消ClaudeCode许可-AI编码战企业政治](../2026-05-23-Microsoft取消ClaudeCode许可-AI编码战企业政治.md)
- [Superset-YC-P26-AI-Agent-IDE](../2026-05-23-Superset-YC-P26-AI-Agent-IDE.md)
- [Cloudflare-Agents-Week-2026-Agentic-Cloud全栈基础设施](../2026-05-24-Cloudflare-Agents-Week-2026-Agentic-Cloud全栈基础设施.md)
- [PiAgent深度分析](../2026-05-24-PiAgent深度分析.md)
- [不管用ClaudeCode还是OpenClaw先记住这12个知识](../ai-agent/2026-04-15-不管用ClaudeCode还是OpenClaw先记住这12个知识.md)
- [RD-Agent-Quant-multi-agent-quant-framework-deep-dive](2026-05-18-RD-Agent-Quant-multi-agent-quant-framework-deep-dive.md)
- [agent-self-evolution-quant-trading](2026-05-18-agent-self-evolution-quant-trading.md)
- [多模态Agent框架对比2026-深度探索](2026-05-18-多模态Agent框架对比2026-深度探索.md)
- [IBM2026多智能体趋势](2026-05-19-IBM2026多智能体趋势.md)
- [agent-self-evolution-reflexion-metacognition](2026-05-19-agent-self-evolution-reflexion-metacognition.md)
- [AgentSelfEvolution-LearningSystem-深度探索](2026-05-20-AgentSelfEvolution-LearningSystem-深度探索.md)
- [Hermes-Agent源码解析-越用越聪明的秘密](2026-05-20-Hermes-Agent源码解析-越用越聪明的秘密.md)
- [TencentDB-Agent-Memory架构深度分析与进化建议](2026-05-20-TencentDB-Agent-Memory架构深度分析与进化建议.md)
- [Agent自我进化-Reflexion-ReAct-元认知框架](2026-05-21-Agent自我进化-Reflexion-ReAct-元认知框架.md)
- [开源具身智能项目横评-LeRobot-OpenVLA-RT2](2026-05-21-开源具身智能项目横评-LeRobot-OpenVLA-RT2.md)
- [零信任安全2026-Agent系统新攻击面与安全基线-深度蒸馏](2026-05-21-零信任安全2026-Agent系统新攻击面与安全基线-深度蒸馏.md)
- [GROW开放世界VLM-Agent强化学习框架](2026-05-22-GROW开放世界VLM-Agent强化学习框架.md)
- [agent-evolution-rag](2026-05-23-agent-evolution-rag.md)
- [agent-capability-boundary-detection-20260518](agent-capability-boundary-detection-20260518.md)
- [agent-drift-stability-degradation-20260518](agent-drift-stability-degradation-20260518.md)
- [agent-stability-degradation-drift-detection](agent-stability-degradation-drift-detection.md)
- [tradingagents-cn-deep-20260520](tradingagents-cn-deep-20260520.md)
- [google-a2a-protocol-multi-agent-2026-05-19](../google-a2a-protocol-multi-agent-2026-05-19.md)
- [hermes-agent-arxiv-search](../hermes-agent-arxiv-search.md)
