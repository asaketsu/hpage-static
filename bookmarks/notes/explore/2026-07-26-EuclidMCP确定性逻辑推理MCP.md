# Euclid-MCP：通过 Prolog 实现确定性逻辑推理的 MCP Server

> **来源**：arXiv 2026
> **原文链接**：https://arxiv.org/abs/2607.21412
> **作者**：Bartolomeo Bogliolo
> **记录日期**：2026-07-26

**标签**：#MCP #逻辑推理 #Prolog #神经符号AI #确定性推理 #工具调用 #规则引擎

---

## 一、内容详细整理

### 1.1 核心问题：LLM 推理的不可靠性

LLM 在自然语言理解和生成方面表现出色，但在多步逻辑推理上存在系统性缺陷：

- 非确定性输出：同一问题多次询问可能得到不同答案
- 幻觉倾向：在事实无法验证时编造看似合理但错误的结论
- 缺乏可审计性：无法提供形式化的推理证明链

这些问题在安全关键域（security-critical）和合规敏感域（compliance-sensitive）尤为致命——这些场景要求决策既正确又可解释。

### 1.2 RAG 的根本性错配

论文的核心论点之一：**语义 RAG 是规则执行的错误工具**。

RAG 流程的工作原理是：将用户查询嵌入向量空间 → 通过近似最近邻搜索检索相似文档 → LLM 基于检索上下文生成答案。这在开放式问答中有效，但在规则密集型任务中存在根本性错配：

- 正确性依赖逻辑推导，而非文本相似度
- 检索的规则子集必须逻辑完备且一致，向量检索无法保证
- 审计和可解释性需要形式化证明，而非"模型看到了类似规则"

> 论文用了一个精准比喻："用钻头钉钉子"（using a drill to hammer a nail）——工具很强大，但底层操作（近似匹配 vs 逻辑推理）与任务不匹配。

### 1.3 Euclid-MCP 架构设计

Euclid-MCP 采用混合认知架构：LLM 负责描述世界（生成事实和规则），确定性推理引擎负责执行推理。

三层核心组件：

1. **LLM 客户端** — 任何支持 MCP 的 LLM 应用，负责解析自然语言输入、生成 Euclid-IR 知识库、调用推理工具、渲染结果
2. **Euclid-MCP Server** — Python 进程（基于 FastMCP），包含 Euclid-IR 解析器、Prolog 编译层、安全沙箱
3. **推理后端** — SWI-Prolog 作为确定性推理引擎，通过子进程调用执行推理

> 关键设计决策：LLM 永远不需要在内部执行多步逻辑推理，只需描述问题并解读结果。所有推导委托给推理后端，保证逻辑正确性。

### 1.4 Euclid-IR：引擎无关的中间表示

Euclid-IR 是 Euclid-MCP 的核心抽象——一种声明式逻辑推理语言，设计目标：

- 可读性 — 语法优化为人类和 LLM 均可理解
- 最小化 — 仅包含 Horn 子句逻辑的必要构造
- 确定性 — 每个查询有有限的、可追踪的证明
- 后端无关 — 今天编译到 Prolog，明天可编译到 Datalog/SMT/自定义规则引擎

知识库由四种元素构成：
- **事实（Facts）** — `parent(tom, bob)`, `active(user_42)`
- **规则（Rules）** — `mortal($x) IF human($x)`
- **查询（Queries）** — `? mortal(socrates)`
- **闭世界否定** — `blocked($user) IF NOT active($user)`

变量以 `$` 前缀标识（`$x`, `$who`），在编译时转换为 Prolog 的大写变量。支持算术比较（`>`, `>=`, `=<`, `=:=`）和多行规则（以 `IF` 或 `AND` 结尾时自动续行）。

### 1.5 四个 MCP 工具：translate-run-inspect-repair 循环

Euclid-MCP 暴露四个无状态 MCP 工具，构成完整的推理调试循环：

**reason** — 主推理工具
- 输入：Euclid-IR 知识库文本，可选查询覆盖，max_solutions=5，max_depth=30
- 输出：解列表，每个解含变量绑定和证明树（节点类型：fact/rule/and）
- 用途：执行推导，返回带完整证明链的答案

