# 微软 Agent Governance Toolkit：确定性 Agent 治理全栈

> 📅 2026-06-06 | 夜间自学习
> 🔗 来源：GitHub microsoft/agent-governance-toolkit (MIT License) + OWASP Agentic AI Top 10 + NIST AI RMF
> 🏷️ 关键词：Agent 治理、策略引擎、零信任、确定性拦截、OWASP、MCP 安全网关、审计、Policy-as-Code

---

## 一、项目定位与核心问题

### 1.1 解决什么问题？

AI Agent 部署到生产环境后面临三个核心问题：

1. **这个动作允许吗？** — Agent 有 `send_email` 和 `query_database` 权限，但不应能执行 `drop_table`。OAuth scopes 控制的是"能连到哪个服务"，不是"连上后能做什么"
2. **是哪个 Agent 做的？** — 多 Agent 系统中 5 个 Agent 共享一个 API key，出问题时"某个 Agent 干的"不够
3. **能证明发生了什么吗？** — 审计和监管需要防篡改的决策记录：什么策略生效、Agent 请求了什么、为什么被允许或拒绝

### 1.2 核心论点：Prompt 不是控制面

OWASP LLM01:2025 明确指出："目前尚不清楚是否存在万无一失的 Prompt 注入防护方法。"Andriushchenko et al. (ICLR 2025) 报告 GPT-4o、Claude 3、Llama-3 的**100% 攻击成功率**。微软自己的 AI Red Teaming Agent 也证实了这一点。

**AGT 的策略**：不在 Prompt 内打这场仗。每个工具调用、消息发送、委托操作都在**确定性应用代码**中被拦截——在模型意图到达网络之前。AGT 拒绝的动作不是"不太可能发生"，而是**结构上不可能发生**。

> "That is the difference between asking an agent to behave and making it incapable of misbehaving."

---

## 二、架构设计

### 2.1 五大模块

```
agent-governance-toolkit-core      → 策略引擎 + 能力模型 + 审计 + MCP 网关 + 零信任身份 + 信任评分 + A2A/MCP/IATP 桥接
agent-governance-toolkit-runtime   → 特权环 + Saga 编排 + 终止控制 + 执行计划验证
agent-governance-toolkit-sre       → SLO + 错误预算 + 混沌工程 + 熔断器
agent-governance-toolkit-cli       → agt CLI + OWASP 合规检查 + 完整性验证 + 策略 lint
agent-governance-toolkit[full]     → 全部安装的 meta 包
```

v4.0.0 将原先 45 个包整合为 5 个顶级发行版，大幅简化依赖管理。

### 2.2 六语言 SDK

| 语言 | 包名 | 安装命令 |
|------|------|---------|
| Python | agent-governance-toolkit | `pip install agent-governance-toolkit[full]` |
| TypeScript | @microsoft/agent-governance-sdk | `npm install @microsoft/agent-governance-sdk` |
| .NET | Microsoft.AgentGovernance | `dotnet add package Microsoft.AgentGovernance` |
| Rust | agent-governance | `cargo add agent-governance` |
| Go | agent-governance-toolkit | `go get .../agent-governance-golang` |
| Claude Code | 插件 | `/plugin install agt-governance@agent-governance-toolkit` |

### 2.3 框架支持

支持 14+ 框架的原生/适配器集成：

- **原生**: Microsoft Agent Framework, Semantic Kernel
- **适配器**: AutoGen, LangGraph/LangChain, CrewAI, Google ADK, LlamaIndex, Haystack, Mastra, Dify
- **中间件**: OpenAI Agents SDK
- **插件**: Claude Code, GitHub Copilot CLI

---

## 三、核心机制

### 3.1 Policy-as-Code

YAML 声明策略，每次工具调用时评估：

```yaml
apiVersion: governance.toolkit/v1
name: production-policy
default_action: allow
rules:
  - name: block-destructive
    condition: "action.type in ['drop', 'delete', 'truncate']"
    action: deny
    description: "Destructive operations require human approval"

  - name: require-approval-for-send
    condition: "action.type == 'send_email'"
    action: require_approval
    approvers: ["security-team"]
```

两行代码即可治理任何工具函数：

```python
from agentmesh.governance import govern
safe_tool = govern(my_tool, policy="policy.yaml")  # 每次调用检查、记录、执行
```

### 3.2 零信任身份与信任评分

- 每个 Agent 有独立身份（不共享 API key）
- 基于行为的信任评分（不是静态权限）
- 委托链追踪（Agent A → Agent B → Tool C 的完整路径）
- 135 个一致性测试覆盖身份和信任规范

### 3.3 MCP 安全网关

专门针对 MCP 的安全防护层：
- Tool Poisoning 检测（工具描述中的隐藏指令）
- 漂移检测（工具行为是否偏离声明）
- 127 个一致性测试

### 3.4 审计与合规

- **Merkle 审计日志**：防篡改的决策记录
- **Decision BOM**（物料清单）：每次决策的完整上下文
- 自动映射到合规标准

---

## 四、正式规范体系

AGT 最独特之处是**每个核心组件都有 RFC 2119 级正式规范 + 一致性测试**：

| 规范 | 测试数 |
|------|--------|
| Policy Engine | 68 |
| Identity & Trust | 135 |
| Execution Control | 80 |
| Trust & Coordination | 62 |
| SRE Governance | 111 |
| MCP Security Gateway | 127 |
| Lightning Fast-Path (RL) | 100 |
| Framework Adapter Contract | 152 |
| Audit & Compliance | 157 |
| **总计** | **992** |

