# LLM 自我 Prompt 优化：让 AI 自动改写自己的 System Prompt

> 深度研究笔记 | 2026-05-18 | 来源：OPRO/GEPA/SPO/ORPP/DSPy 等论文与实践

---

## 一、核心问题与动机

### 为什么需要自动 Prompt 优化？

传统 Prompt Engineering 依赖人工试错：写 prompt → 测试 → 发现边缘案例失败 → 调整措辞 → 重复。这个过程有三个根本性缺陷：

1. **不可扩展**：人工只能探索提示词空间中极小的子集
2. **不可迁移**：对模型 A 有效的 prompt 对模型 B 可能完全失效
3. **不可维护**：任务变化时需要重新人工调优

自动 Prompt 优化的核心洞察：**既然 LLM 能理解自然语言，为什么不让它自己优化自己的 prompt？**

这催生了 2022-2025 年间的一系列研究，从 APE（Automatic Prompt Engineer）到 OPRO、GEPA、SPO、ORPP 等方法，形成了一个完整的研究谱系。

---

## 二、核心发现

### 发现 1：OPRO — LLM 作为 Prompt 优化器（Google DeepMind, 2023）

**论文**：*Large Language Models as Optimizers* (Yang et al., 2023)

**核心思想**：用一个 LLM（优化器 LLM）来生成和改进另一个 LLM（目标 LLM）的 prompt。关键机制是 **Meta-Prompt**：

```
Meta-Prompt 结构：
┌─────────────────────────────────────┐
│ 任务描述："解决小学数学应用题"        │
│                                     │
│ 已评估的 prompt + 分数（按分数排序）： │
│   "Let's solve the problem" → 72%   │
│   "Let's break it down" → 78%       │
│   "Let's think carefully" → 81%     │
│   "Let's calculate our way" → 84%   │
│   "Let's do the math" → 87%         │
│                                     │
│ 请生成一个更好的 prompt。             │
└─────────────────────────────────────┘
```

**算法流程**：
1. 初始化：生成一批随机 prompt
2. 评估：用每个 prompt 在目标 LLM 上跑任务，打分
3. 排序：将 (prompt, score) 对按分数排列放入 meta-prompt
4. 生成：优化器 LLM 根据历史记录生成新 prompt
5. 迭代：重复 2-4 直到收敛

**关键技术细节**：
- OPRO 本质是无梯度优化（gradient-free optimization），利用 LLM 的 in-context learning 能力
- 收敛行为类似梯度下降：早期大步探索，后期精细调优
- DeepMind 发现最优 prompt 往往超越人工设计的（如 GSM8K 上 "Take a deep breath" 比 "Let's think step by step" 更好）
- 使用 PaLM-2 实验时，提示词从 "Let's solve the problem"（72%）进化到 "Let's do the math"（87%）

**局限性**：
- 迭代成本高（每轮需要大量评估）
- 容易陷入局部最优
- 对 meta-prompt 的格式敏感

### 发现 2：GEPA — 反思式 Prompt 进化（UC Berkeley/Databricks, 2025）

**论文**：*GEPA: Reflective Prompt Evolution Can Outperform Reinforcement Learning* (Yang et al., 2025)

**核心思想**：GEPA（Genetic-Pareto）不使用标量奖励更新权重（RL 方式），而是分析完整的执行轨迹（prompt → output → error → feedback），让 LLM 反思并提出有针对性的改进。

**算法核心**：
```
GEPA 迭代流程：
1. 维护 5-10 个候选 prompt 的种群
2. 选择一些候选进行进化
3. 在 mini-batch（3-5 个问题）上执行
4. 收集执行轨迹 + 错误信息
5. 用 LLM 反思：分析失败原因，提出具体修改
   例："失败因为没有隔离变量" → 添加 "使用逆运算"
6. 测试新 prompt 在 mini-batch 上的表现
7. 仅改进的 prompt 加入候选池（Pareto 前沿选择）
```

