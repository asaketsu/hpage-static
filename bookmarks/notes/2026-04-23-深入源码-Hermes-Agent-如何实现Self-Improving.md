# 深入源码：Hermes Agent 如何实现 Self-Improving

> 来源：微信公众号 | 2026-04-23
> 链接：https://mp.weixin.qq.com/s/Qi68ptxQRyiA932JU49SYQ

## 摘要

Hermes Agent 通过三大子系统实现自进化闭环：**Memory**（记住你是谁）+ **Skill**（记住怎么做事）+ **Nudge Engine**（定时触发反思）。用得越久能力越强，与 OpenClaw 的"手写 Skill + 纯追加记忆"形成代际差异。

---

## 一、三大子系统架构

### 1. Memory — 越用越懂你

| 特性 | 实现 |
|------|------|
| 存储 | 两个文件：`MEMORY.md`(2200 chars) + `USER.md`(1375 chars) |
| 容量策略 | 严格上限，超限返回错误+现有条目，**引导模型主动做信息压缩** |
| 冻结快照 | 会话启动时捕获，系统提示词不变→共享前缀缓存省 token |
| 写入规范 | 声明式事实（"User prefers X"）而非命令式指令（"Always do X"） |

**关键洞察**：容量有限倒逼信息压缩，过时内容自然被挤掉，留下高密度事实。对比 OpenClaw 的纯追加模式（用几个月膨胀成几万行），这是本质差异。

### 2. Skill — 把做过的事变成会做的事

| 特性 | 实现 |
|------|------|
| 结构 | `~/.hermes/skills/` 下目录，核心 `SKILL.md` + YAML frontmatter |
| 创建触发 | 工具调用>5次 + 踩过坑 + 用户纠正过 |
| 修补机制 | `fuzzy_find_and_replace` 局部 patch，非全量重写 |
| 安全 | 修改后自动 `_security_scan_skill()`，不通过就回滚 |
| 加载策略 | 轻量索引（名字+一句话描述）→ 按需 `skill_view` 加载全文 |

**关键洞察**：OpenClaw 的 Skill 是静态配置文件，用一年还是那份文件；Hermes 的 Skill 是越用越厚的经验资产。

### 3. Nudge Engine — 谁来提醒"该学习了"

| 计数器 | 粒度 | 默认阈值 |
|--------|------|----------|
| Memory Nudge | 按用户回合 | 10 回合 |
| Skill Nudge | 按工具迭代 | 10 迭代 |

**后台 fork 机制**：
- 触发后在后台 fork 独立 Agent 实例
- 输出重定向到 `/dev/null`，用户完全无感知
- review agent 最多 8 次工具调用
- 自身 nudge 被禁用，防止无限递归
- 共享同一份 Memory，写入直接生效

---

## 二、完整案例：三次会话的进化过程

| 维度 | 会话1(冷启动) | 会话2(Skill复用) | 会话3(全协同) |
|------|-------------|----------------|-------------|
| 工具调用 | 12次 | 9次 | 6次 |
| 错误数 | 2 | 1 | 0 |
| Memory | 无 | 触发写入 | 系统提示词注入 |
| Skill | 触发创建 | 复用+自我修补 | 复用已修补版本 |

**进化路径**：踩坑→提炼→复用→修补→零错误

---

## 三、安全机制

- **Memory 扫描**：检测 prompt injection、欺骗隐藏、系统提示词覆盖、凭证泄露等模式
- **Skill 扫描**：自创和 Hub 安装走同一套扫描，不通过就回滚
- **RDSHermes 增强**：AK/SK 加密托管，网关代理鉴权，密钥不落盘

---

## 四、设计取舍

| 设计决策 | 考量 |
|---------|------|
| Memory 限 2200 chars | 低质量 Memory = 每次 API 调用都带噪声 |
| 事实 vs 步骤分离 | 更新频率、触发条件、安全风险完全不同 |
| 冻结快照 | 保护前缀缓存，避免重复计费 |
| 后台 fork 审查 | 自省不应占用用户 attention budget |
| patch 优先于重写 | 保留已验证部分，只改需要改的 |
| Nudge 默认10 | 太频繁浪费成本，太稀疏错过学习 |

---

## 五、Skill 自动进化的下一步方向

1. **生命周期管理**：加 `last_used`/`use_count`/`success_rate`，自动降权归档
2. **技能组合**：识别经常一起用的 Skill 合成工作流
3. **创建透明度**：创建后给用户简短通知，支持审核纠正
4. **团队治理**：写操作需二次确认，全链路审计

---

## 🔗 借鉴点（可执行）

