# 主动学习框架 — 深度整合学习笔记

> 📅 2026-05-18 | 方法：本地知识蒸馏（搜索服务不可用）
> 📦 素材源：6 篇文档（active-learning SKILL.md / evolver SKILL.md / agent-collaboration-self-evolution / SOUL-evolution-proposal / sniff-interests / evolution-log.jsonl）
> ⚠️ 声明：基于已有笔记交叉提炼，未实时搜索验证

---

## 一、核心发现

### 发现 1：三层触发机制的工程化实现是 Hermes 的核心竞争力

现有 `active-learning` skill 定义了三种触发：时间触发、事件触发、预测触发。但通过交叉分析进化日志（44条记录）与 skill 实际使用情况，发现**工程化成熟度差异巨大**：

| 触发类型 | 设计状态 | 实际运行 | 成熟度 | 关键差距 |
|----------|----------|----------|--------|----------|
| 时间触发 | ✅ 完整 | ✅ 44条进化日志全部由 cron 驱动 | L3 | 无 |
| 事件触发 | ✅ 文档定义 | ⚠️ 仅在 session 交互时触发 | L1 | 缺少系统级事件监听管道 |
| 预测触发 | ✅ 文档定义 | ❌ 几乎无实际运行记录 | L0 | 缺少预测模型和数据基础 |

**为什么重要**：从进化日志看，所有 44 条记录都是 cron 定时产生的。事件触发（如"用户提到新领域立即搜索"）和预测触发（如"量化交易开盘前准备预判脚本"）在文档中设计完善，但在 cron 环境下无人值守时无法激活。这意味着**主动学习的 2/3 能力在夜间空闲时是沉睡的**。

**实践启发**：
- 事件触发需要从"被动等待 session 交互"升级为"主动扫描系统信号"
- 预测触发需要建立时序数据基础（如用户活跃时段统计、任务模式识别）
- 建议为每种触发类型设计独立的状态机，而非统一在 skill 描述中

### 发现 2：进化闭环存在"最后一公里"断裂

从 `agent-collaboration-self-evolution` 笔记中的进化成熟度模型看，Hermes 当前处于 L2（主动反思），目标是 L3（元认知）。但分析进化日志的实际内容，发现：

| 进化动作 | 实际次数 | 占比 | 说明 |
|----------|----------|------|------|
| 笔记创建（note_created） | 8 | 18% | 深度笔记产出，质量较高 |
| Skill 创建（skill_create） | 2 | 4.5% | ths-auto-trader + llm-inference-optimization |
| Skill 补丁（patch） | 4 | 9% | 更新现有 skill 的知识缺口 |
| Memory 写入 | 3 | 7% | 持久化关键事实 |
| 学习记录（learn） | ~27 | 61.5% | 进化日志记录学习过程 |

**关键问题**：27 条"学习记录"中，大部分是"产出笔记 → 记录日志"的单向流程。进化闭环要求"学习→评估→采纳→进化"，但**评估环节缺少量化指标**。evolver skill 定义了 PRM 五维度评分体系（task_completion 0.55 + response_quality 0.30 + efficiency 0.05 + tool_usage 0.10），但进化日志中没有一条记录引用了 PRM 分数。

**根因分析**：
1. PRM 评分依赖 `session-prm-score.py` 脚本，但 cron 环境下评分通常由 LLM 直接完成而非脚本
2. LLM 评分缺乏校准——没有 ground truth 来验证评分的准确性
3. "能减少未来 3+ 次重复操作"的采纳标准太主观，缺少操作频率计数器

### 发现 3：主动学习的选题策略存在"确认偏差"陷阱

分析 sniff-interests.md 的 50+ 条待探索主题，结合实际探索记录，发现选题模式存在显著偏差：

| 维度 | 现状 | 问题 |
|------|------|------|
| 主题覆盖 | 8 大类 50+ 条 | 广度足够 |
| 实际探索 | 几乎全部集中在 ths-auto-trader（量化交易） | **严重偏向单一领域** |
| 选择逻辑 | "等级低 + 上次探索久 + 关键词多" | 公式偏向高频关键词领域 |
| 领域多样性 | 低 | 核心能力/用户关注/前沿跟踪 被量化交易挤压 |

