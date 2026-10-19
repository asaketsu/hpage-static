# 飞猪 AgentForge：73秒造一个云端 Agent Team

> 来源：阿里妹（飞猪 CTO 线-用户技术）
> 链接：https://mp.weixin.qq.com/s/6Bs2mLC-o7qiUllx5zJ8xQ
> 评分：⭐⭐⭐⭐ (4/5) — 企业级 Agent 平台架构参考价值高，自研技术栈值得关注

---

## 一、解决什么问题

四类人的痛点：

| 用户类型 | 痛点 |
|---------|------|
| **非技术同学** | 有自动化需求但不会写代码/Prompt/MCP/容器 |
| **前端/Node 同学** | 每造一个 Agent 从零搭 Dockerfile + 部署 + IM 对接，重复劳动 |
| **Java 同学** | Agent 生态全是 Node/Python，想用但不想学新语言栈 |
| **小团队** | 想快速玩一下，框架太重，轻工具又不够 |

**一句话**：让任何人5分钟造出可部署的生产级 Agent。

---

## 二、AgentForge 是什么

Agent 工厂型平台 —— 一句话描述需求 → 流式生成7层 Prompt + 自动匹配 Skill/MCP → 浏览器调试 → 一键部署。

### 核心流程

```
描述需求 → AI Builder 生成 Prompt + Skill/MCP 装备 → 浏览器调试 → 一键云端部署
```

### 对不同用户的价值

| 用户 | 价值 |
|------|------|
| **非技术** | 5分钟出真 Loop Agent（Function Calling + 记忆召回 + 工具重试） |
| **Node 技术** | 直接拿走 Dockerfile + Aone 适配 + Egg 启动 + 全链路 SOP |
| **Java 同学** | 纯 HTTP API 调用，零 Node 依赖，不碰 LLM SDK |
| **小团队** | TeamCanvas 拖拽编排，多 Agent 组队作战 |

---

## 三、核心技术资产（自研）

### 1. fliggy-memory-sdk — 飞猪自研 mem0
- namespace 隔离 + catalog 注入 + topK 召回 + 事实抽取 + 衰减/合并/去重
- 对标 mem0，为阿里内场景深度适配
- Agent 跨 Session/跨用户/跨业务域记忆复用

### 2. FECHO — HSF 自动变 MCP 网关
- 把阿里内部成千上万 HSF 服务自动翻译成 MCP
- **Agent 能力边界 = 集团服务全集**，不再手工逐个适配
- 这是真正的"上限突破点"

### 3. ANVIL / ANVIL MULTI — Agent 运行时框架
- 不是 LangGraph 套壳，是自研的完整运行时
- 单 Agent 用 ANVIL，多 Agent 用 ANVIL MULTI
- BUC 鉴权 → 模型调用 → MCP 集成 → 调度 → 钉钉对接 → 监控审计全链路

### 4. chatLoop — ReAct + Function Calling 主循环
- 2200 行核心 + 5 子模块懒加载
- 类 Hermes/OpenClaw 的 Loop 结构
- 每步暴露 SSE 事件，工具确认/重试/跳过/历史压缩/错误兜底均为标准 hook

### 5. 7层 Prompt 模板权责分离

| 层 | 职责 |
|----|------|
| SOUL | Agent 人格/价值观 |
| USER | 用户上下文 |
| AGENTS | 多 Agent 协作定义 |
| SKILL | 单个技能描述 |
| SKILL_CHAIN | 技能链编排 |
| TOOLS | 工具装备 |
| MEMORY | 记忆注入 |

> 对比：我们 Hermes 用 SKILL.md 单文件承载技能定义，更轻量但缺乏这种分层隔离。

---

## 四、Agent 编排协议

### TeamCanvas 可视化拖拽
- 任意 Agent 拖进画布 → 连 handoff 线 → Manager + Worker 战队
- 统一对接契约：人设描述 / 能力声明 / 接收消息 / 回传结果

### hub-and-spoke 拓扑
```
Manager（拆解任务 + 语义路由）
  ├── Worker A（客服 Agent）
  ├── Worker B（行程规划 Agent）
  └── Worker C（设计师 Agent）
```
- 共享 namespace 记忆，各成员保留私有 Skill

### Java 同学三条复用通道
1. **HTTP API** — POST /api/chat，SSE 流式响应
2. **钉钉机器人** — Agent 挂群，零代码
3. **MCP 反向调用** — Java 服务暴露为 MCP Server

---

## 五、工程哲学

- **Agent 生命周期五阶段标准**：生成→装备→调试→部署→调度，每阶段独立模块 + 标准契约
- **多环境一致性**：dev/pre/prod 同代码同行为，config.{env}.ts 自动切换
- **DB-first + 文件 fallback 双模存储**：生产 RDS 持久化，本地零 MySQL 也能跑
- **Skill/MCP/Memory 三类扩展点协议化**：按契约写就能扩展，平台不改代码

---

## 💡 对我们的价值

### ✅ 可借鉴
- **7层 Prompt 分层**比扁平 system prompt 更适合复杂 Agent 协作，我们 Hermes 的 Skill 体系可以考虑引入类似的分层
- **FECHO（HSF→MCP 网关）**思路：把内部服务自动暴露为 MCP 工具，与我们的 MCP 集成方向一致
- **chatLoop 的 SSE 事件暴露**：每步可观测，比 Hermes 当前更透明

### ⚠️ 差异
- AgentForge 面向阿里内部（Aone/HSF/BUC/钉钉），我们是开源 Agent + 多平台
- 我们 Skill 用 Markdown-as-Config，比他们的 ZIP 上传更轻量
- 我们的 delegate_task 机制 ≈ 他们的 ANVIL MULTI，但稳定性待提升

### 🔥 行动建议
1. 研究 chatLoop 的工具确认/重试/历史压缩 hook 设计，评估是否可 Patch 进 Hermes
2. 7层 Prompt 模板 → 考虑在 SKILL.md frontmatter 中增加分层字段
3. FECHO 思路 → 评估是否可为 Hermes 做一个"本地服务自动暴露为 MCP"的工具

---

## 关键词

`Agent平台` `飞猪` `阿里` `MCP` `多Agent编排` `记忆系统` `ReAct循环` `Prompt分层` `ANVIL`

## 相关笔记
- [[2026-06-05-A2A协议v1.0正式发布-三层架构-多绑定与Agent互联新范式.md]] (关键词: Agent, Team, 多Agent)
- [[explore/2026-06-05-StreamMA多Agent流式推理.md]] (关键词: 多Agent)
- [[explore/2026-05-18-多模态Agent框架对比2026-深度探索.md]] (关键词: Agent框架)
- [[explore/2026-05-18-RD-Agent-Quant-multi-agent-quant-framework-deep-dive.md]] (关键词: multi-agent)
