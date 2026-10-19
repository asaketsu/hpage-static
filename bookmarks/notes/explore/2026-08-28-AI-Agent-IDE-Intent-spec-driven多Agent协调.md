# Intent Spec-Driven 多 Agent 协调：CIV 模式与 living spec

> 探索日期：2026-08-28 | 兴趣等级：L3 | 来源数量：2 篇精读 + 3 篇搜索佐证 | 前序：2026-07-10 自进化Agent 3×3矩阵 / 2026-08-21 多机协同SLAM（无直接前序）

## 摘要

Spec-Driven Development（SDD）从「被动文档」进化为「可执行约束」。核心范式转换：工程师的瓶颈从「写代码」转移到「协调 Agent」。Augment Intent 提出 **living spec**（活体规格）——规格随实现自动更新，向下游 Agent 传播变更；其 CIV 架构（Coordinator-Implementor-Verifier）以**两嵌套控制环**（Implementor 内层 ReAct 环 + Coordinator/Verifier 外层 plan-execute-verify-replan 环）解决多 Agent 并行编码的结构性失败（静默覆盖/上下文漂移/重复实现/级联错误/提前完成）。Peer-reviewed 基线是 EACL 2026 VeriMAP（DAG 子任务 + 每节点验证模块 + 重试预算 3 次/复规划 5 次上限）。

## 关键发现

- **CIV 三角色是行业收敛共识**：Osmani（Planner/Worker/Judge）、Composio（Orchestrator/spawned agents/CI review）、GitHub Spec Kit（Constitution→Specify→Plan→Tasks→Implement）、Anthropic（Lead/Subagent/Evaluator）角色映射一致，分歧仅在操作层：运行时 Verifier vs 人类 PR review、静态 vs 双向共享上下文、git worktree vs Docker sandbox vs 仅上下文隔离
- **五大结构性失败模式各有根因**：静默文件覆盖=执行层无写锁（git worktree 是标准补救）；上下文漂移=隔离窗口无推送机制；重复实现=无共享实现注册表；级联错误=无输出校验、信任链传播；提前完成=无共享进度状态。每个失败都映射到一个缺失的架构原语
- **重试预算 = CIV 最重要的生产配置**：VeriMAP 默认每子任务 3 次执行-验证循环 + 5 次复规划上限；校准因子 = 每轮 token 成本（40K tokens/attempt → 10 轮 = 400K）、失败形态（格式错易恢复、语义错加轮次无益但复规划有效）、任务确定性（纯代码生成可收敛，外部 API 任务未必）
- **隔离三件套**：输入隔离（每 Implementor 独立上下文，只装 Coordinator 组装的范围上下文）+ 输出隔离（结构化契约只放行声明变量）+ 文件系统隔离（git worktree 防并发写）。缺 worktree 层，前两层仍挡不住静默覆盖
- **验证分层铁律**：确定性检查（lint/type/test）先跑，昂贵 LLM 语义评审后跑；反馈质量决定重试环效果——SpecLoop（arXiv 2603.02895）证明结构化反例反馈 >> 二元 pass/fail。Verifier 误报阻塞正确工作、漏报放行 bug，需记录决策并抽样人工复核

## 对工作的价值

- **P0 — 与 Hermes kanban-workflows / agent-orchestration-pattern 直接互补**：本机 kanban 多 Agent 工作流目前缺「Verifier 独立验证」与「重试预算」两个显式机制。CIV 的 DAG 分解 + 依赖排序 + 拓扑序执行可直接迁移到 kanban-codex-lane 的拆分逻辑
- **P0 — 验证门禁制度化**：现有 verification-gate skill 是静态模板，缺「先确定性后语义」分层执行顺序与 Verifier 决策日志。VeriMAP「每个子任务自带验证模块/定义 of done」模式可升级 verification-gate
- **P1 — 上下文工程对照**：CIV 的 pull 模型（Coordinator 合并结构化输出给子节点）vs push 模型（转发全历史）的权衡，与 context-engineering-patterns 的「预算化检索」同构；Cosmos Context Engine 400K 文件语义索引 = 本机 rag-index-rebuild 的企业级参照
- **P1 — Agent 成本模型**：Implementor 可用便宜模型、Coordinator 用前沿模型的模型路由策略，支持 model-adapter / selective-proxy 的经济性论证

## 行动建议

- 读 kanban-workflows + verification-gate，评估在 kanban 编排中加「Verifier 独立子任务」角色（P0，1-2 天）
- 在 verification-gate skill 补「分层验证顺序 + Retry Budget 配置指南」小节（P0，半天）
- 给 agent-orchestration-pattern 增加 CIV 五实现对比表（P2，顺手）

## 关键风险与盲点

- CIV 有真实成本：token 消耗为单 Agent 基线 5-15x；单文件/探索性任务/弱 Coordinator 模型时反而更差（官方验证）
- living spec 的自动更新有哲学风险：规格始终反映「实际构建」而非「原始意图」时，会静默漂移成回顾性文档（specdriven.com 社区验证）
- spec 本身不可执行、不可证明满足性；Verifier 只是检查，不能形式化保证（specdriven.com 评估维度）
- 多数数据来自 Augment 官方博客 + 单社区评估站，厂商倾向性需注意（社区复现级）

## 一页速查

> **CIV 模式**：Coordinator 分解 spec 为 DAG→拓扑排序→每节点组装范围上下文→并行 Implementors 隔离执行→Verifier 对照原 spec 验证→PASS 推进 / FAIL 带结构化反馈重试（≤3 次）→超限复规划（≤5 次）或升级人工。
> **重试预算默认**：3 attempt/subtask + 5 replan cap。**验证顺序**：lint → type → test → LLM 语义评审。**隔离**：context + 结构化契约 + git worktree 三层。
> **适用边界**：3-6 个跨服务独立子任务、可 DAG 化的确定目标；单文件改动/探索性任务/d成本敏感 → 单 Agent 更快。
> **五失败模式**：静默覆盖 / 上下文漂移 / 重复实现 / 级联错误 / 提前完成——各对应一个缺失原语（锁/推送/注册表/校验/共享状态）。

## 待深入

- VeriMAP 论文全文（arXiv 2510.17109）：DAG 验证感知规划的形式化细节
- SpecLoop 反例反馈（arXiv 2603.02895）：如何把结构化反例接入现有验证管线
- GitHub Spec Kit 实操：四位一体 /speckit.specify→plan→tasks→implement 与 Hermes skill 体系映射

## 来源列表

1. Augment Code — Coordinator-Implementor-Verifier Pattern for Dev Teams（2026-04/06 更新，精读 24KB 全文）
2. SpecDriven.com — Intent by Augment Code Tool Profile（社区评估，living spec 局限分析）
3. Parallel Code — Multi-Agent Coding Tools in 2026（工具矩阵定位）
4. Augment Code — Spec-Driven AI Code Generation With Multi-Agent Systems（CIV 同步机制补充）
5. Ry Walker Research — Augment Intent（产品定位：what comes after the IDE）

## 相关笔记

- [2026-08-25-AI-Agent-IDE-Intent-SpecDriven多Agent协调](2026-08-25-AI-Agent-IDE-Intent-SpecDriven多Agent协调.md) — 同主题前序笔记
- [2026-08-28-本地模型部署-引擎场景分化矩阵](2026-08-28-本地模型部署-引擎场景分化矩阵.md) — Agent IDE 底层引擎依赖
- 2026-07-10 自进化Agent 3×3矩阵 — CIV 协调模式的历史演进背景
- hermes-dashboard-panel / project-scaffolding / writing-plans skill — 本地 IDE 类工作流

