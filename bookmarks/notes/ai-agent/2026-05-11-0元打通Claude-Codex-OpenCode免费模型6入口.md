# 0元打通Claude + Codex + OpenCode：一个免费模型，6个入口，20分钟搞定

> 来源：[@雨哥向前冲](https://x.com/xiangxiang103/status/2053431793483960656) · 2026-05-10
> 互动：37回复 / 32转发 / 95赞 / 153收藏

## 核心方案

用 **CC Switch + OpenRouter** 跑通，模型是 OpenRouter 上的 **Ring-2.6-1T**（免费版）。

### 免费模型：Ring-2.6-1T (InclusionAI/蚂蚁百灵)

| 属性 | 说明 |
|------|------|
| 来源 | 蚂蚁百灵大模型 |
| 模型ID | `inclusionai/ring-2.6-1t:free` |
| 日限额 | 50次/天（免费），充值≥$10 → 1000次/天 |
| 速率 | 20次/分钟 |
| 特点 | 知识储备足、思考维度深、输出质量高、响应偏慢 |
| 免费token | 每人每日50万token，02:00前发放 |
| 定位 | 复杂任务主模型（vs 快速小模型处理简单任务） |

### 6个入口

Claude CLI + Claude Desktop + Codex CLI + Codex Desktop + OpenCode CLI + OpenCode Desktop

### 核心工具：CC Switch

一键切换 API 提供商的可视化管理工具，不用手动改配置文件。

## 步骤概要

1. **准备OpenRouter Key** — 注册 openrouter.ai，获取API Key
2. **安装CC Switch** — 可视化管理工具
3. **OpenCode接入** — CC Switch的OpenCode页面配置OpenRouter，手动填模型名 `inclusionai/ring-2.6-1t:free`，回桌面端选模型
4. **Claude接入** — CC Switch配置
5. **Codex接入** — CC Switch配置
6. **验证结果** — 确认6个入口全部通

> 小技巧：配置好一个直接复制，编辑粘贴模型ID，点"一键设置"

## 我的点评

**实用度：⭐⭐⭐⭐/5**

- ✅ 价值点：零成本体验 Claude Code 级编程，蚂蚁百灵模型确实能打
- ✅ 教程清晰，CC Switch 降低了配置门槛
- ⚠️ 免费额度 50次/天偏少，重度使用需充值$10
- ⚠️ Ring-2.6-1T 响应速度偏慢，复杂任务OK但不适合高频简单任务
- 💡 与之前笔记"AI省钱"思路呼应：简单活给免费小模型，主力模型只做高价值活

## 标签

`#AI工具` `#Claude` `#Codex` `#OpenCode` `#OpenRouter` `#免费模型` `#CC-Switch` `#蚂蚁百灵` `#AI编程` `#零成本`

## 相关笔记
- [AI趋势2026-推理时计算与反思Agent](../2026-05-11-AI趋势2026-推理时计算与反思Agent.md)
- [具身智能2026-世界模型VLA车企入局](../2026-05-11-具身智能2026-世界模型VLA车企入局.md)
- [具身智能2026从实验到实战](../2026-05-11-具身智能2026从实验到实战.md)
- [Claude-3D-CAD-创意连接器深度分析](../2026-05-13-Claude-3D-CAD-创意连接器深度分析.md)
- [Agent工程4月实践-不要一上来就做Agent](../2026-05-14-Agent工程4月实践-不要一上来就做Agent.md)
- [HTML-Anything-Agent驱动HTML编辑器](../2026-05-14-HTML-Anything-Agent驱动HTML编辑器.md)
- [MATLAB-Agentic-Toolkit分析](../2026-05-14-MATLAB-Agentic-Toolkit分析.md)
- [手撸Agent-ReAct-Loop从零实现](../2026-05-14-手撸Agent-ReAct-Loop从零实现.md)
- [上下文才是Agent的命门-QClaw上下文竞争论](../2026-05-15-上下文才是Agent的命门-QClaw上下文竞争论.md)
- [OpenHuman-记忆树AI智能体-i龙虾](../2026-05-16-OpenHuman-记忆树AI智能体-i龙虾.md)
- [PicoClaw-超轻量AI-Agent框架](../2026-05-16-PicoClaw-超轻量AI-Agent框架.md)
- [具身智能前沿学习](../2026-05-17-具身智能前沿学习.md)
- [20260513-llm-wiki-obsidian-gbrain-知识自组织与自进化](../20260513-llm-wiki-obsidian-gbrain-知识自组织与自进化.md)
- [ai-agent-protocols-mcp-a2a](../explore/2026-05-11-ai-agent-protocols-mcp-a2a.md)
- [AI-Agent架构-MCP-A2A协议栈](../explore/2026-05-13-AI-Agent架构-MCP-A2A协议栈.md)
- [Agentic-SOC-安全自动化的范式转变](../explore/2026-05-13-Agentic-SOC-安全自动化的范式转变.md)
- [Agentic-Engineering-从Vibe-Coding到Agent工程](../explore/2026-05-14-Agentic-Engineering-从Vibe-Coding到Agent工程.md)
- [ai-agent-architecture](../explore/2026-05-15-ai-agent-architecture.md)
- [ai开源生态-huggingface春季](../explore/2026-05-15-ai开源生态-huggingface春季.md)
- [AI-Agent-协议生态-深度整合学习](../explore/2026-05-16-AI-Agent-协议生态-深度整合学习.md)
- [Agentic-AI元年-智能体全面落地趋势](../explore/2026-05-16-Agentic-AI元年-智能体全面落地趋势.md)
- [HuggingFace-Spring2026-开源生态报告](../explore/2026-05-16-HuggingFace-Spring2026-开源生态报告.md)
- [qclaw-上下文四层模型](../explore/2026-05-16-qclaw-上下文四层模型.md)
- [具身智能-从造产品到抢落地六大趋势](../explore/2026-05-16-具身智能-从造产品到抢落地六大趋势.md)
- [竞品动态-Agentic-Engineering范式转变](../explore/2026-05-16-竞品动态-Agentic-Engineering范式转变.md)
- [agent-collaboration-self-evolution](../explore/2026-05-17-agent-collaboration-self-evolution.md)
- [hermes-agent-源码拆解自我进化机制](../hermes-agent-源码拆解自我进化机制.md)
- [llm-wiki-gbrain-agent-evolution_33aa818c](../llm-wiki-gbrain-agent-evolution_33aa818c.md)
- [HuggingFace-春季生态-Agentic-World-Modeling](2026-05-13-HuggingFace-春季生态-Agentic-World-Modeling.md)
- [具身智能量产关键年](2026-05-15-具身智能量产关键年.md)
- [HTML的不合理有效性-Claude-Code-团队](2026-05-16-HTML的不合理有效性-Claude-Code-团队.md)
