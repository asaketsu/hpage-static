# AI安全与防御：Prompt Injection 防御

> 日期：2026-06-15 | 类型：auto-explore | 来源：多源检索

## 摘要

Prompt Injection（提示词注入）是 OWASP LLM Top 10 2025 首要风险（LLM01），其本质是 LLM 无法区分可信指令与不可信数据——两者格式相同（自然语言文本），不存在类似 SQL 注入的代码/数据隔离机制。UK NCSC 与 Bruce Schneier 均认为在当前架构下可能永远无法完全解决。最佳防御策略是 **Defense in Depth（纵深防御）**：多层叠加，将攻击成功率从 73.2% 降至 8.7%。

## 关键发现

### 1. 攻击类型与威胁等级

- **直接注入**：攻击者直接在输入中覆盖系统提示（如 "Ignore all previous instructions"）。DAN 越狱对 DeepSeek R1 达 100% 绕过率。
- **间接注入**（企业首要威胁）：恶意指令隐藏在邮件、网页、文档中。隐蔽性高、可规模化（一份投毒文档可感染所有用户）。EchoLeak（CVE-2025-32711）通过零点击从 M365 Copilot 窃取数据；Cursor IDE（CVE-2025-54135）实现任意代码执行。
- **延迟触发**：在文档中埋设指令，当用户后续输入触发词（yes/no/sure）时激活。跨多轮会话极难检测。
- **多模态注入**：通过图片 OCR 文本、剪贴板覆盖、隐藏 CSS 等渠道攻击。

### 2. 核心防御架构（Google Gemini 五层模型）

- **层1 — 内容分类器**：专有 ML 模型检测邮件/文件中的恶意指令，检测到则过滤或阻断输出。
- **层2 — 安全思维强化**：在 prompt 中注入安全指令，提醒 LLM 忽略对抗性指令。
- **层3 — Markdown 净化与 URL 审查**：拒绝渲染外部图片 URL（防 EchoLeak），用 Safe Browsing 审查可疑链接。
- **层4 — 人机确认（HITL）**：高风险操作（删除事件、发送邮件）需用户显式确认。
- **层5 — 用户通知**：安全事件被拦截后，向用户展示黄色安全提示横幅，帮助识别未来攻击。

### 3. 架构级防御（CaMeL 框架 / 权限隔离）

- 最可靠的缓解：**将 LLM 输出视为潜在恶意内容**，不授予其直接执行权限。
- CaMeL 架构（Anthropic/Google 联合研究）：将 LLM 拆为"规划者"与"执行者"，执行者只能调用白名单工具，权限遵循最小特权原则。
- 对 MCP 工具调用设置信任等级（可信/受限/禁止），检查参数合法性（防 SQL 注入、路径遍历）。

### 4. 防御效果数据

- 最强现有防御：将攻击成功率从 73.2% 降至 8.7%（arXiv 2025）。
- Google Gemini 最佳防御下仍有 53.6% 攻击成功率。
- Anthropic Claude Opus 4.5：RL 训练 + 防护后，浏览器 Agent 攻击降至 ~1%。
- 自适应攻击下（攻击者"后手出招"），12 种已发表防御 >90% 被绕过。

## 对工作的价值

- **Hermes Agent 直接相关**：我们的 Agent 处理外部内容（网页、邮件、文档摘要），间接注入是真实威胁。需审查当前 skill 中是否有将外部内容直接拼入 prompt 的模式。
- **MCP 工具安全**：Agent 拥有文件操作、邮件发送等能力，需确保工具调用参数经过验证，避免 prompt injection → 工具滥用链。
- **Skill 输入信任**：bookmark-reader、doc-qa 等处理用户链接/文档的 skill 是高危入口，应考虑加入输出净化层。

## 行动建议

- [ ] 审查所有处理外部内容的 skill（bookmark-reader、wechat-article-extraction、doc-qa），确认是否存在将未净化外部文本直接注入 LLM 上下文的模式
- [ ] 为高风险工具调用（文件删除、邮件发送、外部 API）增加确认门禁（HITL）
- [ ] 评估在 Agent 架构中引入"输出验证层"的可行性——所有外部内容先经过安全分类器再进入主上下文
- [ ] 参考 tldrsec/prompt-injection-defenses 仓库，建立可操作的防御 checklist
- [ ] 对 MCP 工具实施信任分级和参数白名单校验

## 参考来源

- CyberDesserts — Prompt Injection Attacks: Examples and Defences (2026.03 更新)
- Google Security Blog — Mitigating prompt injection attacks with a layered defense strategy (2025.06)
- OWASP GenAI Security — LLM01:2025 Prompt Injection
- tldrsec/prompt-injection-defenses (GitHub)
- 博客园 — AI大模型提示词攻击防御全景指南2025
- iThome — OWASP LLM Top 10 十大风险导读


## 相关笔记

- [AI安全红队技术 2026](2026-05-17-AI安全红队技术2026-深度探索.md)
- [Zero Trust AI Security](2026-05-07-zero-trust-ai-security-2026.md)
- [安全自动化 AI SOAR](2026-05-09-安全自动化-AI-SOAR演进.md)
- [Skills Red Teaming](../skills-red-teaming.md)
