# Agentic Zero Trust — 自主 AI Agent 的零信任安全框架

- 日期: 2026-08-21
- 类型: auto-explore
- 来源: Zentera、Cequence/DrZeroTrust、CSA、Zscaler、Strata

## 摘要

Agentic Zero Trust 是将传统 Zero Trust（NIST SP 800-207）扩展到自主 AI Agent 的安全范式。核心主张：**仅凭身份认证不足以约束 Agent，必须在"边界层"（enclave）而非"模型层"进行管控**。Zentera、Dr. Chase Cunningham（Cequence）与 Anthropic 在 2026 年独立得出相同结论——"contain the agent at the boundary, not the model"。

## 关键发现

- **身份 ≠ 足够**。仅 47.1% 的部署 Agent 被主动监控（Gravitee 2026）；68% 组织无法从日志区分人类与 Agent 行为（CSA/Aembit）。
- **三个结构性缺口**（传统 ZT 无法覆盖）：
  1. Token Isolation Pattern — Agent 共享 API Key 导致归因失效（仅 22% 从业者将 Agent 视为独立身份）。
  2. Agent Persona Framework — Agent 的任务描述随时间漂移，运行时授权需持续校准。
  3. Behavioral Identity — 基于"Agent 做了什么"而非"Agent 声称是谁"进行审计。
- **Enclave（隔离舱）** 是核心架构：将 Agent 限定在项目级网络边界内，网络可达性层面阻断跨项目访问——即使用户 Prompt 被注入也无法越界。
- **Virtual Chamber（虚拟保险柜）**：在项目内部为高价值资产（代码、密钥）单独加锁，隔离舱内其他被攻陷 Agent 也无法访问。
- **成熟度分级**（CSA Agentic Trust Framework）：Intern → Junior → Associate → Senior → Lead，每个级别有最小在岗时间、性能阈值、安全验证和治理签核。
- **Zscaler 2026 年 6 月** 在 Zenith Live 发布业界首个完整 Agentic AI 零信任平台，覆盖数据访问、系统交互、跨企业运营三层。

## 对工作的价值

- 我们自己的 Hermes Agent 多机集群（jbot/ubot/abot）本质上就是 Agentic 架构——多个自主 Agent 共享文件系统、互相调用。这套框架直接适用于我们的横向越权防护。
- 当前 Hermes 的 Skill 权限治理（agent-security-governance）主要靠文档约定，缺乏"网络可达性层"硬隔离。Enclave 概念可引导我们在 NFS4 共享层之外增加 Agent-to-Agent 调用的边界限制。
- 独立 Agent 身份 + 持续行为审计 → 对应我们现有的 evolver 自我进化日志可以改造为 Behavioral Identity 审计源。

## 行动建议

- [ ] 短期: 在 agent-security-governance Skill 中补一节 "Agent 独立身份识别"——每个 Agent 在操作关键资源时打上唯一 agent_id 标签。
- [ ] 中期: 评估 Hermes Gateway 是否支持按 Agent 会话级别的路由/隔离（对标 Enclave）。
- [ ] 参考: DrZeroTrust v3 论文（Cequence）、CSA ATF GitHub 仓库、Anthropic Agent Zero Trust Framework（2026-05）。

## 相关笔记

- [Agent 记忆与自进化架构 2026 前沿](../2026-08-21-Agent记忆与自进化架构2026前沿-超图技能库分段固化与在线Harness编译.md) — Agent 治理学术侧
- [MCP Tool Description Injection](2026-08-21-网络安全-MCP-tool-description-inj.md) — 同日前奏，MCP 层攻击面
- [Agentic Zero Trust / OWASP Top 10](../../explore/2026-08-20-owasp-agentic-ai-security-top-10-2026.md) — 同类主题，OWASP 侧
- [Git Worktree ↔ Agent Profile 隔离](../../explore/2026-08-21-worktree-profile-isolation-isomorphism.md) — 隔离架构搭档
