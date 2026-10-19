# 网络安全: Execution Provenance（2026-08-15 增量更新）

> 嗅探学习 | 2026-08-15 | 兴趣等级 L3 | 来源: web_search + GitHub awesome-auditable-ai
> 前序笔记: [ProvenanceGuard: MCP-Based LLM Agents 的源感知事实性验证](2026-06-18-ProvenanceGuard.md)

## 摘要

本次为 58 天后的增量追踪。2026-06-18 的前序笔记聚焦**内容溯源**（claim-to-source 归因验证，ProvenanceGuard 8 阶段管道）；过去两个月领域重心已明确转向**执行溯源**（execution provenance）：记录 Agent"做了什么、为什么、依据什么授权"的运行时谱系，用于安全约束与合规审计。标志性进展：专项 survey 落地、Agent-Sentry 用合法运行谱系做运行时边界约束、MemLineage 把 Merkle 日志签名引入记忆层防投毒、OpenKedge 定义意图-执行证据链协议。监管侧 EU AI Act 已于 2026-08-02 全面执行（72 小时事件报告窗口）。

## 关键发现（增量）

### 1. 领域有了专属 survey 和 awesome 清单 — "Execution Provenance" 正式成为学科术语

- **From Agent Traces to Trust: A Survey of Evidence Tracing and Execution Provenance in LLM Agents**（arXiv 2606.04990）：组织 trace sources / evidence units / lineage relations 三层结构，服务 process-level accountability
- **awesome-auditable-ai**（USC Yue Zhao 维护，PyOD 作者）：183 条目 = 129 篇 arXiv + 84 个仓库 + 16 个标准，把审计性与可靠性工程统一到一个清单。核心论断："Agent capability is rising much faster than agent reliability"

### 2. Agent-Sentry：执行谱系从"事后审计"升级为"运行时约束"

arXiv 2603.22868。记录先前合法运行的执行谱系（execution lineage），运行时用它**界定和约束** Agent 后续行动——超出历史合法谱系的动作被拦截。这是 provenance 的安全用法转向：不再只是出事后取证，而是事前预防（preventative, execution-bound enforcement）。

### 3. MemLineage：Merkle 日志 + 谱系强制，记忆投毒攻击成功率归零

arXiv 2605.14421。每条记忆条目按 principal 用 RFC 6962 Merkle 日志签名；**当敏感动作的 justification 链追溯到外部内容时拒绝执行**。三个记忆投毒 workload + 六个 AgentDojo banking 对上攻击成功率归零，开销亚毫秒。直接回应了 Memory Poisoning 关键词（兴趣表同组关键词）。

### 4. OpenKedge 协议 + Asqav SDK：意图-执行证据链（IEEC）工业化

- **OpenKedge**（arXiv 2604.08601）：三段式——声明式意图提案（不直接调 API）→ 批准后编译为执行契约（限定动作/资源/时间窗 + 临时任务身份）→ 五要素密码学链接证据链（意图、上下文评估、策略决策、执行边界、结果）
- **Asqav**（开源 SDK）：每动作量子安全 ML-DSA-65 签名 + hash 链接，篡改即断链；多方签名要求关键操作最低审批数

### 5. 软件供应链安全标准被系统性移植到 Agent 审计

in-toto attestation（签名声明绑定 artifact 与操作）、SLSA（分级 provenance 要求）、DSSE（签名信封）、Rekor（append-only Merkle 透明日志）、Certificate Transparency——这些供应链安全基础设施正被 Agent 审计链复用。跨域迁移模式：**成熟密码学骨架 + Agent 语义载荷**。

### 6. 证据质量决定归因精度（数据支撑）

- Who&When（ICML 2025）：最强方法仅 53.5% 定位责任 Agent、14.2% 定位关键错误步
- TraceElephant（ACL 2026）：完整执行 trace 使步级归因准确率 17%→30%（相对提升 76%）
- AgenTracer（ICLR 2026）、StepFinder（KDD 2026，推理时间降 79%）持续在 Who&When 上刷新

### 7. 行业基线数据（CSA/RSAC + Kiteworks 2026）

