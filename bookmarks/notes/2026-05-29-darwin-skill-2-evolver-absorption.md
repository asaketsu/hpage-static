# 达尔文 Skill 2.0 vs Hermes Evolver — 深度对比与融合吸收

> 来源：@AlchainHust（花叔）推文 2026-05-28 | darwin-skill 4万star | 融合日期：2026-05-29

## 摘要

分析花叔的达尔文 Skill 2.0 自进化系统（受 Karpathy autoresearch 启发的 5 阶段进化循环），与 Hermes Evolver 做架构级对比，提炼 3 个关键差异并融合落地。

## Darwin Skill 2.0 核心架构

5 阶段进化循环：
```
Discovery → Evaluation → Improvement → Testing → Keep or Revert
```

核心思想：把模型训练的实验循环（hypothesis → experiment → evaluate → keep/discard）移植到 Skill 进化。

## Hermes Evolver 原架构（融合前）

5 阶段管线：COLLECT → IDENTIFY → GENERATE → VALIDATE → RECORD

优势（Darwin Skill 不具备的）：
- 三问验证门禁（Q1行为改变 + Q2可grep + Q3机器验证）
- PRM 多维度量化评分
- Rejected-Edit Buffer（借鉴 SkillOpt 论文）
- 经验闭环四步法（DECIDE → REVIEW → REFLECT → RETRIEVE）
- 辩证法记忆融合（黑格尔正反合）
- 反馈驱动规则自适应

## 三大关键差异与融合

### 差异 1：Testing 阶段 — 改进后自动执行验证

| Darwin Skill 2.0 | Hermes Evolver（融合前） |
|-----------------|----------------------|
| Testing 阶段：改进后自动测试，验证 Skill 真正可用 | VALIDATE 三问门禁：逻辑验证但不执行实际测试 |

**融合方案**：新增 TEST 阶段（阶段 5）
- 三档风险分级：LOW/MEDIUM/HIGH 对应不同验证深度
- LOW（ADD）：grep + skill_view → 自动 Keep
- MEDIUM（REPLACE）：+ 检查依赖方影响
- HIGH（DELETE/跨依赖）：构造测试用例空跑 → Keep/Revert
- 24h 回归检查窗口

### 差异 2：Keep or Revert — 已应用编辑的自动回滚

| Darwin Skill 2.0 | Hermes Evolver（融合前） |
|-----------------|----------------------|
| 明确回滚机制：测试不通过自动 revert | Rejected-Edit Buffer 只管"拒绝的"，已应用的无回滚 |

**融合方案**：新增 REVERT 阶段（阶段 6）
- applied-edits.jsonl 记录每次应用的 old_string 快照
- 触发条件：TEST 失败 / 48h 内 PRM 持续下降 / 用户反馈改坏
- 回滚 = 逆向 patch（new→old）
- 防死循环：同一编辑回滚 ≥2 次标记 abandoned

### 差异 3：Discovery — 主动发现改进机会

| Darwin Skill 2.0 | Hermes Evolver（融合前） |
|-----------------|----------------------|
| Discovery 阶段：主动探索改进机会 | COLLECT：被动收集错误信号 |

**融合方案**：新增 DISCOVERY 子阶段（阶段 1.5）
- Skill 使用频率扫描（被加载但未执行 → 过时/缺陷）
- Cron 产出质量趋势（PRM 持续下降 → prompt 退化）
- Pitfall 积累率（>10 条 → 结构性缺陷需重构）
- 用户隐性信号（跳过建议、反复手动纠正）
- 跨 skill 重复代码（候选合并）
- 产出写入 discovery-candidates.jsonl

## 融合后架构

```
Evolution Pipeline（7 阶段，v2026-05-29）

1. COLLECT      → 收集显式错误信号
  1.5. DISCOVERY → 主动发现隐式改进机会 ⭐ 新增
2. IDENTIFY     → 识别重复模式
3. GENERATE     → 生成修复协议（有界编辑）
4. VALIDATE     → 三问门禁验证
5. TEST         → 改进后自动执行验证 ⭐ 新增
6. REVERT       → 自动回滚机制 ⭐ 新增
7. RECORD       → 记录进化日志（含 TEST 结果）
```

## 竞品定位分析

| 维度 | Darwin Skill 2.0 | Hermes Evolver（融合后） |
|------|-----------------|----------------------|
| 进化驱动 | 主动探索 + 实验循环 | 错误驱动 + 主动发现（互补） |
| 验证体系 | Testing + Keep/Revert | 三问门禁 + TEST + REVERT（更强） |
| 评分体系 | 无 | PRM 五维度量化（独有优势） |
| 记忆体系 | 无 | 辩证融合 + 三层降级 + 经验闭环（独有） |
| 适用范围 | Claude Code Skill | Hermes Agent 全栈（skill/cron/memory/脚本） |

**结论**：融合后 Hermes Evolver 在 Darwin Skill 的实验循环框架基础上，保留了独有的 PRM 评分、经验闭环、辩证融合三大能力，形成更完整的自进化体系。

## 关联笔记
- [[2026-05-29-self-evolution-research]] — 自进化研究综述
- [[2026-05-26-skillopt-absorption]] — SkillOpt 吸收映射

## 借鉴点落实审计

| 借鉴点 | 档次 | 落实方式 | 状态 |
|--------|------|---------|------|
| Testing 阶段 | ①有利进化 | evolver 新增阶段 5 TEST | ✅ 已 patch |
| Keep or Revert | ①有利进化 | evolver 新增阶段 6 REVERT | ✅ 已 patch |
| Discovery 主动发现 | ①有利进化 | evolver 新增阶段 1.5 DISCOVERY | ✅ 已 patch |

## 相关笔记
- [[达尔文Skill2.0深度分析-Evolver对比吸收.md]] (关键词: 达尔文, Skill, Evolver, Hermes)
- [[2026-05-27-45个HermesAgent自动化案例（上）.md]] (关键词: Skill, Hermes)
- [[2026-04-17-AutoClaw-自进化与Skill商店.md]] (关键词: Skill, Hermes)
