# OpenClaw Mission Control — 多 Agent 监控仪表盘分析

> 来源：GitHub sharbelxyz/openclaw-mission-control ｜ 89 ⭐ 22 Fork ｜ 2026-04-23
> 链接：https://github.com/sharbelxyz/openclaw-mission-control

---

## 一句话定位

一个极简的多 AI Agent 监控仪表盘模板——每个 Agent 通过一个 HTTP POST 端点上报状态，仪表盘统一展示在线/离线/任务/成本。

---

## 技术栈

| 层 | 技术 | 版本 |
|----|------|------|
| 框架 | Next.js App Router | 16.2.3 |
| 前端 | React + Tailwind CSS v4 | React 19 |
| ORM | Prisma | 6 |
| 数据库 | PostgreSQL | 任意（Neon/Supabase/本地） |
| 图标 | lucide-react | - |
| 部署 | Vercel | - |

---

## 数据模型（Prisma Schema）

项目定义了 4 个核心模型，设计极其精简：

### 1. AgentState（Agent 状态）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | String @id | 稳定标识（如 "content-writer"） |
| name | String | 人类友好名 |
| emoji | String? | 卡片渲染 |
| role | String? | 角色（Content/Trading/Research） |
| status | String | online / idle / working / offline / error |
| lastActive | DateTime? | 最后活跃时间 |
| tasksCompleted | Int | 累计完成任务数 |
| totalCost | Float | 累计 API 调用成本（$） |
| currentTask | String? | 当前正在做的事 |
| recentActivity | Json | 最近活动日志数组 |

### 2. Mission（任务）

| 字段 | 说明 |
|------|------|
| agentId | 关联 Agent |
| title / description | 任务内容 |
| status | pending / active / completed / failed |
| priority | high / medium / low |
| result | 执行结果 |

### 3. Idea（想法）

| 字段 | 说明 |
|------|------|
| source | 哪个 Agent 生成的 |
| status | pending / approved / rejected |

### 4. DataStore（KV 存储）

通用 Key-Value 存储，用于 Agent 配置和临时数据。

---

## 核心架构模式

### 1. Agent 自注册 + Upsert 模式

```python
# 每个 Agent 定期 POST 自己的状态
requests.post("http://localhost:3000/api/agents/state",
    headers={"Authorization": f"Bearer {INTERNAL_API_SECRET}"},
    json={
        "id": "content-writer",
        "name": "Content Writer",
        "status": "working",
        "currentTask": "Drafting thread",
        "tasksCompleted": 42,
        "totalCost": 3.14,
    })
```

**设计精髓**：
- Agent 侧是 push 模式（不是 pull），Agent 主动上报
- 服务端用 `upsert`（存在则更新，不存在则创建）
- 简单的 Bearer Token 认证
- 无需服务发现，Agent 只需知道一个 URL

### 2. 极简 CSS 变量体系

```css
:root {
  --bg: #0a0a0a;      /* 背景 */
  --panel: #111111;   /* 面板 */
  --line: #1f1f1f;    /* 边框 */
  --ink: #ededed;     /* 主文字 */
  --ink-2: #a1a1aa;   /* 次文字 */
  --ink-3: #71717a;   /* 弱文字 */
  --accent: #10b981;  /* 强调色（翡翠绿） */
}
```

仅 7 个变量，覆盖所有颜色需求。**三个灰度层（ink/ink-2/ink-3）** 分级表达信息重要度。

### 3. Server Component 直出

所有页面都是 Next.js Server Component（`async function`），直接查库渲染，**零客户端状态管理**。

```tsx
export const dynamic = "force-dynamic";  // 禁用缓存，每次请求都刷新

async function getStats() {
  const [agents, pendingMissions, pendingIdeas] = await Promise.all([...]);
  return { ... };
}
```

### 4. BOOTSTRAP.md 驱动的 Agent Onboarding

项目有一个 `BOOTSTRAP.md`，专门写给 AI Agent 看——告诉 Agent 如何帮用户安装和扩展这个仪表盘。这是 **"AI Agent 作为用户"** 的设计思路。

---

## 页面结构