**Pareto 选择机制**：
- 一个 prompt 是 Pareto 最优的，当且仅当无法在某个任务类型上改进而不使其他类型变差
- 这防止优化收敛到局部最优
- 维持多样化的 prompt 种群而非单一"最优"

**GEPA vs RL 的关键区别**：

| 维度 | RL (GRPO) | GEPA |
|------|-----------|------|
| 学习信号 | 稀疏标量奖励 | 完整执行轨迹文本 |
| 样本效率 | 需要数千次 rollout | 一次失败可修复整类错误 |
| 可解释性 | 黑盒 | 自然语言反思可追溯 |
| 部署成本 | 需要训练 | 仅优化 prompt |

**实际效果**：GEPA 在多个基准上超越了 GRPO 和 MIPROv2，同时需要远更少的 rollout 次数。

**Pydantic AI 集成**：Pydantic 团队已实现 GEPA + pydantic-ai + pydantic-evals 的完整优化管线，将 prompt engineering 从艺术变成科学。

### 发现 3：SPO — 无标签自监督 Prompt 优化（EMNLP 2025）

**论文**：*Self-Supervised Prompt Optimization* (Xiang et al., EMNLP 2025 Findings)

**核心创新**：完全消除对标注数据的需求。用 LLM-based pairwise evaluator 替代 ground-truth 标签。

**算法流程**：
1. 给定初始 prompt，在任务上执行得到输出
2. 用另一个 LLM 作为评判者（pairwise evaluator），对比两个 prompt 的输出质量
3. 优化器 LLM 根据「当前 prompt + 成功输出」作为素材生成下一版候选 prompt
4. 递归优化直到收敛

**成本优势**：
- 比传统方法降低 94%-99% 的优化成本
- 典型成本约 $0.15 完成一次完整优化

**局限**：
- 评判 LLM 存在噪音（judge noise）
- 小样本集上容易过拟合
- "prompt hacking" 风险（优化器可能利用评判者的偏好而非真正提升质量）
- 推理和表面正确性任务上表现好，但更复杂任务仍有挑战

### 补充发现：ORPP — 自优化角色扮演 Prompt（EMNLP 2025）

**论文**：*ORPP: Self-Optimizing Role-playing Prompts to Enhance Language Model Capabilities* (Duan et al., EMNLP 2025)

**创新点**：将角色扮演（role-playing）与自动 prompt 优化结合。通过为特定任务自动生成优化的角色扮演 prompt，激发模型的潜在能力。实验表明 ORPP 在大多数情况下超越了现有主流 prompt 优化方法。

---

## 三、技术谱系与演进路线

```
时间线：自动 Prompt 优化方法演进

2022 --- APE (Zhou et al.)
         |   "Let's think step by step" 的自动发现
         |   基于 LLM 生成 + 评分选择
         |
2023 --- OPRO (DeepMind)
         |   LLM 作为优化器，meta-prompt 迭代
         |   无梯度优化范式
         |
2024 --- DSPy 生态
         |   MIPROv2: 同时优化指令 + few-shot
         |   COPRO: 基于 OPRO 的 DSPy 实现
         |   SIMBA: 基于模拟退火的优化
         |
2025 --- GEPA (Berkeley/Databricks)
         |   反思式进化，Pareto 选择
         |   超越 RL 方法，极高样本效率
         |
2025 --- SPO (DeepWisdom/HKUST)
         |   无标签，自监督
         |   成本降低 94-99%
         |
2025 --- ORPP (HIT Shenzhen)
         |   角色扮演 + 自动优化
         |   复杂任务上超越通用方法
```

---

## 四、实践案例：OPRO 的 Python 实现模式

以下是一个简化版 OPRO 实现的核心逻辑：

