# Skill 自生自灭生命周期：自动发现模式→生成SKILL.md→退化检测→清理归档

> 2026-05-18 | proactive-learn 深度研究 | Topic: Agent Self-Evolution
> 方法：本地知识蒸馏（外部搜索全挂），基于 Hermes Agent 现有 356 个 Skills 的实证分析 + 架构推演
> 字数: ~4500 | 难度: L4（系统设计级）

---

## 一、核心发现（5 个关键发现）

### 发现 1：Hermes 已有 3 层 Skill 管理机制，但生命周期存在"创建容易淘汰难"的不对称问题 — 🔴 核心矛盾

**现状分析**：

| 机制 | Skill | 覆盖阶段 | 成熟度 |
|------|-------|---------|--------|
| 自动创建 | `auto-skill` | 发现→评估→生成→注册 | ✅ 可用 |
| 定期审查 | `skill-review` | 僵尸检测→冗余检测→合并→归档 | ⚠️ 规则完整但执行不充分 |
| 自我进化 | `evolver` | 错误→模式→修复→基因 | ✅ 可用 |

**不对称问题实证**：
- 当前系统有 **356 个 Skills**，但 **归档目录为空**（`~/.hermes/skills/.archive/` 下 0 个文件）
- 创建速度：近 45 天新增 ~150 个 Skills（日均 3.3 个）
- 淘汰速度：0 个被归档或删除
- 预测：按此速度，6 个月内 Skills 将达到 700+，管理成本指数级增长

**根因分析**：
1. **创建有明确触发**（auto-skill 在任务完成时自动评估），但**淘汰无自动化执行**
2. `skill-review` 定义了僵尸检测规则（90 天未使用），但 Cron 执行频率（每周）和执行深度不足
3. 删除操作有心理摩擦力——担心"删了以后要用"，缺乏"安全删除"机制（类似垃圾箱）
4. 缺少**Skill 使用计数器**——没有程序化追踪每个 Skill 的调用频次

---

### 发现 2：Skill 生命周期可建模为 5 阶段，每阶段需要不同的自动化策略 — 🔴 系统设计框架

借鉴软件开发生命周期（SDLC）和生物生命周期理论，提出 **Skill Lifecycle Model (SLM)**：

```
    ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐
    │ DISCOVER │───→│  CREATE  │───→│  ACTIVE  │───→│  DECAY   │───→│ RETIRE   │
    │ 模式发现  │    │ 生成注册  │    │ 活跃使用  │    │ 退化降级  │    │ 归档清理  │
    └─────────┘    └─────────┘    └─────────┘    └─────────┘    └─────────┘
         ↑                                              │                │
         └──────────────────── REVIVE ──────────────────┘                │
         （被唤醒的 Skill 重新进入 ACTIVE）                                 │
                                                                └→ RECYLE
                                                                  （经验提取
                                                                   后彻底删除）
```

**各阶段的自动化策略**：

| 阶段 | 持续时间 | 自动化程度 | 关键指标 | 触发条件 |
|------|---------|-----------|---------|---------|
| **DISCOVER** | 实时 | 80% 自动 | 模式匹配得分 | 同类任务出现 ≥2 次 |
| **CREATE** | 分钟级 | 90% 自动 | SKILL.md 质量分 | auto-skill 评估通过 |
| **ACTIVE** | 数周-数月 | 10% 自动（被动记录） | 使用频次/成功率 | 每次被 skill_view 加载 |
| **DECAY** | 数周 | 70% 自动 | 无使用天数/错误率 | 30 天未使用 或 错误率 >30% |
| **RETIRE** | 数天 | 50% 自动 | 最终决策 | 90 天未使用 + 无人反对 |

**关键洞察**：当前系统在 DISCOVER→CREATE 和 ACTIVE 阶段有良好覆盖，但 **DECAY→RETIRE 的自动化几乎为零**。这是最大的改进空间。

---

### 发现 3：Skill 退化有 4 种可检测的模式，每种需要不同的响应策略 — 🟡 可操作

通过分析 Hermes 历史错误模式（evolver pitfalls 库），识别出 4 种 Skill 退化模式：

#### 模式 A：内容过时（Content Stale）
```
症状：Skill 中引用的命令/URL/版本号已失效
检测：定期验证 Skill 中的外部引用（URL 可达性、CLI 版本兼容性）
案例：ths-auto-trader skill 中 "xtquant 不在 PyPI" 的描述在 2026-05-18 被发现过时
响应：自动 patch 或标记 ⚠️
频率估计：~10% 的 Skills 每月会产生过时内容
```

