# OpenHuman — 通过记忆树记住你全部的AI智能体

> **来源**：i龙虾 · 微信公众号 · 2026-05-17
> **原文**：https://mp.weixin.qq.com/s/hntFcRtJoA4QsOJ0skRMtA
> **GitHub**：https://github.com/tinyhumansai/openhuman
> **官网**：https://tinyhumans.ai/openhuman

## 一句话

TinyHumans 团队的开源个人AI超级智能体，核心创新是**记忆树（Memory Tree）**— 自动抓取118+服务的个人数据，组织成树状记忆空间（最大10亿token），兼容Obsidian可编辑可审计。

## 核心机制

**记忆树（Memory Tree）**
- 接入 Gmail/Notion/GitHub/Slack/日历等 118+ 服务（OAuth一键授权）
- 数据统一转 Markdown，切成 ≤3000 token 片段，按来源+主题组织成树状结构
- 存本地 SQLite，同步成 .md 文件放 Obsidian 兼容目录
- 每 20 分钟自动预取（别人等你问，它提前准备好）
- 灵感来自 Karpathy 的 Obsidian + AI 笔记工作流

**TokenJuice 压缩层**
- HTML→Markdown、长URL缩短、非ASCII清理，最多减少80% token消耗
- 内置模型路由：推理→重型模型，简单→快速模型，视觉→视觉模型

**Tiny 桌面宠物**
- 可作为真实参与者加入 Google Meet 通话
- 实时监听+记笔记+ElevenLabs TTS回应+口型同步

## 技术栈

Rust + Tauri + TypeScript | GNU GPL3 | SQLite 本地存储 | 支持 macOS/Windows/Linux

## 竞品对比（原文数据，有立场偏向）

| 维度 | Claude Cowork | OpenClaw | Hermes Agent | OpenHuman |
|------|--------------|----------|--------------|-----------|
| 记忆机制 | 对话范围 | 依赖插件 | 自学习 | 记忆树+Obsidian |
| 集成数量 | 少量 | 自己接 | 自己接 | 118+ OAuth |
| 自动抓取 | 无 | 无 | 无 | 每20分钟 |
| 模型路由 | 单模型 | 手动 | 手动 | 内置 |
| 上手难度 | 简单 | 需终端 | 需终端 | GUI几分钟 |

## 关键洞察

1. **"AI不缺能力，缺的是对人的持续理解"** — 这是方向押注
2. **透明度优于黑箱** — 记忆树可打开文件夹看AI记住了什么，可手动改
3. **预取 vs 按需** — 别人等你发问再查，OpenHuman提前20分钟准备好
4. **隐私风险** — 大量个人数据（邮件/日历/聊天）授权给Beta工具，需审慎

## 对Hermes的借鉴点

| 借鉴方向 | 说明 |
|----------|------|
| 记忆树分层 | Hermes的记忆是flat的MEMORY.md，可考虑按来源+主题组织 |
| 自动预取 | Hermes的knowledge-fusion已有5源扫描，但不是20分钟级实时 |
| Obsidian兼容 | Hermes的WikiKB已有PageIndex树，但缺用户可编辑的反向同步 |
| Token压缩 | Hermes的context-compressor已有，TokenJuice思路可参考 |
| 模型路由 | Hermes的model-adapter已有smart routing，比OpenHuman更灵活 |

## 风险与不足

- Beta阶段，Issues 里 Bug 未消化完
- 118个集成=118个攻击面，OAuth token管理是安全挑战
- 本地存储 ≠ 绝对隔离，需审隐私政策
- GNU GPL3 对商业使用有限制

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
- [hermes-agent-源码拆解自我进化机制](hermes-agent-源码拆解自我进化机制.md)
- [llm-wiki-gbrain-agent-evolution_33aa818c](llm-wiki-gbrain-agent-evolution_33aa818c.md)
- [0元打通Claude-Codex-OpenCode免费模型6入口](orphan/2026-05-11-0元打通Claude-Codex-OpenCode免费模型6入口.md)
- [HuggingFace-春季生态-Agentic-World-Modeling](orphan/2026-05-13-HuggingFace-春季生态-Agentic-World-Modeling.md)
- [具身智能量产关键年](orphan/2026-05-15-具身智能量产关键年.md)
- [HTML的不合理有效性-Claude-Code-团队](orphan/2026-05-16-HTML的不合理有效性-Claude-Code-团队.md)
