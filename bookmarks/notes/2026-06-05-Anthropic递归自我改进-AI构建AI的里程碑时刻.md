# Anthropic 递归自我改进：AI 构建 AI 的里程碑时刻

> **来源**：Anthropic Institute · anthropic.com · 2026-06-05
> **原文**：https://www.anthropic.com/institute/recursive-self-improvement
> **评分**：⭐5/5
> **标签**：#递归自我改进 #AI安全 #Anthropic #Agent #编码代理 #自主进化

## 摘要

Anthropic Institute 发布重磅报告，披露内部数据表明 AI 正在加速 AI 自身的开发。Anthropic 工程师 2026 Q2 每天合并的代码量是 2024 年的 8 倍，其中超过 80% 的代码由 Claude 编写。Claude Mythos Preview 可连续工作 16 小时以上。报告描绘了从"人写代码"到"AI 自主构建 AI 继任者"的演进路径，并警告：递归自我改进虽然不是必然，但可能比大多数机构准备得更快到来。

## 核心内容

### AI 开发 AI 的四阶段演进

1. **2021-2023 人类驱动**：传统软件工程，人写代码、人做研究
2. **2023-2025 聊天机器人**：AI 辅助生成代码片段，人工复制粘贴
3. **2025-2026 编码代理**：Agent 可独立编写和编辑整个文件
4. **Today 自主代理**：Agent 可自行运行代码、委派工作给其他 Agent

### 关键数据

- 80%+ Anthropic 合并代码由 Claude 编写（2026.05）
- 工程师日均代码合并量 8× 于 2024 年
- 任务完成时长趋势：每 4 个月翻倍（从 7 个月翻倍加速）
  - Claude Opus 3（2024.03）：4 分钟任务
  - Claude Sonnet 3.7（2025.03）：1.5 小时任务
  - Claude Opus 4.6（2026.03）：12 小时任务
- SWE-bench：2 年内从个位数到饱和
- CORE-Bench（论文复现）：从 20%（2024）到饱和（15 个月后）
- Mythos Preview 在 METR 测试中可工作 16+ 小时

### 工程能力 vs 研究能力

- **工程**：Claude 已能处理非明确指定的问题（给出目标，自动找方法）
- **研究**：Claude 在执行明确实验时已匹配甚至超越人类
- **差距**：选择正确目标/方向的判断力仍是人类优势
- 这正是"今天的 AI"与"能自主设计继任者的系统"之间的差距

### 安全隐含

- 递归自我改进可能增加人类失去对 AI 控制的风险
- 如果系统能完全构建自己的继任者，安全、监控、行为塑造变得至关重要
- Anthropic 员工调查显示 4× 生产力提升（自我估计，可能偏高）

## 关键概念

- **递归自我改进 (Recursive Self-Improvement)**：AI 系统能够完全自主地设计和开发自己的继任者
- **任务长度倍增时间**：AI 可靠完成的任务时长翻倍周期，从 7 个月缩短到 4 个月
- **工程 vs 研究**：工程是"执行明确方案"，研究是"判断哪些问题值得解"
- **Benchmark 饱和**：模型在某个测试中接近 100% 表现

## 能力边界

- 数据仅来自 Anthropic 内部，其他公司可能不同
- LOC（代码行数）是不完美的生产力指标
- 员工自评 4× 生产力可能有幸存者偏差
- 报告未给出递归自我改进的具体时间预测（只说"202X?"）
- 缺少独立第三方验证

## 最佳实践

- 跟踪"任务长度倍增时间"而非单一 benchmark 分数
- 区分"执行能力"和"判断力"两个维度评估 AI
- 关注 AI 生成代码的合并比例作为采纳度指标
- 安全治理必须与能力增长同步推进

## 🔍 借鉴学习进化点

1. **任务长度倍增追踪法**：Hermes 可用类似指标追踪 Agent 任务完成能力。在 cron 任务中记录每个任务的实际执行时长，建立倍增基线。
2. **8× 工程师生产力模型**：80% 代码由 AI 编写的模式直接适用于 Hermes Skill 开发。量化记录每条 Skill 的"AI 贡献比"，评估 skill_auto_inject 的实际效率。
3. **Agent 自主等级分类**：借鉴四阶段模型（聊天→编码→代理→自主），为 Hermes cron jobs 建立类似的自主等级评估体系，当前大部分 cron 处于"聊天"到"编码"级别。
4. **安全与能力同步推进**：Hermes auto-defense-check 应随 Agent 能力提升而升级检测项。当 cron 任务复杂度增加时，自动增加安全审查频率。
5. **多 Agent 委派模式**：报告中"Agent 委派工作给其他 Agent"与 Hermes 的 subtask-lifecycle 直接相关。可探索让 watchdog 委派修复任务给专门的修复 Agent。

## 🔗 RAG / Wiki 联动

### 当前状态
- Wiki KB 已有多篇 Anthropic 相关笔记
- RAG 索引包含 AI 安全相关内容
- Memory 中有 Anthropic 首度盈利、Colossus2 等条目

### 改进方案
1. 将"递归自我改进"加入 Wiki KB 的 AI 安全节点
2. 与已有 Anthropic 首度盈利笔记建立交叉引用
3. 关联 agent-memory-contamination 笔记（行为漂移风险）

### 已执行操作
- ✅ 笔记写入 bookmarks/notes
- ⏳ 待更新 ubot-topics-index.json


## 相关笔记

- [[2026-04-21-AI自我进化与人类退场]] — AI自我进化主题
- [[2026-05-29-AI-Agent自进化系统2026-闭环设计-记忆架构与工程实践]] — Agent自进化闭环
- [[2026-04-23-深入源码-Hermes-Agent-如何实现Self-Improving]] — Self-Improving实践
- [[2026-05-25-Claude-Code之父Boris-Cherny-编程已死千级Agent夜间打工]] — Claude编码代理
- [[2026-06-05-Anthropic开源AI漏洞发现框架-Defending-Code-Reference-Harness]] — 同源Anthropic安全

