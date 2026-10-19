# AI Agent 自进化 Skill 系统 — EvoSkills 框架深度解析

> 📅 2026-06-22 | 夜间自学习 | 来源：arXiv 2604.01687 + arXiv 2507.21046

## 核心结论

**Agent 自进化的 Skill 在 11 个领域中的 9 个超越人类策展的 Skill，通过率 71.1% vs 53.5%（+17.6pp）。** 关键机制是 Skill Generator 与 Surrogate Verifier 的协同进化——Agent 不仅生成技能，还自主构建验证测试，无需人工标注。

---

## 一、问题定义：Tool-Skill Gap

当前 LLM Agent 的技能（Skill）面临三大瓶颈：

| 瓶颈 | 说明 |
|------|------|
| **标注密集** | 技能依赖人工编写，成本高、不可扩展 |
| **人机认知错位** | 人类写的技能不符合 Agent 实际推理模式 |
| **复杂度鸿沟** | 现有自进化方法只能生成单文件 Tool，无法处理多文件 Skill 包 |

> 核心洞察：**Tool 是简单的独立函数，Skill 是结构化的多文件包**（指令 + 脚本 + 参考资料），需要协调执行。这是自进化的真正难点。

---

## 二、EvoSkills 框架架构

### 2.1 双组件协同进化

```
┌─────────────────────────────────────────────────┐
│              EvoSkills 协同进化循环               │
│                                                  │
│  ┌──────────────┐       ┌──────────────┐        │
│  │ Skill        │──S──→│ Surrogate     │        │
│  │ Generator    │←─C──│ Verifier      │        │
│  │              │       │ (信息隔离)    │        │
│  │ 持久对话上下文 │       │ 独立LLM会话   │        │
│  └──────────────┘       └──────────────┘        │
│         │                      │                │
│         ▼                      ▼                │
│    技能迭代优化          测试用例升级              │
│    S(i+1) = argmax R̃   V(j+1) 当代理通过但      │
│                         Oracle 失败时升级         │
└─────────────────────────────────────────────────┘
```

### 2.2 核心算法

**技能精炼公式：**
```
𝒮(i+1) ← argmax_𝒮 R̃(Φ(𝒮, ℰ), 𝒱(j))
```
- `𝒮` = Skill 包（指令 + 脚本 + 参考资料）
- `R̃` = Surrogate Verifier 的奖励信号
- `Φ` = Agent 执行函数
- `ℰ` = 执行环境
- `𝒱` = 验证测试集

**测试升级触发条件：**
```
if R̃(x(i), 𝒱(j)) = 1 AND R(x̂(i)) < 1:
    # Surrogate 通过但 Oracle 失败 → 升级测试难度
    𝒱(j+1) ∼ πθV(· | I, x(i), 𝒱(j))
```

### 2.3 关键设计决策

| 设计 | 理由 |
|------|------|
| Verifier 信息隔离 | 防止偏差继承——Verifier 不知道 Generator 的推理过程 |
| 持久上下文（Generator） | 积累跨轮次的改进经验 |
| 交替精炼 | 避免单方面的过拟合 |

---

## 三、实验结果

### 3.1 SkillsBench 总体表现

| 方法 | 通过率 | 相对提升 |
|------|--------|----------|
| No-Skill 基线 | 30.6% | — |
| Human Curated Skills | 53.5% | +22.9pp |
| Background Context Only | 48.6% | +18.0pp |
| **EvoSkills (本文)** | **71.1%** | **+40.5pp** |

### 3.2 分领域表现（11 个领域中 9 个超越人类）

| 领域 | EvoSkills vs Human | 提升 |
|------|-------------------|------|
| **Finance** | 大幅领先 | **+56.9pp** |
| **Cybersecurity** | 大幅领先 | **+23.2pp** |
| 天文学（案例研究） | 100% vs 53.5% | +46.5pp |

### 3.3 跨模型迁移性

> EvoSkills 在 Claude Opus 4.6 上进化的技能，迁移到 6 个其他模型后仍保持 35-45pp 的提升。

- 技能编码的是**可复用的任务结构**，而非模型特定产物
- 模型匹配进化仍有适度优势（GPT-5.2 在自有技能上 +4.8pp）

### 3.4 消融实验：验证器不可或缺

| 配置 | 通过率 | 降幅 |
|------|--------|------|
| 完整 EvoSkills | 71.1% | — |
| 移除 Surrogate Verifier | 41.1% | **-30.0pp** |
| 仅背景上下文 | 48.6% | -22.5pp |