#### 模式 B：需求消失（Demand Death）
```
症状：Skill 长时间未被触发加载
检测：追踪 skill_view() 和 Cron 任务中的 Skill 引用
案例：大量红队安全 Skills（200+）可能属于此类——创建了但极少在 Cron 空闲时使用
响应：30 天标记观察 → 90 天归档 → 180 天经验提取后删除
```

#### 模式 C：功能重叠（Functional Overlap）
```
症状：多个 Skills 解决同一问题，触发条件模糊
检测：语义相似度分析 + description 字段关键词重叠
案例：`skill-pipeline` vs `harness-architecture` vs `task-executor` 可能有重叠
响应：合并为统一 Skill，被合并的标记 `absorbed_into`
```

#### 模式 D：模型超越（Model Outgrown）
```
症状：基础模型能力提升后，Skill 中的详细步骤变为冗余
检测：对比 Skill 创建时的模型版本 vs 当前版本
案例：早期详细描述 curl 用法的 Skill，在当前模型下可能只需一句话提示
响应：精简 Skill 内容，从 200 行压缩到 50 行
```

---

### 发现 4：Skill 使用追踪是当前系统最关键的缺失基础设施 — 🔴 架构缺陷

**问题**：Hermes 的 skill_view() 和 skill_manage() 没有内置使用统计。无法回答"这个 Skill 上次被使用是什么时候？"

**影响链**：
```
无使用统计 → 无法判断僵尸 → 无法自动退化 → Skills 膨胀 → 上下文污染 → 效率下降
```

**可行方案（3 种，按实现难度排序）**：

| 方案 | 实现方式 | 精度 | 工作量 |
|------|---------|------|--------|
| **方案 1：文件时间戳** | 每次 skill_view() 后 touch SKILL.md 更新 atime | 低（被系统备份等干扰） | 极小 |
| **方案 2：访问日志** | skill_view() 内部追加 JSONL 日志到 `~/.hermes/skill-access.log` | 中（记录每次加载） | 小 |
| **方案 3：使用计数器** | SKILL.md frontmatter 新增 `access_count` + `last_accessed` 字段 | 高（精确统计） | 中 |

**推荐方案 2**：JSONL 追加日志，零侵入，可异步分析。

```jsonl
{"skill":"evolver","action":"view","timestamp":"2026-05-18T04:50:00Z","context":"cron"}
{"skill":"skill-review","action":"view","timestamp":"2026-05-18T04:50:05Z","context":"cron"}
```

统计脚本定期（每日 Cron）分析日志，更新 `~/.hermes/skills/skill-usage-stats.json`：
```json
{
  "evolver": {"views": 42, "last_viewed": "2026-05-18", "last_patched": "2026-05-18"},
  "skill-review": {"views": 5, "last_viewed": "2026-05-11", "last_patched": "2026-05-11"}
}
```

---

### 发现 5：Skill 自生自灭的最佳实践可以从 3 个领域借鉴 — 🟡 跨领域知识融合

#### 借鉴 1：软件包管理（npm/PyPI）

| 概念 | 映射到 Skill |
|------|-------------|
| `package.json` dependencies | Skill 的 triggers/dependencies 声明 |
| deprecation 警告 | 退化检测 → 通知用户 |
| `npm audit` | Skill 安全审查（引用的 URL/命令是否安全） |
| semver 语义化版本 | Skill 版本号 + 兼容性声明 |
| `npm unpublish` | Skill 归档/删除 |

**关键学习**：npm 的 `deprecation` 是"软标记"——不删除但警告使用者。Skill 也应如此：先标记 deprecated，给缓冲期，再归档。

#### 借鉴 2：Git 分支生命周期（GitHub Flow）

| 概念 | 映射到 Skill |
|------|-------------|
| feature branch | 新创建的 Skill（experimental） |
| merge to main | 经过验证的 Skill（stable） |
| branch deletion | Skill 归档（合并后的分支可安全删除） |
| stale branch 检测 | GitHub 自动标记超过 X 天无 commit 的分支 |

**关键学习**：GitHub 的 stale bot 机制——自动给不活跃的分支加标签，如果无人反对则自动删除。Skill 也需要一个 "stale bot"。

#### 借鉴 3：免疫系统的细胞凋亡（Apoptosis）

生物学启示：人体每天有 500 亿个细胞通过"程序性死亡"被清除。这不是随机破坏，而是精确控制的：

| 概念 | 映射到 Skill |
|------|-------------|
| 细胞凋亡信号 | Skill 退化信号（未使用/过时/重叠） |
| 死亡标记（磷脂酰丝氨酸外翻） | Skill 标记 deprecated |
| 巨噬细胞清理 | evolver 执行归档 |
| 记忆 B 细胞 | 提取关键经验后保留 |

