# AutoTTS 深度分析：用 LLM Agent 自动发现 Test-Time Scaling 策略

> 日期：2026-05-19 | 论文：arXiv 2605.08083 | 机构：UMD/UVA/WUSTL/UNC/Google/Meta
> GitHub：https://github.com/zhengkid/AutoTTS | Star 124 | 2026-05-10 首次提交
> 关键词：Test-Time Scaling (TTS)、Coding Agent、Replay Environment、Confidence Momentum Controller

---

## 一、核心创新点

### 1.1 核心思想

**用 LLM Agent 自动发现 LLM 的推理时算力分配策略，而非人工设计启发式规则。**

传统方法：人类专家手写 TTS 策略（如 Self-Consistency、Early Stopping）
AutoTTS：人类只构建离线 Replay 环境 -> Coding Agent 迭代搜索最优策略代码 -> 无梯度更新

### 1.2 为什么重要

- **人工策略的局限**：SC@64、ESC、ASC 等策略是人类凭直觉设计的，存在大量超参，泛化差
- **搜索空间巨大**：何时开新分支、何时停止、何时剪枝——组合爆炸
- **AutoTTS 的解法**：把策略搜索变成代码搜索，让 Agent 在离线环境中反复试错

### 1.3 关键数据

| 指标 | 数值 |
|------|------|
| Token 节省 | ~69.5%（vs SC@64, beta=0.5） |
| 准确率 | 持平 SC@64（四骨干模型均值） |
| 发现成本 | $39.9 / 次（LLM API 费用） |
| 发现耗时 | 160 分钟 / 次 |
| 评估成本 | 0 次 LLM 调用（纯 Replay） |

---

## 二、技术架构

### 2.1 问题建模：MDP 形式化

将自适应推理建模为有限预算下的 MDP（Markov Decision Process）：

**状态** s_t = (q, m_t, I_t, l_t, Omega_t)
- q: 问题
- m_t: 已创建分支数
- I_t: 活跃分支集合
- l_t: 深度向量
- Omega_t: 已揭示的探测结果

**动作空间** A(s_t):
- BRANCH -- 开新分支
- CONTINUE(i) -- 分支 i 前进一个区间
- PROBE(i) -- 揭示分支 i 的探测结果（不推进深度）
- PRUNE(i) -- 剪掉分支 i
- ANSWER -- 终止，聚合答案

**目标函数**：max over (pi, beta) of E[ accuracy - gamma * cost ]

其中 beta 是单一元参数，确定性映射到所有内部超参。

### 2.2 系统架构（三层）

```
+-------------------------------------------+
|         Coding Agent Layer                |
|  Claude Code / Codex -> 提出策略代码       |
+-------------------------------------------+
|         Replay Environment                |
|  离线缓存的推理轨迹 -> 零 LLM 调用评估     |
+-------------------------------------------+
|         History & Feedback                |
|  beta-sweep 结果 + 执行轨迹 -> 下一轮输入  |
+-------------------------------------------+
```

### 2.3 发现流程（多轮迭代）

```
Round 1: Template -> Agent 生成 method.py -> Replay 评估 -> 记录结果+轨迹
Round 2: 历史+轨迹 -> Agent 修改 method.py -> Replay 评估 -> ...
Round N: 收敛 -> 最终 CMC 控制器
```

每轮：
1. Agent 读取历史结果和执行轨迹
2. 重写 method.py 中的 OptimalController 类
3. 在 Replay 环境中评估（0 LLM 调用）
4. 结果和轨迹存入历史

### 2.4 beta 参数化设计

每个候选控制器导出单一标量 beta + 确定性单调映射：
- beta=0.5 -> 省算力模式（省 69.5% tokens）
- beta=1.0 -> 准确率优先模式

关键优势：外层搜索退化为扫 beta，消除了对脆弱阈值的直接调参。

---

## 三、发现的控制器：CMC

AutoTTS 自动发现的最优策略名为 **Confidence Momentum Controller (CMC)**：

### 3.1 四大机制

| 机制 | 原理 | 效果 |
|------|------|------|
| 趋势感知停止 | 维护置信度 EMA，只在置信高且趋势非负时停止 | 避免在瞬时 spike 上误停 |
| 耦合宽深控制 | EMA delta 联动：强置信增益抑制新分支；停滞则拓宽搜索 | 自适应分配算力 |
| 对齐感知深度 | 最新答案与池中胜者匹配的分支获额外探测步 | 集中算力到共识方向 |
| 保守分支放弃 | 持续偏离多轮后才剪枝，且保底 2 个活跃分支 | 防止过早收敛 |

### 3.2 与人工策略对比

| 策略 | 核心思路 | 缺陷 | CMC 如何改进 |
|------|----------|------|-------------|
| SC@64 | 64 路并行投票 | 固定算力，无自适应 | 自适应分支数+深度 |
| ASC | Beta 置信度早停 | 阈值需人工调 | EMA 趋势动态停止 |
| ESC | 滑窗一致性停止 | 只看一致性，不看趋势 | 趋势感知 |
| Parallel-Probe | 预热+剪枝+多数终止 | 人工规则组合 | Agent 自动发现规则 |

