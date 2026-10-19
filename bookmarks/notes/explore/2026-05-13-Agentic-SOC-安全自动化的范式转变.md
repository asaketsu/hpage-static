# Agentic SOC：安全自动化的范式转变

- **来源**: CRN, Dropzone AI, Torq, Prophet Security, Trend Micro
- **日期**: 2026-05-13
- **类型**: auto-explore

## 摘要

2026年网络安全自动化正经历从传统 SOAR（编排+剧本）到 Agentic SOC（自主推理）的范式转变。新一代平台不再依赖预定义剧本，而是用 AI Agent 自主调查警报、猎捕威胁并做出响应决策。

## 关键要点

### 1. SOAR → Agentic SOC 的演进
- **传统 SOAR**: 静态剧本(if/then)、自定义脚本、12-18个月实施周期
- **Agentic SOC**: 自主推理 AI Agent 无需预定义剧本，像专家分析师一样调查
- 核心区别：从"执行步骤"到"推理该执行什么步骤"

### 2. 六大主流 SOAR/Agentic SOC 平台
1. **Prophet Security** — Agentic AI 代表，Glass Box 调查可回放
2. **Tines** — 灵活无代码自动化
3. **Torq** — Hyperautomation + Agentic AI
4. **Cortex XSOAR** (Palo Alto Networks) — 传统巨头转型
5. **Splunk SOAR** — Cisco 生态整合
6. **Swimlane Turbine** — 低代码自动化

### 3. 十大 Agentic SOC 工具阵营
- 巨头：CrowdStrike, Microsoft, Palo Alto, SentinelOne, Zscaler
- 创业：Dropzone AI, Torq, Prophet Security, Radiant Security
- 解决的核心痛点：警报疲劳、工具碎片化

### 4. 关键技术特征
- **自主调查**: AI Agent 根据上下文动态规划调查路径
- **自适应分流**: 新型威胁无需更新剧本即可处理
- **全案管理**: 端到端调查→响应闭环
- **可解释性**: Glass Box 模式，每步决策可审计

## 个人分析

**对工作的价值**：Agentic SOC 是 2026 年最值得关注的安全趋势之一。对我们 Hermes Agent 架构有启发——Agentic SOC 的本质就是让安全 Agent 像"虚拟分析师团队"协作，与我们的多 Agent 协作模式高度一致。

**关键信号**：
- Torq 明确宣称"SOAR is Dead"，行业话语权之争白热化
- 传统 SOAR 厂商（Palo Alto、Splunk）在积极转型而非抵抗
- Agentic SOC 的 ROI 从"月级"压缩到"天级"，这会加速采纳

**值得关注的方向**：
1. Agentic SOAR 的标准化（类似 MCP/A2A 对 Agent 协议的影响）
2. 安全 Agent 的可解释性和审计合规
3. 多租户 SOC Agent 的隔离与权限管理

## 相关笔记
- [网络安全-zero-trust](2026-05-13-网络安全-zero-trust.md)
- [AI威胁检测与SOC自动化](2026-05-13-AI威胁检测与SOC自动化.md)
- [网络安全-threat-detection](2026-05-14-网络安全-threat-detection.md)
- [网络安全-zero-trust](2026-05-14-网络安全-zero-trust.md)
- [openai-daybreak-ai网安](2026-05-15-openai-daybreak-ai网安.md)
- [zero-trust-network-security](2026-05-15-zero-trust-network-security.md)
- [网络安全-security-automation](../2026-05-15-网络安全-security-automation.md)
- [30个网络抓包调试工具速查](../2026-05-14-30个网络抓包调试工具速查.md)
