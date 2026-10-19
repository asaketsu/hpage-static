# GenericAgent 竞品吸收笔记

> 来源：https://github.com/lsdefine/GenericAgent | 7.9K ⭐ | MIT | 2026-04-30 分析

## 一、项目定位

GenericAgent 是一个极简自进化 Agent 框架，核心仅 ~3K 行 Python 代码。通过 9 个原子工具 + ~100 行 Agent Loop，赋予任何 LLM 对本地计算机的系统级控制能力。

核心理念：**不预装技能——让技能进化出来**。每次解决新任务时，自动将执行路径结晶为可复用的技能文件（SOP），形成个人专属技能树。

## 二、架构分析

### 代码结构（极简）

```
GenericAgent/
├── agent_loop.py       (6.6KB) — Agent Loop 核心，~100行
├── ga.py               (33KB)  — 9 个原子工具实现 + Handler
├── llmcore.py          (55KB)  — LLM 多后端适配层
├── agentmain.py        (15KB)  — 主入口 + 任务调度
├── simphtml.py         (42KB)  — HTML 简化引擎
├── TMWebDriver.py      (15KB)  — 浏览器 CDP 驱动
├── memory/             — 四层记忆体系（L0~L4）
├── frontends/          — 多前端（TG/QQ/微信/钉钉/飞书/Qt）
└── assets/             — Prompt 模板 + 工具 Schema
```

### Agent Loop 核心设计（agent_loop.py）

```
messages → LLM.chat() → 解析 tool_calls → handler.dispatch() → StepOutcome → 下一轮
```

关键机制：
1. **StepOutcome** 数据类：`data + next_prompt + should_exit` — 每个工具返回三件套
2. **BaseHandler** 基类：`do_{tool_name}` 约定 → 自动路由到工具方法
3. **Generator 协程**：整个 loop 是 generator，支持流式输出
4. **turn_end_callback**：每轮结束后注入 working memory、安全护栏、自动记忆提醒

### 9 个原子工具

| 工具 | 功能 | 设计亮点 |
|------|------|----------|
| code_run | 执行 Python/Shell | 文件模式 + 流式输出 + 超时/中断 |
| file_read | 读文件 | 模糊搜索 + 相似文件推荐 + 行号 |
| file_patch | 精确替换 | 唯一性校验 + `{{file:路径:行:行}}` 引用展开 |
| file_write | 写文件 | `<file_content>` 标签提取 + 模式覆盖/追加/前置 |
| web_scan | 浏览器内容扫描 | HTML 简化 + 标签页管理 |
| web_execute_js | JS 执行 | 完全控制浏览器 + 结果可存文件 |
| ask_user | 请求用户输入 | 中断当前任务等待回复 |
| update_working_checkpoint | 更新工作记忆 | key_info + related_sop 双字段 |
| start_long_term_update | 触发长期记忆结算 | 读取 SOP → 最小化更新记忆库 |

### 四层记忆体系

| 层级 | 存储 | 内容 | 生命周期 |
|------|------|------|----------|
| L0 | SOP 文件（MD） | 操作规程、流程文档 | 永久 |
| L1 | global_mem.txt | 环境事实、用户偏好 | 永久 |
| L2 | global_mem_insight.txt | 从 L1 压缩的洞察摘要 | 永久 |
| L3 | 工作记忆（working dict） | 当前任务 key_info + related_sop | 会话级 |
| L4 | raw_sessions/ | 原始会话归档 | 永久 |

记忆管理 SOP：工具 `start_long_term_update` 触发结算 → agent 读取 memory_management_sop.md → 最小化更新 L1/L2 → 避免信息膨胀。

### Token 效率设计

1. **每 10 轮重置工具描述**（`client.last_tools = ''`），避免上下文膨胀
2. **compress_history_tags**：每 5 轮压缩历史中的 `<thinking>/<tool_use>` 标签
3. **Working Memory 注入**：只注入最近 40 条历史摘要，不全量
4. **HTML 简化**（simphtml.py）：35K 字符上限，过滤边栏/浮窗
5. **smart_format**：超长输出中间截断，只保留头尾

### 安全护栏

1. **每 7 轮注入 `[DANGER]`** — 提醒禁止无效重试
2. **每 65 轮强制 ask_user** — 防止无限循环
3. **Plan 模式验证拦截** — 声称完成前必须执行 `[VERIFY]`
4. **代码块检测** — 大代码块未调工具时要求确认

## 三、与我们系统的对比

| 维度 | GenericAgent | Hermes (猫仔) |
|------|-------------|---------------|
| 核心代码量 | ~3K 行 | ~50K+ 行 (含 Skills) |
| 记忆体系 | L0~L4 文件系统 | memory tool + Skills + M-Flow |
| 技能进化 | SOP 文件自结晶 | SKILL.md 规范化 |
| 工具数量 | 9 个原子工具 | 100+ Skills 分层 |
| 前端 | TG/QQ/微信/钉钉/飞书/Qt | 飞书/微信 |
| LLM 支持 | Claude/Gemini/Kimi/MiniMax/OpenAI | GLM-5.1 + 多模型 |
| 浏览器控制 | CDP 注入真实浏览器 | browser tool (Playwright) |
| Token 优化 | 历史压缩 + 工具重置 | context-compressor skill |
| 自进化 | 核心卖点，SOP 自动沉淀 | evolver + skill_manage |

## 四、可借鉴模式（高价值）

### 1. StepOutcome 三件套模式
每个工具返回 `data + next_prompt + should_exit`，Agent Loop 根据这三件套自动决定下一步。**简洁优雅，我们目前没有这个模式。**

### 2. do_{tool_name} 约定路由
Handler 中方法名 `do_xxx` 直接映射到工具名 `xxx`，零配置路由。比我们的 skill 系统更轻量。

### 3. Generator 协程流式输出
Agent Loop 整体是 generator，工具内部也是 generator（yield 中间状态），支持流式输出 + 嵌套 yield from。

### 4. 文件引用展开 `{{file:path:start:end}}`
file_patch 工具支持在参数中引用外部文件片段，避免大段内容直接传入参数。

### 5. 反射模式（--reflect）
加载外部 check() 函数，定时轮询触发任务。类似我们的 cron 但更灵活（热加载脚本）。

### 6. 工作记忆双字段（key_info + related_sop）
简洁的工作记忆模型：只记"关键信息"和"相关 SOP 路径"，每轮注入 prompt。

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
- [深入源码-Hermes-Agent-如何实现Self-Improving](2026-04-23-深入源码-Hermes-Agent-如何实现Self-Improving.md)
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
