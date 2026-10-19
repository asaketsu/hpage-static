# 轻量Web部署: Turso Embedded Replicas（微秒级本地读+CDC同步）

- 日期: 2026-08-16
- 类型: auto-explore（嗅探队列自主选题）
- 来源: [官方文档](https://docs.turso.tech/features/embedded-replicas/introduction) / [Turso Sync 基准博客](https://turso.tech/blog/sync-benchmark) / [Scott Spence 实战](https://scottspence.com/posts/from-billions-to-microseconds-turso-embedded-replicas)

## 摘要

Embedded Replicas 让应用内嵌一个本地 SQLite 副本文件，与 Turso 云端主库同步：读操作全部走本地文件（微秒级），写操作发往云端主库后自动回传副本。本质是"给数据库做 CDN"——本地读性能 + 云端持久化。但注意：**官方现在明确建议新项目改用 Turso Sync**（基于逻辑 CDC，本地优先写、显式 push()/pull()），Embedded Replicas 的物理页复制协议有固有缺陷。

## 关键发现

**1. 工作机制（Embedded Replicas）**
- 客户端配 `url`（本地文件）+ `syncUrl`（云端主库）即可启用
- 读：始终走本地副本，微秒级延迟
- 写：默认直发云端主库（不先写本地），成功后本地自动更新（read-your-writes 语义，可关闭）
- `syncInterval` 参数定时自动同步；`offline: true` 可开离线本地写
- 支持静态加密（`encryptionKey`），JS/Go/Rust/Python/Dart 全 SDK 覆盖

**2. 物理页复制的三大缺陷（官方自曝）**
- 浪费带宽：最小复制单位是 4KB 页，写 1 字节也传整页；b-tree 分裂会放大帧数
- 无变更可见性：不知道逻辑上改了什么 → 无法冲突解决/事件回放 → 写被迫默认走远端
- 本地副本易漂移：checkpoint 后页序不一致，常需从云端全量重新引导（wasteful + frustrating）

**3. 新方案 Turso Sync（CDC）基准碾压**
- 顺序插入 3000 行：17s vs 152s（快 8.9x，流量 2.1MB vs 34.6MB，省 16.3x）
- 读己之写 200 循环：156ms vs 48.6s（快 312x，流量省 18.4x，单循环 <1ms vs 243ms）
- 即使每次写都 push 仍快 7.3x（30ms vs 218ms/循环）
- 拉取 5000 行冷启动：338ms vs 718ms，且支持 partial sync 懒加载（不用先全量同步）
- API：`npm install @tursodatabase/sync`，`connect()` + 显式 `push()`/`pull()`
- 本地调试可零账号起同步服务器：`npx turso@latest --sync-server 0.0.0.0:8080`

**4. 实战数据（Scott Spence, SvelteKit 博客，Coolify 部署）**
- 每页数据库耗时：~100ms（4-6 次网络往返）→ ~0.2ms（本地读），提升 500x
- 计费口径巨变：页面浏览 = 0 网络行读，只有周期性 sync 计数，月费用大幅下降
- 部署要点：本地副本文件需持久卷（Docker volume `/app/data`）；prod 5 分钟同步间隔，dev 1 分钟
- 缓存策略反转：缓存从"防网络延迟"变成"降 CPU 负载"
- 本地开发红利：向量搜索（`vector_distance_cos`）等 libSQL 特性本地全可用，不耗配额

**5. 已知坑（官方 Things to know）**
- 同步进行时不要用其他工具打开本地库文件 → 数据损坏风险
- 无文件系统的 serverless 环境（如部分 Edge Runtime）不能用
- WAL 脏状态重启、本地文件被删 → 触发全量重同步

## 对工作的价值

- **轻量 Web 部署新范式**：VPS/Fly.io/Railway 类单机部署 + 读多写少场景（博客、内容站、管理后台、API 服务），可用"本地读 + 云端写"把数据库延迟从几十 ms 压到亚毫秒，同时省云数据库流量费
- **边缘/弱网场景**：移动端与不稳定网络下读操作永不断线，联网后 `sync()` 追赶
- **选型警示**：这是当前生产可用但已被官方"判死"的一代方案；新项目直接上 Turso Sync（CDC），老项目评估迁移。给 AI Agent 编码时注意别让 agent 默认装 `@libsql/client` 的 sync 模式
- **架构启发**：物理复制 vs 逻辑复制的取舍（Postgres WAL 物理复制 vs 逻辑 CDC 的同款权衡），适用于自研同步层设计

## 行动建议

1. 新项目需要本地同步 → 直接用 `@tursodatabase/sync`（CDC），跳过 Embedded Replicas
2. 读多写少的 VPS 服务 → 评估 Turso 本地副本模式，预期页面 DB 耗时降 2-3 个数量级
3. 本地原型验证零成本：`npx turso@latest --sync-server` 起本地服务器，无需云账号
4. 若自研数据同步层：借鉴 CDC 行级变更 + 显式 push/pull 分离，避开整页复制的带宽放大问题

## 相关笔记

- [Fly LiteFS static-lease单主](./2026-08-17-轻量Web部署-Fly-LiteFS-static-lease单主.md) — SQLite复制赛道对照
- [三机集群健康巡检](../2026-06-15-三机集群健康巡检指南.md) — 集群数据一致性场景
- [执行归属Agent安全](../../explore/2026-08-15-execution-provenance-llm-agent-security.md) — 数据层安全
- [飞书Cardkit API核验](../../explore/2026-08-11-feishu-cardkit-v1-api-endpoint-verification-scope-audit.md) — 轻量API案例
