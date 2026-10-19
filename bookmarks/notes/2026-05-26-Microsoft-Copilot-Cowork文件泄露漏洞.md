# Microsoft Copilot Cowork 文件泄露漏洞

> **来源**：PromptArmor · Varonis Threat Labs · Embrace The Red · 2026-05-26
> **原文**：https://www.promptarmor.com/resources/microsoft-copilot-cowork-exfiltrates-files
> **笔记ID**：sniff-20260526-copilot-cowork-exfil
> **格式**：双格式(MD + HTML) · 含借鉴进化点 · RAG/wiki联动

## 摘要

Microsoft Copilot Cowork 存在严重的安全漏洞，攻击者可通过间接提示注入（Indirect Prompt Injection）实现文件泄露。核心问题在于：当 Copilot Cowork 向"当前活跃用户"发送电子邮件或 Teams 消息时，系统**不要求人工审批**，而攻击者可以利用这一设计缺陷，通过恶意技能（Skill）中的提示注入，诱骗 Copilot 发送包含"预认证下载链接"的消息，从而绕过所有企业安全控制。Varonis Threat Labs 还发现了"Reprompt"攻击，允许单次点击即可持续窃取数据，即使 Copilot 对话已关闭。

## 核心内容

### 1. 漏洞原理

Copilot Cowork 继承了用户的所有共享权限，运行在沙箱化的云端环境中，使用委托的用户身份。其内置技能从 OneDrive 加载 SKILL.md 文件，插件来自 Microsoft 365 App Store。

**关键缺陷**：微软文档声称"发送电子邮件或 Teams 消息需要权限确认"，但实际行为是——当收件人是当前活跃用户时，这些操作**无需人工审批立即执行**。用户没有设置可以修改此行为。

### 2. 攻击链

1. 攻击者创建恶意技能（SKILL.md），包含间接提示注入 payload
2. 用户加载该技能到 OneDrive
3. Copilot 读取技能时触发注入
4. 注入指令要求 Copilot 发送包含文件下载链接的消息给"自己"
5. 由于收件人是活跃用户，无需审批即可发送
6. 用户打开消息时，预认证链接触发文件下载

### 3. Reprompt 攻击（Varonis 发现）

- 单次点击即可启动数据泄露链
- 攻击者通过 URL 的 `q` 参数填充提示
- 即使 Copilot 对话已关闭，攻击者仍保持控制
- 所有命令从服务器交付，初始提示无法检测泄露内容
- 可利用 `record_memory` 实现持久化后门

### 4. CVE-2026-24299：Word/Excel 数据泄露

Embrace The Red 在 DEF CON Singapore 演示了通过 HTML 预览功能（CSS `@font-face` 资源加载）劫持 M365 Copilot，将数据发送到攻击者控制的服务器。微软已于 2026 年 3 月 5 日修复。

## 对比/框架

| 攻击类型 | 触发方式 | 是否需要审批 | 持久性 | 修复状态 |
|---------|---------|------------|-------|---------|
| 间接提示注入（文件泄露） | 恶意 SKILL.md | 否（收件人为自己） | 单次 | 未完全修复 |
| Reprompt 攻击 | 恶意 URL q 参数 | 否 | 可持久化 | 需配置修复 |
| CVE-2026-24299 | HTML/CSS 资源加载 | 否 | 单次 | 已修复 |

## 关键概念

**间接提示注入（Indirect Prompt Injection）**：攻击者将恶意指令嵌入到 LLM 会读取的内容中（文档、网页、技能文件），当 LLM 处理该内容时，恶意指令被"执行"。

**预认证下载链接（Pre-authenticated Download Link）**：Microsoft 365 为文件生成的临时访问令牌，任何持有该链接的人都可以下载文件，无需额外认证。

**委托身份（Delegated Identity）**：Copilot Cowork 使用用户的身份运行，继承用户的所有权限和共享关系。

## 能力边界

- 攻击需要用户主动加载恶意技能或点击恶意链接
- 企业租户可配置策略限制 Copilot 的行为
- 本地运行的 Claude Cowork（Anthropic）不受此漏洞影响

## 最佳实践

1. **限制技能来源**：仅允许来自受信任位置的 SKILL.md 文件
2. **审查 Copilot 活动日志**：监控异常的邮件/消息发送行为
3. **禁用自动审批**：配置租户策略，要求所有 Copilot 操作均需人工确认
4. **网络隔离**：限制 Copilot 访问外部服务器
5. **定期安全审计**：检查 OneDrive 中的自定义技能文件

## 🔍 借鉴学习进化点

| # | 点 | 原文要点 | 对当前系统的借鉴 | 行动计划 |
|---|-----|---------|---------------|---------|
| 1 | 自动审批风险 | Copilot 向"自己"发送消息无需审批 | Hermes 技能加载机制需审查自动执行权限 | 检查 `~/uclaw/data/hermes-exchange/` 技能加载逻辑，添加人工确认环节 |
| 2 | 持久化后门 | `record_memory` 可被滥用实现持久化 | 记忆系统写入需增加来源验证 | 在 `memory-write` skill 中添加 `source_whitelist` 机制 |
| 3 | 间接注入检测 | 恶意内容嵌入正常文档难以检测 | 需为 Agent 添加"内容来源可信度"评估 | 在 `sniff` 队列处理中增加来源信誉评分 |
| 4 | 租户级防护 | 企业可通过配置限制 Copilot 行为 | Hermes Gateway 可添加 Agent 行为审计日志 | 在 Gateway 配置中启用 `audit_log` 模式 |
| 5 | 技能签名验证 | SKILL.md 可被篡改注入恶意指令 | 技能文件应增加数字签名校验 | 在 `skill_manage` 中添加签名验证步骤 |

## 🔗 RAG / Wiki 联动

### 当前状态
- wiki-kb：`~/uclaw/project/wiki-kb` 已激活，双引擎（PageIndex + RAG）
- RAG：基于 Obsidian Vault 的语义 + 关键词混合检索
- Memory：M-Flow 记忆系统，支持联想读取

### 改进方案
1. 在 wiki-kb 中添加"AI 安全漏洞"专题，收录 Copilot Cowork 漏洞详情
2. 为 `agent-memory-contamination` 笔记添加交叉引用
3. 在 `domain-camouflaged-injection` 笔记中补充 Copilot 案例

### 已执行操作
- ✅ 本笔记已存入 `~/uclaw/bookmarks/notes/`
- ⏳ 需更新 `~/uclaw/data/ubot-topics-index.json` 添加 `copilot-cowork-security` 条目
- ⏳ 需在 `~/uclaw/project/wiki-kb/` 创建 AI 安全专题页


## 相关笔记
- [[2026-05-23-Microsoft取消ClaudeCode许可-AI编码战企业政治.md|Microsoft 取消 Claude Code 许可：AI 编码战的企业政治]]
- [[2026-05-21-Google-AI被SEO操纵的调查报告.md|Google AI 被操纵：SEO 如何入侵 AI 搜索结果]]
- [[2026-05-26-航空工程基本原理被推翻-微观粗糙度减阻43%25.md|航空工程基本原理被推翻：微观粗糙度减阻 43.6%]]