---

## 四、代码结构分析

```
AutoTTS/
+-- efficient_reasoning_controller/
    +-- eval/                      # 独立评估 (Way A)
    +-- logs/search_history/       # 搜索过程归档
    +-- test_environment/          # 持出测试集（不暴露给 Agent）
    +-- workspace/
        +-- code_base/
        |   +-- controller_api.py  # 基类接口：LLMDesignedMethod
        |   +-- method.py          # 活跃控制器实现
        |   +-- method.template.py # 每轮重置的模板
        |   +-- eval.py            # 评估入口
        |   +-- data_loader.py     # Replay 环境加载
        |   +-- environment/       # 搜索集 Replay 数据
        |   +-- history/           # 种子基线 + 搜索历史
        +-- controller_search/
            +-- run_workflow.sh    # 启动多轮搜索
            +-- workflow_propose_critic.py
            +-- claude_proposer.py # Claude Code 后端
            +-- codex_proposer.py  # OpenAI Codex 后端
            +-- prompts/           # Agent 提示词
```

### 4.1 关键接口

LLMDesignedMethod 抽象基类：
- 属性：NAME（策略名）
- 抽象方法：solve(question) -> str（运行完整推理控制算法，返回最终答案）
- 适配器：MethodStrategyAdapter 包装为旧评估管线兼容接口

### 4.2 Agent 后端

- **Claude Code**：主要后端，通过 claude-agent-sdk (v0.1.58) 调用
- **OpenAI Codex**：备选后端
- 使用 OpenRouter 作为 API 代理（支持 Claude Sonnet 4.6 / Opus 4.6）

---

## 五、评估体系

### 5.1 训练/测试分离

- **搜索集**：AIME24（Replay 环境构建 + Agent 发现用）
- **测试集**：AIME25 / HMMT25（完全持出，Agent 从未见过）

### 5.2 骨干模型

Qwen3 系列四个规模：8B / 14B / 32B / 235B (MoE)

### 5.3 核心结论

1. **泛化性强**：AIME24 上发现的策略在 AIME25/HMMT25 上仍然有效
2. **Pareto 前沿超越**：CMC 在准确率-token 权衡上全面超越人工基线
3. **beta=0.5 省算力模式**：省 69.5% tokens，准确率持平
4. **beta=1.0 准确率模式**：8 个对比单元中 5 个超越所有基线

---

## 六、对我们的启发

### 6.1 可借鉴的模式

| 模式 | 说明 | 适用场景 |
|------|------|----------|
| 离线 Replay 环境 | 一次性收集轨迹，后续评估零成本 | 任何需要反复评估策略的场景 |
| Agent 代码搜索 | 让 Agent 写策略代码而非人工设计 | 复杂规则/策略系统 |
| beta 参数化 | 单一标量映射到所有超参 | 需要简洁控制面的系统 |
| 轨迹反馈 | 不只给结果，还给出逐步执行轨迹 | 帮助 Agent 定位问题 |

### 6.2 与 Hermes Agent 的关联

- **Cron 调度策略**：可用类似思路让 Agent 自动发现最优调度参数
- **错误修复策略**：Replay 环境模式可用于自动修复策略搜索
- **工具选择策略**：类似 BRANCH/PRUNE 的动作空间可应用于工具调用决策

### 6.3 局限性

1. **需要预构建 Replay 环境**：一次性成本高（需大量推理轨迹）
2. **只适用于可离线评估的场景**：在线交互场景无法直接使用
3. **发现成本 $39.9**：虽不贵但不免费
4. **策略迁移性**：AIME->HMMT 有效，但跨领域（如代码->数学）未验证
5. **依赖 Claude Code CLI**：不是纯 Python 方案，需要 Node.js 环境

---

## 七、知识缺口与进一步探索

1. Replay 环境的构建成本（N 条并行轨迹的具体数量）
2. 跨领域迁移效果（数学->代码->推理）
3. 与 RL-based 策略搜索（如 GRPO）的对比
4. 是否可以用更便宜的模型（如 Qwen3-8B）做 Agent 后端
5. CMC 的理论基础：为什么 EMA 趋势比原始置信度更好

---

## 八、总结

AutoTTS 是一篇方法论文的工程实现，核心理念是 **"LLM 改进 LLM"**：

> 用 LLM Agent 在离线 Replay 环境中自动搜索最优推理策略，替代人类专家手写启发式。

**三个关键设计决策**：
1. **Replay 环境**：一次构建，零成本评估
2. **代码搜索**：Agent 写策略代码，不是调参数
3. **beta 参数化**：单一标量控制所有超参

**工程启示**：这种"构建环境 -> Agent 搜索 -> 零成本评估"的模式可以推广到任何需要策略发现的场景。

---