1. **Memory 容量压缩策略** → 我们系统的 MEMORY 2200/USER 1375 限制已经在用，但可以加"自动合并相似条目"逻辑
2. **Nudge 后台 fork 机制** → 我们的 cron evolver/auto-dream 已经在做类似的事，但可以考虑用后台线程做更细粒度的回合级触发
3. **Skill fuzzy patch** → 我们的 `skill_manage(action='patch')` 已经实现了模糊匹配，继续保持
4. **安全扫描模式** → 我们的 `_MEMORY_THREAT_PATTERNS` 已覆盖，可考虑加"凭证泄露检测"
5. **Skill 生命周期管理** → 可以为 SKILL.md frontmatter 加 `last_used`/`use_count`，实现自动归档

## 🧠 启发（超越原文）

- **"Data Is the Final Moat"**：模型智能被商品化后，真正的护城河是 Agent 在工作中积累的领域知识。这验证了我们 evolver + auto-learner + skill-pipeline 的自进化体系方向是对的。
- **声明式 vs 命令式 Memory**：这个区分很精妙——前者可被上下文覆盖（灵活），后者是死命令（僵化）。我们的 memory 写入规范应该强化这一点。
- **"Skills that aren't maintained become liabilities"**：这也是我们的技能审计 cron 的核心理念，但可以更激进——给每个 skill 加"健康度"评分。

## 📊 预判

- **趋势**：Agent 自进化将从"单点学习"走向"组织级共享"（RDSHermes 已验证），团队级 Skill Hub 会成为标配
- **行动**：持续完善我们的自进化体系，重点关注 Skill 生命周期管理和跨 session 经验共享

