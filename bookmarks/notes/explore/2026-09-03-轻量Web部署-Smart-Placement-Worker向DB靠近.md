# 轻量 Web 部署：Smart Placement 深挖 — Worker 向 DB 靠近的机制、实测与选型铁律

> 探索日期 2026-09-03 | 兴趣等级 L3 | 来源 4 篇 | 类型 auto-explore（嗅探队列）
> 前序笔记：2026-08-31-Workers全栈部署-单Worker架构与生产实践.md（Smart Placement 仅一笔带过，本篇补全）

## 摘要

Smart Placement 解决 serverless 的经典矛盾：Worker 默认跑在离用户最近的节点，但后端 DB/API 往往是中心化的——用户在 Sydney、DB 在 Frankfurt 时，3 次 round trip 的跨球延迟成了瓶颈。官方实测：将 Worker 迁到 DB 附近，请求耗时提升 4-8x。2026 年该能力已从"自动 Smart 单模"演化为三模体系：Smart（自动分析流量）/ Region（`aws:us-east-1` 显式区域）/ Host（非云厂商后端探测三角定位）。核心洞察是"网络决策不应是人类决策"，但也有明确反例（<1% Worker 会被自动回退 UNSUPPORTED_APPLICATION）。与 Hyperdrive、Durable Objects 构成外接 DB 加速的完整决策树。

---

## 一、核心机制：反向的"靠近"逻辑（关键发现 1）

> 传统 CDN 思维是"计算靠近用户"；Smart Placement 反其道而行——当后端是中心化服务且多次 round trip 时，"计算靠近数据"更优。

```
默认（无 Placement）:
  Sydney用户 ──近──> Worker(悉尼DC) ──3×RTT≈90ms×3──> DB(法兰克福)
                      总耗时 ≈ 270ms+ 网络来回

开启 Smart Placement:
  Sydney用户 ──~50ms──> 转发 ──> Worker(法兰克福DC) ──<1ms──> DB
                            总耗时 ≈ 50ms + 3×<1ms
```

- Cloudflare 网络 ~50ms 覆盖 95% 全球联网人口——反过来意味着它也"离你的后端很近"
- 判定算法：实时分析 Worker 发出的 fetch subrequest，若平均对同一后端 >1 次请求，结合全网延迟数据（Argo Smart Routing 同源情报）自动选择最优 DC
- **只考虑 Worker 曾经运行过的位置**——没有流量的区域不会被选中，冷门地区流量可能导致 INSUFFICIENT_INVOCATIONS

## 二、三模体系：Smart / Region / Host（关键发现 2）

官方 Placement 已演化为三种模式，按后端可观测性递增选择：

```
知道得越少 ──> 越自动
┌─────────────────────────────────────────────────────┐
│ Smart   mode="smart"      多后端/位置未知/后端有副本  │
│ Region  placement.region  单一已知云区域(aws/gcp/az) │
│ Host    placement.host    非云厂商单宿主后端          │
│         L4: TCP CONNECT 探测 / L7: HTTP HEAD 探测    │
└─────────────────────────────────────────────────────┘
```

- **Region 模式**：`{provider}:{region}` 格式（如 `aws:eu-central-1`），Cloudflare 映射到对该区域延迟最低的 DC，网络维护/变更自动调整，无需配 failover
- **Host 模式**：探测从公共 IP 段（非 CF IP）发出，定期重测；**对 broadcast/anycast/多副本资源无效**——只适合单宿主
- Placement Hints 官方宣称收益：单点 DB 场景 round trip 从 20-30ms 降到 1-3ms

### wrangler 配置

```toml
[placement]
mode = "smart"              # 自动模式

# 或显式提示（二选一）
[placement]
region = "aws:us-east-1"    # 云区域
# host = "db.example.com"   # L4 探测
# hostname = "api.example.com"  # L7 探测
```

## 三、硬限制清单（关键发现 3）

> 这些限制决定了"何时不能用"，比"怎么开"更重要。

1. **只影响 fetch event handler**——RPC 方法、named entrypoints 不受影响；无 fetch handler 的 Worker 直接被忽略
2. **静态资源始终离用户最近**——但通过 `env.ASSETS.fetch`（static assets binding）取的资产跟随 Worker 位置，Pages `_middleware.js` 全量拦截时会造成意外的资产延迟增加
3. **生效条件苛刻**：需多地点持续流量，分析最长 15 分钟；默认保留 1% 请求不走 Smart Placement 作 baseline 对照
4. **自动回退机制**：状态 `UNSUPPORTED_APPLICATION`（Smart Placement 反而变慢，<1% Worker 触发）——说明它有真实失败面，不是纯收益
5. 状态可观测：响应头 `cf-placement: remote-LHR`（被路由）/ `local-EWR`（默认位置）；API 可查 SUCCESS / INSUFFICIENT_INVOCATIONS / UNSUPPORTED_APPLICATION

## 四、架构模式：双 Worker 拆分（关键发现 4）

> 全栈应用的标准解法：边缘逻辑与后端逻辑分离，各得其所。

```
┌─ edge-worker（无 placement，离用户近）────────┐
│  认证 / 路由 / 快速拒绝未授权请求              │
└──────────────Service Bindings + RPC──────────┘
                 │
┌─ app-worker（placement 靠近 DB）─────────────┐
│  DB 查询 / 外部 API 调用，单毫秒级往返         │
└──────────────────────────────────────────────┘
```

