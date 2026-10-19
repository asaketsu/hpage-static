# SkillOpt — 微软开源的 AI Agent 技能训练优化器

> **来源**：[github.com/microsoft/SkillOpt](https://github.com/microsoft/SkillOpt) · [项目页](https://microsoft.github.io/SkillOpt/) · [arXiv:2605.23904](https://arxiv.org/abs/2605.23904)
> **论文**：SkillOpt: Executive Strategy for Self-Evolving Agent Skills (2026年5月)
> **机构**：Microsoft Research
> **License**：MIT
> **PyPI**：`pip install skillopt`（Python 3.10+）

---

## 一句话定义

> SkillOpt 把 AI Agent 的 **skill.md 文档当作可训练参数**，用类似神经网络训练的方法（epochs、batch size、learning rate、validation gate）在文本空间优化它——**不动模型权重，只训练技能文档**。

---

## 内容整理

### 核心思想：训练过程知识，而非模型权重

AI Agent 的瓶颈不再是"知识"（模型权重里已经有了），而是**过程能力**（procedural capability）——工具调用、中间状态检查、领域惯例、失败恢复。

传统 Agent 技能的三种来源都有问题：

| 方式 | 问题 |
|------|------|
| 专家手写 | 依赖经验，无法自动化 |
| LLM 一次性生成 | 无验证，容易跑偏 |
| 自由自修订 | 缺乏优化纪律，技能越改越长，悄悄退化 |

SkillOpt 的方案：**把 skill.md 当作冻结模型外部的一个可训练参数，用深度学习优化的纪律来训练它**。

### 前向-反向-更新循环

SkillOpt 刻意模拟学习算法的三个阶段：

```
1. 前向传播 (Forward / Rollout)
   冻结的目标模型用当前 skill.md 执行一批训练任务
   → 记录消息、工具调用、验证反馈、最终得分

2. 反向传播 (Backward / Reflection)
   独立的优化器模型分析成功和失败的轨迹（分开做 minibatch）
   → 成功轨迹：提炼可复用的模式
   → 失败轨迹：找到需要修正的反复错误

3. 参数更新 (Update / Bounded Edits)
   优化器提出 add/delete/replace 编辑
   → 编辑被合并、去重、排序、按学习率裁剪
   → 通过验证门控：只有严格提升验证集得分才接受
   → 被拒绝的编辑进入 rejected-edit buffer（负反馈）
```

### 五个关键控制组件

| 组件 | 类比 | 作用 |
|------|------|------|
| **Rollout batch size** | forward pass 的 batch size | 控制每次更新收集多少证据 |
| **Textual learning rate** | 学习率 | 限制每步编辑量，防止有用规则被大重写覆盖 |
| **Rejected-edit buffer** | 负样本记忆 | 被拒绝的编辑作为负反馈传给后续优化器调用 |
| **Slow / Meta update** | epoch 级慢更新 | 跨 epoch 整合长期教训（单 batch 看不到的） |
| **Validation gate** | held-out validation | 严格单调提升——不通过就拒绝 |

### 产出物：best_skill.md

- 紧凑：中位数 ~920 tokens（300-2000 范围）
- 可读：像资深从业者的建议
- 可审计：每条编辑有记录
- **可迁移**：跨模型规模、跨 Agent 框架、跨相近基准测试无需重训

> 最终技能里通常只有 1-4 条被接受的编辑。OfficeQA 的 +39.0 分提升来自**单条被接受的编辑**。

### 实验结果：52/52 全胜

6 个基准测试 × 7 个目标模型 × 3 种执行模式 = **52 个评测单元，全部最佳或并列最佳**。

| 目标模型 | 执行方式 | 平均提升 |
|---------|---------|---------|
| GPT-5.5 | Direct chat | **+23.5** |
| GPT-5.5 | Codex CLI | **+24.8** |
| GPT-5.5 | Claude Code | **+19.1** |
| GPT-5.4-mini | Direct chat | +12.7 |
| GPT-5.4-nano | Direct chat | +24.9 |
| GPT-5.2 | Direct chat | +16.6 |
| Qwen3.5-4B | Direct chat | +19.2 |

**最大提升出现在过程性任务**：
- SpreadsheetBench: 41.8 → 80.7 (+38.9)
- OfficeQA: 33.1 → 72.1 (+39.0)
- LiveMathBench: 37.6 → 66.9 (+29.3)

### 小模型 + 优化技能 ≈ 大模型

- GPT-5.4-mini + skill (64.3) > GPT-5.4 无 skill 基线 (59.7)
- GPT-5.4-nano + skill (57.4) > GPT-5.2 无 skill 基线 (51.3)
- Qwen3.5-4B + skill > GPT-5.2 无 skill 基线

> 曾经需要更大模型才能实现的收益，现在一个优化的 skill 文件就能近似。

### 跨框架迁移验证

| 迁移方向 | 结果 |
|---------|------|
| GPT-5.4 → GPT-5.4-nano (跨模型) | 技能仍然有效 |
| Codex 训练 → Claude Code (跨框架) | 22.1 → 81.8 (+59.7)，略高于 Claude Code 内直接训练 (80.4) |
| GPT-5.4-nano 自优化 | SpreadsheetBench 超越基线 |

> 跨框架迁移说明 SkillOpt 学到的是**通用工作流逻辑**，不是框架特定的配方。

### 消融实验

| 组件 | 移除后 SpreadsheetBench |
|------|----------------------|
| 完整 SkillOpt | **77.5** |
| 无 learning rate | 75.7 |
| 无 rejected buffer | 72.9 |
| 无 meta skill + slow update | **55.0** (暴跌) |

### 工程架构

| 组件 | 说明 |
|------|------|
| **目标模型** | 冻结的 LLM（GPT/Qwen/任意 OpenAI 兼容） |
| **优化器模型** | 独立模型（论文用 GPT-5.5），分析轨迹提出编辑 |
| **后端** | `openai_chat` / `claude_chat` / `qwen_chat` / `openai_compatible` / `codex_exec` / `claude_code_exec` / `cursor_exec` |
| **基准测试** | `skillopt/envs/<name>/` 包含 adapter + data loader + 评分 helper |
| **WebUI** | Gradio 监控面板（默认端口 7860） |
| **Cursor 插件** | `.cursor-plugin` 目录 |

### 安装与使用

```bash
# 安装
pip install skillopt

# 文档
# https://github.com/microsoft/SkillOpt/blob/main/docs/index.md
```

---

## 查询拓展

- SkillOpt 的 textual learning rate 具体怎么度量"编辑量"？按 token 数还是编辑操作数？
- rejected-edit buffer 的容量和淘汰策略是什么？
- 论文中 GPT-5.5 作为优化器的 API 成本是多少？一次完整训练需要多少次优化器调用？
- best_skill.md 跨模型迁移时，有没有出现负面迁移（某模型上变差）的情况？
- SkillOpt 的 validation gate 是否会过拟合验证集？validation split 怎么设计？
- Hermes Agent 的 Skill 体系能否直接接入 SkillOpt？需要什么适配？
- `skillopt_sleep` 是什么？从目录名看像是"睡眠/低频训练"模式？

---

## 归纳总结

SkillOpt 是一个范式转换级的工作——**把"写 prompt"变成了"训练 skill"**。

核心洞察：AI Agent 的过程知识（procedural knowledge）不一定非得存在模型权重里。一个紧凑的、可读的、可审计的 natural language skill 文档，同样可以作为"可训练参数"被系统化优化。而且这种优化：

1. **不需要 GPU** — 训练成本是优化器模型的 API 调用
2. **部署成本为零** — skill.md 只是系统提示词的一部分
3. **可迁移** — 跨模型、跨框架、跨任务
4. **可审计** — 每条编辑有记录，rejected 有反馈
5. **单调提升** — validation gate 保证不退化

这意味着领域适配 Agent 的路径从"微调权重"转向"训练一个小的、可版本控制的 natural language 技能层"——**只要存在自动评估或可靠的验证器**。

---

## 趋势判断

- **Skill-as-Trainable-Parameter 范式确立**：SkillOpt 证明了"模型冻结、训练外部技能"这条路走通了。微软同时推出 SkillLens（配套项目），说明这是系统性的研究方向
- **小模型+优化技能>大模型**：GPT-5.4-nano + skill > GPT-5.2 无 skill，意味着推理成本可以被技能优化大幅压缩
- **Agent 训练不需要 GPU 的时代**：text-space optimization 只需 API 调用，AI Agent 的"微调"门槛从 GPU 集群降到 API Key
- **技能市场崛起**：当 best_skill.md 可以迁移复用，技能本身成为可交易的数字资产（类似模型权重在 HuggingFace 上的地位）
- **验证器（Verifier）成为关键基础设施**：SkillOpt 的前提是"存在自动评估或可靠验证器"，验证器质量直接决定技能优化上限

---

## 关联分析

- **与 Hermes Agent Skill 体系的直接关联**：Hermes 有 180+ Skills，全部是手写或错误模式提取的。SkillOpt 可以**自动化优化这些 Skill**——用 Hermes 的 cron 执行历史作为 rollout 数据，用 glm-5.2 或更强模型作为优化器，自动迭代每个 Skill 的 SKILL.md。这是 Hermes 自我进化能力的直接升级路径
- **与用户 evolver/error-case-library 系统的关联**：用户已有的 evolver Skill（错误模式→规则沉淀）和 SkillOpt 是同一个思路的不同实现——evolver 是手工规则提取，SkillOpt 是系统化自动优化。两者可以融合
- **与 auto-prompt-optimization 的关联**：用户已有 OPRO/GEPA/Sprig 方法选型的 Skill。SkillOpt 是 GEPA（生成式提示优化）的工业级进化版——增加了 validation gate、rejected buffer、slow update 等稳定性控制
- **与 FDE 商业模式的关联**：SkillOpt 的跨框架迁移特性意味着——FDE 训练好的 best_skill.md 可以跨 Codex/Claude Code/Cursor 复用，一次训练多次交付
- **与数字克隆的关联**：用户的数字克隆项目需要建模用户的决策风格和行为模式，SkillOpt 可以把这种"过程知识"训练成可迁移的 skill 文档

---

## 📎 关键链接

- 📖 论文：[arXiv:2605.23904](https://arxiv.org/abs/2605.23904)
- 🏠 项目页：[microsoft.github.io/SkillOpt](https://microsoft.github.io/SkillOpt/)
- 💻 GitHub：[github.com/microsoft/SkillOpt](https://github.com/microsoft/SkillOpt)
- 📦 PyPI：`pip install skillopt`
- 📰 微软博客：[SkillOpt: Agent skills as trainable parameters](https://www.microsoft.com/en-us/research/blog/skillopt-agent-skills-as-trainable-parameters)
- 🎬 Demo：[YouTube](https://youtu.be/JUBMDTCiM0M)

---

*笔记创建：2026-08-06 · 来源：Microsoft Research · arXiv:2605.23904*


## 相关笔记

- [Skill-Use Benchmark](./explore/2026-08-06-SkillUse.md) — Skill 使用能力评估，SkillOpt 优化的验证靶标
- [DeepSeek Agent Harness](./2026-08-06-DeepSeek-Agent-Harness执行栈全景图.md) — Harness 作为 SkillOpt 执行底座
- [open-kimi-ppt skill](./2026-08-06-open-kimi-ppt-skill-AI-Agent生成PPT.md) — 具体 Skill 实现案例，SkillOpt 可优化对象
- [自进化 AI Agent 前沿 MANTA](./2026-08-01-自进化AI-Agent前沿-MANTA动态拓扑与Skill-Self-Play技能共进化.md) — Skill 自进化理论框架