29 个架构决策记录（ADR）文档化每个关键设计选择的"为什么"。

---

## 五、合规映射

| 标准 | 覆盖 |
|------|------|
| OWASP Agentic AI Top 10 | 10/10 全覆盖 |
| NIST AI RMF 1.0 | GOVERN/MAP/MEASURE/MANAGE 全对齐 |
| EU AI Act | 合规映射 + 自动证据 |
| SOC 2 | 控制映射 + 审计跟踪导出 |

---

## 六、与 Hermes 系统的关联

### 6.1 直接价值

1. **策略拦截**：Hermes 的 `terminal`、`write_file`、`patch` 等工具调用可包装为 governed tool，所有破坏性操作走 `deny` 或 `require_approval`
2. **MCP 安全**：AGT 的 MCP Security Gateway 直接解决 6-03 笔记中记录的 50 CVE 威胁
3. **审计日志**：Hermes 的所有决策可自动获得 Merkle 审计追踪
4. **三机身份**：jbot/ubot/abot 各自独立身份 + 信任评分

### 6.2 评估路径

```
Phase 1: pip install agent-governance-toolkit[full]
Phase 2: 为 Hermes 工具编写 policy.yaml（block destructive ops, require approval for production）
Phase 3: 集成到 Hermes Gateway 中间件层
Phase 4: 三机互信 + Merkle 审计
```

### 6.3 与已有 Skill 的关系

- **agent-security-governance Skill**：AGT 是该 Skill 的**生产级实现**，应 patch 增加引用
- **mcp-security-audit Skill**：AGT 的 MCP Security Gateway 是更完整的方案
- **deterministic-guardrails Skill**：AGT 的 Policy Engine 是确定性护栏的工业级范例

---

## 七、关键洞察

1. **确定性 > 概率性**：AGT 的哲学是"在确定性代码中拦截，不依赖模型的概率行为"。这对 Hermes 的架构方向有根本性指导意义
2. **Policy-as-Code**：用 YAML 声明安全策略，而非硬编码或依赖 Prompt 指令。这与 Hermes 的"龙虾法则"（机械化质量门禁）高度一致
3. **992 个测试**：形式化规范 + 一致性测试是真正的工程化标准，远超一般开源项目的质量基线
4. **多语言多框架**：AGT 不绑定特定框架，而是作为中间件层插入任何 Agent 系统。这与 Hermes 的"模型中立性"策略一致
5. **MCP 安全是独立规范**：微软将 MCP 安全网关作为独立规范（127 测试），表明 MCP 安全已成为工业界的一级关注

---

## 八、参考资料

- [GitHub: microsoft/agent-governance-toolkit](https://github.com/microsoft/agent-governance-toolkit)
- [PyPI: agent-governance-toolkit](https://pypi.org/project/agent-governance-toolkit/)
- [官方文档](https://microsoft.github.io/agent-governance-toolkit/)
- [OWASP Agentic AI Top 10 合规映射](https://github.com/microsoft/agent-governance-toolkit/blob/main/docs/compliance/owasp-agentic-top10-architecture.md)
- Andriushchenko et al. (ICLR 2025) — JailbreakBench 100% ASR 报告
- OWASP LLM01:2025 — Prompt Injection 风险定义

## 相关笔记
- [AI编码工具战争-CodexClaudeCodeCursor收敛为分层架构](2026-05-24-AI编码工具战争-CodexClaudeCodeCursor收敛为分层架构.md)
- [AI-Agent依赖更新安全风险-117K变更实证研究](2026-06-01-AI-Agent依赖更新安全风险-117K变更实证研究.md)
- [AI-Agent长期记忆架构2026-范式演进与生产化](2026-06-03-AI-Agent长期记忆架构2026-范式演进与生产化.md)
- [Beetle-OS-ESP32智能设备Agent系统](2026-06-03-Beetle-OS-ESP32智能设备Agent系统.md)
- [AI-Agent协议生态2026全景-MCP-A2A-ACP-UCP四层协议栈](2026-06-04-AI-Agent协议生态2026全景-MCP-A2A-ACP-UCP四层协议栈.md)
- [Claude-Code动态工作流六种调度模式](2026-06-04-Claude-Code动态工作流六种调度模式.md)
- [EtherCAT-IgH开源主站与具身智能落地](2026-06-04-EtherCAT-IgH开源主站与具身智能落地.md)
- [A2A协议v1.0正式发布-三层架构-多绑定与Agent互联新范式](2026-06-05-A2A协议v1.0正式发布-三层架构-多绑定与Agent互联新范式.md)
- [Meta智能眼镜暗藏人脸识别管道-隐私与AI的边界](2026-06-05-Meta智能眼镜暗藏人脸识别管道-隐私与AI的边界.md)
- [OrcaLab-松应具身智能仿真平台](2026-06-05-OrcaLab-松应具身智能仿真平台.md)
- [微软RD-Agent-Quant-首个数据驱动的量化多Agent框架](2026-06-05-微软RD-Agent-Quant-首个数据驱动的量化多Agent框架.md)
- [AI科研工具生态2026-智能化工具链](explore/2026-06-05-AI科研工具生态2026-智能化工具链.md)
- [StreamMA多Agent流式推理](explore/2026-06-05-StreamMA多Agent流式推理.md)
