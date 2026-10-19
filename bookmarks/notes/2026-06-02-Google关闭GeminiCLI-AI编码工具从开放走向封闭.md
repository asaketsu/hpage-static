# Google 关闭 Gemini CLI：AI 编码工具从开放走向封闭

来源：The Register / HN / Reddit
链接：https://www.theregister.com/ai-ml/2026/05/20/bye-bye-gemini-cli-google-nudges-devs-toward-antigravity/5243605
日期：2026-06-02
评分：⭐4/5
标签：#AI编码 #GeminiCLI #Antigravity #Google #开源 #开发者工具

关联：[AI编码工具战争](2026-05-24-AI编码工具战争-CodexClaudeCodeCursor收敛为分层架构.md) [Antigravity2.0](2026-05-23-Antigravity2.0-OpenSCAD-LLM-Benchmark-AI编程3D建模能力.md)

## 事件概述

Google 宣布 2026 年 6 月 18 日正式关闭 Gemini CLI 和 Gemini Code Assist IDE 扩展，取而代之的是 I/O 2026 发布的 Antigravity CLI。这个决定在开发者社区引发巨大争议——Gemini CLI 是开源的，而 Antigravity CLI 远比其封闭。

## 时间线

- 2025年：Gemini CLI 发布，迅速获得开发者社区好评，开源、免费
- 2026年5月 I/O：Google 发布 Antigravity CLI，号称"统一命令行 AI 代理"
- 2026年5月20日：宣布 Gemini CLI 6月18日停止服务
- 2026年6月18日（即将）：Gemini CLI 和 Code Assist IDE 扩展正式下线

## 核心争议

1. 开源变封闭：Gemini CLI 是开源项目，Antigravity CLI 的开放程度远低于前者。开发者社区普遍感到被背叛。

2. 强制迁移：Google AI Pro、Ultra 用户以及免费用户全部被强制迁移，没有选择余地。

3. 配额共享问题：Antigravity CLI 与 Google AI Studio 共享配额，开发者担心编码消耗会挤占其他用途的配额。

4. VSCode 扩展命运未卜：社区在 Google AI 论坛追问 VSCode 扩展是否会保留，Google 未给出明确答案。

## 技术变化

Antigravity CLI 新特性：
- 多代理环境支持（官方主推理由）
- 后台任务管理（/btw 命令，不阻塞终端）
- 1400+ 预置 Agent Skills
- 上下文查看（/context 命令）
- 模型不锁定 Gemini（/model 命令可切换）

但缺失的：
- 开源代码
- 社区贡献机制
- 透明度

## 借鉴进化点

1. ⚡ 开源工具的战略风险：Google 用开源 Gemini CLI 获取用户和社区信任，然后用封闭产品替代。这印证了"开源是获客手段而非信仰"的商业逻辑。对于依赖第三方工具的 Agent 系统（如我们的 Hermes），需要建立"工具替代预案"——每个关键外部依赖都应有 Plan B。

2. ⚡ AI 编码工具正在收敛：Gemini CLI → Antigravity、Codex CLI、Claude Code、Cursor 都在走向"编排/执行/审核"的分层架构。我们之前的分析（2026-05-24 笔记）被进一步验证。下一个分化点不在工具本身，而在"谁拥有 Agent 的工作流数据"。

3. ⚡ 配额池化是新博弈场：Google 将 CLI 配额与 AI Studio 池化，意味着开发者的编码消费会影响其研究/实验配额。这是一种隐形的"AI 税"——用免费工具吸引你，用配额限制锁定你。AI Agent 的资源管理策略需要考虑这种跨场景配额竞争。

## 行业格局影响

这个事件标志着 AI 编码工具进入"平台锁定"阶段：
- Google：Gemini CLI (开源) → Antigravity (封闭) = 收网
- Anthropic：Claude Code 持续开放，但收购 Stainless 暗示 SDK 控制意图
- OpenAI：Codex CLI 封闭但功能强大
- 独立工具（Cursor、Windsurf）：夹在大厂之间，差异化越来越难

开发者的选择空间在缩小，而不是扩大。

## 相关笔记
- [开源3D_设计AI-Antigravity](explore/2026-05-28-开源3D_设计AI-Antigravity.md)
- [Antigravity 模型支持测试结果 2026-05-28](Antigravity 模型支持测试结果 2026-05-28.md)
- [MCP已死-CLI-First策略与Skills模式回归](2026-05-30-MCP已死-CLI-First策略与Skills模式回归.md)
