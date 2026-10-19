# HCP：MCP 式 Agent 运行时的安全执行控制层

> **来源**：arXiv 2026.06.27
> **原文链接**：https://arxiv.org/abs/2606.29073
> **作者**：Ting Liu (SymbolicLight Research)
> **记录日期**：2026-07-01

**标签**：#MCP #Agent安全 #执行控制 #能力系统 #信息流 #审计追踪

---

## 一、内容详细整理

### 1.1 核心问题：连接 ≠ 执行

MCP（Model Context Protocol）标准化了 Agent 如何**连接**工具服务器——JSON-RPC 消息、工具元数据、传输规则、OAuth 授权指导。但连接建立之后，**执行安全**由谁负责？

论文指出一个关键缺口：

- 模型可能看到 UI 隐藏的工具描述
- 客户端可能请求用户批准，但不把批准绑定到资源级 grant
- 工具返回的内容可能被管道传输到写入、Shell、浏览器、数据库或外发操作
- 如果这些决策分散在 prompt、服务器约定和可选日志中，系统没有单一检查点

> **核心论点**：MCP 式 Agent 系统需要一个**执行控制层**（execution-control layer），在连接层之上，将 principal、resource、grant、capability、approval、handle、data-flow、audit 集中到一条运行时决策路径上。

### 1.2 HCP 运行时架构

HCP（Handle-Capability Protocol）是一个参考运行时原型，**不是** MCP 或 OAuth 的生产替代品。它在 Agent 意图和 Provider 执行之间插入一个运行时对象模型：

```
MCP 连接层：Host/Client ←JSON-RPC→ Server tools
                    ↓
HCP 控制层：Principal intent → Runtime Broker → Vault/Audit
                    ↓
Provider 执行：canonical resources → capability effects → outputs
```

**运行时对象词汇表**：

- **Principal**：调用者（用户或 Agent 身份）
- **Resource**：稳定的 provider 规范化对象（文件、外部服务目标）
- **Grant**：将 principal 链接到 scopes、resources、capabilities
- **Capability**：provider 声明的操作（含效果、必需 scopes、资源解析行为、可选审批要求）
- **Policy Decision**：运行时的 allow/deny 判断
- **Handle**：vault 中对输出数据的引用（绑定 principal、capability、resource、task）
- **DataPipe**：从源 handle 到目标 capability 的数据移动（需双向授权）
- **Audit Entry**：策略决策、handle 访问、pipe 尝试、撤销的可追溯记录

### 1.3 八条安全不变量

论文定义了 8 条 MCP 式 Agent 执行的安全不变量：

- **I1 — 元数据非权威**：工具描述和 prompt 不能授予权限或覆盖策略
- **I2 — 审批不能绕过 Grant**：高风险操作需要同时有匹配的 grant 和审批
- **I3 — 调用者资源不能覆盖 Provider 规范化资源**：策略使用 provider 解析的资源
- **I4 — Principal 绑定到 grant、task、handle、audit**：错误主体不能调用或检查他人 handle
- **I5 — 作用域化能力调用需 Grant 支撑**：必需 scopes 触发 principal/resource/capability 匹配
- **I6 — Data Pipe 授权源和目标**：源所有权和目标能力策略都必须通过
- **I7 — 拒绝路径可审计**：失败的调用、peek、pipe 和策略决策都留下证据
- **I8 — 会话和协议状态显式化**：缺失初始化、错误版本、过期会话以可预测方式失败

> **设计哲学**：用户审批仍有用，但 I2 阻止它成为授权的替代品。Provider 元数据仍有用，但 I1 阻止它成为权威。OAuth token 仍有用，但 I3-I6 要求 OAuth 未定义的本地运行时检查。

### 1.4 威胁模型

**受保护资产**：用户资源、工具调用权威、服务器持有凭据、中间工具输出、handle 内容、审计证据

**攻击者能力**：
- 控制工具描述（tool poisoning）
- 操作或攻陷 MCP 式服务器
- 向工具输出注入内容（context poisoning）
- 使模型请求宽泛审批
- 在初始化前发送协议消息或使用过期会话
- 利用调用者提供的资源字符串与 Provider 实际资源解析的不匹配

