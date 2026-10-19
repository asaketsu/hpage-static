# VSCode 一键窃取 GitHub Token：供应链攻击新范式

> **来源**：Ammar Askar Blog / HN #1 (546 pts) / Reddit r/netsec · 2026-06-01
> **原文**：https://blog.ammaraskar.com/github-token-stealing/
> **笔记ID**：vscode-github-token-stealing-20260603
> **格式**：双格式(MD + HTML) · 含借鉴进化点 · RAG/wiki联动

## 摘要

安全研究员 Ammar Askar 披露了一种通过 VSCode 漏洞一键窃取 GitHub Token 的攻击方法（HN 546 pts）。这发生在 TeamPCP 组织通过恶意 Nx Console VSCode 扩展入侵 GitHub 内部（3800 仓库泄露）的大背景下。攻击链展示了从浏览器漏洞到 VSCode 扩展 Marketplace 信任链的完整攻击面，揭示了开发工具供应链安全的系统性风险。

## 核心内容

### 新漏洞：1-Click GitHub Token Stealing

HN 热度第一（546 pts），通过 VSCode 的特定 bug 实现：
  攻击者构造恶意链接/页面
  VSCode 漏洞允许跨站请求窃取已存储的 GitHub Token
  一次点击即可获得完整的仓库访问权限

### 背景：TeamPCP GitHub 入侵事件

2026年5月的更大背景：
  攻击组织：TeamPCP
  攻击向量：恶意 Nx Console (nrwl.angular-console) v18.95.0 扩展
  攻击窗口：18 分钟（5月18日 12:36 UTC 上传）
  影响：约 3800 个 GitHub 内部仓库被克隆
  攻击链：VSCode Marketplace → 自动更新 → 员工设备 → GitHub 内部代码

### 攻击面分析

VSCode 扩展生态的三个核心风险：
  1. 自动更新机制（1秒延迟后自动安装新版扩展）
  2. Marketplace 验证不充分（verified publisher badge 不等于安全）
  3. 扩展权限模型过于宽松（可访问文件系统、网络、token）

### 已披露的类似攻击

  AsyncAPI npm 和 OpenVSX 发布 token 被盗
  durabletask PyPI 包被植入恶意代码
  codexui-android npm 供应链攻击窃取 OpenAI Codex 认证 token

## 关键概念

Supply Chain Attack on Developer Tools：攻击者不直接攻击目标系统，而是通过开发者日常使用的工具（IDE 扩展、npm 包、CI/CD actions）渗透。

Extension Auto-Update Exploitation：VSCode 的自动更新机制（eventuallyAutoUpdateExtensions）在扩展发布新版后 1 秒内自动安装，攻击者只需在 Marketplace 上发布恶意版本即可推送至全球安装了该扩展的设备。

BYOVD (Bring Your Own Vulnerable Driver)：在 VSCode 攻击之后，攻击者可能进一步利用已知漏洞驱动程序进行提权。

## 能力边界

  48小时延迟策略（Aikido 方案）可有效拦截此类攻击
  纯端点防护难以应对，需要 Marketplace 侧验证
  开发者个人的安全意识无法解决系统性问题

## 最佳实践

  企业级：部署扩展白名单 + 新版本 48h hold 策略
  个人级：关闭自动更新，审查已安装扩展的权限
  开发者工具供应商：加强 Marketplace 审核，引入行为分析
  CI/CD：扫描依赖项和扩展的完整性

## 🔍 借鉴学习进化点（必填）

| # | 点 | 原文要点 | 对当前系统的借鉴 | 行动计划 |
|---|-----|---------|---------------|---------|
| 1 | 自动更新的风险 | 1秒延迟自动安装恶意扩展 | Hermes Agent 的 skill 自动注入和 skill-auto-inject 应有安全审查 | 在 skill-vetter 中增加来源验证和行为分析 |
| 2 | 48h 延迟策略 | Aikido 的 48h hold 可拦截零日扩展攻击 | Hermes skill 安装应有冷却期，新 skill 不立即获得高权限 | 在 skill-contracts 中增加新 skill 的权限渐进策略 |
| 3 | Token 存储安全 | VSCode 暴露了 GitHub Token | Hermes 的 API key 存储需要额外保护层 | 审查 config.yaml 中的敏感信息存储方式 |
| 4 | 扩展权限模型 | VSCode 扩展权限过于宽松 | Hermes plugins/skills 的权限模型应最小化 | 在 auto-defense-check 中加入 skill 权限审计 |
| 5 | 供应链完整性 | npm/PyPI/VSCode Marketplace 连续被攻击 | 对外部依赖（pip、npm、pip install）应有 hash 校验 | 在 hermes-agent skill 中增加依赖完整性检查步骤 |

## 🔗 RAG / Wiki 联动

### 当前状态
- wiki-kb: 网络安全话题已有大量笔记
- RAG: 供应链攻击有相关索引
- Memory: VSCode 攻击为新增话题

### 改进方案
1. 建立开发工具供应链安全专题
2. 将 TeamPCP 攻击链加入安全案例库

### 已执行操作
- ✅ 笔记已写入 bookmarks/notes
- ⏳ 待更新 ubot-topics-index.json

关联：[2026-05-21-GitHub-3800-仓库被恶意-VSCode-扩展入侵](2026-05-21-GitHub-3800-仓库被恶意-VSCode-扩展入侵.md) [2026-05-22-OpenClaw日常聊天黑化Agent-ULSPB安全研究](2026-05-22-OpenClaw日常聊天黑化Agent-ULSPB安全研究.md) [2026-06-03-Meta-AI聊天机器人被黑利用劫持Instagram账号](2026-06-03-Meta-AI聊天机器人被黑利用劫持Instagram账号.md)

## 相关笔记
- [一键偷走GitHub-Token-VSCode-Webview安全漏洞](2026-06-03-一键偷走GitHub-Token-VSCode-Webview安全漏洞.md)
