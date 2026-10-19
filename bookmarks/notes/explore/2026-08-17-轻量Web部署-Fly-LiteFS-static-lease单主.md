# 轻量Web部署: Fly LiteFS（static-lease 单主架构）

> 日期: 2026-08-17 | 类型: auto-explore | 前序: [Turso Embedded Replicas](2026-08-16-轻量Web部署-Turso-Embedded-Replic.md)（互补对照）

- 来源: [LiteFS Config Reference](https://fly.io/docs/litefs/config) / [Introducing LiteFS (Ben Johnson)](https://fly.io/blog/introducing-litefs) / [Fly 社区: Sunsetting LiteFS Cloud](https://community.fly.io/t/sunsetting-litefs-cloud/20829)

## 摘要

LiteFS 是 Fly.io 开源的分布式 SQLite 文件系统：通过 FUSE 挂载拦截文件系统调用，把 SQLite 事务打包成 LTX 文件复制到多节点。static-lease 模式 = 单一固定主节点 + 只读副本，不依赖 Consul、无自动故障转移，是"读多写少 + 可容忍主库短暂停机"场景的最简部署形态。与昨日 Turso Embedded Replicas 同属"SQLite 复制"赛道，但 LiteFS 完全自托管、无 SDK 侵入（应用无感知），Turso 是托管云服务。注意 LiteFS Cloud 已 sunset，备份需自建 Litestream → S3/Tigris。

## 关键发现

**1. 架构：FUSE 透传层 + LTX 事务文件**
- LiteFS 不是新数据库，是应用与磁盘之间的"文件系统代理"：拦截 `-journal` 文件创建/删除来识别事务边界，把变更页打包为 LTX 文件复制
- 选择 FUSE 而非 SQLite VFS 的原因：VFS 需要每个进程（含 sqlite3 CLI）记得显式加载；FUSE 挂载后任何进程零改动可用，且天然解决"谁跑 API server"的多进程问题
- 应用把数据库路径指向 `/litefs` 挂载点即可，完全无感知

**2. static lease vs consul lease（核心分野）**

```
consul: 候选节点抢时间租约 → 主可漂移 → 自动故障转移（需跑 Consul，TTL≥10s）
static: candidate=true 的那个节点永远为主 → 副本 candidate=false 永不晋升 → 无故障转移
```

- static 配置极简：主节点设 `lease.type: "static"` + `candidate: true` + `hostname` + `advertise-url`，副本只设 `candidate: false`，无需任何额外配置节
- 主挂了副本就一直只读等着，主恢复后自动追同步——适合"rarely up"架构（写频率极低、主库恢复即可接受）
- 生产建议仍是 Consul（部署时主可无缝交接租约），static 是用可用性换运维简单性

**3. 一致性防御：XOR 页校验和**
- 每个数据库维护全量校验和：`chksum = XOR(crc64(page.number, page.data))`，增量维护（旧页 XOR 掉、新页 XOR 进来）
- LTX 文件乱序应用会校验失败 → 防脑裂损坏；启动时校验，保证副本字节级一致
- 异步复制，用持久性换性能和运维简单（写确认 ≠ 已复制）

**4. 运维要点（来自官方文档+社区）**
- 内部数据目录（含 LTX）必须放持久卷 `/var/lib/litefs`；LTX 默认 LZ4 压缩，retention 默认 10m
- HTTP API 端口 20202 节点间通信，**绝不可公网暴露**；内置 proxy 可做写转发 + 副本一致性（`primary-redirect-timeout: 5s`）
- LiteFS Cloud 已关停：备份方案 = 在 static 主节点上跑 Litestream → Tigris/S3；官方同时承认想要全托管就去看 Turso
- 已知坑：候选过滤 `databases: [...]` 只能在非 candidate 节点用；`skip-sync` 可跳过等主启动（调试用）

**5. 与 Turso Embedded Replicas 对照（昨日笔记增量）**

- 复制单位：LiteFS 复制 LTX（事务级，含多页变更）；Turso ER 复制 4KB 物理页（官方自曝缺陷：写 1 字节传整页）
- 侵入性：LiteFS 零 SDK（FUSE 层，任意语言/进程可用）；Turso 需专用 SDK（`@libsql/client`）
- 主库位置：LiteFS 主库在自己 VM 上（数据主权完整）；Turso 主库在 Turso 云
- 演进状态：LiteFS 稳定但云服务已撤；Turso ER 被官方判死、主推 Turso Sync（CDC）
- 共同本质：都是"本地读 + 单点写"的 SQLite 单写者范式扩展

## 对工作的价值

- **内网多机 SQLite 复制的零依赖方案**：三台 Hermes（jbot/ubot/abot）共享 NFS，若有需一致读的 SQLite 数据（如经验池索引、任务状态），LiteFS static lease 可在 LAN 内做"1 写 N 读"，比 NFS 上的并发 SQLite 访问安全（NFS + SQLite WAL 是公认的损坏组合，LiteFS 恰好规避）
- **Jetson 自托管场景**：LiteFS 开源且不锁 Fly.io，ARM64 可编译，适合边缘集群里给只读副本分发数据（如行情快照库：主节点写入，其余节点本地微秒读）
- **架构参考价值**：FUSE 拦截 + 事务打包（LTX）+ XOR 增量校验和，是"不侵入应用做数据复制"的经典设计，可借鉴到自研同步层

## 行动建议

1. 三机集群若出现"多机读同一 SQLite"需求，优先评估 LiteFS static lease 替代 NFS 直读（防 SQLite-on-NFS 损坏）
2. 任何 LiteFS 部署必须配 Litestream 备份到对象存储——LiteFS Cloud 已死，无官方托管备份
3. 读多写少 + 需要数据完全自托管 → LiteFS；能接受托管云 + 要 CDC 语义 → Turso Sync；单机 → 直接 Litestream

## 相关笔记

- [Turso Embedded Replicas](./2026-08-16-轻量Web部署-Turso-Embedded-Replic.md) — 同日SQLite复制赛道对照
- [Agent-Optimization替代SEO商业模式](./2026-08-16-Agent-Optimization替代SEO-GEO商业模式.md) — 商业流量分发模型
- [飞书Cardkit v1 API核验](../../explore/2026-08-11-feishu-cardkit-v1-api-endpoint-verification-scope-audit.md) — 轻量Web API核验案例
- [执行归属Agent安全](../../explore/2026-08-15-execution-provenance-llm-agent-security.md) — 部署层安全考量