**信任边界**：运行时核心（grant store、policy engine、data vault、audit log）可信；Provider 部分可信；模型和自然语言工具元数据**不作为策略权威**。

### 1.5 基准测试设计

**三种执行模式**：

- **B0 — 朴素连接层**：连接组件但缺乏执行控制不变量。下界对照组。
- **B1 — 实践感知缓解**：添加元数据 linting、警告、每调用审批、身份字段、会话检查。不是稻草人，而是连接层可实现的合理缓解。
- **B2 — HCP 运行时**：唯一将 principal、grant、资源、capability、审批、handle、data-pipe、协议状态、审计作为运行时管理对象的模式。

**五类攻击 × 每类两案例 = 10 个基准案例**：

1. **工具投毒（Tool Poisoning）** — 隐藏元数据要求 controller 外泄密钥 / 良性读元数据请求委托外发
2. **混淆代理（Confused Deputy）** — Bob 通过服务器权威读取 Alice 资源 / Bob 用相似前缀 grant 请求 Alice 私有资源
3. **过度权限与审批疲劳** — 宽泛审批用于无 grant 的工作区写入 / 宽泛审批用于无 grant 的外发
4. **上下文投毒（Data Pipe）** — 含 PII 的工具输出被管道传输到不接受 PII 的目标 / 错误 principal 读取他人 handle
5. **传输/会话混淆** — 初始化前发送普通方法 / 不兼容协议版本

### 1.6 关键实验结果

**安全成果（Table 4）**：

- B0（朴素）：10/10 攻击成功，0 阻止，0 审计完整
- B1（缓解）：6/10 攻击成功，4 阻止，0 审计完整
- B2（HCP）：0/10 攻击成功，10 阻止，10 审计完整

**B1 按类别表现**：工具投毒 0/2 阻止、混淆代理 2/2 阻止、过度权限 0/2 阻止、数据管道 0/2 阻止、传输 2/2 阻止

> **诊断价值**：连接层缓解对身份和会话状态有效，但 grant、handle 和 data-pipe 边界需要运行时对象。

**消融实验（Table 5）**：

- 移除 grant 匹配 → 暴露 6/10 案例
- 移除审批门 → 暴露 2/10
- 移除 handle 所有者检查 → 暴露 1/10
- 移除 data-pipe 目标策略 → 暴露 1/10
- 移除协议初始化门 / 版本检查 → 各暴露 2/10
- 移除拒绝路径审计 → 0 攻击暴露但 10/10 审计丢失

**运行时开销（Table 6，本地内存微基准，50 次迭代）**：

- 策略解释：均值 0.021ms，P95 0.054ms
- 任务启动读：均值 0.101ms，P95 0.201ms
- 数据 peek 预览：均值 0.004ms
- Data pipe 写入：均值 0.118ms
- 记录 888 条审计条目，371179 字节 JSON 审计数据

### 1.7 HCP 策略决策流程

一次 capability 调用的完整流程：

```
1. Principal 发起调用
2. Provider 规范化资源解析（调用者资源字符串不能覆盖）
3. Grant 匹配（principal + scope + resource + capability ID）
4. 审批门检查（高风险效果需要额外审批）
5. Provider 执行
6. 输出存储到 owned handle（绑定 principal/capability/resource/task）
7. 审计 allow/deny 记录
8. 失败时返回稳定的拒绝原因码
```

拒绝原因码包括：MISSING_PRINCIPAL、MISSING_GRANT、INSUFFICIENT_SCOPE、RESOURCE_MISMATCH、CAPABILITY_MISMATCH、EXPIRED_OR_REVOKED_GRANT、MISSING_APPROVAL、PROTOCOL_INITIALIZATION_FAILURE。

### 1.8 DataPipe 双向授权

DataPipe 是 HCP 的核心创新之一——将工具输出到下一个工具的数据移动视为新的授权事件，而非简单的字符串传递：

```
源 handle → [所有者检查] → [数据类兼容] → 目标 capability
                                    ↓
                           [目标策略检查]
                           [资源匹配]
                           [审批检查（如需）]
                                    ↓
                              审计条目（源+目标）
```

这不是完整的语言级信息流控制（IFC），但使源到目标的流显式且可测试。

### 1.9 GitHub 开源

