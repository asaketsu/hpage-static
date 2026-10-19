# 轻量 Web 部署：浏览器 WASM SQLite 持久化全景 — sql.js / wa-sqlite / sqlite-wasm / PowerSync

> 探索日期 2026-09-03 | 兴趣等级 L2 | 来源 5 篇 | 类型 auto-explore（嗅探队列）

## 摘要

浏览器端 SQLite 持久化在 2026 年已从"实验性"迈入"可用"阶段。四个项目各有定位：sql.js（2014，仅内存，最简但无持久化）、wa-sqlite（2021，多 VFS 后端，性能最优）、官方 sqlite-wasm（2022，SQLite 官方维护，OPFS 支持）、PowerSync（商业 SDK，封装 wa-sqlite + Postgres 同步）。核心突破是 OPFS SyncAccessHandle API 使同步文件操作成为可能，解决了 WASM SQLite 的同步 VFS 需求。2026 年 4 月新增的 OPFSWriteAheadVFS 首次实现浏览器端读写并发。选型铁律：通用首选 wa-sqlite OPFSCoopSyncVFS，读密集选 OPFSWriteAheadVFS，兼容旧浏览器降级 IDBBatchAtomicVFS。

---

## 一、四个项目定位速查（关键发现 1）

```
时间线：
2014  sql.js         ← 第一个 SQLite→Web 编译，仅内存，无持久化
2021  wa-sqlite       ← 实验性 IndexedDB 持久化，多 VFS 架构
2021  absurd-sql      ← IndexedDB + 性能优化，但项目已停更
2022  sqlite-wasm     ← SQLite 官方 Wasm build，OPFS 原生支持
2024  PowerSync      ← 商业 SDK，wa-sqlite + Postgres 同步
2026  OPFSWriteAheadVFS ← wa-sqlite 新增，首个支持读写并发的 VFS
```

- **sql.js**：2014 年发布，Alon Zakai 将 SQLite 交叉编译到 JS 再到 Wasm。仅支持内存数据库，持久化只能整体导入导出数据库文件。**定位**：快速原型、一次性数据处理，不适合生产持久化。
- **wa-sqlite**：2021 年发布，核心创新是支持用 JavaScript 完全实现 SQLite 虚拟文件系统（VFS），可接入 IndexedDB 和 OPFS 等浏览器存储。**定位**：生产级持久化的首选底层库，1.4k ⭐。
- **sqlite-wasm（官方）**：2022 年底 SQLite 官方发布 beta Wasm build，是首个与 SQLite 项目正式关联的 Wasm 制品。**定位**：官方背书、互操作性最好，但 OPFS VFS 需要跨域隔离头。
- **PowerSync**：商业服务，在 wa-sqlite 之上封装 Kysely/Drizzle ORM + Postgres 双向同步。**定位**：需要后端数据库同步的完整方案。

## 二、核心技术难题：同步 VFS 的三种解法（关键发现 2）

> SQLite 是 C 库，操作是同步的；编译到 Wasm 后 VFS 实现也必须同步。但浏览器文件系统 API 通常是异步的。

### 2.1 Emscripten Asyncify

- 将同步调用翻译为异步调用，允许 VFS 异步
- 代价：Wasm 体积 2×，性能降 2-5×，SQLite 行为可能受影响
- SQLite 官方不用此方案

### 2.2 SharedArrayBuffer + Atomics

- 独立 Worker 进程处理文件操作
- 需要 COOP + COEP 跨域隔离头（部署复杂度增加）
- 额外开销显著

### 2.3 OPFS FileSystemSyncAccessHandle（推荐）

- File System API 提供 `createSyncAccessHandle()` → 在 Worker 中同步读写 OPFS 文件
- Chrome/Safari/Firefox 全部支持
- 限制：打开文件仍异步；默认独占锁（仅单连接）

### 2.4 JSPI（2026 新标准）

- WebAssembly JavaScript Promise Integration：核心浏览器特性，性能优于 Asyncify
- Chrome 137+ 无需 flag；Firefox 仍需 flag；Safari Technology Preview 可用
- 2026 Interop 重点领域

## 三、VFS 实现全景对比（关键发现 3）

> 来源：PowerSync 博客（2026-05 更新），最权威的 WASM SQLite 持久化综述

### 3.1 wa-sqlite VFS 家族

| VFS | 存储 | 需 Asyncify/JSPI | 并发 | 文件透明 | COOP+COEP | 推荐 |
|-----|------|-----------------|------|---------|-----------|------|
| IDBBatchAtomicVFS | IndexedDB | 是 | 并发读 | 否 | 否 | 旧浏览器降级 |
| OPFSAdaptiveVFS | OPFS | 是 | 并发读 | 是 | 否 | — |
| AccessHandlePoolVFS | OPFS | 否 | 无 | 否 | 否 | — |
| OPFSCoopSyncVFS | OPFS | 否 | 并发连接 | 是 | 否 | **通用首选** |
| OPFSWriteAheadVFS | OPFS | 否 | **并发写+读** | 否 | 否 | **读密集首选** |