**diagnose** — 诊断分析工具
- 输入：知识库 + 查询 + mode（why / why_not / what_needs）
- 输出：DiagnosisResult（holds 布尔值、findings 列表、人类可读结论、可选证明树）
- 三种模式：
  - `why` — 解释查询为何成立（或不成立）
  - `why_not` — 解释查询为何失败（缺失哪些事实/规则）
  - `what_needs` — 建议需要添加什么才能使假查询变真

**what_if** — 场景分析工具
- 输入：base_knowledge + modifications（`+` 添加、`-` 删除事实）+ query
- 输出：WhatIfResult（before_count, after_count, delta, 前后解列表、影响结论）
- 用途：假设性变更的影响分析，支持策略设计和角色工程

**check_kb** — 知识库验证器
- 输入：Euclid-IR 文本
- 输出：KBCheckResult（valid 布尔值、errors、warnings、facts_count、rules_count、predicates_count）
- 用途：推理前检查语法错误、未定义谓词、循环规则、重复项

六步循环：Validate → Translate → Run → Inspect → Repair → Explore

> 错误以可读文本返回，符合 MCP 最佳实践，LLM 可将其作为自我修正的反馈。

### 1.6 IT 安全合规用例

论文构建了一个真实的云环境安全合规模型（代码开源在 GitHub），三层知识库结构：

第一层 - Standards（外部标准）：CIS AWS 基础基准，覆盖账户管理、S3、CloudTrail、网络、GuardDuty 等控制项，按严重程度分级（critical/high/medium/low）

第二层 - Policies（内部策略）：角色层级（intern → junior_dev → ... → cto，含运维/安全/产品角色线）、环境分层（production/golden/staging/development/sandbox）、数据分类（public/internal/confidential/secret）、访问控制规则

第三层 - Data（具体数据）：30 用户（小版本）或 200 用户（大版本），50-300 资源（EC2/S3/RDS/KMS/Lambda 等），含部门、角色、权限、MFA 状态、登录时间等属性

代表性查询：
- Q1 单跳权限检查：`? user_has_permission(user_0005, manage_servers)` — 通过角色层级验证
- Q2 多跳策略推理：`? can_deploy($who, production)` — 生产环境要求 level≥6 + deploy_code 权限
- Q6 跨策略违规：`? violates_separation_of_duties($who)` — 同时拥有 deploy_code + approve_deploy
- Q7 资源审计：`? production 中哪些资源未加密`

### 1.7 实验评估结果

两组对照实验，三个条件：A=llama3.1:8B（本地小模型）、B=qwen3-coder:480B-cloud（云端大模型）、C=llama3.1:8B + Euclid-MCP

小规模基准（5-15 事实，系谱/分类/RBAC 五题）：
- A、B、C 三者准确率均为 5/5
- Euclid-MCP 在小规模无优势，输入 token 略高（254 vs 131）

大规模 RBAC 基准（1000 合成用户，1053 事实）：
- A（8B）：2/5 准确率，平均 6966ms，输出 165 token
- B（480B 云端）：2/5 准确率，平均 3695ms，输出 212 token
- **C（8B+Euclid）：5/5 完全准确，平均 963ms，输出仅 12 token**

> 关键发现：在 1000+ 事实规模下，无论 8B 还是 480B 的 LLM 都系统性幻觉——计数错误、遗漏显式事实。Euclid-MCP 每次都给出精确答案，同时更快（963ms vs 6966ms）、更省 token（12 vs 165），因为 LLM 只生成简单查询而非冗长的错误推理。

### 1.8 共享推理基底的愿景

论文提出 Euclid-MCP 作为 Agent 的"稳定共享推理基底"（stable reasoning substrate）：

解决的问题：每个新合规问题可能导致不同的 agent 用不同的程序编码，同一个策略产生不一致解释，最终积累成难以审计的临时实现。

解决方案：外部化规则知识到单一规范表示（Euclid-IR），实现四个特性：
- **Shared** — 所有 agent 查询相同的策略定义
- **Stable** — 策略只在知识库更新时变化，不因新 agent 部署而改变
- **Auditable** — 每个决策可追溯到具体规则和事实
- **Reusable** — 同一知识库支持访问审查、部署审批、事件响应、合规报告

## 二、查询拓展

### 2.1 Model Context Protocol (MCP)

