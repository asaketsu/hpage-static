# ReAct Agent 系统 + LLM Agentic 能力训练研究报告

来源：GLM-5 技术报告（arXiv:2602.15763）+ ReAct 范式梳理 + Claude 进步分析
链接：https://arxiv.org/abs/2602.15763
日期：2026-05-21
评分：⭐5/5（GLM-5 技术报告细节极其丰富，是近年来最透明的 LLM 训练报告之一）
标签：#ReAct #Agent #RL #GLM-5 #agentic-engineering #SFT #RLHF

---

## 一、核心结论

**从 Vibe Coding 到 Agentic Engineering**——这不只是智谱的口号，而是整个 LLM 行业正在发生的范式转移。LLM 不再是「你问我答」的知识库，而是能够自主规划、执行、纠错的工程 agent。GLM-5 的技术报告把这条路径的每一步都拆开了，从预训练数据配比到异步 RL 基础设施，是目前能看到的最详细的 agentic LLM 训练全链路文档。

三个最值得关注的发现：

1. **代码数据量是王炸**：27T 总 token 中，代码占比远超预期。加上 Mid-Training 的 1.55T（32K→128K→200K 三阶段），总训练量 28.5T token，其中代码和软件工程数据是 agentic 能力的基石
2. **top-k 里的 random 是魔鬼**：DSA（DeepSeek Sparse Attention）的 indexer 用 top-k 检索 KV entries，但 CUDA 原生 top-k 是非确定性的！这个"小 bug"能在 RL 训练几步后导致 entropy 骤降、性能崩塌。用 `torch.topk` 替换才解决
3. **异步 RL 是 agent 训练的生死线**：同步 RL 在长 horizon agent 任务上 GPU 利用率极低（一条慢轨迹拖住整个 batch），GLM-5 的解法是完全解耦 inference 和 training engine

---

## 二、ReAct Agent 系统架构

### 2.1 什么是 ReAct

ReAct（Reasoning + Acting）是 2022 年 Yao et al. 提出的 agent 范式。核心思想：LLM 在推理（Thought）和行动（Action）之间交替循环，每步行动后观察环境反馈（Observation），再进入下一轮推理。

```
Thought: 我需要搜索用户账户余额
Action: query_database("SELECT balance FROM accounts WHERE user_id = 123")
Observation: 余额为 ¥5,000
Thought: 余额充足，可以执行转账
Action: transfer(from=123, to=456, amount=1000)
```

这个范式看似简单，但训练一个真正能稳定执行 ReAct 循环的 LLM 是极难的。原因：

- **长 horizon 灾难**：一次 agent 任务可能产生数万 token 的轨迹（SWE 任务平均 10K-50K token），训练时 gradient 容易爆炸或消失
- **探索效率低**：随机采样到一条能走通的长轨迹概率极低，需要大量采样
- **环境不稳定**：代码执行沙箱、终端环境、搜索引擎——每个都可能因为和模型无关的原因崩溃

### 2.2 Agentic 能力的三层训练

根据 GLM-5 报告和行业实践，LLM agentic 能力训练可以拆成三层：

**Layer 1: 基础能力（Pre-Training）**

代码+推理+工具使用的基础知识。这是地基。

| 数据类型 | GLM-5 做法 | 要点 |
|---------|-----------|------|
| Web | DCLM 分类器 + World Knowledge 分类器 | 长尾知识抽取 |
| Code | 多平台代码 + 含代码网页，28% token 增量 | 低资源语言专用分类器 |
| Math & Science | 网页+书籍+论文，LLM 评分过滤 | 禁止合成/AI 生成数据 |
| Mid-Training | 32K(1T) → 128K(500B) → 200K(50B) | 三阶段渐进扩展上下文 |

关键洞察：**软件工程数据不只是代码，而是完整的 issue-PR-diff-相关文件 拼接序列**。GLM-5 收集了约 1000 万 issue-PR 对，过滤后约 160B unique token。这种数据让模型理解了「改代码不只是写函数，而是理解需求→定位文件→修改→测试」的完整工作流。

