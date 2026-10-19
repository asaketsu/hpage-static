# Agent 能力边界自动探测：压力测试→弱项识别→定向学习→再测试

> 深度研究笔记 | 2026-05-18 07:45 | 网络：不可用（Tavily + curl 均失败，纯本地知识蒸馏）

---

## 一、核心概念

### 1.1 能力边界（Capability Boundary）定义

**能力边界**是指 AI Agent 在给定任务域中，能够可靠、稳定、正确执行操作的范围。超出此范围，Agent 的行为变得不可预测、质量下降或完全失败。

能力边界不是静态的——它随以下因素变化：
- **模型版本更新**：新模型可能扩展某些能力但退化其他能力（"能力漂移"）
- **上下文长度**：接近 context window 上限时，指令遵循率下降
- **工具复杂度**：工具链越长，累积错误率越高
- **任务类型**：推理密集 vs 检索密集 vs 创意密集，各有不同边界

### 1.2 自动探测框架（Auto-Probe Framework）

完整的自动探测框架包含四个阶段闭环：

```
┌─────────────┐    ┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│  Stress Test │───→│  Weakness ID │───→│  Directed    │───→│  Re-test &   │
│  (压力测试)   │    │  (弱项识别)   │    │  Learning    │    │  Verify      │
│             │←───│              │←───│  (定向学习)   │←───│  (再测试验证) │
└─────────────┘    └──────────────┘    └──────────────┘    └──────────────┘
                         │                                         │
                         └─────────→ Capability Map ──────────────┘
                                     (能力图谱持续更新)
```

这个闭环类似于软件工程中的 **CI/CD 管线**，但目标是 Agent 的认知能力而非代码质量。

---

## 二、技术细节

### 2.1 压力测试方法论

#### 2.1.1 渐进式难度提升（Progressive Difficulty Scaling）

核心思想：从简单任务开始，逐步增加难度维度，直到 Agent 失败。

```python
class DifficultyDimension(Enum):
    CONTEXT_LENGTH = "context_length"      # 上下文长度
    TOOL_CHAIN_DEPTH = "tool_chain_depth"  # 工具调用链深度
    AMBIGUITY = "ambiguity"                # 指令模糊度
    MULTI_TASK = "multi_task"              # 并行任务数
    DISTRACTION = "distraction"            # 干扰信息量
    TIME_PRESSURE = "time_pressure"        # 时间约束

class StressTestSuite:
    def __init__(self, agent, dimensions):
        self.agent = agent
        self.dimensions = dimensions
        self.results = {}

    def run_progressive_test(self, base_task, dimension, levels=10):
        """在单个维度上渐进加压测试"""
        results = []
        for level in range(1, levels + 1):
            test_case = self.scale_difficulty(base_task, dimension, level)
            result = self.agent.execute(test_case)
            score = self.evaluate(result, test_case.expected_output)
            results.append({"level": level, "score": score, "task": test_case})
            if score < 0.5:  # 能力断崖点
                break
        self.results[dimension] = results
        return results
```

#### 2.1.2 多维交叉测试（Cross-Dimensional Stress）

单维度测试可能遗漏维度交互效应。实际场景中，Agent 往往在**多维度同时压力**时暴露问题。

```python
def cross_dimensional_stress(agent, dimensions, base_task):
    """测试多个维度同时加压时的表现"""
    from itertools import combinations
    results = {}
    for combo in combinations(dimensions, 2):
        for level in [3, 5, 7]:
            test = base_task.copy()
            for dim in combo:
                test = scale_difficulty(test, dim, level)
            result = agent.execute(test)
            key = f"{'_'.join(d.value for d in combo)}_L{level}"
            results[key] = evaluate(result)
    return results
```

#### 2.1.3 对抗性测试用例生成

基于已知 Agent 弱点模式生成专门测试：

| 弱点模式 | 测试策略 | 示例 |
|----------|---------|------|
| 指令遗忘 | 长上下文中插入早期约束 | 在第2条消息中要求格式，第15条消息检查 |
| 工具幻觉 | 请求不存在的工具 | 要求用 `nmap` 扫描（但 Agent 没有此工具） |
| 数字推理 | 多步数学计算 | 复合利率计算 + 汇率换算 |
| 格式遵循 | 复杂输出格式要求 | 要求输出特定 JSON schema + 嵌套层级 |
| 安全绕过 | 社会工程测试 | 伪装成管理员要求绕过限制 |