MCP 是 Anthropic 提出的标准化协议，让 LLM 应用以统一方式发现和调用外部工具/数据源。Euclid-MCP 将逻辑推理引擎作为 MCP 工具暴露，任何 MCP 客户端（Claude Desktop、Cursor、OpenCode 等）均可直接使用，无需 bespoke 集成。这与 Hermes Agent 的 MCP 原生客户端架构直接相关——native-mcp skill 支持在 config.yaml 中配置 MCP server 实现自动工具发现。

### 2.2 Horn 子句与 Prolog 推理

Horn 子句是至多一个正文字的析取式，形式为 `head IF body1 AND body2 AND ...`，是逻辑编程的理论基础。Prolog 的回溯搜索 + 统一（unification）机制自动从事实和规则推导结论。Euclid-IR 将 Horn 子句包装为人类可读语法（`IF`/`AND`/`NOT` 关键词，`$` 变量前缀），降低 LLM 生成正确逻辑编码的难度。

### 2.3 神经符号 AI (Neuro-Symbolic AI)

将神经模型的模式识别能力与符号方法（逻辑推理、结构化知识）结合。常见模式：LLM 解析自然语言生成结构化表示 → 符号引擎保证正确性和可解释性。论文引用了基于 SMT 的金融合规分析、LLM+Prolog 的推理增强等工作。

### 2.4 SWI-Prolog

SWI-Prolog 是 Prolog 语言的成熟开源实现，广泛用于知识表示和逻辑编程。Euclid-MCP 通过子进程调用 `swipl` 二进制，将 Euclid-IR 编译为自包含 Prolog 程序写入临时 `.pl` 文件执行，捕获 JSON 格式的解和证明树，执行后清理临时文件。这种方式无需编译扩展或持久 Prolog 进程，优先保证简单性和可移植性。

## 三、归纳总结

### 3.1 确定性推理 vs 神经推理的能力边界

```
                    小规模 (<100 事实)        大规模 (≥1000 事实)
                    ┌─────────────────┐       ┌─────────────────┐
  LLM-only          │ ✓ 准确率相当     │       │ ✗ 系统性幻觉     │
                    │ ✓ 速度快         │       │ ✗ 计数/交集错误  │
                    │ △ 成本低         │       │ ✗ 不可审计       │
                    └─────────────────┘       └─────────────────┘
                    ┌─────────────────┐       ┌─────────────────┐
  LLM + Euclid-MCP  │ ✓ 准确率相当     │       │ ✓ 精确推导       │
                    │ △ 输入token略高  │       │ ✓ 更快更省token  │
                    │ ✓ 可审计证明     │       │ ✓ 完整证明树     │
                    └─────────────────┘       └─────────────────┘
```

核心结论：**Euclid-MCP 的价值随知识库规模增长而急剧上升**。小规模时确定性引擎的开销不划算；大规模时 LLM 必然幻觉而确定性推理保证精确。

### 3.2 translate-run-inspect-repair 工具设计模式

这是论文对 MCP 工具设计的最佳实践贡献——不是暴露一个大而全的推理接口，而是分解为四个正交工具：

- **check_kb（验证）**：推理前确保知识库结构正确
- **reason（执行）**：核心推导 + 证明树
- **diagnose（诊断）**：结果异常时的归因分析
- **what_if（探索）**：策略变更的假设性影响

这种分离使 LLM 能在工具调用层面进行自我修正循环——run 失败 → inspect 原因 → repair 知识库 → re-run，比单一黑盒接口的调试效率高得多。

### 3.3 三个基线对比维度

对比 LLM-only 与 LLM+Euclid-MCP 的量化差异：

- **准确率**：大规模下 2/5 vs 5/5（8B 和 480B LLM 均失败）
- **延迟**：大规模下 6966ms vs 963ms（7.2 倍加速）
- **token 效率**：大规模下 165 输出 token vs 12 输出 token（13.8 倍效率）
- **可解释性**：无证明 vs 完整证明树
- **可审计性**：不可重现 vs 可追溯到具体规则

## 四、趋势判断

### 趋势1：MCP 工具从"数据检索"向"确定性计算"扩展

