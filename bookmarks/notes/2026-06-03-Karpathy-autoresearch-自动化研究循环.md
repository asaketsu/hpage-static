# Karpathy autoresearch：仅用 Markdown 做出自动化研究循环

- 📅 2026-06-03
- ⭐ 5/5 — Markdown-as-Program 范式的极致验证，直接印证我们的 SKILL.md 体系方向
- 🏷️ #Agent #自动化研究 #Markdown即程序 #Karpathy
- 📰 53AI 转载 / GitHub karpathy/autoresearch
- 🔗 https://github.com/karpathy/autoresearch (84.8k⭐, 12.3k forks)

## 摘要

Andrej Karpathy 发布 autoresearch 项目——一个极简的 AI 自主研究框架。核心创新：不写复杂 Python 编排脚本，而是用纯 Markdown 文件（program.md）作为"可执行程序"，LLM（Claude Code/Codex）作为运行时读取并执行。整个仓库仅 3 个核心文件，48 小时自主完成 700 次实验，18% 保留率，将验证损失从 0.9979 降至 0.9697。

## 核心内容

### 1. 极简三文件架构

| 文件 | 职责 | 可变性 |
|------|------|--------|
| `program.md` | 自然语言"程序"——定义研究循环逻辑 | Agent 可迭代优化 |
| `prepare.py` | 数据准备、评估、常量定义 | 只读，不可修改 |
| `train.py` | 模型架构、优化器、训练循环（~630行） | Agent 唯一可修改的代码文件 |

### 2. program.md 研究循环

```markdown
LOOP FOREVER:
1. 查看 git 状态：当前分支/commit
2. 用实验想法修改 train.py
3. git commit
4. 运行实验：uv run train.py > run.log 2>&1
5. 读取结果：grep "^val_bpb:" run.log
6. 如果为空→崩溃，读堆栈追踪，尝试修复
7. 将结果记录到 TSV
8. 如果 val_bpb 改善（更低）→保留分支
9. 如果 val_bpb 持平或更差→git reset 回退
```

### 3. 两条铁律

**NEVER STOP**：Agent 不许停下来问"要继续吗"之类的问题。人类可能在睡觉，期望 Agent 无限工作直到被手动停止。

**Simplicity Criterion**：同等条件下，简洁优先。加 20 行 hacky 代码换来 0.001 改进？不值得。删代码换来 0.001 改进？必须保留。

### 4. 关键设计决策

- **固定时间预算**：每实验严格 5 分钟（`TIME_BUDGET`），确保公平比较
- **val_bpb 指标**：Validation Bits Per Byte，对词汇表大小不敏感，Agent 可以安全修改词汇表
- **TSV 结果追踪**：三状态（keep/discard/crash），简洁可解析
- **Git 即状态机**：branch/commit/reset 作为实验管理基础设施

### 5. 实战成绩

| 指标 | 数值 |
|------|------|
| 运行时长 | 48 小时 |
| 总实验次数 | ~700 次 |
| 保留改进 | 23 次（18% 保留率） |
| val_bpb | 0.9979 → 0.9697 |

## 🔍 借鉴学习进化点

| 档次 | 借鉴点 | 落实动作 |
|------|--------|----------|
| ①有利进化 | Markdown-as-Program 范式验证，SKILL.md 方向正确 | 已 patch agent-primitive-architecture skill |
| ①有利进化 | NEVER STOP + Simplicity Criterion 双规则 | 已写入 memory |
| ①有利进化 | TSV 结构化实验追踪模式 | 已写入 memory |
| ②有价值 | 固定时间预算做公平比较 | 未来可用于 cron job 评估 |
| ②有价值 | 18% 保留率作为自动化实验基准 | 知识储备 |
| ③知识库 | 单 GPU nanochat 训练、H100 需求 | 仅笔记 |

## 差距对标

| 我们的实践 | 对应 autoresearch 概念 | 差距 |
|-----------|----------------------|------|
| SKILL.md 天然 Markdown-as-program | program.md | ✅ 理念一致，已验证 |
| analysis-learning-loop 闭环 | 自主研究循环 | ⚠️ 有闭环但缺持续迭代机制 |
| Cron job 长时运行 | NEVER STOP 永不停止 | ⚠️ cron 有超时限制 |
| small-batch-execution | Simplicity Criterion | ✅ 已有简洁优先理念 |
| session_search + memory | TSV results 追踪 | ⚠️ 缺结构化实验追踪 |
| harness-checkpoint | Git checkpoint | ✅ 已有检查点机制 |
| error-case-library | crash→修复循环 | ✅ 已有类似机制 |
| skill_stress_test | 实验验证 | ⚠️ 有但非系统化 |

## 🔗 关联性

- 关联 [agent-primitive-architecture](../skills/) — 三原语架构，autoresearch 是 Skills 原语的业界验证
- 关联 [state-machine-loop](../skills/) — 10步状态机循环，与 program.md 的 LOOP FOREVER 异曲同工
- 关联 [harness-architecture](../skills/) — 六层 Harness，更重量级的任务编排

## 💡 启发

1. **自然语言即程序**：Karpathy 证明了不写 Python 编排脚本也能做自动化研究。我们的 SKILL.md 体系走在同一条路上——核心不是代码框架多精巧，而是"指令"写得多清晰。

2. **极简主义的力量**：3 个文件就跑通整个研究循环。对比业界动辄 10+ 文件夹的 Agent 框架，autoresearch 的极简设计更值得学习。

3. **Git 作为实验管理器**：不需要数据库，不需要 MLflow，git commit/reset 就是最好的实验版本控制。这个思路可用于我们的 cron 结果管理。

4. **18% 保留率的启示**：自动化不是100%成功才好。700 次实验只保留 23 次改进，说明"快速试错+严格筛选"比"精心设计单次实验"更高效。

## 🔮 预判

- **短期**：autoresearch 模式会被大量复刻到非训练场景（代码优化、prompt 调优、配置搜索）
- **中期**："Markdown as Program" 成为 Agent 系统的标准接口之一，类似 Dockerfile 之于容器
- **长期**：program.md 本身也会被 Agent 自主迭代优化——Karpathy 已暗示这个方向

## ✅ 落实情况

```
📋 借鉴点落实审计
├── ①有利进化 项：3个
│   ├── Markdown-as-Program 范式 → skill_manage(patch agent-primitive-architecture) ✅
│   ├── NEVER STOP + Simplicity 规则 → memory add ✅
│   └── TSV 追踪模式 → memory add ✅
├── ②有价值 项：2个 → memory 写入 ✅
└── ③知识库 项：3个 → 仅笔记 ✅
```

**三问验证**：
- Q1 系统行为改变？→ 会。下次讨论架构设计时，autoresearch 作为验证案例被自动注入
- Q2 能 grep 到？→ `grep autoresearch agent-primitive-architecture/SKILL.md` = 2 hits ✅
- Q3 谁验证的？→ exit_code=0 + memory tool 返回确认 ✅

## 相关笔记
- [达尔文Skill2.0深度分析-Evolver对比吸收](达尔文Skill2.0深度分析-Evolver对比吸收.md)
