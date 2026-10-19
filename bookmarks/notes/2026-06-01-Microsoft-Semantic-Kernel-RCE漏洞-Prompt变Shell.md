# Microsoft Semantic Kernel RCE 漏洞：当 Prompt 变成 Shell

> **来源**：Microsoft Security Blog · 2026-05-07
> **原文**：https://www.microsoft.com/en-us/security/blog/2026/05/07/prompts-become-shells-rce-vulnerabilities-ai-agent-frameworks
> **笔记ID**：sniff-20260601-ms-sk-rce
> **格式**：双格式(MD + HTML) · 含借鉴进化点 · RAG/wiki联动

## 摘要

Microsoft 安全团队披露了 Semantic Kernel AI Agent 框架中的两个严重 RCE 漏洞（CVE-2026-25592 和 CVE-2026-26030），攻击者可通过 prompt 注入实现远程代码执行。CVE-2026-25592（CVSS 10.0）是 .NET SDK 中 SessionsPythonPlugin 的路径穿越漏洞，允许任意文件写入。CVE-2026-26030 是 Python SDK 中 InMemoryVectorStore 的 lambda 过滤器代码注入漏洞。这两个漏洞不是 bug，而是"设计即如此"（developed by design），暴露了 AI Agent 框架安全模型的根本性缺陷。

## 核心内容

### 1. CVE-2026-25592：SessionsPythonPlugin 路径穿越

- **组件**：Semantic Kernel .NET SDK 的 SessionsPythonPlugin
- **漏洞类型**：CWE-22 Path Traversal → Arbitrary File Write → RCE
- **CVSS 评分**：10.0（满分）
- **根因**：DownloadFileAsync 和 UploadFileAsync 函数未对 localFilePath 参数做路径校验
- **影响版本**：< 1.70.0（.NET SDK）
- **修复版本**：Microsoft.SemanticKernel.Core 1.71.0
- **攻击链**：低权限用户 → 路径穿越写入恶意文件 → 代码执行 → 系统接管

### 2. CVE-2026-26030：InMemoryVectorStore 代码注入

- **组件**：Semantic Kernel Python SDK 的 InMemoryCollection._parse_and_validate_filter
- **漏洞类型**：不安全的字符串插值 → lambda 表达式注入 → RCE
- **影响版本**：< 1.39.4（Python SDK）
- **根因**：向量存储的 filter 功能直接将用户输入拼接进 Python lambda 表达式
- **攻击面**：任何接受外部输入作为向量搜索 filter 的 Agent 应用
- **关键洞察**：这不是编程错误，而是设计选择 — 框架故意用 eval 式的动态代码生成来实现灵活性

### 3. 攻击链概览

Microsoft 描述的完整攻击链：
1. 攻击者构造恶意 prompt → Agent 框架解析
2. Prompt 注入 → 触发 SessionsPythonPlugin 或 VectorStore filter
3. 路径穿越 / 代码注入 → 在服务器端执行任意代码
4. 利用 Agent 持有的凭证横向移动

### 4. 防御建议

- Microsoft 发布了 Agent Governance Toolkit (AGT) 的 ATR 规则覆盖这两个 CVE
- 建议实施"语义防火墙"（Semantic Firewall）— 用二级隔离模型评估输入/输出
- 最小权限原则：Agent 的工具访问权限必须严格限制
- 运行时行为监控：检测 .NET 进程异常子进程、Python 异常 import

## 对比/框架