- 68% 组织事后无法区分动作来自人类还是 AI Agent
- 33% 完全缺乏证据级审计链；61% 基础设施碎片化无法产出可用证据
- 88% 已经历过 AI Agent 安全事件；97% 预期 12 个月内再发重大事件
- EU AI Act 2026-08-02 全面执行：高风险系统需合规评估 + 72 小时事件报告 → 无审计链 = 无法合规

## 对工作的价值

- **P1 — Hermes 可观测性升级方向**：evolution-log.jsonl / observability-dashboard 可借鉴 in-toto 式结构——每个动作记录 `(intent, policy_decision, execution_boundary, outcome)` 四元组，而非裸事件流。当前日志回答"发生了什么"，缺"为什么 + 依据什么授权"
- **P1 — 记忆系统防御**：MemLineage 的"justification 谱系追溯"模式可直接用于 MEMORY 写入策略——外部内容（网页/工具输出）派生的结论标记 provenance，敏感动作（生产部署/文件删除）触发谱系检查
- **P2 — agent-security-governance / auto-defense-check skill 增强**：awesome-auditable-ai 的 16 个标准（in-toto/SLSA/DSSE/Rekor）是现成的合规检查项来源
- **P2 — 量化 Agent 场景**：交易决策的执行谱系（信号来源→策略规则→风控检查→下单）即 OpenKedge IEEC 的天然应用

## 行动建议

1. 把 `(intent, decision, boundary, outcome)` 四元组加入 evolution-log.jsonl schema（P1，一次 patch）
2. MemLineage 模式评估写入 memory-write skill：外部内容派生记忆打 provenance 标记（P2）
3. 保持关注：Agent-Sentry 后续开源（当前无 code 链接）、Asqav SDK 生产可用性（P3）

## 关键风险与盲点

- Agent-Sentry / MemLineage / OpenKedge 均为 2026 Preprint，无第三方生产级复现（社区验证级别：仅作者实验）
- awesome-auditable-ai 星数仅 73，清单权威性依赖维护者信誉（USC FORTIS 实验室，PyOD 作者背书）
- 68%/97% 等统计来自厂商资助调研（CSA/RSAC、Kiteworks、AGAT），存在夸大动机，采信时降权

## 一页速查

> **Execution Provenance = Agent 版的飞行黑匣子 + 供应链 attestation**
> 核心公式：意图 → 策略决策 → 执行边界 → 结果，四要素密码学串联
> 三条路线：运行时约束（Agent-Sentry）/ 记忆谱系（MemLineage）/ 协议化（OpenKedge+Asqav）
> 密码学骨架：Merkle 日志（RFC 6962）+ DSSE 签名信封 + hash 链
> 监管死线：EU AI Act 2026-08-02 已生效，72h 事件报告
> 关键数据：完整 trace 使归因准确率 +76% 相对提升；68% 组织分不清人/Agent 动作

## 待深入

- Agent-Sentry 的"合法谱系"如何防止投毒（合法运行本身被污染怎么办）
- TraceElephant 基准复跑成本（Jetson Orin 上 LLM-based 归因器可行性）
- OpenKedge 执行契约的临时身份（ephemeral identity）与现有 PAM 体系集成

## 参考来源（增量）

1. awesome-auditable-ai — github.com/yzhao062/awesome-auditable-ai（2026-08-15 提取）
2. From Agent Traces to Trust survey — arxiv.org/abs/2606.04990
3. Agent-Sentry — arxiv.org/abs/2603.22868
4. MemLineage — arxiv.org/abs/2605.14421
5. OpenKedge / TierZero 分析文 — arxiv.org/abs/2604.08601 + tierzero.ai/blog/ai-agent-audit-trail
6. Who&When — arxiv.org/abs/2505.00212；TraceElephant — arxiv.org/abs/2604.22708
7. CSA/RSAC 2026 / Kiteworks 2026 统计（转引自 tierzero.ai）

## 相关笔记

- [ProvenanceGuard: MCP-Based LLM Agents 的源感知事实性验证](2026-06-18-ProvenanceGuard.md)（前序，内容溯源方向）
- [网络安全-OWASP-AI-Agent-Security-Top-10](2026-08-12-网络安全-OWASP-AI-Agent-Security-Top-10.md)
- [AI-Agent记忆系统2026](../2026-07-28-AI-Agent记忆系统2026-从对话缓冲到制度化知识.md)