**关键学习**：细胞凋亡的精髓是"有序退出"——先标记、再收缩、最后清除，每个阶段都有检查点。Skill 的退休也应遵循这种"有序退出"模式。

---

## 二、技术细节：Skill Lifecycle Engine 架构设计

基于以上发现，提出 **Skill Lifecycle Engine (SLE)** 的具体架构：

### 2.1 核心组件

```
~/.hermes/scripts/skill-lifecycle.py
├── discover()     — 扫描任务历史，识别重复模式
├── evaluate()     — 评估是否值得创建 Skill
├── track()        — 追踪 Skill 使用（JSONL 日志）
├── decay_check()  — 退化检测（4 种模式）
├── retire()       — 归档/删除（有序退出）
└── revive()       — 唤醒已归档的 Skill
```

### 2.2 退化检测算法

```python
def decay_check(skill_name: str) -> DecayReport:
    """四维退化检测"""
    signals = []
    
    # 维度 1：需求消失（时间衰减）
    days_unused = (now() - last_access(skill_name)).days
    if days_unused > 90:
        signals.append(("DEMAND_DEATH", "critical", f"{days_unused} 天未使用"))
    elif days_unused > 30:
        signals.append(("DEMAND_DEATH", "warning", f"{days_unused} 天未使用"))
    
    # 维度 2：内容过时（引用检查）
    stale_refs = check_external_refs(skill_name)
    if stale_refs:
        signals.append(("CONTENT_STALE", "critical", 
                        f"{len(stale_refs)} 个引用失效"))
    
    # 维度 3：功能重叠（语义分析）
    overlap_skills = find_similar_skills(skill_name, threshold=0.7)
    if overlap_skills:
        signals.append(("OVERLAP", "warning",
                        f"与 {overlap_skills} 功能重叠"))
    
    # 维度 4：模型超越（压缩潜力）
    skill_size = get_skill_size(skill_name)
    model_capability = estimate_model_coverage(skill_name)
    if model_capability > 0.8 and skill_size > 100:
        signals.append(("MODEL_OUTGROWN", "info",
                        f"当前模型覆盖 {model_capability:.0%}，可压缩"))
    
    return DecayReport(skill_name, signals)
```

### 2.3 有序退出流程（5 步检查点）

```
CHECKPOINT 1: 标记（Tag）
  └─ 在 SKILL.md frontmatter 添加 `status: deprecated`
  └─ 在 skills-index.json 标记 ⚠️
  └─ 缓冲期：14 天

CHECKPOINT 2: 通知（Notify）
  └─ 写入 evolution-log.jsonl
  └─ 如果有 Cron 任务依赖此 Skill，记录影响范围
  └─ 缓冲期：7 天

CHECKPOINT 3: 经验提取（Extract）
  └─ 分析 Skill 内容，提取可复用的知识点
  └─ 写入经验池：experience-pool.jsonl
  └─ 保留到 memory（如果包含独特知识）

CHECKPOINT 4: 归档（Archive）
  └─ 移动到 ~/.hermes/skills/.archive/{skill-name}/
  └─ 更新 skills-index.json（移除条目，添加归档记录）
  └─ 可通过 revive() 恢复

CHECKPOINT 5: 彻底删除（Purge）
  └─ 仅在归档 180 天后且无 revive 记录时执行
  └─ 保留经验池中的提取记录作为"记忆细胞"
```

---

## 三、实践案例

### 案例 1：Hermes 当前 356 个 Skills 的健康度快照

| 类别 | 数量 | 预估僵尸比例 | 说明 |
|------|------|------------|------|
| red-teaming | ~200 | 80%+ | 安全渗透类，日常 Cron 几乎不触发 |
| mlops | ~30 | 30% | 部分过时（如旧版训练方法） |
| devops | ~25 | 20% | 核心运维，活跃 |
| productivity | ~30 | 15% | 高频使用 |
| software-dev | ~20 | 25% | 中频使用 |
| research | ~15 | 20% | 中频使用 |
| 其他 | ~36 | 40% | 混合 |

**预估**：约 120-160 个 Skills（33-45%）处于僵尸或低频状态，但从未被清理。

### 案例 2：Skill 内容过时的真实案例

`ths-auto-trader` skill 在 2026-05-17 的笔记中发现关键过时信息：
- **旧描述**："xtquant 不在 PyPI，需券商渠道获取"
- **实际情况**：xtquant 已上架 PyPI（`pip install xtquant`），版本 250516.1.1
- **检测延迟**：这个过时信息存在了至少 2 周才被发现

