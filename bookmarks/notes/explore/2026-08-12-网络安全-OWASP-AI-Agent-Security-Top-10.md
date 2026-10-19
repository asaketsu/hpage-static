# 网络安全: OWASP AI Agent Security Top 10

> ⚠️ 网络受限，基于多源信息整合整理，部分细节未经实时搜索验证。来源：DDG搜索结果 + StartupDefense.io文章 + DEV Community深度分析 + Alex Ewerlöf Cheat Sheet

---

## 摘要

OWASP 于 **2025年12月** 发布了《OWASP Top 10 for Agentic Applications 2026》（简称 **ASI Top 10**），这是首个专门针对自主AI智能体安全的行业框架。由 **100+ 安全研究人员和实践者** 同行评审，识别出AI Agent在规划、决策和执行工作流时面临的十大关键安全风险。

核心背景：根据Dark Reading调查，**48%的网络安全从业者将Agent AI列为2026年头号攻击向量**，超过deepfake、勒索软件和供应链攻击。但仅34%的企业拥有AI特定安全控制措施。79%的组织已部署Agent AI，预计到2034年市场规模达$199B。不到40%的组织对Agent工作流进行定期安全测试。

---

## 十大风险一览（ASI01–ASI10）

| ASI ID | 风险名称 | 一句话描述 |
|--------|---------|-----------|
| ASI01 | Agent Goal Hijack（目标劫持） | 攻击者通过间接提示注入操控Agent的核心目标或决策路径（传统LLM Injection的Agent演进版） |
| ASI02 | Tool Misuse / Abstraction Flaws（工具滥用） | Agent调用API、执行代码、操作文件等工具的抽象层存在漏洞，导致越权执行 |
| ASI03 | Credential Access & Data Leakage（凭证访问与数据泄露） | Agent可自动访问数据库、邮箱、外部API，凭证管理不当会导致大规模数据外泄 |
| ASI04 | Supply Chain Compromise（供应链投毒） | Agent使用的模型、技能库、Prompt模板被植入恶意逻辑，通过链式调用传播 |
| ASI05 | Insecure Output Handling（不安全输出处理） | Agent输出的指令/代码/命令未经验证直接执行，类似RCE漏洞 |
| ASI06 | Excessive Agency（过度代理权） | Agent被授予超出任务所需的最小权限，任何漏洞都被放大为系统级损害 |
| ASI07 | Autonomous Decision Flaws（自主决策缺陷） | Agent在没有人类监督的情况下做出不可逆决策（删除文件、发送敏感邮件等） |
| ASI08 | Multi-Agent Coordination Attacks（多Agent协调攻击） | 多个Agent之间的通信通道被劫持，一个Agent的违规结果传递到其他Agent |
| ASI09 | Insufficient Observability（可观测性不足） | 缺乏对Agent行为的完整审计追踪，无法检测异常行为或事后追溯 |
| ASI10 | Resource Exploitation & Cost Abuse（资源剥削与成本滥用） | Agent循环消耗token导致巨额账单，或被利用执行加密挖矿等资源密集型操作 |

---

## 两大核心防护原则

### 1. 最小代理权（Least-Agency）

- 传统PoLP（最小权限原则）在Agent场景下的延伸
- Agent应仅被赋予完成其定义任务所需的**最小自治级别**
- 自治性是挣来的特性，不是默认设置
- 示例：财务Agent只能发起审批请求，不能直接转账；客服Agent只能查询订单，不能修改用户账户

### 2. 强可观测性（Strong Observability）

- 需要对Agent的行为有清晰、全面的可见性
- 必须记录：目标状态、工具使用模式、决策路径、每步推理
- 日志需要包含完整的因果链（为什么调用这个工具？触发条件是什么？）
- 实时监控比事后审计更重要

---

## Agent特有的安全挑战（与传统LLM不同）

### 1. 指令与数据混合空间

