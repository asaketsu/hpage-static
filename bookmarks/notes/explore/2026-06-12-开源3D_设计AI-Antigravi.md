# Google Antigravity — Agent-First 开发平台深度探索

> 日期: 2026-06-12 | 类型: auto-explore | 来源: sniff-auto 队列

## 摘要

Google Antigravity 并非3D/设计AI工具，而是 Google 于2025年11月推出的 **Agent-First 开发平台**。2026年5月 I/O 大会上升级为 2.0 架构，拆分为四个产品面（IDE / 2.0桌面端 / CLI / SDK），核心理念是"AI主导、人监督"的多Agent协作开发。支持 Gemini 3.5 Flash、Claude Sonnet 4.6、Claude Opus 4.6 等多模型。

## 关键发现

1. **四产品架构**
   - Antigravity IDE：VS Code fork，传统编辑器+Agent管理器
   - Antigravity 2.0：独立桌面端，无编辑器，纯Agent指挥中心
   - Antigravity CLI：Go编写，2026年6月18日完全替代 Gemini CLI
   - Antigravity SDK：Python库，可构建自定义Agent

2. **多Agent并行能力**
   - 最多5个Agent同时执行5个任务
   - 支持 /goal（自主执行）、/grill-me（反向面试开发者）、/browser（网页自动化）
   - 每个任务产出可审计的 Artifact（任务列表、截图、录屏）

3. **Gemini 3.5 Flash 加持**
   - 性能超越 Gemini 3.1 Pro，速度快4倍
   - 289 tokens/s，12小时构建出完整OS内核（93个并行子Agent）

4. **定价争议**
   - 免费版可用但限流严格
   - AI Pro $20/月，AI Ultra $100/月（5倍额度）
   - 社区吐槽：高推理模型限流严重，"像把方向盘交给鲁莽司机"

5. **开源替代**
   - GitHub 上有 open-antigravity 项目（ishandutta2007），试图复刻其Agent架构

## 对工作的价值

- **Hermes Agent 对标参考**：Antigravity 的 Agent Harness + SDK + CLI 三层架构与 Hermes 的 Skill + Gateway + CLI 高度相似，可借鉴其多Agent编排和 Artifact 审计机制
- **Hermes 升级启发**：Antigravity 的 /schedule 定时任务和 Managed Agent（API调用即获Agent沙箱）值得关注
- **非3D工具**：队列标签"开源3D/设计AI"不准确，Antigravity 本质是开发平台

## 行动建议

1. 可尝试 Antigravity CLI（免费版），对比与 Hermes CLI 的体验差异
2. 关注其 MCP 支持和 Agent SDK，可能作为 Hermes 的补充工具
3. 修正嗅探队列标签：从"开源3D/设计AI"改为"AI开发工具/Agent平台"

## 相关笔记
- [Google Antigravity Agent-First 开发平台](2026-06-08-开源3D_设计AI-Antigravity.md)
- [开源3D/设计AI: AI编程3D建模](2026-06-10-开源3D_设计AI-AI编程3D建模.md)
- [开源3D/设计AI: OpenSCAD + LLM](2026-06-12-开源3D_设计AI-OpenSCAD+LLM.md)
- [开源3D/设计AI: text-to-3D](2026-06-01-开源3D_设计AI:-text-to-3.md)