仓库 `SymbolicLight-AGI/handle-capability-protocol` 包含：
- 协议草案（SPEC.md）+ 中文版 README
- JavaScript 参考运行时 + CLI + 演示
- JS/Python SDK 原型 + 一致性测试框架
- 论文基准复现 artifact（10 案例 + 验证器 + 表格生成器）
- MIT 许可证

---

## 二、查询拓展

### 2.1 MCP（Model Context Protocol）

Anthropic 于 2024 年底推出的开放协议，标准化 AI 模型与外部工具/数据源的连接方式。类似 USB-C 之于设备——提供统一接口，但 MCP 本身只定义连接层规范，不规定执行安全策略。Hermes Agent 已内置 native MCP 客户端，支持通过 config.yaml 配置 MCP server 实现自动工具发现。

### 2.2 混淆代理问题（Confused Deputy）

Norman Hardy 1988 年提出的经典安全问题：一个有特权的程序（deputy）被诱导，以自己的权限代表一个低权限调用者操作高权限资源。在 Agent 场景中，MCP server 持有凭据和文件权威，如果信任调用者提供的资源字符串而不做规范化解析，就可能成为混淆代理。HCP 通过 I3（Provider 规范化资源覆盖调用者字符串）直接应对此问题。

### 2.3 信息流控制（Information Flow Control）

Denning 的格模型（1976）和 JFlow（Myers 1999）将数据从一个安全域流向另一个安全域视为核心安全对象，而非仅检查初始读取。HCP 的 DataPipe 借鉴此理念，但采用更务实的简化版——检查源所有权 + 目标策略 + 数据类兼容，而非完整的语言级 IFC 标签系统。

### 2.4 Capability-Based Security vs ACL-Based Security

能力系统（capability systems）中，权限与操作绑定——持有 capability 即持有执行权。访问控制列表（ACL）中，权限与资源绑定——资源上记录谁可以访问。HCP 采用能力系统思路：Grant 作为显式 authority 绑定到 principal + resource + capability + scope，而非依赖 server 的"环境特权"。

### 2.5 AgentDojo / InjecAgent

两个间接 prompt injection 基准测试，研究恶意内容如何影响工具集成 Agent。HCP 与这些工作的区别在于：不依赖检测或过滤恶意内容来防御，而是将 provider 输出和元数据视为非权威，在运行时边界强制执行下一次调用。

---

## 三、归纳总结

### 3.1 两层分离架构

```
┌─────────────────────────────────────┐
│  Agent 意图层（LLM）                │
│  "帮我读取文件并发送到邮箱"          │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│  连接层（MCP）                        │
│  JSON-RPC / 工具发现 / 传输 / OAuth  │
│  ✓ 怎么到达工具服务器                │
│  ✗ 调用是否被授权                    │
│  ✗ 数据流是否安全                    │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│  执行控制层（HCP）                    │
│  Grant / Resource / Handle / Pipe    │
│  Policy Decision / Audit             │
│  ✓ Principal 是谁？                  │
│  ✓ 哪个 Grant 授权此调用？           │
│  ✓ 审批是否绑定到具体资源？           │
│  ✓ 输出数据归谁所有？                 │
│  ✓ 数据流向哪里？目标接受此数据类？   │
│  ✓ 拒绝路径有审计证据吗？             │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│  Provider 执行层                      │
│  文件系统 / Shell / 浏览器 / API     │
└─────────────────────────────────────┘
```

### 3.2 三种模式防护能力对比

- **B0 朴素连接**：无 grant 存储、无 handle 检查、无 data-pipe 策略、无审计 → 全部攻击成功
- **B1 连接层缓解**：有元数据 linting + 会话检查 + 每调用审批 + 身份字段 → 阻止身份/会话类攻击（4/10），但 grant/handle/pipe 边界仍敞开（6/10 成功）
- **B2 HCP 运行时**：8 条不变量全覆盖 → 阻止全部 10 例 + 完整审计证据

**关键洞察**：连接层缓解在"知道谁在调用"和"会话是否有效"方面有效（I1/I8 部分近似），但在"调用是否被授权"、"数据归谁所有"、"数据能否流向此处"方面力不从心（I2-I6 需要 grant/handle/pipe 对象）。

