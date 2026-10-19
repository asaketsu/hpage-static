# patent-disclosure-skill 精读：8.9k★ 中国专利 Agent 技能的架构解剖——YAML 状态机、路径交接合同与单协调者模式

> **来源**：GitHub handsomestWei/patent-disclosure-skill
> **原文链接**：https://github.com/handsomestWei/patent-disclosure-skill
> **仓库画像**：⭐ 8,930 / 🍴 921 / 393 文件 11MB / Python 3.9+ + Playwright / MIT / 2026-04-07 创建，09-09 仍在活跃更新（5 个月）
> **本地副本**：`~/uclaw/project/patent-disclosure-skill/`（351 文件 5.5MB，剔 .git/图片）
> **沉淀 Skill**：`~/.hermes/skills/devops/orchestrator-handoff-pattern/`
> **笔记日期**：2026-09-09

---

## 零、结论先行

这是目前见过的**工程化程度最高的中文 Agent Skill 仓库**——它把"中国专利全生命周期"（挖点→交底→申请→答复→解读→检索→政策）做成了 7 个子技能包 + 1 个根路由，核心创新不在专利知识本身，而在**多包长流程的编排纪律**：

1. **YAML 状态机 + validator**：phase 跳转必须落在 transitions 表内，机器校验，prompt 里发明新 phase = bug
2. **路径交接合同**：跨包只传路径 + issue id，明令禁止传摘要——从机制上掐死"信息凭记忆漂移"
3. **轮次硬上限**：max_rounds=3 + 三个终态出口（complete/max_rounds/blocked），防死循环
4. **单协调者**：patent-docket 刻意单 agent，不为"技术员/代理师"开子进程

**与用户领域高度相关**：飞机设计企业背景（构型管理/型号资料体系）+ 专利场景天然契合——这套 skill 可直接用于实际专利交底工作。

---

## 一、仓库全景

### 1.1 七子技能架构

| 子包 | 能力 | 触发 | 关键约束 |
|------|------|------|---------|
| patent-disclosure | 挖点→查新→成文→迭代 | "交底书" | Step 1-8 分步 prompt |
| patent-application | 交底→权要/说明书/摘要/附图 | **须显式**+指定交底目录 | 门禁未过未开写 |
| patent-docket | 一趟串起交底+申请 | **须显式**（一条龙/会稿） | 单协调者，只调度不写正文 |
| patent-search | 著录检索（发明人/申请人/分类号） | "/patent-search" | 禁止当查新引擎 |
| patent-reader | 公开号/PDF→通俗笔记+图谱 | "读专利" | Obsidian 知识库沉淀 |
| patent-oa | 审查意见拆解+答复草稿 | "审查答复"/"OA" | RAG 检索增强 |
| patent-exam-policy | 对照国知局口径出政策简报 | "政策简报" | 技能进化仅为旁路 |

### 1.2 规模数据

- 129 个 markdown prompt（知识主体）+ 100+ Python 工具 + YAML schema + pytest 测试
- 每个子包含完整 tests/（test_docket.py / test_material_gate.py 等）——**Skill 带测试**，罕见的高标准
- examples/ 三个完整示例（batch_job_scheduler 发明 / ev_powertrain 实用新型 / desk_lamp 外观）

---

## 二、核心架构解剖（本笔记重点）

### 2.1 根路由 SKILL.md：意图 → 入口

根 SKILL.md 只做一件事：按用户意图 Read 对应子包的 SKILL.md。精髓在**触发纪律**：

```
申请文件：须显式且指定交底目录——"申请文件、申请底稿、申报材料、/patent-apply"
案卷：须显式——"交底申请一起做、从零出交底和申请、一条龙、会稿、/patent-docket"
禁止：因写交底或读专利自动进入政策简报、审查答复、申请文件或案卷
```

**为什么重要**：LLM 执行 A 任务时有惯性顺手做完 B 任务（自动滑包）。显式触发词白名单是从机制上防住这种越界——这和 Hermes 的"笔记指令语义"（「笔记<X链接>」与飞书 wiki 同权=即做免确认）是同一个问题的两面：**哪些动作免确认、哪些必须点名**。

### 2.2 patent-docket：YAML 状态机（最精华）

**静态定义** `references/phases.yaml`：
```yaml
phases: [intake, bootstrap_disclosure, wait_disclosure, bootstrap_application,
         wait_application, triage, ask_human, dispatch_disclosure, wait_disclosure_fix,
         dispatch_application, round_close, terminal_complete, terminal_max_rounds, terminal_blocked]
transitions:
  ask_human: [triage, terminal_blocked]        # 问人时禁止派工
  terminal_*: []                                # 终态禁止再派工
notes:
  - 存在 blocking 且 status=open 的 ask_human 时，只能停留 ask_human 或 terminal_blocked
  - 交底纠正后必须 dispatch_application，禁止只改交底就 round_close
```

**运行时状态** `docket.yaml`：case_id / patent_type / phase / round / paths / issues
**机器校验** `validate_docket.py`：phase 跳转必须在 transitions 内，改完必跑
**人类视图** `TRACKER.md`：由 `emit_tracker.py` 从 yaml 生成，**禁止手搓后与 yaml 分叉**

### 2.3 路径交接合同（handoff_contract.md）

跨包交接**只允许传**：case_id、phase/round、**工作区相对路径**、issue id 列表。