**Layer 2: 对齐与推理（Post-Training: SFT → Reasoning RL）**

SFT 阶段引入三种思维模式（这是 GLM-5 的重要创新）：

- **Interleaved Thinking**：每次 response 和 tool call 前都先思考（Claude 最先引入）
- **Preserved Thinking**：coding agent 场景下，跨 turn 保留所有思考块，避免重复推导
- **Turn-level Thinking**：简单请求关闭思考降低延迟，复杂任务开启

Reasoning RL 阶段（基于 GRPO + IcePop）：
- 四个域混合训练：数学、科学、代码、工具集成推理（TIR）
- 难度过滤：只保留 GLM-4.7 解不出但 GPT-5.2/Gemini 3 Pro 能解的题目
- 二元 outcome reward

**Layer 3: Agentic RL（核心突破）**

这是 GLM-5 真正拉开差距的地方。完整的异步 agent RL 框架：

```
┌──────────────────────────────────────────────┐
│          Multi-Task Rollout Orchestrator       │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐      │
│  │ SWE Task │ │ Terminal  │ │  Search   │      │
│  │ Service  │ │  Service  │ │  Service  │      │
│  └────┬─────┘ └────┬─────┘ └────┬─────┘      │
│       │             │             │            │
│       └──────┬──────┘─────────────┘            │
│              │                                  │
│    ┌─────────▼──────────┐                      │
│    │  TITO Gateway      │ ← Token-in-Token-out  │
│    │  (保留精确 token)    │    避免 re-tokenize    │
│    └─────────┬──────────┘                      │
│              │                                  │
│    ┌─────────▼──────────┐                      │
│    │  Inference Engine   │ ← 独立 GPU 集群       │
│    │  (持续生成轨迹)      │    异步推送轨迹        │
│    └─────────┬──────────┘                      │
│              │                                  │
│    ┌─────────▼──────────┐                      │
│    │  Training Engine    │ ← 独立 GPU 集群       │
│    │  (批量梯度更新)      │    每 K 步同步权重     │
│    └────────────────────┘                      │
└──────────────────────────────────────────────┘
```

关键技术细节：

**Token-in-Token-out (TITO)**：inference engine 直接输出 token IDs + metadata，training engine 直接消费，不做文本往返。为什么这很重要？re-tokenization 会引入 token boundary 不匹配、空白字符处理差异、特殊 token 位置偏移——在长轨迹多轮交互中，这些微小差异会导致 action-reward 对齐完全错乱。

**Direct Double-sided Importance Sampling**：异步场景下无法追踪精确的 πθold（因为 rollout engine 可能在一条轨迹生成过程中被更新多次）。GLM-5 的解法：直接复用 rollout 时的 log-probabilities 作为 behavior proxy，跳过 πθold，用双边裁剪 [1-εl, 1+εh] 替代 PPO 的非对称裁剪。

**DP-aware Routing**：同一 agent 实例的多轮请求路由到同一 DP rank，最大化 KV-cache 复用。用一致性哈希 + 轻量动态负载均衡。

---

## 三、top-k Random 问题详解

这可能是整篇报告里最有工程价值的发现。

### 3.1 问题

DSA（DeepSeek Sparse Attention）的 indexer 需要从大量 KV entries 中检索 top-k（k=2048）最相关的。这个操作在训练和推理之间必须一致——就像 MoE 模型需要在训练时记录哪些 experts 被激活（routing replay），推理时复用同样的 experts。

问题：**CUDA 原生 top-k 是非确定性的**。对于边界值（第 k 个和第 k+1 个 score 接近时），不同运行可能返回不同的 top-k 结果。

### 3.2 影响

在 RL 训练中，这个非确定性是致命的：

1. 训练时 indexer 选择了 tokens A 作为 top-k
2. 推理时（生成 rollout）indexer 选择了 tokens B（不同的边界 token）
3. attention 计算结果不同 → 输出分布偏移 → importance sampling ratio 异常 → gradient 方向错误
4. **几步之后 entropy 骤降，性能崩塌**