```python
import json
from openai import OpenAI

client = OpenAI()

def opro_optimize(
    task_description: str,
    evaluator,           # (prompt) -> float
    initial_prompts: list[str],
    n_iterations: int = 10,
    n_candidates: int = 5,
) -> str:
    """OPRO 核心循环"""
    
    history = []  # (prompt, score) pairs
    
    # Initial evaluation
    for p in initial_prompts:
        score = evaluator(p)
        history.append((p, score))
    
    for i in range(n_iterations):
        # Sort by score, take top-k
        history.sort(key=lambda x: x[1], reverse=True)
        top_k = history[:n_candidates]
        
        # Build meta-prompt
        scored_list = "\n".join(
            f'  [{s:.1f}] "{p}"' for p, s in top_k
        )
        meta_prompt = (
            f"Task: {task_description}\n\n"
            f"Evaluated prompts (best first):\n{scored_list}\n\n"
            f"Generate a better prompt. Output ONLY the new prompt text."
        )
        
        # Optimizer LLM generates new prompt
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": meta_prompt}],
            temperature=0.9,  # Higher temperature for exploration
        )
        new_prompt = response.choices[0].message.content.strip()
        
        # Evaluate new prompt
        score = evaluator(new_prompt)
        history.append((new_prompt, score))
        
        print(f"Iter {i+1}: score={score:.2f}")
    
    # Return best prompt
    history.sort(key=lambda x: x[1], reverse=True)
    return history[0][0]
```

---

## 五、GEPA 反思式进化的核心模式

```python
def gepa_evolve(
    base_prompt: str,
    task_fn,          # (prompt, problem) -> result
    problems: list,   # test problems
    n_generations: int = 20,
    population_size: int = 8,
) -> list[dict]:
    """GEPA evolution loop"""
    
    population = [{"prompt": base_prompt, "fitness": 0, "history": []}]
    
    for gen in range(n_generations):
        # Select candidate to evolve
        candidate = select_candidate(population)
        
        # Execute on mini-batch
        minibatch = sample_minibatch(problems, k=5)
        results = []
        for prob in minibatch:
            output = task_fn(candidate["prompt"], prob)
            results.append({
                "problem": prob,
                "output": output,
                "success": evaluate_output(output, prob),
            })
        
        # Reflect on failures
        failed = [r for r in results if not r["success"]]
        if failed:
            reflection = reflect_on_failures(
                candidate["prompt"], 
                failed,
                candidate["history"]
            )
            new_prompt = apply_reflection(
                candidate["prompt"], reflection
            )
        else:
            new_prompt = candidate["prompt"]
        
        # Evaluate new prompt
        new_fitness = evaluate_full(
            new_prompt, task_fn, problems
        )
        
        # Only add if improved (Pareto selection)
        if new_fitness > candidate["fitness"]:
            population.append({
                "prompt": new_prompt,
                "fitness": new_fitness,
                "history": candidate["history"] + [reflection],
            })
            population = pareto_select(population, population_size)
    
    return sorted(population, key=lambda x: x["fitness"], reverse=True)
```

---

## 六、实践启发

### 6.1 可直接应用的工作流

**对于 Hermes Agent 场景**，最有价值的洞察是：

1. **Skill Prompt 可以自动优化**：每个 SKILL.md 的指令部分本质上就是一个 system prompt。可以用 OPRO/GEPA 的思路，在实际任务执行中收集成功/失败案例，自动改进 skill 的指令。

2. **反思循环是核心**：GEPA 的「执行 → 反思失败 → 提出修改 → 验证」模式，本质上就是我们已经在做的「经验沉淀」的算法化版本。

3. **无需标注数据的优化**：SPO 证明了 pairwise comparison（让 LLM 判断 A 好还是 B 好）可以替代 ground-truth 标签。这对实际部署意义重大。

### 6.2 方法选择指南

| 场景 | 推荐方法 | 理由 |
|------|----------|------|
| 简单任务，少量样本 | APE/OPRO | 实现简单，快速收敛 |
| 复杂多步骤任务 | GEPA | 反思机制能捕获深层失败模式 |
| 无标注数据 | SPO | 自监督，成本极低 |
| 角色扮演/人格任务 | ORPP | 针对性优化 |
| 生产系统 | DSPy (MIPROv2/GEPA) | 成熟框架，可观测性 |