| 维度 | CVE-2026-25592 | CVE-2026-26030 |
|------|----------------|----------------|
| 语言 | .NET (C#) | Python |
| SDK 版本 | < 1.70.0 | < 1.39.4 |
| 组件 | SessionsPythonPlugin | InMemoryVectorStore |
| 攻击向量 | 路径穿越 → 文件写入 | Lambda 注入 → 代码执行 |
| CVSS | 10.0 | 未公布（推测 9.0+） |
| 根因 | 未校验文件路径 | eval 式动态代码生成 |
| 性质 | 设计缺陷 | 设计缺陷 |
| 修复 | 路径白名单校验 | 移除动态 lambda 生成 |

## 关键概念

- **Prompt Injection → RCE**：从文本操控跨越到系统级代码执行，是 AI 安全的新范式
- **Semantic Kernel**：Microsoft 的 AI Agent SDK，用于构建、编排和部署 AI Agent 和多 Agent 系统
- **InMemoryVectorStore**：语义内核的内存向量数据库，用于 RAG 场景中的相似性搜索
- **SessionsPythonPlugin**：允许 Agent 在隔离的 Python 环境中执行代码的插件
- **"Developed by Design"**：微软原话 — 漏洞不是 bug，而是框架设计理念的安全盲区
- **Semantic Firewall**：用独立的小型模型对 Agent 输入/输出做安全评估的防御层

## 能力边界

- 分析基于公开 CVE 信息和第三方安全报告，未直接访问 Microsoft 原始博客
- 具体利用代码细节未披露（Microsoft 仅提供概念验证 CTF）
- 修复版本可能引入新的 API breaking changes，迁移需评估
- 仅覆盖 Semantic Kernel，其他 Agent 框架（LangChain、CrewAI 等）可能存在类似问题

## 最佳实践

1. 立即升级：Semantic Kernel .NET ≥ 1.71.0，Python ≥ 1.39.4
2. 禁用不必要插件：如果不用 SessionsPythonPlugin 就不要加载它
3. Agent 最小权限：永远不要给 Agent 比任务所需更多的系统权限
4. 输入验证层：在 Agent 框架之上加独立的输入校验层
5. 运行时监控：部署 ATR 规则检测异常行为模式
6. CTF 练习：Microsoft 发布了攻击自己的 Agent 的 CTF 挑战，推荐团队实战

## 🔍 借鉴学习进化点（必填）

| # | 点 | 原文要点 | 对当前系统的借鉴 | 行动计划 |
|---|-----|---------|---------------|---------|
| 1 | Prompt 注入 → RCE 攻击链 | "When prompts become shells" — prompt 可跨越到系统级代码执行 | Hermes Agent 的 tool 执行层需要类似的安全审计 | 为 Hermes 工具调用链添加输入校验层，特别是文件操作和代码执行类工具 |
| 2 | "设计即如此"安全盲区 | 框架为灵活性牺牲安全性，用 eval 式动态代码生成 | Hermes Skill 系统的动态加载和执行可能存在类似风险 | 审查 skill 中所有 eval/exec 调用，建立白名单机制 |
| 3 | Agent 最小权限原则 | Microsoft 建议严格限制 Agent 工具访问权限 | Hermes 的工具权限模型需要更细粒度的控制 | 设计 per-skill 权限声明机制，限制每个 skill 可调用的工具子集 |
| 4 | 语义防火墙概念 | 用二级隔离模型评估输入/输出 | 可为 Hermes Gateway 添加 prompt 安全评估中间件 | 评估在 gateway 层添加轻量级 prompt 安全检测的可行性 |
| 5 | ATR 规则模式 | Agent Governance Toolkit 的运行时威胁检测规则 | 可借鉴为 Hermes 的 auto-defense-check 增加运行时异常检测 | 在 auto-defense-check skill 中添加 Agent 行为异常模式检测 |

## 🔗 RAG / Wiki 联动（必填）

### 当前状态
- wiki-kb 已收录 AI 安全相关笔记 5+ 篇
- RAG 索引覆盖网络安全/Agent 安全领域
- Memory 中有 ULSPB 安全研究笔记

### 改进方案
1. 将 CVE-2026-25592/26030 加入安全知识库的"已知漏洞"索引
2. 与之前的 OpenClaw 日常聊天黑化 Agent 笔记交叉引用
3. 更新 Hermes 安全运维手册，增加 Agent 框架漏洞应急流程

### 已执行操作
- ✅ 笔记已生成并存入 bookmarks/notes
- ⏳ 交换池同步待执行
- ⏳ wiki-kb 索引更新待下次维护窗口

## 相关笔记
- [[2026-05-13-Claude-3D-CAD-创意连接器深度分析]]
- [[2026-06-01-AI-Agent依赖更新安全风险-117K变更实证研究]]
- [[2026-05-27-Cloudflare-Flagship-Feature-Flag服务正式发布]]