## 相关笔记
- [Claude-Code四层记忆架构](2026-04-03-Claude-Code四层记忆架构.md)
- [Hermes-Agent-competitor-analysis](2026-04-05-Hermes-Agent-competitor-analysis.md)
- [4-ai-agent-frameworks-comparison](2026-04-13-4-ai-agent-frameworks-comparison.md)
- [Gemini3-AI-Agent-competition](2026-04-16-Gemini3-AI-Agent-competition.md)
- [Hermes-Agent-v0.10.0-insight](2026-04-18-Hermes-Agent-v0.10.0-insight.md)
- [Hermes-Agent-v0.10.0-release-analysis](2026-04-18-Hermes-Agent-v0.10.0-release-analysis.md)
- [Claude-Opus4.7-Claude-Code-最佳实践](2026-04-20-Claude-Opus4.7-Claude-Code-最佳实践.md)
- [ESP-Claw扩展分析-NeuroClaw边缘AI-Agent](2026-04-22-ESP-Claw扩展分析-NeuroClaw边缘AI-Agent.md)
- [MCP协议与Agentic-LLM-2025趋势](2026-04-23-MCP协议与Agentic-LLM-2025趋势.md)
- [深入源码Hermes-Agent-Self-Improving](2026-04-23-深入源码Hermes-Agent-Self-Improving.md)
- [MCP协议生态与Agentic-RAG架构深度学习](2026-04-27-MCP协议生态与Agentic-RAG架构深度学习.md)
- [LLM-Agent驱动量化交易系统前沿学习](2026-04-29-LLM-Agent驱动量化交易系统前沿学习.md)
- [Meta-Hyperagents自适应Agent框架](2026-04-30-Meta-Hyperagents自适应Agent框架.md)
- [stoc蒸馏-AI-Agent自学习量化交易系统](2026-04-30-stoc蒸馏-AI-Agent自学习量化交易系统.md)
- [AI-Agent记忆架构前沿学习](2026-05-01-AI-Agent记忆架构前沿学习.md)
- [deepseek-agent-ecosystem](2026-05-01-deepseek-agent-ecosystem.md)
- [AI-Agent-Protocol-Ecosystem-2026-学习](2026-05-03-AI-Agent-Protocol-Ecosystem-2026-学习.md)
- [ai-agent-resources-ecosystem](2026-05-03-ai-agent-resources-ecosystem.md)
- [智能教育-自适应评估](2026-05-03-智能教育-自适应评估.md)
- [Agent协议生态2026最新进展-MCP-A2A深度融合](2026-05-04-Agent协议生态2026最新进展-MCP-A2A深度融合.md)
- [个人Agent自进化五步闭环](2026-05-04-个人Agent自进化五步闭环.md)
- [Claude-MCP直连Fusion-Blender-AI操控工业设计](2026-05-05-Claude-MCP直连Fusion-Blender-AI操控工业设计.md)
- [Claude创意连接器9大工具-Blender-MCP深度解析](2026-05-05-Claude创意连接器9大工具-Blender-MCP深度解析.md)
- [Zero-to-CAD-Agent闭环合成百万级可执行CAD程序](2026-05-05-Zero-to-CAD-Agent闭环合成百万级可执行CAD程序.md)
- [tradingagents-deep-analysis](2026-05-05-tradingagents-deep-analysis.md)
- [SOUL-md-Agent-Partner-Transformation](2026-05-07-SOUL-md-Agent-Partner-Transformation.md)
- [Superpowers-Agentic技能框架](2026-05-07-Superpowers-Agentic技能框架.md)
- [AI-Agent控制流](2026-05-08-AI-Agent控制流.md)
- [addyosmani-agent-skills生产级Agent技能包](2026-05-08-addyosmani-agent-skills生产级Agent技能包.md)
- [企业AI转型三步法-知识库技能化智能体](2026-05-08-企业AI转型三步法-知识库技能化智能体.md)
- [AG-UI-AI-Agent前端标准](2026-05-09-AG-UI-AI-Agent前端标准.md)
- [Agent-native-PM方法论](2026-05-09-Agent-native-PM方法论.md)
- [Claude-Code工程师放弃Markdown转HTML](2026-05-09-Claude-Code工程师放弃Markdown转HTML.md)
- [OfficeCLI-AI-Agent的Office工具](2026-05-09-OfficeCLI-AI-Agent的Office工具.md)
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
- [anthropic-managed-agents-dreaming-outcomes](anthropic-managed-agents-dreaming-outcomes.md)
- [智能教育-AI-tutoring](explore/2026-05-05-智能教育-AI-tutoring.md)
- [ai-agent-protocol-stack-2026](explore/2026-05-06-ai-agent-protocol-stack-2026.md)
- [ai-agent-protocol-wars-a2a-mcp](explore/2026-05-08-ai-agent-protocol-wars-a2a-mcp.md)
- [ai-coding-agent-competition-landscape](explore/2026-05-08-ai-coding-agent-competition-landscape.md)
- [2025年5月AI大爆发-Claude4-Qwen3-DeepSeek-R1](explore/2026-05-09-2025年5月AI大爆发-Claude4-Qwen3-DeepSeek-R1.md)
- [ai-agent-protocols-mcp-a2a-acp](explore/2026-05-09-ai-agent-protocols-mcp-a2a-acp.md)
- [开源AI春季爆发-模型推理Agent](explore/2026-05-09-开源AI春季爆发-模型推理Agent.md)
- [mcp-a2a-agent-ecosystem](explore/2026-05-10-mcp-a2a-agent-ecosystem.md)
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
- [具身智能2026数据规模化元年](explore/2026-05-17-具身智能2026数据规模化元年.md)
- [hermes-agent-源码拆解自我进化机制](hermes-agent-源码拆解自我进化机制.md)
- [llm-wiki-gbrain-agent-evolution_33aa818c](llm-wiki-gbrain-agent-evolution_33aa818c.md)
- [AI幻觉案例分析-Hermes-Agent不实报道](orphan/2026-04-19-AI幻觉案例分析-Hermes-Agent不实报道.md)
- [深入源码-Hermes-Agent-Self-Improving源码拆解](orphan/2026-04-24-深入源码-Hermes-Agent-Self-Improving源码拆解.md)
- [智能教育-personalized-learning](orphan/2026-05-04-智能教育-personalized-learning.md)
- [agent-coding-playbook-analysis](orphan/2026-05-05-agent-coding-playbook-analysis.md)
- [具身智能机器人2025年终盘点](orphan/2026-05-05-具身智能机器人2025年终盘点.md)
- [具身智能机器人2025-商业化元年](orphan/2026-05-09-具身智能机器人2025-商业化元年.md)
- [claude-learning-roadmap](orphan/2026-05-10-claude-learning-roadmap.md)
- [0元打通Claude-Codex-OpenCode免费模型6入口](orphan/2026-05-11-0元打通Claude-Codex-OpenCode免费模型6入口.md)
- [HuggingFace-春季生态-Agentic-World-Modeling](orphan/2026-05-13-HuggingFace-春季生态-Agentic-World-Modeling.md)
- [具身智能量产关键年](orphan/2026-05-15-具身智能量产关键年.md)
- [HTML的不合理有效性-Claude-Code-团队](orphan/2026-05-16-HTML的不合理有效性-Claude-Code-团队.md)
- [GenericAgent](orphan/GenericAgent.md)
- [skills-autonomous-ai-agents](skills-autonomous-ai-agents.md)
- [竞品吸收笔记_GenericAgent](竞品吸收笔记_GenericAgent.md)
