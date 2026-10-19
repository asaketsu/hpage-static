# SQLite-on-NFS 损坏规避：WAL 陷阱与回滚日志方案

> 探索日期 2026-08-30 | 兴趣等级 L2 | 来源 5（SQLite 官方×2 + GitHub issue + HN + 实战博客）| 关联笔记：2026-08-17-Fly-LiteFS-static-lease单主、2026-05-30-SQLite足以支撑持久化工作流

## 摘要

SQLite 官方明确：网络文件系统（尤其 NFS）的锁实现不保证正确，跨机并发访问可导致静默损坏。核心矛盾在 WAL 模式——其 `-shm` 共享内存索引要求所有读写进程在同一台机器，跨 NFS 挂载必然失效。规避方案：跨机场景强制 rollback journal（DELETE/TRUNCATE）模式，或干脆放弃多机共享、改单主复制（LiteFS/Turso 模式）。

## 关键发现

1. **WAL 在 NFS 上是结构性不兼容，不是 bug**。官方 wal.html 原文："WAL mode does not work on a network filesystem"——WAL 索引存在共享内存中，所有 reader 必须在同一 OS 实例。跨机 NFS 各自持有独立 `-shm` 视图 → checkpoint 判断失真 → 静默损坏，下次启动才报 `SQLITE_CORRUPT`。
2. **三大 AI CLI 工具在同一坑里翻车**（2026 年实证）：oh-my-pi #9082（两台服务器共享同一 NFS home，WAL 静默损坏）、openai/codex #30957（CODEX_HOME 在 NFS 上 WAL 损坏 runtime DB）、opencode #14970（NFS 并发会话 "database disk image is malformed"）。修复模式一致：检测到 NFS 时自动降级 `journal_mode=DELETE/TRUNCATE`。
3. **官方对 NFS 的立场是"不承诺"而非"禁止"**。howtocorrupt.html §2.1：锁语义靠底层文件系统兑现，"NFS 谎报锁成功 → SQLite 提交 → 损坏在未来任意时刻显形"（SQLite 论坛原话）。POSIX advisory lock 在 NFSv3 上由锁守护进程模拟，NFSv4 才有内建锁，但实现质量参差。
4. **单机多进程 + 本地盘才是 SQLite 安全区**：WAL 的全部收益（读不阻塞写、fsync 批处理）都建立在共享内存可见的前提下。Lobsters/tenousandmeters 博客结论一致——rollback 模式慢但"works on NFS"。
5. **备份是第二重陷阱**：`fs.copyFile()`/`cp` 只拷 `.db` 丢 `-wal`/`-shm` = 必损坏。安全三选：`sqlite3_rsync`（3.47+）、`VACUUM INTO`、backup API。

## 决策速查

```
DB 文件所在位置？
├─ 本地盘 + 单机多进程 → WAL + synchronous=NORMAL（最优）
├─ NFS + 单机访问      → journal_mode=DELETE 可用，仍不推荐长期
├─ NFS + 跨机访问      → 禁止直开。三选一：
│    1) 每机独立 DB + 应用层同步（经验池 JSONL 追加式更简单）
│    2) 单主复制：LiteFS / Turso embedded replica（本机已有笔记）
│    3) 换真服务器：libSQL/Postgres
└─ 需要跨机共享的读多写少数据 → JSONL 追加 + 定期快照，绕开锁问题
```

关键 PRAGMA：

```sql
PRAGMA journal_mode=DELETE;   -- NFS 上唯一安全的日志模式
PRAGMA synchronous=FULL;      -- NFS 缓存更激进，勿降级
PRAGMA locking_mode=NORMAL;   -- EXCLUSIVE+WAL 可绕过共享内存，但单连接独占
```

## 对工作的价值

- 本机三台 Hermes（jbot/ubot/abot）共享 NFS4，exchange-protocol 的 experience-pool.jsonl 用追加式 JSONL 而非 SQLite——这个设计决策被本次调研证实为正确规避了 NFS 损坏坑。
- 未来任何 cron/Agent 状态存储想上 SQLite 时：若文件落在 NFS 挂载点（/home/jc 在 NFS 上则全部中招），必须先执行上述决策树。

## 行动建议

1. P1：检查现有项目中是否有 SQLite 文件落在 NFS 路径（`find ~/uclaw -name "*.db" -o -name "*.sqlite*"`），命中则迁移或改 journal_mode=DELETE
2. P2：exchange-protocol 文档补一行"NFS 上禁用 SQLite WAL"的设计依据，引用本笔记
3. P2：新项目脚手架模板中加入"存储位置自检"步骤（NFS 检测 + journal_mode 决策）

## 关键风险与盲点

- NFSv4.2 + 现代 Linux 内核的锁实现比论坛时代（2021-2023 讨论）改善程度未知，但官方文档 2026-04 更新仍未松口——保守优先（来源级别：官方文档）
- "单机访问 NFS 上的 DB" 的实际风险低于跨机，但断连重连时的锁状态恢复仍无保证（社区经验）

## 来源

- https://www.sqlite.org/howtocorrupt.html（官方，§2.1 锁问题）
- https://www.sqlite.org/wal.html（官方，WAL 共享内存限制）
- https://github.com/can1357/oh-my-pi/issues/9082（三工具踩坑汇总）
- https://news.ycombinator.com/item?id=35745014（HN：WAL 不支持网络文件系统）
- https://tenthousandmeters.com/blog/sqlite-concurrent-writes-and-database-is-locked-errors
- https://scottspence.com/posts/sqlite-corruption-fs-copyfile-issue（备份陷阱实战）

## 相关笔记

- [Fly-LiteFS static-lease单主](./2026-08-17-轻量Web部署-Fly-LiteFS-static-lease单主.md) — 同集群前作：LiteFS 复制方案正是为绕开 NFS 分布式锁缺陷而生
- [SQLite: Edge 到 Cloud 的数据库](./2026-06-16-sqlite-edge-cloud-database.md) — SQLite 边缘部署选型总览，本文 NFS 场景的专项深挖