### 2.2 弱项识别算法

#### 2.2.1 能力画像（Capability Profiling）

```python
@dataclass
class CapabilityProfile:
    agent_id: str
    timestamp: datetime
    dimensions: Dict[str, float]  # 各维度得分 0-1
    failure_patterns: List[FailurePattern]
    confidence_intervals: Dict[str, Tuple[float, float]]

    def weakest_dimensions(self, n=3) -> List[str]:
        return sorted(self.dimensions, key=self.dimensions.get)[:n]

    def improvement_potential(self) -> Dict[str, float]:
        """计算每个维度的提升潜力（距离满分的距离 × 重要性权重）"""
        weights = load_dimension_weights()
        return {
            dim: (1.0 - score) * weights.get(dim, 1.0)
            for dim, score in self.dimensions.items()
        }
```

#### 2.2.2 失败模式聚类

将测试失败用例进行聚类，识别系统性弱点：

```python
from sklearn.cluster import DBSCAN
import numpy as np

def cluster_failures(failure_cases):
    """对失败案例进行聚类，识别系统性弱点模式"""
    features = np.array([case.to_feature_vector() for case in failure_cases])
    clustering = DBSCAN(eps=0.3, min_samples=3).fit(features)

    patterns = {}
    for label in set(clustering.labels_):
        if label == -1:
            continue  # 噪声点
        cluster_cases = [c for c, l in zip(failure_cases, clustering.labels_) if l == label]
        pattern = FailurePattern(
            name=f"pattern_{label}",
            common_features=extract_common_features(cluster_cases),
            frequency=len(cluster_cases),
            severity=compute_severity(cluster_cases)
        )
        patterns[pattern.name] = pattern
    return patterns
```

#### 2.2.3 元认知不确定性检测

让 Agent 对自己的回答进行置信度评估：

```python
def assess_uncertainty(agent, task, n_samples=5):
    """通过多次采样检测 Agent 的不确定性"""
    responses = [agent.execute(task) for _ in range(n_samples)]

    # 方法 1：一致性检查
    consistency = compute_pairwise_similarity(responses)

    # 方法 2：自评置信度
    confidences = []
    for resp in responses:
        prompt = f"On a scale of 1-10, how confident are you in this answer?"
        conf = agent.execute(MetaTask(prompt))
        confidences.append(conf.score)

    # 高不一致 + 低置信度 = 确定的弱项
    uncertainty_score = 1 - consistency + (1 - np.mean(confidences) / 10)
    return uncertainty_score
```

### 2.3 定向学习策略

#### 2.3.1 课程学习（Curriculum Learning）

根据弱项设计个性化学习路径：

```python
class AgentCurriculum:
    def __init__(self, capability_profile):
        self.profile = capability_profile
        self.learning_path = []

    def generate_curriculum(self):
        """基于能力画像生成个性化课程"""
        weakest = self.profile.weakest_dimensions(n=3)
        potential = self.profile.improvement_potential()
        prioritized = sorted(weakest, key=lambda d: potential[d], reverse=True)

        for dim in prioritized:
            boundary = self.profile.dimensions[dim]
            start_level = max(1, int(boundary * 10) - 2)
            curriculum = self._build_graded_tasks(dim, start_level)
            self.learning_path.extend(curriculum)
        return self.learning_path
```

#### 2.3.2 少样本示例注入（Few-shot Injection）

针对识别的弱点，注入专门的示例到 system prompt 或知识库：

```python
def inject_weakness_examples(agent, weakness_pattern, n_examples=5):
    """针对特定弱点模式注入少样本示例"""
    examples = load_high_quality_examples(weakness_pattern.category, n_examples)
    enhanced_prompt = agent.system_prompt + "\n\n## 针对性参考示例\n"
    for i, ex in enumerate(examples):
        enhanced_prompt += f"\n### 示例 {i+1}\n输入: {ex.input}\n输出: {ex.expected_output}\n"
    agent.update_system_prompt(enhanced_prompt)
```

#### 2.3.3 Skill 自动生成

将学习成果固化为可复用的 Skill：

```python
def learned_to_skill(learning_result):
    """将学习成果转化为 Skill"""
    if learning_result.improvement >= 0.3 and learning_result.reusability >= 3:
        skill_content = f"""---
name: {learning_result.domain}-enhanced
description: 针对性增强的 {learning_result.domain} 能力
---

# {learning_result.domain} Enhanced

## 获取的能力模式
{learning_result.patterns}

## 关键示例
{learning_result.best_examples}
"""
        return skill_manage(action='create', name=f"{learning_result.domain}-enhanced",
                          content=skill_content)
```