### 3.3 论文核心贡献

1. **概念贡献**：定义 8 条 MCP 式 Agent 执行安全不变量，将模糊的"安全最佳实践"转化为可测试的运行时属性
2. **工程贡献**：实现参考运行时（Principal/Resource/Grant/Capability/Handle/DataPipe/Audit 对象模型），验证不变量可执行
3. **评估贡献**：10 案例基准 + 消融 + 开销测量，证明 HCP 阻止全部攻击且亚毫秒级延迟
4. **方法论贡献**：将连接层安全与执行层安全明确分离，为 MCP 生态安全讨论提供了精确的词汇表

---

## 四、趋势判断

### 趋势1：MCP 安全将从"连接层规范"向"执行控制层"演进
依据：论文展示了连接层缓解（B1）即使加了元数据 linting + 会话检查 + 每调用审批，仍有 60% 攻击成功。微软也已发文讨论"MCP 控制面"（搜索结果 #5）。业界正在认识到连接层不足以覆盖执行安全。

### 趋势2：Agent 运行时将引入 Handle 机制替代原始字符串传输
依据：HCP 的 Handle 设计将工具输出从"自由复用的原始字符串"变为"运行时控制的引用对象"，附带所有者/来源/数据类元数据。这是信息流控制思想在 Agent 场景的务实落地。随着 Agent 多步链式调用增多，数据溯源将成为刚需。

### 趋势3：审计从"可选日志"向"运行时生成的 provenance"演进
依据：论文明确引用 W3C PROV-DM 和 Certificate Transparency，将审计定位为运行时生成的溯源记录而非应用层可选日志。I7 独立于攻击阻止——即使防御失效，审计证据仍支持事后检测和问责。

### 趋势4：Grant-Approval 双门模型将成为 Agent 权限管理标准
依据：论文最有诊断价值的发现是 B1 中"审批存在但无匹配 grant"的攻击全部成功。审批（人类确认）和授权（策略匹配）是两个正交维度，缺少任一都不安全。这比当前的"用户点了同意就行"模型严格得多。

---

## 五、关联分析

### 5.1 与 Hermes Agent MCP 集成的关联

Hermes 通过 `config.yaml` 配置 MCP server（`native-mcp` skill），当前实现了连接层——工具发现、自动调用。HCP 论文指出的安全缺口在 Hermes 中同样存在：

- Hermes 的 tool 调用没有 grant 概念——所有工具对所有会话平等可用
- 工具输出作为原始字符串在上下文中流转，没有 handle 所有权追踪
- 审批机制依赖用户交互（Hermes 的 permissions 系统），但不绑定到资源级 grant
- 审计依赖 session log，非结构化的运行时 provenance

**可落地的增量改进**：参考 HCP 的 I7（拒绝路径审计），可以为 Hermes 的 tool 调用失败增加结构化审计记录（调用者/capability/资源/拒绝原因），当前 session log 只有文本描述。

### 5.2 与 agent-security-governance Skill 的关联

Hermes 已有 `agent-security-governance` skill（"AI Agent 技能权限治理框架 — 基于零信任原则的多 Agent 系统安全基线"）。HCP 论文的 8 条不变量可以直接映射到此框架：

- I1（元数据非权威）→ skill 描述不能自动获得执行权限（Hermes 的 skill 虽然声明了 capabilities，但最终由用户/system prompt 决定）
- I2-I5（Grant-backed 调用）→ Hermes 的 permissions 系统目前是二元（允许/拒绝），缺少 scope/resource 粒度
- I6（DataPipe 双向授权）→ Hermes 完全没有数据流控制——一个工具的输出可以无限制地流入下一个工具
- I7（审计）→ Hermes 有 session log 但缺少结构化 provenance

### 5.3 与 Hermes 三机交换协议的关联

Hermes jbot/ubot/abot 三机通过 `exchange.jsonl` 共享经验和任务。HCP 的 Principal/Grant 模型可以指导多 Agent 场景的权限设计——当前三机共享文件系统上的经验池没有访问控制，任何 Agent 可以读写所有经验。如果引入 HCP 式的 principal-bound handle，可以实现"仅 ubot 可写 ubot 的经验记录"的隔离。

