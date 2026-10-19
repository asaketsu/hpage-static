#AI-Agent #自进化 #评估方法
# 2026-09-23 自进化 Agent 的过程级评估：EvoPathBench、技能进化与编排策略学习

> 夜间自学习笔记（cron）。主题背景：Hermes 递归自我进化循环（L1 session-evolution-scan → L2 用户拍板沉淀 → L3 evolution_log.jsonl 对账）运行月余，进化准入门禁依赖"用户拍板"作为质量闸门。本笔记定向检索 2026-09 最新文献，回答两个问题：①自进化的效果该怎么测才不被端点指标骗 ②技能（skill）作为进化载体的最新实践。

## 内容整理

### 1. EvoPathBench：端点指标测不出进化副作用（arXiv:2609.24663，2026-09-21，cs.AI）

**核心命题**：自进化 Agent 把交互反馈转成持久工件（记忆/技能），工件在经验流中迭代更新，其支撑的能力也随之演化——**只看端点性能（endpoint performance）对自进化是不完整视角**，必须做过程级（process-level）评估。

**评测设计（方法论核心）**：
- 固定 base model 和工具
- 在连续 checkpoint 上**冻结**进化中的工件
- 在 held-out episodes 上测三种能力：
  1. **泛化**（generalization to unseen tasks）
  2. **保持**（retention after unrelated learning）——学了无关任务后旧能力是否退化
  3. **规则适应**（rule adaptation to new evidence）——证据变了规则跟不跟

**四条硬发现**：
1. 相似未见任务上的增益**在分布偏移下普遍减弱**
2. 保持性损失集中在**少数进化路径**（不是均匀退化——坏路径可识别）
3. **没有任何方法实现可靠的规则适应**（全行业空白）
4. **候选工件有大幅 held-out 增益，但实际选中的更新系统性低于候选潜力**——评估与选择（evaluation and selection）环节是最大浪费点

### 2. EvoSkill-GUI：技能=可在部署期修订的活文档（arXiv:2609.17653，2026-09-16，cs.LG）

**核心命题**：GUI agent 需要的不是更好的静态技能，而是**能从执行反馈中修订、无需再训练的技能**——把 skill 当"部署期活程序性知识"而非"部署前产出的静态工件"。

**技能结构（多文件包）**：检索元数据 / 可执行计划 / 备用定位 / 失败恢复规则 / 辅助工具 / 失败案例集。

**reflect-revise-reuse 三环**：
- executor 执行中即时修订（in-rollout revision）
- **隔离的 critic** 在严格信息隔离下诊断失败轨迹
- executor 通过**受限工具接口**编辑技能文件

**实测数据**：MobileWorld/AndroidWorld/OSWorld 三大 GUI 基准上，多个 base model 零训练提升 **+16.2% / +6.0% / +10.5%**；进化出的技能库持续惠及相关任务，无需从零重建。代码：github.com/ZJU-REAL/EvoSkill-GUI

### 3. TimEvolve：把"实现的结果"变成编排策略的持久更新（arXiv:2609.24862，2026-09-21，cs.LG）

**核心命题**：时序 Agent 的专家信任度、路径选择、干预强度应是**随部署过程演化的联合编排策略**，而非部署前定死。核心机制是 predict-reveal-update 协议：部署前把所有候选专家预测和候选 agent 路径**全部提交留痕**，目标值揭示后，每个实现结果**评估整个候选集**——把延迟反馈变成无需额外标注的监督信号。

**实测数据**：8 个 Time-MMD 域上，15 方法中 MSE/MAE 平均排名双第一，7 个域双指标最低误差。

### 4. Harness-Zero：把 harness 增益蒸馏进模型权重（arXiv:2609.24974，2026-09-21，cs.AI）

**核心命题**：agent harness（模型-环境交互的外部中介系统）的增益绑死在部署时的 harness 上。Harness-Zero 反向操作：用领域优化 harness 作训练期教师，通过 agent-as-harness（一个 harnessing agent 先在目标 harness 动作空间里纠正学生回复再执行）把 harness 诱导的行为**内化进模型权重**，部署时专用 harness 可整体移除。