如果有自动化的**引用验证**机制，这种过时信息可在 1 天内被检测。

### 案例 3：Skill 创建-淘汰不对称的恶性循环

```
创建容易（auto-skill 自动触发）
    → Skills 增长（356 个且持续增长）
    → available_skills 列表膨胀
    → 模型每次 turn 都要扫描 356 个 Skill 描述
    → Token 浪费（即使大部分 Skill 不相关）
    → 触发条件模糊，错误匹配增加
    → 任务效率下降
```

**量化估算**：356 个 Skill 的 description 字段总长约 50K tokens，每次 turn 的 skill scanning 消耗约 50K tokens。如果清理到 200 个活跃 Skill，可节省 ~22K tokens/turn。

---

## 四、对 Hermes Agent 的具体建议（优先级排序）

### P0 — 立即可做（零代码改动）

1. **手动审查 red-teaming Skills（200+）**：这些安全渗透类 Skill 在日常 Cron 中几乎不使用。建议：
   - 保留 Top 20 最常用的（hack、recon 等入口级）
   - 其余 180+ 全部归档到 `.archive/red-teaming/`
   - 效果：Skills 从 356 降到 ~176，token 节省 ~25K/turn

2. **为 `skill-review` 的 Cron 增加执行深度**：当前只做"报告"，应增加"自动标记 deprecated"动作

### P1 — 短期实现（1-2 天）

3. **实现 Skill 访问日志**：在 skill_view() 调用后追加 JSONL 到 `~/.hermes/skill-access.log`
4. **每日统计脚本**：分析访问日志，更新 `skill-usage-stats.json`
5. **退化检测脚本**：基于统计数据，每周输出退化报告

### P2 — 中期优化（1 周）

6. **Skill Lifecycle Engine（SLE）**：实现上述 5 阶段引擎
7. **引用验证自动化**：定期检查 Skill 中的 URL 可达性和 CLI 版本兼容性
8. **语义重叠检测**：用 embedding 相似度分析 Skill 描述，识别合并候选

---

## 五、知识缺口分析

| 缺口 | 说明 | 填补方式 |
|------|------|---------|
| **Skill 调用频次的精确数据** | 当前无任何使用统计 | 实现 P1 的访问日志 |
| **Token 消耗的量化分析** | 不确定 356 个 Skill 的扫描开销具体多大 | 需要 Hermes 框架层面的 token 计数 |
| **模型超越的检测方法** | 如何判断"当前模型已能覆盖此 Skill" | 需要设计 benchmark 或 A/B 测试 |
| **归档 Skill 的恢复成本** | 归档后再需要的恢复时间 | 需要实测 revive() 流程的延迟 |
| **跨 Agent 的 Skill 共享** | jbot 和 ubot 如何共享/同步 Skill 生命周期 | 需要 exchange-protocol 层面的设计 |
| **Skill 依赖图谱** | Skill 之间的依赖关系（A 引用 B 的输出） | 需要 skill-orchestrator 的依赖分析 |

---

## 六、进化闭环评估

### 可采纳的新工作流/方法

1. ✅ **Skill 退化检测 4 模式框架** → 可 patch 到 `skill-review` skill，增加具体的检测规则
2. ✅ **有序退出 5 步检查点** → 可作为新 skill `skill-retirement` 或 patch 到 `evolver`
3. ✅ **Skill 访问日志方案** → 可记录到 memory 供下次实现

### 一次性知识（仅存笔记）
- 跨领域类比（npm/Git/免疫系统）— 启发性强但无需落地
- 理论模型（SLM 5 阶段）— 概念框架，暂不实现

### 现有 Skill 缺陷
- `skill-review`：缺少**自动化执行**（只有报告没有动作）
- `auto-skill`：缺少**淘汰阶段**（生命周期管理表不完整）
- `evolver`：退化检测只有错误模式，缺少**需求消失**和**模型超越**维度

---

*研究方法：本地知识蒸馏（Tavily/web_search/web_extract 全部不可用），基于 Hermes Agent 356 个 Skills 的文件系统分析和已有 Skill 内容的深度整合。*
*数据来源：skill-review SKILL.md、evolver SKILL.md、auto-skill SKILL.md、agent-autonomy SKILL.md、explore/ 目录历史笔记。*