传统计算系统中，指令（代码/二进制）与数据（字符串/文档）物理分离。LLM上下文窗口中，系统Prompt、工具调用结果和用户输入全部拼接成单一字符串。这打开了大量越狱技术的攻击面（Prompt Injection、角色扮演、"忽略所有之前指令"等）。

### 2. 自主行动的级联效应

传统LLM只生成文本输出。Agent会**规划→决策→执行**。一个小漏洞可以迅速级联为系统性妥协：
- Prompt注入 → 目标劫持 → 调用恶意API → 数据外泄 → 横向移动
- 这种链式传播在传统系统中不存在

### 3. 非确定性带来的可靠性问题

LLM本质上是不确定的文本预测引擎。加上while循环和API访问后，Agent可能在错误方向无限循环消耗token。最坏情况是财务灾难——每次迭代都昂贵，且预期需要更少的人类监督。

### 4. 多Agent协调攻击面

单Agent攻击 vs 多Agent攻击完全不同：
- 攻击一个Agent可能污染其输出
- 该输出作为输入传递给其他Agent
- 形成跨系统的信任链崩塌

---

## 对Hermes Agent的借鉴点

### 直接应用

1. **Skill权限隔离**：每个Skill应遵循最小代理权原则。`terminal`工具不应无条件开放给任何Skill，应根据Skill类型限定可执行的命令白名单。

2. **Agent行为日志**：Hermes当前已有cron执行日志，但缺少Agent层面的行为追踪。建议增加：工具调用链日志（谁调了什么？为什么调？）、决策路径快照（Agent选择了哪个降级路径？原因？）。

3. **子代理沙箱隔离**：`delegate_task`的子agent之间应相互隔离，防止ASI08描述的跨Agent信任链崩塌。当前已有一定隔离（isolated contexts），但需确认工具调用权限不互相泄漏。

4. **Cost监控机制**：Agent循环中的token消耗无上限可能导致成本失控。建议增加per-session token预算限制和异常消耗告警。

### 架构改进方向

```
Hermes vNext 安全增强优先级：

P0: Skill级工具权限白名单（Least-Agency）
P0: 子Agent间工具调用权限隔离（Multi-Agent Attack Prevention）
P1: Agent行为全链路审计日志（Observability）
P1: Session token预算上限 + 超限熔断
P2: Input sanitization中间件（Intent Capsule模式）
P2: 多Agent信任链验证（跨session上下文完整性检查）
```

---

## 行动建议

1. **立即**：审查现有Hermes Skill列表，标记所有含`terminal`/`browser_navigate`权限的Skill，评估是否符合最小代理权原则。

2. **本周内**：在`AGENTS.md`中补充"Agent行为审计"章节，要求所有复杂任务产出包含决策路径记录。

3. **月度回顾**：将ASI Top 10纳入季度安全评审议程，结合evolver的错误案例库进行交叉分析。

4. **长期**：考虑为Hermes开发内置的安全护栏框架（Security Guardrails Framework），实现运行时权限检查和异常行为拦截。

---

*参考链接：*
- *https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/*（官方OWASP源）
- *https://dev.to/alessandro_pignati/the-owasp-top-10-for-ai-agents-your-2026-security-checklist-asi-top-10-cck*（开发者指南）
- *https://blog.alexewerlof.com/p/owasp-top-10-ai-llm-agents*（工程实践Cheatsheet）
- *https://www.startupdefense.io/blog/owasp-top-10-agentic-ai-security-risks-2026*（企业视角解读）

## 相关笔记

- [AI安全与防御 五大技术路线对比](./2026-08-12-AI安全与防御-五大技术路线对比.md) — 防御技术全景，与本篇威胁清单互补
- [技能污染与守门人 自进化Agent相位跃迁](./explore/2026-08-06-技能污染与守门人-自进化Agent的相位跃迁.md) — Agent 安全治理
- [自进化Agent三层进化矩阵](./2026-07-06-自进化Agent2026-三层进化矩阵与源码级重写.md) — 安全边界与进化约束
