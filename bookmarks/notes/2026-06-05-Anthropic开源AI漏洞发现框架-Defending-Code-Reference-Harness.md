# Anthropic 开源 AI 漏洞发现框架：Defending Code Reference Harness

> **来源**：Anthropic · GitHub · 2026-06-05
> **原文**：https://github.com/anthropics/defending-code-reference-harness
> **评分**：⭐4.5/5
> **标签**：#AI安全 #漏洞发现 #Claude #开源 #安全自动化 #gVisor

## 摘要

Anthropic 开源了基于 Claude 的自主漏洞发现与修复参考实现——Defending Code Reference Harness。该框架实现了 recon→find→verify→report→patch 的完整自动化管线，集成了 Claude Code Skills（/quickstart、/threat-model、/vuln-scan、/triage、/patch），默认针对 C/C++ 内存漏洞，使用 Docker + ASAN 沙箱执行。Anthropic 还提供商业产品 Claude Security，支持多项目扫描和生命周期管理。

## 核心内容

### 管线架构

1. **Recon（侦察）**：代码库范围界定和攻击面分析
2. **Find（发现）**：Claude 驱动的漏洞扫描
3. **Verify（验证）**：ASAN + Docker 沙箱中运行验证
4. **Report（报告）**：结构化漏洞报告生成
5. **Patch（修复）**：自动生成修复代码

### Claude Code Skills 集成

- `/quickstart` — 30 秒引导式入门
- `/threat-model` — 交互式威胁建模
- `/vuln-scan` — 自动漏洞扫描
- `/triage` — 漏洞分诊和优先级排序
- `/patch` — 自动修复生成
- `/customize` — 移植到其他语言/检测器/漏洞类

### 安全设计

- 读操作 Skills（/quickstart、/threat-model 等）只读写文件，安全可无沙箱运行
- `/patch` 在静态结果上也只读写
- 自主管线执行目标代码时强制 gVisor 沙箱
- `scripts/setup_sandbox.sh` 一键沙箱配置
- `bin/vp-sandboxed` 沙箱化执行入口

### Claude Security 商业版

- 托管式漏洞发现与修复服务
- 多阶段验证管线降低误报
- 跨多项目的发现管理生命周期

## 关键概念

- **Reference Implementation**：非产品级工具，是最佳实践参考
- **gVisor Sandbox**：Google 的用户空间内核，提供强隔离
- **ASAN (AddressSanitizer)**：C/C++ 内存错误检测工具
- **Multi-stage Verification**：多阶段验证降低误报率

## 能力边界

- 仅是参考实现，不维护，不接受贡献
- 默认配置仅支持 C/C++ 内存漏洞
- 需要手动 /customize 移植到其他语言
- 需要 Claude Code 环境
- 非 Claude API 用户需自行适配

## 最佳实践

- 先用 /quickstart 了解全貌再深入
- 威胁建模先于漏洞扫描（/threat-model → /vuln-scan）
- 沙箱执行不可跳过（安全红线）
- 漏洞分诊避免修复一切（/triage 优先级排序）

## 🔍 借鉴学习进化点

1. **Recon→Find→Verify→Report→Patch 管线模式**：Hermes auto-defense-check 可借鉴此五阶段管线，当前仅做"检查"，缺少"修复"闭环。扩展为检查→验证→修复→报告四步。
2. **Claude Code Skills 结构**：每个功能（quickstart/threat-model/vuln-scan）作为独立 Skill 的模式与 Hermes Skill 系统一致。可创建安全扫描系列 Skill（security-recon、security-scan、security-triage）。
3. **gVisor 沙箱执行**：Hermes cron 执行外部命令时应考虑沙箱化。特别是 watchdog 和 auto-defense-check 涉及系统命令执行的场景。
4. **多阶段验证降误报**：当前 Hermes 漏报/误报处理粗糙。可引入 verify 阶段，对检测结果做二次确认。
5. **/customize 移植模式**：Skill 设计应默认可移植。当前安全相关 Skill 硬编码较多，可参考此框架的定制化接口设计。

## 🔗 RAG / Wiki 联动

### 当前状态
- 已有 agent-memory-contamination、domain-camouflaged-injection 等安全笔记
- auto-defense-check cron job 已在运行

### 改进方案
1. 将此框架加入 Wiki KB 安全节点
2. 关联 Anthropic Project Glasswing 笔记（同为 Anthropic 安全产品）
3. 为 auto-defense-check 增加 patch 生成能力

### 已执行操作
- ✅ 笔记写入
- ⏳ 待更新索引

## 相关笔记
- [Claude-Code动态工作流六种调度模式](2026-06-04-Claude-Code动态工作流六种调度模式.md)
- [Anthropic递归自我改进-AI构建AI的里程碑时刻](2026-06-05-Anthropic递归自我改进-AI构建AI的里程碑时刻.md)
