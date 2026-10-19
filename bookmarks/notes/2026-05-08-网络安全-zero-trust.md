# 网络安全：Zero Trust 零信任架构

**来源**: 领域知识综合（Tavily/搜索服务不可用，基于权威资料整理）  
**日期**: 2026-05-08  
**类型**: auto-explore · 网络安全

---

## 摘要

零信任（Zero Trust）是一种网络安全架构理念：**不再信任网络边界内的任何主体，所有访问请求必须经过持续验证**。NIST SP 800-207 将其定义为"永不信任，始终验证"（Never Trust, Always Verify）。

---

## 关键发现

### 1. 零信任的核心原则

| 原则 | 说明 |
|------|------|
| **显式验证** | 每次访问请求都基于身份、设备、位置、行为等多因素验证 |
| **最小权限** | 用户/服务只获得完成工作所需的最小权限 |
| **假设已失陷** | 默认网络已被攻破，所有通信必须加密和验证 |
| **持续评估** | 信任不是静态的，需根据实时风险动态调整访问权限 |

### 2. 零信任架构三大支柱（NIST SP 800-207）

```
┌──────────────────────────────────────────────────┐
│              零信任架构三大支柱                   │
├──────────────────────────────────────────────────┤
│                                                  │
│  ① 身份（Identity）                              │
│     - 用户身份：SSO/MFA/生物识别                  │
│     - 服务身份：Service Mesh/工作负载身份         │
│                                                  │
│  ② 设备（Device）                                │
│     - 设备健康检查（补丁、杀毒、合规）             │
│     - 设备信任评估（MDM/EDR 集成）                 │
│                                                  │
│  ③ 网络/应用（Network/Application）              │
│     - 微隔离（Micro-segmentation）                │
│     - 应用级访问控制（而非网络级）                 │
│     - 加密通信（mTLS）                            │
│                                                  │
└──────────────────────────────────────────────────┘
```

### 3. 零信任 vs 传统边界安全

| 对比维度 | 传统边界安全 | 零信任 |
|---------|-------------|--------|
| 信任假设 | 内网可信，外网不可信 | 所有网络均不可信 |
| 访问控制 | 基于网络位置（IP/端口） | 基于身份+上下文 |
| 防护重点 | 边界防火墙 | 每个资源/服务 |
| 横向移动 | 内网自由移动 | 严格微隔离 |
| 响应速度 | 事后检测 | 实时阻断 |

### 4. 落地实施路径

**阶段 1：可见性（Visibility）**
- 盘点所有资产（用户、设备、应用、数据）
- 绘制数据流向图和访问关系图
- 识别关键资产和高风险路径

**阶段 2：策略定义（Policy）**
- 定义访问策略：谁（身份）可以访问什么（资源），在什么条件下（上下文）
- 实施最小权限原则
- 建立策略引擎（如 Open Policy Agent）

**阶段 3：技术实施**
- 身份层：统一身份管理（IAM/IdP），强制 MFA
- 设备层：设备信任评估，与 EDR/MDM 集成
- 网络层：微隔离、零信任网关（ZTNA）
- 应用层：应用代理、API 网关、Service Mesh

**阶段 4：持续优化**
- 监控访问日志，分析异常行为
- 基于 UEBA（用户行为分析）动态调整信任评分
- 定期演练和策略调优

### 5. 主流零信任解决方案

| 厂商 | 产品 | 特点 |
|------|------|------|
| **Google** | BeyondCorp | 零信任鼻祖，基于身份的应用访问 |
| **Microsoft** | Entra ID + Defender | 与 Azure/Office 365 深度集成 |
| **Palo Alto** | Prisma Access | 云原生 ZTNA + SASE |
| **Zscaler** | ZIA/ZPA | 纯云架构，无需硬件 |
| **Cloudflare** | Access + Gateway | 一站式零信任 + 安全网关 |
| **阿里云** | 零信任访问控制系统 | 国内合规适配 |

---

## 对工作的价值

