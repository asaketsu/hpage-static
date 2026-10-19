# Hermes Agent 源码拆解与自我进化机制详解

- 来源：https://mp.weixin.qq.com/s/qdycBcCUujnVBkO4vky0wA
- 作者：刘庭辉（腾讯云开发者）
- 日期：2025-05-12

---

## 核心观点

Hermes 的"自我进化"不是模型微调，而是 **Prompt Engineering + 文件持久化** 的工程化实现——不改权重，只改"怎么用模型"的策略。

## 三大核心机制

### 1. 四维持久记忆

- 身份记忆（SOUL.md）— Agent 角色定义、行为准则
- Agent 笔记（MEMORY.md）— 用户偏好、项目上下文、经验教训
- 程序性记忆（SKILL.md）— 可复用的工作流程、操作步骤
- 对话历史 — 当前会话的完整上下文

设计要点："冻结快照"模式——会话开始时加载快照，会话期间后台更新不影响当前上下文，避免不一致。

### 2. 技能自动创造

Agent 执行任务 → 后台自动审查 → 判断是否有价值 → 自动创建/更新 Skill → 下次会话自动加载。

Skill 是纯 Markdown 文件，无代码，LLM 自主读写修改。不需要编程能力。

### 3. KEPA（Knowledge-Enhanced Prompt Adaptation）

作者自造术语，类比深度学习：
- 前向传播：用户意图 → Hermes（LLM+工具）→ 执行结果
- 反向传播：周期性回顾执行过程 → 检测失败点 → 更新 Skill/记忆

实现：每 N 次工具调用触发后台审查线程，不阻塞主 Agent。审查 Agent 判断任务是否有试错或策略变更，有则保存 Skill，无则跳过。

本质：一段 Prompt + 一个后台线程 + 文件系统。没有强化学习、没有模型微调、没有向量数据库。

## 优势

1. 零成本进化——审查 Agent Token 消耗极小
2. 可解释可编辑——Skill 是 Markdown，人可读可改
3. 跨模型迁移——Skill 不依赖特定模型
4. 渐进式积累——越用越强

## 局限

| 问题 | 说明 |
|------|------|
| "自动"不等于"准确" | 可能产生噪声或漏判 |
| 只有复杂任务才触发 | 简单任务大概率返回 "Nothing to save" |
| 更新有延迟 | 后台更新的 Skill 下次会话才生效 |
| 生态差距 | 第三方生态仍在早期 |

## 我的评价

**准确的部分**：记忆分层架构正确、Skill 自动创建机制基本准确、冻结快照设计确实存在、优劣势分析客观。

**不准确/过度简化的部分**：
- KEPA 并非官方术语，是作者自己造的概念类比
- OpenClaw vs Hermes 做了非此即彼对比，实际定位不同
- 后台审查触发逻辑（"每 10 次工具调用"）过于简化
- 本质是"自动笔记"式的经验闭环，没有评估函数、选择压力、淘汰机制，和真正的"进化"差距很大

## 与 Claude Code 路线对比

Hermes 的 Skill 体系与 Claude Code 的 CLAUDE.md + slash commands 思路相似——都是通过持久化文件让 Agent 积累经验。但 Hermes 多了"自动审查→自动创建 Skill"的闭环，Claude Code 目前依赖用户手动维护。

## 关键引用

> 整个"自我进化"核心 = 一段 Prompt + 一个后台线程 + 文件持久化。没有强化学习、没有模型微调、没有向量数据库——纯粹的 Prompt Engineering + 文件系统。

## 相关笔记
- [AI趋势2026-推理时计算与反思Agent](2026-05-11-AI趋势2026-推理时计算与反思Agent.md)
- [具身智能2026-世界模型VLA车企入局](2026-05-11-具身智能2026-世界模型VLA车企入局.md)
- [具身智能2026从实验到实战](2026-05-11-具身智能2026从实验到实战.md)
- [Claude-3D-CAD-创意连接器深度分析](2026-05-13-Claude-3D-CAD-创意连接器深度分析.md)
- [Agent工程4月实践-不要一上来就做Agent](2026-05-14-Agent工程4月实践-不要一上来就做Agent.md)
- [HTML-Anything-Agent驱动HTML编辑器](2026-05-14-HTML-Anything-Agent驱动HTML编辑器.md)
- [MATLAB-Agentic-Toolkit分析](2026-05-14-MATLAB-Agentic-Toolkit分析.md)
- [手撸Agent-ReAct-Loop从零实现](2026-05-14-手撸Agent-ReAct-Loop从零实现.md)
- [上下文才是Agent的命门-QClaw上下文竞争论](2026-05-15-上下文才是Agent的命门-QClaw上下文竞争论.md)
- [OpenHuman-记忆树AI智能体-i龙虾](2026-05-16-OpenHuman-记忆树AI智能体-i龙虾.md)
- [PicoClaw-超轻量AI-Agent框架](2026-05-16-PicoClaw-超轻量AI-Agent框架.md)
- [具身智能前沿学习](2026-05-17-具身智能前沿学习.md)
- [20260513-llm-wiki-obsidian-gbrain-知识自组织与自进化](20260513-llm-wiki-obsidian-gbrain-知识自组织与自进化.md)
- [ai-agent-protocols-mcp-a2a](explore/2026-05-11-ai-agent-protocols-mcp-a2a.md)
- [AI-Agent架构-MCP-A2A协议栈](explore/2026-05-13-AI-Agent架构-MCP-A2A协议栈.md)
- [Agentic-SOC-安全自动化的范式转变](explore/2026-05-13-Agentic-SOC-安全自动化的范式转变.md)
- [Agentic-Engineering-从Vibe-Coding到Agent工程](explore/2026-05-14-Agentic-Engineering-从Vibe-Coding到Agent工程.md)
- [ai-agent-architecture](explore/2026-05-15-ai-agent-architecture.md)
- [ai开源生态-huggingface春季](explore/2026-05-15-ai开源生态-huggingface春季.md)
- [AI-Agent-协议生态-深度整合学习](explore/2026-05-16-AI-Agent-协议生态-深度整合学习.md)
- [Agentic-AI元年-智能体全面落地趋势](explore/2026-05-16-Agentic-AI元年-智能体全面落地趋势.md)
- [HuggingFace-Spring2026-开源生态报告](explore/2026-05-16-HuggingFace-Spring2026-开源生态报告.md)
- [qclaw-上下文四层模型](explore/2026-05-16-qclaw-上下文四层模型.md)
- [具身智能-从造产品到抢落地六大趋势](explore/2026-05-16-具身智能-从造产品到抢落地六大趋势.md)
- [竞品动态-Agentic-Engineering范式转变](explore/2026-05-16-竞品动态-Agentic-Engineering范式转变.md)
- [agent-collaboration-self-evolution](explore/2026-05-17-agent-collaboration-self-evolution.md)
- [llm-wiki-gbrain-agent-evolution_33aa818c](llm-wiki-gbrain-agent-evolution_33aa818c.md)
- [0元打通Claude-Codex-OpenCode免费模型6入口](orphan/2026-05-11-0元打通Claude-Codex-OpenCode免费模型6入口.md)
- [HuggingFace-春季生态-Agentic-World-Modeling](orphan/2026-05-13-HuggingFace-春季生态-Agentic-World-Modeling.md)
- [具身智能量产关键年](orphan/2026-05-15-具身智能量产关键年.md)
- [HTML的不合理有效性-Claude-Code-团队](orphan/2026-05-16-HTML的不合理有效性-Claude-Code-团队.md)