### 6.3 成本考量

- OPRO 每轮迭代成本 = n_candidates x eval_cost + 1 x optimize_cost
- GEPA 比 GRPO 减少 10-100x rollout
- SPO 典型优化成本 $0.15，传统方法 $5-50
- 实际部署建议：先在小子集验证，再全量优化

---

## 七、知识缺口与未来方向

### 当前未解决的问题

1. **优化稳定性**：不同运行可能产生差异很大的结果，缺乏理论保证
2. **过拟合风险**：优化可能在训练集上过拟合，泛化性不确定
3. **评估可靠性**：LLM-as-judge 存在位置偏见、长度偏见等系统性偏差
4. **多目标优化**：同时优化准确率、延迟、成本等目标仍具挑战
5. **跨模型迁移**：对模型 A 优化的 prompt 对模型 B 效果如何？缺乏系统研究

### 有价值的后续探索方向

1. **Prompt 版本管理 + A/B 测试**：将自动优化的 prompt 纳入 CI/CD
2. **领域特化**：在特定领域（如代码生成、数学推理）的 prompt 优化策略
3. **与 RLHF 的互补**：先 GEPA 优化 prompt，再用 RLHF 微调权重
4. **自优化 Agent 系统**：Agent 在运行时持续收集反馈并自动改进自己的 system prompt

---

## 八、参考资源

| 资源 | 链接 | 说明 |
|------|------|------|
| OPRO 论文 | arXiv:2309.03409 | DeepMind 原始论文 |
| GEPA 论文 | arXiv:2507.19457 | Berkeley/Databricks, 2025 |
| SPO 论文 | ACL Anthology 2025.findings-emnlp.479 | 无标签优化 |
| ORPP 论文 | ACL Anthology 2025.emnlp-main.1453 | 角色扮演优化 |
| DSPy 优化器 | dspy.ai/learn/optimization/optimizers/ | 生产级框架 |
| DeepEval GEPA | deepeval.com/docs/prompt-optimization-gepa | 评估框架集成 |
| Pydantic + GEPA | pydantic.dev/articles/prompt-optimization-with-gepa | 实战教程 |
| PromptingGuide APE | promptingguide.ai/techniques/ape | 入门教程 |

---

*本笔记基于 2023-2025 年间发表的 OPRO、GEPA、SPO、ORPP 等论文及 DSPy 框架文档整理。*
*关键词：OPRO, GEPA, SPO, ORPP, APE, DSPy, MIPROv2, 自动 Prompt 优化, LLM 自优化, 反思式进化, Pareto 选择*