### 2.4 再测试验证

#### 2.4.1 A/B 对比测试

```python
def ab_test_improvement(agent_before, agent_after, test_suite):
    """对比学习前后的能力变化"""
    results_before = run_test_suite(agent_before, test_suite)
    results_after = run_test_suite(agent_after, test_suite)

    improvements = {}
    for dim in results_before:
        delta = results_after[dim] - results_before[dim]
        improvements[dim] = {
            'before': results_before[dim],
            'after': results_after[dim],
            'delta': delta,
            'significant': abs(delta) > 0.05
        }
    return improvements
```

#### 2.4.2 回归测试

确保学习新能力没有导致其他能力退化：

```python
def regression_check(agent, baseline_results, test_suite):
    """检查是否出现能力回归"""
    current_results = run_test_suite(agent, test_suite)
    regressions = []
    for dim, score in current_results.items():
        baseline = baseline_results.get(dim, 1.0)
        if score < baseline - 0.05:
            regressions.append({
                'dimension': dim,
                'baseline': baseline,
                'current': score,
                'regression': baseline - score
            })
    return regressions
```

---

## 三、实践案例

### 3.1 OpenCompass / AgentBench 模型评估

**OpenCompass**（上海 AI Lab）是最全面的 LLM 评估框架：
- 支持超过 50 个评估维度
- 包含知识、推理、代码、Agent 能力等分项
- 提供 OpenCompass 排行榜跟踪模型进化

**AgentBench**（清华）专门评估 LLM Agent 能力：
- 8 个不同环境（OS、数据库、Web、游戏等）
- 多轮交互评估
- 长程任务规划能力

**关键发现**：大部分模型在单轮任务中表现优秀，但在多轮长程任务中性能显著下降（平均下降 30-50%）。这正是"能力边界"的典型表现。

### 3.2 Hermes Agent 自身应用

Hermes Agent 可以将此框架应用于自身：

| 阶段 | 现有 Skill | 扩展建议 |
|------|-----------|---------|
| 压力测试 | skill-stress-test | 增加多维度渐进式测试 |
| 弱项识别 | error-case-library | 增加自动化聚类分析 |
| 定向学习 | auto-learner | 根据弱项自动调整学习优先级 |
| 验证 | ❌ 缺失 | 新建 A/B test + regression check |

### 3.3 METR 评估框架

METR（前身为 OUGHT）专注于 LLM Agent 的自动评估：
- 标准化任务集（autograding, fact-checking 等）
- **时间到成功率曲线**（Time-to-Success Curve）
- 启发：对 Hermes Agent 可以定义类似指标——给定不同时间限制，任务完成率如何变化

### 3.4 SWE-bench / HumanEval 类型评估

**SWE-bench**（Princeton）：给定 GitHub issue，Agent 生成 PR。当前最佳模型仅能解决约 50% 实例。

**HumanEval / MBPP**（代码生成）：
- pass@1 < 60%（大多数模型）
- pass@10 > 90%（多次尝试后）
- 启发：评估代码生成能力时，不仅看单次成功，还要看多次尝试的改进曲线

---

## 四、对 Hermes Agent 的实践启发

### 4.1 现有 Skill 整合建议

| 现有 Skill | 整合建议 | 优先级 |
|------------|---------|--------|
| skill-stress-test | 扩展为多维度渐进式测试框架 | P1 |
| error-case-library | 增加聚类分析能力，自动识别系统性弱点 | P1 |
| auto-learner | 接收弱项识别结果，动态调整学习优先级 | P2 |
| evolver | 增加能力回归检测，确保进化不退化 | P2 |
| idle-busy-loop | 增加"能力巡检"Phase，定期做轻量级自测 | P3 |

### 4.2 最小可行实现（MVP）

