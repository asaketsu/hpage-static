# Google 首次发现 AI 生成的零日漏洞：攻击者用 AI 绕过 2FA

> **来源**：Google Threat Intelligence Group · SecurityWeek · CNBC · NYT · 2026-05-11
> **原文**：https://www.securityweek.com/google-detects-first-ai-generated-zero-day-exploit
> **笔记ID**：sniff-20260525-google-ai-zero-day
> **格式**：双格式(MD + HTML) · 含借鉴进化点 · RAG/wiki联动
> **关联**：[AI辅助攻击2026](2026-05-24-AI辅助攻击2026-零日2FA绕过与自主恶意软件生成.html) [Anthropic Project Glasswing](2026-05-23-Anthropic-Project-Glasswing-初始更新-AI安全防御新范式.md) [IBM X-Force 2026](2026-05-24-IBM-X-Force-2026威胁指数-AI驱动攻击升级44.md)

## 摘要

Google Threat Intelligence Group (GTIG) 在 2026 年 5 月发布报告，首次确认发现由 AI 生成的零日漏洞利用代码。一个知名网络犯罪组织使用 AI 模型（包括 OpenClaw）开发了一个针对开源 Web 管理工具的零日漏洞，旨在绕过双因素认证（2FA），并计划进行大规模漏洞利用。Google 在攻击者行动前发现了该漏洞并通知了供应商，成功阻止了大规模攻击。这是 AI 安全攻防从理论威胁变为现实威胁的分水岭。

## 核心内容

### 1. 事件详情

攻击链：
  网络犯罪组织 APT45 使用 AI 模型分析开源软件代码库
  AI 发现了一个未知的身份验证绕过漏洞
  AI 辅助编写了零日漏洞利用代码，可绕过 2FA
  目标是一个广泛使用的开源 Web 管理工具（具体名称未公开）
  计划进行大规模漏洞利用（mass exploitation）

Google 的应对：
  GTIG 在攻击者准备阶段就发现了该漏洞利用代码
  通知了受影响的供应商，协助修补
  在攻击者发起大规模利用前成功阻断

### 2. AI 在攻击中的角色

GTIG 评估认为 AI 在整个过程中发挥了"有意义的"作用：
  漏洞发现：AI 辅助分析代码库，发现人类难以发现的漏洞模式
  漏洞利用代码开发：AI 参与编写绕过 2FA 的利用代码
  攻击规模规划：AI 可能参与规划了大规模利用的执行方案

关键未确认点：GTIG 尚未确定漏洞本身是否也是 AI 发现的（即 AI 是否完成了从漏洞发现到利用的全链条）。

### 3. 行业连锁反应

这一事件引发了连锁反应：
  Anthropic 此前已因安全担忧推迟了 Mythos 模型的发布（2026年4月）
  OpenAI 宣布 GPT-5.5-Cyber 限量预览，仅面向经过审查的网络安全团队
  白宫召开了 AI 网络安全威胁的高层会议
  整个行业开始认真对待"AI 武器化"的威胁

### 4. GTIG 的判断

GTIG 研究人员表示：
  "这可能只是冰山一角"
  "这肯定不会是最后一次"
  AI 生成的漏洞利用代码的质量正在快速提升
  防御方需要同样利用 AI 来检测和响应

## 关键概念

**AI 零日（AI Zero-Day）**：由 AI 模型辅助或完全自主发现的未知漏洞，及其对应的利用代码。区别于传统人工发现的零日。

**2FA 绕过（2FA Bypass）**：绕过双因素认证机制，通常涉及在认证流程中找到逻辑缺陷或会话管理漏洞。

**大规模利用（Mass Exploitation）**：针对大量目标同时发起漏洞利用，区别于针对性攻击。需要自动化工具链支持。

## 能力边界

  本次事件中 Google 是在攻击准备阶段发现的，不代表所有 AI 零日都能被提前发现
  GTIG 未确认 AI 是否独立完成了从漏洞发现到利用的全过程
  攻击者使用的是公开可用的 AI 模型，如果使用更强的专用模型，威胁更大
  防御方目前仍处于被动应对状态

## 最佳实践

  安全团队必须引入 AI 辅助的代码审计工具，以 AI 对抗 AI
  对所有开源依赖进行持续的自动化漏洞扫描
  实施深度防御：即使 2FA 被绕过，也要有后续的检测和响应机制
  建立 AI 安全事件的应急响应预案

## 🔍 借鉴学习进化点（必填）

| # | 点 | 原文要点 | 对当前系统的借鉴 | 行动计划 |
|---|-----|---------|---------------|---------|
| 1 | AI 对抗 AI | 防御方需要同样利用 AI 来检测和响应 | Hermes 的 auto-defense-check 和 Glasswing 式安全扫描可增强防御 | 在 auto-defense-check 中增加对 skill 注入和 prompt 泄露的 AI 辅助检测 |
| 2 | 准备阶段发现 | Google 在攻击者准备阶段就发现了漏洞 | 安全监控不应只关注"已发生"的攻击，还要检测"准备中"的异常 | 为 gateway 日志增加"准备阶段异常模式"检测规则 |
| 3 | 开源依赖的持续审计 | 攻击目标是广泛使用的开源工具 | Hermes 依赖大量开源工具（Python 库、CLI 工具），需持续审计 | 建立 Hermes 依赖的第三方库安全追踪清单 |
| 4 | AI 安全事件预案 | 整个行业需要 AI 安全应急预案 | Hermes 系统本身也需要防范 Agent 被恶意利用 | 制定 Hermes Agent 滥用防护预案，包括 rate-limit 和行为异常检测 |
| 5 | 模型分级访问 | GPT-5.5-Cyber 仅面向审查过的安全团队 | Hermes 的 skill 和 model 访问也应有分级机制 | 在 model-adapter 中增加安全敏感功能的访问控制层 |

## 🔗 RAG / Wiki 联动（必填）

### 当前状态
  已有多篇 AI 安全相关笔记（Glasswing、Domain Camouflaged Injection、AI辅助攻击）
  auto-defense-check skill 实现了基础安全自检
  sniff 队列中网络安全话题已饱和

### 改进方案
1. 建立 AI 安全事件时间线 wiki 页面，追踪从 Mythos 延迟到 AI 零日发现的完整链路
2. 将 AI 零日检测纳入 auto-defense-check 的检查项
3. 设计 Hermes 系统的"AI 安全事件应急响应"预案

### 已执行操作
- ✅ 笔记已写入 bookmarks/notes
- ⏳ AI 安全事件时间线待下次会话创建

## 相关笔记
- [[2026-05-23-Anthropic-Project-Glasswing-初始更新-AI安全防御新范式]] (关键词: anthropic, glasswing, AI安全)
- [[2026-05-24-AI辅助攻击2026-零日2FA绕过与自主恶意软件生成]] (关键词: 零日, 2FA绕过, AI攻击)
- [[2026-05-24-IBM-X-Force-2026威胁指数-AI驱动攻击升级44]] (关键词: IBM, X-Force, 威胁指数)