### 3.3 解决方案

用 `torch.topk` 替换 CUDA 原生 top-k。虽然稍慢，但是确定性的。同时冻结 indexer 参数，只训练 attention 部分。

这个发现对整个行业的启示：**在 RL 训练中，任何非确定性操作都是定时炸弹**。不只是 top-k，任何有浮点精度歧义的操作（argsort、argmax 并列时）都可能造成训练-推理不一致。

---

## 四、Claude 的进步从哪来——SFT/RL 推断分析

（注：Anthropic 未公开 Claude 训练细节，以下基于公开行为变化和 GLM-5 报告中的引用进行推断）

### 4.1 Interleaved Thinking（2025 H2）

GLM-5 报告脚注 4 明确引用了 Claude 的 Interleaved Thinking 文档。这说明 Claude 在 2025 年下半年率先引入了「在 tool call 之间插入思考」的模式。

推断的 SFT 数据构造：
- 收集多轮 tool-use 对话数据
- 在每个 tool call 前插入 <thinking> 块，让模型先规划再行动
- 这比 ReAct 的纯文本 Thought 更结构化

### 4.2 Preserved Thinking（Opus 4.5+）

GLM-5 脚注 5 引用了 Claude Opus 4.5 的 Preserved Thinking。在 coding agent 场景下，保留跨 turn 的思考块。

这解决了什么问题？想象一个 agent 在写一个复杂功能：
- Turn 1：思考了整体架构，写了主文件
- Turn 2：如果没有 preserved thinking，模型需要重新理解上下文，可能走偏
- 有 preserved thinking：直接在上一轮思考的基础上继续

推断的实现：SFT 阶段构造多轮对话数据，显式将前几轮的 <thinking> 块拼接到后续 context 中。

### 4.3 RL 阶段推断

Claude 在 SWE-bench 上的持续进步（从 Sonnet 3.5 的 33% 到 Opus 4.5 的 70%+），可以合理推断经历了：

1. **大规模 SWE 环境 RL**：类似 GLM-5 的做法，构建大量真实 issue-PR 对的可执行环境
2. **长 horizon 异步 RL**：Claude 的 coding agent 能连续工作数小时不崩溃，必然经过了长轨迹 RL 训练
3. **Outcome-based reward**：SWE 任务有天然的二值 reward（测试通过/不通过），不需要复杂的 reward model

### 4.4 关键差异

| 维度 | 推断的 Claude 路径 | GLM-5 公开路径 |
|------|-------------------|---------------|
| 基座模型 | 未公开 | 744B MoE, 40B active, DSA |
| 训练数据量 | 未公开 | 28.5T tokens |
| RL 框架 | 未公开 | slime 异步框架 |
| Thinking 模式 | Interleaved + Preserved（原创） | 三种模式（借鉴+扩展） |
| Agentic 环境 | 未公开 | 10K+ SWE 环境 + Terminal + Search |
| top-k 确定性 | 未公开 | torch.topk 替换 CUDA top-k |

---

## 五、Agent 轨迹 Action 构造与 RL 训练要点

### 5.1 数据构造

从 GLM-5 的做法中提炼的 agent 训练数据构造 pipeline：

**Phase 1: 环境构建**
- SWE：基于 RepoLaunch 框架，自动分析仓库安装依赖，构建可执行环境，提取 F2P/P2P 测试用例
- Terminal：Harbor 格式，LLM 生成任务草稿 → 构建代理实例化 → 精炼代理迭代优化
- Search：Web Knowledge Graph → 多跳子图采样 → 高难度 QA 生成

**Phase 2: 轨迹采集**
- 多版本模型生成候选轨迹
- 保留错误段但在 loss 中 mask 掉（让模型学纠错，而不是学错误）

**Phase 3: 质量过滤**
- 四阶段 pipeline：任务综合 → Checklist 生成精炼 → 执行验证 → 动态迭代
- Agent-as-a-Judge + 人类专家交叉验证