| 页面 | 路径 | 功能 |
|------|------|------|
| Dashboard | `/` | KPI 概览 + Agent 卡片 |
| Agents | `/agents` | 全部 Agent 列表表格 |
| Missions | `/missions` | 任务队列 |
| Ideas | `/ideas` | Agent 生成的想法 |
| Calendar | `/calendar` | 待建（占位页） |

---

## 可进化内容（与 Hermes 关联）

### 🟢 可直接吸收的模式

| 模式 | 项目做法 | Hermes 可用场景 |
|------|---------|----------------|
| **Agent 心跳上报** | POST /api/agents/state | Hermes 三机（jbot/ubot/abot）状态汇总到统一仪表盘 |
| **三灰度文字体系** | ink / ink-2 / ink-3 | 所有 HTML 输出的信息分级表达 |
| **Upsert 自注册** | Agent 按稳定 ID 注册 | Hermes Agent 群的动态发现和管理 |
| **极简 KV 存储** | DataStore 模型 | Agent 间共享配置的轻量方案 |
| **Server Component 直出** | 零客户端状态 | Hermes Dashboard 面板的数据直出模式 |
| **BOOTSTRAP.md** | AI Agent 的安装引导 | Hermes Skill 的 AGENTS.md 同源设计 |

### 🟡 架构启发

1. **Agent → Dashboard 解耦**：Agent 只管 push，Dashboard 只管展示。这种单向数据流极其简洁。
2. **成本追踪字段**：`totalCost` 每次心跳累加。Hermes 也可以在心跳中带上 token 消耗统计。
3. **Mission 模型**：pending → active → completed/failed 状态机。Hermes Kanban 的简化版。
4. **Idea 收集**：Agent 产出的创意汇总到统一池等待审批。Hermes 也可以让各猫将发现/建议汇总。

### 🔴 局限性

1. **无实时更新**：需要刷新页面。可加 WebSocket/SSE。
2. **无认证**：仅 Bearer Token，无用户系统。
3. **无历史数据**：Agent 状态覆盖式更新，无法回溯。
4. **Calendar 占位**：尚未实现。
5. **单节点**：无分布式考虑。

---

## 关键代码片段

### Prisma 单例模式（防热重载泄漏）

```typescript
const globalForPrisma = global as unknown as { prisma?: PrismaClient };
export const prisma =
  globalForPrisma.prisma ?? new PrismaClient({ log: [...] });
if (process.env.NODE_ENV !== "production") globalForPrisma.prisma = prisma;
```

### KPI 卡片组件

```tsx
function Kpi({ icon, label, value }) {
  return (
    <div className="p-4 rounded-xl flex flex-col gap-1"
         style={{ background: "var(--panel)", border: "1px solid var(--line)" }}>
      <div className="flex items-center gap-1.5 text-[11px] uppercase tracking-wider text-[var(--ink-3)]">
        {icon}{label}
      </div>
      <div className="text-[22px] font-semibold">{value}</div>
    </div>
  );
}
```

### 状态点颜色映射

```tsx
const color = status === "online" || status === "working" ? "bg-emerald-500"
  : status === "error" ? "bg-red-500"
  : status === "idle" ? "bg-amber-500"
  : "bg-zinc-600";
```

---

## 与 Hermes 现有能力的对比

| 能力 | Hermes 现有 | Mission Control |
|------|-------------|-----------------|
| Agent 状态监控 | cron job 日志 + process poll | 心跳 POST + 仪表盘 |
| 成本追踪 | 模型调用级 | Agent 聚合级 |
| 任务管理 | Kanban | Mission（简化版） |
| 可视化 | homepage-dashboard | Web 仪表盘 |
| 多 Agent 协调 | exchange-protocol（NFS JSONL） | HTTP POST API |

---

## 总结

OpenClaw Mission Control 是一个**教科书级的极简 MVP**：

- 27 个文件，1 个 commit，功能完整
- 4 个数据模型覆盖 Agent 管理全流程
- Agent 自注册 + Upsert 的 push 模式，零配置接入
- 7 个 CSS 变量，视觉一致性强
- BOOTSTRAP.md 面向 AI Agent 的文档范式

**最适合 Hermes 借鉴的不是代码，而是其"Agent 心跳 + 统一仪表盘"的架构思想**——用最少的端点（1 个 POST）实现多 Agent 的状态聚合。

---

*分析时间：2026-06-05*

## 相关笔记