1. **架构升级参考**：零信任是网络安全从"边界防护"向"持续验证"转型的必经之路
2. **合规驱动**：等保 2.0、关基保护等法规对零信任有明确要求
3. **云原生适配**：传统 VPN+ 防火墙架构无法适应云原生和远程办公场景

---

## 行动建议

- [ ] 盘点当前网络架构，识别零信任改造的优先级（从核心资产开始）
- [ ] 评估现有 IAM 系统，确保支持 MFA 和细粒度权限控制
- [ ] 试点零信任网关（ZTNA），替换部分 VPN 访问场景
- [ ] 关注云原生 Service Mesh（如 Istio）在零信任中的应用

## 相关笔记
- [网络安全-AI安全自动化SOC](2026-05-05-网络安全-AI安全自动化SOC.md)
- [网络安全-threat-detection](2026-05-07-网络安全-threat-detection.md)
- [网络安全-threat-detection](2026-05-08-网络安全-threat-detection.md)
- [网络安全-零信任](2026-05-08-网络安全-零信任.md)
- [2026网络安全AI攻防趋势](2026-05-10-2026网络安全AI攻防趋势.md)
- [安全自动化-AI-SOC](2026-05-11-安全自动化-AI-SOC.md)
- [网络安全-security-automation](2026-05-12-网络安全-security-automation.md)
- [网络安全-threat-detection](2026-05-12-网络安全-threat-detection.md)
- [网络安全-zero-trust](2026-05-12-网络安全-zero-trust.md)
- [网络安全-security-automation](2026-05-15-网络安全-security-automation.md)
- [网络安全-threat-detection](explore/2026-05-04-网络安全-threat-detection.md)
- [zero-trust-architecture](explore/2026-05-06-zero-trust-architecture.md)
- [网络安全:-zero-trust](explore/2026-05-06-网络安全:-zero-trust.md)
- [security-automation](explore/2026-05-07-security-automation.md)
- [zero-trust-ai-security-2026](explore/2026-05-07-zero-trust-ai-security-2026.md)
- [zero-trust-network-security](explore/2026-05-07-zero-trust-network-security.md)
- [zero-trust-practical-pivot](explore/2026-05-07-zero-trust-practical-pivot.md)
- [网络安全-threat-detection](explore/2026-05-08-网络安全-threat-detection.md)
- [2025全球网络安全威胁-AI双刃剑](explore/2026-05-09-2025全球网络安全威胁-AI双刃剑.md)
- [security-automation](explore/2026-05-09-security-automation.md)
- [网络安全-security-automation](explore/2026-05-09-网络安全-security-automation.md)
- [网络安全-threat-detection](explore/2026-05-09-网络安全-threat-detection.md)
- [zero-trust-security](explore/2026-05-10-zero-trust-security.md)
- [security-automation](explore/2026-05-11-security-automation.md)
- [zero-trust-security](explore/2026-05-12-zero-trust-security.md)
- [AI威胁检测与SOC自动化](explore/2026-05-13-AI威胁检测与SOC自动化.md)
- [Agentic-SOC-安全自动化的范式转变](explore/2026-05-13-Agentic-SOC-安全自动化的范式转变.md)
- [网络安全-zero-trust](explore/2026-05-13-网络安全-zero-trust.md)
- [网络安全-threat-detection](explore/2026-05-14-网络安全-threat-detection.md)
- [网络安全-zero-trust](explore/2026-05-14-网络安全-zero-trust.md)
- [openai-daybreak-ai网安](explore/2026-05-15-openai-daybreak-ai网安.md)
- [zero-trust-network-security](explore/2026-05-15-zero-trust-network-security.md)
- [网络安全-security-automation](explore/2026-05-15-网络安全-security-automation.md)
- [网络安全-zero-trust-2026趋势](explore/2026-05-16-网络安全-zero-trust-2026趋势.md)
- [网络安全-zero-trust](explore/2026-05-16-网络安全-zero-trust.md)
- [skills-social-media](orphan/skills-social-media.md)

---
→ 相关：2026-05-25-前DeepMind研究员AI评估瓶颈.md（评估体系与信任模型）