### 5.2 RL 训练关键参数

```
GLM-5 RL 训练配置:
├── 算法: GRPO + IcePop (无 KL 项)
├── Group size: 32
├── Batch size: 32
├── β (mismatch clipping): 2.0
├── εlow: 0.2, εhigh: 0.28
├── DSA top-k: torch.topk (确定性)
├── Indexer: 冻结参数
└── 异步同步: 每 K 步推送到 inference engine
```

### 5.3 On-Policy Cross-Stage Distillation

多阶段 RL 的遗忘问题解法：

1. Reasoning RL checkpoint → Teacher 1
2. General RL checkpoint → Teacher 2
3. SFT checkpoint → Teacher 3

最终阶段用 KL 散度 loss 将当前模型拉回这些 teacher 的分布，Group size=1（不需要多采样估 advantage），Batch size=1024。

---

## 六、借鉴进化点（≥3 条）

### 1. Agent 训练环境的工程化思维
GLM-5 把环境构建做成了 pipeline，不是手动造几个 demo 环境。10K+ 可执行 SWE 环境、自动化的 Docker 构建验证（90%+ 准确率）。**对自己的启示**：做 agent 训练不要在数据量上省，要在自动化 pipeline 上投入。

### 2. 确定性 > 速度
top-k 的故事告诉我们，在 RL 训练中，确定性比速度重要 100 倍。`torch.topk` 比 CUDA top-k 慢一点，但避免了训练崩塌。**对自己的启示**：任何涉及 importance sampling 的场景，先审计所有操作是否确定性。

### 3. 三种 Thinking 模式的区分
不是所有任务都需要深度思考。Interleaved（复杂任务）、Preserved（长 horizon coding）、Turn-level（可开关）的分层设计，把推理成本变成了可控的维度。**对自己的启示**：agent 系统设计时，thinking 不应是 all-or-nothing，而是按任务复杂度自适应。

### 4. 异步 RL 的「工程解」优于「算法解」
GLM-5 没有发明新 RL 算法，而是通过系统设计（解耦 inference/training、TITO、DP-aware routing）解决了同步 RL 的效率问题。**对自己的启示**：很多 AI 工程问题，系统层面的解法比算法层面的更实际。

### 5. Cross-Stage Distillation 防遗忘
多阶段训练的遗忘是普遍问题。用前序阶段的 checkpoint 做 teacher，在最后阶段统一蒸馏回来。**对自己的启示**：任何多阶段训练都要考虑这个 pattern。

---

## 七、局限与未解答问题

1. **9T Code 数据的具体配比**：报告说 28.5T 总 token，但代码/数学/网页各自多少没有公开。从 28% code token 增量推算，code 数据可能在 6-9T 范围
2. **Agentic RL 的具体 reward 设计**：只说了 binary outcome reward，但 SWE 任务的 partial credit 怎么算？测试通过 5/10 给 0.5？
3. **异步 RL 的最佳 K 值**：每 K 步同步一次权重，K 选多少？报告没给
4. **训练成本**：28.5T token + 744B 参数的训练成本未披露
5. **与其他前沿模型的 RL 对比**：没有对比 DeepSeek-R1/ZRO 等其他 RL 训练方法的消融

---

*报告基于 GLM-5 技术报告原文（40页 PDF）+ ReAct 原始论文 + Claude 公开文档分析*

**补充阅读**：[LLM 微调数据管线：DataFlow + DataFlex 全链路](2026-05-21-llm-finetune-dataflow-dataflex-pipeline.md) — SFT 数据准备工程化工具链，与本文的 RL 训练阶段互补


## 相关笔记
- [llm-wiki-gbrain-agent-evolution_33aa818c](llm-wiki-gbrain-agent-evolution_33aa818c.html)
- [structureclaw-research](structureclaw-research.html)
- [skills-research](skills-research.html)
- [llm-pid-tuner](llm-pid-tuner.html)
- [hermes-agent-源码拆解自我进化机制](hermes-agent-源码拆解自我进化机制.html)