## 相关笔记
- [Karpathy-LLM-Wiki-second-brain](../2026-04-05-Karpathy-LLM-Wiki-second-brain.md)
- [Hermes-LLM-Wiki-学习笔记](../2026-04-18-Hermes-LLM-Wiki-学习笔记.md)
- [LLM推理优化前沿技术2026](../2026-04-28-LLM推理优化前沿技术2026.md)
- [LLM-Agent驱动量化交易系统前沿学习](../2026-04-29-LLM-Agent驱动量化交易系统前沿学习.md)
- [边缘AI与On-Device-LLM前沿学习](../2026-04-30-边缘AI与On-Device-LLM前沿学习.md)
- [deepseek-agent-ecosystem](../2026-05-01-deepseek-agent-ecosystem.md)
- [LLM对齐训练范式RLHF-DPO-GRPO-DAPO](../2026-05-04-LLM对齐训练范式RLHF-DPO-GRPO-DAPO.md)
- [开源AI模型2025-DeepSeek-Qwen新格局](../2026-05-05-开源AI模型2025-DeepSeek-Qwen新格局.md)
- [PageIndex-无向量推理式RAG](../2026-05-07-PageIndex-无向量推理式RAG.md)
- [大模型量化技术全景-GGUF-GPTQ-AWQ-FP8-BitNet](../2026-05-07-大模型量化技术全景-GGUF-GPTQ-AWQ-FP8-BitNet.md)
- [推理加速深度解析-投机解码-KVCache-连续批处理](../2026-05-08-推理加速深度解析-投机解码-KVCache-连续批处理.md)
- [LLM知识蒸馏技术全景](../2026-05-09-LLM知识蒸馏技术全景.md)
- [DeepSeek-V4-开源模型新格局](../2026-05-10-DeepSeek-V4-开源模型新格局.md)
- [蒸馏量化联合策略-QAD-LBLLM-CapacityGap](../2026-05-10-蒸馏量化联合策略-QAD-LBLLM-CapacityGap.md)
- [5月AI模型大战-GPT55-DeepSeekV4](../2026-05-11-5月AI模型大战-GPT55-DeepSeekV4.md)
- [AI趋势2026-推理时计算与反思Agent](../2026-05-11-AI趋势2026-推理时计算与反思Agent.md)
- [LLM冲击下PINN应用变化与发展](../2026-05-11-LLM冲击下PINN应用变化与发展.md)
- [MoE蒸馏与压缩-专家路由迁移-稀疏结构处理](../2026-05-11-MoE蒸馏与压缩-专家路由迁移-稀疏结构处理.md)
- [JAX-NVIDIA-GPU-微调Llama3.1实战方案](../2026-05-15-JAX-NVIDIA-GPU-微调Llama3.1实战方案.md)
- [LoRA高效微调前沿技术全景](../2026-05-17-LoRA高效微调前沿技术全景.md)
- [SGLang高性能LLM推理框架深度分析](../2026-05-17-SGLang高性能LLM推理框架深度分析.md)
- [Agent元认知-LLM不确定性感知](../2026-05-18-Agent元认知-LLM不确定性感知.md)
- [MoE模型LoRA微调最佳实践](../2026-05-18-MoE模型LoRA微调最佳实践.md)
- [蒸馏量化RL三联流水线-后训练范式统一](../2026-05-19-蒸馏量化RL三联流水线-后训练范式统一.md)
- [Active-Data-Selection-LLM训练动态数据选择前沿](../2026-05-20-Active-Data-Selection-LLM训练动态数据选择前沿.md)
- [AutoSearch 自主训练任务](../AutoSearch 自主训练任务.md)
- [2025年5月AI大爆发-Claude4-Qwen3-DeepSeek-R1](2026-05-09-2025年5月AI大爆发-Claude4-Qwen3-DeepSeek-R1.md)
- [开源AI春季爆发-模型推理Agent](2026-05-09-开源AI春季爆发-模型推理Agent.md)
- [LLM推理优化-MoE量化加速全景](2026-05-16-LLM推理优化-MoE量化加速全景.md)
- [LLM推理优化技术](2026-05-16-LLM推理优化技术.md)
- [llm-inference-opt-incremental2](2026-05-18-llm-inference-opt-incremental2.md)
- [llm-inference-opt-update](2026-05-18-llm-inference-opt-update.md)
- [MoE-稀疏激活微调工程实践](2026-05-19-MoE-稀疏激活微调工程实践.md)
- [SGLang-vs-vLLM-推理引擎对比](2026-05-19-SGLang-vs-vLLM-推理引擎对比.md)
- [llm_wiki分析与Skill进化](2026-05-20-llm_wiki分析与Skill进化.md)
- [llm-inference-opt-2026-05-17](llm-inference-opt-2026-05-17.md)
- [llm-inference-opt-incremental-20260517](llm-inference-opt-incremental-20260517.md)
- [llm-pid-tuner](../llm-pid-tuner.md)
- [分布式训练技术全景-FSDP-DeepSpeed-Megatron](../orphan/2026-05-05-分布式训练技术全景-FSDP-DeepSpeed-Megatron.md)
- [表达清晰的5个训练](../orphan/2026-05-16-表达清晰的5个训练.md)
- [tinyedge-lora](../tinyedge-lora.md)
- [前瞻性问题-AI垂域LLM载具设计](../前瞻性问题-AI垂域LLM载具设计.md)