### 5.4 与 kv-cache eviction 论文（2606.29563）的关联

同批次候选论文中的 KV Cache eviction 研究关注推理效率，而 HCP 关注执行安全。两者构成了 Agent 系统优化的两个正交维度——一个让推理更快，一个让执行更安全。在边缘部署（Jetson Orin）场景中，两者都需要考虑：KV Cache eviction 降低显存占用，HCP 式审计增加少量延迟（论文测得 P95 < 0.2ms，边缘可接受）。

---

## 六、借鉴点优先级评估

### P0 — 结构化工具调用审计（可立即落地）
- **内容**：为 Hermes tool 调用增加结构化审计记录（timestamp + caller + tool_name + resource + result + reason）
- **现状**：Hermes 的 `exchange.jsonl` 只记录经验交换，tool 调用审计依赖 session log 文本
- **工作量**：2-3 小时（修改 tool 调用 hook，追加 JSON 结构到 audit log）
- **收益**：为后续安全分析、性能调优、行为回溯提供结构化数据

### P1 — 工具输出数据类标注（中等工程量）
- **内容**：参考 HCP Handle，为工具输出增加简单的数据类标签（PII/credential/public/intermediate）
- **现状**：工具输出作为原始文本在上下文中流转，敏感信息无标注
- **工作量**：1-2 天（需要定义数据类 schema + 修改 tool 调用返回值格式 + 在 DataPipe 等价物中检查）
- **收益**：防止凭据通过工具链意外外泄（如 web_search 结果中的 API key 被自动传入下一个工具）

### P2 — Grant-Based 工具权限系统（需架构改造）
- **内容**：引入 principal + scope + resource 粒度的工具调用授权
- **现状**：Hermes permissions 是二元 allow/deny，缺少 scope（如"只读"vs"读写"vs"外发"）和 resource 粒度
- **工作量**：3-5 天（需要重新设计 permissions schema + 修改 tool dispatch + UI 展示 grant 状态）
- **收益**：实现"用户审批 ≠ 授权"的双门模型，防止审批疲劳攻击

### P3 — DataPipe 双向授权（高级架构改造）
- **内容**：将工具间数据传递从"原始字符串"升级为"带元数据的 handle"
- **现状**：完全缺失
- **工作量**：1-2 周（需要引入 handle 层、修改上下文管理、对所有 tool 适配）
- **收益**：实现完整的信息流控制，从根本上阻止 context poisoning 攻击
- **障碍**：当前 LLM 上下文管理机制（文本拼接）与 handle 抽象存在阻抗失配

---

## 七、金句摘录

> 「A connection protocol can define how an agent reaches a tool server, but execution security depends on what happens after the connection is available.」

> 「The model and provider metadata propose actions; the runtime decides whether those actions are authorized.」

> 「Approval is a second gate, not a replacement for grant.」

> 「Audit does not replace prevention, but it improves detection and accountability.」

## 相关笔记
- [ROS2-Gazebo-VLM具身智能闭环控制](../2026-06-24-ROS2-Gazebo-VLM具身智能闭环控制.md)
- [AI-Agent自进化架构-记忆安全技能迁移](../2026-06-25-AI-Agent自进化架构-记忆安全技能迁移.md)
- [AI-Agent自进化架构](../2026-06-27-AI-Agent自进化架构.md)
- [量化推理隐藏成本与多Agent记忆扩展](../2026-06-29-量化推理隐藏成本与多Agent记忆扩展.md)
- [AI-Agent记忆自进化2026-WorldEvolver与神经程序记忆](../2026-07-01-AI-Agent记忆自进化2026-WorldEvolver与神经程序记忆.md)
- [AI-Agent自进化架构2026全景-WhatWhenHow三维框架](2026-06-28-AI-Agent自进化架构2026全景-WhatWhenHow三维框架.md)
- [检索记忆中的时间有效性-消除AI Agent在演化知识上的过时事实错误](2026-06-29-检索记忆中的时间有效性-消除AI Agent在演化知识上的过时事实错误.md)
- [AI-Agent工具链安全新攻击面-MCP协议脆弱性](2026-06-30-AI-Agent工具链安全新攻击面-MCP协议脆弱性.md)