- edge Worker 快速拒绝未授权请求（省 DB 流量），认证后 RPC 转发到 placed Worker
- 这是 2026-08-31 笔记"单 Worker 架构"在数据库密集场景下的进阶演进路径

## 五、与 Durable Objects / Hyperdrive 的决策树

```
后端是什么？
├─ Cloudflare 自家（D1/DO/KV/R2）
│   └─ 不需要 Placement。DO 天然自动放置，
│      内嵌 SQLite 计算与数据同进程 = 零延迟
├─ 外接中心化 DB（Supabase/PlanetScale/自建PG）
│   ├─ 多次 round trip + 位置不明/多副本 → Smart
│   ├─ 单一已知云区域 → Region hints（确定性更高）
│   ├─ 连接建立慢（TCP/TLS 握手瓶颈）→ 叠加 Hyperdrive
│   └─ 读多写少 + 用户全球分布 → 考虑不启用，
│      保持离用户近（PlanetScale 工程师的实际选择）
└─ 非云厂商单宿主服务 → Host/Hostname 探测
```

> Hyperdrive 解决"连接建立慢"（连接池+缓存），Smart Placement 解决"往返距离远"——两者正交可叠加。

## 六、对现有 Skill/笔记改进建议

- **P1**：`2026-08-31-Workers全栈部署` 笔记的 Smart Placement 段落可补充本篇链接（三模体系 + 双 Worker 模式），当前仅一句话带过
- **P2**：兴趣表中 "Smart Placement(Worker向DB靠近)" 关键词已充分覆盖，建议标记 ✅ 并维持 last_explored 2026-09-03
- **P2**：与 Hyperdrive 关键词形成组合条目（"外接DB加速=Placement×Hyperdrive 叠加"），未来探索 Hyperdrive 时可直接引用本篇决策树

## 七、关键风险与盲点

- **【官方验证】** UNSUPPORTED_APPLICATION 存在（<1%）：盲目开启可能变慢且有自动回退兜底，但回退期间性能受损
- **【社区复现】** Reddit 案例：开启 Smart Placement 后 SaaS 仍 500ms+ 延迟——Placement 只优化 Worker→后端段，用户→Worker 段（~50ms）和后端本身慢（free-tier DB）它管不了；瓶颈定位要先分段测量
- **【官方验证】** 静态资产与 Worker 位置解耦的陷阱：middleware 全量拦截 + ASSETS binding 组合会把资产服务拉到 DB 附近，页面首屏反而变慢
- **【盲点】** Smart Placement 依赖历史流量模式——灰度发布/新上线 Worker 的前 15 分钟行为不可控，SLA 敏感场景建议用 Region hints 换确定性

## Actionable Insights

1. **外接 DB 的 Workers 项目**：立即检查 `wrangler.toml`，单一云区域 DB 加 `[placement] region = "aws:xxx"`，一行配置换 round trip 从 20-30ms → 1-3ms
2. **验证手法**：部署后 curl 检查 `cf-placement` 响应头确认实际路由位置，配合 Functions Metrics 的 request duration 对照 1% baseline
3. **全栈拆分**：认证类逻辑留在 edge Worker，DB 密集逻辑拆到 placed Worker，用 Service Bindings RPC 串联——两段延迟各自最优

## 一页速查

> **何时用**：外接中心化 DB/API + 多次 round trip（官方 4-8x 提升）
> **三模选择**：位置未知→smart / 已知云区域→region / 非云单宿主→host
> **不用**：数据在 CF 自家（DO 零延迟天然放置）；读密集全球用户（保持离用户）
> **叠加**：Hyperdrive（连接池）× Placement（位置）正交组合
> **红线**：只作用于 fetch handler；静态资产离用户；1% baseline 对照；<1% 自动回退
> **观测**：cf-placement 头 + API 状态 + request duration 指标

## 待深入

- Hyperdrive 与 Placement 叠加的实测数据（官方缺联合 benchmark）
- Smart Placement 对 Queues/Workflows/Cron Triggers 等非 fetch 触发器的行为（文档未覆盖）
- Region hints 在多云多区域后端（读写分离）下的组合策略

## 来源列表

1. Cloudflare Developer Docs — Placement（官方，2026 更新）：https://developers.cloudflare.com/workers/configuration/placement
2. Cloudflare Blog — Announcing Smart Placement（官方，含 Sydney→Frankfurt 4-8x 实测）：https://blog.cloudflare.com/announcing-workers-smart-placement
3. PlanetScale Blog — Hyperdrive real-time（第三方实践，含"选择不用 Smart Placement"的反例）：https://planetscale.com/blog/cloudflare-hyperdrive-real-time
4. Cloudflare Community / Reddit — Smart Placement 实际效果讨论（社区反馈，含 500ms+ 负面案例）


## 相关笔记

- [Workers全栈部署-单Worker架构与生产实践](./2026-08-31-轻量Web部署-Workers全栈部署-单Worker架构与生产实践.md) — 前序笔记，本篇补全其一笔带过的 Smart Placement
- [浏览器WASM-SQLite](./2026-09-03-轻量Web部署-浏览器WASM-SQLite.md) — 轻量部署姊妹篇：DB 向 Worker 靠拢 vs DB 进浏览器
- [SQLite-on-NFS损坏规避-WAL陷阱与回滚日志方案](./2026-08-30-轻量Web部署-SQLite-on-NFS损坏规避-WAL陷阱与回滚日志方案.md) — 轻量部署系列的存储层陷阱篇