## 相关笔记
- [Agent Skills才是关键抽象层](../2026-04-02-Agent Skills才是关键抽象层.md)
- [MiniMax Office Skills全家桶](../2026-04-02-MiniMax Office Skills全家桶.md)
- [OpenClaw-paper-review-skill](../2026-04-03-OpenClaw-paper-review-skill.md)
- [SelfImproving-Agent-CLI-infra](../2026-04-05-SelfImproving-Agent-CLI-infra.md)
- [SKILL-md-ai-agent-skills](../2026-04-09-SKILL-md-ai-agent-skills.md)
- [distill-skill-yupi](../2026-04-12-distill-skill-yupi.md)
- [歸藏PPT-Skill-电子杂志风网页演示](../2026-04-24-歸藏PPT-Skill-电子杂志风网页演示.md)
- [竞品吸收笔记-khazix-skills](../2026-04-29-竞品吸收笔记-khazix-skills.md)
- [SkillClaw-analysis](../2026-05-02-SkillClaw-analysis.md)
- [github-ai-trending-mattpocock-skills](../2026-05-05-github-ai-trending-mattpocock-skills.md)
- [lewislulu-html-ppt-skill-analysis](../2026-05-06-lewislulu-html-ppt-skill-analysis.md)
- [skill-building-invoice-automation](../2026-05-10-skill-building-invoice-automation.md)
- [softwarecopyright-skill-analysis](../2026-05-10-softwarecopyright-skill-analysis.md)
- [开源AI模型工具2025春季爆发](../2026-05-18-开源AI模型工具2025春季爆发.md)
- [f5-tts-voice-cloning-incremental](2026-05-18-f5-tts-voice-cloning-incremental.md)
- [autotts-analysis](2026-05-19-autotts-analysis.md)
- [tts-stt-pipeline-optimization-deep-dive](2026-05-19-tts-stt-pipeline-optimization-deep-dive.md)
- [llm_wiki分析与Skill进化](2026-05-20-llm_wiki分析与Skill进化.md)
- [f5-tts-zero-shot-voice-cloning-deep-dive-20260518](f5-tts-zero-shot-voice-cloning-deep-dive-20260518.md)
- [local-tts-stt-optimization-20260519](local-tts-stt-optimization-20260519.md)
- [OpenClaw核心机制Skills全解析](../orphan/2026-04-02-OpenClaw核心机制Skills全解析.md)
- [OpenClaw-Skills-handbook](../orphan/2026-04-07-OpenClaw-Skills-handbook.md)
- [CyberVerse公众号HTML模板分析](../orphan/2026-05-03-CyberVerse公众号HTML模板分析.md)
- [国自然申请书AI-Skill流水线](../orphan/2026-05-04-国自然申请书AI-Skill流水线.md)
- [数据血缘-lineage-工具全景](../orphan/2026-05-09-数据血缘-lineage-工具全景.md)
- [HTML的不合理有效性-Claude-Code-团队](../orphan/2026-05-16-HTML的不合理有效性-Claude-Code-团队.md)
- [20260512-10-skill-学术去ai味框架](../orphan/20260512-10-skill-学术去ai味框架.md)
- [build-ai-cli](../orphan/build-ai-cli.md)
- [frontend-slides-skill](../orphan/frontend-slides-skill.md)
- [hermes-skill-top10-2026w18](../orphan/hermes-skill-top10-2026w18.md)
- [skills-apple](../orphan/skills-apple.md)
- [skills-catalog](../orphan/skills-catalog.md)
- [skills-data-science](../orphan/skills-data-science.md)
- [skills-dogfood](../orphan/skills-dogfood.md)
- [skills-email](../orphan/skills-email.md)
- [skills-github](../orphan/skills-github.md)
- [skills-leisure](../orphan/skills-leisure.md)
- [skills-logo-generator-skill](../orphan/skills-logo-generator-skill.md)
- [skills-smart-home](../orphan/skills-smart-home.md)
- [skills-social-media](../orphan/skills-social-media.md)
- [skills-team-roles](../orphan/skills-team-roles.md)
- [skills-autonomous-ai-agents](../skills-autonomous-ai-agents.md)
- [skills-creative](../skills-creative.md)
- [skills-devops](../skills-devops.md)
- [skills-gaming](../skills-gaming.md)
- [skills-mcp](../skills-mcp.md)
- [skills-media](../skills-media.md)
- [skills-mlops](../skills-mlops.md)
- [skills-note-taking](../skills-note-taking.md)
- [skills-openclaw-imports](../skills-openclaw-imports.md)
- [skills-overview](../skills-overview.md)
- [skills-productivity](../skills-productivity.md)
- [skills-red-teaming](../skills-red-teaming.md)
- [skills-research](../skills-research.md)
- [skills-software-development](../skills-software-development.md)