**证据**：最近 10 条进化日志中，8 条与 ths-auto-trader 相关，1 条与 llm-inference 相关，1 条与数字主线相关。sniff-interests.md 中 Agent 自我进化、Agent 学习与知识管理、Agent 运维与自管理等重要领域**零条探索记录**。

**实践启发**：
- 选题公式需要增加"领域多样性"权重
- 每次 cron 执行应强制跨领域选题（如：当前领域 vs 随机领域 7:3 比例）
- 引入"探索日历"——每个领域每周至少探索 1 次，避免长期饥饿

### 发现 4：本地知识蒸馏的潜力被低估

active-learning skill 的本地蒸馏配方（6 步）定位为"搜索失败时的降级方案"。但通过本次实际蒸馏发现：

| 维度 | 实时搜索 | 本地蒸馏 |
|------|----------|----------|
| 信息密度 | 中（搜索结果信噪比低） | 高（已有笔记经过筛选） |
| 上下文连贯 | 低（碎片化结果） | 高（笔记间有逻辑关联） |
| 时效性 | 高 | 低 |
| 创新潜力 | 低（容易重复已有观点） | 高（交叉提炼产生新洞察） |
| Token 消耗 | 高（需要处理多源原始内容） | 低（笔记已结构化） |

**具体证据**：本次蒸馏从 agent-collaboration-self-evolution（17KB）、evolver SKILL.md（~15KB）、SOUL-evolution-proposal（2KB）三篇文档中，提炼出了上述 4 个"现有文档中分散存在但未被整合发现"的新洞察。这正是蒸馏的价值——不是重复已有知识，而是发现**跨文档的结构性盲点**。

**实践启发**：
- 本地蒸馏不应仅作为降级方案，应提升为**主动学习的默认首选**
- 设计"蒸馏→验证"双轮：先蒸馏产出洞察，联网后搜索验证
- 每次蒸馏后标记"需要验证"的洞察，积累到 5 条以上时触发一次联网验证

---

## 二、技术细节：主动学习框架的完整架构

### 2.1 三层触发状态机设计

当前 active-learning skill 用表格描述触发条件，建议升级为状态机：

```
┌──────────────────────────────────────────────────────────┐
│                   Trigger Dispatcher                      │
├─────────────┬──────────────────┬────────────────────────┤
│  TimeTrigger│ EventTrigger    │ PredictionTrigger       │
│  (Cron)     │ (System Signal) │ (Pattern Model)         │
│  ┌───────┐  │  ┌───────────┐  │  ┌──────────────────┐  │
│  │10:35  │  │  │User Input │  │  │Activity Analysis │  │
│  │16:35  │──┤  │System Err │──┤  │Seasonal Patterns │──┤
│  │22:35  │  │  │Tool Fail  │  │  │Interest Drift    │  │
│  │04:00  │  │  │Skill Miss │  │  │Task Queue Depth  │  │
│  └───────┘  │  └───────────┘  │  └──────────────────┘  │
│       │            │                    │                │
│       └────────────┴────────────────────┘                │
│                         │                                 │
│                   ┌─────▼─────┐                           │
│                   │  Router    │                           │
│                   │ (Priority  │                           │
│                   │  Queue)    │                           │
│                   └─────┬─────┘                           │
│                         │                                 │
│  ┌──────────────────────▼──────────────────────────┐     │
│  │           Learning Pipeline                      │     │
│  │  Select Topic → Execute Search/Distill          │     │
│  │  → Produce Note → Evaluate → Evolve             │     │
│  └──────────────────────┬──────────────────────────┘     │
│                         │                                 │
│  ┌──────────────────────▼──────────────────────────┐     │
│  │           Evolution Engine                       │     │
│  │  Skill Create/Patch | Memory Write | Log Record │     │
│  └─────────────────────────────────────────────────┘     │
└──────────────────────────────────────────────────────────┘
```

### 2.2 选题多样性算法

