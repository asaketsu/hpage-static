# 让AI自己做增长：基于OPC和Harness思想的自主增长系统探索

> **来源**: 阿里云开发者（高德PC站SEO团队）/ 曼行
> **链接**: https://mp.weixin.qq.com/s/sZm-KDM7NoITchuhpbJkJQ
> **日期**: 2026-05-25
> **关联**: [[2026-05-07-Harness-Engineering-AI-Coding-90%-实战.md]] [[2026-05-06-harness-engineering-落地实践.md]] [[2026-04-30-Harness-Engineering即控制论.md]] [[垂域模型.md]]

---

## 摘要

高德PC站SEO团队基于OPC（One Person Company）理念 + Harness Engineering思想，构建了一套多Agent自主增长系统。系统从发现增长机会、生成提案、PRD编写、代码实现到部署上线，全程0人为干预。以"路书"功能验证，连续运行4小时，主流程无P0 Bug。

---

## 一、核心架构

### 1.1 设计理念

- **OPC（一人公司）**: AI Agent独立完成发现需求→设计方案→编写代码→测试上线全链路
- **Harness Engineering**: 围绕AI Agent构建约束机制、反馈回路、工作流控制和持续改进循环
- **总控Agent（Orchestrator）**: 状态机派发 + 心跳监控 + 超时恢复

### 1.2 Agent拆分

| 阶段 | Agent | 职责 |
|------|-------|------|
| 产品 | product_agent | 需求→结构化PRD |
| 设计 | design_agent | UI/UX设计规格 |
| 架构 | arch_agent | 技术架构、API设计、Sprint分解 |
| 测试 | testcase_agent | 测试用例设计 |
| 实现 | builder_agent | 功能代码实现 |
| 评审 | 6个独立reviewer | proposal/prd/contract/testcase/impl/frontend_design |

### 1.3 Memory系统（文件系统即记忆）

| 分类 | 目录 | 用途 |
|------|------|------|
| 定义产物 | prds/, designs/, architectures/, contracts/ | 各阶段产出 |
| 评审记录 | evaluations/ | 评审报告 + E2E证据 |
| 运行记录 | runs/ | Agent生命周期状态 |
| 决策记录 | decisions/ | 总控派发决策 |

---

## 二、关键设计模式

### 2.1 状态机 + 心跳 + 超时恢复

```
DISPATCHED → ACKED → RUNNING → SUCCEEDED / FAILED
                         ↓
               TIMED_OUT / STALLED / BLOCKED
```

- 心跳监控：每60秒
- ACK超时：300秒 → TIMED_OUT
- 执行超时：1200秒 → STALLED
- 每个Agent有进入条件（condition），防止跳过必要环节

### 2.2 上下文隔离

- Planner拆分为product/design/arch三个Agent
- Builder拆分为testcase/builder两个Agent
- **每次执行完一轮后强制开新SubAgent**，避免上下文污染
- 实验验证：同一Agent在同一上下文做多件事，记忆混乱，质量快速下降

### 2.3 零信任评估三原则

1. **评审与生成彻底分离** — 同一个AI既写又审，给自己打满分太容易
2. **零信任** — Builder说"测试通过了"，Evaluator得自己跑一遍验证
3. **零Broken Feature** — Evaluator是最后防线，不能因为"只差一点点"就放水

### 2.4 三层评审 + 快速失败优先

| 层级 | 内容 | 成本 | 退出条件 |
|------|------|------|---------|
| L1 代码质量 | 类型安全、命名规范、错误处理 | 秒级 | 编译失败 → 立即终止 |
| L2 静态质量 | 架构合规、安全实践 | 分钟级 | 漏洞/违规 → 终止 |
| L3 动态运行 | E2E测试、Playwright | 2-5分钟 | P0失败 → 终止 |

**快速失败6步**: 环境变量(<1s) → 依赖安装(5-10s) → 编译(10-30s) → 服务器启动(15-30s) → 静态分析(30-60s) → 动态验证(2-5min)

**实战数据**: .env.local缺失导致E2E 215个测试全挂，评审4分钟。引入快速失败后Step 1就拦住，1秒退回。

### 2.5 Benchmark元评估

评估的不是代码质量，而是Evaluator"评得准不准"：

- **code snippets层**: 评测代码规范检出能力（good/bad example + Golden Answer）
- **project层**: 评测功能完整性（todo简单/博客中等/电商复杂，OWASP植入bug）
- **三维度**: 精确匹配率、误报率、CRITICAL漏检率
- **三轮迭代**: 64.5% → 67.5% → 83.4%

### 2.6 Agent自进化闭环

```
Evaluator找问题 → 分析根因 → 优化Prompt/Skill → Benchmark复测验证 → 持续循环
```

常见进化场景：
- builder卡点不严 → 强化条件检查
- design丢失维度 → 维度完整性校验
- arch未执行superpower skill → 强制skill注入

---

## 三、踩坑与经验

### 3.1 环境工具化

- 能工具化的底层工具都要面向AI工具化
- 封装好的SDK比让AI自己实现成功率高10倍
- 本地和云端环境统一是基础

### 3.2 端到端自动化的隐性成本