**明令禁止**（每条都是对 LLM 真实失败模式的精准防御）：
- 把交底第三章"概括成要点"代替原文路径 → **防摘要失真**
- 把独权"改写后"交给下一手而不给申请目录 → **防版本漂移**
- "请补全合理结构/常见连接方式"等诱导编造 → **防幻觉填空**
- 子 agent brief、聊天长摘要当技术事实 → **防上下文污染**

回到协调者时必须：Read 新产物路径（不凭记忆）→ 写 docket.yaml → validate → emit_tracker。

### 2.4 机器可读输出前缀

所有工具脚本输出统一前缀：`DOCKET_DIR:` / `DOCKET_OK:` / `DOCKET_ERROR:` / `EPUB_HITS_JSON:` / `APPLICATION_GATE:`

判读铁律：**stderr 有字 ≠ 失败。以退出码 0 + 机读前缀为准**（Windows PowerShell 会把 stderr 标成 NativeCommandError）。

### 2.5 轮次治理

max_rounds=3（config.yaml），每"分诊→派工→再核"计 1 轮，第 3 轮后必须停。三个终态保证流程**永远有出口**：terminal_complete / terminal_max_rounds / terminal_blocked。

### 2.6 门禁与默认值设计

- intake Q2 默认规则（硬性）：未显式指定专利类型 → 统一默认"发明"并写明"（默认）"
- 发明人/申请人缺失 → 文头写"待填写"，**blocking: false 不卡流程**——分清"事实缺口"（问人）与"文头占位"（不阻塞）
- 申请文件门禁：缺 schema/线稿/交底书则停，引导先补交底
- 内容争议 → 写入问题清单，**不阻塞主文件**

---

## 三、可借鉴模式（三档判定）

| 模式 | 说明 | 新颖性 | 判定 | 落实方式 |
|------|------|--------|------|---------|
| YAML 状态机+validator | phase 跳转机器校验 | 我们无对应物（delegate_task 无状态机） | ① 有利进化 | ✅ 已沉淀 orchestrator-handoff-pattern skill |
| 路径交接合同 | 跨包只传路径禁传摘要 | AGENTS.md"上下文一次性写透"同构，但禁止清单更细 | ① 有利进化 | ✅ 并入同一 skill |
| 轮次上限+三终态 | max_rounds=3 防死循环 | delegate_task 无 retry 上限 | ① 有利进化 | ✅ 并入同一 skill |
| 机读前缀判读 | stderr≠失败，退出码+前缀为准 | 我们已有类似意识但未成文 | ② 备用 | 已写入 skill 常见坑 |
| 显式触发词白名单 | 防自动滑包 | 与笔记指令语义互补 | ② 备用 | skill 常见坑节 |
| Skill 带 pytest | 每子包含 tests/ | skill-stress-test 已有，但静态单测更轻 | ② 备用 | 记忆即可 |
| CNIPA EPUB 爬虫+过 WAF browser.py | 国知局检索工程 | 用户领域直接可用 | ① 有利进化 | 本地副本已存 |
| 工具各包自带副本（禁跨包调用） | browser.py/md_to_docx.py 每包一份 | 反 DRY 但换来包自治 | ③ 知识 | 只记笔记 |
| Obsidian vault 通俗解读 | 专利知识库+图谱 | 与 rag-index-rebuild 思路相通 | ③ 知识 | 只记笔记 |

**不借鉴**：工具副本模式（虽然防了跨包耦合，但对我们是维护负担——我们的 skill 生态共享 tools 更合理）。

---

## 四、与 Hermes 体系的映射与差距

| patent-docket 概念 | Hermes 对应物 | 差距 |
|---|---|---|
| docket.yaml 状态机 | harness-checkpoint（检查点快照） | checkpoint 无 transition 校验 |
| handoff_contract | AGENTS.md"上下文一次性写透" | 我们有原则无合同格式 |
| validate_docket.py | 质量门禁机械化（AGENTS.md 准则 3） | 已对齐 |
| TRACKER.md | PROGRESS.md | 我们手搓，人家脚本生成——**可改进点** |
| max_rounds=3 | 无 | **delegate_task 缺 retry 上限，可补强** |
| 机读前缀 | 无成文规范 | **可成文** |

---

## 五、局限性

1. **专利知识深度未验证**：本笔记聚焦架构精读，CNIPA 检索/交底模板/审查答复的领域正确性未实测（需要真实案件验证）
2. **Playwright 依赖**：CNIPA 爬虫和 mermaid 渲染依赖 Playwright，Jetson 上需要额外安装
3. **单 agent 设计的代价**：patent-docket 刻意不开子进程，长流程全靠单上下文推进——超长案件可能撞 context 上限（它用"只 Read 对应 phase 的 prompt"缓解，按需加载）
4. **examples 未跑通**：三个示例目录是静态材料，未实际执行全流程验证

## 出处标注

| 章节 | 来源类型 |
|------|---------|
| 一、二 | **仓库源码精读**（本地 clone 逐文件读） |
| 三 | **判定+落实**（三档判定标准来自 repo-absorption skill） |
| 四 | 扩展分析 |
| 五 | 局限性 |


## 相关笔记

- [SKILL.state长程Agent状态架构](./2026-09-01-SKILL.state长程Agent状态架构-16倍Token削减与准确率反升.md) — 状态机+路径交接同族
- [Agent记忆离线整理-AutoDreamer](./2026-09-10-Agent记忆离线整理-AutoDreamer区域重写与SleepTimeCompute精读.md) — Agent 架构设计对照