### 3.2 sqlite-wasm VFS

| VFS | 存储 | 需 Asyncify | 并发 | 文件透明 | COOP+COEP |
|-----|------|------------|------|---------|-----------|
| opfs | OPFS | 否 | 并发连接 | 是 | 是 |
| opfs-sahpool | OPFS | 否 | 无 | 否 | 否 |

### 3.3 OPFSWriteAheadVFS 详解（2026-04 新增，最重要突破）

首个支持浏览器端读写并发的 VFS，实现类 WAL 模式：

```
写事务流程：
1. SQLite 正常用 journal，但 VFS 拦截写入
2. 追加到内部 write-ahead log（不直接写 OPFS）
3. 读事务启动时：将 WAL 至当前位置视为主库 overlay

优势：多 tab / 单 tab 多 Worker 均可并发读
限制：
- 写事务必须 BEGIN IMMEDIATE
- VACUUM 需 PRAGMA locking_mode = EXCLUSIVE
- 默认弱持久性（crash 可能丢最近事务），PRAGMA synchronous 恢复全持久
- readwrite-unsafe 模式仅 Chrome 121+ 支持
```

## 四、性能调优四板斧（关键发现 4）

1. **Batch-atomic 写事务**：IndexedDB 可保证一批写入全成功或全失败 → SQLite 免除回滚日志 → 显著性能提升
2. **Exclusive 锁定**：`PRAGMA locking_mode = EXCLUSIVE` → 单连接独占 → 减少锁开销 → 写入显著加速
3. **宽松持久性**：`PRAGMA synchronous = NORMAL`（OS crash 可能丢数据，应用 crash 安全）或 `OFF`（不等待文件系统，吞吐极高但可能损坏）
4. **组合最优**：Exclusive + synchronous=OFF → 写入不等待文件系统 → 极高 TPS

## 五、真实世界踩坑（PowerSync 生产经验）

1. IDBBatchAtomicVFS 在 100MB+ 数据库性能退化；OPFSCoopSyncVFS 1GB+ 仍稳定
2. Safari + IDBBatchAtomicVFS 大查询触发 `RangeError: Maximum call stack size exceeded`；OPFSCoopSyncVFS 无此问题
3. Safari 无痕模式不支持 OPFS → IDBBatchAtomicVFS 降级
4. Chrome 无痕模式 100MB 数据库上限 → 超限报错
5. OPFSCoopSyncVFS 事务中途抛 SQLITE_BUSY → 应用需处理重试
6. OPFSCoopSyncVFS 需 dedicated worker（SharedWorker 不支持 OPFS）→ 跨 tab 需 MessageChannel 到单 worker
7. Chrome/Edge 标签页可被"挂起" → worker 失效 → 用 Web Lock 防止挂起
8. Ionic Capacitor 后台关闭 access handle → 用原生 SQLite 或 IDBBatchAtomicVFS

## 六、加密支持

- **SQLite Encryption Extension (SSE)**：商业方案，支持 sqlite-wasm build
- **SQLite3 Multiple Ciphers**：社区方案，兼容 sqlite-wasm 和 wa-sqlite；PowerSync Web SDK 内含
- **SQLCipher**：尚不支持 Wasm build

## 七、ORM 层选项

- **SQLocal**：Drizzle + Kysely on sqlite-wasm
- **kysely-sqlite-tools**：Kysely on sqlite-wasm 和 wa-sqlite
- **PowerSync SDK**：Kysely + Drizzle on wa-sqlite（需完整 SDK）

## 八、选型决策铁律

```
需求 → 推荐方案：
┌─────────────────────────┬─────────────────────────────────────┐
│ 通用生产部署             │ wa-sqlite OPFSCoopSyncVFS            │
│ 读密集(并发读)           │ wa-sqlite OPFSWriteAheadVFS(Chrome+) │
│ 旧浏览器兼容             │ wa-sqlite IDBBatchAtomicVFS          │
│ 快速原型/无持久化        │ sql.js                               │
│ 官方背书+互操作          │ sqlite-wasm opfs-sahpool             │
│ 后端同步(Postgres等)     │ PowerSync SDK                        │
│ 需加密                   │ SQLite3 Multiple Ciphers             │
└─────────────────────────┴─────────────────────────────────────┘
```

## 九、对现有 Skill/笔记的改进建议

- **P2**：当前无专门 Web 前端部署 skill，但此知识对 Hermes homepage/dashboard 等浏览器端项目有参考价值。如果后续需要在浏览器端做本地数据库（如离线笔记浏览），OPFSCoopSyncVFS + Drizzle ORM 是首选栈。

## 十、Actionable Insights

