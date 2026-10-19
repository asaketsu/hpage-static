# agent-coding-playbook 竞品分析

> 分析日期：2026-05-05  
> 仓库：https://github.com/bravekingzhang/agent-coding-playbook  
> 定位：AI Coding 工程实践手册

---

## 项目概要

**一句话总结**：把工程师的工程判断沉淀成 Agent 能执行的规则、Skill、检查清单和工作流。

**核心原则**：
1. Think Before Coding — 写代码前先想清楚
2. Simplicity First — 优先最简单直接的实现
3. Surgical Changes Only — 像外科手术一样精准改代码

---

## 架构分析

```
agent-coding-playbook/
├── CLAUDE.md / AGENTS.md   # 项目级行为规则
├── skills/                  # 5个标准化 Skill
├── checklists/              # 4个检查清单
├── docs/                    # 5篇方法论文档
├── examples/                # 好坏 Prompt 示例
└── templates/               # 模板
```

**技术栈**：纯文档项目（Markdown），无代码依赖。

---

## 核心模式

### 1. Context Engineering
> 控制 signal 和 noise，不是信息越多越好。

关键点：
- Context 太小 → Agent 猜
- Context 太大 → 噪音淹没信号
- 正确做法：项目规则 + 相关文件 + 工具结果

### 2. AI Coding Maturity Model
5级成熟度：
- L0: 随意使用（无共享规则）
- L1: 有项目规则（CLAUDE.md/AGENTS.md）
- L2: 有共享 Skills 和检查清单
- L3: 有自动化检查和 CI 集成
- L4: 可审计、可回溯、可度量

### 3. Vibe Coding Risk Level
- L1 低风险：个人脚本、原型（可接受 vibe coding）
- L2 中风险：普通业务功能（需检查清单）
- L3 高风险：支付、权限、安全（禁止 vibe coding）

---

## 与我们系统的对比

| 维度 | agent-coding-playbook | Hermes Agent |
|------|----------------------|--------------|
| 定位 | 方法论手册 | 自动化系统 |
| 落地 | 人工执行 | 自动执行 |
| Skill 系统 | 5个示例 | 70+ 实战 Skills |
| 自我进化 | 无 | 有（evolver + memory） |

**结论**：它是"教人怎么用 Agent"，我们是"Agent 自己就会"。

---

## 融合计划

### 立即落实（①档）— 已执行

1. **Context Engineering 概念** → ✅ 已融入 hermes-agent-skill-authoring skill
   - 新增 "Context Engineering" 章节（含模板扩展、评估标准）
   - 每个新 Skill 可选增加 `## Context Requirements` 段
   - 核心原则：信息不够就停下来问，不要猜；区分信号与噪音

2. **AI Coding Maturity Model 自评**
   - **当前 Hermes Agent 水平：L3.5**（有自动化检查 + 可度量，但审计链不完整）
   
   | 级别 | 标准 | Hermes Agent 现状 | 达成度 |
   |------|------|-------------------|--------|
   | L0 随意 | 无共享规则 | ❌ 不适用 | — |
   | L1 有规则 | CLAUDE.md/AGENTS.md | ✅ 双规则文件 | 100% |
   | L2 有 Skills | 共享 Skills + 检查清单 | ✅ 70+ Skills + checklists | 100% |
   | L3 自动化 | 自动检查 + CI | ✅ watchdog/cron/evolver | 90% |
   | L4 可审计 | 全链路可追溯可度量 | 🟡 部分达成（event-journal 有，但非强制） | 60% |
   
   - **差距**：L4 需要 event-journal 成为每个 Skill 的默认行为（当前是可选的）
   - **目标**：关键 Skill 强制写 event-journal，实现全链路审计

### 记录备用（②档）
- Vibe Coding Risk Level → Memory 记录，未来做任务风险评估用

### 知识存档（③档）
- Checklist 模板 → 参考资料，不主动使用

---

## 相关笔记
- [[repo-absorption]] — 开源项目吸收流程
- [[skill-pipeline]] — Skill 组合流水线模式