当前 MCP 生态以数据检索和 API 调用为主（数据库、文件系统、搜索）。Euclid-MCP 展示了将确定性推理引擎作为 MCP 工具的范式。未来会看到更多形式化引擎（SMT solver、约束求解器、定理证明器）通过 MCP 标准化暴露给 LLM。依据：论文明确将 Euclid-IR 设计为后端无关，今天 Prolog，明天可换 Datalog/SMT。

### 趋势2：规则引擎在 LLM Agent 中的回归

论文指出 Agent 生成程序解决合规问题的模式会导致策略编码碎片化（每个 agent 不同实现）。将规则外部化到共享知识库，是 expert system 传统在 LLM 时代的回归。这与 Hermes Agent 的 Skill 体系（规则外部化到 SKILL.md 而非硬编码在 prompt 中）理念一致。

### 趋势3：混合架构成为安全关键域标配

论文结论明确：RAG 适合开放式查询和文档检索，确定性推理适合策略执行和合规检查，两者互补。未来安全合规类 LLM 应用的标准架构将是"RAG 检索策略 → 确定性引擎验证合规"的混合模式。

## 五、关联分析

### 5.1 与 Hermes Agent MCP 架构的关联

Hermes Agent 的 native-mcp skill 支持在 config.yaml 中配置 MCP server。Euclid-MCP 可以直接作为 Hermes 的 MCP server 添加——`pip install euclid-mcp` 后配置 stdio 传输，Hermes 自动发现四个推理工具。特别适合 Hermes 的安全策略验证场景（如 cron job 权限检查、工具调用权限矩阵验证）。

### 5.2 与 Binding Drift (2607.18316) 的关联

Binding Drift 论文分析了多步 Agent 的实体绑定漂移问题——随步骤增加，参数绑定错误累积传播。Euclid-MCP 通过将关键推理委托给确定性引擎，从架构层面消除了这类错误——Prolog 推理不存在"漂移"，每次执行结果完全确定。两者从不同角度解决 Agent 可靠性问题。

### 5.3 与 SlotGuard (2607.17147) 的关联

SlotGuard 关注 Agent 转录本的隐私边界（类型化槽位 + 合成替换）。Euclid-MCP 的安全合规用例（IT 安全策略验证）与 SlotGuard 的隐私保护形成互补——前者保证推理正确性，后者保证数据隐私。在合规审计场景中，两者可组合使用。

### 5.4 与 Beyond the Leaderboard (2607.05775) 的关联

Beyond the Leaderboard 定义了 LLM Agent 六大失败模式分类法。Euclid-MCP 直接解决了其中"工具参数编造"和"多步推理幻觉"两类——通过确定性引擎消除了推理过程中的幻觉可能性。

## 六、金句摘录

> "语义搜索行为就像用钻头钉钉子：工具很强大，但底层操作与任务不匹配。"

> "当事实适合 LLM 上下文窗口且推理链浅时，LLM 独自就够了。当不适合时——超过几百个事实——任何大小的确定性推理都至关重要。"

> "Euclid-MCP 不是 agent 的替代品；它是 agent 在需要规则问题的确定性答案时通过 MCP 调用的共享策略引擎。"

## 七、行动启示

- 启示：将确定性推理工具作为 MCP server 集成到 Hermes，解决规则密集型任务的幻觉问题
- 行动：评估 `pip install euclid-mcp` 可行性，在 Hermes config.yaml 中配置为 MCP server

- 启示：translate-run-inspect-repair 四工具分离模式可应用于 Hermes 工具设计
- 行动：对复杂的 Skill 执行流程，考虑拆分为 check/execute/diagnose/explore 四阶段

- 启示：大规模知识库（>1000 事实）是确定性推理的关键价值区
- 行动：审计 Hermes Skill 库规模，超过阈值时考虑引入确定性推理层


## 相关笔记

- [ACM上下文管理五原语](./2026-07-24-ACM上下文管理五原语.md) — MCP 工具调用与上下文管理的工程化交汇
- [BindingDrift-多步Agent实体绑定漂移](./2026-07-23-BindingDrift-多步Agent实体绑定漂移.md) — 确定性推理可缓解多步 Agent 的实体漂移
- [SupraCognitiveModes-Agent记忆路由架构](./2026-07-22-SupraCognitiveModes-Agent记忆路由架构.md) — 符号推理层与认知模式的互补架构