```python
# capability-probe-mvp.py — 可集成到 Hermes Cron

class CapabilityProbe:
    """Hermes Agent 能力边界探测 MVP"""

    DIMENSIONS = {
        'code_generation': '代码生成',
        'file_editing': '文件编辑',
        'web_search': '信息检索',
        'tool_chaining': '工具链',
        'long_context': '长上下文',
        'error_recovery': '错误恢复',
        'instruction_following': '指令遵循'
    }

    def run_probe(self, dimension, level):
        """运行单个探测任务"""
        task = PROBE_TASKS[dimension][level]
        result = delegate_task(
            goal=task['prompt'],
            toolsets=task.get('tools', ['terminal', 'file']),
            role='leaf'
        )
        return self._evaluate(result, task['expected'])

    def find_boundary(self, dimension):
        """二分搜索能力边界"""
        lo, hi = 1, 10
        while lo < hi:
            mid = (lo + hi + 1) // 2
            score = self.run_probe(dimension, mid)
            if score >= 0.6:
                lo = mid
            else:
                hi = mid - 1
        return lo  # 最高稳定通过等级
```

### 4.3 探测任务库设计

| 维度 | Level 1 (简单) | Level 5 (中等) | Level 10 (极限) |
|------|----------------|----------------|-----------------|
| 代码生成 | 写 hello world | 实现排序算法 | 实现分布式锁 |
| 文件编辑 | 改一行注释 | 重构函数签名 | 跨文件重构 |
| 信息检索 | 搜一个已知事实 | 交叉验证矛盾信息 | 从多个源合成新知 |
| 工具链 | 单工具调用 | 3工具串联 | 7+工具复杂管线 |
| 长上下文 | 处理 1K 文本 | 处理 20K 文档 | 处理 100K+ 代码库 |
| 错误恢复 | 重试失败命令 | 诊断编译错误 | 从段错误中恢复 |
| 指令遵循 | 单一明确指令 | 5条约束条件 | 20条冲突约束 |

---

## 五、知识缺口

1. **能力回归的定量阈值**：多少退化算"显著"？需要针对不同维度设定不同阈值
2. **跨模型能力对比**：同一套探测任务在不同底层模型上的表现差异（GPT-4 vs Claude vs GLM）
3. **能力边界的时变模型**：长期运行后能力是否自然退化（模型更新、prompt 膨胀、记忆污染）
4. **多 Agent 协作的能力边界**：团队 vs 个体的能力差异是否为线性叠加
5. **元认知校准**：Agent 自评的置信度与实际表现的相关性如何提升
6. **课程学习的收敛速度**：定向学习需要多少轮才能显著提升特定能力
7. **负迁移检测**：强化某能力是否导致其他能力的隐性退化

---

## 六、核心发现总结

### 发现 1：能力边界是动态的、多维的
Agent 的能力不是单一的"聪明/笨"二元判断，而是一个多维向量。每个维度都有独立的边界点，且这些边界会随时间、上下文、任务类型动态变化。**单维度评估（如仅看代码生成 pass@1）严重低估了 Agent 的真实能力差距。**

### 发现 2：渐进式压力测试是发现边界的最优方法
相比固定测试集，渐进式加压能精确定位"断崖点"——即 Agent 从可靠变为不可靠的临界难度。这个信息比简单的通过/失败更有价值，因为它指导了定向学习的起点。

### 发现 3：弱项识别需要聚类而非枚举
随机测试发现的是分散的失败点，而聚类分析能揭示**系统性弱点模式**。10 个失败案例可能指向同 1 个根因（如"长上下文中的指令遗忘"），修复一个根因比逐个修复 10 个案例高效 10 倍。

### 发现 4：闭环验证不可或缺
定向学习后必须回归测试——确保学到了新能力且没有退化。没有验证的学习是盲目的。A/B 对比 + 回归检测是最小验证集。

### 发现 5：Hermes Agent 已有 80% 基础设施
skill-stress-test + error-case-library + auto-learner + evolver 已经覆盖了框架的大部分环节。缺少的关键部件是：**自动聚类分析**和**回归检测**。一个周末可以实现 MVP。

---

*笔记字数: ~3500 字 | 产出时间: 2026-05-18 07:45 | 网络: 不可用*
*数据来源: 纯本地知识蒸馏（已有 Skill + 通用 AI 知识库）*