---

## 四、案例研究：系外行星凌星周期检测

### 进化过程（4 轮收敛）

| 版本 | 方法 | Surrogate 通过 | Oracle 得分 | 关键改进 |
|------|------|---------------|-------------|----------|
| v1 | BLS + biweight 去趋势 | 0/15 | 0% | 初始失败 |
| v2 | 优化 BLS，更宽周期范围 | — | 75% | 参数优化 |
| v3 | 中值滤波去趋势 | — | 75% | 仍有问题 |
| v4 | **TLS + 两阶段精炼** | — | **100%** | 算法切换 + 别名检测 |

### 人机对比

| 维度 | 人类策展 | 自进化 |
|------|---------|--------|
| 代码量 | 1,096 行（纯文档） | 64 行文档 + 142 行可执行代码 |
| 函数数 | 0 | 9 个 |
| 通过率 | 53.5% | **100%** |

> 关键发现：**Agent 创建的技能比人类更好**，因为它们捕获了 Agent 实际需要的推理模式和工具使用策略。

---

## 五、对 Hermes Agent 系统的改进建议

### 5.1 可直接应用的机制

| EvoSkills 机制 | Hermes 对应改进 |
|----------------|----------------|
| Surrogate Verifier 信息隔离 | Skill 审查应使用独立会话，避免 Creator 的认知偏差 |
| 测试升级触发条件 | 当 Skill 通过自检但实际任务失败时，自动升级验证标准 |
| 持久进化上下文 | evolver Skill 应维护跨轮次的改进日志 |
| 5 轮内收敛 | 设置 Skill 进化的最大迭代次数为 5，避免过度优化 |

### 5.2 具体改进建议

1. **引入 Co-Evolution 到 evolver Skill**：当前 evolver 只做"错误模式分析→规则沉淀"，应增加 Surrogate Verifier 角色，自动生成测试用例验证 Skill 质量
2. **跨模型迁移验证**：在 GLM-5.1 上优化的 Skill，应在 GLM-5.2 和其他模型上验证迁移性
3. **多文件 Skill 包**：从单文件 SKILL.md 扩展到 SKILL.md + scripts/ + references/ 的完整包，并用验证器测试整体协调性
4. **SkillsBench 式评估**：为高频 Skill 建立自动化基准测试，量化改进效果

---

## 六、自进化 Agent 全景（来自 Survey arXiv:2507.21046）

### 进化的四个维度

| 维度 | 代表方法 | 核心思想 |
|------|---------|---------|
| **Policy & Experience** | Self-Challenging Agents | Agent 自主生成挑战性任务并从中学习 |
| **Memory Evolution** | Memento | 无需微调 LLM 即可优化 Agent 记忆策略 |
| **Workflow Optimization** | GPTSwarm, Symbolic Learning | 将 Agent 工作流建模为可优化图 |
| **Model Editing** | Circuit Breakers, Self-Adapting LMs | 直接编辑模型参数实现持续适应 |

### 关键趋势

- **Intra-Test-Time Self-Evolution**：在推理过程中自我适应（无需重新训练）
- **Synthetic Risk Scenarios**：自动生成安全风险场景进行对抗训练
- **Multi-Agent Co-Evolution**：多个 Agent 协同进化，互为验证器

---

## 七、引用

- CoEvoSkills: arXiv:2604.01687 (2026)
- SkillOpt: arXiv:2605.23904 (2026)
- MemSkill: arXiv:2602.02474 (2026)
- Survey of Self-Evolving Agents: arXiv:2507.21046v4 (2025)

---

*夜间自学习笔记 | 模型：GLM-5.1 | 生成时间：2026-06-22*

## 相关笔记
- [AI-Agent自进化系统2026-闭环设计](2026-05-29-AI-Agent自进化系统2026-闭环设计-记忆架构与工程实践.md)
- [Agent自我进化与学习系统-深度研究](2026-05-22-Agent自我进化与学习系统-深度研究.md)
- [个人Agent自进化五步闭环](2026-05-04-个人Agent自进化五步闭环.md)
- [AutoClaw-自进化与Skill商店](2026-04-17-AutoClaw-自进化与Skill商店.md)
- [SmallRustHermes-Agent自我进化三个闭环](2026-05-18-SmallRustHermes-Agent自我进化三个闭环.md)