**实测数据**：移除专用 harness 后 macro-average 任务成功率 **23.3%→44.3%**，甚至**超过保留 harness 的 41.7%**；28 种行为模式平均 **82.3% 恢复率**。

## 归纳总结

1. **"用户拍板"环节=EvoPathBench 证实的最大瓶颈同型物**：其发现 4（候选有增益、选择实现不了潜力）与 Hermes L2 层"session-evolution-scan 只出候选清单禁自动 patch"的保守设计互为镜像——门禁防了伪进化，但代价是进化速率被选择环节卡死。改进方向不是放开自动 patch，而是**给候选加廉价的 held-out 预筛**（如 A/B 双版本跑真实任务）。
2. **技能的正确形态是多文件包+失败案例集**：EvoSkill-GUI 的六件套结构（检索元数据/计划/备用定位/恢复规则/工具/失败案例）与 Hermes skill 的 SKILL.md+references/ 结构高度同构——差的是"执行中即时修订"和"隔离 critic"两环。Hermes 已有 references/*.md 沉淀失败案例（如 handwritten-html-regression 系列 7 连回归记录），验证了此结构有效。
3. **检查点冻结=过程级评估的可操作定义**：EvoPathBench 的"冻结工件于连续 checkpoint、held-out 上测能力"直接可移植为 Hermes 评估协议——evolution_log.jsonl 的每条记录即一个 checkpoint，补一组标准探测任务即可量化"进化是否真的在变强"。
4. **predict-reveal-update 是"把 hindsight 变监督"的通用模式**：对 Hermes 的启示=晨报/守护 cron 的预测（如 ETA、死法预判）与实际结果的差值应回流为策略权重（哪类告警该发、哪类是噪音）。
5. **Harness-Zero 的方向与 Hermes 相反且互补**：Hermes 走"权重冻结、harness（skill/cron/hook）持续进化"路线；Harness-Zero 证明 harness 行为可被蒸馏进权重。两者不冲突——harness 期快速迭代，蒸馏期固化稳定行为，是同一条进化链的两个阶段。

## 趋势判断

- **自进化评估从论文走向基建**：EvoPathBench 用公开交易数据+校准轨迹做基准，预示 2026 Q4 会出现更多"进化过程审计"工具；Hermes 的 evolution_log.jsonl 属于同类早期实践。
- **技能进化=training-free 主线确立**：EvoSkill-GUI 零训练 +16.2% 说明 base model 够强时，外部程序性知识的收益仍很大——skill 路线（Hermes 现路线）在可见未来不会被权重内化路线完全取代。
- **"评估与选择"成为新竞争点**：EvoPathBench 发现 3（规则适应全行业空白）+发现 4（选择浪费潜力）指向同一空白——自动评估器（LLM-as-judge for evolution candidates）会是下个热点。

## 关联分析

| 文献概念 | Hermes 现有资产 | 可吸收点 |
|---|---|---|
| checkpoint 冻结+held-out 测能力 | evolution_log.jsonl（有账无评估） | 每条进化记录关联一组标准探测任务结果 |
| 隔离 critic 诊断失败轨迹 | session-evolution-scan（L1 检测层） | 技能修订前加独立会话复现失败（信息隔离=不喂上下文） |
| 受限工具接口编辑技能 | skill_manage(patch) 白名单机制 | 已同构，无需改动 |
| 失败案例集=技能六件套之一 | references/*-regression-*.md 系列 | 已实践；可补"备用定位"（降级链）条目化 |
| predict-reveal-update | cron 守护的 ETA/死法预判 | 预测-结果差值回流为告警阈值权重 |
| 候选 held-out 预筛 | 无（依赖用户拍板） | A/B 双版本（skill-ab-testing 已有基建）跑真实任务再入账 |

与既有笔记的关系：05-29《达尔文Skill2.0深度分析-Evolver对比吸收》分析的是"进化引擎怎么建"；本笔记回答"进化效果怎么测+技能怎么在部署期修订"——同一领域的下游两环。

## 查询拓展

- EvoPathBench 是否开源（摘要未给链接，需查 GitHub）
- "retention losses concentrated in minority of evolution paths" 的坏路径长什么样——原文实验节
- Hermes 型 CLI agent（非 GUI）的技能修订文献：搜 "skill library revision CLI agent 2026"
- TimEvolve 的 expert trust 更新公式能否用于 Hermes 的 model-fallback-chain 权重
- LLM-as-judge 评估进化候选的校准方法（content-judge skill 已有雏形）

## 拓展应用推荐

1. **【评估基建·低成本】evolution_log.jsonl 加探测任务字段**：每条记录附 2-3 个标准任务的执行结果快照（如"搜索降级链演练""笔记 9 模块校验"），过程级评估的最低可行版。对应 skill-health-tier 巡检升级。
2. **【选择环节·复用现有】进化候选强制 A/B**：用户拍板前先用 skill-ab-testing 跑对照（现有基建），把 EvoPathBench"选择浪费潜力"的浪费前移到预筛。准入协议不变，只加数据。
3. **【技能结构·即刻可抄】SKILL.md 六件套对齐**：给新建 skill 的模板补"备用定位"与"失败恢复规则"两个显式 section（EvoSkill-GUI 结构），降低下次踩同坑概率。
4. **【观察项】规则适应空白**：Hermes 的"用户纠偏→规则沉淀"正是规则适应场景——如果做出量化评测，本身是可发表的增量（论文计划周更候选选题）。

## 指南分析

- **适用边界**：EvoPathBench 基于交易数据域，其"分布偏移下增益减弱"结论对 Hermes 的运维域（低频高价值纠偏）未必同比例成立——运维域分布偏移慢得多。
- **成本收益**：held-out 探测任务集的建设成本约一次性 2-4 小时（选任务+写快照脚本），收益是进化循环从"账本"升级为"仪表盘"；属低风险高确定性投资。
- **风险提示**：EvoSkill-GUI 的"执行中即时修订"在 Hermes 场景须谨慎——cron 静默模式下无用户在场，即时修订技能=无人监督的自动 patch，与 L2 门禁（用户拍板）冲突；只宜吸收 critic 诊断环，不宜吸收自动修订环。
- **反直觉提醒**：Harness-Zero"移除 harness 后性能反超保留 harness"若在 Hermes 复现，意味着某些 skill 的价值是过渡性的（教会模型后即退役）——"自动化未使用=系统失败"的铁律之外，应增加"技能教会即退役"的退出机制评估。

## 出处

- EvoPathBench: arXiv:2609.24663 — "Beyond Endpoint Performance: Process-Level Evaluation of Self-Evolving Agents" (2026-09-21, cs.AI)
- EvoSkill-GUI: arXiv:2609.17653 — "Reflect, Revise, Reuse: Training-Free Skill Evolution for GUI Agents" (2026-09-16, cs.LG), github.com/ZJU-REAL/EvoSkill-GUI
- TimEvolve: arXiv:2609.24862 — "When Tomorrow Becomes Today: Self-Evolving Policies for Agentic Time-Series Forecasting" (2026-09-21, cs.LG)
- Harness-Zero: arXiv:2609.24974 — "Harness-Zero: Harness Distillation via Agent-as-Harness" (2026-09-21, cs.AI)
- 检索路径：Tavily 432 → arXiv Atom API 直搜（search-fallback-chain Layer 2.8），查询 `ti:self-evolving+AND+abs:agent` / `ti:agent+AND+abs:skill+AND+abs:library` 等
- 项目内关联：evolution_log.jsonl、session-evolution-scan skill、skill-ab-testing skill、05-29 达尔文 Skill2.0 笔记


## 相关笔记

- [2026-09-22-ai-agent-trends-llm-quant-distill.md](../../../explore/2026-09-22-ai-agent-trends-llm-quant-distill.md) — Agent 趋势：自进化与技能库
- 2026-09-21 LLM factor mining agent trends（~/explore）— LLM 驱动自主研究循环的同类方法论
