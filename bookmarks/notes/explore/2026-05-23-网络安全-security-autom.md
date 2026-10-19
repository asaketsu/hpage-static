# 网络安全: Security Automation (2026趋势)

> 嗅探自动学习 | 2026-05-23

## 摘要

2026年安全自动化领域正经历从传统SOAR向Agentic AI SOC的范式转移。静态playbook编排已无法应对机器速度的威胁，AI原生平台正在取代第一代SOAR工具。

## 关键发现

### 1. SOAR → Agentic AI 范式转移
- 传统SOAR基于静态if/then playbook，实施周期12-18个月，已无法跟上威胁速度
- 新一代Agentic AI SOC平台使用自主推理Agent替代预定义playbook
- 代表：Prophet Security、Radiant Security、Torq Hyperautomation
- 核心差异：从"手动编写每个调查步骤"到"AI自主规划并执行调查"

### 2. 市场现状与痛点
- SOC团队平均每天收到4,500+告警，67%被直接忽略（SANS 2024调查）
- SOAR在用户满意度排名中处于安全工具倒数前十
- 71%的SOC分析师报告职业倦怠
- SOAR效能受限于SIEM日志覆盖率（平均仅覆盖约2/3企业环境）

### 3. 2026年三大市场类别
- **Legacy SOAR**：传统playbook引擎（Splunk SOAR、IBM QRadar SOAR）
- **Workflow Automation**：无代码/低代码工作流自动化（Torq、Swimlane Turbine）
- **AI SOC Agent平台**：Agentic AI驱动的自主调查与响应（Prophet、Radiant、Stellar Cyber）

### 4. 顶级平台对比
- **Stellar Cyber**：Open XDR + Agentic AI，统一自治SOC
- **Palo Alto Cortex XSIAM**：AI驱动安全平台，适合全Palo Alto生态
- **Torq**：Hyperautomation架构，AI原生替代SOAR
- **Prophet Security**：Glass Box调查模式，可回放推理链
- **Radiant Security**：Agentic AI SOC，自动化告警分类与调查

### 5. AI SOC核心能力
- 自动威胁检测与分类：AI过滤误报，优先排序真实威胁
- 加速事件响应：跨数据源关联，自动生成根因分析和响应方案
- 24/7持续覆盖：降低对人工值班依赖
- 自适应学习：应对新型威胁无需手动更新规则

## 对工作的价值

- Agent安全治理（agent-security-governance skill）可借鉴SOC自动化的分层架构
- Hermes的watchdog/defense-check机制本质是安全自动化的轻量实现
- Agentic AI SOC的"Glass Box"可审计理念适用于所有Agent系统的安全设计

## 行动建议

1. 评估现有watchdog机制是否可引入Agentic AI思路（自适应规则而非静态阈值）
2. 关注Agentic AI SOC的开源工具链，可能为Agent安全提供可复用组件
3. 将"安全自动化"纳入Agent自我进化循环的一个传感器维度

## 来源
- Exabeam: Best SOAR Tools 2026
- Prophet Security: Top 6 SOAR Platforms 2026
- Stellar Cyber: Security Automation Tools 2026
- Torq: SOAR Replacement 2026
- Vectra AI: SOC Automation Guide
- Radiant Security: Best AI SOC Services 2026
- SANS SOC Survey 2024

## 相关笔记
- [网络安全-security-automation](../2026-05-18-网络安全-security-automation.md)
- [网络安全-threat-detection](../2026-05-18-网络安全-threat-detection.md)
- [网络安全自动化2026](../2026-05-19-网络安全自动化2026.md)
- [网络安全-threat-detection-2026前沿](../2026-05-20-网络安全-threat-detection-2026前沿.md)
- [网络安全-zero-trust-2026演进](../2026-05-20-网络安全-zero-trust-2026演进.md)
- [Domain-Camouflaged-Injection-Attacks-域伪装注入绕过多Agent检测](../2026-05-23-Domain-Camouflaged-Injection-Attacks-域伪装注入绕过多Agent检测.md)
- [edgetunnel边缘隧道方案分析](../2026-05-24-edgetunnel边缘隧道方案分析.md)
- [网络安全-threat-detection](2026-05-17-网络安全-threat-detection.md)
- [网络安全-security-automation](2026-05-19-网络安全-security-automation.md)
- [网络安全-zero-trust](2026-05-19-网络安全-zero-trust.md)