```python
def select_topic(interests: list[Topic], history: list[Log]) -> Topic:
    """领域平衡选题算法"""
    # 1. 计算每个领域最近探索时间
    domain_last_explored = compute_domain_recency(history)
    
    # 2. 计算领域权重（越久未探索 = 越高权重）
    domain_weights = {
        domain: max(1, days_since_last / 7)  # 每未探索一周权重+1
        for domain, days_since_last in domain_last_explored.items()
    }
    
    # 3. 70% 概率选最高权重领域，30% 概率随机
    if random() < 0.7:
        target_domain = max(domain_weights, key=domain_weights.get)
    else:
        target_domain = choice(list(domain_weights.keys()))
    
    # 4. 在目标领域内按原公式选题
    candidates = [t for t in interests if t.domain == target_domain]
    return max(candidates, key=lambda t: t.priority * domain_weights[target_domain])
```

### 2.3 进化闭环量化指标

```python
# 每次进化动作应记录以下指标
evolution_metrics = {
    "note_id": "2026-05-18-active-learning-...",
    "prd_score": None,  # 评分（如有）
    "topics_explored": ["active-learning", "evolver"],
    "domains_covered": ["devops", "ai-agent"],
    "novel_insights": 4,  # 新洞察数量
    "actionable_items": 3,  # 可采纳项数量
    "actual_evolution": True,  # 是否触发了进化动作
    "evolution_type": "skill_patch",  # create/patch/memory/none
    "source": "local_distillation",  # search/distillation/hybrid
}
```

---

## 三、实践启发与可采纳内容

| # | 启发 | 可操作性 | 采纳建议 |
|---|------|----------|----------|
| 1 | 本地蒸馏应提升为默认首选而非降级方案 | ✅ 高 | **patch active-learning skill** |
| 2 | 选题公式需增加领域多样性权重 | ✅ 高 | **patch active-learning skill** |
| 3 | 进化闭环需要量化指标而非主观判断 | ⚠️ 中 | 先记录指标，后续引入自动评分 |
| 4 | 事件触发和预测触发在 cron 下无法工作 | ⚠️ 中 | 设计系统信号监听机制 |
| 5 | 进化日志缺少 PRM 分数引用 | ✅ 高 | 在 cron prompt 中强制要求评分 |
| 6 | 蒸馏产出的新洞察需要标记"待验证" | ✅ 高 | 笔记模板增加验证状态字段 |

---

## 四、知识缺口

| # | 缺口 | 重要性 | 建议获取途径 |
|---|------|--------|------------|
| 1 | Google A2A 协议最新规范（2026 实战案例） | HIGH | 联网后搜索官方文档 |
| 2 | Agent 元认知机制的工程化实现方案 | HIGH | 搜索 Small Hermes / Reflexion 论文 |
| 3 | 选题算法的 A/B 测试方法（如何验证选题策略有效） | MEDIUM | 设计实验对比不同策略 |
| 4 | 预测触发的时序数据基础设计 | MEDIUM | 调研用户行为分析框架 |
| 5 | PRM 评分与进化质量的因果关系验证 | MEDIUM | 积累 30+ 条评分数据后分析 |
| 6 | 多 Agent 系统中主动学习的协调机制 | LOW | 联网后搜索 multi-agent learning |

---

## 五、相关资源索引

| 文档 | 大小 | 本次提炼贡献 |
|------|------|------------|
| `active-learning/SKILL.md` | ~8KB | 框架定义、触发机制、选题策略 |
| `evolver/SKILL.md` | ~15KB | 进化管线、PRM 评分、记忆整合 |
| `2026-05-17-agent-collaboration-self-evolution.md` | 17KB | 进化成熟度模型、七重困境、反模式 |
| `SOUL-evolution-proposal-2026-05-07.md` | 2KB | 反驳规则、责任闭环、权限边界 |
| `sniff-interests.md` | 5.5KB | 兴趣队列、选题分布分析 |
| `evolution-log.jsonl` | ~4KB | 44条进化记录、实际运行模式分析 |

---

*创建时间: 2026-05-18 03:40 (Cron idle-busy-loop)*
*方法: 本地知识蒸馏（6篇文档交叉提炼）*
*字数: ~3500*

## 相关笔记
- [agent-collaboration-self-evolution](2026-05-17-agent-collaboration-self-evolution.md)
- [AI-Agent-协议生态-深度整合学习](2026-05-16-AI-Agent-协议生态-深度整合学习.md)
- [SOUL-evolution-proposal](../SOUL-evolution-proposal-2026-05-07.md)