1. **状态管理**: 部分成功怎么办？产出是否满足下游输入？
2. **超时和资源管理**: 5-6个Agent串联 + 门禁 + 重试，总耗时十几分钟
3. **环境一致性**: 构建、依赖、测试隔离
4. **可追溯日志**: 失败发生在哪、什么时间、为什么

### 3.3 对"完全无人干预"的重新理解

不是0/1状态，而是把人工干预频率降到一个人可同时监护几十个并行任务。日常环境全自动，线上保留人工确认。

### 3.4 小步快跑

不要追求一步到位的全自动化。每次循环只解决一个Agent的一个问题。保证当前版本基线可信，新问题一定出在新加部分。

### 3.5 长链路稳定性

90%单节点成功率 × 8-10节点 → 端到端一次通过率极低。靠重试+门禁回退兜底，基本上需要1-3次循环才能修掉P0问题。

---

## 四、借鉴学习进化点

| 档次 | 借鉴点 | 落实动作 |
|------|--------|---------|
| ①有利进化 | 状态机+心跳+超时恢复模式 | ✅ 已patch到 `harness-architecture` skill |
| ①有利进化 | 三层评审+快速失败优先 | ✅ 已patch到 `harness-architecture` skill |
| ②有价值 | Benchmark元评估概念 | ✅ 已写入Memory |
| ②有价值 | OPC+AI Agent扩产模式 | ✅ 已写入Memory |
| ③知识库 | Memory系统4类目录结构 | 仅笔记 |
| ③知识库 | 零信任评估三原则 | 仅笔记，harness已有类似思想 |
| ③知识库 | 上下文隔离(每次新SubAgent) | 仅笔记，Hermes delegate_task已自动隔离 |

### 自检三问

1. **可复用方法**: 状态机编排+快速失败评审，可直接用于Hermes多步骤任务编排
2. **可优化配置**: harness-architecture已补充两节实战模式
3. **关键事实**: Benchmark元评估是评估"裁判员能力"而非"代码质量"——这个视角转变很关键

---

## ✅ 落实情况

```
📋 借鉴点落实审计
├── ①有利进化 项：2个
│   ├── 状态机+心跳+超时 → skill_manage(patch harness-architecture) ✅
│   └── 三层评审+快速失败 → skill_manage(patch harness-architecture) ✅
├── ②有价值 项：2个 → memory add ✅
└── ③知识库 项：3个 → 仅笔记 ✅
```

## 相关笔记
- [Agent Skills才是关键抽象层](2026-04-02-Agent Skills才是关键抽象层.md)
- [Claude-Code四层记忆架构](2026-04-03-Claude-Code四层记忆架构.md)
- [Claude-Code-324-prompts-analysis](2026-04-04-Claude-Code-324-prompts-analysis.md)
- [Hermes-Agent四层记忆架构深度分析](2026-05-22-Hermes-Agent四层记忆架构深度分析.md)
- [OpenClaw日常聊天黑化Agent-ULSPB安全研究](2026-05-22-OpenClaw日常聊天黑化Agent-ULSPB安全研究.md)
- [Domain-Camouflaged-Injection-Attacks-域伪装注入绕过多Agent检测](2026-05-23-Domain-Camouflaged-Injection-Attacks-域伪装注入绕过多Agent检测.md)
- [Microsoft取消ClaudeCode许可-AI编码战企业政治](2026-05-23-Microsoft取消ClaudeCode许可-AI编码战企业政治.md)
- [Superset-YC-P26-AI-Agent-IDE](2026-05-23-Superset-YC-P26-AI-Agent-IDE.md)
- [AI编码工具战争-CodexClaudeCodeCursor收敛为分层架构](2026-05-24-AI编码工具战争-CodexClaudeCodeCursor收敛为分层架构.md)
- [Cloudflare-Agents-Week-2026-Agentic-Cloud全栈基础设施](2026-05-24-Cloudflare-Agents-Week-2026-Agentic-Cloud全栈基础设施.md)
- [PiAgent深度分析](2026-05-24-PiAgent深度分析.md)
- [Claude-Code之父Boris-Cherny-编程已死千级Agent夜间打工](2026-05-25-Claude-Code之父Boris-Cherny-编程已死千级Agent夜间打工.md)
- [浅浅走入Hermes-Agent的记忆-毛毛MA](2026-05-25-浅浅走入Hermes-Agent的记忆-毛毛MA.md)
- [零信任安全2026-Agent系统新攻击面与安全基线-深度蒸馏](explore/2026-05-21-零信任安全2026-Agent系统新攻击面与安全基线-深度蒸馏.md)
- [GROW开放世界VLM-Agent强化学习框架](explore/2026-05-22-GROW开放世界VLM-Agent强化学习框架.md)
- [agent-evolution-rag](explore/2026-05-23-agent-evolution-rag.md)
- [Harness-工程-AI-编程智能体成功率从20%到100%](explore/2026-05-24-Harness-工程-AI-编程智能体成功率从20%到100%.md)
- [MOSS自主Agent源码级自进化](explore/2026-05-24-MOSS自主Agent源码级自进化.md)