1. **浏览器端 SQLite 已可用于生产**：PowerSync 自 2025 年初在客户端 SDK 中支持 OPFSCoopSyncVFS 和 IDBBatchAtomicVFS，实测 1GB+ 数据库稳定。
2. **OPFS 是关键分水岭**：所有基于 OPFS SyncAccessHandle 的 VFS 都不需要 Asyncify/JSPI，性能和兼容性最优。
3. **JSPI 是 2026 值得关注的新标准**：Chrome 137+ 无 flag，性能接近 Asyncify，比 SharedArrayBuffer 方案更简洁。但 Firefox/Safari 支持尚不完整。
4. **并发是最后的短板**：即使 2026 年 4 月新增 OPFSWriteAheadVFS，浏览器端 SQLite 仍无完整 WAL 模式支持。并发写仍只能单事务串行。

## 十一、关键风险与盲点

- **跨浏览器一致性**：OPFS readwrite-unsafe 模式仅 Chrome 121+ 支持，Firefox/Safari 尚未跟进 → OPFSWriteAheadVFS 实际仅 Chrome 可用。
- **SharedWorker 限制**：OPFS sync access handle 在 SharedWorker/ServiceWorker 中不可用 → 跨 tab 共享数据库必须用 dedicated worker + MessageChannel，架构复杂。
- **持久性 vs 性能权衡**：`synchronous=OFF` 性能极高但 OS crash 可能损坏数据库 → 生产环境需评估数据可恢复性。
- **无 WAL 模式**：截至 2026-05，浏览器端无 VFS 完整支持 SQLite WAL journal 模式。OPFSWriteAheadVFS 在 VFS 层模拟类似行为，但非 SQLite 原生 WAL。

## 十二、一页速查

```
┌──────────────────────────────────────────────────────────┐
│  浏览器 WASM SQLite 速查 (2026-05)                        │
├──────────────────────────────────────────────────────────┤
│  四个项目：                                                │
│  sql.js(2014,内存only) / wa-sqlite(2021,多VFS)           │
│  sqlite-wasm(2022,官方) / PowerSync(商业,wa-sqlite+同步) │
│                                                          │
│  同步VFS三解法：                                           │
│  Asyncify(2×体积,2-5×降速) / SAB+Atomics(需COOP+COEP)    │
│  OPFS SyncAccessHandle(推荐,全浏览器支持)                  │
│  JSPI(2026新标准,Chrome137+无flag)                       │
│                                                          │
│  VFS选型：                                                 │
│  通用 → OPFSCoopSyncVFS(wa-sqlite)                       │
│  读密集 → OPFSWriteAheadVFS(2026-04,首个读写并发)        │
│  旧浏览器 → IDBBatchAtomicVFS(IndexedDB)                 │
│  官方 → sqlite-wasm opfs-sahpool                          │
│                                                          │
│  性能四板斧：batch-atomic写 / exclusive锁 /               │
│             relaxed持久性 / 组合最优                       │
│                                                          │
│  踩坑：Safari无痕不支持OPFS / Chrome无痕100MB上限        │
│       SharedWorker不支持OPFS / Capacitor后台关handle      │
│                                                          │
│  未解：无完整WAL模式支持 / 跨浏览器并发不一致              │
└──────────────────────────────────────────────────────────┘
```

## 十三、待深入

- PowerSync 的 Postgres 双向同步协议设计（Conflict resolution 策略）
- OPFSWriteAheadVFS 在生产环境的稳定性（2026-04 才发布，缺乏大规模验证）
- WASM SQLite 在移动端（iOS Safari / Android Chrome）的实际性能基线
- 将 Hermes homepage data.json 迁移到浏览器端 SQLite 的可行性（离线搜索 + 全文检索）

## 来源列表

1. PowerSync 博客 — The Current State Of SQLite Persistence On The Web: May 2026 Update — https://powersync.com/blog/sqlite-persistence-on-the-web
2. Chrome for Developers — 由源私有文件系统提供支持的浏览器中的 SQLite Wasm — https://developer.chrome.com/blog/sqlite-wasm-in-the-browser-backed-by-the-origin-private-file-system
3. SQLite 官方 — About the sqlite3 WASM/JS Subproject — https://sqlite.org/wasm/doc/trunk/about.md
4. wa-sqlite GitHub — https://github.com/rhashimoto/wa-sqlite
5. Ippon 博客 — Bringing SQLite to the Browser: A Journey with WebAssembly — https://blog.ippon.tech/bringing-sqlite-to-the-browser-a-journey-with-webassembly

> 相关：[[2026-08-25-JupyterLab使用方法完全指南-安装快捷键Magic命令与Agent集成]] · [[2026-08-19-LEANN世界最小向量索引-省97存储的图重计算RAG与全场景示例实战]]


## 相关笔记

- [轻量Web部署-Turso-Embedded-Replic](./2026-08-16-轻量Web部署-Turso-Embedded-Replic.md) — 同系列前篇：嵌入式SQLite同步路线，本文浏览器端方案的对照面