*论文引用：Zheng et al., "LLMs Improving LLMs: Agentic Discovery for Test-Time Scaling", arXiv:2605.08083, 2026*

## 相关笔记
- [Agent Skills才是关键抽象层](../2026-04-02-Agent Skills才是关键抽象层.md)
- [MiniMax Office Skills全家桶](../2026-04-02-MiniMax Office Skills全家桶.md)
- [OpenClaw-paper-review-skill](../2026-04-03-OpenClaw-paper-review-skill.md)
- [SelfImproving-Agent-CLI-infra](../2026-04-05-SelfImproving-Agent-CLI-infra.md)
- [SKILL-md-ai-agent-skills](../2026-04-09-SKILL-md-ai-agent-skills.md)
- [distill-skill-yupi](../2026-04-12-distill-skill-yupi.md)
- [歸藏PPT-Skill-电子杂志风网页演示](../2026-04-24-歸藏PPT-Skill-电子杂志风网页演示.md)
- [竞品吸收笔记-khazix-skills](../2026-04-29-竞品吸收笔记-khazix-skills.md)
- [SkillClaw-analysis](../2026-05-02-SkillClaw-analysis.md)
- [github-ai-trending-mattpocock-skills](../2026-05-05-github-ai-trending-mattpocock-skills.md)
- [lewislulu-html-ppt-skill-analysis](../2026-05-06-lewislulu-html-ppt-skill-analysis.md)
- [skill-building-invoice-automation](../2026-05-10-skill-building-invoice-automation.md)
- [softwarecopyright-skill-analysis](../2026-05-10-softwarecopyright-skill-analysis.md)
- [开源AI模型工具2025春季爆发](../2026-05-18-开源AI模型工具2025春季爆发.md)
- [f5-tts-voice-cloning-incremental](2026-05-18-f5-tts-voice-cloning-incremental.md)
- [skill-lifecycle-management-deep-dive](2026-05-18-skill-lifecycle-management-deep-dive.md)
- [tts-stt-pipeline-optimization-deep-dive](2026-05-19-tts-stt-pipeline-optimization-deep-dive.md)
- [llm_wiki分析与Skill进化](2026-05-20-llm_wiki分析与Skill进化.md)
- [f5-tts-zero-shot-voice-cloning-deep-dive-20260518](f5-tts-zero-shot-voice-cloning-deep-dive-20260518.md)
- [local-tts-stt-optimization-20260519](local-tts-stt-optimization-20260519.md)
- [OpenClaw核心机制Skills全解析](../orphan/2026-04-02-OpenClaw核心机制Skills全解析.md)
- [OpenClaw-Skills-handbook](../orphan/2026-04-07-OpenClaw-Skills-handbook.md)
- [CyberVerse公众号HTML模板分析](../orphan/2026-05-03-CyberVerse公众号HTML模板分析.md)
- [国自然申请书AI-Skill流水线](../orphan/2026-05-04-国自然申请书AI-Skill流水线.md)
- [数据血缘-lineage-工具全景](../orphan/2026-05-09-数据血缘-lineage-工具全景.md)
- [HTML的不合理有效性-Claude-Code-团队](../orphan/2026-05-16-HTML的不合理有效性-Claude-Code-团队.md)
- [20260512-10-skill-学术去ai味框架](../orphan/20260512-10-skill-学术去ai味框架.md)
- [build-ai-cli](../orphan/build-ai-cli.md)
- [frontend-slides-skill](../orphan/frontend-slides-skill.md)
- [hermes-skill-top10-2026w18](../orphan/hermes-skill-top10-2026w18.md)
- [skills-apple](../orphan/skills-apple.md)
- [skills-catalog](../orphan/skills-catalog.md)
- [skills-data-science](../orphan/skills-data-science.md)
- [skills-dogfood](../orphan/skills-dogfood.md)
- [skills-email](../orphan/skills-email.md)
- [skills-github](../orphan/skills-github.md)
- [skills-leisure](../orphan/skills-leisure.md)
- [skills-logo-generator-skill](../orphan/skills-logo-generator-skill.md)
- [skills-smart-home](../orphan/skills-smart-home.md)
- [skills-social-media](../orphan/skills-social-media.md)
- [skills-team-roles](../orphan/skills-team-roles.md)
- [skills-autonomous-ai-agents](../skills-autonomous-ai-agents.md)
- [skills-creative](../skills-creative.md)
- [skills-devops](../skills-devops.md)
- [skills-gaming](../skills-gaming.md)
- [skills-mcp](../skills-mcp.md)
- [skills-media](../skills-media.md)
- [skills-mlops](../skills-mlops.md)
- [skills-note-taking](../skills-note-taking.md)
- [skills-openclaw-imports](../skills-openclaw-imports.md)
- [skills-overview](../skills-overview.md)
- [skills-productivity](../skills-productivity.md)
- [skills-red-teaming](../skills-red-teaming.md)
- [skills-research](../skills-research.md)
- [skills-software-development](../skills-software-development.md)