## 相关笔记
- [Agent Skills才是关键抽象层](../2026-04-02-Agent Skills才是关键抽象层.md)
- [Claude-Code四层记忆架构](../2026-04-03-Claude-Code四层记忆架构.md)
- [Claude-Code-324-prompts-analysis](../2026-04-04-Claude-Code-324-prompts-analysis.md)
- [SelfImproving-Agent-CLI-infra](../2026-04-05-SelfImproving-Agent-CLI-infra.md)
- [spatial-intelligence-agent-action](../2026-04-05-spatial-intelligence-agent-action.md)
- [agent-loop-core-scheduling](../2026-04-07-agent-loop-core-scheduling.md)
- [email-not-revival-agent-needs-it](../2026-04-07-email-not-revival-agent-needs-it.md)
- [hermes-agent-deep-dive-evolution-roadmap](../2026-04-07-hermes-agent-deep-dive-evolution-roadmap.md)
- [claude-code-tool-execution-orchestration](../2026-04-08-claude-code-tool-execution-orchestration.md)
- [SKILL-md-ai-agent-skills](../2026-04-09-SKILL-md-ai-agent-skills.md)
- [gbrain-hybrid-search-proposal](../2026-04-11-gbrain-hybrid-search-proposal.md)
- [hermes-agent-vs-openclaw](../2026-04-13-hermes-agent-vs-openclaw.md)
- [Cloudflare-EmDash-AI-Agent-CMS](../2026-04-14-Cloudflare-EmDash-AI-Agent-CMS.md)
- [Hermes-Agent-v0.10.0-release-analysis](../2026-04-18-Hermes-Agent-v0.10.0-release-analysis.md)
- [Claude-Opus4.7-Claude-Code-最佳实践](../2026-04-20-Claude-Opus4.7-Claude-Code-最佳实践.md)
- [深入源码-Hermes-Agent-如何实现Self-Improving](../2026-04-23-深入源码-Hermes-Agent-如何实现Self-Improving.md)
- [深入源码Hermes-Agent-Self-Improving](../2026-04-23-深入源码Hermes-Agent-Self-Improving.md)
- [MCP协议生态与Agentic-RAG架构深度学习](../2026-04-27-MCP协议生态与Agentic-RAG架构深度学习.md)
- [LLM-Agent驱动量化交易系统前沿学习](../2026-04-29-LLM-Agent驱动量化交易系统前沿学习.md)
- [Meta-Hyperagents自适应Agent框架](../2026-04-30-Meta-Hyperagents自适应Agent框架.md)
- [AI-Agent记忆架构前沿学习](../2026-05-01-AI-Agent记忆架构前沿学习.md)
- [deepseek-agent-ecosystem](../2026-05-01-deepseek-agent-ecosystem.md)
- [AI-Agent-Protocol-Ecosystem-2026-学习](../2026-05-03-AI-Agent-Protocol-Ecosystem-2026-学习.md)
- [ai-agent-resources-ecosystem](../2026-05-03-ai-agent-resources-ecosystem.md)
- [智能教育-自适应评估](../2026-05-03-智能教育-自适应评估.md)
- [Agent协议生态2026最新进展-MCP-A2A深度融合](../2026-05-04-Agent协议生态2026最新进展-MCP-A2A深度融合.md)
- [个人Agent自进化五步闭环](../2026-05-04-个人Agent自进化五步闭环.md)
- [tradingagents-deep-analysis](../2026-05-05-tradingagents-deep-analysis.md)
- [SOUL-md-Agent-Partner-Transformation](../2026-05-07-SOUL-md-Agent-Partner-Transformation.md)
- [AI-Agent控制流](../2026-05-08-AI-Agent控制流.md)
- [AI趋势2026-推理时计算与反思Agent](../2026-05-11-AI趋势2026-推理时计算与反思Agent.md)
- [具身智能2026-世界模型VLA车企入局](../2026-05-11-具身智能2026-世界模型VLA车企入局.md)
- [具身智能2026从实验到实战](../2026-05-11-具身智能2026从实验到实战.md)
- [OpenHuman-记忆树AI智能体-i龙虾](../2026-05-16-OpenHuman-记忆树AI智能体-i龙虾.md)
- [PicoClaw-超轻量AI-Agent框架](../2026-05-16-PicoClaw-超轻量AI-Agent框架.md)
- [具身智能前沿学习](../2026-05-17-具身智能前沿学习.md)
- [Agent元认知-LLM不确定性感知](../2026-05-18-Agent元认知-LLM不确定性感知.md)
- [SmallRustHermes-Agent自我进化三个闭环](../2026-05-18-SmallRustHermes-Agent自我进化三个闭环.md)
- [agent-memory-systems-comparison](../2026-05-18-agent-memory-systems-comparison.md)
- [具身智能机器人2025十大趋势](../2026-05-18-具身智能机器人2025十大趋势.md)
- [anthropic-managed-agents-dreaming-outcomes](../anthropic-managed-agents-dreaming-outcomes.md)
- [智能教育-AI-tutoring](2026-05-05-智能教育-AI-tutoring.md)
- [ai-agent-protocol-stack-2026](2026-05-06-ai-agent-protocol-stack-2026.md)
- [ai-agent-protocol-wars-a2a-mcp](2026-05-08-ai-agent-protocol-wars-a2a-mcp.md)
- [ai-coding-agent-competition-landscape](2026-05-08-ai-coding-agent-competition-landscape.md)
- [2025年5月AI大爆发-Claude4-Qwen3-DeepSeek-R1](2026-05-09-2025年5月AI大爆发-Claude4-Qwen3-DeepSeek-R1.md)
- [ai-agent-protocols-mcp-a2a-acp](2026-05-09-ai-agent-protocols-mcp-a2a-acp.md)
- [开源AI春季爆发-模型推理Agent](2026-05-09-开源AI春季爆发-模型推理Agent.md)
- [mcp-a2a-agent-ecosystem](2026-05-10-mcp-a2a-agent-ecosystem.md)
- [ai-agent-protocols-mcp-a2a](2026-05-11-ai-agent-protocols-mcp-a2a.md)
- [AI-Agent-协议生态-深度整合学习](2026-05-16-AI-Agent-协议生态-深度整合学习.md)
- [Agentic-AI元年-智能体全面落地趋势](2026-05-16-Agentic-AI元年-智能体全面落地趋势.md)
- [HuggingFace-Spring2026-开源生态报告](2026-05-16-HuggingFace-Spring2026-开源生态报告.md)
- [具身智能-从造产品到抢落地六大趋势](2026-05-16-具身智能-从造产品到抢落地六大趋势.md)
- [agent-collaboration-self-evolution](2026-05-17-agent-collaboration-self-evolution.md)
- [具身智能2026数据规模化元年](2026-05-17-具身智能2026数据规模化元年.md)
- [RD-Agent-Quant-multi-agent-quant-framework-deep-dive](2026-05-18-RD-Agent-Quant-multi-agent-quant-framework-deep-dive.md)
- [agent-self-evolution-quant-trading](2026-05-18-agent-self-evolution-quant-trading.md)
- [多模态Agent框架对比2026-深度探索](2026-05-18-多模态Agent框架对比2026-深度探索.md)
- [IBM2026多智能体趋势](2026-05-19-IBM2026多智能体趋势.md)
- [agent-self-evolution-reflexion-metacognition](2026-05-19-agent-self-evolution-reflexion-metacognition.md)
- [AgentSelfEvolution-LearningSystem-深度探索](2026-05-20-AgentSelfEvolution-LearningSystem-深度探索.md)
- [agent-drift-stability-degradation-20260518](agent-drift-stability-degradation-20260518.md)
- [agent-stability-degradation-drift-detection](agent-stability-degradation-drift-detection.md)
- [google-a2a-protocol-multi-agent-2026-05-19](../google-a2a-protocol-multi-agent-2026-05-19.md)
- [hermes-agent-arxiv-search](../hermes-agent-arxiv-search.md)
- [hermes-agent-源码拆解自我进化机制](../hermes-agent-源码拆解自我进化机制.md)
- [不管用ClaudeCode还是OpenClaw先记住这12个知识](../orphan/2026-04-15-不管用ClaudeCode还是OpenClaw先记住这12个知识.md)
- [AI幻觉案例分析-Hermes-Agent不实报道](../orphan/2026-04-19-AI幻觉案例分析-Hermes-Agent不实报道.md)
- [智能教育-personalized-learning](../orphan/2026-05-04-智能教育-personalized-learning.md)
- [具身智能机器人2025年终盘点](../orphan/2026-05-05-具身智能机器人2025年终盘点.md)
- [具身智能机器人2025-商业化元年](../orphan/2026-05-09-具身智能机器人2025-商业化元年.md)
- [claude-learning-roadmap](../orphan/2026-05-10-claude-learning-roadmap.md)
- [0元打通Claude-Codex-OpenCode免费模型6入口](../orphan/2026-05-11-0元打通Claude-Codex-OpenCode免费模型6入口.md)
- [HTML的不合理有效性-Claude-Code-团队](../orphan/2026-05-16-HTML的不合理有效性-Claude-Code-团队.md)
- [GenericAgent](../orphan/GenericAgent.md)
- [skills-autonomous-ai-agents](../skills-autonomous-ai-agents.md)
- [竞品吸收笔记_GenericAgent](../竞品吸收笔记_GenericAgent.md)
