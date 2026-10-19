# 网络安全: Tool Permission Graph

**日期**: 2026-06-16  
**类型**: auto-explore  
**来源**: FeatBit, Cerbos, Stytch, AWS, OWASP

## 相关笔记
- [[2026-06-05-Anthropic开源AI漏洞发现框架-Defending-Code-Reference-Harness]] (关键词: 网络安全, 工具权限)
- [[2026-04-08-claude-code-tool-execution-orchestration]] (关键词: Tool, 执行编排)

---

## 摘要

AI Agent的工具权限管理是生产级安全的核心环节。核心原则：**权限分层 + 运行时控制 + 人类审批矩阵**，而非简单的工具开关。

---

## 关键发现

### 1. 权限模式阶梯（Permission Mode Ladder）

不应只有"开/关"两种状态，应设计7层权限模式：

- off：完全禁用工具调用
- observe_only：记录意图但不执行
- search_only：仅查询和推荐
- read_only：读取受限数据
- draft_write：创建草稿/分支，不提交
- approval_required：准备操作等待人工审批
- autonomous_limited：执行有限自动操作
- break_glass：紧急操作，需指定负责人

核心设计原则：单调安全（monotonic safety）——当控制系统缺失上下文时，应降级到更安全的模式。

### 2. 审批矩阵设计

审批应针对"人类判断能改变结果"的决策，而非所有操作：

- 结合：操作类别 + 可逆性 + 影响范围 + 证据成熟度
- 避免：所有小操作都审批（用户会习惯性点击通过）
- 避免：只有灾难性操作才审批（错过中间地带）

### 3. 身份分离原则

AI Agent应作为独立客户端运行，而非继承用户身份：

- 使用独立的OAuth Client ID和访问令牌
- 明确定义、审计和限制Agent权限
- 防止Agent继承超出其职责范围的权限

### 4. OWASP Agentic AI威胁分类

关键威胁向量：

- T2：工具滥用（Tool Misuse）——通过欺骗性提示操纵Agent
- T10：过度的人类监督（Overwhelming Human in the Loop）——利用人类认知局限
- T13：多Agent系统中的恶意Agent（Rogue Agents）
- T14：多Agent系统中的人类攻击

### 5. 分层防护模型

- 外层：通用应用安全
- 中层：生成式AI安全
- 内层：身份管理、工具操纵、记忆投毒等风险控制

---

## 对工作的价值

1. **Hermes Agent权限治理**：当前工具权限为三层模型（允许/禁止/确认），可升级为7层权限阶梯，支持更细粒度控制
2. **审批矩阵落地**：为每个工具定义审批触发条件，避免"全开"或"全关"的极端
3. **身份分离**：Agent应使用独立身份而非继承用户身份，便于审计和限制
4. **运行时降级**：当控制服务不可用时，自动降级到更安全的模式

---

## 行动建议

1. 在Hermes Gateway中实现权限模式阶梯（从3层扩展到7层）
2. 为每个Skill定义审批矩阵（操作类别 × 可逆性 × 影响范围）
3. 添加运行时降级机制：控制服务不可用时自动切换到safe mode
4. 记录所有工具调用的权限评估结果、原因和审批人
5. 参考Microsoft Entra Agent ID的三层模型（Blueprint → Principle → Identity）

---

## 参考链接

- https://www.featbit.co/blogs/ai-agent-tool-permissions-approval-fallback
- https://www.cerbos.dev/blog/permission-management-for-ai-agents
- https://stytch.com/blog/handling-ai-agent-permissions
- https://aws.amazon.com/cn/blogs/china/privacy-and-security-of-agent-applications
- https://genai.owasp.org/llm-top-10/
